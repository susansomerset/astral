"""
Cost calculation utilities for LLM API calls.

Pure functions. Pricing from LLM_MODEL_CONFIG via get_sku_pricing (AST-1851).
"""

from src.utils.config import get_sku_pricing


def calculate_cost(usage, model_code: str) -> float:
    """Calculate cost in USD for an API call (no caching).

    Args:
        usage: Anthropic response usage object (input_tokens, output_tokens)
        model_code: Vendor SKU (catalog pricing key)

    Returns: Cost in USD

    Raises:
        ValueError: If model_code has no catalog pricing row
    """
    m = get_sku_pricing(model_code)
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
        model_code: Vendor SKU (catalog pricing key)

    Returns: Cost in USD with cache pricing applied

    Raises:
        ValueError: If model_code has no catalog pricing row
    """
    m = get_sku_pricing(model_code)
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
    m = get_sku_pricing(model_code)
    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
    return {
        "calc_cost_cache_write": (cache_write / 1_000_000) * m["cpm_cache_write"],
        "calc_cost_cache_read": (cache_read / 1_000_000) * m["cpm_cache_read"],
        "calc_cost_no_cache_input": (usage.input_tokens / 1_000_000) * m["cpm_input"],
        "calc_cost_output": (usage.output_tokens / 1_000_000) * m["cpm_output"],
    }


def usage_to_token_counts(usage) -> dict:
    """Map Anthropic-Messages usage to agent_timesheets buckets.

    cache_miss = usage.input_tokens (fresh input after the last cache breakpoint);
    cache_read / cache_write default 0 when the server omits them.
    """
    # Hollow response (AST-2098): no usage object reads as zero tokens, never an exception.
    if usage is None:
        return {"cache_read": 0, "cache_miss": 0, "output": 0, "cache_write": 0}
    return {
        "cache_read": getattr(usage, "cache_read_input_tokens", 0) or 0,
        "cache_miss": usage.input_tokens,
        "output": usage.output_tokens,
        "cache_write": getattr(usage, "cache_creation_input_tokens", 0) or 0,
    }


def calculate_cost_components_from_counts(
    cache_read: int, cache_miss: int, output: int, cache_write: int, *, sku: str, server_id: str | None = None,
) -> dict:
    """Granular cost components from token integers, priced by catalog SKU (same keys as calculate_cost_components)."""
    m = get_sku_pricing(sku, server_id)
    return {
        "calc_cost_cache_write": (cache_write / 1_000_000) * m["cpm_cache_write"],
        "calc_cost_cache_read": (cache_read / 1_000_000) * m["cpm_cache_read"],
        "calc_cost_no_cache_input": (cache_miss / 1_000_000) * m["cpm_input"],
        "calc_cost_output": (output / 1_000_000) * m["cpm_output"],
    }


CALC_COST_KEYS = (
    "calc_cost_cache_write",
    "calc_cost_cache_read",
    "calc_cost_no_cache_input",
    "calc_cost_output",
)


def sum_calc_cost_components(row: dict) -> float:
    """Row total spend from stored calc_cost_* only."""
    return sum(float(row.get(k) or 0) for k in CALC_COST_KEYS)
