---
schema: bibliography-entry/1.0
---

# Ouyang, L., et al. (2022). Training language models to follow instructions with human feedback.

## Citation

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., Schulman, J., Hilton, J., Kelton, F., Miller, L., Simens, M., Askell, A., Welinder, P., Christiano, P., Leike, J., & Lowe, R. (2022). Training language models to follow instructions with human feedback. *Advances in Neural Information Processing Systems*, *35*.

## Abstract

Making language models bigger does not inherently make them better at following a user's intent. For example, large language models can generate outputs that are untruthful, toxic, or simply not helpful to the user. In other words, these models are not aligned with their users. In this paper, we show an avenue for aligning language models with user intent on a wide range of tasks by fine-tuning with human feedback. Starting with a set of labeler-written prompts and prompts submitted through the OpenAI API, we collect a dataset of labeler demonstrations of the desired model behavior, which we use to fine-tune GPT-3 using supervised learning. We then collect a dataset of rankings of model outputs, which we use to further fine-tune this supervised model using reinforcement learning from human feedback. We call the resulting models InstructGPT. In human evaluations on our prompt distribution, outputs from the 1.3B parameter InstructGPT model are preferred to outputs from the 175B GPT-3, despite having 100x fewer parameters. Moreover, InstructGPT models show improvements in truthfulness and reductions in toxic output generation while having minimal performance regressions on public NLP datasets. Even though InstructGPT still makes simple mistakes, our results show that fine-tuning with human feedback is a promising direction for aligning language models with human intent.

## Project Relevance

Ouyang et al. establish the three-stage RLHF pipeline — supervised fine-tuning, reward model training from pairwise human preference labels, and PPO-based policy optimization — and provide the most detailed published account of how a reward model is implemented as a scalar-output language model head trained to predict human preferences. This is the canonical methodological reference for reward model architecture and training, and the direct precedent for the project's approach of training LLaMA 8B on pairwise intervention preference pairs. The paper also demonstrates that RLHF-trained models outperform supervised fine-tuning baselines on behavioral alignment tasks, motivating the project's framing of intervention quality as a preference learning problem.
