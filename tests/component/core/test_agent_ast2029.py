"""AST-2029: stored NO_CACHE (live content) and RESPONSE rows carry real entity ids; the wire stays positional."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional

import pytest

from src.core import agent as agent_mod
from src.utils import formatting as fmt
from tests.component.core.test_agent import _agent_rows, _api_response


@pytest.fixture
def batch_token() -> Any:
    # A live batch id → do_task's _should_store gate opens.
    token = agent_mod.log_batch_id.set("batch-2029")
    yield token
    agent_mod.log_batch_id.reset(token)


@pytest.fixture
def saved(monkeypatch: pytest.MonkeyPatch) -> List[Dict[str, Any]]:
    # Real store helpers; only the DB write is captured.
    rows: List[Dict[str, Any]] = []
    monkeypatch.setattr(agent_mod, "save_agent_data", lambda **kw: rows.append(kw))
    return rows


def _blocks(rows: List[Dict[str, Any]], block_type: str) -> List[str]:
    return [r["block_data"] for r in rows if r["block_type"] == block_type]


# Branches: seven-segment + legacy cache_content both hydrate live only (D4); no ids → stored as-is.
class TestAst2029StorePromptBlocks:
    def test_seven_segment_hydrates_live_not_nocache(self, saved: List[Dict[str, Any]]) -> None:
        agent_mod._store_prompt_blocks(
            "job", "evaluate_jd", "b1", "sys",
            caches_resolved_four=("ca", None, None, None),
            nocache_content="000: prompt text",
            live_content="000: alpha\n001: beta",
            entity_ids=["job-a", "job-b"],
        )
        # Prompt-text NO_CACHE first, live NO_CACHE second (segment order in _store_prompt_blocks).
        assert _blocks(saved, "NO_CACHE") == ["000: prompt text", "[entity_id=job-a]: alpha\n[entity_id=job-b]: beta"]

    def test_legacy_cache_content_hydrates_live(self, saved: List[Dict[str, Any]]) -> None:
        agent_mod._store_prompt_blocks(
            "job", "evaluate_jd", "b2", "sys",
            cache_content="ca",
            live_content="[index=000]: alpha",
            entity_ids=["job-a"],
        )
        assert _blocks(saved, "NO_CACHE") == ["[entity_id=job-a]: alpha"]

    def test_without_ids_live_stored_positional(self, saved: List[Dict[str, Any]]) -> None:
        agent_mod._store_prompt_blocks(
            "job", "evaluate_jd", "b3", "sys",
            caches_resolved_four=("ca", None, None, None),
            live_content="000: alpha",
        )
        assert _blocks(saved, "NO_CACHE") == ["000: alpha"]


# Branches: hydrated row + id hash over hydrated text; no ids → unchanged.
class TestAst2029StoreResponseBlock:
    def test_failed_raw_response_hydrated_and_hashed(self, saved: List[Dict[str, Any]]) -> None:
        rid = agent_mod._store_response_block(
            "job", "evaluate_jd", "b4", "000|DTA5\n001|GCA4", index="job-a", entity_ids=["job-a", "job-b"],
        )
        want = "[entity_id=job-a]|DTA5\n[entity_id=job-b]|GCA4"
        assert _blocks(saved, "RESPONSE") == [want]
        digest = hashlib.sha256(f"b4:RESPONSE:job-a:{want}".encode()).hexdigest()[:16]
        assert rid == f"b4-response-{digest}"

    def test_without_ids_response_unchanged(self, saved: List[Dict[str, Any]]) -> None:
        agent_mod._store_response_block("job", "evaluate_jd", "b5", "000|DTA5")
        assert _blocks(saved, "RESPONSE") == ["000|DTA5"]


class TestAst2029DoTaskStoresIds:
    """End to end through do_task: stored rows carry ids (AC1–AC3), wire stays positional."""

    _FAIL_RAW = "000|DTA5\n001|GCA4\n002|RCA3"

    def _run_setup(self, monkeypatch: pytest.MonkeyPatch, result: Dict[str, Any]) -> List[Any]:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda _key: _agent_rows())
        # Past the server-key gate — storage, not key selection, is under test.
        monkeypatch.setattr(agent_mod, "_candidate_server_key", lambda ctx, cid, server_id: "sk-test")
        monkeypatch.setattr(agent_mod.database, "update_dispatch_ledger", lambda *_a, **_k: None)
        wire: List[Any] = []

        async def send(user_blocks: Any, **kw: Any) -> Dict[str, Any]:
            wire.append({"user": user_blocks, "system": kw.get("system_blocks")})
            return dict(result)

        monkeypatch.setattr(agent_mod, "_send_to_server", send)
        return wire

    def _failed(self, raw: str) -> Dict[str, Any]:
        return {"success": False, "error": "boom", "api_response": _api_response(raw), "timesheet": {}}

    @staticmethod
    def _ctx(entities: List[Any]) -> Dict[str, Any]:
        return {"astral_candidate_id": "somerset", "candidate_data": {}, "batch_entities": entities}

    async def _do(self, task: str, live: str, entities: List[Any], index: Optional[str] = None) -> Dict[str, Any]:
        return await agent_mod.do_task(task, live_content=live, index=index, ctx=self._ctx(entities))

    async def test_ac1_stored_with_ids_wire_positional(
        self, monkeypatch: pytest.MonkeyPatch, batch_token: Any, saved: List[Dict[str, Any]],
    ) -> None:
        wire = self._run_setup(monkeypatch, self._failed(self._FAIL_RAW))
        ents = [{"astral_job_id": i} for i in ("job-a", "job-b", "job-c")]
        await self._do("evaluate_jd", "000: alpha\n001: beta\n002: gamma", ents)
        live_row = [b for b in _blocks(saved, "NO_CACHE") if "alpha" in b]
        assert live_row == ["[entity_id=job-a]: alpha\n[entity_id=job-b]: beta\n[entity_id=job-c]: gamma"]
        sent = json.dumps(wire)
        assert "000: alpha" in sent and "001: beta" in sent
        assert "job-a" not in sent and "entity_id" not in sent

    async def test_ac2_enumerate_form_stored_with_ids(
        self, monkeypatch: pytest.MonkeyPatch, batch_token: Any, saved: List[Dict[str, Any]],
    ) -> None:
        wire = self._run_setup(monkeypatch, self._failed(self._FAIL_RAW))
        ents = [{"astral_job_id": "job-a"}, {"astral_job_id": "job-b"}]
        await self._do("evaluate_jd", "[index=000]: alpha\n[index=001]: beta", ents)
        live_row = [b for b in _blocks(saved, "NO_CACHE") if "alpha" in b]
        assert live_row == ["[entity_id=job-a]: alpha\n[entity_id=job-b]: beta"]
        assert "[index=000]: alpha" in json.dumps(wire)

    async def test_ac3_failed_response_stored_with_ids(
        self, monkeypatch: pytest.MonkeyPatch, batch_token: Any, saved: List[Dict[str, Any]],
    ) -> None:
        self._run_setup(monkeypatch, self._failed("000|DTA5\n001|GCA4"))
        ents = [{"astral_job_id": "job-a"}, {"astral_job_id": "job-b"}]
        out = await self._do("evaluate_jd", "000: alpha\n001: beta", ents)
        assert out["success"] is False
        (resp,) = _blocks(saved, "RESPONSE")
        assert "[entity_id=job-a]|DTA5" in resp and "[entity_id=job-b]|GCA4" in resp
        assert "000|" not in resp and "001|" not in resp

    async def test_company_entities_use_company_id(
        self, monkeypatch: pytest.MonkeyPatch, batch_token: Any, saved: List[Dict[str, Any]],
    ) -> None:
        self._run_setup(monkeypatch, self._failed("000|PCA4"))
        await self._do("prefilter_company", "000: acme", [{"company_id": 42, "astral_job_id": "wrong"}])
        assert "[entity_id=42]: acme" in _blocks(saved, "NO_CACHE")
        assert "[entity_id=42]|PCA4" in _blocks(saved, "RESPONSE")[0]

    @pytest.mark.parametrize(
        "entities",
        [
            pytest.param([{"astral_job_id": "job-a"}, {"astral_job_id": ""}], id="one_missing_id"),
            pytest.param([{"astral_job_id": "job-a"}, "job-b"], id="non_dict_entity"),
            pytest.param([], id="no_entities"),
        ],
    )
    async def test_d3_incomplete_ids_store_positional(
        self, monkeypatch: pytest.MonkeyPatch, batch_token: Any, saved: List[Dict[str, Any]], entities: List[Any],
    ) -> None:
        # D3: all-or-nothing — a partial mapping would mislabel rows.
        self._run_setup(monkeypatch, self._failed("000|DTA5\n001|GCA4"))
        await self._do("evaluate_jd", "000: alpha\n001: beta", entities)
        assert "000: alpha\n001: beta" in _blocks(saved, "NO_CACHE")
        assert "entity_id" not in _blocks(saved, "RESPONSE")[0]

    async def test_success_response_splits_by_real_id(
        self, monkeypatch: pytest.MonkeyPatch, batch_token: Any, saved: List[Dict[str, Any]],
    ) -> None:
        # Success RESPONSE is decoded JSON already keyed by ids; hydrate is a no-op, split keys it by id.
        ok = {
            "success": True,
            "parsed_response": {"agent_payload": "0|CRA2"},
            "api_response": _api_response("ok"),
            "timesheet": {},
        }
        self._run_setup(monkeypatch, ok)
        out = await self._do("evaluate_jd", "000: alpha", [{"astral_job_id": "job-a"}], index="job-a")
        assert out["success"] is True
        (resp,) = _blocks(saved, "RESPONSE")
        assert list(fmt.split_entity_segments(resp)) == ["job-a"]
