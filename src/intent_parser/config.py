from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    llm_api_key: str | None
    llm_model: str
    llm_base_url: str | None
    per_user_bandwidth_mbps: float
    high_bandwidth_threshold_mbps: int

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            llm_api_key=os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY"),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            llm_base_url=os.getenv("LLM_BASE_URL") or None,
            per_user_bandwidth_mbps=float(os.getenv("PER_USER_BANDWIDTH_MBPS", "1")),
            high_bandwidth_threshold_mbps=int(
                os.getenv("HIGH_BANDWIDTH_THRESHOLD_MBPS", "100")
            ),
        )
