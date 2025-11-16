#!/usr/bin/env python3
"""
Test script to understand the output format of the claim extraction and verification agents.

This will help us design the proper mapping for our thesis results file.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from claim_extractor import graph as claim_extractor_graph
from claim_verifier import graph as claim_verifier_graph
from claim_extractor.schemas import ValidatedClaim
from claim_verifier.schemas import Verdict


async def test_claim_extractor():
    """Test the claim extraction agent to understand its output format."""
    
    print("🧪 Testing Claim Extraction Agent...")
    
    # Use a factual sentence from the BingCheck dataset
    test_sentence = "The invention of the first artificial heart was inspired by the need to save lives of people with heart failure and to overcome the shortage of donor hearts for transplantation."
    
    payload = {
        "answer_text": test_sentence,
        "metadata": "test_thesis"
    }
    
    print(f"Input: {test_sentence}")
    print("-" * 80)
    
    try:
        result = await claim_extractor_graph.ainvoke(payload)
        
        print("Claim Extraction Output Format:")
        print(f"Keys in result: {result.keys()}")
        print(f"Number of contextual_sentences: {len(result.get('contextual_sentences', []))}")
        print(f"Number of selected_contents: {len(result.get('selected_contents', []))}")
        print(f"Number of disambiguated_contents: {len(result.get('disambiguated_contents', []))}")
        print(f"Number of potential_claims: {len(result.get('potential_claims', []))}")
        print(f"Number of validated_claims: {len(result.get('validated_claims', []))}")
        
        # Display validated claims if any
        validated_claims = result.get('validated_claims', [])
        for i, claim in enumerate(validated_claims):
            print(f"\nValidated Claim {i+1}:")
            print(f"  claim_text: {claim.claim_text}")
            print(f"  is_complete_declarative: {claim.is_complete_declarative}")
            print(f"  disambiguated_sentence: {claim.disambiguated_sentence}")
            print(f"  original_sentence: {claim.original_sentence}")
            print(f"  original_index: {claim.original_index}")
            
        return result
        
    except Exception as e:
        print(f"Error in claim extraction: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_claim_verifier():
    """Test the claim verification agent to understand its output format."""
    
    print("\n🧪 Testing Claim Verification Agent...")
    
    # Create a sample validated claim to test verification on
    sample_claim = ValidatedClaim(
        claim_text="The invention of the first artificial heart was inspired by the need to save lives of people with heart failure",
        is_complete_declarative=True,
        disambiguated_sentence="The invention of the first artificial heart was inspired by the need to save lives of people with heart failure",
        original_sentence="The invention of the first artificial heart was inspired by the need to save lives of people with heart failure and to overcome the shortage of donor hearts for transplantation.",
        original_index=0
    )
    
    payload = {
        "claim": sample_claim
    }
    
    print(f"Input claim: {sample_claim.claim_text}")
    print("-" * 80)
    
    try:
        result = await claim_verifier_graph.ainvoke(payload)
        
        print("Claim Verification Output Format:")
        print(f"Keys in result: {result.keys()}")
        
        verdict = result.get('verdict')
        if verdict:
            print(f"\nVerdict found:")
            print(f"  claim_text: {verdict.claim_text}")
            print(f"  result: {verdict.result}")
            print(f"  reasoning: {verdict.reasoning}")
            print(f"  sources: {len(verdict.sources)} sources")
            print(f"  disambiguated_sentence: {verdict.disambiguated_sentence}")
            print(f"  original_sentence: {verdict.original_sentence}")
            print(f"  original_index: {verdict.original_index}")
        else:
            print("No verdict found in result")
            
        return result
        
    except Exception as e:
        print(f"Error in claim verification: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Run the test."""
    print("Testing Agent Output Formats for Thesis Data Structure")
    print("="*60)
    
    # Test claim extraction
    extraction_result = await test_claim_extractor()
    
    # Only test verification if we have a validated claim from extraction
    if extraction_result and extraction_result.get('validated_claims'):
        await test_claim_verifier()
    
    print("\n" + "="*60)
    print("Test completed. This helps us understand how to structure the thesis results.")


if __name__ == "__main__":
    asyncio.run(main())