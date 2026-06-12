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
        "profile.title_patterns": "Engineer\nLead",
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
        assert ctx["starting_resume_text"] == "Resume body"
        assert ctx["sample_cover_text"] == "Cover"
        assert ctx["linkedin_profile_text"] == "LinkedIn"
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
        assert build_save[1]["profile"]["title_patterns"] == "Engineer\nLead"
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
