<!-- linear-archive: AST-1647 archived 2026-09-24 -->

## Linear archive (AST-1647)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1647/migrate-candidate-bio-summary-to-use-the-artifact-table-and-remove  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / 5  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1572

### Description

## Purpose

Bio summary today is a library blob at `candidate_data.context.bio_summary`, edited as a tabbed textarea on the candidate profile page, with `{$BIO_SUMMARY}` still typed as a `data_field`. [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) already proved the artifact-catalog + `plain_text` + ContextTextPage path for Strengths. This epic migrates **bio summary only** onto that same proven path and relocates editing off the profile page onto its own candidate nav leaf — so bio summary is a true versioned artifact in the UI, not a profile field.

## Functional scope

1. **Catalog bio summary** — Register `ARTIFACT_CONFIG["candidate.context.bio_summary"]` with the existing `plain_text` body shape from AST-1629. No other context or artifact keys are added in this epic.
2. **Operative write** — Saving bio summary goes through candidate write-operative (`save_candidate_data(candidate_id, artifact_key, body)` → `database.save_artifact`). No in-place blob UPDATE; no craft-specific persist helper.
3. **Current read / hydrate** — GET/UI loads bio summary via read-current and overlays the string onto `candidate_data.context.bio_summary` for the editor contract. Miss → empty editor (legacy blob may still display until re-save). No coat-check.
4. **Retire blob authority** — Stop durable library-merge writes of `context.bio_summary` as source of truth; stop token/live assembly from reading the blob for bio summary after cutover.
5. **Token typing** — Flip `TOKEN_SOURCES["BIO_SUMMARY"]` from `data_field` to `artifact` with `artifact_key: "candidate.context.bio_summary"`.
6. **Remove from candidate profile** — Drop the profile “Bio Summary” section so bio summary no longer renders as an inline/tabbed field on the candidate profile page.
7. **Dedicated editor surface** — Give bio summary its own Candidate nav item, route, and thin ContextTextPage wrapper (same pattern as Strengths), with `bodyShape: "plain_text"`. Do not extend `ArtifactEditor` / `resume_content` for this leaf. Do not re-parameterize `ContextTextPage` unless something is broken for reuse.
8. **No legacy backfill** — Do not migrate historical bio summary blobs. Existing text stays in the blob until the operator re-saves through the new path; first operative save creates the artifact row.
9. **Explicit non-goals** — No coat-check. No new craft task. No other context leaves (priorities, deal_breakers, backstory, ideal_day, writing_preferences, company search terms). No identical-body versioning work beyond whatever already landed with Strengths. No changes to unrelated profile fields (contact, sample cover letter, signatures, etc.). No `INTAKE_CONFIG` changes.

## Component scope

* `src/utils/config.py` — **modified** — `ARTIFACT_CONFIG["candidate.context.bio_summary"]` + closed-set asserts; `TOKEN_SOURCES["BIO_SUMMARY"]` → `artifact` + `artifact_key`; remove `DATA_SHAPES["candidates"]["detail"]["profile"]` “Bio Summary” section (`context.bio_summary` textarea); add `NAV_CONFIG` Candidate item for Bio Summary (path `/candidate/bio_summary`). Reuses existing `BUILD_CONFIG["artifact_shapes"]["plain_text"]` — do not invent a second shape. `INTAKE_CONFIG` / unrelated profile fields — **untouched**.
* `src/core/candidate.py` — **modified** — extend operative `plain_text` save/hydrate/blob-gate paths already used for Strengths to own `context.bio_summary` / `candidate.context.bio_summary`.
* `src/ui/api/api_candidate.py` — **modified** — PUT intercept + GET hydrate for bio summary (same contract as Strengths: context-leaf payload → operative save).
* `src/ui/frontend/src/pages/CandidateBioSummary.tsx` — **new** — bio-summary-only ContextTextPage wrapper (`contextKey="bio_summary"`, `bodyShape="plain_text"`).
* `src/ui/frontend/src/routes.tsx` — **modified** — register `candidate/bio_summary` route to the new page.
* `src/ui/frontend/src/pages/CandidateProfile.tsx` — **untouched** — profile sections are config-driven; removing the Bio Summary block from config is sufficient.
* `src/ui/frontend/src/components/ContextTextPage.tsx` — **untouched** — reuse as parameterized in AST-1634.
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — **untouched**.
* `src/data/database.py` — **untouched** — existing `save_artifact` / `get_current_artifact` primitives only.

## Technical scope

* `src/utils/config.py` — Catalog entry: `entity_type: "candidate"`, `candidate_scoped: True`, `body_shape: "plain_text"`, `ingestion_owner: "candidate"`. Closed-set asserts include the new key and keep sibling context leaves out. Flip `TOKEN_SOURCES["BIO_SUMMARY"]` to `source_type: "artifact"` with `artifact_key: "candidate.context.bio_summary"`. Delete the `DATA_SHAPES["candidates"]["detail"]["profile"]` section whose only field is `context.bio_summary`. Add `NAV_CONFIG` Candidate item `{label: "Bio Summary", path: "/candidate/bio_summary"}` (placement with the other context leaves).
* `src/core/candidate.py` — Operative str-path already validates `plain_text`; wire bio summary leaf through the same save/hydrate/library-gate behavior Strengths uses (catalog key `candidate.context.bio_summary`, library path `context.bio_summary`). No new validation shape.
* `src/ui/api/api_candidate.py` — On PUT with bio summary: pop from library `context` merge, call `save_candidate_data(candidate_id, "candidate.context.bio_summary", body)`; on GET hydrate current row into `context.bio_summary`.
* `src/ui/frontend/src/pages/CandidateBioSummary.tsx` — Thin page: title Bio Summary, `contextKey="bio_summary"`, `bodyShape="plain_text"`; load/save only through the existing context-leaf API contract.
* `src/ui/frontend/src/routes.tsx` — Import + path `candidate/bio_summary` only for this leaf.

## Architectural definition

**Patterns to reuse**

* `patt.artifact.manage-catalog` — register bio summary; retire blob authority for that key. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* `patt.artifact.write-operative` — bio summary saves via blind retire+insert through entity-owned operative save. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>)
* `patt.artifact.read-current` — UI/GET hydrate and live bio summary from current row. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>)
* `patt.artifact.read-operative` — pin→body remains available via generic path (no bio-summary-only pin surface required). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-operative.md>)
* `patt.artifact.ui-consistency` — editor path follows catalog `body_shape` (`plain_text` → ContextTextPage, not resume_content ArtifactEditor, and not inline on the profile page). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.ui-consistency.md>)

**New patterns proposed**

* none — copy AST-1629; `plain_text` already exists under manage-catalog.

**Applicable statutes**

* `stat.logging.info` — info contracts on touched surfaces. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md>)
* `stat.logging.warning` — warning contracts on touched surfaces. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>)
* `stat.logging.error` — error contracts on touched surfaces. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>)
* `stat.logging.debug` — debug contract on any `debug=` surfaces this epic touches. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)
* `stat.logging.info.entity` — entity/core info logging when candidate paths change. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>)
* `stat.logging.info.api` — API info logging when api_candidate bio summary paths change. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>)
* `astral.config.config-source-of-truth` — catalog key, body_shape, token typing, profile/nav shape live in config. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.standards.no-hardcoded-sets` — closed catalog / shape membership via config asserts. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
* `astral.standards.in-scope-only` — bio summary only. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* `astral.layers.import-direction` — utils/config + core + ui layering. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
* `astral.git.engineer-test-tree-ban` — engineers do not own `tests/` / bible. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md>)
* `astral.standards.logging-via-utils` — logging through utils helpers. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md>)

Note: Artifact `patt.artifact.*` ids remain under `draft/` until promoted; logging `stat.logging.*` are active. Comply with every active directive that applies to touched surfaces. This epic assumes the AST-1629 Strengths cutover (catalog key + `plain_text` + ContextTextPage parameterization) is available to reuse — sibling Foundation migrations AST-1641–AST-1646 stay out of scope.

## Acceptance criteria

 1. **Catalog key present** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.bio_summary' in ARTIFACT_CONFIG"` exits 0. Fail: key absent or differently named without Description amendment.
 2. **plain_text reuse** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG, BUILD_CONFIG; assert ARTIFACT_CONFIG['candidate.context.bio_summary']['body_shape']=='plain_text'; assert BUILD_CONFIG['artifact_shapes']['plain_text']=='raw_string'"` exits 0. Fail: bio summary bound to `resume_content` / `cover_letter`, or a second invented shape name.
 3. **Token is artifact-typed** — `python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['BIO_SUMMARY']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.bio_summary'"` exits 0. Fail: still `data_field` or wrong `artifact_key`.
 4. **Operative round-trip** — Save bio summary via Bio Summary UI/API; `database.get_current_artifact('candidate', <id>, 'bio_summary')` returns a row whose `artifact_data` matches the saved string; a second distinct save creates a new uuid and retires prior `current=1`. Fail: body only in library blob with no artifact row, or in-place UPDATE of same uuid.
 5. **Blob not SoT on write** — Successful bio summary save calls operative `save_artifact`; does not rely on library-merge of `context.bio_summary` alone. Fail: PUT only deep-merges the blob.
 6. **Gone from profile** — `python3 -c "from src.utils.config import DATA_SHAPES; p=DATA_SHAPES['candidates']['detail']['profile']; assert not any(s.get('label')=='Bio Summary' or any(f.get('key')=='context.bio_summary' for f in s.get('fields',[])) for s in p)"` exits 0. Fail: Bio Summary section or `context.bio_summary` still listed under `DATA_SHAPES['candidates']['detail']['profile']`.
 7. **Dedicated editor path** — `NAV_CONFIG` Candidate items include Bio Summary → `/candidate/bio_summary`; that route renders ContextTextPage with `contextKey="bio_summary"` and `bodyShape="plain_text"`; after save, reload shows the same text. Fail: no nav/route, or page uses ArtifactEditor / omits `plain_text`.
 8. **No backfill required** — Candidates with only legacy blob bio summary and no artifact row still load that blob (or empty) until re-save; no bulk migration job ships. Fail: epic adds a required one-shot migrate-all script as SoT.
 9. **Sibling freeze** — `ARTIFACT_CONFIG` has no priorities / deal_breakers / backstory / ideal_day / writing_preferences keys from this epic. Fail: any of those registered here.
10. **UI path purity** — `ArtifactEditor.tsx` and `ContextTextPage.tsx` diffs for this epic are empty (reuse only). Fail: bio summary forced through resume_content ArtifactEditor, or ContextTextPage reworked instead of a thin new page.

## Open questions

none

## Proposed child tickets

#### 1!!: **Catalog + BIO_SUMMARY token + profile/nav config - Ada**

Register `candidate.context.bio_summary` in `ARTIFACT_CONFIG` with existing `plain_text`, flip `TOKEN_SOURCES["BIO_SUMMARY"]` to artifact + `artifact_key`, lock startup asserts, remove profile Bio Summary section, add Candidate nav leaf. Does not own hydrate, API intercept, or React pages.
**Citations:** `patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `stat.logging.info` / `stat.logging.debug` as touched
**Scope:** `src/utils/config.py` — new catalog entry + asserts; `TOKEN_SOURCES["BIO_SUMMARY"]` flip; delete `DATA_SHAPES["candidates"]["detail"]["profile"]` Bio Summary section (`context.bio_summary`); add `NAV_CONFIG` Candidate item `{label: "Bio Summary", path: "/candidate/bio_summary"}`.
**Estimate: 2**

#### 2!: **Operative save, hydrate, blob retirement - Hedy**

Wire bio summary through the same candidate operative `plain_text` validation + hydrate-on-GET and API PUT intercept Strengths already uses; stop durable library SoT writes for `context.bio_summary`. No backfill helper. Does not own React chrome or catalog/nav. After #1.
**Citations:** `patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.in-scope-only`; `stat.logging.info.entity`; `stat.logging.info.api`; `stat.logging.error`
**Scope:** `src/core/candidate.py` — extend operative validation/hydrate/library-gate for `context.bio_summary` / `candidate.context.bio_summary`. `src/ui/api/api_candidate.py` — PUT intercept + GET hydrate for bio summary.
**Estimate: 3**

#### 3: **Bio Summary page + route - Katherine**

Stand up dedicated Bio Summary ContextTextPage wrapper and route. No ArtifactEditor. No ContextTextPage edits. No sibling context page rewrites. After #1 (and API hydrate from #2 as needed).
**Citations:** `patt.artifact.ui-consistency`; `patt.artifact.read-current`; `patt.artifact.write-operative`
**Scope:** `src/ui/frontend/src/pages/CandidateBioSummary.tsx` — **new** thin wrapper (`contextKey="bio_summary"`, `bodyShape="plain_text"`). `src/ui/frontend/src/routes.tsx` — register `candidate/bio_summary`.
**Estimate: 2**

**Monolith check:** 9 functional capabilities → 3 children (config / core+API / UI). Matches AST-1629’s config → operative → UI split; profile removal lives with catalog/nav config (#1) because profile sections are config-driven.

**Scope partition check:** `config.py` → #1; `candidate.py` + `api_candidate.py` → #2; `CandidateBioSummary.tsx` + `routes.tsx` → #3. `CandidateProfile.tsx`, `ContextTextPage.tsx`, `ArtifactEditor.tsx`, and `database.py` untouched / unclaimed by design.

---

## Original brief

Use the pattern established by Strengths ([AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table)) exactly — no rederived logic, wiring, or architecture. Add support for the field `bio_summary`, which already exists as a token and in candidate data, so it becomes a true artifact in the UI rather than a tabbed input field on the candidate profile page.

### Comments

#### chuckles — 2026-09-15T22:16:52.467Z
@susan Dispatch blocked on AST-1647 — definition not ready to materialize:

- **Open questions** still open: exact catalog key, token name, and current profile-page location for bio summary (Description says confirm before child tickets are finalized).
- **Component scope** and **Technical scope** are placeholders (“To be finalized…”), not locked file/API lists.
- **Acceptance criteria** same — “To be finalized against the confirmed field/entity.”
- **## Proposed child tickets** is prose Ticket A/B/C only — needs `#### <seq><bangs>: **Title - Dev**` blocks with Citations + Scope (and partition of Component/Technical scope), matching AST-1629’s shape. No invent at dispatch.

Please finish via define-parent (or paste the locked sections), then Todo + Chuckles again.

---

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/778773dfd35340acd0f01b6d48a105ea/901adc18-6b27-4481-9e3b-803d72e10f0f/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/778773dfd35340acd0f01b6d48a105ea/66851543-06f1-49d0-ae2d-06f7ed0e302f/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/778773dfd35340acd0f01b6d48a105ea/27253292-fb1a-4add-8def-b1cd87267592/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/a3ddf83e-3cd8-49ae-808c-e315d5bda504/store.db` |
| Radia | review | `/home/susan/.cursor/chats/778773dfd35340acd0f01b6d48a105ea/37e4d036-4bfd-4282-8d81-a185267ff3a3/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1647 (parent) | ftr/AST-1647-migrate-bio-summary-artifact |
| AST-1648 | sub/AST-1647/AST-1648-catalog-bio-summary-token-profile-nav |
| AST-1649 | sub/AST-1647/AST-1649-operative-save-hydrate-blob-retirement |
| AST-1650 | sub/AST-1647/AST-1650-bio-summary-page-route |

**Epic worktree:** `astral-AST-1647/` — one active sub checked out at a time.
