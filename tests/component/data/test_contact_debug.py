"""Component tests for src/data/contact_debug.py (AST-1206)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.data import contact_debug as debug_mod
from src.utils.config import ASTRAL_CONFIG, CONTACT_CONFIG


# Branches: missing/corrupt → None; round-trip bool; TypeError; listen file untouched.
class TestAst1206ContactDebugData:
    def test_load_missing_and_corrupt(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        assert debug_mod.load_contact_debug_enabled() is None
        bad = tmp_path / CONTACT_CONFIG["debug_state_filename"]
        bad.write_text("{not-json", encoding="utf-8")
        assert debug_mod.load_contact_debug_enabled() is None
        bad.write_text(json.dumps({"debug_enabled": "yes"}), encoding="utf-8")
        assert debug_mod.load_contact_debug_enabled() is None
        bad.write_text(json.dumps(["not-a-dict"]), encoding="utf-8")
        assert debug_mod.load_contact_debug_enabled() is None

    def test_save_load_round_trip(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        debug_mod.save_contact_debug_enabled(True)
        path = tmp_path / CONTACT_CONFIG["debug_state_filename"]
        assert path.is_file()
        raw = json.loads(path.read_text(encoding="utf-8"))
        assert raw == {"debug_enabled": True}
        assert debug_mod.load_contact_debug_enabled() is True
        debug_mod.save_contact_debug_enabled(False)
        assert debug_mod.load_contact_debug_enabled() is False

    def test_save_rejects_non_bool(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        with pytest.raises(TypeError, match="enabled must be bool"):
            debug_mod.save_contact_debug_enabled("yes")  # type: ignore[arg-type]

    def test_save_does_not_touch_listen_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        listen = tmp_path / CONTACT_CONFIG["listen_state_filename"]
        listen.write_text(
            json.dumps({"listen_enabled": True}, indent=2) + "\n",
            encoding="utf-8",
        )
        before = listen.read_text(encoding="utf-8")
        debug_mod.save_contact_debug_enabled(True)
        assert listen.read_text(encoding="utf-8") == before
        assert (tmp_path / CONTACT_CONFIG["debug_state_filename"]).is_file()
