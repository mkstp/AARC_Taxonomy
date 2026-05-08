---
schema: bibliography-entry/1.0
---

# Nie, Y., et al. (2021). I like fish, especially dolphins: Addressing contradictions in dialogue modeling.

## Citation

Nie, Y., Williamson, M., Bansal, M., Kiela, D., & Weston, J. (2021). I like fish, especially dolphins: Addressing contradictions in dialogue modeling. In *Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing* (Volume 1: Long Papers) (pp. 1699–1713). Association for Computational Linguistics. https://doi.org/10.18653/v1/2021.acl-long.134

## Abstract

To quantify how well natural language understanding models can capture consistency in a general conversation, we introduce the DialoguE COntradiction DEtection task (DECODE) and a new conversational dataset containing both human-human and human-bot contradictory dialogues. We then compare a structured utterance-based approach of using pre-trained Transformer models for contradiction detection with the typical unstructured approach. Results reveal that: (i) our newly collected dataset is notably more effective at providing supervision for the dialogue contradiction detection task than existing NLI data including those aimed to cover the dialogue domain; (ii) the structured utterance-based approach is more robust and transferable on both analysis and out-of-distribution dialogues than its unstructured counterpart. We also show that our best contradiction detection model correlates well with human judgments and further provide evidence for its usage in both automatically evaluating and improving the consistency of state-of-the-art generative chatbots.

## Project Relevance

Nie et al. introduce DECODE (DialoguE COntradiction DEtection), a task and dataset for detecting contradictions in multi-turn dialogue, and demonstrate that models trained on dialogue-native contradiction data substantially outperform models trained on standard sentence-pair NLI corpora such as SNLI and MultiNLI when applied to conversational contradiction. This establishes that contradiction detection in dialogue is methodologically distinct from general-purpose NLI — a distinction FPO's contradiction submodel must reckon with — and is the appropriate peer-reviewed precedent for applying NLI-based contradiction detection to turn-level dialogue analysis.
