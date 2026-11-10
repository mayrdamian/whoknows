"""Four years of company history (DESIGN.md §3).

    world = build_world(CompanyConfig(seed=3))

Nobody is handed a picture of who knows what. Quarter by quarter the company
grows from 40 people in one office to about 130 in six; people join client
teams, learn the work, get moved, leave; and they learn about each other by
working together, by sharing an office, rarely across offices, and by asking
questions the way the field-study company did (best guess, otherwise the most
senior person they know, then follow referrals). Whatever memory people have
at the end of the history is what every strategy starts from.
"""

from __future__ import annotations

import hashlib
import os
import pickle
from dataclasses import dataclass, field, asdict, replace

from functools import lru_cache

import numpy as np

from . import text as T
from .embed import CACHE_DIR, get_embedder
from .memory import Memory
from .topics import CORE, Space, TopicVectors

# The v3 company's topic space: 8 domains of 6 topics, 16 client systems + the
# core platform, 6 aspects. Its sentences come from text.py.
SPACE_V3 = Space(len(T.DOMAINS), T.N_TOPICS_PER_DOMAIN, len(T.CLIENT_NAMES), T.N_ASPECTS)
N_DOMAINS = SPACE_V3.domains
N_TOPICS = SPACE_V3.n_topics
N_SYSTEMS = SPACE_V3.n_systems
SERVICE_DOMAINS = (0, 2, 3)                  # contracts, billing, documents
A = SPACE_V3.aspects
N_ITEMS = SPACE_V3.n_items
item_id = SPACE_V3.item_id
item_parts = SPACE_V3.item_parts


@dataclass(frozen=True)
class CompanyConfig:
    quarters: int = 16
    start_people: int = 40
    end_people: int = 130            # size after 16 quarters; sets the growth rate
    office_opens: tuple = (0, 3, 6, 9, 11, 13)   # quarter in which office i opens (assumed)
    hq_hire_share: float = 0.25      # assumed
    client_quarters: tuple = (0, 0, 0, 3, 6, 9, 12, 15, 18, 21)  # a new client every ~3 quarters
    service_team_quarter: int | None = 8   # a customer-service team from year 2 (None: none)
    service_team_size: int = 8
    core_weight: float = 1.5         # hiring weight of the core team relative to a client team
    reassign_rate: float = 0.04      # per person and quarter (assumed)
    attrition_rate: float = 0.02     # per person and quarter (assumed)
    items_per_quarter: int = 2       # items a person learns per quarter, in their own focus topic
    focus_topics: int = 4            # topics a team is active in
    focus_change: float = 0.25       # per team topic and quarter
    personal_change: float = 0.3     # a person picks another of the team's topics
    declared_quarters: int = 4       # declared skills = current team's work of the last year
    office_mixing: float = 10.0      # p(learn about an office colleague per quarter) = min(1, x / office size)
    cross_mixing: float = 0.045      # p per cross-office pair and quarter, tuned to ~30 % awareness
    hist_questions: int = 3          # questions per person and quarter
    hist_hops: int = 6
    confident: float = 0.5           # memory score at which people ask their best guess directly
    senior_frac: float = 0.10
    n_leadership: int = 3            # 0: no leadership (an open network has none)
    tier: str = "text"               # text | minilm | synthetic: v3 sentences; network: TopicVectors
    seed: int = 0
    # -- v5: the same history as a general network (DESIGN.md §14) ----------------
    # Defaults are the v3 company. Larger values describe an open network of agents:
    # communities instead of offices, groups on platform lanes instead of client teams.
    domains: int = 8                 # topic space (must be the v3 sizes for the text tiers)
    topics_per_domain: int = 6
    lanes: int = 16                  # platform lanes; groups share a lane when there are more groups
    aspects: int = 6
    cross_contacts: float | None = None   # if set: expected cross-office contacts per person and
                                          # quarter, instead of a probability per pair (cross_mixing)
    stewards: str = "first_team"     # who owns a core domain: the member of the first team who holds
                                     # most of it (v3), or "anyone" in the whole network
    vector_dim: int = 64             # tier "network": dimension of the topic vectors ...
    vector_spread: float = 0.45      # ... and how much lanes, aspects and wordings vary (topics.py)

    def space(self) -> Space:
        return Space(self.domains, self.topics_per_domain, self.lanes, self.aspects)

    def people_at(self, quarter: int) -> int:
        g = (self.end_people / self.start_people) ** (1 / 16)
        return int(round(self.start_people * g ** quarter))


@dataclass
class Team:
    id: int
    kind: str                # core | client | service
    client: int              # -1 for the core team
    home_office: int
    focus: list[int] = field(default_factory=list)


@dataclass
class Person:
    id: int
    office: int
    team: int
    joined: int                                   # quarter
    focus: int = 0                                # the topic this person works on now
    items: set[int] = field(default_factory=set)
    worklog: list[tuple[int, int, int, int]] = field(default_factory=list)  # (quarter, team, topic, client)
    left: bool = False


@dataclass
class World:
    """The company at the end of the history, re-indexed 0..n-1."""
    cfg: CompanyConfig
    n: int
    office: np.ndarray
    team: np.ndarray
    team_client: np.ndarray            # per person: client of their team (-1 core)
    tenure: np.ndarray                 # quarters
    senior: np.ndarray                 # bool
    items: list[set[int]]
    declared: list[list[tuple[int, int]]]   # (topic, client) per person
    roles: dict[tuple, list[int]]      # role -> owners
    person_roles: list[list[tuple]]
    holders: dict[int, list[int]]
    memory: list[Memory]               # each person's who-knows-what
    role_known: list[dict]             # role -> person, as each person believes
    central_log: Memory                # every question outcome of the history
    receipts: list[dict[int, set[int]]]  # topic -> distinct signers (history)
    teams: list[Team]
    vec_item: np.ndarray               # (N_ITEMS, d)
    vec_work: np.ndarray               # (N_TOPICS, N_SYSTEMS, d)
    vec_role: dict[tuple, np.ndarray]
    embedder_name: str
    stats: dict
    adversary: list[str] = field(default_factory=list)   # '' | stuffer | wrong | ring
    ring: list[int] = field(default_factory=list)        # the colluders, if any
    space: Space = SPACE_V3                              # v5: the topic space

    @property
    def dim(self) -> int:
        return self.vec_item.shape[1]

    def __getstate__(self):
        """Vectors are rebuilt from the embedding cache instead of being pickled."""
        state = dict(self.__dict__)
        for name in ("vec_item", "vec_work", "vec_role"):
            state[name] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.vec_item, self.vec_work, self.vec_role, _ = vectors_for(self.cfg)

    def item_id(self, topic: int, client: int, k: int) -> int:
        return self.space.item_id(topic, client, k)

    def item_parts(self, item: int) -> tuple[int, int, int]:
        return self.space.item_parts(item)

    def work_vec(self, topic: int, client: int) -> np.ndarray:
        return self.vec_work[topic, self.space.system_index(client)]

    def question_vec(self, qtype: str, topic: int, client: int | None, k: int, variant: int):
        return question_vec_for(self.cfg, qtype, topic, client, k, variant)

    def owner_role(self, client: int | None, topic: int) -> tuple:
        if client is None:
            return ("leadership",)
        if client == CORE:
            return ("owner", self.space.domain(topic))
        return ("lead", client)

    def analogues(self, item: int) -> list[int]:
        """The same work in other lanes (other clients); shared-lane items have none."""
        topic, client, k = self.space.item_parts(item)
        if client == CORE:
            return []
        return [self.space.item_id(topic, c, k) for c in range(self.space.lanes) if c != client]

    def summary(self) -> dict:
        return dict(self.stats)


# --------------------------------------------------------------------------
# vectors (shared by all worlds of a tier)
# --------------------------------------------------------------------------

_QCACHE: dict = {}


def question_vectors(tier: str) -> dict:
    if tier not in _QCACHE:
        emb = get_embedder(tier)
        keys, sents = [], []
        n_clients = len(T.CLIENT_NAMES)
        for t in range(N_TOPICS):
            for c in list(range(n_clients)) + [CORE]:
                for k in range(A):
                    for qtype in T.QUESTION_TEMPLATES:
                        for v in range(3):
                            keys.append((qtype, t, c, k, v))
                            sents.append(T.question_sentence(qtype, t, c, k, v))
            for v in range(3):
                keys.append(("decision", t, None, 0, v))
                sents.append(T.question_sentence("decision", t, None, 0, v))
        _QCACHE[tier] = dict(zip(keys, emb.embed(sents)))
    return _QCACHE[tier]


@lru_cache(maxsize=None)
def topic_vectors(space: Space, dim: int, spread: float) -> TopicVectors:
    return TopicVectors(space, dim=dim, lane_spread=spread, aspect_spread=spread)


def vectors_for(cfg: CompanyConfig):
    """(item vectors, work vectors, role vectors, embedder name) for a world's tier."""
    if cfg.tier != "network":
        assert cfg.space() == SPACE_V3, "the text tiers only know the v3 topic space"
        return _base_vectors(cfg.tier)
    return _network_vectors(cfg.space(), cfg.vector_dim, cfg.vector_spread)


@lru_cache(maxsize=None)
def _network_vectors(space: Space, dim: int, spread: float):
    tv = topic_vectors(space, dim, spread)
    roles = [("lead", c) for c in range(space.lanes)] + [("owner", d) for d in range(space.domains)] \
        + [("leadership",)]
    return tv.item_matrix(), tv.work, {r: tv.role_vec(r) for r in roles}, "topic-vectors"


def question_vec_for(cfg: CompanyConfig, qtype: str, topic: int, client, k: int, variant: int):
    if cfg.tier == "network":
        return topic_vectors(cfg.space(), cfg.vector_dim, cfg.vector_spread).question_vec(
            qtype, topic, client, k, variant)
    return question_vectors(cfg.tier)[(qtype, topic, client, k, variant)]


@lru_cache(maxsize=None)
def _base_vectors(tier: str):
    emb = get_embedder(tier)
    n_clients = len(T.CLIENT_NAMES)
    items = [T.item_sentence(*item_parts(i)) for i in range(N_ITEMS)]
    vec_item = emb.embed(items)
    work = [T.work_sentence(t, c) for t in range(N_TOPICS) for c in list(range(n_clients)) + [CORE]]
    vec_work = emb.embed(work).reshape(N_TOPICS, N_SYSTEMS, -1)
    roles = [("lead", c) for c in range(n_clients)] + [("owner", d) for d in range(N_DOMAINS)] \
        + [("leadership",)]
    vec_role = dict(zip(roles, emb.embed([T.role_sentence(r) for r in roles])))
    return vec_item, vec_work, vec_role, emb.name


# --------------------------------------------------------------------------
# the history
# --------------------------------------------------------------------------

class History:
    def __init__(self, cfg: CompanyConfig):
        self.cfg = cfg
        self.space = cfg.space()
        self.rng = np.random.default_rng(cfg.seed)
        self.vec_item, self.vec_work, self.vec_role, self.embedder_name = vectors_for(cfg)
        self.dim = self.vec_item.shape[1]
        self.people: list[Person] = []
        self.teams: list[Team] = []
        self.mem: list[Memory] = []
        self.role_known: list[dict] = []
        self.receipts: list[dict] = []
        self.n_max = 4 * cfg.people_at(cfg.quarters) + 50     # id space for memories
        self.central = Memory(self.n_max, self.dim)
        self.quarter = 0
        self.topic_rank = self.rng.permutation(self.space.n_topics)   # popularity of topics
        self.n_clients = 0

    # -- helpers ---------------------------------------------------------------

    def active(self) -> list[Person]:
        return [p for p in self.people if not p.left]

    def tenure(self, p: Person) -> int:
        return self.quarter - p.joined

    def team_members(self, team: int) -> list[Person]:
        return [p for p in self.people if not p.left and p.team == team]

    def open_offices(self) -> list[int]:
        return [o for o, q in enumerate(self.cfg.office_opens) if q <= self.quarter]

    def work_vec(self, topic, client):
        return self.vec_work[topic, self.space.system_index(client)]

    def question_vec(self, qtype, topic, client, k, variant):
        return question_vec_for(self.cfg, qtype, topic, client, k, variant)

    def roles_now(self) -> dict[tuple, list[int]]:
        """Leads, core-domain owners and leadership, from current tenure.
        When several groups share a lane (v5), its lead is the longest-serving
        member of any of them."""
        act = self.active()
        by_tenure = sorted(act, key=lambda p: (p.joined, p.id))
        roles: dict[tuple, list[int]] = {}
        if self.cfg.n_leadership > 0:
            roles[("leadership",)] = [p.id for p in by_tenure[: self.cfg.n_leadership]]
        lane_members: dict[int, list[Person]] = {}
        for tm in self.teams:
            if tm.kind == "client":
                lane_members.setdefault(tm.client, []).extend(self.team_members(tm.id))
        for lane, members in lane_members.items():
            if members:
                roles[("lead", lane)] = [min(members, key=lambda p: (p.joined, p.id)).id]
        if self.cfg.stewards == "first_team":
            core = sorted(self.team_members(0), key=lambda p: (p.joined, p.id))
        else:                                       # v5 open network: whoever knows the domain best
            core = by_tenure
        # core items each candidate holds, per domain
        core_items = []
        for p in core:
            per_domain: dict[int, int] = {}
            for i in p.items:
                topic, lane, _ = self.space.item_parts(i)
                if lane == CORE:
                    d = self.space.domain(topic)
                    per_domain[d] = per_domain.get(d, 0) + 1
            core_items.append(per_domain)
        for d in range(self.space.domains):
            if not core:
                continue
            held = [(counts.get(d, 0), -p.joined, -p.id, p) for p, counts in zip(core, core_items)]
            roles[("owner", d)] = [max(held, key=lambda x: x[:3])[3].id]
        return roles

    def most_senior_known(self, a: int, exclude) -> int | None:
        known = [b for b in self.mem[a].known() if b not in exclude and not self.people[b].left]
        if not known:
            return None
        return min(known, key=lambda b: (self.people[b].joined, b))

    # -- people and teams ------------------------------------------------------

    def new_team(self, kind: str, client: int, office: int) -> Team:
        tm = Team(len(self.teams), kind, client, office)
        tm.focus = self._topics_for(tm, self.cfg.focus_topics)
        self.teams.append(tm)
        return tm

    def _topics_for(self, tm: Team, n: int) -> list[int]:
        if tm.kind == "service":
            pool = [t for t in range(self.space.n_topics) if self.space.domain(t) in SERVICE_DOMAINS]
        else:
            pool = list(range(self.space.n_topics))
        return [int(t) for t in self.rng.choice(pool, size=n, replace=False)]

    def _team_weights(self, office: int, exclude: int | None = None) -> tuple[list[Team], np.ndarray]:
        cand, w = [], []
        sizes: dict[int, int] = {}
        for p in self.people:
            if not p.left:
                sizes[p.team] = sizes.get(p.team, 0) + 1
        for tm in self.teams:
            if tm.id == exclude:
                continue
            size = sizes.get(tm.id, 0)
            base = self.cfg.core_weight if tm.kind == "core" else 1.0
            if tm.kind == "service":
                if size >= self.cfg.service_team_size:
                    continue
                base = 3.0
            local = 1.0 if tm.home_office == office else 0.25
            cand.append(tm)
            w.append(base * local / (size + 1))
        w = np.array(w)
        return cand, w / w.sum()

    def hire(self) -> Person:
        offices = self.open_offices()
        if len(offices) == 1 or self.rng.random() < self.cfg.hq_hire_share:
            office = 0
        else:
            office = int(self.rng.choice(offices[1:]))
        cand, w = self._team_weights(office)
        tm = cand[int(self.rng.choice(len(cand), p=w))]
        joined = self.quarter
        if self.quarter == 0:             # the first 40 joined over the years before
            joined = -int(self.rng.integers(0, 20))
        p = Person(len(self.people), office, tm.id, joined)
        p.focus = tm.focus[int(self.rng.integers(len(tm.focus)))]
        self.people.append(p)
        self.mem.append(Memory(self.n_max, self.dim))
        self.role_known.append({})
        self.receipts.append({})
        return p

    # -- one quarter -------------------------------------------------------------

    def step(self) -> None:
        cfg, rng = self.cfg, self.rng
        # new clients and the service team
        while self.n_clients < len(cfg.client_quarters) and cfg.client_quarters[self.n_clients] <= self.quarter:
            offices = self.open_offices()
            home = 0 if self.quarter == 0 else int(offices[-1] if rng.random() < 0.6 else rng.choice(offices))
            tm = self.new_team("client", self.n_clients % self.space.lanes, home)   # groups may share a lane
            self.n_clients += 1
            # two experienced people seed a new team after the start
            if self.quarter > 0:
                movers = [p for p in self.active() if p.office == home] or self.active()
                for p in rng.choice(movers, size=min(2, len(movers)), replace=False):
                    p.team = tm.id
        if cfg.service_team_quarter is not None and self.quarter == cfg.service_team_quarter:
            office = self.open_offices()[1] if len(self.open_offices()) > 1 else 0
            self.new_team("service", 0, office)
        # attrition, reassignment, hiring
        for p in self.active():
            if self.quarter > 0 and rng.random() < cfg.attrition_rate:
                p.left = True
        for p in self.active():
            if self.quarter > 0 and rng.random() < cfg.reassign_rate:
                cand, w = self._team_weights(p.office, exclude=p.team)
                if cand:                          # (a network may start with a single group)
                    p.team = cand[int(rng.choice(len(cand), p=w))].id
        target = cfg.people_at(self.quarter)
        while len(self.active()) < target:
            self.hire()
        # team focus moves on
        for tm in self.teams:
            for j in range(len(tm.focus)):
                if rng.random() < cfg.focus_change:
                    tm.focus[j] = self._topics_for(tm, 1)[0]
        self._learn_work()
        self._get_to_know()
        self._ask_questions()
        self.quarter += 1

    def _learn_work(self) -> None:
        """Each person works on one of their team's topics and learns a few items."""
        rng = self.rng
        for p in self.active():
            tm = self.teams[p.team]
            if p.focus not in tm.focus or rng.random() < self.cfg.personal_change:
                p.focus = tm.focus[int(rng.integers(len(tm.focus)))]
            for _ in range(self.cfg.items_per_quarter):
                if tm.kind == "core":
                    client = CORE
                elif tm.kind == "service":
                    client = tm.client
                else:
                    client = tm.client if rng.random() < 0.8 else CORE
                p.items.add(self.space.item_id(p.focus, client, int(rng.integers(self.space.aspects))))
                p.worklog.append((self.quarter, p.team, p.focus, client))

    def _current_work(self, p: Person) -> list[tuple[int, int]]:
        return sorted({(t, c) for q, tm, t, c in p.worklog if q == self.quarter})

    def _learn_about(self, a: int, b: int, weight: float, all_work: bool) -> None:
        """a sees what b works on now, and b's roles."""
        work = self._current_work(self.people[b])
        if not work:
            return
        if not all_work:
            work = [work[int(self.rng.integers(len(work)))]]
        for t, c in work:
            self.mem[a].add(b, self.work_vec(t, c), weight)
        for role, owners in self.roles.items():
            if b in owners:
                self.role_known[a][role] = b

    def _get_to_know(self) -> None:
        cfg, rng = self.cfg, self.rng
        self.roles = self.roles_now()
        act = self.active()
        by_office: dict[int, list[Person]] = {}
        for p in act:
            by_office.setdefault(p.office, []).append(p)
        for tm in self.teams:                      # teammates: everything, every quarter
            members = self.team_members(tm.id)
            for a in members:
                for b in members:
                    if a.id != b.id:
                        self._learn_about(a.id, b.id, 1.0, all_work=True)
        for office, ps in by_office.items():       # office colleagues: sometimes
            p_office = min(1.0, cfg.office_mixing / len(ps))
            for a in ps:
                for b in ps:
                    if a.id != b.id and a.team != b.team and rng.random() < p_office:
                        self._learn_about(a.id, b.id, 0.5, all_work=False)
        ids = np.array([p.id for p in act])
        offices = np.array([p.office for p in act])
        other = offices[:, None] != offices[None, :]
        if cfg.cross_contacts is None:
            p_cross = cfg.cross_mixing
        else:                                      # v5: a fixed number of contacts, however large the network
            p_cross = cfg.cross_contacts / np.maximum(1, other.sum(axis=1))[:, None]
        cross = other & (rng.random((len(ids), len(ids))) < p_cross)
        for i, j in zip(*np.nonzero(cross)):       # other offices: rarely
            self._learn_about(int(ids[i]), int(ids[j]), 0.5, all_work=False)
        if ("leadership",) in self.roles:
            everyone = self.roles[("leadership",)]
            for p in act:                          # everybody knows who leadership is
                self.role_known[p.id][("leadership",)] = everyone[0]

    # -- asking around, the way the company actually worked -------------------

    def _ask_questions(self) -> None:
        cfg, rng = self.cfg, self.rng
        act = self.active()
        holders: dict[int, list[int]] = {}
        for p in act:
            for i in p.items:
                holders.setdefault(i, []).append(p.id)
        held = np.array(sorted(holders))
        for p in act:
            for _ in range(cfg.hist_questions):
                if rng.random() < 0.1:
                    self._ask_decision(p)
                    continue
                for _ in range(20):
                    i = int(rng.choice(held))
                    if p.id not in holders[i]:
                        break
                else:
                    continue
                topic, client, k = self.space.item_parts(i)
                vec = self.question_vec("content", topic, client, k, int(rng.integers(3)))
                self._ask_item(p.id, i, topic, vec, set(holders[i]))

    def _ask_item(self, a: int, item: int, topic: int, vec, holders: set[int]) -> None:
        cfg = self.cfg
        asked: set[int] = {a}
        referrals: list[int] = []
        referrers: list[int] = []
        for _ in range(cfg.hist_hops):
            b = None
            while referrals and b is None:
                c = referrals.pop()
                if c not in asked and not self.people[c].left:
                    b = c
            if b is None:
                top = self.mem[a].top(vec, 1, exclude=asked)
                if top and top[0][1] >= cfg.confident:
                    b = top[0][0]
                else:
                    b = self.most_senior_known(a, asked)
                    if b is None and top:
                        b = top[0][0]
            if b is None or self.people[b].left:
                return
            asked.add(b)
            if b in holders:
                self.mem[a].add(b, vec, 1.0)
                self.central.add(b, vec, 1.0)
                for r in set(referrers):
                    self.mem[r].add(b, vec, 0.5)
                self.receipts[b].setdefault(topic, set()).add(a)
                return
            self.mem[a].add(b, vec, 1.0, sign=-1)
            self.central.add(b, vec, 1.0, sign=-1)
            top = self.mem[b].top(vec, 3, exclude=asked)
            if top and top[0][1] >= cfg.confident:
                nxt = [c for c, s in reversed(top) if s >= cfg.confident]
            else:
                s = self.most_senior_known(b, asked)
                nxt = [s] if s is not None else [c for c, _ in reversed(top)]
            if nxt:
                referrers.append(b)
                referrals.extend(nxt)

    def _ask_decision(self, p: Person) -> None:
        """Decisions go to the owner if known, otherwise up the seniority line."""
        rng = self.rng
        roles = list(self.roles)
        role = roles[int(rng.integers(len(roles)))]
        owners = self.roles[role]
        asked = {p.id}
        b = self.role_known[p.id].get(role)
        for _ in range(self.cfg.hist_hops):
            if b is None or b in asked or self.people[b].left:
                b = self.most_senior_known(p.id, asked)
            if b is None:
                return
            asked.add(b)
            if b in owners:
                self.role_known[p.id][role] = b
                return
            b = self.role_known[b].get(role)

    # -- result ---------------------------------------------------------------

    def run(self) -> "History":
        """Quarters 0..quarters: the last step brings the company to its final size."""
        for _ in range(self.cfg.quarters + 1):
            self.step()
        return self

    def world(self) -> World:
        cfg = self.cfg
        act = self.active()
        mapping = {p.id: i for i, p in enumerate(act)}
        n = len(act)
        roles_old = self.roles_now()
        roles = {r: [mapping[x] for x in owners] for r, owners in roles_old.items()}
        person_roles = [[] for _ in range(n)]
        for r, owners in roles.items():
            for x in owners:
                person_roles[x].append(r)
        tenure = np.array([self.tenure(p) for p in act], dtype=float)
        order = np.lexsort((np.arange(n), tenure))[::-1]
        senior = np.zeros(n, dtype=bool)
        senior[order[: max(1, int(round(cfg.senior_frac * n)))]] = True
        declared = []
        for p in act:
            recent = {(t, c) for q, tm, t, c in p.worklog
                      if tm == p.team and q >= self.quarter - cfg.declared_quarters}
            declared.append(sorted(recent))
        holders: dict[int, list[int]] = {}
        for i, p in enumerate(act):
            for it in p.items:
                holders.setdefault(it, []).append(i)
        role_known = []
        for p in act:
            rk = {r: mapping[x] for r, x in self.role_known[p.id].items()
                  if x in mapping and r in roles and mapping[x] in roles[r]}
            role_known.append(rk)
        w = World(
            cfg=cfg, n=n,
            office=np.array([p.office for p in act]),
            team=np.array([p.team for p in act]),
            team_client=np.array([self.teams[p.team].client if self.teams[p.team].kind != "core" else CORE
                                  for p in act]),
            tenure=tenure, senior=senior,
            items=[set(p.items) for p in act], declared=declared,
            roles=roles, person_roles=person_roles, holders=holders,
            memory=[self.mem[p.id].remapped(mapping, n) for p in act],
            role_known=role_known,
            central_log=self.central.remapped(mapping, n),
            receipts=[{t: {mapping.get(s, -1 - s) for s in signers} for t, signers in self.receipts[p.id].items()}
                      for p in act],
            teams=self.teams, vec_item=self.vec_item, vec_work=self.vec_work,
            vec_role=self.vec_role, embedder_name=self.embedder_name, stats={},
            adversary=[""] * n, space=self.space,
        )
        w.stats = calibration_stats(w)
        return w


# --------------------------------------------------------------------------
# calibration checks
# --------------------------------------------------------------------------

def calibration_stats(w: World) -> dict:
    n = w.n
    known = [m.known_positive() for m in w.memory]
    cross, office = [], []
    for a in range(n):
        others_cross = [b for b in range(n) if w.office[b] != w.office[a]]
        others_office = [b for b in range(n) if w.office[b] == w.office[a] and b != a]
        if others_cross:
            cross.append(np.mean([b in known[a] for b in others_cross]))
        if others_office:
            office.append(np.mean([b in known[a] for b in others_office]))
    pairs = sum(len(s) for s in w.items)
    undeclared = 0
    for a in range(n):
        decl = set(w.declared[a])
        for it in w.items[a]:
            t, c, _ = w.item_parts(it)
            undeclared += (t, c) not in decl
    sen = w.senior
    breadth = np.array([len(k) for k in known])
    return {
        "people": n,
        "offices": int(len(set(w.office.tolist()))),
        "client_teams": int(sum(1 for t in w.teams if t.kind == "client")),
        "cross_office_awareness": float(np.mean(cross)) if cross else 0.0,
        "office_awareness": float(np.mean(office)) if office else 0.0,
        "undeclared_share": undeclared / max(1, pairs),
        "items_held_mean": float(np.mean([len(s) for s in w.items])),
        "holders_per_item_mean": float(np.mean([len(h) for h in w.holders.values()])),
        "single_holder_share": float(np.mean([len(h) == 1 for h in w.holders.values()])),
        "known_people_senior": float(breadth[sen].mean()),
        "known_people_others": float(breadth[~sen].mean()),
        "tenure_senior_quarters": float(w.tenure[sen].mean()),
        "tenure_others_quarters": float(w.tenure[~sen].mean()),
        "embedder": w.embedder_name,
    }


def build_world(cfg: CompanyConfig, use_cache: bool = True) -> World:
    fields = sorted(asdict(cfg).items())
    if cfg.tier == "network":                 # the history depends on the vectors, so does the cache
        from .topics import VECTOR_VERSION
        fields.append(("vector_version", VECTOR_VERSION))
    key = "world_" + hashlib.sha1(repr(fields).encode()).hexdigest()[:16]
    path = os.path.join(CACHE_DIR, key + ".pkl")
    if use_cache and os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    w = History(cfg).run().world()
    if use_cache:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(w, f)
    return w


def with_adversaries(w: World, stuffers: float = 0.10, wrong: float = 0.05, ring: int = 5,
                     seed: int = 0) -> World:
    """A copy of the world with dishonest people (DESIGN.md §8), drawn from
    non-seniors without roles, from their own random stream:
      stuffer  declares many topics it has not worked on (keyword stuffing)
      wrong    confidently answers questions in its declared topics, wrongly
      ring     colluders who sign receipts for each other and refer to each other
    """
    import copy
    rng = np.random.default_rng(seed + 7919)
    w2 = copy.copy(w)
    w2.declared = [list(d) for d in w.declared]
    w2.receipts = [{t: set(s) for t, s in r.items()} for r in w.receipts]
    w2.adversary = [""] * w.n
    pool = [a for a in range(w.n) if not w.senior[a] and not w.person_roles[a]]
    pool = list(rng.permutation(pool))
    n_stuff, n_wrong = int(round(stuffers * w.n)), int(round(wrong * w.n))
    for a in pool[:n_stuff]:
        w2.adversary[a] = "stuffer"
        client = int(w.team_client[a])
        for t in rng.choice(w.space.n_topics, size=12, replace=False):
            w2.declared[a].append((int(t), client))
    for a in pool[n_stuff:n_stuff + n_wrong]:
        w2.adversary[a] = "wrong"
    members = [int(a) for a in pool[n_stuff + n_wrong:n_stuff + n_wrong + ring]]
    for a in members:
        w2.adversary[a] = "ring"
        topics = rng.choice(w.space.n_topics, size=12, replace=False)
        for t in topics:                     # fake receipts from the other ring members
            w2.receipts[a].setdefault(int(t), set()).update(m for m in members if m != a)
            w2.declared[a].append((int(t), int(w.team_client[a])))
    w2.ring = members
    return w2
