# Inter-Annotator Agreement Analysis

**Date:** 2026-05-07
**Annotators:** Human (gold standard, Marc) vs. LLM (gpt-5.4)
**Matched turns:** 140 of 140 human-annotated turns (140 LLM pre-annotations available)
**Schema:** current
**Labels:** Binary deficit flags per AARC component (Acknowledgement, Agency, Reciprocity, Clarity)
**Metrics:** Cohen's Kappa (κ), Krippendorff's Alpha (α), observed agreement (P_o), and per-annotator positive rates

---

## Results by Component

| Component | κ | Interpretation | α | P_o | Human+ | LLM+ |
|-----------|---|----------------|---|-----|--------|------|
| Acknowledgement (A) | 0.534 | moderate | 0.533 | 84.3% | 22.9% | 20.0% |
| Agency (G) | 0.389 | fair | 0.384 | 90.7% | 10.7% | 5.7% |
| Reciprocity (R) | 0.533 | moderate | 0.533 | 89.3% | 12.9% | 13.6% |
| Clarity (C) | 0.196 | slight | 0.185 | 73.6% | 15.7% | 25.0% |

---

## Positive Signal (F1 Analysis)

Human annotations treated as ground truth. LLM as predictor.

| Component | TP | FP | FN | TN | Precision | Recall | F1 |
|-----------|----|----|----|----|-----------|--------|----|
| Acknowledgement (A) | 19 | 9 | 13 | 99 | 0.679 | 0.594 | 0.633 |
| Agency (G) | 5 | 3 | 10 | 122 | 0.625 | 0.333 | 0.435 |
| Reciprocity (R) | 11 | 8 | 7 | 114 | 0.579 | 0.611 | 0.595 |
| Clarity (C) | 10 | 25 | 12 | 93 | 0.286 | 0.455 | 0.351 |
| **Macro avg** | | | | | **0.542** | **0.498** | **0.503** |

Total positive label slots (human): 87 / 560 (15.5% positive rate). Agreed positives (TP): 45. Agreed negatives (TN): 428.

---

## Analysis

### Prevalence and Kappa Interpretation


The following components have sufficient positive-case prevalence (≥ 10%) for kappa to be straightforwardly interpretable: **Acknowledgement (A), Agency (G), Reciprocity (R), Clarity (C)**.

### Component-Level Findings

**Acknowledgement (A):** κ = 0.534 (moderate), α = 0.533, P_o = 84.3%. LLM and human positive rates are closely aligned.

**Agency (G):** κ = 0.389 (fair), α = 0.384, P_o = 90.7%. LLM labels positive less often than the human annotator by 5.0%, suggesting the model may be under-sensitive to this deficit.

**Reciprocity (R):** κ = 0.533 (moderate), α = 0.533, P_o = 89.3%. LLM and human positive rates are closely aligned.

**Clarity (C):** κ = 0.196 (slight), α = 0.185, P_o = 73.6%. LLM labels positive more often than the human annotator by 9.3%, suggesting the model may be over-sensitive to this deficit.

### Overall Assessment

Mean across components: κ = 0.413, α = 0.409, P_o = 84.5%. These figures reflect agreement under the current schema. They should not be used as a final validity measure for the corpus; they establish a reference point for tracking annotation quality across schema iterations.

### Limitations

1. **Schema version:** All 140 turns were annotated under the current schema.
2. **Sample size:** 140 turns from a single corpus provides adequate signal for per-component trending but is underpowered for fine-grained subcategory analysis.
3. **LLM annotator:** The LLM was prompted to apply the schema; any systematic prompt-induced bias (e.g., conservative labeling under the opening-turn epistemic constraint) will suppress positive rates and inflate apparent agreement on negatives.