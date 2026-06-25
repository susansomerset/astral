"""AST-724: lenient parse helpers for rubric vector_reviews envelope strings."""

from __future__ import annotations

from src.utils import rubric_feedback as rf_mod
from src.utils import config as cfg


class TestParseVectorReviewString:
    def test_parses_compact_review_line(self) -> None:
        out = rf_mod.parse_vector_review_string("RCRACOVK")
        assert out is not None
        code, vals = out
        assert code == "RC"
        assert vals == {"relevance": "A", "clarity": "O", "verdict": "K"}

    def test_rejects_invalid_value_letters(self) -> None:
        assert rf_mod.parse_vector_review_string("RCRXCXVX") is None

    def test_rejects_malformed_line(self) -> None:
        assert rf_mod.parse_vector_review_string("not-a-review") is None


class TestParseVectorReviews:
    def test_parses_full_expected_set(self) -> None:
        rows = rf_mod.parse_vector_reviews(
            ["G1RACOVK", "G2RSCOVE"],
            frozenset({"G1", "G2"}),
            {"G1": "uuid-1", "G2": "uuid-2"},
        )
        assert rows is not None
        assert len(rows) == 2
        assert rows[0]["rubric_vector_uuid"] == "uuid-1"
        assert rows[0]["verdict"] == "K"

    def test_returns_none_on_missing_code(self) -> None:
        assert (
            rf_mod.parse_vector_reviews(
                ["G1RAOCVK"],
                frozenset({"G1", "G2"}),
                {"G1": "uuid-1", "G2": "uuid-2"},
            )
            is None
        )

    def test_returns_none_on_unknown_uuid_code(self) -> None:
        assert (
            rf_mod.parse_vector_reviews(
                ["G1RAOCVK"],
                frozenset({"G1"}),
                {},
            )
            is None
        )


class TestFormatVectorReviewsRaw:
    def test_serializes_vector_reviews_key_when_present(self) -> None:
        raw = rf_mod.format_vector_reviews_raw(
            {"status": "success", "vector_reviews": ["G1RACOVK"]}
        )
        assert "G1RACOVK" in raw

    def test_serializes_whole_perf_when_vector_reviews_absent(self) -> None:
        raw = rf_mod.format_vector_reviews_raw({"status": "success", "failure_note": ""})
        assert "success" in raw


class TestAst808HydrateVectorReviewStrings:
    """AST-808: display hydration for compact vector_reviews (partial lists OK)."""

    def test_hydrates_with_rubric_lookup(self) -> None:
        rubric = {
            "G1": {"label": "Grade fit", "content": "Criterion body\nA = one", "importance": 8},
        }
        rows = rf_mod.hydrate_vector_review_strings(["G1RACOVK"], rubric)
        assert len(rows) == 1
        assert rows[0]["code"] == "G1"
        assert rows[0]["label"] == "Grade fit"
        assert "Criterion body" in rows[0]["content"]
        assert rows[0]["relevance_label"] == cfg.RUBRIC_FEEDBACK_CONFIG["value_labels"]["A"]

    def test_skips_malformed_and_non_list_input(self) -> None:
        assert rf_mod.hydrate_vector_review_strings(None, {}) == []
        assert rf_mod.hydrate_vector_review_strings(["not-valid"], {"G1": {}}) == []
