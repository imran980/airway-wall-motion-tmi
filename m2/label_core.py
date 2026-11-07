"""The clinician-label statistic, in one place.

Both the real test (m2/label_test_combine.py) and the calibration harness (tests/label_fpr.py) must compute the
SAME number, or the false-positive rate measured on synthetic data says nothing about the real p-value. Having two
implementations agree by inspection is not good enough, so there is one implementation and both import it.

The statistic: per (frame, station, sector) radius, in units of the tube radius, with that sector's own time mean
removed; the mean over an ARC minus the median over the sectors outside the arc and a guard (common-mode removal);
the median over the stations a frame sees. Then the difference of means between OUT-labelled and IN-labelled frames,
pooled within run. The null circularly shifts the label sequence, which keeps its rhythm and destroys only its
alignment.
"""
import os, subprocess, tempfile, shutil, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from station_frame import frame_from_grid


def q2R(q):
    w, x_, y_, z_ = q
    return np.array([[1-2*(y_*y_+z_*z_), 2*(x_*y_-z_*w), 2*(x_*z_+y_*w)],
                     [2*(x_*y_+z_*w), 1-2*(x_*x_+z_*z_), 2*(y_*z_-x_*w)],
                     [2*(x_*z_-y_*w), 2*(y_*z_+x_*w), 1-2*(x_*x_+y_*y_)]])


def load(run, min_cos=0.25, min_sectors=3):
    """A reconstruction's per-sector deviations, and the floor direction fixed by camera geometry alone."""
    G = np.load(f"{run}/m1_real_grid.npz"); r = G["r_grid"]; R = float(G["R"]); S = G["S"]; fr = G["frames"]
    sup = G["support"] if "support" in G.files else np.isfinite(r); cos = G["cos_grid"]
    nb = r.shape[2]; deg = (np.arange(nb) + 0.5) / nb * 360 - 180
    N1, N2, _ = frame_from_grid(G)                        # the frame the grid was binned in, never a fresh guess
    rr = np.where(sup & (cos >= min_cos), r, np.nan) / R
    with np.errstate(all="ignore"): x = rr - np.nanmean(rr, axis=0)[None]
    vis = np.isfinite(rr).sum(2) >= min_sectors
    td = tempfile.mkdtemp()
    try:
        subprocess.run([os.environ.get("BRONCHO_COLMAP", "colmap"), "model_converter",
                        "--input_path", f"{run}/dense/sparse", "--output_path", td, "--output_type", "TXT"],
                       capture_output=True, check=True)
        P = {}
        for l in [l for l in open(f"{td}/images.txt") if l.strip() and not l.startswith("#")][0::2]:
            t = l.split(); P[int("".join(c for c in os.path.basename(t[9]) if c.isdigit()))] = q2R(np.array(list(map(float, t[1:5])))).T
    finally:
        shutil.rmtree(td, ignore_errors=True)
    down = np.full((len(fr), 3), np.nan)
    for j, f_ in enumerate(fr):
        if int(f_) in P: down[j] = P[int(f_)][:, 1]       # COLMAP looks along +z with +y DOWN in the image
    floor = np.full(len(S), np.nan)
    for i in range(len(S)):
        k = np.where(vis[:, i] & np.isfinite(down[:, 0]))[0]
        if len(k) < 3: continue
        c1 = (down[k] * N1[i]).sum(1); c2 = (down[k] * N2[i]).sum(1); ang = np.degrees(np.arctan2(c2, c1))
        m = np.array([np.cos(np.radians(ang)).mean(), np.sin(np.radians(ang)).mean()])
        floor[i] = np.degrees(np.arctan2(m[1], m[0]))
    return dict(x=x, vis=vis, fr=fr, deg=deg, nb=nb, floor=floor)


def arc_sectors(nb, deg, centre_deg, arc_width, guard):
    k_arc = max(3, int(round(arc_width / (360.0 / nb))))
    if k_arc % 2 == 0: k_arc += 1          # an even arc cannot be centred on a sector; it biases every angle by half one
    c = int(np.argmin(np.abs((deg - centre_deg + 180) % 360 - 180)))
    idx = [(c + d - k_arc // 2) % nb for d in range(k_arc)]
    out = [b for b in range(nb) if min((b - c) % nb, (c - b) % nb) > k_arc // 2 + guard]
    return idx, out


def pooled(D, offset, arc_width=60.0, guard=2, min_stations=3, keep=None, weight="boxcar"):
    """The per-frame deviation at the arc, one value per frame. Depends on the ARC only, never on the labels.

    weight="boxcar" is the original: the mean over a 60 deg arc minus the median over the sectors outside it.
    weight="cosine" is the matched filter for a DIPOLE - a wall swinging in on one side and out on the other, which
    is the shape the arc scan actually shows. It weights every sector by cos(theta - centre) instead of using six of
    them and discarding the rest, so it uses the whole ring and is the efficient estimator if the motion really is
    dipolar. The weights are re-centred on whichever sectors a frame actually measured, which makes common-mode
    rejection exact rather than approximate: a ring that simply changes size contributes nothing.
    """
    dev = np.full(D["x"].shape[:2], np.nan)
    th = np.radians(D["deg"])
    for i in range(D["x"].shape[1]):
        cd = D["floor"][i] + offset
        if not np.isfinite(cd): continue
        if weight == "cosine":
            w0 = np.cos(th - np.radians(cd))
            X = D["x"][:, i, :]; fin = np.isfinite(X)
            W = np.where(fin, w0[None, :], np.nan)
            with np.errstate(all="ignore"):
                W = W - np.nanmean(W, axis=1, keepdims=True)         # exact common-mode rejection on the sectors present
                num = np.nansum(np.where(fin, W * X, 0.0), axis=1)
                den = np.nansum(np.where(fin, np.abs(W), 0.0), axis=1)
                val = np.where(den > 1e-9, num / np.maximum(den, 1e-9), np.nan)
            dev[:, i] = np.where(D["vis"][:, i] & (fin.sum(1) >= 6), val, np.nan)
            continue
        idx, out = arc_sectors(D["nb"], D["deg"], cd, arc_width, guard)
        with np.errstate(all="ignore"):
            arc = np.nanmean(D["x"][:, i, idx], axis=1); cm = np.nanmedian(D["x"][:, i, out], axis=1)
        dev[:, i] = np.where(D["vis"][:, i], arc - cm, np.nan)
    if keep is not None: dev[:, ~keep] = np.nan
    with np.errstate(all="ignore"): s = np.nanmedian(dev, axis=1)
    s[np.isfinite(dev).sum(1) < min_stations] = np.nan
    return s


def score(series, ks, labmap, min_frames=4):
    """Mean within-run (OUT minus IN) difference. `series` is [(name, per-frame values, frame->index), ...]."""
    diffs = []; tot = 0
    for _nm, s_, fset in series:
        have = [(k, s_[fset[k]]) for k in ks if k in fset and np.isfinite(s_[fset[k]])]
        if len(have) < min_frames: continue
        kk = [h[0] for h in have]; vv = np.array([h[1] for h in have]); yy = np.array([labmap[k] for k in kk])
        if (yy > 0).sum() < 2 or (yy < 0).sum() < 2: continue
        diffs.append(vv[yy < 0].mean() - vv[yy > 0].mean()); tot += len(kk)
    return (float(np.mean(diffs)) if diffs else np.nan), tot, len(diffs)


def shift_null(series, ks, ys, min_frames=4):
    """Every distinct circular shift. Returns (observed, null values, their lags)."""
    base = {k: v for k, v in zip(ks, ys)}
    stat, n, nr = score(series, ks, base, min_frames)
    null = []; lags = []
    for sh in range(1, len(ys)):
        st, _, _ = score(series, ks, {k: v for k, v in zip(ks, np.roll(ys, sh))}, min_frames)
        if np.isfinite(st): null.append(st); lags.append(sh)
    return stat, n, nr, np.array(null), np.array(lags)


def exact_p(stat, null):
    """Conservative (k+1)/(n+1). The shift null is discrete: n labels give at most n-1 outcomes."""
    if not len(null) or not np.isfinite(stat): return np.nan
    return float((np.sum(null >= stat) + 1) / (len(null) + 1))
