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
| Learned, local | 84 % ± 1 | 9 % ± 0 | 6.3 ± 0.1 | 21.4 ± 0.3 | 20 % ± 1 | 2.60 ± 0.04 | 20 % ± 1 | 0.01 ± 0.00 | – |
| Signed track records | 86 % ± 1 | 9 % ± 0 | 6.7 ± 0.1 | 19.3 ± 0.3 | 24 % ± 1 | 2.30 ± 0.04 | 24 % ± 1 | 0.00 ± 0.00 | – |
| Search + learned (hybrid) | 85 % ± 1 | 9 % ± 0 | 6.7 ± 0.1 | 19.9 ± 0.2 | 18 % ± 1 | 2.59 ± 0.04 | 18 % ± 1 | 0.00 ± 0.00 | – |
| Learned, local, load-aware | 83 % ± 1 | 9 % ± 0 | 6.0 ± 0.1 | 18.3 ± 0.2 | 19 % ± 1 | 2.78 ± 0.04 | 19 % ± 1 | 0.00 ± 0.00 | – |
| Learned, central log | 77 % ± 1 | 15 % ± 1 | 7.8 ± 0.4 | 24.9 ± 0.7 | 30 % ± 1 | 2.58 ± 0.06 | 30 % ± 1 | 0.01 ± 0.00 | – |
| Declared search | 65 % ± 2 | 7 % ± 0 | 6.6 ± 0.4 | 23.3 ± 0.7 | 20 % ± 1 | 3.86 ± 0.16 | 20 % ± 1 | 0.02 ± 0.00 | – |
| Declared search, trust-ranked | 63 % ± 2 | 9 % ± 1 | 7.6 ± 0.5 | 24.3 ± 0.8 | 21 % ± 1 | 3.91 ± 0.17 | 21 % ± 1 | 0.02 ± 0.00 | – |
| Phonebook | 62 % ± 1 | 6 % ± 0 | 4.4 ± 0.2 | 18.6 ± 0.5 | 11 % ± 0 | 4.02 ± 0.08 | 11 % ± 0 | 0.02 ± 0.00 | – |
| Ask the senior / oldest agent | 73 % ± 2 | 13 % ± 1 | 10.1 ± 0.8 | 27.9 ± 1.4 | 47 % ± 1 | 2.98 ± 0.08 | 46 % ± 1 | 0.02 ± 0.01 | – |

*agents+approvals*

| strategy | correct | wrong | typical wait (s) | slowest 10 % (s) | busiest 5 % get | reads per question | busiest 5 % read | refusals per question | approval wait, slowest 10 % (s) |
|---|---|---|---|---|---|---|---|---|---|
| Learned, local | 84 % ± 1 | 9 % ± 0 | 7.0 ± 0.1 | 25.9 ± 0.4 | 20 % ± 1 | 2.60 ± 0.04 | 20 % ± 1 | 0.01 ± 0.00 | 1912 ± 423 |
| Signed track records | 86 % ± 1 | 9 % ± 0 | 7.3 ± 0.2 | 22.4 ± 0.4 | 23 % ± 1 | 2.31 ± 0.04 | 23 % ± 1 | 0.00 ± 0.00 | 1921 ± 434 |
| Search + learned (hybrid) | 85 % ± 1 | 9 % ± 0 | 7.5 ± 0.1 | 23.2 ± 0.3 | 18 % ± 1 | 2.60 ± 0.04 | 18 % ± 1 | 0.00 ± 0.00 | 1804 ± 391 |
| Learned, local, load-aware | 83 % ± 1 | 9 % ± 0 | 6.6 ± 0.1 | 21.5 ± 0.4 | 18 % ± 1 | 2.78 ± 0.04 | 18 % ± 1 | 0.00 ± 0.00 | 1840 ± 390 |
| Learned, central log | 77 % ± 1 | 14 % ± 0 | 8.8 ± 0.4 | 29.9 ± 0.7 | 30 % ± 2 | 2.58 ± 0.06 | 30 % ± 1 | 0.01 ± 0.00 | 2133 ± 510 |
| Declared search | 65 % ± 2 | 7 % ± 0 | 7.5 ± 0.4 | 29.4 ± 0.8 | 20 % ± 1 | 3.86 ± 0.16 | 20 % ± 1 | 0.02 ± 0.00 | 2012 ± 448 |
| Declared search, trust-ranked | 63 % ± 2 | 9 % ± 1 | 8.6 ± 0.5 | 30.6 ± 0.9 | 21 % ± 1 | 3.91 ± 0.17 | 21 % ± 1 | 0.02 ± 0.00 | 2064 ± 466 |
| Phonebook | 62 % ± 1 | 6 % ± 0 | 5.0 ± 0.2 | 23.4 ± 0.5 | 11 % ± 0 | 4.02 ± 0.08 | 11 % ± 0 | 0.02 ± 0.00 | 1772 ± 432 |
| Ask the senior / oldest agent | 73 % ± 2 | 13 % ± 1 | 10.8 ± 0.6 | 33.4 ± 1.4 | 47 % ± 1 | 2.98 ± 0.09 | 46 % ± 1 | 0.02 ± 0.01 | 2160 ± 493 |
