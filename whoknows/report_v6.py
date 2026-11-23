"""Tables for the v6 runs (Phase 3: towards 100,000 agents).

    python -m whoknows.report_v6 --runs results/runs.csv --out results

Writes the gate check of DESIGN.md §15.2, the size table (1,000 and 10,000
agents at the same run settings) and results/key_numbers_v6.md with every
number the write-ups quote.
"""

from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from .report_v4 import NAMES, ORDER, mean_ci, num, ordered, pct, table
from .report_v5 import KEY_COLUMNS, _mean

GATE_VARIANT = "agents, v6 options"


def _same_seeds(runs, a, b):
    """Rows of the scenarios (scenario, variant) a and b restricted to the seeds both have."""
    ga = runs[(runs.scenario == a[0]) & (runs.variant == a[1])]
    gb = runs[(runs.scenario == b[0]) & (runs.variant == b[1])]
    seeds = sorted(set(ga.seed) & set(gb.seed))
    return ga[ga.seed.isin(seeds)], gb[gb.seed.isin(seeds)], seeds


def gate(runs: pd.DataFrame) -> tuple[str, list[str], bool]:
    """DESIGN.md §15.2: the v6 options at 1,000 agents against Phase 2 on the same seeds."""
    old, new, seeds = _same_seeds(runs, ("net_speed", "agents"), ("p3_gate", GATE_VARIANT))
    rows = ["| strategy | Phase 2 | v6 options | difference | busiest 1 %: Phase 2 | v6 options |",
            "|---|---|---|---|---|---|"]
    a_all, b_all, diffs = [], [], []
    for s in ORDER:
        a = old[old.strategy == s].correct.mean() * 100
        b = new[new.strategy == s].correct.mean() * 100
        if np.isnan(a) or np.isnan(b):
            continue
        h_a = old[old.strategy == s].top1_share_inbox.mean() * 100
        h_b = new[new.strategy == s].top1_share_inbox.mean() * 100
        rows.append(f"| {NAMES[s]} | {a:.1f} % | {b:.1f} % | {b - a:+.1f} | {h_a:.0f} % | {h_b:.0f} % |")
        a_all.append(a)
        b_all.append(b)
        diffs.append(abs(b - a))
    rho = spearmanr(a_all, b_all).statistic
    hub_a = old[old.strategy == "ask_senior"].top1_share_inbox.mean() * 100
    hub_b = new[new.strategy == "ask_senior"].top1_share_inbox.mean() * 100
    passed = max(diffs) <= 4 and rho >= 0.9 and abs(hub_b - hub_a) <= 5
    checks = [
        f"seeds compared: {', '.join(map(str, seeds))}",
        f"largest difference in the share answered: {max(diffs):.1f} points (pass if at most 4)",
        f"rank correlation of the nine strategies: {rho:.2f} (pass if at least 0.9)",
        f"asking the oldest agent, busiest 1 % get: {hub_a:.0f} % → {hub_b:.0f} % (pass if within 5 points)",
        "**gate passed**" if passed else "**gate NOT passed**",
    ]
    return "\n".join(rows), checks, passed


SIZE_COLUMNS = [
    ("correct", lambda g: pct(g.correct)), ("wrong", lambda g: pct(g.wrong)),
    ("busiest 1 % get", lambda g: pct(g.top1_share_inbox)),
    ("busiest 0.1 % get", lambda g: pct(g.top01_share_inbox)),
    ("reads per question", lambda g: num(g.reads_per_query, 1, 2)),
    ("refusals per question", lambda g: num(g.rejected_per_query, 1, 2)),
    ("undeclared: correct", lambda g: pct(g.correct_undeclared)),
    ("newcomers' questions", lambda g: pct(g.correct_newcomers)),
    ("asks per item, newcomers ÷ others", lambda g: num(g.asked_ratio_newcomers, 1, 2)),
    ("run time (s)", lambda g: num(g.runtime_s, 1, 0)),
]


def summary_tables(runs: pd.DataFrame) -> str:
    """The compact tables of RESULTS_V6.md (means over seeds)."""
    def m(variant, strategy, column, scale=100.0):
        return _mean(runs, "p3_size", variant, strategy, column, scale)

    out = ["### Size (a quarter of an hour of questions, 30 per agent per hour)", "",
           "| strategy | answered: 1,000 → 10,000 agents | 10 busiest agents get: 1,000 → 10,000 "
           "| reads per question | refusals per question | undeclared knowledge found |",
           "|---|---|---|---|---|---|"]
    big = "agents=10000"
    order = sorted([s for s in ORDER if not np.isnan(m(big, s, "correct"))], key=lambda s: -m(big, s, "correct"))
    for s in order:
        out.append(f"| {NAMES[s]} | {m('agents=1000', s, 'correct'):.0f} % → {m(big, s, 'correct'):.0f} % "
                   f"| {m('agents=1000', s, 'top1_share_inbox'):.0f} % → {m(big, s, 'top01_share_inbox'):.0f} % "
                   f"| {m('agents=1000', s, 'reads_per_query', 1):.1f} → {m(big, s, 'reads_per_query', 1):.1f} "
                   f"| {m('agents=1000', s, 'rejected_per_query', 1):.2f} → {m(big, s, 'rejected_per_query', 1):.2f} "
                   f"| {m('agents=1000', s, 'correct_undeclared'):.0f} % → {m(big, s, 'correct_undeclared'):.0f} % |")
    return "\n".join(out) + "\n"


def key_numbers(runs: pd.DataFrame, path: str) -> None:
    """Every number the v6 write-ups quote, straight from runs.csv."""
    lines = ["# Key numbers for the v6 write-ups (computed from runs.csv)", ""]
    columns = KEY_COLUMNS + [("top01_share_inbox", 100, " %", 1), ("runtime_s", 1, " s", 0)]
    for scenario in ("p3_gate", "p3_size"):
        sub = runs[runs.scenario == scenario]
        for (variant, strategy), g in sub.groupby(["variant", "strategy"], sort=False):
            lines.append(f"## {scenario} / {variant} / {NAMES.get(strategy, strategy)} ({len(g)} seeds)")
            for column, scale, unit, digits in columns:
                if column in g:
                    mm, c = mean_ci(g[column])
                    if not np.isnan(mm):
                        lines.append(f"- {column}: {mm * scale:.{digits}f}{unit} ± {c * scale:.{digits}f}")
            lines.append("")
    with open(path, "w") as f:
        f.write("\n".join(lines))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runs", default="results/runs.csv")
    p.add_argument("--out", default="results")
    a = p.parse_args(argv)
    runs = pd.read_csv(a.runs)
    written = []

    def save(name: str, title: str, text: str) -> None:
        with open(os.path.join(a.out, f"table_v6_{name}.md"), "w") as f:
            f.write(f"**{title}**\n\n{text}\n")
        written.append(name)

    if len(runs[runs.scenario == "p3_gate"]):
        text, checks, _ = gate(runs)
        save("gate", "Gate: 1,000 agents with every large-network option, against Phase 2 (same seeds)",
             text + "\n\n" + "\n".join(f"- {c}" for c in checks))
    size = runs[runs.scenario == "p3_size"]
    if len(size):
        save("size", "1,000 and 10,000 agents at the same run settings (mean ± 95 % interval over seeds)",
             table(ordered(size), SIZE_COLUMNS, by=("variant", "strategy")))
        with open(os.path.join(a.out, "summary_tables_v6.md"), "w") as f:
            f.write(summary_tables(runs))
    key_numbers(runs, os.path.join(a.out, "key_numbers_v6.md"))
    print("wrote", ", ".join(f"table_v6_{n}.md" for n in written), "and key_numbers_v6.md")


if __name__ == "__main__":
    main()
