#!/usr/bin/env python3
"""Create or update a GitHub PR (ftr/* → dev) with Linear parent + child summary."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API_URL = "https://api.linear.app/graphql"


def _token() -> str:
    for env in ("LINEAR_API_KEY", "LINEAR_KEY_CHUCKLES", "LINEAR_KEY_CURSOR"):
        t = os.environ.get(env, "").strip()
        if t:
            return t
    print(
        "Missing Linear key: LINEAR_KEY_CHUCKLES or LINEAR_API_KEY",
        file=sys.stderr,
    )
    sys.exit(2)


def _gql(token: str, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Authorization": token, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Linear HTTP {e.code}: {body[:2000]}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(raw)
    if data.get("errors"):
        print(json.dumps(data["errors"], indent=2), file=sys.stderr)
        sys.exit(1)
    return data["data"]


def _run(cmd: list[str], *, cwd: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def _resolve_ftr(repo: Path, parent_id: str, ftr_hint: str | None, *, allow_missing: bool = False) -> str:
    if ftr_hint:
        ref = ftr_hint.removeprefix("origin/").removeprefix("refs/heads/")
        if not ref.startswith("ftr/"):
            ref = f"ftr/{ref}"
        r = _run(["git", "-C", str(repo), "ls-remote", "origin", f"refs/heads/{ref}"], check=False)
        if r.returncode == 0 and r.stdout.strip():
            return ref
        if allow_missing:
            return ref
    pid = parent_id.upper()
    r = _run(
        [
            "git",
            "-C",
            str(repo),
            "ls-remote",
            "--heads",
            "origin",
            f"refs/heads/ftr/*{pid[4:]}*",
            f"refs/heads/ftr/{pid}*",
            f"refs/heads/ftr/*{pid}*",
        ],
        check=False,
    )
    if r.returncode != 0 or not r.stdout.strip():
        print(f"no origin ftr branch for {parent_id}", file=sys.stderr)
        sys.exit(1)
    line = r.stdout.strip().splitlines()[0]
    return line.split("\t", 1)[1].replace("refs/heads/", "")


def _fetch_epic(token: str, parent_id: str) -> dict[str, Any]:
    q = """
    query FinishUpEpic($id: String!) {
      issue(id: $id) {
        identifier
        title
        description
        state { name }
        children {
          nodes {
            identifier
            title
            state { name }
            assignee { name displayName }
          }
        }
      }
    }
    """
    issue = _gql(token, q, {"id": parent_id.upper()})["issue"]
    if not issue:
        print(f"Linear issue not found: {parent_id}", file=sys.stderr)
        sys.exit(1)
    return issue


def _purpose_excerpt(description: str) -> str:
    m = re.search(r"## Purpose\s*\n+(.*?)(?:\n## |\Z)", description or "", re.S)
    if not m:
        return ""
    text = re.sub(r"\s+", " ", m.group(1).strip())
    return text[:500] + ("…" if len(text) > 500 else "")


def _pr_body(issue: dict[str, Any], ftr: str) -> str:
    ident = issue["identifier"]
    title = issue.get("title") or ""
    purpose = _purpose_excerpt(issue.get("description") or "")
    children = (issue.get("children") or {}).get("nodes") or []
    rows: list[str] = []
    for child in sorted(children, key=lambda c: c.get("identifier") or ""):
        cid = child.get("identifier") or "?"
        ctitle = (child.get("title") or "").replace("|", "\\|")
        cstate = ((child.get("state") or {}).get("name") or "").replace("|", "\\|")
        assignee = child.get("assignee") or {}
        dev = (assignee.get("name") or assignee.get("displayName") or "—").replace("|", "\\|")
        rows.append(f"| **{cid}** | {cstate} | {dev} | {ctitle} |")
    child_table = (
        "\n".join(["| Ticket | Status | Dev | Title |", "| --- | --- | --- | --- |", *rows])
        if rows
        else "_No child tickets on parent._"
    )
    parts = [
        f"## Parent epic",
        f"**{ident}** — {title}",
        "",
    ]
    if purpose:
        parts.extend([f"> {purpose}", ""])
    parts.extend(
        [
            f"**Integration branch:** `{ftr}` → `dev`",
            "",
            "## Child tickets",
            child_table,
            "",
            "— Chuckles (`finish-up`)",
        ]
    )
    return "\n".join(parts)


def _pr_title(issue: dict[str, Any]) -> str:
    ident = issue["identifier"]
    title = (issue.get("title") or "").strip()
    short = title[:72] + ("…" if len(title) > 72 else "")
    return f"[{ident}] {short}"


def _existing_pr(repo: Path, ftr: str) -> dict[str, Any] | None:
    r = _run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            _gh_repo(repo),
            "--base",
            "dev",
            "--head",
            ftr,
            "--state",
            "all",
            "--json",
            "number,url,state",
            "--limit",
            "1",
        ],
        check=False,
    )
    if r.returncode != 0:
        print(r.stderr or r.stdout, file=sys.stderr)
        sys.exit(1)
    rows = json.loads(r.stdout or "[]")
    return rows[0] if rows else None


def _gh_repo(repo: Path) -> str:
    r = _run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"], cwd=str(repo))
    return r.stdout.strip()


def _ftr_ahead_of_dev(repo: Path, ftr: str) -> bool:
    """True if origin/ftr has commits not on origin/dev (PR create needs a diff)."""
    _run(["git", "-C", str(repo), "fetch", "origin", "dev", ftr], check=False)
    r = _run(
        ["git", "-C", str(repo), "rev-list", "--count", f"origin/dev..origin/{ftr}"],
        check=False,
    )
    if r.returncode != 0:
        return True
    return int((r.stdout or "0").strip() or 0) > 0


def _create_or_update_pr(repo: Path, ftr: str, title: str, body: str) -> str:
    existing = _existing_pr(repo, ftr)
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(body)
        body_path = f.name
    try:
        if existing:
            num = existing["number"]
            _run(
                [
                    "gh",
                    "pr",
                    "edit",
                    str(num),
                    "--repo",
                    _gh_repo(repo),
                    "--title",
                    title,
                    "--body-file",
                    body_path,
                ]
            )
            url = existing.get("url") or ""
            print(f"PR updated #{num} {url}")
            return str(num)
        if not _ftr_ahead_of_dev(repo, ftr):
            print(f"PR skipped — {ftr} already on dev (prep-uat land)")
            return ""
        r = _run(
            [
                "gh",
                "pr",
                "create",
                "--repo",
                _gh_repo(repo),
                "--base",
                "dev",
                "--head",
                ftr,
                "--title",
                title,
                "--body-file",
                body_path,
            ]
        )
        url = r.stdout.strip()
        print(f"PR created {url}")
        m = re.search(r"/pull/(\d+)", url)
        return m.group(1) if m else ""
    finally:
        Path(body_path).unlink(missing_ok=True)


def _merge_pr(repo: Path, ftr: str) -> None:
    existing = _existing_pr(repo, ftr)
    if not existing:
        print("no PR to merge (skipped)")
        return
    if existing.get("state") == "MERGED":
        print(f"PR #{existing['number']} already merged")
        return
    num = existing["number"]
    r = _run(
        [
            "gh",
            "pr",
            "merge",
            str(num),
            "--repo",
            _gh_repo(repo),
            "--merge",
            "--delete-branch=false",
        ],
        check=False,
    )
    if r.returncode != 0:
        # dev may already contain ftr after prep-uat / merge-parent — close if merged locally
        err = (r.stderr or r.stdout or "").lower()
        if "already" in err or "not mergeable" in err:
            _run(
                ["gh", "pr", "close", str(num), "--repo", _gh_repo(repo), "--comment", "Closed — landed on dev via finish-up."],
                check=False,
            )
            print(f"PR #{num} closed (already on dev)")
            return
        print(r.stderr or r.stdout, file=sys.stderr)
        sys.exit(1)
    print(f"PR #{num} merged")


def main() -> None:
    ap = argparse.ArgumentParser(description="GitHub PR ftr/* → dev with Linear epic summary")
    ap.add_argument("--repo", default=os.environ.get("ASTRAL_MAIN", "/Users/susan/chuckles/astral"))
    ap.add_argument("--parent-id", required=True, help="e.g. AST-539")
    ap.add_argument("--ftr", default="", help="ftr branch path e.g. ftr/ast-539-slug")
    ap.add_argument("--create", action="store_true", help="Create or update PR body")
    ap.add_argument("--merge", action="store_true", help="Merge open PR after land")
    args = ap.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    token = _token()
    allow_missing = bool(args.merge and not args.create)
    ftr = _resolve_ftr(repo, args.parent_id, args.ftr or None, allow_missing=allow_missing)
    issue = _fetch_epic(token, args.parent_id)
    title = _pr_title(issue)
    body = _pr_body(issue, ftr)

    if args.create:
        _create_or_update_pr(repo, ftr, title, body)
    if args.merge:
        _merge_pr(repo, ftr)
    if not args.create and not args.merge:
        ap.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
