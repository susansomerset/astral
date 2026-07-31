"""Component tests for src/data/contact_estelle_activity.py (AST-1094)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.data import contact_estelle_activity as act_mod
from src.utils.config import ASTRAL_CONFIG, CONTACT_CONFIG


# Branches: missing/corrupt → empty; record upsert+increment; list sort by ts; TypeError.
class TestAst1094EstelleActivityData:
    def test_list_missing_and_corrupt(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        assert act_mod.list_estelle_activity_rows() == []
        bad = tmp_path / CONTACT_CONFIG["activity_state_filename"]
        bad.write_text("{not-json", encoding="utf-8")
        assert act_mod.list_estelle_activity_rows() == []
        bad.write_text(json.dumps({"by_slack_user_id": "nope"}), encoding="utf-8")
        assert act_mod.list_estelle_activity_rows() == []

    def test_record_increments_and_list_sorts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        r1 = act_mod.record_estelle_activity(
            slack_user_id="U1",
            bind_ok=True,
            astral_candidate_id="c1",
            candidate_state="PROSPECT",
            last_channel="C1",
            last_message_ts="100.0",
        )
        assert r1["inbound_message_count"] == 1
        r2 = act_mod.record_estelle_activity(
            slack_user_id="U1",
            bind_ok=True,
            astral_candidate_id="c1",
            candidate_state="PROSPECT",
            last_channel="C2",
            last_message_ts="200.0",
        )
        assert r2["inbound_message_count"] == 2
        assert r2["last_channel"] == "C2"
        act_mod.record_estelle_activity(
            slack_user_id="U2",
            bind_ok=False,
            astral_candidate_id=None,
            candidate_state=None,
            last_channel="C9",
            last_message_ts="150.0",
        )
        rows = act_mod.list_estelle_activity_rows()
        assert [r["slack_user_id"] for r in rows] == ["U1", "U2"]
        assert rows[0]["last_message_ts"] == "200.0"

    def test_record_rejects_bad_args(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        with pytest.raises(TypeError, match="slack_user_id"):
            act_mod.record_estelle_activity(
                slack_user_id="  ",
                bind_ok=True,
                astral_candidate_id=None,
                candidate_state=None,
                last_channel=None,
                last_message_ts=None,
            )
        with pytest.raises(TypeError, match="bind_ok"):
            act_mod.record_estelle_activity(
                slack_user_id="U1",
                bind_ok="yes",  # type: ignore[arg-type]
                astral_candidate_id=None,
                candidate_state=None,
                last_channel=None,
                last_message_ts=None,
            )


# Branches: persist username/display; preserve prior when None (AST-1105).
class TestAst1105ActivityIdentity:
    def test_record_stores_and_preserves_identity(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(ASTRAL_CONFIG, "db_dir", str(tmp_path))
        r1 = act_mod.record_estelle_activity(
            slack_user_id="U1",
            bind_ok=True,
            astral_candidate_id="c1",
            candidate_state="PROSPECT",
            last_channel="C1",
            last_message_ts="100.0",
            slack_username="ada",
            slack_display_name="Ada L",
        )
        assert r1["slack_username"] == "ada"
        assert r1["slack_display_name"] == "Ada L"
        r2 = act_mod.record_estelle_activity(
            slack_user_id="U1",
            bind_ok=True,
            astral_candidate_id="c1",
            candidate_state="PROSPECT",
            last_channel="C2",
            last_message_ts="200.0",
            slack_username=None,
            slack_display_name=None,
        )
        assert r2["inbound_message_count"] == 2
        assert r2["slack_username"] == "ada"
        assert r2["slack_display_name"] == "Ada L"
        assert r2["last_channel"] == "C2"

