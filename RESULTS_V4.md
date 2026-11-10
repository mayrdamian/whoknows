# WhoKnows v4, Phase 1 – results

The v3 company (130 people, 6 offices, four years of history) with every person
replaced by their agent, and five ways of setting a question's priority. Design
and expectations, written before the runs: `DESIGN.md` §13. 1,610 runs:
20 seeds for the speed scenario, 10 for the rest. Full tables with 95 %
intervals: `results/table_v4_*.md`; every number quoted here, computed from the
runs: `results/key_numbers_v4.md`; one row per run: `results/runs.csv`.

**Rerun after review (9 Nov).** A review before publishing found that the
agent profile gave agents a quarter of the own work it was meant to (the
speed-up for parallel calls also applied to the owner's tasks). It was fixed
and every agent scenario was rerun (`DESIGN.md` §13.8). Everything below is
from the rerun; the first run is kept in `results_first_run/`. People runs
were not affected.

**In one sentence:** fast agents remove the waiting but not the hubs – asking
the oldest agent answers 69 % instead of 54 % yet still sends 47 % of messages
to 5 % of agents – and a priority set by the asker halves urgent waits at those
hubs at no extra reading, while making the receiver rank every message more
than doubles the reading and costs answers.

## 1. People vs agents (30 questions per agent per hour, 20 seeds)

| strategy | correct, people → agents | busiest 5 % get, people → agents | wrong (agents) | messages read per question | refusals per question | slowest 10 % of approvals wait |
|---|---|---|---|---|---|---|
| Learned, local | 83 % → 80 % | 21 % → 19 % | 9 % | 2.7 | 0.32 | 29 min |
| Signed track records | 79 % → 79 % | 21 % → 21 % | 9 % | 2.9 | 0 | 29 min |
| Search + learned (hybrid) | 78 % → 77 % | 17 % → 17 % | 9 % | 3.2 | 0 | 29 min |
| Learned, local, load-aware | 76 % → 76 % | 17 % → 17 % | 9 % | 3.4 | 0 | 29 min |
| Learned, central log | 76 % → 73 % | 34 % → 29 % | 15 % | 2.6 | 0.32 | 32 min |
| Ask the senior → oldest agent | 54 % → 69 % | 66 % → 47 % | 13 % | 3.0 | 0.40 | 31 min |
| Declared search | 65 % → 62 % | 21 % → 19 % | 7 % | 3.7 | 0.44 | 31 min |
| Declared search, trust-ranked | 62 % → 59 % | 23 % → 21 % | 9 % | 3.7 | 0.45 | 32 min |
| Phonebook | 62 % → 59 % | 11 % → 11 % | 6 % | 3.8 | 0.42 | 28 min |

* Agents remove the sinking: nobody waits half a day for a reply any more. That
  helps asking the oldest agent most (+15 points); its hubs still receive 47 %
  of all messages and do 46 % of all reading.
* Reading cost: learned local memory reads 27 % fewer messages per question than
  search over declared skills (2.7 against 3.7), signed track records 21 %
  fewer. Search + learned and learned local, load-aware read only 13 % and 9 %
  fewer, because each BUSY reply is a read too (0.6–0.7 per question; signed
  track records get them as well, 0.6 per question); in exchange these three
  meet no refusals.
* Human approvals (20 % of decisions, 2 % of content and technical answers)
  barely change the answered share (within 0.3 points). The typical approval
  takes 5 minutes; the slowest 10 % wait 28–32 minutes. 48–54 % of approvals
  land with the 5 % of humans who approve most, under every strategy, because
  decisions go to owners.

## 2. Rising load (agents, 10 seeds; 30/h from the 20-seed speed runs)

| questions per agent per hour | 15 | 30 | 60 | 120 |
|---|---|---|---|---|
| Ask the oldest agent: correct | 70 % | 69 % | 69 % | 64 % |
| Ask the oldest agent: refusals per question | 0.37 | 0.40 | 0.75 | 1.62 |
| Ask the oldest agent: busiest 5 % get | 47 % | 47 % | 50 % | 56 % |
| Ask the oldest agent: slowest 10 % wait | 44 s | 47 s | 61 s | 71 s |
| Learned, local: correct | 80 % | 80 % | 80 % | 78 % |
| Learned, local, load-aware: correct | 76 % | 76 % | 76 % | 74 % |
| Learned, local, load-aware: refusals per question | 0 | 0 | 0 | 0 |
| Learned, local, load-aware: slowest 10 % wait | 29 s | 30 s | 31 s | 35 s |

Refusals and losses appear at the hubs first: asking the oldest agent loses 7
points from 15 to 120 questions per hour, learned routing 2–3.

## 3. Who sets the priority (10 seeds)

Agents at 60 questions per agent per hour:

| rule | ask the oldest: correct | urgent: typical wait | reads per question | learned local: correct | urgent: typical wait | reads |
|---|---|---|---|---|---|---|
| none | 69 % | 31 s | 2.8 | 80 % | 17 s | 2.5 |
| asker | 70 % | 16 s | 2.8 | 82 % | 14 s | 2.5 |
| budget | 69 % | 16 s | 2.8 | 80 % | 15 s | 2.5 |
| audit | 69 % | 16 s | 3.5 | 81 % | 15 s | 3.1 |
| answerer, 2 s per triage read | 55 % | 44 s | 7.2 | 79 % | 16 s | 5.5 |
| answerer, triage takes no time | 69 % | 13 s | 6.3 | 81 % | 14 s | 5.4 |
| answerer, 8 s per triage read | 23 % | 15 s | 7.4 | 72 % | 25 s | 6.1 |

People (two weeks): asking the senior answers 55 % with no priority (urgent
questions wait 4.8 h), 56 % with asker labels (4.1 h), 44 % when the senior
reads and ranks everything (2.2 h), 53 % with audits (3.5 h), 56 % with a
budget (4.8 h). Learned local memory answers 84 % under every rule.

* Priorities matter most where work queues up – at the hubs of asking the
  oldest agent or the senior. Under learned routing, asker labels still help a
  little (urgent waits 17 → 14 s, +1.5 points answered).
* Under asking the oldest agent, 63 % of all triage reads are done by the 5 %
  of agents who triage most.
* Inflation (share of askers labelling everything urgent), urgent wait under
  asking the oldest agent at 0 / 30 / 60 % inflaters: asker labels 13.9 / 15.5 /
  21.3 s (± 3.2 at 60 %); budget 14.2 / 16.4 / 21.7 s (± 2.3); audit 14.6 /
  15.9 / 18.1 s (± 1.1). No priority: 30.7 s. At 60 % inflaters asker labels no
  longer separate urgent from low-importance questions (21.3 s against
  21.8 s); audits still do (18.1 s against 21.5 s), at 25 % more reading.

## 4. Expectations (DESIGN.md §13.6)

| # | expectation | outcome |
|---|---|---|
| 1 | agents remove the sinking; asking the oldest agent answers far more but still concentrates load and gets more wrong; learned local stays first | confirmed (54 % → 69 %; 47 % of messages at 5 %; 13 % wrong against 9 %); learned local first, signed track records within a point |
| 2 | refusals appear at the hubs first; asking the oldest agent loses most | confirmed (refusals 0.37 → 1.62 per question; −7 points against −2 to −3) |
| 3 | humans behind decision owners become the slow part for every strategy | confirmed (48–54 % of approvals at 5 % of humans; slowest 10 % wait about half an hour) |
| 4 | asker labels speed up urgent questions at hubs, lose that with inflation; audit and budget recover part | confirmed for asker labels and audits; the budget recovers nothing at 60 % inflaters (21.7 s against 21.3 s) |
| 5 | answerer ranking is accurate but its reading lands on hubs and costs answers; with free triage it is best | confirmed (−14 points at 2 s per read; fastest urgent answers with free triage, but 2.3 times the reading) |

In the first (faulty) run, expectation 1 had failed at the top (track records
first) and the costs in 2 and 5 were smaller; the fix made agents as busy as
designed.

## 5. Limits

* All agent numbers (answer times, rates, parallel calls, own work, approval
  shares and times, the importance mix, how often askers inflate) are
  assumptions; the scenarios sweep the ones that drive the results.
* The company, its history and its question kinds are still v3's; the open
  network with general tasks is Phase 2.
* Parallel calls are modelled as one queue that handles messages four times
  faster; own work is not sped up.
* A refused asker moves on instead of retrying after the Retry-After time.
* The code was reviewed by me, not by an independent person; the review found
  the own-work bug above and a docstring that did not match the code.
