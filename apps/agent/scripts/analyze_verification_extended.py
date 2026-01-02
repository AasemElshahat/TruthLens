#!/usr/bin/env python3
"""
Extended Verification Analysis Script

This script performs comprehensive analysis of verification results including:
1. Basic metrics (accuracy, precision, recall, F1) - per run
2. Inter-model agreement metrics (Fleiss' Kappa, Cohen's Kappa)
3. Error pattern analysis
4. Claim difficulty analysis
5. Cross-run aggregation (after all runs complete)

Usage:
    # After each run:
    poetry run python scripts/analyze_verification_extended.py --run 1 --benchmark ../../my_thesis_benchmark_claims_run1.csv
    
    # After all 3 runs (aggregates everything):
    poetry run python scripts/analyze_verification_extended.py --aggregate
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import cohen_kappa_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# CONFIGURATION
# ============================================================================

RESULTS_DIR = Path(__file__).parent.parent.parent.parent / "results" / "verification"
PROVIDERS = ['gpt4', 'gemini', 'deepseek']
VERDICT_CLASSES = ['supported', 'refuted', 'insufficient_information']


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def normalize_verdict(v):
    """Normalize verdict strings to consistent format."""
    if pd.isna(v):
        return v
    v = str(v).lower().strip()
    if 'insufficient' in v:
        return 'insufficient_information'
    elif 'refuted' in v:
        return 'refuted'
    elif 'supported' in v:
        return 'supported'
    return v


def fleiss_kappa(ratings_matrix):
    """
    Calculate Fleiss' Kappa for inter-rater reliability.
    
    Args:
        ratings_matrix: numpy array of shape (n_subjects, n_categories)
                       where each cell is the count of raters who assigned that category
    
    Returns:
        Fleiss' Kappa score
    """
    n_subjects, n_categories = ratings_matrix.shape
    n_raters = ratings_matrix.sum(axis=1)[0]  # Assuming all subjects have same number of raters
    
    # Proportion of all assignments to each category
    p_j = ratings_matrix.sum(axis=0) / (n_subjects * n_raters)
    
    # For each subject, calculate P_i (extent of agreement)
    P_i = (ratings_matrix.sum(axis=1) ** 2 - ratings_matrix.sum(axis=1)) / (n_raters * (n_raters - 1))
    P_i = ((ratings_matrix ** 2).sum(axis=1) - n_raters) / (n_raters * (n_raters - 1))
    
    # Mean of P_i
    P_bar = P_i.mean()
    
    # Expected agreement by chance
    P_e = (p_j ** 2).sum()
    
    # Fleiss' Kappa
    if P_e == 1:
        return 1.0
    kappa = (P_bar - P_e) / (1 - P_e)
    
    return kappa


def calculate_inter_model_agreement(df):
    """Calculate all inter-model agreement metrics."""
    results = {}
    
    # Normalize verdicts
    gt = df['ground_truth_verdict'].apply(normalize_verdict)
    predictions = {p: df[f'{p}_verdict'].apply(normalize_verdict) for p in PROVIDERS}
    
    # 1. Pairwise agreement percentages
    for i, p1 in enumerate(PROVIDERS):
        for p2 in PROVIDERS[i+1:]:
            agreement = (predictions[p1] == predictions[p2]).mean()
            results[f'{p1}_{p2}_agreement'] = agreement
    
    # 2. All three agree percentage
    all_agree = ((predictions['gpt4'] == predictions['gemini']) & 
                 (predictions['gemini'] == predictions['deepseek'])).mean()
    results['all_three_agree_pct'] = all_agree
    
    # 3. Cohen's Kappa for each model vs ground truth
    for provider in PROVIDERS:
        try:
            kappa = cohen_kappa_score(gt, predictions[provider])
            results[f'cohens_kappa_{provider}'] = kappa
        except:
            results[f'cohens_kappa_{provider}'] = np.nan
    
    # 4. Fleiss' Kappa (all 3 models as raters)
    # Create ratings matrix: each row is a claim, each column is a verdict category
    n_claims = len(df)
    ratings_matrix = np.zeros((n_claims, len(VERDICT_CLASSES)))
    
    for idx in range(n_claims):
        for provider in PROVIDERS:
            verdict = predictions[provider].iloc[idx]
            if verdict in VERDICT_CLASSES:
                col_idx = VERDICT_CLASSES.index(verdict)
                ratings_matrix[idx, col_idx] += 1
    
    try:
        results['fleiss_kappa'] = fleiss_kappa(ratings_matrix)
    except:
        results['fleiss_kappa'] = np.nan
    
    return results


def analyze_error_patterns(df):
    """Analyze types of errors each model makes."""
    gt = df['ground_truth_verdict'].apply(normalize_verdict)
    results = {}
    
    for provider in PROVIDERS:
        pred = df[f'{provider}_verdict'].apply(normalize_verdict)
        
        # Error counts
        results[f'{provider}_errors_total'] = (pred != gt).sum()
        results[f'{provider}_over_cautious'] = ((gt == 'supported') & (pred == 'insufficient_information')).sum()
        results[f'{provider}_wrong_rejection'] = ((gt == 'supported') & (pred == 'refuted')).sum()
        results[f'{provider}_over_confident_supported'] = ((gt == 'insufficient_information') & (pred == 'supported')).sum()
        results[f'{provider}_over_confident_refuted'] = ((gt == 'insufficient_information') & (pred == 'refuted')).sum()
        results[f'{provider}_wrong_direction'] = (
            ((gt == 'refuted') & (pred == 'supported')).sum() + 
            ((gt == 'supported') & (pred == 'refuted')).sum()
        )
    
    return results


def identify_difficult_claims(df):
    """Identify claims that were difficult for models."""
    gt = df['ground_truth_verdict'].apply(normalize_verdict)
    predictions = {p: df[f'{p}_verdict'].apply(normalize_verdict) for p in PROVIDERS}
    
    # Count correct predictions per claim
    df_analysis = df.copy()
    df_analysis['num_correct'] = sum(
        (predictions[p] == gt).astype(int) for p in PROVIDERS
    )
    
    # Classify difficulty
    df_analysis['difficulty'] = df_analysis['num_correct'].map({
        0: 'very_hard',  # All models wrong
        1: 'hard',       # 2 models wrong
        2: 'medium',     # 1 model wrong
        3: 'easy'        # All models correct
    })
    
    # Identify failure pattern
    def get_failure_pattern(row):
        patterns = []
        for p in PROVIDERS:
            pred = predictions[p].loc[row.name]
            actual = gt.loc[row.name]
            if pred != actual:
                patterns.append(f'{p}:{pred}')
        return '|'.join(patterns) if patterns else 'none'
    
    df_analysis['failure_pattern'] = df_analysis.apply(get_failure_pattern, axis=1)
    
    # Select columns for output
    output_cols = [
        'claim_id', 'claim_text', 'ground_truth_verdict',
        'gpt4_verdict', 'gemini_verdict', 'deepseek_verdict',
        'num_correct', 'difficulty', 'failure_pattern'
    ]
    
    return df_analysis[output_cols].sort_values('num_correct')


def calculate_verdict_distribution(df):
    """Calculate verdict distribution per model."""
    results = {}
    
    for provider in PROVIDERS:
        col = f'{provider}_verdict'
        verdicts = df[col].apply(normalize_verdict)
        for verdict in VERDICT_CLASSES:
            results[f'{provider}_{verdict}_count'] = (verdicts == verdict).sum()
    
    # Ground truth distribution
    gt = df['ground_truth_verdict'].apply(normalize_verdict)
    for verdict in VERDICT_CLASSES:
        results[f'ground_truth_{verdict}_count'] = (gt == verdict).sum()
    
    return results


# ============================================================================
# MAIN ANALYSIS FUNCTIONS
# ============================================================================

def analyze_single_run(benchmark_path: Path, run_number: int):
    """Analyze a single verification run."""
    print(f"\n{'='*60}")
    print(f"ANALYZING VERIFICATION RUN {run_number}")
    print(f"{'='*60}")
    
    # Load data
    df = pd.read_csv(benchmark_path)
    print(f"[OK] Loaded {len(df)} claims from {benchmark_path.name}")
    
    # 1. Inter-model agreement
    print("\nCalculating inter-model agreement metrics...")
    agreement_metrics = calculate_inter_model_agreement(df)
    
    # 2. Error patterns
    print("Analyzing error patterns...")
    error_patterns = analyze_error_patterns(df)
    
    # 3. Verdict distribution
    print("Calculating verdict distributions...")
    distributions = calculate_verdict_distribution(df)
    
    # 4. Difficult claims
    print("Identifying difficult claims...")
    difficult_claims = identify_difficult_claims(df)
    
    # Save results
    per_run_dir = RESULTS_DIR / "per_run"
    claim_level_dir = RESULTS_DIR / "claim_level"
    
    # Save inter-model agreement
    agreement_df = pd.DataFrame([{
        'run': run_number,
        **agreement_metrics,
        **error_patterns,
        **distributions
    }])
    agreement_path = per_run_dir / f"inter_model_metrics_run{run_number}.csv"
    agreement_df.to_csv(agreement_path, index=False)
    print(f"[OK] Saved inter-model metrics to {agreement_path.name}")
    
    # Save difficult claims
    difficult_path = claim_level_dir / f"claim_analysis_run{run_number}.csv"
    difficult_claims.to_csv(difficult_path, index=False)
    print(f"[OK] Saved claim analysis to {difficult_path.name}")
    
    # Print summary
    print_run_summary(agreement_metrics, error_patterns, distributions, difficult_claims)
    
    return agreement_metrics, error_patterns, distributions


def print_run_summary(agreement, errors, distributions, difficult_claims):
    """Print a formatted summary of the run analysis."""
    print(f"\n{'─'*60}")
    print("SUMMARY")
    print(f"{'─'*60}")
    
    print("\nINTER-MODEL AGREEMENT:")
    print(f"   All 3 agree:        {agreement['all_three_agree_pct']*100:.1f}%")
    print(f"   GPT-4 & Gemini:     {agreement['gpt4_gemini_agreement']*100:.1f}%")
    print(f"   GPT-4 & DeepSeek:   {agreement['gpt4_deepseek_agreement']*100:.1f}%")
    print(f"   Gemini & DeepSeek:  {agreement['gemini_deepseek_agreement']*100:.1f}%")
    print(f"   Fleiss' Kappa:      {agreement['fleiss_kappa']:.3f}")
    
    print("\nCOHEN'S KAPPA (vs Ground Truth):")
    for p in PROVIDERS:
        kappa = agreement[f'cohens_kappa_{p}']
        interpretation = (
            "Poor" if kappa < 0.2 else
            "Fair" if kappa < 0.4 else
            "Moderate" if kappa < 0.6 else
            "Substantial" if kappa < 0.8 else
            "Almost Perfect"
        )
        print(f"   {p.upper():12s}: {kappa:.3f} ({interpretation})")
    
    print("\nERROR PATTERNS:")
    for p in PROVIDERS:
        total = errors[f'{p}_errors_total']
        cautious = errors[f'{p}_over_cautious']
        wrong_rej = errors[f'{p}_wrong_rejection']
        over_sup = errors[f'{p}_over_confident_supported']
        print(f"   {p.upper():12s}: {total} errors (cautious:{cautious}, wrong_rej:{wrong_rej}, over_conf:{over_sup})")
    
    print("\nCLAIM DIFFICULTY DISTRIBUTION:")
    difficulty_counts = difficult_claims['difficulty'].value_counts()
    for diff in ['easy', 'medium', 'hard', 'very_hard']:
        count = difficulty_counts.get(diff, 0)
        print(f"   {diff:12s}: {count} claims")
    
    # Show hardest claims
    very_hard = difficult_claims[difficult_claims['difficulty'] == 'very_hard']
    if len(very_hard) > 0:
        print(f"\nCLAIMS ALL MODELS GOT WRONG ({len(very_hard)}):")
        for _, row in very_hard.head(5).iterrows():
            claim_preview = row['claim_text'][:50] + "..." if len(row['claim_text']) > 50 else row['claim_text']
            print(f'   • "{claim_preview}"')
            print(f"     GT: {row['ground_truth_verdict']} | Pattern: {row['failure_pattern']}")


def aggregate_all_runs():
    """Aggregate metrics across all completed runs."""
    print(f"\n{'='*60}")
    print("AGGREGATING ALL VERIFICATION RUNS")
    print(f"{'='*60}")
    
    per_run_dir = RESULTS_DIR / "per_run"
    aggregated_dir = RESULTS_DIR / "aggregated"
    
    # Find all run files
    run_files = sorted(per_run_dir.glob("inter_model_metrics_run*.csv"))
    
    if len(run_files) == 0:
        print("[ERROR] No run files found. Run analysis on individual runs first.")
        return
    
    print(f"[OK] Found {len(run_files)} runs to aggregate")
    
    # Load all runs
    all_runs = pd.concat([pd.read_csv(f) for f in run_files], ignore_index=True)
    
    # Calculate mean and std for numeric columns
    numeric_cols = all_runs.select_dtypes(include=[np.number]).columns.drop('run', errors='ignore')
    
    summary_data = []
    for col in numeric_cols:
        summary_data.append({
            'metric': col,
            'mean': all_runs[col].mean(),
            'std': all_runs[col].std(),
            'min': all_runs[col].min(),
            'max': all_runs[col].max(),
            'run1': all_runs[all_runs['run'] == 1][col].values[0] if 1 in all_runs['run'].values else np.nan,
            'run2': all_runs[all_runs['run'] == 2][col].values[0] if 2 in all_runs['run'].values else np.nan,
            'run3': all_runs[all_runs['run'] == 3][col].values[0] if 3 in all_runs['run'].values else np.nan,
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Save aggregated summary
    summary_path = aggregated_dir / "verification_summary_aggregated.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"[OK] Saved aggregated summary to {summary_path.name}")
    
    # Also load and combine the basic verification metrics
    basic_metrics_files = sorted(Path(__file__).parent.parent.parent.parent.glob("verification_metrics_run*.csv"))
    if basic_metrics_files:
        all_basic = pd.concat([
            pd.read_csv(f).assign(run=int(f.stem.split('run')[1])) 
            for f in basic_metrics_files
        ], ignore_index=True)
        
        # Pivot for easier reading: one row per provider with mean/std
        providers_summary = []
        for provider in PROVIDERS:
            provider_data = all_basic[all_basic['provider'] == provider]
            providers_summary.append({
                'provider': provider,
                'accuracy_mean': provider_data['accuracy'].mean(),
                'accuracy_std': provider_data['accuracy'].std(),
                'macro_f1_mean': provider_data['macro_f1_score'].mean(),
                'macro_f1_std': provider_data['macro_f1_score'].std(),
                'supported_f1_mean': provider_data['supported_f1_score'].mean(),
                'supported_f1_std': provider_data['supported_f1_score'].std(),
                'refuted_f1_mean': provider_data['refuted_f1_score'].mean(),
                'refuted_f1_std': provider_data['refuted_f1_score'].std(),
                'insufficient_f1_mean': provider_data['insufficient_f1_score'].mean(),
                'insufficient_f1_std': provider_data['insufficient_f1_score'].std(),
            })
        
        providers_df = pd.DataFrame(providers_summary)
        providers_path = aggregated_dir / "provider_metrics_aggregated.csv"
        providers_df.to_csv(providers_path, index=False)
        print(f"[OK] Saved provider metrics to {providers_path.name}")
    
    # Print aggregated summary
    print_aggregated_summary(summary_df, len(run_files))
    
    # Aggregate difficult claims across runs
    aggregate_difficult_claims()


def aggregate_difficult_claims():
    """Find claims that were consistently difficult across runs."""
    claim_level_dir = RESULTS_DIR / "claim_level"
    aggregated_dir = RESULTS_DIR / "aggregated"
    
    claim_files = sorted(claim_level_dir.glob("claim_analysis_run*.csv"))
    
    if len(claim_files) < 2:
        print("[WARNING] Need at least 2 runs to aggregate claim difficulty")
        return
    
    # Load all claim analyses
    all_claims = []
    for f in claim_files:
        run_num = int(f.stem.split('run')[1])
        df = pd.read_csv(f)
        df['run'] = run_num
        all_claims.append(df)
    
    combined = pd.concat(all_claims, ignore_index=True)
    
    # Calculate average difficulty per claim
    difficulty_map = {'easy': 3, 'medium': 2, 'hard': 1, 'very_hard': 0}
    combined['difficulty_score'] = combined['difficulty'].map(difficulty_map)
    
    claim_summary = combined.groupby('claim_id').agg({
        'claim_text': 'first',
        'ground_truth_verdict': 'first',
        'num_correct': 'mean',
        'difficulty_score': 'mean'
    }).reset_index()
    
    claim_summary['avg_difficulty'] = claim_summary['difficulty_score'].map(
        lambda x: 'very_hard' if x < 0.5 else 'hard' if x < 1.5 else 'medium' if x < 2.5 else 'easy'
    )
    
    claim_summary = claim_summary.sort_values('difficulty_score')
    
    # Save
    output_path = aggregated_dir / "claim_difficulty_aggregated.csv"
    claim_summary.to_csv(output_path, index=False)
    print(f"[OK] Saved aggregated claim difficulty to {output_path.name}")
    
    # Show consistently hard claims
    very_hard = claim_summary[claim_summary['avg_difficulty'] == 'very_hard']
    if len(very_hard) > 0:
        print(f"\nCONSISTENTLY DIFFICULT CLAIMS ({len(very_hard)}):")
        for _, row in very_hard.head(5).iterrows():
            preview = row['claim_text'][:60] + "..." if len(row['claim_text']) > 60 else row['claim_text']
            print(f'   • "{preview}"')
            print(f"     GT: {row['ground_truth_verdict']} | Avg correct: {row['num_correct']:.1f}/3")


def print_aggregated_summary(summary_df, num_runs):
    """Print formatted aggregated summary."""
    print(f"\n{'─'*60}")
    print(f"AGGREGATED SUMMARY ({num_runs} runs)")
    print(f"{'─'*60}")
    
    # Key metrics
    key_metrics = [
        ('all_three_agree_pct', 'All 3 Models Agree'),
        ('fleiss_kappa', "Fleiss' Kappa"),
        ('cohens_kappa_gpt4', "Cohen's Kappa (GPT-4)"),
        ('cohens_kappa_gemini', "Cohen's Kappa (Gemini)"),
        ('cohens_kappa_deepseek', "Cohen's Kappa (DeepSeek)"),
    ]
    
    print("\nKEY METRICS (Mean +/- Std):")
    for metric, label in key_metrics:
        row = summary_df[summary_df['metric'] == metric]
        if len(row) > 0:
            mean = row['mean'].values[0]
            std = row['std'].values[0]
            if 'pct' in metric or 'agreement' in metric:
                print(f"   {label:30s}: {mean*100:.1f}% ± {std*100:.1f}%")
            else:
                print(f"   {label:30s}: {mean:.3f} ± {std:.3f}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Extended verification analysis")
    parser.add_argument('--run', type=int, help='Run number (1, 2, or 3)')
    parser.add_argument('--benchmark', type=str, help='Path to benchmark CSV')
    parser.add_argument('--aggregate', action='store_true', help='Aggregate all completed runs')
    
    args = parser.parse_args()
    
    # Ensure results directories exist
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "per_run").mkdir(exist_ok=True)
    (RESULTS_DIR / "aggregated").mkdir(exist_ok=True)
    (RESULTS_DIR / "claim_level").mkdir(exist_ok=True)
    
    if args.aggregate:
        aggregate_all_runs()
    elif args.run and args.benchmark:
        benchmark_path = Path(args.benchmark)
        if not benchmark_path.exists():
            print(f"[ERROR] Benchmark file not found: {benchmark_path}")
            return 1
        analyze_single_run(benchmark_path, args.run)
    else:
        print("Usage:")
        print("  Analyze single run:")
        print("    poetry run python scripts/analyze_verification_extended.py --run 1 --benchmark ../../my_thesis_benchmark_claims_run1.csv")
        print("")
        print("  Aggregate all runs:")
        print("    poetry run python scripts/analyze_verification_extended.py --aggregate")
        return 1
    
    print("\n[DONE] Analysis complete!")
    return 0


if __name__ == "__main__":
    exit(main())
