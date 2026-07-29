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


# AST-996: craft-base Experience wire shape (shared fixture for schema-valid payloads).
_SAMPLE_EXPERIENCE_JOBS: list[dict[str, str]] = [
    {
        "company": "Acme Corp",
        "title": "Engineer",
        "dates": "2020-2023",
        "location": "Remote",
        "accomplishments": "Shipped widgets",
    },
    {
        "company": "Beta LLC",
        "title": "Lead",
        "dates": "2023",
        "location": "",
        "accomplishments": "Led the team",
    },
]


def _craft_resume_base_payload(
    structure: dict, content: dict[str, Any] | None = None
) -> dict[str, Any]:
    payload: dict[str, Any] = {"resume_structure": structure}
    for sid, spec in structure["sections"].items():
        if not spec.get("enabled"):
            continue
        if content is not None and sid in content:
            payload[sid] = content[sid]
        elif sid == "experience":
            payload[sid] = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        else:
            payload[sid] = f"content-{sid}"
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
        hist = saved[0][1]["state_history"]
        assert len(hist) == 1
        assert hist[0]["from_state"] == ""
        assert hist[0]["to_state"] == "NEW_CANDIDATE"
        assert hist[0]["batch_id"] is None
        assert "timestamp" in hist[0]


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
            "candidate_data": {"context": {"raw_resume": "resume body"}},
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

        cd = {"first": "Ada", "contact": {}, "context": {}, "artifacts": {}}
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "first": "Ada", "candidate_data": cd},
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
            lambda candidate_id: {"state": "NEW_CANDIDATE", "state_history": []},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.delete_candidate("somerset")
        # DELETED transition (state + history) + reap timer merge
        deleted = [c for c in save.call_args_list if c.kwargs.get("state") == "DELETED"]
        assert len(deleted) == 1
        assert deleted[0].kwargs["state_history"][-1]["to_state"] == "DELETED"
        assert deleted[0].kwargs["state_history"][-1]["from_state"] == "NEW_CANDIDATE"
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
            lambda candidate_id: {"state": "NEW_CANDIDATE", "state_history": []},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.transition_candidate_state("somerset", "INTAKE_INITIATED")
        assert save.call_count == 1
        assert save.call_args.kwargs["state"] == "INTAKE_INITIATED"
        assert save.call_args.kwargs["state_history"][-1]["from_state"] == "NEW_CANDIDATE"
        assert save.call_args.kwargs["state_history"][-1]["to_state"] == "INTAKE_INITIATED"


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
            lambda candidate_id: {"candidate_data": {"context": {"raw_resume": "resume"}}},
        )
        monkeypatch.setattr(candidate_mod, "do_task", AsyncMock(return_value=None))
        out = await candidate_mod.parse_candidate_resume("somerset")
        assert out["error"] == "do_task returned None for parse_resume"

    @pytest.mark.asyncio
    async def test_returns_task_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"candidate_data": {"context": {"raw_resume": "resume"}}},
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
            lambda candidate_id: {"candidate_data": {"context": {"raw_resume": "resume"}}},
        )
        monkeypatch.setattr(candidate_mod, "do_task", AsyncMock(return_value={"success": True}))
        out = await candidate_mod.parse_candidate_resume("somerset")
        assert out["error"] == "parse_resume returned None parsed_response"

    @pytest.mark.asyncio
    async def test_never_auto_transitions_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        store = {
            "state": "INTAKE_INITIATED",
            "candidate_data": {"context": {"raw_resume": "resume"}},
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
        # Nested section.content strings for scalars; experience jobs via content dict
        # (section.content job arrays are not promoted — top-level / content-dict heal only).
        content = {
            sid: f"body-{sid}"
            for sid in structure["sections"]
            if sid != "experience"
        }
        content["experience"] = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        parsed: dict[str, Any] = {
            "agent_payload": {
                "resume_structure": {"sections": structure["sections"], "content": content}
            }
        }
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
                "experience": [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS],
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
                "experience": [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS],
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
            "cand-a": {"state": "NEW_CANDIDATE", "candidate_data": {"context": {"raw_resume": "a"}}},
            "cand-b": {"state": "NEW_CANDIDATE", "candidate_data": {"context": {"raw_resume": "b"}}},
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
        section_ids = {"professional_summary", "technical_skills", "experience"}
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        raw = {
            "professional_summary": "body",
            "orphan_section": "drop",
            "accent_color": "#112233",
            "technical_skills": 99,  # non-str / non-job-array → drop (no str()-corrupt)
            "experience": jobs,
        }
        assert candidate_mod.filter_base_resume_to_structure(raw, section_ids) == {
            "professional_summary": "body",
            "experience": jobs,
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
        state = {"cur": "NEW_CANDIDATE", "hist": []}
        saves: list[str] = []

        def _get(_cid):
            return {"state": state["cur"], "state_history": list(state["hist"])}

        def _save(_cid, **kwargs):
            if "state" in kwargs:
                state["cur"] = kwargs["state"]
                saves.append(kwargs["state"])
            if "state_history" in kwargs:
                state["hist"] = list(kwargs["state_history"])

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
            lambda _cid: {"state": "INTAKE_INITIATED", "state_history": []},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.transition_candidate_state("somerset", "REQUIRED_TOPICS_READY")
        assert save.call_args.kwargs["state"] == "REQUIRED_TOPICS_READY"
        assert save.call_args.kwargs["state_history"][-1]["to_state"] == "REQUIRED_TOPICS_READY"

    def test_stale_companion_may_advance_to_next(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "REQUIRED_TOPICS_READY_STALE", "state_history": []},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.transition_candidate_state("somerset", "ALL_TOPICS_READY")
        assert save.call_args.kwargs["state"] == "ALL_TOPICS_READY"
        assert save.call_args.kwargs["state_history"][-1]["to_state"] == "ALL_TOPICS_READY"

    def test_inactive_and_deleted_from_any_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "REQUESTED_RESUME_ERROR", "state_history": []},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.transition_candidate_state("somerset", "INACTIVE")
        assert save.call_args.kwargs["state"] == "INACTIVE"
        assert save.call_args.kwargs["state_history"][-1]["to_state"] == "INACTIVE"

    def test_error_state_has_no_forward_happy_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "REQUESTED_RESUME_ERROR", "state_history": []},
        )
        with pytest.raises(ValueError, match="Invalid candidate state transition"):
            candidate_mod.transition_candidate_state("somerset", "RESUME_READY")

    def test_deleted_starts_reap_timer(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "ACTIVE_SEARCH", "state_history": []},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.transition_candidate_state("somerset", "DELETED")
        deleted = [c for c in save.call_args_list if c.kwargs.get("state") == "DELETED"]
        assert len(deleted) == 1
        assert deleted[0].kwargs["state_history"][-1]["to_state"] == "DELETED"
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
        state = {"cur": "ACTIVE_SEARCH", "hist": []}
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": state["cur"], "state_history": list(state["hist"])},
        )

        def _save(_cid, **kwargs):
            if "state" in kwargs:
                state["cur"] = kwargs["state"]
            if "state_history" in kwargs:
                state["hist"] = list(kwargs["state_history"])

        monkeypatch.setattr(candidate_mod.database, "save_candidate", _save)
        candidate_mod.transition_candidate_state("somerset", "PAUSE_SEARCH")
        candidate_mod.transition_candidate_state("somerset", "ACTIVE_SEARCH")
        assert state["cur"] == "ACTIVE_SEARCH"


class TestAst971CandidateTransitionHistory:
    """AST-971: company-shaped state_history on initiate + sole transition path."""

    def test_helper_appends_company_shaped_entry(self) -> None:
        out = candidate_mod._append_candidate_state_history(
            {"state_history": [{"from_state": "", "to_state": "NEW_CANDIDATE", "timestamp": "t0", "batch_id": None}],
             "batch_id": "b1"},
            "NEW_CANDIDATE",
            "INTAKE_INITIATED",
            "t1",
        )
        assert len(out) == 2
        assert out[-1] == {
            "from_state": "NEW_CANDIDATE",
            "to_state": "INTAKE_INITIATED",
            "timestamp": "t1",
            "batch_id": "b1",
        }

    def test_illegal_hop_writes_nothing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "NEW_CANDIDATE", "state_history": []},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        with pytest.raises(ValueError, match="Invalid candidate state transition"):
            candidate_mod.transition_candidate_state("somerset", "ACTIVE_SEARCH")
        save.assert_not_called()

    def test_delete_appends_exactly_once_via_transition(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """delete_candidate must not double-append — history only inside transition."""
        save = MagicMock()
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "ACTIVE_SEARCH", "state_history": [
                {"from_state": "", "to_state": "NEW_CANDIDATE", "timestamp": "t0", "batch_id": None},
            ]},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.delete_candidate("somerset")
        deleted = [c for c in save.call_args_list if c.kwargs.get("state") == "DELETED"]
        assert len(deleted) == 1
        hist = deleted[0].kwargs["state_history"]
        assert hist[-1]["from_state"] == "ACTIVE_SEARCH"
        assert hist[-1]["to_state"] == "DELETED"
        assert sum(1 for e in hist if e["to_state"] == "DELETED") == 1

    def test_same_save_writes_state_and_history(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "NEW_CANDIDATE", "state_history": []},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.transition_candidate_state("somerset", "INTAKE_INITIATED")
        assert save.call_count == 1
        kw = save.call_args.kwargs
        assert kw["state"] == "INTAKE_INITIATED"
        assert "state_history" in kw


@pytest.mark.skipif(
    not hasattr(__import__("src.utils.config", fromlist=["CANDIDATE_STAGE_DISPATCH"]), "CANDIDATE_STAGE_DISPATCH"),
    reason="AST-972 product not on this publish tip",
)
class TestAst972RequestedStageDispatch:
    """AST-972: REQUESTED_* claim workers → ready / retry / error."""

    @pytest.mark.asyncio
    async def test_resume_dispatch_success_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda cid: {
                "astral_candidate_id": cid,
                "state": "REQUESTED_RESUME",
                "candidate_data": {"context": {"raw_resume": "hello"}},
            },
        )
        monkeypatch.setattr(
            candidate_mod,
            "do_task",
            AsyncMock(return_value={"success": True, "parsed_response": {"ok": 1}}),
        )
        persist = MagicMock()
        monkeypatch.setattr(candidate_mod, "_persist_craft_dispatch_success", persist)
        trans = MagicMock()
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", trans)
        out = await candidate_mod.run_requested_resume_dispatch("c1")
        assert out == {"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}
        persist.assert_called_once()
        trans.assert_called_once_with("c1", "RESUME_READY")

    @pytest.mark.asyncio
    async def test_resume_dispatch_primary_failure_retries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "state": "REQUESTED_RESUME", "candidate_data": {}},
        )
        monkeypatch.setattr(
            candidate_mod,
            "do_task",
            AsyncMock(return_value={"success": False, "error": "boom"}),
        )
        trans = MagicMock()
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", trans)
        out = await candidate_mod.run_requested_resume_dispatch("c1")
        assert out["total_failed"] == 1 and out["total_passed"] == 0
        trans.assert_called_once_with("c1", "REQUESTED_RESUME_RETRY")

    @pytest.mark.asyncio
    async def test_resume_dispatch_retry_failure_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda cid: {
                "astral_candidate_id": cid,
                "state": "REQUESTED_RESUME_RETRY",
                "candidate_data": {},
            },
        )
        monkeypatch.setattr(
            candidate_mod,
            "do_task",
            AsyncMock(return_value={"success": False, "error": "boom"}),
        )
        trans = MagicMock()
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", trans)
        out = await candidate_mod.run_requested_resume_dispatch("c1")
        assert out["total_failed"] == 1
        trans.assert_called_once_with("c1", "REQUESTED_RESUME_ERROR")

    @pytest.mark.asyncio
    async def test_artifacts_dispatch_success_runs_all_crafts(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "state": "REQUESTED_ARTIFACTS", "candidate_data": {}},
        )
        from src.utils.config import CANDIDATE_STAGE_DISPATCH
        keys = list(CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["craft_task_keys"])
        do = AsyncMock(return_value={"success": True, "parsed_response": {}})
        monkeypatch.setattr(candidate_mod, "do_task", do)
        monkeypatch.setattr(candidate_mod, "_persist_craft_dispatch_success", MagicMock())
        trans = MagicMock()
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", trans)
        out = await candidate_mod.run_requested_artifacts_dispatch("c1")
        assert out["total_passed"] == 1
        assert do.await_count == len(keys)
        assert [c.kwargs["task_key"] for c in do.await_args_list] == keys
        trans.assert_called_once_with("c1", "ARTIFACTS_READY")

    @pytest.mark.asyncio
    async def test_artifacts_dispatch_mid_chain_failure_retries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "state": "REQUESTED_ARTIFACTS", "candidate_data": {}},
        )
        calls = {"n": 0}

        async def _do(**kwargs):
            calls["n"] += 1
            if calls["n"] == 2:
                return {"success": False, "error": "fail"}
            return {"success": True, "parsed_response": {}}

        monkeypatch.setattr(candidate_mod, "do_task", _do)
        monkeypatch.setattr(candidate_mod, "_persist_craft_dispatch_success", MagicMock())
        trans = MagicMock()
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", trans)
        out = await candidate_mod.run_requested_artifacts_dispatch("c1")
        assert out["total_failed"] == 1
        trans.assert_called_once_with("c1", "REQUESTED_ARTIFACTS_RETRY")


class TestAst973HardDeleteAndReapPurge:
    """AST-973: hard_delete wrapper + purge_reap_due_candidates."""

    def test_hard_delete_delegates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        counts = {"candidate": 1, "dispatch_task": 2}
        monkeypatch.setattr(
            candidate_mod.database,
            "hard_delete_candidate",
            lambda cid: counts if cid == "gone" else {},
        )
        assert candidate_mod.hard_delete_candidate("gone") == counts

    def test_purge_reap_due_only_due_deleted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [
            {"astral_candidate_id": "due", "state": "DELETED"},
            {"astral_candidate_id": "fresh", "state": "DELETED"},
            {"astral_candidate_id": "live", "state": "ACTIVE_SEARCH"},
        ]
        monkeypatch.setattr(candidate_mod, "list_candidates", lambda include_deleted=False: rows)
        monkeypatch.setattr(
            candidate_mod,
            "is_candidate_reap_due",
            lambda row, now=None: row["astral_candidate_id"] == "due",
        )
        deleted: list[str] = []
        monkeypatch.setattr(
            candidate_mod,
            "hard_delete_candidate",
            lambda cid: deleted.append(cid) or {"candidate": 1},
        )
        assert candidate_mod.purge_reap_due_candidates() == 1
        assert deleted == ["due"]


# Branches: 400 empty/non-str; ledger session sentinel; do_task fail/exception/non-dict;
# success split + no get/save_candidate; debug Style D on/off.
class TestAst986SessionResumeParse:
    def _patch_ledger(self, monkeypatch: pytest.MonkeyPatch) -> tuple[list, list]:
        saves: list = []
        updates: list = []
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
        monkeypatch.setattr(candidate_mod, "compute_batch_cost", MagicMock(return_value=0.5))
        monkeypatch.setattr(candidate_mod, "flush_log_buffer", MagicMock())
        return saves, updates

    @pytest.mark.parametrize("bad", ["", "   ", None, 12])
    def test_400_requires_nonempty_resume_text(self, bad: Any) -> None:
        body, status = candidate_mod.run_session_resume_parse(bad)  # type: ignore[arg-type]
        assert status == 400
        assert body == {"success": False, "error": "resume_text is required"}

    def test_500_on_task_exception(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saves, updates = self._patch_ledger(monkeypatch)
        monkeypatch.setattr(
            candidate_mod, "asyncio", MagicMock(run=MagicMock(side_effect=RuntimeError("boom")))
        )
        body, status = candidate_mod.run_session_resume_parse("paste me")
        assert status == 500
        assert body["success"] is False
        assert body["error"] == "boom"
        assert body["batch_id"].startswith("user-session-parse-resume-")
        assert saves[0][0][1] == "user-session-parse-resume"
        assert saves[0][0][2] == "session"
        assert saves[0][1]["entity_type"] is None
        assert updates[-1][1]["status"] == "FAILED"

    def test_500_on_task_exception_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_ledger(monkeypatch)
        dbg = MagicMock()
        monkeypatch.setattr(candidate_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(candidate_mod.logger, "debug_detail", MagicMock())
        monkeypatch.setattr(
            candidate_mod, "asyncio", MagicMock(run=MagicMock(side_effect=RuntimeError("x")))
        )
        body, status = candidate_mod.run_session_resume_parse("paste", debug=True)
        assert status == 500
        assert body["success"] is False
        dbg.assert_called_once()
        assert dbg.call_args.kwargs["outcome"] == "exception"

    def test_500_on_failed_task(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saves, updates = self._patch_ledger(monkeypatch)
        monkeypatch.setattr(
            candidate_mod,
            "asyncio",
            MagicMock(run=MagicMock(return_value={"success": False, "error": "bad parse"})),
        )
        body, status = candidate_mod.run_session_resume_parse("paste me")
        assert status == 500
        assert body["error"] == "bad parse"
        assert body["batch_id"].startswith("user-session-parse-resume-")
        assert updates[-1][1]["status"] == "FAILED"
        assert updates[-1][1]["total_failed"] == 1
        assert saves  # ledger opened before fail

    def test_500_on_failed_task_default_error_and_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_ledger(monkeypatch)
        dbg = MagicMock()
        monkeypatch.setattr(candidate_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(candidate_mod.logger, "debug_detail", MagicMock())
        monkeypatch.setattr(
            candidate_mod,
            "asyncio",
            MagicMock(run=MagicMock(return_value={"success": False})),
        )
        body, status = candidate_mod.run_session_resume_parse("paste", debug=True)
        assert status == 500
        assert body["error"] == "Generation failed"
        assert dbg.call_args.kwargs["outcome"] == "failed"

    def test_500_when_task_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_ledger(monkeypatch)
        monkeypatch.setattr(candidate_mod, "asyncio", MagicMock(run=MagicMock(return_value=None)))
        body, status = candidate_mod.run_session_resume_parse("paste me")
        assert status == 500
        assert body["error"] == "do_task returned None"

    def test_500_when_parsed_response_not_dict(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_ledger(monkeypatch)
        dbg = MagicMock()
        monkeypatch.setattr(candidate_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(candidate_mod.logger, "debug_detail", MagicMock())
        monkeypatch.setattr(
            candidate_mod,
            "asyncio",
            MagicMock(run=MagicMock(return_value={"success": True, "parsed_response": "nope"})),
        )
        body, status = candidate_mod.run_session_resume_parse("paste", debug=True)
        assert status == 500
        assert body["error"] == "craft_resume_base returned non-dict parsed_response"
        assert dbg.call_args.kwargs["outcome"] == "invalid payload"

    def test_500_non_dict_parsed_without_debug(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _, updates = self._patch_ledger(monkeypatch)
        monkeypatch.setattr(
            candidate_mod,
            "asyncio",
            MagicMock(run=MagicMock(return_value={"success": True, "parsed_response": ["x"]})),
        )
        body, status = candidate_mod.run_session_resume_parse("paste")
        assert status == 500
        assert updates[-1][1]["status"] == "FAILED"
        assert body["success"] is False

    def test_200_success_splits_payload_no_candidate_bind_or_persist(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        saves, updates = self._patch_ledger(monkeypatch)
        get_c = MagicMock()
        save_c = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "get_candidate", get_c)
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save_c)
        parsed = _craft_resume_base_payload(_three_section_structure(), {"experience": "Jobs"})
        calls: list[dict[str, Any]] = []

        async def _fake_do_task(**kwargs: Any) -> dict[str, Any]:
            calls.append(kwargs)
            return {"success": True, "parsed_response": parsed, "timesheet": {"tokens": 1}}

        monkeypatch.setattr(candidate_mod, "do_task", _fake_do_task)
        body, status = candidate_mod.run_session_resume_parse("  full resume text  ")
        assert status == 200
        assert body["success"] is True
        assert body["parsed_response"] == parsed
        assert body["timesheet"] == {"tokens": 1}
        assert body["batch_id"].startswith("user-session-parse-resume-")
        assert "resume_structure" in body
        assert body["base_resume"]["experience"] == "Jobs"
        assert calls[0]["task_key"] == "craft_resume_base"
        assert calls[0]["live_content"] == "full resume text"
        assert calls[0]["index"] == body["batch_id"]
        assert "astral_candidate_id" not in calls[0]["ctx"]
        assert calls[0]["ctx"]["candidate_data"]["context"]["raw_resume"] == "full resume text"
        assert saves[0][0][2] == "session"
        assert updates[-1][1]["status"] == "COMPLETED"
        get_c.assert_not_called()
        save_c.assert_not_called()

    def test_200_success_debug_style_d(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_ledger(monkeypatch)
        dbg = MagicMock()
        detail = MagicMock()
        monkeypatch.setattr(candidate_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(candidate_mod.logger, "debug_detail", detail)
        parsed = _craft_resume_base_payload(_three_section_structure())
        monkeypatch.setattr(
            candidate_mod,
            "asyncio",
            MagicMock(run=MagicMock(return_value={"success": True, "parsed_response": parsed})),
        )
        body, status = candidate_mod.run_session_resume_parse("paste", debug=True)
        assert status == 200
        assert body["success"] is True
        assert dbg.call_args.kwargs["outcome"] == "ok"
        detail_msgs = [c.args[0] for c in detail.call_args_list if c.args]
        assert any(m.startswith("experience[0] company=") for m in detail_msgs)
        assert any(m.startswith("experience[1] company=") for m in detail_msgs)


class TestAst996ExperienceJobArray:
    """AST-996: craft-base Experience as ordered job array (preserve / debug / token)."""

    def test_is_experience_job_array_helper(self) -> None:
        assert candidate_mod.is_experience_job_array(_SAMPLE_EXPERIENCE_JOBS) is True
        assert candidate_mod.is_experience_job_array([]) is True
        assert candidate_mod.is_experience_job_array("Jobs") is False
        assert candidate_mod.is_experience_job_array([{"a": 1}, "x"]) is False

    def test_split_preserves_experience_job_array(self) -> None:
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        parsed = _craft_resume_base_payload(_three_section_structure(), {"experience": jobs})
        _, content = candidate_mod.split_craft_resume_base_payload(parsed)
        assert content["experience"] == jobs
        assert content["experience"][0]["company"] == "Acme Corp"
        assert content["experience"][1]["location"] == ""

    def test_split_still_keeps_legacy_string_experience(self) -> None:
        parsed = _craft_resume_base_payload(
            _three_section_structure(), {"experience": "legacy prose"}
        )
        _, content = candidate_mod.split_craft_resume_base_payload(parsed)
        assert content["experience"] == "legacy prose"

    def test_filter_content_preserves_nonempty_job_array(self) -> None:
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        out = candidate_mod.filter_content_to_resume_structure(
            {"experience": jobs, "orphan_section": "drop", "technical_skills": "  "},
            _three_section_structure(),
        )
        assert out == {"experience": jobs}

    def test_filter_content_drops_empty_job_array(self) -> None:
        out = candidate_mod.filter_content_to_resume_structure(
            {"experience": [], "professional_summary": "ok"},
            _three_section_structure(),
        )
        assert "experience" not in out
        assert out == {"professional_summary": "ok"}

    def test_flatten_promotes_job_array_from_content_dict(self) -> None:
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        structure = candidate_mod.default_resume_structure()
        parsed: dict[str, Any] = {
            "agent_payload": {
                "resume_structure": {
                    "sections": structure["sections"],
                    "content": {"experience": jobs, "professional_summary": "Summary"},
                }
            }
        }
        candidate_mod.normalize_craft_resume_base_agent_payload(parsed)
        assert parsed["agent_payload"]["experience"] == jobs
        assert parsed["agent_payload"]["professional_summary"] == "Summary"

    def test_flatten_does_not_str_coerce_existing_job_array(self) -> None:
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        structure = candidate_mod.default_resume_structure()
        parsed: dict[str, Any] = {
            "agent_payload": {
                "resume_structure": {
                    "sections": structure["sections"],
                    "content": {"experience": "should not overwrite"},
                },
                "experience": jobs,
            }
        }
        candidate_mod.normalize_craft_resume_base_agent_payload(parsed)
        assert parsed["agent_payload"]["experience"] == jobs

    def test_format_base_resume_token_includes_job_array_json(self) -> None:
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        structure = candidate_mod.default_resume_structure()
        cd = {
            "artifacts": {
                "resume_structure": structure,
                "base_resume": {"experience": jobs, "professional_summary": "Summary"},
            }
        }
        out = candidate_mod.format_base_resume_for_token(cd)
        parsed = json.loads(out)
        assert parsed["experience"] == jobs
        assert parsed["professional_summary"] == "Summary"

    def test_debug_experience_jobs_emits_style_d_lines(self) -> None:
        log = MagicMock()
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        candidate_mod._debug_experience_jobs(log, {"experience": jobs})
        msgs = [c.args[0] for c in log.debug_detail.call_args_list]
        assert msgs[0].startswith("experience[0] company='Acme Corp'")
        assert any("accomplishments:" in m for m in msgs)
        assert any(m.startswith("experience[1] company='Beta LLC'") for m in msgs)

    def test_debug_experience_jobs_legacy_string_shape(self) -> None:
        log = MagicMock()
        candidate_mod._debug_experience_jobs(log, {"experience": "old prose"})
        log.debug_detail.assert_called_with("experience_shape=str")

    def test_session_parse_returns_job_array_in_base_resume(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        saves: list = []
        updates: list = []
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
        monkeypatch.setattr(candidate_mod, "compute_batch_cost", MagicMock(return_value=0.0))
        monkeypatch.setattr(candidate_mod, "flush_log_buffer", MagicMock())
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        parsed = _craft_resume_base_payload(_three_section_structure(), {"experience": jobs})

        async def _fake_do_task(**kwargs: Any) -> dict[str, Any]:
            return {"success": True, "parsed_response": parsed, "timesheet": {}}

        monkeypatch.setattr(candidate_mod, "do_task", _fake_do_task)
        body, status = candidate_mod.run_session_resume_parse("multi-job resume")
        assert status == 200
        assert body["base_resume"]["experience"] == jobs
        assert body["base_resume"]["experience"][0]["accomplishments"] == "Shipped widgets"

    def test_persist_craft_resume_base_keeps_job_array(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        saves: list[tuple[Any, ...]] = []
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        parsed = _craft_resume_base_payload(_three_section_structure(), {"experience": jobs})
        monkeypatch.setattr(
            candidate_mod.database, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id}
        )
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
        body, status = candidate_mod.run_candidate_artifact_generation(
            "karfo", "craft_resume_base", "resume text", debug=True
        )
        assert status == 200
        artifacts = saves[0][1]["candidate_data"]["artifacts"]
        assert artifacts["base_resume"]["experience"] == jobs

    @pytest.mark.asyncio
    async def test_parse_candidate_resume_debug_lists_jobs(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        detail = MagicMock()
        monkeypatch.setattr(candidate_mod.logger, "debug_detail", detail)
        monkeypatch.setattr(candidate_mod.logger, "debug_index", MagicMock())
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {
                "state": "NEW_CANDIDATE",
                "candidate_data": {"context": {"raw_resume": "paste"}},
            },
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", MagicMock())
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", lambda *a, **k: None)

        async def _do_task(**kwargs: Any) -> dict[str, Any]:
            return {
                "success": True,
                "parsed_response": _craft_resume_base_payload(
                    _three_section_structure(), {"experience": jobs}
                ),
            }

        monkeypatch.setattr(candidate_mod, "do_task", _do_task)
        out = await candidate_mod.parse_candidate_resume("c1", debug=True)
        assert out["success"] is True
        msgs = [c.args[0] for c in detail.call_args_list if c.args]
        assert any(m.startswith("experience[0] company=") for m in msgs)

    def test_craft_resume_base_prompt_requires_job_array_contract(self) -> None:
        # Repo admin JSON is the Judith prompt source (applied at bootstrap).
        from pathlib import Path

        rows = json.loads(Path("data/admin/agent_task.json").read_text(encoding="utf-8"))
        row = next(r for r in rows if r.get("task_key") == "craft_resume_base")
        prompt = row.get("cache_prompt") or ""
        assert "Ordered JSON array of jobs" in prompt
        assert "`accomplishments`" in prompt
        assert "Do **not** enrich, blend, or expand accomplishments from LinkedIn" in prompt


class TestAst1027CraftResumeBaseMarkerPreserve:
    """AST-1027: craft_resume_base cache_prompt preserves __ / ~~ for builder expand."""

    def test_cache_prompt_preserves_typography_markers(self) -> None:
        from pathlib import Path

        rows = json.loads(Path("data/admin/agent_task.json").read_text(encoding="utf-8"))
        row = next(r for r in rows if r.get("task_key") == "craft_resume_base")
        prompt = row.get("cache_prompt") or ""
        # Preserve contract (replaces prior strip-to-space/hyphen rule).
        assert "Typography markers (preserve)" in prompt
        assert "Do **not** replace `__` with a space or `~~` with a hyphen" in prompt
        assert "`__` → NBSP" in prompt
        assert (
            "When the resume/paste contains `__` or `~~`, those digraphs appear unchanged"
            in prompt
        )
        # Old strip instructions must be gone.
        assert "Strip ANY formatting artifacts" not in prompt
        assert "All formatting codes stripped clean" not in prompt
        assert "`__` (replace with space)" not in prompt
        assert "`~~` (replace with hyphen)" not in prompt
        # Segment instructions stay paste-faithful (UAT skills / contact / prior).
        assert "do not rewrite marked bullet separators into pipes" in prompt
        assert "Jira__•__Confluence__•__Linear" in prompt
        assert "When the paste uses `__•__`" in prompt
        assert "Preserve `__` / `~~` / `•` from the paste line" in prompt


class TestAst1028CraftResumeBaseTitleTaglineSplit:
    """AST-1028: craft_resume_base splits title vs specialty/keyword tagline."""

    def test_cache_prompt_title_only_and_candidate_tagline_segment(self) -> None:
        from pathlib import Path

        rows = json.loads(Path("data/admin/agent_task.json").read_text(encoding="utf-8"))
        row = next(r for r in rows if r.get("task_key") == "craft_resume_base")
        prompt = row.get("cache_prompt") or ""
        # Segment order: title → tagline → contact.
        title_i = prompt.find("### candidate_title")
        tagline_i = prompt.find("### candidate_tagline")
        contact_i = prompt.find("### candidate_contact_detail")
        assert title_i >= 0 and tagline_i > title_i and contact_i > tagline_i
        # Title must stay title-only (UAT mash was title + em-dash keywords).
        assert "Put **only** the title in this field" in prompt
        assert 'Do **not** append specialty phrases, keyword lists, "specializing in …"' in prompt
        assert "em/en-dash–joined keyword tails" in prompt or "em/en-dash" in prompt
        assert "belong in `candidate_tagline`, not here" in prompt
        # Tagline feeds ATS meta only — not header/body.
        assert "HTML emit uses it for ATS meta only" in prompt
        assert "Do **not** duplicate this text into `candidate_title`" in prompt
        assert "Enterprise Implementation • Service Delivery" in prompt
        # Quality checklist locks the split.
        assert (
            "Title is title-only; when the paste has a separate specialty/keyword line, "
            "it appears in `candidate_tagline`"
            in prompt
        )


class TestAst1029CraftResumeBaseCompetenciesBullets:
    """AST-1029: craft_resume_base requires • competencies separators; forbids pipes."""

    def test_cache_prompt_requires_bullet_not_pipe_separators(self) -> None:
        from pathlib import Path

        rows = json.loads(Path("data/admin/agent_task.json").read_text(encoding="utf-8"))
        row = next(r for r in rows if r.get("task_key") == "craft_resume_base")
        prompt = row.get("cache_prompt") or ""
        # Soft AST-1027 prefer-language must be gone.
        assert "Prefer separators from the paste" not in prompt
        assert 'rather than rewriting to " | "' not in prompt
        # Hard require • / forbid |
        assert "Item separator is the bullet character `•`" in prompt
        assert '**Do not** use `|` (pipe) as an item separator' in prompt
        assert 'not `" | "`, not bare `|`' in prompt
        assert "**join with ` • `**, never `|`" in prompt
        # Prior experience same convention.
        assert "Use `•` between role items (same convention as core competencies)" in prompt
        assert "**Do not** use `|` as separators" in prompt
        # Checklist.
        assert (
            "`core_competencies` (and `prior_experience` when non-empty) use `•` separators, not `|`"
            in prompt
        )


class TestAst1030CraftResumeBaseNoBulletPreserve:
    """AST-1030: craft_resume_base must preserve paste `<no bullet>` on role leads."""

    def test_cache_prompt_preserves_no_bullet_lead_prefix(self) -> None:
        from pathlib import Path

        rows = json.loads(Path("data/admin/agent_task.json").read_text(encoding="utf-8"))
        row = next(r for r in rows if r.get("task_key") == "craft_resume_base")
        prompt = row.get("cache_prompt") or ""
        assert (
            "copy that line into `accomplishments` **including the literal prefix** "
            "`<no bullet>`"
            in prompt
        )
        assert "Do **not** invent a `<no bullet>` lead when the paste has none." in prompt
        assert (
            "When the paste uses `<no bullet>` on a role lead, keep that exact prefix "
            "on the corresponding `accomplishments` line(s)"
            in prompt
        )
        assert (
            "When the paste uses `<no bullet>` on a role lead, that prefix appears "
            "unchanged on the corresponding `accomplishments` line(s)"
            in prompt
        )


class TestAst997JobTailoredExperience:
    """AST-997: draft/finalize experience job-array accept + pin by (company, title)."""

    def _base_cd(self, jobs: list[dict[str, str]]) -> dict[str, Any]:
        return {"artifacts": {"base_resume": {"experience": jobs}, "resume_structure": _three_section_structure()}}

    def test_normalize_preserves_experience_job_array(self) -> None:
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        parsed: dict[str, Any] = {"agent_payload": {"experience": jobs, "professional_summary": "S"}}
        candidate_mod.normalize_draft_job_resume_agent_payload(parsed)
        assert parsed["agent_payload"]["experience"] == jobs

    def test_validate_accepts_job_array_and_pins_metadata(self) -> None:
        base = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        tailored = [
            {
                "company": "Beta LLC",
                "title": "Lead",
                "dates": "WRONG",
                "location": "WRONG",
                "accomplishments": "Tailored lead bullets",
            },
            {
                "company": "Acme Corp",
                "title": "Engineer",
                "dates": "WRONG",
                "location": "WRONG",
                "accomplishments": "Tailored eng bullets",
            },
        ]
        payload = {"professional_summary": "S", "experience": tailored}
        err = candidate_mod.validate_draft_job_resume_payload(payload, self._base_cd(base))
        assert err is None
        # Reordered: pin by company+title, not index
        assert payload["experience"][0]["dates"] == "2023"
        assert payload["experience"][0]["location"] == ""
        assert payload["experience"][0]["accomplishments"] == "Tailored lead bullets"
        assert payload["experience"][1]["dates"] == "2020-2023"
        assert payload["experience"][1]["location"] == "Remote"
        assert payload["experience"][1]["accomplishments"] == "Tailored eng bullets"

    def test_pin_does_not_index_fallback_on_unmatched(self) -> None:
        base = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        tailored = [
            {
                "company": "Other Co",
                "title": "Intern",
                "dates": "kept-model",
                "location": "kept-loc",
                "accomplishments": "new role text",
            }
        ]
        payload = {"experience": tailored}
        candidate_mod.pin_experience_job_facts_from_base(payload, self._base_cd(base))
        assert payload["experience"][0]["dates"] == "kept-model"
        assert payload["experience"][0]["location"] == "kept-loc"

    def test_pin_consumes_duplicate_company_title_in_base_order(self) -> None:
        base = [
            {
                "company": "Amazon",
                "title": "SPM",
                "dates": "2018-2020",
                "location": "SEA",
                "accomplishments": "first tour",
            },
            {
                "company": "Amazon",
                "title": "SPM",
                "dates": "2021-2023",
                "location": "NYC",
                "accomplishments": "second tour",
            },
        ]
        tailored = [
            {
                "company": "Amazon",
                "title": "SPM",
                "dates": "x",
                "location": "x",
                "accomplishments": "tailored-1",
            },
            {
                "company": "Amazon",
                "title": "SPM",
                "dates": "y",
                "location": "y",
                "accomplishments": "tailored-2",
            },
        ]
        payload = {"experience": tailored}
        candidate_mod.pin_experience_job_facts_from_base(payload, self._base_cd(base))
        assert payload["experience"][0]["dates"] == "2018-2020"
        assert payload["experience"][0]["location"] == "SEA"
        assert payload["experience"][0]["accomplishments"] == "tailored-1"
        assert payload["experience"][1]["dates"] == "2021-2023"
        assert payload["experience"][1]["location"] == "NYC"

    def test_validate_accepts_legacy_string_experience(self) -> None:
        assert (
            candidate_mod.validate_draft_job_resume_payload(
                {"experience": "legacy prose"}, self._base_cd([dict(j) for j in _SAMPLE_EXPERIENCE_JOBS])
            )
            is None
        )

    def test_validate_rejects_non_job_array_experience_object(self) -> None:
        err = candidate_mod.validate_draft_job_resume_payload(
            {"experience": {"company": "Acme"}},
            self._base_cd([dict(j) for j in _SAMPLE_EXPERIENCE_JOBS]),
        )
        assert err is not None
        assert "job array or prose string" in err

    def test_tailor_hop_prompts_teach_job_array_and_pin_policy(self) -> None:
        from pathlib import Path

        rows = json.loads(Path("data/admin/agent_task.json").read_text(encoding="utf-8"))
        by_key = {r["task_key"]: r for r in rows if r.get("task_key")}
        draft = by_key["draft_job_resume"]["user_prompt"]
        assert "ordered array of job objects" in draft
        assert "**Do not** change `company`, `title`, `dates`, or `location`" in draft
        fin = by_key["finalize_job_resume"]["user_prompt"]
        assert "ordered array of job objects" in fin
        assert "restore factual metadata" in fin
        advise = by_key["advise_job_resume"]["user_prompt"]
        assert "**forbid** rewriting company, title, dates, or location" in advise
        check = by_key["check_job_resume"]["user_prompt"]
        assert "Experience metadata drift" in check
        assert "company, title, dates, or location" in check


class TestAst1005FalseMissingCandidateName:
    """AST-1005: promote direct resume_structure section keys before default wipe."""

    _OTHER_REQUIRED = {
        "candidate_title": "Engineer",
        "candidate_contact_detail": "a@b.c",
        "professional_summary": "Summary",
        "core_competencies": "Skills",
    }

    def _jobs(self) -> list[dict[str, str]]:
        return [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]

    def test_promote_direct_candidate_name_with_sections_passes_schema(self) -> None:
        from src.core.agent import _validate_response_schema
        from src.utils.config import TASK_CONFIG

        structure = candidate_mod.default_resume_structure()
        jobs = self._jobs()
        parsed: dict[str, Any] = {
            "agent_performance": {"status": "success"},
            "agent_payload": {
                "resume_structure": {
                    "sections": structure["sections"],
                    "candidate_name": "Susan Somerset",
                    "experience": jobs,
                },
                **self._OTHER_REQUIRED,
            },
        }
        candidate_mod.normalize_craft_resume_base_agent_payload(parsed)
        ap = parsed["agent_payload"]
        assert ap["candidate_name"] == "Susan Somerset"
        assert ap["experience"] == jobs
        assert isinstance(ap["experience"], list)
        schema = TASK_CONFIG["craft_resume_base"]["response_schema"]
        assert _validate_response_schema(parsed, schema, "craft_resume_base") is None

    def test_promote_direct_candidate_name_without_sections_passes_schema(self) -> None:
        from src.core.agent import _validate_response_schema
        from src.utils.config import TASK_CONFIG

        jobs = self._jobs()
        parsed: dict[str, Any] = {
            "agent_performance": {"status": "success"},
            "agent_payload": {
                "resume_structure": {
                    "candidate_name": "Susan Somerset",
                    "experience": jobs,
                },
                **self._OTHER_REQUIRED,
            },
        }
        candidate_mod.normalize_craft_resume_base_agent_payload(parsed)
        ap = parsed["agent_payload"]
        assert ap["candidate_name"] == "Susan Somerset"
        assert ap["experience"] == jobs
        assert "candidate_name" in ap["resume_structure"]["sections"]
        schema = TASK_CONFIG["craft_resume_base"]["response_schema"]
        assert _validate_response_schema(parsed, schema, "craft_resume_base") is None

    def test_missing_candidate_name_still_fails_schema(self) -> None:
        from src.core.agent import _validate_response_schema
        from src.utils.config import TASK_CONFIG

        jobs = self._jobs()
        parsed: dict[str, Any] = {
            "agent_performance": {"status": "success"},
            "agent_payload": {
                "resume_structure": {"experience": jobs},
                **self._OTHER_REQUIRED,
            },
        }
        candidate_mod.normalize_craft_resume_base_agent_payload(parsed)
        schema = TASK_CONFIG["craft_resume_base"]["response_schema"]
        err = _validate_response_schema(parsed, schema, "craft_resume_base")
        assert err is not None
        assert "Missing required field 'candidate_name'" in err


class TestAst1014CandidateLibrary:
    """AST-1014: contact/context library, name columns, token view, save contract."""

    def test_build_candidate_token_view(self) -> None:
        row = {
            "astral_candidate_id": "c1",
            "first": "Ada",
            "last": "Lovelace",
            "full": "Ada Lovelace",
            "pronouns": "they/them",
            "candidate_data": {
                "contact": {"contact_email": "ada@example.com"},
                "context": {"raw_resume": "paste"},
                "artifacts": {"base_resume": {}},
            },
        }
        view = candidate_mod.build_candidate_token_view(row)
        assert view["first"] == "Ada"
        assert view["full"] == "Ada Lovelace"
        assert view["pronouns"] == "they/them"
        assert view["contact"]["contact_email"] == "ada@example.com"
        assert view["context"]["raw_resume"] == "paste"
        assert "profile" not in view

    def test_recompute_full_name(self) -> None:
        assert candidate_mod.recompute_full_name("Ada", "Lovelace") == "Ada Lovelace"
        assert candidate_mod.recompute_full_name("Ada", "") == "Ada"
        assert candidate_mod.recompute_full_name("", "Lovelace") == "Lovelace"

    def test_normalize_contact_urls(self) -> None:
        contact = {"linkedin_url": "ada-lovelace", "github": "ada"}
        candidate_mod.normalize_contact_urls(contact)
        assert contact["linkedin_url"] == "https://www.linkedin.com/in/ada-lovelace"
        assert contact["github"] == "https://github.com/ada"

    def test_save_refuses_profile_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "save_candidate", MagicMock())
        with pytest.raises(ValueError, match="profile was renamed to contact"):
            candidate_mod.save_candidate_data("c1", {"profile": {"first": "Ada"}})

    def test_save_columns_contact_and_full_recompute(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"first": "Ada", "last": "Lovelace"},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.save_candidate_data(
            "c1",
            {
                "first": "Grace",
                "last": "Hopper",
                "pronouns": "she/her",
                "contact": {"contact_email": "grace@example.com"},
            },
        )
        assert save.call_args.kwargs["first"] == "Grace"
        assert save.call_args.kwargs["last"] == "Hopper"
        assert save.call_args.kwargs["full"] == "Grace Hopper"
        assert save.call_args.kwargs["pronouns"] == "she/her"
        merged = save.call_args.kwargs["candidate_data"]
        assert merged["contact"]["contact_email"] == "grace@example.com"

    def test_save_candidate_data_debug_optional(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dbg = MagicMock()
        monkeypatch.setattr(candidate_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(candidate_mod.database, "save_candidate", MagicMock())
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda candidate_id: {})
        candidate_mod.save_candidate_data("c1", {"contact": {"phone": "555"}}, debug=True)
        assert dbg.called
        candidate_mod.save_candidate_data("c1", {"contact": {"phone": "555"}}, debug=False)
