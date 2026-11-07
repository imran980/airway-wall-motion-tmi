"""Ablation table (paper Table ablation) recomputed from the canonical fixed-seed re-scoring (runs/r3/rescore/orig)."""
import json, glob, os, numpy as np
R = {}
for f in glob.glob("runs/r3/rescore/orig/*.json"):
    for k, v in json.load(open(f)).items():
        if isinstance(v, dict) and v.get("trials"): R[k] = v
cfg = {"Full": lambda x: x["sig"] and x["ctrl"] and x["plat"] and x["win"], "-ctrl": lambda x: x["sig"] and x["plat"] and x["win"], "-plat": lambda x: x["sig"] and x["ctrl"] and x["win"],
       "-win": lambda x: x["sig"] and x["ctrl"] and x["plat"], "Sig": lambda x: x["sig"], "Rule": lambda x: x["sig"] and x["ctrl"] and x["plat"] and x["win"] and x["T"] >= 0.02}
DEV_RIGID = ["G0_a0", "G1_a0", "G2_a0", "G3_a0", "K11_cb_a0", "N_G0_s11", "N_G1_s12", "N_G2_s13", "N_G3_s14", "N_G1cb_s15", "N_G1irr_s16", "NS_G1_s34", "NS_G2_s35", "K4_G1_a0"]
DEV_SEQ = ["eval_G0", "eval_G1", "eval_G1sg", "G0_a0.07", "G1_a0.07", "G1lit_a0.07", "G2_a0.07", "K11_cb", "M_G0_s21", "M_G1_s22", "M_G2_s23", "M_G1irr_s24", "MS_G0_s31", "MS_G1_s32", "MS_G2_s33"]
HO = lambda pre, kinds: [k for k in R if any(k.startswith(pre + p) for p in kinds) and any(f"_s{s}" in k for s in range(61, 81))]
groups = [("Rigid wall (development)", DEV_RIGID), ("Far floor, motion", ["G3_a0.07"]), ("Phase-gated, motion (development)", ["K4_G1", "K4_G1_irr"]), ("Sequential, motion (development)", DEV_SEQ),
          ("Held-out rigid wall", [k for k in R if k[0] == "N" and any(f"_s{s}" in k for s in range(61, 81))]), ("Held-out phase-gated", HO("K4_", ["M_", "MS_"])), ("Held-out sequential", [k for k in R if k[:2] in ("M_", "MS") and any(f"_s{s}" in k for s in range(61, 81))])]
out = {}
for name, ks in groups:
    ks = [k for k in ks if k in R]; miss = None
    rates = {c: [np.mean([f(x) for x in R[k]["trials"]]) for k in ks] for c, f in cfg.items()}
    out[name] = dict(runs=ks, trials=int(sum(len(R[k]["trials"]) for k in ks)), **{c: [round(min(v), 3), round(float(np.median(v)), 3), round(max(v), 3)] for c, v in rates.items()})
    print(f"{name:36s} n {len(ks):2d} trials {out[name]['trials']:5d} | " + " | ".join(f"{c} {min(v):.2f}-{max(v):.2f} (med {np.median(v):.2f})" for c, v in rates.items()))
json.dump(out, open("docs/supplement/ablation_table_canonical.json", "w"), indent=1)
