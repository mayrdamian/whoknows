"""Metrics computed after a run (DESIGN.md §9)."""

from __future__ import annotations

import numpy as np

from .sim import QTYPES, Sim


def gini(x) -> float:
    x = np.sort(np.asarray(x, dtype=float))
    if x.sum() == 0:
        return 0.0
    n = len(x)
    cum = np.cumsum(x)
    return float((n + 1 - 2 * (cum / cum[-1]).sum()) / n)


def _rate(qs, pred) -> float:
    return float(np.mean([pred(q) for q in qs])) if qs else float("nan")


def summarize(sim: Sim) -> dict:
    w, cfg, qs, st = sim.world, sim.cfg, sim.queries, sim.state
    n = max(1, len(qs))
    correct = [q for q in qs if q.status == "ok" and q.correct]
    lat = np.array([q.t_end - q.t0 for q in correct]) if correct else np.array([np.nan])
    seniors = w.senior
    received = np.array([s.received for s in st], dtype=float)
    reminders = np.array([s.reminders for s in st], dtype=float)
    busy = np.array([s.busy_replies for s in st], dtype=float)
    inbox = received + reminders                       # every message that needs reading
    k5 = max(1, int(round(0.05 * len(st))))
    help_time = np.array([s.help_time for s in st])
    backlog = np.array([s.help_backlog_at_h for s in st])
    owners = np.zeros(sim.n, dtype=bool)
    for owner_list in w.roles.values():
        owners[owner_list] = True

    out = {
        "queries": len(qs),
        "correct": _rate(qs, lambda q: q.status == "ok" and q.correct),
        "wrong": _rate(qs, lambda q: q.status == "ok" and not q.correct),
        "partly": _rate(qs, lambda q: q.status != "ok" and len(q.covered) > 0),
        "latency_median": float(np.nanmedian(lat)),
        "latency_p90": float(np.nanpercentile(lat, 90)) if correct else float("nan"),
        "messages_mean": float(np.mean([q.msgs for q in qs])) if qs else 0.0,
        "attempts_mean": float(np.mean([q.attempts for q in qs])) if qs else 0.0,
        "reminders_per_query": float(reminders.sum() / n),
        "top5_share_inbox": float(np.sort(inbox)[::-1][:k5].sum() / max(1.0, inbox.sum())),
        "senior_share_inbox": float(inbox[seniors].sum() / max(1.0, inbox.sum())),
        "gini_inbox": gini(inbox),
        "senior_share_help": float(help_time[seniors].sum() / max(1e-9, help_time.sum())),
        "help_share_senior_mean": float(help_time[seniors].mean() / cfg.horizon),
        "help_share_others_mean": float(help_time[~seniors].mean() / cfg.horizon),
        "backlog_senior_mean": float(backlog[seniors].mean()),
        "backlog_max": float(backlog.max()),
        "own_backlog_senior_mean": float(np.mean([s.own_backlog_at_h for s, sen in zip(st, seniors) if sen])),
        "own_backlog_others_mean": float(np.mean([s.own_backlog_at_h for s, sen in zip(st, seniors) if not sen])),
        "ignored_per_query": float(sum(s.ignored for s in st) / n),
        "never_read_per_query": float(sum(s.ignored - s.rescued for s in st) / n),
        "wasted_per_query": float(sum(s.wasted for s in st) / n),
        "busy_per_query": float(busy.sum() / n),
        "owner_share_decisions": float(sum(s.decisions for s in st) / max(1, sum(s.answers for s in st))),
        "owner_share_inbox": float(inbox[owners].sum() / max(1.0, inbox.sum())),
        "fail_reasons": _count(q.fail_reason for q in qs if q.status == "fail"),
    }
    for t in QTYPES:
        sub = [q for q in qs if q.qtype == t]
        out[f"correct_{t}"] = _rate(sub, lambda q: q.status == "ok" and q.correct)
        out[f"wrong_{t}"] = _rate(sub, lambda q: q.status == "ok" and not q.correct)
    # knowledge from other client teams (cross-client help)
    helped = [q for q in qs if q.status == "ok" and q.qtype in ("content", "technical")]
    out["cross_client_help_share"] = _rate(
        helped, lambda q: any(sim.world.team_client[h] not in (q.system, -1) for h, _, _ in q.helpers))
    undecl = [q for q in qs if q.qtype in ("content", "technical", "whom")
              and not _declared_anywhere(w, q.pieces[0])]
    out["correct_undeclared"] = _rate(undecl, lambda q: q.status == "ok" and q.correct)
    stats = getattr(sim.strategy, "memory_stats", None)
    if stats is not None:
        out.update({k: int(v) for k, v in stats().items()})
    if cfg.dropout_at is not None:
        lost = set(sim.dropped)
        before = [q for q in qs if q.t0 < cfg.dropout_at]
        after = [q for q in qs if q.t0 >= cfg.dropout_at + 12 and q.asker not in lost]
        out["correct_before_dropout"] = _rate(before, lambda q: q.status == "ok" and q.correct)
        out["correct_after_dropout"] = _rate(after, lambda q: q.status == "ok" and q.correct)
    out.update(_v4_metrics(sim, qs, n, k5))
    out.update(_v5_metrics(sim, qs, n))
    edges = np.arange(0, cfg.horizon + cfg.window, cfg.window)
    out["curve"] = [_rate([q for q in qs if lo <= q.t0 < hi], lambda q: q.status == "ok" and q.correct)
                    for lo, hi in zip(edges[:-1], edges[1:])]
    out["followup_reasons"] = dict(sim.followup_reasons)
    return out


def _top_share(values, k: int) -> float:
    v = np.sort(np.asarray(values, dtype=float))[::-1]
    return float(v[:k].sum() / max(1.0, v.sum()))


def _v4_metrics(sim: Sim, qs, n: int, k5: int) -> dict:
    """Cost, refusals, approvals and importance (DESIGN.md, v4 section)."""
    st = sim.state
    reads = [s.reads for s in st]
    ok = lambda q: q.status == "ok" and q.correct
    out = {
        "reads_per_query": float(sum(reads) / n),                 # every read costs an agent tokens
        "top5_share_reads": _top_share(reads, k5),                # who pays for the reading
        "triage_per_query": float(sum(s.triage_reads for s in st) / n),
        "top5_share_triage": _top_share([s.triage_reads for s in st], k5),
        "rejected_per_query": float(sum(s.rejected for s in st) / n),
        "approvals_per_query": float(sum(s.approvals for s in st) / n),
        "top5_share_approvals": _top_share([s.approvals for s in st], k5),
    }
    waits = [q.approval_wait for q in qs if q.approval_wait is not None]
    out["approval_wait_median"] = float(np.median(waits)) if waits else float("nan")
    out["approval_wait_p90"] = float(np.percentile(waits, 90)) if waits else float("nan")
    human = [q for q in qs if q.needs_human or q.approval_wait is not None]
    out["correct_needs_human"] = _rate(human, ok)
    for level, name in ((2, "high"), (1, "normal"), (0, "low")):
        sub = [q for q in qs if q.importance == level]
        out[f"correct_{name}"] = _rate(sub, ok)
        lat = [q.t_end - q.t0 for q in sub if ok(q)]
        out[f"latency_{name}_median"] = float(np.median(lat)) if lat else float("nan")
        out[f"latency_{name}_p90"] = float(np.percentile(lat, 90)) if lat else float("nan")
    return out


def _declared_anywhere(w, item) -> bool:
    t, c, _ = w.item_parts(item)
    return any(w.holders.get(item) and (t, c) in set(w.declared[h]) for h in w.holders.get(item, []))


def _count(it) -> dict:
    d: dict = {}
    for x in it:
        d[x] = d.get(x, 0) + 1
    return d


def per_agent_table(sim: Sim) -> list[dict]:
    w = sim.world
    rows = []
    for a, s in enumerate(sim.state):
        rows.append({"agent": a, "office": int(w.office[a]), "team": int(w.team[a]),
                     "tenure_quarters": float(w.tenure[a]), "senior": bool(w.senior[a]),
                     "roles": ";".join("-".join(map(str, r)) for r in w.person_roles[a]),
                     "items": len(w.items[a]), "received": s.received, "reminders": s.reminders,
                     "answers": s.answers, "referrals": s.referrals, "ignored": s.ignored,
                     "help_time": round(s.help_time, 2), "own_time": round(s.own_time, 2),
                     "backlog_at_end": round(s.help_backlog_at_h, 2), "alive": s.alive})
    return rows


NEWCOMER_QUARTERS = 2       # joined in the last half year of the history


def _v5_metrics(sim: Sim, qs, n: int) -> dict:
    """Load on the very busiest, and how newcomers fare (DESIGN.md §14.4).

    Newcomers are agents that joined in the last half year. They can be slow
    to *find* help (they know few others) and slow to *be found* (few others
    know them): "found ratio" compares the correct answers they gave per item
    they hold with the same ratio for everyone else (1 = found as often as
    their knowledge would justify, below 1 = overlooked)."""
    w, st = sim.world, sim.state
    k1 = max(1, int(round(0.01 * len(st))))
    inbox = [s.received + s.reminders for s in st]
    new = np.asarray(w.tenure) <= NEWCOMER_QUARTERS
    ok = lambda q: q.status == "ok" and q.correct
    out = {
        "top1_share_inbox": _top_share(inbox, k1),
        "top1_share_reads": _top_share([s.reads for s in st], k1),
        "newcomer_share": float(new.mean()),
        "correct_newcomers": _rate([q for q in qs if new[q.asker]], ok),
        "correct_others": _rate([q for q in qs if not new[q.asker]], ok),
    }
    given = np.zeros(sim.n)
    for q in qs:
        for helper, right, _ in q.helpers:
            given[helper] += right
    held = np.array([len(items) for items in w.items], dtype=float)
    received = np.array([s.received for s in st], dtype=float)

    def per_item(values, mask):
        return values[mask].sum() / max(1.0, held[mask].sum())

    if new.any() and (~new).any():
        others = per_item(given, ~new)
        out["found_ratio_newcomers"] = float(per_item(given, new) / others) if others > 0 else float("nan")
        others = per_item(received, ~new)
        out["asked_ratio_newcomers"] = float(per_item(received, new) / others) if others > 0 else float("nan")
        known_by = np.zeros(sim.n)
        for m in w.memory:
            for b in m.known_positive():
                known_by[b] += 1
        out["known_by_newcomers"] = float(known_by[new].mean())
        out["known_by_others"] = float(known_by[~new].mean())
    return out
