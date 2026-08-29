"""Component tests for src/core/inbox.py (AST-1032 / AST-1047)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import inbox as inbox_mod


def _inbox_html(**overrides: object) -> dict:
    base = {
        "id": "m1",
        "html_body": "<p>" + ("x" * 50) + "</p>",
        "subject": "Engineer",
        "from_address": "ada@ex.com",
    }
    base.update(overrides)
    return base


def _patch_bind_candidate(monkeypatch: pytest.MonkeyPatch, cid: str) -> None:
    monkeypatch.setattr(
        inbox_mod, "get_candidate_id_for_query", MagicMock(return_value=cid)
    )


def _patch_land_enrich(
    monkeypatch: pytest.MonkeyPatch,
    *,
    stem: str = "alice@example.com",
    company_job_id: str = "INBOXJOB1",
) -> None:
    async def _enrich(_cid, scraps, **_k):
        return {
            "success": True,
            "jobs": [{
                "company_job_id": company_job_id,
                "job_title": "Eng",
                "job_link": "",
                "jd_text": "y" * 50,
                "employer_name": "",
                "company_stem": stem,
                "scrap_index": 0,
            }],
        }

    monkeypatch.setattr(
        "src.core.consult.enrich_meteorite_land_packet", _enrich
    )


# Branches: success enrichment; log + re-raise on failure.
class TestListInboxMessages:
    def test_returns_external_rows_with_candidate_match(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        rows = [
            {
                "id": "m1",
                "thread_id": "t1",
                "subject": "Hi",
                "from_address": "a@x",
                "date": "Mon",
                "unread": True,
            }
        ]
        monkeypatch.setattr(inbox_mod, "external_list_inbox_messages", MagicMock(return_value=rows))
        monkeypatch.setattr(
            inbox_mod,
            "get_candidate_id_for_query",
            MagicMock(return_value=None),
        )
        out = inbox_mod.list_inbox_messages()
        assert len(out) == 1
        assert out[0]["id"] == "m1"
        assert out[0]["from_address"] == "a@x"
        assert out[0]["candidate_match"] == {
            "matched": False,
            "astral_candidate_id": None,
        }
        # External row must not be mutated in place.
        assert "candidate_match" not in rows[0]

    def test_logs_and_reraises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "external_list_inbox_messages",
            MagicMock(side_effect=RuntimeError("list fail")),
        )
        warn = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "warning", warn)
        with pytest.raises(RuntimeError, match="list fail"):
            inbox_mod.list_inbox_messages()
        warn.assert_called_once()
        assert "list_inbox_messages failed" in warn.call_args.args[0]


# Branches: success passthrough; log + re-raise on failure (includes message id).
class TestGetMessageHtml:
    def test_returns_external_payload(self, monkeypatch: pytest.MonkeyPatch) -> None:
        payload = {"id": "m1", "html_body": "<p>x</p>"}
        monkeypatch.setattr(inbox_mod, "external_get_message_html", MagicMock(return_value=payload))
        assert inbox_mod.get_message_html("m1") == payload

    def test_logs_and_reraises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "external_get_message_html",
            MagicMock(side_effect=RuntimeError("get fail")),
        )
        warn = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "warning", warn)
        with pytest.raises(RuntimeError, match="get fail"):
            inbox_mod.get_message_html("m9")
        warn.assert_called_once()
        assert "get_message_html failed" in warn.call_args.args[0]
        assert warn.call_args.args[1] == "m9"


# AST-1047: From → candidate_match enrichment.
class TestAst1047InboxFromBind:
    def test_list_enriches_matched_from(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [{"id": "m1", "from_address": "Ada <ada@ex.com>", "subject": "x"}]
        monkeypatch.setattr(inbox_mod, "external_list_inbox_messages", MagicMock(return_value=rows))
        lookup = MagicMock(return_value="cand-ada")
        monkeypatch.setattr(inbox_mod, "get_candidate_id_for_query", lookup)
        out = inbox_mod.list_inbox_messages(debug=False)
        assert out[0]["candidate_match"] == {
            "matched": True,
            "astral_candidate_id": "cand-ada",
        }
        lookup.assert_called_once_with("Ada <ada@ex.com>", debug=False)

    def test_list_debug_emits_style_d(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [{"id": "m9", "from_address": "nobody@ex.com"}]
        monkeypatch.setattr(inbox_mod, "external_list_inbox_messages", MagicMock(return_value=rows))
        monkeypatch.setattr(
            inbox_mod, "get_candidate_id_for_query", MagicMock(return_value=None)
        )
        dbg_index = MagicMock()
        dbg_detail = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(inbox_mod.logger, "debug_index", dbg_index)
        monkeypatch.setattr(inbox_mod.logger, "debug_detail", dbg_detail)
        inbox_mod.list_inbox_messages(debug=True)
        assert dbg_index.called
        assert dbg_index.call_args.kwargs["func"] == "inbox_bind"
        assert dbg_index.call_args.kwargs["outcome"] == "found|none"
        details = [str(c) for c in dbg_detail.call_args_list]
        # empty bind_address is omitted — truncate_debug_content("") yields no lines
        assert any("bind_header=" in d for d in details)


# AST-1313: From unique hit wins; else To binds only on one remaining address after inbox ignore.
class TestAst1313FromThenToBind:
    def _inbox(self) -> str:
        return inbox_mod.INBOX_BIND_CONFIG["inbox_address"]

    def _lookup(self, monkeypatch: pytest.MonkeyPatch, table: dict[str, str | None]) -> MagicMock:
        folded = {k.casefold(): v for k, v in table.items()}

        def _side(q: str, debug: bool = False):
            from email.utils import parseaddr

            _display, addr = parseaddr(q or "")
            token = (addr or q or "").strip().casefold()
            return folded.get(token)

        lookup = MagicMock(side_effect=_side)
        monkeypatch.setattr(inbox_mod, "get_candidate_id_for_query", lookup)
        return lookup

    def _list(self, monkeypatch: pytest.MonkeyPatch, **msg) -> list[dict]:
        monkeypatch.setattr(
            inbox_mod, "external_list_inbox_messages", MagicMock(return_value=[msg])
        )
        return inbox_mod.list_inbox_messages(debug=False)

    def test_from_unique_wins_over_conflicting_to(self, monkeypatch: pytest.MonkeyPatch) -> None:
        lookup = self._lookup(monkeypatch, {"ada@ex.com": "cand-ada", "bob@ex.com": "cand-bob"})
        out = self._list(
            monkeypatch,
            id="m1",
            from_address="Ada <ada@ex.com>",
            to_address="Bob <bob@ex.com>",
        )
        assert out[0]["candidate_match"] == {
            "matched": True,
            "astral_candidate_id": "cand-ada",
        }
        assert set(out[0]["candidate_match"]) == {"matched", "astral_candidate_id"}
        assert lookup.call_count == 1
        assert lookup.call_args.args[0] == "Ada <ada@ex.com>"

    def test_to_single_remaining_after_inbox_ignore(self, monkeypatch: pytest.MonkeyPatch) -> None:
        inbox = self._inbox()
        self._lookup(monkeypatch, {"ada@ex.com": "cand-ada"})
        out = self._list(
            monkeypatch,
            id="m2",
            from_address="recruiter@corp.com",
            to_address=f"Astral <{inbox}>, Ada <ada@ex.com>",
        )
        assert out[0]["candidate_match"] == {
            "matched": True,
            "astral_candidate_id": "cand-ada",
        }

    def test_unbound_when_to_empty_multi_or_inbox_only(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        inbox = self._inbox()
        self._lookup(monkeypatch, {"ada@ex.com": "cand-ada", "bob@ex.com": "cand-bob"})
        empty = self._list(monkeypatch, id="e", from_address="x@y", to_address="")
        multi = self._list(
            monkeypatch, id="m", from_address="x@y", to_address="ada@ex.com, bob@ex.com"
        )
        only_inbox = self._list(monkeypatch, id="i", from_address="x@y", to_address=inbox)
        unbound = {"matched": False, "astral_candidate_id": None}
        assert empty[0]["candidate_match"] == unbound
        assert multi[0]["candidate_match"] == unbound
        assert only_inbox[0]["candidate_match"] == unbound

    def test_duplicate_to_address_is_one_remaining(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._lookup(monkeypatch, {"ada@ex.com": "cand-ada"})
        out = self._list(
            monkeypatch,
            id="m3",
            from_address="x@y",
            to_address="Ada <ada@ex.com>, ada@ex.com",
        )
        assert out[0]["candidate_match"]["astral_candidate_id"] == "cand-ada"

    def test_create_rematch_uses_to_when_from_misses(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "get_message_html",
            MagicMock(
                return_value=_inbox_html(
                    html_body="<p>JD</p>",
                    subject="Role",
                    from_address="recruiter@corp.com",
                    to_address=f"{self._inbox()}, ada@ex.com",
                )
            ),
        )
        self._lookup(monkeypatch, {"ada@ex.com": "cand-ada"})
        _patch_land_enrich(monkeypatch, stem="alice@example.com")
        db = sqlite_in_memory
        db.save_candidate("cand-ada", state="NEW_CANDIDATE", candidate_data={"name": "A"})
        dbg_index = MagicMock()
        dbg_detail = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(inbox_mod.logger, "debug_index", dbg_index)
        monkeypatch.setattr(inbox_mod.logger, "debug_detail", dbg_detail)
        out = inbox_mod.create_meteorite_job_from_inbox_message("m1", debug=True)
        assert out["astral_candidate_id"] == "cand-ada"
        assert out["mode"] == "land_meteorite"
        assert out["company"] == "alice@example.com-cand-ada"
        details = [str(c) for c in dbg_detail.call_args_list]
        assert any("bind_header=to" in d for d in details)
        assert any("bind_address=ada@ex.com" in d for d in details)
        assert any("company=" in d for d in details)
        dbg_index.reset_mock()
        inbox_mod.create_meteorite_job_from_inbox_message("m1", debug=False)
        assert not dbg_index.called

    def test_list_debug_false_emits_no_contract(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "external_list_inbox_messages",
            MagicMock(return_value=[{"id": "m1", "from_address": "a@x"}]),
        )
        self._lookup(monkeypatch, {})
        dbg = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(inbox_mod.logger, "debug_detail", MagicMock())
        inbox_mod.list_inbox_messages(debug=False)
        assert not dbg.called


# AST-1049: strip/extract + Create orchestration.
# AST-1537: wrap embeds From/To/Subject/Date (not subject-only).
class TestAst1049StripExtractEmailHtml:
    def test_strips_tags_attrs_and_wraps_subject(self) -> None:
        raw = (
            '<html><body><script>alert(1)</script>'
            '<p style="x" onclick="y" onfocus="z">Hello</p></body></html>'
        )
        out = inbox_mod.strip_extract_email_html(
            "Role <A>",
            raw,
            from_address='Ada <ada@ex.com>',
            to_address='To <t@ex.com>',
            date='Sat, 29 Aug 2026',
        )
        assert "<script>" not in out
        assert "onclick" not in out
        assert "onfocus" not in out
        assert 'style="' not in out
        assert "Hello" in out
        assert "Role &lt;A&gt;" in out
        assert 'class="email-headers"' in out
        assert 'class="email-from"' in out
        assert "Ada &lt;ada@ex.com&gt;" in out
        assert 'class="email-to"' in out
        assert "To &lt;t@ex.com&gt;" in out
        assert 'class="email-subject"' in out
        assert 'class="email-date"' in out
        assert "Sat, 29 Aug 2026" in out
        assert 'class="email-body"' in out


# Branches: get_message_with_assembled_html keeps raw html_body + assembled header wrap.
class TestAst1537AssembledHtmlGet:
    def test_assembled_html_keeps_raw_body(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "get_message_html",
            MagicMock(
                return_value={
                    "id": "m1",
                    "html_body": "<p onclick=x>Body</p>",
                    "subject": "Subj <X>",
                    "from_address": "From <f@x>",
                    "to_address": "To <t@x>",
                    "date": "Mon",
                }
            ),
        )
        out = inbox_mod.get_message_with_assembled_html("m1")
        assert out["html_body"] == "<p onclick=x>Body</p>"
        assert out["assembled_html"] != out["html_body"]
        assert "Body" in out["assembled_html"]
        assert "onclick" not in out["assembled_html"]
        assert "Subj &lt;X&gt;" in out["assembled_html"]
        assert "From &lt;f@x&gt;" in out["assembled_html"]
        assert "To &lt;t@x&gt;" in out["assembled_html"]
        assert 'class="email-date"' in out["assembled_html"]
        assert "Mon" in out["assembled_html"]


class TestAst1049CreateMeteoriteJobFromInboxMessage:
    def test_happy_path_rematch_strip_land(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import METEORITE_CONFIG

        cid = "cand-1"
        stem = "alice@example.com"
        short = METEORITE_CONFIG["stem_short_name_template"].format(
            stem=stem, candidate_id=cid
        )
        sqlite_in_memory.save_candidate(
            cid, state="NEW_CANDIDATE", candidate_data={"name": "T"}
        )
        monkeypatch.setattr(
            inbox_mod, "get_message_html", MagicMock(return_value=_inbox_html())
        )
        _patch_bind_candidate(monkeypatch, cid)
        _patch_land_enrich(monkeypatch, stem=stem)
        out = inbox_mod.create_meteorite_job_from_inbox_message("m1", debug=False)
        assert out["astral_job_id"] is not None
        assert out["astral_candidate_id"] == cid
        assert out["mode"] == "land_meteorite"
        assert out["company"] == short
        assert len(out["created"]) == 1
        assert out["skipped"] == []
        row = sqlite_in_memory.get_job(out["astral_job_id"])
        assert row is not None
        assert row["company"] == short

    def test_unmatched_and_empty_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "get_message_html",
            MagicMock(
                return_value={
                    "id": "m1",
                    "html_body": "<p>x</p>",
                    "subject": "S",
                    "from_address": "x@y",
                }
            ),
        )
        monkeypatch.setattr(
            inbox_mod, "get_candidate_id_for_query", MagicMock(return_value=None)
        )
        with pytest.raises(ValueError, match="not matched"):
            inbox_mod.create_meteorite_job_from_inbox_message("m1")
        with pytest.raises(ValueError, match="message_id is required"):
            inbox_mod.create_meteorite_job_from_inbox_message("  ")

    def test_debug_emits_four_style_d_steps_with_company(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        cid = "cand-1"
        sqlite_in_memory.save_candidate(
            cid, state="NEW_CANDIDATE", candidate_data={"name": "T"}
        )
        monkeypatch.setattr(
            inbox_mod, "get_message_html", MagicMock(return_value=_inbox_html())
        )
        _patch_bind_candidate(monkeypatch, cid)
        _patch_land_enrich(monkeypatch, stem="alice@example.com", company_job_id="job-9")
        dbg = MagicMock()
        dbg_detail = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(inbox_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(inbox_mod.logger, "debug_detail", dbg_detail)
        inbox_mod.create_meteorite_job_from_inbox_message("m1", debug=True)
        outcomes = [c.kwargs.get("outcome") for c in dbg.call_args_list]
        assert outcomes == ["found", "matched", "extracted", "created"]
        details = [str(c) for c in dbg_detail.call_args_list]
        assert any("company=" in d for d in details)
        dbg.reset_mock()
        inbox_mod.create_meteorite_job_from_inbox_message("m1", debug=False)
        assert not dbg.called

    def test_all_skipped_style_d_outcome_skipped(
        self, sqlite_in_memory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import JOB_SOURCE_METEORITE, METEORITE_CONFIG

        cid = "cand-1"
        stem = "alice@example.com"
        short = METEORITE_CONFIG["stem_short_name_template"].format(
            stem=stem, candidate_id=cid
        )
        db = sqlite_in_memory
        db.save_candidate(cid, state="NEW_CANDIDATE", candidate_data={"name": "T"})
        db.save_company(short, state="METEORITE", candidate_id=cid)
        db.save_job(
            "existing-inbox",
            company=short,
            state=METEORITE_CONFIG["job_create_state"],
            source=JOB_SOURCE_METEORITE,
            company_job_id="SKIPINBOX1",
            job_title="Old",
        )
        monkeypatch.setattr(
            inbox_mod, "get_message_html", MagicMock(return_value=_inbox_html())
        )
        _patch_bind_candidate(monkeypatch, cid)
        _patch_land_enrich(monkeypatch, stem=stem, company_job_id="SKIPINBOX1")
        dbg = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(inbox_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(inbox_mod.logger, "debug_detail", MagicMock())
        out = inbox_mod.create_meteorite_job_from_inbox_message("m1", debug=True)
        assert out["astral_job_id"] == "existing-inbox"
        assert out["created"] == []
        assert len(out["skipped"]) == 1
        outcomes = [c.kwargs.get("outcome") for c in dbg.call_args_list]
        assert outcomes[-1] == METEORITE_CONFIG["land_outcome_duplicate_skip"]


# Branches: strip_extract runs paste normalize before subject wrap (AST-1131).
class TestAst1131StripNormalizePastedList:
    def test_strip_unwraps_nested_autolink_job_href(self) -> None:
        from bs4 import BeautifulSoup

        uid = "9f704ad3-7a18-506a-bd5e-6a84e73b7c00"
        dice = f"https://www.dice.com/job-detail/{uid}"
        raw = (
            f'&lt;div xmlns="&lt;a href="http://www.w3.org/2000/svg"&gt;'
            f'http://www.w3.org/2000/svg&lt;/a&gt;"&gt;'
            f'&lt;a href="&lt;a href="{dice}"&gt;{dice}&lt;/a&gt;"&gt;Job&lt;/a&gt;'
            f'&lt;/div&gt;'
        )
        out = inbox_mod.strip_extract_email_html(
            "Saved jobs", f"<html><body><p>{raw}</p></body></html>"
        )
        hrefs = [
            a.get("href")
            for a in BeautifulSoup(out, "html.parser").find_all("a", href=True)
        ]
        assert hrefs == [dice]
        assert "w3.org/2000/svg" not in hrefs
        assert 'class="email-subject"' in out
        assert 'class="email-body"' in out


# AST-1135: live bind-filtered inbox counts (Avail source).
class TestAst1135InboxBoundCounts:
    def test_map_and_per_candidate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        msgs = [
            {"id": "1", "candidate_match": {"matched": True, "astral_candidate_id": "A"}},
            {"id": "2", "candidate_match": {"matched": True, "astral_candidate_id": "A"}},
            {"id": "3", "candidate_match": {"matched": True, "astral_candidate_id": "B"}},
            {"id": "4", "candidate_match": {"matched": False, "astral_candidate_id": None}},
            {"id": "5", "candidate_match": {"matched": True, "astral_candidate_id": "  "}},
        ]
        monkeypatch.setattr(inbox_mod, "list_inbox_messages", MagicMock(return_value=msgs))
        assert inbox_mod.count_inbox_bound_by_candidate() == {"A": 2, "B": 1}
        assert inbox_mod.count_inbox_messages_bound_to_candidate("A") == 2
        assert inbox_mod.count_inbox_messages_bound_to_candidate("B") == 1
        assert inbox_mod.count_inbox_messages_bound_to_candidate("Z") == 0

    def test_blank_candidate_skips_list(self, monkeypatch: pytest.MonkeyPatch) -> None:
        listed = MagicMock(return_value=[{"id": "1"}])
        monkeypatch.setattr(inbox_mod, "list_inbox_messages", listed)
        assert inbox_mod.count_inbox_messages_bound_to_candidate("") == 0
        assert inbox_mod.count_inbox_messages_bound_to_candidate("   ") == 0
        listed.assert_not_called()


# --- AST-1531: inbox land/fetch → stage_meteorite ---


class TestAst1531InboxStageCutover:
    """_land_bound_inbox_message strips then stages with source_kind=email."""

    @pytest.mark.asyncio
    async def test_land_bound_stages_stripped_html(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.core import meteorite as meteorite_mod
        from src.utils.config import METEORITE_CONFIG

        created = METEORITE_CONFIG["land_outcome_created"]
        monkeypatch.setattr(
            inbox_mod,
            "get_message_html",
            MagicMock(
                return_value={
                    "subject": "Role",
                    "html_body": "<p onclick=x>JD body here</p>",
                    "from_address": "Ada <a@b.c>",
                    "to_address": "Susan <s@x>",
                    "date": "Fri, 28 Aug 2026",
                }
            ),
        )
        seen = {}

        async def _stage(cid, blob, *, source_kind, source_id, debug=False):
            seen.update(
                {
                    "cid": cid,
                    "blob": blob,
                    "source_kind": source_kind,
                    "source_id": source_id,
                    "debug": debug,
                }
            )
            return {
                "skipped": False,
                "stage_outcome": "single_jd_with_more",
                "outcome": created,
                "land": {"outcome": created, "error": None},
                "error": None,
                "scraps": [],
                "batch_id": "b-inbox",
            }

        monkeypatch.setattr(meteorite_mod, "stage_meteorite", _stage)
        out = await inbox_mod._land_bound_inbox_message("m-inbox", "c1", debug=False)
        assert out["outcome"] == created
        assert seen["cid"] == "c1"
        assert seen["source_kind"] == "email"
        assert seen["source_id"] == "m-inbox"
        assert "JD body here" in seen["blob"]
        assert "onclick" not in seen["blob"]
        assert "Role" in seen["blob"]
        # AST-1537: land blob is header+body HTML, not subject-only wrap.
        assert 'class="email-from"' in seen["blob"]
        assert "Ada &lt;a@b.c&gt;" in seen["blob"]
        assert 'class="email-to"' in seen["blob"]
        assert "Susan &lt;s@x&gt;" in seen["blob"]
        assert 'class="email-date"' in seen["blob"]
        assert "Fri, 28 Aug 2026" in seen["blob"]

    @pytest.mark.asyncio
    async def test_land_bound_empty_strip_errors_without_stage(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.core import meteorite as meteorite_mod
        from src.utils.config import METEORITE_CONFIG

        monkeypatch.setattr(
            inbox_mod,
            "get_message_html",
            MagicMock(return_value={"subject": "S", "html_body": "<p>x</p>", "from_address": "a"}),
        )
        # Strip gate is on the post-strip blob; force empty to assert no stage call.
        monkeypatch.setattr(inbox_mod, "strip_extract_email_html", MagicMock(return_value="  "))
        stage = AsyncMock()
        monkeypatch.setattr(meteorite_mod, "stage_meteorite", stage)
        out = await inbox_mod._land_bound_inbox_message("m-empty", "c1", debug=False)
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_error"]
        assert "empty" in (out.get("error") or "").lower()
        stage.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_land_inbox_message_ids_uses_stage_path(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import METEORITE_CONFIG

        created = METEORITE_CONFIG["land_outcome_created"]
        monkeypatch.setattr(
            inbox_mod,
            "list_inbox_messages",
            MagicMock(
                return_value=[
                    {
                        "id": "bound",
                        "candidate_match": {
                            "matched": True,
                            "astral_candidate_id": "c1",
                        },
                    }
                ]
            ),
        )
        land = AsyncMock(
            return_value={
                "skipped": False,
                "outcome": created,
                "land": {"outcome": created},
            }
        )
        monkeypatch.setattr(inbox_mod, "_land_bound_inbox_message", land)
        out = await inbox_mod.land_inbox_message_ids(["bound", "missing"], debug=False)
        assert out["total_processed"] == 2
        assert out["total_passed"] == 1
        assert out["total_skipped"] == 1
        land.assert_awaited_once()
        assert land.await_args.args[:2] == ("bound", "c1")

