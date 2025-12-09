#!/usr/bin/env python3
"""
Script to run the verification phase for all three LLMs on the benchmark claims.

This script runs claim verification for all LLMs on the standardized benchmark,
with per-claim updates and resume capability for cost protection.
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

from claim_verifier import graph as claim_verifier_graph
from claim_extractor.schemas import ValidatedClaim
from claim_verifier.schemas import VerificationResult, Evidence


def serialize_sources(sources: Optional[List[Evidence]]) -> str:
    """Convert Evidence objects into a JSON string for CSV storage."""
    if not sources:
        return json.dumps([])

    serialized_sources = []
    for source in sources:
        try:
            serialized_sources.append({
                'url': source.url,
                'title': source.title,
                'text': source.text,
                'is_influential': source.is_influential
            })
        except Exception as exc:  # Defensive: ensure serialization never blocks the run
            print(f"⚠️  Failed to serialize source for URL {getattr(source, 'url', 'unknown')} - {exc}")

    return json.dumps(serialized_sources)


async def run_verification_for_claim(claim_data: Dict, provider: str) -> Dict[str, Any]:
    """
    Run claim verification for a single claim using the specified LLM provider.

    Args:
        claim_data: The claim to verify (as dictionary from JSON)
        provider: The LLM provider to use ('openai', 'gemini', 'deepseek')

    Returns:
        Dictionary with verification results or None if error
    """
    # Update provider for this execution
    from utils.settings import settings
    original_provider = settings.llm_provider
    settings.llm_provider = provider

    try:
        # Create ValidatedClaim object from the claim data
        validated_claim = ValidatedClaim(**claim_data)
        
        payload = {
            "claim": validated_claim
        }

        result = await claim_verifier_graph.ainvoke(payload)

        if result:
            # Extract verification result components
            verdict = result.get('verdict')
            if verdict:
                return {
                    'verdict': verdict.result.value if hasattr(verdict.result, 'value') else str(verdict.result),
                    'reasoning': verdict.reasoning,
                    'sources_count': len(verdict.sources) if hasattr(verdict, 'sources') else 0,
                    'sources': serialize_sources(getattr(verdict, 'sources', [])),
                    'original_claim': validated_claim.claim_text
                }
            else:
                return {
                    'verdict': 'No verdict returned',
                    'reasoning': 'No reasoning provided',
                    'sources_count': 0,
                    'sources': json.dumps([]),
                    'original_claim': validated_claim.claim_text
                }
        else:
            return {
                'verdict': 'No result returned',
                'reasoning': 'No result from verifier',
                'sources_count': 0,
                'sources': json.dumps([]),
                'original_claim': validated_claim.claim_text
            }
    except Exception as e:
        print(f"Error in verification for provider {provider} on claim: {claim_data.get('claim_text', '')[:50]}... - {e}")
        # Return None to indicate error - this allows for retries since the row will remain unprocessed
        return None
    finally:
        # Restore original provider
        settings.llm_provider = original_provider


def add_verification_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add verification result columns to the dataframe if they don't exist."""
    required_columns = [
        'gpt4_verdict', 'gpt4_reasoning', 'gpt4_sources',
        'gemini_verdict', 'gemini_reasoning', 'gemini_sources',
        'deepseek_verdict', 'deepseek_reasoning', 'deepseek_sources'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = None  # Initialize with null values
    
    return df


def is_verification_complete_for_provider(df: pd.DataFrame, provider_prefix: str) -> bool:
    """Check if verification is complete for a particular provider (all claims have results)."""
    verdict_col = f"{provider_prefix}_verdict"
    
    # Check if all non-null values exist for this provider
    return df[verdict_col].notna().all()


def has_verification_result_for_claim(df: pd.DataFrame, idx: int, provider_prefix: str) -> bool:
    """Check if a specific claim has verification results for a particular provider."""
    verdict_col = f"{provider_prefix}_verdict"
    value = df.iloc[idx][verdict_col]
    return pd.notna(value) and value is not None


async def run_verification_for_provider(
    df: pd.DataFrame, 
    provider: str, 
    provider_prefix: str, 
    output_path: str
) -> pd.DataFrame:
    """Run verification for a single provider across all claims with per-claim updates."""
    print(f"🧪 Starting verification for {provider.upper()} provider...")
    
    # Get provider-specific columns
    verdict_col = f"{provider_prefix}_verdict"
    reasoning_col = f"{provider_prefix}_reasoning"
    sources_col = f"{provider_prefix}_sources"
    
    total_claims = len(df)
    processed_count = 0
    
    for idx, row in df.iterrows():
        # Skip if this claim already has verification results for this provider
        if has_verification_result_for_claim(df, idx, provider_prefix):
            print(f"⏭️  Skipping claim {idx + 1}/{total_claims} (already processed for {provider})")
            continue
        
        print(f"Processing claim {idx + 1}/{total_claims} with {provider.upper()}...")
        
        # Get claim data from the JSON column
        claim_data_str = row['validated_claim_object']
        if pd.isna(claim_data_str) or claim_data_str == '':
            print(f"⚠️  Skipping claim {idx + 1} - no claim data")
            continue
            
        try:
            claim_data = json.loads(claim_data_str)
        except json.JSONDecodeError:
            print(f"⚠️  Skipping claim {idx + 1} - invalid JSON")
            continue
        
        # Run verification for this claim
        result = await run_verification_for_claim(claim_data, provider)
        
        # Only update if we got a successful result
        if result is not None:
            # Update the dataframe with results
            df.at[idx, verdict_col] = result['verdict']
            df.at[idx, reasoning_col] = result['reasoning']
            df.at[idx, sources_col] = result.get('sources', json.dumps([]))
            
            processed_count += 1
        else:
            # Keep the cell as None to allow for retries
            print(f"⚠️  Error processing claim {idx + 1}, keeping as None for retry")
        
        # Save immediately to protect against cost loss
        df.to_csv(output_path, index=False)
        print(f"💾 Saved results for claim {idx + 1} to CSV")
        
        # Add a small async delay between API calls to respect rate limits
        await asyncio.sleep(0.1)
    
    print(f"✅ Completed verification for {provider.upper()}: {processed_count} claims processed")
    return df


async def run_verification_phase(
    benchmark_path: str, 
    output_path: str, 
    providers: List[str] = ['openai', 'gemini', 'deepseek']
):
    """Run verification phase for all providers with per-claim updates."""
    print("🚀 Starting verification phase with all LLMs...")
    print(f"Benchmark: {benchmark_path}")
    print(f"Output: {output_path}")
    print(f"Providers: {providers}")
    
    # Load the benchmark claims
    df = pd.read_csv(benchmark_path)
    print(f"Loaded benchmark with {len(df)} claims")
    
    # Add required columns if they don't exist
    df = add_verification_columns(df)
    
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
        
        # Run verification for this provider
        df = await run_verification_for_provider(df, provider, provider_prefix, output_path)
    
    # Final save
    df.to_csv(output_path, index=False)
    print(f"\n🎉 Verification phase complete! Results saved to {output_path}")
    print(f"Final benchmark has {len(df)} claims with verification results from all providers")


async def main():
    parser = argparse.ArgumentParser(description="Run TruthLens verification phase with all LLMs")
    parser.add_argument(
        "--benchmark",
        type=str,
        default="../../my_thesis_benchmark_claims.csv",
        help="Path to the benchmark claims CSV file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="../../my_thesis_benchmark_claims.csv",
        help="Path to save results CSV file (default: same as input for in-place update)"
    )

    args = parser.parse_args()

    print(f"📄 Benchmark: {args.benchmark}")
    print(f"💾 Output: {args.output}")

    # Verify the benchmark exists
    if not Path(args.benchmark).exists():
        print(f"❌ Benchmark file not found: {args.benchmark}")
        sys.exit(1)

    # Run verification phase
    await run_verification_phase(args.benchmark, args.output)

    print("✅ Verification phase completed successfully!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())