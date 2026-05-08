# Deliverables

---

**DEL-001: Formal literature review**
A structured review of the relevant literature spanning FPO, AARC, dispute resolution theory (CPRI, dignity, face-negotiation), and related computational approaches to dialogue intervention.
Justification: Establishes the theoretical foundation for all downstream design decisions, particularly the intervention taxonomy and annotation schema.
Issue: FPO-dk9

---

**DEL-002: Position paper**
An argumentative paper establishing the case for an AARC-grounded intervention framework for AI-assisted mediation, situating the work relative to FPO and conflict resolution theory.
Justification: Required course deliverable; also serves as the theoretical framing document for the project.
Issue: FPO-max

---

**DEL-003: Intervention taxonomy**
A defined set of intervention types an agent can execute at high-friction turns, grounded in AARC deficit states and positioned relative to FPO's existing action space (extending, replacing, or drawing selectively from it).
Justification: Required before annotation can begin; determines what labels are applied to preference pairs.
Issue: FPO-1jn

---

**DEL-004: Annotation schema**
A formal specification mapping AARC deficit labels (Acknowledgement, Agency, Reciprocity, Clarity) to FPO friction signals, with each AARC component operationalized as observable turn-level dialogue behavior.
Justification: The primary theoretical contribution of the project; governs all corpus annotation and reward model training.
Issue: FPO-yax

---

**DEL-005: Gold standard trajectories**
10–15 LLM-generated, researcher-reviewed mediation dialogue trajectories, fully annotated according to the schema, produced before LLM-assisted scaling begins.
Justification: Establishes annotation quality baseline and trains LLM-assisted generation; required by VC-04.
Issue: FPO-77p

---

**DEL-006: Synthetic annotated corpus**
LLM-scaled dialogue trajectories annotated with FPO submodel scores, AARC deficit labels, intervention taxonomy labels, and pairwise preference pairs at every high-friction turn.
Justification: Primary training data for the reward model; required for ablation study.
Issue: FPO-5a3

---

**DEL-007: Reward model**
LLaMA 8B fine-tuned on pairwise preference signals derived from the annotated corpus.
Justification: Proof-of-concept demonstrating that AARC-grounded preference signals can train a turn-level intervention classifier.
Issue: FPO-4xm

---

**DEL-008: Ablation study**
Quantitative comparison of reward model performance trained on AARC-enriched signals vs. friction scores alone.
Justification: Primary empirical validation of VC-01 and VC-05 — the claim that AARC labels add discriminative value.
Issue: FPO-a2n

---

**DEL-009: Final writeup**
Written results report covering the full project — methodology, corpus construction, reward model training, and ablation study.
Justification: Required course deliverable.
Issue: FPO-zhw

---

**DEL-010: Final presentation**
8–10 minute presentation covering the full project.
Justification: Required course deliverable. Completed prior to session 42.
Issue: FPO-5du
