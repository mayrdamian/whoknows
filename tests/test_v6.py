"""Tests for v6: the options for large networks (DESIGN.md §15)."""

from dataclasses import replace

import numpy as np
import pytest

from whoknows.company import build_world
from whoknows.experiments import NET_SIM
from whoknows.memory import Memory
from whoknows.metrics import summarize
from whoknows.network import large_network_config, network_config
from whoknows.sim import Sim
from whoknows.strategies import DeclaredSearch, make
from whoknows.topics import LazyTopicVectors, Space, TopicVectors


def unit(v):
    return v / np.linalg.norm(v)


def test_memory_limit_forgets_the_agent_seen_longest_ago():
    rng = np.random.default_rng(0)
    m = Memory(10, 8, limit=3)
    for agent in (1, 2, 3):
        m.add(agent, unit(rng.normal(size=8)))
    m.add(1, unit(rng.normal(size=8)))          # 1 seen again: 2 is now the oldest
    m.add(4, unit(rng.normal(size=8)))
    assert m.known() == {1, 3, 4}
    assert set(m._owner[: m._size].tolist()) == {1, 3, 4}


def test_memory_index_gives_the_same_prototypes_after_forgetting():
    """A forgotten agent starts again from nothing: the remaining memory equals one
    built only from the observations since each kept agent last came back."""
    rng = np.random.default_rng(1)
    obs = [(int(rng.integers(6)), unit(rng.normal(size=8)), int(rng.choice([1, -1]))) for _ in range(300)]
    limited = Memory(10, 8, limit=4)
    for agent, vec, sign in obs:
        limited.add(agent, vec, 1.0, sign)
    remembered: list[int] = []                  # least recently seen first
    came_back = {}
    for i, (agent, _, _) in enumerate(obs):
        if agent in remembered:
            remembered.remove(agent)
        else:
            if len(remembered) == 4:
                remembered.pop(0)
            came_back[agent] = i
        remembered.append(agent)
    assert limited.known() == set(remembered)
    fresh = Memory(10, 8)
    for i, (agent, vec, sign) in enumerate(obs):
        if agent in remembered and i >= came_back[agent]:
            fresh.add(agent, vec, 1.0, sign)
    q = unit(rng.normal(size=8))
    assert limited.scores(q) == pytest.approx(fresh.scores(q))


def test_large_network_config_scales_the_topic_space():
    a, b = network_config(1000), large_network_config(1000)
    assert a.space() == b.space()
    big = large_network_config(10_000).space()
    assert (big.lanes, big.domains) == (280, 400)


def test_lazy_vectors_have_the_dense_similarities():
    space = Space(40, 6, 28, 6)
    dense, lazy = TopicVectors(space), LazyTopicVectors(space)
    rng = np.random.default_rng(2)

    def sims(tv):
        own, analogue, other_lane = [], [], []
        for _ in range(300):
            t, lane, k = int(rng.integers(space.n_topics)), int(rng.integers(space.lanes)), int(rng.integers(6))
            q = tv.question_vec("content", t, lane, k, 0)
            own.append(q @ tv.item_vec(space.item_id(t, lane, k)))
            analogue.append(q @ tv.item_vec(space.item_id(t, (lane + 1) % space.lanes, k)))
            other_lane.append(tv.work_vec(t, lane) @ tv.work_vec(t, (lane + 1) % space.lanes))
        return np.mean(own), np.mean(analogue), np.mean(other_lane)

    for d, l in zip(sims(dense), sims(lazy)):
        assert abs(d - l) < 0.03


def test_sampled_contacts_know_about_as_many_others():
    base = network_config(300, seed=4)
    pairs = build_world(base, use_cache=False)
    sampled = build_world(replace(base, contacts="sampled"), use_cache=False)
    k_pairs = np.mean([len(m.known_ids()) for m in pairs.memory])
    k_sampled = np.mean([len(m.known_ids()) for m in sampled.memory])
    assert abs(k_sampled - k_pairs) / k_pairs < 0.1


@pytest.fixture(scope="module")
def net():
    return build_world(network_config(300, seed=5), use_cache=False)


def test_hnsw_search_finds_the_exact_best_agent(net):
    exact, approx = DeclaredSearch(), DeclaredSearch()
    sim = Sim(net, make("declared_search"), replace(NET_SIM, seed=1))
    exact.setup(sim)
    approx.setup(Sim(net, make("declared_search"), replace(NET_SIM, seed=1, search_index="hnsw")))
    rng = np.random.default_rng(3)
    same = 0
    for _ in range(200):
        t, lane = int(rng.integers(net.space.n_topics)), int(rng.integers(net.space.lanes))
        q = net.question_vec("content", t, lane, int(rng.integers(6)), 0)
        same += exact.ranked(sim, q, {0})[0][1] == pytest.approx(approx.ranked(sim, q, {0})[0][1])
    assert same >= 190


def test_lazy_own_work_keeps_the_amount_of_own_work(net):
    def own_blocks(**kw):
        sim = Sim(net, make("declared_search"), replace(NET_SIM, seed=1, horizon=300.0, **kw))
        sim._schedule_questions = lambda: None      # own work only
        arrivals = []
        real = sim._own_work_arrives
        sim._own_work_arrives = lambda a, length: (arrivals.append(length), real(a, length))
        sim.run()
        return len(arrivals), float(np.mean(arrivals))

    (n_up, mean_up), (n_lazy, mean_lazy) = own_blocks(), own_blocks(own_work_events="lazy")
    assert abs(n_lazy - n_up) / n_up < 0.03
    assert abs(mean_lazy - mean_up) / mean_up < 0.05


def test_peak_window_spreads_the_peaks_in_short_runs(net):
    short = Sim(net, make("declared_search"), replace(NET_SIM, seed=1, horizon=600.0))
    windowed = Sim(net, make("declared_search"), replace(NET_SIM, seed=1, horizon=600.0, peak_window=3600.0))
    short.run(), windowed.run()
    in_peak_short = np.mean([0 <= s < 1 for s in short.peak_start.values()])
    spread = np.ptp(list(windowed.peak_start.values()))
    assert in_peak_short == 1.0 and spread > 1500


def test_v6_options_run_end_to_end():
    w = build_world(large_network_config(200, seed=6), use_cache=False)
    cfg = replace(NET_SIM, seed=6, horizon=300.0, search_index="hnsw", own_work_events="lazy")
    for name in ("learned_central", "attested_search", "declared_search_trust"):
        m = summarize(Sim(w, make(name), cfg).run())
        assert 0.2 < m["correct"] < 1.0
        assert 0.0 < m["top01_share_inbox"] <= m["top1_share_inbox"]


def test_held_topics_ask_only_about_held_knowledge_and_drop_nothing():
    w = build_world(large_network_config(300, seed=7), use_cache=False)
    counts = {}
    for rule in ("tries", "held"):
        sim = Sim(w, make("declared_search"), replace(NET_SIM, seed=7, horizon=300.0, question_topics=rule))
        sim._schedule_questions()
        counts[rule] = len(sim.queries)
        for q in sim.queries:
            for item in q.pieces:            # every piece is held by someone other than the asker
                assert any(h != q.asker for h in w.holders[item])
    nominal = NET_SIM.questions_per_day * w.n * 300.0 / NET_SIM.day
    assert counts["held"] >= counts["tries"] and counts["held"] > 0.95 * nominal
