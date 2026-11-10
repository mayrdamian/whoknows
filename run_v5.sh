#!/bin/sh
# All Phase 2 runs (DESIGN.md §14.5), one scenario after another, then the tables.
set -e
python -m whoknows.experiments --scenario gate --seeds 10 --procs 2 --out results
python -m whoknows.experiments --scenario net_size,net_speed --seeds 5 --procs 2 --out results
python -m whoknows.experiments --scenario net_priority,net_inflation --seeds 4 --procs 2 --out results
python -m whoknows.report_v5 --runs results/runs.csv --out results
echo ALL DONE
