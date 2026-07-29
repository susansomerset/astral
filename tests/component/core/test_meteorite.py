"""Component tests for src/core/meteorite.py (AST-1041)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.core import meteorite as meteorite_mod
from src.utils.config import METEORITE_CONFIG


# Branches: empty id; insert once; idempotent no-op; Style D debug on/off.
class TestAst1041EnsureMeteoriteCompany:
    def test_empty_candidate_id_raises(self, sqlite_in_memory) -> None:
        with pytest.raises(ValueError, match="candidate_id is required"):
            meteorite_mod.ensure_meteorite_company("")
        with pytest.raises(ValueError, match="candidate_id is required"):
            meteorite_mod.ensure_meteorite_company("   ")

    def test_inserts_once_then_noop(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-m1"
        first = meteorite_mod.ensure_meteorite_company(cid)
        short = METEORITE_CONFIG["short_name_template"].format(candidate_id=cid)
        assert first["inserted"] is True
        assert first["short_name"] == short
        row = db.get_company(short)
        assert row is not None
        assert row["state"] == METEORITE_CONFIG["company_state"]
        assert row["company_name"] == METEORITE_CONFIG["company_name"]
        assert row["candidate_id"] == cid
        assert row["company_data"]["note"] == METEORITE_CONFIG["company_data"]["note"]

        second = meteorite_mod.ensure_meteorite_company(cid)
        assert second["inserted"] is False
        assert second["short_name"] == short
        assert second["company"]["short_name"] == short
        assert len(db.list_companies(states=[METEORITE_CONFIG["company_state"]], candidate_id=cid)) == 1

    def test_debug_true_emits_style_d_insert_and_present(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        log = MagicMock()
        monkeypatch.setattr(meteorite_mod, "get_logger", lambda _name: log)
        cid = "cand-dbg"
        short = METEORITE_CONFIG["short_name_template"].format(candidate_id=cid)

        meteorite_mod.ensure_meteorite_company(cid, debug=True)
        log.set_debug_flag.assert_called_with(True)
        assert log.debug_index.call_args.kwargs["outcome"] == "inserted"
        assert log.debug_index.call_args.kwargs["identifier"] == short
        assert log.debug_index.call_args.kwargs["func"] == "meteorite.ensure_meteorite_company"
        log.debug_detail.assert_called()
        assert f"candidate_id={cid}" in log.debug_detail.call_args.args[0]

        log.reset_mock()
        meteorite_mod.ensure_meteorite_company(cid, debug=True)
        log.set_debug_flag.assert_called_with(True)
        assert log.debug_index.call_args.kwargs["outcome"] == "already-present"
        log.debug_detail.assert_called()

    def test_debug_false_skips_style_d(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        log = MagicMock()
        monkeypatch.setattr(meteorite_mod, "get_logger", lambda _name: log)
        meteorite_mod.ensure_meteorite_company("cand-quiet", debug=False)
        log.set_debug_flag.assert_called_with(False)
        log.debug_index.assert_not_called()
        log.debug_detail.assert_not_called()


# Branches: validation; missing candidate; insert job_create_state+score+HTML; second call ensures no-op company + new job.
class TestAst1042CreateMeteoriteJob:
    def test_validation_errors(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        db.save_candidate("cand-ok", state="NEW_CANDIDATE", candidate_data={"name": "Ok"})
        with pytest.raises(ValueError, match="candidate_id is required"):
            meteorite_mod.create_meteorite_job("", "<p>x</p>")
        with pytest.raises(ValueError, match="html_body is required"):
            meteorite_mod.create_meteorite_job("cand-ok", "   ")
        with pytest.raises(ValueError, match="html_body is required"):
            meteorite_mod.create_meteorite_job("cand-ok", None)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="candidate not found"):
            meteorite_mod.create_meteorite_job("missing-cand", "<p>x</p>")

    def test_creates_job_in_config_create_state_with_score_and_html(self, sqlite_in_memory) -> None:
        from src.utils.config import METEORITE_CONFIG, TRACKER_CONFIG

        db = sqlite_in_memory
        cid = "cand-1042"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "M"})
        html = "<html><body><h1>Role</h1></body></html>"
        out = meteorite_mod.create_meteorite_job(cid, html)
        short = METEORITE_CONFIG["short_name_template"].format(candidate_id=cid)
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        # AST-1056: job_create_state is METEORITE_NEW (config-owned; no hardcode in core).
        landing = METEORITE_CONFIG["job_create_state"]
        assert landing == "METEORITE_NEW"
        assert out["company"] == short
        assert out["state"] == landing
        assert out["latest_score"] == float(METEORITE_CONFIG["job_create_latest_score"]) == 10.0
        assert out["company_inserted"] is True
        row = db.get_job(out["astral_job_id"])
        assert row is not None
        assert row["company"] == short
        assert row["state"] == landing
        assert row["latest_score"] == 10.0
        assert row["job_data"][jd_key] == html
        assert db.get_company(short)["state"] == "IGNORE"

        # Second create: company no-op, new job id
        out2 = meteorite_mod.create_meteorite_job(cid, "<p>second</p>")
        assert out2["company_inserted"] is False
        assert out2["astral_job_id"] != out["astral_job_id"]
        assert out2["job"]["job_data"][jd_key] == "<p>second</p>"
