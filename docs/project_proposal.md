**COSI 115 NLP2 Final Project Proposal**  
**Marc St. Pierre**  
**Wed 11 Mar 2026**

**1\. Task**  
The task is turn-level dialogue intervention classification: given an evolving mediation transcript, predict when and how a mediator should intervene to improve the epistemic quality of the exchange. This is framed as a preference learning problem — the model is trained to distinguish better from worse intervention strategies at high-friction moments using pairwise reward signals derived from annotated dialogue trajectories.

**2\. Track**  
Research. The project investigates a specific hypothesis: that AARC deficit labels (Acknowledgement, Agency, Reciprocity, Clarity) correlate meaningfully with FPO friction signals (Unc, Contr, Haz, ValConf, InfoGain) at the turn level. Rather than deploying a finished system, the goal is to validate an annotation schema, produce labeled preference pairs, and assess whether AARC-grounded motivation labels enrich the reward signal compared to friction scores alone.

**3\. Focus**  
Data. The primary contribution is the construction of a synthetic annotated dialogue corpus, which does not currently exist. "Going deep" means: 

1. Designing an annotation schema from scratch,  
2. Authoring researcher-written gold standard trajectories before scaling with LLM assistance  
3. Generating pairwise intervention comparisons at high-friction turns  
4. Validating the schema with professional practitioners

**4\. Data**  
No publicly available dataset is used as the primary source. The dataset is self-constructed: synthetically generated dialogue trajectories annotated with FPO submodel scores, intervention taxonomy labels drawn from the FPO action space, and AARC deficit labels applied top-down. Each high-friction turn generates a preference pair (intervention A vs. intervention B) scored for friction amelioration. CBI practitioner roleplay transcripts are a planned validation source in a later phase but are not available for Phase 1\.

**5\. Approach**  
The primary model is a reward model using LLama 8b, trained on pairwise preference signals derived from the annotated trajectories. Individual friction components are estimated by a provided subagent pipeline which handles uncertainty, hazard, value conflict, and information gain estimation. 

**6\. Timeline**

Week 1 (now – Mar 13): Submit proposal. Finalize gold standard trajectory structure and annotation schema.

Week 2 (Mar 13–20): Author 10–15 researcher-written gold standard trajectories. Begin friction scoring pipeline.

Weeks 3–4 (Mar 20 – Apr 3): Scale trajectory generation with LLM assistance. Generate pairwise preference pairs. Begin reward model training on gold examples.

Weeks 5–6 (Apr 3–17): Run data ablations. Validate annotation schema with CBI practitioners. Iterate on AARC label operationalization based on feedback.

Week 7 (Apr 17 – May 6): Write up results, prepare 8–10 minute presentation.