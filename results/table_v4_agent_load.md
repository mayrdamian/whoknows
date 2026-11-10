**Agents at 15, 60 and 120 questions per agent per hour (10 seeds; 30/h is in table_v4_speed)** (mean ± 95 % interval over seeds)

| variant | strategy | correct | wrong | slowest 10 % (s) | busiest 5 % get | refusals per question | reads per question |
|---|---|---|---|---|---|---|---|
| rate=15/h | Learned, local | 80 % ± 1 | 8 % ± 1 | 40.5 ± 1.2 | 19 % ± 1 | 0.30 ± 0.02 | 2.75 ± 0.06 |
| rate=60/h | Learned, local | 80 % ± 1 | 9 % ± 1 | 44.0 ± 1.1 | 20 % ± 1 | 0.36 ± 0.02 | 2.52 ± 0.04 |
| rate=120/h | Learned, local | 78 % ± 1 | 10 % ± 1 | 51.5 ± 2.0 | 20 % ± 1 | 0.51 ± 0.05 | 2.43 ± 0.06 |
| rate=15/h | Signed track records | 79 % ± 1 | 9 % ± 1 | 29.2 ± 0.6 | 21 % ± 1 | 0.00 ± 0.00 | 2.98 ± 0.06 |
| rate=60/h | Signed track records | 79 % ± 1 | 9 % ± 1 | 32.2 ± 1.0 | 21 % ± 1 | 0.00 ± 0.00 | 2.89 ± 0.07 |
| rate=120/h | Signed track records | 77 % ± 1 | 10 % ± 1 | 35.5 ± 1.5 | 19 % ± 1 | 0.00 ± 0.00 | 2.98 ± 0.07 |
| rate=15/h | Search + learned (hybrid) | 78 % ± 1 | 8 % ± 1 | 30.8 ± 0.6 | 17 % ± 1 | 0.00 ± 0.00 | 3.23 ± 0.06 |
| rate=60/h | Search + learned (hybrid) | 77 % ± 1 | 10 % ± 1 | 32.7 ± 0.7 | 16 % ± 1 | 0.00 ± 0.00 | 3.10 ± 0.04 |
| rate=120/h | Search + learned (hybrid) | 75 % ± 1 | 11 % ± 1 | 36.1 ± 0.9 | 15 % ± 1 | 0.00 ± 0.00 | 3.14 ± 0.06 |
| rate=15/h | Learned, local, load-aware | 76 % ± 1 | 8 % ± 1 | 29.4 ± 0.5 | 17 % ± 1 | 0.00 ± 0.00 | 3.40 ± 0.06 |
| rate=60/h | Learned, local, load-aware | 76 % ± 1 | 9 % ± 1 | 31.4 ± 0.8 | 17 % ± 1 | 0.00 ± 0.00 | 3.23 ± 0.04 |
| rate=120/h | Learned, local, load-aware | 74 % ± 1 | 11 % ± 1 | 34.7 ± 1.0 | 16 % ± 1 | 0.00 ± 0.00 | 3.24 ± 0.07 |
| rate=15/h | Learned, central log | 74 % ± 1 | 14 % ± 1 | 42.9 ± 1.6 | 29 % ± 2 | 0.28 ± 0.03 | 2.61 ± 0.08 |
| rate=60/h | Learned, central log | 73 % ± 1 | 15 % ± 1 | 51.5 ± 2.9 | 28 % ± 2 | 0.39 ± 0.04 | 2.53 ± 0.07 |
| rate=120/h | Learned, central log | 70 % ± 1 | 15 % ± 0 | 61.6 ± 3.0 | 27 % ± 2 | 0.62 ± 0.09 | 2.51 ± 0.07 |
| rate=15/h | Declared search | 63 % ± 3 | 7 % ± 1 | 42.3 ± 1.7 | 20 % ± 3 | 0.39 ± 0.03 | 3.65 ± 0.21 |
| rate=60/h | Declared search | 63 % ± 3 | 7 % ± 1 | 48.5 ± 2.8 | 19 % ± 3 | 0.49 ± 0.03 | 3.60 ± 0.19 |
| rate=120/h | Declared search | 61 % ± 3 | 7 % ± 1 | 58.3 ± 4.9 | 19 % ± 3 | 0.67 ± 0.06 | 3.54 ± 0.20 |
| rate=15/h | Ask the senior / oldest agent | 70 % ± 1 | 11 % ± 1 | 43.7 ± 2.0 | 47 % ± 1 | 0.37 ± 0.03 | 3.09 ± 0.09 |
| rate=60/h | Ask the senior / oldest agent | 69 % ± 2 | 12 % ± 1 | 61.1 ± 2.1 | 50 % ± 1 | 0.75 ± 0.11 | 2.77 ± 0.06 |
| rate=120/h | Ask the senior / oldest agent | 64 % ± 1 | 13 % ± 1 | 70.6 ± 2.9 | 56 % ± 1 | 1.62 ± 0.12 | 2.47 ± 0.06 |
