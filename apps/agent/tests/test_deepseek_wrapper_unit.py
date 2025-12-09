"""Unit tests for the DeepSeek structured output wrapper.

These tests mock the underlying LLM so we can exercise the JSON translation logic
without calling the real DeepSeek API.
"""

import unittest
from typing import Any, List

from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field

from utils.models import DeepSeekChatWrapper
from utils.llm import call_llm_with_structured_output


class DummyOutput(BaseModel):
    claims: List[str] = Field(default_factory=list)
    no_claims: bool = False


class FakeLLM:
    """Simple stand-in for ChatOpenAI to keep the tests offline."""

    def __init__(self, response_content: Any):
        self.response_content = response_content
        self.recorded_messages = None
        self._recorded_kwargs = None

    @property
    def _identifying_params(self):
        return {}

    def bind(self, **kwargs):
        return self

    def invoke(self, messages, **kwargs):
        self.recorded_messages = messages
        self._recorded_kwargs = kwargs
        return AIMessage(content=self.response_content)

    async def ainvoke(self, messages, **kwargs):
        self.recorded_messages = messages
        self._recorded_kwargs = kwargs
        return AIMessage(content=self.response_content)


class DeepSeekWrapperTests(unittest.IsolatedAsyncioTestCase):
    async def test_parses_plain_json_payload(self):
        fake_llm = FakeLLM('{"claims": ["c1"], "no_claims": false}')
        wrapper = DeepSeekChatWrapper(fake_llm)

        result = await call_llm_with_structured_output(
            llm=wrapper,
            output_class=DummyOutput,
            messages=[("human", "List claims")],
            context_desc="unit-plain-json",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.claims, ["c1"])
        self.assertFalse(result.no_claims)
        self.assertIn("Please respond ONLY", fake_llm.recorded_messages[-1].content)

    async def test_parses_json_from_code_block(self):
        fake_llm = FakeLLM(
            "Here you go:\n```json\n{\n  \"claims\": [],\n  \"no_claims\": true\n}\n```"
        )
        wrapper = DeepSeekChatWrapper(fake_llm)

        result = await call_llm_with_structured_output(
            llm=wrapper,
            output_class=DummyOutput,
            messages=[("system", "Do task"), ("human", "Need JSON")],
            context_desc="unit-code-block",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.claims, [])
        self.assertTrue(result.no_claims)
        # Ensure the JSON instruction is appended to the last prompt
        self.assertIn("valid JSON", fake_llm.recorded_messages[-1].content)

    async def test_returns_schema_defaults_when_no_json(self):
        fake_llm = FakeLLM("I cannot comply with that request.")
        wrapper = DeepSeekChatWrapper(fake_llm)

        result = await call_llm_with_structured_output(
            llm=wrapper,
            output_class=DummyOutput,
            messages=[("human", "Return JSON anyway")],
            context_desc="unit-no-json",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.claims, [])
        self.assertFalse(result.no_claims)


if __name__ == "__main__":
    unittest.main()
