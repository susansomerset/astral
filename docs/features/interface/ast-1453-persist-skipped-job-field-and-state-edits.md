<!-- linear-archive: AST-1453 archived 2026-09-09 -->

## Linear archive (AST-1453)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1453/persist-skipped-job-field-and-state-edits-when-a-job-is-in-a-skipped  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1446 — When a job is in a Skipped state, make all fields editable  
**Blocked by / blocks / related:** parent: AST-1446; blocks: AST-1454

### Description

## What this implements

Authenticated persist for title, link, and job description on jobs whose current state is skipped; state changes use the existing job transition path with prior-state enforcement. API tells the client whether the job is field-editable and which states are legal next. Rejects edits when the job is not skipped. Does not own the Job Detail form chrome (#2).

## Citations

`pattern.state.entity-state-transitions`, `pattern.ui.admin-endpoint`, `pattern.config.config-block`, `astral.state.job-prior-states-enforced`, `astral.state.core-decides-transitions`, `astral.layers.ui-config-driven-business-logic`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.standards.no-hardcoded-sets`, `astral.layers.import-direction`.

## Acceptance criteria

- [X] Open a job whose state is a skipped state: GET returns `fields_editable` and `legal_next_states` (editable form controls → sibling #2 / AST-1454); agent story tabs remain non-editable chrome.
- [X] Save (PUT) persists title, link, and job description; reload of Job Detail via GET shows the saved values (Skipped list after refresh once chrome wires).
- [X] A skipped job with no job description still accepts a job-description write; saving a pasted description persists it.
- [X] `legal_next_states` lists only legal successors; PUT with a legal `state` moves the job through `transition_job_state` (history recorded). An illegal target is rejected (409) and the job stays in its current state (field edits already applied).
- [X] After a save that leaves a skipped state, GET shows non-skipped state / `fields_editable=false`; job leaves Skipped list on refresh.
- [X] Open a job that is not in a skipped state: `fields_editable=false`, `legal_next_states=[]`; PUT rejected with 409 (title/link/JD/state remain display-only as today until chrome).

## Boundaries

- [X] Does not own Job Detail form chrome (sibling #2).
- [X] Does not waive prior-state law.
- [X] Does not unlock non-skipped jobs.
- [X] Does not auto-re-run consult, scrape, or dispatch.
- [X] Does not change bulk Retry, Skip This Job, Copy, or list-row Skip.

## Notes for planning

Estimate: 3. After persist exists, #2 wires the modal.

### Comments

#### radia — 2026-08-24T23:06:22.438Z
[code-rubric] PROCEED (Commit: 23a69171) skipped-job persist clean

#### betty — 2026-08-24T22:29:29.420Z
`origin/sub/AST-1446/AST-1453-persist-skipped-job-field-and-state-edits` @ `23a691710ee3ed4aea4959161d21cc70fa6e0516` · skipped persist coverage

#### chuckles — 2026-08-24T22:14:19.556Z
[agent-busy-timeout] blocked: Cursor conversation still busy after 20m call-wait (spawn=`6b38f971`, attempts=14).
- parent: `AST-1446`
- agent: **Joan** role=validate `validate-plan` on `AST-1453`
- AGENT_SESSION: `7219634c-bc1b-47c3-bc3f-b2cb04ac5901`

Do **not** `agent create-chat` and do **not** treat this as `[thread-missing]` — the Thread UUID is fine; another run held it.

#### ada — 2026-08-19T20:15:56.349Z
`origin/sub/AST-1446/AST-1453-persist-skipped-job-field-and-state-edits` @ `147c59ae1dcf95e75ada48b22cc7454ac1592c1b` · persist API plan ready

---

# AST-1453 — Persist skipped-job field and state edits

**Linear:** [AST-1453](https://linear.app/astralcareermatch/issue/AST-1453/persist-skipped-job-field-and-state-edits-when-a-job-is-in-a-skipped)  
**Parent:** [AST-1446](https://linear.app/astralcareermatch/issue/AST-1446/when-a-job-is-in-a-skipped-state-make-all-fields-editable)  
**Publish ref:** `sub/AST-1446/AST-1453-persist-skipped-job-field-and-state-edits`

Authenticated persist for title, link, and job description on jobs whose current `job.state` is in `SKIPPED_STATES`. State changes go through `tracker.transition_job_state` (prior-state enforcement and `state_history`). GET job detail tells the client whether fields are editable and which registered states are legal next. This ticket does not change Job Detail form chrome (sibling AST-1454 / child #2).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | Add `legal_job_successor_states` and `persist_skipped_job_edits`; skipped-state gate; title/link/`job_description` writes; optional `transition_job_state` | core |
| `src/ui/api/api_jobs.py` | Attach `fields_editable` + `legal_next_states` on GET detail; add `PUT /api/jobs/<astral_job_id>` | ui |

Do not edit `JobDetailModal.tsx`, `JobsSkipped.tsx`, `src/utils/config.py`, `bulk_state`, `/skip`, `/copy`, candidate_action, artifact PUTs, or `tests/` / `docs/test-bible/**` (Betty).

## Stage 1: Core persist and successor list

**Done when:** `persist_skipped_job_edits` writes title/link/`job_description` only when current `job.state` is in `SKIPPED_STATES`, calls `transition_job_state` for a different requested `state`, and `legal_job_successor_states(from_state)` is exactly the set of `JOB_STATES` keys `transition_job_state` would accept from that `from_state` excluding `from_state` itself. No Flask routes yet.

1. In `src/core/tracker.py`, add this import next to the existing `JOB_STATES` import from `src.utils.config`: `SKIPPED_STATES`. Do not add any other config names.

2. Immediately after `_job_state_matches_prior` (before `write_job_dispatch_hop_label`), add:

```python
def legal_job_successor_states(from_state: str) -> List[str]:
    """JOB_STATES keys that transition_job_state would accept from from_state, excluding from_state."""
    current = (from_state or "").strip()
    out: List[str] = []
    for name, cfg in JOB_STATES.items():
        if name == current:
            continue
        if _job_state_matches_prior(current, cfg.get("prior_states")):
            out.append(name)
    return out
```

⚠️ **Decision:** Include unrestricted-entry states (`prior_states is None`: `NEW`, `FAILED_TECHNICAL`, `METEORITE_NEW`, `ERROR_QUALIFY_JOB_LISTINGS`, `ERROR_EVALUATE_JD`). Those hops are legal under existing `transition_job_state` / `_job_state_matches_prior`. Do not invent a narrower operator allowlist. Do not put a parallel successor list in config or TypeScript.

3. Immediately after `legal_job_successor_states`, add `persist_skipped_job_edits` with this contract:

- Signature: `persist_skipped_job_edits(astral_job_id: str, fields: Dict[str, Any]) -> Dict[str, Any]`
- Load the job via `get_job`. If missing, raise `ValueError(f"Job not found: {astral_job_id}")`.
- If `(job.get("state") or "")` is not in `SKIPPED_STATES`, raise `ValueError("Job is not in a skipped state")`. Below-dispatch-floor jobs whose state is not in `SKIPPED_STATES` fail this check (parent: not unlocked).
- Allowed keys in `fields`: `job_title`, `job_link`, `job_description`, `state`. Ignore any other key.
- If `job_title` is in `fields`: `title = (fields["job_title"] if fields["job_title"] is not None else "")` then `title = str(title).strip()`. If `title` is empty, raise `ValueError("job_title required")`.
- If `job_link` is in `fields`: same strip; empty → `ValueError("job_link required")`.
- If `job_description` is in `fields`: coerce with `"" if fields["job_description"] is None else str(fields["job_description"])` (do **not** strip the whole blob; persist the operator string, including empty). Write via `save_job_data(astral_job_id, {jd_key: text})` where `jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]`. Do **not** call `get_job_data` (that coat-check scrapes).
- If `job_title` and/or `job_link` were provided, call `save_job(astral_job_id, **col)` with only the provided column kwargs. If `save_job` returns `False`, raise `ValueError("job identity collision")`. If `sqlite3.IntegrityError` is raised and `_is_job_identity_unique_violation(exc)` is true, raise `ValueError("job identity collision")`; otherwise re-raise.
- If `state` is in `fields`: `to_state = str(fields["state"] or "").strip()`. If `to_state` is empty, raise `ValueError("state required")`. If `to_state != (job.get("state") or "")`, call `transition_job_state([astral_job_id], to_state)` (do not catch `ValueError` here — caller maps HTTP). Same-state is a no-op (do not append `state_history`).
- Apply column/JD writes **before** the transition so a later illegal hop still keeps field edits.
- Return `get_job(astral_job_id)` after writes (must not be `None`; if it is, raise `ValueError(f"Job not found: {astral_job_id}")`).
- Do not log. Do not dispatch, scrape, or consult.

4. Do not change `transition_job_state`, `bulk_state` callers, or `JOB_STATES` / `SKIPPED_STATES` contents.

## Stage 2: GET meta + PUT persist

**Done when:** `GET /api/jobs/<id>` includes `fields_editable` (bool) and `legal_next_states` (list of strings) on every found job; `PUT /api/jobs/<id>` with `@require_auth` persists skipped-job edits through `persist_skipped_job_edits` and returns the same detail shape as GET (including agent_story flatten). Non-skipped PUT is 409. Illegal `state` is 409. Missing job is 404. Unauthenticated is 401 via existing decorator. No React files changed.

1. In `src/ui/api/api_jobs.py`, import `legal_job_successor_states` and `persist_skipped_job_edits` from `src.core.tracker` (same import block as `transition_job_state`). `SKIPPED_STATES` is already imported.

2. Add this helper above `list_view` (after `_flatten_grades`):

```python
def _attach_skipped_edit_meta(job: dict) -> dict:
    state = job.get("state") or ""
    editable = state in SKIPPED_STATES
    job["fields_editable"] = editable
    job["legal_next_states"] = legal_job_successor_states(state) if editable else []
    return job
```

3. In `detail`, after `_flatten_grades(job)` and before the artifacts hydrate, call `_attach_skipped_edit_meta(job)`. Keep agent_story try/except unchanged. Do **not** attach these keys on list_view rows.

4. Register `PUT` on the same path as GET, after `detail` and before `/copy`:

```python
@jobs_bp.route("/<astral_job_id>", methods=["PUT"])
@require_auth
def persist_skipped_edits(astral_job_id):
```

Body: `request.get_json(force=True) or {}`. Allowed keys: `job_title`, `job_link`, `job_description`, `state`. Build `fields = {k: data[k] for k in ("job_title", "job_link", "job_description", "state") if k in data}`. If `fields` is empty, return `jsonify({"error": "No valid fields to update"}), 400`.

Call `get_job(astral_job_id)` first; if missing, `jsonify({"error": "Not found"}), 404` (do not call persist). Then:

```python
    try:
        persist_skipped_job_edits(astral_job_id, fields)
    except ValueError as exc:
        msg = str(exc)
        if msg == "Job is not in a skipped state" or msg.startswith("Invalid transition") or msg == "job identity collision":
            return jsonify({"error": msg}), 409
        if "not in allowed list" in msg:
            return jsonify({"error": msg}), 409
        return jsonify({"error": msg}), 400
```

After success, reuse the GET `detail` body: call `detail(astral_job_id)` **or** duplicate the GET assembly (flatten, `_attach_skipped_edit_meta`, artifact hydrate, agent_story try/except, `jsonify(job)`). Prefer calling the existing `detail` function so the response shape cannot drift.

⚠️ **Decision:** Put persist on `jobs_bp` `PUT /api/jobs/<id>` with `@require_auth`, not `api_admin.py`. Job Detail is already an authenticated jobs surface (`skip`, `copy`, GET). `pattern.ui.admin-endpoint` here means auth + thin API + eligibility in the API, not the admin blueprint.

⚠️ **Decision:** 409 for not-skipped and illegal/unknown target state (same family as `POST .../skip`); 400 for empty title/link/state string and empty body.

5. Do not change `/bulk_state`, `/skip`, `/copy`, artifact PUTs, or `candidate_action`. Do not auto-re-run consult, scrape, or dispatch after save.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

**Rubric:** plan-rubric.v1
**Ticket:** AST-1453
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1446/AST-1453-persist-skipped-job-field-and-state-edits` @ `147c59ae1dcf95e75ada48b22cc7454ac1592c1b`

**Gates:** Plan Ready · assignee Joan · 0 Plan Discuss rounds · child scope only

## Traceability
AC1→S2 (API: `fields_editable`/`legal_next_states`; editable controls→AST-1454) · AC2→S1+S2 · AC3→S1 · AC4→S1+S2 · AC5→S1+S2 · AC6→S1+S2 · parent AC7→N/A (sibling scope; plan excludes `/copy`, `/skip`, bulk Retry)

## Findings

No `fix-now` findings.

### acceptable
- **Location:** Stage 2 — `PUT` on `jobs_bp` vs `api_admin.py`
- **Finding:** `pattern.ui.admin-endpoint` names the admin blueprint; plan routes persist on authenticated `jobs_bp` alongside existing `skip`/`copy`/`GET detail`.
- **Recommendation:** Keep as written; plan ⚠️ Decision matches pattern intent (auth + thin API + server-side eligibility), not blueprint name alone.

### acceptable
- **Location:** Stage 1 — column/JD writes before `transition_job_state`
- **Finding:** One PUT can persist field edits even when the requested state hop returns 409.
- **Recommendation:** Explicit plan decision; consistent with “correct the record.” No change unless Susan wants transactional all-or-nothing save.

**Considered (in-session):** Universal orchestration statutes — N/A to this product diff. Scoped statutes/plan citations — all conform. Files Changed stays inside child scope (`tracker.py`, `api_jobs.py` only).

## Review (build)

**Built:** `origin/sub/AST-1446/AST-1453-persist-skipped-job-field-and-state-edits` @ `58c90b1adad18aef857f327ff348d3f0102bff37`

Stage 1–2: `legal_job_successor_states` + `persist_skipped_job_edits` in tracker; GET detail meta (`fields_editable` / `legal_next_states`) + authenticated PUT persist on `jobs_bp`. Form chrome deferred to AST-1454. Tests deferred to Betty.

## Radia review

# Radia review — AST-1453

**Publish ref:** `origin/sub/AST-1446/AST-1453-persist-skipped-job-field-and-state-edits` @ `23a691710ee3ed4aea4959161d21cc70fa6e0516`  
**Baseline:** `origin/dev`  
**Status gate:** Tests Passed (spawn prompt; trusted)  
**Product delta:** `58c90b1a` (+ Betty `c8ecee59` tests/bible)

---

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1453  
**Publish ref:** `origin/sub/AST-1446/AST-1453-persist-skipped-job-field-and-state-edits` @ `23a691710ee3ed4aea4959161d21cc70fa6e0516`  
**Overall:** CLEAN

## Statutes checked

Registry: 64 active rows from `canon/statutes/README.md` § Harvested corpus (doc header says 65; table lists 64 distinct ids at review SHA).

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent.py changes in AST-1453 product delta |
| astral.agent.do-task-delegation | scoped | not-applicable | no do_task / dispatch changes in child delta |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector paths touched |
| astral.batch.batch-id-first | scoped | not-applicable | no batch claim/release in child delta |
| astral.batch.batch-id-format | scoped | not-applicable | no batch_id emission in child delta |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/process/finally paths in child delta |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no entity_agent_responses writes |
| astral.config.config-source-of-truth | scoped | conforms | SKIPPED_STATES / JOB_STATES / TRACKER_CONFIG from config, not duplicated |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no env/secret surface in child delta |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifact dirs |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spike files |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch seed paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run_next / chain edits |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single `ast-1453-*.md` issue doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commit limited to tests + test-bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer product commit excludes tests/ |
| astral.layers.core-vs-external-bright-line | scoped | conforms | child delta stays core + ui/api |
| astral.layers.import-direction | scoped | conforms | api_jobs → core.tracker only; tracker → data/utils |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts/ changes in child delta |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | editability + successors resolved server-side from config/registry |
| astral.idioms.coat-check-never-store-empty | scoped | conforms | JD via direct save_job_data per plan; empty JD is intentional operator edit, not coat-check cache |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | PUT `/api/jobs/<id>` uses `@require_auth`; 401 test present |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed/json changes in child delta |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed catalog edits |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no boot/seed hot-path changes |
| astral.seed.define-approved | scoped | not-applicable | no define/seed work |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed row mutations |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage-join seed work |
| astral.standards.data-raises-caller-logs | scoped | conforms | persist_skipped_job_edits logs nothing (plan: do not log) |
| astral.standards.database-header-inventory | scoped | not-applicable | no database.py / migration changes in child delta |
| astral.standards.debug-contract-gated | scoped | not-applicable | no new debug= surfaces in child delta |
| astral.standards.dry-and-focused-functions | scoped | conforms | two focused helpers; PUT delegates to detail() for shape parity |
| astral.standards.in-scope-only | scoped | conforms | product commits touch only tracker.py + api_jobs.py |
| astral.standards.logging-via-utils | scoped | conforms | no new print/logging in persist path |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain names throughout |
| astral.standards.no-cross-contamination | scoped | conforms | no unrelated subsystem edits in child product commits |
| astral.standards.no-hardcoded-sets | scoped | conforms | SKIPPED_STATES imported; successors derived from JOB_STATES |
| astral.standards.public-then-helpers | scoped | conforms | new public functions precede existing transition helpers block |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils→data late-import changes |
| astral.state.core-decides-transitions | scoped | conforms | state hops via transition_job_state only |
| astral.state.job-prior-states-enforced | scoped | conforms | legal_job_successor_states mirrors _job_state_matches_prior; illegal hops propagate ValueError |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run/daisy-chain edits |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend changes (AST-1454 sibling) |
| astral.ui.naming-conventions | scoped | not-applicable | no frontend changes |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server worker config in child delta |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip includes merge-tests(AST-1453) single test SHA |
| orch.git.commit-vocabulary | universal | conforms | code/test/docs commits use standard prefixes |
| orch.git.flow-direction-inviolable | universal | conforms | sub publish ref topology correct |
| orch.git.ftr-sub-topology | universal | conforms | child on sub/AST-1446/AST-1453-* |
| orch.git.merge-on-checkout | universal | conforms | sync(dev) merges present on publish ref |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no cherry-pick/rebase/force evidence on child path |
| orch.git.no-dev-agent-branches | universal | conforms | engineer branch naming follows sub convention |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in astral-AST-1446 worktree |
| orch.git.three-permanent-branches | universal | conforms | diff vs origin/dev only |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | plan decisions documented; no unresolved product forks |
| orch.pipeline.plan-is-bible | universal | conforms | implementation matches staged plan contract |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Interface child reviewed in isolation |
| orch.pipeline.status-gates-skill-entry | universal | conforms | spawned at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | statute corpus active at review SHA |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty landed manifest + bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Radia recommend-only |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada remains assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path commits observed on child delta |

**C4 straggler:** Joan APPROVED @ `147c59ae`; no Excluded statute table attached — `no plan-rubric Excluded list attached`.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.admin-endpoint | conforms | Plan ⚠️ routes on authenticated `jobs_bp` not admin blueprint; auth + thin API + server-side eligibility match pattern intent (Joan acceptable finding stands) |

## Plan adherence

Stages 1–2 delivered exactly as planned:

- **`legal_job_successor_states`** — derives successors from `JOB_STATES` + `_job_state_matches_prior`, excludes self, includes unrestricted `prior_states is None` entries.
- **`persist_skipped_job_edits`** — gates on `SKIPPED_STATES`; writes JD then columns then optional `transition_job_state`; field-before-hop ordering tested; no logging/dispatch/scrape/consult.
- **GET detail** — `_attach_skipped_edit_meta` adds `fields_editable` / `legal_next_states`; list_view untouched.
- **PUT persist** — `@require_auth`, allowed-key filter, 404 pre-check, ValueError→status map per plan, success returns via `detail()` for shape parity.

Estimate **3** fits (~102 LOC product + focused Betty tests). No React / JobDetailModal scope (AST-1454). Cross-ticket: child product commits do not smuggle sibling scope; publish-ref rollup includes epic merges from other AST-1446 children — outside AST-1453 commits, not charged to this ticket.

**Test manifest (Betty):** `TestAst1453LegalJobSuccessorStates`, `TestAst1453PersistSkippedJobEdits`, `TestAst1453SkippedEditMetaAndPut` align with bible entries; status Tests Passed.

## Frame diff

| Plan frame | Tip reality |
|------------|-------------|
| Engineer: `tracker.py`, `api_jobs.py` only | `58c90b1a` matches (+ `SKIPPED_STATES` import only) |
| No tests/docs by engineer | Engineer excluded tests; Betty added bible + component tests (`c8ecee59`) — expected pipeline |
| No React | unchanged |
| Form chrome → AST-1454 | unchanged |

(none beyond expected Betty/test-bible additions)

## Findings

### advisory

- **Location:** `tests/component/core/test_tracker.py`, `tests/component/ui/api/test_api_jobs.py` vs bible status map  
- **Finding:** Bible documents PUT **409** for `job identity collision`, but no component test asserts that path (core or API).  
- **Recommendation:** Optional Betty follow-up before UT if Susan wants the status map fully locked; not blocking — handler mapping is present in `api_jobs.py`.

- **Location:** `legal_job_successor_states` return order  
- **Finding:** Successors follow `JOB_STATES.items()` iteration order (unsorted). Plan does not require sort; AST-1454 dropdown may want stable alphabetical order.  
- **Recommendation:** Discuss with AST-1454 implementer only if UX needs it; no backend change required now.

- **Location:** PUT pre-check vs persist reload (`api_jobs.py` ~188–203)  
- **Finding:** 404 only on pre-check; if row vanishes between pre-check and persist, client gets **400** `"Job not found: …"` not 404.  
- **Recommendation:** Accept as extremely rare; document only if operators report confusion.

### acceptable (prior Joan — unchanged)

- **jobs_bp vs admin blueprint** for persist — plan decision + pattern intent satisfied.

- **Field writes before failed transition** — explicit plan decision; tested (`test_field_writes_before_illegal_transition_propagates`).

## What's solid

- Plan-faithful core contract with explicit write ordering and skipped-state gate.
- PUT reuses `detail()` — response shape cannot drift from GET.
- Transitions stay on `transition_job_state`; no parallel successor list in TS/config.
- Component tests cover successor derivation, persist gates/writes/hop ordering, GET meta, PUT auth/status/success shape.

## Notes

- Three-dot diff vs `origin/dev` spans full AST-1446 epic rollup (~203 files); **AST-1453 product scope** is the isolated `58c90b1a` diff above. Statute sweep scored against child product delta + Betty test delta; epic sibling code not flagged.
- §5f / §5g not applied — no debug= or LLM external changes in child delta.
- C7 complete — Chuckles may append, commit docs, post slim upshot, move to Review Posted → resolve-child (PROCEED) or UT.

context_tokens≈92000

---

```
[code-rubric] PROCEED (Commit: 23a69171) skipped-job persist clean
```

---

## Bug: AST-1813 — statute carve-out for skipped-job prior-state bypass (AST-1811 board REVISE)

**Mini-parent:** AST-1809. **Sibling:** AST-1811 (product fix, `sub/AST-1809/AST-1811-skipped-any-state`); its `## Bug: AST-1811` block and `## Fix-board Joan findings (AST-1811)` live on that ref and reach this doc via `ftr` at merge-child.  
**Publish ref:** `sub/AST-1809/AST-1813-skipped-any-state-canon`  
**Canon-only gap:** no product code, no tests.

### As-is

`canon/statutes/astral/state/astral.state.job-prior-states-enforced.md` (active, scoped `src/core/**`) states without exception that job transitions enforce `JOB_STATES.prior_states` via tracker and raise when the current state may not enter the target. Its Violating example is any shortcut that sets job state "without prior_states checks." AST-1811 adds exactly such a bypass: `persist_skipped_job_edits` → `transition_job_state(..., enforce_prior_states=False)`. So the product diff reads as a violation of the corpus (Joan `[board-joan] CANON: REVISE`).

### To-be

The statute records one bounded carve-out for the skipped-job operator edit, and restates that every other caller keeps default enforcement. The AST-1811 diff then conforms to the corpus as written, and any other `enforce_prior_states=False` caller is still a violation.

### Repro

Read the statute as a reviewer would against the AST-1811 diff (`origin/sub/AST-1809/AST-1811-skipped-any-state` @ `57b178d8`, `src/core/tracker.py` `persist_skipped_job_edits`). The Statement has no exception clause, and the Violating example ("sets job state without prior_states checks") matches the new call. The corpus has no carve-out text naming `enforce_prior_states` (`rg -n enforce_prior_states canon/` → no hits).

### Root cause

The statute predates Susan's AST-1809 product call. It was written as a universal rule, and the corpus has no mechanism other than statute text to record an approved exception. Issue-doc prose (AST-1811's Canon note) does not amend canon (Joan triage).

### Proposed change

**One file:** `canon/statutes/astral/state/astral.state.job-prior-states-enforced.md`. Leave everything else in the file unchanged, and change only what the three steps below name.

1. **Frontmatter:** set `approved_at: "<landing date, YYYY-MM-DD>"`. Leave `approved_by: Archie` and every other field unchanged: `id`, `tier`, `checkable`, `status`, `applies_when`, `source_docs`, `supersedes`, `superseded_by`.

2. **`# Statement`:** keep the existing sentence verbatim, then append one blank line and this paragraph (house style matches the `dispatch_task` carve-out in `astral.seed.archie-catalog-wins`):

```markdown
**Skipped-job operator edit carve-out (AST-1809 / AST-1811):** exactly one caller may skip the prior_states check — `persist_skipped_job_edits` in `src/core/tracker.py`, which calls `transition_job_state(..., enforce_prior_states=False)` only when the job's current state is in `SKIPPED_STATES` and the target is a `JOB_STATES` key (not an implicit `{base}_RETRY`, not a runtime dispatch-hop label). The hop still goes through `transition_job_state` (registry check, `state_history`, `state_changed_at`). Every other caller uses the default `enforce_prior_states=True`; passing `False` anywhere else is a violation.
```

3. **`## Examples`:** append one bullet to each list, after the existing bullet:

   - `### Conforming`: `` - `persist_skipped_job_edits` on a job in `SKIPPED_STATES` moves it to any `JOB_STATES` key via `transition_job_state(..., enforce_prior_states=False)` (the carve-out above). ``
   - `### Violating`: `` - Any caller other than `persist_skipped_job_edits` passes `enforce_prior_states=False`, or the skipped-edit path accepts a target that is not a `JOB_STATES` key. ``

Leave `## Rationale` unchanged.

⚠️ **Decision — draft directive copy untouched.** `canon/directives/draft/stat.state.job-prior-states-enforced.md` is in scope only "if `docs/canon-index.md` § Resolving ids resolves the id through this directive copy." `docs/canon-index.md` does not exist on this branch, on `origin/dev`, or anywhere in git history, so I resolved the id from the corpus's own rules instead. First, `canon/statutes/README.md` § Harvested corpus maps `astral.state.job-prior-states-enforced` to `astral/state/astral.state.job-prior-states-enforced.md`. Second, `canon/docs/DIRECTIVE-ANATOMY.md` says a directive under `directives/draft/` is not in force. The id therefore resolves to the statute, the condition is false, and the draft stays as-is. Consequence: the two copies (byte-identical today) will diverge. If fix-board or Joan wants them mirrored anyway, the same Statement paragraph and example bullets apply verbatim to the draft, with no frontmatter change there.

⚠️ **Decision — `approved_at` bump rests on Susan's AST-1809 approval.** `orch.roles.archie-approves-statutes` requires Archie approval recorded in frontmatter for any amendment. Archie is Susan's alias. She approved AST-1809's To-be ("Should not be filtered beyond the entity type"), and its Canon note names this waiver explicitly. Joan ruled "Not ESCALATE — product intent explicit; remaining work is recording the exception." make-fix therefore keeps `approved_by: Archie` and sets `approved_at` to the landing date. If Chuckles or Joan judge that the AST-1809 approval does not cover statute text, this needs Archie's confirmation before merge-child, not an engineer-authored approval.

⚠️ **Decision — pattern untouched.** `pattern.state.entity-state-transitions` lists this id in `related_statutes`. DIRECTIVE-ANATOMY says patterns "Cite, never restate," so the carve-out reaches the pattern through the citation. No `related_statutes` or "Solution shape" edit is required (ticket Boundary: "only if … linkage requires it").

### Blast radius

- **Consumers of the statute:** Joan (`validate-plan`, fix-board) and Radia (`review-child` / `review-fix` code-rubric full active-set sweep). After this lands, AST-1811's `review-fix` scores `astral.state.job-prior-states-enforced` as **conforms** instead of violating. Future reviews must flag any other `enforce_prior_states=False` caller.
- **Registry / harvest tables:** `canon/statutes/README.md`, `canon/statutes/HARVEST.md`, `canon/docs/HARVEST-statutes.md`, and `canon/docs/DIRECTIVES-DIRECTORY.md` carry id, tier, checkable and path only. None changes, so no edit is needed.
- **Draft copy:** diverges from the statute (see Decision).
- **Merge-child ordering:** AST-1811 and AST-1813 both append a `## Bug:` block to the end of this doc from the same base (`ed02c7f9`), so their `ftr` merges conflict textually at EOF. Resolve by keeping both blocks: AST-1811 block, its Joan findings, then AST-1813. AST-1813 must merge before or with AST-1811, so `review-fix` on the rolled-up `ftr` sees the carve-out.
- **No product or test impact.** Betty's sibling test gap AST-1812 is unaffected.

### What must still hold

- The original Statement sentence stays verbatim. Prior-state enforcement remains the rule for every job transition except the one named carve-out.
- The carve-out names exactly one caller, `persist_skipped_job_edits`, and all three bounds: current state ∈ `SKIPPED_STATES`, target ∈ `JOB_STATES` keys, and the hop goes through `transition_job_state`. It never grants a general "operator override."
- `astral.state.core-decides-transitions` and `astral.standards.no-hardcoded-sets` are not touched. They stay satisfied because the carve-out routes through the tracker and the registry.
- Frontmatter: `approved_by: Archie` is present, `status: active` and `tier: scoped` are unchanged, and `applies_when` is unchanged.
- No files outside `canon/statutes/astral/state/astral.state.job-prior-states-enforced.md` are edited by make-fix, unless the draft-mirror Decision is overturned at fix-board.


## Fix-board Joan findings (AST-1813)

### Triage notes

**Fix-board question:** Does the `## Proposed change` conflict with or still require amending any directive in force?

**Verdict:** No further canon work beyond this single statute file as written. The carve-out text matches AST-1811 board REVISE (one caller, `SKIPPED_STATES` gate, `JOB_STATES` keys only, still via `transition_job_state`). Pattern left alone is consistent with DIRECTIVE-ANATOMY (“cite, never restate”) and `related_statutes` on `pattern.state.entity-state-transitions`.

**`approved_at` / `orch.roles.archie-approves-statutes` (second Decision):** **Conforming — not ESCALATE.** That statute requires Archie approval in frontmatter (`approved_by: Archie`, `approved_at` set) and states explicitly that **Archie is the architect alias and Linear assignee Susan is the approval gate**. Susan’s AST-1809 approval of the To-be plus a Canon note that names this `astral.state.job-prior-states-enforced` waiver is architect approval of the **substance** of the amendment; AST-1813 is the scoped landing of that already-approved exception. make-fix updating `approved_at` to the landing date while keeping `approved_by: Archie` matches the conforming example (draft on branch → Archie approved → merged file carries fresh `approved_at`). What would violate the role statute is an engineer setting approval without that gate — not Susan’s prior AST-1809 call followed by a plan that quotes the exact Statement carve-out. No separate “Archie must comment on AST-1813 before merge” step is required unless AST-1809 never actually carried Susan/Archie sign-off on the named waiver (spawn assumes it did).

**Draft directive copy untouched (first Decision):** **Accept.** `docs/canon-index.md` is absent; id resolution via `canon/statutes/README.md` § Harvested corpus + DIRECTIVE-ANATOMY (only `directives/active/` in force) is sound. Leaving `canon/directives/draft/stat.state.job-prior-states-enforced.md` unchanged matches existing practice (e.g. `astral.seed.archie-catalog-wins` statute carries AST-1456 carve-out; the draft sibling stayed pre-carve-out). Divergence is a known mirror lag, not an in-force corpus gap. Optional mirror is hygiene only; fix-board does not require REVISE for it.

**Routing:** With Betty’s pass (if any) and Joan OK, Chuckles can treat AST-1813 as board-cleared for **make-fix** on canon-only scope; merge-child ordering vs AST-1811 remains as the plan’s blast-radius note (carve-out on `ftr` before/with product sibling for `review-fix`).

context_tokens≈22000
