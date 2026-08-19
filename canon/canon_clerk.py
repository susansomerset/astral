#!/usr/bin/env python3
"""Serve the canon corpus to pipeline agents.

Two commands:

  index   Roster of every directive: id, kind, domain, status, and the
          human-readable point (first line of the body). Cheap enough to
          load on every pass — used by Chuckles/Joan/Radia to select.

  expand  Full content for a curated list of ids, as one JSON object, so a
          caller reads N directives in one call instead of N. Fed to the
          implementing engineer in the issue thread and to Radia at review.

The corpus is the directory tree this file sits in. No third-party
dependencies are required, so the script travels with the corpus when it is
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
CANON_ROOT = Path(os.environ.get("CANON_ROOT", Path(__file__).resolve().parent))

# Files that live in the corpus tree but are not directives.
HARNESS_NAMES = {"README.md", "SCHEMA.md", "AUTHORING.md", "HARVEST.md"}

# Subtree -> kind. Kind is structural today; it moves to frontmatter when the
# corpus flattens.
KIND_BY_SUBTREE = {
    # current layout
    "statutes": "statute", "patterns": "pattern",
    # proposed flat layout (canon-v2)
    "statute": "statute", "pattern": "pattern", "orchestrate": "orchestration",
}

# The two kinds carry different status enums: statutes are active|retired,
# patterns are proposed|approved|retired. These are the values a consumer is
# meant to load — a proposed pattern is not citable until Archie approves it.
LIVE_STATUS_BY_KIND = {"statute": "active", "pattern": "approved",
                       "orchestration": "active"}


def load_corpus(include_all: bool = False) -> list[dict]:
    """Every directive in the corpus, sorted by id.

    Defaults to the live set only — active statutes and approved patterns.
    """
    directives = []
    for subtree, kind in KIND_BY_SUBTREE.items():
        root = CANON_ROOT / subtree
        if not root.is_dir():
            continue
        for path in root.rglob("*.md"):
            if path.name in HARNESS_NAMES:
                continue
            directives.append(_read_directive(path, kind))
    if not include_all:
        directives = [d for d in directives if _is_live(d)]
    return sorted(directives, key=lambda d: d["id"])


def _is_live(directive: dict) -> bool:
    return directive["status"] == LIVE_STATUS_BY_KIND.get(directive["kind"])


def build_index(include_all: bool = False) -> dict:
    """Roster without body content."""
    fields = ("id", "kind", "namespace", "domain", "tier", "status", "point", "path")
    return {
        **_corpus_version(),
        "directives": [
            {k: d[k] for k in fields} for d in load_corpus(include_all)
        ],
    }


def build_expansion(ids: list[str], include_all: bool = False) -> dict:
    """Full content for a curated id list. Raises on anything unresolvable."""
    by_id = {d["id"]: d for d in load_corpus(include_all=True)}

    unknown = [i for i in ids if i not in by_id]
    if unknown:
        raise LookupError(f"unknown directive id(s): {', '.join(sorted(unknown))}")

    if not include_all:
        not_live = [i for i in ids if not _is_live(by_id[i])]
        if not_live:
            detail = ", ".join(f"{i} ({by_id[i]['status']})" for i in sorted(not_live))
            raise LookupError(
                f"directive id(s) not in the live set: {detail} "
                "(pass --allow-any to read anyway)"
            )

    selected = [by_id[i] for i in ids]
    payload = {**_corpus_version(), "requested": ids, "resolved": len(selected)}
    payload["directives"] = selected
    payload["size"] = _size_report(selected)
    return payload


def full_text(ids: list[str] | None = None, kind: str | None = None,
              include_all: bool = False) -> dict:
    """Fat bodies for a curated selection — the call agents make.

    Pass explicit `ids` (the usual case: the issue's rubric list), or `kind`
    to take a whole class at once (`full_text(kind="pattern")`). Raises
    LookupError on any id that is unknown or not in the live set, so a stale
    rubric fails loudly instead of silently serving less than it claims.
    """
    if ids is None:
        if kind is None:
            raise ValueError("full_text needs ids or kind")
        ids = [d["id"] for d in load_corpus(include_all) if d["kind"] == kind]
    elif kind is not None:
        by_id = {d["id"]: d for d in load_corpus(include_all=True)}
        ids = [i for i in ids if by_id.get(i, {}).get("kind") == kind]
    return build_expansion(ids, include_all=include_all)


def verify_refs(include_all: bool = False) -> dict:
    """Check every `canonical_refs` entry resolves to real code.

    A directive that names a renamed function is the way canon rots, and it is
    the one part of "is this accurate?" that does not need an opinion. Returns
    one row per broken ref.
    """
    repo_root = CANON_ROOT.parent
    broken = []
    checked = 0
    for directive in load_corpus(include_all):
        for ref in directive["frontmatter"].get("canonical_refs") or []:
            if not isinstance(ref, dict):
                continue
            checked += 1
            path, symbol = ref.get("path"), ref.get("symbol")
            target = repo_root / str(path)
            if not target.is_file():
                reason = "path not found"
            elif not symbol:
                reason = None
            else:
                reason = _symbol_missing(target, str(symbol))
            if reason:
                broken.append({"id": directive["id"], "path": path,
                               "symbol": symbol, "reason": reason})
    return {**_corpus_version(), "refs_checked": checked, "broken": broken}


def _symbol_missing(target: Path, symbol: str) -> str | None:
    """None when the symbol resolves, else the reason it does not.

    Prose targets cite sections (`§2.4`); code targets cite identifiers. A
    section resolves against a numbered heading, not a raw substring.
    """
    text = target.read_text(encoding="utf-8", errors="ignore")
    section = symbol.lstrip("§ ").rstrip(".")
    if target.suffix == ".md" and section and section[0].isdigit():
        wanted = f"{section} "
        if any(line.lstrip("# ").startswith(wanted)
               for line in text.splitlines() if line.startswith("#")):
            return None
        return "section heading not found"
    return None if symbol in text else "symbol not found in file"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="roster of directives, no body content")
    p_index.add_argument("--json", action="store_true", help="JSON instead of text")
    p_index.add_argument("--kind", choices=sorted(set(KIND_BY_SUBTREE.values())))
    p_index.add_argument("--namespace", help="filter by id namespace, e.g. astral, orch")
    p_index.add_argument("--all", action="store_true",
                         help="include retired and unapproved")

    p_verify = sub.add_parser("verify", help="check canonical_refs resolve to real code")
    p_verify.add_argument("--all", action="store_true", help="include retired and unapproved")

    p_expand = sub.add_parser("expand", help="full content for a curated id list")
    p_expand.add_argument("ids", nargs="*", help="directive ids; omit to read stdin")
    p_expand.add_argument("--ids-file", type=Path, help="file with one id per line")
    p_expand.add_argument("--allow-any", action="store_true",
                          help="permit retired or unapproved ids")

    args = parser.parse_args(argv)

    if args.command == "index":
        return _run_index(args)
    if args.command == "verify":
        return _run_verify(args)
    return _run_expand(args)


def _run_index(args) -> int:
    index = build_index(include_all=args.all)
    rows = index["directives"]
    if args.kind:
        rows = [r for r in rows if r["kind"] == args.kind]
    if args.namespace:
        rows = [r for r in rows if r["namespace"] == args.namespace]
    index["directives"] = rows
    index["count"] = len(rows)

    if args.json:
        print(json.dumps(index, indent=2))
        return 0

    print(f"# canon index — {len(rows)} directives @ {index['corpus_sha'][:10]}"
          f"{' (DIRTY)' if index['corpus_dirty'] else ''}")
    for row in rows:
        print(f"\n{row['id']}  [{row['kind']}/{row['status']}]\n    {row['point']}")
    return 0


def _run_verify(args) -> int:
    report = verify_refs(include_all=args.all)
    print(json.dumps(report, indent=2))
    return 1 if report["broken"] else 0


def _run_expand(args) -> int:
    ids = _collect_ids(args)
    if not ids:
        print("expand: no ids given", file=sys.stderr)
        return 2
    try:
        payload = build_expansion(ids, include_all=args.allow_any)
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
    namespace, _, remainder = directive_id.partition(".")
    domain = remainder.partition(".")[0]
    # Frontmatter wins where the new anatomy states these explicitly; the
    # structural derivation is the fallback for the pre-v2 corpus.
    return {
        "id": directive_id,
        "kind": frontmatter.get("kind") or kind,
        "namespace": namespace,
        "domain": frontmatter.get("scope") or domain,
        "tier": frontmatter.get("tier"),
        "status": frontmatter.get("status", "active"),
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
