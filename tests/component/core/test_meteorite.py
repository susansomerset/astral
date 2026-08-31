"""Component tests for src/core/meteorite.py (AST-1041)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import meteorite as meteorite_mod
from src.utils.config import (
    METEORITE_BOT_BLOCKED_NOTIFY_CONFIG,
    METEORITE_CONFIG,
    METEORITE_EMAIL_MAILBOX_CONFIG,
    METEORITE_INGRESS_DISPATCH_CONFIG,
    METEORITE_MONITORING_CONFIG,
)


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

    def test_optional_stem_forwards_to_ensure(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-stem-create"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})
        stem = "alice@example.com"
        out = meteorite_mod.create_meteorite_job(
            cid, "<p>" + ("x" * 50) + "</p>", stem=stem
        )
        short = METEORITE_CONFIG["stem_short_name_template"].format(
            stem=stem, candidate_id=cid
        )
        assert out["company"] == short
        assert db.get_job(out["astral_job_id"])["company"] == short
        assert db.get_company(short)["state"] == "METEORITE"


# AST-1495: enrich-first per-row Ruth company_stem → ensure → save attach.
class TestAst1495LandStemAttach:
    """AST-1495: land_meteorite stem attach after enrich (no pre-enrich ensure)."""

    @pytest.mark.asyncio
    async def test_ruth_stem_attaches_stem_keyed_company(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import JOB_SOURCE_METEORITE, METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "somerset"
        stem = "alice@example.com"
        short = METEORITE_CONFIG["stem_short_name_template"].format(
            stem=stem, candidate_id=cid
        )
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})

        async def _enrich(_cid, scraps, **_k):
            return {
                "success": True,
                "jobs": [{
                    "company_job_id": "STEMJOB1",
                    "job_title": "Eng",
                    "job_link": "",
                    "jd_text": "d" * 50,
                    "employer_name": "Acme",
                    "company_stem": stem,
                    "scrap_index": 0,
                }],
            }

        monkeypatch.setattr(
            "src.core.consult.enrich_meteorite_land_packet", _enrich
        )
        out = await meteorite_mod.land_meteorite(cid, text="z" * 50)
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_created"]
        assert out["company"] == short == "alice@example.com-somerset"
        save = out["outcomes"][0]
        row = db.get_job(save["astral_job_id"])
        assert row is not None
        assert row["company"] == short
        assert row["source"] == JOB_SOURCE_METEORITE
        assert db.get_company(short)["state"] == "METEORITE"

    @pytest.mark.asyncio
    async def test_empty_stem_uses_default_meteorite_bucket(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-default-stem"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "D"})
        short = METEORITE_CONFIG["short_name_template"].format(candidate_id=cid)

        async def _enrich(*_a, **_k):
            return {
                "success": True,
                "jobs": [{
                    "company_job_id": "DEFJOB01",
                    "job_title": "Role",
                    "job_link": "",
                    "jd_text": "e" * 50,
                    "employer_name": "",
                    "company_stem": "",
                    "scrap_index": 0,
                }],
            }

        monkeypatch.setattr(
            "src.core.consult.enrich_meteorite_land_packet", _enrich
        )
        out = await meteorite_mod.land_meteorite(cid, text="f" * 50)
        assert out["company"] == short
        assert db.get_job(out["outcomes"][0]["astral_job_id"])["company"] == short


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
        assert out["company"] is None
        assert out["company_inserted"] is False

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
        detail_args = [c.args[0] for c in log.debug_detail.call_args_list]
        assert any("stem=" in d for d in detail_args)
        assert any("company=" in d for d in detail_args)
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


# Branches: URL detector; no_candidate/param_required; text vs link mode; scrape soft-fail; Style D (AST-1517).
class TestAst1517CreateContactMeteorite:
    """AST-1517: contact-task create — scrape-or-text → create_meteorite_job."""

    def test_contact_param_looks_like_url(self) -> None:
        looks = meteorite_mod._contact_param_looks_like_url
        assert looks("") is False
        assert looks("   ") is False
        assert looks("line one\nline two") is False
        assert looks("has space.com") is False
        assert looks(".hidden") is False
        assert looks("https://jobs.example/jd") is True
        assert looks("jobs.example.com/path") is True

    @pytest.mark.asyncio
    async def test_no_candidate(self) -> None:
        out = await meteorite_mod.create_contact_meteorite("", "https://x.example/j")
        assert out == {
            "ok": False,
            "error": "no_candidate",
            "task_key": "create_contact_meteorite",
        }

    @pytest.mark.asyncio
    async def test_param_required(self) -> None:
        out = await meteorite_mod.create_contact_meteorite("c1", "  ")
        assert out == {
            "ok": False,
            "error": "param_required",
            "task_key": "create_contact_meteorite",
        }

    @pytest.mark.asyncio
    async def test_text_mode_creates_without_scrape(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-1517-text"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "T"})
        body = "Senior Engineer\n" + ("detail " * 20)

        async def _fail_scrape(*_a, **_k):
            raise AssertionError("text mode must not scrape")

        monkeypatch.setattr(
            "src.core.gazer.contact_task_gazer_scrape", _fail_scrape
        )
        out = await meteorite_mod.create_contact_meteorite(cid, body, debug=False)
        assert out["ok"] is True
        assert out["mode"] == "text"
        assert out["task_key"] == "create_contact_meteorite"
        assert out["result"]["astral_job_id"]
        from src.utils.config import TRACKER_CONFIG

        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        row = db.get_job(out["result"]["astral_job_id"])
        assert row["job_data"][jd_key] == body.rstrip()

    @pytest.mark.asyncio
    async def test_link_mode_scrape_then_create(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-1517-link"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "L"})
        url = "https://jobs.example/jd"
        visible = "Role title\n" + ("jd " * 20)

        async def _scrape(_cid, _url, debug=False):
            assert _url == url
            return {
                "ok": True,
                "visible_text": visible,
                "url": url,
                "final_url": "https://jobs.example/jd/final",
                "page_status": "ok",
                "task_key": "gazer_scrape",
            }

        monkeypatch.setattr(
            "src.core.gazer.contact_task_gazer_scrape", _scrape
        )
        out = await meteorite_mod.create_contact_meteorite(cid, url, debug=False)
        assert out["ok"] is True
        assert out["mode"] == "link"
        assert out["page_status"] == "ok"
        assert out["final_url"] == "https://jobs.example/jd/final"
        row = db.get_job(out["result"]["astral_job_id"])
        assert row["job_link"] == "https://jobs.example/jd/final"

    @pytest.mark.asyncio
    async def test_link_mode_scrape_failure_soft_return(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def _scrape(_cid, _url, debug=False):
            return {"ok": False, "error": "no_connectivity", "task_key": "gazer_scrape"}

        monkeypatch.setattr(
            "src.core.gazer.contact_task_gazer_scrape", _scrape
        )
        out = await meteorite_mod.create_contact_meteorite(
            "c1", "https://jobs.example/jd", debug=False
        )
        assert out["ok"] is False
        assert out["error"] == "no_connectivity"
        assert out["mode"] == "link"

    @pytest.mark.asyncio
    async def test_link_mode_empty_visible_text(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def _scrape(_cid, _url, debug=False):
            return {
                "ok": True,
                "visible_text": "   ",
                "page_status": "blocked",
                "task_key": "gazer_scrape",
            }

        monkeypatch.setattr(
            "src.core.gazer.contact_task_gazer_scrape", _scrape
        )
        out = await meteorite_mod.create_contact_meteorite(
            "c1", "https://jobs.example/jd", debug=False
        )
        assert out["ok"] is False
        assert out["error"] == "empty_visible_text"
        assert out["scrape"]["page_status"] == "blocked"

    @pytest.mark.asyncio
    async def test_debug_true_emits_style_d(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-1517-dbg"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "D"})
        log = MagicMock()
        monkeypatch.setattr(meteorite_mod, "get_logger", lambda _n: log)
        out = await meteorite_mod.create_contact_meteorite(
            cid, "plain pasted jd\n" + ("x" * 40), debug=True
        )
        assert out["ok"] is True
        contact_calls = [
            c
            for c in log.debug_index.call_args_list
            if c.kwargs.get("func") == "meteorite.create_contact_meteorite"
        ]
        assert len(contact_calls) == 2
        assert contact_calls[0].kwargs.get("outcome") == "found"
        assert str(contact_calls[1].kwargs.get("outcome", "")).startswith(
            "recorded astral_job_id="
        )


# Branches: stage gates; skip; classify-only return; Style D (AST-1530 / AST-1560).
@pytest.mark.skipif(
    not hasattr(meteorite_mod, "stage_meteorite"),
    reason="AST-1530 stage_meteorite not on this publish tip",
)
class TestAst1530StageMeteorite:
    """AST-1530 / AST-1560: public stage_meteorite — classify only (no scrap map / land)."""

    @pytest.mark.asyncio
    async def test_empty_candidate_and_missing_candidate(
        self, sqlite_in_memory
    ) -> None:
        err = METEORITE_CONFIG["land_outcome_error"]
        out = await meteorite_mod.stage_meteorite(
            "", "blob", source_kind="email", source_id="m1"
        )
        assert out["outcome"] == err
        assert "candidate_id" in (out.get("error") or "")
        assert out["skipped"] is False

        out2 = await meteorite_mod.stage_meteorite(
            "missing", "blob text", source_kind="email", source_id="m1"
        )
        assert out2["outcome"] == err
        assert "candidate not found" in (out2.get("error") or "")

    @pytest.mark.asyncio
    async def test_skip_outcomes_return_skipped_empty_jobs(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-stage-skip"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})

        async def _invoke(*_a, **_k):
            return {
                "success": True,
                "outcome": "not_job_content",
                "jobs": [{"jd_text": "should be ignored"}],
                "error": None,
                "batch_id": "stage_meteorite-stage-skip",
            }

        land_calls = []

        async def _land(*_a, **_k):
            land_calls.append(1)
            return {"outcome": "should-not-run"}

        monkeypatch.setattr(
            "src.core.consult.invoke_stage_meteorite", _invoke
        )
        monkeypatch.setattr(meteorite_mod, "land_meteorite", _land)
        out = await meteorite_mod.stage_meteorite(
            cid, "noise thread", source_kind="email", source_id="msg-skip"
        )
        assert out["skipped"] is True
        assert out["outcome"] == "not_job_content"
        assert out["stage_outcome"] == "not_job_content"
        assert out["jobs"] == []
        assert "land" not in out
        assert "scraps" not in out
        assert land_calls == []

    @pytest.mark.asyncio
    async def test_landable_returns_classify_jobs_only(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-stage-land"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "L"})
        jobs = [{"jd_text": "Original JD " + ("z" * 40)}]

        async def _invoke(*_a, **_k):
            return {
                "success": True,
                "outcome": "single_jd_no_link",
                "jobs": jobs,
                "error": None,
                "batch_id": "stage_meteorite-stage-land",
            }

        land = AsyncMock()
        monkeypatch.setattr("src.core.consult.invoke_stage_meteorite", _invoke)
        monkeypatch.setattr(meteorite_mod, "land_meteorite", land)
        out = await meteorite_mod.stage_meteorite(
            cid, "blob", source_kind="email", source_id="msg-land", debug=False
        )
        assert out["skipped"] is False
        assert out["stage_outcome"] == "single_jd_no_link"
        assert out["outcome"] == "single_jd_no_link"
        assert out["jobs"] == jobs
        assert "land" not in out
        land.assert_not_called()

    @pytest.mark.asyncio
    async def test_debug_true_emits_style_d_on_skip(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-stage-dbg"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "D"})

        async def _invoke(*_a, **_k):
            return {
                "success": True,
                "outcome": "not_original_posting",
                "jobs": [],
                "error": None,
                "batch_id": "b-dbg",
            }

        log = MagicMock()
        monkeypatch.setattr(meteorite_mod, "get_logger", lambda _n: log)
        monkeypatch.setattr(
            "src.core.consult.invoke_stage_meteorite", _invoke
        )
        out = await meteorite_mod.stage_meteorite(
            cid, "reply", source_kind="email", source_id="m", debug=True
        )
        assert out["skipped"] is True
        stage_calls = [
            c
            for c in log.debug_index.call_args_list
            if c.kwargs.get("func") == "meteorite.stage_meteorite"
        ]
        assert len(stage_calls) >= 1
        assert stage_calls[0].kwargs.get("outcome") == "not_original_posting"


def _ingress_task(*, batch_id: str, task_key: str | None = None) -> dict:
    cfg = METEORITE_INGRESS_DISPATCH_CONFIG
    return {
        "task_key": task_key or cfg["stage_task_key"],
        "entity_batch_id": batch_id,
        "batch_size": cfg["batch_size"],
    }


def _insert_meteorite_row(db, cid: str, **fields: object) -> int:
    row_id = db.insert_meteorite_rows(
        [
            {
                "candidate_id": cid,
                "source_kind": str(fields.get("source_kind") or "email"),
                "source_id": str(fields.get("source_id") or f"mid-{cid}"),
                "classify_outcome": fields.get("classify_outcome"),
                "content": fields.get("content"),
                "link": fields.get("link"),
            }
        ]
    )[0]
    state = fields.get("state")
    extra = {
        k: fields[k]
        for k in (
            "content",
            "link",
            "error",
            "estelle_thread_ts",
            "nag_count",
            "estelle_notified_at",
        )
        if k in fields and fields[k] is not None
    }
    if state and state != "NEW":
        db.update_meteorite(row_id, state=str(state), **extra)
    elif extra:
        db.update_meteorite(row_id, **extra)
    return row_id


def _notify_task(*, batch_id: str) -> dict:
    cfg = METEORITE_BOT_BLOCKED_NOTIFY_CONFIG
    return {
        "task_key": cfg["task_key"],
        "entity_batch_id": batch_id,
        "batch_size": cfg["batch_size"],
    }


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "run_stage_meteorite"),
    reason="AST-1560 ingress transition runners not on this publish tip",
)
class TestAst1560RunStageMeteorite:
    """AST-1560: NEW → SCRAPE_LINK | READY via dispatch claim batch."""

    @pytest.mark.asyncio
    async def test_entity_batch_id_required(self) -> None:
        with pytest.raises(ValueError, match="entity_batch_id is required"):
            await meteorite_mod.run_stage_meteorite({"task_key": "stage_meteorite"})

    @pytest.mark.asyncio
    async def test_url_outcome_to_scrape_link(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-stg-url"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "U"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            classify_outcome="single_jd_with_more",
            link="https://jobs.example.com/role",
        )
        batch_id = "stage-batch-url"
        out = await meteorite_mod.run_stage_meteorite(_ingress_task(batch_id=batch_id))
        assert out["total_passed"] == 1
        row = db.get_meteorite(row_id)
        assert row["state"] == "SCRAPE_LINK"
        assert row["link"] == "https://jobs.example.com/role"
        assert db.get_meteorite_batch(batch_id) == []

    @pytest.mark.asyncio
    async def test_text_outcome_to_ready(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-stg-text"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "T"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            classify_outcome="single_jd_no_link",
            content="Full JD body " + ("x" * 40),
        )
        batch_id = "stage-batch-text"
        out = await meteorite_mod.run_stage_meteorite(_ingress_task(batch_id=batch_id))
        assert out["total_passed"] == 1
        assert db.get_meteorite(row_id)["state"] == "READY"

    @pytest.mark.asyncio
    async def test_missing_classify_outcome_errors_with_monitoring(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-stg-miss"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "M"})
        row_id = _insert_meteorite_row(db, cid)
        log = MagicMock()
        monkeypatch.setattr(meteorite_mod, "get_logger", lambda _n: log)
        out = await meteorite_mod.run_stage_meteorite(
            _ingress_task(batch_id="stage-batch-miss")
        )
        assert out["total_errors"] == 1
        assert db.get_meteorite(row_id)["state"] == "ERROR"
        assert any(
            "missing classify_outcome" in c.args[0] for c in log.info.call_args_list
        )


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "run_scrape_meteorite"),
    reason="AST-1560 run_scrape_meteorite not on this publish tip",
)
class TestAst1560RunScrapeMeteorite:
    """AST-1560: SCRAPE_LINK → READY | BOT_BLOCKED | ERROR."""

    @pytest.mark.asyncio
    async def test_ok_visible_text_to_ready(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-scp-ok"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "O"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            state="SCRAPE_LINK",
            link="https://jobs.example.com/post",
        )

        async def _fetch(_link, debug=False):
            return ("Visible JD " + ("y" * 40), "https://jobs.example.com/final")

        monkeypatch.setattr(meteorite_mod, "_land_fetch_link_text", _fetch)
        monkeypatch.setattr("src.core.gazer._classify_jd", lambda _t: "ok")
        out = await meteorite_mod.run_scrape_meteorite(
            _ingress_task(
                batch_id="scrape-batch-ok",
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["scrape_task_key"],
            )
        )
        assert out["total_passed"] == 1
        row = db.get_meteorite(row_id)
        assert row["state"] == "READY"
        assert row["content"].startswith("Visible JD")
        assert row["link"] == "https://jobs.example.com/final"

    @pytest.mark.asyncio
    async def test_blocked_emits_monitoring(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-scp-block"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "B"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            state="SCRAPE_LINK",
            link="https://jobs.example.com/bot",
        )

        async def _fetch(_link, debug=False):
            return ("blocked page", _link)

        log = MagicMock()
        monkeypatch.setattr(meteorite_mod, "get_logger", lambda _n: log)
        monkeypatch.setattr(meteorite_mod, "_land_fetch_link_text", _fetch)
        monkeypatch.setattr("src.core.gazer._classify_jd", lambda _t: "bot")
        out = await meteorite_mod.run_scrape_meteorite(
            _ingress_task(
                batch_id="scrape-batch-block",
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["scrape_task_key"],
            )
        )
        assert out["total_passed"] == 1
        assert db.get_meteorite(row_id)["state"] == "BOT_BLOCKED"
        assert any(
            "meteorite scrape blocked" in c.args[0] for c in log.info.call_args_list
        )

    @pytest.mark.asyncio
    async def test_sibling_rows_do_not_abort_batch(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-scp-sib"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})
        bad_id = _insert_meteorite_row(
            db,
            cid,
            source_id="mid-bad",
            state="SCRAPE_LINK",
            link="not-http",
        )
        good_id = _insert_meteorite_row(
            db,
            cid,
            source_id="mid-good",
            state="SCRAPE_LINK",
            link="https://jobs.example.com/good",
        )

        async def _fetch(link, debug=False):
            return ("Visible JD " + ("z" * 40), link)

        monkeypatch.setattr(meteorite_mod, "_land_fetch_link_text", _fetch)
        monkeypatch.setattr("src.core.gazer._classify_jd", lambda _t: "ok")
        out = await meteorite_mod.run_scrape_meteorite(
            _ingress_task(
                batch_id="scrape-batch-sib",
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["scrape_task_key"],
            )
        )
        assert out["total_processed"] == 2
        assert out["total_passed"] == 1
        assert out["total_errors"] == 1
        assert db.get_meteorite(bad_id)["state"] == "ERROR"
        assert db.get_meteorite(good_id)["state"] == "READY"


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "run_land_meteorite"),
    reason="AST-1560 run_land_meteorite not on this publish tip",
)
class TestAst1560RunLandMeteorite:
    """AST-1560: READY → LANDED + METEORITE_NEW job (no enrich-in-front)."""

    @pytest.mark.asyncio
    async def test_ready_to_landed_without_enrich(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-land-1"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "L"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            state="READY",
            content="Landable JD " + ("q" * 40),
        )
        captured: dict = {}

        def _save(_cid, **kwargs):
            captured.update(kwargs)
            return {
                "outcome": METEORITE_CONFIG["land_outcome_created"],
                "astral_job_id": "job-table-1",
            }

        enrich = AsyncMock()
        monkeypatch.setattr(meteorite_mod.tracker, "save_meteorite_job", _save)
        monkeypatch.setattr(
            "src.core.consult.enrich_meteorite_land_packet", enrich
        )
        log = MagicMock()
        monkeypatch.setattr(meteorite_mod, "get_logger", lambda _n: log)
        out = await meteorite_mod.run_land_meteorite(
            _ingress_task(
                batch_id="land-batch-1",
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["land_task_key"],
            )
        )
        assert out["total_passed"] == 1
        row = db.get_meteorite(row_id)
        assert row["state"] == "LANDED"
        assert row["astral_job_id"] == "job-table-1"
        assert captured.get("job_link") is None
        assert captured.get("company_job_id") is None
        enrich.assert_not_awaited()
        assert any("meteorite land id=" in c.args[0] for c in log.info.call_args_list)

    @pytest.mark.asyncio
    async def test_missing_content_errors(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-land-miss"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "X"})
        row_id = _insert_meteorite_row(db, cid, content="placeholder")
        db.update_meteorite(row_id, state="READY", content="")
        out = await meteorite_mod.run_land_meteorite(
            _ingress_task(
                batch_id="land-batch-miss",
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["land_task_key"],
            )
        )
        assert out["total_errors"] == 1
        assert db.get_meteorite(row_id)["state"] == "ERROR"


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "apply_paste"),
    reason="AST-1561 BOT_BLOCKED paste recovery not on this publish tip",
)
class TestAst1561ApplyPaste:
    """AST-1561: BOT_BLOCKED → READY via paste (no classify)."""

    def test_moves_bot_blocked_to_ready(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-paste-ok"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "P"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            state="BOT_BLOCKED",
            link="https://blocked.example/j",
        )
        out = meteorite_mod.apply_paste(row_id, "Full JD paste " + ("x" * 40))
        assert out == {"ok": True, "meteorite_id": row_id, "state": "READY"}
        row = db.get_meteorite(row_id)
        assert row["state"] == "READY"
        assert row["content"].startswith("Full JD paste")

    def test_rejects_non_bot_blocked_state(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-paste-bad"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "B"})
        row_id = _insert_meteorite_row(db, cid, state="READY", content="already")
        out = meteorite_mod.apply_paste(row_id, "text")
        assert out["ok"] is False
        assert out["error"] == "invalid_state"
        assert out["state"] == "READY"

    def test_empty_paste_errors(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-paste-empty"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "E"})
        row_id = _insert_meteorite_row(db, cid, state="BOT_BLOCKED")
        assert meteorite_mod.apply_paste(row_id, "   ")["error"] == "empty_paste"


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "find_meteorite_for_estelle_thread"),
    reason="AST-1561 lookup helpers not on this publish tip",
)
class TestAst1561BotBlockedLookup:
    def test_find_by_estelle_thread(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-thread"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "T"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            state="BOT_BLOCKED",
            estelle_thread_ts="1234.5678",
        )
        found = meteorite_mod.find_meteorite_for_estelle_thread(
            candidate_id=cid, thread_ts="1234.5678"
        )
        assert found is not None
        assert int(found["id"]) == row_id

    def test_find_paste_source_kind(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-paste-src"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            source_kind="paste",
            source_id="blob-1",
            state="BOT_BLOCKED",
        )
        found = meteorite_mod.find_meteorite_bot_blocked_paste_source(candidate_id=cid)
        assert found is not None
        assert int(found["id"]) == row_id


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "run_notify_meteorite_bot_blocked"),
    reason="AST-1561 notify runner not on this publish tip",
)
class TestAst1561RunNotifyBotBlocked:
    """AST-1561: scheduled notify → Estelle DM + nag → ABANDONED."""

    @pytest.mark.asyncio
    async def test_first_dm_stamps_thread(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-notify-1"
        db.save_candidate(
            cid,
            state="NEW_CANDIDATE",
            candidate_data={"name": "N", "contact": {"slack_user_id": "U-notify"}},
        )
        row_id = _insert_meteorite_row(
            db,
            cid,
            state="BOT_BLOCKED",
            link="https://jobs.example/blocked",
        )
        monkeypatch.setattr(
            meteorite_mod,
            "_resolve_slack_dm_channel_for_candidate",
            lambda _c: "D-notify",
        )
        monkeypatch.setattr(
            "src.core.contact.contact_post_message",
            lambda **kw: {"ok": True, "ts": "9999.0001"},
        )
        out = await meteorite_mod.run_notify_meteorite_bot_blocked(
            _notify_task(batch_id="notify-batch-1")
        )
        assert out["total_passed"] == 1
        row = db.get_meteorite(row_id)
        assert row["estelle_notified_at"]
        assert row["estelle_thread_ts"] == "9999.0001"
        assert int(row["nag_count"]) == 1

    @pytest.mark.asyncio
    async def test_nag_limit_moves_to_abandoned(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-abandon"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "A"})
        nag_limit = METEORITE_BOT_BLOCKED_NOTIFY_CONFIG["nag_limit"]
        row_id = _insert_meteorite_row(
            db,
            cid,
            state="BOT_BLOCKED",
            nag_count=nag_limit,
        )
        post = MagicMock()
        monkeypatch.setattr("src.core.contact.contact_post_message", post)
        out = await meteorite_mod.run_notify_meteorite_bot_blocked(
            _notify_task(batch_id="notify-batch-abandon")
        )
        assert out["total_passed"] == 1
        assert db.get_meteorite(row_id)["state"] == "ABANDONED"
        post.assert_not_called()


def _check_inbox_msg(
    mid: str,
    *,
    from_address: str = "sender@ex.com",
    internal_date_ms: int = 1_700_000_000_000,
    subject: str = "Role at ACME",
) -> dict:
    return {
        "id": mid,
        "from_address": from_address,
        "internal_date_ms": internal_date_ms,
        "subject": subject,
    }


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "check_inbox"),
    reason="AST-1559 check_inbox not on this publish tip",
)
class TestAst1559CheckInbox:
    """AST-1559: aliases → fetch → classify → fan-out rows → archive + monitoring."""

    @pytest.mark.asyncio
    async def test_candidate_id_required(self) -> None:
        with pytest.raises(ValueError, match="candidate_id is required"):
            await meteorite_mod.check_inbox({}, debug=False)

    @pytest.mark.asyncio
    async def test_fan_out_n_rows_archives_and_monitors(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-inbox-fan"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Fan"})
        mid = "msg-fan"
        monkeypatch.setattr(meteorite_mod, "email_aliases_for_candidate", lambda _c: ["ada@ex.com"])
        monkeypatch.setattr(
            meteorite_mod, "fetch_candidate_email", lambda _a, debug=False: [_check_inbox_msg(mid)]
        )
        monkeypatch.setattr(
            meteorite_mod,
            "get_message_html",
            lambda _m: {"subject": "Two roles", "html_body": "<p>jd</p>", "from_address": "a"},
        )
        monkeypatch.setattr(meteorite_mod, "strip_extract_email_html", lambda *a, **k: "blob")
        archive = MagicMock()
        monkeypatch.setattr(meteorite_mod, "archive_candidate_email", archive)

        async def _invoke(*_a, **_k):
            return {
                "success": True,
                "outcome": "link_list",
                "jobs": [
                    {"job_link": "https://jobs.example/a", "jd_text": "A"},
                    {"job_link": "https://jobs.example/b", "jd_text": "B"},
                ],
                "error": None,
                "batch_id": "b",
            }

        monkeypatch.setattr("src.core.consult.invoke_stage_meteorite", _invoke)
        out = await meteorite_mod.check_inbox({"candidate_id": cid}, debug=False)
        assert out["total_passed"] == 1
        assert len(db.list_meteorites_by_source("email", mid)) == 2
        archive.assert_called_once_with(mid)
        assert db.get_candidate(cid)["last_email_check"]

    @pytest.mark.asyncio
    async def test_classify_failed_zero_rows_no_archive(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-inbox-fail"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Fail"})
        mid = "msg-fail"
        monkeypatch.setattr(meteorite_mod, "email_aliases_for_candidate", lambda _c: ["x@y.z"])
        monkeypatch.setattr(
            meteorite_mod, "fetch_candidate_email", lambda _a, debug=False: [_check_inbox_msg(mid)]
        )
        monkeypatch.setattr(
            meteorite_mod, "get_message_html", lambda _m: {"subject": "s", "html_body": "", "from_address": "a"}
        )
        monkeypatch.setattr(meteorite_mod, "strip_extract_email_html", lambda *a, **k: "blob")
        archive = MagicMock()
        monkeypatch.setattr(meteorite_mod, "archive_candidate_email", archive)

        async def _invoke(*_a, **_k):
            return {"success": False, "outcome": "", "jobs": [], "error": "llm timeout", "batch_id": None}

        monkeypatch.setattr("src.core.consult.invoke_stage_meteorite", _invoke)
        out = await meteorite_mod.check_inbox({"candidate_id": cid}, debug=False)
        assert out["total_errors"] == 1
        assert db.list_meteorites_by_source("email", mid) == []
        archive.assert_not_called()

    @pytest.mark.asyncio
    async def test_skip_outcome_zero_rows_monitor_archive(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-inbox-skip"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Skip"})
        mid = "msg-skip"
        monkeypatch.setattr(meteorite_mod, "email_aliases_for_candidate", lambda _c: ["x@y.z"])
        monkeypatch.setattr(
            meteorite_mod, "fetch_candidate_email", lambda _a, debug=False: [_check_inbox_msg(mid)]
        )
        monkeypatch.setattr(
            meteorite_mod, "get_message_html", lambda _m: {"subject": "n", "html_body": "", "from_address": "a"}
        )
        monkeypatch.setattr(meteorite_mod, "strip_extract_email_html", lambda *a, **k: "blob")
        archive = MagicMock()
        monkeypatch.setattr(meteorite_mod, "archive_candidate_email", archive)

        async def _invoke(*_a, **_k):
            return {"success": True, "outcome": "not_job_content", "jobs": [], "error": None, "batch_id": "b"}

        monkeypatch.setattr("src.core.consult.invoke_stage_meteorite", _invoke)
        out = await meteorite_mod.check_inbox({"candidate_id": cid}, debug=False)
        assert out["total_passed"] == 1
        assert db.list_meteorites_by_source("email", mid) == []
        archive.assert_called_once_with(mid)

    @pytest.mark.asyncio
    async def test_already_ingested_skips_classify_archives(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-inbox-dedup"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Dedup"})
        mid = "msg-dedup"
        db.insert_meteorite_rows(
            [{"candidate_id": cid, "source_kind": "email", "source_id": mid, "link": "https://x/j"}]
        )
        invoke = AsyncMock()
        monkeypatch.setattr("src.core.consult.invoke_stage_meteorite", invoke)
        monkeypatch.setattr(meteorite_mod, "email_aliases_for_candidate", lambda _c: ["x@y.z"])
        monkeypatch.setattr(
            meteorite_mod, "fetch_candidate_email", lambda _a, debug=False: [_check_inbox_msg(mid)]
        )
        archive = MagicMock()
        monkeypatch.setattr(meteorite_mod, "archive_candidate_email", archive)
        out = await meteorite_mod.check_inbox({"candidate_id": cid}, debug=False)
        invoke.assert_not_awaited()
        archive.assert_called_once_with(mid)

    @pytest.mark.asyncio
    async def test_empty_aliases_still_stamps_last_check(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-inbox-empty"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Empty"})
        monkeypatch.setattr(meteorite_mod, "email_aliases_for_candidate", lambda _c: [])
        monkeypatch.setattr(meteorite_mod, "fetch_candidate_email", lambda _a, debug=False: [])
        await meteorite_mod.check_inbox({"candidate_id": cid}, debug=False)
        assert db.get_candidate(cid)["last_email_check"]

    def test_sanitize_monitor_subject(self) -> None:
        out = meteorite_mod._sanitize_meteorite_monitor_subject("a\nb\t" + ("x" * 200))
        assert len(out) <= METEORITE_MONITORING_CONFIG["subject_max_len"]
