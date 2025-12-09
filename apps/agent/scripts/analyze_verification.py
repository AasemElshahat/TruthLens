#!/usr/bin/env python3
"""
Script to analyze verification results from all three LLMs against manual ground truth.

This script compares verification performance against manual annotations
and creates verification_metrics.csv with performance metrics for all LLMs.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


def load_benchmark_with_verifications(benchmark_path: str) -> pd.DataFrame:
    """Load the benchmark that includes verification results."""
    df = pd.read_csv(benchmark_path)
    
    return df


def normalize_verdict(verdict: str) -> str:
    """Normalize verdict to standard categories."""
    if pd.isna(verdict):
        return 'unknown'
    
    verdict_lower = str(verdict).strip().lower()
    
    if 'supported' in verdict_lower or 'true' in verdict_lower or 'correct' in verdict_lower:
        return 'supported'
    elif 'refuted' in verdict_lower or 'false' in verdict_lower or 'incorrect' in verdict_lower or 'contradicted' in verdict_lower:
        return 'refuted'
    elif 'neutral' in verdict_lower or 'mixed' in verdict_lower or 'incomplete' in verdict_lower:
        return 'neutral'
    elif 'unknown' in verdict_lower or 'undetermined' in verdict_lower or 'unverifiable' in verdict_lower:
        return 'unknown'
    else:
        # For cases where the verdict is already a simple category
        if verdict_lower in ['supported', 'refuted', 'neutral', 'unknown']:
            return verdict_lower
        else:
            # If it's an unexpected verdict type, categorize as "other"
            return 'other'


def calculate_verification_metrics(df: pd.DataFrame, provider_prefix: str) -> Dict[str, Any]:
    """Calculate verification metrics for a specific LLM provider."""
    print(f"\n🔍 Calculating verification metrics for {provider_prefix}...")
    
    # Filter to only rows with ground truth verdicts (manually annotated)
    original_count = len(df)
    annotated_df = df[df['ground_truth_verdict'].notna() & (df['ground_truth_verdict'] != '')].copy()
    annotated_count = len(annotated_df)
    
    print(f"  Total claims: {original_count}, Manually annotated: {annotated_count}")
    
    if annotated_count == 0:
        print(f"  ⚠️  No manually annotated claims found for {provider_prefix}")
        return None
    
    # Get ground truth and predictions
    y_true = annotated_df['ground_truth_verdict'].apply(normalize_verdict)
    y_pred = annotated_df[f'{provider_prefix}_verdict'].apply(normalize_verdict)

    # Report counts of different verdict types to expose what's being filtered
    y_true_value_counts = y_true.value_counts()
    y_pred_value_counts = y_pred.value_counts()
    
    print(f"  Ground truth verdict distribution: {dict(y_true_value_counts)}")
    print(f"  Predicted verdict distribution: {dict(y_pred_value_counts)}")

    # Identify and report 'unknown' and 'other' categories that will be filtered out
    true_unknown_mask = (y_true == 'unknown') | (y_true == 'other')
    pred_unknown_mask = (y_pred == 'unknown') | (y_pred == 'other')
    
    true_unknown_count = true_unknown_mask.sum()
    pred_unknown_count = pred_unknown_mask.sum()
    
    if true_unknown_count > 0 or pred_unknown_count > 0:
        print(f"  Note: Filtering out {true_unknown_count} ground truth and {pred_unknown_count} predicted 'unknown'/'other' values")
    
    # Filter to remove 'unknown' and 'other' categories for meaningful metrics
    valid_mask = ~true_unknown_mask & ~pred_unknown_mask
    
    y_true_filtered = y_true[valid_mask]
    y_pred_filtered = y_pred[valid_mask]

    valid_comparison_count = len(y_true_filtered)
    
    if valid_comparison_count == 0:
        print(f"  ⚠️  No valid comparisons found for {provider_prefix} after filtering")
        print(f"     All {annotated_count} annotated items were filtered out due to 'unknown'/'other' verdicts")
        return None

    # Calculate metrics
    accuracy = accuracy_score(y_true_filtered, y_pred_filtered)
    
    # For multi-class, calculate macro average
    precision = precision_score(y_true_filtered, y_pred_filtered, average='macro', zero_division=0)
    recall = recall_score(y_true_filtered, y_pred_filtered, average='macro', zero_division=0)
    f1 = f1_score(y_true_filtered, y_pred_filtered, average='macro', zero_division=0)

    # Detailed classification report
    report = classification_report(
        y_true_filtered,
        y_pred_filtered,
        output_dict=True
    )

    # Confusion matrix
    cm = confusion_matrix(y_true_filtered, y_pred_filtered)

    # Per-class metrics
    unique_labels = set(y_true_filtered) | set(y_pred_filtered)
    per_class_metrics = {}
    for label in unique_labels:
        if label in report:
            per_class_metrics[label] = {
                'precision': report[label]['precision'],
                'recall': report[label]['recall'],
                'f1_score': report[label]['f1-score'],
                'support': report[label]['support']
            }

    metrics = {
        'provider': provider_prefix,
        'accuracy': accuracy,
        'macro_precision': precision,
        'macro_recall': recall,
        'macro_f1_score': f1,
        'per_class_metrics': per_class_metrics,
        'classification_report': report,
        'confusion_matrix': cm.tolist() if len(cm) > 0 else [],
        'total_samples': valid_comparison_count,
        'total_annotated': annotated_count,
        'samples_excluded': annotated_count - valid_comparison_count,
        'samples_per_class': {
            'ground_truth': dict(y_true_filtered.value_counts()),
            'predictions': dict(y_pred_filtered.value_counts())
        },
        'annotation_quality': annotated_count / original_count if original_count > 0 else 0
    }

    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Macro Precision: {precision:.4f}")
    print(f"  Macro Recall: {recall:.4f}")
    print(f"  Macro F1-Score: {f1:.4f}")
    print(f"  Classes: {list(unique_labels)}")
    print(f"  Valid comparisons: {valid_comparison_count}/{annotated_count} annotated")

    return metrics


def create_verifications_comparison_summary(
    gpt4_metrics: Dict[str, Any], 
    gemini_metrics: Dict[str, Any], 
    deepseek_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a summary comparing all three LLMs' verification performance."""
    
    # Determine winner based on F1-score
    metrics_list = [gpt4_metrics, gemini_metrics, deepseek_metrics]
    winners = []
    
    for metrics in metrics_list:
        if metrics and 'macro_f1_score' in metrics:
            winners.append((metrics['provider'], metrics['macro_f1_score']))
    
    # Sort by F1-score to determine winner
    winners.sort(key=lambda x: x[1], reverse=True)
    verification_winner = winners[0] if winners else ('unknown', 0.0)
    
    summary = {
        'verification_winner': verification_winner[0],
        'winner_f1_score': verification_winner[1],
        'all_providers_ranking': winners,
        'gpt4_metrics': gpt4_metrics,
        'gemini_metrics': gemini_metrics,
        'deepseek_metrics': deepseek_metrics
    }
    
    return summary


def analyze_verification_phase(benchmark_path: str, output_path: str):
    """Analyze verification results and create metrics summary."""
    print("🔍 Analyzing verification phase results...")
    print(f"Benchmark: {benchmark_path}")
    print(f"Output: {output_path}")
    
    # Load benchmark with verifications
    df = load_benchmark_with_verifications(benchmark_path)
    print(f"Loaded benchmark with {len(df)} claims")
    
    # Calculate metrics for each provider
    gpt4_metrics = calculate_verification_metrics(df, 'gpt4')
    gemini_metrics = calculate_verification_metrics(df, 'gemini')
    deepseek_metrics = calculate_verification_metrics(df, 'deepseek')
    
    # Create comparison summary
    summary = create_verifications_comparison_summary(gpt4_metrics, gemini_metrics, deepseek_metrics)
    
    # Print summary
    print(f"\n🏆 Verification Winner: {summary['verification_winner']} (Macro F1-Score: {summary['winner_f1_score']:.4f})")
    print("All providers ranking:")
    for i, (provider, f1_score) in enumerate(summary['all_providers_ranking'], 1):
        print(f"  {i}. {provider}: {f1_score:.4f}")
    
    # Save metrics to CSV
    metrics_data = []
    
    for provider_metrics in [summary['gpt4_metrics'], summary['gemini_metrics'], summary['deepseek_metrics']]:
        if provider_metrics:
            # Prepare row data with flattened structure for CSV
            row_data = {
                'provider': provider_metrics['provider'],
                'accuracy': provider_metrics['accuracy'],
                'macro_precision': provider_metrics['macro_precision'],
                'macro_recall': provider_metrics['macro_recall'],
                'macro_f1_score': provider_metrics['macro_f1_score'],
                'total_samples': provider_metrics['total_samples'],
                'total_annotated': provider_metrics['total_annotated'],
                'samples_excluded': provider_metrics['samples_excluded'],
                'annotation_quality': provider_metrics['annotation_quality']
            }
            
            # Add per-class metrics as separate columns if they exist
            for class_name, class_metrics in provider_metrics.get('per_class_metrics', {}).items():
                row_data[f'{class_name}_precision'] = class_metrics['precision']
                row_data[f'{class_name}_recall'] = class_metrics['recall']
                row_data[f'{class_name}_f1_score'] = class_metrics['f1_score']
                row_data[f'{class_name}_support'] = class_metrics['support']
            
            metrics_data.append(row_data)
    
    if metrics_data:
        metrics_df = pd.DataFrame(metrics_data)
        metrics_df.to_csv(output_path, index=False)
        print(f"\n📈 Verification metrics saved to {output_path}")
    else:
        print("⚠️  No metrics to save")
    
    return summary


def main():
    parser = argparse.ArgumentParser(description="Analyze verification phase results")
    parser.add_argument(
        "--benchmark",
        type=str,
        default="../../my_thesis_benchmark_claims.csv",
        help="Path to the benchmark CSV file with verification results"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="../../verification_metrics.csv",
        help="Path to save verification metrics CSV file"
    )
    
    args = parser.parse_args()

    print(f"📄 Benchmark: {args.benchmark}")
    print(f"💾 Output: {args.output}")
    
    # Verify the benchmark exists
    if not Path(args.benchmark).exists():
        print(f"❌ Benchmark file not found: {args.benchmark}")
        sys.exit(1)
    
    # Analyze verification results
    summary = analyze_verification_phase(args.benchmark, args.output)
    
    print("\n✅ Verification analysis completed successfully!")


if __name__ == "__main__":
    main()