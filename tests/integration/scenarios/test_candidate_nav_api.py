"""AST-711 first integration scenario: real SQLite + HTTP + auth across API → core → data."""

from __future__ import annotations

from flask import Flask


def _jobs_group(payload: list) -> dict | None:
    # AST-2230: Jobs → Job Opportunities
    return next((group for group in payload if group.get("label") == "Job Opportunities"), None)


def test_list_candidates_returns_seeded_row(
    integration_app: Flask,
    seeded_candidate,
    auth_headers: dict[str, str],
) -> None:
    client = integration_app.test_client()
    resp = client.get("/api/candidates", headers=auth_headers)
    assert resp.status_code == 200
    rows = resp.get_json()
    assert isinstance(rows, list)
    assert any(
        row.get("astral_candidate_id") == "cand-1" and row.get("state") == "ACTIVE_SEARCH"
        for row in rows
    )


def test_nav_config_reflects_seeded_candidate_state(
    integration_app: Flask,
    seeded_candidate,
    auth_headers: dict[str, str],
) -> None:
    client = integration_app.test_client()
    resp = client.get("/api/nav_config?candidate_id=cand-1", headers=auth_headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    jobs = _jobs_group(payload)
    assert jobs is not None
    # AST-2230: Ready to Apply under Job Opportunities; badge counts still present.
    ready = next(item for item in jobs["items"] if item["path"] == "/jobs/ready")
    assert ready["enabled"] is True
    assert all("count" in item for item in jobs["items"])
    labels = [group["label"] for group in payload]
    assert labels[:4] == ["Candidate", "Criteria", "Company", "Job Opportunities"]

    # NEW_CANDIDATE (stage 1) still gets the four facing groups; Criteria items disabled.
    seeded_candidate.save_candidate(
        "cand-1", state="NEW_CANDIDATE", candidate_data={"name": "Integration Test"}
    )
    resp_new = client.get("/api/nav_config?candidate_id=cand-1", headers=auth_headers)
    payload_new = resp_new.get_json()
    assert _jobs_group(payload_new) is not None
    labels_new = [group["label"] for group in payload_new]
    assert labels_new[:4] == ["Candidate", "Criteria", "Company", "Job Opportunities"]
    criteria = next(g for g in payload_new if g["label"] == "Criteria")
    assert all(it["enabled"] is False for it in criteria["items"])


def test_unauthenticated_nav_config_returns_401(integration_app: Flask, seeded_candidate) -> None:
    client = integration_app.test_client()
    resp = client.get("/api/nav_config?candidate_id=cand-1")
    assert resp.status_code == 401
