# language-legal-outcome-variation

Corpus, prompts, model outputs and analysis code for an empirical study of whether input language affects LLM outcomes on Cypriot summary-judgment applications under Part 24 of the Civil Procedure Rules 2023.

Associated with a paper under submission. **Work in progress**: the corpus and results are incomplete until the submission release, and the contents of this repository may change.

## Contents

| Folder | Contents |
|---|---|
| `protocol/` | Study design, model and parameter decisions, codebook |
| `prompts/` | Prompt templates and the text of Part 24, one per language |
| `data/` | Case list; anonymised source texts and their translations |
| `raw/` | Model outputs, one JSON line per draw, never edited |
| `results/` | Parsed draws, tables, coded analysis |
| `scripts/` | Translation checks, job construction, runner, parser, analysis |

## Source material

First-instance decisions of the District Courts of Cyprus, from [CyLaw](https://www.cylaw.org), redistributed under CyLaw's terms.

## Running

```
pip install -r requirements.txt
cp .env.example .env            # add API keys
python scripts/build_jobs.py --dry-run
python scripts/run.py           # resumable
python scripts/parse.py
python scripts/analyse.py
```

API models cannot be replayed bit-for-bit. Every draw is logged with its model identifier, parameters and response metadata.

## Licence

Code: MIT. Annotations, prompts, codebook, model outputs and results: CC BY 4.0. Judgment text and its translations: sourced from CyLaw and not covered by the licences above.

## Citation

See `CITATION.cff`.

## Author

Yiolanti Maou, Procedural Law Unit, University of Nicosia.
