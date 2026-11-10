"""Tests for v5: the topic space and the open network (DESIGN.md §14)."""

from dataclasses import replace

import numpy as np
import pytest

from whoknows.company import CompanyConfig, SPACE_V3, build_world
from whoknows.experiments import NET_SIM
from whoknows.metrics import summarize
from whoknows.network import company_in_network_terms, network_config
from whoknows.sim import Sim
from whoknows.strategies import make
from whoknows.topics import CORE, Space, TopicVectors

SMALL_NET = network_config(200, seed=3)


@pytest.fixture(scope="module")
def net():
    return build_world(SMALL_NET, use_cache=False)


@pytest.mark.parametrize("space", [SPACE_V3, Space(40, 6, 28, 6)])
def test_item_ids_round_trip(space):
    for item in range(0, space.n_items, 97):
        assert space.item_id(*space.item_parts(item)) == item
    assert space.item_parts(space.item_id(3, CORE, 2)) == (3, CORE, 2)


def test_topic_vectors_have_the_v3_similarities():
    space = Space(40, 6, 28, 6)
    tv = TopicVectors(space)
    rng = np.random.default_rng(0)
    own, analogue, aspect, domain, rand = [], [], [], [], []
    for _ in range(400):
        t, lane, k = int(rng.integers(space.n_topics)), int(rng.integers(space.lanes)), int(rng.integers(6))
        q = tv.question_vec("content", t, lane, k, 0)
        own.append(q @ tv.item_vec(space.item_id(t, lane, k)))
        analogue.append(q @ tv.item_vec(space.item_id(t, (lane + 1) % space.lanes, k)))
        aspect.append(q @ tv.item_vec(space.item_id(t, lane, (k + 1) % 6)))
        t2 = space.domain(t) * 6 + (t % 6 + 1) % 6
        domain.append(q @ tv.item_vec(space.item_id(t2, lane, k)))
        rand.append(q @ tv.item_vec(int(rng.integers(space.n_items))))
    assert np.mean(own) == pytest.approx(0.95, abs=0.03)
    assert np.mean(analogue) == pytest.approx(0.81, abs=0.04)
    assert np.mean(aspect) == pytest.approx(0.88, abs=0.04)
    assert np.mean(domain) == pytest.approx(0.22, abs=0.05)
    assert abs(np.mean(rand)) < 0.05


def test_the_same_question_always_gets_the_same_vector():
    tv = TopicVectors(Space(4, 6, 5, 6))
    a = tv.question_vec("technical", 7, 2, 3, 1)
    tv.question_vec.cache_clear()
    assert np.array_equal(a, tv.question_vec("technical", 7, 2, 3, 1))


def test_network_vectors_leave_the_company_history_unchanged():
    """The history's random draws do not depend on the vectors, so the company
    described with network vectors has the same people, items and roles."""
    small = CompanyConfig(quarters=6, seed=3)
    v3 = build_world(small, use_cache=False)
    net = build_world(company_in_network_terms(quarters=6, seed=3), use_cache=False)
    assert [sorted(s) for s in v3.items] == [sorted(s) for s in net.items]
    assert v3.roles == net.roles
    assert v3.declared == net.declared


def test_the_open_network_has_no_company(net):
    assert net.n == 200
    assert ("leadership",) not in net.roles
    assert all(t.kind != "service" for t in net.teams)
    lanes = [t.client for t in net.teams if t.kind == "client"]
    assert len(lanes) > len(set(lanes)) or len(lanes) <= SMALL_NET.lanes   # groups share lanes once there are enough
    assert len(set(net.office.tolist())) == 200 // 50
    assert all(len(owners) == 1 for owners in net.roles.values())


def test_a_network_run_keeps_its_books(net):
    cfg = replace(NET_SIM, horizon=300.0, seed=3)
    for name in ("ask_senior", "learned_local", "declared_search"):
        sim = Sim(net, make(name), cfg)
        sim.check_invariants = True
        sim.run()
        assert all(q.status in ("ok", "fail") for q in sim.queries)
        assert all(q.system is not None for q in sim.queries)          # no company-wide decisions
        for q in sim.queries:
            if q.qtype == "decision" and q.status == "ok":
                assert q.answerer in sim.roles[q.role]
        m = summarize(sim)
        assert 0 < m["newcomer_share"] < 1
        assert m["top1_share_inbox"] <= m["top5_share_inbox"]
