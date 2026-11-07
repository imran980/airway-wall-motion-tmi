"""Paper figure: workflow diagram built from real 2-V2 data (frame, reconstructed camera path and rings, one station's ring,
the per-frame floor series at the clinician's labels). Restrained styling. Output docs/figures/paper/fig_workflow.png"""
import json, sys, numpy as np, cv2, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Wedge
sys.path.insert(0, "m2"); import label_core as LC
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.linewidth": 0.6})
INK, GREY, ACC, ACC2 = "#222222", "#8a8a8a", "#b5452b", "#2f5f8a"
G = np.load("runs/g6_2v2/m1_real_grid.npz", allow_pickle=True); D = LC.load("runs/g6_2v2"); L = json.load(open("labels/2V2_f2870_f3370.json"))
S, C, N1, N2, CEN, RC = G["S"], G["C"], G["N1"], G["N2"], G["centre"], G["r_can"]; R = float(G["R"]); fr = np.array([int(f) for f in D["fr"]])
fig = plt.figure(figsize=(14, 4.2)); W = [0.01, 0.20, 0.42, 0.64, 0.84]; wd = [0.16, 0.19, 0.15, 0.15, 0.16]
def head(ax, n, t): ax.set_title(f"{n}  {t}", fontsize=9, loc="left", color=INK, pad=6)
# (a) input frame
ax = fig.add_axes([W[0], 0.22, wd[0], 0.62]); im = cv2.cvtColor(cv2.imread("runs/base_frames/2V2/f02942.png"), cv2.COLOR_BGR2RGB)
g = im.max(-1) > 12; ys, xs = np.nonzero(g); im = im[ys.min():ys.max(), xs.min():xs.max()]; ax.imshow(im); ax.axis("off"); head(ax, "a", "bronchoscopy video")
ax.text(0.5, -0.06, "sequential decode, bezel mask,\ncalibrated intrinsics held fixed", transform=ax.transAxes, ha="center", va="top", color=GREY, fontsize=7.5)
# (b) reconstruction: camera path + rings, oblique side view
ax = fig.add_axes([W[1], 0.22, wd[1], 0.62]); ax.axis("off"); head(ax, "b", "rigid SfM + multi-view stereo")
from scipy.ndimage import uniform_filter1d
Cs = uniform_filter1d(C, size=25, axis=0, mode="nearest"); u_, s_, vt = np.linalg.svd(S - S.mean(0)); ax_ = vt[0] * np.sign(vt[0] @ (S[-1] - S[0]))
up = N2[len(S) // 2] - (N2[len(S) // 2] @ ax_) * ax_; up /= np.linalg.norm(up); sd = np.cross(ax_, up)
z = (S - S[0]) @ ax_; seg = (z > z.max() * 0.30) & (z < z.max() * 0.30 + 7 * R); i_seg = np.nonzero(seg)[0]; i_seg = i_seg[: int(len(i_seg) * 0.8)]; z0 = z[i_seg[0]]
rm = float(np.nanmedian(RC[i_seg])); ctr = S.mean(0) - ((S.mean(0) - S[0]) @ ax_) * ax_
P = lambda X: np.stack([((X - S[0]) @ ax_ - z0) + 0.55 * ((X - ctr) @ sd), (X - ctr) @ up + 0.25 * ((X - ctr) @ sd)], -1)
th = np.linspace(0, 2 * np.pi, 160); back = np.sin(th) > 0
for i in i_seg[::5]:
    o = ctr + (z[i]) * ax_; r = float(np.nanmedian(RC[i])) if np.isfinite(RC[i]).any() else rm
    ring = o[None] + r * (np.cos(th)[:, None] * up[None] + np.sin(th)[:, None] * sd[None]); p = P(ring)
    ax.plot(p[~back, 0], p[~back, 1], color=GREY, lw=0.7); ax.plot(p[back, 0], p[back, 1], color=GREY, lw=0.5, ls=(0, (2, 2)), alpha=0.6)
for sgn in (1, -1):
    a = P(ctr + z[i_seg[0]] * ax_ + sgn * rm * up); b = P(ctr + z[i_seg[-1]] * ax_ + sgn * rm * up); ax.plot([a[0], b[0]], [a[1], b[1]], color=GREY, lw=0.7)
zc = (Cs - S[0]) @ ax_; m = (zc > z0) & (zc < z[i_seg[-1]]); pc = P(Cs[m]); ax.plot(pc[:, 0], pc[:, 1], color=ACC2, lw=1.4)
ax.text(pc[-1, 0] + 0.2 * rm, pc[-1, 1], "scope path", fontsize=7, color=ACC2, va="center")
ax.set_aspect("equal"); ax.text(0.5, -0.02, "dense depth from baseline-chosen sources;\nrings sampled at stations along the path", transform=ax.transAxes, ha="center", va="top", color=GREY, fontsize=7.5)
# (c) one station: canonical ring + one OUT frame and one IN frame
ax = fig.add_axes([W[2], 0.22, wd[2], 0.62], projection="polar"); head(ax, "c", "per-frame ring at a station")
cnt = np.isfinite(G["r_grid"]).sum((0, 2)); i = int(np.argmax(cnt)); deg = np.radians((np.arange(36) + 0.5) * 10 - 180); fl = np.radians(D["floor"][i])
rc = RC[i] / np.nanmedian(RC[i]); ax.plot(np.r_[deg, deg[0]] - fl, np.r_[rc, rc[0]], color=INK, lw=1.0, label="canonical ring")
out = set(L["outward"]); idx = {f: j for j, f in enumerate(fr)}; rg = G["r_grid"][:, i, :] / np.nanmedian(RC[i])
fo = [f for f in fr if f in out and np.isfinite(rg[idx[f]]).sum() > 20]; fi = [f for f in fr if f not in out and np.isfinite(rg[idx[f]]).sum() > 20]
if fo: ax.plot(deg - fl, rg[idx[fo[len(fo) // 2]]], ".", color=ACC, ms=3, label="frame at OUT")
if fi: ax.plot(deg - fl, rg[idx[fi[len(fi) // 2]]], ".", color=ACC2, ms=3, label="frame at IN")
ax.set_theta_zero_location("S"); ax.set_theta_direction(-1); ax.set_ylim(0, 1.4); ax.set_yticks([]); ax.set_xticks(np.radians([0, 90, 180, 270])); ax.set_xticklabels(["floor", "", "roof", ""], fontsize=7, color=GREY)
ax.add_patch(Wedge((0, 0), 1.4, -120, -60, transform=ax.transData._b, color=ACC, alpha=0.08))
ax.grid(color="#e6e6e6", lw=0.5); ax.legend(loc="upper left", bbox_to_anchor=(0.80, 1.02), fontsize=6.8, frameon=False, handletextpad=0.3)
# (d) floor series with labels
ax = fig.add_axes([W[3], 0.30, wd[3] + 0.02, 0.50]); head(ax, "d", "floor arc vs. rest of ring")
s = LC.pooled(D, 0.0); ax.plot(fr, s, color=INK, lw=0.7)
lab = np.array([f not in out for f in fr]); runs = []; start = None
for f, v in zip(fr, lab):
    if v and start is None: start = f
    if not v and start is not None: runs.append((start, f)); start = None
for a, b in runs: ax.axvspan(a, b, color=ACC, alpha=0.12, lw=0)
ax.axhline(0, color=GREY, lw=0.5); ax.set_xlabel("frame", color=GREY, fontsize=7.5); ax.set_ylabel("deviation (R)", color=GREY, fontsize=7.5)
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
ax.tick_params(labelsize=6.5, colors=GREY); ax.text(0.02, 0.97, "shaded: clinician-marked IN (lumen narrowest)", transform=ax.transAxes, va="top", fontsize=6.8, color=ACC)
# (e) readout and checks
ax = fig.add_axes([W[4], 0.12, wd[4], 0.74]); ax.axis("off"); head(ax, "e", "readout and checks")
TC = json.load(open("docs/figures/paper/table_cohort.json"))["2-V2"]                                       # same values as Table I
ax.text(0.0, 0.88, f"OUT − IN = {TC['T']:+.3f} R", fontsize=10, color=INK, fontweight="bold"); ax.text(0.0, 0.80, f"exact shift-null p = {TC['p']:.3f}", fontsize=7.8, color=GREY)
checks = ["detection limit from the clip's own null", "roof and side arcs as controls", "label-shift plateau (position, not velocity)", "leave-one-window-out", "test–retest on a new reconstruction", "independent feature-pair measurement"]
for k, c in enumerate(checks): ax.text(0.0, 0.66 - k * 0.095, "–  " + c, fontsize=7.6, color=INK)
# arrows between panels
for x0, x1 in ((W[0] + wd[0] + 0.003, W[1] - 0.003), (W[1] + wd[1] + 0.003, W[2] - 0.005), (W[2] + wd[2] + 0.005, W[3] - 0.03), (W[3] + wd[3] + 0.025, W[4] - 0.003)):
    fig.patches.append(FancyArrowPatch((x0, 0.53), (x1, 0.53), transform=fig.transFigure, arrowstyle="-|>", mutation_scale=9, lw=0.8, color=GREY))
fig.savefig("docs/figures/paper/fig_workflow.png", dpi=220, bbox_inches="tight", facecolor="white"); print("saved")
