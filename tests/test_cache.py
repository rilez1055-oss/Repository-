from reference_arch.cache import (
    CacheMetrics,
    build_cache_key,
    build_stable_prefix,
    canonical_render,
    explicit_breakpoint_content,
    stable_prefix_digest,
)


def test_canonical_render_is_order_independent():
    a = {"b": 2, "a": 1}
    b = {"a": 1, "b": 2}
    assert canonical_render(a) == canonical_render(b)
    assert stable_prefix_digest(a) == stable_prefix_digest(b)


def test_dynamic_suffix_does_not_change_stable_prefix():
    stable = build_stable_prefix(
        agent_policy="agent-policy-v1",
        reference_set="reference-set-v3",
        mcp_tools=[{"name": "customer.read", "version": "v2"}],
        response_policy="response-policy-v1",
    )
    digest = stable_prefix_digest(stable)
    request_a = {**stable, "dynamic": {"resource": "48291"}}
    request_b = {**stable, "dynamic": {"resource": "99310"}}
    assert stable_prefix_digest(request_a) != digest
    assert stable_prefix_digest(request_b) != digest
    assert stable_prefix_digest(stable) == digest


def test_cache_key_is_deterministic_and_non_sensitive_shape():
    assert build_cache_key("agent-v1", "policy-v1", "acme", 3) == (
        "agent-v1:policy-v1:acme:shard-03"
    )


def test_explicit_breakpoint_shape():
    assert explicit_breakpoint_content("stable") == {
        "type": "input_text",
        "text": "stable",
        "prompt_cache_breakpoint": {"mode": "explicit"},
    }


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
