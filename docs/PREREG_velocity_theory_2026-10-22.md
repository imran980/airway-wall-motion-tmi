# Velocity-artefact theory for axial scope motion (2026-10-22) — derivation + predictions declared before computing
Derivation. Camera moving along the tube axis at speed s (per frame, + = toward the wall point), wall point at depth d and radius r, radial wall
velocity v; source frame τ frames away. Image radial coordinate ρ = f r / d. With the source: ρ1/ρ0 = (1 + ε)/(1 − β), ε = vτ/r, β = sτ/d.
Static two-view triangulation along the known translation gives d̂ = d β(1+ε)/(β+ε) and r̂/r = β(1+ε)/(β+ε) ≈ 1/(1 + v d/(s r)), i.e.
  r̂ − r ≈ −(d/s) v       (first order; τ cancels; same sign for sources before and after the frame).
Consequences: the static-stereo error is a VELOCITY term (quadrature to position), scaled by the time the camera needs to travel the wall depth;
its sign flips with travel direction; it vanishes when sources share the breathing phase (vτ ≈ 0: phase gating). The paper's "∝ Δt(s/d + v/r)"
is replaced by this result.
Predictions (A, renders; truth phase φ_t known; floor series S_t = pooled floor statistic in R, regressed on [cos φ_t, sin φ_t, 1]):
 A1 sequential renders (constant withdrawal: dev M_G0_s21, M_G1_s22, M_G2_s23, M_G1irr_s24 + held-out sequential grids s61–s75): the
    quadrature coefficient dominates, |q| > 2 |c|;
 A2 implied depth d_eff = |q| |s| / (A w ω) lies inside the station depth range 0.5–5 R (s = measured axial camera speed, w = mean floor-arc
    weight, ω = 2π/period);
 A3 phase-gated (K4) renders: |q| < |c| and c / (A w) in 0.6–1.2 (position reading).
(B, real clinical windows; descriptive) S_t regressed on the label indicator (position) and on the predicted velocity regressor −v̂_t/s_t
(v̂_t = derivative of the smoothed indicator, s_t = measured axial camera speed); report which explains more variance, and the measured
source-frame separations τ (selection rule of m1/windowed_depth_real.py: |j−k| ≤ 12, baseline ≥ 3 median steps, nearest six) — median τ,
fraction of frames with ≥ 2 sources.

## Results
A (runs/theory/part_a.log): sequential constant-speed renders (10): |q|/|c| 3.2–4.0, q < 0 in 10/10 (withdrawal), d_eff 1.10–1.42 R — A1 and A2
met. Camera riding the breathing (2): |q|/|c| 1.95–1.98 (just under 2), d_eff 0.22–0.24 R (outside 0.5–5) — the constant-s model does not fit
when s is breathing-locked. Stop-and-go (2): |q|/|c| 5–9, d_eff 0.44–0.49 R (borderline; non-constant s). Phase-gated (10): |q|/|c| median 0.2,
c/(A w) 0.64–0.82 — A3 met. In-phase coefficient on sequential renders inflated (c/Aw 1.45–1.99; second-order term).
B (runs/theory/part_b.log): source separation τ median 4–5 frames (p10–p90 2–10), 92–100 % of frames with ≥ 2 sources. Variance explained,
position vs predicted velocity regressor: 2-V2 0.110 / 0.002; 20-V1 wd 0.021 / 0.002; 18-V1 0.126 / 0.099; 33-V1 wd (not reproduced) 0.038 /
0.041; nulls ≈ 0. Caveat: the velocity regressor is built from the clinician's short OUT windows, a crude proxy for the wall velocity.
Paper: the "∝ Δt(s/d + v/r)" sentence replaced by the derivation (new equation) and the render verification.
