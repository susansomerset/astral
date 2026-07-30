"""Component tests for src/data/contact_listen.py (AST-1067)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.data import contact_listen as listen_mod
from src.utils.config import ASTRAL_CONFIG, CONTACT_CONFIG


# Branches: missing/invalid → None; round-trip bool; TypeError on non-bool save.
class TestAst1067ContactListenData:
    def test_load_missing_and_invalid(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", tmp_path)
        assert listen_mod.load_contact_listen_enabled() is None
        bad = tmp_path / CONTACT_CONFIG["listen_state_filename"]
        bad.write_text("{not-json", encoding="utf-8")
        assert listen_mod.load_contact_listen_enabled() is None
        bad.write_text(json.dumps({"listen_enabled": "yes"}), encoding="utf-8")
        assert listen_mod.load_contact_listen_enabled() is None

    def test_save_round_trip(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", tmp_path)
        listen_mod.save_contact_listen_enabled(True)
        assert listen_mod.load_contact_listen_enabled() is True
        listen_mod.save_contact_listen_enabled(False)
        assert listen_mod.load_contact_listen_enabled() is False
        raw = json.loads(
            (tmp_path / CONTACT_CONFIG["listen_state_filename"]).read_text(encoding="utf-8")
        )
        assert raw == {"listen_enabled": False}

    def test_save_rejects_non_bool(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", tmp_path)
        with pytest.raises(TypeError, match="bool"):
            listen_mod.save_contact_listen_enabled("yes")  # type: ignore[arg-type]
