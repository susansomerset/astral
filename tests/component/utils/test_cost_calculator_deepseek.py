"""DeepSeek cost math and token bucket mapping (AST-570)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.utils.cost_calculator import (
    calculate_cost_components,
    calculate_cost_components_deepseek,
    calculate_cost_components_deepseek_from_counts,
    deepseek_usage_to_token_counts,
)


class TestDeepseekUsageToTokenCounts:
    def test_maps_cache_hit_miss_output_and_zero_write(self) -> None:
        usage = SimpleNamespace(
            input_tokens=100,
            output_tokens=25,
            cache_read_input_tokens=50,
        )
        assert deepseek_usage_to_token_counts(usage) == {
            "cache_read": 50,
            "cache_miss": 100,
            "output": 25,
            "cache_write": 0,
        }


class TestDeepseekCostComponentsFromCounts:
    def test_pro_utc_day_export_totals_match_pricing_snapshot(self) -> None:
        parts = calculate_cost_components_deepseek_from_counts(
            54400, 39339, 23547, 0, "deepseek-v4-pro"
        )
        assert parts["calc_cost_cache_write"] == 0.0
        assert parts["calc_cost_cache_read"] == pytest.approx(0.1972, abs=1e-9)
        assert parts["calc_cost_no_cache_input"] == pytest.approx(0.017112465, abs=1e-9)
        assert parts["calc_cost_output"] == pytest.approx(0.02048589, abs=1e-9)

    def test_flash_utc_day_export_miss_and_output_match_pricing_snapshot(self) -> None:
        parts = calculate_cost_components_deepseek_from_counts(
            6656, 3874, 3102, 0, "deepseek-v4-flash"
        )
        assert parts["calc_cost_cache_write"] == 0.0
        assert parts["calc_cost_cache_read"] == pytest.approx(6656 / 1_000_000 * 0.0028, abs=1e-12)
        assert parts["calc_cost_no_cache_input"] == pytest.approx(0.00054236, abs=1e-9)
        assert parts["calc_cost_output"] == pytest.approx(0.00086856, abs=1e-9)

    def test_usage_wrapper_matches_from_counts(self) -> None:
        usage = SimpleNamespace(
            input_tokens=100,
            output_tokens=25,
            cache_read_input_tokens=50,
        )
        assert calculate_cost_components_deepseek(usage, "deepseek-v4-pro") == (
            calculate_cost_components_deepseek_from_counts(50, 100, 25, 0, "deepseek-v4-pro")
        )


class TestAnthropicCostComponentsRegression:
    def test_anthropic_path_unchanged(self) -> None:
        usage = SimpleNamespace(
            input_tokens=10,
            output_tokens=5,
            cache_read_input_tokens=2,
            cache_creation_input_tokens=1,
        )
        parts = calculate_cost_components(usage, "claude-sonnet-4-6")
        assert set(parts) == {
            "calc_cost_cache_write",
            "calc_cost_cache_read",
            "calc_cost_no_cache_input",
            "calc_cost_output",
        }
        assert parts["calc_cost_cache_write"] > 0
