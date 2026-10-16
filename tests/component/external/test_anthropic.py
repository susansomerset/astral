"""Component tests for src/external/anthropic.py (AST-391)."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.external import anthropic as anthropic_mod


# Branches: timestamp prefix shape; hour rollover at noon/midnight.
class TestGetTimestampPrefix:
    def test_includes_day_and_envelope_instruction(self, monkeypatch) -> None:
        class _FixedDatetime:
            @classmethod
            def now(cls):
                return cls()

            def strftime(self, fmt: str) -> str:
                if fmt == "%A":
                    return "Thursday"
                if fmt == "%-m/%-d/%y":
                    return "5/13/26"
                if fmt == "%M":
                    return "05"
                raise AssertionError(fmt)

            @property
            def hour(self) -> int:
                return 15

        monkeypatch.setattr(anthropic_mod, "datetime", _FixedDatetime)
        monkeypatch.setitem(anthropic_mod.ASTRAL_CONFIG, "prompt_prefix", "Envelope here.")
        out = anthropic_mod.getTimestampPrefix()
        assert "Thursday, 5/13/26" in out
        assert "3:05pm Pacific time" in out
        assert "Envelope here." in out

    def test_midnight_uses_twelve_hour_clock(self, monkeypatch) -> None:
        class _FixedDatetime:
            @classmethod
            def now(cls):
                return cls()

            def strftime(self, fmt: str) -> str:
                return {"%A": "Monday", "%-m/%-d/%y": "1/1/26", "%M": "00"}.get(fmt, "")

            @property
            def hour(self) -> int:
                return 0

        monkeypatch.setattr(anthropic_mod, "datetime", _FixedDatetime)
        assert "12:00am" in anthropic_mod.getTimestampPrefix()

    def test_structured_swaps_envelope_for_performance_rules(self, monkeypatch) -> None:
        # AST-2179: forced-tool calls get prompt_prefix_structured instead of the two-key envelope sentence.
        monkeypatch.setitem(anthropic_mod.ASTRAL_CONFIG, "prompt_prefix", "Envelope here.")
        monkeypatch.setitem(anthropic_mod.ASTRAL_CONFIG, "prompt_prefix_structured", "Rules only.")
        structured = anthropic_mod.getTimestampPrefix(structured=True)
        assert structured.startswith("Today is ") and structured.endswith("Pacific time. Rules only.\n")
        assert "Envelope here." not in structured
        assert anthropic_mod.getTimestampPrefix().endswith("Pacific time. Envelope here.\n")


# Branches: success path; missing/invalid response fields.
class TestParseApiResponse:
    @pytest.mark.asyncio
    async def test_extracts_first_text_block(self) -> None:
        response = {
            "success": True,
            "api_response": SimpleNamespace(content=[SimpleNamespace(text='{"a":1}')]),
        }
        assert await anthropic_mod._parse_api_response(response) == '{"a":1}'

    @pytest.mark.asyncio
    async def test_extracts_text_after_thinking_block(self) -> None:
        response = {
            "success": True,
            "api_response": SimpleNamespace(
                content=[
                    SimpleNamespace(thinking="internal chain"),
                    SimpleNamespace(text='{"agent_payload":"000|DTA5"}'),
                ]
            ),
        }
        assert await anthropic_mod._parse_api_response(response) == '{"agent_payload":"000|DTA5"}'

    @pytest.mark.asyncio
    async def test_raises_when_response_invalid(self) -> None:
        with pytest.raises(ValueError, match="API response is None"):
            await anthropic_mod._parse_api_response(None)  # type: ignore[arg-type]
        with pytest.raises(RuntimeError, match="API call failed"):
            await anthropic_mod._parse_api_response({"success": False, "error": "nope"})
        with pytest.raises(ValueError, match="missing from response dict"):
            await anthropic_mod._parse_api_response({"success": True})
        with pytest.raises(ValueError, match="content is empty"):
            await anthropic_mod._parse_api_response({"success": True, "api_response": SimpleNamespace(content=[])})
        with pytest.raises(ValueError, match="missing text attribute"):
            await anthropic_mod._parse_api_response(
                {"success": True, "api_response": SimpleNamespace(content=[SimpleNamespace()])}
            )


# Branches: fenced JSON; extra data; heal fallbacks; parse failure.
class TestParseJsonResponse:
    def test_parses_plain_and_fenced_json(self) -> None:
        assert anthropic_mod._parse_json_response('{"a":1}') == {"a": 1}
        assert anthropic_mod._parse_json_response("```json\n{\"b\":2}\n```") == {"b": 2}

    def test_trims_extra_data_after_valid_json(self) -> None:
        payload = '{"a":1} trailing'
        assert anthropic_mod._parse_json_response(payload) == {"a": 1}

    def test_top_level_json_string_is_not_wrapped(self) -> None:
        # AST-2179: encoded-grade coercion removed — graders answer through the forced tool.
        assert anthropic_mod._parse_json_response('"000|DTA5|GCA4"') == "000|DTA5|GCA4"

    def test_bare_encoded_text_is_a_parse_failure(self) -> None:
        # AST-2179: no {"agent_payload": …} rescue for encoded lines any more.
        with pytest.raises(ValueError, match="Failed to parse JSON response"):
            anthropic_mod._parse_json_response("[evaluate_jd_batch_x]\n000|DTA5|GCA4")

    def test_raises_when_json_cannot_be_recovered(self) -> None:
        with pytest.raises(ValueError, match="Failed to parse JSON response"):
            anthropic_mod._parse_json_response("{not json")


# Branches: problem vs success; required fields; job_ids parsing errors.
class TestParsePythonCodeResponse:
    def test_problem_result(self) -> None:
        text = 'parse_result = "problem"\nproblem_notes = "broken"'
        assert anthropic_mod._parse_python_code_response(text) == {
            "parse_result": "problem",
            "problem_notes": "broken",
        }

    def test_success_result(self) -> None:
        text = (
            'parse_result = "success"\n'
            'job_container = "div.jobs"\n'
            'job_tag = "a.posting"\n'
            'job_ids = ["1", "2"]'
        )
        out = anthropic_mod._parse_python_code_response(text)
        assert out["parse_result"] == "success"
        assert out["job_ids"] == ["1", "2"]

    def test_rejects_invalid_parse_result(self) -> None:
        with pytest.raises(ValueError, match="parse_result must be"):
            anthropic_mod._parse_python_code_response('parse_result = "maybe"')

    def test_requires_job_container_tag_and_ids(self) -> None:
        with pytest.raises(ValueError, match="job_container"):
            anthropic_mod._parse_python_code_response('parse_result = "success"')
        with pytest.raises(ValueError, match="job_tag"):
            anthropic_mod._parse_python_code_response(
                'parse_result = "success"\njob_container = "div"'
            )
        with pytest.raises(ValueError, match="job_ids"):
            anthropic_mod._parse_python_code_response(
                'parse_result = "success"\njob_container = "div"\njob_tag = "a"'
            )


# Branches: model required; text/json/python formats; failures; timesheet hooks.
class TestSendToAnthropic:
    @pytest.mark.asyncio
    async def test_requires_model_code(self) -> None:
        with pytest.raises(ValueError, match="model_code is required"):
            await anthropic_mod.send_to_anthropic([])

    @pytest.mark.asyncio
    async def test_text_json_and_python_success(self, monkeypatch, fake_anthropic_client) -> None:
        client = fake_anthropic_client(response_text='{"agent_performance":{"status":"success"},"agent_payload":{}}')

        def _client(*_args, **_kwargs):
            return client

        monkeypatch.setattr(anthropic_mod, "_get_client", _client)
        for fmt, expected in (
            ("text", str),
            ("json", dict),
            ("python", dict),
        ):
            if fmt == "text":
                client._response_text = "plain text"
            elif fmt == "json":
                client._response_text = '{"agent_performance":{"status":"success"},"agent_payload":{}}'
            else:
                client._response_text = (
                    'parse_result = "success"\n'
                    'job_container = "motion.div"\n'
                    'job_tag = "a.job"\n'
                    'job_ids = ["1"]'
                )
            out = await anthropic_mod.send_to_anthropic(
                [{"type": "text", "text": "hi"}],
                model_code="claude-sonnet-4-6",
                response_format=fmt,
                system_blocks=[{"type": "text", "text": "sys"}],
                enable_web_search=True,
                debug=True,
            )
            assert out["success"] is True
            assert isinstance(out["parsed_response"], expected)

    @pytest.mark.asyncio
    async def test_records_timesheet_and_handles_parse_failure(self, monkeypatch, fake_anthropic_client) -> None:
        client = fake_anthropic_client(response_text="not-json")
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        recorded: list = []

        def _record(**kwargs):
            recorded.append(kwargs)

        out = await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}],
            model_code="claude-sonnet-4-6",
            response_format="json",
            record_timesheet=_record,
            task_key_uuid="task-1",
            candidate_id="cand-1",
        )
        assert out["success"] is False
        assert recorded and recorded[0]["agent_performance"] == "failure"

    @pytest.mark.asyncio
    async def test_api_failure_returns_error_payload(self, monkeypatch, fake_anthropic_client) -> None:
        client = fake_anthropic_client(raise_on_create=RuntimeError("timeout"))
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        out = await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}],
            model_code="claude-sonnet-4-6",
        )
        assert out["success"] is False
        assert "timeout" in out["error"]

    @pytest.mark.asyncio
    async def test_invalid_response_format_raises(self, monkeypatch, fake_anthropic_client) -> None:
        client = fake_anthropic_client()
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        out = await anthropic_mod.send_to_anthropic(
            [{"type": "document", "source": {"type": "text", "data": "x"}}],
            model_code="claude-sonnet-4-6",
            response_format="xml",
        )
        assert out["success"] is False
        assert "Invalid response_format" in out["error"]

    @pytest.mark.asyncio
    async def test_success_without_response_format(self, monkeypatch, fake_anthropic_client) -> None:
        client = fake_anthropic_client(response_text="ignored")
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        out = await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}],
            model_code="claude-sonnet-4-6",
        )
        assert out["success"] is True
        assert out["parsed_response"] is None

    @pytest.mark.asyncio
    async def test_timesheet_recording_swallows_callback_errors(self, monkeypatch, fake_anthropic_client) -> None:
        client = fake_anthropic_client(
            response_text='{"agent_performance":{"status":"success","failure_note":null},"agent_payload":{}}'
        )
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)

        def _record(**_kwargs):
            raise RuntimeError("db down")

        out = await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}],
            model_code="claude-sonnet-4-6",
            response_format="json",
            record_timesheet=_record,
        )
        assert out["success"] is True


class TestAst897BalanceRefusalTagging:
    """AST-897: anthropic API exceptions tag failure_class for balance/credit refusals."""

    @pytest.mark.asyncio
    async def test_status_402_tags_failure_class(self, monkeypatch, fake_anthropic_client) -> None:
        from src.utils.config import PROVIDER_BALANCE_REFUSAL

        err = type("BalanceErr", (Exception,), {"status_code": 402})("payment required")
        client = fake_anthropic_client(raise_on_create=err)
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        out = await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}],
            model_code="claude-sonnet-4-6",
        )
        assert out["success"] is False
        assert out["failure_class"] == PROVIDER_BALANCE_REFUSAL["failure_class"]
        assert "payment required" in out["error"]

    @pytest.mark.asyncio
    async def test_substring_tags_failure_class(self, monkeypatch, fake_anthropic_client) -> None:
        from src.utils.config import PROVIDER_BALANCE_REFUSAL

        client = fake_anthropic_client(raise_on_create=RuntimeError("Insufficient Balance"))
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        out = await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}],
            model_code="claude-sonnet-4-6",
        )
        assert out["success"] is False
        assert out["failure_class"] == PROVIDER_BALANCE_REFUSAL["failure_class"]

    @pytest.mark.asyncio
    async def test_ordinary_api_failure_omits_failure_class(self, monkeypatch, fake_anthropic_client) -> None:
        client = fake_anthropic_client(raise_on_create=RuntimeError("timeout"))
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        out = await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}],
            model_code="claude-sonnet-4-6",
        )
        assert out["success"] is False
        assert "failure_class" not in out


class TestAst903JsonMaxTokensHardFail:
    """AST-903: JSON + stop_reason=max_tokens fails closed (no heal/parse success)."""

    @pytest.mark.asyncio
    async def test_json_max_tokens_returns_failure_class(self, monkeypatch, fake_anthropic_client) -> None:
        client = fake_anthropic_client(
            response_text='{"criteria":[{"content":"A == The JD',
            stop_reason="max_tokens",
        )
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        recorded: list = []
        out = await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}],
            model_code="claude-sonnet-4-6",
            response_format="json",
            record_timesheet=lambda **kwargs: recorded.append(kwargs),
        )
        assert out["success"] is False
        assert out["failure_class"] == "max_tokens"
        assert "max_tokens" in out["error"]
        assert out["parsed_response"] is None
        assert recorded and recorded[0]["agent_performance"] == "failure"

    @pytest.mark.asyncio
    async def test_text_max_tokens_still_succeeds(self, monkeypatch, fake_anthropic_client) -> None:
        client = fake_anthropic_client(response_text="plain truncated ok", stop_reason="max_tokens")
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        out = await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}],
            model_code="claude-sonnet-4-6",
            response_format="text",
        )
        assert out["success"] is True
        assert "failure_class" not in out


class TestAst1190EmptyUnusableProviderResponse:
    """AST-1190: hollow response fail-closed + blank exception error normalize."""

    @pytest.mark.asyncio
    async def test_hollow_stop_question_zero_tokens_fails_closed(
        self, monkeypatch, fake_anthropic_client, caplog
    ) -> None:
        from src.utils.config import PROVIDER_EMPTY_RESPONSE
        from src.utils.logging import log_batch_id

        zero = SimpleNamespace(
            input_tokens=0,
            output_tokens=0,
            cache_read_input_tokens=0,
            cache_creation_input_tokens=0,
        )
        client = fake_anthropic_client(response_text="", stop_reason="?", usage=zero)
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        recorded: list = []
        token = log_batch_id.set("batch-hollow-anth")
        try:
            with caplog.at_level("INFO"):
                out = await anthropic_mod.send_to_anthropic(
                    [{"type": "text", "text": "hi"}],
                    model_code="claude-sonnet-4-6",
                    response_format="text",
                    prompt_label="anticipate_scan",
                    record_timesheet=lambda **kwargs: recorded.append(kwargs),
                )
        finally:
            log_batch_id.reset(token)

        assert out["success"] is False
        assert out["failure_class"] == PROVIDER_EMPTY_RESPONSE["failure_class"]
        assert out["error"] == PROVIDER_EMPTY_RESPONSE["error"]
        assert out["error"].strip()
        assert recorded and recorded[0]["agent_performance"] == "failure"
        err_msgs = [r.message for r in caplog.records if r.levelname == "ERROR"]
        assert any("error=" in m and "unusable" in m for m in err_msgs)
        info_msgs = [
            r.message
            for r in caplog.records
            if r.levelname == "INFO" and "LLM anthropic" in r.message
        ]
        assert not any("stop=?" in m and "tokens in=0" in m for m in info_msgs)

    @pytest.mark.asyncio
    async def test_blank_timeout_error_returns_non_empty_error(
        self, monkeypatch, fake_anthropic_client
    ) -> None:
        client = fake_anthropic_client(raise_on_create=TimeoutError())
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        out = await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}],
            model_code="claude-sonnet-4-6",
        )
        assert out["success"] is False
        assert out["error"].strip()
        # AST-1189 may tag TimeoutError as provider_call_timeout; never blank error=
        if out.get("failure_class") is not None:
            assert out["failure_class"] == "provider_call_timeout"

    @pytest.mark.asyncio
    async def test_healthy_end_turn_still_succeeds(
        self, monkeypatch, fake_anthropic_client
    ) -> None:
        client = fake_anthropic_client(response_text="plain ok", stop_reason="end_turn")
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        out = await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}],
            model_code="claude-sonnet-4-6",
            response_format="text",
        )
        assert out["success"] is True
        assert "failure_class" not in out


class TestAst1189ProviderCallBudgetTimeout:
    """AST-1189: TimeoutError → provider_call_timeout + non-empty budget error."""

    @pytest.mark.asyncio
    async def test_timeout_error_tags_failure_class(
        self, monkeypatch, fake_anthropic_client
    ) -> None:
        from src.utils.config import PROVIDER_CALL_BUDGET
        from src.utils.llm_external import provider_call_timeout_error_message

        client = fake_anthropic_client(raise_on_create=TimeoutError())
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        out = await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}],
            model_code="claude-sonnet-4-6",
        )
        assert out["success"] is False
        assert out["failure_class"] == PROVIDER_CALL_BUDGET["failure_class"]
        assert out["error"] == provider_call_timeout_error_message()
        assert out["error"].strip()

    @pytest.mark.asyncio
    async def test_ordinary_runtime_error_still_omits_timeout_class(
        self, monkeypatch, fake_anthropic_client
    ) -> None:
        client = fake_anthropic_client(raise_on_create=RuntimeError("boom"))
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        out = await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}],
            model_code="claude-sonnet-4-6",
        )
        assert out["success"] is False
        assert out["error"] == "boom"
        assert out.get("failure_class") != "provider_call_timeout"

    @pytest.mark.asyncio
    async def test_healthy_response_still_succeeds(
        self, monkeypatch, fake_anthropic_client
    ) -> None:
        client = fake_anthropic_client(response_text="plain ok", stop_reason="end_turn")
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        out = await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}],
            model_code="claude-sonnet-4-6",
            response_format="text",
        )
        assert out["success"] is True
        assert "failure_class" not in out


# AST-1956: send_to_anthropic sends temperature / reasoning_effort only when set, exactly as given.
# Branches: temperature None vs set (0.0 included); effort empty / "none" / other (via extra_body, no vocabulary);
# a rejected setting is the ordinary failure envelope (no failure_class).
class TestAst1956SettingsOnTheWire:
    @staticmethod
    def _recording(monkeypatch, fake_anthropic_client, **client_kwargs):
        client = fake_anthropic_client(response_text="ok", **client_kwargs)
        client.calls = []
        real_create = client.create

        def _create(**kwargs):
            client.calls.append(kwargs)
            return real_create(**kwargs)

        client.create = _create
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda *_a, **_k: client)
        return client

    @staticmethod
    async def _send(**kwargs):
        return await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}], model_code="claude-sonnet-4-6", response_format="text", **kwargs
        )

    @pytest.mark.asyncio
    async def test_empty_settings_send_nothing(self, monkeypatch, fake_anthropic_client) -> None:
        # AC 2: the SDK would serialize temperature=None as null, so an empty one is left out entirely.
        client = self._recording(monkeypatch, fake_anthropic_client)
        out = await self._send()
        assert out["success"] is True
        assert not {"temperature", "extra_body", "thinking", "output_config"} & set(client.calls[0])

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("settings", "expected"),
        [
            ({"temperature": 0.3}, {"temperature": 0.3}),
            ({"temperature": 0.0}, {"temperature": 0.0}),
            ({"reasoning_effort": "high"}, {"extra_body": {"output_config": {"effort": "high"}}}),
            ({"reasoning_effort": "none"}, {"extra_body": {"thinking": {"type": "disabled"}}}),
            ({"reasoning_effort": "ultra"}, {"extra_body": {"output_config": {"effort": "ultra"}}}),
            ({"temperature": 0.3, "reasoning_effort": "high"},
             {"temperature": 0.3, "extra_body": {"output_config": {"effort": "high"}}}),
        ],
    )
    async def test_ac3_temperature_and_effort_exactly_as_set(
        self, monkeypatch, fake_anthropic_client, settings, expected
    ) -> None:
        client = self._recording(monkeypatch, fake_anthropic_client)
        await self._send(**settings)
        call = client.calls[0]
        assert {k: call[k] for k in ("temperature", "extra_body") if k in call} == expected

    @pytest.mark.asyncio
    async def test_ac4_rejected_setting_is_a_plain_failure(self, monkeypatch, fake_anthropic_client) -> None:
        msg = "Error code: 400 - Reasoning is mandatory for this endpoint and cannot be disabled"
        client = self._recording(monkeypatch, fake_anthropic_client, raise_on_create=RuntimeError(msg))
        out = await self._send(reasoning_effort="none")
        assert client.calls[0]["extra_body"] == {"thinking": {"type": "disabled"}}
        assert out["success"] is False and msg in out["error"]
        assert "failure_class" not in out


# AST-2179 — forced-tool transport. Branches: forced_tool None vs set (× response_format None / text / json);
# reply has the named tool / another tool / text only / non-object input; stop_reason max_tokens; + web search guard.
_TOOL = {"name": "submit_grades", "input_schema": {"type": "object", "properties": {"agent_performance": {"type": "object"}}}}
_TOOL_INPUT = {"agent_performance": {"status": "success"}, "grades": [{"id": "000", "DTA": 5}]}


def _tool_use(name: str = "submit_grades", tool_input=None) -> SimpleNamespace:
    return SimpleNamespace(type="tool_use", id="toolu_1", name=name, input=_TOOL_INPUT if tool_input is None else tool_input)


class _BlocksClient:
    """messages.create records kwargs and answers with the given content blocks — never the network."""

    def __init__(self, content, stop_reason: str = "tool_use") -> None:
        self.calls: list = []
        self._content = content
        self._stop_reason = stop_reason
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        usage = SimpleNamespace(input_tokens=10, output_tokens=5, cache_read_input_tokens=0, cache_creation_input_tokens=0)
        return SimpleNamespace(content=self._content, stop_reason=self._stop_reason, id="msg_tool", usage=usage)


class TestAst2179ForcedToolTransport:
    @staticmethod
    def _client(monkeypatch, content=None, **kw) -> _BlocksClient:
        client = _BlocksClient([_tool_use()] if content is None else content, **kw)
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda *_a, **_k: client)
        return client

    @staticmethod
    async def _send(**kwargs):
        kwargs.setdefault("forced_tool", _TOOL)
        return await anthropic_mod.send_to_anthropic([{"type": "text", "text": "hi"}], model_code="claude-sonnet-4-6", **kwargs)

    def test_forced_tool_body_is_one_tool_and_a_named_choice(self) -> None:
        assert anthropic_mod._forced_tool_body(_TOOL) == {
            "tools": [{"name": "submit_grades", "input_schema": _TOOL["input_schema"]}],
            "tool_choice": {"type": "tool", "name": "submit_grades"},
        }

    @pytest.mark.asyncio
    async def test_ac3_request_carries_exactly_one_tool_and_forcing_choice(self, monkeypatch) -> None:
        client = self._client(monkeypatch)
        await self._send(response_format="json")
        call = client.calls[0]
        assert call["tools"] == [{"name": "submit_grades", "input_schema": _TOOL["input_schema"]}]
        assert call["tool_choice"] == {"type": "tool", "name": "submit_grades"}

    @pytest.mark.asyncio
    async def test_ac3_no_tool_keys_without_forced_tool(self, monkeypatch) -> None:
        client = self._client(monkeypatch, content=[SimpleNamespace(text='{"ok": true}')], stop_reason="end_turn")
        out = await self._send(forced_tool=None, response_format="json")
        assert out["parsed_response"] == {"ok": True}
        assert not {"tools", "tool_choice"} & set(client.calls[0])

    @pytest.mark.asyncio
    async def test_ac3_debug_logs_request_kwargs_and_response(self, monkeypatch, caplog) -> None:
        import logging

        from src.utils.logging import log_debug

        self._client(monkeypatch)
        # The project logger's debug() emits only while log_debug is on; dict args land JSON-encoded.
        token = log_debug.set(True)
        try:
            with caplog.at_level(logging.DEBUG, logger="src.external.anthropic"):
                await self._send()
        finally:
            log_debug.reset(token)
        lines = [r.getMessage() for r in caplog.records if r.levelno == logging.DEBUG]
        assert any("Calling messages.create:" in m and '"tool_choice": {"type": "tool", "name": "submit_grades"}' in m for m in lines)
        assert any("Response from messages.create:" in m for m in lines)

    @pytest.mark.asyncio
    async def test_forced_tool_with_web_search_is_refused(self, monkeypatch) -> None:
        client = self._client(monkeypatch)
        with pytest.raises(ValueError, match="cannot be combined"):
            await self._send(enable_web_search=True)
        assert client.calls == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize("response_format", [None, "text", "json"])
    async def test_tool_input_is_parsed_response_whatever_format(self, monkeypatch, response_format) -> None:
        # A stray text block next to the tool call is ignored — the tool input is the payload.
        self._client(monkeypatch, content=[SimpleNamespace(type="text", text="preamble"), _tool_use()])
        out = await self._send(response_format=response_format)
        assert out["success"] is True
        assert out["parsed_response"] == _TOOL_INPUT

    @pytest.mark.asyncio
    async def test_tool_input_agent_performance_reaches_timesheet(self, monkeypatch) -> None:
        ap = {"status": "failure", "failure_note": "JD text missing"}
        self._client(monkeypatch, content=[_tool_use(tool_input={"agent_performance": ap})])
        recorded: list = []
        await self._send(record_timesheet=lambda **kw: recorded.append(kw))
        assert (recorded[0]["agent_performance"], recorded[0]["failure_note"]) == ("failure", "JD text missing")

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("content", "error"),
        [
            ([SimpleNamespace(type="text", text='{"agent_performance": "success"}')], "has no 'submit_grades' tool call"),
            ([_tool_use(name="other_tool")], "has no 'submit_grades' tool call"),
            ([_tool_use(tool_input="000|DTA5")], "input is not an object"),
        ],
        ids=["text_only", "other_tool", "non_object_input"],
    )
    async def test_missing_or_malformed_tool_call_is_a_failure(self, monkeypatch, content, error) -> None:
        self._client(monkeypatch, content=content, stop_reason="end_turn")
        recorded: list = []
        out = await self._send(response_format="json", record_timesheet=lambda **kw: recorded.append(kw))
        assert out["success"] is False and out["parsed_response"] is None
        assert error in out["error"]
        assert recorded and recorded[0]["agent_performance"] == "failure"

    @pytest.mark.asyncio
    async def test_max_tokens_fails_closed_even_without_json_format(self, monkeypatch) -> None:
        self._client(monkeypatch, stop_reason="max_tokens")
        out = await self._send(response_format=None)
        assert out["success"] is False and out["failure_class"] == "max_tokens"
        assert out["parsed_response"] is None

    @pytest.mark.asyncio
    async def test_debug_raw_text_falls_back_to_tool_input_json(self, monkeypatch) -> None:
        # debug=True reads raw text off the reply; a tool-only reply must not break the call.
        seen: list = []
        monkeypatch.setattr(anthropic_mod, "emit_llm_call_debug", lambda **kw: seen.append(kw["raw_text"]))
        self._client(monkeypatch)
        out = await self._send(debug=True)
        assert out["success"] is True and out["parsed_response"] == _TOOL_INPUT
        assert seen == [json.dumps(_TOOL_INPUT)]

class TestAst2217ReceiptStubAndAttribution:
    """AST-2217 AC5 stub half + AC8 call-time attribution on Anthropic recorded rows."""

    def test_get_receipt_zero_stub_shape_and_null_cost(self) -> None:
        from src.utils.config import TIMESHEET_RECEIPT_FIELDS
        receipts = anthropic_mod.get_receipt(["id-a", "id-b"], api_key="ignored")
        assert len(receipts) == 2
        for row in receipts:
            assert set(row) == set(TIMESHEET_RECEIPT_FIELDS)
            assert row["platform_cost"] is None
            assert row["completion_status"] == "stub"
            assert row["native_tokens_prompt"] == 0
            assert row["native_tokens_completion"] == 0

    @pytest.mark.asyncio
    async def test_recorded_call_carries_attribution(self, monkeypatch, fake_anthropic_client) -> None:
        client = fake_anthropic_client(
            response_text='{"agent_performance":{"status":"success"},"agent_payload":{}}'
        )
        monkeypatch.setattr(anthropic_mod, "_get_client", lambda: client)
        recorded: list = []
        out = await anthropic_mod.send_to_anthropic(
            [{"type": "text", "text": "hi"}],
            model_code="claude-sonnet-4-6",
            response_format="json",
            record_timesheet=lambda **kw: recorded.append(kw),
            request_type="DISPATCH_AGENT",
            entity_type="job",
            entity_id="job-1",
        )
        assert out["success"] is True
        assert recorded
        row = recorded[0]
        assert row["request_type"] == "DISPATCH_AGENT"
        assert (row["entity_type"], row["entity_id"]) == ("job", "job-1")
        assert row["call_start"] and row["call_stop"]
        assert row["call_stop"] >= row["call_start"]
        assert row["response_char_length"] > 0
        assert row["response_item_count"] == 1
