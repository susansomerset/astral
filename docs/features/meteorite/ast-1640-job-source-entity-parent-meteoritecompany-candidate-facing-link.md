# AST-1640 — Job source_entity parent (meteorite|company) + candidate-facing link

<!-- linear-archive: AST-1640 archived 2026-09-24 -->

## Linear archive (AST-1640)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1640/job-source-entity-parent-meteoritecompany-candidate-facing-link  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** None / 8  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1620; related: AST-1555

### Description

## Purpose

Partial foundation already ships (`job.source`, meteorite staging + `link`, gazed→meteorite supersede), but jobs still require a company parent via placeholder / stem METEORITE companies. This epic finishes the locked model: parent to **where the listing came from** (`meteorite` or gazed `company`), optional real employer, candidate-facing link inheritance, and track that follows the parent — so meteorite analysis is not yanked onto gazed fail-early when an employer is attached.

## Functional scope

1. **Source-entity parent** — Every job has a required ingest parent: `source_entity_type` is `company` (gazer) or `meteorite` (staging row), plus `source_entity_id` (company `short_name`, or meteorite row `id` as text). Placeholder `meteorite-*` / stem companies are never job parents after this ships.
2. **Repurpose or drop** `job.source` — Prefer **repurposing** the existing `job.source` column into this parent/track SoT (`company` | `meteorite`, migrating `gazed` → `company`). If in-place repurpose is unsafe, **drop** `job.source` / `JOB_SOURCES` and add `source_entity_type` instead — clean stale references either way. One SoT when this ships; no parallel unused flag left as authority.
3. **Optional real employer** — Nullable `company_id` holds a real employer `short_name` for website / culture / scan data when known. Never a fake meteorite company. Setting `company_id` does not change the analysis track.
4. **Track follows parent** — Analysis track is driven by `source_entity_type`, not by whether `company_id` is set. Meteorite-parented jobs run the meteorite GDL (`qualify_meteorite`, score_floor 0, no title-pattern kill) even when `company_id` is a real employer.
5. **Same row on gazed → meteorite** — If a posting was already gazed (including fail-early) and later lands as a meteorite: keep the same `astral_job_id`, keep `company_id` if known, flip parent to the meteorite row, state → `METEORITE_NEW`, run full meteorite GDL. Prior gazed outcomes stay in `state_history`. No second job row.
6. **Link + JD content** — `job.job_link` **inherits** from `meteorite.link`. JD text may come from a different source (email body or candidate paste). Checking the link must **not fail the land on bot-block**; when the check is **not** bot-blocked, append that JD content to existing job text. Email breadcrumb format for no-URL outcomes: `From:<email> M/D H:MM <timezone> To:<email>` (peel inner headers on forward; Python formats clock in `contact.timezone`). Job Detail “open listing” is an href only when `job_link` is `http(s)`; non-http inherited text remains visible as text. Slack/paste **breadcrumb format** stays out; paste as a **JD content** source is allowed per the append rule above.
7. **Manual backfill only** — Ship a SQL statement Susan can run to backfill existing jobs (prefer `meteorite.astral_job_id` reverse link → meteorite parent). **Do not** seed an automatic migration/update on boot.

## Component scope

* `src/utils/config.py` — **modified** — source-entity type literals / validators; repurpose or retire `JOB_SOURCES` per Functional scope; breadcrumb format + timezone clock helpers; METEORITE_CONFIG keys that still force placeholder company parents.
* `src/data/database.py` — **modified** — job schema for `source_entity_type`/`source_entity_id` (via repurposed `source` or new columns), nullable `company_id` replacing required `company`; candidate_id resolution when parent is meteorite; save/get/list/dedupe helpers + header inventory; **operator SQL backfill script** (docs or `data/` SQL file — not auto-run seed).
* `src/core/tracker.py` — **modified** — `save_meteorite_job` / create / gazed→meteorite supersede write parent fields + optional `company_id`; stop requiring meteorite company short_name as parent; stop using old `gazed`/`meteorite` source flag as track authority once repurposed/dropped.
* `src/core/meteorite.py` — **modified** — land parents to meteorite row; `job.job_link` inherits `meteorite.link`; link check does not fail land on bot-block; append non-blocked JD content to existing text; stop `ensure_meteorite_company` as job parent; optional real `company_id`; email breadcrumb authorship for no-URL outcomes.
* `src/core/consult.py` — **modified** — qualify / land-packet / track selection uses `source_entity_type` so meteorite+`company_id` stays on meteorite GDL.
* `src/core/gazer.py` and/or `src/core/tracker.py` gazed ingest — **modified** — gazed creates set `source_entity_type=company`, `source_entity_id=short_name`, `company_id` to that employer when known.
* `src/ui/api/api_jobs.py` — **modified** — expose parent fields, nullable `company_id`, and `job_link` (inherited) for detail.
* `src/ui/frontend/src/pages/JobsJobDetail.tsx` — **modified** — deeplink host for Job Detail (prefetch/mount only).
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified** — job_link open/window.open only when `http(s)`.
* `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` — **modified** — title href only when `http(s)`; non-http text still shown.
* `src/ui/frontend/src/components/JobDetailModal.tsx` — **modified** — Link-row href only when `http(s)`; non-http text still shown.

## Technical scope

* `config` — closed set `company` | `meteorite` for parent/track; migrate `gazed`→`company` when repurposing `job.source`; else add `source_entity_type` and delete `JOB_SOURCES` / transition helpers; breadcrumb format string + clock shape.
* `database` job table — required parent fields after backfill; nullable `company_id` instead of NOT NULL `company`; `_resolve_job_candidate_id` (or successor) from meteorite row when parent is meteorite.
* `database` writers/dedupe — accept meteorite parent + optional `company_id`; gazed→meteorite supersede finds same row; `meteorite.astral_job_id` stays 1:1 on land.
* **Backfill artifact** — one Susan-runnable SQL script mapping existing `meteorite-*`/stem-parented jobs via `meteorite.astral_job_id` (and gazed defaults) to the new parent fields; **not** invoked from `SEED_CONFIG` / boot.
* `tracker.save_meteorite_job` — create under meteorite parent; gazed match flips parent to meteorite, keeps `company_id`, state `METEORITE_NEW`, appends history; no second row; no clobber of existing meteorite-parented row.
* `meteorite` land — inherit `meteorite.link` → `job.job_link`; on link check, bot-block does not fail the land; if not bot-blocked, append JD text onto existing job description content; no-URL email outcomes write breadcrumb onto `meteorite.link` (then inherit); stop `ensure_meteorite_company` solely for `job.company`.
* `consult` / consumers — track from `source_entity_type` (or single config helper), not company state `METEORITE` and not legacy `source == "meteorite"` meaning.
* `gazer` create — company parent + `company_id` for gazed employer.
* `api_jobs` + Job Detail FE (`JobsJobDetail` host + `JobAnalysisReportModal` / `RecommendedJobReportHeader` / `JobDetailModal`) — serialize fields; href only for http(s) `job_link`.

## Architectural definition

**Patterns to reuse**

* [`patt.entity.batch-processing`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-processing.md>) — `land_meteorite` keeps claim → process claimed rows → release.
* [`patt.entity.batch-criteria`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-criteria.md>) — qualify/land eligibility stays criteria on the dispatch_task row, not literals on fake company state.

**New patterns proposed**

* none

**Applicable statutes**

* [`stat.logging.info.entity`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>) — land / reparent / state outcomes stay id-pipe entity info lines.
* [`stat.logging.debug`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>) — tracker/meteorite debug detail stays ContextVar-gated.
* [`stat.logging.error`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>) — land loop exceptions logged once at the handler with traceback.
* [`stat.logging.warning`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>) — per-row land failures warn who/why without aborting the batch.

## Acceptance criteria

1. After Susan runs the shipped backfill SQL (and for all new lands), every job has `source_entity_type` in (`company`,`meteorite`) and non-empty `source_entity_id`. Fail: null/blank parent fields, or type outside that pair. Boot/seed alone must **not** rewrite existing job parents (`grep`/code review: no auto UPDATE of job parents in `SEED_CONFIG` / startup).
2. Prefer-repurpose path: either `job.source` values are only `company`|`meteorite` (no `gazed`) **or** `job.source`/`JOB_SOURCES` are gone and `source_entity_type` is the only parent SoT. Fail: both a live `gazed` meaning and a separate `source_entity_type` both acting as track authority.
3. `grep -rn "ensure_meteorite_company" src/core/meteorite.py` shows no call whose only purpose is to satisfy a required job company parent on land→create. Fail: land still parents via `meteorite-*` / stem placeholder short_name.
4. A meteorite-parented job with real `company_id` is claimed/run by `qualify_meteorite`, not gazed title-pattern fail-early. Fail: track flips to gazed solely because `company_id` is set.
5. Gazed→meteorite match keeps the same `astral_job_id`, ends meteorite-parented at `METEORITE_NEW`, prior gazed states remain in `state_history`. Fail: second row or wiped history.
6. After land, `job.job_link` equals `meteorite.link` for that row’s linked job. Fail: inherited link missing when `meteorite.link` is set.
7. Link check that returns bot-block does **not** fail the land outcome solely for that reason; when the check is not bot-blocked, job description text gains the scraped/append JD content. Fail: land errors only because of bot-block, or non-blocked JD never appended when content was returned.
8. Job Detail “open listing” is a navigable href only when `job.job_link` starts with `http://` or `https://`; non-http inherited text is still shown as text. Fail: breadcrumb/`email-` token used as href, or non-http `job_link` hidden with no text surface.
9. Track/parent selection paths use `source_entity_type` (or its config helper), not legacy `source == "meteorite"` / company state `METEORITE` as SoT. Fail: qualify/gazer still keys off the old flag meaning.

## Open questions

none

## Proposed child tickets

#### 1!!!: **Job source_entity schema + config SSOT + manual backfill SQL - Ada**

Owns schema reshape (repurpose `job.source` → `company`|`meteorite` **or** drop + add `source_entity_type`), nullable `company_id`, candidate_id resolution for meteorite parents, config validators, and the **Susan-runnable** backfill SQL (no auto seed). Does not own land/tracker write semantics or UI.  
**Citations:** `patt.entity.batch-criteria`; `stat.logging.debug`.  
**Scope:** `src/utils/config.py` — source-entity type literals / validators; repurpose or retire `JOB_SOURCES` per Functional scope; breadcrumb format + timezone clock helpers; METEORITE_CONFIG keys that still force placeholder company parents. `src/data/database.py` — job schema for `source_entity_type`/`source_entity_id` (via repurposed `source` or new columns), nullable `company_id` replacing required `company`; candidate_id resolution when parent is meteorite; save/get/list/dedupe helpers + header inventory; **operator SQL backfill script** (docs or `data/` SQL file — not auto-run seed). Technical: `config` — closed set `company` | `meteorite` for parent/track; migrate `gazed`→`company` when repurposing `job.source`; else add `source_entity_type` and delete `JOB_SOURCES` / transition helpers; breadcrumb format string + clock shape. `database` job table — required parent fields after backfill; nullable `company_id` instead of NOT NULL `company`; `_resolve_job_candidate_id` (or successor) from meteorite row when parent is meteorite. `database` writers/dedupe — accept meteorite parent + optional `company_id`; gazed→meteorite supersede finds same row; `meteorite.astral_job_id` stays 1:1 on land. **Backfill artifact** — one Susan-runnable SQL script mapping existing `meteorite-*`/stem-parented jobs via `meteorite.astral_job_id` (and gazed defaults) to the new parent fields; **not** invoked from `SEED_CONFIG` / boot.  
**Estimate: 5**

#### 2!!: **Tracker + land parent writes, link inherit, bot-block JD append - Hedy**

After #1: create/supersede under meteorite parent; optional real `company_id`; gazed→meteorite same-row flip; `job.job_link` inherits `meteorite.link`; link check does not fail land on bot-block; append non-blocked JD to existing text. Does not own breadcrumb string authorship or consumer rewires.  
**Citations:** `patt.entity.batch-processing`, `stat.logging.info.entity`, `stat.logging.error`, `stat.logging.warning`, `stat.logging.debug`.  
**Scope:** `src/core/tracker.py` — `save_meteorite_job` / create / gazed→meteorite supersede write parent fields + optional `company_id`; stop requiring meteorite company short_name as parent; stop using old `gazed`/`meteorite` source flag as track authority once repurposed/dropped. `src/core/meteorite.py` — land parents to meteorite row; `job.job_link` inherits `meteorite.link`; link check does not fail land on bot-block; append non-blocked JD content to existing text; stop `ensure_meteorite_company` as job parent; optional real `company_id` (breadcrumb *format* for no-URL outcomes is #3). Technical: `tracker.save_meteorite_job` — create under meteorite parent; gazed match flips parent to meteorite, keeps `company_id`, state `METEORITE_NEW`, appends history; no second row; no clobber of existing meteorite-parented row. `meteorite` land — inherit `meteorite.link` → `job.job_link`; on link check, bot-block does not fail the land; if not bot-blocked, append JD text onto existing job description content; stop `ensure_meteorite_company` solely for `job.company`.  
**Estimate: 5** — after #1.

#### 3!: **Email breadcrumb on [meteorite.link](<http://meteorite.link>) (forward peel + timezone clock) - Katherine**

Owns no-URL email breadcrumb authorship (`single_jd_no_link` / `multi_jd_inline`): peel inner From/To when forwarded; format clock in `contact.timezone`. Does not own parent columns, bot-block append, or Job Detail.  
**Citations:** `stat.logging.info.entity`, `stat.logging.debug`.  
**Scope:** `src/core/meteorite.py` — classify/land path that authors non-http `meteorite.link` breadcrumbs (forward peel + timezone clock); does not re-own parent/inherit/append writes from #2. `src/utils/config.py` — only calling the breadcrumb format / timezone helpers introduced in #1 (no second SSOT). Technical: breadcrumb writer for text outcomes — agent returns from / to / sent-at; Python formats clock in `contact.timezone`; forwarded mail uses inner headers; `source_ref` stays unused.  
**Estimate: 3** — after #1; coordinates with #2 inherit of `meteorite.link` → `job.job_link`.

#### 4: **Track routing + Job Detail / jobs API consumers - Ada**

Rewires qualify/consult/gazer so track follows `source_entity_type`; gazed ingest writes company parent fields; jobs API + Job Detail show inherited `job_link` with http(s)-only href.  
**Citations:** `patt.entity.batch-criteria`, `stat.logging.debug`.  
**Scope:** `src/core/consult.py` — qualify / land-packet / track selection uses `source_entity_type` so meteorite+`company_id` stays on meteorite GDL. `src/core/gazer.py` and/or `src/core/tracker.py` gazed ingest — gazed creates set `source_entity_type=company`, `source_entity_id=short_name`, `company_id` to that employer when known. `src/ui/api/api_jobs.py` — expose parent fields, nullable `company_id`, and `job_link` (inherited) for detail. `src/ui/frontend/src/pages/JobsJobDetail.tsx` — deeplink host for Job Detail (prefetch/mount only). `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`, `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`, and `src/ui/frontend/src/components/JobDetailModal.tsx` — show inherited `job_link` text; “open listing” / title / Link-row href only when `http(s)` (non-http text still shown; no new meteorite pages). Technical: `consult` / consumers — track from `source_entity_type` (or single config helper), not company state `METEORITE` and not legacy `source == "meteorite"` meaning. `gazer` create — company parent + `company_id` for gazed employer. `api_jobs` + Job Detail FE (`JobsJobDetail` host + `JobAnalysisReportModal` / `RecommendedJobReportHeader` / `JobDetailModal`) — serialize fields; href only for http(s) `job_link`.  
**Estimate: 3** — after #2.

**Monolith check:** Functional scope has 7 capabilities; 4 children — OK.

**Scope partition check:** Each Component/Technical item appears in exactly one child Scope block (#3 calls #1 format helpers only).

---

## Original brief

Jobs currently always hang off a company row. Meteorite ingest fakes that with placeholder / stem-keyed METEORITE companies (`meteorite-{candidate_id}`, `{stem}-{candidate_id}`) plus a weaker `job.source` (`gazed` | `meteorite`). The meteorite table is now a first-class entity (AST-1555 / AST-1620). Jobs should parent to **where the listing came from**, optionally attach a **real employer**, and carry a **candidate-facing breadcrumb** so a high-scoring job can be found again to submit a resume.

`source_ref` on `meteorite` is unused on purpose (no `email-<mid>` synthesis). `source_id` is the machine handle (Gmail mid, Slack ts). Use `meteorite.link` for the human-readable reference.

## Locked decisions (2026-09-15)

### Job pointers

| Column | Meaning |
| -- | -- |
| `source_entity_type` | `company` (gazer) or `meteorite` (staging row). This is the ingest parent and the analysis **track**. |
| `source_entity_id` | Company `short_name`, or meteorite row `id` (store as text). |
| `company_id` | Nullable real employer (`short_name`). Never a fake `meteorite-*` company. Website / culture / scan data when we have it. |

Track follows `source_entity_type`, not whether `company_id` is set. A meteorite with `company_id` = Acme still runs `qualify_meteorite` → meteorite GDL (score_floor 0, no title-pattern kill). Attaching Acme must not yank it onto gazed fail-early.

`job.source` and placeholder METEORITE companies stop being job parents once this ships.

### Same job row on gazed → meteorite

If a posting was already gazed (and may have failed early) and later arrives as a meteorite: **same** `astral_job_id`. Keep `company_id` if known. Flip parent to the meteorite row. State → `METEORITE_NEW`. Meteorite GDL runs in full. Gazed outcomes stay in `state_history` — do not create a second job row.

### `meteorite.link` (candidate-facing)

* `link_list` / `single_jd_with_more`: keep the `http(s)` posting URL (already written).
* `single_jd_no_link` / `multi_jd_inline`: write an inbox breadcrumb, not a fake ATS id.
* Format: `From:<email> M/D H:MM <timezone> To:<email>`
* **From / To:** original sender and original To (the candidate’s inbox). If the candidate **forwarded** the listing to the platform, envelope From is them — Ruth must peel the inner headers. Direct send to the platform uses envelope From/To.
* **Clock:** original send time, formatted in `contact.timezone` (Manage Candidate timezone). Python formats `M/D H:MM` + zone label; the agent returns from / to / sent-at, it does not invent the clock string.
* Land copies `link` onto `job.job_link` only when it is `http(s)` so Job Detail “open listing” stays a real href. Email breadcrumbs stay on `meteorite.link`; the job points at the meteorite via `source_entity_*`.

Slack / paste breadcrumbs are out of this ticket unless called out in define.

## Why

Gazed jobs can fail early (title pattern, JD floor) and never get the full GDL. Meteorite analysis is the complete set. Re-parenting the **same** row lets the candidate get that full pass without losing company website data or the gazed history.

## Adjacent

* AST-1555 — meteorite staging table (source_kind / source_id / empty source_ref / link).
* AST-1620 — meteorite as dispatch `entity_type`.
* AST-1469 — `job.source` gazed→meteorite one-way (this replaces that as SoT).
* AST-1484 / AST-1493 / AST-1495 — stem-keyed meteorite companies as job parents (retire that role).

## Out of scope unless define says otherwise

* New meteorite UI chrome beyond what land/Job Detail already need.
* Changing company PK off `short_name`.
* Two-row duplicate (gazed leftover + new meteorite job).

### Comments

#### chuckles — 2026-09-17T01:35:19.798Z
AST-1704 Scope amended — Job Detail href surfaces named for AC5 (modal/header, not only JobsJobDetail host).

#### chuckles — 2026-09-16T23:35:29.975Z
[check-linear] Discussion — answered (@susan)

Yes — partial today, still worth finishing.

Already shipped pieces: `job.source` gazed|meteorite + one-way supersede (AST-1469), meteorite staging + `meteorite.link` + `astral_job_id` (AST-1555), meteorite as dispatch entity (AST-1620). Land still parents via `ensure_meteorite_company` / required `job.company`; no `source_entity_type`/`source_entity_id`; nullable real `company_id` separate from track; inbox breadcrumb format + http(s)-only `job.job_link` copy; track keyed off parent instead of `job.source`/fake METEORITE companies.

So the ticket is still the gap between “provenance flag + placeholder company” and the locked parent model. Without it, meteorite+real-employer keeps fighting gazed fail-early, and no-link listings still lack a durable candidate-facing breadcrumb on the job’s parent.

#### susan — 2026-09-16T23:34:09.556Z
@chuckles I think it is possible that we have implemented this idea partially at this point, but not completely. Would you agree with that observation and do you feel that implementing this ticket would still be valued?

#### chuckles — 2026-09-15T23:21:47.724Z
@susan

1. Drop the `job.source` column and `JOB_SOURCES` helpers in this epic once `source_entity_type` is SoT, or leave the column unused/deprecated for a later cleanup ticket?
2. When `job.job_link` is empty and the breadcrumb lives only on `meteorite.link`, must Job Detail (or the jobs API payload it already uses) **display** that breadcrumb text in this epic, or is parentage via `source_entity_*` enough for UAT without new detail chrome?
3. Existing live jobs still parented under `meteorite-*` / stem companies: best-effort backfill in this epic (prefer `meteorite.astral_job_id` reverse link → `source_entity_type=meteorite`), or only enforce the new parent model for new lands + gazed→meteorite flips going forward?

---

_Implementation detail may live in git history on `origin/dev`._
