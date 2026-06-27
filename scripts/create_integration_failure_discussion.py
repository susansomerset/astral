#!/usr/bin/env python3
"""Open Linear Discussion for integration harness failure (AST-818)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.linear.app/graphql"
TEAM_KEY = "AST"
PARENT_NUMBER = 512
PROJECT_NAME = "Astral Foundation"
STATE_NAME = "Discussion"
DEFAULT_HOST = "astral-test.up.railway.app"
DEFAULT_CHUCKLES_EMAIL = "susan+chuckles@susansomerset.com"


def _api_key() -> str:
    for name in ("LINEAR_KEY_CHUCKLES", "LINEAR_API_KEY", "LINEAR_KEY_CURSOR"):
        val = os.environ.get(name, "").strip()
        if val:
            return val
    print("BLOCKED: set LINEAR_KEY_CHUCKLES or LINEAR_API_KEY", file=sys.stderr)
    sys.exit(2)


def _gql(key: str, query: str, variables: dict | None = None) -> dict:
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        API,
        data=body,
        headers={"Authorization": key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        print(f"Linear HTTP {exc.code}: {err_body[:500]}", file=sys.stderr)
        sys.exit(1)
    if data.get("errors"):
        print(json.dumps(data["errors"], indent=2), file=sys.stderr)
        sys.exit(1)
    return data["data"]


def _resolve_ids(key: str, chuckles_email: str) -> tuple[str, str, str, str, str]:
    query = """
    query ResolveIds($teamKey: String!, $stateName: String!, $projectName: String!,
                     $chucklesEmail: String!, $parentNumber: Float!) {
      teams(filter: { key: { eq: $teamKey } }) { nodes { id } }
      workflowStates(filter: { team: { key: { eq: $teamKey } }, name: { eq: $stateName } }) {
        nodes { id }
      }
      projects(filter: { name: { eq: $projectName } }) { nodes { id } }
      users(filter: { email: { eq: $chucklesEmail } }) { nodes { id } }
      parent: issues(filter: { team: { key: { eq: $teamKey } }, number: { eq: $parentNumber } }) {
        nodes { id }
      }
    }
    """
    variables = {
        "teamKey": TEAM_KEY,
        "stateName": STATE_NAME,
        "projectName": PROJECT_NAME,
        "chucklesEmail": chuckles_email,
        "parentNumber": float(PARENT_NUMBER),
    }
    data = _gql(key, query, variables)
    try:
        team_id = data["teams"]["nodes"][0]["id"]
        state_id = data["workflowStates"]["nodes"][0]["id"]
        project_id = data["projects"]["nodes"][0]["id"]
        chuckles_id = data["users"]["nodes"][0]["id"]
        parent_id = data["parent"]["nodes"][0]["id"]
    except (IndexError, KeyError) as exc:
        print(f"BLOCKED: Linear lookup failed: {exc}", file=sys.stderr)
        sys.exit(1)
    return team_id, project_id, state_id, chuckles_id, parent_id


def _read_log_tail(log_path: str, tail_lines: int) -> str:
    if not log_path or not os.path.isfile(log_path):
        return ""
    with open(log_path, encoding="utf-8", errors="replace") as handle:
        lines = handle.readlines()
    return "".join(lines[-tail_lines:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Create Linear Discussion for integration failure")
    parser.add_argument("--sha", required=True, help="origin/dev full sha")
    parser.add_argument("--railway-sha", default="", help="RAILWAY_GIT_COMMIT_SHA")
    parser.add_argument("--host", default=os.environ.get("ASTRAL_RAILWAY_TEST_HOST_URL", ""))
    parser.add_argument("--log", default="", help="path to harness log file")
    parser.add_argument("--tail-lines", type=int, default=80)
    args = parser.parse_args()

    key = _api_key()
    chuckles_email = os.environ.get("LINEAR_CHUCKLES_EMAIL", DEFAULT_CHUCKLES_EMAIL).strip()
    team_id, project_id, state_id, chuckles_id, parent_id = _resolve_ids(key, chuckles_email)

    log_tail = _read_log_tail(args.log, args.tail_lines)
    host = args.host.strip() or DEFAULT_HOST
    railway_sha = args.railway_sha.strip() or args.sha
    short = args.sha[:7]
    title = f"Integration harness failure — test host @ {short}"
    body = f"""## Deploy
- origin/dev: {args.sha}
- railway RAILWAY_GIT_COMMIT_SHA: {railway_sha}
- test host: {host}

## Command
./scripts/testing/post_deploy_integration_gate.sh

## Log tail
```
{log_tail or "(no log file)"}
```

## Joan action
Auto-opened by post-deploy gate (AST-818). Chuckles triages — Joan does not fix product.
"""

    mutation = """
    mutation CreateIssue($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue { identifier url }
      }
    }
    """
    variables = {
        "input": {
            "teamId": team_id,
            "projectId": project_id,
            "stateId": state_id,
            "assigneeId": chuckles_id,
            "parentId": parent_id,
            "title": title,
            "description": body,
        }
    }
    result = _gql(key, mutation, variables)
    issue = result.get("issueCreate", {}).get("issue") or {}
    identifier = issue.get("identifier", "")
    url = issue.get("url", "")
    if not identifier:
        print("BLOCKED: issueCreate returned no issue", file=sys.stderr)
        return 1
    print(f"{identifier} {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
