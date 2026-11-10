# WhoKnows v3 – design

*Written 6 Nov 2026, before any v3 result was looked at. Every later change
is listed in §12 with the reason, so nobody mistakes it for a choice made in
advance.*

The question stays the same as in v1:

> How can people and their agents find knowledge that nobody declared, by
> learning who knows what from past interactions, without piling the load
> onto a few senior people and without a central log of everyone's
> conversations?

v1 answered it in a model with known weak spots (its own §10 and the paper's
limitations). The follow-up branch (v2) added reminders. v3 fixes the weak
spots it can, keeps reminders, and grounds the organisation in numbers from
a field study.

## 1. What v3 fixes

| weak spot in v1 | what v3 does |
|---|---|
| Seniors got a perfect starting picture of who knows what (ground truth). Results depended on it. | Nobody gets ground truth. Four years of company history are simulated; whatever anyone knows about colleagues comes from working with them, sharing an office, or past questions. Seniority is just tenure. |
| Synthetic organisation, nothing calibrated. | Size, growth and offices from a field study of a real software company (anonymised, §2). Remaining assumptions are labelled and swept. |
| Undeclared knowledge set by a parameter. | It emerges: people are moved between client teams and keep what they learned; only current work is declared. |
| Knowledge all-or-nothing; one kind of question. | Four question types (content, whom to ask, technical issue, decision), partial answers, help from similar work in another client team, honest mistakes. |
| No own work; one FIFO queue; load peaks absent. | Everyone has their own work; client teams have deadline peaks. |
| BUSY reply almost free; askers saw the exact queue length. | BUSY costs queue time; askers estimate load from how slowly people reply. |
| Central look-ups free. | They take time. |
| Askers moved on at once (v1) or chased forever without withdrawing (v2). | One reminder by default (0–3 swept); askers withdraw questions they no longer need. |
| Liars only over-declared skills. | Also confidently wrong answerers and a colluding ring. |
| No middle ground between a central log and purely local memory. | New strategy: signed, coarse track records (§6). |
| Synthetic vectors only. | Text world plus a real embedding model (§7); the synthetic tier is kept for comparison. |
| Parameters I picked myself (patience, deadline, load-aware settings) were not tested. | Sensitivity sweeps (§10). 20 seeds for the baseline, 10 elsewhere. |

What v3 does **not** fix: no LLM agents (prepared in v1, not run); no real
zero-knowledge proofs (track records are simulated by their information
content); NANDA Town is not updated in this round.

## 2. Field study numbers (anonymised)

From a mixed-methods culture study (survey n = 81 plus interviews) at a
software company that builds tailored systems for several large clients. No
names are used anywhere in v3.

| fact | value | used for |
|---|---|---|
| headcount | about 40 → about 130 in about four years | growth path of the history (§3) |
| offices | 1 → 6 (confirmed; 5 offices kept as a sensitivity case) | offices opening during the history |
| structure | flat; everyone codes; leaders sit among colleagues; no managers assigning tasks | no managers; decision owners are team leads and core-area owners |
| "I have a clear picture of what teams in other offices are working on" | 2.19 / 5 (lowest item in the survey) | calibration target for cross-office awareness (§3) |
| teams duplicate work already solved elsewhere | 3.05 / 5 | similar work across client teams exists (§4) |
| leadership easily accessible | 4.58 / 5 | owners answer decision questions themselves |
| knowledge sits in single heads; decisions bottleneck on individuals; long tenure on one client system | interviews | rare knowledge; decision questions; client teams |
| work comes in peaks; people moved between projects without warning | interviews | deadline peaks; reassignments in the history |
| a customer-service team works under one client's service agreement | interviews | one service team attached to a client |

Mapping a 1–5 agreement score to a model quantity is a judgement call. The
one score used directly: 2.19 / 5 is read as "an average person knows what
about 30 % of people in other offices currently work on" ((2.19 − 1) / 4).
The history's cross-office mixing rate is tuned to hit that number at the
end of year 4, and the target is swept (15 %, 30 %, 50 %).

## 3. Four years of history (replaces seniors' ground truth)

A quarter-by-quarter generator, 16 quarters, run once per seed and shared by
all strategies.

* **Growth.** 40 people in one office at the start, growing geometrically to
  130. Offices 2–6 open in quarters 3, 6, 9, 11 and 13 *(assumed timing)*.
  A new hire joins head office with probability 0.25, otherwise one of the
  other open offices *(assumed)*.
* **Teams.** A core platform team, client teams, and a customer-service
  team (from year 2). Three client teams at the start, a new client about
  every three quarters, eight by the end *(assumed)*. A client team has a
  home office; most members sit there, some elsewhere.
* **Reassignment.** Each quarter 4 % of people move to another team,
  preferably in their office *(assumed; "moved between projects without
  warning")*. Attrition 2 % per quarter, replaced by hires *(assumed)*.
* **Learning the work.** Each quarter every person learns a few items in
  their team's current focus topics. Moving keeps old knowledge; only the
  topics of the last four quarters of current work are declared. So
  undeclared knowledge emerges from careers, and long-tenured people hold
  more of it.
* **Learning who knows what** (the only source of anyone's memory):
  * teammates learn each other's current focus topics every quarter;
  * office colleagues learn about each other with a probability that falls
    with office size (everyone knew everyone when the company had 40 people
    in one room);
  * cross-office colleagues learn about each other with a small probability,
    tuned to the 30 % awareness target;
  * every person asks a few questions per quarter, the way the company
    actually worked: their best guess if they have one, otherwise the most
    senior person they know, then follow referrals. Who answered, who did
    not, and feedback to referrers go into memory, exactly as in the
    measured period but without queues.
* **Roles.** Each client team has a lead (its longest-serving member); each
  core domain has an owner; the three longest-serving people are
  leadership. Roles are public.
* "Senior" means the 10 % longest-serving, as in v1, but they now have
  whatever picture their career gave them.

The central log of the `learned_central` strategy contains the history's
question outcomes too: if the company had kept such a log, it would have
recorded them.

## 4. Knowledge and questions

* **Knowledge.** 8 product domains × 6 topics. Each topic has 3 items per
  client system (client-specific) and 3 core items. Items with the same
  topic and index in different client systems are *analogues*: similar work
  done for another client.
* **Question types** *(mix assumed; decision share swept)*:

| type | share | what counts as answered | who can answer |
|---|---|---|---|
| content ("how does X work for client C?") | 35 % | the item | holders; an analogue holder from another client team helps with probability 0.5, is wrong with 0.1 |
| whom to ask ("who knows about X?") | 20 % | a correct name | anyone who knows a holder (names their best guess), or a holder |
| technical issue ("this fails, how do I fix it?") | 35 % | two pieces: the client item and the related core item | holders of either piece; analogue help as above; several people may be needed |
| decision ("can we change X for client C?") | 10 % | a decision | only the owner: the client team's lead, the core domain's owner, or leadership |

* Askers mostly ask about their own client (70 %), the core (20 %), or
  another client (10 %) *(assumed)*.
* Holders answer correctly with probability 0.98. Wrong answers count as
  answered but wrong; the asker finds out later with probability 0.5 and
  then counts it against the answerer.
* Service times (time units; 1 ≈ 10 minutes): content answer 1.0, technical
  help 2.0 per piece, decision 1.5, naming someone 0.3, referral 0.5, "don't
  know" 0.2, BUSY reply 0.1, reading a reminder 0.1.

## 5. The measured period (discrete-event, two working weeks)

* 480 time units (10 days × 48). Questions arrive at 1.5 per person per day
  *(assumed; swept 0.5×–2×)*.
* **Own work.** Everyone's inbox also receives their own work, in blocks of
  about an hour, filling 60 % of their time *(assumed; swept 40–80 %)*.
  Each client team has a two-day deadline peak during which own work fills
  85 % *(assumed; peaks on/off swept)*.
* **Inbox.** As in v2: an urgent lane (reminders and reminded questions)
  before a normal lane (asks and own work, first come first served). An ask
  whose projected wait exceeds `patience` (24 ≈ 4 hours) sinks unread.
* **Asking.** One candidate at a time; up to 8 contacts; deadline 96 (two
  days). Partial answers keep the question open for the missing piece.
* **Reminders.** An unopened message gets one reminder after `patience`
  (0–3 swept). An asker who gives up on someone, or no longer needs the
  answer, withdraws the question; withdrawn asks leave the inbox if not
  started.
* **BUSY (load-aware protocols).** A recipient whose projected wait exceeds
  12 (2 hours) replies "busy, try X"; the reply costs 0.1 of queue time.
* **Load estimates.** Askers estimate others' load from their past response
  times and BUSY replies; nobody sees an exact queue length.
* **Central look-ups** (search index, central log, track-record lookup)
  take 0.2 time units.
* **Feedback.** On success the asker tells the referrers who answered.

## 6. Strategies

| id | whom the asker contacts | memory |
|---|---|---|
| `phonebook` | own memory only; no referrals | local |
| `ask_senior` | own best guess if confident, otherwise the most senior person they know; seniors refer from memory, others pass the asker up (the field study's pattern) | local |
| `declared_search` | semantic search over declared skills and public roles | central index of self-descriptions |
| `declared_search_trust` | the same, matches sorted by answers given so far (NANDA Town `index.v1`) | index + reputation |
| `learned_central` | best match in one shared log of all outcomes (history included) | central log |
| `learned_local` | own memory + referrals | local |
| `learned_local_loadaware` | the same + load penalty, random among near-equals, BUSY | local |
| `hybrid_search_learned` | declared search for the first hop, then load-aware learned | local + index |
| `attested_search` *(new)* | declared search re-ranked by signed track records, load-aware, own memory | local + public coarse counts |
| `random_walk` | control | – |

**Signed track records.** When a question is answered correctly, the asker
signs a one-line receipt "answered a question in topic T". Each person
publishes, per topic, the number of *distinct* signers of such receipts.
Nobody publishes who asked what. Askers rank candidates by declared skill +
log(1 + receipts in matching topics) + their own memory, with the load
penalty. This is what a zero-knowledge track record would reveal ("I
answered 40 billing questions"), simulated without the cryptography.

## 7. Two embedding tiers

* **Synthetic** (as v1): vectors built from domain, topic, item index and
  client components, so analogues are close but not identical.
* **Text.** Every topic, item, role, self-description and question is a
  sentence from templates in a generic B2B software domain with anonymous
  clients ("Client A"…"Client H"). Sentences are embedded with a real
  model: `all-MiniLM-L6-v2` if available, otherwise spaCy `en_core_web_md`
  word vectors with SIF weighting (Arora et al., 2017). The model used is
  recorded in every result row.

The main results use the text tier; the synthetic tier is a check that the
ranking does not depend on it.

## 8. Adversaries (scenario)

10 % keyword stuffers (declare many topics, cannot answer); 5 % confident
wrong answerers (claim to know their declared topics, answer wrongly); a
ring of 5 colluders who sign receipts for each other and refer askers to
each other.

## 9. Metrics

Effectiveness: share answered **correctly** (main), answered wrongly,
partly answered; by question type; median and 90th-percentile time.
Load: share of inbox messages (asks + reminders + BUSY) on the busiest 5 %
and on seniors; share of decision questions (unavoidable load on owners);
work still queued at the end (backlog); asks never read; asks worked on
after withdrawal. Privacy: records held by any single party; what is
public. Robustness: success after the longest-serving people leave.
Calibration checks: cross-office awareness, undeclared share, tenure
spread, memory breadth of seniors vs. newcomers.

## 10. Scenarios

| name | what varies | seeds |
|---|---|---|
| `baseline` | – | 20 |
| `growth` | the company at year 1, 2, 3, 4 (and 200 people, extrapolated) | 10 |
| `reminders` | 0, 1, 2, 3 reminders | 10 |
| `decisions` | decision share 5 %, 10 %, 20 %, 30 % | 10 |
| `load` | question rate 0.5×, 1×, 1.5×, 2× | 10 |
| `own_work` | own work 40 %, 60 %, 80 %; peaks off | 10 |
| `turnover` | 3 longest-serving leave mid-period: no handover / handover to a successor | 10 |
| `adversaries` | §8 | 10 |
| `tiers` | synthetic vs. text embeddings | 10 |
| `sensitivity` | patience, deadline, BUSY threshold and cost, load-aware settings, analogue help, cross-office awareness target, 5 offices | 10 |

Sweeps run a subset of strategies to keep compute reasonable: `ask_senior`,
`declared_search`, `learned_central`, `learned_local`,
`learned_local_loadaware`, `hybrid_search_learned`, `attested_search`.

## 11. Expectations (stated before running)

1. With an earned rather than given picture, asking the senior answers fewer
   questions than in v1, but still concentrates load on seniors.
2. Decision questions put load on owners under every strategy; declared
   search (public roles) handles them best. This load cannot be routed away.
3. Help from similar work in other client teams raises the share answered,
   at the price of some wrong answers; strategies that can find it (search,
   learned) benefit most.
4. Load-aware learned routing and signed track records keep load spread;
   track records get close to the central log without one.
5. The ranking survives the move to real-language embeddings.
6. Reminders hurt strategies that let messages sink, less than in v2
   because askers withdraw.
7. Keyword stuffers hurt declared search; the colluding ring hurts track
   records less because only distinct signers count.

## 12. Amendments

Changes made after the design above was written. "Before results" means no
strategy had been run yet; "after the smoke run" means one seed of all
strategies had been looked at.

**Before results (calibration and building):**

* Six knowledge items per topic and system instead of three, and each
  person works on one of the team's topics at a time. With whole teams
  learning the same three items, every item had about as many holders as
  the team had members; now about a third of items have a single holder,
  matching "knowledge sits in single heads".
* Cross-office mixing tuned to 0.045 per pair and quarter, which gives
  about 30 % cross-office awareness at the end (target from §2).
* Clients are named with distinct words ("Client Alpha", "Client Beta", …):
  with one-letter names the word-vector model could not tell clients apart.
* Who owns a decision is a structured fact (an org chart), not something
  found by text similarity: people know owners they met in the history;
  search-based strategies read a public role directory. The word-vector
  model could not match "who decides X" to role descriptions reliably.
* Questions are only about items someone currently holds.

**After the smoke run (one seed, all strategies):**

* The 40 founding staff now joined over the five years before the history
  starts. Before, all 40 had the same tenure and "the most senior person I
  know" was a tie broken by id number, which sent everything to a few
  low-numbered people. *Bug.*
* An owner never replies BUSY to a decision only they can make. Before,
  load-aware askers moved on from a busy owner and could not get the
  decision at all. *Bug in the protocol.*
* Own work is a background lane outside a team's deadline peak: people
  finish the block they are on, read their messages, then return to their
  own work; during the peak, own work queues with messages. Before, own work
  queued like messages all the time, so almost everyone looked "busy"
  (projected wait above two hours) most of the day and load-aware askers got
  a BUSY reply from most contacts. *Model change.*
* Sensitivity adds `max_attempts = 12`, because BUSY replies use up the
  attempt budget and that budget was chosen, not measured.

**After the first baseline run (20 seeds), before any sweep was run:**

* A whom-to-ask answer now teaches the asker the person who was named (the
  answer *is* who knows). Before, the asker only credited the person who
  gave the name.
* A wrong answer found out later now counts against the answerer for the
  piece they actually answered. Before, it used the question's last need,
  which for a technical issue could be the other piece. *Bug.*
* Both changes made, the baseline and all sweeps were rerun from scratch;
  only the rerun is reported.

**Environment:** `all-MiniLM-L6-v2` could not be downloaded in the build
environment (huggingface.co blocked), so every text-tier result uses spaCy
`en_core_web_md` word vectors with SIF weighting. The model name is stored
in every result row.

**After the first paper (6–7 Nov 2026), on request:**

* The office count is confirmed at 6. The 5-office sensitivity case stays as
  a check; nothing in the model changed.
* A third embedding tier, `minilm`, runs all-MiniLM-L6-v2 from two local files
  (`models/all-MiniLM-L6-v2/model.onnx` and `tokenizer.json`) with
  onnxruntime: token vectors averaged over the attention mask, then unit
  length. The `text` tier is now always spaCy, so every earlier result stays
  reproducible; before, `text` silently preferred MiniLM when it could be
  loaded. The baseline was rerun with MiniLM (scenario `minilm`, 20 seeds,
  `results_minilm/`); nothing else was rerun.

---

# v4, Phase 1: agents instead of people, and priorities

Written on 8 Nov 2026 before the Phase 1 runs. Before writing it I ran a
one-company pilot (seed 0) of the agent profile at 30 and 120 questions per
agent per hour for three or four strategies, and of the five priority rules for
"ask the senior"; the expectations below were written after seeing that pilot,
like the smoke run in v3. Plan: the "WhoKnows for NANDA" doc, phase 1.

## 13.1 Question

Does the v3 ranking hold when the 130 people are replaced by their agents,
which answer in seconds, work on several messages at once, refuse when full
and pay for every message they read? And what happens when questions carry a
priority, set by the asker or by the one asked?

## 13.2 Three timing profiles (the company and its history stay as in v3)

| | people (v3) | agents | agents + approvals |
|---|---|---|---|
| time unit | 10 minutes | 1 second | 1 second |
| measured period | 2 working weeks | 1 hour | 1 hour |
| questions per person / agent | 1.5 per day | 30 per hour (swept 15-120) | 30 per hour |
| answer a content question | 10 min | 10 s | 10 s |
| one piece of a technical issue | 20 min | 20 s | 20 s |
| refer / don't know / name someone | 5 / 2 / 3 min | 3 / 2 / 3 s | same |
| parallel work | one thing at a time | 4 calls (queue served 4x faster) | same |
| full inbox | sinks unread after 4 h of work ahead | refused at once after 30 s of work ahead ("rate limited", no read) | same |
| reminders | 1 | none (agents move on) | none |
| give up | 8 contacts or 2 working days | 8 contacts or 10 minutes | 10 minutes; a working day when a human must approve |
| own work | 60 % of the time, 1-hour blocks | 60 % of capacity, 7.5-second blocks (the owner's tasks; amended, §13.8) | same |
| human approval | - | - | 20 % of decisions and 2 % of content and technical answers wait for the owner: 5 minutes of human attention each, one queue per human |
| reading cost | - | every message read counts (answer, refer, don't know, BUSY reply, reminder, triage); a refusal costs nothing (under the answerer rule an ask is read to rank it before the agent decides to refuse it or reply BUSY, so there it costs that triage read) | same |

Load-aware strategies keep the same logic: BUSY when more than 15 s of work is
ahead (2 h for people), and the same score penalty for a BUSY or a refusal as
people get for a BUSY. "Ask the senior" becomes "ask the oldest agent you
know": tenure is time in the company, now time in the network.

## 13.3 Priorities

Every question gets a hidden true importance: high for 60 % of decisions, 30 %
of technical issues, 15 % of content and 10 % of whom-to-ask questions; low for
10 %, 30 %, 40 % and 40 %; normal otherwise (assumed). The asker writes a
label: 30 % of askers label everything high ("inflaters"); the rest write the
true importance 70 % of the time and a random level otherwise. Five rules:

| rule | what the receiver does |
|---|---|
| none | first in, first out (v3) |
| asker | sorts by the asker's label |
| answerer | reads every ask to rank it (1 minute for people, 2 seconds for agents, counted as a read) and sees the true importance 90 % of the time |
| audit | sorts by the label, reads 20 % of asks to check, and treats labels from askers caught inflating more than half the time as normal |
| budget | sorts by the label, but each asker has high labels for only 25 % of the questions they expect to ask |

Priority sets the place in the normal lane and the work counted "ahead" when
deciding whether an ask sinks, is refused or gets a BUSY reply. Priorities only
matter when work queues up, so the agent priority runs use a busy network of
60 questions per agent per hour. All importance and label draws have their own
seeds, so every rule sees the same questions.

## 13.4 Measures added

Reads per question and the share of all reads done by the busiest 5 % (who
pays); refusals per question; triage reads and their share at the busiest 5 %;
approvals per question, approval wait (median, 90th percentile) and the share
of approvals at the busiest 5 % of humans; answered correctly and median wait
by true importance.

## 13.5 Scenarios

| scenario | varies | strategies | seeds |
|---|---|---|---|
| speed | people / agents / agents + approvals | all nine | 20 |
| agent_load | 15, 60, 120 questions per agent per hour | the seven sweep strategies | 10 |
| priority_people | the five rules, people | ask the senior, declared search, learned local, load-aware, track records | 10 |
| priority_agents | the five rules, agents at 60/h | the same five | 10 |
| inflation | asker / audit / budget with 0, 30, 60 % inflaters, agents at 60/h | ask the senior, learned local, load-aware | 10 |
| triage_cost | answerer rule with 0, 2, 8 s per triage read, agents at 60/h | the same three | 10 |

## 13.6 Expectations (stated before the runs)

1. Agents remove the sinking: asking the oldest agent answers far more than
   asking the senior did with people, but still sends a large share of messages
   and reading cost to a few agents and gets more answers wrong than learned
   routing. Learned local memory stays first.
2. As the question rate rises, refusals appear at the hubs first; asking the
   oldest agent loses most, load-aware routing least.
3. With approvals, the humans behind decision-owning agents become the slow
   part for every strategy, because decisions can only go to owners.
4. Asker-set priority speeds up high-importance questions where queues exist
   (asking the senior) and loses that effect as the share of inflaters rises;
   audit and budget recover part of it.
5. Answerer-set priority ranks best, but its reading cost lands on the busiest
   receivers and lowers the answered share wherever there are hubs; with free
   triage (0 s) it is the best rule.

## 13.7 Implementation notes

* With the default settings v4 reproduces v3 exactly (checked on seed 0 for
  three strategies; all v3 tests pass).
* Four parallel calls are modelled as one queue that handles messages four
  times faster, which keeps the queue bookkeeping exact; a single message is
  answered a bit faster than with real parallel calls, which matters little at
  second scale. Own work is not sped up (§13.8).
* A refused asker moves on to the next candidate (no retry after the
  Retry-After time); the refusal uses up one of the 8 contacts.

## 13.8 Amendment after the first Phase 1 run (9 Nov 2026)

A review of the code before publishing found one bug and one inconsistency:

* **Bug: agents had a quarter of the own work they were meant to have.** The
  four-times speed-up for parallel calls was also applied to the agent's own
  tasks, so own work took about 15 % of an agent's capacity instead of the
  60 % in §13.2 (measured in the regression test's setting: 19 % of the run
  before the fix; after it 58 % for agents and 55 % for people over the same
  span). Agents were therefore much less busy than designed. Fixed: own
  work is not sped up. To keep the same proportions as for people (one block
  of own work : BUSY threshold : refusal threshold = 1 : 2 : 4, people 1 h :
  2 h : 4 h), own-work blocks are 7.5 s instead of 30 s. Regression tests:
  `test_parallel_calls_speed_up_messages_but_not_own_work`,
  `test_agents_spend_the_designed_share_on_own_work`.
* **Run length.** With approvals, own work was scheduled for the whole
  working day that approvals may take. It is now scheduled only while asks
  still move between agents (horizon + deadline + patience); after that only
  human approvals and the answers they release are left. People runs are
  unchanged by both fixes: their speed is 1 and they have no approvals, so
  the code path is the same (also checked on sample runs).

All agent scenarios were rerun; people scenarios were kept. The first run is
kept in `results_first_run/` for comparison. The expectations in §13.6 were
written before both runs and are not changed.

## 14. v5: Phase 2, an open network of 1,000 agents (10 Nov 2026)

Phase 2 of the "WhoKnows for NANDA" plan: the same questions in an open
network of agents instead of one company, at 1,000 agents. Everything in this
section up to §14.7 was written before the Phase 2 runs (one smoke test, see
§14.7).

### 14.1 What changes and what stays

The company history (§3) is kept as the *process* and generalised in its
*settings*: a company is one setting, an open network another. The code path
for the v3 company is unchanged; a fingerprint of a v3 world (items, roles,
memories, receipts, central log) and of eight runs is bit-identical before and
after the change.

| | v3 company | open network (Phase 2) |
|---|---|---|
| who | 40 → 130 people over 16 quarters | 100 → 1,000 agents over 16 quarters |
| where they meet | 6 offices | 20 communities (one per 50 agents), opening as the network grows |
| who works together | 8 client teams by the end, a service team (see the note below) | 83 groups (one per 12 agents, at least three from the start) on 28 platform lanes (about three groups per lane), no service team |
| contacts outside one's office / community | 4.5 % per pair and quarter | 4.5 per agent and quarter (a larger network is not better connected) |
| leaving, moving | 2 %, 4 % per quarter | 4 %, 6 % per quarter (assumed) |
| authorities | leadership (3), a lead per client, an owner per core domain | a lead per platform lane (its longest-serving agent), a steward per domain of the shared lane (whoever holds most of it); no leadership, no company-wide decisions |
| topic space | 8 domains × 6 topics, 16 clients + core, 6 aspects (4,896 items) | 40 domains × 6 topics, 28 lanes + shared, 6 aspects (41,760 items, about 7,000 topic-lanes) |
| vectors | sentence embeddings of generated text | `TopicVectors` (§14.2) |

*Note on v3, found while writing Phase 2:* §3 describes a core platform team,
but the v3 code never creates one. Core-platform items are learned by the
client teams (a fifth of their items), and the owner of each core domain is
the member of the first client team who holds most of that domain's core
items. The v3 and v4 results are what this code produced, and the gate uses
the same rule. In the open network that rule would make the members of one
founding group the stewards of all 40 domains, so there the steward of a
domain is the agent that holds most of its shared-lane items, anywhere in the
network (`stewards="anyone"`). Whether a separate core team changes the v3
results is left as a check for later.

Asking in the history (best guess, else the oldest agent one knows, then
referrals), learning from outcomes, declared skills (the last year's work),
receipts and the central log are as in v3. Timing is the Phase 1 agent profile
(§13.2) with no company-wide decisions.

### 14.2 The topic space and its vectors

An item is (topic, lane, aspect); knowing the same topic and aspect in another
lane is an analogue, as in v3. Text for 42,000 items would be slow to embed and
does not scale to Phase 3, so vectors are built from random components
(`whoknows/topics.py`, 64 dimensions):

    item     = unit(0.29 domain + 0.83 topic + 0.38 lane + 0.27 aspect-of-topic)
               (+ 1.0 "shared-lane wording" for items of the shared lane)
    work     = unit(0.29 domain + 0.83 topic + 0.38 lane)
    question = unit(item + m · kind + m · wording),  m depends on the kind

The lane part is the same for every topic in a lane (in v3's text, the
client's name). Lane, aspect and shared-lane weights vary around their means
(log-normal, spread 0.45), and so does the size of the kind-and-wording part,
which is larger for whom-to-ask and technical questions than for content
questions. All weights were fitted to similarities measured on v3's text
vectors, mean and spread of each class (§14.8):

| similarity of a question to ... | v3 text | topic vectors |
|---|---|---|
| its own item | 0.95 ± 0.02 | 0.95 ± 0.02 |
| an analogue (same topic and aspect, other lane) | 0.81 ± 0.07 | 0.80 ± 0.09 |
| another aspect, same topic and lane | 0.88 ± 0.05 | 0.87 ± 0.06 |
| another topic of the same domain, same lane | 0.22 ± 0.15 | 0.21 ± 0.13 |
| a topic of another domain, same lane | 0.12 ± 0.13 | 0.13 ± 0.14 |
| a random item | 0.02 ± 0.18 | 0.03 ± 0.17 |
| the work it is about (content / whom / technical) | 0.91 / 0.75 / 0.82 | 0.91 / 0.75 / 0.81 |
| shared lane: the work it is about | 0.64 ± 0.20 | 0.67 ± 0.12 |

Popularity of topics is Zipf (a = 1) over the 240 topics, as in v3.

### 14.3 The gate

Phase 2 may only be used if the open-network code reproduces v3 when given the
company's settings. Two checks:

1. Same settings, same vectors: the generalised code reproduces v3 exactly
   (the fingerprint above; also the 52 tests).
2. Same settings, the open network's vectors (`company_in_network_terms`): the
   world statistics match v3 (awareness, undeclared share, holders per item),
   and the nine strategies give the same results within the noise. Pass if
   (a) every strategy is within 6 points of v3 under people timing and within
   6 points of Phase 1 under agent timing, (b) the order of the nine
   strategies has a rank correlation of at least 0.8 with v3's, and (c) asking
   the senior still sends more than half of all messages to 5 % of people.

### 14.4 What is measured in addition

* Load on the busiest 1 % (at 1,000 agents the busiest 5 % are 50 agents).
* Newcomers, agents that joined in the last half year of the history: the
  share of their own questions answered correctly, against everyone else's;
  how many others know them; and a *found ratio*: correct answers they gave per
  item they hold, divided by the same ratio for everyone else (1 = found as
  often as their knowledge justifies).

### 14.5 Scenarios

| scenario | what varies | strategies | seeds |
|---|---|---|---|
| gate | the v3 company with network vectors; people and agent timing | all nine | 10 |
| net_size | the open network at 130 and 300 agents, agents at 30/h | all nine | 5 |
| net_speed | 1,000 agents at 30/h; with human approvals | all nine; five with approvals | 5 |
| net_priority | 1,000 agents at 60/h; none, asker, answerer (2 s), audit, budget | oldest agent, learned local, track records | 4 |
| net_inflation | 60 % of askers inflate; asker labels vs audits | the same three | 4 |

Fewer seeds than Phase 1 because one run at 1,000 agents takes one to four
minutes on the two available cores.

### 14.6 Not in Phase 2

Agents joining and leaving *during* a run (experiment 6), multi-hop referral
at 100,000 agents, bounded memory and a sharded index (Phase 3); dishonest
agents (Phase 4). Agents join and leave in the history, so the network a run
starts from already has newcomers and missing veterans.

### 14.7 Expectations (written before the runs)

Before writing these, one smoke test was run to measure run times: one seed of
the 1,000-agent network, five strategies, agents at 30/h. It showed asking the
oldest agent at 45 % with 80 % of messages at the busiest 5 %, learned local
and declared search both at 66 %, signed track records at 74 %. Expectations 2
and 3 are therefore partly informed by it; the others are not.

1. **Gate.** Passes both checks of §14.3.
2. **Scale.** From 130 to 1,000 agents, asking the oldest agent loses the
   most (at least 15 points) and its busiest 1 % receive more than a quarter
   of all messages. Learned local memory loses more than declared search,
   because one agent's memory covers a smaller part of a larger network; the
   gap between them closes. Signed track records, which combine search with
   network-wide evidence, come first.
3. **Newcomers.** Under learned routing and asking the oldest agent, newcomers
   are found less than their knowledge justifies (found ratio below 0.8);
   under declared search, whose AgentFacts are fresh, close to 1 or above. As
   askers, newcomers get at least 5 points fewer answers than others under
   learned local memory, and about the same under declared search.
4. **Priority.** As in Phase 1: asker labels halve the wait for urgent
   questions at the oldest agents without extra reading; ranking by the
   receiver costs answers there, more than in the company (more than 14
   points), because the hubs are bigger; under learned routing and track
   records the rule matters little. With 60 % inflaters, audits keep urgent
   questions faster than plain asker labels.
5. **Approvals.** The busiest 5 % of humans still give at least 40 % of all
   approvals.

### 14.8 Amendment: the gate failed first, and what was changed (10 Nov 2026)

The first gate run (10 seeds) used simpler vectors: 128 dimensions, every
lane part specific to its topic, and the same small kind-and-wording part for
every kind of question, fitted only to the *mean* similarities of content
questions. It failed: the largest difference was 18.6 points (asking the
senior 72 % instead of 54 %, central log 85 % instead of 76 %) and the rank
correlation 0.77. Looking for the cause (on seeds 0–3 and one diagnostic seed):

* in v3's text, whom-to-ask and technical questions are much further from
  the work they are about (0.75 and 0.82) than content questions (0.91), and
  shared-lane (core) questions are far from core work (0.64); the simple
  vectors had 0.91 for all of them, so askers found the right person directly
  more often and fewer questions sank at the seniors (technical questions
  under asking the senior: 49 % answered instead of 38 %);
* the client's name is a part shared by all topics of a client (0.12
  similarity across domains), which the simple vectors lacked;
* the spreads of the similarities were too narrow.

The vectors were refitted to all the similarity classes in the table of §14.2
(means and spreads), not to any result. Cached worlds now carry a version of
the vectors, because a world built with older vectors had been reused once
during the fitting (that check was repeated with fresh worlds). The gate was
then run again with the same criteria on all 10 seeds; seeds 0–3 had been
used to check the fit, seeds 4–9 had not. The first run's numbers are in
`results/gate_first_attempt.md`.

Two more changes before any open-network result was used: (1) at 130 agents
the network started with a single group, so nobody could be moved; it now
starts with at least three groups, as the company did, and a move is skipped
when there is no other group. (2) Stewards of the shared lane come from the
whole network (see the note in §14.1). The open-network runs made before these
changes, and before the refit of §14.8, were stopped and discarded.

## 15. Phase 3 plan: towards 100,000 agents (written 10 Nov 2026, not built yet)

Phase 2 showed that at 1,000 agents an agent's own memory covers too little
of the network and that search plus network-wide evidence scales best. Phase
3 asks whether that holds at 10,000 and 100,000 agents, where no agent can
know more than a sliver and every central component becomes a hub.

What has to change in the code before it can run at that size (measured at
1,000 agents: a world takes 40 s, a run 1–6 minutes on one core):

| part | now | needed |
|---|---|---|
| contacts in the history | a random number for every pair of agents (n² per quarter) | draw each agent's contacts directly (expected numbers unchanged) |
| memory | one score per known agent, arrays sized to the whole network | at most K agents remembered (K = 200), least recently seen forgotten first; scores over the remembered prototypes only |
| declared search | exact cosine over every declared row | the same rows in an approximate index (HNSW), and as variant a sharded index (one shard per domain) with its own load |
| run length | one hour of questions | ten minutes at 100,000 agents (about 500,000 questions) |
| referrals | up to 8 contacts | the same, and hops per question measured |
| measures | busiest 5 % and 1 % | also the busiest 0.1 % and the load on each index shard |

Experiments: 3 (size: 1,000 → 10,000 → 100,000), 4 (hot topics: popularity
skew a = 0.5, 1, 1.5), 6 (churn during the run: agents leaving and joining per
hour), 7 (index: one, sharded, none). Gate: at 1,000 agents the scalable code
gives the Phase 2 results within the noise, and one 100,000-agent run fits in a
few hours on two cores. The expectations will be written after the scalable
code passes that gate and before the large runs.
