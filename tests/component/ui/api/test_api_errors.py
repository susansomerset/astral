"""Component tests for src/ui/api_errors.py and /api/* exception handler (AST-779)."""

from __future__ import annotations

from typing import Iterator

import pytest
from flask import Flask, request
from flask.testing import FlaskClient

from ui.api_errors import error_json, server_error_from_exception


def _register_api_exception_handler(app: Flask) -> None:
    @app.errorhandler(Exception)
    def _api_uncaught_exception(exc: Exception):
        if not request.path.startswith("/api/"):
            raise exc
        return server_error_from_exception(exc)


@pytest.fixture
def api_errors_client() -> Iterator[FlaskClient]:
    app = Flask(__name__)
    app.config["TESTING"] = True
    _register_api_exception_handler(app)

    @app.get("/api/test/boom")
    def _api_boom() -> None:
        raise RuntimeError("boom")

    @app.get("/page/boom")
    def _page_boom() -> None:
        raise RuntimeError("page boom")

    with app.test_client() as client:
        yield client


class TestApiErrorsHelpers:
    def test_error_json_includes_error_and_extra(self, api_errors_client: FlaskClient) -> None:
        app = api_errors_client.application
        with app.app_context():
            resp, status = error_json("bad", 400, exception_type="ValueError")
        payload = resp.get_json()
        assert status == 400
        assert payload == {"error": "bad", "exception_type": "ValueError"}

    def test_server_error_from_exception_enriches_500(self, api_errors_client: FlaskClient) -> None:
        app = api_errors_client.application
        try:
            raise RuntimeError("boom")
        except RuntimeError as exc:
            with app.app_context():
                resp, status = server_error_from_exception(exc)
        payload = resp.get_json()
        assert status == 500
        assert payload["error"] == "boom"
        assert payload["exception_type"] == "RuntimeError"
        assert "RuntimeError: boom" in payload["traceback"]


class TestApiUncaughtExceptionHandler:
    def test_api_route_returns_enriched_500_json(self, api_errors_client: FlaskClient) -> None:
        resp = api_errors_client.get("/api/test/boom")
        assert resp.status_code == 500
        payload = resp.get_json()
        assert payload["error"] == "boom"
        assert payload["exception_type"] == "RuntimeError"
        assert "RuntimeError: boom" in payload["traceback"]

    def test_non_api_route_not_swallowed_by_handler(self, api_errors_client: FlaskClient) -> None:
        with pytest.raises(RuntimeError, match="page boom"):
            api_errors_client.get("/page/boom")
