"""Component tests for src/core/candidate.py (AST-393)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import candidate as candidate_mod
from src.utils.config import (
    ASTRAL_CONFIG,
    BUILD_CONFIG,
    CANDIDATE_STATES,
    RESUME_STRUCTURE_CONTACT_SECTION_IDS,
    RESUME_STRUCTURE_KNOWN_SECTION_IDS,
)

_RUBRIC_CONTENT = "body\nA = one\nB = two"
_CI = ASTRAL_CONFIG["consult_importance"]
_VALID_ACCENT = (BUILD_CONFIG.get("accent_palette") or ["#1A1A2E"])[0].upper()


def _three_section_structure() -> dict[str, Any]:
    return {
        "sections": {
            "professional_summary": {
                "id": "professional_summary",
                "title": "Custom Summary",
                "enabled": True,
                "order": 0,
                "job_agent_editable": True,
            },
            "experience": {
                "id": "experience",
                "title": "Custom Jobs",
                "enabled": True,
                "order": 1,
                "job_agent_editable": True,
            },
            "technical_skills": {
                "id": "technical_skills",
                "title": "Custom Skills",
                "enabled": True,
                "order": 2,
                "job_agent_editable": True,
            },
        },
    }


def _craft_resume_base_payload(structure: dict, content: dict[str, str] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"resume_structure": structure}
    for sid, spec in structure["sections"].items():
        if spec.get("enabled"):
            payload[sid] = (content or {}).get(sid, f"content-{sid}")
    return payload


def _criterion(**overrides: Any) -> Dict[str, Any]:
    row = {"label": "fit", "content": _RUBRIC_CONTENT, "importance": 5}
    row.update(overrides)
    return row


# Branches: create row; list filters deleted; invalid transition.
class TestInitiateCandidate:
    def test_creates_new_candidate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved: list[tuple] = []
        monkeypatch.setattr(candidate_mod.database, "save_candidate", lambda *args, **kwargs: saved.append((args, kwargs)))
        candidate_mod.initiate_candidate("somerset", {"context": {}})
        assert saved[0][1]["state"] == "NEW_CANDIDATE"


class TestListCandidates:
    def test_hides_deleted_by_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "list_candidates",
            lambda: [
                {"astral_candidate_id": "a", "state": "NEW_CANDIDATE"},
                {"astral_candidate_id": "b", "state": "DELETED"},
            ],
        )
        ids = {c["astral_candidate_id"] for c in candidate_mod.list_candidates()}
        assert ids == {"a"}


class TestTransitionCandidateState:
    def test_rejects_disallowed_hop(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database, "get_candidate", lambda candidate_id: {"state": "NEW_CANDIDATE"}
        )
        with pytest.raises(ValueError, match="Invalid candidate state transition"):
            candidate_mod.transition_candidate_state("somerset", "ACTIVE_SEARCH")

    def test_rejects_unknown_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database, "get_candidate", lambda candidate_id: {"state": "NEW_CANDIDATE"}
        )
        with pytest.raises(ValueError, match="Unknown candidate state"):
            candidate_mod.transition_candidate_state("somerset", "LIVE_PROMPTS")

    def test_rejects_missing_candidate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: None)
        with pytest.raises(ValueError, match="Candidate not found"):
            candidate_mod.transition_candidate_state("missing", "INTAKE_INITIATED")


class TestNormalizeRubricArtifactsOnSave:
    def test_rejects_non_list_artifact(self) -> None:
        with pytest.raises(ValueError, match="must be a list"):
            candidate_mod.normalize_rubric_artifacts_on_save({"company_prefilter": "bad"})


class TestCheckContextComplete:
    def test_returns_false_when_context_incomplete(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {
                "state": "NEW_CANDIDATE",
                "candidate_data": {"context": {"strengths": "x"}},
            },
        )
        assert candidate_mod.check_context_complete("somerset") is False


class TestParseCandidateResume:
    @pytest.mark.asyncio
    async def test_returns_error_without_resume_text(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"state": "NEW_CANDIDATE", "candidate_data": {}},
        )
        out = await candidate_mod.parse_candidate_resume("somerset")
        assert out["success"] is False

    @pytest.mark.asyncio
    async def test_persists_parsed_resume(self, monkeypatch: pytest.MonkeyPatch) -> None:
        store = {
            "candidate_data": {"context": {"starting_resume_text": "resume body"}},
            "state": "NEW_CANDIDATE",
        }
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: dict(store))
        saves: list[dict] = []
        transition = MagicMock()

        def _save(candidate_id: str, **kwargs):
            if kwargs.get("candidate_data"):
                store["candidate_data"] = {**store["candidate_data"], **kwargs["candidate_data"]}
            if kwargs.get("state"):
                store["state"] = kwargs["state"]
            saves.append(kwargs)

        monkeypatch.setattr(candidate_mod.database, "save_candidate", _save)
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", transition)
        structure = _three_section_structure()
        parsed = _craft_resume_base_payload(structure, {"professional_summary": "ok"})
        monkeypatch.setattr(
            candidate_mod,
            "do_task",
            AsyncMock(return_value={"success": True, "parsed_response": parsed}),
        )
        out = await candidate_mod.parse_candidate_resume("somerset")
        assert out["success"] is True
        artifacts = store["candidate_data"]["artifacts"]
        assert artifacts["resume_structure"]["sections"]["professional_summary"]["title"] == "Custom Summary"
        assert artifacts["base_resume"]["professional_summary"] == "ok"
        # AST-970: parse no longer auto-hops to PROFILE_READY / any state
        transition.assert_not_called()
        assert store["state"] == "NEW_CANDIDATE"


class TestSaveCandidateData:
    def test_merge_and_replace_delegate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.save_candidate_data("somerset", {"a": 1})
        candidate_mod.save_candidate_data("somerset", {"b": 2}, replace=True)
        assert save.call_args_list[0].kwargs["merge"] is True
        assert save.call_args_list[1].kwargs["merge"] is False


class TestGetCandidate:
    def test_delegates_to_database(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        assert candidate_mod.get_candidate("somerset")["astral_candidate_id"] == "somerset"


class TestListCandidatesIncludeDeleted:
    def test_can_include_deleted_rows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [{"state": "NEW_CANDIDATE"}, {"state": "DELETED"}]
        monkeypatch.setattr(candidate_mod.database, "list_candidates", lambda: rows)
        assert candidate_mod.list_candidates(include_deleted=True) == rows


class TestNormalizeRubricArtifactsOnSaveExtended:
    def test_ignores_non_dict_artifacts(self) -> None:
        candidate_mod.normalize_rubric_artifacts_on_save("nope")  # type: ignore[arg-type]

    def test_skips_unknown_keys_and_none_values(self) -> None:
        artifacts: Dict[str, Any] = {"other": [], "company_prefilter": None}
        candidate_mod.normalize_rubric_artifacts_on_save(artifacts)
        assert artifacts["other"] == []

    def test_rejects_non_object_criterion(self) -> None:
        with pytest.raises(ValueError, match="must be an object"):
            candidate_mod.normalize_rubric_artifacts_on_save({"company_prefilter": ["bad"]})

    def test_wraps_grade_table_errors(self) -> None:
        with pytest.raises(ValueError, match="Rubric 'company_prefilter'"):
            candidate_mod.normalize_rubric_artifacts_on_save({"company_prefilter": [_criterion(content="only one line")]})

    def test_wraps_importance_errors(self) -> None:
        with pytest.raises(ValueError, match="importance must be an integer"):
            candidate_mod.normalize_rubric_artifacts_on_save({"company_prefilter": [_criterion(importance=True)]})

    def test_sets_grade_descriptions_and_importance(self) -> None:
        item = _criterion(importance="7")
        candidate_mod.normalize_rubric_artifacts_on_save({"company_prefilter": [item]})
        assert item["grade_descriptions"][0]["grade"] == "A"
        assert item["importance"] == 7


class TestNormalizeImportanceValue:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            (None, 5),
            (8, 8),
            (8.0, 8),
            ("6", 6),
            (0, 1),
            (99, 10),
        ],
    )
    def test_coerces_and_clamps(self, raw: Any, expected: int) -> None:
        assert candidate_mod._normalize_importance_value(raw, _CI) == expected

    @pytest.mark.parametrize(
        "raw",
        [True, 1.5, "high", object()],
    )
    def test_rejects_invalid_values(self, raw: Any) -> None:
        with pytest.raises(ValueError):
            candidate_mod._normalize_importance_value(raw, _CI)


class TestPreviewTaskPrompt:
    def test_requires_existing_candidate_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: None)
        with pytest.raises(ValueError, match="Candidate not found"):
            candidate_mod.preview_task_prompt("craft_resume_base", candidate_id="missing")

    def test_requires_active_candidate_when_id_omitted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "list_candidates", lambda: [])
        with pytest.raises(ValueError, match="No active candidate"):
            candidate_mod.preview_task_prompt("craft_resume_base")

    def test_uses_first_candidate_and_preview_prompt(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "list_candidates", lambda: [{"astral_candidate_id": "somerset", "candidate_data": {}}])
        monkeypatch.setattr(
            candidate_mod,
            "preview_prompt",
            lambda task_key, cd, chain_context=None, job_context=None: {"prompt": task_key},
        )
        out = candidate_mod.preview_task_prompt("craft_resume_base")
        assert out["candidate_id"] == "somerset"
        assert out["prompt"] == "craft_resume_base"

    def test_uses_requested_candidate_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_data": {"context": {}}},
        )
        monkeypatch.setattr(
            candidate_mod,
            "preview_prompt",
            lambda task_key, cd, chain_context=None, job_context=None: {"prompt": task_key},
        )
        out = candidate_mod.preview_task_prompt("craft_resume_base", candidate_id="somerset")
        assert out["candidate_id"] == "somerset"

    def test_chain_sim_overrides_only_passes_chain_context(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "candidate_data": {}},
        )
        captured: dict = {}

        def _pp(task_key: str, cd: dict, chain_context=None, job_context=None):
            captured["chain"] = chain_context
            return {"prompt": task_key}

        monkeypatch.setattr(candidate_mod, "preview_prompt", _pp)
        candidate_mod.preview_task_prompt(
            "craft_resume_base",
            candidate_id="somerset",
            chain_sim_enabled=True,
            chain_overrides={"CALLER_RESPONSE": "hop"},
        )
        assert captured["chain"] == {"CALLER_RESPONSE": "hop"}

    def test_preview_resolves_agent_body_when_system_is_selected_agent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Manage Tasks preview path mirrors production for {$SELECTED_AGENT} tasks (AST-631 AC3)."""
        from src.core import agent as agent_mod

        cd = {"profile": {"first": "Ada"}}
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_data": cd},
        )
        monkeypatch.setattr(
            agent_mod,
            "_resolve_task_prompts",
            lambda task_key: (
                {"content": "Hi, you're Grace. You're helping {$FIRST_NAME} find a great role."},
                {"system_prompt": "{$SELECTED_AGENT}", "user_prompt": "", "cache_prompt": "", "nocache_prompt": ""},
            ),
        )
        out = candidate_mod.preview_task_prompt("craft_resume_base", candidate_id="c1")
        assert "helping Ada find" in out["system"]
        assert "{$FIRST_NAME}" not in out["system"]

    def test_chain_sim_parent_only_merges_simulated_context(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "candidate_data": {}},
        )
        monkeypatch.setattr(
            candidate_mod,
            "simulated_chain_context_for_preview",
            lambda parent, cd, simulate_parsed=None, job_context=None: {"CALLER_RESPONSE": "sim"},
        )
        captured: dict = {}

        def _pp(task_key: str, cd: dict, chain_context=None, job_context=None):
            captured["chain"] = chain_context
            return {"prompt": task_key}

        monkeypatch.setattr(candidate_mod, "preview_prompt", _pp)
        candidate_mod.preview_task_prompt(
            "craft_resume_base",
            candidate_id="c1",
            chain_sim_enabled=True,
            chain_simulate_parent=" parent_task ",
            chain_simulate_parsed='{"jobs": []}',
        )
        assert captured["chain"] == {"CALLER_RESPONSE": "sim"}


class TestDeleteCandidate:
    def test_rejects_missing_candidate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: None)
        with pytest.raises(ValueError, match="Candidate not found"):
            candidate_mod.delete_candidate("missing")

    def test_marks_candidate_deleted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"state": "NEW_CANDIDATE"},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.delete_candidate("somerset")
        # DELETED transition + reap timer merge
        assert save.call_args_list[0].kwargs == {"state": "DELETED"} or save.call_args_list[0].args == (
            "somerset",
        )
        assert any(
            c.kwargs.get("state") == "DELETED" or (len(c.args) >= 2 and c.args[1] == "DELETED")
            for c in save.call_args_list
        )
        # Prefer explicit kwargs form used by transition_candidate_state
        save.assert_any_call("somerset", state="DELETED")
        life_calls = [c for c in save.call_args_list if (c.kwargs.get("candidate_data") or {}).get("lifecycle")]
        assert len(life_calls) == 1
        life = life_calls[0].kwargs["candidate_data"]["lifecycle"]
        assert life["reap_after_hours"] == 720
        assert life["reap_started_at"]


class TestTransitionCandidateStateSuccess:
    def test_saves_allowed_transition(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"state": "NEW_CANDIDATE"},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.transition_candidate_state("somerset", "INTAKE_INITIATED")
        save.assert_called_once_with("somerset", state="INTAKE_INITIATED")


class TestCheckContextCompleteExtended:
    def test_returns_false_when_candidate_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: None)
        assert candidate_mod.check_context_complete("missing") is False

    def test_returns_true_when_already_at_or_past_all_topics_ready(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"state": "ACTIVE_SEARCH"},
        )
        assert candidate_mod.check_context_complete("somerset") is True

    def test_returns_true_when_all_context_fields_present_without_transition(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Completeness helper no longer writes state (AST-970)
        ctx = {key: "filled" for key in candidate_mod._CONTEXT_TEXT_KEYS}
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"state": "INTAKE_INITIATED", "candidate_data": {"context": ctx}},
        )
        transition = MagicMock()
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", transition)
        assert candidate_mod.check_context_complete("somerset") is True
        transition.assert_not_called()

    def test_returns_false_when_context_incomplete_early_state(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {
                "state": "INTAKE_INITIATED",
                "candidate_data": {"context": {"strengths": "only"}},
            },
        )
        assert candidate_mod.check_context_complete("somerset") is False


class TestParseCandidateResumeExtended:
    @pytest.mark.asyncio
    async def test_returns_not_found(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: None)
        out = await candidate_mod.parse_candidate_resume("missing")
        assert out["success"] is False

    @pytest.mark.asyncio
    async def test_handles_none_task_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"candidate_data": {"context": {"starting_resume_text": "resume"}}},
        )
        monkeypatch.setattr(candidate_mod, "do_task", AsyncMock(return_value=None))
        out = await candidate_mod.parse_candidate_resume("somerset")
        assert out["error"] == "do_task returned None for parse_resume"

    @pytest.mark.asyncio
    async def test_returns_task_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"candidate_data": {"context": {"starting_resume_text": "resume"}}},
        )
        monkeypatch.setattr(
            candidate_mod,
            "do_task",
            AsyncMock(return_value={"success": False, "error": "bad", "raw_response": "x"}),
        )
        out = await candidate_mod.parse_candidate_resume("somerset")
        assert out["success"] is False
        assert out["raw_response"] == "x"

    @pytest.mark.asyncio
    async def test_requires_parsed_response(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"candidate_data": {"context": {"starting_resume_text": "resume"}}},
        )
        monkeypatch.setattr(candidate_mod, "do_task", AsyncMock(return_value={"success": True}))
        out = await candidate_mod.parse_candidate_resume("somerset")
        assert out["error"] == "parse_resume returned None parsed_response"

    @pytest.mark.asyncio
    async def test_never_auto_transitions_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        store = {
            "state": "INTAKE_INITIATED",
            "candidate_data": {"context": {"starting_resume_text": "resume"}},
        }
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: dict(store))
        monkeypatch.setattr(candidate_mod.database, "save_candidate", lambda candidate_id, **kwargs: None)
        transition = MagicMock()
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", transition)
        parsed = _craft_resume_base_payload(_three_section_structure(), {"experience": "ok"})
        monkeypatch.setattr(candidate_mod, "do_task", AsyncMock(return_value={"success": True, "parsed_response": parsed}))
        out = await candidate_mod.parse_candidate_resume("somerset")
        assert out["success"] is True
        transition.assert_not_called()


class TestCandidateAdminFacades:
    def test_save_candidate_admin_and_clear_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        clear = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(candidate_mod.database, "clear_candidate_api_key", clear)
        candidate_mod.save_candidate_admin("somerset", state="ACTIVE_SEARCH")
        candidate_mod.clear_candidate_api_key("somerset")
        save.assert_called_once_with("somerset", state="ACTIVE_SEARCH")
        clear.assert_called_once_with("somerset")


class TestRunCandidateArtifactGeneration:
    def test_returns_404_when_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: None)
        body, status = candidate_mod.run_candidate_artifact_generation("missing", "craft_resume_base", "text")
        assert status == 404

    def test_returns_500_on_task_exception(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        monkeypatch.setattr(candidate_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(candidate_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(candidate_mod, "asyncio", MagicMock(run=MagicMock(side_effect=RuntimeError("boom"))))
        body, status = candidate_mod.run_candidate_artifact_generation("somerset", "craft_resume_base", "text")
        assert status == 500
        assert body["success"] is False

    def test_returns_500_on_failed_task(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saves: list = []
        updates: list = []
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        monkeypatch.setattr(
            candidate_mod.database,
            "save_dispatch_ledger",
            lambda *args, **kwargs: saves.append((args, kwargs)),
        )
        monkeypatch.setattr(
            candidate_mod.database,
            "update_dispatch_ledger",
            lambda batch_id, **kwargs: updates.append((batch_id, kwargs)),
        )
        monkeypatch.setattr(candidate_mod, "asyncio", MagicMock(run=MagicMock(return_value={"success": False, "error": "bad"})))
        body, status = candidate_mod.run_candidate_artifact_generation("somerset", "craft_resume_base", "text")
        assert status == 500
        assert body["error"] == "bad"
        assert body["batch_id"].startswith("user-craft_resume_base-")
        assert saves[0][0][1] == "user-craft_resume_base"
        assert updates[-1][1]["status"] == "FAILED"
        assert updates[-1][1]["total_failed"] == 1

    def test_returns_500_when_task_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        monkeypatch.setattr(candidate_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(candidate_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(candidate_mod, "asyncio", MagicMock(run=MagicMock(return_value=None)))
        body, status = candidate_mod.run_candidate_artifact_generation("somerset", "craft_resume_base", "text")
        assert status == 500
        assert body["error"] == "do_task returned None"

    def test_returns_200_on_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        monkeypatch.setattr(candidate_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(candidate_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(candidate_mod.database, "save_candidate", MagicMock())
        monkeypatch.setattr(candidate_mod, "asyncio", MagicMock(run=MagicMock(return_value={"success": True, "parsed_response": {"x": 1}, "timesheet": {"y": 2}})))
        monkeypatch.setattr(candidate_mod, "compute_batch_cost", MagicMock(return_value=1.25))
        body, status = candidate_mod.run_candidate_artifact_generation("somerset", "craft_resume_base", None)
        assert status == 200
        assert body["parsed_response"] == {"x": 1}
        assert body["timesheet"] == {"y": 2}

    def test_persists_artifacts_on_craft_resume_base_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saves: list[tuple[Any, ...]] = []
        parsed = _craft_resume_base_payload(_three_section_structure(), {"experience": "Jobs"})
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        monkeypatch.setattr(candidate_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(candidate_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(candidate_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(
            candidate_mod.database,
            "save_candidate",
            lambda candidate_id, **kwargs: saves.append((candidate_id, kwargs)),
        )
        monkeypatch.setattr(
            candidate_mod,
            "asyncio",
            MagicMock(run=MagicMock(return_value={"success": True, "parsed_response": parsed})),
        )
        body, status = candidate_mod.run_candidate_artifact_generation("karfo", "craft_resume_base", "resume text")
        assert status == 200
        assert body["success"] is True
        assert len(saves) == 1
        assert saves[0][0] == "karfo"
        assert saves[0][1]["merge"] is True
        artifacts = saves[0][1]["candidate_data"]["artifacts"]
        assert "resume_structure" in artifacts
        assert artifacts["base_resume"]["experience"] == "Jobs"

    def test_does_not_persist_artifacts_on_other_task_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saves: list[tuple[Any, ...]] = []
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        monkeypatch.setattr(candidate_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(candidate_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(candidate_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(
            candidate_mod.database,
            "save_candidate",
            lambda candidate_id, **kwargs: saves.append((candidate_id, kwargs)),
        )
        monkeypatch.setattr(
            candidate_mod,
            "asyncio",
            MagicMock(
                run=MagicMock(
                    return_value={
                        "success": True,
                        "parsed_response": {"bio_summary": "x", "strengths": "y", "priorities": "z", "deal_breakers": "a", "backstory": "b"},
                    }
                )
            ),
        )
        body, status = candidate_mod.run_candidate_artifact_generation("karfo", "bootstrap_candidate_context", "text")
        assert status == 200
        assert saves == []


class TestNormalizeCompanySearchTermsOnSave:
    def test_normalizes_multiline_string(self) -> None:
        artifacts: Dict[str, Any] = {"company_search_terms": "  foo \n\n bar  \n"}
        candidate_mod.normalize_company_search_terms_on_save(artifacts)
        assert artifacts["company_search_terms"] == "foo\nbar"

    def test_skips_when_key_absent(self) -> None:
        artifacts: Dict[str, Any] = {"other": "x"}
        candidate_mod.normalize_company_search_terms_on_save(artifacts)
        assert "company_search_terms" not in artifacts

    def test_skips_none_value(self) -> None:
        artifacts: Dict[str, Any] = {"company_search_terms": None}
        candidate_mod.normalize_company_search_terms_on_save(artifacts)
        assert artifacts["company_search_terms"] is None

    def test_rejects_non_string(self) -> None:
        with pytest.raises(ValueError, match="must be a string"):
            candidate_mod.normalize_company_search_terms_on_save({"company_search_terms": ["bad"]})

    def test_rejects_all_blank_lines(self) -> None:
        with pytest.raises(ValueError, match="at least one non-empty"):
            candidate_mod.normalize_company_search_terms_on_save({"company_search_terms": "  \n  \n"})


class TestCompanySearchTermsLines:
    def test_returns_trimmed_non_empty_lines(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "list_company_search_terms",
            lambda cid: [{"search_term": "alpha"}, {"search_term": "beta"}],
        )
        assert candidate_mod.company_search_terms_lines("c1") == ["alpha", "beta"]

    def test_returns_empty_when_table_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "list_company_search_terms", lambda cid: [])
        assert candidate_mod.company_search_terms_lines("c1") == []


class TestAst524CompanySearchTermsTable:
    def test_apply_save_syncs_table_and_strips_artifact_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        synced: list[tuple[str, list[str]]] = []
        monkeypatch.setattr(
            candidate_mod.database,
            "sync_company_search_terms",
            lambda cid, terms: synced.append((cid, list(terms))),
        )
        arts: Dict[str, Any] = {"company_search_terms": "  one \n two "}
        candidate_mod.apply_company_search_terms_save("c524", arts)
        assert "company_search_terms" not in arts
        assert synced == [("c524", ["one", "two"])]

    def test_apply_save_skips_when_key_absent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        sync = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "sync_company_search_terms", sync)
        arts: Dict[str, Any] = {"other": "x"}
        candidate_mod.apply_company_search_terms_save("c524", arts)
        sync.assert_not_called()

    def test_table_backed_lines_and_joined_text(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "list_company_search_terms",
            lambda cid: [{"search_term": "a"}, {"search_term": "b"}],
        )
        assert candidate_mod.company_search_terms_lines_for_candidate("c524") == ["a", "b"]
        assert candidate_mod.company_search_terms_joined_text("c524") == "a\nb"


# Branches: default copy; normalize valid/invalid; resolve stored/default/shim; split payload; parse isolation.
class TestAst517ResumeStructure:
    def test_default_resume_structure_deep_copy(self) -> None:
        first = candidate_mod.default_resume_structure()
        second = candidate_mod.default_resume_structure()
        first["sections"]["experience"]["title"] = "mutated"
        assert second["sections"]["experience"]["title"] == "Experience"
        assert set(first["sections"]) == set(RESUME_STRUCTURE_KNOWN_SECTION_IDS)

    def test_normalize_accepts_valid_structure_with_accent(self) -> None:
        raw = _three_section_structure()
        raw["accent_color"] = _VALID_ACCENT.lower()
        out = candidate_mod.normalize_resume_structure(raw)
        assert out["accent_color"] == _VALID_ACCENT
        assert out["sections"]["experience"]["title"] == "Custom Jobs"

    @pytest.mark.parametrize(
        ("raw", "match"),
        [
            ("bad", "resume_structure must be a dict"),
            ({}, "sections must be a non-empty dict"),
            ({"sections": {}}, "sections must be a non-empty dict"),
            ({"sections": {"bad_id": {}}}, "unknown resume section id"),
            ({"sections": {"experience": "x"}}, "section experience must be a dict"),
            (
                {"sections": {"experience": {"id": "wrong", "title": "T", "enabled": True, "order": 0, "job_agent_editable": True}}},
                "section id mismatch",
            ),
            (
                {"sections": {"experience": {"id": "experience", "title": " ", "enabled": True, "order": 0, "job_agent_editable": True}}},
                "requires non-empty title",
            ),
            (
                {"sections": {"experience": {"id": "experience", "title": "T", "enabled": "yes", "order": 0, "job_agent_editable": True}}},
                "enabled must be boolean",
            ),
            (
                {"sections": {"experience": {"id": "experience", "title": "T", "enabled": True, "order": "0", "job_agent_editable": True}}},
                "order must be int",
            ),
            (
                {"sections": {"experience": {"id": "experience", "title": "T", "enabled": True, "order": 0, "job_agent_editable": "no"}}},
                "job_agent_editable must be boolean",
            ),
            (
                {"sections": {"experience": {"id": "experience", "title": "T", "enabled": True, "order": 0, "job_agent_editable": True}}, "accent_color": "red"},
                "accent_color must be #RRGGBB",
            ),
            (
                {"sections": {"experience": {"id": "experience", "title": "T", "enabled": True, "order": 0, "job_agent_editable": True}}, "accent_color": "#ABCDEF"},
                "accent_color not in accent_palette",
            ),
        ],
    )
    def test_normalize_rejects_invalid_structure(self, raw: Any, match: str) -> None:
        with pytest.raises(ValueError, match=match):
            candidate_mod.normalize_resume_structure(raw)

    def test_resolve_returns_stored_structure(self) -> None:
        stored = _three_section_structure()
        out = candidate_mod.resolve_resume_structure({"artifacts": {"resume_structure": stored}})
        assert out["sections"]["technical_skills"]["title"] == "Custom Skills"

    def test_resolve_falls_back_to_default_when_invalid(self) -> None:
        out = candidate_mod.resolve_resume_structure({"artifacts": {"resume_structure": {"sections": {"nope": {}}}}})
        assert out["sections"]["candidate_name"]["title"] == "Candidate Name"

    def test_resolve_shims_legacy_base_resume_accent(self) -> None:
        out = candidate_mod.resolve_resume_structure(
            {"artifacts": {"base_resume": {"accent_color": _VALID_ACCENT.lower(), "professional_summary": "x"}}}
        )
        assert out["accent_color"] == _VALID_ACCENT

    def test_resolve_ignores_invalid_legacy_accent(self) -> None:
        out = candidate_mod.resolve_resume_structure({"artifacts": {"base_resume": {"accent_color": "not-hex"}}})
        assert "accent_color" not in out

    def test_split_uses_default_when_structure_missing(self) -> None:
        structure, content = candidate_mod.split_craft_resume_base_payload({"professional_summary": "only body"})
        assert "candidate_name" in structure["sections"]
        assert content == {"professional_summary": "only body"}

    def test_split_filters_disabled_sections_from_content(self) -> None:
        structure = _three_section_structure()
        structure["sections"]["technical_skills"]["enabled"] = False
        parsed = _craft_resume_base_payload(structure, {"technical_skills": "skip", "experience": "keep"})
        _, content = candidate_mod.split_craft_resume_base_payload(parsed)
        assert "technical_skills" not in content
        assert content["experience"] == "keep"

    def test_split_skips_non_string_section_values(self) -> None:
        structure = _three_section_structure()
        parsed = _craft_resume_base_payload(structure)
        parsed["technical_skills"] = 99
        _, content = candidate_mod.split_craft_resume_base_payload(parsed)
        assert "technical_skills" not in content

    def test_split_omits_enabled_sections_absent_from_payload(self) -> None:
        structure = _three_section_structure()
        parsed = {"resume_structure": structure, "experience": "only this"}
        _, content = candidate_mod.split_craft_resume_base_payload(parsed)
        assert content == {"experience": "only this"}

    def test_split_rejects_non_dict_payload(self) -> None:
        with pytest.raises(ValueError, match="must be a dict"):
            candidate_mod.split_craft_resume_base_payload([])  # type: ignore[arg-type]

    def test_normalize_flattens_nested_section_content_onto_top_level(self) -> None:
        structure = candidate_mod.default_resume_structure()
        sections = {
            sid: {**spec, "content": f"nested-{sid}"}
            for sid, spec in structure["sections"].items()
        }
        parsed: dict[str, Any] = {"agent_payload": {"resume_structure": {"sections": sections}}}
        candidate_mod.normalize_craft_resume_base_agent_payload(parsed)
        ap = parsed["agent_payload"]
        assert ap["candidate_name"] == "nested-candidate_name"
        assert ap["experience"] == "nested-experience"

    def test_normalize_flattens_resume_structure_content_dict(self) -> None:
        structure = candidate_mod.default_resume_structure()
        parsed: dict[str, Any] = {
            "agent_payload": {
                "resume_structure": {
                    "sections": structure["sections"],
                    "content": {
                        "candidate_name": "Ada Lovelace",
                        "professional_summary": "Summary text",
                    },
                }
            }
        }
        candidate_mod.normalize_craft_resume_base_agent_payload(parsed)
        ap = parsed["agent_payload"]
        assert ap["candidate_name"] == "Ada Lovelace"
        assert ap["professional_summary"] == "Summary text"

    def test_normalize_allows_schema_validation_for_structure_heavy_payload(self) -> None:
        from src.core.agent import _validate_response_schema
        from src.utils.config import TASK_CONFIG

        structure = candidate_mod.default_resume_structure()
        sections = {
            sid: {**spec, "content": f"body-{sid}"}
            for sid, spec in structure["sections"].items()
        }
        parsed: dict[str, Any] = {"agent_payload": {"resume_structure": {"sections": sections}}}
        candidate_mod.normalize_craft_resume_base_agent_payload(parsed)
        schema = TASK_CONFIG["craft_resume_base"]["response_schema"]
        assert _validate_response_schema(parsed, schema, "craft_resume_base") is None

    def test_normalize_injects_default_when_resume_structure_missing(self) -> None:
        from src.core.agent import _validate_response_schema
        from src.utils.config import TASK_CONFIG

        parsed: dict[str, Any] = {
            "agent_performance": {"status": "success"},
            "agent_payload": {
                "candidate_name": "Kar Fo",
                "candidate_title": "Engineer",
                "candidate_contact_detail": "kar@example.com",
                "professional_summary": "Summary",
                "core_competencies": "Skills",
                "experience": "Jobs",
            },
        }
        candidate_mod.normalize_craft_resume_base_agent_payload(parsed)
        ap = parsed["agent_payload"]
        assert "candidate_name" in ap["resume_structure"]["sections"]
        schema = TASK_CONFIG["craft_resume_base"]["response_schema"]
        assert _validate_response_schema(parsed, schema, "craft_resume_base") is None

    def test_normalize_injects_default_when_resume_structure_sections_empty(self) -> None:
        from src.core.agent import _validate_response_schema
        from src.utils.config import TASK_CONFIG

        parsed: dict[str, Any] = {
            "agent_performance": {"status": "success"},
            "agent_payload": {
                "resume_structure": {"sections": {}},
                "candidate_name": "Kar Fo",
                "candidate_title": "Engineer",
                "candidate_contact_detail": "kar@example.com",
                "professional_summary": "Summary",
                "core_competencies": "Skills",
                "experience": "Jobs",
            },
        }
        candidate_mod.normalize_craft_resume_base_agent_payload(parsed)
        ap = parsed["agent_payload"]
        assert "candidate_name" in ap["resume_structure"]["sections"]
        schema = TASK_CONFIG["craft_resume_base"]["response_schema"]
        assert _validate_response_schema(parsed, schema, "craft_resume_base") is None

    def test_normalize_preserves_valid_custom_resume_structure(self) -> None:
        custom = _three_section_structure()
        parsed: dict[str, Any] = {
            "agent_payload": {
                "resume_structure": custom,
                "candidate_name": "Ada",
                "candidate_title": "Eng",
                "candidate_contact_detail": "a@b.c",
                "professional_summary": "S",
                "core_competencies": "C",
                "experience": "E",
            }
        }
        candidate_mod.normalize_craft_resume_base_agent_payload(parsed)
        assert parsed["agent_payload"]["resume_structure"]["sections"]["experience"]["title"] == "Custom Jobs"

    def test_split_promotes_nested_section_content(self) -> None:
        structure = _three_section_structure()
        sections = {
            sid: {**spec, "content": f"nested-{sid}"}
            for sid, spec in structure["sections"].items()
        }
        parsed = {"resume_structure": {"sections": sections}}
        _, content = candidate_mod.split_craft_resume_base_payload(parsed)
        assert content["experience"] == "nested-experience"

    @pytest.mark.asyncio
    async def test_parse_persists_custom_structure_per_candidate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        stores: dict[str, dict] = {
            "cand-a": {"state": "NEW", "candidate_data": {"context": {"starting_resume_text": "a"}}},
            "cand-b": {"state": "NEW", "candidate_data": {"context": {"starting_resume_text": "b"}}},
        }
        struct_a = _three_section_structure()
        struct_b = _three_section_structure()
        struct_b["sections"]["experience"]["title"] = "Other Jobs"

        async def _do_task(**kwargs):
            cid = kwargs.get("index")
            struct = struct_a if cid == "cand-a" else struct_b
            return {"success": True, "parsed_response": _craft_resume_base_payload(struct)}

        def _save(candidate_id: str, **kwargs):
            cd = kwargs.get("candidate_data") or {}
            if cd:
                stores[candidate_id]["candidate_data"] = {
                    **stores[candidate_id]["candidate_data"],
                    **cd,
                }

        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: dict(stores[candidate_id]))
        monkeypatch.setattr(candidate_mod.database, "save_candidate", _save)
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", lambda *args, **kwargs: None)
        monkeypatch.setattr(candidate_mod, "do_task", _do_task)

        assert (await candidate_mod.parse_candidate_resume("cand-a"))["success"] is True
        assert (await candidate_mod.parse_candidate_resume("cand-b"))["success"] is True

        a_title = stores["cand-a"]["candidate_data"]["artifacts"]["resume_structure"]["sections"]["experience"]["title"]
        b_title = stores["cand-b"]["candidate_data"]["artifacts"]["resume_structure"]["sections"]["experience"]["title"]
        assert a_title == "Custom Jobs"
        assert b_title == "Other Jobs"

    def test_contact_sections_not_job_agent_editable_in_default(self) -> None:
        sections = candidate_mod.default_resume_structure()["sections"]
        for sid in RESUME_STRUCTURE_CONTACT_SECTION_IDS:
            assert sections[sid]["job_agent_editable"] is False


class TestAst518ResumeStructureProjection:
    """AST-518: structure projection helpers for builder and tracker."""

    def test_enabled_resume_section_ids_sorted_by_order(self) -> None:
        structure = _three_section_structure()
        assert candidate_mod.enabled_resume_section_ids(structure) == [
            "professional_summary",
            "experience",
            "technical_skills",
        ]

    def test_resume_section_titles_for_enabled_sections(self) -> None:
        titles = candidate_mod.resume_section_titles(_three_section_structure())
        assert titles["experience"] == "Custom Jobs"

    def test_filter_content_drops_orphan_and_empty_strings(self) -> None:
        structure = _three_section_structure()
        out = candidate_mod.filter_content_to_resume_structure(
            {"experience": "ok", "orphan_section": "drop", "technical_skills": "  "},
            structure,
        )
        assert out == {"experience": "ok"}

    def test_filter_content_excludes_contact_when_allow_contact_false(self) -> None:
        structure = candidate_mod.default_resume_structure()
        out = candidate_mod.filter_content_to_resume_structure(
            {
                "candidate_name": "Ada",
                "professional_summary": "Body",
            },
            structure,
            allow_contact=False,
        )
        assert "candidate_name" not in out
        assert out.get("professional_summary") == "Body"


# Branches: enabled list projection; base_resume key filter for API/UI.
class TestAst519ResumeStructureUiHelpers:
    def test_enabled_resume_structure_sections_sorted_and_labeled(self) -> None:
        structure = _three_section_structure()
        structure["sections"]["experience"]["enabled"] = False
        out = candidate_mod.enabled_resume_structure_sections(structure)
        assert out == [
            {"id": "professional_summary", "label": "Custom Summary"},
            {"id": "technical_skills", "label": "Custom Skills"},
        ]

    def test_filter_base_resume_to_structure_drops_orphans_and_accent(self) -> None:
        section_ids = {"professional_summary", "technical_skills"}
        raw = {
            "professional_summary": "body",
            "orphan_section": "drop",
            "accent_color": "#112233",
            "technical_skills": 99,
        }
        assert candidate_mod.filter_base_resume_to_structure(raw, section_ids) == {
            "professional_summary": "body",
            "technical_skills": "99",
        }

    def test_filter_base_resume_to_structure_non_dict_returns_empty(self) -> None:
        assert candidate_mod.filter_base_resume_to_structure([], {"x"}) == {}


class TestAst607BaseResumeToken:
    """AST-607: {$BASE_RESUME} injects section-id JSON, not markdown label sections."""

    def test_format_dict_keys_as_json_not_markdown(self) -> None:
        structure = candidate_mod.default_resume_structure()
        cd = {
            "artifacts": {
                "resume_structure": structure,
                "base_resume": {
                    "professional_summary": "Summary body",
                    "accent_color": "#112233",
                },
            }
        }
        out = candidate_mod.format_base_resume_for_token(cd)
        assert "###" not in out
        parsed = json.loads(out)
        assert parsed["professional_summary"] == "Summary body"
        assert "accent_color" not in parsed

    def test_format_legacy_label_list_maps_to_section_ids(self) -> None:
        structure = candidate_mod.default_resume_structure()
        summary_title = structure["sections"]["professional_summary"]["title"]
        cd = {
            "artifacts": {
                "resume_structure": structure,
                "base_resume": [{"label": summary_title, "content": "Legacy summary"}],
            }
        }
        out = candidate_mod.format_base_resume_for_token(cd)
        assert "###" not in out
        assert json.loads(out)["professional_summary"] == "Legacy summary"


class TestAst594DraftJobResumePayload:
    """AST-594: normalize + catalog validation for draft_job_resume section payloads."""

    def test_validate_accepts_structure_keyed_subset(self) -> None:
        payload = {"professional_summary": "Summary", "experience": "Jobs"}
        assert candidate_mod.validate_draft_job_resume_payload(payload, {}) is None

    def test_validate_rejects_unknown_section_key(self) -> None:
        err = candidate_mod.validate_draft_job_resume_payload({"made_up_section": "x"}, {})
        assert err is not None
        assert "Unknown resume section key" in err
        assert "made_up_section" in err

    def test_validate_rejects_grades_field(self) -> None:
        err = candidate_mod.validate_draft_job_resume_payload({"grades": []}, {})
        assert err is not None
        assert "grades" in err

    def test_normalize_promotes_nested_content_dict(self) -> None:
        parsed = {"agent_payload": {"content": {"professional_summary": "x"}}}
        candidate_mod.normalize_draft_job_resume_agent_payload(parsed)
        assert parsed["agent_payload"]["professional_summary"] == "x"

    def test_normalize_flattens_resume_structure_wrapper(self) -> None:
        structure = candidate_mod.default_resume_structure()
        sections = {
            sid: {**spec, "content": f"nested-{sid}"}
            for sid, spec in structure["sections"].items()
        }
        parsed: dict[str, Any] = {"agent_payload": {"resume_structure": {"sections": sections}}}
        candidate_mod.normalize_draft_job_resume_agent_payload(parsed)
        ap = parsed["agent_payload"]
        assert ap["professional_summary"] == "nested-professional_summary"

    def test_normalize_renames_candidate_contact_alias(self) -> None:
        parsed = {"agent_payload": {"candidate_contact": "ada@example.com"}}
        candidate_mod.normalize_draft_job_resume_agent_payload(parsed)
        ap = parsed["agent_payload"]
        assert "candidate_contact" not in ap
        assert ap["candidate_contact_detail"] == "ada@example.com"
        assert candidate_mod.validate_draft_job_resume_payload(ap, {}) is None


class TestAst723RubricVectorsCutover:
    def test_apply_save_syncs_table_and_strips_artifact_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        synced: list[tuple[str, str, list]] = []
        monkeypatch.setattr(
            candidate_mod.database,
            "sync_rubric_vectors_from_criteria",
            lambda cid, owner, val: synced.append((cid, owner, list(val))),
        )
        criteria = [{"code": "CR", "label": "fit", "content": "line", "importance": 5}]
        arts: Dict[str, Any] = {"joblist_rubric": criteria}
        candidate_mod.apply_rubric_vectors_save("c723", arts)
        assert "joblist_rubric" not in arts
        assert synced == [("c723", "qualify_job_listings", criteria)]

    def test_hydrate_overlays_table_backed_artifacts(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod,
            "rubric_criteria_for_task",
            lambda cid, owner: [{"code": "CR", "content": "x", "importance": 5}] if owner == "qualify_job_listings" else [],
        )
        cd: Dict[str, Any] = {"artifacts": {"base_resume": "keep"}}
        candidate_mod.hydrate_rubric_artifacts_for_response("c723", cd)
        assert cd["artifacts"]["joblist_rubric"][0]["code"] == "CR"
        assert cd["artifacts"]["base_resume"] == "keep"

    def test_prefilter_merges_embedded_rc_from_table(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("prefilter_company", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1",
            "prefilter_company",
            [
                {
                    "code": "MP",
                    "label": "Mission",
                    "content": "Mission body",
                    "importance": 5,
                }
            ],
        )
        rubric = candidate_mod.rubric_criteria_for_task("cand-1", "prefilter_company")
        assert rubric[0]["code"] == "RC"
        assert rubric[0]["label"] == "Reality Check"
        assert any(r["code"] == "MP" for r in rubric)

    def test_preview_injects_astral_candidate_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_data": {}},
        )
        captured: dict = {}

        def _pp(task_key: str, cd: dict, chain_context=None, job_context=None):
            captured["cd"] = cd
            return {"prompt": task_key}

        monkeypatch.setattr(candidate_mod, "preview_prompt", _pp)
        candidate_mod.preview_task_prompt("craft_joblist_rubric", candidate_id="c723")
        assert captured["cd"]["_astral_candidate_id"] == "c723"


class TestAst901CraftRubricGenerateDelivery:
    """AST-901: pending stash, empty-criteria guard, recovery (stash / ledger)."""

    _CRITERIA = [{"code": "GT", "label": "get", "content": "line", "importance": 5}]

    def _stub_generate_common(self, monkeypatch: pytest.MonkeyPatch, store: dict[str, Any]) -> list:
        saves: list[tuple[Any, ...]] = []
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: dict(store) if store.get("astral_candidate_id") == candidate_id else None,
        )
        monkeypatch.setattr(candidate_mod.database, "save_dispatch_ledger", MagicMock())
        monkeypatch.setattr(candidate_mod.database, "update_dispatch_ledger", MagicMock())
        monkeypatch.setattr(candidate_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(
            candidate_mod.database,
            "save_candidate",
            lambda candidate_id, **kwargs: saves.append((candidate_id, kwargs)),
        )
        return saves

    def test_craft_get_rubric_success_stashes_pending_not_artifact(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        store = {"astral_candidate_id": "karfo", "candidate_data": {}}
        saves = self._stub_generate_common(monkeypatch, store)
        parsed = {"criteria": list(self._CRITERIA)}
        monkeypatch.setattr(
            candidate_mod,
            "asyncio",
            MagicMock(run=MagicMock(return_value={"success": True, "parsed_response": parsed})),
        )
        body, status = candidate_mod.run_candidate_artifact_generation(
            "karfo", "craft_get_rubric", None,
        )
        assert status == 200
        assert body["success"] is True
        assert body["parsed_response"] == parsed
        assert len(saves) == 1
        pending = saves[0][1]["candidate_data"]["pending_craft_generations"]["craft_get_rubric"]
        assert pending["parsed_response"] == parsed
        assert pending["batch_id"].startswith("user-craft_get_rubric-")
        assert "artifacts" not in saves[0][1].get("candidate_data", {})

    def test_empty_criteria_fails_ledger_and_skips_stash(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        store = {"astral_candidate_id": "karfo", "candidate_data": {}}
        saves = self._stub_generate_common(monkeypatch, store)
        updates: list = []
        monkeypatch.setattr(
            candidate_mod.database,
            "update_dispatch_ledger",
            lambda batch_id, **kwargs: updates.append((batch_id, kwargs)),
        )
        monkeypatch.setattr(
            candidate_mod,
            "asyncio",
            MagicMock(run=MagicMock(return_value={"success": True, "parsed_response": {"criteria": []}})),
        )
        body, status = candidate_mod.run_candidate_artifact_generation(
            "karfo", "craft_get_rubric", None,
        )
        assert status == 500
        assert body["success"] is False
        assert body["error"] == "Generation returned no criteria"
        assert saves == []
        assert updates[-1][1]["status"] == "FAILED"

    def test_get_pending_from_stash(self, monkeypatch: pytest.MonkeyPatch) -> None:
        parsed = {"criteria": list(self._CRITERIA)}
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {
                "astral_candidate_id": candidate_id,
                "candidate_data": {
                    "pending_craft_generations": {
                        "craft_get_rubric": {
                            "batch_id": "user-craft_get_rubric-abc",
                            "parsed_response": parsed,
                        }
                    }
                },
            },
        )
        body, status = candidate_mod.get_pending_craft_generation("karfo", "craft_get_rubric")
        assert status == 200
        assert body["source"] == "pending_stash"
        assert body["recovered"] is True
        assert body["parsed_response"] == parsed
        assert body["batch_id"] == "user-craft_get_rubric-abc"

    def test_get_pending_ledger_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        parsed = {"criteria": list(self._CRITERIA)}
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_data": {}},
        )
        monkeypatch.setattr(
            "src.core.dispatcher.list_dispatch_ledger",
            lambda **kwargs: [{"batch_id": "user-craft_get_rubric-ledger1"}],
        )
        monkeypatch.setattr(
            candidate_mod,
            "get_entity_response",
            lambda batch_id, entity_id: {"block_data": json.dumps(parsed)},
        )
        body, status = candidate_mod.get_pending_craft_generation("karfo", "craft_get_rubric")
        assert status == 200
        assert body["source"] == "ledger_agent_data"
        assert body["batch_id"] == "user-craft_get_rubric-ledger1"
        assert body["parsed_response"] == parsed

    def test_get_pending_rejects_non_rubric_and_missing(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        body, status = candidate_mod.get_pending_craft_generation("karfo", "craft_resume_base")
        assert status == 400
        assert "craft rubric" in body["error"].lower()
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: None)
        body, status = candidate_mod.get_pending_craft_generation("missing", "craft_get_rubric")
        assert status == 404

    def test_clear_pending_removes_task_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        store = {
            "astral_candidate_id": "karfo",
            "candidate_data": {
                "pending_craft_generations": {
                    "craft_get_rubric": {"batch_id": "b1", "parsed_response": {"criteria": self._CRITERIA}},
                    "craft_do_rubric": {"batch_id": "b2", "parsed_response": {"criteria": self._CRITERIA}},
                }
            },
        }
        saves: list = []
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: dict(store))
        monkeypatch.setattr(
            candidate_mod.database,
            "save_candidate",
            lambda candidate_id, **kwargs: saves.append((candidate_id, kwargs)),
        )
        candidate_mod._clear_pending_craft_generation("karfo", "craft_get_rubric")
        assert len(saves) == 1
        assert saves[0][1]["merge"] is False
        pending = saves[0][1]["candidate_data"]["pending_craft_generations"]
        assert "craft_get_rubric" not in pending
        assert "craft_do_rubric" in pending


class TestAst905RecoverOnlyWhenEmpty:
    """AST-905: pending recovery 404 when stored rubric criteria already exist."""

    _CRITERIA = [{"code": "GT", "label": "get", "content": "line", "importance": 5}]
    _STASHED = {
        "batch_id": "user-craft_get_rubric-abc",
        "parsed_response": {"criteria": [{"code": "GT", "label": "get", "content": "stash", "importance": 5}]},
    }

    def test_get_pending_404_when_stored_rubric_nonempty(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {
                "astral_candidate_id": candidate_id,
                "candidate_data": {"pending_craft_generations": {"craft_get_rubric": dict(self._STASHED)}},
            },
        )
        monkeypatch.setattr(
            candidate_mod,
            "rubric_criteria_for_task",
            lambda candidate_id, owner: list(self._CRITERIA),
        )
        body, status = candidate_mod.get_pending_craft_generation("karfo", "craft_get_rubric")
        assert status == 404
        assert body["error"] == "No recoverable generation"

    def test_get_pending_ok_when_stored_rubric_empty(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {
                "astral_candidate_id": candidate_id,
                "candidate_data": {"pending_craft_generations": {"craft_get_rubric": dict(self._STASHED)}},
            },
        )
        monkeypatch.setattr(candidate_mod, "rubric_criteria_for_task", lambda candidate_id, owner: [])
        body, status = candidate_mod.get_pending_craft_generation("karfo", "craft_get_rubric")
        assert status == 200
        assert body["source"] == "pending_stash"
        assert body["recovered"] is True


# AST-970: prior_states enforcement, DELETED reap, stale aging helper
class TestAst970CandidateStateMachine:
    _HAPPY = (
        "NEW_CANDIDATE",
        "INTAKE_INITIATED",
        "REQUIRED_TOPICS_READY",
        "ALL_TOPICS_READY",
        "REQUESTED_RESUME",
        "RESUME_READY",
        "REQUESTED_ARTIFACTS",
        "ARTIFACTS_READY",
        "ACTIVE_SEARCH",
    )

    def test_happy_path_hops_succeed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        state = {"cur": "NEW_CANDIDATE"}
        saves: list[str] = []

        def _get(_cid):
            return {"state": state["cur"]}

        def _save(_cid, **kwargs):
            if "state" in kwargs:
                state["cur"] = kwargs["state"]
                saves.append(kwargs["state"])

        monkeypatch.setattr(candidate_mod.database, "get_candidate", _get)
        monkeypatch.setattr(candidate_mod.database, "save_candidate", _save)
        for nxt in self._HAPPY[1:]:
            candidate_mod.transition_candidate_state("somerset", nxt)
        assert saves == list(self._HAPPY[1:])
        assert state["cur"] == "ACTIVE_SEARCH"

    def test_manual_topic_ready_from_intake(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "INTAKE_INITIATED"},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.transition_candidate_state("somerset", "REQUIRED_TOPICS_READY")
        save.assert_called_once_with("somerset", state="REQUIRED_TOPICS_READY")

    def test_stale_companion_may_advance_to_next(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "REQUIRED_TOPICS_READY_STALE"},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.transition_candidate_state("somerset", "ALL_TOPICS_READY")
        save.assert_called_once_with("somerset", state="ALL_TOPICS_READY")

    def test_inactive_and_deleted_from_any_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "REQUESTED_RESUME_ERROR"},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.transition_candidate_state("somerset", "INACTIVE")
        save.assert_called_once_with("somerset", state="INACTIVE")

    def test_error_state_has_no_forward_happy_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "REQUESTED_RESUME_ERROR"},
        )
        with pytest.raises(ValueError, match="Invalid candidate state transition"):
            candidate_mod.transition_candidate_state("somerset", "RESUME_READY")

    def test_deleted_starts_reap_timer(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "ACTIVE_SEARCH"},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.transition_candidate_state("somerset", "DELETED")
        save.assert_any_call("somerset", state="DELETED")
        life = next(
            c.kwargs["candidate_data"]["lifecycle"]
            for c in save.call_args_list
            if (c.kwargs.get("candidate_data") or {}).get("lifecycle")
        )
        assert life["reap_after_hours"] == CANDIDATE_STATES["DELETED"]["reap_after_hours"]
        assert life["reap_started_at"]

    def test_reap_due_helpers(self) -> None:
        started = datetime(2026, 1, 1, tzinfo=timezone.utc)
        cand = {
            "state": "DELETED",
            "candidate_data": {
                "lifecycle": {
                    "reap_after_hours": 720,
                    "reap_started_at": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            },
        }
        due = candidate_mod.candidate_reap_due_at(cand)
        assert due == started + timedelta(hours=720)
        assert candidate_mod.is_candidate_reap_due(cand, now=started + timedelta(hours=719)) is False
        assert candidate_mod.is_candidate_reap_due(cand, now=started + timedelta(hours=720)) is True
        assert candidate_mod.candidate_reap_due_at({"state": "ACTIVE_SEARCH"}) is None

    def test_age_stale_moves_due_waiting_rows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        old = (datetime.now(timezone.utc) - timedelta(hours=80)).strftime("%Y-%m-%dT%H:%M:%SZ")
        rows = [
            {
                "astral_candidate_id": "due",
                "state": "REQUIRED_TOPICS_READY",
                "state_changed_at": old,
            },
            {
                "astral_candidate_id": "fresh",
                "state": "REQUIRED_TOPICS_READY",
                "state_changed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            {
                "astral_candidate_id": "already",
                "state": "REQUIRED_TOPICS_READY_STALE",
                "state_changed_at": old,
            },
        ]
        monkeypatch.setattr(candidate_mod, "list_candidates", lambda include_deleted=False: rows)
        moved: list[tuple[str, str]] = []

        def _transition(cid, to_state):
            moved.append((cid, to_state))

        monkeypatch.setattr(candidate_mod, "transition_candidate_state", _transition)
        assert candidate_mod.age_stale_candidate_states() == 1
        assert moved == [("due", "REQUIRED_TOPICS_READY_STALE")]

    def test_pause_search_round_trip(self, monkeypatch: pytest.MonkeyPatch) -> None:
        state = {"cur": "ACTIVE_SEARCH"}
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda _cid: {"state": state["cur"]})

        def _save(_cid, **kwargs):
            if "state" in kwargs:
                state["cur"] = kwargs["state"]

        monkeypatch.setattr(candidate_mod.database, "save_candidate", _save)
        candidate_mod.transition_candidate_state("somerset", "PAUSE_SEARCH")
        candidate_mod.transition_candidate_state("somerset", "ACTIVE_SEARCH")
        assert state["cur"] == "ACTIVE_SEARCH"
