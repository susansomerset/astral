# AST-1643 — Migrate candidate_data.context.ideal_day to use the artifact table

<!-- linear-archive: AST-1643 archived 2026-09-24 -->

## Linear archive (AST-1643)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1643/migrate-candidate-datacontextideal-day-to-use-the-artifact-table  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / 5  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1572

### Description

## Purpose

Follow-on sibling to [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) (Strengths migration). `candidate_data.context.ideal_day` is still a plain library blob: no versioning, no `current` row, no pin, and `{$IDEAL_DAY}` resolves as a `data_field`. AST-1629 proved the artifact table + `ARTIFACT_CONFIG` path, plus the `plain_text` body shape, for Strengths. This ticket migrates **Ideal Day only** onto that same proven path — copy the pattern, do not rederive a second special case.

## Functional scope

1. **Catalog Ideal Day** — Register `candidate.context.ideal_day` in `ARTIFACT_CONFIG`, reusing the `plain_text` body shape added in AST-1629. No other context or artifact keys are added.
2. **Operative write** — Saving Ideal Day goes through candidate write-operative (`save_candidate_data` → `database.save_artifact`). No in-place blob UPDATE.
3. **Current read / hydrate** — GET/UI loads Ideal Day via read-current and overlays the string onto `candidate_data.context.ideal_day` for the existing editor contract. Miss → empty editor.
4. **Retire blob authority** — Stop durable library-merge writes of `context.ideal_day` as source of truth; stop token/live assembly from reading the blob for Ideal Day after cutover.
5. **Token typing** — Flip `TOKEN_SOURCES["IDEAL_DAY"]` from `data_field` to `artifact` with `artifact_key: "candidate.context.ideal_day"`.
6. **UI path** — Keep Ideal Day on `ContextTextPage`, the shared plain-text artifact editor from AST-1629. Do not extend `ArtifactEditor` / `resume_content` for this leaf.
7. **No legacy backfill** — Do not migrate historical `context.ideal_day` blobs. Existing text stays in the blob until the operator re-saves through the new path; first operative save creates the artifact row.
8. **Explicit non-goals** — No coat-check. No new craft task. No job/company catalog keys. No other context leaves (priorities, deal_breakers, backstory, writing_preferences).

## Component scope

* `src/utils/config.py` — **modified** — `ARTIFACT_CONFIG["candidate.context.ideal_day"]` plus asserts; reuses existing `BUILD_CONFIG["artifact_shapes"]["plain_text"]` raw-string contract from AST-1629; `TOKEN_SOURCES["IDEAL_DAY"]` becomes `artifact` plus `artifact_key`.
* `src/core/candidate.py` — **modified** — operative save validation for `plain_text` (reused path); hydrate Ideal Day from `get_candidate_current` on GET paths; gate durable library writes for `context.ideal_day`.
* `src/ui/api/api_candidate.py` — **modified** — PUT intercept: strip library `context.ideal_day`, call operative save; GET hydrate overlays current Ideal Day string.
* `src/ui/frontend/src/pages/CandidateIdealDay.tsx` — **modified** — Ideal Day-only; stay on ContextTextPage path.
* `src/ui/frontend/src/components/ContextTextPage.tsx` — **untouched** — shared plain-text artifact editor already parameterized by AST-1629; Ideal Day is a new consumer, not a new wiring change.
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — **untouched**.
* `src/data/database.py` — **untouched** — existing `save_artifact` / `get_current_artifact` primitives only.

## Technical scope

* `src/utils/config.py` — Catalog entry: `entity_type: "candidate"`, `candidate_scoped: True`, `body_shape: "plain_text"`, `ingestion_owner: "candidate"`. Closed-set asserts include the new key; remove it from the sibling-freeze-out list. `TOKEN_SOURCES["IDEAL_DAY"]` gains `source_type: "artifact"` and `artifact_key: "candidate.context.ideal_day"`.
* `src/core/candidate.py` — Operative str-path validates `plain_text` (reuses AST-1629 validation, no new rules); hydrate overlay writes current string into `context.ideal_day` for display; refuse durable library SoT write for that leaf when catalog owns it.
* `src/ui/api/api_candidate.py` — On PUT with Ideal Day: pop from library `context` merge, `save_candidate_data(candidate_id, "candidate.context.ideal_day", body)`; on GET hydrate current row into `context.ideal_day`.
* `src/ui/frontend/src/pages/CandidateIdealDay.tsx` — Load/save only through the operative API contract via existing `ContextTextPage`; no parallel client storage key; no ArtifactEditor.

## Architectural definition

**Patterns to reuse**

* `patt.artifact.manage-catalog` — register Ideal Day; retire blob authority for that key. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* `patt.artifact.write-operative` — Ideal Day saves via blind retire+insert through entity-owned operative save. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>)
* `patt.artifact.read-current` — UI/GET hydrate and live Ideal Day from current row. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>)
* `patt.artifact.read-operative` — pin→body remains available via generic path (no Ideal Day-only pin surface required). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-operative.md>)
* `patt.artifact.ui-consistency` — editor path follows catalog `body_shape` (`plain_text` → ContextTextPage, not resume_content ArtifactEditor). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.ui-consistency.md>)

**New patterns proposed**

* none — Ideal Day reuses the `plain_text` shape and all patterns as-is; this is config catalog data under manage-catalog, not a new pattern id.

**Applicable statutes** (active folder + product statutes still under `canon/statutes/`)

* `stat.logging.info` — info contracts on touched surfaces. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md>)
* `stat.logging.warning` — warning contracts on touched surfaces. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>)
* `stat.logging.error` — error contracts on touched surfaces. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>)
* `stat.logging.debug` — debug contract on any `debug=` surfaces this epic touches. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)
* `stat.logging.info.entity` — entity/core info logging when candidate paths change. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>)
* `stat.logging.info.api` — API info logging when api_candidate Ideal Day paths change. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>)
* `astral.config.config-source-of-truth` — catalog key, body_shape, and token typing live in config. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.standards.no-hardcoded-sets` — closed catalog / shape membership via config asserts. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
* `astral.standards.in-scope-only` — Ideal Day only. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* `astral.layers.import-direction` — utils/config + core + ui layering. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
* `astral.git.engineer-test-tree-ban` — engineers do not own `tests/` / bible. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md>)
* `astral.standards.logging-via-utils` — logging through utils helpers. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md>)

Note: `canon/directives/active/` is present on origin/dev. Artifact `patt.artifact.*` ids remain under `draft/` until promoted; logging `stat.logging.*` are active. Comply with every active directive that applies to touched surfaces. Sibling context migrations queued or in flight: AST-1641 (priorities), AST-1642 (deal_breakers), AST-1644 (backstory), AST-1645 (writing_preferences) — this epic must not register those keys.

## Acceptance criteria

1. **Catalog key present** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.ideal_day' in ARTIFACT_CONFIG"` exits 0. Fail: key absent or differently named without Description amendment.
2. **plain_text shape reused** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG, BUILD_CONFIG; assert ARTIFACT_CONFIG['candidate.context.ideal_day']['body_shape']=='plain_text'; assert 'plain_text' in BUILD_CONFIG['artifact_shapes']"` exits 0. Fail: Ideal Day bound to `resume_content` / `cover_letter`, or a new shape added.
3. **Token is artifact-typed** — `python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['IDEAL_DAY']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.ideal_day'"` exits 0. Fail: still `data_field` or wrong `artifact_key`.
4. **Operative round-trip** — Save Ideal Day via Ideal Day UI/API; `database.get_current_artifact('candidate', <id>, 'ideal_day')` returns a row whose `artifact_data` matches the saved string; a second save creates a new uuid and retires prior `current=1`. Fail: body only in library blob with no artifact row, or in-place UPDATE of same uuid.
5. **Blob not SoT on write** — Successful Ideal Day save calls operative `save_artifact`; does not rely on library-merge of `context.ideal_day` alone. Fail: PUT only deep-merges the blob.
6. **Editor reload** — Ideal Day page after save shows the same text. Fail: empty editor while a current artifact row exists.
7. **No backfill required** — Candidates with only legacy blob Ideal Day and no artifact row still load that blob (or empty) until re-save; no bulk migration job ships. Fail: epic adds a required one-shot migrate-all script as SoT.
8. **Sibling freeze** — `ARTIFACT_CONFIG` has no priorities/deal_breakers/backstory/writing_preferences keys. Fail: any of those registered.
9. **UI path** — Ideal Day still uses ContextTextPage (or a thin wrapper of it); `ArtifactEditor` diff for this ticket is empty. Fail: Ideal Day forced through resume_content ArtifactEditor.

## Open questions

none

## Proposed child tickets

#### 1!!: **Catalog + plain_text shape reuse + IDEAL_DAY token - Ada**

Register `candidate.context.ideal_day` in `ARTIFACT_CONFIG` reusing the existing `plain_text` shape, flip `TOKEN_SOURCES["IDEAL_DAY"]` to artifact plus `artifact_key`, lock startup asserts (add key to closed set; remove from sibling-freeze-out list). Does not own UI or hydrate.
**Citations:** `patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `stat.logging.info` / `stat.logging.debug` as touched
**Scope:** `src/utils/config.py` — new catalog entry plus asserts; `TOKEN_SOURCES["IDEAL_DAY"]` flip.
**Estimate: 1**

#### 2!: **Operative save, hydrate, blob retirement - Hedy**

Wire Ideal Day through candidate operative `plain_text` validation plus `get_candidate_current` hydrate on GET; intercept API PUT for operative save; stop durable library SoT writes for `context.ideal_day`. No backfill helper. Does not own React chrome. After #1.
**Citations:** `patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.in-scope-only`; `stat.logging.info.entity`; `stat.logging.info.api`; `stat.logging.error`
**Scope:** `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.ideal_day`. `src/ui/api/api_candidate.py` — PUT intercept plus GET hydrate for Ideal Day.
**Estimate: 3**

#### 3: **Ideal Day ContextTextPage wire-up - Katherine**

Retarget Ideal Day-only UI load/save to the operative API contract via existing `ContextTextPage`. No ArtifactEditor. No sibling context pages. After #1 (and API hydrate from #2 as needed).
**Citations:** `patt.artifact.ui-consistency`; `patt.artifact.read-current`; `patt.artifact.write-operative`
**Scope:** `src/ui/frontend/src/pages/CandidateIdealDay.tsx` — Ideal Day-only wire-up against existing ContextTextPage.
**Estimate: 2**

Monolith check: 8 functional capabilities into 3 children (config / core+API / UI), matching AST-1629's split.

Scope partition check: `config.py` → #1; `candidate.py` + `api_candidate.py` → #2; `CandidateIdealDay.tsx` → #3. `ArtifactEditor.tsx`, `database.py`, and `ContextTextPage.tsx` untouched / unclaimed by design.

---

## Original brief

Follow-on sibling to [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) (Strengths migration). `candidate_data.context.ideal_day` is still a plain library blob: no versioning, no `current` row, no pin, and `{$IDEAL_DAY}` resolves as a `data_field`. [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) proved the artifact table + `ARTIFACT_CONFIG` path, plus the `plain_text` body shape, for Strengths. This ticket migrates **Ideal Day only** onto that same proven path.

### Functional scope (Archie)

1. **Catalog Ideal Day** — Register `candidate.context.ideal_day` in `ARTIFACT_CONFIG`, reusing the `plain_text` body shape added in [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table). No other context or artifact keys are added.
2. **Operative write** — Saving Ideal Day goes through candidate write-operative (`save_candidate_data(candidate_id, artifact_key, body)` → `database.save_artifact`). No in-place blob UPDATE.
3. **Current read / hydrate** — GET/UI loads Ideal Day via read-current and overlays the string onto `candidate_data.context.ideal_day` for the existing editor contract. Miss → empty editor.
4. **Retire blob authority** — Stop durable library-merge writes of `context.ideal_day` as source of truth; stop token/live assembly from reading the blob for Ideal Day after cutover.
5. **Token typing** — Flip `TOKEN_SOURCES["IDEAL_DAY"]` from `data_field` to `artifact` with `artifact_key: "candidate.context.ideal_day"`.
6. **UI path** — Keep Ideal Day on `ContextTextPage`, the shared plain-text artifact editor introduced in [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table). Do not extend `ArtifactEditor` / `resume_content` for this leaf.
7. **No legacy backfill** — Do not migrate historical `context.ideal_day` blobs in this ticket. Existing text stays in the blob until the operator re-saves through the new path; first operative save creates the artifact row.
8. **Explicit non-goals** — No coat-check ([AST-1572](https://linear.app/astralcareermatch/issue/AST-1572/implement-pattartifactno-coat-check)). No new craft task. No job/company catalog keys. No other context leaves (priorities, deal_breakers, backstory, writing_preferences).

### Notes (Archie)

Copies the pattern established in [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) (Strengths) — same catalog / operative-save / hydrate / token-typing / UI shape, applied to the Ideal Day field instead. Related to [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table). Claude Fable (2026-09-15): do not rederive from scratch — use [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table) implementation guidelines.

### Comments

#### chuckles — 2026-09-15T22:12:10.989Z
@susan Dispatch blocked — `## Proposed child tickets` is Ticket A/B/C prose, not `#### <seq><bangs>: **Title - Dev**` blocks with implementers. Citations/Scope bodies are fine; headers + assignees are missing (dispatch cannot invent Ada/Hedy/Katherine).

Paste something like this under `## Proposed child tickets` (edit assignees if wrong), move parent to Todo, assign Chuckles:

#### 1!!: **Catalog + plain_text shape reuse + IDEAL_DAY token - Ada**
Register `candidate.context.ideal_day` in `ARTIFACT_CONFIG` reusing the existing `plain_text` shape, flip `TOKEN_SOURCES["IDEAL_DAY"]` to artifact plus `artifact_key`, lock startup asserts. Does not own UI or hydrate.
Citations: `patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `stat.logging.info` / `stat.logging.debug` as touched.
Scope: `src/utils/config.py` — new catalog entry plus asserts; `TOKEN_SOURCES["IDEAL_DAY"]` flip.
Estimate: 1

#### 2!: **Operative save, hydrate, blob retirement - Hedy**
Wire Ideal Day through candidate operative `plain_text` validation plus `get_candidate_current` hydrate on GET; intercept API PUT for operative save; stop durable library SoT writes for `context.ideal_day`. No backfill helper. Does not own React chrome. Depends on Ticket A / after #1.
Citations: `patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.in-scope-only`; `stat.logging.info.entity`; `stat.logging.info.api`; `stat.logging.error`.
Scope: `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.ideal_day`. `src/ui/api/api_candidate.py` — PUT intercept plus GET hydrate for Ideal Day.
Estimate: 3

#### 3: **Ideal Day ContextTextPage wire-up - Katherine**
Retarget Ideal Day-only UI load/save to the operative API contract via existing `ContextTextPage`. No ArtifactEditor. No sibling context pages. Depends on Ticket A and API hydrate from Ticket B / after #1 and #2 as needed.
Citations: `patt.artifact.ui-consistency`; `patt.artifact.read-current`; `patt.artifact.write-operative`.
Scope: `src/ui/frontend/src/pages/CandidateIdealDay.tsx` — Ideal Day-only wire-up against existing ContextTextPage.
Estimate: 2

---

_Implementation detail may live in git history on `origin/dev`._
