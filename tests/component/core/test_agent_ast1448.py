"""AST-1448: persist assembled prompt before the provider await."""

from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import agent as agent_mod

from tests.component.core.test_agent import _agent_rows, _api_response, _draft_job_resume_ctx


@pytest.fixture
def batch_token() -> Any:
    token = agent_mod.log_batch_id.set("batch-1")
    yield token
    agent_mod.log_batch_id.reset(token)


class TestAst1448PersistPromptBeforeProvider:
    """Prompt rows land before the provider await; RESPONSE only after return."""

    _OK = {
        "success": True,
        "parsed_response": {"agent_payload": "0|CRA2"},
        "api_response": _api_response("ok"),
        "timesheet": {},
    }

    def _patch_prompts(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda _key: _agent_rows())

    def _timeline_helpers(self, monkeypatch: pytest.MonkeyPatch) -> List[str]:
        events: List[str] = []

        def store_prompt(*_a: Any, **_k: Any) -> List[Dict[str, str]]:
            events.append("prompt")
            return []

        def store_response(*_a: Any, **_k: Any) -> str:
            events.append("response")
            return "resp-1"

        monkeypatch.setattr(agent_mod, "_store_prompt_blocks", store_prompt)
        monkeypatch.setattr(agent_mod, "_store_response_block", store_response)
        return events

    async def test_do_task_stores_prompt_before_provider_and_response_after(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        self._patch_prompts(monkeypatch)
        events = self._timeline_helpers(monkeypatch)

        async def send(*_a: Any, **_k: Any) -> Dict[str, Any]:
            events.append("provider")
            return dict(self._OK)

        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_draft_job_resume_ctx(),
        )
        assert out["success"] is True
        assert events[:2] == ["prompt", "provider"]
        assert events.index("prompt") < events.index("provider") < events.index("response")

    async def test_do_task_provider_raise_keeps_prompt_omits_response(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        self._patch_prompts(monkeypatch)
        events = self._timeline_helpers(monkeypatch)

        async def send(*_a: Any, **_k: Any) -> Dict[str, Any]:
            events.append("provider")
            raise RuntimeError("killed mid-call")

        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)
        with pytest.raises(RuntimeError, match="killed mid-call"):
            await agent_mod.do_task(
                "evaluate_jd",
                index="job-1",
                ctx=_draft_job_resume_ctx(),
            )
        assert events == ["prompt", "provider"]

    async def test_do_task_storage_off_skips_prompt_and_response(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        self._patch_prompts(monkeypatch)
        events = self._timeline_helpers(monkeypatch)

        async def send(*_a: Any, **_k: Any) -> Dict[str, Any]:
            events.append("provider")
            return dict(self._OK)

        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_draft_job_resume_ctx(),
            store_agent_data=False,
        )
        assert out["success"] is True
        assert events == ["provider"]

    async def test_do_task_prompt_persist_failure_still_calls_provider(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        self._patch_prompts(monkeypatch)
        events: List[str] = []

        def boom(*_a: Any, **_k: Any) -> List[Dict[str, str]]:
            events.append("prompt-fail")
            raise RuntimeError("db down")

        async def send(*_a: Any, **_k: Any) -> Dict[str, Any]:
            events.append("provider")
            return dict(self._OK)

        monkeypatch.setattr(agent_mod, "_store_prompt_blocks", boom)
        monkeypatch.setattr(
            agent_mod,
            "_store_response_block",
            lambda *_a, **_k: events.append("response") or "r",
        )
        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)
        out = await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_draft_job_resume_ctx(),
        )
        assert out["success"] is True
        assert events[0] == "prompt-fail"
        assert "provider" in events

    async def test_do_task_debug_emits_prompt_found_recorded_before_provider(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        self._patch_prompts(monkeypatch)
        events: List[str] = []

        class _Dbg:
            def debug_index(self, **kwargs: Any) -> None:
                if kwargs.get("func") == "_store_prompt_blocks":
                    events.append(f"prompt-debug:{kwargs.get('outcome')}")

            def debug_detail(self, msg: str = "") -> None:
                if msg.startswith("found block_type="):
                    events.append("prompt-found")
                if "recorded outcome=" in msg:
                    events.append("prompt-recorded")

            def debug_detail_block(self, *_a: Any, **_k: Any) -> None:
                return None

        monkeypatch.setattr(
            agent_mod,
            "get_logger",
            lambda *_a, **_k: _Dbg() if _k.get("debug_flag") else MagicMock(),
        )
        monkeypatch.setattr(
            agent_mod,
            "save_agent_data",
            lambda **kwargs: {
                "outcome": "inserted",
                "agent_data_id": kwargs.get("agent_data_id") or "id",
                "ref_agent_data_id": None,
            },
        )

        async def send(*_a: Any, **_k: Any) -> Dict[str, Any]:
            events.append("provider")
            return dict(self._OK)

        monkeypatch.setattr(agent_mod, "send_to_anthropic", send)
        await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_draft_job_resume_ctx(),
            debug=True,
        )
        assert "prompt-found" in events
        assert events.index("prompt-found") < events.index("provider")
        assert any(
            e.startswith("prompt-debug:") for e in events if events.index(e) < events.index("provider")
        )

    async def test_do_task_debug_false_skips_persist_contract_lines(
        self,
        monkeypatch: pytest.MonkeyPatch,
        batch_token: Any,
    ) -> None:
        self._patch_prompts(monkeypatch)
        spy = MagicMock()
        monkeypatch.setattr(agent_mod, "get_logger", spy)
        monkeypatch.setattr(
            agent_mod,
            "save_agent_data",
            lambda **kwargs: {
                "outcome": "inserted",
                "agent_data_id": kwargs.get("agent_data_id") or "id",
                "ref_agent_data_id": None,
            },
        )
        monkeypatch.setattr(agent_mod, "send_to_anthropic", AsyncMock(return_value=dict(self._OK)))
        await agent_mod.do_task(
            "evaluate_jd",
            index="job-1",
            ctx=_draft_job_resume_ctx(),
            debug=False,
        )
        assert not any(c.kwargs.get("debug_flag") for c in spy.call_args_list)

    async def test_do_task_later_success_does_not_rewrite_interrupted_batch_prompts(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self._patch_prompts(monkeypatch)
        prompt_batches: List[str] = []
        response_batches: List[str] = []

        def store_prompt(*_a: Any, **kwargs: Any) -> List[Dict[str, str]]:
            prompt_batches.append(str(kwargs.get("batch_id")))
            return []

        def store_response(*args: Any, **kwargs: Any) -> str:
            batch = kwargs.get("batch_id") or (args[2] if len(args) > 2 else "")
            response_batches.append(str(batch))
            return "resp"

        monkeypatch.setattr(agent_mod, "_store_prompt_blocks", store_prompt)
        monkeypatch.setattr(agent_mod, "_store_response_block", store_response)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(side_effect=RuntimeError("killed")),
        )
        t1 = agent_mod.log_batch_id.set("batch-killed")
        try:
            with pytest.raises(RuntimeError, match="killed"):
                await agent_mod.do_task(
                    "evaluate_jd",
                    index="job-1",
                    ctx=_draft_job_resume_ctx(),
                )
        finally:
            agent_mod.log_batch_id.reset(t1)

        monkeypatch.setattr(agent_mod, "send_to_anthropic", AsyncMock(return_value=dict(self._OK)))
        t2 = agent_mod.log_batch_id.set("batch-ok")
        try:
            out = await agent_mod.do_task(
                "evaluate_jd",
                index="job-1",
                ctx=_draft_job_resume_ctx(),
            )
        finally:
            agent_mod.log_batch_id.reset(t2)
        assert out["success"] is True
        assert prompt_batches == ["batch-killed", "batch-ok"]
        assert "batch-killed" not in response_batches
        assert "batch-ok" in response_batches

    async def test_prompt_only_batch_is_not_latest_ref(
        self,
        sqlite_in_memory: Any,
    ) -> None:
        db = sqlite_in_memory
        if not hasattr(db, "save_job") or not hasattr(db, "list_entity_latest_agent_refs"):
            pytest.skip("database helpers missing on sqlite_in_memory")
        db.save_job("job-1448", company="acme", state="NEW")
        db.save_agent_data(
            agent_data_id="kill-sys",
            entity_type="job",
            task_key="evaluate_jd",
            batch_id="batch-killed",
            block_type="SYSTEM",
            block_data="prompt-only",
            token_size=1,
            created_at="2026-08-19 00:00:00",
            entity_id="job-1448",
        )
        refs = db.list_entity_latest_agent_refs("job", "job-1448")
        assert refs == []
        db.save_agent_data(
            agent_data_id="ok-resp",
            entity_type="job",
            task_key="evaluate_jd",
            batch_id="batch-ok",
            block_type="RESPONSE",
            block_data="done",
            token_size=1,
            created_at="2026-08-19 01:00:00",
            entity_id="job-1448",
        )
        refs = db.list_entity_latest_agent_refs("job", "job-1448")
        assert len(refs) == 1
        assert refs[0]["batch_id"] == "batch-ok"

    async def test_workbench_stores_prompt_before_run_adhoc(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        events: List[str] = []
        monkeypatch.setattr(agent_mod.database, "save_dispatch_ledger", lambda *_a, **_k: None)
        monkeypatch.setattr(agent_mod.database, "update_dispatch_ledger", lambda *_a, **_k: None)
        monkeypatch.setattr(agent_mod, "compute_batch_cost", lambda _b: 0)

        def store_prompt(*_a: Any, **_k: Any) -> List[Dict[str, str]]:
            events.append("prompt")
            return []

        def store_response(*_a: Any, **_k: Any) -> str:
            events.append("response")
            return "r"

        monkeypatch.setattr(agent_mod, "_store_prompt_blocks", store_prompt)
        monkeypatch.setattr(agent_mod, "_store_response_block", store_response)

        async def run_adhoc(**_k: Any) -> Dict[str, Any]:
            events.append("provider")
            return {"success": True, "parsed_response": {"agent_payload": "ok"}, "timesheet": {}}

        monkeypatch.setattr(agent_mod, "run_adhoc", run_adhoc)
        out = await agent_mod.run_adhoc_workbench_test(
            workbench_task_key="evaluate_jd",
            candidate_id="c1",
            entity_id="j1",
            system_content="sys",
            user_content="usr",
        )
        assert out["success"] is True
        assert events[:2] == ["prompt", "provider"]
        assert events.index("provider") < events.index("response")

    async def test_workbench_raise_keeps_prompt_omits_response(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        events: List[str] = []
        monkeypatch.setattr(agent_mod.database, "save_dispatch_ledger", lambda *_a, **_k: None)
        monkeypatch.setattr(agent_mod.database, "update_dispatch_ledger", lambda *_a, **_k: None)
        monkeypatch.setattr(agent_mod, "compute_batch_cost", lambda _b: 0)
        monkeypatch.setattr(
            agent_mod,
            "_store_prompt_blocks",
            lambda *_a, **_k: events.append("prompt") or [],
        )
        monkeypatch.setattr(
            agent_mod,
            "_store_response_block",
            lambda *_a, **_k: events.append("response") or "r",
        )

        async def boom(**_k: Any) -> Dict[str, Any]:
            events.append("provider")
            raise RuntimeError("boom")

        monkeypatch.setattr(agent_mod, "run_adhoc", boom)
        with pytest.raises(RuntimeError, match="boom"):
            await agent_mod.run_adhoc_workbench_test(
                workbench_task_key="evaluate_jd",
                candidate_id="c1",
            )
        assert events == ["prompt", "provider"]

    async def test_bare_run_adhoc_does_not_store_agent_data(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        store_prompt = MagicMock()
        store_response = MagicMock()
        monkeypatch.setattr(agent_mod, "_store_prompt_blocks", store_prompt)
        monkeypatch.setattr(agent_mod, "_store_response_block", store_response)
        monkeypatch.setattr(
            agent_mod,
            "send_to_anthropic",
            AsyncMock(return_value={"success": True, "parsed_response": "ok", "timesheet": {}}),
        )
        out = await agent_mod.run_adhoc(
            system_content="sys",
            user_content="usr",
            model_code="claude-haiku-4-5",
        )
        assert store_prompt.call_count == 0
        assert store_response.call_count == 0
        assert out["success"] is True
