import sys, numpy as np
sys.path.insert(0, "/home/mi3dr/projects/airway-canonical-deform/m2"); import label_core as LC
_orig = LC.shift_null
def cycle_idx(ys):
    st = [i for i in range(len(ys)) if ys[i] < 0 and (i == 0 or ys[i - 1] >= 0)]
    return float(np.median(np.diff(st))) if len(st) >= 2 else np.nan
def shift_null_offphase(series, ks, ys, min_frames=4):
    stat, n, nr, null, lags = _orig(series, ks, ys, min_frames); c = cycle_idx(ys)
    if not np.isfinite(c) or len(lags) == 0: return stat, n, nr, np.array([]), np.array([])
    ph = (lags / c) % 1.0; keep = (ph >= 0.25) & (ph <= 0.75); return stat, n, nr, null[keep], lags[keep]
LC.shift_null = shift_null_offphase
