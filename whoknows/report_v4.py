"""Tables for the v4 runs (agents and priorities).

    python -m whoknows.report_v4 --runs results/runs.csv --out results

Writes one markdown table per v4 scenario: mean and 95 % interval over seeds.
Times are converted to a readable unit: hours for people, seconds for agents.
"""

from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd
from scipy.stats import t as t_dist

NAMES = {
    "learned_local": "Learned, local", "attested_search": "Signed track records",
    "hybrid_search_learned": "Search + learned (hybrid)", "learned_local_loadaware": "Learned, local, load-aware",
    "learned_central": "Learned, central log", "declared_search": "Declared search",
    "declared_search_trust": "Declared search, trust-ranked", "phonebook": "Phonebook",
    "ask_senior": "Ask the senior / oldest agent",
}
ORDER = list(NAMES)


def mean_ci(x) -> tuple[float, float]:
    x = pd.to_numeric(x, errors="coerce").dropna()
    if len(x) < 2:
        return (float(x.mean()) if len(x) else float("nan")), 0.0
    return float(x.mean()), float(t_dist.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x)))


def pct(x) -> str:
    m, c = mean_ci(x)
    return "–" if np.isnan(m) else f"{100 * m:.0f} % ± {100 * c:.0f}"


def num(x, scale=1.0, digits=1) -> str:
    m, c = mean_ci(x)
    return "–" if np.isnan(m) else f"{m * scale:.{digits}f} ± {c * scale:.{digits}f}"


def table(df: pd.DataFrame, columns: list[tuple[str, callable]], by=("variant", "strategy")) -> str:
    head = "| " + " | ".join(list(by) + [c for c, _ in columns]) + " |"
    rule = "|" + "---|" * (len(by) + len(columns))
    rows = [head, rule]
    for keys, g in df.groupby(list(by), sort=False):
        keys = keys if isinstance(keys, tuple) else (keys,)
        label = [NAMES.get(k, k) for k in keys]
        rows.append("| " + " | ".join(label + [f(g) for _, f in columns]) + " |")
    return "\n".join(rows)


def ordered(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["_o"] = df.strategy.map({s: i for i, s in enumerate(ORDER)})
    return df.sort_values(["_o"], kind="stable").drop(columns="_o")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runs", default="results/runs.csv")
    p.add_argument("--out", default="results")
    a = p.parse_args(argv)
    runs = pd.read_csv(a.runs)
    out = []

    def save(name: str, title: str, text: str) -> None:
        body = f"**{title}** (mean ± 95 % interval over seeds)\n\n{text}\n"
        with open(os.path.join(a.out, f"table_v4_{name}.md"), "w") as f:
            f.write(body)
        out.append(name)

    sp = runs[runs.scenario == "speed"]
    if len(sp):
        parts = []
        for variant, g in sp.groupby("variant", sort=False):
            scale, unit = (1 / 6, "h") if variant == "people" else (1.0, "s")
            cols = [
                ("correct", lambda g: pct(g.correct)), ("wrong", lambda g: pct(g.wrong)),
                (f"typical wait ({unit})", lambda g, s=scale: num(g.latency_median, s)),
                (f"slowest 10 % ({unit})", lambda g, s=scale: num(g.latency_p90, s)),
                ("busiest 5 % get", lambda g: pct(g.top5_share_inbox)),
                ("reads per question", lambda g: num(g.reads_per_query, 1, 2)),
                ("busiest 5 % read", lambda g: pct(g.top5_share_reads)),
                ("refusals per question", lambda g: num(g.rejected_per_query, 1, 2)),
                ("approval wait, slowest 10 % (s)", lambda g: num(g.approval_wait_p90, 1, 0)),
            ]
            parts.append(f"*{variant}*\n\n" + table(ordered(g), cols, by=("strategy",)))
        save("speed", "People vs agents vs agents with human approvals (20 seeds)", "\n\n".join(parts))

    al = runs[runs.scenario == "agent_load"]
    if len(al):
        cols = [("correct", lambda g: pct(g.correct)), ("wrong", lambda g: pct(g.wrong)),
                ("slowest 10 % (s)", lambda g: num(g.latency_p90)),
                ("busiest 5 % get", lambda g: pct(g.top5_share_inbox)),
                ("refusals per question", lambda g: num(g.rejected_per_query, 1, 2)),
                ("reads per question", lambda g: num(g.reads_per_query, 1, 2))]
        save("agent_load", "Agents at 15, 60 and 120 questions per agent per hour (10 seeds; 30/h is in table_v4_speed)",
             table(ordered(al), cols))

    for scen, unit, scale in (("priority_people", "h", 1 / 6), ("priority_agents", "s", 1.0)):
        pr = runs[runs.scenario == scen]
        if len(pr):
            cols = [("correct", lambda g: pct(g.correct)),
                    ("high: correct", lambda g: pct(g.correct_high)),
                    ("low: correct", lambda g: pct(g.correct_low)),
                    (f"high: typical wait ({unit})", lambda g, s=scale: num(g.latency_high_median, s)),
                    (f"low: typical wait ({unit})", lambda g, s=scale: num(g.latency_low_median, s)),
                    ("reads per question", lambda g: num(g.reads_per_query, 1, 2)),
                    ("triage reads at busiest 5 %", lambda g: pct(g.top5_share_triage))]
            save(scen, f"Who sets the priority: {scen.split('_')[1]} (10 seeds)",
                 table(ordered(pr), cols, by=("strategy", "variant")))

    for scen, title in (("inflation", "Asker-set priority as more askers inflate (agents, 60/h, 10 seeds)"),
                        ("triage_cost", "Answerer-set priority by cost of a triage read (agents, 60/h, 10 seeds)")):
        sc = runs[runs.scenario == scen]
        if len(sc):
            cols = [("correct", lambda g: pct(g.correct)),
                    ("high: correct", lambda g: pct(g.correct_high)),
                    ("high: typical wait (s)", lambda g: num(g.latency_high_median)),
                    ("low: typical wait (s)", lambda g: num(g.latency_low_median)),
                    ("refusals per question", lambda g: num(g.rejected_per_query, 1, 2)),
                    ("reads per question", lambda g: num(g.reads_per_query, 1, 2))]
            save(scen, title, table(ordered(sc), cols, by=("strategy", "variant")))

    key_numbers(runs, os.path.join(a.out, "key_numbers_v4.md"))
    print("wrote", ", ".join(f"table_v4_{n}.md" for n in out), "and key_numbers_v4.md")


def key_numbers(runs: pd.DataFrame, path: str) -> None:
    """Every number the v4 write-ups quote, computed straight from runs.csv,
    so the text can be checked against the runs line by line."""
    lines = ["# Key numbers for the v4 write-ups (computed from runs.csv)", ""]

    def mean(scenario, variant, strategy, column, scale=1.0):
        g = runs[(runs.scenario == scenario) & (runs.variant == variant) & (runs.strategy == strategy)]
        return float(pd.to_numeric(g[column], errors="coerce").mean()) * scale if len(g) else float("nan")

    def line(text, value, unit="", digits=1):
        lines.append(f"- {text}: {value:.{digits}f}{unit}")

    for strategy in ORDER:
        name = NAMES[strategy]
        for variant in ("people", "agents", "agents+approvals"):
            if not len(runs[(runs.scenario == "speed") & (runs.variant == variant) & (runs.strategy == strategy)]):
                continue
            lines.append(f"## speed / {variant} / {name}")
            line("correct", mean("speed", variant, strategy, "correct", 100), " %")
            line("wrong", mean("speed", variant, strategy, "wrong", 100), " %")
            line("busiest 5 % get (inbox)", mean("speed", variant, strategy, "top5_share_inbox", 100), " %")
            line("busiest 5 % readers do (reads)", mean("speed", variant, strategy, "top5_share_reads", 100), " %")
            line("reads per question", mean("speed", variant, strategy, "reads_per_query"), "", 2)
            line("refusals per question", mean("speed", variant, strategy, "rejected_per_query"), "", 2)
            line("approvals by busiest 5 % of humans", mean("speed", variant, strategy, "top5_share_approvals", 100), " %")
            line("approval wait, slowest 10 % (min)", mean("speed", variant, strategy, "approval_wait_p90", 1 / 60), " min")
            lines.append("")
    for scenario in ("agent_load", "priority_agents", "priority_people", "inflation", "triage_cost"):
        sub = runs[runs.scenario == scenario]
        for (variant, strategy), g in sub.groupby(["variant", "strategy"], sort=False):
            lines.append(f"## {scenario} / {variant} / {NAMES.get(strategy, strategy)}")
            scale = 1 / 6 if scenario == "priority_people" else 1.0
            unit = " h" if scenario == "priority_people" else " s"
            line("correct", mean(scenario, variant, strategy, "correct", 100), " %")
            line("urgent: typical wait", mean(scenario, variant, strategy, "latency_high_median", scale), unit)
            line("low: typical wait", mean(scenario, variant, strategy, "latency_low_median", scale), unit)
            line("reads per question", mean(scenario, variant, strategy, "reads_per_query"), "", 2)
            line("refusals per question", mean(scenario, variant, strategy, "rejected_per_query"), "", 2)
            line("triage reads by the 5 % who triage most", mean(scenario, variant, strategy, "top5_share_triage", 100), " %")
            line("slowest 10 % wait", mean(scenario, variant, strategy, "latency_p90", scale), unit)
            lines.append("")
    with open(path, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
