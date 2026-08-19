"""Component tests for src/ui/api/api_system.py (AST-394)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from src.utils import deploy_status as ds_mod
from ui.api import api_system as system_mod


class TestSystemHealth:
    def test_health_is_open(self, system_client: FlaskClient) -> None:
        resp = system_client.get("/api/health")
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "ok"}


class TestSystemAuthRoutes:
    def test_me_requires_bearer(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        assert system_client.get("/api/me").status_code == 401
        resp = system_client.get("/api/me", headers=auth_headers)
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload["user_id"] == "susan"
        assert payload["is_admin"] is True

    def test_me_non_admin_includes_is_admin_false(
        self, system_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        resp = system_client.get("/api/me", headers=non_admin_headers)
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload["user_id"] == "u2"
        assert payload["is_admin"] is False

    def test_shapes_unknown_entity_404(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = system_client.get("/api/shapes/missing", headers=auth_headers)
        assert resp.status_code == 404

    def test_shapes_known_entity(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = system_client.get("/api/shapes/candidates", headers=auth_headers)
        assert resp.status_code == 200
        assert "list" in resp.get_json()

    def test_ui_config_and_state_manifest(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        ui = system_client.get("/api/ui_config", headers=auth_headers)
        manifest = system_client.get("/api/state_ui_manifest", headers=auth_headers)
        assert ui.status_code == 200
        assert manifest.status_code == 200

    def test_ui_config_includes_base_resume_accent_palette(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        payload = system_client.get("/api/ui_config", headers=auth_headers).get_json()
        palette = payload.get("base_resume_accent_palette")
        assert isinstance(palette, list)
        assert palette
        assert all(isinstance(hex, str) and hex.startswith("#") for hex in palette)

    def test_ui_config_includes_list_table_layout_defaults(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        payload = system_client.get("/api/ui_config", headers=auth_headers).get_json()
        assert payload.get("list_table_frozen_data_columns") == 2
        assert payload.get("list_table_cell_truncate_chars") == 30

    def test_ui_config_includes_preamble_config(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        # AST-1016: Intro + steps for AST-1017; route alias matches existing ui_config tests.
        from src.utils.config import PREAMBLE_CONFIG

        payload = system_client.get("/api/ui_config", headers=auth_headers).get_json()
        preamble = payload.get("preamble")
        assert isinstance(preamble, dict)
        assert preamble["intro"] == PREAMBLE_CONFIG["intro"]
        assert preamble["validation_task_key"] == PREAMBLE_CONFIG["validation_task_key"]
        assert len(preamble["steps"]) == len(PREAMBLE_CONFIG["steps"])
        assert [s["id"] for s in preamble["steps"]] == [s["id"] for s in PREAMBLE_CONFIG["steps"]]

    def test_ui_config_includes_cover_from_block(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        # AST-1149: Session Cover Letter reads authoring chrome from ui_config.
        from src.utils.config import COVER_FROM_BLOCK_CONFIG

        payload = system_client.get("/api/ui_config", headers=auth_headers).get_json()
        block = payload.get("cover_from_block")
        assert isinstance(block, dict)
        assert block["default_template"] == COVER_FROM_BLOCK_CONFIG["default_template"]
        assert block["authoring_help"] == COVER_FROM_BLOCK_CONFIG["authoring_help"]
        assert block["session_authoring_help"] == COVER_FROM_BLOCK_CONFIG["session_authoring_help"]

    def test_nav_config_without_candidate_id(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = system_client.get("/api/nav_config", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_nav_config_missing_candidate(self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("ui.api.api_system.get_candidate", lambda candidate_id: None)
        resp = system_client.get("/api/nav_config?candidate_id=missing", headers=auth_headers)
        assert resp.status_code == 200

    def test_nav_config_uses_candidate_state(self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("ui.api.api_system.get_candidate", lambda candidate_id: {"state": "ACTIVE_SEARCH"})
        monkeypatch.setattr(system_mod, "_get_company_counts", lambda candidate_id: {"/companies/watch_list": 4})
        monkeypatch.setattr(system_mod, "_get_job_counts", lambda candidate_id: {"/jobs/in_review": 1})
        resp = system_client.get("/api/nav_config?candidate_id=cand-1", headers=auth_headers)
        payload = resp.get_json()
        assert resp.status_code == 200
        jobs = next(group for group in payload if group["label"] == "Jobs")
        assert jobs["items"][0]["count"] == 1

    def test_nav_config_early_state_keeps_candidate_facing_groups(
        self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("ui.api.api_system.get_candidate", lambda candidate_id: {"state": "NEW_CANDIDATE"})
        monkeypatch.setattr(system_mod, "_get_company_counts", lambda candidate_id: {})
        monkeypatch.setattr(system_mod, "_get_job_counts", lambda candidate_id: {})
        resp = system_client.get("/api/nav_config?candidate_id=cand-1", headers=auth_headers)
        assert resp.status_code == 200
        labels = {group["label"] for group in resp.get_json()}
        assert {"Jobs", "Companies", "Artifacts", "Candidate"} <= labels

    def test_nav_config_admin_agent_ad_hoc_label(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        payload = system_client.get("/api/nav_config", headers=auth_headers).get_json()
        tools = next(group for group in payload if group["label"] == "Tools")
        ad_hoc = next(item for item in tools["items"] if item["path"] == "/admin/anthropic_ad_hoc")
        assert ad_hoc["label"] == "Agent Ad Hoc"

    def test_nav_config_omits_admin_group_for_non_admin(
        self, system_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        # AST-1386: all admin_only segments (Operations / Admin / Tools) omitted for non-admins.
        payload = system_client.get("/api/nav_config", headers=non_admin_headers).get_json()
        assert all(
            group.get("label") not in {"Operations", "Admin", "Tools"} for group in payload
        )

    def test_nav_config_three_admin_segments_for_admin(
        self, system_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        # AST-1386: admin sees Operations → Admin → Tools; paste labels; no admin_only in JSON.
        payload = system_client.get("/api/nav_config", headers=auth_headers).get_json()
        labels = [group["label"] for group in payload]
        cand_i = labels.index("Candidate")
        assert labels[cand_i + 1 : cand_i + 4] == ["Operations", "Admin", "Tools"]
        tools = next(group for group in payload if group["label"] == "Tools")
        resume = next(it for it in tools["items"] if it["path"] == "/admin/session_resume_paste")
        cover = next(it for it in tools["items"] if it["path"] == "/admin/session_cover_letter")
        assert resume["label"] == "Resume Paste"
        assert cover["label"] == "Cover Letter Paste"
        assert all("admin_only" not in group for group in payload)

    def test_nav_config_omits_board_searches(self, system_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        payload = system_client.get("/api/nav_config", headers=auth_headers).get_json()
        paths = [item.get("path") for group in payload for item in group.get("items", [])]
        assert "/candidate/board_searches" not in paths

    def test_agent_data_returns_rows(self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.agent.get_agent_data", MagicMock(return_value=[{"id": "block-1"}]))
        resp = system_client.get("/api/agent_data/batch-1?block_type=RESPONSE&entity_id=acme", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()[0]["id"] == "block-1"

    def test_agent_data_missing_entity_404(self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.agent.get_entity_response", MagicMock(return_value=None))
        resp = system_client.get("/api/agent_data/batch-1/entity/acme", headers=auth_headers)
        assert resp.status_code == 404

    def test_agent_data_entity_response(self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.agent.get_entity_response", MagicMock(return_value={"block_data": "{}"}))
        resp = system_client.get("/api/agent_data/batch-1/entity/acme", headers=auth_headers)
        assert resp.status_code == 200


class TestDeployStatus:
    def test_requires_bearer(self, system_client: FlaskClient) -> None:
        assert system_client.get("/api/deploy_status").status_code == 401

    def test_non_admin_forbidden(
        self, system_client: FlaskClient, non_admin_headers: dict[str, str]
    ) -> None:
        resp = system_client.get("/api/deploy_status", headers=non_admin_headers)
        assert resp.status_code == 403

    def test_admin_returns_payload(
        self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        expected = {
            "uptime": "5m",
            "uptime_seconds": 300,
            "environment": "local",
            "merge_tickets": [],
        }
        monkeypatch.setattr(system_mod, "get_deploy_status_payload", lambda: expected)
        resp = system_client.get("/api/deploy_status", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == expected

    def test_admin_omits_environment_when_unset(
        self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        payload = {
            "uptime": "<1m",
            "uptime_seconds": 10,
            "merge_tickets": [],
        }
        monkeypatch.setattr(system_mod, "get_deploy_status_payload", lambda: payload)
        resp = system_client.get("/api/deploy_status", headers=auth_headers)
        assert resp.status_code == 200
        assert "environment" not in resp.get_json()

    def test_admin_uptime_format_samples_via_payload_builder(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(ds_mod, "_PROCESS_BOOT_TIME", 0.0)
        cases = [
            (30, "<1m"),
            (5 * 60, "5m"),
            (75 * 60, "1h15m"),
            (3 * 86400 + 22 * 3600 + 7 * 60, "3d22h07m"),
        ]
        for seconds, expected_uptime in cases:
            monkeypatch.setattr("time.time", lambda s=seconds: float(s))
            payload = ds_mod.get_deploy_status_payload()
            assert payload["uptime"] == expected_uptime


class TestSystemNavHelpers:
    def test_is_at_or_past_compares_candidate_states(self) -> None:
        assert system_mod._is_at_or_past("ACTIVE_SEARCH", "RESUME_READY") is True
        assert system_mod._is_at_or_past("NEW_CANDIDATE", "ACTIVE_SEARCH") is False
        # Terminals never unlock gated nav
        assert system_mod._is_at_or_past("INACTIVE", "RESUME_READY") is False
        assert system_mod._is_at_or_past("DELETED", "NEW_CANDIDATE") is False

    def test_company_counts_without_candidate(self) -> None:
        assert system_mod._get_company_counts(None) == {}

    def test_company_counts_swallow_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.roster.get_active_trigger_states", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))
        assert system_mod._get_company_counts("cand-1") == {}

    def test_company_counts_with_pipeline_and_history(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.roster.get_active_trigger_states", lambda *args, **kwargs: ["WATCH", "IGNORE"])
        monkeypatch.setattr("src.core.roster.list_companies", lambda **kwargs: [1, 2] if kwargs.get("states") == ["WATCH"] else [])
        monkeypatch.setattr("src.core.roster.list_company_job_scans", lambda **kwargs: [1])
        counts = system_mod._get_company_counts("cand-1")
        assert counts["/companies/watch_list"] == 2
        assert counts["/companies/new_list"] == 0

    def test_job_counts_without_candidate(self) -> None:
        assert system_mod._get_job_counts(None) == {}

    def test_job_counts_swallow_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.tracker.count_jobs_below_dispatch_score_floor", lambda candidate_id: (_ for _ in ()).throw(RuntimeError("boom")))
        assert system_mod._get_job_counts("cand-1") == {}

    def test_resolve_nav_keeps_candidate_facing_groups_and_stubs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # AST-1449: no group-level visible skip; Applied/Responded stay disabled stubs.
        monkeypatch.setattr(system_mod, "_get_company_counts", lambda candidate_id: {})
        monkeypatch.setattr(system_mod, "_get_job_counts", lambda candidate_id: {})
        facing = {"Jobs", "Companies", "Artifacts", "Candidate"}
        for state in ("NEW_CANDIDATE", "RESUME_READY"):
            nav = system_mod._resolve_nav(state, "cand-1")
            labels = {group["label"] for group in nav}
            assert facing <= labels
            jobs = next(group for group in nav if group["label"] == "Jobs")
            applied = next(item for item in jobs["items"] if item["label"] == "Applied")
            responded = next(item for item in jobs["items"] if item["label"] == "Responded")
            assert applied["enabled"] is False
            assert responded["enabled"] is False
        nav_ready = system_mod._resolve_nav("RESUME_READY", "cand-1")
        artifacts = next(group for group in nav_ready if group["label"] == "Artifacts")
        assert all(item["enabled"] for item in artifacts["items"])
        candidate = next(group for group in nav_ready if group["label"] == "Candidate")
        assert candidate["items"][0]["enabled"] is True

    def test_resolve_nav_uses_string_enabled_gate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            system_mod,
            "NAV_CONFIG",
            [{"label": "G", "items": [{"label": "X", "path": "/x", "enabled": "ACTIVE_SEARCH"}]}],
        )
        monkeypatch.setattr(system_mod, "_get_company_counts", lambda candidate_id: {})
        monkeypatch.setattr(system_mod, "_get_job_counts", lambda candidate_id: {})
        nav = system_mod._resolve_nav("NEW_CANDIDATE", "cand-1")
        assert nav[0]["items"][0]["enabled"] is False
        nav_live = system_mod._resolve_nav("ACTIVE_SEARCH", "cand-1")
        assert nav_live[0]["items"][0]["enabled"] is True


class TestAst1116ShapesCoverLetter:
    """AST-1116: /api/shapes/candidates exposes detail.cover_letter field defs."""

    def test_shapes_candidates_detail_cover_letter(
        self, system_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        resp = system_client.get("/api/shapes/candidates", headers=auth_headers)
        assert resp.status_code == 200
        cover = resp.get_json()["detail"]["cover_letter"]
        assert [f["key"] for f in cover] == ["Subject", "Letter", "signature"]


class TestAst1253StateUiManifestChainFields:
    """AST-1253: GET /state_ui_manifest merges live chain arrays from core."""

    def test_manifest_includes_chain_fields(
        self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            system_mod,
            "requested_artifacts_chain_task_keys",
            lambda: ["craft_get_rubric", "craft_do_rubric"],
        )
        monkeypatch.setattr(
            system_mod,
            "requested_artifacts_chain_hop_labels",
            lambda: ["Get Job Criteria", "Do Job Criteria"],
        )
        monkeypatch.setattr(
            system_mod,
            "requested_artifacts_chain_artifact_keys",
            lambda: ["get_rubric", "do_rubric"],
        )
        resp = system_client.get("/api/state_ui_manifest", headers=auth_headers)
        assert resp.status_code == 200
        cand = resp.get_json()["candidate"]
        assert cand["artifacts_chain_task_keys"] == ["craft_get_rubric", "craft_do_rubric"]
        assert cand["artifacts_chain_hop_labels"] == ["Get Job Criteria", "Do Job Criteria"]
        assert cand["artifacts_chain_artifact_keys"] == ["get_rubric", "do_rubric"]
        assert "ARTIFACTS_READY" in cand["artifact_generate_states"]

    def test_manifest_degrades_chain_on_walk_failure(
        self, system_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            system_mod,
            "requested_artifacts_chain_task_keys",
            MagicMock(side_effect=RuntimeError("boom")),
        )
        resp = system_client.get("/api/state_ui_manifest", headers=auth_headers)
        assert resp.status_code == 200
        cand = resp.get_json()["candidate"]
        assert cand["artifacts_chain_task_keys"] == []
        assert cand["artifacts_chain_hop_labels"] == []
        assert cand["artifacts_chain_artifact_keys"] == []
        assert "artifact_generate_states" in cand


class TestAst1375InflightHideStatesManifest:
    """AST-1375: state_ui_manifest exposes artifact_generate_inflight_hide_states."""

    def test_manifest_includes_inflight_hide_states(
        self, system_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        from src.utils.config import build_state_ui_manifest

        resp = system_client.get("/api/state_ui_manifest", headers=auth_headers)
        assert resp.status_code == 200
        cand = resp.get_json()["candidate"]
        expected = build_state_ui_manifest()["candidate"]["artifact_generate_inflight_hide_states"]
        assert cand["artifact_generate_inflight_hide_states"] == expected
        assert cand["artifact_generate_inflight_hide_states"] == [
            "REQUESTED_ARTIFACTS",
            "REQUESTED_ARTIFACTS_RETRY",
        ]


class TestAst1351ExperienceJobUiConfig:
    """AST-1351: ui_config exposes experience job field spine + unsupported message."""

    def test_ui_config_includes_experience_job_fields(
        self, system_client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        from src.utils.config import BUILD_CONFIG

        payload = system_client.get("/api/ui_config", headers=auth_headers).get_json()
        fields = payload.get("experience_job_ui_fields")
        assert fields == BUILD_CONFIG["experience_job_ui_fields"]
        assert payload.get("unsupported_resume_structure_message") == BUILD_CONFIG[
            "unsupported_resume_structure_message"
        ]


class TestAst1373AuthSessionPolicyRoute:
    """AST-1373: public GET /api/auth_session_policy (pre-login SPA read)."""

    def test_auth_session_policy_is_open(self, system_client: FlaskClient) -> None:
        # No Bearer — deliberately public for authenticate handoff (sibling AST-1374).
        resp = system_client.get("/api/auth_session_policy")
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload == {
            "session_duration_minutes": 20,
            "activity_extension_interval_minutes": 10,
        }
        for forbidden in (
            "stytch_secret",
            "stytch_project_id",
            "admin_user_ids",
            "admin_emails",
        ):
            assert forbidden not in payload

    def test_auth_session_policy_reflects_config(
        self, system_client: FlaskClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.utils import config as cfg

        monkeypatch.setitem(cfg.AUTH_CONFIG, "session_duration_minutes", 45)
        monkeypatch.setitem(cfg.AUTH_CONFIG, "activity_extension_interval_minutes", 15)
        payload = system_client.get("/api/auth_session_policy").get_json()
        assert payload == {
            "session_duration_minutes": 45,
            "activity_extension_interval_minutes": 15,
        }


class TestAst1440AuthPassthroughRoute:
    """AST-1440: public GET /api/auth_passthrough + local /api/me and /api/nav_config."""

    @pytest.mark.parametrize(
        "env, expected",
        [
            ("local", True),
            ("staging", False),
            ("production", False),
            (None, False),
        ],
    )
    def test_auth_passthrough_follows_deploy_env(
        self,
        system_client: FlaskClient,
        monkeypatch: pytest.MonkeyPatch,
        env: str | None,
        expected: bool,
    ) -> None:
        if env is None:
            monkeypatch.delenv("ASTRAL_DEPLOY_ENV", raising=False)
        else:
            monkeypatch.setenv("ASTRAL_DEPLOY_ENV", env)
        resp = system_client.get("/api/auth_passthrough")
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload == {"local_auth_passthrough": expected}
        for forbidden in ("stytch_secret", "stytch_project_id", "admin_user_ids", "admin_emails"):
            assert forbidden not in payload

    def test_me_and_nav_config_passthrough_when_local(
        self, system_client: FlaskClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "local")
        me = system_client.get("/api/me")
        assert me.status_code == 200
        body = me.get_json()
        assert body["user_id"] == "local-operator"
        assert body["is_admin"] is True
        nav = system_client.get("/api/nav_config")
        assert nav.status_code == 200

    def test_me_still_401_when_staging(
        self, system_client: FlaskClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ASTRAL_DEPLOY_ENV", "staging")
        assert system_client.get("/api/me").status_code == 401

