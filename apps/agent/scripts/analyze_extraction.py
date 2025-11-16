#!/usr/bin/env python3
"""
Script to analyze extraction results from all three LLMs and determine the winner.

This script compares extraction performance against BingCheck ground truth
and creates extraction_metrics.csv with performance metrics for all LLMs.
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


def load_dataset_with_extractions(dataset_path: str) -> pd.DataFrame:
    """Load the dataset that includes extraction results."""
    df = pd.read_csv(dataset_path)
    
    # Parse JSON fields that were stored as strings
    json_fields = [
        'gpt4_extracted_claims_json', 
        'gemini_extracted_claims_json', 
        'deepseek_extracted_claims_json'
    ]
    
    for field in json_fields:
        def safe_json_parse(x):
            if pd.isna(x) or x == '' or x == 'null' or x == '[]':
                return []
            if isinstance(x, str):
                try:
                    return json.loads(x)
                except (json.JSONDecodeError, TypeError):
                    return []
            return x

        df[field] = df[field].apply(safe_json_parse)
    
    return df


def calculate_extraction_metrics(df: pd.DataFrame, provider_prefix: str) -> Dict[str, Any]:
    """Calculate extraction metrics for a specific LLM provider."""
    print(f"\n📊 Calculating extraction metrics for {provider_prefix}...")
    
    # Get ground truth and predictions
    y_true = df['contains_factual_claim'].values  # BingCheck ground truth
    y_pred_raw = df[f'{provider_prefix}_binary_result'].values  # LLM predictions

    # Filter out None/NaN values (sentences not processed yet)
    valid_mask = pd.notna(y_pred_raw) & (y_pred_raw != 'None') & (y_pred_raw != 'null')
    y_true_filtered = y_true[valid_mask]
    y_pred_raw_filtered = y_pred_raw[valid_mask]

    # Convert predictions to boolean (this addresses the data type casting issue)
    # Handle both string 'True'/'False' and actual boolean values
    y_pred_filtered = []
    for pred in y_pred_raw_filtered:
        if isinstance(pred, bool):
            y_pred_filtered.append(pred)
        elif isinstance(pred, str):
            if pred.lower() in ['true', '1', 'yes', 't']:
                y_pred_filtered.append(True)
            elif pred.lower() in ['false', '0', 'no', 'f']:
                y_pred_filtered.append(False)
            else:
                print(f"Warning: Unexpected prediction value: {pred}, defaulting to False")
                y_pred_filtered.append(False)
        elif pd.isna(pred):
            y_pred_filtered.append(False)  # or could skip this item
        else:
            y_pred_filtered.append(bool(pred))
    
    y_pred_filtered = pd.Series(y_pred_filtered).astype(bool)

    if len(y_true_filtered) == 0:
        print(f"  ⚠️  No processed sentences found for {provider_prefix}")
        return None

    if len(y_true_filtered) != len(y_pred_filtered):
        print(f"  ⚠️  Mismatch in filtered arrays: {len(y_true_filtered)} vs {len(y_pred_filtered)}")
        return None

    # Calculate metrics
    accuracy = accuracy_score(y_true_filtered, y_pred_filtered)
    precision = precision_score(y_true_filtered, y_pred_filtered, zero_division=0)
    recall = recall_score(y_true_filtered, y_pred_filtered, zero_division=0)
    f1 = f1_score(y_true_filtered, y_pred_filtered, zero_division=0)

    # Detailed classification report
    report = classification_report(
        y_true_filtered,
        y_pred_filtered,
        target_names=['No Factual Claim', 'Has Factual Claim'],
        output_dict=True
    )

    # Confusion matrix
    cm = confusion_matrix(y_true_filtered, y_pred_filtered)

    # Calculate TP, TN, FP, FN manually for clarity
    tn, fp, fn, tp = cm.ravel()

    metrics = {
        'provider': provider_prefix,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'confusion_matrix': cm.tolist(),
        'classification_report': report,
        'tp': int(tp),  # True Positives
        'tn': int(tn),  # True Negatives
        'fp': int(fp),  # False Positives
        'fn': int(fn),  # False Negatives
        'total_samples': len(y_true_filtered),
        'processed_samples': len(y_pred_filtered)
    }

    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    print(f"  Samples processed: {len(y_pred_filtered)}/{len(y_true)}")

    return metrics


def create_extractions_comparison_summary(
    gpt4_metrics: Dict[str, Any], 
    gemini_metrics: Dict[str, Any], 
    deepseek_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a summary comparing all three LLMs' extraction performance."""
    
    # Determine winner based on F1-score
    metrics_list = [gpt4_metrics, gemini_metrics, deepseek_metrics]
    winners = []
    
    for metrics in metrics_list:
        if metrics:
            winners.append((metrics['provider'], metrics['f1_score']))
    
    # Sort by F1-score to determine winner
    winners.sort(key=lambda x: x[1], reverse=True)
    extraction_winner = winners[0] if winners else ('unknown', 0.0)
    
    summary = {
        'extraction_winner': extraction_winner[0],
        'winner_f1_score': extraction_winner[1],
        'all_providers_ranking': winners,
        'gpt4_metrics': gpt4_metrics,
        'gemini_metrics': gemini_metrics,
        'deepseek_metrics': deepseek_metrics
    }
    
    return summary


def analyze_extraction_phase(dataset_path: str, output_path: str):
    """Analyze extraction results and create metrics summary."""
    print("🔍 Analyzing extraction phase results...")
    print(f"Dataset: {dataset_path}")
    print(f"Output: {output_path}")
    
    # Load dataset with extractions
    df = load_dataset_with_extractions(dataset_path)
    print(f"Loaded dataset with {len(df)} sentences")
    
    # Calculate metrics for each provider
    gpt4_metrics = calculate_extraction_metrics(df, 'gpt4')
    gemini_metrics = calculate_extraction_metrics(df, 'gemini')
    deepseek_metrics = calculate_extraction_metrics(df, 'deepseek')
    
    # Create comparison summary
    summary = create_extractions_comparison_summary(gpt4_metrics, gemini_metrics, deepseek_metrics)
    
    # Print summary
    print(f"\n🏆 Extraction Winner: {summary['extraction_winner']} (F1-Score: {summary['winner_f1_score']:.4f})")
    print("All providers ranking:")
    for i, (provider, f1_score) in enumerate(summary['all_providers_ranking'], 1):
        print(f"  {i}. {provider}: {f1_score:.4f}")
    
    # Save metrics to CSV
    metrics_data = []
    
    for provider_metrics in [summary['gpt4_metrics'], summary['gemini_metrics'], summary['deepseek_metrics']]:
        if provider_metrics:
            metrics_data.append({
                'provider': provider_metrics['provider'],
                'accuracy': provider_metrics['accuracy'],
                'precision': provider_metrics['precision'],
                'recall': provider_metrics['recall'],
                'f1_score': provider_metrics['f1_score'],
                'tp': provider_metrics['tp'],
                'tn': provider_metrics['tn'],
                'fp': provider_metrics['fp'],
                'fn': provider_metrics['fn'],
                'total_samples': provider_metrics['total_samples']
            })
    
    if metrics_data:
        metrics_df = pd.DataFrame(metrics_data)
        metrics_df.to_csv(output_path, index=False)
        print(f"\n📈 Extraction metrics saved to {output_path}")
    else:
        print("⚠️  No metrics to save")
    
    return summary


def main():
    parser = argparse.ArgumentParser(description="Analyze extraction phase results")
    parser.add_argument(
        "--dataset",
        type=str,
        default="../../my_thesis_dataset.csv",
        help="Path to the dataset CSV file with extraction results"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="../../extraction_metrics.csv",
        help="Path to save extraction metrics CSV file"
    )
    
    args = parser.parse_args()

    print(f"📄 Dataset: {args.dataset}")
    print(f"💾 Output: {args.output}")
    
    # Verify the dataset exists
    if not Path(args.dataset).exists():
        print(f"❌ Dataset file not found: {args.dataset}")
        sys.exit(1)
    
    # Analyze extraction results
    summary = analyze_extraction_phase(args.dataset, args.output)
    
    print("\n✅ Extraction analysis completed successfully!")


if __name__ == "__main__":
    main()