# -*- coding: utf-8 -*-
"""Pure helpers for consult rubric text: trailing grade table parse + validation (AST-351).

Grade lines at end of ``content``: ``{grade}{sep}{description}`` where sep is
whitespace, optional ``=``, ``==``, or ``:``, optional whitespace. At least two
consecutive lines from the bottom must match.
"""

import hashlib
import re
from typing import Dict, List

# A–F and X; case-insensitive on input, normalized to uppercase in output.
# Prefer == before = so "A == text" does not split on a single '='.
_GRADE_LINE = re.compile(r"^([ABCDEFX])\s*(?:==|=|:)\s*(.+)$", re.IGNORECASE)
# Inline form (AST-1434): "A == … B == …" on one physical line.
_GRADE_INLINE = re.compile(r"([ABCDEFX])\s*(?:==|=|:)\s*", re.IGNORECASE)


def _parse_inline_grade_tokens(text: str) -> List[Dict[str, str]]:
    """Split inline ``A == … B == …`` (no newlines) into grade rows. Empty if fewer than two."""
    raw = (text or "").rstrip()
    matches = list(_GRADE_INLINE.finditer(raw))
    if len(matches) < 2:
        return []
    out: List[Dict[str, str]] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        desc = raw[m.end():end].strip()
        if not desc:
            return []
        out.append({"grade": m.group(1).upper(), "description": desc})
    return out if len(out) >= 2 else []


def _content_has_newline_grade_table(content: str) -> bool:
    lines = (content or "").rstrip().split("\n")
    if len(lines) < 2:
        return False
    return bool(_GRADE_LINE.match(lines[-1].strip()) and _GRADE_LINE.match(lines[-2].strip()))


def coerce_embedded_newline_escapes(content: str) -> str:
    """If content has few real newlines but contains \\n / \\r\\n escapes, expand them.

    Craft rubric prompts show grade tables as one JSON string with literal ``\\n``
    between grade lines (AST-906). Models often copy that into ``content``; Save
    then sees a single physical line and fails trailing grade-table parse.
    """
    raw = content or ""
    if raw.count("\n") >= 2:
        return raw
    if "\\n" not in raw and "\\r\\n" not in raw:
        return raw
    # Expand \\r\\n before \\n so a single pass does not leave stray \\r.
    return raw.replace("\\r\\n", "\n").replace("\\n", "\n")


def parse_trailing_grade_table_lines(content: str) -> List[Dict[str, str]]:
    """Return ``[{"grade": "A", "description": "..."}, ...]`` for the trailing grade block.

    The block is the maximal suffix of ``content`` consisting only of lines that
    match the grade-line pattern. Raises ``ValueError`` if fewer than two lines.
    """
    raw = (content or "").rstrip()
    if not raw:
        raise ValueError("rubric criterion content is empty")
    lines = raw.split("\n")
    j = len(lines) - 1
    while j >= 0:
        if _GRADE_LINE.match(lines[j].strip()):
            j -= 1
        else:
            break
    block = lines[j + 1 :]
    if len(block) >= 2:
        out: List[Dict[str, str]] = []
        for ln in block:
            m = _GRADE_LINE.match(ln.strip())
            if not m:
                raise ValueError(f"invalid grade line in trailing block: {ln!r}")
            out.append({"grade": m.group(1).upper(), "description": m.group(2).strip()})
        return out
    inline_src = lines[-1] if lines else raw
    inline = _parse_inline_grade_tokens(inline_src)
    if len(inline) < 2:
        inline = _parse_inline_grade_tokens(raw)
    if len(inline) < 2:
        raise ValueError(
            "rubric text must end with at least two lines of the form "
            "'A = description' / 'B: text' / 'C == text' (one grade letter per line)"
        )
    return inline


def rubric_vector_content_fingerprint(label: str, content: str) -> str:
    """Normalized label+content identity for rubric_vector versioning (AST-378)."""
    combined = f"{label or ''}{content or ''}"
    normalized = re.sub(r"[^a-z0-9]", "", combined.lower())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def ensure_criterion_grade_table(item: dict) -> None:
    """Parse ``item['content']`` and set ``item['grade_descriptions']``. Mutates ``item``."""
    original = item.get("content") or ""
    content = coerce_embedded_newline_escapes(original)
    rows = parse_trailing_grade_table_lines(content)
    item["grade_descriptions"] = rows
    if not _content_has_newline_grade_table(content):
        m = _GRADE_INLINE.search(content)
        preamble = content[:m.start()].rstrip() if m else ""
        grade_block = "\n".join(f"{r['grade']} == {r['description']}" for r in rows)
        item["content"] = f"{preamble}\n{grade_block}".strip() if preamble else grade_block
    elif content != original:
        item["content"] = content
