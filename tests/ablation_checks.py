"""R3 controlled ablation (pre-registered in docs/PREREG_ablation_2026-10-11.md). For each synthetic run with ground truth: 200 clinician-like
label trials from the TRUE breathing phase; the ring statistic and the four validity checks; acceptance under FULL, FULL minus one check,
and SIG-ONLY; false-motion rate (amp-0 runs), retention and displacement error (amp>0 runs). Usage: ablation_checks.py RUN [RUN ...] --out J"""
import argparse, json, os, sys, shutil, zlib, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "m2")); import label_core as LC
ap = argparse.ArgumentParser(); ap.add_argument("runs", nargs="+"); ap.add_argument("--trials", type=int, default=200); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", required=True); ap.add_argument("--half-width", type=float, default=30.0, help="OUT = true phase within +-this of peak opening (deg); 30 = the published 17 %% duty"); a = ap.parse_args()
TH = np.linspace(-30, 30, 61); 
def wbar(sigma): return float(np.mean(np.exp(-(TH / sigma) ** 2)))
def runs_of(fs):
    fs = sorted(fs); r = []
    for k in fs:
        if r and k - r[-1][1] <= 1: r[-1][1] = k
        else: r.append([k, k])
    return r
results = {}
for run in a.runs:
    m1 = f"{run}/m1"; T = np.load(f"{run}/truth.npz"); PH = (T["phase_table"] if "phase_table" in T.files else 2 * np.pi * np.arange(len(T["poses"])) / float(T["period"])); amp = float(T["amp"]); sig = float(T["sigma"]); period = float(T["period"])
    if not os.path.isdir(f"{m1}/dense/sparse"):
        subs = sorted(os.listdir(f"{run}/sfm/sparse")); best = max(subs, key=lambda d: len(os.listdir(f"{run}/sfm/sparse/{d}")) and os.path.getsize(f"{run}/sfm/sparse/{d}/images.bin") if os.path.exists(f"{run}/sfm/sparse/{d}/images.bin") else 0)
        os.makedirs(f"{m1}/dense", exist_ok=True); shutil.copytree(f"{run}/sfm/sparse/{best}", f"{m1}/dense/sparse")
    D = LC.load(m1); fr = np.array([int(f) for f in D["fr"]]); fs = {int(f): j for j, f in enumerate(fr)}
    S = {nm: LC.pooled(D, off) for nm, off in (("floor", 0.0), ("roof", 180.0), ("s90", 90.0), ("s270", 270.0))}
    fin = fr[np.isfinite(S["floor"])]; lo, hi = int(fin.min()), int(fin.max())
    rng = np.random.default_rng(a.seed + zlib.crc32(os.path.basename(run).encode()) % 1000); w = wbar(sig); trials = []
    for _ in range(a.trials):
        ncyc = int(rng.integers(3, 7)); L_ = int(ncyc * period)
        if hi - lo + 1 <= L_: s0, s1 = lo, hi
        else: s0 = int(rng.integers(lo, hi - L_ + 2)); s1 = s0 + L_ - 1
        span = [f for f in range(s0, s1 + 1) if f in fs]
        true_out = [f for f in span if np.cos(PH[f]) >= np.cos(np.radians(a.half_width))]
        wins = runs_of(true_out); lab_out = set()
        for wn in wins:
            if rng.random() < 0.15: continue
            a0 = wn[0] + int(rng.integers(-2, 3)); a1 = wn[1] + int(rng.integers(-2, 3)); lab_out.update(range(min(a0, a1), max(a0, a1) + 1))
        sh = int(rng.integers(-2, 3)); lab_out = {f + sh for f in lab_out}
        span_set = set(span); lab_out &= span_set
        wl = runs_of(lab_out)
        if len(wl) < 2: continue
        lab = {f: (-1 if f in lab_out else 1) for f in span}; ks = np.array(sorted(lab)); ys = np.array([lab[k] for k in ks])
        cosv = np.cos(PH[ks]); Tstar = amp * w * (cosv[ys < 0].mean() - cosv[ys > 0].mean())
        Tf, n, nr, null, lags = LC.shift_null([("r", S["floor"], fs)], ks, ys)
        if not np.isfinite(Tf) or len(null) < 20: continue
        p = float(np.mean(null >= Tf)); Lim = float(np.percentile(null, 95))
        ctr = [LC.score([("r", S[c], fs)], ks, lab)[0] for c in ("roof", "s90", "s270")]
        prof = []
        for k in (-2, -1, 1, 2):
            mm = {f + k: v for f, v in lab.items() if (f + k) in fs}; kk = np.array(sorted(mm)); prof.append(LC.score([("r", S["floor"], fs)], kk, mm)[0])
        loo = []
        for wn in wl:
            rest = {f: v for f, v in lab.items() if not (v == -1 and wn[0] <= f <= wn[1])}; loo.append(LC.score([("r", S["floor"], fs)], np.array(sorted(rest)), rest)[0])
        c_sig = p < 0.05 and Tf > 0
        c_ctrl = all(np.isfinite(c) and abs(c) < 0.5 * Tf for c in ctr) if Tf > 0 else False
        c_plat = Tf > 0 and all(np.isfinite(v) and v >= 0.5 * Tf for v in prof)
        c_win = Tf > 0 and all(np.isfinite(v) and v >= 0.33 * Tf for v in loo)
        trials.append(dict(T=float(Tf), Tstar=float(Tstar), p=p, L=Lim, sig=bool(c_sig), ctrl=bool(c_ctrl), plat=bool(c_plat), win=bool(c_win)))
    results[os.path.basename(run)] = dict(amp=amp, n=len(trials), trials=trials)
    t = trials; acc = lambda f: np.mean([f(x) for x in t]) if t else np.nan
    cfg = {"FULL": lambda x: x["sig"] and x["ctrl"] and x["plat"] and x["win"], "-ctrl": lambda x: x["sig"] and x["plat"] and x["win"], "-plat": lambda x: x["sig"] and x["ctrl"] and x["win"], "-win": lambda x: x["sig"] and x["ctrl"] and x["plat"], "SIG": lambda x: x["sig"]}
    line = f"{os.path.basename(run):14s} amp {amp:.2f} n {len(t):3d} | " + " ".join(f"{k} {acc(f):.2f}" for k, f in cfg.items())
    if amp > 0:
        for k in ("FULL", "SIG"):
            A_ = [x for x in t if cfg[k](x)]
            if A_: line += f" | {k} T/T* med {np.median([x['T']/x['Tstar'] for x in A_]):.2f} |err| med {np.median([abs(x['T']-x['Tstar']) for x in A_]):.3f}"
    print(line, flush=True)
json.dump(results, open(a.out, "w")); print("saved", a.out)
