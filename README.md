# TruthLens

**A Comparative Analysis of Large Language Models for Factual Claim Extraction and Verification**

This repository contains the implementation, experimental data, and reproduction materials for a Bachelor's thesis submitted to Berliner Hochschule für Technik (BHT).

---

## Overview

TruthLens is a **decoupled two-phase framework** for automated fact-checking that evaluates Large Language Models (LLMs) on two distinct tasks:

| Phase | Task | Methodology |
|-------|------|-------------|
| **Phase 1** | Claim Extraction | Claimify (Metropolitansky & Larson, 2025) |
| **Phase 2** | Claim Verification | SAFE (Wei et al., 2024) |

### Models Evaluated

| Model | Provider | F1-Score (Extraction) | Accuracy (Verification) |
|-------|----------|----------------------|------------------------|
| gpt-4o-mini | OpenAI | **80.4%** | 79.0% |
| gemini-2.5-flash | Google | 55.4% | **82.0%** |
| deepseek-v3.2 | DeepSeek | 65.3% | 77.5% |

### Key Findings

- **gpt-4o-mini** achieves the best extraction performance with balanced precision-recall
- **gemini-2.5-flash** achieves the highest verification accuracy
- **deepseek-v3.2** shows the best Macro-F1 for minority class detection
- Models achieve **69% unanimous correctness** on verification tasks

---

## Repository Structure

```
TruthLens/
├── apps/agent/                 # Python agent implementation
│   ├── claim_extractor/        # Phase 1: Extraction agent
│   ├── claim_verifier/         # Phase 2: Verification agent
│   ├── scripts/                # Experiment execution scripts
│   └── search/                 # Search provider integrations
├── results/                    # Experimental data and metrics
│   ├── thesis_datasets_with_LLM_results/
│   ├── extraction/
│   └── verification/
├── thesis_latex_files/         # Thesis document and sources
│   ├── thesis.tex
│   ├── references.bib
│   └── sources/
├── visualization_scripts/      # Figure generation
└── REPRODUCTION_GUIDE.md       # Complete reproduction instructions
```

---

## Quick Start

For complete reproduction instructions, see **[REPRODUCTION_GUIDE.md](REPRODUCTION_GUIDE.md)**.

### Prerequisites

- Python 3.11+
- Poetry 1.7+
- API keys: OpenAI, Google AI, DeepSeek, Brave Search

### Installation

```bash
cd apps/agent
poetry install
poetry shell
```

### Run Experiments

```bash
# Phase 1: Claim Extraction
poetry run python scripts/run_extraction_phase.py \
    --dataset ../../results/thesis_dataset_empty/my_thesis_dataset_extraction.csv \
    --output ../../results/thesis_datasets_with_LLM_results/my_thesis_dataset_run1.csv

# Phase 2: Claim Verification
poetry run python scripts/run_verification_phase.py \
    --benchmark ../../results/thesis_dataset_empty/my_thesis_benchmark_claims_verification.csv \
    --output ../../results/thesis_datasets_with_LLM_results/my_thesis_benchmark_claims_run1.csv
```

---

## Citation

If you use this framework or reproduce these experiments, please cite:

```bibtex
@thesis{elshahat2026truthlens,
  title={A Comparative Analysis of Large Language Models (GPT-4o-mini,
         Gemini-2.5-Flash, DeepSeek-V3.2) for Factual Claim Extraction
         and Verification},
  author={Elshahat, Aasem},
  year={2026},
  school={Berliner Hochschule für Technik},
  type={Bachelor's Thesis}
}
```

---

## Acknowledgements

This work builds upon the open-source [ClaimeAI](https://github.com/BharathxD/ClaimeAI) framework by BharathxD, which implements the Claimify and SAFE methodologies.

**Thesis Supervisors:**
- Prof. Dr. Siamak Haschemi
- Dipl.-Inf. (FH) Markus Schubert

**Examiner:**
- Prof. Dr. Felix Gers

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

*Submitted January 2, 2026 | Experiments conducted December 2025*
