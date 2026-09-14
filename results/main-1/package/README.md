# Results package: main-1

Tables (one tab each in `results_package.xlsx`, also as CSV):

- Run summary: 19 rows
- Outcomes by model and arm: 24 rows
- Modal outcome per case: 10 rows
- Grant share per case: 10 rows
- Inter-model agreement: 36 rows
- Agreement with court by arm: 24 rows
- Grounds by model and arm: 24 rows
- Modal ground per case: 10 rows
- Reliability by arm: 24 rows
- Tokens and cost: 24 rows
- Flips against Greek: 5 rows
- Rates (all definitions): 128 rows
- Direction RQ2: 4 rows
- Stated ground RQ3: 4 rows

Figures (PDF and PNG): outcome_distribution_by_model_and_arm, ground_distribution_by_model_and_arm, inter_model_agreement_by_arm, grant_share_per_case_small_multiples.

Regenerate with `python scripts/results_package.py --run main-1` after `python scripts/analyse.py --run main-1 --court <coding sheet>`.
