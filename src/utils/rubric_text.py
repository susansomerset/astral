# -*- coding: utf-8 -*-
"""Pure helpers for consult rubric text: trailing grade table parse + validation (AST-351).

Grade lines at end of ``content``: ``{grade}{sep}{description}`` where sep is
whitespace, optional ``=``, ``==``, or ``:``, optional whitespace. At least two
consecutive lines from the bottom must match.
"""

import re
from typing import Dict, List

# A–F and X; case-insensitive on input, normalized to uppercase in output.
# Prefer == before = so "A == text" does not split on a single '='.
_GRADE_LINE = re.compile(r"^([ABCDEFX])\s*(?:==|=|:)\s*(.+)$", re.IGNORECASE)


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
    if len(block) < 2:
        raise ValueError(
            "rubric text must end with at least two lines of the form "
            "'A = description' / 'B: text' / 'C == text' (one grade letter per line)"
        )
    out: List[Dict[str, str]] = []
    for ln in block:
        m = _GRADE_LINE.match(ln.strip())
        if not m:
            raise ValueError(f"invalid grade line in trailing block: {ln!r}")
        out.append({"grade": m.group(1).upper(), "description": m.group(2).strip()})
    return out


def ensure_criterion_grade_table(item: dict) -> None:
    """Parse ``item['content']`` and set ``item['grade_descriptions']``. Mutates ``item``."""
    rows = parse_trailing_grade_table_lines(item.get("content") or "")
    item["grade_descriptions"] = rows
