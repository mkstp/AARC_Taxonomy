# Inter-Annotator Agreement Analysis

**Date:** 2026-05-04
**Annotators:** Human (gold standard, Marc) vs. LLM (claude-sonnet-4-6)
**Matched turns:** 90 of 100 human-annotated turns (140 LLM pre-annotations available)
**Schema:** v1
**Labels:** Binary deficit flags per AARC component (Acknowledgement, Agency, Reciprocity, Clarity)
**Metrics:** Cohen's Kappa (κ), Krippendorff's Alpha (α), observed agreement (P_o), and per-annotator positive rates

---

## Results by Component

| Component | κ | Interpretation | α | P_o | Human+ | LLM+ |
|-----------|---|----------------|---|-----|--------|------|
| Acknowledgement (A) | 0.560 | moderate | 0.558 | 85.6% | 17.8% | 23.3% |
| Agency (G) | 0.352 | fair | 0.352 | 85.6% | 12.2% | 13.3% |
| Reciprocity (R) | 0.379 | fair | 0.379 | 86.7% | 13.3% | 11.1% |
| Clarity (C) | 0.313 | fair | 0.313 | 76.7% | 22.2% | 21.1% |

---

## Analysis

### Prevalence and Kappa Interpretation


The following components have sufficient positive-case prevalence (≥ 10%) for kappa to be straightforwardly interpretable: **Acknowledgement (A), Agency (G), Reciprocity (R), Clarity (C)**.

### Component-Level Findings

**Acknowledgement (A):** κ = 0.560 (moderate), α = 0.558, P_o = 85.6%. LLM labels positive more often than the human annotator by 5.5%, suggesting the model may be over-sensitive to this deficit.

**Agency (G):** κ = 0.352 (fair), α = 0.352, P_o = 85.6%. LLM and human positive rates are closely aligned.

**Reciprocity (R):** κ = 0.379 (fair), α = 0.379, P_o = 86.7%. LLM and human positive rates are closely aligned.

**Clarity (C):** κ = 0.313 (fair), α = 0.313, P_o = 76.7%. LLM and human positive rates are closely aligned.

### Overall Assessment

Mean across components: κ = 0.401, α = 0.400, P_o = 83.6%. These figures reflect agreement under the v1 schema and serve as a baseline prior to moving the full annotation pass to v2. They should not be used as a final validity measure for the corpus; they establish the floor from which v2 schema agreement should improve.

### Limitations

1. **Schema version:** All 90 turns were annotated under the v1 schema.
2. **Sample size:** 90 turns from a single corpus provides adequate signal for per-component trending but is underpowered for fine-grained subcategory analysis.
3. **LLM annotator:** The LLM was prompted to apply the schema; any systematic prompt-induced bias (e.g., conservative labeling under the opening-turn epistemic constraint) will suppress positive rates and inflate apparent agreement on negatives.