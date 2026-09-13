# Data

Frozen 13 September 2026, before any model was run. Fingerprints in `../FROZEN.sha256`.

## `stimuli/`

Ten Part 24 summary-judgment applications, one file per case, in six versions. Each file is the material before the court — the relief sought, the affidavit evidence and the grounds of opposition — cut immediately before the court's statement of the law. The court's reasoning and order are held privately and fingerprinted in `../FROZEN-unpublished.sha256`.

| Folder | Arm | Language | Made from |
|---|---|---|---|
| `gr/` | GR | Greek | the judgment as published, trimmed and de-identified |
| `en/` | EN | English | `gr/` |
| `bt-en/` | BT-en | Greek | `en/`, translated back without sight of `gr/` |
| `de-lit/` | DE-lit | German, plain terminology | `gr/`, without sight of `en/` |
| `de-eng/` | DE-eng | German, English Part 24 terminology | `de-lit/`, by substituting the glossary terms; nothing else differs |
| `bt-de/` | BT-de | Greek | `de-lit/`, translated back without sight of `gr/` |

The two back-translations are the rewording controls for their language arms: each carries its arm's translation drift back into Greek without the change of language.

Parties, deponents, companies, localities and other proceedings are replaced by bracketed role-naming placeholders (`[όνομα εταιρείας]`, `[name of company]`), rendered from `glossary.csv` so that each appears identically wherever it occurs in every arm. Deponent initials in affidavit labels (`ΕΔ-ΝΜ`), statute and regulation numbers, and law-report citations are kept in every arm. Each file opens with a `case_id` line and nothing else identifying.

Cases: C0990, C1026, C1099, C1195, C1292, C1316, C1387, C1423, C1460, C1621. The identifiers are opaque; the case list with the court's disposals is added after the analysis plan is frozen.

## `glossary.csv`

The placeholder and terminology glossary every translator worked from: one row per Greek string, with its English, DE-lit and DE-eng renderings. The two German columns differ only in the Part 24 vocabulary.
