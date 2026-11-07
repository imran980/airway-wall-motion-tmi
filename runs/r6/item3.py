"""Item 3 (docs/PREREG_r6_reviewer_items_2026-10-27.md): (a) harmonic decomposition on clinical clips with label-derived phase; (b) camera
check (pose retention >= 70 % and same sign) added to the rule, on every clinical window and on all C3VD null placements; (c) regime index
from the depth-free pair amplitude."""
import os, sys, json, numpy as np, pycolmap
from scipy.spatial.transform import Rotation
from scipy.ndimage import uniform_filter1d
sys.path.insert(0, "m2"); import label_core as LC
sys.path.insert(0, "runs/baselines"); import common as C
def fidx(n): return int("".join(c for c in os.path.basename(n) if c.isdigit()))
def cams(m1, Rg):
    rec = pycolmap.Reconstruction(f"{m1}/dense/sparse"); ims = sorted(rec.images.values(), key=lambda im: fidx(im.name)); fr = np.array([fidx(im.name) for im in ims])
    cw = [im.cam_from_world() if callable(im.cam_from_world) else im.cam_from_world for im in ims]; Rm = Rotation.from_matrix(np.array([np.asarray(x.rotation.matrix()) for x in cw])); rel = (Rm * Rm.mean().inv()).as_rotvec()
    Cc = np.array([np.asarray(im.projection_center()) for im in ims]); ax = np.linalg.svd(Cc - Cc.mean(0))[2][0]; P = (Cc - Cc.mean(0)) / Rg; z = P @ ax; lat = P - np.outer(z, ax); e1 = np.linalg.svd(lat)[2][0]; e2 = np.cross(ax, e1)
    return {int(f): v for f, v in zip(fr, np.c_[rel, z, lat @ e1, lat @ e2])}, (Cc, ax, fr)
def pose_retention(S, fs, lab, cam):
    rr = [f for f in sorted(lab) if f in fs and np.isfinite(S[fs[f]]) and f in cam]
    if len(rr) < 20: return np.nan, np.nan, np.nan
    y = np.array([S[fs[f]] for f in rr]); ind = np.array([1.0 if lab[f] < 0 else 0.0 for f in rr]); X = np.array([cam[f] for f in rr])
    b0 = np.linalg.lstsq(np.c_[ind, np.ones(len(rr))], y, rcond=None)[0][0]; b1 = np.linalg.lstsq(np.c_[ind, X, np.ones(len(rr))], y, rcond=None)[0][0]
    return float(b0), float(b1), float(b1 / b0) if abs(b0) > 1e-9 else np.nan
def label_phase(lab):
    O = sorted(k for k in lab if lab[k] < 0); wins = []
    for f in O:
        if wins and f - wins[-1][1] <= 2: wins[-1][1] = f
        else: wins.append([f, f])
    cent = np.array([(a + b) / 2 for a, b in wins]); P = float(np.median(np.diff(cent))) if len(cent) > 1 else np.nan
    lo, hi = min(lab), max(lab); knots = np.r_[cent[0] - P * np.arange(int(np.ceil((cent[0] - lo) / P)) + 1, 0, -1), cent, cent[-1] + P * np.arange(1, int(np.ceil((hi - cent[-1]) / P)) + 2)]
    return {f: v for f, v in zip(range(lo, hi + 1), np.interp(np.arange(lo, hi + 1), knots, 2 * np.pi * np.arange(len(knots))))}, P
out = {"clinical": {}, "c3vd": {}, "regime": {}}
W = [("2-V2", "g6_2v2", "2V2_f2870_f3370"), ("2-V2 rec B", "m1_2V2regen_lab", "2V2_f2870_f3370"), ("20-V1 wd", "m1_20V1_lab", "20V1_f2517_f2823"), ("20-V1 ins", "m1_20V1ins_lab", "20V1_insertion_f960_f1180"),
     ("18-V1", "m1_18V1_lab", "18V1_f450_f760"), ("7-V1", "m1_7V1_lab", "7V1_f480_f840_corrected"), ("33-V1 wd", "m1_33V1wd_lab", "33V1_withdrawal_f1060_f1215"), ("26-V2", "m1_26V2_lab_m1", "26V2_f780_f1210"),
     ("31-V1", "m1_31V1_lab", "31V1_f320_f580"), ("17-V1 wd", "m1_17V1wd_lab", "17V1_withdrawal_f1190_f1310"), ("2-V1", "m1_2V1_lab", "2V1_sessionB_f3626_f3760")]
TC = json.load(open("docs/figures/paper/table_cohort.json")); TC.update(json.load(open("docs/figures/paper/table_regen_extra_out.json")))
print("(a)+(b) clinical windows")
for name, g, labf in W:
    m1 = f"runs/{g}"; D = LC.load(m1); fs = {int(f): j for j, f in enumerate(D["fr"])}; S = LC.pooled(D, 0.0); Rg = float(np.load(f"{m1}/m1_real_grid.npz")["R"]); lab = C.labels(f"labels/{labf}.json")
    ph, P = label_phase(lab); ks = [k for k in lab if k in fs and np.isfinite(S[fs[k]])]; y = np.array([S[fs[k]] for k in ks]); phi = np.array([ph[k] for k in ks])
    c, q, _ = np.linalg.lstsq(np.c_[np.cos(phi), np.sin(phi), np.ones(len(ks))], y, rcond=None)[0]
    cam, _ = cams(m1, Rg); b0, b1, ret = pose_retention(S, fs, lab, cam); key = {"2-V2 rec B": "2-V2 regen"}.get(name, name); rule = TC.get(key, {}).get("rule")
    cam_ok = bool(np.isfinite(ret) and ret >= 0.7 and np.sign(b1) == np.sign(b0)); out["clinical"][name] = dict(c=float(c), q=float(q), q_over_c=float(abs(q) / abs(c)) if c else None, pose_retention=ret, rule=rule, rule_with_camera_check=bool(rule and cam_ok))
    print(f"  {name:11s} c {c:+.4f} q {q:+.4f} |q|/|c| {abs(q)/abs(c):5.2f} ({'position' if abs(q) < abs(c) else 'velocity'}-dominated) | pose retention {ret:+.2f} | rule {rule} -> with camera check {out['clinical'][name]['rule_with_camera_check']}")
print("(b) C3VD null placements with the camera check")
m1 = "runs/c3vd_cecum/g5_est_rc"; D = LC.load(m1); fr = [int(f) for f in D["fr"]]; fs = {f: j for j, f in enumerate(fr)}; lo, hi = min(fr), max(fr)
S4 = {"floor": LC.pooled(D, 0.0), "roof": LC.pooled(D, 180.0), "s90": LC.pooled(D, 90.0), "s270": LC.pooled(D, 270.0)}; cam, _ = cams(m1, float(np.load(f"{m1}/m1_real_grid.npz")["R"]))
fams = {}
for lf in ["2V2_f2870_f3370", "20V1_f2517_f2823", "18V1_f450_f760", "7V1_f480_f840_corrected", "33V1_withdrawal_f1060_f1215", "20V1_insertion_f960_f1180", "26V2_f780_f1210", "31V1_f320_f580", "17V1_withdrawal_f1190_f1310", "2V1_sessionB_f3626_f3760"]:
    lab = C.labels(f"labels/{lf}.json"); a0 = min(lab); pat = {k - a0: v for k, v in lab.items()}; L = max(pat) + 1
    if L <= hi - lo + 1: fams[f"clinical {lf}"] = [{lo + o + k: v for k, v in pat.items()} for o in range(0, hi - lo + 2 - L)]
for Pp in (30, 45, 52, 65, 79, 134):
    for duty in (0.17, 0.80): fams[f"periodic P{Pp} duty{duty}"] = [{f: (-1 if ((f - lo + ph_) % Pp) < duty * Pp else 1) for f in range(lo, hi + 1)} for ph_ in range(Pp)]
tot = dict(n=0, rule=0, rule_cam=0)
for nm, labs in fams.items():
    n = k1 = k2 = 0
    for l in labs:
        e = C.evaluate(S4, fs, l)
        if not e.get("ok"): continue
        n += 1
        if e["detected"]:
            k1 += 1; b0, b1, ret = pose_retention(S4["floor"], fs, l, cam)
            if np.isfinite(ret) and ret >= 0.7 and np.sign(b1) == np.sign(b0): k2 += 1
    out["c3vd"][nm] = dict(n=n, rule=k1, rule_with_camera_check=k2); tot["n"] += n; tot["rule"] += k1; tot["rule_cam"] += k2
    if k1: print(f"  {nm:34s} placements {n:3d} | rule {k1} -> with camera check {k2}")
print(f"  ALL C3VD: {tot['rule']}/{tot['n']} accepted by the rule -> {tot['rule_cam']}/{tot['n']} with the camera check"); out["c3vd"]["ALL"] = tot
print("(c) regime index from the depth-free pair amplitude")
for name, g, labf, pf in (("2-V2", "g6_2v2", "2V2_f2870_f3370", "runs/pair_feat/2V2/pair_features.json"), ("20-V1 wd", "m1_20V1_lab", "20V1_f2517_f2823", "runs/pair_feat/20V1/pair_features.json")):
    a = float(np.mean([p["S"] for p in json.load(open(pf))])); m1 = f"runs/{g}"; G = np.load(f"{m1}/m1_real_grid.npz"); Rg = float(G["R"]); Cg = G["C"]; Sg = G["S"]
    ax = np.linalg.svd(Cg - Cg.mean(0))[2][0]; z = uniform_filter1d((Cg - Cg.mean(0)) @ ax / Rg, 7, mode="nearest"); s = np.abs(np.gradient(z)); zst = (Sg - Cg.mean(0)) @ ax / Rg
    vis = np.isfinite(G["r_grid"]).sum(2) >= 3; d = np.array([np.median(np.abs(zst[vis[j]] - z[j])) if vis[j].any() else np.nan for j in range(len(z))])
    _, P = label_phase(C.labels(f"labels/{labf}.json")); v = 2 * np.pi * a / P; eb = v * d / np.maximum(s, 1e-6)
    out["regime"][name] = dict(pair_amplitude=a, period=P, eps_over_beta_median=float(np.nanmedian(eb)), frac_ge_1=float(np.nanmean(eb >= 1)))
    print(f"  {name}: pair amplitude {a:+.3f} R, cycle {P:.0f} fr -> |eps/beta| median {np.nanmedian(eb):.2f}, frames >= 1: {np.nanmean(eb >= 1):.2f}")
json.dump(out, open("runs/r6/item3.json", "w"), indent=1, default=float)
