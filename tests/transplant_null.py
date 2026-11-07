"""R5: real-data false-positive rate by label transplant (see PREREG_ablation R5)."""
import json, os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "m2")); import label_core as LC
T = [("2-V2", "g6_2v2", "2V2_f2870_f3370"), ("20-V1 wd", "m1_20V1_lab", "20V1_f2517_f2823"), ("20-V1 ins", "m1_20V1ins_lab", "20V1_insertion_f960_f1180"), ("7-V1", "m1_7V1_lab", "7V1_f480_f840_corrected"),
     ("18-V1", "m1_18V1_lab", "18V1_f450_f760"), ("33-V1 wd", "m1_33V1wd_lab", "33V1_withdrawal_f1060_f1215"), ("26-V2", "m1_26V2_lab_m1", "26V2_f780_f1210"), ("31-V1", "m1_31V1_lab", "31V1_f320_f580"),
     ("17-V1 wd", "m1_17V1wd_lab", "17V1_withdrawal_f1190_f1310"), ("2-V1", "m1_2V1_lab", "2V1_sessionB_f3626_f3760")]
DELTA = 0.02
def runs_of(fs):
    fs = sorted(fs); r = []
    for k in fs:
        if r and k - r[-1][1] <= 1: r[-1][1] = k
        else: r.append([k, k])
    return r
pats = {}
for name, g, l in T:
    L = json.load(open(f"labels/{l}.json")); allf = sorted(set(int(x) for x in L["outward"]) | set(int(x) for x in L["inward"])); f0 = allf[0]; outs = set(int(x) for x in L["outward"])
    pats[name] = np.array([1 if f in outs else 0 for f in range(f0, allf[-1] + 1)]), [f for f in range(f0, allf[-1] + 1) if f in set(allf)]
res = {}
for name, g, l in T:
    D = LC.load(f"runs/{g}"); fs = {int(f): j for j, f in enumerate(D["fr"])}; S = {nm: LC.pooled(D, off) for nm, off in (("floor", 0.0), ("roof", 180.0), ("s90", 90.0), ("s270", 270.0))}
    own = json.load(open(f"labels/{l}.json")); own_out = set(int(x) for x in own["outward"])
    fin = sorted(f for f in fs if np.isfinite(S["floor"][fs[f]])); lo, hi = fin[0], fin[-1]; rows = []
    for dn, (pat, _) in pats.items():
        if dn.split()[0] == name.split()[0]: continue        # never the same patient
        P = pat[: hi - lo + 1]
        for off in range(0, max(1, hi - lo + 2 - len(P)), 3):
            frames = list(range(lo + off, lo + off + len(P))); lab = {f: (-1 if P[i] else 1) for i, f in enumerate(frames) if f in fs}
            outs = [f for f, v in lab.items() if v < 0]
            if len(runs_of(outs)) < 2 or len(lab) - len(outs) < 4: continue
            ownv = np.array([1 if f in own_out else 0 for f in lab]); trv = np.array([1 if lab[f] < 0 else 0 for f in lab])
            if ownv.std() > 0 and trv.std() > 0 and abs(np.corrcoef(ownv, trv)[0, 1]) > 0.3: continue
            ks = np.array(sorted(lab)); ys = np.array([lab[k] for k in ks]); Tf, n, nr, null, lags = LC.shift_null([("r", S["floor"], fs)], ks, ys)
            if not np.isfinite(Tf) or len(null) < 20: continue
            p = float(np.mean(null >= Tf)); sig = p < 0.05 and Tf > 0
            ctrl = sig and all(np.isfinite(c) and abs(c) < 0.5 * Tf for c in (LC.score([("r", S[c], fs)], ks, lab)[0] for c in ("roof", "s90", "s270")))
            plat = sig and all(np.isfinite(v) and v >= 0.5 * Tf for v in (LC.score([("r", S["floor"], fs)], np.array(sorted({f + k for f in lab if f + k in fs})), {f + k: v for f, v in lab.items() if f + k in fs})[0] for k in (-2, -1, 1, 2)))
            win = sig and all(np.isfinite(v) and v >= 0.33 * Tf for v in (LC.score([("r", S["floor"], fs)], np.array(sorted(r_)), r_)[0] for r_ in ({f: v for f, v in lab.items() if not (v < 0 and w[0] <= f <= w[1])} for w in runs_of(outs))))
            rows.append(dict(donor=dn, T=float(Tf), p=p, sig=bool(sig), full=bool(sig and ctrl and plat and win)))
    res[name] = rows; r = rows; m = lambda f: np.mean([f(x) for x in r]) if r else np.nan
    print(f"{name:10s} placements {len(r):4d} | SIG {m(lambda x: x['sig']):.3f}  SIG+d {m(lambda x: x['sig'] and x['T'] >= DELTA):.3f}  FULL {m(lambda x: x['full']):.3f}  FULL+d {m(lambda x: x['full'] and x['T'] >= DELTA):.3f}", flush=True)
json.dump(res, open("runs/ablation/transplant.json", "w"))
for k, f in (("SIG", lambda x: x["sig"]), ("SIG+d", lambda x: x["sig"] and x["T"] >= DELTA), ("FULL", lambda x: x["full"]), ("FULL+d", lambda x: x["full"] and x["T"] >= DELTA)):
    v = [np.mean([f(x) for x in r]) for r in res.values() if r]; print(f"pooled (target = unit) {k}: mean {np.mean(v):.3f}, max {np.max(v):.3f}")
