---
schema: bibliography-entry/1.0
---

# Artstein, R., & Poesio, M. (2008). Inter-coder agreement for computational linguistics.

## Citation

Artstein, R., & Poesio, M. (2008). Inter-coder agreement for computational linguistics. *Computational Linguistics*, *34*(4), 555–596.

## Abstract

The statistical measurement of agreement—the most commonly used form of which is inter-coder agreement (also called inter-rater reliability), i.e., consistency of scoring among two or more coders for the same units of analysis—is important in a number of fields, e.g., content analysis, education, computational linguistics, sports. We propose Sklar’s Omega, a Gaussian copula-based framework for measuring not only inter-coder agreement but also intra-coder agreement, inter-method agreement, and agreement relative to a gold standard. We demonstrate the efficacy and advantages of our approach by applying both Sklar’s Omega and Krippendorff’s Alpha (a well-established nonparametric agreement coefficient) to simulated data, to nominal data previously analyzed by Krippendorff, and to continuous data from an imaging study of hip cartilage in femoroacetabular impingement. Application of our proposed methodology is supported by our open-source R package, sklarsomega, which is available for download from the Comprehensive R Archive Network. The package permits users to apply the Omega methodology to nominal scores, ordinal scores, percentages, counts, amounts (i.e., non-negative real numbers), and balances (i.e., any real number); and can accommodate any number of units, any number of coders, and missingness. Classical inference is available for all levels of measurement while Bayesian inference is available for continuous outcomes only.

## Project Relevance

Artstein and Poesio survey the full range of inter-annotator agreement statistics used in computational linguistics — Cohen's kappa, Krippendorff's alpha, Scott's pi, and related measures — and establish the conditions under which each is appropriate. The paper directly addresses the trade-offs between kappa and alpha for nominal categorical coding tasks with multiple annotators, which is the methodological decision this project faces in designing its reliability protocol for the AARC/FPO turn-level schema. It is the standard reference for any NLP methodology section that must justify its choice of agreement statistic. *Verify: DOI and page range via ACL Anthology (J08-4004) before submission.*
