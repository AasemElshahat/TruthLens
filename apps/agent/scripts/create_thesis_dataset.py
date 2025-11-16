#!/usr/bin/env python3
"""
Script to create the thesis dataset from BingCheck ground truth data.

This script samples 150 sentences randomly from the BingCheck dataset and creates
the initial structure for manual annotation of ground truth verdicts.
"""

import pandas as pd
import random
from pathlib import Path


def create_thesis_dataset():
    """Create the thesis dataset with 150 randomly sampled sentences."""
    
    # Define file paths
    input_file = Path("../../ground_truth_data-BingCheck/bingcheck.csv")
    output_file = Path("../../my_thesis_dataset.csv")
    
    # Read the BingCheck dataset
    print("Reading BingCheck dataset...")
    df = pd.read_csv(input_file)
    
    print(f"Dataset contains {len(df)} sentences")
    print(f"Columns: {list(df.columns)}")
    
    # Randomly sample 150 sentences
    print("Sampling 150 sentences randomly...")
    if len(df) >= 150:
        sampled_df = df.sample(n=150, random_state=42)  # Using fixed seed for reproducibility
    else:
        print(f"Warning: Dataset only has {len(df)} sentences, using all of them")
        sampled_df = df
    
    # Reset index to ensure clean numbering
    sampled_df = sampled_df.reset_index(drop=True)
    
    # Add the ground_truth_verdict column for manual annotation
    sampled_df['ground_truth_verdict'] = None  # Will be filled manually later
    
    # Display basic statistics
    factual_claim_count = sampled_df['contains_factual_claim'].sum()
    print(f"Sampled dataset contains {len(sampled_df)} sentences")
    print(f"Of which {factual_claim_count} contain factual claims (from BingCheck ground truth)")
    print(f"Percentage with factual claims: {factual_claim_count/len(sampled_df)*100:.1f}%")
    
    # Display first few rows as sample
    print("\nFirst 5 rows of the sampled dataset:")
    print(sampled_df[['sentence_id', 'sentence', 'contains_factual_claim', 'ground_truth_verdict']].head())
    
    # Save to CSV
    sampled_df.to_csv(output_file, index=False)
    print(f"\nDataset saved to {output_file}")
    
    # Print some examples of sentences with factual claims for manual review
    factual_sentences = sampled_df[sampled_df['contains_factual_claim'] == True].head(10)
    print("\nSample factual sentences for manual annotation (ground_truth_verdict):")
    for idx, row in factual_sentences.iterrows():
        print(f"  {idx}: {row['sentence']}")
        print(f"     Question context: {row['question']}")
        print()
    
    # Print some examples of sentences without factual claims
    non_factual_sentences = sampled_df[sampled_df['contains_factual_claim'] == False].head(5)
    print("\nSample non-factual sentences (no manual annotation needed for verification):")
    for idx, row in non_factual_sentences.iterrows():
        print(f"  {idx}: {row['sentence']}")
        print(f"     Question context: {row['question']}")
        print()
    
    return sampled_df


if __name__ == "__main__":
    create_thesis_dataset()