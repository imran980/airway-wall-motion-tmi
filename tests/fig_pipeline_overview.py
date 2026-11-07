"""Paper figure: pipeline overview as a flow of boxes with the checks each result carries. Output docs/figures/paper/fig_pipeline.png"""
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
fig, ax = plt.subplots(figsize=(13, 4.6)); ax.set_xlim(0, 13); ax.set_ylim(0, 4.6); ax.axis("off")
def box(x, y, w, h, title, body, fc="#f3f6f9", ec="#1b6ca8"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h - 0.22, title, ha="center", va="top", fontsize=9.5, fontweight="bold", color="#1b1b1b")
    ax.text(x + w / 2, y + h - 0.55, body, ha="center", va="top", fontsize=7.6, color="#333", linespacing=1.35)
def arrow(x0, y0, x1, y1): ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=12, lw=1.2, color="#555"))
y0 = 2.0; h = 1.9; w = 1.95; xs = [0.25, 2.45, 4.65, 6.85, 9.05]
box(xs[0], y0, w, h, "1. Frames", "sequential decode\nbezel mask, CLAHE\nper-session calibration\n(intrinsics pinned)")
box(xs[1], y0, w, h, "2. Rigid SfM + MVS", "COLMAP, pinned intrinsics\nPatchMatch depth\nsources ≥ 3 steps apart\n(baseline, not time)")
box(xs[2], y0, w, h, "3. Stations", "camera path = centreline\nslabs every 0.2 R\n36 sectors, recentred\non the lumen axis")
box(xs[3], y0, w, h, "4. Per-frame rings", "sector radius per frame\ncanonical ring = median\nfloor = image-down\n(posterior wall)")
box(xs[4], y0, w, h, "5. Statistic", "floor arc − other sectors\nOUT − IN at the clinician's\nbreathing extremes\nshift-null p, in R units")
for a, b in zip(xs[:-1], xs[1:]): arrow(a + w, y0 + h / 2, b, y0 + h / 2)
box(11.25, y0, 1.6, h, "Result", "detection, null below\nthe limit, or\nnot measurable", fc="#e8f1e8", ec="#2e7d4f"); arrow(xs[4] + w, y0 + h / 2, 11.25, y0 + h / 2)
# checks row
cy = 0.15; ch = 1.45; cw = 2.45; cx = [0.25, 2.85, 5.45, 8.05, 10.65]
checks = [("Detection limit", "shift-null floor at the\nclip's own window: the\nsmallest detectable separation"), ("Controls", "roof and side arcs\nmust stay ≈ 0"), ("Label-shift profile", "plateau over ±8 frames\n= a position reading;\na ramp = velocity"), ("Window consistency", "every leave-one-window-out\nvalue positive and near\nthe pooled value"), ("Independent check", "feature pair test on\nnear-identical-pose frames;\nplanted-truth validated")]
for x, (t, b) in zip(cx, checks): box(x, cy, cw if x < 10 else 2.1, ch, t, b, fc="#fbf7ee", ec="#b8860b")
ax.text(0.25, y0 + h + 0.35, "Reconstruction (unchanged production pipeline)", fontsize=10, fontweight="bold", color="#1b6ca8")
ax.text(0.25, cy + ch + 0.12, "Every reported number carries these checks", fontsize=10, fontweight="bold", color="#b8860b")
fig.savefig("docs/figures/paper/fig_pipeline.png", dpi=170, bbox_inches="tight"); print("saved")
