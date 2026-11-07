# Label circularity (2026-10-22) — declared before running
(a) Camera-motion confound: per frame, camera pitch / yaw / roll (relative to the mean orientation), axial position and two lateral position
components from the SfM poses. Report (i) each camera variable's OUT−IN at the clinician labels with its off-phase-shift p; (ii) the floor
OUT−IN coefficient with and without regressing out all six camera variables (S_t ~ Ind_t + camera_t + 1). Pass (for each detection clip):
the floor coefficient retains ≥ 70 % of its unadjusted value and stays positive.
(b) Label-independent clock: breathing period from the camera's axial ride (dominant spectral peak of the detrended axial position in 30–150
frames); OUT frames = the frames within ±3 of each peak of the band-passed axial signal (two choices of sign: peaks and troughs). Report the
agreement of each with the clinician labels (fraction of clinician OUT frames within ±3 frames of a camera-clock OUT) and the floor OUT−IN with
the camera-clock labels under the off-phase null. No pass/fail declared for (b) beyond reporting; it is the independent timing check.
Clips: 2-V2, 20-V1 wd, 18-V1 (detections); 26-V2, 31-V1, 17-V1 wd, 2-V1 (nulls).

## Results (appended 2026-10-22; runs/theory/circularity.{py,log,json})
**(a) Camera-motion confound — 1 of 3 detection clips passes.**
| clip | floor coef → camera-adjusted | retained | verdict | camera variables label-locked (off-phase p < 0.05) |
|---|---|---|---|---|
| 2-V2 | +0.067 → +0.043 | 64 % | FAIL (marginal; < 70 %) | pitch, yaw, lateral-1 |
| 20-V1 wd | +0.043 → −0.019 | sign flips | FAIL | pitch, yaw, roll, axial |
| 18-V1 | +0.064 → +0.046 | 71 % | PASS | roll only |
Nulls stay null after adjustment (26-V2 −0.037, 31-V1 +0.014, 17-V1 −0.002, 2-V1 +0.011; none near a detection).
Reading: the scope moves with the breath, so on 20-V1 camera motion and wall motion are collinear and regression cannot apportion the
signal between them. This is a non-identifiability, not proof that the 20-V1 signal is camera-made — but the 3-D statistic alone cannot
exclude it on 20-V1.

**(b) Label-independent clock — unusable.** The camera axial ride's dominant period is mostly ~149 frames (the search ceiling) and matches the
labelled cycle only on 26-V2 and 18-V1; agreement with clinician OUT frames 0–23 %; no camera-clock floor OUT−IN is significant. The camera
does not carry a usable breathing clock; a recorded ventilator / capnography trace is required for a label-free timing reference.

**(c) 3-D pipeline vs its depth-free pair test (added after (a)/(b); descriptive, not pre-declared).** runs/theory/pair_vs_pipeline.{py,log},
pair_null_motion.{py,log}. The pair test cancels rotation and fits zoom + translation from reference-wall features, so it uses no depth map.
- Per breathing window (pipeline OUT−IN / pair mean S): 2-V2 4/4 windows same sign (+0.093/+0.300, +0.098/+0.057, +0.107/+0.080,
  +0.014/+0.068; n pairs 1–6); 20-V1 3/4 same sign (+0.165/+0.060, +0.123/+0.036, +0.121/+0.034; disagreement f2723 −0.027/+0.028).
  Four windows per clip are too few for a meaningful rank correlation.
- Labelled pairs vs null pairs: 2-V2 median S +0.071 (12/12 > 0) vs null −0.004 (n 231); 20-V1 +0.049 (91 % > 0) vs null −0.002 (n 285).
- Camera-motion dependence: in labelled pairs S rises with the camera motion between the two frames (Spearman ρ ≈ +0.5–0.6), but in null
  pairs it does not (ρ −0.05…+0.02), so S is not a generic camera-motion artefact. Motion-matched null pairs (rotation AND translation at
  least the labelled medians): 2-V2 median −0.006 (n 27, 44 % > 0) — clean; 20-V1 +0.024 (n 10, 70 % > 0) — about half the labelled
  +0.049, on only 10 pairs. So on 20-V1 roughly half of the depth-free signal may be shared with large camera excursions; the other half
  exceeds the motion-matched null.
**Overall:** 2-V2 is supported by two independent estimators and survives camera adjustment at 64 %; 18-V1 passes (a); 20-V1 is NOT
separable from scope motion by either estimator and must be reported as camera-confounded.
