"""Component tests for src/core/meteorite.py (AST-1041)."""

from __future__ import annotations

from datetime import datetime, timezone
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

    # AST-1702: ensure no longer Style-D (ungated logger.debug via _with_log_debug).

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
        from src.utils.config import (
            METEORITE_CONFIG,
            SOURCE_ENTITY_TYPE_METEORITE,
            TRACKER_CONFIG,
        )

        db = sqlite_in_memory
        cid = "cand-1042"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "M"})
        html = "<html><body><h1>Role</h1></body></html>"
        out = meteorite_mod.create_meteorite_job(cid, html)
        jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]
        landing = METEORITE_CONFIG["job_create_state"]
        assert landing == "METEORITE_NEW"
        assert out["company_id"] is None
        assert out["meteorite_id"] is not None
        assert out["state"] == landing
        assert out["latest_score"] == float(METEORITE_CONFIG["job_create_latest_score"]) == 10.0
        assert out["company_inserted"] is False
        row = db.get_job(out["astral_job_id"])
        assert row is not None
        assert row["source"] == SOURCE_ENTITY_TYPE_METEORITE
        assert row["source_entity_id"] == str(out["meteorite_id"])
        assert row["company_id"] in (None, "")
        assert row["state"] == landing
        assert row["latest_score"] == 10.0
        assert row["job_data"][jd_key] == html
        mrow = db.get_meteorite(out["meteorite_id"])
        assert mrow is not None and mrow["state"] == "LANDED"

        out2 = meteorite_mod.create_meteorite_job(cid, "<p>second</p>")
        assert out2["company_inserted"] is False
        assert out2["astral_job_id"] != out["astral_job_id"]
        assert out2["meteorite_id"] != out["meteorite_id"]
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

    def test_optional_company_id_real_employer_only(self, sqlite_in_memory) -> None:
        # AST-1702: stem= removed; optional company_id is real employer, never placeholder.
        from src.utils.config import SOURCE_ENTITY_TYPE_METEORITE

        db = sqlite_in_memory
        cid = "cand-stem-create"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})
        db.save_company("acme-real", state="IMPORTED", candidate_id=cid)
        out = meteorite_mod.create_meteorite_job(
            cid, "<p>" + ("x" * 50) + "</p>", company_id="acme-real"
        )
        row = db.get_job(out["astral_job_id"])
        assert row is not None
        assert row["company_id"] == "acme-real"
        assert row["source"] == SOURCE_ENTITY_TYPE_METEORITE
        assert out["company_id"] == "acme-real"


# AST-1495 / AST-1702: enrich-first; optional real company_id from stem (never placeholder parent).
class TestAst1495LandStemAttach:
    """AST-1495 revised AST-1702: stem maps to real employer only; parent is meteorite row."""

    @pytest.mark.asyncio
    async def test_ruth_stem_attaches_real_employer_when_company_exists(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import SOURCE_ENTITY_TYPE_METEORITE, METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "somerset"
        stem = "acme-stem"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})
        db.save_company(stem, state="IMPORTED", candidate_id=cid)

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
            "src.core.meteorite.enrich_meteorite_land_packet", _enrich
        )
        out = await meteorite_mod.land_meteorite(cid, text="z" * 50)
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_created"]
        assert out["company"] == stem
        save = out["outcomes"][0]
        row = db.get_job(save["astral_job_id"])
        assert row is not None
        assert row["company_id"] == stem
        assert row["source"] == SOURCE_ENTITY_TYPE_METEORITE
        assert row["source_entity_id"]
        assert db.get_meteorite(int(row["source_entity_id"])) is not None

    @pytest.mark.asyncio
    async def test_empty_stem_parents_meteorite_without_employer(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import SOURCE_ENTITY_TYPE_METEORITE, METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-default-stem"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "D"})

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
            "src.core.meteorite.enrich_meteorite_land_packet", _enrich
        )
        out = await meteorite_mod.land_meteorite(cid, text="f" * 50)
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_created"]
        assert out["company"] is None
        row = db.get_job(out["outcomes"][0]["astral_job_id"])
        assert row is not None
        assert row["source"] == SOURCE_ENTITY_TYPE_METEORITE
        assert row["company_id"] in (None, "")
        assert row["source_entity_id"]


# Branches: validation errors; enrich fail; create+employer; skip/supersede rollup;
# Playwright thin-body fetch; tracker Style D; no Gmail imports (AST-1470 / AST-1702).
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
            "src.core.meteorite.enrich_meteorite_land_packet", _enrich
        )
        out = await meteorite_mod.land_meteorite(cid, text="x" * 50)
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_error"]
        assert out["error"] == "do_task failed"
        assert out["company"] is None
        assert out["company_inserted"] is False

    @pytest.mark.asyncio
    async def test_create_under_meteorite_parent_with_employer_name(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import SOURCE_ENTITY_TYPE_METEORITE, METEORITE_CONFIG, TRACKER_CONFIG

        db = sqlite_in_memory
        cid = "cand-land-create"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "L"})
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
            "src.core.meteorite.enrich_meteorite_land_packet", _enrich
        )
        out = await meteorite_mod.land_meteorite(
            cid,
            text="seed text " + ("y" * 40),
            employer_name="Acme Known",
            debug=False,
        )
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_created"]
        assert out["company"] is None  # no real employer company_id
        assert len(out["outcomes"]) == 1
        save = out["outcomes"][0]
        assert save["outcome"] == METEORITE_CONFIG["land_outcome_created"]
        assert save["source"] == SOURCE_ENTITY_TYPE_METEORITE
        row = db.get_job(save["astral_job_id"])
        assert row is not None
        assert row["source"] == SOURCE_ENTITY_TYPE_METEORITE
        assert row["source_entity_id"]
        assert row["company_id"] in (None, "")
        assert row["job_data"][emp_key] == "Acme Known"
        assert jd_key in row["job_data"]

    @pytest.mark.asyncio
    async def test_duplicate_skip_rollup(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import SOURCE_ENTITY_TYPE_METEORITE, METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-land-skip"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})
        mids = db.insert_meteorite_rows(
            [{"candidate_id": cid, "source_kind": "paste", "source_id": "skip-seed", "content": "old", "state": "NEW"}]
        )
        mid = str(mids[0])
        db.save_job(
            "existing-met",
            state=METEORITE_CONFIG["job_create_state"],
            source=SOURCE_ENTITY_TYPE_METEORITE,
            source_entity_id=mid,
            candidate_id=cid,
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
            "src.core.meteorite.enrich_meteorite_land_packet", _enrich
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
        # AST-1702: append only when gazer classifies page_status ok.
        monkeypatch.setattr("src.core.gazer._classify_jd", lambda _t: "ok")

        async def _enrich(_cid, scraps, **_k):
            assert "VISIBLE" in (scraps[0].get("content") or "")
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
            "src.core.meteorite.enrich_meteorite_land_packet", _enrich
        )
        out = await meteorite_mod.land_meteorite(
            cid, job_link="https://jobs.example.com/thin", text="short"
        )
        assert fetched == ["https://jobs.example.com/thin"]
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_created"]

    @pytest.mark.asyncio
    async def test_debug_true_emits_tracker_style_d_false_silent(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # AST-1702: Style D lives on tracker.save_meteorite_job (meteorite_id=), not land.
        from src.core import tracker as tracker_mod
        from src.utils.config import METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-land-dbg"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "D"})
        log = MagicMock()
        monkeypatch.setattr(tracker_mod, "get_logger", lambda _name: log)

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
            "src.core.meteorite.enrich_meteorite_land_packet", _enrich
        )
        log = MagicMock()
        monkeypatch.setattr(meteorite_mod, "get_logger", lambda _n: log)
        await meteorite_mod.land_meteorite(cid, text="d" * 50, debug=True)
        assert any(
            c.kwargs.get("func") == "tracker.save_meteorite_job"
            for c in log.debug_index.call_args_list
        )
        detail_args = [c.args[0] for c in log.debug_detail.call_args_list]
        assert any("meteorite_id=" in d for d in detail_args)
        log.reset_mock()
        await meteorite_mod.land_meteorite(
            cid, text="e" * 50, job_link="https://other.example/j", debug=False
        )
        assert log.debug_index.call_args_list == []



# Branches: tracker parent writes; link inherit; bot-block continue; JD append; no ensure-as-parent (AST-1702).
class TestAst1702SourceEntityLand:
    """AST-1702: meteorite-row parent, link inherit, bot-block soft-continue, JD append."""

    def test_save_meteorite_job_create_and_gazed_supersede(self, sqlite_in_memory) -> None:
        from src.core import tracker as tracker_mod
        from src.utils.config import (
            METEORITE_CONFIG,
            SOURCE_ENTITY_TYPE_COMPANY,
            SOURCE_ENTITY_TYPE_METEORITE,
        )

        db = sqlite_in_memory
        cid = "cand-1702-sup"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})
        db.save_company("acme", state="IMPORTED", candidate_id=cid)
        # Legacy company/gazed parent row
        assert db.save_job(
            "job-gazed",
            company="acme",
            state="NEW",
            source=SOURCE_ENTITY_TYPE_COMPANY,
            company_job_id="EXT-1702",
            job_title="Eng",
        ) is True
        mids = db.insert_meteorite_rows(
            [{"candidate_id": cid, "source_kind": "email", "source_id": "m1702", "content": "jd", "state": "NEW"}]
        )
        mid = mids[0]
        out = tracker_mod.save_meteorite_job(
            cid,
            meteorite_id=mid,
            company_job_id="EXT-1702",
            job_title="Eng",
        )
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_superseded"]
        assert out["astral_job_id"] == "job-gazed"
        row = db.get_job("job-gazed")
        assert row["source"] == SOURCE_ENTITY_TYPE_METEORITE
        assert row["source_entity_id"] == str(mid)
        assert row["company_id"] == "acme"
        assert row["state"] == METEORITE_CONFIG["job_create_state"]
        hist = row.get("state_history") or []
        assert any(h.get("to_state") == METEORITE_CONFIG["job_create_state"] for h in hist)

    def test_save_meteorite_job_never_clobbers_meteorite_parent(
        self, sqlite_in_memory
    ) -> None:
        from src.core import tracker as tracker_mod
        from src.utils.config import METEORITE_CONFIG, SOURCE_ENTITY_TYPE_METEORITE

        db = sqlite_in_memory
        cid = "cand-1702-skip"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "K"})
        mids = db.insert_meteorite_rows(
            [{"candidate_id": cid, "source_kind": "paste", "source_id": "skip2", "content": "x", "state": "NEW"}]
        )
        mid = str(mids[0])
        db.save_job(
            "job-met-keep",
            state=METEORITE_CONFIG["job_create_state"],
            source=SOURCE_ENTITY_TYPE_METEORITE,
            source_entity_id=mid,
            candidate_id=cid,
            company_job_id="KEEPJOB01",
            job_title="OldTitle",
        )
        out = tracker_mod.save_meteorite_job(
            cid, meteorite_id=mids[0], company_job_id="KEEPJOB01", job_title="NewTitle"
        )
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_duplicate_skip"]
        assert db.get_job("job-met-keep")["job_title"] == "OldTitle"

    @pytest.mark.asyncio
    async def test_land_inherits_meteorite_link(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-1702-link"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "L"})
        mids = db.insert_meteorite_rows(
            [{
                "candidate_id": cid,
                "source_kind": "paste",
                "source_id": "link1",
                "content": "seed",
                "link": "https://jobs.example/inherited",
                "state": "NEW",
            }]
        )
        mid = mids[0]
        db.update_meteorite(mid, state="READY")

        async def _enrich(*_a, **_k):
            return {
                "success": True,
                "jobs": [{
                    "company_job_id": "LNK1",
                    "job_title": "Role",
                    "job_link": "https://other.example/ignored",
                    "jd_text": "j" * 50,
                    "employer_name": "",
                    "scrap_index": 0,
                }],
            }

        monkeypatch.setattr("src.core.meteorite.enrich_meteorite_land_packet", _enrich)
        out = await meteorite_mod.land_meteorite(
            cid, text="j" * 50, meteorite_id=mid
        )
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_created"]
        row = db.get_job(out["outcomes"][0]["astral_job_id"])
        assert row["job_link"] == "https://jobs.example/inherited"

    @pytest.mark.asyncio
    async def test_land_bot_block_continues_without_append(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-1702-bot"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "B"})
        fetched: list[str] = []

        async def _pw(url: str, return_final_url: bool = False):
            fetched.append(url)
            body = "CHALLENGE WALL " + ("x" * 40)
            return (body, url) if return_final_url else body

        monkeypatch.setattr(meteorite_mod, "get_visible_text", _pw)
        monkeypatch.setattr("src.core.gazer._classify_jd", lambda _t: "bot")

        async def _enrich(_cid, scraps, **_k):
            # Bot-block must not append scraped challenge text onto thin seed.
            assert scraps[0].get("content", "") in ("", "short") or scraps[0].get("text") == "short"
            assert not (scraps[0].get("content") or "").startswith("CHALLENGE")
            return {
                "success": True,
                "jobs": [{
                    "company_job_id": "BOT1",
                    "job_title": "Role",
                    "job_link": scraps[0].get("job_link") or "",
                    "jd_text": "seed-jd " + ("y" * 40),
                    "employer_name": "",
                    "scrap_index": 0,
                }],
            }

        monkeypatch.setattr("src.core.meteorite.enrich_meteorite_land_packet", _enrich)
        out = await meteorite_mod.land_meteorite(
            cid, job_link="https://jobs.example.com/bot", text="short"
        )
        assert fetched == ["https://jobs.example.com/bot"]
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_created"]
        assert out["outcome"] != METEORITE_CONFIG["land_outcome_error"]

    @pytest.mark.asyncio
    async def test_land_does_not_call_ensure_as_parent(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-1702-noensure"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "N"})
        ensure = MagicMock(side_effect=AssertionError("ensure must not parent jobs"))
        monkeypatch.setattr(meteorite_mod, "ensure_meteorite_company", ensure)

        async def _enrich(*_a, **_k):
            return {
                "success": True,
                "jobs": [{
                    "company_job_id": "NE1",
                    "job_title": "T",
                    "job_link": "",
                    "jd_text": "n" * 50,
                    "employer_name": "",
                    "scrap_index": 0,
                }],
            }

        monkeypatch.setattr("src.core.meteorite.enrich_meteorite_land_packet", _enrich)
        out = await meteorite_mod.land_meteorite(cid, text="n" * 50)
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_created"]
        ensure.assert_not_called()

    def test_ensure_meteorite_company_has_no_job_parent_call_sites(self) -> None:
        import inspect
        import src.core.meteorite as m
        src = inspect.getsource(m)
        # Definition + internal debug strings only — no other call sites.
        calls = [
            line for line in src.splitlines()
            if "ensure_meteorite_company(" in line and not line.strip().startswith("def ")
            and "Calling ensure_meteorite_company" not in line
            and "Response from ensure_meteorite_company" not in line
            and "without ensure_meteorite_company" not in line
        ]
        assert calls == [], calls



# Branches: create_contact_meteorite retired; Contact markup never reaches create_meteorite_job (AST-2061).
class TestAst2061NoContactJobWrite:
    def test_create_contact_meteorite_removed(self) -> None:
        assert not hasattr(meteorite_mod, "create_contact_meteorite")
        assert not hasattr(meteorite_mod, "_contact_param_looks_like_url")

    def test_contact_markup_never_reaches_create_meteorite_job(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # [bug-repro] AST-2061: the retired task key is ignored, so no job row is written.
        create = MagicMock()
        monkeypatch.setattr(meteorite_mod, "create_meteorite_job", create)
        from src.core import contact as contact_mod

        results = contact_mod.run_contact_task_dispatch(
            astral_candidate_id="c1",
            markup_spans=[("create_contact_meteorite", "Senior Engineer at Acme")],
        )
        create.assert_not_called()
        assert results == []


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
            "src.core.meteorite._classify_stage_blob", _invoke
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
        jobs = [{
            "jd_text": "Original JD " + ("z" * 40),
            "from_email": "recruiter@co.com",
            "to_email": "me@ex.com",
            "sent_at": "2026-09-17T18:05:00+00:00",
        }]

        async def _invoke(*_a, **_k):
            return {
                "success": True,
                "outcome": "single_jd_no_link",
                "jobs": jobs,
                "error": None,
                "batch_id": "stage_meteorite-stage-land",
            }

        land = AsyncMock()
        monkeypatch.setattr("src.core.meteorite._classify_stage_blob", _invoke)
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
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

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
            "src.core.meteorite._classify_stage_blob", _invoke
        )
        with caplog.at_level(logging.DEBUG, logger="src.core.meteorite"):
            out = await meteorite_mod.stage_meteorite(
                cid, "reply", source_kind="email", source_id="m", debug=True
            )
        assert out["skipped"] is True
        assert any("not_original_posting" in r.getMessage() for r in caplog.records)


def _ingress_task(*, batch_id: str, candidate_id: str, task_key: str | None = None) -> dict:
    cfg = METEORITE_INGRESS_DISPATCH_CONFIG
    return {
        "task_key": task_key or cfg["stage_task_key"],
        "entity_batch_id": batch_id,
        "candidate_id": candidate_id,
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
                "state": str(fields.get("state") or "NEW"),
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
            "astral_job_id",  # AST-1690 retention skip fixtures
            "job_title",  # AST-1757 staged title fixtures
            "employer_name",  # AST-1774 check_unique peer fixtures
            *(
                [METEORITE_CONFIG["electronic_contact_column"]]
                if "electronic_contact_column" in METEORITE_CONFIG
                else []
            ),  # AST-1689
        )
        if k in fields and fields[k] is not None
    }
    if state and state != "NEW":
        db.update_meteorite(row_id, state=str(state), **extra)
    elif extra:
        db.update_meteorite(row_id, **extra)
    return row_id


def _notify_task(*, batch_id: str, candidate_id: str) -> dict:
    cfg = METEORITE_BOT_BLOCKED_NOTIFY_CONFIG
    return {
        "task_key": cfg["task_key"],
        "entity_batch_id": batch_id,
        "candidate_id": candidate_id,
        "batch_size": cfg["batch_size"],
    }


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "run_stage_meteorite"),
    reason="AST-1560 ingress transition runners not on this publish tip",
)

# Branches: map breadcrumb for email text; timezone clock; stage blank-link ERROR; schema fields (AST-1703).
class TestAst1703EmailBreadcrumb:
    """AST-1703: non-http meteorite.link breadcrumb for email text outcomes."""

    def test_email_breadcrumb_link_iso_and_rfc2822(self) -> None:
        from src.utils.config import format_job_link_breadcrumb

        iso = meteorite_mod._email_breadcrumb_link(
            from_email="list@co.com",
            to_email="cand@ex.com",
            sent_at="2026-09-17T18:05:00Z",
            timezone_key="America/New_York",
        )
        assert iso.startswith("From:list@co.com ")
        assert "Eastern" in iso
        assert iso.endswith(" To:cand@ex.com")
        assert not iso.startswith("http")
        assert not iso.startswith("email-")
        rfc = meteorite_mod._email_breadcrumb_link(
            from_email="a@x.com",
            to_email="b@y.com",
            sent_at="Thu, 17 Sep 2026 18:05:00 +0000",
            timezone_key="",
        )
        assert "From:a@x.com" in rfc and "To:b@y.com" in rfc
        assert "UTC" in rfc

    def test_email_breadcrumb_link_rejects_blank_and_bad_sent_at(self) -> None:
        with pytest.raises(ValueError, match="from_email"):
            meteorite_mod._email_breadcrumb_link(
                from_email="", to_email="b@y.com", sent_at="2026-09-17T18:05:00Z",
                timezone_key="",
            )
        with pytest.raises(ValueError, match="unparseable"):
            meteorite_mod._email_breadcrumb_link(
                from_email="a@x.com", to_email="b@y.com", sent_at="not-a-date",
                timezone_key="",
            )

    def test_map_email_text_sets_breadcrumb_paste_stays_none(self, sqlite_in_memory) -> None:
        from src.utils.config import STAGE_METEORITE_CONFIG

        outcome = STAGE_METEORITE_CONFIG["text_source_ref_outcomes"][0]
        rows, err = meteorite_mod._map_classify_jobs_to_meteorite_rows(
            outcome,
            [{
                "jd_text": "JD " + ("x" * 40),
                "from_email": "recruiter@co.com",
                "to_email": "me@ex.com",
                "sent_at": "2026-09-17T18:05:00+00:00",
            }],
            candidate_id="cand-map",
            source_kind="email",
            source_id="mid-1",
            timezone_key="America/Chicago",
        )
        assert err is None and len(rows) == 1
        link = rows[0]["link"]
        assert link and link.startswith("From:recruiter@co.com")
        assert "Central" in link
        assert link.endswith(" To:me@ex.com")

        paste_rows, paste_err = meteorite_mod._map_classify_jobs_to_meteorite_rows(
            outcome,
            [{"jd_text": "paste JD " + ("y" * 40)}],
            candidate_id="cand-map",
            source_kind="paste",
            source_id="paste-1",
            timezone_key="America/Chicago",
        )
        assert paste_err is None and paste_rows[0]["link"] is None

    def test_map_email_text_missing_headers_errors(self) -> None:
        from src.utils.config import STAGE_METEORITE_CONFIG

        outcome = STAGE_METEORITE_CONFIG["text_source_ref_outcomes"][0]
        rows, err = meteorite_mod._map_classify_jobs_to_meteorite_rows(
            outcome,
            [{"jd_text": "JD " + ("x" * 40), "from_email": "a@x.com"}],
            candidate_id="cand-map",
            source_kind="email",
            source_id="mid-2",
        )
        assert rows == []
        assert err and "to_email" in err

    def test_candidate_contact_timezone_reads_nested_contact(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-tz"
        db.save_candidate(
            cid,
            state="NEW_CANDIDATE",
            candidate_data={"name": "Z", "contact": {"timezone": "America/Los_Angeles"}},
        )
        assert meteorite_mod._candidate_contact_timezone(cid) == "America/Los_Angeles"
        assert meteorite_mod._candidate_contact_timezone("missing") == ""

    @pytest.mark.asyncio
    async def test_stage_email_text_blank_link_errors(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-stg-nobread"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "N"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            classify_outcome="single_jd_no_link",
            content="JD " + ("z" * 40),
            # link omitted → blank → ERROR missing breadcrumb link
        )
        out = await meteorite_mod.run_stage_meteorite(
            _ingress_task(batch_id="stage-batch-nobread", candidate_id=cid)
        )
        # AST-1751: ERROR arms bump total_errors only — not total_failed.
        assert out["total_failed"] == 0
        assert out["total_errors"] == 1
        row = db.get_meteorite(row_id)
        assert row["state"] == "ERROR_STAGE_METEORITE_UNPARSEABLE"
        assert "breadcrumb" in (row.get("error") or "")

    def test_stage_meteorite_schema_accepts_breadcrumb_fields(self) -> None:
        from src.utils import config as cfg

        items = cfg.TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]
        for key in ("from_email", "to_email", "sent_at"):
            assert key in items
            assert items[key]["type"] == "str"
            assert items[key]["required"] is False

    def test_agent_task_prompt_requires_header_fields(self) -> None:
        import json
        from pathlib import Path

        path = Path("data/admin/agent_task.json")
        assert path.is_file()
        blob = json.loads(path.read_text())
        rows = blob if isinstance(blob, list) else blob.get("agent_task") or blob.get("tasks") or []
        if isinstance(blob, dict) and not rows:
            # flat dict keyed by task — or list under another key
            rows = [v for v in blob.values() if isinstance(v, dict) and v.get("task_key") == "stage_meteorite"]
            if not rows and "task_key" in blob:
                rows = [blob]
        stage = next(
            (r for r in rows if isinstance(r, dict) and r.get("task_key") == "stage_meteorite"),
            None,
        )
        assert stage is not None, "stage_meteorite task missing from agent_task.json"
        cache = (stage.get("cache_prompt") or "") + (stage.get("user_prompt") or "")
        assert "from_email" in cache and "to_email" in cache and "sent_at" in cache
        assert "forward" in cache.lower() or "inner" in cache.lower()



class TestAst1560RunStageMeteorite:
    """AST-1560 / AST-1774: NEW → SCRAPE_LINK | CHECK_UNIQUE via dispatch claim batch."""

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
        out = await meteorite_mod.run_stage_meteorite(_ingress_task(batch_id=batch_id, candidate_id=cid))
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
        # AST-1703: email text rows require non-http breadcrumb on link before landable success.
        # AST-1774: landable success is CHECK_UNIQUE (not READY).
        crumb = "From:a@x.com 9/17 14:05 Eastern To:b@y.com"
        row_id = _insert_meteorite_row(
            db,
            cid,
            classify_outcome="single_jd_no_link",
            content="Full JD body " + ("x" * 40),
            link=crumb,
        )
        batch_id = "stage-batch-text"
        out = await meteorite_mod.run_stage_meteorite(_ingress_task(batch_id=batch_id, candidate_id=cid))
        assert out["total_passed"] == 1
        row = db.get_meteorite(row_id)
        assert row["state"] == "CHECK_UNIQUE"
        assert row["link"] == crumb

    @pytest.mark.asyncio
    async def test_missing_classify_outcome_errors_with_monitoring(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch, caplog
    ) -> None:
        # AST-2034 (parent AC8): unclassified NEW now goes to Ruth; a Ruth failure parks the
        # row at ERROR_STAGE_METEORITE — the old SCRAPE_ERROR "missing classify_outcome" arm is a Fail.
        import logging

        import src.core.agent as agent_mod

        db = sqlite_in_memory
        cid = "cand-stg-miss"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "M"})
        row_id = _insert_meteorite_row(db, cid, content="raw blob " + ("m" * 40))

        async def _do_task(**_kwargs):
            return {"success": False, "error": "llm down"}

        monkeypatch.setattr(agent_mod, "do_task", _do_task)
        with caplog.at_level(logging.WARNING):
            out = await meteorite_mod.run_stage_meteorite(
                _ingress_task(batch_id="stage-batch-miss", candidate_id=cid)
            )
        # AST-1751: ERROR arms bump total_errors only — not total_failed.
        assert out["total_failed"] == 0
        assert out["total_errors"] == 1
        row = db.get_meteorite(row_id)
        assert row["state"] == "ERROR_STAGE_METEORITE"
        assert row["error"] == "llm down"
        assert not any("missing classify_outcome" in r.getMessage() for r in caplog.records)
        # _row_miss warning names the row and the human-reset next step.
        assert any("ERROR_STAGE_METEORITE" in r.getMessage() for r in caplog.records)


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "run_scrape_meteorite"),
    reason="AST-1560 run_scrape_meteorite not on this publish tip",
)
class TestAst1560RunScrapeMeteorite:
    """AST-1560 / AST-1774: SCRAPE_LINK → CHECK_UNIQUE | BOT_BLOCKED_SCRAPE_METEORITE | SCRAPE_LINK_RETRY → ERROR_SCRAPE_METEORITE."""

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
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["scrape_task_key"],
            )
        )
        assert out["total_passed"] == 1
        row = db.get_meteorite(row_id)
        # AST-1774: scrape ok uses status_map["ok"] → CHECK_UNIQUE.
        assert row["state"] == "CHECK_UNIQUE"
        assert row["content"].startswith("Visible JD")
        assert row["link"] == "https://jobs.example.com/final"

    @pytest.mark.asyncio
    async def test_blocked_emits_monitoring(
        self,
        sqlite_in_memory,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        import logging

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

        monkeypatch.setattr(meteorite_mod, "_land_fetch_link_text", _fetch)
        monkeypatch.setattr("src.core.gazer._classify_jd", lambda _t: "bot")
        with caplog.at_level(logging.WARNING, logger="src.core.meteorite"):
            out = await meteorite_mod.run_scrape_meteorite(
                _ingress_task(
                    batch_id="scrape-batch-block",
                    candidate_id=cid,
                    task_key=METEORITE_INGRESS_DISPATCH_CONFIG["scrape_task_key"],
                )
            )
        # AST-1751: scrape BOT_BLOCKED_SCRAPE_METEORITE is fail-only (not pass, not error).
        assert out["total_failed"] == 1
        assert out["total_passed"] == 0
        assert out["total_errors"] == 0
        assert db.get_meteorite(row_id)["state"] == "BOT_BLOCKED_SCRAPE_METEORITE"
        # Product: _row_miss → logger.warning "… — scrape blocked at {link}" / BOT_BLOCKED_SCRAPE_METEORITE.
        assert any(
            "scrape blocked at" in r.getMessage() and "BOT_BLOCKED_SCRAPE_METEORITE" in r.getMessage()
            for r in caplog.records
        ), "expected _row_miss warning with scrape blocked + BOT_BLOCKED_SCRAPE_METEORITE"

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
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["scrape_task_key"],
            )
        )
        assert out["total_processed"] == 2
        assert out["total_passed"] == 1
        # AST-1751: ERROR row must not also bump total_failed.
        assert out["total_failed"] == 0
        assert out["total_errors"] == 1
        assert db.get_meteorite(bad_id)["state"] == "SCRAPE_LINK_RETRY"
        assert db.get_meteorite(good_id)["state"] == "CHECK_UNIQUE"

    @pytest.mark.asyncio
    async def test_ast1751_error_only_batch_fail_zero_error_n(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AST-1751 bug-repro: five failing SCRAPE_LINK rows (→ SCRAPE_LINK_RETRY) → fail:0 error:5 (not fail:5)."""
        db = sqlite_in_memory
        cid = "cand-scp-err5"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "E5"})
        for i in range(5):
            _insert_meteorite_row(
                db,
                cid,
                source_id=f"mid-err-{i}",
                state="SCRAPE_LINK",
                link="not-http",
            )

        out = await meteorite_mod.run_scrape_meteorite(
            _ingress_task(
                batch_id="scrape-batch-err5",
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["scrape_task_key"],
            )
        )
        assert out["total_processed"] == 5
        assert out["total_passed"] == 0
        assert out["total_failed"] == 0, (
            "AST-1751: ERROR-only batch must report fail:0 (errors are not also fails)"
        )
        assert out["total_errors"] == 5

    @pytest.mark.asyncio
    async def test_ast2086_scrape_failure_retries_once_then_errors(self, sqlite_in_memory) -> None:
        """AST-2086 AC5: SCRAPE_LINK failure → SCRAPE_LINK_RETRY; a failure from the retry → ERROR_SCRAPE_METEORITE."""
        db = sqlite_in_memory
        cid = "cand-scp-retry"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "R"})
        row_id = _insert_meteorite_row(db, cid, state="SCRAPE_LINK", link="not-http")
        tk = METEORITE_INGRESS_DISPATCH_CONFIG["scrape_task_key"]

        first = await meteorite_mod.run_scrape_meteorite(_ingress_task(batch_id="scrape-retry-1", candidate_id=cid, task_key=tk))
        assert db.get_meteorite(row_id)["state"] == "SCRAPE_LINK_RETRY"
        assert (first["total_errors"], first["total_failed"]) == (1, 0)

        # The retry companion is claimed by the same scrape dispatch; the second strike is terminal.
        second = await meteorite_mod.run_scrape_meteorite(_ingress_task(batch_id="scrape-retry-2", candidate_id=cid, task_key=tk))
        assert second["total_processed"] == 1
        assert db.get_meteorite(row_id)["state"] == "ERROR_SCRAPE_METEORITE"
        assert (second["total_errors"], second["total_failed"]) == (1, 0)

    @pytest.mark.asyncio
    async def test_ast1750_scrape_closed_error_includes_signal_text_len_final_url(
        self,
        sqlite_in_memory,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """AST-1750 bug-repro: soft-fail scrape_closed must carry signal/text_len/final_url."""
        import logging

        db = sqlite_in_memory
        cid = "cand-scp-closed"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "C"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            state="SCRAPE_LINK",
            link="https://www.dice.com/job-detail/abc",
        )
        visible = "Sorry, this job is no longer available. " + ("x" * 80)
        final_url = "https://www.dice.com/job-detail/abc-final"

        async def _fetch(_link, debug=False):
            return (visible, final_url)

        monkeypatch.setattr(meteorite_mod, "_land_fetch_link_text", _fetch)
        monkeypatch.setattr("src.core.gazer._classify_jd", lambda _t: "closed")

        with caplog.at_level(logging.WARNING, logger="src.core.meteorite"):
            out = await meteorite_mod.run_scrape_meteorite(
                _ingress_task(
                    batch_id="scrape-batch-closed",
                    candidate_id=cid,
                    task_key=METEORITE_INGRESS_DISPATCH_CONFIG["scrape_task_key"],
                ),
                debug=True,
            )

        # AST-1752: closed content is a JD_SCRAPE_FAIL_CLOSED fail, not an error.
        assert out["total_failed"] == 1
        assert out["total_errors"] == 0
        assert db.get_meteorite(row_id)["state"] == "JD_SCRAPE_FAIL_CLOSED"
        err = db.get_meteorite(row_id)["error"] or ""
        assert "scrape_closed" in err, f"expected scrape_closed in error, got {err!r}"
        assert "signal=" in err, (
            "AST-1750: scrape_closed error must name the matched closed_signals token"
        )
        assert "no longer available" in err
        assert f"text_len={len(visible)}" in err, (
            "AST-1750: scrape_closed error must include text_len="
        )
        assert "final_url=" in err and final_url in err, (
            "AST-1750: scrape_closed error must include final_url="
        )
        assert any(
            "signal=" in r.getMessage() and "scrape_closed" in r.getMessage()
            for r in caplog.records
        ), "AST-1750: warning must carry the same diagnostic why string"
        assert any(
            "This row is JD_SCRAPE_FAIL_CLOSED" in r.getMessage() for r in caplog.records
        ), "AST-1752: closed warning next step is JD_SCRAPE_FAIL_CLOSED"

    @pytest.mark.asyncio
    async def test_ast1752_missing_content_is_link_expired_fail(
        self,
        sqlite_in_memory,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """AST-1752 bug-repro: missing content verdict is a JD_SCRAPE_FAIL_MISSING fail, not an error."""
        import logging

        db = sqlite_in_memory
        cid = "cand-scp-missing"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "M"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            state="SCRAPE_LINK",
            link="https://jobs.example.com/gone",
        )
        visible = "not a posting"

        async def _fetch(_link, debug=False):
            return (visible, "https://jobs.example.com/gone-final")

        monkeypatch.setattr(meteorite_mod, "_land_fetch_link_text", _fetch)
        monkeypatch.setattr("src.core.gazer._classify_jd", lambda _t: "missing")

        with caplog.at_level(logging.WARNING, logger="src.core.meteorite"):
            out = await meteorite_mod.run_scrape_meteorite(
                _ingress_task(
                    batch_id="scrape-batch-missing",
                    candidate_id=cid,
                    task_key=METEORITE_INGRESS_DISPATCH_CONFIG["scrape_task_key"],
                )
            )

        assert out["total_failed"] == 1, (
            "AST-1752: missing content must count as fail, not error"
        )
        assert out["total_errors"] == 0
        assert out["total_passed"] == 0
        row = db.get_meteorite(row_id)
        assert row["state"] == "JD_SCRAPE_FAIL_MISSING"
        err = row["error"] or ""
        assert "scrape_missing" in err
        assert "signal=None" in err
        assert f"text_len={len(visible)}" in err
        assert "final_url=" in err
        assert any(
            "This row is JD_SCRAPE_FAIL_MISSING" in r.getMessage() for r in caplog.records
        )


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "run_land_meteorite"),
    reason="AST-1560 run_land_meteorite not on this publish tip",
)
class TestAst1560RunLandMeteorite:
    """AST-1560: READY → LANDED + METEORITE_NEW job (no enrich-in-front)."""

    @pytest.mark.asyncio
    async def test_ready_to_landed_without_enrich(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

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
            "src.core.meteorite.enrich_meteorite_land_packet", enrich
        )
        with caplog.at_level(logging.DEBUG, logger="src.core.meteorite"):
            out = await meteorite_mod.run_land_meteorite(
                _ingress_task(
                    batch_id="land-batch-1",
                    candidate_id=cid,
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
        assert any("READY -> LANDED" in r.getMessage() for r in caplog.records)

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
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["land_task_key"],
            )
        )
        # AST-1751: land ERROR arm bumps total_errors only — not total_failed.
        assert out["total_failed"] == 0
        assert out["total_errors"] == 1
        assert db.get_meteorite(row_id)["state"] == "ERROR_LAND_METEORITE"


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "apply_paste"),
    reason="AST-1561 BOT_BLOCKED_SCRAPE_METEORITE paste recovery not on this publish tip",
)
class TestAst1561ApplyPaste:
    """AST-1561: BOT_BLOCKED_SCRAPE_METEORITE → READY via paste (no classify)."""

    def test_moves_bot_blocked_to_ready(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-paste-ok"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "P"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            state="BOT_BLOCKED_SCRAPE_METEORITE",
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
        row_id = _insert_meteorite_row(db, cid, state="BOT_BLOCKED_SCRAPE_METEORITE")
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
            state="BOT_BLOCKED_SCRAPE_METEORITE",
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
            state="BOT_BLOCKED_SCRAPE_METEORITE",
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
            state="BOT_BLOCKED_SCRAPE_METEORITE",
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
            _notify_task(batch_id="notify-batch-1", candidate_id=cid)
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
            state="BOT_BLOCKED_SCRAPE_METEORITE",
            nag_count=nag_limit,
        )
        post = MagicMock()
        monkeypatch.setattr("src.core.contact.contact_post_message", post)
        out = await meteorite_mod.run_notify_meteorite_bot_blocked(
            _notify_task(batch_id="notify-batch-abandon", candidate_id=cid)
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

        monkeypatch.setattr("src.core.meteorite._classify_stage_blob", _invoke)
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

        monkeypatch.setattr("src.core.meteorite._classify_stage_blob", _invoke)
        out = await meteorite_mod.check_inbox({"candidate_id": cid}, debug=False)
        assert out["total_errors"] == 1
        rows = db.list_meteorites_by_source("email", mid)
        assert len(rows) == 1
        assert rows[0]["state"] == "ERROR_STAGE_METEORITE"
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

        monkeypatch.setattr("src.core.meteorite._classify_stage_blob", _invoke)
        out = await meteorite_mod.check_inbox({"candidate_id": cid}, debug=False)
        assert out["total_passed"] == 1
        rows = db.list_meteorites_by_source("email", mid)
        assert len(rows) == 1
        assert rows[0]["state"] == "NOT_A_JOB"
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
            [{"candidate_id": cid, "source_kind": "email", "source_id": mid, "link": "https://x/j", "state": "NEW"}]
        )
        invoke = AsyncMock()
        monkeypatch.setattr("src.core.meteorite._classify_stage_blob", invoke)
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

@pytest.mark.skipif(
    "electronic_contact_column" not in METEORITE_CONFIG
    or not hasattr(meteorite_mod, "_soft_persist_meteorite_electronic_contact"),
    reason="AST-1689 electronic_contact map/persist not on this publish tip",
)
class TestAst1689ElectronicContactMapPersist:
    """AST-1689: map Ruth contact → row; soft-fail; BOT_BLOCKED_SCRAPE_METEORITE preserve; no job_data."""

    @pytest.mark.asyncio
    async def test_text_outcome_stores_contact_on_row(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-1689-text"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "T"})
        mid = "msg-1689-text"
        col = METEORITE_CONFIG["electronic_contact_column"]
        monkeypatch.setattr(meteorite_mod, "email_aliases_for_candidate", lambda _c: ["a@b.c"])
        monkeypatch.setattr(
            meteorite_mod, "fetch_candidate_email", lambda _a, debug=False: [_check_inbox_msg(mid)]
        )
        monkeypatch.setattr(
            meteorite_mod,
            "get_message_html",
            lambda _m: {"subject": "JD", "html_body": "<p>x</p>", "from_address": "from@ex.com"},
        )
        monkeypatch.setattr(meteorite_mod, "strip_extract_email_html", lambda *a, **k: "blob")
        monkeypatch.setattr(meteorite_mod, "archive_candidate_email", MagicMock())

        async def _invoke(*_a, **_k):
            return {
                "success": True,
                "outcome": "single_jd_no_link",
                "jobs": [
                    {
                        "jd_text": "Full JD body " + ("x" * 40),
                        "from_email": "recruiter@co.com",
                        "to_email": "me@ex.com",
                        "sent_at": "2026-09-17T18:05:00+00:00",
                        "electronic_contact": "hiring@example.com",
                    }
                ],
                "error": None,
                "batch_id": "b",
            }

        monkeypatch.setattr("src.core.meteorite._classify_stage_blob", _invoke)
        out = await meteorite_mod.check_inbox({"candidate_id": cid}, debug=False)
        assert out["total_passed"] == 1
        rows = db.list_meteorites_by_source("email", mid)
        assert len(rows) == 1
        assert rows[0][col] == "hiring@example.com"
        assert rows[0]["state"] == "READY"

    @pytest.mark.asyncio
    async def test_empty_contact_still_ingests(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-1689-empty"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "E"})
        mid = "msg-1689-empty"
        col = METEORITE_CONFIG["electronic_contact_column"]
        monkeypatch.setattr(meteorite_mod, "email_aliases_for_candidate", lambda _c: ["a@b.c"])
        monkeypatch.setattr(
            meteorite_mod, "fetch_candidate_email", lambda _a, debug=False: [_check_inbox_msg(mid)]
        )
        monkeypatch.setattr(
            meteorite_mod,
            "get_message_html",
            lambda _m: {"subject": "JD", "html_body": "", "from_address": "a"},
        )
        monkeypatch.setattr(meteorite_mod, "strip_extract_email_html", lambda *a, **k: "blob")
        monkeypatch.setattr(meteorite_mod, "archive_candidate_email", MagicMock())

        async def _invoke(*_a, **_k):
            return {
                "success": True,
                "outcome": "single_jd_no_link",
                "jobs": [{
                    "jd_text": "Full JD body " + ("y" * 40),
                    "from_email": "recruiter@co.com",
                    "to_email": "me@ex.com",
                    "sent_at": "2026-09-17T18:05:00+00:00",
                }],
                "error": None,
                "batch_id": "b",
            }

        monkeypatch.setattr("src.core.meteorite._classify_stage_blob", _invoke)
        out = await meteorite_mod.check_inbox({"candidate_id": cid}, debug=False)
        assert out["total_passed"] == 1
        row = db.list_meteorites_by_source("email", mid)[0]
        assert row["state"] == "READY"
        assert row.get(col) in (None, "")

    @pytest.mark.asyncio
    async def test_soft_persist_failure_warns_row_stays_new(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch, caplog
    ) -> None:
        import logging

        db = sqlite_in_memory
        cid = "cand-1689-soft"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})
        mid = "msg-1689-soft"
        col = METEORITE_CONFIG["electronic_contact_column"]
        monkeypatch.setattr(meteorite_mod, "email_aliases_for_candidate", lambda _c: ["a@b.c"])
        monkeypatch.setattr(
            meteorite_mod, "fetch_candidate_email", lambda _a, debug=False: [_check_inbox_msg(mid)]
        )
        monkeypatch.setattr(
            meteorite_mod,
            "get_message_html",
            lambda _m: {"subject": "JD", "html_body": "", "from_address": "a"},
        )
        monkeypatch.setattr(meteorite_mod, "strip_extract_email_html", lambda *a, **k: "blob")
        monkeypatch.setattr(meteorite_mod, "archive_candidate_email", MagicMock())

        async def _invoke(*_a, **_k):
            return {
                "success": True,
                "outcome": "single_jd_no_link",
                "jobs": [
                    {
                        "jd_text": "Full JD body " + ("z" * 40),
                        "from_email": "recruiter@co.com",
                        "to_email": "me@ex.com",
                        "sent_at": "2026-09-17T18:05:00+00:00",
                        "electronic_contact": "soft@example.com",
                    }
                ],
                "error": None,
                "batch_id": "b",
            }

        monkeypatch.setattr("src.core.meteorite._classify_stage_blob", _invoke)
        real_update = meteorite_mod.update_meteorite

        def _boom(mid_arg, **kwargs):
            if col in kwargs:
                raise RuntimeError("contact persist boom")
            return real_update(mid_arg, **kwargs)

        monkeypatch.setattr(meteorite_mod, "update_meteorite", _boom)
        with caplog.at_level(logging.WARNING):
            out = await meteorite_mod.check_inbox({"candidate_id": cid}, debug=False)
        assert out["total_passed"] == 1
        row = db.list_meteorites_by_source("email", mid)[0]
        assert row["state"] == "READY"
        assert row[col] == "soft@example.com"

    @pytest.mark.asyncio
    async def test_bot_blocked_preserves_contact(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-1689-bot"
        col = METEORITE_CONFIG["electronic_contact_column"]
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "B"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            state="SCRAPE_LINK",
            link="https://jobs.example.com/bot",
            **{col: "keep@example.com"},
        )

        async def _fetch(_link, debug=False):
            return ("blocked page", _link)

        monkeypatch.setattr(meteorite_mod, "_land_fetch_link_text", _fetch)
        monkeypatch.setattr("src.core.gazer._classify_jd", lambda _t: "bot")
        out = await meteorite_mod.run_scrape_meteorite(
            _ingress_task(
                batch_id="scrape-1689-block",
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["scrape_task_key"],
            )
        )
        # AST-1751: scrape BOT_BLOCKED_SCRAPE_METEORITE counts as fail (contact column still preserved).
        assert out["total_failed"] == 1
        assert out["total_passed"] == 0
        row = db.get_meteorite(row_id)
        assert row["state"] == "BOT_BLOCKED_SCRAPE_METEORITE"
        assert row[col] == "keep@example.com"

    @pytest.mark.asyncio
    async def test_land_job_data_has_no_contact(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-1689-land"
        col = METEORITE_CONFIG["electronic_contact_column"]
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "L"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            state="READY",
            content="Landable JD " + ("q" * 40),
            **{col: "land@example.com"},
        )
        captured: dict = {}

        def _save(_cid, **kwargs):
            captured.update(kwargs)
            return {
                "outcome": METEORITE_CONFIG["land_outcome_created"],
                "astral_job_id": "job-1689-1",
            }

        monkeypatch.setattr(meteorite_mod.tracker, "save_meteorite_job", _save)
        monkeypatch.setattr(
            "src.core.meteorite.enrich_meteorite_land_packet", AsyncMock()
        )
        out = await meteorite_mod.run_land_meteorite(
            _ingress_task(
                batch_id="land-1689-1",
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["land_task_key"],
            )
        )
        assert out["total_passed"] == 1
        assert db.get_meteorite(row_id)["state"] == "LANDED"
        assert db.get_meteorite(row_id)[col] == "land@example.com"
        job_data = captured.get("job_data") or {}
        assert col not in job_data
        assert "electronic_contact" not in job_data
        assert col not in captured

    @pytest.mark.asyncio
    async def test_debug_emits_returned_vs_recorded(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch, caplog
    ) -> None:
        import logging

        db = sqlite_in_memory
        cid = "cand-1689-dbg"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "D"})
        mid = "msg-1689-dbg"
        monkeypatch.setattr(meteorite_mod, "email_aliases_for_candidate", lambda _c: ["a@b.c"])
        monkeypatch.setattr(
            meteorite_mod, "fetch_candidate_email", lambda _a, debug=False: [_check_inbox_msg(mid)]
        )
        monkeypatch.setattr(
            meteorite_mod,
            "get_message_html",
            lambda _m: {"subject": "JD", "html_body": "", "from_address": "a"},
        )
        monkeypatch.setattr(meteorite_mod, "strip_extract_email_html", lambda *a, **k: "blob")
        monkeypatch.setattr(meteorite_mod, "archive_candidate_email", MagicMock())

        async def _invoke(*_a, **_k):
            return {
                "success": True,
                "outcome": "single_jd_no_link",
                "jobs": [
                    {
                        "jd_text": "Full JD body " + ("d" * 40),
                        "from_email": "recruiter@co.com",
                        "to_email": "me@ex.com",
                        "sent_at": "2026-09-17T18:05:00+00:00",
                        "electronic_contact": "debug@example.com",
                    }
                ],
                "error": None,
                "batch_id": "b",
            }

        monkeypatch.setattr("src.core.meteorite._classify_stage_blob", _invoke)
        col = METEORITE_CONFIG["electronic_contact_column"]
        await meteorite_mod.check_inbox({"candidate_id": cid}, debug=True)
        row = db.list_meteorites_by_source("email", mid)[0]
        assert row["state"] == "READY"
        assert row[col] == "debug@example.com"

        mid2 = "msg-1689-nodbg"
        monkeypatch.setattr(
            meteorite_mod, "fetch_candidate_email", lambda _a, debug=False: [_check_inbox_msg(mid2)]
        )
        await meteorite_mod.check_inbox({"candidate_id": cid}, debug=False)
        row2 = db.list_meteorites_by_source("email", mid2)[0]
        assert row2[col] == "debug@example.com"

@pytest.mark.skipif(not hasattr(meteorite_mod, "run_land_meteorite"), reason="AST-1560 land runner not on this publish tip")
class TestAst1693RunLandBotBlocked:
    """AST-1693: claim BOT_BLOCKED_SCRAPE_METEORITE; contentful land with http job_link; empty stays."""

    @pytest.mark.asyncio
    async def test_contentful_bot_blocked_lands_with_http_link(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        cid = "cand-1693-land"
        link = "https://example.test/job/1"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "L"})
        row_id = _insert_meteorite_row(db, cid, state="BOT_BLOCKED_SCRAPE_METEORITE", content="Non-scrape JD " + ("q" * 40), link=link)
        captured: dict = {}
        def _save(_cid, **kwargs):
            captured.update(kwargs)
            return {"outcome": METEORITE_CONFIG["land_outcome_created"], "astral_job_id": "job-1693-land"}
        monkeypatch.setattr(meteorite_mod.tracker, "save_meteorite_job", _save)
        out = await meteorite_mod.run_land_meteorite(_ingress_task(batch_id="land-1693-bb", candidate_id=cid, task_key=METEORITE_INGRESS_DISPATCH_CONFIG["land_task_key"]))
        assert out["total_passed"] == 1
        row = db.get_meteorite(row_id)
        assert row["state"] == "LANDED" and row["astral_job_id"] == "job-1693-land"
        assert captured.get("job_link") == link

    @pytest.mark.asyncio
    async def test_empty_bot_blocked_left_for_estelle(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-1693-empty"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "E"})
        row_id = _insert_meteorite_row(db, cid, state="BOT_BLOCKED_SCRAPE_METEORITE", content="", link="https://example.test/job/empty")
        out = await meteorite_mod.run_land_meteorite(_ingress_task(batch_id="land-1693-empty", candidate_id=cid, task_key=METEORITE_INGRESS_DISPATCH_CONFIG["land_task_key"]))
        assert out["total_failed"] == 0 and out["total_errors"] == 0 and out["total_passed"] == 0
        row = db.get_meteorite(row_id)
        assert row["state"] == "BOT_BLOCKED_SCRAPE_METEORITE" and not row.get("astral_job_id")


@pytest.mark.skipif(not hasattr(meteorite_mod, "run_notify_meteorite_bot_blocked"), reason="AST-1561 notify runner not on this publish tip")
class TestAst1693NotifySkipsContentful:
    """AST-1693: contentful BOT_BLOCKED_SCRAPE_METEORITE belongs to land — notify must not DM."""

    @pytest.mark.asyncio
    async def test_skips_contentful_bot_blocked(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        cid = "cand-1693-notify"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "N", "contact": {"slack_user_id": "U-1693"}})
        row_id = _insert_meteorite_row(db, cid, state="BOT_BLOCKED_SCRAPE_METEORITE", content="Paste-ready JD " + ("x" * 40), link="https://jobs.example/blocked-contentful")
        post = MagicMock()
        monkeypatch.setattr(meteorite_mod, "_resolve_slack_dm_channel_for_candidate", lambda _c: "D-1693")
        monkeypatch.setattr("src.core.contact.contact_post_message", post)
        out = await meteorite_mod.run_notify_meteorite_bot_blocked(_notify_task(batch_id="notify-1693-skip", candidate_id=cid))
        assert out["total_passed"] == 0
        row = db.get_meteorite(row_id)
        assert row["state"] == "BOT_BLOCKED_SCRAPE_METEORITE" and not row.get("estelle_notified_at")
        post.assert_not_called()



@pytest.mark.skipif(
    not hasattr(meteorite_mod, "_classify_stage_blob"),
    reason="AST-1713 stage save not on this publish tip",
)
class TestAst1713StageSavesRuthRow:
    """AST-1713: stage_meteorite inserts the Ruth row; consult is off this path."""

    def _save(self, db, cid: str) -> None:
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "R"})

    def _patch(self, monkeypatch: pytest.MonkeyPatch, payload: dict) -> None:
        async def _classify(*_a, **_k):
            return payload

        monkeypatch.setattr(meteorite_mod, "_classify_stage_blob", _classify)

    @pytest.mark.asyncio
    async def test_not_a_job_inserts_one_row(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import STAGE_METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-1713-skip"
        self._save(db, cid)
        outcome = STAGE_METEORITE_CONFIG["skip_outcomes"][0]
        self._patch(monkeypatch, {
            "success": True,
            "outcome": outcome,
            "jobs": [],
            "error": None,
            "batch_id": "b-skip",
        })
        out = await meteorite_mod.stage_meteorite(
            cid, "noise", source_kind="email", source_id="mid-skip",
        )
        assert out["skipped"] is True
        assert out["outcome"] == outcome
        rows = db.list_meteorites_by_source("email", "mid-skip")
        assert len(rows) == 1
        assert rows[0]["state"] == "NOT_A_JOB"
        assert rows[0]["classify_outcome"] == outcome

    @pytest.mark.asyncio
    async def test_scrape_link_http_and_ruth_fields(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import STAGE_METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-1713-url"
        self._save(db, cid)
        outcome = STAGE_METEORITE_CONFIG["url_scrape_outcomes"][0]
        self._patch(monkeypatch, {
            "success": True,
            "outcome": outcome,
            "jobs": [{
                "job_link": "https://jobs.example/role",
                "jd_text": "JD " + ("u" * 40),
                "job_title": "Engineer",
                "employer_name": "Acme",
            }],
            "error": None,
            "batch_id": "b-url",
        })
        out = await meteorite_mod.stage_meteorite(
            cid, "blob", source_kind="email", source_id="mid-url",
        )
        assert out["skipped"] is False
        assert out["error"] is None
        rows = db.list_meteorites_by_source("email", "mid-url")
        assert len(rows) == 1
        assert rows[0]["state"] == "SCRAPE_LINK"
        assert str(rows[0]["link"]).startswith("https://")
        assert rows[0]["job_title"] == "Engineer"
        assert rows[0]["employer_name"] == "Acme"

    @pytest.mark.asyncio
    async def test_ready_breadcrumb_is_not_http(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import STAGE_METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-1713-text"
        self._save(db, cid)
        outcome = STAGE_METEORITE_CONFIG["text_source_ref_outcomes"][0]
        self._patch(monkeypatch, {
            "success": True,
            "outcome": outcome,
            "jobs": [{
                "jd_text": "JD " + ("t" * 40),
                "from_email": "recruiter@co.com",
                "to_email": "me@ex.com",
                "sent_at": "2026-09-17T18:05:00+00:00",
            }],
            "error": None,
            "batch_id": "b-text",
        })
        out = await meteorite_mod.stage_meteorite(
            cid, "blob", source_kind="email", source_id="mid-text",
        )
        assert out["error"] is None
        rows = db.list_meteorites_by_source("email", "mid-text")
        assert len(rows) == 1
        link = rows[0]["link"] or ""
        assert rows[0]["state"] == "READY"
        assert link and not link.startswith("http")

    @pytest.mark.asyncio
    async def test_missing_candidate_inserts_new_email_error(
        self, sqlite_in_memory
    ) -> None:
        db = sqlite_in_memory
        out = await meteorite_mod.stage_meteorite(
            "missing-1713", "blob", source_kind="email", source_id="mid-miss",
        )
        assert out["error"] and "candidate not found" in out["error"]
        rows = db.list_meteorites_by_source("email", "mid-miss")
        assert len(rows) == 1
        assert rows[0]["state"] == "ERROR_STAGE_METEORITE"

    def test_insert_binds_caller_state(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-1713-ins"
        self._save(db, cid)
        row_id = db.insert_meteorite_rows([{
            "candidate_id": cid,
            "source_kind": "paste",
            "source_id": "ins-1",
            "state": "READY",
            "job_title": "Title",
            "employer_name": "Emp",
        }])[0]
        row = db.get_meteorite(row_id)
        assert row["state"] == "READY"
        assert row["job_title"] == "Title"
        assert row["employer_name"] == "Emp"

    def test_stage_invoke_and_consult_import_gone(self) -> None:
        import inspect
        import src.core.consult as consult_mod

        assert not hasattr(consult_mod, "invoke_stage_meteorite")
        assert not hasattr(consult_mod, "enrich_meteorite_land_packet")
        assert "consult" not in inspect.getsource(meteorite_mod)


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "ingest_candidate_email_message"),
    reason="ingest_candidate_email_message not on this publish tip",
)
class TestAst1743IngestSkipFailed:
    """AST-1743: ingest skip / NOT_A_JOB returns counter=failed (not passed)."""

    @pytest.mark.asyncio
    async def test_skip_outcome_returns_counter_failed(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AST-1743 [bug-repro]: skip + archive success → counter failed."""
        db = sqlite_in_memory
        cid = "cand-1743-ingest"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Ing"})
        mid = "msg-1743-ingest"
        monkeypatch.setattr(
            meteorite_mod,
            "get_message_html",
            lambda _m: {
                "subject": "s",
                "html_body": "<p>x</p>",
                "from_address": "a@ex.com",
                "to_address": "b@ex.com",
                "date": "1",
            },
        )
        monkeypatch.setattr(
            meteorite_mod, "strip_extract_email_html", lambda *a, **k: "blob"
        )
        archive = MagicMock()
        monkeypatch.setattr(meteorite_mod, "archive_candidate_email", archive)

        async def _stage(*_a, **_k):
            return {
                "outcome": "not_job_content",
                "stage_outcome": "not_job_content",
                "skipped": True,
                "jobs": [],
                "error": None,
                "batch_id": "b",
            }

        monkeypatch.setattr(meteorite_mod, "stage_meteorite", _stage)
        out = await meteorite_mod.ingest_candidate_email_message(cid, mid, debug=False)
        assert out["counter"] == "failed"
        assert out["outcome"] == "not_job_content"
        assert out.get("error") in (None, "")
        archive.assert_called_once_with(mid)


# Branches: text-outcome blank/missing jd_text → ingress_blob content; present jd_text wins;
# degenerate empty blob still errors; URL empty jd_text unchanged; stage_meteorite wires blob (AST-1756).
@pytest.mark.skipif(
    not hasattr(meteorite_mod, "_map_classify_jobs_to_meteorite_rows"),
    reason="AST-1756 map helper not on this publish tip",
)
class TestAst1756IngressBlobJdTextFallback:
    """AST-1756: text landable blank jd_text falls back to classify ingress blob."""

    _BLOB = "Subject: Widget role\n\nFull JD body here."

    def test_blank_jd_text_uses_ingress_blob(self) -> None:
        from src.utils.config import STAGE_METEORITE_CONFIG

        outcome = STAGE_METEORITE_CONFIG["text_source_ref_outcomes"][0]
        rows, err = meteorite_mod._map_classify_jobs_to_meteorite_rows(
            outcome,
            [{"jd_text": ""}],
            candidate_id="c1",
            source_kind="paste",
            source_id="s1",
            ingress_blob=self._BLOB,
        )
        assert err is None
        assert rows and rows[0]["content"] == self._BLOB.strip()

    def test_missing_jd_text_key_uses_ingress_blob(self) -> None:
        from src.utils.config import STAGE_METEORITE_CONFIG

        outcome = STAGE_METEORITE_CONFIG["text_source_ref_outcomes"][0]
        rows, err = meteorite_mod._map_classify_jobs_to_meteorite_rows(
            outcome,
            [{}],
            candidate_id="c1",
            source_kind="paste",
            source_id="s1",
            ingress_blob=self._BLOB,
        )
        assert err is None
        assert rows[0]["content"] == self._BLOB.strip()

    def test_present_jd_text_wins_over_blob(self) -> None:
        from src.utils.config import STAGE_METEORITE_CONFIG

        outcome = STAGE_METEORITE_CONFIG["text_source_ref_outcomes"][0]
        rows, err = meteorite_mod._map_classify_jobs_to_meteorite_rows(
            outcome,
            [{"jd_text": "  Ruth JD only  "}],
            candidate_id="c1",
            source_kind="paste",
            source_id="s1",
            ingress_blob=self._BLOB,
        )
        assert err is None
        assert rows[0]["content"] == "Ruth JD only"

    def test_blank_jd_text_and_blank_blob_still_errors(self) -> None:
        from src.utils.config import STAGE_METEORITE_CONFIG

        outcome = STAGE_METEORITE_CONFIG["text_source_ref_outcomes"][0]
        rows, err = meteorite_mod._map_classify_jobs_to_meteorite_rows(
            outcome,
            [{"jd_text": ""}],
            candidate_id="c1",
            source_kind="paste",
            source_id="s1",
            ingress_blob="   ",
        )
        assert rows == []
        assert err == "text scrap missing jd_text"

    def test_url_outcome_empty_jd_text_unchanged(self) -> None:
        from src.utils.config import STAGE_METEORITE_CONFIG

        outcome = STAGE_METEORITE_CONFIG["url_scrape_outcomes"][0]
        rows, err = meteorite_mod._map_classify_jobs_to_meteorite_rows(
            outcome,
            [{"job_link": "https://example.com/j", "jd_text": ""}],
            candidate_id="c1",
            source_kind="paste",
            source_id="s1",
            ingress_blob=self._BLOB,
        )
        assert err is None
        assert rows[0]["content"] is None

    @pytest.mark.asyncio
    async def test_stage_meteorite_blank_jd_text_persists_blob(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import STAGE_METEORITE_CONFIG

        if not hasattr(meteorite_mod, "stage_meteorite"):
            pytest.skip("stage_meteorite not on this publish tip")
        db = sqlite_in_memory
        cid = "cand-1756-blob"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "B"})
        outcome = STAGE_METEORITE_CONFIG["text_source_ref_outcomes"][0]
        blob = self._BLOB

        async def _classify(*_a, **_k):
            return {
                "success": True,
                "outcome": outcome,
                "jobs": [{"jd_text": ""}],
                "error": None,
                "batch_id": "b-1756",
            }

        monkeypatch.setattr(meteorite_mod, "_classify_stage_blob", _classify)
        out = await meteorite_mod.stage_meteorite(
            cid, blob, source_kind="paste", source_id="paste-1756",
        )
        assert out.get("error") in (None, "")
        rows = db.list_meteorites_by_source("paste", "paste-1756")
        assert len(rows) == 1
        assert rows[0]["content"] == blob.strip()
        assert rows[0]["state"] == "READY"


# Branches: dispatch land passes staged job_title; public land enrich-preferred /
# staged-fallback (AST-1757).
@pytest.mark.skipif(
    not hasattr(meteorite_mod, "run_land_meteorite"),
    reason="AST-1757 land runners not on this publish tip",
)
class TestAst1757LandStagedJobTitle:
    """AST-1757: land wires staged meteorite.job_title; enrich title wins when present."""

    @pytest.mark.asyncio
    async def test_dispatch_passes_staged_job_title(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AC7: run_land_meteorite passes row job_title into save_meteorite_job."""
        db = sqlite_in_memory
        cid = "cand-1757-dispatch"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "D"})
        _insert_meteorite_row(
            db,
            cid,
            state="READY",
            content="Landable JD " + ("q" * 40),
            job_title="Senior Widget Engineer",
        )
        captured: dict = {}

        def _save(_cid, **kwargs):
            captured.update(kwargs)
            return {
                "outcome": METEORITE_CONFIG["land_outcome_created"],
                "astral_job_id": "job-1757-d",
            }

        monkeypatch.setattr(meteorite_mod.tracker, "save_meteorite_job", _save)
        out = await meteorite_mod.run_land_meteorite(
            _ingress_task(
                batch_id="land-1757-d",
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["land_task_key"],
            )
        )
        assert out["total_passed"] == 1
        assert captured.get("job_title") == "Senior Widget Engineer"

    @pytest.mark.asyncio
    async def test_public_land_staged_when_enrich_blank(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AC8: enrich blank → job.job_title from meteorite column."""
        db = sqlite_in_memory
        cid = "cand-1757-ac8"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "A"})
        mid = _insert_meteorite_row(
            db,
            cid,
            state="READY",
            content="seed " + ("z" * 40),
            source_kind="paste",
            source_id="paste-1757-ac8",
            job_title="Senior Widget Engineer",
        )

        async def _enrich(_cid, scraps, **_k):
            return {
                "success": True,
                "jobs": [{
                    "company_job_id": "AC8JOB01",
                    "job_title": "",
                    "jd_text": "JD " + ("x" * 40),
                    "scrap_index": 0,
                }],
            }

        monkeypatch.setattr(
            "src.core.meteorite.enrich_meteorite_land_packet", _enrich
        )
        out = await meteorite_mod.land_meteorite(
            cid, text="j" * 50, meteorite_id=mid
        )
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_created"]
        job = db.get_job(out["outcomes"][0]["astral_job_id"])
        assert job["job_title"] == "Senior Widget Engineer"

    @pytest.mark.asyncio
    async def test_public_land_enrich_wins_over_staged(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AC9: non-empty enrich title wins over differing staged column."""
        db = sqlite_in_memory
        cid = "cand-1757-ac9"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "B"})
        mid = _insert_meteorite_row(
            db,
            cid,
            state="READY",
            content="seed " + ("z" * 40),
            source_kind="paste",
            source_id="paste-1757-ac9",
            job_title="Staged Title Only",
        )

        async def _enrich(_cid, scraps, **_k):
            return {
                "success": True,
                "jobs": [{
                    "company_job_id": "AC9JOB01",
                    "job_title": "Enrich Preferred Title",
                    "jd_text": "JD " + ("y" * 40),
                    "scrap_index": 0,
                }],
            }

        monkeypatch.setattr(
            "src.core.meteorite.enrich_meteorite_land_packet", _enrich
        )
        out = await meteorite_mod.land_meteorite(
            cid, text="k" * 50, meteorite_id=mid
        )
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_created"]
        job = db.get_job(out["outcomes"][0]["astral_job_id"])
        assert job["job_title"] == "Enrich Preferred Title"


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "run_check_unique_meteorite"),
    reason="AST-1774 run_check_unique_meteorite not on this publish tip",
)
class TestAst1774RunCheckUniqueMeteorite:
    """AST-1774: CHECK_UNIQUE → READY (unique) | peer paths call hook (AST-1775 fills body)."""

    @pytest.mark.asyncio
    async def test_unique_promotes_to_ready(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-cu-unique"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "U"})
        # Unrelated LANDED peer (different title) must not block unique path.
        _insert_meteorite_row(
            db,
            cid,
            source_id="landed-other",
            state="LANDED",
            job_title="Other Role",
            employer_name="Other Co",
            content="landed " + ("x" * 40),
        )
        row_id = _insert_meteorite_row(
            db,
            cid,
            source_id="cu-unique",
            state="CHECK_UNIQUE",
            job_title="Engineer",
            employer_name="Acme",
            content="unique JD " + ("y" * 40),
        )
        batch_id = "cu-batch-unique"
        out = await meteorite_mod.run_check_unique_meteorite(
            _ingress_task(
                batch_id=batch_id,
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"],
            )
        )
        assert out["total_passed"] == 1
        assert out["total_errors"] == 0
        assert db.get_meteorite(row_id)["state"] == "READY"
        assert db.get_meteorite_batch(batch_id) == []

    @pytest.mark.asyncio
    async def test_title_employer_sql_peers_call_hook_leave_check_unique(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-cu-sql"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})
        peer_id = _insert_meteorite_row(
            db,
            cid,
            source_id="landed-match",
            state="LANDED",
            job_title="Engineer",
            employer_name="Acme",
            content="peer JD " + ("z" * 40),
        )
        row_id = _insert_meteorite_row(
            db,
            cid,
            source_id="cu-sql",
            state="CHECK_UNIQUE",
            job_title="Engineer",
            employer_name="Acme",
            content="subject JD " + ("a" * 40),
        )
        seen: list = []

        async def _hook(row, peers, *, batch_id, debug=False):
            seen.append((int(row["id"]), [int(p["id"]) for p in peers], batch_id))

        monkeypatch.setattr(meteorite_mod, "_review_duplicate_meteorite_hook", _hook)
        out = await meteorite_mod.run_check_unique_meteorite(
            _ingress_task(
                batch_id="cu-batch-sql",
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"],
            )
        )
        assert out["total_passed"] == 1
        assert db.get_meteorite(row_id)["state"] == "CHECK_UNIQUE"
        assert seen == [(row_id, [peer_id], "cu-batch-sql")]

    @pytest.mark.asyncio
    async def test_null_field_multi_peers_call_hook(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-cu-null"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "N"})
        p1 = _insert_meteorite_row(
            db, cid, source_id="null-1", state="LANDED", content="p1 " + ("b" * 40),
        )
        p2 = _insert_meteorite_row(
            db, cid, source_id="null-2", state="LANDED", content="p2 " + ("c" * 40),
        )
        # Subject missing employer — SQL path empty; ≥2 nullish LANDED → hook.
        row_id = _insert_meteorite_row(
            db,
            cid,
            source_id="cu-null",
            state="CHECK_UNIQUE",
            job_title="Engineer",
            content="subject " + ("d" * 40),
        )
        seen: list = []

        async def _hook(row, peers, *, batch_id, debug=False):
            seen.append((int(row["id"]), sorted(int(p["id"]) for p in peers)))

        monkeypatch.setattr(meteorite_mod, "_review_duplicate_meteorite_hook", _hook)
        out = await meteorite_mod.run_check_unique_meteorite(
            _ingress_task(
                batch_id="cu-batch-null",
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"],
            )
        )
        assert out["total_passed"] == 1
        assert db.get_meteorite(row_id)["state"] == "CHECK_UNIQUE"
        assert seen == [(row_id, sorted([p1, p2]))]

    @pytest.mark.asyncio
    async def test_no_match_on_content_or_source_id(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AC5: equal JD text / source_id alone must not count as SQL peers."""
        db = sqlite_in_memory
        cid = "cand-cu-nomatch"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "M"})
        same_body = "Same JD body " + ("e" * 40)
        _insert_meteorite_row(
            db,
            cid,
            source_id="shared-mid",
            state="LANDED",
            job_title="Different Title",
            employer_name="Acme",
            content=same_body,
        )
        row_id = _insert_meteorite_row(
            db,
            cid,
            source_id="shared-mid",  # same source_id — must not match
            state="CHECK_UNIQUE",
            job_title="Engineer",
            employer_name="Acme",
            content=same_body,
        )
        hooks = []

        async def _hook(*_a, **_k):
            hooks.append(True)

        monkeypatch.setattr(meteorite_mod, "_review_duplicate_meteorite_hook", _hook)
        out = await meteorite_mod.run_check_unique_meteorite(
            _ingress_task(
                batch_id="cu-batch-nomatch",
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"],
            )
        )
        assert out["total_passed"] == 1
        assert hooks == []
        assert db.get_meteorite(row_id)["state"] == "READY"

    @pytest.mark.asyncio
    async def test_land_does_not_claim_check_unique(self, sqlite_in_memory) -> None:
        """AC6 / AC9: land remains READY-gated; CHECK_UNIQUE is not landable."""
        db = sqlite_in_memory
        cid = "cand-cu-landgate"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "L"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            state="CHECK_UNIQUE",
            content="stuck " + ("f" * 40),
            link="https://jobs.example.com/stuck",
        )
        out = await meteorite_mod.run_land_meteorite(
            _ingress_task(
                batch_id="cu-batch-landgate",
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["land_task_key"],
            )
        )
        assert out["total_processed"] == 0
        assert db.get_meteorite(row_id)["state"] == "CHECK_UNIQUE"
        assert METEORITE_INGRESS_DISPATCH_CONFIG["land_trigger_state"] == "READY"

    def test_apply_paste_still_writes_ready(self, sqlite_in_memory) -> None:
        """Boundary: apply_paste stays READY — not retargeted to CHECK_UNIQUE."""
        db = sqlite_in_memory
        cid = "cand-cu-paste"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "P"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            state="BOT_BLOCKED_SCRAPE_METEORITE",
            link="https://jobs.example.com/blocked",
        )
        out = meteorite_mod.apply_paste(row_id, "Paste JD body " + ("p" * 40))
        assert out == {"ok": True, "meteorite_id": row_id, "state": "READY"}
        assert db.get_meteorite(row_id)["state"] == "READY"


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "_review_duplicate_live_content"),
    reason="AST-1775 Ruth duplicate-review invoke not on this publish tip",
)
class TestAst1775RuthDuplicateReviewInvoke:
    """AST-1775: peer hook → do_task → DUPLICATE|READY; failures stay CHECK_UNIQUE."""

    @staticmethod
    def _sql_peer_fixture(db, cid: str) -> tuple[int, int]:
        peer_id = _insert_meteorite_row(
            db,
            cid,
            source_id="landed-ruth",
            state="LANDED",
            job_title="Engineer",
            employer_name="Acme",
            content="peer full body " + ("z" * 40),
            link="https://jobs.example.com/peer",
        )
        row_id = _insert_meteorite_row(
            db,
            cid,
            source_id="cu-ruth",
            state="CHECK_UNIQUE",
            job_title="Engineer",
            employer_name="Acme",
            content="subject full body " + ("a" * 40),
            link="https://jobs.example.com/subject",
        )
        return row_id, peer_id

    @pytest.mark.asyncio
    async def test_sql_peers_duplicate_maps_to_duplicate_with_peer_id(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import REVIEW_DUPLICATE_METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-ruth-dup"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "D"})
        row_id, peer_id = self._sql_peer_fixture(db, cid)
        peer_key = REVIEW_DUPLICATE_METEORITE_CONFIG["peer_id_response_key"]
        task_key = REVIEW_DUPLICATE_METEORITE_CONFIG["task_key"]
        calls: list = []

        async def _do_task(**kwargs):
            calls.append(kwargs)
            return {
                "success": True,
                "parsed_response": {
                    "outcome": "duplicate",
                    peer_key: str(peer_id),
                },
            }

        monkeypatch.setattr("src.core.agent.do_task", _do_task)
        out = await meteorite_mod.run_check_unique_meteorite(
            _ingress_task(
                batch_id="ruth-batch-dup",
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"],
            )
        )
        assert out["total_passed"] == 1
        row = db.get_meteorite(row_id)
        assert row["state"] == "DUPLICATE"
        assert row["error"] == f"duplicate_of:{peer_id}"
        assert len(calls) == 1
        assert calls[0]["task_key"] == task_key
        live = calls[0]["live_content"]
        assert "CHECK_UNIQUE:" in live
        assert f"LANDED peer id={peer_id}:" in live
        assert "subject full body" in live
        assert "peer full body" in live
        assert calls[0]["index"] == f"{task_key}_{row_id}_ruth-batch-dup"

    @pytest.mark.asyncio
    async def test_sql_peers_not_duplicate_maps_to_ready(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-ruth-nd"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "N"})
        row_id, _peer_id = self._sql_peer_fixture(db, cid)

        async def _do_task(**_kwargs):
            return {"success": True, "parsed_response": {"outcome": "not_duplicate"}}

        monkeypatch.setattr("src.core.agent.do_task", _do_task)
        out = await meteorite_mod.run_check_unique_meteorite(
            _ingress_task(
                batch_id="ruth-batch-nd",
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"],
            )
        )
        assert out["total_passed"] == 1
        assert db.get_meteorite(row_id)["state"] == "READY"

    @pytest.mark.asyncio
    async def test_null_peers_invoke_ruth_with_full_content(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-ruth-null"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Z"})
        p1 = _insert_meteorite_row(
            db, cid, source_id="null-r1", state="LANDED", content="null peer one " + ("b" * 40),
        )
        p2 = _insert_meteorite_row(
            db, cid, source_id="null-r2", state="LANDED", content="null peer two " + ("c" * 40),
        )
        row_id = _insert_meteorite_row(
            db,
            cid,
            source_id="cu-ruth-null",
            state="CHECK_UNIQUE",
            job_title="Engineer",
            content="null subject " + ("d" * 40),
        )
        calls: list = []

        async def _do_task(**kwargs):
            calls.append(kwargs)
            return {"success": True, "parsed_response": {"outcome": "not_duplicate"}}

        monkeypatch.setattr("src.core.agent.do_task", _do_task)
        out = await meteorite_mod.run_check_unique_meteorite(
            _ingress_task(
                batch_id="ruth-batch-null",
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"],
            )
        )
        assert out["total_passed"] == 1
        assert db.get_meteorite(row_id)["state"] == "READY"
        assert len(calls) == 1
        live = calls[0]["live_content"]
        assert "null subject" in live
        assert "null peer one" in live
        assert "null peer two" in live
        assert f"LANDED peer id={p1}:" in live
        assert f"LANDED peer id={p2}:" in live

    @pytest.mark.asyncio
    async def test_do_task_failure_leaves_check_unique(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-ruth-fail"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "F"})
        row_id, _peer_id = self._sql_peer_fixture(db, cid)

        async def _do_task(**_kwargs):
            return {"success": False, "error": "ruth down"}

        monkeypatch.setattr("src.core.agent.do_task", _do_task)
        out = await meteorite_mod.run_check_unique_meteorite(
            _ingress_task(
                batch_id="ruth-batch-fail",
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"],
            )
        )
        assert out["total_passed"] == 1
        assert db.get_meteorite(row_id)["state"] == "CHECK_UNIQUE"

    @pytest.mark.asyncio
    async def test_invalid_outcome_leaves_check_unique(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-ruth-badout"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "B"})
        row_id, _peer_id = self._sql_peer_fixture(db, cid)

        async def _do_task(**_kwargs):
            return {"success": True, "parsed_response": {"outcome": "maybe"}}

        monkeypatch.setattr("src.core.agent.do_task", _do_task)
        out = await meteorite_mod.run_check_unique_meteorite(
            _ingress_task(
                batch_id="ruth-batch-badout",
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"],
            )
        )
        assert out["total_passed"] == 1
        assert db.get_meteorite(row_id)["state"] == "CHECK_UNIQUE"

    @pytest.mark.asyncio
    async def test_invalid_peer_id_leaves_check_unique(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import REVIEW_DUPLICATE_METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-ruth-badpeer"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "P"})
        row_id, _peer_id = self._sql_peer_fixture(db, cid)
        peer_key = REVIEW_DUPLICATE_METEORITE_CONFIG["peer_id_response_key"]

        async def _do_task(**_kwargs):
            return {
                "success": True,
                "parsed_response": {"outcome": "duplicate", peer_key: "999999"},
            }

        monkeypatch.setattr("src.core.agent.do_task", _do_task)
        out = await meteorite_mod.run_check_unique_meteorite(
            _ingress_task(
                batch_id="ruth-batch-badpeer",
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["check_unique_task_key"],
            )
        )
        assert out["total_passed"] == 1
        assert db.get_meteorite(row_id)["state"] == "CHECK_UNIQUE"

    @pytest.mark.asyncio
    async def test_land_does_not_claim_duplicate(self, sqlite_in_memory) -> None:
        """AC9: DUPLICATE is not landable; land stays READY-gated."""
        db = sqlite_in_memory
        cid = "cand-ruth-landgate"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "L"})
        row_id = _insert_meteorite_row(
            db,
            cid,
            state="DUPLICATE",
            content="dup " + ("f" * 40),
            link="https://jobs.example.com/dup",
            error="duplicate_of:1",
        )
        out = await meteorite_mod.run_land_meteorite(
            _ingress_task(
                batch_id="ruth-batch-landgate",
                candidate_id=cid,
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["land_task_key"],
            )
        )
        assert out["total_processed"] == 0
        assert db.get_meteorite(row_id)["state"] == "DUPLICATE"
        assert METEORITE_INGRESS_DISPATCH_CONFIG["land_trigger_state"] == "READY"


# Branches: text outcome + http job_link → URL on link + SCRAPE_LINK; breadcrumb only
# when no http job_link; URL outcomes unchanged (AST-1785).
@pytest.mark.skipif(
    not hasattr(meteorite_mod, "_map_classify_jobs_to_meteorite_rows"),
    reason="AST-1785 map helper not on this publish tip",
)
class TestAst1785PreferHttpJobLinkOverBreadcrumb:
    """AST-1785: http(s) job_link wins over email breadcrumb; scrape path when link is http."""

    def test_map_text_outcome_http_job_link_wins_over_breadcrumb(self) -> None:
        from src.utils.config import STAGE_METEORITE_CONFIG

        outcome = STAGE_METEORITE_CONFIG["text_source_ref_outcomes"][0]
        url = "https://example.com/jobs/1"
        rows, err = meteorite_mod._map_classify_jobs_to_meteorite_rows(
            outcome,
            [{
                "jd_text": "JD " + ("x" * 40),
                "job_link": url,
                "job_title": "Senior Widget Engineer",
                "from_email": "recruiter@co.com",
                "to_email": "me@ex.com",
                "sent_at": "2026-09-17T18:05:00+00:00",
            }],
            candidate_id="cand-1785-map",
            source_kind="email",
            source_id="mid-1785-map",
            timezone_key="America/New_York",
        )
        assert err is None and len(rows) == 1
        assert rows[0]["link"] == url
        assert not str(rows[0]["link"]).startswith("From:")

    def test_map_text_outcome_without_http_job_link_keeps_breadcrumb(self) -> None:
        from src.utils.config import STAGE_METEORITE_CONFIG

        outcome = STAGE_METEORITE_CONFIG["text_source_ref_outcomes"][0]
        rows, err = meteorite_mod._map_classify_jobs_to_meteorite_rows(
            outcome,
            [{
                "jd_text": "JD " + ("x" * 40),
                "from_email": "recruiter@co.com",
                "to_email": "me@ex.com",
                "sent_at": "2026-09-17T18:05:00+00:00",
            }],
            candidate_id="cand-1785-crumb",
            source_kind="email",
            source_id="mid-1785-crumb",
            timezone_key="America/Chicago",
        )
        assert err is None and len(rows) == 1
        link = rows[0]["link"] or ""
        assert link.startswith("From:recruiter@co.com")
        assert not link.startswith("http")

    def test_map_url_outcome_still_requires_http_job_link(self) -> None:
        from src.utils.config import STAGE_METEORITE_CONFIG

        outcome = STAGE_METEORITE_CONFIG["url_scrape_outcomes"][0]
        url = "https://jobs.example.com/list-item"
        rows, err = meteorite_mod._map_classify_jobs_to_meteorite_rows(
            outcome,
            [{"job_link": url, "jd_text": ""}],
            candidate_id="cand-1785-url",
            source_kind="email",
            source_id="mid-1785-url",
        )
        assert err is None and len(rows) == 1
        assert rows[0]["link"] == url

    @pytest.mark.asyncio
    async def test_stage_text_outcome_http_job_link_scrape_link_and_title(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import STAGE_METEORITE_CONFIG

        db = sqlite_in_memory
        cid = "cand-1785-stage"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "L"})
        outcome = STAGE_METEORITE_CONFIG["text_source_ref_outcomes"][0]
        url = "https://example.com/jobs/1"

        async def _classify(*_a, **_k):
            return {
                "success": True,
                "outcome": outcome,
                "jobs": [{
                    "jd_text": "JD " + ("t" * 40),
                    "job_link": url,
                    "job_title": "Senior Widget Engineer",
                    "from_email": "recruiter@co.com",
                    "to_email": "me@ex.com",
                    "sent_at": "2026-09-17T18:05:00+00:00",
                }],
                "error": None,
                "batch_id": "b-1785",
            }

        monkeypatch.setattr(meteorite_mod, "_classify_stage_blob", _classify)
        out = await meteorite_mod.stage_meteorite(
            cid, '<a href="https://example.com/jobs/1">Senior Widget Engineer</a>',
            source_kind="email", source_id="mid-1785-stage",
        )
        assert out.get("error") is None
        rows = db.list_meteorites_by_source("email", "mid-1785-stage")
        assert len(rows) == 1
        assert rows[0]["link"] == url
        assert rows[0]["state"] == "SCRAPE_LINK"
        assert rows[0]["job_title"] == "Senior Widget Engineer"

    @pytest.mark.asyncio
    async def test_run_stage_text_outcome_http_link_to_scrape_link(
        self, sqlite_in_memory
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-1785-run"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "R"})
        url = "https://example.com/jobs/1"
        row_id = _insert_meteorite_row(
            db,
            cid,
            classify_outcome="single_jd_no_link",
            content="JD " + ("z" * 40),
            link=url,
            source_kind="email",
        )
        out = await meteorite_mod.run_stage_meteorite(
            _ingress_task(batch_id="stage-batch-1785-http", candidate_id=cid)
        )
        assert out["total_passed"] == 1
        row = db.get_meteorite(row_id)
        assert row["state"] == "SCRAPE_LINK"
        assert row["link"] == url


# Branches: blank jd_text + http job_link under text outcome must NOT use ingress_blob
# (combo link-only scrap); classic blank+no-link still uses blob (AST-1756) (AST-1796).
@pytest.mark.skipif(
    not hasattr(meteorite_mod, "_map_classify_jobs_to_meteorite_rows"),
    reason="AST-1796 map helper not on this publish tip",
)
class TestAst1796ComboBlankJdTextHttpJobLinkSkipsIngressBlob:
    """AST-1796 bug-repro: link-only jobs item under text outcome must not swallow the email blob."""

    _BLOB = (
        "Here is the full JD for role A.\n\n"
        "Also open: https://example.com/jobs/other"
    )

    def test_blank_jd_text_with_http_job_link_skips_ingress_blob(self) -> None:
        # Pre-fix: AST-1756 fills content from ingress_blob before AST-1785 sets link —
        # link-only combo items become full-email scraps. Fixed: empty content + http link.
        url = "https://example.com/jobs/other"
        rows, err = meteorite_mod._map_classify_jobs_to_meteorite_rows(
            "multi_jd_inline",
            [{
                "jd_text": "",
                "job_link": url,
                "from_email": "recruiter@co.com",
                "to_email": "me@ex.com",
                "sent_at": "2026-09-17T18:05:00+00:00",
            }],
            candidate_id="cand-1796",
            source_kind="email",
            source_id="mid-1796",
            ingress_blob=self._BLOB,
            timezone_key="America/New_York",
        )
        assert err is None and len(rows) == 1
        assert rows[0]["link"] == url
        content = (rows[0].get("content") or "").strip()
        assert content != self._BLOB.strip()
        assert content == ""


# Branches: classify-fail fallthrough + map-error both warn once when the ERROR-row
# insert succeeds; a failed ERROR-row insert keeps its own single log (no extra warn).
class TestAst1617StageErrorWarns:
    """[bug-repro] AST-1617: stage errors that callers count must emit an always-on WARNING."""

    @staticmethod
    def _stage_common(monkeypatch: pytest.MonkeyPatch, *, insert=None) -> None:
        monkeypatch.setattr(
            meteorite_mod, "get_candidate", lambda _cid: {"astral_candidate_id": "c1617"}
        )
        monkeypatch.setattr(
            meteorite_mod, "_insert_stage_rows", insert or (lambda _rows: ([101], None))
        )
        monkeypatch.setattr(meteorite_mod, "_candidate_contact_timezone", lambda _cid: None)

    @staticmethod
    def _warns_for(caplog: pytest.LogCaptureFixture, sid: str) -> list:
        import logging

        return [
            r
            for r in caplog.records
            if r.name == "src.core.meteorite"
            and r.levelno >= logging.WARNING
            and sid in r.getMessage()
        ]

    @pytest.mark.asyncio
    async def test_classify_fail_warns_once(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        self._stage_common(monkeypatch)

        async def _classify_fail(*_a, **_k):
            return {"success": False, "outcome": "", "jobs": [], "error": "llm timeout", "batch_id": "b1"}

        monkeypatch.setattr(meteorite_mod, "_classify_stage_blob", _classify_fail)
        with caplog.at_level(logging.WARNING, logger="src.core.meteorite"):
            out = await meteorite_mod.stage_meteorite(
                "c1617", "blob", source_kind="email", source_id="mid-1617-a"
            )
        assert out["error"] == "llm timeout"
        warns = self._warns_for(caplog, "mid-1617-a")
        assert len(warns) == 1
        msg = warns[0].getMessage()
        assert "c1617" in msg and "email" in msg and "llm timeout" in msg

    @pytest.mark.asyncio
    async def test_map_error_warns_once(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        from src.utils.config import STAGE_METEORITE_CONFIG

        self._stage_common(monkeypatch)
        landable = STAGE_METEORITE_CONFIG["text_source_ref_outcomes"][0]

        async def _classify_ok(*_a, **_k):
            return {"success": True, "outcome": landable, "jobs": [{}], "error": None, "batch_id": "b2"}

        monkeypatch.setattr(meteorite_mod, "_classify_stage_blob", _classify_ok)
        monkeypatch.setattr(
            meteorite_mod,
            "_map_classify_jobs_to_meteorite_rows",
            lambda *_a, **_k: ([], "jobs[0] missing content"),
        )
        with caplog.at_level(logging.WARNING, logger="src.core.meteorite"):
            out = await meteorite_mod.stage_meteorite(
                "c1617", "blob", source_kind="email", source_id="mid-1617-b"
            )
        assert out["error"] == "jobs[0] missing content"
        warns = self._warns_for(caplog, "mid-1617-b")
        assert len(warns) == 1
        msg = warns[0].getMessage()
        assert "c1617" in msg and "email" in msg and "missing content" in msg

    @pytest.mark.asyncio
    async def test_error_row_insert_failure_logs_once_no_extra_warn(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        def _insert_boom(_rows):
            raise RuntimeError("insert boom")

        self._stage_common(monkeypatch, insert=_insert_boom)

        async def _classify_fail(*_a, **_k):
            return {"success": False, "outcome": "", "jobs": [], "error": "llm timeout", "batch_id": "b3"}

        monkeypatch.setattr(meteorite_mod, "_classify_stage_blob", _classify_fail)
        with caplog.at_level(logging.WARNING, logger="src.core.meteorite"):
            out = await meteorite_mod.stage_meteorite(
                "c1617", "blob", source_kind="email", source_id="mid-1617-c"
            )
        assert out["error"] == "llm timeout"
        warns = self._warns_for(caplog, "mid-1617-c")
        assert len(warns) == 1
        assert warns[0].levelno == logging.ERROR


# Branches: ctx key map forwarded / absent → do_task loads by candidate id (AST-1879).
class TestAst1879ClassifyKeyMapHandOff:
    """AST-1879: _classify_stage_blob forwards candidate_api_keys to do_task ctx."""

    async def _run(self, monkeypatch: pytest.MonkeyPatch, ctx: object) -> dict:
        import src.core.agent as agent_mod

        seen: dict = {}

        async def _do_task(**kwargs):
            seen.update(kwargs)
            return {"success": False, "error": "stop"}

        monkeypatch.setattr(agent_mod, "do_task", _do_task)
        await meteorite_mod._classify_stage_blob(
            "cand-1879", "blob", source_kind="email", source_id="msg-1879", ctx=ctx
        )
        return seen["ctx"]

    @pytest.mark.asyncio
    async def test_forwards_key_map_from_ctx(self, monkeypatch: pytest.MonkeyPatch) -> None:
        keys = {"kimi": "sk-kimi"}
        task_ctx = await self._run(
            monkeypatch, {"candidate_data": {"a": 1}, "candidate_api_keys": keys}
        )
        assert task_ctx["candidate_api_keys"] == keys
        assert task_ctx["astral_candidate_id"] == "cand-1879"
        assert "candidate_api_key" not in task_ctx

    @pytest.mark.asyncio
    @pytest.mark.parametrize("ctx", [None, {"astral_candidate_id": "cand-1879"}])
    async def test_no_key_map_in_ctx_leaves_it_off(self, monkeypatch: pytest.MonkeyPatch, ctx: object) -> None:
        # do_task then loads the map by candidate id (_candidate_server_key).
        task_ctx = await self._run(monkeypatch, ctx)
        assert "candidate_api_keys" not in task_ctx
        assert task_ctx["astral_candidate_id"] == "cand-1879"


# AST-1988: _hold_log_batch stamps batch + candidate as a token pair, or no-ops under a parent batch.
# Branches: no parent → (batch_tok, cand_tok); parent batch set → None, parent ids kept; blank cid → candidate None;
# _classify_stage_blob caller resets both tokens in finally.
class TestAst1988HoldLogBatchPairing:
    """log_candidate_id rides _hold_log_batch (AST-1988 AC 4); #14 is the bug-repro."""

    @staticmethod
    def _ids() -> tuple:
        from src.utils.logging import log_batch_id, log_candidate_id

        return log_batch_id.get(), log_candidate_id.get()

    @staticmethod
    def _start(batch=None, cand=None) -> tuple:
        # Pin a known start state so a leak from another test can't green these.
        from src.utils.logging import log_batch_id, log_candidate_id

        return log_batch_id.set(batch), log_candidate_id.set(cand)

    @staticmethod
    def _restore(tokens: tuple) -> None:
        from src.utils.logging import log_batch_id, log_candidate_id

        log_candidate_id.reset(tokens[1])
        log_batch_id.reset(tokens[0])

    def test_hold_sets_both_and_returns_token_pair(self) -> None:
        # bug-repro: pre-fix _hold_log_batch takes one arg (TypeError) and returns a single token.
        from src.utils.logging import log_batch_id, log_candidate_id

        start = self._start()
        try:
            tok = meteorite_mod._hold_log_batch("b-1988", "cand-1988")
            assert isinstance(tok, tuple) and len(tok) == 2
            assert self._ids() == ("b-1988", "cand-1988")
            log_batch_id.reset(tok[0])
            log_candidate_id.reset(tok[1])
            assert self._ids() == (None, None)
        finally:
            self._restore(start)

    def test_hold_noop_under_parent_batch(self) -> None:
        start = self._start("parent-b", "parent-c")
        try:
            assert meteorite_mod._hold_log_batch("b-1988", "cand-1988") is None
            assert self._ids() == ("parent-b", "parent-c")
        finally:
            self._restore(start)

    def test_hold_blank_candidate_stamps_none(self) -> None:
        from src.utils.logging import log_batch_id, log_candidate_id

        start = self._start()
        try:
            tok = meteorite_mod._hold_log_batch("b-1988", "")
            assert self._ids() == ("b-1988", None)
            log_batch_id.reset(tok[0])
            log_candidate_id.reset(tok[1])
        finally:
            self._restore(start)

    @pytest.mark.asyncio
    async def test_classify_stage_blob_stamps_and_releases(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Same do_task patch as TestAst1879ClassifyKeyMapHandOff._run, capturing ids mid-run.
        import src.core.agent as agent_mod

        seen: list = []

        async def _do_task(**kwargs):
            seen.append(self._ids())
            return {"success": False, "error": "stop"}

        monkeypatch.setattr(agent_mod, "do_task", _do_task)
        start = self._start()
        try:
            await meteorite_mod._classify_stage_blob(
                "cand-1988", "blob", source_kind="email", source_id="msg-1988"
            )
            assert len(seen) == 1
            batch, cand = seen[0]
            assert batch.startswith(meteorite_mod.STAGE_METEORITE_CONFIG["task_key"] + "-stage-")
            assert cand == "cand-1988"
            assert self._ids() == (None, None)
        finally:
            self._restore(start)


# AST-2034: insert_slack_meteorite — raw Slack blob at NEW, unclassified (parent AC1/AC2 row shape
# via direct call; mention/command strip + link unwrap are sibling AST-2035's job, not tested here).
# Branches: ok + anchor stamped / ok no anchor; misses (cid, payload, source_id) insert nothing;
# insert raises → soft-fail; anchor stamp raises → still ok.
class TestAst2034InsertSlackMeteorite:
    URL = "http://www.dice.com/jobs/13234abcd"

    @staticmethod
    def _last_row(db) -> dict:
        rows = db.list_meteorites_by_source("slack", "C1:1700000000.000100")
        assert len(rows) == 1
        return rows[0]

    def test_link_payload_lands_raw_at_new(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        out = meteorite_mod.insert_slack_meteorite(
            "cand-2034", self.URL, source_id="C1:1700000000.000100", thread_ts="1700000000.000100",
        )
        assert out["ok"] is True and out["error"] is None
        row = self._last_row(db)
        assert row["id"] == out["meteorite_id"]
        assert (row["candidate_id"], row["state"], row["source_kind"]) == ("cand-2034", "NEW", "slack")
        assert row["classify_outcome"] is None
        assert row["content"] == self.URL
        assert row["link"] is None
        assert row["estelle_thread_ts"] == "1700000000.000100"

    def test_text_payload_lands_one_row_trimmed_interior_kept(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        jd = "Senior Engineer\nAcme Corp\n\nResponsibilities:\n- build things"
        out = meteorite_mod.insert_slack_meteorite(
            "cand-2034", f"  \n{jd}\n  ", source_id="C1:1700000000.000100",
        )
        assert out["ok"] is True
        row = self._last_row(db)
        assert row["state"] == "NEW" and row["classify_outcome"] is None
        assert row["content"] == jd
        # No anchor passed → nothing stamped.
        assert not row.get("estelle_thread_ts")

    @pytest.mark.parametrize(
        ("cid", "payload", "sid", "why"),
        [
            ("", "blob", "C1:1", "candidate_id is required"),
            ("cand-2034", "   ", "C1:1", "payload is required"),
            ("cand-2034", None, "C1:1", "payload is required"),
            ("cand-2034", "blob", " ", "source_id is required"),
        ],
    )
    def test_validation_miss_inserts_nothing(self, sqlite_in_memory, cid, payload, sid, why) -> None:
        db = sqlite_in_memory
        out = meteorite_mod.insert_slack_meteorite(cid, payload, source_id=sid)
        assert out == {"ok": False, "meteorite_id": None, "error": why}
        assert db.list_meteorites_by_source("slack", sid.strip() or "C1:1") == []

    def test_insert_raises_soft_fails(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        def _boom(_rows):
            raise RuntimeError("db locked")

        monkeypatch.setattr(meteorite_mod, "_insert_stage_rows", _boom)
        out = meteorite_mod.insert_slack_meteorite("cand-2034", "blob", source_id="C1:1")
        assert out == {"ok": False, "meteorite_id": None, "error": "db locked"}

    def test_anchor_stamp_failure_still_ok(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory

        def _boom(*_a, **_k):
            raise RuntimeError("update failed")

        monkeypatch.setattr(meteorite_mod, "update_meteorite", _boom)
        out = meteorite_mod.insert_slack_meteorite(
            "cand-2034", "blob", source_id="C1:1700000000.000100", thread_ts="1700000000.000100",
        )
        # Row is saved; Contact must not tell the candidate nothing was saved.
        assert out["ok"] is True
        assert self._last_row(db)["state"] == "NEW"


# AST-2034: run_stage_meteorite Ruth-classifies unclassified NEW rows (parent AC8/AC9/AC10).
# Branches: insert sanitized / URL query kept / markup-only → payload miss; apply_paste drops script,
# decodes entity-encoded markup, keeps plain line shaping; helper table (AST-2061). The double-encoded
# plain-text residual is accepted and deliberately not pinned.
class TestAst2061ContactSanitize:
    SID = "C1:1700000000.000200"

    @staticmethod
    def _bot_blocked_row(db, cid: str) -> int:
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})
        return _insert_meteorite_row(db, cid, state="BOT_BLOCKED_SCRAPE_METEORITE", link="https://blocked.example/j")

    def test_insert_slack_meteorite_stores_sanitized_content(self, sqlite_in_memory) -> None:
        # [bug-repro] AST-2061: Contact markup / entity-encoded script never reaches stored content.
        db = sqlite_in_memory
        payload = "<img src=x onerror=alert(1)>Senior Eng &lt;script&gt;alert(1)&lt;/script&gt;"
        out = meteorite_mod.insert_slack_meteorite("cand-2061", payload, source_id=self.SID)
        assert out["ok"] is True
        rows = db.list_meteorites_by_source("slack", self.SID)
        assert len(rows) == 1
        assert rows[0]["content"] == "Senior Eng"
        assert rows[0]["state"] == "NEW"
        assert rows[0]["classify_outcome"] is None

    def test_insert_slack_meteorite_keeps_url_query(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        out = meteorite_mod.insert_slack_meteorite(
            "cand-2061", "https://x.io/job?id=1&amp;src=slack", source_id=self.SID
        )
        assert out["ok"] is True
        assert db.list_meteorites_by_source("slack", self.SID)[0]["content"] == "https://x.io/job?id=1&src=slack"

    def test_insert_markup_only_payload_is_required_miss(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        out = meteorite_mod.insert_slack_meteorite("cand-2061", "<script>alert(1)</script>", source_id=self.SID)
        assert out == {"ok": False, "meteorite_id": None, "error": "payload is required"}
        assert db.list_meteorites_by_source("slack", self.SID) == []

    def test_apply_paste_drops_script_content(self, sqlite_in_memory) -> None:
        # [bug-repro] AST-2061: the old regex tag strip kept script text ("Senior Eng alert(1)").
        db = sqlite_in_memory
        row_id = self._bot_blocked_row(db, "cand-2061-script")
        out = meteorite_mod.apply_paste(row_id, "<p>Senior Eng</p><script>alert(1)</script>")
        assert out["ok"] is True
        assert db.get_meteorite(row_id)["content"] == "Senior Eng"

    def test_apply_paste_entity_encoded_plain_text(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        row_id = self._bot_blocked_row(db, "cand-2061-entity")
        out = meteorite_mod.apply_paste(row_id, "&lt;script&gt;alert(1)&lt;/script&gt;Senior Eng")
        assert out["ok"] is True
        assert db.get_meteorite(row_id)["content"] == "Senior Eng"

    def test_apply_paste_plain_lines_unchanged(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        row_id = self._bot_blocked_row(db, "cand-2061-lines")
        out = meteorite_mod.apply_paste(row_id, "line1\n\n  line2  ")
        assert out["ok"] is True
        assert db.get_meteorite(row_id)["content"] == "line1\n\nline2"

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("https://x.io/job?id=1&amp;src=slack", "https://x.io/job?id=1&src=slack"),
            ("&lt;script&gt;alert(1)&lt;/script&gt;Senior Eng", "Senior Eng"),
            ("<b>Senior</b> Eng <img src=x onerror=alert(1)> AT&amp;T", "Senior Eng  AT&T"),
            ("<@U123> salary 1 < 2", "<@U123> salary 1 < 2"),
            ("line1\n\nline2  <!-- c -->", "line1\n\nline2"),
            (None, ""),
        ],
    )
    def test_sanitize_contact_text_table(self, raw, expected) -> None:
        assert meteorite_mod.sanitize_contact_text(raw) == expected


# Branches: link_list → SCRAPE_LINK; single_jd_no_link → CHECK_UNIQUE; skip → NOT_A_JOB (failed);
# do_task fail → ERROR_STAGE_METEORITE (TestAst1560RunStageMeteorite::test_missing_classify_outcome_…);
# map fail → ERROR_STAGE_METEORITE with outcome kept; candidate missing → ERROR_STAGE_METEORITE;
# multi_jd_inline 3 jobs → original routed + 2 unclaimed classified NEW siblings;
# classified row → zero do_task calls; classify agent_data batch = claim id; claim released.
class TestAst2034StageHopClassify:
    URL = "http://www.dice.com/jobs/13234abcd"
    SID = "C1:1700000000.000100"

    @staticmethod
    def _patch_ruth(monkeypatch: pytest.MonkeyPatch, outcome: str, jobs: list) -> list:
        """Patch do_task with a Ruth reply; returns call log of (kwargs, log_batch_id at call)."""
        import src.core.agent as agent_mod
        from src.utils.logging import log_batch_id

        calls: list = []

        async def _do_task(**kwargs):
            calls.append((kwargs, log_batch_id.get()))
            return {"success": True, "parsed_response": {"outcome": outcome, "jobs": jobs}}

        monkeypatch.setattr(agent_mod, "do_task", _do_task)
        return calls

    def _seed(self, db, cid: str, payload: str, *, save_candidate: bool = True) -> int:
        if save_candidate:
            db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "S"})
        out = meteorite_mod.insert_slack_meteorite(cid, payload, source_id=self.SID)
        assert out["ok"] is True
        return out["meteorite_id"]

    @staticmethod
    async def _run(cid: str, batch_id: str) -> dict:
        return await meteorite_mod.run_stage_meteorite(_ingress_task(batch_id=batch_id, candidate_id=cid))

    @pytest.mark.asyncio
    async def test_link_list_routes_to_scrape_link(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        row_id = self._seed(db, "cand-2034-link", self.URL)
        calls = self._patch_ruth(monkeypatch, "link_list", [{"job_link": self.URL, "job_title": "SWE"}])
        out = await self._run("cand-2034-link", "b-2034-link")
        assert len(calls) == 1
        assert out["total_passed"] == 1 and out["total_errors"] == 0
        row = db.get_meteorite(row_id)
        assert row["state"] == "SCRAPE_LINK"
        assert row["link"] == self.URL
        assert row["classify_outcome"] == "link_list"
        assert row["job_title"] == "SWE"

    @pytest.mark.asyncio
    async def test_single_jd_no_link_routes_to_check_unique(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        jd = "Senior Engineer at Acme\n" + ("x" * 60)
        row_id = self._seed(db, "cand-2034-text", jd)
        self._patch_ruth(monkeypatch, "single_jd_no_link", [{"jd_text": jd, "employer_name": "Acme"}])
        out = await self._run("cand-2034-text", "b-2034-text")
        assert out["total_passed"] == 1
        row = db.get_meteorite(row_id)
        # Slack text rows carry no breadcrumb requirement (that gate is email-only).
        assert row["state"] == "CHECK_UNIQUE"
        assert row["content"] == jd
        assert row["employer_name"] == "Acme"

    @pytest.mark.asyncio
    async def test_not_job_content_to_not_a_job(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        row_id = self._seed(db, "cand-2034-skip", "lol hi estelle")
        self._patch_ruth(monkeypatch, "not_job_content", [])
        out = await self._run("cand-2034-skip", "b-2034-skip")
        # AST-1742 / AST-1751: skip counts as failed, not error.
        assert (out["total_failed"], out["total_errors"], out["total_passed"]) == (1, 0, 0)
        row = db.get_meteorite(row_id)
        assert row["state"] == "NOT_A_JOB"
        assert row["classify_outcome"] == "not_job_content"

    @pytest.mark.asyncio
    async def test_map_failure_to_new_email_error_keeps_outcome(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        row_id = self._seed(db, "cand-2034-map", "www.dice.com/jobs/x")
        # link_list with a non-http job_link → _map_classify_jobs_to_meteorite_rows error.
        self._patch_ruth(monkeypatch, "link_list", [{"job_link": "www.dice.com/jobs/x"}])
        out = await self._run("cand-2034-map", "b-2034-map")
        assert (out["total_errors"], out["total_failed"]) == (1, 0)
        row = db.get_meteorite(row_id)
        assert row["state"] == "ERROR_STAGE_METEORITE"
        assert row["error"] == "url scrap missing http(s) job_link"
        assert row["classify_outcome"] == "link_list"

    @pytest.mark.asyncio
    async def test_candidate_missing_to_new_email_error_no_ruth(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        row_id = self._seed(db, "cand-2034-ghost", "blob", save_candidate=False)
        calls = self._patch_ruth(monkeypatch, "single_jd_no_link", [])
        out = await self._run("cand-2034-ghost", "b-2034-ghost")
        assert calls == []
        assert out["total_errors"] == 1
        row = db.get_meteorite(row_id)
        assert row["state"] == "ERROR_STAGE_METEORITE"
        assert "candidate not found" in row["error"]

    @pytest.mark.asyncio
    async def test_multi_jd_inline_three_jobs_fans_out_two_siblings(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        batch_id = "b-2034-multi"
        row_id = self._seed(db, "cand-2034-multi", "three postings pasted")
        jobs = [{"jd_text": f"Role {n} " + ("y" * 40), "job_title": f"Role {n}"} for n in (1, 2, 3)]
        self._patch_ruth(monkeypatch, "multi_jd_inline", jobs)
        out = await self._run("cand-2034-multi", batch_id)
        # Counters are per claimed row: one row claimed, one routed.
        assert (out["total_processed"], out["total_passed"]) == (1, 1)
        rows = {r["id"]: r for r in db.list_meteorites_by_source("slack", self.SID)}
        assert len(rows) == 3
        assert rows.pop(row_id)["state"] == "CHECK_UNIQUE"
        siblings = sorted(rows.values(), key=lambda r: r["id"])
        assert [s["job_title"] for s in siblings] == ["Role 2", "Role 3"]
        for s in siblings:
            assert s["state"] == "NEW"
            assert s["classify_outcome"] == "multi_jd_inline"
            assert s["source_kind"] == "slack"
            # Not claimed by this hop; next stage tick routes them via the classified branch.
            assert s.get("batch_id") is None

    @pytest.mark.asyncio
    async def test_classified_row_never_calls_ruth(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        # Parent AC9: same fixture shape as TestAst1560RunStageMeteorite::test_url_outcome_to_scrape_link.
        db = sqlite_in_memory
        cid = "cand-2034-classified"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "C"})
        row_id = _insert_meteorite_row(
            db, cid, classify_outcome="single_jd_with_more", link="https://jobs.example.com/role",
        )
        calls = self._patch_ruth(monkeypatch, "not_job_content", [])
        out = await self._run(cid, "b-2034-classified")
        assert calls == []
        assert out["total_passed"] == 1
        assert db.get_meteorite(row_id)["state"] == "SCRAPE_LINK"

    @pytest.mark.asyncio
    async def test_classify_batch_joins_claim_and_claim_released(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Parent AC10: do_task stamps agent_data.batch_id from log_batch_id; with no parent
        # batch set, it must be the claim id — not a self-minted stage_meteorite-stage-… id.
        from src.utils.logging import log_batch_id

        db = sqlite_in_memory
        batch_id = "b-2034-join"
        cid = "cand-2034-join"
        a = self._seed(db, cid, self.URL)
        b = self._seed(db, cid, "lol", save_candidate=False)
        calls = self._patch_ruth(monkeypatch, "link_list", [{"job_link": self.URL}])
        tok = log_batch_id.set(None)
        try:
            await self._run(cid, batch_id)
        finally:
            log_batch_id.reset(tok)
        assert len(calls) == 2
        task_key = meteorite_mod.STAGE_METEORITE_CONFIG["task_key"]
        for kwargs, stamped in calls:
            assert stamped == batch_id
            assert kwargs["index"] == f"{task_key}_batch_{batch_id}"
        assert db.get_meteorite_batch(batch_id) == []
        for mid in (a, b):
            assert db.get_meteorite(mid).get("batch_id") is None
