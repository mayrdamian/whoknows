# WhoKnows v6, Phase 3 – results

Phase 3 asks whether the Phase 2 results hold when the open network grows
from 1,000 to 10,000 agents. Design, gate and amendments: `DESIGN.md` §15
(§15.2 gate written before its runs; §15.4 amendments before the size runs;
§15.5 outcome). Tables with 95 % intervals: `results/table_v6_*.md`; every
number quoted here: `results/key_numbers_v6.md`; one row per run:
`results/runs.csv`. 45 gate runs (5 seeds) and 81 size runs (3 seeds).

**In one sentence:** at 10,000 agents every strategy answers less, but very
unequally – search ranked by signed track records stays first (71 % → 62 %)
and plain search over declared AgentFacts holds best (65 % → 59 %), while an
agent's own memory halves (51 % → 27 %) and asking the oldest agent collapses
to 11 %, with the 10 busiest agents receiving three-quarters of all messages.

## 0. What was built, and the gate

v6 adds options that let the simulator reach 10,000 agents on two cores and
7 GB: contacts drawn per agent instead of per pair, a memory limit of 200
agents, topic vectors built on demand, an approximate search index (HNSW),
own work scheduled one block at a time, and a topic space that grows with the
network (28 lanes and 40 domains per 1,000 agents). Everything else is
unchanged, and with the options off the code reproduces v5 bit for bit (a
fingerprint of a v3 world and eight runs and of two network worlds and nine
runs). Speed-ups that change no result (same fingerprints) bring a
10,000-agent world down to under 5 minutes.

**Gate** (1,000 agents, one hour of questions, every option on, against
Phase 2 on the same 5 seeds): largest difference 2.0 points (central log
57.0 % → 55.0 %), all others within 1.2 points; rank correlation 1.00;
asking the oldest agent, busiest 1 % get 67 % → 67 %. **Passed.**

## 1. From 1,000 to 10,000 agents

Both sizes at the same settings: a quarter of an hour of questions at 30 per
agent per hour (about 7,500 and 75,000 questions), the deadline peaks spread
over the hour. Short runs answer a little less than an hour for learned
routing (agents learn during the run), so these 1,000-agent numbers are
below Phase 2's.

| strategy | answered: 1,000 → 10,000 agents | 10 busiest agents get | reads per question | refusals per question | undeclared knowledge found |
|---|---|---|---|---|---|
| Signed track records | 71 % → 62 % | 13 % → 5 % | 3.6 → 4.0 | 0.00 → 0.00 | 51 % → 39 % |
| Search + learned (hybrid) | 70 % → 61 % | 12 % → 5 % | 3.7 → 4.1 | 0.00 → 0.00 | 50 % → 38 % |
| Declared search | 65 % → 59 % | 12 % → 7 % | 3.6 → 3.6 | 0.36 → 0.66 | 26 % → 25 % |
| Declared search, trust-ranked | 61 % → 55 % | 13 % → 8 % | 3.6 → 3.6 | 0.35 → 0.71 | 26 % → 25 % |
| Learned, central log | 53 % → 41 % | 28 % → 19 % | 3.5 → 3.1 | 0.68 → 1.79 | 48 % → 31 % |
| Learned, local | 51 % → 27 % | 11 % → 3 % | 4.6 → 5.7 | 0.49 → 0.71 | 48 % → 26 % |
| Learned, local, load-aware | 48 % → 26 % | 9 % → 2 % | 5.4 → 6.5 | 0.00 → 0.00 | 44 % → 23 % |
| Phonebook | 21 % → 16 % | 3 % → 0 % | 6.0 → 6.3 | 0.58 → 0.70 | 17 % → 12 % |
| Ask the senior / oldest agent | 30 % → 11 % | 69 % → 76 % | 2.9 → 1.7 | 3.72 → 5.69 | 28 % → 7 % |

("10 busiest agents" = the busiest 1 % at 1,000 and the busiest 0.1 % at
10,000.)

* **Search holds best.** Declared search loses 6 points, track records and
  the hybrid 9. Track records stay first, but their lead over plain declared
  search shrinks from 6 points to 3, and the undeclared knowledge they find
  falls from 51 % to 39 % (declared search: 26 % → 25 %).
* **An agent's own memory does not scale.** Learned local memory falls from
  51 % to 27 %, with and without load-awareness. An agent is known by about
  90 others at both sizes (newcomers by about 31): 9 % of the network at
  1,000 agents, under 1 % at 10,000.
* **Asking the oldest agent collapses:** 11 % answered, 76 % of all messages
  to 10 agents, 5.7 refusals per question.
* **One central log becomes a hub of its own:** 41 % answered with 14 % wrong
  answers, the busiest 1 % (100 agents) receive 46 % of all messages, and it
  is by far the most expensive to run (23 minutes per run against 2–4 for the
  others).
* **Load spreads less under search too:** the busiest 1 % of agents receive
  19–23 % of messages under the search strategies at 10,000 agents, against
  12–13 % at 1,000 (wide intervals with 3 seeds).
* **Newcomers** (31 % of agents) find help almost as well as others under
  search (within 1.5 points), and under asking the oldest agent they are
  still overlooked as helpers (per item they hold, 0.04 times the asks
  others get).

## 2. What changed in the questions (an amendment, §15.4)

A question is about knowledge someone holds. The v3 rule draws a topic by
popularity up to 30 times until someone holds it in the lane asked about.
In a topic space that grows with the network that failed for 55 % of
questions at 10,000 agents, which would have halved the load. v6 draws among
the topics held in the lane, with the same weights. At 1,000 agents this
changes the answered share by at most 3 points (asking the oldest agent:
33 % → 30 %, with 8 % more questions), the rest by 1.2 points or less
(`table_v6_size.md`, "Phase 2 questions").

## 3. 100,000 agents

Not run: by the measured growth a 100,000-agent world needs about 17 GB and
a run about 32 GB, against 7 GB here (§15.5). Time would not be the limit
(about an hour for a world and 40 minutes for a run), except for the
central log.

## 4. Limits

* No expectations were written down before the size runs (§15.5): the
  10,000-agent results are exploratory.
* 3 seeds per point: differences of 3–4 points between strategies at one
  size are within the noise (intervals in `table_v6_size.md`).
* A quarter of an hour of questions per run: learned routing has less time
  to learn than in Phase 2's hour.
* The size comparison changes more than size: the topic space grows with the
  network, and question topics are drawn by v6's rule at both sizes.
* All agent and network settings are assumptions, as in Phases 1 and 2; the
  memory limit of 200 never binds at these sizes, so its effect is untested.
* The code was reviewed by me, not by an independent person.
