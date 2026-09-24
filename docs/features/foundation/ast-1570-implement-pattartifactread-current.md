# AST-1570 — Implement patt.artifact.read-current

<!-- linear-archive: AST-1570 archived 2026-09-24 -->

## Linear archive (AST-1570)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1570/implement-pattartifactread-current  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / 5  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-1572

### Description

## Purpose

Ship **read-current** so UI edit and live-display paths return the **artifacts-table** `current=1` **body** for the pilot catalog key `candidate.artifacts.base_resume` via a candidate-owned current-read helper — never a stale `candidate_data` blob copy. Write-operative ([AST-1569](https://linear.app/astralcareermatch/issue/AST-1569)) already hydrates pilot GET; this epic finishes API/server current reads for editors, live display, and existing base_resume fetch sites in batch/builder token paths. Sibling **read-operative** ([AST-1571](https://linear.app/astralcareermatch/issue/AST-1571)) owns pin/explainability; **no-coat-check** ([AST-1572](https://linear.app/astralcareermatch/issue/AST-1572)) depends on both reads. Contact Estelle cache freshen and tracker job paths are **out of scope** (Archie).

## Functional scope

1. **Current read for pilot key** — Load the `current=1` artifacts-table body for `candidate.artifacts.base_resume` (catalog key in, body or empty out). This is the only supported path for UI editors and for server live display / existing base_resume consumers that must reflect the latest operator-approved body.
2. **Candidate-owned helper** — Entity-owned current-read entry that takes the catalog artifact key (Archie’s working name: `get_candidate_current`) and returns the operative current body — callers pass the key, not scrape blobs.
3. **GET hydrate ignores blobs** — Candidate GET overlays base_resume from the artifacts table only. Ignore leftover `candidate_data.artifacts.base_resume` blobs (manual cleanup later); on miss use empty contract — do not fall back to the blob.
4. **API GET handlers** — Edit/live candidate GET surfaces that serve base_resume resolve through that hydrate / current read. No new blob reads for the pilot key.
5. **Existing base_resume fetch sites** — Where batch / builder / token / live-display code currently fetches base_resume from `candidate_data` blobs, replace with the current-read helper and the artifact key. Contact Estelle freshen / surgical cache is out of scope. Tracker stays out.
6. **Pattern draft alignment** — Revise `patt.artifact.read-current` so `src/core/tracker.py` is an **example** application, not an explicit `scope` requirement for this implementation wave.
7. **Explicit non-goals** — No Contact Estelle cache management (unscoped statute). No tracker job live-path changes. No read-operative / pin work. No coat-check retirement. No new `ARTIFACT_CONFIG` keys. No React editor / ui-consistency work. No HTTP `artifact_id` on ordinary candidate GET.

## Component scope

* `src/data/database.py` — **modified** — `get_current_artifact` remains data-layer SoT for current rows; empty-on-miss; no blob fallback.
* `src/core/candidate.py` — **modified** — current-read helper by artifact key; GET hydrate from artifacts table only (ignore blob); rewire in-file live-display / token / structure helpers that still walk raw base_resume blobs.
* `src/ui/api/api_candidate.py` — **modified** — GET edit/live surfaces use hydrate / current-read for base_resume; no blob dual-read.
* `src/core/builder.py` — **modified** — `build_base_resume` and other in-file base_resume blob fetches switch to current-read + artifact key.
* `src/ui/api/api_resume_html.py` — **modified** — only if it assembles base_resume outside builder; otherwise stays a thin caller of the rewired builder path (claim only the edit needed).
* `src/utils/config.py` — **modified** — only the token-serialize path that pulls base_resume for live content (`BASE_RESUME` / `format_base_resume_for_token`); no catalog key additions.
* `canon/directives/draft/patt.artifact.read-current.md` — **modified** — drop tracker from hard `scope` list; reference tracker as an example consumer, not a required touch for this epic.

## Technical scope

* `src/data/database.py` — Current-row SELECT by entity type / entity id / artifact type; deserialize; return row or empty on miss. No logging; no blob read; no coat-check.
* `src/core/candidate.py` — New public current-read by catalog artifact key (working name `get_candidate_current`): resolve `ARTIFACT_CONFIG`, call `get_current_artifact`, return body or empty. GET hydrate overlays that body and does not read/merge leftover blob for base_resume. Live helpers (`format_base_resume_for_token`, structure/whitelist sources, etc.) obtain the body via current-read (candidate id + key) rather than `artifacts.get("base_resume")` from a raw blob. Debug on touched `debug=` surfaces: Style D index + `|` found/recorded per AST-538.
* `src/ui/api/api_candidate.py` — GET detail / resume-structure paths that expose base_resume use hydrated candidate / current-read only.
* `src/core/builder.py` — Replace blob reads of `candidate_data.artifacts.base_resume` in live build paths with current-read + artifact key; miss → empty / existing error contract without blob fallback.
* `src/ui/api/api_resume_html.py` — Retarget only if it bypasses builder; otherwise no independent logic change beyond calling updated builder.
* `src/utils/config.py` — Token serializer for `BASE_RESUME` uses current-read (or a helper that does) instead of formatting a raw blob copy.
* `canon/directives/draft/patt.artifact.read-current.md` — Frontmatter `scope` lists the files this wave actually requires (data / ui api / candidate — not tracker). Applications / Implementation mention tracker only as a future/example consumer when job keys exist.

## Architectural definition

**Patterns to reuse**

* `patt.artifact.read-current` — authoritative current-read arc; this epic also amends draft `scope` so tracker is example-only. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>)
* `patt.artifact.write-operative` — writes the current rows this epic reads. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>)
* `patt.artifact.manage-catalog` — pilot key only via `ARTIFACT_CONFIG`. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* `patt.artifact.read-operative` — **boundary only** (pins stay on [AST-1571](https://linear.app/astralcareermatch/issue/AST-1571)). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-operative.md>)
* `patt.artifact.no-coat-check` — **boundary only** ([AST-1572](https://linear.app/astralcareermatch/issue/AST-1572)). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.no-coat-check.md>)

**New patterns proposed**

* none

**Applicable statutes**

* `astral.standards.in-scope-only` — [in-scope-only](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* `astral.standards.database-header-inventory` — [database-header-inventory](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.database-header-inventory.md>)
* `astral.standards.data-raises-caller-logs` — [data-raises-caller-logs](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.data-raises-caller-logs.md>)
* `astral.standards.debug-contract-gated` — [debug-contract-gated](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>)
* `astral.layers.import-direction` — [import-direction](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
* `astral.config.config-source-of-truth` — [config-source-of-truth](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* Universal set applies to product code.

**Requesting a change to an existing pattern: **`patt.artifact.read-current` — current draft lists `src/core/tracker.py` in frontmatter `scope` as if required; change needed: treat tracker as an example consumer only until job keys are cataloged (Archie). Draft file linked above is the current text to amend — not already amended.

## Acceptance criteria

1. A caller can load the pilot current base_resume body via a candidate-owned helper that takes the catalog artifact key; miss returns empty — no `candidate_data` blob fallback.
2. Candidate GET overlays base_resume from the artifacts table only; leftover blobs are ignored (not merged as recovery).
3. API GET edit/live surfaces that serve base_resume use that hydrate / current-read; no new blob reads for the pilot key on those paths.
4. Existing in-scope base_resume fetch sites in builder / token / live-display helpers use the current-read helper + artifact key instead of raw blob walks.
5. Draft `patt.artifact.read-current` no longer lists tracker as a hard `scope` requirement; tracker appears only as an example.
6. No Contact Estelle cache work; no tracker product changes; no new catalog keys; no pin/explainability; no coat-check retirement; no React editor changes.
7. Touched backend `debug=True` current-resolve paths emit Style D index + `|` found/recorded detail per AST-538.

## Open questions

none

## Proposed child tickets

#### 1!: **Current-read helper + GET hydrate + pattern scope revise - Ada**

Data-layer current-read contract; candidate `get_candidate_current`-style helper by artifact key; GET hydrate ignores blobs for base_resume; `api_candidate` GET surfaces use it; revise draft pattern so tracker is example-only. Does **not** own builder / token consumer rewires (sibling #2).

**Citations: **`patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.database-header-inventory`; `astral.standards.data-raises-caller-logs`; `astral.layers.import-direction`; `astral.config.config-source-of-truth`

**Scope: **`src/data/database.py`; `src/core/candidate.py` (helper + GET hydrate only); `src/ui/api/api_candidate.py`; `canon/directives/draft/patt.artifact.read-current.md`

**Estimate: 3**

#### 2: **Base_resume consumer rewires (builder / token / live helpers) - Hedy**

After #1: replace remaining in-scope blob fetches of base_resume with current-read + artifact key in builder, candidate live-display/token/structure helpers, config token-serialize path, and `api_resume_html` only if it bypasses builder; debug contract on touched `debug=` paths. Contact and tracker stay out.

**Citations: **`patt.artifact.read-current`; `patt.artifact.write-operative`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`; `astral.layers.import-direction`

**Scope: **`src/core/builder.py`; `src/core/candidate.py` (live-display / format / structure / whitelist helpers only — helper+hydrate owned by #1); `src/utils/config.py` (BASE_RESUME token path only); `src/ui/api/api_resume_html.py` (only if independent of builder)

**Estimate: 5**

**Monolith check:** Helper+API+pattern vs consumer sweep → 2 children. Contact/tracker excluded by Archie.

**Scope partition check:** database + helper/hydrate + api_candidate + pattern draft → child 1. builder + candidate live helpers + config token path + conditional api_resume_html → child 2. No file claimed twice for the same change kind.

---

## Original brief

## Scope

read-current API and server paths for UI edit and live display.

## Pattern

`canon/directives/draft/patt.artifact.read-current.md`

## Depends on

write-operative

## Done when

GET handlers use get_current_artifact; no new blob reads for catalog-covered keys.

### Comments

#### chuckles — 2026-09-03T14:49:27.401Z
AST-1562 REVIEW — Radia discuss: Betty fix test_meteorite_email.py collection before broad component pytest.

#### chuckles — 2026-09-03T00:23:54.627Z
@susan

1. **Contact Estelle** — Pattern Implementation calls for candidate-scoped cache freshen + surgical artifact fetch on conversation start. Include Contact current-read wiring in this epic, or defer to AST-1572 / a follow-on?
2. **Batch / consult pre-dispatch** — Pattern also lists pre-dispatch assembly calling read-current for latest operator bodies. Include those consumers here, or leave them to AST-1572 (no-coat-check / ingestion-before-dispatch)?
3. **Miss vs leftover blob** — Today pilot hydrate no-ops when no current row, leaving any legacy `candidate_data.artifacts.base_resume` blob visible. On miss, should GET overlay force catalog empty shape (hide stale blob), or leave the blob until a dedicated migration ticket?
4. **Tracker / job live paths** — Draft pattern `scope` lists `src/core/tracker.py`, but `ARTIFACT_CONFIG` has no job keys yet and tracker already prefers `get_current_artifact` with legacy blob fallback. Touch tracker this ticket (e.g. ban blob fallback for any future catalog key), or keep tracker out until a job key is registered?

---

_Implementation detail may live in git history on `origin/dev`._
