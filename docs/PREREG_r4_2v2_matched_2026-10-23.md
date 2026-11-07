# 2-V2-matched renders: does sequential stereo reproduce a position-like readout under 2-V2's conditions? (2026-10-23) — declared before rendering
Question (reviewer): the paper reports near-zero sensitivity of sequential stereo on renders, yet the clinical readings (2-V2) come from
sequential stereo. Do renders matched to 2-V2's capture conditions reproduce a positive, position-like readout?
2-V2 conditions measured from its reconstruction (runs/g6_2v2): withdrawal at 0.0315 R/frame (median |axial speed|), camera 0.22 R from the
lumen axis, offset sideways (83° from image-down), pitch to the axis 2.6°, labelled breathing cycle 79 frames, clinician OUT duty 0.80;
breath-locked axial camera ride not significant on 2-V2 (off-phase p 0.19; Section camera motion), pitch/yaw/lateral label-locked by < 1°.
Renderer change: one optional flag --offset-x (sideways offset, default 0; s61 frame 0 re-renders identically, 0.62 grey levels).
Renders (300 frames, frozen texture/lighting/noise defaults, seeds 111–116): speed 0.0315, period 79, --offset 0 --offset-x 0.22, tilt 0,
amplitude 0.07 R on the 35° floor arc unless stated:
  M_2V2m_s111, M_2V2m_s112 (motion; sequential and phase-gated K4), M_2V2mcb_s113 (motion + breath-locked axial ride 0.2 R; sequential + K4),
  N_2V2m_s114, N_2V2m_s115 (rigid; sequential), N_2V2mcb_s116 (rigid + ride 0.2 R; sequential).
Scoring (unchanged rule, original circular-shift null primary, off-phase reported): 200 clinician-like trials per render with (a) the
standard OUT half-width 30° (17 % duty, as every render so far) and (b) 144° (80 % duty, as the 2-V2 clinician labels); tests/ablation_checks.py
--half-width (default unchanged, verified bit-identical). Plus the quadrature fit (runs/theory/exact_geom.py) and the label-shift profile at
true labels.
Decision, fixed now: "reproduces" if, for (a) or (b), the sequential motion renders accept ≥ 20 % of trials with median T/T* in 0.5–2 and the
quadrature fit has |c| ≥ |q|, while the rigid renders accept ≤ 2 %. Otherwise the paper states that 2-V2's clinical reading is not explained
by the render model. Prediction from the existing renders: not reproduced (sequential acceptance ≈ 0, velocity-dominated).

## Result: NOT reproduced (runs/r4/summary.log, runs/r4/exact_geom_r4.log)
Matched renders are in 2-V2's regime (floor-arc |ε/β| median 0.22 = the clinical estimate; alignment 0.012–0.014 R).
Sequential motion renders (s111, s112, s113 with ride): 17 % duty 0/198, 0/197, 0/195 accepted; 80 % duty 9/200, 9/200, 11/198 (4–6 %) at
T/T* 4.66, 4.62, 4.94; quadrature c +0.057, +0.065, +0.099 vs q −0.256, −0.244, −0.246 (velocity-dominated). Rigid renders (s114–s116): 0
accepted at either duty and under either null. Phase-gated: 0 accepted (17 %), ≤ 2 % (80 %), reading ≈ 0.4× the truth — the same-phase
source lies one 79-frame cycle (≈ 2.4 R of travel) back. Decision: not reproduced → the paper states that the render model does not explain
the clinical 2-V2 reading.
