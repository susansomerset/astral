"""Component tests for src/core/agent.py (AST-393)."""

from __future__ import annotations

import inspect
import json
from typing import Any, Dict, List, Tuple
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import agent as agent_mod
from src.core import consult as consult_mod
from src.data import database as database_mod
from src.utils import config as cfg
from src.utils.config import ASTRAL_CONFIG, TASK_CONFIG, resolve_tokens


def _batch_entities(*job_ids: str) -> List[Dict[str, str]]:
    return [{"astral_job_id": job_id} for job_id in job_ids]


def _agent_rows(*, run_next: str = "", brain_setting: str = "Little") -> Tuple[Dict[str, Any], Dict[str, Any]]:
    return (
        {
            "content": "agent sys",
            "model_code": "claude-haiku-4-5",
            "brain_setting": brain_setting,
            "agent_id": "agent-1",
            "temperature": 0.4,
            "max_tokens": 100,
        },
        {
            "user_prompt": "user",
            "cache_prompt": "cache",
            "nocache_prompt": "nocache",
            "system_prompt": "",
            "task_key_uuid": "uuid-1",
            "agent_id": "agent-1",
            "run_next": run_next,
        },
    )


def _api_response(text: str = "raw") -> Any:
    return type("Resp", (), {"content": [type("Blk", (), {"text": text})()], "id": "req-1"})()


def _llm_failure_envelope(**extra: Any) -> Dict[str, Any]:
    """Strict encoded-batch tasks require agent_performance + agent_payload (AST-501)."""
    body: Dict[str, Any] = {"agent_performance": "failure", "agent_payload": "", "failure_note": "nope"}
    body.update(extra)
    return body


def _rubric_evaluate_jd_ctx() -> Dict[str, Any]:
    return {"candidate_data": {}, "batch_entities": _batch_entities("job-1")}


def _patch_normalize_rubric_response(
    monkeypatch: pytest.MonkeyPatch,
    side_effect: Any,
) -> None:
    """evaluate_jd rubric path uses consult normalize, not agent._decode_payload (AST-603)."""
    monkeypatch.setattr(consult_mod, "_normalize_rubric_task_response", side_effect)


def _strict_batch_llm_ok(*, payload: str = "0|CRA2", api_label: str = "raw") -> Dict[str, Any]:
    """Mock LLM result for _STRICT_ENCODED_BATCH_CONSULT_KEYS tasks (AST-501 envelope)."""
    return {
        "success": True,
        "parsed_response": {"agent_performance": "success", "agent_payload": payload},
        "api_response": _api_response(api_label),
        "timesheet": {},
    }


def _patch_strict_batch_anthropic(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default active_provider is deepseek; chain-hop tests mock send_to_anthropic only."""
    monkeypatch.setattr(agent_mod, "get_active_llm_provider", lambda: "anthropic")
    monkeypatch.setattr(agent_mod, "send_to_deepseek", AsyncMock())


@pytest.fixture
def batch_token() -> Any:
    token = agent_mod.log_batch_id.set("batch-1")
    yield token
    agent_mod.log_batch_id.reset(token)


@pytest.fixture
def agent_prompt_rows(monkeypatch: pytest.MonkeyPatch) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    rows = _agent_rows()
    monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: rows)
    return rows


@pytest.fixture
def stub_agent_storage(monkeypatch: pytest.MonkeyPatch) -> Dict[str, MagicMock]:
    mocks = {
        "save": MagicMock(),
        "append": MagicMock(),
        "audit": MagicMock(),
    }
    monkeypatch.setattr(agent_mod, "save_agent_data", mocks["save"])
    monkeypatch.setattr(agent_mod, "append_agent_response", mocks["append"])
    monkeypatch.setattr(agent_mod, "add_agent_response_entry", mocks["audit"])
    monkeypatch.setattr(agent_mod, "compute_batch_cost", lambda batch_id: 1.0)
    return mocks


@pytest.fixture
def enable_debug_log(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(agent_mod.logger, "isEnabledFor", lambda level: level == agent_mod._LOG_DEBUG)


def _draft_job_resume_ctx() -> dict[str, Any]:
    """Truthy candidate_data so AST-594 catalog validation runs (empty {} skips it)."""
    return {"candidate_data": {"artifacts": {}}}


# Branches: X grade conf 0 (inner loop continue), empty job.grades skip (89->85), CRX0 decode segment
class TestGradeValidation:
    def test_rejects_bad_confidence_and_non_object_rows(self) -> None:
        assert agent_mod._validate_grade_confidence_list([], "grades") is None
        assert "must be object" in agent_mod._validate_grade_confidence_list(["bad"], "grades")
        assert "confidence must be int" in agent_mod._validate_grade_confidence_list(
            [{"grade": "A", "confidence": "2"}], "grades"
        )
        assert "grade X requires confidence 0" in agent_mod._validate_grade_confidence_list(
            [{"grade": "X", "confidence": 2}], "grades"
        )
        assert "confidence must be 1-5" in agent_mod._validate_grade_confidence_list(
            [{"grade": "A", "confidence": 0}], "grades"
        )

    def test_walks_payload_jobs_and_top_level_grades(self) -> None:
        payload = {
            "jobs": [{"grades": [{"grade": "A", "confidence": 2, "vector": "fit"}]}],
            "grades": [{"grade": "A", "confidence": 2, "vector": "fit"}],
        }
        assert agent_mod._validate_grade_confidence_in_payload(payload, "task") is None
        bad = {"jobs": [{"grades": [{"grade": "A", "confidence": 0, "vector": "fit"}]}]}
        assert "confidence must be 1-5" in agent_mod._validate_grade_confidence_in_payload(bad, "task")

    def test_accepts_x_zero_confidence_and_skips_empty_job_grades(self) -> None:
        assert agent_mod._validate_grade_confidence_list([{"grade": "X", "confidence": 0}], "g") is None
        assert agent_mod._validate_grade_confidence_in_payload({"jobs": [{"grades": []}]}, "t") is None


class TestInnerTaskPayload:
    def test_unwraps_agent_payload_or_returns_raw(self) -> None:
        assert agent_mod._inner_task_payload({"agent_payload": {"ok": True}}) == {"ok": True}
        assert agent_mod._inner_task_payload({"flat": True}) == {"flat": True}
        assert agent_mod._inner_task_payload("raw") == "raw"


class TestDecodePayload:
    def test_decodes_grade_rows_and_meta_fields(self) -> None:
        ctx = {
            "batch_entities": _batch_entities("job-1"),
            "vector_labels": {"CR": "Culture"},
        }
        payload = "0|CRA2|company-1|Title|https://example.com/job|location:Remote"
        decoded = agent_mod._decode_payload("qualify_job_listings", "grades_meta", payload, ctx)
        job = decoded["jobs"][0]
        assert job["astral_job_id"] == "job-1"
        assert job["grades"] == [{"vector": "Culture", "grade": "A", "confidence": 2}]
        assert job["company_job_id"] == "company-1"
        assert job["job_data"]["location"] == "Remote"

    def test_decodes_notes_tail_and_skips_out_of_range_lines(self, caplog: pytest.LogCaptureFixture) -> None:
        ctx = {"batch_entities": _batch_entities("job-1")}
        notes = agent_mod._decode_payload(
            "consult_do",
            "grades_encoded_notes",
            "0|CRA2|note one|note two",
            ctx,
        )
        assert notes["jobs"][0]["notes"] == "note one|note two"
        skipped = agent_mod._decode_payload("consult_do", "grades", "1|CRAP2", ctx)
        assert skipped["jobs"] == []
        assert "skipping line with pos 1" in caplog.text

    def test_rejects_bad_positions_and_trailing_meta(self) -> None:
        ctx = {"batch_entities": _batch_entities("job-1")}
        with pytest.raises(ValueError, match="bad position"):
            agent_mod._decode_payload("task", "grades", "bad|CRA2", ctx)
        with pytest.raises(ValueError, match="unexpected trailing content"):
            agent_mod._decode_payload("task", "grades", "0|CRA2|extra", ctx)
        with pytest.raises(ValueError, match="grade X requires confidence digit 0"):
            agent_mod._decode_payload("task", "grades", "0|CRX2", ctx)

    def test_decodes_x_zero_notes_and_bare_notes_line(self) -> None:
        ctx = {"batch_entities": _batch_entities("job-1")}
        ok_x = agent_mod._decode_payload("task", "grades", "0|CRX0", ctx)
        assert ok_x["jobs"][0]["grades"][0]["grade"] == "X"
        assert ok_x["jobs"][0]["grades"][0]["confidence"] == 0
        tail = agent_mod._decode_payload("consult_do", "grades_encoded_notes", "0|CRX0|  ", ctx)
        assert "notes" not in tail["jobs"][0]
        bare = agent_mod._decode_payload(
            "grade_do",
            "grades_encoded_notes",
            "0|CRA2",
            {"batch_entities": _batch_entities("job-1")},
        )
        assert "notes" not in bare["jobs"][0]

    def test_decodes_whitespace_inside_grade_tokens_preserves_meta(self) -> None:
        # AST-483: _GRADE_SEG match uses norm (strip space / hyphen / colon); meta slots keep originals.
        graded_ctx = {
            "batch_entities": _batch_entities("job-1"),
            "vector_labels": {"DT": "Duty", "GC": "Greatness"},
        }
        embellished = agent_mod._decode_payload("evaluate_jd", "grades", "0|DT A5|GC-B4", graded_ctx)
        compact = agent_mod._decode_payload("evaluate_jd", "grades", "0|DTA5|GCB4", graded_ctx)
        expect = [
            {"vector": "Duty", "grade": "A", "confidence": 5},
            {"vector": "Greatness", "grade": "B", "confidence": 4},
        ]
        assert embellished["jobs"][0]["grades"] == expect
        assert compact["jobs"][0]["grades"] == expect

        meta_ctx = {
            "batch_entities": _batch_entities("job-1"),
            "vector_labels": {"CR": "Culture"},
        }
        payload_meta = "0|CR A2|company-1|Sr Job Role|https://example.com/job|location:Remote"
        decoded = agent_mod._decode_payload("qualify_job_listings", "grades_meta", payload_meta, meta_ctx)
        job = decoded["jobs"][0]
        assert job["grades"] == [{"vector": "Culture", "grade": "A", "confidence": 2}]
        assert job["company_job_id"] == "company-1"
        assert job["job_title"] == "Sr Job Role"


def _ast603_prefilter_task_config() -> Dict[str, Any]:
    return TASK_CONFIG["prefilter_company"]


def _ast603_prefilter_ctx() -> Dict[str, Any]:
    criteria = [
        {
            "label": "Reality Check",
            "code": "RC",
            "content": "body\nA = real\nB = ok",
            "importance": 5,
            "grade_descriptions": [{"grade": "A", "description": "real company"}],
        },
        {
            "label": "Mission Product Orientation",
            "code": "MP",
            "content": "body\nA = aligned\nB = ok",
            "importance": 5,
            "grade_descriptions": [{"grade": "B", "description": "decent fit"}],
        },
        {
            "label": "US Presence",
            "code": "UP",
            "content": "body\nA = us\nB = ok",
            "importance": 3,
            "grade_descriptions": [{"grade": "A", "description": "US based"}],
        },
    ]
    return {
        "candidate_data": {"artifacts": {"company_prefilter": criteria}},
        "batch_entities": [{"astral_job_id": "co-acme"}],
        "vector_labels": {
            "RC": "Reality Check",
            "MP": "Mission Product Orientation",
            "US": "US Presence",
        },
    }


class TestAst603RubricNormalize:
    """AST-603: consult-parity rubric response normalization before do_task validation."""

    def test_karbon_dict_envelope_yields_jobs_grades(self) -> None:
        parsed = {
            "agent_performance": {"status": "success"},
            "agent_payload": {
                "reality_check": "A",
                "mission_product_orientation": "B",
                "us_presence": "A",
                "possible_job_links": [77],
                "culture_links_to_explore": [75, 76],
            },
        }
        out = consult_mod._normalize_rubric_task_response(
            "prefilter_company", _ast603_prefilter_task_config(), parsed, _ast603_prefilter_ctx()
        )
        job = out["jobs"][0]
        assert len(job["grades"]) == 3
        assert job["possible_job_links"] == [77]
        assert job["culture_links_to_explore"] == [75, 76]

    def test_letter_pipe_parses_grades_and_link_indices(self) -> None:
        out = consult_mod._normalize_rubric_task_response(
            "prefilter_company",
            _ast603_prefilter_task_config(),
            "A|B|A|15|13,16,14",
            _ast603_prefilter_ctx(),
        )
        job = out["jobs"][0]
        assert [g["grade"] for g in job["grades"]] == ["A", "B", "A"]
        assert job["possible_job_links"] == [15]
        assert job["culture_links_to_explore"] == [13, 16, 14]

    def test_berry_json_string_payload(self) -> None:
        payload = (
            '{"Reality_Check":"A","Mission_Product_Orientation":"B","US_Presence":"A",'
            '"POSSIBLE_JOB_LINKS":[7],"CULTURE_LINKS_TO_EXPLORE":[10,5,3]}'
        )
        out = consult_mod._normalize_rubric_task_response(
            "prefilter_company", _ast603_prefilter_task_config(), payload, _ast603_prefilter_ctx()
        )
        job = out["jobs"][0]
        assert len(job["grades"]) == 3
        assert job["possible_job_links"] == [7]
        assert job["culture_links_to_explore"] == [10, 5, 3]

    def test_lovable_encoded_line_with_job_cult_tails(self) -> None:
        out = consult_mod._normalize_rubric_task_response(
            "prefilter_company",
            _ast603_prefilter_task_config(),
            "000|RCA3|MPB3|USA3|JOB:16|CULT:38,3,27",
            _ast603_prefilter_ctx(),
        )
        job = out["jobs"][0]
        assert len(job["grades"]) == 3
        assert job["possible_job_links"] == [16]
        assert job["culture_links_to_explore"] == [38, 3, 27]

    def test_parse_link_index_field_variants(self) -> None:
        assert consult_mod._parse_link_index_field("[7]") == [7]
        assert consult_mod._parse_link_index_field("JOB:16") == [16]
        assert consult_mod._parse_link_index_field("CULT:38,3") == [38, 3]

    def test_lovable_encoded_line_with_bracket_tails(self) -> None:
        # AST-697: positional bracket link_set tails via consult normalizer (AST-603 path).
        out = consult_mod._normalize_rubric_task_response(
            "prefilter_company",
            _ast603_prefilter_task_config(),
            "000|RCA3|MPB3|USA3|[59,60]|[51,46,53]",
            _ast603_prefilter_ctx(),
        )
        job = out["jobs"][0]
        assert job["possible_job_links"] == [59, 60]
        assert job["culture_links_to_explore"] == [51, 46, 53]


class TestAst697PrefilterBracketLinkDecode:
    """AST-697: bracket link_set tails in _decode_payload and shared consult helper."""

    @staticmethod
    def _prefilter_decode_ctx() -> Dict[str, Any]:
        return {
            "batch_entities": [{"astral_job_id": "co-acme"}],
            "vector_labels": {
                "RC": "Reality Check",
                "MP": "Mission Product Orientation",
                "US": "US Presence",
            },
        }

    def test_decode_payload_susan_canonical_bracket_tails(self) -> None:
        ctx = {
            "batch_entities": [{"astral_job_id": "acme"}],
            "vector_labels": {"ER": "Example", "ME": "Mission", "PG": "Product"},
        }
        job = agent_mod._decode_payload(
            "prefilter_company",
            "grades_encoded_prefilter_links",
            "000|ERC2|MEA3|PGA2|[13]|[3,6,19]",
            ctx,
        )["jobs"][0]
        assert job["possible_job_links"] == [13]
        assert job["culture_links_to_explore"] == [3, 6, 19]

    def test_decode_payload_bracket_tails_rca_mpb_usa(self) -> None:
        job = agent_mod._decode_payload(
            "prefilter_company",
            "grades_encoded_prefilter_links",
            "000|RCA3|MPB3|USA3|[59,60]|[51,46,53]",
            self._prefilter_decode_ctx(),
        )["jobs"][0]
        assert job["possible_job_links"] == [59, 60]
        assert job["culture_links_to_explore"] == [51, 46, 53]

    def test_decode_payload_job_cult_prefix_unchanged(self) -> None:
        job = agent_mod._decode_payload(
            "prefilter_company",
            "grades_encoded_prefilter_links",
            "000|RCA3|MPB3|USA3|JOB:16|CULT:38,3,27",
            self._prefilter_decode_ctx(),
        )["jobs"][0]
        assert job["possible_job_links"] == [16]
        assert job["culture_links_to_explore"] == [38, 3, 27]

    def test_decode_payload_grades_only_omits_link_keys(self) -> None:
        job = agent_mod._decode_payload(
            "prefilter_company",
            "grades_encoded_prefilter_links",
            "000|RCA3|MPB3|USA3",
            self._prefilter_decode_ctx(),
        )["jobs"][0]
        assert "possible_job_links" not in job
        assert "culture_links_to_explore" not in job


class TestAst699LetterPipePositionPrefix:
    """AST-699: position-prefixed letter-pipe lines must not misroute to _decode_payload."""

    def test_position_prefixed_letter_pipe_bracket_tails(self) -> None:
        out = consult_mod._normalize_rubric_task_response(
            "prefilter_company",
            _ast603_prefilter_task_config(),
            "0|A|B|A|[35]|[22,34,39,52,53]",
            _ast603_prefilter_ctx(),
        )
        job = out["jobs"][0]
        assert [g["grade"] for g in job["grades"]] == ["A", "B", "A"]
        assert job["possible_job_links"] == [35]
        assert job["culture_links_to_explore"] == [22, 34, 39, 52, 53]

    def test_bare_letter_pipe_bracket_tails(self) -> None:
        out = consult_mod._normalize_rubric_task_response(
            "prefilter_company",
            _ast603_prefilter_task_config(),
            "A|B|A|[35]|[22,34,39,52,53]",
            _ast603_prefilter_ctx(),
        )
        job = out["jobs"][0]
        assert job["possible_job_links"] == [35]
        assert job["culture_links_to_explore"] == [22, 34, 39, 52, 53]

    def test_should_decode_as_encoded_line_routing(self) -> None:
        assert consult_mod._should_decode_as_encoded_line("0|A|B|A|[35]|[22,34,39,52,53]") is False
        assert consult_mod._should_decode_as_encoded_line("000|RCA3|MPB3|USA3|[59,60]|[51,46,53]") is True
        assert consult_mod._should_decode_as_encoded_line("A|B|A|15|13,16,14") is False


class TestAst698DoTaskDebugRawResponse:
    @pytest.mark.asyncio
    async def test_short_raw_response_emits_under_debug_contract(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        caplog.set_level("INFO")
        short_body = '{\n  "agent_performance": {},\n  "agent_payload": "0|CRA2"\n}'
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_performance": {}, "agent_payload": "0|CRA2"},
                    "api_response": _api_response(short_body),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
            debug=True,
        )
        assert out["success"] is True
        combined = "\n".join(r.message for r in caplog.records)
        assert "raw_response task_key=evaluate_jd" in combined
        assert "agent_payload" in combined

    @pytest.mark.asyncio
    async def test_encoded_payload_uses_contract_helpers_not_legacy_info(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        caplog.set_level("INFO")
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(return_value=_strict_batch_llm_ok(api_label="envelope")),
        )
        await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
            debug=True,
        )
        combined = "\n".join(r.message for r in caplog.records)
        assert "encoded_payload task_key=evaluate_jd" in combined
        assert "literal encoded agent_payload" not in combined

    @pytest.mark.asyncio
    async def test_debug_false_skips_raw_response_contract_lines(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        caplog.set_level("INFO")
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(return_value=_strict_batch_llm_ok(api_label="envelope")),
        )
        await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
            debug=False,
        )
        combined = "\n".join(r.message for r in caplog.records)
        assert "raw_response task_key=" not in combined
        assert "encoded_payload task_key=" not in combined


class TestPromptHelpers:
    def test_resolves_system_prompt_and_chain_tokens(self) -> None:
        agent_row = {"content": "agent {$TASK}", "model_code": "claude"}
        task_row = {"system_prompt": "task {$TASK}"}
        cd = {"profile": {"first": "Ada"}}
        assert "task" in agent_mod.resolved_task_system(agent_row, task_row, cd, "qualify_job_listings", {})
        hop = agent_mod._chain_tokens_for_next_hop(
            system_content="sys",
            cache_content="cache",
            nocache_content="nocache",
            live_content="live",
            parsed={"jobs": []},
        )
        assert json.loads(hop["CALLER_RESPONSE"]) == {"jobs": []}
        assert "CACHED CONTEXT" in hop["CACHE_BLOCK_B"]

    def test_builds_context_and_assembles_blocks(self) -> None:
        cfg = TASK_CONFIG["qualify_job_listings"]
        assert agent_mod._build_context("qualify_job_listings", cfg, None) == "qualify_job_listings"
        assert agent_mod._build_context("qualify_job_listings", cfg, "job-1").endswith("job-1")
        system_blocks, user_blocks, runtime, prompt_tokens, live_tokens = agent_mod._assemble_blocks(
            system_content="system",
            user_content="user",
            cache_content="cache",
            nocache_content="nocache",
            live_content="live",
            model_code="claude",
            skip_cache=True,
        )
        assert system_blocks[0]["text"] == "system"
        assert "cache_control" not in system_blocks[0]
        assert any("CONTENT" in block["text"] for block in user_blocks)
        assert runtime
        assert prompt_tokens > 0
        assert live_tokens > 0


class TestResponseValidation:
    def test_validates_envelope_and_required_fields(self) -> None:
        schema = {
            "task_success": {"type": "bool", "required": True},
            "notes": {"type": "str", "required": "when_task_success"},
        }
        assert "empty or not a dict" in agent_mod._validate_response_schema({}, schema, "task")
        assert "Agent failure" in agent_mod._validate_response_schema(
            _llm_failure_envelope(),
            schema,
            "task",
        )
        assert "Missing required field" in agent_mod._validate_response_schema(
            {"agent_payload": {"task_success": True}},
            schema,
            "task",
        )

    def test_validates_grade_vectors(self) -> None:
        vectors = [{"name": "fit"}]
        assert "Missing vectors" in agent_mod._validate_grades([], vectors)
        assert "Unexpected vectors" in agent_mod._validate_grades(
            [{"vector": "fit", "grade": "A", "confidence": 2}, {"vector": "other", "grade": "A", "confidence": 2}],
            vectors,
        )
        allowed = sorted(ASTRAL_CONFIG.get("valid_grades", []))
        bad_grade = allowed[0] if allowed else "A"
        assert "Invalid grade" in agent_mod._validate_grades(
            [{"vector": "fit", "grade": "Z", "confidence": 2}],
            vectors,
        ) or agent_mod._validate_grades(
            [{"vector": "fit", "grade": bad_grade, "confidence": 0}],
            vectors,
        )


class TestAgentDataHelpers:
    def test_extracts_entity_segments_and_batch_cost(self, monkeypatch: pytest.MonkeyPatch) -> None:
        payload = json.dumps({"jobs": [{"astral_job_id": "job-1", "grades": []}]})
        assert agent_mod._extract_entity_segment(payload, "job-1") == json.dumps({"astral_job_id": "job-1", "grades": []})
        marker_body = agent_mod._extract_entity_segment("[job-1]\nsegment\n[job-2]\nother", "job-1")
        assert marker_body == "segment"
        assert agent_mod._failure_response_block_data("job-1", "body").startswith("[job-1]")
        assert agent_mod._audit_response_body(None, err="boom") == "boom"
        monkeypatch.setattr(agent_mod, "sum_cost_by_batch", lambda batch_ids: {"batch-1": 1.25})
        assert agent_mod.compute_batch_cost("batch-1") == 1.25

    def test_get_agent_data_filters_entity_segments(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [
            {"block_type": "TASK", "block_data": json.dumps({"jobs": [{"astral_job_id": "job-1", "x": 1}]})},
            {"block_type": "SYSTEM", "block_data": "system"},
        ]
        monkeypatch.setattr(agent_mod, "get_agent_data_by_batch", lambda batch_id, block_type: rows)
        filtered = agent_mod.get_agent_data("batch-1", entity_id="job-1")
        assert json.loads(filtered[0]["block_data"])["x"] == 1
        assert agent_mod.get_entity_response("batch-1", "job-1") is not None

    def test_preview_prompt_resolves_blocks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            agent_mod,
            "_resolve_task_prompts",
            lambda task_key: (
                {"content": "agent", "model_code": "claude"},
                {"user_prompt": "user", "cache_prompt": "cache", "nocache_prompt": "nocache"},
            ),
        )
        blocks = agent_mod.preview_prompt("qualify_job_listings", {"profile": {}})
        assert blocks["system"]
        assert blocks["user"]
        assert blocks["cache"] == "cache"


class TestResolveTaskPrompts:
    def test_returns_rows_when_configured(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(agent_mod, "get_agent_task", lambda task_key: {"agent_id": "agent-1"})
        monkeypatch.setattr(
            agent_mod,
            "get_agent",
            lambda agent_id: {"agent_id": agent_id, "model_code": "claude-haiku-4-5"},
        )
        agent_row, task_row = agent_mod._resolve_task_prompts("any_key")
        assert agent_row["model_code"] == "claude-haiku-4-5"
        assert task_row["agent_id"] == "agent-1"

    def test_raises_when_task_or_agent_rows_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(agent_mod, "get_agent_task", lambda task_key: None)
        with pytest.raises(ValueError, match="No agent_task row"):
            agent_mod._resolve_task_prompts("missing")
        monkeypatch.setattr(agent_mod, "get_agent_task", lambda task_key: {"agent_id": ""})
        with pytest.raises(ValueError, match="no agent_id"):
            agent_mod._resolve_task_prompts("task")
        monkeypatch.setattr(agent_mod, "get_agent_task", lambda task_key: {"agent_id": "agent-1"})
        monkeypatch.setattr(agent_mod, "get_agent", lambda agent_id: None)
        with pytest.raises(ValueError, match="not found"):
            agent_mod._resolve_task_prompts("task")


class TestChainContext:
    def test_merges_extra_chain_tokens(self) -> None:
        base = agent_mod._chain_context(
            {"content": "agent"},
            {},
            "qualify_job_listings",
            None,
            {"CALLER_RESPONSE": "hop"},
        )
        assert base["CALLER_RESPONSE"] == "hop"
        assert base["SELECTED_AGENT"] == "agent"

    def test_formats_non_json_caller_response(self) -> None:
        hop = agent_mod._chain_tokens_for_next_hop(
            system_content="",
            cache_content=None,
            nocache_content=None,
            live_content=None,
            parsed=42,
        )
        assert hop["CALLER_RESPONSE"] == "42"

    def test_caller_response_empty_when_parsed_none(self) -> None:
        hop = agent_mod._chain_tokens_for_next_hop(
            system_content="",
            cache_content=None,
            nocache_content=None,
            live_content=None,
            parsed=None,
        )
        assert hop["CALLER_RESPONSE"] == ""

    def test_legacy_chain_tokens_with_cache_content(self) -> None:
        """Test legacy ABI path with cache_content kwarg (AST-458 coverage)."""
        hop = agent_mod._chain_tokens_for_next_hop(
            parsed={"jobs": []},
            system_content="legacy_sys",
            cache_content="legacy_cache",
            nocache_content="legacy_nocache",
            live_content="legacy_live",
        )
        assert hop["CALLER_RESPONSE"] == '{"jobs": []}'
        assert hop["CACHE_BLOCK_A"] == "legacy_sys"
        assert hop["CACHE_BLOCK_B"] == "--- CACHED CONTEXT ---\nlegacy_cache"
        assert hop["CACHE_BLOCK_C"] == "--- ADDITIONAL CONTEXT ---\nlegacy_nocache"
        assert hop["CACHE_BLOCK_D"] == "--- CONTENT ---\nlegacy_live"

    def test_legacy_chain_tokens_system_content_none_handling(self) -> None:
        """Test legacy system_content coercion (str vs None) (AST-458 coverage)."""
        hop = agent_mod._chain_tokens_for_next_hop(
            parsed=42,
            system_content=None,
            cache_content="c",
        )
        assert hop["CALLER_RESPONSE"] == "42"
        assert hop["CACHE_BLOCK_A"] == ""

    def test_legacy_chain_tokens_empty_slots(self) -> None:
        """Test legacy path with empty/omitted slots (AST-458 coverage)."""
        hop = agent_mod._chain_tokens_for_next_hop(
            parsed="result",
            system_content="",
        )
        assert hop["CALLER_RESPONSE"] == "result"
        assert hop["CACHE_BLOCK_A"] == ""
        assert hop["CACHE_BLOCK_B"] == ""
        assert hop["CACHE_BLOCK_C"] == ""
        assert hop["CACHE_BLOCK_D"] == ""

    def test_legacy_chain_tokens_rejects_unknown_kwargs(self) -> None:
        """Test legacy path raises TypeError on unknown kwargs (AST-458 coverage)."""
        with pytest.raises(TypeError, match="unexpected keyword arguments"):
            agent_mod._chain_tokens_for_next_hop(
                parsed={},
                system_content="sys",
                unknown_param="bad",
            )


# Branches: resolved_agent_content; SELECTED_AGENT injection; direct vs template system paths (AST-631).
class TestAst631AgentContentTokens:
    _AGENT_BODY = "Hi, you're Grace. You're helping {$FIRST_NAME} find a great role."
    _PLAIN_BODY = "Hi, you're Grace. No tokens here."

    def _cd(self) -> dict:
        return {"profile": {"first": "Ada"}}

    def test_resolved_agent_content_substitutes_candidate_tokens(self) -> None:
        out = agent_mod.resolved_agent_content(
            {"content": self._AGENT_BODY},
            self._cd(),
            "qualify_job_listings",
        )
        assert "helping Ada find" in out
        assert "{$FIRST_NAME}" not in out

    def test_direct_system_block_resolves_first_name(self) -> None:
        agent_row = {"content": self._AGENT_BODY}
        task_row = {"system_prompt": ""}
        text = agent_mod.resolved_task_system(
            agent_row,
            task_row,
            self._cd(),
            "qualify_job_listings",
            {},
        )
        assert "helping Ada find" in text
        assert "{$FIRST_NAME}" not in text

    def test_selected_agent_path_resolves_agent_body_tokens(self) -> None:
        agent_row = {"content": self._AGENT_BODY}
        task_row = {"system_prompt": "{$SELECTED_AGENT}"}
        cc = agent_mod._chain_context(agent_row, self._cd(), "qualify_job_listings", None)
        text = agent_mod.resolved_task_system(
            agent_row,
            task_row,
            self._cd(),
            "qualify_job_listings",
            cc,
        )
        assert "helping Ada find" in text
        assert "{$FIRST_NAME}" not in text

    def test_plain_agent_body_unchanged_on_direct_and_selected_paths(self) -> None:
        agent_row = {"content": self._PLAIN_BODY}
        task_row_empty = {"system_prompt": ""}
        direct = agent_mod.resolved_task_system(
            agent_row,
            task_row_empty,
            self._cd(),
            "qualify_job_listings",
            {},
        )
        cc = agent_mod._chain_context(agent_row, self._cd(), "qualify_job_listings", None)
        via_selected = agent_mod.resolved_task_system(
            agent_row,
            {"system_prompt": "{$SELECTED_AGENT}"},
            self._cd(),
            "qualify_job_listings",
            cc,
        )
        assert direct == self._PLAIN_BODY
        assert via_selected == self._PLAIN_BODY

    def test_preview_prompt_selected_agent_path_matches_production(self, monkeypatch: pytest.MonkeyPatch) -> None:
        agent_row = {"content": self._AGENT_BODY, "model_code": "claude"}
        task_row = {
            "system_prompt": "{$SELECTED_AGENT}",
            "user_prompt": "user",
            "cache_prompt": "",
            "nocache_prompt": "",
        }
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: (agent_row, task_row))
        blocks = agent_mod.preview_prompt("qualify_job_listings", self._cd())
        assert "helping Ada find" in blocks["system"]
        assert "{$FIRST_NAME}" not in blocks["system"]


class TestLegacyAbiGuards:
    """Branch coverage: dual-path _chain_tokens / _store_prompt_blocks (AST-455 legacy + seven-segment)."""

    def test_chain_tokens_rejects_unknown_legacy_kwargs(self) -> None:
        with pytest.raises(TypeError, match="unexpected keyword"):
            agent_mod._chain_tokens_for_next_hop(parsed={}, bad_kw=1)

    def test_chain_tokens_coerces_non_str_system_segment(self) -> None:
        hop = agent_mod._chain_tokens_for_next_hop(
            parsed=None,
            system_content=123,
            cache_content="",
            nocache_content=None,
            live_content=None,
        )
        assert hop["CACHE_BLOCK_A"] == "123"

    def test_store_prompt_blocks_rejects_dual_cache_interfaces(self) -> None:
        with pytest.raises(TypeError, match="not both"):
            agent_mod._store_prompt_blocks(
                "job",
                "t",
                "b",
                "sys",
                caches_resolved_four=("a", None, None, None),
                cache_content="oops",
            )

    def test_store_prompt_blocks_requires_slot_args(self) -> None:
        with pytest.raises(TypeError, match="missing"):
            agent_mod._store_prompt_blocks("job", "t", "b", "sys")

    def test_store_seven_segment_optional_sections(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(agent_mod, "save_agent_data", lambda **kw: kw["agent_data_id"])
        mid = agent_mod._store_prompt_blocks(
            "job",
            "t",
            "b1",
            "sys",
            caches_resolved_four=("", "slotb", "", ""),
            nocache_content="nc",
            user_content="u",
            live_content="lv",
        )
        assert {b["type"] for b in mid} >= {"SYSTEM", "CACHE_B", "NO_CACHE", "TASK"}

    def test_simulated_chain_preview_invalid_json_keeps_fragment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            agent_mod,
            "_resolve_task_prompts",
            lambda _tk: (
                {"content": "agent {$TASK}", "model_code": "claude"},
                {
                    "system_prompt": "",
                    "user_prompt": "",
                    "cache_prompt": "",
                    "cache_prompt_b": "",
                    "cache_prompt_c": "",
                    "cache_prompt_d": "",
                },
            ),
        )
        monkeypatch.setattr(agent_mod, "resolved_task_system", lambda *a, **k: "")
        monkeypatch.setattr(agent_mod, "resolve_tokens", lambda *_a, **_k: "")
        hop = agent_mod.simulated_chain_context_for_preview(
            "craft_resume_base",
            {},
            simulate_parsed='{"truncated json',
        )
        assert hop["CALLER_RESPONSE"] == '{"truncated json'

    def test_store_seven_segment_live_without_nocache(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(agent_mod, "save_agent_data", lambda **kw: kw["agent_data_id"])
        mid = agent_mod._store_prompt_blocks(
            "job",
            "t",
            "b2",
            "sys",
            caches_resolved_four=("x", None, None, None),
            nocache_content=None,
            user_content="",
            live_content="lv",
        )
        assert {"SYSTEM", "CACHE_A", "NO_CACHE"} <= {b["type"] for b in mid}

    def test_store_seven_segment_task_without_live(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(agent_mod, "save_agent_data", lambda **kw: kw["agent_data_id"])
        mid = agent_mod._store_prompt_blocks(
            "job",
            "t",
            "b3",
            "sys",
            caches_resolved_four=("x", None, None, None),
            nocache_content=None,
            live_content=None,
            user_content="taskonly",
        )
        assert {"SYSTEM", "CACHE_A", "TASK"} <= {b["type"] for b in mid}

    def test_simulated_chain_non_json_string_skips_parse(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            agent_mod,
            "_resolve_task_prompts",
            lambda _tk: (
                {"content": "agent {$TASK}", "model_code": "claude"},
                {
                    "system_prompt": "",
                    "user_prompt": "",
                    "cache_prompt": "",
                    "cache_prompt_b": "",
                    "cache_prompt_c": "",
                    "cache_prompt_d": "",
                },
            ),
        )
        monkeypatch.setattr(agent_mod, "resolved_task_system", lambda *a, **k: "")
        monkeypatch.setattr(agent_mod, "resolve_tokens", lambda *_a, **_k: "")
        hop = agent_mod.simulated_chain_context_for_preview("craft_resume_base", {}, simulate_parsed="plain hop")
        assert hop["CALLER_RESPONSE"] == "plain hop"


class TestLegacyAbiGuards:
    """Branch coverage: dual-path _chain_tokens / _store_prompt_blocks (AST-455 legacy + seven-segment)."""

    def test_chain_tokens_rejects_unknown_legacy_kwargs(self) -> None:
        with pytest.raises(TypeError, match="unexpected keyword"):
            agent_mod._chain_tokens_for_next_hop(parsed={}, bad_kw=1)

    def test_chain_tokens_coerces_non_str_system_segment(self) -> None:
        hop = agent_mod._chain_tokens_for_next_hop(
            parsed=None,
            system_content=123,
            cache_content="",
            nocache_content=None,
            live_content=None,
        )
        assert hop["CACHE_BLOCK_A"] == "123"

    def test_store_prompt_blocks_rejects_dual_cache_interfaces(self) -> None:
        with pytest.raises(TypeError, match="not both"):
            agent_mod._store_prompt_blocks(
                "job",
                "t",
                "b",
                "sys",
                caches_resolved_four=("a", None, None, None),
                cache_content="oops",
            )

    def test_store_prompt_blocks_requires_slot_args(self) -> None:
        with pytest.raises(TypeError, match="missing"):
            agent_mod._store_prompt_blocks("job", "t", "b", "sys")

    def test_store_seven_segment_optional_sections(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(agent_mod, "save_agent_data", lambda **kw: kw["agent_data_id"])
        mid = agent_mod._store_prompt_blocks(
            "job",
            "t",
            "b1",
            "sys",
            caches_resolved_four=("", "slotb", "", ""),
            nocache_content="nc",
            user_content="u",
            live_content="lv",
        )
        assert {b["type"] for b in mid} >= {"SYSTEM", "CACHE_B", "NO_CACHE", "TASK"}

    def test_simulated_chain_preview_invalid_json_keeps_fragment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            agent_mod,
            "_resolve_task_prompts",
            lambda _tk: (
                {"content": "agent {$TASK}", "model_code": "claude"},
                {
                    "system_prompt": "",
                    "user_prompt": "",
                    "cache_prompt": "",
                    "cache_prompt_b": "",
                    "cache_prompt_c": "",
                    "cache_prompt_d": "",
                },
            ),
        )
        monkeypatch.setattr(agent_mod, "resolved_task_system", lambda *a, **k: "")
        monkeypatch.setattr(agent_mod, "resolve_tokens", lambda *_a, **_k: "")
        hop = agent_mod.simulated_chain_context_for_preview(
            "craft_resume_base",
            {},
            simulate_parsed='{"truncated json',
        )
        assert hop["CALLER_RESPONSE"] == '{"truncated json'

    def test_store_seven_segment_live_without_nocache(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(agent_mod, "save_agent_data", lambda **kw: kw["agent_data_id"])
        mid = agent_mod._store_prompt_blocks(
            "job",
            "t",
            "b2",
            "sys",
            caches_resolved_four=("x", None, None, None),
            nocache_content=None,
            user_content="",
            live_content="lv",
        )
        assert {"SYSTEM", "CACHE_A", "NO_CACHE"} <= {b["type"] for b in mid}

    def test_store_seven_segment_task_without_live(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(agent_mod, "save_agent_data", lambda **kw: kw["agent_data_id"])
        mid = agent_mod._store_prompt_blocks(
            "job",
            "t",
            "b3",
            "sys",
            caches_resolved_four=("x", None, None, None),
            nocache_content=None,
            live_content=None,
            user_content="taskonly",
        )
        assert {"SYSTEM", "CACHE_A", "TASK"} <= {b["type"] for b in mid}

    def test_simulated_chain_non_json_string_skips_parse(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            agent_mod,
            "_resolve_task_prompts",
            lambda _tk: (
                {"content": "agent {$TASK}", "model_code": "claude"},
                {
                    "system_prompt": "",
                    "user_prompt": "",
                    "cache_prompt": "",
                    "cache_prompt_b": "",
                    "cache_prompt_c": "",
                    "cache_prompt_d": "",
                },
            ),
        )
        monkeypatch.setattr(agent_mod, "resolved_task_system", lambda *a, **k: "")
        monkeypatch.setattr(agent_mod, "resolve_tokens", lambda *_a, **_k: "")
        hop = agent_mod.simulated_chain_context_for_preview("craft_resume_base", {}, simulate_parsed="plain hop")
        assert hop["CALLER_RESPONSE"] == "plain hop"


class TestStoreBlocks:
    def test_store_prompt_and_response_blocks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: List[Dict[str, Any]] = []
        monkeypatch.setattr(
            agent_mod,
            "save_agent_data",
            lambda **kwargs: saved.append(kwargs) or kwargs["agent_data_id"],
        )
        blocks = agent_mod._store_prompt_blocks(
            entity_type="job",
            task_key="evaluate_jd",
            batch_id="batch-1",
            system_content="system",
            cache_content="cache",
            nocache_content="nocache",
            user_content="task",
            live_content="live",
        )
        assert {block["type"] for block in blocks} == {"SYSTEM", "CACHE_A", "NO_CACHE", "TASK"}
        resp_id = agent_mod._store_response_block("job", "evaluate_jd", "batch-1", "ok", index="job-1")
        assert resp_id.startswith("batch-1-response-")
        assert any(row["block_type"] == "RESPONSE" for row in saved)

    def test_optional_cache_nocache_user_live_omitted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: List[Dict[str, Any]] = []
        monkeypatch.setattr(
            agent_mod,
            "save_agent_data",
            lambda **kwargs: saved.append(kwargs) or kwargs["agent_data_id"],
        )
        blocks = agent_mod._store_prompt_blocks(
            entity_type="job",
            task_key="evaluate_jd",
            batch_id="batch-1",
            system_content="system",
            cache_content=None,
            nocache_content=None,
            user_content="",
            live_content=None,
        )
        assert [b["type"] for b in blocks] == ["SYSTEM"]
        assert {row["block_type"] for row in saved} == {"SYSTEM"}

    def test_store_agent_response_skips_or_records(self, monkeypatch: pytest.MonkeyPatch) -> None:
        audit = MagicMock()
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", audit)
        cfg = TASK_CONFIG["evaluate_jd"]
        agent_mod._store_agent_response(cfg, "evaluate_jd", None, "raw", None, {"api_response": _api_response()})
        audit.assert_not_called()
        agent_mod._store_agent_response(
            cfg,
            "evaluate_jd",
            "job-1",
            "raw",
            {"jobs": []},
            {"api_response": _api_response(), "runtime_prompt": "prompt"},
        )
        audit.assert_called_once()

    def test_store_prompt_blocks_with_four_cache_slots(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test _store_prompt_blocks with caches_resolved_four (AST-458 coverage)."""
        saved: List[Dict[str, Any]] = []
        monkeypatch.setattr(
            agent_mod,
            "save_agent_data",
            lambda **kwargs: saved.append(kwargs) or kwargs["agent_data_id"],
        )
        blocks = agent_mod._store_prompt_blocks(
            entity_type="job",
            task_key="evaluate_jd",
            batch_id="batch-1",
            system_content="system",
            caches_resolved_four=("cache_a", "cache_b", "cache_c", "cache_d"),
            nocache_content="nocache",
            user_content="task",
            live_content="live",
        )
        types = [b["type"] for b in blocks]
        assert types == ["SYSTEM", "CACHE_A", "CACHE_B", "CACHE_C", "CACHE_D", "NO_CACHE", "NO_CACHE", "TASK"]

    def test_store_prompt_blocks_four_caches_with_empty_blobs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test _store_prompt_blocks skips empty/whitespace cache blobs (AST-458 coverage)."""
        saved: List[Dict[str, Any]] = []
        monkeypatch.setattr(
            agent_mod,
            "save_agent_data",
            lambda **kwargs: saved.append(kwargs) or kwargs["agent_data_id"],
        )
        blocks = agent_mod._store_prompt_blocks(
            entity_type="job",
            task_key="evaluate_jd",
            batch_id="batch-1",
            system_content="system",
            caches_resolved_four=("", "   ", "cache_c", None),
            nocache_content=None,
            user_content="",
            live_content=None,
        )
        types = [b["type"] for b in blocks]
        assert types == ["SYSTEM", "CACHE_C"]

    def test_store_prompt_blocks_requires_one_cache_api(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test error when both cache_content and caches_resolved_four passed (AST-458 coverage)."""
        monkeypatch.setattr(agent_mod, "save_agent_data", lambda **kwargs: kwargs["agent_data_id"])
        with pytest.raises(TypeError, match="pass caches_resolved_four or cache_content, not both"):
            agent_mod._store_prompt_blocks(
                entity_type="job",
                task_key="evaluate_jd",
                batch_id="batch-1",
                system_content="system",
                caches_resolved_four=("a", None, None, None),
                cache_content="should_not_pass",
                nocache_content=None,
                user_content="",
                live_content=None,
            )

    def test_store_prompt_blocks_legacy_cache_content_full_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test legacy cache_content path with all optional sections (lines 425-432 branches)."""
        saved: List[Dict[str, Any]] = []
        monkeypatch.setattr(
            agent_mod,
            "save_agent_data",
            lambda **kwargs: saved.append(kwargs) or kwargs["agent_data_id"],
        )
        blocks = agent_mod._store_prompt_blocks(
            entity_type="job",
            task_key="evaluate_jd",
            batch_id="batch-1",
            system_content="system",
            cache_content="legacy_cache",
            nocache_content="nocache_text",
            user_content="user_task",
            live_content="live_text",
        )
        types = [b["type"] for b in blocks]
        assert types == ["SYSTEM", "CACHE_A", "NO_CACHE", "NO_CACHE", "TASK"]
        block_names = [row["block_type"] for row in saved]
        assert "CACHE_A" in block_names

    def test_store_prompt_blocks_legacy_cache_content_empty_and_omitted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test legacy cache_content with empty cache and omitted optional sections (lines 425-432)."""
        saved: List[Dict[str, Any]] = []
        monkeypatch.setattr(
            agent_mod,
            "save_agent_data",
            lambda **kwargs: saved.append(kwargs) or kwargs["agent_data_id"],
        )
        blocks = agent_mod._store_prompt_blocks(
            entity_type="job",
            task_key="evaluate_jd",
            batch_id="batch-1",
            system_content="system",
            cache_content="",
            nocache_content=None,
            user_content="",
            live_content=None,
        )
        types = [b["type"] for b in blocks]
        assert types == ["SYSTEM"]

    def test_store_prompt_blocks_missing_both_cache_apis_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test error when neither cache_content nor caches_resolved_four passed (line 435-436)."""
        monkeypatch.setattr(agent_mod, "save_agent_data", lambda **kwargs: kwargs["agent_data_id"])
        with pytest.raises(TypeError, match="missing caches_resolved_four or cache_content"):
            agent_mod._store_prompt_blocks(
                entity_type="job",
                task_key="evaluate_jd",
                batch_id="batch-1",
                system_content="system",
                nocache_content=None,
                user_content="",
                live_content=None,
            )


class TestDoTask:
    async def test_rejects_unknown_or_misconfigured_tasks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        with pytest.raises(ValueError, match="Unknown task_key"):
            await agent_mod.do_task("missing_task")
        monkeypatch.setitem(agent_mod.TASK_CONFIG, "broken", {"entity_type": "job"})
        with pytest.raises(ValueError, match="missing required response_schema"):
            await agent_mod.do_task("broken")
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: ({"agent_id": "a"}, {"agent_id": "a"}))
        with pytest.raises(ValueError, match="no brain_setting"):
            await agent_mod.do_task("evaluate_jd")

    async def test_returns_api_failure_and_stores_audit(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(return_value={"success": False, "error": "api down", "api_response": _api_response("fail")}),
        )
        out = await agent_mod.do_task("evaluate_jd", index="job-1", ctx=_draft_job_resume_ctx())
        assert out["success"] is False
        assert stub_agent_storage["save"].called
        stub_agent_storage["audit"].assert_called_once()

    async def test_do_task_stores_agent_data_for_craft_null_entity_type(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        agent_prompt_rows: Tuple[Dict[str, Any], Dict[str, Any]],
        stub_agent_storage: Dict[str, MagicMock],
    ) -> None:
        """Phase B craft tasks use entity_type None in TASK_CONFIG; prompts still persist."""
        monkeypatch.setattr(agent_mod, "get_active_llm_provider", lambda: "anthropic")
        monkeypatch.setattr(agent_mod, "send_to_deepseek", AsyncMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"search_terms": "line one\nline two"},
                    "api_response": _api_response('{"search_terms":"line one\\nline two"}'),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "craft_company_search_terms",
            index="somerset",
            ctx={"candidate_data": {"astral_candidate_id": "somerset"}},
        )
        assert out["success"] is True
        assert stub_agent_storage["save"].call_count >= 1
        first_save = stub_agent_storage["save"].call_args_list[0][1]
        assert first_save["entity_type"] == "candidate"
        assert first_save["batch_id"] == "batch-1"

    async def test_rejects_json_schema_and_confidence_failures(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        send = AsyncMock(
            return_value={
                "success": True,
                "parsed_response": _llm_failure_envelope(),
                "api_response": _api_response(),
                "timesheet": {},
            }
        )
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)
        out = await agent_mod.do_task("evaluate_jd", index="job-1", ctx=_draft_job_resume_ctx())
        assert out["success"] is False
        assert "empty agent_payload" in out["error"]

        send.return_value = {
            "success": True,
            "parsed_response": {
                "agent_payload": {
                    "grades": [{"vector": "MISSION", "grade": "A", "confidence": 0, "reason": "x"}],
                }
            },
            "api_response": _api_response(),
            "timesheet": {},
        }
        out = await agent_mod.do_task(
            "draft_job_resume",
            index="job-1",
            ctx=_draft_job_resume_ctx(),
        )
        assert out["success"] is False
        assert "grades" in out["error"]

    async def test_rejects_grade_vector_mismatch(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "agent_payload": {
                            "grades": [{"vector": "MISSION", "grade": "A", "confidence": 2, "reason": "x"}],
                        }
                    },
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task("draft_job_resume", index="job-1", ctx=_draft_job_resume_ctx())
        assert out["success"] is False
        assert "grades" in out["error"]

    async def test_decodes_encoded_payload_and_stores_success(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
        enable_debug_log: None,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": ["0|CRA2"]},
                    "api_response": _api_response("encoded"),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_size": 2, "batch_entities": _batch_entities("job-1")},
        )
        assert out["success"] is True
        assert out["parsed_response"]["jobs"][0]["astral_job_id"] == "job-1"
        assert out["agent_ref"]["entity_cost"] == 0.5
        stub_agent_storage["append"].assert_called_once()

    @pytest.mark.asyncio
    async def test_decodes_top_level_json_string_encoded_payload(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        """DeepSeek may return agent_payload as a string inside the envelope object."""
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_deepseek",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_performance": {}, "agent_payload": "000|DTA5|GCA4"},
                    "api_response": _api_response("encoded"),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "send_to_anthropic", AsyncMock())
        monkeypatch.setattr(agent_mod, "get_active_llm_provider", lambda: "deepseek")
        monkeypatch.setattr(
            agent_mod,
            "resolve_brain_setting_to_deepseek_tier_meta",
            lambda _bs: {"vendor_model": "deepseek-v4-flash", "thinking": False},
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={
                "candidate_data": {},
                "batch_entities": _batch_entities("job-1"),
                "vector_labels": {"DT": "Domain & Technology Fit", "GC": "Gut Check"},
            },
        )
        assert out["success"] is True
        assert out["parsed_response"]["jobs"][0]["grades"][0]["grade"] == "A"

    async def test_ast501_rejects_evaluate_jd_when_api_returns_bare_encoded_lines_without_envelope(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
    ) -> None:
        """Qualify/evaluate batch consult must use the outer JSON envelope — no bare compact lines."""
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(agent_mod, "get_active_llm_provider", lambda: "anthropic")
        monkeypatch.setattr(agent_mod, "send_to_deepseek", AsyncMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    # Two lines — still invalid without agent_performance / agent_payload envelope.
                    "parsed_response": "000|CRA2\n001|CRA3",
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1", "job-2")},
        )
        assert out["success"] is False
        assert "bare text" in (out["error"] or "").lower()

    async def test_ast501_rejects_evaluate_jd_when_agent_payload_is_structured_json_object(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "agent_performance": {},
                        "agent_payload": {"grades": [{"vector": "FT", "grade": "A", "confidence": 2}]},
                    },
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
        )
        assert out["success"] is False
        err = (out["error"] or "").lower()
        assert "newline-separated" in err or "encoded string" in err

    async def test_ast503_rejects_grade_do_when_api_returns_bare_encoded_lines_without_envelope(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
    ) -> None:
        """DO scored batch (grade_* agent_task) rejects bare compact lines — same envelope contract as AST-501."""
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(agent_mod, "get_active_llm_provider", lambda: "anthropic")
        monkeypatch.setattr(agent_mod, "send_to_deepseek", AsyncMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": "000|FTA2\n001|MBB2",
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "grade_do",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1", "job-2")},
        )
        assert out["success"] is False
        assert "bare text" in (out["error"] or "").lower()

    async def test_ast503_rejects_grade_do_when_agent_payload_is_structured_json_object(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "agent_performance": {},
                        "agent_payload": {"0": [{"vector": "FT", "grade": "A", "confidence": 2}]},
                    },
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "grade_do",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
        )
        assert out["success"] is False
        err = (out["error"] or "").lower()
        assert "newline-separated" in err or "encoded string" in err

    async def test_returns_decode_and_post_decode_validation_errors(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
        enable_debug_log: None,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        send = AsyncMock(
            return_value={
                "success": True,
                "parsed_response": _llm_failure_envelope(),
                "api_response": _api_response(),
                "timesheet": {},
            }
        )
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert out["success"] is False
        assert "empty agent_payload" in out["error"]

        send.return_value = {
            "success": True,
            "parsed_response": {"agent_payload": "0|CRX2"},
            "api_response": _api_response(),
            "timesheet": {},
        }
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert out["success"] is False
        assert "confidence digit 0" in out["error"]

    async def test_chains_run_next_when_configured(self, monkeypatch: pytest.MonkeyPatch, batch_token: Any) -> None:
        def resolve(task_key: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
            if task_key == "qualify_job_listings":
                return _agent_rows(run_next="evaluate_jd")
            return _agent_rows(run_next="")

        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", resolve)
        _patch_strict_batch_anthropic(monkeypatch)
        send = AsyncMock(
            side_effect=[
                _strict_batch_llm_ok(api_label="first"),
                _strict_batch_llm_ok(api_label="second"),
            ]
        )
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task(
            "qualify_job_listings",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
        )
        assert out["success"] is True
        assert send.await_count == 2

    @pytest.mark.asyncio
    async def test_chain_entry_log(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        caplog.set_level("INFO")
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
        )
        assert any("run_next chain entry" in rec.message and "task=evaluate_jd" in rec.message for rec in caplog.records)

    @pytest.mark.asyncio
    async def test_hop_boundary_log_on_run_next(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        caplog.set_level("INFO")

        def resolve(task_key: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
            if task_key == "qualify_job_listings":
                return _agent_rows(run_next="evaluate_jd")
            return _agent_rows(run_next="")

        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", resolve)
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                side_effect=[
                    _strict_batch_llm_ok(api_label="first"),
                    _strict_batch_llm_ok(api_label="second"),
                ]
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        await agent_mod.do_task(
            "qualify_job_listings",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
        )
        assert any(
            "run_next hop:" in rec.message
            and "qualify_job_listings -> evaluate_jd" in rec.message
            and "caller_keys=" in rec.message
            and "CALLER_RESPONSE=populated(len=" in rec.message
            for rec in caplog.records
        )

    @pytest.mark.asyncio
    async def test_mid_chain_empty_caller_skips_api(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        agent_row, child_row = _agent_rows()
        child_row["system_prompt"] = "sys {$CALLER_SYSTEM}"
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: (agent_row, child_row))
        send = AsyncMock()
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())

        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
            chain_context={
                "CALLER_SYSTEM": "",
                "CALLER_RESPONSE": "x",
                "_hop_parent_task_key": "anticipate_scan",
            },
        )
        assert out["success"] is False
        assert "CALLER_SYSTEM" in (out.get("error") or "")
        send.assert_not_called()

    @pytest.mark.asyncio
    async def test_debug_flag_passed_to_child(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        inner_debug: List[bool] = []
        orig_do_task = agent_mod.do_task

        async def tracking_do_task(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            if args and args[0] == "evaluate_jd":
                inner_debug.append(kwargs.get("debug") is True)
            return await orig_do_task(*args, **kwargs)

        def resolve(task_key: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
            if task_key == "qualify_job_listings":
                return _agent_rows(run_next="evaluate_jd")
            return _agent_rows(run_next="")

        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", resolve)
        monkeypatch.setattr(agent_mod, "do_task", tracking_do_task)
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                side_effect=[
                    _strict_batch_llm_ok(api_label="first"),
                    _strict_batch_llm_ok(api_label="second"),
                ]
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        await agent_mod.do_task(
            "qualify_job_listings",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
            debug=True,
        )
        assert inner_debug == [True]

    async def test_ignores_invalid_run_next(self, monkeypatch: pytest.MonkeyPatch, batch_token: Any) -> None:
        rows = _agent_rows(run_next="missing_task")
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: rows)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2|co|title|link"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task(
            "qualify_job_listings",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
        )
        assert out["success"] is True


# brain_setting → Anthropic SKU + send_to_anthropic, or DeepSeek tier_meta + send_to_deepseek (AST-492 + AST-493).
class TestAst492BrainSettingDoTask:
    @pytest.mark.asyncio
    async def test_send_to_anthropic_receives_resolved_key_for_big_tier(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
    ) -> None:
        monkeypatch.setattr(agent_mod, "get_active_llm_provider", lambda: "anthropic")
        monkeypatch.setattr(agent_mod, "send_to_deepseek", AsyncMock())
        monkeypatch.setattr(
            agent_mod,
            "_resolve_task_prompts",
            lambda task_key: _agent_rows(brain_setting="Big"),
        )
        send = AsyncMock(
            return_value={
                "success": True,
                "parsed_response": {"agent_payload": "0|CRA2"},
                "api_response": _api_response(),
                "timesheet": {},
            }
        )
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
        )
        assert out["success"] is True
        assert send.await_args is not None
        assert send.await_args.kwargs.get("model_code") == "claude-opus-4-6"

    @pytest.mark.asyncio
    async def test_send_to_deepseek_receives_vendor_model_and_tier_meta(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        tier_meta = cfg.resolve_brain_setting_to_deepseek_tier_meta(cfg.BRAIN_LITTLE)
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(agent_mod, "get_active_llm_provider", lambda: "deepseek")
        send_anth = AsyncMock()
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send_anth)
        send_ds = AsyncMock(
            return_value={
                "success": True,
                "parsed_response": {"agent_payload": "0|CRA2"},
                "api_response": _api_response(),
                "timesheet": {},
            }
        )
        monkeypatch.setattr(agent_mod, "send_to_deepseek", send_ds)
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
        )
        assert out["success"] is True
        send_anth.assert_not_called()
        assert send_ds.await_args is not None
        kwa = send_ds.await_args.kwargs
        assert kwa.get("vendor_model") == tier_meta["vendor_model"]
        assert kwa.get("tier_meta") == tier_meta

    @pytest.mark.asyncio
    async def test_do_task_deepseek_raises_when_vendor_model_not_in_pricing(self, monkeypatch: pytest.MonkeyPatch, batch_token: Any) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(agent_mod, "get_active_llm_provider", lambda: "deepseek")
        monkeypatch.setattr(
            agent_mod,
            "resolve_brain_setting_to_deepseek_tier_meta",
            lambda _bs: {"vendor_model": "unknown-vendor-model", "thinking": False},
        )
        with pytest.raises(ValueError, match="Unknown DeepSeek vendor_model"):
            await agent_mod.do_task(
                "evaluate_jd",
                index="job-1",
                ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
            )

    @pytest.mark.asyncio
    async def test_do_task_raises_on_unknown_llm_provider(self, monkeypatch: pytest.MonkeyPatch, batch_token: Any) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(agent_mod, "get_active_llm_provider", lambda: "__no_such_vendor__")
        with pytest.raises(ValueError, match="Unknown LLM active_provider"):
            await agent_mod.do_task(
                "evaluate_jd",
                index="job-1",
                ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
            )


class TestAst469ResolveRunNextLive:
    """AST-461 / AST-469: tuple from resolve_run_next_live seeds JOB_LIST_VISIBLE for parse_job_list."""

    @pytest.mark.asyncio
    async def test_chain_passes_JOB_LIST_VISIBLE_into_parse_resolve_tokens(
        self,
        monkeypatch: pytest.MonkeyPatch,
        stub_agent_storage: Dict[str, MagicMock],
    ) -> None:

        def resolve_prompt(task_key: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
            if task_key == "select_job_page":
                return _agent_rows(run_next="parse_job_list")
            return _agent_rows(run_next="")

        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", resolve_prompt)

        captured: Dict[str, Any] = {}

        def capture_resolve_tokens(
            prompt: str,
            cd: Any,
            tk: str,
            cc: Any,
            job_context: Any = None,
            **kwargs: Any,
        ) -> str:
            if tk == "parse_job_list" and isinstance(cc, dict):
                captured["JOB_LIST_VISIBLE"] = cc.get("JOB_LIST_VISIBLE")
                captured["calls"] = captured.get("calls", 0) + 1
            return resolve_tokens(prompt, cd, tk, cc, job_context, **kwargs)

        monkeypatch.setattr(agent_mod, "resolve_tokens", capture_resolve_tokens)

        send = AsyncMock(
            side_effect=[
                {
                    "success": True,
                    "parsed_response": {
                        "selected_page": 1,
                        "response_type": "JOBLIST_TITLES",
                        "job_titles": ["Engineer"],
                    },
                    "api_response": _api_response("sel"),
                    "timesheet": {},
                },
                {
                    "success": True,
                    "parsed_response": {
                        "job_container": "motion",
                        "job_tag": "a",
                        "job_ids": ["jr-1"],
                    },
                    "api_response": _api_response("parse"),
                    "timesheet": {},
                },
            ]
        )
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)

        def resolver(_parsed: Dict[str, Any]) -> Tuple[str, str]:
            return (
                "<motion class='jobs'><a>Engineer role</a></motion>",
                "Role listing plain text",
            )

        out = await agent_mod.do_task(
            "select_job_page",
            live_content="<root> enumerated parent </root>",
            index="co-ast469",
            ctx={
                "candidate_data": {"k": "stub"},
                "resolve_run_next_live": resolver,
            },
            store_agent_data=False,
        )

        assert out["success"] is True
        assert out.get("run_next_parent_parsed", {}).get("response_type") == "JOBLIST_TITLES"
        assert send.await_count == 2
        assert captured.get("JOB_LIST_VISIBLE") == "Role listing plain text"


class TestAst692JobsiteScrapeIssueAgent:
    """AST-692: agent suppresses parse_job_list when select_job_page returns JOBSITE_SCRAPE_ISSUE."""

    @pytest.mark.asyncio
    async def test_select_job_page_suppresses_parse_chain_for_jobsite_scrape_issue(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        def resolve_prompt(task_key: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
            if task_key == "select_job_page":
                return _agent_rows(run_next="parse_job_list")
            return _agent_rows(run_next="")

        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", resolve_prompt)
        send = AsyncMock(
            return_value={
                "success": True,
                "parsed_response": {
                    "response_type": "JOBSITE_SCRAPE_ISSUE",
                    "selected_page": 1,
                    "scrape_issue_summary": "shell only",
                },
                "api_response": _api_response("sel"),
                "timesheet": {},
            }
        )
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)

        out = await agent_mod.do_task(
            "select_job_page",
            live_content="<root>shell page</root>",
            index="co-692",
            ctx={"candidate_data": {}, "resolve_run_next_live": lambda _p: ("<div/>", "visible")},
            store_agent_data=False,
        )

        assert out["success"] is True
        assert out.get("parsed_response", {}).get("response_type") == "JOBSITE_SCRAPE_ISSUE"
        assert send.await_count == 1


class TestAst834SelectJobPageEmptyRunNext:
    """AST-834: catalog-empty run_next must not chain parse without resolve_run_next_live."""

    @pytest.mark.asyncio
    async def test_jblist_titles_single_hop_when_run_next_empty(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            agent_mod,
            "_resolve_task_prompts",
            lambda task_key: _agent_rows(run_next=""),
        )
        send = AsyncMock(
            return_value={
                "success": True,
                "parsed_response": {
                    "response_type": "JOBLIST_TITLES",
                    "selected_page": 1,
                    "job_titles": ["Engineer"],
                },
                "api_response": _api_response("sel"),
                "timesheet": {},
            }
        )
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)

        out = await agent_mod.do_task(
            "select_job_page",
            live_content="<root> enumerated parent </root>",
            index="co-ast834",
            ctx={"candidate_data": {}},
            store_agent_data=False,
        )

        assert out["success"] is True
        assert send.await_count == 1


class TestRunAdhoc:
    async def test_requires_model_code(self) -> None:
        with pytest.raises(ValueError, match="requires model_code"):
            await agent_mod.run_adhoc("system", "user")

    async def test_with_tier_meta_sends_via_deepseek(self, monkeypatch: pytest.MonkeyPatch) -> None:
        send_deep = AsyncMock(return_value={"success": True, "parsed_response": "ds-ok"})
        send_anth = AsyncMock()
        monkeypatch.setattr(agent_mod, "send_to_deepseek", send_deep)
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send_anth)
        out = await agent_mod.run_adhoc(
            "sys",
            "usr",
            model_code="deepseek-v4-flash",
            tier_meta={"thinking": False, "vendor_model": "deepseek-v4-flash"},
        )
        assert out["parsed_response"] == "ds-ok"
        send_deep.assert_awaited()
        send_anth.assert_not_called()

    async def test_returns_runtime_prompt(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(return_value={"success": True, "parsed_response": "ok"}),
        )
        out = await agent_mod.run_adhoc(
            "system",
            "user",
            cache_content="cache",
            nocache_content="nocache",
            live_content="live",
            model_code="claude-haiku-4-5",
        )
        assert out["runtime_prompt"]


class TestResponseSchemaBranches:
    def test_skips_non_dict_field_specs_and_nested_item_errors(self) -> None:
        schema = {
            "ignore_me": "not_a_spec",
            "jobs": {
                "type": "list",
                "required": True,
                "items_schema": {"id": {"type": "str", "required": True}},
            },
        }
        assert "jobs[0]" in agent_mod._validate_response_schema({"agent_payload": {"jobs": [{"id": None}]}}, schema, "t")

    def test_covers_failure_and_type_branches(self) -> None:
        schema = {
            "flag": {"type": "bool", "required": True},
            "label": {"type": "str", "required": True},
            "count": {"type": "int", "required": True},
            "items": {
                "type": "list",
                "required": True,
                "items_schema": {"name": {"type": "str", "required": True}},
            },
            "meta": {"type": "dict", "required": True},
            "mode": {"type": "str", "required": True, "enum": ["a"]},
            "optional": {"type": "str", "required": "when_task_success"},
        }
        assert "status=failure" in agent_mod._validate_response_schema(
            {"agent_performance": {"status": "failure"}},
            schema,
            "task",
        )
        assert "missing 'agent_payload'" in agent_mod._validate_response_schema(
            {"agent_performance": "ok"},
            schema,
            "task",
        )
        assert agent_mod._validate_response_schema({"agent_payload": "plain"}, schema, "task") is None
        payload = {
            "task_success": True,
            "flag": True,
            "label": "x",
            "count": 1,
            "items": [{"name": "one"}],
            "meta": {},
            "mode": "a",
            "optional": "ok",
        }
        assert agent_mod._validate_response_schema({"agent_payload": payload}, schema, "task") is None
        assert "must be bool" in agent_mod._validate_response_schema({"agent_payload": {**payload, "flag": "n"}}, schema, "task")
        assert "must be str" in agent_mod._validate_response_schema({"agent_payload": {**payload, "label": 1}}, schema, "task")
        assert "must be int" in agent_mod._validate_response_schema({"agent_payload": {**payload, "count": "1"}}, schema, "task")
        assert "must be list" in agent_mod._validate_response_schema({"agent_payload": {**payload, "items": {}}}, schema, "task")
        assert "must be dict" in agent_mod._validate_response_schema({"agent_payload": {**payload, "meta": []}}, schema, "task")
        assert "must be one of" in agent_mod._validate_response_schema({"agent_payload": {**payload, "mode": "b"}}, schema, "task")
        assert "items[0] must be object" in agent_mod._validate_response_schema(
            {"agent_payload": {**payload, "items": ["bad"]}},
            schema,
            "task",
        )

    def test_coerce_schema_str_list_to_newlines_before_validate(self) -> None:
        schema = {"search_terms": {"type": "str", "required": True}}
        parsed = {"agent_payload": {"search_terms": [" site:linkedin.com foo ", "bar"]}}
        agent_mod._coerce_schema_str_fields_from_list(parsed, schema)
        assert parsed["agent_payload"]["search_terms"] == "site:linkedin.com foo\nbar"
        assert agent_mod._validate_response_schema(parsed, schema, "craft_company_search_terms") is None

    def test_ast676_int_bounds_and_bool_rejection(self) -> None:
        schema = {"importance": {"type": "int", "required": True, "min": 1, "max": 10}}
        ok = {"agent_payload": {"importance": 5}}
        assert agent_mod._validate_response_schema(ok, schema, "task") is None
        missing = agent_mod._validate_response_schema({"agent_payload": {}}, schema, "task")
        assert missing is not None and "Missing required field 'importance'" in missing
        assert "must be int, got bool" in agent_mod._validate_response_schema(
            {"agent_payload": {"importance": True}}, schema, "task"
        )
        assert "must be >= 1" in agent_mod._validate_response_schema(
            {"agent_payload": {"importance": 0}}, schema, "task"
        )
        assert "must be <= 10" in agent_mod._validate_response_schema(
            {"agent_payload": {"importance": 11}}, schema, "task"
        )

    def test_ast676_craft_rubric_criteria_schema(self) -> None:
        schema = TASK_CONFIG["craft_prefilter_rubric"]["response_schema"]
        ok = {
            "agent_payload": {
                "criteria": [{"label": "L", "content": "c", "importance": 5}],
            },
        }
        assert agent_mod._validate_response_schema(ok, schema, "craft_prefilter_rubric") is None
        bad = {
            "agent_payload": {
                "criteria": [{"label": "L", "content": "c"}],
            },
        }
        err = agent_mod._validate_response_schema(bad, schema, "craft_prefilter_rubric")
        assert err is not None and "criteria[0]" in err

    def test_effective_entity_type_defaults_candidate_for_craft(self) -> None:
        tc = TASK_CONFIG["craft_company_search_terms"]
        assert agent_mod._effective_entity_type(tc, "somerset") == "candidate"
        assert agent_mod._effective_entity_type(tc, None) == ""
        assert agent_mod._effective_entity_type({"entity_type": "job"}, "job-1") == "job"


class TestValidateGradesSuccess:
    def test_returns_none_when_all_vectors_and_confidence_ok(self) -> None:
        vectors = [{"name": "MISSION"}, {"name": "GUT"}]
        grades = [
            {"vector": "MISSION", "grade": "A", "confidence": 2},
            {"vector": "GUT", "grade": "B", "confidence": 3},
        ]
        assert agent_mod._validate_grades(grades, vectors) is None


class TestDecodeAndAuditBranches:
    def test_skips_non_dict_payload_rows_and_invalid_confidence(self) -> None:
        assert agent_mod._validate_grade_confidence_in_payload("bad", "task") is None
        payload = {"jobs": ["bad", {"grades": [{"grade": "A", "confidence": 2, "vector": "fit"}]}]}
        assert agent_mod._validate_grade_confidence_in_payload(payload, "task") is None
        ctx = {"batch_entities": _batch_entities("job-1")}
        with pytest.raises(ValueError, match="confidence 1-5"):
            agent_mod._decode_payload("task", "grades", "0|CRA0", ctx)

    def test_audit_and_failure_block_helpers(self) -> None:
        assert agent_mod._audit_response_body("raw") == "raw"
        assert agent_mod._audit_response_body(None, parsed={"ok": True}) == '{"ok": true}'
        assert agent_mod._audit_response_body(None, parsed=42) == "42"
        assert agent_mod._failure_response_block_data(None, "body") == "body"


class TestAssembleBlocks:
    def test_builds_cached_and_minimal_blocks(self) -> None:
        system_blocks, user_blocks, runtime, prompt_tokens, live_tokens = agent_mod._assemble_blocks(
            system_content="system",
            user_content="user",
            cache_content=None,
            nocache_content=None,
            live_content=None,
            model_code="claude-haiku-4-5",
            skip_cache=False,
        )
        assert system_blocks[0]["cache_control"]["type"] == "ephemeral"
        assert len(user_blocks) == 1
        assert prompt_tokens >= 0
        assert live_tokens == 0
        assert runtime[0]["system_prompt"]["cache"] is True


# Branches: resolved_task_system uses agent content when system_prompt empty; _build_context KeyError replace
class TestPromptEdgeCases:
    def test_resolved_task_system_falls_back_to_agent_content(self) -> None:
        agent_row = {"content": "fallback {$TASK}", "model_code": "claude"}
        task_row = {"system_prompt": "", "user_prompt": ""}
        cd = {"profile": {"first": "Ada"}}
        text = agent_mod.resolved_task_system(agent_row, task_row, cd, "qualify_job_listings", {})
        assert "fallback" in text

    def test_whitespace_system_prompt_falls_back(self) -> None:
        agent_row = {"content": "agent {$TASK}"}
        task_row = {"system_prompt": "   "}
        assert "agent" in agent_mod.resolved_task_system(agent_row, task_row, {}, "task", None)

    def test_build_context_no_placeholder_or_keyerror_replace(self) -> None:
        assert agent_mod._build_context("mytask", {"context_format": "static"}, "ent-1") == "mytask"
        weird = agent_mod._build_context(
            "mytask",
            {"context_format": "pre_{index}_post_{missing}"},
            "ent-1",
        )
        assert weird == "pre_ent-1_post_{missing}"
        assert (
            agent_mod._build_context("task", {"context_format": "task_{index}_{missing}"}, "job-1")
            == "task_job-1_{missing}"
        )


class TestAgentDataAccess:
    def test_get_agent_data_without_entity_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [{"block_type": "SYSTEM", "block_data": "system"}]
        monkeypatch.setattr(agent_mod, "get_agent_data_by_batch", lambda batch_id, block_type: rows)
        assert agent_mod.get_agent_data("batch-1") == rows

    def test_get_entity_response_fallbacks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(agent_mod, "get_agent_data_by_batch", lambda batch_id, block_type: [])
        assert agent_mod.get_entity_response("batch-1", "job-1") is None
        rows = [{"block_data": "full"}]
        monkeypatch.setattr(agent_mod, "get_agent_data_by_batch", lambda batch_id, block_type: rows)
        assert agent_mod.get_entity_response("batch-1", "job-1")["block_data"] == "full"

    def test_extract_entity_segment_flat_json(self) -> None:
        payload = json.dumps({"astral_job_id": "job-1", "grades": []})
        assert agent_mod._extract_entity_segment(payload, "job-1") == payload
        assert agent_mod._extract_entity_segment("no marker", "job-1") is None

    def test_extract_entity_segment_results_entities_and_empty_id(self) -> None:
        assert agent_mod._extract_entity_segment("x", "") is None
        via_results = json.dumps({"results": [{"astral_job_id": "job-1", "k": 1}]})
        assert '"job-1"' in (agent_mod._extract_entity_segment(via_results, "job-1") or "")
        via_entities = json.dumps({"entities": [{"astral_job_id": "job-2"}]})
        assert "job-2" in (agent_mod._extract_entity_segment(via_entities, "job-2") or "")
        blob = json.dumps({"other": 1})
        assert agent_mod._extract_entity_segment(blob, "nope") == blob

    def test_get_agent_data_keeps_row_when_segment_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        raw = json.dumps({"jobs": [{"astral_job_id": "other"}]})
        rows = [{"block_type": "TASK", "block_data": raw}]
        monkeypatch.setattr(agent_mod, "get_agent_data_by_batch", lambda batch_id, block_type: rows)
        out = agent_mod.get_agent_data("batch-1", entity_id="job-1")
        assert out[0]["block_data"] == raw


class TestDoTaskStorageFailures:
    async def test_swallows_storage_failures_on_success_and_failure(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock(side_effect=RuntimeError("db")))
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock(side_effect=RuntimeError("db")))
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock(side_effect=RuntimeError("db")))
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
            debug=True,
        )
        assert out["success"] is True

        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(return_value={"success": False, "error": "api down"}),
        )
        out = await agent_mod.do_task("evaluate_jd", index="job-1", ctx=_draft_job_resume_ctx())
        assert out["success"] is False

    async def test_post_decode_schema_and_confidence_failures(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        send = AsyncMock(
            return_value={
                "success": True,
                "parsed_response": {"agent_payload": "0|CRA2"},
                "api_response": _api_response(),
                "timesheet": {},
            }
        )
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        with monkeypatch.context() as patch:
            patch.setattr(
                agent_mod,
                "_validate_response_schema",
                lambda parsed, schema, task_key: "schema failed",
            )
            out = await agent_mod.do_task(
                "evaluate_jd",
                index="job-1",
                ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
            )
            assert out["error"] == "schema failed"

        send.return_value = {
            "success": True,
            "parsed_response": {"agent_payload": "0|CRA2"},
            "api_response": _api_response(),
            "timesheet": {},
        }
        with monkeypatch.context() as patch:
            patch.setattr(
                agent_mod,
                "_validate_grade_confidence_in_payload",
                lambda parsed, task_key: "confidence failed",
            )
            out = await agent_mod.do_task(
                "evaluate_jd",
                index="job-1",
                ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
            )
            assert out["error"] == "confidence failed"


class TestDoTaskRemainingPaths:
    async def test_warns_when_candidate_data_missing(
        self,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        caplog.set_level("WARNING")
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"batch_entities": _batch_entities("job-1")},
        )
        assert "requires_candidate_key" in caplog.text

    async def test_stores_plain_text_task_response(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response("body"),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(agent_mod, "compute_batch_cost", lambda batch_id: 1.0)
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {"profile": {}}, "batch_size": 1, "batch_entities": _batch_entities("job-1")},
        )
        assert out["success"] is True
        assert out["agent_ref"]["entity_cost"] == 1.0

    async def test_validation_failures_swallow_response_store_errors(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "agent_payload": {
                            "bogus_section": "x",
                        }
                    },
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock(side_effect=RuntimeError("db")))
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task("draft_job_resume", index="job-1", ctx=_draft_job_resume_ctx())
        assert out["success"] is False

    async def test_decode_failure_appends_payload_snippet(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        enable_debug_log: None,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "agent_performance": "ok",
                        "agent_payload": "bad|CRA2",
                    },
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        saved: List[str] = []

        def _save(**kwargs: Any) -> str:
            saved.append(kwargs["block_data"])
            return kwargs["agent_data_id"]

        monkeypatch.setattr(agent_mod, "save_agent_data", _save)
        _patch_normalize_rubric_response(
            monkeypatch,
            lambda task_key, task_config, parsed, ctx: (_ for _ in ()).throw(ValueError("boom")),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert out["success"] is False
        assert any("bad|CRA2" in body or "agent_payload" in body for body in saved)


class TestPromptAndSchemaEdges:
    def test_resolved_system_and_context_fallbacks(self) -> None:
        agent_row = {"content": "agent {$TASK}"}
        task_row = {"system_prompt": "   "}
        assert "agent" in agent_mod.resolved_task_system(agent_row, task_row, {}, "task", None)
        cfg = {"context_format": "task_{index}_{missing}"}
        assert agent_mod._build_context("task", cfg, "job-1") == "task_job-1_{missing}"

    def test_validate_grades_accepts_matching_vectors(self) -> None:
        vectors = [{"name": "fit"}]
        grades = [{"vector": "fit", "grade": "A", "confidence": 2}]
        assert agent_mod._validate_grades(grades, vectors) is None

    def test_validate_response_schema_nested_item_error(self) -> None:
        schema = {
            "jobs": {
                "type": "list",
                "required": True,
                "items_schema": {"name": {"type": "str", "required": True}},
            },
            "skip": "not-a-dict",
        }
        err = agent_mod._validate_response_schema(
            {"agent_payload": {"jobs": [{"name": 1}]}},
            schema,
            "task",
        )
        assert "jobs[0]" in err

    def test_store_prompt_blocks_without_optional_sections(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(agent_mod, "save_agent_data", lambda **kwargs: kwargs["agent_data_id"])
        blocks = agent_mod._store_prompt_blocks(
            entity_type="job",
            task_key="evaluate_jd",
            batch_id="batch-1",
            system_content="system",
            cache_content=None,
            nocache_content=None,
            user_content="",
            live_content=None,
        )
        assert blocks == [{"type": "SYSTEM", "id": blocks[0]["id"]}]
        assert blocks[0]["type"] == "SYSTEM"


class TestDecodeNotesAndChain:
    def test_skips_empty_notes_tail(self) -> None:
        decoded = agent_mod._decode_payload(
            "grade_do",
            "grades_encoded_notes",
            "0|CRA2",
            {"batch_entities": _batch_entities("job-1")},
        )
        assert "notes" not in decoded["jobs"][0]

    def test_chain_tokens_use_empty_caller_response(self) -> None:
        hop = agent_mod._chain_tokens_for_next_hop(
            system_content="",
            cache_content=None,
            nocache_content=None,
            live_content=None,
            parsed=None,
        )
        assert hop["CALLER_RESPONSE"] == ""


class TestDoTaskValidationStoreErrors:
    async def test_swallows_response_store_errors_on_validation_failures(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())

        def _save(**kwargs: Any) -> str:
            if kwargs.get("block_type") == "RESPONSE":
                raise RuntimeError("db")
            return kwargs["agent_data_id"]

        monkeypatch.setattr(agent_mod, "save_agent_data", _save)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "agent_payload": {
                            "bogus_section": "x",
                        }
                    },
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task("draft_job_resume", index="job-1", ctx=_draft_job_resume_ctx())
        assert out["success"] is False

        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        with monkeypatch.context() as patch:
            patch.setattr(agent_mod, "_validate_response_schema", lambda parsed, schema, task_key: "schema failed")
            out = await agent_mod.do_task(
                "evaluate_jd",
                index="job-1",
                ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
            )
            assert out["error"] == "schema failed"


class TestAgentPayloadListUnwrap:
    async def test_unwraps_list_agent_payload_before_decode(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": ["0|CRA2"]},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
        )
        assert out["success"] is True


class TestEntitySegmentAccess:
    def test_get_agent_data_keeps_rows_without_matching_segment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [{"block_type": "TASK", "block_data": json.dumps({"jobs": [{"astral_job_id": "other"}]})}]
        monkeypatch.setattr(agent_mod, "get_agent_data_by_batch", lambda batch_id, block_type: rows)
        out = agent_mod.get_agent_data("batch-1", entity_id="job-1")
        assert out[0]["block_data"] == rows[0]["block_data"]

    def test_extract_entity_segment_results_and_empty_inputs(self) -> None:
        payload = json.dumps({"results": [{"astral_job_id": "job-1", "x": 1}]})
        assert agent_mod._extract_entity_segment(payload, "job-1") == json.dumps({"astral_job_id": "job-1", "x": 1})
        assert agent_mod._extract_entity_segment("", "job-1") is None


class TestDoTaskFinalBranches:
    async def test_api_failure_without_response_content(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(return_value={"success": False, "error": "api down", "api_response": object()}),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task("evaluate_jd", index="job-1", ctx=_draft_job_resume_ctx())
        assert out["success"] is False

    async def test_success_without_raw_response_text(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": type("Resp", (), {"content": []})(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
            store_agent_data=False,
        )
        assert out["success"] is True

    async def test_skips_json_validation_for_text_tasks(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"company": "co", "title": "role"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task(
            "draft_cover_letter",
            index="job-1",
            ctx={"candidate_data": {"profile": {}}},
        )
        assert out["success"] is True

    async def test_swallows_append_agent_response_failure(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock(side_effect=RuntimeError("db")))
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
        )
        assert out["success"] is True

    async def test_post_decode_validation_store_failures(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())

        def _save(**kwargs: Any) -> str:
            if kwargs.get("block_type") == "RESPONSE":
                raise RuntimeError("db")
            return kwargs["agent_data_id"]

        monkeypatch.setattr(agent_mod, "save_agent_data", _save)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        send = AsyncMock(side_effect=lambda *args, **kwargs: _strict_batch_llm_ok(payload="0|CRA2"))
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)
        monkeypatch.setattr(
            agent_mod,
            "_validate_response_schema",
            lambda parsed, schema, task_key: "schema failed",
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert out["error"] == "schema failed"

        monkeypatch.setattr(agent_mod, "_validate_response_schema", lambda parsed, schema, task_key: None)
        monkeypatch.setattr(
            agent_mod,
            "_validate_grade_confidence_in_payload",
            lambda parsed, task_key: "confidence failed" if isinstance(parsed, dict) and parsed.get("jobs") else None,
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert out["error"] == "confidence failed"

    def test_decode_notes_tail_is_preserved(self) -> None:
        decoded = agent_mod._decode_payload(
            "grade_do",
            "grades_encoded_notes",
            "0|CRA2|note tail",
            {"batch_entities": _batch_entities("job-1")},
        )
        assert decoded["jobs"][0]["notes"] == "note tail"

    def test_get_entity_response_prefers_matching_row(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [
            {"block_data": json.dumps({"jobs": [{"astral_job_id": "other"}]})},
            {"block_data": json.dumps({"jobs": [{"astral_job_id": "job-1", "x": 1}]})},
        ]
        monkeypatch.setattr(agent_mod, "get_agent_data_by_batch", lambda batch_id, block_type: rows)
        out = agent_mod.get_entity_response("batch-1", "job-1")
        assert json.loads(out["block_data"])["x"] == 1


class TestDoTaskStoreExceptions:
    async def _run_with_response_store_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        send_return: Dict[str, Any],
        task_key: str = "evaluate_jd",
        ctx: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        monkeypatch.setattr(agent_mod, "send_to_anthropic", AsyncMock(return_value=send_return))

        def _save(**kwargs: Any) -> str:
            if kwargs.get("block_type") == "RESPONSE":
                raise RuntimeError("db")
            return kwargs["agent_data_id"]

        monkeypatch.setattr(agent_mod, "save_agent_data", _save)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        return await agent_mod.do_task(
            task_key,
            index="job-1",
            ctx=ctx or _rubric_evaluate_jd_ctx(),
        )

    async def test_records_validation_failure_response_block(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": _llm_failure_envelope(),
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        saved = MagicMock(return_value="resp-id")
        monkeypatch.setattr(agent_mod, "save_agent_data", saved)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task("evaluate_jd", index="job-1", ctx=_draft_job_resume_ctx())
        assert out["success"] is False
        assert any(call.kwargs.get("block_type") == "RESPONSE" for call in saved.call_args_list)
        out = await self._run_with_response_store_error(
            monkeypatch,
            batch_token,
            {"success": False, "error": "api down", "api_response": _api_response("fail")},
        )
        assert out["success"] is False

    async def test_json_schema_store_exception(self, monkeypatch: pytest.MonkeyPatch, batch_token: Any) -> None:
        _patch_normalize_rubric_response(
            monkeypatch,
            lambda task_key, task_config, parsed, ctx: (_ for _ in ()).throw(ValueError("normalize failed")),
        )
        out = await self._run_with_response_store_error(
            monkeypatch,
            batch_token,
            {
                "success": True,
                "parsed_response": {"agent_payload": "not-valid-encoded"},
                "api_response": _api_response(),
                "timesheet": {},
            },
        )
        assert "normalize failed" in out["error"]

    async def test_json_confidence_store_exception(self, monkeypatch: pytest.MonkeyPatch, batch_token: Any) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        _patch_normalize_rubric_response(
            monkeypatch,
            lambda task_key, task_config, parsed, ctx: {
                "jobs": [
                    {
                        "astral_job_id": "job-1",
                        "grades": [{"vector": "MISSION", "grade": "A", "confidence": 0}],
                    }
                ],
            },
        )

        def _save(**kwargs: Any) -> str:
            if kwargs.get("block_type") == "RESPONSE":
                raise RuntimeError("db")
            return kwargs["agent_data_id"]

        monkeypatch.setattr(agent_mod, "save_agent_data", _save)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
        )
        assert "confidence" in out["error"]

    async def test_json_grade_store_exception(self, monkeypatch: pytest.MonkeyPatch, batch_token: Any) -> None:
        out = await self._run_with_response_store_error(
            monkeypatch,
            batch_token,
            {
                "success": True,
                "parsed_response": {"agent_payload": {"bogus_section": "x"}},
                "api_response": _api_response(),
                "timesheet": {},
            },
            task_key="draft_job_resume",
            ctx=_draft_job_resume_ctx(),
        )
        assert "Unknown resume section key" in out["error"]

    async def test_decode_failure_store_exception(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        enable_debug_log: None,
    ) -> None:
        _patch_normalize_rubric_response(
            monkeypatch,
            lambda task_key, task_config, parsed, ctx: (_ for _ in ()).throw(ValueError("normalize failed")),
        )
        out = await self._run_with_response_store_error(
            monkeypatch,
            batch_token,
            {
                "success": True,
                "parsed_response": {"agent_payload": "bad|CRA2"},
                "api_response": _api_response(),
                "timesheet": {},
            },
        )
        assert "normalize failed" in out["error"]

    async def test_post_decode_store_exceptions(self, monkeypatch: pytest.MonkeyPatch, batch_token: Any) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        _patch_normalize_rubric_response(
            monkeypatch,
            lambda task_key, task_config, parsed, ctx: {"jobs": [{"astral_job_id": "job-1"}]},
        )
        def _llm_ok(*_a: Any, **_k: Any) -> Dict[str, Any]:
            return {
                "success": True,
                "parsed_response": {
                    "agent_performance": "ok",
                    "agent_payload": "0|CRA2",
                },
                "api_response": _api_response(),
                "timesheet": {},
            }

        monkeypatch.setattr(agent_mod, "send_to_anthropic", AsyncMock(side_effect=_llm_ok))

        def _save(**kwargs: Any) -> str:
            if kwargs.get("block_type") == "RESPONSE":
                raise RuntimeError("db")
            return kwargs["agent_data_id"]

        monkeypatch.setattr(agent_mod, "save_agent_data", _save)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(agent_mod, "_validate_response_schema", lambda parsed, schema, task_key: "schema failed")
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert out["error"] == "schema failed"

        monkeypatch.setattr(agent_mod, "_validate_response_schema", lambda parsed, schema, task_key: None)
        monkeypatch.setattr(
            agent_mod,
            "_validate_grade_confidence_in_payload",
            lambda parsed, task_key: "confidence failed",
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert out["error"] == "confidence failed"

    def test_get_agent_data_replaces_matching_segment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        raw = json.dumps({"jobs": [{"astral_job_id": "job-1", "x": 1}]})
        rows = [{"block_type": "TASK", "block_data": raw}]
        monkeypatch.setattr(agent_mod, "get_agent_data_by_batch", lambda batch_id, block_type: rows)
        out = agent_mod.get_agent_data("batch-1", entity_id="job-1")
        assert json.loads(out[0]["block_data"])["x"] == 1

    def test_extract_entity_segment_marker_without_trailing_bracket(self) -> None:
        assert agent_mod._extract_entity_segment("[job-1]\nsegment only", "job-1") == "segment only"

    async def test_success_when_raw_api_block_has_no_text_attr(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        blk = object()
        api = type("Resp", (), {"content": [blk], "id": "r1"})()
        saves = MagicMock(return_value="id")
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": api,
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", saves)
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(agent_mod, "compute_batch_cost", lambda batch_id: 1.0)
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
        )
        assert out["success"] is True
        assert not any(c.kwargs.get("block_type") == "RESPONSE" for c in saves.call_args_list)

    async def test_success_skips_append_when_no_index(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        append = MagicMock()
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock(return_value="id"))
        monkeypatch.setattr(agent_mod, "append_agent_response", append)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(agent_mod, "compute_batch_cost", lambda batch_id: 1.0)
        out = await agent_mod.do_task(
            "evaluate_jd",
            index=None,
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
        )
        assert out["success"] is True
        append.assert_not_called()

    async def test_post_decode_schema_requires_job_grades(self, monkeypatch: pytest.MonkeyPatch, batch_token: Any) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        _patch_normalize_rubric_response(
            monkeypatch,
            lambda task_key, task_config, parsed, ctx: {"jobs": [{"astral_job_id": "job-1"}]},
        )
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock(return_value="id"))
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert out["success"] is False
        assert "grades" in out["error"].lower()

    async def test_post_decode_confidence_error_swallows_response_store(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        _patch_normalize_rubric_response(
            monkeypatch,
            lambda task_key, task_config, parsed, ctx: {
                "jobs": [
                    {
                        "astral_job_id": "job-1",
                        "grades": [{"vector": "MISSION", "grade": "A", "confidence": 0}],
                    }
                ],
            },
        )
        monkeypatch.setattr(agent_mod, "_validate_response_schema", lambda parsed, schema, task_key: None)

        def _save2(**kwargs: Any) -> str:
            if kwargs.get("block_type") == "RESPONSE":
                raise RuntimeError("db")
            return kwargs["agent_data_id"]

        monkeypatch.setattr(agent_mod, "save_agent_data", _save2)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert out["success"] is False
        assert "confidence" in out["error"]

    async def test_decode_error_skips_agent_payload_suffix_when_blank(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "\n\t  \n"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        bodies: List[str] = []

        def _save(**kwargs: Any) -> str:
            if kwargs.get("block_type") == "RESPONSE":
                bodies.append(kwargs["block_data"])
            return kwargs["agent_data_id"]

        monkeypatch.setattr(agent_mod, "save_agent_data", _save)
        _patch_normalize_rubric_response(
            monkeypatch,
            lambda task_key, task_config, parsed, ctx: (_ for _ in ()).throw(ValueError("boom")),
        )
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert out["success"] is False
        assert bodies and "agent_payload" not in bodies[0]

    def test_get_agent_data_segment_none_keeps_raw_task_block(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [{"block_type": "TASK", "block_data": "{}"}]
        monkeypatch.setattr(agent_mod, "get_agent_data_by_batch", lambda *a: rows)
        out = agent_mod.get_agent_data("batch-1", entity_id="job-1")
        assert out[0]["block_data"] == "{}"

    def test_extract_entity_top_level_jobs_value_not_list_returns_blob(self) -> None:
        blob = json.dumps({"jobs": "not-a-list", "k": 1})
        assert agent_mod._extract_entity_segment(blob, "job-1") == blob

    def test_extract_entity_json_list_skips_object_path(self) -> None:
        assert agent_mod._extract_entity_segment(json.dumps([1, 2, 3]), "job-1") is None

    def test_extract_entity_empty_object_json(self) -> None:
        assert agent_mod._extract_entity_segment("{}", "job-1") is None

    def test_extract_entity_jobs_scan_without_match_returns_full(self) -> None:
        blob = json.dumps({"jobs": [{"astral_job_id": "other"}]})
        assert agent_mod._extract_entity_segment(blob, "job-1") == blob


class TestDoTaskShouldStoreBranches:
    async def test_failure_paths_skip_response_store_without_batch(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        saved = MagicMock(return_value="id")
        monkeypatch.setattr(agent_mod, "save_agent_data", saved)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        send = AsyncMock(
            return_value={
                "success": True,
                "parsed_response": _llm_failure_envelope(),
                "api_response": _api_response(),
                "timesheet": {},
            }
        )
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)
        out = await agent_mod.do_task("evaluate_jd", index="job-1", ctx=_draft_job_resume_ctx())
        assert out["success"] is False
        assert not any(c.kwargs.get("block_type") == "RESPONSE" for c in saved.call_args_list)

        send.return_value = {
            "success": True,
            "parsed_response": {
                "agent_payload": {
                    "bogus_section": "x",
                }
            },
            "api_response": _api_response(),
            "timesheet": {},
        }
        out = await agent_mod.do_task("draft_job_resume", index="job-1", ctx=_draft_job_resume_ctx())
        assert "Unknown resume section key" in out["error"]
        assert not any(c.kwargs.get("block_type") == "RESPONSE" for c in saved.call_args_list)

    async def test_failure_paths_skip_response_store_when_disabled(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        saved = MagicMock(return_value="id")
        monkeypatch.setattr(agent_mod, "save_agent_data", saved)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": False,
                    "error": "api down",
                    "api_response": _api_response("fail"),
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_draft_job_resume_ctx(),
            store_agent_data=False,
        )
        assert out["success"] is False
        assert not any(c.kwargs.get("block_type") == "RESPONSE" for c in saved.call_args_list)

    async def test_draft_job_resume_accepts_structure_keyed_payload_without_grades(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "agent_payload": {
                            "professional_summary": "Seasoned engineer.",
                            "experience": "Built things.",
                        }
                    },
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock(return_value="id"))
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task("draft_job_resume", index="job-1", ctx=_draft_job_resume_ctx())
        assert out["success"] is True

    async def test_draft_job_resume_rejects_unknown_section_key(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": {"bogus_section": "x"}},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock(return_value="id"))
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task("draft_job_resume", index="job-1", ctx=_draft_job_resume_ctx())
        assert out["success"] is False
        assert "Unknown resume section key" in out["error"]

    async def test_draft_job_resume_validation_failure_surfaces_message_in_error_and_response_block(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        saved = MagicMock(return_value="id")
        monkeypatch.setattr(agent_mod, "save_agent_data", saved)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": {"bogus_section": "x"}},
                    "api_response": _api_response("model body"),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task("draft_job_resume", index="job-1", ctx=_draft_job_resume_ctx())
        assert out["success"] is False
        assert "Unknown resume section key" in out["error"]
        response_calls = [c for c in saved.call_args_list if c.kwargs.get("block_type") == "RESPONSE"]
        assert response_calls
        body = response_calls[0].kwargs["block_data"]
        assert "Validation failed:" in body
        assert "Unknown resume section key" in body

    async def test_success_without_api_response_content(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": None,
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock(return_value="id"))
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
        )
        assert out["success"] is True

    async def test_draft_job_resume_rejects_disallowed_grades_field(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": {"grades": []}},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock(return_value="id"))
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task("draft_job_resume", index="job-1", ctx=_draft_job_resume_ctx())
        assert out["success"] is False
        assert "grades" in out["error"]

    async def test_grade_validation_failure_stores_response_block(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        saved = MagicMock(return_value="id")
        monkeypatch.setattr(agent_mod, "save_agent_data", saved)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "agent_payload": {
                            "bogus_section": "x",
                        }
                    },
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task("draft_job_resume", index="job-1", ctx=_draft_job_resume_ctx())
        assert "Unknown resume section key" in out["error"]
        assert any(c.kwargs.get("block_type") == "RESPONSE" for c in saved.call_args_list)

    async def test_decode_failure_stores_response_block(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        saved = MagicMock(return_value="id")
        monkeypatch.setattr(agent_mod, "save_agent_data", saved)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": _llm_failure_envelope(),
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert out["success"] is False
        assert any(c.kwargs.get("block_type") == "RESPONSE" for c in saved.call_args_list)

    async def test_post_decode_schema_failure_stores_response_block(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        saved = MagicMock(return_value="id")
        monkeypatch.setattr(agent_mod, "save_agent_data", saved)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        _patch_normalize_rubric_response(
            monkeypatch,
            lambda task_key, task_config, parsed, ctx: {"jobs": [{"astral_job_id": "job-1"}]},
        )
        monkeypatch.setattr(agent_mod, "_validate_response_schema", lambda parsed, schema, task_key: "schema failed")
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert out["success"] is False
        assert out["error"] == "schema failed"
        assert any(c.kwargs.get("block_type") == "RESPONSE" for c in saved.call_args_list)

    async def test_post_decode_confidence_failure_stores_response_block(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        saved = MagicMock(return_value="id")
        monkeypatch.setattr(agent_mod, "save_agent_data", saved)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        _patch_normalize_rubric_response(
            monkeypatch,
            lambda task_key, task_config, parsed, ctx: {
                "jobs": [
                    {
                        "astral_job_id": "job-1",
                        "grades": [{"vector": "MISSION", "grade": "A", "confidence": 0}],
                    }
                ],
            },
        )
        monkeypatch.setattr(agent_mod, "_validate_response_schema", lambda parsed, schema, task_key: None)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert out["success"] is False
        assert "confidence" in out["error"]
        assert any(c.kwargs.get("block_type") == "RESPONSE" for c in saved.call_args_list)

    async def test_grade_validation_store_exception_with_batch(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "_store_response_block",
            MagicMock(side_effect=RuntimeError("db")),
        )
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "agent_payload": {
                            "bogus_section": "x",
                        }
                    },
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task("draft_job_resume", index="job-1", ctx=_draft_job_resume_ctx())
        assert "Unknown resume section key" in out["error"]

    async def test_decode_failure_store_exception_with_batch(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "_store_response_block",
            MagicMock(side_effect=RuntimeError("db")),
        )
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": _llm_failure_envelope(),
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert "empty agent_payload" in out["error"]

    async def test_post_decode_schema_store_exception_with_batch(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        _patch_normalize_rubric_response(
            monkeypatch,
            lambda task_key, task_config, parsed, ctx: {"jobs": [{"astral_job_id": "job-1"}]},
        )
        monkeypatch.setattr(agent_mod, "_validate_response_schema", lambda parsed, schema, task_key: "schema failed")
        monkeypatch.setattr(
            agent_mod,
            "_store_response_block",
            MagicMock(side_effect=RuntimeError("db")),
        )
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert out["success"] is False
        assert out["error"] == "schema failed"

    async def test_post_decode_confidence_store_exception_with_batch(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        _patch_normalize_rubric_response(
            monkeypatch,
            lambda task_key, task_config, parsed, ctx: {
                "jobs": [
                    {
                        "astral_job_id": "job-1",
                        "grades": [{"vector": "MISSION", "grade": "A", "confidence": 0}],
                    }
                ],
            },
        )
        monkeypatch.setattr(agent_mod, "_validate_response_schema", lambda parsed, schema, task_key: None)
        monkeypatch.setattr(
            agent_mod,
            "_store_response_block",
            MagicMock(side_effect=RuntimeError("db")),
        )
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert "confidence" in out["error"]


class TestDoTaskStoreExceptionWithoutBatch:
    async def test_grade_validation_store_exception_without_batch(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "_store_response_block",
            MagicMock(side_effect=RuntimeError("db")),
        )
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "agent_payload": {
                            "bogus_section": "x",
                        }
                    },
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task("draft_job_resume", index="job-1", ctx=_draft_job_resume_ctx())
        assert "Unknown resume section key" in out["error"]

    async def test_decode_failure_store_exception_without_batch(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        monkeypatch.setattr(
            agent_mod,
            "_store_response_block",
            MagicMock(side_effect=RuntimeError("db")),
        )
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": _llm_failure_envelope(),
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert "empty agent_payload" in out["error"]

    async def test_post_decode_schema_failure_without_batch(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        _patch_normalize_rubric_response(
            monkeypatch,
            lambda task_key, task_config, parsed, ctx: {"jobs": [{"astral_job_id": "job-1"}]},
        )
        monkeypatch.setattr(agent_mod, "_validate_response_schema", lambda parsed, schema, task_key: "schema failed")
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert out["success"] is False
        assert out["error"] == "schema failed"

    async def test_post_decode_confidence_failure_without_batch(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        _patch_normalize_rubric_response(
            monkeypatch,
            lambda task_key, task_config, parsed, ctx: {
                "jobs": [
                    {
                        "astral_job_id": "job-1",
                        "grades": [{"vector": "MISSION", "grade": "A", "confidence": 0}],
                    }
                ],
            },
        )
        monkeypatch.setattr(agent_mod, "_validate_response_schema", lambda parsed, schema, task_key: None)
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_rubric_evaluate_jd_ctx(),
        )
        assert "confidence" in out["error"]


class TestDoTaskEncodedPostDecodeFallthrough:
    async def test_skips_confidence_check_when_decoded_payload_is_not_dict(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows())
        _patch_normalize_rubric_response(monkeypatch, lambda task_key, task_config, parsed, ctx: "decoded-text")
        real_schema = agent_mod._validate_response_schema

        def _schema(parsed: Any, schema: Any, task_key: str) -> str | None:
            if isinstance(parsed, str):
                return None
            return real_schema(parsed, schema, task_key)

        monkeypatch.setattr(agent_mod, "_validate_response_schema", _schema)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"agent_payload": "0|CRA2"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock(return_value="id"))
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
        )
        assert out["success"] is True


class TestMergeChainContextForNextHop:
    def test_parent_none_only_hop_keys(self) -> None:
        hop = {"A": "1", "B": "2"}
        assert agent_mod._merge_chain_context_for_next_hop(None, hop) == hop

    def test_parent_empty_dict_skips_copy_loop(self) -> None:
        assert agent_mod._merge_chain_context_for_next_hop({}, {"X": "y"}) == {"X": "y"}

    def test_parent_copies_non_selected_agent_hop_wins_overlap(self) -> None:
        parent = {"SELECTED_AGENT": "old-agent", "KEEP": "p"}
        hop = {"KEEP": "h", "NEW": "n"}
        assert agent_mod._merge_chain_context_for_next_hop(parent, hop) == {
            "KEEP": "h",
            "NEW": "n",
        }


class TestAst597MidChainResumeHydrationAndTransitions:
    """AST-597 / AST-803: agent_data caller hydration; per-hop compound transitions retired."""

    def test_resume_artifact_parent_hop_key_first_hop_none(self) -> None:
        assert agent_mod._resume_artifact_parent_hop_key("anticipate_scan") is None

    def test_resume_artifact_parent_hop_key_mid_chain(self) -> None:
        assert agent_mod._resume_artifact_parent_hop_key("draft_job_resume") == "advise_job_resume"

    def test_parsed_response_from_stored_unwraps_agent_payload(self) -> None:
        raw = json.dumps({"agent_payload": ["line-a", "line-b"]})
        parsed = agent_mod._parsed_response_from_stored_response_text(raw, "advise_job_resume")
        assert parsed == "line-a\nline-b"

    def test_hop_agent_ref_for_parent_skips_failed_response_rows(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            agent_mod,
            "get_agent_data_for_ids",
            MagicMock(
                side_effect=lambda ids: {
                    "bad": {"block_data": "Validation failed: schema"},
                    "good": {"block_data": "upstream advice"},
                }
            ),
        )
        job = {
            "agent_responses": [
                {
                    "task_key": "advise_job_resume",
                    "prompt_blocks": [{"type": "RESPONSE", "id": "bad"}],
                },
                {
                    "task_key": "advise_job_resume",
                    "prompt_blocks": [{"type": "RESPONSE", "id": "good"}],
                },
            ],
        }
        ref = agent_mod._hop_agent_ref_for_parent(job, "advise_job_resume", None)
        assert ref is not None
        assert ref["prompt_blocks"][0]["id"] == "good"

    def test_hydrate_resume_entry_chain_context_first_hop_empty(self) -> None:
        ctx, err = agent_mod._hydrate_resume_entry_chain_context("job-1", "anticipate_scan")
        assert err is None
        assert ctx == {}

    def test_hydrate_resume_entry_chain_context_builds_agent_data_tokens(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        job = {
            "astral_job_id": "job-hydrate",
            "agent_responses": [
                {
                    "task_key": "advise_job_resume",
                    "prompt_blocks": [
                        {"type": "SYSTEM", "id": "sys-1"},
                        {"type": "RESPONSE", "id": "resp-1"},
                    ],
                }
            ],
        }
        monkeypatch.setattr(
            "src.core.tracker.get_job",
            lambda jid: job if jid == "job-hydrate" else None,
        )
        monkeypatch.setattr(
            agent_mod,
            "get_agent_data_for_ids",
            MagicMock(
                return_value={
                    "sys-1": {"block_data": "parent system"},
                    "resp-1": {"block_data": "resume advice body"},
                }
            ),
        )
        ctx, err = agent_mod._hydrate_resume_entry_chain_context(
            "job-hydrate", "draft_job_resume"
        )
        assert err is None
        assert ctx is not None
        assert ctx.get("_caller_hydration_source") == "agent_data"
        assert ctx.get("_hop_parent_task_key") == "advise_job_resume"
        assert (ctx.get("CALLER_SYSTEM") or "").strip() == "parent system"
        assert (ctx.get("CALLER_RESPONSE") or "").strip() == "resume advice body"

    def test_hydrate_resume_entry_chain_context_missing_upstream(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "src.core.tracker.get_job",
            lambda jid: {"astral_job_id": jid, "agent_responses": []},
        )
        ctx, err = agent_mod._hydrate_resume_entry_chain_context(
            "job-miss", "draft_job_resume"
        )
        assert ctx is None
        assert err and "No stored agent_data" in err

    @pytest.mark.asyncio
    async def test_do_task_success_does_not_transition_compound_build_state(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
    ) -> None:
        transition = MagicMock()
        monkeypatch.setattr("src.core.tracker.transition_job_state", transition)
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows(run_next=""))
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"title": "Role", "company": "Co"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "anticipate_scan",
            index="job-597",
            ctx={"candidate_data": {"artifacts": {}}, "batch_entities": _batch_entities("job-597")},
        )
        assert out["success"] is True
        transition.assert_not_called()

    @pytest.mark.asyncio
    async def test_resume_hop_debug_logs_agent_data_source_on_mid_chain_entry(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        caplog.set_level("DEBUG")
        job = {
            "astral_job_id": "job-dbg",
            "agent_responses": [
                {
                    "task_key": "advise_job_resume",
                    "batch_id": "batch-1",
                    "prompt_blocks": [
                        {"type": "SYSTEM", "id": "sys-dbg"},
                        {"type": "RESPONSE", "id": "resp-dbg"},
                    ],
                }
            ],
        }
        monkeypatch.setattr(
            "src.core.tracker.get_job",
            lambda jid: job if jid == "job-dbg" else None,
        )
        monkeypatch.setattr(
            agent_mod,
            "get_agent_data_for_ids",
            MagicMock(
                return_value={
                    "sys-dbg": {"block_data": "upstream sys"},
                    "resp-dbg": {"block_data": "upstream resp"},
                }
            ),
        )
        agent_row, task_row = _agent_rows(run_next="")
        task_row["system_prompt"] = "sys {$CALLER_SYSTEM}"
        monkeypatch.setattr(
            agent_mod, "_resolve_task_prompts", lambda key: (agent_row, task_row)
        )
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"professional_summary": "ok"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        await agent_mod.do_task(
            "draft_job_resume",
            index="job-dbg",
            ctx=_draft_job_resume_ctx(),
            debug=True,
            chain_context={
                "_hop_parent_task_key": "advise_job_resume",
            },
        )
        combined = "\n".join(r.message for r in caplog.records)
        assert "caller_source=agent_data" in combined
        assert "caller_hydration=agent_data" in combined
        assert "upstream=advise_job_resume" in combined


class TestAst769GeneralCallerHydration:
    """AST-769: general caller hydration from agent_data for all entity types."""

    def test_anchor_batch_id_from_state_history_uses_current_state_row(self) -> None:
        entity = {
            "state": "JOBLIST_IDENTIFIED",
            "state_history": [
                {"to_state": "PJL_READY", "batch_id": "batch-old"},
                {"to_state": "JOBLIST_IDENTIFIED", "batch_id": "batch-anchor"},
            ],
        }
        assert agent_mod._anchor_batch_id_from_state_history(entity) == "batch-anchor"

    def test_hop_agent_ref_for_parent_prefers_anchor_batch_over_newer_ref(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            agent_mod,
            "get_agent_data_for_ids",
            MagicMock(
                side_effect=lambda ids: {
                    "resp-wrong": {"block_data": '{"selected_page": 9}'},
                    "resp-right": {"block_data": '{"selected_page": 1}'},
                }
            ),
        )
        entity = {
            "state": "JOBLIST_IDENTIFIED",
            "state_history": [
                {"to_state": "JOBLIST_IDENTIFIED", "batch_id": "batch-anchor"},
            ],
            "agent_responses": [
                {
                    "task_key": "select_job_page",
                    "batch_id": "batch-newer-unrelated",
                    "prompt_blocks": [{"type": "RESPONSE", "id": "resp-wrong"}],
                },
                {
                    "task_key": "select_job_page",
                    "batch_id": "batch-anchor",
                    "prompt_blocks": [{"type": "RESPONSE", "id": "resp-right"}],
                },
            ],
        }
        anchor = agent_mod._anchor_batch_id_from_state_history(entity)
        ref = agent_mod._hop_agent_ref_for_parent(entity, "select_job_page", anchor)
        assert ref is not None
        assert ref["batch_id"] == "batch-anchor"
        assert ref["prompt_blocks"][0]["id"] == "resp-right"

    def test_merge_hydrated_caller_context_preserves_non_caller_keys(self) -> None:
        hydrated = {
            "CALLER_SYSTEM": "stored sys",
            "CALLER_RESPONSE": "stored resp",
            "_caller_hydration_source": "agent_data",
            "_hop_parent_task_key": "select_job_page",
        }
        merged = agent_mod._merge_hydrated_caller_context(
            {"JOB_LIST_VISIBLE": "listing plain text", "SELECTED_AGENT": "Grace"},
            hydrated,
        )
        assert merged["JOB_LIST_VISIBLE"] == "listing plain text"
        assert merged["SELECTED_AGENT"] == "Grace"
        assert merged["CALLER_SYSTEM"] == "stored sys"
        assert merged["_caller_hydration_source"] == "agent_data"

    @pytest.mark.asyncio
    async def test_do_task_parse_job_list_hydrates_caller_from_company_agent_data(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        company = {
            "short_name": "co-769",
            "state": "JOBLIST_IDENTIFIED",
            "state_history": [
                {"to_state": "JOBLIST_IDENTIFIED", "batch_id": "batch-1"},
            ],
            "agent_responses": [
                {
                    "task_key": "select_job_page",
                    "batch_id": "batch-1",
                    "prompt_blocks": [
                        {"type": "SYSTEM", "id": "sys-sjp"},
                        {"type": "RESPONSE", "id": "resp-sjp"},
                    ],
                }
            ],
        }
        monkeypatch.setattr(
            "src.core.tracker.get_company",
            lambda cid: company if cid == "co-769" else None,
        )
        monkeypatch.setattr(
            agent_mod,
            "get_agent_data_for_ids",
            MagicMock(
                return_value={
                    "sys-sjp": {"block_data": "parent roster system"},
                    "resp-sjp": {
                        "block_data": json.dumps(
                            {
                                "selected_page": 1,
                                "response_type": "JOBLIST_TITLES",
                                "job_titles": ["Engineer"],
                            }
                        )
                    },
                }
            ),
        )

        def resolve_prompt(task_key: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
            agent_row, task_row = _agent_rows()
            if task_key == "parse_job_list":
                task_row["system_prompt"] = (
                    "Parse {$CALLER_SYSTEM} {$CALLER_RESPONSE} visible={$JOB_LIST_VISIBLE}"
                )
            return agent_row, task_row

        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", resolve_prompt)
        monkeypatch.setattr(
            agent_mod,
            "get_agent_task",
            lambda tk: {"agent_id": "agent-1", "run_next": "parse_job_list"}
            if tk == "select_job_page"
            else None,
        )
        monkeypatch.setattr(
            agent_mod,
            "get_task_keys",
            lambda: ["select_job_page", "parse_job_list"],
        )

        captured: Dict[str, Any] = {}
        orig_resolve = agent_mod.resolve_tokens

        def capture_resolve(
            prompt: str,
            cd: Any,
            tk: str,
            cc: Any,
            job_context: Any = None,
            **kwargs: Any,
        ) -> str:
            if tk == "parse_job_list":
                captured["CALLER_SYSTEM"] = (cc or {}).get("CALLER_SYSTEM")
                captured["CALLER_RESPONSE"] = (cc or {}).get("CALLER_RESPONSE")
                captured["JOB_LIST_VISIBLE"] = (cc or {}).get("JOB_LIST_VISIBLE")
            return orig_resolve(prompt, cd, tk, cc, job_context, **kwargs)

        monkeypatch.setattr(agent_mod, "resolve_tokens", capture_resolve)
        _patch_strict_batch_anthropic(monkeypatch)
        send = AsyncMock(
            return_value={
                "success": True,
                "parsed_response": {
                    "job_container": "div",
                    "job_tag": "a",
                    "job_ids": ["j-1"],
                },
                "api_response": _api_response("parse"),
                "timesheet": {},
            }
        )
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())

        out = await agent_mod.do_task(
            "parse_job_list",
            live_content="<jobs/>",
            index="co-769",
            ctx={"candidate_data": {}},
            chain_context={"JOB_LIST_VISIBLE": "Role listing plain text"},
        )

        assert out["success"] is True
        send.assert_awaited_once()
        assert captured.get("CALLER_SYSTEM") == "parent roster system"
        assert "Engineer" in (captured.get("CALLER_RESPONSE") or "")
        assert captured.get("JOB_LIST_VISIBLE") == "Role listing plain text"

    @pytest.mark.asyncio
    async def test_do_task_job_cover_letter_hydrates_from_stored_parent_hop(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        job = {
            "astral_job_id": "job-cl-769",
            "agent_responses": [
                {
                    "task_key": "contemplate_job",
                    "batch_id": "batch-cl",
                    "prompt_blocks": [
                        {"type": "SYSTEM", "id": "sys-cj"},
                        {"type": "RESPONSE", "id": "resp-cj"},
                    ],
                }
            ],
        }
        monkeypatch.setattr(
            "src.core.tracker.get_job",
            lambda jid: job if jid == "job-cl-769" else None,
        )
        monkeypatch.setattr(
            agent_mod,
            "get_agent_data_for_ids",
            MagicMock(
                return_value={
                    "sys-cj": {"block_data": "contemplate system"},
                    "resp-cj": {"block_data": "contemplate narrative"},
                }
            ),
        )

        agent_row, task_row = _agent_rows()
        task_row["system_prompt"] = "Draft {$CALLER_SYSTEM} {$CALLER_RESPONSE}"
        monkeypatch.setattr(
            agent_mod, "_resolve_task_prompts", lambda key: (agent_row, task_row)
        )
        monkeypatch.setattr(
            agent_mod,
            "_parent_hop_task_key_for_child",
            lambda child: "contemplate_job" if child == "draft_cover_letter" else None,
        )

        captured: Dict[str, str] = {}

        def capture_resolve(
            prompt: str,
            cd: Any,
            tk: str,
            cc: Any,
            job_context: Any = None,
            **kwargs: Any,
        ) -> str:
            if tk == "draft_cover_letter":
                captured["CALLER_SYSTEM"] = (cc or {}).get("CALLER_SYSTEM", "")
                captured["CALLER_RESPONSE"] = (cc or {}).get("CALLER_RESPONSE", "")
            return resolve_tokens(prompt, cd, tk, cc, job_context, **kwargs)

        monkeypatch.setattr(agent_mod, "resolve_tokens", capture_resolve)
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"re_line": "Re:", "body": "Dear hiring manager"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())

        out = await agent_mod.do_task(
            "draft_cover_letter",
            index="job-cl-769",
            ctx={"candidate_data": {"profile": {}}},
        )

        assert out["success"] is True
        assert captured.get("CALLER_SYSTEM") == "contemplate system"
        assert captured.get("CALLER_RESPONSE") == "contemplate narrative"

    @pytest.mark.asyncio
    async def test_do_task_hydration_miss_returns_error_without_llm(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        monkeypatch.setattr(
            "src.core.tracker.get_company",
            lambda cid: {"short_name": cid, "agent_responses": []},
        )
        agent_row, task_row = _agent_rows()
        task_row["system_prompt"] = "Parse {$CALLER_SYSTEM}"
        monkeypatch.setattr(
            agent_mod, "_resolve_task_prompts", lambda key: (agent_row, task_row)
        )
        monkeypatch.setattr(
            agent_mod,
            "_parent_hop_task_key_for_child",
            lambda child: "select_job_page" if child == "parse_job_list" else None,
        )
        send = AsyncMock()
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)

        out = await agent_mod.do_task(
            "parse_job_list",
            live_content="<jobs/>",
            index="co-miss",
            ctx={"candidate_data": {}},
        )

        assert out["success"] is False
        assert "No stored agent_data" in (out.get("error") or "")
        send.assert_not_called()

    @pytest.mark.asyncio
    async def test_do_task_hydrated_hop_debug_logs_agent_data(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        caplog.set_level("DEBUG")
        company = {
            "short_name": "co-dbg",
            "agent_responses": [
                {
                    "task_key": "select_job_page",
                    "batch_id": "batch-1",
                    "prompt_blocks": [
                        {"type": "SYSTEM", "id": "sys-dbg"},
                        {"type": "RESPONSE", "id": "resp-dbg"},
                    ],
                }
            ],
        }
        monkeypatch.setattr(
            "src.core.tracker.get_company",
            lambda cid: company if cid == "co-dbg" else None,
        )
        monkeypatch.setattr(
            agent_mod,
            "get_agent_data_for_ids",
            MagicMock(
                return_value={
                    "sys-dbg": {"block_data": "dbg sys"},
                    "resp-dbg": {"block_data": '{"selected_page": 1}'},
                }
            ),
        )
        agent_row, task_row = _agent_rows()
        task_row["system_prompt"] = "Parse {$CALLER_SYSTEM}"
        monkeypatch.setattr(
            agent_mod, "_resolve_task_prompts", lambda key: (agent_row, task_row)
        )
        monkeypatch.setattr(
            agent_mod,
            "_parent_hop_task_key_for_child",
            lambda child: "select_job_page" if child == "parse_job_list" else None,
        )
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "job_container": "d",
                        "job_tag": "a",
                        "job_ids": ["1"],
                    },
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())

        await agent_mod.do_task(
            "parse_job_list",
            live_content="<jobs/>",
            index="co-dbg",
            ctx={"candidate_data": {}},
            debug=True,
        )

        combined = "\n".join(r.message for r in caplog.records)
        assert "caller_hydration=agent_data" in combined
        assert "upstream=select_job_page" in combined


class TestRunCoverLetterArtifactChainForJob:
    async def test_raises_when_first_task_key_missing_from_task_config(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(
            agent_mod.BUILD_CONFIG,
            "cover_letter_artifact_chain",
            {"first_task_key": "__not_in_task_config__"},
        )
        with pytest.raises(ValueError, match="first_task_key"):
            await agent_mod.run_cover_letter_artifact_chain_for_job("job-1")

    async def test_job_not_found_returns_error_dict(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(database_mod, "get_job", lambda jid: None)
        out = await agent_mod.run_cover_letter_artifact_chain_for_job("missing-job")
        assert out["success"] is False
        assert "not found" in (out.get("error") or "").lower()

    async def test_starts_cover_letter_chain_with_draft_cover_letter_via_do_task(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        job = {"astral_job_id": "j-cl", "company": None}
        monkeypatch.setattr(
            database_mod,
            "get_job",
            lambda jid: (_ for _ in ()).throw(AssertionError("get_job should not run")),
        )
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        do_task = AsyncMock(return_value={"success": True})
        monkeypatch.setattr(agent_mod, "do_task", do_task)

        await agent_mod.run_cover_letter_artifact_chain_for_job("j-cl", ctx={"job": job})

        do_task.assert_awaited_once()
        assert do_task.await_args.args[0] == "draft_cover_letter"

    async def test_loads_company_when_job_has_company_ref(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        job = {"astral_job_id": "j-cl", "company": "co-1"}
        get_co = MagicMock(return_value={"short_name": "co-1"})
        monkeypatch.setattr(
            database_mod,
            "get_job",
            lambda jid: (_ for _ in ()).throw(AssertionError("get_job should not run")),
        )
        monkeypatch.setattr(database_mod, "get_company", get_co)
        prep = AsyncMock(return_value="live")
        monkeypatch.setattr(consult_mod, "_prep_live_content", prep)
        monkeypatch.setattr(agent_mod, "do_task", AsyncMock(return_value={"success": True}))

        await agent_mod.run_cover_letter_artifact_chain_for_job("j-cl", ctx={"job": job})

        get_co.assert_called_once_with("co-1")
        assert prep.await_args[0][1] == get_co.return_value

    async def test_empty_live_content_returns_error_on_cover_chain(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        job = {"astral_job_id": "j-cl", "company": None}
        monkeypatch.setattr(
            database_mod,
            "get_job",
            lambda jid: (_ for _ in ()).throw(AssertionError("get_job should not run")),
        )
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value=""))
        out = await agent_mod.run_cover_letter_artifact_chain_for_job("j-cl", ctx={"job": job})
        assert out["success"] is False
        assert "live_content" in (out.get("error") or "").lower()

    async def test_fetches_job_when_ctx_has_no_matching_row(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fetched = {"astral_job_id": "j-remote", "company": None}
        monkeypatch.setattr(database_mod, "get_job", lambda jid: fetched if jid == "j-remote" else None)
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        do_task = AsyncMock(return_value={"success": True})
        monkeypatch.setattr(agent_mod, "do_task", do_task)

        await agent_mod.run_cover_letter_artifact_chain_for_job(
            "j-remote",
            ctx={"noise": True},
        )

        assert do_task.await_args.kwargs["index"] == "j-remote"
        batch = do_task.await_args.kwargs["ctx"]["batch_entities"][0]
        assert batch["astral_job_id"] == "j-remote"

    async def test_keeps_existing_vector_labels_in_cover_chain_ctx(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        job = {"astral_job_id": "jl", "company": None}
        monkeypatch.setattr(
            database_mod,
            "get_job",
            lambda jid: (_ for _ in ()).throw(AssertionError("no fetch")),
        )
        monkeypatch.setattr(consult_mod, "_prep_live_content", AsyncMock(return_value="live"))
        do_task = AsyncMock(return_value={"success": True})
        monkeypatch.setattr(agent_mod, "do_task", do_task)

        vl = {"custom": True}
        await agent_mod.run_cover_letter_artifact_chain_for_job(
            "jl",
            ctx={"job": job, "vector_labels": vl},
        )

        assert do_task.await_args.kwargs["ctx"]["vector_labels"] is vl


# AST-531 — per-hop dispatch_ledger for run_next chains (parent AST-528).
class TestAst531RunNextHopLedger:
    @pytest.fixture
    def hop_ledger_trackers(self, monkeypatch: pytest.MonkeyPatch) -> Dict[str, Any]:
        saves: List[Any] = []
        updates: List[Any] = []
        monkeypatch.setattr(
            agent_mod.database,
            "save_dispatch_ledger",
            lambda *args, **kwargs: saves.append((args, kwargs)),
        )
        monkeypatch.setattr(
            agent_mod.database,
            "update_dispatch_ledger",
            lambda batch_id, **kwargs: updates.append((batch_id, kwargs)),
        )
        monkeypatch.setattr(agent_mod, "compute_batch_cost", lambda batch_id: 0.0)
        uuids = iter(
            [
                __import__("uuid").UUID("00000000-0000-0000-0000-000000000001"),
                __import__("uuid").UUID("00000000-0000-0000-0000-000000000002"),
            ]
        )
        monkeypatch.setattr(agent_mod.uuid, "uuid4", lambda: next(uuids))
        return {"saves": saves, "updates": updates}

    @pytest.mark.asyncio
    async def test_two_hop_chain_creates_distinct_ledger_rows(
        self, monkeypatch: pytest.MonkeyPatch, hop_ledger_trackers: Dict[str, Any]
    ) -> None:
        def resolve(task_key: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
            if task_key == "qualify_job_listings":
                return _agent_rows(run_next="evaluate_jd")
            return _agent_rows(run_next="")

        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", resolve)
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                side_effect=[
                    _strict_batch_llm_ok(api_label="first"),
                    _strict_batch_llm_ok(api_label="second"),
                ]
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        agent_mod.log_batch_id.set(None)
        out = await agent_mod.do_task(
            "qualify_job_listings",
            index="job-1",
            ctx={
                "astral_candidate_id": "c1",
                "candidate_api_key": "key",
                "candidate_data": {},
                "batch_entities": _batch_entities("job-1"),
            },
        )
        assert out["success"] is True
        saves = hop_ledger_trackers["saves"]
        updates = hop_ledger_trackers["updates"]
        assert len(saves) == 2
        assert saves[0][0][0] != saves[1][0][0]
        assert saves[0][0][1] == "qualify_job_listings"
        assert saves[1][0][1] == "evaluate_jd"
        assert saves[0][0][2] == "c1"
        assert saves[0][1]["status"] == "RUNNING"
        assert len(updates) == 2
        assert all(u[1]["status"] == "COMPLETED" for u in updates)
        assert agent_mod.log_batch_id.get() is None

    @pytest.mark.asyncio
    async def test_single_hop_without_run_next_does_not_open_hop_ledger(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        saves: List[Any] = []
        monkeypatch.setattr(
            agent_mod.database,
            "save_dispatch_ledger",
            lambda *args, **kwargs: saves.append((args, kwargs)),
        )
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows(run_next=""))
        monkeypatch.setattr(agent_mod, "get_active_llm_provider", lambda: "anthropic")
        monkeypatch.setattr(agent_mod, "send_to_deepseek", AsyncMock())
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"search_terms": "alpha\nbeta"},
                    "api_response": _api_response('{"search_terms":"alpha\\nbeta"}'),
                    "timesheet": {},
                }
            ),
        )
        monkeypatch.setattr(agent_mod, "save_agent_data", MagicMock())
        monkeypatch.setattr(agent_mod, "append_agent_response", MagicMock())
        monkeypatch.setattr(agent_mod, "add_agent_response_entry", MagicMock())
        token = agent_mod.log_batch_id.set("outer-batch-123")
        try:
            out = await agent_mod.do_task(
                "craft_company_search_terms",
                index="c1",
                ctx={"candidate_data": {"artifacts": {}}},
            )
            assert out["success"] is True
            assert saves == []
            assert agent_mod.log_batch_id.get() == "outer-batch-123"
        finally:
            agent_mod.log_batch_id.reset(token)


# AST-515 — workbench Test writes dispatch_ledger + agent_data (parent AST-514).
class TestAst515AdhocWorkbenchLedger:
    @pytest.fixture
    def ledger_trackers(self, monkeypatch: pytest.MonkeyPatch) -> Dict[str, Any]:
        saves: List[Any] = []
        updates: List[Any] = []
        monkeypatch.setattr(
            agent_mod.database,
            "save_dispatch_ledger",
            lambda *args, **kwargs: saves.append((args, kwargs)),
        )
        monkeypatch.setattr(
            agent_mod.database,
            "update_dispatch_ledger",
            lambda batch_id, **kwargs: updates.append((batch_id, kwargs)),
        )
        monkeypatch.setattr(agent_mod, "compute_batch_cost", lambda batch_id: 2.5)
        monkeypatch.setattr(
            agent_mod.uuid,
            "uuid4",
            lambda: __import__("uuid").UUID("00000000-0000-0000-0000-000000000001"),
        )
        store_prompt = MagicMock()
        store_response = MagicMock()
        monkeypatch.setattr(agent_mod, "_store_prompt_blocks", store_prompt)
        monkeypatch.setattr(agent_mod, "_store_response_block", store_response)
        return {
            "saves": saves,
            "updates": updates,
            "store_prompt": store_prompt,
            "store_response": store_response,
        }

    async def test_success_completes_ledger_and_stores_blocks(
        self, monkeypatch: pytest.MonkeyPatch, ledger_trackers: Dict[str, Any]
    ) -> None:
        async def _ok(**kwargs: Any) -> Dict[str, Any]:
            return {"success": True, "parsed_response": {"agent_payload": "ok"}, "timesheet": {}}

        monkeypatch.setattr(agent_mod, "run_adhoc", _ok)
        out = await agent_mod.run_adhoc_workbench_test(
            workbench_task_key="evaluate_jd",
            candidate_id="c1",
            entity_id="j1",
            system_content="sys",
            user_content="usr",
        )
        assert out["success"] is True
        assert len(ledger_trackers["saves"]) == 1
        save_args = ledger_trackers["saves"][0][0]
        assert save_args[1] == "adhoc-evaluate_jd"
        assert save_args[2] == "c1"
        assert ledger_trackers["saves"][0][1]["status"] == "RUNNING"
        assert ledger_trackers["store_prompt"].call_count == 1
        assert ledger_trackers["store_response"].call_args[0][3] == "ok"
        final = ledger_trackers["updates"][-1][1]
        assert final["status"] == "COMPLETED"
        assert final["total_passed"] == 1
        assert agent_mod.log_batch_id.get() is None

    async def test_failure_marks_ledger_failed_and_stores_failure_response(
        self, monkeypatch: pytest.MonkeyPatch, ledger_trackers: Dict[str, Any]
    ) -> None:
        async def _fail(**kwargs: Any) -> Dict[str, Any]:
            return {"success": False, "error": "nope"}

        monkeypatch.setattr(agent_mod, "run_adhoc", _fail)
        out = await agent_mod.run_adhoc_workbench_test(
            workbench_task_key="evaluate_jd",
            candidate_id="c1",
            entity_id="j1",
        )
        assert out["success"] is False
        assert ledger_trackers["updates"][-1][1]["status"] == "FAILED"
        assert ledger_trackers["updates"][-1][1]["total_failed"] == 1
        assert ledger_trackers["store_response"].call_count == 1

    async def test_exception_updates_ledger_then_reraises(
        self, monkeypatch: pytest.MonkeyPatch, ledger_trackers: Dict[str, Any]
    ) -> None:
        async def _boom(**kwargs: Any) -> Dict[str, Any]:
            raise RuntimeError("boom")

        monkeypatch.setattr(agent_mod, "run_adhoc", _boom)
        with pytest.raises(RuntimeError, match="boom"):
            await agent_mod.run_adhoc_workbench_test(
                workbench_task_key="evaluate_jd",
                candidate_id="c1",
            )
        assert any(u[1].get("total_errors") == 1 for u in ledger_trackers["updates"])
        assert agent_mod.log_batch_id.get() is None


class TestAst724VectorFeedbackCapture:
    """AST-724: lenient vector_reviews capture on SUCCESS — parse failures store FEEDBACK only."""

    def test_agent_performance_status_normalizes_dict_and_string(self) -> None:
        assert agent_mod._agent_performance_status({"status": "SUCCESS"}) == "success"
        assert agent_mod._agent_performance_status("Failure") == "failure"
        assert agent_mod._agent_performance_status(None) is None

    def test_rubric_feedback_owner_and_candidate_resolves_from_cd_and_ctx(self) -> None:
        owner, cid = agent_mod._rubric_feedback_owner_and_candidate(
            "grade_get",
            {"_astral_candidate_id": "cand-1"},
            None,
        )
        assert owner == "grade_get"
        assert cid == "cand-1"
        owner2, cid2 = agent_mod._rubric_feedback_owner_and_candidate(
            "evaluate_jd",
            {},
            {"astral_candidate_id": "cand-2"},
        )
        assert owner2 == "evaluate_jd"
        assert cid2 == "cand-2"

    def test_clean_parse_inserts_vector_feedback_rows(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [{"code": "G1", "label": "G1", "content": "body\nA = one\nB = two", "importance": 5}],
        )
        prompt_blocks: List[Dict[str, str]] = []
        agent_mod._capture_rubric_vector_feedback(
            task_key="grade_get",
            owner_task_key="grade_get",
            candidate_id="cand-1",
            batch_id="batch-724-clean",
            entity_type="candidate",
            index=None,
            perf={"status": "success", "vector_reviews": ["G1RACOVK"]},
            debug=False,
            prompt_blocks=prompt_blocks,
            batch_size=1,
        )
        conn = db._get_connection()
        try:
            n = conn.execute(
                "SELECT COUNT(*) FROM vector_feedback WHERE batch_id = ?",
                ("batch-724-clean",),
            ).fetchone()[0]
            assert n == 3
        finally:
            conn.close()
        assert prompt_blocks == []

    def test_unparseable_stores_feedback_block_not_rows(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [{"code": "G1", "label": "G1", "content": "body\nA = one\nB = two", "importance": 5}],
        )
        prompt_blocks: List[Dict[str, str]] = []
        agent_mod._capture_rubric_vector_feedback(
            task_key="grade_get",
            owner_task_key="grade_get",
            candidate_id="cand-1",
            batch_id="batch-724-raw",
            entity_type="candidate",
            index="0",
            perf={"status": "success", "vector_reviews": ["not-valid"]},
            debug=False,
            prompt_blocks=prompt_blocks,
            batch_size=1,
        )
        assert len(prompt_blocks) == 1
        assert prompt_blocks[0]["type"] == "FEEDBACK"
        rows = db.get_agent_data_by_batch("batch-724-raw", block_type="FEEDBACK")
        assert len(rows) == 1

    def test_non_success_skips_capture(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [{"code": "G1", "label": "G1", "content": "body\nA = one\nB = two", "importance": 5}],
        )
        prompt_blocks: List[Dict[str, str]] = []
        agent_mod._capture_rubric_vector_feedback(
            task_key="grade_get",
            owner_task_key="grade_get",
            candidate_id="cand-1",
            batch_id="batch-724-fail",
            entity_type="candidate",
            index=None,
            perf={"status": "failure", "vector_reviews": ["G1RACOVK"]},
            debug=False,
            prompt_blocks=prompt_blocks,
            batch_size=1,
        )
        assert prompt_blocks == []
        rows = db.get_agent_data_by_batch("batch-724-fail", block_type="FEEDBACK")
        assert rows == []


class TestAst809VectorFeedbackBatchMetadata:
    """AST-809: batch_id, batch_size, and completed_at on vector_feedback rows."""

    def test_capture_skips_insert_when_batch_id_missing(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [{"code": "G1", "label": "G1", "content": "body\nA = one\nB = two", "importance": 5}],
        )
        prompt_blocks: List[Dict[str, str]] = []
        agent_mod._capture_rubric_vector_feedback(
            task_key="grade_get",
            owner_task_key="grade_get",
            candidate_id="cand-1",
            batch_id="",
            entity_type="candidate",
            index=None,
            perf={"status": "success", "vector_reviews": ["G1RACOVK"]},
            debug=False,
            prompt_blocks=prompt_blocks,
            batch_size=5,
        )
        assert prompt_blocks == []

    def test_capture_persists_batch_metadata_on_rows(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [{"code": "G1", "label": "G1", "content": "body\nA = one\nB = two", "importance": 5}],
        )
        completed = "2026-06-25 14:30:00"
        agent_mod._capture_rubric_vector_feedback(
            task_key="grade_get",
            owner_task_key="grade_get",
            candidate_id="cand-1",
            batch_id="batch-809-meta",
            entity_type="candidate",
            index=None,
            perf={"status": "success", "vector_reviews": ["G1RACOVK"]},
            debug=False,
            prompt_blocks=[],
            batch_size=7,
            completed_at=completed,
        )
        rows = db.list_vector_feedback(candidate_id="cand-1", batch_id="batch-809-meta")
        assert len(rows) == 3
        assert all(r["batch_id"] == "batch-809-meta" for r in rows)
        assert all(r["batch_size"] == 7 for r in rows)
        assert all(r["completed_at"] == completed for r in rows)


class TestAst816VectorFeedbackCapture:
    """AST-816: normalize parse, UUID-backed expected codes, debug hydration."""

    def test_json_string_vector_reviews_persists_rows(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("evaluate_jd", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "evaluate_jd",
            [
                {"code": "CLR", "label": "Culture", "content": "c\nA = one", "importance": 5},
                {"code": "DOR", "label": "Domain", "content": "d\nA = one", "importance": 5},
            ],
        )
        agent_mod._capture_rubric_vector_feedback(
            task_key="evaluate_jd",
            owner_task_key="evaluate_jd",
            candidate_id="cand-1",
            batch_id="batch-816-json",
            entity_type="candidate",
            index=None,
            perf={
                "status": "success",
                "vector_reviews": '["CLRRACOVK", "DORRACOVK"]',
            },
            debug=False,
            prompt_blocks=[],
            batch_size=2,
        )
        rows = db.list_vector_feedback(candidate_id="cand-1", batch_id="batch-816-json")
        assert len(rows) == 6

    def test_debug_emits_diagnostic_on_parse_failure(
        self, seeded_db, caplog: pytest.LogCaptureFixture
    ) -> None:
        db = seeded_db
        db.save_agent_task("evaluate_jd", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "evaluate_jd",
            [{"code": "CLR", "label": "Culture", "content": "c\nA = one", "importance": 5}],
        )
        caplog.set_level("INFO")
        prompt_blocks: List[Dict[str, str]] = []
        agent_mod._capture_rubric_vector_feedback(
            task_key="evaluate_jd",
            owner_task_key="evaluate_jd",
            candidate_id="cand-1",
            batch_id="batch-816-diag",
            entity_type="candidate",
            index=None,
            perf={"status": "success", "vector_reviews": ["CLRRACOVK", "DORRACOVK"]},
            debug=True,
            prompt_blocks=prompt_blocks,
            batch_size=1,
        )
        combined = "\n".join(r.message for r in caplog.records)
        assert any(
            token in combined
            for token in ("reason=unknown_code", "reason=extra_codes", "reason=missing_codes")
        )
        assert "CLR Culture" in combined
        assert len(prompt_blocks) == 1


class TestAst820VectorFeedbackDebugTrace:
    """AST-820: debug-only pipeline trace and explicit early-return skip reasons."""

    def test_debug_skip_empty_batch_id(self, seeded_db, caplog: pytest.LogCaptureFixture) -> None:
        db = seeded_db
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [{"code": "G1", "label": "G1", "content": "body\nA = one", "importance": 5}],
        )
        caplog.set_level("INFO")
        agent_mod._capture_rubric_vector_feedback(
            task_key="grade_get",
            owner_task_key="grade_get",
            candidate_id="cand-1",
            batch_id="",
            entity_type="candidate",
            index=None,
            perf={"status": "success", "vector_reviews": ["G1RACOVK"]},
            debug=True,
            prompt_blocks=[],
            batch_size=1,
        )
        combined = "\n".join(r.message for r in caplog.records)
        assert "vector feedback capture skipped" in combined
        assert "skip reason=empty batch_id" in combined

    def test_debug_skip_empty_expected_codes(self, seeded_db, caplog: pytest.LogCaptureFixture) -> None:
        db = seeded_db
        db.save_agent_task("evaluate_jd", agent_id="a1", user_prompt="p")
        caplog.set_level("INFO")
        agent_mod._capture_rubric_vector_feedback(
            task_key="evaluate_jd",
            owner_task_key="evaluate_jd",
            candidate_id="cand-no-rubric",
            batch_id="batch-820-empty",
            entity_type="candidate",
            index=None,
            perf={"status": "success", "vector_reviews": ["CLRRACOVK"]},
            debug=True,
            prompt_blocks=[],
            batch_size=1,
        )
        combined = "\n".join(r.message for r in caplog.records)
        assert "skip reason=empty_expected_codes" in combined
        assert "candidate=cand-no-rubric" in combined

    def test_debug_emits_pipeline_trace_on_capture_start(
        self, seeded_db, caplog: pytest.LogCaptureFixture
    ) -> None:
        db = seeded_db
        db.save_agent_task("grade_get", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "grade_get",
            [{"code": "G1", "label": "G1", "content": "body\nA = one", "importance": 5}],
        )
        caplog.set_level("INFO")
        agent_mod._capture_rubric_vector_feedback(
            task_key="grade_get",
            owner_task_key="grade_get",
            candidate_id="cand-1",
            batch_id="batch-820-trace",
            entity_type="candidate",
            index=None,
            perf={"status": "success", "vector_reviews": ["G1RACOVK"]},
            debug=True,
            prompt_blocks=[],
            batch_size=1,
        )
        combined = "\n".join(r.message for r in caplog.records)
        assert "vector feedback capture start" in combined
        assert "vector_reviews trace candidate=cand-1" in combined
        assert "normalize -> 1 lines" in combined
        assert "diagnostic reason=ok" in combined

    @pytest.mark.asyncio
    async def test_do_task_debug_skip_when_candidate_id_missing(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        caplog.set_level("INFO")
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda task_key: _agent_rows())
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "agent_performance": {
                            "status": "success",
                            "vector_reviews": ["G1RACOVK"],
                        },
                        "agent_payload": "0|CRA2",
                    },
                    "api_response": _api_response("envelope"),
                    "timesheet": {},
                }
            ),
        )
        await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx={"candidate_data": {}, "batch_entities": _batch_entities("job-1")},
            debug=True,
        )
        combined = "\n".join(r.message for r in caplog.records)
        assert "vector feedback capture skipped" in combined
        assert "skip reason=missing owner=" in combined


class TestAst848DispatchChainDoTask:
    """AST-848: per-hop DB labels + terminal graduation inside do_task."""

    def _dispatch_chain_ctx(self, *, graduate: bool) -> Dict[str, Any]:
        return {
            "candidate_data": {"artifacts": {}},
            "batch_entities": _batch_entities("job-848"),
            "dispatch_trigger_state": cfg.BUILD_ARTIFACTS_BASE_STATE,
            "dispatch_chain_graduate_on_terminal": graduate,
        }

    @pytest.mark.asyncio
    async def test_writes_hop_label_without_graduation_when_disabled(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
    ) -> None:
        write_hop = MagicMock(return_value=f"{cfg.BUILD_ARTIFACTS_BASE_STATE}.anticipate_scan")
        graduate = MagicMock()
        monkeypatch.setattr("src.core.tracker.write_job_dispatch_hop_label", write_hop)
        monkeypatch.setattr("src.core.tracker.graduate_job_from_dispatch_chain", graduate)
        monkeypatch.setattr(
            "src.core.tracker.get_job",
            lambda jid: {"astral_job_id": jid, "state": cfg.BUILD_ARTIFACTS_BASE_STATE},
        )
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows(run_next=""))
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"title": "Role", "company": "Co"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "anticipate_scan",
            index="job-848",
            ctx=self._dispatch_chain_ctx(graduate=False),
        )
        assert out["success"] is True
        write_hop.assert_called_once_with(
            "job-848", cfg.BUILD_ARTIFACTS_BASE_STATE, "anticipate_scan",
        )
        graduate.assert_not_called()

    @pytest.mark.asyncio
    async def test_graduates_on_terminal_hop_when_enabled(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
    ) -> None:
        write_hop = MagicMock(return_value=f"{cfg.BUILD_ARTIFACTS_BASE_STATE}.anticipate_scan")
        graduate = MagicMock(return_value="CANDIDATE_REVIEW")
        monkeypatch.setattr("src.core.tracker.write_job_dispatch_hop_label", write_hop)
        monkeypatch.setattr("src.core.tracker.graduate_job_from_dispatch_chain", graduate)
        monkeypatch.setattr(
            "src.core.tracker.get_job",
            lambda jid: {"astral_job_id": jid, "state": cfg.BUILD_ARTIFACTS_BASE_STATE},
        )
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows(run_next=""))
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {"title": "Role", "company": "Co"},
                    "api_response": _api_response(),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "anticipate_scan",
            index="job-848",
            ctx=self._dispatch_chain_ctx(graduate=True),
        )
        assert out["success"] is True
        graduate.assert_called_once_with("job-848", cfg.BUILD_ARTIFACTS_BASE_STATE)

    @pytest.mark.asyncio
    async def test_hard_failure_transitions_error_build_artifacts(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
        stub_agent_storage: Dict[str, MagicMock],
    ) -> None:
        transition = MagicMock()
        monkeypatch.setattr("src.core.tracker.transition_job_state", transition)
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda key: _agent_rows(run_next=""))
        _patch_strict_batch_anthropic(monkeypatch)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(
                return_value={
                    "success": False,
                    "error": "Missing candidate_data for job job-848",
                    "api_response": _api_response("fail"),
                    "timesheet": {},
                }
            ),
        )
        out = await agent_mod.do_task(
            "anticipate_scan",
            index="job-848",
            ctx=self._dispatch_chain_ctx(graduate=True),
        )
        assert out["success"] is False
        transition.assert_called_once_with(["job-848"], cfg.ERROR_BUILD_ARTIFACTS_STATE)

    def test_dispatch_chain_ctx_reads_trigger_and_graduate_flag(self) -> None:
        trigger, graduate = agent_mod._dispatch_chain_ctx({
            "dispatch_trigger_state": cfg.BUILD_ARTIFACTS_BASE_STATE,
            "dispatch_chain_graduate_on_terminal": True,
        })
        assert trigger == cfg.BUILD_ARTIFACTS_BASE_STATE
        assert graduate is True

    def test_should_write_hop_label_only_for_graduation_map_trigger(self) -> None:
        assert agent_mod._should_write_dispatch_hop_label(
            entity_type="job",
            index="job-1",
            ctx={"dispatch_trigger_state": cfg.BUILD_ARTIFACTS_BASE_STATE},
            trigger_state=cfg.BUILD_ARTIFACTS_BASE_STATE,
        )
        assert not agent_mod._should_write_dispatch_hop_label(
            entity_type="job",
            index="job-1",
            ctx={},
            trigger_state="UNKNOWN",
        )
