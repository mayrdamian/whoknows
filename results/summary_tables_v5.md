### Size

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

### Newcomers (1,000 agents)

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

### Approvals (1,000 agents)

| strategy | approvals given by the busiest 5 % of humans | typical approval wait | slowest 10 % wait |
|---|---|---|---|
| Signed track records | 67 % | 8.4 min | 40 min |
| Declared search | 68 % | 8.4 min | 40 min |
| Learned, local | 71 % | 7.1 min | 33 min |
| Learned, local, load-aware | 71 % | 7.7 min | 33 min |
| Ask the senior / oldest agent | 80 % | 8.7 min | 32 min |

### Priority (1,000 agents, 60/h)

| rule | oldest agent: answered | urgent: typical wait | reads | learned local: answered | urgent wait | track records: answered | urgent wait | reads |
|---|---|---|---|---|---|---|---|---|
| none | 27 % | 33 s | 2.0 | 58 % | 24 s | 71 % | 15 s | 3.4 |
| asker | 30 % | 35 s | 2.2 | 59 % | 17 s | 74 % | 13 s | 3.2 |
| budget | 26 % | 34 s | 2.0 | 58 % | 17 s | 73 % | 13 s | 3.3 |
| audit | 15 % | 12 s | 2.7 | 58 % | 17 s | 73 % | 13 s | 4.0 |
| answerer | 11 % | 12 s | 8.2 | 53 % | 20 s | 69 % | 14 s | 7.2 |
