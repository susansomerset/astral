"""Component tests for src/core/inbox.py (AST-1032 / AST-1047)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.core import inbox as inbox_mod


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
        assert dbg_index.call_args.kwargs["func"] == "inbox_from_bind"
        assert dbg_index.call_args.kwargs["outcome"] == "found|none"
        assert any("from_address=" in str(c) for c in dbg_detail.call_args_list)


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
    def test_happy_path_rematch_strip_create(self, monkeypatch: pytest.MonkeyPatch) -> None:
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
        # AST-1061: orchestration calls gazer ingest sync (not create_meteorite_job).
        created_row = {
            "astral_job_id": "job-1",
            "company": "meteorite-cand-1",
            "state": "METEORITE_NEW",
            "latest_score": 10.0,
            "company_inserted": True,
        }
        ingest = MagicMock(
            return_value={
                "astral_candidate_id": "cand-1",
                "mode": "body",
                "created": [created_row],
                "skipped": [],
            }
        )
        monkeypatch.setattr(inbox_mod, "ingest_meteorite_jobs_from_email_html_sync", ingest)
        out = inbox_mod.create_meteorite_job_from_inbox_message("m1", debug=False)
        assert out["astral_job_id"] == "job-1"
        assert out["astral_candidate_id"] == "cand-1"
        assert out["mode"] == "body"
        assert out["created"] == [created_row]
        assert out["skipped"] == []
        ingest.assert_called_once()
        assert ingest.call_args.args[0] == "cand-1"
        html = ingest.call_args.args[1]
        assert "Engineer" in html
        assert "JD body" in html
        assert ingest.call_args.kwargs.get("debug") is False

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
        monkeypatch.setattr(
            inbox_mod,
            "ingest_meteorite_jobs_from_email_html_sync",
            MagicMock(
                return_value={
                    "astral_candidate_id": "cand-1",
                    "mode": "body",
                    "created": [
                        {
                            "astral_job_id": "job-9",
                            "company": "meteorite-cand-1",
                            "state": "METEORITE_NEW",
                            "latest_score": 10.0,
                            "company_inserted": False,
                        }
                    ],
                    "skipped": [],
                }
            ),
        )
        dbg = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(inbox_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(inbox_mod.logger, "debug_detail", MagicMock())
        inbox_mod.create_meteorite_job_from_inbox_message("m1", debug=True)
        outcomes = [c.kwargs.get("outcome") for c in dbg.call_args_list]
        assert outcomes == ["found", "matched", "extracted", "recorded"]
        dbg.reset_mock()
        inbox_mod.create_meteorite_job_from_inbox_message("m1", debug=False)
        assert not dbg.called

    def test_all_skipped_style_d_outcome_skipped(
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
        monkeypatch.setattr(
            inbox_mod,
            "ingest_meteorite_jobs_from_email_html_sync",
            MagicMock(
                return_value={
                    "astral_candidate_id": "cand-1",
                    "mode": "body",
                    "created": [],
                    "skipped": [
                        {
                            "reason": "known_company_job_id",
                            "url": None,
                            "matched_company_job_id": "EXT-1",
                        }
                    ],
                }
            ),
        )
        dbg = MagicMock()
        monkeypatch.setattr(inbox_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(inbox_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(inbox_mod.logger, "debug_detail", MagicMock())
        out = inbox_mod.create_meteorite_job_from_inbox_message("m1", debug=True)
        assert out["astral_job_id"] is None
        assert out["created"] == []
        assert len(out["skipped"]) == 1
        outcomes = [c.kwargs.get("outcome") for c in dbg.call_args_list]
        assert outcomes == ["found", "matched", "extracted", "skipped"]
