---
schema: bibliography-entry/1.0
---

# Hong, J., et al. (2024). Interactive dialogue agents via reinforcement learning on hindsight regenerations.

## Citation

Hong, J., Lin, J., Dragan, A., & Levine, S. (2024). *Interactive dialogue agents via reinforcement learning on hindsight regenerations* (arXiv:2411.05194). arXiv.

## Abstract

Recent progress on large language models (LLMs) has enabled dialogue agents to generate highly naturalistic and plausible text. However, current LLM language generation focuses on responding accurately to questions and requests with a single effective response. In reality, many real dialogues are interactive, meaning an agent's utterances will influence their conversational partner, elicit information, or change their opinion. Accounting for how an agent can effectively steer a conversation is a crucial ability in many dialogue tasks, from healthcare to preference elicitation. Existing methods for fine-tuning dialogue agents to accomplish such tasks would rely on curating some amount of expert data. However, doing so often requires understanding the underlying cognitive processes of the conversational partner, which is a skill neither humans nor LLMs trained on human data can reliably do. Our key insight is that while LLMs may not be adept at identifying effective strategies for steering conversations a priori, or in the middle of an ongoing conversation, they can do so post-hoc, or in hindsight, after seeing how their conversational partner responds. We use this fact to rewrite and augment existing suboptimal data, and train via offline reinforcement learning (RL) an agent that outperforms both prompting and learning from unaltered human demonstrations. We apply our approach to two domains that require understanding human mental state, intelligent interaction, and persuasion: mental health support, and soliciting charitable donations. Our results in a user study with real humans show that our approach greatly outperforms existing state-of-the-art dialogue agents.

## Project Relevance

Hong et al. train dialogue agents via offline RL using hindsight-regenerated data — rewriting suboptimal responses post-hoc after observing interlocutor reactions — and apply the method to persuasion and mental health support, domains requiring the agent to manage resistance, disagreement, and emotional friction. The finding that LLMs can identify better strategies in hindsight even when they cannot identify them in real-time suggests a methodological basis for the project's approach of using LLM-generated preference pairs to supervise a reward model. *Note: arXiv preprint submitted November 2024; conference acceptance not confirmed at time of inclusion. Verify peer-review status before submission.*
