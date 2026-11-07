"""Item 7 (docs/PREREG_r6_reviewer_items_2026-10-27.md): identifiability of wall position vs velocity under static two-view stereo.
On-axis exact two-view model r_hat/r = beta(1+eps)/(beta+eps), median over the frame's sources, for a wall r = R(1 + a cos phi).
Per policy and regime: quadrature coefficients (c, q) of (r_hat - R)/R, |q|/|c|, the in-phase bias produced by a label-phase error delta,
and the phase accuracy needed for <= 20 % position error (sigma_delta <= 0.2 |c| / |q|). Overlays the measured render and clinical
|q|/|c| at their |eps/beta|. Writes runs/r6/identifiability.json and docs/figures/paper/fig_identifiability.png"""
import json, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
a = 0.07; R = 1.0
def readout(s, d, P, policy, n=600):
    t = np.arange(n); ph = 2 * np.pi * t / P; r = R * (1 + a * np.cos(ph)); z = s * t                                     # camera axial position (toward the wall point: +)
    if policy == "sequential": taus = [-5, -4, -3, 3, 4, 5]
    elif policy == "phase-gated": taus = [-int(round(P)), int(round(P))]
    rh = np.full(n, np.nan)
    for i in range(n):
        vals = []
        for tau in taus:
            j = i + tau
            if 0 <= j < n:
                beta = (z[j] - z[i]) / d; eps = (r[j] - r[i]) / r[i]
                if abs(beta + eps) > 1e-9: vals.append(r[i] * beta * (1 + eps) / (beta + eps))
        if vals: rh[i] = np.median(vals)
    ok = np.isfinite(rh) & (np.abs(rh - R) < 2.0); X = np.c_[np.cos(ph[ok]), np.sin(ph[ok]), np.ones(ok.sum())]
    c, q, _ = np.linalg.lstsq(X, (rh[ok] - R) / R, rcond=None)[0]; return float(c), float(q)
res = {"model": []}
for policy in ("sequential", "phase-gated"):
    for s in (0.005, 0.008, 0.013, 0.02, 0.026, 0.035, 0.05, 0.08):
        for d in (1.25, 2.0, 3.0):
            for P in (30, 48, 79, 134):
                eb = a * (2 * np.pi / P) * d / (s * R); c, q = readout(-s, d, P, policy)
                res["model"].append(dict(policy=policy, s=s, d=d, P=P, eps_over_beta=eb, c=c, q=q, q_over_c=abs(q) / max(abs(c), 1e-9),
                                         sigma_delta_max_rad=0.2 * abs(c) / max(abs(q), 1e-9), sigma_delta_max_frames=0.2 * abs(c) / max(abs(q), 1e-9) * P / (2 * np.pi)))
M = [m for m in res["model"] if m["policy"] == "sequential"]; G = [m for m in res["model"] if m["policy"] == "phase-gated"]
print("model, sequential: |q|/|c| vs |eps/beta|  (median over d, P at similar |eps/beta|)")
for lo, hi in ((0, 0.1), (0.1, 0.3), (0.3, 0.6), (0.6, 1.2), (1.2, 5)):
    sel = [m for m in M if lo <= m["eps_over_beta"] < hi]
    if sel: print(f"  |e/b| {lo}-{hi}: n {len(sel):2d} |q|/|c| median {np.median([m['q_over_c'] for m in sel]):6.2f} | c/a median {np.median([m['c'] for m in sel]) / a:+.2f} | phase accuracy for <=20 % error: {np.median([m['sigma_delta_max_rad'] for m in sel]) * 180 / np.pi:5.1f} deg")
print(f"model, phase-gated: |q|/|c| median {np.median([m['q_over_c'] for m in G]):.3f}, c/a median {np.median([m['c'] for m in G]) / a:+.2f}")
# measured points
EG = json.load(open("runs/theory/exact_geom.json")); rend = [dict(run=k, eb=v["eps_over_beta_median"], qc=abs(v["meas"]["q"]) / abs(v["meas"]["c"]), gated=k.startswith("K4_")) for k, v in EG.items() if v["align_rms_R"] <= 0.1 and v["eps_over_beta_median"] is not None]
I3 = json.load(open("runs/r6/item3.json")); clin = [dict(clip=k, eb=I3["regime"][k2]["eps_over_beta_median"], qc=I3["clinical"][k]["q_over_c"]) for k, k2 in (("2-V2", "2-V2"), ("2-V2 rec B", "2-V2"), ("20-V1 wd", "20-V1 wd"))]
res["renders"] = rend; res["clinical"] = clin
RP = json.load(open("runs/r6/item1_regime.json")); rep = [dict(run=k, eb=v["eps_over_beta_median"], qc=v["q_over_c"]) for k, v in RP.items()]; res["replays"] = rep   # item 1 (descriptive regime)
lab_err = {"2-V2": 2 * 2 * np.pi / 78, "20-V1 wd": 2 * 2 * np.pi / 48}                                                    # +-2-frame label timing (the plateau check's tolerance)
print("label timing +-2 frames as phase:", {k: f"{v * 180 / np.pi:.0f} deg" for k, v in lab_err.items()})
for c_ in clin: print(f"  clinical {c_['clip']}: |e/b| {c_['eb']:.2f}, measured |q|/|c| {c_['qc']:.2f}")
print("renders (sequential): |q|/|c| median", round(float(np.median([r["qc"] for r in rend if not r["gated"]])), 2), "at |e/b| median", round(float(np.median([r["eb"] for r in rend if not r["gated"]])), 2))
fig, ax = plt.subplots(1, 2, figsize=(12, 4.3))
for pol, col in (("sequential", "#c0392b"), ("phase-gated", "#1b6ca8")):
    S_ = sorted([m for m in res["model"] if m["policy"] == pol], key=lambda m: m["eps_over_beta"])
    ax[0].scatter([m["eps_over_beta"] for m in S_], [max(m["q_over_c"], 0.012) for m in S_], s=10, color=col, alpha=0.5, label=f"two-view model, {pol}" + (" (|q|/|c| ≈ 0, drawn at the floor)" if pol == "phase-gated" else ""))
ax[0].scatter([r["eb"] for r in rend if not r["gated"]], [r["qc"] for r in rend if not r["gated"]], marker="s", s=28, facecolor="none", edgecolor="#c0392b", label="renders, sequential (measured)")
ax[0].scatter([r["eb"] for r in rend if r["gated"]], [r["qc"] for r in rend if r["gated"]], marker="s", s=28, facecolor="none", edgecolor="#1b6ca8", label="renders, phase-gated (measured)")
for nm, key, mk in (("2-V2", "2V2", "D"), ("20-V1", "20V1", "^")): ax[0].scatter([r["eb"] for r in rep if key in r["run"]], [r["qc"] for r in rep if key in r["run"]], marker=mk, s=40, facecolor="none", edgecolor="#1e8449", lw=1.4, zorder=4, label=f"replays of the {nm} camera path (measured)")
for c_ in clin: ax[0].scatter(c_["eb"], c_["qc"], marker="*", s=140, color="k", zorder=5); ax[0].annotate(c_["clip"], (c_["eb"], c_["qc"]), fontsize=7, xytext=(6, -10) if "rec" in c_["clip"] else ((-30, 2) if c_["clip"] == "2-V2" else (6, 4)), textcoords="offset points")
ax[0].axhline(1, color="k", ls=":", lw=0.8); ax[0].set_xscale("log"); ax[0].set_yscale("log"); ax[0].set_ylim(0.01, 1000); ax[0].set_xlabel("|ε/β| = v d / (s r)"); ax[0].set_ylabel("|q| / |c|  (velocity / position)")
ax[0].set_title("(a) velocity contamination of the position reading", fontsize=10); ax[0].legend(fontsize=7, loc="upper left")
S_ = sorted(M, key=lambda m: m["eps_over_beta"]); ax[1].scatter([m["eps_over_beta"] for m in S_], [m["sigma_delta_max_rad"] * 180 / np.pi for m in S_], s=10, color="#c0392b", alpha=0.5, label="sequential (model)")
for k, v in lab_err.items(): ax[1].axhline(v * 180 / np.pi, color="0.4", ls="--", lw=0.8); ax[1].text(0.045, v * 180 / np.pi * 1.08, f"±2-frame label timing, {k}", fontsize=7, color="0.3")
ax[1].set_xscale("log"); ax[1].set_yscale("log"); ax[1].set_xlabel("|ε/β|"); ax[1].set_ylabel("phase accuracy needed for ≤ 20 % position error (deg)")
ax[1].set_title("(b) label timing needed to separate position from velocity", fontsize=10); ax[1].legend(fontsize=7)
plt.tight_layout(); plt.savefig("docs/figures/paper/fig_identifiability.png", dpi=150); json.dump(res, open("runs/r6/identifiability.json", "w"), indent=1); print("saved")
