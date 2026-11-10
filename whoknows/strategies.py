"""Routing strategies (DESIGN.md §6).

Each strategy answers five questions:
  start / next_candidate   whom does the asker contact next?
  suggestions              whom does a contacted person suggest?
  best_guess               whom does a contacted person name ("who knows X?")?
  observe / on_success /   what is learned from the outcome?
  on_timeout / on_wrong
What a contacted person can answer is ground truth and lives in sim.respond.

Everyone starts from the memory the company history gave them
(company.py); nobody is handed a perfect picture.
"""

from __future__ import annotations

import math

import numpy as np

from .memory import Memory
from .sim import Query, Sim


class Strategy:
    name = "base"
    load_aware = False
    uses_feedback = False
    lookup = False            # consults a shared service (index or log): costs lookup_delay
    central_log = False       # keeps one log of everyone's question outcomes
    learns = False
    confident = 0.5           # memory score at which people trust their own guess

    def setup(self, sim: Sim) -> None:
        w = sim.world
        self.mem = [m.copy() for m in w.memory]
        self.role_known = [dict(r) for r in w.role_known]
        self.load = [dict() for _ in range(sim.n)]

    # -- asker side ------------------------------------------------------------
    def start(self, sim: Sim, q: Query) -> None: ...
    def next_candidate(self, sim: Sim, q: Query) -> int | None: ...

    # -- recipient side --------------------------------------------------------
    def suggestions(self, sim: Sim, b: int, q: Query) -> list[tuple[int, float]]:
        return []

    def _ring(self, sim: Sim, b: int, q: Query) -> list[tuple[int, float]] | None:
        """A colluder sends askers to the other colluders."""
        if sim.world.adversary[b] != "ring":
            return None
        return [(m, 1.0) for m in getattr(sim.world, "ring", []) if m != b and m not in q.asked][:3]

    def best_guess(self, sim: Sim, b: int, q: Query) -> tuple[int, float] | None:
        top = self._top(b, q.vec, 1, exclude={b, q.asker})
        return top[0] if top else None

    # -- learning --------------------------------------------------------------
    def observe(self, sim: Sim, q: Query, b: int, kind: str, sugg, delay: float) -> None: ...

    def on_success(self, sim: Sim, q: Query, b: int) -> None:
        if q.qtype == "decision":
            self.role_known[q.asker][q.role] = b
        if q.qtype == "whom" and self.learns and q.named is not None:
            self._learn(q.asker, q.named, q.vec, 1.0)     # the answer *is* who knows

    def on_timeout(self, sim: Sim, q: Query, b: int) -> None: ...

    def on_wrong(self, sim: Sim, q: Query, b: int, vec) -> None:
        """A wrong answer was found out: count it against the answerer."""
        if self.learns:
            self._learn(q.asker, b, vec, 2.0, sign=-1)

    def handover(self, sim: Sim, leaver: int, successor: int) -> None:
        """The successor takes over the leaver's picture of who knows what."""
        self.mem[successor].absorb(self.mem[leaver])
        for role, who in self.role_known[leaver].items():
            self.role_known[successor].setdefault(role, who)

    # -- shared helpers ------------------------------------------------------
    def _top(self, agent: int, vec, k: int, exclude) -> list[tuple[int, float]]:
        return self.mem[agent].top(vec, k, exclude=exclude)

    def _learn(self, observer: int, target: int, vec, weight: float, sign: int = 1) -> None:
        self.mem[observer].add(target, vec, weight, sign)

    def _known_owner(self, who: int, q: Query, exclude) -> int | None:
        if q.qtype != "decision":
            return None
        owner = self.role_known[who].get(q.role)
        return owner if owner is not None and owner not in exclude else None

    def describe(self) -> dict:
        return {"name": self.name, "load_aware": self.load_aware, "central_log": self.central_log,
                "lookup": self.lookup}


# --------------------------------------------------------------------------
# S1 phonebook: ask the people you know; nobody refers you on
# --------------------------------------------------------------------------

class Phonebook(Strategy):
    name = "phonebook"

    def next_candidate(self, sim, q):
        excl = set(q.asked) | {q.asker}
        owner = self._known_owner(q.asker, q, excl)
        if owner is not None:
            return owner
        top = self._top(q.asker, q.vec, 1, exclude=excl)
        return top[0][0] if top else None


# --------------------------------------------------------------------------
# S2 ask the senior: the field study's pattern
# --------------------------------------------------------------------------

class AskSenior(Strategy):
    """Own best guess if confident; otherwise the most senior person you know.
    Seniors refer from their memory; others pass you up to a senior."""
    name = "ask_senior"
    uses_feedback = True
    learns = True

    def _most_senior(self, sim, who: int, exclude) -> int | None:
        known = [c for c in self.mem[who].known() if c not in exclude]
        if not known:
            return None
        return max(known, key=lambda c: (sim.world.tenure[c], -c))

    def start(self, sim, q):
        q.refq = []

    def next_candidate(self, sim, q):
        excl = set(q.asked) | {q.asker}
        owner = self._known_owner(q.asker, q, excl)
        if owner is not None:
            return owner
        while q.refq:                     # follow the latest referral first
            c = q.refq.pop()
            if c not in excl:
                return c
        top = self._top(q.asker, q.vec, 1, exclude=excl)
        if top and top[0][1] >= self.confident:
            return top[0][0]
        senior = self._most_senior(sim, q.asker, excl)
        if senior is not None:
            return senior
        return top[0][0] if top else None

    def suggestions(self, sim, b, q):
        excl = set(q.asked) | {q.asker, b}
        owner = self._known_owner(b, q, excl)
        if owner is not None:
            return [(owner, 1.0)]
        top = self._top(b, q.vec, sim.cfg.n_refer, exclude=excl)
        if sim.world.senior[b]:
            return top
        if top and top[0][1] >= self.confident:
            return top[:1]
        senior = self._most_senior(sim, b, excl)
        return [(senior, 1.0)] if senior is not None else top[:1]

    def observe(self, sim, q, b, kind, sugg, delay):
        if kind == "answer":
            self._learn(q.asker, b, q.vec, 1.0)
        elif kind in ("refer", "dontknow"):
            self._learn(q.asker, b, q.vec, 1.0, sign=-1)
        for c, _ in sorted(sugg, key=lambda x: x[1]):   # best suggestion popped first
            q.refq.append(c)

    def on_success(self, sim, q, b):
        super().on_success(sim, q, b)
        if sim.cfg.feedback:
            for r in set(q.referrers):
                self._learn(r, b, q.vec, sim.cfg.feedback_weight)


# --------------------------------------------------------------------------
# S3/S4 semantic search over declared skills and public roles
# --------------------------------------------------------------------------

class DeclaredSearch(Strategy):
    """A central index of declared skills (AgentFacts) plus a public role
    directory; cosine top-k. Contacted people answer or say they don't know."""
    name = "declared_search"
    lookup = True

    def setup(self, sim):
        super().setup(sim)
        w = sim.world
        rows, owners = [], []
        for a in range(sim.n):
            for t, c in w.declared[a]:
                rows.append(w.work_vec(t, c))
                owners.append(a)
        self.matrix = np.stack(rows)
        self.owners = np.array(owners)
        # rows are grouped by agent: where each agent's rows start (for a fast per-agent maximum)
        self.row_agents, self.row_starts = np.unique(self.owners, return_index=True)
        # answers given so far, starting from the history's receipts
        self.reputation = np.array([sum(len(s) for s in w.receipts[a].values()) for a in range(sim.n)],
                                   dtype=float)

    def ranked(self, sim, vec, exclude) -> list[tuple[int, float]]:
        cos = self.matrix @ vec
        best = np.full(sim.n, -np.inf)
        best[self.row_agents] = np.maximum.reduceat(cos, self.row_starts)   # each agent's best row
        for e in exclude:
            best[e] = -np.inf
        order = np.argsort(-best)
        order = order[np.isfinite(best[order])]
        return list(zip(order.tolist(), best[order].tolist()))

    def next_candidate(self, sim, q):
        excl = set(q.asked) | {q.asker}
        if q.qtype == "decision":          # the role directory names the owner
            owners = [o for o in sim.roles.get(q.role, []) if o not in excl]
            return owners[0] if owners else None
        ranked = self._order(sim, q, self.ranked(sim, q.vec, excl))
        return ranked[0][0] if ranked else None

    def _order(self, sim, q, ranked):
        return ranked

    def observe(self, sim, q, b, kind, sugg, delay):
        if kind == "answer":
            self.reputation[b] += 1


class DeclaredSearchTrust(DeclaredSearch):
    """NANDA Town's index.v1 rule: matches above a threshold sorted by reputation."""
    name = "declared_search_trust"
    threshold = 0.6

    def _order(self, sim, q, ranked):
        match = [(c, s) for c, s in ranked if s >= self.threshold]
        rest = [(c, s) for c, s in ranked if s < self.threshold]
        match.sort(key=lambda cs: (-self.reputation[cs[0]], -cs[1]))
        return match + rest


# --------------------------------------------------------------------------
# S5-S9 learned routing: who-knows-what from observed outcomes
# --------------------------------------------------------------------------

class Learned(Strategy):
    name = "learned_local"
    uses_feedback = True
    learns = True
    ref_trust = 0.9           # a referral is a strong but not certain signal

    def setup(self, sim):
        super().setup(sim)
        w = sim.world
        self.shared = w.central_log.copy() if self.central_log else None
        if self.central_log:      # the log also knows every owner anyone found
            union = {}
            for rk in self.role_known:
                union.update(rk)
            self.role_known = [dict(union) for _ in range(sim.n)]

    # -- load estimates (only used when load-aware) ------------------------------
    def _load_est(self, sim, observer: int, c: int) -> float:
        v = self.load[observer].get(c)
        if v is None:
            return 0.0
        val, t = v
        return val * math.exp(-(sim.now - t) / sim.cfg.load_tau)

    def _note_load(self, sim, observer: int, c: int, value: float) -> None:
        old = self._load_est(sim, observer, c)
        self.load[observer][c] = (0.5 * old + 0.5 * value, sim.now)

    def _adjusted(self, sim, observer: int, cands: dict[int, float]) -> dict[int, float]:
        if not self.load_aware:
            return cands
        lam = sim.cfg.load_lambda
        return {c: s - lam * self._load_est(sim, observer, c) for c, s in cands.items()}

    # -- memory --------------------------------------------------------------
    def _top(self, agent, vec, k, exclude):
        if self.shared is None:
            return self.mem[agent].top(vec, k, exclude=exclude)
        sc = self.mem[agent].scores(vec)
        for t, v in self.shared.scores(vec).items():
            sc[t] = max(sc.get(t, -np.inf), v)
        ranked = sorted(((v, t) for t, v in sc.items() if t not in exclude), reverse=True)
        return [(t, v) for v, t in ranked[:k]]

    def _learn(self, observer, target, vec, weight, sign=1):
        (self.shared if self.shared is not None else self.mem[observer]).add(target, vec, weight, sign)

    def memory_stats(self):
        if self.shared is not None:
            return {"central_records": self.shared.records, "max_local_records": 0}
        return {"central_records": 0, "max_local_records": max(m.records for m in self.mem)}

    # -- protocol --------------------------------------------------------------
    def _candidates(self, sim, q) -> dict[int, float]:
        """Who might know, for what the asker needs right now."""
        return dict(self._top(q.asker, q.vec, 30, exclude={q.asker}))

    def start(self, sim, q):
        q.frontier = self._candidates(sim, q)
        q.frontier_need = q.need

    def next_candidate(self, sim, q):
        excl = set(q.asked) | {q.asker}
        owner = self._known_owner(q.asker, q, excl)
        if owner is not None:
            return owner
        if q.frontier_need != q.need:     # a partial answer changed what is needed
            fresh = self._candidates(sim, q)
            for c, s in q.frontier.items():
                fresh[c] = max(fresh.get(c, -np.inf), s * 0.5)
            q.frontier, q.frontier_need = fresh, q.need
        open_ = {c: s for c, s in q.frontier.items() if c not in excl}
        if not open_:
            return None
        adj = self._adjusted(sim, q.asker, open_)
        if not self.load_aware:
            return max(adj, key=lambda c: (adj[c], -c))
        best = max(adj.values())
        near = [c for c, s in adj.items() if s >= best - sim.cfg.near_best]
        logits = np.array([adj[c] for c in near]) / sim.cfg.softmax_temp
        p = np.exp(logits - logits.max())
        return int(sim.rng.choice(near, p=p / p.sum()))

    def suggestions(self, sim, b, q):
        excl = set(q.asked) | {q.asker, b}
        owner = self._known_owner(b, q, excl)
        if owner is not None:
            return [(owner, 1.0)]
        cands = dict(self._top(b, q.vec, sim.cfg.n_refer * 3, exclude=excl))
        if not cands:
            return []
        adj = self._adjusted(sim, b, cands)
        return sorted(adj.items(), key=lambda cs: -cs[1])[: sim.cfg.n_refer]

    def observe(self, sim, q, b, kind, sugg, delay):
        if kind == "answer":
            self._learn(q.asker, b, q.vec, 1.0)
        elif kind in ("refer", "dontknow"):
            self._learn(q.asker, b, q.vec, 1.0, sign=-1)
        if self.load_aware:
            # a BUSY reply or a refusal ("rate limited") says: this one is overloaded
            seen = sim.cfg.busy_threshold * 1.5 if kind in ("busy", "rejected") else delay
            self._note_load(sim, q.asker, b, seen)
        for c, s in sugg:
            if c != q.asker and c not in q.asked:
                q.frontier[c] = max(q.frontier.get(c, -np.inf), self.ref_trust * s)

    def on_success(self, sim, q, b):
        super().on_success(sim, q, b)
        if sim.cfg.feedback and not self.central_log:
            for r in set(q.referrers):
                self.mem[r].add(b, q.vec, sim.cfg.feedback_weight)

    def on_timeout(self, sim, q, b):
        if self.load_aware:
            self._note_load(sim, q.asker, b, sim.cfg.patience)


class LearnedCentral(Learned):
    name = "learned_central"
    central_log = True
    lookup = True
    uses_feedback = False


class LearnedLocalLoadAware(Learned):
    name = "learned_local_loadaware"
    load_aware = True


class HybridSearchLearned(Learned):
    """Declared search (and the role directory) for the first hop, then
    load-aware learned referrals for everything the declarations miss."""
    name = "hybrid_search_learned"
    load_aware = True
    lookup = True
    search_trust = 0.6        # a declaration is weaker evidence than an observation
    search_k = 5

    def setup(self, sim):
        super().setup(sim)
        self.index = DeclaredSearch()
        self.index.setup(sim)

    def _candidates(self, sim, q):
        cands = super()._candidates(sim, q)
        for c, s in self.index.ranked(sim, q.vec, {q.asker})[: self.search_k]:
            cands[c] = max(cands.get(c, -np.inf), self.search_trust * s)
        return cands

    def next_candidate(self, sim, q):
        if q.qtype == "decision" and q.role not in self.role_known[q.asker]:
            owners = sim.roles.get(q.role, [])
            if owners:
                self.role_known[q.asker][q.role] = owners[0]
        return super().next_candidate(sim, q)


class AttestedSearch(HybridSearchLearned):
    """Hybrid, re-ranked by signed track records: per person and topic, the
    number of distinct people who signed "answered my question". Coarse and
    public; nobody publishes who asked what."""
    name = "attested_search"
    weight = 0.3              # boost for a strong track record
    saturation = 10           # signers at which the boost is ~ full

    def setup(self, sim):
        super().setup(sim)
        self.receipts = [{t: set(s) for t, s in r.items()} for r in sim.world.receipts]

    def _record(self, a: int, topic: int) -> float:
        n = len(self.receipts[a].get(topic, ()))
        return self.weight * math.log1p(n) / math.log1p(self.saturation)

    def _candidates(self, sim, q):
        cands = super()._candidates(sim, q)
        return {c: s + self._record(c, q.topic) for c, s in cands.items()}

    def on_success(self, sim, q, b):
        super().on_success(sim, q, b)
        for helper, _, _ in q.helpers:    # the asker signs a receipt (it believes the answer)
            self.receipts[helper].setdefault(q.topic, set()).add(q.asker)
        if q.qtype == "decision":
            self.receipts[b].setdefault(q.topic, set()).add(q.asker)

    def on_wrong(self, sim, q, b, vec):
        super().on_wrong(sim, q, b, vec)
        self.receipts[b].get(q.topic, set()).discard(q.asker)   # the receipt is revoked


# --------------------------------------------------------------------------
# control
# --------------------------------------------------------------------------

class RandomWalk(Strategy):
    name = "random_walk"

    def start(self, sim, q):
        contacts = sorted(self.mem[q.asker].known())
        sim.rng.shuffle(contacts)
        q.refq = contacts

    def next_candidate(self, sim, q):
        while q.refq:
            c = q.refq.pop()
            if c not in q.asked and c != q.asker:
                return c
        return None

    def suggestions(self, sim, b, q):
        contacts = [c for c in self.mem[b].known() if c not in q.asked and c != q.asker]
        if not contacts:
            return []
        return [(int(sim.rng.choice(contacts)), 0.0)]

    def observe(self, sim, q, b, kind, sugg, delay):
        for c, _ in sugg:
            q.refq.append(c)


STRATEGIES = {cls.name: cls for cls in [
    Phonebook, AskSenior, DeclaredSearch, DeclaredSearchTrust, LearnedCentral, Learned,
    LearnedLocalLoadAware, HybridSearchLearned, AttestedSearch, RandomWalk,
]}

MAIN = ["phonebook", "ask_senior", "declared_search", "declared_search_trust",
        "learned_central", "learned_local", "learned_local_loadaware",
        "hybrid_search_learned", "attested_search"]

SWEEP = ["ask_senior", "declared_search", "learned_central", "learned_local",
         "learned_local_loadaware", "hybrid_search_learned", "attested_search"]


def make(name: str) -> Strategy:
    return STRATEGIES[name]()
