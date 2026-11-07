"""Table I, regenerated from the RETAINED reconstruction of every window with one rule (2026-10-22). The primary rule is exactly the one
calibrated on renders and label transplants (tests/ablation_checks.py, tests/transplant_null.py): labels on every labelled frame registered
in the model (frames without a floor reading stay in the shifted sequence), circular-shift null, p = mean(null >= T), limit = Q95(null);
detection = p < 0.05 AND T > 0 AND controls (roof and both sides |T| < T/2) AND plateau (T at shifts +-1, +-2 >= T/2) AND window
consistency (every leave-one-OUT-window value >= T/3) AND T >= 0.02 R. Off-phase variant: same frame set, shifts with phase in 1/4-3/4 of the
median labelled cycle. Added columns: breathing-cycle bootstrap 95 % interval (B = 10 000, seed 0; docs/PREREG_cycle_bootstrap_2026-10-22.md)
and the camera-pose-adjusted floor coefficient (docs/PREREG_label_circularity_2026-10-22.md). Usage: table_cohort.py"""
import os, sys, json, numpy as np, pycolmap
from scipy.spatial.transform import Rotation
sys.path.insert(0, "m2"); import label_core as LC
W = [("2-V2", "normal", "g6_2v2", "2V2_f2870_f3370"), ("20-V1 wd", "malacia", "m1_20V1_lab", "20V1_f2517_f2823"), ("7-V1", "likely normal", "m1_7V1_lab", "7V1_f480_f840_corrected"),
     ("18-V1", "likely normal", "m1_18V1_lab", "18V1_f450_f760"), ("33-V1 wd", "likely normal", "m1_33V1wd_lab", "33V1_withdrawal_f1060_f1215"), ("20-V1 ins", "malacia", "m1_20V1ins_lab", "20V1_insertion_f960_f1180"),
     ("26-V2", "likely normal", "m1_26V2_lab_m1", "26V2_f780_f1210"), ("31-V1", "likely normal", "m1_31V1_lab", "31V1_f320_f580"), ("17-V1 wd", "likely normal", "m1_17V1wd_lab", "17V1_withdrawal_f1190_f1310"),
     ("2-V1", "normal", "m1_2V1_lab", "2V1_sessionB_f3626_f3760"), ("13-V3", "likely normal", "m1_13V3_lab", "13V3_f1830_f1995")]
def runs_of(fs):
    r = []
    for k in sorted(fs):
        if r and k - r[-1][1] <= 1: r[-1][1] = k
        else: r.append([k, k])
    return r
def cyc_len(ys):
    st = [i for i in range(len(ys)) if ys[i] < 0 and (i == 0 or ys[i - 1] >= 0)]; return float(np.median(np.diff(st))) if len(st) >= 2 else np.nan
def fidx(n): return int("".join(c for c in os.path.basename(n) if c.isdigit()))
if len(sys.argv) > 1: W = json.load(open(sys.argv[1]))                          # optional: [[name, status, grid, labels], ...] (Table II regenerations)
OUT = sys.argv[2] if len(sys.argv) > 2 else "docs/figures/paper/table_cohort.json"
rows = {}
for name, status, g, labf in W:
    m1 = f"runs/{g}"; L = json.load(open(f"labels/{labf}.json")); O = set(map(int, L["outward"])); I = set(map(int, L["inward"]))
    D = LC.load(m1); fs = {int(f): j for j, f in enumerate(D["fr"])}; S = {nm: LC.pooled(D, off) for nm, off in (("floor", 0.0), ("roof", 180.0), ("s90", 90.0), ("s270", 270.0))}
    lab = {f: (-1 if f in O else 1) for f in sorted(O | I) if f in fs}; ks = np.array(sorted(lab)); ys = np.array([lab[k] for k in ks]); F = [("r", S["floor"], fs)]
    T, n, nr, null, lags = LC.shift_null(F, ks, ys); p = float(np.mean(null >= T)); Lim = float(np.percentile(null, 95)); c = cyc_len(ys)
    off = ((lags / c) % 1 >= 0.25) & ((lags / c) % 1 <= 0.75) if np.isfinite(c) else np.zeros(len(lags), bool)
    p_off = float(np.mean(null[off] >= T)) if off.sum() >= 20 else np.nan; L_off = float(np.percentile(null[off], 95)) if off.sum() >= 20 else np.nan
    ctr = [LC.score([("r", S[k], fs)], ks, lab)[0] for k in ("roof", "s90", "s270")]
    prof = [LC.score(F, np.array(sorted({f + k for f in lab if f + k in fs})), {f + k: v for f, v in lab.items() if f + k in fs})[0] for k in (-2, -1, 1, 2)]
    loo = [LC.score(F, np.array(sorted(r_)), r_)[0] for wn in runs_of([f for f in lab if lab[f] < 0]) for r_ in [{f: v for f, v in lab.items() if not (v < 0 and wn[0] <= f <= wn[1])}]]
    nfin = int(sum(np.isfinite(S["floor"][fs[f]]) for f in lab))
    chk = dict(sig=bool(p < 0.05 and T > 0), ctrl=bool(T > 0 and all(np.isfinite(x) and abs(x) < 0.5 * T for x in ctr)), plat=bool(T > 0 and all(np.isfinite(x) and x >= 0.5 * T for x in prof)),
               win=bool(T > 0 and all(np.isfinite(x) and x >= T / 3 for x in loo)), minT=bool(T >= 0.02))
    # cycle bootstrap (finite frames; T is identical)
    fl = {f: v for f, v in lab.items() if np.isfinite(S["floor"][fs[f]])}; fr = sorted(fl); starts = [f for i, f in enumerate(fr) if fl[f] < 0 and (i == 0 or fl[fr[i - 1]] > 0)]; cyc = []
    for i, s0 in enumerate(starts):
        lo = fr[0] if i == 0 else s0; hi = starts[i + 1] if i + 1 < len(starts) else fr[-1] + 1; cyc.append([f for f in fr if lo <= f < hi])
    ci = [np.nan, np.nan]
    if len(cyc) >= 2:
        rng = np.random.default_rng(0); bs = []
        for _ in range(10000):
            pick = rng.integers(0, len(cyc), len(cyc)); vv = np.concatenate([[S["floor"][fs[f]] for f in cyc[j]] for j in pick]); yy = np.concatenate([[fl[f] for f in cyc[j]] for j in pick])
            if (yy < 0).any() and (yy > 0).any(): bs.append(vv[yy < 0].mean() - vv[yy > 0].mean())
        ci = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    # camera-pose adjustment (same regression as runs/theory/circularity.py)
    G = np.load(f"{m1}/m1_real_grid.npz"); Rg = float(G["R"]); rec = pycolmap.Reconstruction(f"{m1}/dense/sparse"); ims = sorted(rec.images.values(), key=lambda im: fidx(im.name)); frc = np.array([fidx(im.name) for im in ims])
    cw = [im.cam_from_world() if callable(im.cam_from_world) else im.cam_from_world for im in ims]; Rm = Rotation.from_matrix(np.array([np.asarray(x.rotation.matrix()) for x in cw])); rel = (Rm * Rm.mean().inv()).as_rotvec()
    C = np.array([np.asarray(im.projection_center()) for im in ims]); ax = np.linalg.svd(C - C.mean(0))[2][0]; P = (C - C.mean(0)) / Rg; z = P @ ax; lat = P - np.outer(z, ax); e1 = np.linalg.svd(lat)[2][0]; e2 = np.cross(ax, e1)
    cam = np.c_[rel, z, lat @ e1, lat @ e2]; cpos = {f: j for j, f in enumerate(frc)}
    rr = [f for f in fr if f in cpos]; y = np.array([S["floor"][fs[f]] for f in rr]); ind = np.array([1.0 if fl[f] < 0 else 0.0 for f in rr]); Xc = cam[[cpos[f] for f in rr]]
    b0 = np.linalg.lstsq(np.c_[ind, np.ones(len(rr))], y, rcond=None)[0][0]; b1 = np.linalg.lstsq(np.c_[ind, Xc, np.ones(len(rr))], y, rcond=None)[0][0]
    rows[name] = dict(status=status, grid=g, labels=labf, T=float(T), p=p, L=Lim, p_off=p_off, L_off=L_off, n_labelled=len(ks), n_floor=nfin, checks=chk, rule=bool(all(chk.values())), controls=ctr, plateau=prof, loo=loo,
                      cycles=len(cyc), cycle_ci=ci, pose_unadj=float(b0), pose_adj=float(b1), pose_retained=float(b1 / b0) if abs(b0) > 1e-9 else np.nan)
    r = rows[name]; print(f"{name:9s} T {T:+.4f} p {p:.3f} L {Lim:.3f} | off-phase p {p_off:.3f} L {L_off:.3f} | checks {''.join(k[0].upper() if v else '.' for k, v in chk.items())} rule {r['rule']} | floor frames {nfin}/{len(ks)} | LOO {min(loo):+.3f}..{max(loo):+.3f} | cycles {len(cyc)} CI [{ci[0]:+.3f}, {ci[1]:+.3f}] | pose {b0:+.3f}->{b1:+.3f} ({r['pose_retained']:.2f})", flush=True)
json.dump(rows, open(OUT, "w"), indent=1)
