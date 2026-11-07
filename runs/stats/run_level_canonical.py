"""Run-level statistics from the canonical fixed-seed scoring: every synthetic run x null (x OUT duty), with trial counts, accepted counts
(four checks; detection rule = four checks and T >= 0.02 R), exact Clopper-Pearson intervals, median accepted T/T*, and render parameters
from truth.npz. Sources: runs/r3/rescore/{orig,off} (87 grids), runs/r3/scores (slow-scope + regeneration), runs/r4/scores (2-V2-matched).
Writes docs/supplement/run_level_canonical.csv and a condition summary docs/supplement/run_level_summary.txt."""
import json, glob, os, csv, re, numpy as np
from scipy.stats import beta
def cp(k, n): return (0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k)))
full = lambda x: x["sig"] and x["ctrl"] and x["plat"] and x["win"]; rule = lambda x: full(x) and x["T"] >= 0.02
man = {r["run"]: r for r in csv.DictReader(open("docs/supplement/synthetic_manifest.csv"))}
SRC = [("original", "30", "runs/r3/rescore/orig/*.json"), ("off-phase", "30", "runs/r3/rescore/off/*.json")]
for pre, root in (("r3", "runs/r3/scores"), ("r4", "runs/r4/scores")):
    SRC += [("original", "30", f"{root}/[MNK]*.json"), ("off-phase", "30", f"{root}/offphase_*.json"), ("original", "144", f"{root}/hw144_*.json")]
def condition(run, amp):
    k4 = run.startswith("K4_"); b = run[3:] if k4 else run; amp0 = float(amp) == 0.0
    tags = []
    if "slow" in b: tags.append("slow scope (20-V1 speed)")
    elif "2V2m" in b: tags.append("2-V2-matched")
    elif re.search(r"_s(6\d|7\d|8\d|9\d|100)", b): tags.append("held-out/envelope/fresh")
    else: tags.append("development")
    if "cb" in b: tags.append("scope riding breath")
    if b.startswith("MS_") or b.startswith("NS_"): tags.append("stop-and-go")
    if "irr" in b: tags.append("irregular breathing")
    return ("rigid wall" if amp0 else "motion") + ("; phase-gated" if k4 else "; sequential") + "; " + ", ".join(tags)
rows = []
for null, duty, pat in SRC:
    for f in sorted(glob.glob(pat)):
        for run, v in json.load(open(f)).items():
            if not isinstance(v, dict) or not v.get("trials"): continue
            t = v["trials"]; n = len(t); kf = sum(full(x) for x in t); kr = sum(rule(x) for x in t); lo, hi = cp(kr, n); acc = [x["T"] / x["Tstar"] for x in t if rule(x) and x["Tstar"] > 0]
            rows.append(dict(run=run, condition=condition(run, v["amp"]), null=null, out_duty_halfwidth_deg=duty, amp_R=v["amp"], trials=n, accepted_four_checks=kf, accepted_rule=kr, rate_rule=round(kr / n, 4),
                             cp95_lo=round(lo, 4), cp95_hi=round(hi, 4), median_T_over_Tstar_accepted=round(float(np.median(acc)), 3) if acc else "", source=f))
with open("docs/supplement/run_level_canonical.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writerow; w.writeheader(); w.writerows(rows)
out = []; rng = np.random.default_rng(0)
for key in sorted(set((r["condition"], r["null"], r["out_duty_halfwidth_deg"]) for r in rows)):
    R = [r for r in rows if (r["condition"], r["null"], r["out_duty_halfwidth_deg"]) == key]; rates = np.array([r["rate_rule"] for r in R])
    k = sum(r["accepted_rule"] for r in R); n = sum(r["trials"] for r in R); a = sum(r["accepted_rule"] > 0 for r in R); alo, ahi = cp(a, len(R))
    bs = [rates[rng.integers(0, len(rates), len(rates))].mean() for _ in range(5000)]
    out.append(f"{key[0]:62s} | {key[1]:9s} hw{key[2]:>3s} | runs {len(R):2d} | trials {n:5d} accepted {k:4d} | mean rate {rates.mean():.3f} (render bootstrap {np.percentile(bs, 2.5):.3f}-{np.percentile(bs, 97.5):.3f}) | runs with any acceptance {a}/{len(R)} (CP {alo:.2f}-{ahi:.2f})")
open("docs/supplement/run_level_summary.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out)); print(len(rows), "rows")
