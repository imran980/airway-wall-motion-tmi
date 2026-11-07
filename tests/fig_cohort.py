"""Paper figure: the labelled cohort at a glance, drawn from docs/figures/paper/table_cohort.json (tests/table_cohort.py: every window
re-scored with one rule on its retained reconstruction). Per clip: floor OUT-IN (R), the detection limit (grey band), roof/side controls, the
leave-one-window-out range and the breathing-cycle 95 % interval. Output docs/figures/paper/fig_cohort.png"""
import json, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D; from matplotlib.patches import Patch
T = json.load(open("docs/figures/paper/table_cohort.json"))
cls = {"2-V2": "supported", "20-V1 wd": "exploratory", "18-V1": "notdet", "7-V1": "notrepro", "33-V1 wd": "notrepro", "20-V1 ins": "notdet", "26-V2": "null", "31-V1": "null", "17-V1 wd": "null", "2-V1": "null", "13-V3": "unmeas"}
col = {"supported": "#1b6ca8", "exploratory": "#7fa7c9", "notdet": "#9a9a9a", "notrepro": "#b8860b", "null": "#c0392b", "unmeas": "#cccccc"}
lab = {"supported": "supported (both reconstructions)", "exploratory": "exploratory (at limit; cycle CI and pose test fail)", "notdet": "not detected", "notrepro": "first-run detection not reproduced", "null": "null below its limit", "unmeas": "not measurable"}
names = list(T); fig, ax = plt.subplots(figsize=(11, 6.6)); y = np.arange(len(names))[::-1]
for yi, k in zip(y, names):
    r = T[k]; c = col[cls[k]]
    ax.add_patch(plt.Rectangle((-r["L"], yi - 0.4), 2 * r["L"], 0.8, color="#e9e9e9", zorder=0))
    lo, hi = r["cycle_ci"]
    if np.isfinite(lo): ax.plot([lo, hi], [yi - 0.18, yi - 0.18], color=c, lw=1.2, zorder=2); ax.plot([lo, hi], [yi - 0.18] * 2, "|", color=c, ms=6)
    loo = [v for v in r["loo"] if v == v]
    if loo: ax.plot([min(loo), max(loo)], [yi + 0.12] * 2, color=c, lw=3, alpha=0.5, solid_capstyle="round", zorder=2)
    ax.plot(r["T"], yi, "o", color=c, ms=9, zorder=3)
    for v, mk in zip(r["controls"], ("^", "s", "s")):
        if v == v: ax.plot(v, yi, mk, color="k", ms=4.5, mfc="white", zorder=3)
    ax.text(0.27, yi, f"p = {r['p']:.3f}" if r["p"] < 0.1 else f"p = {r['p']:.2f}", va="center", fontsize=8.5, color="#333")
ax.axvline(0, color="k", lw=0.6); ax.set_yticks(y); ax.set_yticklabels([f"{k}\n{T[k]['status']}" for k in names], fontsize=8); ax.set_xlim(-0.1, 0.33); ax.set_ylim(-0.7, len(names) - 0.3)
ax.set_xlabel("floor OUT − IN at the clinician's breathing extremes  (fraction of lumen radius R)")
h = [Line2D([], [], marker="o", color=col[k], ls="", ms=8, label=lab[k]) for k in col] + [Patch(color="#e9e9e9", label="detection limit (±)"), Line2D([], [], color="#888", lw=3, alpha=0.5, label="leave-one-window-out range"),
     Line2D([], [], color="#888", lw=1.2, marker="|", label="breathing-cycle 95 % interval"), Line2D([], [], marker="^", color="k", mfc="white", ls="", label="roof control"), Line2D([], [], marker="s", color="k", mfc="white", ls="", label="side controls")]
ax.legend(handles=h, fontsize=7.6, loc="upper center", bbox_to_anchor=(0.5, -0.11), ncol=3, frameon=False)
ax.set_title("Posterior-wall OUT − IN, every labelled window re-scored on its retained reconstruction", fontsize=11)
fig.tight_layout(); fig.savefig("docs/figures/paper/fig_cohort.png", dpi=170); print("saved")
