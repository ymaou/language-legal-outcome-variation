**Supplementary Table 2.** Decide against predict, Greek and English versions. Under "decide" (main run) the model decides the application as a judge, 31 draws per version and 62 in Greek; under "predict" (exploratory run, designed after the main results were known) it predicts the court's decision as a legal analyst, 15 draws per version and 30 in Greek. Measures as in Supplementary Table 1. The predictive run had no back-translation version, so its language rate is not net of rewording.

| Model | Framing | Greek draws dismissed | Agreement with court | F | L_EN | Mean D [95% CI] | Cases flipping to refusal in English |
|---|---|---|---|---|---|---|---|
| GPT-5.6 Terra | decide | 620/620 | 0.40 | 0.00 | 0.00 | 0.00 [0.00, 0.01] | 0 |
| GPT-5.6 Terra | predict | 300/300 | 0.40 | 0.00 | 0.00 | 0.02 [0.00, 0.06] | 0 |
| GPT-5.6 Terra, reasoning off | decide | 597/620 | 0.40 | 0.00 | 0.00 | −0.04 [−0.11, 0.00] | 0 |
| GPT-5.6 Terra, reasoning off | predict | 300/300 | 0.40 | 0.00 | 0.00 | 0.00 [0.00, 0.00] | 0 |
| Claude Sonnet 5 | decide | 546/620 | 0.40 | 0.00 | 0.00 | −0.10 [−0.18, −0.04] | 0 |
| Claude Sonnet 5 | predict | 196/300 | 0.50 | 0.18 | 0.33 | −0.31 [−0.47, −0.15] | 3 |
| Gemini 3.6 Flash | decide | 577/620 | 0.50 | 0.00 | 0.00 | −0.01 [−0.03, 0.01] | 0 |
| Gemini 3.6 Flash | predict | 277/300 | 0.50 | 0.01 | 0.01 | 0.00 [−0.03, 0.03] | 0 |
