# AST-669 — find_job_page job doesn't display the agent content

<!-- linear-archive: AST-669 archived 2026-06-23 -->

## Linear archive (AST-669)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-669/find-job-page-job-doesnt-display-the-agent-content  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-716; related: AST-671; related: AST-328

### Description

## Purpose

Susan runs **find_job_page** from Scheduled Actions / dispatch and uses **Execution History** to inspect prompt, model response, and cost — the same way she does for consult and artifact tasks. On staging batch `find_job_page-22f8263f-c8a5-420d-b193-7a3974afabdc` (komodohealth), the dispatch completed and the company moved **TO_WATCH → NO_JOBLIST** in under a second with **no agent data** in the batch inspector. That blocks UAT: Susan cannot tell whether the locate pipeline ran correctly, failed before any LLM call, or failed to persist agent content.

Susan's direction: when a company already has a **job_site** that differs from **company_website**, **find_job_page** should use that job site and attempt to parse the job list — not exit immediately because **possible job links** (PJL: link ids from prefilter stored in company data) are empty.

## Functional scope

* **Job_site-aware locate:** When **find_job_page** runs for a company that has a populated **job_site** distinct from **company_website**, the task attempts to locate and parse the job list from that job site — the same product outcome Susan expects when a careers URL is already known. Zero PJLs alone does not justify an instant **NO_JOBLIST** exit if a usable **job_site** exists.
* **Real agent content in Execution History:** When **find_job_page** invokes roster LLM steps (**select_job_page**, **parse_job_list** when chained), Susan can open that batch in Execution History and see stored prompt blocks and model response — not an empty agent-data modal.
* **Correct batch association:** Agent-data blocks are keyed to the **batch_id** on the Execution History row Susan clicked (consistent with per-hop history from [AST-528](https://linear.app/astralcareermatch/issue/AST-528)).
* **Staging repro:** The komodohealth scenario (0 PJLs, nav_links present, fast **NO_JOBLIST**, empty agent-data modal) is a first-class acceptance case — after fix, either the job-site path runs with inspectable agent content, or Susan can see from logs and history why a legitimate no-call outcome occurred (no synthetic placeholder summaries).

## Boundaries

* Does **not** fix **company.job_site** overwritten with **company_website** — [AST-671](https://linear.app/astralcareermatch/issue/AST-671/companyjob-site-is-overwritten-with-companycompany-website).
* Does **not** include [AST-666](https://linear.app/astralcareermatch/issue/AST-666/find-job-page-is-well-and-truly-borked) (long-run / hang placeholder); stay limited to this staging repro and agent-data visibility.
* Does **not** add company-modal agent-story tabs ([AST-328](https://linear.app/astralcareermatch/issue/AST-328/company-modal-enhancements) backlog).
* Does **not** invent synthetic agent-data blocks when no LLM call occurred — Susan expects the correct roster path to run and produce real agent content when a job site is available.
* Must not break agent-data inspection for other dispatch tasks, ad-hoc workbench runs ([AST-515](https://linear.app/astralcareermatch/issue/AST-515)), or consult batches.

## Acceptance criteria

1. On staging, re-run **find_job_page** for komodohealth (or equivalent company at **TO_WATCH** with a verified **job_site** distinct from **company_website** and 0 PJLs): the run does **not** instantly land **NO_JOBLIST** solely because PJLs are empty when **job_site** is usable.
2. When that run invokes roster LLM steps, Execution History agent-data inspection for the batch shows readable **TASK** and **RESPONSE** (and related prompt block types).
3. Agent-data rows use the batch_id on the Execution History row Susan clicked.
4. If no LLM call is genuinely correct after the job-site path is evaluated, Susan can determine that from execution logs and history without a misleading empty modal that looks like a persistence failure.
5. Other dispatch task types and ad-hoc workbench history rows still show agent data as before.

## Dependencies and blockers

* [AST-330](https://linear.app/astralcareermatch/issue/AST-330/create-agent-data-as-pure-data-storage) — Done.
* [AST-528](https://linear.app/astralcareermatch/issue/AST-528/per-hop-execution-history-for-daisy-chained-tasks) — Done.
* [AST-469](https://linear.app/astralcareermatch/issue/AST-469/roster-locateparse-split-run-next-job-list-visible-jobs-found-path) — Done; **JOBS_FOUND** / **job_site** scrape path is the reference behavior for known careers URLs.
* [AST-671](https://linear.app/astralcareermatch/issue/AST-671/companyjob-site-is-overwritten-with-companycompany-website) — related; not a blocker.
* [AST-666](https://linear.app/astralcareermatch/issue/AST-666/find-job-page-is-well-and-truly-borked) — related placeholder; explicitly out of scope.

## Open questions

none.

---

## Original brief

find_job_page-22f8263f-c8a5-420d-b193-7a3974afabdc just ran, but when I opened the modal, it said no agent data existed for the job.

This was the log output:
[2026-06-15 16:40:58] INFO dispatch.scheduler: Dispatching find_job_page — 1 available, batch find_job_page-22f8263f-c8a5-420d-b193-7a3974afabdc

[2026-06-15 16:40:58] INFO src.core.dispatcher: dispatcher._run_dispatch_loop index 1/1 find_job_page -> loop iteration 1 starting

[2026-06-15 16:40:58] INFO src.core.dispatcher:  | available=1 effective_min=1 max_runs=1 draining=False entity_batch_id=find_job_page-22f8263f-c8a5-420d-b193-7a3974afabdc
[2026-06-15 16:40:58] INFO src.core.dispatcher: dispatcher._run_task index 1/1 find_job_page -> running batch

[2026-06-15 16:40:58] INFO src.core.dispatcher:  | batch_size=5 batch_id=find_job_page-22f8263f-c8a5-420d-b193-7a3974afabdc entity_type='company' trigger_state='TO_WATCH'
[2026-06-15 16:40:58] INFO src.core.dispatcher: dispatcher._run_unified index 1/1 company/TO_WATCH -> claimed 1 entity/entities

[2026-06-15 16:40:58] INFO src.core.dispatcher:  | task_key=find_job_page batch_id=find_job_page-22f8263f-c8a5-420d-b193-7a3974afabdc batch_call_mode=False dispatch batch_size=5 claim_cap=None claim_states=['TO_WATCH']
[2026-06-15 16:40:58] INFO src.core.dispatcher: dispatcher._run_unified index 1/1 komodohealth -> claimed

[2026-06-15 16:40:58] INFO src.core.dispatcher:  | entity_type=company trigger_state=TO_WATCH state='TO_WATCH'
[2026-06-15 16:40:58] INFO src.core.roster: [ ~ ] [find_job_page] komodohealth: 0 PJLs, nav_links=3427 chars

[2026-06-15 16:40:58] INFO src.core.roster: [komodohealth] company state TO_WATCH -> NO_JOBLIST (batch_id=find_job_page-22f8263f-c8a5-420d-b193-7a3974afabdc)

[2026-06-15 16:40:58] INFO src.core.dispatcher:  | batch end summary={'total_processed': 1, 'total_passed': 0, 'total_failed': 1, 'total_errors': 0}
[2026-06-15 16:40:58] INFO src.core.dispatcher:  | runner returned summary={'total_processed': 1, 'total_passed': 0, 'total_failed': 1, 'total_errors': 0}
[2026-06-15 16:40:58] INFO src.core.dispatcher:  | iteration 1 summary processed=1 passed=0 failed=1 errors=0 accumulated={'total_processed': 1, 'total_passed': 0, 'total_failed': 1, 'total_errors': 0}
[2026-06-15 16:40:58] INFO src.core.dispatcher:  | loop stop: max_runs reached max_runs=1 run_count=1

### Comments

#### chuckles — 2026-06-15T18:09:11.928Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-669 (parent) | ftr/AST-669-find-job-page-job-doesnt-display-the-agent-content |
| AST-674 | sub/AST-669/AST-674-job-site-find-job-page-agent-data |

**Epic worktree:** `astral-AST-669/` — one active sub checked out at a time.

**Parent:** AST-669

— Chuckles

#### chuckles — 2026-06-15T17:02:14.366Z
@susan — open questions on the definition (answer in-thread when you can):

1. For komodohealth at **TO_WATCH** with **0 PJLs** but nav_links present: should **find_job_page** have invoked **select_job_page** anyway, or is **NO_JOBLIST** without an LLM call correct and the fix is only better empty-state messaging in the inspector?
2. Should this ticket absorb any of **AST-666** (long-run batches with no agent data), or stay limited to the fast-fail staging repro and inspector behavior?
3. When early exit occurs, is a synthetic inspectable summary (inputs + reason, no LLM blocks) sufficient, or must every **find_job_page** dispatch always produce real **select_job_page** agent_data?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
