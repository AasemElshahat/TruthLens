#!/usr/bin/env python3
"""
Test script to understand how agents classify sentences as containing factual claims or not.
This will help us determine if Option 1 (sentence-level classification) is realistic.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from claim_extractor import graph as claim_extractor_graph


async def test_factual_sentence():
    """Test with a sentence that contains factual claims."""
    
    print("🧪 Testing Sentence with Factual Claims...")
    
    # Use a factual sentence from the BingCheck dataset
    factual_sentence = "The invention of the first artificial heart was inspired by the need to save lives of people with heart failure and to overcome the shortage of donor hearts for transplantation."
    
    payload = {
        "answer_text": factual_sentence,
        "metadata": "test_thesis"
    }
    
    print(f"Input: {factual_sentence}")
    print("-" * 80)
    
    try:
        result = await claim_extractor_graph.ainvoke(payload)
        
        print("Factual Sentence Analysis:")
        print(f"Number of selected_contents: {len(result.get('selected_contents', []))}")
        print(f"Number of validated_claims: {len(result.get('validated_claims', []))}")
        
        # Check if the sentence was selected as containing verifiable content
        selected_contents = result.get('selected_contents', [])
        validated_claims = result.get('validated_claims', [])
        
        sentence_contains_factual_claim = len(selected_contents) > 0
        print(f"Sentence classified as containing factual claims: {sentence_contains_factual_claim}")
        
        return sentence_contains_factual_claim, result
        
    except Exception as e:
        print(f"Error in factual sentence test: {e}")
        import traceback
        traceback.print_exc()
        return None, None


async def test_non_factual_sentence():
    """Test with a sentence that does NOT contain factual claims."""
    
    print("\n🧪 Testing Sentence WITHOUT Factual Claims...")
    
    # Use a non-factual sentence (opinion, recommendation, speculative)
    non_factual_sentence = "By prioritizing ethical considerations, companies can ensure that their innovations are not only groundbreaking but also socially responsible."
    
    payload = {
        "answer_text": non_factual_sentence,
        "metadata": "test_thesis"
    }
    
    print(f"Input: {non_factual_sentence}")
    print("-" * 80)
    
    try:
        result = await claim_extractor_graph.ainvoke(payload)
        
        print("Non-Factual Sentence Analysis:")
        print(f"Number of selected_contents: {len(result.get('selected_contents', []))}")
        print(f"Number of validated_claims: {len(result.get('validated_claims', []))}")
        
        # Check if the sentence was selected as containing verifiable content
        selected_contents = result.get('selected_contents', [])
        validated_claims = result.get('validated_claims', [])
        
        sentence_contains_factual_claim = len(selected_contents) > 0
        print(f"Sentence classified as containing factual claims: {sentence_contains_factual_claim}")
        
        return sentence_contains_factual_claim, result
        
    except Exception as e:
        print(f"Error in non-factual sentence test: {e}")
        import traceback
        traceback.print_exc()
        return None, None


async def main():
    """Run the tests."""
    print("Testing Sentence Classification for Thesis Option 1")
    print("="*60)
    
    # Test factual sentence
    factual_result, factual_full_result = await test_factual_sentence()
    
    # Test non-factual sentence
    non_factual_result, non_factual_full_result = await test_non_factual_sentence()
    
    print("\n" + "="*60)
    print("Summary for Option 1 (Sentence-Level Classification):")
    print(f"Factual sentence classified correctly: {factual_result}")
    print(f"Non-factual sentence classified correctly: {not non_factual_result}")
    
    if factual_result is not None and non_factual_result is not None:
        print(f"\nOption 1 appears {(factual_result and not non_factual_result)*100:.0f}% accurate on this test")
    
    print("\nThis helps determine if Option 1 is realistic for your thesis.")


if __name__ == "__main__":
    asyncio.run(main())