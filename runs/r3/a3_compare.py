"""A3 comparison: fixed-seed re-scoring (runs/r3/rescore/{orig,off}) vs the stored per-trial outputs (docs/supplement/acceptance_trials.csv).
Writes docs/supplement/rescore_vs_stored.csv and prints a summary."""
import json, glob, os, csv, numpy as np
from scipy.stats import beta
def cp(k, n): return (0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k)))
stored = {}
for r in csv.DictReader(open("docs/supplement/acceptance_trials.csv")):
    stored.setdefault((r["null"], r["run"]), []).append(r)
rows = []
for null, d in (("original", "orig"), ("off-phase", "off")):
    for f in sorted(glob.glob(f"runs/r3/rescore/{d}/*.json")):
        for name, r in json.load(open(f)).items():
            t = r["trials"]; n = len(t)
            if not n: continue
            k = sum(x["sig"] and x["ctrl"] and x["plat"] and x["win"] and x["T"] >= 0.02 for x in t); lo, hi = cp(k, n)
            st = stored.get((null, name), []); s0 = st[0] if st else None
            rows.append(dict(null=null, run=name, amp=r["amp"], trials=n, accepted_rule=k, rate=round(k / n, 4), cp_lo=round(lo, 4), cp_hi=round(hi, 4),
                             stored_rate=(float(s0["rate_rule"]) if s0 else ""), stored_trials=(int(s0["trials"]) if s0 else ""), n_stored_copies=len(st)))
with open("docs/supplement/rescore_vs_stored.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
both = [r for r in rows if r["stored_rate"] != ""]; d = np.array([r["rate"] - r["stored_rate"] for r in both])
print(f"re-scored rows {len(rows)}, with a stored counterpart {len(both)}; rate difference new - stored: median {np.median(d):+.3f}, mean {d.mean():+.3f}, max |d| {np.abs(d).max():.3f}")
big = sorted(both, key=lambda r: -abs(r["rate"] - r["stored_rate"]))[:8]
for r in big: print(f"  {r['null']:9s} {r['run']:22s} amp {r['amp']} new {r['rate']:.3f} [{r['cp_lo']:.2f},{r['cp_hi']:.2f}] stored {r['stored_rate']:.3f}")
inside = np.mean([r["cp_lo"] - 0.02 <= r["stored_rate"] <= r["cp_hi"] + 0.02 for r in both]); print(f"stored rate inside the new run's exact 95% CI (+-0.02): {inside:.2f}")
for null in ("original", "off-phase"):
    for kind, sel in (("null", lambda r: r["amp"] == 0), ("motion", lambda r: r["amp"] > 0)):
        R = [r for r in rows if r["null"] == null and sel(r)]
        if R: print(f"{null:9s} {kind:6s} renders {len(R)} | trials {sum(r['trials'] for r in R)} accepted {sum(r['accepted_rule'] for r in R)} | renders with any acceptance {sum(r['accepted_rule'] > 0 for r in R)}")
