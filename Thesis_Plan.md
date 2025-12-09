# TruthLens Decoupled Evaluation Plan

**Single Source of Truth for Bachelor Thesis Evaluation**

## Objective

Compare the fact-checking performance of three LLMs: Google Gemini, DeepSeek, and OpenAI GPT-4/5, using the BingCheck ground truth dataset with a decoupled two-phase evaluation approach:

- Phase 1: Extract claims from sentences using all 3 LLMs, compare against binary ground truth to determine the most accurate extractor
- Phase 2: Use the winning extractor's claims as a benchmark, then verify these claims with all 3 LLMs to determine the most accurate verifier

## Research Questions

1. **Claim Extraction**: Which LLM most accurately identifies verifiable factual claims from text at the sentence level?
2. **Claim Verification**: Which LLM most accurately assesses the veracity of identified claims?
3. **Qualitative Analysis**: What are the common failure modes for each LLM?

## Prerequisites

Before running the evaluation, ensure you have:

1. Valid API keys in your environment:

   - `OPENAI_API_KEY` for OpenAI
   - `GOOGLE_API_KEY` for Google Gemini
   - `DEEPSEEK_API_KEY` for DeepSeek
2. Required dependencies installed (via Poetry in the agent app)

## Files Overview

- `my_thesis_dataset.csv` - The sampled dataset with 150 sentences from BingCheck, enhanced with extraction results from all 3 LLMs
- `my_thesis_benchmark_claims.csv` - Claims from winning extractor, enhanced with ground truth and verification results from all 3 LLMs
- `extraction_metrics.csv` - Phase 1 summary metrics for all LLMs
- `verification_metrics.csv` - Phase 2 summary metrics for all LLMs
- `apps/agent/scripts/create_thesis_dataset.py` - Create 150-sentence dataset from BingCheck
- `apps/agent/scripts/run_extraction_phase.py` - Run extraction for all LLMs and append results to dataset
- `apps/agent/scripts/run_verification_phase.py` - Run verification for all LLMs and append results to benchmark claims
- `apps/agent/scripts/create_benchmark_claims.py` - Create benchmark claims from winning extractor
- `apps/agent/scripts/analyze_extraction.py` - Analyze extraction results and find winner
- `apps/agent/scripts/analyze_verification.py` - Analyze verification results against ground truth

## Experimental Pipeline

### Phase 1: Claim Extraction Evaluation (Decoupled)

Run each LLM through the claim extractor on all 150 sentences:

- Input: Raw sentences from `my_thesis_dataset.csv`
- Output: Extracted claims per LLM per sentence
- Process: Append extraction results directly to `my_thesis_dataset.csv`
- Evaluation: Compare each LLM's extraction (1+ claims vs 0 claims) against BingCheck binary ground truth
- **Script**: `run_extraction_phase.py`
- **Output**: Enhanced `my_thesis_dataset.csv` with extraction results

### Phase 2A: Benchmark Creation

- Input: Enhanced `my_thesis_dataset.csv` with extraction results
- Process: Analyze to determine which LLM was most accurate at claim extraction
- Output: `my_thesis_benchmark_claims.csv` containing only the claims from the winning extractor
- **Script**: `create_benchmark_claims.py` or `analyze_extraction.py`

### Phase 2B: Manual Annotation (Manual Task)

- Input: `my_thesis_benchmark_claims.csv`
- Process: Annotate each claim with ground truth verdicts
- Add `ground_truth_verdict` column with labels:
  - **"Supported"**: Claim is factually correct
  - **"Refuted"**: Claim is factually incorrect
- Output: `my_thesis_benchmark_claims.csv` with complete ground truth

### Phase 2C: Claim Verification Evaluation (Decoupled)

Run the claim verifier for ALL 3 LLMs on the standardized set of claims:

- Input: Claims from `my_thesis_benchmark_claims.csv` (fair benchmark for all 3 LLMs)
- Process: Append verification results directly to `my_thesis_benchmark_claims.csv`
- Output: Structured results with `verdict` and `reasoning` per LLM added to the same file
- Evaluation: Compare against your manual ground truth annotations
- **Script**: `run_verification_phase.py`
- **Output File**: Enhanced `my_thesis_benchmark_claims.csv` with verification results

### Phase 3: Analysis and Comparison

- Compare extraction performance across all LLMs
- Determine which LLM was most accurate for extraction
- Compare verification performance against manual ground truth
- Final ranking of LLMs for each task

## Output File Structures

### `my_thesis_dataset.csv` (Enhanced with extraction results):

- `sentence_id`, `sentence`, `binary_ground_truth`
- `gpt4_extracted_claims_json`: JSON array of extracted claims from GPT-4
- `gpt4_binary_result`: True/False if GPT-4 extracted 1+ claims
- `gpt4_num_claims`: Number of claims extracted by GPT-4
- `gemini_extracted_claims_json`: JSON array of extracted claims from Gemini
- `gemini_binary_result`: True/False if Gemini extracted 1+ claims
- `gemini_num_claims`: Number of claims extracted by Gemini
- `deepseek_extracted_claims_json`: JSON array of extracted claims from DeepSeek
- `deepseek_binary_result`: True/False if DeepSeek extracted 1+ claims
- `deepseek_num_claims`: Number of claims extracted by DeepSeek

### `my_thesis_benchmark_claims.csv` (Enhanced with verification results):

- `claim_id`: Sequential ID for each extracted claim
- `original_sentence_id`: Reference to original sentence
- `original_sentence`: Original sentence text
- `validated_claim_object`: Complete ValidatedClaim object as JSON string (for processing)
- `claim_text`: Individual claim text from winning LLM
- `ground_truth_verdict`: The manual annotation (Supported/Refuted)
- `gpt4_verdict`, `gpt4_reasoning`
- `gemini_verdict`, `gemini_reasoning`
- `deepseek_verdict`, `deepseek_reasoning`

## Metrics Collection

### Phase 1: Claim Extraction Metrics

For each LLM, calculate per-sentence classification using scikit-learn against BingCheck ground truth:

**Binary Classification Metrics (The "Finder" Score):**

- **Accuracy** = (TP + TN) / (TP + TN + FP + FN) - Overall correctness
- **Precision (Positive Class)** = TP / (TP + FP) - Of all "positive" predictions, how many were correct?
- **Recall (Positive Class)** = TP / (TP + FN) - Of all actual positives, how many did we find?
- **F1-Score (Positive Class)** = 2 × (Precision × Recall) / (Precision + Recall) - Balanced metric for positive class
- **Precision (Negative Class)** = TN / (TN + FN) - Of all "negative" predictions, how many were correct? [Same as NPV - Negative Predictive Value]
- **Recall (Negative Class)** = TN / (TN + FP) - Of all actual negatives, how many did we find?
- **F1-Score (Negative Class)** = 2 × (Precision_Neg × Recall_Neg) / (Precision_Neg + Recall_Neg) - Balanced metric for negative class

Where:

- TP: Sentences correctly identified as containing factual claims
- TN: Sentences correctly identified as not containing factual claims
- FP: Sentences incorrectly identified as containing factual claims
- FN: Sentences incorrectly identified as not containing factual claims

**Optional Enhancement - Claim-Level Entailment (The "Creator" Score):**

As an additional quality metric, we may optionally calculate an Entailment Rate to evaluate the faithfulness of extracted claims to the source text:

- **Entailment Rate** = (Total claims judged as entailed by a "Judge" LLM) / (Total claims extracted by that LLM)
- This metric evaluates: "When an LLM does create claims, are they faithful to the source text?"
- Implementation: Use a powerful "Judge" LLM (e.g., GPT-4) to determine if each extracted claim is logically entailed by the original sentence
- This provides a quality measure beyond the simple binary classification, addressing whether extracted claims maintain fidelity to the source text

### Phase 2: Claim Verification Metrics

For each LLM, calculate verification accuracy against manual annotations using scikit-learn:

**Multi-class Classification Metrics:**

- **Accuracy** = Correct verifications / Total verifications
- **Per-class Precision/Recall/F1** for each verdict type (Supported/Refuted)
- **Macro-F1** across all verdict classes

## Implementation Workflow

### Step 1: Dataset Preparation

```bash
cd apps/agent
poetry run python scripts/create_thesis_dataset.py
```

Creates `my_thesis_dataset.csv` with 150 sampled sentences and BingCheck ground truth.

### Step 2: Phase 1 - Extraction Comparison

```bash
poetry run python scripts/run_extraction_phase.py
```

Appends extraction results for all 3 LLMs directly to `my_thesis_dataset.csv`.

### Step 3: Phase 1 - Analysis

```bash
poetry run python scripts/analyze_extraction.py
```

Analyzes `my_thesis_dataset.csv` to create `extraction_metrics.csv` with performance metrics for all 3 LLMs.

### Step 4: Winner Determination

Analyze `extraction_metrics.csv` to determine which LLM performed best on extraction.

### Step 5: Phase 2A - Benchmark Creation

```bash
poetry run python scripts/create_benchmark_claims.py
```

Creates `my_thesis_benchmark_claims.csv` containing only the claims from the winning extractor along with the ValidatedClaim object as JSON string to feed the verification agent later.

### Step 6: Phase 2B - Manual Annotation

Manually add `ground_truth_verdict` to `my_thesis_benchmark_claims.csv`.

### Step 7: Phase 2C - Verification Comparison

```bash
poetry run python scripts/run_verification_phase.py
```

Appends verification results for all 3 LLMs directly to `my_thesis_benchmark_claims.csv`.

### Step 8: Phase 2 - Analysis

```bash
poetry run python scripts/analyze_verification.py
```

Analyzes `my_thesis_benchmark_claims.csv` to create `verification_metrics.csv` with performance metrics for all 3 LLMs.

## Expected Deliverables

- **Code**:
  - All new scripts: `run_extraction_phase.py`, `run_verification_phase.py`, `create_benchmark_claims.py`, `analyze_extraction.py`, `analyze_verification.py`
  - Updated `utils/llm.py` supporting all 3 providers
- **Data**:
  - `my_thesis_dataset.csv`: 150-sentence dataset with extraction results from all 3 LLMs
  - `my_thesis_benchmark_claims.csv`: Standardized claims set with ground truth and verification results from all 3 LLMs
- **Analysis**:
  - `extraction_metrics.csv`: Phase 1 summary metrics comparing LLMs on extraction
  - `verification_metrics.csv`: Phase 2 summary metrics comparing LLMs on verification
- **Thesis Document**:
  - Methodology chapter describing the agents and decoupled evaluation approach
  - Results chapter with charts and tables
  - Discussion chapter analyzing qualitative findings
  - Conclusion and limitations chapter

## Success Criteria

- All three LLMs successfully integrated and tested in both phases
- Clear extraction winner identified with comprehensive metrics
- Fair verification comparison using standardized benchmark
- Comprehensive metrics calculated with statistical validity using scikit-learn
- Clear performance ranking with visual comparisons across both phases
- Qualitative error analysis identifying distinct failure modes per phase
- Reproducible evaluation framework documented
- Complete thesis document with all required chapters
