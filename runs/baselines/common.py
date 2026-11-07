"""Shared pieces for the round-3 baselines (docs/PREREG_r3_list3_2026-10-22.md, amendment 2): sequential frame reading, scope circle and
dark-lumen centre, arc masks, and the SAME label statistic, nulls and five detection conditions used for the pipeline."""
import json, cv2, numpy as np
ARCS = {"floor": 90.0, "roof": -90.0, "s90": 0.0, "s270": 180.0}            # image angle of each arc centre (image-down = +y = 90 deg)
def read_span(video, lo, hi, size=(640, 360)):
    cap = cv2.VideoCapture(video); f = 0; out = {}
    while f <= hi:
        ok, im = cap.read()
        if not ok: break
        if f >= lo: out[f] = cv2.resize(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), size, interpolation=cv2.INTER_AREA).astype(np.float32)
        f += 1
    return out
def scope_circle(g):
    m = g > 12; ys, xs = np.nonzero(m); cy, cx = ys.mean(), xs.mean(); r = np.sqrt(((ys - cy) ** 2 + (xs - cx) ** 2).max()) * 0.95; return cy, cx, r
def lumen_centre(g, circ, pct=10, sigma=2):
    gb = cv2.GaussianBlur(g, (0, 0), sigma); thr = np.percentile(gb[circ], pct); n, lab = cv2.connectedComponents(((gb <= thr) & circ).astype(np.uint8))
    if n < 2: return None, None
    k = 1 + int(np.argmax(np.bincount(lab.ravel())[1:])); ys, xs = np.nonzero(lab == k); return (ys.mean(), xs.mean()), lab == k
def angdiff(a, b): return np.abs((a - b + 180) % 360 - 180)
def labels(labf):
    L = json.load(open(labf)); O = set(map(int, L["outward"])); I = set(map(int, L["inward"])); return {f: (-1 if f in O else 1) for f in sorted(O | I)}
def score(series, fs, lab):
    ks = [k for k in lab if k in fs and np.isfinite(series[fs[k]])]
    if len(ks) < 8: return np.nan
    v = np.array([series[fs[k]] for k in ks]); y = np.array([lab[k] for k in ks])
    if (y < 0).sum() < 2 or (y > 0).sum() < 2: return np.nan
    return float(v[y < 0].mean() - v[y > 0].mean())
def runs_of(fs_):
    r = []
    for k in sorted(fs_):
        if r and k - r[-1][1] <= 1: r[-1][1] = k
        else: r.append([k, k])
    return r
def evaluate(S, fs, lab):
    """S: dict arc -> per-frame array; fs: frame -> index; lab: frame -> -1 (OUT) / +1 (IN). Circular shifts over every labelled frame."""
    ks = np.array([k for k in sorted(lab) if k in fs]); ys = np.array([lab[k] for k in ks]); L0 = {k: lab[k] for k in ks}
    T = score(S["floor"], fs, L0)
    null = []; lags = []
    for sh in range(1, len(ys)):
        t = score(S["floor"], fs, dict(zip(ks, np.roll(ys, sh))))
        if np.isfinite(t): null.append(t); lags.append(sh)
    null, lags = np.array(null), np.array(lags)
    if not np.isfinite(T) or len(null) < 20: return dict(T=T, ok=False)
    st = [i for i in range(len(ys)) if ys[i] < 0 and (i == 0 or ys[i - 1] >= 0)]; cyc = float(np.median(np.diff(st))) if len(st) >= 2 else np.nan
    off = ((lags / cyc) % 1 >= 0.25) & ((lags / cyc) % 1 <= 0.75) if np.isfinite(cyc) else np.zeros(len(lags), bool)
    p = float(np.mean(null >= T)); Lim = float(np.percentile(null, 95)); p_off = float(np.mean(null[off] >= T)) if off.sum() >= 20 else np.nan
    ctr = [score(S[a], fs, L0) for a in ("roof", "s90", "s270")]
    prof = [score(S["floor"], fs, {k + d: v for k, v in L0.items()}) for d in (-2, -1, 1, 2)]
    loo = [score(S["floor"], fs, {k: v for k, v in L0.items() if not (v < 0 and w[0] <= k <= w[1])}) for w in runs_of([k for k in L0 if L0[k] < 0])]
    chk = dict(sig=bool(p < 0.05 and T > 0), ctrl=bool(T > 0 and all(np.isfinite(c) and abs(c) < 0.5 * T for c in ctr)), plat=bool(T > 0 and all(np.isfinite(x) and x >= 0.5 * T for x in prof)),
               win=bool(T > 0 and all(np.isfinite(x) and x >= T / 3 for x in loo)), minT=bool(T >= 0.02))
    return dict(ok=True, T=T, p=p, L=Lim, p_off=p_off, controls=ctr, plateau=prof, checks=chk, detected=bool(all(chk.values())), detected_off=bool(all(v for k, v in chk.items() if k != "sig") and np.isfinite(p_off) and p_off < 0.05), sd=float(np.nanstd(S["floor"])))
