# Analysis plan and protocol extract

*Extracted from the study design (v8, 13 September 2026) and published before the main run, so that the
research questions, the arms, the prompt, the models and parameters, the measures, the tests, the
interpretation of each possible outcome, the coding scheme, the error analysis, the threats and the
limitations are all on record with a timestamp before any result exists. Sections of the study design that
describe the corpus, the selection of cases and the preparation of the stimuli are held back until the
paper is out, because they carry details that would identify the anonymised cases. Section numbers are the
study design's own. Internal file references (`methodology/...`, `10 cases/...`) point to the private
working record, which is released with the paper.*

## 1. Research questions

**RQ1, invariance.** For a fixed case and model, does the majority disposal change between Greek and English more often than it changes between Greek and its back-translation? The question is paired by case and needs no gold label.

**RQ2, direction.** Where the disposal changes, does it move systematically towards granting or towards refusing? Random flips are an unreliability finding; a systematic shift is an equal-treatment finding.

**RQ3, stated ground.** Where the disposal holds, does the model's stated ground change across languages more often than across the back-translation?

**Precondition, sensitivity.** Does the Greek majority disposal agree with the court's order above the majority-class baseline? If it does not, the models are not responding to the cases, RQ1 cannot be interpreted, and the paper says so.

**Secondary contrasts, tier 2.** German against Greek, to separate an English-specific shift from a shift away from Greek; German-literal against German-with-English-vocabulary, to ask whether the Part 24 vocabulary alone moves the disposal inside one language; each German arm against its own back-translation.

**Out of scope.** A rule-withheld condition (mechanism; a later study); equivalence claims, which n does not support; the model's reasoning as distinct from its stated ground; interpretive guidance on the rule.

*Sources.* `study-design-v5_YM.md` §1, retained; `NOTES.md` §1 and `methodology/translation.md` §1 for the matched back-translation and the tier-2 contrasts.

---

## 6. The arms

*Full record: `methodology/translation.md`; the decision to run two back-translations at `NOTES.md` §1.*

| Arm | Text | Made from | Tier | Prompt and rule text |
|---|---|---|---|---|
| GR | Greek original File A | the split | 1 | Greek |
| EN | English | GR | 1 | English |
| BT-en | Greek back-translation | the final EN | 1 | Greek |
| DE-lit | German, descriptive Part 24 vocabulary | GR | 2 | German (DE-lit) |
| DE-eng | German, English Part 24 vocabulary | derived from DE-lit | 2 | German (DE-eng) |
| BT-de | Greek back-translation | the final DE-lit | 2 | Greek |

**Why a back-translation.** Translating into English changes the language and rewords the text at once. The back-translation is Greek text that has been through the same pipeline and back, so it carries the rewording without the change of language; the estimand is the English flip rate net of the back-translation flip rate. It is a *matched* control, made from the very English file the EN arm uses, not a generic paraphrase; Choi 2025's 2,000 paraphrases per item (L565–599) give a distribution this design cannot, and the paraphrase arm is named as the 2027 extension (`NOTES.md` §1). Gazal Ayal et al name, as their own limitation, the gap the arm fills: consistency under repetition is not robustness to rewording. Each back-translation has passed through two translation steps where its language arm passed through one, so the rewording rate is expected to overstate the drift and the estimand is conservative; the paper says so (`translation.md` §1, L36–39).

**Why two German arms.** DE-lit renders the Part 24 vocabulary descriptively (*summarisches Urteil*, *realistische Erfolgsaussicht*); DE-eng carries the English CPR terms into German text (*Summary Judgment*, *real prospect of success*). Everything else is the same text, so the diff between the two files is the whole treatment, and a reader can inspect it. If DE-eng sits closer to EN than DE-lit does, the vocabulary carries the shift (§1, L52–66). This is the design's answer to the doctrinal-home confound of §2, alongside error code D. At n = 10 it is descriptive and secondary.

### 6.1 What each arm receives, and what each comparison changes

**The matching rule.** Each arm is run with the prompt and the rule text of its own language, and nothing in any arm is in another language. The three Greek-text arms share one Greek prompt and one Greek rule text; the two German arms differ in prompt and rule text exactly as they differ in File A, in the Part 24 vocabulary and nothing else.

| Arm | File A (`10 cases/`) | Prompt (`prompts/`) | Rule text (`prompts/rule text/`) | Draws per case |
|---|---|---|---|---|
| GR | `3 stimulus/` | `prompt_el.md` | `part24_el_official.md` | 62 |
| BT-en | `7 stimulus BT en/` | `prompt_el.md` | `part24_el_official.md` | 31 |
| BT-de | `10 stimulus BT de/` | `prompt_el.md` | `part24_el_official.md` | 31 |
| EN | `6 stimulus EN/` | `prompt_en.md` | `part24_en.md` | 31 |
| DE-lit | `8 stimulus DE lit/` | `prompt_de-lit.md` | `part24_de-lit.md` | 31 |
| DE-eng | `9 stimulus DE eng/` | `prompt_de-eng.md` | `part24_de-eng.md` | 31 |

One case, one model: 217 calls. Ten cases: 2,170 per model. Every call is a single turn: system prompt; user prompt holding the rule text, File A with its `case_id` line removed, and the restated output instruction (§9.2).

**What each comparison holds constant and what it changes.** The design's logic is in this table; every rate in §10.5 is a row of it.

| Comparison | Language of File A | Language of prompt and rule | Wording of File A | What the rate measures |
|---|---|---|---|---|
| GR half against GR half | same | same | same | sampling noise, F |
| GR against BT-en | same | same | reworded via English | rewording, W_en |
| GR against BT-de | same | same | reworded via German | rewording, W_de |
| GR against EN | changed | changed | reworded once | language, L_EN (net of W_en is Δ_EN) |
| GR against DE-lit | changed | changed | reworded once | language, L_DE (net of W_de is Δ_DE) |
| DE-lit against DE-eng | same | same, apart from the Part 24 terms | Part 24 terms only | the vocabulary contrast |
| EN against BT-en | changed | changed | one further step | secondary: a language contrast with one translation step between texts, as GR against EN |
| DE-lit against BT-de | changed | changed | one further step | secondary, the German analogue |

Two things follow. The rewording controls (rows 2 and 3) hold the prompt fixed as well as the language, so they isolate wording alone. The language contrasts (rows 4 and 5) change the prompt with the input, which is the treatment as a real user experiences it and is stated as such (§9.1). The vocabulary contrast (row 6) is the only comparison in which the prompt and rule text differ between arms by design, and they differ in the same terms as File A, so the substituted vocabulary is the whole difference across all three components.

---

## 9. The prompt

*Full record: `methodology/prompting.md` D-P1 to D-P6 and §2A; the literature behind each at `literature review/prompting-literature-review.md`; files at `prompts/`.*

### 9.1 One prompt, in each arm's language

One frozen prompt is used for the main run, identical in content across arms and reported in full. Prompt wording moves legal answers (Choi 2025 L633–657; Engel & McAdams L2854–2857), so a reworded prompt is run after the main run if time allows, as a robustness check, never as a condition of it; each variant would have to be translated into every arm, and each translation is itself the rewording the back-translation arms measure (D-P1).

**Each arm is prompted wholly in its own language.** This is the convention of the two closest studies (Engel 2024 L141–146, L170–172; Wang & Suresh L257–259). A user working in Greek writes the instructions in Greek; English instructions over Greek material would test an input no Greek-language user produces (D-P3). Consequences stated: Greek against either back-translation shares one Greek prompt, so the rewording control is clean; Greek against English changes the prompt language as well as the input language, which is part of the treatment, as it is for a real user.

**The Greek prompt is the master.** The prompt was drafted in English as a working text, translated into Greek by a blind agent, approved by the author with one edit, and frozen; the English and German prompts were then translated *from* the Greek master by fresh agents, DE-eng derived from DE-lit. Every element of every arm therefore has the same history, Greek source translated outwards, and the Greek arms carry no translated text at all; an English master would have given the English arm the only untranslated prompt and put English in front of the German agent that P9 keeps English-blind (D-P3, amendment). The production log records every step, agent, input and check (§2A).

### 9.2 Content

**Role and task.** "You are a judge of a District Court in Cyprus. Your task is to decide an application under Part 24 of the Civil Procedure Rules 2023." The first sentence follows Gazal Ayal et al's system prompt ("You are a judge in a criminal proceeding in Israel", L542–543); the second follows Posner & Saran's task statement (L551–555). Cyprus and Part 24 are named in every arm because, when no jurisdiction is named, input language acts as a proxy for one (Wang & Suresh L632–636); naming both holds the forum and the law constant so that what remains is a different answer from a model told the law and the forum. The model *decides*; it is not asked to predict, because a predictive framing invites base rates (Posner & Saran L1066–1100) and a should/will split (Stillwell & Harrington L245–249). The judicial role pulls a model towards applying the formal rule (Posner & Saran L1446–1447); for a threshold test that is the task (D-P2).

**System and user parts.** The system prompt carries what is fixed for every call: role, task, the complete-record instruction, the answer options and the output schema. The user prompt carries the rule text, then File A without its `case_id` line, then the output instruction restated, because instructions placed before a long document may be lost by the time the model answers (Choi 2023 L574–586, L599–600) and File A runs to 25,628 characters (D-P5). The pattern follows Posner & Saran (L555–566), Gazal Ayal et al (L542–557) and Engel 2024 (L141–146).

**Zero-shot.** No examples. Examples anchored outputs in opposite directions across models (Gazal Ayal et al L648–655), were "unreliable" for outcome prediction and made five of seven models worse on legal text through demonstration anchoring (Ovcharov, Multi-Legal-Bench L417–420; Tokenizer Tax L575–590, whose first recommendation is to default to zero-shot for morphologically rich languages, L729–731), and slightly worsened a legal classification (Choi 2023 L603–608). No paper in the library tests whether examples narrow a language gap; the nearest evidence finds the few-shot effect the same across languages. Each example here would be a whole File A, would need translating into every arm, and would be drawn from the ten cases under test (D-P6).

### 9.3 Output

A JSON object with three fields in this order: the **reasoning**, at most five sentences; the **disposal**, one of four options numbered 1 to 4; the **ground**, one of five numbered 1 to 5.

**Disposal options**, framed from the side of the application so that C1099 reads correctly: 1 granted in full; 2 granted in part (as to part of the claim, or as to one or more issues, and dismissed as to the rest, r 24.1(1)); 3 dismissed; 4 conditional order under r 24.6(2). The conditional order is offered although no case in the ten ended in one, because the model reads r 24.6 and might judge that order correct; an answer set narrower than the rule invites a forced choice (Ovcharov L331–334) (D-P4).

**Grounds**, taken from the text of Part 24 and nowhere else: 1 whether the respondent has a real prospect of success (r 24.2(1)(α)); 2 a point of law or the construction of a document (r 24.4(2)(α)); 3 whether there is some other compelling reason why the case or issue should be decided at a trial (r 24.2(1)(β)); 4 a procedural point; 5 another ground, stated in the reasoning. The finer *Easyair* categories of the codebook (disputed facts, evidence not yet available, complexity) are not offered, because offering them tells the model what counts as a reason for trial, which §8 excludes, and because "a conflict of evidence that cannot be resolved without a trial" would hand the model threshold code T4 (D-P4, amendment). The ground is defined for the model by the codebook's test: the reason which, if removed, would change the decision (`coding-decisions.md` L372–373). The full list is shown whatever disposal is chosen; a mismatch is data, not something the prompt prevents.

**Reasoning first.** Reasons written after a committed answer rationalise it (Peng et al L121–133; Tapwal et al L105–109); Stillwell & Harrington required the analysis before the prediction (L249–254). Reasoning models reason internally before any visible field (Raina et al L414–429), so the visible reason is still not read as the cause of the decision. Its cap is in sentences, not words, because Greek costs about 3.1 tokens per word against 1.2 for English (Ovcharov, Tokenizer Tax, abstract) and a word limit would vary by language (D-P4).

**Labels and field names.** Disposals and grounds are digits, identical in every language, so the parsed token is the same in every arm and no Latin script enters the Greek or German prompt. The field names are translated with the rest of the prompt (`αιτιολογία / κατάληξη / λόγος`; `reasoning / outcome / ground`; `Begründung / Ergebnis / Grund`), tested in the pilot, with neutral keys `r`/`d`/`g` as the recorded fallback if they do not parse reliably (D-P4; `run-parameters.md` R-6). No provider's structured-output (schema) mode is used: it works differently at each provider and constrains how the model writes, so every model receives the same plain JSON instruction and every reply is parsed and validated on receipt (author's decision, 13 September 2026).

---

## 10. Models, run parameters and measures

*Full record: `methodology/run-parameters.md` R-1 to R-8.*

### 10.1 Models

Tier 1, run on every arm: GPT-5.6 Terra, Claude Sonnet 5 and Gemini 3.6 Flash (GA), three mid-tier 2026 releases from three providers, identifiers pinned to dated snapshots **[verify]**. Between-model disagreement is itself a source of variation worth exposing (Choi 2025 L1263–1264). Sonnet 5 shares a provider lineage with the translation engine. v7 stated that this cannot produce a within-model language effect; that overstates it. Every arm except the Greek original is text written by a Claude model, and language models have been shown to recognise and favour their own generations over text written by humans and by other models (Panickssery, Bowman & Feng 2024, arXiv 2404.13076, abstract read, not in the library; shown for models acting as evaluators, not as decision-makers, so how far it reaches here is open). A familiarity effect would therefore run in the direction of the language contrast for Sonnet alone. The back-translation arms are Claude-written as well, so the rewording rate absorbs part of it, but it cannot be assumed to cancel, because the English arm is Claude-written English and the back-translation Claude-written Greek. Sonnet 5 stays in tier 1 by the author's decision; the check is pre-specified at §10.11, Stage 5, and the limitation is §14 item 24 (R-1). **A fourth configuration, reasoning off.** GPT-5.6 Terra is also run on every arm with reasoning effort `none`, which the provider documents as supported (OpenAI model page for `gpt-5.6-terra`, consulted 13 September 2026). It answers one question: whether the models' language behaviour depends on hidden reasoning (§10.2; §10.11, Stage 3). **No open model.** Llama-Krikri-8B-Instruct, the tier-2 contrast in v7, is dropped by the author's decision of 13 September 2026: it would have needed paid hosting within a fixed budget, and it was a labelled contrast rather than a peer of the tier-1 models. The largest input in any arm is about 15,000 tokens; every model's window exceeds it many times over.

### 10.2 Sampling and reasoning

Provider-default temperature, not set, because it cannot be set uniformly across providers **[verify]**, because the noise floor needs a non-zero setting to be a sample at all (Engel 2024 L95–98; Human Realignment L499–523), because temperature 0 does not buy determinism (Blair-Stanek & Van Durme L204–212; Cohen-Sasson L1628–1642), and because the default is the deployment setting. The split-half floor is reported as sampling noise under the stated setting, not as the model's uncertainty (Choi 2025 L327–349). With 2026 models the floor may be near zero (Engel 2024 L100–107 on newer models reducing variance); that is a result. Reasoning at the middle tier, `medium`, on every model, fixed and reported, with hidden reasoning treated as scratchpad and not data (Raina et al L248, L414–429). Medium is the provider default for Terra and Gemini; Sonnet 5's default is `high` (Anthropic API reference, consulted 13 September 2026), so Sonnet is set to `medium` explicitly, which keeps the three models at the same nominal tier (author's decision, 13 September 2026); the three controls are not one scale (R-2, R-3). **Hidden reasoning may run in English.** Large reasoning models tend to reason in English, or another high-resource language, whatever the language of the input (Tam et al 2025, arXiv 2505.17407; Saji et al 2025, arXiv 2510.20647; abstracts read, neither paper in the library, and neither tests legal tasks). Neither OpenAI nor Google returns the raw reasoning (provider documentation consulted 13 September 2026), so the language in which a closed model reasons cannot be observed here. The design responds in three ways: the Terra reasoning-off configuration (§10.1); reasoning-token counts logged for every call and reported per arm and model, so that a model reasoning at markedly different length by language is visible; and a reading of invariance, fixed in advance, that names this mechanism (§10.11, Stage 3).

### 10.3 Draws

k = 31 independent single calls per arm per case per model; Greek 62, split at random into two halves of 31, over repeated splits. The request-level multiple-completion parameter is never used, so the sampling procedure is identical across providers. No seed is sent to any model. This follows the language-variance studies in the library, which draw repeated answers as independent calls without a seed: Engel 2024 treats each run as an "independent identical observation" (n 6, L126–129), and Ioannou et al use 25 and 30 independent runs (L1149, L1183). It also keeps the sampling procedure identical across providers, since only OpenAI accepts a seed. Posner & Saran's use of the same seeds in every condition (2026 L574–578) suits a one-model design with no noise floor and no rewording control, and is not followed here. Per model: 217 calls per case, 2,170 in all; the literature runs 20 to 100 per condition (Blair-Stanek 20; Posner & Saran 25; Gazal Ayal 30; Engel 100). Failures (truncated, unparseable, refused, wrong language) are recorded with raw text, never silently retried, replaced until the arm has k valid responses, and their rate reported per arm and model, following Kneer & Baumgartner's structural validation (L175–178) and Engel & McAdams's oversampling (L1083–1086); a failure rate that differs by language is a finding (R-4, R-5). **Output cap.** The maximum output length is set high enough that truncation is negligible, at least 32,000 tokens, because reasoning tokens count against the cap on at least two of the providers **[verify]** and Greek costs more tokens: a low cap would truncate Greek answers more often, and replacing them would over-represent shorter deliberations in the Greek arms. For the same reason the replacement rule is itself checked: the disposal rates are also reported with failed draws counted as a category of their own rather than replaced (§14 item 34). **The reasoning-off configuration** takes the same k and the same failure rules: a further 2,170 calls. **Budget, and the one permitted reduction.** The run is budgeted at €100, with a ceiling of €150, both fixed before the pilot. The pilot measures the tokens per call for every model and arm, and the full run is projected from them before it starts. If the projection at k = 31 (Greek 62) is within €100, that is run. If not, k is reduced to 25 in every arm (Greek 50), never in some arms only, because a smaller set of draws flips more often by chance and unequal counts would read as a difference between arms; 25 is the count of Posner & Saran (2026) and the lower end of Ioannou et al's 25–30. If the projection at k = 25 still exceeds €100, the run proceeds up to the €150 ceiling; if it exceeds €150, the run does not start and the author decides. *Recorded after the pilot, 13 September 2026, before the protocol freeze.* The pilot (96 calls, all replies valid, $1.33) projected $52 for the full run at k = 25 and $64 at k = 31. The author raised k from 25 to 31 (Greek 50 to 62) on that projection, a modest increase within the budget; 31 rather than 30 keeps k odd, so that two options cannot tie exactly. 25 becomes the fallback. No other parameter changed. No other reduction (fewer models, arms or cases, or lower reasoning) is made to meet the budget. A spending limit is set on each provider account before the pilot.

### 10.4 The unit of analysis and the outcome

For case *i*, model *m* and arm *a*, each valid draw yields a disposal on the four options. **The modal disposal** is the option chosen by the most draws. Where two or more options tie for most, the modal disposal is recorded as *no clear answer*, a value of its own: two sets of draws that are both *no clear answer* are not a flip, and *no clear answer* against any option is. **A flip is any change of modal disposal between two sets of draws.** Throughout this document, "majority disposal" and "majority" mean the modal disposal defined here. The strict majority (an option held by more than half the draws, otherwise no majority) is reported alongside as a secondary definition. *Why changed from v7.* With four options, no option need exceed half the draws even without a tie (11 granted in full, 10 in part, 4 dismissed), and v7 counted that as a flip against any arm, including against an identical half. The cases were selected as marginal and include partial grants, so that pattern is expected, and it would have inflated F, W and L alike. The court's order maps onto the same options: judgment on the claim in full, or the claim dismissed on a defendant's application, to 1; a partial order to 2; dismissal of the application to 3; a conditional order to 4. The binary collapse, any relief (1 or 2) against none (3 or 4), is reported as secondary. This adopts the case-selection decision that the effect is most likely to appear as a shift in *how much* relief, which a binary primary would round away (`case-selection-criteria.md` §7A), and supersedes v5 §8's binary primary.

### 10.5 Rates and the estimand

All comparisons are 31 draws against 31 (25 against 25 if the budget rule of §10.3 applies).

- **F, the noise floor:** the share of case-model pairs whose majority differs between the two Greek halves, averaged over 200 random splits.
- **W, the rewording rate:** the share whose majority differs between a Greek half and BT-en, averaged over both halves.
- **L_EN, the language rate:** the same between a Greek half and EN.
- **Estimand, RQ1:** Δ = L_EN − W, per model; L_EN − F alongside.
- **The German analogue, tier 2:** W_de, a Greek half against BT-de; L_DE, a Greek half against DE-lit; Δ_DE = L_DE − W_de.
- **Secondary contrasts:** EN against BT-en (one translation step between the texts, as GR against EN; if both language contrasts flip and GR against BT-en does not, language is doing the work); DE-lit against BT-de, the German analogue; DE-lit against DE-eng, the vocabulary contrast (§6.1).
- **Direction, RQ2:** per case, the grant share (options 1 and 2) in EN minus the grant share across all 62 Greek draws; the mean, and the counts of flips in each direction.
- **Stated ground, RQ3:** among case-model pairs whose majority disposal is the same in a Greek half and EN, the share whose majority ground differs, against the same share for a Greek half and BT-en; a tied ground counts as a mismatch.
- **Descriptive:** mean majority share per arm and model; per-case results in full, which the draws make reliable.

**Five clarifications, fixed by the author on 13 September 2026 before the run, and implemented in `scripts/analyse.py` and `scripts/measures.py`.**

1. *Which draws count.* A block's draws in analysis are its first k valid replies in draw order; replacement draws beyond k are not used. Engel 2024 uses "the first 100 usable responses" of 110 requested, each run being an independent observation (n 6, L126–129).
2. *The halvings.* The 200 random halvings of the Greek draws are generated once from a recorded seed and the same 200 are used for every case and every model configuration, so every comparison is reproducible and on the same footing.
3. *Ties in RQ3.* A disposal "holds" only where the Greek half and the arm both have a clear modal option and it is the same. A tie on either side is not a settled disposal and is excluded from RQ3; the number excluded is reported. The modal label follows Ioannou et al's majority vote across runs (L246, L1184).
4. *Direction of a flip.* Read from D, the grant share (options 1 and 2) in EN minus the grant share across all the Greek draws, as defined above: above zero towards granting, below zero towards refusing, zero recorded as a flip with unchanged grant share. Direction and the tests of §10.7, which run on D, therefore agree by construction.
5. *Aggregation and intervals.* Each rate is averaged within a case over the halvings, then across cases; every interval treats the cases, not the draws, as the sample, following Choi 2025's bootstrap "resampling questions rather than retraining models" (L1038–1047) and his warning that an interval over draws shrinks towards zero as draws grow and is not a confidence interval for anything (L670–671). The intervals are wide at n = 10 and are reported as such.

### 10.6 The sensitivity check

Agreement between the 62-draw Greek majority and the court's order on the four options, n = 10, majority-class baseline 40%; reported as accuracy and MCC against the baseline (Ovcharov's rule that a cell at or below the majority baseline tells almost nothing; Mumford's warning that respectable accuracy can hide MCC 0). Also reported on the binary collapse (baseline 60%). Raina et al's point governs its use: accuracy is not a proxy for reasoning quality (L5–28), and the court's order is not treated as the right answer.

### 10.7 Statistics

Ten cases bound everything across cases; the draws bound nothing across cases. The paper therefore **estimates and bounds**: paired bootstrap over cases (10,000 resamples) for Δ and for the mean direction; Wilson intervals on flip rates; an exact sign test on flip direction with a Wilcoxon signed-rank test on the per-case direction as secondary. At n = 10 a flip-rate interval is roughly ±0.3, and the power limit is stated up front; no equivalence is claimed, and a null is reported as unresolved with its interval, not as an absence. The RQs, measures, tests and the interpretation map of §10.11 are committed to the public repository with a timestamp before the main run; the paper says "specified before data collection", not "pre-registered". Judge clustering (four of ten by one judge) cannot be modelled and is stated.

### 10.8 Contamination

The judgments are on CyLaw and may be in training data. Memorisation can help only the Greek original, so it is a confound specific to the language comparison; a memorised outcome is memorised in both languages only where the model recognises the case from its facts. Two responses. (i) Names, numbers, dates and courts are removed from File A (§5.2), so a model cannot retrieve a case from what it is given. (ii) Cases that post-date each model's stated cutoff are reported separately; C1460 and C1621 post-date the Terra cutoff of 16 February 2026 **[verify all cutoffs]**. The strongest argument is structural: a memorised outcome cannot generate a Greek/English gap unless recognition itself is language-dependent (`design-open-questions.md` B8). **The caption probe of v5 §10 is not run** (author's decision, 13 September 2026). Once the stimuli had been de-identified first, the probe could no longer gate anything; it would have measured recall from captions the models never see. The paper states that memorisation was bounded by de-identification and the post-cutoff subset, not tested directly, and lists this as a limitation (§14 item 31).

### 10.9 Run discipline and logging

One continuous session, the three providers run in parallel, with normal rather than batch processing so that the run completes in hours. The unit of order is the block (one case, in one arm, on one model configuration): blocks run in a random order under a recorded seed, so that provider drift cannot align with a language, and the draws within a block are sent together, so that the providers' discount on repeated input applies. v7 interleaved single draws, which spreads identical prompts apart in time and forfeits most of that discount (author's decision, 13 September 2026). The prompt is identical across draws within an arm; Gemini search grounding off **[verify how]**; top_p and penalties untouched. Per call, one JSONL line, never edited: job, case, arm, model and snapshot, every parameter, seed, timestamp, response ID, fingerprint, token counts, raw text, parse status, replacement flag. A manifest records the SHA-256 of every prompt and rule-text file, model identifiers, defaults in force, the interleaving seed and the date. Reproducibility for API models rests on auditability, not replay, and the paper follows Waldon et al's documentation list (L2466–2489) and states Blair-Stanek's limitation on proprietary models (L430–435) (R-7, R-8). The seal: nothing that talks to a model reads File B or the court's order; the order is joined only downstream of every call (`methodology/PIPELINE.md`, "The seal", the one part of that file that survives).

### 10.10 The pilot

Before the main run: two cases (the shortest and longest File A), all six arms, all tier-1 models and the Terra reasoning-off configuration, k = 2 (reduced from 3 by the author on 13 September 2026, to save cost; two draws per block suffice to check parsing, reply language, truncation and the caching discount), about 96 calls, to check that each model returns parseable JSON with the translated field names, answers in the arm's language, and is not truncated, and to measure the tokens, cost and time per call from which the full run is projected under the budget rule (§10.3). The prompts and rule texts were frozen and published on 13 September 2026 (`methodology/freeze-log.md`, freeze 1; public repository commit 2041818), so the one change the pilot may produce is the fallback recorded at D-P4: if a model mishandles the translated JSON field names, every arm switches to the neutral keys `r`, `d`, `g`. If used, it is a new prompt version with its own fingerprints, logged in the freeze log and in `prompting.md` §2A, and the frozen versions stay in the record. No other change to wording, format, options, grounds or rule text. The two pilot cases are test cases, so the pilot report shows parse status, reply language, truncation and token counts only, and does not display their disposals or grounds. Pilot draws are not counted (`run-parameters.md` §4). The four pilot cases of v5 §7 were never prepared and are not used.

### 10.11 Pre-specified interpretation of outcomes

*Written before the run and frozen with the protocol. The purpose is Engel 2024's: to name the rival readings of each result in advance (his §§5–6 walk "a difference in law" and "a difference in societal attitudes" as competing accounts of the same figure, L230–314), so that the paper's reading is chosen before the numbers exist rather than fitted to them. Each entry states the pattern, what it would mean, what it would not mean, and which secondary measure discriminates. Nothing here is a prediction; the study does not have a directional hypothesis.*

#### Stage 0. The precondition

**Greek majority disposal at or below the 40% baseline.** The models are not responding to the cases. RQ1 is uninterpretable and the paper says so. Two readings, both to be checked: File A is too thin to decide on (the interleaving confound, §5.1; the discordance pilot's Q1), or the task as posed is unanswerable. Blair-Stanek found leading models only slightly above 50% against the court on two-party questions and agreeing with each other far more than with the court (L368–395); inter-model agreement well above court agreement is reported here as evidence of shared training rather than of the cases.

**Greek majority disposal well above baseline.** The precondition is met; proceed. **At or near 100%** is not good news on its own: Engel, Hermstrüwer & Kruse attributed near-75% zero-context accuracy on ECtHR cases to training data (L1194–1204). The post-cutoff subset (§10.8) is read before any accuracy is claimed.

#### Stage 1. The floor, F

**F near zero.** Repeated draws of the same Greek text return the same majority. Consistent with Engel 2024's observation that newer models reduce variance at temperature 1 (L100–107) and with Gazal Ayal's finding of near-zero dispersion across strategies (L646–655). It means any W or L above zero is signal, and that the majority statistic is close to the model's fixed answer. It does not mean the model is reliable in any deeper sense (Choi 2025 L362–366: greedy-like consistency is a decoding property).

**F substantial (above about 0.2).** Instability of the Blair-Stanek kind, which they found on 10 to 50% of questions depending on model, with instability largely model-specific (L241–248, L280–293). W and L are then read only relative to F; a small Δ is unresolvable and is reported as such. Per-model F is reported, because Blair-Stanek's low inter-model correlation predicts it will differ.

#### Stage 2. Rewording, W

**W ≈ F.** The model is insensitive to the rewording a translation round trip introduces. Any excess of L over W is then attributable to language.

**W well above F.** Rewording alone moves the disposal. This is Choi 2025's finding transposed from prompt phrasing to the case text (two rephrasings, 14.8% and 73.1%, L633–657), and Grimmelmann's brittleness (L307–308). Δ remains separable, but the paper foregrounds W as a finding in its own right: a translation of a filing, with no change of language, changes the answer, which bears on deployment as directly as the language result. The route difference already measured on the texts (§7.3) predicts W_en < W_de; if the disposals show the same ordering, the text-similarity measure is validated as a proxy for rewording; if not, that is reported.

#### Stage 3. The estimand, Δ_EN = L_EN − W_en

**Δ ≈ 0 with L ≈ F.** Invariance in this setting: with the case, the rule and the forum held constant, the language of presentation does not change the answer, within the interval n = 10 allows. Two readings are stated together. The first is the Posner & Saran reading: the models apply the formal rule and disregard a legally irrelevant variable, as GPT disregarded sympathy (L432–435). The second is the Wang & Suresh reading: language moves answers by selecting a jurisdiction, and naming the jurisdiction switches the mechanism off (L632–636, L718–719), which is why Engel 2024, who named none, saw large effects. The third is the internal-pivot reading: a reasoning model that translates into English before it reasons would give the same answer in both languages without having reasoned about the Greek text as Greek (§10.2). It is read from the Terra reasoning-off configuration. If Terra with reasoning off shows a language effect that Terra at its default does not, the invariance depends on hidden reasoning and is reported as such; if both are invariant, the pivot is not what produces it. What is not claimed: equivalence; the interval is stated and only a large Δ was ever resolvable (§10.7).

**Δ ≈ 0 with L and W both well above F.** The flips are rewording, not language. This is a methodological result: what single-prompt designs read as a language effect may be wording. It supports Choi 2025 and Grimmelmann against Engel 2024's design, and it is reported as the study's main contribution if it occurs.

**Δ clearly positive (L > W > F).** Language changes the answer beyond rewording. The mechanism is then read from four secondary measures, in this order.

1. *The German pair.* If Δ_DE resembles Δ_EN, the shift is away from Greek rather than towards English: consistent with Ioannou's gradient of performance and stability with syntactic similarity to English (L1796–1798, L2025–2030) and with Greek's tokenizer cost (Ovcharov, Tokenizer Tax). If Δ_DE ≈ 0 while Δ_EN > 0, the shift is English-specific. If DE-eng sits closer to EN than DE-lit does, the Part 24 vocabulary carries the shift: the English term triggers the English doctrine (§2), which is the reading `design-open-questions.md` A2(c) required to be pre-registered, and it is. If DE-lit and DE-eng agree, the vocabulary does not carry it. Caveat stated in advance: the German text is less idiomatic by design (§7.3) and the modal force of limb (b) differs between the English and German material (§14, item 17).
2. *Direction, RQ2.* A systematic shift, towards granting or towards refusing, is an equal-treatment finding: the same application fares differently by the language it is presented in. Random flips are an unreliability finding. Both are reportable; they mean different things for deployment.
3. *The error codes on each flip, §12.* T dominant: translation quality, not language; the finding is about the translation step, and the targeted verification says so. S dominant (same ground, threshold applied differently), with T1 and T4: the real-prospect standard is applied differently by language, the study's most specific result. G dominant: a different ground on the same facts, read with RQ3. D present: English authorities or concepts in the English reasons absent from the Greek, the doctrinal-home account made visible.
4. *Overlap across models.* If the same cases flip for all three models, the flip is a property of the case (the marginal cases the filter selected); if flips are model-specific with little overlap, as Blair-Stanek's instability was (L270–293), the "language effect" is a model property and is reported per model, not as a general finding.

**Δ negative (W > L).** The back-translation flips more than the English. Expected in part, because the back-translation has passed through two steps and its Greek is the less idiomatic text (§6). Read as no evidence of a language effect, with the EN-against-BT-en contrast (§6.1, row 7) reported: if that contrast also shows little, wording and language are both weak here.

#### Stage 4. The stated ground, RQ3

**Ground changes while the disposal holds.** The route to the answer depends on language even where the answer does not. For a decision aid this matters as much as the disposal (Raina et al: accuracy is not reasoning quality, L5–28). Before it is reported the hand check of §12 confirms that the model's chosen ground matches its reasoning; where it does not, the automatic RQ3 figure is set aside for that pair and the coder's reading is used.

**Limb (b) by language (threshold code T2).** If limb (b) is addressed at markedly different rates across languages, the two-limb test is being applied as a different test by language. Between English and German this cannot be separated from the modal difference in the material (§14, item 17); between Greek and English it can.

#### Stage 5. Contamination and the translator's lineage

**Contamination.** No probe is run (§10.8). If the Greek arm's agreement with the court differs markedly between the post-cutoff cases (C1460, C1621 for Terra) and the rest, memorisation is a candidate explanation and is stated; otherwise the structural argument stands that a memorised outcome cannot produce a language gap unless recognition itself is language-dependent.

**Sonnet 5 and the translator's lineage.** Every arm except the Greek original was written by a Claude model (§10.1). If Sonnet 5 alone shows a W or a Δ markedly different from the other two tier-1 models, in either direction, the lineage is a candidate explanation, and Sonnet's language result is reported on its own with that caveat attached. If Sonnet's W and Δ sit with the other models, there is no sign of a lineage effect; that does not exclude one.

#### Stage 6. Failure rates

Parse failures, refusals and wrong-language replies that differ by arm are reported as a deployment finding in their own right, whatever the disposals show (Ioannou et al report a model answering in the wrong language despite instruction, L1068–1070).

#### What the paper will not claim, in any outcome

Equivalence between languages; a causal mechanism established at n = 10; generalisation beyond Part 24 applications and beyond the three models on the run date; that the court's order is the correct answer; that hidden reasoning was measured.

---

## 11. Blind coding of the court's order

The court's disposal and ground are coded from File B by the author, into a sealed sheet, using the r 24.6(1) orders and the eight-value ground taxonomy derived from the corpus (`coding-decisions.md` §4; `HOW-TO-CODE.md`). The taxonomy was rebuilt after the first version, carried from Order 18 vocabulary, failed a check against the corpus (quantum language in 4 of 64); every value traces to the rule, to a named English authority these courts adopt, or to a precedent in the literature (Ribeiro de Faria et al for `procedural`), with a dominant ground plus one optional secondary (§4.2). For comparison with the model's five options, the codebook's grounds map: `no_real_prospect`, `disputed_facts`, `evidence_not_investigated` to 1; `law_point` to 2; `limb_b` to 3; `procedural` to 4; `complex_case` to 1 or 3 case by case (`prompting.md` D-P4, amendment). The coding for the ten was completed by the author on 12 September 2026 in `data/outcome-coding_against actual court decision.xlsx`: all ten cases coded, every value within the sheet's codebook, and no case coded `complex_case`, so no case-by-case mapping is needed. It was fingerprinted on 13 September 2026, before any model was run, and the fingerprint is published in the repository's `FROZEN-unpublished.sha256` (`methodology/freeze-log.md`, freeze 1, addition). The sheet is read-only and nothing that talks to a model reads it.

---

## 12. Error analysis

**Unit.** A robust flip: a case-model pair whose majority disposal in an arm differs from the 62-draw Greek majority. Expected volume across three models and five non-Greek arms: tens of pairs at most.

**Material.** The Greek and the arm's File A side by side; the reasons of three majority draws in each arm. This reading is also the targeted human verification of the English arm (§7.3).

**Three instruments, one reading per flip, single coder.**

1. *Flip codes* (v5 §11): T, the translation changes or drops a legally material fact; G, the same facts, a different ground; S, the same ground, the "real prospect" threshold applied differently; D, the arm's reasons invoke English authorities or concepts absent from the Greek; N, noise, a majority share below 0.60 in either arm; O, other, with a note. One primary code, at most one secondary.
2. *Threshold codes* T1 to T4 (`methodology/threshold-codes.md`), derived from the two limbs of r 24.2(1): does the output apply a real-prospect standard or decide the merits; does it address limb (b) at all; does it assess the respondent's prospects or the merits at large; does it treat a conflict of affidavit evidence as a reason not to resolve the matter. T2 is the headline: a model that never mentions limb (b) has not applied Part 24, whatever label it emitted. No existing codebook models a threshold determination as a threshold determination (`design-open-questions.md` B6), and these four codes survive a small n because they are frequencies, not comparisons.
3. *The ground check:* the model's chosen ground against the coder's reading of its reasoning, so that the automatic ground comparison of RQ3, which rests on a self-report that models apply poorly (Thalken et al L423–438), is validated where it matters most (D-P4).

**Tier 2.** Back-translation flips are coded with the same scheme, to show whether English flips differ in kind from rewording flips (v5 §11).

**Reliability.** A single coder; the codebook and every coded unit are released, and T codes can be checked against the texts. Single expert coding is accepted at this venue (`jurix-proceedings-review.md` §1.2); stated as a limitation. Authority checking (v5 H4, `threshold-codes.md` §"Authorities coding") is not a measure in this design; where a reason cites an authority, it is recorded descriptively and the distinction between fabricated, Cypriot and genuine English authority is kept, because English authority applied to a transposed rule is not a hallucination.

---

## 13. Threats and the design's responses

| # | Threat | Response |
|---|---|---|
| 1 | Sampling noise read as a language effect | the Greek split-half floor F (§10.5) |
| 2 | Rewording read as a language effect | matched back-translation per language arm; Δ = L − W; two-step conservatism stated (§6) |
| 3 | Translation error | seven automated checks on every file; the English arm read in full by the author; reading at every coded flip; code T (§7.3, §12) |
| 4 | Leakage through the judge's voice | cut before the court's voice; hearing detail and counsel's argument removed; two outcome-indicative passages removed; leak scan (§5) |
| 5 | Memorisation helping only Greek | de-identification; post-cutoff subset; no probe (§10.8) |
| 6 | A prompt favouring one language | Greek master, translated outwards by blind agents; equivalence check; identical content (§9.1) |
| 7 | A prompt favouring one model | one prompt, fixed before the run, no per-model tuning (§9.1) |
| 8 | English as the rule's doctrinal home | the DE-lit / DE-eng pair; code D; the reading stated in advance (§2, §6) |
| 9 | Provider drift | pinned snapshots, one session, random order of blocks, logged IDs (§10.9) |
| 10 | Small n | intervals; no equivalence claim; per-case reporting; committed protocol (§10.7) |
| 11 | Single coder | released codebook and units; checkable T codes (§12) |
| 12 | Non-independence | duplicates and twins removed at selection; judge clustering stated (§4.4) |
| 13 | Label coarsening hiding flips | four-option primary; binary secondary (§10.4) |
| 14 | Opaque selection | rated population, filter fixed before rating, every removal and withdrawal logged with its ground (§4) |
| 15 | Instructions lost in a long input | output instruction restated after File A (§9.2) |
| 16 | Wrong-language or malformed replies | recorded, replaced to k, rate reported (§10.3) |
| 17 | Invariance produced by hidden reasoning in English | Terra reasoning-off configuration; reasoning tokens per arm; the reading stated in advance (§10.2, §10.11) |
| 18 | A Claude model responding to Claude-written arms differently | per-model reporting; the Sonnet check stated in advance (§10.1, §10.11 Stage 5) |

---

## 14. Limitations, collected

*Every limitation the record has identified, in one place, grouped by where it arises. Each names its response; the response is the mitigation, not a denial.*

**Sample and selection.**

1. Ten cases. The language effect is a rate over cases with an interval of roughly ±0.3; only a large effect is resolvable; a null is reported as unresolved with its interval. The draws make each case's result reliable but add no cases (§10.7).
2. Selection saw the outcome; marginality cannot be rated from the facts alone. Coding and the run were blind (§4.1).
3. The sample was constructed to balance the answer set, not drawn; both the designed and the population compositions are reported (§4.4).
4. One judge decided four of the ten and another two; clustering cannot be modelled at this n (§4.4).
5. Appellate authority on Part 24 emerged during the corpus period; reported by stratum (§4.4).
6. The corpus is what CyLaw publishes; the base rate is not the Cypriot summary judgment standard (§3).
7. Two withdrawals have no recorded ground (§4.3, §16).

**Stimulus.**

8. Cypriot judges interleave fact with evaluation; the cut is a human judgment recorded as a marker, with the earlier cut taken and logged (§5.1).
9. Counsel's legal argument was removed, so the models decide on a thinner record than the judge had; the parties' pleaded case, including limb (b), is retained (§5.2).
10. De-identification cannot be proved complete by pattern matching; every file was read in full, and the record says what reading found that scanning had not (§5.2).

**Translation.**

11. No German legal reader. The German arms are checked structurally only; they are tier 2 and descriptive (§7.3).
12. The English arm was read in full by one bilingual reader, the author; there is no second reader (§7.3).
13. The translator is the same class of system as the object of study, and the translation is not exactly reproducible; the audit trail is the release (§7.1).
14. Blindness of the back-translation agents was instructed and structurally supported, not technically enforced; chrF is the after-the-fact diagnostic (§7.2).
15. The mechanical checks verify that nothing was lost, not that what arrived is right; the "she" defect is the proof (§7.3).
16. The round-trip similarity gap between routes is an observation about the instrument, partly produced by the German arm's deliberately plain vocabulary (§7.3).
17. The limb (b) formula carries modal force that differs by language in the material each arm receives (German *muss*, English "ought to"); a difference on T2 between English and German is not attributable to language alone (`prompting.md` §2B O1).
18. Three Greek phrasings close to, but not identical with, the Part 24 term were not swapped in DE-eng, so the vocabulary contrast covers the glossary term and not every real-prospect phrasing; the conditional-order and Order 18 rows do not occur in the ten files and are untested by the contrast (`translation.md` §5, M10–M11).
19. Greek word-for-word variation in the German arms (*Anspruch*, *Forderung*, *Klage* for one Greek word) is within ordinary lexical variation and is logged (`translation.md` §4.5).

**Prompt and rule.**

20. One prompt wording; sensitivity to wording is known (Choi 2025) and a reworded prompt is a post-run check, not a condition (§9.1).
21. The English and German prompts and rule texts are translations of the Greek master, with the author's idiom edits logged; the English prompt is not the working text (§9.1, §8).
22. Translated JSON field names are untested on the providers until the pilot; the fallback is recorded (§9.3).

**Models and run.**

23. Three closed models on one run date; behaviour behind closed doors changes, and future reproducibility cannot be guaranteed (Blair-Stanek L430–435).
24. One tested model, Sonnet 5, shares a provider lineage with the translation engine, and every arm except the Greek original is Claude-written text. A familiarity effect could run in the direction of the language contrast for that model; the back-translation absorbs part of it but cannot be assumed to cancel it. Checked, not excluded (§10.1; §10.11, Stage 5).
25. Default temperature is provider-specific and the three reasoning controls are not one scale; hidden reasoning is not observed (§10.2).
26. The noise floor is sampling noise under the stated settings, not a measure of the model's uncertainty (Choi 2025 L327–349).
27. Provider claims about parameters, cutoffs and limits are unverified until the pilot (`run-parameters.md` §5).

**Measurement and coding.**

28. Single coder for the court's order, the error codes, the threshold codes and the ground check; codebook and units released (§11, §12).
29. The model's stated ground is a self-report, validated only on the hand-coded flips (§9.3, §12).
30. The court's order is used as a sensitivity check, not as ground truth; accuracy against it is not a measure of reasoning quality (§10.6).
31. Memorisation is bounded by de-identification and the post-cutoff subset, and is not tested directly: the caption probe was not run (§10.8).
32. The doctrinal-home confound (English authority in 88% of the corpus) is read through the German pair and code D; it is not eliminated (§2, §10.11).
33. Hidden reasoning is not observable on the closed models, and reasoning models tend to reason in English whatever the input language, so an invariant result may reflect an internal pivot to English. Bounded by the Terra reasoning-off configuration, not excluded (§10.2; §10.11, Stage 3).
34. Failed draws are replaced to k. If failures differ by language and are related to the outcome, replacement keeps the draws that succeeded; checked by reporting the disposal rates with failures counted as a category of their own (§10.3).
