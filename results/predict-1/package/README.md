# Results package: predict-1

Tables (one tab each in `results_package.xlsx`, also as CSV):

- Run summary: 19 rows
- Outcomes by model and arm: 8 rows
- Modal outcome per case: 10 rows
- Grant share per case: 10 rows
- Inter-model agreement: 12 rows
- Agreement with court by arm: 8 rows
- Grounds by model and arm: 8 rows
- Modal ground per case: 10 rows
- Reliability by arm: 8 rows
- Tokens and cost: 8 rows
- Flips against Greek: 3 rows
- Rates (all definitions): 128 rows
- Direction RQ2: 4 rows
- Stated ground RQ3: 4 rows

Figures (PDF and PNG): outcome_distribution_by_model_and_arm, ground_distribution_by_model_and_arm, inter_model_agreement_by_arm, grant_share_per_case_small_multiples.

Regenerate with `python scripts/results_package.py --run predict-1` after `python scripts/analyse.py --run predict-1 --court <coding sheet>`.
