"""Paper figure: what the instrument cannot measure. (a) 26-V2 collapse stretch: the wall folds into the lumen and the rigid reconstruction
loses registration at f1907-1920; (b) 16-V2 and (c) 13-V1: PI-confirmed pulsatile wall motion that fragments the rigid reconstruction;
(d) MonST3R on a real window: bowl-shaped depth without a lumen. Frames are decoded sequentially from the videos. Output docs/figures/paper/fig_failure_taxonomy.png"""
import cv2, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
def circ(im, s=320):
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY); ys, xs = np.nonzero(g > 12); x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max(); c = im[y0:y1, x0:x1]; c = cv2.resize(c, (s, s)); return cv2.cvtColor(c, cv2.COLOR_BGR2RGB)
fig = plt.figure(figsize=(13, 9.0)); sub = fig.subfigures(4, 1, hspace=0.06, height_ratios=[1, 1, 1, 1.05])
rows = [("(a) 26-V2, suspected posterior-wall collapse: the wall folds into the lumen and the rigid reconstruction loses registration at f1907–1920 (the minimum-lumen phase); the image-domain pair test fails there too", "26V2", [1898, 1904, 1910, 1916, 1922, 1928], lambda f: 1907 <= f <= 1920),
        ("(b) 16-V2, pulsatile wall motion at the heart rate (clinician-confirmed): the reconstruction splits into interleaved sub-models", "16V2", [700, 712, 724, 736, 748, 760], lambda f: False),
        ("(c) 13-V1, low-amplitude pulsation (clinician-confirmed): only a fragment reconstructs", "13V1", [800, 812, 824, 836, 848, 860], lambda f: False)]
for sf, (title, tag, frames, bad) in zip(sub[:3], rows):
    sf.suptitle(title, fontsize=9.6, x=0.01, ha="left"); axs = sf.subplots(1, 6)
    for ax, f in zip(axs, frames):
        ax.imshow(circ(cv2.imread(f"runs/fig_frames/{tag}_f{f:05d}.png"))); ax.axis("off"); ax.set_title(f"f{f}" + ("  unregistered" if bad(f) else ""), fontsize=8.5, color=("#c0392b" if bad(f) else "#222"), pad=3)
sf = sub[3]; sf.suptitle("(d) a learned 4-D reconstruction (MonST3R) on a real 2-V2 window: depth is a shallow bowl with no lumen (far/near 1.3; a tube seen down its axis gives ≥ 4)\n     and a depth slab in the ring plane is a crescent, not a ring", fontsize=9.6, x=0.01, ha="left", y=1.08)
z = np.load("runs/base_monst3r/2V2_w0/npz/win0000.npz"); i = 24; rgb = z["rgb"][i]; d = z["depth"][i]; K = z["K"][0]; ok = (rgb.max(-1) > 12) & (d > 0)
axs = sf.subplots(1, 3, width_ratios=[1, 1.08, 1])
axs[0].imshow(rgb); axs[0].set_title(f"input frame f{int(z['frames'][i])}", fontsize=8.5, pad=3)
im = axs[1].imshow(np.where(ok, d, np.nan), cmap="turbo"); axs[1].set_title("MonST3R depth (relative units)", fontsize=8.5, pad=3); cb = sf.colorbar(im, ax=axs[1], fraction=0.045, pad=0.02); cb.ax.tick_params(labelsize=7)
h, w = d.shape; v, u = np.mgrid[0:h:2, 0:w:2]; dd = d[::2, ::2]; o = ok[::2, ::2]
X = np.stack([(u[o] - K[0, 2]) / K[0, 0] * dd[o], (v[o] - K[1, 2]) / K[1, 1] * dd[o], dd[o]], 1); far = X[X[:, 2] >= np.quantile(X[:, 2], 0.9)]; ax_ = far.mean(0); ax_ /= np.linalg.norm(ax_)
down = np.array([0, 1.0, 0]); down -= (down @ ax_) * ax_; down /= np.linalg.norm(down); right = np.cross(ax_, down); zz = X @ ax_; lo, hi = np.quantile(zz, [0.25, 0.75]); sl = (zz > lo) & (zz < hi); P = X[sl]
axs[2].scatter(P @ right, P @ down, s=1, c=zz[sl], cmap="viridis"); axs[2].set_aspect("equal"); axs[2].invert_yaxis(); axs[2].set_title("its points in the ring plane (25–75 % depth slab)", fontsize=8.5, pad=3); axs[2].set_xticks([]); axs[2].set_yticks([])
for ax in axs[:2]: ax.axis("off")
fig.savefig("docs/figures/paper/fig_failure_taxonomy.png", dpi=150, bbox_inches="tight"); print("saved")
