#!/usr/bin/env python3
"""
Unified test runner for TruthLens integration tests.

This script runs all integration tests for LLM providers, agents, and search providers,
providing a comprehensive verification of the system.
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

from tests.test_llm_provider_integration import LLMProviderIntegrationTester
from tests.test_agent_integration import AgentIntegrationTester
from tests.test_search_integration import SearchProviderIntegrationTester
from utils.settings import settings


class UnifiedIntegrationTestRunner:
    """Unified test runner for TruthLens integration tests."""
    
    def __init__(self):
        self.test_results = {}
    
    async def run_all_tests(self, include_search=True) -> Dict:
        """Run all integration tests and collect results."""
        print("🚀 Starting TruthLens Unified Integration Test Suite")
        print(f"Default provider configured: {settings.llm_provider}")
        print(f"Test run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        results = {}
        
        # Run LLM provider tests
        print("\n🔬 Running LLM Provider Integration Tests...")
        llm_tester = LLMProviderIntegrationTester()
        provider_results = await llm_tester.test_all_providers()
        results["llm_providers"] = {
            "results": provider_results,
            "overall_success": all(r["overall_success"] for r in provider_results)
        }
        
        print("\n" + "-" * 80)
        
        # Run agent integration tests
        print("\n🤖 Running Agent Integration Tests...")
        agent_tester = AgentIntegrationTester()
        agent_results = await agent_tester.test_all_providers()
        results["agents"] = {
            "results": agent_results,
            "overall_success": all(r["overall_success"] for r in agent_results)
        }
        
        # Run search provider tests if requested
        if include_search:
            print("\n" + "-" * 80)
            print("\n🔍 Running Search Provider Integration Tests...")
            search_tester = SearchProviderIntegrationTester()
            search_results = await search_tester.test_all_providers()
            results["search"] = {
                "results": search_results,
                "overall_success": all(r["success"] for r in search_results)
            }
        else:
            print("\n⚠️  Skipping search provider tests per request")
            results["search"] = {
                "results": [],
                "overall_success": True  # Considered successful if not run
            }
        
        # Calculate overall success
        overall_success = (
            results["llm_providers"]["overall_success"] and 
            results["agents"]["overall_success"] and
            results["search"]["overall_success"]
        )
        
        results["overall"] = {
            "success": overall_success,
            "timestamp": datetime.now().isoformat(),
            "config": {
                "default_provider": settings.llm_provider,
                "has_openai": bool(settings.openai_api_key),
                "has_google": bool(settings.google_api_key),
                "has_deepseek": bool(settings.deepseek_api_key),
                "has_brave": bool(settings.brave_api_key),
                "has_exa": bool(settings.exa_api_key),
                "has_tavily": bool(settings.tavily_api_key)
            }
        }
        
        self.test_results = results
        return results
    
    def generate_full_report(self) -> str:
        """Generate a comprehensive test report."""
        results = self.test_results
        
        report = "\n" + "="*80 + "\n"
        report += "TRUTHLENS UNIFIED INTEGRATION TEST REPORT\n"
        report += "="*80 + "\n"
        report += f"Timestamp: {results['overall']['timestamp']}\n"
        
        # Only include default provider if LLM tests are present
        if "default_provider" in results['overall']['config']:
            report += f"Default Provider: {results['overall']['config']['default_provider']}\n"
        
        # Include API keys based on what's available in config
        api_key_info = []
        if "has_openai" in results['overall']['config']:
            api_key_info.append(f"OpenAI={results['overall']['config']['has_openai']}")
        if "has_google" in results['overall']['config']:
            api_key_info.append(f"Google={results['overall']['config']['has_google']}")
        if "has_deepseek" in results['overall']['config']:
            api_key_info.append(f"DeepSeek={results['overall']['config']['has_deepseek']}")
        if "has_brave" in results['overall']['config']:
            api_key_info.append(f"Brave={results['overall']['config']['has_brave']}")
        if "has_exa" in results['overall']['config']:
            api_key_info.append(f"Exa={results['overall']['config']['has_exa']}")
        if "has_tavily" in results['overall']['config']:
            api_key_info.append(f"Tavily={results['overall']['config']['has_tavily']}")
        
        report += f"API Keys Available: {', '.join(api_key_info)}\n"
        report += "\n"
        
        # LLM Provider Results (if present)
        if results.get("llm_providers"):
            report += "🔬 LLM PROVIDER INTEGRATION TESTS\n"
            report += "-"*40 + "\n"
            for result in results["llm_providers"]["results"]:
                report += f"\nProvider: {result['provider']}\n"
                report += f"Model: {result.get('model_name', 'default')}\n"
                report += f"Status: {result['summary']}\n"
                
                if 'responses' in result and result['responses']:
                    for i, response in enumerate(result['responses']):
                        status = "✅" if response['success'] else "❌"
                        report += f"  Prompt {i+1}: {status}\n"
                        if response.get('error'):
                            report += f"    Error: {response['error']}\n"
        
        # Agent Integration Results (if present)
        if results.get("agents"):
            if results.get("llm_providers"):  # Add separator if LLM tests were shown
                report += "\n\n"
            report += "🤖 AGENT INTEGRATION TESTS\n"
            report += "-"*40 + "\n"
            for result in results["agents"]["results"]:
                report += f"\nProvider: {result['provider']}\n"
                report += f"Status: {'✅ Working' if result['overall_success'] else '❌ Failed'}\n"
                
                for test_name, test_result in result['agent_tests'].items():
                    status = "✅" if test_result.get('success', True) else "❌"
                    report += f"  {test_name}: {status}\n"
                    if test_result.get('error'):
                        report += f"    Error: {test_result['error']}\n"
                    elif test_result.get('message'):
                        report += f"    Info: {test_result['message']}\n"
        
        # Search Integration Results (if present)
        if results.get("search"):
            if results.get("llm_providers") or results.get("agents"):  # Add separator if other tests were shown
                report += "\n\n"
            report += "🔍 SEARCH PROVIDER INTEGRATION TESTS\n"
            report += "-"*40 + "\n"
            current_provider = None
            for result in results["search"]["results"]:
                # Group by provider
                if current_provider != result['provider']:
                    current_provider = result['provider']
                    report += f"\nProvider: {result['provider']}\n"
                    report += "-" * 20 + "\n"
                
                report += f"Query: '{result['query']}'\n"
                report += f"Status: {result['summary']}\n"
                if result.get('result_count', 0) > 0:
                    report += f"Results: {result['result_count']} items\n"
                if result.get('validation_errors'):
                    report += f"Validation errors: {result['validation_errors']}\n"
                if result.get('error'):
                    report += f"Error: {result['error']}\n"
                report += "\n"
        
        # Summary - only include test types that were run
        llm_success = results["llm_providers"]["overall_success"] if results.get("llm_providers") else True
        agent_success = results["agents"]["overall_success"] if results.get("agents") else True
        search_success = results["search"]["overall_success"] if results.get("search") else True
        overall_success = results["overall"]["success"]
        
        report += f"\n\n📊 SUMMARY\n"
        report += "-"*40 + "\n"
        if results.get("llm_providers"):
            report += f"LLM Provider Tests: {'✅ PASS' if llm_success else '❌ FAIL'}\n"
        if results.get("agents"):
            report += f"Agent Integration Tests: {'✅ PASS' if agent_success else '❌ FAIL'}\n"
        if results.get("search"):
            report += f"Search Provider Tests: {'✅ PASS' if search_success else '❌ FAIL'}\n"
        report += f"Overall Status: {'🎉 ALL TESTS PASSED' if overall_success else '⚠️ SOME TESTS FAILED'}\n"
        
        return report
    
    def save_report(self, filename: str = None) -> str:
        """Save the test report to a file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.txt"
        
        # Ensure the report is saved in the test_reports directory at the agent level (one level up from tests)
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
    """Main entry point for the unified test runner."""
    # Parse command line arguments
    run_llm_tests = True
    run_agent_tests = True
    include_search = True  # Default to include search tests
    save_report = False
    
    for arg in sys.argv[1:]:
        if arg == "--llm-only":
            run_agent_tests = False
            include_search = False
        elif arg == "--agent-only":
            run_llm_tests = False
            include_search = False
        elif arg == "--search-only":
            # For search-only, we'll run a separate search-only flow
            print("🔍 Running Search Provider Integration Tests...")
            from tests.test_search_integration import SearchProviderIntegrationTester
            search_tester = SearchProviderIntegrationTester()
            search_results = await search_tester.test_all_providers()
            
            results = {
                "search": {
                    "results": search_results,
                    "overall_success": all(r["success"] for r in search_results)
                },
                "overall": {
                    "success": all(r["success"] for r in search_results),
                    "timestamp": datetime.now().isoformat(),
                    "config": {
                        "default_provider": settings.llm_provider,  # Include for compatibility
                        "has_brave": bool(settings.brave_api_key),
                        "has_exa": bool(settings.exa_api_key),
                        "has_tavily": bool(settings.tavily_api_key)
                    }
                }
            }
            
            # Update test_results for report generation
            runner = UnifiedIntegrationTestRunner()
            runner.test_results = results
            
            report = runner.generate_full_report()
            print(report)
            
            if save_report:
                filename = runner.save_report()
                print(f"\n📋 Report saved to: {filename}")
            
            # Exit with appropriate code
            overall_success = results["overall"]["success"]
            if overall_success:
                print("\n✅ All search integration tests passed!")
                sys.exit(0)
            else:
                print("\n❌ Some search integration tests failed!")
                sys.exit(1)
        elif arg == "--no-search":
            include_search = False
        elif arg == "--with-search":
            include_search = True
        elif arg == "--save-report":
            save_report = True
        elif arg in ["-h", "--help"]:
            print("Usage: python unified_test_runner.py [OPTIONS]")
            print("Options:")
            print("  --llm-only     Run only LLM provider tests")
            print("  --agent-only   Run only agent integration tests")
            print("  --search-only  Run only search provider tests")
            print("  --no-search    Run tests without search provider tests")
            print("  --with-search  Run tests including search provider tests (default)")
            print("  --save-report  Save test report to file")
            print("  -h, --help     Show this help message")
            return
    
    runner = UnifiedIntegrationTestRunner()
    results = await runner.run_all_tests(include_search=include_search)
    
    report = runner.generate_full_report()
    print(report)
    
    if save_report:
        filename = runner.save_report()
        print(f"\n📋 Report saved to: {filename}")
    
    # Exit with appropriate code
    overall_success = results["overall"]["success"]
    if overall_success:
        print("\n✅ All integration tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some integration tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())