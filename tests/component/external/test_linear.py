"""Component tests for src/external/linear.py (AST-792)."""

from __future__ import annotations

import json

import pytest

from src.external import linear as linear_mod
from src.external.linear import LinearApiError, fetch_parent_issue_states, fetch_user_testing_parent_ids


class _FakeResponse:
    def __init__(self, body: str) -> None:
        self._body = body.encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None


def _mock_graphql(monkeypatch: pytest.MonkeyPatch, payload: dict) -> None:
    monkeypatch.setenv("LINEAR_API_KEY", "test-linear-key")

    def _urlopen(_req, timeout=60):
        return _FakeResponse(json.dumps(payload))

    monkeypatch.setattr("urllib.request.urlopen", _urlopen)


class TestFetchParentIssueStates:
    def test_fetch_parent_issue_states_maps_identifiers(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _mock_graphql(
            monkeypatch,
            {
                "data": {
                    "issues": {
                        "nodes": [
                            {"identifier": "AST-100", "state": {"name": "User Testing"}},
                            {"identifier": "AST-200", "state": {"name": "Done"}},
                        ]
                    }
                }
            },
        )
        assert fetch_parent_issue_states(["AST-100", "AST-200"]) == {
            "AST-100": "User Testing",
            "AST-200": "Done",
        }

    def test_fetch_parent_issue_states_empty_input(self) -> None:
        assert fetch_parent_issue_states([]) == {}

    def test_invalid_ticket_id_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LINEAR_API_KEY", "test-linear-key")
        with pytest.raises(ValueError, match="invalid ticket id"):
            fetch_parent_issue_states(["not-a-ticket"])

    def test_graphql_errors_raise_linear_api_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _mock_graphql(monkeypatch, {"errors": [{"message": "bad query"}]})
        with pytest.raises(LinearApiError):
            fetch_parent_issue_states(["AST-100"])


class TestResolveLinearApiKey:
    def test_resolve_linear_api_key_prefers_linear_api_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("LINEAR_API_KEY", "primary-key")
        monkeypatch.setenv("LINEAR_KEY_CHUCKLES", "chuckles-key")
        assert linear_mod._resolve_linear_api_key() == "primary-key"

    def test_resolve_linear_api_key_falls_back_to_chuckles_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("LINEAR_API_KEY", raising=False)
        monkeypatch.setenv("LINEAR_KEY_CHUCKLES", "chuckles-key")
        assert linear_mod._resolve_linear_api_key() == "chuckles-key"

    def test_fetch_raises_linear_api_error_when_no_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        for name in linear_mod._LINEAR_KEY_ENVS:
            monkeypatch.delenv(name, raising=False)
        with pytest.raises(LinearApiError, match="not configured"):
            fetch_parent_issue_states(["AST-791"])


class TestFetchUserTestingParentIds:
    def test_fetch_user_testing_parent_ids_returns_sorted_parents(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _mock_graphql(
            monkeypatch,
            {
                "data": {
                    "issues": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "nodes": [
                            {"identifier": "AST-791"},
                            {"identifier": "AST-650"},
                        ],
                    }
                }
            },
        )
        assert fetch_user_testing_parent_ids("User Testing") == [
            "AST-650",
            "AST-791",
        ]

    def test_fetch_user_testing_parent_ids_paginates(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("LINEAR_API_KEY", "test-linear-key")
        pages = [
            {
                "data": {
                    "issues": {
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor-1"},
                        "nodes": [{"identifier": "AST-100"}],
                    }
                }
            },
            {
                "data": {
                    "issues": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "nodes": [{"identifier": "AST-200"}],
                    }
                }
            },
        ]
        calls: list[dict | None] = []

        def _urlopen(req, timeout=60):
            body = json.loads(req.data.decode("utf-8"))
            calls.append(body.get("variables"))
            return _FakeResponse(json.dumps(pages[len(calls) - 1]))

        monkeypatch.setattr("urllib.request.urlopen", _urlopen)
        assert fetch_user_testing_parent_ids("User Testing") == [
            "AST-100",
            "AST-200",
        ]
        assert calls[1]["after"] == "cursor-1"
