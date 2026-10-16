# AST-2020 — [✅/Abrams] qualify_job_listings COMPLETED: 2 error(s) / 2 processed | qualify_job_listings-3e0aa3ec-a853-42fa-ad37-63aea7c24a02

<!-- linear-archive: AST-2020 archived 2026-10-16 -->

## Linear archive (AST-2020)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2020/abrams-qualify-job-listings-completed-2-errors-2-processed-qualify-job  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

I thought we had decommissioned VALID_TITLE?  Are we still seeing it in production log content?  The dispatch task should be disabled if the rubric vectors would respond empty as part of the validation.

**Re: VALID_TITLE.** This log is from before the decommission landed. The run was at 2026-10-07 22:19 UTC. Commit `7b2424d4a` ("Stop redundant title screen inside qualify_job_listings") went in at 23:56 UTC the same day and is on `origin/main` and `origin/dev`. Current `qualify_job_listings` no longer calls `gazer.validate_title_batch`, so NEW jobs aren't stamped `VALID_TITLE` on that path anymore. The production log's line numbers (1935/1963/1972) match the old file, not the current one (1957/1979/1988). The `VALID_TITLE` *state* still exists as a legacy drain: it's in `JOB_STATES`, it's in `_qualify_ai_states`, and the `GAZER_CONFIG.validate_title` pass_state remains. Retiring the state itself is separate scope, not this bug.

## As-is

The pre-dispatch empty-render validation (`_evaluate_dispatch_empty_render` in `src/ui/api/api_admin.py`) calls AST-1779's `empty_render_for_prompts` with `entity_contexts=None`. That helper scores only `source: candidate` tokens. `{$RUBRIC_VECTORS}` (and the AST-1405 named rubric pins) are `source: rubric`, meaning per-candidate `rubric_vector` rows for the task's rubric owner. For `qualify_job_listings` the owner is `qualify_job_listings` / artifact `joblist_rubric`. So a candidate with no current joblist rubric still validates `empty_render: false`, AUTO stays on, and Run is allowed. The dispatch then claims jobs, `agent.do_task` refuses the call ("Empty tokens: RUBRIC_VECTORS"), and every claimed job is routed to `ERROR_QUALIFY_JOB_LISTINGS`. In this report that was abrams: 2 jobs claimed, 2 errored.

## To-be

Dispatch validation treats an empty rubric token as non-executable. When `{$RUBRIC_VECTORS}` or any `source: rubric` token in the task's prompts resolves empty for the row's candidate, the row validates `empty_render: true` with that token in `empty_tokens`. Then AST-1780's list enrichment forces AUTO off, the Invalid tooltip names the token (AST-1819), and Run/AUTO-on return the existing 400 "Prompt tokens resolve empty for this candidate". No jobs are claimed or errored because a rubric was never crafted.

## Proposed steps

1. In `_evaluate_dispatch_empty_render`, pass an `entity_contexts` entry keyed `rubric` to `empty_render_for_prompts`. That's AST-1779's documented extension seam, and its manifest test 7 (`test_rubric_scored_only_via_entity_contexts`) already proves rubric tokens score through it. The candidate token view already carries `_astral_candidate_id`, so the `rubric` resolver branch reads the candidate's `rubric_vector` rows exactly as the runtime does.
2. Leave `empty_render_for_prompts`' default (candidate-only, chain ignored, job only via the seam) unchanged so AST-1779's contract and tests still hold.
3. Every existing gate caller picks this up with no further changes, because they all go through `_evaluate_dispatch_empty_render` / `_candidate_dispatch_empty_render_error`: list enrichment with AUTO force-off, save, AUTO-on, and `POST …/run`.

## Component scope

`src/ui/api/api_admin.py` — modified. `_evaluate_dispatch_empty_render` is the single dispatch-validation gate behind list enrichment (AUTO force-off), save, AUTO-on, and Run. Today it passes `entity_contexts=None`, which hides rubric emptiness.

## Technical scope

`src/ui/api/api_admin.py` — modified function `_evaluate_dispatch_empty_render`: supply the `rubric` entity-context key to `empty_render_for_prompts` so empty `source: rubric` tokens flip `empty_render` true for that candidate and task. No new functions, tables, or fields.

## Ancestor candidates

- [ ] AST-1779 — Empty-token predicate helper (dispatch validation) — `docs/features/dispatcher/ast-1779-empty-token-predicate-helper.md`. Owns `empty_render_for_prompts`, which deliberately scores rubric only via `entity_contexts` (manifest test 7, `test_rubric_scored_only_via_entity_contexts`).
- [ ] AST-1780 — List-enrich AUTO-run gates / force AUTO off — `docs/features/dispatcher/ast-1780-list-enrich-auto-run-gates-force-auto-off.md`. Owns the `_evaluate_dispatch_empty_render` call sites (list, save, Run, AUTO-on) that pass `entity_contexts=None`.
- [ ] AST-1766 — Dispatch Validation (parent epic of AST-1779 / AST-1780), which set the "candidate-scoped only this epic" boundary.
- [ ] AST-1405 — Named rubric prompt tokens — `docs/features/foundation/ast-1405-named-rubric-prompt-tokens.md`. Defines the `source: rubric` resolver and pinned owners that the gate would now score.

## Original report

```
2026-10-07 22:19:35  [INFO]  abrams | dispatch job task completed:
qualify_job_listings pass:0 fail:0 error:2 (batch:
qualify_job_listings-3e0aa3ec-a853-42fa-ad37-63aea7c24a02)
2026-10-07 22:19:35  [DEBUG]  1425: Response from _run_dispatch_loop:
{"total_processed": 2, "total_passed": 0, "total_failed": 0,
"total_errors": 2}
2026-10-07 22:19:35  [DEBUG]  1623: End dispatch loop after 1 run(s)
2026-10-07 22:19:35  [DEBUG]  1619: loop stop: max_runs reached
max_runs=1 run_count=1
2026-10-07 22:19:35  [DEBUG]  1591: Response from _run_task:
{"total_processed": 2, "total_passed": 0, "total_failed": 0,
"total_errors": 2}
2026-10-07 22:19:35  [DEBUG]  967: Response from _run_unified:
{"total_processed": 2, "total_passed": 0, "total_failed": 0,
"total_errors": 2}
2026-10-07 22:19:35  [DEBUG]  878: Response from
consult.run_consult_task: {"total_processed": 2, "total_passed": 0,
"total_failed": 0, "total_errors": 2}
2026-10-07 22:19:35  [DEBUG]  126: Response from qualify_job_listings:
{"success": false, "error": "Empty tokens: RUBRIC_VECTORS
(task=qualify_job_listings)", "passed": 0, "failed": 0, "total": 2,
"retried": 0}
2026-10-07 22:19:35  [DEBUG]  1689: empty_tokens route
task=qualify_job_listings ids=["1bb7f647-cb10-419a-b138-b6e47b4476fc",
"99f7de49-7f19-4bcb-9473-cd9ba341f3f7"]
dest=ERROR_QUALIFY_JOB_LISTINGS
2026-10-07 22:19:35  [DEBUG]  1663: Response from agent.do_task:
{"success": false, "error": "Empty tokens: RUBRIC_VECTORS
(task=qualify_job_listings)", "empty_tokens": ["RUBRIC_VECTORS"],
"empty_token_task": "qualify_job_listings", "api_response": null,
"parsed_response": null, "timesheet": {}, "source_artifact_ids": []}
2026-10-07 22:19:35  [ERROR]
qualify_job_listings_batch_qualify_job_listings-3e0aa3ec-a853-42fa-ad37-63aea7c24a02
| qualify_job_listings skipped — empty tokens RUBRIC_VECTORS
  This call is not going out
2026-10-07 22:19:35  [DEBUG]  1658: Calling agent.do_task:
[task_key=qualify_job_listings,
index=qualify_job_listings_batch_qualify_job_listings-3e0aa3ec-a853-42fa-ad37-63aea7c24a02,
n=2]
2026-10-07 22:19:35  [DEBUG]  1639:
batch_id=qualify_job_listings-3e0aa3ec-a853-42fa-ad37-63aea7c24a02
batch_states=["VALID_TITLE"] batch_chunk_index=None
astral_ids=["1bb7f647-cb10-419a-b138-b6e47b4476fc",
"99f7de49-7f19-4bcb-9473-cd9ba341f3f7"]
2026-10-07 22:19:35  [DEBUG]  1635: Beginning qualify_job_listings
loop on 2 items
2026-10-07 22:19:35  [DEBUG]  1972: total_listing_chars=1891
2026-10-07 22:19:35  [DEBUG]  1966: input job 2/2
99f7de49-7f19-4bcb-9473-cd9ba341f3f7 title='3 Locations Neuroscience
Specialist - Minneapolis N, MN Job SummaryOtsuka America
Pharmaceutical Inc. is a global healthcare company with the corporate
philosophy: “Otsuka-people creating new products for better health
worldwide.” Otsuka… Apply' listing_chars=1688 link=None
2026-10-07 22:19:35  [DEBUG]  1966: input job 1/2
1bb7f647-cb10-419a-b138-b6e47b4476fc title='Save Job Research Lab
Technician II Los Angeles, California' listing_chars=203 link=None
2026-10-07 22:19:35  [DEBUG]  1963: Beginning qualify_job_listings
loop on 2 items
2026-10-07 22:19:35  [DEBUG]   | summary passed=2 failed=0 total=2
2026-10-07 22:19:35  [DEBUG]   | raw_listing_chars=1688 patterns=33
permissive=False
2026-10-07 22:19:35  [DEBUG]  gazer.validate_title_batch index 2/2
99f7de49-7f19-4bcb-9473-cd9ba341f3f7 -> passed -> VALID_TITLE
2026-10-07 22:19:35  [DEBUG]   | raw_listing_chars=203 patterns=33
permissive=False
2026-10-07 22:19:35  [DEBUG]  gazer.validate_title_batch index 1/2
1bb7f647-cb10-419a-b138-b6e47b4476fc -> passed -> VALID_TITLE
2026-10-07 22:19:35  [DEBUG]  gazer.validate_title_batch index 1/1
qualify_job_listings-3e0aa3ec-a853-42fa-ad37-63aea7c24a02 -> batch
start 2 job(s) pattern_count=33
2026-10-07 22:19:35  [DEBUG]  1940: End meteorite NEW re-home loop after 0 items
2026-10-07 22:19:35  [DEBUG]  1935: Beginning meteorite NEW re-home
loop on 0 items
2026-10-07 22:19:35  [DEBUG]  124: Calling qualify_job_listings:
[batch_id=qualify_job_listings-3e0aa3ec-a853-42fa-ad37-63aea7c24a02,
n=2]
2026-10-07 22:19:35  [DEBUG]  870: Calling consult.run_consult_task:
[entity_type=job, state=NEW, n=2,
batch=qualify_job_listings-3e0aa3ec-a853-42fa-ad37-63aea7c24a02,
task_key=qualify_job_listings]
2026-10-07 22:19:35  [DEBUG]  790: End job claim loop after 2 items
2026-10-07 22:19:35  [DEBUG]  789: Beginning job claim loop on 2 items
2026-10-07 22:19:35  [DEBUG]  742: Response from get_new_job_batch: 2
entities batch=qualify_job_listings-3e0aa3ec-a853-42fa-ad37-63aea7c24a02
2026-10-07 22:19:35  [DEBUG]  728: Calling get_new_job_batch:
[state=NEW, limit=20, sort_by=updated_at, score_floor=None,
candidate_id=abrams,
batch_id=qualify_job_listings-3e0aa3ec-a853-42fa-ad37-63aea7c24a02,
claim_cap=2, states=["NEW", "NEW_RETRY"]]
2026-10-07 22:19:35  [DEBUG]  959: Calling _run_unified:
[task_key=qualify_job_listings, batch_size=20, entity_type=job,
trigger_state=NEW]
2026-10-07 22:19:35  [DEBUG]  1589: Calling _run_task:
[task_key=qualify_job_listings, available=2]
2026-10-07 22:19:35  [DEBUG]  1540: Beginning dispatch loop on 2 items
2026-10-07 22:19:35  [DEBUG]  1420: Calling _run_dispatch_loop:
[task_key=qualify_job_listings, available=2,
entity_batch_id=qualify_job_listings-3e0aa3ec-a853-42fa-ad37-63aea7c24a02]
2026-10-07 22:19:35  [INFO]  abrams | dispatch job starting
qualify_job_listings — 2 available (batch:
qualify_job_listings-3e0aa3ec-a853-42fa-ad37-63aea7c24a02)
```

### Comments

#### chuckles — 2026-10-09T02:50:09.283Z
@susan reassigned back with no new note, and nothing has changed: [AST-2019](https://linear.app/astralcareermatch/issue/AST-2019)'s fix [AST-2092](https://linear.app/astralcareermatch/issue/AST-2092) is still at User Testing, and it covers this exact gate. I still haven't created anything for AST-2020. Reply with one word and reassign me:

- **dup** — I'll mark AST-2020 Duplicate of AST-2019 and stop.
- **proceed** — I'll dispatch a separate fix anyway. It'll have to be planned against AST-2092's change, since both touch the same gate.

#### chuckles — 2026-10-09T02:30:08.883Z
@susan bug-fix stopped before dispatch — this looks like a duplicate of [AST-2019](https://linear.app/astralcareermatch/issue/AST-2019): same candidate (Abrams), same task (`qualify_job_listings`), same `Empty tokens: RUBRIC_VECTORS`, filed ~30 min earlier.

- AST-2019 is already In Progress on `ftr/AST-2019-rubric-empty-render-gate`. Its fix child [AST-2092](https://linear.app/astralcareermatch/issue/AST-2092) is at **User Testing** — `5ff29d792` scores rubric tokens by default in `empty_render_for_prompts`, Radia PROCEED. The test-gap child [AST-2094](https://linear.app/astralcareermatch/issue/AST-2094) is at Plan Approved.
- AST-2020's approved approach was the call-site version of the same change (`_evaluate_dispatch_empty_render` passing a `rubric` entity context). If both landed, they'd change the same gate twice.
- Nothing was created for AST-2020: no `ftr`, no child, no registry ref.

Suggest marking AST-2020 **Duplicate** of AST-2019. If you want something different here, reassign me with a note.

---

_Implementation detail may live in git history on `origin/dev`._
