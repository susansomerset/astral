# AST-889 — fetch_website infinite loop

<!-- linear-archive: AST-889 archived 2026-07-29 -->

## Linear archive (AST-889)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-889/fetch-website-infinite-loop  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

`fetch_website` is spinning forever on companies that already have homepage text and are waiting for a prefilter second strike (e.g. `ey_com`). The dispatcher keeps reclaiming the same pool; each batch skip-logs and leaves state unchanged, so available count never drains. Production dispatch and monitor alerts cannot move past this stuck reclaim cycle. Fix the handoff so homepage-scraped companies leave `fetch_website` alone and progress under prefilter instead of locking the website-fetch loop.

## Functional scope

* Stop the infinite reclaim loop: once a company is already scraped for homepage content and is in the prefilter second-strike holding path, `fetch_website` must not keep claiming and no-opping that company on every dispatch iteration.
* Preserve real re-fetch work: companies that still need a homepage scrape (including genuine first-pass `WEBSITE_FOUND` and infra-retry cases that do **not** already have usable homepage text) still scrape and still move to pass / fail / retry destinations as today.
* Leave second-strike prefilter ownership intact: companies intentionally held for prefilter after homepage text exists remain eligible for prefilter (one automatic retry then terminal error per the AST-881 / AST-882 product contract), not stuck forever under website fetch.
* Dispatch loop termination: a `fetch_website` run facing a pool composed only of those already-scraped second-strike companies finishes (no further claim iterations on that same unchanged set) rather than iterating indefinitely with `processed > 0` and `passed = failed = errors = 0`.
* Debug/UAT observability (backend `debug=True`): for each claimed company, emit a clear per-index outcome showing whether the company was scraped, failed, or intentionally left for prefilter — enough to confirm the loop no longer reclaims no-ops forever (AST-538 style: found vs recorded / index headers).

## Boundaries

* Does not redesign prefilter grading, rubric content, or successful evaluate destinations (`PREFILTER_PASSED` / `PREFILTER_FAILED` / `NO_PREFILTER_JOBLISTS`).
* Does not change the infra-vs-site failure classification contract from AST-850 / AST-854 (Playwright infra → retry once, then terminal unreadability).
* Does not add new company states or new schedulable task keys unless the plan proves a state rename is the only safe product boundary — prefer fixing claim/eligibility ownership over inventing parallel holding states.
* Does not touch job-side gazer paths (`fetch_job_pages`, gaze, title validation) or UI/dispatch admin screens unless a dispatch-row claim definition change is required for the company fix.
* Must not break: first-pass website fetch → `HOMEPAGE_READY`; infra first failure → `WEBSITE_FOUND_RETRY` without homepage text still re-scrapable by `fetch_website`.

## Acceptance criteria

1. With a set of companies that match the production repro (state in the website-fetch claim pool, homepage text already present, destined for prefilter second strike), running `fetch_website` does **not** loop forever reclaiming those same companies; the run ends after a finite number of iterations.
2. Those same companies remain claimable by **prefilter** for the second-strike attempt and still follow one-retry-then-terminal-error behavior from AST-881 / AST-882.
3. A company that needs an actual homepage scrape (no usable homepage text yet) still scrapes under `fetch_website` and lands in the correct pass, fail, or retry holding outcome.
4. A `fetch_website` batch that only contains already-scraped second-strike companies does not accumulate unbounded `total_processed` across endless iterations with zero passes/fails/errors.
5. With `debug=True`, logs show a per-company outcome for skip-vs-scrape paths so UAT can verify the handoff without guessing from aggregate summary rows alone.

## Dependencies and blockers

none. Adjacent shipped context: AST-850 / AST-854 (fetch_website infra retry), AST-881 / AST-882 (prefilter second strike + intentional skip of homepage-ready holding companies for prefilter). Those are Done; this ticket closes the remaining claim-loop hole between those contracts.

## Open questions

none

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-889 (parent) | ftr/AST-889-fetch-website-infinite-loop |
| AST-892 | sub/AST-889/AST-892-stop-fetch-website-prefilter-second-strike-reclaim |

**Epic worktree:** `astral-AST-889/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | 404d4e74-8526-4b0d-bcfd-795a923fc78e |
| Betty | qa | af67b16e-1940-41cf-bc79-cb13adc14cc4 |
| Radia | review | f47ffb7e-6778-42d7-9958-38917b4ecb04 |

---

## Original brief

It's looping infinitely on ey_com and others.

```
2026-07-13 18:40:13  [INFO]   | available=3 effective_min=1 max_runs=0
draining=False entity_batch_id=fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813
2026-07-13 18:40:13  [INFO]  dispatcher._run_dispatch_loop index 2/2
fetch_website -> loop iteration 2 starting
2026-07-13 18:40:13  [INFO]   | iteration 1 summary processed=3
passed=0 failed=0 errors=0 accumulated={'total_processed': 3,
'total_passed': 0, 'total_failed': 0, 'total_errors': 0}
2026-07-13 18:40:13  [INFO]   | runner returned
summary={'total_processed': 3, 'total_passed': 0, 'total_failed': 0,
'total_errors': 0}
2026-07-13 18:40:13  [INFO]   | batch end summary={'total_processed':
3, 'total_passed': 0, 'total_failed': 0, 'total_errors': 0}
2026-07-13 18:40:13  [INFO]   | summary passed=0 failed=0 errors=0
total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
2026-07-13 18:40:13  [INFO]   | summary passed=0 failed=0 errors=0
total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
2026-07-13 18:40:13  [INFO]  gazer.fetch_website_batch index 1/1
allworknow_com -> skip — homepage_text present; leave for prefilter
second strike
2026-07-13 18:40:13  [INFO]  gazer.fetch_website_batch index 1/1
ey_com -> skip — homepage_text present; leave for prefilter second
strike
2026-07-13 18:40:13  [INFO]  gazer.fetch_website_batch index 1/1
fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813 -> batch start 1
company/companies
2026-07-13 18:40:13  [INFO]  gazer.fetch_website_batch index 1/1
fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813 -> batch start 1
company/companies
2026-07-13 18:40:13  [INFO]   | summary passed=0 failed=0 errors=0
total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
2026-07-13 18:40:13  [INFO]  gazer.fetch_website_batch index 1/1
cubefinance_swiss -> skip — homepage_text present; leave for prefilter
second strike
2026-07-13 18:40:13  [INFO]  gazer.fetch_website_batch index 1/1
fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813 -> batch start 1
company/companies
2026-07-13 18:40:13  [INFO]   | entity_type=company
trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND_RETRY'
2026-07-13 18:40:13  [INFO]  dispatcher._run_unified index 3/3
allworknow_com -> claimed
2026-07-13 18:40:13  [INFO]   | entity_type=company
trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND_RETRY'
2026-07-13 18:40:13  [INFO]  dispatcher._run_unified index 2/3 ey_com -> claimed
2026-07-13 18:40:13  [INFO]   | entity_type=company
trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND_RETRY'
2026-07-13 18:40:13  [INFO]  dispatcher._run_unified index 1/3
cubefinance_swiss -> claimed
2026-07-13 18:40:13  [INFO]   | task_key=fetch_website
batch_id=fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813
batch_call_mode=False dispatch batch_size=3 claim_cap=None
claim_states=['WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY']
2026-07-13 18:40:13  [INFO]  dispatcher._run_unified index 1/1
company/WEBSITE_FOUND -> claimed 3 entity/entities
2026-07-13 18:40:13  [INFO]   | batch_size=3
batch_id=fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813
entity_type='company' trigger_state='WEBSITE_FOUND'
2026-07-13 18:40:13  [INFO]  dispatcher._run_task index 1/1
fetch_website -> running batch
2026-07-13 18:40:13  [INFO]   | available=3 effective_min=1 max_runs=0
draining=False entity_batch_id=fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813
2026-07-13 18:40:13  [INFO]  dispatcher._run_dispatch_loop index 1/1
fetch_website -> loop iteration 1 starting
2026-07-13 18:40:13  [INFO]  Dispatching fetch_website — 3 available,
batch fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813
2026-07-13 18:40:27  [INFO]   | task_key=fetch_website
batch_id=fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813
batch_call_mode=False dispatch batch_size=3 claim_cap=None
claim_states=['WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY']
2026-07-13 18:40:27  [INFO]  dispatcher._run_unified index 1/1
company/WEBSITE_FOUND -> claimed 3 entity/entities
2026-07-13 18:40:27  [INFO]   | batch_size=3
batch_id=fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813
entity_type='company' trigger_state='WEBSITE_FOUND'
2026-07-13 18:40:27  [INFO]  dispatcher._run_task index 1/1
fetch_website -> running batch
2026-07-13 18:40:28  [INFO]   | batch_size=3
batch_id=fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813
entity_type='company' trigger_state='WEBSITE_FOUND'
2026-07-13 18:40:28  [INFO]  dispatcher._run_task index 1/1
fetch_website -> running batch
2026-07-13 18:40:28  [INFO]   | available=3 effective_min=1 max_runs=0
draining=False entity_batch_id=fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813
2026-07-13 18:40:28  [INFO]  dispatcher._run_dispatch_loop index 4/4
fetch_website -> loop iteration 4 starting
2026-07-13 18:40:28  [INFO]   | iteration 3 summary processed=3
passed=0 failed=0 errors=0 accumulated={'total_processed': 9,
'total_passed': 0, 'total_failed': 0, 'total_errors': 0}
2026-07-13 18:40:28  [INFO]   | runner returned
summary={'total_processed': 3, 'total_passed': 0, 'total_failed': 0,
'total_errors': 0}
2026-07-13 18:40:28  [INFO]   | batch end summary={'total_processed':
3, 'total_passed': 0, 'total_failed': 0, 'total_errors': 0}
2026-07-13 18:40:28  [INFO]   | summary passed=0 failed=0 errors=0
total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
2026-07-13 18:40:28  [INFO]  gazer.fetch_website_batch index 1/1
allworknow_com -> skip — homepage_text present; leave for prefilter
second strike
2026-07-13 18:40:28  [INFO]   | summary passed=0 failed=0 errors=0
total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
2026-07-13 18:40:28  [INFO]  gazer.fetch_website_batch index 1/1
ey_com -> skip — homepage_text present; leave for prefilter second
strike
2026-07-13 18:40:28  [INFO]  gazer.fetch_website_batch index 1/1
fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813 -> batch start 1
company/companies
2026-07-13 18:40:28  [INFO]  gazer.fetch_website_batch index 1/1
fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813 -> batch start 1
company/companies
2026-07-13 18:40:28  [INFO]   | summary passed=0 failed=0 errors=0
total=1 pass_state='HOMEPAGE_READY' fail_state='CANNOT_READ_WEBSITE'
2026-07-13 18:40:28  [INFO]  gazer.fetch_website_batch index 1/1
cubefinance_swiss -> skip — homepage_text present; leave for prefilter
second strike
2026-07-13 18:40:28  [INFO]  gazer.fetch_website_batch index 1/1
fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813 -> batch start 1
company/companies
2026-07-13 18:40:28  [INFO]   | entity_type=company
trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND_RETRY'
2026-07-13 18:40:28  [INFO]  dispatcher._run_unified index 3/3
allworknow_com -> claimed
2026-07-13 18:40:28  [INFO]   | entity_type=company
trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND_RETRY'
2026-07-13 18:40:28  [INFO]  dispatcher._run_unified index 2/3 ey_com -> claimed
2026-07-13 18:40:28  [INFO]   | entity_type=company
trigger_state=WEBSITE_FOUND state='WEBSITE_FOUND_RETRY'
2026-07-13 18:40:28  [INFO]  dispatcher._run_unified index 1/3
cubefinance_swiss -> claimed
2026-07-13 18:40:28  [INFO]   | task_key=fetch_website
batch_id=fetch_website-b8e2b2dc-d1a9-4d83-bba4-232c0c233813
batch_call_mode=False dispatch batch_size=3 claim_cap=None
claim_states=['WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY']
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
