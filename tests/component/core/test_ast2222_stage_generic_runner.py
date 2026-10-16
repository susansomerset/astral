"""AST-2222: stage-generic candidate chain runner (REQUESTED_RESUME + artifacts regression)."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core import candidate as candidate_mod
from src.core import consult as consult_mod
from src.utils.config import (
    BASE_RESUME_CHAIN_TASK_KEYS,
    TASK_CONFIG,
    dispatch_hop_label,
    error_state_for,
)

_REPO = Path(__file__).resolve().parents[3]
_PILOT = "candidate.artifacts.base_resume"
_STRUCTURE = "candidate.artifacts.resume_structure"


def _resume_blob(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "candidate_name": "Ada Lovelace",
        "candidate_title": "Engineer",
        "candidate_contact_detail": "ada@example.com",
        "professional_summary": "summary",
        "core_competencies": "python",
        "experience": [
            {
                "company": "Analytical",
                "title": "Engineer",
                "start_date": "2020-01",
                "end_date": "Present",
                "accomplishments": ["Built engines"],
            }
        ],
    }
    body.update(overrides)
    return body


def _hop_payload(task_key: str) -> dict[str, Any]:
    schema = TASK_CONFIG[task_key]["response_schema"]
    out: dict[str, Any] = {}
    for field, spec in schema.items():
        if field == "experience":
            out[field] = _resume_blob()["experience"]
        elif field == "resume_structure":
            out[field] = candidate_mod.default_resume_structure()
        elif isinstance(spec, dict) and spec.get("type") == "str":
            out[field] = f"{field}-value"
        else:
            out[field] = "x"
    return out


class TestAst2222StageGenericHelpers:
    """Claim walk + membership helpers for every CANDIDATE_STAGE_DISPATCH stage."""

    def test_claim_states_for_both_stages(self) -> None:
        arts = candidate_mod.requested_artifacts_dispatch_claim_states()
        assert "REQUESTED_ARTIFACTS" in arts
        assert "REQUESTED_ARTIFACTS_RETRY" in arts
        assert dispatch_hop_label("REQUESTED_ARTIFACTS", "craft_get_rubric") in arts

        resume = candidate_mod.candidate_stage_dispatch_claim_states("REQUESTED_RESUME")
        assert resume[:2] == ["REQUESTED_RESUME", "REQUESTED_RESUME_RETRY"]
        for tk in BASE_RESUME_CHAIN_TASK_KEYS:
            assert dispatch_hop_label("REQUESTED_RESUME", tk) in resume
        # Hop-label input still expands from bare trigger.
        via_hop = candidate_mod.candidate_stage_dispatch_claim_states(
            dispatch_hop_label("REQUESTED_RESUME", "draft_highlights"),
        )
        assert via_hop == resume

    def test_is_candidate_stage_chain_task(self) -> None:
        assert candidate_mod.is_candidate_stage_chain_task("shape_the_story") is True
        assert candidate_mod.is_candidate_stage_chain_task("craft_get_rubric") is True
        assert candidate_mod.is_candidate_stage_chain_task("grade_do") is False

    def test_ac6_ac7_source_scans(self) -> None:
        # Ticket AC 6 / AC 7 — dispatcher + consult stay stage-generic.
        ban = (
            "shape_the_story|draft_resume_experiences|draft_supporting_sections|"
            "draft_highlights|draft_core_competencies|draft_professional_summary|"
            "draft_keywords|BASE_RESUME_CHAIN"
        )
        import re

        for rel in ("src/core/dispatcher.py", "src/core/consult.py"):
            text = (_REPO / rel).read_text(encoding="utf-8")
            assert 'CANDIDATE_STAGE_DISPATCH["requested_artifacts"]' not in text, rel
            assert re.search(ban, text) is None, rel


class TestAst2222PersistCraftDispatch:
    """AC 10 / AC 11 persist gate: title_patterns contact write; intermediate no-op."""

    def test_title_patterns_str_and_list(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls: list[tuple] = []
        monkeypatch.setattr(
            candidate_mod,
            "save_candidate_data",
            lambda cid, data, *a, **k: calls.append((cid, data)) or None,
        )
        candidate_mod._persist_craft_dispatch_success(
            "c1", "draft_title_patterns", {"title_patterns": "Eng.*\nSr Eng"},
        )
        assert calls == [("c1", {"contact": {"title_patterns": "Eng.*\nSr Eng"}})]
        calls.clear()
        candidate_mod._persist_craft_dispatch_success(
            "c1", "draft_title_patterns", {"title_patterns": ["Eng.*", "", "Sr Eng"]},
        )
        assert calls == [("c1", {"contact": {"title_patterns": "Eng.*\nSr Eng"}})]

    def test_intermediate_noop_and_junk_still_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls: list = []
        monkeypatch.setattr(
            candidate_mod,
            "save_candidate_data",
            lambda *a, **k: calls.append((a, k)) or None,
        )
        candidate_mod._persist_craft_dispatch_success("c1", "shape_the_story", {"story": "x"})
        candidate_mod._persist_craft_dispatch_success(
            "c1", "draft_highlights", {"highlights": "h"},
        )
        assert calls == []
        with pytest.raises(ValueError, match="unsupported craft task_key"):
            candidate_mod._persist_craft_dispatch_success("c1", "grade_do", {"x": 1})


class TestAst2222RequestedResumeDispatch:
    """Runner pass / retry→error / mid-chain resume start (AC 8 slice, AC 12, AC 13)."""

    @pytest.mark.asyncio
    async def test_success_lands_resume_ready(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda cid: {
                "astral_candidate_id": cid,
                "state": "REQUESTED_RESUME",
                "candidate_data": {},
            },
        )
        do = AsyncMock(return_value={"success": True, "parsed_response": {"story": "x"}})
        monkeypatch.setattr(candidate_mod, "do_task", do)
        trans = MagicMock()
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", trans)
        out = await candidate_mod.run_requested_artifacts_dispatch(
            "c1", task_key="shape_the_story", trigger_state="REQUESTED_RESUME",
        )
        assert out["total_passed"] == 1
        assert do.await_args.kwargs["task_key"] == "shape_the_story"
        assert do.await_args.kwargs["ctx"].get("persist_candidate_craft_hops") is True
        assert do.await_args.kwargs["ctx"].get("dispatch_trigger_state") == "REQUESTED_RESUME"
        trans.assert_called_once_with("c1", "RESUME_READY")

    @pytest.mark.asyncio
    async def test_retry_then_hop_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda cid: {
                "astral_candidate_id": cid,
                "state": "REQUESTED_RESUME",
                "candidate_data": {},
            },
        )
        monkeypatch.setattr(
            candidate_mod, "do_task", AsyncMock(return_value={"success": False, "error": "fail"}),
        )
        trans = MagicMock()
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", trans)
        out = await candidate_mod.run_requested_artifacts_dispatch(
            "c1", task_key="shape_the_story", trigger_state="REQUESTED_RESUME",
        )
        assert out["total_failed"] == 1
        trans.assert_called_once_with("c1", "REQUESTED_RESUME_RETRY")

        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda cid: {
                "astral_candidate_id": cid,
                "state": "REQUESTED_RESUME_RETRY",
                "candidate_data": {},
            },
        )
        trans.reset_mock()
        out = await candidate_mod.run_requested_artifacts_dispatch(
            "c1", task_key="shape_the_story", trigger_state="REQUESTED_RESUME",
        )
        assert out["total_errors"] == 1
        trans.assert_called_once_with("c1", error_state_for("shape_the_story"))

    @pytest.mark.asyncio
    async def test_mid_chain_resume_starts_at_next_hop(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AC 12: state REQUESTED_RESUME.draft_highlights → consult resumes draft_core_competencies.
        hop = dispatch_hop_label("REQUESTED_RESUME", "draft_highlights")
        monkeypatch.setattr(
            candidate_mod.database,
            "get_candidate",
            lambda cid: {"astral_candidate_id": cid, "state": hop, "candidate_data": {}},
        )
        do = AsyncMock(return_value={"success": True, "parsed_response": {}})
        monkeypatch.setattr(candidate_mod, "do_task", do)
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", MagicMock())
        await candidate_mod.run_requested_artifacts_dispatch(
            "c1",
            task_key="draft_core_competencies",
            trigger_state="REQUESTED_RESUME",
        )
        assert do.await_args.kwargs["task_key"] == "draft_core_competencies"
        assert do.await_args.kwargs["task_key"] != "shape_the_story"


class TestAst2222ResumeChainSeededSmoke:
    """AC 8–11: mocked chain walk rotates base_resume, tagline→meta, title_patterns, assembler-only arts."""

    @pytest.mark.asyncio
    async def test_walk_persist_tagline_patterns_and_artifact_growth(
        self, seeded_db, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.core import builder as builder_mod

        db = seeded_db
        cid = "cand-1"
        prior = candidate_mod.save_candidate_data(cid, _PILOT, _resume_blob(candidate_tagline="old"))
        db.save_candidate(cid, state="REQUESTED_RESUME")
        before_base = len(db.list_artifacts("candidate", cid, "base_resume", current_only=False) or [])
        before_struct = len(
            db.list_artifacts("candidate", cid, "resume_structure", current_only=False) or []
        )
        tagline = "distributed systems"
        patterns = "Engineer.*\nLead.*"
        walked: list[str] = []
        # Component sqlite has no agent_task seed — walk the registry order (same as live run_next).
        nxt = {
            BASE_RESUME_CHAIN_TASK_KEYS[i]: BASE_RESUME_CHAIN_TASK_KEYS[i + 1]
            for i in range(len(BASE_RESUME_CHAIN_TASK_KEYS) - 1)
        }

        async def _fake_do_task(*, task_key, ctx, index, **_kw):
            hop = task_key
            while hop:
                walked.append(hop)
                if hop == "draft_resume_base":
                    blob = _resume_blob(candidate_tagline=tagline)
                    candidate_mod.save_candidate_data(index, _PILOT, blob)
                    candidate_mod.save_candidate_data(
                        index, _STRUCTURE, candidate_mod.default_resume_structure(),
                    )
                elif hop == "draft_title_patterns":
                    candidate_mod._persist_craft_dispatch_success(
                        index, hop, {"title_patterns": patterns},
                    )
                else:
                    candidate_mod._persist_craft_dispatch_success(index, hop, _hop_payload(hop))
                if ctx.get("suppress_run_next"):
                    break
                hop = nxt.get(hop, "")
            return {"success": True, "parsed_response": {}}

        monkeypatch.setattr(candidate_mod, "do_task", _fake_do_task)
        out = await candidate_mod.run_requested_artifacts_dispatch(
            cid, task_key="shape_the_story", trigger_state="REQUESTED_RESUME",
        )
        assert out["total_passed"] == 1
        assert walked == list(BASE_RESUME_CHAIN_TASK_KEYS)
        row = db.get_candidate(cid)
        assert row["state"] == "RESUME_READY"
        current = db.get_current_artifact("candidate", cid, "base_resume")
        assert current["artifact_uuid"] != prior
        assert current["artifact_data"].get("candidate_tagline") == tagline
        assert (row["candidate_data"].get("contact") or {}).get("title_patterns") == patterns
        # Assembler-only growth: +1 base_resume version and +1 resume_structure version.
        assert len(db.list_artifacts("candidate", cid, "base_resume", current_only=False)) == before_base + 1
        assert (
            len(db.list_artifacts("candidate", cid, "resume_structure", current_only=False))
            == before_struct + 1
        )
        html = builder_mod.build_base_resume(cid)
        assert f"specializing in {tagline}" in html
        assert (
            f'<meta name="description" content="Resume of Ada Lovelace, Engineer, specializing in {tagline}"'
            in html
        )

class TestAst2222ConsultRoutesResumeStage:
    """Consult routes REQUESTED_RESUME (+ hop resume) to the shared stage worker."""

    @pytest.mark.asyncio
    async def test_routes_shape_the_story(self, monkeypatch: pytest.MonkeyPatch) -> None:
        worker = AsyncMock(
            return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}
        )
        monkeypatch.setattr("src.core.candidate.run_requested_artifacts_dispatch", worker)
        entity = {"astral_candidate_id": "c-resume", "state": "REQUESTED_RESUME"}
        out = await consult_mod.run_consult_task(
            "candidate",
            "REQUESTED_RESUME",
            [entity],
            "b1",
            entity,
            False,
            dispatch_task_key="shape_the_story",
        )
        assert out["total_passed"] == 1
        worker.assert_awaited_once()
        assert worker.await_args.args[0] == "c-resume"
        assert worker.await_args.kwargs.get("task_key") == "shape_the_story"
        assert worker.await_args.kwargs.get("trigger_state") == "REQUESTED_RESUME"

    @pytest.mark.asyncio
    async def test_routes_mid_hop_resume(self, monkeypatch: pytest.MonkeyPatch) -> None:
        worker = AsyncMock(
            return_value={"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}
        )
        monkeypatch.setattr("src.core.candidate.run_requested_artifacts_dispatch", worker)
        hop = dispatch_hop_label("REQUESTED_RESUME", "draft_highlights")
        entity = {"astral_candidate_id": "c-mid", "state": hop}
        out = await consult_mod.run_consult_task(
            "candidate",
            "REQUESTED_RESUME",
            [entity],
            "b1",
            entity,
            False,
            dispatch_task_key="draft_core_competencies",
        )
        assert out["total_passed"] == 1
        assert worker.await_args.kwargs.get("task_key") == "draft_core_competencies"
