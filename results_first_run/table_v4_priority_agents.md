**Who sets the priority: agents (10 seeds)** (mean ± 95 % interval over seeds)

| strategy | variant | correct | high: correct | low: correct | high: typical wait (s) | low: typical wait (s) | reads per question | triage reads at busiest 5 % |
|---|---|---|---|---|---|---|---|---|
| Learned, local | priority=none | 85 % ± 1 | 88 % ± 1 | 84 % ± 1 | 9.6 ± 0.6 | 7.2 ± 0.4 | 2.43 ± 0.06 | 0 % ± 0 |
| Learned, local | priority=asker | 85 % ± 1 | 88 % ± 1 | 84 % ± 1 | 8.6 ± 0.4 | 6.9 ± 0.4 | 2.44 ± 0.05 | 0 % ± 0 |
| Learned, local | priority=answerer | 85 % ± 1 | 88 % ± 1 | 83 % ± 1 | 10.1 ± 0.4 | 9.8 ± 0.8 | 4.91 ± 0.11 | 21 % ± 1 |
| Learned, local | priority=audit | 85 % ± 1 | 88 % ± 1 | 84 % ± 1 | 8.7 ± 0.4 | 7.4 ± 0.5 | 2.92 ± 0.07 | 22 % ± 2 |
| Learned, local | priority=budget | 85 % ± 1 | 88 % ± 1 | 84 % ± 1 | 8.5 ± 0.5 | 7.1 ± 0.4 | 2.43 ± 0.05 | 0 % ± 0 |
| Signed track records | priority=none | 87 % ± 1 | 90 % ± 1 | 86 % ± 2 | 9.3 ± 0.5 | 7.4 ± 0.4 | 2.20 ± 0.07 | 0 % ± 0 |
| Signed track records | priority=asker | 87 % ± 1 | 90 % ± 1 | 86 % ± 1 | 8.4 ± 0.4 | 7.2 ± 0.4 | 2.18 ± 0.07 | 0 % ± 0 |
| Signed track records | priority=answerer | 87 % ± 1 | 90 % ± 1 | 85 % ± 2 | 9.6 ± 0.5 | 9.5 ± 0.7 | 4.46 ± 0.14 | 23 % ± 1 |
| Signed track records | priority=audit | 87 % ± 1 | 90 % ± 1 | 86 % ± 1 | 8.7 ± 0.4 | 7.7 ± 0.4 | 2.63 ± 0.09 | 24 % ± 1 |
| Signed track records | priority=budget | 87 % ± 1 | 90 % ± 1 | 86 % ± 2 | 8.5 ± 0.4 | 7.3 ± 0.4 | 2.19 ± 0.07 | 0 % ± 0 |
| Learned, local, load-aware | priority=none | 84 % ± 1 | 87 % ± 1 | 83 % ± 1 | 8.3 ± 0.4 | 6.4 ± 0.2 | 2.61 ± 0.05 | 0 % ± 0 |
| Learned, local, load-aware | priority=asker | 84 % ± 1 | 87 % ± 1 | 82 % ± 1 | 7.8 ± 0.3 | 6.3 ± 0.2 | 2.60 ± 0.06 | 0 % ± 0 |
| Learned, local, load-aware | priority=answerer | 84 % ± 1 | 87 % ± 1 | 82 % ± 1 | 9.1 ± 0.3 | 8.5 ± 0.4 | 5.27 ± 0.10 | 19 % ± 1 |
| Learned, local, load-aware | priority=audit | 84 % ± 1 | 87 % ± 1 | 83 % ± 1 | 8.2 ± 0.2 | 6.8 ± 0.3 | 3.11 ± 0.06 | 19 % ± 1 |
| Learned, local, load-aware | priority=budget | 84 % ± 1 | 87 % ± 1 | 82 % ± 1 | 7.8 ± 0.2 | 6.4 ± 0.3 | 2.61 ± 0.06 | 0 % ± 0 |
| Declared search | priority=none | 66 % ± 3 | 70 % ± 3 | 65 % ± 3 | 8.0 ± 1.2 | 8.3 ± 1.0 | 3.80 ± 0.22 | 0 % ± 0 |
| Declared search | priority=asker | 66 % ± 3 | 70 % ± 3 | 65 % ± 3 | 7.2 ± 0.9 | 8.1 ± 0.8 | 3.80 ± 0.22 | 0 % ± 0 |
| Declared search | priority=answerer | 66 % ± 3 | 70 % ± 3 | 64 % ± 3 | 8.5 ± 0.9 | 11.6 ± 1.4 | 7.63 ± 0.44 | 20 % ± 3 |
| Declared search | priority=audit | 66 % ± 3 | 70 % ± 3 | 65 % ± 3 | 7.5 ± 0.8 | 8.7 ± 0.9 | 4.57 ± 0.26 | 20 % ± 3 |
| Declared search | priority=budget | 66 % ± 3 | 70 % ± 3 | 65 % ± 3 | 7.3 ± 0.9 | 8.1 ± 0.9 | 3.80 ± 0.22 | 0 % ± 0 |
| Ask the senior / oldest agent | priority=none | 75 % ± 1 | 80 % ± 1 | 73 % ± 1 | 23.9 ± 3.6 | 20.7 ± 3.3 | 2.76 ± 0.08 | 0 % ± 0 |
| Ask the senior / oldest agent | priority=asker | 74 % ± 1 | 80 % ± 1 | 72 % ± 1 | 10.7 ± 1.0 | 13.1 ± 1.4 | 2.78 ± 0.08 | 0 % ± 0 |
| Ask the senior / oldest agent | priority=answerer | 66 % ± 2 | 79 % ± 1 | 58 % ± 4 | 30.1 ± 6.2 | 22.4 ± 3.8 | 6.79 ± 0.20 | 60 % ± 2 |
| Ask the senior / oldest agent | priority=audit | 74 % ± 1 | 80 % ± 1 | 71 % ± 1 | 11.0 ± 0.6 | 15.6 ± 2.0 | 3.40 ± 0.09 | 50 % ± 1 |
| Ask the senior / oldest agent | priority=budget | 75 % ± 1 | 80 % ± 1 | 72 % ± 1 | 11.0 ± 0.5 | 15.4 ± 1.9 | 2.78 ± 0.07 | 0 % ± 0 |
