# WhoKnows v5, Phase 2 – results

The questions of v3 and Phase 1 asked again in an open network of agents:
no company, 100 → 1,000 agents over four years, 20 communities, 83 groups on
28 platform lanes, a topic space of 240 topics in 29 lanes. Design and
expectations, written before the runs: `DESIGN.md` §14 (§14.8: the gate failed
first and the vectors were refitted). Tables with 95 % intervals:
`results/table_v5_*.md`; every number quoted here: `results/key_numbers_v5.md`;
one row per run: `results/runs.csv`. 180 gate runs (10 seeds) and 244
open-network runs (4–5 seeds).

**In one sentence:** in an open network of 1,000 agents, what one agent has
learned by itself is no longer enough – learned local memory falls from 80 % of
questions answered at 130 agents to 57 %, below search over declared AgentFacts
(67 %) – while signed track records, which add network-wide evidence of past
answers to search, stay best (73 %); asking the oldest agent collapses to 36 %,
with 10 agents receiving two-thirds of all messages.

## 0. The gate: the company in network terms

The generalised code reproduces v3 exactly with the company's settings (a
fingerprint of a world and eight runs is bit-identical, and all v3 and v4
tests pass). With the open network's topic vectors instead of v3's sentence
embeddings, the company gives (people timing, 10 seeds, against v3's 20):

| strategy | v3 | network vectors | Phase 1 agents | network vectors, agents |
|---|---|---|---|---|
| Learned, local | 83 % | 79 % | 80 % | 77 % |
| Signed track records | 79 % | 78 % | 79 % | 78 % |
| Search + learned (hybrid) | 78 % | 76 % | 77 % | 76 % |
| Learned, local, load-aware | 76 % | 74 % | 76 % | 73 % |
| Learned, central log | 76 % | 75 % | 73 % | 72 % |
| Declared search | 65 % | 65 % | 62 % | 62 % |
| Declared search, trust-ranked | 62 % | 62 % | 59 % | 59 % |
| Phonebook | 62 % | 61 % | 59 % | 59 % |
| Ask the senior / oldest agent | 54 % | 52 % | 69 % | 68 % |

Largest difference 3.3 points, rank correlation 0.98 for people and for
agents; asking the senior still sends 68 % of messages to 5 % of people.
**Passed.** On the same seeds the network vectors are 1–4 points lower for
every strategy (learned local the most, 4.4 points), so a small offset in
level remains; the order and the gaps do not change. The first attempt,
with simpler vectors, failed (§14.8, `results/gate_first_attempt.md`).

## 1. From a company-sized network to 1,000 agents (agents, 30 questions per agent per hour)

| strategy | answered: 130 → 300 → 1,000 agents | busiest 1 % get (1,000) | reads per question (1,000) | refusals per question (1,000) | undeclared knowledge found (1,000) |
|---|---|---|---|---|---|
| Signed track records | 81 % → 79 % → 73 % | 12 % | 3.3 | 0.00 | 55 % |
| Search + learned (hybrid) | 80 % → 77 % → 72 % | 11 % | 3.5 | 0.00 | 54 % |
| Declared search | 66 % → 63 % → 67 % | 10 % | 3.3 | 0.43 | 27 % |
| Declared search, trust-ranked | 65 % → 62 % → 63 % | 13 % | 3.4 | 0.46 | 28 % |
| Learned, local | 80 % → 73 % → 57 % | 19 % | 4.0 | 0.57 | 53 % |
| Learned, central log | 78 % → 70 % → 57 % | 26 % | 3.2 | 0.59 | 54 % |
| Learned, local, load-aware | 77 % → 69 % → 55 % | 14 % | 4.8 | 0.00 | 50 % |
| Ask the senior / oldest agent | 70 % → 61 % → 36 % | 67 % | 2.9 | 3.30 | 34 % |
| Phonebook | 57 % → 49 % → 21 % | 3 % | 6.0 | 0.61 | 16 % |

* **Asking the oldest agent collapses with size:** 70 % → 61 % → 36 %. At
  1,000 agents the 10 busiest agents (1 %) receive 67 % of all messages, and
  questions meet 3.3 refusals each.
* **Learned memory alone does not scale:** learned local memory 80 % → 73 % →
  57 %, central log 78 % → 70 % → 57 % (with 15 % wrong answers). One agent's
  notes cover a shrinking part of the network: newcomers are known by 31
  agents, others by 91, out of 1,000.
* **Search over declared AgentFacts holds its level** (66 % → 63 % → 67 %) and
  overtakes learned local memory at 1,000 agents, but still finds only 27 % of
  undeclared knowledge, against 50–55 % for the strategies that learn from
  outcomes.
* **Combining both wins:** signed track records (search over declared skills
  ranked by signed receipts of past answers) 81 % → 79 % → 73 %, and declared
  search for the first hop with learned routing after it 80 % → 77 % → 72 %.
  Both spread the load (busiest 1 %: 11–12 %) and meet no refusals.
* At 1,000 agents three groups share each platform lane, so most knowledge has
  more holders than at 300; this helps every strategy that searches and is
  part of why declared search does not fall with size.
* Reading cost per question rises with size for learned routing (2.7 → 4.0
  messages read for learned local memory), less for track records (2.8 → 3.3).

## 2. Newcomers (joined in the last half year: 31 % of agents at 1,000)

| strategy | newcomers' questions answered | others' questions answered | asks per item held, newcomers ÷ others |
|---|---|---|---|
| Signed track records | 73 % | 73 % | 1.78 |
| Search + learned (hybrid) | 71 % | 72 % | 1.77 |
| Declared search | 67 % | 67 % | 2.54 |
| Declared search, trust-ranked | 63 % | 63 % | 1.92 |
| Learned, local | 56 % | 58 % | 0.90 |
| Learned, central log | 56 % | 57 % | 0.42 |
| Learned, local, load-aware | 54 % | 56 % | 1.04 |
| Ask the senior / oldest agent | 34 % | 37 % | 0.10 |
| Phonebook | 14 % | 25 % | 2.47 |

* **Newcomers find help as well as everyone else** (within 2 points under
  every strategy except the phonebook), although they know a third as many
  agents: most questions are about their own lane, where their group knows.
* **They are overlooked as helpers where routing follows reputation:** per
  item they hold, newcomers receive a tenth of the asks under asking the
  oldest agent (0.10) and less than half under the central log (0.42); about
  par under learned local memory (0.90); and more than others under declared
  search (2.5), because their AgentFacts describe all they know while older
  agents also hold knowledge they no longer declare.

## 3. Human approvals at 1,000 agents

| strategy | approvals given by the busiest 5 % of humans | typical approval wait | slowest 10 % wait |
|---|---|---|---|
| Signed track records | 67 % | 8.4 min | 40 min |
| Declared search | 68 % | 8.4 min | 40 min |
| Learned, local | 71 % | 7.1 min | 33 min |
| Learned, local, load-aware | 71 % | 7.7 min | 33 min |
| Ask the senior / oldest agent | 80 % | 8.7 min | 32 min |

Approvals concentrate more than in the company: the busiest 5 % of humans
give 67–80 % of all approvals (company: 48–54 %). The typical approval waits
7–9 minutes, the slowest 10 % 32–40 minutes. The answered share changes by
less than half a point.

## 4. Who sets the priority (1,000 agents at 60 questions per agent per hour)

| rule | oldest agent: answered | urgent: typical wait | reads | learned local: answered | urgent wait | track records: answered | urgent wait | reads |
|---|---|---|---|---|---|---|---|---|
| none | 27 % | 33 s | 2.0 | 58 % | 24 s | 71 % | 15 s | 3.4 |
| asker | 30 % | 35 s | 2.2 | 59 % | 17 s | 74 % | 13 s | 3.2 |
| budget | 26 % | 34 s | 2.0 | 58 % | 17 s | 73 % | 13 s | 3.3 |
| audit | 15 % | 12 s | 2.7 | 58 % | 17 s | 73 % | 13 s | 4.0 |
| answerer | 11 % | 12 s | 8.2 | 53 % | 20 s | 69 % | 14 s | 7.2 |

* **Where the hubs are saturated, labels cannot shorten the wait, but they
  decide who gets through.** Under asking the oldest agent (4–5 refusals per
  question), asker labels leave the typical urgent wait at 33–35 s but raise
  the share of urgent questions answered from 32 % to 45 %.
* **Anything that makes the receiver read costs most at the hubs.** Ranking by
  the receiver cuts asking the oldest agent from 27 % to 11 % (−16 points; in
  the company −14) and more than doubles the reading; audits, which read one
  ask in five, already cut it to 15 %. 95–96 % of all triage reads land on the
  busiest 5 % of agents.
* **With spread-out routing the rules matter little:** learned local memory
  58–59 % and track records 71–74 % under asker labels, budget and audits;
  asker labels shorten urgent waits there (24 → 17 s and 15 → 13 s) and raise
  urgent questions answered by 6–7 points; receiver ranking costs 2–4 points.
* **Audits do not help at this size.** At the hubs they cost too much
  reading (asking the oldest agent: 15 % answered); under spread-out routing
  queues are short, and with 60 % of askers inflating neither plain labels nor
  audits keep urgent questions faster than low-importance ones (differences
  of 1 s or less). A receiver there gets on average 0.2 asks per run from any
  one other agent, so it almost never audits the same asker twice and cannot
  build a record of their labels; such a record would have to be shared
  across the network. (In the company, audits helped only at the senior's
  hub: 18.1 s against 21.5 s.)

## 5. Expectations (DESIGN.md §14.7)

| # | expectation | outcome |
|---|---|---|
| 1 | gate passes both checks | passed on the second attempt, after refitting the vectors (first attempt failed by 18.6 points; §14.8) |
| 2 | from 130 to 1,000 agents the oldest agent loses most (≥ 15 points) and its busiest 1 % get > 25 %; learned local loses more than declared search; track records come first | confirmed (70 % → 36 %; busiest 1 % 67 %; learned local −23, declared search +1; track records first, 73 %); partly informed by a smoke test |
| 3 | newcomers found less than their knowledge justifies under learned routing and the oldest agent (< 0.8), about 1 under declared search; as askers ≥ 5 points worse under learned local | partly: overlooked under the oldest agent (0.10 asks per item, relative) and the central log (0.42), not under learned local (0.90); found more under declared search (2.5); as askers *not* worse (within 2 points) |
| 4 | asker labels halve urgent waits at the oldest agents; receiver ranking costs > 14 points there; little effect under learned routing; audits beat plain labels with 60 % inflaters | partly: at saturated hubs labels do not shorten waits but raise urgent questions answered (32 % → 45 %); receiver ranking −16 points (confirmed); little effect elsewhere (confirmed); audits do not beat plain labels (refuted) |
| 5 | busiest 5 % of humans give ≥ 40 % of approvals | confirmed, and more than in the company (67–80 % against 48–54 %) |

## 6. Limits

* All agent numbers are assumptions (see Phase 1); the open network's
  settings (communities, groups, lanes, leaving and moving rates, contacts
  outside one's community) are assumptions too, and only size was varied.
* The topic vectors were fitted to v3's text vectors, so the open network
  inherits v3's similarity structure; a real agent network's questions may be
  more or less similar to each other.
* Fewer seeds than Phase 1 (4–5), so differences of 2–3 points are within the
  noise; the intervals are in the tables.
* Agents do not join or leave during a run; the network a run starts from
  already has newcomers and missing veterans (experiment 6 is Phase 3).
* The number of lanes is fixed at 28, so lanes are shared by more groups in
  larger networks; this is a confound in the size comparison.
* v3 never created the core team its design describes (DESIGN.md §14.1);
  results are what the code produced.
* The code was reviewed by me, not by an independent person.
