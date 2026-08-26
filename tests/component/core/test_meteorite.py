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
        detail_args = [c.args[0] for c in log.debug_detail.call_args_list]
        assert f"candidate_id={cid}" in detail_args
        assert f"stem={METEORITE_CONFIG['default_stem']}" in detail_args
        assert f"company_state={METEORITE_CONFIG['company_state']}" in detail_args

        log.reset_mock()
        meteorite_mod.ensure_meteorite_company(cid, debug=True)
        log.set_debug_flag.assert_called_with(True)
        assert log.debug_index.call_args.kwargs["outcome"] == "already-present"
        detail_args = [c.args[0] for c in log.debug_detail.call_args_list]
        assert f"candidate_id={cid}" in detail_args
        assert f"stem={METEORITE_CONFIG['default_stem']}" in detail_args

    def test_debug_false_skips_style_d(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        log = MagicMock()
        monkeypatch.setattr(meteorite_mod, "get_logger", lambda _name: log)
        meteorite_mod.ensure_meteorite_company("cand-quiet", debug=False)
        log.set_debug_flag.assert_called_with(False)
        log.debug_index.assert_not_called()
        log.debug_detail.assert_not_called()


# Branches: stem shapes; leave-in-place IGNORE; track predicate state+prefix; Style D stem.
class TestAst1493StemEnsureAndTrack:
    """AST-1493: stem-keyed ensure into METEORITE + widened is_meteorite_company."""

    def test_email_stem_ensures_meteorite_state(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "somerset"
        stem = "alice@example.com"
        out = meteorite_mod.ensure_meteorite_company(cid, stem=stem)
        short = METEORITE_CONFIG["stem_short_name_template"].format(
            stem=stem, candidate_id=cid
        )
        assert out["inserted"] is True
        assert out["short_name"] == short == "alice@example.com-somerset"
        row = db.get_company(short)
        assert row is not None
        assert row["state"] == "METEORITE"
        assert row["candidate_id"] == cid
        # Idempotent
        again = meteorite_mod.ensure_meteorite_company(cid, stem=stem)
        assert again["inserted"] is False
        assert again["short_name"] == short

    def test_meteorite_self_and_slug_stems(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "somerset"
        self_stem = METEORITE_CONFIG["meteorite_self_stem"]
        out_self = meteorite_mod.ensure_meteorite_company(cid, stem=self_stem)
        assert out_self["short_name"] == f"{self_stem}-{cid}"
        assert db.get_company(out_self["short_name"])["state"] == "METEORITE"

        slug = "acme-careers"
        out_slug = meteorite_mod.ensure_meteorite_company(cid, stem=slug)
        assert out_slug["short_name"] == f"{slug}-{cid}"
        assert db.get_company(out_slug["short_name"])["state"] == "METEORITE"

    def test_default_stem_matches_legacy_template(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-default"
        out = meteorite_mod.ensure_meteorite_company(cid)  # no stem=
        short = METEORITE_CONFIG["short_name_template"].format(candidate_id=cid)
        assert out["short_name"] == short
        assert db.get_company(short)["state"] == "METEORITE"

    def test_leave_in_place_ignore_row(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-legacy"
        short = METEORITE_CONFIG["short_name_template"].format(candidate_id=cid)
        db.save_company(
            short,
            state="IGNORE",
            company_name=METEORITE_CONFIG["company_name"],
            company_data=dict(METEORITE_CONFIG["company_data"]),
            candidate_id=cid,
        )
        out = meteorite_mod.ensure_meteorite_company(cid)
        assert out["inserted"] is False
        assert out["short_name"] == short
        # AC7: no IGNORE→METEORITE rewrite
        assert db.get_company(short)["state"] == "IGNORE"

    def test_is_meteorite_company_prefix_and_state(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        # Legacy prefix (no DB needed)
        assert meteorite_mod.is_meteorite_company("meteorite-cand-x") is True
        assert meteorite_mod.is_meteorite_company("") is False
        assert meteorite_mod.is_meteorite_company(None) is False

        # Stem short_name in METEORITE state (no meteorite- prefix)
        stem_sn = "alice@example.com-somerset"
        db.save_company(
            stem_sn,
            state="METEORITE",
            company_name=METEORITE_CONFIG["company_name"],
            candidate_id="somerset",
        )
        assert meteorite_mod.is_meteorite_company(stem_sn) is True

        # Non-meteorite company
        db.save_company("acme", state="NEW", company_name="Acme", candidate_id="somerset")
        assert meteorite_mod.is_meteorite_company("acme") is False
        assert meteorite_mod.is_meteorite_company("missing-co") is False

    def test_debug_true_emits_stem_detail(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        log = MagicMock()
        monkeypatch.setattr(meteorite_mod, "get_logger", lambda _name: log)
        cid = "cand-stem-dbg"
        stem = "jobs.example.com/role"
        meteorite_mod.ensure_meteorite_company(cid, stem=stem, debug=True)
        detail_args = [c.args[0] for c in log.debug_detail.call_args_list]
        assert f"candidate_id={cid}" in detail_args
        assert f"stem={stem}" in detail_args
        assert f"company_state={METEORITE_CONFIG['company_state']}" in detail_args


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
        # AST-1493: ensure inserts METEORITE (was IGNORE).
        assert db.get_company(short)["state"] == METEORITE_CONFIG["company_state"] == "METEORITE"

        # Second create: company no-op, new job id
        out2 = meteorite_mod.create_meteorite_job(cid, "<p>second</p>")
        assert out2["company_inserted"] is False
        assert out2["astral_job_id"] != out["astral_job_id"]
        assert out2["job"]["job_data"][jd_key] == "<p>second</p>"


    def test_optional_job_link_persists_company_job_id_none(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-1061-link"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "L"})
        link = "https://jobs.example.com/role/42"
        out = meteorite_mod.create_meteorite_job(
            cid, "<p>" + ("x" * 50) + "</p>", job_link=link
        )
        row = db.get_job(out["astral_job_id"])
        assert row is not None
        assert row["job_link"] == link
        assert row["company_job_id"] is None


# Branches: validation errors; enrich fail; create+employer; skip/supersede rollup;
# Playwright thin-body fetch; Style D; no Gmail imports (AST-1470).
class TestAst1470LandMeteorite:
    """AST-1470: public land_meteorite scrap → enrich → Tracker save."""

    def test_module_has_no_gmail_or_mailbox_imports(self) -> None:
        from pathlib import Path

        text = Path(meteorite_mod.__file__).read_text(encoding="utf-8")
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("from ") or s.startswith("import "):
                low = s.lower()
                assert "gmail" not in low
                assert "mailbox" not in low

    @pytest.mark.asyncio
    async def test_empty_candidate_and_empty_scraps_error(self, sqlite_in_memory) -> None:
        from src.utils.config import METEORITE_CONFIG

        err = METEORITE_CONFIG["land_outcome_error"]
        out = await meteorite_mod.land_meteorite("")
        assert out["outcome"] == err
        assert "candidate_id" in (out.get("error") or "")
        assert out["outcomes"] == []

        out2 = await meteorite_mod.land_meteorite("cand-x", text="  ", job_link="")
        assert out2["outcome"] == err
        assert "scraps required" in (out2.get("error") or "")

    @pytest.mark.asyncio
    async def test_missing_candidate_error(self, sqlite_in_memory) -> None:
        from src.utils.config import METEORITE_CONFIG

        out = await meteorite_mod.land_meteorite("missing-cand", text="enough text here for scrap")
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_error"]
        assert "candidate not found" in (out.get("error") or "")

    @pytest.mark.asyncio
    async def test_enrich_failure_returns_error(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-enrich-fail"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "E"})

        async def _enrich(*_a, **_k):
            return {"success": False, "error": "do_task failed", "jobs": []}

        monkeypatch.setattr(
            "src.core.consult.enrich_meteorite_land_packet", _enrich
        )
        out = await meteorite_mod.land_meteorite(cid, text="x" * 50)
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_error"]
        assert out["error"] == "do_task failed"
        assert out["company"] == METEORITE_CONFIG["short_name_template"].format(
            candidate_id=cid
        )

    @pytest.mark.asyncio
    async def test_create_with_employer_on_meteorite_company(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import JOB_SOURCE_METEORITE, METEORITE_CONFIG, TRACKER_CONFIG

        db = sqlite_in_memory
        cid = "cand-land-create"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "L"})
        short = METEORITE_CONFIG["short_name_template"].format(candidate_id=cid)
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        emp_key = METEORITE_CONFIG["employer_name_job_data_key"]

        async def _enrich(_cid, scraps, **_k):
            assert scraps
            return {
                "success": True,
                "jobs": [{
                    "company_job_id": "LANDCREATE",
                    "job_title": "Eng",
                    "job_link": "https://jobs.example.com/land",
                    "jd_text": "JD body " + ("x" * 40),
                    "employer_name": "Acme Known",
                    "scrap_index": 0,
                }],
            }

        monkeypatch.setattr(
            "src.core.consult.enrich_meteorite_land_packet", _enrich
        )
        out = await meteorite_mod.land_meteorite(
            cid,
            text="seed text " + ("y" * 40),
            employer_name="Acme Known",
            debug=False,
        )
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_created"]
        assert out["company"] == short
        assert len(out["outcomes"]) == 1
        save = out["outcomes"][0]
        assert save["outcome"] == METEORITE_CONFIG["land_outcome_created"]
        assert save["source"] == JOB_SOURCE_METEORITE
        row = db.get_job(save["astral_job_id"])
        assert row is not None
        assert row["company"] == short
        assert row["source"] == JOB_SOURCE_METEORITE
        assert row["job_data"][emp_key] == "Acme Known"
        assert jd_key in row["job_data"]

    @pytest.mark.asyncio
    async def test_duplicate_skip_rollup(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import JOB_SOURCE_METEORITE, METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-land-skip"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})
        short = METEORITE_CONFIG["short_name_template"].format(candidate_id=cid)
        db.save_company(short, state="IGNORE", candidate_id=cid)
        db.save_job(
            "existing-met",
            company=short,
            state=METEORITE_CONFIG["job_create_state"],
            source=JOB_SOURCE_METEORITE,
            company_job_id="SKIPLAND1",
            job_title="Old",
        )

        async def _enrich(*_a, **_k):
            return {
                "success": True,
                "jobs": [{
                    "company_job_id": "SKIPLAND1",
                    "job_title": "New",
                    "job_link": "",
                    "jd_text": "x" * 50,
                    "employer_name": "",
                    "scrap_index": 0,
                }],
            }

        monkeypatch.setattr(
            "src.core.consult.enrich_meteorite_land_packet", _enrich
        )
        out = await meteorite_mod.land_meteorite(cid, text="z" * 50)
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_duplicate_skip"]
        assert out["outcomes"][0]["astral_job_id"] == "existing-met"
        assert db.get_job("existing-met")["job_title"] == "Old"

    @pytest.mark.asyncio
    async def test_playwright_fetch_when_link_and_thin_body(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-land-pw"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "P"})
        fetched: list[str] = []

        async def _pw(url: str, return_final_url: bool = False):
            fetched.append(url)
            if return_final_url:
                return ("VISIBLE " + ("v" * 50), "https://final.example/job")
            return "VISIBLE " + ("v" * 50)

        monkeypatch.setattr(meteorite_mod, "get_visible_text", _pw)

        async def _enrich(_cid, scraps, **_k):
            assert scraps[0].get("content", "").startswith("VISIBLE")
            assert scraps[0]["job_link"] == "https://final.example/job"
            return {
                "success": True,
                "jobs": [{
                    "company_job_id": "PWJOB001",
                    "job_title": "Role",
                    "job_link": scraps[0]["job_link"],
                    "jd_text": scraps[0]["content"],
                    "employer_name": "",
                    "scrap_index": 0,
                }],
            }

        monkeypatch.setattr(
            "src.core.consult.enrich_meteorite_land_packet", _enrich
        )
        out = await meteorite_mod.land_meteorite(
            cid, job_link="https://jobs.example.com/thin", text="short"
        )
        assert fetched == ["https://jobs.example.com/thin"]
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_created"]

    @pytest.mark.asyncio
    async def test_debug_true_emits_style_d_false_silent(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-land-dbg"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "D"})

        async def _enrich(*_a, **_k):
            return {
                "success": True,
                "jobs": [{
                    "company_job_id": "DBGJOB01",
                    "job_title": "T",
                    "job_link": "https://x.example/j",
                    "jd_text": "d" * 50,
                    "employer_name": "",
                    "scrap_index": 0,
                }],
            }

        monkeypatch.setattr(
            "src.core.consult.enrich_meteorite_land_packet", _enrich
        )
        log = MagicMock()
        monkeypatch.setattr(meteorite_mod, "get_logger", lambda _n: log)
        await meteorite_mod.land_meteorite(cid, text="d" * 50, debug=True)
        assert any(
            c.kwargs.get("func") == "meteorite.land_meteorite"
            for c in log.debug_index.call_args_list
        )
        log.reset_mock()
        await meteorite_mod.land_meteorite(
            cid, text="e" * 50, job_link="https://other.example/j", debug=False
        )
        # ensure_meteorite may still set debug flag; land row Style D must not fire.
        land_indexes = [
            c for c in log.debug_index.call_args_list
            if c.kwargs.get("func") == "meteorite.land_meteorite"
        ]
        assert land_indexes == []
