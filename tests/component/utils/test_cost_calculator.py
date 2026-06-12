"""Shared cost_calculator helpers (AST-571 display parity)."""

from __future__ import annotations

import pytest

from src.utils.cost_calculator import sum_calc_cost_components


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
