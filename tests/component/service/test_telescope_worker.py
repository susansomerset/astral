"""Telescope queue worker — job policy, result writes, heartbeat, /healthz (no Postgres)."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("asyncpg")

from fastapi.testclient import TestClient  # noqa: E402

import jobqueue  # noqa: E402
import worker as worker_mod  # noqa: E402
from scrape import ScrapeError, parse_request  # noqa: E402


def _job(attempts: int = 1, max_attempts: int = 4, **request: Any) -> jobqueue.ClaimedJob:
    return jobqueue.ClaimedJob(
        id="00000000-0000-0000-0000-000000000001",
        request={"url": "https://example.com", "fields": ["text"], **request},
        attempts=attempts,
        max_attempts=max_attempts,
    )


def _json_lines(capsys) -> list[dict]:
    return [json.loads(ln) for ln in capsys.readouterr().out.splitlines() if ln.strip()]


@pytest.fixture(autouse=True)
def _json_logging():
    import logging

    import logging_util

    logging.getLogger().handlers.clear()
    logging_util.configure_logging()
    yield


def _worker() -> worker_mod.QueueWorker:
    return worker_mod.QueueWorker(MagicMock(), MagicMock(), worker_id="w-1", concurrency=2)


class TestParseRequest:
    def test_bad_selector_is_bad_request(self) -> None:
        with pytest.raises(ScrapeError) as exc:
            parse_request({"url": "https://example.com", "class_name": "bad class!"})
        assert exc.value.error_class == "bad_request"

    def test_blank_url_is_bad_request(self) -> None:
        with pytest.raises(ScrapeError) as exc:
            parse_request({"url": "  "})
        assert exc.value.error_class == "bad_request"

    def test_defaults_text_links_expand_on_wait_ready_off(self) -> None:
        req, sel = parse_request({"url": "https://example.com"})
        assert req.fields == ["text", "links"]
        assert req.expand is True and req.wait_ready is False and req.debug is False
        assert sel is None


class TestRetryPolicy:
    def test_bad_request_never_retries(self) -> None:
        assert _worker()._retry_delay(_job(attempts=1), "bad_request") is None

    def test_exponential_until_attempts_exhausted(self) -> None:
        w = _worker()
        assert w._retry_delay(_job(attempts=1), "scrape_failed") == 2.0
        assert w._retry_delay(_job(attempts=3), "scrape_failed") == 8.0
        assert w._retry_delay(_job(attempts=4), "scrape_failed") is None

    def test_timeout_gets_one_retry(self) -> None:
        w = _worker()
        assert w._retry_delay(_job(attempts=1), "timeout") == 2.0
        assert w._retry_delay(_job(attempts=2), "timeout") is None


class TestRunJob:
    async def test_success_writes_result_and_logs_done(self, monkeypatch, capsys) -> None:
        result = {"final_url": "https://example.com/", "text": "hi", "scrape_meta": {}}
        monkeypatch.setattr(worker_mod, "run_scrape", AsyncMock(return_value=result))
        complete = AsyncMock(return_value=True)
        monkeypatch.setattr(jobqueue, "complete", complete)

        await _worker()._run_job(_job(debug=True))

        assert complete.await_args.kwargs["result"] == result
        assert complete.await_args.kwargs["worker_id"] == "w-1"
        out = _json_lines(capsys)
        done = [p for p in out if "telescope job done" in p["message"]]
        assert len(done) == 1 and done[0]["level"] == "info"
        assert done[0]["message"].startswith("00000000 | telescope job done: https://example.com -> https://example.com/")
        assert done[0]["job"] == "00000000" and done[0]["attempt"] == "1/4"
        assert any(p["level"] == "debug" and p["message"].startswith("Claimed job") for p in out)

    async def test_no_debug_lines_without_debug_flag(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(
            worker_mod, "run_scrape", AsyncMock(return_value={"final_url": "x", "text": ""})
        )
        monkeypatch.setattr(jobqueue, "complete", AsyncMock(return_value=True))
        await _worker()._run_job(_job())
        assert all(p["level"] != "debug" for p in _json_lines(capsys))

    async def test_retry_is_warning_with_first_line_only(self, monkeypatch, capsys) -> None:
        err = "TimeoutError: Page.goto: Timeout 30000ms exceeded.\nCall log:\n  - navigating"
        monkeypatch.setattr(
            worker_mod, "run_scrape", AsyncMock(side_effect=ScrapeError("scrape_failed", err))
        )
        monkeypatch.setattr(jobqueue, "fail", AsyncMock(return_value="queued"))
        await _worker()._run_job(_job())
        (line,) = [p for p in _json_lines(capsys) if "retry" in p["message"]]
        assert line["level"] == "warn"
        assert line["message"].endswith("— TimeoutError: Page.goto: Timeout 30000ms exceeded.")

    async def test_terminal_failure_is_error(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(
            worker_mod, "run_scrape", AsyncMock(side_effect=ScrapeError("scrape_failed", "boom"))
        )
        monkeypatch.setattr(jobqueue, "fail", AsyncMock(return_value="failed"))
        await _worker()._run_job(_job(attempts=4))
        (line,) = [p for p in _json_lines(capsys) if "failed" in p["message"]]
        assert line["level"] == "error"


class TestStatsLine:
    def test_logs_when_active_and_resets(self, capsys) -> None:
        w = _worker()
        w._firefox.status = MagicMock(return_value=("F-003", 37))
        w._stats = {"done": 5, "retried": 1, "failed": 0}
        w._stats_at -= 61
        w._maybe_log_stats()
        (line,) = _json_lines(capsys)
        assert line["message"].startswith("w-1 | telescope stats: in_flight:0/2 done:5 retried:1 failed:0")
        assert line["message"].endswith("firefox:F-003 served:37")
        assert w._stats == {"done": 0, "retried": 0, "failed": 0}

    def test_silent_when_idle(self, capsys) -> None:
        w = _worker()
        w._stats_at -= 61
        w._maybe_log_stats()
        assert _json_lines(capsys) == []

    async def test_failure_requeues_with_backoff(self, monkeypatch) -> None:
        monkeypatch.setattr(
            worker_mod,
            "run_scrape",
            AsyncMock(side_effect=ScrapeError("scrape_failed", "boom")),
        )
        fail = AsyncMock(return_value="queued")
        monkeypatch.setattr(jobqueue, "fail", fail)

        await _worker()._run_job(_job(attempts=2))

        kw = fail.await_args.kwargs
        assert kw["error_class"] == "scrape_failed"
        assert kw["retry_in_seconds"] == 4.0


class TestHeartbeat:
    async def test_jobs_claimed_mid_heartbeat_are_not_cancelled(self, monkeypatch) -> None:
        w = _worker()
        old = asyncio.create_task(asyncio.sleep(60))
        w._in_flight["old"] = old

        async def fake_heartbeat(_db, **kw):
            # A claim lands while the heartbeat query is in flight.
            w._in_flight["new"] = new
            w._stopping.set()
            return set(kw["job_ids"])

        new = asyncio.create_task(asyncio.sleep(60))
        monkeypatch.setattr(jobqueue, "heartbeat", fake_heartbeat)
        await w._heartbeat_loop()
        assert not new.cancelled() and not old.cancelled()
        old.cancel()
        new.cancel()

    async def test_job_missing_from_db_is_cancelled(self, monkeypatch) -> None:
        w = _worker()
        task = asyncio.create_task(asyncio.sleep(60))
        w._in_flight["gone"] = task

        async def fake_heartbeat(_db, **_kw):
            w._stopping.set()
            return set()

        monkeypatch.setattr(jobqueue, "heartbeat", fake_heartbeat)
        await w._heartbeat_loop()
        await asyncio.sleep(0)
        assert task.cancelled()


class TestResultCodec:
    def test_round_trips_nul_and_lone_surrogates(self) -> None:
        # jsonb would reject both — which is why results are compressed bytea.
        payload = {"text": "a\x00b\ud800c", "links": [{"href": "/x"}]}
        assert jobqueue.decode_result(jobqueue.encode_result(payload)) == payload


class TestHealthz:
    def _client(self, *, db_ok: bool, browser_ok: bool) -> TestClient:
        import app as app_mod

        firefox = MagicMock()
        firefox.health_poke = AsyncMock(return_value=browser_ok)
        w = _worker()
        w.db_ok = db_ok
        app_mod.app.state.firefox = firefox
        app_mod.app.state.worker = w
        return TestClient(app_mod.app)  # no `with` — lifespan (DB, Firefox) not started

    def test_ok_without_auth(self) -> None:
        resp = self._client(db_ok=True, browser_ok=True).get("/healthz")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_db_down_is_503(self) -> None:
        resp = self._client(db_ok=False, browser_ok=True).get("/healthz")
        assert resp.status_code == 503
        assert resp.json()["db_ok"] is False
