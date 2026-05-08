---
schema: bibliography-entry/1.0
---

# Suresh, S. K., et al. (2025). DiaSynth: Synthetic dialogue generation framework for low resource dialogue applications.

## Citation

Suresh, S. K., Mengjun, W., Pranav, T., & Chng, E. S. (2025). DiaSynth: Synthetic dialogue generation framework for low resource dialogue applications. In *Proceedings of the 2025 Annual Conference of the North American Chapter of the Association for Computational Linguistics* (pp. TBD). Association for Computational Linguistics. arXiv:2409.19020

## Abstract

The scarcity of domain-specific dialogue datasets limits the development of dialogue systems across applications. Existing research is constrained by general or niche datasets that lack sufficient scale for training dialogue systems. To address this gap, we introduce DiaSynth - a synthetic dialogue generation framework capable of generating high-quality, contextually rich dialogues across a wide range of domains. Unlike existing frameworks, DiaSynth uses Large Language Models (LLMs) and Chain of Thought (CoT) reasoning to generate dynamic, domain-specific dialogues with simulated personas and diverse conversational features. We perform our experiments by generating synthetic data using different LLMs and few-shot examples from DialogSum and SAMSum. The pretrained language models fine-tuned on the synthetic data outperform the base models by 16.47% on dialogue summarization, while the comparison between models fine-tuned on in-domain data and synthetic data shows that the synthetic data is able to capture 90.48% of the performance distribution of the in-domain data on dialogue summarization. The quality of the data generated also increases as we increase the size of LLM from 3B to 8B. These results validate DiaSynth’s potential as a robust alternative to traditional data collection methods.1 We open source the code and data generated for future research.

## Project Relevance

Suresh et al. introduce DiaSynth, a framework for generating synthetic dialogue data by conditioning LLMs on simulated personas and conversational scenarios, augmented with chain-of-thought reasoning at generation time. Their central finding — that models fine-tuned on DiaSynth-generated data outperform base models by 16.47% on dialogue summarization and capture 90.48% of the performance distribution of in-domain naturalistic data — establishes the methodological case for persona-conditioned synthetic dialogue as a viable substitute for naturalistic corpus data in low-resource settings. The persona-scenario pipeline this project adopts for corpus construction is a direct adaptation of DiaSynth's framework to the conflict dialogue domain: character personas define psychology and activation patterns, scenario briefs specify situational stakes and relationship context, and chain-of-thought generation ensures that deficit-relevant behavior emerges from character reasoning rather than from direct deficit specification. *Note: presented at NAACL 2025; arXiv preprint 2409.19020. Verify page range and final proceedings details before submission.*
