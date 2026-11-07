# Second-rater relabelling (item 4) — analysis declared before any rater-2 label exists
Package: relabel_package/to_share (git-ignored; patient frames): ten blinded clips W01–W10 in random order (seed 20261027), local frame
numbers, CSV templates, README with the same OUT definition as rater 1 (posterior/image-down wall lowest = lumen widest). The ID → clip key
(relabel_package/PRIVATE_key.json) stays with the analyst; rater 2 sees no earlier labels and works independently.
Analysis (unchanged rule and code; rater-2 CSV parsed into the label JSON format, OUT = marked frames, IN = all other frames of the span;
rows with −1 = unreadable, excluded from both raters' comparison):
 A1 frame-level agreement OUT/IN: Cohen's κ and percent agreement per window and pooled.
 A2 timing: for each rater-1 OUT window, the nearest rater-2 window centre; median absolute centre offset (frames), and the fraction of
    rater-1 windows matched within ±5 frames; breathing-cycle length per rater (median OUT-centre spacing) and their ratio.
 A3 outcome stability: Table I re-scored with rater-2 labels (tests/table_cohort.py with the label path swapped): T, p, limit, the five
    checks, camera check, cycle interval; does each verdict (supported / exploratory / not detected / null) change?
 A4 image-derived phase: per-frame dark-lumen area (common.lumen_centre component area, 10th percentile) → band-passed phase; phase
    coherence of each rater's OUT windows with the area minima/maxima (Rayleigh test of the area phase at OUT-window centres).
No pass/fail; all reported. If rater 2 marks the 20-V1 insertion window at a different breathing rate from rater 1, that is reported as the
resolution of the 20 vs 40/min question.
