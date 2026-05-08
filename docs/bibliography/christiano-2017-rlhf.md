---
schema: bibliography-entry/1.0
---

# Christiano, P., et al. (2017). Deep reinforcement learning from human preferences.

## Citation

Christiano, P., Leike, J., Brown, T. B., Martic, M., Legg, S., & Amodei, D. (2017). Deep reinforcement learning from human preferences. *Advances in Neural Information Processing Systems*, *30*.

## Abstract

For sophisticated reinforcement learning (RL) systems to interact usefully with real-world environments, we need to communicate complex goals to these systems. In this work, we explore goals defined in terms of (non-expert) human preferences between pairs of trajectory segments. We show that this approach can effectively solve complex RL tasks without access to the reward function, including Atari games and simulated robot locomotion, while providing feedback on less than one percent of our agent's interactions with the environment. This reduces the cost of human oversight far enough that it can be practically applied to state-of-the-art RL systems. To demonstrate the flexibility of our approach, we show that we can successfully train complex novel behaviors with about an hour of human time. These behaviors and environments are considerably more complex than any that have been previously learned from human feedback.

## Project Relevance

Christiano et al. establish the empirical RLHF training procedure in which a reward model is fitted to binary pairwise human preference judgments using a cross-entropy loss over Bradley-Terry-style comparisons, demonstrating that the resulting reward signal can supervise policy learning without requiring access to an explicit reward function. The paper introduces the pairwise preference annotation paradigm — human raters compare pairs of behavioral trajectories and select the preferred one — that this project applies at the dialogue turn level to distinguish better from worse interventions at high-friction moments. It is the foundational methodological reference for the project's pairwise preference construction and reward model training approach.
