# AST-1274 — Restore Recommended job detail open (Job isn't loading on Recommended page)

**Linear:** [AST-1274](https://linear.app/astralcareermatch/issue/AST-1274/restore-recommended-job-detail-open-job-isnt-loading-on-recommended)
**Parent:** [AST-1273](https://linear.app/astralcareermatch/issue/AST-1273/job-isnt-loading-on-recommended-page)
**Publish ref:** `sub/AST-1273/AST-1274-restore-recommended-job-detail-open`

A RECOMMENDED job that already appears in the list fails on open: `GET /api/jobs/<id>` returns HTTP 500 and `JobAnalysisReportModal` labels every non-OK response as "Job not found," so Susan cannot read Summary / analysis for a job the list already surfaced. This ticket restores successful detail load for that path and makes modal failure copy match the real HTTP outcome (404 vs other errors), without redesigning Recommended list/tabs or changing consult/dispatch.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_jobs.py` | Guard `_flatten_grades` when `job_data` is not a dict; catch story/hydrate failures in `detail` so a listed job still returns 200 with payload (empty `agent_story` / raw artifacts dict as fallback — no re-entry into failing helpers); log via utils logger | ui |
| `src/core/roster.py` | Harden `get_entity_agent_story` so `list_entity_latest_agent_refs` / `get_agent_data_for_ids` failures (e.g. agent_data ref cycle / missing ref `ValueError` from data layer) log and return `[]` instead of raising into the UI | core |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | On detail load: 404 → "Job not found"; other non-OK → message from JSON `error` or `Load failed (HTTP <status>)`; network/parse errors keep generic load-failed copy — never map 500 to not-found | ui |

## Diagnosis (planner — binding for Stage 1)

**Observed**

* List shows job `4a7dbb0c-a1cb-4c1d-ab9d-0c098c8313fc` (`meteorite-somerset`, `RECOMMENDED`) with full phase scores / `analysis_upshot` in `job_data`.
* Open triggers `GET /api/jobs/4a7dbb0c-a1cb-4c1d-ab9d-0c098c8313fc` → HTTP 500; modal shows "Job not found."

**Code differences that explain list-OK / detail-500**

* `list_view` (`GET /api/jobs?view=recommended`): `list_jobs` → `_flatten_grades` → `jsonify`. **No** `get_entity_agent_story`, **no** artifact hydrate.
* `detail` (`GET /api/jobs/<id>`): `get_job` → `_flatten_grades` → `hydrate_job_artifacts_for_display` → **`get_entity_agent_story`** → `jsonify`. Uncaught exceptions become Flask 500.

**Reproduction on this worktree (2026-08-08)**

* Local `data/astral.db` (symlink to `astral/data/astral.db`) has **no** row for the reported id (`recommended` count 0).
* Parent brief JSON for that job, with `job_data` / `state_history` parsed, runs flatten + hydrate + `jsonify` successfully when `agent_story` is empty (no agent_data for the id in this DB).
* Therefore the brief payload alone is not enough to re-trigger the 500 here; the failure almost certainly needs live `agent_data` for that entity (or another throw on the detail-only path).

**Primary hypothesis (implement against this first — only after Stage 1 reproduces a throw, or after Stage 4 forced soft-fail proof when live 500 is unavailable)**

* `get_entity_agent_story` → `list_entity_latest_agent_refs` / `get_agent_data_for_ids` → `_resolve_agent_data_block_data` can **raise** `ValueError` (ref cycle / missing ref target). That escapes `detail` → HTTP 500.
* Independently confirmed UI bug: `JobAnalysisReportModal` `load` does `if (!res.ok) throw new Error("Job not found")` — every non-OK including 500.

**Secondary hardening (same stages, cheap)**

* `_flatten_grades` today does `jd = job.get("job_data") or {}` then `if key in jd: job[key] = jd[key]`. If `job_data` were ever a non-dict string, this `TypeError`s. Detail already treats non-dict `job_data` as `{}` for artifacts; align `_flatten_grades` the same way. (List would also fail in that case — still fix for consistency.)

**Wrong fixes rejected**

* Returning 404 from detail when story hydration fails — job exists; would keep the dishonest not-found UX.
* Swallowing all exceptions at Flask app level without fixing story/detail — hides every API bug.
* Changing data-layer `_resolve_agent_data_block_data` to never raise — violates `astral.standards.data-raises-caller-logs`; callers (core/UI) must catch and log.
* Redesigning Recommended tabs / regenerating artifacts / re-running consult for this job — out of boundaries.
* Proceeding to Stage 2 after a brief-JSON upsert that never 500'd — would greenwash AC1/AC2 without proving the soft-fail path.

## Stages

### Stage 1: Reproduce detail 500 and confirm throw site

**Done when:** One of: (A) a concrete traceback for the reported/equivalent job matching story/hydrate is captured and Stage 2 may proceed; (B) a traceback elsewhere is posted on parent AST-1273 and work stops until the plan is amended; or (C) **no reproduction available** (job missing and brief upsert yields **no** traceback) — parent AST-1273 gets a `🛑 Stage 1 blocked` comment asking for the live row / `agent_data`, and **Stage 2 must not begin** until either the live 500 is reproduced or Susan/Chuckles explicitly green-lights implementing the soft-fail path with Stage 4’s forced-raise proof alone.

1. On epic worktree, ensure Flask can import (`PYTHONPATH` / venv as `launch.sh`: repo root + `src` on path; use `/home/susan/astral/.venv` if the worktree has no venv).
2. Look up job `4a7dbb0c-a1cb-4c1d-ab9d-0c098c8313fc` via `get_job`. Prefer restoring from Susan's live DB if the row reappears on the shared `astral.db` symlink. If still missing: upsert from the parent AST-1273 Original brief JSON array (parse string `job_data` / `state_history` before save) using existing tracker/database save helpers — **do not** invent a new migration. Treat brief upsert as a **payload fixture only**, not as proof the original 500 is reproduced.
3. Call the same sequence as `api_jobs.detail` in a short `debug/spikes/AST-1274/` script (gitignored): `get_job` → `_flatten_grades` → `hydrate_job_artifacts_for_display(...)` → `get_entity_agent_story` → `jsonify`. Catch and print full traceback. Optionally hit live `GET /api/jobs/<id>` on `:5001` if the server is already up.
4. **Branch — traceback inside** `get_entity_agent_story` / agent_data ref resolve / hydrate: proceed to Stage 2 with no plan change.
5. **Branch — traceback elsewhere:** **stop**. Comment on **parent** AST-1273 with the `🛑 Stage 1 blocked` format (throw site, proposed plan amendment). Do not invent a different fix.
6. **Branch — no traceback (most likely on this worktree today):** **stop**. Do **not** proceed to Stage 2. Comment on **parent** AST-1273: reported id / equivalent never 500'd after lookup or brief upsert; need the live `job` + `agent_data` rows (or Susan approval to implement soft-fail + Stage 4 forced-raise proof without a live reproduction). Wait for that row or approval before Stage 2.

⚠️ **Decision:** Diagnosis-first stage is mandatory because the reported job is not currently in this worktree DB; a green detail after brief upsert alone must not unlock Stage 2.

### Stage 2: Backend — detail succeeds when the job row exists

**Done when:** For the reported job (or the Stage 1 equivalent that previously 500'd), `GET /api/jobs/<id>` returns **200** with `astral_job_id`, `job_title` / `company`, and `job_data` including Summary fields (`analysis_upshot` when present). Missing job still returns **404** `{"error": "Not found"}`. Server log for the open is not HTTP 500. (If Stage 1 used Susan’s green-light without a live 500, this Done-when for the reported id is deferred to Stage 4’s forced soft-fail proof plus any available RECOMMENDED row smoke.)

1. In `src/core/roster.py` `get_entity_agent_story`:
   * Keep entity-type detection and empty early returns unchanged.
   * Wrap `list_entity_latest_agent_refs(entity_type, entity_id)` in `try/except Exception`: on failure, `logger.warning` (or `logger.exception`) with `entity_type`, `entity_id`, and the exception; **return `[]`**.
   * Wrap `get_agent_data_for_ids(all_ids)` the same way: on failure log and use `data_map = {}` so blocks render with empty content rather than aborting the whole story.
   * Do **not** change `src/data/database.py` raise behavior for ref cycles / missing refs.
   * Do **not** add new `debug=` contract emission unless Stage 1 proved a `debug=` path is required; default is ordinary warning/exception logs only (AC5 N/A if untouched).
2. In `src/ui/api/api_jobs.py`:
   * Change `_flatten_grades` so `jd` is only used as a mapping when `isinstance(job.get("job_data"), dict)`; otherwise treat as `{}` (same pattern as `detail`'s artifact branch).
   * In `detail`, after `_flatten_grades`:
     * Keep 404 when `get_job` returns falsy.
     * Compute `raw_artifacts = jd.get("artifacts") if isinstance(jd.get("artifacts"), dict) else {}` (pure dict read — do **not** call `get_job_artifacts` inside an `except`).
     * Call `art = hydrate_job_artifacts_for_display(get_job_artifacts(job) or raw_artifacts)` inside `try/except Exception`: on failure log via `get_logger(__name__)` and set `art = raw_artifacts` (already computed; **never** re-invoke `get_job_artifacts` or `hydrate_job_artifacts_for_display` in the `except`).
     * Wrap `get_entity_agent_story(job)` in `try/except Exception` as belt-and-suspenders (core already hardened): on failure log and set `job["agent_story"] = []`.
     * Keep `@require_auth` on the route.
   * Do not broaden into other jobs endpoints (bulk_state, artifacts PUT, generate/cancel) unless Stage 1 traceback pointed there (then stop and amend).
3. Manually verify when a previously-500ing job exists: that job → 200; unknown id → 404; Flask log shows no 500 for the open.

⚠️ **Decision:** Soft-fail story/hydrate at **core + UI callers**, leave data-layer raises intact (`astral.standards.data-raises-caller-logs`). Empty `agent_story` is acceptable for AC1 — JAR Summary reads `job_data.analysis_upshot`, not story blocks. Hydrate fallback is a pure `jd` artifacts dict so a throw inside `get_job_artifacts` cannot re-raise from the `except`.

### Stage 3: Frontend — honest failure copy in JobAnalysisReportModal

**Done when:** Opening a missing job id shows not-found copy; a non-404 failure (e.g. forced 500 via temporary test double or by mocking `api`) shows a non-not-found error string; successful open still sets `job` and clears `error`.

1. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` `load`:
   * Replace `if (!res.ok) throw new Error("Job not found")` with status-aware handling:
     * `res.status === 404` → error message `"Job not found"` (keep existing user-facing phrase).
     * Other non-OK → try `await res.json()` for `{ error?: string }`; use `error` string when present and non-empty; else ``Load failed (HTTP ${res.status})``.
   * Keep `catch` setting `setError(e instanceof Error ? e.message : "Load failed")` and `setJob(null)`.
   * Do **not** change tab layout, artifact actions, or company secondary fetch beyond leaving existing `.catch` behavior.
2. Do **not** edit `JobDetailModal.tsx` in this ticket (In Review shell; out of Recommended report modal scope). If a shared helper is tempting, skip it — one-call-site change only (same file’s `runPrimaryAction` already has a similar JSON-`error`/HTTP status pattern; keep the 404 branch local).
3. Smoke: Recommended open on healthy row still works; error UI renders the new strings when forced.

### Stage 4: End-to-end check against acceptance criteria

**Done when:** AC1–AC4 confirmed on epic worktree; AC2’s soft-fail path is **demonstrated** (not only inferred); AC5 marked N/A in the Linear stage comment if no `debug=` surfaces were edited.

1. AC1: From Recommended, open the reported/equivalent job that previously 500'd (when available) → modal shows title/company and Summary content (not not-found empty state). If live 500 never returned, AC1 on the reported id stays blocked pending Susan’s row — still complete steps 2–5 below.
2. AC2 soft-fail proof (**mandatory even when live 500 is unavailable**): with Stage 2 shipped, force `get_entity_agent_story` (or `list_entity_latest_agent_refs`) to raise for a known existing job id (monkeypatch in `debug/spikes/AST-1274/` or a one-shot Flask test client against the epic worktree app). Confirm `GET /api/jobs/<id>` still returns **200**, body has `agent_story: []` (or omitted-empty equivalent), job identity fields present, and a warning/exception log line was emitted. Without this step AC2 is not done.
3. AC3: Missing id → not-found; forced non-404 failure → not the not-found copy.
4. AC4: At least one other Recommended row that already worked still opens (skip only if the DB has zero RECOMMENDED rows — note that in the stage comment).
5. AC5: If Stage 2 did not touch `debug=` paths, note N/A; if it did, verify `debug=True` / `debug=False` per Code Rules §1.5.1.

## Execution contract

* Execute stages in order; one commit per stage on the epic worktree; publish each commit to `origin/sub/AST-1273/AST-1274-restore-recommended-job-detail-open`.
* Do not edit `tests/` or `docs/test-bible/**` (Betty).
* Do not push `origin/dev`. Do not create refs. Do not self-cherry-pick.
* Ambiguity or Stage 1 mismatch / no-reproduction branch → comment on **parent** AST-1273 with `🛑 Stage N blocked` and wait.

## Self-Assessment

**Scope:** `Single-Component` — UI jobs detail API + one core story helper + Recommended report modal load path; no list redesign, no consult/dispatch, no schema migration.

**Conf:** `Medium` — UI not-found mapping is confirmed and high-confidence; backend soft-fail targets the list-vs-detail split (story/hydrate) but the original 500 was not reproduced on this worktree, so Stage 1 / Stage 4 forced-raise proof carry the load.

**Risk:** `Medium` — soft-failing agent_story could hide broken refs (mitigation: warning/exception logs); wrong catch breadth could mask unrelated detail bugs (mitigation: Stage 1 traceback gate; only wrap hydrate + story, not `get_job`); hydrate `except` must not re-enter failing helpers.

## Self-review vs ASTRAL_CODE_RULES

* §1.3 DRY / public-then-helpers: small wraps in existing functions; no new modules.
* §1.5 / data-raises-caller-logs: data continues to raise; core + UI log and degrade.
* §1.5.1 debug-contract: no new debug-contract lines unless Stage 1 forces a `debug=` edit (default N/A).
* §2.1 config: no new config keys.
* §2.4 batch: no claim/process changes; story still uses latest-per-task refs only.
* §3.3 imports: UI stays on core/utils; no UI→data.
* §3.5 frontend placement: edit existing `components/JobAnalysisReportModal.tsx` only.
* `astral.idioms.require-auth-on-protected-endpoints`: keep `@require_auth` on `detail`.

## Revisions

Revision 1 — 2026-08-08
Driven by: Joan `[plan-discuss] round=1 concern` (fix-now: Stage 1 missing no-reproduction branch; discuss: hydrate fallback re-invokes helper; Conf high vs unreproduced cause).
Changes: Stage 1 step 6 stops on no traceback; Stage 2 hydrate fallback uses precomputed `raw_artifacts` from `jd` (no `get_job_artifacts` in `except`); Stage 4 mandatory forced soft-fail proof for AC2; Conf → Medium.
