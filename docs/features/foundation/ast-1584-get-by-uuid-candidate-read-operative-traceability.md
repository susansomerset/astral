# get-by-uuid + candidate read-operative + traceability draft

**Linear:** [AST-1584](https://linear.app/astralcareermatch/issue/AST-1584/get-by-uuid-candidate-read-operative-traceability-draft-implement)
**Parent:** [AST-1571](https://linear.app/astralcareermatch/issue/AST-1571/implement-pattartifactread-operative) — Implement patt.artifact.read-operative
**Publish ref:** `sub/AST-1571/AST-1584-get-by-uuid-candidate-read-operative-traceability`

Ship the data + candidate half of `patt.artifact.read-operative` for the pilot catalog key `candidate.artifacts.base_resume`: by-`artifact_uuid` fetch in `database.py`, a public pin→body helper on `candidate.py`, and a **docs-only** draft of `patt.artifacts.traceability`. Does **not** wire JAR UI, Contact Estelle call sites, grade/analysis pin writers, or any product persist of seed artifact ids (sibling AST-1585 + later implement tickets).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/data/database.py` — by-`artifact_uuid` fetch; deserialize `artifact_data`; empty on miss
- `src/core/candidate.py` — pilot pin→body helper for `candidate.artifacts.base_resume`
- `canon/directives/draft/patt.artifacts.traceability.md` — **new** draft only

Every row in **Files Changed** is one of those three paths. Technical kinds match: new PK SELECT helper on the existing `artifacts` table; new public core helper that calls that fetch and returns body or empty; new draft directive file. No new catalog keys, no UI/API/Contact rewires, no schema migration.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `get_artifact(artifact_uuid)` — SELECT by PK, deserialize via `_artifact_row_dict`, return row dict or `None`; no coat-check / blob | data |
| `src/core/candidate.py` | Add public `get_operative_base_resume(artifact_uuid)` pin→body for pilot key; update module In-scope line | core |
| `canon/directives/draft/patt.artifacts.traceability.md` | **New** draft pattern: versioned agent_id / agent_task_id, seed `artifact_id[]`, manual-edit inheritance; implement-later flagged | canon |

**Out of this ticket (do not touch):** `src/core/contact.py`; `src/ui/api/**`; `JobAnalysisReportModal.tsx` (sibling AST-1585); `ARTIFACT_CONFIG` new keys; `get_current_artifact` / read-current editor hydrate; coat-check maps; grade/analysis pin writers; ordinary-save HTTP `artifact_id` field; product persist of seed artifact ids; `canon/directives/draft/patt.artifact.read-operative.md` (cite only — do not rewrite). Engineer must not create or edit `tests/` or `docs/test-bible/**`.

## Stage 1: Data-layer by-uuid fetch

**Done when:** `database.get_artifact(artifact_uuid)` returns the same public row shape as `get_current_artifact` (via `_artifact_row_dict`) when the PK exists, and `None` when it does not; blank uuid raises `ValueError`; the function never reads `*_data` blobs, never coat-checks, and never logs.

1. In `src/data/database.py`, immediately **after** `get_current_artifact` and **before** `list_artifacts`, add:

```python
def get_artifact(artifact_uuid: str) -> Optional[Dict[str, Any]]:
    """Return one artifacts row by primary key, or None (patt.artifact.read-operative).

    Deserializes artifact_data via _artifact_row_dict. No coat-check; no blob fallback.
    """
    uid = (artifact_uuid or "").strip()
    if not uid:
        raise ValueError("artifact_uuid required")

    def _with_conn() -> Optional[Dict[str, Any]]:
        conn = _get_connection()
        try:
            _ensure_artifacts_table(conn)
            row = conn.execute(
                f"""SELECT {_ARTIFACT_SELECT}
                      FROM artifacts
                     WHERE artifact_uuid = ?
                     LIMIT 1""",
                (uid,),
            ).fetchone()
            return _artifact_row_dict(row) if row else None
        finally:
            conn.close()

    return _run_with_retry(_with_conn)
```

2. Do **not** change the `artifacts` table schema, header inventory line (table already listed), `save_artifact`, `get_current_artifact`, `retire_current_artifact`, or `list_artifacts` signatures/behavior.
3. Do **not** add logging inside this function (data raises / returns; callers log — `astral.standards.data-raises-caller-logs`).

⚠️ **Decision:** Name the PK fetch `get_artifact` (parallel to `get_agent_data` by PK) rather than `get_artifact_by_uuid`. Scoped current read stays `get_current_artifact`; pin read is the unqualified PK getter. Return the **full row dict** (not body alone) so core can enforce pilot `entity_type` / `artifact_type` before exposing body.

## Stage 2: Candidate pin→body helper

**Done when:** `from src.core.candidate import get_operative_base_resume` works; a known pin for a `candidate` / `base_resume` row returns that row’s `artifact_data`; miss / wrong type / wrong entity returns `None`; the helper never walks `candidate_data.artifacts.base_resume` and never calls coat-check.

1. In `src/core/candidate.py` module docstring **In-scope:** line, append after the AST-1576 hydrate clause:

```
get_operative_base_resume(artifact_uuid) pin→body for pilot
candidate.artifacts.base_resume (AST-1584 / patt.artifact.read-operative).
```

2. Immediately **before** `hydrate_operative_base_resume_for_response`, add this public function (public-then-helpers: place with other public artifact helpers, not buried under private `_` helpers):

```python
def get_operative_base_resume(artifact_uuid: str) -> Optional[Any]:
    """Pin→body for pilot candidate.artifacts.base_resume (patt.artifact.read-operative).

    Returns deserialized artifact_data, or None on miss / non-pilot row.
    No coat-check; no candidate_data blob fallback.
    """
    row = database.get_artifact(artifact_uuid)
    if row is None:
        return None
    pilot_key = "candidate.artifacts.base_resume"
    entry = ARTIFACT_CONFIG[pilot_key]
    artifact_type = pilot_key.rsplit(".", 1)[-1]
    if row.get("entity_type") != entry["entity_type"]:
        return None
    if row.get("artifact_type") != artifact_type:
        return None
    return row.get("artifact_data")
```

3. Do **not** change `hydrate_operative_base_resume_for_response` (that remains read-current via `get_current_artifact`). Do **not** add Contact/API call sites here — AST-1585 owns those.
4. Do **not** add a scoped-without-pin overload on this helper (parent + ticket notes: pin-only; scoped-without-pin is read-current / AST-1570).

⚠️ **Decision:** Wrong-entity or wrong-`artifact_type` pins return `None` (same as miss), not the foreign body and not `ValueError`. Sibling consumers treat empty as “gap — no blob fallback.” Pilot identity is resolved from `ARTIFACT_CONFIG["candidate.artifacts.base_resume"]` + key suffix so config remains SoT (`astral.config.config-source-of-truth`); do not invent a second catalog.

## Stage 3: Draft `patt.artifacts.traceability`

**Done when:** `canon/directives/draft/patt.artifacts.traceability.md` exists in the same frontmatter/body shape as sibling drafts under `canon/directives/draft/patt.artifact.*.md`; it covers versioned `agent_id`, versioned `agent_task_id`, seed artifact id array, and manual-edit inheritance; it explicitly flags implement-later / no product wire in this epic.

1. Create `canon/directives/draft/patt.artifacts.traceability.md` with this exact structure (match sibling draft style — `id` / `kind` / `scope` / `point` frontmatter + Abstract / Arc / Applications / Exceptions / Implementation / OPEN QUESTIONS — **not** the `canon/patterns/SCHEMA.md` package frontmatter; draft directives stay in `canon/directives/draft/` until Archie promotes):

```markdown
---
id: patt.artifacts.traceability
kind: pattern
scope: [src/data/database.py, src/core/candidate.py, src/core/contact.py]
point: >
  Record which versioned agent + agent_task and which seed artifact ids produced a
  derived artifact; manual edits inherit originating task sources.
---

# Abstract

**Traceability** records the **generation circumstances** of a derived artifact
version: the **versioned `agent_id`**, the **versioned `agent_task_id`**
(`task_key_uuid`), and the **array of artifact ids** whose bodies seeded prompt
tokens for that write. Later **manual** edits (UI or Estelle) create a new
artifact version marked manual while **inheriting** those originating task
sources — so explainability can still name the generative lineage after human
revision. This pattern is **documentation only** until a dedicated implement
ticket lands; read-operative / write-operative do **not** persist seed ids by
themselves.

# Arc

1. **Before** — An agent (or craft chain) is about to write a derived operative
   artifact, holding the active agent row, agent_task row, and the current
   artifact ids used as prompt inputs.
2. **During** — Persist provenance beside the new artifact version (exact column
   / sidecar shape is implement-ticket work): versioned agent_id, versioned
   agent_task_id, seed `artifact_id[]`.
3. **After** — A UI or Estelle manual edit writes a new version via write-operative,
   marks the version as manual, and copies forward the inherited originating
   task sources (does not clear generative lineage).

# Applications

1. Explaining which prompt inputs seeded a job artifact build.
2. Contact answers that must cite generative lineage after a human touch-up.
3. Future grade/analysis explainability that needs seed pins beyond a single
   output pin.

# Exceptions

1. **This epic (AST-1571)** — Draft only; no product persist/wire.
2. **Read-operative / write-operative alone** — Pins identify a body; they do not
   replace the seed-id array documented here.
3. **Library blob fields** — Not a substitute for versioned provenance.

# Implementation

1. **Draft** — Land this file under `canon/directives/draft/`; cite from define /
   plan tickets; do not treat as approved runtime law until Archie promotes.
2. **Capture at generative write** — When an agent-produced operative write lands,
   record versioned `agent_id`, versioned `agent_task_id`, and the seed
   `artifact_id[]` that fed tokens (implement ticket).
3. **Manual edit inheritance** — UI / Estelle write-operative paths that create a
   new version after a human edit mark the version manual and copy inherited
   originating task sources forward (implement ticket).
4. **Consumers** — Prefer provenance records over reconstructing seeds from live
   current rows.
5. **Non-goal here** — No schema, no API field, no Contact/UI wire in AST-1584 /
   AST-1585.

# OPEN QUESTIONS / DECISIONS

1. Storage shape (columns on `artifacts` vs sidecar table) — deferred to the
   implement ticket Archie approves after this draft.
2. Whether every manual edit must require a non-empty inherited seed array when
   the prior version had none (legacy rows) — deferred.
```

2. Do **not** add product code that writes seed ids. Do **not** promote this file out of `draft/`. Do **not** edit `patt.artifact.read-operative.md` beyond leaving it cited.

## Estimate

Confirm Chuckles estimate: 3 — agree

One data PK fetch + one core helper + one draft directive; known pattern parallel to write-operative / `get_agent_data`; no schema migration; sibling owns UI/Contact.

## Review (build)

**Built @ `635931b3`** — `origin/sub/AST-1571/AST-1584-get-by-uuid-candidate-read-operative-traceability`

Stages 1–3 landed: `database.get_artifact` by PK; `candidate.get_operative_base_resume` pin→body for pilot `candidate.artifacts.base_resume`; draft `canon/directives/draft/patt.artifacts.traceability.md` (docs only). Sibling AST-1585 owns UI/Contact wire.

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1584
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1571/AST-1584-get-by-uuid-candidate-read-operative-traceability` @ `361d33257f74fcc1202772c9a536844af9535893`

## Traceability
AC1→S1+S2 (by-uuid fetch + operative path; no coat-check/blob fallback) · AC2→S2 (`get_operative_base_resume` pilot pin→body) · AC3→S3 (traceability draft; docs-only, no persist/wire) · AC4→Explicit scope gate + Out-of-scope table (no UI/Contact/grade writers/new catalog keys/read-current/coat-check/HTTP `artifact_id`)

## Findings

### acceptable — Stage 1 Decision note cites `get_agent_data` as PK parallel
**Location:** Stage 1 ⚠️ Decision  
**Finding:** Existing PK helper is `get_agent`, not `get_agent_data`.  
**Recommendation:** Optional wording fix only; placement/shape parallel to `get_agent` is correct.

### acceptable — Child AC1 “pilot body” vs data-layer row dict
**Location:** Stage 1 vs child AC1  
**Finding:** `get_artifact` returns full row dict; body extraction is in S2 — matches parent Technical scope (“structured result”) and read-operative pattern (core enforces pilot identity before body).  
**Recommendation:** No plan change required.

context_tokens≈48000


## Radia review

# Radia review — AST-1584

**Status gate:** Spawn prompt `Tests Passed` — trusted; no re-fetch.

**Baseline:** `origin/dev`  
**Publish ref:** `origin/sub/AST-1571/AST-1584-get-by-uuid-candidate-read-operative-traceability` @ `cd309487`

---

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1584
**Publish ref:** origin/sub/AST-1571/AST-1584-get-by-uuid-candidate-read-operative-traceability @ cd309487
**Overall:** CLEAN
```

## Statutes checked

Full active set (64 per `canon/statutes/README.md` § Harvested corpus). Diff layers: `core`, `data`, `docs`; paths include `src/core/candidate.py`, `src/data/database.py`, `canon/directives/draft/patt.artifacts.traceability.md`, `docs/features/**`, `docs/test-bible/**`, `tests/component/**`.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | No `src/utils/config.py` or agent-confidence paths in diff |
| astral.agent.do-task-delegation | scoped | conforms | Read helper only; no `do_task` / delegation change |
| astral.agent.grade-vector-validation | scoped | conforms | No grade-vector logic touched |
| astral.batch.batch-id-first | scoped | conforms | No batch-id write paths changed |
| astral.batch.batch-id-format | scoped | conforms | No batch-id formatting changed |
| astral.batch.claim-process-release | scoped | conforms | No claim/process/release paths changed |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No entity-agent-responses paths changed |
| astral.config.config-source-of-truth | scoped | conforms | Pilot identity from `ARTIFACT_CONFIG["candidate.artifacts.base_resume"]` |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No secrets/env wiring in diff |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No repo-root `artifacts/` dir changes |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No `debug/` spike paths in diff |
| astral.dispatch.seed-auto-false | scoped | not-applicable | No `dispatcher.py` / dispatch config paths |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | No run-next / chain paths |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/foundation/ast-1584-…md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch test-tree only; product `src/` from engineer lane |
| astral.git.engineer-test-tree-ban | scoped | conforms | Test-tree on branch via Betty `test()` + `merge-tests()` — not engineer build commits |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Core read helper; no external imports |
| astral.layers.import-direction | scoped | conforms | `candidate.py` → `database` only |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No `scripts/**` changes |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | No `src/ui/**` changes |
| astral.idioms.coat-check-never-store-empty | scoped | conforms | Explicit no coat-check / no blob fallback on read-operative path |
| astral.idioms.render-verdict-orchestrates-consult | scoped | conforms | No consult/render orchestration changed |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | No `src/ui/**` API surface |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | No seed JSON / bootstrap paths |
| astral.seed.archie-catalog-wins | scoped | not-applicable | No dispatcher/catalog seed paths |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | No boot/migration hot-path changes |
| astral.seed.define-approved | scoped | not-applicable | No define/seed approval paths |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No operator-row seed paths |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage-join paths |
| astral.standards.data-raises-caller-logs | scoped | conforms | `get_artifact` returns/raises; no data-layer logging |
| astral.standards.database-header-inventory | scoped | conforms | Uses existing `artifacts` table; no schema/header inventory change needed |
| astral.standards.debug-contract-gated | scoped | conforms | No `debug=` surfaces added |
| astral.standards.dry-and-focused-functions | scoped | conforms | Two focused PK fetch + pin→body helpers |
| astral.standards.in-scope-only | scoped | conforms | Three planned product paths; sibling OOS paths untouched |
| astral.standards.logging-via-utils | scoped | conforms | No new `print` / raw `logging` |
| astral.standards.names-not-ticket-ids | scoped | conforms | `get_artifact`, `get_operative_base_resume` — domain names; ticket ids comments only |
| astral.standards.no-cross-contamination | scoped | conforms | Pilot gate via config; no foreign-entity body leak |
| astral.standards.no-hardcoded-sets | scoped | conforms | `entity_type` / `artifact_type` from `ARTIFACT_CONFIG`, not ad-hoc literals |
| astral.standards.public-then-helpers | scoped | conforms | Public `get_operative_base_resume` placed before hydrate helper |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No `src/utils/**` changes |
| astral.state.core-decides-transitions | scoped | conforms | Read-only; no ad-hoc state writes |
| astral.state.job-prior-states-enforced | scoped | not-applicable | No job-state config paths |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No in-run chain changes |
| astral.ui.frontend-file-placement | scoped | not-applicable | No frontend files |
| astral.ui.naming-conventions | scoped | not-applicable | No UI files |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No gunicorn/config UI paths |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1584): origin/tests 63bbc4a9` present |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `docs` / `merge-tests` vocabulary on branch |
| orch.git.flow-direction-inviolable | universal | conforms | `sub/AST-1571/AST-1584-…` topology |
| orch.git.ftr-sub-topology | universal | conforms | Child on `sub/<parent>/<child>` |
| orch.git.merge-on-checkout | universal | conforms | No rebase/cherry-pick signals in reviewed commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | Clean linear child history |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named branches in publish ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1571 epic worktree pattern |
| orch.git.three-permanent-branches | universal | conforms | Diff vs `origin/dev` only |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No product-policy decisions smuggled in code |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 match plan shape |
| orch.pipeline.project-scoped-queues | universal | conforms | Foundation child within AST-1571 epic |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Review at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No `canon/statutes/**` edits |
| orch.roles.betty-owns-test-tree | universal | conforms | `tests/` + `docs/test-bible/` from Betty lane |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee Ada (engineer) |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | No hook-evasion patterns in diff |

**Straggler (C4):** Joan `[plan-rubric] APPROVED` attached; no Excluded statute list — no straggler rows.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `patt.artifact.read-operative` (parent draft directive) | conforms | By-pin `database.get_artifact`; core pilot gate; no coat-check / blob fallback; retired pins readable |
| `patt.artifacts.traceability` (Stage 3 draft) | conforms | Docs-only draft under `canon/directives/draft/`; no product persist/wire |
| none cited in plan `Patterns to reuse` | — | Parent mandates read-operative; implementation matches draft `# Implementation` steps 1–2 |

## Plan adherence

- **Stage 1:** `get_artifact` matches plan snippet — PK SELECT via `_ARTIFACT_SELECT`, `_artifact_row_dict`, `_run_with_retry`, blank uuid → `ValueError`, no logging, no coat-check, placement after `get_current_artifact`.
- **Stage 2:** `get_operative_base_resume` matches plan — `ARTIFACT_CONFIG` pilot gate, wrong entity/type → `None`, no `candidate_data` walk; module docstring In-scope updated; placed immediately before `hydrate_operative_base_resume_for_response`.
- **Stage 3:** `patt.artifacts.traceability` draft matches plan structure and content; not promoted.
- **Estimate 3:** Footprint fits — one data PK fetch, one core helper, one draft directive (+ expected Betty test-tree).
- **Cross-ticket (AST-1585):** No `contact.py`, `src/ui/api/**`, JAR UI, or pin writers in diff.
- **C6 lenses (§5a–§5g):** Imports top-level; layer direction clean; no silent failure / fallback on operative path; no debug or external-layer touch.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Issue doc vs test-bible sync** — `docs/test-bible/core/candidate.md` and `docs/test-bible/data/database/artifacts.md` carry AST-1584 QA manifest sections; issue doc on publish tip stops at Joan validate (no qa-child block). Chuckles may append manifest pointer when writing back — not blocking.
- **Plan wording (Joan carry-forward)** — Stage 1 Decision cites `get_agent_data` as PK parallel; actual parallel is `get_agent`. Cosmetic plan note only.

## What's solid

- Operative read shape is correct: retired pins remain addressable by uuid; miss/wrong-type/entity return `None`; blob fallback explicitly tested absent (`TestAst1584GetOperativeBaseResume::test_no_candidate_data_blob_fallback`).
- Data layer stays thin — no schema drift, no logging, mirrors `get_current_artifact` deserialization path.
- Traceability draft is appropriately scoped as implement-later documentation.

## Frame diff

| Planned | Landed |
|---------|--------|
| `src/data/database.py` — `get_artifact` | ✓ |
| `src/core/candidate.py` — `get_operative_base_resume` | ✓ |
| `canon/directives/draft/patt.artifacts.traceability.md` | ✓ |
| Betty test-tree (`tests/`, `docs/test-bible/`) | ✓ via `63bbc4a9` + `cd309487 merge-tests` |
| Issue doc qa manifest section | (none) — test-bible holds manifest |

## Notes

- Joan plan-rubric verdict attached; no Excluded statutes to straggle-check.
- Review diff: `git diff origin/dev...origin/sub/AST-1571/AST-1584-get-by-uuid-candidate-read-operative-traceability` (8 files, +494).

context_tokens≈72000

---
