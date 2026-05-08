---
schema: bibliography-entry/1.0
---

# Ahmad, Z., et al. (2023). INA: An integrative approach for enhancing negotiation strategies with reward-based dialogue system.

## Citation

Ahmad, Z., Saurabh, S., Menon, V., Ekbal, A., Ramnani, R., & Maitra, A. (2023). INA: An integrative approach for enhancing negotiation strategies with reward-based dialogue system. In *Findings of the Association for Computational Linguistics: EMNLP 2023* (pp. 2447–2458). Association for Computational Linguistics.

## Abstract

In this paper, we propose a novel negotiation dialogue agent designed for the online marketplace. Our agent is integrative in nature i.e, it possesses the capability to negotiate on price as well as other factors, such as the addition or removal of items from a deal bundle, thereby offering a more flexible and comprehensive negotiation experience. We create a new dataset called Integrative Negotiation Dataset (IND) to enable this functionality. For this dataset creation, we introduce a new semi-automated data creation method, which combines defining negotiation intents, actions, and intent-action simulation between users and the agent to generate potential dialogue flows. Finally, the prompting of GPT-J, a state-of-the-art language model, is done to generate dialogues for a given intent, with a human-in-the-loop process for post-editing and refining minor errors to ensure high data quality. We employ a set of novel rewards, specifically tailored for the negotiation task to train our Negotiation Agent, termed as the Integrative Negotiation Agent (INA). These rewards incentivize the chatbot to learn effective negotiation strategies that can adapt to various contextual requirements and price proposals. By leveraging the IND, we train our model and conduct experiments to evaluate the effectiveness of our reward-based dialogue system for negotiation. Our results demonstrate that the proposed approach and reward system significantly enhance the agent's negotiation capabilities. The INA successfully engages in integrative negotiations, displaying the ability to dynamically adjust prices and negotiate the inclusion or exclusion of items in a bundle deal

## Project Relevance

Ahmad et al. train a reward-based dialogue agent for multi-issue integrative negotiation using task-specific reward functions, demonstrating that reward signal design — specifying what counts as a better versus worse response in a conflictual exchange — is a central methodological challenge in building dialogue systems capable of managing adversarial interaction. The multi-issue framing is structurally parallel to the AARC model's multi-dimensional treatment of conflict: both frameworks require the agent to manage competing objectives simultaneously rather than optimizing a single scalar outcome. *Verify: page range via ACL Anthology (2023.findings-emnlp.166) before submission.*
