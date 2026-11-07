"""Label circularity (docs/PREREG_label_circularity_2026-10-22.md): (a) camera-motion confound, (b) camera-clock labels."""
import os, sys, json, numpy as np, pycolmap
from scipy.spatial.transform import Rotation
from scipy.signal import butter, filtfilt, find_peaks
sys.path.insert(0, "m2"); import label_core as LC
sys.path.insert(0, "runs/v5"); import offphase_lib as OL
os.environ.setdefault("BRONCHO_COLMAP", "/home/mi3dr/.conda/envs/colmap-cuda/bin/colmap"); os.environ["LD_LIBRARY_PATH"] = "/home/mi3dr/.conda/envs/colmap-cuda/lib:" + os.environ.get("LD_LIBRARY_PATH", "")
W = [("2-V2", "runs/g6_2v2", "2V2_f2870_f3370"), ("20-V1 wd", "runs/m1_20V1_lab", "20V1_f2517_f2823"), ("18-V1", "runs/m1_18V1_lab", "18V1_f450_f760"),
     ("26-V2", "runs/m1_26V2_lab_m1", "26V2_f780_f1210"), ("31-V1", "runs/m1_31V1_lab", "31V1_f320_f580"), ("17-V1 wd", "runs/m1_17V1wd_lab", "17V1_withdrawal_f1190_f1310"), ("2-V1", "runs/m1_2V1_lab", "2V1_sessionB_f3626_f3760")]
def outin_p(series, fs, O, span):
    lab = {f: (-1 if f in O else 1) for f in span if f in fs and np.isfinite(series[fs[f]])}; ks = np.array(sorted(lab)); ys = np.array([lab[k] for k in ks])
    T, n, nr, null, lags = OL.shift_null_offphase([("r", series, fs)], ks, ys); return float(T), (float(np.mean(null >= T)) if len(null) else np.nan), float(np.mean(np.abs(null) >= abs(T))) if len(null) else np.nan
res = {}
for name, m1, labf in W:
    G = np.load(f"{m1}/m1_real_grid.npz"); R = float(G["R"]); rec = pycolmap.Reconstruction(f"{m1}/dense/sparse")
    ims = sorted(rec.images.values(), key=lambda im: int("".join(c for c in os.path.basename(im.name) if c.isdigit()))); fr = np.array([int("".join(c for c in os.path.basename(im.name) if c.isdigit())) for im in ims])
    cfw = [im.cam_from_world() if callable(im.cam_from_world) else im.cam_from_world for im in ims]; Rm = np.array([np.asarray(c.rotation.matrix()) for c in cfw]); C = np.array([np.asarray(im.projection_center()) for im in ims])
    Rmean = Rotation.from_matrix(Rm).mean(); rel = (Rotation.from_matrix(Rm) * Rmean.inv()).as_rotvec()                 # pitch/yaw/roll about camera axes
    ax = np.linalg.svd(C - C.mean(0))[2][0]; P = (C - C.mean(0)) / R; z = P @ ax; lat = P - np.outer(z, ax); e1 = np.linalg.svd(lat)[2][0]; e2 = np.cross(ax, e1)
    cam = {"pitch": rel[:, 0], "yaw": rel[:, 1], "roll": rel[:, 2], "axial": z, "lat1": lat @ e1, "lat2": lat @ e2}
    L = json.load(open(f"labels/{labf}.json")); O = set(map(int, L["outward"])); I = set(map(int, L["inward"])); span = sorted(O | I)
    D = LC.load(m1); fs = {int(f): j for j, f in enumerate(D["fr"])}; S = LC.pooled(D, 0.0); fpos = {f: j for j, f in enumerate(fr)}
    r = dict(); camvals = {k: np.full(len(S), np.nan) for k in cam}
    for f, j in fs.items():
        if f in fpos:
            for k in cam: camvals[k][j] = cam[k][fpos[f]]
    r["camera_OUTIN"] = {k: outin_p(camvals[k], fs, O, span)[::2] for k in cam}                                # (OUT-IN, two-sided off-phase p)
    rows = [f for f in span if f in fs and np.isfinite(S[fs[f]]) and all(np.isfinite(camvals[k][fs[f]]) for k in cam)]
    y = np.array([S[fs[f]] for f in rows]); ind = np.array([1.0 if f in O else 0.0 for f in rows]); Xc = np.array([[camvals[k][fs[f]] for k in cam] for f in rows])
    b0 = np.linalg.lstsq(np.c_[ind, np.ones(len(rows))], y, rcond=None)[0][0]; b1 = np.linalg.lstsq(np.c_[ind, Xc, np.ones(len(rows))], y, rcond=None)[0][0]
    r["floor_coef_unadj"], r["floor_coef_adj"] = float(b0), float(b1); r["retained"] = float(b1 / b0) if b0 else np.nan
    # (b) camera clock from the axial ride
    fl = np.arange(fr.min(), fr.max() + 1); zi = np.interp(fl, fr, z); zi = zi - np.polyval(np.polyfit(fl, zi, 2), fl)
    F = np.abs(np.fft.rfft(zi * np.hanning(len(zi)), n=8192)) ** 2; fq = np.fft.rfftfreq(8192); band = (fq > 1 / 150) & (fq < 1 / 30); Tp = 1 / fq[band][np.argmax(F[band])]
    bb, aa = butter(2, [0.6 / Tp, 1.6 / Tp], btype="band", fs=1.0); zb = filtfilt(bb, aa, zi)
    lab_cyc = None; st = [s for s in sorted(O) if s - 1 not in O]; lab_cyc = float(np.median(np.diff(st))) if len(st) > 1 else None
    for sgn, nm in ((1, "peaks"), (-1, "troughs")):
        pk, _ = find_peaks(sgn * zb, distance=max(1, int(0.6 * Tp))); Oc = set(int(fl[p] + d) for p in pk for d in range(-3, 4)) & set(span)
        agree = float(np.mean([any(abs(f - g) <= 3 for g in Oc) for f in O])) if O else np.nan
        T, p1, p2 = outin_p(S, fs, Oc, span) if len(Oc) > 4 else (np.nan, np.nan, np.nan)
        r[f"clock_{nm}"] = dict(period=float(Tp), label_cycle=lab_cyc, agree_with_clinician=agree, floor_OUTIN=T, p_offphase=p1)
    res[name] = r
    print(f"{name:9s} floor coef {b0:+.4f} -> adjusted {b1:+.4f} (retained {r['retained']:.2f}) | camera OUT-IN (p): " + " ".join(f"{k} {v[0]:+.4f}({v[1]:.2f})" for k, v in r["camera_OUTIN"].items()), flush=True)
    for nm in ("peaks", "troughs"):
        c = r[f"clock_{nm}"]; print(f"          camera clock ({nm}): period {c['period']:.1f} (labelled cycle {c['label_cycle']}) | agrees with clinician OUT {c['agree_with_clinician']:.2f} | floor OUT-IN {c['floor_OUTIN']:+.4f} p {c['p_offphase']:.3f}", flush=True)
json.dump(res, open("runs/theory/circularity.json", "w"), indent=1, default=float)
