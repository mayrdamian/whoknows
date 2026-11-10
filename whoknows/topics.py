"""The topic space: what there is to know (DESIGN.md §14.2).

A piece of knowledge is an *item* (topic, lane, aspect):

    topic   an area of work, e.g. "refunds" or "user access"; topics are grouped
            into domains (v3: 48 topics in 8 domains)
    lane    the setting the work is done in: one of several platforms, or the
            shared lane that every platform uses (v3: one of 16 client systems,
            or the core platform)
    aspect  one detail of that work (v3: 6 per topic and lane)

Knowing the same topic and aspect in another lane is help from similar work
(an "analogue"): it is right only some of the time. This is v3's structure
with the company taken out, so a company is one setting of the space and an
open network of agents is another, larger one.

The v3 company uses sentence embeddings of generated text (company.py). The
open network uses `TopicVectors`: vectors built from random components, with
weights chosen so that similarities match those measured on v3's text vectors
(DESIGN.md §14.2). They need no text and scale to any number of topics.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np

CORE = -1                       # the shared lane (v3: the core platform)
VECTOR_VERSION = 4              # bump when TopicVectors changes: cached worlds depend on it
QTYPES = ("content", "whom", "technical", "decision")


@dataclass(frozen=True)
class Space:
    domains: int
    topics_per_domain: int
    lanes: int                  # platform lanes; the shared lane comes on top
    aspects: int

    @property
    def n_topics(self) -> int:
        return self.domains * self.topics_per_domain

    @property
    def n_systems(self) -> int:
        """Lanes including the shared one."""
        return self.lanes + 1

    @property
    def n_items(self) -> int:
        return self.n_topics * self.n_systems * self.aspects

    def item_id(self, topic: int, lane: int, k: int) -> int:
        system = self.lanes if lane == CORE else lane
        return (topic * self.n_systems + system) * self.aspects + k

    def item_parts(self, item: int) -> tuple[int, int, int]:
        """item id -> (topic, lane, aspect); lane -1 = the shared lane."""
        k = item % self.aspects
        rest = item // self.aspects
        system = rest % self.n_systems
        topic = rest // self.n_systems
        return topic, (CORE if system == self.lanes else system), k

    def domain(self, topic: int) -> int:
        return topic // self.topics_per_domain

    def system_index(self, lane: int) -> int:
        return self.lanes if lane == CORE else lane


def _unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n == 0, 1, n)


class TopicVectors:
    """Vectors for a topic space, built from random components.

    item(t, lane, k) = unit( 0.48 domain + 0.74 topic + 0.37 topic-in-lane + 0.27 aspect-of-topic )

    Two items of the same topic share the domain and topic parts; analogues
    (same topic and aspect, another lane) also share the aspect part. The
    weights reproduce the similarities of v3's text vectors (question to its
    own item 0.95, to an analogue 0.81, to another aspect 0.88, to another
    topic of the same domain about 0.2, to a random item about 0).

    A question is its item plus a part for the kind of question and a part
    for the wording, drawn from its own seed so that the same question always
    gets the same vector. How far a question sits from its item depends on its
    kind, as in v3's text: "who knows about X?" and "X is blocked" questions
    are worded further from the work they are about than "how do I X?".
    """

    W_DOMAIN, W_TOPIC, W_LANE, W_ASPECT = 0.29, 0.83, 0.38, 0.27
    W_DECIDES = 0.8
    # Items and questions in the shared lane are worded with words of their own
    # ("on the core platform") that descriptions of the work do not use; in
    # v3's text a core question is only 0.64 similar to the core work it is about.
    W_SHARED_WORDING = 1.0
    # per kind of question: size of the kind + wording part, and how much it varies
    # (fitted to v3's text: similarity to the own item 0.95 / 0.76 / 0.83 for content / whom / technical)
    QUESTION_OFFSET = {"content": (0.33, 0.2), "whom": (0.85, 0.7), "technical": (0.62, 0.4),
                       "decision": (0.33, 0.2)}

    def __init__(self, space: Space, dim: int = 64, seed: int = 7,
                 lane_spread: float = 0.45, aspect_spread: float = 0.45, lane_shared: float = 1.0):
        self.space = space
        self.dim = dim
        self.seed = seed
        rng = np.random.default_rng(seed)

        def parts(n: int) -> np.ndarray:
            return _unit(rng.normal(size=(n, dim)))

        s = space
        self.D = parts(s.domains)
        self.T = parts(s.n_topics)
        # the lane part: partly the same for every topic in that lane (v3: the client's name)
        own_lane = parts(s.n_topics * s.n_systems).reshape(s.n_topics, s.n_systems, dim)
        shared_lane = parts(s.n_systems)
        self.TL = _unit(np.sqrt(1 - lane_shared) * own_lane + np.sqrt(lane_shared) * shared_lane[None, :, :])
        self.K = parts(s.n_topics * s.aspects).reshape(s.n_topics, s.aspects, dim)
        self.Q = dict(zip(QTYPES, parts(len(QTYPES))))
        self.R = parts(1)[0]                       # "decides on ..."
        self.LEADERSHIP = parts(1)[0]
        # Some lanes differ more from the others than some do, and some aspects
        # more than others: weights vary around their means (log-normal), which
        # gives the spread of similarities seen in v3's text vectors.
        self.w_lane = self.W_LANE * np.exp(lane_spread * rng.normal(size=(s.n_topics, s.n_systems))
                                           - lane_spread ** 2 / 2)
        self.w_aspect = self.W_ASPECT * np.exp(aspect_spread * rng.normal(size=(s.n_topics, s.aspects))
                                               - aspect_spread ** 2 / 2)
        self.SW = parts(1)[0]
        self.w_shared_wording = self.W_SHARED_WORDING * np.exp(aspect_spread * rng.normal(size=s.n_topics)
                                                               - aspect_spread ** 2 / 2)
        topic_domain = np.repeat(np.arange(s.domains), s.topics_per_domain)
        base = self.W_DOMAIN * self.D[topic_domain] + self.W_TOPIC * self.T      # (topics, dim)
        self.work = _unit(base[:, None, :] + self.w_lane[:, :, None] * self.TL)   # (topics, systems, dim)
        self._base = base

    # -- the three kinds of vector the simulator uses -----------------------------

    def work_vec(self, topic: int, lane: int) -> np.ndarray:
        return self.work[topic, self.space.system_index(lane)]

    def item_vec(self, item: int) -> np.ndarray:
        t, lane, k = self.space.item_parts(item)
        sys = self.space.system_index(lane)
        v = self._base[t] + self.w_lane[t, sys] * self.TL[t, sys] + self.w_aspect[t, k] * self.K[t, k]
        if lane == CORE:
            v = _unit(v) + self.w_shared_wording[t] * self.SW
        return _unit(v)

    def item_matrix(self) -> np.ndarray:
        """All item vectors in item-id order (only for small spaces)."""
        return np.stack([self.item_vec(i) for i in range(self.space.n_items)])

    def role_vec(self, role: tuple) -> np.ndarray:
        if role[0] == "leadership":
            return _unit(self.LEADERSHIP + self.R)
        if role[0] == "lead":                     # whoever decides for a platform lane
            return _unit(self.work[:, role[1]].mean(axis=0) + self.R)
        return _unit(self.D[role[1]] + self.R)    # ("owner", domain): the shared lane of a domain

    @lru_cache(maxsize=200_000)
    def question_vec(self, qtype: str, topic: int, lane, k: int, variant: int) -> np.ndarray:
        if qtype == "decision":
            if lane is None:                      # company-wide
                base = _unit(self.D[self.space.domain(topic)] + self.LEADERSHIP)
            else:
                base = self.work_vec(topic, lane)
            v = _unit(base + self.W_DECIDES * self.R)
            lane_key = -2 if lane is None else lane
        else:
            v = self.item_vec(self.space.item_id(topic, lane, k))
            lane_key = lane
        kind = QTYPES.index(qtype)
        draw = np.random.default_rng((self.seed, 101, kind, topic, lane_key + 2, k, variant))
        noise = _unit(draw.normal(size=self.dim))
        size, spread = self.QUESTION_OFFSET[qtype]
        m = size * np.exp(spread * draw.normal() - spread ** 2 / 2) / np.sqrt(2)
        return _unit(v + m * self.Q[qtype] + m * noise)
