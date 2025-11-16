"""Tests for LLM utility helpers."""

import unittest
from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from utils.llm import call_llm_with_structured_output


class DummyOutput(BaseModel):
    value: str = ""


class FakeLLM:
    def __init__(self, content: Any):
        self.content = content
        self.recorded_messages = None

    @property
    def _identifying_params(self):
        return {}

    def bind(self, **kwargs):
        return self

    def with_structured_output(self, schema):
        fake = self

        class _Structured:
            async def ainvoke(_, messages):
                fake.recorded_messages = messages
                if isinstance(fake.content, str):
                    return schema.model_validate_json(fake.content)
                if isinstance(fake.content, dict):
                    return schema(**fake.content)
                return schema(value=str(fake.content))

        return _Structured()


class LLMUtilsTests(unittest.IsolatedAsyncioTestCase):
    async def test_call_llm_accepts_chat_prompt_value(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "sys instruction"),
            ("human", "Hello {name}"),
        ])
        prompt_value = prompt.invoke({"name": "World"})

        fake_llm = FakeLLM('{"value": "ok"}')
        result = await call_llm_with_structured_output(
            llm=fake_llm,
            output_class=DummyOutput,
            messages=prompt_value,
            context_desc="unit-chat-prompt",
        )

        self.assertEqual(result.value, "ok")
        self.assertIsNotNone(fake_llm.recorded_messages)
        self.assertEqual(len(fake_llm.recorded_messages), 2)
        self.assertEqual(fake_llm.recorded_messages[0].content, "sys instruction")
        self.assertEqual(fake_llm.recorded_messages[1].content, "Hello World")


if __name__ == "__main__":
    unittest.main()
