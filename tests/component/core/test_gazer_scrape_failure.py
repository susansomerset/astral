"""AST-2002 · AST-1997 bug-repro: process_gazer_batch records the real scrape failure reason."""

from __future__ import annotations

import asyncio
from typing import Dict
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import gazer as gazer_mod


# short_name -> exception scrape_one raises for it; "nosite" has a blank job_site so it is never scraped.
_RAISES: Dict[str, BaseException] = {
    "trustmarkbenefits_com": RuntimeError("net::ERR_NAME_NOT_RESOLVED"),
    "timeoutco": asyncio.TimeoutError(),
}

# Expected failure reason per company (AST-1997 plan § Proposed change).
_EXPECTED = {
    "trustmarkbenefits_com": "Scrape failed: RuntimeError: net::ERR_NAME_NOT_RESOLVED",
    "timeoutco": "Scrape failed: TimeoutError",  # empty str(e) -> no trailing ": "
    "nosite": "No job_site to scrape",
}


class TestProcessGazerBatchFailureMessage:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("debug", [False, True])
    async def test_failure_message_carries_scrape_reason(
        self, monkeypatch: pytest.MonkeyPatch, debug: bool
    ) -> None:
        monkeypatch.setattr(gazer_mod, "check_connectivity", AsyncMock(return_value=True))

        async def _scrape(short_name: str, job_site: str):
            raise _RAISES[short_name]

        monkeypatch.setattr(gazer_mod, "scrape_one", _scrape)
        record = MagicMock()
        monkeypatch.setattr(gazer_mod, "record_to_company_job_scan", record)
        # Keep debug=True from flipping the module logger's global debug flag for later tests.
        monkeypatch.setattr(gazer_mod, "_log", MagicMock())

        outcomes = await gazer_mod.process_gazer_batch(
            "batch-1",
            [
                {"short_name": "trustmarkbenefits_com", "job_site": "https://example.com/careers"},
                {"short_name": "timeoutco", "job_site": "https://example.com/jobs"},
                {"short_name": "nosite", "job_site": "  "},
            ],
            debug=debug,
        )

        # Outcome dict message (what roster logs as -> ERROR_GAZE [...]).
        assert {o["short_name"]: o["message"] for o in outcomes} == _EXPECTED
        assert all(o["status"] == "failure" for o in outcomes)
        # company_job_scan row: short_name is the 2nd positional arg.
        recorded = {c.args[1]: c.kwargs["failure_message"] for c in record.call_args_list}
        assert recorded == _EXPECTED
