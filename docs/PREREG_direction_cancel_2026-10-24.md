# Removing the velocity confound by scope-direction cancellation (2026-10-24) — declared before any render or analysis
Idea (from the derivation r̂ − r ≈ −(d/s)·v): the stereo artefact changes sign with the direction of scope travel s, the wall position does
not. Readings taken while the scope moves in opposite directions, at the same breathing phase, therefore cancel the velocity term and keep
the position. No new data or respiratory signal is needed, only passes in both directions over the same segment.
Estimators.
 (E1) Pass pair: two passes over the same tube with the same breathing (same seed → same texture and phase table), one withdrawing and one
      inserting. Combined per-frame series S_c(t) = ½[S_wd(t) + S_ins(t)] (frames aligned by breathing phase, identical here).
 (E2) Within one clip: per-frame axial scope speed s_t from the SfM path (15-frame smoothing); frames with |s_t| < 25 % of the clip's median
      |s| are excluded (near reversals the artefact diverges); OUT−IN is computed separately on forward (s > 0) and backward (s < 0) frames
      and the two are averaged: T_c = ½[T_fwd + T_bwd].
Scoring: the unchanged five-condition rule with the primary circular-shift null, applied to the combined quantity: for E1 to S_c with the
true-phase labels (common.evaluate); for E2 the null shifts the label sequence once and recomputes both direction halves; controls, plateau
(±1, ±2) and leave-one-window-out are computed on the combined quantity; T_c ≥ 0.02 R. Quadrature fit (c cos φ + q sin φ + k) on every series.
Renders (frozen renderer defaults, 300 frames, G1 geometry unless stated, seeds 121–128), sequential sources only:
  pair A  M_G1_s121 (withdraw 0.026 R/fr)  + M_G1ins_s121 (insert 0.026)          motion 0.07 R
  pair B  M_G2_s122 + M_G2ins_s122 (G2 geometry)                                     motion
  pair C  M_G1irr_s123 + M_G1irrins_s123 (irregular breathing)                       motion
  pair D  N_G1_s124 + N_G1ins_s124                                                   rigid
  pair E  M_G1slow_s125 + M_G1slowins_s125 (0.013 R/fr, 20-V1 regime)                motion
  scan    M_G1scan_s126, N_G1scan_s127: back-and-forth scope (axial oscillation 1.0 R, period 110 frames, not breath-locked; net travel
          0.005 R/fr) for E2; renderer flags --scan-amp/--scan-period added (default 0 leaves every earlier render unchanged).
Predictions / criteria:
 P1 sign flip: in every motion pair the quadrature coefficient q has opposite sign in the two passes.
 P2 cancellation: the combined series has |q_c| < 0.5 |c_c| in ≥ 3 of the 4 motion pairs (A, B, C, E).
 P3 detection: the combined readout passes the rule in ≥ 3 of 4 motion pairs; the rigid pair D does not pass (E1).
 P4 magnitude (reported; a 2.2× position inflation is already known for sequential stereo): combined T/T* in 0.5–2.5.
 P5 within-clip (E2): on M_G1scan_s126 the direction-combined readout passes the rule and |q_c| < 0.5|c_c|; N_G1scan_s127 does not pass.
Then (separately, after this result, unchanged estimator): clinical 20-V1 insertion + withdrawal (E1 by breathing labels) and E2 on every
labelled clip with ≥ 30 labelled frames in each direction. Failures are reported.

## Amendment 1 (before any render): storage and verification
The /scratch/mi3dr_* directories were purged by the system (2026-10-24; all paper numbers had already been computed and committed). New
renders and reconstructions go to the local disk /var/tmp/mi3dr_r5. Renderer flags --scan-amp/--scan-period verified not to change an
existing render (development render M_G1_s22, frame 0 re-render vs stored video: 0.62 grey levels = codec noise). Negative --speed renders
insertion (camera z increases 60.00 → 60.13 → 60.26 R).

## Result (runs/r5/combine.{log,json}; per-frame plot runs/r5/pairA_series.png)
| pair | q withdraw / insert | combined c, q | combined OUT−IN (T*) | rule |
|---|---|---|---|---|
| A G1 | −0.323 / +0.346 | +0.053, +0.011 | +0.035 (0.062), p 0.18 | no |
| B G2 | −0.348 / +0.355 | +0.048, +0.007 | +0.003 (0.062), p 0.57 | no |
| C G1 irregular | −0.364 / +0.378 | +0.047, +0.005 | +0.006 (0.064), p 0.63 | no |
| E slow (0.013) | −0.427 / +0.353 | −0.002, −0.060 | −0.087 (0.062), p 0.93 | no |
| D rigid | 0 / 0 | 0, 0 | 0.000 | no (correct) |
P1 PASS (sign flips in 4/4 pairs). P2 PASS (|q_c| < 0.5|c_c| in 3/4; fails at slow speed). P3 FAIL (0/4 detected; rigid clean). P4 FAIL for
OUT−IN (0.05–0.56× truth) but the combined in-phase coefficient c is 0.047–0.053 vs ≈0.044 for the truth through the statistic (≈1.1–1.2×)
in pairs A–C. P5 FAIL (within-clip E2: −0.033, wrong sign; rigid scan clean).
Reading: reversing the scope cancels the velocity term and recovers the position term over the whole cycle, but each pass's artefact is a
saturated near-square wave whose sign switches at the breathing extremes (v = 0); the two passes switch a few frames apart, leaving sharp
residual dips exactly in the OUT windows, so the OUT−IN-at-extremes statistic does not recover the motion. Within one clip, direction
halves differ in speed profile and do not cancel. The confound is cancellable in principle but not by this statistic; reported as such.
