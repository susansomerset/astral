<!-- linear-archive: AST-1644 archived 2026-09-24 -->

## Linear archive (AST-1644)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1644/migrate-candidate-datacontextbackstory-to-use-the-artifact-table  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / 5  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1572

### Description

## Purpose

Follow-on sibling to [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) (Strengths migration). `candidate_data.context.backstory` is still a plain library blob: no versioning, no `current` row, no pin, and `{$BACKSTORY}` resolves as a `data_field`. AST-1629 proved the artifact table + `ARTIFACT_CONFIG` path and the `plain_text` body shape. This epic migrates **Backstory only** onto that same proven path — copy AST-1629's implementation guidelines; do not invent a second special case.

## Functional scope

1. **Catalog Backstory** — Register `candidate.context.backstory` in `ARTIFACT_CONFIG`, reusing the existing `plain_text` body shape from AST-1629. No other context or artifact keys are added.
2. **Operative write** — Saving Backstory goes through candidate write-operative (`save_candidate_data(candidate_id, artifact_key, body)` → `database.save_artifact`). No in-place blob UPDATE.
3. **Current read / hydrate** — GET/UI loads Backstory via read-current and overlays the string onto `candidate_data.context.backstory` for the existing editor contract. Miss → empty editor.
4. **Retire blob authority** — Stop durable library-merge writes of `context.backstory` as source of truth; stop token/live assembly from reading the blob for Backstory after cutover.
5. **Token typing** — Flip `TOKEN_SOURCES["BACKSTORY"]` from `data_field` to `artifact` with `artifact_key: "candidate.context.backstory"`.
6. **UI path** — Keep Backstory on `ContextTextPage` (already parameterized by AST-1629). Wire `CandidateBackstory` like `CandidateStrengths` (`bodyShape="plain_text"`). Do not extend `ArtifactEditor` / `resume_content` for this leaf.
7. **No legacy backfill** — Do not migrate historical `context.backstory` blobs in this ticket. Existing text stays in the blob until the operator re-saves through the new path; first operative save creates the artifact row.
8. **Explicit non-goals** — No coat-check ([AST-1572](https://linear.app/astralcareermatch/issue/AST-1572)). No new craft task. No job/company catalog keys. No other context leaves (priorities, deal_breakers, ideal_day, writing_preferences). No new body shape.

## Component scope

* `src/utils/config.py` — **modified** — `ARTIFACT_CONFIG["candidate.context.backstory"]` plus asserts; reuse existing `BUILD_CONFIG["artifact_shapes"]["plain_text"]`; `TOKEN_SOURCES["BACKSTORY"]` → `artifact` plus `artifact_key`; drop `candidate.context.backstory` from the sibling-freeze assert list that currently requires it absent.
* `src/core/candidate.py` — **modified** — operative save validation for `plain_text` (reuse AST-1629 path); hydrate Backstory from `get_candidate_current` on GET paths; gate durable library writes for `context.backstory`.
* `src/ui/api/api_candidate.py` — **modified** — PUT intercept: strip library `context.backstory`, call operative save; GET hydrate overlays current Backstory string.
* `src/ui/frontend/src/pages/CandidateBackstory.tsx` — **modified** — Backstory-only; mirror `CandidateStrengths.tsx` ContextTextPage props (`bodyShape="plain_text"`).
* `src/ui/frontend/src/components/ContextTextPage.tsx` — **untouched** — already parameterized by AST-1629; Backstory is a new consumer.
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — **untouched**.
* `src/data/database.py` — **untouched** — existing `save_artifact` / `get_current_artifact` primitives only.

## Technical scope

* `src/utils/config.py` — Catalog entry: `entity_type: "candidate"`, `candidate_scoped: True`, `body_shape: "plain_text"`, `ingestion_owner: "candidate"`. Closed-set asserts include the new key and stop asserting Backstory absent. `TOKEN_SOURCES["BACKSTORY"]` gains `source_type: "artifact"` and `artifact_key: "candidate.context.backstory"`.
* `src/core/candidate.py` — Operative str-path validates `plain_text` (reuses AST-1629 validation); hydrate overlay writes current string into `context.backstory` for display; refuse durable library SoT write for that leaf when catalog owns it.
* `src/ui/api/api_candidate.py` — On PUT with Backstory: pop from library `context` merge, `save_candidate_data(candidate_id, "candidate.context.backstory", body)`; on GET hydrate current row into `context.backstory`.
* `src/ui/frontend/src/pages/CandidateBackstory.tsx` — Load/save only through the operative API contract via existing `ContextTextPage` with the same prop shape as Strengths; no parallel client storage key; no ArtifactEditor.

## Architectural definition

**Patterns to reuse** (same set as AST-1629 — copy those guidelines; no new patterns):

* `patt.artifact.manage-catalog` — register Backstory; retire blob authority for that key. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* `patt.artifact.write-operative` — Backstory saves via blind retire+insert through entity-owned operative save. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>)
* `patt.artifact.read-current` — UI/GET hydrate and live Backstory from current row. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>)
* `patt.artifact.read-operative` — pin to body remains available via generic path (no Backstory-only pin surface required). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-operative.md>)
* `patt.artifact.ui-consistency` — editor path follows catalog `body_shape` (`plain_text` → ContextTextPage, not resume_content ArtifactEditor). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.ui-consistency.md>)

**New patterns proposed:** none — Backstory reuses the existing `plain_text` shape and AST-1629 patterns as-is.

**Applicable statutes** (same set as AST-1629):

* `stat.logging.info` — info contracts on touched surfaces. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md>)
* `stat.logging.warning` — warning contracts on touched surfaces. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>)
* `stat.logging.error` — error contracts on touched surfaces. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>)
* `stat.logging.debug` — debug contract on any `debug=` surfaces this epic touches. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)
* `stat.logging.info.entity` — entity/core info logging when candidate paths change. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>)
* `stat.logging.info.api` — API info logging when api_candidate Backstory paths change. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>)
* `astral.config.config-source-of-truth` — catalog key, body_shape, and token typing live in config. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.standards.no-hardcoded-sets` — closed catalog / shape membership via config asserts. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
* `astral.standards.in-scope-only` — Backstory only. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* `astral.layers.import-direction` — utils/config + core + ui layering. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
* `astral.git.engineer-test-tree-ban` — engineers do not own `tests/` / bible. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md>)
* `astral.standards.logging-via-utils` — logging through utils helpers. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md>)

Note: Artifact `patt.artifact.*` ids remain under `draft/` until promoted; logging `stat.logging.*` are active. Comply with every active directive that applies to touched surfaces. Prefer AST-1629 child plans / issue docs as the implementation template.

## Acceptance criteria

1. **Catalog key present** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.backstory' in ARTIFACT_CONFIG"` exits 0. Fail: key absent or differently named without Description amendment.
2. **plain_text shape reused** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert ARTIFACT_CONFIG['candidate.context.backstory']['body_shape']=='plain_text'"` exits 0. Fail: Backstory bound to `resume_content` / `cover_letter`, or a new shape added.
3. **Token is artifact-typed** — `python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['BACKSTORY']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.backstory'"` exits 0. Fail: still `data_field` or wrong `artifact_key`.
4. **Operative round-trip** — Save Backstory via Backstory UI/API; `database.get_current_artifact('candidate', <id>, 'backstory')` returns a row whose `artifact_data` matches the saved string; a second save creates a new uuid and retires prior `current=1`. Fail: body only in library blob with no artifact row, or in-place UPDATE of same uuid.
5. **Blob not SoT on write** — Successful Backstory save calls operative `save_artifact`; does not rely on library-merge of `context.backstory` alone. Fail: PUT only deep-merges the blob.
6. **Editor reload** — Backstory page after save shows the same text. Fail: empty editor while a current artifact row exists.
7. **No backfill required** — Candidates with only legacy blob Backstory and no artifact row still load that blob (or empty) until re-save; no bulk migration job ships. Fail: epic adds a required one-shot migrate-all script as SoT.
8. **Sibling freeze** — `ARTIFACT_CONFIG` has no priorities/deal_breakers/ideal_day/writing_preferences keys. Fail: any of those registered. (Backstory itself is in the catalog after this epic.)
9. **UI path** — `CandidateBackstory.tsx` passes `bodyShape="plain_text"` into `ContextTextPage` (same shape as Strengths); `ArtifactEditor` diff for this ticket is empty. Fail: Backstory routed through ArtifactEditor / resume_content, or still missing `bodyShape`.

## Open questions

none

## Proposed child tickets

#### 1!!: **Catalog plus BACKSTORY token - Ada**

Register `candidate.context.backstory` in `ARTIFACT_CONFIG` reusing the existing `plain_text` shape, flip `TOKEN_SOURCES["BACKSTORY"]` to artifact plus `artifact_key`, lock startup asserts (including removing Backstory from the sibling-freeze absent list). Does not own UI or hydrate. Does not add a new body shape. Mirror AST-1632 guidelines for the catalog/token slice.
**Citations:** `patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `stat.logging.info` / `stat.logging.debug` as touched
**Scope:** `src/utils/config.py` — new catalog entry plus asserts; `TOKEN_SOURCES["BACKSTORY"]` flip; sibling-freeze list update for Backstory.
**Estimate: 1**

#### 2!: **Operative save, hydrate, blob retirement - Hedy**

Wire Backstory through candidate operative `plain_text` validation plus `get_candidate_current` hydrate on GET; intercept API PUT for operative save; stop durable library SoT writes for `context.backstory`. No backfill helper. Does not own React chrome. After #1. Mirror AST-1633 guidelines for the Strengths→Backstory leaf swap.
**Citations:** `patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.in-scope-only`; `stat.logging.info.entity`; `stat.logging.info.api`; `stat.logging.error`
**Scope:** `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.backstory`. `src/ui/api/api_candidate.py` — PUT intercept plus GET hydrate for Backstory.
**Estimate: 3**

#### 3: **Backstory ContextTextPage wire-up - Katherine**

Retarget Backstory-only UI to the operative API contract via existing `ContextTextPage`, matching `CandidateStrengths.tsx` (`bodyShape="plain_text"`). No ArtifactEditor. No sibling context pages. No ContextTextPage changes. After #1 (and API hydrate from #2 as needed). Mirror AST-1634 page-level wire-up only.
**Citations:** `patt.artifact.ui-consistency`; `patt.artifact.read-current`; `patt.artifact.write-operative`
**Scope:** `src/ui/frontend/src/pages/CandidateBackstory.tsx` — Backstory-only wire-up against existing ContextTextPage.
**Estimate: 2**

**Monolith check:** 8 functional capabilities → 3 children (config / core+API / UI), matching AST-1629's split.

**Scope partition check:** `config.py` → #1; `candidate.py` + `api_candidate.py` → #2; Backstory page → #3. `ContextTextPage.tsx`, `ArtifactEditor.tsx`, and `database.py` untouched / unclaimed by design.

---

## Original brief

Follow-on sibling to [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) (Strengths migration). `candidate_data.context.backstory` is still a plain library blob: no versioning, no `current` row, no pin, and `{$BACKSTORY}` resolves as a `data_field`. AST-1629 proved the artifact table + `ARTIFACT_CONFIG` path, plus the `plain_text` body shape, for Strengths. This ticket migrates **Backstory only** onto that same proven path.

### Functional scope (Archie)

1. **Catalog Backstory** — Register `candidate.context.backstory` in `ARTIFACT_CONFIG`, reusing the `plain_text` body shape added in [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table). No other context or artifact keys are added.
2. **Operative write** — Saving Backstory goes through candidate write-operative (`save_candidate_data(candidate_id, artifact_key, body)` → `database.save_artifact`). No in-place blob UPDATE.
3. **Current read / hydrate** — GET/UI loads Backstory via read-current and overlays the string onto `candidate_data.context.backstory` for the existing editor contract. Miss → empty editor.
4. **Retire blob authority** — Stop durable library-merge writes of `context.backstory` as source of truth; stop token/live assembly from reading the blob for Backstory after cutover.
5. **Token typing** — Flip `TOKEN_SOURCES["BACKSTORY"]` from `data_field` to `artifact` with `artifact_key: "candidate.context.backstory"`.
6. **UI path** — Keep Backstory on `ContextTextPage`, the shared plain-text artifact editor introduced in [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table). Do not extend `ArtifactEditor` / `resume_content` for this leaf.
7. **No legacy backfill** — Do not migrate historical `context.backstory` blobs in this ticket. Existing text stays in the blob until the operator re-saves through the new path; first operative save creates the artifact row.
8. **Explicit non-goals** — No coat-check ([AST-1572](https://linear.app/astralcareermatch/issue/AST-1572/implement-pattartifactno-coat-check)). No new craft task. No job/company catalog keys. No other context leaves (priorities, deal_breakers, ideal_day, writing_preferences).

### Notes (Archie)

Copies the pattern established in [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) (Strengths) — same catalog / operative-save / hydrate / token-typing / UI shape, applied to the Backstory field instead. Related to [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table). Claude Fable (2026-09-15): do not rederive from scratch — use [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) implementation guidelines.

### Comments

#### chuckles — 2026-09-16T02:04:35.472Z
AST-1663 REVIEW — Radia fix-now: strip AST-1667 orphan tests/bible from publish ref before merge.

#### chuckles — 2026-09-16T01:42:27.867Z
AST-1662 REVIEW — merge-child blocked; recalling @Betty White for duplicate merge-tests(AST-1662) on the publish ref.

#### chuckles — 2026-09-16T01:31:28.505Z
AST-1662 REVIEW — Radia FIX-NOW: tip drops Writing Preferences catalog/operative vs origin/dev; Hedy must union backstory+ideal_day+writing_preferences before UT.

#### chuckles — 2026-09-16T01:19:38.820Z
AST-1662 — Betty scope gate: plan is Backstory-only; recalling @Hedy Lamarr to strip Writing Preferences operative bits from the publish-ref and re-Code Complete (no plan revise).

#### chuckles — 2026-09-16T01:05:40.550Z
[refresh-ftr] blocked: Ideal Day ∪ Backstory merge into origin/ftr/AST-1644-migrate-backstory-artifact-table
Conflicts:
- src/utils/config.py — @Ada Lovelace (union both leaves; do not drop Ideal Day or Backstory)
- docs/test-bible/utils/config.md, tests/component/utils/test_config.py, tests/component/core/test_candidate.py, tests/component/ui/api/test_api_candidate.py — @Betty White
Worktree with conflicted merge: /home/susan/astral-AST-1644-ftr-refresh (branch tmp-ftr-refresh-1644). Resolve, commit merge, push origin HEAD:ftr/AST-1644-migrate-backstory-artifact-table.

#### hedy — 2026-09-16T01:04:39.312Z
🛑 Stage 1 blocked: catalog sibling not on tip (ftr sync blocked by test-tree ban)

Step: Catalog prerequisite — `candidate.context.backstory` must be in `ARTIFACT_CONFIG` before Stage 1 verify.

Issue: Spawn `sync-child --ftr AST-1644` skips (short segment missing). Registry `parent_ftr` is `ftr/AST-1644-migrate-backstory-artifact-table` (AST-1661 UT). Merging that ftr onto tip (already has Ideal Day from `origin/dev`) conflicts in `src/utils/config.py` + Betty paths (`tests/component/utils/test_config.py`, `docs/test-bible/utils/config.md`, candidate/API tests). Config union is engineer-ok; committing the merge with resolved Betty files is blocked by the engineer pre-commit test-tree ban.

Proposed resolutions:
1. Chuckles: land/resolve the Ideal Day ∪ Backstory ftr merge (or re-seed `origin/ftr/AST-1644-migrate-backstory-artifact-table` already unioned with `origin/dev`) so `sync-child --ftr AST-1644-migrate-backstory-artifact-table` is clean for this sub.
2. Betty: resolve the Betty-side conflict files on this publish-ref sync merge, then Hedy resumes build-child.
3. Need guidance — do not invent catalog registration on AST-1662 (Ada owns `config.py` for Backstory).

#### chuckles — 2026-09-16T00:54:35.155Z
AST-1663 STALE(dev+55) — pausing AST-1662 build until Katherine refreshes sub (merge origin/dev + origin/ftr/AST-1644 + republish). @Katherine Johnson

#### chuckles — 2026-09-16T00:29:30.672Z
AST-1661 REVIEW — merge-child blocked; recalling @Betty White for duplicate merge-tests(AST-1661) on the publish ref.

#### chuckles — 2026-09-16T00:21:23.530Z
AST-1661 REVIEW — Radia needs resolve: AST-1659 Ideal Day tests/bible landed on the Backstory catalog publish ref.

#### chuckles — 2026-09-15T22:13:14.953Z
@susan Dispatch blocked — `## Proposed child tickets` is missing the mechanical `#### <seq><bangs>: **Title - Assignee**` headers (and per-block assignee). Ticket A/B/C prose is present with Citations/Scope/deps, but `dispatch-parent` cannot create children without the `####` form.

Please paste (or rewrite) something like this under `## Proposed child tickets`, pick Ada/Hedy/Katherine per child, then Todo + Chuckles again:

#### 1!: **Catalog plus plain_text shape reuse plus BACKSTORY token - <dev>**
Register `candidate.context.backstory` in `ARTIFACT_CONFIG` reusing the existing `plain_text` shape, flip `TOKEN_SOURCES["BACKSTORY"]` to artifact plus `artifact_key`, lock startup asserts. Does not own UI or hydrate.
Citations: `patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `stat.logging.info` / `stat.logging.debug` as touched.
Scope: `src/utils/config.py` — new catalog entry plus asserts; `TOKEN_SOURCES["BACKSTORY"]` flip.
Estimate: 1

#### 2: **Operative save, hydrate, blob retirement - <dev>**
Wire Backstory through candidate operative `plain_text` validation plus `get_candidate_current` hydrate on GET; intercept API PUT for operative save; stop durable library SoT writes for `context.backstory`. No backfill helper. Does not own React chrome. After #1.
Citations: `patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.in-scope-only`; `stat.logging.info.entity`; `stat.logging.info.api`; `stat.logging.error`.
Scope: `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.backstory`. `src/ui/api/api_candidate.py` — PUT intercept plus GET hydrate for Backstory.
Estimate: 3

#### 3: **Backstory ContextTextPage wire-up - <dev>**
Retarget Backstory-only UI load/save to the operative API contract via existing `ContextTextPage`. No ArtifactEditor. No sibling context pages. After #1; API hydrate from #2 as needed.
Citations: `patt.artifact.ui-consistency`; `patt.artifact.read-current`; `patt.artifact.write-operative`.
Scope: `src/ui/frontend/src/pages/CandidateBackstory.tsx` — Backstory-only wire-up against existing ContextTextPage.
Estimate: 2

---

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/ea61515142013a8c685014866bc1c6f5/452028ba-5a42-44c8-a3b4-8a976c598e9d/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/ea61515142013a8c685014866bc1c6f5/0ea1c373-2ab0-418c-8ed5-b2735bae4455/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/ea61515142013a8c685014866bc1c6f5/6b92ba86-b404-4f55-8e6b-7b0bceef8303/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/d096fa09-b56f-41d1-b9c0-425e13d79db1/store.db` |
| Radia | review | `/home/susan/.cursor/chats/ea61515142013a8c685014866bc1c6f5/c74ea9e2-84c7-40b4-9cdc-7a611cf926cb/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1644 (parent) | ftr/AST-1644-migrate-backstory-artifact-table |
| AST-1661 | sub/AST-1644/AST-1661-catalog-plus-backstory-token |
| AST-1662 | sub/AST-1644/AST-1662-operative-save-hydrate-blob-retirement |
| AST-1663 | sub/AST-1644/AST-1663-backstory-contexttextpage-wire-up |

**Epic worktree:** `astral-AST-1644/` — one active sub checked out at a time.
