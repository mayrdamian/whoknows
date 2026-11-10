"""Tables for the v5 runs (Phase 2: the open network).

    python -m whoknows.report_v5 --runs results/runs.csv --out results

Writes one markdown table per v5 scenario (mean and 95 % interval over seeds),
the gate check of DESIGN.md §14.3, and results/key_numbers_v5.md with every
number the write-ups quote.
"""

from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from .report_v4 import NAMES, ORDER, mean_ci, num, ordered, pct, table



def _mean(df, scenario, variant, strategy, column, scale=1.0) -> float:
    g = df[(df.scenario == scenario) & (df.variant == variant) & (df.strategy == strategy)]
    return float(pd.to_numeric(g[column], errors="coerce").mean()) * scale if len(g) else float("nan")


def gate(runs: pd.DataFrame) -> tuple[str, list[str]]:
    """The gate of DESIGN.md §14.3, check 2: the company with network vectors against v3."""
    rows = ["| strategy | people: v3 | people: network vectors | agents: Phase 1 | agents: network vectors |",
            "|---|---|---|---|---|"]
    diffs, ref, new = [], {"people": [], "agents": []}, {"people": [], "agents": []}
    for s in ORDER:
        cells = [NAMES[s]]
        for variant in ("people", "agents"):
            a = _mean(runs, "speed", variant, s, "correct", 100)
            b = _mean(runs, "gate", variant, s, "correct", 100)
            cells += [f"{a:.0f} %", f"{b:.0f} %"]
            diffs.append(abs(a - b))
            ref[variant].append(a)
            new[variant].append(b)
        rows.append("| " + " | ".join(cells) + " |")
    rho = {v: spearmanr(ref[v], new[v]).statistic for v in ref}
    hub = _mean(runs, "gate", "people", "ask_senior", "top5_share_inbox", 100)
    checks = [
        f"largest difference in the share answered: {max(diffs):.1f} points (pass if at most 6)",
        f"rank correlation with v3: people {rho['people']:.2f}, agents {rho['agents']:.2f} (pass if at least 0.8)",
        f"asking the senior, busiest 5 % get: {hub:.0f} % of messages (pass if more than 50 %)",
    ]
    passed = max(diffs) <= 6 and min(rho.values()) >= 0.8 and hub > 50
    checks.append("**gate passed**" if passed else "**gate NOT passed**")
    return "\n".join(rows), checks


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runs", default="results/runs.csv")
    p.add_argument("--out", default="results")
    a = p.parse_args(argv)
    runs = pd.read_csv(a.runs)
    written = []

    def save(name: str, title: str, text: str) -> None:
        with open(os.path.join(a.out, f"table_v5_{name}.md"), "w") as f:
            f.write(f"**{title}** (mean ± 95 % interval over seeds)\n\n{text}\n")
        written.append(name)

    if len(runs[runs.scenario == "gate"]):
        text, checks = gate(runs)
        save("gate", "Gate: the v3 company described with the open network's topic vectors",
             text + "\n\n" + "\n".join(f"- {c}" for c in checks))

    size = runs[(runs.scenario == "net_size") | ((runs.scenario == "net_speed") & (runs.variant == "agents"))].copy()
    size.loc[size.scenario == "net_speed", "variant"] = "agents=1000"
    if len(size):
        cols = [("correct", lambda g: pct(g.correct)), ("wrong", lambda g: pct(g.wrong)),
                ("busiest 5 % get", lambda g: pct(g.top5_share_inbox)),
                ("busiest 1 % get", lambda g: pct(g.top1_share_inbox)),
                ("reads per question", lambda g: num(g.reads_per_query, 1, 2)),
                ("refusals per question", lambda g: num(g.rejected_per_query, 1, 2)),
                ("slowest 10 % (s)", lambda g: num(g.latency_p90)),
                ("undeclared: correct", lambda g: pct(g.correct_undeclared))]
        save("size", "The open network at 130, 300 and 1,000 agents, agents at 30/h (5 seeds)",
             table(ordered(size), cols, by=("variant", "strategy")))
        cols = [("newcomers", lambda g: pct(g.newcomer_share)),
                ("their questions: correct", lambda g: pct(g.correct_newcomers)),
                ("others' questions: correct", lambda g: pct(g.correct_others)),
                ("found ratio", lambda g: num(g.found_ratio_newcomers, 1, 2)),
                ("asked ratio", lambda g: num(g.asked_ratio_newcomers, 1, 2)),
                ("known by (newcomers)", lambda g: num(g.known_by_newcomers, 1, 0)),
                ("known by (others)", lambda g: num(g.known_by_others, 1, 0))]
        save("newcomers", "Newcomers (joined in the last half year) in the open network (5 seeds)",
             table(ordered(size), cols, by=("variant", "strategy")))

    ap = runs[(runs.scenario == "net_speed") & (runs.variant == "agents+approvals")]
    if len(ap):
        cols = [("correct", lambda g: pct(g.correct)),
                ("approvals per question", lambda g: num(g.approvals_per_query, 1, 3)),
                ("approvals by busiest 5 % of humans", lambda g: pct(g.top5_share_approvals)),
                ("approval wait, typical (s)", lambda g: num(g.approval_wait_median, 1, 0)),
                ("approval wait, slowest 10 % (s)", lambda g: num(g.approval_wait_p90, 1, 0))]
        save("approvals", "Human approvals in the open network, 1,000 agents (5 seeds)",
             table(ordered(ap), cols, by=("strategy",)))

    for scen, title in (("net_priority", "Who sets the priority: 1,000 agents at 60/h (4 seeds)"),
                        ("net_inflation", "60 % of askers inflate: 1,000 agents at 60/h (4 seeds)")):
        pr = runs[runs.scenario == scen]
        if len(pr):
            cols = [("correct", lambda g: pct(g.correct)),
                    ("high: correct", lambda g: pct(g.correct_high)),
                    ("high: typical wait (s)", lambda g: num(g.latency_high_median)),
                    ("low: typical wait (s)", lambda g: num(g.latency_low_median)),
                    ("reads per question", lambda g: num(g.reads_per_query, 1, 2)),
                    ("refusals per question", lambda g: num(g.rejected_per_query, 1, 2)),
                    ("triage reads at busiest 5 %", lambda g: pct(g.top5_share_triage))]
            save(scen.replace("net_", ""), title, table(ordered(pr), cols, by=("strategy", "variant")))

    with open(os.path.join(a.out, "summary_tables_v5.md"), "w") as f:
        f.write(summary_tables(runs))
    key_numbers(runs, os.path.join(a.out, "key_numbers_v5.md"))
    print("wrote", ", ".join(f"table_v5_{n}.md" for n in written), "and key_numbers_v5.md")


def summary_tables(runs: pd.DataFrame) -> str:
    """The compact tables of RESULTS_V5.md (means over seeds)."""
    def m(scenario, variant, strategy, column, scale=100.0):
        return _mean(runs, scenario, variant, strategy, column, scale)

    def size(strategy, column, scale=100.0):
        return [m("net_size", "agents=130", strategy, column, scale), m("net_size", "agents=300", strategy, column, scale),
                m("net_speed", "agents", strategy, column, scale)]

    out = ["### Size", "",
           "| strategy | answered: 130 → 300 → 1,000 agents | busiest 1 % get (1,000) | reads per question (1,000) "
           "| refusals per question (1,000) | undeclared knowledge found (1,000) |", "|---|---|---|---|---|---|"]
    order = sorted(ORDER, key=lambda s: -m("net_speed", "agents", s, "correct"))
    for s in order:
        a = size(s, "correct")
        out.append(f"| {NAMES[s]} | {a[0]:.0f} % → {a[1]:.0f} % → {a[2]:.0f} % "
                   f"| {m('net_speed', 'agents', s, 'top1_share_inbox'):.0f} % "
                   f"| {m('net_speed', 'agents', s, 'reads_per_query', 1):.1f} "
                   f"| {m('net_speed', 'agents', s, 'rejected_per_query', 1):.2f} "
                   f"| {m('net_speed', 'agents', s, 'correct_undeclared'):.0f} % |")
    out += ["", "### Newcomers (1,000 agents)", "",
            "| strategy | newcomers' questions answered | others' questions answered "
            "| asks per item held, newcomers ÷ others |", "|---|---|---|---|"]
    for s in order:
        out.append(f"| {NAMES[s]} | {m('net_speed', 'agents', s, 'correct_newcomers'):.0f} % "
                   f"| {m('net_speed', 'agents', s, 'correct_others'):.0f} % "
                   f"| {m('net_speed', 'agents', s, 'asked_ratio_newcomers', 1):.2f} |")
    out += ["", "### Approvals (1,000 agents)", "",
            "| strategy | approvals given by the busiest 5 % of humans | typical approval wait | slowest 10 % wait |",
            "|---|---|---|---|"]
    for s in order:
        if len(runs[(runs.scenario == "net_speed") & (runs.variant == "agents+approvals") & (runs.strategy == s)]):
            out.append(f"| {NAMES[s]} | {m('net_speed', 'agents+approvals', s, 'top5_share_approvals'):.0f} % "
                       f"| {m('net_speed', 'agents+approvals', s, 'approval_wait_median', 1 / 60):.1f} min "
                       f"| {m('net_speed', 'agents+approvals', s, 'approval_wait_p90', 1 / 60):.0f} min |")
    pr = runs[runs.scenario == "net_priority"]
    if len(pr):
        out += ["", "### Priority (1,000 agents, 60/h)", "",
                "| rule | oldest agent: answered | urgent: typical wait | reads | learned local: answered "
                "| urgent wait | track records: answered | urgent wait | reads |", "|---|---|---|---|---|---|---|---|---|"]
        for rule in ("none", "asker", "budget", "audit", "answerer"):
            v = f"priority={rule}"
            cells = [rule]
            for s, with_reads in (("ask_senior", True), ("learned_local", False), ("attested_search", True)):
                cells += [f"{m('net_priority', v, s, 'correct'):.0f} %",
                          f"{m('net_priority', v, s, 'latency_high_median', 1):.0f} s"]
                if with_reads:
                    cells.append(f"{m('net_priority', v, s, 'reads_per_query', 1):.1f}")
            out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


KEY_COLUMNS = [
    ("correct", 100, " %", 1), ("wrong", 100, " %", 1), ("top5_share_inbox", 100, " %", 1),
    ("top1_share_inbox", 100, " %", 1), ("top5_share_reads", 100, " %", 1), ("reads_per_query", 1, "", 2),
    ("rejected_per_query", 1, "", 2), ("busy_per_query", 1, "", 2), ("latency_median", 1, " s", 1),
    ("latency_p90", 1, " s", 1), ("correct_undeclared", 100, " %", 1),
    ("newcomer_share", 100, " %", 1), ("correct_newcomers", 100, " %", 1), ("correct_others", 100, " %", 1),
    ("found_ratio_newcomers", 1, "", 2), ("asked_ratio_newcomers", 1, "", 2),
    ("known_by_newcomers", 1, "", 1), ("known_by_others", 1, "", 1),
    ("latency_high_median", 1, " s", 1), ("latency_low_median", 1, " s", 1),
    ("top5_share_triage", 100, " %", 1), ("top5_share_approvals", 100, " %", 1),
    ("approval_wait_median", 1, " s", 0), ("approval_wait_p90", 1, " s", 0),
]


def key_numbers(runs: pd.DataFrame, path: str) -> None:
    """Every number the v5 write-ups quote, straight from runs.csv."""
    lines = ["# Key numbers for the v5 write-ups (computed from runs.csv)", ""]
    for scenario in ("gate", "net_size", "net_speed", "net_priority", "net_inflation"):
        sub = runs[runs.scenario == scenario]
        for (variant, strategy), g in sub.groupby(["variant", "strategy"], sort=False):
            lines.append(f"## {scenario} / {variant} / {NAMES.get(strategy, strategy)} ({len(g)} seeds)")
            for column, scale, unit, digits in KEY_COLUMNS:
                if column in g:
                    m, c = mean_ci(g[column])
                    if not np.isnan(m):
                        lines.append(f"- {column}: {m * scale:.{digits}f}{unit} ± {c * scale:.{digits}f}")
            lines.append("")
    with open(path, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
