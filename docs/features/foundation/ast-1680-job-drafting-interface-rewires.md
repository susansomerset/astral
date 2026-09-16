# Job drafting interface rewires

**Linear:** [AST-1680](https://linear.app/astralcareermatch/issue/AST-1680)
**Parent:** [AST-1677](https://linear.app/astralcareermatch/issue/AST-1677) — Move candidate_data.artifacts.resume_structure to artifact table
**Publish ref:** `sub/AST-1677/AST-1680-job-drafting-interface-rewires`

Point job artifact drafting interfaces at table-backed structure: `RESUME_SECTION_CATALOG` assembly in consult, and tracker job-resume prepare/filter paths that read structure — all via hydrate then `resolve_resume_structure`, with no blob-only bypass that ignores an artifacts-table current row. Does not own catalog (AST-1678) or operative save/API (AST-1679). After #2.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/consult.py` — `build_job_token_context` / `RESUME_SECTION_CATALOG` assembly reads structure only through resolve/hydrate (no blob-only bypass).
- `src/core/tracker.py` — job resume prepare/filter paths that consult structure use the same resolve/hydrate SoT (no blob-only bypass).

Every Files Changed row and every Stage step stays inside those two files. No `candidate.py` (hydrate helper already shipped by AST-1679 — import/call only), no `agent.py`, no `api_candidate.py`, no `config.py` (including no `TOKEN_SOURCES` retype), no React, no `database.py`, no other catalog keys.

**Already on tip (do not re-invent):**

- `ARTIFACT_CONFIG["candidate.artifacts.resume_structure"]` + `BUILD_CONFIG["artifact_shapes"]["resume_structure"] == "structure_dict"` (AST-1678).
- `hydrate_operative_resume_structure_for_response(candidate_id, cd)` + `get_candidate` / `get_candidate_detail` wiring (AST-1679). Miss → leave legacy blob; hit → overlay current onto `artifacts.resume_structure` so `resolve_resume_structure(cd)` sees table SoT without a second table path inside resolve.
- `resolve_resume_structure` / `enabled_resume_structure_sections` / `filter_content_to_resume_structure` / `draft_job_resume_allowed_section_keys` — reuse; do not rewrite section contracts or move hydrate into `resolve_resume_structure` (that would be `candidate.py`, out of scope).
- Tracker `_candidate_data_for_job` already calls `get_candidate` (hydrated). This ticket still hydrates at prepare/filter entry points so a caller-passed unhydrated `candidate_data` (or a blob emptied by AST-1679 library retirement) cannot bypass table current.
- `TOKEN_SOURCES["RESUME_SECTION_CATALOG"]` remains `special_case` (ticket Notes) — do not retype.

**Operative prerequisite:** Before Stage 1 hand-verify:

```bash
python3 -c "from src.core.candidate import hydrate_operative_resume_structure_for_response, resolve_resume_structure; assert callable(hydrate_operative_resume_structure_for_response)"
```

must exit 0 (true on this tip — AST-1679 is an ancestor). If missing at **build-child** start — stop, comment on parent AST-1677 with Stage blocked (operative sibling not on tip); do **not** implement hydrate in this ticket.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | In `build_job_token_context`, hydrate structure onto a working `cd` copy when `candidate_id` is known, then assemble `RESUME_SECTION_CATALOG` from `resolve_resume_structure` / `enabled_resume_structure_sections` only | core |
| `src/core/tracker.py` | On job-resume prepare/filter paths that call `resolve_resume_structure`, hydrate structure onto a working `cd` copy when a candidate id is known (same SoT as consult) before resolve/filter | core |

**Out of this ticket (do not touch):** `src/core/candidate.py` (AST-1679); `src/core/agent.py`; `src/ui/api/api_candidate.py`; `src/utils/config.py` / `TOKEN_SOURCES`; React; `database.py`; other artifact/context leaves; `tests/` / `docs/test-bible/**`.

## Stage 1: Consult — hydrate before `RESUME_SECTION_CATALOG`

**Done when:** With a candidate that has a current `resume_structure` artifact row and an empty/missing library `artifacts.resume_structure` blob, `build_job_token_context(job, cd, candidate_id=<cid>)` returns a non-empty `RESUME_SECTION_CATALOG` whose lines match enabled sections from that current row (ids + titles + `job_agent_editable=`). Passing the same unhydrated `cd` without a usable `candidate_id` / `_astral_candidate_id` still falls through existing `resolve_resume_structure` behavior (legacy blob or default) — no new coat-check. `TOKEN_SOURCES["RESUME_SECTION_CATALOG"]` unchanged.

1. In `src/core/consult.py` `build_job_token_context`, extend the existing lazy import from `src.core.candidate` to also import `hydrate_operative_resume_structure_for_response` (keep `enabled_resume_structure_sections` and `resolve_resume_structure`).

2. Immediately after the existing block that sets `cd = dict(candidate_data or {})`, resolves `cid` from `candidate_id` / `_astral_candidate_id`, and stamps `cd["_astral_candidate_id"]` when `cid` is truthy — and **before** any `resolve_resume_structure(cd)` call — when `cid` is truthy, call:

```python
    # AST-1680: table-backed structure SoT for job drafting tokens (no blob-only bypass).
    hydrate_operative_resume_structure_for_response(cid, cd)
```

Do **not** mutate the caller’s original `candidate_data` dict beyond the existing `cd = dict(...)` copy. Do **not** call `get_candidate` from consult (would pull unrelated leaves / widen scope). Do **not** read `artifacts.resume_structure` directly for catalog lines — keep the existing `resolve_resume_structure` + `enabled_resume_structure_sections` loop unchanged after hydrate.

3. Leave the rest of `build_job_token_context` (VISIBLE_JD, analysis phases, catalog line format) unchanged. Do not edit other functions in `consult.py` on this ticket.

⚠️ **Decision:** Hydrate-then-resolve at the consumer, not a current-read fork inside catalog assembly — matches AST-1679’s contract that `resolve_resume_structure` stays honest against hydrated/current overlay and keeps this ticket inside `consult.py` / `tracker.py` only.

## Stage 2: Tracker — hydrate before prepare / structure filter

**Done when:** With only an artifacts-table current structure (library blob empty/missing), `_prepare_job_resume_content` filters/merges using enabled sections from that current (not an empty/default catalog that ignores the row); `persist_job_artifact_from_parsed`’s resume branch and the other in-file `resolve_resume_structure` call sites listed below likewise see hydrated structure when a candidate id is available. No new blob-only `artifacts["resume_structure"]` reads are introduced.

1. In `src/core/tracker.py` `_prepare_job_resume_content`, at the top of the function **before** `resolve_resume_structure`, work on a shallow copy and hydrate when an id is present:

```python
    cd = dict(candidate_data) if isinstance(candidate_data, dict) else {}
    cid = candidate_mod.candidate_id_for_current_read(cd)
    if cid:
        # AST-1680: same hydrate→resolve SoT as consult job drafting tokens.
        candidate_mod.hydrate_operative_resume_structure_for_response(cid, cd)
    structure = candidate_mod.resolve_resume_structure(cd)
```

Use `cd` (not the original `candidate_data`) for the rest of this function’s structure / `draft_job_resume_allowed_section_keys` / artifacts reads that already go through this parameter. Do **not** retarget the contact `base_resume` snapshot block to current-read (base_resume consumer rewires are prior epics; out of structure scope).

2. Apply the same hydrate-before-resolve pattern (copy → `candidate_id_for_current_read` → hydrate when cid → `resolve_resume_structure`) at every other `resolve_resume_structure` call site in `tracker.py` that feeds job-resume prepare/filter / enabled-section checks:

- `parsed_matches_resume_content_shape`
- `parsed_matches_job_resume_content` (after `_candidate_data_for_job`; hydrate is idempotent if `get_candidate` already overlaid)
- `job_has_persisted_resume_body` (same)
- `persist_job_artifact_from_parsed` resume branch (the `resolve_resume_structure` + `filter_content_to_resume_structure` pair)

Do **not** add hydrate to unrelated tracker paths (cover letter, job current-read for `job_resume` body, etc.). Do **not** invent a tracker-local structure loader that bypasses `hydrate_operative_resume_structure_for_response`.

3. Do **not** change `_candidate_data_for_job`’s use of `get_candidate` (already hydrates via AST-1679). Defense-in-depth at the resolve sites above is required so prepare/filter cannot ignore table current when handed a raw/unhydrated dict.

⚠️ **Decision:** Duplicate hydrate calls at each resolve site rather than a new tracker helper module — keeps the change local, grep-visible as AST-1680, and avoids a third file. Idempotent with `get_candidate` hydrate.

## Estimate

Confirm Chuckles estimate: 3 — agree
