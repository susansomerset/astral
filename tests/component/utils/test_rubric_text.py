"""Component tests for src/utils/rubric_text.py (AST-906)."""

from __future__ import annotations

import pytest

from src.utils import rubric_text as rt

# Craft Get prompt shape: one JSON string with literal \n between grade lines.
_LITERAL_GET_SHAPE = "Fit criterion.\\nA = strong match\\nB = weak match"


class TestCoerceEmbeddedNewlineEscapes:
    def test_expands_literal_n_when_few_real_newlines(self) -> None:
        out = rt.coerce_embedded_newline_escapes(_LITERAL_GET_SHAPE)
        assert out == "Fit criterion.\nA = strong match\nB = weak match"

    def test_expands_literal_rn_before_n(self) -> None:
        raw = "body\\r\\nA = one\\r\\nB = two"
        assert rt.coerce_embedded_newline_escapes(raw) == "body\nA = one\nB = two"

    def test_skips_when_already_multiline(self) -> None:
        # >=2 real newlines: leave literal \\n untouched (do not double-expand).
        raw = "body\nA = one\nB = two\\nC = three"
        assert rt.coerce_embedded_newline_escapes(raw) == raw

    def test_noop_without_escapes(self) -> None:
        assert rt.coerce_embedded_newline_escapes("single line") == "single line"
        assert rt.coerce_embedded_newline_escapes("") == ""


class TestEnsureCriterionGradeTableAst906:
    def test_literal_n_content_parses_and_mutates(self) -> None:
        item = {"label": "get", "content": _LITERAL_GET_SHAPE}
        rt.ensure_criterion_grade_table(item)
        assert "\n" in item["content"]
        assert "\\n" not in item["content"]
        assert [r["grade"] for r in item["grade_descriptions"]] == ["A", "B"]
        assert item["grade_descriptions"][0]["description"] == "strong match"

    def test_real_newlines_unchanged(self) -> None:
        item = {"label": "get", "content": "body\nA = one\nB = two"}
        rt.ensure_criterion_grade_table(item)
        assert item["content"] == "body\nA = one\nB = two"
        assert len(item["grade_descriptions"]) == 2

    def test_empty_still_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            rt.ensure_criterion_grade_table({"content": ""})

    def test_single_grade_line_still_raises(self) -> None:
        with pytest.raises(ValueError, match="at least two lines"):
            rt.ensure_criterion_grade_table({"content": "A = only"})

    def test_single_grade_after_coerce_still_raises(self) -> None:
        # One grade line even after \\n expand — still reject.
        with pytest.raises(ValueError, match="at least two lines"):
            rt.ensure_criterion_grade_table({"content": "intro\\nA = only"})
