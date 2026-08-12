"""Component tests for src/ui/api/api_candidate.py (AST-394)."""

from __future__ import annotations

import base64
from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from ui.api import api_candidate as candidate_mod


class TestSanitizeCandidate:
    def test_strips_api_key_and_sets_flag(self) -> None:
        row = {"candidate_api_key": "secret", "state": "NEW_CANDIDATE"}
        out = candidate_mod._sanitize_candidate(row)
        assert out["has_api_key"] is True
        assert "candidate_api_key" not in out


def _tiny_jpeg_bytes(height: int, width: int) -> bytes:
    """Minimal JPEG bytes readable by `_jpeg_dimensions` (SOF0 stub; AST-394 / AST-366 tests)."""
    body = bytearray(bytes.fromhex("ffd8ffc0000b088000000801011100"))
    body[7:9] = height.to_bytes(2, "big")
    body[9:11] = width.to_bytes(2, "big")
    return bytes(body)


def _tiny_jpeg_data_url(height: int, width: int) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(_tiny_jpeg_bytes(height, width)).decode("ascii")


class TestJpegDimensions:
    def test_none_when_truncated_after_magic(self) -> None:
        assert candidate_mod._jpeg_dimensions(b"\xff\xd8\xff") is None

    def test_none_when_not_jpeg_magic(self) -> None:
        assert candidate_mod._jpeg_dimensions(b"\x00\x01\x02\xff") is None

    def test_none_when_reserved_byte_where_marker_expected(self) -> None:
        # After SOI, marker stream must restart with 0xFF; stray byte breaks sync.
        assert candidate_mod._jpeg_dimensions(b"\xff\xd8\x99\xff\xc0000b088012000801011100") is None

    def test_none_when_marker_segment_length_is_too_short(self) -> None:
        # Needs len >= SOF scan horizon (loop guard i+9 < len); seg_len unpack must still trip <2 branch.
        raw = bytes.fromhex("ffd8ffc40001000000000000")
        assert candidate_mod._jpeg_dimensions(raw) is None

    def test_reads_sof0_dimensions(self) -> None:
        assert candidate_mod._jpeg_dimensions(_tiny_jpeg_bytes(8, 12)) == (12, 8)

    def test_reads_progressive_sof2_marker_dimensions(self) -> None:
        body = bytearray(bytes.fromhex("ffd8ffc2000b088000000801011100"))
        body[7:9] = (9).to_bytes(2, "big")
        body[9:11] = (11).to_bytes(2, "big")
        assert candidate_mod._jpeg_dimensions(bytes(body)) == (11, 9)

    def test_skips_app0_marker_segment_before_sof0(self) -> None:
        app0 = bytes.fromhex("ffd8ffe000104a46494600010100000100010000")
        combined = app0 + _tiny_jpeg_bytes(8, 31)[2:]
        assert candidate_mod._jpeg_dimensions(combined) == (31, 8)


class TestCoverLetterSignatureValidation:
    def test_none_and_empty_accepted(self) -> None:
        candidate_mod._validate_cover_letter_signature_image(None)
        candidate_mod._validate_cover_letter_signature_image("")

    def test_rejects_non_string(self) -> None:
        with pytest.raises(ValueError, match="must be a string"):
            candidate_mod._validate_cover_letter_signature_image(42)

    def test_rejects_non_jpeg_prefix(self) -> None:
        with pytest.raises(ValueError, match="JPEG data URL"):
            candidate_mod._validate_cover_letter_signature_image("data:image/png;base64,abcd")

    def test_rejects_invalid_base64(self) -> None:
        with pytest.raises(ValueError, match="valid base64"):
            candidate_mod._validate_cover_letter_signature_image(
                "data:image/jpeg;base64,%%%not!!!"
            )

    def test_rejects_non_jpeg_magic(self) -> None:
        blob = base64.standard_b64encode(b"GIF87a").decode("ascii")
        with pytest.raises(ValueError, match="valid JPEG"):
            candidate_mod._validate_cover_letter_signature_image(f"data:image/jpeg;base64,{blob}")

    def test_rejects_truncated_marker_stream(self) -> None:
        raw = b"\xff\xd8\xff\xe0\x00\x10"
        blob = base64.standard_b64encode(raw).decode("ascii")
        with pytest.raises(ValueError, match="valid JPEG"):
            candidate_mod._validate_cover_letter_signature_image(f"data:image/jpeg;base64,{blob}")

    def test_rejects_dimensions_over_max(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod, "_MAX_COVER_SIG_W", 4)
        monkeypatch.setattr(candidate_mod, "_MAX_COVER_SIG_H", 4)
        big = _tiny_jpeg_data_url(100, 400)
        with pytest.raises(ValueError, match="pixels"):
            candidate_mod._validate_cover_letter_signature_image(big)

    def test_accepts_bounded_jpeg(self) -> None:
        candidate_mod._validate_cover_letter_signature_image(_tiny_jpeg_data_url(8, 8))


class TestCandidateRouteSignatureImageIntegration:
    def test_put_data_validates_bounded_signature_image_via_route(
        self,
        candidate_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(candidate_mod, "save_candidate_data", MagicMock())
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        url = _tiny_jpeg_data_url(8, 8)
        resp = candidate_client.put(
            "/api/candidates/c-rout/data",
            json={"contact": {"cover_letter_signature_image": url}},
            headers=auth_headers,
        )
        assert resp.status_code == 200


class TestCandidateRoutes:
    def test_list_requires_auth(self, candidate_client: FlaskClient) -> None:
        assert candidate_client.get("/api/candidates").status_code == 401

    def test_non_admin_cannot_create_delete_or_override_state(
        self,
        candidate_client: FlaskClient,
        non_admin_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(candidate_mod, "initiate_candidate", MagicMock())
        monkeypatch.setattr(candidate_mod, "core_delete_candidate", MagicMock())
        assert (
            candidate_client.post(
                "/api/candidates", json={"astral_candidate_id": "cand-x"}, headers=non_admin_headers
            ).status_code
            == 403
        )
        assert candidate_client.delete("/api/candidates/cand-x", headers=non_admin_headers).status_code == 403
        resp = candidate_client.put(
            "/api/candidates/cand-x/data",
            json={"state": "ACTIVE_SEARCH"},
            headers=non_admin_headers,
        )
        assert resp.status_code == 403
        key_resp = candidate_client.put(
            "/api/candidates/cand-x/data",
            json={"api_key": "secret"},
            headers=non_admin_headers,
        )
        assert key_resp.status_code == 403

    def test_list_candidates_and_states(self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod, "core_list_candidates", lambda include_deleted=False: [{"candidate_api_key": "x"}] if include_deleted else [])
        assert candidate_client.get("/api/candidates", headers=auth_headers).get_json() == []
        assert candidate_client.get("/api/candidates?include_deleted=true", headers=auth_headers).get_json()[0]["has_api_key"] is True
        states = candidate_client.get("/api/candidates/states", headers=auth_headers)
        assert states.status_code == 200
        assert "NEW_CANDIDATE" in states.get_json()
        assert "PROSPECT" not in states.get_json()

    def test_create_requires_candidate_id(self, candidate_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = candidate_client.post("/api/candidates", json={}, headers=auth_headers)
        assert resp.status_code == 400

    def test_create_success_and_failure(self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod, "initiate_candidate", MagicMock())
        created = candidate_client.post("/api/candidates", json={"astral_candidate_id": "Cand-1"}, headers=auth_headers)
        assert created.status_code == 201
        monkeypatch.setattr(candidate_mod, "initiate_candidate", MagicMock(side_effect=RuntimeError("bad")))
        failed = candidate_client.post("/api/candidates", json={"astral_candidate_id": "cand-2"}, headers=auth_headers)
        assert failed.status_code == 400

    def test_get_missing_returns_404(self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: None)
        resp = candidate_client.get("/api/candidates/missing", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_returns_sanitized_candidate(self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_api_key": "x"})
        resp = candidate_client.get("/api/candidates/cand-1", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["has_api_key"] is True

    def test_update_requires_body(self, candidate_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = candidate_client.put("/api/candidates/cand-1/data", json={}, headers=auth_headers)
        assert resp.status_code == 400

    def test_update_rejects_legacy_profile_body(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        resp = candidate_client.put(
            "/api/candidates/cand-1/data",
            json={"profile": {"first": "Ada"}},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "profile was renamed to contact" in resp.get_json()["error"]

    def test_update_merges_data_state_and_api_key(self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        save_data = MagicMock()
        save_admin = MagicMock()
        clear_key = MagicMock()
        transition = MagicMock()
        monkeypatch.setattr(candidate_mod, "save_candidate_data", save_data)
        monkeypatch.setattr(candidate_mod, "save_candidate_admin", save_admin)
        monkeypatch.setattr(candidate_mod, "clear_candidate_api_key", clear_key)
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", transition)
        monkeypatch.setattr(candidate_mod, "normalize_rubric_artifacts_on_save", MagicMock())
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        monkeypatch.setattr(candidate_mod, "resolve_resume_structure", lambda cd: {"sections": {}}, raising=False)
        monkeypatch.setattr(candidate_mod, "enabled_resume_structure_sections", lambda resolved: [], raising=False)
        monkeypatch.setattr(candidate_mod, "filter_base_resume_to_structure", lambda base, ids: base, raising=False)
        monkeypatch.setattr(candidate_mod, "normalize_resume_structure", lambda merged: merged, raising=False)
        resp = candidate_client.put(
            "/api/candidates/cand-1/data",
            json={"state": "ACTIVE_SEARCH", "api_key": "  new-key  ", "artifacts": {"joblist_rubric": []}, "note": "x"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        save_data.assert_called_once()
        # AST-1287: keyword-only force= (default false) on every transition call
        transition.assert_called_once_with("cand-1", "ACTIVE_SEARCH", force=False)
        save_admin.assert_any_call("cand-1", candidate_api_key="new-key")
        clear = candidate_client.put("/api/candidates/cand-1/data", json={"api_key": "   "}, headers=auth_headers)
        assert clear.status_code == 200
        clear_key.assert_called_once_with("cand-1")

    def test_update_rejects_blank_company_search_terms(self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod, "save_candidate_data", MagicMock())
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        resp = candidate_client.put(
            "/api/candidates/cand-1/data",
            json={"artifacts": {"company_search_terms": "   \n  "}},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "non-empty search term" in resp.get_json()["error"]

    def test_put_company_search_terms_populates_table_without_persisting_blob(
        self,
        candidate_client: FlaskClient,
        auth_headers: dict[str, str],
        sqlite_in_memory,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        db = sqlite_in_memory
        db.save_candidate("c802", state="ACTIVE_SEARCH", candidate_data={})
        monkeypatch.setattr(candidate_mod, "normalize_rubric_artifacts_on_save", MagicMock())
        resp = candidate_client.put(
            "/api/candidates/c802/data",
            json={"artifacts": {"company_search_terms": "one\n two"}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        rows = db.list_company_search_terms("c802")
        assert [r["search_term"] for r in rows] == ["one", "two"]
        cand = db.get_candidate("c802")
        arts = (cand.get("candidate_data") or {}).get("artifacts") or {}
        assert "company_search_terms" not in arts

    def test_update_handles_errors(self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod, "save_candidate_data", MagicMock(side_effect=RuntimeError("bad")))
        resp = candidate_client.put("/api/candidates/cand-1/data", json={"note": "x"}, headers=auth_headers)
        assert resp.status_code == 400

    def test_delete_success_and_failure(self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod, "core_delete_candidate", MagicMock())
        ok = candidate_client.delete("/api/candidates/cand-1", headers=auth_headers)
        assert ok.status_code == 200
        monkeypatch.setattr(candidate_mod, "core_delete_candidate", MagicMock(side_effect=ValueError("missing")))
        bad = candidate_client.delete("/api/candidates/cand-1", headers=auth_headers)
        assert bad.status_code == 400

    def test_update_returns_empty_when_candidate_missing(self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod, "save_candidate_data", MagicMock())
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: None)
        resp = candidate_client.put("/api/candidates/cand-1/data", json={"note": "x"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == {}

    def test_generate_unknown_task_400(self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_data": {}})
        resp = candidate_client.post("/api/candidates/cand-1/generate/not-a-task", headers=auth_headers)
        assert resp.status_code == 400

    def test_generate_delegates_to_core(self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_data": {}})
        monkeypatch.setattr(candidate_mod, "run_candidate_artifact_generation", MagicMock(return_value=({"success": True}, 200)))
        resp = candidate_client.post("/api/candidates/cand-1/generate/craft_resume_base", headers=auth_headers)
        assert resp.status_code == 200

    def test_generate_resume_base_passes_live_content(self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_data": {"context": {"raw_resume": "resume"}}},
        )
        run = MagicMock(return_value=({"success": True}, 200))
        monkeypatch.setattr(candidate_mod, "run_candidate_artifact_generation", run)
        candidate_client.post("/api/candidates/cand-1/generate/craft_resume_base", headers=auth_headers)
        assert run.call_args.args[2] == "resume"

    def test_generate_other_task_uses_none_live_content(self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_data": {}})
        run = MagicMock(return_value=({"success": True}, 200))
        monkeypatch.setattr(candidate_mod, "run_candidate_artifact_generation", run)
        candidate_client.post("/api/candidates/cand-1/generate/craft_joblist_rubric", headers=auth_headers)
        assert run.call_args.args[2] is None

    def test_generate_missing_candidate_404(self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: None)
        resp = candidate_client.post("/api/candidates/cand-1/generate/craft_resume_base", headers=auth_headers)
        assert resp.status_code == 404


class TestAst1253GenerateArtifactsApi:
    """AST-1253: POST /generate_artifacts handoff + chain-key ad-hoc generate 409."""

    def test_generate_artifacts_happy_path(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "state": "ARTIFACTS_READY"},
        )
        monkeypatch.setattr(
            candidate_mod,
            "start_requested_artifacts",
            MagicMock(return_value="REQUESTED_ARTIFACTS"),
        )
        resp = candidate_client.post("/api/candidates/cand-1/generate_artifacts", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == {"ok": True, "state": "REQUESTED_ARTIFACTS"}
        candidate_mod.start_requested_artifacts.assert_called_once_with("cand-1")

    def test_generate_artifacts_404(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: None)
        resp = candidate_client.post("/api/candidates/missing/generate_artifacts", headers=auth_headers)
        assert resp.status_code == 404

    def test_generate_artifacts_409_illegal_prior(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "state": "NEW_CANDIDATE"},
        )
        monkeypatch.setattr(
            candidate_mod,
            "start_requested_artifacts",
            MagicMock(side_effect=ValueError("Invalid candidate state transition")),
        )
        resp = candidate_client.post("/api/candidates/cand-1/generate_artifacts", headers=auth_headers)
        assert resp.status_code == 409
        assert "Invalid" in resp.get_json()["error"]

    def test_chain_task_generate_returns_core_409(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_data": {}},
        )
        monkeypatch.setattr(
            candidate_mod,
            "run_candidate_artifact_generation",
            MagicMock(
                return_value=(
                    {
                        "success": False,
                        "error": "Use POST /api/candidates/<id>/generate_artifacts",
                    },
                    409,
                )
            ),
        )
        resp = candidate_client.post(
            "/api/candidates/cand-1/generate/craft_get_rubric",
            headers=auth_headers,
        )
        assert resp.status_code == 409
        assert "generate_artifacts" in resp.get_json()["error"]


# Keep legacy class boundary for AST-723+ suites below this point when present.

# Branches: GET resume_structure 404/success; PUT base_resume orphan strip; PUT resume_structure normalize errors.
class TestAst519ResumeStructureApi:
    def _valid_accent(self) -> str:
        from src.utils.config import BUILD_CONFIG

        return (BUILD_CONFIG.get("accent_palette") or ["#1A1A2E"])[0].upper()

    def _three_section_cd(self) -> dict:
        # Normalize-valid ten-id blob (AST-1303 required seven); disable an optional.
        from src.core.candidate import default_resume_structure

        structure = default_resume_structure()
        structure["sections"]["professional_summary"]["title"] = "Custom Summary"
        structure["sections"]["experience"]["title"] = "Custom Jobs"
        structure["sections"]["technical_skills"]["title"] = "Custom Skills"
        structure["sections"]["technical_skills"]["enabled"] = False
        structure["accent_color"] = self._valid_accent()
        return {
            "astral_candidate_id": "c1",
            "candidate_data": {"artifacts": {"resume_structure": structure}},
        }

    def test_get_resume_structure_returns_enabled_ordered_sections(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: self._three_section_cd())
        resp = candidate_client.get("/api/candidates/c1/resume_structure", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["accent_color"] == self._valid_accent()
        ids = [row["id"] for row in body["sections"]]
        assert "professional_summary" in ids
        assert "technical_skills" not in ids
        assert next(r["label"] for r in body["sections"] if r["id"] == "professional_summary") == "Custom Summary"

    def test_get_resume_structure_uses_resolve_default_when_blob_missing(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.core import candidate as core_candidate

        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_data": {}},
        )
        default = core_candidate.default_resume_structure()
        expected = core_candidate.enabled_resume_structure_sections(default)
        resp = candidate_client.get("/api/candidates/c1/resume_structure", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["sections"] == expected

    def test_get_resume_structure_missing_candidate_404(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: None)
        resp = candidate_client.get("/api/candidates/missing/resume_structure", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_resume_structure_null_accent_when_not_string(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        cd = self._three_section_cd()
        cd["candidate_data"]["artifacts"]["resume_structure"]["accent_color"] = 42
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: cd)
        resp = candidate_client.get("/api/candidates/c1/resume_structure", headers=auth_headers)
        assert resp.get_json()["accent_color"] is None

    def test_put_base_resume_strips_orphan_keys(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        save_data = MagicMock()
        monkeypatch.setattr(candidate_mod, "save_candidate_data", save_data)
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: self._three_section_cd())
        monkeypatch.setattr(candidate_mod, "normalize_rubric_artifacts_on_save", MagicMock())
        monkeypatch.setattr(candidate_mod, "apply_company_search_terms_save", MagicMock())
        resp = candidate_client.put(
            "/api/candidates/c1/data",
            json={"artifacts": {"base_resume": {"professional_summary": "ok", "123bad": "drop", "accent_color": "#ABCDEF"}}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        payload = save_data.call_args.args[1]
        assert payload["artifacts"]["base_resume"] == {"professional_summary": "ok"}

    def test_put_resume_structure_merges_and_normalizes_accent(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.utils.config import BUILD_CONFIG

        save_data = MagicMock()
        monkeypatch.setattr(candidate_mod, "save_candidate_data", save_data)
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: self._three_section_cd())
        monkeypatch.setattr(candidate_mod, "normalize_rubric_artifacts_on_save", MagicMock())
        monkeypatch.setattr(candidate_mod, "apply_company_search_terms_save", MagicMock())
        accent = (BUILD_CONFIG.get("accent_palette") or ["#1A1A2E"])[0].upper()
        resp = candidate_client.put(
            "/api/candidates/c1/data",
            json={"artifacts": {"resume_structure": {"accent_color": accent.lower()}}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        merged = save_data.call_args.args[1]["artifacts"]["resume_structure"]
        assert merged["accent_color"] == accent

    def test_put_resume_structure_rejects_invalid_accent(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(candidate_mod, "save_candidate_data", MagicMock())
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: self._three_section_cd())
        resp = candidate_client.put(
            "/api/candidates/c1/data",
            json={"artifacts": {"resume_structure": {"accent_color": "not-hex"}}},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"] == "invalid accent_color"

    def test_put_resume_structure_rejects_invalid_sections(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(candidate_mod, "save_candidate_data", MagicMock())
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: self._three_section_cd())
        resp = candidate_client.put(
            "/api/candidates/c1/data",
            json={"artifacts": {"resume_structure": {"sections": {"nope": {"id": "nope", "title": "X", "enabled": True, "order": 0, "job_agent_editable": True}}}}},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "missing required" in resp.get_json()["error"]


class TestAst723RubricVectorsApi:
    def test_put_syncs_rubric_vectors_before_save(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        save_data = MagicMock()
        synced: list[tuple[str, list]] = []
        monkeypatch.setattr(candidate_mod, "save_candidate_data", save_data)
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: {"astral_candidate_id": candidate_id})
        monkeypatch.setattr(candidate_mod, "normalize_rubric_artifacts_on_save", MagicMock())
        monkeypatch.setattr(candidate_mod, "apply_company_search_terms_save", MagicMock())
        monkeypatch.setattr(
            candidate_mod,
            "apply_rubric_vectors_save",
            lambda cid, arts: synced.append((cid, dict(arts))),
        )
        criteria = [{"code": "CR", "label": "fit", "content": "line", "importance": 5}]
        resp = candidate_client.put(
            "/api/candidates/c723/data",
            json={"artifacts": {"joblist_rubric": criteria}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert synced and synced[0][0] == "c723"
        save_data.assert_called_once()

    def test_get_hydrates_rubric_artifacts_for_display(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda candidate_id: {
                "astral_candidate_id": candidate_id,
                "candidate_data": {"artifacts": {}},
            },
        )
        monkeypatch.setattr(candidate_mod, "company_search_terms_joined_text", lambda cid: "")
        monkeypatch.setattr(
            candidate_mod,
            "hydrate_rubric_artifacts_for_response",
            lambda cid, cd: cd.setdefault("artifacts", {}).update(
                {"joblist_rubric": [{"code": "CR", "content": "x", "importance": 5}]}
            ),
        )
        resp = candidate_client.get("/api/candidates/c723", headers=auth_headers)
        assert resp.status_code == 200
        arts = resp.get_json()["candidate_data"]["artifacts"]
        assert arts["joblist_rubric"][0]["code"] == "CR"


class TestAst901PendingCraftGenerationApi:
    """AST-901: GET …/generate/<task_key>/pending + clear pending on artifact Save."""

    def test_get_pending_delegates_to_core(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            candidate_mod,
            "get_pending_craft_generation",
            MagicMock(
                return_value=(
                    {
                        "success": True,
                        "parsed_response": {"criteria": [{"code": "GT"}]},
                        "batch_id": "user-craft_get_rubric-x",
                        "recovered": True,
                        "source": "pending_stash",
                    },
                    200,
                )
            ),
        )
        resp = candidate_client.get(
            "/api/candidates/karfo/generate/craft_get_rubric/pending",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["recovered"] is True
        assert body["source"] == "pending_stash"
        candidate_mod.get_pending_craft_generation.assert_called_once_with("karfo", "craft_get_rubric")

    def test_put_artifact_clears_matching_pending(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # AST-904: apply_rubric_vectors_save deletes artifact keys — clear must use
        # keys captured before apply, not `if key in arts` after del.
        cleared: list[tuple[str, str]] = []
        monkeypatch.setattr(candidate_mod, "save_candidate_data", MagicMock())
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_data": {}},
        )
        monkeypatch.setattr(candidate_mod, "normalize_rubric_artifacts_on_save", MagicMock())
        monkeypatch.setattr(candidate_mod, "apply_company_search_terms_save", MagicMock())

        def _apply_del(_cid: str, arts: dict) -> None:
            arts.pop("get_rubric", None)

        monkeypatch.setattr(candidate_mod, "apply_rubric_vectors_save", _apply_del)
        monkeypatch.setattr(
            candidate_mod,
            "_clear_pending_craft_generation",
            lambda cid, task_key: cleared.append((cid, task_key)),
        )
        criteria = [{"code": "GT", "label": "get", "content": "line", "importance": 5}]
        resp = candidate_client.put(
            "/api/candidates/karfo/data",
            json={"artifacts": {"get_rubric": criteria}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert ("karfo", "craft_get_rubric") in cleared


class TestAst904SavePendingRecovery:
    """AST-904: failed Save re-stashes criteria; clear pending only after success."""

    def test_put_save_failure_restashes_pending(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        stashed: list[tuple] = []
        cleared: list[tuple[str, str]] = []
        monkeypatch.setattr(
            candidate_mod,
            "normalize_rubric_artifacts_on_save",
            MagicMock(side_effect=ValueError("criterion content invalid")),
        )
        monkeypatch.setattr(candidate_mod, "apply_company_search_terms_save", MagicMock())
        monkeypatch.setattr(candidate_mod, "apply_rubric_vectors_save", MagicMock())
        monkeypatch.setattr(candidate_mod, "save_candidate_data", MagicMock())
        monkeypatch.setattr(
            candidate_mod,
            "_stash_pending_craft_generation",
            lambda cid, task_key, batch_id, parsed: stashed.append(
                (cid, task_key, batch_id, parsed)
            ),
        )
        monkeypatch.setattr(
            candidate_mod,
            "_clear_pending_craft_generation",
            lambda cid, task_key: cleared.append((cid, task_key)),
        )
        criteria = [{"code": "GT", "label": "get", "content": "A == match", "importance": 5}]
        resp = candidate_client.put(
            "/api/candidates/karfo/data",
            json={"artifacts": {"get_rubric": criteria}},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert resp.get_json()["error"] == "criterion content invalid"
        assert cleared == []
        assert len(stashed) == 1
        assert stashed[0][0] == "karfo"
        assert stashed[0][1] == "craft_get_rubric"
        assert stashed[0][2] is None
        assert stashed[0][3] == {"criteria": criteria}


class TestAst906GetRubricLiteralNewlineSave:
    """AST-906: PUT get_rubric with craft-shaped literal \\n content → 200; empty/single grade → 400."""

    def _put_mocks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(candidate_mod, "apply_company_search_terms_save", MagicMock())
        monkeypatch.setattr(candidate_mod, "apply_rubric_vectors_save", MagicMock())
        monkeypatch.setattr(candidate_mod, "save_candidate_data", MagicMock())
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "candidate_data": {}},
        )
        monkeypatch.setattr(candidate_mod, "_clear_pending_craft_generation", MagicMock())

    def test_put_get_rubric_literal_n_succeeds(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self._put_mocks(monkeypatch)
        # Literal backslash-n (craft Get prompt shape) — coerce expands before grade parse.
        criteria = [
            {
                "code": "GT",
                "label": "get",
                "content": "Fit criterion.\\nA = strong match\\nB = weak match",
                "importance": 5,
            }
        ]
        resp = candidate_client.put(
            "/api/candidates/karfo/data",
            json={"artifacts": {"get_rubric": criteria}},
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_put_get_rubric_empty_still_400(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self._put_mocks(monkeypatch)
        criteria = [{"code": "GT", "label": "get", "content": "", "importance": 5}]
        resp = candidate_client.put(
            "/api/candidates/karfo/data",
            json={"artifacts": {"get_rubric": criteria}},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "empty" in resp.get_json()["error"].lower() or "Rubric" in resp.get_json()["error"]

    def test_put_get_rubric_single_grade_still_400(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self._put_mocks(monkeypatch)
        criteria = [{"code": "GT", "label": "get", "content": "A = only", "importance": 5}]
        resp = candidate_client.put(
            "/api/candidates/karfo/data",
            json={"artifacts": {"get_rubric": criteria}},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        err = resp.get_json()["error"]
        assert "at least two lines" in err or "Rubric" in err


class TestAst970AdminStateOverride:
    """AST-970: admin state override goes through transition_candidate_state (fail closed)."""

    def test_illegal_hop_returns_400(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "state": "NEW_CANDIDATE"},
        )
        # AST-1287: core raises IllegalCandidateTransition; API maps to structured 400
        monkeypatch.setattr(
            candidate_mod,
            "transition_candidate_state",
            MagicMock(
                side_effect=candidate_mod.IllegalCandidateTransition("NEW_CANDIDATE", "ACTIVE_SEARCH")
            ),
        )
        resp = candidate_client.put(
            "/api/candidates/cand-1/data",
            json={"state": "ACTIVE_SEARCH"},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        body = resp.get_json()
        assert "Invalid candidate state transition" in body["error"]
        assert body["code"] == "illegal_candidate_transition"
        assert body["from_state"] == "NEW_CANDIDATE"
        assert body["to_state"] == "ACTIVE_SEARCH"

    def test_legal_hop_calls_transition(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        transition = MagicMock()
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "state": "NEW_CANDIDATE"},
        )
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", transition)
        resp = candidate_client.put(
            "/api/candidates/cand-1/data",
            json={"state": "INTAKE_INITIATED"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        transition.assert_called_once_with("cand-1", "INTAKE_INITIATED", force=False)


class TestAst1287AdminConfirmOverride:
    """AST-1287: confirm_state_override + same-state skip + structured illegal hop."""

    def test_confirm_forces_illegal_hop(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        transition = MagicMock()
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "state": "NEW_CANDIDATE"},
        )
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", transition)
        resp = candidate_client.put(
            "/api/candidates/cand-1/data",
            json={"state": "ACTIVE_SEARCH", "confirm_state_override": True},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        transition.assert_called_once_with("cand-1", "ACTIVE_SEARCH", force=True)

    def test_same_state_skips_transition_and_saves_non_state(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save_data = MagicMock()
        transition = MagicMock()
        monkeypatch.setattr(candidate_mod, "save_candidate_data", save_data)
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", transition)
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda candidate_id: {
                "astral_candidate_id": candidate_id,
                "state": "ACTIVE_SEARCH",
                "candidate_data": {},
            },
        )
        resp = candidate_client.put(
            "/api/candidates/cand-1/data",
            json={"state": "ACTIVE_SEARCH", "note": "name-only edit"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        save_data.assert_called_once()
        transition.assert_not_called()

    def test_non_admin_cannot_send_confirm_flag(
        self,
        candidate_client: FlaskClient,
        non_admin_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(candidate_mod, "save_candidate_data", MagicMock())
        resp = candidate_client.put(
            "/api/candidates/cand-x/data",
            json={"confirm_state_override": True, "note": "x"},
            headers=non_admin_headers,
        )
        assert resp.status_code == 403

    def test_unknown_state_400_without_illegal_code(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "state": "NEW_CANDIDATE"},
        )
        monkeypatch.setattr(
            candidate_mod,
            "transition_candidate_state",
            MagicMock(side_effect=ValueError("Unknown candidate state: LIVE_PROMPTS")),
        )
        resp = candidate_client.put(
            "/api/candidates/cand-1/data",
            json={"state": "LIVE_PROMPTS", "confirm_state_override": True},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        body = resp.get_json()
        assert "Unknown candidate state" in body["error"]
        assert "code" not in body

    def test_string_true_confirm_does_not_force(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        transition = MagicMock()
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda candidate_id: {"astral_candidate_id": candidate_id, "state": "NEW_CANDIDATE"},
        )
        monkeypatch.setattr(candidate_mod, "transition_candidate_state", transition)
        resp = candidate_client.put(
            "/api/candidates/cand-1/data",
            json={"state": "INTAKE_INITIATED", "confirm_state_override": "true"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        transition.assert_called_once_with("cand-1", "INTAKE_INITIATED", force=False)


class TestAst1306ResumeStructureAuthorApi:
    """AST-1306: GET catalog/all_sections; PUT replace (not overlay) when sections sent."""

    def _cd(self) -> dict:
        return TestAst519ResumeStructureApi()._three_section_cd()

    def _patch_put(self, monkeypatch: pytest.MonkeyPatch) -> MagicMock:
        save_data = MagicMock()
        monkeypatch.setattr(candidate_mod, "save_candidate_data", save_data)
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: self._cd())
        monkeypatch.setattr(candidate_mod, "normalize_rubric_artifacts_on_save", MagicMock())
        monkeypatch.setattr(candidate_mod, "apply_company_search_terms_save", MagicMock())
        return save_data

    def test_get_includes_catalog_and_all_sections(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from src.utils.config import (
            RESUME_STRUCTURE_BODY_FORMATS,
            RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT,
            RESUME_STRUCTURE_REQUIRED_SECTION_IDS,
        )

        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: self._cd())
        resp = candidate_client.get("/api/candidates/c1/resume_structure", headers=auth_headers)
        body = resp.get_json()
        assert resp.status_code == 200
        assert body["catalog"]["body_formats"] == list(RESUME_STRUCTURE_BODY_FORMATS)
        assert body["catalog"]["new_extra_default_format"] == RESUME_STRUCTURE_NEW_EXTRA_DEFAULT_FORMAT
        assert body["catalog"]["required_ids"] == list(RESUME_STRUCTURE_REQUIRED_SECTION_IDS)
        by_id = {row["id"]: row for row in body["all_sections"]}
        assert by_id["technical_skills"]["enabled"] is False
        assert by_id["experience"]["format_locked"] is True
        assert by_id["candidate_name"]["required"] is True
        assert {s["id"] for s in body["sections"]}.isdisjoint({"technical_skills"})

    def test_put_replace_drops_omitted_optional_and_keeps_required_title(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        save_data = self._patch_put(monkeypatch)
        from src.core.candidate import default_resume_structure
        from src.utils.config import RESUME_STRUCTURE_REQUIRED_SECTION_IDS

        sections = {
            sid: dict(spec)
            for sid, spec in default_resume_structure()["sections"].items()
            if sid in RESUME_STRUCTURE_REQUIRED_SECTION_IDS
        }
        sections["professional_summary"]["title"] = "Summary"
        sections["highlights"] = {
            "id": "highlights",
            "title": "Highlights",
            "enabled": True,
            "order": 10,
            "format": "bullet_list",
            "job_agent_editable": True,
        }
        resp = candidate_client.put(
            "/api/candidates/c1/data",
            json={"artifacts": {"resume_structure": {"sections": sections}}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        stored = save_data.call_args.args[1]["artifacts"]["resume_structure"]["sections"]
        assert "prior_experience" not in stored
        assert stored["highlights"]["format"] == "bullet_list"
        assert stored["professional_summary"]["id"] == "professional_summary"
        assert stored["professional_summary"]["title"] == "Summary"

    def test_put_accent_only_leaves_sections(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        save_data = self._patch_put(monkeypatch)
        accent = TestAst519ResumeStructureApi()._valid_accent()
        resp = candidate_client.put(
            "/api/candidates/c1/data",
            json={"artifacts": {"resume_structure": {"accent_color": accent.lower()}}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        stored = save_data.call_args.args[1]["artifacts"]["resume_structure"]
        assert stored["accent_color"] == accent
        assert "technical_skills" in stored["sections"]
        assert stored["sections"]["technical_skills"]["enabled"] is False

    def test_put_omitting_required_is_400(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self._patch_put(monkeypatch)
        from src.core.candidate import default_resume_structure
        from src.utils.config import RESUME_STRUCTURE_REQUIRED_SECTION_IDS

        sections = {
            sid: dict(spec)
            for sid, spec in default_resume_structure()["sections"].items()
            if sid in RESUME_STRUCTURE_REQUIRED_SECTION_IDS and sid != "experience"
        }
        resp = candidate_client.put(
            "/api/candidates/c1/data",
            json={"artifacts": {"resume_structure": {"sections": sections}}},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "missing required" in resp.get_json()["error"]

    def test_put_pending_key_slugs_from_title(
        self, candidate_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        save_data = self._patch_put(monkeypatch)
        from src.core.candidate import default_resume_structure
        from src.utils.config import RESUME_STRUCTURE_REQUIRED_SECTION_IDS

        sections = {
            sid: dict(spec)
            for sid, spec in default_resume_structure()["sections"].items()
            if sid in RESUME_STRUCTURE_REQUIRED_SECTION_IDS
        }
        sections["_pending_0"] = {
            "id": "_pending_0",
            "title": "Publications",
            "enabled": True,
            "order": 10,
            "format": "bullet_list",
            "job_agent_editable": True,
        }
        resp = candidate_client.put(
            "/api/candidates/c1/data",
            json={"artifacts": {"resume_structure": {"sections": sections}}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        stored = save_data.call_args.args[1]["artifacts"]["resume_structure"]["sections"]
        assert "publications" in stored
        assert "_pending_0" not in stored


class TestAst1305LegacyLabelIngestApi:
    """AST-1305: PUT /data ingest keeps unmatched Abrams labels as extras."""

    def _cd(self) -> dict:
        from src.core import candidate as core_candidate

        return {
            "astral_candidate_id": "c1",
            "candidate_data": {
                "artifacts": {"resume_structure": core_candidate.default_resume_structure()},
            },
        }

    def test_put_label_list_keeps_highlights_and_drops_prose_experience(
        self,
        candidate_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        save_data = MagicMock()
        monkeypatch.setattr(candidate_mod, "save_candidate_data", save_data)
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: self._cd())
        monkeypatch.setattr(candidate_mod, "normalize_rubric_artifacts_on_save", MagicMock())
        monkeypatch.setattr(candidate_mod, "apply_company_search_terms_save", MagicMock())
        labels = [
            {"label": "Professional Summary", "content": "Summary body"},
            {"label": "Highlights", "content": "Won awards"},
            {"label": "Publications", "content": "Paper one"},
            {"label": "Experience", "content": "leftover prose"},
        ]
        resp = candidate_client.put(
            "/api/candidates/c1/data",
            json={"artifacts": {"base_resume": labels}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        arts = save_data.call_args.args[1]["artifacts"]
        assert arts["base_resume"]["highlights"] == "Won awards"
        assert arts["base_resume"]["publications"] == "Paper one"
        assert arts["base_resume"]["professional_summary"] == "Summary body"
        assert "experience" not in arts["base_resume"]
        assert arts["resume_structure"]["sections"]["highlights"]["format"] == "bullet_list"
        assert arts["resume_structure"]["sections"]["publications"]["title"] == "Publications"

    def test_put_title_keyed_dict_keeps_highlights_and_publications(
        self,
        candidate_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # AST-1322 bug-repro: title-case keys must mint extras before orphan filter.
        save_data = MagicMock()
        monkeypatch.setattr(candidate_mod, "save_candidate_data", save_data)
        monkeypatch.setattr(candidate_mod, "get_candidate", lambda candidate_id: self._cd())
        monkeypatch.setattr(candidate_mod, "normalize_rubric_artifacts_on_save", MagicMock())
        monkeypatch.setattr(candidate_mod, "apply_company_search_terms_save", MagicMock())
        resp = candidate_client.put(
            "/api/candidates/c1/data",
            json={
                "artifacts": {
                    "base_resume": {
                        "professional_summary": "Summary body",
                        "Highlights": "Won awards",
                        "Publications": "Paper one",
                    }
                }
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        arts = save_data.call_args.args[1]["artifacts"]
        assert arts["base_resume"]["highlights"] == "Won awards"
        assert arts["base_resume"]["publications"] == "Paper one"
        assert arts["base_resume"]["professional_summary"] == "Summary body"
        assert "Highlights" not in arts["base_resume"]
        assert arts["resume_structure"]["sections"]["highlights"]["format"] == "bullet_list"
        assert arts["resume_structure"]["sections"]["publications"]["title"] == "Publications"


class TestAst1324HydrateResumeStructureFromBaseResumeGet:
    """AST-1324 bug-repro: GET /resume_structure unions base_resume keys; missing format → free_prose."""

    def _cd_base_resume_extra_missing_from_structure(self) -> dict:
        from src.core.candidate import default_resume_structure

        structure = default_resume_structure()
        # Ensure highlights is only on base_resume (load path must mint it).
        structure["sections"].pop("highlights", None)
        return {
            "astral_candidate_id": "c1",
            "candidate_data": {
                "artifacts": {
                    "resume_structure": structure,
                    "base_resume": {
                        "professional_summary": "Existing summary",
                        "highlights": "Line A\nLine B",
                        "experience": [
                            {
                                "title": "Role",
                                "company": "Co",
                                "dates": "",
                                "location": "",
                                "accomplishments": "",
                            }
                        ],
                    },
                }
            },
        }

    def test_get_includes_base_resume_extra_with_free_prose_default(
        self,
        candidate_client: FlaskClient,
        auth_headers: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            candidate_mod,
            "get_candidate",
            lambda candidate_id: self._cd_base_resume_extra_missing_from_structure(),
        )
        resp = candidate_client.get("/api/candidates/c1/resume_structure", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        by_id = {row["id"]: row for row in body["all_sections"]}
        assert "highlights" in by_id
        assert by_id["highlights"]["enabled"] is True
        # Load default is free_prose — not Add-section / list-ingest bullet_list.
        assert by_id["highlights"]["format"] == "free_prose"
        assert "highlights" in {s["id"] for s in body["sections"]}
