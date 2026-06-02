from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


@dataclass(frozen=True)
class Settings:
    llm_api_key: str | None
    llm_model: str
    llm_base_url: str | None
    llm_enable_thinking: bool | None
    llm_enable_search: bool | None
    llm_cache_control: str | None
    llm_temperature: float
    llm_max_tokens: int
    llm_timeout_seconds: float
    per_user_bandwidth_mbps: float
    high_bandwidth_threshold_mbps: int

    @classmethod
    def from_env(cls) -> "Settings":
        if load_dotenv:
            load_dotenv()

        return cls(
            llm_api_key=os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY"),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            llm_base_url=os.getenv("LLM_BASE_URL") or None,
            llm_enable_thinking=parse_optional_bool(
                os.getenv("LLM_ENABLE_THINKING"), default=False
            ),
            llm_enable_search=parse_optional_bool(os.getenv("LLM_ENABLE_SEARCH")),
            llm_cache_control=normalize_optional_text(os.getenv("LLM_CACHE_CONTROL")),
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
            llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "300")),
            llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "60")),
            per_user_bandwidth_mbps=float(os.getenv("PER_USER_BANDWIDTH_MBPS", "1")),
            high_bandwidth_threshold_mbps=int(
                os.getenv("HIGH_BANDWIDTH_THRESHOLD_MBPS", "100")
            ),
        )


def parse_optional_bool(value: str | None, *, default: bool | None = None) -> bool | None:
    if value is None or value.strip() == "":
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    if not normalized or normalized.lower() in {"0", "false", "none", "off"}:
        return None
    return normalized
