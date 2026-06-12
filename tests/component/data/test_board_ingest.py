"""Component tests for board listing ingest (AST-417)."""

from __future__ import annotations

import os
import re

import pytest

os.environ.setdefault("GMAIL_USER", "astral.test@example.com")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("GOOGLE_REFRESH_TOKEN", "test-refresh-token")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")

from src.core.boards import save_board_search
from src.core.tracker import ingest_board_listings
from src.utils.config import BOARD_CONFIG


_LISTING = '<a href="https://jobs.example.com/senior-engineer">Senior Engineer</a>'
_PARSE = {}


@pytest.fixture
def board_ingest_env(sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    monkeypatch.setattr("src.core.tracker.database", sqlite_in_memory)
    monkeypatch.setattr("src.core.boards.database", sqlite_in_memory)
    sqlite_in_memory._board_search_schema_ensured = False
    sqlite_in_memory._board_search_run_schema_ensured = False
    monkeypatch.setitem(BOARD_CONFIG, "a16z", {"status": "adopted"})
    sqlite_in_memory.save_candidate("cand-1", state="NEW")
    row = save_board_search("cand-1", "a16z", "Eng roles", {"title_query": "engineer"})
    return {
        "candidate_id": "cand-1",
        "board_key": "a16z",
        "board_search_id": row["board_search_id"],
    }


class TestIngestBoardListings:
    def test_duplicate_listing_skipped(self, board_ingest_env: dict[str, str]) -> None:
        env = board_ingest_env
        first = ingest_board_listings(
            env["candidate_id"],
            env["board_key"],
            env["board_search_id"],
            "batch-1",
            [_LISTING],
            None,
            _PARSE,
        )
        second = ingest_board_listings(
            env["candidate_id"],
            env["board_key"],
            env["board_search_id"],
            "batch-2",
            [_LISTING],
            None,
            _PARSE,
        )
        assert first == {"new": 1, "duplicates": 0, "invalid_title": 0}
        assert second == {"new": 0, "duplicates": 1, "invalid_title": 0}

    def test_title_filter_counts_invalid_title(self, board_ingest_env: dict[str, str]) -> None:
        env = board_ingest_env
        matchers = [re.compile(r"Director", re.I)]
        counts = ingest_board_listings(
            env["candidate_id"],
            env["board_key"],
            env["board_search_id"],
            "batch-3",
            [_LISTING],
            matchers,
            _PARSE,
        )
        assert counts == {"new": 0, "duplicates": 0, "invalid_title": 1}

    def test_records_board_search_run_and_job_metadata(
        self, board_ingest_env: dict[str, str], sqlite_in_memory
    ) -> None:
        env = board_ingest_env
        ingest_board_listings(
            env["candidate_id"],
            env["board_key"],
            env["board_search_id"],
            "batch-4",
            [_LISTING],
            None,
            _PARSE,
        )
        conn = sqlite_in_memory._get_connection()
        try:
            run = conn.execute(
                "SELECT new, duplicates, invalid_title FROM board_search_run WHERE batch_id = ?",
                ("batch-4",),
            ).fetchone()
            assert run is not None
            assert run[0] == 1 and run[1] == 0 and run[2] == 0

            job = conn.execute(
                """SELECT state, board_search_id, json_extract(job_data, '$.board_key') AS bk
                   FROM job WHERE board_search_id = ?""",
                (env["board_search_id"],),
            ).fetchone()
            assert job is not None
            assert job[0] == "NEW"
            assert job[1] == env["board_search_id"]
            assert job[2] == "a16z"
        finally:
            conn.close()
