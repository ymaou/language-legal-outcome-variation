# language-legal-outcome-variation

Corpus, prompts, model outputs and analysis code for an empirical study of whether input language affects LLM outcomes on Cypriot summary-judgment applications under Part 24 of the Civil Procedure Rules 2023.

Associated with a paper under submission. **Work in progress**: the corpus and results are incomplete until the submission release, and the contents of this repository may change.

## Contents

| Folder | Contents |
|---|---|
| `protocol/` | Study design, model and parameter decisions, codebook |
| `prompts/` | Prompt templates and the text of Part 24, one per language |
| `data/` | Case list; anonymised source texts and their translations |
| `raw/` | Model outputs, one JSON line per call, never edited |
| `results/` | Parsed draws, tables, coded analysis |
| `scripts/` | Run construction, runner, reply parser, pilot report; analysis to follow |

## Source material

First-instance decisions of the District Courts of Cyprus, from [CyLaw](https://www.cylaw.org), redistributed under CyLaw's terms.

## Running

```
python -m venv .venv                                   # then activate it
pip install -r requirements.txt
cp .env.example .env                                   # add API keys
python scripts/build_jobs.py --run pilot-1 --mode pilot
python scripts/run.py --run pilot-1                    # resumable; --dry-run tests without API calls
python scripts/pilot_report.py --run pilot-1
python scripts/build_jobs.py --run main-1 --mode main  # or --mode reduced: 20 draws per arm
python scripts/run.py --run main-1
```

`run.py` checks every file in `FROZEN.sha256` before calling a model and appends one line per call to `raw/<run>/raw.jsonl`. The analysis scripts are added with the analysis plan.

API models cannot be replayed bit-for-bit. Every draw is logged with its model identifier, parameters and response metadata.

## Licence

Code: MIT. Annotations, prompts, codebook, model outputs and results: CC BY 4.0. Judgment text and its translations: sourced from CyLaw and not covered by the licences above.

## Citation

See `CITATION.cff`.

## Author

Yiolanti Maou, Procedural Law Unit, University of Nicosia.
