"""Who-knows-what memory.

A memory holds, for each other agent it knows about, a few *prototypes*:
vectors with a weight and a sign. Positive prototypes come from observed
answers ("B answered a question like this") or from seeing what B works on;
negative ones from observed misses ("B did not know this"). In v3 nothing is
handed out at the start: every prototype comes from the simulated company
history (company.py).

Score of agent B for a query q:

    pos(B) = max_k  cos(q, p_k) * conf(w_k)                                   over positive prototypes
    neg(B) = max_k  conf(w_k) * relu(cos(q, n_k) - neg_floor) / (1 - neg_floor)  over negative prototypes
    score  = pos(B) - gamma * neg(B)

(A miss only counts against questions closer to it than neg_floor. Agents with
only negative prototypes get no score. This docstring was corrected in v4 to
match the code; the code itself is unchanged since v3.)

conf(w) = w / (w + c) grows with evidence. Only *observed outcomes* are
learned; hearsay (a referral) is used for the next step but never stored.
That mirrors NANDA Town's data-facts rule: one observer, one subject.
"""

from __future__ import annotations

import numpy as np


def without(ids: np.ndarray, exclude) -> np.ndarray:
    """Mask that drops `exclude` from the ascending array `ids` (exclusion sets are small)."""
    keep = np.ones(len(ids), dtype=bool)
    if exclude and len(ids):
        excl = np.fromiter(exclude, dtype=np.int64, count=len(exclude))
        where = np.minimum(np.searchsorted(ids, excl), len(ids) - 1)
        keep[where[ids[where] == excl]] = False
    return keep


def _run_starts(sorted_ids: np.ndarray) -> np.ndarray:
    """Where each run of equal values starts in a sorted array."""
    if len(sorted_ids) == 0:
        return np.zeros(0, dtype=np.int64)
    return np.flatnonzero(np.r_[True, sorted_ids[1:] != sorted_ids[:-1]])


class Memory:
    def __init__(self, n_agents: int, dim: int, max_protos: int = 6,
                 merge_cos: float = 0.8, conf_c: float = 1.0,
                 gamma: float = 1.0, neg_floor: float = 0.6, limit: int | None = None):
        self.n = n_agents
        # v6: remember at most `limit` agents; when a new one comes in, the agent
        # observed longest ago is forgotten (None: no limit, as in v3-v5)
        self.limit = limit
        self._clock = 0
        self._last_seen: dict[int, int] = {}
        self.dim = dim
        self.max_protos = max_protos
        self.merge_cos = merge_cos
        self.conf_c = conf_c
        self.gamma = gamma
        self.neg_floor = neg_floor
        cap = 64
        self._P = np.zeros((cap, dim), dtype=np.float32)
        self._w = np.zeros(cap)
        self._owner = np.full(cap, -1, dtype=np.int64)
        self._sign = np.zeros(cap, dtype=np.int8)
        self._size = 0
        self.records = 0  # number of observations stored (privacy proxy)

    # -- storage -----------------------------------------------------------

    def _grow(self):
        cap = len(self._w) * 2
        for name in ("_P", "_w", "_owner", "_sign"):
            old = getattr(self, name)
            if name == "_P":
                new = np.zeros((cap, self.dim), dtype=np.float32)
            elif name == "_owner":
                new = np.full(cap, -1, dtype=np.int64)
            else:
                new = np.zeros(cap, dtype=old.dtype)
            new[: len(old)] = old
            setattr(self, name, new)
        self._norms = None                   # caches sized by capacity: rebuilt on demand

    def __getstate__(self):
        """Pickle only the filled part (worlds are cached on disk)."""
        state = dict(self.__dict__)
        n = max(1, self._size)
        for name in ("_P", "_w", "_owner", "_sign"):
            state[name] = getattr(self, name)[:n].copy()
        for cache in ("_known", "_slots", "_norms", "_groups"):   # caches, rebuilt on demand
            state.pop(cache, None)
        return state

    def copy(self) -> "Memory":
        new = Memory.__new__(Memory)
        new.__dict__.update(self.__dict__)
        for name in ("_P", "_w", "_owner", "_sign"):
            setattr(new, name, getattr(self, name).copy())
        if hasattr(self, "_last_seen"):
            new._last_seen = dict(self._last_seen)
        new._slots = None
        new._norms = getattr(self, "_norms", None)
        if new._norms is not None:
            new._norms = new._norms.copy()
        new._groups = getattr(self, "_groups", None)      # read-only arrays, safe to share
        return new

    def remapped(self, mapping: dict[int, int], n_new: int) -> "Memory":
        """Keep only prototypes about agents in `mapping` (old id -> new id)."""
        new = Memory(n_new, self.dim, self.max_protos, self.merge_cos, self.conf_c,
                     self.gamma, self.neg_floor, getattr(self, "limit", None))
        if new.limit is not None:
            new._clock = self._clock
            new._last_seen = {mapping[a]: c for a, c in self._last_seen.items() if a in mapping}
        n = self._size
        new_owner = np.array([mapping.get(int(o), -1) for o in self._owner[:n]], dtype=np.int64)
        keep = np.flatnonzero(new_owner >= 0)
        cap = max(64, len(keep))           # v6: no spare room (saves memory in large networks)
        new._P = np.zeros((cap, self.dim), dtype=np.float32)
        new._w = np.zeros(cap)
        new._owner = np.full(cap, -1, dtype=np.int64)
        new._sign = np.zeros(cap, dtype=np.int8)
        m = len(keep)
        new._P[:m] = self._P[keep]
        new._w[:m] = self._w[keep]
        new._owner[:m] = new_owner[keep]
        new._sign[:m] = self._sign[keep]
        new._size = m
        new.records = self.records
        return new

    def _forget(self, agent: int) -> None:
        """Drop everything remembered about one agent (bounded memory)."""
        n = self._size
        keep = self._owner[:n] != agent
        m = int(keep.sum())
        for name in ("_P", "_w", "_owner", "_sign"):
            arr = getattr(self, name)
            arr[:m] = arr[:n][keep]
        self._owner[m:n] = -1
        self._size = m
        self._slots = self._norms = self._groups = None
        del self._last_seen[agent]

    def absorb(self, other: "Memory", weight: float = 1.0) -> None:
        """Take over another memory's prototypes (a handover), scaled by `weight`."""
        for i in range(other._size):
            self.add(int(other._owner[i]), other._P[i], float(other._w[i]) * weight,
                     int(other._sign[i]))

    def _slots_of(self, target: int, sign: int) -> list[int]:
        """Positions of the prototypes about `target` with `sign`, ascending
        (an index, so that adding to a large memory such as the central log
        does not scan every prototype)."""
        slots = getattr(self, "_slots", None)
        if slots is None:
            slots = self._slots = {}
            for i in range(self._size):
                slots.setdefault((int(self._owner[i]), int(self._sign[i])), []).append(i)
        return slots.setdefault((target, sign), [])

    def known_positive(self) -> set[int]:
        """Agents this memory holds positive evidence about (knows what they do)."""
        n = self._size
        live = self._owner[:n][self._sign[:n] > 0]
        return set(int(x) for x in np.unique(live))

    def known_ids(self) -> np.ndarray:
        """Every agent this memory holds anything about, ascending (cached until the next add)."""
        cached = getattr(self, "_known", None)
        if cached is None:
            live = self._owner[: self._size]
            cached = self._known = np.unique(live[live >= 0])
        return cached

    def known(self) -> frozenset[int]:
        return frozenset(self.known_ids().tolist())

    def add(self, target: int, vec: np.ndarray, weight: float = 1.0,
            sign: int = 1) -> None:
        """Merge an observation into the nearest prototype of the same
        target and sign, or open a new prototype."""
        self.records += 1
        self._known = None
        if getattr(self, "limit", None) is not None:
            if target not in self._last_seen and len(self._last_seen) >= self.limit:
                self._forget(min(self._last_seen, key=self._last_seen.get))
            self._clock += 1
            self._last_seen[target] = self._clock
        slots = self._slots_of(target, sign)
        if slots:
            idx = np.array(slots)
            P = self._P[idx]
            norms = np.linalg.norm(P, axis=1)
            cos = (P @ vec) / np.where(norms == 0, 1, norms)
            j = int(np.argmax(cos))
            if cos[j] >= self.merge_cos or len(idx) >= self.max_protos:
                k = int(idx[j])
                w = self._w[k]
                self._P[k] = (self._P[k] * w + vec * weight) / (w + weight)
                self._w[k] = w + weight
                self._update_norm(k)
                return
        if self._size == len(self._w):
            self._grow()
        k = self._size
        self._P[k] = vec
        self._w[k] = weight
        self._owner[k] = target
        self._sign[k] = sign
        self._size += 1
        slots.append(k)
        self._update_norm(k)
        self._groups = None                  # a new prototype: owners and signs changed

    # -- scoring -------------------------------------------------------------

    def _update_norm(self, k: int) -> None:
        """Keep the cached length of prototype k current (same computation as
        the full recomputation, so scores stay bit-identical)."""
        norms = getattr(self, "_norms", None)
        if norms is not None:
            norms[k] = np.linalg.norm(self._P[k:k + 1], axis=1)[0]

    def _prototype_norms(self) -> np.ndarray:
        norms = getattr(self, "_norms", None)
        if norms is None:
            norms = self._norms = np.zeros(len(self._w), dtype=self._P.dtype)
            norms[: self._size] = np.linalg.norm(self._P[: self._size], axis=1)
        return norms[: self._size]

    def _grouping(self):
        """Which agents have positive prototypes, and where each prototype's
        agent sits in that list (cached until a prototype is added or dropped)."""
        g = getattr(self, "_groups", None)
        if g is None:
            n = self._size
            owner, sign = self._owner[:n], self._sign[:n]
            pm, nm = sign > 0, sign < 0
            agents, slot = np.unique(owner[pm], return_inverse=True)
            # positive prototypes sorted by agent, and where each agent's run starts
            pos_order = np.argsort(slot, kind="stable")
            pos_starts = _run_starts(slot[pos_order])
            neg = None
            if nm.any() and len(agents):
                where = np.minimum(np.searchsorted(agents, owner[nm]), len(agents) - 1)
                has_positive = agents[where] == owner[nm]     # misses of agents without positives are ignored
                target = where[has_positive]
                neg_order = np.argsort(target, kind="stable")
                neg_starts = _run_starts(target[neg_order])
                neg = (has_positive, neg_order, neg_starts, target[neg_order][neg_starts])
            g = self._groups = (pm, nm, agents, pos_order, pos_starts, neg)
        return g

    def score_arrays(self, q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """The agents with positive evidence (ascending ids) and their scores for q.

        Arrays are sized by the agents this memory knows, not by the whole
        network, so a score costs the same in a network of 100 or 100,000."""
        n = self._size
        if n == 0:
            return np.zeros(0, dtype=np.int64), np.zeros(0)
        P = self._P[:n]
        norms = self._prototype_norms()
        cos = (P @ q) / np.where(norms == 0, 1, norms)
        conf = self._w[:n] / (self._w[:n] + self.conf_c)
        val = cos * conf
        pm, nm, agents, pos_order, pos_starts, negs = self._grouping()
        if len(agents) == 0:
            return agents, np.zeros(0)
        # each agent's best positive prototype (a maximum per run of the sorted prototypes)
        pos = np.maximum.reduceat(val[pm][pos_order], pos_starts)
        neg = np.zeros(len(agents))
        if negs is not None:
            # A miss only counts against questions close to the one missed.
            has_positive, neg_order, neg_starts, neg_agents = negs
            nval = conf[nm] * np.maximum(0.0, cos[nm] - self.neg_floor) / (1 - self.neg_floor)
            neg[neg_agents] = np.maximum.reduceat(nval[has_positive][neg_order], neg_starts)
        return agents, pos - self.gamma * neg

    def scores(self, q: np.ndarray) -> dict[int, float]:
        """Score every agent this memory knows about."""
        agents, score = self.score_arrays(q)
        return dict(zip(agents.tolist(), score.tolist()))

    def top(self, q: np.ndarray, k: int, exclude: set[int] | frozenset = frozenset()
            ) -> list[tuple[int, float]]:
        """The k best agents, best first; ties go to the higher id."""
        agents, score = self.score_arrays(q)
        if exclude:
            keep = without(agents, exclude)
            agents, score = agents[keep], score[keep]
        order = np.lexsort((-agents, -score))[:k]
        return list(zip(agents[order].tolist(), score[order].tolist()))
