#!/bin/bash
cd /home/mi3dr/projects/airway-canonical-deform; export OUTROOT=/scratch/mi3dr_r3/synth; PY=/home/mi3dr/.conda/envs/depth-eval/bin/python
export LD_LIBRARY_PATH=/home/mi3dr/.conda/envs/colmap-cuda/lib:${LD_LIBRARY_PATH:-}; export BRONCHO_COLMAP=/home/mi3dr/.conda/envs/colmap-cuda/bin/colmap
M="--speed 0.0315 --period 79 --offset-x 0.22"
JOBS=("M_2V2m_s111 0.07 --seed 111 $M" "N_2V2m_s114 0.0 --seed 114 $M" "M_2V2m_s112 0.07 --seed 112 $M" "M_2V2mcb_s113 0.07 --seed 113 --cam-breath 0.2 $M" "N_2V2m_s115 0.0 --seed 115 $M" "N_2V2mcb_s116 0.0 --seed 116 --cam-breath 0.2 $M")
for J in "${JOBS[@]}"; do
  set -- $J; TAG=$1; AMP=$2; shift 2
  bash runs/v3/render_sfm_root.sh 0 $TAG 0 0 $AMP 0.18 1.0 "$@"
  bash runs/r4/mvs_score.sh $OUTROOT/$TAG
  for D in $OUTROOT/$TAG $OUTROOT/K4_$TAG; do [ -d $D/m1 ] || continue; T=$(basename $D)
    $PY -W ignore tests/ablation_checks.py $D --half-width 144 --out runs/r4/scores/hw144_$T.json > runs/r4/scores/hw144_$T.log 2>&1
    $PY runs/v5/offphase.py $D --out runs/r4/scores/offphase_$T.json > runs/r4/scores/offphase_$T.log 2>&1; done
  echo "[$TAG] $(date +%H:%M) ALL DONE; scratch free $(df -h /scratch | tail -1 | awk '{print $4}')"
done
echo "QUEUE DONE"
