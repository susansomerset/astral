"""Component tests for src/core/inbox.py (AST-1032 / AST-1558)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.core import inbox as inbox_mod


# Branches: success passthrough; log + re-raise on failure.
class TestListInboxMessages:
    def test_returns_external_rows_passthrough(
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
        out = inbox_mod.list_inbox_messages()
        assert len(out) == 1
        assert out[0]["id"] == "m1"
        assert out[0]["from_address"] == "a@x"
        assert "candidate_match" not in out[0]
        assert out[0] is not rows[0]

    def test_debug_true_emits_style_d_listed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [{"id": "m9", "from_address": "nobody@ex.com"}]
        monkeypatch.setattr(inbox_mod, "external_list_inbox_messages", MagicMock(return_value=rows))
        dbg_index = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(inbox_mod.logger, "debug_index", dbg_index)
        inbox_mod.list_inbox_messages(debug=True)
        assert dbg_index.called
        assert dbg_index.call_args.kwargs["func"] == "inbox.list"
        assert dbg_index.call_args.kwargs["outcome"] == "listed"

    def test_debug_false_emits_no_contract(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            inbox_mod,
            "external_list_inbox_messages",
            MagicMock(return_value=[{"id": "m1", "from_address": "a@x"}]),
        )
        dbg = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(inbox_mod.logger, "set_debug_flag", MagicMock())
        inbox_mod.list_inbox_messages(debug=False)
        assert not dbg.called

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


class TestAst1558CandidateInboxVerbs:
    def _rows(self, monkeypatch: pytest.MonkeyPatch, *msgs: dict) -> None:
        monkeypatch.setattr(
            inbox_mod, "external_list_inbox_messages", MagicMock(return_value=list(msgs))
        )

    def test_fetch_candidate_email_matches_from_or_to(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._rows(
            monkeypatch,
            {"id": "from-hit", "from_address": "Ada <ada@ex.com>", "to_address": ""},
            {"id": "to-hit", "from_address": "x@y", "to_address": "Bob <bob@ex.com>"},
            {"id": "miss", "from_address": "nobody@z.com", "to_address": "other@z.com"},
        )
        out = inbox_mod.fetch_candidate_email(["ada@ex.com", "bob@ex.com"])
        assert [m["id"] for m in out] == ["from-hit", "to-hit"]

    def test_fetch_candidate_email_empty_aliases_returns_empty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        listed = MagicMock(return_value=[{"id": "m1"}])
        monkeypatch.setattr(inbox_mod, "external_list_inbox_messages", listed)
        assert inbox_mod.fetch_candidate_email([]) == []
        assert inbox_mod.fetch_candidate_email(["", "not-an-email"]) == []
        listed.assert_not_called()

    def test_fetch_candidate_email_casefold(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._rows(
            monkeypatch,
            {"id": "m1", "from_address": "ADA@EX.COM", "to_address": ""},
        )
        out = inbox_mod.fetch_candidate_email(["Ada@Ex.Com"])
        assert len(out) == 1
        assert out[0]["id"] == "m1"

    def test_archive_candidate_email_happy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        archive = MagicMock()
        monkeypatch.setattr(inbox_mod, "external_archive_message", archive)
        inbox_mod.archive_candidate_email("m1")
        archive.assert_called_once_with("m1")

    def test_archive_candidate_email_blank_raises(self) -> None:
        with pytest.raises(ValueError, match="message_id is required"):
            inbox_mod.archive_candidate_email("")
        with pytest.raises(ValueError, match="message_id is required"):
            inbox_mod.archive_candidate_email("   ")

    def test_count_stubs_return_empty_and_zero(self) -> None:
        assert inbox_mod.count_inbox_bound_by_candidate() == {}
        assert inbox_mod.count_inbox_messages_bound_to_candidate("cand-1") == 0
        assert inbox_mod.count_inbox_messages_bound_to_candidate("") == 0

    def test_retired_symbols_absent(self) -> None:
        for name in (
            "run_fetch_email",
            "create_meteorite_job_from_inbox_message",
            "land_inbox_message_ids",
            "_land_bound_inbox_message",
            "_bind_inbox_message",
        ):
            assert not hasattr(inbox_mod, name), f"{name} should be removed"
