"""AST-2030: agent-data read and agent story cut NO_CACHE / TASK / RESPONSE to one entity."""

from __future__ import annotations

import json
from typing import Any, Dict, List

import pytest

from src.core import agent as agent_mod
from src.utils.config import TASK_CONFIG
from src.utils.formatting import hydrate_entity_labels

# Stored text as AST-2029 writes it: chunk 1 = [A,B,C], chunk 2 = [D,E] in the same batch.
_LIVE_1 = hydrate_entity_labels("000: alpha\n001: beta\n002: gamma", ["job-a", "job-b", "job-c"])
_RESP_1 = hydrate_entity_labels("000|DTA5\n001|GCA4\n002|RCA3", ["job-a", "job-b", "job-c"])
_LIVE_2 = hydrate_entity_labels("000: delta\n001: epsilon", ["job-d", "job-e"])
_RESP_2 = hydrate_entity_labels("000|DTA1\n001|GCA2", ["job-d", "job-e"])
_LEGACY = "000: old one\n001: old two"


# Branches: SYSTEM/CACHE pass through; tagged row sliced; other chunk dropped; untagged (legacy / shared
# prompt) whole; empty block_data whole; no entity_id → rows untouched.
class TestAst2030GetAgentDataSlice:
    _ROWS: List[Dict[str, Any]] = [
        {"block_type": "SYSTEM", "block_data": "sys"},
        {"block_type": "CACHE_A", "block_data": "000: cached rubric"},
        {"block_type": "NO_CACHE", "block_data": "shared prompt text"},
        {"block_type": "NO_CACHE", "block_data": _LIVE_1},
        {"block_type": "RESPONSE", "block_data": _RESP_1},
        {"block_type": "NO_CACHE", "block_data": _LIVE_2},
        {"block_type": "RESPONSE", "block_data": _RESP_2},
        {"block_type": "TASK", "block_data": _LEGACY},
        {"block_type": "TASK", "block_data": None},
    ]

    @pytest.fixture(autouse=True)
    def _rows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(agent_mod, "get_agent_data_by_batch", lambda batch_id, block_type: self._ROWS)

    def test_ac4_ac5_ac7_entity_read(self) -> None:
        out = [(r["block_type"], r["block_data"]) for r in agent_mod.get_agent_data("b1", entity_id="job-b")]
        assert out == [
            ("SYSTEM", "sys"),
            ("CACHE_A", "000: cached rubric"),  # shared prompt slots never sliced
            ("NO_CACHE", "shared prompt text"),  # D6: untagged prompt NO_CACHE whole
            ("NO_CACHE", "[entity_id=job-b]: beta"),  # AC4
            ("RESPONSE", "[entity_id=job-b]|GCA4"),
            ("TASK", _LEGACY),  # AC7: legacy positional whole
            ("TASK", ""),
        ]
        # AC5: nothing from chunk 2, nothing of A / C.
        text = json.dumps(out)
        assert not any(s in text for s in ("delta", "epsilon", "alpha", "gamma", "DTA1"))

    def test_without_entity_id_rows_untouched(self) -> None:
        assert agent_mod.get_agent_data("b1") == self._ROWS

    def test_source_rows_not_mutated(self) -> None:
        agent_mod.get_agent_data("b1", entity_id="job-b")
        assert self._ROWS[3]["block_data"] == _LIVE_1


# Branches: NO_CACHE + RESPONSE sliced on every task (unscored too); other-chunk block → ""; legacy whole;
# TASK / SYSTEM never sliced in the story; company via short_name; candidate (no ref id) whole (D5).
class TestAst2030AgentStorySlice:
    _UNSCORED_JOB_TASK = next(k for k, c in TASK_CONFIG.items() if c.get("entity_type") == "job" and not c.get("scored"))
    _DATA = {
        "sys": "sys", "task": "[entity_id=job-a]: task", "live1": _LIVE_1, "resp1": _RESP_1,
        "live2": _LIVE_2, "legacy": _LEGACY,
    }

    def _story(self, monkeypatch: pytest.MonkeyPatch, entity: Dict[str, Any], refs: List[str]) -> Dict[str, str]:
        types = {"sys": "SYSTEM", "task": "TASK", "resp1": "RESPONSE"}
        blocks = [{"type": types.get(r, "NO_CACHE"), "id": r} for r in refs]
        monkeypatch.setattr(
            agent_mod.database, "list_entity_latest_agent_refs",
            lambda et, eid: [{"task_key": self._UNSCORED_JOB_TASK, "prompt_blocks": blocks}],
        )
        monkeypatch.setattr(agent_mod, "_get_agent_data_row", lambda bid: {"block_data": self._DATA[bid]})
        monkeypatch.setattr(agent_mod, "get_agent_task", lambda _k: None)
        (entry,) = agent_mod.get_entity_agent_story(entity)
        return {b["id"]: b["content"] for b in entry["blocks"]}

    def test_ac6_ac7_unscored_job_story(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert not TASK_CONFIG[self._UNSCORED_JOB_TASK].get("scored")
        got = self._story(monkeypatch, {"astral_job_id": "job-b"}, ["sys", "task", "live1", "resp1", "live2", "legacy"])
        assert got == {
            "sys": "sys",
            "task": "[entity_id=job-a]: task",  # story slices NO_CACHE / RESPONSE only
            "live1": "[entity_id=job-b]: beta",  # AC6
            "resp1": "[entity_id=job-b]|GCA4",
            "live2": "",  # D2: other chunk's block kept with empty content
            "legacy": _LEGACY,  # AC7
        }

    def test_company_story_slices_by_short_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._DATA["co"] = hydrate_entity_labels("000: acme row\n001: zeta row", ["acme", "zeta"])
        try:
            assert self._story(monkeypatch, {"short_name": "acme"}, ["co"]) == {"co": "[entity_id=acme]: acme row"}
        finally:
            del self._DATA["co"]

    def test_candidate_story_stays_whole(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert self._story(monkeypatch, {"astral_candidate_id": "somerset"}, ["live1"]) == {"live1": _LIVE_1}
