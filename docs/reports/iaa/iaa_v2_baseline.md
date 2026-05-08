# Inter-Annotator Agreement Analysis

**Date:** 2026-05-04
**Annotators:** Human (gold standard, Marc) vs. LLM (claude-sonnet-4-6)
**Matched turns:** 100 of 100 human-annotated turns (150 LLM pre-annotations available)
**Schema:** v2
**Labels:** Binary deficit flags per AARC component (Acknowledgement, Agency, Reciprocity, Clarity)
**Metrics:** Cohen's Kappa (κ), Krippendorff's Alpha (α), observed agreement (P_o), and per-annotator positive rates

---

## Results by Component

| Component | κ | Interpretation | α | P_o | Human+ | LLM+ |
|-----------|---|----------------|---|-----|--------|------|
| Acknowledgement (A) | 0.751 | substantial | 0.750 | 91.0% | 21.0% | 26.0% |
| Agency (G) | 0.559 | moderate | 0.558 | 91.0% | 10.0% | 13.0% |
| Reciprocity (R) | 0.772 | substantial | 0.771 | 95.0% | 14.0% | 11.0% |
| Clarity (C) | 0.540 | moderate | 0.540 | 85.0% | 19.0% | 22.0% |

---

## Positive Signal (F1 Analysis)

Human annotations treated as ground truth. LLM as predictor.

| Component | TP | FP | FN | TN | Precision | Recall | F1 |
|-----------|----|----|----|----|-----------|--------|----|
| Acknowledgement (A) | 19 | 7 | 2 | 72 | 0.731 | 0.905 | 0.808 |
| Agency (G) | 7 | 6 | 3 | 84 | 0.538 | 0.700 | 0.609 |
| Reciprocity (R) | 10 | 1 | 4 | 85 | 0.909 | 0.714 | 0.800 |
| Clarity (C) | 13 | 9 | 6 | 72 | 0.591 | 0.684 | 0.634 |
| **Macro avg** | | | | | **0.692** | **0.751** | **0.713** |

Total positive label slots (human): 64 / 400 (16.0% positive rate). Agreed positives (TP): 49. Agreed negatives (TN): 313.

---

## Analysis

### Prevalence and Kappa Interpretation


The following components have sufficient positive-case prevalence (≥ 10%) for kappa to be straightforwardly interpretable: **Acknowledgement (A), Agency (G), Reciprocity (R), Clarity (C)**.

### Component-Level Findings

**Acknowledgement (A):** κ = 0.751 (substantial), α = 0.750, P_o = 91.0%. LLM labels positive more often than the human annotator by 5.0%, suggesting the model may be over-sensitive to this deficit.

**Agency (G):** κ = 0.559 (moderate), α = 0.558, P_o = 91.0%. LLM labels positive more often than the human annotator by 3.0%, suggesting the model may be over-sensitive to this deficit.

**Reciprocity (R):** κ = 0.772 (substantial), α = 0.771, P_o = 95.0%. LLM labels positive less often than the human annotator by 3.0%, suggesting the model may be under-sensitive to this deficit.

**Clarity (C):** κ = 0.540 (moderate), α = 0.540, P_o = 85.0%. LLM labels positive more often than the human annotator by 3.0%, suggesting the model may be over-sensitive to this deficit.

### Overall Assessment

Mean across components: κ = 0.655, α = 0.655, P_o = 90.5%. These figures reflect agreement under the v2 schema. They should not be used as a final validity measure for the corpus; they establish a reference point for tracking annotation quality across schema iterations.

### Limitations

1. **Schema version:** All 100 turns were annotated under the v2 schema.
2. **Sample size:** 100 turns from a single corpus provides adequate signal for per-component trending but is underpowered for fine-grained subcategory analysis.
3. **LLM annotator:** The LLM was prompted to apply the schema; any systematic prompt-induced bias (e.g., conservative labeling under the opening-turn epistemic constraint) will suppress positive rates and inflate apparent agreement on negatives.