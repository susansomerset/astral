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

## Joan validate

```
[plan-rubric]
**Ticket:** AST-1680
**Overall:** APPROVED
**Corpus:** fc0c368e59 · ticket ids partially outside clerk roster (draft pattern + statute paths resolved from worktree)
**Publish ref:** sub/AST-1677/AST-1680-job-drafting-interface-rewires @ 3a5df9b00a7192d4dcfaa125840e50edc1501596

## Canon scores

patt.artifact.read-current | A | | Stage 1–2 hydrate→resolve at consult + tracker consumers; get_candidate_current via AST-1679 helper; no blob-only bypass when cid known
astral.standards.in-scope-only | A | | consult.py + tracker.py only; explicit fence; import/call hydrate only, no candidate.py edits
astral.config.config-source-of-truth | A | | TOKEN_SOURCES unchanged; structure via config-backed resolve/enabled sections; no scattered literals

## Traceability

AC7→Stage 1 (build_job_token_context RESUME_SECTION_CATALOG) + Stage 2 (_prepare_job_resume_content, parsed_matches_*, job_has_persisted_resume_body, persist_job_artifact_from_parsed) | Parent functional scope §6 + parent AC7; parent AC1–6 N/A (AST-1678/1679); parent AC8–9 N/A

## Findings

### acceptable — _prepare_job_resume_content follow-through
- **Location:** Stage 2 §1 snippet vs prose
- **Finding:** Snippet hydrates `cd` before `resolve_resume_structure` but does not show retargeting `draft_job_resume_allowed_section_keys(candidate_data)` → `(cd)` or `artifacts` reads to `cd`.
- **Recommendation:** No plan revision required — prose explicitly requires `cd` for remainder of function; engineer must apply beyond the snippet.

### acceptable — canon infrastructure
- **Location:** canon_clerk roster
- **Finding:** `patt.artifact.read-current` not in active clerk roster; logging/statute paths resolved from worktree.
- **Recommendation:** No plan change.

context_tokens≈52000
```

## Review (build stub)

**Built:** `origin/sub/AST-1677/AST-1680-job-drafting-interface-rewires` @ `7dbc595ad287f583409b9af3c4ba19f1463f6526`.

**Stages delivered:**
- Stage 1: consult hydrate before `RESUME_SECTION_CATALOG` — `1512385639586e6c9eb2713c19adb4f7b955d247`.
- Stage 2: tracker hydrate before prepare/filter resolve sites — `7dbc595ad287f583409b9af3c4ba19f1463f6526`.

**Betty:** at **Code Complete** — cover table-only structure (legacy blob empty/missing) still yields non-empty `RESUME_SECTION_CATALOG` from `build_job_token_context`; `_prepare_job_resume_content` / persist filter use hydrated enabled sections; no blob-only bypass when cid known; `TOKEN_SOURCES["RESUME_SECTION_CATALOG"]` stays `special_case`.

## Radia review

```
[code-rubric]
**Ticket:** AST-1680
**Publish ref:** 44af3439cbf491c3c4d7881af4068880bcaa27be
**Corpus:** fc0c368e59 · `patt.artifact.read-current` not in `canon_clerk` active roster (resolved from `canon/directives/draft/patt.artifact.read-current.md` + statute paths)
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.read-current | A | | |
| astral.standards.in-scope-only | A | | |
| astral.config.config-source-of-truth | A | | |

## Column diff vs plan stage

(aligned)

## Frame diff

(none)

## Findings

### advisory

- **Location:** `origin/dev...publish-ref` cumulative diff
- **Finding:** Three-dot diff includes AST-1678/AST-1679 ancestor commits (`config.py`, `candidate.py`, `api_candidate.py`, etc.). AST-1680 code commits (`15123856`, `7dbc595a`) touch only `src/core/consult.py` and `src/core/tracker.py`.
- **Recommendation:** Expected epic branch union; no AST-1680 action.

- **Location:** `tests/component/core/test_tracker.py::TestAst1680JobResumeHydrateBeforeResolve`
- **Finding:** Betty gates `_prepare_job_resume_content` and `parsed_matches_resume_content_shape`; `parsed_matches_job_resume_content`, `job_has_persisted_resume_body`, and `persist_job_artifact_from_parsed` receive the same hydrate→resolve pattern but lack dedicated AST-1680 table-only tests.
- **Recommendation:** Acceptable for this ticket — pattern is identical and idempotent with `get_candidate` hydrate; optional hardening in a future test pass if desired (not fix-now).

- **Location:** `canon/canon_clerk.py expand`
- **Finding:** `patt.artifact.read-current` fails clerk expand; scoring used draft pattern body.
- **Recommendation:** Infrastructure track only — out of AST-1680 scope.

## What's solid

- **Consult (AC7 / Stage 1):** `build_job_token_context` imports `hydrate_operative_resume_structure_for_response`, hydrates working `cd` copy when `cid` is truthy, then assembles `RESUME_SECTION_CATALOG` via existing `resolve_resume_structure` + `enabled_resume_structure_sections` loop. Caller dict not mutated beyond pre-existing shallow copy.
- **Tracker (AC7 / Stage 2):** Hydrate→resolve at all five planned sites: `_prepare_job_resume_content` (with `cd` retargeted for `draft_job_resume_allowed_section_keys` and `artifacts` reads per Joan follow-through), `parsed_matches_resume_content_shape`, `parsed_matches_job_resume_content`, `job_has_persisted_resume_body`, `persist_job_artifact_from_parsed` resume branch.
- **No blob-only bypass:** `TestAst1680JobDraftingHydrateCatalog::test_catalog_from_table_current_when_blob_empty` and `TestAst1680JobResumeHydrateBeforeResolve::test_prepare_uses_table_current_when_blob_empty` prove table current drives catalog/filter when library blob is empty.
- **Legacy path preserved:** Without `candidate_id` / `_astral_candidate_id`, hydrate is skipped and blob/default resolve still works (`test_without_candidate_id_skips_hydrate_*`, `test_prepare_without_cid_skips_hydrate`).
- **Config SoT:** `TOKEN_SOURCES["RESUME_SECTION_CATALOG"]` remains `special_case` (`test_resume_section_catalog_token_stays_special_case`); no new inline section sets or magic literals.
- **Scope:** No edits to `candidate.py`, `config.py`, API, or React on AST-1680 commits.

## Recommended actions (for Chuckles — not Radia)

1. Post slim upshot and advance to **Review Posted** — operative prerequisite (AST-1679 hydrate helper) is on branch ancestor; drafting rewire slice is complete.
2. No `resolve-child` product work indicated from canon pass.

context_tokens≈35000
```
