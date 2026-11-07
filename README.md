# Velocity confounding in monocular bronchoscopic stereo — code, labels and pre-registrations

Companion repository for the manuscript *Velocity Confounding in Monocular Bronchoscopic Stereo: Diagnostics for When Respiratory Wall Motion Can Be Read* (IEEE Transactions on Medical Imaging, under review). It contains every analysis script named in the paper, the clinician label files, the synthetic renderer with the per-render seeds and commands, the canonical scorer outputs behind the synthetic tables, and the dated pre-registration documents. It was extracted from the authors' working repository at commit `f990416` (2026-11-07) with a fresh history.

## What is here

| Paper item | File(s) |
|---|---|
| Rigid pipeline (SfM, windowed stereo) | `m1/real_sfm_relaxed.py`, `m1/windowed_depth_real.py` |
| Ring statistic, label handling, circular-shift null | `m2/label_core.py`, `m2/station_frame.py`, `runs/baselines/common.py` |
| Off-phase null (Sec. IV) | `runs/v5/offphase_lib.py` |
| Synthetic renderer with planted truth (Sec. IV-B) | `tests/render_breathing_tube.py`, launchers `tests/mvs_synth_run.sh`, `runs/v3/render_sfm_root.sh`, `runs/r3/queue.sh`, `runs/r4/queue.sh`, `runs/r6/queue.sh`, `runs/r6/build_replay.py` |
| Per-render parameters, seeds, commands, hashes (Supplementary) | `docs/supplement/synthetic_manifest.csv` (`runs/r3/a1_manifest.py`, re-render check `runs/r3/a2_rerender.py`) |
| Validity-check ablation, fixed-seed scorer (Table I) | `tests/ablation_checks.py`, `runs/r3/ablation_table.py`, scorer outputs `runs/r3/rescore/`, `runs/r4/scores/` |
| Run-level synthetic statistics (Supplementary Table S1) | `runs/stats/run_level_canonical.py` → `docs/supplement/run_level_canonical.csv`, `run_level_summary.txt` |
| Label-transplant false-positive test | `tests/transplant_null.py` |
| Cohort table and regeneration table (Tables II, III) | `tests/table_cohort.py` → `docs/figures/paper/table_cohort.json`, `table_regen_extra*.json` |
| Camera-motion confound, label-free clock | `runs/theory/circularity.py` |
| Quadrature fit, camera check, C3VD null, regime index | `runs/r6/item3.py` → `runs/r6/item3.json` |
| Identifiability and clinical-path replays | `runs/r6/identifiability.py`, `runs/r6/item1_score.py`, `runs/r6/item1_regime.py` → `runs/r6/*.json` |
| Depth-free feature-pair test | `tests/pair_feature_amplitude.py` |
| Baselines (optical flow, 2-D segmentation, trajectory-basis NRSfM, CUT3R) | `runs/baselines/d1_raft.py`, `d2_seg.py`, `d3a_trajbasis.py`, `pipeline_row.py`, results `runs/baselines/*.jsonl`, summary `runs/baselines/summarise.py` |
| Figures | `tests/fig_workflow.py`, `fig_stereo_artifact.py`, `fig_sensitivity.py`, `fig_label_shift.py`, `fig_cohort.py`, `fig_ct_correlate_tubefree.py`, `fig_pair_test.py`, `fig_failure_taxonomy.py`, `fig_pipeline_overview.py`; figure data `docs/figures/paper/*.json` |
| Frame extraction used by the pipeline | `tests/extract_production_frames.py`, `tests/extract_span.py` |
| Clinician labels (OUT/IN windows per clip) | `labels/*.json` |
| CT inspiration/expiration sector measurements (20-V1) | `reports/ct_ett_check/tubefree/sectors.json` |
| Scope intrinsics example | `calib/2V1_intrinsics.json` |
| Pre-registration documents | `docs/PREREG_*.md` (dated; written before the corresponding runs) |

## What is not here

- The bronchoscopic videos, CT scans, extracted frames and the reconstructions (`runs/<clip>/...`) are clinical data and are not distributed. Scripts that read a reconstruction expect it at the `runs/` path used in the paper.
- The synthetic renders are not stored; every render is reproducible from `tests/render_breathing_tube.py` with the parameters, seed and commands listed per run in `docs/supplement/synthetic_manifest.csv` (the `dir` column shows the run name under `renders/`). The manifest also carries each render's first-frame hash for verification (`runs/r3/a2_rerender.py`).
- The C3VD and StereoMIS public datasets must be obtained from their own sources.

## Privacy edits made to the released files

Clip identifiers (e.g. `2-V2`, `20-V1`) are internal study codes. In the label files the labeller's name was replaced by `clinician (co-author)`, and the two 2-V1 sessions, previously distinguished by their recording dates in file and video names, are now `session A` and `session B` (`labels/2V1_sessionA_*.json`, `labels/2V1_sessionB_*.json`; the scripts were updated to match). Absolute cluster paths to the datasets were shortened to the clip name. No other content was changed.

## Environment

Python 3.11 with `numpy<2`, `scipy`, `opencv-python`, `matplotlib`, `pycolmap`, and COLMAP 3.x (`BRONCHO_COLMAP=/path/to/colmap`). The RAFT, CoTracker3 and CUT3R baselines need `torch`, `torchvision` and the respective upstream packages. The pipeline's frame decoding and calibration helpers come from the authors' `bronchotrust` repository (`BRONCHOTRUST=/path/to/bronchotrust`). Scripts are run from the repository root.

## Regenerating the paper's numbers

- Synthetic tables: `python runs/r3/ablation_table.py` and `python runs/stats/run_level_canonical.py` read the stored scorer outputs in `runs/r3/rescore/` and `runs/r4/scores/`; `python runs/baselines/summarise.py` reads `runs/baselines/*.jsonl`.
- Clinical tables and figures need the retained reconstructions: `python tests/table_cohort.py`, `python tests/fig_cohort.py`, `python tests/fig_label_shift.py`, `python tests/fig_ct_correlate_tubefree.py`, `python runs/r6/item3.py`.

## License and citation

License: to be set by the authors before public release. Citation: see the manuscript.
