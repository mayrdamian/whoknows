"""Tests for WhoKnows v3."""

from dataclasses import replace

import numpy as np
import pytest

from whoknows.company import (A, CORE, CompanyConfig, build_world, item_id, item_parts,
                              with_adversaries)
from whoknows.memory import Memory
from whoknows.metrics import gini, summarize
from whoknows.sim import Job, Query, Sim, SimConfig
from whoknows.strategies import MAIN, STRATEGIES, Strategy, make

SMALL = CompanyConfig(quarters=6, seed=3)          # about 60 people, three offices
FAST = SimConfig(horizon=96.0, seed=3)


@pytest.fixture(scope="module")
def world():
    return build_world(SMALL, use_cache=False)


def run(world, name, **kw):
    sim = Sim(world, make(name), replace(FAST, **kw))
    sim.check_invariants = True
    return sim.run()


# -- the company history ------------------------------------------------------

def test_item_ids_round_trip():
    for topic, client, k in [(0, 0, 0), (47, CORE, A - 1), (13, 7, 2)]:
        assert item_parts(item_id(topic, client, k)) == (topic, client, k)


def test_history_is_deterministic(world):
    again = build_world(SMALL, use_cache=False)
    assert [sorted(s) for s in again.items] == [sorted(s) for s in world.items]
    assert again.stats == world.stats


def test_company_reaches_its_planned_size(world):
    assert world.n == SMALL.people_at(SMALL.quarters)


def test_nobody_gets_ground_truth(world):
    """Memories hold only people one could have met; seniors are not omniscient."""
    for a in range(world.n):
        assert a not in world.memory[a].known()
    seniors = np.flatnonzero(world.senior)
    known = [len(world.memory[a].known_positive()) for a in seniors]
    assert max(known) < world.n - 1 or world.n < 20


def test_seniors_know_more_people_than_newcomers(world):
    assert world.stats["known_people_senior"] > world.stats["known_people_others"]


def test_some_knowledge_is_undeclared(world):
    assert 0.2 < world.stats["undeclared_share"] < 0.9


def test_roles_have_owners(world):
    assert len(world.roles[("leadership",)]) == SMALL.n_leadership
    for role, owners in world.roles.items():
        assert owners and all(0 <= o < world.n for o in owners)


# -- the measured period ------------------------------------------------------

@pytest.mark.parametrize("name", sorted(STRATEGIES))
def test_simulation_invariants(world, name):
    sim = run(world, name)
    assert sim.queries
    for q in sim.queries:
        assert q.status in ("ok", "fail")
        assert q.attempts <= FAST.max_attempts
        assert q.msgs >= q.attempts
        if q.status == "ok" and q.qtype == "decision":
            assert q.answerer in sim.roles[q.role]
        if q.status == "ok" and q.qtype == "whom" and q.correct:
            assert any(q.pieces[0] in world.items[h] for h in range(world.n))
    m = summarize(sim)
    assert 0.0 <= m["correct"] + m["wrong"] <= 1.0


def test_same_seed_same_result(world):
    a = summarize(run(world, "learned_local_loadaware"))
    b = summarize(run(world, "learned_local_loadaware"))
    assert a["correct"] == b["correct"] and a["messages_mean"] == b["messages_mean"]


def test_owners_never_reply_busy_to_their_own_decisions(world):
    sim = run(world, "learned_local_loadaware", busy_threshold=0.0)
    for q in sim.queries:
        if q.qtype == "decision" and q.status == "ok":
            assert q.answerer in sim.roles[q.role]
    assert any(q.qtype == "decision" and q.status == "ok" for q in sim.queries)


def test_whom_answers_are_correct_only_if_the_named_person_holds_it(world):
    sim = run(world, "learned_local")
    for q in sim.queries:
        if q.qtype == "whom" and q.status == "ok":
            assert q.correct == all(ok for _, ok, _ in q.helpers[-1:])
            assert q.correct == (q.pieces[0] in world.items[q.named])


def test_technical_questions_need_both_pieces(world):
    sim = run(world, "learned_local")
    for q in sim.queries:
        if q.qtype == "technical" and q.status == "ok":
            assert set(q.covered) == set(q.pieces)


def test_withdrawn_asks_leave_the_inbox_and_queue_bookkeeping_holds(world):
    sim = run(world, "ask_senior", max_followups=2)      # invariants checked at every start
    assert sum(s.withdrawn for s in sim.state) > 0


def test_adversary_ring_refers_to_itself(world):
    w2 = with_adversaries(world, seed=3)
    sim = Sim(w2, make("learned_local"), FAST)
    q = Query(0, 0, "content", 0.0, 0, 0, 0, [item_id(0, 0, 0)], vec=w2.vec_item[0])
    for m in w2.ring:
        sugg = sim.suggest(m, q)
        assert sugg and all(c in w2.ring for c, _ in sugg)


def test_central_log_holds_only_history_outcomes(world):
    """Its records come from question outcomes, not from a handed-out picture."""
    assert world.central_log.records > 0
    assert world.central_log.records <= SMALL.hist_questions * SMALL.hist_hops * 4 * world.n * (SMALL.quarters + 1)


# -- a hand-made situation: one overloaded senior ---------------------------------

class AskOne(Strategy):
    name = "ask_one"

    def __init__(self, target):
        self.target = target

    def next_candidate(self, sim, q):
        return None if self.target in q.asked else self.target


def test_a_reminder_digs_out_an_ignored_ask(world):
    item = next(iter(world.items[1]))
    asker = next(a for a in range(world.n) if item not in world.items[a])
    cfg = replace(FAST, questions_per_day=1e-9, own_work=0.0, peaks=False, max_followups=1)
    sim = Sim(world, AskOne(1), cfg)
    for _ in range(100):                                  # 50 units of other people's asks
        sim._add_work(1, Job(None, "busy", 0.5, 0.0), "normal")
    q = Query(0, asker, "content", 0.0, item_parts(item)[0], item_parts(item)[1], 0, [item],
              vec=world.vec_item[item])
    sim.queries.append(q)
    sim.at(0.0, sim._start, q)
    sim.run()
    assert sim.state[1].ignored == 1 and sim.state[1].rescued == 1
    assert q.status == "ok" and q.followups == 1


# -- small helpers ---------------------------------------------------------------

def test_memory_learns_and_forgets_by_evidence():
    mem = Memory(5, 4)
    v = np.array([1.0, 0, 0, 0])
    mem.add(2, v, 1.0)
    mem.add(3, np.array([0, 1.0, 0, 0]), 1.0)
    assert mem.top(v, 1)[0][0] == 2
    before = mem.scores(v)[2]
    mem.add(2, v, 3.0, sign=-1)
    assert mem.scores(v)[2] < before


def test_gini():
    assert gini([1, 1, 1, 1]) == pytest.approx(0.0)
    assert gini([0, 0, 0, 10]) == pytest.approx(0.75)


def test_main_strategies_registered():
    for name in MAIN:
        assert name in STRATEGIES
