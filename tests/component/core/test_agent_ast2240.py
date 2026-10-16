"""AST-2240 — do_task / Ad Hoc provider hand-off via astral_agent.submit."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from src.core import agent as agent_mod
from src.external.astral_agent import AstralAgentError

_REPO = Path(__file__).resolve().parents[3]


def _agent_src() -> str:
    return Path(agent_mod.__file__).read_text(encoding="utf-8")


class TestAst2240CutoverGrep:
    def test_agent_has_no_in_process_send_to(self) -> None:
        text = _agent_src()
        assert "send_to_anthropic" not in text
        assert "send_to_llm_compat" not in text

    def test_database_has_no_agent_job_sync(self) -> None:
        db = (_REPO / "src" / "data" / "database.py").read_text(encoding="utf-8")
        assert "agent_job" not in db
        assert "astral_agent" not in db

    def test_do_task_stores_prompt_before_send(self) -> None:
        body = _agent_src().split("async def do_task", 1)[1].split("\nasync def ", 1)[0]
        store_at = body.find("_store_prompt_blocks")
        send_at = body.find("_send_to_server")
        assert store_at >= 0 and send_at > store_at

    def test_run_next_and_story_still_on_platform(self) -> None:
        text = _agent_src()
        assert "def get_entity_agent_story" in text
        assert "run_next" in text
        adhoc = text.split("async def run_adhoc(", 1)[1].split("\nasync def ", 1)[0]
        assert "_send_to_server" in adhoc


class TestAst2240SubmitAdapter:
    def test_provider_request_anthropic_shape(self) -> None:
        req = agent_mod._provider_request(
            [{"type": "text", "text": "hi"}],
            server_id="anthropic",
            sku="claude-haiku-4-5",
            tier={"reasoning_effort": "high"},
            api_key="sk-test",
            system_blocks=[],
            temperature=0.2,
            max_tokens=32,
            forced_tool=None,
        )
        assert req["protocol"] == "anthropic"
        assert req["model"] == "claude-haiku-4-5"
        assert req["api_key"] == "sk-test"
        assert req["messages"] == [{"role": "user", "content": [{"type": "text", "text": "hi"}]}]
        assert req["temperature"] == 0.2
        assert "send_to" not in req

    @pytest.mark.asyncio
    async def test_send_maps_submit_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            agent_mod,
            "submit",
            AsyncMock(return_value={
                "success": True,
                "api_response": "plain",
                "usage": {"input_tokens": 3, "output_tokens": 4},
            }),
        )
        monkeypatch.setattr(agent_mod, "record_timesheet_entry", lambda **_k: None)
        monkeypatch.setattr(
            agent_mod, "calculate_cost_components_from_counts", lambda *a, **k: {},
        )
        out = await agent_mod._send_to_server(
            [{"type": "text", "text": "hi"}],
            server_id="anthropic",
            sku="claude-haiku-4-5",
            tier={},
            api_key="sk-test",
            system_blocks=[],
            response_format=None,
            prompt_label="t",
            candidate_id=None,
            temperature=None,
            max_tokens=16,
            debug=False,
            task_key_uuid=None,
            no_cache_prompt_tokens=0,
            no_cache_live_tokens=0,
        )
        assert out["success"] is True
        assert out["api_response"] == "plain"
        assert out["timesheet"]["inputtotal"] == 3
        sent = agent_mod.submit.await_args.args[0]
        assert sent["server_id"] == "anthropic"
        assert sent["api_key"] == "sk-test"

    @pytest.mark.asyncio
    async def test_astral_agent_error_becomes_failure_dict(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            agent_mod,
            "submit",
            AsyncMock(side_effect=AstralAgentError("connectivity_failure", "dsn missing")),
        )
        out = await agent_mod._send_to_server(
            [{"type": "text", "text": "hi"}],
            server_id="anthropic",
            sku="claude-haiku-4-5",
            tier={},
            api_key="sk-test",
            system_blocks=[],
            response_format=None,
            prompt_label="t",
            candidate_id=None,
            temperature=None,
            max_tokens=16,
            debug=False,
            task_key_uuid=None,
            no_cache_prompt_tokens=0,
            no_cache_live_tokens=0,
        )
        assert out["success"] is False
        assert out["failure_class"] == "connectivity_failure"
        assert "dsn missing" in out["error"]
