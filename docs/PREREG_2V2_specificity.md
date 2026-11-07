# Pre-registration: is the wall-motion result specific to the malacic airway?

Written **before any 2-V2 label exists.** The point of writing it now is that the power calculation below is made
without the data, so a null result will mean something.

## The question

20-V1 is **confirmed moderate tracheobronchomalacia** (clinician, clinical). On its withdrawal window the estimator's
floor arc moves outward when the clinician says the floor drops: **+0.055 R, p = 0.023**, three null controls,
replicating across disjoint halves.

That result is worth nothing clinically if the same test fires on a normal airway. **2-V2 is clinically normal** —
it is the cohort's control case, and the PI describes it as breathing with only very slow internal movement. So:

> **Does the floor test separate a malacic airway from a normal one, or does it fire on any breathing airway?**

## Why a null on 2-V2 would be informative rather than merely underpowered

This is the failure that wasted the 20-V1 insertion window, so it is settled first. Using `m2/testability.py`, which
computes the test's sensitivity from the shift null **with no labels at all**:

| | manoeuvre | registered frames | floor support vs ring | detection limit |
|---|---|---|---|---|
| 20-V1 withdrawal (malacic) | withdrawal, 38 % advancing | 307 (10.2 s) | 3.2 % / 8.0 % = **0.40** | 0.045 R |
| **2-V2 f2870–3370 (normal)** | withdrawal, 32 % advancing | **501 (16.7 s)** | 2.6 % / 2.6 % = **0.99** | **0.052 R** |
| 20-V1 insertion (rejected) | insertion, 69 % advancing | 239 | 1.0 % / 6.4 % = 0.16 | 0.143 R |

**2-V2's detection limit is 0.052 R, just below the 0.055 R effect measured on 20-V1.** So if the normal airway moved
as much as the malacic one, this window could see it. Its floor is also observed *more evenly* than 20-V1's — support
in the floor arc equals support over the rest of the ring (ratio 0.99 against 0.40) — and it runs 16.7 s, about ten
respiratory cycles against 20-V1's six.

## Fixed in advance

1. **Labels.** The PI marks only the OUT (floor drops / lumen opens) windows in milliseconds on
   `docs/marking/2V2_frame_numbered.mp4`, which carries the frame number and millisecond burned into every frame;
   every other frame in the span is IN. Identical convention to 20-V1.
2. **Window.** f2870–f3370, the registered span of `runs/g6_2v2`. No other stretch will be substituted after seeing
   a result.
3. **Analysis.** Unchanged and already written: `m2/label_test_combine.py` on `runs/g6_2v2`. The arc is fixed by
   camera geometry, never fitted; the null is every distinct circular shift; the roof and both ±90° arcs must stay
   null. One test, at the floor, one-tailed.
4. **The comparison is the separation, not the p.** p depends on the number of labels, which will differ between the
   two clips. The quantity compared is the floor separation in R.

## The predictions, and what each outcome means

**Predicted:** 2-V2's floor separation is **smaller than 20-V1's +0.055 R** and does not reach p < 0.05.

| outcome | reading |
|---|---|
| 2-V2 separation < ~0.03 R, not significant | **The result is specific.** The test distinguishes a malacic from a normal airway, and 20-V1's motion is not what any breathing airway produces. This is the outcome the project needs. |
| 2-V2 separation ≈ 0.055 R, significant | **The result is NOT specific** and the 20-V1 finding is a measurement of breathing, not of malacia. The claim would have to be withdrawn as a clinical one, and I will say so plainly. |
| 2-V2 separation intermediate (0.03–0.05 R) | Graded rather than binary — consistent with malacia being excess motion rather than a different phenomenon, but it would then need a cohort and a threshold, not two clips. |
| Controls NOT null on 2-V2 | The test is misbehaving on this clip; both results are suspect and the cause must be found before either is used. |

**Pre-registered honesty clause.** The 2-V2 window is longer and its floor better observed than 20-V1's, so it is the
*more* favourable clip for detecting motion. A null there is therefore the stronger evidence for specificity, and a
positive there is the stronger evidence against the clinical claim. That asymmetry is stated now, not after.

---

# RESULT: the prediction failed, and the clinical claim is withdrawn

The PI marked 2-V2 on 2026-09-28, reporting that the airway looks almost static and that only the floor "beats a
little". He marked the **inward** phase (floor bumps up / airway closes) — the opposite convention to 20-V1, where he
marked the floor dropping — so those windows are IN and the rest of the span is OUT. Five windows, 101 IN / 400 OUT,
all frames registered. Labels in `labels/2V2_f2870_f3370.json`.

The windows recur at 2.27, 2.14, 5.07 and 2.54 s. The 5.07 s gap is about two cycles, so one faint beat was probably
missed — consistent with his description.

| arc | separation | p (exact) |
|---|---|---|
| **floor** | **+0.066 R** | **0.046** |
| roof (control) | −0.010 R | 0.808 |
| side +90 (control) | −0.022 R | 0.980 |
| side −90 (control) | −0.001 R | 0.581 |

**The floor clears 0.05 and all three controls are null.** The arc scan is a clean dipole, positive from about −60°
through the floor to +40°, negative opposite — the same shape as 20-V1.

## What this does to the claim

The pre-registration named this outcome and named its consequence:

> *2-V2 separation ≈ 0.055 R, significant → **The result is NOT specific** and the 20-V1 finding is a measurement of
> breathing, not of malacia. The claim would have to be withdrawn as a clinical one, and I will say so plainly.*

| | separation | p | R | in mm |
|---|---|---|---|---|
| 20-V1, **confirmed malacic** | +0.055 R | 0.023 | 3.98 mm | **0.22 mm** |
| 2-V2, **clinically normal** | **+0.066 R** | 0.046 | ~6.6 mm | **0.44 mm** |

**The normal airway shows the larger wall excursion, in R and in millimetres.** So:

**The method does not distinguish a malacic airway from a normal one, and the 20-V1 result is withdrawn as a clinical
finding.** It remains a valid measurement of *respiratory wall motion* — the controls are null in both clips, the
dipole has the same shape and sits at the clinician's floor in both, and the false-positive rate is 1–3 % on two
no-motion datasets. What it measures is breathing, which every airway does.

## What survives, stated exactly

- **The instrument works.** It detects floor wall motion that a clinician independently marked, on two clips, with
  null controls, a measured false-positive rate and a calibrated amplitude.
- **It is not a diagnostic.** Nothing here separates disease from health, and the one experiment designed to test
  that says it does not.
- **Why this was worth doing.** Without 2-V2 the 20-V1 result would have been written up as detecting malacia. It
  detects breathing. The pre-registration is what made that visible rather than arguable.

## What would make it diagnostic

Amplitude during quiet breathing is evidently not the discriminator. Tracheomalacia is defined by **excessive
collapse on forced expiration or cough**, which is a different manoeuvre, not a bigger version of the same one — and
20-V1's own CT says so: 78 % lumen loss between inspiration and expiration against the 0.22 mm we measured while it

## Audit note (2026-09-29): the millimetre figures are not equally grounded

The result above was stated as "20-V1 0.22 mm vs 2-V2 0.44 mm". Those two numbers do not have the same provenance:

| | radius used | where it came from |
|---|---|---|
| 20-V1 | 3.98 mm | **its own paired CT** (inspiratory median tracheal D_CE 7.95 mm) |
| 2-V2 | ~6.6 mm | a 13.2 mm tracheal calibre taken from the separate bronchotrust CT-registration analysis |

Scene units are gauge-free per reconstruction, so that analysis's mm-per-unit scale cannot be transferred to this
one; what was transferred is an *anatomical* calibre measured on a different reconstruction of the same patient.
That is a defensible estimate for a tracheal segment, but it is weaker than 20-V1's, and presenting both to two
decimal places implied a parity that does not exist.

**The falsification does not depend on it.** The pre-registered comparison is the separation in units of each clip's
own radius — **+0.066 R (normal) against +0.055 R (malacic)** — which is scale-free and unchanged. Only the
millimetre restatement is affected, and it should be quoted as "2-V2's excursion is larger in R, and also larger in
mm if its trachea is indeed the wider of the two, which is likely but is not measured here."

---

# Refinement (2026-10-04): image-domain corroboration, and "more" becomes "the same"

Both clips were re-measured directly in the video — peak-to-trough wall motion between the clinician's phase
centres with scope motion compensated per frame, nothing from the reconstruction used — with positive controls
(injected bumps recovered 92–105 %) and a negative control (same-phase pairs, ratio 0.03 on 20-V1, 0.08 on 2-V2).
Full detail in `RESEARCH_calibration.md` §19–25.

**Direction corroborated.** Both clips move at the floor, in the correct sign on every pair (8/8 and 9/9), with
roof and sides quiet. The normal airway's floor moves at least as much as the malacic one in the raw pixels.

**The pipeline's floor arc was differentially off-centre.** Mapping its own arc-scan peak to image angle: on 2-V2
the fixed arc catches 95 % of the peak; on 20-V1, 79 %. Peak-centred, the two clips read **0.0699 vs 0.0702 R —
equal.** The result above, "+0.066 vs +0.055", therefore refines to **"the same"**: the normal airway and the
confirmed malacic airway show equal quiet-breathing wall motion. The conclusion is unchanged and if anything
cleaner — tidal amplitude carries no diagnostic information here — and the 1.20 is now understood as partly an
arc-placement artefact rather than a physiological difference.

**One open item.** In pixels the normal airway's floor moves ~3.9× the malacic one's, where the pipeline's
equal-motion result, converted through each camera and floor depth, predicts ~1.5×. A positive control on 2-V2 is
running to test whether the image-domain method inflates on that clip (its baseline is noisier). This affects the
*magnitude ratio only*; the direction, and the falsification, do not depend on it.
