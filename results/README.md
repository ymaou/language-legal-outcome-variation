# Results

Everything here is computed from the raw model outputs in `raw/` by the scripts in `scripts/`; nothing is
edited by hand. The court's order enters only in `analyse.py`, from a private coding sheet, and only its
case identifier, disposal, partial flag and dominant ground are read.

## Runs

| run | what | replies | draws per arm (Greek) | arms | cost (USD, list prices) |
|---|---|---|---|---|---|
| `main-1` | the main run: the model decides the application | 8,680 | 31 (62) | GR, BT-en, EN, BT-de, DE-lit, DE-eng | 62.06 |
| `predict-1` | the model predicts the court's decision (exploratory, protocol §10.12) | 1,800 | 15 (30) | GR, EN | 12.59 |
| `pilot-1` | plumbing and cost check on two cases; never analysed | 96 | 2 (2) | all six | 1.33 |

Four model configurations in every run: GPT-5.6 Terra (reasoning medium), GPT-5.6 Terra (reasoning off),
Claude Sonnet 5 (reasoning medium), Gemini 3.6 Flash (reasoning medium). No temperature, top-p or seed was
sent. The raw outputs were fingerprinted before parsing (`FROZEN-outputs.sha256`).

## What each folder holds

| path | contents | made by |
|---|---|---|
| `<run>/results.xlsx` | the pre-specified analysis: rates under every definition, contrasts, direction, stated ground, sensitivity check, per case, blocks, failures, tokens, every draw with its reasoning | `analyse.py` |
| `<run>/csv/` | the same tables as CSV | `analyse.py` |
| `<run>/report.md` | one-page summary, one headline row per configuration | `analyse.py` |
| `<run>/error_coding.xlsx` | one row per flip against the Greek modal outcome, with both File A texts, three typical reasons a side, and empty coding columns with drop-down lists (flip codes T/G/S/D/N/O, threshold codes T1–T4, ground check) | `error_workbook.py` |
| `<run>/package/` | every comparison the design allows, one tab per table in `results_package.xlsx` and as CSV: run summary; outcome distribution by model and arm; modal outcome per case for every model and arm against the court; grant share per case; inter-model agreement per arm; agreement with the court per arm (accuracy and MCC); ground distribution by model and arm; modal ground per case; reply language and reliability by arm; tokens, latency and cost; flips; rates, direction, stated ground. Four figures. | `results_package.py` |
| `main-1/paper/` | the paper's tables (`tables.md`, `paper_tables.xlsx`) and figures at proceedings text width: Figure 1 (modal outcome, 10 cases × 6 arms × 4 models, court in the margin), Figure 2 (decide against predict, Greek and English), Figure 3 (reasoning tokens by language); `T3_considerations.csv`, the keyword screen of the reasons | `paper_figures.py` |

## Reading the tables

- Outcomes are the four options of the prompt: 1 granted in full, 2 granted in part, 3 dismissed, 4 conditional
  order. Grounds are the five options: 1 real prospect of success, 2 point of law or construction of a document,
  3 other compelling reason for a trial, 4 procedural point, 5 another ground.
- The *modal outcome* of a block is the option chosen by most of its valid draws; a tie is "no clear answer".
  The *grant share* is the share of valid draws choosing option 1 or 2.
- F, W and L are the noise floor, the rewording rate and the language rate of the analysis plan
  (`protocol/analysis-plan.md`, §10.5); Δ = L − W. Intervals treat the ten cases as the sample.
- The court's order is the sensitivity check, not ground truth (analysis plan, §10.6).
- `T3_considerations.csv` and the "considerations" table in the paper are an automated keyword screen of the
  reasoning text in three languages, not hand coding.

## Regenerating

```
python scripts/analyse.py --run main-1 --court "<path to the private coding sheet>"
python scripts/error_workbook.py --run main-1
python scripts/results_package.py --run main-1
python scripts/paper_figures.py --run main-1
```

The same for `predict-1` (no `paper_figures.py`; its figure is Figure 2 of `main-1/paper/`). The coding sheet
is private because it names the cases; its fingerprint is in `FROZEN-unpublished.sha256`.
