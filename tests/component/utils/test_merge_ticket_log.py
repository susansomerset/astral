"""Component tests for src/utils/merge_ticket_log.py (AST-681)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.utils import merge_ticket_log as mtl
from src.utils.config import MERGE_TICKET_LOG_CONFIG


@pytest.fixture
def log_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "merge_ticket_log.json"
    monkeypatch.setitem(MERGE_TICKET_LOG_CONFIG, "log_path", path)
    return path


class TestReadMergeTicketLog:
    def test_read_empty_when_missing(self, log_path: Path) -> None:
        assert mtl.read_merge_ticket_log() == []

    def test_read_returns_file_order(self, log_path: Path) -> None:
        log_path.write_text(
            json.dumps(
                [
                    {"ticket_id": "AST-100", "recorded_at": "2026-01-01T00:00:00+00:00"},
                    {"ticket_id": "AST-200", "recorded_at": "2026-01-02T00:00:00+00:00"},
                ]
            ),
            encoding="utf-8",
        )
        entries = mtl.read_merge_ticket_log()
        assert len(entries) == 2
        assert entries[0]["ticket_id"] == "AST-100"
        assert entries[1]["ticket_id"] == "AST-200"

    def test_read_rejects_non_array(self, log_path: Path) -> None:
        log_path.write_text('{"bad": true}', encoding="utf-8")
        with pytest.raises(ValueError, match="JSON array"):
            mtl.read_merge_ticket_log()


class TestAppendMergeTicketLog:
    def test_append_and_read_preserves_order(self, log_path: Path) -> None:
        mtl.append_merge_ticket_log("ast-100")
        mtl.append_merge_ticket_log("AST-200")
        entries = mtl.read_merge_ticket_log()
        assert len(entries) == 2
        assert entries[0]["ticket_id"] == "AST-100"
        assert entries[1]["ticket_id"] == "AST-200"
        assert "recorded_at" in entries[0]
        assert "recorded_at" in entries[1]

    def test_append_rejects_invalid_id(self, log_path: Path) -> None:
        with pytest.raises(ValueError, match="invalid ticket id"):
            mtl.append_merge_ticket_log("foo")

    def test_append_never_truncates(self, log_path: Path) -> None:
        for n in (100, 200, 300):
            mtl.append_merge_ticket_log(f"AST-{n}")
        assert len(mtl.read_merge_ticket_log()) == 3

    def test_append_same_id_updates_timestamp_no_duplicate(self, log_path: Path) -> None:
        first = mtl.append_merge_ticket_log("AST-700")
        mtl.append_merge_ticket_log("AST-100")
        second = mtl.append_merge_ticket_log("AST-700")
        entries = mtl.read_merge_ticket_log()
        assert len(entries) == 2
        assert entries[0]["ticket_id"] == "AST-100"
        assert entries[1]["ticket_id"] == "AST-700"
        assert entries[1]["recorded_at"] >= first["recorded_at"]
        assert second["recorded_at"] == entries[1]["recorded_at"]
