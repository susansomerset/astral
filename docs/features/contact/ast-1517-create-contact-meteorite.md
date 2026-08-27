# AST-1517 — create_contact_meteorite

**Linear:** [AST-1517](https://linear.app/astralcareermatch/issue/AST-1517/create-contact-meteorite-estelle-needs-to-be-able-to-use-our-endpoints)  
**Parent:** [AST-1414](https://linear.app/astralcareermatch/issue/AST-1414/estelle-needs-to-be-able-to-use-our-endpoints) — Estelle needs to be able to use our endpoints  
**Publish ref:** `sub/AST-1414/AST-1517-create-contact-meteorite`

Child #3 of AST-1414: implement the `create_contact_meteorite` handler already registered by sibling AST-1515 as `CONTACT_TASK_CONFIG["create_contact_meteorite"]["handler"]` → `src.core.meteorite.create_contact_meteorite`. Link mode calls AST-1516 `contact_task_gazer_scrape` then `create_meteorite_job`; text mode calls `create_meteorite_job` with the pasted body and no fetch. Lands in existing `METEORITE_CONFIG["job_create_state"]` (`METEORITE_NEW`); analysis continues via existing meteorite dispatch (no new states, no new dispatch rows). Does **not** own markup/dispatch (AST-1515) or the scrape helper body (AST-1516).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/meteorite.py` (modified — `create_contact_meteorite` wrapper). Technical: candidate-scoped entrypoint; link mode calls gazer scrape helper then `create_meteorite_job`; text mode calls `create_meteorite_job` directly; returns create result dict for contact dispatch.

**Out of scope:** `src/utils/config.py` / `src/core/contact.py` / `data/admin/agent_task.json` (AST-1515); `src/core/gazer.py` (AST-1516 — call `contact_task_gazer_scrape` only; do not edit); `src/core/tracker.py` (AST-1518); `land_meteorite` / email / mailbox paths; new job states or dispatch_task seeds.

**Depends on:** AST-1515 handler contract + AST-1516 `contact_task_gazer_scrape` (both present on epic worktree after `sync-child.sh` merges `origin/ftr/AST-1414-estelle-endpoints`). Dispatch calls `handler(astral_candidate_id, param, debug=debug)` and supports async via `asyncio.run`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/meteorite.py` | New public async `create_contact_meteorite`; private URL-vs-text helper; module docstring In-scope; Style D when `debug=True` | core |

## Stage 1: `create_contact_meteorite` handler

**Done when:** `from src.core.meteorite import create_contact_meteorite` succeeds; calling it with a URL-shaped param scrapes via `contact_task_gazer_scrape` then inserts a job in `METEORITE_NEW` with visible text + `job_link`; calling it with pasted page text inserts from that text with `job_link=None` and never opens a browser; failure paths return `ok=False` dicts (no raise into Contact); Style D emits only when `debug=True`.

1. In `src/core/meteorite.py` module docstring, add `create_contact_meteorite` (AST-1517 contact-task create) to the described public surface (keep existing land/ensure/create summary intact — one short clause is enough).

2. Add private URL detector (module-level helper, immediately above the new public handler section):

```python
def _contact_param_looks_like_url(param: str) -> bool:
    """True when param is a single-line URL / bare host-path (link mode)."""
```

   Rules (exact):

   - `s = (param or "").strip()`; empty → `False`.
   - If `"\n"` or `"\r"` in `s` → `False` (pasted multi-line page text).
   - If any whitespace (`" "` / `"\t"`) in `s` → `False` (prose with an embedded URL stays text mode — AC4 “no usable link” as the param itself).
   - If `"://"` in `s` → `True`.
   - Else: `True` only when `"."` in `s` and `s` does not start with `"."` (bare `host.tld/...` same scheme-fix path gazer uses).

   ⚠️ **Decision — URL vs text:** AST-1515 `param_hint` is “URL or page text (rest of line)” with no mode flag. Single-token URL-shaped params → link mode (scrape-first). Anything with whitespace/newlines, or no domain dot / scheme → text mode (no fetch). Do **not** scrape when Estelle pastes a paragraph that happens to contain a URL.

3. Add a labeled section `# ---- Contact-task create (AST-1517) ----` immediately **after** `create_meteorite_job` (before `_land_fetch_link_text` / land helpers). Add public async handler:

```python
async def create_contact_meteorite(
    astral_candidate_id: str,
    param: str,
    *,
    debug: bool = False,
) -> Dict[str, Any]:
```

   Signature matches AST-1515 dispatch: positional `(astral_candidate_id, param)` plus keyword-only `debug`.

4. Implement body as follows:

   a. `log = get_logger(__name__)`; `log.set_debug_flag(debug)`.

   b. `cid = (astral_candidate_id or "").strip()`. If empty: return
      `{"ok": False, "error": "no_candidate", "task_key": "create_contact_meteorite"}`.

   c. `raw = (param or "").strip()`. If empty: return
      `{"ok": False, "error": "param_required", "task_key": "create_contact_meteorite"}`.

   d. **Link mode** when `_contact_param_looks_like_url(raw)`:

      - Late-import inside the function (avoid import cycle — `gazer` already imports `create_meteorite_job` at module top):
        `from src.core.gazer import contact_task_gazer_scrape`
      - `scrape = await contact_task_gazer_scrape(cid, raw, debug=debug)`
      - If not a `dict` or `not scrape.get("ok")`: return
        `{"ok": False, "error": (scrape.get("error") if isinstance(scrape, dict) else "scrape_failed") or "scrape_failed", "task_key": "create_contact_meteorite", "mode": "link", "scrape": scrape if isinstance(scrape, dict) else None}` — do **not** call `create_meteorite_job`.
      - `visible = (scrape.get("visible_text") or "").strip()`; if empty: return
        `{"ok": False, "error": "empty_visible_text", "task_key": "create_contact_meteorite", "mode": "link", "scrape": scrape}`.
      - `link = (scrape.get("final_url") or scrape.get("url") or raw).strip()`
      - Call create (step e) with `html_body=visible`, `job_link=link`, `mode="link"`, and attach scrape summary fields on success (`page_status`, `url`, `final_url` from scrape).

      ⚠️ **Decision — still create when `page_status` is blocked/closed/missing:** Parent AC3 requires a job with stored visible text + link after a URL create; it does not gate on `ok` page status. Classifier outcome stays on the scrape payload / follow-up turn. Only hard-fail scrape (`ok=False`) or empty visible text blocks create.

   e. **Text mode** otherwise:

      - Call create (step f) with `html_body=raw`, `job_link=None`, `mode="text"`.
      - Do **not** import or call gazer / Playwright / `_land_fetch_link_text`.

   f. Shared create + normalize (both modes):

      ```python
      try:
          created = create_meteorite_job(
              cid,
              html_body,
              job_link=job_link,
              debug=debug,
          )
      except Exception as exc:
          return {
              "ok": False,
              "error": str(exc),
              "task_key": "create_contact_meteorite",
              "mode": mode,
          }
      ```

      Success return dict (exact keys):

      ```python
      {
          "ok": True,
          "task_key": "create_contact_meteorite",
          "mode": mode,  # "link" | "text"
          "astral_candidate_id": cid,
          "result": created,  # create_meteorite_job return dict (astral_job_id, company, state, …)
          # link mode only — omit keys in text mode:
          "url": scrape.get("url"),
          "final_url": scrape.get("final_url"),
          "page_status": scrape.get("page_status"),
      }
      ```

      ⚠️ **Decision — call `create_meteorite_job`, not `land_meteorite` / `tracker.save_meteorite_job`:** Ticket Technical scope names `create_meteorite_job` explicitly. That path is the same METEORITE_NEW carve-out gazer email ingest already uses; `METEORITE_NEW` is the meteorite landing state; existing `qualify_meteorite` dispatch claims that state — no new dispatch wiring in this ticket.

   g. **Style D (`debug=True` only):** two index headers (found → recorded), matching parent AC8 / sibling AST-1518 write-path shape:

      - `func="meteorite.create_contact_meteorite"`
      - `index=1`, `total=2`, `identifier=` truncated param (80 chars) or `cid`, `outcome="found"`; `debug_detail` lines: `mode=`, `param=` (via `truncate_debug_content` when long).
      - `index=2`, `total=2`, same identifier, `outcome=` either `recorded astral_job_id=… state=…` or `failed error=…`; on success `debug_detail` for `company=`, `job_link=`, and link-mode `page_status=`.

      Import `truncate_debug_content` from `src.utils.logging` if not already imported. No Style D when `debug=False`. Emit Style D on both success and soft-fail returns (so Contact debug shows the create attempt).

5. Do **not** edit `CONTACT_TASK_CONFIG`, contact dispatch, gazer, or tracker. Do **not** add stub alternate handler names. Do **not** change `create_meteorite_job` / `land_meteorite` behavior.

## Execution contract

- Execute stages and steps in order; one commit per stage on epic worktree; push `git push origin HEAD:sub/AST-1414/AST-1517-create-contact-meteorite` after each stage.
- No files outside Files Changed.
- Ambiguity, missing `contact_task_gazer_scrape`, or `create_meteorite_job` signature drift → stop, comment on **AST-1517** with Stage blocked format, wait.
- Test tree / bible: Betty only — engineer does not edit `tests/` or `docs/test-bible/**`.

## Estimate

Confirm Chuckles estimate: 3 — agree
