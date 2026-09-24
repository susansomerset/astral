# AST-1569 — Implement patt.artifact.write-operative

<!-- linear-archive: AST-1569 archived 2026-09-24 -->

## Linear archive (AST-1569)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1569/implement-pattartifactwrite-operative  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / 8  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1572; blocks: AST-1571; blocks: AST-1570

### Description

## Purpose

Ship **write-operative** for the pilot catalog key `candidate.artifacts.base_resume`: entity-owned `candidate.save_candidate_data(candidate_id, artifact_key, blob)` calls `database.save_artifact` (blind retire of prior current by entity + type, insert new UUID current row, return id). Write surfaces — **UI** and `craft_resume_base` — use that generic call only (no craft-specific persist helpers). UI editors standardize on catalog **body shape** via new draft `patt.artifacts.ui-consistency`. No separate artifact component; delete `artifact_catalog` and read `ARTIFACT_CONFIG` from config.

## Functional scope

1. **Operative write** — Blind `UPDATE … SET current=0` for matching entity + artifact type, then insert new `current=1` UUID row; return that id. Do not look up the prior row’s id first. Never UPDATE bodies in place.
2. **Generic candidate save** — `save_candidate_data(candidate_id, artifact_key, blob)` reads `ARTIFACT_CONFIG[artifact_key]`, validates body shape, calls `save_artifact`, handles errors. Pass `candidate_id` whenever the call needs entity scope (pilot: entity is the candidate).
3. **Callers are generic** — Agent (and parse/UI) call `candidate.save_candidate_data(candidate_id, artifact_key, blob)` using the task’s config `artifact_key`. Remove craft/daisy-chain-specific persist helpers (`_persist_craft_dispatch_success` craft branches and related agent gunk) for this path — replace with that single generic call.
4. **Config** — `TASK_CONFIG["craft_resume_base"]["artifact_key"] = "candidate.artifacts.base_resume"`.
5. **UI consistency by shape** — Standardize base_resume edit on catalog `body_shape` (`resume_content`) under new draft `patt.artifacts.ui-consistency`. Do not cross-link that file from write-operative (names are intentional).
6. **Pilot editor hydrate** — Candidate loads current operative body via existing `get_current_artifact`. Full read-current product sweep remains [AST-1570](https://linear.app/astralcareermatch/issue/AST-1570).
7. **Remove** `artifact_catalog` — Delete the module; callers use `ARTIFACT_CONFIG` in config.
8. **Explicit non-goals** — No new catalog keys. No coat-check ([AST-1572](https://linear.app/astralcareermatch/issue/AST-1572)). No grade pin writers ([AST-1571](https://linear.app/astralcareermatch/issue/AST-1571)). No job `job_resume` / finalize-replica work this ticket. No denormalized blob mirror required on write. API response shape follows existing candidate-data conventions (no special-case ban or special-case expose of `artifact_id`).

## Component scope

* `src/data/database.py` — **modified** — `save_artifact`: blind retire-by-key + insert + return uuid; no new read helpers.
* `src/utils/artifact_catalog.py` — **deleted**.
* `src/utils/config.py` — **modified** — `craft_resume_base` `artifact_key`; keep `ARTIFACT_CONFIG`; drop catalog-helper coupling.
* `src/core/candidate.py` — **modified** — generic `save_candidate_data(candidate_id, artifact_key, blob)` → `save_artifact`; retarget parse + UI save; remove craft-specific persist helper for base_resume; hydrate via existing `get_current_artifact`.
* `src/core/agent.py` — **modified** — rewire craft persist: drop `_persist_craft_*` / `persist_candidate_craft_hops` gunk for operative artifact land; call `candidate.save_candidate_data(candidate_id, artifact_key, blob)` from task config.
* `src/ui/api/api_candidate.py` — **modified** — UI save uses candidate generic save for the pilot key; response follows normal candidate-data save conventions (today: return sanitized candidate after save — do not invent a one-off `artifact_id` field or a one-off ban).
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — **modified** — body-shape-driven pilot edit per ui-consistency.
* `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` — **modified** — wire page to that editor + save/hydrate.
* `tests/component/utils/test_artifact_catalog.py` (+ bible) — **deleted or retargeted** (Betty).
* `canon/directives/draft/patt.artifacts.ui-consistency.md` — **new**.
* `canon/directives/draft/patt.artifact.write-operative.md` — **untouched** for UI mandate (no cross-link).

## Technical scope

* `src/data/database.py` — Blind `UPDATE artifacts SET current=0 … WHERE entity_type/entity_id/artifact_type match`, then `INSERT` new uuid `current=1`; return new uuid. No prior-id lookup.
* `src/utils/config.py` — Set `TASK_CONFIG["craft_resume_base"]["artifact_key"] = "candidate.artifacts.base_resume"`. Metadata SoT remains `ARTIFACT_CONFIG["candidate.artifacts.base_resume"]`.
* `src/core/candidate.py` — Implement/repurpose `save_candidate_data(candidate_id, artifact_key, blob)`: resolve `ARTIFACT_CONFIG[artifact_key]`, validate `body_shape`, call `save_artifact` with catalog entity_type + leaf type + candidate_id as entity_id for the pilot. `parse_candidate_resume` and UI-facing save use this generic function (not blob dual-write / not snapshot helper).
* `src/core/agent.py` — Large rewire: remove craft-persist special case path that calls `_persist_craft_dispatch_success` for operative bodies; on success, read `artifact_key` from task config and call `candidate.save_candidate_data(index, artifact_key, blob)`. Strip daisy-chain-specific persist helpers that only existed to land craft blobs.
* `src/ui/api/api_candidate.py` — When save includes pilot body, call the generic candidate save; keep existing response pattern (`_sanitize_candidate` after save).
* Frontend — Parameterize by `body_shape`; save via candidate data API.
* Delete `artifact_catalog.py` + tests; add `patt.artifacts.ui-consistency.md` with no cross-links to write-operative.

## Architectural definition

**Patterns to reuse**

* `patt.artifact.write-operative` — data-layer + entity write path for the pilot. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.write-operative.md>)
* `patt.artifact.manage-catalog` — `ARTIFACT_CONFIG` in config is registration SoT; no Python accessor module. [draft on dev](<https://github.com/susansomerset/astral/blob/dev/canon/directives/draft/patt.artifact.manage-catalog.md>)
* **Supersede conflicting patterns:** Joan treats write-operative + `ARTIFACT_CONFIG` as authoritative for pilot writes; ui-consistency for shape-shared editors. Cite blob-only craft land, wrapper-module guidance, craft-specific persist helpers, one-off base_resume editor forks.

**New patterns proposed**

* `patt.artifacts.ui-consistency` — UI editors standardized on catalog `body_shape`; same-typed artifacts share components. Draft this ticket; Archie approval before active. **Do not** cross-link from write-operative.

**Applicable statutes**

* `astral.config.config-source-of-truth` — [config-source-of-truth](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.standards.no-hardcoded-sets` — [no-hardcoded-sets](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
* `astral.standards.in-scope-only` — [in-scope-only](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* `astral.standards.database-header-inventory` — [database-header-inventory](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.database-header-inventory.md>)
* `astral.standards.data-raises-caller-logs` — [data-raises-caller-logs](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.data-raises-caller-logs.md>)
* `astral.layers.import-direction` — [import-direction](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
* Universal set applies to product code.

## Acceptance criteria

1. Pilot writes use blind retire-by-key + insert new current uuid via `database.save_artifact`; no in-place body UPDATE; no prior-id lookup.
2. `save_candidate_data(candidate_id, artifact_key, blob)` is the only candidate write entry for the pilot body; UI save and `craft_resume_base` land both use it.
3. `TASK_CONFIG["craft_resume_base"]["artifact_key"] == "candidate.artifacts.base_resume"`.
4. Agent craft land no longer routes pilot body through `_persist_craft_dispatch_success` / craft-specific persist helpers — generic `save_candidate_data` only, and all replaced functions are removed from the component.
5. `src/utils/artifact_catalog.py` is gone.
6. Base resume edit UI follows `patt.artifacts.ui-consistency` (`resume_content`); save→reload shows operative current body via existing `get_current_artifact`.
7. Draft `canon/directives/draft/patt.artifacts.ui-consistency.md` exists; no cross-link from write-operative.
8. No new `ARTIFACT_CONFIG` keys; no coat-check; no job finalize / grade pin writers this ticket.

## Open questions

none

## Proposed child tickets

#### 1!: **Generic save_candidate_data + agent craft-persist rewire - Ada**

Blind `save_artifact` retire+insert; `save_candidate_data(candidate_id, artifact_key, blob)` against `ARTIFACT_CONFIG`; `craft_resume_base` `artifact_key`; rewire agent to call that generic save and remove craft-persist gunk for operative bodies; retarget parse + API save; delete `artifact_catalog`. Does **not** own React editor or ui-consistency draft.

**Citations: **`patt.artifact.write-operative`; `patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.database-header-inventory`; `astral.standards.data-raises-caller-logs`; `astral.layers.import-direction`

**Scope: **`src/data/database.py`; `src/utils/artifact_catalog.py` (**deleted**); `src/utils/config.py`; `src/core/candidate.py`; `src/core/agent.py` (craft-persist rewire); `src/ui/api/api_candidate.py`; Betty delete/retarget catalog wrapper tests.

**Estimate: 5**

#### 2: **patt.artifacts.ui-consistency + shape-standardized base_resume editor - Katherine**

After #1: author draft `patt.artifacts.ui-consistency.md` (no cross-links) and refactor ArtifactEditor / ArtifactsBaseResumeContent for body_shape `resume_content`, save via candidate API, hydrate operative current body.

**Citations: **`patt.artifacts.ui-consistency` (new); `patt.artifact.write-operative`; `astral.layers.import-direction`; `astral.standards.in-scope-only`

**Scope: **`canon/directives/draft/patt.artifacts.ui-consistency.md` (**new**); `src/ui/frontend/src/components/ArtifactEditor.tsx`; `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx`

**Estimate: 3**

**Monolith check:** Core/agent rewire vs UI pattern+editor → 2 children.

**Scope partition check:** database / config / candidate / agent / api_candidate / delete artifact_catalog → child 1. ui-consistency draft + frontend → child 2.

---

## Original brief

## Scope

Data-layer and caller paths for write-operative (retire+insert, return artifact_id).

## Pattern

`canon/directives/draft/patt.artifact.write-operative.md`

## Depends on

manage-catalog

## Done when

save_artifact paths match pattern; grades can persist artifact_id pins.

### Comments

#### susan — 2026-09-02T21:42:26.585Z
When we wire the UI, plan to standardize the edit screen based on the artifact shape so that all the same-typed artifacts can use the same components.  This is in scope for this ticket and should update the pattern to reflect that mandate.

#### susan — 2026-09-02T21:40:25.410Z
There are two surfaces that will use this write pattern: the ui and the craft_base_resume task.  I believe we have config set up for tasks to designate their persistence location.  For craft_base_resume, we should replace it with "artifact_key":"candidate.artifacts.base_resume"

#### susan — 2026-09-02T21:37:53.125Z
I don't believe we need an artifact component.  It is a natural child of the entities and it's just doing writes and reads.

candidate.py should have a generic "save_candidate_data" function that can be used for any content that was originally stored in the candidate_data object.  Update the save surface from api to candidate to save candidate data, then that function calls calls database.py directly to save_artifact, which always returns the new current uuid on success.

artifact id should not be a consideration for the API, since we don't expose the artifact id to the user and if an error happened, candidate would handle it.

#### chuckles — 2026-09-02T20:25:26.706Z
@susan

1. **Pin storage shape** — Where should a grade/analysis record store the pilot `artifact_id`? (e.g. per-grade-row field, sibling map next to a `grades_key`, candidate-scoped pin map, or other.) Name the field/envelope you want as SoT for AST-1571 readers.
2. **Which writers this ticket** — Which runtime lands must pin `candidate.artifacts.base_resume` **in AST-1569** (enumerate tasks / save paths), vs pin-helper + Save Base Resume propagate only now and defer remaining writers to a follow-on / AST-1571 pairing?
3. **API visibility** — Must Save Base Resume HTTP responses expose `artifact_id` to the client this ticket, or is core-internal propagation enough until a consumer needs it?

---

_Implementation detail may live in git history on `origin/dev`._
