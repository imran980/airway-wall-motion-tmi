# Real-optics null on C3VD (2026-10-23) — declared before running
Purpose: the clinical-video false-positive test (label transplants) uses real airways whose walls may move; renders are "too clean". C3VD
is a static silicone colon filmed with a real colonoscope (real optics, lighting, specularity, scope handling) whose walls do NOT move, so
every acceptance is a false positive with certainty.
Data: runs/c3vd_cecum/g5_est_rc (cecum_t1_a, 276 frames, production recipe: SfM poses, sequential sources, recentred; earlier validated
against C3VD ground truth). Further sequences (trans_t2_a, desc_t4_a, sigmoid_t2_a, cecum_t4_b) are added if reconstructed; same analysis.
Labels (no tuning, all placements): (a) each of the 10 clinical windows' label patterns (OUT/IN sequence as frame offsets) placed at every
offset where it fits inside the sequence; (b) periodic labels with periods 30, 45, 52, 65, 79, 134 frames (the cohort's labelled cycles)
at duty 17 % and 80 %, every phase offset (step 1 frame).
Scoring: the unchanged five-condition rule with the primary circular-shift null (labels over every frame registered), via
runs/baselines/common.evaluate on the LC pooled floor/roof/side series; floor = image-down as in the pipeline. Report acceptance per family
with Clopper–Pearson intervals (placements within a family overlap and are correlated, so the intervals are optimistic), and the
significance-only rate. Prediction: rule acceptance ≤ 3.7 % (the upper bound of the clinical transplant rate) in every family.
