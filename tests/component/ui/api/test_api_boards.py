"""Component tests for boards catalog (AST-415) and board_search API (AST-416).

Includes read-only adopted-board list/detail and `/searches` CRUD stubs.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from src.utils import config as config_mod
from ui.api import api_boards as boards_api


class TestBoardsReadApi:
    def test_list_empty_when_no_adopted_boards(
        self, boards_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(config_mod, "BOARD_CONFIG", {})
        resp = boards_client.get("/api/boards", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_and_detail_adopted_only(
        self, boards_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            config_mod,
            "BOARD_CONFIG",
            {
                "a16z": {
                    "label": "a16z Jobs",
                    "entry_url": "https://jobs.a16z.com",
                    "adopted": True,
                    "parse_instructions": {},
                    "search_criteria_schema": {"type": "object"},
                    "criteria_param_map": {},
                    "craft_task_key": "craft_joblist_rubric",
                    "scrape_mode": "deep_link",
                },
                "draft": {
                    "label": "Draft",
                    "entry_url": "https://example.com",
                    "adopted": False,
                    "parse_instructions": {},
                    "search_criteria_schema": {},
                    "criteria_param_map": {},
                    "craft_task_key": "craft_joblist_rubric",
                    "scrape_mode": "deep_link",
                },
            },
        )
        listed = boards_client.get("/api/boards", headers=auth_headers)
        assert listed.status_code == 200
        body = listed.get_json()
        assert len(body) == 1
        assert body[0]["board_key"] == "a16z"

        missing = boards_client.get("/api/boards/draft", headers=auth_headers)
        assert missing.status_code == 404

        detail = boards_client.get("/api/boards/a16z", headers=auth_headers)
        assert detail.status_code == 200
        row = detail.get_json()
        assert row["board_key"] == "a16z"
        assert row["label"] == "a16z Jobs"
        assert "parse_instructions" in row

class TestBoardsSearchesApi:
    def test_list_requires_candidate_id(self, boards_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = boards_client.get("/api/boards/searches", headers=auth_headers)
        assert resp.status_code == 400
        assert "candidate_id" in resp.get_json()["error"]

    def test_create_rejects_board_credentials(self, boards_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        body = {
            "candidate_id": "cand-1",
            "board_key": "a16z",
            "label": "x",
            "criteria": {"title_query": "eng"},
            "password": "secret",
        }
        resp = boards_client.post("/api/boards/searches", json=body, headers=auth_headers)
        assert resp.status_code == 400
        assert "credentials" in resp.get_json()["error"]

    def test_create_two_searches_same_board(
        self, boards_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "src.utils.config.BOARD_CONFIG",
            {"a16z": {"status": "adopted"}},
        )
        stored: list[dict] = []

        def _save(candidate_id: str, board_key: str, label: str, criteria: object, **kwargs: object) -> dict:
            row = {
                "board_search_id": f"bs-{len(stored) + 1}",
                "candidate_id": candidate_id,
                "board_key": board_key,
                "label": label,
                "criteria": criteria,
            }
            stored.append(row)
            return row

        monkeypatch.setattr(boards_api, "save_board_search", _save)
        monkeypatch.setattr(boards_api, "list_board_searches", lambda candidate_id, board_key=None: stored)

        payload = {
            "candidate_id": "cand-1",
            "board_key": "a16z",
            "label": "Search A",
            "criteria": {"title_query": "engineer"},
        }
        first = boards_client.post("/api/boards/searches", json=payload, headers=auth_headers)
        second = boards_client.post(
            "/api/boards/searches",
            json={**payload, "label": "Search B"},
            headers=auth_headers,
        )
        assert first.status_code == 201
        assert second.status_code == 201
        assert first.get_json()["board_search_id"] != second.get_json()["board_search_id"]

        listed = boards_client.get("/api/boards/searches?candidate_id=cand-1", headers=auth_headers)
        assert listed.status_code == 200
        assert len(listed.get_json()) == 2

    def test_generate_unknown_task(self, boards_client: FlaskClient, auth_headers: dict[str, str]) -> None:
        resp = boards_client.post(
            "/api/boards/searches/bs-1/generate/not_a_task",
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_generate_delegates_to_core(
        self, boards_client: FlaskClient, auth_headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        gen = MagicMock(return_value=({"label": "My search"}, 200))
        monkeypatch.setattr(boards_api, "run_board_search_generation", gen)
        resp = boards_client.post(
            "/api/boards/searches/bs-1/generate/craft_board_search_label",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["label"] == "My search"
        gen.assert_called_once()
