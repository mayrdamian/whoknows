**Agents at 15, 60 and 120 questions per agent per hour (10 seeds; 30/h is in table_v4_speed)** (mean ± 95 % interval over seeds)

| variant | strategy | correct | wrong | slowest 10 % (s) | busiest 5 % get | refusals per question | reads per question |
|---|---|---|---|---|---|---|---|
| rate=15/h | Learned, local | 85 % ± 1 | 8 % ± 1 | 20.4 ± 0.5 | 20 % ± 1 | 0.01 ± 0.00 | 2.70 ± 0.05 |
| rate=60/h | Learned, local | 85 % ± 1 | 9 % ± 1 | 25.0 ± 1.3 | 21 % ± 1 | 0.02 ± 0.00 | 2.43 ± 0.06 |
| rate=120/h | Learned, local | 84 % ± 1 | 10 % ± 1 | 35.7 ± 2.3 | 21 % ± 1 | 0.07 ± 0.02 | 2.34 ± 0.05 |
| rate=15/h | Signed track records | 86 % ± 2 | 9 % ± 1 | 18.6 ± 0.5 | 24 % ± 2 | 0.00 ± 0.00 | 2.39 ± 0.08 |
| rate=60/h | Signed track records | 87 % ± 1 | 9 % ± 1 | 21.3 ± 0.8 | 24 % ± 1 | 0.00 ± 0.00 | 2.20 ± 0.07 |
| rate=120/h | Signed track records | 86 % ± 1 | 9 % ± 1 | 25.8 ± 1.3 | 22 % ± 1 | 0.00 ± 0.00 | 2.24 ± 0.07 |
| rate=15/h | Search + learned (hybrid) | 85 % ± 1 | 8 % ± 1 | 19.5 ± 0.4 | 17 % ± 1 | 0.00 ± 0.00 | 2.68 ± 0.05 |
| rate=60/h | Search + learned (hybrid) | 85 % ± 1 | 9 % ± 1 | 21.2 ± 0.5 | 18 % ± 1 | 0.00 ± 0.00 | 2.46 ± 0.05 |
| rate=120/h | Search + learned (hybrid) | 84 % ± 1 | 10 % ± 1 | 24.9 ± 0.8 | 17 % ± 1 | 0.00 ± 0.00 | 2.46 ± 0.06 |
| rate=15/h | Learned, local, load-aware | 83 % ± 1 | 8 % ± 1 | 17.8 ± 0.5 | 19 % ± 1 | 0.00 ± 0.00 | 2.87 ± 0.05 |
| rate=60/h | Learned, local, load-aware | 84 % ± 1 | 9 % ± 1 | 19.9 ± 0.5 | 19 % ± 1 | 0.00 ± 0.00 | 2.61 ± 0.05 |
| rate=120/h | Learned, local, load-aware | 83 % ± 1 | 10 % ± 1 | 23.8 ± 0.9 | 17 % ± 1 | 0.00 ± 0.00 | 2.57 ± 0.06 |
| rate=15/h | Learned, central log | 78 % ± 1 | 14 % ± 1 | 22.4 ± 0.7 | 31 % ± 2 | 0.01 ± 0.00 | 2.59 ± 0.09 |
| rate=60/h | Learned, central log | 77 % ± 1 | 15 % ± 1 | 32.4 ± 3.4 | 30 % ± 2 | 0.04 ± 0.02 | 2.51 ± 0.10 |
| rate=120/h | Learned, central log | 76 % ± 1 | 15 % ± 1 | 46.7 ± 4.6 | 28 % ± 2 | 0.16 ± 0.06 | 2.52 ± 0.07 |
| rate=15/h | Declared search | 66 % ± 4 | 7 % ± 1 | 21.6 ± 0.9 | 20 % ± 3 | 0.02 ± 0.00 | 3.82 ± 0.24 |
| rate=60/h | Declared search | 66 % ± 3 | 7 % ± 1 | 27.5 ± 2.8 | 20 % ± 3 | 0.02 ± 0.01 | 3.80 ± 0.22 |
| rate=120/h | Declared search | 66 % ± 3 | 7 % ± 1 | 41.4 ± 8.0 | 20 % ± 3 | 0.08 ± 0.04 | 3.79 ± 0.22 |
| rate=15/h | Ask the senior / oldest agent | 74 % ± 1 | 12 % ± 1 | 22.3 ± 0.8 | 47 % ± 1 | 0.01 ± 0.00 | 3.06 ± 0.08 |
| rate=60/h | Ask the senior / oldest agent | 75 % ± 1 | 13 % ± 1 | 46.5 ± 3.1 | 48 % ± 1 | 0.23 ± 0.06 | 2.76 ± 0.08 |
| rate=120/h | Ask the senior / oldest agent | 72 % ± 2 | 13 % ± 1 | 62.3 ± 3.2 | 54 % ± 2 | 0.90 ± 0.11 | 2.58 ± 0.06 |
