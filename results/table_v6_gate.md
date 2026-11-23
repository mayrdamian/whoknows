**Gate: 1,000 agents with every large-network option, against Phase 2 (same seeds)**

| strategy | Phase 2 | v6 options | difference | busiest 1 %: Phase 2 | v6 options |
|---|---|---|---|---|---|
| Learned, local | 57.2 % | 56.1 % | -1.1 | 19 % | 18 % |
| Signed track records | 73.1 % | 73.0 % | -0.1 | 12 % | 14 % |
| Search + learned (hybrid) | 71.6 % | 71.4 % | -0.2 | 11 % | 12 % |
| Learned, local, load-aware | 55.1 % | 54.0 % | -1.1 | 14 % | 16 % |
| Learned, central log | 57.0 % | 55.0 % | -2.0 | 26 % | 27 % |
| Declared search | 66.9 % | 66.5 % | -0.4 | 10 % | 12 % |
| Declared search, trust-ranked | 63.4 % | 62.2 % | -1.2 | 13 % | 14 % |
| Phonebook | 21.5 % | 21.3 % | -0.2 | 3 % | 3 % |
| Ask the senior / oldest agent | 36.0 % | 35.8 % | -0.2 | 67 % | 67 % |

- seeds compared: 0, 1, 2, 3, 4
- largest difference in the share answered: 2.0 points (pass if at most 4)
- rank correlation of the nine strategies: 1.00 (pass if at least 0.9)
- asking the oldest agent, busiest 1 % get: 67 % → 67 % (pass if within 5 points)
- **gate passed**
