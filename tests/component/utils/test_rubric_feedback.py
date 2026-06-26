"""AST-724: lenient parse helpers for rubric vector_reviews envelope strings."""

from __future__ import annotations

from typing import List

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


class TestAst816NormalizeVectorReviews:
    def test_parses_json_string_envelope(self) -> None:
        out = rf_mod.normalize_vector_reviews_raw('["CLRRACOVK", " DORRACOVK "]')
        assert out == ["CLRRACOVK", "DORRACOVK"]

    def test_rejects_non_string_elements(self) -> None:
        assert rf_mod.normalize_vector_reviews_raw(["G1RACOVK", 1]) is None


class TestAst816ParseVectorReviewsDiagnostic:
    def test_success_returns_rows_and_empty_reason(self) -> None:
        rows, reason, parsed, missing = rf_mod.parse_vector_reviews_diagnostic(
            ["G1RACOVK", "G2RSCOVE"],
            frozenset({"G1", "G2"}),
            {"G1": "uuid-1", "G2": "uuid-2"},
        )
        assert reason is None
        assert missing == frozenset()
        assert parsed == frozenset({"G1", "G2"})
        assert rows is not None and len(rows) == 2

    def test_missing_codes_reason(self) -> None:
        _, reason, _, missing = rf_mod.parse_vector_reviews_diagnostic(
            ["G1RACOVK"],
            frozenset({"G1", "G2"}),
            {"G1": "uuid-1", "G2": "uuid-2"},
        )
        assert reason == "missing_codes"
        assert missing == frozenset({"G2"})

    def test_evaluate_jd_style_codes_parse(self) -> None:
        # 3-letter rubric codes: CODE + R + rel + C + cla + V + ver (Susan UAT evaluate_jd set)
        codes = [
            "CLRRACOVK", "DORRACOVK", "DQRRACOVK", "JNRRACOVK",
            "LORRACOVK", "RLRRACOVK", "TIRRACOVK",
        ]
        parsed_codes: List[str] = []
        for line in codes:
            one = rf_mod.parse_vector_review_string(line)
            assert one is not None
            parsed_codes.append(one[0])
        expected = frozenset(parsed_codes)
        uuid_map = {code: f"uuid-{code}" for code in expected}
        rows, reason, _, _ = rf_mod.parse_vector_reviews_diagnostic(codes, expected, uuid_map)
        assert reason is None
        assert rows is not None and len(rows) == len(expected)


class TestAst816FormatHydratedReviewDebugLine:
    def test_formats_labels_and_truncates_content(self) -> None:
        row = {
            "code": "CLR",
            "label": "Culture fit",
            "relevance_label": "Aligned",
            "clarity_label": "OK",
            "verdict_label": "Keep",
            "content": "x" * 100,
        }
        line = rf_mod.format_hydrated_review_debug_line(row)
        assert line.startswith("CLR Culture fit — R/Aligned C/OK V/Keep — ")
        assert line.endswith("…")
        assert len(line) < 200


class TestAst820VectorReviewsPipelineTrace:
    """AST-820: pure pipeline trace lines for debug_detail (no logging side effects)."""

    def test_success_path_emits_normalize_diagnostic_and_hydrate_steps(self) -> None:
        lines = rf_mod.vector_reviews_pipeline_trace(
            raw_reviews=["G1RACOVK"],
            expected_codes=frozenset({"G1"}),
            code_to_uuid={"G1": "uuid-1"},
            rubric_by_code={"G1": {"label": "Grade fit", "content": "Criterion body", "importance": 8}},
            candidate_id="cand-1",
            owner_task_key="grade_get",
        )
        joined = "\n".join(lines)
        assert "vector_reviews trace candidate=cand-1 owner=grade_get" in joined
        assert "raw type=list" in joined
        assert "normalize -> 1 lines" in joined
        assert "expected_codes=['G1'] count=1" in joined
        assert "line[0] G1RACOVK parse=ok code=G1" in joined
        assert "diagnostic reason=ok" in joined
        assert "hydrate rows=1" in joined
        assert "G1 Grade fit" in joined

    def test_bad_input_shows_normalize_failure_reason(self) -> None:
        lines = rf_mod.vector_reviews_pipeline_trace(
            raw_reviews=None,
            expected_codes=frozenset({"G1"}),
            code_to_uuid={"G1": "uuid-1"},
            rubric_by_code={},
        )
        assert any("normalize -> None (reason=missing)" in line for line in lines)

    def test_truncates_long_raw_repr(self) -> None:
        long_list = ["G1RACOVK"] + ["X" * 200]
        lines = rf_mod.vector_reviews_pipeline_trace(
            raw_reviews=long_list,
            expected_codes=frozenset({"G1"}),
            code_to_uuid={"G1": "uuid-1"},
            rubric_by_code={"G1": {"label": "G1", "content": "", "importance": 1}},
        )
        raw_line = next(line for line in lines if line.startswith("raw type="))
        assert raw_line.endswith("…")
        assert len(raw_line) <= 140
