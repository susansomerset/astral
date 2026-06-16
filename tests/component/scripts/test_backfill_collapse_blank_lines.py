"""AST-714: backfill collapse_consecutive_blank_lines on persisted visible text."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = REPO_ROOT / "scripts/migrations/backfill_collapse_blank_lines.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("backfill_collapse_blank_lines", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_module()
_HOMEPAGE_KEY = _mod._HOMEPAGE_KEY
_JD_KEY = _mod._JD_KEY


# Branches: non-str/empty skip; changed vs unchanged normalized text.
class TestNormalizeIfChanged:
    def test_skips_non_string_and_empty(self) -> None:
        assert _mod._normalize_if_changed(None) == (None, False)
        assert _mod._normalize_if_changed("") == (None, False)
        assert _mod._normalize_if_changed(7) == (None, False)

    def test_unchanged_when_already_normalized(self) -> None:
        assert _mod._normalize_if_changed("line1\nline2") == (None, False)

    def test_returns_normalized_when_blank_runs_collapse(self) -> None:
        text = "line1\n\n\nline2"
        normalized, changed = _mod._normalize_if_changed(text)
        assert changed is True
        assert normalized == "line1\n\nline2"


# Branches: dry-run vs save; filter; not found; unchanged; save error.
class TestBackfillCompanies:
    def test_dry_run_reports_without_save(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        monkeypatch.setattr(
            _mod,
            "list_companies",
            lambda: [{"short_name": "acme", "company_data": {_HOMEPAGE_KEY: "a\n\n\nb"}}],
        )
        save = MagicMock()
        monkeypatch.setattr(_mod, "save_company_data", save)

        counts = _mod.backfill_companies(dry_run=True, company=None)

        assert counts == {"scanned": 1, "updated": 1, "unchanged": 0, "errors": 0}
        save.assert_not_called()
        assert "DRY RUN" in capsys.readouterr().out

    def test_live_save_persists_normalized_text(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            _mod,
            "list_companies",
            lambda: [{"short_name": "acme", "company_data": {_HOMEPAGE_KEY: "a\n\n\nb"}}],
        )
        saved: list[tuple[str, dict[str, Any]]] = []

        def _save(short_name: str, data: dict[str, Any]) -> None:
            saved.append((short_name, data))

        monkeypatch.setattr(_mod, "save_company_data", _save)

        counts = _mod.backfill_companies(dry_run=False, company=None)

        assert counts["updated"] == 1
        assert saved == [("acme", {_HOMEPAGE_KEY: "a\n\nb"})]

    def test_unchanged_and_not_found(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        monkeypatch.setattr(
            _mod,
            "list_companies",
            lambda: [{"short_name": "acme", "company_data": {_HOMEPAGE_KEY: "already\n\nok"}}],
        )
        monkeypatch.setattr(_mod, "save_company_data", MagicMock())

        unchanged = _mod.backfill_companies(dry_run=False, company=None)
        assert unchanged["unchanged"] == 1
        assert unchanged["updated"] == 0

        missing = _mod.backfill_companies(dry_run=False, company="missing")
        assert missing == {"scanned": 0, "updated": 0, "unchanged": 0, "errors": 0}
        assert "Company 'missing' not found." in capsys.readouterr().out

    def test_save_error_increments_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            _mod,
            "list_companies",
            lambda: [{"short_name": "acme", "company_data": {_HOMEPAGE_KEY: "a\n\n\nb"}}],
        )
        monkeypatch.setattr(_mod, "save_company_data", MagicMock(side_effect=RuntimeError("boom")))

        counts = _mod.backfill_companies(dry_run=False, company="acme")

        assert counts == {"scanned": 1, "updated": 0, "unchanged": 0, "errors": 1}


# Branches: dry-run vs save; filter; not found; unchanged; save error.
class TestBackfillJobs:
    def test_dry_run_and_live_save(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [{"astral_job_id": "job-1", "job_data": {_JD_KEY: "x\n\n\ny"}}]
        monkeypatch.setattr(_mod, "list_jobs", lambda: rows)
        save = MagicMock()
        monkeypatch.setattr(_mod, "save_job_data", save)

        dry = _mod.backfill_jobs(dry_run=True, job_id=None)
        assert dry["updated"] == 1
        save.assert_not_called()

        saved: list[tuple[str, dict[str, Any]]] = []

        def _save(job_id: str, data: dict[str, Any]) -> None:
            saved.append((job_id, data))

        monkeypatch.setattr(_mod, "save_job_data", _save)
        live = _mod.backfill_jobs(dry_run=False, job_id="job-1")
        assert live["updated"] == 1
        assert saved == [("job-1", {_JD_KEY: "x\n\ny"})]

    def test_not_found_and_unchanged(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        monkeypatch.setattr(
            _mod,
            "list_jobs",
            lambda: [{"astral_job_id": "job-1", "job_data": {_JD_KEY: "clean"}}],
        )
        monkeypatch.setattr(_mod, "save_job_data", MagicMock())

        assert _mod.backfill_jobs(dry_run=False, job_id=None)["unchanged"] == 1

        missing = _mod.backfill_jobs(dry_run=False, job_id="missing")
        assert missing["scanned"] == 0
        assert "Job 'missing' not found." in capsys.readouterr().out


# Branches: --company only; --job only; batch both; dry-run banner/summary.
class TestRunBackfill:
    def test_company_only_skips_jobs(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        monkeypatch.setattr(_mod, "backfill_companies", lambda dry_run, company: {"scanned": 1, "updated": 0, "unchanged": 1, "errors": 0})
        jobs = MagicMock()
        monkeypatch.setattr(_mod, "backfill_jobs", jobs)

        _mod.run_backfill(dry_run=False, company="acme", job_id=None)

        jobs.assert_not_called()
        out = capsys.readouterr().out
        assert "Companies:" in out
        assert "Jobs     :" not in out

    def test_job_only_skips_companies(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        companies = MagicMock()
        monkeypatch.setattr(_mod, "backfill_companies", companies)
        monkeypatch.setattr(_mod, "backfill_jobs", lambda dry_run, job_id: {"scanned": 1, "updated": 1, "unchanged": 0, "errors": 0})

        _mod.run_backfill(dry_run=False, company=None, job_id="job-1")

        companies.assert_not_called()
        out = capsys.readouterr().out
        assert "Jobs     :" in out
        assert "Companies:" not in out

    def test_batch_runs_both_sections(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        monkeypatch.setattr(_mod, "backfill_companies", lambda dry_run, company: {"scanned": 2, "updated": 0, "unchanged": 2, "errors": 0})
        monkeypatch.setattr(_mod, "backfill_jobs", lambda dry_run, job_id: {"scanned": 3, "updated": 0, "unchanged": 3, "errors": 0})

        _mod.run_backfill(dry_run=True, company=None, job_id=None)

        out = capsys.readouterr().out
        assert "=== DRY RUN — no DB writes ===" in out
        assert "=== DRY RUN SUMMARY ===" in out
        assert "Companies:" in out
        assert "Jobs     :" in out
