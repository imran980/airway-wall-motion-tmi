# Reviewer items 1, 3, 7 (2026-10-27) — declared before computing
## Item 3: the paper's own diagnostics on the clinical windows, and a camera check in the rule
(3a) Harmonic decomposition on clinical clips: label-derived phase φ_t (OUT-window centres = 0, linear in time to the next centre = 2π);
quadrature fit S_t = c cos φ + q sin φ + k on the retained grid; report c, q, |q|/|c| per clip. Render reference (exact-geometry runs):
sequential |q|/|c| 3.1–4.0, phase-gated ≈ 0.04. A clip is called position-dominated if |q|/|c| < 1.
(3b) Camera-periodicity check: for each camera variable (pitch, yaw, roll, axial, two lateral; SfM poses) the OUT−IN at the labels with
the primary circular-shift null; and the pose-regression retention of the floor coefficient (already pre-registered, criterion ≥ 70 %).
Rule extension (fixed now): a detection additionally requires pose retention ≥ 70 % (floor coefficient after regressing out all six camera
variables keeps ≥ 70 % of its value and its sign). Applied unchanged to (i) the C3VD null placements (all 1,301; question: does it remove
the 7–11 % periodic-label false acceptance?) and (ii) every clinical window (retained grids; 2-V2 both reconstructions).
(3c) Regime index from the depth-free pair amplitude: |ε/β| = v d/(s r) with v = 2π a/P, a = the clip's mean pair-test S (not an assumed
0.05 R), d = median station depth, s = median axial speed; for 2-V2 and 20-V1 (the clips with pair data).
## Item 7: identifiability of position vs velocity
Numerical, no new data. With the exact two-view model (runs/theory/exact_geom.py geometry, on-axis and the G1 off-axis camera) compute,
for a wall r(t) = R(1 + a cos φ), the per-frame readout r̂ for each source policy (sequential τ = 3–6 frames; stop-and-go; phase-gated
τ = one cycle), its linear decomposition r̂ − r ≈ g_p·p + g_v·v (sensitivities to position p and velocity v), and the quadrature
coefficients (c, q). Report |q|/|c| and the in-phase bias produced by a label-phase error δ (Δc ≈ q sin δ) as functions of |ε/β| and τ;
derive the phase accuracy needed for a ≤ 20 % position bias, and compare with the label timing uncertainty implied by the clinician's
±2-frame plateau check. Also the 2×2 Fisher information for (c, q) under per-frame noise σ with phase jitter σ_δ, giving the conditioning
of the position estimate per policy.
## Item 1: renders driven by the clinical camera trajectories
Renderer option to replay a camera path (per-frame centre and orientation in tube coordinates) and a per-frame phase table. For 2-V2
(f2870–3370) and 20-V1 wd (f2517–2823): tube frame from the retained reconstruction (axis = station line, +y = mean camera down ⟂ axis,
centre = lumen centre per station), camera centres in units of R, orientations relative to that frame; phase from the clinician's labels
(as in 3a), so the planted motion is locked to the clinician's breathing timing and the clinician's own labels are the true labels.
Renders: each clip × {motion 0.07 R, rigid} × 2 seeds (texture), sequential sources, production pipeline. Scored with the unchanged rule on
the clinician's labels, plus the quadrature fit.
Predictions (stated, not tuned): (R1) rigid replays accept nothing; (R2) if the render model explains the clinical readings, the motion
replays reproduce the sign of each clip's clinical readout (+ for both) and |q| < |c|; if not (as the parametric matched renders
suggest), the clinical readings remain unexplained. Either outcome is reported.

## Item 3 results (runs/r6/item3.{py,log,json})
(3a) Label-phase harmonic decomposition on the retained clinical grids, |q|/|c|: 2-V2 0.51 and 0.11 (two reconstructions), 20-V1 wd 0.42,
18-V1 0.24, 31-V1 0.35, 2-V1 0.72, 20-V1 ins 0.60 (c negative) — position-dominated; 7-V1 1.66 and 33-V1 9.9 — velocity-dominated (the two
first-run detections that did not reproduce); 26-V2 7.4 and 17-V1 3.7 have c ≈ 0 (ratio uninformative). Renders: sequential 3.1–4.0.
(3b) Camera check in the rule (pose retention ≥ 70 %, same sign). Clinical: only 2-V2 reconstruction B passes (77 %); 2-V2 A fails (64 %),
20-V1 fails (sign reverses). C3VD: 21/1,301 → 9/1,301 false accepts (1.6 % → 0.7 %); the camera-period family (134 frames) 9 → 0; its third
harmonic (45 frames) 9 → 6; the 33-V1 pattern 3 → 3.
(3c) Regime index with the measured pair amplitude: 2-V2 |ε/β| median 0.38 (16 % of frames ≥ 1); 20-V1 wd 0.95 (47 % ≥ 1).
## Item 7 results (runs/r6/identifiability.{py,log,json}; docs/figures/paper/fig_identifiability.png)
Exact two-view model, sequential sources: |q|/|c| ≈ 1.2 (|ε/β| < 0.1), 3.0 (0.1–0.3), 8.7 (0.3–0.6), 18.6 (0.6–1.2); phase-gated ≈ 0
(c/a ≈ 1.00). Measured sequential renders (|q|/|c| 3.4 at |ε/β| 0.25) lie on the model curve. Phase accuracy needed for ≤ 20 % position
error: 9.6° (|ε/β| < 0.1), 3.8° (0.1–0.3), 1.3° (0.3–0.6), 0.6° (0.6–1.2); the clinician's ±2-frame timing is 9° (2-V2) and 15° (20-V1).
The clinical points (|q|/|c| 0.11–0.51 at |ε/β| 0.38–0.95) lie 1–2 orders of magnitude below the model: at their regime, static stereo of a
moving wall would be strongly velocity-dominated and position would not be identifiable from label timing. The clinical readings therefore do
not behave as the render model predicts (consistent with the matched-render result).
## Item 1 results (runs/r6/item1_score.{py,log,json}; traces runs/r6/item1_series.png) — 2026-10-28
Replays: 2-V2 501 frames (axial −11.05 R, lateral 0.21 R, tilt 2.4°), 20-V1 wd 307 frames (−6.85 R, 0.50 R, 5.5°); all 8 reconstructed as one
large model (302–501 frames). Scored with the unchanged rule on the clinician's labels; T_truth = the same statistic on a perfect floor reading.
| render | T | T_truth | p | detected | pose ret. | |q|/|c| |
| M 2-V2 s131 | +0.024 | +0.048 | 0.134 | no (sig) | 0.82 | 0.15 |
| M 2-V2 s132 | +0.021 | +0.048 | 0.142 | no (sig) | 0.95 | 0.10 |
| M 20-V1 s135 | +0.111 | +0.060 | 0.144 | no (sig, plateau, window) | 0.27 | 0.73 |
| M 20-V1 s136 | +0.018 | +0.060 | 0.266 | no (sig, window, minT) | 1.77 | 2.60 |
| N 2-V2 s133/s134 | +0.000 / −0.001 | 0 | 0.68 / 0.71 | no | — | — |
| N 20-V1 s137/s138 | −0.001 / −0.002 | 0 | 0.70 / 0.94 | no | — | — |
(R1) PASS: rigid replays accept nothing (0/4). (R2) sign + 4/4; |q| < |c| 3/4 (both 2-V2 seeds 0.10–0.15, matching the clinical 2-V2 0.11/0.51;
20-V1 0.73 and 2.60, seeds disagree); but 0/4 motion replays are detected. Visual check: the 2-V2 readings track the planted wave in phase at
≈ 0.45× its amplitude (frames 150–300, 370–450); the 20-V1 readings are dominated by large swings not locked to the wave (rigid 20-V1 is flat, so
the swings need the moving wall); a spike at render frames ~100–107 in both rigid 2-V2 seeds is a camera-path event (T unaffected).
Reference (not a test): the rule detects a perfect floor reading on both label sets (p ≤ 0.006, all checks), also with iid noise 0.01 R, so the
failure is attenuation + structured error of the reading, not the null.
Outcome: the real 2-V2 camera path reproduces the clinical CHARACTER (+ sign, position-dominated) but at 0.07 R planted the reading (0.021–0.024)
is ≈ 1/3 of the clinical 2-V2 readout (0.066–0.075) and not significant; 20-V1 is not reproduced (seed-dependent, camera check fails, as clinically).
Descriptive, NOT pre-registered: the replays' own regime index (planted amplitude) is 2-V2 0.21–0.22, 20-V1 0.43–0.79; at 0.21 the item-7
sequential model predicts |q|/|c| ≈ 3, the 2-V2 replays give 0.10–0.15. So rendered static stereo of a moving wall along the REAL 2-V2 path also
falls far below the steady-motion model curve. This withdraws the item-7 inference that the clinical points' position for |q|/|c| shows they
"do not behave as static stereo of a moving wall": the model curve describes steady sequential motion, not the measured clinical paths.
