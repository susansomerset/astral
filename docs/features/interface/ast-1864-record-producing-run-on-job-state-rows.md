# AST-1864 — Record the producing run on each job state row (Execution History for job modals)

- **Parent:** AST-1853 — Execution History for job modals
- **Ticket:** AST-1864
- **Publish ref:** `sub/AST-1853/AST-1864-record-producing-run-on-job-state-rows` (origin only)
- **Canon Scope:** `astral.entity.required-metadata`

Every new job `state_history` entry written inside a run gets a `run_id` key holding the id of the
run that actually wrote the logs and agent data — the active `log_batch_id` context var. For
single-hop dispatch that is the dispatch batch id (same value as the job's `batch_id`); for
chained tasks it is the per-hop ledger id opened by `agent._open_run_next_hop_ledger`, which
differs from the job's claim `batch_id`. When no run is active (operator skip / edit, API
transitions), `run_id` is **absent**. The existing `batch_id` key is unchanged. Backend only;
sibling AST-1853 child #2 (Ada) reads `run_id` and falls back to `batch_id`.

## Code facts this plan relies on (verified on this ref)

- `src/utils/logging.py:49` — `log_batch_id: ContextVar[Optional[str]]`, default `None`.
- `src/core/dispatcher.py` sets `log_batch_id` to `entity_batch_id` around each dispatch run and
  resets it to `None` in `finally`.
- `src/core/agent.py:3002–3020` — `_open_run_next_hop_ledger` writes a `dispatch_ledger` row with
  id `f"{task_key}-{uuid}"` and sets `log_batch_id` to it for the hop.
- `src/core/agent.py:2782–2867` — on a chained hop's success, `_write_dispatch_hop_label_on_success`
  (→ `tracker.write_job_dispatch_hop_label`) and `_maybe_graduate_dispatch_chain`
  (→ `tracker.graduate_job_from_dispatch_chain` → `tracker.transition_job_state`) both run
  **before** `_close_hop_ledger(..., clear_log=True)` clears the context. The hop-failure
  error-state transition (`agent.py:1142`) runs inside `_close_hop_ledger` before finalize/clear.
  So `log_batch_id` holds the hop id at every chained write.
- Job `state_history` rows are appended by two transition functions in `src/core/tracker.py`:
  `write_job_dispatch_hop_label` (line 1416 — the per-hop `BUILD_ARTIFACTS.<hop>` rows of a chain)
  and `transition_job_state` (line 1455 — every registered-state transition, incl. chain
  graduation and chain error states). `ingest_jobs` / `save_meteorite_job` write a job's
  creation row, not a transition, and stay untouched.
- API transitions (`src/ui/api/api_jobs.py:204, 448, 537`) run with no run context →
  `log_batch_id.get()` is `None` → no `run_id` (AC3).

## Scope gate

Ticket `## Scope` names `src/core/tracker.py` only, change kind: "the job state-transition
function that appends `state_history` … each new history entry also records the current run's
audit id (the active log batch context set per hop / per dispatch) … existing `batch_id` key stays
… when no run context is active the new key is absent … key name is `plan-child`'s call."
Every change below is in that file and is that kind of change. No file under `src/ui/api/` or
`src/data/` is touched (AC4).

⚠️ **Decision (key name):** `run_id`. Short, matches the ticket's "run-id key" wording, and
`rg '\brun_id\b' src` has zero hits today, so nothing collides.

⚠️ **Decision (two appenders, one helper):** Scope says "the job state-transition function"
(singular), but chained runs write their per-hop state rows through `write_job_dispatch_hop_label`,
not `transition_job_state`. Stamping only `transition_job_state` would leave every chain hop row
without its hop run id — the exact case parent Functional scope #4 exists for. Both functions get
the stamp through one small private helper so the rule lives in one place. Same file, same kind
of change the Scope describes; no new capability.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | Import `log_batch_id`; new private helper `_stamp_run_id`; call it from `write_job_dispatch_hop_label` and `transition_job_state` | core |

## Stage 1: Stamp `run_id` on job state-history entries

**Done when:** with `log_batch_id` set to `H`, both `transition_job_state` and
`write_job_dispatch_hop_label` append an entry with `run_id == "H"` and `batch_id` equal to the
job's `batch_id`; with `log_batch_id` unset (`None`) or `""`, the appended entry has no `run_id`
key at all. `python3 -m py_compile src/core/tracker.py` passes.

1. In `src/core/tracker.py`, change the import at line 50 from
   `from src.utils.logging import get_logger, truncate_debug_content` to
   `from src.utils.logging import get_logger, log_batch_id, truncate_debug_content`.

2. In `src/core/tracker.py`, immediately **above** `def write_job_dispatch_hop_label` (line 1416),
   add exactly this function:

   ```python
   def _stamp_run_id(entry: Dict[str, Any]) -> Dict[str, Any]:
       """Add run_id = the active run's audit id (log_batch_id) to a job state_history entry (AST-1864).

       Chained hops set log_batch_id to their own hop ledger id, so run_id can differ from the
       claim batch_id. No active run (operator/API transition) -> key left absent, never None/"".
       """
       run_id = log_batch_id.get()
       if run_id:
           entry["run_id"] = run_id
       return entry
   ```

3. In `write_job_dispatch_hop_label`, wrap the appended dict in `_stamp_run_id(...)`. Result:

   ```python
   history.append(_stamp_run_id({
       "to_state": label,
       "timestamp": now,
       "batch_id": job.get("batch_id"),
   }))
   ```

   No other line in the function changes.

4. In `transition_job_state`, change the entry construction line from
   `entry: Dict[str, Any] = {"to_state": to_state, "timestamp": now, "batch_id": job.get("batch_id")}`
   to
   `entry: Dict[str, Any] = _stamp_run_id({"to_state": to_state, "timestamp": now, "batch_id": job.get("batch_id")})`.
   The following `score` handling, `history.append(entry)`, and `save_job` call stay as-is.

5. Update the `transition_job_state` docstring: after the `score:` line, add one line:
   `run_id: stamped from log_batch_id when a run is active; absent otherwise (AST-1864).`

6. Compile: `python3 -m py_compile src/core/tracker.py`. No `.ts`/`.tsx` changed, so no `tsc`.

7. Scope check before commit:
   `git diff origin/dev -- src/ui/api/ src/data/` must be empty, and `git diff --stat origin/dev`
   (product files) must list only `src/core/tracker.py` plus this plan doc.

8. Commit on the epic worktree: `code(AST-1864): stamp run_id on job state_history entries`;
   publish with `git push origin HEAD:sub/AST-1853/AST-1864-record-producing-run-on-job-state-rows`.

⚠️ **Decision (no tests in build):** AC1–AC3 tests in `tests/component/core/test_tracker.py` are
Betty's (`qa-child`). Existing tracker tests assert individual keys (`to_state`, `score`), not
whole-entry dict equality, and `log_batch_id` defaults to `None`, so the absent-by-default key
does not disturb them.

## Out of scope (reference only)

- All frontend reading of `run_id` / fallback to `batch_id` — AST-1853 child #2 (Ada).
- Company transitions (`roster.transition_company_state`), candidate hop labels, job creation rows
  (`ingest_jobs`, `save_meteorite_job`) — not job state transitions per this ticket.
- Back-matching old chained rows — forbidden (Susan: forward-only).

## Canon alignment

`astral.entity.required-metadata`: no column added, renamed, dropped, or repurposed. `batch_id`
column and the `batch_id` key inside history entries keep their current meaning. The new key
lives inside `state_history` JSON entries, which already carry optional keys (`score`).
Note: `docs/canon-index.md` is not present on this ref; the id was resolved directly to
`canon/directives/active/stat.entity.required-metadata.md`.

## Estimate

Confirm Chuckles estimate: 2 — revise to 1 because the change is one helper plus two call sites in a single file, with no schema or API contract change.


## Joan validate

[plan-rubric]
**Ticket:** AST-1864
**Overall:** APPROVED
**Corpus:** e1f2699fad
**Publish ref tip:** b45705c1

## Canon scores
astral.entity.required-metadata | X | | applies_when targets `src/data/database.py`; plan only modifies `src/core/tracker.py` — column-set statute is not in mechanical territory for this diff; plan § Canon alignment still commits to no column/API change and preserves `batch_id` semantics (Radia should grade the landed diff the same way).

## Traceability
AC1→Stage 1 (`transition_job_state` + `log_batch_id`); AC2→Stage 1 (`write_job_dispatch_hop_label` + chained hop context); AC3→Stage 1 (absent `run_id` when no context; modal clickability → sibling #2 per Boundaries); AC4→Stage 1 steps 7–8 (empty `src/ui/api/` + `src/data/` diff).

### Findings

**acceptable** — `## Scope gate` / two-appender decision: Scope text names one “state-transition function,” but `write_job_dispatch_hop_label` is the chained per-hop appender; plan documents why both need `_stamp_run_id` and keeps all edits in `tracker.py`. Matches parent Functional scope #4 (per-hop run id).

**discuss** — Child AC3 quotes “row is not clickable in the modal”; this child is backend-only. Plan correctly defers UI to AST-1853 child #2; Betty’s `qa-child` should assert key absence here and leave clickability to the frontend child (already partitioned in parent Scope).

**acceptable** — Tests deferred to `qa-child` per workflow; plan cites why existing tracker tests stay green (`log_batch_id` default `None`, partial key asserts).

**acceptable** — Code-facts block (dispatcher `log_batch_id`, hop ledger open/close ordering, API skip paths) matches current `agent.py` / `tracker.py` on this worktree; chained graduation and hop-failure transitions run before `log_batch_id` clear.

context_tokens≈28000

## Review

- **Code commit:** `23d6145d` on `origin/sub/AST-1853/AST-1864-record-producing-run-on-job-state-rows`
- **Diff:** `src/core/tracker.py` only (+17 / −4). `git diff origin/dev -- src/ui/api/ src/data/` empty.
- **Built as planned:** Stage 1 steps 1–8, no deviation.
- **Compile:** `python3 -m py_compile src/core/tracker.py` OK (no `.ts`/`.tsx` changed; no Python linter configured in repo).
- **Existing tests (read-only run):** `tests/component/core/test_tracker.py` → 135 passed, 20 failed. The same 20 fail on the pre-change tree
  (identical `FAILED` list): `TestAst562ArtifactBuildTransitions` ×6, `TestAst551StructureAlignedResumeChain` ×3,
  `TestAst733InitializeJobCollision` ×3, `TestGetJobData` ×3, `TestAst1693SaveMeteoriteDuplicateLinkBackfill` ×2,
  `TestAst1523NotesMetadataRetention`, `TestAst552BuildArtifactsGate`, `TestAst997ExperienceJobArrayPersist`. Not caused by this change.
- **Sub-log pre-check:** `validate-sub-log.sh --stage=build … ftr/AST-1853-execution-history-for-job-modals` → ok.


## Radia review

[code-rubric]
**Ticket:** AST-1864
**Publish ref:** 5ccfca280ff0f387fa5e82e394685ae286774a93
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores
astral.entity.required-metadata | X | | `applies_when` is `src/data/database.py` add/modify only; landed diff touches `src/core/tracker.py` + tests/bible — no column-set change; optional `run_id` inside `state_history` JSON parallels existing `score`; `batch_id` column and history key unchanged

## Column diff vs plan stage
(aligned) — Joan graded `astral.entity.required-metadata` **X** for the same territorial reason; landed product diff matches that rationale.

## Frame diff
(none)

## Findings

### fix-now
(none)

### discuss
(none)

### advisory
- **sibling test carry:** none — `tests/component/core/test_tracker.py` and `docs/test-bible/core/tracker.md` AST-1864 blocks belong to this child (Betty `qa-child` / `merge-tests`), not a sibling product leak.
- **docs/test-bible/core/tracker.md** — `**Bible shasum (publish tip):**` still shows `*(filled after publish)*`; hygiene only for Chuckles doc pass, not a product gate.
- **Linear AC3** still bundles “row is not clickable in the modal” with backend stamping; implementation and `TestAst1864RunIdStamp` correctly assert key absence only; clickability remains sibling #2 per Boundaries (already Joan-noted at plan stage).

## What's solid
- `_stamp_run_id` matches plan verbatim: truthy `log_batch_id` stamps `run_id`; `None` / `""` leave the key absent (never `null`/empty string values).
- Both appenders (`write_job_dispatch_hop_label`, `transition_job_state`) share one helper; `score` still applied after stamp on transitions.
- `TestAst1864RunIdStamp` covers AC1 (single-hop), AC2 (hop label + graduation path via `transition_job_state`), AC3 (parametrized `None`/`""`, both appenders); manifest regression classes named in bible.
- AC4: `git diff origin/dev...origin/sub/AST-1853/AST-1864-record-producing-run-on-job-state-rows -- src/ui/api/ src/data/` is empty.
- Plan fidelity: product change is Stage 1 as written; estimate footprint still fits confirmed **1** point.

## Recommended actions (downstream — not Radia)
- Chuckles: append this artifact, commit `docs(AST-1864): Radia review — clean`, post slim upshot, move to **Review Posted**; datt **PROCEED** → **User Testing** per mapping.
- Optional doc tidy: fill bible shasum line on publish tip when touching the issue doc anyway.

context_tokens≈32000
