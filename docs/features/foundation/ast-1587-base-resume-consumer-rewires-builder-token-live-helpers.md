# Base_resume consumer rewires (builder / token / live helpers)

**Linear:** [AST-1587](https://linear.app/astralcareermatch/issue/AST-1587/base-resume-consumer-rewires-builder-token-live-helpers-implement)
**Parent:** [AST-1570](https://linear.app/astralcareermatch/issue/AST-1570/implement-pattartifactread-current) — Implement patt.artifact.read-current
**Publish ref:** `sub/AST-1570/AST-1587-base-resume-consumer-rewires`

After sibling AST-1586 ships `get_candidate_current`, replace every **in-scope** remaining read of `candidate_data.artifacts.base_resume` blobs with `get_candidate_current(candidate_id, "candidate.artifacts.base_resume")` in builder live-render paths, candidate live-display/token/structure helpers, and the config `{$BASE_RESUME}` token path. Miss → empty / existing error contracts — **no blob fallback**. Add Style D found/recorded on touched `debug=True` current-resolve paths. `api_resume_html` stays a thin builder caller unless audit finds independent blob logic.

**Prerequisite (build-child):** `get_candidate_current` and updated hydrate from **AST-1586** must be present before Stage 1 — merge `origin/sub/AST-1570/AST-1586-current-read-helper-get-hydrate-pattern-revise` (or `origin/ftr/AST-1570-read-current` once rolled) into this worktree via `sync-child.sh` + parent ftr merge. Do **not** re-implement the helper or touch GET hydrate / `api_candidate` / pattern draft (sibling #1 scope).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/builder.py` — replace in-file base_resume blob reads in live build paths
- `src/core/candidate.py` — **live-display / format / structure / whitelist helpers only** (not helper+hydrate — AST-1586)
- `src/utils/config.py` — **`BASE_RESUME` token path only**
- `src/ui/api/api_resume_html.py` — **only if independent of builder**

Every row in **Files Changed** is one of those four paths. Every Stage step is the kind of change Scope describes for that file.

**Out of this ticket (do not touch):** `src/data/database.py`; `get_candidate_current` / `hydrate_operative_base_resume_for_response` implementation (AST-1586); `src/ui/api/api_candidate.py`; `get_operative_base_resume` / read-operative pin path (AST-1585); `src/core/contact.py`; `src/core/tracker.py`; new `ARTIFACT_CONFIG` keys; React editor; coat-check retirement. Engineer must not create or edit `tests/` or `docs/test-bible/**`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Private id helper + rewire live/token/structure helpers to `get_candidate_current`; update whitelist debug source label | core |
| `src/core/builder.py` | Rewire base_resume consumers + source labels; extend `_coerce_candidate_blob` with `_astral_candidate_id`; Style D on current-read in `build_base_resume` | core |
| `src/utils/config.py` | Audit `{$BASE_RESUME}` resolve path — change only if `format_base_resume_for_token` signature/call site needs a threading fix | utils |
| `src/ui/api/api_resume_html.py` | Audit only — expected **no change** (thin `build_base_resume` caller) | ui |

## Stage 1: Candidate live helpers + shared id extraction

**Done when:** `format_base_resume_for_token`, `resolve_resume_structure` (accent shim), `draft_job_resume_allowed_section_keys`, and `pin_experience_job_facts_from_base` obtain pilot base_resume body only via `get_candidate_current` + catalog key; no `artifacts.get("base_resume")` reads remain in these four functions; miss → treat as empty (no blob recovery).

⚠️ **Decision:** Add public helper `candidate_id_for_current_read(cd: dict) -> Optional[str]` that returns stripped `_astral_candidate_id` or `astral_candidate_id` from a token-view / inner `candidate_data` dict. When id is missing, current-read helpers treat body as `None` (empty) — **never** fall back to blob. `do_task` and `build_candidate_token_view` already populate `_astral_candidate_id` on dispatch paths.

1. In `src/core/candidate.py`, immediately **before** `format_base_resume_for_token`, add module constant and helpers (keep `get_candidate_current` public block from AST-1586 untouched):

```python
_PILOT_BASE_RESUME_ARTIFACT_KEY = "candidate.artifacts.base_resume"


def candidate_id_for_current_read(cd: dict) -> Optional[str]:
    """Extract candidate id from token view or inner candidate_data for current-read."""
    if not isinstance(cd, dict):
        return None
    cid = (cd.get("_astral_candidate_id") or cd.get("astral_candidate_id") or "").strip()
    return cid or None


def load_pilot_base_resume_for_candidate(candidate_id: str) -> Optional[Any]:
    """Current-read pilot base_resume body for live/builder consumers (AST-1587)."""
    cid = (candidate_id or "").strip()
    if not cid:
        return None
    return get_candidate_current(cid, _PILOT_BASE_RESUME_ARTIFACT_KEY)
```

2. Replace the body of `format_base_resume_for_token` so it loads body via current-read:

```python
def format_base_resume_for_token(candidate_data: dict) -> str:
    """{$BASE_RESUME}: section-id-keyed JSON for agent prompts (AST-607), never markdown."""
    cd = candidate_data if isinstance(candidate_data, dict) else {}
    cid = candidate_id_for_current_read(cd)
    raw = (
        get_candidate_current(cid, _PILOT_BASE_RESUME_ARTIFACT_KEY)
        if cid
        else None
    )
    structure = resolve_resume_structure(cd)
    content, _struct = ingest_legacy_label_content_base_resume(raw, structure)
    section_ids = {
        sid for sid, spec in _struct.get("sections", {}).items()
        if isinstance(spec, dict) and spec.get("id")
    }
    payload = filter_base_resume_to_structure(content, section_ids)
    return json.dumps(payload, indent=2) if payload else ""
```

3. In `resolve_resume_structure`, replace the legacy accent shim block that reads `artifacts.get("base_resume")` with current-read:

```python
    resolved = default_resume_structure()
    cid = candidate_id_for_current_read(cd)
    br = (
        get_candidate_current(cid, _PILOT_BASE_RESUME_ARTIFACT_KEY)
        if cid
        else None
    )
    if isinstance(br, dict):
        ac = br.get("accent_color")
        ...
```

   (Keep the existing palette / `_HEX_COLOR_RE` validation logic unchanged.)

4. In `draft_job_resume_allowed_section_keys`, replace blob read:

```python
    cid = candidate_id_for_current_read(cd)
    base = (
        get_candidate_current(cid, _PILOT_BASE_RESUME_ARTIFACT_KEY)
        if cid
        else None
    )
```

5. In `pin_experience_job_facts_from_base`, replace:

```python
    cid = candidate_id_for_current_read(candidate_data)
    base = (
        get_candidate_current(cid, _PILOT_BASE_RESUME_ARTIFACT_KEY)
        if cid
        else None
    )
```

   Remove the `artifacts.get("base_resume")` branch entirely.

6. In `validate_draft_job_resume_payload`, when `debug=True`, change the whitelist found detail line from `whitelist_source=base_resume` to:

```python
        logger.debug_detail(
            f"found whitelist_source=get_candidate_current "
            f"artifact_key={_PILOT_BASE_RESUME_ARTIFACT_KEY!r} keys={sorted(allowed)}"
        )
```

7. Do **not** change `hydrate_operative_base_resume_for_response`, `get_operative_base_resume`, `get_candidate`, or `hydrate_resume_structure_from_base_resume` signature/behavior (callers pass an already-resolved body).

## Stage 2: Builder live-render consumer rewires

**Done when:** Every in-scope base_resume **read** in `builder.py` uses `get_candidate_current` (directly or via a passed `candidate_id`); debug source labels and `build_base_resume` Style D reflect current-read, not `candidate_data.artifacts.base_resume`; `build_session_base_resume` unchanged (caller-supplied body, not a blob walk).

⚠️ **Decision:** Extend `_coerce_candidate_blob` to stamp `_astral_candidate_id` when unwrapping a full `get_candidate` row so job-tailored paths can current-read without threading a new parameter through every public entry point.

1. In `_coerce_candidate_blob`, when unwrapping `candidate_data` from a full row, add:

```python
        out["_astral_candidate_id"] = str(raw.get("astral_candidate_id") or "").strip()
```

2. Builder paths call **`candidate_mod.load_pilot_base_resume_for_candidate(cid)`** or resolve `cid` via `candidate_mod.candidate_id_for_current_read(cd)` when only inner `candidate_data` is available.

3. **`build_base_resume`:** Replace `(cd.get("artifacts") or {}).get("base_resume")` with `raw = candidate_mod.load_pilot_base_resume_for_candidate(candidate_id)`. When `debug=True`, **before** ingest, emit current-read Style D:

```python
    if debug:
        _log.debug_index(
            func="builder.build_base_resume",
            index=1,
            total=2,
            identifier=identifier,
            outcome="found",
        )
        _log.debug_detail(
            f"found artifact_key=candidate.artifacts.base_resume "
            f"current_read={'hit' if raw is not None else 'miss'}"
        )
```

   Shift the existing success `debug_index` to `index=2, total=2` with outcome `recorded — base resume html`. Update success detail `resume_source=` to `get_candidate_current(candidate.artifacts.base_resume)`.

4. **`_resolve_resume_sections`:** Replace final blob fallback with:

```python
    cid = candidate_mod.candidate_id_for_current_read(candidate_data)
    br = candidate_mod.load_pilot_base_resume_for_candidate(cid) if cid else None
```

5. **`_merge_effective_style`:** Replace `(candidate_data.get("artifacts") or {}).get("base_resume")` accent fallback with current-read body via `candidate_id_for_current_read` + `load_pilot_base_resume_for_candidate`.

6. **`_resume_content_source_label`:** When job paths miss, if current-read body is non-empty return `"get_candidate_current(candidate.artifacts.base_resume)"` instead of `"candidate_data.artifacts.base_resume"`.

7. **`_accent_source_label`:** When legacy accent comes from current-read body dict, return `"get_candidate_current.accent_color"` instead of `"artifacts.base_resume.accent_color"`.

8. Do **not** change `build_session_base_resume` (explicit in-memory `base_resume` arg). Do **not** change contact/header helpers unrelated to base_resume.

## Stage 3: Config `{$BASE_RESUME}` token path audit

**Done when:** `TOKEN_SOURCES["BASE_RESUME"]` resolve path uses current-read only — via Stage 1 `format_base_resume_for_token` — with no parallel blob walk in `config.py`.

1. In `src/utils/config.py`, grep `BASE_RESUME`, `format_base_resume_for_token`, and `artifacts.base_resume` in `resolve_tokens` / `_replace`.
2. **Expected:** Stage 1 already fixes the serialize branch — **no `config.py` edit** unless grep finds a second blob read for pilot base_resume (e.g. `_walk_dot_path(candidate_data, "artifacts.base_resume")` on the BASE_RESUME spec). If found, route that branch through `format_base_resume_for_token(candidate_data)` or `load_pilot_base_resume_for_candidate` — do **not** add new config keys.
3. Do **not** change other `TOKEN_SOURCES` entries or `ARTIFACT_CONFIG`.

## Stage 4: `api_resume_html` audit (expected no-op)

**Done when:** Confirmed HTML routes delegate to rewired builder only; no independent blob assembly.

1. Read `src/ui/api/api_resume_html.py` — `resume_base` calls `build_base_resume(candidate_id)` only.
2. **No file change** unless a route reads `artifacts.base_resume` directly (grep should be clean). Document in build stub if unchanged.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Revisions

```
Revision 1 — 2026-09-03
Driven by: Joan [plan-discuss] round=1 — fix-now Stage 1 step 5 helper name typo
Changes: Stage 1 step 5 `pin_experience_job_facts_from_base` — `_candidate_id_for_current_read` → `candidate_id_for_current_read` (matches step 1 definition).
```

## Joan validate

```
[plan-discuss] round=1 concern
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1587
**Overall:** REVISE
**Publish ref:** `sub/AST-1570/AST-1587-base-resume-consumer-rewires` @ `7a1606e504caa9e88395a158278fba3a4dd2c6cf`

## Traceability
AC4→Stages1–2 (+Stages3–4 audit/no-op); AC5→Stage1:6, Stage2:3–7; parent AC1–3,5,6→N/A (AST-1586); parent AC7→AC5

## Findings

**fix-now** | Stage 1 step 5 (`pin_experience_job_facts_from_base`) | Plan calls `_candidate_id_for_current_read(candidate_data)` but Stage 1 defines `candidate_id_for_current_read` — implementer would hit `NameError`. | Replace with `candidate_id_for_current_read(candidate_data)` (or rename consistently everywhere).

context_tokens≈52000
```

### Joan validate (round 2)

```
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1587
**Overall:** APPROVED
**Publish ref:** `sub/AST-1570/AST-1587-base-resume-consumer-rewires` @ `eefcd796463eb8c7c38fc41e803b4d6945f1839e`

## Traceability
AC4→Stages1–2 (+Stages3–4 audit/no-op); AC5→Stage1:6, Stage2:3–7; parent AC1–3,5,6→N/A (AST-1586); parent AC7→AC5

## Findings
None.

context_tokens≈56000
```
