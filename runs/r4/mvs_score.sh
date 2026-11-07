#!/bin/bash
# R-1: production MVS + stations on held-out renders, then the paper's unchanged FULL-rule scorer; K4 phase-gated on motion renders.
export LD_LIBRARY_PATH=/home/mi3dr/.conda/envs/colmap-cuda/lib:${LD_LIBRARY_PATH:-}; export BRONCHO_COLMAP=/home/mi3dr/.conda/envs/colmap-cuda/bin/colmap
cd /home/mi3dr/projects/airway-canonical-deform; PY=/home/mi3dr/.conda/envs/depth-eval/bin/python
for D in "$@"; do
  T=$(basename $D); echo "[$T] $(date +%H:%M) MVS"
  [ -d $D/sfm/images ] || $PY runs/v3/reextract.py $D/video.mp4 $D/sfm 0 299 > /dev/null
  [ -f $D/m1/m1_real_grid.npz ] || $PY m1/windowed_depth_real.py $D/sfm --out $D/m1 --gpus 0,1,2,3 --max-size 1000 --recentre --ahead 0.5,5.0 --frame global --radius-from rings --min-baseline 3 --max-gap 12 > $D/m1.log 2>&1
  rm -rf $D/m1/dense/stereo $D/m1/dense/images
  [ -f $D/m1/m1_real_grid.npz ] && $PY tests/ablation_checks.py $D --out runs/r4/scores/$T.json > runs/r4/scores/$T.log 2>&1 && echo "[$T] $(date +%H:%M) scored" || echo "[$T] FAILED"
  if [[ $T == M* ]]; then
    K=$(dirname $D)/K4_$T; mkdir -p $K; ln -sfn $D/sfm $K/sfm; ln -sfn $D/truth.npz $K/truth.npz
    $PY -c "import json, numpy as np; T=np.load('$D/truth.npz'); json.dump({str(i): float(p) for i, p in enumerate(T['phase_table'])}, open('$K/phase.json','w'))"
    [ -f $K/m1/m1_real_grid.npz ] || $PY m1/windowed_depth_real.py $D/sfm --out $K/m1 --gpus 0,1,2,3 --max-size 1000 --recentre --ahead 0.5,5.0 --frame global --radius-from rings --min-baseline 3 --max-gap 12 --phase-json $K/phase.json > $K/m1.log 2>&1
    rm -rf $K/m1/dense/stereo $K/m1/dense/images
    [ -f $K/m1/m1_real_grid.npz ] && $PY tests/ablation_checks.py $K --out runs/r4/scores/K4_$T.json > runs/r4/scores/K4_$T.log 2>&1 && echo "[K4_$T] $(date +%H:%M) scored" || echo "[K4_$T] FAILED"
  fi
  rm -rf $D/sfm/images
done
