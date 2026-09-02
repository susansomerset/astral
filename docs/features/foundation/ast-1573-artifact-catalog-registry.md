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
