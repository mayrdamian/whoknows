#!/bin/sh
# All Phase 3 runs (DESIGN.md §15), then the tables.
# The 10,000-agent runs need up to 3.2 GB each; on a 7 GB machine run them one
# per process (run_large), not two per process pool.
set -e
python -m whoknows.experiments --scenario p3_gate --seeds 5 --procs 2 --out results
python -m whoknows.run_large --scenario p3_size --variant agents=1000 --seeds 3 --out results_p3/size1k.csv \
    --strategies learned_local,attested_search,hybrid_search_learned,learned_local_loadaware,learned_central,declared_search,declared_search_trust,phonebook,ask_senior
python -m whoknows.run_large --scenario p3_size --variant agents=10000 --seeds 3 --out results_p3/size10k.csv \
    --strategies learned_local,attested_search,hybrid_search_learned,learned_local_loadaware,learned_central,declared_search,declared_search_trust,phonebook,ask_senior
python - <<'PY'
import pandas as pd
runs = pd.read_csv("results/runs.csv")
new = pd.concat([pd.read_csv("results_p3/size1k.csv"), pd.read_csv("results_p3/size10k.csv")], ignore_index=True)
key = ["scenario", "variant", "strategy", "seed"]
old = runs.merge(new[key], on=key, how="left", indicator=True)["_merge"].eq("left_only").values
pd.concat([runs[old], new], ignore_index=True).to_csv("results/runs.csv", index=False)
PY
python -m whoknows.report_v6 --runs results/runs.csv --out results
echo ALL DONE
