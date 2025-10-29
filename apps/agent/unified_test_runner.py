#!/usr/bin/env python3
"""
Unified test runner for TruthLens integration tests.

This script runs all integration tests for LLM providers and agents,
providing a comprehensive verification of the system.
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List

# Add the project root to Python path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sys
import os
# Add the tests directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests'))

from test_llm_provider_integration import LLMProviderIntegrationTester
from test_agent_integration import AgentIntegrationTester
from utils.settings import settings


class UnifiedIntegrationTestRunner:
    """Unified test runner for TruthLens integration tests."""
    
    def __init__(self):
        self.test_results = {}
    
    async def run_all_tests(self) -> Dict:
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
        
        # Calculate overall success
        overall_success = (
            results["llm_providers"]["overall_success"] and 
            results["agents"]["overall_success"]
        )
        
        results["overall"] = {
            "success": overall_success,
            "timestamp": datetime.now().isoformat(),
            "config": {
                "default_provider": settings.llm_provider,
                "has_openai": bool(settings.openai_api_key),
                "has_google": bool(settings.google_api_key),
                "has_deepseek": bool(settings.deepseek_api_key)
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
        report += f"Default Provider: {results['overall']['config']['default_provider']}\n"
        report += f"API Keys Available: OpenAI={results['overall']['config']['has_openai']}, "
        report += f"Google={results['overall']['config']['has_google']}, "
        report += f"DeepSeek={results['overall']['config']['has_deepseek']}\n"
        report += "\n"
        
        # LLM Provider Results
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
        
        # Agent Integration Results
        report += "\n\n🤖 AGENT INTEGRATION TESTS\n"
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
        
        # Summary
        llm_success = results["llm_providers"]["overall_success"]
        agent_success = results["agents"]["overall_success"]
        overall_success = results["overall"]["success"]
        
        report += f"\n\n📊 SUMMARY\n"
        report += "-"*40 + "\n"
        report += f"LLM Provider Tests: {'✅ PASS' if llm_success else '❌ FAIL'}\n"
        report += f"Agent Integration Tests: {'✅ PASS' if agent_success else '❌ FAIL'}\n"
        report += f"Overall Status: {'🎉 ALL TESTS PASSED' if overall_success else '⚠️ SOME TESTS FAILED'}\n"
        
        return report
    
    def save_report(self, filename: str = None) -> str:
        """Save the test report to a file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.txt"
        
        # Ensure the report is saved in the test_reports directory at the agent level
        agent_dir = os.path.dirname(os.path.abspath(__file__))
        reports_dir = os.path.join(agent_dir, '..', 'test_reports')
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
    save_report = False
    
    for arg in sys.argv[1:]:
        if arg == "--llm-only":
            run_agent_tests = False
        elif arg == "--agent-only":
            run_llm_tests = False
        elif arg == "--save-report":
            save_report = True
        elif arg in ["-h", "--help"]:
            print("Usage: python unified_test_runner.py [OPTIONS]")
            print("Options:")
            print("  --llm-only     Run only LLM provider tests")
            print("  --agent-only   Run only agent integration tests")
            print("  --save-report  Save test report to file")
            print("  -h, --help     Show this help message")
            return
    
    runner = UnifiedIntegrationTestRunner()
    results = await runner.run_all_tests()
    
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