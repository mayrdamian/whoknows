**Who sets the priority: agents (10 seeds)** (mean ± 95 % interval over seeds)

| strategy | variant | correct | high: correct | low: correct | high: typical wait (s) | low: typical wait (s) | reads per question | triage reads at busiest 5 % |
|---|---|---|---|---|---|---|---|---|
| Learned, local | priority=none | 80 % ± 1 | 82 % ± 0 | 79 % ± 1 | 17.1 ± 0.4 | 15.4 ± 0.5 | 2.52 ± 0.04 | 0 % ± 0 |
| Learned, local | priority=asker | 82 % ± 1 | 87 % ± 1 | 79 % ± 1 | 14.3 ± 0.2 | 14.8 ± 0.3 | 2.49 ± 0.04 | 0 % ± 0 |
| Learned, local | priority=answerer | 79 % ± 1 | 88 % ± 1 | 75 % ± 1 | 15.6 ± 0.2 | 19.2 ± 1.0 | 5.49 ± 0.08 | 20 % ± 1 |
| Learned, local | priority=audit | 81 % ± 1 | 87 % ± 0 | 78 % ± 1 | 14.5 ± 0.2 | 15.5 ± 0.5 | 3.07 ± 0.05 | 21 % ± 1 |
| Learned, local | priority=budget | 80 % ± 1 | 85 % ± 1 | 78 % ± 1 | 14.5 ± 0.3 | 15.6 ± 0.4 | 2.51 ± 0.04 | 0 % ± 0 |
| Signed track records | priority=none | 79 % ± 1 | 81 % ± 1 | 78 % ± 2 | 14.2 ± 0.4 | 12.4 ± 0.3 | 2.89 ± 0.07 | 0 % ± 0 |
| Signed track records | priority=asker | 81 % ± 1 | 87 % ± 1 | 79 % ± 1 | 13.1 ± 0.3 | 12.6 ± 0.3 | 2.69 ± 0.05 | 0 % ± 0 |
| Signed track records | priority=answerer | 78 % ± 1 | 87 % ± 1 | 75 % ± 2 | 14.0 ± 0.3 | 15.1 ± 0.5 | 5.89 ± 0.13 | 20 % ± 1 |
| Signed track records | priority=audit | 80 % ± 1 | 87 % ± 1 | 78 % ± 2 | 13.2 ± 0.4 | 13.1 ± 0.4 | 3.31 ± 0.07 | 21 % ± 1 |
| Signed track records | priority=budget | 80 % ± 1 | 85 % ± 1 | 78 % ± 1 | 13.1 ± 0.3 | 12.7 ± 0.3 | 2.80 ± 0.05 | 0 % ± 0 |
| Learned, local, load-aware | priority=none | 76 % ± 1 | 78 % ± 1 | 75 % ± 1 | 13.8 ± 0.2 | 12.0 ± 0.4 | 3.23 ± 0.04 | 0 % ± 0 |
| Learned, local, load-aware | priority=asker | 78 % ± 1 | 84 % ± 1 | 76 % ± 1 | 12.8 ± 0.2 | 12.2 ± 0.3 | 3.06 ± 0.04 | 0 % ± 0 |
| Learned, local, load-aware | priority=answerer | 75 % ± 1 | 84 % ± 1 | 72 % ± 1 | 13.8 ± 0.4 | 14.3 ± 0.4 | 6.56 ± 0.10 | 17 % ± 1 |
| Learned, local, load-aware | priority=audit | 77 % ± 1 | 84 % ± 0 | 75 % ± 1 | 13.1 ± 0.3 | 12.6 ± 0.3 | 3.72 ± 0.05 | 18 % ± 1 |
| Learned, local, load-aware | priority=budget | 77 % ± 0 | 82 % ± 1 | 75 % ± 1 | 12.9 ± 0.3 | 12.3 ± 0.3 | 3.15 ± 0.04 | 0 % ± 0 |
| Declared search | priority=none | 63 % ± 3 | 66 % ± 3 | 61 % ± 3 | 16.3 ± 1.6 | 17.3 ± 1.1 | 3.60 ± 0.19 | 0 % ± 0 |
| Declared search | priority=asker | 64 % ± 3 | 69 % ± 3 | 61 % ± 3 | 13.7 ± 1.0 | 17.1 ± 1.0 | 3.66 ± 0.20 | 0 % ± 0 |
| Declared search | priority=answerer | 62 % ± 3 | 70 % ± 3 | 57 % ± 3 | 14.9 ± 1.0 | 22.8 ± 1.8 | 7.74 ± 0.38 | 19 % ± 3 |
| Declared search | priority=audit | 63 % ± 3 | 69 % ± 3 | 60 % ± 3 | 13.9 ± 1.0 | 18.1 ± 1.2 | 4.46 ± 0.24 | 20 % ± 3 |
| Declared search | priority=budget | 63 % ± 3 | 68 % ± 3 | 60 % ± 3 | 14.1 ± 1.0 | 17.5 ± 1.1 | 3.62 ± 0.19 | 0 % ± 0 |
| Ask the senior / oldest agent | priority=none | 69 % ± 2 | 73 % ± 2 | 67 % ± 2 | 30.7 ± 1.2 | 28.6 ± 1.2 | 2.77 ± 0.06 | 0 % ± 0 |
| Ask the senior / oldest agent | priority=asker | 70 % ± 1 | 78 % ± 1 | 66 % ± 2 | 15.5 ± 1.0 | 20.7 ± 0.8 | 2.77 ± 0.06 | 0 % ± 0 |
| Ask the senior / oldest agent | priority=answerer | 55 % ± 3 | 77 % ± 1 | 43 % ± 4 | 44.4 ± 6.9 | 23.7 ± 2.5 | 7.25 ± 0.15 | 63 % ± 1 |
| Ask the senior / oldest agent | priority=audit | 69 % ± 1 | 78 % ± 1 | 64 % ± 2 | 15.9 ± 0.6 | 23.9 ± 1.4 | 3.50 ± 0.07 | 51 % ± 1 |
| Ask the senior / oldest agent | priority=budget | 69 % ± 2 | 76 % ± 1 | 65 % ± 2 | 16.4 ± 1.0 | 23.9 ± 1.0 | 2.77 ± 0.06 | 0 % ± 0 |
