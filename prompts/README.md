# Prompts and rule texts

Frozen 13 September 2026, before any model was run. Fingerprints in `../FROZEN.sha256`.

Each file has a `# SYSTEM PROMPT` and a `# USER PROMPT` section. Those two headings, and the placeholders `{rule text}` and `{File A}`, are not sent to the model: at run time the placeholders are replaced by the arm's Part 24 text and by the stimulus file without its `case_id` line. Everything else is sent as it stands.

| File | Language | Used by arm(s) | How it was made |
|---|---|---|---|
| `prompt_el.md` | Greek | GR, BT-en, BT-de | The master. Translated from an English working text by a translator with no knowledge of the study's hypothesis, then reviewed and approved by the author (one wording change, to ground 5). |
| `prompt_en.md` | English | EN | Translated from the Greek master by a second translator, who was not shown the English working text. Four wording changes by the author, all to English legal idiom. |
| `prompt_de-lit.md` | German, plain terminology | DE-lit | Translated from the Greek master by a third translator, who was shown no English. No changes. |
| `prompt_de-eng.md` | German, English Part 24 terminology | DE-eng | Not translated: derived from `prompt_de-lit.md` by substituting the English Part 24 terms from `../data/glossary.csv` and repairing German agreement around each substitution. The two German files differ in nothing else. One article corrected by the author. |
| `part24_el.md` | Greek | GR, BT-en, BT-de | The official Greek text of Part 24 of the Civil Procedure Rules 2023, rules 24.1 to 24.7, as supplied by the author. Two Latin-script letters mistyped for Greek in the source were repaired. |
| `part24_en.md` | English | EN | Translated from the official Greek text by the same translator as `prompt_en.md`. Eleven wording changes by the author, all to English legislative idiom ("give judgment", "make an order", "ought to be decided at a trial"). |
| `part24_de-lit.md` | German, plain terminology | DE-lit | Translated from the official Greek text by the same translator as `prompt_de-lit.md`. No changes. |
| `part24_de-eng.md` | German, English Part 24 terminology | DE-eng | Derived from `part24_de-lit.md` in the same way as the DE-eng prompt. |

All translators were instances of one large language model, Claude Opus 5, which is not among the models tested. Each worked from a written brief and the glossary column for its arm, in a fresh context, without sight of the study design, the other arms, or any court's decision. The full production record, including every change by the author with its reason, is released with the paper.
