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
    """Mailbox outcomes: unbound trash/leave, bound ignore/create/archive, Style D gate."""

    @pytest.mark.asyncio
    async def test_unbound_fresh_left_stale_trashed(self, monkeypatch: pytest.MonkeyPatch) -> None:
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
        out = await ge.run_gaze_email({}, debug=False)
        assert out["total_processed"] == 2
        assert out["total_passed"] == 2
        trash.assert_called_once_with("stale")
        archive.assert_not_called()

    @pytest.mark.asyncio
    async def test_bound_ignore_non_url_empty_body(self, monkeypatch: pytest.MonkeyPatch) -> None:
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
        out = await ge.run_gaze_email({}, debug=False)
        assert out == {"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}
        archive.assert_not_called()
        trash.assert_not_called()
        create.assert_not_called()

    @pytest.mark.asyncio
    async def test_subject_url_create_then_archive(self, monkeypatch: pytest.MonkeyPatch) -> None:
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
        out = await ge.run_gaze_email({}, debug=False)
        assert out["total_passed"] == 1 and out["total_errors"] == 0
        create.assert_called_once()
        assert create.call_args.kwargs.get("job_link") == "https://jobs.example.com/role-1"
        archive.assert_called_once_with("m2")

    @pytest.mark.asyncio
    async def test_all_duplicate_skips_still_archive(self, monkeypatch: pytest.MonkeyPatch) -> None:
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
        out = await ge.run_gaze_email({}, debug=False)
        assert out["total_passed"] == 1
        create.assert_not_called()
        archive.assert_called_once_with("m3")

    @pytest.mark.asyncio
    async def test_html_links_ruth_jobs_create(self, monkeypatch: pytest.MonkeyPatch) -> None:
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
        out = await ge.run_gaze_email({}, debug=False)
        assert out["total_passed"] == 1
        create.assert_called_once()
        archive.assert_called_once_with("m4")

    @pytest.mark.asyncio
    async def test_debug_false_skips_style_d(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            ge, "list_inbox_messages", MagicMock(return_value=[_msg("m5", matched=False)])
        )
        dbg = MagicMock()
        monkeypatch.setattr(ge.logger, "debug_index", dbg)
        monkeypatch.setattr(ge.logger, "debug_detail", MagicMock())
        await ge.run_gaze_email({}, debug=False)
        dbg.assert_not_called()

    @pytest.mark.asyncio
    async def test_debug_true_emits_found_and_outcome(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            ge, "list_inbox_messages", MagicMock(return_value=[_msg("m6", matched=False)])
        )
        monkeypatch.setattr(ge, "trash_message", MagicMock())
        dbg = MagicMock()
        monkeypatch.setattr(ge.logger, "debug_index", dbg)
        monkeypatch.setattr(ge.logger, "set_debug_flag", MagicMock())
        await ge.run_gaze_email({}, debug=True)
        outcomes = [c.kwargs.get("outcome") for c in dbg.call_args_list]
        assert "found" in outcomes
        assert "ignored-unbound" in outcomes
        assert all(c.kwargs.get("func") == GAZE_EMAIL_CONFIG["debug_func"] for c in dbg.call_args_list)


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
