"""The 3-D pipeline scored exactly like the baselines (one label set per render: its labels.json; clinician labels for clinical windows),
via runs/baselines/common.evaluate on the LC pooled arc series. Sequential grids, and K4 phase-gated grids where they exist."""
import os, sys, json, numpy as np
sys.path.insert(0, "m2"); import label_core as LC
sys.path.insert(0, "runs/baselines"); import common as C
M = {"2-V2": "runs/g6_2v2", "20-V1_wd": "runs/m1_20V1_lab", "18-V1": "runs/m1_18V1_lab", "7-V1": "runs/m1_7V1_lab", "33-V1_wd": "runs/m1_33V1wd_lab", "20-V1_ins": "runs/m1_20V1ins_lab",
     "26-V2": "runs/m1_26V2_lab_m1", "31-V1": "runs/m1_31V1_lab", "17-V1_wd": "runs/m1_17V1wd_lab", "2-V1": "runs/m1_2V1_lab"}
for l in open("runs/baselines/jobs.txt"):
    V, L, T = l.strip().split("|"); d = os.path.dirname(V)
    for tag, m1 in ((T, M.get(T, f"{d}/m1")), ("K4_" + T, f"{os.path.dirname(d)}/K4_{T}/m1" if T not in M else None)):
        if not m1 or not os.path.exists(f"{m1}/m1_real_grid.npz"): continue
        D = LC.load(m1); fs = {int(f): j for j, f in enumerate(D["fr"])}; S = {"floor": LC.pooled(D, 0.0), "roof": LC.pooled(D, 180.0), "s90": LC.pooled(D, 90.0), "s270": LC.pooled(D, 270.0)}
        out = C.evaluate(S, fs, C.labels(L)); out.update(tag=tag, method="pipeline_3D" + ("_phase_gated" if tag.startswith("K4_") else ""))
        print(json.dumps(out), flush=True)
