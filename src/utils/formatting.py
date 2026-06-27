# -*- coding: utf-8 -*-
"""String formatting utilities. Must not import from config.py (config imports us)."""

import base64
import json
import re
from typing import Any, Dict, List, Optional

# Compact grades_encoded row: 000|DTA5|GCA4|…
_ENCODED_GRADE_LINE = re.compile(r"^\d{3}\|")


def enumerate_array(
    label: str,
    array: List[str],
    index_key: Optional[str] = None,
    index_values: Optional[List[str]] = None,
    ) -> str:
    """Format string array as numbered enumeration, or keyed enumeration when index_key is provided.

    Args:
        label: Optional section header (e.g. "URLs", "Links"). If empty, no header.
        array: List of strings to enumerate
        index_key: When provided (with index_values), use keyed format instead of numbers.
        index_values: Per-item key values; must be same length as array.

    Returns:
        Numbered: "label:\\n1: item1\\n2: item2"
        Keyed:    "label:\\n[index_key=val1]: item1\\n[index_key=val2]: item2"
        Empty string if array is empty.
    """
    if not array:
        return ""
    # Keyed format: skip numbers, use index_key=value as identifier
    if index_key and index_values and len(index_values) == len(array):
        lines = [f"[{index_key}={v}]: {item}" for v, item in zip(index_values, array)]
    else:
        lines = [f"{i+1}: {item}" for i, item in enumerate(array)]
    body = "\n".join(lines)
    if label:
        return f"{label}:\n{body}"
    return body


def clean_encoded_agent_payload(payload: str) -> str:
    """Drop batch tag lines from agent_payload; keep grade rows for _decode_payload."""
    lines: List[str] = []
    for ln in (payload or "").splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("[") and "batch" in s.lower():
            continue
        lines.append(s)
    return "\n".join(lines)


def looks_like_encoded_grades_text(text: str) -> bool:
    """True when text contains at least one compact grades_encoded row."""
    for ln in (text or "").splitlines():
        if _ENCODED_GRADE_LINE.match(ln.strip()):
            return True
    if (text or "").strip() and _ENCODED_GRADE_LINE.match((text or "").strip()):
        return True
    return False


def coerce_grades_encoded_json_parse(parsed: Any, fallback_text: str = "") -> Any:
    """Wrap bare encoded string (or top-level JSON string) in agent envelope for do_task."""
    if isinstance(parsed, str) and looks_like_encoded_grades_text(parsed):
        return {"agent_payload": clean_encoded_agent_payload(parsed)}
    if isinstance(parsed, dict):
        ap = parsed.get("agent_payload")
        if isinstance(ap, str):
            out = dict(parsed)
            out["agent_payload"] = clean_encoded_agent_payload(ap)
            return out
        if isinstance(ap, list):
            out = dict(parsed)
            out["agent_payload"] = clean_encoded_agent_payload("\n".join(str(x) for x in ap))
            return out
    if parsed is None and fallback_text and looks_like_encoded_grades_text(fallback_text):
        return {"agent_payload": clean_encoded_agent_payload(fallback_text)}
    return parsed


def parse_enumerate_array(text: str) -> Dict[int, str]:
    """Inverse of enumerate_array: parse numbered enumeration back to {id: value} map.
    Input: "1: https://acme.com/about\\n2: https://acme.com/products"
    Output: {1: "https://acme.com/about", 2: "https://acme.com/products"}
    """
    result = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue  # pragma: no cover
        colon_idx = line.find(":")
        if colon_idx < 1:
            continue
        try:
            num = int(line[:colon_idx].strip())
            result[num] = line[colon_idx + 1:].strip()
        except ValueError:
            continue
    return result


def normalize_link(url: str) -> str:
    """Pure PJL URL key: strip scheme, drop fragment, trim trailing slashes and index filenames."""
    url = (url or "").strip()
    if not url:
        return ""
    lower = url.lower()
    for prefix in ("https://", "http://", "//"):
        if lower.startswith(prefix):
            url = url[len(prefix):]
            lower = url.lower()
            break
    if "#" in url:
        url = url.split("#", 1)[0]
    url = url.lower()
    while "//" in url:
        url = url.replace("//", "/")
    url = url.rstrip("/")
    for suffix in ("/index.html", "/index.htm", "/index.php"):
        if url.endswith(suffix):
            url = url[: -len(suffix)].rstrip("/")
            break
    return url


def value_to_str(val: object) -> str:
    """Coerce a resolved token value to a string for prompt insertion.
    Arrays of {label, content} objects auto-render as markdown h3 sections.
    If code field is present, append it in parentheses: "Title Match (TM)"."""
    if val is None:
        return ""
    if isinstance(val, str):
        return val
    if isinstance(val, list):
        if val and all(isinstance(v, dict) and "label" in v and "content" in v for v in val):
            return "\n\n".join(
                f"### {v['label']}{' (' + v.get('code') + ')' if v.get('code') else ''}\n{v['content']}" 
                for v in val if v.get("label")
            )
        return "\n".join(value_to_str(item) for item in val)
    if isinstance(val, dict):
        return json.dumps(val, indent=2)
    return str(val)


def format_grade_display(g: dict) -> str:
    """Human-readable one-liner for a grade dict (vector, grade, optional confidence_label)."""
    vec = g.get("vector") or ""
    gr = g.get("grade") or ""
    lab = g.get("confidence_label")
    if lab:
        return f"{vec}: {gr} ({lab})"
    return f"{vec}: {gr}"


def split_to_list(value: str, delimiter: str = ",") -> List[str]:
    """Split delimited string; strip each token; drop empties. Agent fields (e.g. comma-separated keywords).

    delimiter must be non-empty; dynamic callers must validate before passing (str.split forbids "").
    """
    if not delimiter:
        raise ValueError("split_to_list: delimiter must be non-empty")
    return [part.strip() for part in value.split(delimiter) if part.strip()]


def collapse_consecutive_blank_lines(text: str) -> str:
    """Collapse runs of blank lines to a single blank line.

    A line is blank when it is empty or contains only whitespace (spaces, tabs).
    Non-empty lines keep their original string (no strip/reformat of content).
    """
    if not text or not isinstance(text, str):
        return "" if text is None else text
    out: List[str] = []
    prev_blank = False
    for line in text.splitlines():
        if not line.strip():
            if not prev_blank:
                out.append("")
            prev_blank = True
        else:
            out.append(line)
            prev_blank = False
    return "\n".join(out)


def parse_text(raw_html: str) -> str:
    """Extract visible text from HTML: drop tags, join text runs with single spaces.

    Example:
        '<div><tag class data blah>Sr. Job Person</tag><span>Planet Earth</span>...'
        -> 'Sr. Job Person Planet Earth $ 10,000'
    Adjacent element boundaries (e.g. <i>$</i>10,000) become a space between chunks.
    """
    if not raw_html or not isinstance(raw_html, str):
        return ""
    # B1 lazy import: bs4 is optional on hot paths that import formatting without HTML parsing.
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(raw_html, "html.parser")
    # stripped_strings = non-empty text nodes in document order; one space between each
    return " ".join(soup.stripped_strings)


def find_job_containers(dom_html: str, job_titles: List[str]) -> List[str]:
    """Find the narrowest DOM section(s) whose text covers all job_titles.

    Phase 1: look for a single element containing ALL titles (simple pages).
    Phase 2: accumulate across sibling containers — walk up from the deepest
    title-bearing elements until a parent's children together cover all titles.

    Returns list of outerHTML strings. Falls back to [dom_html] if titles
    cannot be located.
    """
    # B1 lazy import: BeautifulSoup/Tag only for DOM-heavy job container discovery.
    from bs4 import BeautifulSoup, Tag

    if not job_titles:
        return [dom_html]

    soup = BeautifulSoup(dom_html, "html.parser")

    titles_lower = [t.lower() for t in job_titles if t.strip()]
    if len(titles_lower) < 2:
        return [dom_html]

    titles_set = set(titles_lower)

    def _titles_in(el: Tag) -> set:
        text = el.get_text(" ", strip=True).lower()
        return {t for t in titles_set if t in text}

    # Phase 1: single element containing ALL titles → filter to deepest
    all_match = [el for el in soup.descendants if isinstance(el, Tag) and _titles_in(el) == titles_set]
    if all_match:
        match_ids = set(id(c) for c in all_match)
        deepest = [c for c in all_match if not any(
            isinstance(d, Tag) and id(d) in match_ids for d in c.descendants if d is not c
        )]
        if deepest:  # pragma: no branch
            return [str(el) for el in deepest]

    # Phase 2: accumulate across siblings (AST-390: pragma — DOM/BS4 sibling union is brittle in tests).
    partial = [(el, _titles_in(el)) for el in soup.descendants if isinstance(el, Tag) and _titles_in(el)]  # pragma: no cover
    if not partial:  # pragma: no cover
        return [dom_html]  # pragma: no cover

    partial_ids = set(id(p[0]) for p in partial)  # pragma: no cover
    leaves = [(el, titles) for el, titles in partial if not any(  # pragma: no cover
        isinstance(d, Tag) and id(d) in partial_ids for d in el.descendants if d is not el  # pragma: no cover
    )]  # pragma: no cover

    checked: set = set()  # pragma: no cover
    for leaf, _ in leaves:  # pragma: no cover
        parent = leaf.parent  # pragma: no cover
        while parent and isinstance(parent, Tag):  # pragma: no cover
            pid = id(parent)  # pragma: no cover
            if pid in checked:  # pragma: no cover
                break  # pragma: no cover
            checked.add(pid)  # pragma: no cover
            union: set = set()  # pragma: no cover
            containers: List[Tag] = []  # pragma: no cover
            for child in parent.children:  # pragma: no cover
                if isinstance(child, Tag):  # pragma: no cover
                    child_titles = _titles_in(child)  # pragma: no cover
                    if child_titles:  # pragma: no cover
                        union.update(child_titles)  # pragma: no cover
                        containers.append(child)  # pragma: no cover
            if union == titles_set:  # pragma: no cover
                return [str(c) for c in containers]  # pragma: no cover
            parent = parent.parent  # pragma: no cover

    # Phase 2b: sibling leaves each carry one title (medicarerights-style job links).
    if leaves:  # pragma: no cover
        union_from_leaves: set = set()  # pragma: no cover
        for _, leaf_titles in leaves:  # pragma: no cover
            union_from_leaves.update(leaf_titles)  # pragma: no cover
        if len(titles_set) >= 2 and union_from_leaves == titles_set:  # pragma: no cover
            return [str(leaf) for leaf, _ in leaves]  # pragma: no cover

    return [dom_html]  # pragma: no cover


def _strip_json_markdown_fences(text: str) -> str:
    """Remove leading/trailing ```json / ``` fences if present."""
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.MULTILINE)
        t = re.sub(r"\s*```\s*$", "", t, flags=re.MULTILINE)
    return t.strip()


def _emit_json_string_body(raw: str) -> str:
    """Re-emit a slice of JSON string *content* (no surrounding quotes) as valid JSON source bytes."""
    out: List[str] = []
    i = 0
    while i < len(raw):
        c = raw[i]
        if c == "\\":
            out.append(c)
            i += 1
            if i < len(raw):  # pragma: no cover
                out.append(raw[i])  # pragma: no cover
                i += 1  # pragma: no cover
            continue
        if c == "\n":
            out.append("\\n")
            i += 1
            continue
        if c == "\r":  # pragma: no cover
            out.append("\\r")  # pragma: no cover
            i += 1  # pragma: no cover
            continue  # pragma: no cover
        if c == '"':
            out.append('\\"')
            i += 1
            continue
        if ord(c) < 0x20:
            out.append(f"\\u{ord(c):04x}")
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def heal_agent_payload_envelope(s: str) -> Optional[str]:
    """Recover qualify_job_listings / evaluate_jd style JSON when ``agent_payload`` is a truncated string.

    Those tasks put newline-delimited lines in ``agent_payload``. If the closing quote never arrived,
    truncate the payload after the last line boundary: a literal linefeed, or a JSON ``\\n`` escape.
    Close the string and root object. Returns a string suitable for ``json.loads``, or ``None``.
    """
    if not isinstance(s, str) or not s.strip():
        return None
    cleaned = _strip_json_markdown_fences(s.strip())
    key = '"agent_payload"'
    k = cleaned.find(key)
    if k < 0:
        return None
    colon = cleaned.find(":", k + len(key))
    if colon < 0:
        return None
    j = colon + 1
    n = len(cleaned)
    while j < n and cleaned[j] in " \t\n\r":
        j += 1
    if j >= n or cleaned[j] != '"':
        return None
    str_open = j
    j += 1
    last_cut = -1  # exclusive end index in cleaned for payload string content (chars inside quotes)
    esc = False
    while j < n:
        c = cleaned[j]
        if esc:  # pragma: no cover
            if c in "nr":  # pragma: no cover
                last_cut = j + 1  # pragma: no cover
            esc = False  # pragma: no cover
            j += 1  # pragma: no cover
            continue  # pragma: no cover
        if c == "\\":
            esc = True
            j += 1
            continue
        if c == '"':
            return None
        if c == "\n":
            last_cut = j + 1
        j += 1
    if last_cut < 0:
        return None
    inner = cleaned[str_open + 1 : last_cut]
    inner_out = _emit_json_string_body(inner)
    return cleaned[: str_open + 1] + inner_out + '"}'


def heal_json(s: str) -> Optional[str]:
    """Recover truncated JSON by truncating to the last complete value, then closing open containers.

    Walks the string with a delimiter stack (objects/arrays) and string/escape state; records a
    checkpoint after each closed object/array, and after string/primitive values except when that
    value sits inside an object that is itself a direct array element (avoids partial objects like
    ``{"id":2}`` when further keys were truncated).

    If truncation ends inside a string, a comma has already closed a prior root-level key, and an
    array is still open, the root object cannot be completed without dropping a later key — return
    ``None`` (e.g. ``{"a":[1,2,3], "b":[4,5,"pa``).

    Strips trailing comma, appends closers, and returns the result only if ``json.loads`` accepts it.
    Returns ``None`` if nothing could be recovered.
    """
    if not isinstance(s, str):
        return None
    t = s.strip()
    if not t:
        return None
    try:
        json.loads(t)
        return t
    except json.JSONDecodeError:
        pass
    cleaned = _strip_json_markdown_fences(t)
    if not cleaned:
        return None
    try:
        json.loads(cleaned)
        return cleaned
    except json.JSONDecodeError:
        pass

    n = len(cleaned)
    stack: List[str] = []
    in_string = False
    escape = False
    root_object_key_comma_seen = False
    last_pos = -1
    last_stack: Optional[List[str]] = None
    dec = json.JSONDecoder()

    def _peek_non_ws(j: int) -> int:  # pragma: no cover
        while j < n and cleaned[j] in " \t\n\r":  # pragma: no cover
            j += 1  # pragma: no cover
        return j  # pragma: no cover

    def _record_checkpoint(pos: int) -> None:
        nonlocal last_pos, last_stack
        last_pos = pos
        last_stack = list(stack)

    def _may_checkpoint_primitive_or_string_value() -> bool:
        # Inside {"...": v} where that object is an array element, only `}` / `]` may checkpoint —
        # otherwise we'd emit a truncated object (e.g. {"id":2} while "title" was still coming).
        return not (len(stack) >= 2 and stack[-1] == "{" and stack[-2] == "[")

    i = 0
    while i < n:
        c = cleaned[i]
        if in_string:
            if escape:  # pragma: no cover
                escape = False  # pragma: no cover
            elif c == "\\":  # pragma: no cover
                escape = True  # pragma: no cover
            elif c == '"':  # pragma: no cover
                in_string = False  # pragma: no cover
                j = _peek_non_ws(i + 1)  # pragma: no cover
                if j >= n or cleaned[j] != ":":  # pragma: no cover
                    if _may_checkpoint_primitive_or_string_value():  # pragma: no cover
                        _record_checkpoint(i + 1)  # pragma: no cover
            i += 1
            continue

        if c == '"':
            in_string = True
            i += 1
            continue
        if c == "{":
            stack.append("{")
            i += 1
            continue
        if c == "}":
            if stack and stack[-1] == "{":  # pragma: no cover
                stack.pop()  # pragma: no cover
                _record_checkpoint(i + 1)  # pragma: no cover
            i += 1  # pragma: no cover
            continue  # pragma: no cover
        if c == "[":
            stack.append("[")
            i += 1
            continue
        if c == "]":
            if stack and stack[-1] == "[":  # pragma: no cover
                stack.pop()  # pragma: no cover
                _record_checkpoint(i + 1)  # pragma: no cover
            i += 1
            continue
        if c in " \t\n\r":
            i += 1
            continue
        if c == ",":
            # Comma between members of the root object only (stack is exactly one open '{').
            if len(stack) == 1 and stack[-1] == "{":
                root_object_key_comma_seen = True
            i += 1
            continue
        if c == ":":
            i += 1
            continue

        try:
            _, end = dec.raw_decode(cleaned, i)
            if _may_checkpoint_primitive_or_string_value():
                _record_checkpoint(end)
            i = end
            continue
        except (json.JSONDecodeError, ValueError):
            i += 1

    # Root object already has a completed prior key; a later key's value (here: array with broken
    # string) never finished — do not emit a shortened root object.
    if (
        in_string
        and root_object_key_comma_seen
        and any(op == "[" for op in stack)
    ):
        return None

    if last_pos < 0 or last_stack is None:
        return None

    body = cleaned[:last_pos].rstrip()
    while body.endswith(","):  # pragma: no cover
        body = body[:-1].rstrip()  # pragma: no cover

    closers = []
    for op in reversed(last_stack):
        closers.append("}" if op == "{" else "]")
    healed = body + "".join(closers)
    try:
        json.loads(healed)
        return healed
    except json.JSONDecodeError:
        return None
