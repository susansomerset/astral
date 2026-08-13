# AST-1274 — Restore Recommended job detail open (Job isn't loading on Recommended page)

**Linear:** [AST-1274](https://linear.app/astralcareermatch/issue/AST-1274/restore-recommended-job-detail-open-job-isnt-loading-on-recommended)
**Parent:** [AST-1273](https://linear.app/astralcareermatch/issue/AST-1273/job-isnt-loading-on-recommended-page)
**Publish ref:** `sub/AST-1273/AST-1274-restore-recommended-job-detail-open`

A RECOMMENDED job that already appears in the list fails on open: `GET /api/jobs/<id>` returns HTTP 500 and `JobAnalysisReportModal` labels every non-OK as "Job not found." Susan confirmed (AST-1276) the root cause is incomplete **fetch-side** `ref_agent_data_id` handling: when an `agent_data` row is loaded and `block_data` / block content is null while `ref_agent_data_id` is set, the fetch must return that ref’s content. This ticket completes that resolve path as the **primary** fix, adds a **secondary** caller-side soft-fail so corrupt graphs (missing target / cycle `ValueError`) do not 500 detail, and makes modal failure copy match HTTP status (404 vs other errors). Soft-fail alone is not sufficient.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Complete fetch-side `ref_agent_data_id` resolution in `_resolve_agent_data_block_data` (verify public readers route through it): null/empty `block_data` + populated ref → return referenced row’s decompressed content. Keep `ValueError` for missing ref target and for cycles (data-raises). No schema migration. | data |
| `src/core/roster.py` | **Secondary:** in `get_entity_agent_story`, catch exceptions from `list_entity_latest_agent_refs` / `get_agent_data_for_ids`, log via utils logger, return `[]` / empty `data_map` so detail can still open | core |
| `src/ui/api/api_jobs.py` | **Secondary:** in `detail`, catch exceptions around `get_entity_agent_story(job)`, log, set `job["agent_story"] = []`; keep `@require_auth` and 404-when-missing. Do not change hydrate/artifact paths unless a Stage 1 spike shows they throw. | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | On detail load: 404 → "Job not found"; other non-OK → JSON `error` or `Load failed (HTTP <status>)` — never map 500 to not-found | ui |

## Diagnosis (binding)

**Observed**

* List shows job `4a7dbb0c-a1cb-4c1d-ab9d-0c098c8313fc` (`meteorite-somerset`, `RECOMMENDED`); open → `GET /api/jobs/<id>` HTTP 500; modal "Job not found."
* List does not hydrate agent story; detail calls `get_entity_agent_story` → `get_agent_data_for_ids` / batch readers → `_resolve_agent_data_block_data`.

**Confirmed cause (Susan on AST-1276 Done)**

> When the content is fetched from agent_data for the agent_data_id, the block_content is null, and it does not yet support recognizing if the block_content is null and the ref_agent_data_id is populated, then return that ref's block_content.

`save_agent_data` already writes content-dedup rows with `block_data=NULL` and `ref_agent_data_id=<canonical id>`. Fetch must complete that contract. Susan did **not** authorize changing the missing-target raise contract.

**Also confirmed (UI)**

* `JobAnalysisReportModal` `load`: `if (!res.ok) throw new Error("Job not found")` — dishonest for non-404.

**Wrong fixes rejected**

* Soft-fail-only as the **primary** fix — does not implement Susan’s fetch contract.
* Silent `None` in data for missing ref targets (global read-contract change) — violates `astral.standards.data-raises-caller-logs`; dangling refs become invisible to all consumers. Callers catch instead.
* Changing save/dedup write path — out of scope.
* Returning 404 when resolve fails — job exists.
* Inventing content when the ref target is missing — must raise; callers soft-fail.
* Redesigning Recommended tabs / consult / dispatch / Meteorite ingest.

## Stages

### Stage 1: Complete `ref_agent_data_id` fetch in the data layer (primary)

**Done when:** Loading an `agent_data` row with `block_data` null/empty and a populated `ref_agent_data_id` returns the referenced row’s plain-text content via `get_agent_data` / `get_agent_data_for_ids` / `get_agent_data_by_batch`. A row with content and no ref is unchanged. Missing ref target and cycles still raise `ValueError` from data (no silent `None`).

1. In `src/data/database.py`, open `_resolve_agent_data_block_data` and make Susan’s rule explicit and complete:
   * If `ref_agent_data_id` is null/blank: return `_decompress_payload(row_dict.get("block_data"))` (unchanged).
   * If `ref_agent_data_id` is set: follow the ref chain to the canonical row and return that row’s decompressed `block_data` (existing hop loop). Ensure the null-content + ref-populated case cannot short-circuit to `None` without following the ref (no early return of local null when a ref is present).
   * Keep cycle detection (`ValueError` with clear message).
   * **Missing ref target:** keep raising `ValueError` (do **not** convert to `None`). Callers in Stage 2 catch.
2. Confirm these public readers all assign `d["block_data"] = _resolve_agent_data_block_data(conn, d)` before return (fix any reader that returns raw unresolved `block_data`):
   * `get_agent_data`
   * `get_agent_data_for_ids`
   * `get_agent_data_by_batch`
3. Do **not** change `save_agent_data` / `backfill_agent_data_refs` write semantics.
4. Do **not** add new `debug=` contract lines unless you must touch an existing `debug=` signature; default AC5 N/A.
5. Prove with a short `debug/spikes/AST-1274/` script (gitignored): two rows — canonical with non-empty `block_data` and `ref_agent_data_id` NULL; alias with `block_data` NULL and `ref_agent_data_id` = canonical id — then `get_agent_data(alias_id)` / `get_agent_data_for_ids([alias_id])` must return the canonical plain text on `block_data`. Also assert a dangling ref still raises `ValueError`. Use a throwaway DB file under `debug/spikes/AST-1274/` (no shared-DB pollution).

⚠️ **Decision:** Primary fix is complete ref fetch in data. Data keeps raising on missing target / cycle (`astral.standards.data-raises-caller-logs`). Soft-fail is Stage 2 only, secondary.

### Stage 2: Secondary caller soft-fail + modal honesty

**Done when:** (A) `get_entity_agent_story` / `detail` do not let resolve `ValueError` become an uncaught Flask 500 — detail returns 200 with `agent_story: []` and a logged warning when story hydration fails; (B) missing job id still 404; (C) modal shows not-found only for 404, other failures use honest copy.

1. In `src/core/roster.py` `get_entity_agent_story`:
   * Keep entity-type detection and empty early returns unchanged.
   * Wrap `list_entity_latest_agent_refs(...)` in `try/except Exception`: log via existing `logger` (`warning` or `exception`) with `entity_type` / `entity_id`; **return `[]`**.
   * Wrap `get_agent_data_for_ids(all_ids)` the same way: on failure log and use `data_map = {}`.
2. In `src/ui/api/api_jobs.py` `detail`:
   * Keep 404 when `get_job` returns falsy; keep `@require_auth`.
   * Wrap `get_entity_agent_story(job)` in `try/except Exception`: log via `get_logger(__name__)`; set `job["agent_story"] = []`.
   * Do **not** broaden into hydrate/artifact wraps unless Stage 1 proves they throw for this bug.
3. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` `load`:
   * Replace `if (!res.ok) throw new Error("Job not found")` with:
     * `res.status === 404` → `"Job not found"`.
     * Other non-OK → try JSON `{ error?: string }`; else ``Load failed (HTTP ${res.status})``.
   * Keep existing `catch` → `setError` / `setJob(null)`.
   * Do **not** edit `JobDetailModal.tsx`; do **not** extract a shared helper.

⚠️ **Decision:** Soft-fail is explicitly **secondary** — Susan ruled it out as the primary fix, not as a production backstop for corrupt graphs. Data-layer raise contract unchanged.

### Stage 3: End-to-end check against acceptance criteria

**Done when:** AC1–AC4 verified; AC5 N/A unless Stage 1 touched `debug=`.

1. AC1 / AC2: With Stages 1–2 shipped, `GET /api/jobs/<id>` for a job that exercises null-`block_data` + populated `ref_agent_data_id` (spike-backed resolve proof and/or live RECOMMENDED row) returns **200** with job identity + Summary fields; server log is not HTTP 500. Additionally prove the secondary guard: force `get_entity_agent_story` (or `list_entity_latest_agent_refs`) to raise → GET still **200** with `agent_story: []` and a log line.
2. AC3: Missing id → not-found in modal; forced non-404 → not the not-found copy.
3. AC4: If the shared DB has at least one other RECOMMENDED row, open it and confirm the modal loads. If it has **zero** RECOMMENDED rows: skip the live AC4 smoke, leave AC4 unchecked in the Linear description at Code Complete, and add one sentence in the Code Complete comment: `AC4 skipped — zero RECOMMENDED rows in shared DB`.
4. AC5: N/A if no `debug=` edits.

## Execution contract

* Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1273/AST-1274-restore-recommended-job-detail-open`.
* Do not edit `tests/` or `docs/test-bible/**` (Betty).
* Do not push `origin/dev`. Do not create refs. Do not self-cherry-pick.
* Ambiguity → comment on **parent** AST-1273 with `🛑 Stage N blocked` and wait.

## Self-Assessment

**Scope:** `Single-Component` — data-layer ref resolve (primary) + thin core/UI soft-fail backstop + Recommended report modal load copy. No list redesign, consult, dispatch, or schema migration.

**Conf:** `high` — Susan named the fetch contract; write side already stores null-`block_data` + ref; secondary catch restores revision-1 layer placement Joan required.

**Risk:** `Medium` — soft-fail can hide corrupt refs (mitigation: logged warnings; data still raises for other callers that do not catch); wrong resolve could empty story text (spike proof for alias→canonical).

## Self-review vs ASTRAL_CODE_RULES

* §1.3 DRY / public-then-helpers: one resolve helper; readers reuse it; soft-fail stays at callers.
* §1.5 data-raises-caller-logs: missing target / cycle still raise from data; core/UI catch and log.
* §1.5.1 debug-contract: default untouched (AC5 N/A).
* §2.4 / entity-agent-responses-latest-only: story still via latest-per-task refs; content from resolved `block_data`.
* §3.3 imports: data utils-only; UI → core/utils; no UI→data.
* `astral.idioms.require-auth-on-protected-endpoints`: keep `@require_auth` on `detail`.
* Soft-fail as primary: excluded; soft-fail as secondary backstop: in scope.

## Revisions

Revision 1 — 2026-08-08
Driven by: Joan `[plan-discuss] round=1 concern` (soft-fail plan).
Changes: Stage 1 no-reproduction branch; hydrate fallback without re-entry; Stage 4 forced soft-fail; Conf → Medium.

Revision 2 — 2026-08-08
Driven by: PLAN AMEND / Susan on AST-1276 — incomplete `ref_agent_data_id` fetch.
Changes: Full rewrite — primary data-layer ref resolve; dropped soft-fail-primary; modal honesty kept.

Revision 3 — 2026-08-08
Driven by: Joan `[plan-discuss] round=1 concern` on revision 2 @ `503795bd` (fix-now: missing-target `None` is wrong-layer; restore secondary caller catch; reword AC4 skip).
Changes: Keep data `ValueError` for missing target/cycle; restore `roster.get_entity_agent_story` + `api_jobs.detail` secondary soft-fail; clarify AC4 zero-row skip instruction; update Files Changed / In-scope framing.

---

## Review (build)

**Built:** `origin/sub/AST-1273/AST-1274-restore-recommended-job-detail-open` @ `355f0cda4cb62f2affd645e21a52d7daac027967`

Stages 1–2: `_resolve_agent_data_block_data` follows null/empty `block_data` + populated `ref_agent_data_id` (spike alias→canonical + dangling `ValueError`); secondary soft-fail in `get_entity_agent_story` / `detail`; `JobAnalysisReportModal` 404 vs non-404 copy. Stage 3: soft-fail GET 200 + `agent_story: []` proven; AC4 skipped (zero RECOMMENDED in shared DB). AC5 N/A. Tests deferred to Betty.

---

## Review (code-rubric.v2)

`[code-rubric] revision=2` — **Publish ref @** `e2b2b2aed1c8c0bf5867960e1caed2e12fb603a2`

**Overall: DISCUSS**

Full active-set swept in-session (65 active statutes: 18 universal, 47 scoped). No fix-now findings. Primary/secondary layering (`data` raises `ValueError` on missing ref target / cycle, `core`+`ui` catch-and-log per `astral.standards.data-raises-caller-logs`), `@require_auth` retained, `pattern.ui.admin-endpoint` and `pattern.layers.import-discipline` both conform, no cross-ticket scope smuggling in the product diff (the AST-1277/AST-1278/AST-1279 hunks in `tests/component/**` and `docs/test-bible/**` ride in via the shared `origin/tests` merge-tests SHA, not new work on this ticket — expected per `orch.git.betty-merge-tests-one-sha`, not a boundary violation).

**Discuss:** `_resolve_agent_data_block_data` now prefers local `block_data` over a populated `ref_agent_data_id` when both are non-blank (`has_local` branch, `src/data/database.py`). Susan's stated contract (AST-1276) only describes the null-local + populated-ref case; the old code always followed the ref when populated, regardless of local content. The new "local wins" branch is defensive and covered by `test_local_body_preferred_over_ref`, and it doesn't disturb the documented dedup-write contract (dedup rows write `block_data=NULL` alongside `ref_agent_data_id`), but it is a behavior change for a case outside the literal bug report. Worth a one-line confirmation from Susan/Archie that "local wins" is the intended tie-break, not just an implementer default.

**Pattern conformance**

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.admin-endpoint | conforms | `GET /api/jobs/<id>` keeps `@require_auth`; story-resolve soft-fail lives in API/core, not React |
| pattern.layers.import-discipline | conforms | `api_jobs.py` adds only `src.utils.logging` (ui→utils); no new ui→data/external import |

**Frame diff:** (none) — AC4 already unchecked in the description, matching the documented zero-RECOMMENDED-rows skip; no other description drift found.

context_tokens≈45000
— Radia

---

## Resolution

**Resolved:** 2026-08-08 — Radia `[code-rubric] revision=2` **Discuss** (local-wins tie-break).

Dropped the `has_local` early return in `_resolve_agent_data_block_data`. Plan Stage 1 and pre-AST-1274 behavior: when `ref_agent_data_id` is populated, follow the ref chain; when it is not, return local `block_data`. Null/empty local + populated ref still resolves (primary bug). Both-present rows keep following the ref (no new tie-break invent).

Betty's `test_local_body_preferred_over_ref` asserted the removed branch — `[qa-handoff]` for test/bible update; stay Review Posted until she republishes.

## Bug: AST-1354 — Fix agent story soft-fail + move to agent.py

### As-is
Opening a job whose latest `propose_application_responses` batch has a dangling / missing TASK (or other sibling) `agent_data` ref causes `list_entity_latest_agent_refs` → `get_agent_data_by_batch` → `_resolve_agent_data_block_data` to raise `ValueError: agent_data ref target missing: '…-task-…'`. AST-1274’s soft-fail in `roster.get_entity_agent_story` catches it with `logger.exception` (full stacktrace) and returns `[]`, so detail stays up but logs are noisy and **one** broken optional prompt-block piece empties the **entire** entity story. `get_entity_agent_story` still lives in `roster.py` (company coat-check module).

### To-be
Expected missing optional prompt-block / `agent_data` pieces for proposed application responses do **not** dump a stacktrace; they do **not** abort story (or detail) as if required. Story still soft-fails for truly corrupt graphs (AST-1274 contract). `get_entity_agent_story` lives in `src/core/agent.py`; `api_jobs` / `api_companies` import it from agent; roster no longer owns entity story.

### Repro
1. Entity has a latest RESPONSE for `propose_application_responses` (example batch `propose_application_responses-fafe75d0-e41d-48d7-95d6-d489483832dc`) whose batch also contains a row whose `ref_agent_data_id` points at a missing TASK id (`…-task-bb404bc0bb2e68f4`), or the TASK row is absent while siblings remain.
2. `GET /api/jobs/<astral_job_id>` (observed job `8178a846-d026-4ca3-be3f-1f5a0d3113a5` on Susan’s local).
3. Server log shows `get_entity_agent_story: list_entity_latest_agent_refs failed …` with a full `ValueError` traceback from `_resolve_agent_data_block_data`; story is `[]` even when other tasks’ refs are healthy.

### Root cause
`list_entity_latest_agent_refs` rebuilds `prompt_blocks` via `get_agent_data_by_batch(batch_id)`, which **resolves** every batch row’s `block_data` (including optional SYSTEM/CACHE/TASK siblings). Listing only needs `{type, id}`; the resolve step makes optional / missing sibling pieces required for **any** latest-ref list, and AST-1274’s catch-all `logger.exception` turns that expected miss into a stack dump. Secondary: story ownership is misplaced in `roster.py` (Susan: roster = company data; entity story → `agent.py`).

### Proposed change
Do **not** reopen AST-1274’s primary `_resolve_agent_data_block_data` contract (missing target / cycle still raise `ValueError` from data). Soft-fail remains at callers.

1. **`src/data/database.py` — `list_entity_latest_agent_refs` (listing must not require resolved siblings)**  
   For each latest RESPONSE, build `prompt_blocks` from a **metadata-only** batch read (`agent_data_id`, `block_type` ordered like today’s batch list — **no** `_resolve_agent_data_block_data`). Keep ref shape `{task_key, batch_id, created_at, prompt_blocks}` (non-RESPONSE siblings + this RESPONSE).  
   ⚠️ **Decision:** Listing ids/types without resolve is in scope; changing `_resolve_agent_data_block_data` / silent `None` on missing target is **out**. If a batch has zero sibling rows, `prompt_blocks` may be RESPONSE-only — that is valid (do not invent TASK/SYSTEM).

2. **`src/core/agent.py` — own entity story**  
   Move `get_entity_agent_story` and `_filter_response_block` from `roster.py` into `agent.py` (public then private helper; keep entity-type detection + scored-task enrichment behavior).  
   Soft-fail adjustments inside the moved function:  
   - Wrap `list_entity_latest_agent_refs` / content load in `try/except Exception` as today, but log **`logger.warning` without traceback** for expected missing-ref / `ValueError` (and any soft-fail that previously used `logger.exception`). Message still includes `entity_type` / `entity_id` / exception text.  
   - When hydrating block content: do **not** all-or-nothing on one bad id — load per `prompt_blocks[].id` (reuse `get_agent_data` or equivalent) and on `ValueError`/missing row log a one-line warning and leave that block’s `content` as `""`; continue other blocks/tasks so a missing TASK does not blank healthy RESPONSE text or other tasks.  
   - Outer catch may still return `[]` only when the **list** itself fails for a non-degraded reason; prefer partial story over empty when list succeeds.

3. **`src/core/roster.py`** — delete `get_entity_agent_story` / `_filter_response_block` and drop imports used only by them (`list_entity_latest_agent_refs`, `get_agent_data_for_ids`, etc. if unused). **No** roster re-export shim.

4. **Call sites**  
   - `src/ui/api/api_jobs.py`: import `get_entity_agent_story` from `src.core.agent`; keep detail soft-fail wrap; change its log from `logger.exception` → `logger.warning` (no stack) for the same expected class of failure.  
   - `src/ui/api/api_companies.py`: import from `src.core.agent` (same).

5. **Out of scope**  
   Artifact pin write (AST-1099), `propose_application_responses` LLM/task behavior, modal copy, and AST-1274 data-layer raise semantics.

### Blast radius
- Shared `list_entity_latest_agent_refs` consumers (`agent.py` hop hydrate, story): listing no longer throws solely because a sibling block’s content-ref is dangling; content readers still raise when those ids are fetched.  
- UI imports flip roster → agent; any code/tests still importing story from `roster` break (Betty owns `tests/` — expect fix-board / qa-fix if roster story tests need retarget).  
- Quieter logs: missing expected pieces no longer look like unhandled crashes.

### What must still hold
- AST-1274: data still raises on missing ref target / cycle; detail still returns 200 with usable job payload when story hydration fails; `@require_auth` + 404-when-missing job unchanged; modal 404 vs non-404 honesty unchanged.  
- AST-984 / code-rules §2.4: story still from latest-per-task RESPONSE refs + `prompt_blocks` ids (not entity JSON columns); RESPONSE content still shown when present.  
- Layer imports: UI → core/utils only; no UI→data.  
- Roster remains company coat-check / company data — not entity agent story.

## Radia review (AST-1354)

**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.pipeline.plan-is-bible | universal | conforms | plan-fix patch followed; no scope smuggling |
| orch.pipeline.project-scoped-queues | universal | conforms | single fix ticket |
| orch.pipeline.status-gates-skill-entry | universal | conforms | n/a to diff |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no product decisions taken in diff |
| orch.git.betty-merge-tests-one-sha | universal | conforms | no test-tree edits on sub |
| orch.git.commit-vocabulary | universal | conforms | uses `code`/`docs`/`test` types (see advisory on `test`+`src/`) |
| orch.git.flow-direction-inviolable | universal | conforms | sub stacked on ftr |
| orch.git.ftr-sub-topology | universal | conforms | publish ref naming correct |
| orch.git.merge-on-checkout | universal | conforms | n/a |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | n/a |
| orch.git.no-dev-agent-branches | universal | conforms | n/a |
| orch.git.one-epic-worktree-per-parent | universal | conforms | n/a |
| orch.git.three-permanent-branches | universal | conforms | n/a |
| orch.roles.archie-approves-statutes | universal | conforms | n/a |
| orch.roles.betty-owns-test-tree | universal | conforms | engineer left tests to Betty/gap child |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | n/a |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | n/a |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path commits in diff |
| astral.agent.confidence-bounds | scoped | not-applicable | no confidence/scoring logic touched |
| astral.agent.do-task-delegation | scoped | not-applicable | do_task path unchanged |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector edits |
| astral.batch.batch-id-first | scoped | not-applicable | no batch-id authority changes |
| astral.batch.batch-id-format | scoped | not-applicable | no batch-id format changes |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/release touched |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | metadata listing + entity_id on dedup RESPONSE copies strengthen latest-ref lookup |
| astral.config.config-source-of-truth | scoped | not-applicable | no config authority changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env edits |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug/artifact-dir changes |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spike files |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | run_next chain untouched |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch seed changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | plan-fix patched existing AST-1274 feature doc |
| astral.git.betty-no-src-or-features | scoped | not-applicable | engineer diff is src-only (Betty lane) |
| astral.git.engineer-test-tree-ban | scoped | conforms | no tests/ edits on publish ref |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check writes |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | consult/render untouched |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | `GET /api/jobs/<id>` keeps `@require_auth` |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no external I/O added to story path |
| astral.layers.import-direction | scoped | conforms | ui→core only; core→data via existing agent imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts/ changes |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | story logic stays in core, not React |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed JSON changes |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no catalog edits |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no seed boot path |
| astral.seed.define-approved | scoped | not-applicable | n/a |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | n/a |
| astral.seed.other-via-coverage-join | scoped | not-applicable | n/a |
| astral.standards.data-raises-caller-logs | scoped | conforms | `_resolve_agent_data_block_data` still raises; core/ui catch+log warning |
| astral.standards.database-header-inventory | scoped | not-applicable | no new DB headers |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug contract changes |
| astral.standards.dry-and-focused-functions | scoped | conforms | listing vs hydrate split is focused |
| astral.standards.in-scope-only | scoped | conforms | entity_id dedup write is root-cause-adjacent, not drive-by |
| astral.standards.logging-via-utils | scoped | conforms | `logger.warning` via utils logger |
| astral.standards.names-not-ticket-ids | scoped | conforms | n/a |
| astral.standards.no-cross-contamination | scoped | conforms | fix scoped to story/list/hydrate |
| astral.standards.no-hardcoded-sets | scoped | not-applicable | no new hardcoded sets |
| astral.standards.public-then-helpers | scoped | conforms | `get_entity_agent_story` public, `_filter_response_block` private in same block |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils↔data import changes |
| astral.state.core-decides-transitions | scoped | not-applicable | no job-state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | n/a |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | n/a |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend files |
| astral.ui.naming-conventions | scoped | not-applicable | no frontend files |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | n/a |

**Notes:** no plan-rubric / Joan fix-mode verdict attached for AST-1354 (fix-lane norm). No straggler callout.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.admin-endpoint | conforms | `detail` keeps `@require_auth`; soft-fail in API/core |
| pattern.layers.import-discipline | conforms | `api_jobs`/`api_companies` import `src.core.agent` only; no new ui→data |

## Plan adherence

Delivers all five numbered **Proposed change** items:

1. **`list_entity_latest_agent_refs`** — metadata-only batch read (`agent_data_id`, `block_type`); no `_resolve_agent_data_block_data` on listing. Final SHA has loop inside `_with_conn` (commit `3bc5c8cf` corrected the brief regression in `c5ca227b` that left work after `conn.close()`).
2. **`get_entity_agent_story` in `agent.py`** — moved from roster with per-id hydration, partial story on per-block failure, `logger.warning` (no traceback) on list/content errors.
3. **`roster.py`** — story helpers deleted; unused imports dropped; no shim.
4. **Call sites** — `api_jobs` / `api_companies` import from `src.core.agent`; `api_jobs.detail` soft-fail uses `logger.warning`.
5. **Out of scope** — `_resolve` raise semantics, LLM/task behavior, modal copy untouched.

Extra **`save_agent_data` entity_id on content-dedup INSERT** is not in the numbered bullets but is root-cause-adjacent (dedup RESPONSE copies without `entity_id` break `list_entity_latest_agent_refs`); conforms to `astral.batch.entity-agent-responses-latest-only`.

## Fix-specific checks

**[bug-repro]** — not applicable — clean board opt-out (no `[board-betty] TESTS: REVISE`, no qa-fix thread, no `[bug-repro]` test in diff or on `origin/tests` for AST-1354). Blast radius explicitly deferred roster/agent-story test retarget to gap sibling **AST-1355**.

**## What must still hold** — OK

| item | verdict |
|------|---------|
| AST-1274: data raises on missing ref/cycle; detail 200 + usable payload on story fail; `@require_auth`; 404 when missing | OK — `_resolve` unchanged; `detail` try/except + 404 path intact |
| AST-984: story from latest-per-task refs + `prompt_blocks` ids; RESPONSE content when present | OK — listing shape preserved; per-id `_get_agent_data_row` hydration |
| Layer imports: UI → core/utils only | OK |
| Roster = company coat-check, not entity story | OK — function removed from roster |

## Findings

### Advisory

1. **Plan doc optional line** — `save_agent_data` entity_id on dedup copies is implemented and commented but not listed under numbered **Proposed change**; worth a one-line plan patch when Chuckles appends this review.
2. **Commit hygiene** — two commits labeled `test(AST-1354)` touch `src/data/database.py` product code (`c5ca227b`, `3bc5c8cf`); functionally fine, vocabulary is misleading (`code` would be clearer).
3. **Test gap (expected)** — `tests/component/core/test_roster.py` still calls `roster_mod.get_entity_agent_story`; publish ref has no test-tree changes. Plan blast radius + **AST-1355** gap child own retarget + dangling-sibling repro. Not a product defect on this SHA.
4. **Hydration log nuance** — plan text says log on “missing row”; implementation logs on `Exception` (e.g. dangling ref `ValueError`) but treats `get_agent_data` → `None` as silent `""`. Reasonable soft-fail; only matters if Susan wants a warning on absent PK rows too.

### fix-now

(none)

### discuss

(none)

## What's solid

- Root cause addressed at the right layer: listing no longer requires resolving optional sibling `block_data`, so dangling TASK refs cannot abort the entire latest-ref list.
- Story hydration is per-block with partial results — one bad id no longer blanks healthy RESPONSE text or other tasks.
- Log noise fixed: `logger.exception` → `logger.warning` in story path and `api_jobs.detail`.
- Ownership corrected: entity story lives in `agent.py` beside agent_data orchestration; roster imports cleaned.
- Hop blast radius preserved: `_hop_agent_ref_for_parent` still uses `list_entity_latest_agent_refs` for metadata; content fetch via `_block_text_by_type` / `get_agent_data_for_ids` unchanged (content readers still raise when ids are fetched).

## Frame diff

(none) — AST-1354 plan-fix sections in `docs/features/interface/ast-1274-restore-recommended-job-detail-open.md` match the product diff.

## Chuckles branching

| Gate | Parent | Next action |
|------|--------|-------------|
| **PROCEED** (C7 complete) | Normal AST-1316 | → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped) |

Spawn **AST-1355** (or confirm already queued) for roster→agent test retarget + metadata-only listing / dangling-sibling repro — parallel hygiene, not a blocker for this product SHA.

context_tokens≈55000
— Radia
```

```
[code-rubric] PROCEED (Commit: 3bc5c8cf) metadata story soft-fail
```

## Docs-acceptance (AST-1354)

No test-tree delivery on this sub — Betty TESTS:REVISE filed as sibling gap **AST-1355**.

## Bug: AST-1355 — Gap: retarget agent-story tests/bible after move to agent.py

### As-is
Component tests and bible still assume `get_entity_agent_story` lives in `src/core/roster.py` (`tests/component/core/test_roster.py` classes `TestEntityAgentStory`, `TestEntityAgentStoryBranches`, `TestAst1274AgentStorySoftFail`, `TestAst726LatestOnlyRosterStory`; `docs/test-bible/core/roster.md` + `docs/test-bible/frontend/components.md` rows pointing at roster). After AST-1354 the symbol is only on `src/core/agent.py`, so those imports/monkeypatches are wrong. There is also **no** coverage for the AST-1354 repro shape: dangling / missing `propose_application_responses` TASK sibling → **partial** story without an exception stacktrace.

### To-be
Bible + component tests own entity story under **agent** (`test_agent.py` / `docs/test-bible/core/agent.md`), with imports and patches matching AST-1354’s implementation (`database.list_entity_latest_agent_refs`, per-id `get_agent_data` / `_get_agent_data_row`, `logger.warning` without traceback). A repro-shaped case asserts partial story (healthy RESPONSE/other tasks kept; bad sibling content `""`) and **no** `logger.exception` stack for that expected miss. Product code unchanged (already on ftr via AST-1354).

### Repro
1. Product already fixed on `origin/ftr/AST-1316-…` / AST-1354 publish: story in `agent.get_entity_agent_story`; `list_entity_latest_agent_refs` metadata-only; soft-fail via `logger.warning`.
2. Run existing roster story tests as-written → `AttributeError` / import failure on `roster_mod.get_entity_agent_story` (or patches targeting removed `list_entity_latest_agent_refs` / `get_agent_data_for_ids` on roster).
3. Gap (missing coverage): fixture batch for `propose_application_responses` with a RESPONSE row for the job plus a sibling TASK row whose `ref_agent_data_id` points at a missing id (or TASK id absent) while another task’s content is healthy — no test yet asserts partial story + warning-without-stack.

### Root cause
fix-board `[board-betty] TESTS: REVISE` on AST-1354: product moved story ownership and soft-fail shape, but test-tree / bible were deferred to this sibling gap. Soft-fail tests still patch the pre-move roster API (`get_agent_data_for_ids` all-or-nothing) instead of AST-1354’s per-id resolve path.

### Proposed change
**Product:** none (AST-1354 already shipped). This ticket is test/bible only (Betty / astral-tests conventions as applicable).

1. **`tests/component/core/test_roster.py`** — remove story-ownership classes (or leave thin redirects **only if** bible still needs a one-line pointer; prefer delete):
   - `TestEntityAgentStory`
   - `TestEntityAgentStoryBranches`
   - `TestAst1274AgentStorySoftFail`
   - `TestAst726LatestOnlyRosterStory` (story assertions only; keep any non-story roster tests untouched)

2. **`tests/component/core/test_agent.py`** — add equivalent classes importing `src.core.agent` as `agent_mod`:
   - Retarget every `roster_mod.get_entity_agent_story` → `agent_mod.get_entity_agent_story`.
   - Monkeypatch **`src.data.database.list_entity_latest_agent_refs`** (or `agent_mod.database.list_entity_latest_agent_refs`) for list failures — not `roster_mod.list_entity_latest_agent_refs`.
   - Soft-fail content path: patch **per-id** `agent_mod._get_agent_data_row` (or `database.get_agent_data`) to raise `ValueError` for the bad id; do **not** patch removed `get_agent_data_for_ids` all-or-nothing behavior.
   - Keep AST-1274 behaviors: list failure → `[]`; single-block resolve failure → entry present with `content == ""`.
   - Logging: soft-fail paths use `logger.warning` (no `exc_info` / no `logger.exception`). Assert with `caplog` or mock logger that **exception** was not called for the expected missing-ref case.

3. **New coverage (AST-1354 repro / this gap’s AC2)** — e.g. `TestAst1354AgentStoryDanglingTaskSibling` in `test_agent.py`:
   - Seed (sqlite fixture / in-memory DB): job entity_id `job-1354`; latest RESPONSE for `propose_application_responses` with real content; same batch includes a TASK (or sibling) row with `ref_agent_data_id` → missing target **or** list returns that TASK id and per-id get raises `ValueError("agent_data ref target missing: …-task-…")`.
   - Optionally include a second healthy task entry so “partial” is observable (not empty story).
   - **Assert:** `get_entity_agent_story(job)` returns non-empty story; `propose_application_responses` RESPONSE content still present (or other task intact); dangling TASK block `content == ""` if listed; call does not raise; **no** exception-level stack log for that miss (`warning` OK).

4. **Bible**
   - `docs/test-bible/core/roster.md`: retarget/remove rows that name `roster.py` (`get_entity_agent_story`); point to agent bible section / `test_agent.py` nodes.
   - `docs/test-bible/core/agent.md`: add (or extend) entity-story section — ownership AST-984/AST-1354, soft-fail AST-1274, dangling TASK sibling AST-1354/AST-1355 — with command nodes for the moved classes + new dangling-sibling test.
   - `docs/test-bible/frontend/components.md`: change Agent story phase row from `src/core/roster.py` / `test_roster.py` → `src/core/agent.py` / `test_agent.py` (`TestEntityAgentStory::test_ast520_…`).

5. **Out of scope:** re-implementing AST-1354 product; canon/statute edits (Joan CANON: OK); other roster non-story coverage.

### Blast radius
- Any CI / manifests that still invoke `test_roster.py::TestEntityAgentStory*` / `TestAst1274AgentStorySoftFail` / `TestAst726LatestOnlyRosterStory` must be updated to `test_agent.py` nodes (bible is the source of those commands).
- UI API tests that monkeypatch `jobs_mod` / `companies_mod.get_entity_agent_story` stay valid (they patch the API module binding, not roster).
- Product import surface already `api_*` → `agent`; no further product callers expected.

### What must still hold
- AST-1354 product contracts: data still raises on missing ref target / cycle; story soft-fails at caller with warning (no stack) for expected misses; metadata-only `list_entity_latest_agent_refs`; story lives in `agent.py` only.
- AST-1274 soft-fail semantics preserved in tests (list fail → `[]`; resolve fail → empty block content, detail still openable).
- AST-984 latest-per-task story via `list_entity_latest_agent_refs` + `prompt_blocks` ids (not entity JSON columns).
- This gap does not regress non-story roster tests or change Joan’s CANON: OK surface.

## Radia review (AST-1355)

**Overall:** FIX-NOW

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.pipeline.plan-is-bible | universal | violates | plan says **Product: none**; publish ref includes AST-1341/1342/1343 product via `sync(dev)` |
| orch.pipeline.project-scoped-queues | universal | conforms | single gap ticket |
| orch.pipeline.status-gates-skill-entry | universal | conforms | n/a |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | n/a |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1355)` @ `0402abdc` lands tests SHA `3b11fdf0` |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`test`/`merge-tests` types used |
| orch.git.flow-direction-inviolable | universal | needs-discussion | `sync(dev)` merged foreign product onto gap sub before test work |
| orch.git.ftr-sub-topology | universal | violates | sub should be ftr + this ticket only; carries 1341/1342/1343 product not on ftr |
| orch.git.merge-on-checkout | universal | conforms | n/a |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | n/a |
| orch.git.no-dev-agent-branches | universal | conforms | n/a |
| orch.git.one-epic-worktree-per-parent | universal | conforms | n/a |
| orch.git.three-permanent-branches | universal | conforms | n/a |
| orch.roles.archie-approves-statutes | universal | conforms | n/a |
| orch.roles.betty-owns-test-tree | universal | conforms | test/bible work on `origin/tests` + merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | n/a |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | n/a |
| orch.roles.pre-commit-path-bans | universal | conforms | n/a |
| astral.agent.confidence-bounds | scoped | not-applicable | no agent scoring changes in **AST-1355 commits** |
| astral.agent.do-task-delegation | scoped | not-applicable | n/a |
| astral.agent.grade-vector-validation | scoped | not-applicable | n/a |
| astral.batch.batch-id-first | scoped | not-applicable | n/a |
| astral.batch.batch-id-format | scoped | not-applicable | n/a |
| astral.batch.claim-process-release | scoped | not-applicable | n/a |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | tests retarget to `list_entity_latest_agent_refs` + agent story |
| astral.config.config-source-of-truth | scoped | not-applicable | n/a |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | n/a |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | n/a |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | n/a |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | n/a |
| astral.dispatch.seed-auto-false | scoped | not-applicable | n/a |
| astral.docs.features-single-file-per-ticket | scoped | violates | `sync(dev)` appends AST-1342/1343 plan-fix to **other** feature docs on this sub |
| astral.git.betty-no-src-or-features | scoped | violates | publish ref modifies `src/**` + foreign `docs/features/**` (not merge-tests exception) |
| astral.git.engineer-test-tree-ban | scoped | not-applicable | Betty lane; tests on `origin/tests` |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | n/a |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | n/a |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API route changes in AST-1355 commits |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | foreign product diff only |
| astral.layers.import-direction | scoped | not-applicable | foreign product diff only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | n/a |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | foreign product diff only |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | n/a |
| astral.seed.archie-catalog-wins | scoped | not-applicable | n/a |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | n/a |
| astral.seed.define-approved | scoped | not-applicable | n/a |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | n/a |
| astral.seed.other-via-coverage-join | scoped | not-applicable | n/a |
| astral.standards.data-raises-caller-logs | scoped | conforms | soft-fail tests assert `warning` not `exception` |
| astral.standards.database-header-inventory | scoped | not-applicable | n/a |
| astral.standards.debug-contract-gated | scoped | not-applicable | n/a |
| astral.standards.dry-and-focused-functions | scoped | conforms | moved classes mirror roster originals with API retarget |
| astral.standards.in-scope-only | scoped | violates | gap ticket is test/bible-only; `sync(dev)` @ `04b876aa` smuggles 1341/1342/1343 product |
| astral.standards.logging-via-utils | scoped | conforms | logger assertions on `agent_mod.logger` |
| astral.standards.names-not-ticket-ids | scoped | conforms | n/a |
| astral.standards.no-cross-contamination | scoped | not-applicable | layer imports unchanged in AST-1355 test commits |
| astral.standards.no-hardcoded-sets | scoped | not-applicable | n/a |
| astral.standards.public-then-helpers | scoped | not-applicable | no new product public API |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | n/a |
| astral.state.core-decides-transitions | scoped | not-applicable | n/a |
| astral.state.job-prior-states-enforced | scoped | not-applicable | n/a |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | n/a |
| astral.ui.frontend-file-placement | scoped | violates | foreign frontend edits on gap sub (`ArtifactEditor`, `CandidateProfile`, …) |
| astral.ui.naming-conventions | scoped | not-applicable | foreign diff |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | n/a |

**Notes:** no Joan fix-mode verdict attached. AST-1355 **test/bible commits** (`9e982b62`, `3b11fdf0`) are clean; violation is branch topology (`sync(dev)`), not Betty's test content.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.admin-endpoint | not-applicable | no API changes in AST-1355 test commits |
| pattern.layers.import-discipline | not-applicable | test-only commits |

## Plan adherence

**AST-1355 commits only** (`9e982b62` + `3b11fdf0` + `merge-tests`):

| # | item | verdict |
|---|------|---------|
| 1 | Remove roster story classes | OK — `TestEntityAgentStory`, `TestEntityAgentStoryBranches`, `TestFilterResponseBlock`, `TestAst1274AgentStorySoftFail` deleted; `TestAst726LatestOnlyRosterStory` story method removed, non-story kept |
| 2 | Add `test_agent.py` classes with agent imports/patches | OK — `agent_mod.database.list_entity_latest_agent_refs`, per-id `_get_agent_data_row`, no `get_agent_data_for_ids` |
| 3 | New dangling-sibling repro | OK — `TestAst1354AgentStoryDanglingTaskSibling` |
| 4 | Bible retarget | OK — `agent.md` section, `roster.md` + `frontend/components.md` rows |
| 5 | Out of scope | OK in test commits — no product re-implementation |

**Publish ref vs plan:** **FAIL** — `sync(dev)` @ `04b876aa` (parent `978435c5` merge-child refresh) adds product + foreign plan-fix docs **before** AST-1355 work. Ftr tip `22347825` already has AST-1354; it does **not** have AST-1341 (`1abf0e4e` not ancestor of ftr). Six files outside AST-1355 scope on tip:

- `src/core/builder.py` (AST-1341)
- `src/ui/frontend/src/components/ArtifactEditor.tsx`, `ArtifactsBaseResumeContent.tsx` (AST-1342)
- `src/ui/frontend/src/pages/CandidateProfile.tsx` (AST-1343)
- `docs/features/artifacts/ast-1337-print-control-on-base-resume-content.md` (AST-1342 plan-fix append)
- `docs/features/interface/ast-1336-candidate-profile-dirty-leave-wiring.md` (AST-1343 plan-fix append)

## Fix-specific checks

**[bug-repro]** — OK

`TestAst1354AgentStoryDanglingTaskSibling::test_partial_story_no_exception_stack` (`test_agent.py` ~7739):

- Tagged `[bug-repro]` in class docstring; bible row cites it.
- Pins concrete **To-be** values: 2-task partial story; `propose_application_responses` RESPONSE retains `"healthy propose response"`; dangling TASK `content == ""`; second task intact; `logger.warning` called; `logger.exception` **not** called.
- Exercises AST-1354 per-id hydrate path (`_get_agent_data_row` raises `ValueError` only for bad id) — would fail pre-move roster `get_agent_data_for_ids` all-or-nothing / roster import.
- List step mocked (plan allows); repro targets hydration soft-fail + partial story, matching gap AC2.

**## What must still hold** — OK (for test/bible commits)

| item | verdict |
|------|---------|
| AST-1354 product contracts preserved in tests | OK — metadata list mocked; per-id soft-fail; warning not exception |
| AST-1274 semantics in tests | OK — list fail → `[]`; single-block fail → `content == ""` |
| AST-984 latest-per-task via list API | OK — patches target `database.list_entity_latest_agent_refs` |
| Non-story roster tests untouched | OK — only story classes removed |

## Findings

### fix-now

1. **Strip foreign product from publish ref** — `origin/sub/AST-1316/AST-1355-gap-agent-story-tests` must rebase onto ftr tip `22347825` **without** `sync(dev)` `04b876aa` / `978435c5` ancestry. Keep only:
   - `docs(AST-1355): plan-fix`
   - `test(AST-1355): bug-repro` (already on `origin/tests` @ `3b11fdf0`)
   - `merge-tests(AST-1355)`
   
   **Why:** Plan §Proposed change line 399: **Product: none.** Ftr already has AST-1354. AST-1341/1342/1343 product belongs on their own subs merged to ftr via normal fix/feature lane — not piggybacked on a Betty gap sub. Until stripped, this sub cannot merge without shipping unreviewed-on-ftr product and violates `astral.git.betty-no-src-or-features`, `orch.git.ftr-sub-topology`, `astral.standards.in-scope-only`.

   **Locations:** `sync(dev)` `04b876aa`; product files listed above.

### discuss

1. **Repro uses mocks not sqlite seed** — plan allows “list returns TASK id + per-id get raises”; optional follow-up component test against real `list_entity_latest_agent_refs` metadata-only path (database layer) could harden AC2. Not blocking once branch topology is fixed.

### advisory

1. `TestAst1274AgentStorySoftFail::test_get_agent_data_failure_yields_empty_block_content` — `_get_agent_data_row` `side_effect` hits every id; still valid for “single RESPONSE block fails” shape.
2. After rebase, confirm `merge-tests` SHA still matches `origin/tests` tip containing `3b11fdf0`.

## What's solid (test/bible commits only)

- Complete roster → agent retarget: imports, monkeypatch targets, and bible command nodes aligned.
- Soft-fail tests updated for AST-1354 shape (`warning` asserted, `exception` forbidden).
- `[bug-repro]` dangling TASK sibling test is substantive — partial story, concrete content assertions, logging contract.
- `TestAst726LatestOnlyRosterStory` correctly trimmed to non-story coverage with pointer comment.
- Bible manifest in `agent.md` lists all moved classes + narrowed `run_component_tests.sh` command.

## Frame diff

AST-1355 plan-fix section matches **test/bible** commits. Publish ref **drifts** via foreign `sync(dev)` product/docs — not frame drift in the AST-1355 patch itself.

## Chuckles branching

| Gate | Parent | Next action |
|------|--------|-------------|
| **REVIEW** (fix-now, C7 complete) | Normal AST-1316 | → **Review Posted** → rebase/strip `sync(dev)` on sub (Chuckles/git hygiene) → re-run **Tests Passed** → re-review or fast-path if only topology fix → then UT |

Do **not** merge this sub to ftr until product churn is removed. AST-1341/1342/1343 should land on ftr through their own tickets first if not already there.

context_tokens≈48000
— Radia
```

```
[code-rubric] REVIEW (Commit: 0402abdc) strip sync dev product
```

## Resolution (AST-1355)

**Resolved:** 2026-08-13 — Radia FIX-NOW + merge-child `validate-sub-log` block.

Rebuilt `origin/sub/AST-1316/AST-1355-gap-agent-story-tests` as linear tip on `origin/ftr/AST-1316-cant-find-agent-data-for-proposed-application-responses` @ `22347825` plus AST-1355 keepers only:

1. `docs(AST-1355): plan-fix`
2. `merge-tests(AST-1355)` ← `origin/tests` @ `3b11fdf0` (`test(AST-1355)` second parent)
3. `docs(AST-1355): Radia review`
4. `resolve(AST-1355)` — this rebuild

No `sync(dev)`, no `Merge remote-tracking branch`, no AST-1341/1342/1343 product on the tip. Plan **Product: none** honored.

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/b795dcab1f52977524ed7785d011d2b1/4f33b37a-f82a-459f-adf8-557760e2fd57/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/37525f18-cbca-4cd2-880b-798a1b353737/store.db` |
| Radia | review | `/home/susan/.cursor/chats/b795dcab1f52977524ed7785d011d2b1/ea8ba71b-2397-40d1-bac5-191c6ddfb534/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1316 (parent) | ftr/AST-1316-cant-find-agent-data-for-proposed-application-responses |
| AST-1354 | sub/AST-1316/AST-1354-fix-agent-story-no-require-artifacts |
| AST-1355 | sub/AST-1316/AST-1355-gap-agent-story-tests |

**Epic worktree:** `astral-AST-1316/` — one active sub checked out at a time.
