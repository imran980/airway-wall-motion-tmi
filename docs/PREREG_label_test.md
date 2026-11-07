# Pre-registration: does the estimator agree with the clinician?

Written **before** the reconstruction of the labelled stretch finished, and committed with its timestamp, because
every finding that dissolved in this project dissolved on a choice made after seeing the answer.

## The labels

The PI marked frames of **20-V1** by eye, watching the floor of the airway:

- **inward** (the floor bumps up, the airway shrinks): f900, 960, 1020, 1050, 1110, 1140, 1200, 1260, 2100, 2160,
  2190, 2250, 2340, 2550, 2610, 2640, 2700
- **outward** (the floor drops, the airway opens): f930, 990, 1080, 1170, 1230, 2130, 2220, 2280, 2310, 2370, 2430,
  2520, 2730
- **between** (not used): f2400, 2460, 2490, 2580, 2760

These labels carry their own rhythm: fitted alone, with no images and no geometry, they give **23.8 per minute
overall and 24.0 for the second cluster**. 20-V1's vocal cords, measured independently from the glottic aperture,
give **24 per minute with autocorrelation +0.67**. Two independent routes to the same rate.

## What is fixed in advance

**The arc is geometry, not a fit.** "The floor" is the bottom of the endoscopist's view. For each station the floor
direction is the camera's own down-axis, taken from the real poses, projected into that station's frame and averaged
over the frames that saw it. No deviation value enters it. On the existing whole-clip reconstruction this gives
**−34°, with agreement across stations of 0.89**, so the floor is a well-defined direction and not a fitted one.

**The statistic** is mean(sectoral deviation | outward) − mean(sectoral deviation | inward) at the floor arc, arc
width 60°, pooled over the stations visible at each frame with the per-ring common mode removed. It is **one-tailed**:
the estimator agrees only if this is positive.

**The null preserves the labels' rhythm.** The marks alternate about once a second, so a free shuffle would destroy
an autocorrelation the data really has and flatter the result. The null instead circularly shifts the whole label
sequence by a random lag, keeping its rhythm and destroying only its alignment with the estimator. 2000 draws.

**The control** is the arc 180° away, the roof. It was never fitted and should show nothing.

**The threshold** is p < 0.05 one-tailed at the floor, with the roof not significant.

## What has already been seen, and why it does not contaminate this

A dry run on the existing whole-clip reconstruction, which only 6 of the 30 labels reach, gave floor separation
**+0.167 R, p = 0.207**, and roof separation −0.007 R, p = 0.461. The direction is right, the control is null, and
neither result is significant at n = 6. Nothing about the arc, the statistic or the null was chosen from it, because
the arc comes from geometry and the rest was written down first. The confirmatory run uses
`runs/m1_20V1_lab` (frames 2060–2620), which reaches 18 labels, of which **16 were not in the dry run**. Both the
full 18 and the fresh 16 will be reported.

## What each outcome means

- **Floor significant, roof not**: the estimator tracks the wall motion a clinician can see. That is the first
  external validation of the deformation estimate in this project, and it would make the amplitude worth arguing
  about.
- **Neither significant**: the estimator does not track what the clinician sees, at this sample size. Given the
  reproducibility limit already measured, that is the more likely outcome and it bounds what the method can claim.
- **Roof significant too**: something common to the whole ring is moving with the labels, and the common-mode
  removal is not doing its job. That would be a defect to fix, not a result.

---

## Result, run once as specified

`runs/m1_20V1_lab` (SfM split; the largest model, 449 frames f2060–2508, was used — the new model-picker reported
`2 sub-models present (0:113, 1:449); using the largest`). It reaches **11 labels, 9 of them usable, all fresh**.

| arc | inward | outward | separation | p |
|---|---|---|---|---|
| **floor, per station** | **−0.107 R** | **+0.008 R** | **+0.115 R** | **0.161** |
| roof, per station | +0.068 R | −0.014 R | −0.082 R | 1.000 |
| floor, one global arc | −0.016 R | −0.003 R | +0.013 R | 0.308 |
| roof, one global arc | +0.048 R | +0.016 R | −0.032 R | 0.801 |

**The pre-registered test does not reach significance: p = 0.161 against a threshold of 0.05.** With 4 inward and 5
outward frames it could hardly have. That is the result and it stands.

**An implementation deviation, reported because it changed the number.** The first run collapsed the per-station
floor directions into one global angle before pooling, which is not what the section above specifies ("for each
station the floor direction is..."). The cross-station agreement of the floor direction in this window is only
**0.42**, against 0.89 on the whole-clip reconstruction, because the scope rotates as it travels here — so one global
angle mixes different anatomical directions. Implementing the per-station form as written takes the separation from
+0.013 R to +0.115 R. Both are reported above. The per-station row is the pre-registered statistic; the global row is
the bug.

**What did happen, stated without spin.** The floor moves inward by 0.107 R on the frames marked inward and is flat
on those marked outward, a separation of 0.115 R, which is above the 0.05 R coherent-artefact floor measured on the
static phantom. The roof moves the *opposite* way, −0.082 R. A floor bumping up while the roof drops is a ring
flattening vertically, which is what the PI describes — but the pre-registration said the roof "should show
nothing", and it shows the reverse, so this is a deviation from expectation, not a confirmation of it. The
floor-minus-roof contrast is 0.197 R and was **not** pre-registered; it is exploratory and is recorded here only so
it cannot be presented later as though it had been planned.

**What would settle it.** Nine labelled frames cannot. The cheapest fix needs no compute: `mark_20V1_dense.png`
holds 63 panels at f2600–2850, every 4th frame, and that whole stretch already sits inside `runs/m1_20V1_full`.
Labelling those panels would raise n from 9 to about 60 inside an existing reconstruction, a sevenfold increase,
and the same pre-registered test could then be run unchanged.

---

## Replication, and the combined result

The identical test, with the same geometric arc rule and the same null, was repeated on **cluster 1 (f850–1320,
471 frames)**, which shares no frame with cluster 2. The replication was announced before its result.

| | labelled frames | floor separation | p | roof (control) | p |
|---|---|---|---|---|---|
| cluster 2, f2060–2508 | 9 (4 in, 5 out) | +0.115 R | 0.161 | −0.082 R | 1.000 |
| cluster 1, f850–1320 | 11 (8 in, 3 out) | +0.159 R | 0.116 | −0.025 R | 0.765 |
| **combined, 2 runs** | **20** | **+0.137 R** | **0.0565** | **−0.054 R** | **1.000** |

The combination pools the **within-run** differences, since each reconstruction has its own baseline, and applies
one joint null: the label sequence is shifted by a single random lag and both runs are re-scored with it, so the
labels' rhythm is preserved and shifting the runs independently cannot flatter the result.

**The combined test does not clear the pre-registered threshold: p = 0.0565 against 0.05.** It fails, narrowly, and
a threshold set in advance is not worth setting if it is moved afterwards.

What can be said alongside that, without claiming it:

- The effect **replicates**. Two structure-from-motion runs on non-overlapping footage, with an arc fixed by camera
  geometry rather than fitted, give +0.115 R and +0.159 R — the same sign and comparable size. A spurious effect has
  no reason to do that.
- Its size, 0.137 R, is well above the **0.05 R coherent-artefact floor** measured on the static phantom.
- The roof moves the other way in both runs, which is a ring flattening vertically and is what the PI describes.
  The pre-registration expected the roof to show *nothing*, so this remains a deviation from prediction. The
  floor-minus-roof contrast of 0.191 R was not pre-registered and is not tested here, deliberately: reaching for it
  now would be choosing a statistic after seeing that the planned one missed.

**What settles it, and it needs no compute.** `docs/figures/mark_20V1_dense.png` holds 63 panels at f2600–2850,
every 4th frame, and that stretch already lies inside `runs/m1_20V1_full`. Labelling them would take the sample from
20 to roughly 60 with no new reconstruction, and the same pre-registered test runs unchanged. At the observed effect
size that is the difference between p = 0.06 and a decisive answer either way.

---

## Correction, after the second audit pass

Three faults were found in the machinery behind the table above. None changes the verdict — **the test still fails
the pre-registered 0.05** — but the numbers in that table should not be quoted, and here is why.

**1. The table mixes two runs.** Its combined separation, +0.137 R, comes from `runs/label_combined.json`, which
predates the even-arc fix. The post-fix run, `runs/label_combined_fixed.json`, gives **+0.113 R** with a roof of
−0.047 R. The p of 0.0565 was carried across from the older run. The corrected separation is the one to use.

**2. The p-value was a Monte Carlo estimate of a quantity that can be counted exactly, and is not reproducible.**
With 30 labels the shift null has exactly **29** outcomes. The code sampled 5000 of them with replacement. Counted
exactly, the observed +0.113 R is reached by **2 of the 29 shifts**: p = 0.069 under the old convention, **p = 0.100**
under the standard conservative (k+1)/(n+1). Repeated Monte Carlo runs land at 0.057–0.058; the recorded 0.0565 is
not recoverable by enumeration. The test is now enumerated, so its p is exact and seed-free — and **5.5 seconds
instead of over twenty minutes**, because the pooled deviation was being recomputed inside every draw although it
does not depend on the labels at all.

**A limit that was never stated: a 29-outcome null cannot resolve below p = 0.033.** With this many labels the test
is barely able to address a 0.05 threshold. That is an argument for more labels, not for re-running this one.

**3. The roof was never a valid control.** If the wall moves as a dipole — floor in, roof out — the roof is
anti-correlated with the floor by geometry, so it cannot discriminate. The arcs at ±90°, which a dipole leaves at
zero, have been added and must also stay null. On the corrected grids:

| arc | separation | p (exact) |
|---|---|---|
| **floor (pre-registered)** | **+0.069 R** | **0.179** |
| roof (control) | −0.016 R | 0.800 |
| side +90 (control) | −0.008 R | 0.833 |
| side −90 (control) | +0.032 R | 0.033 |

The controls are much closer to zero than before, which is the frame fix working. But **side −90 now reaches the
null's resolution floor while the floor does not** — so the effect is not localised to the floor, and the
pre-registered statistic is not the best description of what is in the data.

### What the data actually shows, stated as exploratory

Scanning the separation over all 36 arc centres (**exploratory — the maximum of a scan is fished and is not a test**)
gives one coherent lobe, not scatter: positive from about −90° through the floor to +10°, negative across the
opposite side. That is a **dipolar wall motion locked to the clinician's labels, with its axis roughly 10–40° from
the floor the clinician named** — one to four sectors. The same lobe, with the same axis, appears on the old grids
too, so it survives both the frame and the radius correction.

The honest summary: **the direction the clinician described is recovered to within a few sectors, and the
pre-registered amplitude test does not clear its threshold.** Those are both true and neither should be dropped.

### One caveat that cuts against the effect size

Correcting the reference radius (it was measured from the camera path and read ~17 % low on these clips) tightened
the support gate, which is quoted in R, by the same ~17 %. Fewer sectors now qualify — support fell from 6.9 % to
4.2 % on cluster 1 — and the floor arc keeps only **10** labelled frames instead of 20. The smaller separation
(+0.069 R vs +0.113 R) is partly that loss of data, not only a truer measurement. **More labels remain the fix**:
`docs/figures/mark_20V1_dense.png` would take the sample to roughly 60 with no new reconstruction.

---

# Second test: dense labels over six respiratory cycles, f2517–f2823

The first test was underpowered by design — 30 labels, a null with 29 outcomes, unable to resolve below p = 0.033.
The fix was always more labels, not more analysis. The PI marked the window **1:24–1:34** by scrubbing a copy of the
clip with the frame number burned into every frame, listing only the **OUT** (floor drops, lumen opens) intervals in
milliseconds, on the instruction that every other frame in the span is **IN**. Labels are in
`labels/20V1_f2517_f2823.json`.

| OUT window (ms) | frames | duration |
|---|---|---|
| 85819–86110 | f2572–2581 | 0.29 s |
| 87520–87720 | f2623–2629 | 0.20 s |
| 89420–89600 | f2680–2685 | 0.18 s |
| 90858–90999 | f2723–2727 | 0.14 s |
| 92350–92700 | f2768–2778 | 0.35 s |
| 93827–94210 | f2812–2823 | 0.38 s |

**256 IN, 51 OUT, all 307 registered** in `runs/g6_tube` (20-V1 whole-clip, f2508–3000, rebuilt in the corrected
frame with the lumen-measured radius).

**A consistency check the labels pass before any estimate is involved:** the OUT windows recur every 43–57 frames —
1.43 to 1.90 s, mean 1.60 s, **37 per minute**. A regular rhythm at a plausible paediatric respiratory rate. Nothing
in the marking enforced that.

## Result

Identical machinery to the first test: the arc fixed by camera geometry rather than fitted, the null a circular shift
of the label sequence, and all three controls required to stay null.

| arc | separation | p (exact) |
|---|---|---|
| **floor** | **+0.055 R** | **0.023**  (6 of 306 shifts) |
| roof (control) | −0.020 R | 0.707 |
| side +90 (control) | +0.014 R | 0.326 |
| side −90 (control) | +0.004 R | 0.401 |

**The floor clears 0.05 and all three controls are null.** Four things support it, and three qualify it.

**Supporting it.**

1. **The p is conservative.** The only 6 shifts that reach the observed value are at lags 1, 53, 54, 303, 304, 305 —
   and on a 307-frame circle 303–305 are −4 to −2. So they are either **near-identity** (±1 to 4 frames, essentially
   the same labelling) or **one full respiratory period** (53–54, against a measured mean cycle of 48). *No genuinely
   misaligned shift reaches the observed separation.*
2. **It strengthens when transitions are removed**, which is the direction a real effect must move: excluding frames
   within ±3 of an OUT boundary gives **+0.063 R, p = 0.011**; within ±6, **+0.067 R, p = 0.004** (0 of 240 shifts).
   Controls stay null throughout. These are sensitivity checks, not the test — the headline is the unguarded 0.023.
3. **It replicates on disjoint halves.** First three cycles (f2517–2700): **+0.070 R, p = 0.049**. Last three
   (f2701–2823): **+0.056 R, p = 0.049**. Same sign, comparable size, controls null in both.
4. **The angular structure is a clean dipole, not a spike.** Scanning all 36 arcs gives one positive lobe from about
   −80° through the floor to +60°, peaking at **+40° (+0.070 R)**, and a negative lobe opposite. That is what a wall
   moving in and out about an axis looks like, and it is why the roof and sides are null: they sit on the nodes.

**Qualifying it.**

1. **This is not the pre-registered test.** The *analysis* was fixed in advance and is unchanged, but the labels and
   the reconstruction are new. It is a new test run with pre-specified machinery — confirmatory in design, not a
   re-run of the original, whose clusters remain at p = 0.100.
2. **The effect is close to the coherent-artefact floor.** A static phantom yields spurious periodic wall motion of
   about **0.050 R** from estimated depth; the separation here is 0.055–0.070 R. What argues against artefact is
   structure rather than size: an artefact has no reason to form a dipole whose positive lobe contains a floor
   direction derived independently from camera geometry, nor to leave all three controls null.
3. **One reconstruction.** The split-half is internal replication, not independent. The clean next step is a second
   labelled window elsewhere in the clip, scored on a reconstruction that does not share these frames.

## What this is, stated plainly

**On 20-V1, in a window the clinician labelled frame by frame, the estimator's floor arc moves outward when he says
the floor drops and inward when he says it bumps up, at p = 0.023, with the roof and both orthogonal controls null,
replicating across disjoint halves.** The motion is dipolar with its axis about 40° — four sectors — from the floor
he named. That is the first time in this project that recovered per-frame wall motion has been tied to an external
reference standard.

---

# Third test: a second labelled window — and why it does not test the second

The PI labelled a second window, **0:31.3–0:39.2 (f937–f1175)**, four OUT intervals, 201 IN / 38 OUT, all 239 frames
registered in `runs/g6_c1` — a reconstruction sharing **no frame** with the first window. Labels in
`labels/20V1_f937_f1175_insertion.json`.

**The labels again pass their own consistency check, and strikingly so.** The OUT windows recur every 42–54 frames,
mean **1.60 s = 37.5 per minute** — identical to the first window's 1.60 s / 37.5 per minute, measured from different
marks fifty seconds earlier in the clip. Nothing in the marking enforced that.

## The result, stated first

| arc | separation | p (exact) |
|---|---|---|
| floor | **−0.007 R** | 0.515 |
| roof (control) | −0.049 R | 0.900 |
| side +90 (control) | +0.030 R | 0.038 |
| side −90 (control) | +0.006 R | 0.393 |

**The floor shows nothing.** Taken at face value this is a failed replication, and it is recorded as the headline of
this section for that reason.

## Why it is an uninformative negative rather than a contradiction

The two windows are **different manoeuvres**, which the PI pointed out and the poses confirm independently. Asking
whether the camera moves along its own view axis:

| window | | advancing | manoeuvre | median scope speed |
|---|---|---|---|---|
| f937–1175 | 0:31.3–0:39.2 | 69 % | **insertion** | 0.0405 /frame |
| f2060–2508 | 1:08.7–1:23.7 | 44 % | mixed | 0.0751 /frame |
| f2517–2823 | 1:24.0–1:34.2 | 38 % | **withdrawal** | 0.0261 /frame |

The withdrawal pass is the slowest of the three, and on insertion the floor is barely observed at all. Over the
labelled frames, the fraction of trusted cells in the floor arc against the rest of the ring:

| window | floor arc | rest of ring | ratio |
|---|---|---|---|
| withdrawal (f2517–2823) | 3.2 % | 8.0 % | 0.40 |
| **insertion (f937–1175)** | **1.0 %** | 6.4 % | **0.16** |

**And the test's own noise says it directly.** The floor null has sd **0.032 R** on withdrawal and **0.088 R** on
insertion — 2.8× wider. To reach p ≈ 0.05 on the insertion window an effect would have to be about **0.145 R**. The
effect measured on withdrawal is 0.055 R, which on this window would sit at 0.6 standard deviations: **the insertion
test could not have detected it even if it were there.** That is not a refutation, it is an absence of power, and the
cause is measurable rather than assumed — the scope advancing down the airway images the floor at grazing incidence
and close range, so the floor sectors fail the support gate six times more often than the rest of the ring.

The side +90 control reaches p = 0.038 here, but its beating shifts are lags 1–8 — all near-identity — so it is the
same near-identity artefact rather than a signal, and with the floor null at 0.088 R nothing on this window means much.

## Where this leaves the claim

**The withdrawal result stands as reported (p = 0.023, three null controls, replicating across disjoint halves), and
it still has no independent replication.** The insertion window does not provide one and cannot. What would:

- A second **withdrawal** window, reconstructed separately so it shares no frames with f2517–2823. The clip's
  withdrawal continues past 1:34, so **1:34–1:40 (f2824–f3000)** is the natural candidate, but it must be given its
  own reconstruction — inside `g6_tube` it is the same model and would not be independent.
- Cluster 2 (f2060–2508) is not a candidate: its longest clean pullback is 3.0 s, under two respiratory cycles, at
  2.4× the withdrawal window's scope speed.

**A general rule falls out of this, and it is worth more than the single result:** labelled wall motion is testable
on a *slow pullback* and is not testable on an insertion pass with this estimator, because the floor is not
sufficiently observed while the scope advances. That is a statement about acquisition, which is where this project
has repeatedly found its limits.
