#!/bin/bash
cd /home/mi3dr/projects/airway-canonical-deform; PY=/home/mi3dr/.conda/envs/depth-eval/bin/python
export LD_LIBRARY_PATH=/home/mi3dr/.conda/envs/colmap-cuda/lib:${LD_LIBRARY_PATH:-}; export BRONCHO_COLMAP=/home/mi3dr/.conda/envs/colmap-cuda/bin/colmap
while IFS='|' read -r M V L T; do $PY -W ignore runs/baselines/d3a_trajbasis.py "$M" "$V" "$L" "$T" 1 2>runs/baselines/d3a_$T.err | tail -1 >> runs/baselines/d3a_traj.jsonl; done < runs/baselines/jobs_d3a.txt
echo D3ADONE >> runs/baselines/d3a_traj.jsonl
