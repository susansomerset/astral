"""AST-711 first integration scenario: real SQLite + HTTP + auth across API → core → data."""

from __future__ import annotations

from flask import Flask


def _jobs_group(payload: list) -> dict | None:
    return next((group for group in payload if group.get("label") == "Jobs"), None)


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
        row.get("astral_candidate_id") == "cand-1" and row.get("state") == "LIVE_PROMPTS"
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
    in_review = next(item for item in jobs["items"] if item["path"] == "/jobs/in_review")
    assert in_review["enabled"] is True

    # LIVE_PROMPTS satisfies Jobs group visible gate; NEW would hide the whole group.
    seeded_candidate.save_candidate("cand-1", state="NEW", candidate_data={"name": "Integration Test"})
    resp_new = client.get("/api/nav_config?candidate_id=cand-1", headers=auth_headers)
    assert _jobs_group(resp_new.get_json()) is None


def test_unauthenticated_nav_config_returns_401(integration_app: Flask, seeded_candidate) -> None:
    client = integration_app.test_client()
    resp = client.get("/api/nav_config?candidate_id=cand-1")
    assert resp.status_code == 401
