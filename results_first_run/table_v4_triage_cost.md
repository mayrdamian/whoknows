**Answerer-set priority by cost of a triage read (agents, 60/h, 10 seeds)** (mean ± 95 % interval over seeds)

| strategy | variant | correct | high: correct | high: typical wait (s) | low: typical wait (s) | refusals per question | reads per question |
|---|---|---|---|---|---|---|---|
| Learned, local | triage=0.0s | 85 % ± 1 | 88 % ± 1 | 7.9 ± 0.3 | 7.3 ± 0.5 | 0.01 ± 0.00 | 4.89 ± 0.11 |
| Learned, local | triage=2.0s | 85 % ± 1 | 88 % ± 1 | 10.1 ± 0.4 | 9.8 ± 0.8 | 0.02 ± 0.01 | 4.91 ± 0.11 |
| Learned, local | triage=8.0s | 83 % ± 1 | 88 % ± 1 | 16.3 ± 0.8 | 16.8 ± 1.1 | 0.07 ± 0.02 | 5.19 ± 0.16 |
| Learned, local, load-aware | triage=0.0s | 84 % ± 1 | 87 % ± 1 | 7.4 ± 0.2 | 6.4 ± 0.2 | 0.00 ± 0.00 | 5.20 ± 0.10 |
| Learned, local, load-aware | triage=2.0s | 84 % ± 1 | 87 % ± 1 | 9.1 ± 0.3 | 8.5 ± 0.4 | 0.00 ± 0.00 | 5.27 ± 0.10 |
| Learned, local, load-aware | triage=8.0s | 81 % ± 1 | 86 % ± 1 | 14.6 ± 0.2 | 14.5 ± 0.5 | 0.00 ± 0.00 | 5.64 ± 0.16 |
| Ask the senior / oldest agent | triage=0.0s | 74 % ± 1 | 81 % ± 1 | 8.5 ± 0.5 | 22.8 ± 6.3 | 0.13 ± 0.05 | 5.79 ± 0.16 |
| Ask the senior / oldest agent | triage=2.0s | 66 % ± 2 | 79 % ± 1 | 30.1 ± 6.2 | 22.4 ± 3.8 | 1.13 ± 0.19 | 6.79 ± 0.20 |
| Ask the senior / oldest agent | triage=8.0s | 26 % ± 2 | 24 % ± 2 | 8.8 ± 0.9 | 8.3 ± 0.4 | 5.35 ± 0.15 | 7.29 ± 0.15 |
