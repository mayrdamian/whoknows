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


class Memory:
    def __init__(self, n_agents: int, dim: int, max_protos: int = 6,
                 merge_cos: float = 0.8, conf_c: float = 1.0,
                 gamma: float = 1.0, neg_floor: float = 0.6):
        self.n = n_agents
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

    def __getstate__(self):
        """Pickle only the filled part (worlds are cached on disk)."""
        state = dict(self.__dict__)
        n = max(1, self._size)
        for name in ("_P", "_w", "_owner", "_sign"):
            state[name] = getattr(self, name)[:n].copy()
        return state

    def copy(self) -> "Memory":
        new = Memory.__new__(Memory)
        new.__dict__.update(self.__dict__)
        for name in ("_P", "_w", "_owner", "_sign"):
            setattr(new, name, getattr(self, name).copy())
        return new

    def remapped(self, mapping: dict[int, int], n_new: int) -> "Memory":
        """Keep only prototypes about agents in `mapping` (old id -> new id)."""
        new = Memory(n_new, self.dim, self.max_protos, self.merge_cos, self.conf_c,
                     self.gamma, self.neg_floor)
        n = self._size
        keep = [i for i in range(n) if int(self._owner[i]) in mapping]
        while len(new._w) < len(keep):
            new._grow()
        for j, i in enumerate(keep):
            new._P[j] = self._P[i]
            new._w[j] = self._w[i]
            new._owner[j] = mapping[int(self._owner[i])]
            new._sign[j] = self._sign[i]
        new._size = len(keep)
        new.records = self.records
        return new

    def absorb(self, other: "Memory", weight: float = 1.0) -> None:
        """Take over another memory's prototypes (a handover), scaled by `weight`."""
        for i in range(other._size):
            self.add(int(other._owner[i]), other._P[i], float(other._w[i]) * weight,
                     int(other._sign[i]))

    def known_positive(self) -> set[int]:
        """Agents this memory holds positive evidence about (knows what they do)."""
        n = self._size
        live = self._owner[:n][self._sign[:n] > 0]
        return set(int(x) for x in np.unique(live))

    def known(self) -> set[int]:
        live = self._owner[: self._size]
        return set(int(x) for x in np.unique(live[live >= 0]))

    def add(self, target: int, vec: np.ndarray, weight: float = 1.0,
            sign: int = 1) -> None:
        """Merge an observation into the nearest prototype of the same
        target and sign, or open a new prototype."""
        self.records += 1
        n = self._size
        mask = (self._owner[:n] == target) & (self._sign[:n] == sign)
        idx = np.flatnonzero(mask)
        if len(idx):
            P = self._P[idx]
            norms = np.linalg.norm(P, axis=1)
            cos = (P @ vec) / np.where(norms == 0, 1, norms)
            j = int(np.argmax(cos))
            if cos[j] >= self.merge_cos or len(idx) >= self.max_protos:
                k = int(idx[j])
                w = self._w[k]
                self._P[k] = (self._P[k] * w + vec * weight) / (w + weight)
                self._w[k] = w + weight
                return
        if self._size == len(self._w):
            self._grow()
        k = self._size
        self._P[k] = vec
        self._w[k] = weight
        self._owner[k] = target
        self._sign[k] = sign
        self._size += 1

    # -- scoring -------------------------------------------------------------

    def scores(self, q: np.ndarray) -> dict[int, float]:
        """Score every agent this memory knows about."""
        n = self._size
        if n == 0:
            return {}
        P = self._P[:n]
        norms = np.linalg.norm(P, axis=1)
        cos = (P @ q) / np.where(norms == 0, 1, norms)
        conf = self._w[:n] / (self._w[:n] + self.conf_c)
        val = cos * conf
        owner = self._owner[:n]
        sign = self._sign[:n]
        pos = np.full(self.n, -np.inf)
        neg = np.zeros(self.n)
        pm = sign > 0
        np.maximum.at(pos, owner[pm], val[pm])
        nm = sign < 0
        if nm.any():
            # A miss only counts against questions close to the one missed.
            nval = conf[nm] * np.maximum(0.0, cos[nm] - self.neg_floor) / (1 - self.neg_floor)
            np.maximum.at(neg, owner[nm], nval)
        out = {}
        for t in np.flatnonzero(np.isfinite(pos)):
            out[int(t)] = float(pos[t] - self.gamma * neg[t])
        return out

    def top(self, q: np.ndarray, k: int, exclude: set[int] | frozenset = frozenset()
            ) -> list[tuple[int, float]]:
        sc = self.scores(q)
        ranked = sorted(((s, t) for t, s in sc.items() if t not in exclude), reverse=True)
        return [(t, s) for s, t in ranked[:k]]
