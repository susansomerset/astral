# Artifact catalog registry

**Linear:** [AST-1573](https://linear.app/astralcareermatch/issue/AST-1573/artifact-catalog-registry-implement-pattartifactmanage-catalog)
**Parent:** [AST-1568](https://linear.app/astralcareermatch/issue/AST-1568/implement-pattartifactmanage-catalog) — Implement patt.artifact.manage-catalog
**Publish ref:** `sub/AST-1568/AST-1573-artifact-catalog-registry`

Ship the catalog half of `patt.artifact.manage-catalog` for one pilot key only: candidate `base_resume`. Config holds the authoritative registry; thin utils helpers resolve and validate keys so AST-1569+ never scrape `config` internals. No write-operative / read-current product wiring, no job keys, no coat-check changes, no UI/API.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/utils/config.py` — catalog block + `base_resume` entry
- `src/utils/artifact_catalog.py` — new helpers
- `tests/component/utils/test_artifact_catalog.py` — lookup + data-layer scaffold round-trip

Every row in **Files Changed** is one of those three paths. Engineer `code()` commits touch only the two `src/utils/` files; Betty owns the test path via `qa-child` (engineer test-tree ban).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add top-level `ARTIFACT_CATALOG` with sole `base_resume` entry; module-docstring inventory line; startup asserts | utils |
| `src/utils/artifact_catalog.py` | New module: `get_catalog_entry`, `require_catalog_entry`, `is_candidate_scoped` (read-only, no I/O) | utils |
| `tests/component/utils/test_artifact_catalog.py` | New: catalog lookup + unknown-key fail-fast + `save_artifact` → `get_current_artifact` scaffold using catalog-derived identity (**Betty `qa-child` only**) | tests |

**Out of this ticket (do not touch):** `job_resume` / `cover_letter` catalog rows; write-operative / read-current / read-operative product paths (AST-1569+); coat-check registration or retirement (AST-1572); UI/API; `src/core/**`; `src/data/database.py` signatures; `docs/ASTRAL_CODE_RULES.md`; canon draft promotion. Engineer must not create or edit `tests/` or `docs/test-bible/**`.

## Stage 1: `ARTIFACT_CATALOG` in config

**Done when:** Importing `src.utils.config` exposes `ARTIFACT_CATALOG` with exactly one key `base_resume`, metadata complete, and startup asserts pass. No helper module yet.

1. In `src/utils/config.py` module docstring **Config sections:** list, add this line immediately after the existing `BUILD_CONFIG` line:

```
  ARTIFACT_CATALOG — versioned artifact-type registry (entity, candidate_scoped, body_shape, ingestion_owner); pilot = base_resume only (AST-1573)
```

2. Immediately **after** the `BUILD_CONFIG = { ... }` closing `}` (the block that ends just before `def get_cover_letter_render_token`), insert:

```python
# AST-1573: authoritative artifact-type registry (patt.artifact.manage-catalog register half).
# Key = artifact_type string. Pilot only: candidate base_resume. Job keys = siblings.
ARTIFACT_CATALOG = {
    "base_resume": {
        "entity_type": "candidate",
        "candidate_scoped": True,
        # Name into BUILD_CONFIG["artifact_shapes"] (resume section contract).
        "body_shape": "resume_content",
        # Core component that owns first-row ingestion for this key (UI save / snapshot today).
        "ingestion_owner": "candidate",
    },
}
```

⚠️ **Decision:** Catalog is a dedicated top-level `ARTIFACT_CATALOG` (not nested under `BUILD_CONFIG` / a fictional `ARTIFACT_CONFIG`). Helpers import this symbol; callers never read `config.ARTIFACT_CATALOG` directly after Stage 2 (AST-1569 AC). Keying by artifact type string alone matches parent AC (“unknown artifact type strings fail fast”); `entity_type` lives in the value.

3. Immediately after that dict, add these asserts (same style as nearby TOPIC_MENU / BUILD asserts):

```python
assert set(ARTIFACT_CATALOG.keys()) == {"base_resume"}
_br = ARTIFACT_CATALOG["base_resume"]
assert _br["entity_type"] == "candidate"
assert _br["entity_type"] in ENTITY_TYPES
assert _br["candidate_scoped"] is True
assert isinstance(_br["candidate_scoped"], bool)
assert _br["body_shape"] == "resume_content"
assert _br["body_shape"] in BUILD_CONFIG["artifact_shapes"]
assert _br["ingestion_owner"] == "candidate"
assert set(_br.keys()) == {
    "entity_type",
    "candidate_scoped",
    "body_shape",
    "ingestion_owner",
}
```

4. Do **not** add any other catalog keys. Do **not** change `BUILD_CONFIG["artifact_shapes"]`, `TOPIC_MENU_CONFIG`, coat-check maps, or token sources.

## Stage 2: `artifact_catalog.py` helpers

**Done when:** `from src.utils.artifact_catalog import get_catalog_entry, require_catalog_entry, is_candidate_scoped` works; known key resolves; unknown key fails fast; helpers perform no DB/network I/O and do not import `src.data` or `src.core`.

1. Create `src/utils/artifact_catalog.py` with this module docstring and imports:

```python
# -*- coding: utf-8 -*-
"""Read-only accessors over ARTIFACT_CATALOG (AST-1573 / patt.artifact.manage-catalog).

Callers resolve artifact keys here — do not scrape config.ARTIFACT_CATALOG internals.
No I/O.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.utils.config import ARTIFACT_CATALOG
```

2. Implement public functions in this order (public then helpers — no private helpers needed):

```python
def get_catalog_entry(artifact_type: str) -> Optional[Dict[str, Any]]:
    """Return the catalog metadata dict for ``artifact_type``, or None if unregistered."""
    if not isinstance(artifact_type, str) or not artifact_type.strip():
        return None
    entry = ARTIFACT_CATALOG.get(artifact_type.strip())
    return dict(entry) if entry is not None else None


def require_catalog_entry(artifact_type: str) -> Dict[str, Any]:
    """Return catalog metadata for ``artifact_type``; raise ValueError if unknown/blank."""
    if not isinstance(artifact_type, str) or not artifact_type.strip():
        raise ValueError(f"unknown artifact type: {artifact_type!r}")
    key = artifact_type.strip()
    entry = ARTIFACT_CATALOG.get(key)
    if entry is None:
        raise ValueError(f"unknown artifact type: {key!r}")
    return dict(entry)


def is_candidate_scoped(artifact_type: str) -> bool:
    """True when the registered key is candidate-scoped; unknown keys raise via require."""
    return bool(require_catalog_entry(artifact_type)["candidate_scoped"])
```

⚠️ **Decision:** `get_catalog_entry` returns `None` for blank/unknown (soft lookup); `require_catalog_entry` / `is_candidate_scoped` raise `ValueError` with message prefix `unknown artifact type:` and the repr’d key — no silent fallback, no default entity. Returned dicts are shallow copies so callers cannot mutate the config literal in place.

3. Do **not** add write helpers, list-all APIs, coat-check hooks, or imports of `database` / `candidate`. Do **not** re-export `ARTIFACT_CATALOG` as a public module attribute beyond the import used by the three functions.

## Scaffold test contract (Betty `qa-child` — not engineer `code()`)

**Done when (Betty):** `tests/component/utils/test_artifact_catalog.py` exists and covers AC1–AC3. Engineer does not create this file.

Betty implements approximately:

1. **Lookup** — `require_catalog_entry("base_resume")` returns `entity_type == "candidate"`, `candidate_scoped is True`, `body_shape == "resume_content"`, `ingestion_owner == "candidate"`; `get_catalog_entry("base_resume")` is non-None; `is_candidate_scoped("base_resume") is True`; `len`/`set` of `ARTIFACT_CATALOG` is exactly `{"base_resume"}` (via helpers or config import only as needed for AC1).
2. **Fail-fast** — `require_catalog_entry("not_a_real_artifact")` and `is_candidate_scoped("not_a_real_artifact")` raise `ValueError` whose message contains `unknown artifact type`; `get_catalog_entry("not_a_real_artifact") is None`.
3. **Scaffold round-trip** — Using catalog-derived `entity_type` and the artifact type string `"base_resume"` (not hardcoding a parallel tuple outside the catalog), call `database.save_artifact(entity_type, entity_id, artifact_type, payload)` then `database.get_current_artifact(...)` against the existing `sqlite_in_memory` fixture pattern from `tests/component/data/database/test_artifacts.py`. Assert returned row `artifact_data` matches payload and `artifact_type == "base_resume"`. This proves catalog identity plugs into the existing data-layer APIs — not write-operative product paths.

## Execution contract

- Stages 1 → 2 in order on the epic worktree; one commit per stage (or one combined `code()` if build-child allows a single product commit — prefer one commit per stage).
- Do not add files outside **Files Changed**.
- Do not register job artifact keys or wire UI/API/core consumers.
- Ambiguity or codebase drift → stop; comment on parent AST-1568 with the Stage blocked template from plan-child.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Review (build)

**Built @ `cdf7fe63`** — `origin/sub/AST-1568/AST-1573-artifact-catalog-registry`

Product stages 1–2 landed (`ARTIFACT_CATALOG` + `artifact_catalog.py`). Scaffold test path remains Betty `qa-child` (AC3).

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1573
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1568/AST-1573-artifact-catalog-registry` @ `c4215e2e08fd805d848f87ce6996c1ba8c4c3c43`

## Traceability
AC1→Stage 1 (`ARTIFACT_CATALOG` + asserts); AC2→Stage 2 (`require_catalog_entry` / `is_candidate_scoped` fail-fast); AC3→Betty scaffold test contract (`save_artifact`→`get_current_artifact`); AC4→Explicit scope gate + OOS list (no coat-check/blob reads); AC5→Stage 2 (`artifact_catalog.py` accessors, no config scraping).

## Findings

### acceptable — Draft pattern citation path
- **Location:** Parent Architectural definition / plan intro
- **Finding:** `patt.artifact.manage-catalog` lives under `canon/directives/draft/`, not `canon/patterns/**` with `status: approved`.
- **Recommendation:** Accept for this epic per parent definition + Archie supersede note; draft promotion explicitly OOS. Register-half stages match pattern Implementation §1.

### acceptable — Superseded conflicting guidance (not co-equal)
- **Location:** Plan boundaries vs legacy idioms
- **Finding:** Parent requires catalog authority over ad-hoc `base_resume` tuples, coat-check registration, and direct blob reads for this key.
- **Recommendation:** Plan correctly defers read/write-operative wiring (AST-1569+), coat-check retirement (AST-1572), and UI/API; no conflicting steps in Files Changed or Stages.

### acceptable — No formal `## Self-assessment` block
- **Location:** Plan structure
- **Finding:** Scope/Conf/Risk axes absent; `## Estimate` confirm line present.
- **Recommendation:** Catalog-only vertical with explicit scope gate and stage Done-when lines — sufficient for this slice (cf. AST-1529 precedent).

### acceptable — Assignee at fetch time
- **Location:** Linear ticket
- **Finding:** Assignee was Ada Lovelace at `get-issue`, not Joan.
- **Recommendation:** Chuckles handoff in flight; validation proceeded per spawn. No plan defect.

**In-session (R1/R2/R3/R4 — not in attachment):** Universal `orch.*` statutes considered — all `conforms`. Scoped statutes considered: `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.standards.in-scope-only` — all `conforms`. Layer/import/file-placement/config/DRY checklist: pass (`utils`-only product footprint; `body_shape` references existing `BUILD_CONFIG["artifact_shapes"]["resume_content"]`; Betty owns test path per `orch.roles.betty-owns-test-tree`).

context_tokens≈42000

---

## Radia review

# Radia code review — AST-1573

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1573
**Publish ref:** `origin/sub/AST-1568/AST-1573-artifact-catalog-registry` @ `2de65c08cf46c2fcf4e25b08a0646388269de8e2`
**Overall:** CLEAN

**Diff change set:** 5 paths — `src/utils/config.py` (modify), `src/utils/artifact_catalog.py` (add), `tests/component/utils/test_artifact_catalog.py` (add), `docs/test-bible/utils/artifact_catalog.md` (add), `docs/features/foundation/ast-1573-artifact-catalog-registry.md` (add). Layers: `utils`, `docs`/tests. Change types: `add`, `modify`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `orch.pipeline.plan-is-bible` | universal | conforms | Product + tests match staged plan; no scope drift |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | No product-policy forks |
| `orch.pipeline.project-scoped-queues` | universal | conforms | N/A to diff |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | N/A to diff |
| `orch.roles.archie-approves-statutes` | universal | conforms | N/A to diff |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Test + bible on Betty `test()` / `merge-tests()` SHAs |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | N/A to diff |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada assignee; engineer `code()` only `src/utils/` |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No hook-evasion signals in diff |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1573)` present |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `test` / `docs` / `merge-tests` vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | `sub/AST-1568/…` publish topology |
| `orch.git.ftr-sub-topology` | universal | conforms | Child sub under parent AST-1568 |
| `orch.git.merge-on-checkout` | universal | conforms | No rebase/cherry-pick on diff |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | Clean three-dot diff vs `origin/dev` |
| `orch.git.no-dev-agent-branches` | universal | conforms | No agent-named publish refs |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | Epic worktree path correct |
| `orch.git.three-permanent-branches` | universal | conforms | N/A to diff |
| `astral.agent.confidence-bounds` | scoped | not-applicable | No agent/dispatch paths |
| `astral.agent.do-task-delegation` | scoped | not-applicable | No agent paths |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | No grading paths |
| `astral.batch.batch-id-first` | scoped | not-applicable | No batch paths |
| `astral.batch.batch-id-format` | scoped | not-applicable | No batch paths |
| `astral.batch.claim-process-release` | scoped | not-applicable | No batch paths |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | No batch paths |
| `astral.config.config-source-of-truth` | scoped | conforms | `ARTIFACT_CATALOG` authoritative block in `config.py` |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | No secrets/env reads |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | No debug artifact paths |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | No spike files |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | No dispatch/seed |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | No run_next |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single `ast-1573-*.md` feature doc |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty diff: tests + test-bible only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Engineer `code()` SHAs touch only `src/utils/` |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | No core/external |
| `astral.layers.import-direction` | scoped | conforms | `artifact_catalog` → `config` only (utils→utils) |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | No scripts |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | No UI |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | Coat-check OOS (AST-1572) |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | No render/consult |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | No API |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | No seed tables |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | No seed catalog |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | No boot SQL |
| `astral.seed.define-approved` | scoped | not-applicable | No define |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | No seed rows |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | No seed |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | No `src/data` edits |
| `astral.standards.database-header-inventory` | scoped | not-applicable | No `database.py` |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | No debug logging |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Three small accessors; no duplication |
| `astral.standards.in-scope-only` | scoped | conforms | Pilot key only; siblings deferred |
| `astral.standards.logging-via-utils` | scoped | conforms | No logging added |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | `AST-1573` only in comments/docstring carve-out |
| `astral.standards.no-cross-contamination` | scoped | not-applicable | No cross-module contamination |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Registry + startup asserts in config |
| `astral.standards.public-then-helpers` | scoped | conforms | Public API only; no private helpers |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | No data imports |
| `astral.state.core-decides-transitions` | scoped | not-applicable | No state machine |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | No job states |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | No run chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | No frontend |
| `astral.ui.naming-conventions` | scoped | not-applicable | No UI |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | No server config |

**Sweep count:** 64 active harvested statutes scored (per `canon/statutes/README.md` harvested table; `astral.config.pass-threshold-vs-score-floor` retired — excluded).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `patt.artifact.manage-catalog` | conforms | Register-half matches draft Implementation §1; Joan APPROVED draft-directive citation at plan time; promotion OOS |

## Plan adherence

Stages 1–2 land exactly as specced: `ARTIFACT_CATALOG` with sole `base_resume`, module-docstring inventory line, startup asserts wired to `ENTITY_TYPES` and `BUILD_CONFIG["artifact_shapes"]`, and read-only `artifact_catalog.py` helpers with soft `None` / hard `ValueError` fail-fast and shallow-copy returns. Betty scaffold (`test_artifact_catalog.py` + bible manifest) covers AC1–AC3 including catalog-derived `entity_type` → `save_artifact` / `get_current_artifact` round-trip. Explicit scope gate honored: no job keys, coat-check, core/UI/API, or write-operative wiring. Estimate **3** still fits footprint. Cross-ticket boundaries clean (AST-1569+ / AST-1572 deferred).

**Joan straggler (C4):** No Excluded-statute list in Joan attachment; no straggler rows.

## Findings

*(none — no fix-now / discuss / advisory code findings)*

## What's solid

- Thin utils accessor module with correct layer imports and zero I/O.
- Startup asserts prevent catalog drift from `ENTITY_TYPES` / `artifact_shapes`.
- Tests exercise whitespace trimming, blank/unknown fail-fast, shallow-copy isolation, and data-layer scaffold without hardcoding a parallel `(entity, type)` tuple.
- Engineer/test ownership split respected (`code()` → `src/utils/` only; Betty → tests + bible).

## Frame diff

Post-Joan (`c4215e2e`) → tip (`2de65c08`):

| Area | Change |
|------|--------|
| `src/utils/config.py` | `+ARTIFACT_CATALOG` block + asserts (Stage 1) |
| `src/utils/artifact_catalog.py` | New module (Stage 2) |
| `tests/component/utils/test_artifact_catalog.py` | Betty AC1–AC3 scaffold |
| `docs/test-bible/utils/artifact_catalog.md` | Betty manifest |
| Issue doc | Build review stub + Joan block (pre-existing on branch) |

All frame deltas are expected post-plan execution; no unplanned product surface.

## Notes

- Pattern id `patt.artifact.manage-catalog` lives under `canon/directives/draft/` (not approved `canon/patterns/**`); Joan closed this at plan validate — no re-litigation.
- Product callers should route through `artifact_catalog` helpers per plan (AST-1569 AC); tests may import `ARTIFACT_CATALOG` for key-set asserts per scaffold contract.
- Branch history includes merged sibling meteorite work; **three-dot diff vs `origin/dev` is AST-1573-only** (5 files) — correct review surface.

context_tokens≈38000

## Bug: AST-1575 — Rename ARTIFACT_CATALOG→ARTIFACT_CONFIG and hierarchical catalog keys

### As-is

Landed AST-1573 pilot registers flat catalog key `base_resume` under top-level config block `ARTIFACT_CATALOG`. Helpers in `src/utils/artifact_catalog.py` import that symbol and look up by the flat key; Betty’s scaffold (`tests/component/utils/test_artifact_catalog.py` + bible) asserts the same names.

### To-be

Config block is `ARTIFACT_CONFIG` (standard `_CONFIG` suffix). Sole pilot catalog key is the hierarchical `_data` path `candidate.artifacts.base_resume`. Helpers, startup asserts, and catalog tests/bible use `ARTIFACT_CONFIG` and that hierarchical key. Flat `base_resume` no longer resolves. Data-layer `artifacts.artifact_type` for the pilot remains the leaf `base_resume`.

### Repro

1. `from src.utils.config import ARTIFACT_CATALOG` succeeds; `ARTIFACT_CONFIG` is missing.
2. `require_catalog_entry("base_resume")` returns the pilot entry; `require_catalog_entry("candidate.artifacts.base_resume")` raises `ValueError`.
3. Module docstring inventory still lists `ARTIFACT_CATALOG`.

### Root cause

AST-1573 Stage 1 chose a dedicated top-level `ARTIFACT_CATALOG` keyed by bare artifact-type strings. UAT on the parent asks for the platform’s usual `_CONFIG` block suffix and for catalog keys that match existing entity `_data` dotted paths (`candidate.artifacts.*`, etc.).

### Proposed change

⚠️ **Decision:** Keep the four metadata fields (`entity_type`, `candidate_scoped`, `body_shape`, `ingestion_owner`) unchanged. Hierarchical key is the dict key only. For `save_artifact` / `get_current_artifact`, callers use `entry["entity_type"]` and the leaf segment of the catalog key (`catalog_key.rsplit(".", 1)[-1]` → `base_resume`). Do **not** add a fifth metadata field; do **not** alias flat `base_resume` as a second lookup key.

1. In `src/utils/config.py` module docstring **Config sections:** line, replace `ARTIFACT_CATALOG — …` with:

```
  ARTIFACT_CONFIG — versioned artifact registry keyed by entity._data path (entity, candidate_scoped, body_shape, ingestion_owner); pilot = candidate.artifacts.base_resume (AST-1573 / AST-1575)
```

2. In `src/utils/config.py`, rename the block and sole key (same placement after `BUILD_CONFIG`):

```python
ARTIFACT_CONFIG = {
    "candidate.artifacts.base_resume": {
        "entity_type": "candidate",
        "candidate_scoped": True,
        "body_shape": "resume_content",
        "ingestion_owner": "candidate",
    },
}

assert set(ARTIFACT_CONFIG.keys()) == {"candidate.artifacts.base_resume"}
_br = ARTIFACT_CONFIG["candidate.artifacts.base_resume"]
assert _br["entity_type"] == "candidate"
assert _br["entity_type"] in ENTITY_TYPES
assert _br["candidate_scoped"] is True
assert isinstance(_br["candidate_scoped"], bool)
assert _br["body_shape"] == "resume_content"
assert _br["body_shape"] in BUILD_CONFIG["artifact_shapes"]
assert _br["ingestion_owner"] == "candidate"
assert set(_br.keys()) == {
    "entity_type",
    "candidate_scoped",
    "body_shape",
    "ingestion_owner",
}
```

Delete every remaining `ARTIFACT_CATALOG` identifier in this file (no compatibility alias).

3. In `src/utils/artifact_catalog.py`:
   - Import `ARTIFACT_CONFIG` (not `ARTIFACT_CATALOG`).
   - Update module docstring to name `ARTIFACT_CONFIG` and hierarchical catalog keys.
   - Keep public function names `get_catalog_entry`, `require_catalog_entry`, `is_candidate_scoped`.
   - Parameter remains a string key; document it as the hierarchical catalog key. Lookup uses `ARTIFACT_CONFIG.get(key.strip())` exactly as today (no path parsing inside get/require).
   - Error message prefix becomes `unknown catalog key:` (was `unknown artifact type:`). Betty updates `match=` / message asserts in the same fix wave.
   - Flat `base_resume`, blank, and unknown hierarchical strings still fail soft (`None`) / hard (`ValueError`) with no silent fallback.
   - Shallow-copy return behavior unchanged.

4. **Betty-owned (qa-fix / make-fix board):** update `tests/component/utils/test_artifact_catalog.py` and `docs/test-bible/utils/artifact_catalog.md` so:
   - Imports and key-set asserts use `ARTIFACT_CONFIG` and `{"candidate.artifacts.base_resume"}`.
   - Lookup / fail-fast / shallow-copy cases call helpers with `candidate.artifacts.base_resume` (and whitespace trim on that hierarchical key).
   - Unknown-key case still uses a non-registered string (e.g. `not_a_real_artifact`); assert flat `base_resume` does **not** resolve via `get_catalog_entry` / `require_catalog_entry`.
   - Scaffold round-trip: `entry = require_catalog_entry("candidate.artifacts.base_resume")`; `artifact_type = "candidate.artifacts.base_resume".rsplit(".", 1)[-1]` (or equivalent literal leaf derived from that key); `save_artifact(entry["entity_type"], …, artifact_type, payload)` then `get_current_artifact` — assert `artifact_type == "base_resume"` on the row.
   - Engineer does **not** commit under `tests/` or `docs/test-bible/**`.

5. Do **not** register `job.artifacts.cover_letter` / `candidate.context.strengths` (UAT examples only). Do **not** wire write-operative / read-current / coat-check / UI/API. Do **not** rename the `artifact_catalog.py` module path this ticket.

### Blast radius

- Any future AST-1569+ code or docs that cite `ARTIFACT_CATALOG` or flat `base_resume` catalog lookup must use `ARTIFACT_CONFIG` + hierarchical keys (none landed yet outside AST-1573 helpers/tests).
- Betty scaffold + bible for AST-1573 must retarget in the same fix wave or the existing node ids go red.
- `save_artifact` / artifacts-table natural key for this content remains leaf `base_resume` — no schema change.

### What must still hold

- Exactly one pilot catalog entry (now keyed `candidate.artifacts.base_resume`).
- Unknown catalog keys fail fast — no silent fallback / no flat-key alias.
- Catalog-derived identity still drives scaffold `save_artifact` → `get_current_artifact` for leaf `base_resume`.
- No new runtime blob reads or coat-check registrations.
- Callers reach catalog via `artifact_catalog` helpers, not by scraping config internals (AST-1573 AC5).
- Parent boundaries: no job keys, no product read/write path wiring, no UI/API, no coat-check retirement.
