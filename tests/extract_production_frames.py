"""Extract the pipeline's production frames (sequential decode, bezel mask, CLAHE) for a frame span without running SfM.
Mirrors m1/real_sfm_relaxed.py's extraction exactly (same bezel(), same CLAHE, same brightness gate). Usage:
python tests/extract_production_frames.py --video V --lo LO --hi HI --out DIR [--clahe 3.0] [--every 1]"""
import argparse, os, sys, numpy as np, cv2
ap = argparse.ArgumentParser(); ap.add_argument("--video", required=True); ap.add_argument("--lo", type=int, required=True); ap.add_argument("--hi", type=int, required=True)
ap.add_argument("--out", required=True); ap.add_argument("--clahe", type=float, default=3.0); ap.add_argument("--every", type=int, default=1); a = ap.parse_args()

def bezel(video, n=60):
    cap = cv2.VideoCapture(video); N = int(cap.get(7)); H = int(cap.get(4)); W = int(cap.get(3)); cum = np.zeros((H, W), np.int32)
    for fi in np.linspace(0, max(N - 1, 0), n).astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(fi)); ok, f = cap.read()
        if ok: cum += (f.mean(2) > 8).astype(np.int32)
    cap.release(); m = ((cum >= max(int(0.2 * n), 5)).astype(np.uint8)) * 255
    return cv2.erode(cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)), np.ones((7, 7), np.uint8), iterations=5) > 0

os.makedirs(a.out, exist_ok=True); mask = bezel(a.video); clahe = cv2.createCLAHE(clipLimit=a.clahe, tileGridSize=(8, 8))
cap = cv2.VideoCapture(a.video); fi = 0; n = 0; dark = 0
while True:
    ok, fr = cap.read()
    if not ok or fi > a.hi: break
    if a.lo <= fi <= a.hi and (fi - a.lo) % a.every == 0:
        lab = cv2.cvtColor(fr, cv2.COLOR_BGR2LAB)
        if lab[:, :, 0][mask].mean() * 100 / 255 >= 12:
            lab[:, :, 0] = clahe.apply(lab[:, :, 0]); im = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR); im[~mask] = 0
            cv2.imwrite(f"{a.out}/f{fi:05d}.png", im, [cv2.IMWRITE_PNG_COMPRESSION, 1]); n += 1
        else: dark += 1
    fi += 1
np.save(f"{a.out}/bezel_mask.npy", mask); print(f"{a.out}: {n} frames written (sequential decode), {dark} dark skipped, size {mask.shape}")
