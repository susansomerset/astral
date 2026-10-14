"""Component tests for src/core/grade_schema.py (AST-2178): call-time forced-tool schema + hydrate."""

from __future__ import annotations

import json

import pytest

from src.core import grade_schema as gs
from src.utils.config import ASTRAL_CONFIG, TASK_CONFIG
from src.utils.logging import log_debug

AP = {"status": "success", "failure_note": None}
LABELS = {"CL": "Clarity", "RE": "Remote"}
J = [{"astral_job_id": "j0"}, {"astral_job_id": "j1"}]
CTX = {"batch_entities": J, "vector_labels": LABELS}
VET = "vet_inflow_discovery"
VCTX = {"batch_entities": [{"short_name": "a"}]}


def ot(task_key: str) -> str:
    return TASK_CONFIG[task_key]["output_type"]


def g(letter: object, conf: object) -> dict:
    return {"grade": letter, "confidence": conf}


def ok_row() -> dict:
    return {"CL": g("A", 5), "RE": g("B", 3)}


# Branches: batch_index_map keys (sorted, zero-padded) vs batch_entities positions vs empty ctx.
class TestGradeRowIds:
    def test_index_map_wins_and_sorts(self) -> None:
        assert gs.grade_row_ids({"batch_index_map": {9: {}, 5: {}}, "batch_entities": [{}]}) == ["005", "009"]

    def test_batch_entities_positions(self) -> None:
        assert gs.grade_row_ids({"batch_entities": [{}, {}]}) == ["000", "001"]

    def test_empty_ctx(self) -> None:
        assert gs.grade_row_ids({}) == []


# Branches: AC 1 closed schema; AC 2 no codes; non-grader type; nullable extras; vet bounds.
class TestBuildGradeToolSchema:
    def test_ac1_schema_is_complete_and_closed(self) -> None:
        s = gs.build_grade_tool_schema(ot("evaluate_jd"), ["CL", "RE"], ["000", "001"])
        assert s["required"] == ["000", "001", "agent_performance"]
        assert s["additionalProperties"] is False
        for rid in ("000", "001"):
            row = s["properties"][rid]
            assert row["required"] == ["CL", "RE"]
            assert row["additionalProperties"] is False
            for code in ("CL", "RE"):
                cell = row["properties"][code]
                assert cell["required"] == ["grade", "confidence"] and cell["additionalProperties"] is False
                assert cell["properties"]["grade"]["enum"] == ASTRAL_CONFIG["valid_grades"]
                assert cell["properties"]["confidence"] == {"type": "integer", "minimum": 0, "maximum": 5}

    def test_agent_performance_rides_in_the_schema(self) -> None:
        ap = gs.build_grade_tool_schema(ot("evaluate_jd"), ["CL"], ["000"])["properties"]["agent_performance"]
        assert ap["required"] == ["status", "failure_note"] and ap["additionalProperties"] is False
        assert ap["properties"]["status"]["enum"] == ["success", "failure"]
        assert ap["properties"]["failure_note"]["type"] == ["string", "null"]

    def test_ac2_empty_rubric_refuses_to_build(self) -> None:
        with pytest.raises(ValueError, match="no rubric codes"):
            gs.build_grade_tool_schema(ot("evaluate_jd"), [], ["000"])

    def test_non_grader_output_type_raises(self) -> None:
        with pytest.raises(ValueError, match="not a structured-output grader type"):
            gs.build_grade_tool_schema("grades_json", ["CL"], ["000"])
        with pytest.raises(ValueError, match="not a structured-output grader type"):
            gs.build_grade_tool_schema("no_such_type", ["CL"], ["000"])

    def test_extra_fields_are_required_but_nullable(self) -> None:
        notes = gs.build_grade_tool_schema(ot("grade_do"), ["CL"], ["000"])["properties"]["000"]
        assert notes["required"] == ["CL", "notes"]
        assert notes["properties"]["notes"] == {"type": ["string", "null"]}
        meta = gs.build_grade_tool_schema(ot("qualify_job_listings"), ["CL"], ["000"])["properties"]["000"]
        assert meta["required"] == ["CL", "company_job_id", "job_title", "job_link", "job_data"]
        # Nested fragment keys survive the nullable rewrite.
        assert meta["properties"]["job_data"] == {"type": ["object", "null"], "additionalProperties": {"type": "string"}}
        links = gs.build_grade_tool_schema(ot("prefilter_company"), ["CL"], ["000"])["properties"]["000"]
        assert links["properties"]["possible_job_links"] == {"type": ["array", "null"], "items": {"type": "integer"}}

    def test_vet_uses_its_own_letters_and_confidence_range(self) -> None:
        row = gs.build_grade_tool_schema(ot(VET), ["LT"], ["000"])["properties"]["000"]
        assert row["required"] == ["LT", "website"]
        props = row["properties"]["LT"]["properties"]
        assert props["grade"]["enum"] == ["A", "B", "C", "D", "F"]
        assert props["confidence"] == {"type": "integer", "minimum": 1, "maximum": 5}

    def test_schema_logged_in_full_at_debug(self, caplog: pytest.LogCaptureFixture) -> None:
        # stat.logging.debug: full schema, no truncation; debug() emits only while log_debug is on.
        caplog.set_level("DEBUG")
        token = log_debug.set(True)
        try:
            s = gs.build_grade_tool_schema(ot("evaluate_jd"), ["CL"], ["000"])
        finally:
            log_debug.reset(token)
        # The logger JSON-encodes dict args.
        want = f"Built grade tool schema for grades_encoded: {json.dumps(s)}"
        assert any(want in r.getMessage() for r in caplog.records)


# AC 3: hydrate output equals what src.core.agent._decode_payload produced for the equivalent encoded line.
# Expected dicts were captured from _decode_payload on this sub @ 9b7f68bd7 (AST-2180 deletes the decoder).
_AC3 = [
    (
        "evaluate_jd",
        {"batch_index_map": {5: J[0], 9: J[1]}},
        ["CL", "RE"],
        # encoded: 005|CLA5|REX0 / 009|CLB3|REC0 (C0 → X0, AST-2124)
        {"005": {"CL": g("A", 5), "RE": g("X", 0)}, "009": {"CL": g("B", 3), "RE": g("C", 0)}},
        {"jobs": [
            {"astral_job_id": "j0", "grades": [
                {"vector": "Clarity", "grade": "A", "confidence": 5}, {"vector": "Remote", "grade": "X", "confidence": 0}]},
            {"astral_job_id": "j1", "grades": [
                {"vector": "Clarity", "grade": "B", "confidence": 3}, {"vector": "Remote", "grade": "X", "confidence": 0}]},
        ]},
    ),
    (
        "grade_do",
        {"batch_entities": J},
        ["CL", "RE"],
        # encoded: 000|CLA5|REB2|remote but vague / 001|CLX0|RED4
        {"000": {"CL": g("A", 5), "RE": g("B", 2), "notes": "remote but vague"},
         "001": {"CL": g("X", 0), "RE": g("D", 4), "notes": None}},
        {"jobs": [
            {"astral_job_id": "j0", "grades": [
                {"vector": "Clarity", "grade": "A", "confidence": 5}, {"vector": "Remote", "grade": "B", "confidence": 2}],
             "notes": "remote but vague"},
            {"astral_job_id": "j1", "grades": [
                {"vector": "Clarity", "grade": "X", "confidence": 0}, {"vector": "Remote", "grade": "D", "confidence": 4}]},
        ]},
    ),
    (
        "qualify_job_listings",
        {"batch_entities": J},
        ["CL", "RE"],
        # encoded: 000|CLA4|REB3|4471|Staff Engineer|https://x.co/j/1|location: Remote|salary_range: 200k / 001|CLF5|REX0|4472
        {"000": {"CL": g("A", 4), "RE": g("B", 3), "company_job_id": "4471", "job_title": "Staff Engineer",
                 "job_link": "https://x.co/j/1", "job_data": {"location": "Remote", "salary_range": "200k"}},
         "001": {"CL": g("F", 5), "RE": g("X", 0), "company_job_id": "4472", "job_title": None,
                 "job_link": None, "job_data": None}},
        {"jobs": [
            {"astral_job_id": "j0", "grades": [
                {"vector": "Clarity", "grade": "A", "confidence": 4}, {"vector": "Remote", "grade": "B", "confidence": 3}],
             "company_job_id": "4471", "job_title": "Staff Engineer", "job_link": "https://x.co/j/1",
             "job_data": {"location": "Remote", "salary_range": "200k"}},
            {"astral_job_id": "j1", "grades": [
                {"vector": "Clarity", "grade": "F", "confidence": 5}, {"vector": "Remote", "grade": "X", "confidence": 0}],
             "company_job_id": "4472"},
        ]},
    ),
    (
        "prefilter_company",
        {"batch_entities": [{"company_id": "c0"}]},
        ["CL", "RE"],
        # encoded: 000|CLA5|REB3|JOB:3,7|CULT:12
        {"000": {"CL": g("A", 5), "RE": g("B", 3), "possible_job_links": [3, 7], "culture_links_to_explore": [12]}},
        {"companies": [
            {"company_id": "c0", "grades": [
                {"vector": "Clarity", "grade": "A", "confidence": 5}, {"vector": "Remote", "grade": "B", "confidence": 3}],
             "possible_job_links": [3, 7], "culture_links_to_explore": [12]},
        ]},
    ),
    (
        VET,
        {"batch_entities": [{"short_name": "a"}, {"short_name": "b"}]},
        ["LT"],
        # encoded: 000|LTA5|https://acme.com / 001|LTF4|https://b.io
        {"000": {"LT": g("A", 5), "website": "https://acme.com"}, "001": {"LT": g("F", 4), "website": "https://b.io"}},
        {"results": [
            {"hit_index": 0, "grade": "A", "website": "https://acme.com", "confidence": 5},
            {"hit_index": 1, "grade": "F", "website": "https://b.io", "confidence": 4},
        ]},
    ),
]


class TestHydrateDownstreamShape:
    @pytest.mark.parametrize(("task_key", "ctx", "codes", "tool", "expected"), _AC3, ids=[c[0] for c in _AC3])
    def test_ac3_matches_old_decoder_shape(self, task_key, ctx, codes, tool, expected) -> None:
        ctx = {**ctx, "vector_labels": {} if task_key == VET else LABELS}
        out = gs.hydrate_grade_tool_input(task_key, ot(task_key), {**tool, "agent_performance": AP}, codes, ctx)
        assert out == expected
        # Schema built from grade_row_ids covers exactly the rows the hydrate maps back.
        schema = gs.build_grade_tool_schema(ot(task_key), codes, gs.grade_row_ids(ctx))
        assert set(schema["properties"]) == {*tool, "agent_performance"}

    def test_label_falls_back_to_code(self) -> None:
        out = gs.hydrate_grade_tool_input("evaluate_jd", ot("evaluate_jd"), {"000": ok_row()}, ["CL", "RE"],
                                          {"batch_entities": J[:1]})
        assert [x["vector"] for x in out["jobs"][0]["grades"]] == ["CL", "RE"]

    def test_rows_follow_row_id_order_not_tool_key_order(self) -> None:
        tool = {"001": {"CL": g("B", 2), "RE": g("B", 2)}, "000": ok_row(), "agent_performance": AP}
        out = gs.hydrate_grade_tool_input("evaluate_jd", ot("evaluate_jd"), tool, ["CL", "RE"], CTX)
        assert [j["astral_job_id"] for j in out["jobs"]] == ["j0", "j1"]


# Light check (stat.agent.grade-vector-validation / confidence-bounds): a bad row fails only that entity.
class TestHydrateLightCheck:
    @pytest.mark.parametrize(
        ("bad", "why"),
        [
            (None, "row 001 missing from tool input"),
            ("A5B3", "row 001 must be an object, got str"),
            ({"CL": g("A", 5)}, "missing vector code RE"),
            ({"CL": g("A", 5), "RE": g("B", 3), "ZZ": g("A", 5)}, "unexpected key ZZ"),
            ({"CL": g("A", 5), "RE": g("X", 3)}, "RE: grade X requires confidence 0, got 3"),
            ({"CL": g("Q", 5), "RE": g("B", 3)}, "CL: illegal grade 'Q'"),
            ({"CL": "A5", "RE": g("B", 3)}, "CL: illegal grade None"),
            ({"CL": g("A", 6), "RE": g("B", 3)}, "CL: confidence must be an integer 0-5, got 6"),
            ({"CL": g("A", -1), "RE": g("B", 3)}, "confidence must be an integer 0-5, got -1"),
            ({"CL": g("A", "5"), "RE": g("B", 3)}, "confidence must be an integer 0-5, got '5'"),
            ({"CL": g("A", True), "RE": g("B", 3)}, "confidence must be an integer 0-5, got True"),
        ],
        ids=["missing-row", "row-not-object", "missing-code", "extra-code", "x-nonzero", "illegal-letter",
             "cell-not-object", "conf-high", "conf-negative", "conf-string", "conf-bool"],
    )
    def test_bad_row_fails_only_its_entity(self, bad, why) -> None:
        tool = {"000": ok_row(), "agent_performance": AP}
        if bad is not None:
            tool["001"] = bad
        out = gs.hydrate_grade_tool_input("evaluate_jd", ot("evaluate_jd"), tool, ["CL", "RE"], CTX)
        assert [j["astral_job_id"] for j in out["jobs"]] == ["j0"]
        (fail,) = out["decode_failures"]
        assert fail == {"astral_job_id": "j1", "pos": 1, "reason": fail["reason"]}
        assert fail["reason"].startswith("[evaluate_jd] ") and why in fail["reason"]

    def test_missing_code_is_never_defaulted_to_x(self) -> None:
        out = gs.hydrate_grade_tool_input("evaluate_jd", ot("evaluate_jd"), {"000": {"CL": g("A", 5)}}, ["CL", "RE"],
                                          {"batch_entities": J[:1], "vector_labels": LABELS})
        assert out["jobs"] == [] and "missing vector code RE" in out["decode_failures"][0]["reason"]

    def test_clean_batch_has_no_decode_failures_key(self) -> None:
        out = gs.hydrate_grade_tool_input("evaluate_jd", ot("evaluate_jd"),
                                          {"000": ok_row(), "001": ok_row(), "agent_performance": AP}, ["CL", "RE"], CTX)
        assert "decode_failures" not in out and len(out["jobs"]) == 2

    def test_unknown_row_warned_once_and_skipped(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level("WARNING")
        tool = {"000": ok_row(), "001": ok_row(), "007": ok_row(), "agent_performance": AP}
        out = gs.hydrate_grade_tool_input("evaluate_jd", ot("evaluate_jd"), tool, ["CL", "RE"], CTX)
        assert "decode_failures" not in out and len(out["jobs"]) == 2
        warns = [r.getMessage() for r in caplog.records if r.levelname == "WARNING"]
        assert warns == ["evaluate_jd skipped — index 007 not in this batch\n  This line is not being graded"]

    def test_mangled_row_key_is_unknown_and_real_row_fails_missing(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level("WARNING")
        out = gs.hydrate_grade_tool_input("evaluate_jd", ot("evaluate_jd"), {"000": ok_row(), "1": ok_row()},
                                          ["CL", "RE"], CTX)
        assert out["decode_failures"][0]["astral_job_id"] == "j1"
        assert "row 001 missing from tool input" in out["decode_failures"][0]["reason"]
        assert any("index 1 not in this batch" in r.getMessage() for r in caplog.records)

    def test_company_task_keys_by_company_id(self) -> None:
        out = gs.hydrate_grade_tool_input("prefilter_company", ot("prefilter_company"), {}, ["CL", "RE"],
                                          {"batch_entities": [{"company_id": "c9"}]})
        assert out == {"companies": [], "decode_failures": [
            {"company_id": "c9", "pos": 0, "reason": "[prefilter_company] row 000 missing from tool input"}]}


# Extra fields: null / absent skipped; wrong JSON type fails the entity; text stripped, blanks dropped.
class TestHydrateExtraFields:
    def _one(self, task_key: str, extras: dict) -> dict:
        ctx = {"batch_entities": [{"company_id": "c0", "astral_job_id": "j0"}], "vector_labels": LABELS}
        return gs.hydrate_grade_tool_input(task_key, ot(task_key), {"000": {**ok_row(), **extras}}, ["CL", "RE"], ctx)

    def test_absent_extra_counts_as_null(self) -> None:
        out = self._one("grade_do", {})
        assert "notes" not in out["jobs"][0] and "decode_failures" not in out

    @pytest.mark.parametrize(
        ("task_key", "extras", "why"),
        [
            ("grade_do", {"notes": 5}, "notes must be string, got int"),
            ("prefilter_company", {"possible_job_links": "3,7"}, "possible_job_links must be array, got str"),
            ("prefilter_company", {"possible_job_links": [3, "7"]}, "possible_job_links must be array, got list"),
            ("prefilter_company", {"possible_job_links": [True]}, "possible_job_links must be array, got list"),
            ("qualify_job_listings", {"job_data": {"location": 3}}, "job_data must be object, got dict"),
            ("qualify_job_listings", {"job_data": ["Remote"]}, "job_data must be object, got list"),
        ],
        ids=["notes-int", "links-string", "links-mixed", "links-bool", "job-data-nonstring", "job-data-list"],
    )
    def test_wrong_type_fails_the_entity(self, task_key, extras, why) -> None:
        out = self._one(task_key, extras)
        array_key = "companies" if task_key == "prefilter_company" else "jobs"
        assert out[array_key] == [] and why in out["decode_failures"][0]["reason"]

    def test_text_stripped_and_blanks_dropped(self) -> None:
        out = self._one("qualify_job_listings", {
            "company_job_id": "  4471 ", "job_title": "   ", "job_link": "",
            "job_data": {" location ": " Remote ", "salary_range": "  "},
        })
        row = out["jobs"][0]
        assert row["company_job_id"] == "4471"
        assert "job_title" not in row and "job_link" not in row
        assert row["job_data"] == {"location": "Remote", "salary_range": None}

    def test_empty_array_and_object_dropped(self) -> None:
        out = self._one("prefilter_company", {"possible_job_links": [], "culture_links_to_explore": [4]})
        assert "possible_job_links" not in out["companies"][0]
        assert out["companies"][0]["culture_links_to_explore"] == [4]
        assert "job_data" not in self._one("qualify_job_listings", {"job_data": {}})["jobs"][0]


# Vet: one LT code, A–F, confidence 1–5 (no X0 rewrite), website required per hit.
class TestHydrateVet:
    def _vet(self, row: dict) -> dict:
        return gs.hydrate_grade_tool_input(VET, ot(VET), {"000": row, "agent_performance": AP}, ["LT"], VCTX)

    def test_confidence_zero_is_out_of_range_not_rewritten(self) -> None:
        out = self._vet({"LT": g("A", 0), "website": "https://a.co"})
        assert out["results"] == []
        assert out["decode_failures"] == [
            {"hit_index": 0, "pos": 0, "reason": "[vet_inflow_discovery] row 000 LT: confidence must be an integer 1-5, got 0"}]

    def test_x_is_not_a_vet_letter(self) -> None:
        assert "illegal grade 'X'" in self._vet({"LT": g("X", 1), "website": "https://a.co"})["decode_failures"][0]["reason"]

    @pytest.mark.parametrize("website", [None, "  "], ids=["null", "blank"])
    def test_missing_website_fails_the_hit(self, website) -> None:
        out = self._vet({"LT": g("A", 5), "website": website})
        assert out["results"] == [] and "row 000 missing website" in out["decode_failures"][0]["reason"]

    def test_website_stripped(self) -> None:
        assert self._vet({"LT": g("B", 3), "website": " https://a.co "})["results"] == [
            {"hit_index": 0, "grade": "B", "website": "https://a.co", "confidence": 3}]

    def test_vet_requires_exactly_one_code(self) -> None:
        with pytest.raises(ValueError, match="exactly one vector code"):
            gs.hydrate_grade_tool_input(VET, ot(VET), {}, ["LT", "XX"], VCTX)


# Contract errors: non-object tool input; non-grader output type.
class TestHydrateContractErrors:
    def test_non_object_tool_input_raises(self) -> None:
        with pytest.raises(TypeError, match=r"\[evaluate_jd\] tool input must be an object, got list"):
            gs.hydrate_grade_tool_input("evaluate_jd", ot("evaluate_jd"), [], ["CL"], CTX)

    def test_non_grader_output_type_raises(self) -> None:
        with pytest.raises(ValueError, match="not a structured-output grader type"):
            gs.hydrate_grade_tool_input("evaluate_jd", "grades_json", {}, ["CL"], CTX)
