# Metrics Explanation for TruthLens Thesis

## Binary Classification Metrics (Phase 1: Extraction)

### Confusion Matrix
|                     | LLM Predicted: Yes* | LLM Predicted: No* |
|---------------------|---------------------|---------------------|
| Actually: Yes*      | TP (True Positives) | FN (False Negatives)|
| Actually: No*       | FP (False Positives)| TN (True Negatives) |

*Yes = LLM detected 1+ claims, No = LLM detected 0 claims

### Theory
- **Accuracy** = (TP + TN) / (TP + TN + FP + FN) - Overall correctness
- **Precision** = TP / (TP + FP) - Of all "positive" predictions, how many were correct?
- **Recall** = TP / (TP + FN) - Of all actual positives, how many did we find?
- **F1-Score** = 2 × (Precision × Recall) / (Precision + Recall) - Balanced metric

### Example (GPT-4 extracting from 100 sentences):
|                     | GPT Predicted: Has Claims | GPT Predicted: No Claims |
|---------------------|---------------------------|--------------------------|
| Actually: Has Claims| 65 (TP)                   | 5 (FN)                   |
| Actually: No Claims | 10 (FP)                   | 20 (TN)                  |

### Metrics Calculations
- **Accuracy** = (65 + 20) / (65 + 20 + 10 + 5) = 85%
  - "Overall, GPT correctly identified 85% of sentences"
- **Precision** = 65 / (65 + 10) = 86.7%
  - "Of sentences GPT said had claims, 86.7% actually did"
- **Recall** = 65 / (65 + 5) = 92.9%
  - "Of sentences that actually had claims, GPT found 92.9%"
- **F1-Score** = 2 × (0.867 × 0.929) / (0.867 + 0.929) = 89.7%
  - "Harmonic average of precision and recall"

## Multi-class Classification Metrics (Phase 2: Verification)

### Example (GPT-4 verifying 100 claims):
|                     | GPT Predicted: Supported | GPT Predicted: Refuted |
|---------------------|--------------------------|------------------------|
| Actually: Supported | 45 (TP)                  | 15 (FN)                |
| Actually: Refuted   | 10 (FP)                  | 30 (TN)                |

### Per-class Metrics
- **Precision for Supported** = 45 / (45 + 10) = 81.8%
  - "Of all claims GPT said were Supported, 81.8% were actually Supported"
- **Recall for Supported** = 45 / (45 + 15) = 75%
  - "Of all claims that were actually Supported, GPT found 75% of them"
- **Precision for Refuted** = 30 / (30 + 15) = 66.7%
  - "Of all claims GPT said were Refuted, 66.7% were actually Refuted"
- **Recall for Refuted** = 30 / (30 + 10) = 75%
  - "Of all claims that were actually Refuted, GPT found 75% of them"

### Key Differences
- **Precision** = "Of the things I said were X, how many were actually X?"
- **Recall** = "Of the things that were actually X, how many did I find?"

### Other Metrics
- **Macro-F1** = Average of F1-scores for all classes
- **Accuracy** = Overall percentage correct: (45 + 30) / 100 = 75%