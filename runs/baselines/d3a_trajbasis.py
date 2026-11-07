"""D3a trajectory-basis non-rigid reconstruction baseline (Park et al. 2010) with the pipeline's SfM poses
(docs/PREREG_r3_list3_2026-10-22.md, amendment 3). Usage: d3a_trajbasis.py M1_DIR VIDEO LABELS.json TAG [GPU]"""
import os, sys, json, cv2, numpy as np, torch, pycolmap
sys.path.insert(0, "/scratch/mi3dr_cvpr/co-tracker"); sys.path.insert(0, "runs/baselines"); import common as C
from cotracker.predictor import CoTrackerPredictor
m1, vid, labf, tag = sys.argv[1:5]; dev = f"cuda:{sys.argv[5]}" if len(sys.argv) > 5 else "cuda:0"
def fidx(n): return int("".join(c for c in os.path.basename(n) if c.isdigit()))
rec = pycolmap.Reconstruction(f"{m1}/dense/sparse"); cam = next(iter(rec.cameras.values())); K = np.asarray(cam.calibration_matrix())
ws = json.load(open(f"{m1}/m1_real_result.json")).get("workspace"); oc = next(iter(pycolmap.Reconstruction(f"{ws}/sparse/0").cameras.values()))   # original (distorted) camera of the video
op = list(oc.params); Ko = np.array([[op[0], 0, op[2]], [0, op[1], op[3]], [0, 0, 1.0]]); dist = np.array(op[4:8] if len(op) >= 8 else [0, 0, 0, 0], float)
def to_dense(uv_video):                                                     # video pixels (original camera) -> undistorted dense-model pixels
    x = cv2.undistortPoints(np.asarray(uv_video, np.float64).reshape(-1, 1, 2), Ko, dist).reshape(-1, 2); return (K @ np.c_[x, np.ones(len(x))].T).T[:, :2]
Pm = {}; Cc = {}; Dn = {}
for im in rec.images.values():
    cw = im.cam_from_world() if callable(im.cam_from_world) else im.cam_from_world; R = np.asarray(cw.rotation.matrix()); t = np.asarray(cw.translation)
    f = fidx(im.name); Pm[f] = K @ np.c_[R, t]; Cc[f] = -R.T @ t; Dn[f] = R.T @ np.array([0, 1.0, 0])          # camera down axis in world
lab = C.labels(labf); lo, hi = min(lab), max(lab)
cap = cv2.VideoCapture(vid); f = 0; frames = []; W0 = None
while f <= hi:
    ok, im = cap.read()
    if not ok: break
    if f >= lo: W0 = W0 or im.shape[1]; frames.append(cv2.resize(im, (640, 360), interpolation=cv2.INTER_AREA))
    f += 1
F = np.stack(frames); TT = len(F); sc_track = 640.0 / W0; sc_cam = cam.width / W0                         # video px -> track px, video px -> camera px
g = cv2.cvtColor(F[0], cv2.COLOR_BGR2GRAY).astype(np.float32); cy, cx, rs = C.scope_circle(g)
gy, gx = np.meshgrid(np.linspace(cy - 0.9 * rs, cy + 0.9 * rs, 16), np.linspace(cx - 0.9 * rs, cx + 0.9 * rs, 16), indexing="ij"); G = np.c_[gx.ravel(), gy.ravel()]
inside = lambda x, y: (y - cy) ** 2 + (x - cx) ** 2 < (0.9 * rs) ** 2; G = G[[inside(x, y) for x, y in G]]
model = CoTrackerPredictor(checkpoint="/scratch/mi3dr_cvpr/ckpt/scaled_offline.pth").to(dev); tracks = []
for s0 in range(0, max(1, TT - 30), 60):
    s1 = min(TT, s0 + 150); v = torch.from_numpy(F[s0:s1, ..., ::-1].copy()).permute(0, 3, 1, 2)[None].float().to(dev); q = torch.tensor([(0, x, y) for x, y in G]).float()[None].to(dev)
    with torch.no_grad(): t_, v_ = model(v, queries=q, backward_tracking=False)
    t_ = t_[0].cpu().numpy(); v_ = v_[0].cpu().numpy() > 0.5
    for k in range(len(G)):
        obs = []
        for i in range(s1 - s0):
            x, y = t_[i, k]
            if not v_[i, k] or not inside(x, y): break
            fr_ = lo + s0 + i
            if fr_ in Pm: u_, w_ = to_dense([[x / sc_track, y / sc_track]])[0]; obs.append((fr_, u_, w_))
        if len(obs) >= 30: tracks.append(obs)
    del v; torch.cuda.empty_cache()
Cs = np.array([Cc[f] for f in sorted(Cc)]); mu = Cs.mean(0); ax = np.linalg.svd(Cs - mu)[2][0]
down = np.mean([Dn[f] for f in Dn], 0); down -= (down @ ax) * ax; down /= np.linalg.norm(down); side = np.cross(ax, down)
def dct_basis(n, k):
    t = np.arange(n); return np.stack([np.ones(n) / np.sqrt(n)] + [np.sqrt(2.0 / n) * np.cos(np.pi * (2 * t + 1) * j / (2 * n)) for j in range(1, k)], 1)
recs = []
for obs in tracks:
    fr_ = np.array([o[0] for o in obs]); n = fr_.max() - fr_.min() + 1; k = 1 + (2 * n) // 25; B = dct_basis(n, k)[fr_ - fr_.min()]
    A = []; b = []
    for (f_, u, v_), th in zip(obs, B):
        P = Pm[f_]; Th = np.kron(np.eye(3), th[None])                                               # X = Th @ beta, Th 3 x 3k
        for row, c in ((u * P[2] - P[0], None), (v_ * P[2] - P[1], None)):
            A.append(row[:3] @ Th); b.append(-row[3])
    A = np.array(A); b = np.array(b); lam = 1e-6 * np.trace(A.T @ A) / A.shape[1]
    beta = np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]), A.T @ b); X = np.stack([np.kron(np.eye(3), th[None]) @ beta for th in B])
    vv = X - mu; radv = vv - np.outer(vv @ ax, ax); r = np.linalg.norm(radv, axis=1)
    if not np.all(np.isfinite(r)) or np.median(r) <= 0: continue
    m = radv.mean(0); ang = np.degrees(np.arctan2(m @ side, m @ down)); recs.append((fr_, r / np.median(r) - 1, ang))
allf = sorted(set(range(lo, hi + 1))); fs = {f: j for j, f in enumerate(allf)}; ARC = {"floor": 0.0, "roof": 180.0, "s90": 90.0, "s270": -90.0}
S = {a: np.full(len(allf), np.nan) for a in ARC}
for a, c0 in ARC.items():
    for f in allf:
        inn = [d[np.searchsorted(fr__, f)] for fr__, d, an in recs if C.angdiff(an, c0) <= 30 and f in set(fr__)]
        out = [d[np.searchsorted(fr__, f)] for fr__, d, an in recs if C.angdiff(an, c0) > 50 and f in set(fr__)]
        if len(inn) >= 3 and len(out) >= 3: S[a][fs[f]] = np.median(inn) - np.median(out)
res = C.evaluate(S, fs, lab); res.update(tag=tag, method="D3a_trajectory_basis", tracks=len(tracks), reconstructed=len(recs), floor_tracks=int(sum(C.angdiff(an, 0) <= 30 for _, _, an in recs)))
if os.path.exists(os.path.join(os.path.dirname(labf), "truth.npz")):
    PH = np.load(os.path.join(os.path.dirname(labf), "truth.npz"))["phase_table"]; v = S["floor"]; ok = np.isfinite(v); res["corr_truth"] = float(np.corrcoef(v[ok], np.cos(PH[np.array(allf)[ok]]))[0, 1]) if ok.sum() > 20 else None
print(json.dumps(res), flush=True)
