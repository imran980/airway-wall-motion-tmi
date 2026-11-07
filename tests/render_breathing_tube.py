"""Render a textured, BREATHING tube as a scope video the production pipeline can run on unchanged.

The existing synthetic (make_synth_workspace.py) writes analytic depth maps and flat-grey placeholder images, so the
power curve never exercised SfM or MVS. This renders real frames: aperiodic albedo texture (no helical symmetry),
irregular cartilage rings that fade out on the ringless membranous floor, a co-located light with cos/dist^2
falloff, a circular scope mask, and mild sensor noise. The wall breathes on a Gaussian arc centred on the floor:

    r(theta, t) = R * (1 + amp * exp(-((theta - theta_floor)/sigma)^2) * cos(2 pi t / period))

Camera geometry is explicit: perpendicular offset from the axis (positive = toward the ROOF, which is where the real
scopes sit), pitch toward the axis, forward-looking withdrawal at a chosen speed. Ray-tube intersection is the
uniform-radius quadratic refined by three Newton steps for the angular perturbation, so 300 frames at 1280x720 take
minutes.

Writes: images/f%05d.png, video.mp4 (for real_sfm_relaxed.py), calib.json (OPENCV, zero distortion), labels.json
(OUT = within +-30 deg of peak-open, 17 % duty like 20-V1), truth.npz (everything needed to regenerate r(theta,t)).

Usage: python tests/render_breathing_tube.py --out runs/mvs_synth/G1_a0.07 --amp 0.07 --offset 0.16 --tilt 15
"""
import argparse, os, json, subprocess, numpy as np, cv2

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--frames", type=int, default=300); ap.add_argument("--W", type=int, default=1280); ap.add_argument("--H", type=int, default=720)
ap.add_argument("--fx", type=float, default=500.0, help="pixels; HFOV = 2 atan(W/2/fx) ~ 104 deg at 1280")
ap.add_argument("--R", type=float, default=5.0); ap.add_argument("--amp", type=float, default=0.07, help="peak radial amplitude as a fraction of R")
ap.add_argument("--sigma", type=float, default=35.0, help="deg, Gaussian arc half-width around the floor")
ap.add_argument("--period", type=float, default=48.0); ap.add_argument("--speed", type=float, default=0.026, help="camera travel per frame, in R (MEAN speed when stop-and-go is on)")
ap.add_argument("--cam-breath", type=float, default=0.0, help="axial camera oscillation amplitude in R, locked to the breathing phase (scope riding the patient's breathing)"); ap.add_argument("--period-jitter", type=float, default=0.0, help="irregular breathing: cycle lengths drawn uniformly in [1-j, 1+j]*period (phase accumulates per cycle)"); ap.add_argument("--move-frames", type=int, default=0, help="stop-and-go: frames moving per block (0 = constant speed)"); ap.add_argument("--pause-frames", type=int, default=0, help="stop-and-go: frames paused per block")
ap.add_argument("--offset", type=float, default=0.0, help="camera perpendicular offset from the axis, in R; + = toward the ROOF (image-up), - = toward the floor")
ap.add_argument("--tilt", type=float, default=0.0, help="deg, camera pitched toward the tube axis")
ap.add_argument("--scan-amp", type=float, default=0.0, help="back-and-forth axial scope oscillation amplitude in R, NOT breath-locked (default 0 = off)"); ap.add_argument("--scan-period", type=float, default=110.0, help="frames per back-and-forth cycle")
ap.add_argument("--offset-x", type=float, default=0.0, help="camera sideways offset from the axis, in R (+ = image-right); default 0 leaves every earlier render unchanged")
ap.add_argument("--mask-r", type=float, default=0.265, help="scope circle radius as a fraction of W; 20-V1 rim is 414 px = 0.68 fx after undistortion -> 0.266 W at fx 500")
ap.add_argument("--blur", type=float, default=1.2, help="optical PSF sigma in px, applied before sensor noise")
ap.add_argument("--sat-pct", type=float, default=97.0, help="brightness percentile mapped to 255 (above it saturates, like the real near wall)")
ap.add_argument("--tex", type=float, default=0.30, help="albedo texture contrast; calibrated so the PRODUCTION extractor yields ~the real clips' keypoint density (~1900/image on 20-V1), not the 10k the first render gave")
ap.add_argument("--tex-blur", type=float, default=1.0, help="multiplier on the texture blur scales; >1 removes fine speckle")
ap.add_argument("--falloff", type=float, default=2.0, help="light falloff exponent on distance; 2.0 is a point source, real scopes with spread light + auto-gain look gentler")
ap.add_argument("--ambient", type=float, default=0.010, help="ambient fraction so the far lumen is dark but not black")
ap.add_argument("--noise", type=float, default=0.006); ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--phase0", type=float, default=0.0, help="radians added to the breathing phase (C4 shortcut check, 2026-11-03); 0 leaves every earlier render unchanged")
ap.add_argument("--only", type=int, default=0, help="render only the first N frames (smoke test)")
ap.add_argument("--replay", default=None, help="npz with C (N,3; tube frame, units of R, z along the axis), Rc2w (N,3,3; camera-to-tube) and PH (N): replay a measured camera path and breathing phase (default off)")
a = ap.parse_args()
REP = dict(np.load(a.replay)) if a.replay else None
if REP is not None: a.frames = len(REP["C"])
rng = np.random.default_rng(a.seed)
# breathing phase per frame: regular (2*pi*t/period) or irregular (cycle lengths uniform in [1-j, 1+j]*period, phase accumulating)
_nfr = max(a.frames, (a.only or 0)) + 2
if a.period_jitter > 0:
    _rng_ph = np.random.default_rng(a.seed + 1000); PH = np.zeros(_nfr); _t = 0.0; _ph = a.phase0; _L = a.period * _rng_ph.uniform(1 - a.period_jitter, 1 + a.period_jitter)
    for _i in range(_nfr):
        PH[_i] = _ph; _ph += 2 * np.pi / _L
        if _ph >= 2 * np.pi * (int(PH[_i] / (2 * np.pi)) + 1): _L = a.period * _rng_ph.uniform(1 - a.period_jitter, 1 + a.period_jitter)
else: PH = 2 * np.pi * np.arange(_nfr) / a.period + a.phase0
if REP is not None: PH = np.r_[REP["PH"], REP["PH"][-1] + 2 * np.pi / a.period * np.arange(1, 3)]
os.makedirs(f"{a.out}/images", exist_ok=True)

W, H, fx = a.W, a.H, a.fx; cx, cy = W/2, H/2; R = a.R
N = a.only if a.only else a.frames
# ---- texture: smooth aperiodic field in (z, theta), plus irregular rings that vanish on the membranous floor
TZ, TT = 2048, 720
base = np.zeros((TZ, TT))
for s in (3, 9, 27):
    base += cv2.GaussianBlur(rng.normal(0, 1, (TZ, TT)), (0, 0), s*a.tex_blur) * s**0.5
base = (base - base.mean()) / base.std()
ring_z = np.cumsum(rng.uniform(1.2, 2.0, 60)) * R          # irregular ring spacing
zgrid = np.linspace(-20, 120, TZ)
rings = np.zeros(TZ)
for z0 in ring_z: rings += np.exp(-((zgrid - z0)/(0.18*R))**2)
rings = rings / max(rings.max(), 1e-9)
th_grid = np.linspace(-np.pi, np.pi, TT, endpoint=False)
floor_w = np.exp(-(np.degrees(np.arctan2(np.sin(th_grid - np.pi/2), np.cos(th_grid - np.pi/2)))/50.0)**2)  # floor at +y = +90 deg
ALB = 1.0 + a.tex*base + 0.35*rings[:, None]*(1.0 - 0.9*floor_w[None, :])
ALB = np.clip(ALB, 0.25, None)

ALB_P = np.hstack([ALB, ALB[:, :1]]).astype(np.float32)                 # wrapped column for bilinear theta lookup
def albedo_at(z, th):
    zf = np.clip((z - zgrid[0]) / (zgrid[-1] - zgrid[0]) * (TZ - 1), 0, TZ - 1).astype(np.float32)
    tf = (((th + np.pi) / (2*np.pi)) % 1.0 * TT).astype(np.float32)
    return cv2.remap(ALB_P, tf, zf, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

def radius(th, t):
    w = np.exp(-(np.degrees(np.arctan2(np.sin(th - np.pi/2), np.cos(th - np.pi/2)))/a.sigma)**2)
    return R * (1.0 + a.amp * w * np.cos(PH[t]))

# ---- camera: world z = tube axis, +y = floor (image-down when unrotated). Offset + => toward roof (-y).
u, v = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5)
d_cam = np.stack([(u - cx)/fx, (v - cy)/fx, np.ones_like(u)], -1); d_cam /= np.linalg.norm(d_cam, axis=-1, keepdims=True)
pitch = np.radians(a.tilt) * (1 if a.offset > 0 else -1 if a.offset < 0 else 0)   # pitch toward the axis
Rx = np.array([[1, 0, 0], [0, np.cos(pitch), -np.sin(pitch)], [0, np.sin(pitch), np.cos(pitch)]])
d_w = d_cam @ Rx.T
mask = np.hypot(u - cx, v - cy) < a.mask_r * W
poses = []
z_start = 60.0
def travel(t):                                                       # cumulative withdrawal in R at frame t; stop-and-go keeps the SAME mean speed
    if a.move_frames <= 0: return a.speed * t
    blk = a.move_frames + a.pause_frames; v_move = a.speed * blk / a.move_frames
    return v_move * (blk * (t // blk) * a.move_frames / blk + min(t % blk, a.move_frames))
R_c2w = Rx                                                           # camera-to-world rotation, constant along the straight path (saved for oracle-pose tests)
for t in range(N):
    C = np.array([a.offset_x*R, -a.offset*R, z_start - travel(t)*R + a.cam_breath*R*np.cos(PH[t]) + a.scan_amp*R*np.sin(2*np.pi*t/a.scan_period)])          # withdrawal (+ optional breathing-locked axial oscillation): camera moves toward -z, looks +z
    d_w = d_cam @ Rx.T
    if REP is not None: C = REP["C"][t] * R + np.array([0.0, 0.0, z_start]); d_w = d_cam @ REP["Rc2w"][t].T
    # ray-tube intersection, uniform radius first then refine for the angular perturbation
    ox, oy = C[0], C[1]; dx, dy, dz = d_w[..., 0], d_w[..., 1], d_w[..., 2]
    r_t = np.full((H, W), R)
    s = np.zeros((H, W))
    for it in range(4):
        A_ = dx*dx + dy*dy; B_ = 2*(ox*dx + oy*dy); Cc = ox*ox + oy*oy - r_t*r_t
        disc = np.maximum(B_*B_ - 4*A_*Cc, 0)
        s = (-B_ + np.sqrt(disc)) / (2*np.maximum(A_, 1e-12))
        px, py = ox + s*dx, oy + s*dy
        th = np.arctan2(py, px)
        r_t = radius(th, t)
    pz = C[2] + s*dz
    hit = (s > 0.05) & (dz > 0.02) & (pz > -15) & (pz < 115)
    # shading: co-located light, inward normal (-cos th, -sin th, 0)
    nrm = -np.stack([np.cos(th), np.sin(th), np.zeros_like(th)], -1)
    cosang = np.clip(-(d_w * nrm).sum(-1), 0.05, 1.0)
    I = albedo_at(pz, th) * (a.ambient + cosang / np.maximum(s, 0.3)**a.falloff)
    I = np.where(hit & mask, I, 0.0)
    g = I / (np.percentile(I[mask & hit], a.sat_pct) + 1e-9) * 255.0
    if a.blur > 0: g = cv2.GaussianBlur(g, (0, 0), a.blur)
    g = np.clip(g + rng.normal(0, a.noise*255, g.shape), 0, 255)
    rgb = np.stack([0.58*g, 0.62*g, 1.00*g], -1).astype(np.uint8)       # BGR: pink mucosa, passes the tissue gate
    rgb[~mask] = 0
    cv2.imwrite(f"{a.out}/images/f{t:05d}.png", rgb)
    poses.append(dict(t=t, C=C.tolist(), pitch_deg=float(np.degrees(pitch)), Rc2w=(REP["Rc2w"][t] if REP is not None else Rx).tolist()))
# ---- sidecars
json.dump(dict(model="OPENCV", width=W, height=H, fx=fx, fy=fx, cx=cx, cy=cy, k1=0, k2=0, p1=0, p2=0,
               params_colmap=[fx, fx, cx, cy, 0, 0, 0, 0], provenance="synthetic pinhole, no distortion"),
          open(f"{a.out}/calib.json", "w"), indent=1)
phase = np.cos(PH[:a.frames])
out_frames = [int(t) for t in range(a.frames) if phase[t] >= np.cos(np.radians(30))]       # +-30 deg of peak-open: 17 % duty
in_frames = [int(t) for t in range(a.frames) if t not in set(out_frames)]
wins = []; 
for t in out_frames:
    if wins and t == wins[-1][1] + 1: wins[-1][1] = t
    else: wins.append([t, t])
json.dump(dict(clip="synthetic", fps=29.97, convention="OUT = within +-30 deg of peak-open (floor dropped), 17 % duty like 20-V1",
               span_frames=[0, a.frames - 1], out_windows_frames=wins, outward=out_frames, inward=in_frames,
               truth=dict(amp=a.amp, sigma_deg=a.sigma, period=a.period, R=R, offset_R=a.offset, tilt_deg=a.tilt, speed_R=a.speed)),
          open(f"{a.out}/labels.json", "w"), indent=1)
np.savez(f"{a.out}/truth.npz", amp=a.amp, sigma=a.sigma, period=a.period, R=R, offset=a.offset, offset_x=a.offset_x, scan_amp=a.scan_amp, scan_period=a.scan_period, tilt=a.tilt, speed=a.speed,
         fx=fx, W=W, H=H, poses=np.array([p["C"] for p in poses]), Rc2w_frames=np.array([p["Rc2w"] for p in poses]), replay=str(a.replay), pitch_deg=float(np.degrees(pitch)), R_c2w=R_c2w, mask_r=a.mask_r, phase_table=PH[:N], period_jitter=a.period_jitter, cam_breath=a.cam_breath,
         move_frames=a.move_frames, pause_frames=a.pause_frames)
if True:   # always write the mp4 (short --only renders feed the calibration SfM too)
    subprocess.run(["/home/mi3dr/.conda/envs/depth-eval/bin/ffmpeg", "-y", "-v", "error", "-framerate", "29.97", "-i", f"{a.out}/images/f%05d.png",
                    "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", f"{a.out}/video.mp4"], check=True)
print(f"rendered {N} frames -> {a.out}  (amp {a.amp} R on a {a.sigma:.0f}-deg floor arc, period {a.period:.0f}, offset {a.offset:+.2f} R {'roof' if a.offset>0 else 'floor' if a.offset<0 else 'axis'}-ward, tilt {a.tilt:.0f} deg, speed {a.speed} R/frame; {len(out_frames)} OUT frames in {len(wins)} windows)")
