# Register job.artifacts.job_resume and job.artifacts.cover_letter

**Linear:** [AST-1590](https://linear.app/astralcareermatch/issue/AST-1590/register-job-artifactsjob-resume-and-job-artifactscover-letter-support)
**Parent:** [AST-1588](https://linear.app/astralcareermatch/issue/AST-1588/support-job-artifactsjob-resume-and-job-artifactscover-letteras) — Support “job.artifacts.job_resume” and “job.artifacts.cover_letter” as artifacts
**Publish ref:** `sub/AST-1588/AST-1590-register-job-artifact-catalog-keys`

Owns catalog registration only: add both job keys to `ARTIFACT_CONFIG` beside the candidate pilot, bind body-replica (and editable-type) authority to those catalog keys so they cannot diverge, and assert JAR tab keys stay a 1:1 map to catalog leaves. No tracker public API, no schema, no consumer rewires.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/utils/config.py` — **modified** — register `job.artifacts.job_resume` and `job.artifacts.cover_letter` in `ARTIFACT_CONFIG`; retire or derive any parallel job-only editable-type authority so it cannot diverge; align JAR / body-replica config to cite catalog keys (or a 1:1 map to them).

Every row in **Files Changed** is that path. Stages only change config literals, docstring inventory, and startup asserts — no `src/core/**`, `src/data/**`, `src/ui/**`, or test-tree edits (Betty owns tests).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add both job keys to `ARTIFACT_CONFIG`; retarget body-replica values to catalog keys; derive `JOB_EDITABLE_ARTIFACT_TYPES` from those keys (leaf artifact_type strings); bind JAR resume/cover tabs to catalog via 1:1 leaf asserts; update module docstring + startup asserts | utils |

**Out of this ticket (do not touch):** artifacts table source refs (AST-1591); tracker generic write/read + base_resume citation (AST-1592); builder/UI consumer inventory (AST-1593); coat-check; sibling blob keys (`notes`, `resume_content`, `proposed_answers`, `application_responses`); `tests/` / `docs/test-bible/**`.

## Stage 1: Register job keys in `ARTIFACT_CONFIG`

**Done when:** Importing `src.utils.config` exposes `ARTIFACT_CONFIG` with exactly three keys — `candidate.artifacts.base_resume`, `job.artifacts.job_resume`, `job.artifacts.cover_letter` — each with complete metadata; startup asserts pass; sibling blob keys are absent from the catalog.

1. In `src/utils/config.py` module docstring **Config sections:** list, update the existing `ARTIFACT_CONFIG` line to name both job keys beside the pilot (keep the same SoT wording; cite AST-1590):

```
  ARTIFACT_CONFIG — versioned artifact registry keyed by entity._data path (entity, candidate_scoped, body_shape, ingestion_owner); keys = candidate.artifacts.base_resume, job.artifacts.job_resume, job.artifacts.cover_letter; SoT in config — callers import ARTIFACT_CONFIG (AST-1573 / AST-1575 / AST-1576 / AST-1590)
```

2. In the existing `ARTIFACT_CONFIG = { ... }` block (immediately after `BUILD_CONFIG`, currently pilot-only), **keep** the `candidate.artifacts.base_resume` entry unchanged and **add** these two entries (same metadata key set as the pilot):

```python
    "job.artifacts.job_resume": {
        "entity_type": "job",
        "candidate_scoped": True,
        # Same resume section contract as candidate base_resume / JAR use_resume_structure.
        "body_shape": "resume_content",
        # Tracker owns first-row ingestion for job editable bodies today (AST-1556).
        "ingestion_owner": "tracker",
    },
    "job.artifacts.cover_letter": {
        "entity_type": "job",
        "candidate_scoped": True,
        # Name into BUILD_CONFIG["artifact_shapes"]["cover_letter"] (JAR shapes_key).
        "body_shape": "cover_letter",
        "ingestion_owner": "tracker",
    },
```

⚠️ **Decision:** `body_shape` for `job_resume` is `resume_content` (existing `BUILD_CONFIG["artifact_shapes"]` key), not a new shape and not the leaf string `job_resume`. Matches candidate pilot + JAR `use_resume_structure` / `shapes_key: None` for the resume tab. Cover letter uses existing `cover_letter` shape. `candidate_scoped: True` and `ingestion_owner: "tracker"` are required by parent Technical scope.

3. Replace the pilot-only key-set assert and extend per-entry asserts. Keep the existing `_br` / `craft_resume_base` asserts. Immediately after them, add job-key asserts in this shape:

```python
assert set(ARTIFACT_CONFIG.keys()) == {
    "candidate.artifacts.base_resume",
    "job.artifacts.job_resume",
    "job.artifacts.cover_letter",
}
# Sibling job blob keys stay out of the catalog (parent AC / this ticket AC2).
for _sibling in (
    "notes",
    "resume_content",
    "proposed_answers",
    "application_responses",
    "job.artifacts.notes",
    "job.artifacts.resume_content",
    "job.artifacts.proposed_answers",
    "job.artifacts.application_responses",
):
    assert _sibling not in ARTIFACT_CONFIG

_jr = ARTIFACT_CONFIG["job.artifacts.job_resume"]
assert _jr["entity_type"] == "job"
assert _jr["entity_type"] in ENTITY_TYPES
assert _jr["candidate_scoped"] is True
assert isinstance(_jr["candidate_scoped"], bool)
assert _jr["body_shape"] == "resume_content"
assert _jr["body_shape"] in BUILD_CONFIG["artifact_shapes"]
assert _jr["ingestion_owner"] == "tracker"
assert set(_jr.keys()) == {
    "entity_type",
    "candidate_scoped",
    "body_shape",
    "ingestion_owner",
}

_cl = ARTIFACT_CONFIG["job.artifacts.cover_letter"]
assert _cl["entity_type"] == "job"
assert _cl["entity_type"] in ENTITY_TYPES
assert _cl["candidate_scoped"] is True
assert isinstance(_cl["candidate_scoped"], bool)
assert _cl["body_shape"] == "cover_letter"
assert _cl["body_shape"] in BUILD_CONFIG["artifact_shapes"]
assert _cl["ingestion_owner"] == "tracker"
assert set(_cl.keys()) == {
    "entity_type",
    "candidate_scoped",
    "body_shape",
    "ingestion_owner",
}
```

4. Do **not** add other catalog keys. Do **not** change `BUILD_CONFIG["artifact_shapes"]`, coat-check maps, or `JOB_BUILD_ARTIFACT_CLEAR_KEYS` (those remain job_data blob leaf names, not catalog authority).

## Stage 2: Derive editable / body-replica authority from catalog; bind JAR 1:1

**Done when:** `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` values are the two catalog keys; `JOB_EDITABLE_ARTIFACT_TYPES` is derived from those keys as leaf `artifact_type` strings (`job_resume`, `cover_letter`) so existing tracker table I/O keeps working; JAR resume/cover tabs keep leaf `artifact_key` strings but startup asserts prove each is the leaf of its catalog key (1:1 map); no independent hardcoded editable-type tuple remains as SoT.

1. In the AST-1548 body-replica block (near `JOB_ARTIFACT_BODY_REPLICA_BY_TASK`), change values to catalog keys:

```python
JOB_ARTIFACT_BODY_REPLICA_BY_TASK = {
    "finalize_job_resume": "job.artifacts.job_resume",
    "finalize_cover_letter": "job.artifacts.cover_letter",
}
```

Keep the existing disjointness assert vs `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK`.

⚠️ **Decision:** Body-replica **cites catalog keys** (parent Scope). Agent only uses the map for task membership + debug label today; persist still goes through type-specific tracker helpers until AST-1592. Putting hierarchical keys here does not change DB `artifact_type` leaves.

2. Replace the independent editable-type SoT with derivation from body-replica catalog values (leaf = last dotted segment — same rule candidate uses for `save_artifact`):

```python
# AST-1556 / AST-1590: editable job drafts SoT leaf types, derived from catalog keys in body-replica.
JOB_EDITABLE_ARTIFACT_TYPES = tuple(
    catalog_key.rsplit(".", 1)[-1]
    for catalog_key in JOB_ARTIFACT_BODY_REPLICA_BY_TASK.values()
)
JOB_ARTIFACT_ENTITY_TYPE = "job"
```

Delete the old hardcoded `assert JOB_EDITABLE_ARTIFACT_TYPES == ("job_resume", "cover_letter")` at that site — binding moves to post-`ARTIFACT_CONFIG` asserts in step 4.

3. Leave `JOBS_RECOMMENDED_ARTIFACT_TABS` `artifact_key` values for resume/cover as leaf strings (`job_resume`, `cover_letter`) and leave `proposed_answers` unchanged. Do **not** rewrite frontend contract in this ticket.

⚠️ **Decision:** JAR uses the parent-allowed **1:1 map** (leaf tab key ↔ catalog key leaf), not hierarchical tab keys yet. Hierarchical JAR keys would break ArtifactEditor / recommended-report blob lookup before AST-1593 rewires consumers; leaf + assert keeps mid-wave ftr usable while catalog remains authority.

4. Immediately **after** the Stage 1 `ARTIFACT_CONFIG` asserts (still in `config.py`), add binding asserts so body-replica / editable / JAR cannot drift from the catalog:

```python
# Body-replica values are catalog keys (not bare type strings as authority).
assert set(JOB_ARTIFACT_BODY_REPLICA_BY_TASK.values()) == {
    "job.artifacts.job_resume",
    "job.artifacts.cover_letter",
}
assert set(JOB_ARTIFACT_BODY_REPLICA_BY_TASK.values()) <= set(ARTIFACT_CONFIG)

# Editable leaf types are exactly the catalog job-key leaves (order = body-replica values).
assert JOB_EDITABLE_ARTIFACT_TYPES == ("job_resume", "cover_letter")
assert all(
    ARTIFACT_CONFIG[k]["entity_type"] == JOB_ARTIFACT_ENTITY_TYPE
    for k in JOB_ARTIFACT_BODY_REPLICA_BY_TASK.values()
)

# JAR resume/cover tabs: 1:1 leaf map to catalog keys; shapes_key matches body_shape when set.
_jar_by_id = {t["tab_id"]: t for t in JOBS_RECOMMENDED_ARTIFACT_TABS}
assert _jar_by_id["artifact_resume"]["artifact_key"] == "job_resume"
assert _jar_by_id["artifact_resume"]["artifact_key"] == (
    "job.artifacts.job_resume".rsplit(".", 1)[-1]
)
assert ARTIFACT_CONFIG["job.artifacts.job_resume"]["body_shape"] == "resume_content"
assert _jar_by_id["artifact_cover"]["artifact_key"] == "cover_letter"
assert _jar_by_id["artifact_cover"]["artifact_key"] == (
    "job.artifacts.cover_letter".rsplit(".", 1)[-1]
)
assert _jar_by_id["artifact_cover"]["shapes_key"] == (
    ARTIFACT_CONFIG["job.artifacts.cover_letter"]["body_shape"]
)
# proposed_answers remains a non-catalog pin/blob slot.
assert _jar_by_id["artifact_application"]["artifact_key"] == "proposed_answers"
assert "job.artifacts.proposed_answers" not in ARTIFACT_CONFIG
```

5. Do **not** edit `src/core/tracker.py`, `src/core/agent.py`, API, or frontend. Do **not** invent a second job-key registry module.

## Execution contract

- Stages 1 → 2 in order on the epic worktree; one `code()` commit per stage (or one combined product commit if build-child collapses — prefer one per stage).
- Do not add files outside **Files Changed**.
- Ambiguity or codebase drift → stop; comment on parent AST-1588 with the Stage blocked template from plan-child.
- Engineer must not create or edit `tests/` or `docs/test-bible/**` (Betty `qa-child`).

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1590
**Overall:** APPROVED
**Publish ref:** `sub/AST-1588/AST-1590-register-job-artifact-catalog-keys` @ `05bcd654020c7bf1a234e429b04592c63c81e1db`

### Traceability
- **AC1** → Stage 1 (`ARTIFACT_CONFIG` adds `job.artifacts.job_resume` + `job.artifacts.cover_letter` with full metadata; pilot unchanged; startup asserts).
- **AC2** → Stage 1 step 3 (sibling blob keys excluded from catalog via negative asserts); Stage 2 steps 1–4 bind body-replica / editable-leaf / JAR 1:1 map to those catalog keys without registering siblings.
- **Stages → definition:** Stage 1 → parent Functional scope §1 + child Scope (catalog registration only); Stage 2 → parent Technical scope (derive editable authority, JAR/body-replica cite catalog keys, no parallel SoT).

### Findings

#### acceptable
- **Location:** Plan structure — no `## Self-assessment` block.
- **Finding:** plan-child convention often includes conf/self-assessment; this plan omits it.
- **Recommendation:** Optional for a 2-point config-only ticket with explicit scope gate and staged asserts; not blocking.

No `fix-now` or `discuss` findings. In-session statute pass: universal set + scoped `astral.config.config-source-of-truth` and `astral.standards.no-hardcoded-sets` conform; utils-only footprint excludes data/UI/batch statutes by path/layer predicates.

context_tokens≈42000

## Review (build)

**Built @ `c097d2be`** — `origin/sub/AST-1588/AST-1590-register-job-artifact-catalog-keys`

Product stages 1–2 landed (`ARTIFACT_CONFIG` job keys + body-replica/editable/JAR catalog binding). Test path remains Betty `qa-child`.

## Radia review

# Radia review — AST-1590

**Publish ref:** `origin/sub/AST-1588/AST-1590-register-job-artifact-catalog-keys` @ `0f8b7a7a5b5364575501991b99c1c1dd6ee8ca52`

---

```
[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1590
**Publish ref:** `origin/sub/AST-1588/AST-1590-register-job-artifact-catalog-keys` @ `0f8b7a7a5b5364575501991b99c1c1dd6ee8ca52`
**Overall:** CLEAN
```

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no `src/core/**` diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no `src/core/**` diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | no `src/core/**` diff |
| astral.batch.batch-id-first | scoped | not-applicable | no batch/dispatcher paths in diff |
| astral.batch.batch-id-format | scoped | not-applicable | no batch paths in diff |
| astral.batch.claim-process-release | scoped | not-applicable | no batch paths in diff |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch paths in diff |
| astral.config.config-source-of-truth | scoped | conforms | catalog keys + bindings live in `config.py` blocks |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env surface in diff |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no `debug/` paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no dispatch paths |
| astral.docs.features-single-file-per-ticket | scoped | conforms | `ast-1590-*.md` is single file for this ticket |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Betty paths are tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | test/bible edits via Betty pipeline + one `merge-tests` SHA; engineer commits are `code()` only |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | no core/external diff |
| astral.layers.import-direction | scoped | conforms | `config.py` adds no layer violations |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` diff |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no `src/ui/**` diff |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API/auth paths |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed JSON paths |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed runtime paths |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no seed boot paths |
| astral.seed.define-approved | scoped | not-applicable | no seed define paths |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed operator paths |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no seed coverage paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no `src/data/**` diff |
| astral.standards.database-header-inventory | scoped | not-applicable | no `src/data/**` diff |
| astral.standards.debug-contract-gated | scoped | conforms | no new debug emission; agent skip label inherits catalog key from config |
| astral.standards.dry-and-focused-functions | scoped | conforms | focused config registration + derivation |
| astral.standards.in-scope-only | scoped | conforms | product footprint is `src/utils/config.py` only |
| astral.standards.logging-via-utils | scoped | conforms | no new logging in diff |
| astral.standards.names-not-ticket-ids | scoped | conforms | keys use domain names not ticket ids |
| astral.standards.no-cross-contamination | scoped | conforms | no unrelated module edits |
| astral.standards.no-hardcoded-sets | scoped | conforms | `JOB_EDITABLE_ARTIFACT_TYPES` derived from catalog keys; parallel SoT retired |
| astral.standards.public-then-helpers | scoped | conforms | public config constants before asserts |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no new utils→data import |
| astral.state.core-decides-transitions | scoped | not-applicable | no state machine paths |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job-state paths |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run-chain paths |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend diff |
| astral.ui.naming-conventions | scoped | not-applicable | no UI diff |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server config diff |
| orch.git.betty-merge-tests-one-sha | universal | conforms | exactly one `merge-tests(AST-1590)` on sub |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `docs` / `merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | sub publish ref topology |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1588/AST-1590-…` |
| orch.git.merge-on-checkout | universal | conforms | no merge violation in diff |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | linear child history |
| orch.git.no-dev-agent-branches | universal | conforms | no agent-named publish ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1588 epic worktree |
| orch.git.three-permanent-branches | universal | conforms | sub off ftr/dev pattern |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | plan decisions documented inline |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–2 match plan |
| orch.pipeline.project-scoped-queues | universal | conforms | n/a to diff content |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed gate satisfied |
| orch.roles.archie-approves-statutes | universal | conforms | n/a |
| orch.roles.betty-owns-test-tree | universal | conforms | manifest + `TestAst1590*` + merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | n/a |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee through review |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path violation evident |

**Active-set count:** 65 rows (per `canon/statutes/README.md` harvested + universal registry).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan has no "Patterns to reuse" block; code comments reference draft `patt.artifact.manage-catalog` (register half) — informational only |

## Plan adherence

- **AC1 (catalog registration):** `ARTIFACT_CONFIG` adds `job.artifacts.job_resume` and `job.artifacts.cover_letter` with full metadata; pilot unchanged; key-set and per-entry asserts pass.
- **AC2 (sibling exclusion):** negative sibling loop + `proposed_answers` JAR assert keep blob keys out of catalog.
- **Stage 2 (authority binding):** `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` values are catalog keys; `JOB_EDITABLE_ARTIFACT_TYPES` derived as leaf strings via `rsplit` (tracker table I/O unchanged); JAR tabs remain leaf keys with 1:1 binding asserts.
- **Scope gate:** no `src/core/**`, `src/data/**`, `src/ui/**` product edits. Agent debug label change is config-propagated (`replica_slot` in `agent.py` already logs the map value) — no agent product commit required.
- **Estimate (2):** footprint matches — single-module config registration + asserts.
- **Joan:** APPROVED @ `05bcd654`; no Excluded statute list → no straggler callout.
- **Tests:** Betty manifest (`TestAst1590JobArtifactCatalogKeys`, revised AST-1099/1576 asserts, agent debug string) aligns with plan; one `merge-tests` SHA.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

1. **Branch hygiene — unrelated docs on publish ref:** diff also adds `docs/features/tracker/ast-1591-artifacts-table-source-references.md` and AST-1587 bible shasum lines in `docs/test-bible/core/builder.md` / `candidate.md`. No product scope smuggle for AST-1590, but ftr rollup will carry sibling-doc noise — Chuckles may want those on their own sub tips before merge-child.
2. **Draft pattern comment:** `ARTIFACT_CONFIG` header cites `patt.artifact.manage-catalog` under `canon/directives/draft/` — fine as narrative; not an approved `canon/patterns/**` citation and correctly not listed as a pattern conformance row.

## What's solid

- Catalog registration matches parent technical scope: hierarchical keys, `candidate_scoped: True`, `ingestion_owner: "tracker"`, correct `body_shape` bindings.
- Deriving `JOB_EDITABLE_ARTIFACT_TYPES` from catalog-key leaves prevents the footgun of body-replica values becoming table `artifact_type` strings after the map retarget.
- Startup assert suite gives strong anti-drift guarantees between catalog, body-replica, editable leaves, and JAR tabs without touching runtime consumers (deferred to AST-1592/1593 per plan).
- Component tests mirror the assert surface area; revised agent debug assertion correctly expects `key=job.artifacts.cover_letter`.

## Frame diff

- `ARTIFACT_CONFIG`: `candidate.artifacts.base_resume` (unchanged) + **`job.artifacts.job_resume`** + **`job.artifacts.cover_letter`**
- `JOB_ARTIFACT_BODY_REPLICA_BY_TASK`: `job_resume` / `cover_letter` leaf values → **`job.artifacts.job_resume`** / **`job.artifacts.cover_letter`**
- `JOB_EDITABLE_ARTIFACT_TYPES`: was `tuple(map.values())` (would break after retarget) → **`tuple(catalog_key.rsplit(".", 1)[-1] for …)`** preserving `("job_resume", "cover_letter")` for tracker I/O
- New startup asserts: sibling exclusion, job metadata, body-replica ⊆ catalog, JAR 1:1 leaf map
- Agent debug skip lines: `key=cover_letter` → **`key=job.artifacts.cover_letter`** (via config, no `agent.py` edit)

## Notes

- Joan plan-rubric verdict attached; no Excluded-statute table → straggler check N/A.
- C7 complete — recommend **Review Posted** → **resolve-child** (PROCEED) or straight **User Testing** per datt routing.

context_tokens≈58000

