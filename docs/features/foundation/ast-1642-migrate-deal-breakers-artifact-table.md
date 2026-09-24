<!-- linear-archive: AST-1642 archived 2026-09-24 -->

## Linear archive (AST-1642)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1642/migrate-candidate-datacontextdeal-breakers-to-use-the-artifact-table  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / 5  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1572

### Description

## Purpose

Follow-on sibling to [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) (Strengths migration). `candidate_data.context.deal_breakers` is still a plain library blob: no versioning, no `current` row, no pin, and `{$DEAL_BREAKERS}` resolves as a `data_field`. AST-1629 proved the artifact table + `ARTIFACT_CONFIG` path, plus the `plain_text` body shape, for Strengths. This ticket migrates **Deal Breakers only** onto that same proven path — copy the Strengths guidelines, do not rederive a second special case.

## Functional scope

1. **Catalog Deal Breakers** — Register Deal Breakers in the artifact catalog using the existing plain-text body shape. No other context or artifact keys are added.
2. **Operative write** — Saving Deal Breakers goes through the candidate write-operative into the artifact table. No in-place library blob UPDATE as source of truth.
3. **Current read / hydrate** — GET/UI loads Deal Breakers from the current artifact row and overlays it for the existing editor contract. Miss → empty editor.
4. **Retire blob authority** — Stop durable library-merge writes of Deal Breakers as source of truth; stop token/live assembly from reading the blob for Deal Breakers after cutover.
5. **Token typing** — Flip the Deal Breakers token from data-field to artifact-typed against the new catalog key.
6. **UI path** — Keep Deal Breakers on the shared plain-text ContextTextPage editor introduced in AST-1629. Do not extend ArtifactEditor / resume_content for this leaf.
7. **No legacy backfill** — Do not migrate historical Deal Breakers blobs in this ticket. Existing text stays in the blob until the operator re-saves through the new path; first operative save creates the artifact row.
8. **Explicit non-goals** — No coat-check (AST-1572). No new craft task. No job/company catalog keys. No other context leaves (priorities, backstory, ideal_day, writing_preferences).

## Component scope

* `src/utils/config.py` — modified — catalog entry for Deal Breakers plus asserts; reuses existing `plain_text` shape from AST-1629; Deal Breakers token becomes artifact plus `artifact_key`; remove Deal Breakers from the sibling-freeze assert list.
* `src/core/candidate.py` — modified — operative save validation for `plain_text` (reused path); hydrate Deal Breakers from current on GET paths; gate durable library writes for that leaf.
* `src/ui/api/api_candidate.py` — modified — PUT intercept: strip library Deal Breakers, call operative save; GET hydrate overlays current Deal Breakers string.
* `src/ui/frontend/src/pages/CandidateDealBreakers.tsx` — modified — Deal Breakers-only; stay on ContextTextPage path.
* `src/ui/frontend/src/components/ContextTextPage.tsx` — untouched — shared plain-text artifact editor already parameterized by AST-1629; Deal Breakers is a new consumer, not a new wiring change.
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — untouched.
* `src/data/database.py` — untouched — existing save/get-current artifact primitives only.

## Technical scope

* `src/utils/config.py` — Catalog entry: candidate entity, candidate-scoped, `plain_text` body shape, candidate ingestion owner. Closed-set asserts include the new key and drop Deal Breakers from the context-sibling freeze list. Deal Breakers token gains artifact source type and artifact key.
* `src/core/candidate.py` — Operative str-path validates `plain_text` (reuses AST-1629 validation, no new rules); hydrate overlay writes current string into the Deal Breakers context leaf for display; refuse durable library SoT write for that leaf when catalog owns it.
* `src/ui/api/api_candidate.py` — On PUT with Deal Breakers: pop from library context merge, call operative save with the Deal Breakers catalog key; on GET hydrate current row into the Deal Breakers context leaf.
* `src/ui/frontend/src/pages/CandidateDealBreakers.tsx` — Load/save only through the operative API contract via existing ContextTextPage; no parallel client storage key; no ArtifactEditor.

## Architectural definition

**Patterns to reuse** (same as AST-1629 — no new patterns proposed):

* `patt.artifact.manage-catalog` — register Deal Breakers; retire blob authority for that key. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* `patt.artifact.write-operative` — Deal Breakers saves via blind retire+insert through entity-owned operative save. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>)
* `patt.artifact.read-current` — UI/GET hydrate and live Deal Breakers from current row. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>)
* `patt.artifact.read-operative` — pin to body remains available via generic path (no Deal Breakers-only pin surface required). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-operative.md>)
* `patt.artifact.ui-consistency` — editor path follows catalog `body_shape` (`plain_text` → ContextTextPage, not resume_content ArtifactEditor). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.ui-consistency.md>)

**New patterns proposed**

* none — Deal Breakers reuses the `plain_text` shape and all patterns as-is; this is config catalog data under manage-catalog, not a new pattern id.

**Applicable statutes** (same set as AST-1629):

* `stat.logging.info` — info contracts on touched surfaces. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md>)
* `stat.logging.warning` — warning contracts on touched surfaces. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>)
* `stat.logging.error` — error contracts on touched surfaces. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>)
* `stat.logging.debug` — debug contract on any `debug=` surfaces this epic touches. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)
* `stat.logging.info.entity` — entity/core info logging when candidate paths change. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>)
* `stat.logging.info.api` — API info logging when api_candidate Deal Breakers paths change. [active](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>)
* `astral.config.config-source-of-truth` — catalog key, body_shape, and token typing live in config. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.standards.no-hardcoded-sets` — closed catalog / shape membership via config asserts. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
* `astral.standards.in-scope-only` — Deal Breakers only. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* `astral.layers.import-direction` — utils/config + core + ui layering. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
* `astral.git.engineer-test-tree-ban` — engineers do not own `tests/` / bible. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md>)
* `astral.standards.logging-via-utils` — logging through utils helpers. [statute](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md>)

Note: Artifact `patt.artifact.*` ids remain under `draft/` until promoted; logging `stat.logging.*` are active. Comply with every active directive that applies to touched surfaces. Follow AST-1629 implementation guidelines — do not rederive from scratch.

## Acceptance criteria

1. Catalog key present — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.deal_breakers' in ARTIFACT_CONFIG"` exits 0. Fail: key absent.
2. plain_text shape reused — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert ARTIFACT_CONFIG['candidate.context.deal_breakers']['body_shape']=='plain_text'"` exits 0. Fail: Deal Breakers bound to `resume_content` / `cover_letter`, or a new shape added.
3. Token is artifact-typed — `python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['DEAL_BREAKERS']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.deal_breakers'"` exits 0. Fail: still `data_field` or wrong key.
4. Operative round-trip — Save Deal Breakers via Deal Breakers UI/API; `database.get_current_artifact('candidate', <id>, 'deal_breakers')` returns a row whose `artifact_data` matches the saved string; a second save creates a new uuid and retires prior `current=1`. Fail: no current row, or second save overwrites in place without retire.
5. Blob not SoT on write — Successful Deal Breakers save calls operative `save_artifact`; does not rely on library-merge of `context.deal_breakers` alone. Fail: only library blob updated, no artifact row.
6. Editor reload — Deal Breakers page after save shows the same text. Fail: empty editor while a current artifact row exists.
7. No backfill required — Candidates with only legacy blob Deal Breakers and no artifact row still load that blob (or empty) until re-save; no bulk migration job ships. Fail: migration script or forced wipe of legacy text.
8. Sibling freeze — `ARTIFACT_CONFIG` has no priorities/backstory/ideal_day/writing_preferences keys; Deal Breakers is present and no longer in the context-sibling freeze assert. Fail: any of those other keys registered, or Deal Breakers still asserted absent.
9. UI path — Deal Breakers still uses ContextTextPage (or a thin wrapper of it); `ArtifactEditor` diff for this ticket is empty. Fail: ArtifactEditor changed or Deal Breakers routed through resume_content editor.

## Open questions

none

## Proposed child tickets

#### 1!!: **Catalog + plain_text shape reuse + DEAL_BREAKERS token - Ada**

Register `candidate.context.deal_breakers` in `ARTIFACT_CONFIG` reusing the existing `plain_text` shape, flip `TOKEN_SOURCES["DEAL_BREAKERS"]` to artifact plus `artifact_key`, lock startup asserts (drop Deal Breakers from sibling freeze). Does not own UI or hydrate. Mirror AST-1632 guidelines.
**Citations:** `patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `stat.logging.info` / `stat.logging.debug` as touched
**Scope:** `src/utils/config.py` — new catalog entry plus asserts; `TOKEN_SOURCES["DEAL_BREAKERS"]` flip; remove Deal Breakers from context-sibling freeze assert.
**Estimate: 1**

#### 2!: **Operative save, hydrate, blob retirement - Hedy**

Wire Deal Breakers through candidate operative `plain_text` validation plus `get_candidate_current` hydrate on GET; intercept API PUT for operative save; stop durable library SoT writes for `context.deal_breakers`. No backfill helper. Does not own React chrome. After #1. Mirror AST-1633 guidelines.
**Citations:** `patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.in-scope-only`; `stat.logging.info.entity`; `stat.logging.info.api`; `stat.logging.error`
**Scope:** `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.deal_breakers`. `src/ui/api/api_candidate.py` — PUT intercept plus GET hydrate for Deal Breakers.
**Estimate: 3**

#### 3: **Deal Breakers ContextTextPage wire-up - Katherine**

Retarget Deal Breakers-only UI load/save to the operative API contract via existing `ContextTextPage`. No ArtifactEditor. No sibling context pages. After #1 (and API hydrate from #2 as needed). Mirror AST-1634 guidelines.
**Citations:** `patt.artifact.ui-consistency`; `patt.artifact.read-current`; `patt.artifact.write-operative`
**Scope:** `src/ui/frontend/src/pages/CandidateDealBreakers.tsx` — Deal Breakers-only wire-up against existing ContextTextPage.
**Estimate: 2**

**Monolith check:** 8 functional capabilities → 3 children (config / core+API / UI), matching AST-1629's split.

**Scope partition check:** `src/utils/config.py` → #1; `src/core/candidate.py` + `src/ui/api/api_candidate.py` → #2; `CandidateDealBreakers.tsx` → #3. `ContextTextPage.tsx`, `ArtifactEditor.tsx`, and `database.py` untouched / unclaimed by design.

---

## Original brief

Follow-on sibling to [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) (Strengths migration). `candidate_data.context.deal_breakers` is still a plain library blob: no versioning, no `current` row, no pin, and `{$DEAL_BREAKERS}` resolves as a `data_field`. AST-1629 proved the artifact table + `ARTIFACT_CONFIG` path, plus the `plain_text` body shape, for Strengths. This ticket migrates **Deal Breakers only** onto that same proven path.

### Functional scope (Archie)

1. **Catalog Deal Breakers** — Register `candidate.context.deal_breakers` in `ARTIFACT_CONFIG`, reusing the `plain_text` body shape added in [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table). No other context or artifact keys are added.
2. **Operative write** — Saving Deal Breakers goes through candidate write-operative (`save_candidate_data(candidate_id, artifact_key, body)` → `database.save_artifact`). No in-place blob UPDATE.
3. **Current read / hydrate** — GET/UI loads Deal Breakers via read-current and overlays the string onto `candidate_data.context.deal_breakers` for the existing editor contract. Miss → empty editor.
4. **Retire blob authority** — Stop durable library-merge writes of `context.deal_breakers` as source of truth; stop token/live assembly from reading the blob for Deal Breakers after cutover.
5. **Token typing** — Flip `TOKEN_SOURCES["DEAL_BREAKERS"]` from `data_field` to `artifact` with `artifact_key: "candidate.context.deal_breakers"`.
6. **UI path** — Keep Deal Breakers on `ContextTextPage`, the shared plain-text artifact editor introduced in [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table). Do not extend `ArtifactEditor` / `resume_content` for this leaf.
7. **No legacy backfill** — Do not migrate historical `context.deal_breakers` blobs in this ticket. Existing text stays in the blob until the operator re-saves through the new path; first operative save creates the artifact row.
8. **Explicit non-goals** — No coat-check ([AST-1572](https://linear.app/astralcareermatch/issue/AST-1572/implement-pattartifactno-coat-check)). No new craft task. No job/company catalog keys. No other context leaves (priorities, backstory, ideal_day, writing_preferences).

### Notes (Archie)

Copies the pattern established in [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) (Strengths) — same catalog / operative-save / hydrate / token-typing / UI shape, applied to the Deal Breakers field instead. Related to [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table). Claude Fable (2026-09-15): do not rederive from scratch — use [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) implementation guidelines.

### Comments

#### chuckles — 2026-09-15T22:10:59.316Z
@susan — dispatch blocked on AST-1642. What's missing:

- `## Proposed child tickets` must use `#### <seq><bangs>: **<Working title> - <Ada|Hedy|Katherine>**` blocks (one per child). Current text is Ticket A/B/C prose with no assignee names and no `####` headers — dispatch can't materialize assignees or bang/`blockedBy` from that shape.
- Paste (or edit) something like the sibling AST-1629 list, e.g.:

#### 1!!: **Catalog + plain_text shape + DEAL_BREAKERS token - Ada**
(body from Ticket A — Citations + Scope)

#### 2!: **Operative save, hydrate, blob retirement - Hedy**
(body from Ticket B — after #1)

#### 3: **Deal Breakers ContextTextPage wire-up - Katherine**
(body from Ticket C — after #1 / #2 as needed)

When the `####` list is on the Description, move back to Todo + assignee Chuckles.

---

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/ded614485dc3bef86b1a03905cff6e5b/eb7d4efe-07e7-473a-99d1-793db4940dd3/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/ded614485dc3bef86b1a03905cff6e5b/1e7d59f4-f3e9-41cb-a39d-d62e939d4d39/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/ded614485dc3bef86b1a03905cff6e5b/67a87835-2fab-4ec7-bd56-5053157395fc/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/78d77a20-c160-4560-bcba-7d345cc187ae/store.db` |
| Radia | review | `/home/susan/.cursor/chats/ded614485dc3bef86b1a03905cff6e5b/b296098e-0781-45eb-a3ea-207602805e9e/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1642 (parent) | ftr/AST-1642-migrate-deal-breakers-artifact-table |
| AST-1654 | sub/AST-1642/AST-1654-catalog-plain-text-deal-breakers-token |
| AST-1655 | sub/AST-1642/AST-1655-operative-save-hydrate-blob-retirement |
| AST-1656 | sub/AST-1642/AST-1656-deal-breakers-contexttextpage-wire-up |

**Epic worktree:** `astral-AST-1642/` — one active sub checked out at a time.
