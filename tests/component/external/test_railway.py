"""Component tests for src/external/railway.py (AST-2250)."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest
import requests

from src.external import railway as railway_mod

_ENV = {
    "ASTRAL_RAILWAY_TOKEN": "tok-secret",
    "ASTRAL_RAILWAY_PROJECT_ID": "proj-1",
    "ASTRAL_RAILWAY_ENVIRONMENT_ID": "env-1",
    "ASTRAL_RAILWAY_SERVICE_ID": "svc-1",
}
_SECRET = "sk-live-value"


def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, val in _ENV.items():
        monkeypatch.setenv(key, val)


def _response(*, status: int = 200, payload: object | None = None, bad_json: bool = False) -> MagicMock:
    rsp = MagicMock()
    rsp.status_code = status
    rsp.text = "body-must-not-be-logged " + _SECRET
    if bad_json:
        rsp.json.side_effect = ValueError("not json " + _SECRET)
    else:
        rsp.json.return_value = payload
    return rsp


def _post(monkeypatch: pytest.MonkeyPatch, rsp: MagicMock) -> MagicMock:
    post = MagicMock(return_value=rsp)
    monkeypatch.setattr(railway_mod.requests, "post", post)
    return post


def _assert_ids(sent: dict) -> None:
    assert sent["projectId"] == "proj-1"
    assert sent["environmentId"] == "env-1"
    assert sent["serviceId"] == "svc-1"


class TestAst2250RailwayVariableClient:
    def test_upsert_posts_one_variable_and_skips_deploy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _env(monkeypatch)
        post = _post(monkeypatch, _response(payload={"data": {"variableCollectionUpsert": True}}))
        assert railway_mod.upsert_service_variable(name="CANDIDATE_ADA_1_ANTHROPIC", value=_SECRET) is None
        assert post.call_count == 1
        kwargs = post.call_args.kwargs
        assert kwargs["timeout"] == 30
        assert post.call_args.args[0] == "https://backboard.railway.com/graphql/v2"
        assert kwargs["headers"]["Authorization"] == "Bearer tok-secret"
        body = kwargs["json"]
        assert body["query"].lstrip().startswith("mutation")
        assert "variableCollectionUpsert" in body["query"]
        assert "skipDeploys" in body["query"]
        _assert_ids(body["variables"])
        assert body["variables"]["variables"] == {"CANDIDATE_ADA_1_ANTHROPIC": _SECRET}
        assert body["variables"]["skipDeploys"] is True

    def test_delete_posts_name_without_skip_deploys(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _env(monkeypatch)
        post = _post(monkeypatch, _response(payload={"data": {"variableDelete": True}}))
        assert railway_mod.delete_service_variable(name="CANDIDATE_ADA_1_ANTHROPIC") is None
        body = post.call_args.kwargs["json"]
        assert "variableDelete" in body["query"]
        assert "skipDeploys" not in body["query"]
        assert "skipDeploys" not in body["variables"]
        assert body["variables"]["name"] == "CANDIDATE_ADA_1_ANTHROPIC"
        _assert_ids(body["variables"])

    def test_deploy_returns_id_and_does_not_log_it(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        _env(monkeypatch)
        post = _post(monkeypatch, _response(payload={"data": {"serviceInstanceDeployV2": "dep-9"}}))
        with caplog.at_level(logging.DEBUG, logger="src.external.railway"):
            assert railway_mod.trigger_service_deploy() == "dep-9"
        body = post.call_args.kwargs["json"]
        assert body["query"].lstrip().startswith("mutation")
        assert "serviceInstanceDeployV2" in body["query"]
        assert set(body["variables"]) == {"environmentId", "serviceId"}
        assert body["variables"]["environmentId"] == "env-1"
        assert body["variables"]["serviceId"] == "svc-1"
        assert "dep-9" not in caplog.text

    def test_blank_name_or_value_raises_before_http(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _env(monkeypatch)
        post = _post(monkeypatch, _response(payload={}))
        with pytest.raises(ValueError, match="name and value are required"):
            railway_mod.upsert_service_variable(name="  ", value=_SECRET)
        with pytest.raises(ValueError, match="name and value are required"):
            railway_mod.upsert_service_variable(name="CANDIDATE_ADA_1_ANTHROPIC", value="")
        with pytest.raises(ValueError, match="name and value are required"):
            railway_mod.upsert_service_variable(name="CANDIDATE_ADA_1_ANTHROPIC", value=None)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="name is required"):
            railway_mod.delete_service_variable(name="")
        assert post.call_count == 0

    def test_missing_env_is_key_error_without_log(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        _env(monkeypatch)
        monkeypatch.delenv("ASTRAL_RAILWAY_TOKEN")
        post = _post(monkeypatch, _response(payload={}))
        with caplog.at_level(logging.DEBUG, logger="src.external.railway"):
            with pytest.raises(KeyError, match="ASTRAL_RAILWAY_TOKEN"):
                railway_mod.upsert_service_variable(name="CANDIDATE_ADA_1_ANTHROPIC", value=_SECRET)
        assert post.call_count == 0
        assert caplog.records == []

    def test_http_error_logs_status_only(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        _env(monkeypatch)
        _post(monkeypatch, _response(status=401, payload={"data": {}}))
        with caplog.at_level(logging.ERROR, logger="src.external.railway"):
            with pytest.raises(railway_mod.RailwayCallFailed, match="railway upsert failed for CANDIDATE_ADA_1_ANTHROPIC") as caught:
                railway_mod.upsert_service_variable(name="CANDIDATE_ADA_1_ANTHROPIC", value=_SECRET)
        assert caught.value.__cause__ is None
        assert caught.value.__suppress_context__ is True
        assert _SECRET not in str(caught.value)
        assert "tok-secret" not in str(caught.value)
        assert "body-must-not-be-logged" not in caplog.text
        assert _SECRET not in caplog.text
        assert "tok-secret" not in caplog.text
        assert "HTTP 401" in caplog.text
        assert "The Railway call did not finish" in caplog.text
        assert len(caplog.records) == 1

    def test_request_exception_redacts_secret_and_token(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        _env(monkeypatch)
        post = MagicMock(side_effect=requests.ConnectionError(f"down {_SECRET} tok-secret"))
        monkeypatch.setattr(railway_mod.requests, "post", post)
        with caplog.at_level(logging.ERROR, logger="src.external.railway"):
            with pytest.raises(railway_mod.RailwayCallFailed, match="railway upsert failed for CANDIDATE_ADA_1_ANTHROPIC"):
                railway_mod.upsert_service_variable(name="CANDIDATE_ADA_1_ANTHROPIC", value=_SECRET)
        assert _SECRET not in caplog.text
        assert "tok-secret" not in caplog.text
        assert "[redacted]" in caplog.text
        assert len(caplog.records) == 1

    def test_graphql_errors_are_not_returned(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        _env(monkeypatch)
        _post(
            monkeypatch,
            _response(payload={"errors": [{"message": f"nope {_SECRET} tok-secret"}]}),
        )
        with caplog.at_level(logging.ERROR, logger="src.external.railway"):
            with pytest.raises(
                railway_mod.RailwayCallFailed,
                match=r"^railway upsert failed for CANDIDATE_ADA_1_ANTHROPIC$",
            ) as caught:
                railway_mod.upsert_service_variable(name="CANDIDATE_ADA_1_ANTHROPIC", value=_SECRET)
        assert "nope" not in str(caught.value)
        assert _SECRET not in caplog.text
        assert "tok-secret" not in caplog.text
        assert "[redacted]" in caplog.text

    def test_graphql_error_shapes_and_bad_json(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _env(monkeypatch)
        post = _post(monkeypatch, _response(payload={"errors": ["plain"]}))
        with pytest.raises(railway_mod.RailwayCallFailed, match="railway deploy failed$"):
            railway_mod.trigger_service_deploy()
        post.return_value = _response(payload={"errors": "boom"})
        with pytest.raises(railway_mod.RailwayCallFailed, match="railway deploy failed$"):
            railway_mod.trigger_service_deploy()
        post.return_value = _response(payload=["not-a-dict"])
        with pytest.raises(railway_mod.RailwayCallFailed, match="railway deploy failed$"):
            railway_mod.trigger_service_deploy()
        post.return_value = _response(bad_json=True)
        with pytest.raises(railway_mod.RailwayCallFailed, match="railway deploy failed$"):
            railway_mod.trigger_service_deploy()
        post.return_value = _response(payload={"data": None})
        with pytest.raises(railway_mod.RailwayCallFailed, match="railway deploy failed$"):
            railway_mod.trigger_service_deploy()

    def test_false_upsert_delete_and_empty_deploy_fail(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _env(monkeypatch)
        post = _post(monkeypatch, _response(payload={"data": {"variableCollectionUpsert": False}}))
        with pytest.raises(railway_mod.RailwayCallFailed, match="railway upsert failed for CANDIDATE_ADA_1_ANTHROPIC"):
            railway_mod.upsert_service_variable(name="CANDIDATE_ADA_1_ANTHROPIC", value=_SECRET)
        post.return_value = _response(payload={"data": {"variableDelete": False}})
        with pytest.raises(railway_mod.RailwayCallFailed, match="railway delete failed for CANDIDATE_ADA_1_ANTHROPIC"):
            railway_mod.delete_service_variable(name="CANDIDATE_ADA_1_ANTHROPIC")
        post.return_value = _response(payload={"data": {"serviceInstanceDeployV2": ""}})
        with pytest.raises(railway_mod.RailwayCallFailed, match="railway deploy failed$"):
            railway_mod.trigger_service_deploy()
        post.return_value = _response(payload={"data": {"serviceInstanceDeployV2": 12}})
        with pytest.raises(railway_mod.RailwayCallFailed, match="railway deploy failed$"):
            railway_mod.trigger_service_deploy()

    def test_calls_external_io_guard(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _env(monkeypatch)
        seen: list[str] = []

        def _guard(caller: str) -> None:
            seen.append(caller)

        monkeypatch.setattr(railway_mod, "require_controlled_external_io", _guard)
        _post(monkeypatch, _response(payload={"data": {"variableCollectionUpsert": True}}))
        railway_mod.upsert_service_variable(name="CANDIDATE_ADA_1_ANTHROPIC", value=_SECRET)
        assert seen == ["railway.upsert"]

    def test_public_surface(self) -> None:
        assert set(railway_mod.__all__) == {
            "RailwayCallFailed",
            "delete_service_variable",
            "trigger_service_deploy",
            "upsert_service_variable",
        }
