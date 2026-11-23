"""The measured period: two working weeks of people asking around
(DESIGN.md §5).

One query = one question an agent cannot answer itself: content, whom to
ask, a technical issue (two pieces of knowledge), or a decision (only its
owner can make it). The asker contacts one candidate at a time. Everybody
works through an inbox with three lanes: urgent (reminders and reminded
questions), normal (questions), and background (own work). People finish the
block they are on, then read messages before going back to their own work;
during their team's deadline peak, own work joins the normal lane and
questions wait behind it. An ask whose projected wait exceeds `patience`
sinks unread; the asker checks
back after `patience`, sends a reminder (up to `max_followups`), and in the
end gives up on that person and withdraws the question.
"""

from __future__ import annotations

import heapq
import itertools
from collections import deque
from dataclasses import dataclass, field, asdict

import numpy as np

from .company import CORE, World

QTYPES = ("content", "whom", "technical", "decision")

# v4: how often a question of each kind truly is (high, low) importance; the rest is normal.
# Decisions about a client and blocked technical work are the urgent ones (assumed).
IMPORTANCE = {"content": (0.15, 0.40), "whom": (0.10, 0.40),
              "technical": (0.30, 0.30), "decision": (0.60, 0.10)}


@dataclass(frozen=True)
class SimConfig:
    horizon: float = 480.0            # two working weeks; 1 unit ~ 10 minutes
    day: float = 48.0
    questions_per_day: float = 1.5    # per person (assumed)
    mix: tuple = (0.35, 0.20, 0.35, 0.10)   # content, whom, technical, decision (assumed)
    company_decisions: float = 0.2    # share of decisions that are company-wide
    own_system: float = 0.7           # questions about the asker's own system ...
    core_system: float = 0.2          # ... the core platform; the rest: another client
    zipf_a: float = 1.0               # popularity skew of topics
    max_attempts: int = 8
    deadline: float = 96.0            # two working days
    patience: float = 24.0            # half a day before checking back
    latency: float = 0.01
    lookup_delay: float = 0.2         # a central search or log look-up
    t_content: float = 1.0
    t_technical: float = 2.0          # per piece of help
    t_decision: float = 1.5
    t_name: float = 0.3
    t_refer: float = 0.5
    t_dontknow: float = 0.2
    t_busy: float = 0.1
    t_followup: float = 0.1
    p_correct: float = 0.98           # a holder's answer is right
    p_analog: float = 0.5             # help from similar work for another client is right ...
    p_analog_wrong: float = 0.1       # ... or wrong (otherwise: no help)
    p_discover: float = 0.5           # a wrong answer is found out later
    discover_delay: float = 48.0
    name_threshold: float = 0.5       # memory score at which someone names a person
    n_refer: int = 3
    feedback: bool = True
    feedback_weight: float = 0.5
    own_work: float = 0.6             # share of time on own work (assumed)
    own_block: float = 6.0            # mean length of a block of own work
    peaks: bool = True
    peak_work: float = 0.85           # own work during a team's deadline peak
    peak_length: float = 96.0
    max_followups: int = 1
    withdraw: bool = True             # askers withdraw questions they gave up on
    busy_threshold: float = 12.0      # projected wait above which load-aware agents reply BUSY
    busy_queued: bool = True          # the BUSY reply takes queue time (t_busy)
    load_lambda: float = 0.015        # score penalty per unit of estimated wait
    near_best: float = 0.12
    softmax_temp: float = 0.04
    load_tau: float = 48.0
    dropout_at: float | None = None
    dropout_k: int = 3
    handover: str = "none"            # none | successor
    window: float = 48.0              # learning-curve windows (one day)
    seed: int = 0
    # -- v4: agents instead of people (DESIGN.md, v4 section) --------------------
    overflow: str = "sink"            # sink: an ask behind too much work sinks unread (people)
                                      # reject: it is refused at once, "rate limited" (agents)
    reject_after: float = 24.0        # projected wait above which an agent refuses an ask
    speed: float = 1.0                # parallel calls: an agent works through its queue this much faster
    approvals: bool = False           # some answers wait for the owner's (human) approval
    p_human_decision: float = 0.2     # share of decisions the owner's agent may not make alone
    p_approval: float = 0.02          # share of content / technical answers that need a data-access approval
    t_approval: float = 300.0         # human attention per approval (seconds in the agent profile)
    deadline_human: float = 28800.0   # questions waiting for a human get a working day
    # -- v4: priorities -----------------------------------------------------------
    priority: str = "none"            # none | asker | answerer | audit | budget
    asker_accuracy: float = 0.7       # an honest asker labels the true importance this often
    inflaters: float = 0.3            # share of askers who label every question high
    answerer_accuracy: float = 0.9    # a receiver who reads the ask judges its importance this often
    t_triage: float = 0.1             # reading an ask only to rank it
    audit_share: float = 0.2          # audit: share of labelled asks the receiver checks
    budget_share: float = 0.25        # budget: high labels per asker = this share of the questions they expect to ask
    # -- v6 (Phase 3): for very large networks; the defaults reproduce v5 exactly ---
    search_index: str = "exact"       # exact: score every declared row; hnsw: approximate nearest rows (faiss)
    search_rows: int = 256            # hnsw: how many nearest rows a search looks at
    own_work_events: str = "upfront"  # upfront: all blocks of own work queued at the start; lazy: one at a time
    peak_window: float | None = None  # spread the deadline peaks over this long a stretch, of which the run
                                      # sees the middle (None: over the run itself, as in v3-v5)
    question_topics: str = "tries"    # tries: draw a topic by popularity, up to 30 times, until someone
                                      # holds it in the lane asked about (else no question); held: draw
                                      # among the topics held in that lane (same popularity, no drops)


@dataclass
class Query:
    id: int
    asker: int
    qtype: str
    t0: float
    topic: int
    system: int | None                # client, -1 core, None company-wide (decisions)
    variant: int
    pieces: list[int]                 # items needed (empty for decisions)
    role: tuple | None = None         # decisions: whose decision it is
    vec: np.ndarray | None = None     # what the asker is looking for right now
    need: int = 0                     # goes up when a partial answer changes what is needed
    frontier_need: int = -1           # the need the strategy's candidate list was built for
    covered: dict = field(default_factory=dict)   # item -> answered correctly?
    helpers: list = field(default_factory=list)   # (agent, correct, what was asked)
    named: int | None = None          # whom to ask: the person named
    attempts: int = 0
    msgs: int = 0
    asked: list = field(default_factory=list)
    frontier: dict = field(default_factory=dict)
    refq: list = field(default_factory=list)
    referrers: list = field(default_factory=list)
    waiting_on: int | None = None
    sent_at: float = 0.0
    job: "Job | None" = None
    status: str = "open"              # open | ok | fail
    correct: bool = False
    t_end: float | None = None
    answerer: int | None = None
    fail_reason: str = ""
    timeouts: int = 0
    busy_replies: int = 0
    followups: int = 0
    followups_to_current: int = 0
    importance: int = 1               # v4: true importance, 0 low, 1 normal, 2 high (hidden)
    label: int = 1                    # v4: the importance the asker writes on it
    deadline: float | None = None     # v4: questions waiting for a human get longer (None: the default)
    needs_human: bool = False         # v4: a decision the owner's agent may not make alone
    approval_wait: float | None = None
    rejections: int = 0

    def remaining(self) -> list[int]:
        return [i for i in self.pieces if i not in self.covered]


@dataclass
class Response:
    kind: str                         # answer | refer | dontknow
    service: float
    covers: dict = field(default_factory=dict)    # item -> correct?
    named: int | None = None          # whom-to-ask answers


@dataclass(eq=False)                  # jobs are compared by identity
class Job:
    """One piece of work in an agent's inbox.

    kind: ask (q set) | reminder | busy | triage | own (q None)
    """
    q: Query | None
    kind: str
    service: float
    arrived: float
    response: Response | None = None
    projected_wait: float = 0.0       # work ahead of it when it was added
    shift: float = 0.0                # later (+) or earlier (-) because of reminders / withdrawals
    lane: str = "normal"              # normal | urgent | ignored | withdrawn
    started: float | None = None
    prio: int = 1                     # v4: place in the normal lane (higher goes first)
    scaled: bool = False              # v4: service already divided by the agent's speed

    def read_in_time(self, patience: float) -> bool:
        """Will (or did) the recipient open it within `patience` of its arrival?"""
        if self.started is not None:
            return True
        return self.lane == "normal" and self.projected_wait + self.shift <= patience + 1e-9


@dataclass
class AgentState:
    current_end: float = 0.0          # when the job in hand is done
    help_time: float = 0.0            # time spent on other people's questions
    own_time: float = 0.0
    handled: int = 0
    answers: int = 0
    referrals: int = 0
    dontknows: int = 0
    busy_replies: int = 0
    ignored: int = 0
    received: int = 0                 # asks that reached this agent
    reminders: int = 0                # reminders that reached this agent
    decisions: int = 0                # decision questions answered
    wasted: int = 0                   # asks worked on after the asker had moved on
    withdrawn: int = 0
    rescued: int = 0                  # ignored asks dug out by a reminder
    alive: bool = True
    help_backlog_at_h: float = 0.0    # other people's work still queued at the end
    own_backlog_at_h: float = 0.0     # own work still queued at the end (overtime)
    reads: int = 0                    # v4: messages read (each costs an agent tokens)
    triage_reads: int = 0             # v4: of those, read only to rank them
    rejected: int = 0                 # v4: asks refused at once (agents, "rate limited")
    approvals: int = 0                # v4: approvals this person's human owner gave
    human_free_at: float = 0.0        # v4: when the human owner is through their approval queue
    urgent: deque = field(default_factory=deque)
    normal: deque = field(default_factory=deque)
    background: deque = field(default_factory=deque)   # own work outside peaks
    current: Job | None = None


class Sim:
    def __init__(self, world: World, strategy, cfg: SimConfig):
        self.world = world
        self.cfg = cfg
        self.strategy = strategy
        self.rng = np.random.default_rng(cfg.seed)
        self.now = 0.0
        self._heap: list = []
        self._seq = itertools.count()
        self.n = world.n
        self.state = [AgentState() for _ in range(self.n)]
        self.queries: list[Query] = []
        self.roles = {r: list(o) for r, o in world.roles.items()}   # may change on departures
        self.dropped: list[int] = []
        self.followup_reasons = {"ignored": 0, "pushed_back": 0, "repeat": 0, "gone": 0}
        self.check_invariants = False     # tests switch this on
        # v4 priorities: who inflates, how many high labels are left today, whom a receiver trusts.
        # Drawn from their own seeds so the questions stay the same in every priority variant.
        self.inflater = np.random.default_rng((cfg.seed, 11)).random(self.n) < cfg.inflaters
        self.high_used = np.zeros(self.n, dtype=int)                 # budget: high labels used so far
        self.high_budget = max(1, round(cfg.budget_share * cfg.questions_per_day * cfg.horizon / cfg.day))
        self.label_trust: list[dict[int, list[int]]] = [dict() for _ in range(self.n)]  # receiver -> asker -> [ok, checked]
        strategy.setup(self)

    # -- event plumbing ------------------------------------------------------

    def at(self, t: float, fn, *args) -> None:
        heapq.heappush(self._heap, (t, next(self._seq), fn, args))

    def run(self) -> "Sim":
        longest = max(self.cfg.deadline, self.cfg.deadline_human if self.cfg.approvals else 0.0)
        end = self.cfg.horizon + longest + self.cfg.patience
        self._schedule_questions()
        # own work only while asks are still moving between agents; after that
        # only human approvals and the answers they release are left
        own_end = self.cfg.horizon + self.cfg.deadline + self.cfg.patience
        if self.cfg.own_work_events == "lazy":
            self._schedule_own_work_lazy(own_end)
        else:
            self._schedule_own_work(own_end)
        if self.cfg.dropout_at is not None:
            self.at(self.cfg.dropout_at, self._dropout)
        self.at(self.cfg.horizon, self._snapshot)
        while self._heap:
            t, _, fn, args = heapq.heappop(self._heap)
            if t > end:
                break
            self.now = t
            fn(*args)
        for q in self.queries:
            if q.status == "open":
                q.status, q.t_end, q.fail_reason = "fail", self.now, "horizon"
        return self

    # -- what happens: questions and own work ----------------------------------

    def _schedule_questions(self) -> None:
        w, cfg, rng = self.world, self.cfg, self.rng
        n_topics = w.space.n_topics
        pop = 1.0 / (rng.permutation(n_topics) + 1) ** cfg.zipf_a
        pop /= pop.sum()
        # Drawing a topic from this cumulative table is what rng.choice(len(pop), p=pop)
        # does internally, without rebuilding the table for every question.
        self._topic_cdf = pop.cumsum()
        self._topic_cdf /= self._topic_cdf[-1]
        if cfg.question_topics == "held":
            self._held_cdf = self._held_topic_tables(pop)
        clients = sorted({int(c) for c in w.team_client if c >= 0})
        self._client_position = {c: i for i, c in enumerate(clients)}
        rate = cfg.questions_per_day * self.n / cfg.day
        t, qid = 0.0, 0
        while True:
            t += rng.exponential(1.0 / rate)
            if t > cfg.horizon:
                break
            q = self._new_question(qid, int(rng.integers(self.n)), t, pop, clients)
            if q is None:
                continue
            qid += 1
            self._tag(q)
            self.queries.append(q)
            self.at(t, self._start, q)

    def _new_question(self, qid, asker, t, pop, clients) -> Query | None:
        w, cfg, rng = self.world, self.cfg, self.rng
        qtype = QTYPES[int(rng.choice(4, p=np.array(cfg.mix) / sum(cfg.mix)))]
        own = int(w.team_client[asker])
        u = rng.random()
        if u < cfg.own_system:
            system = own
        elif u < cfg.own_system + cfg.core_system:
            system = CORE if own != CORE else clients[int(rng.integers(len(clients)))]
        else:
            system = self._other_client(clients, own)
        variant = int(rng.integers(3))
        if qtype == "decision":
            topic = self._draw_topic()
            if rng.random() < cfg.company_decisions:
                system = None
            role = w.owner_role(system, topic)
            if asker in self.roles.get(role, []):
                return None
            vec = w.question_vec("decision", topic, system, 0, variant)
            return Query(qid, asker, qtype, t, topic, system, variant, [], role, vec)
        for _ in range(30):
            topic = self._draw_topic(system)
            first = self._held_item(topic, system, asker)
            if first is None:
                continue
            pieces = [first]
            if qtype == "technical" and system != CORE:
                second = self._held_item(topic, CORE, asker)
                if second is None:
                    continue
                pieces.append(second)
            _, _, k = w.item_parts(first)
            vec = w.question_vec(qtype, topic, system, k, variant)
            return Query(qid, asker, qtype, t, topic, system, variant, pieces, None, vec)
        return None

    def _tag(self, q: Query) -> None:
        """v4: true importance, the asker's label, and whether a human must decide.
        Own seeds per question, so every variant sees the same questions."""
        cfg = self.cfg
        u = np.random.default_rng((cfg.seed, 7, q.id)).random(4)
        p_high, p_low = IMPORTANCE[q.qtype]
        q.importance = 2 if u[0] < p_high else 0 if u[0] < p_high + p_low else 1
        if self.inflater[q.asker]:
            q.label = 2
        elif u[1] < cfg.asker_accuracy:
            q.label = q.importance
        else:
            q.label = int(u[2] * 3)
        if cfg.priority == "budget" and q.label == 2:     # only so many high labels per asker
            if self.high_used[q.asker] >= self.high_budget:
                q.label = 1
            else:
                self.high_used[q.asker] += 1
        q.needs_human = cfg.approvals and q.qtype == "decision" and u[3] < cfg.p_human_decision
        q.deadline = cfg.deadline_human if q.needs_human else cfg.deadline

    def _draw_topic(self, system=None) -> int:
        if system is not None and self.cfg.question_topics == "held":
            table = self._held_cdf.get(system)
            if table is None:
                return self._draw_topic()
            topics, cdf = table
            return int(topics[cdf.searchsorted(self.rng.random(), side="right")])
        return int(self._topic_cdf.searchsorted(self.rng.random(), side="right"))

    def _held_topic_tables(self, pop: np.ndarray) -> dict:
        """v6: per lane, the topics someone holds there and their cumulative
        popularity. Drawing from it is the same as drawing by popularity until
        the topic is held in the lane, without a limit on the tries.

        Why: the topic space of large networks grows with the network, so each
        lane covers a smaller share of all topics; with 30 tries, half of all
        questions at 10,000 agents found no topic and were dropped (7 % at
        1,000), which would have halved the load in large networks."""
        space = self.world.space
        by_system: dict[int, set[int]] = {}
        for item in self.world.holders:
            topic, lane, _ = space.item_parts(item)
            by_system.setdefault(lane, set()).add(topic)
        tables = {}
        for lane, topics in by_system.items():
            topics = np.array(sorted(topics))
            cdf = pop[topics].cumsum()
            tables[lane] = (topics, cdf / cdf[-1])
        return tables

    def _other_client(self, clients: list[int], own: int) -> int:
        """A random client other than `own` (the same draw as rng.choice of that list)."""
        position = self._client_position.get(own)
        if position is None:
            return clients[int(self.rng.integers(len(clients)))] if clients else own
        if len(clients) == 1:
            return own
        j = int(self.rng.integers(len(clients) - 1))
        return clients[j if j < position else j + 1]

    def _held_item(self, topic, system, asker) -> int | None:
        """A random aspect of (topic, system) that someone other than the asker holds."""
        ks = self.rng.permutation(self.world.space.aspects)
        for k in ks:
            i = self.world.item_id(topic, system, int(k))
            hs = self.world.holders.get(i, [])
            if hs and (len(hs) > 1 or hs[0] != asker) and i not in self.world.items[asker]:
                return i
        return None

    def _schedule_own_work(self, end: float) -> None:
        """Blocks of own work; each team has one deadline peak (thinned Poisson)."""
        cfg, rng = self.cfg, self.rng
        self.peak_start = {}
        for tm in sorted(set(self.world.team.tolist())):
            self.peak_start[tm] = self._peak_start(rng)
        peak_start = self.peak_start
        top = max(cfg.own_work, cfg.peak_work if cfg.peaks else 0.0)
        if top <= 0:
            return
        lam = top / cfg.own_block
        for a in range(self.n):
            t = 0.0
            ps = peak_start[int(self.world.team[a])]
            while True:
                t += rng.exponential(1.0 / lam)
                if t > end:
                    break
                share = cfg.peak_work if (cfg.peaks and ps <= t < ps + cfg.peak_length) else cfg.own_work
                if rng.random() < share / top:
                    self.at(t, self._own_work_arrives, a, float(rng.exponential(cfg.own_block)))

    def _peak_start(self, rng) -> float:
        """When a team's deadline peak starts. Peaks are spread over the run; a
        run shorter than a peak would otherwise put every team in its peak at
        once, so v6's short runs spread them over a longer window (peak_window)
        and look at its middle."""
        cfg = self.cfg
        if cfg.peak_window is None:
            return rng.uniform(0, max(1.0, cfg.horizon - cfg.peak_length))
        offset = (cfg.peak_window - cfg.horizon) / 2
        return rng.uniform(0, max(1.0, cfg.peak_window - cfg.peak_length)) - offset

    def _schedule_own_work_lazy(self, end: float) -> None:
        """v6: the same blocks of own work (same rates, same peaks), but each
        agent's next block is drawn when the previous one arrives, from a
        random stream of its own. The event queue then holds one block per
        agent instead of a few hundred (a network of 100,000 agents would
        otherwise queue tens of millions of events at the start)."""
        cfg = self.cfg
        self.peak_start = {}
        for tm in sorted(set(self.world.team.tolist())):
            self.peak_start[tm] = self._peak_start(self.rng)
        top = max(cfg.own_work, cfg.peak_work if cfg.peaks else 0.0)
        if top <= 0:
            return
        self._own_rng = np.random.default_rng((cfg.seed, 13))
        self._own_end, self._own_top = end, top
        for a in range(self.n):
            self._next_own_work(a, 0.0)

    def _next_own_work(self, a: int, t: float) -> None:
        cfg, rng = self.cfg, self._own_rng
        ps = self.peak_start[int(self.world.team[a])]
        while True:
            t += rng.exponential(cfg.own_block / self._own_top)
            if t > self._own_end:
                return
            share = cfg.peak_work if (cfg.peaks and ps <= t < ps + cfg.peak_length) else cfg.own_work
            if rng.random() < share / self._own_top:
                self.at(t, self._own_work_lazy, a, float(rng.exponential(cfg.own_block)))
                return

    def _own_work_lazy(self, a: int, length: float) -> None:
        self._own_work_arrives(a, length)
        self._next_own_work(a, self.now)

    def in_peak(self, a: int) -> bool:
        if not self.cfg.peaks:
            return False
        start = self.peak_start[int(self.world.team[a])]
        return start <= self.now < start + self.cfg.peak_length

    def _own_work_arrives(self, a: int, length: float) -> None:
        if self.state[a].alive:
            lane = "normal" if self.in_peak(a) else "background"
            self._add_work(a, Job(None, "own", length, self.now), lane)

    # -- the inbox -------------------------------------------------------------

    def projected_wait(self, b: int) -> float:
        """How long a new message would wait: the job in hand, then both message lanes."""
        return self.wait_ahead(b, None)

    def wait_ahead(self, b: int, prio: int | None) -> float:
        """v4: the work in front of a new message of this priority (None: everything)."""
        st = self.state[b]
        wait = max(0.0, st.current_end - self.now) if st.current is not None else 0.0
        wait += sum(j.service for j in st.urgent)
        return wait + sum(j.service for j in st.normal if prio is None or j.prio >= prio)

    def _add_work(self, b: int, job: Job, lane: str) -> None:
        st = self.state[b]
        if not job.scaled:
            # Parallel calls make an agent faster at messages. Its owner's own
            # tasks keep their share of its capacity (own_work), so they are
            # not sped up (DESIGN.md §13.8).
            if job.kind != "own":
                job.service /= self.cfg.speed
            job.scaled = True
        job.projected_wait = self.projected_wait(b)
        job.lane = lane
        if lane == "urgent":              # everything in the normal lane now comes later
            for waiting in st.normal:
                waiting.shift += job.service
            st.urgent.append(job)
        elif lane == "normal":            # behind everything of equal or higher priority
            pos = next((i for i, w in enumerate(st.normal) if w.prio < job.prio), len(st.normal))
            job.projected_wait = self.wait_ahead(b, job.prio)
            for i, waiting in enumerate(st.normal):
                if i >= pos:
                    waiting.shift += job.service
            st.normal.insert(pos, job)
        else:
            st.background.append(job)
        if st.current is None:
            self._start_next_job(b)

    def _move_to_urgent(self, b: int, job: Job) -> None:
        st = self.state[b]
        if job.lane == "normal":          # the asks it overtakes come later
            for waiting in itertools.takewhile(lambda j: j is not job, st.normal):
                waiting.shift += job.service
            st.normal.remove(job)
            job.lane = "urgent"
            st.urgent.append(job)
        elif job.lane == "ignored":       # dug out of the pile it had sunk into
            st.rescued += 1
            self._add_work(b, job, "urgent")

    def _remove_unstarted(self, b: int, job: Job) -> None:
        """A withdrawn ask leaves the inbox; whatever waited behind it moves up."""
        st = self.state[b]
        if job.lane == "normal":
            behind = False
            for waiting in st.normal:
                if waiting is job:
                    behind = True
                elif behind:
                    waiting.shift -= job.service
            st.normal.remove(job)
        elif job.lane == "urgent":
            st.urgent.remove(job)
            for waiting in st.normal:
                waiting.shift -= job.service
        job.lane = "withdrawn"

    def _start_next_job(self, b: int) -> None:
        st = self.state[b]
        lane = st.urgent or st.normal or st.background
        if not lane:
            st.current = None
            return
        job = lane.popleft()
        job.started = self.now
        if self.check_invariants and job.lane == "normal":
            due = job.arrived + job.projected_wait + job.shift
            assert abs(due - self.now) < 1e-6, ("queue bookkeeping is off", due, self.now)
        st.current = job
        st.current_end = self.now + job.service
        self.at(self.now + job.service, self._finish_job, b, job)

    def _finish_job(self, b: int, job: Job) -> None:
        st = self.state[b]
        st.current = None
        if job.kind == "own":
            st.own_time += job.service
        elif job.kind in ("reminder", "busy", "triage"):
            if st.alive:
                st.help_time += job.service
        else:
            self._ask_done(b, job)
        self._start_next_job(b)

    # -- query lifecycle -------------------------------------------------------

    def _start(self, q: Query) -> None:
        if q.deadline is None:            # a question built by hand, not by the schedule
            q.deadline = self.cfg.deadline
        if not self.state[q.asker].alive:
            q.status, q.t_end, q.fail_reason = "fail", self.now, "asker_gone"
            return
        self.strategy.start(self, q)
        self._next(q)

    def _next(self, q: Query) -> None:
        if q.status != "open":
            return
        if q.attempts >= self.cfg.max_attempts:
            return self._fail(q, "attempts")
        if self.now - q.t0 > q.deadline:
            return self._fail(q, "deadline")
        c = self.strategy.next_candidate(self, q)
        if c is None:
            return self._fail(q, "no_candidate")
        q.attempts += 1
        q.msgs += 1
        q.asked.append(c)
        q.waiting_on = c
        q.job = None
        q.followups_to_current = 0
        delay = self.cfg.latency + (self.cfg.lookup_delay if self.strategy.lookup else 0.0)
        q.sent_at = self.now
        self.at(self.now + delay, self._arrive, q, c)

    def _fail(self, q: Query, reason: str) -> None:
        q.status, q.t_end, q.fail_reason, q.waiting_on = "fail", self.now, reason, None

    def _arrive(self, q: Query, b: int) -> None:
        st, cfg = self.state[b], self.cfg
        if q.status != "open" or q.waiting_on != b:
            return
        if not st.alive:                  # nobody will ever read it
            self._wait_for_reply(q, b)
            return
        st.received += 1
        prio = self._receiver_priority(b, q)
        wait = self.wait_ahead(b, prio)
        own_decision = q.qtype == "decision" and b in self.roles.get(q.role, [])
        if self.strategy.load_aware and wait > cfg.busy_threshold and not own_decision:
            # (an owner never answers BUSY to a decision only they can make)
            st.busy_replies += 1
            st.reads += 1                 # it reads the ask to say whom to try instead
            if cfg.busy_queued:
                self._add_work(b, Job(None, "busy", cfg.t_busy, self.now), "normal")
            sugg = self.suggest(b, q)
            q.msgs += 1
            q.busy_replies += 1
            self.at(self.now + cfg.latency, self._reply, q, b, Response("busy", 0.0), sugg)
            return
        if cfg.overflow == "reject" and wait > cfg.reject_after and not own_decision:
            # an agent behind too much work refuses at once, unread ("rate limited")
            st.rejected += 1
            q.rejections += 1
            q.msgs += 1
            self.at(self.now + cfg.latency, self._reply, q, b, Response("rejected", 0.0), [])
            return
        if cfg.overflow == "sink" and wait > cfg.patience:   # sinks unread; nothing decided yet
            st.ignored += 1
            q.job = Job(q, "ask", 0.0, self.now, lane="ignored")
            self._wait_for_reply(q, b)
            return
        response = self.respond(b, q)
        q.job = Job(q, "ask", response.service, self.now, response, prio=prio)
        self._add_work(b, q.job, "normal")
        self._wait_for_reply(q, b)

    # -- v4: priorities ------------------------------------------------------------

    def _receiver_priority(self, b: int, q: Query) -> int:
        """Where the ask goes in b's normal lane, under the chosen priority rule."""
        cfg = self.cfg
        if cfg.priority == "none":
            return 1
        if cfg.priority in ("asker", "budget"):
            return q.label
        if cfg.priority == "answerer":    # b reads every ask to rank it
            self._triage(b)
            return self._judged(b, q)
        # audit: trust the label, check a sample, discount askers whose labels were inflated
        record = self.label_trust[b].setdefault(q.asker, [0, 0])
        if np.random.default_rng((cfg.seed, 17, b, q.id)).random() < cfg.audit_share:
            self._triage(b)
            seen = self._judged(b, q)
            record[0] += q.label <= seen
            record[1] += 1
            return seen
        if record[1] >= 2 and record[0] / record[1] < 0.5:
            return min(q.label, 1)
        return q.label

    def _judged(self, b: int, q: Query) -> int:
        """The importance b sees after reading the ask."""
        u = np.random.default_rng((self.cfg.seed, 13, b, q.id)).random(2)
        return q.importance if u[0] < self.cfg.answerer_accuracy else int(u[1] * 3)

    def _triage(self, b: int) -> None:
        st = self.state[b]
        st.reads += 1
        st.triage_reads += 1
        self._add_work(b, Job(None, "triage", self.cfg.t_triage, self.now), "urgent")

    # -- what a contacted person does --------------------------------------------

    def _draw(self, b: int, q: Query, item: int) -> float:
        """The same person asked the same thing gets the same luck in every strategy.
        item = -1 is the draw for 'is this wrong answer found out later?'."""
        return float(np.random.default_rng((self.cfg.seed, b, q.id, item + 1)).random())

    def suggest(self, b: int, q: Query) -> list[tuple[int, float]]:
        ring = self.strategy._ring(self, b, q)
        return ring if ring is not None else self.strategy.suggestions(self, b, q)

    def respond(self, b: int, q: Query) -> Response:
        cfg, w = self.cfg, self.world
        adversary = w.adversary[b]
        if q.qtype == "decision":
            if b in self.roles.get(q.role, []):
                return Response("answer", cfg.t_decision)
        elif adversary == "wrong" and any(t == q.topic for t, _ in w.declared[b]):
            covers = {i: False for i in q.remaining()}
            named = b if q.qtype == "whom" else None
            return Response("answer", cfg.t_content, covers, named)
        elif q.qtype == "whom":
            target = q.pieces[0]
            if target in w.items[b]:
                return Response("answer", cfg.t_name, named=b)
            guess = self.strategy.best_guess(self, b, q)
            if guess is not None and guess[1] >= cfg.name_threshold:
                return Response("answer", cfg.t_name, named=guess[0])
        else:
            covers = {}
            for item in q.remaining():
                u = self._draw(b, q, item)
                if item in w.items[b]:
                    covers[item] = u < cfg.p_correct
                elif w.has_analogue(b, item):
                    if u < cfg.p_analog:
                        covers[item] = True
                    elif u < cfg.p_analog + cfg.p_analog_wrong:
                        covers[item] = False
            if covers:
                t = cfg.t_content if q.qtype == "content" else cfg.t_technical * len(covers)
                return Response("answer", t, covers)
        if self.suggest(b, q):
            return Response("refer", cfg.t_refer)
        return Response("dontknow", cfg.t_dontknow)

    # -- waiting, reminders, withdrawing ------------------------------------------

    def _wait_for_reply(self, q: Query, b: int) -> None:
        self.at(self.now + self.cfg.patience, self._check_back, q, b)

    def _check_back(self, q: Query, b: int) -> None:
        """No reply yet. Opened: keep waiting. Not opened: remind or give up."""
        if q.status != "open" or q.waiting_on != b:
            return
        if q.job is not None and q.job.read_in_time(self.cfg.patience):
            return
        before_deadline = self.now - q.t0 <= q.deadline
        if q.followups_to_current < self.cfg.max_followups and before_deadline:
            self._send_followup(q, b)
        else:
            self._give_up(q, b)

    def _send_followup(self, q: Query, b: int) -> None:
        q.followups += 1
        q.followups_to_current += 1
        q.msgs += 1
        if not self.state[b].alive:
            self.followup_reasons["gone"] += 1
        elif q.job.lane == "ignored":
            self.followup_reasons["ignored"] += 1
        elif q.job.lane == "normal":
            self.followup_reasons["pushed_back"] += 1
        else:
            self.followup_reasons["repeat"] += 1
        self.at(self.now + self.cfg.latency, self._followup_arrives, q, b)

    def _followup_arrives(self, q: Query, b: int) -> None:
        if q.status != "open" or q.waiting_on != b:
            return
        st = self.state[b]
        if st.alive:
            st.reminders += 1
            st.reads += 1
            self._add_work(b, Job(None, "reminder", self.cfg.t_followup, self.now), "urgent")
            job = q.job
            if job.response is None:      # an ignored ask, looked at for the first time
                job.response = self.respond(b, q)
                job.service = job.response.service
            if job.started is None:
                self._move_to_urgent(b, job)
        self._wait_for_reply(q, b)

    def _withdraw(self, q: Query, b: int) -> None:
        job = q.job
        if self.cfg.withdraw and job is not None and job.started is None and job.lane != "withdrawn":
            self._remove_unstarted(b, job)
            self.state[b].withdrawn += 1

    def _give_up(self, q: Query, b: int) -> None:
        q.waiting_on = None
        q.timeouts += 1
        self._withdraw(q, b)
        self.strategy.on_timeout(self, q, b)
        self._next(q)

    def _timeout(self, q: Query, b: int) -> None:
        if q.status == "open" and q.waiting_on == b:
            self._give_up(q, b)

    # -- answers -----------------------------------------------------------------

    def _ask_done(self, b: int, job: Job) -> None:
        st, q, r = self.state[b], job.q, job.response
        if not st.alive:                  # left while it was queued
            if q.status == "open" and q.waiting_on == b:
                self.at(self.now, self._timeout, q, b)
            return
        st.help_time += job.service
        st.handled += 1
        st.reads += 1
        if q.status != "open" or q.waiting_on != b:
            st.wasted += 1
        sugg = []
        if r.kind == "answer":
            st.answers += 1
            st.decisions += q.qtype == "decision"
        elif r.kind == "refer":
            st.referrals += 1
            sugg = self.suggest(b, q)
        else:
            st.dontknows += 1
        q.msgs += 1
        if r.kind == "answer" and self._needs_approval(b, q):
            # the owner's human has to approve before the answer goes out (one queue per human)
            start = max(self.now, st.human_free_at)
            st.human_free_at = start + self.cfg.t_approval
            st.approvals += 1
            q.approval_wait = st.human_free_at - self.now
            q.deadline = max(q.deadline, self.cfg.deadline_human)
            self.at(st.human_free_at + self.cfg.latency, self._reply, q, b, r, sugg)
            return
        self.at(self.now + self.cfg.latency, self._reply, q, b, r, sugg)

    def _needs_approval(self, b: int, q: Query) -> bool:
        cfg = self.cfg
        if not cfg.approvals or q.status != "open" or q.waiting_on != b:
            return False
        if q.qtype == "decision":
            return q.needs_human
        if q.qtype in ("content", "technical"):   # data access the owner must allow
            return bool(np.random.default_rng((cfg.seed, 19, b, q.id)).random() < cfg.p_approval)
        return False

    def _reply(self, q: Query, b: int, r: Response, sugg) -> None:
        if q.status != "open" or q.waiting_on != b:
            return
        q.waiting_on = None
        if self.now - q.t0 > q.deadline:          # too late to count
            return self._fail(q, "deadline")
        delay = self.now - q.sent_at
        self.strategy.observe(self, q, b, r.kind, sugg, delay)
        if r.kind != "answer":
            if sugg:
                q.referrers.append(b)
            return self._next(q)
        if q.qtype == "decision":
            return self._finish(q, b, True)
        if q.qtype == "whom":
            correct = q.pieces[0] in self.world.items[r.named]
            q.named = r.named
            q.helpers.append((b, correct, q.vec))
            return self._finish(q, b, correct)
        for item, ok in r.covers.items():
            if item not in q.covered:
                q.covered[item] = ok
                q.helpers.append((b, ok, q.vec))
        if q.remaining():                 # partly answered: look for the rest
            topic, system, k = self.world.item_parts(q.remaining()[0])
            q.vec = self.world.question_vec(q.qtype, topic, system, k, q.variant)
            q.need += 1
            return self._next(q)
        self._finish(q, b, all(q.covered.values()))

    def _finish(self, q: Query, b: int, correct: bool) -> None:
        q.status, q.t_end, q.answerer, q.correct = "ok", self.now, b, correct
        if self.cfg.feedback and self.strategy.uses_feedback:
            q.msgs += len(set(q.referrers))
        self.strategy.on_success(self, q, b)
        for helper, ok, vec in q.helpers:  # wrong answers may be found out later
            if not ok and self._draw(helper, q, -1) < self.cfg.p_discover:
                self.at(self.now + self.cfg.discover_delay, self.strategy.on_wrong, self, q, helper, vec)

    # -- end of period, departures ----------------------------------------------------

    def _snapshot(self) -> None:
        for st in self.state:
            queued = list(st.urgent) + list(st.normal) + list(st.background)
            st.help_backlog_at_h = sum(j.service for j in queued if j.kind != "own")
            st.own_backlog_at_h = sum(j.service for j in queued if j.kind == "own")

    def _dropout(self) -> None:
        """The longest-serving people leave; their roles pass to a teammate."""
        w = self.world
        ranked = sorted(range(self.n), key=lambda a: (-w.tenure[a], a))
        for a in ranked[: self.cfg.dropout_k]:
            self.state[a].alive = False
            self.dropped.append(a)
        for a in self.dropped:
            mates = [b for b in range(self.n) if w.team[b] == w.team[a] and self.state[b].alive]
            successor = max(mates, key=lambda b: (w.tenure[b], -b)) if mates else None
            for role, owners in self.roles.items():
                if a in owners:
                    owners.remove(a)
                    if successor is not None:
                        owners.append(successor)
            if successor is not None and self.cfg.handover == "successor":
                self.strategy.handover(self, a, successor)

    def holds(self, agent: int, item: int) -> bool:
        return item in self.world.items[agent]


def sim_config_dict(cfg: SimConfig) -> dict:
    return asdict(cfg)
