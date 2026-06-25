"""Linear GraphQL client for deploy-status parent state lookup (AST-792)."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

LINEAR_GRAPHQL_URL = "https://api.linear.app/graphql"
_TEAM_KEY = "AST"

__all__ = ["LinearApiError", "fetch_parent_issue_states"]

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
            "Authorization": os.environ["LINEAR_API_KEY"],
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
