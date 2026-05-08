# Inter-Annotator Agreement Analysis

**Date:** 2026-05-07
**Annotators:** Human (gold standard, Marc) vs. LLM (gpt-5.4)
**Matched turns:** 140 of 188 human-annotated turns (140 LLM pre-annotations available)
**Schema:** current
**Labels:** Binary deficit flags per AARC component (Acknowledgement, Agency, Reciprocity, Clarity)
**Metrics:** Cohen's Kappa (κ), Krippendorff's Alpha (α), observed agreement (P_o), and per-annotator positive rates

---

## Results by Component

| Component | κ | Interpretation | α | P_o | Human+ | LLM+ |
|-----------|---|----------------|---|-----|--------|------|
| Acknowledgement (A) | 0.597 | moderate | 0.595 | 85.7% | 25.7% | 20.0% |
| Agency (G) | 0.272 | fair | 0.253 | 85.7% | 15.7% | 5.7% |
| Reciprocity (R) | 0.349 | fair | 0.347 | 86.4% | 10.0% | 13.6% |
| Clarity (C) | 0.140 | slight | 0.139 | 69.3% | 21.4% | 25.0% |

---

## Positive Signal (F1 Analysis)

Human annotations treated as ground truth. LLM as predictor.

| Component | TP | FP | FN | TN | Precision | Recall | F1 |
|-----------|----|----|----|----|-----------|--------|----|
| Acknowledgement (A) | 22 | 6 | 14 | 98 | 0.786 | 0.611 | 0.688 |
| Agency (G) | 5 | 3 | 17 | 115 | 0.625 | 0.227 | 0.333 |
| Reciprocity (R) | 7 | 12 | 7 | 114 | 0.368 | 0.500 | 0.424 |
| Clarity (C) | 11 | 24 | 19 | 86 | 0.314 | 0.367 | 0.339 |
| **Macro avg** | | | | | **0.523** | **0.426** | **0.446** |

Total positive label slots (human): 102 / 560 (18.2% positive rate). Agreed positives (TP): 45. Agreed negatives (TN): 413.

---

## Analysis

### Prevalence and Kappa Interpretation


The following components have sufficient positive-case prevalence (≥ 10%) for kappa to be straightforwardly interpretable: **Acknowledgement (A), Agency (G), Reciprocity (R), Clarity (C)**.

### Component-Level Findings

**Acknowledgement (A):** κ = 0.597 (moderate), α = 0.595, P_o = 85.7%. LLM labels positive less often than the human annotator by 5.7%, suggesting the model may be under-sensitive to this deficit.

**Agency (G):** κ = 0.272 (fair), α = 0.253, P_o = 85.7%. LLM labels positive less often than the human annotator by 10.0%, suggesting the model may be under-sensitive to this deficit.

**Reciprocity (R):** κ = 0.349 (fair), α = 0.347, P_o = 86.4%. LLM labels positive more often than the human annotator by 3.6%, suggesting the model may be over-sensitive to this deficit.

**Clarity (C):** κ = 0.140 (slight), α = 0.139, P_o = 69.3%. LLM labels positive more often than the human annotator by 3.6%, suggesting the model may be over-sensitive to this deficit.

### Overall Assessment

Mean across components: κ = 0.340, α = 0.334, P_o = 81.8%. These figures reflect agreement under the current schema. They should not be used as a final validity measure for the corpus; they establish a reference point for tracking annotation quality across schema iterations.

### Limitations

1. **Schema version:** All 140 turns were annotated under the current schema.
2. **Sample size:** 140 turns from a single corpus provides adequate signal for per-component trending but is underpowered for fine-grained subcategory analysis.
3. **LLM annotator:** The LLM was prompted to apply the schema; any systematic prompt-induced bias (e.g., conservative labeling under the opening-turn epistemic constraint) will suppress positive rates and inflate apparent agreement on negatives.