"""Paper figure: ablation / sensitivity of the ring statistic on the supported clip (2-V2, both retained reconstructions) and the exploratory 20-V1, computed from the retained grids with the unchanged
statistic code (m2/label_core). Panels: (a) label-shift profile k = -8..+8; (b) floor-arc width 30-120 deg; (c) estimator weighting
(boxcar vs cosine) and minimum stations per frame; (d) leave-one-window-out. Usage: fig_sensitivity.py [--clips 2V2:runs/g6_2v2:labels/2V2_f2870_f3370.json ...]"""
import argparse, json, sys, os, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "m2")); import label_core as LC
ap = argparse.ArgumentParser(); ap.add_argument("--clips", nargs="+", default=["2-V2 (rec. A):runs/g6_2v2:labels/2V2_f2870_f3370.json", "2-V2 (rec. B):runs/m1_2V2regen_lab:labels/2V2_f2870_f3370.json", "20-V1 (exploratory):runs/m1_20V1_lab:labels/20V1_f2517_f2823.json"]); ap.add_argument("--out", default="docs/figures/paper/fig_sensitivity.png"); a = ap.parse_args()
col = {"2-V2 (rec. A)": "#1b6ca8", "2-V2 (rec. B)": "#5fa3d6", "20-V1 (exploratory)": "#c0392b"}; fig, axs = plt.subplots(1, 4, figsize=(14, 3.6)); res = {}
for spec in a.clips:
    name, run, lab = spec.split(":")
    if not os.path.exists(f"{run}/m1_real_grid.npz"): print("skip", name); continue
    D = LC.load(run); L = json.load(open(lab)); fs = {int(f): j for j, f in enumerate(D["fr"])}
    m = {int(k): 1 for k in L["inward"] if int(k) in fs}; m.update({int(k): -1 for k in L["outward"] if int(k) in fs}); ks = np.array(sorted(m)); ys = np.array([m[k] for k in ks])
    def stat(series, labmap=m, keys=ks): return LC.score([("r", series, fs)], keys, labmap)[0]
    s0 = LC.pooled(D, 0.0); base = stat(s0)
    # (a) label shift
    shifts = list(range(-8, 9)); prof = []
    for k in shifts:
        mm = {kk + k: v for kk, v in m.items() if (kk + k) in fs}; kk_ = np.array(sorted(mm)); prof.append(LC.score([("r", s0, fs)], kk_, mm)[0] if len(kk_) else np.nan)
    axs[0].plot(shifts, prof, "o-", ms=3, color=col[name], label=name)
    # (b) arc width
    widths = [30, 45, 60, 90, 120]; aw = [stat(LC.pooled(D, 0.0, arc_width=w)) for w in widths]; axs[1].plot(widths, aw, "o-", ms=4, color=col[name], label=name)
    # (c) weighting and min stations
    variants = [("boxcar\n3 st.", stat(LC.pooled(D, 0.0, weight="boxcar", min_stations=3))), ("cosine\n3 st.", stat(LC.pooled(D, 0.0, weight="cosine", min_stations=3))), ("boxcar\n1 st.", stat(LC.pooled(D, 0.0, min_stations=1))), ("boxcar\n5 st.", stat(LC.pooled(D, 0.0, min_stations=5)))]
    x = np.arange(len(variants)) + {"2-V2 (rec. A)": -0.25, "2-V2 (rec. B)": 0.0, "20-V1 (exploratory)": 0.25}[name]; axs[2].bar(x, [v for _, v in variants], width=0.22, color=col[name], label=name); axs[2].set_xticks(np.arange(len(variants))); axs[2].set_xticklabels([n for n, _ in variants], fontsize=8)
    # (d) leave-one-window-out
    outs = sorted(k for k in m if m[k] == -1); wins = []
    for k in outs:
        if wins and k - wins[-1][1] <= 2: wins[-1][1] = k
        else: wins.append([k, k])
    loo = []
    for w in wins:
        rest = {k: v for k, v in m.items() if not (v == -1 and w[0] <= k <= w[1])}; loo.append(LC.score([("r", s0, fs)], np.array(sorted(rest)), rest)[0])
    axs[3].plot(np.arange(len(loo)) + 1, loo, "o-", ms=4, color=col[name], label=f"{name} ({len(wins)} windows)")
    res[name] = dict(base=base, shift=prof, arc=aw, variants=variants, loo=loo); print(f"{name}: base {base:+.4f}; shift range {np.nanmin(prof):+.3f}..{np.nanmax(prof):+.3f}; arc 30-120: {[round(v,3) for v in aw]}; variants {[(n.replace(chr(10),' '), round(v,3)) for n,v in variants]}; LOO {np.min(loo):+.3f}..{np.max(loo):+.3f}")
axs[0].axhline(0, color="k", lw=0.5); axs[0].set_xlabel("label shift k (frames)"); axs[0].set_ylabel("floor OUT − IN (R)"); axs[0].set_title("(a) label-shift profile: a plateau, not a ramp", fontsize=9.5); axs[0].legend(fontsize=8, frameon=False)
axs[1].axhline(0, color="k", lw=0.5); axs[1].set_xlabel("floor-arc width (deg)"); axs[1].set_title("(b) arc width (60° published)", fontsize=9.5)
axs[2].axhline(0, color="k", lw=0.5); axs[2].set_title("(c) estimator weighting, min. stations per frame", fontsize=9.5)
axs[3].axhline(0, color="k", lw=0.5); axs[3].set_xlabel("window left out"); axs[3].set_title("(d) leave-one-window-out", fontsize=9.5); axs[3].legend(fontsize=8, frameon=False)
for ax in axs[1:]: ax.set_ylabel("floor OUT − IN (R)")
fig.tight_layout(); fig.savefig(a.out, dpi=170); json.dump({k: dict(v, variants=[(n, float(x)) for n, x in v["variants"]]) for k, v in res.items()}, open(a.out.replace(".png", ".json"), "w"), indent=1, default=float); print("saved", a.out)
