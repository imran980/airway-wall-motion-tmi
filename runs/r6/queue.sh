#!/bin/bash
# Item 1: renders replaying the clinical camera paths and the clinician's breathing timing (docs/PREREG_r6_reviewer_items_2026-10-27.md)
cd /home/mi3dr/projects/airway-canonical-deform; OUT=/var/tmp/mi3dr_r6/synth; mkdir -p $OUT; PY=/home/mi3dr/.conda/envs/depth-eval/bin/python
export LD_LIBRARY_PATH=/home/mi3dr/.conda/envs/colmap-cuda/lib:${LD_LIBRARY_PATH:-}; export BRONCHO_COLMAP=/home/mi3dr/.conda/envs/colmap-cuda/bin/colmap
JOBS=("M_rep2V2_s131 2V2 0.07" "N_rep2V2_s133 2V2 0.0" "M_rep20V1_s135 20V1 0.07" "N_rep20V1_s137 20V1 0.0" "M_rep2V2_s132 2V2 0.07" "M_rep20V1_s136 20V1 0.07" "N_rep2V2_s134 2V2 0.0" "N_rep20V1_s138 20V1 0.0")
for J in "${JOBS[@]}"; do
  set -- $J; TAG=$1; CL=$2; AMP=$3; D=$OUT/$TAG; SEED=${TAG##*_s}; rm -rf $D
  echo "[$TAG] $(date +%H:%M) render"
  $PY tests/render_breathing_tube.py --out $D --amp $AMP --tex 0.18 --tex-blur 1.0 --seed $SEED --replay /var/tmp/mi3dr_r6/${CL}_replay.npz > $D.render.log 2>&1 || { echo "[$TAG] RENDER FAILED"; continue; }
  cp /var/tmp/mi3dr_r6/${CL}_labels_clinician.json $D/labels_clinician.json
  N=$($PY -c "import numpy as np; print(len(np.load('/var/tmp/mi3dr_r6/${CL}_replay.npz')['C']))"); HI=$((N-1))
  echo "[$TAG] $(date +%H:%M) SfM ($N frames)"
  $PY m1/real_sfm_relaxed.py --video $D/video.mp4 --calib $D/calib.json --lo 0 --hi $HI --out $D/sfm --overlap 30 --gpu 0 > $D/sfm.log 2>&1
  rm -rf $D/images
  $PY m1/windowed_depth_real.py $D/sfm --out $D/m1 --gpus 0,1,2,3 --max-size 1000 --recentre --ahead 0.5,5.0 --frame global --radius-from rings --min-baseline 3 --max-gap 12 > $D/m1.log 2>&1
  rm -rf $D/m1/dense/stereo $D/m1/dense/images $D/sfm/images
  echo "[$TAG] $(date +%H:%M) ALL DONE $( [ -f $D/m1/m1_real_grid.npz ] && echo grid-ok || echo NO-GRID ) $(tr -d ' \n' < $D/sfm/sfm_report.json 2>/dev/null | grep -o '"models":.*' | head -c 90)"
done
echo "QUEUE DONE"
