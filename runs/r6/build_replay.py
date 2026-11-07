"""Item 1 (docs/PREREG_r6_reviewer_items_2026-10-27.md): replay file for tests/render_breathing_tube.py --replay from a clinical window.
Tube frame from the retained reconstruction: z = station-line axis (oriented along the mean viewing direction), y = mean camera down ⟂ z
(the floor), x = y × z; lateral camera position relative to the nearest station's lumen centre; units of the grid's R. Phase from the
clinician's labels (OUT-window centres = 0 mod 2π, linear in between, median cycle outside). Also writes the clinician labels in render
frame indices. Usage: build_replay.py M1_DIR LABELS.json OUT_PREFIX"""
import os, sys, json, numpy as np, pycolmap
from scipy.spatial.transform import Rotation, Slerp
m1, labf, out = sys.argv[1:4]
def fidx(n): return int("".join(c for c in os.path.basename(n) if c.isdigit()))
G = np.load(f"{m1}/m1_real_grid.npz"); R = float(G["R"]); S = G["S"]; N1, N2, cen = G["N1"], G["N2"], G["centre"]; lum = S + cen[:, :1] * N1 + cen[:, 1:2] * N2
rec = pycolmap.Reconstruction(f"{m1}/dense/sparse"); ims = sorted(rec.images.values(), key=lambda im: fidx(im.name)); fr = np.array([fidx(im.name) for im in ims])
cw = [im.cam_from_world() if callable(im.cam_from_world) else im.cam_from_world for im in ims]; Rc2w = np.array([np.asarray(c.rotation.matrix()).T for c in cw]); Cc = np.array([np.asarray(im.projection_center()) for im in ims])
z = np.linalg.svd(lum - lum.mean(0))[2][0]; z *= np.sign(np.mean(Rc2w[:, :, 2], 0) @ z)
y = np.mean(Rc2w[:, :, 1], 0); y -= (y @ z) * z; y /= np.linalg.norm(y); x = np.cross(y, z); B = np.stack([x, y, z], 1)          # columns = tube axes in world
L = json.load(open(labf)); O = sorted(map(int, L["outward"])); I = sorted(map(int, L["inward"])); lo, hi = min(O + I), max(O + I)
T = np.arange(lo, hi + 1); n = len(T)
Cs = np.array([np.interp(T, fr, Cc[:, k]) for k in range(3)]).T                                                            # registered gaps filled
rot = Slerp(fr, Rotation.from_matrix(Rc2w))(np.clip(T, fr.min(), fr.max())).as_matrix()
Ct = np.zeros((n, 3)); z0 = (Cs[0] - lum.mean(0)) @ z
for i in range(n):
    j = np.argmin(np.abs((lum - Cs[i]) @ z)); v = Cs[i] - lum[j]; Ct[i] = [(v @ x) / R, (v @ y) / R, ((Cs[i] - lum.mean(0)) @ z - z0) / R]
lat = np.hypot(Ct[:, 0], Ct[:, 1]); sc = np.where(lat > 0.8, 0.8 / np.maximum(lat, 1e-9), 1.0); Ct[:, :2] *= sc[:, None]           # keep the camera inside the tube
Rt = np.einsum("ij,njk->nik", B.T, rot)                                                                                 # camera-to-tube rotation
wins = []
for f in O:
    if wins and f - wins[-1][1] <= 2: wins[-1][1] = f
    else: wins.append([f, f])
cent = np.array([(a + b) / 2 for a, b in wins]); P = float(np.median(np.diff(cent)))
knots = np.r_[cent[0] - P * np.arange(int(np.ceil((cent[0] - lo) / P)) + 1, 0, -1), cent, cent[-1] + P * np.arange(1, int(np.ceil((hi - cent[-1]) / P)) + 2)]
PH = np.interp(T, knots, 2 * np.pi * np.arange(len(knots)))
np.savez(f"{out}_replay.npz", C=Ct, Rc2w=Rt, PH=PH, frames=T)
json.dump(dict(outward=[f - lo for f in O], inward=[f - lo for f in I], source=labf, frame_offset=lo), open(f"{out}_labels_clinician.json", "w"))
ax_tr = Ct[-1, 2] - Ct[0, 2]; print(f"{os.path.basename(m1)}: {n} frames f{lo}-{hi}; axial travel {ax_tr:+.2f} R; lateral offset median {np.median(lat):.2f} R (clamped {int((sc < 1).sum())} frames); "
      f"view tilt to axis median {np.degrees(np.median(np.arccos(np.clip(Rt[:, 2, 2], -1, 1)))):.1f} deg; labelled cycle {P:.0f} fr; {len(wins)} OUT windows")
