"""Fig. 4 (regenerated 2026-10-22): floor OUT-IN versus label shift k = -8..8.
(a) HELD-OUT renders (seeds 61-70, never used in development), true-phase labels (OUT = cos(phase) >= cos 30 deg), sequential vs phase-gated
    sources, with the planted truth T*(k) = amp * wbar * (mean cos phase at OUT - at IN) under the same shifted labels (dashed).
(b) Retained clinical grids with the clinician labels; the k = 0 detection limit L0.05 (primary circular-shift null, calibrated frame set) drawn as a tick."""
import sys, json, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "m2"); import label_core as LC
# (no offphase_lib import: it replaces LC.shift_null globally)
K = np.arange(-8, 9); SY = "/scratch/mi3dr_v31/synth"
TH = np.linspace(-30, 30, 61); wbar = lambda s: float(np.mean(np.exp(-(TH / s) ** 2)))
def curve(m1, lab):
    D = LC.load(m1); fs = {int(f): j for j, f in enumerate(D["fr"])}; S = LC.pooled(D, 0.0); out = []
    for k in K:
        mm = {f + k: v for f, v in lab.items() if (f + k) in fs and np.isfinite(S[fs[f + k]])}; kk = np.array(sorted(mm)); out.append(LC.score([("r", S, fs)], kk, mm)[0])
    return np.array(out), S, fs
fig, ax = plt.subplots(1, 2, figsize=(12, 5.0)); rec = {}
for kind, pre, col in (("sequential sources", "", "tab:red"), ("phase-gated sources", "K4_", "tab:blue"), ("rigid-wall null (sequential)", "", "0.5")):
    seeds = ["N_G1_s66", "N_G2_s67", "N_G1cb_s68", "NS_G1_s69", "NS_G2_s70"] if "null" in kind else ["M_G1_s61", "M_G2_s62", "M_G1irr_s63", "M_G1cb_s64", "MS_G1_s65"]
    C = []; Ts = []
    for s in seeds:
        T = np.load(f"{SY}/{s}/truth.npz"); PH = T["phase_table"] if "phase_table" in T.files else 2 * np.pi * np.arange(len(T["poses"])) / float(T["period"])
        D = LC.load(f"{SY}/{pre}{s}/m1"); fin = [int(f) for f, v in zip(D["fr"], LC.pooled(D, 0.0)) if np.isfinite(v)]
        lab = {f: (-1 if np.cos(PH[f]) >= np.cos(np.radians(30)) else 1) for f in range(min(fin), max(fin) + 1)}
        c, _, _ = curve(f"{SY}/{pre}{s}/m1", lab); C.append(c)
        w = wbar(float(T["sigma"])); amp = float(T["amp"]); ts = []
        for k in K:
            mm = {f + k: v for f, v in lab.items() if 0 <= f + k < len(PH)}; ks = np.array(sorted(mm)); ys = np.array([mm[q] for q in ks]); cs = np.cos(PH[ks]); ts.append(amp * w * (cs[ys < 0].mean() - cs[ys > 0].mean()))
        Ts.append(ts)
        ax[0].plot(K, c, color=col, alpha=0.25, lw=1)
    C = np.array(C); ax[0].plot(K, np.median(C, 0), color=col, lw=2.2, marker="o", ms=3, label=f"{kind} (median of 5)"); rec[kind] = dict(seeds=seeds, curves=C.tolist())
    if "null" not in kind and pre == "": Tm = np.median(np.array(Ts), 0); ax[0].plot(K, Tm, "k--", lw=1.8, label="planted truth $T^*(k)$"); rec["truth"] = Tm.tolist()
ax[0].axhline(0, color="k", lw=0.5); ax[0].set_xlabel("label shift k (frames)"); ax[0].set_ylabel("floor OUT$-$IN ($R$)"); ax[0].set_title("(a) Held-out renders, planted 0.07$R$ motion", fontsize=10); ax[0].legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False)
CL = [("2-V2 (normal)", "runs/g6_2v2", "2V2_f2870_f3370", "tab:green"), ("20-V1 wd (malacia, exploratory)", "runs/m1_20V1_lab", "20V1_f2517_f2823", "tab:purple"),
      ("18-V1 (not detected)", "runs/m1_18V1_lab", "18V1_f450_f760", "tab:orange"), ("26-V2 (null)", "runs/m1_26V2_lab_m1", "26V2_f780_f1210", "0.5")]
for name, m1, labf, col in CL:
    L = json.load(open(f"labels/{labf}.json")); O = set(map(int, L["outward"])); I = set(map(int, L["inward"])); lab = {f: (-1 if f in O else 1) for f in sorted(O | I)}
    c, S, fs = curve(m1, lab); ks = np.array([f for f in sorted(lab) if f in fs]); ys = np.array([lab[f] for f in ks])       # primary rule: every registered labelled frame (as calibrated)
    T0, n, nr, null, lags = LC.shift_null([("r", S, fs)], ks, ys); Lim = float(np.percentile(null, 95)); p = float(np.mean(null >= T0))
    ax[1].plot(K, c, color=col, lw=2, marker="o", ms=3, label=f"{name}: k=0 {c[8]:+.3f}, $L_{{0.05}}$ {Lim:.3f}"); ax[1].plot([-0.4, 0.4], [Lim, Lim], color=col, lw=3, alpha=0.6)
    rec[name] = dict(curve=c.tolist(), L=Lim, p=p)
ax[1].axhline(0, color="k", lw=0.5); ax[1].axvspan(-2, 2, color="0.9", zorder=0); ax[1].set_xlabel("label shift k (frames)"); ax[1].set_title("(b) Clinical windows, clinician labels (bars at k=0: detection limit)", fontsize=10); ax[1].legend(fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False)
plt.tight_layout(); plt.savefig("docs/figures/paper/fig_label_shift.png", dpi=150); json.dump(rec, open("docs/figures/paper/fig_label_shift.json", "w"), indent=1)
for k_, v in rec.items():
    if "curve" in v: print(f"{k_:20s} k=-2..2 " + " ".join(f"{x:+.3f}" for x in v["curve"][6:11]) + f" | k=+-8 {v['curve'][0]:+.3f} {v['curve'][-1]:+.3f} | L {v['L']:.3f} p {v['p']:.3f}")
    elif "curves" in v: m = np.median(np.array(v["curves"]), 0); print(f"{k_:30s} median k=-2..2 " + " ".join(f"{x:+.3f}" for x in m[6:11]))
print("truth k=-2..2", " ".join(f"{x:+.3f}" for x in rec["truth"][6:11]))
