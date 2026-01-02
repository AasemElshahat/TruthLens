#!/usr/bin/env python3
"""
Script to create benchmark claims from the winning extractor's results.

This script creates my_thesis_benchmark_claims.csv containing only the claims 
from the winning extractor for use in Phase 2 verification.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd


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


def get_winning_extractor_provider(extraction_metrics_path: str) -> str:
    """Get the provider that won the extraction phase."""
    try:
        metrics_df = pd.read_csv(extraction_metrics_path)
        # Find the provider with the highest F1 score
        winner_row = metrics_df.loc[metrics_df['f1_score'].idxmax()]
        winner_provider = winner_row['provider']
        
        # Map provider names back to standardized format
        provider_mapping = {
            'gpt4': 'gpt4',
            'gemini': 'gemini',
            'deepseek': 'deepseek'
        }
        
        return provider_mapping.get(winner_provider, winner_provider)
    except Exception as e:
        print(f"[WARNING] Could not read extraction metrics, defaulting to gpt4: {e}")
        return 'gpt4'


def create_benchmark_claims(dataset_path: str, extraction_metrics_path: str, output_path: str):
    """Create benchmark claims from the winning extractor."""
    print("Creating benchmark claims from winning extractor...")
    print(f"Dataset: {dataset_path}")
    print(f"Extraction Metrics: {extraction_metrics_path}")
    print(f"Output: {output_path}")
    
    # Load dataset with extractions
    df = load_dataset_with_extractions(dataset_path)
    print(f"Loaded dataset with {len(df)} sentences")
    
    # Determine winning extractor
    winning_provider = get_winning_extractor_provider(extraction_metrics_path)
    print(f"Winning extractor: {winning_provider}")
    
    # Get the extraction claims column for the winning provider
    claims_column = f"{winning_provider}_extracted_claims_json"
    
    # Create benchmark claims dataframe
    benchmark_data = []
    benchmark_sentence_counter = 0
    
    for idx, row in df.iterrows():
        sentence_id = row['sentence_id']
        answer_id = row.get('answer_id', '')
        original_sentence = row['sentence']
        contains_factual_claim = row['contains_factual_claim']

        # CRITICAL: Only process sentences that actually contain factual claims
        if contains_factual_claim == True:
            # Get claims from winning extractor for this sentence
            claims = row[claims_column]

            if isinstance(claims, list) and len(claims) > 0:
                benchmark_sentence_counter += 1
                benchmark_sentence_id = benchmark_sentence_counter

                # For each claim from the winning extractor, create a benchmark record
                for claim_idx, claim_data in enumerate(claims):
                    # Ensure the claim_data is properly formatted as a ValidatedClaim dict
                    # This ensures compatibility with the original ValidatedClaim schema
                    validated_claim_dict = {
                        'claim_text': claim_data.get('claim_text', ''),
                        'is_complete_declarative': claim_data.get('is_complete_declarative', True),
                        'disambiguated_sentence': claim_data.get('disambiguated_sentence', ''),
                        'original_sentence': claim_data.get('original_sentence', ''),
                        'original_index': claim_data.get('original_index', 0)
                    }

                    claim_identifier = f"B{benchmark_sentence_id:03d}_C{claim_idx:02d}"

                    benchmark_record = {
                        'claim_id': claim_identifier,
                        'answer_id': answer_id,
                        'original_sentence': original_sentence,
                        'contains_factual_claim_ground_truth': contains_factual_claim,
                        'validated_claim_object': json.dumps(validated_claim_dict),
                        'claim_text': validated_claim_dict['claim_text'],
                        'disambiguated_sentence': validated_claim_dict['disambiguated_sentence'],
                        'ground_truth_verdict': '',  # This will be filled manually in Phase 2
                        'ground_truth_verdict_sources': ''  # This will be filled manually in Phase 2
                    }

                    benchmark_data.append(benchmark_record)
    
    # Create benchmark dataframe
    benchmark_df = pd.DataFrame(benchmark_data)
    
    # Print statistics
    print(f"Created benchmark with {len(benchmark_df)} claims from {len(df)} original sentences")
    
    if len(benchmark_df) > 0:
        sentences_with_claims = benchmark_sentence_counter
        avg_claims_per_sentence = len(benchmark_df) / sentences_with_claims if sentences_with_claims > 0 else 0
        print(f"  - {sentences_with_claims} sentences had claims")
        print(f"  - Average {avg_claims_per_sentence:.2f} claims per sentence")
    
    # Save benchmark claims
    benchmark_df.to_csv(output_path, index=False)
    print(f"\n[DONE] Benchmark claims saved to {output_path}")
    
    return benchmark_df


def main():
    parser = argparse.ArgumentParser(description="Create benchmark claims from winning extractor")
    parser.add_argument(
        "--dataset",
        type=str,
        default="../../my_thesis_dataset.csv",
        help="Path to the dataset CSV file with extraction results"
    )
    parser.add_argument(
        "--extraction-metrics",
        type=str,
        default="../../extraction_metrics.csv",
        help="Path to the extraction metrics CSV file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="../../my_thesis_benchmark_claims.csv",
        help="Path to save benchmark claims CSV file"
    )
    
    args = parser.parse_args()

    print(f"Dataset: {args.dataset}")
    print(f"Extraction Metrics: {args.extraction_metrics}")
    print(f"Output: {args.output}")
    
    # Verify files exist
    if not Path(args.dataset).exists():
        print(f"[ERROR] Dataset file not found: {args.dataset}")
        sys.exit(1)
        
    if not Path(args.extraction_metrics).exists():
        print(f"[WARNING] Extraction metrics file not found: {args.extraction_metrics}")
        print("   Will attempt to determine winning extractor without metrics...")
    
    # Create benchmark claims
    benchmark_df = create_benchmark_claims(args.dataset, args.extraction_metrics, args.output)
    
    print("\n[DONE] Benchmark creation completed successfully!")
    print("Next step: Manually annotate ground_truth_verdict column in the benchmark file")


if __name__ == "__main__":
    main()