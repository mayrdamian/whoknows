**Asker-set priority as more askers inflate (agents, 60/h, 10 seeds)** (mean ± 95 % interval over seeds)

| strategy | variant | correct | high: correct | high: typical wait (s) | low: typical wait (s) | refusals per question | reads per question |
|---|---|---|---|---|---|---|---|
| Learned, local | priority=asker,inflaters=0.0 | 80 % ± 1 | 87 % ± 0 | 14.1 ± 0.4 | 16.1 ± 0.6 | 0.30 ± 0.02 | 2.51 ± 0.04 |
| Learned, local | priority=asker,inflaters=0.3 | 82 % ± 1 | 87 % ± 1 | 14.3 ± 0.2 | 14.8 ± 0.3 | 0.24 ± 0.02 | 2.49 ± 0.04 |
| Learned, local | priority=asker,inflaters=0.6 | 83 % ± 1 | 87 % ± 1 | 15.0 ± 0.3 | 14.3 ± 0.4 | 0.16 ± 0.01 | 2.47 ± 0.05 |
| Learned, local | priority=audit,inflaters=0.0 | 80 % ± 1 | 87 % ± 1 | 14.2 ± 0.2 | 16.6 ± 0.7 | 0.32 ± 0.02 | 3.08 ± 0.05 |
| Learned, local | priority=audit,inflaters=0.3 | 81 % ± 1 | 87 % ± 0 | 14.5 ± 0.2 | 15.5 ± 0.5 | 0.27 ± 0.02 | 3.07 ± 0.05 |
| Learned, local | priority=audit,inflaters=0.6 | 82 % ± 1 | 87 % ± 1 | 15.0 ± 0.5 | 15.1 ± 0.5 | 0.21 ± 0.01 | 3.05 ± 0.05 |
| Learned, local | priority=budget,inflaters=0.0 | 80 % ± 1 | 86 % ± 0 | 14.2 ± 0.4 | 16.0 ± 0.6 | 0.31 ± 0.02 | 2.51 ± 0.04 |
| Learned, local | priority=budget,inflaters=0.3 | 80 % ± 1 | 85 % ± 1 | 14.5 ± 0.3 | 15.6 ± 0.4 | 0.31 ± 0.02 | 2.51 ± 0.04 |
| Learned, local | priority=budget,inflaters=0.6 | 81 % ± 1 | 84 % ± 1 | 15.3 ± 0.4 | 15.3 ± 0.4 | 0.31 ± 0.02 | 2.51 ± 0.04 |
| Learned, local, load-aware | priority=asker,inflaters=0.0 | 77 % ± 0 | 83 % ± 1 | 12.6 ± 0.3 | 12.4 ± 0.4 | 0.00 ± 0.00 | 3.16 ± 0.05 |
| Learned, local, load-aware | priority=asker,inflaters=0.3 | 78 % ± 1 | 84 % ± 1 | 12.8 ± 0.2 | 12.2 ± 0.3 | 0.00 ± 0.00 | 3.06 ± 0.04 |
| Learned, local, load-aware | priority=asker,inflaters=0.6 | 80 % ± 1 | 84 % ± 1 | 13.1 ± 0.2 | 11.9 ± 0.3 | 0.00 ± 0.00 | 2.96 ± 0.04 |
| Learned, local, load-aware | priority=audit,inflaters=0.0 | 76 % ± 1 | 83 % ± 1 | 12.9 ± 0.2 | 12.9 ± 0.4 | 0.00 ± 0.00 | 3.81 ± 0.05 |
| Learned, local, load-aware | priority=audit,inflaters=0.3 | 77 % ± 1 | 84 % ± 0 | 13.1 ± 0.3 | 12.6 ± 0.3 | 0.00 ± 0.00 | 3.72 ± 0.05 |
| Learned, local, load-aware | priority=audit,inflaters=0.6 | 78 % ± 1 | 84 % ± 1 | 13.2 ± 0.3 | 12.3 ± 0.4 | 0.00 ± 0.00 | 3.65 ± 0.05 |
| Learned, local, load-aware | priority=budget,inflaters=0.0 | 77 % ± 1 | 83 % ± 1 | 12.8 ± 0.3 | 12.5 ± 0.6 | 0.00 ± 0.00 | 3.17 ± 0.05 |
| Learned, local, load-aware | priority=budget,inflaters=0.3 | 77 % ± 0 | 82 % ± 1 | 12.9 ± 0.3 | 12.3 ± 0.3 | 0.00 ± 0.00 | 3.15 ± 0.04 |
| Learned, local, load-aware | priority=budget,inflaters=0.6 | 77 % ± 0 | 80 % ± 1 | 13.1 ± 0.2 | 12.1 ± 0.4 | 0.00 ± 0.00 | 3.15 ± 0.04 |
| Ask the senior / oldest agent | priority=asker,inflaters=0.0 | 69 % ± 1 | 78 % ± 1 | 13.9 ± 0.4 | 26.8 ± 2.4 | 0.58 ± 0.10 | 2.77 ± 0.06 |
| Ask the senior / oldest agent | priority=asker,inflaters=0.3 | 70 % ± 1 | 78 % ± 1 | 15.5 ± 1.0 | 20.7 ± 0.8 | 0.50 ± 0.08 | 2.77 ± 0.06 |
| Ask the senior / oldest agent | priority=asker,inflaters=0.6 | 72 % ± 1 | 79 % ± 1 | 21.3 ± 3.2 | 21.8 ± 2.5 | 0.39 ± 0.06 | 2.77 ± 0.06 |
| Ask the senior / oldest agent | priority=audit,inflaters=0.0 | 68 % ± 1 | 78 % ± 1 | 14.6 ± 0.4 | 28.4 ± 2.1 | 0.73 ± 0.11 | 3.50 ± 0.08 |
| Ask the senior / oldest agent | priority=audit,inflaters=0.3 | 69 % ± 1 | 78 % ± 1 | 15.9 ± 0.6 | 23.9 ± 1.4 | 0.69 ± 0.11 | 3.50 ± 0.07 |
| Ask the senior / oldest agent | priority=audit,inflaters=0.6 | 70 % ± 1 | 78 % ± 1 | 18.1 ± 1.1 | 21.5 ± 1.3 | 0.64 ± 0.10 | 3.48 ± 0.07 |
| Ask the senior / oldest agent | priority=budget,inflaters=0.0 | 69 % ± 1 | 77 % ± 1 | 14.2 ± 0.5 | 26.9 ± 2.4 | 0.59 ± 0.10 | 2.77 ± 0.06 |
| Ask the senior / oldest agent | priority=budget,inflaters=0.3 | 69 % ± 2 | 76 % ± 1 | 16.4 ± 1.0 | 23.9 ± 1.0 | 0.61 ± 0.11 | 2.77 ± 0.06 |
| Ask the senior / oldest agent | priority=budget,inflaters=0.6 | 69 % ± 1 | 75 % ± 1 | 21.7 ± 2.3 | 25.1 ± 2.2 | 0.64 ± 0.11 | 2.77 ± 0.05 |
