"""AST-722: backfill rubric_vector rows from legacy candidate_data.artifacts."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from src.utils.config import ASTRAL_CONFIG

REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = REPO_ROOT / "scripts/migrations/backfill_rubric_vectors.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("backfill_rubric_vectors", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load_module()
_CI = ASTRAL_CONFIG["consult_importance"]


class TestNormalizeImportance:
    def test_defaults_and_clamps(self) -> None:
        assert _mod._normalize_importance(None, _CI) == int(_CI["default_vector_importance"])
        assert _mod._normalize_importance(99, _CI) == int(_CI["max"])
        assert _mod._normalize_importance(0, _CI) == int(_CI["min"])

    def test_rejects_boolean(self) -> None:
        with pytest.raises(ValueError, match="boolean"):
            _mod._normalize_importance(True, _CI)


class TestCriterionFromArtifactItem:
    def test_builds_code_label_fingerprint(self) -> None:
        item = {"code": "RC", "label": "Reality", "content": "Grade A", "importance": 7}
        code, label, content, importance, fp = _mod._criterion_from_artifact_item(item, 0, _CI)
        assert code == "RC"
        assert label == "Reality"
        assert content == "Grade A"
        assert importance == 7
        assert len(fp) == 64

    def test_generates_code_when_missing(self) -> None:
        item = {"content": "body", "importance": 5}
        code, label, _, _, _ = _mod._criterion_from_artifact_item(item, 2, _CI)
        assert code == "V03"
        assert label == "V03"

    def test_raises_on_empty_content(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            _mod._criterion_from_artifact_item({"code": "X"}, 0, _CI)


class TestBackfillCandidateRubricVectors:
    def test_skips_deleted_candidate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            _mod.database,
            "get_candidate",
            lambda _cid: {"state": "DELETED", "candidate_data": {}},
        )
        counts = _mod.backfill_candidate_rubric_vectors("gone", dry_run=False)
        assert counts["candidates_scanned"] == 1
        assert counts["vectors_inserted"] == 0


class TestBackfillMain:
    def test_purge_without_confirm_exits(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        monkeypatch.setattr(sys, "argv", ["backfill_rubric_vectors.py", "--purge-artifacts"])
        with pytest.raises(SystemExit) as exc:
            _mod.main()
        assert exc.value.code == 1
        assert "requires --confirm-purge" in capsys.readouterr().out
