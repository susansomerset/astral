"""AST-727: backfill latest-only agent_responses on job and company rows."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = REPO_ROOT / "scripts/migrations/backfill_latest_only_rubric_entity_data.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "backfill_latest_only_rubric_entity_data", _SCRIPT
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_module()


def _duplicate_refs() -> list[dict[str, Any]]:
    return [
        {"task_key": "", "batch_id": "orphan"},
        {"task_key": "consult_get", "created_at": "2026-06-01 00:00:00", "batch_id": "old"},
        {"task_key": "consult_get", "created_at": "2026-06-02 00:00:00", "batch_id": "new"},
    ]


class TestBackfillCompanies:
    def test_dry_run_reports_without_write(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(
            _mod,
            "list_companies",
            lambda: [{"short_name": "acme", "agent_responses": _duplicate_refs()}],
        )
        update = MagicMock()
        monkeypatch.setattr(_mod, "update_company", update)

        counts = _mod.backfill_companies(dry_run=True, company=None)

        assert counts["scanned"] == 1
        assert counts["updated"] == 1
        assert counts["unchanged"] == 0
        assert counts["dropped_empty_key_total"] == 1
        assert counts["deduped_refs_removed_total"] == 1
        update.assert_not_called()
        assert "DRY RUN" in capsys.readouterr().out

    def test_live_updates_company_agent_responses(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            _mod,
            "list_companies",
            lambda: [{"short_name": "acme", "agent_responses": _duplicate_refs()}],
        )
        saved: list[tuple[str, list[dict[str, Any]]]] = []

        def _update(short_name: str, *, agent_responses: list[dict[str, Any]]) -> None:
            saved.append((short_name, agent_responses))

        monkeypatch.setattr(_mod, "update_company", _update)

        counts = _mod.backfill_companies(dry_run=False, company=None)

        assert counts["updated"] == 1
        assert len(saved) == 1
        assert saved[0][0] == "acme"
        assert len(saved[0][1]) == 1
        assert saved[0][1][0]["batch_id"] == "new"

    def test_unchanged_and_not_found(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        already = [{"task_key": "consult_do", "created_at": "2026-06-01 00:00:00", "batch_id": "b1"}]
        monkeypatch.setattr(
            _mod,
            "list_companies",
            lambda: [{"short_name": "acme", "agent_responses": already}],
        )
        monkeypatch.setattr(_mod, "update_company", MagicMock())

        unchanged = _mod.backfill_companies(dry_run=False, company=None)
        assert unchanged["unchanged"] == 1
        assert unchanged["updated"] == 0

        missing = _mod.backfill_companies(dry_run=False, company="missing")
        assert missing["scanned"] == 0
        assert "Company 'missing' not found." in capsys.readouterr().out



class TestBackfillJobs:
    def test_dry_run_and_live_set_job_agent_responses(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [{"astral_job_id": "job-727", "agent_responses": _duplicate_refs()}]
        monkeypatch.setattr(_mod, "list_jobs", lambda: rows)
        setter = MagicMock()
        monkeypatch.setattr(_mod, "_set_job_agent_responses", setter)

        dry = _mod.backfill_jobs(dry_run=True, job_id=None)
        assert dry["updated"] == 1
        setter.assert_not_called()

        saved: list[tuple[str, list[dict[str, Any]]]] = []

        def _set(job_id: str, entries: list[dict[str, Any]]) -> None:
            saved.append((job_id, entries))

        monkeypatch.setattr(_mod, "_set_job_agent_responses", _set)
        live = _mod.backfill_jobs(dry_run=False, job_id="job-727")
        assert live["updated"] == 1
        assert saved[0][0] == "job-727"
        assert len(saved[0][1]) == 1

    def test_not_found_and_unchanged(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        already = [{"task_key": "consult_do", "created_at": "2026-06-01 00:00:00", "batch_id": "b1"}]
        monkeypatch.setattr(
            _mod,
            "list_jobs",
            lambda: [{"astral_job_id": "job-727", "agent_responses": already}],
        )
        monkeypatch.setattr(_mod, "_set_job_agent_responses", MagicMock())

        assert _mod.backfill_jobs(dry_run=False, job_id=None)["unchanged"] == 1

        missing = _mod.backfill_jobs(dry_run=False, job_id="missing")
        assert missing["scanned"] == 0
        assert "Job 'missing' not found." in capsys.readouterr().out


class TestRunBackfill:
    def test_company_only_skips_jobs(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(
            _mod,
            "backfill_companies",
            lambda dry_run, company: {
                "scanned": 1,
                "updated": 0,
                "unchanged": 1,
                "errors": 0,
                "dropped_empty_key_total": 0,
                "deduped_refs_removed_total": 0,
            },
        )
        jobs = MagicMock()
        monkeypatch.setattr(_mod, "backfill_jobs", jobs)

        _mod.run_backfill(dry_run=False, company="acme", job_id=None)

        jobs.assert_not_called()
        out = capsys.readouterr().out
        assert "Companies:" in out
        assert "Jobs     :" not in out

    def test_job_only_skips_companies(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        companies = MagicMock()
        monkeypatch.setattr(_mod, "backfill_companies", companies)
        monkeypatch.setattr(
            _mod,
            "backfill_jobs",
            lambda dry_run, job_id: {
                "scanned": 1,
                "updated": 1,
                "unchanged": 0,
                "errors": 0,
                "dropped_empty_key_total": 0,
                "deduped_refs_removed_total": 1,
            },
        )

        _mod.run_backfill(dry_run=False, company=None, job_id="job-727")

        companies.assert_not_called()
        out = capsys.readouterr().out
        assert "Jobs     :" in out
        assert "Companies:" not in out

    def test_batch_runs_both_sections(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        empty = {
            "scanned": 0,
            "updated": 0,
            "unchanged": 0,
            "errors": 0,
            "dropped_empty_key_total": 0,
            "deduped_refs_removed_total": 0,
        }
        monkeypatch.setattr(
            _mod,
            "backfill_companies",
            lambda dry_run, company: {**empty, "scanned": 2, "unchanged": 2},
        )
        monkeypatch.setattr(
            _mod,
            "backfill_jobs",
            lambda dry_run, job_id: {**empty, "scanned": 3, "unchanged": 3},
        )

        _mod.run_backfill(dry_run=True, company=None, job_id=None)

        out = capsys.readouterr().out
        assert "=== DRY RUN — no DB writes ===" in out
        assert "=== DRY RUN SUMMARY ===" in out
        assert "Companies:" in out
        assert "Jobs     :" in out
