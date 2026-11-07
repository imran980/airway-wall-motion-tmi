# PI-indicated motion segments (2026-10-21) — declared before reconstruction
The PI reports visible, repeated breathing-like posterior-wall motion at 2-V2 f620–820 (subtle) and 20-V1 f2220–2420 (more obvious). All earlier
real tests used other windows (2-V2 f2870–3370, 20-V1 f2517–2823). Step 1 (EXPLORATORY — v4 failed its synthetic test on 2/5 motion runs,
amplitude collapse): production SfM (m1/real_sfm_relaxed.py, overlap 30, pinned intrinsics copied from each clip's existing reconstruction) on
f600–840 and f2200–2440; frozen v4 (runs/v4/spec.py decide_v4) unchanged. Reported: T* (breathing period), A*, a_equiv, verdict, and the
recovered waveform w(t) plotted against frames for the PI to compare with what is visible. No labels exist for these segments; nothing is
credited. Step 2 (after the PI labels OUT/IN on these segments): frozen v3.1 (runs/v3/profile31.py decide) on the same reconstructions.

## Step 1 result (exploratory; runs/v4/seg_*.log, figures docs/figures/gate_waveform/pi_segment_*.png)
2-V2 f600–840: one model, 234 frames, 120 floor chains; frozen v4 "detected": T* 78.8 frames (broad peak 64–109), A* 0.017 R (bootstrap 2.5 %
0.014), a_equiv 0.012 R. VISUAL: these frames are the LARYNX (vocal folds, glottis, arytenoids, instruments in view; camera approaching the
glottis), not trachea — the tube model and the radial posterior-wall direction do not apply; the number is not interpretable as tracheal-wall
motion. Asked the PI to confirm the intended frames.
20-V1 f2200–2440: one model, 241 frames, but only 6 of 232 chains on the posterior (image-down) wall → undetermined (< 20). VISUAL: trachea with
the posterior wall bulging close to the lens and overexposed / textureless (white near-field at the bottom of every frame) — the region where the
PI sees the motion yields almost no matchable features. FACT: on the clearest malacia motion the sparse-feature method has no data; a dense /
photometric method would be needed (consistent with the earlier finding that the deformation is visible in pixels but absent from sparse tracks).

## 2-V2 f2250–2570 (PI's alternative, declared before reconstruction; exploratory, same procedure)
Contact strip (docs/figures/gate_waveform/pi_segment_2V2_f2250_2570_frames.png): scope close to one wall, lumen a small off-centre dark opening
(upper-left), large partly overexposed wall in view — the tube model may fit poorly. SfM f2230–2590, frozen v4, waveform + frames figure.
Result: SfM fragmented — largest model f2328–2590 (263 frames); the near-wall, overexposed part f2230–2327 split into small models (47 and 25
frames). Only 17 floor chains in the largest model → undetermined (< 20). Same failure as 20-V1: where the wall is close to the lens and its
motion most visible, sparse features are lost.
