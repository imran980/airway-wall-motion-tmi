"""Figure: same wall, two manoeuvres (20-V1). Left: CT midline AP height and LR width vs height above the carina, inspiration vs
expiration. Middle: CT wall displacement (exp - insp, in R_insp) for the posterior wall vs each lateral wall. Right: the pipeline's
quiet-breathing OUT-IN by ring arc on the labelled withdrawal window (0 = image-down = posterior wall). Usage: fig_ct_correlate.py"""
import json, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "m2"); import label_core as LC
S = json.load(open("reports/ct_ett_check/tubefree/sectors.json")); L = [l for l in S["levels"] if 2 <= l["h_mm"] <= 13]          # tube-free in both phases (tube tip ~25 mm insp / ~15 mm exp)
H = np.array([l["h_mm"] for l in L]); api = np.array([l["ap_insp_mm"] for l in L]); ape = np.array([l["ap_exp_mm"] for l in L]); lri = np.array([l["lr_insp_mm"] for l in L]); lre = np.array([l["lr_exp_mm"] for l in L]); R = np.array([l["R_insp_mm"] for l in L])
D = LC.load("runs/m1_20V1_lab"); lab = json.load(open("labels/20V1_f2517_f2823.json")); fs = {int(f): j for j, f in enumerate(D["fr"])}
m = {int(k): 1 for k in lab["inward"] if int(k) in fs}; m.update({int(k): -1 for k in lab["outward"] if int(k) in fs}); ks = np.array(sorted(m))
offs = np.arange(0, 360, 30); prof = np.array([LC.score([("r", LC.pooled(D, float(o)), fs)], ks, m)[0] for o in offs])
fig = plt.figure(figsize=(13, 4.2)); ax1 = fig.add_subplot(1, 3, 1); ax1.plot(H, api, "-", color="#1b6ca8", label="AP height, inspiration"); ax1.plot(H, ape, "--", color="#1b6ca8", label="AP height, expiration")
ax1.plot(H, lri, "-", color="#c0392b", label="LR width, inspiration"); ax1.plot(H, lre, "--", color="#c0392b", label="LR width, expiration"); ax1.set_xlabel("mm above the carina (tube-free levels)"); ax1.set_ylabel("mm"); ax1.set_title("CT: tracheal lumen, breath-held extremes", fontsize=10); ax1.legend(fontsize=7, loc="lower right"); ax1.set_ylim(0, None)
ax2 = fig.add_subplot(1, 3, 2); dap = (ape - api) / R; dlr = (lre - lri) / (2 * R)
ax2.plot(H, dap, "o-", ms=3, color="#1b6ca8", label="posterior wall (AP height change)"); ax2.plot(H, dlr, "s-", ms=3, color="#c0392b", label="each lateral wall (half LR change)"); ax2.axhline(0, color="k", lw=0.5)
ax2.axhline(-0.053, color="#555", lw=1, ls=":"); ax2.text(H.min() + 1, -0.053 - 0.11, "quiet-breathing video readout, same patient:\n0.043–0.053 R (not separable from scope motion)", fontsize=7, color="#555")
ax2.set_xlabel("mm above the carina"); ax2.set_ylabel("wall displacement, expiration − inspiration  (R_insp)"); ax2.set_title("CT: which wall moves", fontsize=10); ax2.legend(fontsize=7, loc="lower left")
ax3 = fig.add_subplot(1, 3, 3, projection="polar"); th = np.radians(np.r_[offs, 360]); pr = np.r_[prof, prof[0]]
ax3.plot(th, pr, "k-"); ax3.fill_between(th, 0, pr, where=pr > 0, color="#1b6ca8", alpha=0.35); ax3.plot(th, 0 * th, "k:", lw=0.5); ax3.set_theta_zero_location("S"); ax3.set_theta_direction(-1)
ax3.set_title("video pipeline: OUT−IN by ring arc (R)\n0° = image-down = posterior wall", fontsize=9); ax3.set_rlim(-0.03, 0.07)
fig.suptitle("20-V1 (tracheomalacia): CT deformation between breath-held extremes is posterior-dominant (posterior 0.61–1.04 R per level; lateral 0.03–0.52 R, largest near the carina)", fontsize=10)
fig.tight_layout(); fig.savefig("docs/figures/ct_correlate_20V1_tubefree.png", dpi=140); print("saved docs/figures/ct_correlate_20V1_tubefree.png; posterior median", float(np.nanmedian(dap)), "lateral", float(np.nanmedian(dlr)), "pipeline profile", prof.round(3).tolist())
