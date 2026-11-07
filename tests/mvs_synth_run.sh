#!/bin/bash
# MVS-in-the-loop synthetic: render -> production SfM -> production MVS+stations -> recovered vs true separation.
# Usage: mvs_synth_run.sh TAG OFFSET TILT AMP TEX TEXBLUR
export LD_LIBRARY_PATH=/home/mi3dr/.conda/envs/colmap-cuda/lib:${LD_LIBRARY_PATH:-}; export BRONCHO_COLMAP=/home/mi3dr/.conda/envs/colmap-cuda/bin/colmap
cd /home/mi3dr/projects/airway-canonical-deform; PY=/home/mi3dr/.conda/envs/depth-eval/bin/python
TAG=$1; OFF=$2; TILT=$3; AMP=$4; TEX=$5; BLUR=$6
D=runs/mvs_synth/$TAG; QF="$(dirname "$0")/qfree.sh"
say(){ echo "[$TAG] $(date +%H:%M:%S) $*"; }
say "render  offset $OFF R, tilt $TILT, amp $AMP, tex $TEX/$BLUR"
rm -rf $D; shift 6; $PY tests/render_breathing_tube.py --out $D --amp $AMP --offset $OFF --tilt $TILT --tex $TEX --tex-blur $BLUR "$@" > $D.render.log 2>&1 || { say "RENDER FAILED"; tail -3 $D.render.log; exit 1; }
say "SfM (production script, overlap 30)"
$PY m1/real_sfm_relaxed.py --video $D/video.mp4 --calib $D/calib.json --lo 0 --hi 299 --out $D/sfm --overlap 30 --gpu 0 > $D/sfm.log 2>&1
[ -f $D/sfm/sfm_report.json ] || { say "SfM FAILED"; tail -4 $D/sfm.log | strings | tail -3; exit 1; }
say "SfM: $(tr -d ' \n' < $D/sfm/sfm_report.json | grep -o '"models":.*' | head -c 160)"
G=$($QF); say "quota free $G G"; [ "$G" -lt 5 ] && { say "ABORT: need 5 G"; exit 1; }
say "MVS + stations (production flags)"
$PY m1/windowed_depth_real.py $D/sfm --out $D/m1 --gpus 0,1,2,3 --max-size 1000 --recentre --ahead 0.5,5.0 \
    --frame global --radius-from rings --min-baseline 3 --max-gap 12 > $D/m1.log 2>&1
[ -f $D/m1/m1_real_grid.npz ] || { say "MVS/stations FAILED"; tail -4 $D/m1.log | strings | tail -3; exit 1; }
grep -aE "per-sector support|path monotonicity|tube radius from" $D/m1.log | sed "s/^/[$TAG]   /"
rm -rf $D/m1/dense/stereo $D/m1/dense/images $D/sfm/images $D/images      # keep sparse + mp4 + grid
say "recovered vs true"
$PY tests/mvs_synth_truth.py --grid $D/m1 --truth $D/truth.npz --labels $D/labels.json --json $D/result.json --label $TAG 2>&1 | grep -viE "warning|errstate"
say "DONE  (quota free $($QF) G)"
