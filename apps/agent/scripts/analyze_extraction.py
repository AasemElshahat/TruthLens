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

    # Allow for either naming convention so the script tolerates future CSV tweaks
    label_candidates = ['contains_factual_claim', 'binary_ground_truth']
    label_col = next((col for col in label_candidates if col in df.columns), None)
    if not label_col:
        print(f"  ⚠️  None of the expected label columns {label_candidates} exist in dataset")
        return None

    y_true = df[label_col].values
    pred_col = f"{provider_prefix}_binary_result"
    if pred_col not in df.columns:
        print(f"  ⚠️  Missing prediction column '{pred_col}' in dataset")
        return None
    y_pred_series = pd.Series(df[pred_col], dtype="object")
    normalized_pred = y_pred_series.astype(str).str.lower()

    valid_mask = (
        pd.notna(y_true)
        & pd.notna(y_pred_series)
        & (normalized_pred != "none")
        & (normalized_pred != "null")
    )
    y_true_filtered = []
    y_pred_filtered = []
    y_true_raw_filtered = y_true[valid_mask]
    y_pred_raw_filtered = y_pred_series[valid_mask].to_numpy()

    if len(y_true_raw_filtered) == 0:
        print(f"  ⚠️  No valid sentences found for {provider_prefix}")
        return None

    for idx, (truth, pred) in enumerate(zip(y_true_raw_filtered, y_pred_raw_filtered)):
        pred_bool = None
        if isinstance(pred, bool):
            pred_bool = pred
        elif isinstance(pred, str):
            normalized = pred.strip().lower()
            if normalized in {"true", "1", "yes", "t", "y"}:
                pred_bool = True
            elif normalized in {"false", "0", "no", "f", "n"}:
                pred_bool = False
        elif isinstance(pred, (int, float)):
            pred_bool = bool(pred)

        if pred_bool is None:
            print(f"  ⚠️  Unexpected prediction '{pred}' at filtered index {idx}; skipping row")
            continue

        y_true_filtered.append(bool(truth))
        y_pred_filtered.append(pred_bool)

    if not y_true_filtered:
        print(f"  ⚠️  No processed sentences found for {provider_prefix} after cleaning")
        return None

    y_true_filtered = pd.Series(y_true_filtered).astype(bool)
    y_pred_filtered = pd.Series(y_pred_filtered).astype(bool)

    accuracy = accuracy_score(y_true_filtered, y_pred_filtered)
    precision = precision_score(y_true_filtered, y_pred_filtered, zero_division=0)
    recall = recall_score(y_true_filtered, y_pred_filtered, zero_division=0)
    f1 = f1_score(y_true_filtered, y_pred_filtered, zero_division=0)

    report = classification_report(
        y_true_filtered,
        y_pred_filtered,
        labels=[False, True],
        target_names=['No Factual Claim', 'Has Factual Claim'],
        output_dict=True,
        zero_division=0,
    )

    cm = confusion_matrix(y_true_filtered, y_pred_filtered, labels=[False, True])
    tn, fp, fn, tp = cm.ravel()

    metrics = {
        "provider": provider_prefix,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
        "tp": int(tp),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "total_samples": int(len(y_true_filtered)),
    }

    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    print(f"  Samples processed: {len(y_true_filtered)} / {len(df)}")

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