# AST-1762 — Meteorite state CHECK_UNIQUE before LANDED

<!-- linear-archive: AST-1762 archived 2026-10-02 -->

## Linear archive (AST-1762)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1762/meteorite-state-check-unique-before-landed  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** High / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Candidates forward the same job more than once, and different recruiters pitch the same employer role under different message wrappers. Today a landable meteorite row goes straight to `READY` and then `LANDED`, so near-duplicates become parallel jobs. This epic inserts a uniqueness gate before land: stage teaches Ruth to return optional `employer_name` when she can (no guessing), a SQL hop matches title + `employer_name` against already-`LANDED` peers, and a Ruth review hop confirms true duplicates into a terminal `DUPLICATE` hold (state-hold only — candidate rescue UI is a later epic).

## Functional scope

1. **employer_name at stage** — On landable `stage_meteorite` classify, Ruth may return optional `employer_name` (existing schema key and meteorite column — no new `company_name` field). Omit when unsure; never invent. Value persists on the meteorite row for matching.
2. **CHECK_UNIQUE row state before land** — After `run_stage_meteorite` / `run_scrape_meteorite` landable success (today’s `READY` writers on those paths only), the meteorite **row** enters `CHECK_UNIQUE`. This is not a new Ruth classify outcome — the six closed `stage_meteorite` outcome literals are unchanged.
3. **SQL uniqueness gate** — Dispatch task `check_unique_meteorite` claims `CHECK_UNIQUE` rows and matches same-candidate `LANDED` peers by equal `job_title` and `employer_name` only (not email ids, not JD text). No peers → `READY`. Title+employer match found → Ruth duplicate review with candidate row + matched LANDED peers.
4. **Ruth when SQL cannot match** — When `job_title` and/or `employer_name` is empty/unknown but multiple `LANDED` rows share null title and/or null employer, still invoke Ruth with the full CHECK_UNIQUE content plus each candidate LANDED row’s full content (not title/employer string equality).
5. **Ruth duplicate review** — New Ruth agent task compares CHECK_UNIQUE content against peer LANDED JDs; returns duplicate of a specific LANDED peer or not. Duplicate → terminal `DUPLICATE`. Not duplicate → `READY` for land.
6. **Terminal DUPLICATE hold** — `DUPLICATE` is insert-legal for scheduled cleanup later; no Manage Email / candidate rescue surface in this epic. Land continues to claim only `READY` → `LANDED`.

**Out of scope:** Estelle `apply_paste` / `BOT_BLOCKED` → `READY` recovery and any other direct `READY` writers outside stage/scrape landable success — those paths are unchanged; BOT_BLOCKED re-enters via `NEW` and eventually flows through the normal meteorite state machine.

## Component scope

* `src/utils/config.py` — **modified** — add `CHECK_UNIQUE` and `DUPLICATE` to `METEORITE_STATES`; retarget stage/scrape success destinations and ingress dispatch config; add `TASK_CONFIG` + config block for Ruth duplicate-review; seed/assert `check_unique_meteorite`.
* `data/admin/agent_task.json` — **modified** — `stage_meteorite` prompts for optional `employer_name` (never invent); new Ruth duplicate-review catalog row (prompts + schema lockstep with `TASK_CONFIG`). **Blocked by AST-1753** landing first (same `stage_meteorite` row).
* `data/admin/dispatch_task.json` — **modified** — add `check_unique_meteorite` following existing meteorite ingress global-pool shape.
* `src/core/meteorite.py` — **modified** — `run_stage_meteorite` / `run_scrape_meteorite` landable success → `CHECK_UNIQUE` (not `apply_paste` or other READY writers); implement `run_check_unique_meteorite` (SQL match, null-field Ruth fallback, state transitions); keep `run_land_meteorite` on `READY` → `LANDED`.
* `src/core/dispatcher.py` — **modified** — route `check_unique_meteorite` to the meteorite runner like other ingress transition keys.

## Technical scope

* `src/utils/config.py` — **modified** `METEORITE_STATES` — new `CHECK_UNIQUE` (priors from stage/scrape landable-success writers: `NEW`, `SCRAPE_LINK` as applicable) and terminal `DUPLICATE` (`prior_states` from `CHECK_UNIQUE` only or None per registry pattern); update assert closed set.
* `src/utils/config.py` — **modified** `METEORITE_INGRESS_DISPATCH_CONFIG` / scrape success map — stage/scrape success targets become `CHECK_UNIQUE` instead of `READY`; add check-unique task key + trigger state `CHECK_UNIQUE`; land trigger remains `READY`.
* `src/utils/config.py` — **modified** `TASK_CONFIG["stage_meteorite"]` — confirm existing optional `employer_name` on jobs items_schema (`required: False`); no `company_name` key.
* `src/utils/config.py` — **new** `TASK_CONFIG` entry + companion config block for Ruth duplicate-review (closed outcomes: at least duplicate / not-duplicate; peer meteorite id when duplicate).
* `src/utils/config.py` — **modified** `SEED_CONFIG` + monitoring format strings for new hop and `DUPLICATE` transitions.
* `data/admin/agent_task.json` — **modified** `stage_meteorite` prompts — optional `employer_name` from content; forbid guessing; no `$RESPONSE_SCHEMA` dump.
* `data/admin/agent_task.json` — **new** Ruth duplicate-review row — peer comparison; return which `LANDED` id when duplicate.
* `data/admin/dispatch_task.json` — **new** `check_unique_meteorite` row — `trigger_state=CHECK_UNIQUE`, global pool like siblings.
* `src/core/meteorite.py` — **modified** `run_stage_meteorite` / `run_scrape_meteorite` — landable success → `CHECK_UNIQUE` only (leave `apply_paste` and other READY writers untouched).
* `src/core/meteorite.py` — **new** `run_check_unique_meteorite` — claim batch; SQL match by title + `employer_name` among same-candidate `LANDED`; no peers → `READY`; title+employer peers → Ruth; multiple null title/employer LANDED peers → Ruth with full row content; map duplicate → `DUPLICATE`, not-duplicate → `READY`.
* `src/core/dispatcher.py` — **modified** ingress transition router — register `check_unique_meteorite`.

## Architectural definition

**Patterns to reuse**

* `patt.entity.batch-processing` — check-unique claims a batch under one id, processes only those rows, always releases. [patt.entity.batch-processing](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-processing.md>)
* `patt.entity.batch-criteria` — claim shape (state, limit, order) comes from dispatch_task / ingress config, not literals in the runner. [patt.entity.batch-criteria](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-criteria.md>)

**New patterns proposed**

* none — uniqueness is another ingress transition hop in the existing stage → scrape → land family (AST-1560), not a new reusable shape.

**Applicable statutes**

* `astral.batch.claim-process-release` — meteorite is an `ENTITY_TYPES` claim queue; the new hop must claim/process/release with batch_id parity. [astral.batch.claim-process-release](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.batch.claim-process-release.md>)
* `astral.dispatch.entity-state-bound` — `check_unique_meteorite` trigger_state must be a real `METEORITE_STATES` key and must be what the runner claims. [astral.dispatch.entity-state-bound](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.dispatch.entity-state-bound.md>)
* `astral.entity.required-metadata` — new states still use the shared meteorite entity metadata columns; no new entity table. [astral.entity.required-metadata](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.entity.required-metadata.md>)
* `stat.logging.info.entity` — row transitions (`CHECK_UNIQUE` / `DUPLICATE` / promote to `READY`) use entity progress lines. [stat.logging.info.entity](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>)
* `stat.logging.info.dispatcher` — dispatch completion for the new task key. [stat.logging.info.dispatcher](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.dispatcher.md>)
* `stat.logging.debug` — noisy match/peer detail stays debug. [stat.logging.debug](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)

## Acceptance criteria

 1. **employer_name at stage** — `TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]["employer_name"]["required"]` is False; prompts teach optional `employer_name`; no `company_name` key added. Fail: new `company_name` field or `employer_name` required=true.
 2. **No invent instruction** — `stage_meteorite` prompt section for employer forbids guessing/invention. Fail: prompts instruct Ruth to fill `employer_name` without content support.
 3. **CHECK_UNIQUE on stage/scrape success only** — After `run_stage_meteorite` / `run_scrape_meteorite` landable success, `meteorite.state` is `CHECK_UNIQUE`. Fail: those runners still write `READY`, or `apply_paste` / other out-of-scope writers changed to `CHECK_UNIQUE`.
 4. **CHECK_UNIQUE is row state only** — `STAGE_METEORITE_CONFIG["outcomes"]` still has exactly six literals; no `CHECK_UNIQUE` in Ruth outcome enum. Fail: seventh classify outcome or Ruth returning row state names.
 5. **SQL match keys** — Peer selection uses same `candidate_id` + equal non-empty `job_title` + equal non-empty `employer_name` among `LANDED` only. Fail: match on email ids, message ids, or JD text equality.
 6. **Unique → READY** — CHECK_UNIQUE row with no matching LANDED title+employer peer and no null-field Ruth trigger becomes `READY` and is claimable by `land_meteorite`. Fail: unique rows stuck in `CHECK_UNIQUE` or skip to `LANDED`.
 7. **Null peers → Ruth with full content** — When title and/or employer is empty and multiple LANDED rows have null title and/or null employer, Ruth duplicate-review runs with full CHECK_UNIQUE + LANDED row content. Fail: auto-`READY` or auto-`DUPLICATE` without Ruth in that scenario.
 8. **Peers → Ruth → DUPLICATE|READY** — Title+employer SQL match invokes Ruth; duplicate → `DUPLICATE` with peer id recorded; not-duplicate → `READY`. Fail: SQL peers auto-terminal without Ruth.
 9. **Land unchanged gate** — `land_meteorite` trigger remains `READY`; `DUPLICATE` and `CHECK_UNIQUE` are not landable. Fail: land claims `DUPLICATE`/`CHECK_UNIQUE`.
10. **Registry closed set** — `set(METEORITE_STATES)` includes `CHECK_UNIQUE` and `DUPLICATE`; `import src.utils.config` passes asserts. Fail: closed-set assert mismatch.

## Open questions

none

## Proposed child tickets

#### 1!!!: **States, config, stage employer_name prompts - Ada**

Owns `METEORITE_STATES` (`CHECK_UNIQUE`, `DUPLICATE`), ingress dispatch retarget (stage/scrape success → `CHECK_UNIQUE`; land stays `READY`), optional `employer_name` prompts on `stage_meteorite` (existing schema key), Ruth duplicate-review catalog + `TASK_CONFIG`, and `check_unique_meteorite` dispatch seed. **After AST-1753 lands** (parent blocker — do not edit `stage_meteorite` agent_task until then). Does not implement SQL runner or Ruth invoke (#2 / #3).

**Citations:** `astral.dispatch.entity-state-bound`, `astral.entity.required-metadata`, `stat.logging.debug`.
**Scope:** `src/utils/config.py` — **modified** — add `CHECK_UNIQUE` and `DUPLICATE` to `METEORITE_STATES`; retarget stage/scrape success destinations and ingress dispatch config; add `TASK_CONFIG` + config block for Ruth duplicate-review; seed/assert `check_unique_meteorite`. / `src/utils/config.py` — **modified** `METEORITE_STATES` — new `CHECK_UNIQUE` (priors from stage/scrape landable-success writers: `NEW`, `SCRAPE_LINK` as applicable) and terminal `DUPLICATE`; update assert closed set. / `src/utils/config.py` — **modified** `METEORITE_INGRESS_DISPATCH_CONFIG` / scrape success map — success targets become `CHECK_UNIQUE`; add check-unique task key + trigger `CHECK_UNIQUE`; land trigger remains `READY`. / `src/utils/config.py` — **modified** `TASK_CONFIG["stage_meteorite"]` — confirm optional `employer_name` (`required: False`); no `company_name`. / `src/utils/config.py` — **new** Ruth duplicate-review `TASK_CONFIG` + config block. / `src/utils/config.py` — **modified** `SEED_CONFIG` + monitoring format strings. / `data/admin/agent_task.json` — **modified** `stage_meteorite` prompts for optional `employer_name`; **new** Ruth duplicate-review row. / `data/admin/dispatch_task.json` — **new** `check_unique_meteorite` row.
**Estimate: 3**

#### 2!!: **check_unique_meteorite SQL + transitions - Hedy**

Owns `run_stage_meteorite` / `run_scrape_meteorite` landable success → `CHECK_UNIQUE`, `run_check_unique_meteorite` (SQL match + null-field peer detection + hook for Ruth), and dispatcher registration. Does not own Ruth `do_task` / outcome map (#3) or `apply_paste`. After #1.

**Citations:** `patt.entity.batch-processing`, `patt.entity.batch-criteria`, `astral.batch.claim-process-release`, `stat.logging.info.entity`, `stat.logging.info.dispatcher`.
**Scope:** `src/core/meteorite.py` — **modified** `run_stage_meteorite` / `run_scrape_meteorite` landable success → `CHECK_UNIQUE` (not `apply_paste`). / `src/core/meteorite.py` — **new** `run_check_unique_meteorite` — claim batch; SQL match by title + `employer_name` among same-candidate `LANDED`; no peers → `READY`; detect null-field multi-peer case and delegate Ruth hook; unique SQL path → `READY`. / `src/core/dispatcher.py` — **modified** — route `check_unique_meteorite`.
**Estimate: 5**

#### 3: **Ruth duplicate-review invoke + DUPLICATE map - Katherine**

Owns Ruth invoke inside check-unique when SQL peers or null-field multi-LANDED peers exist: build full-content payloads, `do_task` duplicate-review agent_task, map duplicate → `DUPLICATE` (record LANDED peer id) and not-duplicate → `READY`. After #1; consumes #2 hook. Does not re-edit stage prompts or registry.

**Citations:** `patt.entity.batch-processing`, `stat.logging.info.entity`, `stat.logging.debug`.
**Scope:** `src/core/meteorite.py` — **modified** — Ruth invoke + outcome map on SQL-match and null-field multi-peer paths only; does not own SQL unique→READY (#2) or config/catalog (#1).
**Estimate: 3**

**Monolith check:** Functional scope has 6 capabilities (+ explicit out-of-scope line); 3 children — intentional (config/prompts blocked on AST-1753, SQL gate, Ruth invoke).

**Scope partition check:** config + catalogs → #1; stage/scrape→CHECK_UNIQUE writers + SQL + dispatcher + Ruth hook → #2; Ruth invoke/map → #3. `apply_paste` and other READY writers unclaimed (explicitly out of scope). No catalog file claimed twice.

**Blockers:** [AST-1753](https://linear.app/astralcareermatch/issue/AST-1753/stage-email-meteorite-enhancements) (and its landed children AST-1755–1757) must land before #1 edits `stage_meteorite` agent_task. [AST-1711](https://linear.app/astralcareermatch/issue/AST-1711/rework-meteorite-email) ingress spine already on table path. [AST-1763](https://linear.app/astralcareermatch/issue/AST-1763/remove-company-name-validation-error-on-print-resume-and-print-cover) is separate — not this gate.

---

## Original brief

Update the stage_meteorite prompt to tell it to read the content to figure out the name of the company the candidate would be working with, and return that in "company_name" in the sresponse schema, but tell it not to guess, and it's not a required field in the response.  This will help us reduce the duplications.  We need to also create a task to ruth to send her any READY meteorites with the LANDED meteorites of the same job title and company (if known), to review the job descriptions and confirm if the READY is likely a DUPLICATE of another meteorite (and specify which LANDED meteorite it is a duplicate of), either because the candidate accidentally sent it in multiple times, or the job is actually been pitched by different recruiters from different companies for the same position.

If the stage_meteorite response comes back with CHECK_UNIQUE (instead of "READY") Then a SQL task (check_unique_meteorite) will check for duplicates by title and employer company (NOT the email ids or job text strings), and if they are unique, then the state will go to "READY", otherwise, the matching LANDED and CHECK_UNIQUE are sent to the new prompt described above.  If that comes back as DUPLICATE, then mark the CHECK_UNIQUE meteorite to DUPLICATE as a terminal state to be cleaned up with a scheduled query later.  This gives the candidate a period to review what the AI thought was a duplicate and rescue any mis-identified unique jobs.

### Comments

#### chuckles — 2026-09-24T18:09:11.408Z
@Betty White

[refresh-ftr] blocked: `tests/component/utils/test_config.py` (merge origin/ftr/AST-1762-meteorite-state-check-unique-before-landed → local/origin/dev during finish-up).

#### chuckles — 2026-09-22T02:28:39.097Z
AST-1774 REVIEW — merge-child blocked; recalling Hedy to re-stack sub on refreshed ftr.

#### chuckles — 2026-09-22T01:00:32.529Z
@susan

1. Brief names response field `company_name`, but `stage_meteorite` / meteorite rows already use optional `employer_name`. Confirm: reuse and teach `employer_name` (no new key), or add a separate `company_name` field?
2. Brief says stage_meteorite “comes back with CHECK_UNIQUE instead of READY.” Today Ruth outcomes are the six classify literals; `READY` is a meteorite **row** state set by stage/scrape runners. Confirm: `CHECK_UNIQUE` is a new **row** state (not a new Ruth classify outcome literal)?
3. When `job_title` and/or employer/company is empty/unknown, should `check_unique_meteorite` auto-promote to `READY` (cannot match), hold in `CHECK_UNIQUE`, or still call Ruth?
4. “Candidate period to review / rescue” mis-tagged duplicates — is that **state-hold only** this epic (UI/API rescue later), or must Manage Email / a candidate surface be in scope here?
5. Should Estelle paste recovery (`BOT_BLOCKED` → content → today `READY`) and any other direct `READY` writers in `meteorite.py` also enter `CHECK_UNIQUE`, or only the main stage/scrape success paths?
6. Adjacent AST-1753 / AST-1755–1757 (job_title stage prompts + land title) is in flight / PR Ready — OK to edit the same `stage_meteorite` agent_task row for employer prompts after that line merges, or should this epic wait / layer strictly after?

---

_Implementation detail may live in git history on `origin/dev`._
