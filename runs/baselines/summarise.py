"""Summarise baseline results: per method, motion renders detected, null renders falsely detected (primary null and off-phase), clinical readouts."""
import json, sys, collections
F = {"pipeline 3-D (sequential)": "runs/baselines/pipeline_row.jsonl", "D1 RAFT flow": "runs/baselines/d1_raft.jsonl", "D2 tuned 2-D segmentation": "runs/baselines/d2_seg.jsonl", "D3a trajectory basis": "runs/baselines/d3a_traj.jsonl", "D3 modern non-rigid (agent)": "runs/baselines/d3_results.jsonl"}
CLIN = {"2-V2", "20-V1_wd", "18-V1", "7-V1", "33-V1_wd", "20-V1_ins", "26-V2", "31-V1", "17-V1_wd", "2-V1"}
for meth, f in F.items():
    try: R = [json.loads(l) for l in open(f) if l.startswith("{")]
    except FileNotFoundError: print(f"{meth}: no results"); continue
    R = [dict(r["evaluate"], tag=r["tag"]) if "evaluate" in r else r for r in R]                       # agent rows nest the evaluate() output
    rows = collections.defaultdict(list)
    for r in R:
        t = r.get("tag", ""); k4 = t.startswith("K4_"); base = t[3:] if k4 else t
        grp = "clinical" if base in CLIN else ("null" if base.startswith("N") else "motion"); rows[(k4, grp)].append(r)
    for (k4, grp), L in sorted(rows.items()):
        name = meth.replace("(sequential)", "(phase-gated)") if k4 else meth
        if grp == "clinical":
            print(f"{name:34s} clinical: " + "; ".join(f"{r['tag']} {r['T']:+.3f} p {r.get('p', float('nan')):.3f}{' DET' if r.get('detected') else ''}" for r in L if r.get('ok')))
        else:
            d = sum(bool(r.get("detected")) for r in L); do = sum(bool(r.get("detected_off")) for r in L); ok = sum(bool(r.get("ok")) for r in L)
            print(f"{name:34s} {grp:6s} renders {len(L):2d} (scorable {ok}) | detected {d} | detected (off-phase) {do} | median T {sorted(r['T'] for r in L if r.get('ok'))[ok // 2] if ok else float('nan'):+.3f}")
