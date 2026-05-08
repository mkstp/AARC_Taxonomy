# IAA Extended Analysis: Turns 57–100 and Positive Signal Adequacy

**Date:** 2026-05-03
**Annotators:** Human (gold standard, Marc) vs. LLM (claude-sonnet-4-6)
**Corpus coverage:** 100 human-annotated turns; 100 LLM pre-annotations matched; 50 LLM-only turns pending
**Schema:** v2 (speaker-attribution principle; §3.5 Reciprocity boundary added)
**Context:** Extends the v1 baseline (`iaa_v1_baseline.md`, n=56) to the full gold pass and surfaces a structural concern about positive-case prevalence.

---

## 1. Agreement Results by Slice

### Turns 57–100 (n=44, annotated under v2 schema)

| Component | κ | Interpretation | α | P_o | Human+ | LLM+ |
|-----------|---|----------------|---|-----|--------|------|
| Acknowledgement (A) | 0.696 | substantial | 0.694 | 90.9% | 20.4% | 15.9% |
| Agency (G) | 0.661 | substantial | 0.660 | 90.9% | 18.2% | 13.6% |
| Reciprocity (R) | 0.481 | moderate | 0.480 | 88.6% | 13.6% | 11.4% |
| Clarity (C) | 0.441 | moderate | 0.437 | 79.5% | 20.4% | 27.3% |
| **Mean** | **0.570** | | **0.568** | **87.5%** | | |

### Comparison to v1 Baseline (turns 1–56)

| Component | κ v1 (1–56) | κ v2 (57–100) | Δκ |
|-----------|------------|---------------|-----|
| Acknowledgement (A) | 0.249 | **0.696** | +0.447 |
| Agency (G) | 0.614 | 0.661 | +0.047 |
| Reciprocity (R) | 0.340 | 0.481 | +0.141 |
| Clarity (C) | 0.545 | 0.441 | −0.104 |
| **Mean** | **0.437** | **0.570** | **+0.133** |

### Full corpus (n=100)

| Component | κ | Interpretation | α | P_o | Human+ | LLM+ |
|-----------|---|----------------|---|-----|--------|------|
| Acknowledgement (A) | 0.503 | moderate | 0.502 | 88.0% | 16.0% | 12.0% |
| Agency (G) | 0.673 | substantial | 0.673 | 91.0% | 16.0% | 17.0% |
| Reciprocity (R) | 0.502 | moderate | 0.502 | 88.0% | 14.0% | 14.0% |
| Clarity (C) | 0.616 | substantial | 0.616 | 86.0% | 23.0% | 25.0% |
| **Mean** | **0.574** | | **0.573** | **88.2%** | | |

> **Note on the Clarity full-corpus figure:** The pooled κ=0.616 should not be read as stronger agreement than either slice alone. When the two slices are pooled, the marginal positive rates shift (combined H+=23%, LLM+=25%), which raises Pe and mechanically inflates kappa relative to what either slice independently shows. Per-slice figures are the more reliable diagnostic.

---

## 2. Component-Level Interpretation

**Acknowledgement:** The largest shift in the corpus (+0.447 across slices). The v2 speaker-attribution principle — deficits attributed to the *speaker of the turn*, not assessed from a global relational perspective — appears to have resolved the main source of disagreement from the v1 pass. LLM under-labeling persisted but narrowed (−8.9% in v1 → −4.5% full corpus). This is the most important schema improvement signal.

**Agency:** Stable and high throughout. The construct is operationally clear to both annotators. F1=0.727 in the full corpus.

**Reciprocity:** Improved from fair to moderate across slices. The §3.5 boundary case (legitimate assertiveness is not a Reciprocity deficit) appears to have helped. Symmetric bias: FP=6, FN=6 in the full corpus — the LLM and human are making different kinds of errors at similar rates.

**Clarity:** Regressed slightly in turns 57–100 (κ=0.441 vs. 0.545 in v1), with the LLM over-labeling by 6.9 percentage points (H+=20.4%, LLM+=27.3%). The full-corpus κ=0.616 is inflated by the pooling effect noted above. The LLM appears to flag surface-level disfluency or vagueness as Clarity deficit more liberally than the human annotator does. This warrants attention before scaling LLM annotations.

---

## 3. Positive Signal Adequacy

### 3.1 Structural problem

Kappa is dominated by true negatives. Across all four components, 69–80 of 100 turns fall in the TN cell (both annotators agree: no deficit). The observed agreement and kappa figures reflect this structure — they say more about shared ability to recognize *absence* of deficit than about shared ability to recognize *presence*.

### 3.2 Confusion matrix (full corpus, n=100)

| Component | TP | FP | FN | TN | Pos union | Prec | Rec | F1 |
|-----------|----|----|----|----|-----------|------|-----|----|
| Acknowledgement (A) | 8 | 4 | 8 | 80 | 20 | 66.7% | 50.0% | 0.571 |
| Agency (G) | 12 | 5 | 4 | 79 | 21 | 70.6% | 75.0% | 0.727 |
| Reciprocity (R) | 8 | 6 | 6 | 80 | 20 | 57.1% | 57.1% | 0.571 |
| Clarity (C) | 17 | 8 | 6 | 69 | 31 | 68.0% | 73.9% | 0.708 |

*TP = both annotators positive; FP = LLM positive, human negative; FN = human positive, LLM negative; Pos union = turns where at least one annotator said positive.*

The F1 column is the more informative metric for this imbalanced label distribution. Agency (0.727) and Clarity (0.708) are acceptable; Acknowledgement and Reciprocity (both 0.571) indicate the LLM misses roughly half the positive cases the human annotator catches.

### 3.3 What is needed

To reliably estimate agreement on positive cases, approximately 50 jointly-agreed positives per component is a reasonable minimum. Current counts: A=8, G=12, R=8, C=17. Shortfalls: A=−42, G=−38, R=−42, C=−33. At the current corpus-wide positive rate (~17%), closing these gaps through uniform random sampling would require roughly 300–400 additional turns — an impractical lift at this stage.

---

## 4. Latent Signal in Unannotated Turns

Of the 50 LLM-annotated turns not yet reviewed by the human annotator:

| Component | LLM-positive in unannotated set |
|-----------|-------------------------------|
| Acknowledgement (A) | 14 |
| Agency (G) | 3 |
| Reciprocity (R) | 4 |
| Clarity (C) | 5 |
| **At least 1 positive** | **24 of 50** |
| **2+ positives (multi-flag)** | **2 of 50** |

LLM confidence on positive-flagged unannotated turns concentrates at 0.62–0.78, compared to 0.82–0.92 for negative-flagged turns. The model is considerably less certain when flagging deficits, which is expected, but also means the hit rate when a human reviews these will not approach 100%.

If human-annotator confirmation runs at approximately 60% (consistent with the 66–71% precision seen in the annotated set for A and G), annotating all 24 LLM-positive turns would add roughly:
- A: ~8 new TPs (from 14 LLM-positive flags)
- G: ~2 new TPs
- R: ~2 new TPs
- C: ~3 new TPs

This is modest but targeted: the same 24 turns annotated at random from the full 50 would be expected to yield fewer than half as many positives.

---

## 5. Implications

1. **Use F1 alongside kappa** as the primary reporting metric for positive-case agreement. Kappa conveys overall agreement; F1 conveys how reliably the LLM finds what the human finds.
2. **Prioritize LLM-positive turns for remaining human annotation.** Of the 50 unannotated turns, annotate the 24 LLM-positive ones first, starting with the 2 multi-flag turns and then ordering by LLM confidence (descending).
3. **Clarity requires prompt review.** Before scaling LLM annotations, investigate Clarity FP cases to determine whether the LLM is applying a looser criterion than the schema intends.
4. **Acknowledge the floor.** Even after annotating all 50 remaining turns, positive-case counts will remain below what would be needed for fine-grained reliability analysis. These IAA figures establish feasibility and direction, not validated precision. They should be reported as preliminary agreement estimates, not as reliability coefficients for a finished annotation scheme.
