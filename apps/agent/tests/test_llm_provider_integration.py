#!/usr/bin/env python3
"""
Integration tests for LLM provider functionality.

These tests verify that all LLM providers (OpenAI, Gemini, DeepSeek) 
can successfully connect and generate responses.
"""

import asyncio
import os
import sys
from typing import Dict, List

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add the project root to Python path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.models import get_llm, get_default_llm
from utils.settings import settings


class LLMProviderIntegrationTester:
    """Integration tester for LLM providers."""
    
    def __init__(self):
        self.test_prompts = [
            "Hello, can you confirm you're working properly?",
            "What's 2+2? Respond with just the number.",
        ]
        self.test_results: Dict[str, List[Dict]] = {}
    
    async def test_provider(self, provider: str, model_name: str = None) -> Dict:
        """Test a specific LLM provider."""
        print(f"\n🧪 Testing {provider.upper()} provider...")
        
        try:
            # Get LLM instance for this provider
            llm = get_llm(provider=provider, model_name=model_name)
            
            # Test responses for each prompt
            responses = []
            for i, prompt in enumerate(self.test_prompts):
                try:
                    print(f"   Prompt {i+1}: {prompt[:50]}...")
                    response = await llm.ainvoke([("human", prompt)])
                    response_text = response.content if hasattr(response, 'content') else str(response)
                    responses.append({
                        "prompt": prompt,
                        "response": response_text,
                        "success": True,
                        "error": None
                    })
                    print(f"   ✅ Response received: {response_text[:60]}...")
                except Exception as e:
                    print(f"   ❌ Error on prompt {i+1}: {str(e)}")
                    responses.append({
                        "prompt": prompt,
                        "response": None,
                        "success": False,
                        "error": str(e)
                    })
            
            # Overall success is true if all prompts succeeded
            overall_success = all(r["success"] for r in responses)
            
            result = {
                "provider": provider,
                "model_name": model_name,
                "responses": responses,
                "overall_success": overall_success,
                "summary": f"✅ {provider.upper()} provider working" if overall_success else f"❌ {provider.upper()} provider failed"
            }
            
            print(f"   {result['summary']}")
            return result
            
        except Exception as e:
            print(f"   ❌ Failed to initialize {provider} provider: {str(e)}")
            return {
                "provider": provider,
                "model_name": model_name,
                "responses": [],
                "overall_success": False,
                "error": str(e),
                "summary": f"❌ {provider.upper()} provider initialization failed"
            }
    
    async def test_all_providers(self) -> List[Dict]:
        """Test all configured LLM providers."""
        print("🚀 Starting LLM Provider Integration Tests...")
        
        # Determine which providers to test based on available API keys
        providers_to_test = []
        
        if settings.openai_api_key:
            providers_to_test.append(("openai", "openai:gpt-4o-mini"))
        
        if settings.google_api_key:
            providers_to_test.append(("gemini", "gemini-2.5-flash"))
        
        if settings.deepseek_api_key:
            providers_to_test.append(("deepseek", "deepseek-chat"))
        
        if not providers_to_test:
            print("⚠️  No API keys found. Testing will use default provider only.")
            providers_to_test.append((settings.llm_provider, None))
        
        results = []
        for provider, default_model in providers_to_test:
            result = await self.test_provider(provider, default_model)
            results.append(result)
        
        # Test the default provider regardless
        print(f"\n🧪 Testing default provider: {settings.llm_provider}")
        default_result = await self.test_provider(settings.llm_provider)
        results.append({
            **default_result,
            "test_type": "default_provider"
        })
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """Generate a test report."""
        report = "\n" + "="*60 + "\n"
        report += "LLM PROVIDER INTEGRATION TEST REPORT\n"
        report += "="*60 + "\n"
        
        for result in results:
            report += f"\nProvider: {result['provider']}\n"
            report += f"Model: {result.get('model_name', 'default')}\n"
            report += f"Status: {result['summary']}\n"
            
            if 'responses' in result and result['responses']:
                for i, response in enumerate(result['responses']):
                    status = "✅" if response['success'] else "❌"
                    report += f"  Prompt {i+1}: {status}\n"
                    if response.get('error'):
                        report += f"    Error: {response['error']}\n"
        
        # Summary
        successful = sum(1 for r in results if r['overall_success'])
        total = len(results)
        report += f"\n📊 SUMMARY: {successful}/{total} providers working\n"
        
        if successful == total:
            report += "🎉 All providers working correctly!\n"
        else:
            report += "⚠️  Some providers failed - please check configuration\n"
        
        return report


async def main():
    """Run the integration tests."""
    print("🚀 LLM Provider Integration Test Suite")
    print(f"Default provider configured: {settings.llm_provider}")
    
    tester = LLMProviderIntegrationTester()
    results = await tester.test_all_providers()
    report = tester.generate_report(results)
    
    print(report)
    
    # Return success/failure for CI/CD purposes
    successful = sum(1 for r in results if r['overall_success'])
    total = len(results)
    
    if successful == total:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())