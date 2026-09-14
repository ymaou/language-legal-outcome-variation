# Results: main-1

Generated 2026-09-13T22:42:12+00:00 by scripts/analyse.py, as specified in study design v8, sections 10.4-10.7.
Prompt set: decide; arms: gr, bt-en, bt-de, en, de-lit, de-eng. Draws per arm 31, Greek 62. Cases 10. Halvings 200 (seed 20260913); bootstrap 10,000 resamples (seed 20260914); run order seed 131036515.
Incomplete blocks (fewer valid draws than k): none.

## Headline, primary definition (modal disposal)

| configuration | F | W_en | L_EN | Δ_EN [95% CI] | Δ_DE [95% CI] | mean D [95% CI] | flips to granting / refusing | ground differs: EN / BT-en | sensitivity accuracy (baseline) |
|---|---|---|---|---|---|---|---|---|---|
| terra | 0.00 | 0.00 | 0.00 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.01] | 0 / 0 | 0.10 / 0.00 | 0.40 (0.40) |
| terra-off | 0.00 | 0.00 | 0.00 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | -0.04 [-0.11, 0.00] | 0 / 0 | 0.40 / 0.20 | 0.40 (0.40) |
| sonnet | 0.00 | 0.20 | 0.00 | -0.20 [-0.50, 0.00] | -0.10 [-0.30, 0.00] | -0.10 [-0.18, -0.04] | 0 / 0 | 0.36 / 0.11 | 0.40 (0.40) |
| gemini | 0.00 | 0.00 | 0.00 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | -0.01 [-0.03, 0.01] | 0 / 0 | 0.00 / 0.00 | 0.50 (0.40) |

Every other table is in `results.xlsx`; the tab 'About' lists them. The same tables are in `csv/`.
The error-coding workbook is made separately with `scripts/error_workbook.py`.
