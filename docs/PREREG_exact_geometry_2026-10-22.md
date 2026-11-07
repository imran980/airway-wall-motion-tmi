# Exact-geometry validation of the static-stereo artefact (2026-10-22) — declared before writing the code
Reviewer: validate the axial-motion equation against planted truth without linearisation, especially where |ε/β| is not small; define the
quadrature fit; align real and synthetic source-frame intervals. The earlier check (PREREG_velocity_theory) inferred d from a fitted
quadrature coefficient, which assumes the linear model; this test predicts the readout from the truth with NO fitted parameter.

Method. For each render: align the SfM model to the render's true camera path (scale from path length, rotation from camera orientations,
translation from centroids; the straight path makes centre-only Umeyama roll-degenerate). Map every grid station and sector into truth
coordinates. Rebuild each frame's stereo sources with the pipeline's own rule (m1/windowed_depth_real.py: sequential |j−k| ≤ 12, baseline ≥
3 median steps, nearest six; K4: same phase within 0.35 rad, |j−k| > 12, span 120, nearest six, sequential fallback if < 2). For every
measured (frame, station, sector) cell, predict the reconstructed radius three ways, per source then median over sources:
  N  numeric two-view: the point on the reference ray through the true wall point at time t closest to the source ray through the same
     material point at time t' (true poses, true off-axis offset and tilt) — no small-angle or on-axis assumption;
  E  exact closed form r̂/r = β(1+ε)/(β+ε), β = Δz_cam/d (axial camera displacement toward the point over axial depth), ε = (r(t')−r(t))/r(t);
  L  linear r̂ − r = −(d/s)v with instantaneous v and s.
Also T = the true radius (no artefact). Each prediction is put through the unchanged statistic (LC.load deviations → LC.pooled floor arc) on
exactly the cells the pipeline measured, giving S_N(t), S_E(t), S_L(t), S_T(t) beside the measured S(t).
Quadrature fit (definition used in the paper): OLS S_t = c cos φ_t + q sin φ_t + k over frames with finite S, φ = true phase; c = in-phase
(position), q = quadrature (velocity) coefficient.
Runs: constant-speed sequential renders (dev s21–s24; held-out s61–s63, s71–s73; envelope s81–s85, amplitudes 0.035–0.14 R and noise ×2/×4),
camera-riding-the-breath (s64, s74), stop-and-go (s65, s75), phase-gated K4 (all with K4 grids).
Predictions / criteria:
 G1 model adequacy (N vs measured, constant-speed sequential): Pearson(S, S_N) ≥ 0.7 and OLS slope of S on S_N in [0.5, 1.5] in ≥ 80 % of runs.
 G2 closed forms (vs N): E tracks N better than L (RMS(S_E−S_N) < RMS(S_L−S_N)) in ≥ 80 % of runs; where median |ε/β| on the floor arc is
    ≥ 0.3, the quadrature amplitudes of L and E differ by > 10 %.
 G3 phase-gated: |q_N|/|c_N| < 0.5; report measured c / c_N (the stereo/regularisation attenuation).
 G4 source intervals: render median τ within ±1 frame of the clinical median (4–5 frames), same rule.
Descriptive: |ε/β| distributions on renders; on clinical windows |ε/β| with the measured axial speed, a 0.05 R excursion at the labelled cycle
and the median station depth. A failure of G1 means the paper's mechanism sentence must be weakened; it is reported either way.

## Results (runs/theory/exact_geom.{py,log,json}, exact_geom_summary.log, clinical_eps_beta.{py,log,json})
Code check: numeric two-view = closed form to 6 decimals for an on-axis camera (3 cases). Alignment gate (NOT pre-declared, stated as such):
10 of 34 grids excluded because monocular SfM scale drifts along the path (SfM/true step ratio drifts 30–110 %), so no similarity maps them
to the truth (alignment RMS 0.73–1.25 R vs 0.009–0.033 R for the rest): s71, s72, s82, s83, s85 and their K4 twins.
Constant-speed sequential (n 10):
| model | Pearson with measured | slope measured-on-predicted | predicted / measured quadrature |
|---|---|---|---|
| N numeric two-view (true off-axis geometry) | 0.81 [0.51, 0.91] | 0.37 [0.12, 0.58] | 2.00 [1.56, 2.44] |
| E exact closed form (on-axis) | 0.85 [0.82, 0.93] | 0.56 [0.49, 0.65] | 1.48 [1.38, 1.58] |
| L linear −(d/s)v | 0.94 [0.92, 0.95] | 0.80 [0.73, 0.81] | 1.26 [1.23, 1.38] |
- G1 FAIL: 1/10 meet r ≥ 0.7 AND slope 0.5–1.5 (r ≥ 0.7 alone 9/10). The geometry predicts sign and time course with no fitted parameter,
  but the pipeline records about 0.37× of the exact two-view magnitude (multi-view stereo attenuates it). The linear form's better
  apparent fit is a cancellation (it under-predicts the true geometry by about as much as MVS attenuates), not a validation.
- G2a PASS 9/10 (E closer to N than L). G2b: only one run has median |ε/β| ≥ 0.3 (s21, 0.42), where L and E quadrature differ by 2 % (FAIL
  as stated); over all runs they differ by 13 % [2, 22]. |ε/β| on the floor arc: median 0.26 [0.13, 0.42], p90 0.64 [0.30, 1.01].
- Unexplained in-phase excess: measured in-phase c = 2.17× [1.84, 2.34] the truth through the same statistic (0.09 vs 0.04 R); N, E and L
  predict none (c 0.00–0.06). Under sequential sources a moving wall's position component is inflated ~2× by something outside the
  two-view geometry (candidates: consistency filtering or regularisation that depends on velocity phase). Not resolved.
- Camera riding the breath (n 2): N predicts quadrature −0.42, measured −0.07 (6× smaller); L diverges where s → 0. Stop-and-go (n 2):
  N −0.38 vs measured −0.13. The geometric model over-predicts most where the camera slows.
- G3 PASS: phase-gated |q_N|/|c_N| 0.04 [0.00, 0.07]; measured c / c_N 0.88 [0.78, 0.92]. Through the statistic the truth itself reads
  ~0.8 of A·w̄ (common-mode subtraction), so the old "0.65–0.8× of A·w̄" = statistic (~0.8) × stereo (~0.88).
- G4 PASS: render source spacing median 4–6 frames vs clinical 4–5 (same rule).
Clinical |ε/β| (a = 0.05 R, labelled cycle, measured speed and station depth): 2-V2 0.22, 18-V1 0.16, 17-V1 0.24 (inside the rendered
range); 20-V1 wd 1.05 (51 % of frames ≥ 1), 26-V2 0.63, 31-V1 0.86, 2-V1 2.21 — outside the linear regime and outside what the renders tested.
Consequence for the paper: the equation explains the direction, phase and phase-gating cure of the artefact; it does not predict its
magnitude, and sequential-source amplitudes (including the clinical ones) are not calibrated — the in-phase part was inflated ~2× on renders.
