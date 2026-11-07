# Real-tissue test on StereoMIS (2026-10-23) — declared before any monocular reconstruction of StereoMIS
Data: StereoMIS (Hayoz et al., IJCARS 2023; Zenodo 10.5281/zenodo.8154924; CC BY-NC-SA 4.0): in-vivo porcine abdomen, da Vinci Xi
stereo (top/bottom, 1280×1024 per eye, 26 fps), per-sequence stereo calibration (baseline 4.27 mm), per-frame forward-kinematics camera
poses, ventilated breathing. Not a lumen: tests the stereo mechanism and the fix, not the ring statistic.
Independent reference (no monocular method involved): rectified stereo depth per frame (OpenCV SGBM at half resolution, fixed parameters
declared in the code before use) → tissue points in the world frame via the kinematic camera pose → reference breathing displacement p(t)
of the tissue in the central image region (median, along the mean viewing direction) and its phase φ(t) (Hilbert phase of p band-passed
at 6–40 breaths/min).
Segment selection (fixed rule, applied by script before any monocular run): non-overlapping 600-frame windows (≈23 s) from all
sequences with (i) a clear breathing peak in p(t) (spectral peak in 6–40/min ≥ 5× the median band power) and (ii) camera motion from
kinematics with path length ≥ 10 mm over the window (so monocular SfM has a baseline). Up to 6 windows, earliest first, at most 2 per
sequence; each window's axial fraction a = |camera motion along the mean viewing direction| / |camera motion| is recorded.
Monocular arm: left frames only; COLMAP with pinned left intrinsics; production MVS with sequential sources (min-baseline 3, max-gap 12)
and, separately, phase-gated sources using the REFERENCE phase φ(t) (label-independent); per-frame median depth of the same central
region, scaled to mm by a similarity alignment of the SfM camera path to the kinematic path, minus camera motion along the viewing
direction → monocular displacement p̂(t).
Fit-free prediction: the numeric two-view model of runs/theory/exact_geom.py applied with kinematic poses and the reference tissue
trajectory (each tissue point moved by p(t) along the viewing direction), median over the actual sources.
Analysis: quadrature fit p̂(t) = c cos φ + q sin φ + k (and the same for the prediction and for p itself); report c/c_ref, |q|/c_ref,
Pearson(p̂, p), Pearson(p̂, prediction), per window and per source rule.
Predictions: (S1) phase-gated sources read position: |q| < 0.5|c| and c/c_ref in 0.5–1.5 in ≥ 2/3 of windows; (S2) sequential sources'
velocity contamination |q|/c_ref increases with the axial fraction a across windows (Spearman > 0); (S3) Pearson(p̂, prediction) ≥ 0.5
for sequential sources in ≥ 2/3 of windows. Any outcome is reported. If fewer than 3 windows qualify, the test is reported as not
possible on StereoMIS under this rule.

## Amendment 1 (before selection or any monocular run)
Sampling: the reference and the monocular arm use every second frame (the dataset's own step in sequences.txt), so a 600-frame window is
300 images at ≈13 fps, matching the 300-frame renders. Left frames are undistorted with the full 5-coefficient calibration (COLMAP's
OPENCV model has no k3) and passed to the unchanged production SfM as a zero-distortion pinhole video. Pose convention and translation
unit of groundtruth.txt (undocumented) are chosen by world-frame stability of the stereo tissue points over the whole sequence (4
candidates: camera-to-world or world-to-camera × metres or mm); no monocular quantity enters that choice.

## Amendment 2 (before any window is selected or any monocular run)
The whole-sequence spread criterion for the pose convention is ill-posed for a scanning camera (different tissue is in view, so the world
median point legitimately travels; all four candidates gave 32–64 mm). Replaced by a local criterion: for sample pairs 10 samples
(20 frames, ≈0.8 s) apart with ≥ 2 mm camera motion under the candidate, the median nearest-neighbour distance between the two frames'
stereo tissue points in the world frame (both directions); the candidate with the smallest median distance over all pairs is chosen.

## Amendment 3 (before any monocular run; prompted by a visual check of the reference, runs/stereomis/selection_check.png)
The central-region median tracks which tissue is in view when the camera moves (step changes of 5–130 mm, spectral peaks at the 6/min band
edge), so it is not a breathing reference. Static-camera segments (P3, camera path < 3 mm) show clean ventilation at 7.6/min, ≈7 mm
peak-to-peak (runs/stereomis/static_breathing.png). New reference: a FIXED world tissue patch — the stereo points of the window's middle
frame within the central region define a centre M and normal n (mean viewing direction); in every frame, the frame's stereo points in the
world frame within 15 mm of M (in the plane ⟂ n) give p(t) = median of (P − M)·n (NaN if < 20 points). Selection: p finite on ≥ 90 % of
samples; no step (|Δp| between consecutive samples < 2 mm); spectral peak in 6–20/min, ≥ 0.5/min inside the band edge, SNR ≥ 5; camera
path ≥ 5 mm (lowered from 10 mm because the ventilated segments move the camera little). Otherwise unchanged (300 samples, ≤ 2 per
sequence, ≤ 6 windows). If fewer than 3 windows qualify, the monocular test is reported as not possible on StereoMIS.

## Outcome (before any monocular run): the test is not possible on StereoMIS with this design
Under amendment 3, 8 windows qualified (6 selected), but the visual check (runs/stereomis/selection_check2.png) shows that none contains a
breathing waveform: fixed-patch p(t) is noise, flat stretches or steps of 0.1–3 mm, with no oscillation comparable to the static segments
(P3: clean 7.6/min, ≈7 mm peak-to-peak; runs/stereomis/static_breathing.png). Clean ventilation is visible only where the camera is
essentially still (path < 3 mm over 23 s at ≈100 mm depth, ≈1.5° of parallax), which is exactly the condition under which monocular SfM has
no baseline. StereoMIS therefore does not provide, in one window, the two things the test needs (an independent breathing reference and
enough camera translation). No monocular reconstruction was run and no further amendment is made; the paper reports this as a negative
finding about available public data. (Pose convention found: camera-to-world, metres; surface mismatch 2.1 mm vs ≥ 5.0 mm otherwise.)
