"""Re-extract a labelled span with the production preprocessing (sequential decode, bezel mask, CLAHE 3.0 on L) into a persistent dir,
and draw a contact sheet with the clinician's OUT windows marked (red border) for an eye check of the labels.
Usage: python tests/extract_span.py --video V --labels L.json --out runs/frames_CLIP [--every 6]"""
import argparse, json, os, sys, numpy as np, cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "m1"))
ap = argparse.ArgumentParser(); ap.add_argument("--video", required=True); ap.add_argument("--labels", required=True); ap.add_argument("--out", required=True); ap.add_argument("--every", type=int, default=6); ap.add_argument("--pad", type=int, default=10); a = ap.parse_args()
lab = json.load(open(a.labels)); lo, hi = lab["span_frames"][0] - a.pad, lab["span_frames"][1] + a.pad; outf = set(lab["outward"]); exc = set(f for w in lab.get("excluded_unlabelled_cycles", []) for f in range(w[0], w[1] + 1))
def bezel(video, n=60):
    cap = cv2.VideoCapture(video); N = int(cap.get(7)); H = int(cap.get(4)); W = int(cap.get(3)); cum = np.zeros((H, W), np.int32)
    for fi in np.linspace(0, max(N - 1, 0), n).astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(fi)); ok, f = cap.read()
        if ok: cum += (f.mean(2) > 8).astype(np.int32)
    cap.release(); m = ((cum >= max(int(0.2 * n), 5)).astype(np.uint8)) * 255
    return cv2.erode(cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)), np.ones((7, 7), np.uint8), iterations=5) > 0
os.makedirs(f"{a.out}/images", exist_ok=True); mask = bezel(a.video); clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
cap = cv2.VideoCapture(a.video); fi = 0; thumbs = []; n = 0
while True:
    ok, fr = cap.read()
    if not ok or fi > hi: break
    if lo <= fi <= hi:
        l = cv2.cvtColor(fr, cv2.COLOR_BGR2LAB); l[:, :, 0] = clahe.apply(l[:, :, 0]); im = cv2.cvtColor(l, cv2.COLOR_LAB2BGR); im[~mask] = 0
        cv2.imwrite(f"{a.out}/images/f{fi:05d}.png", im, [cv2.IMWRITE_PNG_COMPRESSION, 1]); n += 1
        if (fi - lo) % a.every == 0:
            t = cv2.resize(im, (320, 180)); col = (0, 0, 255) if fi in outf else ((128, 128, 128) if fi in exc else (0, 160, 0))
            cv2.rectangle(t, (0, 0), (319, 179), col, 4 if fi in outf else 2); cv2.putText(t, f"f{fi}" + (" OUT" if fi in outf else (" excl" if fi in exc else "")), (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2); thumbs.append(t)
    fi += 1
cap.release(); cols = 10; rows = (len(thumbs) + cols - 1) // cols; sheet = np.zeros((rows * 180, cols * 320, 3), np.uint8)
for i, t in enumerate(thumbs): sheet[(i // cols) * 180:(i // cols + 1) * 180, (i % cols) * 320:(i % cols + 1) * 320] = t
cv2.imwrite(f"{a.out}/contact_sheet.png", sheet); print(f"{a.out}: {n} frames f{lo}-{hi} (sequential decode), contact sheet {len(thumbs)} thumbs (red = PI OUT window, grey = excluded unlabelled cycle)")
