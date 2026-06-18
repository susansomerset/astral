"""AST-729: cleanup duplicate job identity rows and board-gaze placeholder jobs."""

from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path
from typing import Iterator
from unittest.mock import MagicMock

import pytest

import src.data.database as db_mod

REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = REPO_ROOT / "scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py"
_BOARD_PREFIX = "__board__"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "cleanup_duplicate_and_board_gaze_jobs", _SCRIPT
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_module()


@pytest.fixture
def job_db() -> Iterator[tuple[sqlite3.Connection, str]]:
    db_name = f"ast729-{id(object())}"
    db_uri = f"file:{db_name}?mode=memory&cache=shared"
    conn = sqlite3.connect(db_uri, uri=True)
    db_mod._job_schema_ensured = False
    db_mod._ensure_job_schema(conn)
    yield conn, db_uri
    conn.close()


def _insert_job(
    conn: sqlite3.Connection,
    *,
    astral_job_id: str,
    company: str,
    job_title: str | None = None,
    company_job_id: str | None = None,
    created_at: str | None = None,
    state: str = "JD_READY",
) -> None:
    conn.execute(
        """
        INSERT INTO job (
            astral_job_id, company, job_title, company_job_id, state, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (astral_job_id, company, job_title, company_job_id, state, created_at),
    )
    conn.commit()


def _patch_db(monkeypatch: pytest.MonkeyPatch, db_uri: str) -> None:
    db_mod._job_schema_ensured = False

    def _get_connection() -> sqlite3.Connection:
        return sqlite3.connect(db_uri, uri=True)

    monkeypatch.setattr(_mod, "_run_with_retry", lambda fn: fn())
    monkeypatch.setattr(_mod, "_get_connection", _get_connection)


class TestFindDuplicateIdentityGroups:
    def test_finds_groups_excludes_board_and_incomplete(
        self, job_db: tuple[sqlite3.Connection, str]
    ) -> None:
        job_conn, _ = job_db
        _insert_job(
            job_conn,
            astral_job_id="dup-old",
            company="acme",
            job_title="Engineer",
            company_job_id="123",
            created_at="2026-01-01 00:00:00",
        )
        _insert_job(
            job_conn,
            astral_job_id="dup-new",
            company="acme",
            job_title="Engineer",
            company_job_id="123",
            created_at="2026-06-01 00:00:00",
        )
        _insert_job(
            job_conn,
            astral_job_id="board-dup-a",
            company=f"{_BOARD_PREFIX}indeed",
            job_title="Nurse",
            company_job_id="b1",
            created_at="2026-01-01 00:00:00",
        )
        _insert_job(
            job_conn,
            astral_job_id="board-dup-b",
            company=f"{_BOARD_PREFIX}indeed",
            job_title="Nurse",
            company_job_id="b1",
            created_at="2026-06-01 00:00:00",
        )
        _insert_job(
            job_conn,
            astral_job_id="incomplete",
            company="acme",
            job_title="",
            company_job_id="999",
        )

        groups = _mod.find_duplicate_identity_groups(job_conn, company_filter=None)

        assert len(groups) == 1
        assert groups[0]["company"] == "acme"
        assert [m["astral_job_id"] for m in groups[0]["members"]] == [
            "dup-old",
            "dup-new",
        ]

    def test_company_filter(self, job_db: tuple[sqlite3.Connection, str]) -> None:
        job_conn, _ = job_db
        for company, jid in (("acme", "a1"), ("acme", "a2"), ("other", "o1"), ("other", "o2")):
            _insert_job(
                job_conn,
                astral_job_id=jid,
                company=company,
                job_title="Role",
                company_job_id="x",
                created_at="2026-01-01 00:00:00" if jid.endswith("1") else "2026-06-01 00:00:00",
            )

        groups = _mod.find_duplicate_identity_groups(job_conn, company_filter="acme")

        assert len(groups) == 1
        assert groups[0]["company"] == "acme"

    def test_survivor_order_created_at_then_astral_job_id(
        self, job_db: tuple[sqlite3.Connection, str]
    ) -> None:
        job_conn, _ = job_db
        _insert_job(
            job_conn,
            astral_job_id="job-z",
            company="acme",
            job_title="Role",
            company_job_id="tie",
            created_at="2026-01-01 00:00:00",
        )
        _insert_job(
            job_conn,
            astral_job_id="job-a",
            company="acme",
            job_title="Role",
            company_job_id="tie",
            created_at="2026-01-01 00:00:00",
        )

        members = _mod.find_duplicate_identity_groups(job_conn, None)[0]["members"]

        assert members[0]["astral_job_id"] == "job-a"
        assert members[1]["astral_job_id"] == "job-z"


class TestDeleteJobsByAstralJobIds:
    def test_deletes_and_noop_empty(self, job_db: tuple[sqlite3.Connection, str]) -> None:
        job_conn, _ = job_db
        _insert_job(
            job_conn,
            astral_job_id="keep-me",
            company="acme",
            job_title="Role",
            company_job_id="1",
        )
        _insert_job(
            job_conn,
            astral_job_id="drop-me",
            company="acme",
            job_title="Role",
            company_job_id="2",
        )

        assert _mod.delete_jobs_by_astral_job_ids(job_conn, []) == 0
        deleted = _mod.delete_jobs_by_astral_job_ids(job_conn, ["drop-me"])

        assert deleted == 1
        rows = job_conn.execute("SELECT astral_job_id FROM job ORDER BY astral_job_id").fetchall()
        assert [r[0] for r in rows] == ["keep-me"]


class TestBoardGazeCleanup:
    def test_dry_run_no_delete(
        self,
        job_db: tuple[sqlite3.Connection, str],
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        job_conn, db_uri = job_db
        _insert_job(
            job_conn,
            astral_job_id="board-1",
            company=f"{_BOARD_PREFIX}indeed",
            job_title="Role",
            company_job_id="1",
        )
        _patch_db(monkeypatch, db_uri)
        counts = {k: 0 for k in _mod._COUNT_KEYS}

        _mod.run_board_gaze_cleanup(dry_run=True, counts=counts)

        assert counts["board_jobs_scanned"] == 1
        assert counts["board_jobs_deleted"] == 1
        assert job_conn.execute("SELECT COUNT(*) FROM job").fetchone()[0] == 1
        assert "DRY RUN" in capsys.readouterr().out

    def test_live_deletes_board_rows(
        self, job_db: tuple[sqlite3.Connection, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        job_conn, db_uri = job_db
        _insert_job(
            job_conn,
            astral_job_id="board-1",
            company=f"{_BOARD_PREFIX}indeed",
            job_title="Role",
            company_job_id="1",
        )
        _insert_job(
            job_conn,
            astral_job_id="real-1",
            company="acme",
            job_title="Role",
            company_job_id="1",
        )
        _patch_db(monkeypatch, db_uri)
        counts = {k: 0 for k in _mod._COUNT_KEYS}

        _mod.run_board_gaze_cleanup(dry_run=False, counts=counts)

        assert counts["board_jobs_deleted"] == 1
        rows = job_conn.execute("SELECT astral_job_id FROM job").fetchall()
        assert [r[0] for r in rows] == ["real-1"]

    def test_no_board_rows_message(
        self,
        job_db: tuple[sqlite3.Connection, str],
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        job_conn, db_uri = job_db
        _patch_db(monkeypatch, db_uri)
        counts = {k: 0 for k in _mod._COUNT_KEYS}

        _mod.run_board_gaze_cleanup(dry_run=False, counts=counts)

        assert counts["board_jobs_scanned"] == 0
        assert "no placeholder-company jobs found" in capsys.readouterr().out


class TestIdentityDedupe:
    def test_dry_run_keeps_all_rows(
        self,
        job_db: tuple[sqlite3.Connection, str],
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        job_conn, db_uri = job_db
        _insert_job(
            job_conn,
            astral_job_id="keep",
            company="acme",
            job_title="Role",
            company_job_id="1",
            created_at="2026-01-01 00:00:00",
        )
        _insert_job(
            job_conn,
            astral_job_id="drop",
            company="acme",
            job_title="Role",
            company_job_id="1",
            created_at="2026-06-01 00:00:00",
        )
        _patch_db(monkeypatch, db_uri)
        counts = {k: 0 for k in _mod._COUNT_KEYS}

        _mod.run_identity_dedupe(dry_run=True, company_filter=None, counts=counts)

        assert counts["dedupe_groups"] == 1
        assert counts["dedupe_deleted"] == 0
        assert job_conn.execute("SELECT COUNT(*) FROM job").fetchone()[0] == 2
        assert "DRY RUN" in capsys.readouterr().out

    def test_live_deletes_duplicates_keeps_earliest(
        self, job_db: tuple[sqlite3.Connection, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        job_conn, db_uri = job_db
        _insert_job(
            job_conn,
            astral_job_id="keep",
            company="acme",
            job_title="Role",
            company_job_id="1",
            created_at="2026-01-01 00:00:00",
        )
        _insert_job(
            job_conn,
            astral_job_id="drop",
            company="acme",
            job_title="Role",
            company_job_id="1",
            created_at="2026-06-01 00:00:00",
        )
        _patch_db(monkeypatch, db_uri)
        counts = {k: 0 for k in _mod._COUNT_KEYS}

        _mod.run_identity_dedupe(dry_run=False, company_filter=None, counts=counts)

        assert counts["dedupe_deleted"] == 1
        row = job_conn.execute("SELECT astral_job_id FROM job").fetchone()
        assert row[0] == "keep"

    def test_group_error_increments_errors(
        self,
        job_db: tuple[sqlite3.Connection, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        job_conn, db_uri = job_db
        _insert_job(
            job_conn,
            astral_job_id="a1",
            company="acme",
            job_title="Role",
            company_job_id="1",
            created_at="2026-01-01 00:00:00",
        )
        _insert_job(
            job_conn,
            astral_job_id="a2",
            company="acme",
            job_title="Role",
            company_job_id="1",
            created_at="2026-06-01 00:00:00",
        )
        _patch_db(monkeypatch, db_uri)
        monkeypatch.setattr(
            _mod,
            "delete_jobs_by_astral_job_ids",
            MagicMock(side_effect=RuntimeError("boom")),
        )
        counts = {k: 0 for k in _mod._COUNT_KEYS}

        _mod.run_identity_dedupe(dry_run=False, company_filter=None, counts=counts)

        assert counts["errors"] == 1
        assert counts["dedupe_deleted"] == 0


class TestRunCleanup:
    def test_phase_order_and_skip_flags(
        self, job_db: tuple[sqlite3.Connection, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        job_conn, db_uri = job_db
        _insert_job(
            job_conn,
            astral_job_id="board-1",
            company=f"{_BOARD_PREFIX}indeed",
            job_title="Role",
            company_job_id="1",
        )
        _insert_job(
            job_conn,
            astral_job_id="dup-old",
            company="acme",
            job_title="Role",
            company_job_id="1",
            created_at="2026-01-01 00:00:00",
        )
        _insert_job(
            job_conn,
            astral_job_id="dup-new",
            company="acme",
            job_title="Role",
            company_job_id="1",
            created_at="2026-06-01 00:00:00",
        )
        _patch_db(monkeypatch, db_uri)

        full = _mod.run_cleanup(
            dry_run=False,
            skip_dedupe=False,
            skip_board=False,
            company_filter=None,
        )
        assert full["board_jobs_deleted"] == 1
        assert full["dedupe_deleted"] == 1
        assert job_conn.execute("SELECT astral_job_id FROM job").fetchone()[0] == "dup-old"

        _insert_job(
            job_conn,
            astral_job_id="board-only",
            company=f"{_BOARD_PREFIX}other",
            job_title="Role",
            company_job_id="2",
        )
        board_only = _mod.run_cleanup(
            dry_run=False,
            skip_dedupe=True,
            skip_board=False,
            company_filter=None,
        )
        assert board_only["board_jobs_deleted"] == 1
        assert board_only["dedupe_deleted"] == 0

    def test_dry_run_banner_and_summary(
        self,
        job_db: tuple[sqlite3.Connection, str],
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        job_conn, db_uri = job_db
        _patch_db(monkeypatch, db_uri)

        _mod.run_cleanup(
            dry_run=True,
            skip_dedupe=True,
            skip_board=True,
            company_filter=None,
        )

        out = capsys.readouterr().out
        assert "=== DRY RUN — no DB writes ===" in out
        assert "=== DRY RUN SUMMARY ===" in out
