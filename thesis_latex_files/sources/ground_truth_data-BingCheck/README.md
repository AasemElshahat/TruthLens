---
license: cdla-permissive-2.0
language:
- en
task_categories:
- text-classification
---

# Dataset Card

## Dataset Overview

This dataset is associated with the paper [Towards Effective Extraction and Evaluation of Factual Claims](https://arxiv.org/pdf/2502.10855) by Dasha Metropolitansky and Jonathan Larson, accepted to the ACL 2025 Main Conference. See also our [video](https://www.youtube.com/watch?v=WTs-Ipt0k-M) and [blog post](https://www.microsoft.com/en-us/research/blog/claimify-extracting-high-quality-claims-from-language-model-outputs/). 
 
The dataset contains 6,490 sentences, each annotated with a binary label indicating whether it contains a verifiable factual claim. These sentences were extracted from the 396 answers in the [BingCheck dataset](https://github.com/Miaoranmmm/SelfChecker/tree/main/bingcheck) (Li et al., 2024), which contains long-form responses by a commercial search assistant to questions spanning a wide range of topics.
 
59% of sentences are labeled as containing a verifiable factual claim. Note that this proportion differs slightly from the number reported in the paper (63%) because, as explained in Appendix F, certain sentences were excluded from our analysis.

## Dataset Structure

The dataset has the following columns:
- `answer_id` *(string)* – unique ID for the answer in BingCheck
- `question` *(string)* – original BingCheck question
- `sentence_id` *(int)* – index of the sentence within the answer
- `sentence` *(string)* – sentence text
- `contains_factual_claim` *(bool)* – True if the sentence contains a verifiable factual claim; otherwise, False

The following is an example row:
```
{
  "answer_id": "c910f021-48e2-44e0-a3fa-3552eaacf5b2",
  "question": "What inspired the invention of the first artificial heart?",
  "sentence_id": 3,
  "sentence": "The first patient to receive the Jarvik-7 was **Barney Clark**, a dentist from Seattle, who survived for 112 days after the implantation[^2^].",
  "contains_factual_claim": True
}
```

## Dataset Creation

To divide answers into sentences, we first split on newline characters, then applied NLTK’s sentence tokenizer. Annotation was performed by three employees of Microsoft Research (two of whom were not involved in the project beyond contributing annotations), following the procedure and guidelines detailed in Appendix C of the paper.

## Citation

If you use this dataset, please cite:

```
@inproceedings{metropolitansky-larson-2025-towards,
    title = "Towards Effective Extraction and Evaluation of Factual Claims",
    author = "Metropolitansky, Dasha  and
      Larson, Jonathan",
    editor = "Che, Wanxiang  and
      Nabende, Joyce  and
      Shutova, Ekaterina  and
      Pilehvar, Mohammad Taher",
    booktitle = "Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
    month = jul,
    year = "2025",
    address = "Vienna, Austria",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.acl-long.348/",
    doi = "10.18653/v1/2025.acl-long.348",
    pages = "6996--7045",
    ISBN = "979-8-89176-251-0",
}
```

## Ethics

All data annotation was conducted with the informed consent of the study participants. No personally identifiable information is included.