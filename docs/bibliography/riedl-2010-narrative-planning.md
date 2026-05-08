---
schema: bibliography-entry/1.0
---

# Riedl, M. O., & Young, R. M. (2010). Narrative planning: Balancing plot and character.

## Citation

Riedl, M. O., & Young, R. M. (2010). Narrative planning: Balancing plot and character. *Journal of Artificial Intelligence Research*, *39*, 459–540. https://doi.org/10.1613/jair.2989

## Abstract

[PENDING — fetch verbatim from JAIR at https://www.jair.org/index.php/jair/article/view/10669. Working summary from journal record: The authors present the Intent-based Partial Order Causal Link (IPOCL) planner, a narrative planning algorithm that generates story sequences satisfying both author-level plot goals and character-level intentionality constraints. In empirical evaluation, narratives produced by IPOCL were shown to support audience comprehension of character intentions more reliably than those produced by conventional partial-order planners, supporting the claim that explicitly balancing plot-level and character-level goals yields more coherent and believable narrative output.]

## Project Relevance

Provides the direct computational precedent for the three-LLM architecture: two persona-playing generators pursuing character-level goals, supervised by a director-LLM that enforces scene-level coherence and authenticity. Riedl and Young formalise exactly this tension — author/plot goals versus character-level intentionality — and demonstrate empirically that an architecture which reasons about both levels produces more coherent output than single-level generation. Their result licenses the design choice to separate the director's concerns (dialogue trajectory, fidelity to persona profile) from the personas' concerns (in-character response to the current turn), rather than collapsing them into a single generator. The director's role in the present corpus pipeline is analogous to IPOCL's author-level planner: to catch drift away from the character's psychological profile — most commonly, premature conciliation driven by the underlying model's RLHF training — and restore behavioral fidelity. *Verification: peer-reviewed, open-access journal (JAIR); DOI 10.1613/jair.2989 resolves. Verbatim abstract to be fetched from JAIR before submission.*
