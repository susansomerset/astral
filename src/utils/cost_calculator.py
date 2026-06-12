"""
Cost calculation utilities for Anthropic and DeepSeek API calls.

Pure functions. Anthropic pricing from AGENT_CONFIG; DeepSeek from DEEPSEEK_MODEL_PRICING.
"""

from src.utils.config import AGENT_CONFIG, DEEPSEEK_MODEL_PRICING


def calculate_cost(usage, model_code: str) -> float:
    """Calculate cost in USD for an API call (no caching).

    Args:
        usage: Anthropic response usage object (input_tokens, output_tokens)
        model_code: Model alias key from AGENT_CONFIG

    Returns: Cost in USD

    Raises:
        ValueError: If model_code not found in AGENT_CONFIG
    """
    m = AGENT_CONFIG.get(model_code)
    if not m:
        raise ValueError(f"Unknown model_code for cost calc: {model_code!r}. Valid: {list(AGENT_CONFIG.keys())}")
    return (usage.input_tokens / 1_000_000) * m["cpm_input"] + \
           (usage.output_tokens / 1_000_000) * m["cpm_output"]


def calculate_cost_with_cache(usage, model_code: str) -> float:
    """Calculate cost in USD for an API call with prompt caching.

    Args:
        usage: Anthropic response usage object with:
            - input_tokens: non-cached input tokens (tokens after the last cache breakpoint)
            - output_tokens: output tokens
            - cache_read_input_tokens: tokens read from cache (optional)
            - cache_creation_input_tokens: tokens written to cache (optional)
        model_code: Model alias key from AGENT_CONFIG

    Returns: Cost in USD with cache pricing applied

    Raises:
        ValueError: If model_code not found in AGENT_CONFIG
    """
    m = AGENT_CONFIG.get(model_code)
    if not m:
        raise ValueError(f"Unknown model_code for cost calc: {model_code!r}. Valid: {list(AGENT_CONFIG.keys())}")
    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
    # input_tokens is already the non-cached portion (tokens after the last cache breakpoint).
    # cache_read and cache_write are separate; do NOT subtract them.
    return (
        (usage.input_tokens / 1_000_000) * m["cpm_input"]
        + (cache_read / 1_000_000) * m["cpm_cache_read"]
        + (cache_write / 1_000_000) * m["cpm_cache_write"]
        + (usage.output_tokens / 1_000_000) * m["cpm_output"]
    )


def calculate_cost_components(usage, model_code: str) -> dict:
    """Return individual cost components for granular timesheet storage.

    usage.input_tokens is the non-cached fresh input (Anthropic SDK convention).

    Returns dict with keys:
        calc_cost_cache_write, calc_cost_cache_read,
        calc_cost_no_cache_input, calc_cost_output
    """
    m = AGENT_CONFIG.get(model_code)
    if not m:
        raise ValueError(f"Unknown model_code: {model_code!r}")
    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
    return {
        "calc_cost_cache_write": (cache_write / 1_000_000) * m["cpm_cache_write"],
        "calc_cost_cache_read": (cache_read / 1_000_000) * m["cpm_cache_read"],
        "calc_cost_no_cache_input": (usage.input_tokens / 1_000_000) * m["cpm_input"],
        "calc_cost_output": (usage.output_tokens / 1_000_000) * m["cpm_output"],
    }


def deepseek_usage_to_token_counts(usage) -> dict:
    """Map DeepSeek Messages API usage to agent_timesheets token buckets.

    cache_read = cache hit; cache_miss = usage.input_tokens (vendor cache-miss count
    on compat API); cache_write always 0 (DeepSeek does not bill cache creation).
    """
    return {
        "cache_read": getattr(usage, "cache_read_input_tokens", 0) or 0,
        "cache_miss": usage.input_tokens,
        "output": usage.output_tokens,
        "cache_write": 0,
    }


def calculate_cost_components_deepseek_from_counts(
    cache_read: int,
    cache_miss: int,
    output: int,
    cache_write: int,
    vendor_model: str,
) -> dict:
    """Granular DeepSeek cost components from stored or live token integers."""
    m = DEEPSEEK_MODEL_PRICING.get(vendor_model)
    if not m:
        raise ValueError(f"Unknown DeepSeek vendor_model: {vendor_model!r}")
    return {
        "calc_cost_cache_write": (cache_write / 1_000_000) * m["cpm_cache_write"],
        "calc_cost_cache_read": (cache_read / 1_000_000) * m["cpm_cache_read"],
        "calc_cost_no_cache_input": (cache_miss / 1_000_000) * m["cpm_input"],
        "calc_cost_output": (output / 1_000_000) * m["cpm_output"],
    }


def calculate_cost_components_deepseek(usage, vendor_model: str) -> dict:
    """Granular cost components for DeepSeek usage (same keys as calculate_cost_components)."""
    counts = deepseek_usage_to_token_counts(usage)
    return calculate_cost_components_deepseek_from_counts(
        counts["cache_read"],
        counts["cache_miss"],
        counts["output"],
        counts["cache_write"],
        vendor_model,
    )


CALC_COST_KEYS = (
    "calc_cost_cache_write",
    "calc_cost_cache_read",
    "calc_cost_no_cache_input",
    "calc_cost_output",
)


def sum_calc_cost_components(row: dict) -> float:
    """Row total spend from stored calc_cost_* only."""
    return sum(float(row.get(k) or 0) for k in CALC_COST_KEYS)
