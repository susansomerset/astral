# AST-1641 — Migrate candidate_data.context.priorities to use the artifact table

<!-- linear-archive: AST-1641 archived 2026-09-24 -->

## Linear archive (AST-1641)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1641/migrate-candidate-datacontextpriorities-to-use-the-artifact-table  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / 5  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1572

### Description

## Purpose

Follow-on sibling to [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) (Strengths migration). `candidate_data.context.priorities` is still a plain library blob: no versioning, no `current` row, no pin, and `{$PRIORITIES}` resolves as a `data_field`. AST-1629 proved the artifact table + `ARTIFACT_CONFIG` path, plus the `plain_text` body shape, for Strengths. This ticket migrates **Priorities only** onto that same proven path — copy the pattern, do not rederive a second special case.

## Functional scope

1. **Catalog Priorities** — Register `candidate.context.priorities` in `ARTIFACT_CONFIG`, reusing the `plain_text` body shape added in AST-1629. No other context or artifact keys are added.
2. **Operative write** — Saving Priorities goes through candidate write-operative (`save_candidate_data` → `database.save_artifact`). No in-place blob UPDATE.
3. **Current read / hydrate** — GET/UI loads Priorities via read-current and overlays the string onto `candidate_data.context.priorities` for the existing editor contract. Miss → empty editor.
4. **Retire blob authority** — Stop durable library-merge writes of `context.priorities` as source of truth; stop token/live assembly from reading the blob for Priorities after cutover.
5. **Token typing** — Flip `TOKEN_SOURCES["PRIORITIES"]` from `data_field` to `artifact` with `artifact_key: "candidate.context.priorities"`.
6. **UI path** — Keep Priorities on `ContextTextPage`, the shared plain-text artifact editor from AST-1629. Do not extend `ArtifactEditor` / `resume_content` for this leaf.
7. **No legacy backfill** — Do not migrate historical `context.priorities` blobs. Existing text stays in the blob until the operator re-saves through the new path; first operative save creates the artifact row.
8. **Explicit non-goals** — No coat-check. No new craft task. No job/company catalog keys. No other context leaves (deal_breakers, backstory, ideal_day, writing_preferences).

## Component scope

* `src/utils/config.py` — **modified** — `ARTIFACT_CONFIG["candidate.context.priorities"]` plus asserts; reuses existing `BUILD_CONFIG["artifact_shapes"]["plain_text"]` raw-string contract from AST-1629; `TOKEN_SOURCES["PRIORITIES"]` becomes `artifact` plus `artifact_key`.
* `src/core/candidate.py` — **modified** — operative save validation for `plain_text` (reused path); hydrate Priorities from `get_candidate_current` on GET paths; gate durable library writes for `context.priorities`.
* `src/ui/api/api_candidate.py` — **modified** — PUT intercept: strip library `context.priorities`, call operative save; GET hydrate overlays current Priorities string.
* `src/ui/frontend/src/pages/CandidatePriorities.tsx` — **modified** — Priorities-only; stay on ContextTextPage path.
* `src/ui/frontend/src/components/ContextTextPage.tsx` — **untouched** — shared plain-text artifact editor already parameterized by AST-1629; Priorities is a new consumer, not a new wiring change.
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — **untouched**.
* `src/data/database.py` — **untouched** — existing `save_artifact` / `get_current_artifact` primitives only.

## Technical scope

* `src/utils/config.py` — Catalog entry: `entity_type: "candidate"`, `candidate_scoped: True`, `body_shape: "plain_text"`, `ingestion_owner: "candidate"`. Closed-set asserts include the new key; Priorities leaves the sibling-freeze-out list. `TOKEN_SOURCES["PRIORITIES"]` gains `source_type: "artifact"` and `artifact_key: "candidate.context.priorities"`.
* `src/core/candidate.py` — Operative str-path validates `plain_text` (reuses AST-1629 validation, no new rules); hydrate overlay writes current string into `context.priorities` for display; refuse durable library SoT write for that leaf when catalog owns it.
* `src/ui/api/api_candidate.py` — On PUT with Priorities: pop from library `context` merge, `save_candidate_data(candidate_id, "candidate.context.priorities", body)`; on GET hydrate current row into `context.priorities`.
* `src/ui/frontend/src/pages/CandidatePriorities.tsx` — Load/save only through the operative API contract via existing `ContextTextPage`; no parallel client storage key; no ArtifactEditor.

## Architectural definition

**Patterns to reuse** (all established by AST-1629 — no new patterns proposed):

* `patt.artifact.manage-catalog` — register Priorities; retire blob authority for that key. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* `patt.artifact.write-operative` — Priorities saves via blind retire+insert through entity-owned operative save. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>)
* `patt.artifact.read-current` — UI/GET hydrate and live Priorities from current row. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>)
* `patt.artifact.read-operative` — pin to body remains available via generic path (no Priorities-only pin surface required). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-operative.md>)
* `patt.artifact.ui-consistency` — editor path follows catalog `body_shape` (`plain_text` → ContextTextPage, not resume_content ArtifactEditor). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.ui-consistency.md>)

**New patterns proposed:** none — Priorities reuses the `plain_text` shape and all patterns as-is; this is config catalog data under manage-catalog, not a new pattern id.

**Applicable statutes** (same set as AST-1629):

* `stat.logging.info` — info contracts on touched surfaces. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md>)
* `stat.logging.warning` — warning contracts on touched surfaces. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>)
* `stat.logging.error` — error contracts on touched surfaces. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>)
* `stat.logging.debug` — debug contract on any `debug=` surfaces this epic touches. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)
* `stat.logging.info.entity` — entity/core info logging when candidate paths change. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>)
* `stat.logging.info.api` — API info logging when api_candidate Priorities paths change. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>)
* `astral.config.config-source-of-truth` — catalog key, body_shape, and token typing live in config. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.standards.no-hardcoded-sets` — closed catalog / shape membership via config asserts. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
* `astral.standards.in-scope-only` — Priorities only. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* `astral.layers.import-direction` — utils/config + core + ui layering. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
* `astral.git.engineer-test-tree-ban` — engineers do not own `tests/` / bible. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md>)
* `astral.standards.logging-via-utils` — logging through utils helpers. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md>)

Note: Artifact `patt.artifact.*` ids remain under `draft/` until promoted (same as AST-1629); logging `stat.logging.*` are active. Comply with every active directive that applies to touched surfaces.

## Acceptance criteria

1. **Catalog key present** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.priorities' in ARTIFACT_CONFIG"` exits 0. Fail: key absent or differently named without Description amendment.
2. **plain_text shape reused** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert ARTIFACT_CONFIG['candidate.context.priorities']['body_shape']=='plain_text'"` exits 0. Fail: Priorities bound to `resume_content` / `cover_letter`, or a new shape added.
3. **Token is artifact-typed** — `python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['PRIORITIES']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.priorities'"` exits 0. Fail: still `data_field` or wrong `artifact_key`.
4. **Operative round-trip** — Save Priorities via Priorities UI/API; `database.get_current_artifact('candidate', <id>, 'priorities')` returns a row whose `artifact_data` matches the saved string; a second save creates a new uuid and retires prior `current=1`. Fail: body only in library blob with no artifact row, or in-place UPDATE of same uuid.
5. **Blob not SoT on write** — Successful Priorities save calls operative `save_artifact`; does not rely on library-merge of `context.priorities` alone. Fail: PUT only deep-merges the blob.
6. **Editor reload** — Priorities page after save shows the same text. Fail: empty editor while a current artifact row exists.
7. **No backfill required** — Candidates with only legacy blob Priorities and no artifact row still load that blob (or empty) until re-save; no bulk migration job ships. Fail: epic adds a required one-shot migrate-all script as SoT.
8. **Sibling freeze** — `ARTIFACT_CONFIG` has no deal_breakers/backstory/ideal_day/writing_preferences keys. Fail: any of those registered.
9. **UI path** — Priorities still uses ContextTextPage (or a thin wrapper of it); `ArtifactEditor` diff for this ticket is empty. Fail: Priorities routed through ArtifactEditor / resume_content.

## Open questions

none

## Proposed child tickets

#### 1!!: **Catalog + plain_text shape reuse + PRIORITIES token - Ada**

Register `candidate.context.priorities` in `ARTIFACT_CONFIG` reusing the existing `plain_text` shape, flip `TOKEN_SOURCES["PRIORITIES"]` to artifact plus `artifact_key`, lock startup asserts (add key to closed set; remove from sibling-freeze-out list). Does not own UI or hydrate.
**Citations:** `patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `stat.logging.info` / `stat.logging.debug` as touched
**Scope:** `src/utils/config.py` — new catalog entry plus asserts; `TOKEN_SOURCES["PRIORITIES"]` flip.
**Estimate: 1**

#### 2!: **Operative save, hydrate, blob retirement - Hedy**

Wire Priorities through candidate operative `plain_text` validation plus `get_candidate_current` hydrate on GET; intercept API PUT for operative save; stop durable library SoT writes for `context.priorities`. No backfill helper. Does not own React chrome. After #1.
**Citations:** `patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.in-scope-only`; `stat.logging.info.entity`; `stat.logging.info.api`; `stat.logging.error`
**Scope:** `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.priorities`. `src/ui/api/api_candidate.py` — PUT intercept plus GET hydrate for Priorities.
**Estimate: 3**

#### 3: **Priorities ContextTextPage wire-up - Katherine**

Retarget Priorities-only UI load/save to the operative API contract via existing `ContextTextPage`. No ArtifactEditor. No sibling context pages. After #1 (and API hydrate from #2 as needed).
**Citations:** `patt.artifact.ui-consistency`; `patt.artifact.read-current`; `patt.artifact.write-operative`
**Scope:** `src/ui/frontend/src/pages/CandidatePriorities.tsx` — Priorities-only wire-up against existing ContextTextPage.
**Estimate: 2**

Monolith check: 8 functional capabilities into 3 children (config / core+API / UI), matching AST-1629's split.

Scope partition check: `config.py` → #1; `candidate.py` + `api_candidate.py` → #2; `CandidatePriorities.tsx` → #3. `ArtifactEditor.tsx`, `database.py`, and `ContextTextPage.tsx` untouched / unclaimed by design.

---

## Original brief

Follow-on sibling to [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) (Strengths migration). `candidate_data.context.priorities` is still a plain library blob: no versioning, no `current` row, no pin, and `{$PRIORITIES}` resolves as a `data_field`. [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) proved the artifact table + `ARTIFACT_CONFIG` path, plus the `plain_text` body shape, for Strengths. This ticket migrates **Priorities only** onto that same proven path.

### Functional scope (Archie)

1. **Catalog Priorities** — Register `candidate.context.priorities` in `ARTIFACT_CONFIG`, reusing the `plain_text` body shape added in AST-1629. No other context or artifact keys are added.
2. **Operative write** — Saving Priorities goes through candidate write-operative (`save_candidate_data(candidate_id, artifact_key, body)` → `database.save_artifact`). No in-place blob UPDATE.
3. **Current read / hydrate** — GET/UI loads Priorities via read-current and overlays the string onto `candidate_data.context.priorities` for the existing editor contract. Miss → empty editor.
4. **Retire blob authority** — Stop durable library-merge writes of `context.priorities` as source of truth; stop token/live assembly from reading the blob for Priorities after cutover.
5. **Token typing** — Flip `TOKEN_SOURCES["PRIORITIES"]` from `data_field` to `artifact` with `artifact_key: "candidate.context.priorities"`.
6. **UI path** — Keep Priorities on `ContextTextPage`, the shared plain-text artifact editor introduced in AST-1629. Do not extend `ArtifactEditor` / `resume_content` for this leaf.
7. **No legacy backfill** — Do not migrate historical `context.priorities` blobs in this ticket. Existing text stays in the blob until the operator re-saves through the new path; first operative save creates the artifact row.
8. **Explicit non-goals** — No coat-check ([AST-1572](https://linear.app/astralcareermatch/issue/AST-1572/implement-pattartifactno-coat-check)). No new craft task. No job/company catalog keys. No other context leaves (deal_breakers, backstory, ideal_day, writing_preferences).

### Notes (Archie)

Copies the pattern established in AST-1629 (Strengths) — same catalog / operative-save / hydrate / token-typing / UI shape, applied to the Priorities field instead. Related to AST-1629. Claude Fable (2026-09-15): do not rederive from scratch — use AST-1629 implementation guidelines.

### Comments

#### chuckles — 2026-09-15T23:52:16.461Z
AST-1653 build unblock — origin/ftr/AST-1641-migrate-priorities-artifact-table already carries AST-1651+AST-1652. Re-spawning Katherine sync-child with --ftr AST-1641-migrate-priorities-artifact-table (short origin/ftr/AST-1641 does not exist).

#### katherine — 2026-09-15T23:51:26.466Z
🛑 Stage 1 blocked: build precondition — catalog/API not on tip

Step: Build precondition (plan) — `ARTIFACT_CONFIG["candidate.context.priorities"]` + AST-1652 Priorities PUT/GET after `sync-child.sh`

Issue: `origin/ftr/AST-1641` is not on origin. After sync, this tip still has `candidate.context.strengths` + `candidate.context.bio_summary` only — no `candidate.context.priorities`, and no AST-1652 hydrate/intercept. Attempted merge of `origin/sub/AST-1641/AST-1651-…` into this publish-ref conflicted in `src/utils/config.py` (bio_summary vs priorities catalog divergence); merge aborted — will not invent catalog/API here.

Proposed resolutions:
1. Chuckles publish/merge `origin/ftr/AST-1641` with AST-1651 + AST-1652 rolled up, then re-run sync-child / build-child
2. Chuckles resolve the config divergence and land a clean ftr tip that includes both bio_summary and priorities catalog keys
3. Confirm build may proceed UI-only without sibling product on tip (plan currently forbids inventing catalog)

Need: (1) or (2) before Stage 1 product commit.

#### chuckles — 2026-09-15T23:36:39.495Z
AST-1652 REVIEW — merge-child/sync blocked; recalling @Betty White for sync(dev) commit that stages tests/bible from origin/dev (product conflicts already resolved by Hedy; MERGE still open on sub tip).

#### chuckles — 2026-09-15T23:19:34.622Z
AST-1652 build unblock — origin/ftr/AST-1641-migrate-priorities-artifact-table already carries AST-1651 catalog (a8a50950). Re-spawning Hedy sync-child with --ftr AST-1641-migrate-priorities-artifact-table (short origin/ftr/AST-1641 does not exist).

#### hedy — 2026-09-15T23:18:54.577Z
🛑 Stage 1 blocked: catalog key candidate.context.priorities missing on this sub

Step: Build precondition — ARTIFACT_CONFIG must contain `candidate.context.priorities` (AST-1651) before operative save/hydrate.

Issue: After sync-child on `sub/AST-1641/AST-1652-operative-save-hydrate-blob-retirement`, `origin/ftr/AST-1641` is not on origin and AST-1651 tip is not an ancestor of HEAD. `ARTIFACT_CONFIG` has no Priorities key (`PRIORITIES` still `data_field`; key still in sibling-freeze list). Plan forbids inventing the catalog entry in AST-1652 scope.

Proposed resolutions:
1. Chuckles: publish/merge AST-1651 into `origin/ftr/AST-1641`, then re-run sync-child on the AST-1652 sub so the catalog lands.
2. Temporarily merge `origin/sub/AST-1641/AST-1651-catalog-plain-text-priorities-token` into the AST-1652 sub (same product tip, outside ftr rollup) — need Chuckles OK if ftr path preferred.
3. Need guidance if catalog should wait on another gate.

#### chuckles — 2026-09-15T22:09:37.908Z
@susan Dispatch blocked — `## Proposed child tickets` is Ticket A/B/C prose, not mechanical `####` blocks. Dispatch cannot invent assignees or bang sequencing.

Missing shape (paste over Proposed; fill assignees — AST-1629 used Ada / Hedy / Katherine for the same config / core+API / UI split):

#### 1!!: **Catalog + plain_text shape reuse + PRIORITIES token - <Ada|Hedy|Katherine>**
#### 2!: **Operative save, hydrate, blob retirement - <Ada|Hedy|Katherine>**
#### 3: **Priorities ContextTextPage wire-up - <Ada|Hedy|Katherine>**

Keep each block's Citations / Scope / Estimate from the current Ticket A/B/C bodies. Then Todo + assign Chuckles.

#### chuckles — 2026-09-15T22:06:20.393Z
[check-linear] answered — Priorities will copy AST-1629 Strengths (catalog / operative-save / hydrate / token-typing / UI); no greenfield approach. Component/Technical/Architectural + Proposed children still required before dispatch. (@susan)

#### fable — 2026-09-15T22:04:52.467Z
@chuckles Please don't rederive the implementation approach for this ticket from scratch. Use the implementation guidelines already stipulated in the related ticket, AST-1629 (the Strengths migration) — this ticket is meant to copy that same pattern (catalog / operative-save / hydrate / token-typing / UI shape) applied to the Priorities field.

#### chuckles — 2026-09-15T22:04:03.746Z
@susan Dispatch blocked — definition incomplete for AST-1641. Missing before children can be created:

- `## Component scope`
- `## Technical scope`
- `## Architectural definition` (pattern ids or explicit no-pattern flag)
- `## Proposed child tickets` with `####` blocks (assignee, Citations, Scope)

Purpose / Functional scope / Notes are present; no children, no comments to recover from. Please run define-parent (or paste the missing sections), then Todo + assign Chuckles when ready.

---

_Implementation detail may live in git history on `origin/dev`._
