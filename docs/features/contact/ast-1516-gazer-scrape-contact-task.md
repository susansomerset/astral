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

## Review (build stub)

| Field | Value |
|-------|-------|
| Status | Code Complete |
| Publish ref | `origin/sub/AST-1414/AST-1516-gazer-scrape-contact-task` |
| Tip | `73ef792f` |
| Branch | `sub/AST-1414/AST-1516-gazer-scrape-contact-task` |

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `73ef792f` | `contact_task_gazer_scrape` — Playwright scrape + `_classify_jd` → page_status |

**Betty note:** component tests for handler payload shape, cookie/bot→blocked map, Style D on debug=True, and no job create deferred to qa-child.

## Radia review

# AST-1516 — Radia code review

**Status gate:** Spawn prompt `Tests Passed` — accepted without re-fetch.

**Publish ref:** `origin/sub/AST-1414/AST-1516-gazer-scrape-contact-task` @ `dd66a92370187683f03ff771e55a73f1ef024041`

**Diff baseline:** `git diff origin/dev...origin/sub/AST-1414/AST-1516-gazer-scrape-contact-task` (19 paths, +1836/−11 cumulative on branch tip). **Engineer product commit** `73ef792f`: `src/core/gazer.py` only (+105/−2).

---

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1516
**Publish ref:** `sub/AST-1414/AST-1516-gazer-scrape-contact-task` @ `dd66a92370187683f03ff771e55a73f1ef024041`
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | No confidence-vector surfaces |
| astral.agent.do-task-delegation | scoped | not-applicable | Handler is Playwright scrape orchestration, not inline AI I/O |
| astral.agent.grade-vector-validation | scoped | not-applicable | No grade-vector paths |
| astral.batch.batch-id-first | scoped | not-applicable | No batch claim/clear |
| astral.batch.batch-id-format | scoped | not-applicable | No batch_id emission |
| astral.batch.claim-process-release | scoped | not-applicable | No claim/process/release helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | No entity agent-response writes |
| astral.config.config-source-of-truth | scoped | conforms | Sibling AST-1515 `CONTACT_TASK_CONFIG` on branch; handler path unchanged |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No secrets/env wiring in gazer handler |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No artifact dir usage |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spike files |
| astral.dispatch.seed-auto-false | scoped | not-applicable | Dispatcher untouched |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | No run_next edits |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Dedicated `ast-1516-…md` plan doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty merge-tests; engineer commit is `src/core/gazer.py` only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Hedy did not commit tests/bible (Betty `8177033c`) |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Playwright I/O via `src.external.playwright`; core orchestrates only |
| astral.layers.import-direction | scoped | conforms | `gazer.py` imports data/external/utils per existing module pattern |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No scripts/ changes |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | No UI changes |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | No coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No render/consult paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | No API auth surfaces |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | No agent_task edits in AST-1516 engineer commit |
| astral.seed.archie-catalog-wins | scoped | not-applicable | No seed catalog override |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | Hot-path handler only |
| astral.seed.define-approved | scoped | not-applicable | No define/seed bootstrap |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No operator-row resurrection |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage-join seed edits |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | No `src/data/**` changes in engineer commit |
| astral.standards.database-header-inventory | scoped | not-applicable | No schema/migration changes |
| astral.standards.debug-contract-gated | scoped | conforms | Style D in handler gated on `debug=True`; uses contract helpers + `truncate_debug_content` |
| astral.standards.dry-and-focused-functions | scoped | conforms | Reuses `extract_page_scrape_contract`, `_classify_jd`, `collapse_consecutive_blank_lines` |
| astral.standards.in-scope-only | scoped | conforms | Engineer commit limited to `gazer.py` per plan Files Changed |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` / contract methods; scrape failures use `log.warning` (normal, not debug contract) |
| astral.standards.names-not-ticket-ids | scoped | conforms | Handler/key names are domain-driven |
| astral.standards.no-cross-contamination | scoped | conforms | No dispatch/config/meteorite/tracker edits in engineer commit |
| astral.standards.no-hardcoded-sets | scoped | conforms | `_CONTACT_PAGE_STATUS` is handler-local contact surface map, not a parallel task catalog |
| astral.standards.public-then-helpers | scoped | conforms | Public async handler; `_fail` nested helper scoped to handler |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No utils→data late-import changes |
| astral.state.core-decides-transitions | scoped | conforms | Handler explicitly avoids `transition_job_state` / job writes |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job state logic |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | Single-URL scrape; no entity daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | No frontend product changes in engineer commit |
| astral.ui.naming-conventions | scoped | not-applicable | No UI files in engineer commit |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single merge-tests SHA on publish ref tip |
| orch.git.commit-vocabulary | universal | conforms | `code(AST-1516)` / `test(AST-1516)` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Work on `sub/AST-1414/…`, diff vs `origin/dev` |
| orch.git.ftr-sub-topology | universal | conforms | Child sub-branch under AST-1414 parent |
| orch.git.merge-on-checkout | universal | conforms | Branch stacks prerequisite AST-1515 commits (expected dependency) |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | Linear stage history |
| orch.git.no-dev-agent-branches | universal | conforms | Publish ref is sub/, not agent branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in `astral-AST-1414` worktree |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No product-policy forks |
| orch.pipeline.plan-is-bible | universal | conforms | Handler matches approved Stage 1 line-by-line |
| orch.pipeline.project-scoped-queues | universal | conforms | N/A to code |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No new statutes |
| orch.roles.betty-owns-test-tree | universal | conforms | Component tests/bible from Betty merge |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Hedy |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Expected handoff path |
| orch.roles.pre-commit-path-bans | universal | conforms | No banned-path commits in engineer stage |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| *(none cited)* | — | Plan has no “Patterns to reuse” section; implementation reuses existing gazer Playwright + `_classify_jd` shapes informally |

## Plan adherence

Stage 1 fully implemented in `73ef792f`:

- Module docstring In-scope lists `contact_task_gazer_scrape`.
- Imports extended: `close_page`, `extract_page_scrape_contract`, `truncate_debug_content`.
- `_CONTACT_PAGE_STATUS` collapses `cookie`/`bot` → `blocked` without mutating batch `_JD_ERROR_STATES`.
- Handler placed in labeled section before `# ---- Process batch`, after `scrape_one`.
- Async signature `(astral_candidate_id, param, *, debug=False)` matches AST-1515 dispatch.
- Validation: `url_required`, scheme fix, `no_connectivity` — all return `ok=False` dicts, no raise.
- Scrape: `create_browser_context` → `get_page` → `extract_page_scrape_contract` → `close_page` in `finally`.
- Exception path: warning + error dict (turn stays alive via dispatch).
- Success payload includes all required keys plus raw `classification`.
- Style D when `debug=True`: single index with `func="gazer.contact_task_gazer_scrape"`, detail lines for `final_url`/`visible_chars`/`links_count`, truncated visible text sample.
- No job create/transition/`save_job_data` — verified in Betty tests.

Estimate **3** fits single-file handler footprint. No edits to `CONTACT_TASK_CONFIG`, contact dispatch, meteorite, or tracker in engineer commit.

## Frame diff

| Planned (AST-1516 product) | Engineer commit |
|----------------------------|-----------------|
| `src/core/gazer.py` | ✓ `contact_task_gazer_scrape` + imports + `_CONTACT_PAGE_STATUS` |

| Pipeline (expected) | On branch tip |
|---------------------|---------------|
| `docs/features/contact/ast-1516-…md` | ✓ plan + build stub |
| `docs/test-bible/core/gazer.md` + `tests/component/core/test_gazer.py` | ✓ Betty `8177033c` |

| Cumulative on publish ref (not AST-1516 engineer scope) | Present |
|--------------------------------------------------------|---------|
| AST-1515 product (`contact.py`, `config.py`, `agent_task.json`) | ✓ prerequisite stack |
| AST-1518 plan doc + Betty tracker tests | ✓ sibling stacking on branch tip — partition at merge-child |

No unplanned files in **`code(AST-1516)`** commit.

## Findings

*(none — fix-now / discuss)*

## What's solid

- Handler closes the AST-1515 `handler_unavailable` gap for `gazer_scrape` once this lands on ftr with dispatch framework.
- Playwright boundary clean: all navigation/DOM in external; core composes contract + classifier only.
- `_CONTACT_PAGE_STATUS` gives Estelle-facing `page_status` while preserving raw `classification` for backend trace — matches parent AC2 language.
- Error paths return structured dicts (`url_required`, `no_connectivity`, exception string) — contact turn survives per plan.
- Style D obeys AST-538 on touched path: gated, single index, truncated content via `truncate_debug_content`.
- Betty coverage: status map, blank URL, connectivity fail, scheme fix, success payload keys, cookie/bot→blocked, exception dict, Style D on success, explicit assertions that `save_job_data` / `transition_job_state` / `create_meteorite_job` are not called.

## Recommended actions (downstream — not Radia blockers)

- **Chuckles / merge-child:** Branch tip diff is cumulative (AST-1515 + AST-1518 Betty artifacts + AST-1516). Partition sibling ownership when merging to `origin/ftr/AST-1414-estelle-endpoints`; do not attribute AST-1518 tracker tests to AST-1516 review findings.
- **UAT (Susan):** End-to-end with live Playwright — confirm `page_status=blocked` reads naturally in Estelle follow-up narrative when `_classify_jd` returns cookie/bot on real job boards.

## Notes

- Joan plan-rubric APPROVED attached; no Excluded-statute stragglers.
- §5f (debug contract) and §5g (external cleanliness) applied to `gazer.py` diff — no violations.
- Advisory only: adjacent `scrape_one` still uses `page.close()` while handler uses `close_page(page)` — pre-existing inconsistency in same file, out of AST-1516 scope; optional hygiene if a future gazer cleanup ticket exists.

context_tokens≈38000

---

```
[code-rubric] PROCEED (Commit: dd66a923) Gazer scrape handler clean
```
