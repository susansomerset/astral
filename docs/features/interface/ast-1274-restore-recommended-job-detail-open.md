# AST-1274 — Restore Recommended job detail open (Job isn't loading on Recommended page)

**Linear:** [AST-1274](https://linear.app/astralcareermatch/issue/AST-1274/restore-recommended-job-detail-open-job-isnt-loading-on-recommended)
**Parent:** [AST-1273](https://linear.app/astralcareermatch/issue/AST-1273/job-isnt-loading-on-recommended-page)
**Publish ref:** `sub/AST-1273/AST-1274-restore-recommended-job-detail-open`

A RECOMMENDED job that already appears in the list fails on open: `GET /api/jobs/<id>` returns HTTP 500 and `JobAnalysisReportModal` labels every non-OK as "Job not found." Susan confirmed (AST-1276) the root cause is incomplete **fetch-side** `ref_agent_data_id` handling: when an `agent_data` row is loaded and `block_data` / block content is null while `ref_agent_data_id` is set, the fetch must return that ref’s content. This ticket completes that resolve path (so detail/story hydration gets real text instead of failing or empty), and makes modal failure copy match HTTP status (404 vs other errors). Soft-fail-only wraps around story hydration are **not** the primary fix.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Complete fetch-side `ref_agent_data_id` resolution in `_resolve_agent_data_block_data` (and verify every public reader used by job detail / story already routes through it): when the loaded row’s `block_data` is null/empty **and** `ref_agent_data_id` is populated, return the referenced row’s decompressed content (follow the chain; cycle/missing-target behavior documented in Stage 1). No schema migration. | data |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | On detail load: 404 → "Job not found"; other non-OK → JSON `error` or `Load failed (HTTP <status>)` — never map 500 to not-found | ui |

## Diagnosis (binding)

**Observed**

* List shows job `4a7dbb0c-a1cb-4c1d-ab9d-0c098c8313fc` (`meteorite-somerset`, `RECOMMENDED`); open → `GET /api/jobs/<id>` HTTP 500; modal "Job not found."
* List does not hydrate agent story; detail calls `get_entity_agent_story` → `get_agent_data_for_ids` / batch readers → `_resolve_agent_data_block_data`.

**Confirmed cause (Susan on AST-1276 Done)**

> When the content is fetched from agent_data for the agent_data_id, the block_content is null, and it does not yet support recognizing if the block_content is null and the ref_agent_data_id is populated, then return that ref's block_content.

`save_agent_data` already writes content-dedup rows with `block_data=NULL` and `ref_agent_data_id=<canonical id>`. Fetch must complete that contract.

**Also confirmed (UI)**

* `JobAnalysisReportModal` `load`: `if (!res.ok) throw new Error("Job not found")` — dishonest for non-404.

**Wrong fixes rejected**

* Soft-fail-only (`get_entity_agent_story` → `[]` / swallow in `detail`) as the **primary** fix — leaves ref rows empty/broken and does not implement Susan’s fetch contract (prior plan; superseded).
* Changing save/dedup write path or clearing `block_data` on canonicals — out of scope; write side already sets refs.
* Returning 404 when resolve fails — job exists.
* Data layer silent-success that invents content — must return the **ref target’s** content, not fabricate.
* Redesigning Recommended tabs / consult / dispatch / Meteorite ingest.

## Stages

### Stage 1: Complete `ref_agent_data_id` fetch in the data layer

**Done when:** Loading an `agent_data` row with `block_data` null/empty and a populated `ref_agent_data_id` returns the referenced row’s plain-text content via `get_agent_data` / `get_agent_data_for_ids` / `get_agent_data_by_batch`. A row with content and no ref is unchanged. Cycle and missing-target behavior is explicit and does **not** HTTP 500 the jobs detail path for a listed job that only needs resolved story text (see decisions).

1. In `src/data/database.py`, open `_resolve_agent_data_block_data` and make Susan’s rule explicit and complete:
   * If `ref_agent_data_id` is null/blank: return `_decompress_payload(row_dict.get("block_data"))` (unchanged).
   * If `ref_agent_data_id` is set: follow the ref chain to the canonical row and return that row’s decompressed `block_data` (existing hop loop). **Additionally** ensure the null-content + ref-populated case cannot short-circuit to `None` without following the ref (no early return of local null when a ref is present).
   * Keep cycle detection (`ValueError` with clear message) — do not invent content on cycles.
   * **Missing ref target:** do **not** raise into the UI as an uncaught 500 for ordinary detail loads. Return `None` (empty content) when the target id is absent, so callers get empty block text; data still does not log (callers may log if they choose). Document this in a one-line comment on the `None` return.
2. Confirm these public readers all assign `d["block_data"] = _resolve_agent_data_block_data(conn, d)` before return (already intended — fix any reader that returns raw unresolved `block_data` for the same table):
   * `get_agent_data`
   * `get_agent_data_for_ids`
   * `get_agent_data_by_batch`
3. Do **not** change `save_agent_data` / `backfill_agent_data_refs` write semantics in this ticket.
4. Do **not** add new `debug=` contract lines unless you must touch an existing `debug=` signature; default AC5 N/A.
5. Prove with a short `debug/spikes/AST-1274/` script (gitignored): insert (or use temp connection) two rows — canonical with non-empty `block_data` and `ref_agent_data_id` NULL; alias with `block_data` NULL and `ref_agent_data_id` = canonical id — then `get_agent_data(alias_id)` / `get_agent_data_for_ids([alias_id])` must return the canonical plain text on `block_data`. Clean up spike rows or use a throwaway DB file under `debug/spikes/AST-1274/`.

⚠️ **Decision:** Primary fix is **complete ref fetch in data**, not soft-fail in UI/core. Missing targets return `None` (empty content) rather than `ValueError`, so detail can open; cycles still raise (corrupt graph — rare; if a cycle is observed on the reported job during build, stop and comment on parent).

### Stage 2: Frontend — honest failure copy in JobAnalysisReportModal

**Done when:** Missing job id → not-found copy; non-404 failure → non-not-found error string; successful open sets `job` and clears `error`.

1. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` `load`:
   * Replace `if (!res.ok) throw new Error("Job not found")` with:
     * `res.status === 404` → `"Job not found"`.
     * Other non-OK → try JSON `{ error?: string }`; else ``Load failed (HTTP ${res.status})``.
   * Keep existing `catch` → `setError` / `setJob(null)`.
2. Do **not** edit `JobDetailModal.tsx`. Do **not** extract a shared helper (same-file `runPrimaryAction` already has a similar pattern; keep the 404 branch local).

### Stage 3: End-to-end check against acceptance criteria

**Done when:** AC1–AC4 verified; AC5 N/A unless Stage 1 touched `debug=`.

1. AC1 / AC2: With Stage 1 shipped, open a RECOMMENDED job whose story blocks include null-`block_data` + populated `ref_agent_data_id` (spike fixture and/or live row if present) via `GET /api/jobs/<id>` → **200**, body includes job identity + Summary fields; server log is not HTTP 500. If the original reported id is still absent from the shared DB, the spike-backed resolve proof from Stage 1 plus any available RECOMMENDED row smoke satisfy the fetch contract; note that on the child ticket when moving to Code Complete.
2. AC3: Missing id → not-found in modal; forced non-404 (e.g. mock `api` / temporary 500) → not the not-found copy.
3. AC4: Another healthy Recommended row still opens when the DB has one; if zero RECOMMENDED rows, note in Code Complete description/checklist comment path only via description ticks + optional one-line Betty context.
4. AC5: N/A if no `debug=` edits.

## Execution contract

* Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1273/AST-1274-restore-recommended-job-detail-open`.
* Do not edit `tests/` or `docs/test-bible/**` (Betty).
* Do not push `origin/dev`. Do not create refs. Do not self-cherry-pick.
* Ambiguity → comment on **parent** AST-1273 with `🛑 Stage N blocked` and wait.

## Self-Assessment

**Scope:** `Single-Component` — data-layer `agent_data` ref resolve used by job detail story hydration, plus Recommended report modal load copy. No list redesign, consult, dispatch, or schema migration.

**Conf:** `high` — Susan named the fetch contract on AST-1276; `save_agent_data` already writes null-`block_data` + `ref_agent_data_id`; UI not-found mapping is an explicit one-liner.

**Risk:** `Medium` — wrong resolve behavior could empty story blocks or loop on bad graphs (mitigation: cycle raise retained; spike proof for null+ref); missing-target → `None` changes prior `ValueError` surface (intentional so detail does not 500).

## Self-review vs ASTRAL_CODE_RULES

* §1.3 DRY / public-then-helpers: one resolve helper; all readers reuse it.
* §1.5 data-raises-caller-logs: cycles still raise; missing target returns `None` (documented exception to prior raise — empty content, not invented data). No data-layer logging.
* §1.5.1 debug-contract: default untouched (AC5 N/A).
* §2.4 / entity-agent-responses-latest-only: story still via latest-per-task refs; content comes from resolved `block_data`.
* §3.3 imports: data stays utils-only; UI still core/utils only for modal.
* `astral.idioms.require-auth-on-protected-endpoints`: no change to `@require_auth` on `detail`.
* Soft-fail-only UI/core wraps: **excluded** as primary fix (superseded by fetch completion).

## Revisions

Revision 1 — 2026-08-08
Driven by: Joan `[plan-discuss] round=1 concern`.
Changes: Stage 1 no-reproduction branch; hydrate fallback without re-entry; Stage 4 forced soft-fail; Conf → Medium.

Revision 2 — 2026-08-08
Driven by: PLAN AMEND / Susan on AST-1276 — incomplete `ref_agent_data_id` fetch when block content null and ref set; soft-fail-only insufficient.
Changes: Full rewrite — primary Stage 1 completes data-layer ref resolve; drop soft-fail-primary stages; keep modal honesty; Files Changed / self-assessment / statute frame updated.
