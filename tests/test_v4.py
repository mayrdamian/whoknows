"""Tests for the v4 additions: agents, refusals, approvals and priorities."""

from dataclasses import replace

import pytest

from whoknows.company import CompanyConfig, build_world
from whoknows.metrics import summarize
from whoknows.sim import Job, Sim, SimConfig
from whoknows.strategies import make
from whoknows.experiments import AGENT_SIM, MIXED_SIM

SMALL = CompanyConfig(quarters=6, seed=3)          # about 60 people
PEOPLE = SimConfig(horizon=96.0, seed=3)
AGENTS = replace(AGENT_SIM, horizon=600.0, seed=3)


@pytest.fixture(scope="module")
def world():
    return build_world(SMALL, use_cache=False)


def run(world, name, cfg, **kw):
    sim = Sim(world, make(name), replace(cfg, **kw))
    sim.check_invariants = True          # queue bookkeeping is asserted on every start
    return sim.run()


@pytest.mark.parametrize("priority", ["none", "asker", "answerer", "audit", "budget"])
@pytest.mark.parametrize("cfg", [PEOPLE, AGENTS, MIXED_SIM], ids=["people", "agents", "mixed"])
def test_every_variant_keeps_the_queues_consistent(world, priority, cfg):
    if cfg is MIXED_SIM:
        cfg = replace(MIXED_SIM, horizon=600.0, seed=3)
    for name in ("ask_senior", "learned_local_loadaware"):
        sim = run(world, name, cfg, priority=priority)
        assert all(q.status in ("ok", "fail") for q in sim.queries)


def test_the_questions_are_the_same_in_every_priority_variant(world):
    base = run(world, "learned_local", PEOPLE)
    for priority in ("asker", "answerer", "audit", "budget"):
        other = run(world, "learned_local", PEOPLE, priority=priority)
        assert [(q.asker, q.t0, q.qtype, q.importance) for q in other.queries] == \
               [(q.asker, q.t0, q.qtype, q.importance) for q in base.queries]


def test_a_high_priority_ask_goes_ahead_of_normal_ones(world):
    sim = Sim(world, make("learned_local"), replace(PEOPLE, priority="asker"))
    b = 0
    sim._add_work(b, Job(None, "own", 5.0, 0.0), "normal")        # in hand
    first = Job(None, "busy", 1.0, 0.0, prio=1)
    second = Job(None, "busy", 1.0, 0.0, prio=1)
    urgent = Job(None, "busy", 1.0, 0.0, prio=2)
    for job in (first, second, urgent):
        sim._add_work(b, job, "normal")
    assert list(sim.state[b].normal) == [urgent, first, second]
    assert first.shift == 1.0 and second.shift == 1.0               # both now start one unit later
    assert urgent.projected_wait == 5.0


def test_agents_refuse_instead_of_letting_asks_sink(world):
    busy = replace(AGENTS, questions_per_day=240.0)
    sim = run(world, "ask_senior", busy)
    assert sum(s.rejected for s in sim.state) > 0
    assert sum(s.ignored for s in sim.state) == 0                   # nothing sinks unread


def test_a_refusal_costs_no_read(world):
    sim = run(world, "ask_senior", replace(AGENTS, questions_per_day=240.0))
    for s in sim.state:                 # reads come only from handled asks, BUSY replies, reminders, triage
        assert s.reads == s.handled + s.busy_replies + s.reminders + s.triage_reads


def test_an_answer_needing_approval_waits_for_the_human(world):
    sim = run(world, "learned_local", replace(MIXED_SIM, horizon=600.0, seed=3, p_approval=0.5))
    waited = [q for q in sim.queries if q.approval_wait is not None]
    assert waited
    assert all(q.approval_wait >= sim.cfg.t_approval - 1e-9 for q in waited)
    assert all(q.deadline == sim.cfg.deadline_human for q in waited)


def test_answerer_priority_reads_every_ask(world):
    sim = run(world, "learned_local", PEOPLE, priority="answerer")
    m = summarize(sim)
    assert sum(s.triage_reads for s in sim.state) == sum(s.received for s in sim.state)
    assert m["triage_per_query"] > 0


def test_budget_caps_high_labels(world):
    sim = run(world, "learned_local", PEOPLE, priority="budget", inflaters=1.0)
    per_asker = {}
    for q in sim.queries:
        per_asker[q.asker] = per_asker.get(q.asker, 0) + (q.label == 2)
    assert max(per_asker.values()) <= sim.high_budget


def test_parallel_calls_speed_up_messages_but_not_own_work(world):
    sim = Sim(world, make("learned_local"), AGENTS)
    own, ask = Job(None, "own", 8.0, 0.0), Job(None, "busy", 8.0, 0.0)
    sim._add_work(0, own, "background")
    sim._add_work(0, ask, "normal")
    assert own.service == 8.0 and ask.service == 8.0 / AGENTS.speed


def test_agents_spend_the_designed_share_on_own_work(world):
    """own_work is a share of capacity for people and agents alike."""
    for cfg in (replace(PEOPLE, peaks=False), replace(AGENTS, peaks=False)):
        sim = run(world, "learned_local", replace(cfg, questions_per_day=0.1))
        span = cfg.horizon + cfg.deadline + cfg.patience
        share = sum(s.own_time for s in sim.state) / (sim.n * span)
        assert 0.5 < share < 0.7, (cfg.overflow, share)
