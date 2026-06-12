"""Component tests for app_log table cluster (AST-392)."""

from __future__ import annotations


# Branches: append row; filter by batch/level.
class TestAddLogEntry:
    def test_appends_log_row(self, sqlite_in_memory) -> None:
        assert sqlite_in_memory.add_log_entry("INFO", "tests", "hello", batch_id="batch-1") is True


class TestListLogEntries:
    def test_filters_by_batch_and_level(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.add_log_entry("INFO", "tests", "keep", batch_id="batch-1")
        db.add_log_entry("ERROR", "tests", "drop", batch_id="batch-2")
        rows = db.list_log_entries(batch_id="batch-1", level="INFO")
        assert len(rows) == 1
        assert rows[0]["message"] == "keep"
