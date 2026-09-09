# Tracker generic catalog write/read + job keys + base_resume citation

**Linear:** [AST-1592](https://linear.app/astralcareermatch/issue/AST-1592/tracker-generic-catalog-writeread-job-keys-base-resume-citation-support)
**Parent:** [AST-1588](https://linear.app/astralcareermatch/issue/AST-1588/support-job-artifactsjob-resume-and-job-artifactscover-letteras) — Support `job.artifacts.job_resume` and `job.artifacts.cover_letter` as artifacts
**Publish ref:** `sub/AST-1588/AST-1592-tracker-generic-catalog-write-read-citation`

After AST-1590 (catalog keys) and AST-1591 (`source_artifact_ids`), give tracker the same public catalog write and current-read shape candidate already has for `base_resume` (entity id + artifact key; no per-artifact public function). Route operative writes and backend current-reads for the two job keys through those generics into the artifacts table. On every `job.artifacts.job_resume` write, cite the owning candidate’s then-current `base_resume` `artifact_uuid` as a source (`[]` if none). Rewire jobs API PUT and agent finalize land onto the generic write; remove type-specific public save helpers for these keys (or leave only thin forward shims removed in this epic). Does not own builder/UI consumer inventory (AST-1593).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/tracker.py` — **modified** — add candidate-shaped generic public write and current-read for catalog keys on jobs; route these two keys through them; on job_resume write, resolve current base_resume artifact_id and pass it as a source; remove type-specific public save/hydrate helpers for job_resume / cover_letter; stop job-record SoT writes/reads for those keys
- `src/ui/api/api_jobs.py` — **modified** — GET/PUT for these bodies call the generic tracker functions by catalog key; no new artifact-specific endpoint family
- `src/core/agent.py` — **modified** — finalize / craft-land persist for these two keys calls the generic tracker write only
- `src/core/candidate.py` — **modified** — only if shared catalog resolve/write/read or base_resume current-id lookup must stay DRY with tracker; otherwise untouched

Every row in **Files Changed** is one of those paths (plus this plan doc). Stages only change the kind of work Scope describes for each file.

**Out of this ticket (do not touch):** `src/utils/config.py` / ARTIFACT_CONFIG registration (AST-1590); `src/data/database.py` / DDL (AST-1591); `src/core/builder.py`, ArtifactEditor / JAR / recommendedJobReport (AST-1593); coat-check registration; new body-validation gates beyond what candidate’s catalog str-path already does for `resume_content`; sibling blob keys (`notes`, `resume_content`, `proposed_answers`, `application_responses`); `tests/` / `docs/test-bible/**`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | Add `save_job_artifact` + `get_job_current`; auto-cite base_resume on job_resume write; rewire hydrate / finalize / from-parsed / has-body onto generics; delete type-specific public save helpers (or thin shims only) | core |
| `src/ui/api/api_jobs.py` | PUT handlers for job_resume / cover_letter / legacy resume_content call `save_job_artifact` with catalog keys; detail hydrate path uses `get_job_current` via tracker hydrate | ui |
| `src/core/agent.py` | Finalize body-replica land calls `save_job_artifact` with `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` catalog key (no type-specific persist imports) | core |
| `src/core/candidate.py` | **Untouched** this ticket — Decision below | core |

## Stage 1: Generic public write + current-read + base_resume citation

**Done when:** Tracker exposes `save_job_artifact(astral_job_id, artifact_key, blob, source_artifact_ids=None, *, debug=False) -> Optional[str]` and `get_job_current(astral_job_id, artifact_key, *, debug=False) -> Optional[Any]` with the same calling shape as candidate’s catalog str-path save / `get_candidate_current`. A job_resume write persists `source_artifact_ids` containing the owning candidate’s current `base_resume` `artifact_uuid` when a current row exists, else `[]`. Cover-letter write stores `[]` (or caller-provided list). Unknown / non-job catalog keys raise `ValueError`. No type-specific public function is required to write or read either key.

⚠️ **Decision:** Do **not** touch `src/core/candidate.py`. Tracker already imports `candidate` and `database`; resolve owning `candidate_id` via the existing company chain and call `database.get_current_artifact("candidate", candidate_id, "base_resume")` for the citation uuid. Shared DRY extract is unnecessary for one lookup.

⚠️ **Decision:** Name the write `save_job_artifact` (entity id + catalog key + body + optional sources) rather than overloading `save_job_data`. `save_job_data` remains job_data JSON merge only — catalog operative writes must not share that entry point (epic goal: artifacts table SoT, not job record).

⚠️ **Decision:** For `artifact_key == "job.artifacts.job_resume"`, **always** set sources to the auto-citation list (`[base_resume_uuid]` or `[]`), ignoring any caller-supplied `source_artifact_ids`. Parent AC requires citation on every operative job_resume write; callers must not opt out. Other job catalog keys pass `source_artifact_ids` through to `database.save_artifact` (`None` → data layer `[]`).

1. In `src/core/tracker.py` imports from `src.utils.config`, add `ARTIFACT_CONFIG` (keep existing `BUILD_CONFIG`, `JOB_ARTIFACT_ENTITY_TYPE`, `JOB_EDITABLE_ARTIFACT_TYPES`, `TASK_CONFIG`).

2. Add a private helper `_candidate_id_for_job(astral_job_id: str) -> Optional[str]` next to `_candidate_data_for_job`: same company → `candidate_id` chain; return stripped id string or `None`. Refactor `_candidate_data_for_job` to call it (no behavior change).

3. Add public `get_job_current(astral_job_id: str, artifact_key: str, *, debug: bool = False) -> Optional[Any]`:

   - Strip `artifact_key`; empty → `ValueError("artifact_key required")`.
   - `entry = ARTIFACT_CONFIG.get(key)`; missing → `ValueError(f"unknown catalog key: {key!r}")`.
   - If `entry["entity_type"] != JOB_ARTIFACT_ENTITY_TYPE` (config value `"job"`) → `ValueError(f"catalog key not job-scoped: {key!r}")`.
   - Strip `astral_job_id`; empty → `ValueError("astral_job_id required")`.
   - `artifact_type = key.rsplit(".", 1)[-1]`.
   - `row = database.get_current_artifact(entry["entity_type"], astral_job_id, artifact_type)`.
   - Return `row.get("artifact_data")` if row else `None`.
   - Never read `job_data.artifacts` blobs. No coat-check. Gate any new debug-contract lines on `debug=True` only.

4. Add public `save_job_artifact(astral_job_id: str, artifact_key: str, blob: Any, source_artifact_ids: Optional[Sequence[str]] = None, *, debug: bool = False) -> Optional[str]`:

   - Same key / entity_type / job-id validation as `get_job_current`.
   - If `blob is None` → `ValueError("artifact body required")`.
   - Resolve `shape_name = entry["body_shape"]` and `shape = BUILD_CONFIG["artifact_shapes"][shape_name]`.
   - **Prepare body by catalog key (retain existing prepare/normalize; do not add new validation gates):**
     - If `key == "job.artifacts.job_resume"`: require `isinstance(blob, dict)`; run `_prepare_job_resume_content(blob, _candidate_data_for_job(astral_job_id))`; if no section has body (`_resume_section_has_body`), return `None` without writing (existing empty-skip behavior — not a new coat-check registration).
     - If `key == "job.artifacts.cover_letter"`: `normalized = normalize_cover_letter_artifact(blob)`; if not `_cover_letter_display_nonempty(normalized)`, return `None` without writing; else use `normalized` as body.
     - Else (future job catalog keys): if `shape_name == "resume_content"`, mirror candidate’s required-key check from `save_candidate_data` str-path; otherwise persist `blob` as-is.
   - **Sources:**
     - If `key == "job.artifacts.job_resume"`: `cid = _candidate_id_for_job(astral_job_id)`; if `cid`, `base_row = database.get_current_artifact("candidate", cid, "base_resume")`; `sources = [base_row["artifact_uuid"]]` when `base_row` has a non-empty `artifact_uuid`, else `sources = []`. Do not invent ids. Do not call coat-check / candidate blob fallback.
     - Else: pass `source_artifact_ids` through to `database.save_artifact` (data layer normalizes `None` → `[]`).
   - Call `database.save_artifact(entry["entity_type"], astral_job_id, artifact_type, prepared_body, source_artifact_ids=sources)` and return the new uuid string.
   - Docstring: cite AST-1592 / patt.artifact.write-operative / patt.artifacts.traceability for job_resume→base_resume citation.

5. Place both public functions in the job-artifact section **before** remaining helpers (public-then-helpers). Update the module docstring In-scope line to name `save_job_artifact` and `get_job_current`.

## Stage 2: Route tracker job_resume / cover_letter through generics; retire type-specific public saves

**Done when:** No production path in tracker writes job_resume / cover_letter bodies via direct `database.save_artifact(..., "job_resume"|"cover_letter", ...)` or via the old public type-specific save names. Hydrate and has-body reads use `get_job_current`. Type-specific public save entry points are deleted (preferred) or are one-line forwards to `save_job_artifact` with the catalog key.

1. Rewrite `hydrate_job_artifacts_for_display` so that when `astral_job_id` is known, overlay for the two catalog keys uses `get_job_current(jid, "job.artifacts.job_resume")` and `get_job_current(jid, "job.artifacts.cover_letter")` (then existing `cover_letter_artifact_for_display` for cover). Do **not** call `database.get_current_artifact` with bare leaf types in this overlay loop. Keep pin-resolve for `proposed_answers` unchanged. Keep the no-job-id legacy blob branch unchanged (tests / display without id).

2. Rewrite `job_has_persisted_resume_body` to obtain the body via `get_job_current(astral_job_id, "job.artifacts.job_resume")` instead of `database.get_current_artifact(..., "job_resume")`. Keep the existing legacy blob fallback only when current-read returns None/empty (pre-migration rows).

3. Rewrite `persist_finalize_job_resume_content` to: on match, call `save_job_artifact(astral_job_id, "job.artifacts.job_resume", _resume_payload_body(parsed))` and return whether a uuid was returned (truthy) / match failed → `False`. Same for `persist_finalize_cover_letter_content` → `save_job_artifact(..., "job.artifacts.cover_letter", normalized)`.

4. Rewrite `persist_job_artifact_from_parsed` cover branch to `save_job_artifact(..., "job.artifacts.cover_letter", ...)`. For the resume branch: when `parsed_matches_job_resume_content`, prepare filtered body as today, then call `save_job_artifact(..., "job.artifacts.job_resume", filtered)` — **do not** call `save_job_artifact_resume_content` (that still writes job_data `resume_content` blob and must not be SoT for job_resume).

5. **Delete** public `save_job_artifact_job_resume_body` and `save_job_artifact_cover_letter` once all in-repo call sites (tracker, api_jobs, agent) are rewired. If a brief compile window needs them, replace bodies with thin forwards only:

   ```python
   def save_job_artifact_job_resume_body(astral_job_id: str, resume_body: Dict[str, Any]) -> None:
       save_job_artifact(astral_job_id, "job.artifacts.job_resume", resume_body)
   ```

   Prefer deletion in the same stage commit once api_jobs + agent (Stages 3–4) are updated in the same epic worktree pass — build-child may land Stages 2–4 as separate commits but must not leave deleted symbols referenced.

6. Keep `normalize_cover_letter_artifact`, `cover_letter_artifact_for_display`, `_prepare_job_resume_content`, and `save_job_artifact_resume_content` / `save_job_artifact_notes` (non-catalog sibling blobs). Do **not** add coat-check registration or new body-validation gates.

## Stage 3: `api_jobs` PUT (and display GET path) use generics by catalog key

**Done when:** PUT `/artifacts/job_resume`, PUT `/artifacts/cover_letter`, and legacy PUT `/artifacts/resume_content` persist only via `save_job_artifact` with catalog keys from config. Job detail’s artifact overlay for these keys comes from tracker current-read (via `get_job` / hydrate), not type-specific save imports. No new artifact-specific endpoint family.

1. In `src/ui/api/api_jobs.py`, replace imports of `save_job_artifact_cover_letter` / `save_job_artifact_job_resume_body` with `save_job_artifact` (and keep `hydrate_job_artifacts_for_display` / `get_job` as needed).

2. `put_job_resume_pin_key`: after job-exists + body-is-dict checks, call `save_job_artifact(astral_job_id, "job.artifacts.job_resume", body)` then `{"ok": True}`.

3. `put_job_cover_letter`: same with `"job.artifacts.cover_letter"`.

4. `put_job_resume_content` (legacy URL): same as job_resume — `save_job_artifact(astral_job_id, "job.artifacts.job_resume", body)` (still accepts JSON key `resume_content` as the request field name for wire compat; persist under catalog job_resume).

5. `detail`: ensure overlay uses hydrate **with** `astral_job_id=astral_job_id` so current-read path runs (today the detail re-hydrate omits the id). Prefer relying on `get_job`’s already-overlaid artifacts when present; if re-hydrate remains, pass the job id. Do **not** invent new GET `/artifacts/job_resume` routes — job detail GET is the read surface; sibling AST-1593 owns frontend contract polish.

6. Do not change proposed_answers / application_responses / notes handlers.

## Stage 4: Agent finalize land calls generic write only

**Done when:** `do_task` body-replica land for `finalize_job_resume` / `finalize_cover_letter` calls `save_job_artifact` with the catalog key from `JOB_ARTIFACT_BODY_REPLICA_BY_TASK[task_key]` (already catalog keys after AST-1590). No imports of `persist_finalize_job_resume_content` / `persist_finalize_cover_letter_content` remain in `agent.py` unless those names are deleted and logic inlined.

1. In `src/core/agent.py`, in the `replica_slot = JOB_ARTIFACT_BODY_REPLICA_BY_TASK.get(task_key)` block (~finalize land), replace the `task_key == "finalize_job_resume"` / `finalize_cover_letter` branches that import type-specific persist helpers with:

   - Lazy-import `save_job_artifact` from `src.core.tracker` (and any small private extract helpers still needed).
   - Build the body:
     - For `finalize_job_resume`: reuse the same match + `_resume_payload_body` logic currently inside `persist_finalize_job_resume_content` (either keep that function as a **private** `_persist_finalize_…` in tracker and have it call `save_job_artifact`, or inline the unwrap in agent then call `save_job_artifact(index, replica_slot, body)`). Preferred: keep prepare/match in tracker as private helpers; agent only calls `save_job_artifact(index, replica_slot, prepared)` after a tracker helper returns the prepared body or `None`.
   - Concrete preferred shape (minimize agent logic):

     ```python
     from src.core.tracker import prepare_job_replica_body, save_job_artifact
     body = prepare_job_replica_body(replica_slot, parsed, astral_job_id=index)
     if body is not None:
         save_job_artifact(index, replica_slot, body)
     ```

     Implement `prepare_job_replica_body(catalog_key, parsed, *, astral_job_id)` in tracker: for `job.artifacts.job_resume` run existing match + `_resume_payload_body` (return None if no match); for `job.artifacts.cover_letter` run existing normalize/nonempty (return None if empty); else return None. Then delete public `persist_finalize_*` names.

2. Preserve existing try/except + error log around the land; do not fail the hop on persist errors (same as today).

3. Do not change draft notes pin path, proposed_answers pin path, or candidate craft persist.

4. After Stages 2–4: grep the epic worktree for `save_job_artifact_job_resume_body`, `save_job_artifact_cover_letter`, `persist_finalize_job_resume_content`, `persist_finalize_cover_letter_content` — zero remaining references outside optional deleted definitions.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1588/AST-1592-tracker-generic-catalog-write-read-citation`.
- Do not add files, endpoints, coat-check keys, or body-validation gates not listed above.
- Do not edit `tests/` or `docs/test-bible/**`.
- On ambiguity or codebase drift, stop and comment the **parent** Linear issue with the Stage N blocked template — do not improvise.

## Joan validate

```text
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1592
**Overall:** APPROVED
**Publish ref:** `sub/AST-1588/AST-1592-tracker-generic-catalog-write-read-citation` @ `2bb7b0a1077b71dc7835bf98f4c533702586b680`

## Traceability
AC2 → Stage 1 (`save_job_artifact` + `get_job_current`, catalog-key shape); AC3 → Stage 1 source auto-cite on `job.artifacts.job_resume` (caller cannot override); AC4 → Stages 2–4 (tracker rewire + `api_jobs` PUT + agent finalize land via generic write); AC5 → Stage 2 hydrate / `job_has_persisted_resume_body` + Stage 3 jobs GET/detail overlay (builder live build + full UI load contract → N/A, AST-1593 per ## Boundaries); AC6 → Stage 2 delete/retire type-specific public saves; AC7 → explicit non-goals retained (no coat-check / new validation gates).

## Findings

### acceptable
- **Location:** Child AC5 vs ## Boundaries
- **Finding:** Ticket AC5 quotes parent AC6 (includes builder live build); plan correctly defers builder/frontend consumer rewire to AST-1593 while covering jobs GET + tracker hydrate in-scope.
- **Recommendation:** No plan change; traceability above documents the split.

### acceptable
- **Location:** Stage 2 (`job_has_persisted_resume_body`, hydrate no-id branch)
- **Finding:** Legacy `job_data` blob fallback retained when table current-read is empty (pre-migration / transitional).
- **Recommendation:** Consistent with epic inventory/decommission sibling; not a new SoT write path.

### acceptable
- **Location:** Stage 4 (`prepare_job_replica_body`)
- **Finding:** New tracker helper exported for agent finalize land; could be private `_prepare_job_replica_body`.
- **Recommendation:** Either visibility is fine; prefer private if agent is the sole caller.

**Considered (in-session, slim R7):** Universal orch.* — conform. Scoped core/ui statutes (`import-direction`, `dry-and-focused-functions`, `debug-contract-gated`, `data-raises-caller-logs`, `in-scope-only`, `names-not-ticket-ids`, `public-then-helpers`) — conform. Draft patterns cited (`write-operative`, `read-current`, `traceability`, `manage-catalog`) — conform; `save_job_artifact`/`get_job_current` mirror candidate str-path/current-read shape without overloading `save_job_data`. Depends on AST-1590 `ARTIFACT_CONFIG` + AST-1591 `source_artifact_ids` (stated in plan header).

context_tokens≈52000
```

## Review (build)

**Built @ `6e588366`** — `origin/sub/AST-1588/AST-1592-tracker-generic-catalog-write-read-citation`

Stages 1–4 landed: `save_job_artifact` / `get_job_current` with job_resume→base_resume citation; tracker hydrate/has-body/from-parsed via generics; api_jobs PUT + detail hydrate by catalog key; agent finalize via `prepare_job_replica_body` + `save_job_artifact`; type-specific public save/persist helpers removed. Test path remains Betty `qa-child`.

## Radia review

# Radia review — AST-1592

`[code-rubric] revision=2`
**Rubric:** code-rubric.v2
**Ticket:** AST-1592
**Publish ref:** `sub/AST-1588/AST-1592-tracker-generic-catalog-write-read-citation` @ `e5c94866e67576d3df4fdefc0587e5dcb6659f00`
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1592)` on publish ref. |
| orch.git.commit-vocabulary | universal | conforms | Staged `code` / `test` / `docs` / `merge-tests` commits. |
| orch.git.flow-direction-inviolable | universal | conforms | Child `sub/AST-1588/…` only. |
| orch.git.ftr-sub-topology | universal | conforms | Correct sub topology; `merge-resume` from `ftr` includes blockedBy siblings. |
| orch.git.merge-on-checkout | universal | conforms | No violation in diff. |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | Linear history. |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named branches. |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree pattern OK. |
| orch.git.three-permanent-branches | universal | conforms | Publish ref is `sub/*`. |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No unresolved product forks. |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–4 match implementation. |
| orch.pipeline.project-scoped-queues | universal | conforms | N/A to code. |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed. |
| orch.roles.archie-approves-statutes | universal | conforms | N/A. |
| orch.roles.betty-owns-test-tree | universal | conforms | Test/bible via Betty + `merge-tests`. |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A. |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Hedy assignee through Tests Passed. |
| orch.roles.pre-commit-path-bans | universal | conforms | No hook-ban violations observed. |
| astral.agent.confidence-bounds | scoped | not-applicable | Agent diff is finalize land only; no confidence surface. |
| astral.agent.do-task-delegation | scoped | conforms | Finalize land delegates to tracker `save_job_artifact`; lazy import preserves cycle break. |
| astral.agent.grade-vector-validation | scoped | not-applicable | No grade-vector paths. |
| astral.batch.batch-id-first | scoped | not-applicable | No batch paths changed. |
| astral.batch.batch-id-format | scoped | not-applicable | No batch id paths. |
| astral.batch.claim-process-release | scoped | not-applicable | No claim/clear helpers. |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | No agent_response paths. |
| astral.config.config-source-of-truth | scoped | conforms | Reads `ARTIFACT_CONFIG` / `BUILD_CONFIG` from config; no scattered constants. |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No env/secret changes. |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No debug artifact paths. |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spike paths. |
| astral.dispatch.seed-auto-false | scoped | not-applicable | No dispatch seed paths. |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | Agent finalize land unchanged relative to `run_next` ordering. |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One plan file per ticket. |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty paths are tests/bible only. |
| astral.git.engineer-test-tree-ban | scoped | conforms | Test-tree edits via Betty pipeline. |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Core/UI changes stay in-layer. |
| astral.layers.import-direction | scoped | conforms | `api_jobs` → `tracker` only; `agent` lazy-imports `tracker`; `tracker` → `data` + `utils`. |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No scripts diff. |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | API handlers delegate to tracker by catalog key; no hardcoded state lists added. |
| astral.idioms.coat-check-never-store-empty | scoped | conforms | Empty-body skip retained via existing prepare/normalize; no new coat-check registration. |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No consult/render paths. |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | Existing `@require_auth` on PUT routes unchanged. |
| astral.seed.* (5 statutes) | scoped | not-applicable | No seed paths in diff. |
| astral.standards.data-raises-caller-logs | scoped | conforms | Data layer unchanged in this ticket; tracker raises `ValueError`; agent logs persist errors. |
| astral.standards.database-header-inventory | scoped | conforms | Sibling AST-1591 header inventory present on branch. |
| astral.standards.debug-contract-gated | scoped | conforms | `debug=` kwargs added but no new emission (`_ = debug`); no gated lines without `debug=True`. |
| astral.standards.dry-and-focused-functions | scoped | conforms | `_candidate_id_for_job` extract; `prepare_job_replica_body` centralizes finalize unwrap. |
| astral.standards.in-scope-only | scoped | conforms | `candidate.py` untouched; scope limited to tracker/api_jobs/agent per plan. |
| astral.standards.logging-via-utils | scoped | conforms | No new `print` / raw loggers. |
| astral.standards.names-not-ticket-ids | scoped | conforms | AST cites in comments/docstrings only. |
| astral.standards.no-cross-contamination | scoped | conforms | No out-of-layer imports. |
| astral.standards.no-hardcoded-sets | scoped | conforms | Catalog keys from `ARTIFACT_CONFIG`; no new inline enums. |
| astral.standards.public-then-helpers | scoped | conforms | `save_job_artifact` / `get_job_current` public before private helpers. |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No utils layer changes in AST-1592 product commits. |
| astral.state.core-decides-transitions | scoped | conforms | Artifact writes via tracker entry points; no ad hoc state/data updates. |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job-state machine edits. |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | No run-chain edits. |
| astral.ui.* (3 statutes) | scoped | not-applicable / conforms | UI diff is thin API delegation only. |

**Active set:** 65 statutes scored (18 universal + 47 scoped).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan has no approved-catalog "Patterns to reuse" block; draft pattern prose in Joan attachment only. |

## Plan adherence

**Stages 1–4 delivered as specified.**

- **Stage 1:** `save_job_artifact` / `get_job_current` with catalog-key validation, leaf-type resolution, body prepare by key, and **job_resume always auto-cites** current `base_resume` uuid (caller sources ignored); cover passes `source_artifact_ids` through.
- **Stage 2:** Hydrate overlay, `job_has_persisted_resume_body`, `persist_job_artifact_from_parsed`, and finalize prep route through generics; type-specific public saves removed (`git grep` clean in `src/**`).
- **Stage 3:** `api_jobs` PUT handlers and `detail` re-hydrate with `astral_job_id` call `save_job_artifact` with catalog keys.
- **Stage 4:** Agent finalize uses `prepare_job_replica_body` + `save_job_artifact(replica_slot, …)` with lazy import; error handling preserved.
- **`candidate.py` untouched** per plan decision.
- **Dependencies:** Branch includes merged AST-1590 (`ARTIFACT_CONFIG` + catalog body-replica keys) and AST-1591 (`source_artifact_ids` on `save_artifact`) via `merge-resume` — appropriate for `blockedBy` siblings.

**Estimate 5** matches footprint (tracker refactor + API + agent + Betty test revisions).

## Findings

### advisory

- **`prepare_job_replica_body` is public** — Joan noted private `_prepare_job_replica_body` is acceptable; agent is sole caller today. Optional hygiene for resolve-child, not blocking.
- **`debug=False` kwargs stubbed** (`_ = debug`) on new public functions — fine for AST-1592 (no new debug-contract emission); wire instrumentation later if needed.
- **`docs/test-bible/core/tracker.md` shasum** still says "fill after publish" — Betty/Chuckles doc hygiene; manifest content otherwise matches tests.

## What's solid

- Clean generic API mirrors candidate catalog str-path shape without overloading `save_job_data`.
- `job_resume` → `base_resume` citation is enforced and tested (caller override ignored).
- Hydrate/detail overlay now passes job id so catalog current-read runs in production GET path.
- Zero `src/**` references to deleted type-specific helpers.
- Component tests cover citation, source pass-through, key validation, API PUT wiring, and agent finalize land.

## Frame diff

**AST-1592 product:** `src/core/tracker.py` generics + rewire; `src/ui/api/api_jobs.py` PUT/detail; `src/core/agent.py` finalize land.

**Epic stack on branch (expected):** AST-1590 `config.py`, AST-1591 `database.py`, sibling tests/bible — required foundation for this ticket.

**Out of scope (deferred AST-1593):** builder/UI consumer inventory — correctly untouched.

## Notes

- Joan plan-rubric APPROVED attached; no Excluded-statute straggler list.
- Three-dot diff vs `origin/dev` is wide because `merge-resume` landed sibling children; AST-1592 product slice itself is focused.
- Downstream: AST-1593 should consume `get_job_current` / catalog keys on frontend paths.

context_tokens≈62000

---

```
[code-rubric] PROCEED (Commit: e5c94866) Catalog write/read citation clean
```

## Bug: AST-1600 — Job resume/cover letter not persisting in artifacts table after task success

### As-is

After recommended-job artifact generation hops complete successfully, `job.artifacts.job_resume` and `job.artifacts.cover_letter` are not present as `current=1` rows in the `artifact` table. The job modal therefore has nothing to show from current-read, and Susan’s follow-up requires that modal load use current-read and modal save use the same catalog write path.

### To-be

When `finalize_job_resume` / `finalize_cover_letter` succeed, each hop lands its body through `save_job_artifact` into the artifacts table (with job_resume still citing current `base_resume` when present). Job modal load continues to show bodies from `get_job_current` (via job GET hydrate). Job modal Save continues to PUT through `save_job_artifact` with the catalog key — same write path as finalize land.

### Repro

1. On a RECOMMENDED job for a candidate with an enabled resume structure, run Generate Artifacts through the resume + cover chains until hops report success (including `finalize_job_resume` and `finalize_cover_letter`).
2. Query current artifact rows for that `astral_job_id` with `artifact_type` in (`job_resume`, `cover_letter`) — expect zero / missing currents despite hop success.
3. Open the job modal Artifacts tabs — resume/cover empty (no current body to hydrate).
4. Optional: Edit and Save in ArtifactEditor — PUT `/api/jobs/<id>/artifacts/job_resume` (or `cover_letter`) should still be the write path; after the fix, a successful generate must already have currents before Save.

### Root cause

Two silent no-ops on the AST-1592 finalize land path (compound):

1. **`do_task` body-replica gate requires `resp_id`.** Catalog write only runs when `index and resp_id` after RESPONSE `agent_data` store. Body replica uses in-memory `parsed`, not the pin id — if `_should_store` is false or `_store_response_block` fails, replica is skipped while the hop still returns `success=True`. Pin paths correctly need `resp_id`; body replica must not share that gate.

2. **`save_job_artifact` never passes `candidate_id=` into `database.save_artifact`.** After AST-1597, every artifact INSERT requires a non-empty owning `candidate_id`. Data-layer resolve for `entity_type=job` only JOINs `job → company.candidate_id` and raises `ValueError("candidate_id required")` when that join is blank — it does **not** use denormalized `job.candidate_id` (AST-1598). Tracker’s `_candidate_id_for_job` also ignores `job.candidate_id` and only walks the company chain. Agent wraps the land in `try/except` and logs — hop still succeeds, table stays empty.

Secondary silent path (same symptom): `prepare_job_replica_body` returning `None` or `save_job_artifact` empty-skip (`return None`) with no warning when not `debug` — treat as must-log at WARNING when a mapped replica hop produces no land.

Modal read/write contracts from AST-1592/1593 are already the right shape (GET hydrate → `get_job_current`; PUT → `save_job_artifact`); they fail in UAT primarily because finalize never left a current row.

### Proposed change

⚠️ **Decision:** Fix the land path in `tracker` + `agent` (and tighten data-layer job ownership resolve). Do not add new endpoints or coat-check. Do not change UI components this bug (read/save already on catalog path; empty UI is a missing current row).

1. **`src/core/tracker.py` — `_candidate_id_for_job`:** Prefer non-empty `job["candidate_id"]` from `database.get_job` (AST-1598 denormalized owner). Only if blank, fall back to the existing company → `candidate_id` chain. Still return `None` when neither resolves.

2. **`src/core/tracker.py` — `save_job_artifact`:** After validating the catalog key / preparing the body, resolve `cid = _candidate_id_for_job(jid)`. Call:

   ```python
   database.save_artifact(
       entry["entity_type"],
       jid,
       artifact_type,
       prepared,
       source_artifact_ids=sources,
       candidate_id=cid,
   )
   ```

   If `cid` is `None`, raise `ValueError("candidate_id required")` before the data call (clearer than a late join miss). Keep job_resume auto-citation and empty-body `return None` behavior; do not add new body-validation gates.

3. **`src/data/database.py` — `_resolve_artifact_candidate_id` (job branch):** When caller omits `candidate_id`, resolve in order: (a) `SELECT candidate_id FROM job WHERE astral_job_id = ?` and use if non-empty; (b) else existing `job ⋈ company.candidate_id` lookup; (c) else `ValueError("candidate_id required")`. Explicit non-empty caller `candidate_id` still wins unchanged. No DDL change.

4. **`src/core/agent.py` — body-replica land block:** For `replica_slot` when `result.get("success")` and `index`:

   - Call `prepare_job_replica_body` + `save_job_artifact` **without** requiring `resp_id`.
   - Keep RESPONSE store as today (best-effort ledger).
   - Keep `pin_slot` gated on `index and resp_id` (pins need the agent_data id).
   - On `prepare_job_replica_body` → `None`, or `save_job_artifact` → `None`, `logger.warning` with task_key, index, catalog key, and reason (`prepare_empty` / `save_skipped_empty`) — do not fail the hop.
   - Preserve existing `try/except` + `logger.error` around the land for unexpected raises.

5. **`src/ui/api/api_jobs.py`:** No behavior change required if PUT handlers and `detail(..., astral_job_id=…)` already call `save_job_artifact` / hydrate current-read (AST-1592). Verify only — if a PUT still bypasses `save_job_artifact`, rewire that one handler to the catalog key. Do not add GET `/artifacts/*` routes.

### Blast radius

- **Agent:** Finalize hops land even when RESPONSE store fails; pin tasks unchanged. Betty’s tests that assert `artifact_body_replica … skipped reason=store_failed` will need qa-fix revision (product contract change).
- **Tracker / data:** All `save_job_artifact` callers (API PUT, finalize, `persist_job_artifact_from_parsed`) gain explicit/denormalized `candidate_id` — required for AST-1597 INSERT. Candidate-entity `save_artifact` paths untouched.
- **UI:** No frontend edit; modal Save/load keep current contracts. Builder (`get_job_current`) benefits once currents exist.
- **Sibling AST-1599:** JAR “Source base resume” UI removal stays; this bug does not reintroduce provenance panels.

### What must still hold

- Parent AC2–AC7 / AST-1592: generic `save_job_artifact` / `get_job_current` (entity id + catalog key); job_resume auto-cites current `base_resume` uuid or `[]`; no job-record SoT for these bodies; no type-specific public save helpers; no new coat-check or body-validation gates.
- Cover letter may store empty `source_artifact_ids` (no seed citation this epic).
- Sibling blob keys (`notes`, `resume_content`, `proposed_answers`, `application_responses`) stay out of the catalog.
- Modal read = current-read overlay; modal save = same generic write as finalize.

## Radia review (AST-1600)

# Radia review-fix — AST-1600 (F7)

`[code-rubric] revision=2`
**Rubric:** code-rubric.v2
**Ticket:** AST-1600
**Publish ref:** `sub/AST-1588/AST-1600-job-resume-cover-not-persisting` @ `5e40874c4f2ba66016c47f216a8e01459513b3f0`
**Diff base:** `origin/ftr/AST-1588-job-artifacts-job-resume-cover-letter...origin/sub/AST-1588/AST-1600-job-resume-cover-not-persisting` (fix slice: `agent.py`, `tracker.py`, `database.py` + tests)
**Parent:** AST-1588 (normal UAT-batch — not orphaned)
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1600)` on publish ref. |
| orch.git.commit-vocabulary | universal | conforms | `docs` / `test` / `code` / `merge-tests`. |
| orch.git.flow-direction-inviolable | universal | conforms | Bug `sub/AST-1588/…` on in-flight epic. |
| orch.git.ftr-sub-topology | universal | conforms | Diff base `ftr/AST-1588-…` per fix-lane. |
| orch.git.merge-on-checkout | universal | conforms | N/A to code. |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | Linear history. |
| orch.git.no-dev-agent-branches | universal | conforms | No agent branches. |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree OK. |
| orch.git.three-permanent-branches | universal | conforms | `sub/*` publish ref. |
| orch.pipeline.* (4) | universal | conforms | Fix-lane F7 at Tests Passed. |
| orch.roles.* (5) | universal | conforms | Betty qa-fix + board; engineer product fix. |
| astral.agent.do-task-delegation | scoped | conforms | Finalize land delegates to tracker `save_job_artifact`; lazy import preserved. |
| astral.batch.* | scoped | not-applicable | No batch claim/clear changes. |
| astral.config.* | scoped | not-applicable | No config changes in 1600 commits. |
| astral.debug.* | scoped | not-applicable | No debug spike paths. |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | Land occurs before `run_next`; hop success semantics unchanged. |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Plan-fix patch in `ast-1592-*.md` per `plan-fix` convention. |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty owns tests/bible. |
| astral.git.engineer-test-tree-ban | scoped | conforms | Test-tree via Betty pipeline. |
| astral.layers.import-direction | scoped | conforms | `agent` → `tracker` (lazy); `tracker` → `data`; no UI/external bends. |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Core/data only. |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | No UI changes (verify-only per plan). |
| astral.idioms.coat-check-never-store-empty | scoped | conforms | Empty-body `return None` in `save_job_artifact` retained; new WARNING when land skipped. |
| astral.idioms.* (other 2) | scoped | not-applicable | No auth/consult changes. |
| astral.seed.* | scoped | not-applicable | No seed paths. |
| astral.standards.data-raises-caller-logs | scoped | conforms | Data raises `ValueError`; agent logs WARNING/ERROR at core layer. |
| astral.standards.database-header-inventory | scoped | conforms | No DDL; resolve logic only in existing helper. |
| astral.standards.debug-contract-gated | scoped | conforms | Debug skip path only when `missing_index`; no new debug emission without `debug=True`. |
| astral.standards.dry-and-focused-functions | scoped | conforms | `_candidate_id_for_job` prefer-column-then-chain; single cid resolve in `save_job_artifact`. |
| astral.standards.in-scope-only | scoped | conforms | Agent + tracker + data resolve only; no UI/api_jobs edits. |
| astral.standards.logging-via-utils | scoped | conforms | Uses module `logger` (existing agent pattern). |
| astral.standards.names-not-ticket-ids | scoped | conforms | AST cites in comments only. |
| astral.standards.no-cross-contamination | scoped | conforms | No out-of-layer imports. |
| astral.standards.no-hardcoded-sets | scoped | not-applicable | No new enum sets. |
| astral.standards.public-then-helpers | scoped | conforms | Public `save_job_artifact` updated; private resolve helper in data layer. |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No utils changes. |
| astral.state.core-decides-transitions | scoped | conforms | Writes via tracker `save_job_artifact`; no ad hoc data updates. |
| astral.state.* (other 2) | scoped | not-applicable | No state-machine edits. |
| astral.ui.* | scoped | not-applicable | No frontend diff. |

**Active set:** 65 statutes scored (18 universal + 47 scoped).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | No catalog pattern ids in plan-fix patch. |

## Plan-fix adherence

**Proposed change steps 1–5 delivered.**

| Step | Status |
|------|--------|
| 1. `_candidate_id_for_job` prefers `job.candidate_id`, then company chain | **done** |
| 2. `save_job_artifact` resolves `cid`, raises if missing, passes `candidate_id=` to `save_artifact` | **done** |
| 3. `_resolve_artifact_candidate_id` job branch: job column first, then company JOIN | **done** |
| 4. Agent body-replica land without `resp_id`; pin still gated; WARNING on prepare/save skip | **done** |
| 5. `api_jobs` verify-only — no diff; PUT handlers already call `save_job_artifact` | **verified** |

**Root cause (compound):** Both failure modes addressed — `resp_id` gate removed for body replica; `candidate_id` now flows to INSERT.

**Board:** `[board-joan] CANON: OK`; `[board-betty] TESTS: REVISE` — addressed by qa-fix `[bug-repro]` suite.

## Fix-specific checks

### `[bug-repro]` — **OK**

Three tagged tests, each pins concrete to-be behavior and would fail pre-fix:

| Test | Asserts |
|------|---------|
| `TestAst1600DoTaskBodyReplicaLand::test_bug_repro_body_replica_lands_when_response_store_fails` | `_store_response_block` raises → `save_job_artifact` still called once with `job.artifacts.cover_letter`; no `skipped reason=store_failed` in logs |
| `TestAst1600TrackerCandidateIdLand::test_bug_repro_candidate_id_for_job_prefers_job_column` | Denormalized `job.candidate_id` wins when `company.candidate_id` is null |
| `TestAst1600TrackerCandidateIdLand::test_bug_repro_save_job_artifact_passes_candidate_id` | `database.save_artifact` receives `candidate_id="cand-1600"` |
| `TestAst1600JobArtifactCandidateIdResolve::test_bug_repro_job_write_resolves_cid_via_job_column_when_company_blank` | End-to-end INSERT succeeds with `current["candidate_id"] == "cand-denorm"` when company FK column is NULL |

Obsolete `TestAst1099DoTaskArtifactPin::test_debug_skip_replica_when_store_fails` correctly deleted (blast radius documented in bible).

### `## What must still hold` — **OK**

| Item | Verdict |
|------|---------|
| AST-1592 generic `save_job_artifact` / `get_job_current`; job_resume cites `base_resume` | **holds** — citation path uses resolved `cid` before `get_current_artifact` |
| No job-record SoT; no type-specific public saves | **holds** — unchanged |
| No new coat-check / body-validation gates | **holds** — empty-skip + WARNING only |
| Cover letter may store empty `source_artifact_ids` | **holds** — non-job_resume branch unchanged |
| Sibling blob keys out of catalog | **holds** — not touched |
| Modal read = current-read; modal save = same write as finalize | **holds** — api_jobs unchanged; fix unblocks currents for hydrate |

## Findings

### advisory

- **Susan follow-up (Linear comment):** read current + modal save same path — product contracts were already correct (AST-1592/1593); this fix addresses missing rows after generate. UAT should confirm end-to-end: generate → table current → modal shows body → Save round-trip.
- **Debug path:** when `index` is missing, debug detail is only `missing_index` (no `store_failed` branch for replica) — acceptable; land requires `index` anyway.
- **WARNING on `prepare_empty` / `save_skipped_empty`** — intentional per plan; operators can trace silent skips without failing the hop.

## What's solid

- Fixes both root causes in minimal diff (agent gate + candidate_id ownership).
- Pin path still correctly requires `resp_id`.
- Data-layer resolve matches tracker pass-through (belt-and-suspenders).
- Three-layer `[bug-repro]` coverage (agent, tracker, data) maps to compound root cause.

## Frame diff

**AST-1600 fix (product):**
- `src/core/agent.py` — body replica land gated on `index` only; WARNING on skip paths
- `src/core/tracker.py` — `_candidate_id_for_job` prefers denormalized column; `save_job_artifact` passes `candidate_id=`
- `src/data/database.py` — `_resolve_artifact_candidate_id` job branch prefers `job.candidate_id`

**Tests/bible:** `TestAst1600*` suites in agent/tracker/artifacts; bible § AST-1600 manifests.

**Out of scope (unchanged):** `api_jobs.py`, frontend, builder.

## Notes for Chuckles

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (clean, C7 complete) | Normal AST-1588 UAT-batch | → **Review Posted** → §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped) |

context_tokens≈78000

---

```
[code-rubric] PROCEED (Commit: 5e40874c) Finalize land + candidate_id fix
```

## Bug: AST-1613 — Job artifacts prepare_empty skip after finalize success

### As-is

After a successful `finalize_job_resume` hop (LLM returns a full nested `agent_payload.resume` with section bodies), `do_task` logs `persist_job_artifact_catalog skipped … reason=prepare_empty` and never calls `save_job_artifact`. The artifacts table has zero `entity_type=job` rows for that job.

### To-be

A successful `finalize_job_resume` (and the same catalog land for `finalize_cover_letter` when the cover body is landable) writes an operative `entity_type=job` artifacts-table row for the catalog key (`job.artifacts.job_resume` / `job.artifacts.cover_letter`) so hydrate / `get_job_current` can show it.

### Repro

1. On a RECOMMENDED job with an enabled resume structure, run Generate Artifacts through `finalize_job_resume` until the hop reports success. Confirm the live log line `persist_job_artifact_catalog skipped task=finalize_job_resume … key=job.artifacts.job_resume reason=prepare_empty`.
2. Confirm `do_task`’s in-memory `parsed` at the catalog-land site is still a **string** (raw model text containing the JSON envelope), not a dict — `TASK_CONFIG["finalize_job_resume"]` has no `response_format: "json"`, so the provider path defaults to `text` and leaves `parsed_response` as extracted text.
3. Query the artifacts table for that `astral_job_id` with `entity_type=job` — expect zero rows.
4. Optional same path: `finalize_cover_letter` with a landable `re_line`/`body` under `agent_payload` also hits prepare_empty when `parsed` is still a string.

### Root cause

AST-1600 fixed the `resp_id` gate and `candidate_id` INSERT path; land now runs and WARNINGs fire — but prepare still returns `None`.

`finalize_job_resume` / `finalize_cover_letter` omit `response_format` in `TASK_CONFIG`, so `do_task` uses default `"text"`. Provider parse then sets `parsed_response` to the raw response **string** (`_parse_api_response`), not a JSON dict. The existing `agent_payload` unwrap only runs when `isinstance(parsed, dict)`, so catalog land hands that string to `_prepare_job_replica_body`.

`parsed_matches_job_resume_content` / cover prepare both require a dict → immediate `None` → `reason=prepare_empty`. The hop still returns `success=True` because text-format skips the JSON schema validation block. The landable `agent_payload.resume` (or cover fields) sits inside the string and is never decoded for prepare.

Not the AST-1600 defects (gate / candidate_id); those can already be fixed on this tree. Nested unwrap via `_resume_payload_body` is fine once `parsed` is a dict (envelope or post-unwrap nest both match).

### Proposed change

⚠️ **Decision:** Fix the **shape handed into prepare** inside this ticket’s Scope (`tracker.py` + `agent.py` catalog land). Do **not** edit `src/utils/config.py` to add `response_format: "json"` on finalize rows — that file is outside AST-1613 Component/Technical scope (durable config fix can be a follow-up Scope amend if Archie wants schema validation on finalize too). Do not add endpoints, coat-check, or UI changes. `database.py` untouched (prepare never reaches save today).

1. **`src/core/tracker.py` — coerce helper + `_prepare_job_replica_body`:** Add a private helper (e.g. `_coerce_job_replica_parsed(parsed) -> Any`) used only by prepare:
   - If `parsed` is already a `dict`, return it unchanged.
   - If `parsed` is a non-empty `str`, strip; if it looks like JSON (`{` / `[` after strip, or fenced ```json), parse with `json.loads` (strip markdown fences the same way other core/agent JSON heals do — prefer an existing utils/agent helper already used for RESPONSE text if one is import-safe without a cycle; otherwise local fence strip + `json.loads`). On `JSONDecodeError` / non-dict result, return the original value (prepare will still yield `None`).
   - Other types unchanged.
   
   At the top of `_prepare_job_replica_body`, set `parsed = _coerce_job_replica_parsed(parsed)` before the job_resume / cover_letter branches. Keep existing match + `_resume_payload_body` nest unwrap (`agent_payload` then `draft_job_resume.nested_resume_key`) and cover normalize / nonempty coat-check. Do not add new body-validation gates; true empty still returns `None`.

2. **`src/core/agent.py` — catalog-land branch only:** Before `_prepare_job_replica_body(...)`, if `parsed` is a `str`, coerce via the same tracker helper (lazy import alongside prepare) and pass the coerced value into prepare. Do not reintroduce a `resp_id` gate. Keep WARNING on `prepare_empty` / `save_skipped_empty` and existing `try/except` + `logger.error` for unexpected raises. Do not change pin / draft-notes / candidate-craft branches in this bug.

3. **`src/data/database.py`:** Untouched.

### Blast radius

- **Tracker prepare:** Any caller of `_prepare_job_replica_body` (agent land; tests) gains string→dict coerce. Dict inputs unchanged. Betty will need a `[bug-repro]` that feeds finalize-shaped **string** JSON (envelope with `agent_payload.resume` section bodies) and asserts prepare returns a body / `save_job_artifact` is called — current agent tests mock prepare and inject dict `parsed_response`, so they never catch this.
- **Agent:** Catalog land only; pin path still requires `resp_id`. `pin_experience_job_facts_from_base` still no-ops when `parsed` remains a string earlier in `do_task` — out of this bug’s to-be (artifact row land); do not expand into early global text→JSON coercion for all tasks.
- **Config:** Finalize rows still default `response_format` to `text` (no schema validation). Land works once prepare sees a dict; schema enforcement stays a separate follow-up if Scope is widened.
- **AST-1600:** candidate_id / resp_id fixes remain; this patch is the remaining prepare_empty hole after AST-1603 land-via-artifact_key.

### What must still hold

- Parent AC2–AC7 / AST-1592: generic `save_job_artifact` / `get_job_current`; job_resume auto-cites current `base_resume` uuid or `[]`; no job-record SoT for these bodies; no type-specific public save helpers; no new coat-check or body-validation gates beyond today’s empty → `None`.
- AST-1600: body land ungated on `resp_id`; WARNING on true prepare/save skip; pin still gated on `resp_id`.
- Cover letter may store empty `source_artifact_ids`; sibling blob keys (`notes`, `resume_content`, `proposed_answers`, `application_responses`) stay out of the catalog.
- Modal read = current-read overlay; modal save = same generic write as finalize (unchanged this bug).

## Bug: AST-1614 — Gap: string-JSON prepare/land repro coverage

### As-is

After AST-1613’s product coerce, there is still **no** component test that feeds finalize-shaped **string** JSON (`agent_payload.resume` with section bodies) through `_prepare_job_replica_body` / `do_task` catalog land. Existing suites mock `_prepare_job_replica_body` and inject dict `parsed_response`, so the `prepare_empty` failure mode Betty flagged on AST-1613 never reproduces in CI.

### To-be

At least one tracker test and one agent test (plus bible nodes) assert that finalize-shaped string JSON coerces and lands: prepare returns a landable body, and `do_task` catalog land calls `save_job_artifact` with the catalog key — without mocking prepare to a dict identity.

### Repro (coverage hole)

1. Run the AST-1603 / AST-1554 / AST-1600 agent catalog-land suites — they pass with dict `parsed_response` and/or a prepare mock that returns the dict unchanged when `isinstance(parsed, dict)`, else `None`.
2. Observe: none construct `parsed_response` / prepare input as `json.dumps({agent_performance, agent_payload: {resume: {professional_summary, …}}})` (the text-format finalize shape from AST-1613).
3. Without AST-1613 coerce, that string input yields `prepare_empty`; with coerce, prepare returns a body. No test pins either side today.

### Root cause

Betty’s `[board-betty] TESTS: REVISE` on AST-1613: bible/tests gap — coverage never exercises the string path that caused production `prepare_empty`. Product fix (AST-1613) is already User Testing; this gap child owns only the missing repro coverage.

### Proposed change

⚠️ **Decision:** Tests + bible only — Scope files below. Do **not** change `src/core/tracker.py` / `src/core/agent.py` / `config.py` on this ticket (AST-1613 already landed coerce). Do not invent integration coverage.

1. **`tests/component/core/test_tracker.py` — new class e.g. `TestAst1614StringJsonPrepare`:**
   - Stub `_candidate_data_for_job` → `{}` (default resume structure) so match uses default enabled non-contact sections.
   - Build a finalize-shaped envelope dict: `agent_performance` + `agent_payload.resume` with at least one non-contact section body (e.g. `professional_summary` string; optional non-empty experience job-array).
   - **`test_bug_repro_prepare_lands_finalize_shaped_string_json`:** pass `json.dumps(envelope)` (and optionally a fenced ```json variant) into `_prepare_job_replica_body("job.artifacts.job_resume", …, astral_job_id=…)`. Assert return is a `dict` with the section body present (e.g. `professional_summary == "…"`). Against pre-AST-1613 prepare (no coerce), this assertion fails (`None`).
   - Keep a true-empty control: garbage / non-JSON string → still `None` (coat-check / prepare_empty preserved).
   - Optional one-liner: cover-letter catalog key with string JSON envelope `{agent_payload: {re_line, body, signature}}` → prepare returns nonempty normalized cover — same string path.

2. **`tests/component/core/test_agent.py` — new class e.g. `TestAst1614DoTaskStringParsedCatalogLand`:**
   - Mirror AST-1603 land fixtures (`_agent_rows`, `_patch_strict_batch_anthropic`, stub storage), but:
     - **Do not** monkeypatch `_prepare_job_replica_body` to a dict identity (that hides the bug).
     - Stub `_candidate_data_for_job` / candidate pin as needed so real prepare can match.
     - Stub `save_job_artifact` to capture calls; stub pin so it must not run for finalize.
   - **`test_bug_repro_finalize_string_parsed_lands_save_job_artifact`:** `send_to_anthropic` returns `success=True` with `parsed_response` set to the **string** `json.dumps(envelope)` (finalize nest shape above), not a dict. Assert hop success, `save_job_artifact` called once with `("job-…", "job.artifacts.job_resume", body_dict)` where body has the section, and pin not called. Pre-coerce product: prepare_empty WARNING and save not called.

3. **`docs/test-bible/core/tracker.md`:** Add `### AST-1614 · AST-1610 (gap)` noting string-JSON prepare repro under `TestAst1614StringJsonPrepare`; point agent land to agent.md.

4. **`docs/test-bible/core/agent.md`:** Add matching `### AST-1614` + QA manifest lines naming both new classes (and the `[bug-repro]` node ids above) for `test-fix` / `qa-fix`.

### Blast radius

- **Tests only:** New nodes alongside AST-1554/1600/1603 suites; existing mocks unchanged.
- **Product:** Untouched — relies on AST-1613 `_coerce_job_replica_parsed` already on the epic tree / publish tip when these tests run green.
- **Sibling AST-1613:** Product contract stays; this gap closes Betty’s REVISE diversion without reopening product Scope.

### What must still hold

- AST-1613 coerce behavior: dict inputs unchanged; true empty / non-JSON still `None` + WARNING on land skip; no `resp_id` gate on body land; pin still gated on `resp_id`.
- AST-1592 / AST-1600 invariants: generic catalog write/read; empty → no store; no new coat-check gates; sibling blob keys out of catalog.
- No product edits on this gap ticket; no `response_format: "json"` config change.
