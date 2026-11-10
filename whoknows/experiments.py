"""Scenarios and the experiment runner (DESIGN.md §10).

    python -m whoknows.experiments --scenario baseline --seeds 20 --out results
    python -m whoknows.experiments --scenario sweeps --seeds 10 --out results

Every (scenario, variant, strategy, seed) run is one row in runs.csv. A seed
fixes the company history and the stream of questions; all strategies see
the same company and the same questions.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import replace
from multiprocessing import Pool

import numpy as np
import pandas as pd
from scipy.stats import t as t_dist

from .company import CompanyConfig, build_world, with_adversaries
from .metrics import summarize
from .network import company_in_network_terms, network_config
from .sim import Sim, SimConfig
from .strategies import MAIN, SWEEP, make

BASE_CO = CompanyConfig()
BASE_SIM = SimConfig()

# v4: the same company, but every person replaced by their agent (DESIGN.md, v4 section).
# Time unit = 1 second. Every number here is an assumption to sweep, not a measurement.
AGENT_SIM = replace(
    BASE_SIM,
    horizon=3600.0, day=3600.0,        # one hour of agent time; the question rate is per hour
    questions_per_day=30.0,            # questions per agent per hour (swept: 15-120)
    deadline=600.0, patience=60.0,     # an agent asker gives up after 10 minutes, waits 1 minute per contact
    max_followups=0,                   # agents move on instead of sending reminders
    latency=0.2, lookup_delay=0.5,
    t_content=10.0, t_technical=20.0, t_decision=10.0, t_name=3.0, t_refer=3.0,
    t_dontknow=2.0, t_busy=0.5, t_followup=0.5, t_triage=2.0,
    own_block=7.5, peak_length=720.0,  # the owner's own tasks: 7.5-second blocks, a 12-minute rush
                                       # (block : BUSY : refusal = 1 : 2 : 4, as for people)
    discover_delay=600.0, window=360.0,
    busy_threshold=15.0, load_lambda=0.012, load_tau=300.0,   # same penalty for a BUSY as people get
    overflow="reject", reject_after=30.0,  # more than 30 s of work ahead: refused, "rate limited"
    speed=4.0,                         # four parallel calls
)
# the realistic middle: fast agents, but some answers need their human owner's approval
MIXED_SIM = replace(AGENT_SIM, approvals=True)
PRIORITY_STRATEGIES = ["ask_senior", "declared_search", "learned_local", "learned_local_loadaware",
                       "attested_search"]
SHORT_STRATEGIES = ["ask_senior", "learned_local", "learned_local_loadaware"]
# priorities only matter when work queues up, so they are tested in a busy network
BUSY_AGENT_SIM = replace(AGENT_SIM, questions_per_day=60.0)


# v5: an open network has no company-wide decisions (no leadership)
NET_SIM = replace(AGENT_SIM, company_decisions=0.0)
NET_MIXED_SIM = replace(MIXED_SIM, company_decisions=0.0)
NET_BUSY_SIM = replace(BUSY_AGENT_SIM, company_decisions=0.0)
NET = network_config(1000)
GATE_CO = company_in_network_terms()
NET_PRIORITY_STRATEGIES = ["ask_senior", "learned_local", "attested_search"]


def _sim(**kw) -> SimConfig:
    return replace(BASE_SIM, **kw)


def _co(**kw) -> CompanyConfig:
    return replace(BASE_CO, **kw)


# name -> list of (variant, company config, sim config, adversaries?)
def scenarios() -> dict[str, list[tuple]]:
    base = [("base", BASE_CO, BASE_SIM, False)]
    return {
        "baseline": base,
        # the company at the end of year 1..4, and extrapolated to ~200 people
        "growth": [(f"quarters={q}", _co(quarters=q), BASE_SIM, False) for q in (4, 8, 12, 16, 22)],
        "reminders": [(f"reminders={k}", BASE_CO, _sim(max_followups=k), False) for k in (0, 1, 2, 3)],
        "decisions": [(f"decisions={d}", BASE_CO,
                       _sim(mix=(0.35, 0.20, 0.35, d)), False) for d in (0.05, 0.10, 0.20, 0.30)],
        "load": [(f"rate={r}", BASE_CO, _sim(questions_per_day=1.5 * r), False) for r in (0.5, 1.0, 1.5, 2.0)],
        "own_work": [("own=0.4", BASE_CO, _sim(own_work=0.4), False),
                     ("own=0.6", BASE_CO, BASE_SIM, False),
                     ("own=0.8", BASE_CO, _sim(own_work=0.8, peak_work=0.95), False),
                     ("own=0.6,no peaks", BASE_CO, _sim(peaks=False), False)],
        "turnover": [("handover=none", BASE_CO, _sim(dropout_at=240.0), False),
                     ("handover=successor", BASE_CO, _sim(dropout_at=240.0, handover="successor"), False)],
        "adversaries": [("adversaries", BASE_CO, BASE_SIM, True)],
        "tiers": [("synthetic", _co(tier="synthetic"), BASE_SIM, False),
                  ("text", BASE_CO, BASE_SIM, False)],
        # the baseline again with a sentence-embedding model instead of word vectors
        "minilm": [("minilm", _co(tier="minilm"), BASE_SIM, False)],
        # ---- v4: agents ----
        "speed": [("people", BASE_CO, BASE_SIM, False),
                  ("agents", BASE_CO, AGENT_SIM, False),
                  ("agents+approvals", BASE_CO, MIXED_SIM, False)],
        "agent_load": [(f"rate={r}/h", BASE_CO, replace(AGENT_SIM, questions_per_day=float(r)), False)
                       for r in (15, 60, 120)],
        "priority_people": [(f"priority={p}", BASE_CO, _sim(priority=p), False)
                            for p in ("none", "asker", "answerer", "audit", "budget")],
        "priority_agents": [(f"priority={p}", BASE_CO, replace(BUSY_AGENT_SIM, priority=p), False)
                            for p in ("none", "asker", "answerer", "audit", "budget")],
        "inflation": [(f"priority={p},inflaters={f}", BASE_CO, replace(BUSY_AGENT_SIM, priority=p, inflaters=f), False)
                      for p in ("asker", "audit", "budget") for f in (0.0, 0.3, 0.6)],
        "triage_cost": [(f"triage={t}s", BASE_CO, replace(BUSY_AGENT_SIM, priority="answerer", t_triage=t), False)
                        for t in (0.0, 2.0, 8.0)],
        # ---- v5: the open network (DESIGN.md §14) ----
        # the gate: the v3 company described with the open network's topic vectors
        "gate": [("people", GATE_CO, BASE_SIM, False),
                 ("agents", GATE_CO, AGENT_SIM, False)],
        # experiment 1 in the open network: the same rules at 130, 300 and 1,000 agents
        "net_size": [(f"agents={n}", network_config(n), NET_SIM, False) for n in (130, 300)],
        "net_speed": [("agents", NET, NET_SIM, False),
                      ("agents+approvals", NET, NET_MIXED_SIM, False)],
        # experiment 2 in the open network: who sets the priority, at 60 questions per agent and hour
        "net_priority": [(f"priority={p}", NET, replace(NET_BUSY_SIM, priority=p), False)
                         for p in ("none", "asker", "answerer", "audit", "budget")],
        "net_inflation": [(f"priority={p},inflaters=0.6", NET, replace(NET_BUSY_SIM, priority=p, inflaters=0.6),
                           False) for p in ("asker", "audit")],
        "sensitivity": [
            ("patience=12", BASE_CO, _sim(patience=12.0), False),
            ("patience=48", BASE_CO, _sim(patience=48.0), False),
            ("deadline=48", BASE_CO, _sim(deadline=48.0), False),
            ("deadline=192", BASE_CO, _sim(deadline=192.0), False),
            ("max_attempts=12", BASE_CO, _sim(max_attempts=12), False),
            ("busy_threshold=6", BASE_CO, _sim(busy_threshold=6.0), False),
            ("busy_threshold=24", BASE_CO, _sim(busy_threshold=24.0), False),
            ("busy_cost=0.5", BASE_CO, _sim(t_busy=0.5), False),
            ("busy_cost=0", BASE_CO, _sim(busy_queued=False), False),
            ("load_lambda=0.005", BASE_CO, _sim(load_lambda=0.005), False),
            ("load_lambda=0.045", BASE_CO, _sim(load_lambda=0.045), False),
            ("near_best=0.05", BASE_CO, _sim(near_best=0.05), False),
            ("near_best=0.25", BASE_CO, _sim(near_best=0.25), False),
            ("analogue_help=0.25", BASE_CO, _sim(p_analog=0.25), False),
            ("analogue_help=0.75", BASE_CO, _sim(p_analog=0.75, p_analog_wrong=0.05), False),
            ("cross_office=low", _co(cross_mixing=0.0), BASE_SIM, False),
            ("cross_office=high", _co(cross_mixing=0.12), BASE_SIM, False),
            ("offices=5", _co(office_opens=(0, 3, 6, 9, 11)), BASE_SIM, False),
        ],
    }


SWEEPS = ["growth", "reminders", "decisions", "load", "own_work", "turnover", "adversaries",
          "tiers", "sensitivity"]
V4 = ["speed", "agent_load", "priority_people", "priority_agents", "inflation", "triage_cost"]
V5 = ["gate", "net_size", "net_speed", "net_priority", "net_inflation"]


def _world(ccfg: CompanyConfig, seed: int, adversaries: bool):
    w = build_world(replace(ccfg, seed=seed))
    return with_adversaries(w, seed=seed) if adversaries else w


def _build(args):
    ccfg, seed = args
    build_world(replace(ccfg, seed=seed))
    return seed


def _one(args) -> dict:
    scenario, variant, ccfg, scfg, adv, strategy, seed = args
    w = _world(ccfg, seed, adv)
    t = time.time()
    sim = Sim(w, make(strategy), replace(scfg, seed=seed)).run()
    m = summarize(sim)
    m.update(scenario=scenario, variant=variant, strategy=strategy, seed=seed,
             runtime_s=round(time.time() - t, 2), world=json.dumps(w.summary()))
    for k in ("curve", "fail_reasons", "followup_reasons"):
        m[k] = json.dumps(m[k])
    return m


def run(names: list[str], seeds: int, out: str, procs: int = 2, strategies=None,
        skip_done: bool = False) -> pd.DataFrame:
    """Runs one scenario variant after another and saves each as soon as it is
    done, so an interrupted sweep loses at most the variant in progress."""
    os.makedirs(out, exist_ok=True)
    sc = scenarios()
    path = os.path.join(out, "runs.csv")
    done = set()
    if skip_done and os.path.exists(path):
        old = pd.read_csv(path, usecols=["scenario", "variant"])
        done = set(zip(old.scenario, old.variant))
    with Pool(procs) as pool:
        for name in names:
            for variant, ccfg, scfg, adv in sc[name]:
                if (name, variant) in done:
                    continue
                strats = strategies or _strategies_for(name, variant)
                jobs = [(name, variant, ccfg, scfg, adv, s, seed)
                        for seed in range(seeds) for s in strats]
                t0 = time.time()
                list(pool.imap_unordered(_build, [(ccfg, seed) for seed in range(seeds)]))
                rows = list(pool.imap_unordered(_one, jobs, chunksize=2))
                df = pd.DataFrame(rows)
                if os.path.exists(path):  # keep everything else, replace a rerun
                    old = pd.read_csv(path)
                    keep = ~((old["scenario"] == name) & (old["variant"] == variant))
                    df = pd.concat([old[keep], df], ignore_index=True)
                df.to_csv(path, index=False)
                print(f"  {name} / {variant}: {len(jobs)} runs saved, {time.time() - t0:.0f}s", flush=True)
    return pd.read_csv(path)


def _strategies_for(name: str, variant: str) -> list[str]:
    if name in ("baseline", "minilm", "speed", "gate", "net_size"):
        return MAIN
    if name == "net_speed":
        return MAIN if variant == "agents" else PRIORITY_STRATEGIES
    if name in ("net_priority", "net_inflation"):
        return NET_PRIORITY_STRATEGIES
    if name in ("inflation", "triage_cost"):
        return SHORT_STRATEGIES
    if name in ("priority_people", "priority_agents"):
        return PRIORITY_STRATEGIES
    return SWEEP


KEY_METRICS = [
    "correct", "wrong", "partly", "latency_median", "latency_p90", "messages_mean",
    "reminders_per_query", "busy_per_query", "top5_share_inbox", "senior_share_inbox",
    "gini_inbox", "senior_share_help", "help_share_senior_mean", "help_share_others_mean",
    "backlog_senior_mean", "own_backlog_senior_mean", "own_backlog_others_mean",
    "ignored_per_query", "never_read_per_query", "wasted_per_query", "owner_share_inbox",
    "cross_client_help_share", "correct_undeclared",
    "correct_content", "correct_whom", "correct_technical", "correct_decision",
    "wrong_content", "wrong_whom", "wrong_technical", "wrong_decision",
    "central_records", "max_local_records", "correct_before_dropout", "correct_after_dropout",
]


def aggregate(df: pd.DataFrame, metrics=KEY_METRICS) -> pd.DataFrame:
    """Mean and 95 % CI half-width (Student t) per scenario/variant/strategy."""
    rows = []
    for (sc, var, st), g in df.groupby(["scenario", "variant", "strategy"], sort=False):
        r = {"scenario": sc, "variant": var, "strategy": st, "n": len(g)}
        for m in metrics:
            if m not in g:
                continue
            x = pd.to_numeric(g[m], errors="coerce").dropna()
            if len(x) == 0:
                continue
            r[m] = x.mean()
            r[m + "_ci"] = (t_dist.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
                            if len(x) > 1 else 0.0)
        rows.append(r)
    return pd.DataFrame(rows)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scenario", default="baseline", help="a name, a comma list, 'sweeps' or 'all'")
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--procs", type=int, default=2)
    p.add_argument("--strategies", default=None)
    p.add_argument("--out", default="results")
    p.add_argument("--skip-done", action="store_true", help="skip variants already in runs.csv")
    a = p.parse_args(argv)
    if a.scenario == "all":
        names = ["baseline"] + SWEEPS
    elif a.scenario == "v4":
        names = V4
    elif a.scenario == "v5":
        names = V5
    elif a.scenario == "sweeps":
        names = SWEEPS
    else:
        names = a.scenario.split(",")
    strategies = a.strategies.split(",") if a.strategies else None
    df = run(names, a.seeds, a.out, a.procs, strategies, skip_done=a.skip_done)
    aggregate(df).to_csv(os.path.join(a.out, "summary.csv"), index=False)
    print(f"wrote {len(df)} runs to {a.out}/runs.csv and {a.out}/summary.csv")


if __name__ == "__main__":
    main()
