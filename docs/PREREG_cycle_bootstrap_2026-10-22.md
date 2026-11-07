# Amplitude uncertainty by breathing-cycle bootstrap (2026-10-22) — declared before running
Purpose: a 95 % interval on each clip's floor OUT−IN (reviewer item "provide uncertainty estimates"). Descriptive; nothing is decided by it and
no threshold, window or label changes.
Unit of resampling: the breathing cycle = one clinician OUT window plus the labelled IN frames that follow it up to the next OUT window (frames
before the first OUT window join the first cycle). Resample cycles with replacement (B = 10 000, seed 0), recompute OUT−IN with LC.score on the
paper grid, report the percentile 95 % interval and the number of cycles. Clips and grids exactly as in the circularity run (2-V2 runs/g6_2v2,
20-V1 wd runs/m1_20V1_lab, 18-V1, 26-V2, 31-V1, 17-V1 wd, 2-V1). With 4–7 cycles per clip the interval is coarse and will be stated as such.

## Results (runs/theory/cycle_boot.{py,log,json})
| clip | OUT−IN (R) | cycles | 95 % cycle-bootstrap |
|---|---|---|---|
| 2-V2 | +0.067 | 6 | +0.022 … +0.124 (excludes 0) |
| 20-V1 wd | +0.043 | 6 | −0.018 … +0.109 (includes 0) |
| 18-V1 | +0.064 | 3 | −0.033 … +0.139 (includes 0) |
| 26-V2 | −0.006 | 2 | −0.046 … +0.017 |
| 31-V1 | +0.002 | 5 | −0.024 … +0.036 |
| 17-V1 wd | +0.001 | 3 | −0.021 … +0.014 |
| 2-V1 | +0.011 | 4 | −0.018 … +0.026 |
Consistent with the per-window values: 2-V2 all six windows positive; 20-V1 three strongly positive (+0.12…+0.17) and three slightly negative
(−0.03…−0.04). Only 2-V2's amplitude generalises across its breathing cycles at 95 %; 20-V1 and 18-V1 rest on a subset of cycles.
