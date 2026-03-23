"""Runtime configuration for LLM-backed integrations."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class LLMSettings:
    api_key: str
    model: str
    base_url: str | None = None
    temperature: float = 0.3
    max_tokens: int = 900

    @classmethod
    def from_env(cls) -> "LLMSettings":
        api_key = os.getenv("OPENCHATAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "Missing LLM credentials. Set OPENCHATAI_API_KEY or OPENAI_API_KEY."
            )

        base_url = os.getenv("OPENCHATAI_BASE_URL") or os.getenv("OPENAI_BASE_URL")
        model = os.getenv("OPENCHATAI_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        temperature = float(os.getenv("OPENCHATAI_TEMPERATURE", "0.3"))
        max_tokens = int(os.getenv("OPENCHATAI_MAX_TOKENS", "900"))

        return cls(
            api_key=api_key,
            model=model,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
        )
