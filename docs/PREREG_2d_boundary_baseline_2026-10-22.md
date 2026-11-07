# 2-D posterior-boundary baseline (2026-10-22) — declared before building/running
Question (reviewer-anticipated): does the 3-D pipeline beat directly tracking the visible bright→dark lumen boundary in the image?
Baseline B2D (runs/b2d/b2d.py): per frame (raw → grey, Gaussian σ 2 px, bezel circle), lumen centre = centroid of the darkest connected region
(grey ≤ 10th percentile inside the circle); 72 rays from that centre; on each ray the boundary = radius of the maximum positive radial gradient
(dark lumen → bright wall) within the circle; posterior radius r_p = median over rays within ±30° of image-down; s_t = r_p / median over all rays
(scale-free: cancels zoom / axial scope motion). Readout = OUT−IN of s_t at the labels (units: fraction of lumen radius); significance by the
same circular-shift null AND the off-phase null; detection = p < 0.05 AND |OUT−IN| ≥ 0.02 (no 3-D checks exist for B2D, by design).
Evaluation (same data as the 3-D method): (i) planted renders with truth-phase labels — motion: held-out M_G1_s61, M_G2_s62, M_G1irr_s63,
M_G1cb_s64, MS_G1_s65, M_G1_s71, M_G2_s72, M_G1irr_s73, M_G1cb_s74, MS_G1_s75; nulls: N_G1_s66, N_G2_s67, N_G1cb_s68, NS_G1_s69, NS_G2_s70,
N_G1_s76, N_G2_s77, N_G1cb_s78, NS_G1_s79, NS_G2_s80; reported: detection rate, readout vs planted (gain); (ii) clinical windows with the
clinician labels (2-V2, 20-V1 wd, 18-V1, 7-V1, 33-V1 wd, 20-V1 ins; nulls 26-V2, 31-V1, 17-V1 wd, 2-V1).
Descriptive comparison (no pass/fail): B2D vs the 3-D pipeline on sensitivity, false detections, gain, and agreement on clinical windows.

## Result (runs/b2d/summary.txt) — descriptive
Renders, motion (10): detected 1 / 10 (circular null), 4 / 10 (off-phase null). Renders, nulls (10): FALSELY detected 2 / 10 (circular), 3 / 10
(off-phase: N_G1_s66, N_G2_s67, NS_G2_s80). Clinical: no detections — 2-V2 +0.10 (p 0.14 / 0.24), 20-V1 wd −0.08 (wrong sign); nulls not detected.
Per-frame spread of the boundary ratio 0.10–1.12 (the bright→dark edge jumps with lighting and view).
Comparison: the 3-D pipeline (off-phase rule) keeps phase-gated planted motion in ≈ 82–88 % of trials with 0 / 10 null renders at δ ≥ 0.01 R and
detects both clinical windows; it is ≈ 0 % with sequential sources, where B2D's 10–40 % comes with 20–30 % false detections. Conclusion
(limited to this straightforward pre-declared baseline): direct 2-D boundary tracking is neither sensitive nor specific on these data.
