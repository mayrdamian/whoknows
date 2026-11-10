"""The words of the text world: product topics, knowledge items, questions,
roles and self-descriptions (DESIGN.md §4, §7).

A generic B2B software company that builds and runs tailored systems for a
handful of large clients on a shared core platform. Clients are anonymous
("Client Alpha", "Client Beta", ...; distinct words so a word-vector model
can tell them apart). Every sentence also carries a small feature
dict (domain, topic, client, ...) so the synthetic embedding tier can build
vectors for exactly the same objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field

DOMAINS: list[tuple[str, list[str]]] = [
    ("contract lifecycle", ["new contract onboarding", "contract changes", "renewals",
                            "cancellations", "contract status transitions", "contract versioning"]),
    ("pricing", ["rate tables", "discount rules", "the price calculation engine",
                 "rounding rules", "currency handling", "price simulations"]),
    ("billing and payments", ["invoicing", "payment collection", "dunning", "refunds",
                              "payment file formats", "payment reconciliation"]),
    ("documents", ["letter templates", "the document generation service", "document archiving",
                   "e-signatures", "print output", "document translations"]),
    ("reporting", ["regulatory reports", "management dashboards", "data exports",
                   "audit trails", "month-end reports", "KPI definitions"]),
    ("data migration", ["legacy data import", "field mapping rules", "data validation checks",
                        "migration reruns", "cut-over planning", "data cleansing"]),
    ("interfaces", ["the client API", "batch file interfaces", "authentication and single sign-on",
                    "the partner portal", "message queues", "interface monitoring"]),
    ("build and operations", ["the build pipeline", "deployments", "test environments",
                              "performance tuning", "logging", "incident handling"]),
]

N_TOPICS_PER_DOMAIN = 6
CLIENT_NAMES = [f"Client {c}" for c in [
    "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
    "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi"]]

# six items ("aspects") per (topic, system); the same aspect in another client
# system is an analogue ("similar work done for another client")
CLIENT_ITEM_TEMPLATES = [
    "how {topic} is configured in the {client} system",
    "the custom {topic} logic built for {client}",
    "known problems with {topic} in the {client} system",
    "the data model behind {topic} in the {client} system",
    "the test cases for {topic} in the {client} system",
    "why {topic} was changed for {client} last year",
]
CORE_ITEM_TEMPLATES = [
    "how {topic} works in the shared core platform",
    "the core platform's extension points for {topic}",
    "the performance limits of {topic} in the core platform",
    "the data model behind {topic} in the core platform",
    "the core platform's test suite for {topic}",
    "the design decisions behind {topic} in the core platform",
]
N_ASPECTS = len(CLIENT_ITEM_TEMPLATES)

QUESTION_TEMPLATES = {
    "content": [
        "Can someone explain {item}?",
        "How does {topic} work for {where}? I need to understand {item}.",
        "Where can I learn about {item}?",
    ],
    "whom": [
        "Who knows about {item}?",
        "Who should I ask about {topic} for {where}?",
        "Has anyone here worked on {item}?",
    ],
    "technical": [
        "Something fails in {topic} for {where}; I think it is about {item}. How do I fix it?",
        "We get errors around {item}. Can someone help me debug it?",
        "{topic} is broken for {where} and I am stuck on {item}. Any idea?",
    ],
    "decision": [
        "Can we change {topic} for {where}? Who decides on {item}?",
        "I need a decision about {item}.",
        "Are we allowed to change {topic} for {where}?",
    ],
}
COMPANY_DECISION_TEMPLATES = [
    "Can we change how we handle {topic} across all clients?",
    "I need a company-wide decision about {topic}.",
    "Who decides on our general approach to {topic}?",
]


def topic_name(topic: int) -> str:
    return DOMAINS[topic // N_TOPICS_PER_DOMAIN][1][topic % N_TOPICS_PER_DOMAIN]


def domain_name(domain: int) -> str:
    return DOMAINS[domain][0]


def where(client: int) -> str:
    """'Client C' or 'the core platform' (client = -1)."""
    return "the core platform" if client < 0 else CLIENT_NAMES[client]


@dataclass(frozen=True)
class Sentence:
    """A piece of text plus the facts it is about (for the synthetic tier)."""
    text: str
    domain: int
    topic: int | None = None
    client: int | None = None      # -1 = core platform, None = company-wide
    k: int | None = None           # item index within (topic, system)
    kind: str = "item"             # item | question:<type> | work | role | decision-role
    variant: int = 0
    extra: tuple = field(default_factory=tuple)


def item_sentence(topic: int, client: int, k: int) -> Sentence:
    templates = CORE_ITEM_TEMPLATES if client < 0 else CLIENT_ITEM_TEMPLATES
    text = templates[k].format(topic=topic_name(topic), client=where(client))
    return Sentence(text, topic // N_TOPICS_PER_DOMAIN, topic, client, k, "item")


def question_sentence(qtype: str, topic: int, client: int | None, k: int,
                      variant: int) -> Sentence:
    """A question about item (topic, client, k); client None = company-wide decision."""
    domain = topic // N_TOPICS_PER_DOMAIN
    if client is None:
        text = COMPANY_DECISION_TEMPLATES[variant].format(topic=topic_name(topic))
        return Sentence(text, domain, topic, None, k, "question:decision", variant)
    item = item_sentence(topic, client, k).text
    text = QUESTION_TEMPLATES[qtype][variant].format(item=item, topic=topic_name(topic),
                                                     where=where(client))
    text = text[0].upper() + text[1:]
    return Sentence(text, domain, topic, client, k, f"question:{qtype}", variant)


def work_sentence(topic: int, client: int) -> Sentence:
    """What someone works on: a declared skill, or what colleagues see."""
    text = f"I work on {topic_name(topic)} for {where(client)}."
    return Sentence(text, topic // N_TOPICS_PER_DOMAIN, topic, client, None, "work")


def role_sentence(role: tuple) -> Sentence:
    """Public roles: ('lead', client), ('owner', domain) or ('leadership',)."""
    if role[0] == "lead":
        c = role[1]
        text = (f"Lead of the {where(c)} team; decides on changes to the {where(c)} system.")
        return Sentence(text, -1, None, c, None, "decision-role")
    if role[0] == "owner":
        d = role[1]
        text = (f"Owner of {domain_name(d)} in the core platform; decides on changes "
                f"to {domain_name(d)}.")
        return Sentence(text, d, None, -1, None, "decision-role")
    return Sentence("Member of the leadership team; decides on company-wide questions.",
                    -1, None, None, None, "decision-role")
