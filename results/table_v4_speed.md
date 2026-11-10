**People vs agents vs agents with human approvals (20 seeds)** (mean ± 95 % interval over seeds)

*people*

| strategy | correct | wrong | typical wait (h) | slowest 10 % (h) | busiest 5 % get | reads per question | busiest 5 % read | refusals per question | approval wait, slowest 10 % (s) |
|---|---|---|---|---|---|---|---|---|---|
| Learned, local | 83 % ± 1 | 8 % ± 0 | 2.0 ± 0.1 | 7.4 ± 0.2 | 21 % ± 1 | 3.01 ± 0.06 | 21 % ± 1 | 0.00 ± 0.00 | – |
| Signed track records | 79 % ± 1 | 9 % ± 1 | 1.2 ± 0.0 | 3.4 ± 0.1 | 21 % ± 1 | 2.96 ± 0.05 | 21 % ± 1 | 0.00 ± 0.00 | – |
| Search + learned (hybrid) | 78 % ± 1 | 9 % ± 0 | 1.3 ± 0.0 | 3.5 ± 0.1 | 17 % ± 1 | 3.22 ± 0.07 | 17 % ± 1 | 0.00 ± 0.00 | – |
| Learned, local, load-aware | 76 % ± 1 | 9 % ± 1 | 1.2 ± 0.0 | 3.5 ± 0.1 | 17 % ± 1 | 3.42 ± 0.07 | 17 % ± 1 | 0.00 ± 0.00 | – |
| Learned, central log | 76 % ± 1 | 14 % ± 1 | 2.3 ± 0.2 | 8.3 ± 0.4 | 34 % ± 2 | 2.96 ± 0.08 | 34 % ± 2 | 0.00 ± 0.00 | – |
| Declared search | 65 % ± 2 | 7 % ± 0 | 1.9 ± 0.1 | 7.3 ± 0.3 | 21 % ± 2 | 4.13 ± 0.16 | 21 % ± 2 | 0.00 ± 0.00 | – |
| Declared search, trust-ranked | 62 % ± 2 | 9 % ± 1 | 2.2 ± 0.2 | 7.8 ± 0.3 | 23 % ± 2 | 4.22 ± 0.17 | 23 % ± 2 | 0.00 ± 0.00 | – |
| Phonebook | 62 % ± 1 | 6 % ± 0 | 1.4 ± 0.1 | 6.0 ± 0.2 | 11 % ± 0 | 4.24 ± 0.08 | 11 % ± 0 | 0.00 ± 0.00 | – |
| Ask the senior / oldest agent | 54 % ± 3 | 9 % ± 1 | 4.6 ± 0.6 | 13.0 ± 0.4 | 66 % ± 1 | 3.37 ± 0.06 | 63 % ± 1 | 0.00 ± 0.00 | – |

*agents*

| strategy | correct | wrong | typical wait (s) | slowest 10 % (s) | busiest 5 % get | reads per question | busiest 5 % read | refusals per question | approval wait, slowest 10 % (s) |
|---|---|---|---|---|---|---|---|---|---|
| Learned, local | 80 % ± 1 | 9 % ± 0 | 14.2 ± 0.2 | 40.9 ± 0.5 | 19 % ± 1 | 2.68 ± 0.03 | 19 % ± 1 | 0.32 ± 0.02 | – |
| Signed track records | 79 % ± 1 | 9 % ± 0 | 11.8 ± 0.1 | 30.0 ± 0.4 | 21 % ± 1 | 2.91 ± 0.04 | 21 % ± 1 | 0.00 ± 0.00 | – |
| Search + learned (hybrid) | 77 % ± 1 | 9 % ± 0 | 12.1 ± 0.1 | 31.0 ± 0.3 | 17 % ± 1 | 3.18 ± 0.04 | 17 % ± 1 | 0.00 ± 0.00 | – |
| Learned, local, load-aware | 76 % ± 1 | 9 % ± 0 | 11.5 ± 0.1 | 29.7 ± 0.3 | 17 % ± 1 | 3.35 ± 0.04 | 17 % ± 1 | 0.00 ± 0.00 | – |
| Learned, central log | 73 % ± 1 | 15 % ± 0 | 15.6 ± 0.4 | 45.2 ± 0.9 | 29 % ± 1 | 2.61 ± 0.05 | 28 % ± 1 | 0.32 ± 0.02 | – |
| Declared search | 62 % ± 2 | 7 % ± 0 | 14.9 ± 0.5 | 44.2 ± 1.7 | 19 % ± 1 | 3.68 ± 0.14 | 19 % ± 1 | 0.44 ± 0.02 | – |
| Declared search, trust-ranked | 59 % ± 2 | 9 % ± 1 | 16.1 ± 0.6 | 45.3 ± 1.2 | 21 % ± 1 | 3.72 ± 0.15 | 20 % ± 1 | 0.45 ± 0.02 | – |
| Phonebook | 59 % ± 1 | 6 % ± 0 | 11.7 ± 0.2 | 36.8 ± 0.6 | 11 % ± 0 | 3.84 ± 0.07 | 11 % ± 0 | 0.42 ± 0.02 | – |
| Ask the senior / oldest agent | 69 % ± 1 | 13 % ± 1 | 18.2 ± 0.7 | 47.1 ± 1.0 | 47 % ± 1 | 2.99 ± 0.07 | 46 % ± 1 | 0.40 ± 0.04 | – |

*agents+approvals*

| strategy | correct | wrong | typical wait (s) | slowest 10 % (s) | busiest 5 % get | reads per question | busiest 5 % read | refusals per question | approval wait, slowest 10 % (s) |
|---|---|---|---|---|---|---|---|---|---|
| Learned, local | 80 % ± 1 | 9 % ± 0 | 15.1 ± 0.3 | 48.5 ± 0.7 | 19 % ± 1 | 2.68 ± 0.03 | 19 % ± 1 | 0.32 ± 0.02 | 1768 ± 388 |
| Signed track records | 79 % ± 1 | 9 % ± 0 | 12.4 ± 0.2 | 34.6 ± 0.6 | 21 % ± 1 | 2.93 ± 0.04 | 21 % ± 1 | 0.00 ± 0.00 | 1739 ± 410 |
| Search + learned (hybrid) | 77 % ± 1 | 9 % ± 0 | 12.9 ± 0.2 | 35.9 ± 0.6 | 16 % ± 1 | 3.18 ± 0.04 | 16 % ± 1 | 0.00 ± 0.00 | 1727 ± 387 |
| Learned, local, load-aware | 75 % ± 1 | 9 % ± 0 | 12.0 ± 0.1 | 34.4 ± 0.5 | 17 % ± 1 | 3.35 ± 0.05 | 17 % ± 1 | 0.00 ± 0.00 | 1763 ± 442 |
| Learned, central log | 73 % ± 1 | 15 % ± 1 | 16.6 ± 0.5 | 54.1 ± 1.1 | 29 % ± 1 | 2.62 ± 0.05 | 28 % ± 1 | 0.32 ± 0.02 | 1894 ± 394 |
| Declared search | 62 % ± 2 | 7 % ± 0 | 16.2 ± 0.6 | 53.8 ± 1.8 | 19 % ± 1 | 3.68 ± 0.14 | 19 % ± 1 | 0.44 ± 0.02 | 1841 ± 413 |
| Declared search, trust-ranked | 59 % ± 2 | 9 % ± 1 | 17.4 ± 0.7 | 55.1 ± 1.4 | 21 % ± 1 | 3.72 ± 0.15 | 20 % ± 1 | 0.45 ± 0.02 | 1891 ± 411 |
| Phonebook | 59 % ± 1 | 6 % ± 0 | 12.5 ± 0.2 | 44.6 ± 0.7 | 11 % ± 0 | 3.84 ± 0.07 | 11 % ± 0 | 0.42 ± 0.02 | 1667 ± 424 |
| Ask the senior / oldest agent | 69 % ± 1 | 13 % ± 1 | 19.3 ± 0.7 | 55.5 ± 1.3 | 47 % ± 1 | 2.99 ± 0.07 | 46 % ± 1 | 0.40 ± 0.04 | 1839 ± 366 |
