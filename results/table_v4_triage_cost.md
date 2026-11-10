**Answerer-set priority by cost of a triage read (agents, 60/h, 10 seeds)** (mean ± 95 % interval over seeds)

| strategy | variant | correct | high: correct | high: typical wait (s) | low: typical wait (s) | refusals per question | reads per question |
|---|---|---|---|---|---|---|---|
| Learned, local | triage=0.0s | 81 % ± 1 | 88 % ± 1 | 13.6 ± 0.2 | 16.5 ± 0.7 | 0.31 ± 0.02 | 5.36 ± 0.07 |
| Learned, local | triage=2.0s | 79 % ± 1 | 88 % ± 1 | 15.6 ± 0.2 | 19.2 ± 1.0 | 0.39 ± 0.03 | 5.49 ± 0.08 |
| Learned, local | triage=8.0s | 72 % ± 2 | 86 % ± 1 | 24.7 ± 1.0 | 27.4 ± 1.0 | 0.81 ± 0.11 | 6.08 ± 0.16 |
| Learned, local, load-aware | triage=0.0s | 77 % ± 1 | 84 % ± 1 | 12.4 ± 0.2 | 12.7 ± 0.4 | 0.00 ± 0.00 | 6.30 ± 0.09 |
| Learned, local, load-aware | triage=2.0s | 75 % ± 1 | 84 % ± 1 | 13.8 ± 0.4 | 14.3 ± 0.4 | 0.00 ± 0.00 | 6.56 ± 0.10 |
| Learned, local, load-aware | triage=8.0s | 68 % ± 2 | 81 % ± 1 | 20.6 ± 0.6 | 19.8 ± 0.4 | 0.00 ± 0.00 | 7.64 ± 0.23 |
| Ask the senior / oldest agent | triage=0.0s | 69 % ± 1 | 80 % ± 1 | 13.0 ± 0.3 | 33.1 ± 4.0 | 0.58 ± 0.10 | 6.27 ± 0.13 |
| Ask the senior / oldest agent | triage=2.0s | 55 % ± 3 | 77 % ± 1 | 44.4 ± 6.9 | 23.7 ± 2.5 | 2.23 ± 0.30 | 7.25 ± 0.15 |
| Ask the senior / oldest agent | triage=8.0s | 23 % ± 2 | 24 % ± 2 | 14.6 ± 1.0 | 14.0 ± 0.9 | 5.59 ± 0.14 | 7.35 ± 0.12 |
