#!/bin/bash
cd /home/mi3dr/projects/airway-canonical-deform; PY=/home/mi3dr/.conda/envs/depth-eval/bin/python
while IFS='|' read -r V L T; do $PY -W ignore runs/baselines/d1_raft.py "$V" "$L" "$T" 3 2>/dev/null | tail -1 >> runs/baselines/d1_raft.jsonl; done < runs/baselines/jobs.txt
echo D1DONE >> runs/baselines/d1_raft.jsonl
