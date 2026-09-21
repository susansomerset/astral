# AST-1316 — Can't find agent data for proposed application responses

<!-- linear-archive: AST-1316 archived 2026-08-31 -->

## Linear archive (AST-1316)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1316/cant-find-agent-data-for-proposed-application-responses  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

This should not cause a stacktrace.  We should not be requiring elements in artifacts.

```
et_entity_agent_story: list_entity_latest_agent_refs failed entity_type=job entity_id=8178a846-d026-4ca3-be3f-1f5a0d3113a5: agent_data ref target missing: 'propose_application_responses-fafe75d0-e41d-48d7-95d6-d489483832dc-task-bb404bc0bb2e68f4'
Traceback (most recent call last):
  File "/Users/susan/chuckles/astral/src/core/roster.py", line 3542, in get_entity_agent_story
    entries = list_entity_latest_agent_refs(entity_type, entity_id)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 5982, in list_entity_latest_agent_refs
    return _run_with_retry(_with_conn)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 265, in _run_with_retry
    return fn()
           ^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 5967, in _with_conn
    blocks = get_agent_data_by_batch(batch_id)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 5912, in get_agent_data_by_batch
    return _run_with_retry(_with_conn)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 265, in _run_with_retry
    return fn()
           ^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 5907, in _with_conn
    d["block_data"] = _resolve_agent_data_block_data(conn, d)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 5876, in _resolve_agent_data_block_data
    raise ValueError(f"agent_data ref target missing: {current_id!r}")
ValueError: agent_data ref target missing: 'propose_application_responses-fafe75d0-e41d-48d7-95d6-d489483832dc-task-bb404bc0bb2e68f4'
```

This was in the agent_data table in local

```
[
  {
    "agent_data_id": "propose_application_responses-fafe75d0-e41d-48d7-95d6-d489483832dc-response-dd843941c157d7b9",
    "anthropic_req_id": null,
    "batch_id": "propose_application_responses-fafe75d0-e41d-48d7-95d6-d489483832dc",
    "block_data": "{\n  \"agent_performance\": \"success\",\n  \"agent_payload\": {\n    \"application_questions_found\": false,\n    \"questions\": [],\n    \"note\": \"The provided job description text does not contain any explicit application questions. The text cuts off midway through an equal-opportunity statement, so if the original listing included a 'How to Apply' section with instructions or questions, they are missing. If you can retrieve the full posting or any questions from the application form, I can draft responses immediately.\"\n  }\n}",
    "block_type": "RESPONSE",
    "created_at": "2026-07-31 02:12:30",
    "entity_id": "59157641-dc14-479e-a8fe-046aa049c7f4",
    "entity_type": "job",
    "ref_agent_data_id": null,
    "task_key": "propose_application_responses",
    "token_size": 129
  }
]
```

```
[
  {
    "agent_id": "",
    "cache_prompt": "",
    "cache_prompt_b": "",
    "cache_prompt_c": "",
    "cache_prompt_d": "",
    "current": 1,
    "nocache_prompt": "",
    "run_next": "",
    "system_prompt": "",
    "task_group_name": "(unassigned)",
    "task_group_order": "ZZZ",
    "task_key": "propose_application_responses",
    "task_key_uuid": "67754b5c-1063-45a5-a56a-7c86d6c9f091",
    "task_name": "propose_application_responses",
    "task_seq": 999,
    "updated_at": "2026-08-12 04:36:44",
    "user_prompt": ""
  }
]
```

### Comments

#### chuckles — 2026-08-12T23:40:15.874Z
## bug-find — round 5 (Susan picked AST-1274)

**Ancestor locked:** AST-1274 (`docs/features/interface/ast-1274-restore-recommended-job-detail-open.md`).

**Carry into plan-fix when you Todo this:**
- As-is/to-be from Description: no stacktrace; do not require elements in artifacts.
- Move `get_entity_agent_story` from `roster.py` → `agent.py` (roster = company data).
- Soft-fail / missing TASK `agent_data` for `propose_application_responses` on the story path.

Not seeding git, not filing children — move this ticket to **Todo** (assignee Chuckles) when you want bug-fix to start.

#### susan — 2026-08-12T23:39:27.715Z
1274 please.

#### chuckles — 2026-08-12T23:38:38.095Z
## bug-find — round 4 (Susan: move entity story → agent.py)

**Your brief:** Move entity story out of `roster.py` into `agent.py`. Roster is for company data.

**As-is:** `get_entity_agent_story` lives in `core/roster.py`; missing `propose_application_responses` TASK `agent_data` still hits `list_entity_latest_agent_refs` → logged stack via AST-1274’s `logger.exception` soft-fail; job detail also hydrates artifacts (AST-1100).

**To-be:** No stacktrace noise / don’t require missing artifact or agent_data pieces; **and** entity-story ownership sits in `agent.py`, not roster.

**Grep note (4 tries):** No feature doc already plans “move `get_entity_agent_story` → `agent.py`”. Closest ancestors still own the current placement + soft-fail. Your move is new scope on whichever ancestor you pick (plan-fix will carry it).

### Candidates (re-ranked to this round)

1. **AST-1274** (`docs/features/interface/ast-1274-restore-recommended-job-detail-open.md`) — owns soft-fail on this exact stack; edits `get_entity_agent_story` in roster today — natural seed if the bug is “story open must not scream,” with your move as added stage.
2. **AST-984** (`docs/features/foundation/ast-984-retire-entity-agent-responses-columns.md`) — put `get_entity_agent_story` on `list_entity_latest_agent_refs` **in roster.py**; best seed if the main product call is “wrong component owns story.”
3. **AST-726** (`docs/features/roster/ast-726-latest-only-rubric-writes-and-modal-dedup.md`) — earlier home of story/dedupe in roster.
4. **AST-727** (`docs/features/roster/ast-727-backfill-latest-only-rubric-entity-data.md`) — roster backfill sharing story helpers.
5. **AST-1100** (`docs/features/artifacts/ast-1100-resolve-artifact-agent-data-id.md`) — still the “don’t require elements in artifacts” display/hydrate half (parallel concern).

Pick an ancestor (or Todo with no ancestor). Move-to-`agent.py` is recorded as your direction either way.

#### susan — 2026-08-12T23:37:24.367Z
Let's move the entity story to agent.py.  Roster is specifically for company data.

#### chuckles — 2026-08-12T17:28:19.769Z
## bug-find — round 3 (Susan: justify get_entity_agent_story)

### What `get_entity_agent_story` is

- **Component:** `core` — `src/core/roster.py`
- **Job:** Build the **agent story** payload for an entity (job / company / candidate): latest hop per `task_key` from `list_entity_latest_agent_refs`, then expand each hop’s prompt/RESPONSE block ids into readable block content for the UI (Job Analysis Report tabs, scored grades, etc.). Docstring cites AST-984.
- **Who calls it, when:**
  - `src/ui/api/api_jobs.py` `detail` (`GET /api/jobs/<id>`) — **only on job open**, after artifact hydrate (AST-1100). Soft-wrapped again (AST-1274).
  - `src/ui/api/api_companies.py` `detail` (`GET /api/companies/<short_name>`) — company open. **No** soft-wrap today.
  - Not used on list endpoints.
- **Your log line** (`get_entity_agent_story: list_entity_latest_agent_refs failed …` + traceback) is already the **AST-1274 soft-fail catch** (`logger.exception` then `return []`) — detail should still 200; the stack is log noise from `exception()`, not an uncaught 500. So “should not cause a stacktrace” still lands on this path as a residual of 1274 (quieter log / don’t treat missing TASK/artifact pieces as hard errors upstream).

### Recommendation

**AST-1274** remains the best ancestor to revive for context: it owns this function’s soft-fail + job-detail guard on the exact stack in the Description. AST-1100 stays nearby if the “don’t require elements in artifacts” half is really the hydrate/pin read path rather than story logging.

### Candidates (unchanged set)

1. **AST-1274** — recommended (story soft-fail / no fatal open)
2. **AST-1100** — artifact pin resolve for JAR display
3. **AST-1099** — pin write for `proposed_answers`
4. **AST-1091** — parent artifact-save epic
5. **AST-984** — story/latest-refs contract that introduced this function

Pick / reject / ask more, or Todo to release bug-fix.

#### susan — 2026-08-12T17:27:01.204Z
I honestly don't know which one would be the best choice.  I don't know what get_entity_agent_story does, so maybe 1274 is the right one to bring up.  I want a justification for that function, which component it is in, and which components use it and when.

#### chuckles — 2026-08-12T17:22:07.087Z
## bug-find — round 2 (Description update)

Susan brief (ticket Description): this must not stacktrace; we should not be requiring elements in artifacts.

**As-is (revised):** Opening/loading a job’s agent story blows up with a full traceback when a `propose_application_responses` TASK `agent_data` id is missing — the path treats that hop/artifact graph as required instead of optional.

**To-be (revised):** Missing artifact / agent_data pieces for proposed application responses do not raise; story/detail continues without requiring those elements.

### Candidates (same set, re-ranked to her brief)

1. **AST-1274** (`docs/features/interface/ast-1274-restore-recommended-job-detail-open.md`) — soft-fail `get_entity_agent_story` / detail on missing-ref `ValueError` so no stacktrace / 500 (matches “should not cause a stacktrace”).
2. **AST-1100** (`docs/features/artifacts/ast-1100-resolve-artifact-agent-data-id.md`) — JAR/UI resolve of artifact pin ids including proposed answers; closest to “do not require elements in artifacts” on the read/display side.
3. **AST-1099** (`docs/features/artifacts/ast-1099-pin-agent-data-id.md`) — pins `propose_application_responses` → `artifacts.proposed_answers`; write-side of the artifact slot contract.
4. **AST-1091** (`docs/features/artifacts/ast-1091-job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved-in-job-data.md`) — parent epic for saving suggested responses into job artifacts.
5. **AST-984** (`docs/features/foundation/ast-984-retire-entity-agent-responses-columns.md`) — `list_entity_latest_agent_refs` + prompt-block attach that surfaces missing TASK ids into story load.

No new greps this round — ask refined, not a full reject of the prior list. Pick one / ask about one / reject all and reassign Chuckles, or move to Todo to release bug-fix.

#### chuckles — 2026-08-12T13:19:09.223Z
## bug-find — ancestor candidates

**As-is:** `get_entity_agent_story` → `list_entity_latest_agent_refs` → `get_agent_data_by_batch` raises `ValueError: agent_data ref target missing` for a `propose_application_responses-…-task-…` id, while the matching RESPONSE row still exists in `agent_data`.

**To-be:** Job agent-story / detail load survives a missing TASK block for that hop (skip dangling prompt-block refs and/or soft-fail the story path) so the RESPONSE body stays usable instead of blowing the whole lookup.

### Candidates (ranked)

1. **AST-1274** (`docs/features/interface/ast-1274-restore-recommended-job-detail-open.md`) — exact stack (`get_entity_agent_story` / `list_entity_latest_agent_refs` / `_resolve_agent_data_block_data` missing-ref `ValueError`); primary fetch resolve + secondary soft-fail on story/detail.
2. **AST-984** (`docs/features/foundation/ast-984-retire-entity-agent-responses-columns.md`) — introduced `list_entity_latest_agent_refs` + `get_entity_agent_story` contract that attaches batch prompt blocks (including TASK ids) to RESPONSE latest-refs.
3. **AST-1099** (`docs/features/artifacts/ast-1099-pin-agent-data-id.md`) — pins `propose_application_responses` RESPONSE id into `job_data.artifacts.proposed_answers` (same hop; pin/save path, not story resolve).
4. **AST-1091** (`docs/features/artifacts/ast-1091-job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved-in-job-data.md`) — parent artifact save epic for suggested responses / `proposed_answers`.
5. **AST-1100** (`docs/features/artifacts/ast-1100-resolve-artifact-agent-data-id.md`) — JAR/UI resolve of artifact pin ids (including proposed answers) for display.

Pick a candidate (or reject all / ask about one) and move to Todo when ready for bug-fix — or reassign Chuckles at Discussion to continue the hunt.

---

_Implementation detail may live in git history on `origin/dev`._
