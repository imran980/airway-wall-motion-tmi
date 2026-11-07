"""A1: manifest of every synthetic run (docs/supplement/synthetic_manifest.csv)."""
import os, re, csv, json, hashlib, glob, numpy as np
A2 = {json.loads(l)["run"]: json.loads(l) for l in open("runs/r3/a2_rerender.jsonl")}
rows = []
for d in [l.strip() for l in open("runs/r3/a3_runs.txt")]:
    name = os.path.basename(d); T = np.load(f"{d}/truth.npz"); g = lambda k: (T[k].item() if k in T.files and T[k].size == 1 else "")
    m = re.search(r"_s(\d+)", name); mn = re.search(r"n(\d+)_s", name); src = d[len("K4_"):] if False else d.replace("/K4_", "/")
    grid = f"{d}/m1/m1_real_grid.npz"; h = hashlib.sha256(open(grid, "rb").read()).hexdigest()[:16]
    rows.append(dict(run=name, dir=d, sources="phase-gated (K4)" if name.startswith("K4_") else "sequential", seed=int(m.group(1)) if m else 0, amp=g("amp"), sigma_deg=g("sigma"), period=g("period"),
                     offset_R=g("offset"), tilt_deg=g("tilt"), speed_R_per_frame=g("speed"), period_jitter=g("period_jitter"), cam_breath_R=g("cam_breath"), move_frames=g("move_frames"), pause_frames=g("pause_frames"),
                     noise=int(mn.group(1)) / 1000 if mn else 0.006, tex=0.18, tex_blur=1.0, frames=len(T["poses"]), grid_sha256_16=h,
                     render_check=A2.get(src, {}).get("status", "no video (K4 shares its twin's video)" if name.startswith("K4_") else "no video"),
                     score_original=f"runs/r3/rescore/orig/{name}.json", score_offphase=f"runs/r3/rescore/off/{name}.json",
                     sfm_cmd="m1/real_sfm_relaxed.py --video video.mp4 --calib calib.json --lo 0 --hi 299 --overlap 30", mvs_cmd="m1/windowed_depth_real.py SFM --max-size 1000 --recentre --ahead 0.5,5.0 --frame global --radius-from rings --min-baseline 3 --max-gap 12" + (" --phase-json phase.json" if name.startswith("K4_") else "")))
with open("docs/supplement/synthetic_manifest.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
import collections; print(len(rows), "runs;", collections.Counter(r["render_check"] for r in rows))
