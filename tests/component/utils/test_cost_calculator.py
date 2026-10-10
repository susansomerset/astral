"""Shared cost_calculator helpers (AST-571 display parity)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.utils.config import LLM_MODEL_CONFIG
from src.utils.cost_calculator import (
    calculate_cost,
    calculate_cost_components,
    calculate_cost_components_from_counts,
    calculate_cost_with_cache,
    sum_calc_cost_components,
    usage_to_token_counts,
)


class TestSumCalcCostComponents:
    def test_empty_keys_zero(self) -> None:
        assert sum_calc_cost_components({}) == 0.0

    def test_partial_none_treated_as_zero(self) -> None:
        row = {
            "calc_cost_cache_write": 0.01,
            "calc_cost_cache_read": None,
            "calc_cost_no_cache_input": 0.03,
            "calc_cost_output": 0.04,
        }
        assert sum_calc_cost_components(row) == pytest.approx(0.08)

    def test_parent_brief_pro_row_840f7662(self) -> None:
        row = {
            "calc_cost_cache_write": 0.0,
            "calc_cost_cache_read": 0.000311808,
            "calc_cost_no_cache_input": 0.0071166,
            "calc_cost_output": 0.03751092,
        }
        assert sum_calc_cost_components(row) == pytest.approx(0.044939328, rel=1e-9)


class TestAst1877CatalogPricing:
    """AST-1877: cost math priced through LLM_MODEL_CONFIG (get_sku_pricing); generic token buckets."""

    def test_usage_to_token_counts_maps_all_buckets(self) -> None:
        usage = SimpleNamespace(input_tokens=100, output_tokens=25, cache_read_input_tokens=50,
                                cache_creation_input_tokens=7)
        assert usage_to_token_counts(usage) == {"cache_read": 50, "cache_miss": 100, "output": 25, "cache_write": 7}

    def test_usage_to_token_counts_defaults_missing_or_null_cache_fields_to_zero(self) -> None:
        assert usage_to_token_counts(SimpleNamespace(input_tokens=3, output_tokens=4)) == {
            "cache_read": 0, "cache_miss": 3, "output": 4, "cache_write": 0,
        }
        nulls = SimpleNamespace(input_tokens=3, output_tokens=4, cache_read_input_tokens=None,
                                cache_creation_input_tokens=None)
        assert usage_to_token_counts(nulls)["cache_read"] == 0
        assert usage_to_token_counts(nulls)["cache_write"] == 0

    def test_from_counts_uses_catalog_row_for_sku(self) -> None:
        p = LLM_MODEL_CONFIG["kimi-k2.6"]["pricing"]["kimi-k2.6"]
        parts = calculate_cost_components_from_counts(10, 20, 30, 40, sku="kimi-k2.6", server_id="kimi")
        assert parts == {
            "calc_cost_cache_write": 40 / 1_000_000 * p["cpm_cache_write"],
            "calc_cost_cache_read": 10 / 1_000_000 * p["cpm_cache_read"],
            "calc_cost_no_cache_input": 20 / 1_000_000 * p["cpm_input"],
            "calc_cost_output": 30 / 1_000_000 * p["cpm_output"],
        }

    def test_from_counts_unknown_sku_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown SKU"):
            calculate_cost_components_from_counts(1, 1, 1, 0, sku="__no_sku__")

    def test_anthropic_alias_costs_read_catalog_pricing(self) -> None:
        usage = SimpleNamespace(input_tokens=1_000_000, output_tokens=1_000_000, cache_read_input_tokens=0,
                                cache_creation_input_tokens=0)
        # AST-1955: one model id per SKU.
        p = LLM_MODEL_CONFIG["claude-haiku-4-5"]["pricing"]["claude-haiku-4-5"]
        assert calculate_cost(usage, "claude-haiku-4-5") == pytest.approx(p["cpm_input"] + p["cpm_output"])
        assert calculate_cost_with_cache(usage, "claude-haiku-4-5") == pytest.approx(p["cpm_input"] + p["cpm_output"])

    @pytest.mark.parametrize("fn", [calculate_cost, calculate_cost_with_cache, calculate_cost_components])
    def test_unpriced_model_code_raises(self, fn) -> None:
        usage = SimpleNamespace(input_tokens=1, output_tokens=1, cache_read_input_tokens=0, cache_creation_input_tokens=0)
        with pytest.raises(ValueError, match="Unknown SKU"):
            fn(usage, "__no_sku__")


class TestAst2098UsageNone:
    """AST-2098: a hollow response (no usage object) reads as zero tokens, never an exception."""

    def test_usage_none_reads_zero_tokens(self) -> None:
        assert usage_to_token_counts(None) == {"cache_read": 0, "cache_miss": 0, "output": 0, "cache_write": 0}
