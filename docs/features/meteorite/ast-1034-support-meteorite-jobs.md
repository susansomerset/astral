# AST-1034 — Support meteorite jobs

<!-- linear-archive: AST-1034 archived 2026-08-05 -->

## Linear archive (AST-1034)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1034/support-meteorite-jobs  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Meteorite needs a stable, candidate-scoped **placeholder employer** so jobs can exist in Astral before a real hiring company (and website) is known. Today every job hangs off a `company` row; without a sentinel, email- and paste-sourced JDs have nowhere legal to land. This epic defines a config-owned **meteorite** company template and **lazily** inserts `meteorite-<candidate_id>` when a known candidate needs one (email from a known user, or the job-create API), then allows creating jobs under that company from raw HTML via an API — the foundation for later Meteorite ingest (sibling **AST-1031** is email-read only).

## Functional scope

* A config-owned seed template defines the meteorite placeholder company (display name **meteorite**, short-name shape `meteorite-<candidate_id>`, company state **IGNORE**, and fixed metadata stating the employer is unidentified and cannot be vetted without a website URL).
* Astral **does not** bulk-upsert meteorite companies at server start. Instead it **lazy-ensures** the row: when a known candidate needs a meteorite company (receiving email from a known user in the ingest path, or calling the job-create API), insert `meteorite-<candidate_id>` if it does not already exist — scoped to that candidate, state **IGNORE**, metadata from config.
* Meteorite placeholder companies stay in **IGNORE** and are excluded from roster / website-resolution / gazer company pipelines — they must not be treated as discoverable employers to vet or scrape.
* An **API-only** create path (no admin UI in this epic) creates a job under a candidate’s `meteorite-<candidate_id>` company from raw HTML job-description content; the create path lazy-ensures the company first. The job lands in **JD_READY** with **latest_score 10.0** as a stand-in for the joblist qualifier that did not run, so score-floor filtering does not drop it. The HTML is the JD (no fetch_jd / scrape). No new job state is invented for this entry.
* When a candidate leaves ACTIVE_SEARCH (or otherwise), existing `meteorite-*` company rows and their jobs are **left in place**.
* Lazy-ensure emits backend debug contract detail when `debug=True` (candidate id, inserted vs already-present, outcome) — Style D index headers and `|` working detail; no new contract lines when `debug=False`.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — meteorite seed literals (prefix, display name, metadata text, company state **IGNORE**, short-name shape, create defaults for **JD_READY** + score **10.0**) live in `config.py`; no inline magic strings in ensure/create callers.
  * `pattern.state.entity-state-transitions` — placeholder companies and meteorite-created jobs use registered company/job states only (**IGNORE**, **JD_READY**); core decides transitions; create-into-**JD_READY** must satisfy prior_states law via an explicit config-allowed entry path (expand priors or documented create carve-out) — not a new job state.
  * `pattern.layers.import-discipline` — ensure + job-create orchestration in core; data persists; no UI surface in this epic.
* **New patterns proposed**
  * **Config-templated lazy per-candidate placeholder company** — ensure-if-missing sentinel `company` row from a config template when a known candidate needs it (not bootstrap bulk upsert; distinct from retired board `__board__*` placeholders). Flag for Archie approval before plans treat it as catalog law; until approved, implement under this epic’s citations only.
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — seed template, IGNORE state, JD_READY entry defaults, score stand-in in config.
  * `astral.standards.no-hardcoded-sets` — no inline prefix / metadata / score literals outside config.
  * `astral.state.core-decides-transitions` — company/job state on ensure and create chosen in core from registries.
  * `astral.state.job-prior-states-enforced` — meteorite job create must land in **JD_READY** legally (priors/carve-out in config, not bypass by silent data write).
  * `astral.config.pass-threshold-vs-score-floor` — synthetic **latest_score 10.0** is dispatch/eligibility stand-in for skipped qualify; do not confuse with pass_threshold grading math.
  * `astral.standards.debug-contract-gated` — lazy-ensure debug when `debug=True`.
  * `astral.standards.database-header-inventory` — company/job table usage stays within inventory; no new tables.
  * `astral.layers.import-direction` / `astral.layers.core-vs-external-bright-line` — API → core → data; no external I/O in this epic.
  * `universal` set — product code changes.

## Boundaries

* Does **not** bulk-seed meteorite companies for all ACTIVE_SEARCH candidates at server startup.
* Does **not** implement Gmail/email ingest, classification, mailbox mutation, or email→candidate identity matching (that remains **AST-1031** / a later ingest epic). This epic ships the lazy-ensure helper and calls it from the job-create API; email ingest will call the same helper when a known user is resolved.
* Does **not** add an admin UI to paste HTML or create meteorite jobs — **API capability only**.
* Does **not** invent a new job state for meteorite entry; uses existing **JD_READY** plus synthetic joblist-qualifier score **10.0**.
* Does **not** resolve or replace meteorite placeholders with real employers (no SEEK_COMPANY / website resolution for these rows in this epic).
* Does **not** grant meteorite jobs full consult parity with vetted companies when tasks require a true employer website — this epic only makes the placeholder + raw-HTML API create path real (pipeline continues from **JD_READY** / evaluate_jd onward under existing rules).
* Does **not** revive board-gaze `__board__*` placeholders or boards channel code.
* Does **not** delete or transition `meteorite-*` companies when a candidate leaves ACTIVE_SEARCH.
* Must not break existing roster inflow, gazer, or tracker paths for real companies.
* Must not put meteorite company rows into claimable roster/gazer triggers (they remain **IGNORE**).

## Acceptance criteria

1. Config defines the meteorite placeholder template (display name, `meteorite-<candidate_id>` shape, **IGNORE**, unidentified-employer metadata).
2. Calling lazy-ensure for a candidate inserts `meteorite-<candidate_id>` once when missing and is a no-op when the row already exists; server start alone does **not** create meteorite rows for all ACTIVE_SEARCH candidates.
3. Meteorite placeholder companies in **IGNORE** are never claimed or processed by roster website-resolution / gazer company batch tasks.
4. An authenticated API create call can create a job under `meteorite-<candidate_id>` from raw HTML job-description content; it lazy-ensures the company first; the job is in **JD_READY**, has **latest_score 10.0**, persists that HTML as the JD, and does not require a real employer website or a fetch_jd scrape.
5. No admin UI for meteorite job create ships in this epic.
6. Existing `meteorite-*` companies (and jobs) remain in the database after the candidate is no longer ACTIVE_SEARCH.
7. With `debug=True` on the lazy-ensure path, insert vs already-present outcomes use Style D index headers and `|` detail; with `debug=False`, no new debug-contract lines from that path.
8. Existing non-meteorite company and job flows still behave as before (smoke: a normal company is still claimable on its existing triggers).

## Dependencies and blockers

* Related (not blocked): **AST-1031** (Gmail inbox read / Read email admin seed) — same Astral Meteorite project; full email→job ingest (including calling lazy-ensure for a known user) is a later epic.
* none otherwise.

## Open questions

none

## Proposed child tickets

#### 1!: **Meteorite company config + lazy ensure - Ada**

Owns the config seed template (including **IGNORE**), the core lazy-ensure helper (insert `meteorite-<candidate_id>` if missing for a given candidate), leave-in-place lifecycle, and hard exclusion of those rows from roster/gazer company claim paths. Does **not** own the job create API (child 2) or email ingest.
**Citations:** `pattern.config.config-block`; `pattern.state.entity-state-transitions`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.debug-contract-gated`; `astral.standards.database-header-inventory`.

#### 2: **API create job under meteorite from raw HTML - Hedy**

Owns the API create path that lazy-ensures the candidate’s meteorite company, then creates a job from raw HTML as the JD, landing in **JD_READY** with **latest_score 10.0** (synthetic joblist-qualifier stand-in), with a legal prior_states entry path — no new job state, no admin UI, no email ingest. After #1.
**Citations:** `pattern.state.entity-state-transitions`; `astral.state.job-prior-states-enforced`; `astral.state.core-decides-transitions`; `astral.config.pass-threshold-vs-score-floor`; `pattern.layers.import-discipline`; `astral.layers.import-direction`; `astral.patterns.require-auth-on-protected-endpoints`.

**New patterns:** Child 1 introduces config-templated lazy per-candidate placeholder ensure; later Meteorite ingest epics reuse the same helper + create API.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1034 (parent) | ftr/AST-1034-support-meteorite-jobs |
| AST-1041 | sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure |
| AST-1042 | sub/AST-1034/AST-1042-api-create-job-under-meteorite-from-raw-html |

**Epic worktree:** `astral-AST-1034/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | `/home/susan/.cursor/chats/7b0e833423ebc6a5ec29067f1fb11ea3/1223ef33-6442-4b3f-a048-7a7c8d1a7715/store.db` |
| Ada | engineer | `/home/susan/.cursor/chats/7b0e833423ebc6a5ec29067f1fb11ea3/1435db58-ae87-4b74-8a59-a276592304c5/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/e662e9ef-014e-40f7-be4d-6dc3efcb7417/store.db` |
| Radia | review | `/home/susan/.cursor/chats/7b0e833423ebc6a5ec29067f1fb11ea3/e662e9ef-014e-40f7-be4d-6dc3efcb7417/store.db` |

---

## Original brief

Seed a company called "meteorite" in the company table.  Put its seed content in the [config.py](<http://config.py>) file so that it is upserted when the server starts for all ACTIVE_SEARCH candidates. (27 candidates, 27 "meteorite-<candidate_id>", with metadata like "The company for this job has not been identified, and cannot be vetted without a website url."

Allow jobs to be created in job with the meteorite-<candidate_id> company with just raw HTML content for the job description.

### Comments

#### susan — 2026-07-29T14:52:47.823Z
@chuckles Actually, let's do a lazy load of the meteorite companies, when we get an email from a known user, we can insert their meteorite company if one does not yet exist for them.

#### chuckles — 2026-07-29T04:46:06.690Z
@susan Open questions before Todo:

1. **Company state:** Which registered `COMPANY_STATES` key should meteorite placeholders use (reuse `IGNORE` / `NO_WEBSITE`, or add a dedicated state e.g. `METEORITE`)? Confirm they must stay non-claimable for all roster/gazer company tasks.
2. **Job create surface for this epic:** Core/API capability only (for later Meteorite ingest to call), or also an admin UI to paste HTML and create a job under the selected candidate’s meteorite company?
3. **Job pipeline after create:** Should meteorite-created jobs enter the normal **NEW** → title/JD/consult pipeline with the HTML already treated as the JD (skip scrape), or park in a holding/non-dispatched state until a real company is attached in a later epic?
4. **Lifecycle:** When a candidate leaves ACTIVE_SEARCH, leave their `meteorite-*` company (and any jobs) in place, or transition/delete the placeholder?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
