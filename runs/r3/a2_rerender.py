"""A2 (docs/PREREG_r3_list3_2026-10-22.md): re-render frame 0 of one synthetic run with the tagged renderer from its stored parameters
(truth.npz) + seed/noise from the run name, and compare with frame 0 of the stored video. Prints one JSON line. Usage: a2_rerender.py RUN_DIR OUT_TMP"""
import sys, os, re, json, subprocess, tempfile, numpy as np, cv2
run, tmp = sys.argv[1], sys.argv[2]; name = os.path.basename(run.rstrip("/")); T = np.load(f"{run}/truth.npz")
g = lambda k, d=None: (T[k].item() if k in T.files and T[k].size == 1 else d)
m = re.search(r"_s(\d+)", name); seed = int(m.group(1)) if m else 0; mn = re.search(r"n(\d+)_s", name); noise = int(mn.group(1)) / 1000 if mn else 0.006
args = ["--amp", g("amp"), "--sigma", g("sigma"), "--period", g("period"), "--offset", g("offset"), "--tilt", g("tilt"), "--speed", g("speed"), "--fx", g("fx"), "--W", g("W"), "--H", g("H"),
        "--mask-r", g("mask_r", 0.265), "--period-jitter", g("period_jitter", 0.0), "--cam-breath", g("cam_breath", 0.0), "--move-frames", g("move_frames", 0), "--pause-frames", g("pause_frames", 0),
        "--tex", 0.18, "--tex-blur", 1.0, "--seed", seed, "--noise", noise, "--frames", len(T["poses"]), "--only", 1]
out = os.path.join(tmp, name); cmd = [sys.executable, "tests/render_breathing_tube.py", "--out", out] + [str(x) for x in args]
r = subprocess.run(cmd, capture_output=True, text=True); res = dict(run=run, seed=seed, noise=noise, cmd=" ".join(cmd[1:]))
cap = cv2.VideoCapture(f"{run}/video.mp4"); ok, v = cap.read(); im = cv2.imread(f"{out}/images/f00000.png")
if r.returncode or im is None or not ok: res.update(status="render_failed" if r.returncode or im is None else "no_video", err=r.stderr[-300:])
else:
    d = float(np.abs(im.astype(float) - v.astype(float)).mean()); res.update(status="match" if d < 1.5 else "MISMATCH", mean_abs_diff=round(d, 3))
print(json.dumps(res), flush=True)
subprocess.run(["rm", "-rf", out])
