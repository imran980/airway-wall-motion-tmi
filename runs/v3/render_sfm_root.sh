#!/bin/bash
# render + production SfM only (no MVS), same flags as tests/mvs_synth_run.sh. Usage: render_sfm.sh GPU TAG OFFSET TILT AMP TEX TEXBLUR [extra render flags]
export LD_LIBRARY_PATH=/home/mi3dr/.conda/envs/colmap-cuda/lib:${LD_LIBRARY_PATH:-}; export BRONCHO_COLMAP=/home/mi3dr/.conda/envs/colmap-cuda/bin/colmap
cd /home/mi3dr/projects/airway-canonical-deform; PY=/home/mi3dr/.conda/envs/depth-eval/bin/python
GPU=$1; TAG=$2; OFF=$3; TILT=$4; AMP=$5; TEX=$6; BLUR=$7; shift 7; D=${OUTROOT:-runs/mvs_synth}/$TAG
echo "[$TAG] $(date +%H:%M) render"; rm -rf $D
$PY tests/render_breathing_tube.py --out $D --amp $AMP --offset $OFF --tilt $TILT --tex $TEX --tex-blur $BLUR "$@" > $D.render.log 2>&1 || { echo "[$TAG] RENDER FAILED"; exit 1; }
echo "[$TAG] $(date +%H:%M) SfM"
$PY m1/real_sfm_relaxed.py --video $D/video.mp4 --calib $D/calib.json --lo 0 --hi 299 --out $D/sfm --overlap 30 --gpu $GPU > $D/sfm.log 2>&1
rm -rf $D/sfm/images $D/images
[ -f $D/sfm/sfm_report.json ] && echo "[$TAG] $(date +%H:%M) DONE $(tr -d ' \n' < $D/sfm/sfm_report.json | grep -o '"models":.*' | head -c 120)" || echo "[$TAG] SfM FAILED"
