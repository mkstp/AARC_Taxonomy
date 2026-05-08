---
schema: bibliography-entry/1.0
---

# He, H., et al. (2018). Decoupling strategy and generation in negotiation dialogues.

## Citation

He, H., Chen, D., Balakrishnan, A., & Liang, P. (2018). Decoupling strategy and generation in negotiation dialogues. In *Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing* (pp. 2333–2343). Association for Computational Linguistics.

## Abstract

We consider negotiation settings in which two agents use natural language to bargain on goods. Agents need to decide on both high-level strategy (e.g., proposing $50) and the execution of that strategy (e.g., generating “The bike is brand new. Selling for just $50!”). Recent work on negotiation trains neural models, but their end-to-end nature makes it hard to control their strategy, and reinforcement learning tends to lead to degenerate solutions. In this paper, we propose a modular approach based on coarse dialogue acts (e.g., propose(price=50)) that decouples strategy and generation. We show that we can flexibly set the strategy using supervised learning, reinforcement learning, or domain-specific knowledge without degeneracy, while our retrieval-based generation can maintain context-awareness and produce diverse utterances. We test our approach on the recently proposed DEALORNODEAL game, and we also collect a richer dataset based on real items on Craigslist. Human evaluation shows that our systems achieve higher task success rate and more human-like negotiation behavior than previous approaches.

## Project Relevance

He et al. introduce the CraigslistBargain dataset — a large corpus of human-human negotiation dialogues — and demonstrate that models which decouple negotiation strategy from natural language generation significantly outperform generation-only baselines. The paper's central finding — that strategic intent must be modeled independently of surface linguistic realization — directly supports the project's argument that turn-level intervention selection cannot be reduced to detection of surface friction signals alone. The corpus also establishes a methodological precedent for constructing conflict dialogue datasets from naturalistic human-human interaction, providing a comparison point for the project's synthetic corpus construction approach.
