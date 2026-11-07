# Pre-registration — supervisor review items (2026-10-11), written before any run

## R1. Detection limit: mathematical definition (replaces the generic-label estimator)
For a window with frame set F, clinician labels y_f ∈ {OUT, IN} and per-frame floor series s_f (floor-arc mean deviation minus median of the
other sectors, pooled over stations, in R), the statistic is T(y) = mean_{f: y_f=OUT} s_f − mean_{f: y_f=IN} s_f. Let y^(k), k = 1…|F|−1, be the
circular shifts of the label sequence over the frames with a finite s_f. The **detection limit** is the 95th percentile of {T(y^(k))}:
  L_0.05 = Q_0.95({T(y^(k))}),   so that one-sided p = #{k: T(y^(k)) ≥ T(y)} / (|F|−1) < 0.05  ⇔  T(y) > L_0.05 (up to ties).
Interpretation: the smallest OUT−IN separation that the clip's own data and the clinician's own label pattern could call significant. The
previous estimator (`m2/testability.py`, mean of the same percentile over 200 random generic label patterns of the clip's window count and
period) is kept as a pre-labelling planning quantity only; it can disagree with the labelled limit (regenerated 2-V2: 0.080 vs exact p 0.004).
Action: recompute L_0.05 for every reported clip with the clinician's labels; report it in the cohort table and figure.

## R2. Physiological interpretation — wording, no new data
Claim restricted to: "a breathing-locked excursion of the posterior wall at the clinician's labelled breathing extremes", supported by (i) the
label-shift plateau (position, not stereo velocity), (ii) the breathing-camera control on planted truth (scope motion alone gives 0),
(iii) null roof/side controls, (iv) the independent depth-free pair test, (v) CT identifying the posterior wall as the mover (one patient).
Stated as not shown: an independent respiratory signal (phase comes from the clinician), millimetres except on 20-V1, and whether part of the
near-wall excursion is mechanical coupling to the scope.

## R3. Controlled ablation on synthetic data with known ground truth
**Data.** All production-pipeline synthetic renders with a reconstructed grid (no phase-gated K4 runs, which use a different source rule):
amp 0 (null): G0_a0, G1_a0, G2_a0, G3_a0, K11_cb_a0 (+ new nulls below); amp 0.07 R (motion): eval_G0, eval_G1, eval_G1sg (stop-and-go),
G0_a0.07, G1_a0.07, G1lit_a0.07, G2_a0.07, G3_a0.07, K11_cb (+ new motion renders below). G3 (camera on the roof side; floor far wall) is kept:
it tests whether the rule rejects an unmeasurable geometry.
**New renders (to enlarge the null denominator; launched after this file is committed):** six amp-0 renders with new texture seeds —
G0, G1, G2, G3 geometries, G1 with a 0.2 R breathing-riding camera, G1 with ±25 % irregular breathing — and four amp-0.07 renders with new
seeds (G0, G1, G2, G1 irregular). Same renderer settings and production flags as the existing runs (`tests/mvs_synth_run.sh … 0.18 1.0`).
**Trials.** Per run, 200 label trials derived from the TRUE phase: OUT = frames within ±30° of peak-open (the clinician convention), with
clinician-like imperfection: a random global shift of −2…+2 frames, each window edge jittered ±2 frames, each window dropped with
probability 0.15, and a random contiguous sub-span of 3–6 breathing cycles (the real windows' length). Truth per trial:
T* = A · w̄ · (mean_OUT cos φ − mean_IN cos φ), w̄ = mean of exp(−(θ/35°)²) over the ±30° floor arc (A = 0 for null runs).
**Checks.** C_sig: one-sided shift-null p < 0.05 (⇔ T > L_0.05). C_ctrl: |T_roof|, |T_side+90|, |T_side−90| each < 0.5·T.
C_plat: label-shift profile at k = −2…+2 keeps the sign of T and every value ≥ 0.5·T. C_win: every leave-one-window-out value ≥ 0.33·T.
**Configurations.** FULL = C_sig ∧ C_ctrl ∧ C_plat ∧ C_win; FULL minus each one of C_ctrl, C_plat, C_win; SIG-ONLY = C_sig.
**Metrics.** False-motion rate = fraction of null-run trials accepted; retention = fraction of motion-run trials accepted;
displacement error on accepted motion trials = median |T − T*| and median T/T*; all per run and pooled with run as the unit
(trials within a run are correlated: pooled rates are reported as the mean of per-run rates with the run-level spread).
**Predictions.** (P1) SIG-ONLY accepts velocity-type readings: on motion runs whose truth-aligned label-shift profile is a ramp (G0, G1),
accepted trials have T/T* far from 1 and both signs occur; removing C_plat raises the accepted error most. (P2) FULL false-motion rate ≤ 5 %
on the null runs. (P3) FULL retention is lower than SIG-ONLY; FULL accepted |T/T* − 1| median < 0.5. (P4) G3 (far floor) is rejected by
FULL in ≥ 90 % of trials. If P1–P4 fail, the checks are reported as not doing what we claimed, and the manuscript changes accordingly.

## R1 results (2026-10-11): labelled detection limit L_0.05 recomputed (`tests/labelled_limit.py`)
| grid | T (R) | p | L_0.05 (R) | null sd |
|---|---|---|---|---|
| 2-V2 published | +0.0665 | 0.044 | 0.066 | 0.039 |
| 2-V2 regenerated | +0.0748 | 0.002 | 0.055 | 0.034 |
| 20-V1 (third reconstruction) | +0.0429 | 0.049 | 0.043 | 0.029 |
| 7-V1 label-span regen | +0.0280 | 0.158 | 0.042 | 0.030 |
| 7-V1 original-span regen | +0.0189 | 0.311 | 0.057 | 0.035 |
| 26-V2 best segment | −0.0064 | 0.660 | 0.050 | 0.022 |
| 31-V1 | +0.0023 | 0.542 | 0.034 | 0.026 |
| 17-V1 withdrawal | +0.0007 | 0.408 | 0.013 | 0.007 |
| 2-V1 | +0.0111 | 0.142 | 0.016 | 0.010 |
With this definition "T > limit" and "p < 0.05" are the same statement, as intended. 2-V2 published and 20-V1 sit at their limits (p 0.044 / 0.049); 2-V2's regeneration is well above. 18-V1, 33-V1 withdrawal and 20-V1 insertion grids were deleted in the data-restriction interim and are being regenerated after the ablation renders (`runs/followup_regen.sh`).

## R3 results on the 14 existing runs (2026-10-11), 200 label trials each — acceptance rates
| run | truth | FULL | −ctrl | −plat | −win | SIG only |
|---|---|---|---|---|---|---|
| G0_a0 | null | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| G1_a0 | null | 0.00 | 0.04 | 0.00 | 0.00 | 0.08 |
| G2_a0 | null | 0.01 | 0.06 | 0.01 | 0.01 | **0.22** |
| G3_a0 | null (32 trials) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| K11_cb_a0 (breathing scope) | null | 0.00 | 0.06 | 0.00 | 0.00 | 0.06 |
| eval_G0, G0_a0.07 | 0.07 R | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| eval_G1, G1_a0.07, G1lit, K11_cb | 0.07 R | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| G2_a0.07 | 0.07 R | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| eval_G1sg (stop-and-go) | 0.07 R | 0.03 (T/T* 1.59) | 0.07 | 0.03 | 0.03 | 0.07 (T/T* 2.01) |
| G3_a0.07 (far floor) | 0.07 R (93 trials) | 0.00 | 0.00 | 0.05 | 0.00 | **0.32 (T/T* 3.47)** |
Reading. (a) False motion: significance alone accepts 6–22 % of null trials on three of five null runs — the circular-shift p is anti-conservative on these renders (nonstationary floor series within short sub-spans); the control-arc check removes almost all of it; FULL ≤ 1 % on every null run (P2 ✓). (b) Wrong motion: on the far-floor geometry significance alone accepts 32 % of trials at 3.5× the truth; the plateau check (with the others) rejects them all (P4 ✓; P1 ✓ for the error-reduction part). (c) Retention cannot be measured on these renders: with constant-speed withdrawal the pipeline is in the velocity-dominated regime documented on planted truth (ramp, sign flip at k = +2), so under clinician-like label jitter even significance almost never holds (0–7 %); P3's accuracy part fails on the one run with acceptances (stop-and-go: T/T* 1.59 accepted). This matches the earlier finding that the synthetic captures, unlike the real clips, are velocity-dominated; it is reported as a limitation of the synthetic set, not as evidence of retention.
**Amendment, declared before running:** to measure retention in the position-dominated regime, add renders with planted 0.07 R motion in stop-and-go capture (15 move / 15 pause, as eval_G1sg) at the G0, G1 and G2 geometries with new seeds, plus matching amp-0 stop-and-go nulls; queued after the pre-registered renders and the clip regenerations.

## R3: the ten pre-registered renders (scored 2026-10-11)
Nulls: N_G0 FULL 0.00 / SIG 0.00; N_G1 0.00 / 0.14; N_G2 0.00 / **0.28**; N_G1cb (breathing scope) 0.00 / 0.05; N_G1irr 0.00 / 0.03; N_G3 not scorable (floor never reconstructed: far wall). Motion (constant-speed withdrawal): M_G0, M_G1, M_G2, M_G1irr all 0.00 under every configuration. Pooled over the 10 scorable null runs: SIG-only false-motion rate mean 0.09 (0.00–0.28), FULL 0.00–0.01; the control-arc check is the one that removes it (−ctrl 0.00–0.16). Retention in the constant-speed regime remains unmeasurable (0 % even for significance alone); the stop-and-go renders of the declared amendment are running.

## Regenerated clip grids (deleted in the data-restriction interim) — test–retest outcomes
| clip | published | regenerated | L_0.05 (labelled) | window consistency | reading |
|---|---|---|---|---|---|
| 18-V1 | +0.047, p 0.040 | **+0.064, p 0.027** | 0.060 | 2/3 windows, LOO +0.007…+0.123 | reproduces in sign and significance; still window-fragile |
| 33-V1 withdrawal | +0.055, p 0.013 | **+0.016, p 0.12** | 0.021 | 1 window with data | **not reproduced** (as 7-V1) |
| 20-V1 insertion | +0.047, p 0.30 | +0.045, p 0.28 | 0.122 | 1/2, LOO −0.064…+0.205 | reproduces (sign-only, as before) |
Both detections that did not reproduce (7-V1, 33-V1 withdrawal) were the ones with the weakest support in the original run (pipeline-only; sparse frames). The two independently confirmed detections (2-V2, 20-V1) reproduced.

## R3 diagnosis (16:40) and second amendment, declared before scoring
Stop-and-go motion renders: FULL and SIG-only both accept 0 % (MS_G0/G1/G2). Exact-label diagnosis: on every moving-wall render the per-frame floor series is velocity-dominated — series sd 0.15–0.31 R (2–5× the planted 0.07 R), label-shift profile a monotone ramp through zero, shift-null limit L_0.05 0.13–0.40 R — so the planted motion is below the clip's own limit even with perfect labels; stop-and-go halves the spread but does not reach the position regime. On rigid-wall renders the series is nearly flat (sd 0.004 R; L_0.05 0.002 R), so significance alone flags drifts of ~0.002 R: statistically "significant", physically negligible — those are the SIG-only false motions, and the control-arc and plateau checks remove them.
Consequence: retention of genuine position-like motion cannot be measured on renders reconstructed with sequential stereo sources. **Second amendment:** score the phase-gated reconstructions of the same renders (K4_G1, K4_G1_irr with planted 0.07 R; K4_G1_a0 null), where planted truth showed a position-like, flat reading (0.81×). The validity checks act only on the per-frame series and the labels, so they are evaluated there unchanged. Prediction: FULL retention ≥ 50 % with accepted T/T* within 0.6–1.2; null K4_G1_a0 FULL 0 %.
**Second-amendment result (phase-gated grids, position-like regime):** K4_G1 (0.07 R): FULL 0.37 vs SIG-only 0.40, accepted T/T* 0.81, |error| 0.011 R; K4_G1_irr (irregular breathing): FULL 0.68 vs 0.77, T/T* 0.75, |error| 0.016 R; null K4_G1_a0: FULL 0.00 vs SIG-only 0.06. The checks keep 88–93 % of the genuine detections that significance alone would accept, with unchanged accuracy, and remove all false ones. Prediction "FULL retention ≥ 50 %" met on one of two runs (0.37, 0.68); accuracy prediction (0.6–1.2) met. Retention is bounded by significance itself (40–77 %), i.e. by the clip's own detection limit, not by the checks.
**Final two nulls (stop-and-go, rigid wall):** NS_G1 FULL 0.00 / SIG-only 0.05; NS_G2 FULL 0.00 / SIG-only 0.10. Over all 12 scorable null runs: FULL 0.00–0.01, SIG-only 0.00–0.28. Ablation complete.

## R4. Calibrated null — declared 2026-10-12 before running
Problem: the circular-shift null is anti-conservative on short, non-stationary series (significance alone 0–28 % on rigid-wall renders). Suspected cause: circular shifts wrap windows across the span ends and keep the label sequence's alignment to slow trends.
Candidate A, **window-placement null**: keep the trial's OUT windows (count and lengths), place them at random non-overlapping positions within the span (2000 draws), recompute T; p = fraction ≥ observed. No preprocessing of the series.
Candidate B, **no-wrap shift null**: shift the whole label pattern by every offset that keeps all windows inside the span (no wrap-around).
Selection rule fixed now: a candidate is adopted if significance alone has false-motion rate ≤ 0.05 on every one of the 12 scorable rigid-wall runs (with 200 trials, ≤ 0.08 allowed for sampling error) AND it keeps ≥ 80 % of the circular-shift detections on the two phase-gated motion runs. If both pass, A (more null draws). If neither passes, report that no calibrated label-permutation test was found and keep the full rule as the false-positive control. The adopted test is then applied unchanged to every real clip.
**R4 result (2026-10-12): neither candidate passes the declared rule.** Significance-alone false-motion rate on the 13 rigid-wall runs — circular shift 0.00–0.21; A (random placement) 0.00–**0.73**; B (no-wrap shift) 0.00–0.23. A fails worst on the breathing-camera nulls (0.41, 0.73): random placement destroys the breathing periodicity, so any breathing-locked component of a rigid scene (the scope riding the breathing) becomes "significant"; the circular shift preserves periodicity and is the better null for that reason. B removes the wrap-around but is no better on G1/G2 (0.17–0.23), so wrap-around is not the cause. Retention on phase-gated motion: A 0.99–1.00 (meaningless given its false-positive rate), B 0.47–0.49 vs circular 0.42–0.80. By the declared rule: **no calibrated label-permutation test was found; the circular-shift p is kept and reported as anti-conservative on its own, and the full rule (controls + plateau) remains the false-positive control (≤ 1 % on every null run).** The flagged rigid-wall drifts are ~0.002 R; a physically motivated minimum effect would remove them, but it was not declared before this run and is not adopted here.

## R5. Real-data false-positive calibration by label transplant, and a minimum effect — declared 2026-10-13 before running
**Targets (one grid per window, the currently reported one):** 2-V2 (g6_2v2), 20-V1 withdrawal (m1_20V1_lab), 20-V1 insertion, 7-V1 (m1_7V1_lab), 18-V1, 33-V1 withdrawal, 26-V2 best segment (m1_26V2_lab_m1), 31-V1, 17-V1 withdrawal, 2-V1.
**Donor patterns:** every other clip's clinician label file, reduced to its relative OUT/IN sequence (offsets from its first frame). For each target × donor, the pattern is placed at every offset (step 3 frames) where it fits inside the target's finite floor frames (truncated to the target length; ≥ 2 OUT windows required). Placements whose OUT indicator correlates with the target's own labels at |r| > 0.3 are excluded (they could align with the real breathing). The same clip's own pattern is never used on itself.
**Scored per placement:** T, circular-shift p (as in the paper), and the FULL rule (C_sig ∧ C_ctrl ∧ C_plat ∧ C_win, thresholds as in Methods).
**Minimum effect, declared now:** δ = 0.02 R (just under half the smallest effect claimed, 0.043 R). Rules evaluated: SIG; SIG ∧ T ≥ δ; FULL; FULL ∧ T ≥ δ.
**Metrics:** false-positive rate = fraction of transplanted placements accepted, per target and pooled with target as the unit; the same δ applied to the 13 synthetic rigid-wall runs (ablation trials) and to retention on the phase-gated motion runs and the real reported detections.
**Predictions:** (Q1) SIG alone on transplants exceeds 5 % on some targets (the anti-conservatism carries over to real data); (Q2) FULL ∧ δ ≤ 5 % on every target; (Q3) δ removes all synthetic rigid-wall acceptances (their T ≈ 0.002 R) while keeping ≥ 90 % of phase-gated detections and both real detections (2-V2 0.067/0.075, 20-V1 0.043–0.053). If Q2 fails, the paper states the real-data false-positive rate as measured and weakens the detection claims accordingly.
**R5 results (2026-10-13).** Label transplant on 10 real windows (1,474 placements): significance alone accepts **5.8 %** on average (per target 0–16.7 %; the 16.7 % is 1 of 6 placements on 17-V1); significance ∧ δ 4.0 % (max 9.7 %, 33-V1, 31 placements); **FULL 1.5 % (max 4.0 %, 2-V2, 654 placements); FULL ∧ δ 1.4 % (max 4.0 %)**. On real video the circular-shift p is close to nominal on average; the severe anti-conservatism (to 28 %) is specific to the nearly flat floor series of rigid-wall renders, and δ = 0.02 R removes it there (≤ 2 % on every synthetic null, all phase-gated detections kept). Predictions: Q1 ✓ (SIG > 5 % on 4 targets), Q2 ✓ (FULL ∧ δ ≤ 5 % on every target), Q3 ✓ (δ removes synthetic rigid-wall acceptances, keeps 100 % of phase-gated and both real detections). Adopted for the paper: detection = FULL ∧ T ≥ 0.02 R; its real-data false-positive rate is 1.4 % on average, ≤ 4 % per clip.

## 13-V3 (new CT-paired case, 2026-10-17) — declared before running
Calibration 0.17 px; CT (gated angio, 1 mm lung series) segmented: 68 mm trachea, D_CE median 7.2 mm. Reconstruction probe: f1819–2020 in one model with overlap 90. PI labels (final, third version): OUT 1836–1842, 1884–1890, 1979–1985; f1960–1976 excluded; grade 1/3, likely normal. **Label independence: NOT independent** — the windows were revised after I reported an image-domain floor-position measurement (1848→1839; 1934 dropped). Therefore reported as a separate, non-independent row and excluded from the detection count unless re-marked blind. Run with the unchanged pipeline (`tmi_batch_clip.sh`, overlap as production 30 — and, if it fragments, overlap 90 as in the probe), plus labelled limit, window consistency, pair test with null, and the R5 detection rule (FULL ∧ T ≥ 0.02 R). Prediction: given grade 1/3 and likely normal, floor OUT−IN below the detection rule; if detected, it does not enter the detection count (non-independent labels).
**13-V3 outcome (2026-10-17):** SfM (overlap 90) one model f1829–2020 (gap 1962–1975), 154/166 registered; path doubles back at 5/14 stations, median tilt 35°; 4 % trusted cells. The floor series is finite on only 34 frames and only the first OUT window has floor data (7 frames), so window consistency and the plateau cannot be evaluated: floor OUT−IN −0.0015 R, p 0.53, L_0.05 0.053 R; controls roof −0.006, sides +0.021 / +0.038. → **not measurable** (sparse floor on a short, tilted, doubling-back segment). Prediction ("below the detection rule") holds trivially. Labels were non-independent in any case. 13-V3's CT (68 mm trachea, D_CE 7.2 mm) remains available for a static calibre check.
