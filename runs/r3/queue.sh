#!/bin/bash
# Round-3 GPU queue (docs/PREREG_r3_list3_2026-10-22.md): B slow-scope arm, then A4 end-to-end regenerations. Sequential (disk).
cd /home/mi3dr/projects/airway-canonical-deform; export OUTROOT=/scratch/mi3dr_r3/synth; PY=/home/mi3dr/.conda/envs/depth-eval/bin/python
export LD_LIBRARY_PATH=/home/mi3dr/.conda/envs/colmap-cuda/lib:${LD_LIBRARY_PATH:-}; export BRONCHO_COLMAP=/home/mi3dr/.conda/envs/colmap-cuda/bin/colmap
JOBS=("M_G1slow_s101 0.07 --seed 101 --speed 0.013" "N_G1slow_s103 0.0 --seed 103 --speed 0.013" "M_G1slow_s102 0.07 --seed 102 --speed 0.013" "N_G1slow_s104 0.0 --seed 104 --speed 0.013"
      "M_G1_s61r3 0.07 --seed 61" "N_G1_s66r3 0.0 --seed 66")
for J in "${JOBS[@]}"; do
  set -- $J; TAG=$1; AMP=$2; shift 2
  bash runs/v3/render_sfm_root.sh 0 $TAG -0.28 15 $AMP 0.18 1.0 "$@"
  bash runs/r3/mvs_score.sh $OUTROOT/$TAG
  $PY runs/v5/offphase.py $OUTROOT/$TAG --out runs/r3/scores/offphase_$TAG.json > runs/r3/scores/offphase_$TAG.log 2>&1
  [ -d $OUTROOT/K4_$TAG ] && $PY runs/v5/offphase.py $OUTROOT/K4_$TAG --out runs/r3/scores/offphase_K4_$TAG.json > runs/r3/scores/offphase_K4_$TAG.log 2>&1
  echo "[$TAG] $(date +%H:%M) ALL DONE; scratch free $(df -h /scratch | tail -1 | awk '{print $4}')"
done
echo "QUEUE DONE"
