"""Component tests for src/utils/formatting.py (AST-390)."""

from __future__ import annotations

import json

import pytest

from src.utils import formatting as fmt


# Branches: empty array; keyed match; keyed mismatch; numbered; label present/absent.
class TestEnumerateArray:
    def test_empty_array_returns_empty_string(self) -> None:
        assert fmt.enumerate_array("URLs", []) == ""

    def test_keyed_format_when_lengths_match(self) -> None:
        out = fmt.enumerate_array(
            "Links",
            ["a", "b"],
            index_key="id",
            index_values=["1", "2"],
        )
        assert out == "Links:\n[id=1]: a\n[id=2]: b"

    def test_numbered_format_when_keyed_inputs_do_not_match(self) -> None:
        out = fmt.enumerate_array("Items", ["x"], index_key="id", index_values=["1", "2"])
        assert out == "Items:\n1: x"

    def test_numbered_format_without_label(self) -> None:
        assert fmt.enumerate_array("", ["only"]) == "1: only"


# Branches: empty; scheme strip; fragment drop; slash collapse; index suffix strip.
class TestNormalizeLink:
    def test_plan_examples(self) -> None:
        assert fmt.normalize_link("https://Acme.com/careers/") == "acme.com/careers"
        assert fmt.normalize_link("http://www.acme.com/jobs/index.html") == "www.acme.com/jobs"
        assert fmt.normalize_link("//careers.acme.com/openings//") == "careers.acme.com/openings"

    def test_empty_and_whitespace(self) -> None:
        assert fmt.normalize_link("") == ""
        assert fmt.normalize_link("   ") == ""


# Branches: blank lines; bad prefix; non-int index; happy path.
class TestParseEnumerateArray:
    def test_parses_numbered_lines(self) -> None:
        assert fmt.parse_enumerate_array("1: alpha\n2: beta") == {1: "alpha", 2: "beta"}

    def test_skips_blank_and_malformed_lines(self) -> None:
        text = "\n\nbad\n: no index\n1: ok\nx: not int"
        assert fmt.parse_enumerate_array(text) == {1: "ok"}


# Branches: None/str/list(dict)/list(other)/dict/other.
class TestValueToStr:
    def test_none_and_string(self) -> None:
        assert fmt.value_to_str(None) == ""
        assert fmt.value_to_str("plain") == "plain"

    def test_markdown_sections_with_optional_code(self) -> None:
        val = [{"label": "A", "content": "body", "code": "X"}, {"label": "", "content": "skip"}]
        assert fmt.value_to_str(val) == "### A (X)\nbody"

    def test_nested_list_and_dict(self) -> None:
        assert fmt.value_to_str([1, {"k": "v"}]) == "1\n{\n  \"k\": \"v\"\n}"
        assert fmt.value_to_str(7) == "7"


# Branches: confidence label present/absent.
class TestFormatGradeDisplay:
    def test_with_and_without_confidence_label(self) -> None:
        assert fmt.format_grade_display({"vector": "V", "grade": "A", "confidence_label": "high"}) == "V: A (high)"
        assert fmt.format_grade_display({"vector": "V", "grade": "B"}) == "V: B"


# Branches: None/non-str; consecutive blanks; whitespace-only lines; preserve content.
class TestCollapseConsecutiveBlankLines:
    def test_collapses_runs_of_blank_lines(self) -> None:
        assert fmt.collapse_consecutive_blank_lines("line1\n\n\nline2") == "line1\n\nline2"
        assert fmt.collapse_consecutive_blank_lines("line1\n \n\t\nline2") == "line1\n\nline2"

    def test_preserves_single_blank_and_non_blank_content(self) -> None:
        assert fmt.collapse_consecutive_blank_lines("line1\nline2") == "line1\nline2"
        assert fmt.collapse_consecutive_blank_lines("  content  ") == "  content  "
        assert fmt.collapse_consecutive_blank_lines("only") == "only"

    def test_empty_and_whitespace_only_input(self) -> None:
        assert fmt.collapse_consecutive_blank_lines("") == ""
        assert fmt.collapse_consecutive_blank_lines("\n\n\n") == ""

    def test_none_and_non_string_passthrough(self) -> None:
        assert fmt.collapse_consecutive_blank_lines(None) == ""  # type: ignore[arg-type]
        assert fmt.collapse_consecutive_blank_lines(7) == 7  # type: ignore[arg-type]


# Branches: empty delimiter raises; strip/filter empties.
class TestSplitToList:
    def test_rejects_empty_delimiter(self) -> None:
        with pytest.raises(ValueError, match="delimiter must be non-empty"):
            fmt.split_to_list("a,b", "")

    def test_splits_strips_and_drops_empties(self) -> None:
        assert fmt.split_to_list(" a , ,b ") == ["a", "b"]


# Branches: non-str/empty input; HTML text extraction.
class TestParseText:
    def test_non_string_or_empty_returns_empty(self) -> None:
        assert fmt.parse_text("") == ""
        assert fmt.parse_text(None) == ""  # type: ignore[arg-type]

    def test_extracts_visible_text(self) -> None:
        html = "<div><span>Hello</span> <i>$</i>10</div>"
        assert fmt.parse_text(html) == "Hello $ 10"


# Branches: no titles; single title; phase1 deepest; phase2 siblings; fallback.
class TestFindJobContainers:
    def test_empty_titles_returns_full_dom(self) -> None:
        dom = "<div><p>Job A</p><p>Job B</p></div>"
        assert fmt.find_job_containers(dom, []) == [dom]

    def test_single_title_returns_full_dom(self) -> None:
        dom = "<div>Only one</div>"
        assert fmt.find_job_containers(dom, ["Only one"]) == [dom]

    def test_phase_one_deepest_container(self) -> None:
        dom = (
            "<div id='root'>"
            "<section><h2>Job A</h2><h2>Job B</h2></section>"
            "<div><span>Job A</span><span>Job B</span></div>"
            "</div>"
        )
        out = fmt.find_job_containers(dom, ["Job A", "Job B"])
        assert len(out) >= 1
        assert all("Job A" in chunk and "Job B" in chunk for chunk in out)

    def test_phase_two_sibling_containers(self) -> None:
        dom = (
            "<div id='root'>"
            "<div class='left'>Job A role</div>"
            "<div class='right'>Job B role</div>"
            "</div>"
        )
        out = fmt.find_job_containers(dom, ["Job A", "Job B"])
        assert len(out) == 1
        assert "Job A" in out[0] and "Job B" in out[0]

    def test_fallback_when_titles_missing(self) -> None:
        dom = "<div>unrelated</div>"
        assert fmt.find_job_containers(dom, ["Missing A", "Missing B"]) == [dom]


# Branches: invalid input; missing key; closed string; truncated payload; fence stripping.
class TestHealAgentPayloadEnvelope:
    def test_returns_none_for_non_string_or_blank(self) -> None:
        assert fmt.heal_agent_payload_envelope("") is None
        assert fmt.heal_agent_payload_envelope("   ") is None

    def test_returns_none_when_key_or_string_opener_missing(self) -> None:
        assert fmt.heal_agent_payload_envelope('{"other":1}') is None
        assert fmt.heal_agent_payload_envelope('{"agent_payload": 12}') is None

    def test_returns_none_when_string_already_closed(self) -> None:
        raw = '{"agent_payload":"done"}'
        assert fmt.heal_agent_payload_envelope(raw) is None

    def test_heals_truncated_newline_delimited_payload(self) -> None:
        raw = '{"agent_payload":"line one\nline two'
        healed = fmt.heal_agent_payload_envelope(raw)
        assert healed is not None
        parsed = json.loads(healed)
        assert parsed["agent_payload"].startswith("line one")

    def test_strips_markdown_fences_before_healing(self) -> None:
        raw = "```json\n" + '{"agent_payload":"a\nb'
        healed = fmt.heal_agent_payload_envelope(raw)
        assert healed is not None
        assert json.loads(healed)["agent_payload"] == "a\n"


# Branches: already valid; fence strip; truncate close; in-string root comma guard; failure paths.
class TestHealJson:
    def test_returns_none_for_non_string_or_blank(self) -> None:
        assert fmt.heal_json(123) is None  # type: ignore[arg-type]
        assert fmt.heal_json("   ") is None

    def test_returns_original_when_already_valid(self) -> None:
        assert fmt.heal_json('{"a":1}') == '{"a":1}'

    def test_heals_truncated_object(self) -> None:
        healed = fmt.heal_json('{"a":[1,2,3], "b":')
        assert healed == '{"a":[1,2,3]}'

    def test_returns_none_when_root_key_truncated_inside_array_string(self) -> None:
        assert fmt.heal_json('{"a":[1,2,3], "b":[4,5,"pa') is None

    def test_heals_fenced_truncated_json(self) -> None:
        raw = "```json\n{\"x\":1,"
        assert fmt.heal_json(raw) == '{"x":1}'

    def test_emit_json_string_body_escapes_controls(self) -> None:
        raw = 'a\nb"\\c\x01'
        out = fmt._emit_json_string_body(raw)
        assert out == 'a\\nb\\"\\c\\u0001'
        assert fmt._emit_json_string_body("a\r\\") == 'a\\r\\'

    def test_heals_after_cleaned_json_already_valid(self) -> None:
        assert fmt.heal_json('```json\n{"x":1}\n```') == '{"x":1}'

    def test_returns_none_when_fence_strips_to_empty(self) -> None:
        assert fmt.heal_json("```\n```") is None

    def test_returns_none_when_no_checkpoint_or_invalid_heal(self) -> None:
        assert fmt.heal_json("{not json at all") is None
        assert fmt.heal_json('{"a":[1,2,3], "b":[4,5,"pa') is None
        assert fmt.heal_json('{"items":[1,2,],') is None
        assert fmt.heal_json('{"name":"abc') is None

    def test_heals_truncated_nested_object_inside_array(self) -> None:
        assert fmt.heal_json('{"a":[1,{"b":2') == '{"a":[1]}'

    def test_heals_trailing_comma_after_last_key(self) -> None:
        assert fmt.heal_json('{"a":1,"b":2,') == '{"a":1,"b":2}'

    def test_heals_string_with_json_escape_sequences(self) -> None:
        assert fmt.heal_json('{"a":"\\r\\n"}') == '{"a":"\\r\\n"}'


class TestHealAgentPayloadEnvelopeEdges:
    def test_returns_none_for_non_string(self) -> None:
        assert fmt.heal_agent_payload_envelope(None) is None  # type: ignore[arg-type]

    def test_returns_none_when_colon_or_cut_missing(self) -> None:
        assert fmt.heal_agent_payload_envelope('{"agent_payload" no-colon') is None
        assert fmt.heal_agent_payload_envelope('{"agent_payload":"no newline cut') is None

    def test_heals_json_escape_newline_boundary(self) -> None:
        raw = '{"agent_payload":"line\\nnext'
        healed = fmt.heal_agent_payload_envelope(raw)
        assert healed is not None
        assert json.loads(healed)["agent_payload"] == "line\n"
