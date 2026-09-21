#!/usr/bin/env python3
"""Serve the canon corpus to pipeline agents.

Run with --help for the current commands; this docstring deliberately does not
list them, so it cannot go stale.

Directives in force live in directives/active; drafts and archived directives
sit beside it and are never served. Status is a location, not a field.

No third-party dependencies, so the script travels with the corpus when it is
copied into another repo.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Overridable so the clerk can be pointed at a migration tree (canon-v2) without
# being copied into it.
CANON_ROOT = Path(os.environ.get("CANON_ROOT",
                                 Path(__file__).resolve().parent)).resolve()

# Directives in force. Drafts and archived directives sit beside this directory
# and are never served: status is where a file lives, not a field inside it.
ACTIVE_DIR = CANON_ROOT / "directives" / "active"

# Filename prefix -> kind. The prefix is the first segment of the id.
KIND_BY_PREFIX = {"stat": "statute", "patt": "pattern", "orch": "orchestration"}

# Prepended to every expansion. Exception handling is identical for every
# directive, so it lives here once rather than in each file; rule-specific
# guidance belongs in that directive's `# Resolution` section.
PREAMBLE_FILE = CANON_ROOT / "instruction_preamble.md"





def load_corpus() -> list[dict]:
    """Every directive in force, sorted by id.

    Everything in directives/active is served. Kind comes from the filename
    prefix, so a directive's class is visible in a directory listing.
    """
    directives = []
    for path in sorted(ACTIVE_DIR.glob("*.md")):
        kind = KIND_BY_PREFIX.get(path.stem.split(".", 1)[0])
        if kind is None:
            continue
        directives.append(_read_directive(path, kind))
    return sorted(directives, key=lambda d: d["id"])


def usage_text() -> str:
    """The instruction preamble. Absent means the corpus is incomplete."""
    if not PREAMBLE_FILE.is_file():
        raise FileNotFoundError(f"missing instruction preamble: {PREAMBLE_FILE}")
    return PREAMBLE_FILE.read_text(encoding="utf-8")


def build_index() -> dict:
    """Roster without body content."""
    fields = ("id", "kind", "scope", "point", "path")
    return {
        **_corpus_version(),
        "directives": [{k: d[k] for k in fields} for d in load_corpus()],
    }


def build_expansion(ids: list[str]) -> dict:
    """Full content for a curated id list. Raises on anything unresolvable.

    An id that does not resolve is either a typo or a directive that has been
    moved out of the tree — both are failures, not omissions.
    """
    by_id = {d["id"]: d for d in load_corpus()}

    unknown = [i for i in ids if i not in by_id]
    if unknown:
        raise LookupError(f"unknown directive id(s): {', '.join(sorted(unknown))}")

    selected = [by_id[i] for i in ids]
    payload = {"usage": usage_text(), **_corpus_version(),
               "requested": ids, "resolved": len(selected)}
    payload["directives"] = selected
    payload["size"] = _size_report(selected)
    return payload


def full_text(ids: list[str] | None = None, kind: str | None = None) -> dict:
    """Fat bodies for a curated selection — the call agents make.

    Pass explicit `ids` (the usual case: the issue's rubric list), or `kind`
    to take a whole class at once (`full_text(kind="pattern")`). Raises
    LookupError on any id that does not resolve, so a stale rubric fails loudly
    instead of silently serving less than it claims.
    """
    if ids is None:
        if kind is None:
            raise ValueError("full_text needs ids or kind")
        ids = [d["id"] for d in load_corpus() if d["kind"] == kind]
    elif kind is not None:
        by_id = {d["id"]: d for d in load_corpus()}
        ids = [i for i in ids if by_id.get(i, {}).get("kind") == kind]
    return build_expansion(ids)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="roster of directives, no body content")
    p_index.add_argument("--json", action="store_true", help="JSON instead of text")
    p_index.add_argument("--kind", choices=sorted(set(KIND_BY_PREFIX.values())))
    p_index.add_argument("--scope", help="filter by scope, e.g. functions, errors")

    p_expand = sub.add_parser("expand", help="full content for a curated id list")
    p_expand.add_argument("ids", nargs="*", help="directive ids; omit to read stdin")
    p_expand.add_argument("--ids-file", type=Path, help="file with one id per line")

    args = parser.parse_args(argv)

    if args.command == "index":
        return _run_index(args)
    return _run_expand(args)


def _run_index(args) -> int:
    index = build_index()
    rows = index["directives"]
    if args.kind:
        rows = [r for r in rows if r["kind"] == args.kind]
    if args.scope:
        rows = [r for r in rows if r["scope"] == args.scope]
    index["directives"] = rows
    index["count"] = len(rows)

    if args.json:
        print(json.dumps(index, indent=2))
        return 0

    print(f"# canon index — {len(rows)} directives @ {index['corpus_sha'][:10]}"
          f"{' (DIRTY)' if index['corpus_dirty'] else ''}")
    for row in rows:
        print(f"\n{row['id']}  [{row['kind']}]\n    {row['point']}")
    return 0


def _run_expand(args) -> int:
    ids = _collect_ids(args)
    if not ids:
        print("expand: no ids given", file=sys.stderr)
        return 2
    try:
        payload = build_expansion(ids)
    except LookupError as exc:
        print(f"expand: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(payload, indent=2))
    return 0


def _collect_ids(args) -> list[str]:
    ids = list(args.ids)
    if args.ids_file:
        ids += args.ids_file.read_text().split()
    if not ids and not sys.stdin.isatty():
        ids += sys.stdin.read().split()
    seen, ordered = set(), []
    for i in ids:
        if i not in seen:
            seen.add(i)
            ordered.append(i)
    return ordered


def _read_directive(path: Path, kind: str) -> dict:
    text = path.read_text(encoding="utf-8")
    frontmatter, body = _split_frontmatter(text)
    directive_id = frontmatter.get("id") or path.stem
    derived_scope = directive_id.partition(".")[2].partition(".")[0]
    # Frontmatter wins where the new anatomy states these explicitly; the
    # structural derivation is the fallback for the pre-v2 corpus.
    return {
        "id": directive_id,
        "kind": frontmatter.get("kind") or kind,
        "scope": frontmatter.get("scope") or derived_scope,
        "point": frontmatter.get("point") or _first_body_line(body),
        "path": str(path.relative_to(CANON_ROOT.parent)),
        "frontmatter": frontmatter,
        "body": body.strip(),
    }


def _split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    _, _, remainder = text.partition("---\n")
    raw, _, body = remainder.partition("\n---")
    return _parse_frontmatter(raw), body.lstrip("\n")


def _parse_frontmatter(raw: str) -> dict:
    """YAML when available; otherwise a parser for the schema's flat shapes."""
    try:
        import yaml
    except ImportError:
        return _parse_frontmatter_fallback(raw)
    try:
        return yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        return _parse_frontmatter_fallback(raw)


def _parse_frontmatter_fallback(raw: str) -> dict:
    """Covers the shapes both schemas use: scalars, inline and dashed lists,
    one nested mapping (`applies_when`), and a list of mappings
    (`canonical_refs`). Anything deeper needs PyYAML.
    """
    parsed: dict = {}
    top_key = None      # the open top-level key
    nested_key = None   # the open key inside a nested mapping, if any
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        stripped = line.strip()

        if line[0] not in " \t":
            key, sep, value = stripped.partition(":")
            if not sep:
                continue
            top_key, nested_key = key.strip(), None
            parsed[top_key] = _scalar(value) if value.strip() else None
            continue

        if top_key is None:
            continue

        if stripped.startswith("- "):
            owner, owner_key = ((parsed[top_key], nested_key) if nested_key
                                else (parsed, top_key))
            if not isinstance(owner, dict):
                continue
            if owner.get(owner_key) is None:
                owner[owner_key] = []
            sequence = owner[owner_key]
            if not isinstance(sequence, list):
                continue
            item = stripped[2:].strip()
            key, sep, value = item.partition(":")
            sequence.append({key.strip(): _scalar(value)} if sep else _scalar(item))
            continue

        key, sep, value = stripped.partition(":")
        if not sep:
            continue
        key = key.strip()
        container = parsed[top_key]

        if isinstance(container, list) and container and isinstance(container[-1], dict):
            container[-1][key] = _scalar(value)
            continue

        if not isinstance(container, dict):
            container = parsed[top_key] = {}
        container[key] = _scalar(value) if value.strip() else None
        nested_key = None if value.strip() else key
    return parsed


def _scalar(value: str):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [_scalar(v) for v in inner.split(",")] if inner else []
    if value in {"null", "~", ""}:
        return None
    if value in {"true", "false"}:
        return value == "true"
    return value.strip("\"'")


def _first_body_line(body: str) -> str:
    """The point of the directive: first prose line under its opening heading."""
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("# "):
            for candidate in lines[index + 1:]:
                if candidate.strip():
                    return candidate.strip()
            break
    return ""


def _corpus_version() -> dict:
    return {"corpus_sha": _git(["log", "-1", "--format=%H", "--", str(CANON_ROOT)])
            or "unknown",
            "corpus_dirty": bool(_git(["status", "--porcelain", str(CANON_ROOT)]))}


def _git(args: list[str]) -> str:
    try:
        result = subprocess.run(["git", "-C", str(CANON_ROOT), *args],
                                capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def _size_report(directives: list[dict]) -> dict:
    chars = sum(len(d["body"]) for d in directives)
    return {"chars": chars, "approx_tokens": chars // 4}


if __name__ == "__main__":
    sys.exit(main())
