# WhoKnows v3 – results

All numbers come from simulation of a company whose size, growth, offices and
cross-office visibility are taken from an anonymised field study; the rest is
assumed (DESIGN.md §2–§5). Means over 20 seeds (baseline) or 10 seeds (every
other scenario) with 95 % intervals (Student t). Full tables are in
`results/table_*.md`; one row per run is in `results/runs.csv` (3,260 runs).
The text tier used spaCy word vectors with SIF weighting throughout; the
baseline was also rerun with all-MiniLM (§6).

**In one sentence:** when seniority has to be earned in a simulated company
history, asking the senior answers 54 % of questions and sends two thirds of
all messages to the busiest 5 %; learned routing with local memory answers
76–83 % with about a fifth, and signed track records get 79 % without a
central log.

## 1. Baseline (130 people, 6 offices, 20 seeds)

| strategy | answered correctly | wrongly | undeclared knowledge found | slowest 10 % wait (units) | busiest 5 % get | seniors get | seniors' own work left (units) | central log records |
|---|---|---|---|---|---|---|---|---|
| Learned, local | 83 % | 8 % | 79 % | 45 | 21 % | 26 % | 23 | none |
| Signed track records | 79 % | 9 % | 71 % | 21 | 21 % | 24 % | 18 | none |
| Search + learned (hybrid) | 78 % | 9 % | 68 % | 21 | 17 % | 21 % | 15 | none |
| Learned, local, load-aware | 76 % | 9 % | 70 % | 21 | 17 % | 23 % | 17 | none |
| Learned, central log | 76 % | 14 % | 73 % | 50 | 34 % | 41 % | 42 | ~19,900 |
| Declared search | 65 % | 7 % | 33 % | 44 | 21 % | 19 % | 17 | index |
| Declared search, trust-ranked | 62 % | 9 % | 32 % | 47 | 23 % | 20 % | 19 | index |
| Phonebook | 62 % | 6 % | 50 % | 36 | 11 % | 16 % | 13 | none |
| Ask the senior | 54 % | 9 % | 47 % | 78 | 66 % | 70 % | 55 | none |

1 unit ≈ 10 minutes. Everyone else ends the two weeks with about 8 units of
own work left; under asking the senior, seniors end with 55 (≈ 9 hours).
Figures: `fig1_tradeoff.png`, `fig8_overtime.png`.

Calibration checks (mean over 20 seeds): cross-office awareness 31 % (target
30 %), office awareness 86 %, half of held knowledge undeclared (55 %), a
third of items held by one person (34 %), seniors know about 76 colleagues'
work and have ~8 years' tenure; others know about 56 and have ~2 years.

## 2. By kind of question (baseline)

| strategy | content | whom to ask | technical issue | decision |
|---|---|---|---|---|
| Learned, local | 90 % | 71 % | 78 % | 99 % |
| Signed track records | 87 % | 67 % | 73 % | 100 % |
| Search + learned (hybrid) | 86 % | 68 % | 70 % | 100 % |
| Learned, local, load-aware | 84 % | 66 % | 67 % | 100 % |
| Learned, central log | 88 % | 47 % | 73 % | 100 % |
| Declared search | 72 % | 59 % | 52 % | 100 % |
| Phonebook | 70 % | 63 % | 46 % | 85 % |
| Ask the senior | 65 % | 42 % | 41 % | 85 % |

* Whom-to-ask carries most wrong answers: 19–31 % of them end with a wrong
  name (52 % with the central log), against 3–6 % for content and technical
  questions.
* In 39–60 % of answered content and technical questions, someone from a
  different client team helped.
* Decision share 5 % → 30 %: owners' share of inbox messages rises by 5–8
  points under every strategy (`table_decisions.md`, `fig6_decisions.png`).

## 3. Growth, load, reminders

| people | 54 | 72 | 97 | 130 | 202 |
|---|---|---|---|---|---|
| Ask the senior | 81 % | 77 % | 68 % | 55 % | 37 % |
| Learned, local | 93 % | 90 % | 87 % | 84 % | 80 % |
| Learned, local, load-aware | 84 % | 82 % | 79 % | 77 % | 74 % |
| Signed track records | 85 % | 84 % | 82 % | 79 % | 78 % |
| Declared search | 86 % | 76 % | 71 % | 66 % | 63 % |
| busiest 5 % get, ask the senior | 39 % | 49 % | 55 % | 66 % | 79 % |

* Question rate 0.5× → 2×: ask the senior 72 % → 37 %; learned local
  82–84 %, track records 79–80 %, load-aware 76–77 % (`table_load.md`).
* Reminders 0 → 3: ask the senior 66 % → 38 %; others gain 0–3 points from
  the first reminder and nothing after (`table_reminders.md`). Withdrawn
  questions mean nobody works on stale questions any more.

## 4. When the three longest-serving people leave (mid-period)

Ask the senior 55 % → 28 %; learned local 83 % → 78 %; load-aware 76 % →
73 %; track records 79 % → 74 %; central log 76 % → 66 %; declared search
65 % → 64 %. Handing the leaver's memory to a successor changes nothing
measurable (≤ 1 point), because nobody learns that the successor now knows.
`table_turnover.md`, `fig7_turnover.png`.

## 5. Dishonest agents

10 % keyword stuffers, 5 % confidently wrong answerers, a ring of 5 colluders:

| strategy | honest | dishonest |
|---|---|---|
| Learned, local | 84 % | 79 % |
| Learned, central log | 76 % | 73 % |
| Learned, local, load-aware | 77 % | 72 % |
| Signed track records | 79 % | 68 % |
| Search + learned (hybrid) | 78 % | 68 % |
| Declared search | 66 % | 60 % |
| Ask the senior | 55 % | 54 % |

The index-based strategies lose most. Track records lose no more than the
hybrid without them, so the stuffed profiles hurt, not the fake receipts; but
counting distinct signers did not stop the ring either. Expectation 7 in
DESIGN.md §11 was wrong.

## 6. Synthetic vectors, word vectors, sentence model

| strategy | synthetic (10 seeds) | spaCy word vectors (20) | all-MiniLM (20) |
|---|---|---|---|
| Learned, local | 82 % | 83 % | 81 % |
| Signed track records | 78 % | 79 % | 79 % |
| Search + learned (hybrid) | 77 % | 78 % | 78 % |
| Learned, central log | 83 % | 76 % | 75 % |
| Learned, local, load-aware | 75 % | 76 % | 74 % |
| Declared search | 64 % | 65 % | 67 % |
| Ask the senior | 60 % | 54 % | 51 % |

The ranking is the same in all three tiers except for the central log, which
ties learned local only with synthetic vectors (clients perfectly apart).
MiniLM separates clients better than word vectors and cuts the central log's
wrong answers from 14 % to 12 %, but it stays 6 points behind learned local.
`table_tiers.md`, `results_minilm/summary.csv`.

## 7. Sensitivity (21 variants, 10 seeds each)

Asking the senior is last or second to last in every variant and sends
61–69 % of messages to the busiest 5 %. Learned local is first in 20 of 21
(the exception: a one-day deadline, where track records lead 80 % to 77 %).
The load-aware strategies' gap to learned local depends on the BUSY
threshold (1 h behind: 71 %; 4 h behind: 81 %, track records 84 % = learned
local) and on the contact budget (12 contacts: 82 %). Load-aware settings
(penalty, near-best band) move results by ≤ 1 point. `table_sensitivity.md`,
`table_own_work.md`.

## 8. Expectations (DESIGN.md §11)

| # | expectation | outcome |
|---|---|---|
| 1 | earned seniority: ask the senior answers less than in v1, still concentrates load | confirmed (85 % in v1 → 54 %; 66 % of messages to the busiest 5 %) |
| 2 | decisions load owners under every strategy; role directory best | confirmed |
| 3 | help from other client teams raises answers, with some wrong ones | confirmed (39–60 % of answered questions) |
| 4 | load-aware and track records keep load spread; track records close to central log | confirmed, track records above the central log; load-aware answers ~7 points less than learned local at default settings |
| 5 | ranking survives real-language embeddings | confirmed except the central log (spaCy and MiniLM) |
| 6 | reminders hurt strategies that let messages sink, less than in v2 | confirmed for ask the senior; others gain slightly |
| 7 | stuffers hurt declared search; ring hurts track records less | wrong: index-based strategies lose 11 points, track records included |
