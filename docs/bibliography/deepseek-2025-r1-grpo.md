---
schema: bibliography-entry/1.0
---

# DeepSeek-AI. (2025). DeepSeek-R1: Incentivizing reasoning capability in LLMs via reinforcement learning.

## Citation

DeepSeek-AI. (2025). *DeepSeek-R1: Incentivizing reasoning capability in LLMs via reinforcement learning* (arXiv:2501.12948). arXiv.

## Abstract

General reasoning represents a long-standing and formidable challenge in artificial intelligence. Recent breakthroughs, exemplified by large language models (LLMs) and chain-of-thought prompting, have achieved considerable success on foundational reasoning tasks. However, this success is heavily contingent upon extensive human-annotated demonstrations, and models' capabilities are still insufficient for more complex problems. Here we show that the reasoning abilities of LLMs can be incentivized through pure reinforcement learning (RL), obviating the need for human-labeled reasoning trajectories. The proposed RL framework facilitates the emergent development of advanced reasoning patterns, such as self-reflection, verification, and dynamic strategy adaptation. Consequently, the trained model achieves superior performance on verifiable tasks such as mathematics, coding competitions, and STEM fields, surpassing its counterparts trained via conventional supervised learning on human demonstrations. Moreover, the emergent reasoning patterns exhibited by these large-scale models can be systematically harnessed to guide and enhance the reasoning capabilities of smaller models.

## Project Relevance

DeepSeek-AI introduce GRPO (Group Relative Policy Optimization), a reinforcement learning algorithm in which the reward signal for each response is computed relative to the score distribution of a group of N simultaneously generated responses rather than against a fixed scalar baseline. This eliminates the need for a separate critic model and produces a more stable training signal by grounding reward estimation in within-group comparison. GRPO is the direct methodological precedent for this project's group-ranking annotation structure: generating N candidate interventions at each deficit-present window and ranking them by aggregate AARC component score follows the same relative-comparison logic. *Note: arXiv preprint (January 2025); verify peer-review status before submission.*
