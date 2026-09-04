# Artifacts table source references

**Linear:** [AST-1591](https://linear.app/astralcareermatch/issue/AST-1591/artifacts-table-source-references-support-jobartifactsjob-resume-and)
**Parent:** [AST-1588](https://linear.app/astralcareermatch/issue/AST-1588/support-jobartifactsjob-resume-and-jobartifactscover-letteras) — Support `job.artifacts.job_resume` and `job.artifacts.cover_letter` as artifacts
**Publish ref:** `sub/AST-1588/AST-1591-artifacts-table-source-references`

Data-layer support so each `artifacts` version can store an optional list of source `artifact_uuid` strings (seed bodies that informed that write). DDL/ensure migrates existing DBs; `save_artifact` persists the list; `get_current_artifact` / `get_artifact` return it. Does **not** register catalog keys (AST-1590) or wire tracker `job_resume` → `base_resume` citation (AST-1592).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/data/database.py` — extend `artifacts` DDL/ensure for source-reference storage; `save_artifact` / get-current / get-by-uuid accept and return source artifact ids; header inventory updated; no unrelated schema churn
- `canon/directives/draft/patt.artifacts.traceability.md` — one-line alignment note only; do not promote draft to approved canon

Every row in **Files Changed** is one of those paths (plus this plan doc). Every Stage step is the kind of change Scope describes for that file.

**Out of this ticket (do not touch):** `src/utils/config.py` / `ARTIFACT_CONFIG`; `src/core/tracker.py` / `src/core/candidate.py` / `src/core/agent.py` / `src/core/builder.py`; `src/ui/api/api_jobs.py`; frontend; coat-check; UUID-existence or catalog validation on source ids; agent/task lineage columns beyond source artifact ids; promoting the draft pattern out of `canon/directives/draft/`. Engineer must not create or edit `tests/` or `docs/test-bible/**`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `source_artifact_ids` column (DDL + ensure migrate); extend `save_artifact` optional param; return field from get-current / get-by-uuid (and shared row mapper used by `list_artifacts`); update header inventory | data |
| `canon/directives/draft/patt.artifacts.traceability.md` | One-line note that AST-1588 lands source-artifact-id storage on `artifacts` for the job_resume→base_resume case | canon draft |

## Stage 1: Schema + header inventory

**Done when:** Fresh and existing DBs have an `artifacts.source_artifact_ids` TEXT column (JSON array of strings, default `[]`); module header inventory documents it; no other tables changed.

⚠️ **Decision:** Column name is `source_artifact_ids` (snake_case TEXT storing a JSON array of `artifact_uuid` strings). Matches parent wording (“list of source artifact ids”) and keeps storage on the `artifacts` row rather than a sidecar table (draft pattern left that choice to the implement ticket; parent AC is table storage on each version).

1. In `src/data/database.py` module header inventory, update the `artifacts` bullet so it lists `source_artifact_ids` TEXT (JSON array of artifact_uuid strings; default `[]`) beside the existing columns. Keep the current=1 / retire-and-insert note; cite AST-1591 for the new column.

2. In `_ensure_artifacts_table`, after the table exists under the name `artifacts` (both the “already `artifacts`” path and the `astral_artifacts` rename path) and before setting `_artifacts_schema_ensured = True`, ensure the column:

```python
cols = _column_names("artifacts")
if "source_artifact_ids" not in cols:
    conn.execute(
        "ALTER TABLE artifacts ADD COLUMN source_artifact_ids TEXT NOT NULL DEFAULT '[]'"
    )
```

Call `conn.commit()` after the ALTER (same pattern as `vector_feedback` batch_size/completed_at ensure). Re-fetch or reuse `cols` as needed so rename-of-uuid and add-column both run when required.

3. In the fresh `CREATE TABLE artifacts (...)` branch, add the column to the CREATE:

```sql
source_artifact_ids TEXT NOT NULL DEFAULT '[]'
```

Place it after `artifact_data` and before `current` (semantic grouping: body then provenance, then versioning timestamps).

4. Do **not** change indexes. Do **not** touch other tables. Do **not** reset `_artifacts_schema_ensured` outside this function’s normal flow.

## Stage 2: Persist + return source ids on save / get-current / get-by-uuid

**Done when:** `save_artifact(..., source_artifact_ids=None)` persists a JSON array on the new current row; callers that omit the arg still work and store `[]`; `get_current_artifact` and `get_artifact` return `source_artifact_ids` as a Python `list` of strings (legacy/missing → `[]`). No UUID-existence checks.

⚠️ **Decision:** No validation that source ids exist in `artifacts` or match any catalog key (parent: incremental add; validation would false-positive until the catalog is mature). Only normalize shape: `None` → `[]`; otherwise require a list/tuple of values that stringify+strip to non-empty strings (drop empties after strip so callers can pass sparse lists safely). Raise `ValueError` only for a non-list/non-tuple non-None argument — not for unknown uuids.

1. Extend `_ARTIFACT_SELECT` to include `source_artifact_ids` immediately after `artifact_data`:

```python
_ARTIFACT_SELECT = (
    "artifact_uuid, entity_type, entity_id, artifact_type, "
    "artifact_data, source_artifact_ids, current, created_at, updated_at"
)
```

2. Update `_artifact_row_dict(row)` for the new SELECT order:

- Keep parsing `artifact_data` from `row[4]`.
- Parse `source_artifact_ids` from `row[5]`: if the raw value is `None`/empty → `[]`; if already a list use it; if a string, `json.loads` and require a list (on decode failure → `[]`). Coerce each element to `str`.
- Shift `current` / `created_at` / `updated_at` to `row[6]` / `row[7]` / `row[8]`.
- Include `"source_artifact_ids": <list>` in the returned dict.

`list_artifacts` shares this SELECT/mapper — it will surface the field automatically; do not add a separate list API this ticket.

3. Change `save_artifact` signature to:

```python
def save_artifact(
    entity_type: str,
    entity_id: str,
    artifact_type: str,
    artifact_data: Any,
    source_artifact_ids: Optional[Sequence[str]] = None,
) -> str:
```

Import `Sequence` from `typing` if not already present (keep existing typing style in the file).

4. Inside `save_artifact`, after validating `artifact_data`, normalize sources:

```python
if source_artifact_ids is None:
    sources: list[str] = []
elif isinstance(source_artifact_ids, (list, tuple)):
    sources = [str(x).strip() for x in source_artifact_ids if str(x).strip()]
else:
    raise ValueError("source_artifact_ids must be a list of strings or None")
sources_payload = json.dumps(sources)
```

5. Extend the INSERT to include `source_artifact_ids`:

```sql
INSERT INTO artifacts (
    artifact_uuid, entity_type, entity_id, artifact_type,
    artifact_data, source_artifact_ids, current, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
```

Bind `sources_payload` in the matching position. Keep blind retire-by-key + insert (no prior-id SELECT; no in-place body UPDATE). Docstring: note optional `source_artifact_ids` (JSON array on the new row; default empty; no existence validation — AST-1591 / patt.artifacts.traceability table support).

6. Do **not** change `retire_current_artifact`. Do **not** add logging in the data layer. Do **not** change core/UI callers this ticket — existing positional `save_artifact(et, eid, at, data)` calls remain valid and store `[]`.

## Stage 3: Draft pattern alignment note

**Done when:** `canon/directives/draft/patt.artifacts.traceability.md` has a single new alignment sentence tying AST-1588 table storage to the job_resume→base_resume case; file stays under `draft/`; no other canon files edited.

1. In `canon/directives/draft/patt.artifacts.traceability.md`, under **Exceptions** or **Implementation** (prefer a new bullet under **Implementation** after the existing “Draft” bullet), add exactly one alignment line, e.g.:

   - **AST-1588** — Lands `source_artifact_ids` persistence on the `artifacts` table (data layer) so job_resume versions can cite base_resume; agent/task lineage and full token-catalog harvest remain out of that epic.

2. Do **not** move the file out of `draft/`. Do **not** rewrite the Abstract/Arc. Do **not** mark the pattern approved.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

```text
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1591
**Overall:** APPROVED
**Publish ref:** `sub/AST-1588/AST-1591-artifacts-table-source-references` @ `364201c79981d6cc7d28a4918480168e5cb762f4`

## Traceability
AC3 → Stage 1 (DDL/ensure `source_artifact_ids` + header inventory) + Stage 2 (`save_artifact` persist, `get_current_artifact` / `get_artifact` / `list_artifacts` return); Stage 3 → draft traceability alignment note (in-scope canon only).

## Findings

### acceptable
- **Location:** Plan structure
- **Finding:** No Conf/Risk self-assessment block (Estimate only).
- **Recommendation:** Optional; ticket is a tight data-layer slice — not blocking.

### acceptable
- **Location:** Stage 1 / `_ensure_artifacts_table`
- **Finding:** Column ensure is specified in both early-return branches rather than a single post-rename block (vector_feedback-style consolidation).
- **Recommendation:** Either shape is fine; engineer should not skip either existing-table path.

**Considered (in-session, slim R7):** Universal orch.* statutes — conform (plan review gate). Scoped data-layer statutes (`database-header-inventory`, `data-raises-caller-logs`, `in-scope-only`, `no-cross-contamination`, `import-direction`, `names-not-ticket-ids`, `dry-and-focused-functions`, `public-then-helpers`) — conform. Draft patterns `patt.artifact.write-operative` / `patt.artifacts.traceability` — conform to parent’s draft citations; optional kwarg on `save_artifact` matches write-operative retire+insert; no existence validation matches parent incremental-add intent.

context_tokens≈42000
```

**Summary:** Plan Ready, first pass (no Plan Discuss rounds). Scope gate, files-changed table, and stages align with AST-1591’s slice and parent AC3. Schema migration correctly targets both existing-table paths in `_ensure_artifacts_table` (current code returns early without column ensure). Layer, header-inventory, data-raises/no-logging, and boundary discipline all hold. No fix-now findings — recommend **Plan Approved**.

## Build complete

**Publish ref:** `sub/AST-1588/AST-1591-artifacts-table-source-references` @ `c4684fafc364363466f772687fca726b6a4459aa`

Stages 1–3 delivered: `artifacts.source_artifact_ids` DDL/ensure + header inventory; `save_artifact` optional persist; get-current / get-by-uuid (via shared mapper) return list; draft traceability one-line note.

## Radia review

# Radia review — AST-1591

`[code-rubric] revision=2`
**Rubric:** code-rubric.v2
**Ticket:** AST-1591
**Publish ref:** `sub/AST-1588/AST-1591-artifacts-table-source-references` @ `8701bb5406da155e38a49a24b1e3181426b3812e`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-1591)` on publish ref. |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `docs` / `merge-tests` vocabulary respected. |
| orch.git.flow-direction-inviolable | universal | conforms | Child `sub/AST-1588/…` only; no dev-agent writes. |
| orch.git.ftr-sub-topology | universal | conforms | Correct `sub/<parent>/<child>` topology. |
| orch.git.merge-on-checkout | universal | conforms | No merge-on-checkout violations in diff. |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | Linear history; no rebase/force in diff. |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named publish branches. |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree pattern; no violation in diff. |
| orch.git.three-permanent-branches | universal | conforms | Publish ref is `sub/*`, not a fourth permanent branch. |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No unresolved product forks in implementation. |
| orch.pipeline.plan-is-bible | universal | conforms | `database.py` + draft note match Stages 1–3. |
| orch.pipeline.project-scoped-queues | universal | conforms | N/A to code diff. |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed as expected. |
| orch.roles.archie-approves-statutes | universal | conforms | N/A to this diff. |
| orch.roles.betty-owns-test-tree | universal | conforms | Test/bible edits via Betty `qa-child` + `merge-tests`. |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to diff. |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine assignee through Tests Passed. |
| orch.roles.pre-commit-path-bans | universal | conforms | No hook-ban path violations observed. |
| astral.agent.confidence-bounds | scoped | not-applicable | No `src/core/**` diff paths. |
| astral.agent.do-task-delegation | scoped | not-applicable | No agent layer changes. |
| astral.agent.grade-vector-validation | scoped | not-applicable | No grade-vector paths touched. |
| astral.batch.batch-id-first | scoped | not-applicable | No batch/dispatcher changes. |
| astral.batch.batch-id-format | scoped | not-applicable | No batch id paths. |
| astral.batch.claim-process-release | scoped | not-applicable | No claim/clear helpers changed. |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | No agent_response paths. |
| astral.config.config-source-of-truth | scoped | not-applicable | No `src/utils/config.py` in diff. |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No env/secret surface changes. |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No debug artifact paths. |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spike paths. |
| astral.dispatch.seed-auto-false | scoped | not-applicable | No dispatch changes. |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | No run_next changes. |
| astral.docs.features-single-file-per-ticket | scoped | conforms | `ast-1591-*.md` is one file for this ticket. |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty paths are tests/bible only. |
| astral.git.engineer-test-tree-ban | scoped | conforms | Test-tree edits attributed to Betty pipeline (`merge-tests`). |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | No core/external diff. |
| astral.layers.import-direction | scoped | conforms | `Sequence` added at module top in `database.py`; no layer bends. |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No scripts diff. |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | No UI diff. |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | No coat-check paths. |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No consult/render paths. |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | No API auth paths. |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | No seed JSON changes. |
| astral.seed.archie-catalog-wins | scoped | not-applicable | No catalog seed paths. |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | No boot/seed hot-path changes. |
| astral.seed.define-approved | scoped | not-applicable | No define/seed ticket paths. |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No operator-row paths. |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage-join paths. |
| astral.standards.data-raises-caller-logs | scoped | conforms | `ValueError` on bad type; no new data-layer logging. |
| astral.standards.database-header-inventory | scoped | conforms | Header inventory updated with `source_artifact_ids`. |
| astral.standards.debug-contract-gated | scoped | not-applicable | No debug emission added. |
| astral.standards.dry-and-focused-functions | scoped | conforms | `_ensure_source_artifact_ids_column()` consolidates ALTER logic. |
| astral.standards.in-scope-only | scoped | conforms | `database.py` + draft traceability only in product; see discuss on branch diff footprint. |
| astral.standards.logging-via-utils | scoped | not-applicable | No logging added. |
| astral.standards.names-not-ticket-ids | scoped | conforms | AST-1591 cites are traceability comments, not runtime identifiers. |
| astral.standards.no-cross-contamination | scoped | conforms | Data-layer change stays in `src/data`; no out-of-layer imports. |
| astral.standards.no-hardcoded-sets | scoped | not-applicable | No new inline enum sets outside config. |
| astral.standards.public-then-helpers | scoped | conforms | Public `save_artifact` extended; helper `_artifact_row_dict` updated in place. |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No utils layer changes. |
| astral.state.core-decides-transitions | scoped | not-applicable | No state machine changes. |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job-state paths. |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | No run-chain paths. |
| astral.ui.frontend-file-placement | scoped | not-applicable | No frontend diff. |
| astral.ui.naming-conventions | scoped | not-applicable | No UI diff. |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No server config diff. |

**Active set:** 65 statutes scored (18 universal + 47 scoped).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan has no "Patterns to reuse" block; draft `patt.artifacts.traceability` alignment is in-scope prose only (not approved catalog). |

## Plan adherence

**AST-1591 product slice matches plan Stages 1–3.**

- **Stage 1:** `source_artifact_ids` in fresh `CREATE TABLE`, header inventory updated, `_ensure_source_artifact_ids_column()` called on both existing-table early-return paths (`artifacts` and post-`astral_artifacts` rename).
- **Stage 2:** `_ARTIFACT_SELECT` extended; `_artifact_row_dict` shifts indices and returns `list[str]`; `save_artifact(..., source_artifact_ids=None)` normalizes/strips/persists; INSERT column/`?` bind tuple is consistent (6 binds + literal `current=1` + 2 timestamps); no logging; no caller rewires; no UUID-existence validation (per plan decision).
- **Stage 3:** Draft `patt.artifacts.traceability.md` gains AST-1588 alignment bullet; file stays under `draft/`.

**Estimate 3** fits the actual footprint (single data module + draft note + Betty tests).

**Betty manifest** (`test_artifacts.py` full file) aligns with bible `docs/test-bible/data/database/artifacts.md` § AST-1591.

## Findings

### discuss

**Cross-ticket diff footprint — sibling AST-1590 tests without AST-1590 product on this ref**

- **Location:** `origin/sub/AST-1588/AST-1591-artifacts-table-source-references` three-dot diff vs `origin/dev`; commits `bb427f0c` onward.
- **What:** Diff includes AST-1590 test-tree + bible deltas (`tests/component/utils/test_config.py`, `tests/component/core/test_agent.py`, `docs/test-bible/utils/config.md` § AST-1590) merged from shared `origin/tests`, but **`src/utils/config.py` on this tip is still dev** (leaf body-replica values, pilot-only `ARTIFACT_CONFIG`).
- **Why it matters:** `TestAst1590JobArtifactCatalogKeys` and revised body-replica/agent asserts **will fail** on this ref if the config component suite runs. AST-1591 manifest (`test_artifacts.py` only) can be green while sibling tests are red.
- **Recommendation:** Not a product defect in `database.py`. Resolve at **merge-child** / `blockedBy` order: land AST-1590 product on `ftr` before (or together with) this test footprint, or keep sibling test commits off the AST-1591 publish ref until AST-1590 product is an ancestor. Chuckles should confirm rollup order before UT.

### advisory

- **AST-1587 bible shasum lines** in `docs/test-bible/core/builder.md` and `candidate.md` are unrelated sibling churn on the branch — harmless, not AST-1591 scope.
- **Draft traceability edit** renumbered Implementation bullets (not literally "one line") — acceptable for draft canon; content matches Stage 3 intent.

## What's solid

- Clean data-layer slice: schema ensure on both migration paths, backward-compatible optional kwarg, shared mapper surfaces field through `get_current_artifact` / `get_artifact` / `list_artifacts`.
- Retire-and-insert write-operative shape preserved; no existence validation matches parent incremental-add intent.
- Component tests cover ALTER-on-legacy-table, omit→`[]`, persist/strip, per-version independence, and bad-type `ValueError`.

## Frame diff

**In-scope (AST-1591):** `src/data/database.py` `source_artifact_ids` column + persist/read; `canon/directives/draft/patt.artifacts.traceability.md` alignment; `docs/test-bible/data/database/artifacts.md` + `tests/component/data/database/test_artifacts.py`.

**Cross-frame (sibling, not AST-1591 product):** AST-1590 test/bible deltas on same publish ref without AST-1590 `config.py` product — discuss above.

## Notes

- Joan plan-rubric APPROVED attached; no Excluded-statute straggler list.
- No `src/core/**`, `src/utils/**`, UI, or tracker rewires — boundaries hold for this ticket's product work.
- `8701bb54` is tip under review.

context_tokens≈58000

---

```
[code-rubric] REVIEW (Commit: 8701bb54) Sibling tests need merge order
```

## Resolution

**Date:** 2026-09-04  
**Publish ref:** `sub/AST-1588/AST-1591-artifacts-table-source-references`

Radia `[code-rubric]` REVIEW @ `8701bb54` / docs tip `bc6aac7c`:

- **fix-now:** none.
- **discuss (sibling AST-1590 tests without AST-1590 product on this ref):** Not a product defect in `database.py`. No code change this resolve. Rollup / `blockedBy` order is Chuckles **merge-child** / prep-uat: land AST-1590 product on `ftr` before (or together with) the shared `origin/tests` AST-1590 footprint so config suite asserts are not red on a lone AST-1591 tip. AST-1591 Betty manifest (`test_artifacts.py`) remains the green gate for this child.
- **advisory:** AST-1587 bible shasum churn and draft Implementation renumber — accepted as-is; out of scope / already matching Stage 3 intent.
