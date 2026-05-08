---
schema: bibliography-entry/1.0
---

# Wirth, C., et al. (2017). A survey of preference-based reinforcement learning methods.

## Citation

Wirth, C., Akrour, R., Neumann, G., & Fürnkranz, J. (2017). A survey of preference-based reinforcement learning methods. *Journal of Machine Learning Research*, *18*(136), 1–46.

## Abstract

Reinforcement learning (RL) techniques optimize the accumulated long-term reward of a suitably chosen reward function. However,designing such a reward function often requires a lot of task-specific prior knowledge. The designer needs to consider different objectives that do not only influence the learned behavior but also the learning progress. To alleviate these issues, preference-based reinforcement learning algorithms (PbRL) have been proposed that can directly learn from an expert’s preferences instead of a hand-designed numeric reward. PbRL has gained traction in recent years due to its ability to resolve the reward shaping problem, its ability to learn from non numeric rewards and the possibility to reduce the dependence on expert knowledge. We provide a unified framework for PbRL that describes the task formally and points out the different design principles that affect
the evaluation task for the human as well as the computational complexity. The design principles include the type of feedback that is assumed, the representation that is learned to capture the preferences, the optimization problem that has to be solved as well as how
the exploration/exploitation problem is tackled. Furthermore, we point out shortcomings of current algorithms, propose open research questions and briefly survey practical tasks that have been solved using PbRL.

## Project Relevance

Wirth et al. provide the primary systematic survey of preference-based reinforcement learning, covering the full methodological lineage from ordinal preference models through pairwise comparison-based reward learning. The survey situates the Bradley-Terry model, Christiano et al. (2017), and related methods within a unified taxonomic framework, and is the most appropriate citation for characterizing the general class of methods the project employs. It should be read alongside Christiano et al. and Ouyang et al. (2022), which address the LLM-specific application context that this survey predates.
