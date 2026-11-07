# Off-phase shift null (v5) — pre-registration, 2026-10-21 (before any v5 output)
Diagnosis (envelope, runs/v3/tmi_r1/*): with phase-gated sources the circular-shift detection limit grows with the planted periodic signal
(L 0.022 → 0.119 R for amplitude 0.035 → 0.14 R), because shifts near whole breathing cycles reproduce the signal; acceptance therefore does
not rise with amplitude (34 / 31 / 11 / 16 %).
Fix (only change to the rule): the shift null uses only label shifts whose offset is between 1/4 and 3/4 of the labelled cycle
(cycle = median spacing, in labelled-frame index units, between starts of consecutive OUT runs; label-derived, no truth). p and L_0.05 are
computed over those shifts; ≥ 20 shifts required. Controls, plateau, window consistency, δ unchanged. Valid under H0 (series independent of the
labels: any label-determined subset of shifts is still a null).
Predictions (to be met on FRESH renders): (P1) phase-gated acceptance rises with amplitude; (P2) median phase-gated acceptance at 0.07 R ≥ 0.6;
(P3) rigid-wall false motion ≤ 0.02 under the detection rule; (P4) sequential stays ~0 (velocity physics, not fixable by the null).
Re-analysis (NOT credited: data already seen) on all existing grids; credited test on fresh renders seeds 91–100: amplitude 0.035 / 0.07 / 0.14
(M_G1a035_s91, M_G1_s92, M_G1a14_s93), M_G2_s94, M_G1cb_s95 — each sequential + phase-gated — and nulls N_G1_s96, N_G2_s97, N_G1cb_s98,
NS_G1_s99, NS_G2_s100. PASS iff P1 (monotone over 0.035 / 0.07 / 0.14), P2 (median over s92, s94, s95 ≥ 0.6) and P3 (all 5 nulls ≤ 0.02).
Real data: label-transplant FP and the clinical cohort re-scored with the off-phase null (descriptive; δ sensitivity 0 / 0.01 / 0.02 / 0.03 R).

## Results (2026-10-22)
Re-analysis (uncredited, runs/v5/reanalysis_score.log): phase-gated 0.07 R median acceptance ≈ 0.82 (was 0.31); nulls 0 % at δ ≥ 0.01 (up to 11 %
at δ = 0, so the minimum effect stays); sequential ≈ 0.
**Credited test (runs/v5/score_fresh.log): FAIL on P1.** P1 monotone over amplitude: 0.78 / 0.77 / 0.34 (0.035 / 0.07 / 0.14 R) — FAIL. P2 median
phase-gated acceptance over s92 / s94 / s95 = 0.88 ≥ 0.6 — PASS (original null on the same renders 0.21 / 0.36 / 0.22). P3 all 5 nulls 0.00 — PASS.
Diagnosis of P1 (runs/v5/large_amp_diag.log): at large amplitude in 2 of 3 runs every check degrades together — recovered T/T* 0.46–0.67 (vs 0.70–
0.89), limit ↑, control-arc failures 46–48 % — the phase-gated RECONSTRUCTION leaks large wall motion into other arcs; the third large run (s83,
0.14 R) is fine (0.82). The null is not the cause.
Real data (descriptive): clinical windows (runs/v5/cohort_offphase.log): 2-V2 p 0.003 → 0.006; 20-V1 wd p 0.138 → 0.008 (limit 0.054 → 0.019 R);
18-V1 0.032 → 0.046; 7-V1, 33-V1 (not reproduced) and all nulls stay non-significant. Label-transplant FP (runs/v5/transplant_offphase.log):
detection rule mean 2.2 % (was 1.4 %), max 9.7 % (33-V1, 31 placements); significance alone 11.5 % (was 5.8 %).
Off-phase rule, real FP independence (runs/v5/fp_independence_offphase.log): per-patient mean 2.1 %; one-way patient bootstrap 95 % CI 0.5–4.2 %;
two-way (target × donor) 0.4–6.4 %; non-overlapping placements 3 / 93 (3.2 %). Original rule: 1.3 %, two-way 0.2–3.7 %. Trade-off: off-phase
roughly triples phase-gated sensitivity but its two-way upper bound exceeds 5 %. Report both rules.
