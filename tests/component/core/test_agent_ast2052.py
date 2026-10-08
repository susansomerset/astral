"""AST-2052: get_agent_data(entity_id=X) reads like one Each-mode call for X (envelope + preamble kept, blanks omitted)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

import pytest

from src.core import agent as agent_mod

_JSON_RESP = '{"jobs":[{"astral_job_id":"A","g":1},{"astral_job_id":"B","g":2}],"agent_performance":{"status":"ok"}}'
_FAIL_RESP = 'Provider failed: x\n\n--- model response ---\n{"agent_payload":"[entity_id=A]|DTA5\\n[entity_id=B]|GCA4"}'
_FAIL_PREAMBLE = 'Provider failed: x\n\n--- model response ---\n{"agent_payload":"'

# Plan § Bug: AST-2052 ## Repro fixture, verbatim.
_REPRO_ROWS: List[Dict[str, Any]] = [
    {"block_type": "SYSTEM", "block_data": "sys"},
    {"block_type": "CACHE_A", "block_data": "cache a"},
    {"block_type": "CACHE_C", "block_data": "   "},
    {"block_type": "NO_CACHE", "block_data": "Jobs to grade:\n[entity_id=A]: jd a\n[entity_id=B]: jd b"},
    {"block_type": "TASK", "block_data": "grade them"},
    {"block_type": "RESPONSE", "block_data": _JSON_RESP},
    {"block_type": "RESPONSE", "block_data": _FAIL_RESP},
]


def _read(monkeypatch: pytest.MonkeyPatch, rows: List[Dict[str, Any]], entity_id: Any) -> List[Tuple[str, Any]]:
    monkeypatch.setattr(agent_mod, "get_agent_data_by_batch", lambda batch_id, block_type: rows)
    return [(r["block_type"], r["block_data"]) for r in agent_mod.get_agent_data("b1", entity_id=entity_id)]


class TestAst2052EntityCallView:
    def test_bug_repro_entity_read_is_one_each_mode_call(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # [bug-repro] red pre-fix: bare segments (preamble / JSON envelope lost) and a blank CACHE_C tab.
        assert _read(monkeypatch, _REPRO_ROWS, "B") == [
            ("SYSTEM", "sys"),
            ("CACHE_A", "cache a"),
            ("NO_CACHE", "Jobs to grade:\n[entity_id=B]: jd b"),
            ("TASK", "grade them"),
            ("RESPONSE", json.dumps({"jobs": [{"astral_job_id": "B", "g": 2}], "agent_performance": {"status": "ok"}})),
            ("RESPONSE", _FAIL_PREAMBLE + '[entity_id=B]|GCA4"}'),
        ]

    def test_non_last_entity_keeps_opener_not_closing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # D2-2052: the envelope's closing "} belongs to the last segment; no suffix heuristic.
        got = dict(_read(monkeypatch, [{"block_type": "RESPONSE", "block_data": _FAIL_RESP}], "A"))
        assert got == {"RESPONSE": _FAIL_PREAMBLE + "[entity_id=A]|DTA5"}

    def test_companies_envelope_filtered_with_numeric_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # companies[] preferred over jobs[]; id compared as str (company_id may be stored as int).
        raw = json.dumps({"companies": [{"company_id": 7, "g": "A"}, {"company_id": 8, "g": "B"}], "jobs": [], "note": "n"})
        got = dict(_read(monkeypatch, [{"block_type": "RESPONSE", "block_data": raw}], "7"))
        assert got == {"RESPONSE": json.dumps({"companies": [{"company_id": 7, "g": "A"}], "jobs": [], "note": "n"})}

    def test_blank_rows_omitted_in_entity_view(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [
            {"block_type": "SYSTEM", "block_data": "sys"},
            {"block_type": "CACHE_B", "block_data": None},
            {"block_type": "CACHE_C", "block_data": "  \n "},
            {"block_type": "NO_CACHE", "block_data": "\n\t"},
            {"block_type": "TASK", "block_data": ""},
        ]
        assert _read(monkeypatch, rows, "B") == [("SYSTEM", "sys")]


# Guards — green before and after the fix (What must still hold).
class TestAst2052StillHolds:
    def test_other_chunk_dropped_and_legacy_whole(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-2030 AC5 / AC7: other-ids-only rows dropped; non-blank legacy positional row whole.
        rows = [
            {"block_type": "RESPONSE", "block_data": '{"jobs":[{"astral_job_id":"D"}]}'},
            {"block_type": "NO_CACHE", "block_data": "[entity_id=D]: jd d"},
            {"block_type": "TASK", "block_data": "000: old\n001: older"},
        ]
        assert _read(monkeypatch, rows, "B") == [("TASK", "000: old\n001: older")]

    def test_no_entity_id_batch_view_byte_identical(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Parent §7 / AC9: batch-wide read returns the stored rows untouched, blank rows included.
        monkeypatch.setattr(agent_mod, "get_agent_data_by_batch", lambda batch_id, block_type: _REPRO_ROWS)
        assert agent_mod.get_agent_data("b1") is _REPRO_ROWS

    def test_story_keeps_bare_slice(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-2030 AC6: the agent story still shows the bare per-entity item, not the call envelope.
        monkeypatch.setattr(
            agent_mod.database, "list_entity_latest_agent_refs",
            lambda et, eid: [{"task_key": "analysis_upshot", "prompt_blocks": [{"type": "RESPONSE", "id": "r1"}]}],
        )
        monkeypatch.setattr(agent_mod, "_get_agent_data_row", lambda bid: {"block_data": _JSON_RESP})
        monkeypatch.setattr(agent_mod, "get_agent_task", lambda _k: None)
        (entry,) = agent_mod.get_entity_agent_story({"astral_job_id": "B"})
        assert entry["blocks"][0]["content"] == json.dumps({"astral_job_id": "B", "g": 2}, indent=2)
