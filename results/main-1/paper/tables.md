# Paper tables: main-1

## T1 sensitivity

| model | Greek draws | granted in full | granted in part | dismissed | agreement with court | baseline | MCC |
|---|---|---|---|---|---|---|---|
| GPT-5.6 Terra | 620 | 0.0% | 0.0% | 100.0% | 0.40 | 0.40 | 0.00 |
| GPT-5.6 Terra, reasoning off | 620 | 2.4% | 1.3% | 96.3% | 0.40 | 0.40 | 0.00 |
| Claude Sonnet 5 | 620 | 0.0% | 11.9% | 88.1% | 0.40 | 0.40 | 0.00 |
| Gemini 3.6 Flash | 620 | 6.9% | 0.0% | 93.1% | 0.50 | 0.40 | 0.29 |

## T2 rates

| model | F (noise floor) | W_en (rewording) | L_EN (language) | Δ_EN = L_EN − W_en [95% CI] | W_de | L_DE | Δ_DE [95% CI] |
|---|---|---|---|---|---|---|---|
| GPT-5.6 Terra | 0.00 | 0.00 | 0.00 | 0.00 [0.00, 0.00] | 0.00 | 0.00 | 0.00 [0.00, 0.00] |
| GPT-5.6 Terra, reasoning off | 0.00 | 0.00 | 0.00 | 0.00 [0.00, 0.00] | 0.00 | 0.00 | 0.00 [0.00, 0.00] |
| Claude Sonnet 5 | 0.00 | 0.20 | 0.00 | -0.20 [-0.50, 0.00] | 0.10 | 0.00 | -0.10 [-0.30, 0.00] |
| Gemini 3.6 Flash | 0.00 | 0.00 | 0.00 | 0.00 [0.00, 0.00] | 0.10 | 0.10 | 0.00 [0.00, 0.00] |

## T3 considerations

| consideration invoked in the reasoning (share of all valid replies) | GPT-5.6 Terra | GPT-5.6 Terra, reasoning off | Claude Sonnet 5 | Gemini 3.6 Flash |
|---|---|---|---|---|
| disputed facts / conflicting evidence | 74% | 73% | 82% | 71% |
| credibility / cross-examination | 11% | 11% | 63% | 3% |
| trial or full hearing needed | 34% | 46% | 77% | 57% |
| fanciful / realistic distinction | 19% | 18% | 16% | 16% |
| documents / expert evidence needed | 7% | 9% | 11% | 4% |
| real prospect (the limb (a) phrase) | 76% | 75% | 70% | 99% |
| compelling reason (the limb (b) phrase) | 18% | 27% | 22% | 6% |
| mini-trial | 0% | 0% | 0% | 0% |

## T4 reliability

| model | arm | replies | valid | failure rate |
|---|---|---|---|---|
| GPT-5.6 Terra | Greek | 620 | 620 | 0.0% |
| GPT-5.6 Terra | BT via English | 310 | 310 | 0.0% |
| GPT-5.6 Terra | BT via German | 310 | 310 | 0.0% |
| GPT-5.6 Terra | English | 310 | 310 | 0.0% |
| GPT-5.6 Terra | German (plain terms) | 310 | 310 | 0.0% |
| GPT-5.6 Terra | German (English terms) | 310 | 310 | 0.0% |
| GPT-5.6 Terra, reasoning off | Greek | 620 | 620 | 0.0% |
| GPT-5.6 Terra, reasoning off | BT via English | 310 | 310 | 0.0% |
| GPT-5.6 Terra, reasoning off | BT via German | 310 | 310 | 0.0% |
| GPT-5.6 Terra, reasoning off | English | 310 | 310 | 0.0% |
| GPT-5.6 Terra, reasoning off | German (plain terms) | 310 | 310 | 0.0% |
| GPT-5.6 Terra, reasoning off | German (English terms) | 310 | 310 | 0.0% |
| Claude Sonnet 5 | Greek | 620 | 620 | 0.0% |
| Claude Sonnet 5 | BT via English | 310 | 310 | 0.0% |
| Claude Sonnet 5 | BT via German | 310 | 310 | 0.0% |
| Claude Sonnet 5 | English | 310 | 310 | 0.0% |
| Claude Sonnet 5 | German (plain terms) | 310 | 310 | 0.0% |
| Claude Sonnet 5 | German (English terms) | 310 | 310 | 0.0% |
| Gemini 3.6 Flash | Greek | 620 | 620 | 0.0% |
| Gemini 3.6 Flash | BT via English | 310 | 310 | 0.0% |
| Gemini 3.6 Flash | BT via German | 310 | 310 | 0.0% |
| Gemini 3.6 Flash | English | 310 | 310 | 0.0% |
| Gemini 3.6 Flash | German (plain terms) | 310 | 310 | 0.0% |
| Gemini 3.6 Flash | German (English terms) | 310 | 310 | 0.0% |

## T5 framing: decide (k = 31, Greek 62) against predict (k = 15, Greek 30), Greek and English arms

| model | Greek dismissals, decide | predict | agreement with court, decide | predict | F, decide | predict | L_EN, decide | predict | mean D [95% CI], decide | predict | flips to refusing in English, predict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| GPT-5.6 Terra | 100% | 100% | 0.40 | 0.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 [0.00, 0.01] | 0.02 [0.00, 0.06] | 0 |
| GPT-5.6 Terra, reasoning off | 96% | 100% | 0.40 | 0.40 | 0.00 | 0.00 | 0.00 | 0.00 | -0.04 [-0.11, 0.00] | 0.00 [0.00, 0.00] | 0 |
| Claude Sonnet 5 | 88% | 65% | 0.40 | 0.50 | 0.00 | 0.18 | 0.00 | 0.33 | -0.10 [-0.18, -0.04] | -0.31 [-0.47, -0.15] | 3 |
| Gemini 3.6 Flash | 93% | 92% | 0.50 | 0.50 | 0.00 | 0.01 | 0.00 | 0.01 | -0.01 [-0.03, 0.01] | -0.00 [-0.03, 0.03] | 0 |
