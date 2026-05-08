---
schema: bibliography-entry/1.0
---

# Zhang, T., et al. (2024). Strength lies in differences! Improving strategy planning for non-collaborative dialogues via diversified user simulation.

## Citation

Zhang, T., Huang, C., Deng, Y., Liang, H., Liu, J., Wen, Z., Lei, W., & Chua, T.-S. (2024). Strength lies in differences! Improving strategy planning for non-collaborative dialogues via diversified user simulation. In *Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing* (pp. 424–444). Association for Computational Linguistics.

## Abstract

We investigate non-collaborative dialogue agents, which are expected to engage in strategic conversations with diverse users, for securing a mutual agreement that leans favorably towards the system’s objectives. This poses two main challenges for existing dialogue agents: 1) The inability to integrate user-specific characteristics into the strategic planning, and 2) The difficulty of training strategic planners that
can be generalized to diverse users. To address these challenges, we propose TRIP to enhance the capability in tailored strategic planning, incorporating a user-aware strategic planning module and a population-based training paradigm. Through experiments on benchmark
non-collaborative dialogue tasks, we demonstrate the effectiveness of TRIP in catering to diverse users.

## Project Relevance

Zhang et al. demonstrate that LLM-based dialogue agents trained on homogeneous user simulations fail to generalize across diverse adversarial interlocutor types in non-collaborative tasks, and that a population-based training paradigm — diversifying the simulated user distribution during training — is necessary to produce robust strategic behavior in negotiation and persuasion dialogues. The finding that standard prompted LLMs often fail to generalize robustly in non-collaborative interaction, and that RL-style training is required, supports the argument that dialogue friction management is an active research problem not yet resolved by prompted models alone. *Verify: page range via ACL Anthology (2024.emnlp-main.26) before submission.*
