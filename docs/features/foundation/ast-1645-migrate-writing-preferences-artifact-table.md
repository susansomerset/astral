<!-- linear-archive: AST-1645 archived 2026-09-24 -->

## Linear archive (AST-1645)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1645/migrate-candidate-datacontextwriting-preferences-to-use-the-artifact  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / 5  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1572

### Description

## Purpose

Follow-on sibling to [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) (Strengths migration). `candidate_data.context.writing_preferences` is still a plain library blob: no versioning, no `current` row, no pin, and `{$WRITING_PREFERENCES}` resolves as a `data_field`. AST-1629 proved the artifact table + `ARTIFACT_CONFIG` path, plus the `plain_text` body shape, for Strengths. This ticket migrates **Writing Preferences only** onto that same proven path — copy the pattern, do not rederive a second special case.

## Functional scope

1. **Catalog Writing Preferences** — Register `candidate.context.writing_preferences` in `ARTIFACT_CONFIG`, reusing the `plain_text` body shape added in AST-1629. No other context or artifact keys are added.
2. **Operative write** — Saving Writing Preferences goes through candidate write-operative (`save_candidate_data` → `database.save_artifact`). No in-place blob UPDATE.
3. **Current read / hydrate** — GET/UI loads Writing Preferences via read-current and overlays the string onto `candidate_data.context.writing_preferences` for the existing editor contract. Miss → empty editor.
4. **Retire blob authority** — Stop durable library-merge writes of `context.writing_preferences` as source of truth; stop token/live assembly from reading the blob for Writing Preferences after cutover.
5. **Token typing** — Flip `TOKEN_SOURCES["WRITING_PREFERENCES"]` from `data_field` to `artifact` with `artifact_key: "candidate.context.writing_preferences"`.
6. **UI path** — Keep Writing Preferences on `ContextTextPage`, the shared plain-text artifact editor from AST-1629. Do not extend `ArtifactEditor` / `resume_content` for this leaf.
7. **No legacy backfill** — Do not migrate historical `context.writing_preferences` blobs. Existing text stays in the blob until the operator re-saves through the new path; first operative save creates the artifact row.
8. **Explicit non-goals** — No coat-check. No new craft task. No job/company catalog keys. No other context leaves (priorities, deal_breakers, ideal_day, backstory).

## Component scope

* `src/utils/config.py` — **modified** — `ARTIFACT_CONFIG["candidate.context.writing_preferences"]` plus asserts; reuses existing `BUILD_CONFIG["artifact_shapes"]["plain_text"]` raw-string contract from AST-1629; `TOKEN_SOURCES["WRITING_PREFERENCES"]` becomes `artifact` plus `artifact_key`.
* `src/core/candidate.py` — **modified** — operative save validation for `plain_text` (reused path); hydrate Writing Preferences from `get_candidate_current` on GET paths; gate durable library writes for `context.writing_preferences`.
* `src/ui/api/api_candidate.py` — **modified** — PUT intercept: strip library `context.writing_preferences`, call operative save; GET hydrate overlays current Writing Preferences string.
* `src/ui/frontend/src/pages/CandidateWritingPreferences.tsx` — **modified** — Writing Preferences-only; stay on ContextTextPage path.
* `src/ui/frontend/src/components/ContextTextPage.tsx` — **untouched** — shared plain-text artifact editor already parameterized by AST-1629; Writing Preferences is a new consumer, not a new wiring change.
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — **untouched**.
* `src/data/database.py` — **untouched** — existing `save_artifact` / `get_current_artifact` primitives only.

## Technical scope

* `src/utils/config.py` — Catalog entry: `entity_type: "candidate"`, `candidate_scoped: True`, `body_shape: "plain_text"`, `ingestion_owner: "candidate"`. Closed-set asserts include the new key; Writing Preferences leaves the sibling-freeze-out list. `TOKEN_SOURCES["WRITING_PREFERENCES"]` gains `source_type: "artifact"` and `artifact_key: "candidate.context.writing_preferences"`.
* `src/core/candidate.py` — Operative str-path validates `plain_text` (reuses AST-1629 validation, no new rules); hydrate overlay writes current string into `context.writing_preferences` for display; refuse durable library SoT write for that leaf when catalog owns it.
* `src/ui/api/api_candidate.py` — On PUT with Writing Preferences: pop from library `context` merge, `save_candidate_data(candidate_id, "candidate.context.writing_preferences", body)`; on GET hydrate current row into `context.writing_preferences`.
* `src/ui/frontend/src/pages/CandidateWritingPreferences.tsx` — Load/save only through the operative API contract via existing `ContextTextPage`; no parallel client storage key; no ArtifactEditor.

## Architectural definition

**Patterns to reuse** (all established by AST-1629 — no new patterns proposed):

* `patt.artifact.manage-catalog` — register Writing Preferences; retire blob authority for that key. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* `patt.artifact.write-operative` — Writing Preferences saves via blind retire+insert through entity-owned operative save. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>)
* `patt.artifact.read-current` — UI/GET hydrate and live Writing Preferences from current row. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>)
* `patt.artifact.read-operative` — pin to body remains available via generic path (no Writing Preferences-only pin surface required). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-operative.md>)
* `patt.artifact.ui-consistency` — editor path follows catalog `body_shape` (`plain_text` → ContextTextPage, not resume_content ArtifactEditor). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.ui-consistency.md>)

**New patterns proposed:** none — Writing Preferences reuses the `plain_text` shape and all patterns as-is; this is config catalog data under manage-catalog, not a new pattern id.

**Applicable statutes** (same set as AST-1629):

* `stat.logging.info` — info contracts on touched surfaces. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md>)
* `stat.logging.warning` — warning contracts on touched surfaces. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>)
* `stat.logging.error` — error contracts on touched surfaces. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>)
* `stat.logging.debug` — debug contract on any `debug=` surfaces this epic touches. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)
* `stat.logging.info.entity` — entity/core info logging when candidate paths change. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>)
* `stat.logging.info.api` — API info logging when api_candidate Writing Preferences paths change. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>)
* `astral.config.config-source-of-truth` — catalog key, body_shape, and token typing live in config. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.standards.no-hardcoded-sets` — closed catalog / shape membership via config asserts. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
* `astral.standards.in-scope-only` — Writing Preferences only. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* `astral.layers.import-direction` — utils/config + core + ui layering. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
* `astral.git.engineer-test-tree-ban` — engineers do not own `tests/` / bible. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md>)
* `astral.standards.logging-via-utils` — logging through utils helpers. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md>)

Note: Artifact `patt.artifact.*` ids remain under `draft/` until promoted (same as AST-1629); logging `stat.logging.*` are active. Comply with every active directive that applies to touched surfaces.

## Acceptance criteria

1. **Catalog key present** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.writing_preferences' in ARTIFACT_CONFIG"` exits 0. Fail: key absent or differently named without Description amendment.
2. **plain_text shape reused** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert ARTIFACT_CONFIG['candidate.context.writing_preferences']['body_shape']=='plain_text'"` exits 0. Fail: Writing Preferences bound to `resume_content` / `cover_letter`, or a new shape added.
3. **Token is artifact-typed** — `python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['WRITING_PREFERENCES']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.writing_preferences'"` exits 0. Fail: still `data_field` or wrong `artifact_key`.
4. **Operative round-trip** — Save Writing Preferences via Writing Preferences UI/API; `database.get_current_artifact('candidate', <id>, 'writing_preferences')` returns a row whose `artifact_data` matches the saved string; a second save creates a new uuid and retires prior `current=1`. Fail: body only in library blob with no artifact row, or in-place UPDATE of same uuid.
5. **Blob not SoT on write** — Successful Writing Preferences save calls operative `save_artifact`; does not rely on library-merge of `context.writing_preferences` alone. Fail: PUT only deep-merges the blob.
6. **Editor reload** — Writing Preferences page after save shows the same text. Fail: empty editor while a current artifact row exists.
7. **No backfill required** — Candidates with only legacy blob Writing Preferences and no artifact row still load that blob (or empty) until re-save; no bulk migration job ships. Fail: epic adds a required one-shot migrate-all script as SoT.
8. **Sibling freeze** — `ARTIFACT_CONFIG` has no priorities/deal_breakers/ideal_day/backstory keys. Fail: any of those registered.
9. **UI path** — Writing Preferences still uses ContextTextPage (or a thin wrapper of it); `ArtifactEditor` diff for this ticket is empty. Fail: Writing Preferences routed through ArtifactEditor / resume_content.

## Open questions

none

## Proposed child tickets

#### 1!!: **Catalog + plain_text shape reuse + WRITING_PREFERENCES token - Ada**

Register `candidate.context.writing_preferences` in `ARTIFACT_CONFIG` reusing the existing `plain_text` shape, flip `TOKEN_SOURCES["WRITING_PREFERENCES"]` to artifact plus `artifact_key`, lock startup asserts (add key to closed set; remove from sibling-freeze-out list). Does not own UI or hydrate.
**Citations:** `patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `stat.logging.info` / `stat.logging.debug` as touched
**Scope:** `src/utils/config.py` — new catalog entry plus asserts; `TOKEN_SOURCES["WRITING_PREFERENCES"]` flip.
**Estimate: 1**

#### 2!: **Operative save, hydrate, blob retirement - Hedy**

Wire Writing Preferences through candidate operative `plain_text` validation plus `get_candidate_current` hydrate on GET; intercept API PUT for operative save; stop durable library SoT writes for `context.writing_preferences`. No backfill helper. Does not own React chrome. After #1.
**Citations:** `patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.in-scope-only`; `stat.logging.info.entity`; `stat.logging.info.api`; `stat.logging.error`
**Scope:** `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.writing_preferences`. `src/ui/api/api_candidate.py` — PUT intercept plus GET hydrate for Writing Preferences.
**Estimate: 3**

#### 3: **Writing Preferences ContextTextPage wire-up - Katherine**

Retarget Writing Preferences-only UI load/save to the operative API contract via existing `ContextTextPage`. No ArtifactEditor. No sibling context pages. After #1 (and API hydrate from #2 as needed).
**Citations:** `patt.artifact.ui-consistency`; `patt.artifact.read-current`; `patt.artifact.write-operative`
**Scope:** `src/ui/frontend/src/pages/CandidateWritingPreferences.tsx` — Writing Preferences-only wire-up against existing ContextTextPage.
**Estimate: 2**

Monolith check: 8 functional capabilities into 3 children (config / core+API / UI), matching AST-1629's split.

Scope partition check: `config.py` → #1; `candidate.py` + `api_candidate.py` → #2; `CandidateWritingPreferences.tsx` → #3. `ArtifactEditor.tsx`, `database.py`, and `ContextTextPage.tsx` untouched / unclaimed by design.

---

## Original brief

Follow-on sibling to [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) (Strengths migration). `candidate_data.context.writing_preferences` is still a plain library blob: no versioning, no `current` row, no pin, and `{$WRITING_PREFERENCES}` resolves as a `data_field`. [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) proved the artifact table + `ARTIFACT_CONFIG` path, plus the `plain_text` body shape, for Strengths. This ticket migrates **Writing Preferences only** onto that same proven path.

### Functional scope (Archie)

1. **Catalog Writing Preferences** — Register `candidate.context.writing_preferences` in `ARTIFACT_CONFIG`, reusing the `plain_text` body shape added in AST-1629. No other context or artifact keys are added.
2. **Operative write** — Saving Writing Preferences goes through candidate write-operative (`save_candidate_data(candidate_id, artifact_key, body)` → `database.save_artifact`). No in-place blob UPDATE.
3. **Current read / hydrate** — GET/UI loads Writing Preferences via read-current and overlays the string onto `candidate_data.context.writing_preferences` for the existing editor contract. Miss → empty editor.
4. **Retire blob authority** — Stop durable library-merge writes of `context.writing_preferences` as source of truth; stop token/live assembly from reading the blob for Writing Preferences after cutover.
5. **Token typing** — Flip `TOKEN_SOURCES["WRITING_PREFERENCES"]` from `data_field` to `artifact` with `artifact_key: "candidate.context.writing_preferences"`.
6. **UI path** — Keep Writing Preferences on `ContextTextPage`, the shared plain-text artifact editor introduced in AST-1629. Do not extend `ArtifactEditor` / `resume_content` for this leaf.
7. **No legacy backfill** — Do not migrate historical `context.writing_preferences` blobs in this ticket. Existing text stays in the blob until the operator re-saves through the new path; first operative save creates the artifact row.
8. **Explicit non-goals** — No coat-check ([AST-1572](https://linear.app/astralcareermatch/issue/AST-1572/implement-pattartifactno-coat-check)). No new craft task. No job/company catalog keys. No other context leaves (priorities, deal_breakers, ideal_day, backstory).

### Notes (Archie)

Copies the pattern established in [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) (Strengths) — same catalog / operative-save / hydrate / token-typing / UI shape, applied to the Writing Preferences field instead. Related to [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table). Claude Fable (2026-09-15): do not rederive from scratch — use [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) implementation guidelines.

### Comments

#### chuckles — 2026-09-16T00:53:06.977Z
AST-1664 STALE(dev+556) — @Ada Lovelace refresh sub (merge origin/dev + origin/ftr/AST-1645 + republish) before further build-child on this epic.

#### chuckles — 2026-09-15T22:14:27.789Z
@susan Dispatch blocked on AST-1645 — Proposed child tickets are not dispatchable:

- Missing `#### N!: **Title - Dev**` headers (have Ticket A/B/C prose only)
- No implementer assignees (Ada / Hedy / Katherine) on those rows
- Citations/Scope exist in the prose; format + assignees are the gap

Paste this under `## Proposed child tickets` (mirrors AST-1629 assignees / bangs; edit if wrong), move parent to Todo, assign Chuckles:

#### 1!!: **Catalog + plain_text shape reuse + WRITING_PREFERENCES token - Ada**

Register `candidate.context.writing_preferences` in `ARTIFACT_CONFIG` reusing the existing `plain_text` shape, flip `TOKEN_SOURCES["WRITING_PREFERENCES"]` to artifact plus `artifact_key`, lock startup asserts. Does not own UI or hydrate.
**Citations:** `patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `stat.logging.info` / `stat.logging.debug` as touched.
**Scope:** `src/utils/config.py` — new catalog entry plus asserts; `TOKEN_SOURCES["WRITING_PREFERENCES"]` flip.
**Estimate: 1**

#### 2!: **Operative save, hydrate, blob retirement - Hedy**

Wire Writing Preferences through candidate operative `plain_text` validation plus `get_candidate_current` hydrate on GET; intercept API PUT for operative save; stop durable library SoT writes for `context.writing_preferences`. No backfill helper. Does not own React chrome. After #1.
**Citations:** `patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.in-scope-only`; `stat.logging.info.entity`; `stat.logging.info.api`; `stat.logging.error`.
**Scope:** `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.writing_preferences`. `src/ui/api/api_candidate.py` — PUT intercept plus GET hydrate for Writing Preferences.
**Estimate: 3**

#### 3: **Writing Preferences ContextTextPage wire-up - Katherine**

Retarget Writing Preferences-only UI load/save to the operative API contract via existing `ContextTextPage`. No ArtifactEditor. No sibling context pages. After #1 (and API hydrate from #2 as needed).
**Citations:** `patt.artifact.ui-consistency`; `patt.artifact.read-current`; `patt.artifact.write-operative`.
**Scope:** `src/ui/frontend/src/pages/CandidateWritingPreferences.tsx` — Writing Preferences-only wire-up against existing ContextTextPage.
**Estimate: 2**

---

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/f7dd880d9a9b1c1012e259a01249275f/31b1f45c-753e-46d5-b1da-a0a7e2c0b212/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/f7dd880d9a9b1c1012e259a01249275f/843c5748-ae1b-4084-bc5a-86d36c17f9bf/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/f7dd880d9a9b1c1012e259a01249275f/46dbb980-72ab-40ae-85b8-1357187e43d3/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/63b8787d-68ab-4c8b-aaab-0dbc3e512544/store.db` |
| Radia | review | `/home/susan/.cursor/chats/f7dd880d9a9b1c1012e259a01249275f/c318e3b7-8ec8-47c0-8e10-fc62999669ed/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1645 (parent) | ftr/AST-1645-migrate-writing-preferences-artifact-table |
| AST-1664 | sub/AST-1645/AST-1664-catalog-plain-text-writing-preferences-token |
| AST-1665 | sub/AST-1645/AST-1665-operative-save-hydrate-blob-retirement |
| AST-1666 | sub/AST-1645/AST-1666-writing-preferences-contexttextpage-wire-up |

**Epic worktree:** `astral-AST-1645/` — one active sub checked out at a time.

## Bug: AST-2243 — Coerce dict Writing Preferences on hydrate

### As-is

On candidate `miller`, Writing Preferences artifact rows store dict `artifact_data` (`writing_general_instructions` + nested `writing_style`). `hydrate_operative_writing_preferences_for_response` early-returns on `not isinstance(body, str)`, so GET detail never overlays `context.writing_preferences` and `ContextTextPage` shows a blank textarea for every version (including `current=1`). Version-nav move still lists uuids, then `loadBody()` hits the same hydrate path and blanks again.

### To-be

When a current (or selected-as-current) Writing Preferences row exists, hydrate overlays a readable string into `context.writing_preferences` so the editor is non-empty. Dict bodies coerce for display under the existing `plain_text` contract — no new `body_shape`, no structured editor. Operative saves continue to reject non-strings (`plain_text body must be a non-empty string`). Sibling plain_text hydrates (Strengths / Ideal Day / etc.) stay str-only.

### Repro

Fixture shape (miller-equivalent; not a DB seed — file/JSON persistence):

```python
# Deserialized get_candidate_current(...) return for candidate.context.writing_preferences
body = {
    "writing_general_instructions": "Prefer short sentences. Avoid jargon.",
    "writing_style": {"observations": ["direct", "warm"]},
}
# Today: hydrate_operative_writing_preferences_for_response("miller", cd) leaves
# cd["context"]["writing_preferences"] unset/empty → blank ContextTextPage textarea.
# After fix: overlay is the non-empty writing_general_instructions string.
```

Steps: open Writing Preferences for a candidate whose current `writing_preferences` row deserializes to that dict → textarea blank; arrow-move to the other uuid → still blank after reload.

### Root cause

`hydrate_operative_writing_preferences_for_response` treats any non-`str` current body as a miss (`if not isinstance(body, str): return`). Miller's rows are dict-shaped (historical / pre-gate data). Tip hunt: the only candidate write into `database.save_artifact` is `save_candidate_data` str-path, which already rejects non-str `plain_text` — there is no live bypass writer under `src/core/` (or elsewhere) still inserting dict WP rows. The blank editor is a **read/hydrate** defect against legacy dict rows, not an active write regress.

### Proposed change

1. **`src/core/candidate.py` — `hydrate_operative_writing_preferences_for_response` only** (do not change Strengths / Priorities / Deal Breakers / bio_summary / Ideal Day / Backstory hydrates):
   - Miss (`body is None`) → return unchanged (leave legacy blob).
   - `isinstance(body, str)` → overlay `ctx["writing_preferences"] = body` unchanged.
   - `isinstance(body, dict)` → coerce for **display overlay only** (do not rewrite the artifact row):
     - If `body.get("writing_general_instructions")` is a non-empty `str` (after strip), use that string.
     - Else `json.dumps(body, sort_keys=True)` (stable, readable fallback when instructions are missing/empty).
     - Overlay the coerced string onto `ctx["writing_preferences"]`.
   - Any other non-str type → keep today's early return (no inventing coercions).
2. **Writer / AC4** — no code change. Tip confirms `save_candidate_data` plain_text branch already raises `ValueError("plain_text body must be a non-empty string")` before `save_artifact`; tracker `save_artifact` is job-scoped only. Document that finding in make-fix notes; do not add a `database.py` gate (out of this bug's Component scope / AST-1645 leaves database untouched).
3. **`src/ui/api/api_candidate.py`** — confirm-only, no edit: GET `get_candidate_detail` already calls `hydrate_operative_writing_preferences_for_response`; version move (`PUT .../current`) leaves body untouched, then `ContextTextPage.loadBody()` re-GETs detail (same hydrate). No missing call site.
4. **Frontend** — untouched (`ContextTextPage` / `CandidateWritingPreferences.tsx`). Client `coerceToString` does not understand WP dict keys; server overlay must supply a string.

### Blast radius

- Shared module: `src/core/candidate.py` hydrate helper used by GET detail and any other caller of `hydrate_operative_writing_preferences_for_response` (including `get_candidate` core hydrate if wired). Only the WP function changes.
- Sibling plain_text leaves: identical str-guards remain — no shared helper refactor in this bug.
- Tests that assert WP hydrate early-returns on non-str (AST-1665 suite around `hydrate_operative_writing_preferences_for_response`) will need Betty/qa-fix attention if they encoded the blanking behavior; engineer does not patch `tests/`.
- Token / live assembly reading current WP: if they consume hydrated context string vs raw artifact body, display coerce is response-overlay only — raw artifact_data stays dict until an operator re-saves a string through operative PUT.

### What must still hold

From AST-1645 / AST-1665 (do not regress):

1. Catalog key `candidate.context.writing_preferences` stays `body_shape: "plain_text"` — no new shape, no structured WP editor.
2. Operative save via `save_candidate_data(..., "candidate.context.writing_preferences", body)` still rejects non-empty-string failures with `plain_text body must be a non-empty string`.
3. Miss (no current row) still leaves the legacy `context.writing_preferences` blob untouched (migration window).
4. True string current bodies overlay unchanged.
5. Sibling context hydrates (Strengths, Priorities, Deal Breakers, bio_summary, Ideal Day, Backstory) keep str-only guards.
6. UI stays on `ContextTextPage`; `ArtifactEditor` untouched.
7. No bulk backfill / rewrite of historical dict artifact rows as part of this fix.
8. Bug AC: miller current WP shows non-empty readable text after GET hydrate; both version uuids reload non-empty bodies after move; new dict writes cannot land without plain_text validation (already true on tip).
