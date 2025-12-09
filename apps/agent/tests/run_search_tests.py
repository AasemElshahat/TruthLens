#!/usr/bin/env python3
"""
Dedicated test runner for search provider integration tests.

This script runs only the search provider tests, allowing for 
cost-effective testing of search functionality separately from LLMs.
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add the parent directory (agent) to Python path to import modules
tests_dir = os.path.dirname(os.path.abspath(__file__))
agent_dir = os.path.dirname(tests_dir)
sys.path.insert(0, agent_dir)

from tests.test_search_integration import SearchProviderIntegrationTester


class SearchTestRunner:
    """Dedicated runner for search provider tests."""
    
    def __init__(self):
        self.test_results = {}
    
    async def run_search_tests(self) -> Dict:
        """Run search provider integration tests and collect results."""
        print("🚀 Starting Search Provider Integration Test Runner")
        print(f"Test run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        tester = SearchProviderIntegrationTester()
        results = await tester.test_all_providers()
        
        summary = {
            "results": results,
            "overall_success": all(r["success"] for r in results),
            "timestamp": datetime.now().isoformat(),
            "test_type": "search_providers"
        }
        
        self.test_results = summary
        return summary
    
    def generate_full_report(self) -> str:
        """Generate a comprehensive test report."""
        results = self.test_results
        
        report = "\n" + "="*80 + "\n"
        report += "SEARCH PROVIDER INTEGRATION TEST REPORT\n"
        report += "="*80 + "\n"
        report += f"Timestamp: {results['timestamp']}\n"
        report += f"Test Type: {results['test_type']}\n"
        report += "\n"
        
        current_provider = None
        for result in results['results']:
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
        successful = sum(1 for r in results['results'] if r['success'])
        total = len(results['results'])
        
        report += f"\n📊 SUMMARY\n"
        report += "-"*40 + "\n"
        report += f"Search Queries: {successful}/{total} successful\n"
        report += f"Overall Status: {'🎉 ALL TESTS PASSED' if results['overall_success'] else '⚠️ SOME TESTS FAILED'}\n"
        
        return report
    
    def save_report(self, filename: str = None) -> str:
        """Save the test report to a file in the test_reports directory."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"search_test_report_{timestamp}.txt"
        
        # Save in the test_reports directory at the agent level (one level up from tests)
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        agent_dir = os.path.dirname(tests_dir)  # Go up one level to get to agent dir
        reports_dir = os.path.join(agent_dir, 'test_reports')
        filepath = os.path.join(reports_dir, filename)
        
        report = self.generate_full_report()
        
        # Ensure the directory exists
        os.makedirs(reports_dir, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return filepath


async def main():
    """Main entry point for the search test runner."""
    # Parse command line arguments
    save_report = False
    
    for arg in sys.argv[1:]:
        if arg == "--save-report":
            save_report = True
        elif arg in ["-h", "--help"]:
            print("Usage: python run_search_tests.py [OPTIONS]")
            print("Options:")
            print("  --save-report  Save test report to file")
            print("  -h, --help     Show this help message")
            return
    
    runner = SearchTestRunner()
    results = await runner.run_search_tests()
    
    report = runner.generate_full_report()
    print(report)
    
    if save_report:
        filename = runner.save_report()
        print(f"\n📋 Report saved to: {filename}")
    
    # Exit with appropriate code
    overall_success = results["overall_success"]
    if overall_success:
        print("\n✅ All search integration tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some search integration tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())