#!/bin/bash
# D2 evaluation: starts only after tuning has written the frozen parameters (held-out/clinical untouched until then)
cd /home/mi3dr/projects/airway-canonical-deform; PY=/home/mi3dr/.conda/envs/depth-eval/bin/python
until grep -q CHOSEN runs/baselines/d2_tune.log; do sleep 30; done
while IFS='|' read -r V L T; do $PY -W ignore runs/baselines/d2_seg.py eval runs/baselines/d2_params.json "$V" "$L" "$T" 2>/dev/null | tail -1 >> runs/baselines/d2_seg.jsonl; done < runs/baselines/jobs.txt
echo D2DONE >> runs/baselines/d2_seg.jsonl
