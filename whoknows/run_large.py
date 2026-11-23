"""Runs the large-network scenarios one run at a time (v6, Phase 3).

    python -m whoknows.run_large --scenario p3_size --variant agents=10000 \
        --strategies declared_search,phonebook --seeds 3 --out results_p3/a.csv

The usual runner (experiments.py) saves a scenario variant when all its runs
are done and runs several at once. A 10,000-agent run needs up to 3 GB, so
here each run is appended to its CSV as soon as it ends (an interrupted
sweep loses one run), runs already in the CSV are skipped, and a run starts
only when enough memory is free. Each run gets a fresh process, so that its
memory is given back when it ends.
"""

from __future__ import annotations

import argparse
import os
import time
from multiprocessing import get_context

import pandas as pd

from .experiments import _one, scenarios


def available_mb() -> float:
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable"):
                return int(line.split()[1]) / 1024
    return float("inf")


def append_row(path: str, row: dict) -> None:
    """Append one run; if it has columns the file lacks (learned strategies add
    two), rewrite the file with all columns."""
    new = pd.DataFrame([row])
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        new.to_csv(path, index=False)
        return
    columns = list(pd.read_csv(path, nrows=0).columns)
    if list(new.columns) == columns:
        new.to_csv(path, mode="a", header=False, index=False)
    else:
        pd.concat([pd.read_csv(path), new], ignore_index=True).to_csv(path, index=False)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scenario", required=True)
    p.add_argument("--variant", required=True)
    p.add_argument("--strategies", required=True)
    p.add_argument("--seeds", type=int, default=3)
    p.add_argument("--only-seeds", default=None, help="comma list: run only these seeds (to split work)")
    p.add_argument("--out", required=True)
    p.add_argument("--need-mb", type=float, default=3500, help="free memory needed before a run starts")
    a = p.parse_args(argv)
    (ccfg, scfg, adv), = [(c, s, d) for v, c, s, d in scenarios()[a.scenario] if v == a.variant]
    done = set()
    if os.path.exists(a.out):
        old = pd.read_csv(a.out, usecols=["strategy", "seed"])
        done = set(zip(old.strategy, old.seed))
    seeds = [int(x) for x in a.only_seeds.split(",")] if a.only_seeds else range(a.seeds)
    for seed in seeds:
        for strategy in a.strategies.split(","):
            if (strategy, seed) in done:
                continue
            while available_mb() < a.need_mb:
                time.sleep(20)
            with get_context("fork").Pool(1, maxtasksperchild=1) as pool:
                row = pool.apply(_one, ((a.scenario, a.variant, ccfg, scfg, adv, strategy, seed),))
            append_row(a.out, row)
            print(f"{a.variant} / {strategy} / seed {seed}: {row['runtime_s']:.0f} s, "
                  f"answered {row['correct']:.3f}", flush=True)


if __name__ == "__main__":
    main()
