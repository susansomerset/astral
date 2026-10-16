# AST-2019 — [✅/Abrams] qualify_job_listings COMPLETED: 10 error(s) / 10 processed | qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e

<!-- linear-archive: AST-2019 archived 2026-10-16 -->

## Linear archive (AST-2019)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2019/abrams-qualify-job-listings-completed-10-errors-10-processed-qualify  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

Abrams' `qualify_job_listings` dispatch claimed 10 `NEW` jobs, passed all 10 through the inline title gate (`VALID_TITLE`), then `agent.do_task` refused to send the prompt because `{$RUBRIC_VECTORS}` resolved empty (`Empty tokens: RUBRIC_VECTORS`). All 10 jobs were routed to `ERROR_QUALIFY_JOB_LISTINGS` (batch `qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e`: 0 pass / 0 fail / 10 error).

Two things are wrong here:

1. **Data:** Abrams has no current `joblist_rubric` rows in `rubric_vector` (owner `qualify_job_listings`), so the token has nothing to render. (Inferred from the resolver path: the owner mapping exists and the admin token view carries `_astral_candidate_id`, so the remaining way to get `""` is "no current rows". I haven't checked this against the DB.)
2. **Gate:** Scheduled Actions should have flagged this row Invalid and blocked AUTO/Run *before* anything was claimed. It didn't, because `empty_render_for_prompts` (`src/utils/config.py`) only scores `source: candidate` tokens by default. `RUBRIC_VECTORS` (and the pinned `GET_RUBRIC` / `DO_RUBRIC` / `LIKE_RUBRIC` / `JD_RUBRIC`) are `source: rubric`, so they are skipped unless passed through `entity_contexts`. `_evaluate_dispatch_empty_render` always passes `entity_contexts=None`. This exclusion was deliberate in AST-1779 ("Do not score `pronoun`, `rubric`, `config`…"), but rubric rows are keyed per candidate (`candidate_id` + owner task), so they belong with the candidate-scoped tokens, not with the job tokens.

## To-be

A candidate whose rubric for a task is empty shows that dispatch row as **Invalid** in Scheduled Actions, with the rubric token named in the tooltip (`empty_tokens`). AUTO is forced off and Run/AUTO-on are refused (400), the same as a blank candidate token today. No jobs get claimed and dumped into `ERROR_*`. Separately, once Abrams' joblist rubric is crafted, the row validates and `qualify_job_listings` runs normally.

## Proposed steps

1. In `empty_render_for_prompts`, score `source: rubric` tokens by default, the same as `source: candidate`. They resolve from the candidate view's `_astral_candidate_id` and the task's rubric owner (or the token's pinned owner), with no entity context needed. Keep `chain` never scored and `job` scored only via the `entity_contexts` seam.
2. No change needed in `api_admin.py`: list enrich, the PUT AUTO-on gate and the POST run gate all route through `_evaluate_dispatch_empty_render` → `empty_render_for_prompts`, so they pick this up automatically.
3. Betty revises the pinned AST-1779 test `test_rubric_scored_only_via_entity_contexts`, since its contract flips, and adds a repro: a candidate with no current `rubric_vector` rows for `qualify_job_listings` gives `empty_render: True`, `empty_tokens: ["RUBRIC_VECTORS"]`.
4. Operator side, not code: craft or approve Abrams' joblist rubric (`craft_joblist_rubric`), then reset the 10 `ERROR_QUALIFY_JOB_LISTINGS` jobs back to `NEW` so they rerun.

## Component scope

* `src/utils/config.py` — modified: `empty_render_for_prompts` is where rubric-sourced tokens are skipped by default. This is the whole product fix.
* `tests/component/utils/test_config.py` — modified (Betty-owned): the AST-1779 rubric-seam test asserts the old behaviour and must flip. Needs a new rubric-empty repro.

## Technical scope

* `src/utils/config.py` — modified function `empty_render_for_prompts`: widen the default scoring rule from "candidate only" to "candidate and rubric". Rubric tokens are candidate-scoped data (one `rubric_vector` set per candidate per owner task), and the existing `resolve_tokens` rubric branch already resolves them from the candidate view. No new resolver, no new `TOKEN_SOURCES` entries, no schema change.
* `tests/component/utils/test_config.py` — modified test plus one new test in `TestAst1779EmptyRenderForPrompts`. The pinned seam-only contract becomes default scoring, and the empty-rubric case is pinned as a repro.

## Ancestor candidates

- [ ] AST-1779 — Empty-token predicate helper (`docs/features/dispatcher/ast-1779-empty-token-predicate-helper.md`). This is where `empty_render_for_prompts` was written to deliberately skip `source: rubric`.
- [ ] AST-1780 — List enrich / AUTO-Run gates, force AUTO off (`docs/features/dispatcher/ast-1780-list-enrich-auto-run-gates-force-auto-off.md`). This is the Scheduled Actions gate that calls the helper with `entity_contexts=None`.
- [ ] AST-723 — Rubric vector read/write cutover (`docs/features/auditor/ast-723-rubric-vector-read-write-cutover.md`). This introduced `RUBRIC_VECTORS` as `source: rubric`, resolved from `rubric_vector`.
- [ ] AST-1405 — Named rubric prompt tokens (`docs/features/foundation/ast-1405-named-rubric-prompt-tokens.md`). This added the pinned rubric tokens, which have the same gap.

## Original report

```
2026-10-07 21:48:49  [DEBUG]  67: No pending gen-* timesheet rows
(trigger batch qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e);
skipping platform reconcile
2026-10-07 21:48:49  [INFO]  abrams | dispatch job task completed:
qualify_job_listings pass:0 fail:0 error:10 (batch:
qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e)
2026-10-07 21:48:49  [DEBUG]  1425: Response from _run_dispatch_loop:
{"total_processed": 10, "total_passed": 0, "total_failed": 0,
"total_errors": 10}
2026-10-07 21:48:49  [DEBUG]  1623: End dispatch loop after 1 run(s)
2026-10-07 21:48:49  [DEBUG]  1619: loop stop: max_runs reached
max_runs=1 run_count=1
2026-10-07 21:48:49  [DEBUG]  1591: Response from _run_task:
{"total_processed": 10, "total_passed": 0, "total_failed": 0,
"total_errors": 10}
2026-10-07 21:48:49  [DEBUG]  967: Response from _run_unified:
{"total_processed": 10, "total_passed": 0, "total_failed": 0,
"total_errors": 10}
2026-10-07 21:48:49  [DEBUG]  878: Response from
consult.run_consult_task: {"total_processed": 10, "total_passed": 0,
"total_failed": 0, "total_errors": 10}
2026-10-07 21:48:49  [DEBUG]  126: Response from qualify_job_listings:
{"success": false, "error": "Empty tokens: RUBRIC_VECTORS
(task=qualify_job_listings)", "passed": 0, "failed": 0, "total": 10,
"retried": 0}
2026-10-07 21:48:49  [DEBUG]  1689: empty_tokens route
task=qualify_job_listings ids=["c6300d99-4458-4a81-b1c6-ed068c87f759",
"93dfe63d-ac09-46d4-a308-d0718fb9a368",
"b01b8065-9ddc-4411-8252-a73c1ee4c1bb",
"efedb958-6983-4377-baf0-f0cc40e8c468",
"15cd0a50-bda4-468f-867b-2fd722a142fc",
"21e1ede4-bfe7-493c-b4d2-bb8b66699385",
"dedabec6-62b5-44fc-9f3f-d8e345ac0104",
"b84dc902-0524-4489-b7e4-c2404512fea1",
"35414fd2-4dc6-4b7d-b9cd-08a02eb8d56c",
"cc9a529e-dd25-43af-851f-e6b2df7bdcb5"]
dest=ERROR_QUALIFY_JOB_LISTINGS
2026-10-07 21:48:49  [DEBUG]  1663: Response from agent.do_task:
{"success": false, "error": "Empty tokens: RUBRIC_VECTORS
(task=qualify_job_listings)", "empty_tokens": ["RUBRIC_VECTORS"],
"empty_token_task": "qualify_job_listings", "api_response": null,
"parsed_response": null, "timesheet": {}, "source_artifact_ids": []}
2026-10-07 21:48:49  [ERROR]
qualify_job_listings_batch_qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e
| qualify_job_listings skipped — empty tokens RUBRIC_VECTORS
  This call is not going out
2026-10-07 21:48:49  [DEBUG]  1658: Calling agent.do_task:
[task_key=qualify_job_listings,
index=qualify_job_listings_batch_qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e,
n=10]
2026-10-07 21:48:49  [DEBUG]  1639:
batch_id=qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e
batch_states=["VALID_TITLE"] batch_chunk_index=None
astral_ids=["c6300d99-4458-4a81-b1c6-ed068c87f759",
"93dfe63d-ac09-46d4-a308-d0718fb9a368",
"b01b8065-9ddc-4411-8252-a73c1ee4c1bb",
"efedb958-6983-4377-baf0-f0cc40e8c468",
"15cd0a50-bda4-468f-867b-2fd722a142fc",
"21e1ede4-bfe7-493c-b4d2-bb8b66699385",
"dedabec6-62b5-44fc-9f3f-d8e345ac0104",
"b84dc902-0524-4489-b7e4-c2404512fea1",
"35414fd2-4dc6-4b7d-b9cd-08a02eb8d56c",
"cc9a529e-dd25-43af-851f-e6b2df7bdcb5"]
2026-10-07 21:48:49  [DEBUG]  1635: Beginning qualify_job_listings
loop on 10 items
2026-10-07 21:48:49  [DEBUG]  1972: total_listing_chars=23426
2026-10-07 21:48:49  [DEBUG]  1966: input job 10/10
cc9a529e-dd25-43af-851f-e6b2df7bdcb5 title='Postdoctoral Research
Associate in NeuroOncology, Queen Mary Univeristy of London, United
Kingdom 22 Oct 2026' listing_chars=456 link=None
2026-10-07 21:48:49  [DEBUG]  1966: input job 9/10
35414fd2-4dc6-4b7d-b9cd-08a02eb8d56c title='Postdoctoral Researcher:
AI Safety in Mental Health Closing Date: 04-NOV-2026 | £39,424 -
£47,779 per annum The University of Oxford is a stimulating work
environment, which enjoys an international reputation as a world-class
centre of excellence. Our research plays a key role in tackling many
global challenges, from reducing our carbon emissions to developing
vaccines during a pandemic. The Department of Psychiatry is based on
the Warneford Hospital site in Oxford – a friendly, welcoming place of
work with an international reputation for excellence. The Department
has a substantial research programme, with major funding from Medical
Research Council (MRC), Wellcome Trust and National Institute for
Health Research (NIHR) and provides highly rated medical training in
psychiatry.\xa0 The Head of Department is Professor Belinda Lennox. We
are looking for a postdoctoral researcher to work on delivering state
of the art AI safety work for the ARIADNE consortium, a Wellcome
Trust-funded project<2488 chars omitted>pproaches, and validation of
automated evaluations against human ratings. Experience with AI safety
evaluation methods, such as red-teaming, guardrail architectures or
model-based monitoring and of fine-tuning large language models with
deep learning frameworks (e.g. PyTorch) or applying alignment
techniques (e.g. reinforcement learning from human feedback, DPO)
would be desirable. Diversity Committed to equality and valuing
diversity, our\xa0active Psychiatry People and Culture teams and
initiatives including our values and behaviours framework , work to
make the Department of Psychiatry as supportive, welcoming and
inclusive as possible. Application Process You will be required to
upload a covering letter/supporting statement, CV and the details of
two referees as part of your online application. Please see the
University pages on the application process at
https://www.jobs.ox.ac.uk/application-process The closing date for
applications is 12:00 midday on 4 November 2026 More information'
listing_chars=5727 link=None
2026-10-07 21:48:49  [DEBUG]  1966: input job 8/10
b84dc902-0524-4489-b7e4-c2404512fea1 title='Part-time Research
Assistant: RELMED and RePram Studies Closing Date: 20-OCT-2026 |
£35,681-£39,424 per annum pro rata The University of Oxford is a
stimulating work environment, which enjoys an international reputation
as a world-class centre of excellence. Our research plays a key role
in tackling many global challenges, from reducing our carbon emissions
to developing vaccines during a pandemic. The Department of Psychiatry
is based on the Warneford Hospital site in Oxford – a friendly,
welcoming place of work with an international reputation for
excellence. The Department has a substantial research programme, with
major funding from Medical Research Council (MRC), Wellcome Trust and
National Institute for Health Research (NIHR) and provides highly
rated medical training in psychiatry.\xa0 The Head of Department is
Professor Belinda Lennox. We are looking for a Part-time Research
Assistant to support two related research studies, RELMED and RePRAM
in the Department of Psychiatry. What <1849 chars omitted>athering,
managing and quality-checking scientific data from a range of sources
along with experience of using EEG in a research environment and
performing quality checks of EEG data. Excellent communication skills,
including the ability to work effectively with research participants,
colleagues and collaborators, and to maintain accurate records and
confidentiality are essential. Diversity Committed to equality and
valuing diversity, ouractive Psychiatry People and Culture teams
\xa0and initiatives including our values and behaviours framework
,\xa0 work to make the Department of Psychiatry as supportive,
welcoming and inclusive as possible. Application Process You will be
required to upload a covering letter/supporting statement, CV and the
details of two referees as part of your online application. Please see
the University pages on the application process at
https://www.jobs.ox.ac.uk/application-process The closing date for
applications is 12:00 midday on 20 October 2026 More information'
listing_chars=5166 link=None
2026-10-07 21:48:49  [DEBUG]  1966: input job 7/10
dedabec6-62b5-44fc-9f3f-d8e345ac0104 title='Postdoctoral Researcher
(m/f/d) - Neuropeptide Research | Neurobiology of Positive Emotions
Vollzeit Befristet Forschung und Wissenschaft' listing_chars=518
link=None
2026-10-07 21:48:49  [DEBUG]  1966: input job 6/10
21e1ede4-bfe7-493c-b4d2-bb8b66699385 title='Research Technician'
listing_chars=352 link=None
2026-10-07 21:48:49  [DEBUG]  1966: input job 5/10
15cd0a50-bda4-468f-867b-2fd722a142fc title='CDL Research Assistant
537980 Blacksburg, Virginia Virginia Tech Transportation Instit
Research / Scientific Transportation Hourly Wage/Part-Time Vice
President for Research Read more' listing_chars=2769 link=None
2026-10-07 21:48:49  [DEBUG]  1966: input job 4/10
efedb958-6983-4377-baf0-f0cc40e8c468 title='Research Associate, Data
Science 537973 Arlington, Virginia VTNSI Data Analytics / Security
Information Systems / Technology Research / Scientific Research
Faculty Vice President for Research Read more' listing_chars=2993
link=None
2026-10-07 21:48:49  [DEBUG]  1966: input job 3/10
b01b8065-9ddc-4411-8252-a73c1ee4c1bb title='Research Assistant 538068
Roanoke, Virginia Fralin Biomedical Res. Institute Research /
Scientific Staff Vice President for Research Read more'
listing_chars=2527 link=None
2026-10-07 21:48:49  [DEBUG]  1966: input job 2/10
93dfe63d-ac09-46d4-a308-d0718fb9a368 title='Research Specialist |
Closes July 17, 2026, at 11:59pm' listing_chars=235 link=None
2026-10-07 21:48:49  [DEBUG]  1966: input job 1/10
c6300d99-4458-4a81-b1c6-ed068c87f759 title='Staff Research Assistant -
HPRC 494174 Oklahoma City, Oklahoma Technology/Research College of
Medicine S07 OU Health Stephenson Cancer Center is Oklahoma’s only
National Cancer Institute (NCI)-Designated Cancer Center, and one of
only 74 NCI-Designated Cancer Centers in the United States. This
highly competitive accreditation ensures that our patients receive the
highest standard of care and have access to the most advanced cancer
treatment options. At the Stephenson Cancer Center, we have an
exciting new job opportunity that could be right for you! Apply now'
listing_chars=2683 link=None
2026-10-07 21:48:49  [DEBUG]  1963: Beginning qualify_job_listings
loop on 10 items
2026-10-07 21:48:49  [DEBUG]   | summary passed=10 failed=0 total=10
2026-10-07 21:48:49  [DEBUG]   | raw_listing_chars=456 patterns=33
permissive=False
2026-10-07 21:48:49  [DEBUG]  gazer.validate_title_batch index 10/10
cc9a529e-dd25-43af-851f-e6b2df7bdcb5 -> passed -> VALID_TITLE
2026-10-07 21:48:49  [DEBUG]   | raw_listing_chars=5727 patterns=33
permissive=False
2026-10-07 21:48:49  [DEBUG]  gazer.validate_title_batch index 9/10
35414fd2-4dc6-4b7d-b9cd-08a02eb8d56c -> passed -> VALID_TITLE
2026-10-07 21:48:49  [DEBUG]   | raw_listing_chars=5166 patterns=33
permissive=False
2026-10-07 21:48:49  [DEBUG]  gazer.validate_title_batch index 8/10
b84dc902-0524-4489-b7e4-c2404512fea1 -> passed -> VALID_TITLE
2026-10-07 21:48:49  [DEBUG]   | raw_listing_chars=518 patterns=33
permissive=False
2026-10-07 21:48:49  [DEBUG]  gazer.validate_title_batch index 7/10
dedabec6-62b5-44fc-9f3f-d8e345ac0104 -> passed -> VALID_TITLE
2026-10-07 21:48:49  [DEBUG]   | raw_listing_chars=352 patterns=33
permissive=False
2026-10-07 21:48:49  [DEBUG]  gazer.validate_title_batch index 6/10
21e1ede4-bfe7-493c-b4d2-bb8b66699385 -> passed -> VALID_TITLE
2026-10-07 21:48:49  [DEBUG]   | raw_listing_chars=2769 patterns=33
permissive=False
2026-10-07 21:48:49  [DEBUG]  gazer.validate_title_batch index 5/10
15cd0a50-bda4-468f-867b-2fd722a142fc -> passed -> VALID_TITLE
2026-10-07 21:48:49  [DEBUG]   | raw_listing_chars=2993 patterns=33
permissive=False
2026-10-07 21:48:49  [DEBUG]  gazer.validate_title_batch index 4/10
efedb958-6983-4377-baf0-f0cc40e8c468 -> passed -> VALID_TITLE
2026-10-07 21:48:49  [DEBUG]   | raw_listing_chars=2527 patterns=33
permissive=False
2026-10-07 21:48:49  [DEBUG]  gazer.validate_title_batch index 3/10
b01b8065-9ddc-4411-8252-a73c1ee4c1bb -> passed -> VALID_TITLE
2026-10-07 21:48:49  [DEBUG]   | raw_listing_chars=235 patterns=33
permissive=False
2026-10-07 21:48:49  [DEBUG]  gazer.validate_title_batch index 2/10
93dfe63d-ac09-46d4-a308-d0718fb9a368 -> passed -> VALID_TITLE
2026-10-07 21:48:49  [DEBUG]   | raw_listing_chars=2683 patterns=33
permissive=False
2026-10-07 21:48:49  [DEBUG]  gazer.validate_title_batch index 1/10
c6300d99-4458-4a81-b1c6-ed068c87f759 -> passed -> VALID_TITLE
2026-10-07 21:48:49  [DEBUG]  gazer.validate_title_batch index 1/1
qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e -> batch
start 10 job(s) pattern_count=33
2026-10-07 21:48:49  [DEBUG]  1940: End meteorite NEW re-home loop after 0 items
2026-10-07 21:48:49  [DEBUG]  1935: Beginning meteorite NEW re-home
loop on 0 items
2026-10-07 21:48:49  [DEBUG]  124: Calling qualify_job_listings:
[batch_id=qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e,
n=10]
2026-10-07 21:48:49  [DEBUG]  870: Calling consult.run_consult_task:
[entity_type=job, state=NEW, n=10,
batch=qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e,
task_key=qualify_job_listings]
2026-10-07 21:48:49  [DEBUG]  790: End job claim loop after 10 items
2026-10-07 21:48:49  [DEBUG]  789: Beginning job claim loop on 10 items
2026-10-07 21:48:49  [DEBUG]  742: Response from get_new_job_batch: 10
entities batch=qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e
2026-10-07 21:48:49  [DEBUG]  728: Calling get_new_job_batch:
[state=NEW, limit=20, sort_by=updated_at, score_floor=None,
candidate_id=abrams,
batch_id=qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e,
claim_cap=10, states=["NEW", "NEW_RETRY"]]
2026-10-07 21:48:49  [DEBUG]  959: Calling _run_unified:
[task_key=qualify_job_listings, batch_size=20, entity_type=job,
trigger_state=NEW]
2026-10-07 21:48:49  [DEBUG]  1589: Calling _run_task:
[task_key=qualify_job_listings, available=10]
2026-10-07 21:48:49  [DEBUG]  1540: Beginning dispatch loop on 10 items
2026-10-07 21:48:49  [DEBUG]  1420: Calling _run_dispatch_loop:
[task_key=qualify_job_listings, available=10,
entity_batch_id=qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e]
2026-10-07 21:48:49  [INFO]  abrams | dispatch job starting
qualify_job_listings — 10 available (batch:
qualify_job_listings-9f9fcf12-c163-4e88-b88f-7037ae4bc21e)
```

### Comments

#### chuckles — 2026-10-09T02:30:17.138Z
AST-2094 gated on [AST-2097](https://linear.app/astralcareermatch/issue/AST-2097) — Susan picks who owns "empty rubric → Invalid" (AST-2092 here vs [AST-2091](https://linear.app/astralcareermatch/issue/AST-2091)) and how Betty publishes the AST-2094 tests. Fix [AST-2092](https://linear.app/astralcareermatch/issue/AST-2092) is User Testing and merged on ftr; test gap [AST-2094](https://linear.app/astralcareermatch/issue/AST-2094) waits on the gate.

---

_Implementation detail may live in git history on `origin/dev`._
