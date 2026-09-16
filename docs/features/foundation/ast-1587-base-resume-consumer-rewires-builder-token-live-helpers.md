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

## Review (build stub)

**Built:** `origin/sub/AST-1570/AST-1587-base-resume-consumer-rewires` @ `c53c8ab7`.

**Stages delivered:**
- Prerequisite: merged `origin/sub/AST-1570/AST-1586-current-read-helper-get-hydrate-pattern-revise` — `1176722f`.
- Stage 1: candidate live helpers + `candidate_id_for_current_read` / `load_pilot_base_resume_for_candidate` — `2117c638`.
- Stage 2: builder consumer rewires + Style D current-read in `build_base_resume` — `c53c8ab7`.
- Stage 3: config `{$BASE_RESUME}` audit — no change (`format_base_resume_for_token` covers serialize branch).
- Stage 4: `api_resume_html` audit — no change (thin `build_base_resume` caller only).

**Betty:** at **Code Complete** — builder/candidate current-read consumer coverage; whitelist debug label; `build_base_resume` Style D 2/2 headers.

## Radia review

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1587
**Publish ref:** `sub/AST-1570/AST-1587-base-resume-consumer-rewires` @ `f217d33cc373d0408ce1a5934647264c304ffda8`
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.config.config-source-of-truth` | scoped | conforms | consumers resolve via `ARTIFACT_CONFIG` / `get_candidate_current`; no config scrape |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single `ast-1587-*.md` issue doc |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | engineer commits: `candidate.py` + `builder.py` only |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | core→data/utils only |
| `astral.layers.import-direction` | scoped | conforms | allowed import directions |
| `astral.idioms.coat-check-never-store-empty` | scoped | conforms | miss→empty; no blob recovery on consumer paths |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | no new data-layer logging |
| `astral.standards.debug-contract-gated` | scoped | conforms | `build_base_resume` Style D: `index 1/2` found+`current_read=` before ingest; `index 2/2` recorded |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | `candidate_id_for_current_read` + `load_pilot_base_resume_for_candidate` centralize pilot reads |
| `astral.standards.in-scope-only` | scoped | conforms | 1587 product footprint = builder + candidate live helpers |
| `astral.standards.logging-via-utils` | scoped | conforms | debug via `_log.debug_*` helpers |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | semantic runtime names |
| `astral.standards.no-cross-contamination` | scoped | conforms | read-operative pin path untouched |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | pilot key constant; catalog-backed resolution |
| `astral.standards.public-then-helpers` | scoped | conforms | new public helpers before rewired consumers |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | merge-tests on publish tip |
| `orch.git.commit-vocabulary` | universal | conforms | commit messages on-pattern |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub under AST-1570 parent |
| `orch.git.ftr-sub-topology` | universal | conforms | child publish ref topology |
| `orch.git.merge-on-checkout` | universal | conforms | reviewed vs `origin/dev` |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no forbidden git ops |
| `orch.git.no-dev-agent-branches` | universal | conforms | engineer sub branch |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1570 worktree |
| `orch.git.three-permanent-branches` | universal | conforms | baseline `origin/dev` |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | miss→empty contracts per plan |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–4 + prerequisite delivered |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | reviewed at Tests Passed |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test-bible + component tests match manifest |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Hedy assignee; tight product scope |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no hook-ban violations |

**Sweep count:** 65 active statutes scored (18 universal + 47 scoped).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `patt.artifact.read-current` | conforms | In-scope builder/token/structure consumers delegate to `get_candidate_current` via `load_pilot_base_resume_for_candidate`; miss→empty; no blob fallback; Style D on `build_base_resume` current-resolve |

## Plan adherence

- **Prerequisite:** `merge-resume(AST-1587): attach AST-1586` (`1176722f`) — `get_candidate_current` + hydrate present before consumer rewires.
- **Stage 1:** `candidate_id_for_current_read`, `load_pilot_base_resume_for_candidate`, rewired `format_base_resume_for_token`, `resolve_resume_structure`, `draft_job_resume_allowed_section_keys`, `pin_experience_job_facts_from_base`, whitelist debug label — all match plan.
- **Stage 2:** `_coerce_candidate_blob` stamps `_astral_candidate_id`; builder paths use current-read; Style D 2/2 headers.
- **Stage 3:** `config.py` audit — **no change**; `{$BASE_RESUME}` serialize branch routes through `format_base_resume_for_token`.
- **Stage 4:** `api_resume_html.py` audit — **no change**; thin `build_base_resume` caller only.

**Joan:** APPROVED (round 2).

## Findings

None (no fix-now, discuss, or advisory items requiring engineer action).

## What's solid

- Grep confirms **zero** `artifacts.get("base_resume")` reads remain in `builder.py` or the four Stage-1 candidate functions.
- `format_base_resume_for_token` ignores stale blobs when operative row absent; reads table current on hit.
- Betty harness: `operative_fixture` + autouse `load_pilot` stub preserves existing builder tests while proving current-read semantics.

context_tokens≈52000

## Bug: AST-1682 — {$BASE_RESUME} reads current base_resume artifact (blank token fix)

Orphaned bug mini-parent: [AST-1681](https://linear.app/astralcareermatch/issue/AST-1681). Approved ancestor: this AST-1587 doc (Susan). Publish ref: `sub/AST-1681/AST-1682-base-resume-token-reads-current`.

**Canon (from AST-1587 Citations; parent has no separate Canon Scope):** `patt.artifact.read-current` (pattern — token/prompt assembly must current-read when cid is known); `patt.artifact.write-operative` (id-only); `astral.standards.debug-contract-gated` (id-only); `astral.standards.in-scope-only` (id-only); `astral.layers.import-direction` (id-only).

### As-is

When a prompt containing `{$BASE_RESUME}` is resolved, the substituted value is empty even when the candidate has a current `candidate.artifacts.base_resume` operative artifact that should ground the token.

### To-be

`{$BASE_RESUME}` resolves to the section-id-keyed JSON body of the candidate’s current `candidate.artifacts.base_resume` operative artifact (AST-607 / AST-1587 contract), not blank, whenever that current row exists and the token view carries a candidate id (or an equivalent in-scope path can stamp that id before serialize).

### Repro

No SQL seed — persistence is file/JSON. Fixture-level:

1. Ensure candidate `cand-1` has a non-empty current operative body for `candidate.artifacts.base_resume` (section-id-keyed dict as written by craft/save-operative).
2. Build a **library-shaped** dict with no cid stamp — the shape Contact passes into `do_task` today:

```python
candidate_data = {
    "contact": {"phone": "555"},
    "context": {},
    "artifacts": {},  # blob retired / stripped; do not rely on it
}
```

3. Resolve a prompt that embeds the token **without** threading cid on the view:

```python
from src.utils.config import resolve_tokens
# Mirrors Contact: candidate_data=…, no ctx.astral_candidate_id, index may be cand-1
out = resolve_tokens("X{$BASE_RESUME}Y", candidate_data, "contact_estelle_turn")
assert out == "XY"  # blank today
```

4. Same serialize with cid present must be non-empty JSON (control):

```python
from src.core.candidate import format_base_resume_for_token
assert format_base_resume_for_token({**candidate_data, "_astral_candidate_id": "cand-1"}) != ""
```

5. Live path: `do_task(..., candidate_data=candidate_data, index="cand-1", ctx=None)` (Contact Estelle shape) with a prompt containing `{$BASE_RESUME}` — model input shows blank where resume JSON should be.

### Root cause

AST-1587 correctly rewired `format_base_resume_for_token` to **current-read only** via `candidate_id_for_current_read` → `get_candidate_current` (no `artifacts.base_resume` blob fallback). Blank is therefore expected when cid is missing — but several resolve paths still hand `resolve_tokens` a candidate-shaped dict **without** `_astral_candidate_id` / `astral_candidate_id` even though an astral candidate is in scope:

1. **`is_candidate_token_view`** returns True for raw library `candidate_data` because it has a top-level `"contact"` key — so `_token_view_for_do_task` treats that blob as a finished token view and returns it unchanged (no cid).
2. **Contact Estelle** (`src/core/contact.py`) calls `do_task(..., candidate_data=…, index=astral_candidate_id or channel)` **without** `ctx` / without stamping `_astral_candidate_id`. It may strip or pin `artifacts.base_resume`, but serialize ignores that blob anyway — so pin-into-blob cannot rescue `{$BASE_RESUME}` after AST-1587.
3. Path-walk tokens (`{$FIRST_NAME}`, `{$STRENGTHS}` via `context.*` hydrate/legacy) can still look fine on the same turn, which makes the blank `{$BASE_RESUME}` look like a serialize bug rather than a missing-id bug.

`config.py`’s `resume_sections_json` branch already calls `format_base_resume_for_token(candidate_data)` — the defect is upstream of that call (cid not on the dict), not a second blob walk in config.

### Proposed change

Scope = this child’s `## Scope` (copied from AST-1681 Component/Technical scope). Do **not** revive blob fallback. Do **not** own Contact pin resolve beyond threading cid for current-read.

1. **`src/core/candidate.py` — tighten `is_candidate_token_view`**
   - Require `"_astral_candidate_id" in obj` (key present; value may still be empty) so a raw library blob with only `contact` / `context` / `artifacts` is **not** classified as a token view.
   - Leave `format_base_resume_for_token` / `candidate_id_for_current_read` / `load_pilot_base_resume_for_candidate` on the no-blob-fallback contract (miss or missing cid → `""`).

2. **`src/core/agent.py` — `_token_view_for_do_task` / `do_task` (token-view builder)**
   - Pass `index` into `_token_view_for_do_task`.
   - Resolve walkable cd in this order:
     1. `ctx.astral_candidate_id` → `get_candidate` → `build_candidate_token_view` (unchanged)
     2. `ctx` is a candidate row → `build_candidate_token_view` (unchanged)
     3. **New:** if `index` is non-empty and `get_candidate(index)` returns a row, use `build_candidate_token_view(row)` — covers callers that pass `index=<astral_candidate_id>` without `ctx` (Contact Estelle when a candidate is bound)
     4. `is_candidate_token_view(candidate_data)` → `dict(candidate_data)` (now requires cid key)
     5. Fallback `dict(candidate_data or ctx.candidate_data or {})` (unchanged)
   - Keep the existing post-view stamp: when `ctx.astral_candidate_id` is set, set `cd["_astral_candidate_id"]`.
   - Do **not** treat arbitrary batch/job indexes as candidates when `get_candidate` misses — fall through.

3. **`src/utils/config.py` — audit only**
   - Confirm `TOKEN_SOURCES["BASE_RESUME"]` with `serialize == "resume_sections_json"` remains the only resolve branch and still calls `format_base_resume_for_token(candidate_data)`.
   - **Expected: no file change.** If a parallel `_walk_dot_path(..., "artifacts.base_resume")` for this token exists, route it through `format_base_resume_for_token` instead (do not add keys).

4. **Contact pin block**
   - Leave strip/pin-into-`artifacts.base_resume` logic untouched (Boundaries: not owning pin paths). Step 2 makes `index=astral_candidate_id` sufficient for current-read serialize.
   - If make-fix finds a resolve site that has **neither** ctx cid, **nor** index-as-cid, **nor** a stamped view, stop with `[scope-gate]` naming that file — do not widen silently.

5. **Verify**
   - With current operative present + cid-bearing view (or Contact-shaped `index=cid`, `ctx=None`): `{$BASE_RESUME}` → non-empty section-id JSON.
   - Missing current or missing cid (and index not a candidate id): still `""`.

### Blast radius

- **Contact Estelle turns** that embed `{$BASE_RESUME}` — primary live beneficiary; pin-into-blob no longer needed for this token once cid/index recovery works.
- **Any `do_task` caller** that passes library `candidate_data` without ctx but uses `index=<astral_candidate_id>` — gains current-read serialize.
- **Admin / `preview_task_prompt` / `build_candidate_token_view` paths** that already stamp `_astral_candidate_id` — should already current-read; regression-check only.
- **Sibling artifact tokens** (`STRENGTHS`, etc.) stay on path-walk + hydrate; unchanged.
- **AST-1587 builder HTML / live helpers** — unchanged unless they share `is_candidate_token_view` (tighten may push more callers through `get_candidate` when index/ctx provide an id — desired).

### What must still hold

- AST-1587 / this child’s AC2: missing operative current **or** missing candidate id → empty string; **no** `artifacts.base_resume` blob fallback.
- AST-607 serialize contract: section-id-keyed JSON (via `ingest_legacy_label_content_base_resume` + `filter_base_resume_to_structure`), never markdown.
- `TOKEN_SOURCES` / `ARTIFACT_CONFIG` membership unchanged.
- Contact read-operative **pin** behavior for non-token consumers unchanged (this bug’s to-be is **current**, not pin).
- Engineer must not create or edit `tests/` or `docs/test-bible/**`.

## Radia review-fix — AST-1682

[code-rubric]
**Ticket:** AST-1682
**Publish ref:** `sub/AST-1681/AST-1682-base-resume-token-reads-current` @ `f40d9e502690d8fa441da69c24e9200061a5efe5`
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Overall:** CLEAN

**Parent shape:** Orphaned mini-parent AST-1681 — Chuckles merge target is `origin/dev` (finish-up-style), not `merge-child`/`prep-uat`.

**Diff base:** `origin/ftr/AST-1681-base-resume-does-not-read-current-artifact...origin/sub/AST-1681/AST-1682-base-resume-token-reads-current` (3 files: plan-fix doc append, `src/core/agent.py`, `src/core/candidate.py`).

## Canon scores

| id | grade | effort | one-line |
|----|-------|--------|----------|
| patt.artifact.read-current | A | | index-as-cid path loads `build_candidate_token_view` → `format_base_resume_for_token` current-read; no blob fallback introduced |
| patt.artifact.write-operative | X | | no write paths touched |
| astral.standards.debug-contract-gated | X | | no debug contract changes |
| astral.standards.in-scope-only | A | | product footprint = `agent.py` + `candidate.py` only, matching plan-fix steps 1–2; `config.py` audit-only (no edit) |
| astral.layers.import-direction | A | | existing lazy `candidate` import inside `_token_view_for_do_task`; no new cross-layer violations |

## Column diff vs plan stage

no plan-stage scores attached (fix-board `[board-joan] CANON: OK` only; no `validate-plan` artifact on AST-1682 bug section)

## Frame diff

(none)

## Fix-specific checks

**[bug-repro]** — not on AST-1682 publish ref (board `TESTS: REVISE` routed repro to sibling **AST-1683** @ Tests Ready). Sibling repro on `origin/sub/AST-1681/AST-1683-cover-contact-base-resume-current-read` @ `af453c56`: **OK** — `TestAst1683ContactBaseResumeCurrentRead::test_do_task_index_cid_ctx_none_resolves_base_resume` exercises Contact Estelle shape (`library_blob` without `_astral_candidate_id`, `index=cid`, `ctx=None`), registers operative body, asserts resolved prompt contains operative summary text and `!= "XY"` (pre-fix blank). Concrete To-be pinning; would fail pre-fix (`is_candidate_token_view` True on bare `contact` key).

**## What must still hold — OK**

1. **No blob fallback / miss→empty** — `format_base_resume_for_token` unchanged (current-read only via `candidate_id_for_current_read`); `is_candidate_token_view` now requires `_astral_candidate_id` key so raw library blobs are not mistaken for finished views; index recovery only when `get_candidate(index)` hits, else fall-through unchanged.
2. **AST-607 JSON serialize** — unchanged `ingest_legacy_label_content_base_resume` + `filter_base_resume_to_structure` path.
3. **TOKEN_SOURCES / ARTIFACT_CONFIG** — `config.py` untouched; `resume_sections_json` → `format_base_resume_for_token` branch intact.
4. **Contact pin** — `contact.py` untouched.
5. **Engineer test-tree ban on AST-1682** — no `tests/` or test-bible edits on this publish ref (repro correctly on AST-1683 sibling).

## Findings

None (no fix-now, discuss, or advisory items on AST-1682 product diff).

## What's solid

- Plan-fix steps 1–2 delivered exactly: `is_candidate_token_view` tightened; `_token_view_for_do_task` accepts `index`, inserts Contact-style `get_candidate(index)` → `build_candidate_token_view` before the token-view shortcut.
- Ordering respects plan: arbitrary non-candidate indexes fall through on `get_candidate` miss (no false candidate binding).
- `do_task` call site threads `index=index` — single integration point.

## Chuckles branching

| Gate | Action |
|------|--------|
| **PROCEED** + orphaned parent | → **Review Posted** → skip `resolve-child` → merge `sub/AST-1681/AST-1682-base-resume-token-reads-current` straight to **`origin/dev`** |
| AST-1683 | separate lane — repro test OK qualitatively; still **Tests Ready** on its own branch |

```
[code-rubric] PROCEED (Commit: f40d9e50) cid threading clean
```
