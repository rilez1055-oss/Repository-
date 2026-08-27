import pytest

from reference_arch.cache import (
    CacheMetrics,
    build_cache_key,
    build_stable_prefix,
    canonical_render,
    explicit_breakpoint_content,
    explicit_cache_options,
    stable_prefix_digest,
)


def stable_fixture():
    return build_stable_prefix(
        agent_policy="agent-policy-v1",
        reference_set="reference-set-v3",
        mcp_tools=[{"name": "customer.read", "version": "v2"}],
        response_policy="response-policy-v1",
    )


def test_canonical_render_is_order_independent():
    a = {"b": 2, "a": 1}
    b = {"a": 1, "b": 2}
    assert canonical_render(a) == canonical_render(b)
    assert stable_prefix_digest(a) == stable_prefix_digest(b)


def test_dynamic_suffix_does_not_change_stable_prefix():
    stable_a = stable_fixture()
    stable_b = stable_fixture()
    request_a = {"stable": stable_a, "dynamic": {"resource": "48291"}}
    request_b = {"stable": stable_b, "dynamic": {"resource": "99310"}}

    assert stable_prefix_digest(request_a["stable"]) == stable_prefix_digest(
        request_b["stable"]
    )
    assert stable_prefix_digest(request_a) != stable_prefix_digest(request_b)


def test_cache_key_is_deterministic_and_non_sensitive_shape():
    assert build_cache_key("agent-v1", "policy-v1", "acme", 3) == (
        "agent-v1:policy-v1:acme:shard-03"
    )


def test_cache_key_rejects_ambiguous_or_oversized_values():
    with pytest.raises(ValueError):
        build_cache_key("agent:v1", "policy-v1", "acme", 3)
    with pytest.raises(ValueError):
        build_cache_key("a" * 70, "policy-v1", "acme", 3)
    with pytest.raises(ValueError):
        build_cache_key("agent-v1", "policy-v1", "acme", -1)


def test_explicit_breakpoint_shape():
    assert explicit_breakpoint_content("stable") == {
        "type": "input_text",
        "text": "stable",
        "prompt_cache_breakpoint": {"mode": "explicit"},
    }
    assert explicit_cache_options() == {"mode": "explicit", "ttl": "30m"}


def test_cache_metrics():
    metrics = CacheMetrics(
        input_tokens=1000,
        cached_tokens=700,
        cache_write_tokens=100,
        latency_ms=42.5,
    )
    assert metrics.uncached_input_tokens == 200
    assert metrics.cache_hit_ratio == 0.7
    assert metrics.estimated_input_cost(2.0) == 0.00079


def test_cache_metrics_reject_impossible_usage():
    with pytest.raises(ValueError):
        CacheMetrics(input_tokens=100, cached_tokens=80, cache_write_tokens=30)
    with pytest.raises(ValueError):
        CacheMetrics(input_tokens=100, cached_tokens=-1, cache_write_tokens=0)
