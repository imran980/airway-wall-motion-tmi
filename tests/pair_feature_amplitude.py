"""P-DENSE, sparse-feature form: the PI's two-landmark pair test with hundreds of automatically matched features per pair. For each
near-identical-pose OUT/IN pair: SIFT matches IN<->OUT (ratio test), the pose rotation removed analytically, a zoom + translation model
(k, tx, ty about the dark-lumen centre) fitted robustly to the NON-floor matches (|angle from image-down| > 60 deg), and the residual
outward fractional shift drho/rho of the FLOOR-arc matches (|angle| <= 30 deg) = S for that pair, in R units like the pipeline's floor
OUT-IN. Usage: pair_feature_amplitude.py --frames DIR --model SPARSE --labels L.json --out DIR --R R_model [--pairs-json sealed.json] [--max-pairs 400] [--images-from-pairs DIR]"""
import argparse, json, os, subprocess, tempfile, numpy as np, cv2
ap = argparse.ArgumentParser(); ap.add_argument("--frames", default=None); ap.add_argument("--model", required=True); ap.add_argument("--labels", required=True); ap.add_argument("--out", required=True); ap.add_argument("--R", type=float, required=True)
ap.add_argument("--width", type=int, default=960); ap.add_argument("--max-angle", type=float, default=2.0); ap.add_argument("--max-lateral", type=float, default=0.05); ap.add_argument("--max-axial", type=float, default=0.5); ap.add_argument("--min-gap", type=int, default=6); ap.add_argument("--max-gap", type=int, default=90)
ap.add_argument("--max-pairs", type=int, default=400); ap.add_argument("--pairs-json", default=None); ap.add_argument("--null", action="store_true", help="control: pairs drawn from IN x IN frames (random breathing-phase differences) - S must be ~0"); ap.add_argument("--images-from-pairs", default=None, help="use the 960-px pair images pNN_L/R.jpg of this human_pairs dir (when the frames dir is gone)"); ap.add_argument("--truth", default=None); ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--matcher", choices=["sift", "roma"], default="sift", help="correspondences: SIFT + ratio test (default, unchanged) or RoMa dense matches (CVPR K1)"); ap.add_argument("--roma-num", type=int, default=5000, help="RoMa matches sampled per pair (certainty-weighted)"); a = ap.parse_args()
os.makedirs(a.out, exist_ok=True); COLMAP = os.environ.get("BRONCHO_COLMAP", "colmap")
def q2R(q):
    w, x, y, z = q; return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
with tempfile.TemporaryDirectory() as td:
    subprocess.run([COLMAP, "model_converter", "--input_path", a.model, "--output_path", td, "--output_type", "TXT"], check=True, capture_output=True)
    cam = [l.split() for l in open(f"{td}/cameras.txt") if l.strip() and not l.startswith("#")][0]; W0, H0 = int(cam[2]), int(cam[3]); prm = [float(x) for x in cam[4:]]
    if cam[1] in ("PINHOLE", "OPENCV"): K0 = np.array([[prm[0], 0, prm[2]], [0, prm[1], prm[3]], [0, 0, 1]]); dist = np.array(prm[4:8] + [0] * (4 - len(prm[4:8]))) if cam[1] == "OPENCV" else np.zeros(4)
    else: K0 = np.array([[prm[0], 0, prm[1]], [0, prm[0], prm[2]], [0, 0, 1]]); dist = np.zeros(4)
    poses = {}
    for l in [l for l in open(f"{td}/images.txt") if l.strip() and not l.startswith("#")][0::2]:
        f = l.split(); Rm = q2R(np.array(list(map(float, f[1:5])))); t = np.array(list(map(float, f[5:8]))); poses[int(os.path.splitext(f[9])[0].lstrip("f"))] = (Rm.T, -Rm.T @ t)
s = a.width / W0; W, H = a.width, int(round(H0 * s)); K = K0.copy(); K[:2] *= s; R = a.R
lab = json.load(open(a.labels)); img_cache = {}
if a.images_from_pairs:
    meta = json.load(open(f"{a.images_from_pairs}/sealed.json"))
    for p in meta["pairs"]:
        L, Rr = (p["out_frame"], p["in_frame"]) if p["out_left"] else (p["in_frame"], p["out_frame"]); img_cache[L] = f"{a.images_from_pairs}/images/p{p['pair']:02d}_L.jpg"; img_cache[Rr] = f"{a.images_from_pairs}/images/p{p['pair']:02d}_R.jpg"
def load(f):
    if f in img_cache: return cv2.imread(img_cache[f])
    im = cv2.imread(f"{a.frames}/f{f:05d}.png"); return cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA)
avail = set(img_cache) if a.images_from_pairs else set(int(f[1:6]) for f in os.listdir(a.frames) if f.endswith(".png"))
OUT = [k for k in sorted(set(int(x) for x in lab["outward"])) if k in poses and k in avail]; IN = [k for k in sorted(set(int(x) for x in lab["inward"])) if k in poses and k in avail]
if a.null:                                                      # control pairs within ONE label class (random breathing-phase differences): the larger class is split in two
    big = IN if len(IN) >= len(OUT) else OUT; OUT, IN = big[0::2], big[1::2]
if a.pairs_json: pairs = [(p["out_frame"], p["in_frame"], p["pair"]) for p in json.load(open(a.pairs_json))["pairs"] if not p["repeat"]]
else:
    cand = []
    for o in OUT:
        Ro, Co = poses[o]
        for i in IN:
            if not (a.min_gap <= abs(o - i) <= a.max_gap): continue
            Ri, Ci = poses[i]; ang = np.degrees(np.arccos(np.clip(Ro[:, 2] @ Ri[:, 2], -1, 1))); m = Ro[:, 2] + Ri[:, 2]; m /= np.linalg.norm(m); dv = Ci - Co; ax = dv @ m; lat = np.linalg.norm(dv - ax * m) / R
            if ang < a.max_angle and lat < a.max_lateral and abs(ax) / R < a.max_axial: cand.append((o, i, -1))
    rng = np.random.default_rng(a.seed); rng.shuffle(cand); pairs = cand[:a.max_pairs]; print(f"{len(cand)} candidate pairs; scoring {len(pairs)}")
TR = None
if a.truth: T = np.load(a.truth); PH = T["phase_table"]; amp = float(T["amp"]); TR = lambda o, i: float(amp * (np.cos(PH[o]) - np.cos(PH[i])))
sift = cv2.SIFT_create(nfeatures=4000, contrastThreshold=0.01); bf = cv2.BFMatcher(cv2.NORM_L2)
if a.matcher == "roma":                                         # RoMa (romatch, MIT) from a local target dir; weights under TORCH_HOME
    import sys, torch; from PIL import Image; sys.path.insert(0, os.environ.get("ROMA_PYLIB", "/var/tmp/mi3dr_k1/pylib")); from romatch import roma_outdoor
    roma = roma_outdoor(device="cuda", use_custom_corr=False); torch.manual_seed(a.seed)   # native-torch local correlation (no fused CUDA kernel installed)
def correspondences(gi, go, mask, ci=None, co=None):
    """IN->OUT pixel correspondences (pI, pO) with the IN point inside the mask, or a failure key."""
    if a.matcher == "roma":
        warp, cert = roma.match(Image.fromarray(cv2.cvtColor(ci, cv2.COLOR_BGR2RGB)), Image.fromarray(cv2.cvtColor(co, cv2.COLOR_BGR2RGB)), device="cuda")  # colour frames
        m, _ = roma.sample(warp, cert, num=a.roma_num); kI, kO = roma.to_pixel_coordinates(m, H, W, H, W); pI, pO = kI.cpu().numpy(), kO.cpu().numpy()
        xi, yi = np.clip(pI[:, 0].astype(int), 0, W - 1), np.clip(pI[:, 1].astype(int), 0, H - 1); xo, yo = np.clip(pO[:, 0].astype(int), 0, W - 1), np.clip(pO[:, 1].astype(int), 0, H - 1)
        keep = (mask[yi, xi] > 0) & (mask[yo, xo] > 0); return (pI[keep], pO[keep]) if keep.sum() >= 40 else "few_matches"
    k1, d1 = sift.detectAndCompute(gi, mask); k2, d2 = sift.detectAndCompute(go, mask)
    if d1 is None or d2 is None or len(k1) < 50 or len(k2) < 50: return "few_keypoints"
    good = [m[0] for m in bf.knnMatch(d1, d2, k=2) if len(m) == 2 and m[0].distance < 0.75 * m[1].distance]
    if len(good) < 40: return "few_matches"
    return np.array([k1[m.queryIdx].pt for m in good]), np.array([k2[m.trainIdx].pt for m in good])
def lumen_centre(g):
    yy, xx = np.mgrid[0:g.shape[0], 0:g.shape[1]]; r = np.hypot(xx - W / 2, yy - H / 2) < 0.26 * W; thr = np.quantile(g[r], 0.03); m = r & (g <= thr); return np.array([xx[m].mean(), yy[m].mean()])
def rot_map(uv, Rin, Rout):
    x = cv2.undistortPoints(uv.reshape(-1, 1, 2).astype(np.float64), K, dist).reshape(-1, 2); d = np.concatenate([x, np.ones((len(x), 1))], 1) @ (Rin.T @ Rout).T; p, _ = cv2.projectPoints(d.reshape(-1, 1, 3), np.zeros(3), np.zeros(3), K, dist); return p.reshape(-1, 2)
rows = []; fail = {"few_keypoints": 0, "few_matches": 0, "few_region_matches": 0}
for o, i, pid in pairs:
    imo, imi = load(o), load(i); go, gi = cv2.cvtColor(imo, cv2.COLOR_BGR2GRAY), cv2.cvtColor(imi, cv2.COLOR_BGR2GRAY); c = (lumen_centre(gi.astype(float)) + lumen_centre(go.astype(float))) / 2
    mask = (np.hypot(*np.mgrid[0:H, 0:W][::-1] - c[:, None, None]) > 0.10 * W).astype(np.uint8) * (gi > 20).astype(np.uint8)
    cr = correspondences(gi, go, mask, imi, imo)
    if isinstance(cr, str): fail[cr] += 1; continue
    pI, pO = cr; pIr = rot_map(pI, poses[i][0], poses[o][0]); disp = pO - pIr
    rel = pIr - c; rho = np.linalg.norm(rel, axis=1); ang = np.degrees(np.arctan2(rel[:, 0], rel[:, 1])); band = (rho > 0.10 * W) & (rho < 0.27 * W)
    ref = band & (np.abs(ang) > 60); flo = band & (np.abs(ang) <= 30)
    if ref.sum() < 25 or flo.sum() < 8: fail["few_region_matches"] += 1; continue
    # robust zoom+translation fit on the reference matches (RANSAC-like: IRLS with Huber), then residual outward fraction on the floor matches
    M = np.concatenate([np.stack([np.ones(ref.sum()), np.zeros(ref.sum()), rel[ref, 0]], 1), np.stack([np.zeros(ref.sum()), np.ones(ref.sum()), rel[ref, 1]], 1)]); b = np.concatenate([disp[ref, 0], disp[ref, 1]]); w = np.ones(len(b))
    for _ in range(8):
        sol, *_ = np.linalg.lstsq(M * w[:, None], b * w, rcond=None); res = b - M @ sol; sc_ = 1.4826 * np.median(np.abs(res)) + 1e-6; w = np.minimum(1, 1.5 * sc_ / np.maximum(np.abs(res), 1e-6))
    tx, ty, k = sol; resid = disp - (np.array([tx, ty]) + k * rel); er = rel / rho[:, None]; out_frac = (resid * er).sum(1) / rho
    inl_ref = np.abs(res).reshape(2, -1).max(0) < 3 * sc_; S = float(np.median(out_frac[flo])); S_ref = float(np.median(out_frac[ref][inl_ref])) if inl_ref.sum() > 5 else np.nan
    rows.append(dict(pair=pid, out=o, inn=i, S=S, S_ref=S_ref, zoom_k=float(k), tx=float(tx), ty=float(ty), n_floor=int(flo.sum()), n_ref=int(ref.sum()), ref_resid_px=float(sc_), truth=(TR(o, i) if TR else None)))
json.dump(rows, open(f"{a.out}/pair_features.json", "w"), indent=1)
print(f"unscored pairs: {fail}")
if not rows: raise SystemExit(f"{a.out}: no pair could be scored")
S = np.array([r["S"] for r in rows]); print(f"{a.out}: {len(rows)} pairs scored (floor matches median {int(np.median([r['n_floor'] for r in rows]))}, reference {int(np.median([r['n_ref'] for r in rows]))}, reference residual {np.median([r['ref_resid_px'] for r in rows]):.1f} px); S: mean {S.mean():+.4f} ± {S.std(ddof=1)/np.sqrt(len(S)):.4f}, median {np.median(S):+.4f}, positive {np.mean(S > 0):.2f}; reference residual outward {np.nanmedian([r['S_ref'] for r in rows]):+.4f}")
if TR: t = np.array([r["truth"] for r in rows]); from scipy import stats; print(f"  TRUTH: planted mean {t.mean():+.4f}; S/true {S.mean()/t.mean():.2f}; Pearson {stats.pearsonr(S, t)[0]:+.2f}; sign agreement {np.mean(np.sign(S) == np.sign(t)):.2f}")
