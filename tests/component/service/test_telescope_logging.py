"""Telescope logging — Railway JSON, worker/job fields, per-job debug gating."""

from __future__ import annotations

import json
import logging

import pytest


@pytest.fixture
def lines(capsys):
    import logging_util as log_util

    logging.getLogger().handlers.clear()
    log_util.configure_logging()  # TELESCOPE_LOG_LEVEL default INFO
    log_util.set_worker_label("rep12345")

    def read() -> list[dict]:
        return [json.loads(ln) for ln in capsys.readouterr().out.splitlines() if ln.strip()]

    yield read
    log_util.set_worker_label(None)


class TestRailwayJsonLogging:
    def test_levels_map_to_railway_and_carry_worker(self, lines) -> None:
        log = logging.getLogger("worker")
        log.info("inf")
        log.warning("wrn")
        log.error("err")
        out = lines()
        assert [p["level"] for p in out] == ["info", "warn", "error"]
        assert all(p["worker"] == "rep12345" and p["logger"] == "worker" for p in out)

    def test_job_lines_carry_job_attempt_firefox(self, lines) -> None:
        import joblog

        tokens = joblog.begin_job("9c72bc3c-edc9-4c47", attempt=2, max_attempts=4, debug=False)
        joblog.bind_firefox("F-003")
        logging.getLogger("worker").info("done")
        joblog.end_job(tokens)
        logging.getLogger("worker").info("after")
        done, after = lines()
        assert (done["job"], done["attempt"], done["firefox"]) == ("9c72bc3c", "2/4", "F-003")
        assert "job" not in after and "firefox" not in after

    def test_debug_prints_only_for_debug_jobs_and_own_loggers(self, lines) -> None:
        import joblog

        logging.getLogger("scrape").debug("hidden: no debug job")
        tokens = joblog.begin_job("aaaaaaaa-1", attempt=1, max_attempts=4, debug=True)
        logging.getLogger("scrape").debug("shown: debug job")
        logging.getLogger("asyncpg").debug("hidden: library logger")
        joblog.end_job(tokens)
        tokens = joblog.begin_job("bbbbbbbb-1", attempt=1, max_attempts=4, debug=False)
        logging.getLogger("scrape").debug("hidden: job without debug")
        joblog.end_job(tokens)
        out = lines()
        assert [p["message"] for p in out] == ["shown: debug job"]
        assert out[0]["level"] == "debug" and out[0]["job"] == "aaaaaaaa"

    def test_settings_log_level_from_env(self, monkeypatch) -> None:
        import importlib

        import settings as settings_mod

        monkeypatch.setenv("TELESCOPE_LOG_LEVEL", "WARNING")
        importlib.reload(settings_mod)
        assert settings_mod.settings.log_level == "WARNING"
        monkeypatch.delenv("TELESCOPE_LOG_LEVEL")
        importlib.reload(settings_mod)


class TestCaptureSummary:
    def test_sizes_per_field(self) -> None:
        import joblog

        assert joblog.capture_summary({"text": "abcd", "links": [{}, {}]}) == "text:4 links:2"
        assert joblog.capture_summary({"html": ["ab", "c"]}) == "html:3(2 matches)"
        assert joblog.capture_summary({"final_url": "x"}) == "-"
