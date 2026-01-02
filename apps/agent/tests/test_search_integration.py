#!/usr/bin/env python3
"""
Integration tests for search provider functionality.

These tests verify that all search providers (Brave, Exa, Tavily) 
can successfully connect and return search results.
"""

import asyncio
import os
import sys
from typing import Dict, List

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add the project root to Python path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search.provider import search
from utils.settings import settings


class SearchProviderIntegrationTester:
    """Integration tester for search providers."""
    
    def __init__(self):
        self.test_queries = [
            "TruthLens fact checking system",
            "climate change scientific evidence", 
            "COVID-19 pandemic statistics"
        ]
        self.test_results: Dict[str, List[Dict]] = {}
    
    async def test_provider(self, provider: str, query: str = None) -> Dict:
        """Test a specific search provider."""
        if query is None:
            query = self.test_queries[0]
            
        print(f"\nTesting {provider.upper()} search provider with query: '{query[:50]}{'...' if len(query) > 50 else ''}'")
        
        # Temporarily set the provider
        original_provider = os.getenv("SEARCH_PROVIDER", "brave")
        os.environ["SEARCH_PROVIDER"] = provider
        
        try:
            # Perform search
            results = await search(query, max_results=2)
            
            # Validate results structure
            success = True
            validation_errors = []
            
            if not results:
                success = False
                validation_errors.append("No results returned")
            else:
                for i, result in enumerate(results):
                    if not hasattr(result, 'url') or not result.url:
                        validation_errors.append(f"Result {i}: Missing or empty URL")
                        success = False
                    if not hasattr(result, 'title') or not result.title:
                        validation_errors.append(f"Result {i}: Missing or empty title")
                        success = False
                    if not hasattr(result, 'content') or not result.content:
                        validation_errors.append(f"Result {i}: Missing or empty content")
                        success = False
            
            result_obj = {
                "provider": provider,
                "query": query,
                "results": results,
                "success": success,
                "result_count": len(results),
                "validation_errors": validation_errors,
                "summary": f"{'[OK]' if success else '[FAIL]'} {provider.upper()} search {'succeeded' if success else 'failed'}",
            }
            
            print(f"   {result_obj['summary']}")
            if success:
                print(f"   Retrieved {len(results)} valid results")
                if results:
                    print(f"   First result: '{results[0].title[:60]}{'...' if len(results[0].title) > 60 else ''}'")
            else:
                print(f"   Validation errors: {validation_errors}")
            
            return result_obj
            
        except Exception as e:
            print(f"   [ERROR] Error during search: {str(e)}")
            return {
                "provider": provider,
                "query": query,
                "results": [],
                "success": False,
                "error": str(e),
                "result_count": 0,
                "validation_errors": [f"Exception: {str(e)}"],
                "summary": f"[FAIL] {provider.upper()} search failed with error: {str(e)}"
            }
        finally:
            # Restore original provider
            os.environ["SEARCH_PROVIDER"] = original_provider
    
    async def test_all_providers(self) -> List[Dict]:
        """Test all configured search providers."""
        print("Starting Search Provider Integration Tests...")
        
        # Determine which providers to test based on available API keys
        providers_to_test = []
        
        if settings.brave_api_key:
            providers_to_test.append("brave")
        if settings.exa_api_key:
            providers_to_test.append("exa")
        if settings.tavily_api_key:
            providers_to_test.append("tavily")
        
        if not providers_to_test:
            print("[WARNING] No API keys found for search providers. Testing with default provider only.")
            providers_to_test.append(os.getenv("SEARCH_PROVIDER", "brave"))
        
        print(f"Providers to test: {providers_to_test}")
        
        results = []
        for provider in providers_to_test:
            for i, query in enumerate(self.test_queries[:2]):  # Test with first 2 queries for each provider
                result = await self.test_provider(provider, query)
                results.append(result)
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """Generate a test report."""
        report = "\n" + "="*60 + "\n"
        report += "SEARCH PROVIDER INTEGRATION TEST REPORT\n"
        report += "="*60 + "\n"
        
        current_provider = None
        for result in results:
            # Group by provider
            if current_provider != result['provider']:
                current_provider = result['provider']
                report += f"\nProvider: {result['provider']}\n"
                report += "-" * 30 + "\n"
            
            report += f"Query: '{result['query']}'\n"
            report += f"Status: {result['summary']}\n"
            if result.get('result_count', 0) > 0:
                report += f"Results: {result['result_count']} items\n"
            if result.get('validation_errors'):
                report += f"Validation errors: {result['validation_errors']}\n"
            if result.get('error'):
                report += f"Error: {result['error']}\n"
            report += "\n"
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        report += f"\nSUMMARY: {successful}/{total} search queries successful\n"
        
        if successful == total:
            report += "All search providers working correctly!\n"
        else:
            report += "[WARNING] Some search providers failed - please check API keys and configuration\n"
        
        return report


async def main():
    """Run the search provider integration tests."""
    print(f"Search Provider Integration Test Suite")
    print(f"Default search provider configured: {os.getenv('SEARCH_PROVIDER', 'brave')}")
    
    tester = SearchProviderIntegrationTester()
    results = await tester.test_all_providers()
    report = tester.generate_report(results)
    
    print(report)
    
    # Return success/failure for CI/CD purposes
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    if successful == total:
        print("[DONE] All search integration tests passed!")
        sys.exit(0)
    else:
        print("[FAIL] Some search integration tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())