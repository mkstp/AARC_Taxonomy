# Inter-Annotator Agreement Analysis

**Date:** 2026-05-05
**Annotators:** Human (gold standard, Marc) vs. LLM (claude-sonnet-4-6)
**Matched turns:** 139 of 139 human-annotated turns (188 LLM pre-annotations available)
**Schema:** v3
**Labels:** Binary deficit flags per AARC component (Acknowledgement, Agency, Reciprocity, Clarity)
**Metrics:** Cohen's Kappa (κ), Krippendorff's Alpha (α), observed agreement (P_o), and per-annotator positive rates

---

## Results by Component

| Component | κ | Interpretation | α | P_o | Human+ | LLM+ |
|-----------|---|----------------|---|-----|--------|------|
| Acknowledgement (A) | 0.767 | substantial | 0.766 | 91.4% | 23.0% | 25.9% |
| Agency (G) | 0.597 | moderate | 0.595 | 90.6% | 10.8% | 15.8% |
| Reciprocity (R) | 0.788 | substantial | 0.788 | 95.7% | 13.0% | 10.1% |
| Clarity (C) | 0.546 | moderate | 0.544 | 86.3% | 15.8% | 20.9% |

---

## Positive Signal (F1 Analysis)

Human annotations treated as ground truth. LLM as predictor.

| Component | TP | FP | FN | TN | Precision | Recall | F1 |
|-----------|----|----|----|----|-----------|--------|----|
| Acknowledgement (A) | 28 | 8 | 4 | 99 | 0.778 | 0.875 | 0.824 |
| Agency (G) | 12 | 10 | 3 | 114 | 0.545 | 0.800 | 0.649 |
| Reciprocity (R) | 13 | 1 | 5 | 120 | 0.929 | 0.722 | 0.812 |
| Clarity (C) | 16 | 13 | 6 | 104 | 0.552 | 0.727 | 0.627 |
| **Macro avg** | | | | | **0.701** | **0.781** | **0.728** |

Total positive label slots (human): 87 / 556 (15.6% positive rate). Agreed positives (TP): 69. Agreed negatives (TN): 437.

---

## Analysis

### Prevalence and Kappa Interpretation


The following components have sufficient positive-case prevalence (≥ 10%) for kappa to be straightforwardly interpretable: **Acknowledgement (A), Agency (G), Reciprocity (R), Clarity (C)**.

### Component-Level Findings

**Acknowledgement (A):** κ = 0.767 (substantial), α = 0.766, P_o = 91.4%. LLM and human positive rates are closely aligned.

**Agency (G):** κ = 0.597 (moderate), α = 0.595, P_o = 90.6%. LLM labels positive more often than the human annotator by 5.0%, suggesting the model may be over-sensitive to this deficit.

**Reciprocity (R):** κ = 0.788 (substantial), α = 0.788, P_o = 95.7%. LLM and human positive rates are closely aligned.

**Clarity (C):** κ = 0.546 (moderate), α = 0.544, P_o = 86.3%. LLM labels positive more often than the human annotator by 5.0%, suggesting the model may be over-sensitive to this deficit.

### Overall Assessment

Mean across components: κ = 0.674, α = 0.673, P_o = 91.0%. These figures reflect agreement under the v3 schema. They should not be used as a final validity measure for the corpus; they establish a reference point for tracking annotation quality across schema iterations.

### Limitations

1. **Schema version:** All 139 turns were annotated under the v3 schema.
2. **Sample size:** 139 turns from a single corpus provides adequate signal for per-component trending but is underpowered for fine-grained subcategory analysis.
3. **LLM annotator:** The LLM was prompted to apply the schema; any systematic prompt-induced bias (e.g., conservative labeling under the opening-turn epistemic constraint) will suppress positive rates and inflate apparent agreement on negatives.