"""An open network of agents instead of one company (DESIGN.md §14).

    cfg = network_config(1000, seed=3)
    world = build_world(cfg)

The history is the same process as the v3 company (company.py), with other
settings: agents join and leave over four years, work in groups on platform
lanes, belong to communities instead of offices, and learn about each other
by working together, by being in the same community and, rarely, across
communities. Nobody runs the network: there is no leadership, and the only
authorities are the lead agent of each platform lane (its longest-serving
agent) and the steward of each domain in the shared lane (the agent that
holds most of it, anywhere in the network).

What changes with size:
  * communities: one per 50 agents, opening as the network grows;
  * groups: one per 12 agents, created as the network grows, on 28 platform
    lanes (so about three groups share a lane);
  * the topic space: 40 domains of 6 topics, so 240 topics in 29 lanes
    (about 7,000 topic-lanes) with 6 aspects each;
  * contacts outside one's community: a fixed number per agent and quarter,
    not a probability per pair, so a larger network is not better connected.
Everything else (learning, asking around in the history, what is declared)
is the v3 company's.
"""

from __future__ import annotations

import math
from dataclasses import replace

from .company import CompanyConfig

AGENTS_PER_COMMUNITY = 50
AGENTS_PER_GROUP = 12


def network_config(n_agents: int = 1000, seed: int = 0, **changes) -> CompanyConfig:
    quarters = 16
    start = max(20, n_agents // 10)
    n_communities = max(1, n_agents // AGENTS_PER_COMMUNITY)
    n_groups = max(2, n_agents // AGENTS_PER_GROUP)

    def quarter_reached(size: float) -> int:
        """First quarter in which the network has `size` agents (growth as in company.py)."""
        if size <= start:
            return 0
        return min(quarters, math.ceil(quarters * math.log(size / start) / math.log(n_agents / start)))

    communities = tuple(quarter_reached(start + (n_agents - start) * i / n_communities)
                        for i in range(n_communities))
    # at least three groups from the start, as the company had three client teams
    groups = tuple(0 if i < 3 else quarter_reached(AGENTS_PER_GROUP * (i + 1)) for i in range(n_groups))
    cfg = CompanyConfig(
        quarters=quarters, start_people=start, end_people=n_agents,
        office_opens=communities, hq_hire_share=1.0 / n_communities,
        client_quarters=groups, service_team_quarter=None, n_leadership=0,
        reassign_rate=0.06, attrition_rate=0.04,        # agents are repurposed and retired more often (assumed)
        cross_contacts=4.5,                             # about what a v3 person had per quarter
        stewards="anyone",                              # the steward of a domain is whoever knows it best
        domains=40, topics_per_domain=6, lanes=28, aspects=6,
        tier="network", seed=seed,
    )
    return replace(cfg, **changes)


def company_in_network_terms(seed: int = 0, **changes) -> CompanyConfig:
    """The v3 company, with the open network's topic vectors instead of v3's
    sentences: the first check of the gate (DESIGN.md §14.5)."""
    return replace(CompanyConfig(seed=seed, tier="network"), **changes)
