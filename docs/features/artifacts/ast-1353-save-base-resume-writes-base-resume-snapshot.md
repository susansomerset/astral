# AST-1353 — Save Base Resume writes base_resume snapshot

**Linear:** [AST-1353](https://linear.app/astralcareermatch/issue/AST-1353)
**Parent:** [AST-1340](https://linear.app/astralcareermatch/issue/AST-1340) — Create a table called astral_artifacts
**Publish ref:** `sub/AST-1340/AST-1353-save-base-resume-snapshot`

Wire the existing successful Save Base Resume path so that after live `candidate_data.artifacts.base_resume` is persisted, core records that blob into `astral_artifacts` via sibling AST-1352’s `save_astral_artifact` (`entity_type="candidate"`, `artifact_type="base_resume"`, `current=1`). Does **not** create the table/writers, does **not** add restore/Print UI, and does **not** snapshot on Generate/Regenerate.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add `snapshot_saved_base_resume_astral_artifact`; extend module In-scope line | core |
| `src/ui/api/api_candidate.py` | After successful `save_candidate_data` when the PUT included `artifacts.base_resume`, call the new core helper | ui |

**Do not touch:** `src/data/database.py` (AST-1352 owns `save_astral_artifact` / table ensure), `src/ui/frontend/**` (no new Artifacts UI), craft/Generate/Regenerate persist paths that call `database.save_candidate` directly (`parse_candidate_resume`, craft_resume_base success writers in `candidate.py`), `src/utils/config.py`, Print routes (`api_resume_html.py` / AST-1337), `tests/**`, `docs/test-bible/**`, canon pattern catalog files.

**Dependency (already on tree):** AST-1352 is User Testing; `origin/ftr/AST-1340-astral-artifacts-table` (merged into this sub via `sync-child`) exposes `database.save_astral_artifact`, `get_current_astral_artifact`, and `list_astral_artifacts`. Do not reimplement versioning.

## Stage 1: Core snapshot helper + Save Base Resume wire

**Done when:** A successful `PUT /api/candidates/<id>/data` whose body includes `artifacts.base_resume` (the ArtifactEditor Save / autosave path) leaves exactly one `astral_artifacts` row with `current=1` for `(entity_type="candidate", entity_id=<id>, artifact_type="base_resume")` whose `artifact_data` equals the live post-save `artifacts.base_resume`. A second such Save retires the prior row to `current=0` and inserts a new current row (history still listable). Craft/Generate/Regenerate overwrites of live `artifacts.base_resume` that bypass this PUT do **not** call the helper (prior current row remains). No frontend changes.

1. In `src/core/candidate.py` module docstring **In-scope** line, append `snapshot_saved_base_resume_astral_artifact` (AST-1353) so the header inventory of public entry points stays honest.

2. In `src/core/candidate.py`, near the other artifact-save helpers (`apply_rubric_vectors_save` / `apply_company_search_terms_save` region — public functions first), add:

   ```python
   def snapshot_saved_base_resume_astral_artifact(candidate_id: str) -> str:
       """Record live artifacts.base_resume into astral_artifacts after Save Base Resume.

       Reads the post-persist candidate blob so the snapshot matches deep-merged
       candidate_data (AC2). Returns the new astral_artifact_uuid from the data layer.
       """
   ```

   Implementation (literal — do not invent extra kwargs or config):

   - `candidate = database.get_candidate(candidate_id)`; if missing, `raise ValueError` naming the candidate id.
   - `cd = candidate.get("candidate_data") or {}`; if not a `dict`, treat as `{}`.
   - `arts = cd.get("artifacts") or {}`; if not a `dict`, treat as `{}`.
   - `base = arts.get("base_resume")`; if `base is None`, `raise ValueError("artifacts.base_resume missing after save")`.
   - Return `database.save_astral_artifact("candidate", candidate_id, "base_resume", base)`.

   ⚠️ **Decision:** Snapshot **after** live persist and **re-read** via `get_candidate`, not the pre-save PUT payload. `save_candidate` deep-merges nested dicts; AC2 requires the row to match the saved live blob, not only the request fragment.

   ⚠️ **Decision:** Call only from the Save Base Resume API path (step 3). Do **not** invoke from `save_candidate_data` itself or from craft/Generate writers that use `database.save_candidate` — parent AC4 / Boundaries: Regenerate must not replace the last intentional Save snapshot.

   ⚠️ **Decision:** Artifact type string is the literal `"base_resume"` (same contract AST-1352 documented for this sibling). Do not add a new config block for a single epic-scoped type.

3. In `src/ui/api/api_candidate.py` `update_candidate_data`:

   - Import `snapshot_saved_base_resume_astral_artifact` from `src.core.candidate` alongside the existing candidate imports.
   - Before the artifacts processing block (same `try` as today’s save), initialize `base_resume_in_save = False`.
   - Inside the existing gate `if "base_resume" in arts and isinstance(arts["base_resume"], (list, dict)):`, after the ingest/filter assignments that update `arts["base_resume"]`, set `base_resume_in_save = True`.
   - Immediately after the successful `save_candidate_data(candidate_id, body, replace=False, debug=ui_llm_debug())` call (still inside `if body:`), when `base_resume_in_save` is True, call `snapshot_saved_base_resume_astral_artifact(candidate_id)`.
   - Do **not** catch snapshot failures separately — let them fall through the existing `except Exception` → `jsonify({"error": str(e)}), 400` so a failed preserve surfaces as a failed Save response (`astral.standards.data-raises-caller-logs`; UI already returns the error string).

   ⚠️ **Decision:** Wire in the API handler (thin) after core persist, mirroring how `apply_rubric_vectors_save` is orchestrated from `update_candidate_data`, rather than teaching every `save_candidate_data` caller about astral_artifacts. UI still never imports `database`.

4. Do **not** change ArtifactEditor, Base Resume Content Print, or craft_resume_base persistence. UAT for this child is DB/API-level (parent AC5): two successful Saves via the existing PUT, then `get_current_astral_artifact` / `list_astral_artifacts` (or SQL) to verify current-flag + history; optionally overwrite live base_resume via a craft path and confirm the prior `current=1` snapshot row is unchanged.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Review (build stub)

**Publish ref:** `origin/sub/AST-1340/AST-1353-save-base-resume-snapshot`
**Plan path:** `docs/features/artifacts/ast-1353-save-base-resume-writes-base-resume-snapshot.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `6e534039` | `snapshot_saved_base_resume_astral_artifact` + wire after Save Base Resume PUT |

**Tip:** `6e534039` on `origin/sub/AST-1340/AST-1353-save-base-resume-snapshot`

## Joan validate

**Rubric:** plan-rubric.v1
**Ticket:** AST-1353
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1340/AST-1353-save-base-resume-snapshot` @ `cced2c74`

## Traceability
AC2→Stage 1 (core re-read + `save_astral_artifact` after successful PUT persist); AC3→Stage 1 (second PUT with `base_resume` delegates retire-and-insert to AST-1352 writer); AC4→Stage 1 boundary (wire only `update_candidate_data` PUT; craft/Generate/Regenerate use `database.save_candidate` directly — verified `parse_candidate_resume`, `_persist_craft_dispatch_success`, `run_candidate_artifact_generation`); AC5→Stage 1 (no frontend changes; API/DB UAT).

## Findings

### acceptable
- **Location:** Plan structure — no Scope/Conf/Risk self-assessment
- **Finding:** Only `## Estimate` confirm; no formal axes block.
- **Recommendation:** Acceptable for a two-file, single-stage wire; estimate 2 matches footprint.

### discuss
- **Location:** Stage 1 step 3 — autosave path
- **Finding:** `ArtifactEditor` debounced autosave uses the same `PUT …/data` with `artifacts.base_resume`; each successful autosave will snapshot (and retire prior), not only explicit Save clicks.
- **Recommendation:** Plan explicitly names Save/autosave — intentional; operators may accumulate more history rows than manual Save alone. No plan change required unless product wants explicit-Save-only snapshots.

### discuss
- **Location:** Stage 1 step 3 — error handling after `save_candidate_data`
- **Finding:** Snapshot failure after a successful live persist returns 400 (Save failed) while `candidate_data` is already committed; no cross-table transaction.
- **Recommendation:** Reasonable fail-closed surface for this epic; note for UAT that a failed snapshot is a partial persist edge case, not a silent drop.

### acceptable
- **Location:** Stage 1 step 2 — literal `"base_resume"` / `"candidate"`
- **Finding:** No new config block for artifact types; plan documents epic-scoped literal contract matching AST-1352.
- **Recommendation:** Acceptable given sibling writer + parent scope; `ENTITY_TYPES` validation remains in data layer.

**R6 checklist (summary):** Definition fidelity ✓ — Save-path wire only; explicit do-not-touch for table, frontend, craft/Print, backfill. Layer compliance ✓ — `ui` → `core.candidate` → `database.save_astral_artifact`; no `ui`→`data`. Scope ✓ — does not reimplement AST-1352 writers; dependency present on publish ref (`save_astral_artifact` @ database.py). Pattern ✓ — mirrors `apply_rubric_vectors_save` orchestration from `update_candidate_data`. DRY ✓ — single core helper, no duplicate versioning.

**Statute pass (in-session):** All 18 universal orch statutes conform. Considered scoped statutes on `src/core/candidate.py` + `src/ui/api/api_candidate.py` modify — including `astral.layers.import-direction`, `astral.standards.in-scope-only`, `astral.standards.data-raises-caller-logs`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.no-hardcoded-sets` — all `conforms`; no `violates`.

context_tokens≈52000

## Radia review

# Radia review — AST-1353

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1353
**Publish ref:** origin/sub/AST-1340/AST-1353-save-base-resume-snapshot @ de0e559863b7f3d53c5cdedd1cb70f660f63458d
**Overall:** CLEAN
```

**Diff baseline:** `origin/dev...origin/sub/AST-1340/AST-1353-save-base-resume-snapshot` (16 files, +1239/−8)

**AST-1353 product commit:** `6e534039` — `src/core/candidate.py` + `src/ui/api/api_candidate.py` only (+30/−1)  
**Tests/docs:** Betty `merge-tests` tip `de0e5598` (expected per `orch.git.betty-merge-tests-one-sha`)

**Note:** Three-dot diff vs `origin/dev` also carries sibling **AST-1352** (`database.py` writers + data tests) not yet on `dev`; publish ref correctly includes that dependency for end-to-end Save→`astral_artifacts` proof.

---

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent confidence paths |
| astral.agent.do-task-delegation | scoped | not-applicable | no do_task/dispatcher changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch-id emission |
| astral.batch.batch-id-format | scoped | not-applicable | no batch-id formatting |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/process/release helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no entity_agent_responses changes |
| astral.config.config-source-of-truth | scoped | not-applicable | no config-block edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env wiring |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifact dirs |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no debug spikes |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch seed paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run_next changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single AST-1353 plan doc |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty-owned tests/test-bible; engineer `code()` is two `src/` files only |
| astral.git.engineer-test-tree-ban | scoped | conforms | product commit excludes `tests/**` |
| astral.layers.core-vs-external-bright-line | scoped | conforms | core orchestrates snapshot; data persists; no external I/O |
| astral.layers.import-direction | scoped | conforms | `ui/api` → `core.candidate` only; no `ui`→`data` |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` changes |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | no frontend/hardcoded state; API thin orchestration |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no render/verdict paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | wire on existing `@require_auth` PUT handler |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed JSON |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed catalog |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no boot seed |
| astral.seed.define-approved | scoped | not-applicable | no define flow |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator rows |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage join |
| astral.standards.data-raises-caller-logs | scoped | conforms | snapshot raises `ValueError`; API `except Exception` → 400 JSON |
| astral.standards.database-header-inventory | scoped | conforms | sibling AST-1352 inventory on publish ref; 1353 does not add tables |
| astral.standards.debug-contract-gated | scoped | not-applicable | no new `debug=` emission on snapshot path |
| astral.standards.dry-and-focused-functions | scoped | conforms | single core helper; API flag + one call |
| astral.standards.in-scope-only | scoped | conforms | Save PUT wire only; no table reimplementation, no frontend, no craft-path snapshot |
| astral.standards.logging-via-utils | scoped | conforms | no new logging on touched paths |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain-named `snapshot_saved_base_resume_astral_artifact` |
| astral.standards.no-cross-contamination | scoped | conforms | uses AST-1352 `save_astral_artifact`; no duplicate versioning |
| astral.standards.no-hardcoded-sets | scoped | conforms | literal `"candidate"` / `"base_resume"` documented epic contract; `ENTITY_TYPES` check in data layer |
| astral.standards.public-then-helpers | scoped | conforms | public snapshot helper; private logic inline per plan |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no `src/utils/**` product changes |
| astral.state.core-decides-transitions | scoped | not-applicable | no state transition changes |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job state |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend files |
| astral.ui.naming-conventions | scoped | not-applicable | no UI files |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip is `merge-tests(AST-1353): origin/tests b8b8771d` |
| orch.git.commit-vocabulary | universal | conforms | `code` / `docs` / `test` / `merge-tests` |
| orch.git.flow-direction-inviolable | universal | conforms | sub publish; no dev bypass |
| orch.git.ftr-sub-topology | universal | conforms | child on `sub/AST-1340/AST-1353-…` |
| orch.git.merge-on-checkout | universal | conforms | clean child history |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no rebase/cherry-pick signals |
| orch.git.no-dev-agent-branches | universal | conforms | no agent branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-1340` |
| orch.git.three-permanent-branches | universal | conforms | diff vs `origin/dev` |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Joan discuss items documented; no unresolved product fork in code |
| orch.pipeline.plan-is-bible | universal | conforms | implementation matches Stage 1 literal |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Artifacts child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed gate satisfied |
| orch.roles.archie-approves-statutes | universal | conforms | no statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/test-bible via Betty |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to diff |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path commits |

**Active corpus swept:** 64 statutes on tree.

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.layers.import-discipline | conforms | `api_candidate` → `core.candidate` → `database.save_astral_artifact`; no `ui`→`data` (Joan R6) |
| *(in-file orchestration)* | conforms | mirrors `apply_rubric_vectors_save` post-persist call pattern from `update_candidate_data` |
| pattern.data.versioned-current-row | not cited | parent-proposed catalog entry still undrafted; delegates versioning to AST-1352 writer |

---

## Plan adherence

**Stage 1 — all plan steps satisfied:**

1. **Core helper** `snapshot_saved_base_resume_astral_artifact` — re-reads via `database.get_candidate`, `or {}` guards per plan literal, raises on missing candidate/base_resume, calls `save_astral_artifact("candidate", candidate_id, "base_resume", base)`.
2. **In-scope docstring** — appended on module header line.
3. **API wire** — `base_resume_in_save` flag inside existing `base_resume` list/dict gate; set after ingest/filter; snapshot after successful `save_candidate_data`; no separate catch; errors fall through outer `except Exception` → 400.
4. **Boundaries held** — no `database.py`, frontend, craft/Print, or `config.py` changes in product commit; craft/Generate paths verified by tests (`run_candidate_artifact_generation`, direct `save_candidate`).

**Estimate 2:** Footprint matches (two product files, single stage).

**Joan plan-rubric:** APPROVED @ `cced2c74`; no Excluded-statute stragglers.

**C6 lenses:** Layer/imports OK; `or {}` fallbacks plan-mandated; no silent swallows; no debug/LLM/external surfaces on new paths; `@require_auth` preserved.

---

## Findings

### fix-now

*(none)*

### discuss

- **Partial persist on snapshot failure (Joan plan discuss):** If `save_candidate_data` succeeds but `snapshot_saved_base_resume_astral_artifact` raises, client gets 400 (“Save failed”) while live `candidate_data` is already committed — no cross-table transaction. Plan-chosen fail-closed surface; flag for UAT/operators, not a code defect on this child.
- **Autosave snapshots (Joan plan discuss):** Debounced ArtifactEditor autosave uses the same PUT with `artifacts.base_resume`; each successful autosave retires/inserts history, not only explicit Save clicks. Plan names Save/autosave — intentional; product may want explicit-Save-only later (parent/epic decision).

### advisory

- **Publish ref stacks AST-1352:** Three-dot diff vs `dev` includes sibling table/writers until epic lands; UAT on this ref is correct integration shape.
- **Parent catalog `pattern.data.versioned-current-row`:** Still undrafted on AST-1340; wire correctly delegates to AST-1352 — Archie/parent owns catalog harvest.

---

## What's solid

- Engineer footprint is exactly two files — tight scope for estimate 2.
- Post-persist re-read satisfies AC2 (snapshot matches deep-merged live blob, not just PUT fragment).
- AC4 boundary tested at core (`craft_generation` does not call `save_astral_artifact`) and API (`direct save_candidate` leaves snapshot UUID unchanged).
- Existing mocked PUT tests revised to stub snapshot — prevents regressions when `save_candidate_data` is mocked.
- Betty manifest covers core helper, API wire, AC4, and sibling writer regression.

---

## Frame diff

(none)

---

## Notes

- Joan plan-rubric verdict attached; no straggler exclusions violated.
- C7 complete; recommend Chuckles append to issue doc, commit `docs(AST-1353): Radia review — clean`, post slim upshot, advance to **Review Posted** → **User Testing** (PROCEED).

context_tokens≈24000
