#!/usr/bin/env python3
"""
Script to run the extraction phase for all three LLMs (OpenAI, Gemini, DeepSeek)
on the thesis dataset with per-sentence updates and resume capability for cost protection.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

import pandas as pd

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from claim_extractor import graph as claim_extractor_graph
from claim_extractor.schemas import ValidatedClaim


def get_llm_provider(provider: str):
    """Get the configured LLM provider for dynamic switching during execution."""
    from utils.settings import settings

    # Store the original provider
    original_provider = settings.llm_provider

    # Update the provider setting
    settings.llm_provider = provider

    return settings


async def run_extraction_for_sentence(sentence: str, provider: str) -> Dict[str, Any]:
    """
    Run claim extraction for a single sentence using the specified LLM provider.

    Args:
        sentence: The sentence to analyze
        provider: The LLM provider to use ('openai', 'gemini', 'deepseek')

    Returns:
        Dictionary with extraction results or None if error
    """
    # Update provider for this execution
    from utils.settings import settings
    original_provider = settings.llm_provider
    settings.llm_provider = provider

    try:
        payload = {
            "answer_text": sentence,
            "metadata": f"extraction-{provider}"
        }

        result = await claim_extractor_graph.ainvoke(payload)

        selected_contents = result.get('selected_contents', [])
        validated_claims = result.get('validated_claims', [])

        # Determine if the sentence contains factual claims based on validated claims
        contains_factual_claims = len(validated_claims) > 0
        num_validated_claims = len(validated_claims)

        # Convert validated claims to JSON-serializable format
        claims_json = [claim.dict() for claim in validated_claims] if validated_claims else []

        return {
            'extracted_claims_json': json.dumps(claims_json),
            'binary_result': contains_factual_claims,
            'num_claims': num_validated_claims
        }
    except Exception as e:
        print(f"Error in extraction for provider {provider} on sentence: {sentence[:50]}... - {e}")
        # Return None to indicate error - this allows for retries since the row will remain unprocessed
        return None
    finally:
        # Restore original provider
        settings.llm_provider = original_provider


def add_extraction_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add extraction result columns to the dataframe if they don't exist."""
    required_columns = [
        'gpt4_extracted_claims_json', 'gpt4_binary_result', 'gpt4_num_claims',
        'gemini_extracted_claims_json', 'gemini_binary_result', 'gemini_num_claims',
        'deepseek_extracted_claims_json', 'deepseek_binary_result', 'deepseek_num_claims'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = None  # Initialize with null values
    
    return df


def is_extraction_complete_for_provider(df: pd.DataFrame, provider_prefix: str) -> bool:
    """Check if extraction is complete for a particular provider (all sentences have results)."""
    binary_col = f"{provider_prefix}_binary_result"
    
    # Check if all non-null values exist for this provider (excluding actual error values)
    non_empty_mask = df[binary_col].notna()
    # Consider non-None values as completed
    completed_mask = non_empty_mask
    return completed_mask.all()


def has_extraction_result_for_sentence(df: pd.DataFrame, idx: int, provider_prefix: str) -> bool:
    """Check if a specific sentence has extraction results for a particular provider."""
    binary_col = f"{provider_prefix}_binary_result"
    value = df.iloc[idx][binary_col]
    return pd.notna(value) and value is not None


async def run_extraction_for_provider(
    df: pd.DataFrame, 
    provider: str, 
    provider_prefix: str, 
    output_path: str
) -> pd.DataFrame:
    """Run extraction for a single provider across all sentences with per-sentence updates."""
    print(f"🧪 Starting extraction for {provider.upper()} provider...")
    
    # Get provider-specific columns
    json_col = f"{provider_prefix}_extracted_claims_json"
    binary_col = f"{provider_prefix}_binary_result"
    num_claims_col = f"{provider_prefix}_num_claims"
    
    total_sentences = len(df)
    processed_count = 0
    
    for idx, row in df.iterrows():
        # Skip if this sentence already has extraction results for this provider
        if has_extraction_result_for_sentence(df, idx, provider_prefix):
            print(f"⏭️  Skipping sentence {idx + 1}/{total_sentences} (already processed for {provider})")
            continue
        
        print(f"Processing sentence {idx + 1}/{total_sentences} with {provider.upper()}...")
        
        sentence = row['sentence']
        
        # Run extraction for this sentence
        result = await run_extraction_for_sentence(sentence, provider)
        
        # Only update if we got a successful result
        if result is not None:
            # Update the dataframe with results
            df.at[idx, json_col] = result['extracted_claims_json']
            df.at[idx, binary_col] = result['binary_result']
            df.at[idx, num_claims_col] = result['num_claims']
        
            processed_count += 1
        else:
            # Keep the cell as None to allow for retries
            print(f"⚠️  Error processing sentence {idx + 1}, keeping as None for retry")
        
        # Save immediately to protect against cost loss
        df.to_csv(output_path, index=False)
        print(f"💾 Saved results for sentence {idx + 1} to CSV")
        
        # Add a small async delay between API calls to respect rate limits
        await asyncio.sleep(0.1)
    
    print(f"✅ Completed extraction for {provider.upper()}: {processed_count} sentences processed")
    return df


async def run_extraction_phase(
    dataset_path: str, 
    output_path: str, 
    providers: List[str] = ['openai', 'gemini', 'deepseek']
):
    """Run extraction phase for all providers with per-sentence updates."""
    print("🚀 Starting extraction phase with all LLMs...")
    print(f"Dataset: {dataset_path}")
    print(f"Output: {output_path}")
    print(f"Providers: {providers}")
    
    # Load the dataset
    df = pd.read_csv(dataset_path)
    print(f"Loaded dataset with {len(df)} sentences")
    
    # Add required columns if they don't exist
    df = add_extraction_columns(df)
    
    # Provider mappings
    provider_mapping = {
        'openai': 'gpt4',
        'gemini': 'gemini', 
        'deepseek': 'deepseek'
    }
    
    # Process each provider sequentially
    for provider in providers:
        provider_prefix = provider_mapping[provider]
        
        print(f"\n🔄 Processing provider: {provider.upper()}")
        
        # Run extraction for this provider
        df = await run_extraction_for_provider(df, provider, provider_prefix, output_path)
    
    # Final save
    df.to_csv(output_path, index=False)
    print(f"\n🎉 Extraction phase complete! Results saved to {output_path}")
    print(f"Final dataset has {len(df)} sentences with extraction results from all providers")


async def main():
    parser = argparse.ArgumentParser(description="Run TruthLens extraction phase with all LLMs")
    parser.add_argument(
        "--dataset",
        type=str,
        default="../../my_thesis_dataset.csv",
        help="Path to the dataset CSV file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="../../my_thesis_dataset.csv",
        help="Path to save results CSV file (default: same as input for in-place update)"
    )

    args = parser.parse_args()

    print(f"📄 Dataset: {args.dataset}")
    print(f"💾 Output: {args.output}")

    # Verify the dataset exists
    if not Path(args.dataset).exists():
        print(f"❌ Dataset file not found: {args.dataset}")
        sys.exit(1)

    # Run extraction phase
    await run_extraction_phase(args.dataset, args.output)

    print("✅ Extraction phase completed successfully!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())