"""Linear GraphQL client for deploy-status and prep-uat log rebuild (AST-792/800)."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

LINEAR_GRAPHQL_URL = "https://api.linear.app/graphql"
_TEAM_KEY = "AST"
_LINEAR_KEY_ENVS = ("LINEAR_API_KEY", "LINEAR_KEY_CHUCKLES", "LINEAR_KEY_CURSOR")

__all__ = [
    "LinearApiError",
    "fetch_parent_issue_states",
    "fetch_user_testing_parent_ids",
]


def _resolve_linear_api_key() -> str:
    for name in _LINEAR_KEY_ENVS:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    raise LinearApiError("Linear API key not configured")

_TICKET_ID_RE = re.compile(r"^AST-(\d+)$")


class LinearApiError(Exception):
    """Linear GraphQL request failed."""


def _parse_ticket_number(ticket_id: str) -> int:
    normalized = (ticket_id or "").strip().upper()
    match = _TICKET_ID_RE.match(normalized)
    if not match:
        raise ValueError(f"invalid ticket id: {ticket_id!r} (expected AST-<number>)")
    return int(match.group(1))


def _graphql(query: str, variables: dict | None = None) -> dict:
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(
        LINEAR_GRAPHQL_URL,
        data=payload,
        headers={
            "Authorization": _resolve_linear_api_key(),
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise LinearApiError(f"Linear HTTP {exc.code}: {body[:500]}") from exc
    data = json.loads(raw)
    if data.get("errors"):
        raise LinearApiError(json.dumps(data["errors"]))
    if "data" not in data:
        raise LinearApiError("Linear response missing data")
    return data["data"]


def fetch_parent_issue_states(ticket_ids: list[str]) -> dict[str, str | None]:
    """Return {AST-NNN: state.name} for each requested parent id."""
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in ticket_ids:
        ticket_id = (raw or "").strip().upper()
        if not ticket_id or ticket_id in seen:
            continue
        seen.add(ticket_id)
        normalized.append(ticket_id)
    if not normalized:
        return {}

    numbers = [_parse_ticket_number(ticket_id) for ticket_id in normalized]
    query = """
    query IssueStates($teamKey: String!, $numbers: [Float!]!) {
      issues(filter: { team: { key: { eq: $teamKey } }, number: { in: $numbers } }) {
        nodes { identifier state { name } }
      }
    }
    """
    data = _graphql(query, {"teamKey": _TEAM_KEY, "numbers": numbers})
    nodes = data.get("issues", {}).get("nodes") or []
    found: dict[str, str | None] = {}
    for node in nodes:
        identifier = node.get("identifier")
        state = node.get("state") or {}
        name = state.get("name")
        if isinstance(identifier, str) and isinstance(name, str):
            found[identifier] = name
    return {ticket_id: found.get(ticket_id) for ticket_id in normalized}


def fetch_user_testing_parent_ids(uat_state_name: str = "User Testing") -> list[str]:
    """Return sorted top-level parent epic ids in the given Linear workflow state."""
    query = """
    query UserTestingParents($teamKey: String!, $state: String!, $after: String) {
      issues(
        filter: {
          team: { key: { eq: $teamKey } }
          state: { name: { eq: $state } }
          parent: { null: true }
        }
        first: 100
        after: $after
      ) {
        pageInfo { hasNextPage endCursor }
        nodes { identifier }
      }
    }
    """
    identifiers: set[str] = set()
    after: str | None = None
    while True:
        variables: dict = {
            "teamKey": _TEAM_KEY,
            "state": uat_state_name,
            "after": after,
        }
        data = _graphql(query, variables)
        issues = data.get("issues") or {}
        for node in issues.get("nodes") or []:
            identifier = node.get("identifier")
            if isinstance(identifier, str) and identifier.strip():
                identifiers.add(identifier.strip().upper())
        page_info = issues.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        after = page_info.get("endCursor")
        if not after:
            break
    return sorted(identifiers)
