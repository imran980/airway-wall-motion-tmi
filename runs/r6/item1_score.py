"""Item 1 (docs/PREREG_r6_reviewer_items_2026-10-27.md): score the replay renders (clinical camera path + clinician breathing timing) with
the unchanged rule on the clinician's labels (runs/baselines/common.evaluate, the same call used for the C3VD null), the camera check
(pose retention >= 70 %, same sign; item 3b) and the quadrature fit S_t = c cos(PH) + q sin(PH) + k with the planted phase table PH.
Reference: a perfect floor reading = amp * cos(PH) * k_arc, k_arc = mean Gaussian weight on the 60-deg floor arc minus the median outside,
scored with the same OUT-IN statistic (T_truth). Predictions: R1 rigid replays accept nothing; R2 motion replays read + with |q| < |c|."""
import os, sys, json, numpy as np, pycolmap
from scipy.spatial.transform import Rotation
sys.path.insert(0, "m2"); import label_core as LC
sys.path.insert(0, "runs/baselines"); import common as C
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
SY = "/var/tmp/mi3dr_r6/synth"
RUNS = ["M_rep2V2_s131", "M_rep2V2_s132", "N_rep2V2_s133", "N_rep2V2_s134", "M_rep20V1_s135", "M_rep20V1_s136", "N_rep20V1_s137", "N_rep20V1_s138"]
def fidx(n): return int("".join(c for c in os.path.basename(n) if c.isdigit()))
def cams(m1, Rg):                                                                                   # as runs/r6/item3.py
    rec = pycolmap.Reconstruction(f"{m1}/dense/sparse"); ims = sorted(rec.images.values(), key=lambda im: fidx(im.name)); fr = np.array([fidx(im.name) for im in ims])
    cw = [im.cam_from_world() if callable(im.cam_from_world) else im.cam_from_world for im in ims]; Rm = Rotation.from_matrix(np.array([np.asarray(x.rotation.matrix()) for x in cw])); rel = (Rm * Rm.mean().inv()).as_rotvec()
    Cc = np.array([np.asarray(im.projection_center()) for im in ims]); ax = np.linalg.svd(Cc - Cc.mean(0))[2][0]; P = (Cc - Cc.mean(0)) / Rg; z = P @ ax; lat = P - np.outer(z, ax); e1 = np.linalg.svd(lat)[2][0]; e2 = np.cross(ax, e1)
    return {int(f): v for f, v in zip(fr, np.c_[rel, z, lat @ e1, lat @ e2])}
def pose_retention(S, fs, lab, cam):                                                                # as runs/r6/item3.py
    rr = [f for f in sorted(lab) if f in fs and np.isfinite(S[fs[f]]) and f in cam]
    if len(rr) < 20: return np.nan, np.nan, np.nan
    y = np.array([S[fs[f]] for f in rr]); ind = np.array([1.0 if lab[f] < 0 else 0.0 for f in rr]); X = np.array([cam[f] for f in rr])
    b0 = np.linalg.lstsq(np.c_[ind, np.ones(len(rr))], y, rcond=None)[0][0]; b1 = np.linalg.lstsq(np.c_[ind, X, np.ones(len(rr))], y, rcond=None)[0][0]
    return float(b0), float(b1), float(b1 / b0) if abs(b0) > 1e-9 else np.nan
out = {}; fig, axs = plt.subplots(len(RUNS), 1, figsize=(11, 2.0 * len(RUNS)), sharex=False)
for ax_, tag in zip(axs, RUNS):
    D0 = f"{SY}/{tag}"; m1 = f"{D0}/m1"; T = np.load(f"{D0}/truth.npz"); PH = T["phase_table"]; amp = float(T["amp"]); sig = float(T["sigma"])
    th = np.linspace(-180, 180, 3601)[:-1]; w = np.exp(-(th / sig) ** 2); k_arc = w[np.abs(th) <= 30].mean() - np.median(w[np.abs(th) > 30])
    D = LC.load(m1); fs = {int(f): j for j, f in enumerate(D["fr"])}; S4 = {"floor": LC.pooled(D, 0.0), "roof": LC.pooled(D, 180.0), "s90": LC.pooled(D, 90.0), "s270": LC.pooled(D, 270.0)}
    lab = C.labels(f"{D0}/labels_clinician.json"); e = C.evaluate(S4, fs, lab)
    truth = amp * k_arc * np.cos(PH); fs_t = {f: f for f in range(len(PH))}; T_truth = C.score(truth, fs_t, lab) if amp > 0 else 0.0
    ks = [k for k in lab if k in fs and np.isfinite(S4["floor"][fs[k]])]; y = np.array([S4["floor"][fs[k]] for k in ks]); phi = PH[ks]
    c, q, _ = np.linalg.lstsq(np.c_[np.cos(phi), np.sin(phi), np.ones(len(ks))], y, rcond=None)[0]
    b0, b1, ret = pose_retention(S4["floor"], fs, lab, cams(m1, float(np.load(f"{m1}/m1_real_grid.npz")["R"])))
    cam_ok = bool(np.isfinite(ret) and ret >= 0.7 and np.sign(b1) == np.sign(b0))
    r = dict(amp=amp, k_arc=float(k_arc), T=e.get("T"), T_truth=float(T_truth), p=e.get("p"), limit=e.get("L"), checks=e.get("checks"), detected=e.get("detected"), pose_retention=ret, camera_ok=cam_ok,
             detected_with_camera_check=bool(e.get("detected") and cam_ok), c=float(c), q=float(q), q_over_c=float(abs(q) / abs(c)), c_truth=float(amp * k_arc), n_frames_scored=len(ks), n_frames=len(PH))
    out[tag] = r
    print(f"{tag:15s} T {r['T']:+.4f} (truth {T_truth:+.4f}) p {r['p']:.3f} lim {r['limit']:.4f} checks {''.join('Y' if v else 'n' for v in r['checks'].values())} detected {r['detected']} | pose ret {ret:+.2f} -> with cam {r['detected_with_camera_check']} | "
          f"c {c:+.4f} (truth {amp * k_arc:+.4f}) q {q:+.4f} |q|/|c| {r['q_over_c']:.2f} | frames {len(ks)}/{len(PH)}")
    sf = S4["floor"]; fr = np.array(sorted(fs)); ax_.plot(fr, [sf[fs[f]] for f in fr], ".-", ms=2, lw=0.6, label="floor reading")
    ax_.plot(np.arange(len(PH)), truth, "k-", lw=1, label="planted (floor arc)")
    for f in [k for k in lab if lab[k] < 0]: ax_.axvspan(f - 0.5, f + 0.5, color="tab:orange", alpha=0.15, lw=0)
    ax_.set_ylabel("R"); ax_.set_title(f"{tag}: T {r['T']:+.3f} (truth {T_truth:+.3f}), p {r['p']:.3f}, detected {r['detected']}, |q|/|c| {r['q_over_c']:.2f}", fontsize=8); ax_.set_ylim(-0.12, 0.12)
axs[0].legend(fontsize=7, loc="upper right"); axs[-1].set_xlabel("render frame (orange = clinician OUT)"); fig.tight_layout(); fig.savefig("runs/r6/item1_series.png", dpi=110)
M = [r for t, r in out.items() if t.startswith("M")]; N = [r for t, r in out.items() if t.startswith("N")]
print(f"R1 rigid accepts: {sum(r['detected'] for r in N)}/{len(N)} (with camera check {sum(r['detected_with_camera_check'] for r in N)}/{len(N)})")
print(f"R2 motion: sign + {sum(r['T'] > 0 for r in M)}/{len(M)}; |q|<|c| {sum(r['q_over_c'] < 1 for r in M)}/{len(M)}; detected {sum(r['detected'] for r in M)}/{len(M)} (with camera check {sum(r['detected_with_camera_check'] for r in M)}/{len(M)})")
json.dump(out, open("runs/r6/item1.json", "w"), indent=1, default=float)
