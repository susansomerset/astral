# AST-2012 — [✅/Somerset] meteorite_grade_get COMPLETED: 23 error(s) / 52 processed | meteorite_grade_get-a4ec9af6-55e0-4bb6-92a9-2c4754009971

<!-- linear-archive: AST-2012 archived 2026-10-16 -->

## Linear archive (AST-2012)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2012/somerset-meteorite-grade-get-completed-23-errors-52-processed  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Is it possible that we are hard-coding a batch mode processing style for meteorite_grade_get, if we are running it in non-batch mode and every one comes back with 000?  I think the real task is to send a real index on EACH call (so, one item index "024", for example).

Check for the batch handling issue and update the code to send unique indexes for each entity in the batch so that even as asynch calls return, we can affirmatively map the response with its entity.

## As-is

Somerset `meteorite_grade_get` batch `meteorite_grade_get-a4ec9af6…` claimed 27 jobs and finished `pass:4 fail:0 error:23`. Each LLM call (about 20 jobs, `stop=end_turn`) yielded exactly **one** `job consult completed`; every other claimed id was logged `omitted from response`, sent to `METEORITE_PASSED_DO_RETRY`, omitted again on the retry run, and landed in `METEORITE_FAILED_TECHNICAL_GET`.

Why: the alias Do/Get path (`_consult_scored_dispatch_batch_encoded` in `src/core/consult.py`) labels rows by **chunk-local position**. `_prep_live_content` stamps `[index=NNN]` from `len(eligible)`, `assemble` prefixes `NNN:` again from `range(len(rows))`, and every parallel chunk restarts at `000`. The `grade_get` prompt in `data/admin/agent_task.json` also tells the model "zero-based row index (e.g. `000:`)". `_decode_payload` in `src/core/agent.py` then maps each reply line purely by `batch_entities[pos]`, with no check that a position appears only once. When the model starts every line with `000`, all lines decode to the first entity. That entity gets the single "completed" line and every other claim is "missing", which matches this log exactly. Nothing in the prompt or the reply ties a line to a specific entity, so a correct grade can't be told apart from a mislabeled one. The title's "52 processed" also overcounts the 27 claimed: retry runs are counted again.

## To-be

Each entity in a batch is sent with its **own unique index**, unique across the whole claimed batch rather than restarting at `000` per chunk or per call (e.g. a lone row can be `024`). Each reply line is mapped back to its entity by that index, through an explicit index → entity map, not by list position. That way async/parallel chunk replies always land on the right entity. Index collisions (several lines with one index) and unknown indexes are treated as per-entity decode failures, not silently collapsed onto one entity. Only entities truly absent from the reply go to retry or error. The completion summary counts each entity once.

## Proposed steps

1. Build a unique index per claimed entity once per batch (claimed order across all chunks, zero-padded), and pass it through chunking so parallel chunks keep their global indexes instead of restarting at `000`.
2. Use that index as the single row label in the assembled content: drop the duplicate `NNN: [index=NNN]:` double label and stamp the entity's own index in `_prep_live_content` / `assemble`.
3. Put an index → entity map in the decode context (alongside or instead of positional `batch_entities`), and have `_decode_payload` resolve each line's leading index through it. A duplicate or unknown index becomes a `decode_failures` entry for the affected entity instead of a positional overwrite.
4. Update the `grade_do` / `grade_get` prompt text in `data/admin/agent_task.json` ("zero-based row index, e.g. `000:`") to say: echo the exact index shown on each row.
5. Fix the batch-complete summary so retry runs don't double-count entities in "N processed".

## Component scope

`src/core/consult.py`: modified. `_prep_live_content` and the `assemble` inside `_consult_scored_dispatch_batch_encoded` build the chunk-local `000…` labels, and `_run_batch_consult` builds the decode context (`batch_entities`) that maps replies back to entities.
`src/core/agent.py`: modified. `_decode_payload` maps reply lines by list position (`batch_entities[pos]`) with no uniqueness check, which is what collapses every `000` line onto one entity.
`src/core/dispatcher.py`: modified. It splits claims into parallel chunks (each restarting its numbering) and builds the Somerset `COMPLETED: N error(s) / M processed` summary that overcounts.
`data/admin/agent_task.json`: modified. The `grade_do` / `grade_get` prompts tell the model to use a zero-based row index like `000:`, which invites the same label on every line.

## Technical scope

`src/core/consult.py`: modified functions `_prep_live_content` and the encoded-dispatch `assemble`, to stamp the entity's batch-unique index once per row. Modified function `_run_batch_consult`, to put an index → entity map into the `do_task` context so the reply can be mapped back by identity rather than position.
`src/core/agent.py`: modified function `_decode_payload`, to resolve each line's index through the index → entity map (falling back to position only where no map is supplied, so other tasks keep working). Duplicate or unknown indexes are recorded as per-entity `decode_failures`.
`src/core/dispatcher.py`: modified chunking path, so each chunk keeps its batch-global indexes. Modified batch-complete summary, so each entity is counted once across retry runs.
`data/admin/agent_task.json`: modified prompt text fields on `grade_do` / `grade_get`, to tell the model to echo each row's own index.

## Ancestor candidates

- [ ] `docs/features/agent/response-validation-layers.md`: the canonical write-up of Pattern A decode and binding (`_decode_payload` pos → id, `_bind_response_jobs_to_claimed`, the "missing → `omitted from response`" rule). This fix changes how pos → entity works.
- [ ] `docs/features/consult/ast-501-encoded-batch-for-qualify-and-evaluate-jd.md`: introduced the encoded batch format with positional `000:` row labels that the grade tasks inherited
- [ ] `docs/features/meteorite/ast-1076-uat-qualify-meteorite-good-extract-error.md`: the origin of `_bind_response_jobs_to_claimed`, the earlier patch for models echoing `000` placeholder ids
- [ ] `docs/features/dispatcher/ast-642-per-entity-retry-vs-error-routing-in-mixed-batch-consult-auto-retry.md`: per-entity DO_RETRY vs error routing (the omitted → DO_RETRY → FAILED_TECHNICAL hop seen here)
- [ ] `docs/features/meteorite/ast-1222-meteorite-do-get-alias-seed-retarget-dispatch.md`: the `meteorite_grade_get` alias that routes through `_consult_scored_dispatch_batch_encoded`

## Original report

```
2026-10-07 01:52:55  [INFO]  somerset | dispatch job starting
meteorite_grade_get — 27 available (batch:
meteorite_grade_get-a4ec9af6-55e0-4bb6-92a9-2c4754009971)
2026-10-07 01:54:48  [ERROR]  f87f8eab-71cf-4a62-b863-515c08dbb1f5 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  fcbc84ca-cc20-4228-98e3-85f23835bb82 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  2ec2b685-2ad6-49a7-9ba3-4c85eb909150 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  69af53bd-5fe2-48f8-b7b2-85924c11a1b2 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  ab4ff529-d9e3-4472-8c03-47ac73f3b86b ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  1a66955c-50af-4b19-a53c-e9a16442fd91 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  bfac96c4-dc59-461e-88d9-63cc0d51b2d4 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  8674e96f-632b-4179-b48b-a048ae78ab89 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  0f8f1d81-ed8d-4c78-a762-01f7f3f92e7c ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  b5245474-ac8b-496e-ae90-f6ed47065d0f ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  924a7d47-c60c-4a86-a0e2-73bdea142053 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  7028b971-cb43-4c5e-a9fb-0ca32713d235 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  f4bef295-d0fe-42e7-a40d-a85696505861 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  55a6d34a-b8b1-4279-8ec7-e90ea2d40220 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  1a2b14f5-f926-428a-9653-35917822f7f1 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  e769541b-8984-4497-a888-87108ef7f248 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  32999a02-ab1f-451e-ae05-39cedcd5aa0c ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  c23a7e75-d6dc-41d6-95df-c1c00ad05c78 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [ERROR]  8b30ec4c-57cb-49ca-9481-3fecaf4539e1 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:54:48  [INFO]  LLM openrouter host=DekaLLM
task=meteorite_grade_get 41.9s stop=end_turn tokens in=22952 out=1200
2026-10-07 01:54:48  [INFO]  bae2d55d-c402-45c0-bd30-d7f547d60c40 |
job consult completed: METEORITE_PASSED_GET (batch:
meteorite_grade_get-a4ec9af6-55e0-4bb6-92a9-2c4754009971)
2026-10-07 01:54:48  [WARNING]  41f2e6d6-fefc-44e0-8dc0-dbf6638cd728
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  f4bef295-d0fe-42e7-a40d-a85696505861
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  6ddd5bf9-e03f-4898-bcc2-72a78b118c82
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  c5840b77-043b-4c11-b7f9-58c0d7afd0c4
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  9d226642-4969-4423-9f90-1689c5e43e7d
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  8f872f1d-9a7e-4581-818a-cddf09f81a62
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [INFO]  LLM openrouter host=DekaLLM
task=meteorite_grade_get 31.3s stop=end_turn tokens in=15273 out=769
2026-10-07 01:54:48  [INFO]  a8f92e91-da3e-4787-a137-2d9814a24d41 |
job consult completed: METEORITE_PASSED_GET (batch:
meteorite_grade_get-a4ec9af6-55e0-4bb6-92a9-2c4754009971)
2026-10-07 01:54:48  [WARNING]  d34edd2c-c8b3-4aeb-afee-ccfbd70037d3
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  f87f8eab-71cf-4a62-b863-515c08dbb1f5
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  fcbc84ca-cc20-4228-98e3-85f23835bb82
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  2ec2b685-2ad6-49a7-9ba3-4c85eb909150
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  69af53bd-5fe2-48f8-b7b2-85924c11a1b2
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  ab4ff529-d9e3-4472-8c03-47ac73f3b86b
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  1a66955c-50af-4b19-a53c-e9a16442fd91
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  bfac96c4-dc59-461e-88d9-63cc0d51b2d4
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  8674e96f-632b-4179-b48b-a048ae78ab89
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  0f8f1d81-ed8d-4c78-a762-01f7f3f92e7c
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  b5245474-ac8b-496e-ae90-f6ed47065d0f
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  924a7d47-c60c-4a86-a0e2-73bdea142053
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  7028b971-cb43-4c5e-a9fb-0ca32713d235
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  55a6d34a-b8b1-4279-8ec7-e90ea2d40220
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  1a2b14f5-f926-428a-9653-35917822f7f1
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  e769541b-8984-4497-a888-87108ef7f248
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  32999a02-ab1f-451e-ae05-39cedcd5aa0c
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  c23a7e75-d6dc-41d6-95df-c1c00ad05c78
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [WARNING]  8b30ec4c-57cb-49ca-9481-3fecaf4539e1
-> METEORITE_PASSED_DO_RETRY [omitted from response]
2026-10-07 01:54:48  [INFO]  LLM openrouter host=DekaLLM
task=meteorite_grade_get 27.9s stop=end_turn tokens in=23815 out=919
2026-10-07 01:55:26  [INFO]  somerset | dispatch job task completed:
meteorite_grade_get pass:4 fail:0 error:23 (batch:
meteorite_grade_get-a4ec9af6-55e0-4bb6-92a9-2c4754009971)
2026-10-07 01:55:26  [INFO]  somerset | dispatch job stopping
meteorite_grade_get — 0 remaining after 2 run(s)
2026-10-07 01:55:26  [INFO]  41f2e6d6-fefc-44e0-8dc0-dbf6638cd728 |
job consult completed: METEORITE_PASSED_GET (batch:
meteorite_grade_get-a4ec9af6-55e0-4bb6-92a9-2c4754009971)
2026-10-07 01:55:26  [ERROR]  c5840b77-043b-4c11-b7f9-58c0d7afd0c4 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:55:26  [ERROR]  9d226642-4969-4423-9f90-1689c5e43e7d ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:55:26  [ERROR]  8f872f1d-9a7e-4581-818a-cddf09f81a62 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:55:26  [ERROR]  6ddd5bf9-e03f-4898-bcc2-72a78b118c82 ->
METEORITE_FAILED_TECHNICAL_GET [omitted from response]
2026-10-07 01:55:26  [INFO]  LLM openrouter host=DekaLLM
task=meteorite_grade_get 32.1s stop=end_turn tokens in=13906 out=1164
2026-10-07 01:55:26  [INFO]  d34edd2c-c8b3-4aeb-afee-ccfbd70037d3 |
job consult completed: METEORITE_PASSED_GET (batch:
meteorite_grade_get-a4ec9af6-55e0-4bb6-92a9-2c4754009971)
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
