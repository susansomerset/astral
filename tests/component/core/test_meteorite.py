"""Component tests for src/core/meteorite.py (AST-1041)."""

from __future__ import annotations

import importlib.util
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import meteorite as meteorite_mod
from src.utils.config import (
    METEORITE_BOT_BLOCKED_NOTIFY_CONFIG,
    METEORITE_CONFIG,
    METEORITE_EMAIL_MAILBOX_CONFIG,
    METEORITE_INGRESS_DISPATCH_CONFIG,
    METEORITE_MONITORING_CONFIG,
    METEORITE_RETENTION_CONFIG,
)


# Branches: empty id; insert once; idempotent no-op.
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
            "src.core.consult.enrich_meteorite_land_packet", _enrich
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
            "src.core.consult.enrich_meteorite_land_packet", _enrich
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
            "src.core.consult.enrich_meteorite_land_packet", _enrich
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
            "src.core.consult.enrich_meteorite_land_packet", _enrich
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
            [{"candidate_id": cid, "source_kind": "paste", "source_id": "skip-seed", "content": "old"}]
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
            "src.core.consult.enrich_meteorite_land_packet", _enrich
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
            "src.core.consult.enrich_meteorite_land_packet", _enrich
        )
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
            [{"candidate_id": cid, "source_kind": "email", "source_id": "m1702", "content": "jd"}]
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
            [{"candidate_id": cid, "source_kind": "paste", "source_id": "skip2", "content": "x"}]
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

        monkeypatch.setattr("src.core.consult.enrich_meteorite_land_packet", _enrich)
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

        monkeypatch.setattr("src.core.consult.enrich_meteorite_land_packet", _enrich)
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

        monkeypatch.setattr("src.core.consult.enrich_meteorite_land_packet", _enrich)
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
            "astral_job_id",  # AST-1690 retention skip fixtures
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
            _ingress_task(batch_id="stage-batch-nobread")
        )
        assert out["total_errors"] == 1
        row = db.get_meteorite(row_id)
        assert row["state"] == "SCRAPE_ERROR"
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
        # AST-1703: email text rows require non-http breadcrumb on link before READY.
        crumb = "From:a@x.com 9/17 14:05 Eastern To:b@y.com"
        row_id = _insert_meteorite_row(
            db,
            cid,
            classify_outcome="single_jd_no_link",
            content="Full JD body " + ("x" * 40),
            link=crumb,
        )
        batch_id = "stage-batch-text"
        out = await meteorite_mod.run_stage_meteorite(_ingress_task(batch_id=batch_id))
        assert out["total_passed"] == 1
        row = db.get_meteorite(row_id)
        assert row["state"] == "READY"
        assert row["link"] == crumb

    @pytest.mark.asyncio
    async def test_missing_classify_outcome_errors_with_monitoring(
        self, sqlite_in_memory, caplog
    ) -> None:
        import logging

        db = sqlite_in_memory
        cid = "cand-stg-miss"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "M"})
        row_id = _insert_meteorite_row(db, cid)
        with caplog.at_level(logging.WARNING):
            out = await meteorite_mod.run_stage_meteorite(
                _ingress_task(batch_id="stage-batch-miss")
            )
        assert out["total_errors"] == 1
        assert db.get_meteorite(row_id)["state"] == "SCRAPE_ERROR"
        assert any("missing classify_outcome" in r.message for r in caplog.records)


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
        assert db.get_meteorite(bad_id)["state"] == "SCRAPE_ERROR"
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
        assert db.get_meteorite(row_id)["state"] == "SCRAPE_ERROR"


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


def _backdate_meteorite_state_changed(db, row_id: int, iso: str) -> None:
    conn = db._get_connection()
    try:
        conn.execute(
            "UPDATE meteorite SET state_changed_at = ? WHERE id = ?",
            (iso, row_id),
        )
        conn.commit()
    finally:
        conn.close()


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "run_meteorite_retention"),
    reason="AST-1562 retention runner not on this publish tip",
)
class TestAst1562RunMeteoriteRetention:
    """AST-1562: purge old LANDED; info-list stale rows; module retired."""

    def test_meteorite_email_module_deleted(self) -> None:
        assert importlib.util.find_spec("src.core.meteorite_email") is None

    @pytest.mark.asyncio
    async def test_purges_old_landed_rows(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        db = sqlite_in_memory
        cid = "cand-retention-purge"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Purge"})
        row_id = _insert_meteorite_row(db, cid, state="LANDED")
        old = (datetime.now(timezone.utc) - timedelta(days=120)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        _backdate_meteorite_state_changed(db, row_id, old)
        out = await meteorite_mod.run_meteorite_retention(
            {"batch_size": METEORITE_RETENTION_CONFIG["batch_size"]},
            debug=False,
        )
        assert out["total_processed"] >= 1
        assert out["total_passed"] >= 1
        assert db.get_meteorite(row_id) is None

    @pytest.mark.asyncio
    async def test_stale_rows_info_logged_not_deleted(
        self, sqlite_in_memory, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        db = sqlite_in_memory
        cid = "cand-retention-stale"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Stale"})
        row_id = _insert_meteorite_row(db, cid, state="SCRAPE_ERROR", link="https://jobs.example/e")
        old = (datetime.now(timezone.utc) - timedelta(days=30)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        _backdate_meteorite_state_changed(db, row_id, old)
        with caplog.at_level(logging.WARNING, logger="src.core.meteorite"):
            out = await meteorite_mod.run_meteorite_retention({}, debug=False)
        assert out["total_processed"] >= 1
        assert out["total_passed"] >= 1
        assert db.get_meteorite(row_id) is not None
        assert any("still SCRAPE_ERROR" in r.getMessage() for r in caplog.records)
        assert any(str(row_id) in r.getMessage() for r in caplog.records)

    @pytest.mark.asyncio
    async def test_fresh_landed_not_purged(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-retention-fresh"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Fresh"})
        row_id = _insert_meteorite_row(db, cid, state="LANDED")
        out = await meteorite_mod.run_meteorite_retention({}, debug=False)
        assert out["total_processed"] == 0
        assert db.get_meteorite(row_id) is not None


@pytest.mark.skipif(
    not hasattr(meteorite_mod, "run_meteorite_retention"),
    reason="AST-1562 retention runner not on this publish tip",
)
class TestAst1690RetentionJobLinkedSkip:
    """AST-1690: keep age-eligible LANDED when astral_job_id still hits a job."""

    def _old_iso(self) -> str:
        return (datetime.now(timezone.utc) - timedelta(days=120)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

    @pytest.mark.asyncio
    async def test_keeps_old_landed_when_job_exists(self, sqlite_in_memory) -> None:
        # AC7 — job-linked LANDED past landed_purge_days must survive one retention run.
        db = sqlite_in_memory
        cid = "cand-ret-keep"
        jid = "job-ret-keep-1"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Keep"})
        db.save_company("co-ret-keep", state="IGNORE", candidate_id=cid)
        db.save_job(jid, company="co-ret-keep", state="RECOMMENDED")
        row_id = _insert_meteorite_row(
            db, cid, state="LANDED", astral_job_id=jid
        )
        _backdate_meteorite_state_changed(db, row_id, self._old_iso())
        out = await meteorite_mod.run_meteorite_retention({}, debug=False)
        assert db.get_meteorite(row_id) is not None
        assert out["total_processed"] == 0
        assert out["total_passed"] == 0

    @pytest.mark.asyncio
    async def test_purges_old_landed_when_job_missing(self, sqlite_in_memory) -> None:
        # AC8 — orphan astral_job_id (no job row) stays age-purge eligible.
        db = sqlite_in_memory
        cid = "cand-ret-orphan"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Orphan"})
        row_id = _insert_meteorite_row(
            db, cid, state="LANDED", astral_job_id="job-ret-missing-xyz"
        )
        _backdate_meteorite_state_changed(db, row_id, self._old_iso())
        out = await meteorite_mod.run_meteorite_retention({}, debug=False)
        assert db.get_meteorite(row_id) is None
        assert out["total_processed"] >= 1
        assert out["total_passed"] >= 1

    @pytest.mark.asyncio
    async def test_purges_old_landed_blank_astral_job_id(
        self, sqlite_in_memory
    ) -> None:
        # AC8 — whitespace-only astral_job_id strips to empty → purge like null.
        db = sqlite_in_memory
        cid = "cand-ret-blank"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Blank"})
        row_id = _insert_meteorite_row(
            db, cid, state="LANDED", astral_job_id="   "
        )
        _backdate_meteorite_state_changed(db, row_id, self._old_iso())
        out = await meteorite_mod.run_meteorite_retention({}, debug=False)
        assert db.get_meteorite(row_id) is None
        assert out["total_processed"] >= 1

    @pytest.mark.asyncio
    async def test_mixed_batch_keeps_linked_purges_unlinked(
        self, sqlite_in_memory
    ) -> None:
        # One run: linked keep + null-link purge (partition loop).
        db = sqlite_in_memory
        cid = "cand-ret-mix"
        jid = "job-ret-mix-1"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Mix"})
        db.save_company("co-ret-mix", state="IGNORE", candidate_id=cid)
        db.save_job(jid, company="co-ret-mix", state="RECOMMENDED")
        keep_id = _insert_meteorite_row(
            db, cid, state="LANDED", astral_job_id=jid, source_id="mid-keep"
        )
        purge_id = _insert_meteorite_row(
            db, cid, state="LANDED", source_id="mid-purge"
        )
        old = self._old_iso()
        _backdate_meteorite_state_changed(db, keep_id, old)
        _backdate_meteorite_state_changed(db, purge_id, old)
        out = await meteorite_mod.run_meteorite_retention({}, debug=False)
        assert db.get_meteorite(keep_id) is not None
        assert db.get_meteorite(purge_id) is None
        assert out["total_processed"] >= 1
        assert out["total_passed"] >= 1


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

@pytest.mark.skipif(
    "electronic_contact_column" not in METEORITE_CONFIG
    or not hasattr(meteorite_mod, "_soft_persist_meteorite_electronic_contact"),
    reason="AST-1689 electronic_contact map/persist not on this publish tip",
)
class TestAst1689ElectronicContactMapPersist:
    """AST-1689: map Ruth contact → row; soft-fail; BOT_BLOCKED preserve; no job_data."""

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
                        "electronic_contact": "hiring@example.com",
                    }
                ],
                "error": None,
                "batch_id": "b",
            }

        monkeypatch.setattr("src.core.consult.invoke_stage_meteorite", _invoke)
        out = await meteorite_mod.check_inbox({"candidate_id": cid}, debug=False)
        assert out["total_passed"] == 1
        rows = db.list_meteorites_by_source("email", mid)
        assert len(rows) == 1
        assert rows[0][col] == "hiring@example.com"
        assert rows[0]["state"] == "NEW"

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
                "jobs": [{"jd_text": "Full JD body " + ("y" * 40)}],
                "error": None,
                "batch_id": "b",
            }

        monkeypatch.setattr("src.core.consult.invoke_stage_meteorite", _invoke)
        out = await meteorite_mod.check_inbox({"candidate_id": cid}, debug=False)
        assert out["total_passed"] == 1
        row = db.list_meteorites_by_source("email", mid)[0]
        assert row["state"] == "NEW"
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
                        "electronic_contact": "soft@example.com",
                    }
                ],
                "error": None,
                "batch_id": "b",
            }

        monkeypatch.setattr("src.core.consult.invoke_stage_meteorite", _invoke)
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
        assert row["state"] == "NEW"
        assert "persist failed" in caplog.text or "contact persist boom" in caplog.text

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
                task_key=METEORITE_INGRESS_DISPATCH_CONFIG["scrape_task_key"],
            )
        )
        assert out["total_passed"] == 1
        row = db.get_meteorite(row_id)
        assert row["state"] == "BOT_BLOCKED"
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
            "src.core.consult.enrich_meteorite_land_packet", AsyncMock()
        )
        out = await meteorite_mod.run_land_meteorite(
            _ingress_task(
                batch_id="land-1689-1",
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
                        "electronic_contact": "debug@example.com",
                    }
                ],
                "error": None,
                "batch_id": "b",
            }

        monkeypatch.setattr("src.core.consult.invoke_stage_meteorite", _invoke)
        with caplog.at_level(logging.DEBUG):
            await meteorite_mod.check_inbox({"candidate_id": cid}, debug=True)
        assert "electronic_contact returned=" in caplog.text
        assert "recorded=" in caplog.text

        caplog.clear()
        mid2 = "msg-1689-nodbg"
        monkeypatch.setattr(
            meteorite_mod, "fetch_candidate_email", lambda _a, debug=False: [_check_inbox_msg(mid2)]
        )
        with caplog.at_level(logging.DEBUG):
            await meteorite_mod.check_inbox({"candidate_id": cid}, debug=False)
        assert "electronic_contact returned=" not in caplog.text

@pytest.mark.skipif(not hasattr(meteorite_mod, "run_land_meteorite"), reason="AST-1560 land runner not on this publish tip")
class TestAst1693RunLandBotBlocked:
    """AST-1693: claim BOT_BLOCKED; contentful land with http job_link; empty stays."""

    @pytest.mark.asyncio
    async def test_contentful_bot_blocked_lands_with_http_link(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        cid = "cand-1693-land"
        link = "https://example.test/job/1"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "L"})
        row_id = _insert_meteorite_row(db, cid, state="BOT_BLOCKED", content="Non-scrape JD " + ("q" * 40), link=link)
        captured: dict = {}
        def _save(_cid, **kwargs):
            captured.update(kwargs)
            return {"outcome": METEORITE_CONFIG["land_outcome_created"], "astral_job_id": "job-1693-land"}
        monkeypatch.setattr(meteorite_mod.tracker, "save_meteorite_job", _save)
        out = await meteorite_mod.run_land_meteorite(_ingress_task(batch_id="land-1693-bb", task_key=METEORITE_INGRESS_DISPATCH_CONFIG["land_task_key"]))
        assert out["total_passed"] == 1
        row = db.get_meteorite(row_id)
        assert row["state"] == "LANDED" and row["astral_job_id"] == "job-1693-land"
        assert captured.get("job_link") == link

    @pytest.mark.asyncio
    async def test_empty_bot_blocked_left_for_estelle(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-1693-empty"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "E"})
        row_id = _insert_meteorite_row(db, cid, state="BOT_BLOCKED", content="", link="https://example.test/job/empty")
        out = await meteorite_mod.run_land_meteorite(_ingress_task(batch_id="land-1693-empty", task_key=METEORITE_INGRESS_DISPATCH_CONFIG["land_task_key"]))
        assert out["total_failed"] == 0 and out["total_errors"] == 0 and out["total_passed"] == 0
        row = db.get_meteorite(row_id)
        assert row["state"] == "BOT_BLOCKED" and not row.get("astral_job_id")


@pytest.mark.skipif(not hasattr(meteorite_mod, "run_notify_meteorite_bot_blocked"), reason="AST-1561 notify runner not on this publish tip")
class TestAst1693NotifySkipsContentful:
    """AST-1693: contentful BOT_BLOCKED belongs to land — notify must not DM."""

    @pytest.mark.asyncio
    async def test_skips_contentful_bot_blocked(self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch) -> None:
        db = sqlite_in_memory
        cid = "cand-1693-notify"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "N", "contact": {"slack_user_id": "U-1693"}})
        row_id = _insert_meteorite_row(db, cid, state="BOT_BLOCKED", content="Paste-ready JD " + ("x" * 40), link="https://jobs.example/blocked-contentful")
        post = MagicMock()
        monkeypatch.setattr(meteorite_mod, "_resolve_slack_dm_channel_for_candidate", lambda _c: "D-1693")
        monkeypatch.setattr("src.core.contact.contact_post_message", post)
        out = await meteorite_mod.run_notify_meteorite_bot_blocked(_notify_task(batch_id="notify-1693-skip"))
        assert out["total_passed"] == 0
        row = db.get_meteorite(row_id)
        assert row["state"] == "BOT_BLOCKED" and not row.get("estelle_notified_at")
        post.assert_not_called()



@pytest.mark.skipif(
    not hasattr(meteorite_mod, "run_meteorite_retention"),
    reason="AST-1562 retention runner not on this publish tip",
)
class TestAst1712NotAJobPurge:
    """AST-1712: NOT_A_JOB is on the scheduled cleanup selection."""

    @pytest.mark.asyncio
    async def test_purges_old_not_a_job(self, sqlite_in_memory) -> None:
        db = sqlite_in_memory
        cid = "cand-retention-not-a-job"
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "Skip"})
        row_id = _insert_meteorite_row(db, cid, state="NOT_A_JOB")
        old = (datetime.now(timezone.utc) - timedelta(days=120)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        _backdate_meteorite_state_changed(db, row_id, old)
        out = await meteorite_mod.run_meteorite_retention({}, debug=False)
        assert db.get_meteorite(row_id) is None
        assert out["total_processed"] >= 1
        assert out["total_passed"] >= 1

