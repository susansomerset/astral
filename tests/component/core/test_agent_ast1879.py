"""AST-1879: do_task routes by agent model → catalog server with the candidate's key for that server.

No _candidate_server_key stub here (unlike test_agent.py) — key selection / no-fallback is under test.
Outbound requests are intercepted at the SDK client constructor (llm_compat._get_client /
anthropic.Anthropic) or at the protocol send functions; nothing reaches the network.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import agent as agent_mod
from src.external import llm_compat
from src.utils import config as cfg
from src.utils.cost_calculator import calculate_cost_components_from_counts

from tests.component.core.test_agent import _agent_rows, _api_response

_REPO_AGENTS = {
    r["agent_id"]: r
    for r in json.loads((Path(__file__).resolve().parents[3] / "data/admin/agent.json").read_text())
}


_SEED_KEYS = ("model_id", "max_tokens", "quantization", "temperature", "reasoning_effort",
              "provider_allow_fallbacks", "provider_only", "provider_ignore", "provider_sort")


def _seeded_rows(agent_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """_agent_rows prompts + the repo-seeded agent's model / max_tokens / plain settings (AST-1878, AST-1955)."""
    agent_row, task_row = _agent_rows()
    seed = _REPO_AGENTS[agent_id]
    agent_row.update(agent_id=agent_id, **{k: seed[k] for k in _SEED_KEYS})
    task_row["agent_id"] = agent_id
    return agent_row, task_row


class _Msg:
    def __init__(self, text: str) -> None:
        self.content = [SimpleNamespace(text=text)]
        self.stop_reason = "end_turn"
        self.id = "msg_ast1879"
        self.usage = SimpleNamespace(
            input_tokens=100, output_tokens=25, cache_read_input_tokens=50, cache_creation_input_tokens=5
        )


class _CompatClientSpy:
    """Stands in for llm_compat._get_client: records (server_id, api_key) per client build + request bodies."""

    def __init__(self, text: str) -> None:
        self.builds: List[Tuple[str, str]] = []
        self.calls: List[Dict[str, Any]] = []
        self._text = text
        self.messages = self

    def __call__(self, server: Dict[str, Any], api_key: str) -> "_CompatClientSpy":
        self.builds.append((server["base_url"], api_key))
        return self

    def create(self, **kwargs: Any) -> _Msg:
        self.calls.append(kwargs)
        return _Msg(self._text)


@pytest.fixture
def batch_token() -> Any:
    token = agent_mod.log_batch_id.set("batch-1879")
    yield token
    agent_mod.log_batch_id.reset(token)


@pytest.fixture
def no_storage(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    save = MagicMock()
    monkeypatch.setattr(agent_mod, "save_agent_data", save)
    monkeypatch.setattr(agent_mod, "compute_batch_cost", lambda batch_id: 0.0)
    return save


def _clients(monkeypatch: pytest.MonkeyPatch) -> Tuple[AsyncMock, AsyncMock]:
    anth = AsyncMock(return_value={
        "success": True, "parsed_response": {"search_terms": "a"}, "api_response": _api_response(), "timesheet": {},
    })
    compat = AsyncMock(return_value={
        "success": True, "parsed_response": {"search_terms": "a"}, "api_response": _api_response(), "timesheet": {},
    })
    monkeypatch.setattr(agent_mod, "send_to_anthropic", anth)
    monkeypatch.setattr(agent_mod, "send_to_llm_compat", compat)
    return anth, compat


_TASK = "craft_company_search_terms"


def _ctx(keys: Optional[Dict[str, str]], cid: str = "somerset") -> Dict[str, Any]:
    ctx: Dict[str, Any] = {"astral_candidate_id": cid, "candidate_data": {"astral_candidate_id": cid}}
    if keys is not None:
        ctx["candidate_api_keys"] = keys
    return ctx


# Branches: ctx map wins; ctx without map → DB load by id; explicit {} honoured; blank key → None; no id → None.
class TestAst1879CandidateServerKey:
    def test_ctx_map_returns_only_that_servers_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        get = MagicMock()
        monkeypatch.setattr(agent_mod.database, "get_candidate", get)
        keys = {"kimi": "sk-kimi", "anthropic": "sk-ant"}
        assert agent_mod._candidate_server_key({"candidate_api_keys": keys}, "c1", "kimi") == "sk-kimi"
        assert agent_mod._candidate_server_key({"candidate_api_keys": keys}, "c1", "deepseek") is None
        get.assert_not_called()

    def test_ctx_without_map_loads_candidate_by_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        get = MagicMock(return_value={"candidate_api_keys": {"deepseek": "sk-ds"}})
        monkeypatch.setattr(agent_mod.database, "get_candidate", get)
        assert agent_mod._candidate_server_key({"astral_candidate_id": "c1"}, "c1", "deepseek") == "sk-ds"
        assert agent_mod._candidate_server_key(None, "c1", "deepseek") == "sk-ds"
        assert get.call_count == 2
        get.assert_called_with("c1")

    def test_explicit_empty_map_is_honoured_without_db_read(self, monkeypatch: pytest.MonkeyPatch) -> None:
        get = MagicMock(return_value={"candidate_api_keys": {"kimi": "sk-db"}})
        monkeypatch.setattr(agent_mod.database, "get_candidate", get)
        assert agent_mod._candidate_server_key({"candidate_api_keys": {}}, "c1", "kimi") is None
        get.assert_not_called()

    def test_blank_key_missing_row_and_no_id_return_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        get = MagicMock(return_value=None)
        monkeypatch.setattr(agent_mod.database, "get_candidate", get)
        assert agent_mod._candidate_server_key({"candidate_api_keys": {"kimi": ""}}, "c1", "kimi") is None
        assert agent_mod._candidate_server_key({}, "ghost", "kimi") is None
        assert agent_mod._candidate_server_key(None, None, "kimi") is None
        assert agent_mod._candidate_server_key(None, "", "kimi") is None
        get.assert_called_once_with("ghost")


class TestAst1879RouteHelpers:
    def test_agent_llm_route_resolves_catalog(self) -> None:
        # AST-1956: the stripped model_id + the whole row go to resolve_agent_settings; settings pass unchecked
        # (an effort outside any vocabulary still comes back as stored).
        row = {"agent_id": "a", "model_id": " moonshotai/kimi-k2.6 ", "temperature": 0.3,
               "reasoning_effort": "ultra", "quantization": "int4", "provider_allow_fallbacks": False}
        route = agent_mod._agent_llm_route(row)
        assert route == cfg.resolve_agent_settings("moonshotai/kimi-k2.6", row)
        assert route["tier"]["reasoning_effort"] == "ultra"
        assert route["tier"]["provider"] == {"quantizations": ["int4"], "allow_fallbacks": False}

    @pytest.mark.parametrize("model_id", ["claude", "deepseek-v4"])
    def test_agent_llm_route_raises_on_pre_sku_model_id(self, model_id: str) -> None:
        # AST-1956: no brain/mode checks remain; an unmigrated row (AST-1958) fails on its retired id.
        with pytest.raises(ValueError, match="Unknown LLM model"):
            agent_mod._agent_llm_route({"agent_id": "a", "model_id": model_id, "brain_setting": "Medium", "mode": "Wild"})

    def test_task_llm_server_id_uses_task_agent_row(self, monkeypatch: pytest.MonkeyPatch) -> None:
        seen: List[str] = []

        def _resolve(task_key: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
            seen.append(task_key)
            return _agent_rows(model_id="deepseek-v4-flash")

        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", _resolve)
        assert agent_mod.task_llm_server_id("evaluate_jd") == "deepseek"
        assert seen == ["evaluate_jd"]

    def test_task_llm_server_id_raises_on_broken_agent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda k: _agent_rows(model_id=""))
        with pytest.raises(ValueError, match="has no model_id configured"):
            agent_mod.task_llm_server_id("evaluate_jd")

    def test_missing_server_key_result_shape(self) -> None:
        out = agent_mod._missing_server_key_result("c1", "kimi")
        assert out == {
            "success": False,
            "error": "Candidate c1 has no API key for server 'kimi'",
            "api_response": None,
            "parsed_response": None,
            "timesheet": {},
        }
        assert agent_mod._missing_server_key_result(None, "kimi")["error"].startswith("Candidate - ")


# Branches (AST-1944 task_llm_server_id_or_none): strict path returns a server; ValueError + sentinel
# agent_id ("" / "telescope" / no row) → None; ValueError + any other agent_id → re-raise.
class TestAst1944TaskLlmServerIdOrNone:
    _REAL = {"agent_id": "a1", "model_id": "deepseek-v4-pro", "temperature": 0.2}

    @staticmethod
    def _data(
        monkeypatch: pytest.MonkeyPatch, rows: Dict[str, Dict[str, Any]], agents: Dict[str, Dict[str, Any]]
    ) -> None:
        # Data layer only — _resolve_task_prompts (strict) runs for real.
        monkeypatch.setattr(agent_mod, "get_agent_task", lambda k: rows.get(k))
        monkeypatch.setattr(agent_mod, "get_agent", lambda i: agents.get(i))

    @pytest.mark.parametrize(
        "rows",
        [
            {"fetch_jd": {"task_key": "fetch_jd", "agent_id": "telescope"}},
            {"fetch_jd": {"task_key": "fetch_jd", "agent_id": ""}},
            {"fetch_jd": {"task_key": "fetch_jd", "agent_id": "  "}},
            {},
        ],
        ids=["telescope", "empty", "blank", "no_row"],
    )
    def test_non_llm_sentinels_return_none(self, monkeypatch: pytest.MonkeyPatch, rows: Dict[str, Any]) -> None:
        self._data(monkeypatch, rows, {})
        assert agent_mod.task_llm_server_id_or_none("fetch_jd") is None

    def test_llm_row_returns_catalog_server(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._data(monkeypatch, {"evaluate_jd": {"task_key": "evaluate_jd", "agent_id": "a1"}}, {"a1": self._REAL})
        assert agent_mod.task_llm_server_id_or_none("evaluate_jd") == "deepseek"

    def test_unknown_real_agent_reraises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._data(monkeypatch, {"evaluate_jd": {"task_key": "evaluate_jd", "agent_id": "ghost"}}, {})
        with pytest.raises(ValueError, match="Agent 'ghost' referenced by task 'evaluate_jd' not found"):
            agent_mod.task_llm_server_id_or_none("evaluate_jd")

    def test_real_agent_without_model_reraises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._data(
            monkeypatch,
            {"evaluate_jd": {"task_key": "evaluate_jd", "agent_id": "a1"}},
            {"a1": {**self._REAL, "model_id": ""}},
        )
        with pytest.raises(ValueError, match="has no model_id configured"):
            agent_mod.task_llm_server_id_or_none("evaluate_jd")

    def test_mailbox_fold_resolves_legacy_agent_server(self, monkeypatch: pytest.MonkeyPatch) -> None:
        mc = cfg.METEORITE_EMAIL_PARSE_CONFIG
        self._data(
            monkeypatch,
            {
                mc["task_key"]: {"task_key": mc["task_key"], "agent_id": ""},
                mc["legacy_agent_task_key"]: {"task_key": mc["legacy_agent_task_key"], "agent_id": "a1"},
            },
            {"a1": self._REAL},
        )
        # Fold still gated on the legacy agent's server — not treated as non-LLM.
        assert agent_mod.task_llm_server_id_or_none(mc["task_key"]) == "deepseek"

    def test_mailbox_fold_without_legacy_agent_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        mc = cfg.METEORITE_EMAIL_PARSE_CONFIG
        self._data(monkeypatch, {mc["task_key"]: {"task_key": mc["task_key"], "agent_id": ""}}, {})
        assert agent_mod.task_llm_server_id_or_none(mc["task_key"]) is None


# Branches: protocol "anthropic" → send_to_anthropic (SKU + override key); else → send_to_llm_compat.
class TestAst1879SendToServer:
    _COMMON = dict(
        system_blocks=[], response_format="json", prompt_label="t", candidate_id="c1", temperature=0.3,
        max_tokens=10, debug=False, task_key_uuid="u1", no_cache_prompt_tokens=1, no_cache_live_tokens=2,
    )

    @pytest.mark.parametrize("effort", [None, "high", "none"])
    async def test_anthropic_protocol(self, monkeypatch: pytest.MonkeyPatch, effort: Any) -> None:
        anth, compat = _clients(monkeypatch)
        route = cfg.resolve_agent_settings("claude-sonnet-4-6", {"reasoning_effort": effort})
        await agent_mod._send_to_server(
            [], server_id="anthropic", sku=route["sku"], tier=route["tier"], api_key="sk-ant", **self._COMMON
        )
        compat.assert_not_called()
        kw = anth.await_args.kwargs
        assert (kw["model_code"], kw["api_key_override"]) == ("claude-sonnet-4-6", "sk-ant")
        # AST-1956: the tier's effort reaches the Anthropic client as stored; temperature is the caller's.
        assert (kw["reasoning_effort"], kw["temperature"]) == (effort, 0.3)
        assert kw["record_timesheet"] is agent_mod.record_timesheet_entry
        assert kw["batch_size"] == 1 and kw["task_key_uuid"] == "u1"

    # AST-1947: kimi-k2.6-openrouter retired → moonshotai/kimi-k2.6. AST-1955: deepseek-v4 → per-SKU ids.
    @pytest.mark.parametrize("server_id,model_id", [("kimi", "kimi-k2.6"), ("openrouter", "moonshotai/kimi-k2.6"), ("deepseek", "deepseek-v4-flash")])
    async def test_compat_protocol(self, monkeypatch: pytest.MonkeyPatch, server_id: str, model_id: str) -> None:
        anth, compat = _clients(monkeypatch)
        route = cfg.resolve_agent_settings(model_id, {"reasoning_effort": "high", "provider_allow_fallbacks": True})
        await agent_mod._send_to_server(
            [], server_id=server_id, sku=route["sku"], tier=route["tier"], api_key="sk-x", batch_size=3, **self._COMMON
        )
        anth.assert_not_called()
        kw = compat.await_args.kwargs
        assert (kw["server_id"], kw["sku"], kw["tier"], kw["api_key"]) == (server_id, route["sku"], route["tier"], "sk-x")
        assert kw["record_timesheet"] is agent_mod.record_timesheet_entry
        assert kw["batch_size"] == 3


# AC 7: right key, no fallback — intercept at the outbound client.
class TestAst1879RightKeyNoFallback:
    async def test_compat_agent_builds_client_with_only_its_servers_key(
        self, monkeypatch: pytest.MonkeyPatch, batch_token: Any, no_storage: MagicMock
    ) -> None:
        spy = _CompatClientSpy('{"search_terms": "alpha"}')
        monkeypatch.setattr(llm_compat, "_get_client", spy)
        monkeypatch.setattr(agent_mod, "record_timesheet_entry", lambda **kw: None)
        anth = AsyncMock()
        monkeypatch.setattr(agent_mod, "send_to_anthropic", anth)
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda k: _agent_rows(model_id="kimi-k2.6"))
        out = await agent_mod.do_task(
            _TASK, index="somerset",
            ctx=_ctx({"anthropic": "sk-ant", "kimi": "sk-kimi", "deepseek": "sk-ds", "openrouter": "sk-or"}),
        )
        assert out["success"] is True
        anth.assert_not_called()
        assert spy.builds == [(cfg.LLM_SERVER_CONFIG["kimi"]["base_url"], "sk-kimi")]
        assert spy.calls[0]["model"] == "kimi-k2.6"

    async def test_anthropic_agent_builds_sdk_client_with_candidate_key_not_env(
        self, monkeypatch: pytest.MonkeyPatch, batch_token: Any, no_storage: MagicMock
    ) -> None:
        from src.external import anthropic as anthropic_ext

        built: List[Dict[str, Any]] = []

        class _Sdk:
            def __init__(self, **kwargs: Any) -> None:
                built.append(kwargs)
                self.messages = self

            def create(self, **kwargs: Any) -> _Msg:
                return _Msg('{"search_terms": "alpha"}')

        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-env-must-not-be-used")
        monkeypatch.setattr(anthropic_ext, "Anthropic", _Sdk)
        monkeypatch.setattr(agent_mod, "record_timesheet_entry", lambda **kw: None)
        compat = AsyncMock()
        monkeypatch.setattr(agent_mod, "send_to_llm_compat", compat)
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda k: _agent_rows(model_id="claude-haiku-4-5"))
        await agent_mod.do_task(_TASK, index="somerset", ctx=_ctx({"kimi": "sk-kimi", "anthropic": "sk-ant"}))
        compat.assert_not_called()
        assert built and all(b.get("api_key") == "sk-ant" for b in built)

    @pytest.mark.parametrize(
        "model_id,server_id,keys",
        [
            ("kimi-k2.6", "kimi", {"anthropic": "sk-ant", "openrouter": "sk-or", "deepseek": "sk-ds"}),
            ("moonshotai/kimi-k2.6", "openrouter", {"kimi": "sk-kimi"}),
            ("claude-haiku-4-5", "anthropic", {"kimi": "sk-kimi", "deepseek": "sk-ds"}),
            ("deepseek-v4-flash", "deepseek", {}),
        ],
    )
    async def test_missing_server_key_fails_naming_server_and_sends_nothing(
        self,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
        batch_token: Any,
        no_storage: MagicMock,
        model_id: str,
        server_id: str,
        keys: Dict[str, str],
    ) -> None:
        anth, compat = _clients(monkeypatch)
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda k: _agent_rows(model_id=model_id))
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-env")
        with caplog.at_level(logging.WARNING, logger="src.core.agent"):
            out = await agent_mod.do_task(_TASK, index="somerset", ctx=_ctx(keys))
        assert out["success"] is False
        assert out["error"] == f"Candidate somerset has no API key for server {server_id!r}"
        anth.assert_not_called()
        compat.assert_not_called()
        # Key gate runs before prompt storage: no agent_data rows for a call that never went out.
        no_storage.assert_not_called()
        assert any(
            f"somerset | {_TASK} skipped — no {server_id} API key on the candidate" in r.getMessage()
            and "This call is not going out" in r.getMessage()
            for r in caplog.records
        )

    async def test_ctx_without_map_uses_db_keys_for_that_server(
        self, monkeypatch: pytest.MonkeyPatch, batch_token: Any, no_storage: MagicMock
    ) -> None:
        # meteorite classify shape: ctx carries only the id → map loaded by id, same-server key only.
        anth, compat = _clients(monkeypatch)
        monkeypatch.setattr(
            agent_mod.database, "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "candidate_api_keys": {"deepseek": "sk-ds-db", "anthropic": "sk-a"}},
        )
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda k: _agent_rows(model_id="deepseek-v4-flash"))
        out = await agent_mod.do_task(_TASK, index="somerset", ctx=_ctx(None))
        assert out["success"] is True
        anth.assert_not_called()
        assert compat.await_args.kwargs["api_key"] == "sk-ds-db"


# AC 8: a Kimi-routed Estelle task writes an agent_timesheets row per server.
class TestAst1879KimiLedgerRow:
    async def test_estelle_kimi_task_writes_catalog_priced_timesheet_row(
        self, monkeypatch: pytest.MonkeyPatch, sqlite_in_memory: Any, batch_token: Any, no_storage: MagicMock
    ) -> None:
        db = sqlite_in_memory
        agent_row, task_row = _seeded_rows("principal_recruiter_estelle")
        assert agent_row["model_id"] == "kimi-k2.6"
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda k: (agent_row, task_row))
        spy = _CompatClientSpy('{"search_terms": "alpha"}')
        monkeypatch.setattr(llm_compat, "_get_client", spy)
        providers: List[str] = []
        real_add = db._add_timesheet_entry

        def _add(**kw: Any) -> bool:
            providers.append(kw.get("provider"))
            return real_add(**kw)

        monkeypatch.setattr("src.core.timesheets._add_timesheet_entry", _add)
        out = await agent_mod.do_task(_TASK, index="somerset", ctx=_ctx({"kimi": "sk-kimi"}))
        assert out["success"] is True
        # agent_timesheets has no provider column: the server id is the insert's provider arg
        # (SKU-on-server validation) and the SKU is priced on that server only.
        assert providers == ["kimi"]
        assert [s for s, m in cfg.LLM_MODEL_CONFIG.items() if "kimi-k2.6" in m["pricing"]] == ["kimi-k2.6"]
        assert cfg.LLM_MODEL_CONFIG["kimi-k2.6"]["server"] == "kimi"
        rows = db.list_timesheets()
        assert len(rows) == 1
        row = rows[0]
        assert row["model_code"] == "kimi-k2.6"
        # Non-anthropic provider → no anthropic_timesheets mirror.
        conn = db._get_connection()
        try:
            assert conn.execute("SELECT COUNT(*) FROM anthropic_timesheets").fetchone()[0] == 0
        finally:
            conn.close()
        assert row["candidate_id"] == "somerset"
        assert row["task_key_uuid"] == task_row["task_key_uuid"]
        assert (row["cache_read_tokens"], row["total_no_cache_input_tokens"], row["total_output_tokens"], row["cache_write_tokens"]) == (50, 100, 25, 5)
        expected = calculate_cost_components_from_counts(50, 100, 25, 5, sku="kimi-k2.6", server_id="kimi")
        for col, val in expected.items():
            assert row[col] == pytest.approx(val)
        assert sum(expected.values()) > 0


# AC 9 / AC 10: Estelle Slack turn runs at the contact agent row's model + brain, on the candidate's key.
class TestAst1879EstelleTurnRoute:
    async def test_turn_uses_contact_row_model_brain_and_candidate_kimi_key(
        self, monkeypatch: pytest.MonkeyPatch, batch_token: Any, no_storage: MagicMock
    ) -> None:
        agent_row, task_row = _seeded_rows("contact_recruiter_estelle")
        monkeypatch.setattr(agent_mod, "_resolve_task_prompts", lambda k: (agent_row, task_row))
        spy = _CompatClientSpy('{"agent_performance": {"status": "success"}, "agent_payload": {"reply": "hi"}}')
        monkeypatch.setattr(llm_compat, "_get_client", spy)
        monkeypatch.setattr(agent_mod, "record_timesheet_entry", lambda **kw: None)
        anth = AsyncMock()
        monkeypatch.setattr(agent_mod, "send_to_anthropic", anth)
        # Turn ctx shape from contact.run_contact_estelle_turn (AST-1879 Stage 3).
        turn_ctx = {"astral_candidate_id": "somerset", "candidate_data": {}, "candidate_api_keys": {"kimi": "sk-kimi", "anthropic": "sk-ant"}}
        await agent_mod.do_task("contact_estelle_turn", live_content="hi", index="somerset", ctx=turn_ctx)
        anth.assert_not_called()
        route = cfg.resolve_agent_settings(agent_row["model_id"], agent_row)
        assert spy.builds == [(cfg.LLM_SERVER_CONFIG[route["server_id"]]["base_url"], "sk-kimi")]
        call = spy.calls[0]
        assert call["model"] == route["sku"]
        # Seed row leaves max_tokens null → tier default. AST-1956: its stored settings reach the outbound body —
        # temperature 0.2 and effort "none" as thinking disabled; kimi direct gets no provider object.
        assert call["max_tokens"] == route["tier"]["max_tokens"]
        assert call.get("temperature") == agent_row["temperature"] == 0.2
        assert call["extra_body"] == {"thinking": {"type": "disabled"}}

    def test_agent_py_has_no_default_brain_or_legacy_provider_symbols(self) -> None:
        src = Path(agent_mod.__file__).read_text()
        for needle in ("default_brain_setting", "CONTACT_ESTELLE_CONFIG", "get_active_llm_provider",
                       "send_to_" + "deepseek", "resolve_brain_setting_to_", "tier_meta",
                       # AST-1956: the brain / mode route is gone from the call path.
                       "resolve_model_brain", "brain_setting"):
            assert needle not in src, needle
