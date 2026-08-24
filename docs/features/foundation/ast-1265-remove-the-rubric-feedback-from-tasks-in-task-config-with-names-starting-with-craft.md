# AST-1265 — Remove the rubric feedback from tasks in task_config with names starting with craft*

<!-- linear-archive: AST-1265 archived 2026-08-17 -->

## Linear archive (AST-1265)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1265/remove-the-rubric-feedback-from-tasks-in-task-config-with-names  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-755

### Description

## Purpose

Craft (and other non-grading) tasks are being asked for rubric vector feedback even though their prompts never include candidate `{$RUBRIC_VECTORS}` to review. That wastes model attention and produces nonsense feedback expectations. This epic adds an explicit per-task `request_feedback` switch in `TASK_CONFIG`, gates prompt/response feedback on that flag, and retires `is_rubric_backed_task` — a thin AST-724 helper that only existed to drive those same feedback gates from rubric ownership (which incorrectly includes craft authors).

## Functional scope

* **Per-task feedback flag:** Every `TASK_CONFIG` entry has a boolean `request_feedback` that is the sole authority for whether vector rubric feedback is in play for that task.
* **Default truth rule:** `request_feedback` is `false` for every task whose prompt does **not** send candidate `{$RUBRIC_VECTORS}`; it is `true` only for tasks whose prompt does send that token. All `craft*` keys fall on the false side under this rule (they author rubrics; they do not grade against candidate vectors).
* **Prompt gating:** When `request_feedback` is false, the run must not append the vector-feedback instructions to the prompt. When true, those instructions are included as today.
* **Response gating:** When `request_feedback` is false, the run must not expect or require vector-feedback content in the response, and must not treat the task as a vector-feedback capture target. When true, existing feedback expectation and capture behavior remain.
* **Retire is_rubric_backed_task:** After feedback gates use `request_feedback`, delete `is_rubric_backed_task`. It has no non-feedback production purpose.
* **Keep owner resolution:** `rubric_owner_task_key` and the craft/consumer artifact→owner maps stay for token hydrate, feedback attribution (when requested), craft recover, Admin Vector Feedback filters, and twin consumers — they are not the feedback on/off switch.

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block` (behavior-driving `request_feedback` lives on each `TASK_CONFIG` entry; callers read the flag — no parallel magic set of task keys); `pattern.layers.import-discipline` (config owns the flag; core agent consumes it).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.config.config-source-of-truth` (`TASK_CONFIG` is the flag home); `astral.standards.no-hardcoded-sets` (do not special-case `craft*` by name prefix in agent code — use the flag); `astral.standards.in-scope-only`; `astral.standards.no-cross-contamination`; `astral.layers.import-direction`; `astral.agent.grade-vector-validation` (feedback wire format / capture stays behind the flag for grading tasks only).

## Boundaries

* Does **not** delete or redefine `rubric_owner_task_key` / `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` / `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` — those remain for ownership and `{$RUBRIC_VECTORS}` resolution. Only the boolean feedback gate helper `is_rubric_backed_task` is retired.
* Does **not** change rubric authoring prompts, craft response schemas, or craft `run_next` chains (adjacent UAT on Astral Candidate: AST-1264).
* Does **not** build Manage Tasks / admin UI editing for a Feedback flag (Backlog AST-755 stays untouched).
* Does **not** invent new feedback wire formats or change `RUBRIC_FEEDBACK_CONFIG` value codes.
* Does **not** require every non-feedback task to stop using the standard `agent_performance` / `agent_payload` envelope — only the vector-feedback ask/expect/capture path is gated.
* Must not break grading tasks that today correctly receive `{$RUBRIC_VECTORS}` and capture `vector_reviews`.

## Acceptance criteria

1. Every `TASK_CONFIG` entry has an explicit boolean `request_feedback`.
2. Every task whose seeded/runtime prompt includes `{$RUBRIC_VECTORS}` has `request_feedback: true`; every task that does not (including all `craft*` keys) has `request_feedback: false`.
3. Running a `craft*` (or any other `request_feedback: false`) task produces a prompt with **no** vector-feedback instruction suffix asking for `vector_reviews`.
4. Running a `request_feedback: true` task still includes the vector-feedback instructions and still can capture vector feedback on success as today.
5. Agent feedback ask/expect/capture reads `request_feedback` from config — not ownership linkage, and not a hardcoded `craft*` name prefix.
6. `is_rubric_backed_task` is removed from product code (and its dedicated tests/bible references updated or dropped).
7. `rubric_owner_task_key` (and maps) still resolve for `{$RUBRIC_VECTORS}` hydrate, feedback row attribution when requested, craft recover, Admin Vector Feedback filters, and twin consumers.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1!: **TASK_CONFIG request_feedback flag inventory - Ada**

Adds `request_feedback` to every `TASK_CONFIG` entry and sets true/false from the `{$RUBRIC_VECTORS}` prompt rule (false for all keys that do not send that token, including every `craft*`). Exposes a config-side reader for the flag. Does **not** own prompt/response gating or helper deletion (child 2).
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`.

#### 2: **Gate feedback on request_feedback; delete is_rubric_backed_task - Ada**

After #1: prompt suffix, envelope normalize/snapshot, and vector-feedback capture follow `request_feedback` only; delete `is_rubric_backed_task`. Leave `rubric_owner_task_key` / artifact→owner maps intact for non-gate uses. Does **not** own Manage Tasks UI.
**Citations:** `pattern.config.config-block`; `astral.standards.no-hardcoded-sets`; `astral.agent.grade-vector-validation`; `astral.layers.import-direction`.

**Monolith check:** Six functional-scope bullets → two children (config inventory vs agent gate + delete) — intentional; owner maps stay outside the feedback flag.

**New patterns:** none.

---

## Original brief

craft agents are getting asked to give feedback on their rubrics when their prompts don't have rubrics to grade.  Set "request_feedback" as a true/false flag in task_config for each task, to determine if the feedback is requested in the prompt and expected in the response.  Set it to false for all task keys that do not send candidate {$RUBRIC_VECTORS} in the prompt.

### Comments

#### susan — 2026-08-07T22:43:05.511Z
Fix was implemented somewhere along the line…. 🙂

#### chuckles — 2026-08-07T21:39:12.595Z
@susan Clarifier first: `is_rubric_backed_task` is **not** a field on `TASK_CONFIG` entries. It is a computed helper: `True` iff `rubric_owner_task_key(task_key)` is set (owner/consumer key, craft→artifact map, or `rubric_artifact` on the entry).

**True today (17 of 47 `TASK_CONFIG` keys):**
- Owners/consumers: `prefilter_company`, `qualify_job_listings`, `evaluate_jd`, `evaluate_meteorite`, `grade_get`, `grade_do`, `grade_like`
- Craft authors: `craft_prefilter_rubric`, `craft_joblist_rubric`, `craft_jobdesc_rubric`, `craft_evaluate_meteorite_rubric`, `craft_get_rubric`, `craft_do_rubric`, `craft_like_rubric`
- Twins via `rubric_artifact`: `meteorite_like`, `meteorite_grade_get`, `meteorite_grade_do`

**False today (30):** everyone else in `TASK_CONFIG`, including `craft_resume_base`, `craft_company_search_terms`, intake/*, resume/cover hops, `find_company_website`, `parse_job_list`, `qualify_meteorite`, `meteorite_upshot`, etc.

**Contrast with proposed `request_feedback: true`** (seeded prompts that contain `{$RUBRIC_VECTORS}` — only 8): `prefilter_company`, `qualify_job_listings`, `evaluate_jd`, `evaluate_meteorite`, `grade_get`, `grade_do`, `grade_like`, `meteorite_like`.

So the gap that hurts us is the other 9 “True” keys (all seven craft rubric authors + `meteorite_grade_get` / `meteorite_grade_do`) — ownership says True, but they do not send candidate vectors to review.

— Chuckles

#### susan — 2026-08-07T21:37:46.232Z
So, for which tasks in task_config is `is_rubric_backed_task` set to True, and which to False?

#### chuckles — 2026-08-07T21:09:52.248Z
@susan Trace result:

**`is_rubric_backed_task` itself is not necessary.** It is a one-line wrapper (`rubric_owner_task_key(task_key) is not None`) added in AST-724 so “every rubric-backed task” would get the vector-feedback prompt suffix + envelope capture. Production call sites today are **only** those three gates in `do_task` (prompt suffix, normalize-for-capture, envelope snapshot). Once those gates read `request_feedback`, the helper has no remaining callers and should be **deleted** in this epic.

**What would break if we removed only `is_rubric_backed_task` today (before `request_feedback`):** grading tasks would stop getting the feedback ask/capture — that is the whole AST-724 wire. Craft would also stop being wrongly asked (good), but graders would regress until the new flag is in place.

**Related logic that *is* still needed** (do not delete with the boolean):
- `rubric_owner_task_key` / artifact→owner maps — resolve which rubric owner supplies `{$RUBRIC_VECTORS}`, attribute `vector_feedback` rows, craft “already populated” recover, Admin Vector Feedback filters, twin consumers (e.g. `meteorite_like` → `grade_like`).

So: keep owner resolution; retire `is_rubric_backed_task` as part of wiring `request_feedback`. Description updated.

— Chuckles

#### susan — 2026-08-07T21:08:27.868Z
I have zero-memory of a need for `is_rubric_backed_task` or its related logic.  Please trace it back and justify its necessity?  What wouldn't work if we removed it?

#### chuckles — 2026-08-07T20:53:14.380Z
@susan `is_rubric_backed_task` is **not** the feedback flag — it would not fix this.

What it means today: `True` when the task has a **rubric owner linkage** (`rubric_owner_task_key` is set). That includes both:
- **consumers** that grade against candidate vectors (`grade_*`, `evaluate_*`, etc.)
- **craft rubric authors** that *create* those rubrics (`craft_*_rubric`)

What it is used for today (and why craft is broken):
1. Append the vector-feedback prompt suffix
2. Normalize / snapshot the envelope for `vector_reviews` capture

So ownership and “ask for feedback” were collapsed into one helper. Craft is correctly rubric-backed for ownership, and incorrectly treated as a feedback requester.

Your `{$RUBRIC_VECTORS}` rule is a **different** boolean (prompt actually carries candidate vectors to review). Reusing `is_rubric_backed_task` as that switch would leave craft on `True` and keep asking for feedback. Separate `request_feedback` (or narrowing the *feedback* call sites off ownership) is required; we should not redefine ownership to mean feedback.

Description updated to say that explicitly.

— Chuckles

#### susan — 2026-08-07T20:52:07.253Z
What is the `is_rubric_backed_task` value used for?  I don't want to duplicate if that is the actual value that could be used as our flag.

---

_Implementation detail may live in git history on `origin/dev`._
