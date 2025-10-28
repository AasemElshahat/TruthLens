# TruthLens Evaluation Plan
**Single Source of Truth for Bachelor Thesis Evaluation**

## Objective
Compare the fact-checking performance of three LLMs: Google Gemini, DeepSeek, and OpenAI GPT-4, using a novel, manually-annotated dataset sampled from the BingCheck ground truth dataset.

## Research Questions
1. **Claim Extraction**: Which LLM most accurately identifies verifiable factual claims from text?
2. **Claim Verification**: Which LLM most accurately assesses the veracity of claims?
3. **Qualitative Analysis**: What are the common failure modes for each LLM?

## Evaluation Framework

### 1. LLM Providers to Compare
- **OpenAI GPT-4** (Baseline)
- **Google Gemini** (e.g., `gemini-pro`)
- **DeepSeek** (e.g., `deepseek-chat`)

### 2. Dataset Creation
- **Source**: BingCheck dataset (6,490 sentences with factual claim annotations)
- **Sampling**: Randomly sample 150 sentences to create `my_thesis_dataset.csv`
- **Manual Annotation**: For sentences with `contains_factual_claim=True`, manually research and add `ground_truth_verdict` column with labels:
  - **"Supported"**: Claim is factually correct
  - **"Refuted"**: Claim is factually incorrect
  - **"Insufficient Information"**: Cannot verify with available evidence

### 3. Experimental Pipeline

#### Phase 1: Claim Extraction Evaluation
Run each LLM through the claim extractor on all 150 sentences:
- Input: Raw sentences from `my_thesis_dataset.csv`
- Output: Structured JSON with `factual_claims` and `non_factual_sentences` lists
- Storage: Save full JSON output in `my_thesis_results.csv`

#### Phase 2: Claim Verification Evaluation  
Run extracted factual claims through claim verifier with each LLM:
- Input: Verified factual claims only
- Output: Structured JSON with `verdict` and `reason`
- Storage: Save full JSON output in `my_thesis_results.csv`

### 4. Metrics Collection

#### 4.1 Claim Extraction Metrics
For each LLM, calculate per-sentence classification using scikit-learn:

**Binary Classification Metrics:**
- **Accuracy** = (TP + TN) / (TP + TN + FP + FN)
- **Precision** = TP / (TP + FP) 
- **Recall** = TP / (TP + FN)
- **F1-Score** = 2 × (Precision × Recall) / (Precision + Recall)

Where:
- TP: Sentences correctly identified as containing factual claims
- TN: Sentences correctly identified as not containing factual claims
- FP: Sentences incorrectly identified as containing factual claims
- FN: Sentences incorrectly identified as not containing factual claims

#### 4.2 Claim Verification Metrics
For each LLM, calculate verification accuracy using scikit-learn:

**Multi-class Classification Metrics:**
- **Accuracy** = Correct verifications / Total verifications
- **Per-class Precision/Recall/F1** for each verdict type (Supported/Refuted/Insufficient)
- **Macro-F1** across all verdict classes

### 5. Implementation Steps

1. **Week 1**: Setup environment and create `my_thesis_dataset.csv` (150 random sentences)
2. **Weeks 2-3**: Manual annotation of `ground_truth_verdict` column
3. **Week 4**: Modify `apps/agent/utils/llm.py` to support all three LLM providers
4. **Week 5**: Create `run_my_thesis.py` benchmark runner script
5. **Week 6**: Execute experiments and generate `my_thesis_results.csv`
6. **Week 7**: Create `analyze_results.py` for metric calculation and visualization
7. **Week 8**: Write thesis chapters based on results

### 6. Data Storage & Analysis

#### 6.1 Data Storage
All results stored in `my_thesis_results.csv` with:
- Original 150 sentences and ground truth labels
- 6 columns (2 phases × 3 LLMs) with full JSON outputs

#### 6.2 Data Analysis
Script `analyze_results.py` performs:
- **Quantitative Analysis**: Calculate all metrics using scikit-learn
- **Visualization**: Generate bar charts comparing LLM performance
- **Qualitative Analysis**: Examine `reason` fields to identify failure patterns

### 7. Expected Deliverables

- **Code**: 
  - Modified `apps/agent/utils/llm.py` supporting all 3 providers
  - `run_my_thesis.py` benchmark runner
  - `analyze_results.py` analysis script
- **Data**:
  - `my_thesis_dataset.csv`: 150-sentence annotated dataset
  - `my_thesis_results.csv`: Master results file with all outputs
- **Thesis Document**: 
  - Methodology chapter describing the agents and dataset creation
  - Results chapter with charts and tables
  - Discussion chapter analyzing qualitative findings
  - Conclusion and limitations chapter

### 8. Success Criteria

- All three LLMs successfully integrated and tested
- Comprehensive metrics calculated with statistical validity using scikit-learn
- Clear performance ranking with visual comparisons
- Qualitative error analysis identifying distinct failure modes
- Reproducible evaluation framework documented
- Complete thesis document with all required chapters