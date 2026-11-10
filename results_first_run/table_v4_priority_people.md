**Who sets the priority: people (10 seeds)** (mean ± 95 % interval over seeds)

| strategy | variant | correct | high: correct | low: correct | high: typical wait (h) | low: typical wait (h) | reads per question | triage reads at busiest 5 % |
|---|---|---|---|---|---|---|---|---|
| Learned, local | priority=none | 84 % ± 1 | 87 % ± 1 | 83 % ± 1 | 2.2 ± 0.1 | 2.0 ± 0.2 | 2.96 ± 0.08 | 0 % ± 0 |
| Learned, local | priority=asker | 84 % ± 1 | 88 % ± 1 | 83 % ± 2 | 1.6 ± 0.1 | 1.8 ± 0.1 | 2.91 ± 0.07 | 0 % ± 0 |
| Learned, local | priority=answerer | 84 % ± 1 | 87 % ± 1 | 82 % ± 2 | 1.6 ± 0.1 | 2.4 ± 0.2 | 5.70 ± 0.13 | 20 % ± 1 |
| Learned, local | priority=audit | 84 % ± 1 | 88 % ± 1 | 83 % ± 2 | 1.6 ± 0.1 | 2.0 ± 0.2 | 3.48 ± 0.08 | 21 % ± 1 |
| Learned, local | priority=budget | 84 % ± 1 | 87 % ± 2 | 83 % ± 1 | 1.8 ± 0.1 | 2.0 ± 0.1 | 2.97 ± 0.07 | 0 % ± 0 |
| Signed track records | priority=none | 79 % ± 1 | 82 % ± 1 | 79 % ± 1 | 1.4 ± 0.1 | 1.2 ± 0.0 | 2.99 ± 0.07 | 0 % ± 0 |
| Signed track records | priority=asker | 81 % ± 1 | 85 % ± 1 | 80 % ± 1 | 1.2 ± 0.1 | 1.2 ± 0.1 | 2.86 ± 0.07 | 0 % ± 0 |
| Signed track records | priority=answerer | 80 % ± 1 | 87 % ± 1 | 78 % ± 2 | 1.2 ± 0.1 | 1.4 ± 0.1 | 5.90 ± 0.14 | 22 % ± 2 |
| Signed track records | priority=audit | 81 % ± 1 | 85 % ± 2 | 79 % ± 1 | 1.2 ± 0.1 | 1.2 ± 0.1 | 3.45 ± 0.10 | 22 % ± 1 |
| Signed track records | priority=budget | 80 % ± 1 | 84 % ± 2 | 79 % ± 1 | 1.2 ± 0.1 | 1.2 ± 0.1 | 2.95 ± 0.06 | 0 % ± 0 |
| Learned, local, load-aware | priority=none | 77 % ± 1 | 79 % ± 2 | 76 % ± 2 | 1.4 ± 0.1 | 1.2 ± 0.0 | 3.38 ± 0.08 | 0 % ± 0 |
| Learned, local, load-aware | priority=asker | 78 % ± 1 | 83 % ± 1 | 77 % ± 1 | 1.2 ± 0.0 | 1.2 ± 0.1 | 3.28 ± 0.07 | 0 % ± 0 |
| Learned, local, load-aware | priority=answerer | 78 % ± 1 | 84 % ± 2 | 76 % ± 1 | 1.3 ± 0.1 | 1.4 ± 0.1 | 6.70 ± 0.15 | 17 % ± 1 |
| Learned, local, load-aware | priority=audit | 78 % ± 1 | 83 % ± 1 | 77 % ± 1 | 1.2 ± 0.1 | 1.2 ± 0.1 | 3.95 ± 0.08 | 18 % ± 1 |
| Learned, local, load-aware | priority=budget | 78 % ± 1 | 82 % ± 2 | 77 % ± 1 | 1.3 ± 0.0 | 1.2 ± 0.0 | 3.35 ± 0.08 | 0 % ± 0 |
| Declared search | priority=none | 66 % ± 4 | 70 % ± 4 | 64 % ± 3 | 1.7 ± 0.2 | 1.9 ± 0.3 | 4.07 ± 0.24 | 0 % ± 0 |
| Declared search | priority=asker | 66 % ± 4 | 70 % ± 4 | 64 % ± 3 | 1.3 ± 0.1 | 1.8 ± 0.2 | 4.02 ± 0.24 | 0 % ± 0 |
| Declared search | priority=answerer | 66 % ± 3 | 70 % ± 4 | 64 % ± 3 | 1.4 ± 0.1 | 2.5 ± 0.4 | 7.89 ± 0.47 | 20 % ± 3 |
| Declared search | priority=audit | 66 % ± 4 | 70 % ± 4 | 64 % ± 3 | 1.3 ± 0.1 | 1.9 ± 0.2 | 4.80 ± 0.28 | 21 % ± 3 |
| Declared search | priority=budget | 66 % ± 4 | 70 % ± 3 | 64 % ± 3 | 1.4 ± 0.1 | 2.0 ± 0.3 | 4.08 ± 0.23 | 0 % ± 0 |
| Ask the senior / oldest agent | priority=none | 55 % ± 3 | 58 % ± 3 | 54 % ± 3 | 4.8 ± 0.7 | 4.5 ± 0.8 | 3.36 ± 0.08 | 0 % ± 0 |
| Ask the senior / oldest agent | priority=asker | 56 % ± 3 | 60 % ± 3 | 54 % ± 3 | 4.1 ± 0.8 | 4.9 ± 0.8 | 3.43 ± 0.09 | 0 % ± 0 |
| Ask the senior / oldest agent | priority=answerer | 44 % ± 3 | 48 % ± 3 | 43 % ± 3 | 2.2 ± 0.3 | 3.8 ± 0.5 | 5.43 ± 0.14 | 61 % ± 2 |
| Ask the senior / oldest agent | priority=audit | 53 % ± 4 | 57 % ± 4 | 51 % ± 3 | 3.5 ± 1.0 | 4.4 ± 0.6 | 3.85 ± 0.11 | 57 % ± 2 |
| Ask the senior / oldest agent | priority=budget | 56 % ± 3 | 60 % ± 3 | 54 % ± 3 | 4.8 ± 0.9 | 5.0 ± 0.7 | 3.43 ± 0.08 | 0 % ± 0 |
