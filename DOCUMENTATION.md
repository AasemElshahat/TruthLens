# TruthLens Framework - Complete Reproduction Guide

> **A Comparative Analysis of Large Language Models (GPT-4o-mini, Gemini-2.5-Flash, DeepSeek-V3.2) for Factual Claim Extraction and Verification**

This documentation provides a complete step-by-step guide to reproduce all experiments, results, and figures from the thesis.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Prerequisites](#3-prerequisites)
4. [Environment Setup](#4-environment-setup)
5. [API Keys Configuration](#5-api-keys-configuration)
6. [Dataset Preparation](#6-dataset-preparation)
7. [Phase 1: Claim Extraction](#7-phase-1-claim-extraction)
8. [Phase 2: Claim Verification](#8-phase-2-claim-verification)
9. [Metrics Aggregation](#9-metrics-aggregation)
10. [Figure Generation](#10-figure-generation)
11. [Thesis Compilation](#11-thesis-compilation)
12. [Troubleshooting](#12-troubleshooting)
13. [Cost Estimation](#13-cost-estimation)

---

## 1. Project Overview

### 1.1 What is TruthLens?

TruthLens is a **decoupled two-phase framework** for automated fact-checking that evaluates Large Language Models (LLMs) on two distinct tasks:

| Phase             | Task               | Agent               | Methodology                               |
| ----------------- | ------------------ | ------------------- | ----------------------------------------- |
| **Phase 1** | Claim Extraction   | `claim_extractor` | Claimify (Metropolitansky & Larson, 2025) |
| **Phase 2** | Claim Verification | `claim_verifier`  | SAFE (Wei et al., 2024)                   |

### 1.2 Models Evaluated

| Model            | Provider | API Identifier             | Architecture |
| ---------------- | -------- | -------------------------- | ------------ |
| GPT-4o-mini      | OpenAI   | `gpt-4o-mini-2024-07-18` | Proprietary  |
| Gemini-2.5-Flash | Google   | `gemini-2.5-flash`       | Proprietary  |
| DeepSeek-V3.2    | DeepSeek | `deepseek-chat` (V3.2)   | Open Weights |

### 1.3 Key Research Questions

- **RQ1:** Which LLM most accurately identifies verifiable factual claims?
- **RQ2:** Which LLM most accurately assesses claim veracity using search-augmented verification?
- **RQ3:** What are the common failure modes in LLM-based fact-checking?

---

## 2. Repository Structure

```
TruthLens/
├── apps/
│   ├── agent/                      # Main Python agent codebase
│   │   ├── claim_extractor/        # Phase 1: Extraction agent
│   │   │   ├── agent.py            # LangGraph workflow definition
│   │   │   ├── prompts.py          # LLM prompts for extraction
│   │   │   ├── schemas.py          # Pydantic data models
│   │   │   ├── nodes/              # Graph nodes (selection, disambiguation, decomposition)
│   │   │   └── llm/                # LLM configuration
│   │   ├── claim_verifier/         # Phase 2: Verification agent
│   │   │   ├── agent.py            # LangGraph workflow definition
│   │   │   ├── prompts.py          # LLM prompts for verification
│   │   │   ├── schemas.py          # Pydantic data models
│   │   │   └── nodes/              # Graph nodes (search, reason, decide)
│   │   ├── search/                 # Search provider integrations (Brave, Exa, Tavily)
│   │   ├── utils/                  # Shared utilities
│   │   │   └── settings.py         # Environment configuration
│   │   ├── scripts/                # Experiment execution scripts
│   │   │   ├── create_thesis_dataset.py
│   │   │   ├── create_benchmark_claims.py
│   │   │   ├── run_extraction_phase.py
│   │   │   ├── run_verification_phase.py
│   │   │   ├── aggregate_extraction_metrics.py
│   │   │   └── aggregate_verification_metrics.py
│   │   ├── pyproject.toml          # Poetry dependencies
│   │   └── .env.example            # Environment template
│   ├── data/                       # Additional data files
│   ├── extension/                  # Browser extension prototype
│   └── web/                        # Web application
│
├── results/                        # All experiment data and outputs
│   ├── thesis_dataset_empty/       # Empty templates for reproduction
│   │   ├── my_thesis_dataset_extraction.csv      # Template for Phase 1
│   │   └── my_thesis_benchmark_claims_verification.csv  # Template for Phase 2
│   ├── thesis_datasets_with_LLM_results/  # Completed experiment data
│   │   ├── my_thesis_dataset_run1.csv     # Extraction Run 1
│   │   ├── my_thesis_dataset_run2.csv     # Extraction Run 2
│   │   ├── my_thesis_dataset_run3.csv     # Extraction Run 3
│   │   ├── my_thesis_benchmark_claims_run1.csv  # Verification Run 1
│   │   └── my_thesis_benchmark_claims_run2.csv  # Verification Run 2
│   ├── extraction/
│   │   ├── per_run/                # Per-run extraction metrics
│   │   └── aggregated/             # Aggregated extraction statistics
│   └── verification/
│       ├── per_run/                # Per-run verification metrics
│       └── aggregated/             # Aggregated verification statistics
│
├── thesis_latex_files/             # All thesis-related files
│   ├── thesis.tex                  # Main thesis document
│   ├── references.bib              # Bibliography
│   ├── diagrams-thesis.md          # Diagram descriptions
│   └── sources/                    # Source materials
│       ├── ground_truth_data-BingCheck/  # Original BingCheck dataset
│       │   ├── bingcheck.csv       # 6,490 annotated sentences
│       │   └── README.md           # Dataset documentation
│       └── *.pdf                   # Research paper PDFs (13 papers)
│
├── visualization_scripts/          # Figure generation
│   └── generate_all_figures.py
│
├── images/                         # Generated figures for thesis
│   └── results/                    # Result visualization PNGs
│
└── DOCUMENTATION.md                # This file
```

---

## 3. Prerequisites

### 3.1 System Requirements

- **Operating System:** macOS, Linux, or Windows (WSL2 recommended)
- **Python:** 3.11 or higher
- **Memory:** 8GB+ RAM recommended
- **Storage:** ~2GB for dependencies and models

### 3.2 Required Software

| Software | Version       | Purpose               |
| -------- | ------------- | --------------------- |
| Python   | ≥3.11        | Runtime               |
| Poetry   | ≥1.7         | Dependency management |
| Git      | Any           | Version control       |
| LaTeX    | TexLive 2023+ | Thesis compilation    |

### 3.3 Installing Poetry

```bash
# macOS / Linux
curl -sSL https://install.python-poetry.org | python3 -

# Verify installation
poetry --version
```

---

## 4. Environment Setup

### 4.1 Clone the Repository

```bash
git clone https://github.com/AasemElshahat/TruthLens.git
cd TruthLens
```

### 4.2 Install Python Dependencies

```bash
cd apps/agent

# Install all dependencies using Poetry
poetry install

# Activate the virtual environment
poetry shell
```

### 4.3 Verify Installation

```bash
# Check Python version
python --version  # Should be 3.11+

# Verify key packages
python -c "import langchain; import langgraph; import pandas; print('All packages installed!')"
```

---

## 5. API Keys Configuration

### 5.1 Required API Keys

You need API keys from the following providers:

| Provider               | Purpose          | Cost Model          | Get Key                                                      |
| ---------------------- | ---------------- | ------------------- | ------------------------------------------------------------ |
| **OpenAI**       | GPT-4o-mini      | Pay-per-token       | [platform.openai.com](https://platform.openai.com/api-keys)     |
| **Google AI**    | Gemini-2.5-Flash | Pay-per-token       | [aistudio.google.com](https://aistudio.google.com/apikey)       |
| **DeepSeek**     | DeepSeek-V3.2    | Pay-per-token       | [platform.deepseek.com](https://platform.deepseek.com/api_keys) |
| **Brave Search** | Web search       | Free tier available | [brave.com/search/api](https://brave.com/search/api/)           |

### 5.2 Create Environment File

```bash
cd apps/agent

# Copy the example file
cp .env.example .env

# Edit with your API keys
nano .env  # or use any text editor
```

### 5.3 Environment File Structure

```dotenv
# LLM Provider API Keys
OPENAI_API_KEY=sk-proj-your-openai-key-here
GOOGLE_API_KEY=AIza-your-google-key-here
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# Search Provider (brave recommended for cost efficiency)
BRAVE_API_KEY=your-brave-search-key-here
SEARCH_PROVIDER=brave

# Optional: Alternative search providers
# EXA_API_KEY=your-exa-key
# TAVILY_API_KEY=tvly-your-tavily-key

# Optional: For debugging
# LANGSMITH_API_KEY=lsv2_pt_your-langsmith-key
```

### 5.4 Validate API Keys

```bash
# Quick validation script
poetry run python -c "
from utils.settings import settings
print(f'OpenAI: {\"✓\" if settings.openai_api_key else \"✗\"}')
print(f'Google: {\"✓\" if settings.google_api_key else \"✗\"}')
print(f'DeepSeek: {\"✓\" if settings.deepseek_api_key else \"✗\"}')
print(f'Brave: {\"✓\" if settings.brave_api_key else \"✗\"}')
"
```

---

## 6. Dataset Preparation

### 6.1 Source Dataset: BingCheck

The experiments use the **BingCheck** dataset, which contains 6,490 sentences from Bing Chat responses, annotated for factual claim presence.

**Location:** `thesis_latex_files/sources/ground_truth_data-BingCheck/bingcheck.csv`

| Column                     | Type   | Description                      |
| -------------------------- | ------ | -------------------------------- |
| `answer_id`              | string | Unique identifier for the answer |
| `question`               | string | Original user question           |
| `sentence_id`            | int    | Sentence index within answer     |
| `sentence`               | string | The sentence text                |
| `contains_factual_claim` | bool   | Ground truth label               |

### 6.2 Create Thesis Dataset (N=150 sentences)

This script samples 150 sentences using a fixed random seed for reproducibility:

```bash
cd apps/agent
poetry run python scripts/create_thesis_dataset.py
```

**Output:**

- Empty template: `results/thesis_dataset_empty/my_thesis_dataset_extraction.csv`
- Completed runs: `results/thesis_datasets_with_LLM_results/my_thesis_dataset_run*.csv`

**Dataset Statistics:**

- Total sentences: 150
- Sentences with factual claims: ~78 (52%)
- Sentences without factual claims: ~72 (48%)
- Random seed: 42 (for reproducibility)

### 6.3 Verify Dataset

```bash
# Check the generated dataset
poetry run python -c "
import pandas as pd
df = pd.read_csv('../../results/thesis_dataset_empty/my_thesis_dataset_extraction.csv')
print(f'Total sentences: {len(df)}')
print(f'With claims: {df[\"contains_factual_claim\"].sum()}')
print(f'Without claims: {len(df) - df[\"contains_factual_claim\"].sum()}')
"
```

### 6.4 Source Materials Archive

All research papers cited in the thesis are archived in `thesis_latex_files/sources/`:

| Paper                           | Citation Key            | Purpose                        |
| ------------------------------- | ----------------------- | ------------------------------ |
| Long-form factuality in LLMs    | `SAFE2024`            | SAFE methodology (Phase 2)     |
| Towards Effective Extraction... | `Metropolitansky2025` | Claimify methodology (Phase 1) |
| Self-Checker: Plug-and-Play...  | `BingCheck`           | BingCheck dataset source       |
| Survey of Hallucination in LLMs | `Ji2023Survey`        | Hallucination taxonomy         |
| A Survey on Hallucination...    | `Huang2024Survey`     | Factuality vs Faithfulness     |
| Judging LLM-as-a-Judge...       | `LLMJudge`            | LLM evaluation concept         |
| FEVER: Fact Extraction...       | `FEVER`               | Traditional fact-checking      |
| Chain-of-Verification...        | `Dhuliawala2024CoVe`  | Self-correction (Future Work)  |
| A Stitch in Time...             | `Varshney2023`        | Confidence-based detection     |
| Not All Contexts Are Equal...   | `Pan2024CAG`          | Credibility-aware generation   |
| Gemini 2.5 Technical Report     | `Gemini25`            | Model documentation            |
| DeepSeek-V3.2 Technical Report  | `DeepSeekV3.2`        | Model documentation            |

---

## 7. Phase 1: Claim Extraction

### 7.1 Overview

Phase 1 evaluates each model's ability to identify verifiable factual claims from unstructured text. The extraction agent implements the **Claimify** methodology:

1. **Selection:** Filter out non-verifiable sentences
2. **Disambiguation:** Resolve pronouns and context dependencies
3. **Decomposition:** Break compound sentences into atomic claims

### 7.2 Run Extraction for All Models

```bash
cd apps/agent

# Run extraction (processes all 150 sentences × 3 models)
poetry run python scripts/run_extraction_phase.py \
    --dataset ../../results/thesis_dataset_empty/my_thesis_dataset_extraction.csv \
    --output ../../results/thesis_datasets_with_LLM_results/my_thesis_dataset_run1.csv
```

**Important Flags:**

| Flag           | Description                 | Default       |
| -------------- | --------------------------- | ------------- |
| `--dataset`  | Path to input dataset       | Required      |
| `--output`   | Path to save results        | Same as input |
| `--resume`   | Resume from last checkpoint | Enabled       |
| `--provider` | Run single provider only    | All three     |

### 7.3 Run Multiple Independent Runs (k=3)

For statistical reliability, run the extraction phase 3 times:

```bash
# Run 1
poetry run python scripts/run_extraction_phase.py \
    --dataset ../../results/thesis_dataset_empty/my_thesis_dataset_extraction.csv \
    --output ../../results/thesis_datasets_with_LLM_results/my_thesis_dataset_run1.csv

# Run 2
poetry run python scripts/run_extraction_phase.py \
    --dataset ../../results/thesis_dataset_empty/my_thesis_dataset_extraction.csv \
    --output ../../results/thesis_datasets_with_LLM_results/my_thesis_dataset_run2.csv

# Run 3
poetry run python scripts/run_extraction_phase.py \
    --dataset ../../results/thesis_dataset_empty/my_thesis_dataset_extraction.csv \
    --output ../../results/thesis_datasets_with_LLM_results/my_thesis_dataset_run3.csv
```

### 7.4 Output Structure

After extraction, the dataset will have additional columns:

| Column                             | Description                   |
| ---------------------------------- | ----------------------------- |
| `gpt4_contains_claims`           | GPT-4o-mini prediction (bool) |
| `gpt4_extracted_claims_json`     | Extracted claims (JSON)       |
| `gemini_contains_claims`         | Gemini prediction (bool)      |
| `gemini_extracted_claims_json`   | Extracted claims (JSON)       |
| `deepseek_contains_claims`       | DeepSeek prediction (bool)    |
| `deepseek_extracted_claims_json` | Extracted claims (JSON)       |

### 7.5 Analyze Extraction Results

```bash
# Generate per-run metrics
poetry run python scripts/analyze_extraction.py \
    --dataset ../../results/thesis_datasets_with_LLM_results/my_thesis_dataset_run1.csv \
    --output ../../results/extraction/per_run/extraction_metrics_run1.csv

# Repeat for run2 and run3 with appropriate input files
```

---

## 8. Phase 2: Claim Verification

### 8.1 Overview

Phase 2 evaluates each model's ability to verify claims using **search-augmented reasoning** (SAFE methodology):

1. **Query Generation:** Formulate search queries from the claim
2. **Evidence Retrieval:** Search the web via Brave Search API
3. **Reasoning:** Compare claim against retrieved evidence
4. **Verdict:** Classify as Supported, Refuted, or Insufficient Information

### 8.2 Create Benchmark Claims

First, extract claims from the winning extractor (GPT-4o-mini based on F1 score) for the verification benchmark:

```bash
cd apps/agent

poetry run python scripts/create_benchmark_claims.py \
    --dataset ../../results/thesis_datasets_with_LLM_results/my_thesis_dataset_run1.csv \
    --extraction-metrics ../../results/extraction/per_run/extraction_metrics_run1.csv \
    --output ../../results/thesis_dataset_empty/my_thesis_benchmark_claims_verification.csv
```

**Output:**

- Empty template: `results/thesis_dataset_empty/my_thesis_benchmark_claims_verification.csv`
- Completed runs: `results/thesis_datasets_with_LLM_results/my_thesis_benchmark_claims_run*.csv`

### 8.3 Manual Ground Truth Annotation

Before running verification, you must annotate the ground truth verdicts:

1. Open `results/thesis_dataset_empty/my_thesis_benchmark_claims_verification.csv`
2. For each claim, research and add the `ground_truth_verdict`:
   - `Supported` - Claim is factually correct
   - `Refuted` - Claim is factually incorrect
   - `Insufficient Information` - Cannot be verified with available evidence
3. Document your source URL in the `ground_truth_source` column

### 8.4 Run Verification for All Models

```bash
cd apps/agent

poetry run python scripts/run_verification_phase.py \
    --benchmark ../../results/thesis_dataset_empty/my_thesis_benchmark_claims_verification.csv \
    --output ../../results/thesis_datasets_with_LLM_results/my_thesis_benchmark_claims_run1.csv
```

### 8.5 Run Multiple Independent Runs (k=2)

```bash
# Run 1
poetry run python scripts/run_verification_phase.py \
    --benchmark ../../results/thesis_dataset_empty/my_thesis_benchmark_claims_verification.csv \
    --output ../../results/thesis_datasets_with_LLM_results/my_thesis_benchmark_claims_run1.csv

# Run 2
poetry run python scripts/run_verification_phase.py \
    --benchmark ../../results/thesis_dataset_empty/my_thesis_benchmark_claims_verification.csv \
    --output ../../results/thesis_datasets_with_LLM_results/my_thesis_benchmark_claims_run2.csv
```

### 8.6 Output Structure

| Column                | Description         |
| --------------------- | ------------------- |
| `gpt4_verdict`      | GPT-4o-mini verdict |
| `gpt4_reasoning`    | Reasoning chain     |
| `gpt4_sources_json` | Retrieved evidence  |
| `gemini_verdict`    | Gemini verdict      |
| `deepseek_verdict`  | DeepSeek verdict    |

### 8.7 Analyze Verification Results

```bash
poetry run python scripts/analyze_verification.py \
    --benchmark ../../results/thesis_datasets_with_LLM_results/my_thesis_benchmark_claims_run1.csv \
    --output ../../results/verification/per_run/verification_metrics_run1.csv
```

---

## 9. Metrics Aggregation

### 9.1 Aggregate Extraction Metrics

After completing all 3 extraction runs:

```bash
cd apps/agent

poetry run python scripts/aggregate_extraction_metrics.py
```

**Outputs:**

- `results/extraction/aggregated/extraction_metrics_aggregated.csv` - Full statistics
- `results/extraction/aggregated/extraction_summary_simple.csv` - Simplified for thesis

### 9.2 Aggregate Verification Metrics

After completing both verification runs:

```bash
poetry run python scripts/aggregate_verification_metrics.py
```

**Outputs:**

- `results/verification/aggregated/verification_metrics_aggregated.csv`
- `results/verification/aggregated/verification_summary_simple.csv`

### 9.3 Expected Aggregated Results

**Extraction (Phase 1):**

| Model            | Precision | Recall | F1-Score        |
| ---------------- | --------- | ------ | --------------- |
| GPT-4o-mini      | 83.1%     | 77.8%  | **80.4%** |
| Gemini-2.5-Flash | 89.5%     | 40.2%  | 55.4%           |
| DeepSeek-V3.2    | 95.8%     | 49.6%  | 65.3%           |

**Verification (Phase 2):**

| Model            | Accuracy        | Macro-F1        |
| ---------------- | --------------- | --------------- |
| GPT-4o-mini      | 77.0%           | 50.4%           |
| Gemini-2.5-Flash | **82.0%** | 53.7%           |
| DeepSeek-V3.2    | 79.0%           | **55.9%** |

---

## 10. Figure Generation

### 10.1 Generate All Thesis Figures

```bash
cd apps/agent

poetry run python ../../visualization_scripts/generate_all_figures.py
```

### 10.2 Generated Figures

| Figure | Filename                                  | Description                       |
| ------ | ----------------------------------------- | --------------------------------- |
| 5.1    | `fig_extraction_f1_comparison.png`      | F1-Score bar chart (both classes) |
| 5.2    | `fig_precision_recall_tradeoff.png`     | Precision-Recall scatter plot     |
| 5.3    | `fig_extraction_confusion_matrices.png` | Confusion matrices (3 models)     |
| 5.4    | `fig_extraction_reliability.png`        | F1 box plots across runs          |
| 5.5    | `fig_verification_accuracy.png`         | Accuracy vs Macro-F1 comparison   |
| 5.6    | `fig_per_class_f1_heatmap.png`          | Per-class F1 heatmap              |
| 5.7    | `fig_verification_reliability.png`      | Accuracy box plots across runs    |
| 5.8    | `fig_inter_model_agreement.png`         | Pairwise agreement matrix         |
| 5.9    | `fig_radar_comparison.png`              | Multi-dimensional radar chart     |
| A.1    | `fig_reliability_analysis.png`          | Combined reliability analysis     |

### 10.3 Output Location

Figures are saved to: `images/results/`

---

## 11. Thesis Compilation

### 11.1 LaTeX Compilation

```bash
cd /path/to/TruthLens/thesis_latex_files

# Compile thesis
pdflatex thesis.tex
bibtex thesis
pdflatex thesis.tex
pdflatex thesis.tex
```

### 11.2 Using latexmk (Recommended)

```bash
cd thesis_latex_files
latexmk -pdf thesis.tex
```

### 11.3 VS Code LaTeX Workshop

If using VS Code with LaTeX Workshop extension:

1. Open `thesis_latex_files/thesis.tex`
2. Press `Cmd+Alt+B` (macOS) or `Ctrl+Alt+B` (Windows/Linux)
3. View PDF with `Cmd+Alt+V` / `Ctrl+Alt+V`

---

## 12. Troubleshooting

### 12.1 Common Issues

#### API Rate Limits

**Problem:** `RateLimitError` from API providers

**Solution:**

```python
# The scripts have built-in retry logic, but you can adjust:
# In run_extraction_phase.py, increase sleep time:
await asyncio.sleep(2)  # Increase from 1 to 2 seconds
```

#### DeepSeek JSON Parsing Errors

**Problem:** DeepSeek returns malformed JSON

**Solution:** The framework includes middleware to handle this. If issues persist:

```bash
# Check logs for specific errors
cat script_logs/run_extraction_phase_*.txt
```

#### Memory Issues

**Problem:** `MemoryError` during large batch processing

**Solution:**

```bash
# Process in smaller batches
poetry run python scripts/run_extraction_phase.py \
    --batch-size 10  # Default is 50
```

### 12.2 Verify Results Integrity

```bash
# Check extraction results completeness
poetry run python -c "
import pandas as pd
df = pd.read_csv('../../results/thesis_datasets_with_LLM_results/my_thesis_dataset_run1.csv')
for model in ['gpt4', 'gemini', 'deepseek']:
    col = f'{model}_contains_claims'
    if col in df.columns:
        complete = df[col].notna().sum()
        print(f'{model}: {complete}/150 complete')
"
```

---

## 13. Cost Estimation

### 13.1 API Costs (Approximate)

Based on December 2024 pricing:

| Phase        | Model            | Tokens/Run   | Cost/Run              | Total (k runs) |
| ------------ | ---------------- | ------------ | --------------------- | -------------- |
| Extraction   | GPT-4o-mini      | ~75,000      | ~$0.15 | ~$0.45 (k=3) |                |
| Extraction   | Gemini-2.5-Flash | ~75,000      | ~$0.08 | ~$0.24 (k=3) |                |
| Extraction   | DeepSeek-V3.2    | ~75,000      | ~$0.02 | ~$0.06 (k=3) |                |
| Verification | All models       | ~300,000     | ~$2.00 | ~$4.00 (k=2) |                |
| Search       | Brave API        | ~500 queries | Free tier             | $0             |

**Total Estimated Cost:** ~$5-10 USD for full reproduction

### 13.2 Cost Optimization Tips

1. **Use DeepSeek for testing** - 10x cheaper than OpenAI
2. **Use Brave Search free tier** - 2,000 queries/month free
3. **Enable resume capability** - Avoids re-running completed sentences
4. **Run verification once first** - Verify setup before multiple runs

---

## Appendix A: Script Reference

### A.1 All Available Scripts

| Script                                | Purpose                             | Example         |
| ------------------------------------- | ----------------------------------- | --------------- |
| `create_thesis_dataset.py`          | Sample 150 sentences from BingCheck | See Section 6.2 |
| `create_benchmark_claims.py`        | Extract claims for verification     | See Section 8.2 |
| `run_extraction_phase.py`           | Run Phase 1 extraction              | See Section 7.2 |
| `run_verification_phase.py`         | Run Phase 2 verification            | See Section 8.4 |
| `analyze_extraction.py`             | Calculate extraction metrics        | See Section 7.5 |
| `analyze_verification.py`           | Calculate verification metrics      | See Section 8.7 |
| `aggregate_extraction_metrics.py`   | Aggregate across runs               | See Section 9.1 |
| `aggregate_verification_metrics.py` | Aggregate across runs               | See Section 9.2 |

### A.2 LLM Provider Switching

To run with a single provider:

```bash
# OpenAI only
poetry run python scripts/run_extraction_phase.py --provider openai

# Gemini only
poetry run python scripts/run_extraction_phase.py --provider gemini

# DeepSeek only
poetry run python scripts/run_extraction_phase.py --provider deepseek
```

---

## Appendix B: Citation

If you use this framework or reproduce these experiments, please cite:

```bibtex
@thesis{elshahat2025truthlens,
  title={A Comparative Analysis of Large Language Models (GPT-4o-mini, 
         Gemini-2.5-Flash, DeepSeek-V3.2) for Factual Claim Extraction 
         and Verification},
  author={Elshahat, Aasem},
  year={2025},
  school={Berliner Hochschule für Technik},
  type={Bachelor's Thesis}
}
```

---

## Appendix C: Contact & Support

- **Author:** Aasem Elshahat
- **Institution:** Berliner Hochschule für Technik (BHT)
- **Thesis Supervisors:**
  - Prof. Dr. Siamak Haschemi
  - Dipl.-Inf. (FH) Markus Schubert
- **Date:** December 2025

---

*Last Updated: December 23, 2025*
