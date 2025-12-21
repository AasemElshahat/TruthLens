# TruthLens Visualization Scripts

This directory contains scripts for generating thesis figures (Chapter 5: Results and Evaluation).

## Quick Start

```bash
cd visualization_scripts
poetry run python generate_all_figures.py
```

## Output

All figures are saved to `../images/results/` in both PDF (for LaTeX) and PNG formats.

## Generated Figures

| Figure | Description | LaTeX Reference |
|--------|-------------|-----------------|
| `fig_extraction_f1_comparison.pdf` | Bar chart comparing F1-scores (positive & negative class) | Figure 5.1 |
| `fig_precision_recall_tradeoff.pdf` | Scatter plot with iso-F1 curves | Figure 5.2 |
| `fig_verification_accuracy.pdf` | Accuracy vs Macro-F1 comparison | Figure 5.3 |
| `fig_per_class_f1_heatmap.pdf` | Heatmap showing class imbalance impact | Figure 5.4 |
| `fig_extraction_confusion_matrices.pdf` | Side-by-side confusion matrices | Figure 5.5 |
| `fig_reliability_analysis.pdf` | Box plots for run-to-run variability | Figure 5.6 |
| `fig_radar_comparison.pdf` | Multi-dimensional comparison radar | Figure 5.7 |
| `fig_inter_model_agreement.pdf` | Pairwise agreement rates | Figure 5.8 |

## Dependencies

- pandas
- matplotlib
- seaborn
- numpy

All available through the poetry environment in `../apps/agent/`.

## Customization

Colors and labels are defined at the top of `generate_all_figures.py`:

```python
COLORS = {
    "gpt4": "#10A37F",      # OpenAI Green
    "gemini": "#4285F4",    # Google Blue
    "deepseek": "#FF6B35",  # DeepSeek Orange
}
```
