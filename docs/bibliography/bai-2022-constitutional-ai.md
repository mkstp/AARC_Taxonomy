---
schema: bibliography-entry/1.0
---

# Bai, Y., et al. (2022). Constitutional AI: Harmlessness from AI feedback.

## Citation

Bai, Y., Kadavath, S., Kundu, S., Askell, A., Kernion, J., Jones, A., Chen, A., Goldie, A., Mirhoseini, A., McKinnon, C., Chen, C., Olsson, C., Olah, C., Hernandez, D., Drain, D., Ganguli, D., Li, D., Tran-Johnson, E., Perez, E., & Kaplan, J. (2022). *Constitutional AI: Harmlessness from AI feedback* (arXiv:2212.08073). arXiv.

## Abstract

As AI systems become more capable, we would like to enlist their help to supervise other AIs. We experiment with methods for training a harmless AI assistant through self-improvement, without any human labels identifying harmful outputs. The only human oversight is provided through a list of rules or principles, and so we refer to the method as 'Constitutional AI'. The process involves both a supervised learning and a reinforcement learning phase. In the supervised phase we sample from an initial model, then generate self-critiques and revisions, and then finetune the original model on revised responses. In the RL phase, we sample from the finetuned model, use a model to evaluate which of the two samples is better, and then train a preference model from this dataset of AI preferences. We then train with RL using the preference model as the reward signal, i.e. we use 'RL from AI Feedback' (RLAIF). As a result we are able to train a harmless but non-evasive AI assistant that engages with harmful queries by explaining its objections to them. Both the SL and RL methods can leverage chain-of-thought style reasoning to improve the human-judged performance and transparency of AI decision making. These methods make it possible to control AI behavior more precisely and with far fewer human labels.

## Project Relevance

Bai et al. establish a two-phase RLAIF training procedure in which a language model critiques and revises its own responses to adversarial prompts against a fixed set of constitutional principles, then trains a preference model on those revisions. This is the primary published account of an RL-based training regime in which managing harmful or conflictual dialogue is an explicit training objective, making it a foundational precedent for the claim that RL-based policy optimization can be applied to the alignment of harmful and adversarial dialogue. *Note: arXiv preprint; widely cited (3,000+ citations) but not published in a peer-reviewed venue. Characterize accordingly in the writeup.*
