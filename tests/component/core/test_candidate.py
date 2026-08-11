"""Component tests for src/core/candidate.py (AST-393)."""

from __future__ import annotations

import inspect
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import candidate as candidate_mod
from src.utils.config import (
    ASTRAL_CONFIG,
    BUILD_CONFIG,
    CANDIDATE_STATES,
    RESUME_STRUCTURE_BODY_FORMATS,
    RESUME_STRUCTURE_CONTACT_SECTION_IDS,
    RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID,
    RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT,
    RESUME_STRUCTURE_KNOWN_SECTION_IDS,
    RESUME_STRUCTURE_REQUIRED_SECTION_IDS,
)

_RUBRIC_CONTENT = "body\nA = one\nB = two"
_CI = ASTRAL_CONFIG["consult_importance"]
_VALID_ACCENT = (BUILD_CONFIG.get("accent_palette") or ["#1A1A2E"])[0].upper()


def _three_section_structure() -> dict[str, Any]:
    """Slim three-id catalog for projection helpers that do not call normalize."""
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


def _catalog_structure() -> dict[str, Any]:
    """Default ten-id catalog (normalize-valid) with the AST-517 custom titles."""
    out = candidate_mod.default_resume_structure()
    out["sections"]["professional_summary"]["title"] = "Custom Summary"
    out["sections"]["experience"]["title"] = "Custom Jobs"
    out["sections"]["technical_skills"]["title"] = "Custom Skills"
    return out


def _required_seven_structure() -> dict[str, Any]:
    full = candidate_mod.default_resume_structure()
    keep = set(RESUME_STRUCTURE_REQUIRED_SECTION_IDS)
    full["sections"] = {sid: spec for sid, spec in full["sections"].items() if sid in keep}
    return full


def _seven_experience(spec: Any, *, accent: Any = None) -> dict[str, Any]:
    raw = _required_seven_structure()
    raw["sections"]["experience"] = spec
    if accent is not None:
        raw["accent_color"] = accent
    return raw


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
        with pytest.raises(candidate_mod.IllegalCandidateTransition, match="Invalid candidate state transition"):
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
        structure = _catalog_structure()
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

    def test_preview_resolves_names_from_columns_not_blob(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """AST-1192: preview uses build_candidate_token_view — columns win when blob lacks names."""
        from src.core import agent as agent_mod

        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {
                "astral_candidate_id": candidate_id,
                "first": "Ada",
                "last": "Lovelace",
                "full": "Ada Lovelace",
                "candidate_data": {"contact": {}, "context": {}, "artifacts": {}},
            },
        )
        monkeypatch.setattr(
            candidate_mod,
            "company_search_terms_joined_text",
            lambda cid: "",
        )
        monkeypatch.setattr(
            agent_mod,
            "_resolve_task_prompts",
            lambda task_key: (
                {"content": "agent"},
                {
                    "system_prompt": "",
                    "user_prompt": "Scan for {$FIRST_NAME} {$LAST_NAME}",
                    "cache_prompt": "",
                    "nocache_prompt": "",
                },
            ),
        )
        out = candidate_mod.preview_task_prompt("anticipate_scan", candidate_id="cand-1192")
        assert "Scan for Ada Lovelace" in out["user"]
        assert "{$FIRST_NAME}" not in out["user"]
        assert "{$LAST_NAME}" not in out["user"]

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
        parsed = _craft_resume_base_payload(_catalog_structure(), {"experience": "ok"})
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
        parsed = _craft_resume_base_payload(_catalog_structure())
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
        assert artifacts["base_resume"]["experience"] == [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]

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
        raw = _catalog_structure()
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
            ({"sections": {"bad_id": {}}}, "missing required"),
            (_seven_experience("x"), "section experience must be a dict"),
            (
                _seven_experience(
                    {"id": "wrong", "title": "T", "enabled": True, "order": 0, "job_agent_editable": True}
                ),
                "section id mismatch",
            ),
            (
                _seven_experience(
                    {"id": "experience", "title": " ", "enabled": True, "order": 0, "job_agent_editable": True}
                ),
                "requires non-empty title",
            ),
            (
                _seven_experience(
                    {"id": "experience", "title": "T", "enabled": "yes", "order": 0, "job_agent_editable": True}
                ),
                "enabled must be boolean",
            ),
            (
                _seven_experience(
                    {"id": "experience", "title": "T", "enabled": True, "order": "0", "job_agent_editable": True}
                ),
                "order must be int",
            ),
            (
                _seven_experience(
                    {"id": "experience", "title": "T", "enabled": True, "order": 0, "job_agent_editable": "no"}
                ),
                "job_agent_editable must be boolean",
            ),
            (
                _seven_experience(
                    {"id": "experience", "title": "T", "enabled": True, "order": 0, "job_agent_editable": True},
                    accent="red",
                ),
                "accent_color must be #RRGGBB",
            ),
            (
                _seven_experience(
                    {"id": "experience", "title": "T", "enabled": True, "order": 0, "job_agent_editable": True},
                    accent="#ABCDEF",
                ),
                "accent_color not in accent_palette",
            ),
        ],
    )
    def test_normalize_rejects_invalid_structure(self, raw: Any, match: str) -> None:
        with pytest.raises(ValueError, match=match):
            candidate_mod.normalize_resume_structure(raw)

    def test_resolve_returns_stored_structure(self) -> None:
        stored = _catalog_structure()
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
        structure = _catalog_structure()
        structure["sections"]["technical_skills"]["enabled"] = False
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        parsed = _craft_resume_base_payload(structure, {"technical_skills": "skip", "experience": jobs})
        _, content = candidate_mod.split_craft_resume_base_payload(parsed)
        assert "technical_skills" not in content
        assert content["experience"] == jobs

    def test_split_skips_non_string_section_values(self) -> None:
        structure = _catalog_structure()
        parsed = _craft_resume_base_payload(structure)
        parsed["technical_skills"] = 99
        _, content = candidate_mod.split_craft_resume_base_payload(parsed)
        assert "technical_skills" not in content

    def test_split_omits_enabled_sections_absent_from_payload(self) -> None:
        structure = _catalog_structure()
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        parsed = {"resume_structure": structure, "experience": jobs}
        _, content = candidate_mod.split_craft_resume_base_payload(parsed)
        assert content == {"experience": jobs}

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
        structure = _catalog_structure()
        sections = {
            sid: {**spec, "content": f"nested-{sid}"}
            for sid, spec in structure["sections"].items()
        }
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        sections["experience"] = {**structure["sections"]["experience"], "content": jobs}
        parsed = {"resume_structure": {"sections": sections}}
        _, content = candidate_mod.split_craft_resume_base_payload(parsed)
        assert content["experience"] == jobs
        assert content["professional_summary"] == "nested-professional_summary"

    @pytest.mark.asyncio
    async def test_parse_persists_custom_structure_per_candidate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        stores: dict[str, dict] = {
            "cand-a": {"state": "NEW_CANDIDATE", "candidate_data": {"context": {"raw_resume": "a"}}},
            "cand-b": {"state": "NEW_CANDIDATE", "candidate_data": {"context": {"raw_resume": "b"}}},
        }
        struct_a = _catalog_structure()
        struct_b = _catalog_structure()
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
    """AST-594: normalize + section validation for draft_job_resume (whitelist = base_resume; AST-1270)."""

    def _base_cd(self, **sections: Any) -> dict[str, Any]:
        # AST-1270: draft whitelist reads artifacts.base_resume keys (not resume_structure catalog).
        base = {
            "professional_summary": "Summary",
            "experience": [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS],
            "candidate_contact_detail": "ada@example.com",
        }
        base.update(sections)
        return {"artifacts": {"base_resume": base}}

    def test_validate_accepts_structure_keyed_subset(self) -> None:
        payload = {
            "professional_summary": "Summary",
            "experience": [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS],
        }
        assert candidate_mod.validate_draft_job_resume_payload(payload, self._base_cd()) is None

    def test_validate_rejects_unknown_section_key(self) -> None:
        err = candidate_mod.validate_draft_job_resume_payload({"made_up_section": "x"}, self._base_cd())
        assert err is not None
        assert "Unknown resume section key" in err
        assert "made_up_section" in err
        assert "base_resume keys" in err

    def test_validate_rejects_grades_field(self) -> None:
        err = candidate_mod.validate_draft_job_resume_payload({"grades": []}, self._base_cd())
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
        assert candidate_mod.validate_draft_job_resume_payload(ap, self._base_cd()) is None


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

    def test_craft_get_rubric_ui_generate_rejected_for_chain(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # AST-1253: chain keys hand off via generate_artifacts — no ad-hoc UI generate/stash.
        store = {"astral_candidate_id": "karfo", "candidate_data": {}}
        saves = self._stub_generate_common(monkeypatch, store)
        monkeypatch.setattr(
            candidate_mod,
            "is_requested_artifacts_chain_ui_task",
            lambda task_key: task_key == "craft_get_rubric",
        )
        body, status = candidate_mod.run_candidate_artifact_generation(
            "karfo", "craft_get_rubric", None,
        )
        assert status == 409
        assert body["success"] is False
        assert "generate_artifacts" in body["error"]
        assert saves == []

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


class TestAst1253RequestedArtifactsHandoff:
    """AST-1253: start_requested_artifacts + live walk helpers + chain UI generate reject."""

    def test_start_requested_artifacts_transitions(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "state": "ARTIFACTS_READY"},
        )
        trans = MagicMock()
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", trans)
        out = candidate_mod.start_requested_artifacts("c1")
        assert out == "REQUESTED_ARTIFACTS"
        trans.assert_called_once_with("c1", "REQUESTED_ARTIFACTS")

    def test_start_requested_artifacts_missing_raises(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda _cid: None)
        with pytest.raises(ValueError, match="not found"):
            candidate_mod.start_requested_artifacts("missing")

    def test_walk_helpers_order_labels_and_rubric_keys(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Live walk: get → do → company_search_terms (terminal).
        nxt = {
            "craft_get_rubric": "craft_do_rubric",
            "craft_do_rubric": "craft_company_search_terms",
            "craft_company_search_terms": "",
        }
        monkeypatch.setattr(
            candidate_mod,
            "_current_agent_task_run_next",
            lambda key: nxt.get(key, ""),
        )
        keys = candidate_mod.requested_artifacts_chain_task_keys()
        assert keys == [
            "craft_get_rubric",
            "craft_do_rubric",
            "craft_company_search_terms",
        ]
        assert candidate_mod.is_requested_artifacts_chain_ui_task("craft_do_rubric") is True
        assert candidate_mod.is_requested_artifacts_chain_ui_task("craft_resume_base") is False
        labels = candidate_mod.requested_artifacts_chain_hop_labels()
        assert labels == [
            "Get Job Criteria",
            "Do Job Criteria",
            "Company Search Terms",
        ]
        # Rubric-only — table-backed search terms excluded from artifact keys.
        assert candidate_mod.requested_artifacts_chain_artifact_keys() == [
            "get_rubric",
            "do_rubric",
        ]

    def test_walk_cycle_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod,
            "_current_agent_task_run_next",
            lambda key: "craft_get_rubric",
        )
        with pytest.raises(RuntimeError, match="cycle"):
            candidate_mod.requested_artifacts_chain_task_keys()


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
        with pytest.raises(candidate_mod.IllegalCandidateTransition, match="Invalid candidate state transition"):
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
        with pytest.raises(candidate_mod.IllegalCandidateTransition, match="Invalid candidate state transition"):
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
    """AST-972 → AST-1252: REQUESTED_ARTIFACTS → single craft_get_rubric do_task (native run_next)."""

    @pytest.mark.asyncio
    async def test_artifacts_dispatch_success_native_run_next(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "state": "REQUESTED_ARTIFACTS", "candidate_data": {}},
        )
        do = AsyncMock(return_value={"success": True, "parsed_response": {}})
        monkeypatch.setattr(candidate_mod, "do_task", do)
        trans = MagicMock()
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", trans)
        out = await candidate_mod.run_requested_artifacts_dispatch("c1")
        assert out["total_passed"] == 1
        assert do.await_count == 1
        call = do.await_args
        assert call.kwargs["task_key"] == "craft_get_rubric"
        assert call.kwargs["index"] == "c1"
        assert call.kwargs["ctx"].get("persist_candidate_craft_hops") is True
        assert call.kwargs["ctx"].get("suppress_run_next") is not True
        assert call.kwargs["ctx"].get("astral_candidate_id") == "c1"
        trans.assert_called_once_with("c1", "ARTIFACTS_READY")

    @pytest.mark.asyncio
    async def test_artifacts_dispatch_failure_retries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "state": "REQUESTED_ARTIFACTS", "candidate_data": {}},
        )
        monkeypatch.setattr(
            candidate_mod,
            "do_task",
            AsyncMock(return_value={"success": False, "error": "fail"}),
        )
        trans = MagicMock()
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", trans)
        out = await candidate_mod.run_requested_artifacts_dispatch("c1")
        assert out["total_failed"] == 1
        trans.assert_called_once_with("c1", "REQUESTED_ARTIFACTS_RETRY")

    @pytest.mark.asyncio
    async def test_artifacts_dispatch_retry_failure_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda cid: {
                "astral_candidate_id": cid,
                "state": "REQUESTED_ARTIFACTS_RETRY",
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
        out = await candidate_mod.run_requested_artifacts_dispatch("c1")
        assert out["total_failed"] == 1
        trans.assert_called_once_with("c1", "REQUESTED_ARTIFACTS_ERROR")

    def test_resume_wrapper_worker_removed(self) -> None:
        assert not hasattr(candidate_mod, "run_requested_resume_dispatch")

    def test_ui_generate_still_suppresses_run_next(self) -> None:
        import inspect
        gen_src = inspect.getsource(candidate_mod.run_candidate_artifact_generation)
        assert "suppress_run_next" in gen_src


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
        assert body["error"] == "simple_resume_parse returned non-dict parsed_response"
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
        parsed = _craft_resume_base_payload(_catalog_structure())
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
        assert body["base_resume"]["experience"] == [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        assert calls[0]["task_key"] == "simple_resume_parse"
        assert calls[0]["live_content"] == "full resume text"
        assert calls[0]["index"] == body["batch_id"]
        assert "astral_candidate_id" not in calls[0]["ctx"]
        # Session synthetic ctx on this tip still uses starting_resume_text (AST-1014 raw_* not on base).
        assert calls[0]["ctx"]["candidate_data"]["context"]["starting_resume_text"] == "full resume text"
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
        parsed = _craft_resume_base_payload(_catalog_structure())
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


class TestAst1038SessionResumeWire:
    """AST-1038: session parse uses Ruth simple_resume_parse; Judith craft paths unchanged."""

    def test_session_parse_wires_simple_resume_parse_not_craft_base(self) -> None:
        src = inspect.getsource(candidate_mod.run_session_resume_parse)
        assert 'task_key="simple_resume_parse"' in src
        assert 'task_key="craft_resume_base"' not in src
        assert "simple_resume_parse returned non-dict parsed_response" in src

    def test_candidate_craft_paths_still_use_craft_resume_base(self) -> None:
        parse_src = inspect.getsource(candidate_mod.parse_candidate_resume)
        assert 'task_key="craft_resume_base"' in parse_src
        # Artifact generation still accepts craft_resume_base as the catalog key for Judith.
        gen_src = inspect.getsource(candidate_mod.run_candidate_artifact_generation)
        assert "craft_resume_base" in gen_src


class TestAst996ExperienceJobArray:
    """AST-996: craft-base Experience as ordered job array (preserve / debug / token)."""

    def test_is_experience_job_array_helper(self) -> None:
        assert candidate_mod.is_experience_job_array(_SAMPLE_EXPERIENCE_JOBS) is True
        assert candidate_mod.is_experience_job_array([]) is True
        assert candidate_mod.is_experience_job_array("Jobs") is False
        assert candidate_mod.is_experience_job_array([{"a": 1}, "x"]) is False

    def test_split_preserves_experience_job_array(self) -> None:
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        parsed = _craft_resume_base_payload(_catalog_structure(), {"experience": jobs})
        _, content = candidate_mod.split_craft_resume_base_payload(parsed)
        assert content["experience"] == jobs
        assert content["experience"][0]["company"] == "Acme Corp"
        assert content["experience"][1]["location"] == ""

    def test_split_still_keeps_legacy_string_experience(self) -> None:
        parsed = _craft_resume_base_payload(
            _catalog_structure(), {"experience": "legacy prose"}
        )
        _, content = candidate_mod.split_craft_resume_base_payload(parsed)
        assert "experience" not in content

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
        parsed = _craft_resume_base_payload(_catalog_structure(), {"experience": jobs})

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
        parsed = _craft_resume_base_payload(_catalog_structure(), {"experience": jobs})
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
                    _catalog_structure(), {"experience": jobs}
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

    def _base_cd(self, jobs: list[dict[str, str]], **extra_sections: Any) -> dict[str, Any]:
        # AST-1270: whitelist = base_resume keys; include every section the payload may send.
        base: dict[str, Any] = {"experience": jobs, "professional_summary": "S"}
        base.update(extra_sections)
        return {"artifacts": {"base_resume": base, "resume_structure": _three_section_structure()}}

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
        err = candidate_mod.validate_draft_job_resume_payload(
            {"experience": "legacy prose"},
            self._base_cd([dict(j) for j in _SAMPLE_EXPERIENCE_JOBS]),
        )
        assert err is not None
        assert "experience_detail" in err

    def test_validate_rejects_non_job_array_experience_object(self) -> None:
        err = candidate_mod.validate_draft_job_resume_payload(
            {"experience": {"company": "Acme"}},
            self._base_cd([dict(j) for j in _SAMPLE_EXPERIENCE_JOBS]),
        )
        assert err is not None
        assert "experience_detail" in err

    def test_tailor_hop_prompts_teach_job_array_and_pin_policy(self) -> None:
        from pathlib import Path

        # AST-1270: draft seed teaches nested resume + experience value types (string or job array).
        # Pin-by-(company, title) remains covered by validate/pin unit tests above; obsolete
        # literal prompt phrases from the AST-997 seed era are not re-asserted here.
        rows = json.loads(Path("data/admin/agent_task.json").read_text(encoding="utf-8"))
        by_key = {r["task_key"]: r for r in rows if r.get("task_key")}
        draft = by_key["draft_job_resume"]["user_prompt"]
        assert '"resume":' in draft
        assert '"deviations"' in draft
        assert "prose string or job array" in draft
        assert "experience remains a single string" not in draft


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


# AST-1047: reusable string → astral candidate id lookup (From bind).
class TestAst1047GetCandidateIdForQuery:
    def _cand(
        self,
        cid: str,
        *,
        contact_email: str = "",
        reply_email: str = "",
        first: str = "",
        last: str = "",
        full: str = "",
        profile: dict | None = None,
    ) -> dict:
        cd: dict = {"contact": {}, "profile": dict(profile or {})}
        if contact_email:
            cd["contact"]["contact_email"] = contact_email
        if reply_email:
            cd["contact"]["reply_email"] = reply_email
        return {
            "astral_candidate_id": cid,
            "first": first,
            "last": last,
            "full": full,
            "state": "NEW_CANDIDATE",
            "candidate_data": cd,
        }

    def test_unique_contact_email_match(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [
            self._cand("c1", contact_email="ada@ex.com", first="Ada"),
            self._cand("c2", contact_email="other@ex.com"),
        ]
        monkeypatch.setattr(candidate_mod, "list_candidates", lambda include_deleted=False: rows)
        assert candidate_mod.get_candidate_id_for_query("ada@ex.com") == "c1"
        assert candidate_mod.get_candidate_id_for_query("ADA@EX.COM") == "c1"

    def test_parseaddr_display_name_uses_email(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [self._cand("c1", contact_email="ada@ex.com")]
        monkeypatch.setattr(candidate_mod, "list_candidates", lambda include_deleted=False: rows)
        assert candidate_mod.get_candidate_id_for_query("Ada Lovelace <ada@ex.com>") == "c1"

    def test_unique_name_column_match(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [self._cand("c1", first="Ada", last="Lovelace", full="Ada Lovelace")]
        monkeypatch.setattr(candidate_mod, "list_candidates", lambda include_deleted=False: rows)
        assert candidate_mod.get_candidate_id_for_query("Ada Lovelace") == "c1"

    def test_transitional_profile_email(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [
            self._cand("c1", profile={"contact_email": "legacy@ex.com", "first": "Leg"}),
        ]
        monkeypatch.setattr(candidate_mod, "list_candidates", lambda include_deleted=False: rows)
        assert candidate_mod.get_candidate_id_for_query("legacy@ex.com") == "c1"

    def test_none_and_ambiguous(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [
            self._cand("c1", contact_email="shared@ex.com"),
            self._cand("c2", contact_email="shared@ex.com"),
            self._cand("c3", contact_email="solo@ex.com"),
        ]
        monkeypatch.setattr(candidate_mod, "list_candidates", lambda include_deleted=False: rows)
        assert candidate_mod.get_candidate_id_for_query("missing@ex.com") is None
        assert candidate_mod.get_candidate_id_for_query("shared@ex.com") is None
        assert candidate_mod.get_candidate_id_for_query("solo@ex.com") == "c3"

    def test_empty_query(self) -> None:
        assert candidate_mod.get_candidate_id_for_query("") is None
        assert candidate_mod.get_candidate_id_for_query("   ") is None

    def test_get_candidate_id_fetch_unchanged(self, monkeypatch: pytest.MonkeyPatch) -> None:
        row = {"astral_candidate_id": "c1"}
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda cid: row)
        assert candidate_mod.get_candidate("c1") is row

    def test_debug_true_emits_style_d(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [self._cand("c1", contact_email="ada@ex.com")]
        monkeypatch.setattr(candidate_mod, "list_candidates", lambda include_deleted=False: rows)
        dbg = MagicMock()
        monkeypatch.setattr(candidate_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(candidate_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(candidate_mod.logger, "debug_detail", MagicMock())
        assert candidate_mod.get_candidate_id_for_query("ada@ex.com", debug=True) == "c1"
        assert dbg.called
        assert dbg.call_args.kwargs["outcome"] == "found|matched"
        dbg.reset_mock()
        candidate_mod.get_candidate_id_for_query("ada@ex.com", debug=False)
        assert not dbg.called


# Branches: slack_user_id path match; initiate_prospect_candidate PROSPECT (AST-1068).
class TestAst1068CandidateSlackLookup:
    def _cand(self, cid: str, **kwargs):
        data = {"contact": {}, "profile": {}}
        if "slack_user_id" in kwargs:
            data["contact"]["slack_user_id"] = kwargs.pop("slack_user_id")
        if "contact_email" in kwargs:
            data["contact"]["contact_email"] = kwargs.pop("contact_email")
        if "profile" in kwargs:
            data["profile"] = kwargs.pop("profile")
        return {"astral_candidate_id": cid, "candidate_data": data, **kwargs}

    def test_lookup_matches_slack_user_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        rows = [
            self._cand("c1", slack_user_id="Uabc"),
            self._cand("c2", contact_email="x@ex.com"),
        ]
        monkeypatch.setattr(candidate_mod, "list_candidates", lambda include_deleted=False: rows)
        assert candidate_mod.get_candidate_id_for_query("Uabc") == "c1"
        assert candidate_mod.get_candidate_id_for_query("UABC") == "c1"

    def test_initiate_prospect_candidate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        saved = {}

        def _save(cid, state=None, candidate_data=None, state_history=None, merge=None, **kwargs):
            saved["cid"] = cid
            saved["state"] = state
            saved["candidate_data"] = candidate_data
            saved["state_history"] = state_history
            saved["kwargs"] = kwargs

        monkeypatch.setattr(candidate_mod, "get_candidate", lambda cid: None)
        monkeypatch.setattr(candidate_mod.database, "save_candidate", _save)
        # AST-1014: names are columns (first=/last=); contact blob holds slack_user_id only.
        candidate_mod.initiate_prospect_candidate(
            "slack-u1",
            {"contact": {"slack_user_id": "U1"}},
            first="Ada",
            last="",
        )
        assert saved["cid"] == "slack-u1"
        assert saved["state"] == "PROSPECT"
        assert saved["candidate_data"] == {"contact": {"slack_user_id": "U1"}}
        assert "profile" not in saved["candidate_data"]
        assert saved["kwargs"].get("first") == "Ada"
        assert saved["kwargs"].get("last") == ""
        assert saved["state_history"] is not None

    def test_initiate_rejects_empty_and_existing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        with pytest.raises(ValueError, match="required"):
            candidate_mod.initiate_prospect_candidate("")
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda cid: {"astral_candidate_id": cid})
        with pytest.raises(ValueError, match="already exists"):
            candidate_mod.initiate_prospect_candidate("slack-u1")



class TestAst1074TopicMenuPersistence:
    """AST-1074: Topic Menu validate / revise / get / save (no wipe)."""

    def _topic(
        self,
        tid: str,
        *,
        name: str | None = None,
        ask: str = "What matters?",
        required: bool = True,
        informs: list | None = None,
        status: str = "open",
    ) -> dict:
        return {
            "id": tid,
            "name": name if name is not None else tid,
            "ask": ask,
            "required": required,
            "informs": list(["backstory"] if informs is None else informs),
            "status": status,
        }

    def test_validate_topic_happy_and_rejects(self) -> None:
        row = candidate_mod.validate_topic(self._topic("t1", informs=["backstory", "rubrics", "backstory"]))
        assert row["informs"] == ["backstory", "rubrics"]
        assert row["status"] == "open"
        with pytest.raises(ValueError, match="required must be a bool"):
            candidate_mod.validate_topic(self._topic("t1", required="yes"))  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="not in TOPIC_MENU_CONFIG"):
            candidate_mod.validate_topic(self._topic("t1", informs=["invented"]))
        with pytest.raises(ValueError, match="non-empty list"):
            candidate_mod.validate_topic(self._topic("t1", informs=[]))

    def test_validate_topic_menu_rejects_duplicate_ids(self) -> None:
        with pytest.raises(ValueError, match="duplicate topic id"):
            candidate_mod.validate_topic_menu(
                {"topics": [self._topic("dup"), self._topic("dup", name="Other")]}
            )

    def test_revise_retires_missing_ids_keeps_content(self) -> None:
        existing = {
            "topics": [
                self._topic("keep", name="Keep", status="ready"),
                self._topic("drop", name="Drop", ask="Old ask?", informs=["strengths"], status="open"),
            ]
        }
        incoming = {
            "topics": [
                self._topic("keep", name="Keep renamed", ask="New ask?", informs=["priorities"], status="ready"),
                self._topic("new", name="New"),
            ]
        }
        out = candidate_mod.revise_topic_menu(existing, incoming)
        by_id = {t["id"]: t for t in out["topics"]}
        assert list(by_id) == ["keep", "new", "drop"]
        assert by_id["keep"]["name"] == "Keep renamed"
        assert by_id["keep"]["ask"] == "New ask?"
        assert by_id["keep"]["informs"] == ["priorities"]
        assert by_id["drop"]["status"] == "retired"
        assert by_id["drop"]["name"] == "Drop"
        assert by_id["drop"]["ask"] == "Old ask?"
        assert by_id["drop"]["informs"] == ["strengths"]

    def test_get_topic_menu_missing_candidate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda cid: None)
        with pytest.raises(ValueError, match="Candidate not found"):
            candidate_mod.get_topic_menu("missing")

    def test_get_topic_menu_normalizes_absent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "candidate_data": {}},
        )
        assert candidate_mod.get_topic_menu("c1") == {"topics": []}

    def test_save_topic_menu_revise_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        stored: dict = {
            "astral_candidate_id": "c1",
            "candidate_data": {
                "topic_menu": {"topics": [self._topic("old", name="Old", status="open")]}
            },
        }
        saves: list = []

        def _get(cid: str):
            return dict(stored)

        def _save_cd(cid: str, data: dict, replace: bool = False, debug: bool = False):
            saves.append({"cid": cid, "data": data, "debug": debug})
            cd = dict(stored.get("candidate_data") or {})
            cd.update(data)
            stored["candidate_data"] = cd

        monkeypatch.setattr(candidate_mod, "get_candidate", _get)
        monkeypatch.setattr(candidate_mod, "save_candidate_data", _save_cd)
        result = candidate_mod.save_topic_menu(
            "c1",
            {"topics": [self._topic("new", name="New")]},
        )
        assert [t["id"] for t in result["topics"]] == ["new", "old"]
        assert result["topics"][1]["status"] == "retired"
        assert saves[0]["data"]["topic_menu"]["topics"][1]["status"] == "retired"
        assert saves[0]["debug"] is False

    def test_save_topic_menu_revise_false_full_replace(self, monkeypatch: pytest.MonkeyPatch) -> None:
        stored: dict = {
            "astral_candidate_id": "c1",
            "candidate_data": {
                "topic_menu": {"topics": [self._topic("old", status="open")]}
            },
        }
        saves: list = []
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda cid: dict(stored))
        monkeypatch.setattr(
            candidate_mod,
            "save_candidate_data",
            lambda cid, data, replace=False, debug=False: saves.append(data),
        )
        result = candidate_mod.save_topic_menu(
            "c1",
            {"topics": [self._topic("only")]},
            revise=False,
        )
        assert [t["id"] for t in result["topics"]] == ["only"]
        assert "old" not in {t["id"] for t in saves[0]["topic_menu"]["topics"]}

    def test_save_topic_menu_debug_gated(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dbg_index = MagicMock()
        dbg_detail = MagicMock()
        monkeypatch.setattr(candidate_mod.logger, "debug_index", dbg_index)
        monkeypatch.setattr(candidate_mod.logger, "debug_detail", dbg_detail)
        monkeypatch.setattr(candidate_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "candidate_data": {}},
        )
        monkeypatch.setattr(candidate_mod, "save_candidate_data", MagicMock())
        candidate_mod.save_topic_menu("c1", {"topics": [self._topic("t1")]}, debug=True)
        assert dbg_index.call_count == 2
        candidate_mod.save_topic_menu("c1", {"topics": [self._topic("t1")]}, debug=False)
        assert dbg_index.call_count == 2



class TestAst1075PreambleConfirmedAt:
    """AST-1075: optional preamble_confirmed_at on topic_menu + mark helper."""

    def _topic(self, tid: str = "t1") -> dict:
        return {
            "id": tid,
            "name": tid,
            "ask": "What matters?",
            "required": True,
            "informs": ["backstory"],
            "status": "open",
        }

    def test_normalize_and_validate_preserve_stamp(self) -> None:
        raw = {"topics": [self._topic()], "preamble_confirmed_at": " 2026-07-30 12:00:00 "}
        norm = candidate_mod.normalize_topic_menu(raw)
        assert norm["preamble_confirmed_at"] == "2026-07-30 12:00:00"
        validated = candidate_mod.validate_topic_menu(raw)
        assert validated["preamble_confirmed_at"] == "2026-07-30 12:00:00"
        assert candidate_mod.normalize_topic_menu({"topics": []}).get("preamble_confirmed_at") is None
        assert "preamble_confirmed_at" not in candidate_mod.normalize_topic_menu(
            {"topics": [], "preamble_confirmed_at": "   "}
        )

    def test_revise_prefers_incoming_stamp(self) -> None:
        existing = {
            "topics": [self._topic("old")],
            "preamble_confirmed_at": "2026-07-30 10:00:00",
        }
        incoming = {
            "topics": [self._topic("new")],
            "preamble_confirmed_at": "2026-07-30 11:00:00",
        }
        out = candidate_mod.revise_topic_menu(existing, incoming)
        assert out["preamble_confirmed_at"] == "2026-07-30 11:00:00"
        keep = candidate_mod.revise_topic_menu(
            existing, {"topics": [self._topic("new")]}
        )
        assert keep["preamble_confirmed_at"] == "2026-07-30 10:00:00"

    def test_mark_stamps_without_wiping_topics(self, monkeypatch: pytest.MonkeyPatch) -> None:
        stored = {
            "astral_candidate_id": "c1",
            "candidate_data": {"topic_menu": {"topics": [self._topic("keep")]}},
        }
        saves: list = []

        def _save(cid, data, replace=False, debug=False):
            saves.append({"data": data, "debug": debug})
            cd = dict(stored.get("candidate_data") or {})
            cd.update(data)
            stored["candidate_data"] = cd

        monkeypatch.setattr(candidate_mod, "get_candidate", lambda cid: dict(stored))
        monkeypatch.setattr(candidate_mod, "save_candidate_data", _save)
        out = candidate_mod.mark_topic_menu_preamble_confirmed(
            "c1", when="2026-07-30 15:00:00"
        )
        assert out["preamble_confirmed_at"] == "2026-07-30 15:00:00"
        assert [t["id"] for t in out["topics"]] == ["keep"]
        assert saves[0]["data"]["topic_menu"]["topics"][0]["id"] == "keep"
        assert saves[0]["data"]["topic_menu"]["preamble_confirmed_at"] == "2026-07-30 15:00:00"

    def test_mark_debug_gated(self, monkeypatch: pytest.MonkeyPatch) -> None:
        dbg = MagicMock()
        monkeypatch.setattr(candidate_mod.logger, "debug_index", dbg)
        monkeypatch.setattr(candidate_mod.logger, "debug_detail", MagicMock())
        monkeypatch.setattr(candidate_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "candidate_data": {}},
        )
        monkeypatch.setattr(candidate_mod, "save_candidate_data", MagicMock())
        candidate_mod.mark_topic_menu_preamble_confirmed("c1", debug=True)
        assert dbg.call_count == 2
        assert dbg.call_args_list[0].kwargs["func"] == "candidate.mark_topic_menu_preamble_confirmed"
        candidate_mod.mark_topic_menu_preamble_confirmed("c1", debug=False)
        assert dbg.call_count == 2


# AST-1081: empty-full recompute + contact.websites list coercion on save.
class TestAst1081ContactShapesSaveContract:
    """AST-1081: save_candidate_data empty/whitespace full → join; websites list coerce."""

    def test_empty_full_recomputes_from_submitted_first_last(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"first": "Old", "last": "Name"},
        )
        candidate_mod.save_candidate_data(
            "c1",
            {"first": "Ada", "last": "Lovelace", "full": "   "},
        )
        assert save.call_args.kwargs["full"] == "Ada Lovelace"
        assert save.call_args.kwargs["first"] == "Ada"
        assert save.call_args.kwargs["last"] == "Lovelace"

    def test_empty_full_falls_back_to_existing_columns(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"first": "Ada", "last": "Lovelace"},
        )
        candidate_mod.save_candidate_data("c1", {"full": ""})
        assert save.call_args.kwargs["full"] == "Ada Lovelace"

    def test_nonempty_full_override_is_stripped(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda candidate_id: {"first": "Ada", "last": "Lovelace"},
        )
        candidate_mod.save_candidate_data(
            "c1",
            {"full": "  Countess of Lovelace  "},
        )
        assert save.call_args.kwargs["full"] == "Countess of Lovelace"

    def test_websites_none_becomes_empty_list(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(
            candidate_mod.database, "get_candidate", lambda candidate_id: {}
        )
        candidate_mod.save_candidate_data(
            "c1", {"contact": {"websites": None, "phone": "555"}}
        )
        assert save.call_args.kwargs["candidate_data"]["contact"]["websites"] == []

    def test_websites_list_strips_and_drops_empties(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(
            candidate_mod.database, "get_candidate", lambda candidate_id: {}
        )
        candidate_mod.save_candidate_data(
            "c1",
            {
                "contact": {
                    "websites": ["  https://a.example  ", "", "  ", "https://b.example"],
                }
            },
        )
        assert save.call_args.kwargs["candidate_data"]["contact"]["websites"] == [
            "https://a.example",
            "https://b.example",
        ]

    def test_websites_non_list_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "save_candidate", MagicMock())
        monkeypatch.setattr(
            candidate_mod.database, "get_candidate", lambda candidate_id: {}
        )
        with pytest.raises(ValueError, match="contact.websites must be a list"):
            candidate_mod.save_candidate_data(
                "c1", {"contact": {"websites": "https://not-a-list.example"}}
            )


# Branches: within collapse; cross hard-fail; Style D; initiate wire (AST-1080).
class TestAst1080ContactUniqueness:
    """AST-1080: contact uniqueness gate on save / initiate via AST-1079 config."""

    def _other(self, cid: str, **contact_fields: object) -> dict:
        return {
            "astral_candidate_id": cid,
            "candidate_data": {"contact": dict(contact_fields)},
        }

    def test_within_dedupe_clears_duplicate_reply_email(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda *_a, **_k: {})
        monkeypatch.setattr(
            candidate_mod, "list_candidates", lambda include_deleted=False: []
        )
        candidate_mod.save_candidate_data(
            "c1",
            {
                "contact": {
                    "contact_email": "Ada@Example.com",
                    "reply_email": "ada@example.com",
                }
            },
        )
        contact = save.call_args.kwargs["candidate_data"]["contact"]
        assert contact["contact_email"] == "Ada@Example.com"
        assert contact["reply_email"] == ""

    def test_within_dedupe_collapses_websites(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda *_a, **_k: {})
        monkeypatch.setattr(
            candidate_mod, "list_candidates", lambda include_deleted=False: []
        )
        candidate_mod.save_candidate_data(
            "c1",
            {
                "contact": {
                    "websites": [
                        "https://a.example",
                        "HTTPS://A.EXAMPLE",
                        "https://b.example",
                    ]
                }
            },
        )
        assert save.call_args.kwargs["candidate_data"]["contact"]["websites"] == [
            "https://a.example",
            "https://b.example",
        ]

    def test_cross_collision_casefold_email_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda *_a, **_k: {})
        monkeypatch.setattr(
            candidate_mod,
            "list_candidates",
            lambda include_deleted=False: [
                self._other("owner", contact_email="Ada@Example.com")
            ],
        )
        with pytest.raises(
            ValueError,
            match=r"This contact info is already used by another candidate \(ada@example\.com\)\.",
        ):
            candidate_mod.save_candidate_data(
                "c2", {"contact": {"contact_email": "ada@example.com"}}
            )
        assert save.call_count == 0

    def test_same_candidate_keeps_own_email(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda *_a, **_k: self._other("c1", contact_email="ada@example.com"),
        )
        monkeypatch.setattr(
            candidate_mod,
            "list_candidates",
            lambda include_deleted=False: [
                self._other("c1", contact_email="ada@example.com")
            ],
        )
        candidate_mod.save_candidate_data(
            "c1", {"contact": {"contact_email": "ada@example.com", "phone": "555"}}
        )
        assert save.call_count == 1
        assert (
            save.call_args.kwargs["candidate_data"]["contact"]["contact_email"]
            == "ada@example.com"
        )

    def test_initiate_candidate_cross_collision(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(
            candidate_mod,
            "list_candidates",
            lambda include_deleted=False: [
                self._other("owner", contact_email="taken@ex.com")
            ],
        )
        with pytest.raises(
            ValueError, match="already used by another candidate"
        ):
            candidate_mod.initiate_candidate(
                "new-c",
                {"contact": {"contact_email": "taken@ex.com"}},
                first="N",
                last="C",
            )
        assert save.call_count == 0

    def test_debug_emits_within_and_cross_outcomes(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        monkeypatch.setattr(candidate_mod.database, "save_candidate", MagicMock())
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda *_a, **_k: {})
        monkeypatch.setattr(
            candidate_mod, "list_candidates", lambda include_deleted=False: []
        )
        caplog.set_level("DEBUG")
        candidate_mod.save_candidate_data(
            "c1",
            {
                "contact": {
                    "contact_email": "solo@ex.com",
                    "reply_email": "solo@ex.com",
                }
            },
            debug=True,
        )
        combined = "\n".join(r.message for r in caplog.records)
        assert "enforce_contact_uniqueness" in combined
        assert "within_dedupe" in combined or "recorded|within_dedupe" in combined
        assert "cross_clear" in combined or "recorded|cross_clear" in combined

class TestAst1085EvaluateJdEmbeddedMerge:
    """AST-1085: append-merge QC/GC into evaluate_jd hydrate / save / generate."""

    _CANDIDATE_ROW = {
        "code": "JD",
        "label": "Job Description Fit",
        "content": "Candidate JD criterion",
        "importance": 5,
        "grade_descriptions": [{"grade": "A", "description": "good"}],
    }

    def test_merge_helper_appends_and_dedupes_by_code(self) -> None:
        from src.utils.config import EMBEDDED_EVALUATE_JD_CRITERIA

        stale_qc = {
            "code": "QC",
            "label": "Stale",
            "content": "operator edit",
            "importance": 9,
            "grade_descriptions": [{"grade": "A", "description": "x"}],
        }
        out = candidate_mod._merge_embedded_evaluate_jd_criteria(
            [self._CANDIDATE_ROW, stale_qc],
        )
        assert [r["code"] for r in out] == ["JD", "QC", "GC"]
        assert out[-2]["label"] == EMBEDDED_EVALUATE_JD_CRITERIA[0]["label"]
        assert out[-2]["importance"] == 1
        assert [r["code"] for r in candidate_mod._merge_embedded_evaluate_jd_criteria([])] == ["QC", "GC"]

    def test_hydrate_appends_qc_gc_after_candidate_rows(self, seeded_db) -> None:
        from src.utils.config import EMBEDDED_EVALUATE_JD_CRITERIA

        db = seeded_db
        db.save_agent_task("evaluate_jd", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1", "evaluate_jd", [self._CANDIDATE_ROW],
        )
        rubric = candidate_mod.rubric_criteria_for_task("cand-1", "evaluate_jd")
        assert [r["code"] for r in rubric] == ["JD", "QC", "GC"]
        assert rubric[-2]["label"] == EMBEDDED_EVALUATE_JD_CRITERIA[0]["label"]
        assert rubric[-1]["label"] == EMBEDDED_EVALUATE_JD_CRITERIA[1]["label"]

        cd: Dict[str, Any] = {"artifacts": {}}
        candidate_mod.hydrate_rubric_artifacts_for_response("cand-1", cd)
        assert [r["code"] for r in cd["artifacts"]["jobdesc_rubric"]] == ["JD", "QC", "GC"]

    def test_other_owners_do_not_gain_qc_gc(self, seeded_db) -> None:
        db = seeded_db
        db.save_agent_task("qualify_job_listings", agent_id="a1", user_prompt="p")
        db.sync_rubric_vectors_from_criteria(
            "cand-1", "qualify_job_listings", [self._CANDIDATE_ROW],
        )
        rubric = candidate_mod.rubric_criteria_for_task("cand-1", "qualify_job_listings")
        assert [r["code"] for r in rubric] == ["JD"]
        assert not any(r["code"] in ("QC", "GC") for r in rubric)

    def test_apply_save_restores_qc_gc_before_sync(self, monkeypatch: pytest.MonkeyPatch) -> None:
        synced: list[tuple[str, str, list]] = []
        monkeypatch.setattr(
            candidate_mod.database,
            "sync_rubric_vectors_from_criteria",
            lambda cid, owner, val: synced.append((cid, owner, list(val))),
        )
        arts: Dict[str, Any] = {"jobdesc_rubric": [self._CANDIDATE_ROW]}
        candidate_mod.apply_rubric_vectors_save("c1085", arts)
        assert "jobdesc_rubric" not in arts
        assert synced[0][:2] == ("c1085", "evaluate_jd")
        assert [r["code"] for r in synced[0][2]] == ["JD", "QC", "GC"]

    def test_craft_jobdesc_generate_merges_into_response_and_stash(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        store = {"astral_candidate_id": "karfo", "candidate_data": {}}
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
        parsed = {"criteria": [self._CANDIDATE_ROW]}
        monkeypatch.setattr(
            candidate_mod,
            "asyncio",
            MagicMock(run=MagicMock(return_value={"success": True, "parsed_response": parsed})),
        )
        body, status = candidate_mod.run_candidate_artifact_generation(
            "karfo", "craft_jobdesc_rubric", None,
        )
        assert status == 200
        assert [r["code"] for r in body["parsed_response"]["criteria"]] == ["JD", "QC", "GC"]
        pending = saves[0][1]["candidate_data"]["pending_craft_generations"]["craft_jobdesc_rubric"]
        assert [r["code"] for r in pending["parsed_response"]["criteria"]] == ["JD", "QC", "GC"]

    def test_persist_craft_jobdesc_merges_before_sync(self, monkeypatch: pytest.MonkeyPatch) -> None:
        synced: list[tuple[str, str, list]] = []
        monkeypatch.setattr(
            candidate_mod.database,
            "sync_rubric_vectors_from_criteria",
            lambda cid, owner, val: synced.append((cid, owner, list(val))),
        )
        # _criterion content includes a trailing grade table so normalize_rubric_artifacts_on_save passes.
        candidate_mod._persist_craft_dispatch_success(
            "c1085",
            "craft_jobdesc_rubric",
            {"criteria": [_criterion(code="JD", label="Job Description Fit")]},
        )
        assert synced
        assert synced[0][1] == "evaluate_jd"
        assert [r["code"] for r in synced[0][2]] == ["JD", "QC", "GC"]



# AST-1092: extra_emails coerce + bind via email_list_paths (not websites).
class TestAst1092ExtraBindingEmails:
    """AST-1092: save coerce extra_emails; get_candidate_id_for_query expands email_list_paths."""

    def test_extra_emails_none_and_list_coerce(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda *_a, **_k: {})
        monkeypatch.setattr(
            candidate_mod, "list_candidates", lambda include_deleted=False: []
        )
        candidate_mod.save_candidate_data(
            "c1", {"contact": {"extra_emails": None, "phone": "555"}}
        )
        assert save.call_args.kwargs["candidate_data"]["contact"]["extra_emails"] == []
        save.reset_mock()
        candidate_mod.save_candidate_data(
            "c1",
            {
                "contact": {
                    "extra_emails": ["  a@ex.com  ", "", "  ", "b@ex.com"],
                }
            },
        )
        assert save.call_args.kwargs["candidate_data"]["contact"]["extra_emails"] == [
            "a@ex.com",
            "b@ex.com",
        ]

    def test_extra_emails_non_list_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "save_candidate", MagicMock())
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda *_a, **_k: {})
        monkeypatch.setattr(
            candidate_mod, "list_candidates", lambda include_deleted=False: []
        )
        with pytest.raises(ValueError, match="contact.extra_emails must be a list"):
            candidate_mod.save_candidate_data(
                "c1", {"contact": {"extra_emails": "solo@ex.com"}}
            )

    def test_lookup_binds_extra_email_not_websites(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        rows = [
            {
                "astral_candidate_id": "c1",
                "first": "",
                "last": "",
                "full": "",
                "candidate_data": {
                    "contact": {
                        "extra_emails": ["Extra@Ex.com"],
                        "websites": ["https://not-an-email.example"],
                    }
                },
            }
        ]
        monkeypatch.setattr(
            candidate_mod, "list_candidates", lambda include_deleted=False: rows
        )
        assert candidate_mod.get_candidate_id_for_query("extra@ex.com") == "c1"
        assert candidate_mod.get_candidate_id_for_query("EXTRA@EX.COM") == "c1"
        # Websites must not participate in email bind
        assert (
            candidate_mod.get_candidate_id_for_query("https://not-an-email.example")
            is None
        )

# Branches: root↔extra shared email pool on uniqueness gate (AST-1095).
class TestAst1095EmailUniqueRootAndExtra:
    """AST-1095: root and extra_emails share casefold email pool across candidates."""

    def _other(self, cid: str, **contact_fields: object) -> dict:
        return {
            "astral_candidate_id": cid,
            "candidate_data": {"contact": dict(contact_fields)},
        }

    def test_cross_root_blocks_extra_add(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda *_a, **_k: {})
        owner = self._other("owner", contact_email="Ada@Example.com")
        monkeypatch.setattr(
            candidate_mod,
            "list_candidates",
            lambda include_deleted=False: [owner],
        )
        with pytest.raises(
            ValueError,
            match=r"This contact info is already used by another candidate \(ada@example\.com\)\.",
        ):
            candidate_mod.save_candidate_data(
                "c2", {"contact": {"extra_emails": ["ada@example.com"]}}
            )
        assert save.call_count == 0
        assert owner["candidate_data"]["contact"]["contact_email"] == "Ada@Example.com"

    def test_cross_extra_blocks_root_add(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda *_a, **_k: {})
        owner = self._other("owner", extra_emails=["Taken@Ex.com"])
        monkeypatch.setattr(
            candidate_mod,
            "list_candidates",
            lambda include_deleted=False: [owner],
        )
        with pytest.raises(
            ValueError,
            match=r"already used by another candidate \(taken@ex\.com\)",
        ):
            candidate_mod.save_candidate_data(
                "c2", {"contact": {"contact_email": "taken@ex.com"}}
            )
        assert save.call_count == 0
        assert owner["candidate_data"]["contact"]["extra_emails"] == ["Taken@Ex.com"]

    def test_cross_extra_blocks_extra_add(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda *_a, **_k: {})
        monkeypatch.setattr(
            candidate_mod,
            "list_candidates",
            lambda include_deleted=False: [
                self._other("owner", extra_emails=["dup@ex.com"])
            ],
        )
        with pytest.raises(ValueError, match="already used by another candidate"):
            candidate_mod.save_candidate_data(
                "c2", {"contact": {"extra_emails": ["DUP@ex.com"]}}
            )
        assert save.call_count == 0

    def test_within_root_and_extra_collapses_extra(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(candidate_mod.database, "get_candidate", lambda *_a, **_k: {})
        monkeypatch.setattr(
            candidate_mod, "list_candidates", lambda include_deleted=False: []
        )
        candidate_mod.save_candidate_data(
            "c1",
            {
                "contact": {
                    "contact_email": "Ada@Example.com",
                    "extra_emails": ["ada@example.com", "other@ex.com"],
                }
            },
        )
        contact = save.call_args.kwargs["candidate_data"]["contact"]
        assert contact["contact_email"] == "Ada@Example.com"
        assert contact["extra_emails"] == ["other@ex.com"]

    def test_initiate_extra_emails_cross_collision(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(
            candidate_mod,
            "list_candidates",
            lambda include_deleted=False: [
                self._other("owner", contact_email="taken@ex.com")
            ],
        )
        with pytest.raises(ValueError, match="already used by another candidate"):
            candidate_mod.initiate_candidate(
                "new-c",
                {"contact": {"extra_emails": ["  taken@ex.com  "]}},
                first="N",
                last="C",
            )
        assert save.call_count == 0

    def test_initiate_prospect_extra_emails_cross_collision(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save = MagicMock()
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        monkeypatch.setattr(
            candidate_mod,
            "list_candidates",
            lambda include_deleted=False: [
                self._other("owner", extra_emails=["taken@ex.com"])
            ],
        )
        with pytest.raises(ValueError, match="already used by another candidate"):
            candidate_mod.initiate_prospect_candidate(
                "new-p",
                {"contact": {"contact_email": "taken@ex.com"}},
                first="N",
                last="C",
            )
        assert save.call_count == 0


# Branches: custom vs default source; DB-row vs token-view contact; empty segments/lines;
# full vs recompute_full_name; non-str/whitespace custom; debug True/False.
# AST-1148: default path expands default_template (not path composition); custom expands too.
class TestAst1137ResolveCoverFromBlock:
    """AST-1137/1148: resolve_cover_from_block custom vs default_template expand."""

    def test_custom_text_wins_and_strips_outer_whitespace(self) -> None:
        out = candidate_mod.resolve_cover_from_block(
            {
                "full": "Ignored Name",
                "candidate_data": {
                    "contact": {
                        "cover_letter_from_block": "  Custom Line 1\nCustom Line 2  ",
                        "location": "Oakland, CA",
                    }
                },
            }
        )
        assert out == {
            "text": "Custom Line 1\nCustom Line 2",
            "source": "candidate",
        }

    def test_whitespace_only_and_non_str_custom_use_default(self) -> None:
        ws = candidate_mod.resolve_cover_from_block(
            {
                "full": "Ada Lovelace",
                "candidate_data": {
                    "contact": {
                        "cover_letter_from_block": "   \n  ",
                        "location": "London, UK",
                        "contact_email": "ada@example.com",
                    }
                },
            }
        )
        assert ws["source"] == "default"
        # Template expand: empty PHONE segment dropped on line 2.
        assert ws["text"] == "Ada Lovelace • London, UK\nada@example.com"

        non_str = candidate_mod.resolve_cover_from_block(
            {
                "full": "Ada Lovelace",
                "candidate_data": {"contact": {"cover_letter_from_block": 42}},
            }
        )
        assert non_str == {"text": "Ada Lovelace", "source": "default"}

    def test_default_omits_empty_segments_and_lines(self) -> None:
        name_only = candidate_mod.resolve_cover_from_block(
            {"full": "Ada Lovelace", "candidate_data": {"contact": {}}}
        )
        assert name_only == {"text": "Ada Lovelace", "source": "default"}

        contact_only = candidate_mod.resolve_cover_from_block(
            {
                "first": "",
                "last": "",
                "full": "",
                "candidate_data": {
                    "contact": {"contact_email": "ada@example.com", "phone": "555"}
                },
            }
        )
        assert contact_only == {
            "text": "ada@example.com • 555",
            "source": "default",
        }

        empty = candidate_mod.resolve_cover_from_block({"candidate_data": {}})
        assert empty == {"text": "", "source": "default"}

    def test_recompute_full_name_when_full_empty(self) -> None:
        out = candidate_mod.resolve_cover_from_block(
            {
                "first": "Ada",
                "last": "Lovelace",
                "full": "  ",
                "candidate_data": {
                    "contact": {
                        "location": "London, UK",
                        "contact_email": "ada@example.com",
                        "phone": "555-0100",
                    }
                },
            }
        )
        assert out == {
            "text": (
                "Ada Lovelace • London, UK\n"
                "ada@example.com • 555-0100"
            ),
            "source": "default",
        }

    def test_token_view_contact_shape(self) -> None:
        out = candidate_mod.resolve_cover_from_block(
            {
                "full": "Ada Lovelace",
                "contact": {
                    "cover_letter_from_block": "From token view",
                    "location": "ignored",
                },
            }
        )
        assert out == {"text": "From token view", "source": "candidate"}

    def test_candidate_data_contact_not_dict_falls_back(self) -> None:
        out = candidate_mod.resolve_cover_from_block(
            {
                "full": "Ada",
                "candidate_data": {"contact": "not-a-dict"},
                "contact": {"location": "should-not-win"},
            }
        )
        assert out == {"text": "Ada", "source": "default"}

    def test_debug_true_custom_and_default_paths(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        idx = MagicMock()
        detail = MagicMock()
        monkeypatch.setattr(candidate_mod.logger, "debug_index", idx)
        monkeypatch.setattr(candidate_mod.logger, "debug_detail", detail)

        candidate_mod.resolve_cover_from_block(
            {
                "astral_candidate_id": "c-custom",
                "candidate_data": {
                    "contact": {"cover_letter_from_block": "Custom"}
                },
            },
            debug=True,
        )
        # Last index is resolve; expand also indexes when debug=True (AST-1148).
        assert idx.call_args.kwargs["func"] == "candidate.resolve_cover_from_block"
        assert idx.call_args.kwargs["identifier"] == "c-custom"
        assert "candidate" in idx.call_args.kwargs["outcome"]
        detail_msgs = [c.args[0] for c in detail.call_args_list]
        assert "source=candidate" in detail_msgs
        assert "text_chars=6" in detail_msgs

        idx.reset_mock()
        detail.reset_mock()
        candidate_mod.resolve_cover_from_block(
            {
                "_astral_candidate_id": "c-default",
                "full": "Ada Lovelace",
                "candidate_data": {
                    "contact": {
                        "location": "London, UK",
                        "contact_email": "ada@example.com",
                    }
                },
            },
            debug=True,
        )
        assert idx.call_args.kwargs["identifier"] == "c-default"
        assert "default" in idx.call_args.kwargs["outcome"]
        detail_msgs = [c.args[0] for c in detail.call_args_list]
        assert "source=default" in detail_msgs
        # AST-1148 expand details replace AST-1137 line*_segments composition logs.
        assert "tokens_found=4" in detail_msgs
        assert "separator_rewrite=yes" in detail_msgs

        idx.reset_mock()
        detail.reset_mock()
        candidate_mod.resolve_cover_from_block(
            {"full": "Ada", "candidate_data": {"contact": {}}},
            debug=False,
        )
        assert idx.call_count == 0
        assert detail.call_count == 0


class TestAst1148ExpandCoverFromBlock:
    """AST-1148: expand_cover_from_block_text + resolve token/| rewrite + aliases left as-is."""

    def _cand(self, **contact: object) -> dict:
        return {
            "astral_candidate_id": "c-1148",
            "full": "Ada Lovelace",
            "first": "Ada",
            "last": "Lovelace",
            "candidate_data": {
                "contact": {
                    "location": "London, UK",
                    "contact_email": "ada@example.com",
                    "phone": "555-0100",
                    **contact,
                }
            },
        }

    def test_expand_tokens_pipe_and_drop_empty(self) -> None:
        text = candidate_mod.expand_cover_from_block_text(
            "{$FULL_NAME} | {$LOCATION}\n{$CONTACT_EMAIL} | {$PHONE}",
            self._cand(phone=""),
            source="default",
        )
        assert text == "Ada Lovelace • London, UK\nada@example.com"

    def test_expand_leaves_unknown_and_brief_aliases(self) -> None:
        text = candidate_mod.expand_cover_from_block_text(
            "{$FULL_NAME} | {$RESUME_LOCATION} | {$GITHUB}",
            self._cand(),
            source="session",
        )
        # RESUME_LOCATION / GITHUB not allowlisted → left as-is; empty segments not applicable.
        assert text == "Ada Lovelace • {$RESUME_LOCATION} • {$GITHUB}"

    def test_resolve_custom_tokens_and_pipe(self) -> None:
        out = candidate_mod.resolve_cover_from_block(
            self._cand(
                cover_letter_from_block=(
                    "{$FULL_NAME} | {$LOCATION}\n{$CONTACT_EMAIL} | {$PHONE}"
                )
            )
        )
        assert out["source"] == "candidate"
        assert out["text"] == (
            "Ada Lovelace • London, UK\n"
            "ada@example.com • 555-0100"
        )

    def test_resolve_clearing_custom_returns_default_template(self) -> None:
        out = candidate_mod.resolve_cover_from_block(
            self._cand(cover_letter_from_block="   \n\t  ")
        )
        assert out["source"] == "default"
        assert out["text"] == (
            "Ada Lovelace • London, UK\n"
            "ada@example.com • 555-0100"
        )

    def test_expand_debug_style_d(self, monkeypatch: pytest.MonkeyPatch) -> None:
        idx = MagicMock()
        detail = MagicMock()
        monkeypatch.setattr(candidate_mod.logger, "debug_index", idx)
        monkeypatch.setattr(candidate_mod.logger, "debug_detail", detail)
        candidate_mod.expand_cover_from_block_text(
            "{$FULL_NAME} | {$LOCATION}\n{$BOGUS}",
            self._cand(),
            source="session",
            debug=True,
        )
        assert idx.call_args.kwargs["func"] == "candidate.expand_cover_from_block_text"
        assert idx.call_args.kwargs["identifier"] == "c-1148"
        assert "session" in idx.call_args.kwargs["outcome"]
        msgs = [c.args[0] for c in detail.call_args_list]
        assert "source=session" in msgs
        assert "tokens_found=3" in msgs
        assert "tokens_resolved=2" in msgs
        assert "tokens_left_as_is=1" in msgs
        assert "separator_rewrite=yes" in msgs
        assert any(m.startswith("text_chars=") for m in msgs)

        idx.reset_mock()
        detail.reset_mock()
        candidate_mod.expand_cover_from_block_text(
            "plain", self._cand(), source="candidate", debug=False
        )
        assert idx.call_count == 0
        assert detail.call_count == 0



class TestAst1235SurferConsent:
    """AST-1235: versioned Surfer consent normalize / is_current / opt-in / opt-out."""

    def test_normalize_empty_and_unknown(self) -> None:
        empty = candidate_mod.empty_surfer_consent()
        assert empty == {
            "status": "none",
            "accepted_version": None,
            "updated_at": None,
        }
        assert candidate_mod.normalize_surfer_consent(None) == empty
        assert candidate_mod.normalize_surfer_consent("x") == empty
        assert candidate_mod.normalize_surfer_consent({"status": "weird"})["status"] == "none"
        # Extra keys dropped.
        n = candidate_mod.normalize_surfer_consent(
            {
                "status": "opted_in",
                "accepted_version": " 1 ",
                "updated_at": " 2026-01-01 00:00:00 ",
                "extra": True,
            }
        )
        assert n == {
            "status": "opted_in",
            "accepted_version": "1",
            "updated_at": "2026-01-01 00:00:00",
        }
        assert "extra" not in n

    def test_is_current_requires_opt_in_and_matching_version(self) -> None:
        from src.utils.config import SURFER_CONSENT_CONFIG

        ver = SURFER_CONSENT_CONFIG["current_version"]
        assert candidate_mod.is_surfer_consent_current(
            {"status": "opted_in", "accepted_version": ver}
        )
        assert not candidate_mod.is_surfer_consent_current(
            {"status": "opted_in", "accepted_version": "stale"}
        )
        assert not candidate_mod.is_surfer_consent_current(
            {"status": "opted_out", "accepted_version": ver}
        )
        assert not candidate_mod.is_surfer_consent_current({"status": "none"})

    def test_get_surfer_consent_missing_and_absent(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda cid: None)
        with pytest.raises(ValueError, match="Candidate not found"):
            candidate_mod.get_surfer_consent("missing")
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "candidate_data": {}},
        )
        assert candidate_mod.get_surfer_consent("c1") == candidate_mod.empty_surfer_consent()

    def test_opt_in_persists_and_rejects_stale_version(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import SURFER_CONSENT_CONFIG

        ver = SURFER_CONSENT_CONFIG["current_version"]
        stored: dict = {"astral_candidate_id": "c1", "candidate_data": {}}
        saves: list = []

        def _get(cid: str):
            return dict(stored)

        def _save(cid: str, data: dict, replace: bool = False, debug: bool = False):
            saves.append({"data": data, "debug": debug})
            cd = dict(stored.get("candidate_data") or {})
            cd.update(data)
            stored["candidate_data"] = cd

        monkeypatch.setattr(candidate_mod, "get_candidate", _get)
        monkeypatch.setattr(candidate_mod, "save_candidate_data", _save)
        monkeypatch.setattr(candidate_mod, "_surfer_consent_now", lambda: "2026-08-07 12:00:00")

        with pytest.raises(ValueError, match="non-empty string"):
            candidate_mod.opt_in_surfer_consent("c1", "")
        with pytest.raises(ValueError, match="does not match"):
            candidate_mod.opt_in_surfer_consent("c1", "stale")

        dto = candidate_mod.opt_in_surfer_consent("c1", ver)
        assert dto["status"] == "opted_in"
        assert dto["accepted_version"] == ver
        assert dto["is_current"] is True
        assert dto["current_version"] == ver
        assert dto["disclosure_copy"] == SURFER_CONSENT_CONFIG["disclosure_copy"]
        assert saves[0]["data"]["surfer_consent"] == {
            "status": "opted_in",
            "accepted_version": ver,
            "updated_at": "2026-08-07 12:00:00",
        }

    def test_opt_out_preserves_accepted_version(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils.config import SURFER_CONSENT_CONFIG

        ver = SURFER_CONSENT_CONFIG["current_version"]
        stored: dict = {
            "astral_candidate_id": "c1",
            "candidate_data": {
                "surfer_consent": {
                    "status": "opted_in",
                    "accepted_version": ver,
                    "updated_at": "2026-08-07 11:00:00",
                }
            },
        }
        saves: list = []

        def _save(cid: str, data: dict, replace: bool = False, debug: bool = False):
            saves.append(data)
            cd = dict(stored.get("candidate_data") or {})
            cd.update(data)
            stored["candidate_data"] = cd

        monkeypatch.setattr(candidate_mod, "get_candidate", lambda cid: dict(stored))
        monkeypatch.setattr(candidate_mod, "save_candidate_data", _save)
        monkeypatch.setattr(candidate_mod, "_surfer_consent_now", lambda: "2026-08-07 12:30:00")

        dto = candidate_mod.opt_out_surfer_consent("c1")
        assert dto["status"] == "opted_out"
        assert dto["accepted_version"] == ver
        assert dto["is_current"] is False
        assert saves[0]["surfer_consent"]["accepted_version"] == ver
        assert saves[0]["surfer_consent"]["status"] == "opted_out"

    def test_opt_in_debug_gated(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.utils.config import SURFER_CONSENT_CONFIG
        from unittest.mock import MagicMock

        ver = SURFER_CONSENT_CONFIG["current_version"]
        stored = {"astral_candidate_id": "c1", "candidate_data": {}}
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda cid: dict(stored))
        monkeypatch.setattr(
            candidate_mod,
            "save_candidate_data",
            lambda cid, data, replace=False, debug=False: None,
        )
        monkeypatch.setattr(candidate_mod, "_surfer_consent_now", lambda: "t")
        idx = MagicMock()
        detail = MagicMock()
        monkeypatch.setattr(candidate_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(candidate_mod.logger, "debug_index", idx)
        monkeypatch.setattr(candidate_mod.logger, "debug_detail", detail)

        candidate_mod.opt_in_surfer_consent("c1", ver, debug=True)
        assert idx.call_count == 2
        assert detail.call_count == 2
        idx.reset_mock()
        detail.reset_mock()
        candidate_mod.opt_in_surfer_consent("c1", ver, debug=False)
        assert idx.call_count == 0
        assert detail.call_count == 0


class TestAst1237SurferConsentDtoChrome:
    """AST-1237: surfer_consent_dto exposes config chrome fields."""

    def test_dto_includes_chrome_keys(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.utils.config import SURFER_CONSENT_CONFIG

        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "candidate_data": {}},
        )
        dto = candidate_mod.surfer_consent_dto("c1")
        assert dto["current_version"] == SURFER_CONSENT_CONFIG["current_version"]
        assert dto["disclosure_title"] == SURFER_CONSENT_CONFIG["disclosure_title"]
        assert dto["opt_in_label"] == SURFER_CONSENT_CONFIG["opt_in_label"]
        assert dto["decline_label"] == SURFER_CONSENT_CONFIG["decline_label"]
        assert dto["current_ok_title"] == SURFER_CONSENT_CONFIG["current_ok_title"]
        assert dto["current_ok_body"] == SURFER_CONSENT_CONFIG["current_ok_body"]
        assert dto["is_current"] is False


class TestAst1238SurferConsentGate:
    """AST-1238: require_current_surfer_consent + off-switch DTO chrome."""

    def test_require_raises_when_not_current(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.utils.config import SURFER_CONSENT_CONFIG

        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "candidate_data": {}},
        )
        with pytest.raises(ValueError, match="not enabled"):
            candidate_mod.require_current_surfer_consent("c1")
        assert SURFER_CONSENT_CONFIG["capture_denied_message"]

    def test_require_returns_dto_when_current(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.utils.config import SURFER_CONSENT_CONFIG

        ver = SURFER_CONSENT_CONFIG["current_version"]
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda cid: {
                "astral_candidate_id": cid,
                "candidate_data": {
                    "surfer_consent": {
                        "status": "opted_in",
                        "accepted_version": ver,
                        "updated_at": "2026-08-07 12:00:00",
                    }
                },
            },
        )
        dto = candidate_mod.require_current_surfer_consent("c1")
        assert dto["is_current"] is True
        assert dto["off_switch_heading"] == SURFER_CONSENT_CONFIG["off_switch_heading"]
        assert dto["status_stale_label"] == SURFER_CONSENT_CONFIG["status_stale_label"]
        assert dto["capture_denied_message"] == SURFER_CONSENT_CONFIG["capture_denied_message"]


class TestAst1259CandidateBatchApi:
    """AST-1259: get_new_candidate_batch / clear_candidate_batch core wrappers."""

    def test_requires_batch_id_or_context(self) -> None:
        with pytest.raises(ValueError, match="batch_id or context"):
            candidate_mod.get_new_candidate_batch("REQUESTED_ARTIFACTS")

    def test_rejects_unknown_state(self) -> None:
        with pytest.raises(ValueError, match="state must be one of"):
            candidate_mod.get_new_candidate_batch("NOT_A_STATE", batch_id="b")

    def test_claims_and_returns_rows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        claim = MagicMock()
        rows: List[Dict[str, Any]] = [{"astral_candidate_id": "c1", "state": "REQUESTED_ARTIFACTS"}]
        monkeypatch.setattr(candidate_mod.database, "claim_candidate_batch", claim)
        monkeypatch.setattr(candidate_mod.database, "get_candidate_batch", lambda batch_id: rows)
        bid, out = candidate_mod.get_new_candidate_batch(
            "REQUESTED_ARTIFACTS",
            batch_id="fixed-1259",
            limit=2,
            sort_by="updated_at",
            states=["REQUESTED_ARTIFACTS", "REQUESTED_ARTIFACTS_RETRY"],
        )
        assert bid == "fixed-1259"
        assert out == rows
        claim.assert_called_once_with(
            "fixed-1259",
            "REQUESTED_ARTIFACTS",
            2,
            sort_by="updated_at",
            states=["REQUESTED_ARTIFACTS", "REQUESTED_ARTIFACTS_RETRY"],
        )

    def test_generates_batch_id_from_context(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod.database, "claim_candidate_batch", MagicMock())
        monkeypatch.setattr(candidate_mod.database, "get_candidate_batch", lambda batch_id: [])
        bid, _ = candidate_mod.get_new_candidate_batch("ACTIVE_SEARCH", context="inflow_discovery")
        assert bid.startswith("inflow_discovery-")

    def test_clear_delegates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        clear = MagicMock(return_value=3)
        monkeypatch.setattr(candidate_mod.database, "clear_candidate_batch", clear)
        assert candidate_mod.clear_candidate_batch("b-1") == 3
        clear.assert_called_once_with("b-1")


class TestAst1270NestedDraftJobResumeContract:
    """AST-1270: unwrap agent_payload.resume; whitelist base_resume keys; deviations metadata."""

    # Parent brief sample keys (subset) — enough to prove nest + whitelist without full prose dump.
    _BASE_SECTIONS = {
        "candidate_name": "Susan Somerset",
        "candidate_title": "Senior Technical PM",
        "candidate_tagline": "Cloud Platforms",
        "candidate_contact_detail": "hire@example.com",
        "professional_summary": "Summary prose",
        "core_competencies": "Skills",
        "prior_experience": "Prior",
        "education_certifications": "CSM",
        "technical_skills": "Python",
    }

    def _base_sections(self) -> dict[str, Any]:
        out = dict(self._BASE_SECTIONS)
        out["experience"] = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        return out

    def _cd(self, *, with_structure: bool = False) -> dict[str, Any]:
        arts: dict[str, Any] = {"base_resume": self._base_sections()}
        if with_structure:
            arts["resume_structure"] = candidate_mod.default_resume_structure()
        return {"artifacts": arts}

    def test_allowed_section_keys_intersect_known_ids(self) -> None:
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        cd = {
            "artifacts": {
                "base_resume": {
                    "professional_summary": "S",
                    "experience": jobs,
                    "highlights": "Won awards",
                    "accent_color": "#fff",
                    "sections": "reserved",
                    "123bad": "x",
                }
            }
        }
        assert candidate_mod.draft_job_resume_allowed_section_keys(cd) == [
            "experience",
            "highlights",
            "professional_summary",
        ]

    def test_nested_envelope_validates_and_unwraps_resume(self) -> None:
        # Nested sample shape from parent AST-1268 — resume body + sibling deviations.
        resume_body = {k: f"tailored-{k}" for k in self._BASE_SECTIONS}
        resume_body["experience"] = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        parsed: dict[str, Any] = {
            "agent_performance": {"status": "success", "failure_note": ""},
            "agent_payload": {
                "resume": resume_body,
                "deviations": ["Skipped UAT claim — not confirmed in materials."],
            },
        }
        err = candidate_mod.validate_draft_job_resume_payload(parsed, self._cd())
        assert err is None
        ap = parsed["agent_payload"]
        assert "resume" not in ap
        assert ap["professional_summary"] == "tailored-professional_summary"
        assert ap["deviations"] == ["Skipped UAT claim — not confirmed in materials."]

    def test_unknown_key_inside_resume_still_fails(self) -> None:
        parsed = {
            "agent_payload": {
                "resume": {"professional_summary": "ok", "bogus_section": "nope"},
                "deviations": [],
            }
        }
        err = candidate_mod.validate_draft_job_resume_payload(parsed, self._cd())
        assert err is not None
        assert "bogus_section" in err
        assert "base_resume keys" in err

    def test_resume_never_reported_as_unknown_section_after_normalize(self) -> None:
        parsed = {
            "agent_payload": {
                "resume": {
                    "professional_summary": "ok",
                    "experience": [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS],
                },
            }
        }
        candidate_mod.normalize_draft_job_resume_agent_payload(parsed)
        assert "resume" not in parsed["agent_payload"]
        err = candidate_mod.validate_draft_job_resume_payload(parsed, self._cd())
        assert err is None

    def test_no_persisted_resume_structure_still_passes(self) -> None:
        payload = {
            "professional_summary": "S",
            "experience": [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS],
        }
        # Explicitly no artifacts.resume_structure — whitelist is base_resume only.
        assert candidate_mod.validate_draft_job_resume_payload(payload, self._cd(with_structure=False)) is None

    def test_empty_base_resume_fails_clearly(self) -> None:
        err = candidate_mod.validate_draft_job_resume_payload(
            {"professional_summary": "S"},
            {"artifacts": {}},
        )
        assert err == "candidate has no base_resume section keys"

    def test_non_dict_resume_nest_fails_explicitly(self) -> None:
        err = candidate_mod.validate_draft_job_resume_payload(
            {"agent_payload": {"resume": "not-an-object", "professional_summary": "S"}},
            self._cd(),
        )
        assert err is not None
        assert "must be an object of resume sections" in err

    def test_flat_payload_still_accepted(self) -> None:
        # AST-594-era callers: section keys flat on agent_payload (no nest).
        payload = {
            "professional_summary": "S",
            "experience": [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS],
        }
        assert candidate_mod.validate_draft_job_resume_payload(payload, self._cd()) is None

    def test_manage_tasks_prompt_nested_contract(self) -> None:
        from pathlib import Path

        rows = json.loads(Path("data/admin/agent_task.json").read_text(encoding="utf-8"))
        by_key = {r["task_key"]: r for r in rows if r.get("task_key")}
        draft = by_key["draft_job_resume"]["user_prompt"]
        assert '"resume":' in draft
        assert '"deviations"' in draft
        assert "experience remains a single string" not in draft
        assert "prose string or job array" in draft
        # Nested envelope example only (no flat-only agent_payload section-key sample).
        assert '"agent_payload": {\n    "resume"' in draft


class TestAst1272DraftHopDebugWhitelistTrail:
    """AST-1272: Style D unwrap + whitelist/accept/reject trails when debug=True."""

    def _cd(self) -> dict[str, Any]:
        return {
            "artifacts": {
                "base_resume": {
                    "professional_summary": "base summary",
                    "experience": [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS],
                }
            }
        }

    def _patch_debug(self, monkeypatch: pytest.MonkeyPatch) -> tuple[Any, Any]:
        idx = MagicMock()
        detail = MagicMock()
        monkeypatch.setattr(candidate_mod.logger, "set_debug_flag", MagicMock())
        monkeypatch.setattr(candidate_mod.logger, "debug_index", idx)
        monkeypatch.setattr(candidate_mod.logger, "debug_detail", detail)
        return idx, detail

    def _detail_msgs(self, detail: Any) -> list[str]:
        return [c.args[0] for c in detail.call_args_list]

    def test_normalize_debug_popped_emits_unwrap_trail(self, monkeypatch: pytest.MonkeyPatch) -> None:
        idx, detail = self._patch_debug(monkeypatch)
        parsed = {
            "agent_payload": {
                "resume": {"professional_summary": "S", "experience": "E"},
                "astral_job_id": "job-1272",
            }
        }
        candidate_mod.normalize_draft_job_resume_agent_payload(parsed, debug=True)
        assert "resume" not in parsed["agent_payload"]
        idx.assert_called_once()
        kwargs = idx.call_args.kwargs
        assert kwargs["func"] == "candidate.normalize_draft_job_resume_agent_payload"
        assert kwargs["outcome"] == "unwrap popped"
        assert kwargs["identifier"] == "job-1272"
        msgs = self._detail_msgs(detail)
        assert any("unwrap=popped" in m for m in msgs)
        assert any("nested_section_count=2" in m for m in msgs)

    def test_normalize_debug_flat_and_invalid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        idx, detail = self._patch_debug(monkeypatch)
        candidate_mod.normalize_draft_job_resume_agent_payload(
            {"agent_payload": {"professional_summary": "S"}}, debug=True
        )
        assert idx.call_args.kwargs["outcome"] == "unwrap flat"
        assert any("unwrap=flat" in m for m in self._detail_msgs(detail))

        idx.reset_mock()
        detail.reset_mock()
        candidate_mod.normalize_draft_job_resume_agent_payload(
            {"agent_payload": {"resume": "not-a-dict"}}, debug=True
        )
        assert idx.call_args.kwargs["outcome"] == "unwrap invalid"
        assert any("unwrap=invalid" in m for m in self._detail_msgs(detail))

    def test_normalize_debug_false_is_silent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        idx, detail = self._patch_debug(monkeypatch)
        candidate_mod.normalize_draft_job_resume_agent_payload(
            {"agent_payload": {"resume": {"professional_summary": "S"}}}, debug=False
        )
        idx.assert_not_called()
        detail.assert_not_called()

    def test_validate_debug_ok_records_whitelist_and_accepted(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        idx, detail = self._patch_debug(monkeypatch)
        # Flat payload — validate's internal normalize stays quiet (debug=False).
        err = candidate_mod.validate_draft_job_resume_payload(
            {
                "agent_payload": {
                    "professional_summary": "S",
                    "experience": [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS],
                }
            },
            self._cd(),
            debug=True,
        )
        assert err is None
        # Only validate trail (no unwrap index from internal normalize).
        assert idx.call_count == 1
        assert idx.call_args.kwargs["func"] == "candidate.validate_draft_job_resume_payload"
        assert idx.call_args.kwargs["outcome"] == "ok"
        msgs = self._detail_msgs(detail)
        assert any("whitelist_source=base_resume" in m and "experience" in m for m in msgs)
        assert any("recorded accepted_keys=" in m and "experience" in m for m in msgs)
        assert any("recorded rejected_keys=[]" in m for m in msgs)
        assert any("recorded error=none" in m for m in msgs)

    def test_validate_debug_reject_records_unknown_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        idx, detail = self._patch_debug(monkeypatch)
        err = candidate_mod.validate_draft_job_resume_payload(
            {"agent_payload": {"bogus_section": "x"}},
            self._cd(),
            debug=True,
        )
        assert err is not None
        assert "bogus_section" in err
        assert idx.call_args.kwargs["outcome"] == "reject"
        msgs = self._detail_msgs(detail)
        assert any("recorded rejected_keys=" in m and "bogus_section" in m for m in msgs)
        assert any("recorded error=" in m and "bogus_section" in m for m in msgs)

    def test_validate_debug_false_is_silent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        idx, detail = self._patch_debug(monkeypatch)
        assert (
            candidate_mod.validate_draft_job_resume_payload(
                {
                    "professional_summary": "S",
                    "experience": [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS],
                },
                self._cd(),
                debug=False,
            )
            is None
        )
        idx.assert_not_called()
        detail.assert_not_called()


class TestAst1287ForceTransition:
    """AST-1287: keyword-only force= on transition_candidate_state."""

    def test_force_applies_illegal_hop_and_appends_history(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "NEW_CANDIDATE", "state_history": []},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.transition_candidate_state("somerset", "ACTIVE_SEARCH", force=True)
        assert save.call_args.kwargs["state"] == "ACTIVE_SEARCH"
        hist = save.call_args.kwargs["state_history"]
        assert hist[-1]["from_state"] == "NEW_CANDIDATE"
        assert hist[-1]["to_state"] == "ACTIVE_SEARCH"

    def test_default_force_false_still_rejects_illegal(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "NEW_CANDIDATE", "state_history": []},
        )
        with pytest.raises(candidate_mod.IllegalCandidateTransition) as ei:
            candidate_mod.transition_candidate_state("somerset", "ACTIVE_SEARCH")
        assert ei.value.from_state == "NEW_CANDIDATE"
        assert ei.value.to_state == "ACTIVE_SEARCH"

    def test_force_cannot_invent_unknown_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "NEW_CANDIDATE", "state_history": []},
        )
        with pytest.raises(ValueError, match="Unknown candidate state") as ei:
            candidate_mod.transition_candidate_state("somerset", "LIVE_PROMPTS", force=True)
        assert not isinstance(ei.value, candidate_mod.IllegalCandidateTransition)

    def test_same_state_illegal_without_force(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # No core same-state no-op — ACTIVE_SEARCH is not in its own prior_states
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "ACTIVE_SEARCH", "state_history": []},
        )
        with pytest.raises(candidate_mod.IllegalCandidateTransition):
            candidate_mod.transition_candidate_state("somerset", "ACTIVE_SEARCH")

    def test_force_on_legal_hop_still_succeeds(self, monkeypatch: pytest.MonkeyPatch) -> None:
        save = MagicMock()
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda _cid: {"state": "NEW_CANDIDATE", "state_history": []},
        )
        monkeypatch.setattr(candidate_mod.database, "save_candidate", save)
        candidate_mod.transition_candidate_state("somerset", "INTAKE_INITIATED", force=True)
        assert save.call_args.kwargs["state"] == "INTAKE_INITIATED"
        assert save.call_args.kwargs["state_history"][-1]["to_state"] == "INTAKE_INITIATED"


# Branches: required-seven gate; extra slug accept/reject; format default/lock/strip.
class TestAst1303ResumeStructureCatalog:
    """AST-1303: required seven + open extras + closed format on normalize."""

    def test_seven_only_fills_formats_and_strips_contact_format(self) -> None:
        raw = _required_seven_structure()
        raw["sections"]["candidate_name"]["format"] = "free_prose"
        out = candidate_mod.normalize_resume_structure(raw)
        assert set(out["sections"]) == set(RESUME_STRUCTURE_REQUIRED_SECTION_IDS)
        for sid in RESUME_STRUCTURE_CONTACT_SECTION_IDS:
            assert "format" not in out["sections"][sid]
        for sid in ("professional_summary", "core_competencies", "experience"):
            assert out["sections"][sid]["format"] == RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID[sid]

    def test_highlights_and_publications_persist_as_bullet_list(self) -> None:
        raw = _required_seven_structure()
        raw["sections"]["highlights"] = {
            "id": "highlights",
            "title": "Highlights",
            "enabled": True,
            "order": 10,
            "format": "bullet_list",
        }
        raw["sections"]["publications"] = {
            "id": "publications",
            "title": "Publications",
            "enabled": True,
            "order": 11,
            "job_agent_editable": True,
            "format": "bullet_list",
        }
        out = candidate_mod.normalize_resume_structure(raw)
        assert out["sections"]["highlights"]["format"] == "bullet_list"
        assert out["sections"]["highlights"]["job_agent_editable"] is True
        assert out["sections"]["publications"]["title"] == "Publications"
        assert out["sections"]["publications"]["format"] == "bullet_list"

    def test_required_title_change_keeps_id(self) -> None:
        raw = _required_seven_structure()
        raw["sections"]["professional_summary"]["title"] = "Summary"
        out = candidate_mod.normalize_resume_structure(raw)
        assert "professional_summary" in out["sections"]
        assert out["sections"]["professional_summary"]["id"] == "professional_summary"
        assert out["sections"]["professional_summary"]["title"] == "Summary"

    def test_omitting_required_section_raises(self) -> None:
        raw = _required_seven_structure()
        del raw["sections"]["experience"]
        with pytest.raises(ValueError, match="missing required"):
            candidate_mod.normalize_resume_structure(raw)

    def test_disabling_required_section_raises(self) -> None:
        raw = _required_seven_structure()
        raw["sections"]["professional_summary"]["enabled"] = False
        with pytest.raises(ValueError, match="cannot be disabled"):
            candidate_mod.normalize_resume_structure(raw)

    def test_ten_id_blob_without_format_keys_still_normalizes(self) -> None:
        raw = candidate_mod.default_resume_structure()
        for spec in raw["sections"].values():
            spec.pop("format", None)
        out = candidate_mod.normalize_resume_structure(raw)
        for sid, fmt in RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID.items():
            assert out["sections"][sid]["format"] == fmt

    def test_reserved_and_invalid_extra_ids_rejected(self) -> None:
        for bad in ("sections", "AccentColor", "1bad", "has-dash"):
            raw = _required_seven_structure()
            raw["sections"][bad] = {
                "id": bad,
                "title": "Extra",
                "enabled": True,
                "order": 20,
                "format": "bullet_list",
            }
            with pytest.raises(ValueError, match="invalid extra section id"):
                candidate_mod.normalize_resume_structure(raw)

    def test_extra_requires_closed_format(self) -> None:
        raw = _required_seven_structure()
        raw["sections"]["highlights"] = {
            "id": "highlights",
            "title": "Highlights",
            "enabled": True,
            "order": 10,
            "job_agent_editable": True,
        }
        with pytest.raises(ValueError, match="requires format"):
            candidate_mod.normalize_resume_structure(raw)
        raw["sections"]["highlights"]["format"] = "header"
        with pytest.raises(ValueError, match="must be one of"):
            candidate_mod.normalize_resume_structure(raw)

    def test_experience_format_locked_and_extra_may_use_experience_detail(self) -> None:
        raw = _required_seven_structure()
        raw["sections"]["experience"]["format"] = "word_cloud"
        with pytest.raises(ValueError, match="must be experience_detail"):
            candidate_mod.normalize_resume_structure(raw)
        raw = _required_seven_structure()
        raw["sections"]["publications"] = {
            "id": "publications",
            "title": "Publications",
            "enabled": True,
            "order": 11,
            "job_agent_editable": True,
            "format": "experience_detail",
        }
        out = candidate_mod.normalize_resume_structure(raw)
        assert out["sections"]["publications"]["format"] == "experience_detail"
        assert out["sections"]["experience"]["format"] == "experience_detail"
        assert set(RESUME_STRUCTURE_BODY_FORMATS) >= {"bullet_list", "experience_detail"}


# Branches: slug title→id; reserved/empty reject; pending rekey; duplicate after slug.
class TestAst1306ResumeStructureSavePrep:
    """AST-1306: slug_resume_section_id + prepare_resume_structure_sections_for_save."""

    def test_slug_from_title_and_rejects_reserved_or_empty(self) -> None:
        assert candidate_mod.slug_resume_section_id("Highlights") == "highlights"
        assert candidate_mod.slug_resume_section_id("  Prior Experience  ") == "prior_experience"
        with pytest.raises(ValueError, match="invalid extra section title"):
            candidate_mod.slug_resume_section_id("!!!")
        with pytest.raises(ValueError, match="invalid extra section id"):
            candidate_mod.slug_resume_section_id("Content")

    def test_prepare_rekeys_pending_and_rejects_duplicate_slug(self) -> None:
        raw = _required_seven_structure()["sections"]
        raw["_pending_0"] = {
            "id": "_pending_0",
            "title": "Highlights",
            "enabled": True,
            "order": 10,
            "format": "bullet_list",
            "job_agent_editable": True,
        }
        out = candidate_mod.prepare_resume_structure_sections_for_save(raw)
        assert "highlights" in out
        assert out["highlights"]["id"] == "highlights"
        assert "_pending_0" not in out
        raw["_pending_1"] = {
            "id": "_pending_1",
            "title": "Highlights",
            "enabled": True,
            "order": 11,
            "format": "bullet_list",
            "job_agent_editable": True,
        }
        with pytest.raises(ValueError, match="duplicate section id after slug"):
            candidate_mod.prepare_resume_structure_sections_for_save(raw)


class TestAst1304FilterContentToResumeStructure:
    """AST-1304: filter keep-loop widens extras; leftover Experience prose stays in the dict."""

    def _structure(self) -> dict[str, Any]:
        raw = candidate_mod.default_resume_structure()
        raw["sections"]["highlights"] = {
            "id": "highlights",
            "title": "Highlights",
            "enabled": True,
            "order": 10,
            "job_agent_editable": True,
            "format": "bullet_list",
        }
        raw["sections"]["consulting_roles"] = {
            "id": "consulting_roles",
            "title": "Consulting",
            "enabled": True,
            "order": 11,
            "job_agent_editable": True,
            "format": "experience_detail",
        }
        return raw

    def test_keeps_leftover_experience_prose(self) -> None:
        out = candidate_mod.filter_content_to_resume_structure(
            {"experience": "leftover prose", "orphan_section": "drop"},
            self._structure(),
        )
        assert out["experience"] == "leftover prose"
        assert "orphan_section" not in out

    def test_keeps_extra_job_array_on_any_enabled_id(self) -> None:
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        out = candidate_mod.filter_content_to_resume_structure(
            {"consulting_roles": jobs},
            self._structure(),
        )
        assert out["consulting_roles"] == jobs

    def test_coerces_extra_scalar_list_to_newline_string(self) -> None:
        out = candidate_mod.filter_content_to_resume_structure(
            {"highlights": ["Won award", "Spoke at PyCon"]},
            self._structure(),
        )
        assert out["highlights"] == "Won award\nSpoke at PyCon"

    def test_drops_mixed_dict_list_that_is_not_a_job_array(self) -> None:
        out = candidate_mod.filter_content_to_resume_structure(
            {"highlights": [{"x": 1}, "nope"]},
            self._structure(),
        )
        assert "highlights" not in out


class TestAst1305HopsContentBlobsAndLegacyLabels:
    """AST-1305: extra keys on hops; Abrams labels kept; Experience is job-array only."""

    def _abrams_list(self, *, experience: Any = "leftover prose") -> list[dict[str, Any]]:
        return [
            {"label": "Professional Summary", "content": "Summary body"},
            {"label": "Highlights", "content": "Won awards"},
            {"label": "Publications", "content": "Paper one"},
            {"label": "Experience", "content": experience},
        ]

    def _seven(self) -> dict[str, Any]:
        return _required_seven_structure()

    def test_ingest_label_list_keeps_highlights_and_publications(self) -> None:
        content, structure = candidate_mod.ingest_legacy_label_content_base_resume(
            self._abrams_list(), self._seven()
        )
        assert content["professional_summary"] == "Summary body"
        assert content["highlights"] == "Won awards"
        assert content["publications"] == "Paper one"
        assert "experience" not in content
        for sid, title in (("highlights", "Highlights"), ("publications", "Publications")):
            spec = structure["sections"][sid]
            assert spec["title"] == title
            assert spec["enabled"] is True
            assert spec["job_agent_editable"] is True
            assert spec["format"] == RESUME_STRUCTURE_EXTRA_DEFAULT_FORMAT == "bullet_list"

    def test_ingest_dict_extra_id_and_slug_collision(self) -> None:
        content, structure = candidate_mod.ingest_legacy_label_content_base_resume(
            {"professional_summary": "S", "highlights": "H", "experience": "prose"},
            self._seven(),
        )
        assert content == {"professional_summary": "S", "highlights": "H"}
        assert structure["sections"]["highlights"]["format"] == "bullet_list"
        _, collided = candidate_mod.ingest_legacy_label_content_base_resume(
            [
                {"label": "Highlights", "content": "one"},
                {"label": "Highlights", "content": "two"},
            ],
            self._seven(),
        )
        assert "highlights" in collided["sections"]
        assert "highlights_2" in collided["sections"]

    def test_token_keeps_unmatched_labels_and_omits_prose_experience(self) -> None:
        cd = {
            "artifacts": {
                "resume_structure": self._seven(),
                "base_resume": self._abrams_list(),
            }
        }
        parsed = json.loads(candidate_mod.format_base_resume_for_token(cd))
        assert parsed["highlights"] == "Won awards"
        assert parsed["publications"] == "Paper one"
        assert parsed["professional_summary"] == "Summary body"
        assert "experience" not in parsed

    def test_flatten_promotes_extra_keys_outside_known(self) -> None:
        raw = self._seven()
        raw["sections"]["highlights"] = {
            "id": "highlights",
            "title": "Highlights",
            "enabled": True,
            "order": 20,
            "job_agent_editable": True,
            "format": "bullet_list",
        }
        parsed = {
            "resume_structure": {
                "sections": raw["sections"],
                "content": {"highlights": "Won awards", "professional_summary": "S"},
            }
        }
        candidate_mod._flatten_craft_resume_section_strings(parsed)
        assert parsed["highlights"] == "Won awards"
        assert parsed["professional_summary"] == "S"

    def test_draft_whitelist_includes_extras_rejects_invented(self) -> None:
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        cd = {
            "artifacts": {
                "base_resume": {
                    "professional_summary": "S",
                    "highlights": "H",
                    "experience": jobs,
                }
            }
        }
        assert candidate_mod.draft_job_resume_allowed_section_keys(cd) == [
            "experience",
            "highlights",
            "professional_summary",
        ]
        assert (
            candidate_mod.validate_draft_job_resume_payload(
                {"professional_summary": "S", "highlights": "H2"}, cd
            )
            is None
        )
        err = candidate_mod.validate_draft_job_resume_payload({"not_on_base": "x"}, cd)
        assert err is not None
        assert "Unknown resume section key" in err
        assert "not_on_base" in err

    def test_split_and_filter_omit_prose_experience(self) -> None:
        parsed = _craft_resume_base_payload(self._seven(), {"experience": "leftover prose"})
        _, content = candidate_mod.split_craft_resume_base_payload(parsed)
        assert "experience" not in content
        filtered = candidate_mod.filter_base_resume_to_structure(
            {"experience": "leftover prose", "professional_summary": "S"},
            {"experience", "professional_summary"},
        )
        assert filtered == {"professional_summary": "S"}
        jobs = [dict(job) for job in _SAMPLE_EXPERIENCE_JOBS]
        assert candidate_mod.filter_base_resume_to_structure(
            {"experience": jobs}, {"experience"}
        ) == {"experience": jobs}

    def test_education_title_maps_on_seven_only(self) -> None:
        content, structure = candidate_mod.ingest_legacy_label_content_base_resume(
            [{"label": "Education & Certifications", "content": "CSM"}],
            self._seven(),
        )
        assert content["education_certifications"] == "CSM"
        assert "education_certifications" in structure["sections"]
        assert (
            structure["sections"]["education_certifications"]["format"]
            == RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID["education_certifications"]
        )
