#!/bin/bash
# re-score one grid with the fixed scorer under both nulls
cd /home/mi3dr/projects/airway-canonical-deform; PY=/home/mi3dr/.conda/envs/depth-eval/bin/python
export LD_LIBRARY_PATH=/home/mi3dr/.conda/envs/colmap-cuda/lib:${LD_LIBRARY_PATH:-}; export BRONCHO_COLMAP=/home/mi3dr/.conda/envs/colmap-cuda/bin/colmap
D=$1; T=$(basename $D); P=$(echo $D | sed 's|/|_|g; s|^_||')
$PY -W ignore tests/ablation_checks.py $D --out runs/r3/rescore/orig/$T.json > runs/r3/rescore/orig/$T.log 2>&1 || echo "$T orig FAILED"
$PY -W ignore runs/v5/offphase.py $D --out runs/r3/rescore/off/$T.json > runs/r3/rescore/off/$T.log 2>&1 || echo "$T off FAILED"
echo "$T done"
