# Results: predict-1

Generated 2026-09-13T23:13:23+00:00 by scripts/analyse.py, as specified in study design v8, sections 10.4-10.7.
Prompt set: predict; arms: gr, en. Draws per arm 15, Greek 30. Cases 10. Halvings 200 (seed 20260913); bootstrap 10,000 resamples (seed 20260914); run order seed 1112880991.
Incomplete blocks (fewer valid draws than k): none.

## Headline, primary definition (modal disposal)

| configuration | F | W_en | L_EN | Δ_EN [95% CI] | Δ_DE [95% CI] | mean D [95% CI] | flips to granting / refusing | ground differs: EN / BT-en | sensitivity accuracy (baseline) |
|---|---|---|---|---|---|---|---|---|---|
| terra | 0.00 | n/a | 0.00 | n/a [n/a, n/a] | n/a [n/a, n/a] | 0.02 [0.00, 0.06] | 0 / 0 | 0.01 / n/a | 0.40 (0.40) |
| terra-off | 0.00 | n/a | 0.00 | n/a [n/a, n/a] | n/a [n/a, n/a] | 0.00 [0.00, 0.00] | 0 / 0 | 0.30 / n/a | 0.40 (0.40) |
| sonnet | 0.18 | n/a | 0.33 | n/a [n/a, n/a] | n/a [n/a, n/a] | -0.31 [-0.47, -0.15] | 0 / 3 | 0.25 / n/a | 0.50 (0.40) |
| gemini | 0.01 | n/a | 0.01 | n/a [n/a, n/a] | n/a [n/a, n/a] | -0.00 [-0.03, 0.03] | 0 / 0 | 0.00 / n/a | 0.50 (0.40) |

Every other table is in `results.xlsx`; the tab 'About' lists them. The same tables are in `csv/`.
The error-coding workbook is made separately with `scripts/error_workbook.py`.
