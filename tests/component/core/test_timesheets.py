"""Component tests for src/core/timesheets.py (AST-393)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.core import timesheets as timesheets_mod


class TestRecordTimesheetEntry:
    def test_delegates_to_database_add(self, monkeypatch: pytest.MonkeyPatch) -> None:
        add = MagicMock(return_value=True)
        monkeypatch.setattr(timesheets_mod, "_add_timesheet_entry", add)
        timesheets_mod.record_timesheet_entry(agent_req_id="req-1", batch_id="batch-1", batch_size=1)
        add.assert_called_once_with(agent_req_id="req-1", batch_id="batch-1", batch_size=1)
