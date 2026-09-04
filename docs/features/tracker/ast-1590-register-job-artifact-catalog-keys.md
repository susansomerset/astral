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
