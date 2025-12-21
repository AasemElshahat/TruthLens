#!/usr/bin/env python3
"""
Extraction Phase Metrics Aggregation Script

Aggregates extraction metrics across all 3 runs and produces summary statistics.

Usage:
    poetry run python scripts/aggregate_extraction_metrics.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Configuration
RESULTS_DIR = Path(__file__).parent.parent.parent.parent / "results" / "extraction"
PROVIDERS = ['gpt4', 'gemini', 'deepseek']


def main():
    print("=" * 60)
    print("AGGREGATING EXTRACTION METRICS")
    print("=" * 60)
    
    per_run_dir = RESULTS_DIR / "per_run"
    aggregated_dir = RESULTS_DIR / "aggregated"
    
    # Find all run files
    run_files = sorted(per_run_dir.glob("extraction_metrics_run*.csv"))
    
    if len(run_files) == 0:
        print("❌ No extraction metrics files found!")
        return 1
    
    print(f"✓ Found {len(run_files)} runs to aggregate")
    
    # Load all runs
    all_runs = []
    for f in run_files:
        run_num = int(f.stem.split('run')[1])
        df = pd.read_csv(f)
        df['run'] = run_num
        all_runs.append(df)
        print(f"  - Loaded {f.name}")
    
    combined = pd.concat(all_runs, ignore_index=True)
    
    # Calculate aggregated metrics per provider
    metrics_to_aggregate = [
        'accuracy', 'f1_score', 
        'precision_positive', 'recall_positive', 'f1_score_positive',
        'precision_negative', 'recall_negative', 'f1_score_negative',
        'tp', 'tn', 'fp', 'fn'
    ]
    
    summary_data = []
    for provider in PROVIDERS:
        provider_data = combined[combined['provider'] == provider]
        
        row = {'provider': provider}
        for metric in metrics_to_aggregate:
            if metric in provider_data.columns:
                values = provider_data[metric]
                row[f'{metric}_mean'] = values.mean()
                row[f'{metric}_std'] = values.std()
                row[f'{metric}_min'] = values.min()
                row[f'{metric}_max'] = values.max()
        
        summary_data.append(row)
    
    summary_df = pd.DataFrame(summary_data)
    
    # Save aggregated summary
    summary_path = aggregated_dir / "extraction_metrics_aggregated.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"\n✓ Saved aggregated metrics to {summary_path}")
    
    # Also save a simplified version for easy thesis use
    simple_summary = []
    for provider in PROVIDERS:
        provider_data = combined[combined['provider'] == provider]
        simple_summary.append({
            'provider': provider,
            'accuracy_mean': provider_data['accuracy'].mean(),
            'accuracy_std': provider_data['accuracy'].std(),
            'f1_mean': provider_data['f1_score'].mean(),
            'f1_std': provider_data['f1_score'].std(),
            'precision_mean': provider_data['precision_positive'].mean(),
            'precision_std': provider_data['precision_positive'].std(),
            'recall_mean': provider_data['recall_positive'].mean(),
            'recall_std': provider_data['recall_positive'].std(),
        })
    
    simple_df = pd.DataFrame(simple_summary)
    simple_path = aggregated_dir / "extraction_summary_simple.csv"
    simple_df.to_csv(simple_path, index=False)
    print(f"✓ Saved simplified summary to {simple_path}")
    
    # Print formatted summary
    print("\n" + "─" * 60)
    print("EXTRACTION PHASE RESULTS (Mean ± Std across 3 runs)")
    print("─" * 60)
    
    print("\n📊 ACCURACY:")
    for provider in PROVIDERS:
        data = combined[combined['provider'] == provider]['accuracy']
        print(f"   {provider.upper():12s}: {data.mean()*100:.1f}% ± {data.std()*100:.1f}%")
    
    print("\n📊 F1 SCORE (Positive Class - Factual Claims):")
    for provider in PROVIDERS:
        data = combined[combined['provider'] == provider]['f1_score_positive']
        print(f"   {provider.upper():12s}: {data.mean():.3f} ± {data.std():.3f}")
    
    print("\n📊 PRECISION (Factual Claim Detection):")
    for provider in PROVIDERS:
        data = combined[combined['provider'] == provider]['precision_positive']
        print(f"   {provider.upper():12s}: {data.mean():.3f} ± {data.std():.3f}")
    
    print("\n📊 RECALL (Factual Claim Detection):")
    for provider in PROVIDERS:
        data = combined[combined['provider'] == provider]['recall_positive']
        print(f"   {provider.upper():12s}: {data.mean():.3f} ± {data.std():.3f}")
    
    # Calculate average confusion matrix values
    print("\n📊 AVERAGE CONFUSION MATRIX VALUES:")
    print(f"   {'Provider':<12} {'TP':>6} {'TN':>6} {'FP':>6} {'FN':>6}")
    for provider in PROVIDERS:
        pdata = combined[combined['provider'] == provider]
        print(f"   {provider.upper():<12} {pdata['tp'].mean():>6.1f} {pdata['tn'].mean():>6.1f} {pdata['fp'].mean():>6.1f} {pdata['fn'].mean():>6.1f}")
    
    # Key insights
    print("\n" + "─" * 60)
    print("KEY INSIGHTS")
    print("─" * 60)
    
    # Best performer
    best_acc = max(PROVIDERS, key=lambda p: combined[combined['provider'] == p]['accuracy'].mean())
    best_f1 = max(PROVIDERS, key=lambda p: combined[combined['provider'] == p]['f1_score'].mean())
    best_prec = max(PROVIDERS, key=lambda p: combined[combined['provider'] == p]['precision_positive'].mean())
    best_recall = max(PROVIDERS, key=lambda p: combined[combined['provider'] == p]['recall_positive'].mean())
    
    print(f"\n🏆 BEST PERFORMERS:")
    print(f"   Accuracy:  {best_acc.upper()}")
    print(f"   F1 Score:  {best_f1.upper()}")
    print(f"   Precision: {best_prec.upper()}")
    print(f"   Recall:    {best_recall.upper()}")
    
    # Consistency analysis
    print(f"\n📉 CONSISTENCY (Lower Std = More Consistent):")
    for provider in PROVIDERS:
        acc_std = combined[combined['provider'] == provider]['accuracy'].std()
        print(f"   {provider.upper():12s}: Accuracy Std = {acc_std*100:.2f}%")
    
    # Trade-off analysis
    print(f"\n⚖️ PRECISION-RECALL TRADE-OFF:")
    for provider in PROVIDERS:
        pdata = combined[combined['provider'] == provider]
        prec = pdata['precision_positive'].mean()
        rec = pdata['recall_positive'].mean()
        diff = prec - rec
        if diff > 0.1:
            style = "High Precision, Lower Recall (Conservative)"
        elif diff < -0.1:
            style = "High Recall, Lower Precision (Aggressive)"
        else:
            style = "Balanced"
        print(f"   {provider.upper():12s}: P={prec:.2f}, R={rec:.2f} → {style}")
    
    print("\n✅ Aggregation complete!")
    return 0


if __name__ == "__main__":
    exit(main())
