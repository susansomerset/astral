# AST-1753 — stage_email_meteorite enhancements

<!-- linear-archive: AST-1753 archived 2026-09-24 -->

## Linear archive (AST-1753)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1753/stage-email-meteorite-enhancements  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Email (and other ingress) meteorites already can carry an optional `job_title` on the Ruth classify response and on the meteorite row, but Ruth is never asked for a title and the dispatch land path never writes that column onto `job`. Titles often sit in the email subject and are useful before qualify. When Ruth omits `jd_text` on a text landable outcome, staging today fails the map instead of keeping the original subject-and-body blob as row content. This epic teaches the live classify prompts (`stage_meteorite` — the Ruth task behind mailbox `stage_email_meteorite`) to return an optional title, keeps those prompts free of an inlined `$RESPONSE_SCHEMA`, falls back to the ingress blob (subject and body) when `jd_text` is missing, and flows a staged title onto the job row when the meteorite lands.

## Functional scope

* Stage classify prompts ask Ruth for an optional job title on each returned jobs item when she can tell what the role is called — prefer the email subject when it names the role; omit or leave empty when unknown. Do not invent titles.
* Those same prompts do **not** embed `$RESPONSE_SCHEMA` (or an equivalent full schema dump). Downstream validation against `TASK_CONFIG["stage_meteorite"]["response_schema"]` stays as today; missing optional fields remain allowed.
* When a text landable stage outcome returns a jobs item with blank/missing `jd_text`, meteorite row `content` falls back to the original ingress blob text for that classify call (subject and body together — the same CONTENT Ruth saw). Prefer explicit `jd_text` when present. Do not invent JD text.
* When a meteorite lands and the staged row has a non-empty `job_title`, that title is written onto the created/updated `job` record. If land-time qualify/enrich already supplies a non-empty title, that enrich title wins; otherwise the staged meteorite title is used.

## Component scope

* `data/admin/agent_task.json` — **modified** — `stage_meteorite` cache/user prompts instruct optional `job_title` (subject-prefer); do not add `$RESPONSE_SCHEMA`.
* `src/core/meteorite.py` — **modified** — text-outcome stage map falls back to the classify ingress blob when `jd_text` is blank; dispatch land and public land paths pass staged `job_title` through to `tracker.save_meteorite_job` (enrich title preferred when present).

## Technical scope

* `data/admin/agent_task.json` — update `stage_meteorite` prompt text so each landable jobs item may include optional `job_title`, preferring subject-line titles when present; keep the six closed outcomes and existing electronic-contact / breadcrumb instructions; leave `$RESPONSE_SCHEMA` absent from those prompts.
* `src/core/meteorite.py` — thread the classify ingress blob into the jobs→row mapper; on text landable outcomes, when a jobs item's `jd_text` is blank/missing, set row `content` from that blob instead of failing with missing-`jd_text`; when `jd_text` is present, keep today's prefer-Ruth behavior. In the READY/BOT_BLOCKED dispatch land runner, pass the meteorite row's `job_title` into the Tracker save call when non-empty; in the public land path after enrich, fall back to the meteorite row's `job_title` when enrich omitted one (same preference pattern already used for employer name from scrap metadata).

## Architectural definition

* **Patterns to reuse** — `patt.task.daisy-chain` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.task.daisy-chain.md>)) — title and description content are carried on the meteorite row through stage → scrape → land; land and stage fallback must consume that row/blob path, not invent a parallel extract that ignores staged fields.
* **New patterns proposed** — none.
* **Applicable statutes** — `stat.logging.debug` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)) — stage fallback and land/title wiring stay on existing debug call/response style, no new chatter. `stat.logging.info.entity` ([link](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>)) — land success stays the existing entity info line; do not add title- or fallback-specific info logs.

## Acceptance criteria

1. `rg -n 'job_title' data/admin/agent_task.json` shows `stage_meteorite` prompt text instructing optional job title / subject preference. Fail if only unrelated tasks mention `job_title`, or if `stage_meteorite` prompts still never name the field.
2. `rg -n '\$RESPONSE_SCHEMA' data/admin/agent_task.json` shows no match inside the `stage_meteorite` prompt fields (cache_prompt / user_prompt / nocache_prompt). Fail if `$RESPONSE_SCHEMA` was added to that task's prompts.
3. `python3 -c 'from src.utils.config import TASK_CONFIG; s=TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]["job_title"]; assert s.get("required") is False'` exits 0. Fail if `job_title` is missing or required.
4. After a landable stage that returns `job_title` "Senior Widget Engineer" on a jobs item, the meteorite row's `job_title` column is that string (existing stage map). Fail if the column stays NULL while Ruth returned the field.
5. A text landable stage outcome whose jobs item omits `jd_text` (or returns blank) inserts a meteorite row whose `content` equals the classify ingress blob (subject+body text passed into that stage call), and does **not** return the map error `text scrap missing jd_text`. Fail if blank `jd_text` still errors that string, or if `content` is NULL while the blob was non-empty.
6. A text landable stage outcome whose jobs item returns non-empty `jd_text` still stores that `jd_text` as `content` (not the full blob). Fail if present `jd_text` is ignored in favor of the blob.
7. `rg -n 'job_title' src/core/meteorite.py` shows the dispatch land runner (`run_land_meteorite`) passing `job_title` into `tracker.save_meteorite_job`. Fail if that call site still omits `job_title=`.
8. Landing a READY meteorite whose row `job_title` is non-empty and whose enrich/qualify title is empty yields a `job` row whose `job_title` equals the meteorite column. Fail if `job.job_title` is NULL/blank while `meteorite.job_title` was set.
9. Landing when enrich/qualify returns a non-empty `job_title` keeps that enrich title on `job` even if the meteorite column differs. Fail if staged title overwrites a non-empty enrich title.

## Open questions

none

## Proposed child tickets

#### 1!: **stage_meteorite job_title prompts - Ada**

Teach `stage_meteorite` agent_task prompts to return optional `job_title` (prefer email subject when it names the role; omit when unknown; never invent). Do not embed `$RESPONSE_SCHEMA`. Does not own stage content fallback or land → job wiring (siblings #2–#3). Confirm optional `job_title` remains on TASK_CONFIG schema (already present — no schema invention).
**Citations:** `patt.task.daisy-chain` (title must be askable at stage so the row can carry it); `stat.logging.debug` / `stat.logging.info.entity` id-only (no logging edits in this child).
**Scope:** `data/admin/agent_task.json` — **modified** — `stage_meteorite` cache/user prompts instruct optional `job_title` (subject-prefer); do not add `$RESPONSE_SCHEMA`. Technical: update `stage_meteorite` prompt text so each landable jobs item may include optional `job_title`, preferring subject-line titles when present; keep the six closed outcomes and existing electronic-contact / breadcrumb instructions; leave `$RESPONSE_SCHEMA` absent from those prompts.
**Estimate: 2**

#### 2!: **Stage jd_text fallback to ingress blob - Katherine**

On text landable outcomes, when Ruth omits/blanks `jd_text`, set meteorite `content` from the classify ingress blob (subject and body) instead of failing the map. Prefer explicit `jd_text` when present. Does not edit prompts (sibling #1) or land → job title wiring (sibling #3).
**Citations:** `patt.task.daisy-chain` (content stays on the meteorite row from the same stage pass); `stat.logging.debug`.
**Scope:** `src/core/meteorite.py` — **modified** — text-outcome stage map falls back to the classify ingress blob when `jd_text` is blank. Technical: thread the classify ingress blob into the jobs→row mapper; on text landable outcomes, when a jobs item's `jd_text` is blank/missing, set row `content` from that blob instead of failing with missing-`jd_text`; when `jd_text` is present, keep today's prefer-Ruth behavior.
**Estimate: 2**

#### 3: **Land staged job_title onto job - Hedy**

When a meteorite lands, flow non-empty staged `job_title` onto the job record; enrich/qualify title wins when present. Does not edit agent_task prompts or stage content fallback (siblings #1–#2). after #1 for full UAT of title end-to-end.
**Citations:** `patt.task.daisy-chain` (consume the staged column through land); `stat.logging.debug`; `stat.logging.info.entity`.
**Scope:** `src/core/meteorite.py` — **modified** — dispatch land and public land paths pass staged `job_title` through to `tracker.save_meteorite_job` (enrich title preferred when present). Technical: in the READY/BOT_BLOCKED dispatch land runner, pass the meteorite row's `job_title` into the Tracker save call when non-empty; in the public land path after enrich, fall back to the meteorite row's `job_title` when enrich omitted one (same preference pattern already used for employer name from scrap metadata).
**Estimate: 2**

**Monolith note:** four functional capabilities across three children (no-schema is a prompt constraint on #1; title ask / content fallback / land title are the separable slices).

**Scope partition note:** child #2 and #3 both touch `src/core/meteorite.py` but disjoint units — #2 owns stage map / blob threading only; #3 owns land save `job_title=` wiring only. No overlapping edit sites.

---

## Original brief

1. The task prompt does not include $RESPONSE_SCHEMA in the message. We are open to variability of what comes back without explicitly providing the response schema.
2. The task prompt does not ask for the JOB TITLE, which is often available in the subject of the email.  Please add this to the response schema (not required, just in case we don't know), and flow the job title to the job table when the meteorite lands.
3. Please also fallback to the original email text (subject and body) if the agent does not return an explicit jd_text.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
