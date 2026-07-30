"""Component tests for src/ui/api/api_intake.py (AST-558)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from flask.testing import FlaskClient

from ui.api import api_intake as intake_mod


class TestIntakeRoutes:
    def test_create_session_requires_auth(self, intake_client: FlaskClient) -> None:
        assert intake_client.post("/api/candidates/cand-1/intake/sessions", json={}).status_code == 401

    def test_create_session_missing_candidate_404(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(intake_mod, "get_candidate", lambda candidate_id: None)
        resp = intake_client.post(
            "/api/candidates/missing/intake/sessions",
            json={"starting_resume_text": "resume"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_create_session_201_shape(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(intake_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        monkeypatch.setattr(
            intake_mod,
            "create_intake_session_and_start",
            AsyncMock(
                return_value={
                    "session_id": "sess-1",
                    "status": "ACTIVE",
                    "transcript": [],
                    "ready_to_build": False,
                    "can_build": False,
                    "build_completed": False,
                    "awaiting_agent": True,
                }
            ),
        )
        resp = intake_client.post(
            "/api/candidates/cand-1/intake/sessions",
            json={"starting_resume_text": "Resume body"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["session_id"] == "sess-1"
        assert body["transcript"] == []
        assert body["awaiting_agent"] is True
        assert "batch_id" not in body

    def test_create_session_validation_error_400(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(intake_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        monkeypatch.setattr(
            intake_mod,
            "create_intake_session_and_start",
            AsyncMock(side_effect=ValueError("starting_resume_text is required")),
        )
        resp = intake_client.post(
            "/api/candidates/cand-1/intake/sessions",
            json={"starting_resume_text": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "starting_resume_text" in resp.get_json()["error"]

    def test_create_session_duplicate_active_409(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(intake_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        monkeypatch.setattr(
            intake_mod,
            "create_intake_session_and_start",
            AsyncMock(side_effect=ValueError("active intake session already exists for candidate")),
        )
        resp = intake_client.post(
            "/api/candidates/cand-1/intake/sessions",
            json={"starting_resume_text": "Resume body"},
            headers=auth_headers,
        )
        assert resp.status_code == 409
        assert "already exists" in resp.get_json()["error"]

    def test_get_active_session_404_when_none(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(intake_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        monkeypatch.setattr(intake_mod, "fetch_active_intake_session", lambda candidate_id: None)
        resp = intake_client.get("/api/candidates/cand-1/intake/sessions/active", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_active_session_returns_dto(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        row = {"intake_session_id": "sess-1", "candidate_id": "cand-1", "status": "ACTIVE", "transcript": [], "last_ready_to_build": True}
        monkeypatch.setattr(intake_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        monkeypatch.setattr(intake_mod, "fetch_active_intake_session", lambda candidate_id: row)
        monkeypatch.setattr(
            intake_mod,
            "get_intake_session_dto",
            lambda r, **kwargs: {
                "session_id": r["intake_session_id"],
                "status": "ACTIVE",
                "transcript": [],
                "ready_to_build": True,
                "can_build": True,
                "build_completed": False,
            },
        )
        resp = intake_client.get("/api/candidates/cand-1/intake/sessions/active", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["can_build"] is True

    def test_post_build_maps_value_error_to_400(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(intake_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        monkeypatch.setattr(
            intake_mod,
            "fetch_intake_session",
            lambda session_id: {"intake_session_id": session_id, "candidate_id": "cand-1"},
        )
        monkeypatch.setattr(
            intake_mod,
            "post_intake_build",
            AsyncMock(side_effect=ValueError("build already completed for this session")),
        )
        resp = intake_client.post(
            "/api/candidates/cand-1/intake/sessions/sess-1/build",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "build already completed" in resp.get_json()["error"]

    def test_post_turn_runtime_error_includes_batch_id(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(intake_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        monkeypatch.setattr(
            intake_mod,
            "fetch_intake_session",
            lambda session_id: {"intake_session_id": session_id, "candidate_id": "cand-1"},
        )
        monkeypatch.setattr(
            intake_mod,
            "post_intake_turn",
            AsyncMock(side_effect=RuntimeError('{"error": "model failed", "batch_id": "intake-intake_candidate_response-x"}')),
        )
        resp = intake_client.post(
            "/api/candidates/cand-1/intake/sessions/sess-1/turns",
            json={"message": "hello"},
            headers=auth_headers,
        )
        assert resp.status_code == 500
        body = resp.get_json()
        assert body["error"] == "model failed"
        assert body["batch_id"] == "intake-intake_candidate_response-x"


class TestAst1015PreambleValidateRoute:
    """AST-1015: POST /api/candidates/<id>/preamble/validate thin wrapper."""

    def test_requires_auth(self, intake_client: FlaskClient) -> None:
        assert (
            intake_client.post(
                "/api/candidates/cand-1/preamble/validate",
                json={"question": "Q?", "answer": "A"},
            ).status_code
            == 401
        )

    def test_success_200_shape(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            intake_mod,
            "validate_preamble_answer",
            AsyncMock(
                return_value={
                    "success": True,
                    "outcome": "Valid",
                    "error": None,
                    "batch_id": "preamble-preamble_validate_response-x",
                }
            ),
        )
        resp = intake_client.post(
            "/api/candidates/cand-1/preamble/validate",
            json={"question": "Q?", "answer": "A", "step_index": 1, "step_total": 3},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body == {
            "success": True,
            "outcome": "Valid",
            "error": None,
            "batch_id": "preamble-preamble_validate_response-x",
        }

    def test_candidate_missing_404(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            intake_mod,
            "validate_preamble_answer",
            AsyncMock(side_effect=ValueError("Candidate not found: missing")),
        )
        resp = intake_client.post(
            "/api/candidates/missing/preamble/validate",
            json={"question": "Q?", "answer": "A"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_question_required_400(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            intake_mod,
            "validate_preamble_answer",
            AsyncMock(side_effect=ValueError("question required")),
        )
        resp = intake_client.post(
            "/api/candidates/cand-1/preamble/validate",
            json={"question": "", "answer": "A"},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "question" in resp.get_json()["error"]

    def test_structured_failure_still_200(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            intake_mod,
            "validate_preamble_answer",
            AsyncMock(
                return_value={
                    "success": False,
                    "outcome": None,
                    "error": "invalid preamble validation outcome: 'Nope'",
                    "batch_id": "preamble-preamble_validate_response-y",
                }
            ),
        )
        resp = intake_client.post(
            "/api/candidates/cand-1/preamble/validate",
            json={"question": "Q?", "answer": "A"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["success"] is False
        assert resp.get_json()["outcome"] is None



class TestAst1075TopicMenuRoutes:
    """AST-1075: POST topic-menu/confirm and topic-menu/generate thin wrappers."""

    def test_confirm_requires_auth(self, intake_client: FlaskClient) -> None:
        assert (
            intake_client.post(
                "/api/candidates/cand-1/topic-menu/confirm",
                json={},
            ).status_code
            == 401
        )

    def test_confirm_success_200(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            intake_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id},
        )
        monkeypatch.setattr(
            intake_mod,
            "run_topic_menu_preamble_confirm",
            AsyncMock(
                return_value={
                    "success": True,
                    "outcome": "continue",
                    "assistant_message": "Anything here you would change?",
                    "applied_patches": [],
                    "packet": {"context": {"raw_resume": "x"}},
                    "batch_id": "intake-topic_menu_preamble_confirm-x",
                    "error": None,
                }
            ),
        )
        resp = intake_client.post(
            "/api/candidates/cand-1/topic-menu/confirm",
            json={"message": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        assert body["outcome"] == "continue"
        assert "Anything here you would change?" in body["assistant_message"]

    def test_confirm_candidate_missing_404(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(intake_mod, "get_candidate", lambda candidate_id: None)
        resp = intake_client.post(
            "/api/candidates/missing/topic-menu/confirm",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_confirm_structured_failure_500(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            intake_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id},
        )
        monkeypatch.setattr(
            intake_mod,
            "run_topic_menu_preamble_confirm",
            AsyncMock(
                return_value={
                    "success": False,
                    "error": "invalid confirm outcome: 'Valid'",
                    "batch_id": "b",
                    "outcome": None,
                    "assistant_message": None,
                    "applied_patches": [],
                    "packet": {},
                }
            ),
        )
        resp = intake_client.post(
            "/api/candidates/cand-1/topic-menu/confirm",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 500
        assert "invalid confirm outcome" in resp.get_json()["error"]

    def test_generate_success_200(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            intake_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id},
        )
        monkeypatch.setattr(
            intake_mod,
            "generate_topic_menu_from_preamble",
            AsyncMock(
                return_value={
                    "success": True,
                    "menu": {"topics": [{"id": "t1"}], "preamble_confirmed_at": "t"},
                    "batch_id": "intake-topic_menu_generate-x",
                    "rejected_topic_count": 0,
                    "informs_covered": ["backstory"],
                    "error": None,
                }
            ),
        )
        resp = intake_client.post(
            "/api/candidates/cand-1/topic-menu/generate",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        assert body["menu"]["topics"][0]["id"] == "t1"
        assert body["informs_covered"] == ["backstory"]

    def test_generate_not_confirmed_400(
        self, intake_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            intake_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id},
        )
        monkeypatch.setattr(
            intake_mod,
            "generate_topic_menu_from_preamble",
            AsyncMock(side_effect=ValueError("preamble not confirmed; run confirm accept first")),
        )
        resp = intake_client.post(
            "/api/candidates/cand-1/topic-menu/generate",
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "preamble not confirmed" in resp.get_json()["error"]
