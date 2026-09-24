<!-- linear-archive: AST-1586 archived 2026-09-24 -->

## Linear archive (AST-1586)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1586/current-read-helper-get-hydrate-pattern-scope-revise-implement  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1570 — Implement patt.artifact.read-current  
**Blocked by / blocks / related:** parent: AST-1570; blocks: AST-1587

### Description

## What this implements

Data-layer current-read contract; candidate `get_candidate_current`-style helper by artifact key; GET hydrate ignores blobs for base_resume; `api_candidate` GET surfaces use it; revise draft pattern so tracker is example-only. Does **not** own builder / token consumer rewires (sibling #2).

## Citations

`patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.database-header-inventory`; `astral.standards.data-raises-caller-logs`; `astral.layers.import-direction`; `astral.config.config-source-of-truth`

## Scope

`src/data/database.py`; `src/core/candidate.py` (helper + GET hydrate only); `src/ui/api/api_candidate.py`; `canon/directives/draft/patt.artifact.read-current.md`

## Acceptance criteria

- [X] A caller can load the pilot current base_resume body via a candidate-owned helper that takes the catalog artifact key; miss returns empty — no `candidate_data` blob fallback.
- [X] Candidate GET overlays base_resume from the artifacts table only; leftover blobs are ignored (not merged as recovery).
- [X] API GET edit/live surfaces that serve base_resume use that hydrate / current-read; no new blob reads for the pilot key on those paths.
- [X] Draft `patt.artifact.read-current` no longer lists tracker as a hard `scope` requirement; tracker appears only as an example.

## Boundaries

- [X] Does not own builder / token / live-display consumer rewires (sibling AST child #2). Contact and tracker out of scope.

## Notes for planning

Pilot key only: `candidate.artifacts.base_resume`. Working helper name: `get_candidate_current`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1570-read-current`, child `sub/AST-1570/AST-<num>-current-read-helper-get-hydrate-pattern-revise`. Created at dispatch-parent.

### Comments

#### radia — 2026-09-03T14:40:08.590Z
[code-rubric] PROCEED (Commit: 9b7e16f) Read-current helper clean

#### betty — 2026-09-03T14:35:39.461Z
origin/sub/AST-1570/AST-1586-current-read-helper-get-hydrate-pattern-revise @ `9b7e16f0` · read-current tests landed

#### joan — 2026-09-03T14:26:37.881Z
[plan-rubric] PROCEED (Commit: 13f7454226e0a117e6c72bbce99814a32c7bea12) helper hydrate pattern aligned

#### ada — 2026-09-03T14:21:35.460Z
13f7454226e0a117e6c72bbce99814a32c7bea12
`origin/sub/AST-1570/AST-1586-current-read-helper-get-hydrate-pattern-revise` @ `13f7454226e0a117e6c72bbce99814a32c7bea12` · plan ready

---

# Current-read helper + GET hydrate + pattern scope revise

**Linear:** [AST-1586](https://linear.app/astralcareermatch/issue/AST-1586/current-read-helper-get-hydrate-pattern-revise-implement-pattartifactread)
**Parent:** [AST-1570](https://linear.app/astralcareermatch/issue/AST-1570/implement-pattartifactread-current) — Implement patt.artifact.read-current
**Publish ref:** `sub/AST-1570/AST-1586-current-read-helper-get-hydrate-pattern-revise`

Finish the read-current data + candidate + API GET half for pilot key `candidate.artifacts.base_resume`: lock `get_current_artifact` as data-layer SoT, add entity-owned `get_candidate_current(candidate_id, artifact_key)`, fix GET hydrate to ignore leftover `candidate_data` blobs on miss, ensure `api_candidate` edit/live GET surfaces use that hydrate only, and revise draft `patt.artifact.read-current` so `tracker.py` is example-only. Does **not** own builder / token / live-display consumer rewires (sibling AST-1587 / Hedy child #2).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/data/database.py` — `get_current_artifact` remains data-layer SoT; empty-on-miss; no blob fallback
- `src/core/candidate.py` — helper + GET hydrate only
- `src/ui/api/api_candidate.py` — GET edit/live surfaces for base_resume
- `canon/directives/draft/patt.artifact.read-current.md` — tracker example-only scope revise

Every row in **Files Changed** is one of those four paths. Every Stage step is the kind of change Scope describes for that file.

**Out of this ticket (do not touch):** `src/core/builder.py`; `src/utils/config.py` (`BASE_RESUME` token path); `format_base_resume_for_token` / structure / whitelist helpers in `candidate.py` (sibling #2); `src/core/contact.py`; `GET /operative/base_resume` pin path (AST-1585 read-operative); `src/core/tracker.py` product code; new `ARTIFACT_CONFIG` keys; coat-check retirement; React editor. Engineer must not create or edit `tests/` or `docs/test-bible/**`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Lock `get_current_artifact` docstring to read-current contract (empty on miss; no blob; no logging) | data |
| `src/core/candidate.py` | Add `get_candidate_current`; refactor `hydrate_operative_base_resume_for_response` to use it and strip stale blobs on miss; update module In-scope line | core |
| `src/ui/api/api_candidate.py` | Confirm GET edit/live handlers resolve base_resume only via hydrated `get_candidate` / hydrate helper — no direct blob or `get_current_artifact` reads for pilot | ui |
| `canon/directives/draft/patt.artifact.read-current.md` | Drop `tracker.py` from frontmatter `scope`; cite tracker as example consumer only | canon |

## Stage 1: Data-layer current-read contract

**Done when:** `database.get_current_artifact` docstring explicitly cites `patt.artifact.read-current`, states empty-on-miss (`None`), no `*_data` blob read, and no logging; function behavior is unchanged.

1. In `src/data/database.py`, open `get_current_artifact(entity_type, entity_id, artifact_type)`.
2. Replace the one-line docstring with:

```python
"""Return the current=1 artifacts row for the natural key, or None (patt.artifact.read-current).

Deserializes artifact_data via _artifact_row_dict. Empty on miss. Never reads
candidate_data / job_data blobs. No coat-check. No logging (callers log).
"""
```

3. Do **not** change the SELECT, signature, `_normalize_artifact_identity` usage, or retry wrapper.
4. Do **not** add logging inside this function (`astral.standards.data-raises-caller-logs`).

## Stage 2: `get_candidate_current` + GET hydrate (ignore blobs on miss)

**Done when:** `get_candidate_current(candidate_id, artifact_key)` returns the operative current body for a catalog key on hit and `None` on miss; it never reads `candidate_data.artifacts.*`; `hydrate_operative_base_resume_for_response` overlays table current on hit and **removes** stale `artifacts.base_resume` blob copies on miss; `get_candidate` continues to hydrate through the updated helper.

⚠️ **Decision:** On miss, hydrate **pops** `base_resume` from the outbound `cd["artifacts"]` dict when present (do not leave the legacy blob as recovery). On hit, set `arts["base_resume"] = body` as today. Absent `artifacts` dict stays absent on miss — do not invent an empty dict shell unless `artifacts` already exists with a stale key to strip.

1. In `src/core/candidate.py` module docstring **In-scope:** line, append after the AST-1584 read-operative clause:

```
get_candidate_current(candidate_id, artifact_key) current-read by catalog key
(AST-1586 / patt.artifact.read-current).
```

2. Immediately **before** `hydrate_operative_base_resume_for_response`, add this public function (public-then-helpers — same block as `get_operative_base_resume`):

```python
def get_candidate_current(candidate_id: str, artifact_key: str) -> Optional[Any]:
    """Current-read body for a catalog artifact key (patt.artifact.read-current).

    Resolves ARTIFACT_CONFIG, calls database.get_current_artifact for the scoped
    entity + leaf artifact_type. Returns deserialized artifact_data, or None on
    miss. Never reads candidate_data blobs. No coat-check.
    """
    key = (artifact_key or "").strip()
    if not key:
        raise ValueError("artifact_key required")
    entry = ARTIFACT_CONFIG.get(key)
    if entry is None:
        raise ValueError(f"unknown catalog key: {key!r}")
    if not entry.get("candidate_scoped"):
        raise ValueError(f"catalog key not candidate-scoped: {key!r}")
    cid = (candidate_id or "").strip()
    if not cid:
        raise ValueError("candidate_id required")
    artifact_type = key.rsplit(".", 1)[-1]
    row = database.get_current_artifact(entry["entity_type"], cid, artifact_type)
    if row is None:
        return None
    return row.get("artifact_data")
```

3. Ensure `ARTIFACT_CONFIG` is already imported from `src.utils.config` at module top (added in AST-1576). Do **not** add new config keys.

4. Replace the body of `hydrate_operative_base_resume_for_response` with:

```python
def hydrate_operative_base_resume_for_response(candidate_id: str, cd: dict) -> None:
    """Overlay operative current base_resume into candidate_data (display only)."""
    if not isinstance(cd, dict):
        return
    pilot_key = "candidate.artifacts.base_resume"
    body = get_candidate_current(candidate_id, pilot_key)
    arts = cd.get("artifacts")
    if body is None:
        if isinstance(arts, dict) and "base_resume" in arts:
            arts.pop("base_resume")
        return
    if not isinstance(arts, dict):
        arts = {}
        cd["artifacts"] = arts
    arts["base_resume"] = body
```

5. Do **not** change `get_operative_base_resume` (read-operative pin path — AST-1584).
6. Do **not** change `format_base_resume_for_token`, `hydrate_resume_structure_from_base_resume`, whitelist/structure helpers, or `save_candidate_data` operative path (sibling #2 owns live-display/token rewires).
7. Leave `get_candidate` calling `hydrate_operative_base_resume_for_response` as today — no signature change.

## Stage 3: API GET edit/live surfaces

**Done when:** Authenticated GET handlers that expose candidate `base_resume` for edit/live display obtain it only through `get_candidate` / `hydrate_operative_base_resume_for_response` (which now strips stale blobs on miss); no handler calls `database.get_current_artifact` or reads raw `candidate_data` blobs for the pilot key.

1. In `src/ui/api/api_candidate.py`, audit these GET routes only:
   - `GET /<candidate_id>` (`get_candidate_detail`)
   - `GET /<candidate_id>/resume_structure` (`get_candidate_resume_structure`)
   - Any other GET in this file that reads `artifacts.base_resume` from a candidate row for edit/live display (grep `base_resume` in this module).

2. **`get_candidate_detail`:** Keep flow: `get_candidate(candidate_id)` → rubric hydrate → `hydrate_operative_base_resume_for_response(candidate_id, cd)`. The second hydrate call is idempotent after Stage 2 — leave it so the handler’s local `cd` copy is definitely table-backed. Do **not** add blob reads.

3. **`get_candidate_resume_structure`:** Keep `candidate = get_candidate(candidate_id)` then `artifacts.get("base_resume")` from the **already-hydrated** `candidate_data`. After Stage 2, a stale DB blob is stripped on miss before this read — no code change required unless grep finds a pre-hydrate blob path; if so, route through `get_candidate` only.

4. **`GET /<candidate_id>/operative/base_resume`:** **Do not modify** — that route is read-operative pin resolve (AST-1585 / `resolve_pinned_base_resume`), not read-current.

5. Do **not** change PUT/POST save handlers, `_sanitize_candidate`, or import `database` into this module.

## Stage 4: Pattern draft — tracker example-only

**Done when:** `canon/directives/draft/patt.artifact.read-current.md` frontmatter `scope` lists only the files this wave requires (data + candidate + ui api candidate); `src/core/tracker.py` appears in **Applications** or **Implementation** as an example consumer, not as a hard scope requirement.

1. In `canon/directives/draft/patt.artifact.read-current.md`, change frontmatter:

```yaml
scope: [src/data/database.py, src/core/candidate.py, src/ui/api/api_candidate.py]
```

2. In **# Applications**, append a bullet (after existing items):

```
4. Job live-display hydrate — `src/core/tracker.py` calls `get_current_artifact` for job-scoped keys when cataloged; example consumer only until job keys ship (not a required touch for candidate pilot read-current).
```

3. In **# Implementation**, after step 1 (**Load**), add one sentence:

```
Entity-owned wrappers (e.g. `get_candidate_current(candidate_id, artifact_key)` on `candidate.py`) resolve `ARTIFACT_CONFIG` then delegate to `get_current_artifact`.
```

4. Do **not** edit other pattern files. Do **not** change tracker product code.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Review (build stub)

**Built:** `origin/sub/AST-1570/AST-1586-current-read-helper-get-hydrate-pattern-revise` @ `8cbe5486`.

**Stages delivered:**
- Stage 1: `get_current_artifact` read-current docstring — `d91d508b`.
- Stage 2: `get_candidate_current` + hydrate strips stale blobs on miss — `25530082`.
- Stage 3: `api_candidate` GET edit/live paths confirmed (no blob reads; no file change).
- Stage 4: `patt.artifact.read-current` tracker example-only scope — `8cbe5486`.

**Betty:** at **Code Complete** — cover `get_candidate_current` hit/miss/unknown key; hydrate pops stale `artifacts.base_resume` on miss when no current row; GET detail/resume_structure table-only overlay.

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1586
**Overall:** APPROVED
**Publish ref:** `sub/AST-1570/AST-1586-current-read-helper-get-hydrate-pattern-revise` @ `13f7454226e0a117e6c72bbce99814a32c7bea12`

## Traceability
AC1→Stage2; AC2→Stage2; AC3→Stages2–3; AC4→Stage4; parent AC4/AC7→N/A (sibling AST-1587); parent AC6→Explicit scope gate + Boundaries

## Findings
None.

context_tokens≈42000
```

## Radia review

**Overall:** CLEAN — no fix-now, discuss, or advisory items.

```
[code-rubric] PROCEED (Commit: 9b7e16f0ad0ddd356521cf3665bb7fae6989446b) Read-current helper clean
```

All four engineer stages delivered per plan. `get_candidate_current` → `get_current_artifact`; hydrate strips stale blob on miss. Betty manifest covers helper hit/miss, hydrate strip, GET detail overlay. Pattern draft scope revised. Sibling AST-1587 consumer rewires correctly deferred.
