"""Railway-native JSON logging for Telescope service."""

from __future__ import annotations

import json
import logging

import pytest


class TestRailwayJsonLogging:
    def test_handler_maps_python_levels_to_railway(self, capsys) -> None:
        import logging_util as log_util

        root = logging.getLogger()
        root.handlers.clear()
        log_util.configure_logging()
        root.setLevel(logging.DEBUG)
        for handler in root.handlers:
            handler.setLevel(logging.DEBUG)
        log = log_util.get_logger("app")

        log.debug("dbg")
        log.info("inf")
        log.warning("wrn")
        log.error("err")

        lines = [ln for ln in capsys.readouterr().out.strip().splitlines() if ln]
        payloads = [json.loads(ln) for ln in lines]
        assert [p["level"] for p in payloads] == ["debug", "info", "warn", "error"]
        assert payloads[1]["message"] == "inf"
        assert payloads[1]["logger"] == "app"

    def test_railway_log_explicit_debug_bypasses_root_level(self, capsys) -> None:
        import logging_util as log_util

        log = log_util.get_logger("scrape_debug")
        log_util.railway_log(
            "debug",
            log,
            "telescope scrape context_created",
            event="context_created",
            firefox="F-001",
        )
        payload = json.loads(capsys.readouterr().out.strip())
        assert payload["level"] == "debug"
        assert payload["event"] == "context_created"
        assert payload["firefox"] == "F-001"

    def test_settings_log_level_from_env(self, monkeypatch) -> None:
        import importlib

        import settings as settings_mod

        monkeypatch.setenv("TELESCOPE_LOG_LEVEL", "WARNING")
        importlib.reload(settings_mod)
        assert settings_mod.settings.log_level == "WARNING"
        importlib.reload(settings_mod)
