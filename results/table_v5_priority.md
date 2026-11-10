**Who sets the priority: 1,000 agents at 60/h (4 seeds)** (mean ± 95 % interval over seeds)

| strategy | variant | correct | high: correct | high: typical wait (s) | low: typical wait (s) | reads per question | refusals per question | triage reads at busiest 5 % |
|---|---|---|---|---|---|---|---|---|
| Learned, local | priority=none | 58 % ± 3 | 59 % ± 4 | 23.5 ± 2.1 | 21.6 ± 0.7 | 3.67 ± 0.13 | 0.77 ± 0.10 | 0 % ± 0 |
| Learned, local | priority=asker | 59 % ± 3 | 66 % ± 4 | 16.8 ± 0.7 | 18.2 ± 0.2 | 3.66 ± 0.14 | 0.59 ± 0.06 | 0 % ± 0 |
| Learned, local | priority=answerer | 53 % ± 3 | 66 % ± 4 | 20.0 ± 1.2 | 24.8 ± 2.8 | 8.43 ± 0.29 | 0.96 ± 0.10 | 38 % ± 2 |
| Learned, local | priority=audit | 58 % ± 4 | 65 % ± 4 | 17.4 ± 0.7 | 19.4 ± 1.0 | 4.57 ± 0.17 | 0.67 ± 0.09 | 42 % ± 2 |
| Learned, local | priority=budget | 58 % ± 3 | 64 % ± 4 | 16.8 ± 0.5 | 19.6 ± 0.9 | 3.67 ± 0.12 | 0.67 ± 0.10 | 0 % ± 0 |
| Signed track records | priority=none | 71 % ± 2 | 74 % ± 2 | 14.9 ± 0.3 | 14.3 ± 0.4 | 3.44 ± 0.10 | 0.00 ± 0.00 | 0 % ± 0 |
| Signed track records | priority=asker | 74 % ± 2 | 82 % ± 2 | 13.2 ± 0.3 | 14.2 ± 0.4 | 3.24 ± 0.10 | 0.00 ± 0.00 | 0 % ± 0 |
| Signed track records | priority=answerer | 69 % ± 2 | 82 % ± 2 | 14.3 ± 0.3 | 17.0 ± 0.7 | 7.24 ± 0.24 | 0.00 ± 0.00 | 35 % ± 2 |
| Signed track records | priority=audit | 73 % ± 2 | 82 % ± 2 | 13.4 ± 0.3 | 14.6 ± 0.5 | 3.99 ± 0.12 | 0.00 ± 0.00 | 36 % ± 2 |
| Signed track records | priority=budget | 73 % ± 2 | 80 % ± 2 | 13.2 ± 0.2 | 14.5 ± 0.4 | 3.34 ± 0.10 | 0.00 ± 0.00 | 0 % ± 0 |
| Ask the senior / oldest agent | priority=none | 27 % ± 1 | 32 % ± 2 | 33.2 ± 0.2 | 34.2 ± 1.0 | 2.05 ± 0.10 | 4.56 ± 0.08 | 0 % ± 0 |
| Ask the senior / oldest agent | priority=asker | 30 % ± 2 | 45 % ± 3 | 35.2 ± 0.7 | 33.2 ± 0.4 | 2.22 ± 0.14 | 4.21 ± 0.13 | 0 % ± 0 |
| Ask the senior / oldest agent | priority=answerer | 11 % ± 1 | 16 % ± 1 | 12.2 ± 1.0 | 11.5 ± 0.7 | 8.24 ± 0.09 | 6.38 ± 0.08 | 96 % ± 1 |
| Ask the senior / oldest agent | priority=audit | 15 % ± 1 | 20 % ± 1 | 11.7 ± 0.5 | 11.7 ± 1.2 | 2.68 ± 0.03 | 5.97 ± 0.08 | 95 % ± 1 |
| Ask the senior / oldest agent | priority=budget | 26 % ± 2 | 41 % ± 2 | 34.2 ± 0.5 | 25.4 ± 2.3 | 1.99 ± 0.11 | 4.61 ± 0.08 | 0 % ± 0 |
