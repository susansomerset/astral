# Generic save_candidate_data + agent craft-persist rewire

**Linear:** [AST-1576](https://linear.app/astralcareermatch/issue/AST-1576/generic-save-candidate-data-agent-craft-persist-rewire-implement)
**Parent:** [AST-1569](https://linear.app/astralcareermatch/issue/AST-1569/implement-pattartifactwrite-operative) — Implement patt.artifact.write-operative
**Publish ref:** `sub/AST-1569/AST-1576-generic-save-candidate-data`

Ship write-operative for the pilot catalog key `candidate.artifacts.base_resume`: blind `database.save_artifact` (already retire+insert), entity-owned `save_candidate_data(candidate_id, artifact_key, blob)` against `ARTIFACT_CONFIG`, `TASK_CONFIG["craft_resume_base"]["artifact_key"]`, rewire agent / parse / UI save to that generic path, delete `artifact_catalog`. Does **not** own React editor or `patt.artifacts.ui-consistency` (sibling AST-1577).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/data/database.py`
- `src/utils/artifact_catalog.py` (**deleted**)
- `src/utils/config.py`
- `src/core/candidate.py`
- `src/core/agent.py` (craft-persist rewire)
- `src/ui/api/api_candidate.py`
- Betty delete/retarget catalog wrapper tests (engineer does **not** edit `tests/` or `docs/test-bible/**`)

Every row in **Files Changed** is one of those product paths (plus this plan doc). Every Stage step is the kind of change Scope describes for that file.

**Out of this ticket (do not touch):** React `ArtifactEditor` / `ArtifactsBaseResumeContent`; `canon/directives/draft/patt.artifacts.ui-consistency.md`; new `ARTIFACT_CONFIG` keys; coat-check; grade pin writers; job finalize / `job_resume` writers; inventing a one-off API `artifact_id` field or ban.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Confirm / lock blind retire+insert `save_artifact` (no prior-id lookup, no in-place body UPDATE); docstring cites write-operative | data |
| `src/utils/config.py` | Add `TASK_CONFIG["craft_resume_base"]["artifact_key"] = "candidate.artifacts.base_resume"` + assert; drop catalog-helper coupling notes | utils |
| `src/utils/artifact_catalog.py` | **Delete** module | utils |
| `src/core/candidate.py` | Dual-dispatch `save_candidate_data` operative path; retarget parse / UI-facing craft land; hydrate pilot from `get_current_artifact`; remove `snapshot_saved_base_resume_artifact` + craft_resume_base branch of `_persist_craft_dispatch_success` | core |
| `src/core/agent.py` | On `persist_candidate_craft_hops` success for tasks with `artifact_key`, call generic operative save (not `_persist_craft_dispatch_success` for pilot) | core |
| `src/ui/api/api_candidate.py` | Pilot body save → generic `save_candidate_data(candidate_id, artifact_key, blob)`; hydrate on GET; keep `_sanitize_candidate` response | ui |

**Betty-owned (not engineer `code()`):** delete or retarget `tests/component/utils/test_artifact_catalog.py` + `docs/test-bible/utils/artifact_catalog.md` after product delete.

## Stage 1: Lock `save_artifact` write-operative contract

**Done when:** `database.save_artifact` is the sole data-layer pilot write; it blind-retires by `(entity_type, entity_id, artifact_type)` then inserts a new `current=1` UUID row and returns that uuid; there is no prior-id SELECT and no in-place `artifact_data` UPDATE.

1. In `src/data/database.py`, open `save_artifact`. Confirm the body already matches this contract (today: `UPDATE … SET current = 0 WHERE … AND current = 1` then `INSERT` new uuid; return `new_uuid` inside one connection / retry wrapper).
2. Update the `save_artifact` docstring to state explicitly: blind retire-by-key + insert (patt.artifact.write-operative); never SELECT prior uuid first; never UPDATE body in place.
3. If any SELECT-of-prior-id or body `UPDATE` path exists inside `save_artifact`, remove it so only blind retire + insert remain. Do **not** change the public signature `(entity_type, entity_id, artifact_type, artifact_data) -> str`. Do **not** add new read helpers.

## Stage 2: Config — `craft_resume_base` artifact_key

**Done when:** `TASK_CONFIG["craft_resume_base"]["artifact_key"] == "candidate.artifacts.base_resume"` and a startup assert ties that string to the sole `ARTIFACT_CONFIG` key. No new catalog keys.

1. In `src/utils/config.py`, inside `TASK_CONFIG["craft_resume_base"]`, add:

```python
"artifact_key": "candidate.artifacts.base_resume",
```

Place it after the existing keys (`response_schema`, `response_format`, `context_format`, `entity_type`, `requires_candidate_key`, `trigger_state`) — same dict, no other craft keys gain `artifact_key` this ticket.

2. Immediately after the existing `ARTIFACT_CONFIG` asserts block (the block that ends with `assert set(_br.keys()) == {…}`), add:

```python
assert TASK_CONFIG["craft_resume_base"]["artifact_key"] == "candidate.artifacts.base_resume"
assert TASK_CONFIG["craft_resume_base"]["artifact_key"] in ARTIFACT_CONFIG
```

3. In the module docstring **Config sections** line for `ARTIFACT_CONFIG`, if any wording implies a Python accessor module / `artifact_catalog`, reword so config is the SoT and callers import `ARTIFACT_CONFIG` from config (manage-catalog + this ticket: no wrapper module).

4. Do **not** add keys to `ARTIFACT_CONFIG`. Do **not** change `body_shape` / `entity_type` / `ingestion_owner` for the pilot.

## Stage 3: Delete `artifact_catalog`

**Done when:** `src/utils/artifact_catalog.py` is gone; no product import of that module remains under `src/`.

1. Delete `src/utils/artifact_catalog.py`.
2. Grep `src/` for `artifact_catalog` / `get_catalog_entry` / `require_catalog_entry` / `is_candidate_scoped`. There are no product callers today; if any appear, retarget them to `ARTIFACT_CONFIG[...]` lookups in the owning Scope file only (candidate / config / api_candidate / agent — not new files).
3. Do **not** edit `tests/` or bible — Betty deletes/retargets wrapper tests in `qa-child`.

## Stage 4: Generic `save_candidate_data` + candidate callers + hydrate

**Done when:** Operative writes for the pilot go through `save_candidate_data(candidate_id, artifact_key, blob)` → `ARTIFACT_CONFIG` → `database.save_artifact`; library blob merge still works for existing dict callers; `craft_resume_base` land / parse no longer blob-write `artifacts.base_resume`; GET hydrate surfaces operative current via `get_current_artifact`; `snapshot_saved_base_resume_artifact` and the `craft_resume_base` branch of `_persist_craft_dispatch_success` are removed.

⚠️ **Decision:** Keep the existing library-merge function name `save_candidate_data(candidate_id, data: dict, …)` used across intake/contact/etc. (those files are **out of Scope**). Add an **operative overload** on the same symbol via second-argument type: when `second` is `str`, treat it as `artifact_key` and require `blob` as the third positional arg; when `second` is `dict`, keep today’s merge behavior. Do not rename the library path this ticket.

1. Update `src/core/candidate.py` module docstring **In-scope** line: replace `snapshot_saved_base_resume_artifact` with operative `save_candidate_data(candidate_id, artifact_key, blob)` / hydrate via `get_current_artifact` (AST-1576).

2. Change `save_candidate_data` to dual-dispatch:

```python
def save_candidate_data(
    candidate_id: str,
    data_or_artifact_key: Any,
    blob: Any = None,
    replace: bool = False,
    *,
    debug: bool = False,
) -> Optional[str]:
```

- **Operative path** (`isinstance(data_or_artifact_key, str)`):
  - `artifact_key = data_or_artifact_key.strip()`; reject blank with `ValueError`.
  - Look up `entry = ARTIFACT_CONFIG.get(artifact_key)`; if missing → `ValueError(f"unknown catalog key: {artifact_key!r}")`.
  - Import `ARTIFACT_CONFIG` from `src.utils.config` at module top (with other config imports).
  - Validate body against catalog `body_shape`:
    - Resolve `shape = BUILD_CONFIG["artifact_shapes"][entry["body_shape"]]`.
    - If `blob is None` → `ValueError("artifact body required")`.
    - For pilot `resume_content`: require `isinstance(blob, dict)`; reject empty dict; require every `required: True` key in `shape` to be present on `blob` (presence only — do not re-implement experience-array deep validation here; callers that already normalize via `ingest_legacy_label_content_base_resume` / `filter_base_resume_to_structure` / `split_craft_resume_base_payload` run those **before** this call).
  - Derive leaf `artifact_type = artifact_key.rsplit(".", 1)[-1]` (pilot → `base_resume`).
  - `entity_type = entry["entity_type"]`; `entity_id = candidate_id` (pilot is candidate-scoped).
  - Call `database.save_artifact(entity_type, entity_id, artifact_type, blob)` and **return** the new uuid string.
  - Do **not** merge `base_resume` into `candidate_data` on this path (no denormalized blob mirror).
- **Library path** (`isinstance(data_or_artifact_key, dict)`): existing merge/`database.save_candidate` behavior unchanged; ignore `blob`; return `None`.
- Else: `ValueError` describing expected dict or artifact_key string.

3. Add `hydrate_operative_base_resume_for_response(candidate_id: str, cd: dict) -> None` next to `hydrate_rubric_artifacts_for_response`:
   - Read `row = database.get_current_artifact("candidate", candidate_id, "base_resume")`.
   - If row is None, return (leave any legacy blob as-is).
   - Ensure `cd["artifacts"]` is a dict; set `cd["artifacts"]["base_resume"] = row["artifact_data"]` (display overlay only — does not write the DB blob).

4. In `get_candidate(candidate_id)`: after `database.get_candidate`, if a row exists, run `hydrate_operative_base_resume_for_response(candidate_id, cd)` on its `candidate_data` (coerce to dict if needed) and return the hydrated row. This is what keeps `{$BASE_RESUME}` / `format_base_resume_for_token` correct without a denormalized write — do **not** change `format_base_resume_for_token` signature.

5. Retarget **parse** — in `parse_candidate_resume`, after `split_craft_resume_base_payload(parsed)`:
   - Library: `save_candidate_data(candidate_id, {"artifacts": {"resume_structure": structure}})` (dict path).
   - Operative: `save_candidate_data(candidate_id, TASK_CONFIG["craft_resume_base"]["artifact_key"], content)`.
   - Remove the `database.save_candidate(..., base_resume: content)` dual-write of the pilot body.

6. Retarget **UI generate land** — in `run_candidate_artifact_generation`, the `task_key == "craft_resume_base"` success block: same structure library + content operative pattern as step 5; remove blob write of `base_resume`.

7. Remove function `snapshot_saved_base_resume_artifact` entirely (call sites cleared in Stage 6).

8. In `_persist_craft_dispatch_success`, **delete** the entire `if task_key == "craft_resume_base":` branch. Leave `craft_company_search_terms` and rubric branches intact. Agent Stage 5 owns the operative land for `craft_resume_base`.

## Stage 5: Agent craft-persist rewire

**Done when:** Successful `do_task` with `persist_candidate_craft_hops` for `craft_resume_base` lands the pilot body only via `candidate.save_candidate_data(candidate_id, artifact_key, blob)` using `TASK_CONFIG[task_key]["artifact_key"]`; other craft tasks still use `_persist_craft_dispatch_success`.

1. In `src/core/agent.py`, locate the `persist_candidate_craft_hops` success block that currently lazy-imports `_persist_craft_dispatch_success` and always calls it.
2. Replace the inner persist logic with:

   - Read `task_cfg = TASK_CONFIG.get(task_key) or {}` (ensure `TASK_CONFIG` is imported in this module — add top-level or existing config import if missing).
   - `artifact_key = task_cfg.get("artifact_key")`.
   - **If** `artifact_key` is a non-empty string (pilot: `craft_resume_base`):
     - Lazy-import `split_craft_resume_base_payload` and `save_candidate_data` from `src.core.candidate`.
     - Require `parsed_for_persist` is a `dict`; else raise `ValueError` as today.
     - `structure, content = split_craft_resume_base_payload(parsed_for_persist)`.
     - `save_candidate_data(str(index), {"artifacts": {"resume_structure": structure}})` (library).
     - `save_candidate_data(str(index), artifact_key, content)` (operative).
   - **Else:** keep today’s call to `_persist_craft_dispatch_success(str(index), task_key, parsed_for_persist)`.
3. Keep existing error handling / hop-ledger failure / debug_index lines; update debug artifact label to prefer `artifact_key` when set.
4. Do **not** remove `persist_candidate_craft_hops` ctx flag. Do **not** rewire non-pilot crafts. Do **not** delete `_persist_craft_dispatch_success` (still required for search-terms + rubrics).

## Stage 6: API save + GET hydrate

**Done when:** PUT candidate data that includes pilot `artifacts.base_resume` persists via generic operative save (not blob+snapshot); GET detail overlays operative current; response remains `_sanitize_candidate` with no new `artifact_id` field.

1. In `src/ui/api/api_candidate.py` imports: add `hydrate_operative_base_resume_for_response`; add `TASK_CONFIG` (or the catalog key via `TASK_CONFIG["craft_resume_base"]["artifact_key"]`); remove `snapshot_saved_base_resume_artifact`.
2. In `get_candidate_detail`, keep using `get_candidate` (now hydrates in Stage 4). Still call `hydrate_operative_base_resume_for_response(candidate_id, cd)` after rubric hydrate if the handler mutates a local `cd` copy — idempotent overlay is fine.
3. In `update_candidate_data`, when `base_resume_in_save` is True after existing ingest/filter normalization:
   - Capture `pilot_body = arts["base_resume"]`.
   - `del arts["base_resume"]` (or pop) so the library merge does **not** write the pilot body into `candidate_data`.
   - After the existing `save_candidate_data(candidate_id, body, …)` library call (dict path) when `body` still has other fields — or before/after as needed so structure/other keys still merge — call:

```python
save_candidate_data(
    candidate_id,
    TASK_CONFIG["craft_resume_base"]["artifact_key"],
    pilot_body,
)
```

   - Remove the `snapshot_saved_base_resume_artifact(candidate_id)` call.
   - If `arts` is empty after popping pilot + other processing, keep existing `body.pop("artifacts", None)` behavior.
4. After successful PUT, before return, hydrate the refreshed candidate the same way as GET (`hydrate_operative_base_resume_for_response` on its `candidate_data`) so save→reload shows operative current. Return `jsonify(_sanitize_candidate(updated) if updated else {})` unchanged in shape — **do not** add or strip a special-case `artifact_id` field.

## Estimate

Confirm Chuckles estimate: 5 — agree

Agent craft-persist rewire + dual-dispatch save + API retarget + catalog delete is a multi-component known pattern (write-operative + manage-catalog), not a new architecture — 5 fits; not 3 because agent + candidate + API all move together.

## Review (build)

**Built @ `f66d8ac7`** — `origin/sub/AST-1569/AST-1576-generic-save-candidate-data`

Stages 1–6 landed: blind `save_artifact` docstring lock; `craft_resume_base.artifact_key`; `artifact_catalog` deleted; dual-dispatch `save_candidate_data` + hydrate in `get_candidate`; agent craft-persist rewire; API pilot operative save. Betty owns catalog test/bible retarget.

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1576
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1569/AST-1576-generic-save-candidate-data` @ `aa259b450ea3572e54cf080b4afa02965db6225f`

## Traceability
AC1→S1; AC2→S4+S5+S6; AC3→S2; AC4→S5 (+S4 step 8 removes `craft_resume_base` branch / `snapshot_saved_base_resume_artifact`); AC5→S3; AC6→S2 asserts + explicit OOS (no new keys / coat-check / grade pins / job finalize).

## Findings
(none — no fix-now; no discuss blockers)

**Considered (in-session):** Universal orch.* set + scoped product statutes matching plan layers `{data, utils, core, ui}` and paths under `src/**` — all `conforms` (config SoT via `ARTIFACT_CONFIG`/`TASK_CONFIG`; blind retire+insert matches existing `save_artifact`; layer imports respected; data raises / callers log; `artifact_catalog` delete aligns with parent manage-catalog mandate; explicit scope gate matches child `## Scope`; Betty owns test retarget).

context_tokens≈42000
```

## Radia review

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1576
**Publish ref:** `origin/sub/AST-1569/AST-1576-generic-save-candidate-data` @ `47ed93bdb6aaffec06d0fd325e7a65250582598a`
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | Tip is merge-tests(AST-1576) @ `81cab02f`; Betty test/bible deltas land at one SHA with product |
| orch.git.commit-vocabulary | universal | conforms | Branch ancestry uses standard `code` / `merge-tests` / `docs` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Work on `sub/AST-1569/AST-1576-*`; no reverse merges in diff |
| orch.git.ftr-sub-topology | universal | conforms | Child publish ref matches `sub/<parent>/<child-slug>` |
| orch.git.merge-on-checkout | universal | conforms | No checkout/merge mechanics in product diff |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force in diff |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named branches in diff |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1569 epic worktree; sub ref topology correct |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches introduced |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No unresolved product-policy forks |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–6 match landed product code |
| orch.pipeline.project-scoped-queues | universal | conforms | N/A to code content |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed per pipeline |
| orch.roles.archie-approves-statutes | universal | conforms | N/A to code content |
| orch.roles.betty-owns-test-tree | universal | conforms | Test/bible retarget via Betty merge-tests, not engineer `code()` |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to code content |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee at Tests Passed; expected handoff |
| orch.roles.pre-commit-path-bans | universal | conforms | No hook-bypass in diff |
| astral.agent.confidence-bounds | scoped | conforms | No confidence-bound changes in agent craft-persist path |
| astral.agent.do-task-delegation | scoped | conforms | `do_task` still delegates; craft persist branches on `artifact_key` only |
| astral.agent.grade-vector-validation | scoped | not-applicable | No grade-vector write paths touched |
| astral.batch.batch-id-first | scoped | not-applicable | No batch-claim/dispatch batch changes |
| astral.batch.batch-id-format | scoped | not-applicable | No batch id format changes |
| astral.batch.claim-process-release | scoped | not-applicable | No claim/process/release helpers changed |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | No entity-agent-response retention changes |
| astral.config.config-source-of-truth | scoped | conforms | `ARTIFACT_CONFIG` / `TASK_CONFIG["craft_resume_base"]["artifact_key"]` are SoT; `artifact_catalog` deleted |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No secrets/env surface in diff |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No repo-root artifact dir changes |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No debug spike files |
| astral.dispatch.seed-auto-false | scoped | not-applicable | No dispatch seed changes |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | No run_next chain edits |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single plan doc `docs/features/foundation/ast-1576-generic-save-candidate-data.md` |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Betty changes are tests/bible only on merge-tests SHA |
| astral.git.engineer-test-tree-ban | scoped | conforms | Product diff has no engineer-authored `tests/` commits; Betty merge-tests owns test tree |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | No `src/external/**` changes |
| astral.layers.import-direction | scoped | conforms | Agent lazy-import cycle break preserved; layers respected (core→data/config, ui→core) |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No `scripts/**` changes |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Pilot key from `TASK_CONFIG`, not hardcoded in UI handler |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | Coat-check paths out of scope and untouched |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No render-verdict/consult changes |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | `api_candidate` routes retain `@require_auth`; no new unauthenticated surfaces |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | No seed JSON changes |
| astral.seed.archie-catalog-wins | scoped | not-applicable | No seed catalog contention |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | No seed boot-path changes |
| astral.seed.define-approved | scoped | not-applicable | No define/seed work |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No operator-row seed edits |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage-join seed work |
| astral.standards.data-raises-caller-logs | scoped | conforms | `save_artifact` raises `ValueError`; operative path raises; API returns 400 on failure |
| astral.standards.database-header-inventory | scoped | conforms | `config.py` module docstring updated for `ARTIFACT_CONFIG` SoT |
| astral.standards.debug-contract-gated | scoped | conforms | Existing `debug_index` on craft persist/parse/generate unchanged; no new ungated `[DEBUG]` spam |
| astral.standards.dry-and-focused-functions | scoped | conforms | Dual-dispatch is plan-approved; helpers focused (`hydrate_operative_base_resume_for_response`) |
| astral.standards.in-scope-only | scoped | conforms | Product touches only scoped paths; AST-1577 React/editor OOS |
| astral.standards.logging-via-utils | scoped | conforms | No new raw `logging` / `print()` in touched runtime modules |
| astral.standards.names-not-ticket-ids | scoped | conforms | Symbols are domain-named, not ticket-prefixed |
| astral.standards.no-cross-contamination | scoped | conforms | Library merge vs operative write paths cleanly separated |
| astral.standards.no-hardcoded-sets | scoped | conforms | Pilot key from config asserts, not inline string sets |
| astral.standards.public-then-helpers | scoped | conforms | Public `save_candidate_data` / `get_candidate` hydrate before private craft helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | No new utils→data imports; catalog module deleted |
| astral.state.core-decides-transitions | scoped | conforms | No ad hoc state writes introduced |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job-state transition changes |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | No run-chain edits |
| astral.ui.frontend-file-placement | scoped | not-applicable | No `src/ui/frontend/**` changes |
| astral.ui.naming-conventions | scoped | not-applicable | No frontend naming surface |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No server worker config changes |

**Sweep count:** 65 active statutes scored in-session (18 universal + 47 scoped).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `patt.artifact.write-operative` (parent draft directive) | conforms | Blind retire+insert `save_artifact`; operative `save_candidate_data(key, blob)`; no blob mirror; hydrate on read |
| none cited in plan `Patterns to reuse` | — | Parent AST-1569 mandates write-operative; implementation matches draft `# Implementation` steps 1–6 |

## Plan adherence

Stages 1–6 land as specced: `save_artifact` docstring lock; `craft_resume_base.artifact_key` + asserts; `artifact_catalog` deleted with no `src/` imports remaining; dual-dispatch `save_candidate_data` with `resume_content` validation; `snapshot_saved_base_resume_artifact` removed; `_persist_craft_dispatch_success` no longer handles `craft_resume_base`; agent craft-persist branches on `TASK_CONFIG[task_key]["artifact_key"]`; API PUT pops pilot body from library merge and operative-saves; GET/PUT responses hydrate via `get_candidate` (+ idempotent API overlay). Explicit scope gate honored — no AST-1577 React/editor, no new catalog keys, no `artifact_id` API field. Estimate **5** still fits footprint. Cross-ticket boundary clean (AST-1573 catalog delete completes manage-catalog helper retirement; AST-1577 deferred).

## Findings

(none — no fix-now; no discuss blockers)

### advisory — operative `body_shape` validation is pilot-specific today

- **Location:** `src/core/candidate.py` `save_candidate_data` operative branch (~L779–785)
- **Finding:** Required-key validation runs only when `body_shape == "resume_content"`. Future `ARTIFACT_CONFIG` keys with other shapes would pass through to `save_artifact` without shape checks until extended.
- **Recommendation:** Acceptable for this ticket (pilot-only). When the next catalog key ships, generalize the required-key loop for all `BUILD_CONFIG["artifact_shapes"]` entries — not resolve-child scope here.

### advisory — redundant `pilot_body = None` reset

- **Location:** `src/ui/api/api_candidate.py` ~L291 inside the `arts` block
- **Finding:** `pilot_body` is initialized `None` at L255 then reset `None` again before the `base_resume_in_save` branch.
- **Recommendation:** Cosmetic only; optional cleanup in resolve-child or a later hygiene pass.

### advisory — `list_candidates` does not hydrate operative `base_resume`

- **Location:** `src/core/candidate.py` `list_candidates` vs `get_candidate`
- **Finding:** Only `get_candidate` overlays operative current. List API (`GET /api/candidates`) may show stale/missing `artifacts.base_resume` if legacy blob was cleared.
- **Recommendation:** Plan targets detail/token paths via `get_candidate`; confirm list UI does not depend on inline `base_resume` (likely AST-1577 territory). No block for this ticket.

## What's solid

- Write-operative contract is tight: blind retire+insert documented and unchanged in body; operative writes never library-merge pilot body.
- Config wiring is correct: `TASK_CONFIG["craft_resume_base"]["artifact_key"]` locked to sole `ARTIFACT_CONFIG` key with startup asserts.
- Agent rewire is minimal and guarded: `artifact_key` branch uses generic save; rubric/search-term crafts still use `_persist_craft_dispatch_success`.
- `{$BASE_RESUME}` safety: `_token_view_for_do_task` reloads via `get_candidate(cid)` when `astral_candidate_id` is present (normal craft/generate paths).
- Betty merge-tests coverage is strong: operative round-trip, retire prior, hydrate overlay, API library+operative split, agent craft-persist wiring.

## Frame diff

| Area | Paths | Verdict |
|------|-------|---------|
| Product (in-scope) | `src/data/database.py`, `src/utils/config.py`, `src/utils/artifact_catalog.py` (deleted), `src/core/candidate.py`, `src/core/agent.py`, `src/ui/api/api_candidate.py` | In-scope; plan-faithful |
| Plan doc | `docs/features/foundation/ast-1576-generic-save-candidate-data.md` | Present |
| Betty tests | `tests/component/core/test_candidate.py`, `test_agent.py`, `test_api_candidate.py`, `test_config.py`; deleted `test_artifact_catalog.py` | In-scope via merge-tests |
| Betty bible | `docs/test-bible/core/candidate.md`, `agent.md`, `ui/api/api_candidate.md`, `utils/config.md`, `utils/artifact_catalog.md` | In-scope via merge-tests |
| Sibling OOS | AST-1577 React/editor, `patt.artifacts.ui-consistency` | Not touched ✓ |

## Notes

- Joan plan-rubric APPROVED attached; no Excluded-statute straggler list — C4 clear.
- `grep` on `src/` shows zero remaining `artifact_catalog` / `snapshot_saved_base_resume_artifact` references.
- C7 complete: full artifact + frame diff present.

context_tokens≈38000
```
