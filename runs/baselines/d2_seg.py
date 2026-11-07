"""D2 tuned 2-D lumen segmentation + tracking (docs/PREREG_r3_list3_2026-10-22.md, amendment 2).
tune: d2_seg.py tune OUT.json      (development renders only; writes the frozen parameters)
eval: d2_seg.py eval PARAMS.json VIDEO LABELS.json TAG   (prints one JSON line)"""
import sys, json, itertools, cv2, numpy as np
sys.path.insert(0, "runs/baselines"); import common as C
from scipy.ndimage import median_filter
ANG = np.arange(0, 360, 5.0)
def series(F, sigma, q, boundary, k):
    fr = sorted(F); cy, cx, rs = C.scope_circle(F[fr[0]]); H, W = F[fr[0]].shape; yy, xx = np.mgrid[:H, :W]; circ = (yy - cy) ** 2 + (xx - cx) ** 2 < rs ** 2
    rad = np.arange(2, int(rs * 1.6)); S = {a: np.full(len(fr), np.nan) for a in C.ARCS}
    for i, f in enumerate(fr):
        gb = cv2.GaussianBlur(F[f], (0, 0), sigma); c, lum = C.lumen_centre(F[f], circ, pct=q, sigma=sigma)
        if c is None: continue
        rb = np.full(len(ANG), np.nan)
        for j, a in enumerate(np.radians(ANG)):
            py, px = (c[0] + rad * np.sin(a)).astype(int), (c[1] + rad * np.cos(a)).astype(int); ok = (py >= 0) & (py < H) & (px >= 0) & (px < W)
            py, px, rd = py[ok], px[ok], rad[ok]; ins = circ[py, px]; py, px, rd = py[ins], px[ins], rd[ins]
            if len(rd) < 5: continue
            if boundary == "seg":
                m = lum[py, px]; e = np.flatnonzero(~m); rb[j] = rd[e[0]] if len(e) else np.nan
            else:
                prof = gb[py, px]; rb[j] = rd[int(np.argmax(np.gradient(prof)))]
        if np.isfinite(rb).sum() < 20: continue
        for a, c0 in C.ARCS.items():
            inn = C.angdiff(ANG, c0) <= 30; out = C.angdiff(ANG, c0) > 50
            if np.isfinite(rb[inn]).sum() >= 3: S[a][i] = np.nanmedian(rb[inn]) / np.nanmedian(rb[out]) - 1
    if k > 1:
        for a in S:
            v = S[a]; ok = np.isfinite(v)
            if ok.sum() > k: v2 = v.copy(); v2[~ok] = np.interp(np.flatnonzero(~ok), np.flatnonzero(ok), v[ok]); S[a] = np.where(ok, median_filter(v2, k, mode="nearest"), np.nan)
    return S, {f: j for j, f in enumerate(fr)}
GRID = list(itertools.product([1, 2, 4], [5, 10, 20, 30], ["seg", "grad"], [1, 3, 5]))
if sys.argv[1] == "tune":
    DEVM = ["runs/mvs_synth/M_G0_s21", "runs/mvs_synth/M_G1_s22", "runs/mvs_synth/M_G2_s23", "runs/mvs_synth/M_G1irr_s24"]
    DEVN = ["runs/mvs_synth/N_G0_s11", "runs/mvs_synth/N_G1_s12", "runs/mvs_synth/N_G2_s13", "runs/mvs_synth/N_G1cb_s15", "runs/mvs_synth/N_G1irr_s16"]
    vids = {}
    for d in DEVM + DEVN:
        lab = C.labels(f"{d}/labels.json"); vids[d] = (C.read_span(f"{d}/video.mp4", min(lab), max(lab)), lab, np.load(f"{d}/truth.npz")["phase_table"])
    res = []
    cache = {}
    for sigma, q, b, k in GRID:
        cors, nT = [], []
        for d in DEVM:
            F, lab, PH = vids[d]; S, fs = series(F, sigma, q, b, k); fr = sorted(fs); v = S["floor"]; ok = np.isfinite(v)
            cors.append(float(np.corrcoef(v[ok], np.cos(PH[np.array(fr)[ok]]))[0, 1]) if ok.sum() > 20 else np.nan)
        for d in DEVN:
            F, lab, PH = vids[d]; S, fs = series(F, sigma, q, b, k); nT.append(abs(C.score(S["floor"], fs, lab)))
        res.append(dict(sigma=sigma, q=q, boundary=b, k=k, mean_corr=float(np.nanmean(cors)), corrs=cors, mean_null_absT=float(np.nanmean(nT))))
        print(json.dumps(res[-1]), flush=True)
    best = max(r["mean_corr"] for r in res); cand = [r for r in res if r["mean_corr"] >= best - 0.01]; pick = min(cand, key=lambda r: r["mean_null_absT"])
    json.dump(dict(chosen=pick, grid=res), open(sys.argv[2], "w"), indent=1); print("CHOSEN", json.dumps(pick))
else:
    P = json.load(open(sys.argv[2]))["chosen"]; vid, labf, tag = sys.argv[3:6]; lab = C.labels(labf)
    F = C.read_span(vid, min(lab), max(lab)); S, fs = series(F, P["sigma"], P["q"], P["boundary"], P["k"]); import os
    if os.environ.get('SAVE_SERIES'): np.savez(os.environ['SAVE_SERIES'], frames=np.array(sorted(fs)), **{k: v for k, v in S.items()})
    out = C.evaluate(S, fs, lab); out.update(tag=tag, method="D2_seg_tuned", params=P, frames=len(fs))
    print(json.dumps(out), flush=True)
