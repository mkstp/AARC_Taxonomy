# Project Charter: FPO Mediation Extension

## Overarching Objective

Develop an AARC-grounded framework for AI-assisted mediation between humans in conflict, addressing a gap in FPO's current scope: its epistemic-only approach replicates the "content trap" identified in conflict resolution theory, leaving relational, procedural, and identity-based dimensions unaddressed. The relationship to FPO is open — the new framework may extend FPO, replace it, or supersede it in the mediation context. The project validates the core annotation schema and intervention taxonomy, demonstrates that AARC deficit labels produce a richer reward signal than friction scores alone, and delivers a synthetic annotated corpus and trained reward model as proof of concept.

## Project Purpose

This project investigates whether AARC deficit labels (Acknowledgement, Agency, Reciprocity, Clarity) correlate meaningfully with FPO friction signals (Unc, Contr, Haz, ValConf, InfoGain) at the turn level, and whether grounding intervention motivation in AARC theory produces a richer reward signal than friction scores alone. It is framed as a preference learning problem: given an evolving mediation transcript, can a model learn to distinguish better from worse interventions at high-friction moments? Whether the resulting framework operates alongside FPO or displaces it is a design decision to be made as the work develops. The AARC model (Hoben, 2020) is a practitioner heuristic without formal empirical validation; operationalizing its components as turn-level annotation targets and demonstrating their utility as RL reward signal features constitutes initial computational evidence for the model's utility as an annotation framework.

## Scope Commitments

**In scope:**
- Design of a novel annotation schema mapping AARC deficit labels to FPO friction signals at the turn level
- Operationalization of each AARC component as observable, turn-level dialogue behavior
- Definition of an intervention taxonomy — which may extend, replace, or draw selectively from FPO's existing action space
- Construction of a synthetic annotated dialogue corpus (researcher-reviewed gold standard + LLM-scaled)
- Generation of pairwise preference pairs at high-friction turns
- Training a reward model (LLaMA 8B) on pairwise preference signals
- Ablation study comparing AARC-enriched vs. friction-only reward signal
- Practitioner validation of the annotation schema with CBI professionals
- Final written report and 8–10 minute presentation

**Out of scope:**
- Deployment of a finished real-time mediation system
- Use of pre-existing public dialogue datasets as primary data source
- GRPO policy training — the trained reward model is designed to serve as a reward function for downstream GRPO training (e.g., via Unsloth), but that training is not a deliverable of this project
- Formal user studies or evaluations beyond CBI practitioner schema review

## Validation Conditions

**VC-01:** AARC-enriched reward signal outperforms friction-only baseline
- **Applies to:** Ablation study results
- **Check method:** Quantitative comparison of reward model performance with vs. without AARC labels; improvement in preference prediction accuracy

**VC-02:** Annotation schema passes practitioner review
- **Applies to:** Annotation schema and AARC operationalization
- **Check method:** CBI practitioners can reliably apply the schema to sample trajectories; feedback incorporated into final schema

**VC-03:** Pairwise preference pairs are generated for all high-friction turns in the corpus
- **Applies to:** Synthetic annotated corpus
- **Check method:** Every turn annotated as high-friction has at least one corresponding preference pair (intervention A vs. B) with a friction amelioration score

**VC-04:** Gold standard trajectories precede LLM-scaled generation
- **Applies to:** Corpus construction process
- **Check method:** 10–15 LLM-generated, researcher-reviewed trajectories exist and are annotated before LLM-assisted scaling begins

**VC-05:** AARC deficit labels and FPO friction signals co-vary meaningfully at the turn level
- **Applies to:** Annotated corpus
- **Check method:** Statistical analysis of correlation between AARC labels and FPO submodel scores across the corpus

**VC-06:** Annotation quality meets threshold for reward model training
- **Applies to:** Preference pair corpus and reward model training readiness
- **Check method:** Corpus yields between 5,000 and 20,000 preference pairs; reward model agreement on held-out preference pairs reaches at least 70% before training proceeds

## Known Limitations and Future Work

- **Evaluation circularity** — IAA metrics measure annotator consistency, not mediation effectiveness. External validation against practitioner judgments or behavioral outcomes is required before generalization claims hold. (FPO-g3v)
- **Corpus register scope** — LLM-generated dialogues encode WEIRD-adjacent communicative norms. Cross-cultural applicability is unassessed; future corpus work should include explicit register stratification and practitioner consultation for target cultural contexts. (FPO-i93)
- **AARC priority ordering** — Turn-level equal weighting does not test whether the A→G→R→C diagnostic ordering is learnable from training data. Trajectory-structured corpus design is required to assess this. (FPO-q23)
- **Agency and Clarity annotation** — Both components have definitional problems that DSPy optimization cannot resolve: boundary conditions are underspecified relative to the distributional properties of conflict dialogue. Taxonomy revision, a fresh gold pass, and re-optimization are deferred to a future annotation round. The primary Claude silver annotation pass proceeds on all four components (κ=0.671); the limitation applies specifically to the DSPy/GPT-5.4 optimization track. (FPO-aq6)
- **Corpus naturalistic validity** — The synthetic dialogue corpus has not been evaluated against naturalistic conflict data. Whether LLM-generated dialogues adequately represent real conflict interaction for the purposes of deficit detection rests on design reasoning, not empirical measurement. A systematic comparison against real conflict transcripts is required and is deferred to future work. (FPO-b1i)
