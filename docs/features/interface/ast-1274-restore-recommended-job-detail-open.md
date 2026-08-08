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
