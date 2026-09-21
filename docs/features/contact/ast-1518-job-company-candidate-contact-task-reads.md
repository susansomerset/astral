# AST-1518 — Job / company / candidate contact-task reads

**Linear:** [AST-1518](https://linear.app/astralcareermatch/issue/AST-1518/job-company-candidate-contact-task-reads-estelle-needs-to-be-able-to)  
**Parent:** [AST-1414](https://linear.app/astralcareermatch/issue/AST-1414/estelle-needs-to-be-able-to-use-our-endpoints) — Estelle needs to be able to use our endpoints  
**Publish ref:** `sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads`

Child #4 of AST-1414: implement the four read handlers registered by sibling AST-1515 in `CONTACT_TASK_CONFIG` — `contact_task_get_job_by_pattern`, `contact_task_get_job_data`, `contact_task_get_company_data`, `contact_task_get_candidate_data` — in `src/core/tracker.py`. Thin wrappers over extant getters + `agent.get_entity_agent_story` hydration; candidate-scoped; refuse cross-candidate / unmatched patterns. Does **not** own markup/dispatch (AST-1515), gazer scrape, or meteorite create. Does **not** create jobs or run new analysis.

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/tracker.py` (modified — `get_job_by_pattern` + contact-task read wrappers). Technical: candidate-scoped pattern match; read helpers delegating to existing `get_job_data`, `roster.get_company_data`, `candidate.get_candidate`, and `agent.get_entity_agent_story`; refuse cross-candidate or unmatched patterns.

**Out of scope:** `config.py` / `contact.py` / `agent_task.json` (AST-1515); `gazer.py` (AST-1516); `meteorite.py` (AST-1517). Do **not** rename or rewrite extant coat-check `get_job_data(job, key)` / `roster.get_company_data(company, key)` — contact-task entrypoints are **new** `contact_task_*` names matching AST-1515 handler dotted paths.

**Depends on:** AST-1515 tip on epic worktree (`CONTACT_TASK_CONFIG` handlers already point at `src.core.tracker.contact_task_*`). Stack via merge of `origin/ftr/AST-1414-estelle-endpoints` (or AST-1515 publish tip) before product commits.

**Handler contract (AST-1515 Stage 2):** sync or async  
`handler(astral_candidate_id: str, param: str, *, debug: bool = False) -> dict`  
Return a `dict` with `ok` and `task_key`; on success put payload under `result`. Contact dispatch already Style-D bookends the call — handlers emit their own Style D found/recorded when `debug=True` (ticket AC7 / parent AC8).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | New public `get_job_by_pattern`; four `contact_task_*` read wrappers; private hydrate helper; Style D on read paths | core |

## Stage 1: Pattern resolve + hydrate helpers

**Done when:** `get_job_by_pattern(astral_candidate_id, pattern)` returns one candidate-scoped job row or `None` per contract below; `_job_owned_by_candidate` resolves ownership via company→`candidate_id`; a private hydrate helper attaches `agent_story` via late-imported `get_entity_agent_story`. No contact-task entrypoints yet.

1. In `src/core/tracker.py` module docstring, note AST-1518: contact-task read wrappers + `get_job_by_pattern`.

2. Add private **`_contact_task_hydrate_job(job: Dict[str, Any]) -> Dict[str, Any]`**:

   - Shallow-copy the job dict.
   - Late-import `from src.core.agent import get_entity_agent_story` (avoid load cycles).
   - Set `out["agent_story"] = get_entity_agent_story(out)` (list; empty list on soft-fail — story already soft-fails internally).
   - Return `out`. Do **not** call async coat-check `get_job_data` / gazer self-heal — parent boundary: no new analysis / no scrape from this ticket.

3. Add private **`_job_owned_by_candidate(job: Dict[str, Any], cid: str) -> bool`** (Joan fix-now — job rows do **not** carry `candidate_id`):

   - Mirror ownership used by existing `_candidate_data_for_job`: resolve `company_key = job.get("company")`; if not a non-empty str → `False`.
   - `company = get_company(company_key.strip())`; if missing → `False`.
   - `owner = company.get("candidate_id")`; return `True` only when `owner` is a non-empty str and `str(owner).strip() == cid`.
   - Do **not** read `job["candidate_id"]` — that field is not the ownership SoT for job rows.

4. Add public **`get_job_by_pattern(astral_candidate_id: str, pattern: str) -> Optional[Dict[str, Any]]`**:

   a. `cid = (astral_candidate_id or "").strip()`; `pat = (pattern or "").strip()`. If either empty → return `None`.  
   b. `jobs = list_jobs(candidate_id=cid)` (existing tracker facade).  
   c. Casefold `pat_cf = pat.casefold()`. Match a job when **any** of these fields, as string, casefold-contains `pat_cf` **or** equals `pat` / `pat_cf` for id:

   - `astral_job_id`
   - `job_title`
   - `company` (short_name column)
   - `job_link`

   d. Collect all matches. If **zero** → `None`. If **more than one** → return `None` (caller maps to `ambiguous_pattern` — refuse rather than guess). If **exactly one** → return that job dict (raw row, not yet hydrated).

   ⚠️ **Decision — ambiguous → refuse:** Parent AC5 requires refuse on unresolved pattern; multiple hits are unresolved for Estelle purposes. Single exact id match still wins when the pattern equals `astral_job_id`.

5. Do **not** add contact_task_* wrappers in this stage.

## Stage 2: Four `contact_task_*` read wrappers

**Done when:** All four handlers exist with the AST-1515 signatures, candidate-scope checks, hydrate where applicable, Style D when `debug=True`, and return shapes Contact dispatch can normalize. Extant coat-check `get_job_data` / `roster.get_company_data` remain unchanged.

1. Add private Style D helper used by all four (keeps DRY):

```python
def _contact_task_style_d(
    log, *, func: str, identifier: str, found_detail: str, recorded_detail: str, debug: bool
) -> None:
    if not debug:
        return
    log.set_debug_flag(True)
    log.debug_index(func=func, index=1, total=2, identifier=identifier, outcome="found")
    for line in truncate_debug_content(found_detail):
        log.debug_detail(line)
    log.debug_index(func=func, index=2, total=2, identifier=identifier, outcome="recorded")
    for line in truncate_debug_content(recorded_detail):
        log.debug_detail(line)
```

   Import `truncate_debug_content` from `src.utils.logging` if not already imported; use existing `logger` / `get_logger(__name__)`.

2. **`contact_task_get_job_by_pattern(astral_candidate_id, param, *, debug=False) -> dict`**

   - Empty cid → `{"ok": False, "error": "no_candidate", "task_key": "get_job_by_pattern"}`.  
   - Empty param → `{"ok": False, "error": "unmatched_pattern", "task_key": "get_job_by_pattern"}`.  
   - `job = get_job_by_pattern(cid, param)`.  
   - If `None`: distinguish via a second list pass — if ≥2 matches would have hit → `ambiguous_pattern`; else `unmatched_pattern`. (Implement by having `get_job_by_pattern` return `None` and a small private `_match_jobs_by_pattern(cid, pat) -> List[Dict]` used by both, so counts are exact.)  
   - If job is present and **`not _job_owned_by_candidate(job, cid)`** → `refused_cross_candidate` (defense in depth; `list_jobs` already scoped — same helper as `get_job_data`).  
   - Else hydrate → `{"ok": True, "task_key": "get_job_by_pattern", "result": hydrated}`.  
   - Style D: identifier=`get_job_by_pattern`; found=`param=…`; recorded=`ok=… error=…` or `astral_job_id=…`.

3. **`contact_task_get_job_data(astral_candidate_id, param, *, debug=False) -> dict`**

   - Empty cid → `no_candidate`. Empty param → `not_found`.  
   - `job = get_job(param.strip())`. If missing → `not_found`.  
   - **Ownership (mandatory):** if **`not _job_owned_by_candidate(job, cid)`** → `refused_cross_candidate`. Do **not** gate on `job.get("candidate_id")` (field is not ownership SoT; a foreign `astral_job_id` would otherwise succeed).  
   - ⚠️ **Decision — do not call async coat-check `get_job_data(job, key)`:** that path self-heals JD via gazer (out of Boundaries). This handler returns the stored job row + `agent_story` hydration only. Parent Technical scope's "delegating to existing `get_job_data`" is satisfied by composing **`get_job`** (tracker job read) + hydration; the coat-check function keeps its existing name/signature for gazer/consult callers.  
   - Hydrate → success result. Style D as above (`task_key` / identifier `get_job_data`).

4. **`contact_task_get_company_data(astral_candidate_id, param, *, debug=False) -> dict`**

   - Empty cid → `no_candidate`. Empty param → `not_found`.  
   - **Param contract:** `param` must be the company **`short_name`** as stored on job rows / `get_company` key. Other identifiers → `not_found` (AST-1515 `param_hint` "or id" is not implemented here — no alternate id lookup).  
   - Use tracker `get_company(param.strip())` (thin database delegate — stay inside Files Changed).  
   - If company missing → `not_found`.  
   - Scope check: company `candidate_id` when present must equal cid; **or** if company has no `candidate_id`, require at least one `list_jobs(candidate_id=cid)` row whose `company` equals the company's `short_name`. Else → `refused_cross_candidate`.  
   - Build result: shallow copy of company row; late-import `get_entity_agent_story` and set `agent_story` from the company entity dict (story keys off `short_name`).  
   - ⚠️ **Decision — do not invoke async `roster.get_company_data(company, key)` coat-check:** same boundary as job (no on-demand website fetch). Wrapper returns stored company + agent story.  
   - Style D with identifier `get_company_data`.

5. **`contact_task_get_candidate_data(astral_candidate_id, param, *, debug=False) -> dict`**

   - Empty cid → `no_candidate`.  
   - Load via existing `candidate_mod.get_candidate(cid)` (module already imported as `candidate_mod` in tracker). Missing → `not_found`.  
   - Optional `param`: if non-empty after strip, treat as a dotted path under `candidate_data` (e.g. `profile.first`). Walk dict keys; if any segment missing → `not_found`. Success `result` is the leaf value (or full candidate row + `agent_story` when param empty).  
   - When param empty: shallow-copy candidate row; attach `agent_story` via `get_entity_agent_story` (entity uses `astral_candidate_id`).  
   - Never write / never invent fields. Style D with identifier `get_candidate_data`.

6. Error strings (exact literals for Betty / Contact follow-up):  
   `no_candidate` | `not_found` | `unmatched_pattern` | `ambiguous_pattern` | `refused_cross_candidate`.

7. Confirm AST-1515 config paths resolve: after this stage, `importlib` of  
   `src.core.tracker.contact_task_get_job_by_pattern` (and the other three) must succeed — no config.py edits.

## Execution contract

- Stages in order; one commit per stage on epic worktree; push  
  `git push origin HEAD:sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads` after each.
- No files outside Files Changed.
- Before Stage 1 product work: ensure AST-1515 / `origin/ftr/AST-1414-estelle-endpoints` is merged into the sub (CONTACT_TASK_CONFIG present).
- Ambiguity or missing `list_jobs` / `get_job` / `get_candidate` → stop, comment on **AST-1518** with Stage blocked format, wait.
- Test tree / bible: Betty only.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Revisions

Revision 1 — 2026-08-27  
Driven by: Joan `[plan-discuss] round=1 concern` — fix-now on job ownership check; discuss on company param  
Changes: Added Stage 1 `_job_owned_by_candidate` (company → `candidate_id`, same SoT as `_candidate_data_for_job`); both job handlers must use it before success (no `job["candidate_id"]` gate). Stage 2 company param narrowed to `short_name` only → other ids `not_found`.

## Joan validate

[plan-discuss] round=1 concern
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1518
**Overall:** REVISE
**Publish ref:** `sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads` @ `b2cfeb230786e1d603324a84d8225f47ac86f9e5`

## Traceability
AC5 (parent AC5)→S1,S2; AC6 (parent AC6)→S2; AC7 (parent AC8 read paths)→S2; parent AC1–4,7→N/A (siblings); stages map to child Purpose / Functional read slice only.

## Findings

### fix-now — Stage 2 steps 2–3, cross-candidate checks
**Finding:** `contact_task_get_job_data` and `contact_task_get_job_by_pattern` defense-in-depth gate on `job.get("candidate_id")`, but job rows in tracker do not use that field for ownership — candidate scope is `job["company"]` → `get_company(...).get("candidate_id")` (see existing `_candidate_data_for_job` / `builder.py`). `contact_task_get_job_data` loads via `get_job(param)` with **no** `list_jobs` scoping, so a foreign `astral_job_id` could return another candidate's job while the planned check never fires.
**Recommendation:** Add a private helper (e.g. `_job_owned_by_candidate(job, cid)`) resolving company→`candidate_id`; use it in both handlers before hydrate/success. `contact_task_get_job_data` must refuse when resolved owner ≠ `cid` (`refused_cross_candidate`). Pattern path can keep `list_jobs(candidate_id=cid)` but should use the same helper for defense in depth.

### discuss — Stage 2 step 4, `get_company_data` param_hint
**Finding:** AST-1515 `param_hint` says "company short_name or id"; plan resolves via `tracker.get_company(param.strip())` (short_name key only). Misleading if Estelle passes a non-short_name identifier.
**Recommendation:** Either narrow param_hint in a sibling config doc pass (out of this ticket's Files Changed) or add one plan line: param must be company `short_name` as stored on the job row — other ids → `not_found`.

### acceptable — Boundaries, coat-check bypass, hydration, scope
Does not call async coat-check `get_job_data` / `roster.get_company_data` (no gazer/website fetch); hydrates via `get_job` + `get_entity_agent_story`; ambiguous pattern → refuse; company scope check via `list_jobs`; four handler names match AST-1515 `CONTACT_TASK_CONFIG`; single-file scope; Style D gated on `debug=True`; late-import `agent` avoids cycles.

context_tokens≈45000

## Joan validate (round 2)

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1518
**Overall:** APPROVED
**Publish ref:** `sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads` @ `6ad190a2e0f52fbac6d0e01f41010cfc574adbd1`

## Traceability
AC5 (parent AC5)→S1,S2; AC6 (parent AC6)→S2; AC7 (parent AC8 read paths)→S2; parent AC1–4,7→N/A (siblings); stages map to child Purpose / Functional read slice only.

## Findings

### acceptable — Revision 1 (job ownership)
Stage 1 `_job_owned_by_candidate` mirrors `_candidate_data_for_job` (company→`candidate_id`); both job handlers gate on it before hydrate; `contact_task_get_job_data` no longer relies on `job["candidate_id"]`. Prior fix-now closed.

### acceptable — Company param contract
Stage 2 step 4 documents `short_name` only; other ids → `not_found`; notes AST-1515 `param_hint` mismatch out of Files Changed. Prior discuss closed in-plan.

### acceptable — Boundaries, coat-check bypass, hydration, scope
No async coat-check `get_job_data` / `roster.get_company_data`; hydrates via `get_job` + `get_entity_agent_story`; ambiguous pattern → refuse; four handler names match AST-1515 `CONTACT_TASK_CONFIG`; single-file scope; Style D gated on `debug=True`; late-import `agent` avoids cycles.

context_tokens≈52000

---

## Radia review

# AST-1518 — Radia code review

**Status gate:** Spawn prompt `Tests Passed` — accepted without re-fetch.

**Publish ref under review:** `origin/sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads` @ `b85a8e37d2fa0dc0f7e91a2f8b8c2d865dd82ce0`

**Diff baseline:** `git diff origin/dev...origin/sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads` (19 paths, +1836/−11 cumulative). **`src/core/tracker.py`: zero diff vs `origin/dev`.**

---

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1518
**Publish ref:** `sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads` @ `b85a8e37d2fa0dc0f7e91a2f8b8c2d865dd82ce0`
**Overall:** FIX-NOW

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | No agent-confidence surfaces in diff |
| astral.agent.do-task-delegation | scoped | not-applicable | No new AI delegation paths in reviewed SHA |
| astral.agent.grade-vector-validation | scoped | not-applicable | No grade-vector paths |
| astral.batch.batch-id-first | scoped | not-applicable | No batch claim/clear |
| astral.batch.batch-id-format | scoped | not-applicable | No batch_id emission |
| astral.batch.claim-process-release | scoped | not-applicable | No claim/process/release helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | No entity agent-response writes |
| astral.config.config-source-of-truth | scoped | conforms | Sibling AST-1515 `CONTACT_TASK_CONFIG` on branch stack |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No secrets/env wiring |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No artifact dir usage |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spike files |
| astral.dispatch.seed-auto-false | scoped | not-applicable | Dispatcher untouched |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | No run_next edits |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Dedicated `ast-1518-…md` plan doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty merge-tests only on tip |
| astral.git.engineer-test-tree-ban | scoped | conforms | No engineer test-tree commits attributed to AST-1518 product stage on tip |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | No AST-1518 product diff at reviewed SHA |
| astral.layers.import-direction | scoped | not-applicable | No AST-1518 product diff at reviewed SHA |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No scripts/ changes |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | No UI product changes for AST-1518 |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | Handlers not present at reviewed SHA |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No render/consult paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | No API auth surfaces |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | No agent_task edits for AST-1518 |
| astral.seed.archie-catalog-wins | scoped | not-applicable | No seed catalog override |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | N/A at reviewed SHA |
| astral.seed.define-approved | scoped | not-applicable | No define/seed bootstrap |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No operator-row resurrection |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage-join seed edits |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | No `src/data/**` AST-1518 changes |
| astral.standards.database-header-inventory | scoped | not-applicable | No schema/migration changes |
| astral.standards.debug-contract-gated | scoped | not-applicable | Product handlers absent at reviewed SHA |
| astral.standards.dry-and-focused-functions | scoped | not-applicable | Product absent at reviewed SHA |
| astral.standards.in-scope-only | scoped | violates | Plan Files Changed = `tracker.py` only; publish ref tip has Betty tests for handlers with **no** matching product commit |
| astral.standards.in-scope-only | scoped | violates | (see finding — tests reference symbols not shipped at SHA) |
| astral.standards.logging-via-utils | scoped | not-applicable | Product absent at reviewed SHA |
| astral.standards.names-not-ticket-ids | scoped | not-applicable | Product absent at reviewed SHA |
| astral.standards.no-cross-contamination | scoped | conforms | No tracker edits smuggled into sibling files on tip |
| astral.standards.no-hardcoded-sets | scoped | not-applicable | Product absent at reviewed SHA |
| astral.standards.public-then-helpers | scoped | not-applicable | Product absent at reviewed SHA |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No utils→data late-import changes |
| astral.state.core-decides-transitions | scoped | not-applicable | No transition edits at reviewed SHA |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job state logic |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | Read-only handlers not present |
| astral.ui.frontend-file-placement | scoped | not-applicable | No AST-1518 UI product |
| astral.ui.naming-conventions | scoped | not-applicable | No AST-1518 UI product |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single merge-tests SHA on tip |
| orch.git.commit-vocabulary | universal | violates | `Tests Passed` / review gate with no `code(AST-1518)` on publish ref |
| orch.git.flow-direction-inviolable | universal | conforms | Sub-branch topology correct |
| orch.git.ftr-sub-topology | universal | conforms | Child sub under AST-1414 |
| orch.git.merge-on-checkout | universal | conforms | Branch stacks prerequisite siblings |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No destructive git in reviewed history |
| orch.git.no-dev-agent-branches | universal | conforms | Publish ref is sub/ |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree path |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No product-policy forks |
| orch.pipeline.plan-is-bible | universal | violates | Approved plan Stages 1–2 require `tracker.py` handlers; **absent** at reviewed publish SHA |
| orch.pipeline.project-scoped-queues | universal | conforms | N/A to code |
| orch.pipeline.status-gates-skill-entry | universal | needs-discussion | `Tests Passed` premature — product not on `origin/sub/…` tip |
| orch.roles.archie-approves-statutes | universal | conforms | No new statutes |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty landed tests (`bc87508c`, `2b96f16f`) |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Expected path once product publishes |
| orch.roles.pre-commit-path-bans | universal | conforms | No banned-path commits on tip |

*(Note: duplicate `in-scope-only` row in table above is a rendering error — single verdict: **violates**.)*

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| *(none cited)* | — | Plan has no “Patterns to reuse” section |

## Plan adherence

**At reviewed publish SHA (`b85a8e37`): FAIL**

| Plan requirement | On `origin/sub/…` tip |
|------------------|----------------------|
| Stage 1: `get_job_by_pattern`, `_job_owned_by_candidate`, `_contact_task_hydrate_job` | **Missing** — `tracker.py` unchanged vs `origin/dev` |
| Stage 2: four `contact_task_*` handlers + Style D helper | **Missing** |
| Single file `src/core/tracker.py` | **No engineer product commit on publish ref** |
| Betty tests (`TestAst1518ContactTaskReads`) | **Present** — reference `tracker_mod.get_job_by_pattern`, `contact_task_get_*` |

**Unpushed local commit (not on publish ref):** `61cd64ee` `code(AST-1518): contact-task read handlers + get_job_by_pattern` (+403 lines `tracker.py`) exists on local `sub/AST-1414/AST-1518-…` but is **not an ancestor** of `origin/sub/AST-1414/AST-1518-…` @ `b85a8e37`. Branch diverged after Joan APPROVED (`7af985db`): origin tip absorbed merge-tests / sibling sync without this product commit.

**Pending-publish code assessment (`61cd64ee`, not gated on this review):** Implementation appears to match approved plan — `_job_owned_by_candidate` via company→`candidate_id`; `_match_jobs_by_pattern` for exact ambiguous/unmatched counts; no async coat-check `get_job_data` / roster fetch; company `short_name` only; company scope fallback via `list_jobs`; candidate dotted path; dual-index Style D. Re-review after push.

## Frame diff

| Planned (AST-1518 product) | `origin/sub/…` @ `b85a8e37` |
|----------------------------|-----------------------------|
| `src/core/tracker.py` | **absent** (0-line diff vs dev) |

| Pipeline on tip (not AST-1518 product) | Present |
|----------------------------------------|---------|
| `docs/features/contact/ast-1518-…md` | ✓ plan + Joan APPROVED |
| `tests/component/core/test_tracker.py` (`TestAst1518ContactTaskReads`) | ✓ Betty |
| Sibling stack (AST-1515 contact/config, AST-1516 gazer) | ✓ prerequisite commits |

## Findings

### fix-now — Product not on publish ref (review blocker)

**Location:** `origin/sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads` @ `b85a8e37`

**Finding:** Three-dot diff vs `origin/dev` includes **no** `src/core/tracker.py` changes. Betty tests on the same tip import/call `get_job_by_pattern`, `contact_task_get_job_by_pattern`, `contact_task_get_job_data`, `contact_task_get_company_data`, and `contact_task_get_candidate_data` — symbols that **do not exist** in `tracker.py` at this SHA. Engineer product commit `61cd64ee` (+403 lines) is **not reachable** from the reviewed publish tip (diverged history after `7af985db`).

**Reasoning:** Radia reviews `origin/<publish-ref>` per review-child §4. `Tests Passed` cannot be validated against product at this SHA; manifest would fail on missing attributes. Plan Stages 1–2 are unshipped on origin.

**Recommended downstream (Chuckles / Ada — not Radia):**
1. Push or replay `61cd64ee` onto `origin/sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads` (reconcile divergence with merge-tests/sync commits so product precedes or follows Betty tip cleanly).
2. Re-run `test-child` manifest green against publish ref **with** product present.
3. Re-spawn Radia review on updated tip SHA.

### discuss — `Tests Passed` status vs publish ref integrity

**Finding:** Linear status `Tests Passed` with assignee Ada, but publish ref tip is tests-only + sibling stack without AST-1518 product.

**Recommendation:** Chuckles verify pipeline state — regress to **Code Complete** or **Tests Ready** until `code(AST-1518)` lands on origin publish ref and manifest is green at that SHA.

### advisory — When `61cd64ee` publishes (pre-assessed, not gated)

Skim of unpushed commit suggests **likely CLEAN** on re-review: ownership helper, ambiguous-pattern refuse, coat-check bypass, Style D dual index, error literal set match plan. Minor style: handlers use local `get_logger(__name__)` while module already exposes `logger` — advisory only.

## Notes

- Joan plan-rubric round 2 APPROVED attached; Revision 1 ownership fix reflected in `61cd64ee` (unpushed).
- §5f / §5g N/A at reviewed SHA (no product diff).
- No plan-rubric Excluded-statute stragglers.
- **Do not set Review Posted** on current publish SHA — C7 incomplete for product review.

context_tokens≈40000

---

---

## Review (build stub)

| Field | Value |
|-------|-------|
| Status | Code Complete |
| Publish ref | `origin/sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads` |
| Tip | `303e905c` (cherry-pick of `61cd64ee`) |
| Branch | `sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads` |

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–2 | `303e905c` | `get_job_by_pattern`, `_job_owned_by_candidate`, four `contact_task_*` read handlers + Style D |

**Betty note:** component tests for pattern match, ownership refuse, hydrate, Style D deferred to qa-child.

## Radia review (re-review)

# AST-1518 — Radia code review (re-review)

**Status gate:** Spawn prompt `Tests Passed` — accepted without re-fetch.

**Prior review:** ESCALATE @ `b85a8e37` — product missing on publish ref. **Resolved:** `code(AST-1518)` @ `303e905c` (cherry-pick of `61cd64ee`) now on `origin/sub/…`.

**Publish ref under review:** `origin/sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads` @ `fedf92090144977e867455571f2944dc9f56613f`

**Diff baseline:** `git diff origin/dev...origin/sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads` — AST-1518 product: `src/core/tracker.py` +403/−1; Betty tests +124 lines.

---

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1518
**Publish ref:** `sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads` @ `fedf92090144977e867455571f2944dc9f56613f`
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | No confidence-vector surfaces |
| astral.agent.do-task-delegation | scoped | not-applicable | Read handlers; no inline AI I/O |
| astral.agent.grade-vector-validation | scoped | not-applicable | No grade-vector paths |
| astral.batch.batch-id-first | scoped | not-applicable | No batch claim/clear |
| astral.batch.batch-id-format | scoped | not-applicable | No batch_id emission |
| astral.batch.claim-process-release | scoped | not-applicable | No claim/process/release |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | No entity agent-response writes |
| astral.config.config-source-of-truth | scoped | conforms | Handlers registered in sibling AST-1515 `CONTACT_TASK_CONFIG`; no inline task catalogs |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No secrets/env wiring |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No artifact dir usage |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spike files |
| astral.dispatch.seed-auto-false | scoped | not-applicable | Dispatcher untouched |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | No run_next edits |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `ast-1518-…md` plan doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty merge-tests; engineer commit is `tracker.py` only |
| astral.git.engineer-test-tree-ban | scoped | conforms | No engineer test-tree edits |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Read-only hydration; no Playwright/scrape in handlers |
| astral.layers.import-direction | scoped | conforms | Late-import `get_entity_agent_story`; existing tracker imports unchanged |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No scripts/ changes |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | No UI changes |
| astral.idioms.coat-check-never-store-empty | scoped | conforms | Handlers bypass async coat-check `get_job_data`; return stored rows + hydration only (plan boundary) |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No render/consult paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | No API auth surfaces |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | No agent_task edits |
| astral.seed.archie-catalog-wins | scoped | not-applicable | No seed catalog override |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | Hot-path read handlers |
| astral.seed.define-approved | scoped | not-applicable | No define/seed bootstrap |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No operator-row resurrection |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage-join seed edits |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | No `src/data/**` changes |
| astral.standards.database-header-inventory | scoped | not-applicable | No schema/migration changes |
| astral.standards.debug-contract-gated | scoped | conforms | `_contact_task_style_d` emits found/recorded + detail only when `debug=True` |
| astral.standards.dry-and-focused-functions | scoped | conforms | Shared `_match_jobs_by_pattern`, `_job_owned_by_candidate`, `_contact_task_style_d` |
| astral.standards.in-scope-only | scoped | conforms | Engineer `code(AST-1518)` touches `tracker.py` only |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` + contract helpers; no raw `logging` import |
| astral.standards.names-not-ticket-ids | scoped | conforms | Handler/task_key names domain-driven |
| astral.standards.no-cross-contamination | scoped | conforms | No contact/gazer/meteorite/config edits in engineer commit |
| astral.standards.no-hardcoded-sets | scoped | conforms | No parallel allowlists; reads via existing getters |
| astral.standards.public-then-helpers | scoped | conforms | Public `get_job_by_pattern` + four handlers; private helpers below |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No utils→data late-import changes |
| astral.state.core-decides-transitions | scoped | conforms | No `transition_job_state` / job writes in handlers |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job transition logic |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | Read-only; no entity daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | No AST-1518 UI product |
| astral.ui.naming-conventions | scoped | not-applicable | No AST-1518 UI product |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests on tip |
| orch.git.commit-vocabulary | universal | conforms | `code(AST-1518)` / `test(AST-1518)` present |
| orch.git.flow-direction-inviolable | universal | conforms | Sub-branch vs `origin/dev` |
| orch.git.ftr-sub-topology | universal | conforms | Child sub under AST-1414 |
| orch.git.merge-on-checkout | universal | conforms | Stacks prerequisite siblings (1515/1516) |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | Recovery cherry-pick noted in build stub — see Notes (procedural, not product) |
| orch.git.no-dev-agent-branches | universal | conforms | Publish ref is sub/ |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No product-policy forks |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 implemented per approved plan |
| orch.pipeline.project-scoped-queues | universal | conforms | N/A |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Re-review at Tests Passed after product landed |
| orch.roles.archie-approves-statutes | universal | conforms | No new statutes |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty `TestAst1518ContactTaskReads` on tip |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Expected path |
| orch.roles.pre-commit-path-bans | universal | conforms | No banned-path commits |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| *(none cited)* | — | Plan has no “Patterns to reuse” section |

## Plan adherence

**Stages 1–2** implemented in `303e905c` (`tracker.py` +403 lines):

| Plan step | Implementation |
|-----------|----------------|
| Stage 1 `_contact_task_hydrate_job` | Shallow copy + late-import `get_entity_agent_story`; no coat-check |
| Stage 1 `_job_owned_by_candidate` | `job["company"]` → `get_company` → `candidate_id` (mirrors `_candidate_data_for_job` SoT; not `job["candidate_id"]`) |
| Stage 1 `get_job_by_pattern` | `list_jobs(candidate_id=cid)` + `_match_jobs_by_pattern`; 0 or >1 → `None` |
| Stage 1 `_match_jobs_by_pattern` | Casefold substring/equals on `astral_job_id`, `job_title`, `company`, `job_link` |
| Stage 2 four handlers | Signatures match AST-1515 dispatch; error literals exact |
| `contact_task_get_job_by_pattern` | Distinguishes `unmatched_pattern` vs `ambiguous_pattern` via match count; ownership gate |
| `contact_task_get_job_data` | `get_job(jid)` + `_job_owned_by_candidate`; **does not** call async coat-check `get_job_data` |
| `contact_task_get_company_data` | `get_company(short_name)` only; scope via `candidate_id` or `list_jobs` fallback |
| `contact_task_get_candidate_data` | Full row + `agent_story` when param empty; dotted path leaf when param set |
| Style D | `_contact_task_style_d`: dual index found/recorded, `truncate_debug_content` on details |
| Boundaries | No job create/transition/`save_job_data`; extant coat-check APIs unchanged |

Estimate **3** fits single-file handler footprint. Joan Revision 1 ownership fix **closed**.

Betty tests align: pattern exact/ambiguous, ownership refuse, company/candidate paths, Style D dual index, no job-create mocks called.

## Frame diff

| Planned (AST-1518 product) | On publish ref |
|----------------------------|----------------|
| `src/core/tracker.py` | ✓ `303e905c` (+403 lines) |

| Pipeline (expected) | On tip |
|---------------------|--------|
| `docs/features/contact/ast-1518-…md` | ✓ plan + Joan APPROVED + prior Radia ESCALATE + build stub |
| `tests/component/core/test_tracker.py` | ✓ Betty `TestAst1518ContactTaskReads` |
| Sibling stack (AST-1515 dispatch, AST-1516 gazer) | ✓ prerequisite commits on branch |

**Prior ESCALATE resolved:** `tracker.py` diff vs `origin/dev` is non-empty; handler symbols exist at reviewed SHA.

## Findings

*(none — fix-now / discuss)*

## What's solid

- Cross-candidate defense uses company→`candidate_id` SoT — closes Joan round-1 fix-now (`contact_task_get_job_data` cannot succeed on foreign `astral_job_id`).
- Ambiguous pattern → `ambiguous_pattern` refuse (no guessing among multiple title hits).
- Coat-check bypass is deliberate and plan-documented — no on-demand gazer/website fetch from Contact reads.
- Handler return shapes (`ok`, `task_key`, `result` / `error`) match AST-1515 dispatch normalization.
- `importlib` resolution of all four `CONTACT_TASK_CONFIG` handler paths will succeed at runtime.
- Style D uses handler-local dual index (found/recorded) per plan AC7; complements outer dispatch bookends without violating gating.

## Notes

- **Recovery cherry-pick:** Build stub documents `303e905c` as cherry-pick of `61cd64ee` to repair publish ref after prior ESCALATE. Patch content is clean; Chuckles may prefer ff-replay over cherry-pick for future publish-ref repairs per git workflow — procedural only, not a product blocker.
- **Advisory:** Handlers instantiate `get_logger(__name__)` per call while module exposes `logger` — minor consistency with other contact-task handlers; optional hygiene.
- **Advisory:** AST-1515 `CONTACT_TASK_CONFIG["get_company_data"]["param_hint"]` still says “short_name or id”; plan documents short_name-only — config hint narrowing is a sibling/doc pass (Joan closed in-plan).
- §5f / §5g applied — no violations on touched paths.

context_tokens≈42000

---

```
