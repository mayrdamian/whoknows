**Asker-set priority as more askers inflate (agents, 60/h, 10 seeds)** (mean ± 95 % interval over seeds)

| strategy | variant | correct | high: correct | high: typical wait (s) | low: typical wait (s) | refusals per question | reads per question |
|---|---|---|---|---|---|---|---|
| Learned, local | priority=asker,inflaters=0.0 | 85 % ± 1 | 88 % ± 1 | 8.1 ± 0.3 | 7.2 ± 0.4 | 0.01 ± 0.00 | 2.44 ± 0.05 |
| Learned, local | priority=asker,inflaters=0.3 | 85 % ± 1 | 88 % ± 1 | 8.6 ± 0.4 | 6.9 ± 0.4 | 0.01 ± 0.00 | 2.44 ± 0.05 |
| Learned, local | priority=asker,inflaters=0.6 | 85 % ± 1 | 88 % ± 1 | 8.8 ± 0.6 | 6.9 ± 0.4 | 0.01 ± 0.00 | 2.43 ± 0.05 |
| Learned, local | priority=audit,inflaters=0.0 | 85 % ± 1 | 88 % ± 1 | 8.5 ± 0.3 | 7.7 ± 0.5 | 0.01 ± 0.00 | 2.92 ± 0.07 |
| Learned, local | priority=audit,inflaters=0.3 | 85 % ± 1 | 88 % ± 1 | 8.7 ± 0.4 | 7.4 ± 0.5 | 0.01 ± 0.00 | 2.92 ± 0.07 |
| Learned, local | priority=audit,inflaters=0.6 | 85 % ± 1 | 88 % ± 1 | 9.0 ± 0.5 | 7.3 ± 0.4 | 0.01 ± 0.00 | 2.92 ± 0.07 |
| Learned, local | priority=budget,inflaters=0.0 | 85 % ± 1 | 88 % ± 1 | 8.2 ± 0.4 | 7.2 ± 0.4 | 0.01 ± 0.00 | 2.43 ± 0.05 |
| Learned, local | priority=budget,inflaters=0.3 | 85 % ± 1 | 88 % ± 1 | 8.5 ± 0.5 | 7.1 ± 0.4 | 0.01 ± 0.00 | 2.43 ± 0.05 |
| Learned, local | priority=budget,inflaters=0.6 | 85 % ± 1 | 88 % ± 1 | 8.9 ± 0.6 | 7.1 ± 0.4 | 0.01 ± 0.00 | 2.43 ± 0.05 |
| Learned, local, load-aware | priority=asker,inflaters=0.0 | 84 % ± 1 | 87 % ± 1 | 7.6 ± 0.2 | 6.5 ± 0.2 | 0.00 ± 0.00 | 2.61 ± 0.06 |
| Learned, local, load-aware | priority=asker,inflaters=0.3 | 84 % ± 1 | 87 % ± 1 | 7.8 ± 0.3 | 6.3 ± 0.2 | 0.00 ± 0.00 | 2.60 ± 0.06 |
| Learned, local, load-aware | priority=asker,inflaters=0.6 | 84 % ± 1 | 87 % ± 1 | 8.2 ± 0.3 | 6.4 ± 0.3 | 0.00 ± 0.00 | 2.60 ± 0.05 |
| Learned, local, load-aware | priority=audit,inflaters=0.0 | 84 % ± 1 | 87 % ± 1 | 7.9 ± 0.2 | 6.8 ± 0.3 | 0.00 ± 0.00 | 3.12 ± 0.07 |
| Learned, local, load-aware | priority=audit,inflaters=0.3 | 84 % ± 1 | 87 % ± 1 | 8.2 ± 0.2 | 6.8 ± 0.3 | 0.00 ± 0.00 | 3.11 ± 0.06 |
| Learned, local, load-aware | priority=audit,inflaters=0.6 | 84 % ± 1 | 87 % ± 1 | 8.2 ± 0.4 | 6.7 ± 0.2 | 0.00 ± 0.00 | 3.11 ± 0.05 |
| Learned, local, load-aware | priority=budget,inflaters=0.0 | 84 % ± 1 | 87 % ± 1 | 7.6 ± 0.2 | 6.5 ± 0.2 | 0.00 ± 0.00 | 2.61 ± 0.05 |
| Learned, local, load-aware | priority=budget,inflaters=0.3 | 84 % ± 1 | 87 % ± 1 | 7.8 ± 0.2 | 6.4 ± 0.3 | 0.00 ± 0.00 | 2.61 ± 0.06 |
| Learned, local, load-aware | priority=budget,inflaters=0.6 | 84 % ± 1 | 87 % ± 1 | 8.0 ± 0.3 | 6.4 ± 0.3 | 0.00 ± 0.00 | 2.60 ± 0.05 |
| Ask the senior / oldest agent | priority=asker,inflaters=0.0 | 74 % ± 1 | 80 % ± 1 | 9.5 ± 0.6 | 17.5 ± 3.5 | 0.13 ± 0.05 | 2.79 ± 0.07 |
| Ask the senior / oldest agent | priority=asker,inflaters=0.3 | 74 % ± 1 | 80 % ± 1 | 10.7 ± 1.0 | 13.1 ± 1.4 | 0.12 ± 0.05 | 2.78 ± 0.08 |
| Ask the senior / oldest agent | priority=asker,inflaters=0.6 | 74 % ± 1 | 80 % ± 1 | 15.6 ± 3.1 | 14.8 ± 2.2 | 0.15 ± 0.06 | 2.78 ± 0.08 |
| Ask the senior / oldest agent | priority=audit,inflaters=0.0 | 74 % ± 1 | 80 % ± 1 | 10.1 ± 0.4 | 19.4 ± 3.6 | 0.20 ± 0.06 | 3.41 ± 0.09 |
| Ask the senior / oldest agent | priority=audit,inflaters=0.3 | 74 % ± 1 | 80 % ± 1 | 11.0 ± 0.6 | 15.6 ± 2.0 | 0.21 ± 0.06 | 3.40 ± 0.09 |
| Ask the senior / oldest agent | priority=audit,inflaters=0.6 | 74 % ± 1 | 80 % ± 1 | 12.5 ± 0.7 | 15.0 ± 2.0 | 0.23 ± 0.06 | 3.40 ± 0.09 |
| Ask the senior / oldest agent | priority=budget,inflaters=0.0 | 74 % ± 1 | 80 % ± 1 | 9.9 ± 0.5 | 17.7 ± 3.6 | 0.14 ± 0.05 | 2.79 ± 0.07 |
| Ask the senior / oldest agent | priority=budget,inflaters=0.3 | 75 % ± 1 | 80 % ± 1 | 11.0 ± 0.5 | 15.4 ± 1.9 | 0.14 ± 0.06 | 2.78 ± 0.07 |
| Ask the senior / oldest agent | priority=budget,inflaters=0.6 | 74 % ± 1 | 80 % ± 1 | 14.8 ± 2.1 | 17.0 ± 3.1 | 0.18 ± 0.06 | 2.78 ± 0.07 |
