# WhoKnows v5 (Phases 1 and 2 of the NANDA version)

**Do the company results hold in an open network of 1,000 agents, and who is overlooked there?**

v5 = v4 (Phase 1: agent timing, human approvals, priorities) + Phase 2 of the "WhoKnows for NANDA" plan:

- **An open network instead of one company.** The same four-year history, with other settings: 100 → 1,000 agents, 20 communities instead of offices, 83 groups on 28 platform lanes instead of client teams, no leadership, a fixed number of contacts outside one's community, more agents leaving and moving (`whoknows/network.py`).
- **A general topic space.** Knowledge is (topic, lane, aspect) in 40 domains of 6 topics; vectors are built from random components whose weights reproduce the similarities of v3's text vectors (`whoknows/topics.py`).
- **New measures:** load on the busiest 1 %, and newcomers: how well they find help and how often they are found for what they know.
- **A gate:** the generalised code reproduces v3 bit for bit with the company's settings, and the company described with the network's vectors gives the v3 results within the noise.

Design and expectations (written before the runs): `DESIGN.md` §14. Results: `RESULTS_V5.md`; every number quoted: `results/key_numbers_v5.md`.

```bash
python -m whoknows.experiments --scenario gate --seeds 10 --out results
python -m whoknows.experiments --scenario net_size,net_speed --seeds 5 --out results
python -m whoknows.experiments --scenario net_priority,net_inflation --seeds 4 --out results
python -m whoknows.report_v5 --runs results/runs.csv --out results
pytest -q          # 28 v3 tests + 24 v4 tests + 7 v5 tests
```

---

## v4 (Phase 1 of the NANDA version)

**Does the v3 result hold when people are replaced by their agents, and who should set a question's priority?**

v4 keeps the v3 company and its four-year history and adds, for Phase 1 of the "WhoKnows for NANDA" plan:

- **Agent timing:** seconds instead of minutes, four parallel calls, a full agent refuses at once ("rate limited") instead of letting messages sink, no reminders, and every message read counts as a cost.
- **Human approvals:** in the mixed profile, some answers wait for the owner's human (decisions, data access).
- **Priorities:** none, set by the asker, set by the answerer (who reads every ask to rank it), asker-set with spot checks (audit), and a budget of high labels per asker.
- New measures: reads per question and who does them, refusals, approval waits, answered share and wait by true importance.

With the default settings v4 reproduces v3 exactly. The design and the expectations, written before the runs, are in `DESIGN.md` §13 (§13.8: a bug found in review and the rerun); results in `RESULTS_V4.md`, and every number they quote in `results/key_numbers_v4.md`. `results_first_run/` keeps the faulty first run for comparison.

```bash
python -m whoknows.experiments --scenario speed --seeds 20 --out results
python -m whoknows.experiments --scenario priority_people,priority_agents,agent_load,triage_cost,inflation --seeds 10 --out results
python -m whoknows.report_v4 --runs results/runs.csv --out results
```

---

The rest of this file is the v3 README. The version table at its end names folders of the original project; this repository holds the v5 code, which includes v3 and v4.

# WhoKnows v3

**How can people and their agents find knowledge that nobody declared, without overloading a few senior people and without a central log of everyone's conversations?**

v3 is the third version of the WhoKnows simulator. It keeps the question of v1 and the reminders of the follow-up branch (v2), and fixes v1's known weak spots:

- **No ground truth for seniors.** Four years of company history are simulated (40 → 130 people, 1 → 6 offices). Everything anyone knows about colleagues comes from working with them, sharing an office, or past questions.
- **Calibrated to a field study.** Size, growth, offices and cross-office visibility come from a culture study of a real software company (anonymised; see `DESIGN.md` §2).
- **Four kinds of question:** content, whom to ask, technical issue (two pieces of knowledge), decision (only the owner can answer). Partial answers, help from similar work in another client team, honest mistakes.
- **Realistic load:** own work, deadline peaks, reminders, withdrawn questions, a BUSY reply that costs time, load estimated from response times.
- **A new strategy, signed track records:** coarse public counts ("answered questions in topic T, signed by N different people") instead of a central log.
- **Real language:** every item, question and profile is text, embedded with a real model (spaCy word vectors with SIF weighting; the baseline is also run with `all-MiniLM-L6-v2`).
- **Robustness:** 20 seeds for the baseline, 10 for every sweep, sensitivity sweeps over every parameter I chose myself, all changes after the first run logged in `DESIGN.md` §12.

Read `DESIGN.md` first, then `RESULTS.md`. The written paper is "WhoKnows v3" (exported as PDF next to this folder).

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.8.0/en_core_web_md-3.8.0-py3-none-any.whl
pytest -q                                                            # 28 tests

python -m whoknows.experiments --scenario baseline --seeds 20 --out results   # ~8 min on 2 cores
python -m whoknows.experiments --scenario sweeps --seeds 10 --out results     # ~100 min on 2 cores
python -m whoknows.report --runs results/runs.csv --out results

# optional: the baseline with all-MiniLM-L6-v2 (put model.onnx + tokenizer.json in models/all-MiniLM-L6-v2)
pip install onnxruntime tokenizers
python -m whoknows.experiments --scenario minilm --seeds 20 --out results_minilm
```

The first run builds the embedding cache (`.cache/`, about 30 s) and one company history per seed and configuration (about 7 s each, cached).

## Layout

```
DESIGN.md                 the model, fixed before the first run, plus every later change (§12)
RESULTS.md                what came out, with caveats
whoknows/text.py          the text world: topics, items, questions, roles, profiles (anonymous clients)
whoknows/embed.py         embedding tiers: synthetic vectors, or a real model over the text
whoknows/company.py       four years of history: growth, teams, careers, who learns what about whom
whoknows/memory.py        who-knows-what memory (prototypes with positive/negative evidence)
whoknows/sim.py           the two measured weeks: questions, inboxes (urgent/normal/own work), reminders
whoknows/strategies.py    nine strategies + a random-walk control
whoknows/metrics.py       correct/wrong by kind of question, load, overtime, privacy, robustness
whoknows/experiments.py   scenarios + parallel runner -> results/runs.csv
whoknows/report.py        figures + markdown tables
tests/                    pytest (history, protocol, inbox bookkeeping, adversaries)
results/                  runs.csv (one row per run), summary.csv, figures, tables
results_minilm/           the baseline again with all-MiniLM-L6-v2
models/                   put the MiniLM files here (not committed: 90 MB)
```

## Versions

| version | folder | what it added |
|---|---|---|
| v1 | `Knowledge Distirbution Project/whoknows` | the simulator, eight strategies, NANDA Town plugin |
| v2 | `Knowledge Distirbution Project/whoknows-followups` | reminders: chasing unread messages |
| v3 | this folder | history instead of ground truth, field-study calibration, four kinds of question, own work, track records, text + real embeddings, sensitivity |

The NANDA Town plugin is still the v1 one; porting v3 to it is a next step.
