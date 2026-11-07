"""D1 dense optical flow baseline (RAFT). Usage: d1_raft.py VIDEO LABELS.json TAG [GPU]. Prints one JSON line (see common.evaluate)."""
import sys, json, numpy as np, torch
sys.path.insert(0, "runs/baselines"); import common as C
from torchvision.models.optical_flow import raft_large, Raft_Large_Weights
vid, labf, tag = sys.argv[1:4]; dev = f"cuda:{sys.argv[4]}" if len(sys.argv) > 4 else "cuda:0"
lab = C.labels(labf); lo, hi = min(lab), max(lab); F = C.read_span(vid, lo - 1, hi); fr = sorted(F)
cy, cx, rs = C.scope_circle(F[fr[0]]); H, W = F[fr[0]].shape; yy, xx = np.mgrid[:H, :W]; circ = (yy - cy) ** 2 + (xx - cx) ** 2 < rs ** 2
cen = {}
for f in fr:
    c, _ = C.lumen_centre(F[f], circ); cen[f] = c if c is not None else (np.nan, np.nan)
cc = np.array([cen[f] for f in fr]); from scipy.ndimage import median_filter
for j in range(2):
    v = cc[:, j]; ok = np.isfinite(v); v[~ok] = np.interp(np.flatnonzero(~ok), np.flatnonzero(ok), v[ok]) if ok.any() else cy if j == 0 else cx; cc[:, j] = median_filter(v, 9, mode="nearest")
model = raft_large(weights=Raft_Large_Weights.C_T_SKHT_V2).to(dev).eval(); tf = Raft_Large_Weights.C_T_SKHT_V2.transforms()
def to_t(g): x = torch.from_numpy(np.repeat(g[None], 3, 0) / 255.0).float(); return x
vel = {a: np.full(len(fr), np.nan) for a in C.ARCS}
with torch.no_grad():
    for i in range(1, len(fr)):
        a_, b_ = tf(to_t(F[fr[i - 1]])[None], to_t(F[fr[i]])[None]); flow = model(a_.to(dev), b_.to(dev))[-1][0].cpu().numpy()
        cy_, cx_ = cc[i]; dy, dx = yy - cy_, xx - cx_; rho = np.hypot(dy, dx); ang = np.degrees(np.arctan2(dy, dx))
        _, lum = C.lumen_centre(F[fr[i]], circ); valid = circ & (rho > 0.2 * rs) & (rho < 0.9 * rs) & (~lum if lum is not None else True)
        ur = (flow[0] * dx + flow[1] * dy) / np.maximum(rho, 1e-6) / np.maximum(rho, 1e-6)
        for a, c0 in C.ARCS.items():
            inn = valid & (C.angdiff(ang, c0) <= 30); out = valid & (C.angdiff(ang, c0) > 50)
            if inn.sum() > 50 and out.sum() > 50: vel[a][i] = np.median(ur[inn]) - np.median(ur[out])
S = {}
for a in C.ARCS:
    v = np.nan_to_num(vel[a]); P = np.cumsum(v); k = 121; pad = np.pad(P, k // 2, mode="edge"); S[a] = P - np.convolve(pad, np.ones(k) / k, mode="valid")[:len(P)]
fs = {f: j for j, f in enumerate(fr)}; import os
if os.environ.get('SAVE_SERIES'): np.savez(os.environ['SAVE_SERIES'], frames=np.array(sorted(fs)), **{k: v for k, v in S.items()})
out = C.evaluate(S, fs, lab); out.update(tag=tag, method="D1_raft", frames=len(fr))
print(json.dumps(out), flush=True)
