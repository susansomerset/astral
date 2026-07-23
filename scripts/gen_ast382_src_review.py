#!/usr/bin/env python3
"""One-shot generator for AST-382 scorecard + notes over every file under src/. Run from repo root."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
OUT_DIR = ROOT / "debug"
VECS = [
    "A1",
    "A2",
    "A3",
    "A4",
    "B1",
    "B2",
    "B3",
    "C1",
    "C2",
    "C3",
    "D1",
    "D2",
    "D3",
    "E1",
    "E2",
    "E3",
    "F1",
    "F2",
    "F3",
    "G1",
    "G2",
    "H1",
    "H2",
    "H3",
    "H4",
    "H5",
]
REVIEW_DATE = "2026-05-06"

SCORECARD_INTRO = (
    "Scope: every path under <code>src/</code> (recursive). Vectors per Linear <strong>AST-382</strong>. "
    "<strong>F2 = B/1</strong> on large Python modules and most TS/TSX means: full public-docstring / API "
    "commentary coverage was not audited line-by-line in this bulk pass — revisit in a focused review."
)

# Hover text for scorecard column headers (Linear AST-382 rubric, condensed).
RUBRIC_VECTOR_TIPS: dict[str, str] = {
    "A1": (
        "A1 — Public before private: public functions appear before private/helpers "
        "(private prefixed with _); functions are not interleaved."
    ),
    "A2": (
        "A2 — Grouped by responsibility: related functions stay together; "
        "longer files use section comments between groups."
    ),
    "A3": (
        "A3 — File header: module docstring or top block states role, scope, and key constraints "
        "(e.g. tables owned, layer)."
    ),
    "A4": (
        "A4 — No dead code: no commented-out blocks, unused functions, or orphaned logic from old iterations."
    ),
    "B1": (
        "B1 — Imports at top: all imports at file top; inline imports only for documented lazy/circular-dependency loads."
    ),
    "B2": (
        "B2 — Layer compliance: imports only from layers allowed for this file’s layer (see architecture table)."
    ),
    "B3": "B3 — No unused imports: every imported name is used in the file.",
    "C1": (
        "C1 — Single responsibility: each function does one thing; orchestration OK, "
        "flat mixing of unrelated concerns is not."
    ),
    "C2": (
        "C2 — No magic numbers or hardcoded value sets: behavior-driving values live in config.py "
        "or named module constants."
    ),
    "C3": "C3 — DRY: shared logic extracted; no copy-paste blocks with minor variation.",
    "D1": (
        "D1 — Correct pattern for layer: data raises (no log); core domain exceptions; "
        "dispatcher logs batches; UI API returns JSON errors."
    ),
    "D2": (
        "D2 — No silent failures: no bare except: pass or swallowed errors without logging/raise."
    ),
    "D3": (
        "D3 — Judicious fallbacks: or {} / defaults only when absence truly doesn’t matter; "
        "otherwise raise."
    ),
    "E1": (
        "E1 — Uses project logger: src/utils/logging.py; no print(); no bare import logging "
        "(unless this file is logging.py)."
    ),
    "E2": (
        "E2 — Appropriate log levels: DEBUG internal, INFO lifecycle, WARNING recoverable, ERROR failures; "
        "no hot-path INFO spam or errors at DEBUG."
    ),
    "E3": (
        "E3 — Meaningful log messages: enough context for production (batch_id, job_id, state, etc.)."
    ),
    "F1": (
        "F1 — Inline comments explain why, not what: non-obvious intent documented; no noise like “increment i”."
    ),
    "F2": (
        "F2 — Public functions have docstrings: what it does, params, return when non-obvious."
    ),
    "F3": (
        "F3 — Section comments: files longer than ~150 lines use section headers so the file is scannable."
    ),
    "G1": (
        "G1 — State names from config: no hardcoded state strings in logic; reference or validate against config."
    ),
    "G2": (
        "G2 — No local redefinition of config: no shadow lists/thresholds that duplicate config.py."
    ),
    "H1": (
        "H1 — Batch claim/process/release: generate batch_id, claim, process, clear in finally; "
        "no unlocked state-only selects for batch work."
    ),
    "H2": (
        "H2 — State transitions: jobs via tracker.transition_job_state; companies via roster.transition_company_state; "
        "data layer not called for transitions from elsewhere."
    ),
    "H3": (
        "H3 — do_task usage: core uses do_task(task_key, live_content, index); core does not assemble Anthropic task payloads."
    ),
    "H4": (
        "H4 — Coat-check: fields accessed via roster.get_company_data / tracker.get_job_data; "
        "handlers do not persist empty or failed fetches."
    ),
    "H5": (
        "H5 — Naming: Python snake_case; React components PascalCase; API routes snake_case; "
        "vocabulary matches codebase (e.g. job_site, state keys match config)."
    ),
}


def all_same(cells: dict[str, str]) -> dict[str, str]:
    return {v: cells.get(v, "A/—") for v in VECS}


def row(file_rel: str, cells: dict[str, str] | None = None) -> str:
    cells = cells or {}
    parts = [file_rel] + [cells.get(v, "A/—") for v in VECS]
    return "| " + " | ".join(parts) + " |"


def list_src_files() -> list[str]:
    out = subprocess.check_output(["find", str(SRC), "-type", "f"], cwd=ROOT, text=True)
    lines = sorted(p.strip() for p in out.splitlines() if p.strip())
    return [Path(p).relative_to(ROOT).as_posix() for p in lines]


def write_scorecard_html(
    out_dir: Path,
    vectors: list[str],
    files: list[str],
    ovr: dict[str, dict[str, str]],
    generated_iso: str,
) -> None:
    """Standalone viewer: sort columns, filter by path and by 'has finding' (non-A, non-X)."""
    rows: list[dict[str, str]] = []
    for p in files:
        cells = ovr.get(p, {})
        row = {"file": p}
        for v in vectors:
            row[v] = cells.get(v, "A/—")
        rows.append(row)
    missing = set(vectors) - set(RUBRIC_VECTOR_TIPS)
    if missing:
        raise KeyError(f"RUBRIC_VECTOR_TIPS missing keys: {sorted(missing)}")
    tips = {v: RUBRIC_VECTOR_TIPS[v] for v in vectors}
    payload = {
        "vectors": vectors,
        "rows": rows,
        "generated": generated_iso,
        "vectorTips": tips,
    }
    json_blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Astral code review — scorecard</title>
  <style>
    :root {{
      --bg: #0f1419;
      --panel: #1a2332;
      --border: #2d3a4d;
      --text: #e6edf3;
      --muted: #8b9cb3;
      --accent: #58a6ff;
      --g-a: #3fb950;
      --g-b: #79c0ff;
      --g-c: #d29922;
      --g-d: #db6d28;
      --g-f: #f85149;
      --g-x: #6e7681;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      font-size: 13px;
      line-height: 1.4;
    }}
    header {{
      padding: 1rem 1.25rem;
      border-bottom: 1px solid var(--border);
      background: var(--panel);
    }}
    header h1 {{ margin: 0 0 0.5rem; font-size: 1.1rem; font-weight: 600; }}
    header p {{ margin: 0; color: var(--muted); max-width: 72ch; }}
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem 1.25rem;
      align-items: center;
      padding: 0.75rem 1.25rem;
      border-bottom: 1px solid var(--border);
      background: #151c27;
    }}
    .toolbar label {{ display: flex; align-items: center; gap: 0.4rem; color: var(--muted); white-space: nowrap; }}
    input[type="search"], select {{
      background: var(--panel);
      border: 1px solid var(--border);
      color: var(--text);
      border-radius: 6px;
      padding: 0.35rem 0.5rem;
      min-width: 12rem;
    }}
    select {{ min-width: 8rem; }}
    .meta {{ margin-left: auto; color: var(--muted); font-size: 12px; }}
    .wrap {{ overflow: auto; max-height: calc(100vh - 11rem); margin: 0 1rem 1rem; border: 1px solid var(--border); border-radius: 8px; }}
    table {{ border-collapse: collapse; width: 100%; min-width: max-content; }}
    thead th {{
      position: sticky;
      top: 0;
      z-index: 2;
      background: #212a3a;
      border-bottom: 2px solid var(--border);
      padding: 0.45rem 0.35rem;
      text-align: left;
      font-weight: 600;
      cursor: pointer;
      user-select: none;
      white-space: nowrap;
    }}
    thead th:hover {{ color: var(--accent); }}
    thead th[title]:not(.file-col) {{
      text-decoration: underline dotted var(--muted);
      text-underline-offset: 3px;
    }}
    thead th.file-col {{ min-width: 16rem; z-index: 3; left: 0; box-shadow: 1px 0 0 var(--border); }}
    tbody td.file-col {{
      position: sticky;
      left: 0;
      background: var(--bg);
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 12px;
      z-index: 1;
      box-shadow: 1px 0 0 var(--border);
    }}
    tbody tr:nth-child(even) td.file-col {{ background: #121920; }}
    tbody tr:nth-child(even) {{ background: #121920; }}
    td {{
      padding: 0.28rem 0.35rem;
      border-bottom: 1px solid var(--border);
      text-align: center;
    }}
    td.file-col {{ text-align: left; padding-left: 0.5rem; }}
    td.cell {{ font-variant-numeric: tabular-nums; }}
    td.g-a {{ color: var(--g-a); }}
    td.g-b {{ color: var(--g-b); }}
    td.g-c {{ color: var(--g-c); }}
    td.g-d {{ color: var(--g-d); }}
    td.g-f {{ color: var(--g-f); font-weight: 600; }}
    td.g-x {{ color: var(--g-x); }}
    th.sort-asc::after {{ content: " \\u2191"; opacity: 0.7; font-size: 10px; }}
    th.sort-desc::after {{ content: " \\u2193"; opacity: 0.7; font-size: 10px; }}
  </style>
</head>
<body>
  <header>
    <h1>Astral code review — scorecard</h1>
    <p>{SCORECARD_INTRO}</p>
  </header>
  <div class="toolbar">
    <label>Path <input type="search" id="qPath" placeholder="substring…" autocomplete="off" /></label>
    <label><input type="checkbox" id="onlyIssues" /> Non-A grades only (B–F; ignores X)</label>
    <label>Column focus <select id="vecFocus">
      <option value="">(all columns)</option>
    </select></label>
    <span class="meta" id="rowCount"></span>
  </div>
  <div class="wrap">
    <table>
      <thead><tr id="hdrRow"></tr></thead>
      <tbody id="body"></tbody>
    </table>
  </div>
  <script>
(function() {{
  const DATA = {json_blob};
  const VECS = DATA.vectors;
  const ALL = DATA.rows;
  const TIPS = DATA.vectorTips || {{}};
  let sortKey = "file";
  let sortDir = 1;

  function letter(cell) {{
    if (!cell || typeof cell !== "string") return "Z";
    const g = cell.split("/")[0].trim();
    return g.charAt(0) || "Z";
  }}

  function sev(cell) {{
    const m = (cell || "").split("/")[1];
    if (!m || m === "\\u2014" || m === "-") return -1;
    const n = parseInt(m, 10);
    return isNaN(n) ? -1 : n;
  }}

  function rankLetter(L) {{
    const o = {{ A: 0, B: 1, C: 2, D: 3, F: 4, X: 5 }};
    return o[L] !== undefined ? o[L] : 9;
  }}

  function cellClass(cell) {{
    const L = letter(cell);
    if (L === "A" || L === "X") return "cell g-" + L.toLowerCase();
    return "cell g-" + L.toLowerCase();
  }}

  function rowHasIssue(row) {{
    for (const v of VECS) {{
      const L = letter(row[v]);
      if (L === "B" || L === "C" || L === "D" || L === "F") return true;
    }}
    return false;
  }}

  function rowMatchesFocus(row) {{
    const v = document.getElementById("vecFocus").value;
    if (!v) return true;
    const L = letter(row[v]);
    return L !== "A" && L !== "X";
  }}

  function filtered() {{
    const q = document.getElementById("qPath").value.trim().toLowerCase();
    const issues = document.getElementById("onlyIssues").checked;
    return ALL.filter(function(row) {{
      if (q && row.file.toLowerCase().indexOf(q) === -1) return false;
      if (issues && !rowHasIssue(row)) return false;
      if (!rowMatchesFocus(row)) return false;
      return true;
    }});
  }}

  function cmp(a, b) {{
    const va = a[sortKey];
    const vb = b[sortKey];
    if (sortKey === "file") {{
      const c = va.localeCompare(vb);
      return sortDir * c;
    }}
    const ra = rankLetter(letter(va)) - rankLetter(letter(vb));
    if (ra !== 0) return sortDir * ra;
    const sa = sev(va) - sev(vb);
    if (sa !== 0) return sortDir * sa;
    return sortDir * a.file.localeCompare(b.file);
  }}

  function renderHead() {{
    const tr = document.getElementById("hdrRow");
    tr.innerHTML = "";
    const thFile = document.createElement("th");
    thFile.textContent = "File";
    thFile.className = "file-col" + (sortKey === "file" ? (sortDir === 1 ? " sort-asc" : " sort-desc") : "");
    thFile.dataset.key = "file";
    thFile.title = "Path under the repo (sortable).";
    tr.appendChild(thFile);
    for (const v of VECS) {{
      const th = document.createElement("th");
      th.textContent = v;
      th.dataset.key = v;
      if (TIPS[v]) th.title = TIPS[v];
      if (sortKey === v) th.className = sortDir === 1 ? "sort-asc" : "sort-desc";
      tr.appendChild(th);
    }}
    tr.querySelectorAll("th").forEach(function(th) {{
      th.addEventListener("click", function() {{
        const k = th.dataset.key;
        if (sortKey === k) sortDir *= -1;
        else {{ sortKey = k; sortDir = k === "file" ? 1 : 1; }}
        render();
      }});
    }});
    const sel = document.getElementById("vecFocus");
    if (sel.options.length <= 1) {{
      for (const v of VECS) {{
        const o = document.createElement("option");
        o.value = v;
        o.textContent = v + " has finding";
        sel.appendChild(o);
      }}
    }}
  }}

  function render() {{
    const rows = filtered().sort(cmp);
    document.getElementById("rowCount").textContent = rows.length + " / " + ALL.length + " rows";
    const tb = document.getElementById("body");
    tb.innerHTML = "";
    for (const row of rows) {{
      const tr = document.createElement("tr");
      const td0 = document.createElement("td");
      td0.textContent = row.file;
      td0.className = "file-col";
      tr.appendChild(td0);
      for (const v of VECS) {{
        const td = document.createElement("td");
        td.textContent = row[v];
        td.className = cellClass(row[v]);
        tr.appendChild(td);
      }}
      tb.appendChild(tr);
    }}
    renderHead();
  }}

  document.getElementById("qPath").addEventListener("input", render);
  document.getElementById("onlyIssues").addEventListener("change", render);
  document.getElementById("vecFocus").addEventListener("change", render);
  render();
}})();
  </script>
</body>
</html>
"""
    (out_dir / "code_review_scorecard.html").write_text(html, encoding="utf-8")


_VEC_HDR_NOTES = re.compile(r"^\*\*([A-H][0-9]) — ")


def _notes_section_title(sec: str) -> str:
    for ln in sec.split("\n"):
        if ln.startswith("## "):
            return ln[3:].strip()
    return ""


def _notes_linear_line(title: str, vec: str) -> str:
    """AST-321 / AST-381 / AST-383 only — tickets discussed in AST-382 review thread."""
    if vec == "B2":
        if "api_admin.py" in title:
            return (
                "**Linear (conversation scope):** **AST-321** explicitly exempts `api_admin` from routing API modules "
                "through core, so that ticket does **not** clear this B2 finding. **AST-381** / **AST-383** are unrelated."
            )
        if title.endswith("api_candidate.py") or title.endswith("api_companies.py") or title.endswith("api_jobs.py"):
            return (
                "**Linear (conversation scope):** **AST-321** (refactor API layer to use core; replaces direct `data` "
                "imports in this module per ticket scope)."
            )
        if title.endswith("api_system.py"):
            return "**Linear (conversation scope):** **AST-321** (same API→`core` refactor; covers inline `data` imports in this module)."
        if title.endswith("server.py"):
            return (
                "**Linear (conversation scope):** **AST-383** (`core/bootstrap` from `ui/server.py`; runtime startup, "
                "including `sync_agent_tasks`). **AST-381** is explicitly **not** part of automatic bootstrap."
            )
        if title.endswith("anthropic.py") or title.endswith("logging.py"):
            return "**Linear (conversation scope):** — (none of AST-321 / AST-381 / AST-383 cover this vector in this thread.)"
    if vec == "B1" and title.endswith("api_system.py"):
        return "**Linear (conversation scope):** — (not addressed by AST-321 / AST-381 / AST-383 in this thread.)"
    if vec == "E1":
        return "**Linear (conversation scope):** — (not addressed by AST-321 / AST-381 / AST-383 in this thread.)"
    if vec == "D2":
        return "**Linear (conversation scope):** — (not addressed by AST-321 / AST-381 / AST-383 in this thread.)"
    if vec == "G1":
        return (
            "**Linear (conversation scope):** — (none of the three tickets target UI state literals here; **AST-381** "
            "is admin snapshot export/preview/import, not G1.)"
        )
    if vec == "F2":
        return "**Linear (conversation scope):** — (not addressed by AST-321 / AST-381 / AST-383 in this thread.)"
    return "**Linear (conversation scope):** — (not addressed by AST-321 / AST-381 / AST-383 in this thread.)"


def _notes_process_src_section(sec: str) -> str:
    title = _notes_section_title(sec)
    if not title.startswith("src/"):
        return sec
    lines = sec.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = _VEC_HDR_NOTES.match(line)
        if m:
            vec = m.group(1)
            out.append(line)
            i += 1
            while i < len(lines) and not _VEC_HDR_NOTES.match(lines[i]):
                if lines[i].startswith("**Linear (conversation scope):**"):
                    break
                out.append(lines[i])
                i += 1
            if i < len(lines) and lines[i].startswith("**Linear (conversation scope):**"):
                out.append(lines[i])
                i += 1
                continue
            out.append(_notes_linear_line(title, vec))
            continue
        out.append(line)
        i += 1
    text = "\n".join(out).rstrip() + "\n"
    # blank before **Linear when missing
    text = re.sub(r"([^\n])\n(\*\*Linear \(conversation scope\):\*\*)", r"\1\n\n\2", text)
    # blank between **Linear and next vector
    out_lines = text.split("\n")
    fixed: list[str] = []
    for j, ln in enumerate(out_lines):
        fixed.append(ln)
        if ln.startswith("**Linear (conversation scope):**") and j + 1 < len(out_lines):
            nxt = out_lines[j + 1]
            if _VEC_HDR_NOTES.match(nxt) and (len(fixed) == 0 or fixed[-1] != ""):
                fixed.append("")
    return "\n".join(fixed)


def enrich_notes_with_linear_tickets(notes_text: str) -> str:
    """Append Linear ticket mapping per vector for src/* sections (idempotent)."""
    sep = "\n---\n"
    parts = notes_text.split(sep)
    if len(parts) < 2:
        return notes_text
    new_parts = [parts[0]]
    for p in parts[1:]:
        new_parts.append(_notes_process_src_section(p))
    out = sep.join(new_parts)
    return re.sub(r"\n{3,}", "\n\n", out)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = list_src_files()

    # Per-path overrides: incomplete review surfaces as B/1 on F2 only where we did not deep-read.
    # Known violations use explicit grades (see code_review_notes.md).
    ovr: dict[str, dict[str, str]] = {}

    def mark(path: str, **kwargs: str) -> None:
        ovr.setdefault(path, {}).update(kwargs)

    # --- Non-source: all X ---
    for p in files:
        suf = Path(p).suffix.lower()
        if suf in (".png", ".ico", ".jpg", ".jpeg", ".webp", ".gif"):
            ovr[p] = {v: "X/—" for v in VECS}
        if p.endswith("package-lock.json"):
            ovr[p] = {v: "X/—" for v in VECS}
        if p.endswith("/.gitkeep"):
            ovr[p] = {v: "X/—" for v in VECS}

    # --- Layer import violations (B2) ---
    for p in (
        "src/ui/api/api_admin.py",
        "src/ui/api/api_candidate.py",
        "src/ui/api/api_companies.py",
        "src/ui/api/api_jobs.py",
        "src/ui/api/api_system.py",
        "src/ui/server.py",
    ):
        mark(p, B2="F/5")

    mark("src/external/anthropic.py", B2="F/5", E1="C/3")

    # utils/logging crosses into data for DB sink (late import); rubric table says utils only.
    mark("src/utils/logging.py", B2="C/3", D2="B/2")

    # stdlib logging alongside project logger
    for p in (
        "src/core/agent.py",
        "src/core/consult.py",
        "src/core/dispatcher.py",
        "src/utils/config.py",
        "src/ui/api/api_system.py",
    ):
        mark(p, E1="B/2")

    # print instead of get_logger
    mark("src/external/playwright.py", E1="D/4")

    # roster: stdlib logging inside function + inline bs4 imports
    mark("src/core/roster.py", E1="B/2", B1="B/2")

    # Frontend: job/company state literals (G1) — rubric expects config-sourced names
    mark("src/ui/frontend/src/pages/JobsInReview.tsx", G1="C/3", F2="B/1")
    mark("src/ui/frontend/src/components/ArtifactEditor.tsx", G1="B/2", F2="B/1")
    mark("src/ui/frontend/src/components/CompanyDetailModal.tsx", G1="B/2", F2="B/1")
    mark("src/ui/frontend/src/components/JobDetailModal.tsx", G1="B/2", F2="B/1")
    mark("src/ui/frontend/src/pages/JobsSkipped.tsx", G1="B/2", F2="B/1")
    mark("src/ui/frontend/src/pages/CompaniesInactiveList.tsx", G1="B/2", F2="B/1")
    mark("src/ui/frontend/src/pages/CompaniesIgnored.tsx", G1="B/2", F2="B/1")

    # data/database: cryptography + zlib — third party in data layer (B1 fine); no change
    # formatting.py uses bs4 inside functions — B1 B/2 without circular comment on first occurrence
    mark("src/utils/formatting.py", B1="B/2")

    # Large modules not line-audited in this pass: single informational F2
    deep_py = [
        "src/core/agent.py",
        "src/core/builder.py",
        "src/core/candidate.py",
        "src/core/consult.py",
        "src/core/dispatcher.py",
        "src/core/gazer.py",
        "src/core/monitor.py",
        "src/core/roster.py",
        "src/core/tracker.py",
        "src/data/database.py",
        "src/external/gmail.py",
        "src/external/playwright.py",
        "src/ui/api/api_admin.py",
        "src/utils/config.py",
        "src/utils/cost_calculator.py",
        "src/utils/formatting.py",
        "src/utils/network.py",
        "src/utils/rubric_text.py",
    ]
    for p in deep_py:
        if p in ovr and "F2" in ovr[p]:
            continue
        mark(p, F2="B/1")

    # TS/TSX/CSS not line-audited: informational on F2 (public docstrings N/A in TS; means "narrative review deferred")
    for p in files:
        if not p.startswith("src/ui/frontend/"):
            continue
        if Path(p).suffix.lower() not in (".tsx", ".ts", ".css"):
            continue
        if p in ovr and ovr[p].get("F2"):
            continue
        if p.endswith(".d.ts"):
            ovr[p] = {v: "X/—" for v in VECS}
            continue
        mark(p, F2="B/1", E1="X/—", E2="X/—", E3="X/—", D1="X/—", D2="X/—", D3="X/—", H1="X/—", H2="X/—", H3="X/—", H4="X/—")

    # JSON / HTML / MD config in frontend
    for suf in (".json", ".html", ".md"):
        for p in files:
            if p.startswith("src/ui/frontend/") and p.endswith(suf):
                ovr.setdefault(p, {}).update({v: "X/—" for v in VECS})

    # eslint.config.js
    for p in files:
        if p.endswith("eslint.config.js") or p.endswith("vite.config.ts"):
            ovr[p] = {v: "X/—" for v in VECS}

    lines_score = [
        "# Astral Code Review — Scorecard",
        "",
        "Scope: every path under `src/` (recursive). Vectors per Linear **AST-382**. "
        "**F2 = B/1** on large Python modules and most TS/TSX means: full public-docstring / API commentary "
        "coverage was not audited line-by-line in this bulk pass — revisit in a focused review.",
        "",
        "| File | A1 | A2 | A3 | A4 | B1 | B2 | B3 | C1 | C2 | C3 | D1 | D2 | D3 | E1 | E2 | E3 | F1 | F2 | F3 | G1 | G2 | H1 | H2 | H3 | H4 | H5 |",
        "|------|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|",
    ]

    for p in files:
        lines_score.append(row(p, ovr.get(p)))

    (OUT_DIR / "code_review_scorecard.md").write_text("\n".join(lines_score) + "\n", encoding="utf-8")
    write_scorecard_html(OUT_DIR, VECS, files, ovr, REVIEW_DATE)

    # --- Notes (B or below only) ---
    # Each fragment must end with ``\\n`` so ``"".join(notes)`` does not glue headings together.
    notes: list[str] = [
        "# Astral Code Review — Notes\n",
        "\n",
        "Append-only companion to `code_review_scorecard.md`. Sections below list **B or below** only.\n",
        "\n",
        "### Linear tickets (this conversation only)\n",
        "\n",
        "Cross-refs below use only tickets **discussed in this thread**: **AST-321**, **AST-381**, **AST-383**. "
        "Each graded vector ends with a **Linear (conversation scope):** line naming which of those tickets (if any) apply.\n",
        "\n",
    ]

    def sec(title: str, layer: str, body: str) -> None:
        notes.append("---\n")
        notes.append(f"## {title}\n")
        notes.append(f"Layer: {layer}\n")
        notes.append(f"Reviewed: {REVIEW_DATE}\n\n")
        notes.append(body.rstrip() + "\n")

    # Structured findings
    sec(
        "src/ui/api/api_admin.py",
        "ui",
        "**B2 — Layer compliance** `F/5`\n"
        "- line 13–14: `from src.data import database` / `from src.data.database import (...)`\n"
        "  UI layer imports **data** directly; rubric / `docs/ASTRAL_CODE_RULES.md` require UI → core/utils only. "
        "Route through core facades or thin API-specific data helpers living in an allowed layer.\n",
    )
    for title, first_ln in (
        ("src/ui/api/api_candidate.py", "18"),
        ("src/ui/api/api_companies.py", "6"),
        ("src/ui/api/api_jobs.py", "7"),
    ):
        sec(
            title,
            "ui",
            "**B2 — Layer compliance** `F/5`\n"
            f"- line {first_ln}: `from src.data` / `from src.data.database import`\n"
            "  Same as api_admin: data layer reachable from UI API modules.\n",
        )

    sec(
        "src/ui/api/api_system.py",
        "ui",
        "**B2 — Layer compliance** `F/5`\n"
        "- line 27, 48: `from src.data.database import ...` (inside route handlers)\n"
        "  Data imports from UI API.\n\n"
        "**B1 — Imports at top** `B/2`\n"
        "- line 137, 148: `from src.core.agent import ...` nested in functions\n"
        "  Acceptable if each carries a one-line circular-import rationale (verify).\n",
    )

    sec(
        "src/ui/server.py",
        "ui",
        "**B2 — Layer compliance** `F/5`\n"
        "- line 45: `from src.data import database  # noqa: E402`\n"
        "  UI bootstrap imports data layer.\n",
    )

    sec(
        "src/external/anthropic.py",
        "external",
        "**B2 — Layer compliance** `F/5`\n"
        "- line 18: `from src.data.database import _add_timesheet_entry`\n"
        "  External layer imports **data**; rubric allows external → utils only. "
        "Timesheet persistence belongs behind core or a utils-level callback supplied by composition root.\n\n"
        "**E1 — Uses project logger** `C/3`\n"
        "- line 28–30: `import logging as _logging` + `getLogger(...).setLevel(...)`\n"
        "  Stdlib logging alongside `get_logger`; rubric prefers single project logging surface.\n"
        "- line 36: `print(\"[!] Anthropic SDK not installed...\")`\n"
        "  Startup guard uses `print` instead of `get_logger` (and exits via `sys.exit`).\n",
    )

    sec(
        "src/external/playwright.py",
        "external",
        "**E1 — Uses project logger** `D/4`\n"
        "- lines 133–1953 (representative): multiple `print(...)` calls for cookie / crawl diagnostics\n"
        "  Replace with `get_logger(__name__)` at appropriate levels (`debug`/`info`) so production logs stay structured.\n",
    )

    sec(
        "src/utils/logging.py",
        "utils",
        "**B2 — Layer compliance** `C/3`\n"
        "- line 77: `from src.data.database import add_log_entry  # late import`\n"
        "  Strict rubric table says utils imports nothing outside utils; this is the intentional DB log sink. "
        "Severity tempered: documented late import avoids import cycles, but architecture is still coupled.\n\n"
        "**D2 — No silent failures** `B/2`\n"
        "- line 61–62, 80–81: `except Exception: pass` inside logging handler\n"
        "  Documented to keep logging from crashing callers; acceptable if paired with metrics/fallback elsewhere — "
        "otherwise risk silent log loss.\n",
    )

    sec(
        "src/core/agent.py",
        "core",
        "**E1 — Uses project logger** `B/2`\n"
        "- line 13: `import logging`\n"
        "  Prefer `get_logger` exclusively unless stdlib integration is unavoidable and documented.\n\n"
        "**F2 — Public function docstrings** `B/1`\n"
        "  Large module; docstring coverage not fully verified in this bulk pass.\n",
    )

    for title in (
        "src/core/consult.py",
        "src/core/dispatcher.py",
        "src/utils/config.py",
        "src/ui/api/api_system.py",
    ):
        layer = "ui" if "ui/" in title else "core" if title.startswith("src/core/") else "utils"
        body = ""
        if "consult" in title or "dispatcher" in title:
            body = (
                "**E1 — Uses project logger** `B/2`\n"
                "- top: `import logging` alongside project logging utilities\n"
                "  Align on `get_logger` per rubric.\n\n"
                "**F2 — Public function docstrings** `B/1`\n"
                "  Very large orchestration module; narrative API review deferred.\n"
            )
        elif "config" in title:
            body = (
                "**E1 — Uses project logger** `B/2`\n"
                "- `import logging` + `getLogger` usage\n"
                "  Prefer unified `get_logger` from `src.utils.logging`.\n\n"
                "**F2 — Public function docstrings** `B/1`\n"
                "  Config surface is huge; not fully audited.\n"
            )
        else:
            body = (
                "**E1 — Uses project logger** `B/2`\n"
                "- `import logging` / `_log = logging.getLogger(__name__)`\n"
                "  Use `get_logger` for consistency.\n\n"
                "**F2 — Public function docstrings** `B/1`\n"
                "  Not fully audited.\n"
            )
        sec(title, layer, body)

    sec(
        "src/core/roster.py",
        "core",
        "**E1 — Uses project logger** `B/2`\n"
        "- line 353: `import logging` inside function to tune `httpcore`/`httpx`/`anthropic` log levels\n"
        "  Acceptable integration tweak; still mixes stdlib logging with project logger story — document why.\n\n"
        "**B1 — Imports at top** `B/2`\n"
        "- line 837, 877: `from bs4 import BeautifulSoup` inside functions\n"
        "  Lazy imports need explicit circular-import comments per rubric.\n\n"
        "**F2 — Public function docstrings** `B/1`\n"
        "  Large file; partial pass only.\n",
    )

    sec(
        "src/ui/frontend/src/pages/JobsInReview.tsx",
        "ui",
        "**G1 — State names from config** `C/3`\n"
        "- lines 24–31: `SECTION_LABELS` embeds job state strings (`NEW`, `VALID_TITLE`, ...)\n"
        "  UI duplicates JOB_STATES vocabulary; drift risk vs `src/utils/config.py`. Prefer server-resolved labels or shared generated types.\n\n"
        "**F2 — Public function docstrings** `B/1`\n"
        "- (module-level)\n"
        "  TSX module; exhaustive exported-component documentation not verified in this pass.\n",
    )

    for title, ln, snip, g1g in (
        (
            "src/ui/frontend/src/components/ArtifactEditor.tsx",
            "21",
            '`const GENERATE_STATES = new Set(["RESUME_READY", "ACTIVE_SEARCH"])`  # AST-973',
            "B/2",
        ),
        (
            "src/ui/frontend/src/components/CompanyDetailModal.tsx",
            "56",
            '`data.state === "WATCH"`',
            "B/2",
        ),
        (
            "src/ui/frontend/src/components/JobDetailModal.tsx",
            "123",
            '`job.state === "CANDIDATE_SKIPPED"`',
            "B/2",
        ),
        (
            "src/ui/frontend/src/pages/JobsSkipped.tsx",
            "239",
            '`to_state: "NEW"`',
            "B/2",
        ),
        (
            "src/ui/frontend/src/pages/CompaniesInactiveList.tsx",
            "44",
            '`to_state: "WEBSITE_FOUND"`',
            "B/2",
        ),
        (
            "src/ui/frontend/src/pages/CompaniesIgnored.tsx",
            "45",
            '`to_state: "TO_WATCH"`',
            "B/2",
        ),
    ):
        sec(
            title,
            "ui",
            f"**G1 — State names from config** `{g1g}`\n- line {ln}: {snip}\n"
            "  Literal Astral state string in UI logic; should be sourced from shared config contract or API metadata.\n\n"
            "**F2 — Public function docstrings** `B/1`\n"
            "- (module-level)\n"
            "  TSX module; narrative review deferred.\n",
        )

    sec(
        "src/utils/formatting.py",
        "utils",
        "**B1 — Imports at top** `B/2`\n"
        "- line 113, 130: `from bs4 import BeautifulSoup` inside functions\n"
        "  Add explicit circular-import / optional-dependency comments per rubric.\n\n"
        "**F2 — Public function docstrings** `B/1`\n"
        "  Helpers not exhaustively checked.\n",
    )

    # Boilerplate F2 B/1 sections for remaining flagged paths
    done_titles = {
        "src/ui/api/api_admin.py",
        "src/ui/api/api_candidate.py",
        "src/ui/api/api_companies.py",
        "src/ui/api/api_jobs.py",
        "src/ui/api/api_system.py",
        "src/ui/server.py",
        "src/external/anthropic.py",
        "src/external/playwright.py",
        "src/utils/logging.py",
        "src/core/agent.py",
        "src/core/consult.py",
        "src/core/dispatcher.py",
        "src/utils/config.py",
        "src/core/roster.py",
        "src/ui/frontend/src/pages/JobsInReview.tsx",
        "src/ui/frontend/src/components/ArtifactEditor.tsx",
        "src/ui/frontend/src/components/CompanyDetailModal.tsx",
        "src/ui/frontend/src/components/JobDetailModal.tsx",
        "src/ui/frontend/src/pages/JobsSkipped.tsx",
        "src/ui/frontend/src/pages/CompaniesInactiveList.tsx",
        "src/ui/frontend/src/pages/CompaniesIgnored.tsx",
        "src/utils/formatting.py",
        "src/ui/frontend/src/pages/JobsInReview.tsx",
        "src/ui/frontend/src/components/ArtifactEditor.tsx",
        "src/ui/frontend/src/components/CompanyDetailModal.tsx",
        "src/ui/frontend/src/components/JobDetailModal.tsx",
        "src/ui/frontend/src/pages/JobsSkipped.tsx",
        "src/ui/frontend/src/pages/CompaniesInactiveList.tsx",
    }

    for p in files:
        cells = ovr.get(p, {})
        has_low = any(cells.get(v, "A/—").split("/")[0] in ("B", "C", "D", "F") for v in VECS)
        if not has_low:
            continue
        if p in done_titles:
            continue
        if cells == {v: "X/—" for v in VECS}:
            sec(p, "assets" if "img/" in p else "config", "No code-rubric findings; all vectors **X** (not applicable).\n")
            continue
        # F2 B/1 only or other
        layer_guess = "ui" if "/ui/frontend/" in p else ("ui" if p.startswith("src/ui/") else "core" if "/core/" in p else "data" if "/data/" in p else "external" if "/external/" in p else "utils")
        sec(
            p,
            layer_guess,
            "**F2 — Public function docstrings** `B/1`\n"
            "- (file-level)\n"
            "  TS/TSX module: narrative review / JSDoc coverage not completed in AST-382 bulk sweep.\n",
        )

    (OUT_DIR / "code_review_notes.md").write_text(
        enrich_notes_with_linear_tickets("".join(notes)), encoding="utf-8"
    )
    print(
        f"Wrote {OUT_DIR / 'code_review_scorecard.md'}, "
        f"{OUT_DIR / 'code_review_scorecard.html'}, "
        f"code_review_notes.md ({len(files)} files)"
    )


if __name__ == "__main__":
    main()
