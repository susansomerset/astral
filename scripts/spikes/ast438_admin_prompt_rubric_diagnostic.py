#!/usr/bin/env python3
"""AST-438: read-only local vs prod admin prompts + optional rubric validation.

Usage (repo root):
  python3 scripts/spikes/ast438_admin_prompt_rubric_diagnostic.py [--prompt-only]
  python3 scripts/spikes/ast438_admin_prompt_rubric_diagnostic.py --candidates somerset
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sqlite3
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.core.candidate import normalize_rubric_artifacts_on_save
from src.data import database
from src.utils import rubric_text
from src.utils.config import (
    ASTRAL_CONFIG,
    RUBRIC_CRITERIA_ARTIFACT_KEYS,
    TASK_CONFIG,
)

AST438_TASK_KEYS = frozenset({
    "qualify_job_listings", "evaluate_jd", "grade_do", "grade_get", "grade_like",
    "craft_prefilter_rubric", "craft_joblist_rubric", "craft_jobdesc_rubric",
    "craft_get_rubric", "craft_do_rubric", "craft_like_rubric",
})

TASK_FIELDS = ("agent_id", "user_prompt", "cache_prompt", "nocache_prompt", "system_prompt", "run_next")
AGENT_FIELDS = ("content", "model_code", "temperature", "max_tokens")

# artifact_key -> TASK_CONFIG keys that consume it (rubric_artifact on that row)
_ARTIFACT_CONSUMERS: dict[str, list[str]] = defaultdict(list)
for _tk, _cfg in TASK_CONFIG.items():
    _ra = _cfg.get("rubric_artifact")
    if _ra:
        _ARTIFACT_CONSUMERS[_ra].append(_tk)


def _load_prod_url() -> str:
    if not os.environ.get("ASTRAL_PROD_URL"):
        env_file = _ROOT / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line.startswith("ASTRAL_PROD_URL="):
                    os.environ["ASTRAL_PROD_URL"] = line.split("=", 1)[1].strip()
                    break
    return (os.environ.get("ASTRAL_PROD_URL") or "").rstrip("/")


def _prod_get(path: str, timeout: int = 180) -> dict:
    url = f"{_load_prod_url()}{path}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:800]
        raise RuntimeError(f"HTTP {e.code} from {url}: {body or e.reason}") from e


def _rows_to_dicts(columns: list[str], rows: list[list]) -> list[dict[str, Any]]:
    return [dict(zip(columns, row)) for row in rows]


def _is_current(row: dict[str, Any]) -> bool:
    c = row.get("current")
    return c == 1 or c is True or str(c) == "1"


def fetch_prod_table(table: str) -> dict:
    return _prod_get(f"/api/admin/data/table/{table}")


def fetch_local_table(conn: sqlite3.Connection, table: str) -> dict:
    columns = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    rows = [list(r) for r in conn.execute(f"SELECT * FROM {table}").fetchall()]
    return {"columns": columns, "rows": rows}


def _norm(val: Any) -> str:
    if val is None:
        return ""
    return str(val)


def _classify(local: str, prod: str) -> str:
    if local == prod:
        return "IDENTICAL"
    if local.strip() == prod.strip() and local != prod:
        return "WHITESPACE_ONLY"
    if not local and prod:
        return "LOCAL_MISSING"
    if local and not prod:
        return "PROD_MISSING"
    return "CONTENT_DIFF"


def _filter_tasks(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        tk = row.get("task_key")
        if tk in AST438_TASK_KEYS and _is_current(row):
            out[str(tk)] = row
    return out


def _agent_ids_from_tasks(tasks: dict[str, dict[str, Any]]) -> set[str]:
    return {str(t["agent_id"]).strip() for t in tasks.values() if (t.get("agent_id") or "").strip()}


def _filter_agents(rows: list[dict[str, Any]], agent_ids: set[str]) -> dict[str, dict[str, Any]]:
    return {str(r["agent_id"]): r for r in rows if str(r.get("agent_id")) in agent_ids}


def snapshot_tables(out_dir: Path, skip_prod: bool) -> tuple[dict, dict, dict, dict]:
    local_db = ASTRAL_CONFIG["db_dir"] / "astral.db"
    conn = sqlite3.connect(str(local_db))
    try:
        local_at = fetch_local_table(conn, "agent_task")
        local_ag = fetch_local_table(conn, "agent")
    finally:
        conn.close()

    if skip_prod:
        prod_at, prod_ag = {"columns": [], "rows": []}, {"columns": [], "rows": []}
    else:
        prod_url = _load_prod_url()
        if not prod_url:
            raise RuntimeError("ASTRAL_PROD_URL unset — use .env or --skip-prod")
        prod_at = fetch_prod_table("agent_task")
        prod_ag = fetch_prod_table("agent")

    if prod_at["columns"] != local_at["columns"]:
        (out_dir / "schema_mismatch_agent_task.json").write_text(
            json.dumps({"prod": prod_at["columns"], "local": local_at["columns"]}, indent=2)
        )
        raise RuntimeError("agent_task schema mismatch — see schema_mismatch_agent_task.json")

    if prod_ag["columns"] != local_ag["columns"]:
        (out_dir / "schema_mismatch_agent.json").write_text(
            json.dumps({"prod": prod_ag["columns"], "local": local_ag["columns"]}, indent=2)
        )
        raise RuntimeError("agent schema mismatch — see schema_mismatch_agent.json")

    local_tasks = _filter_tasks(_rows_to_dicts(local_at["columns"], local_at["rows"]))
    prod_tasks = _filter_tasks(_rows_to_dicts(prod_at["columns"], prod_at["rows"])) if not skip_prod else {}
    aids = _agent_ids_from_tasks(local_tasks | prod_tasks)
    local_agents = _filter_agents(_rows_to_dicts(local_ag["columns"], local_ag["rows"]), aids)
    prod_agents = _filter_agents(_rows_to_dicts(prod_ag["columns"], prod_ag["rows"]), aids) if not skip_prod else {}

    out_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in (
        ("local_agent_task_ast438.json", local_tasks),
        ("prod_agent_task_ast438.json", prod_tasks),
        ("local_agent_ast438.json", local_agents),
        ("prod_agent_ast438.json", prod_agents),
    ):
        (out_dir / name).write_text(json.dumps(payload, indent=2, default=str))

    print(f"agent_task filtered: local={len(local_tasks)} prod={len(prod_tasks)}")
    print(f"agent filtered: local={len(local_agents)} prod={len(prod_agents)}")
    return local_tasks, prod_tasks, local_agents, prod_agents


def write_prompt_diff_md(
    docs_dir: Path,
    local_tasks: dict,
    prod_tasks: dict,
    local_agents: dict,
    prod_agents: dict,
) -> Path:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    host = urlparse(_load_prod_url()).netloc or "(prod url unset)"
    all_keys = sorted(AST438_TASK_KEYS)
    task_diffs: list[str] = []
    agent_diffs: list[str] = []

    out_lines = [
        "# AST-438 — Prompt diff (local vs production)",
        f"Generated: {now}",
        f"Prod: {host}",
        "",
    ]
    for tk in all_keys:
        loc = local_tasks.get(tk)
        pro = prod_tasks.get(tk)
        out_lines.append(f"### {tk}")
        out_lines.append("")
        if not loc and not pro:
            out_lines.append("_No current row in either environment._")
            out_lines.append("")
            continue
        if not loc:
            out_lines.append("- **Row:** `PROD_ONLY`")
            task_diffs.append(tk)
        elif not pro:
            out_lines.append("- **Row:** `LOCAL_ONLY`")
            task_diffs.append(tk)
        else:
            any_diff = False
            for field in TASK_FIELDS:
                cls = _classify(_norm(loc.get(field)), _norm(pro.get(field)))
                if cls != "IDENTICAL":
                    any_diff = True
                    out_lines.append(f"- `{field}`: **{cls}**")
            if any_diff:
                task_diffs.append(tk)
                if tk.startswith("craft_"):
                    out_lines.append("- **Craft rubric admin task:** factual diff only — Susan review before any sync.")
        out_lines.append("")

    out_lines.extend(["## Per-agent diffs", ""])
    for aid in sorted(set(local_agents) | set(prod_agents)):
        loc = local_agents.get(aid)
        pro = prod_agents.get(aid)
        out_lines.append(f"### {aid}")
        out_lines.append("")
        if not loc:
            out_lines.append("- **Row:** `PROD_ONLY`")
            agent_diffs.append(aid)
        elif not pro:
            out_lines.append("- **Row:** `LOCAL_ONLY`")
            agent_diffs.append(aid)
        else:
            for field in AGENT_FIELDS:
                cls = _classify(_norm(loc.get(field)), _norm(pro.get(field)))
                if cls != "IDENTICAL":
                    out_lines.append(f"- `{field}`: **{cls}**")
                    if aid not in agent_diffs:
                        agent_diffs.append(aid)
        out_lines.append("")

    summary = [
        "## Executive summary",
        f"- Tasks compared: {len(all_keys)}",
        f"- Agent tasks with any diff: {', '.join(task_diffs) or '(none)'}",
        f"- Agents with any diff: {', '.join(agent_diffs) or '(none)'}",
        "",
        "## Per-task diffs",
        "",
    ]
    out_lines = out_lines[:3] + summary + out_lines[3:]

    out_lines.extend([
        "## Follow-ups (out of scope)",
        "- **AST-373** — prompt export/import UI (future sync decision).",
        "- **AST-381** — repo-tracked DB snapshots (longer-term alignment).",
        "",
    ])
    path = docs_dir / "ast-438-prompt-diff-local-vs-production.md"
    path.write_text("\n".join(out_lines))
    return path


def _validate_criterion(artifact_key: str, idx: int, item: dict, ci: dict) -> list[str]:
    issues: list[str] = []
    label = (item.get("label") or item.get("code") or "").strip() or f"#{idx + 1}"
    if not (item.get("label") or "").strip():
        issues.append("missing or empty label")
    if not (item.get("content") or "").strip():
        issues.append("missing or empty content")
    try:
        rubric_text.ensure_criterion_grade_table(item)
        n = len(item.get("grade_descriptions") or [])
        if n < 2:
            issues.append(f"grade_descriptions has {n} rows (expected >=2)")
    except ValueError as e:
        issues.append(f"grade table: {e}")
    imp = item.get("importance")
    try:
        lo, hi = int(ci["min"]), int(ci["max"])
        if imp is None:
            issues.append("importance missing (defaults to 5 on save)")
        elif not isinstance(imp, int) or isinstance(imp, bool) or not (lo <= imp <= hi):
            issues.append(f"importance {imp!r} outside {lo}-{hi}")
    except (KeyError, TypeError):
        issues.append("importance bounds check failed")
    code = (item.get("code") or "").strip()
    if not code:
        issues.append("WARN: code missing")
    return issues


def write_rubric_validation_md(docs_dir: Path, candidate_ids: list[str]) -> Path | None:
    if not candidate_ids:
        return None
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ci = ASTRAL_CONFIG["consult_importance"]
    lines = ["# AST-438 — Rubric validation", f"Generated: {now}", ""]

    for cid in candidate_ids:
        cand = database.get_candidate(cid)
        if not cand:
            lines.extend([f"## Candidate: {cid}", "", f"_Not found: {cid}_", ""])
            continue
        cd = cand.get("candidate_data") or {}
        arts = cd.get("artifacts") or {}
        lines.extend([f"## Candidate: {cid}", ""])

        # normalize copy check
        try:
            arts_copy = copy.deepcopy(arts)
            normalize_rubric_artifacts_on_save(arts_copy)
        except ValueError as e:
            lines.append(f"- **normalize_rubric_artifacts_on_save:** FAIL — {e}")
        lines.append("")
        lines.append("### Summary")
        lines.append("| Artifact key | Criteria | Issues |")
        lines.append("|--------------|----------|--------|")

        codes_seen: dict[str, set[str]] = defaultdict(set)
        findings: list[str] = []

        for key in sorted(RUBRIC_CRITERIA_ARTIFACT_KEYS):
            val = arts.get(key)
            if val is None:
                lines.append(f"| `{key}` | 0 | (absent) |")
                continue
            if not isinstance(val, list):
                lines.append(f"| `{key}` | — | not a list |")
                continue
            issue_count = 0
            for idx, item in enumerate(val):
                if not isinstance(item, dict):
                    findings.append(f"### {key}\n- Criterion {idx + 1}: not an object\n")
                    issue_count += 1
                    continue
                for iss in _validate_criterion(key, idx, item, ci):
                    if iss.startswith("WARN:"):
                        findings.append(f"### {key}\n- Vector \"{item.get('label', idx)}\": {iss}\n")
                    else:
                        issue_count += 1
                        findings.append(
                            f"### {key}\n- Vector \"{(item.get('label') or '').strip() or f'#{idx+1}'}\" "
                            f"(code={item.get('code')!r}): {iss}\n"
                        )
                code = (item.get("code") or "").strip()
                if code:
                    if code in codes_seen[key]:
                        issue_count += 1
                        findings.append(f"### {key}\n- Duplicate code `{code}`\n")
                    codes_seen[key].add(code)

            lines.append(f"| `{key}` | {len(val)} | {issue_count} |")

        lines.append("")
        lines.append("### Consult mapping")
        lines.append("| Artifact key | TASK_CONFIG consumers |")
        lines.append("|--------------|-------------------------|")
        for key in sorted(RUBRIC_CRITERIA_ARTIFACT_KEYS):
            consumers = _ARTIFACT_CONSUMERS.get(key, [])
            lines.append(f"| `{key}` | {', '.join(consumers) or '—'} |")

        lines.append("")
        lines.append("### Admin-task schema (TASK_CONFIG)")
        for tk in sorted(k for k in AST438_TASK_KEYS if k.startswith("craft_")):
            schema = TASK_CONFIG.get(tk, {}).get("response_schema", {})
            lines.append(f"- `{tk}`: expects `criteria[].label` + `criteria[].content` in TASK_CONFIG; "
                         "live rows also use `code`, `importance`, `grade_descriptions` per CANDIDATE_DATA_MODEL.")

        lines.append("")
        lines.append("### Findings")
        lines.append("")
        if findings:
            lines.extend(findings)
        else:
            lines.append("_No validation failures._")
        lines.append("")
        lines.append("### Root-cause hints")
        lines.append("- **Candidate-data:** issues in table/findings above.")
        lines.append("- **Admin-task / prompt:** compare `ast-438-prompt-diff-local-vs-production.md` for craft_*_rubric tasks.")
        lines.append("")

    path = docs_dir / "ast-438-rubric-validation.md"
    path.write_text("\n".join(lines))
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=_ROOT / "debug/spikes/AST-438")
    parser.add_argument("--docs-dir", type=Path, default=_ROOT / "docs/features/administrator")
    parser.add_argument("--candidates", action="append", default=[], help="astral_candidate_id (repeatable)")
    parser.add_argument("--prompt-only", action="store_true")
    parser.add_argument("--rubrics-only", action="store_true")
    parser.add_argument("--skip-prod", action="store_true")
    args = parser.parse_args()

    if args.rubrics_only:
        if not args.candidates:
            print("ERROR: --rubrics-only requires --candidates", file=sys.stderr)
            sys.exit(1)
        write_rubric_validation_md(args.docs_dir, args.candidates)
        print(f"Wrote {args.docs_dir / 'ast-438-rubric-validation.md'}")
        return

    local_tasks, prod_tasks, local_agents, prod_agents = ({}, {}, {}, {})
    if not args.rubrics_only:
        local_tasks, prod_tasks, local_agents, prod_agents = snapshot_tables(args.out_dir, args.skip_prod)
        p = write_prompt_diff_md(args.docs_dir, local_tasks, prod_tasks, local_agents, prod_agents)
        print(f"Wrote {p}")

    if args.candidates:
        rv = write_rubric_validation_md(args.docs_dir, args.candidates)
        if rv:
            print(f"Wrote {rv}")
    elif not args.prompt_only and not args.rubrics_only:
        print("Stage 4 skipped: no --candidates (Susan must designate astral_candidate_id).")


if __name__ == "__main__":
    main()
