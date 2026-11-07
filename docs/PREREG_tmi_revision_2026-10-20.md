# TMI revision analyses (2026-10-20) — declared before running; the paper's detection rule and thresholds are NOT changed

R-1 Held-out true-motion sensitivity. The paper's FULL rule (C_sig ∧ C_ctrl ∧ C_plat ∧ C_win ∧ T ≥ 0.02 R; tests/ablation_checks.py, 200
clinician-like label trials per run, unchanged) on 20 renders never used by the paper: seeds 61–80 (motion M_G1_s61, M_G2_s62, M_G1irr_s63,
M_G1cb_s64, MS_G1_s65, M_G1_s71, M_G2_s72, M_G1irr_s73, M_G1cb_s74, MS_G1_s75; nulls N_G1_s66, N_G2_s67, N_G1cb_s68, NS_G1_s69, NS_G2_s70,
N_G1_s76, N_G2_s77, N_G1cb_s78, NS_G1_s79, NS_G2_s80), production MVS + stations (tests/mvs_synth_run.sh flags), and phase-gated (K4,
--phase-json from the true phase) on the 10 motion renders. Report per run: FULL acceptance (sensitivity / false-motion rate), accepted T / T*.
Expectation stated now (from the published ablation): sequential retention ≤ 0.03, phase-gated 0.37–0.68, false motion ≤ 0.01. Whatever comes
out is reported; the paper text is updated to the held-out numbers.
R-2 Patient-level false-positive calibration. Re-run tests/transplant_null.py unchanged; report the FULL acceptance rate per TARGET PATIENT
(clips of the same patient pooled: 20-V1 wd + ins), Clopper–Pearson 95 % CI per patient, and a patient-cluster bootstrap (B = 10 000) CI of the
mean rate. Same-patient placements remain excluded.
R-3 Synthetic–clinical discrepancy. Measure, from the SfM poses of each clinical window and of the renders, the axial scope speed (R / frame),
the fraction of near-stationary frames (< 0.005 R / frame), and the per-frame spread of the pooled floor series relative to its OUT−IN; compare
with the renders. Descriptive; the independent pair-test confirmation of both clinical detections is cited, not re-derived.
R-4 Reproducibility. Tabulate every regeneration (published vs regenerated readout, registered frames, trusted-cell %, path doubling-back,
floor-visible frames) for all clips that have one; propose quality thresholds as PROSPECTIVE criteria only (not applied retroactively).

## Second revision round (2026-10-21), declared before running
E-1 Operating envelope, new renders (seeds 81–85, G1 geometry, same flags as M_G1_s61 except the varied factor): amplitude 0.035 R (s81),
0.105 R (s82), 0.14 R (s83) at default noise; sensor noise 0.012 (s84) and 0.024 (s85) at amplitude 0.07 R (default 0.006). Each: production
sequential MVS and phase-gated (K4) MVS, scored by the unchanged tests/ablation_checks.py; detection rule = four checks AND T ≥ 0.02 R.
Camera-motion and reconstruction-quality strata use the existing 20 held-out runs. Descriptive; no threshold or rule changes.
E-2 Independence of the label-transplant rate: re-run tests/transplant_null.py unchanged except that each placement's offset is also saved;
report the rate on non-overlapping placements only, by donor patient, and a two-way (target × donor patient) cluster bootstrap.
E-3 Clinical vs synthetic behaviour: label-shift profile shape (T(k) for k = −8…+8, plateau ratio min(T(±2))/T(0), sign changes) and a
quarter-cycle test (labels shifted by a quarter of the median labelled cycle: a position reading drops toward 0 from both sides symmetrically,
a velocity reading changes sign), on clinical windows, phase-gated renders and sequential renders.
