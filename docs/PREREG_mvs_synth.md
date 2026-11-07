# Pre-registration: does the production MVS pipeline compress wall motion at the floor-side grazing geometry?

Written **before any production run**. Design fixed; the renderer and its smoke test are the only things run so far.

## The question

Image-domain measurement says the normal airway's floor moves ~4–5× (pixels) the malacic one's; the pipeline's
peak-centred result says they move the same, which converts to ~1.5×. A ~3× gap on the pipeline's side, with arc
placement, floor depth and image-method inflation ruled out (§24–26). Hypothesis: MVS depth on the floor — the
**near** wall, viewed at **grazing incidence** from a floor-side scope pitched up (§28 correction) — smears radial
excursion toward the rigid mean, so the pipeline under-reads floor motion, more so where the geometry is more
grazing. The existing power curve could not test this: it used analytic depth and never ran MVS.

## What is rendered (`tests/render_breathing_tube.py`)

Textured tube, R = 5, aperiodic albedo (no helical symmetry), irregular cartilage rings that vanish on the floor,
co-located light (falloff 1.3, ambient 0.06), circular scope mask, 2 % noise, 1280×720, fx 500 (HFOV 104°), 300
frames, forward-looking withdrawal at **0.026 R/frame** (20-V1's measured speed), period **48** frames. Wall motion:
`r = R(1 + A·exp(−((θ−θ_floor)/35°)²)·cos(2πt/48))`. Labels: OUT = within ±30° of peak-open (17 % duty, as 20-V1).
Verified by eye (`docs/figures/mvs_synth_smoke.png`): lumen above centre, ringless floor at the bottom in grazing
streaks, as in the real frames.

## Geometries (camera perpendicular offset from the axis, pitch toward the axis)

| tag | offset | pitch | why |
|---|---|---|---|
| **G0** | 0 | 0° | on-axis control |
| **G1** | **−0.28 R** (floor-side) | 15° | 20-V1's measured recentring offset and median tilt |
| **G2** | **−0.22 R** (floor-side) | 15° | 2-V2's measured offset (tilt 12.5°; 15° used for both so only offset varies) |
| **G3** | +0.28 R (roof-side) | 15° | sign-check on the floor-side reading of §28 |

Amplitudes: **A = 0** (static; negative gate per geometry) and **A = 0.07 R** (between the two real values). A third
level (0.10) only if time allows, for linearity.

## The pipeline — unchanged production stages, nothing substituted

`m1/real_sfm_relaxed.py` on the rendered MP4 (its own extraction, bezel mask, CLAHE, pinned intrinsics from
`calib.json`, sequential matcher, mapper) → `m1/windowed_depth_real.py` with the A/B-validated production flags
`--max-size 1000 --recentre --ahead 0.5,5.0 --frame global --radius-from rings --min-baseline 3 --max-gap 12`
→ `label_core` separation with the labels above.

## The measurement and its truth

**Recovered:** label_core's floor-arc separation on the reconstructed grid, exactly as on the real clips.
**Truth:** the *same statistic* applied to the planted `r(θ, t)` sampled on the same stations and sectors — so the
Gaussian arc shape, the 60° arc average and the phase-mean factor are identical on both sides and the ratio
**recovered / true** is apples to apples. Also reported: peak-centred recovery, and `dynamic_tube` peak-to-trough
against planted peak-to-trough.

## Pass / fail, fixed now

1. **Negative gate**: at A = 0, |separation| < 0.01 R for every geometry. Fail → that geometry's MVS produces
   phase-correlated artefacts and its A = 0.07 result is uninterpretable.
2. **Hypothesis survives** if recovered/true at **G1 and G2 is systematically below G0**, and below it by enough to
   matter: G0 ≥ 0.8 and G1, G2 ≤ 0.6, with G1 − G2 in the direction that would explain the real ratio (the more
   grazing geometry recovering less).
3. **Hypothesis dies** if G0, G1, G2 all recover within ±25 % of each other. The ~3× gap then needs another cause.
4. **Sign-check**: G3 is reported; if G3 behaves like G1/G2 while G0 differs, the effect is "off-axis" not
   "floor-side", which still supports compression but not the specific mechanism.

## Named failure modes

- Rendered texture is richer and more uniform than mucosa; MVS may do *better* than on real clips, understating
  any compression. A pass here is therefore conservative; a fail is informative.
- SfM may fragment on a synthetic (as it did on real clips); the largest model is used and its span reported.
- Disk: ~2–3 G per MVS run against 10 G free; runs are sequential with depth maps deleted after each grid is saved.

## Pre-run calibration record (written and committed BEFORE any G/A run; 2026-10-04)

The first smoke renders had 9–11k production keypoints/image against ~1.6k on real 20-V1 (`runs/real_20V1_lab`, 561 frames, median 1568). The side-by-side (`docs/figures/mvs_synth_keypoints_vs_real.png`) showed three renderer artefacts, not a texture-amplitude problem: nearest-neighbour texture lookup (mosaic on the near floor), an unblurred per-texel noise term (sandpaper under CLAHE), and an image circle of 0.46 W where 20-V1's rim is 414 px at fx 717.5 = 0.68 fx after undistortion. Fixed: bilinear lookup, blurred scales only, optical PSF σ 1.2 px, sensor noise 0.006, brightness p97 → 255 (slight near-wall saturation as in the real frames), circle 0.265 W, lighting falloff 2.0 / ambient 0.010.

Texture amplitude then calibrated against ONE criterion fixed in advance — production-extractor keypoints/image on a 30-frame G1 render vs the real median 1568: tex 0.30 → 1900, **0.18 → 1782 (chosen, +14 %)**, 0.10 → 1559. Richer-than-real stays the conservative direction (easier for MVS). Side checks, not tuned on: keypoint scale p50/p90 2.20/6.48 vs real 1.57/6.19; keypoint radial distribution inner/outer third 0.21/0.39 vs real 0.14/0.51; CLAHE'd dark<40 fraction 0.10 vs real 0.03–0.10, dark<80 0.33 vs 0.17–0.29 (synthetic slightly darker = far wall slightly harder); SfM on each calibration clip 30/30 in one model. Frozen renderer defaults: `--tex 0.18 --tex-blur 1.0` plus the values above. Figures: `mvs_synth_smoke3.png` (raw | CLAHE | real).

Run order (sequential, quota-bound): G0_a0.07, G1_a0.07, G0_a0, G1_a0, G2_a0.07, G3_a0.07, G2_a0, G3_a0 via `tests/mvs_synth_run.sh TAG OFFSET TILT AMP 0.18 1.0`; SfM `--overlap 30` as in the real runs; truth by `tests/mvs_synth_truth.py` (label_core statistic on the planted field at the recovered grid's own stations/sectors/visibility; analytic value alongside). Pass/fail criteria above are unchanged.

## Amendment 1 — declared after G0_a0.07 and G1_a0.07, before any further arm is read (2026-10-04 ~16:00)

Observed so far (both arms done, recorded in RESEARCH_calibration §29–30): G0 recovered/true 1.64, G1 1.56 — no compression at the 20-V1 geometry. Sector coverage differs from the real 20-V1 grid: G0 covers the whole ring at 0.18–0.23 of cells, G1 covers only the floor half (0.16 around the floor, 0.01 at the roof), while the REAL 20-V1 grid covers the whole ring at 0.05–0.10 with the roof slightly *better* than the floor. The missing roof in G1 is most likely my lighting (falloff 2.0 / ambient 0.010 leaves the far roof at grey ~20–40 in the raw render; the real scope's spread light + auto-gain shows the roof at mid-grey).

**Added arm, declared before it runs:** `G1lit_a0.07` — identical geometry and planted field to G1, lighting `--falloff 1.3 --ambient 0.03` (the renderer's original gentler values). Purpose: realism robustness only. Expectations written down now: (a) roof coverage should appear (> 0.05 at ±165°); (b) if the G1 conclusion is robust, the floor-arc recovered/true stays within ±25 % of 1.56 and well above the 0.6 compression threshold; (c) if it drops below 0.6 the lighting, not the geometry, drove G1 and the whole test is re-examined. It is reported whatever it shows. It does not replace G1 in the pass/fail table; the pre-registered arms and criteria are unchanged. It runs after the eight pre-registered arms (quota-bound, sequential).

## Results (appended as each arm finishes; the table is the deliverable)

| arm | geometry | planted A | recovered floor sep (R) | lattice truth (R) | recovered/true | roof / sides (R) | gate |
|---|---|---|---|---|---|---|---|
| G0_a0.07 | on-axis, 0° | 0.07 | +0.0891 | +0.0544 | **1.64** | +0.015 / −0.013, −0.011 | ≥ 0.8 ✓ (by over-recovery) |
| G1_a0.07 | −0.28 R floor-side, 15° (20-V1) | 0.07 | +0.0863 | +0.0555 | **1.56** | +0.004 / +0.001, +0.001 | ≤ 0.6 ✗ — no compression |
| G0_a0 | on-axis, 0° | 0 | −0.0003 | 0 | — | +0.0004 / −0.0001, +0.0003 | negative gate ✓ (|sep| < 0.01) |
| G1_a0 | −0.28 R floor-side, 15° | 0 | +0.0016 | 0 | — | n/a (no roof coverage) / +0.0003, −0.0010 | negative gate ✓ (|sep| < 0.01) |
| G2_a0.07 | −0.22 R floor-side, 15° (2-V2) | 0.07 | +0.0952 | +0.0556 | **1.71** | +0.070† / −0.007, +0.002 | ≤ 0.6 ✗ — no compression |
| G3_a0.07 | +0.28 R ROOF-side, 15° (planted wall is the FAR wall) | 0.07 | −0.0165‡ | +0.0582 | (−0.28)‡ | +0.0005 / −0.002, +0.000 | reported, no gate: far wall not measurable |
| G2_a0 | −0.22 R floor-side, 15° | 0 | +0.0013 | 0 | — | −0.0019 / +0.0008, −0.0004 | negative gate ✓ (|sep| < 0.01; its shift-null p = 0.02 is the periodic-label artefact noted above, not a detection) |
| G3_a0 | +0.28 R ROOF-side, 15° | 0 | n/a (no far-wall data) | 0 | — | +0.0008 (near wall) / −0.0001, −0.0003 | negative gate ✓ on the measurable (near) wall and sides |
| G1lit_a0.07 (amendment 1) | G1 geometry, lighting falloff 1.3 / ambient 0.03 | 0.07 | +0.0830 | +0.0552 | **1.50** | n/a / +0.0035, +0.0032 | expectation (b) met: within 4 % of G1's 1.56; expectation (a) NOT met: roof coverage still 0.00–0.03 → the missing roof is not lighting (cause unexplained) |

† The G2 roof value comes from almost no data: only 6 % of (frame, station) cells have even one trusted sector inside the 60° roof arc (4 % have ≥ 3), against 22 % for the floor arc; the per-sector harmonic profile puts the roof at −0.01 R (anti-phase, like G1), so +0.070 is an aggregation artefact of sparse coverage, not a roof motion. G2 diagnostics otherwise repeat G1: in-phase floor gain 1.34–1.37 in the angular profile, all non-floor sectors anti-phase −0.01 to −0.04 R, quadrature gains −5.7 / −7.5 at d = 1–2 / 2–3 R, pose wobble 0.005 R perpendicular / 0.026 along-axis / 0.025°.

‡ G3 is not a sign inversion of a measured wall; it is a wall that was not measured. Floor-arc coverage is 0.02–0.04 of cells (vs 0.16–0.17 in G1/G2), only 6 OUT frames carry any floor data (G1: 45), and where far-wall points exist their radii are grossly wrong (≈ 0.75 R at station 46 against a planted 1.0–1.07). The per-sector harmonic *is* positive and in phase where cells exist (floor ratio 1.3–3.3; d-binned in-phase gains +0.18 at 2–3 R, +2.57 at 3–4 R), so the pipeline is not inverting motion — it has no usable far-wall data, and the pooled OUT−IN number from 6 frames is noise. Lesson for the real clips: only the NEAR wall (the floor the scope rides, 1–3 R ahead) is readable; the opposite wall is not.

Series-level fact (both geometries, `docs/figures/mvs_synth_series_G1_G3.png`): the recovered pooled floor-arc series has std 0.25 R in G1 against a planted-truth std of 0.033 R (corr 0.24) — frame to frame it is dominated by the velocity term; the OUT−IN statistic recovers the signal only by averaging ~45 OUT frames × ~9 stations at the extremes.

**Label-shift sensitivity (`tests/mvs_synth_shift.py`, run after the arms, not pre-registered — reported in full).** Shifting ALL labels by k frames (truth shifted identically) gives, for G0 / G1 / G2, recovered separation +0.42/+0.35/+0.35 R at k = −8, **+0.089/+0.086/+0.095 at k = 0, +0.014/+0.015/+0.030 at k = +1, −0.065/−0.059/−0.042 at k = +2**, −0.32/−0.33/−0.33 at k = +8, while the truth moves smoothly 0.028 → 0.054 → 0.021. The recovered OUT−IN is a steep, nearly antisymmetric ramp through zero at k ≈ +1: it is the velocity term sampled by the window, not a position measurement, and the 1.6× at k = 0 is one point on that ramp. In this configuration (period 48 frames, 0.026 R/frame, d/b ≈ 5–30) the pipeline's floor-arc OUT−IN separation is determined at the one-frame level by where the labels sit relative to the true extremes. Whether the REAL clips behave the same way is testable with the clinician's labels shifted by k on the real grids (next).

**FINAL VERDICT (all eight pre-registered arms complete, 2026-10-04 18:23).** Criterion (1) negative gates: pass at every geometry (|sep| ≤ 0.0016 R on every measurable arc). Criterion (2) survival: **fails** — G0 1.64, G1 1.56, G2 1.71 (G1/G0 0.95, G2/G0 1.04); nothing compresses at grazing incidence. Criterion (3) death condition ("all within ±25 %"): **met**. Criterion (4) G3: the opposite wall is not measurable (coverage 2–4 %), not inverted. The grazing-compression hypothesis for the pipeline-vs-video magnitude gap is dead. Post-hoc but reported in full: the synthetic recovered/true is a velocity ramp sampled by the labels (sign flips at +2 frames) and is NOT a calibration; the real clips with the clinician's labels are label-shift stable over ±8 frames with no sign change (RESEARCH §32–33). G1lit (amendment 1) done: 1.50 — the G1 verdict is robust to lighting; the roof stays unreconstructed under gentle lighting too, so the coverage difference from the real 20-V1 grid (roof 0.07–0.10 there) has a cause other than lighting, not identified; its label-shift profile is the same ramp (sign flip at +2 frames).

Verdict trail: criterion (2) fails (G1 ≈ G2 ≈ G0: 1.56 / 1.71 / 1.64); criterion (3) "dies if all within ±25 %" is met by G0 vs G1 (5 % apart). Remaining arms are reported for completeness, not because they can change the verdict.
