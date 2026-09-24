# AST-1629 — Migrate candidate_data.context.strengths to use the artifact table

<!-- linear-archive: AST-1629 archived 2026-09-24 -->

## Linear archive (AST-1629)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1629/migrate-candidate-datacontextstrengths-to-use-the-artifact-table  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1572; related: AST-1583

### Description

## Purpose

`candidate_data.context.strengths` is still a plain library blob: no versioning, no `current` row, no pin, and `{$STRENGTHS}` resolves as a `data_field`. The artifact table + `ARTIFACT_CONFIG` path already works for `candidate.artifacts.base_resume`. This epic migrates **Strengths only** onto that path so later context-field migrations (priorities, deal_breakers, etc.) copy a proven slice — not a second special case.

## Functional scope

1. **Catalog Strengths** — Register one new `ARTIFACT_CONFIG` key `candidate.context.strengths` (hierarchical `_data` path per AST-1575). No other context or artifact keys are added.
2. **Plain-text body shape** — Add `BUILD_CONFIG["artifact_shapes"]["plain_text"]` as a **raw string** body contract (not a one-field dict; not `resume_content`). Strengths is the first catalog key that uses it; sibling context migrations reuse the same shape later.
3. **Operative write** — Saving Strengths goes through candidate write-operative (`save_candidate_data(candidate_id, artifact_key, body)` → `database.save_artifact`). No in-place blob UPDATE; no craft-specific persist helper.
4. **Current read / hydrate** — GET/UI loads Strengths via read-current and overlays the string onto `candidate_data.context.strengths` for the existing editor contract. Miss → empty editor. No coat-check.
5. **Retire blob authority** — Stop durable library-merge writes of `context.strengths` as SoT; stop token/live assembly from reading the blob for Strengths after cutover.
6. **Token typing** — Flip `TOKEN_SOURCES["STRENGTHS"]` from `data_field` to `artifact` with `artifact_key: "candidate.context.strengths"`.
7. **UI path** — Keep Strengths on `ContextTextPage` as the shared plain-text artifact editor (parameterize for operative hydrate/save). Do not extend `ArtifactEditor` / `resume_content` for this leaf.
8. **No legacy backfill** — Do not migrate historical `context.strengths` blobs in this epic. Existing text stays in the blob until the operator re-saves through the new path; first operative save creates the artifact row.
9. **Explicit non-goals** — No coat-check ([AST-1572](https://linear.app/astralcareermatch/issue/AST-1572)). No new craft task. No job/company catalog keys. No other context leaves (priorities, deal_breakers, backstory, ideal_day, writing_preferences). No [AST-1583](https://linear.app/astralcareermatch/issue/AST-1583) field-list decision.

## Component scope

* `src/utils/config.py` — **modified** — `ARTIFACT_CONFIG["candidate.context.strengths"]` + asserts; `BUILD_CONFIG["artifact_shapes"]["plain_text"]` raw-string contract; `TOKEN_SOURCES["STRENGTHS"]` → `artifact` + `artifact_key`.
* `src/core/candidate.py` — **modified** — operative save validation for `plain_text`; hydrate Strengths from `get_candidate_current` on GET paths; gate durable library writes for `context.strengths`.
* `src/ui/api/api_candidate.py` — **modified** — PUT intercept: strip library `context.strengths`, call operative save; GET hydrate overlays current Strengths string.
* `src/ui/frontend/src/pages/CandidateStrengths.tsx` — **modified** — Strengths-only; stay on ContextTextPage path.
* `src/ui/frontend/src/components/ContextTextPage.tsx` — **modified** — shared plain-text artifact editor wiring (load/save via API contract that lands operative rows / hydrate leaf).
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — **untouched**.
* `src/data/database.py` — **untouched** — existing `save_artifact` / `get_current_artifact` primitives only.

## Technical scope

* `src/utils/config.py` — Catalog entry: `entity_type: "candidate"`, `candidate_scoped: True`, `body_shape: "plain_text"`, `ingestion_owner: "candidate"`. Closed-set asserts include the new key. `artifact_shapes["plain_text"]` documents a raw string body. `TOKEN_SOURCES["STRENGTHS"]` gains `source_type: "artifact"` and `artifact_key: "candidate.context.strengths"`.
* `src/core/candidate.py` — Operative str-path validates `plain_text` (non-empty/string rules as plan chooses under statute); hydrate overlay writes current string into `context.strengths` for display; refuse durable library SoT write for that leaf when catalog owns it.
* `src/ui/api/api_candidate.py` — On PUT with Strengths: pop from library `context` merge, `save_candidate_data(candidate_id, "candidate.context.strengths", body)`; on GET hydrate current row into `context.strengths`.
* `src/ui/frontend/src/pages/CandidateStrengths.tsx` + `ContextTextPage.tsx` — Load/save only through that API contract; no parallel client storage key; no ArtifactEditor.

## Architectural definition

**Patterns to reuse**

* `patt.artifact.manage-catalog` — register Strengths; retire blob authority for that key. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* `patt.artifact.write-operative` — Strengths saves via blind retire+insert through entity-owned operative save. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>)
* `patt.artifact.read-current` — UI/GET hydrate and live Strengths from current row. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-current.md>)
* `patt.artifact.read-operative` — pin→body remains available via generic path (no Strengths-only pin surface required). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.read-operative.md>)
* `patt.artifact.ui-consistency` — editor path follows catalog `body_shape` (`plain_text` → ContextTextPage, not resume_content ArtifactEditor). [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.ui-consistency.md>)

**New patterns proposed**

* none — new `plain_text` shape is config catalog data under manage-catalog, not a new pattern id.

**Applicable statutes** (active folder + product statutes still under `canon/statutes/`)

* `stat.logging.info` — info contracts on touched surfaces. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md>)
* `stat.logging.warning` — warning contracts on touched surfaces. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>)
* `stat.logging.error` — error contracts on touched surfaces. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>)
* `stat.logging.debug` — debug contract on any `debug=` surfaces this epic touches. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)
* `stat.logging.info.entity` — entity/core info logging when candidate paths change. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>)
* `stat.logging.info.api` — API info logging when api_candidate Strengths paths change. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>)
* `astral.config.config-source-of-truth` — catalog key, body_shape, and token typing live in config. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.standards.no-hardcoded-sets` — closed catalog / shape membership via config asserts. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
* `astral.standards.in-scope-only` — Strengths only. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* `astral.layers.import-direction` — utils/config + core + ui layering. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
* `astral.git.engineer-test-tree-ban` — engineers do not own `tests/` / bible. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/git/astral.git.engineer-test-tree-ban.md>)
* `astral.standards.logging-via-utils` — logging through utils helpers. [https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md>)

Note: `canon/directives/active/` is present on origin/dev. Artifact `patt.artifact.*` ids remain under `draft/` until promoted; logging `stat.logging.*` are active. Comply with every active directive that applies to touched surfaces.

## Acceptance criteria

1. **Catalog key present** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.strengths' in ARTIFACT_CONFIG"` exits 0. Fail: key absent or differently named without Description amendment.
2. **plain_text shape** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG, BUILD_CONFIG; assert ARTIFACT_CONFIG['candidate.context.strengths']['body_shape']=='plain_text'; assert 'plain_text' in BUILD_CONFIG['artifact_shapes']"` exits 0. Fail: missing shape or Strengths bound to `resume_content` / `cover_letter`.
3. **Token is artifact-typed** — `python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['STRENGTHS']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.strengths'"` exits 0. Fail: still `data_field` or wrong `artifact_key`.
4. **Operative round-trip** — Save Strengths via Strengths UI/API; `database.get_current_artifact('candidate', <id>, 'strengths')` returns a row whose `artifact_data` matches the saved string; a second save creates a new uuid and retires prior `current=1`. Fail: body only in library blob with no artifact row, or in-place UPDATE of same uuid.
5. **Blob not SoT on write** — Successful Strengths save calls operative `save_artifact`; does not rely on library-merge of `context.strengths` alone. Fail: PUT only deep-merges the blob.
6. **Editor reload** — Strengths page after save shows the same text. Fail: empty editor while a current artifact row exists.
7. **No backfill required** — Candidates with only legacy blob Strengths and no artifact row still load that blob (or empty) until re-save; no bulk migration job ships. Fail: epic adds a required one-shot migrate-all script as SoT.
8. **Sibling freeze** — `ARTIFACT_CONFIG` has no priorities/deal_breakers/backstory/ideal_day/writing_preferences keys. Fail: any of those registered.
9. **UI path** — Strengths still uses ContextTextPage (or a thin wrapper of it); `ArtifactEditor` diff for this epic is empty. Fail: Strengths forced through resume_content ArtifactEditor.

## Open questions

none

## Proposed child tickets

#### 1!!: **Catalog + plain_text shape + STRENGTHS token - Ada**

Register `candidate.context.strengths` in `ARTIFACT_CONFIG` with `body_shape: "plain_text"`, add `BUILD_CONFIG["artifact_shapes"]["plain_text"]` (raw string), flip `TOKEN_SOURCES["STRENGTHS"]` to artifact + `artifact_key`, lock startup asserts. Does not own UI or hydrate.
**Citations:** `patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `stat.logging.info` / `stat.logging.debug` as touched
**Scope:** `src/utils/config.py` — new catalog entry + asserts; `plain_text` artifact_shapes entry; `TOKEN_SOURCES["STRENGTHS"]` flip.
**Estimate: 2**

#### 2!: **Operative save, hydrate, blob retirement - Hedy**

Wire Strengths through candidate operative `plain_text` validation + `get_candidate_current` hydrate on GET; intercept API PUT for operative save; stop durable library SoT writes for `context.strengths`. No backfill helper. Does not own React chrome. After #1.
**Citations:** `patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.in-scope-only`; `stat.logging.info.entity`; `stat.logging.info.api`; `stat.logging.error`
**Scope:** `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.strengths`. `src/ui/api/api_candidate.py` — PUT intercept + GET hydrate for Strengths.
**Estimate: 5**

#### 3: **Strengths ContextTextPage plain-text path - Katherine**

Retarget Strengths-only UI load/save to the operative API contract via `ContextTextPage` (shared plain-text editor for future context migrations). No ArtifactEditor. No sibling context pages. After #1 (and API hydrate from #2 as needed).
**Citations:** `patt.artifact.ui-consistency`; `patt.artifact.read-current`; `patt.artifact.write-operative`
**Scope:** `src/ui/frontend/src/pages/CandidateStrengths.tsx` — Strengths-only wire-up. `src/ui/frontend/src/components/ContextTextPage.tsx` — plain-text artifact editor parameterization.
**Estimate: 3**

**Monolith check:** 8 functional capabilities → 3 children (config / core+API / UI). Intentional split matching base_resume catalog → operative → UI.

**Scope partition check:** [config.py](<http://config.py>) → #1; [candidate.py](<http://candidate.py>) + api_candidate.py → #2; Strengths page + ContextTextPage → #3. ArtifactEditor and [database.py](<http://database.py>) untouched / unclaimed by design.

---

## Original brief

Update the code base to support Strengths in the artifacts table.  Nothing else.  The scope of this ticket will inform other migrations to the artifact table.

All the changes must comply with all the directives in the canon/directives/active folder explicitly, as well as our existing general code standards.

### Comments

#### chuckles — 2026-09-15T00:53:15.801Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-1635** | Do not save a new artifact version when body is identical to current (Migrate candidate_data.context.strengths to use the artifact table) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-1635** — _Do not save a new artifact version when body is identical to current (Migrate candidate_data.context.strengths to use the artifact table)_
- **Quick check:** re-run the failure you reported for **AST-1635**.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### chuckles — 2026-09-15T00:38:03.238Z
[fix-intake] filed AST-1635 at Discussion (assignee Susan) for Susan UAT [bug] — identical-body skip on operative save. Parent stays User Testing / Chuckles.

#### susan — 2026-09-15T00:35:47.854Z
\[bug\]

Do not save a new version of the artifact if it is identical to the current version.

#### chuckles — 2026-09-14T21:20:57.333Z
[check-linear] answered — recommend new plain-string body_shape (see thread reply)

#### chuckles — 2026-09-14T21:20:56.360Z
[check-linear] answered — recommend a new plain-string body_shape, not resume_content

**Recommendation: define a new `body_shape` for a single string blob** (name TBD in OQ2 — e.g. `plain_text` / `free_text`). Do **not** extend `resume_content` / its free_prose section handling for Strengths.

Why:
1. **`free_prose` is a resume *section format***, not an artifact body_shape — it lives under structure-driven section ids inside a `resume_content` dict.
2. **`resume_content` is a multi-key section catalog** (required keys, experience modules, structure tabs). Strengths is one opaque string under `context.strengths` — forcing it into that shape invents fake sections or special-cases the validator.
3. **This epic is the template for other context migrations** (priorities, deal_breakers, …). A shared plain-string shape + `ContextTextPage` (or equivalent) is the reusable path; bolting onto resume_content would not transfer.

So: new shape for one string body; keep `resume_content` for resumes only. @susan

#### fable — 2026-09-14T21:19:31.774Z
@Chuckles Cursor — do you recommend we extend the free_prose-style handling used inside resume_content to support a single blob string shape, like what we're seeing with Strengths, rather than defining an entirely new body_shape?

#### chuckles — 2026-09-14T21:18:09.503Z
[check-linear] answered — existing body_shapes are resume_content + cover_letter only

Yes, the catalog already has a **body_shape** concept (`ARTIFACT_CONFIG[*]["body_shape"]` → `BUILD_CONFIG["artifact_shapes"]`). Today only two shapes are implemented:

1. **`resume_content`** — section dict (includes free_prose-style string sections **and** structured modules like experience `experience_jobs`). Used by `candidate.artifacts.base_resume` and `job.artifacts.job_resume`.
2. **`cover_letter`** — Subject / Letter / optional signature dict. Used by `job.artifacts.cover_letter`.

There is **no** plain-string / free-text-only shape yet. Strengths today is a raw string under `context.strengths`, so it does **not** reuse `resume_content` or `cover_letter` cleanly — OQ2 is still choosing a new shape (or a wrap) rather than picking an existing type. @susan

#### fable — 2026-09-14T21:17:24.321Z
@Chuckles Cursor — question on OQ2 before we lock the body shape: have we already implemented the idea of an artifact "type" concept (e.g. something like the resume sections type that supports both free text and experience modules)? If so, what types are currently implemented? Want to know if Strengths can reuse an existing type rather than defining a new one-off shape.

#### chuckles — 2026-09-14T20:51:02.040Z
[check-linear] answered — logging statutes added to Canon Scope

Folded active `stat.logging.*` (info / warning / error / debug + info.entity / info.api) into **Architectural definition → Applicable statutes** on this Description. Implementers will score against them with the artifact patterns.

#### chuckles — 2026-09-14T20:49:57.765Z
@susan

Dispatch blocked — Open questions still unresolved in the Description:

- **OQ1 (canon active/)** — resolved in-thread: `canon/directives/active/` is on origin/dev after refresh. Please remove or mark answered in `## Open questions`.
- **OQ2 (body shape + UI path)** — still open: (a) `BUILD_CONFIG["artifact_shapes"]` name and raw string vs one-field dict; (b) `ContextTextPage` vs `ArtifactEditor` for Strengths.
- **OQ3 (legacy backfill)** — still open: migrate existing `context.strengths` blobs this epic, or operative-only on re-save.

Need OQ2 + OQ3 answered (and OQ1 cleared from the list), then Todo + assignee Chuckles again.

#### fable — 2026-09-14T20:49:49.549Z
@Chuckles Cursor — when you implement this, make sure the statutes about logging are also incorporated as part of the code change.

#### chuckles — 2026-09-14T20:47:59.091Z
[check-linear] answered — refreshed; `canon/directives/active/` is on origin/dev

Confirmed after `sync-child` / fetch: `origin/dev` has `canon/directives/active/` (and local `dev` matches). OQ1 on this ticket was wrong about absence — Canon Scope should use active-folder ids, not draft-only. @susan

#### fable — 2026-09-14T20:06:12.696Z
@Chuckles Cursor — heads up, you may be looking at an older version of the dev branch. Please refresh from origin dev, since origin dev should absolutely have an active directory of Canon directives.

#### chuckles — 2026-09-14T19:55:40.419Z
@susan

1. **`canon/directives/active/` is absent** on origin/dev (only `canon/directives/draft/` plus legacy `canon/patterns` / `canon/statutes`; no `canon_clerk.py`). Your brief requires active-folder compliance. Confirm we lock Canon Scope to the draft `patt.artifact.*` ids listed in the Description (same as base_resume epics), or name the in-force ids / folder you want instead.

2. **Body shape for Strengths** — today the leaf is a plain string. Confirm: (a) new `BUILD_CONFIG["artifact_shapes"]` name + whether the stored body is a raw string vs a one-field dict; (b) UI path — keep `ContextTextPage` as the shared plain-text artifact editor for Strengths (template for later context pages), or extend `ArtifactEditor`.

3. **Legacy backfill** — one-time migrate existing non-empty `candidate_data.context.strengths` into artifact rows in this epic, or leave historical blobs until the operator re-saves (UI/API writes go operative only going forward)?

#### chuckles — 2026-09-14T19:55:28.279Z
1. **`canon/directives/active/` is absent** on origin/dev (only `canon/directives/draft/` plus legacy `canon/patterns` / `canon/statutes`; no `canon_clerk.py`). Your brief requires active-folder compliance. Confirm we lock Canon Scope to the draft `patt.artifact.*` ids listed in the Description (same as base_resume epics), or name the in-force ids / folder you want instead.

2. **Body shape for Strengths** — today the leaf is a plain string. Confirm: (a) new `BUILD_CONFIG["artifact_shapes"]` name + whether the stored body is a raw string vs a one-field dict; (b) UI path — keep `ContextTextPage` as the shared plain-text artifact editor for Strengths (template for later context pages), or extend `ArtifactEditor`.

3. **Legacy backfill** — one-time migrate existing non-empty `candidate_data.context.strengths` into artifact rows in this epic, or leave historical blobs until the operator re-saves (UI/API writes go operative only going forward)?

---

_Implementation detail may live in git history on `origin/dev`._
