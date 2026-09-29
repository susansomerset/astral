"""DeepSeek V4 catalog pricing snapshots (AST-570; AST-1880: legacy DeepSeek-named wrappers retired).

Bucket mapping lives in test_cost_calculator.py::TestAst1877CatalogPricing (usage_to_token_counts).
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.utils.cost_calculator import (
    calculate_cost_components,
    calculate_cost_components_from_counts,
)
from src.utils import cost_calculator as cost_mod


class TestDeepseekCatalogCostSnapshots:
    def test_pro_utc_day_export_totals_match_pricing_snapshot(self) -> None:
        parts = calculate_cost_components_from_counts(
            54400, 39339, 23547, 0, sku="deepseek-v4-pro", server_id="deepseek"
        )
        assert parts["calc_cost_cache_write"] == 0.0
        assert parts["calc_cost_cache_read"] == pytest.approx(0.1972, abs=1e-9)
        assert parts["calc_cost_no_cache_input"] == pytest.approx(0.017112465, abs=1e-9)
        assert parts["calc_cost_output"] == pytest.approx(0.02048589, abs=1e-9)

    def test_flash_utc_day_export_miss_and_output_match_pricing_snapshot(self) -> None:
        parts = calculate_cost_components_from_counts(
            6656, 3874, 3102, 0, sku="deepseek-v4-flash", server_id="deepseek"
        )
        assert parts["calc_cost_cache_write"] == 0.0
        assert parts["calc_cost_cache_read"] == pytest.approx(6656 / 1_000_000 * 0.0028, abs=1e-12)
        assert parts["calc_cost_no_cache_input"] == pytest.approx(0.00054236, abs=1e-9)
        assert parts["calc_cost_output"] == pytest.approx(0.00086856, abs=1e-9)

    def test_deepseek_named_wrappers_are_gone(self) -> None:
        # AST-1880 / AST-1883: catalog helpers are the only cost path.
        for name in (
            "deepseek_usage_to_token_counts",
            "calculate_cost_components_deepseek_from_counts",
            "calculate_cost_components_deepseek",
        ):
            assert not hasattr(cost_mod, name), name


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
