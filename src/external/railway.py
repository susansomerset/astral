"""Railway public API — one service variable and one deploy trigger (AST-2250).

No variable read. Callers name the variable; this module does not know candidates.
Faults log once here and raise RailwayCallFailed. Callers do not log that exception.
A missing ASTRAL_RAILWAY_* env var is a bare KeyError from os.environ.
"""

from __future__ import annotations

import os
from typing import Dict, NoReturn

import requests

from src.utils.config import CANDIDATE_SECRET_RAILWAY_CONFIG
from src.utils.integration_io import require_controlled_external_io
from src.utils.logging import get_logger

_POST_TIMEOUT_SEC = 30

# Railway CLI v4.58.0 src/gql/mutations/strings/VariableCollectionUpsert.graphql
_UPSERT = """
mutation VariableCollectionUpsert($projectId: String!, $serviceId: String!, $environmentId: String!, $variables: EnvironmentVariables!, $skipDeploys: Boolean) {
  variableCollectionUpsert(
    input: {projectId: $projectId, environmentId: $environmentId, serviceId: $serviceId, variables: $variables, skipDeploys: $skipDeploys}
  )
}
"""

# VariableDelete.graphql — no skipDeploys argument.
_DELETE = """
mutation VariableDelete($projectId: String!, $environmentId: String!, $name: String!, $serviceId: String) {
  variableDelete(
    input: {projectId: $projectId, environmentId: $environmentId, name: $name, serviceId: $serviceId}
  )
}
"""

# ServiceInstanceDeploy.graphql
_DEPLOY = """
mutation ServiceInstanceDeploy($environmentId: String!, $serviceId: String!) {
  serviceInstanceDeployV2(environmentId: $environmentId, serviceId: $serviceId)
}
"""

logger = get_logger(__name__)

__all__ = [
    "RailwayCallFailed",
    "delete_service_variable",
    "trigger_service_deploy",
    "upsert_service_variable",
]


class RailwayCallFailed(RuntimeError):
    """Railway call already logged. Message is operation and variable name only."""


def _redact(text: str, *secrets: str) -> str:
    out = text
    for secret in secrets:
        if secret:
            out = out.replace(secret, "[redacted]")
    return out


def _fail(
    operation: str,
    variable_name: str,
    exc: BaseException,
    secret_value: str,
    token: str,
) -> NoReturn:
    safe = _redact(str(exc), secret_value, token)
    # Traceback is this redacted RuntimeError, not the provider body.
    try:
        raise RuntimeError(safe) from None
    except RuntimeError:
        logger.exception(
            "railway %s | variable %s\n  %s: %s\n  The Railway call did not finish",
            operation,
            variable_name or "-",
            type(exc).__name__,
            safe,
        )
        if variable_name:
            message = f"railway {operation} failed for {variable_name}"
        else:
            message = f"railway {operation} failed"
        raise RailwayCallFailed(message) from None


def _target() -> dict:
    cfg = CANDIDATE_SECRET_RAILWAY_CONFIG
    return {
        "token": os.environ[cfg["token_env"]],
        "project_id": os.environ[cfg["project_id_env"]],
        "environment_id": os.environ[cfg["environment_id_env"]],
        "service_id": os.environ[cfg["service_id_env"]],
    }


def _post(
    query: str,
    variables: dict,
    *,
    operation: str,
    variable_name: str,
    secret_value: str,
) -> dict:
    require_controlled_external_io(f"railway.{operation}")
    ids = _target()
    token = ids["token"]
    bound = {
        "projectId": ids["project_id"],
        "environmentId": ids["environment_id"],
        "serviceId": ids["service_id"],
    }
    for key, val in bound.items():
        if key in variables:
            variables[key] = val
    try:
        resp = requests.post(
            CANDIDATE_SECRET_RAILWAY_CONFIG["graphql_url"],
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={"query": query, "variables": variables},
            timeout=_POST_TIMEOUT_SEC,
        )
    except requests.RequestException as exc:
        _fail(operation, variable_name, exc, secret_value, token)
    if resp.status_code >= 400:
        _fail(
            operation,
            variable_name,
            RuntimeError(f"HTTP {resp.status_code}"),
            secret_value,
            token,
        )
    try:
        payload = resp.json()
    except ValueError as exc:
        _fail(operation, variable_name, exc, secret_value, token)
    errors = payload.get("errors") if isinstance(payload, dict) else payload
    if errors:
        messages = []
        if isinstance(errors, list):
            for err in errors:
                if isinstance(err, dict) and err.get("message"):
                    messages.append(str(err["message"]))
                else:
                    messages.append(str(err))
        else:
            messages.append(str(errors))
        _fail(
            operation,
            variable_name,
            RuntimeError(_redact("; ".join(messages), secret_value, token)),
            secret_value,
            token,
        )
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        _fail(
            operation,
            variable_name,
            RuntimeError("Railway response had no data"),
            secret_value,
            token,
        )
    return data


def upsert_service_variables(variables: Dict[str, str]) -> None:
    """Upsert one or more service variables in one call. skipDeploys so the caller triggers deploy."""
    if not variables:
        raise ValueError("variables is required")
    for name, value in variables.items():
        if not (name or "").strip() or value is None or value == "":
            raise ValueError("name and value are required")
    first_name = next(iter(variables))
    # Join values so _post / _fail redact every secret in the batch, not only the first.
    redact_blob = "\n".join(variables.values())
    label = first_name if len(variables) == 1 else f"{first_name}+{len(variables) - 1}"
    data = _post(
        _UPSERT,
        {
            "projectId": "",
            "serviceId": "",
            "environmentId": "",
            "variables": dict(variables),
            "skipDeploys": True,
        },
        operation="upsert",
        variable_name=label,
        secret_value=redact_blob,
    )
    if data.get("variableCollectionUpsert") is not True:
        _fail(
            "upsert",
            label,
            RuntimeError("variableCollectionUpsert was not true"),
            redact_blob,
            os.environ[CANDIDATE_SECRET_RAILWAY_CONFIG["token_env"]],
        )


def upsert_service_variable(*, name: str, value: str) -> None:
    """Upsert one service variable. skipDeploys so the caller triggers deploy."""
    upsert_service_variables({name: value})


def delete_service_variable(*, name: str) -> None:
    """Delete one service variable. Does not trigger deploy."""
    if not (name or "").strip():
        raise ValueError("name is required")
    data = _post(
        _DELETE,
        {
            "projectId": "",
            "environmentId": "",
            "name": name,
            "serviceId": "",
        },
        operation="delete",
        variable_name=name,
        secret_value="",
    )
    if data.get("variableDelete") is not True:
        _fail(
            "delete",
            name,
            RuntimeError("variableDelete was not true"),
            "",
            os.environ[CANDIDATE_SECRET_RAILWAY_CONFIG["token_env"]],
        )


def trigger_service_deploy() -> str:
    """Deploy the configured service. Returns the deployment id."""
    data = _post(
        _DEPLOY,
        {"environmentId": "", "serviceId": ""},
        operation="deploy",
        variable_name="",
        secret_value="",
    )
    dep = data.get("serviceInstanceDeployV2")
    if not isinstance(dep, str) or not dep:
        _fail(
            "deploy",
            "",
            RuntimeError("serviceInstanceDeployV2 was empty"),
            "",
            os.environ[CANDIDATE_SECRET_RAILWAY_CONFIG["token_env"]],
        )
    return dep
