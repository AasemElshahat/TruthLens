#!/usr/bin/env python3
"""
TruthLens Thesis Visualization Generator
=========================================
Generates all figures for Chapter 5 (Results and Evaluation).

Output files are saved to: ../images/results/
LaTeX-ready format with consistent styling.

Usage:
    cd visualization_scripts
    poetry run python generate_all_figures.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Output directory for figures
OUTPUT_DIR = Path(__file__).parent.parent / "images" / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Data directories
RESULTS_DIR = Path(__file__).parent.parent / "results"
EXTRACTION_AGG = RESULTS_DIR / "extraction" / "aggregated"
VERIFICATION_AGG = RESULTS_DIR / "verification" / "aggregated"
EXTRACTION_PER_RUN = RESULTS_DIR / "extraction" / "per_run"
VERIFICATION_PER_RUN = RESULTS_DIR / "verification" / "per_run"

# Color scheme - consistent across all figures
COLORS = {
    "gpt4": "#00A78E",      # OpenAI Green
    "gemini": "#FDA913",    # Google Yellow
    "deepseek": "#0066FF",  # DeepSeek Blue
}

MODEL_LABELS = {
    "gpt4": "gpt-4o-mini",
    "gemini": "gemini-2.5-flash",
    "deepseek": "deepseek-v3.2",
}

# Plot styling
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
})


# ==============================================================================
# DATA LOADING
# ==============================================================================

def load_extraction_data():
    """Load aggregated extraction metrics."""
    df = pd.read_csv(EXTRACTION_AGG / "extraction_summary_simple.csv")
    return df

def load_verification_data():
    """Load aggregated verification metrics."""
    df = pd.read_csv(VERIFICATION_AGG / "verification_summary_simple.csv")
    return df

def load_extraction_per_run():
    """Load per-run extraction metrics for all runs."""
    runs = []
    for i in range(1, 4):  # 3 runs
        filepath = EXTRACTION_PER_RUN / f"extraction_metrics_run{i}.csv"
        if filepath.exists():
            df = pd.read_csv(filepath)
            df["run"] = i
            runs.append(df)
    return pd.concat(runs, ignore_index=True)

def load_verification_per_run():
    """Load per-run verification metrics for all runs."""
    runs = []
    for i in range(1, 3):  # 2 runs
        filepath = VERIFICATION_PER_RUN / f"verification_metrics_run{i}.csv"
        if filepath.exists():
            df = pd.read_csv(filepath)
            df["run"] = i
            runs.append(df)
    return pd.concat(runs, ignore_index=True)

def load_inter_model_metrics():
    """Load inter-model agreement metrics."""
    filepath = VERIFICATION_PER_RUN / "inter_model_metrics_run1.csv"
    if filepath.exists():
        return pd.read_csv(filepath)
    return None


# ==============================================================================
# FIGURE 1: EXTRACTION F1-SCORE COMPARISON (Bar Chart)
# ==============================================================================

def figure_extraction_f1_comparison(ext_data):
    """
    Bar chart comparing F1-scores across models for extraction phase.
    Shows both positive class (factual claims) and negative class (non-factual).
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    
    models = ext_data["provider"].tolist()
    x = np.arange(len(models))
    width = 0.35
    
    # Get F1 scores for both classes
    f1_positive = ext_data["f1_mean"].values * 100
    f1_positive_std = ext_data["f1_std"].values * 100
    
    # For negative class, we need to load per-run data
    per_run = load_extraction_per_run()
    f1_negative = []
    f1_negative_std = []
    for model in models:
        model_data = per_run[per_run["provider"] == model]["f1_score_negative"]
        f1_negative.append(model_data.mean() * 100)
        f1_negative_std.append(model_data.std() * 100)
    
    # Create bars
    bars1 = ax.bar(x - width/2, f1_positive, width, 
                   label="Positive Class (Factual Claims)",
                   color=[COLORS[m] for m in models],
                   yerr=f1_positive_std, capsize=4, edgecolor="black", linewidth=0.5)
    
    bars2 = ax.bar(x + width/2, f1_negative, width,
                   label="Negative Class (Non-Factual)",
                   color=[COLORS[m] for m in models],
                   alpha=0.5, hatch="//",
                   yerr=f1_negative_std, capsize=4, edgecolor="black", linewidth=0.5)
    
    # Add value labels on bars
    for bar, val in zip(bars1, f1_positive):
        ax.annotate(f"{val:.1f}%", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
    
    for bar, val in zip(bars2, f1_negative):
        ax.annotate(f"{val:.1f}%", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
    
    ax.set_ylabel("F1-Score (%)")
    ax.set_xlabel("Model")
    # No title - use LaTeX caption instead
    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_LABELS[m] for m in models])
    ax.set_ylim(0, 100)
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    
    # Add horizontal line at 50% for reference
    ax.axhline(y=50, color="gray", linestyle=":", alpha=0.5, label="_nolegend_")
    
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig_extraction_f1_comparison.png")
    plt.close(fig)
    print("✓ Generated: fig_extraction_f1_comparison.png")


# ==============================================================================
# FIGURE 2: PRECISION-RECALL TRADE-OFF (Scatter Plot)
# ==============================================================================

def figure_precision_recall_tradeoff(ext_data):
    """
    Scatter plot showing precision vs recall trade-off for extraction.
    Each model represented as a point with error bars.
    """
    fig, ax = plt.subplots(figsize=(7, 6))
    
    for _, row in ext_data.iterrows():
        model = row["provider"]
        prec = row["precision_mean"] * 100
        rec = row["recall_mean"] * 100
        prec_std = row["precision_std"] * 100
        rec_std = row["recall_std"] * 100
        
        ax.errorbar(rec, prec, 
                    xerr=rec_std, yerr=prec_std,
                    fmt="o", markersize=12, 
                    color=COLORS[model],
                    capsize=5, capthick=2,
                    label=MODEL_LABELS[model],
                    markeredgecolor="black", markeredgewidth=1)
    
    # Add iso-F1 curves
    for f1_val in [0.5, 0.6, 0.7, 0.8, 0.9]:
        recall_range = np.linspace(f1_val * 100 / (2 - f1_val), 100, 100)
        precision_curve = f1_val * 100 * recall_range / (2 * recall_range - f1_val * 100)
        valid = precision_curve <= 100
        ax.plot(recall_range[valid], precision_curve[valid], 
                "--", color="gray", alpha=0.3, linewidth=1)
        # Label the curve
        if f1_val in [0.6, 0.8]:
            ax.annotate(f"F1={f1_val}", xy=(recall_range[valid][-1], precision_curve[valid][-1]),
                        fontsize=8, color="gray", alpha=0.7)
    
    ax.set_xlabel("Recall (%)")
    ax.set_ylabel("Precision (%)")
    # No title - use LaTeX caption instead
    ax.set_xlim(30, 100)
    ax.set_ylim(75, 100)
    ax.legend(loc="lower left")
    ax.grid(alpha=0.3, linestyle="--")
    
    # Annotate key insight
    ax.annotate("High Precision,\nLow Recall", 
                xy=(45, 95), fontsize=9, style="italic", color="gray",
                ha="center")
    ax.annotate("Balanced\n(GPT-4o-mini)", 
                xy=(80, 82), fontsize=9, style="italic", color="gray",
                ha="center")
    
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig_precision_recall_tradeoff.png")
    plt.close(fig)
    print("✓ Generated: fig_precision_recall_tradeoff.png")


# ==============================================================================
# FIGURE 3: VERIFICATION ACCURACY COMPARISON (Bar Chart)
# ==============================================================================

def figure_verification_accuracy(ver_data):
    """
    Bar chart comparing verification accuracy and macro-F1 across models.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    
    models = ver_data["provider"].tolist()
    x = np.arange(len(models))
    width = 0.35
    
    accuracy = ver_data["accuracy_mean"].values * 100
    accuracy_std = ver_data["accuracy_std"].values * 100
    macro_f1 = ver_data["macro_f1_mean"].values * 100
    macro_f1_std = ver_data["macro_f1_std"].values * 100
    
    bars1 = ax.bar(x - width/2, accuracy, width,
                   label="Accuracy",
                   color=[COLORS[m] for m in models],
                   yerr=accuracy_std, capsize=4, edgecolor="black", linewidth=0.5)
    
    bars2 = ax.bar(x + width/2, macro_f1, width,
                   label="Macro-F1",
                   color=[COLORS[m] for m in models],
                   alpha=0.5, hatch="//",
                   yerr=macro_f1_std, capsize=4, edgecolor="black", linewidth=0.5)
    
    # Add value labels
    for bar, val in zip(bars1, accuracy):
        ax.annotate(f"{val:.1f}%", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
    
    for bar, val in zip(bars2, macro_f1):
        ax.annotate(f"{val:.1f}%", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
    
    ax.set_ylabel("Score (%)")
    ax.set_xlabel("Model")
    # No title - use LaTeX caption instead
    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_LABELS[m] for m in models])
    ax.set_ylim(0, 100)
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig_verification_accuracy.png")
    plt.close(fig)
    print("✓ Generated: fig_verification_accuracy.png")


# ==============================================================================
# FIGURE 4: PER-CLASS F1 HEATMAP (Verification)
# ==============================================================================

def figure_per_class_f1_heatmap(ver_per_run):
    """
    Heatmap showing per-class F1 scores for verification.
    Highlights class imbalance impact (Refuted has very low F1).
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    
    # Aggregate per-class F1 across runs
    classes = ["supported", "refuted", "insufficient"]
    models = ["gpt4", "gemini", "deepseek"]
    
    data = []
    for model in models:
        model_data = ver_per_run[ver_per_run["provider"] == model]
        row = []
        for cls in classes:
            f1_col = f"{cls}_f1_score"
            row.append(model_data[f1_col].mean() * 100)
        data.append(row)
    
    data = np.array(data)
    
    # Create heatmap
    im = ax.imshow(data, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)
    
    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("F1-Score (%)")
    
    # Set ticks
    ax.set_xticks(np.arange(len(classes)))
    ax.set_yticks(np.arange(len(models)))
    ax.set_xticklabels(["Supported\n(n=85)", "Refuted\n(n=3)", "Insufficient\n(n=12)"])
    ax.set_yticklabels([MODEL_LABELS[m] for m in models])
    
    # Add text annotations - always use black for readability
    for i in range(len(models)):
        for j in range(len(classes)):
            val = data[i, j]
            ax.text(j, i, f"{val:.1f}%", ha="center", va="center", 
                    color="black", fontsize=11, fontweight="bold")
    
    # No title - use LaTeX caption instead
    ax.set_xlabel("Verdict Class (with ground truth support)")
    
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig_per_class_f1_heatmap.png")
    plt.close(fig)
    print("✓ Generated: fig_per_class_f1_heatmap.png")


# ==============================================================================
# FIGURE 5: CONFUSION MATRIX (Extraction - GPT-4 as representative)
# ==============================================================================

def figure_extraction_confusion_matrix(ext_per_run):
    """
    Confusion matrices for extraction phase - one for each model.
    Shows TP, TN, FP, FN distributions.
    """
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    
    models = ["gpt4", "gemini", "deepseek"]
    
    for idx, model in enumerate(models):
        ax = axes[idx]
        model_data = ext_per_run[ext_per_run["provider"] == model]
        
        # Average confusion matrix values across runs
        tp = model_data["tp"].mean()
        tn = model_data["tn"].mean()
        fp = model_data["fp"].mean()
        fn = model_data["fn"].mean()
        
        cm = np.array([[tn, fp], [fn, tp]])
        
        # Create heatmap
        im = ax.imshow(cm, cmap="Blues", aspect="equal")
        
        # Add text annotations
        for i in range(2):
            for j in range(2):
                val = cm[i, j]
                text_color = "white" if val > cm.max() / 2 else "black"
                ax.text(j, i, f"{val:.0f}", ha="center", va="center",
                        color=text_color, fontsize=14, fontweight="bold")
        
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["No Claim", "Claim"])
        ax.set_yticklabels(["No Claim", "Claim"])
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        # Model name as subplot label (not a title)
        ax.set_title(MODEL_LABELS[model], fontsize=12, fontweight="bold",
                     color=COLORS[model])
    
    # No suptitle - use LaTeX caption instead
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig_extraction_confusion_matrices.png")
    plt.close(fig)
    print("✓ Generated: fig_extraction_confusion_matrices.png")


# ==============================================================================
# FIGURE 6a: EXTRACTION RELIABILITY ANALYSIS (Run-to-Run Variability)
# ==============================================================================

def figure_extraction_reliability(ext_per_run):
    """
    Box plot showing run-to-run variability for extraction F1-scores.
    Demonstrates consistency across multiple experimental runs.
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    
    models = ["gpt4", "gemini", "deepseek"]
    
    data_ext = []
    positions = []
    colors = []
    for i, model in enumerate(models):
        model_data = ext_per_run[ext_per_run["provider"] == model]["f1_score"] * 100
        data_ext.append(model_data.values)
        positions.append(i)
        colors.append(COLORS[model])
    
    bp = ax.boxplot(data_ext, positions=positions, widths=0.6, patch_artist=True)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_xticklabels([MODEL_LABELS[m] for m in models])
    ax.set_ylabel("F1-Score (%)")
    # No title - use LaTeX caption instead
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_ylim(40, 90)
    
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig_extraction_reliability.png")
    plt.close(fig)
    print("✓ Generated: fig_extraction_reliability.png")


# ==============================================================================
# FIGURE 6b: VERIFICATION RELIABILITY ANALYSIS (Run-to-Run Variability)
# ==============================================================================

def figure_verification_reliability(ver_per_run):
    """
    Box plot showing run-to-run variability for verification accuracy.
    Demonstrates consistency across multiple experimental runs.
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    
    models = ["gpt4", "gemini", "deepseek"]
    
    data_ver = []
    positions = []
    colors = []
    for i, model in enumerate(models):
        model_data = ver_per_run[ver_per_run["provider"] == model]["accuracy"] * 100
        data_ver.append(model_data.values)
        positions.append(i)
        colors.append(COLORS[model])
    
    bp = ax.boxplot(data_ver, positions=positions, widths=0.6, patch_artist=True)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_xticklabels([MODEL_LABELS[m] for m in models])
    ax.set_ylabel("Accuracy (%)")
    # No title - use LaTeX caption instead
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_ylim(70, 90)
    
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig_verification_reliability.png")
    plt.close(fig)
    print("✓ Generated: fig_verification_reliability.png")


# ==============================================================================
# FIGURE 6 (LEGACY): COMBINED RELIABILITY ANALYSIS - kept for reference
# ==============================================================================

def figure_reliability_analysis(ext_per_run, ver_per_run):
    """
    Box plots showing run-to-run variability for key metrics.
    Demonstrates consistency across multiple experimental runs.
    NOTE: This combined figure is kept for backward compatibility.
    Use figure_extraction_reliability and figure_verification_reliability instead.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    models = ["gpt4", "gemini", "deepseek"]
    
    # Left plot: Extraction F1
    ax1 = axes[0]
    data_ext = []
    positions = []
    colors = []
    for i, model in enumerate(models):
        model_data = ext_per_run[ext_per_run["provider"] == model]["f1_score"] * 100
        data_ext.append(model_data.values)
        positions.append(i)
        colors.append(COLORS[model])
    
    bp1 = ax1.boxplot(data_ext, positions=positions, widths=0.6, patch_artist=True)
    for patch, color in zip(bp1["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax1.set_xticklabels([MODEL_LABELS[m] for m in models])
    ax1.set_ylabel("F1-Score (%)")
    ax1.set_title("Extraction: Run-to-Run Variability (k=3)")
    ax1.grid(axis="y", alpha=0.3, linestyle="--")
    ax1.set_ylim(40, 90)
    
    # Right plot: Verification Accuracy
    ax2 = axes[1]
    data_ver = []
    for model in models:
        model_data = ver_per_run[ver_per_run["provider"] == model]["accuracy"] * 100
        data_ver.append(model_data.values)
    
    bp2 = ax2.boxplot(data_ver, positions=positions, widths=0.6, patch_artist=True)
    for patch, color in zip(bp2["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax2.set_xticklabels([MODEL_LABELS[m] for m in models])
    ax2.set_ylabel("Accuracy (%)")
    ax2.set_title("Verification: Run-to-Run Variability (k=2)")
    ax2.grid(axis="y", alpha=0.3, linestyle="--")
    ax2.set_ylim(70, 90)
    
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig_reliability_analysis.png")
    plt.close(fig)
    print("✓ Generated: fig_reliability_analysis.png (combined - legacy)")


# ==============================================================================
# FIGURE 7: RADAR CHART (Overall Model Comparison)
# ==============================================================================

def figure_radar_comparison(ext_data, ver_data):
    """
    Radar chart showing multi-dimensional comparison of models.
    """
    categories = ["Extraction\nAccuracy", "Extraction\nPrecision", "Extraction\nRecall",
                  "Verification\nAccuracy", "Verification\nMacro-F1"]
    N = len(categories)
    
    # Compute angle for each category
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Complete the loop
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    models = ["gpt4", "gemini", "deepseek"]
    
    for model in models:
        ext_row = ext_data[ext_data["provider"] == model].iloc[0]
        ver_row = ver_data[ver_data["provider"] == model].iloc[0]
        
        values = [
            ext_row["accuracy_mean"] * 100,
            ext_row["precision_mean"] * 100,
            ext_row["recall_mean"] * 100,
            ver_row["accuracy_mean"] * 100,
            ver_row["macro_f1_mean"] * 100,
        ]
        values += values[:1]  # Complete the loop
        
        ax.plot(angles, values, "o-", linewidth=2, label=MODEL_LABELS[model],
                color=COLORS[model])
        ax.fill(angles, values, alpha=0.15, color=COLORS[model])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=10)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20%", "40%", "60%", "80%", "100%"], size=8)
    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.1))
    # No title - use LaTeX caption instead
    
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig_radar_comparison.png")
    plt.close(fig)
    print("✓ Generated: fig_radar_comparison.png")


# ==============================================================================
# FIGURE 8: INTER-MODEL AGREEMENT (Verification)
# ==============================================================================

def figure_inter_model_agreement():
    """
    Bar chart showing pairwise agreement between models.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Data from inter_model_metrics_run1.csv
    pairs = ["GPT-4o-mini ↔ Gemini-2.5-Flash", "GPT-4o-mini ↔ DeepSeek-V3", "Gemini-2.5-Flash ↔ DeepSeek-V3", "All Three Agree"]
    agreement = [82, 86, 73, 71]  # From the inter-model metrics
    
    colors_bars = ["#7B68EE", "#20B2AA", "#FF7F50", "#4169E1"]
    
    bars = ax.barh(pairs, agreement, color=colors_bars, edgecolor="black", linewidth=0.5)
    
    # Add value labels
    for bar, val in zip(bars, agreement):
        ax.annotate(f"{val}%", xy=(val + 1, bar.get_y() + bar.get_height()/2),
                    va="center", fontsize=11, fontweight="bold")
    
    ax.set_xlabel("Agreement Rate (%)")
    # No title - use LaTeX caption instead
    ax.set_xlim(0, 100)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    
    # Add Fleiss' Kappa annotation
    ax.annotate("Fleiss' κ = 0.41\n(Moderate Agreement)", 
                xy=(50, -0.7), fontsize=10, style="italic",
                ha="center", va="top", color="gray")
    
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig_inter_model_agreement.png")
    plt.close(fig)
    print("✓ Generated: fig_inter_model_agreement.png")


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    print("=" * 70)
    print("TruthLens Thesis Visualization Generator")
    print("=" * 70)
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    # Load data
    print("Loading data...")
    ext_data = load_extraction_data()
    ver_data = load_verification_data()
    ext_per_run = load_extraction_per_run()
    ver_per_run = load_verification_per_run()
    
    print(f"  - Extraction aggregated: {len(ext_data)} models")
    print(f"  - Verification aggregated: {len(ver_data)} models")
    print(f"  - Extraction per-run: {len(ext_per_run)} rows ({len(ext_per_run)//3} runs)")
    print(f"  - Verification per-run: {len(ver_per_run)} rows ({len(ver_per_run)//3} runs)")
    print()
    
    # Generate figures
    print("Generating figures...")
    print("-" * 70)
    
    figure_extraction_f1_comparison(ext_data)
    figure_precision_recall_tradeoff(ext_data)
    figure_verification_accuracy(ver_data)
    figure_per_class_f1_heatmap(ver_per_run)
    figure_extraction_confusion_matrix(ext_per_run)
    figure_extraction_reliability(ext_per_run)        # NEW: Extraction only
    figure_verification_reliability(ver_per_run)      # NEW: Verification only
    figure_reliability_analysis(ext_per_run, ver_per_run)  # Legacy combined
    figure_radar_comparison(ext_data, ver_data)
    figure_inter_model_agreement()
    
    print("-" * 70)
    print()
    print("=" * 70)
    print("All figures generated successfully!")
    print(f"Files saved to: {OUTPUT_DIR}")
    print("=" * 70)
    
    # List generated files
    print("\nGenerated files:")
    for f in sorted(OUTPUT_DIR.glob("*.png")):
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
