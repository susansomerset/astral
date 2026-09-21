# AST-1527 — Generalize Meteorite Ingress Point

<!-- linear-archive: AST-1527 archived 2026-09-09 -->

## Linear archive (AST-1527)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1527/generalize-meteorite-ingress-point  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** susan  
**Priority / estimate:** Urgent / 8  
**Parent:** —  
**Blocked by / blocks / related:** duplicate: AST-1555

### Description

## Purpose

Inbound meteorite blobs (email HTML, Slack paste, inspector dumps, forwarded threads) are classified today by brittle heuristics or by dumping the whole blob into `land_meteorite` / `qualify_meteorite`. That mis-routes recruiter homepages and thread replies into enrich and fails real type-1 JDs. This epic adds one Little-brain hop, `stage_meteorite`, that answers what the blob is and what scraps are needed to land complete job row(s) — then core lands only when the closed outcome set says so. AST-1457 already shipped land/inbox/mailbox; this fills the classify hole those paths left. Adjacent in flight: AST-1484 company-stem UT (does not own ingress classify). AST-1320 (old `meteorite_email` parse quality) is superseded by this cutover — cancel when this ships if still open.

## Functional scope

1. **Closed-outcome staging task** — Callers pass a candidate-bound blob plus a source handle into `stage_meteorite`. Ruth returns exactly one of six config literals (`single_jd_no_link`, `single_jd_with_more`, `multi_jd_inline`, `link_list`, `not_job_content`, `not_original_posting`) with the matching job scrap payload — never prompt-invented outcome strings.
2. **Source-ref identity for text lands** — When there is no ATS posting URL worth scraping, scraps use synthesized source-refs (`email-…` / configured equivalents for Slack/paste), not invented UUIDs or company homepages as `job_link` / `company_job_id`.
3. **Core map → land** — After the agent, core builds a scrap array and calls existing `land_meteorite` for landable outcomes (types 1–4). Types 2/4 rely on `land_meteorite`'s existing URL scrape path; types 1/3 land as text+source-ref. Types 5/6 never create jobs.
4. **Caller cutover** — Mailbox (`meteorite_email` poller), inbox Land / `fetch_email`, and Contact scrap paths all go through stage before land. Mailbox hygiene (unbound trash, archive-on-success) stays in the callers after staging.
5. **Retire orphan classify** — Remove mechanical `_handle_bound` heuristics and the live Ruth `meteorite_email` parse_modes catalog. Do not leave parse and stage both live. Do not revive `gaze_email` / gazer email HTML ingest.
6. **Debug observability** — When `debug=True` on the stage path, Style D index headers plus `|` working detail show outcome, source handle, scrap count, and land/skip recorded — per AST-538 / Code Rules. No new contract lines when `debug=False`.

## Component scope

* `src/utils/config.py` — **modified** — add `stage_meteorite` TASK_CONFIG + stage config block (closed outcome literals, source-handle / source-ref prefix kinds); split mailbox `meteorite_email` from retired parse coupling (`METEORITE_EMAIL_PARSE_CONFIG` / shared task_key assert).
* `data/admin/agent_task.json` — **modified** — add `stage_meteorite` catalog row (prompts + schema lockstep with TASK_CONFIG); retire live `meteorite_email` parse prompts so parse and stage are not both live.
* `src/core/meteorite.py` — **modified** — public stage entry: blob + source handle → `do_task(stage_meteorite)` → map closed outcomes to scrap array → call existing `land_meteorite`; ignore/fail outcomes create no jobs; Style D when `debug=True`.
* `src/core/consult.py` — **modified** — thin stage invoke helper only if needed so meteorite does not duplicate `do_task` batch-id / live_content assembly (same shape as land enrich helper).
* `src/core/agent.py` — **modified** — only if stage needs a minimal invoke-path note or validation hook; no new provider client.
* `src/core/meteorite_email.py` — **modified** — `_handle_bound` drops mechanical classify tree; bind → stage → archive/skip from stage outcomes; mailbox hygiene stays here.
* `src/core/inbox.py` — **modified** — `_land_bound_inbox_message` / `fetch_email` / admin Land paths call stage instead of raw HTML → `land_meteorite`.
* `src/core/contact.py` — **modified** — `contact_land_meteorite` (and paste/Slack scrap callers on this path) send blob + source handle through stage before land.

## Technical scope

* `src/utils/config.py` — **new** TASK_CONFIG[`stage_meteorite`] response schema (outcome enum + job scrap fields); **new** stage config block for the six outcome literals and source-ref prefix map; **modified** / **retire **`METEORITE_EMAIL_PARSE_CONFIG` parse_modes coupling and the assert that mailbox task_key equals parse task_key; keep `METEORITE_EMAIL_MAILBOX_CONFIG.task_key` as `meteorite_email`.
* `data/admin/agent_task.json` — **new **`stage_meteorite` row (system/user prompts teaching the six outcomes); **modified** retire or empty parse-mode prompts on `meteorite_email` so only stage is the classify hop.
* `src/core/meteorite.py` — **new** public async stage function (name per plan-child under `stage_meteorite` contract): accept candidate id, blob, source kind/id, debug; call agent; map outcomes 1/3 → text+source-ref scraps, 2/4 → URL scraps for existing `land_meteorite` scrape path, 5/6 → structured skip/fail with no land; **no** second Playwright stack.
* `src/core/consult.py` — **new** optional `stage_meteorite` invoke helper (assemble live_content, mint batch id, `do_task`) mirroring land enrich discipline.
* `src/core/agent.py` — **modified** only if schema validation or context_format for `stage_meteorite` needs a one-line wire; else untouched.
* `src/core/meteorite_email.py` — **major modified **`_handle_bound`: remove subject/href/inspector heuristic tree; call stage; drive archive-on-success / leave-in-inbox from stage+land outcomes; keep unbound trash / `last_email_check`.
* `src/core/inbox.py` — **modified **`_land_bound_inbox_message` and selected-ids / `run_fetch_email` land path: stage then land; preserve bind/strip ownership in inbox.
* `src/core/contact.py` — **modified **`contact_land_meteorite`: pass source handle + scrap body into stage; do not call `land_meteorite` with unclassified blobs.

## Architectural definition

**Patterns to reuse**

* `pattern.config.config-block` — closed outcome literals, source-ref prefixes, and TASK_CONFIG row live in config — not inventable strings. [pattern.config.config-block](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>)
* `pattern.agent.prompt-persist-before-provider` — stage_meteorite Ruth call must persist prompt/RESPONSE before provider like other do_task hops. [pattern.agent.prompt-persist-before-provider](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/agent/pattern.agent.prompt-persist-before-provider.md>)
* `pattern.batch.entity-agent-responses` — stage agent_data keyed to candidate + batch; latest RESPONSE is the stage verdict. [pattern.batch.entity-agent-responses](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/batch/pattern.batch.entity-agent-responses.md>)
* `pattern.layers.import-discipline` — meteorite owns stage+land; mailbox/inbox/contact call in; no Gmail inside meteorite. [pattern.layers.import-discipline](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/layers/pattern.layers.import-discipline.md>)

**New patterns proposed**

* none — meteorite-local stage-before-land orchestration; promote to catalog only if a second ingress surface copies it later.

**Applicable statutes**

* `astral.config.config-source-of-truth` — outcome set and source-ref prefixes are config SSOT. [astral.config.config-source-of-truth](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>)
* `astral.standards.no-hardcoded-sets` — six outcomes + source kinds are named config sets. [astral.standards.no-hardcoded-sets](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>)
* `astral.seed.agent-tables-in-repo-json` — stage_meteorite prompts land in data/admin/agent_task.json. [astral.seed.agent-tables-in-repo-json](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/seed/astral.seed.agent-tables-in-repo-json.md>)
* `astral.seed.archie-catalog-wins` — do not re-seed deleted catalog rows; cutover retires parse, adds stage. [astral.seed.archie-catalog-wins](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/seed/astral.seed.archie-catalog-wins.md>)
* `astral.seed.define-approved` — new agent_task key requires this define approval. [astral.seed.define-approved](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/seed/astral.seed.define-approved.md>)
* `astral.agent.do-task-delegation` — stage invokes Ruth only via do_task. [astral.agent.do-task-delegation](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/agent/astral.agent.do-task-delegation.md>)
* `astral.standards.debug-contract-gated` — Style D only when debug=True on stage path. [astral.standards.debug-contract-gated](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>)
* `astral.standards.names-not-ticket-ids` — task_key stage_meteorite — no ticket ids in symbols. [astral.standards.names-not-ticket-ids](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.names-not-ticket-ids.md>)
* `astral.layers.import-direction` — core callers → meteorite; external scrape stays behind existing land path. [astral.layers.import-direction](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.import-direction.md>)
* `astral.layers.core-vs-external-bright-line` — Playwright scrape remains external; stage does not invent a second scrape stack. [astral.layers.core-vs-external-bright-line](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.core-vs-external-bright-line.md>)
* `astral.standards.in-scope-only` — land_meteorite / qualify_meteorite / Tracker save stay out of rewrite. [astral.standards.in-scope-only](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)
* `astral.standards.dry-and-focused-functions` — one public stage entry shared by mailbox, inbox, Contact. [astral.standards.dry-and-focused-functions](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>)
* `astral.standards.public-then-helpers` — public stage_meteorite first in module layout. [astral.standards.public-then-helpers](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.public-then-helpers.md>)
* `orch.pipeline.plan-is-bible` — child plans may not invent outcomes outside this definition. [orch.pipeline.plan-is-bible](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/orchestration/pipeline/orch.pipeline.plan-is-bible.md>)
* `orch.pipeline.call-susan-for-product-decisions` — outcome vocabulary is product law from this brief. [orch.pipeline.call-susan-for-product-decisions](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/orchestration/pipeline/orch.pipeline.call-susan-for-product-decisions.md>)
* Universal active set also applies to product code in this epic (full corpus load at review).

## Acceptance criteria

1. Given a bound email whose body is an original JD with no posting URL, staging returns `single_jd_no_link` and `land_meteorite` creates a meteorite job whose `job_link`/`company_job_id` are source-refs — not a company homepage URL.
2. Given a blob with one JD plus a real posting URL, staging returns `single_jd_with_more` and land scrapes that URL (existing land scrape path) without treating a bare recruiter homepage as the posting URL.
3. Given one blob with several inline original JDs, staging returns `multi_jd_inline` and land creates one job per scrap (array), each with source-refs.
4. Given a link-list blob (Dice/inspector multi-href), staging returns `link_list` and land receives one scrap per job-page URL.
5. Given non-job content or a thread/reply about an in-play job, staging returns `not_job_content` or `not_original_posting` and no job row is created.
6. Mailbox `meteorite_email`, inbox Land/`fetch_email`, and Contact land paths each invoke stage before land; mechanical subject/href/inspector classify is gone from `_handle_bound`.
7. `TASK_CONFIG` / `agent_task` expose `stage_meteorite` with the six outcome literals; live `meteorite_email` parse_modes classify is not also live; mailbox poller key remains `meteorite_email`.
8. `land_meteorite` remains the write API; `qualify_meteorite` remains post-create enrich only (no METEORITE_NEW claim from stage).
9. With `debug=True`, stage logs Style D found-vs-recorded lines for outcome and scraps; with `debug=False`, no new debug contract noise.

## Open questions

none

## Proposed child tickets

#### 1!!: **stage_meteorite catalog + config literals - Ada**

Owns the closed outcome vocabulary and Ruth catalog: `TASK_CONFIG["stage_meteorite"]`, stage config block (outcomes + source-ref prefixes), and `data/admin/agent_task.json` row. Retires live parse_modes / `METEORITE_EMAIL_PARSE_CONFIG` coupling so mailbox `meteorite_email` stays the poller only. Does not implement core stage orchestration or caller cutover (after #1 → #2 / #3).
**Citations: **`pattern.config.config-block`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.seed.agent-tables-in-repo-json`, `astral.seed.archie-catalog-wins`, `astral.seed.define-approved`, `astral.standards.names-not-ticket-ids`
**Scope: **`src/utils/config.py` — **modified** — add `stage_meteorite` TASK_CONFIG + stage config block (closed outcome literals, source-handle / source-ref prefix kinds); split mailbox `meteorite_email` from retired parse coupling (`METEORITE_EMAIL_PARSE_CONFIG` / shared task_key assert).
`data/admin/agent_task.json` — **modified** — add `stage_meteorite` catalog row (prompts + schema lockstep with TASK_CONFIG); retire live `meteorite_email` parse prompts so parse and stage are not both live.
`src/utils/config.py` — **new** TASK_CONFIG[`stage_meteorite`] response schema (outcome enum + job scrap fields); **new** stage config block for the six outcome literals and source-ref prefix map; **modified** / **retire **`METEORITE_EMAIL_PARSE_CONFIG` parse_modes coupling and the assert that mailbox task_key equals parse task_key; keep `METEORITE_EMAIL_MAILBOX_CONFIG.task_key` as `meteorite_email`.
`data/admin/agent_task.json` — **new **`stage_meteorite` row (system/user prompts teaching the six outcomes); **modified** retire or empty parse-mode prompts on `meteorite_email` so only stage is the classify hop.
**Estimate: 5**

#### 2!: **Core stage → scrap map → land_meteorite - Hedy**

Public stage entry in meteorite (plus consult/`do_task` helper if needed): blob + source handle → agent → map six outcomes to scraps → `land_meteorite` or skip/fail. Reuses land's URL scrape for types 2/4; no second Playwright stack; Style D when debug. Does not retarget mailbox/inbox/Contact (after #2 → #3). Depends on #1 catalog/schema.
**Citations: **`pattern.agent.prompt-persist-before-provider`, `pattern.batch.entity-agent-responses`, `pattern.layers.import-discipline`, `astral.agent.do-task-delegation`, `astral.standards.debug-contract-gated`, `astral.layers.import-direction`, `astral.layers.core-vs-external-bright-line`, `astral.standards.dry-and-focused-functions`, `astral.standards.public-then-helpers`
**Scope: **`src/core/meteorite.py` — **modified** — public stage entry: blob + source handle → `do_task(stage_meteorite)` → map closed outcomes to scrap array → call existing `land_meteorite`; ignore/fail outcomes create no jobs; Style D when `debug=True`.
`src/core/consult.py` — **modified** — thin stage invoke helper only if needed so meteorite does not duplicate `do_task` batch-id / live_content assembly (same shape as land enrich helper).
`src/core/agent.py` — **modified** — only if stage needs a minimal invoke-path note or validation hook; no new provider client.
`src/core/meteorite.py` — **new** public async stage function (name per plan-child under `stage_meteorite` contract): accept candidate id, blob, source kind/id, debug; call agent; map outcomes 1/3 → text+source-ref scraps, 2/4 → URL scraps for existing `land_meteorite` scrape path, 5/6 → structured skip/fail with no land; **no** second Playwright stack.
`src/core/consult.py` — **new** optional `stage_meteorite` invoke helper (assemble live_content, mint batch id, `do_task`) mirroring land enrich discipline.
`src/core/agent.py` — **modified** only if schema validation or context_format for `stage_meteorite` needs a one-line wire; else untouched.
**Estimate: 5**

#### 3: **Caller cutover (mailbox, inbox, Contact) - Katherine**

Wire `meteorite_email` `_handle_bound`, inbox `_land_bound_inbox_message` / `fetch_email` / admin Land, and `contact_land_meteorite` through the public stage entry; keep hygiene/archive in callers. Does not own catalog (#1) or stage core (#2). After #2.
**Citations: **`pattern.layers.import-discipline`, `astral.standards.in-scope-only`, `astral.layers.import-direction`
**Scope: **`src/core/meteorite_email.py` — **modified** — `_handle_bound` drops mechanical classify tree; bind → stage → archive/skip from stage outcomes; mailbox hygiene stays here.
`src/core/inbox.py` — **modified** — `_land_bound_inbox_message` / `fetch_email` / admin Land paths call stage instead of raw HTML → `land_meteorite`.
`src/core/contact.py` — **modified** — `contact_land_meteorite` (and paste/Slack scrap callers on this path) send blob + source handle through stage before land.
`src/core/meteorite_email.py` — **major modified **`_handle_bound`: remove subject/href/inspector heuristic tree; call stage; drive archive-on-success / leave-in-inbox from stage+land outcomes; keep unbound trash / `last_email_check`.
`src/core/inbox.py` — **modified **`_land_bound_inbox_message` and selected-ids / `run_fetch_email` land path: stage then land; preserve bind/strip ownership in inbox.
`src/core/contact.py` — **modified **`contact_land_meteorite`: pass source handle + scrap body into stage; do not call `land_meteorite` with unclassified blobs.
**Estimate: 3**

**Monolith check:** Functional scope has 6 capabilities; 3 children partition catalog, core stage, and caller cutover — intentional split across config/agent vs core vs I/O callers.

**Scope partition check:** every Component/Technical file appears in exactly one child Scope block above.

---

## Original brief

## Original brief (paste-ready)

Name: `stage_meteorite`
 (Do not reuse `meteorite_email` — that key is the candidate-bound mailbox poller. Do not reuse `qualify_meteorite` — that hop enriches a job that already exists.)

Purpose

Inbound meteorite material is a blob (email HTML, Slack paste, forwarded thread, inspector dump). Today we either (a) guess the shape with subject/href heuristics or (b) stuff the whole blob into `land_meteorite` / `qualify_meteorite` and hope. Both dump thread replies and recruiter homepages onto the qualify gate.

Add one Little-brain task that answers: what is this, and what do we need in order to land complete job row(s)? Callers (mailbox, inbox Land, Contact, paste) send the blob plus a source handle. The agent returns one of a closed set of outcomes. Core then scrapes only when told, synthesizes source-refs when there is no ATS URL, and calls `land_meteorite` with an array of scraps. Ignore/fail never create jobs.

Functional scope

Input: candidate-bound blob (text/HTML) + source identity (gmail message id, Slack event, paste session). Not a job-state claim.

Closed outcome set (config literals, not prompt-invented strings):

1. single_jd_no_link — One original JD in the blob; no posting URL worth scraping. Return one job object. `job_link` / `company_job_id` are source-refs (`email-…` / equivalent), not invented UUIDs or company homepages.
2. single_jd_with_more — One JD plus a best “more” / posting URL. Return one job object with that URL as `job_link`; `company_job_id` still source-ref until scrape/qualify extracts a real ATS id.
3. multi_jd_inline — Several type-1 JDs in one blob (no scrape list). Return an array of job objects, each with source-refs.
4. link_list — Series of job-page URLs (Dice list, inspector multi-href, etc.). Return one job record per URL (source + individuated link) for scrape-then-land.
5. not_job_content — Links or text that are not job content. Fail here; do not land.
6. not_original_posting — Reply/thread/noise about a job already in play. Ignore for ingress; do not land.

Core after the agent: scrape only type 2/4 URLs; land type 1/3 as text+source-ref; archive/skip per existing mailbox rules for 5/6. `land_meteorite` stays the write API. `qualify_meteorite` stays post-create enrich. This task does not GDL.

Boundaries

* Does not replace `land_meteorite` or Tracker save/dedupe.
* Does not claim `METEORITE_NEW` or run `qualify_meteorite` dispatch.
* Does not parse Gmail headers in the agent (caller supplies source id + visible blob).
* Attachments remain out of scope.

---

## What this supersedes (clean cutover)

Replace (classify hop — this is the point of the ticket)

1. `src/core/meteorite_email.py` `_handle_bound` — mechanical tree (URL-subject, first href, inspector-tag density, ignore-if-empty-body). That is today’s type 1/2/4/6 guess. It cannot do type 3, type 5, or “thread reply.” After cutover it should only: bind → call `stage_meteorite` → scrape/land from the returned scraps.
2. `inbox.py` `_land_bound_inbox_message` / `run_fetch_email` — stripped HTML straight into `land_meteorite`. Same blob, zero classification.
3. Orphan Ruth parse catalog — `TASK_CONFIG["meteorite_email"]` `parse_modes` (`html_links` / `subject_body`), `METEORITE_EMAIL_PARSE_CONFIG`, and the `agent_task` `meteorite_email` prompts. Two modes, not six; runner already stopped calling them ([AST-1521](https://linear.app/astralcareermatch/issue/AST-1521/meteorite-email-land-meteorite-routing-emailed-job-description-parsed)). Cut over the catalog row to `stage_meteorite` (or retire parse and add a new row). Do not leave both live.

Keep (write / later hops)

* `land_meteorite` + `tracker.save_meteorite_job` — land the array the stager returns.
* `qualify_meteorite` dispatch on `METEORITE_NEW` — title/JD/stem after a row exists. Stop using it as “what is this.”
* Mailbox hygiene (unbound trash, archive-on-success) — stays in `meteorite_email` / inbox, after staging.

Already dead (do not revive)

* `gazer.ingest_meteorite_jobs_from_email_html` — no production callers after [AST-1472](https://linear.app/astralcareermatch/issue/AST-1472/inbox-fetch-email-gaze-email-retarget-meteorite-component).
* `gaze_email.py` — retired.

Why last night’s 7/7 failed under this brief: those Dice/recruiter mails were type 1 (or 2 with a homepage, not a posting URL). Ingress never staged them, so qualify demanded a UUID on a homepage `http` link.

If you want this on Linear as a parent, the natural home is [AST-1457](https://linear.app/astralcareermatch/issue/AST-1457/meteorite-component) (Meteorite component) as a new child — the land/inbox/mailbox work already shipped under that epic and left this hole. I can paste the brief onto a ticket once Linear tools are actually listing issues, or you can drop an id.

### Comments

#### chuckles — 2026-08-29T17:49:19.531Z
AST-1529 REVIEW — merge-child blocked; recalling Betty for squash merge-tests (need true merge so test(AST-1529) is in sub log).

---

_Implementation detail may live in git history on `origin/dev`._
