# AST-1516 — Gazer scrape contact task

**Linear:** [AST-1516](https://linear.app/astralcareermatch/issue/AST-1516/gazer-scrape-contact-task-estelle-needs-to-be-able-to-use-our-endpoints)  
**Parent:** [AST-1414](https://linear.app/astralcareermatch/issue/AST-1414/estelle-needs-to-be-able-to-use-our-endpoints) — Estelle needs to be able to use our endpoints  
**Publish ref:** `sub/AST-1414/AST-1516-gazer-scrape-contact-task`

Child #2 of AST-1414: implement the gazer contact-task scrape handler already registered by sibling AST-1515 as `CONTACT_TASK_CONFIG["gazer_scrape"]["handler"]` → `src.core.gazer.contact_task_gazer_scrape`. One URL in → visible text, page links, and a contact-facing page status (`blocked` / `ok` / `closed` / `missing`) via extant Playwright fetch + `_classify_jd`. Does **not** create a job, does **not** own markup/dispatch (AST-1515), and does **not** implement `create_contact_meteorite` (AST-1517) or read handlers (AST-1518).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/gazer.py` (modified — contact-task scrape helper). Technical: async helper wrapping extant Playwright visible-text fetch + link extraction + `_classify_jd` outcome for a single URL.

**Out of scope:** `src/utils/config.py` / `src/core/contact.py` / `data/admin/agent_task.json` (AST-1515); `src/core/meteorite.py` (AST-1517); `src/core/tracker.py` (AST-1518); any new job create/transition; new config keys.

**Depends on:** AST-1515 handler contract (present on `origin/ftr/AST-1414-estelle-endpoints` after merge-on-checkout). Dispatch calls `handler(astral_candidate_id, param, debug=debug)` and supports async via `asyncio.run`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/gazer.py` | New public async `contact_task_gazer_scrape`; module header + Playwright imports; Style D on this path when `debug=True` | core |

## Stage 1: `contact_task_gazer_scrape` handler

**Done when:** `from src.core.gazer import contact_task_gazer_scrape` succeeds; calling it with a URL param returns a dict with `ok`, `task_key`, `url`, `final_url`, `visible_text`, `links`, and `page_status` in `{blocked, ok, closed, missing}` (or `ok=False` + `error` on validation/scrape failure); no job rows are created or transitioned; Style D index/detail emit only when `debug=True`.

1. In `src/core/gazer.py` module docstring **In-scope** list, add `contact_task_gazer_scrape` (AST-1516 contact-task scrape).

2. Extend the `src.external.playwright` import to also include `close_page` and `extract_page_scrape_contract` (keep existing imports).

3. Immediately after `_JD_ERROR_STATES`, add a contact-facing status map (module constant):

```python
# Maps _classify_jd() → Estelle/contact page_status (parent AC2: blocked/ok/closed/missing)
_CONTACT_PAGE_STATUS = {
    "ok": "ok",
    "closed": "closed",
    "missing": "missing",
    "bot": "blocked",
    "cookie": "blocked",
}
```

   ⚠️ **Decision:** Parent / ticket language uses **blocked**, not separate cookie/bot. Keep `_classify_jd` and `_JD_ERROR_STATES` unchanged for batch JD scrape; only this contact-task surface collapses cookie+bot → `blocked`.

4. Add public async handler (place it in a labeled section `# ---- Contact-task scrape (AST-1516) ----` immediately **before** `# ---- Process batch` / `process_gazer_batch` — after `scrape_one`, same single-URL Playwright family as meteorite helpers without burying it inside email ingest):

```python
async def contact_task_gazer_scrape(
    astral_candidate_id: str,
    param: str,
    *,
    debug: bool = False,
) -> Dict[str, Any]:
```

   Signature matches AST-1515 dispatch: positional `(astral_candidate_id, param)` plus keyword-only `debug`.

5. Implement body as follows (no job create / no `transition_job_state` / no `save_job_data` / no `_prune_jd`):

   a. `log = get_logger(__name__)`; `log.set_debug_flag(debug)`.

   b. `url = (param or "").strip()`. If empty: return
      `{"ok": False, "error": "url_required", "task_key": "gazer_scrape"}`.

   c. If `"://" not in url`: set `url = f"https://{url.lstrip('/')}"` (same scheme fix as roster `_scrape_pjl_page`).

   d. Optional connectivity: if `not await check_connectivity()`: return
      `{"ok": False, "error": "no_connectivity", "task_key": "gazer_scrape", "url": url}`.

   e. Scrape in one browser session (reuse extant external APIs only):

      ```python
      async with create_browser_context() as browser_context:
          page = await get_page(browser_context, url)
          try:
              raw = await extract_page_scrape_contract(page)
          finally:
              await close_page(page)
      ```

      On any exception: log a warning with URL prefix; return
      `{"ok": False, "error": str(exc), "task_key": "gazer_scrape", "url": url}` — do not raise (follow-up turn still gets a payload).

   f. `visible_text = collapse_consecutive_blank_lines(raw.get("visible_text") or "")`.
      `links = list(raw.get("nav_urls") or [])` (plain URL list for the contact payload; do **not** require enumerated string).
      `final_url = (raw.get("final_url") or url).strip() or url`.

   g. `classification = _classify_jd(visible_text)` then
      `page_status = _CONTACT_PAGE_STATUS.get(classification, "missing")`.

   h. Success return dict (exact keys):

      ```python
      {
          "ok": True,
          "task_key": "gazer_scrape",
          "astral_candidate_id": (astral_candidate_id or "").strip(),
          "url": url,
          "final_url": final_url,
          "visible_text": visible_text,
          "links": links,
          "page_status": page_status,  # blocked | ok | closed | missing
          "classification": classification,  # raw _classify_jd for debug/trace
      }
      ```

      ⚠️ **Decision:** Include both `page_status` (Estelle-facing) and `classification` (raw classifier). Contact follow-up / Estelle should prefer `page_status`; raw remains for backend inspection. `astral_candidate_id` is accepted for the dispatch contract but unused for persistence — scrape is not candidate-scoped in the DB.

   i. **Style D (debug=True only):** one `debug_index` with `func="gazer.contact_task_gazer_scrape"`, `index=1`, `total=1`, `identifier=` URL truncated to 80 chars, `outcome=` either `ok page_status={page_status}` or `failed error=…`; `debug_detail` lines for `final_url=`, `visible_chars=`, `links_count=`, and when success a truncated visible-text sample via `truncate_debug_content` (import `truncate_debug_content` from `src.utils.logging` if not already imported). No Style D emission when `debug=False`.

6. Do **not** edit `CONTACT_TASK_CONFIG`, contact dispatch, meteorite, or tracker. Do **not** add stub/alternate handler names.

## Execution contract

- Execute stages and steps in order; one commit per stage on epic worktree; push `git push origin HEAD:sub/AST-1414/AST-1516-gazer-scrape-contact-task` after each stage.
- No files outside Files Changed.
- Ambiguity or missing Playwright symbols → stop, comment on **AST-1516** with Stage blocked format, wait.
- Test tree / bible: Betty only — engineer does not edit `tests/` or `docs/test-bible/**`.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1516
**Overall:** APPROVED
**Publish ref:** `sub/AST-1414/AST-1516-gazer-scrape-contact-task` @ `072cf5a3bd464c5533bc89866c4ffd0c6f0a7ed7`

## Traceability
AC2 (handler slice: visible text + links + blocked/ok/closed/missing, no job create)→S1; AC2 (same-event follow-up / Estelle narrative)→N/A (AST-1515 dispatch); AC3→S1 step 5i; parent AC1/4–8→N/A or sibling scope.

## Findings

### discuss — Linear assignee
**Finding:** Ticket is `Plan Ready` but assignee is Hedy, not Joan. Chuckles normally assigns Joan before validate-plan.
**Recommendation:** Procedural only — does not block plan quality; Chuckles may restore implementer after posting upshot.

### acceptable — Scope, layers, handler contract
Single file `src/core/gazer.py`; Playwright I/O stays in `src.external.playwright` (`create_browser_context`, `get_page`, `extract_page_scrape_contract`, `close_page`); no job create/transition/`save_job_data`; async signature matches AST-1515 dispatch; `CONTACT_TASK_CONFIG` handler path already points at `contact_task_gazer_scrape`.

### acceptable — Classification + payload
`_CONTACT_PAGE_STATUS` collapses `cookie`/`bot`→`blocked` without mutating batch `_classify_jd` / `_JD_ERROR_STATES`; success dict includes Estelle-facing `page_status` plus raw `classification`; `nav_urls`→`links` list matches parent functional scope; connectivity/exception paths return `ok=False` dicts (turn stays alive).

### acceptable — DRY + Style D
Reuses roster-aligned scrape contract (`extract_page_scrape_contract` + `collapse_consecutive_blank_lines`); handler-level Style D is `debug=True`-gated with `truncate_debug_content` for long text; outer dispatch bookends from AST-1515 remain the per-task found/recorded pair — handler uses a single index (sibling AST-1518 uses dual index internally; both acceptable).

context_tokens≈45000

---

[plan-rubric] PROCEED (Commit: 072cf5a3) scrape handler ready
