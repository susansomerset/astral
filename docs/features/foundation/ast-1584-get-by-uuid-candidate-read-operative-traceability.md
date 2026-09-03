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
