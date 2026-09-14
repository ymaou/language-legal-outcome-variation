# Pilot report: pilot-1

Dry run: False. Calls with a reply: 96. Transport errors (retried, not draws): 0. Spent: $1.33.

## Replies, by configuration and arm

| configuration | arm | calls | ok | other statuses | keys as asked / fallback / other | fields in order | mean input tokens | cached share after 1st call | mean output tokens | mean reasoning tokens | mean seconds |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gemini | bt-de | 4 | 4 | none | 4 / 0 / 0 | 4 | 8,974 | 32% | 1,886 | 1,604 | 11.5 |
| gemini | bt-en | 4 | 4 | none | 4 / 0 / 0 | 4 | 9,026 | 31% | 1,357 | 1,104 | 8.2 |
| gemini | de-eng | 4 | 4 | none | 4 / 0 / 0 | 4 | 6,468 | 0% | 1,522 | 1,323 | 9.7 |
| gemini | de-lit | 4 | 4 | none | 4 / 0 / 0 | 4 | 6,557 | 0% | 1,272 | 1,074 | 7.8 |
| gemini | en | 4 | 4 | none | 4 / 0 / 0 | 4 | 5,004 | 0% | 1,234 | 1,083 | 8.2 |
| gemini | gr | 4 | 4 | none | 4 / 0 / 0 | 4 | 8,926 | 32% | 1,452 | 1,198 | 9.0 |
| sonnet | bt-de | 4 | 4 | none | 4 / 0 / 0 | 4 | 14,976 | 100% | 633 | 0 | 14.8 |
| sonnet | bt-en | 4 | 4 | none | 4 / 0 / 0 | 4 | 15,120 | 100% | 650 | 0 | 15.1 |
| sonnet | de-eng | 4 | 4 | none | 4 / 0 / 0 | 4 | 12,310 | 100% | 515 | 0 | 7.6 |
| sonnet | de-lit | 4 | 4 | none | 4 / 0 / 0 | 4 | 12,412 | 100% | 538 | 0 | 7.3 |
| sonnet | en | 4 | 4 | none | 4 / 0 / 0 | 4 | 7,126 | 100% | 313 | 0 | 5.1 |
| sonnet | gr | 4 | 4 | none | 4 / 0 / 0 | 4 | 14,900 | 100% | 568 | 0 | 13.4 |
| terra | bt-de | 4 | 4 | none | 4 / 0 / 0 | 4 | 8,532 | 100% | 406 | 84 | 9.0 |
| terra | bt-en | 4 | 4 | none | 4 / 0 / 0 | 4 | 8,592 | 100% | 352 | 56 | 8.2 |
| terra | de-eng | 4 | 4 | none | 4 / 0 / 0 | 4 | 6,062 | 100% | 214 | 38 | 4.4 |
| terra | de-lit | 4 | 4 | none | 4 / 0 / 0 | 4 | 6,132 | 100% | 204 | 44 | 4.3 |
| terra | en | 4 | 4 | none | 4 / 0 / 0 | 4 | 4,782 | 100% | 262 | 111 | 4.3 |
| terra | gr | 4 | 4 | none | 4 / 0 / 0 | 4 | 8,490 | 100% | 375 | 69 | 8.2 |
| terra-off | bt-de | 4 | 4 | none | 4 / 0 / 0 | 4 | 8,532 | 100% | 303 | 0 | 7.5 |
| terra-off | bt-en | 4 | 4 | none | 4 / 0 / 0 | 4 | 8,592 | 100% | 298 | 0 | 7.0 |
| terra-off | de-eng | 4 | 4 | none | 4 / 0 / 0 | 4 | 6,062 | 100% | 193 | 0 | 3.8 |
| terra-off | de-lit | 4 | 4 | none | 4 / 0 / 0 | 4 | 6,132 | 100% | 182 | 0 | 3.8 |
| terra-off | en | 4 | 4 | none | 4 / 0 / 0 | 4 | 4,782 | 100% | 164 | 0 | 3.2 |
| terra-off | gr | 4 | 4 | none | 4 / 0 / 0 | 4 | 8,490 | 100% | 333 | 0 | 8.4 |

## Projection of the full run

Input tokens are scaled from the pilot's tokens per character for each configuration and arm to every case; output and reasoning tokens are the pilot means for that configuration and arm; draws after the first in each block are charged at the cached share observed in the pilot; 5% is added for replacement draws. Dollars are compared with euros as they stand.

| configuration | cost at 31 draws (Greek 62) | cost at 25 draws (Greek 50) | calls at 31 | hours at 31, at current concurrency |
|---|---|---|---|---|
| terra | $12.18 | $9.96 | 2,170 | 0.5 |
| terra-off | $10.68 | $8.75 | 2,170 | 0.4 |
| sonnet | $19.19 | $15.79 | 2,170 | 0.8 |
| gemini | $21.78 | $17.58 | 2,170 | 0.7 |
| **all** | **$63.84** | **$52.08** | | |

**Under the budget rule (v8 section 10.3): Run at 31 draws: projection within the €100 budget.**

Hours assume no rate limit binds; providers running in parallel, so the run takes about the longest of the three.

**Pilot cost, computed from list prices: $1.33** for 96 replies. Compare with the providers' dashboards; the ledger is raw/COSTS.md.
