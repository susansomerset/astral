"""Component tests for src/core/inbox.py (AST-1032 / AST-1047)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import inbox as inbox_mod
from src.core import meteorite as meteorite_mod
from src.utils.config import METEORITE_CONFIG, METEORITE_EMAIL_MAILBOX_CONFIG


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
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "get_message_html",
            MagicMock(
                return_value={
                    "id": "m1",
                    "html_body": "<p>JD</p>",
                    "subject": "Role",
                    "from_address": "recruiter@corp.com",
                    "to_address": f"{self._inbox()}, ada@ex.com",
                }
            ),
        )
        self._lookup(monkeypatch, {"ada@ex.com": "cand-ada"})
        created_k = METEORITE_CONFIG["land_outcome_created"]
        land = AsyncMock(
            return_value={
                "outcome": created_k,
                "outcomes": [
                    {
                        "outcome": created_k,
                        "astral_job_id": "job-1",
                        "company": "meteorite-cand-ada",
                    }
                ],
                "company": "meteorite-cand-ada",
                "company_inserted": True,
                "error": None,
            }
        )
        monkeypatch.setattr(meteorite_mod, "land_meteorite", land)
        dbg_index = MagicMock()
        dbg_detail = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(inbox_mod.logger, "debug_index", dbg_index)
        monkeypatch.setattr(inbox_mod.logger, "debug_detail", dbg_detail)
        out = inbox_mod.create_meteorite_job_from_inbox_message("m1", debug=True)
        assert out["astral_candidate_id"] == "cand-ada"
        assert out["mode"] == "land_meteorite"
        assert land.await_args.args[0] == "cand-ada"
        details = [str(c) for c in dbg_detail.call_args_list]
        assert any("bind_header=to" in d for d in details)
        assert any("bind_address=ada@ex.com" in d for d in details)
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
class TestAst1049StripExtractEmailHtml:
    def test_strips_tags_attrs_and_wraps_subject(self) -> None:
        raw = (
            '<html><body><script>alert(1)</script>'
            '<p style="x" onclick="y" onfocus="z">Hello</p></body></html>'
        )
        out = inbox_mod.strip_extract_email_html("Role <A>", raw)
        assert "<script>" not in out
        assert "onclick" not in out
        assert "onfocus" not in out
        assert 'style="' not in out
        assert "Hello" in out
        assert "Role &lt;A&gt;" in out
        assert 'class="email-subject"' in out
        assert 'class="email-body"' in out


class TestAst1049CreateMeteoriteJobFromInboxMessage:
    """AST-1049 create path; AST-1472 retargets ingest → land_meteorite."""

    def test_happy_path_rematch_strip_land(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "get_message_html",
            MagicMock(
                return_value={
                    "id": "m1",
                    "html_body": "<p>JD body</p>",
                    "subject": "Engineer",
                    "from_address": "ada@ex.com",
                }
            ),
        )
        monkeypatch.setattr(
            inbox_mod, "get_candidate_id_for_query", MagicMock(return_value="cand-1")
        )
        created_k = METEORITE_CONFIG["land_outcome_created"]
        outcome_row = {
            "outcome": created_k,
            "astral_job_id": "job-1",
            "company": "meteorite-cand-1",
        }
        land = AsyncMock(
            return_value={
                "outcome": created_k,
                "outcomes": [outcome_row],
                "company": "meteorite-cand-1",
                "company_inserted": True,
                "error": None,
            }
        )
        monkeypatch.setattr(meteorite_mod, "land_meteorite", land)
        out = inbox_mod.create_meteorite_job_from_inbox_message("m1", debug=False)
        assert out["astral_job_id"] == "job-1"
        assert out["astral_candidate_id"] == "cand-1"
        assert out["mode"] == "land_meteorite"
        assert out["outcome"] == created_k
        assert out["created"] == [outcome_row]
        assert out["skipped"] == []
        land.assert_awaited_once()
        assert land.await_args.args[0] == "cand-1"
        html = land.await_args.kwargs.get("text") or land.await_args.args[1]
        assert "Engineer" in html
        assert "JD body" in html
        assert land.await_args.kwargs.get("debug") is False

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

    def test_debug_emits_four_style_d_steps(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "get_message_html",
            MagicMock(
                return_value={
                    "id": "m1",
                    "html_body": "<p>body</p>",
                    "subject": "Sub",
                    "from_address": "ada@ex.com",
                }
            ),
        )
        monkeypatch.setattr(
            inbox_mod, "get_candidate_id_for_query", MagicMock(return_value="cand-1")
        )
        created_k = METEORITE_CONFIG["land_outcome_created"]
        monkeypatch.setattr(
            meteorite_mod,
            "land_meteorite",
            AsyncMock(
                return_value={
                    "outcome": created_k,
                    "outcomes": [
                        {
                            "outcome": created_k,
                            "astral_job_id": "job-9",
                            "company": "meteorite-cand-1",
                        }
                    ],
                    "company": "meteorite-cand-1",
                    "company_inserted": False,
                    "error": None,
                }
            ),
        )
        dbg = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(inbox_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(inbox_mod.logger, "debug_detail", MagicMock())
        inbox_mod.create_meteorite_job_from_inbox_message("m1", debug=True)
        outcomes = [c.kwargs.get("outcome") for c in dbg.call_args_list]
        assert outcomes == ["found", "matched", "extracted", created_k]
        dbg.reset_mock()
        inbox_mod.create_meteorite_job_from_inbox_message("m1", debug=False)
        assert not dbg.called

    def test_duplicate_skip_style_d_outcome(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "get_message_html",
            MagicMock(
                return_value={
                    "id": "m1",
                    "html_body": "<p>" + ("x" * 50) + "</p>",
                    "subject": "Sub",
                    "from_address": "ada@ex.com",
                }
            ),
        )
        monkeypatch.setattr(
            inbox_mod, "get_candidate_id_for_query", MagicMock(return_value="cand-1")
        )
        skip_k = METEORITE_CONFIG["land_outcome_duplicate_skip"]
        skip_row = {
            "outcome": skip_k,
            "astral_job_id": "job-known",
            "company": "meteorite-cand-1",
        }
        monkeypatch.setattr(
            meteorite_mod,
            "land_meteorite",
            AsyncMock(
                return_value={
                    "outcome": skip_k,
                    "outcomes": [skip_row],
                    "company": "meteorite-cand-1",
                    "company_inserted": False,
                    "error": None,
                }
            ),
        )
        dbg = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(inbox_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(inbox_mod.logger, "debug_detail", MagicMock())
        out = inbox_mod.create_meteorite_job_from_inbox_message("m1", debug=True)
        assert out["astral_job_id"] == "job-known"
        assert out["created"] == []
        assert out["skipped"] == [skip_row]
        outcomes = [c.kwargs.get("outcome") for c in dbg.call_args_list]
        assert outcomes == ["found", "matched", "extracted", skip_k]



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


# Branches: empty inbox; unbound skip; land pass/fail rollup; no gaze_email (AST-1472).
class TestAst1472RunFetchEmail:
    """AST-1472: null-candidate fetch_email → land_meteorite for matched only."""

    @pytest.mark.asyncio
    async def test_empty_inbox_zeros(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(inbox_mod, "list_inbox_messages", MagicMock(return_value=[]))
        out = await inbox_mod.run_fetch_email(None, debug=False)
        assert out == {
            "total_processed": 0,
            "total_passed": 0,
            "total_failed": 0,
            "total_errors": 0,
        }

    @pytest.mark.asyncio
    async def test_unbound_counts_passed_without_land(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "list_inbox_messages",
            MagicMock(
                return_value=[
                    {
                        "id": "m-u",
                        "candidate_match": {
                            "matched": False,
                            "astral_candidate_id": None,
                        },
                    }
                ]
            ),
        )
        land = AsyncMock()
        monkeypatch.setattr(inbox_mod, "_land_bound_inbox_message", land)
        out = await inbox_mod.run_fetch_email({"task_key": "fetch_email"}, debug=False)
        assert out["total_processed"] == 1
        assert out["total_passed"] == 1
        assert out["total_failed"] == 0
        land.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_matched_created_and_error_rollup(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        created_k = METEORITE_CONFIG["land_outcome_created"]
        err_k = METEORITE_CONFIG["land_outcome_error"]
        monkeypatch.setattr(
            inbox_mod,
            "list_inbox_messages",
            MagicMock(
                return_value=[
                    {
                        "id": "m1",
                        "candidate_match": {
                            "matched": True,
                            "astral_candidate_id": "cand-1",
                        },
                    },
                    {
                        "id": "m2",
                        "candidate_match": {
                            "matched": True,
                            "astral_candidate_id": "cand-2",
                        },
                    },
                ]
            ),
        )

        async def _land(mid, cid, *, debug=False):
            if mid == "m1":
                return {"outcome": created_k, "outcomes": [], "error": None}
            return {"outcome": err_k, "outcomes": [], "error": "boom"}

        monkeypatch.setattr(inbox_mod, "_land_bound_inbox_message", _land)
        out = await inbox_mod.run_fetch_email(None, debug=False)
        assert out["total_processed"] == 2
        assert out["total_passed"] == 1
        assert out["total_failed"] == 1
        assert out["total_errors"] == 1


# Branches: missing/unbound skip; land attach; totals (AST-1472).
class TestAst1472LandInboxMessageIds:
    """AST-1472: admin selected-ids → land_inbox_message_ids."""

    @pytest.mark.asyncio
    async def test_skips_and_lands(self, monkeypatch: pytest.MonkeyPatch) -> None:
        skip_missing = METEORITE_EMAIL_MAILBOX_CONFIG[
            "selected_outcome_skipped_not_in_inbox"
        ]
        skip_unbound = METEORITE_EMAIL_MAILBOX_CONFIG["selected_outcome_skipped_unbound"]
        created_k = METEORITE_CONFIG["land_outcome_created"]
        monkeypatch.setattr(
            inbox_mod,
            "list_inbox_messages",
            MagicMock(
                return_value=[
                    {
                        "id": "m-bound",
                        "candidate_match": {
                            "matched": True,
                            "astral_candidate_id": "cand-1",
                        },
                    },
                    {
                        "id": "m-free",
                        "candidate_match": {
                            "matched": False,
                            "astral_candidate_id": None,
                        },
                    },
                ]
            ),
        )
        land_payload = {
            "outcome": created_k,
            "outcomes": [{"outcome": created_k, "astral_job_id": "j1"}],
            "error": None,
        }
        monkeypatch.setattr(
            inbox_mod,
            "_land_bound_inbox_message",
            AsyncMock(return_value=land_payload),
        )
        out = await inbox_mod.land_inbox_message_ids(
            ["gone", "m-free", "m-bound", "  "], debug=False
        )
        assert out["total_processed"] == 3
        assert out["total_skipped"] == 2
        assert out["total_passed"] == 1
        assert out["total_failed"] == 0
        by_mid = {r["message_id"]: r for r in out["results"]}
        assert by_mid["gone"]["outcome"] == skip_missing
        assert by_mid["m-free"]["outcome"] == skip_unbound
        assert by_mid["m-bound"]["outcome"] == created_k
        assert by_mid["m-bound"]["land"] == land_payload


# Branches: empty strip error; land passthrough (AST-1472).
class TestAst1472LandBoundInboxMessage:
    @pytest.mark.asyncio
    async def test_empty_strip_does_not_land(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "get_message_html",
            MagicMock(return_value={"subject": "S", "html_body": "<p></p>"}),
        )
        monkeypatch.setattr(
            inbox_mod, "strip_extract_email_html", MagicMock(return_value="   ")
        )
        land = AsyncMock()
        monkeypatch.setattr(meteorite_mod, "land_meteorite", land)
        out = await inbox_mod._land_bound_inbox_message("m1", "cand-1", debug=False)
        assert out["outcome"] == METEORITE_CONFIG["land_outcome_error"]
        assert "empty" in (out.get("error") or "")
        land.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_lands_stripped_html(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "get_message_html",
            MagicMock(
                return_value={"subject": "Role", "html_body": "<p>JD text here</p>"}
            ),
        )
        created_k = METEORITE_CONFIG["land_outcome_created"]
        land = AsyncMock(
            return_value={
                "outcome": created_k,
                "outcomes": [],
                "company": "meteorite-cand-1",
                "company_inserted": True,
                "error": None,
            }
        )
        monkeypatch.setattr(meteorite_mod, "land_meteorite", land)
        out = await inbox_mod._land_bound_inbox_message("m1", "cand-1", debug=False)
        assert out["outcome"] == created_k
        land.assert_awaited_once()
        assert land.await_args.args[0] == "cand-1"
        assert "JD text" in land.await_args.kwargs["text"]
