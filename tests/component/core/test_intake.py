"""Component tests for src/core/intake.py (AST-558)."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import intake as intake_mod
from src.utils.config import INTAKE_CONFIG


def _interview_turn(*, ready: bool = False, message: str = "Hello from Estelle") -> dict[str, Any]:
    return {"ready_to_build": ready, "assistant_message": message}


async def _wait_for_transcript_assistant(session_id: str, *, timeout: float = 2.0) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        row = intake_mod.database.get_intake_session(session_id)
        if row and intake_mod._transcript_has_assistant(row.get("transcript") or []):
            return row
        await asyncio.sleep(0.05)
    raise AssertionError(f"timeout waiting for assistant on {session_id}")


async def _wait_until_not_awaiting(session_id: str, *, timeout: float = 2.0) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        row = intake_mod.database.get_intake_session(session_id)
        if row and not intake_mod.get_intake_session_dto(row)["awaiting_agent"]:
            return row
        await asyncio.sleep(0.05)
    raise AssertionError(f"timeout waiting for agent completion on {session_id}")


def _build_payload() -> dict[str, str]:
    return {
        "context.bio_summary": "Bio",
        "context.backstory": "Story",
        "context.strengths": "Strong",
        "context.priorities": "Priority",
        "context.deal_breakers": "No remote",
        "contact.title_patterns": "Engineer\nLead",
        "company_search_terms": "Acme\nBeta Corp",
    }


@pytest.fixture
def mock_do_task(monkeypatch: pytest.MonkeyPatch):
    calls: List[dict[str, Any]] = []

    async def _do_task(**kwargs):
        calls.append(kwargs)
        task_key = kwargs.get("task_key")
        if task_key in ("intake_initiate_candidate", "intake_candidate_response"):
            return {"success": True, "parsed_response": _interview_turn(ready=False)}
        if task_key == "intake_build_request":
            return {"success": True, "parsed_response": _build_payload()}
        raise AssertionError(f"unexpected task_key: {task_key}")

    monkeypatch.setattr(intake_mod, "do_task", _do_task)
    monkeypatch.setattr(intake_mod, "get_agent_data_by_batch", lambda batch_id: [])
    monkeypatch.setattr(intake_mod, "compute_batch_cost", lambda batch_id: 0.0)
    return calls


class TestIntakeHelpers:
    def test_validate_interview_turn_requires_object(self) -> None:
        with pytest.raises(ValueError, match="JSON object"):
            intake_mod._validate_interview_turn([])

    def test_validate_interview_turn_requires_ready_to_build_bool(self) -> None:
        with pytest.raises(ValueError, match="ready_to_build"):
            intake_mod._validate_interview_turn({"assistant_message": "hi"})

    def test_validate_interview_turn_requires_assistant_message(self) -> None:
        with pytest.raises(ValueError, match="assistant_message"):
            intake_mod._validate_interview_turn({"ready_to_build": True, "assistant_message": "  "})

    def test_get_intake_session_dto_flags(self) -> None:
        active_row = {
            "intake_session_id": "sess-1",
            "status": INTAKE_CONFIG["session_status_active"],
            "transcript": [],
            "last_ready_to_build": True,
        }
        dto = intake_mod.get_intake_session_dto(active_row, batch_id="batch-1")
        assert dto["can_build"] is True
        assert dto["build_completed"] is False
        assert dto["awaiting_agent"] is True
        assert dto["batch_id"] == "batch-1"

        with_assistant = {
            **active_row,
            "transcript": [{"role": "assistant", "text": "Hi", "ready_to_build": False}],
        }
        assert intake_mod.get_intake_session_dto(with_assistant)["awaiting_agent"] is False

        built_row = {**active_row, "status": INTAKE_CONFIG["session_status_built"]}
        built = intake_mod.get_intake_session_dto(built_row)
        assert built["build_completed"] is True
        assert built["can_build"] is False


class TestIntakeSessionFlow:
    @pytest.mark.asyncio
    async def test_create_session_persists_source_materials(
        self, seeded_db, mock_do_task, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        saved: list[tuple] = []

        def _save(candidate_id: str, data: dict, **kwargs):
            saved.append((candidate_id, data, kwargs))

        monkeypatch.setattr(intake_mod, "save_candidate_data", _save)
        dto = await intake_mod.create_intake_session_and_start(
            "cand-1",
            "Resume body",
            sample_cover_text="Cover",
            linkedin_profile_text="LinkedIn",
        )
        assert dto["status"] == INTAKE_CONFIG["session_status_active"]
        assert dto["ready_to_build"] is False
        assert dto["awaiting_agent"] is True
        assert len(dto["transcript"]) == 0
        assert saved
        ctx = saved[0][1]["context"]
        assert ctx["raw_resume"] == "Resume body"
        assert ctx["raw_sample"] == "Cover"
        assert ctx["raw_profile"] == "LinkedIn"
        row = await _wait_for_transcript_assistant(dto["session_id"])
        assert len(row["transcript"]) == 2
        assert row["transcript"][-1]["ready_to_build"] is False

    @pytest.mark.asyncio
    async def test_initiate_turn_forces_ready_to_build_false_when_model_returns_true(
        self, seeded_db, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def _do_task(**kwargs):
            if kwargs.get("task_key") == "intake_initiate_candidate":
                return {
                    "success": True,
                    "parsed_response": _interview_turn(ready=True, message="Ready already"),
                }
            raise AssertionError(kwargs.get("task_key"))

        monkeypatch.setattr(intake_mod, "do_task", _do_task)
        monkeypatch.setattr(intake_mod, "get_agent_data_by_batch", lambda batch_id: [])
        monkeypatch.setattr(intake_mod, "compute_batch_cost", lambda batch_id: 0.0)
        monkeypatch.setattr(intake_mod, "save_candidate_data", MagicMock())

        dto = await intake_mod.create_intake_session_and_start("cand-1", "Resume text")
        assert dto["awaiting_agent"] is True
        assert len(dto["transcript"]) == 0
        row = await _wait_for_transcript_assistant(dto["session_id"])
        final = intake_mod.get_intake_session_dto(row)
        assert final["ready_to_build"] is False
        assert final["can_build"] is False
        assert final["transcript"][-1]["ready_to_build"] is False
        assert row["last_ready_to_build"] is False

    @pytest.mark.asyncio
    async def test_turn_appends_transcript_and_propagates_ready_to_build(
        self, seeded_db, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def _do_task(**kwargs):
            if kwargs.get("task_key") == "intake_initiate_candidate":
                return {"success": True, "parsed_response": _interview_turn(ready=False)}
            if kwargs.get("task_key") == "intake_candidate_response":
                return {
                    "success": True,
                    "parsed_response": _interview_turn(ready=True, message="Ready when you are"),
                }
            raise AssertionError(kwargs.get("task_key"))

        monkeypatch.setattr(intake_mod, "do_task", _do_task)
        monkeypatch.setattr(intake_mod, "get_agent_data_by_batch", lambda batch_id: [])
        monkeypatch.setattr(intake_mod, "compute_batch_cost", lambda batch_id: 0.0)
        monkeypatch.setattr(intake_mod, "save_candidate_data", MagicMock())

        created = await intake_mod.create_intake_session_and_start("cand-1", "Resume text")
        session_id = created["session_id"]
        await _wait_for_transcript_assistant(session_id)
        turned = await intake_mod.post_intake_turn(session_id, "My answer")
        assert turned["awaiting_agent"] is True
        assert turned["transcript"][-1]["role"] == "user"
        row = await _wait_until_not_awaiting(session_id)
        final = intake_mod.get_intake_session_dto(row)
        assert final["ready_to_build"] is True
        assert final["can_build"] is True
        assert len(final["transcript"]) == 4
        assert final["transcript"][-1]["ready_to_build"] is True
        assert final["awaiting_agent"] is False

    @pytest.mark.asyncio
    async def test_build_persists_fields_and_blocks_second_build(
        self, seeded_db, mock_do_task, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        sync_calls: list[tuple[str, str]] = []
        save_calls: list[tuple] = []
        complete_calls: list[str] = []

        monkeypatch.setattr(
            intake_mod,
            "sync_company_search_terms_from_text",
            lambda cid, text: sync_calls.append((cid, text)),
        )
        monkeypatch.setattr(
            intake_mod,
            "save_candidate_data",
            lambda cid, data, **kwargs: save_calls.append((cid, data, kwargs)),
        )
        monkeypatch.setattr(
            intake_mod,
            "check_context_complete",
            lambda cid: complete_calls.append(cid),
        )

        created = await intake_mod.create_intake_session_and_start("cand-1", "Resume text")
        session_id = created["session_id"]
        await _wait_for_transcript_assistant(session_id)
        built = await intake_mod.post_intake_build(session_id)
        assert built["build_completed"] is True
        assert built["status"] == INTAKE_CONFIG["session_status_built"]
        assert set(built["persisted_fields"]) == set(INTAKE_CONFIG["build_field_paths"])
        assert sync_calls == [("cand-1", "Acme\nBeta Corp")]
        assert save_calls
        build_save = next(c for c in save_calls if "bio_summary" in (c[1].get("context") or {}))
        assert build_save[1]["context"]["bio_summary"] == "Bio"
        assert build_save[1]["contact"]["title_patterns"] == "Engineer\nLead"
        assert complete_calls == ["cand-1"]

        with pytest.raises(ValueError, match="build already completed"):
            await intake_mod.post_intake_build(session_id)

    @pytest.mark.asyncio
    async def test_ledger_task_key_uses_intake_prefix(
        self, seeded_db, mock_do_task, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        saves: list[tuple] = []
        monkeypatch.setattr(
            intake_mod.database,
            "save_dispatch_ledger",
            lambda *args, **kwargs: saves.append((args, kwargs)),
        )
        monkeypatch.setattr(intake_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(intake_mod, "save_candidate_data", MagicMock())
        created = await intake_mod.create_intake_session_and_start("cand-1", "Resume text")
        await _wait_for_transcript_assistant(created["session_id"])
        assert saves
        assert saves[0][0][1] == "intake-intake_initiate_candidate"

    @pytest.mark.asyncio
    async def test_fetch_active_session_returns_latest_active(self, seeded_db, mock_do_task, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(intake_mod, "save_candidate_data", MagicMock())
        first = await intake_mod.create_intake_session_and_start("cand-1", "Resume one")
        first_row = await _wait_for_transcript_assistant(first["session_id"])
        seeded_db.update_intake_session(
            first["session_id"],
            transcript=first_row["transcript"],
            prompt_snapshot=None,
            last_ready_to_build=False,
            status=INTAKE_CONFIG["session_status_built"],
            built_at="2026-06-02 12:00:00",
        )
        second = await intake_mod.create_intake_session_and_start("cand-1", "Resume two")
        await _wait_for_transcript_assistant(second["session_id"])
        active = intake_mod.fetch_active_intake_session("cand-1")
        assert active is not None
        assert active["intake_session_id"] == second["session_id"]

    @pytest.mark.asyncio
    async def test_create_session_rejects_duplicate_active(
        self, seeded_db, mock_do_task, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(intake_mod, "save_candidate_data", MagicMock())
        await intake_mod.create_intake_session_and_start("cand-1", "Resume text")
        with pytest.raises(ValueError, match="already exists"):
            await intake_mod.create_intake_session_and_start("cand-1", "Resume again")

    @pytest.mark.asyncio
    async def test_background_initiate_failure_writes_assistant_error(
        self, seeded_db, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def _do_task(**kwargs):
            if kwargs.get("task_key") == "intake_initiate_candidate":
                return {"success": False, "parsed_response": None}
            raise AssertionError(kwargs.get("task_key"))

        monkeypatch.setattr(intake_mod, "do_task", _do_task)
        monkeypatch.setattr(intake_mod, "get_agent_data_by_batch", lambda batch_id: [])
        monkeypatch.setattr(intake_mod, "compute_batch_cost", lambda batch_id: 0.0)
        monkeypatch.setattr(intake_mod, "save_candidate_data", MagicMock())

        dto = await intake_mod.create_intake_session_and_start("cand-1", "Resume text")
        row = await _wait_until_not_awaiting(dto["session_id"])
        assert row["transcript"][-1]["text"] == INTAKE_CONFIG["initiate_failure_message"]


class TestIntakeArchive:
    @pytest.mark.asyncio
    async def test_archive_active_session_appends_intakes_old_and_clears_active(
        self, seeded_db, mock_do_task, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        created = await intake_mod.create_intake_session_and_start("cand-1", "Resume text")
        await _wait_for_transcript_assistant(created["session_id"])
        result = intake_mod.archive_active_intake_session("cand-1")
        assert set(result.keys()) == {
            "archived_session_id",
            "archived_at",
            "intakes_old_count",
        }
        assert result["archived_session_id"] == created["session_id"]
        assert result["intakes_old_count"] == 1
        assert intake_mod.fetch_active_intake_session("cand-1") is None
        row = intake_mod.database.get_intake_session(created["session_id"])
        assert row is not None
        assert row["status"] == INTAKE_CONFIG["session_status_archived"]
        cand = intake_mod.get_candidate("cand-1")
        assert cand is not None
        old = (cand.get("candidate_data") or {}).get("intakes_old") or []
        assert len(old) == 1
        assert old[0]["intake_session_id"] == created["session_id"]
        assert len(old[0].get("transcript") or []) >= 2

    def test_archive_raises_when_no_active_session(self, seeded_db) -> None:
        with pytest.raises(LookupError, match="no active"):
            intake_mod.archive_active_intake_session("cand-1")

    @pytest.mark.asyncio
    async def test_second_archive_appends_second_entry(
        self, seeded_db, mock_do_task, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        first = await intake_mod.create_intake_session_and_start("cand-1", "Resume one")
        await _wait_for_transcript_assistant(first["session_id"])
        intake_mod.archive_active_intake_session("cand-1")
        second = await intake_mod.create_intake_session_and_start("cand-1", "Resume two")
        await _wait_for_transcript_assistant(second["session_id"])
        result = intake_mod.archive_active_intake_session("cand-1")
        assert result["intakes_old_count"] == 2
        cand = intake_mod.get_candidate("cand-1")
        ids = [
            e["intake_session_id"]
            for e in (cand.get("candidate_data") or {}).get("intakes_old") or []
        ]
        assert ids == [first["session_id"], second["session_id"]]


class TestAst1015ValidatePreambleAnswer:
    """AST-1015: Ruth Valid / Try Again / Escalate — no library writes."""

    @pytest.mark.asyncio
    async def test_returns_each_configured_outcome(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.utils.config import PREAMBLE_VALIDATION_CONFIG

        monkeypatch.setattr(
            intake_mod, "get_candidate", lambda cid: {"astral_candidate_id": cid},
        )
        monkeypatch.setattr(intake_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(intake_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(intake_mod, "compute_batch_cost", lambda batch_id: 0.0)
        save_spy = MagicMock()
        monkeypatch.setattr(intake_mod, "save_candidate_data", save_spy)

        for outcome in PREAMBLE_VALIDATION_CONFIG["outcomes"]:
            async def _do_task(outcome=outcome, **kwargs):
                assert kwargs["task_key"] == PREAMBLE_VALIDATION_CONFIG["task_key"]
                assert "QUESTION:\nWhat is your resume?" in kwargs["live_content"]
                assert "ANSWER:\nbody" in kwargs["live_content"]
                return {"success": True, "parsed_response": {"outcome": outcome}}

            monkeypatch.setattr(intake_mod, "do_task", _do_task)
            result = await intake_mod.validate_preamble_answer(
                "cand-1", "What is your resume?", "body",
            )
            assert result["success"] is True
            assert result["outcome"] == outcome
            assert result["error"] is None
            assert result["batch_id"].startswith(
                f"preamble-{PREAMBLE_VALIDATION_CONFIG['task_key']}-",
            )
        assert save_spy.call_count == 0

    @pytest.mark.asyncio
    async def test_empty_answer_allowed_unknown_outcome_not_valid(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            intake_mod, "get_candidate", lambda cid: {"astral_candidate_id": cid},
        )
        monkeypatch.setattr(intake_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(intake_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(intake_mod, "compute_batch_cost", lambda batch_id: 0.0)

        async def _do_task(**kwargs):
            assert "ANSWER:\n" in kwargs["live_content"]
            return {"success": True, "parsed_response": {"outcome": "Maybe"}}

        monkeypatch.setattr(intake_mod, "do_task", _do_task)
        result = await intake_mod.validate_preamble_answer("cand-1", "Q?", "")
        assert result["success"] is False
        assert result["outcome"] is None
        assert "invalid preamble validation outcome" in result["error"]

    @pytest.mark.asyncio
    async def test_missing_candidate_and_empty_question(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(intake_mod, "get_candidate", lambda cid: None)
        with pytest.raises(ValueError, match="Candidate not found"):
            await intake_mod.validate_preamble_answer("missing", "Q?", "A")

        monkeypatch.setattr(
            intake_mod, "get_candidate", lambda cid: {"astral_candidate_id": cid},
        )
        with pytest.raises(ValueError, match="question required"):
            await intake_mod.validate_preamble_answer("cand-1", "  ", "A")

    @pytest.mark.asyncio
    async def test_debug_emits_found_outcome(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            intake_mod, "get_candidate", lambda cid: {"astral_candidate_id": cid},
        )
        monkeypatch.setattr(intake_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(intake_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(intake_mod, "compute_batch_cost", lambda batch_id: 0.0)
        dbg = MagicMock()
        detail = MagicMock()
        monkeypatch.setattr(intake_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(intake_mod.logger, "debug_detail", detail)
        monkeypatch.setattr(intake_mod.logger, "set_debug_flag", MagicMock())

        async def _do_task(**kwargs):
            return {"success": True, "parsed_response": {"outcome": "Try Again"}}

        monkeypatch.setattr(intake_mod, "do_task", _do_task)
        await intake_mod.validate_preamble_answer(
            "cand-1", "Q?", "nope", step_index=2, step_total=3, debug=True,
        )
        dbg.assert_called_once()
        assert dbg.call_args.kwargs["func"] == "validate_preamble_answer"
        assert dbg.call_args.kwargs["outcome"] == "found|Try Again"
        assert dbg.call_args.kwargs["index"] == 2
        assert dbg.call_args.kwargs["total"] == 3
        assert any("question=" in str(c.args[0]) for c in detail.call_args_list)



class TestAst1075TopicMenuConfirmGenerate:
    """AST-1075: preamble packet snapshot, Estelle confirm, Topic Menu generate."""

    def _cand(self, **ctx_extra):
        context = {
            "raw_resume": "Resume body",
            "raw_profile": "LinkedIn",
            "raw_sample": "Cover",
            "bio_summary": "",
            "backstory": "",
            "strengths": "focus",
            "priorities": "",
            "deal_breakers": "",
            "hopes": "",
            "interests": "",
            "concerns": "",
        }
        context.update(ctx_extra)
        return {
            "astral_candidate_id": "cand-1",
            "full": "Ada Lovelace",
            "first": "Ada",
            "last": "Lovelace",
            "candidate_data": {
                "context": context,
                "contact": {"title_patterns": "engineer"},
                "topic_menu": {"topics": []},
            },
        }

    def test_build_preamble_packet_snapshot_shape(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(intake_mod, "get_candidate", lambda cid: self._cand())
        snap = intake_mod.build_preamble_packet_snapshot("cand-1")
        assert snap["name"] == {"full": "Ada Lovelace", "first": "Ada", "last": "Lovelace"}
        assert snap["context"]["raw_resume"] == "Resume body"
        assert snap["contact"]["title_patterns"] == "engineer"
        assert "preferred_name" not in snap["contact"]
        monkeypatch.setattr(intake_mod, "get_candidate", lambda cid: None)
        with pytest.raises(ValueError, match="Candidate not found"):
            intake_mod.build_preamble_packet_snapshot("missing")
        monkeypatch.setattr(
            intake_mod,
            "get_candidate",
            lambda cid: self._cand(raw_resume="   "),
        )
        with pytest.raises(ValueError, match="raw_resume required"):
            intake_mod.build_preamble_packet_snapshot("cand-1")

    @pytest.mark.asyncio
    async def test_confirm_continue_and_accepted_stamp(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.utils.config import TOPIC_MENU_GEN_CONFIG

        monkeypatch.setattr(intake_mod, "get_candidate", lambda cid: self._cand())
        mark = MagicMock(return_value={"topics": [], "preamble_confirmed_at": "t"})
        monkeypatch.setattr(intake_mod, "mark_topic_menu_preamble_confirmed", mark)
        save = MagicMock()
        monkeypatch.setattr(intake_mod, "save_candidate_data", save)

        async def _run_continue(cid, task_key, live_content, *, prompt_snapshot, debug=False):
            assert task_key == TOPIC_MENU_GEN_CONFIG["confirm_task_key"]
            assert "PREAMBLE_PACKET" in live_content
            return {
                "success": True,
                "batch_id": "intake-topic_menu_preamble_confirm-x",
                "parsed_response": {
                    "assistant_message": "Anything here you would change?",
                    "outcome": "continue",
                },
            }

        monkeypatch.setattr(intake_mod, "_run_intake_task", _run_continue)
        cont = await intake_mod.run_topic_menu_preamble_confirm("cand-1")
        assert cont["success"] is True
        assert cont["outcome"] == "continue"
        assert "Anything here you would change?" in cont["assistant_message"]
        mark.assert_not_called()

        async def _run_accept(cid, task_key, live_content, *, prompt_snapshot, debug=False):
            return {
                "success": True,
                "batch_id": "intake-topic_menu_preamble_confirm-y",
                "parsed_response": {
                    "assistant_message": "Great — locking this in.",
                    "outcome": "accepted",
                    "library_patches": {
                        "context": {"strengths": "updated strength", "bogus": "nope"},
                    },
                },
            }

        monkeypatch.setattr(intake_mod, "_run_intake_task", _run_accept)
        acc = await intake_mod.run_topic_menu_preamble_confirm(
            "cand-1", candidate_message="looks good",
        )
        assert acc["success"] is True
        assert acc["outcome"] == "accepted"
        assert "strengths" in acc["applied_patches"]
        assert "bogus" not in acc["applied_patches"]
        save.assert_called()
        mark.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_rejects_invalid_outcome(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(intake_mod, "get_candidate", lambda cid: self._cand())

        async def _run(cid, task_key, live_content, *, prompt_snapshot, debug=False):
            return {
                "success": True,
                "batch_id": "b",
                "parsed_response": {
                    "assistant_message": "hi",
                    "outcome": "Valid",
                },
            }

        monkeypatch.setattr(intake_mod, "_run_intake_task", _run)
        result = await intake_mod.run_topic_menu_preamble_confirm("cand-1")
        assert result["success"] is False
        assert "invalid confirm outcome" in result["error"]

    @pytest.mark.asyncio
    async def test_generate_requires_confirm_filters_informs_and_saves(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.utils.config import TOPIC_MENU_GEN_CONFIG

        menu_state = {"topics": [], "preamble_confirmed_at": "2026-07-30 12:00:00"}
        monkeypatch.setattr(intake_mod, "get_candidate", lambda cid: self._cand())
        monkeypatch.setattr(intake_mod, "get_topic_menu", lambda cid: dict(menu_state))
        saved: list = []

        def _save(cid, menu, revise=True, debug=False):
            saved.append({"menu": menu, "revise": revise, "debug": debug})
            return {"topics": menu["topics"], "preamble_confirmed_at": menu.get("preamble_confirmed_at")}

        monkeypatch.setattr(intake_mod, "save_topic_menu", _save)

        async def _run(cid, task_key, live_content, *, prompt_snapshot, debug=False):
            assert task_key == TOPIC_MENU_GEN_CONFIG["generate_task_key"]
            assert "INFORMS_CATALOG" in live_content
            return {
                "success": True,
                "batch_id": "intake-topic_menu_generate-z",
                "parsed_response": {
                    "informs_coverage_confirmed": True,
                    "informs_covered": ["backstory", "like_rubric"],
                    "topics": [
                        {
                            "id": "t-good",
                            "name": "Story",
                            "ask": "Tell me a short win?",
                            "required": True,
                            "informs": ["backstory", "strengths"],
                        },
                        {
                            "id": "t-bad",
                            "name": "Bad",
                            "ask": "Nope",
                            "required": True,
                            "informs": ["like_rubric"],
                        },
                    ],
                },
            }

        monkeypatch.setattr(intake_mod, "_run_intake_task", _run)
        out = await intake_mod.generate_topic_menu_from_preamble("cand-1")
        assert out["success"] is True
        assert out["rejected_topic_count"] == 1
        assert [t["id"] for t in out["menu"]["topics"]] == ["t-good"]
        # Authoritative coverage from survivors — ignore Estelle leftovers.
        assert out["informs_covered"] == ["strengths", "backstory"]
        assert saved[0]["revise"] is True
        assert saved[0]["menu"]["preamble_confirmed_at"] == "2026-07-30 12:00:00"

        menu_state.pop("preamble_confirmed_at", None)
        with pytest.raises(ValueError, match="preamble not confirmed"):
            await intake_mod.generate_topic_menu_from_preamble("cand-1")

    @pytest.mark.asyncio
    async def test_confirm_and_generate_debug_gated(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(intake_mod, "get_candidate", lambda cid: self._cand())
        monkeypatch.setattr(
            intake_mod,
            "get_topic_menu",
            lambda cid: {"topics": [], "preamble_confirmed_at": "t"},
        )
        monkeypatch.setattr(
            intake_mod,
            "save_topic_menu",
            lambda cid, menu, revise=True, debug=False: menu,
        )
        monkeypatch.setattr(intake_mod, "mark_topic_menu_preamble_confirmed", MagicMock())
        dbg = MagicMock()
        monkeypatch.setattr(intake_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(intake_mod.logger, "debug_detail", MagicMock())
        monkeypatch.setattr(intake_mod.logger, "set_debug_flag", MagicMock())

        async def _run_confirm(cid, task_key, live_content, *, prompt_snapshot, debug=False):
            return {
                "success": True,
                "batch_id": "b",
                "parsed_response": {
                    "assistant_message": "ok",
                    "outcome": "accepted",
                },
            }

        monkeypatch.setattr(intake_mod, "_run_intake_task", _run_confirm)
        await intake_mod.run_topic_menu_preamble_confirm("cand-1", debug=True)
        assert any(
            c.kwargs.get("func") == "run_topic_menu_preamble_confirm" for c in dbg.call_args_list
        )
        dbg.reset_mock()

        async def _run_gen(cid, task_key, live_content, *, prompt_snapshot, debug=False):
            return {
                "success": True,
                "batch_id": "b2",
                "parsed_response": {
                    "informs_coverage_confirmed": True,
                    "informs_covered": ["backstory"],
                    "topics": [
                        {
                            "id": "t1",
                            "name": "N",
                            "ask": "A?",
                            "required": False,
                            "informs": ["backstory"],
                        }
                    ],
                },
            }

        monkeypatch.setattr(intake_mod, "_run_intake_task", _run_gen)
        await intake_mod.generate_topic_menu_from_preamble("cand-1", debug=True)
        assert any(
            c.kwargs.get("func") == "generate_topic_menu_from_preamble" for c in dbg.call_args_list
        )
