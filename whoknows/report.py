"""Figures and tables from results/runs.csv (WhoKnows v3).

    python -m whoknows.report --runs results/runs.csv --out results

Colours follow the strategy, never its rank, in the fixed, colour-blind-checked
order of the dataviz reference palette (light mode). Charts with every pair
in view (the trade-off scatter) colour only three strategies and grey the rest.
"""

from __future__ import annotations

import argparse
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from .experiments import KEY_METRICS, aggregate  # noqa: E402

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e4e3df"
NEUTRAL = "#8a8984"

# strategy -> (label, colour); order = legend order
STYLE = {
    "learned_local_loadaware": ("Learned, local, load-aware", "#2a78d6"),
    "ask_senior": ("Ask the senior (field-study habit)", "#eb6834"),
    "learned_central": ("Learned, central log", "#1baf7a"),
    "declared_search_trust": ("Declared search, trust-ranked", "#eda100"),
    "learned_local": ("Learned, local", "#e87ba4"),
    "hybrid_search_learned": ("Search + learned (hybrid)", "#008300"),
    "declared_search": ("Declared search", "#6250d6"),
    "attested_search": ("Signed track records", "#e34948"),
    "phonebook": ("Phonebook (own memory)", NEUTRAL),
    "random_walk": ("Random walk (control)", NEUTRAL),
}
LINE_SET = ["learned_local_loadaware", "ask_senior", "learned_central", "learned_local",
            "hybrid_search_learned", "declared_search", "attested_search"]
HIGHLIGHT = ("learned_local_loadaware", "ask_senior", "learned_central")
QTYPE_LABEL = {"content": "Content", "whom": "Whom to ask", "technical": "Technical issue",
               "decision": "Decision"}


def _style_axes(ax, title, xlabel, ylabel):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", color=INK, fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel(xlabel, color=INK2, fontsize=10)
    ax.set_ylabel(ylabel, color=INK2, fontsize=10)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9)


def _fig(w=7.2, h=5.0):
    fig, ax = plt.subplots(figsize=(w, h), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    return fig, ax


def _legend_below(ax, ncol=2):
    ax.legend(frameon=False, fontsize=8.5, labelcolor=INK2, loc="upper left",
              bbox_to_anchor=(0.0, -0.16), ncol=ncol, handlelength=3)


def _pct(ax, axis="y"):
    fmt = matplotlib.ticker.PercentFormatter(1.0, decimals=0)
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def _save(fig, out, name):
    fig.tight_layout()
    fig.savefig(os.path.join(out, name), facecolor=SURFACE)
    plt.close(fig)


# -- figures -----------------------------------------------------------------

# where each strategy's label goes in the trade-off chart: (x, y) in data units,
# alignment, and whether a thin leader line joins it to its dot
LABEL_POS = {
    "learned_local": (0.40, 0.865, "left", True),
    "attested_search": (0.40, 0.84, "left", True),
    "hybrid_search_learned": (0.40, 0.815, "left", True),
    "learned_local_loadaware": (0.40, 0.79, "left", True),
    "learned_central": (0.372, 0.751, "left", False),
    "declared_search": (0.238, 0.651, "left", False),
    "declared_search_trust": (0.255, 0.613, "left", False),
    "phonebook": (0.126, 0.611, "left", False),
    "ask_senior": (0.648, 0.532, "right", False),
}
LEARNED = ("learned_local", "attested_search", "hybrid_search_learned", "learned_local_loadaware")
ACCENT = "#2a78d6"


def fig_tradeoff(agg, out):
    """One accent: the strategies that learn from outcomes and keep memory local."""
    b = agg[agg.scenario == "baseline"]
    fig, ax = _fig(7.6, 5.0)
    for st, (lx, ly, ha, lead) in LABEL_POS.items():
        r = b[b.strategy == st]
        if r.empty:
            continue
        r = r.iloc[0]
        c = ACCENT if st in LEARNED else NEUTRAL
        ax.errorbar(r.top5_share_inbox, r.correct, xerr=r.top5_share_inbox_ci, yerr=r.correct_ci,
                    fmt="o", ms=8, color=c, ecolor=c, elinewidth=1.2, capsize=0,
                    markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=3)
        if lead:
            ax.plot([r.top5_share_inbox + 0.008, lx - 0.004], [r.correct, ly + 0.004], color=GRID,
                    linewidth=1, zorder=1)
        ax.text(lx, ly, STYLE[st][0].split(" (")[0], ha=ha, va="bottom", fontsize=8.5,
                color=INK if st in LEARNED else INK2, fontweight="bold" if st in LEARNED else "normal")
    ax.axvline(0.05, color=NEUTRAL, linewidth=1, linestyle=(0, (4, 4)), zorder=1)
    ax.text(0.056, 0.895, "5 % = load spread evenly", fontsize=8, color=INK2, va="top")
    _style_axes(ax, "Learned routing answers more and keeps load off the busiest 5 %",
                "Share of all inbox messages that reach the busiest 5 % of people",
                "Questions answered correctly")
    _pct(ax, "x")
    _pct(ax)
    ax.set_xlim(0, 0.72)
    ax.set_ylim(0.5, 0.9)
    _save(fig, out, "fig1_tradeoff.png")


def fig_question_types(agg, out, strategies=("ask_senior", "declared_search", "learned_local",
                                             "learned_local_loadaware")):
    b = agg[agg.scenario == "baseline"]
    types = list(QTYPE_LABEL)
    fig, ax = _fig(7.2, 4.6)
    width = 0.8 / len(strategies)
    x = np.arange(len(types))
    for i, st in enumerate(strategies):
        r = b[b.strategy == st]
        if r.empty:
            continue
        r = r.iloc[0]
        vals = [r[f"correct_{t}"] for t in types]
        cis = [r.get(f"correct_{t}_ci", 0) for t in types]
        ax.bar(x - 0.4 + width * (i + 0.5), vals, width - 0.03, yerr=cis, color=STYLE[st][1],
               label=STYLE[st][0], error_kw=dict(ecolor=INK2, elinewidth=1), zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels([QTYPE_LABEL[t] for t in types])
    _style_axes(ax, "Answered correctly, by kind of question", "", "Questions answered correctly")
    _pct(ax)
    ax.set_ylim(0, 1.05)
    _legend_below(ax)
    _save(fig, out, "fig2_question_types.png")


def _xvals(s, scenario, df_runs=None):
    if scenario == "growth":
        sizes = {}
        if df_runs is not None:
            g = df_runs[df_runs.scenario == "growth"]
            for v, grp in g.groupby("variant"):
                sizes[v] = float(np.mean([json.loads(x)["people"] for x in grp.world]))
        return s.variant.map(sizes)
    return s.variant.str.split("=").str[1].str.split(",").str[0].astype(float)


def fig_sweep(agg, scenario, metric, title, ylabel, xlabel, fname, out, pct=True, df_runs=None,
              strategies=LINE_SET):
    s = agg[agg.scenario == scenario].copy()
    if s.empty or metric not in s:
        return
    s["x"] = _xvals(s, scenario, df_runs)
    fig, ax = _fig()
    for i, st in enumerate(strategies):
        r = s[s.strategy == st].sort_values("x")
        if r.empty:
            continue
        label, color = STYLE[st]
        ax.plot(r.x, r[metric], color=color, linewidth=2, marker="o", ms=6, zorder=10 - i,
                markeredgecolor=SURFACE, markeredgewidth=1.5, label=label)
        ci = r.get(metric + "_ci")
        if ci is not None:
            ax.fill_between(r.x, r[metric] - ci, r[metric] + ci, color=color, alpha=0.10, linewidth=0)
    _style_axes(ax, title, xlabel, ylabel)
    if pct:
        _pct(ax)
    _legend_below(ax)
    _save(fig, out, fname)


def fig_turnover(agg, out):
    d = agg[agg.scenario == "turnover"]
    if d.empty:
        return
    order = [st for st in LINE_SET if st in set(d.strategy)]
    fig, ax = _fig(7.2, 4.8)
    y = np.arange(len(order))[::-1]
    for yi, st in zip(y, order):
        none = d[(d.strategy == st) & (d.variant == "handover=none")].iloc[0]
        succ = d[(d.strategy == st) & (d.variant == "handover=successor")].iloc[0]
        before, a0, a1 = none.correct_before_dropout, none.correct_after_dropout, succ.correct_after_dropout
        ax.plot([min(before, a0, a1), max(before, a0, a1)], [yi, yi], color=GRID, linewidth=2, zorder=1)
        for val, c, lab in ((before, NEUTRAL, "Before they leave"),
                            (a0, "#eb6834", "After, no handover"),
                            (a1, "#2a78d6", "After, handover to a successor")):
            ax.scatter([val], [yi], s=55, color=c, zorder=3, edgecolors=SURFACE, linewidths=1.5,
                       label=lab if yi == y[0] else None)
    ax.set_yticks(y)
    ax.set_yticklabels([STYLE[st][0] for st in order])
    _style_axes(ax, "When the three longest-serving people leave", "Questions answered correctly", "")
    _pct(ax, "x")
    _legend_below(ax, ncol=2)
    _save(fig, out, "fig7_turnover.png")


def fig_overtime(agg, out):
    b = agg[agg.scenario == "baseline"]
    order = [st for st in STYLE if st in set(b.strategy) and st != "random_walk"]
    fig, ax = _fig(7.2, 4.8)
    y = np.arange(len(order))[::-1]
    h = 0.38
    for yi, st in zip(y, order):
        r = b[b.strategy == st].iloc[0]
        ax.barh(yi + h / 2, r.own_backlog_senior_mean, h - 0.04, color="#eb6834", zorder=3,
                label="Seniors (10 % longest-serving)" if yi == y[0] else None)
        ax.barh(yi - h / 2, r.own_backlog_others_mean, h - 0.04, color=NEUTRAL, zorder=3,
                label="Everyone else" if yi == y[0] else None)
    ax.set_yticks(y)
    ax.set_yticklabels([STYLE[st][0] for st in order])
    _style_axes(ax, "Own work left over at the end of two weeks",
                "Time units per person (1 ≈ 10 minutes)", "")
    _legend_below(ax)
    _save(fig, out, "fig8_overtime.png")


# -- tables --------------------------------------------------------------------

def table_md(agg, scenario, cols, out_name, out):
    t = agg[agg.scenario == scenario]
    if t.empty:
        return ""
    order = [st for st in STYLE if st in set(t.strategy)]
    lines = []
    for var in t.variant.unique():
        lines += [f"**{scenario} / {var}** (mean ± 95 % CI over {int(t.n.max())} seeds)", "",
                  "| strategy | " + " | ".join(c for c, _ in cols) + " |",
                  "|---|" + "---|" * len(cols)]
        for st in order:
            r = t[(t.strategy == st) & (t.variant == var)]
            if r.empty:
                continue
            r = r.iloc[0]
            cells = []
            for c, fmt in cols:
                if c not in r or pd.isna(r[c]):
                    cells.append("–")
                    continue
                ci = r.get(c + "_ci", 0) or 0
                cells.append(fmt.format(r[c]) + (f" ± {fmt.format(ci)}" if ci > 0 else ""))
            lines.append(f"| {STYLE[st][0]} | " + " | ".join(cells) + " |")
        lines.append("")
    with open(os.path.join(out, out_name), "w") as f:
        f.write("\n".join(lines))
    return "\n".join(lines)


P, F1, F2 = "{:.0%}", "{:.1f}", "{:.2f}"
BASE_COLS = [("correct", P), ("wrong", P), ("correct_undeclared", P), ("latency_median", F1),
             ("latency_p90", F1), ("messages_mean", F1), ("top5_share_inbox", P),
             ("senior_share_inbox", P), ("never_read_per_query", F2), ("own_backlog_senior_mean", F1),
             ("central_records", "{:,.0f}")]
TYPE_COLS = [(f"correct_{t}", P) for t in QTYPE_LABEL] + [(f"wrong_{t}", P) for t in QTYPE_LABEL]
SHORT_COLS = [("correct", P), ("wrong", P), ("latency_p90", F1), ("top5_share_inbox", P),
              ("senior_share_inbox", P), ("never_read_per_query", F2), ("own_backlog_senior_mean", F1)]


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--runs", default="results/runs.csv")
    p.add_argument("--out", default="results")
    a = p.parse_args(argv)
    df = pd.read_csv(a.runs)
    os.makedirs(a.out, exist_ok=True)
    agg = aggregate(df, KEY_METRICS)
    agg.to_csv(os.path.join(a.out, "summary.csv"), index=False)
    fig_tradeoff(agg, a.out)
    fig_question_types(agg, a.out)
    fig_sweep(agg, "growth", "correct", "Answered correctly as the company grows",
              "Questions answered correctly", "People in the company", "fig3a_growth_correct.png",
              a.out, df_runs=df)
    fig_sweep(agg, "growth", "top5_share_inbox", "Load on the busiest 5 % as the company grows",
              "Share of inbox messages", "People in the company", "fig3b_growth_concentration.png",
              a.out, df_runs=df)
    fig_sweep(agg, "reminders", "correct", "Answered correctly with reminders",
              "Questions answered correctly", "Reminders allowed per person", "fig4_reminders.png", a.out)
    fig_sweep(agg, "load", "correct", "Answered correctly as people ask more",
              "Questions answered correctly", "Question rate (1 = 1.5 per person per day)",
              "fig5_load.png", a.out)
    fig_sweep(agg, "decisions", "owner_share_inbox", "Decision questions land on their owners",
              "Share of inbox messages reaching owners", "Share of questions that are decisions",
              "fig6_decisions.png", a.out)
    fig_turnover(agg, a.out)
    fig_overtime(agg, a.out)
    table_md(agg, "baseline", BASE_COLS, "table_baseline.md", a.out)
    table_md(agg, "baseline", TYPE_COLS, "table_question_types.md", a.out)
    for name in ("growth", "reminders", "decisions", "load", "own_work", "adversaries", "tiers",
                 "sensitivity"):
        table_md(agg, name, SHORT_COLS, f"table_{name}.md", a.out)
    table_md(agg, "turnover", [("correct_before_dropout", P), ("correct_after_dropout", P),
                               ("latency_p90", F1)], "table_turnover.md", a.out)
    print("figures and tables written to", a.out)


if __name__ == "__main__":
    main()
