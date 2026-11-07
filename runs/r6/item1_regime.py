"""Item 1, descriptive (NOT pre-registered): regime index |eps/beta| of the replay renders, computed exactly as item 3c (runs/r6/item3.py)
but with the planted floor-arc amplitude a = amp * k_arc in place of the pair amplitude, and the planted cycle. Output runs/r6/item1_regime.json."""
import json, numpy as np
from scipy.ndimage import uniform_filter1d
I1 = json.load(open("runs/r6/item1.json")); out = {}
for tag, r in I1.items():
    if r["amp"] == 0: continue
    D0 = f"/var/tmp/mi3dr_r6/synth/{tag}"; T = np.load(f"{D0}/truth.npz"); G = np.load(f"{D0}/m1/m1_real_grid.npz"); Rg = float(G["R"]); Cg = G["C"]; Sg = G["S"]
    ax = np.linalg.svd(Cg - Cg.mean(0))[2][0]; z = uniform_filter1d((Cg - Cg.mean(0)) @ ax / Rg, 7, mode="nearest"); s = np.abs(np.gradient(z)); zst = (Sg - Cg.mean(0)) @ ax / Rg
    vis = np.isfinite(G["r_grid"]).sum(2) >= 3; d = np.array([np.median(np.abs(zst[vis[j]] - z[j])) if vis[j].any() else np.nan for j in range(len(z))])
    PH = T["phase_table"]; P = 2 * np.pi / np.median(np.gradient(np.unwrap(PH))); a = r["amp"] * r["k_arc"]; eb = 2 * np.pi * a / P * d / np.maximum(s, 1e-6)
    out[tag] = dict(cycle=float(P), a_floor=float(a), eps_over_beta_median=float(np.nanmedian(eb)), frac_ge_1=float(np.nanmean(eb >= 1)), q_over_c=r["q_over_c"])
    print(f"{tag}: cycle {P:.0f} fr, floor amplitude {a:.3f} R -> |eps/beta| median {np.nanmedian(eb):.2f} (frames >= 1: {np.nanmean(eb >= 1):.2f}); measured |q|/|c| {r['q_over_c']:.2f}")
json.dump(out, open("runs/r6/item1_regime.json", "w"), indent=1)
