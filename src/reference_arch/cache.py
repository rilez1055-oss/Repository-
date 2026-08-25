"""Pure prompt-cache planning utilities.

This module does not make OpenAI API calls. It creates deterministic metadata
for a future Responses integration while keeping authorization outside cache
state.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class CacheMetrics:
    input_tokens: int
    cached_tokens: int
    cache_write_tokens: int
    latency_ms: float | None = None

    @property
    def uncached_input_tokens(self) -> int:
        return max(
            0,
            self.input_tokens - self.cached_tokens - self.cache_write_tokens,
        )

    @property
    def cache_hit_ratio(self) -> float:
        if self.input_tokens <= 0:
            return 0.0
        return self.cached_tokens / self.input_tokens

    def estimated_input_cost(
        self,
        input_price_per_million: float,
        cache_read_multiplier: float = 0.1,
        cache_write_multiplier: float = 1.25,
    ) -> float:
        weighted = (
            self.uncached_input_tokens
            + self.cached_tokens * cache_read_multiplier
            + self.cache_write_tokens * cache_write_multiplier
        )
        return weighted * input_price_per_million / 1_000_000


def canonical_render(components: Mapping[str, Any]) -> str:
    """Render stable context deterministically.

    Sorting keys and using compact JSON prevents incidental dictionary ordering
    from changing the reusable prefix.
    """
    return json.dumps(
        components,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def stable_prefix_digest(components: Mapping[str, Any]) -> str:
    rendered = canonical_render(components).encode("utf-8")
    return hashlib.sha256(rendered).hexdigest()


def build_cache_key(
    agent_version: str,
    policy_version: str,
    tenant_class: str,
    shard: int,
) -> str:
    if shard < 0:
        raise ValueError("shard must be non-negative")
    return f"{agent_version}:{policy_version}:{tenant_class}:shard-{shard:02d}"


def build_stable_prefix(
    *,
    agent_policy: Any,
    reference_set: Any,
    mcp_tools: Sequence[Any],
    response_policy: Any,
) -> dict[str, Any]:
    """Build only stable inputs; dynamic authorization/request data is excluded."""
    return {
        "agent_policy": agent_policy,
        "reference_set": reference_set,
        "mcp_tools": list(mcp_tools),
        "response_policy": response_policy,
    }


def explicit_breakpoint_content(text: str) -> dict[str, Any]:
    """Return the Responses input_text shape for an explicit cache breakpoint."""
    return {
        "type": "input_text",
        "text": text,
        "prompt_cache_breakpoint": {"mode": "explicit"},
    }
