**60 % of askers inflate: 1,000 agents at 60/h (4 seeds)** (mean ± 95 % interval over seeds)

| strategy | variant | correct | high: correct | high: typical wait (s) | low: typical wait (s) | reads per question | refusals per question | triage reads at busiest 5 % |
|---|---|---|---|---|---|---|---|---|
| Learned, local | priority=asker,inflaters=0.6 | 60 % ± 3 | 65 % ± 5 | 18.7 ± 1.4 | 18.2 ± 0.8 | 3.68 ± 0.16 | 0.49 ± 0.08 | 0 % ± 0 |
| Learned, local | priority=audit,inflaters=0.6 | 59 % ± 4 | 65 % ± 4 | 18.7 ± 1.0 | 19.0 ± 0.9 | 4.57 ± 0.17 | 0.61 ± 0.10 | 43 % ± 3 |
| Signed track records | priority=asker,inflaters=0.6 | 75 % ± 2 | 82 % ± 2 | 13.7 ± 0.2 | 14.0 ± 0.4 | 3.14 ± 0.10 | 0.00 ± 0.00 | 0 % ± 0 |
| Signed track records | priority=audit,inflaters=0.6 | 74 % ± 2 | 81 % ± 2 | 13.6 ± 0.5 | 14.3 ± 0.3 | 3.89 ± 0.14 | 0.00 ± 0.00 | 36 % ± 2 |
| Ask the senior / oldest agent | priority=asker,inflaters=0.6 | 32 % ± 2 | 42 % ± 3 | 33.5 ± 0.5 | 34.5 ± 1.1 | 2.30 ± 0.11 | 4.05 ± 0.05 | 0 % ± 0 |
| Ask the senior / oldest agent | priority=audit,inflaters=0.6 | 15 % ± 1 | 19 % ± 1 | 11.9 ± 0.4 | 11.8 ± 1.1 | 2.69 ± 0.03 | 5.97 ± 0.08 | 95 % ± 1 |
