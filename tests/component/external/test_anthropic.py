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

    def test_wraps_top_level_json_string_encoded_grades(self) -> None:
        out = anthropic_mod._parse_json_response('"000|DTA5|GCA4"')
        assert out == {"agent_payload": "000|DTA5|GCA4"}

    def test_wraps_bare_encoded_text_without_json(self) -> None:
        text = "[evaluate_jd_batch_x]\n000|DTA5|GCA4"
        out = anthropic_mod._parse_json_response(text)
        assert out == {"agent_payload": "000|DTA5|GCA4"}

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
