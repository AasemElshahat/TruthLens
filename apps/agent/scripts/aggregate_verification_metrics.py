#!/usr/bin/env python3
"""
Verification Phase Metrics Aggregation Script

Aggregates verification metrics across all 3 runs and produces summary statistics.
Simple version - matches the extraction aggregation script.

Usage:
    poetry run python scripts/aggregate_verification_metrics.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Configuration
RESULTS_DIR = Path(__file__).parent.parent.parent.parent / "results" / "verification"
PROVIDERS = ['gpt4', 'gemini', 'deepseek']


def main():
    print("=" * 60)
    print("AGGREGATING VERIFICATION METRICS")
    print("=" * 60)
    
    per_run_dir = RESULTS_DIR / "per_run"
    aggregated_dir = RESULTS_DIR / "aggregated"
    aggregated_dir.mkdir(exist_ok=True)
    
    # Find all run files
    run_files = sorted(per_run_dir.glob("verification_metrics_run*.csv"))
    
    if len(run_files) == 0:
        print("[ERROR] No verification metrics files found!")
        print(f"   Looking in: {per_run_dir}")
        return 1
    
    print(f"[OK] Found {len(run_files)} runs to aggregate")
    
    # Load all runs
    all_runs = []
    for f in run_files:
        run_num = int(f.stem.split('run')[1])
        df = pd.read_csv(f)
        df['run'] = run_num
        all_runs.append(df)
        print(f"  - Loaded {f.name}")
    
    combined = pd.concat(all_runs, ignore_index=True)
    
    # Create simple summary (one row per provider)
    simple_summary = []
    for provider in PROVIDERS:
        pdata = combined[combined['provider'] == provider]
        simple_summary.append({
            'provider': provider,
            'accuracy_mean': pdata['accuracy'].mean(),
            'accuracy_std': pdata['accuracy'].std(),
            'macro_f1_mean': pdata['macro_f1_score'].mean(),
            'macro_f1_std': pdata['macro_f1_score'].std(),
            'supported_f1_mean': pdata['supported_f1_score'].mean(),
            'supported_f1_std': pdata['supported_f1_score'].std(),
            'refuted_f1_mean': pdata['refuted_f1_score'].mean(),
            'refuted_f1_std': pdata['refuted_f1_score'].std(),
            'insufficient_f1_mean': pdata['insufficient_f1_score'].mean(),
            'insufficient_f1_std': pdata['insufficient_f1_score'].std(),
        })
    
    simple_df = pd.DataFrame(simple_summary)
    simple_path = aggregated_dir / "verification_summary_simple.csv"
    simple_df.to_csv(simple_path, index=False)
    print(f"\n[OK] Saved summary to {simple_path}")
    
    # Print formatted summary
    print("\n" + "─" * 60)
    print("VERIFICATION PHASE RESULTS (Mean ± Std across runs)")
    print("─" * 60)
    
    print("\nACCURACY:")
    for provider in PROVIDERS:
        data = combined[combined['provider'] == provider]['accuracy']
        print(f"   {provider.upper():12s}: {data.mean()*100:.1f}% ± {data.std()*100:.1f}%")
    
    print("\nMACRO F1 SCORE:")
    for provider in PROVIDERS:
        data = combined[combined['provider'] == provider]['macro_f1_score']
        print(f"   {provider.upper():12s}: {data.mean():.3f} ± {data.std():.3f}")
    
    print("\nPER-CLASS F1 SCORES:")
    for provider in PROVIDERS:
        pdata = combined[combined['provider'] == provider]
        sup = pdata['supported_f1_score'].mean()
        ref = pdata['refuted_f1_score'].mean()
        ins = pdata['insufficient_f1_score'].mean()
        print(f"   {provider.upper():12s}: Supported={sup:.2f}, Refuted={ref:.2f}, Insufficient={ins:.2f}")
    
    # Best performers
    print("\n" + "─" * 60)
    print("KEY INSIGHTS")
    print("─" * 60)
    
    best_acc = max(PROVIDERS, key=lambda p: combined[combined['provider'] == p]['accuracy'].mean())
    best_f1 = max(PROVIDERS, key=lambda p: combined[combined['provider'] == p]['macro_f1_score'].mean())
    
    print(f"\nBEST PERFORMERS:")
    print(f"   Accuracy:     {best_acc.upper()}")
    print(f"   Macro F1:     {best_f1.upper()}")
    
    print("\n[DONE] Aggregation complete!")
    return 0


if __name__ == "__main__":
    exit(main())
