"""
Provider-agnostic LLM wrapper — Section 2 tech stack decision.
Swap providers via LLM_PROVIDER in .env without touching calling code.
"""
import json
from typing import Any

from app.core.config import get_settings

settings = get_settings()


class LLMClient:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL

    def _call_anthropic(self, system_prompt: str, user_message: str) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    def _call_openai(self, system_prompt: str, user_message: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content

    def _call_gemini(self, system_prompt: str, user_message: str) -> str:
        """
        Google AI Studio / Gemini — genuinely free tier, no credit card
        required (as of writing). Useful for building/testing the project
        without any spend.

        NOTE: this uses the current `google-genai` SDK. The older
        `google.generativeai` package (genai.configure / GenerativeModel)
        was deprecated by Google in 2025 and is no longer reliable against
        current models — that was the cause of every triage call silently
        falling back to the "AI unavailable" safe default in production.
        """
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=user_message,
            config=types.GenerateContentConfig(system_instruction=system_prompt),
        )
        return response.text

    def get_json_completion(self, system_prompt: str, user_message: str) -> dict[str, Any]:
        """
        Calls the configured provider and parses the response as strict JSON.
        Raises ValueError if the model didn't return valid JSON — callers
        (triage_orchestrator) must catch this and fall back safely
        (Section 7.5 — never fail silently, never crash the UI).
        """
        if self.provider == "anthropic":
            raw = self._call_anthropic(system_prompt, user_message)
        elif self.provider == "openai":
            raw = self._call_openai(system_prompt, user_message)
        elif self.provider == "gemini":
            raw = self._call_gemini(system_prompt, user_message)
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {self.provider}")

        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM did not return valid JSON: {raw[:200]}") from e
