"""Component tests for src/core/gaze_email.py (AST-1090)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import gaze_email as ge
from src.utils.config import GAZE_EMAIL_CONFIG


def _msg(
    mid: str,
    *,
    matched: bool = False,
    cid: str = "c1",
    from_address: str = "x@y.z",
    internal_date_ms: int = 0,
) -> Dict[str, Any]:
    return {
        "id": mid,
        "from_address": from_address,
        "internal_date_ms": internal_date_ms,
        "candidate_match": {
            "matched": matched,
            "astral_candidate_id": cid if matched else None,
        },
    }


# Branches: scheme+netloc URL subject; empty / non-url reject.
class TestAst1090SubjectIsUrl:
    def test_http_https_with_netloc(self) -> None:
        assert ge._subject_is_url("https://jobs.example.com/role") is True
        assert ge._subject_is_url("http://x.test/a") is True

    def test_rejects_non_url_and_scheme_only(self) -> None:
        assert ge._subject_is_url("Hello role") is False
        assert ge._subject_is_url("https://") is False
        assert ge._subject_is_url("") is False


# Branches: retention age vs unknown internalDate.
class TestAst1090UnboundStale:
    def test_stale_when_older_than_retention(self) -> None:
        days = int(GAZE_EMAIL_CONFIG["unbound_retention_days"])
        now = 1_700_000_000_000
        old = now - (days + 1) * 24 * 60 * 60 * 1000
        assert ge._unbound_is_stale(old, now_ms=now) is True

    def test_fresh_and_unknown_left(self) -> None:
        days = int(GAZE_EMAIL_CONFIG["unbound_retention_days"])
        now = 1_700_000_000_000
        fresh = now - (days - 1) * 24 * 60 * 60 * 1000
        assert ge._unbound_is_stale(fresh, now_ms=now) is False
        assert ge._unbound_is_stale(0, now_ms=now) is False


@pytest.mark.skipif(
    not hasattr(ge, "run_gaze_email"),
    reason="AST-1090 gaze_email runner not on this publish tip",
)
class TestAst1090RunGazeEmail:
    """Mailbox outcomes: unbound trash/leave, bound ignore/create/archive, Style D gate.

    AST-1136: run requires candidate_id; stamps last_email_check; skips other-candidate mail.
    """

    def _stub_stamp(self, monkeypatch: pytest.MonkeyPatch) -> MagicMock:
        stamp = MagicMock()
        monkeypatch.setattr(ge, "update_candidate_last_email_check", stamp)
        return stamp

    @pytest.mark.asyncio
    async def test_unbound_fresh_left_stale_trashed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        stamp = self._stub_stamp(monkeypatch)
        days = int(GAZE_EMAIL_CONFIG["unbound_retention_days"])
        now = 1_700_000_000_000
        fresh_ms = now - 1 * 24 * 60 * 60 * 1000
        stale_ms = now - (days + 2) * 24 * 60 * 60 * 1000
        monkeypatch.setattr(ge.time, "time", lambda: now / 1000)
        monkeypatch.setattr(
            ge,
            "list_inbox_messages",
            MagicMock(
                return_value=[
                    _msg("fresh", matched=False, internal_date_ms=fresh_ms),
                    _msg("stale", matched=False, internal_date_ms=stale_ms),
                ]
            ),
        )
        trash = MagicMock()
        archive = MagicMock()
        monkeypatch.setattr(ge, "trash_message", trash)
        monkeypatch.setattr(ge, "archive_message", archive)
        out = await ge.run_gaze_email({"candidate_id": "c1"}, debug=False)
        assert out["total_processed"] == 2
        assert out["total_passed"] == 2
        trash.assert_called_once_with("stale")
        archive.assert_not_called()
        stamp.assert_called_once_with("c1")

    @pytest.mark.asyncio
    async def test_bound_ignore_non_url_empty_body(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._stub_stamp(monkeypatch)
        monkeypatch.setattr(
            ge, "list_inbox_messages", MagicMock(return_value=[_msg("m1", matched=True)])
        )
        monkeypatch.setattr(
            ge,
            "get_candidate",
            MagicMock(return_value={"astral_candidate_id": "c1", "candidate_api_key": "k"}),
        )
        monkeypatch.setattr(
            ge,
            "get_message_html",
            MagicMock(return_value={"subject": "Weekly digest", "html_body": "<p>  </p>", "from_address": "a"}),
        )
        archive = MagicMock()
        trash = MagicMock()
        create = MagicMock()
        monkeypatch.setattr(ge, "archive_message", archive)
        monkeypatch.setattr(ge, "trash_message", trash)
        monkeypatch.setattr(ge, "create_meteorite_job", create)
        out = await ge.run_gaze_email({"candidate_id": "c1"}, debug=False)
        assert out == {"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}
        archive.assert_not_called()
        trash.assert_not_called()
        create.assert_not_called()

    @pytest.mark.asyncio
    async def test_subject_url_create_then_archive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._stub_stamp(monkeypatch)
        monkeypatch.setattr(
            ge, "list_inbox_messages", MagicMock(return_value=[_msg("m2", matched=True)])
        )
        monkeypatch.setattr(
            ge,
            "get_candidate",
            MagicMock(return_value={"astral_candidate_id": "c1", "candidate_api_key": "k"}),
        )
        monkeypatch.setattr(
            ge,
            "get_message_html",
            MagicMock(
                return_value={
                    "subject": "https://jobs.example.com/role-1",
                    "html_body": "",
                    "from_address": "a",
                }
            ),
        )
        monkeypatch.setattr(
            ge,
            "_meteorite_fetch_link_visible_text",
            AsyncMock(return_value=("visible text " * 20, "https://jobs.example.com/role-1")),
        )
        monkeypatch.setattr(ge, "job_link_exists_for_candidate", MagicMock(return_value=False))
        create = MagicMock(return_value={"astral_job_id": "j1"})
        archive = MagicMock()
        monkeypatch.setattr(ge, "create_meteorite_job", create)
        monkeypatch.setattr(ge, "archive_message", archive)
        out = await ge.run_gaze_email({"candidate_id": "c1"}, debug=False)
        assert out["total_passed"] == 1 and out["total_errors"] == 0
        create.assert_called_once()
        assert create.call_args.kwargs.get("job_link") == "https://jobs.example.com/role-1"
        archive.assert_called_once_with("m2")

    @pytest.mark.asyncio
    async def test_all_duplicate_skips_still_archive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._stub_stamp(monkeypatch)
        monkeypatch.setattr(
            ge, "list_inbox_messages", MagicMock(return_value=[_msg("m3", matched=True)])
        )
        monkeypatch.setattr(
            ge,
            "get_candidate",
            MagicMock(return_value={"astral_candidate_id": "c1", "candidate_api_key": "k"}),
        )
        monkeypatch.setattr(
            ge,
            "get_message_html",
            MagicMock(
                return_value={
                    "subject": "https://jobs.example.com/dup",
                    "html_body": "",
                    "from_address": "a",
                }
            ),
        )
        monkeypatch.setattr(
            ge,
            "_meteorite_fetch_link_visible_text",
            AsyncMock(return_value=("visible text " * 20, "https://jobs.example.com/dup")),
        )
        monkeypatch.setattr(ge, "job_link_exists_for_candidate", MagicMock(return_value=True))
        create = MagicMock()
        archive = MagicMock()
        monkeypatch.setattr(ge, "create_meteorite_job", create)
        monkeypatch.setattr(ge, "archive_message", archive)
        out = await ge.run_gaze_email({"candidate_id": "c1"}, debug=False)
        assert out["total_passed"] == 1
        create.assert_not_called()
        archive.assert_called_once_with("m3")

    @pytest.mark.asyncio
    async def test_html_links_ruth_jobs_create(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._stub_stamp(monkeypatch)
        monkeypatch.setattr(
            ge, "list_inbox_messages", MagicMock(return_value=[_msg("m4", matched=True)])
        )
        monkeypatch.setattr(
            ge,
            "get_candidate",
            MagicMock(return_value={"astral_candidate_id": "c1", "candidate_api_key": "k"}),
        )
        monkeypatch.setattr(
            ge,
            "get_message_html",
            MagicMock(return_value={"subject": "", "html_body": "<p>many links here</p>", "from_address": "a"}),
        )
        monkeypatch.setattr(
            ge,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [{"job_link": "https://jobs.example.com/a"}],
                    },
                }
            ),
        )
        monkeypatch.setattr(
            ge,
            "_meteorite_fetch_link_visible_text",
            AsyncMock(return_value=("visible text " * 20, "https://jobs.example.com/a")),
        )
        monkeypatch.setattr(ge, "job_link_exists_for_candidate", MagicMock(return_value=False))
        create = MagicMock(return_value={"astral_job_id": "j2"})
        archive = MagicMock()
        monkeypatch.setattr(ge, "create_meteorite_job", create)
        monkeypatch.setattr(ge, "archive_message", archive)
        out = await ge.run_gaze_email({"candidate_id": "c1"}, debug=False)
        assert out["total_passed"] == 1
        create.assert_called_once()
        archive.assert_called_once_with("m4")

    @pytest.mark.asyncio
    async def test_html_links_dict_metadata_still_creates(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AST-1144: Ruth dict metadata must not block scrape/create/archive."""
        self._stub_stamp(monkeypatch)
        monkeypatch.setattr(
            ge, "list_inbox_messages", MagicMock(return_value=[_msg("m-dict", matched=True)])
        )
        monkeypatch.setattr(
            ge,
            "get_candidate",
            MagicMock(return_value={"astral_candidate_id": "c1", "candidate_api_key": "k"}),
        )
        monkeypatch.setattr(
            ge,
            "get_message_html",
            MagicMock(
                return_value={
                    "subject": "",
                    "html_body": "<a href=\"https://www.dice.com/job-detail/x\">role</a>",
                    "from_address": "a",
                }
            ),
        )
        monkeypatch.setattr(
            ge,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "parse_mode": "html_links",
                        "jobs": [
                            {
                                "job_link": "https://www.dice.com/job-detail/x",
                                "metadata": {"company": "Dice", "location": "Remote"},
                            }
                        ],
                    },
                }
            ),
        )
        monkeypatch.setattr(
            ge,
            "_meteorite_fetch_link_visible_text",
            AsyncMock(return_value=("visible text " * 20, "https://www.dice.com/job-detail/x")),
        )
        monkeypatch.setattr(ge, "job_link_exists_for_candidate", MagicMock(return_value=False))
        create = MagicMock(return_value={"astral_job_id": "j-dict"})
        archive = MagicMock()
        monkeypatch.setattr(ge, "create_meteorite_job", create)
        monkeypatch.setattr(ge, "archive_message", archive)
        out = await ge.run_gaze_email({"candidate_id": "c1"}, debug=False)
        assert out["total_passed"] == 1 and out["total_errors"] == 0
        create.assert_called_once()
        archive.assert_called_once_with("m-dict")

    @pytest.mark.asyncio
    async def test_debug_false_skips_style_d(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._stub_stamp(monkeypatch)
        monkeypatch.setattr(
            ge, "list_inbox_messages", MagicMock(return_value=[_msg("m5", matched=False)])
        )
        dbg = MagicMock()
        monkeypatch.setattr(ge.logger, "debug_index", dbg)
        monkeypatch.setattr(ge.logger, "debug_detail", MagicMock())
        await ge.run_gaze_email({"candidate_id": "c1"}, debug=False)
        dbg.assert_not_called()

    @pytest.mark.asyncio
    async def test_debug_true_emits_found_and_outcome(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._stub_stamp(monkeypatch)
        monkeypatch.setattr(
            ge, "list_inbox_messages", MagicMock(return_value=[_msg("m6", matched=False)])
        )
        monkeypatch.setattr(ge, "trash_message", MagicMock())
        dbg = MagicMock()
        monkeypatch.setattr(ge.logger, "debug_index", dbg)
        monkeypatch.setattr(ge.logger, "set_debug_flag", MagicMock())
        await ge.run_gaze_email({"candidate_id": "c1"}, debug=True)
        outcomes = [c.kwargs.get("outcome") for c in dbg.call_args_list]
        assert "run-start" in outcomes
        assert "found" in outcomes
        assert "ignored-unbound" in outcomes
        assert "run-complete" in outcomes
        assert all(c.kwargs.get("func") == GAZE_EMAIL_CONFIG["debug_func"] for c in dbg.call_args_list)


@pytest.mark.skipif(
    not hasattr(ge, "process_gaze_email_messages"),
    reason="AST-1136 process_gaze_email_messages not on this publish tip",
)
class TestAst1136CandidateBoundGazeEmail:
    """AST-1136: candidate filter, stamp, process_ helper (no trash/stamp)."""

    @pytest.mark.asyncio
    async def test_requires_candidate_id(self) -> None:
        with pytest.raises(ValueError, match="candidate_id is required"):
            await ge.run_gaze_email({}, debug=False)
        with pytest.raises(ValueError, match="candidate_id is required"):
            await ge.process_gaze_email_messages("", [], debug=False)

    @pytest.mark.asyncio
    async def test_skips_other_candidate_leaves_inbox(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        stamp = MagicMock()
        monkeypatch.setattr(ge, "update_candidate_last_email_check", stamp)
        monkeypatch.setattr(
            ge,
            "list_inbox_messages",
            MagicMock(
                return_value=[
                    _msg("mine", matched=True, cid="c1"),
                    _msg("theirs", matched=True, cid="c2"),
                ]
            ),
        )
        # AST-1140: _handle_bound returns (processed, passed, failed, errors, outcome).
        handle = AsyncMock(return_value=(1, 1, 0, 0, "ignored"))
        monkeypatch.setattr(ge, "_handle_bound", handle)
        trash = MagicMock()
        monkeypatch.setattr(ge, "trash_message", trash)
        out = await ge.run_gaze_email({"candidate_id": "c1"}, debug=False)
        assert out["total_processed"] == 2
        assert out["total_passed"] == 2
        assert handle.await_count == 1
        assert handle.await_args.args[0]["id"] == "mine"
        trash.assert_not_called()
        stamp.assert_called_once_with("c1")

    @pytest.mark.asyncio
    async def test_stamps_even_when_zero_bound(self, monkeypatch: pytest.MonkeyPatch) -> None:
        stamp = MagicMock()
        monkeypatch.setattr(ge, "update_candidate_last_email_check", stamp)
        monkeypatch.setattr(ge, "list_inbox_messages", MagicMock(return_value=[]))
        out = await ge.run_gaze_email({"candidate_id": "c1"}, debug=False)
        assert out["total_processed"] == 0
        stamp.assert_called_once_with("c1")

    @pytest.mark.asyncio
    async def test_process_skips_unbound_and_other_no_trash_no_stamp(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        stamp = MagicMock()
        monkeypatch.setattr(ge, "update_candidate_last_email_check", stamp)
        trash = MagicMock()
        monkeypatch.setattr(ge, "trash_message", trash)
        handle = AsyncMock(return_value=(1, 1, 0, 0, "ignored"))
        monkeypatch.setattr(ge, "_handle_bound", handle)
        msgs = [
            _msg("u", matched=False),
            _msg("other", matched=True, cid="c2"),
            _msg("mine", matched=True, cid="c1"),
        ]
        out = await ge.process_gaze_email_messages("c1", msgs, debug=False)
        assert out["total_processed"] == 3
        assert out["total_passed"] == 3
        assert handle.await_count == 1
        assert handle.await_args.args[0]["id"] == "mine"
        trash.assert_not_called()
        stamp.assert_not_called()


@pytest.mark.skipif(
    not hasattr(ge, "run_gaze_email_selected_ids"),
    reason="AST-1140 selected-ids entrypoint not on this publish tip",
)
class TestAst1140RunGazeEmailSelectedIds:
    """Land Meteorite: explicit ids only; skip unbound/missing; no stamp/Create/Trash."""

    @pytest.mark.asyncio
    async def test_skips_missing_unbound_unmatched_and_processes_bound(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        inbox = [
            _msg("bound", matched=True, cid="c1"),
            _msg("unbound", matched=False),
            {
                "id": "unmatched",
                "from_address": "x@y.z",
                "internal_date_ms": 0,
                "candidate_match": {"matched": True, "astral_candidate_id": ""},
            },
        ]
        monkeypatch.setattr(ge, "list_inbox_messages", MagicMock(return_value=inbox))
        monkeypatch.setattr(
            ge,
            "get_candidate",
            MagicMock(return_value={"astral_candidate_id": "c1", "candidate_api_key": "k"}),
        )
        monkeypatch.setattr(
            ge,
            "get_message_html",
            MagicMock(
                return_value={
                    "subject": "https://jobs.example.com/sel",
                    "html_body": "",
                    "from_address": "a",
                }
            ),
        )
        monkeypatch.setattr(
            ge,
            "_meteorite_fetch_link_visible_text",
            AsyncMock(return_value=("visible text " * 20, "https://jobs.example.com/sel")),
        )
        monkeypatch.setattr(ge, "job_link_exists_for_candidate", MagicMock(return_value=False))
        create = MagicMock(return_value={"astral_job_id": "j-sel"})
        archive = MagicMock()
        trash = MagicMock()
        stamp = MagicMock()
        create_strip = MagicMock()
        monkeypatch.setattr(ge, "create_meteorite_job", create)
        monkeypatch.setattr(ge, "archive_message", archive)
        monkeypatch.setattr(ge, "trash_message", trash)
        # Forbidden call sites — must never be invoked from selected-ids.
        import src.core.inbox as inbox_mod
        import src.data.database as database_mod

        # Stamp may be absent on older tips; still spy when present on AST-1128+.
        monkeypatch.setattr(
            database_mod, "update_candidate_last_email_check", stamp, raising=False
        )
        monkeypatch.setattr(
            inbox_mod, "create_meteorite_job_from_inbox_message", create_strip
        )

        out = await ge.run_gaze_email_selected_ids(
            ["  bound  ", "missing", "unbound", "unmatched", "", "  "],
            debug=False,
        )
        by_mid = {r["message_id"]: r for r in out["results"]}
        assert set(by_mid) == {"bound", "missing", "unbound", "unmatched"}
        assert by_mid["missing"]["outcome"] == GAZE_EMAIL_CONFIG[
            "selected_outcome_skipped_not_in_inbox"
        ]
        assert by_mid["unbound"]["outcome"] == GAZE_EMAIL_CONFIG[
            "selected_outcome_skipped_unbound"
        ]
        assert by_mid["unmatched"]["outcome"] == GAZE_EMAIL_CONFIG[
            "selected_outcome_skipped_unmatched"
        ]
        assert by_mid["bound"]["outcome"] == "archived"
        assert by_mid["bound"]["astral_candidate_id"] == "c1"
        assert out["total_skipped"] == 3
        assert out["total_processed"] == 4
        assert out["total_passed"] == 1
        create.assert_called_once()
        archive.assert_called_once_with("bound")
        trash.assert_not_called()
        stamp.assert_not_called()
        create_strip.assert_not_called()

    @pytest.mark.asyncio
    async def test_does_not_process_non_selected_inbox_messages(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            ge,
            "list_inbox_messages",
            MagicMock(
                return_value=[
                    _msg("keep", matched=True, cid="c1"),
                    _msg("other", matched=True, cid="c1"),
                ]
            ),
        )
        handle = AsyncMock(return_value=(1, 1, 0, 0, "ignored"))
        monkeypatch.setattr(ge, "_handle_bound", handle)
        out = await ge.run_gaze_email_selected_ids(["keep"], debug=False)
        assert [r["message_id"] for r in out["results"]] == ["keep"]
        handle.assert_awaited_once()
        assert handle.await_args.args[0]["id"] == "keep"

    @pytest.mark.asyncio
    async def test_debug_gate_uses_selected_func(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            ge, "list_inbox_messages", MagicMock(return_value=[_msg("u1", matched=False)])
        )
        dbg = MagicMock()
        flag = MagicMock()
        monkeypatch.setattr(ge.logger, "debug_index", dbg)
        monkeypatch.setattr(ge.logger, "debug_detail", MagicMock())
        monkeypatch.setattr(ge.logger, "set_debug_flag", flag)

        await ge.run_gaze_email_selected_ids(["u1"], debug=False)
        dbg.assert_not_called()
        flag.assert_not_called()

        await ge.run_gaze_email_selected_ids(["u1"], debug=True)
        flag.assert_called_once_with(True)
        outcomes = [c.kwargs.get("outcome") for c in dbg.call_args_list]
        assert "found" in outcomes
        assert GAZE_EMAIL_CONFIG["selected_outcome_skipped_unbound"] in outcomes
        assert all(
            c.kwargs.get("func") == GAZE_EMAIL_CONFIG["debug_func_selected"]
            for c in dbg.call_args_list
        )


@pytest.mark.skipif(
    not hasattr(ge, "_ruth_live_parts"),
    reason="AST-1213 Ruth live payload helpers not on this publish tip",
)
class TestAst1213RuthLivePayload:
    """AST-1213: visible text + --- LINKS --- for Ruth; tracking wrappers kept."""

    _HTML = (
        "<p>New jobs</p>"
        '<a href="https://jobs.example.com/apply/123">Senior Engineer at Acme</a>'
        '<a href="https://example.list-manage.com/track/click?u=1">Staff Engineer at Globex</a>'
        '<a href="https://example.com/unsubscribe">Unsubscribe</a>'
        '<a href="mailto:x@y.z">x</a>'
    )

    def test_helpers_keep_tracking_drop_noise(self) -> None:
        text, links = ge._ruth_live_parts(self._HTML)
        assert "Staff Engineer at Globex" in text
        assert "https://jobs.example.com/apply/123" in links
        assert any("list-manage.com" in u for u in links)
        assert not any("unsubscribe" in u.casefold() for u in links)
        assert not any(u.lower().startswith("mailto:") for u in links)
        body = ge._format_ruth_live_body(text, links)
        assert "--- LINKS ---" in body
        assert "<a" not in body and "<p>" not in body
        assert ge._format_ruth_live_body("", []).startswith("(no visible text)")

    @pytest.mark.asyncio
    async def test_html_links_live_content_shape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        stamp = MagicMock()
        monkeypatch.setattr(ge, "update_candidate_last_email_check", stamp)
        monkeypatch.setattr(
            ge, "list_inbox_messages", MagicMock(return_value=[_msg("m-html", matched=True)])
        )
        monkeypatch.setattr(
            ge,
            "get_candidate",
            MagicMock(return_value={"astral_candidate_id": "c1", "candidate_api_key": "k"}),
        )
        monkeypatch.setattr(
            ge,
            "get_message_html",
            MagicMock(return_value={"subject": "", "html_body": self._HTML, "from_address": "a"}),
        )
        captured: dict = {}

        async def _do_task(**kwargs):
            captured["live_content"] = kwargs.get("live_content")
            return {"success": True, "parsed_response": {"jobs": []}}

        monkeypatch.setattr(ge, "do_task", _do_task)
        # AST-1294: empty Ruth jobs + payload links → reconcile stubs then ingest; keep this
        # case on live_content shape only (no real Playwright scrape).
        monkeypatch.setattr(ge, "_ingest_link", AsyncMock(return_value="skipped"))
        monkeypatch.setattr(ge, "archive_message", MagicMock())
        await ge.run_gaze_email({"candidate_id": "c1"}, debug=False)
        live = captured["live_content"]
        assert live.startswith("PARSE_MODE: html_links\n\n")
        assert "--- LINKS ---" in live
        assert any("list-manage.com" in line for line in live.splitlines())
        assert "<a href=" not in live
        assert "<p>" not in live

    @pytest.mark.asyncio
    async def test_subject_body_live_content_shape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(ge, "update_candidate_last_email_check", MagicMock())
        monkeypatch.setattr(
            ge, "list_inbox_messages", MagicMock(return_value=[_msg("m-sub", matched=True)])
        )
        monkeypatch.setattr(
            ge,
            "get_candidate",
            MagicMock(return_value={"astral_candidate_id": "c1", "candidate_api_key": "k"}),
        )
        monkeypatch.setattr(
            ge,
            "get_message_html",
            MagicMock(
                return_value={
                    "subject": "Weekly digest",
                    "html_body": self._HTML,
                    "from_address": "a",
                }
            ),
        )
        captured: dict = {}

        async def _do_task(**kwargs):
            captured["live_content"] = kwargs.get("live_content")
            return {
                "success": True,
                "parsed_response": {"jobs": [], "content_text": "Weekly digest"},
            }

        monkeypatch.setattr(ge, "do_task", _do_task)
        monkeypatch.setattr(ge, "create_meteorite_job", MagicMock(return_value={"astral_job_id": "j"}))
        monkeypatch.setattr(ge, "archive_message", MagicMock())
        await ge.run_gaze_email({"candidate_id": "c1"}, debug=False)
        live = captured["live_content"]
        assert live.startswith("PARSE_MODE: subject_body\nSUBJECT: Weekly digest\n\n")
        assert "--- LINKS ---" in live
        assert "<a href=" not in live

    @pytest.mark.asyncio
    async def test_debug_true_emits_ruth_payload_detail(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(ge, "update_candidate_last_email_check", MagicMock())
        monkeypatch.setattr(
            ge, "list_inbox_messages", MagicMock(return_value=[_msg("m-dbg", matched=True)])
        )
        monkeypatch.setattr(
            ge,
            "get_candidate",
            MagicMock(return_value={"astral_candidate_id": "c1", "candidate_api_key": "k"}),
        )
        monkeypatch.setattr(
            ge,
            "get_message_html",
            MagicMock(return_value={"subject": "", "html_body": self._HTML, "from_address": "a"}),
        )
        monkeypatch.setattr(
            ge,
            "do_task",
            AsyncMock(return_value={"success": True, "parsed_response": {"jobs": []}}),
        )
        # AST-1294: reconcile stubs missing payload links before ingest — isolate Style D payload lines.
        monkeypatch.setattr(ge, "_ingest_link", AsyncMock(return_value="skipped"))
        monkeypatch.setattr(ge, "archive_message", MagicMock())
        detail = MagicMock()
        monkeypatch.setattr(ge.logger, "debug_detail", detail)
        monkeypatch.setattr(ge.logger, "debug_index", MagicMock())
        monkeypatch.setattr(ge.logger, "set_debug_flag", MagicMock())
        await ge.run_gaze_email({"candidate_id": "c1"}, debug=True)
        lines = [c.args[0] for c in detail.call_args_list if c.args]
        assert any(isinstance(s, str) and s.startswith("ruth_payload visible_chars=") for s in lines)
        assert any(isinstance(s, str) and "PARSE_MODE: html_links" in s for s in lines)


@pytest.mark.skipif(
    not hasattr(ge, "_ensure_html_links_jobs_complete"),
    reason="AST-1294 html_links completeness helper not on this publish tip",
)
class TestAst1294HtmlLinksJobsComplete:
    """AST-1294: payload-link completeness reconcile + Style D found/recorded/missing."""

    _MISSING_A = "https://www.dice.com/job-detail/3628bf85-8915-4525-93ff-2f05e09f9e39"
    _MISSING_B = "https://www.dice.com/job-detail/add50803-2af1-4f26-aba5-3997c9db8905"
    # Parent UAT enumeration (34 Dice job-detail links); Ruth historically dropped the last two.
    _UAT_PAYLOAD = [
        "https://www.dice.com/job-detail/801012b1-1801-42dc-a784-fecd2ae4f871",
        "https://www.dice.com/job-detail/fe9ffb32-07bb-4fbc-beff-99c45969e423",
        "https://www.dice.com/job-detail/6210dbdf-304e-400f-b73a-3e1dfc5993d4",
        "https://www.dice.com/job-detail/711e4efd-04ca-428a-9d15-954aa9d4850a",
        "https://www.dice.com/job-detail/1f5c5c4c-a427-48aa-8f3c-4168ee3f22e7",
        "https://www.dice.com/job-detail/f00dcb10-f309-42cc-ab4a-aaaffd6a90c4",
        "https://www.dice.com/job-detail/c375529b-543c-48e7-a87c-39fb762e402c",
        "https://www.dice.com/job-detail/a740e541-f52e-4fa6-b522-a10d6845f0a4",
        "https://www.dice.com/job-detail/42f5e734-b1eb-45d3-8493-f18e03107211",
        "https://www.dice.com/job-detail/8e6f94dc-df8b-47b6-a96f-2c10b61e965d",
        "https://www.dice.com/job-detail/5edf3075-df3b-4538-8013-b23a3499eac2",
        "https://www.dice.com/job-detail/cc5614d4-6ff1-4673-8571-e59bdb455736",
        "https://www.dice.com/job-detail/04dd50e5-7829-4187-997e-753a8f1114ad",
        "https://www.dice.com/job-detail/cf1b0f6b-df72-4267-9882-8df914eb31f8",
        "https://www.dice.com/job-detail/0f4fd8c7-3032-47de-9f06-c1602d5a1617",
        "https://www.dice.com/job-detail/1c6049e1-27c4-4a42-b9c8-3e3be446d4e8",
        "https://www.dice.com/job-detail/238439a6-65f4-4c03-99b1-449e21fbc882",
        "https://www.dice.com/job-detail/f97e3e2f-79cc-4217-a8ca-ea07be3cc44b",
        "https://www.dice.com/job-detail/50ac44a4-ca09-4a0e-8297-cbdbe058b9d8",
        "https://www.dice.com/job-detail/68e6f5a7-a112-4ded-b81f-7bbe427f7d97",
        "https://www.dice.com/job-detail/e4a8ade2-7394-41c1-83c6-32e8484edf44",
        "https://www.dice.com/job-detail/5056150a-47c5-483e-8943-ba06fa880d2e",
        "https://www.dice.com/job-detail/b87017d4-f536-40ef-bac1-c9980a4c075d",
        "https://www.dice.com/job-detail/e118abab-d44f-4284-8773-a31de4409586",
        "https://www.dice.com/job-detail/e2bf7ac5-ead5-4d9f-867c-176835f43381",
        "https://www.dice.com/job-detail/3465ba33-4099-4b94-9ebe-f100ff59b843",
        "https://www.dice.com/job-detail/4b9727f4-ddc0-4aab-ab6e-dd7f42d9888e",
        "https://www.dice.com/job-detail/e5536776-23c8-4c86-b9a3-60c29d32ce69",
        "https://www.dice.com/job-detail/62749deb-b3a9-4372-b1fe-ebe0e8be619e",
        "https://www.dice.com/job-detail/c797094a-2fea-406c-8c58-ad2d19471685",
        "https://www.dice.com/job-detail/cd599298-c4ce-418a-9a68-9efc1ecc56f6",
        "https://www.dice.com/job-detail/fc812fa4-8436-4e0e-93eb-931c52c67193",
        _MISSING_A,
        _MISSING_B,
    ]

    def test_uat_34_payload_stubs_two_missing_null_titles(self) -> None:
        # AC1/AC2: 34 payload links + Ruth 32 → 34 jobs including the two UAT UUID tails.
        ruth = [{"job_link": u, "job_title": f"t{i}"} for i, u in enumerate(self._UAT_PAYLOAD[:32])]
        out = ge._ensure_html_links_jobs_complete(ruth, self._UAT_PAYLOAD, debug=False)
        assert len(out) == 34
        assert out[:32] == ruth
        assert out[32] == {"job_link": self._MISSING_A, "job_title": None}
        assert out[33] == {"job_link": self._MISSING_B, "job_title": None}
        links = {j["job_link"] for j in out}
        assert self._MISSING_A in links and self._MISSING_B in links

    def test_normalize_link_avoids_duplicate_stub(self) -> None:
        # Ruth echoes scheme/slash variant of a payload href — one row, no second stub.
        payload = ["https://www.dice.com/job-detail/abc/"]
        ruth = [{"job_link": "http://www.dice.com/job-detail/abc", "job_title": "Lead"}]
        out = ge._ensure_html_links_jobs_complete(ruth, payload, debug=False)
        assert len(out) == 1
        assert out[0]["job_title"] == "Lead"

    def test_preserves_ruth_extras_and_drops_junk_rows(self) -> None:
        payload = ["https://jobs.example.com/a"]
        ruth: List[Any] = [
            "not-a-dict",
            {"job_link": "", "job_title": "empty"},
            {"job_link": "https://jobs.example.com/extra-not-in-payload", "job_title": "keep"},
            {"job_link": "https://jobs.example.com/a", "job_title": "covered"},
        ]
        out = ge._ensure_html_links_jobs_complete(ruth, payload, debug=False)
        assert [j["job_link"] for j in out] == [
            "https://jobs.example.com/extra-not-in-payload",
            "https://jobs.example.com/a",
        ]

    def test_debug_true_emits_found_recorded_missing_ids(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        index = MagicMock()
        detail = MagicMock()
        monkeypatch.setattr(ge.logger, "debug_index", index)
        monkeypatch.setattr(ge.logger, "debug_detail", detail)
        payload = [
            "https://www.dice.com/job-detail/keep-me",
            self._MISSING_A,
            self._MISSING_B,
        ]
        ruth = [{"job_link": payload[0], "job_title": "Kept"}]
        out = ge._ensure_html_links_jobs_complete(ruth, payload, debug=True)
        assert len(out) == 3
        index.assert_called_once_with(
            func="gaze_email._ensure_html_links_jobs_complete",
            index=1,
            total=1,
            identifier="html_links",
            outcome="reconciled",
        )
        detail_msgs = [c.args[0] for c in detail.call_args_list if c.args]
        assert detail_msgs == [
            "found=3 recorded=1 missing="
            "3628bf85-8915-4525-93ff-2f05e09f9e39,add50803-2af1-4f26-aba5-3997c9db8905"
        ]

    def test_debug_false_or_complete_skips_style_d(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        index = MagicMock()
        detail = MagicMock()
        monkeypatch.setattr(ge.logger, "debug_index", index)
        monkeypatch.setattr(ge.logger, "debug_detail", detail)
        payload = [self._MISSING_A]
        ruth = [{"job_link": self._MISSING_A, "job_title": None}]
        # Complete coverage → no Style D even with debug=True.
        ge._ensure_html_links_jobs_complete(ruth, payload, debug=True)
        index.assert_not_called()
        detail.assert_not_called()
        # Incomplete + debug=False → stubs still, silence on Style D.
        out = ge._ensure_html_links_jobs_complete([], payload, debug=False)
        assert out == [{"job_link": self._MISSING_A, "job_title": None}]
        index.assert_not_called()
        detail.assert_not_called()

    @pytest.mark.asyncio
    async def test_html_links_call_site_ingests_stubbed_links(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Call site: incomplete Ruth jobs still feed stubbed payload links into _ingest_link.
        monkeypatch.setattr(ge, "update_candidate_last_email_check", MagicMock())
        monkeypatch.setattr(
            ge, "list_inbox_messages", MagicMock(return_value=[_msg("m-complete", matched=True)])
        )
        monkeypatch.setattr(
            ge,
            "get_candidate",
            MagicMock(return_value={"astral_candidate_id": "c1", "candidate_api_key": "k"}),
        )
        html = (
            f'<a href="{self._MISSING_A}">one</a>'
            f'<a href="{self._MISSING_B}">two</a>'
            '<a href="https://www.dice.com/job-detail/covered-uuid">three</a>'
        )
        monkeypatch.setattr(
            ge,
            "get_message_html",
            MagicMock(return_value={"subject": "", "html_body": html, "from_address": "a"}),
        )
        monkeypatch.setattr(
            ge,
            "do_task",
            AsyncMock(
                return_value={
                    "success": True,
                    "parsed_response": {
                        "jobs": [
                            {
                                "job_link": "https://www.dice.com/job-detail/covered-uuid",
                                "job_title": "Covered",
                            }
                        ],
                    },
                }
            ),
        )
        ingest = AsyncMock(return_value="created")
        monkeypatch.setattr(ge, "_ingest_link", ingest)
        monkeypatch.setattr(ge, "archive_message", MagicMock())
        out = await ge.run_gaze_email({"candidate_id": "c1"}, debug=False)
        assert out["total_passed"] == 1 and out["total_errors"] == 0
        ingested = [c.args[1] if c.args else c.kwargs.get("url") for c in ingest.call_args_list]
        # _ingest_link(cid, url, jd_suffix=..., debug=...) — URL is positional arg 1.
        assert self._MISSING_A in ingested
        assert self._MISSING_B in ingested
        assert "https://www.dice.com/job-detail/covered-uuid" in ingested
        assert len(ingested) == 3
