"""Paper figure: the independent image-domain check. (a) planted truth: per-pair feature-test S vs the planted displacement (150 pairs) with the
within-class null pairs; (b) real clips: per-pair S for OUT/IN pairs vs null pairs, with the pipeline's clip-level value and the clinician's
own landmark marks where available. Reads runs/pair_feat/*/pair_features.json. Output docs/figures/paper/fig_pair_test.png"""
import json, os, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
def load(d): p = f"runs/pair_feat/{d}/pair_features.json"; return json.load(open(p)) if os.path.exists(p) else None
fig, axs = plt.subplots(1, 3, figsize=(13, 4.3), width_ratios=[1.1, 1, 1])
# (a) synthetic
G, Gn = load("G0"), load("G0_null"); ax = axs[0]
S = np.array([r["S"] for r in G]); T = np.array([r["truth"] for r in G]); Sn = np.array([r["S"] for r in Gn]); Tn = np.array([r["truth"] for r in Gn])
ax.scatter(Tn, Sn, s=12, color="#9a9a9a", alpha=0.6, label=f"null pairs (same label class), n {len(Sn)}"); ax.scatter(T, S, s=14, color="#1b6ca8", alpha=0.75, label=f"OUT/IN pairs, n {len(S)}")
lim = [min(T.min(), Sn.min(), -0.05) - 0.01, max(T.max(), S.max()) + 0.02]; ax.plot(lim, lim, "k--", lw=0.8, label="identity"); ax.set_xlim(lim); ax.set_ylim(lim)
r = np.corrcoef(T, S)[0, 1]; ax.set_xlabel("planted floor displacement between the two frames  (ΔR/R)"); ax.set_ylabel("feature-pair measurement S  (ΔR/R)")
ax.set_title(f"(a) planted truth: recovered/true {S.mean()/T.mean():.2f}, Pearson {r:+.2f}, sign agreement {np.mean(np.sign(S)==np.sign(T)):.2f}", fontsize=9.5); ax.legend(fontsize=7.5, loc="upper left", frameon=False)
# (b, c) real clips
TC = json.load(open("docs/figures/paper/table_cohort.json"))                                         # ring-pipeline values exactly as in Table I
real = [("2V2", "2-V2 (normal)", TC["2-V2"]["T"], (0.033, 0.025)), ("20V1", "20-V1 (malacia, exploratory)", TC["20-V1 wd"]["T"], (0.047, 0.029))]
for ax, (tag, name, pipe, human) in zip(axs[1:], real):
    P, N = load(tag), load(f"{tag}_null")
    if P is None: ax.text(0.5, 0.5, f"{name}: pending", ha="center", transform=ax.transAxes); ax.axis("off"); continue
    S = np.array([r["S"] for r in P]); Sn = np.array([r["S"] for r in N]) if N else np.array([])
    bins = np.linspace(-0.15, 0.25, 41)
    if len(Sn): ax.hist(Sn, bins=bins, color="#9a9a9a", alpha=0.55, label=f"null pairs, n {len(Sn)}: {Sn.mean():+.3f} ± {Sn.std(ddof=1)/np.sqrt(len(Sn)):.3f}")
    ax.hist(S, bins=bins, color="#1b6ca8", alpha=0.75, label=f"OUT/IN pairs, n {len(S)}: {S.mean():+.3f} ± {S.std(ddof=1)/np.sqrt(len(S)):.3f}, {np.mean(S>0):.0%} positive")
    ax.axvline(pipe, color="#c0392b", lw=2, label=f"ring pipeline (Table I): {pipe:+.3f}")
    if human: ax.errorbar(human[0], ax.get_ylim()[1] * 0.50, xerr=human[1], fmt="D", color="#2e7d4f", ms=6, capsize=3, label=f"clinician's landmark marks: {human[0]:+.3f} ± {human[1]:.3f}")
    ax.axvline(0, color="k", lw=0.6); ax.set_xlabel("feature-pair measurement S  (ΔR/R)"); ax.set_ylabel("pairs"); ax.set_title(f"({'b' if tag == '2V2' else 'c'}) {name}", fontsize=9.5); ax.legend(fontsize=7, loc="upper right", frameon=False)
fig.tight_layout(); fig.savefig("docs/figures/paper/fig_pair_test.png", dpi=170); print("saved")
