# Revision round 3, "list 3" (2026-10-22) — declared before running; code tagged `tmi-r3-start`
Scope agreed with the PI: (A) provenance of every synthetic number, (B) a render arm in the clinical regime of 20-V1, (C) phase-gated sources
as the method on real clips, (D) baselines. Nothing below changes the detection rule, its thresholds, the labels or the primary null.
Disk: /scratch has ~17 GB free and /home is at quota, so runs are sequential and delete stereo maps after each grid (as before).

A. Provenance
 A1 Manifest (docs/supplement/synthetic_manifest.csv): every synthetic run — directory, renderer parameters and seed (truth.npz), SfM and MVS
    command lines (from logs/scripts), grid file hash, scoring JSON(s).
 A2 Render reproducibility: re-render frame 0 of every run that still has its video with the tagged renderer and its stored parameters and seed;
    report mean |difference| per run (codec noise ≈ 0.6 grey level was seen on s61; a wrong parameter gives ≥ 2).
 A3 Score reproducibility: re-score every retained grid with the tagged scorer (tests/ablation_checks.py; off-phase via runs/v5/offphase.py)
    and compare per-trial outcomes with the stored JSONs (expected identical: deterministic seed).
 A4 End-to-end regeneration from scratch under the tag (render → SfM → MVS → score) of M_G1_s61, its K4 twin and N_G1_s66, into new
    directories; report T, acceptance and the change from the stored runs (this is reconstruction test–retest on renders).
B. Slow-scope arm (20-V1 regime): G1 geometry, axial speed 0.013 R/frame (20-V1's), otherwise the frozen renderer defaults; motion 0.07 R
   seeds 101, 102 (sequential and K4 phase-gated each), rigid-wall nulls seeds 103, 104 (sequential). Scored by the unchanged rule (original
   null primary; off-phase reported) and put through runs/theory/exact_geom.py. Predictions: (B1) nulls accept no trial under the rule;
   (B2) sequential motion renders are velocity-dominated, |q| > |c|, under the quadrature fit; (B3) K4 gives |q| < 0.5 |c|. Floor-arc |ε/β|
   reported (expected ~2× the constant-speed renders). Whatever the outcome, the paper reports it beside the 20-V1 result.
C. Phase-gated sources on real clips: first a diagnosis of why the existing real K4 grid (runs/k4_2V2) did not transfer (registered frames
   with ≥ 2 same-phase sources, baselines, floor coverage, readout). A real-data test is declared separately only after the diagnosis, before
   any new real K4 run is scored.
D. Baselines on the held-out renders (motion s61–s63, s71–s73; nulls s66–s70, s76–s80) and, where they produce a floor signal, the two
   clinical windows (2-V2, 20-V1): D1 dense optical flow (RAFT, torchvision weights) — posterior-boundary radial flow integrated over the
   labelled span → OUT−IN; D2 2-D lumen segmentation + tracking with its free parameters tuned ONLY on development renders (s21–s24, motion and
   s11–s16 nulls) and frozen before the held-out renders are touched; D3 one current non-rigid / deformable endoscopic reconstruction method
   with public code, if it installs and runs within the budget (otherwise reported as attempted). Each baseline is scored with the SAME
   label statistic and circular-shift null (four checks, T ≥ 0.02 R where it outputs R units). Report per-render detection and false
   detection, and clinical readouts.

## Amendment 1 (before A3 ran)
tests/ablation_checks.py and tests/null_calibration.py seeded each run's label trials with Python's hash(run name), which is randomised per
process (PYTHONHASHSEED unset; verified: two processes give 348 and 232 for 'M_G1_s61'). Stored per-trial outputs are therefore valid draws
but not bit-reproducible. Fixed to zlib.crc32(run name) (tag tmi-r3-scorer). A3 becomes: re-score every retained grid with the fixed
scorer (original and off-phase null), check that a second run reproduces it bit-for-bit, and compare rates with the stored draws (agreement
in distribution expected; differences reported). The re-scored set is the canonical one for the paper.

## C. Diagnosis (runs/r3/c_diagnosis.log) — and decision, before any new real phase-gated run
Existing real K4 grid (2-V2, phase from the clinician's labels, tol 0.35 rad, span 120; all 501 frames found ≥ 2 same-phase sources):
| grid | floor reading on OUT / IN frames | trusted cells per frame, median OUT / IN | T (R) | p | limit |
|---|---|---|---|---|---|
| sequential (g6_2v2) | 0.69 / 0.62 | 108 / 100 | +0.067 | 0.044 | 0.066 |
| phase-gated (k4_2V2) | 0.38 / 0.19 | 19 / 3 | +0.033 | 0.156 | 0.040 |
(1) Cross-cycle sources are 45–120 frames away, seen from a different scope position; PatchMatch keeps 5–30× fewer trusted cells, and
unevenly (IN frames lose more than OUT frames), so the OUT−IN contrast is computed on different, sparse subsets. 20-V1 (short OUT windows)
lost the sign entirely (earlier record). (2) More fundamentally: with label-derived phase the stereo sources depend on the labels, so the
circular-shift null is invalid — every shifted label sequence would need its own reconstruction. A label-independent respiratory phase is
therefore a precondition, not an option. Decision: no real phase-gated test is run in this round; phase-gated sources become the method only
with a recorded respiratory signal (ventilator / capnography) and cross-cycle matching robust to the change of viewpoint. Reported as such.

## Amendment 2 (before any baseline is run): baseline details
Common scoring (runs/baselines/common.py): per-frame series for the floor arc (image-down ±30°) and the roof/±90° control arcs, each as the
arc value minus the median outside the arc (as in the ring statistic), in fractional radius units (≈ R). Labels: each render's labels.json
(true phase) or the clinician's labels; all labelled frames in the sequence; circular-shift null (primary) and off-phase null (sensitivity);
detection = the same five conditions as the pipeline (sig, controls, plateau ±1/±2, leave-one-window-out ≥ T/3, T ≥ 0.02 R). The 3-D
pipeline is scored on the same renders with the same single label set for an apples-to-apples row.
D1 RAFT (torchvision raft_large, C_T_SKHT_V2 weights; frames at 640×360): frame-to-frame flow; per-pixel fractional radial flow u_r/ρ
about the tracked dark-lumen centre, annulus 0.2–0.9 of the scope radius excluding dark-lumen pixels; per-arc median minus out-of-arc median
= radial velocity; position = cumulative sum minus a centred 121-frame moving average. No tuned parameters.
D2 tuned 2-D segmentation: lumen = largest component below the q-th intensity percentile after Gaussian blur σ; boundary radius per 5° ray
by either the segmentation edge or the strongest gradient; arc radius / out-of-arc median − 1; temporal moving median of k frames. Grid
σ ∈ {1,2,4}, q ∈ {5,10,20,30}, boundary ∈ {seg, grad}, k ∈ {1,3,5}. Objective, fixed now: maximise the mean Pearson correlation between the
floor series and the true position cos φ over the development motion renders (M_G0_s21, M_G1_s22, M_G2_s23, M_G1irr_s24); ties (within
0.01) broken by the smaller mean |T| on the development nulls (N_G0_s11, N_G1_s12, N_G2_s13, N_G1cb_s15, N_G1irr_s16). Frozen before any
held-out render or clinical clip is processed.

## Amendment 3 (before running): D3a, a classical non-rigid baseline in addition to the agent's D3
D3a trajectory-basis non-rigid reconstruction (Park et al. 2010, cited in the paper) with the SAME SfM poses as the pipeline: CoTracker3
(scaled_offline checkpoint) tracks on a 16×16 grid inside the scope circle, queries every 60 frames, 150-frame chunks; for each track
(≥ 30 visible frames) the 3-D trajectory X(t) = Θ(t)β is solved by linear least squares from all its projections, with a DCT basis whose
frequency ceiling is fixed at 1/25 frames⁻¹ (K = 1 + floor(2·n/25) for n frames; covers every breathing period in the cohort, 30–134 frames;
not derived from labels) and a ridge of 1e-6 (relative). Each track's radial distance from the camera-path axis, divided by its own median,
minus 1 = fractional radial displacement; arcs by the track's mean angle about the axis relative to the mean camera down-vector (floor ±30°,
roof, ±90° sides); per frame the arc median minus the out-of-arc median. Scored with runs/baselines/common.evaluate. Same renders and
clinical windows as D1/D2 where an m1/dense/sparse model exists.

## A. Results (provenance)
A1 docs/supplement/synthetic_manifest.csv: 87 scored synthetic grids with renderer parameters, seed, SfM/MVS command, grid SHA-256 and
score files. A2 (runs/r3/a2_rerender.jsonl): 72 of 73 runs that still have their video re-render to the stored frame 0 from stored
parameters and seed (mean |difference| 0.63–0.75 grey levels = codec noise); the exception, eval_G0_re (5.3), is an early 144-frame test
with an unrecorded setting and is not used in the paper. A3: the scorer seeded trials with Python's per-process hash (amendment 1); fixed to
CRC32 (tag tmi-r3-scorer). The fixed scorer is bit-for-bit reproducible (two grids re-run: identical JSON). Re-scoring all 87 grids under both
nulls reproduces the stored rates in distribution: median change 0.000, mean −0.002, largest 0.088 (K4_M_G1a035_s91, off-phase), 99 % of
stored rates inside the new exact 95 % interval (docs/supplement/rescore_vs_stored.csv). Rigid-wall renders: 0 of 5,355 trials accepted
under either null (28 renders). The re-scored set (runs/r3/rescore) is the canonical one from here on.

## D. Results (runs/baselines/summary.txt; per-render JSON lines in runs/baselines/*.jsonl; visual check runs/baselines/fig_diag.png)
Same five-condition rule and circular-shift null for every method; one label set per render (its labels.json); 10 held-out motion and 10
held-out rigid-wall renders; clinical windows with the clinician's labels.
| method | motion detected | nulls falsely detected | clinical 2-V2 / 20-V1 wd |
|---|---|---|---|
| 3-D pipeline, sequential sources | 0/10 (median T 0.067) | 0/10 | +0.066 det. / +0.043 det. (at limit) |
| 3-D pipeline, phase-gated sources | 9/10 | — | (not valid on real clips, see C) |
| D1 RAFT optical flow | 6/10 (7/10 off-phase; median T 0.063) | 0/10 | −0.057 / −0.070 (wrong sign; no clip detected) |
| D2 tuned 2-D segmentation (σ 2, q 5, seg, k 5) | 2/10 | 0/10 | +2.03 "det." / +1.66 — artefact: segmentation-failure spikes of 10–18 R inside OUT windows (fig_diag) |
| D3a trajectory-basis NRSfM (Park 2010) | 0/10 (median T 0.085, noisy) | 0/10 (but null median T 0.072) | −0.155 / −0.433 |
| D3 CUT3R (CVPR 2025; agent run) | 0/10 (median T 0.014; corr with truth 0.21–0.53) | 0/10 (but 6/10 nulls p < 0.05; null corr with phase +0.20) | +0.021 (controls fail) / −0.027 |
Visual check: RAFT's floor series follows the planted position on renders (so its render detections are real) but drifts on a rigid wall
(±0.2 R after frame 200) and shows no breathing-locked structure on either clinical window. Reading: on these renders a plain 2-D flow
baseline beats the 3-D pipeline with sequential sources, yet none of the baselines reproduces either clinical reading with the right sign
and passing the rule; the renders favour image-plane flow in a way the clinical video does not, so render sensitivity does not transfer
to clinical capture for any method. CUT3R deviations (disclosed by the agent): preprocessing chosen on a development render after a first
look at s61 frames 0–59; on clinical frames the frozen grey-level lumen threshold found no lumen, so the shared 10th-percentile rule was used.

## B. Results (slow-scope arm, 0.013 R/frame; runs/r3/scores, runs/r3/exact_geom_r3.{json,log})
| render | sources | rule acceptance, original / off-phase | T/T* accepted | quadrature c, q (R) |
|---|---|---|---|---|
| M_G1slow_s101 | sequential | 0/195 / 0/195 | — | +0.048, −0.197 |
| M_G1slow_s102 | sequential | 0/196 / 0/196 | — | +0.060, −0.366 |
| K4_M_G1slow_s101 | phase-gated | 50/198 (0.25) / 89/198 (0.45) | 1.38 / 1.33 | +0.062, +0.017 |
| K4_M_G1slow_s102 | phase-gated | 17/193 (0.09) / 136/193 (0.70) | 0.73 / 0.62 | +0.037, +0.015 |
| N_G1slow_s103, s104 | sequential (rigid) | 0/390 / 0/390 | — | — |
B1 PASS (nulls accept nothing). B2 PASS (|q| > |c| on both sequential renders). B3 PASS (|q| < 0.5|c| on both phase-gated renders).
Floor-arc |ε/β|: s102 (aligned, 0.026 R) median 0.46, p90 1.20 — about 1.8× the constant-speed renders; s101's SfM scale-drifted (alignment
0.54 R), so its |ε/β| and exact-geometry comparison are not used. SfM took 55 min on s101 vs ~10 min at full speed (half the baseline).
Sequential slow renders read −0.06 R at clinician-like labels (median over trials), the opposite sign to 20-V1's +0.043: the render
velocity artefact does not reproduce the 20-V1 reading. Phase-gated magnitude is unstable in this regime (0.73–1.38× the truth).
## A4. Results (end-to-end regeneration under the tag)
M_G1_s61 re-rendered + SfM + MVS from scratch: sequential 0/198 accepted (stored 0); quadrature q −0.330 vs stored −0.325, c +0.079 vs
+0.098. K4 twin: 0.42 (original) / 0.87 (off-phase) vs canonical stored 0.34 / 0.88, T/T* 0.77. N_G1_s66 regenerated: 0/198. Reconstruction
test–retest on renders thus moves phase-gated acceptance by ~0.1 and the position coefficient by ~20 %, with the velocity term stable.
