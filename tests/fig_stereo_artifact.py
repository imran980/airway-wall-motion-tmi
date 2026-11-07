"""Paper figure (regenerated 2026-10-22): why static stereo on a moving wall reads velocity, all panels from ONE run set
(runs/theory/exact_geom.json and exact_geom_series_*.npz; docs/PREREG_exact_geometry_2026-10-22.md). (a) geometry sketch with the
derived relation; (b) the per-frame floor series of one constant-speed sequential render (M_G1_s61): measured, the fit-free exact two-view
prediction and the planted position, against the true phase; (c) quadrature fit S = c cos(phi) + q sin(phi) + k for every valid run, as
position c / c_planted and velocity |q| / c_planted, per capture condition. Output docs/figures/paper/fig_stereo_artifact.png"""
import json, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig = plt.figure(figsize=(14, 4.4)); gs = fig.add_gridspec(1, 3, width_ratios=[1.3, 1.2, 1.0], wspace=0.33)
# (a) sketch: side view of the tube wall (bottom), camera at two times, wall moving outward
ax = fig.add_subplot(gs[0]); ax.set_xlim(0, 12); ax.set_ylim(0, 8.6); ax.axis("off")
ax.text(0.3, 8.45, "two-view triangulation: $\\hat r/r=\\beta(1+\\varepsilon)/(\\beta+\\varepsilon)$, $\\beta=s\\tau/d$, $\\varepsilon=v\\tau/r$", fontsize=8.2, va="top")
ax.text(0.3, 7.95, "first order: $\\hat r-r\\approx-(d/s)\\,v$ ($\\tau$ cancels): a velocity term", fontsize=8.2, va="top")
ax.plot([0.3, 11.7], [2.0, 2.0], color="#555", lw=2); ax.plot([0.3, 11.7], [1.3, 1.3], color="#c0392b", lw=2, ls="--")
ax.text(0.4, 2.15, "wall at $t$", fontsize=8.5, va="bottom", color="#555"); ax.text(0.4, 1.15, "wall at $t+\\tau$", fontsize=8.5, va="top", color="#c0392b")
ax.annotate("", xy=(7.5, 1.3), xytext=(7.5, 2.0), arrowprops=dict(arrowstyle="-|>", color="#c0392b", lw=1.5)); ax.text(7.7, 1.62, "$v\\,\\tau$", fontsize=9, color="#c0392b", va="center")
ax.plot(3.0, 6.0, "s", color="#1b6ca8", ms=9); ax.plot(5.6, 6.0, "s", color="#1b6ca8", ms=9)
ax.text(2.7, 6.0, "camera, $t$", ha="right", va="center", fontsize=8.5, color="#1b6ca8"); ax.text(5.9, 6.0, "camera, $t+\\tau$", ha="left", va="center", fontsize=8.5, color="#1b6ca8")
ax.annotate("", xy=(5.6, 6.6), xytext=(3.0, 6.6), arrowprops=dict(arrowstyle="<->", color="#1b6ca8", lw=1)); ax.text(4.3, 6.8, "$s\\,\\tau$", ha="center", va="bottom", fontsize=9, color="#1b6ca8")
p1, p2 = np.array([3.0, 6.0]), np.array([7.5, 2.0]); q1, q2 = np.array([5.6, 6.0]), np.array([7.5, 1.3])
ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#555", lw=1.2); ax.plot([q1[0], q2[0]], [q1[1], q2[1]], color="#c0392b", lw=1.2); ax.plot([q1[0], p2[0]], [q1[1], p2[1]], color="#555", lw=0.8, ls=":")
d1, d2 = p2 - p1, q2 - q1; tt = np.linalg.solve(np.array([d1, -d2]).T, q1 - p1); X = p1 + tt[0] * d1; ax.plot(X[0], X[1], "o", color="#b8860b", ms=8, zorder=5)
ax.text(X[0] - 0.4, X[1] + 0.1, "triangulated point\nradius error $\\approx -\\dfrac{d}{s}\\,v$", fontsize=8.5, color="#b8860b", va="bottom", ha="right")
ax.annotate("", xy=(10.8, 2.0), xytext=(10.8, 6.0), arrowprops=dict(arrowstyle="<->", color="#777", lw=0.8)); ax.text(11.0, 4.0, "$d$", fontsize=9, color="#777", va="center")
ax.set_title("(a) static stereo on a moving wall", fontsize=10, pad=4)
# (b) one sequential render: measured vs exact prediction vs planted position
Z = np.load("runs/theory/exact_geom_series_M_G1_s61.npz"); f = Z["frames"]; ax = fig.add_subplot(gs[1])
ax.plot(f, Z["meas"], color="#c0392b", lw=1.3, label="measured (pipeline)"); ax.plot(f, Z["N"], color="#555", lw=1.0, ls="--", label="exact two-view prediction (no fit)")
ax.plot(f, Z["T"], color="#1b6ca8", lw=1.8, label="planted position"); ax.axhline(0, color="k", lw=0.5)
ax.set_xlabel("frame"); ax.set_ylabel("floor deviation (R)"); ax.set_title("(b) sequential render: reading 90° out of phase with the wall", fontsize=10); ax.legend(fontsize=7.5, loc="lower left"); ax.set_xlim(f.min(), f.max())
# (c) quadrature fit per condition
R = {k: v for k, v in json.load(open("runs/theory/exact_geom.json")).items() if v["align_rms_R"] <= 0.1}
grp = [("sequential\nconstant\nspeed", lambda k: k.startswith("M_G") and "cb" not in k), ("stop-\nand-go", lambda k: k.startswith("MS_")), ("scope\nriding\nbreath", lambda k: k.startswith("M_G1cb")), ("phase-\ngated", lambda k: k.startswith("K4_"))]
ax = fig.add_subplot(gs[2]); summ = {}
for i, (nm, sel) in enumerate(grp):
    ks = [k for k in R if sel(k)]; pos = np.array([R[k]["meas"]["c"] / R[k]["T"]["c"] for k in ks]); vel = np.array([abs(R[k]["meas"]["q"]) / R[k]["T"]["c"] for k in ks])
    ax.bar(i - 0.18, np.median(pos), 0.34, color="#1b6ca8"); ax.bar(i + 0.18, np.median(vel), 0.34, color="#c0392b")
    ax.plot(np.full(len(pos), i - 0.18), pos, "k.", ms=3); ax.plot(np.full(len(vel), i + 0.18), vel, "k.", ms=3); ax.text(i, -0.9, f"n={len(ks)}", ha="center", fontsize=7.5)
    summ[nm.replace("\n", " ")] = dict(n=len(ks), position_median=float(np.median(pos)), position_range=[float(pos.min()), float(pos.max())], velocity_median=float(np.median(vel)), velocity_range=[float(vel.min()), float(vel.max())])
ax.axhline(1, color="k", ls=":", lw=1); ax.set_xticks(range(len(grp))); ax.set_xticklabels([g[0] for g in grp], fontsize=7.5); ax.set_ylim(-1.2, None)
ax.set_ylabel("coefficient / planted position"); ax.set_title("(c) position (blue) and velocity (red) terms", fontsize=10)
fig.savefig("docs/figures/paper/fig_stereo_artifact.png", dpi=150, bbox_inches="tight"); json.dump(summ, open("docs/figures/paper/fig_stereo_artifact.json", "w"), indent=1); print(json.dumps(summ, indent=1))
