# AST-2117 — Consult is validating for grades not expected

<!-- linear-archive: AST-2117 archived 2026-10-16 -->

## Linear archive (AST-2117)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2117/consult-is-validating-for-grades-not-expected  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

Research only — no code changes. Output informs a follow-up bug ticket.

1. **Inventory agent call sites** in `src/core/candidate.py`, `consult.py`, `tracker.py`, `roster.py`: every function that calls into `src/core/agent.py` (`do_task` / dispatch / chain entry points), directly or via a thin wrapper.
2. **Per call site, trace input validation (pre-call):** does the caller (or the agent layer on its behalf) check prompt/rubric content before the call — e.g. asserting the rubric contains a fixed set of grade options, required vectors, or schema keys?
3. **Per call site, trace output validation (post-call):** what runs on the response — e.g. `agent._validate_grade_confidence_in_payload`, `_strict_encoded_batch_consult_envelope_err`, `consult._require_complete_grade_set`, `_hydrate_grade_reasons_from_rubric`, roster `pass_grades` / `fail_grades` checks — and whether each check is **data-driven** (derived from the DB prompt/rubric row) or **hard-coded** (expected grade letters/options baked into code).
4. **Pin the reported failure:** find where roster ends up requiring all grade options even when the prompt content omits them, and why it was wired that way (git blame / originating ticket).
5. **Report** as a comment on this ticket: one table per module — function | agent task key | pre-call validation (Y/N + what) | post-call validation (Y/N + what) | hard-coded vs DB-driven — plus a short summary of how widespread the "code enforces prompt content" pattern is.

## Done when

* Every agent-calling function in the four modules is listed with its pre/post validation status.
* The roster grade-options check is located with file/line and its origin.
* Hard-coded-vs-DB-driven classification is called out for every check, so the follow-up bug ticket can be scoped from the report alone.

## Risks / open questions

* none

---

## Original brief

Somewhere we wired roster to validate rubrics to include all grade options, even when the prompt content omits it.  Why are we validating prompt content for things like this in roster?  If the prompt is wrong, it's a database fix, not a code fix.  As it (wrongly) stands, if the prompt is different than encoded, we get errors.

Peruse candidate, consult, tracker, and roster, list the functions that call agents, and confirm whether or not they validate inputs before the call, and if they validate outputs after the call.

That context of how far the problem is will inform a subsequent bug ticket, this task is research.

### Comments

#### chuckles — 2026-10-09T23:33:33.454Z
[check-linear] answered — re: the `meteorite_grade_do` "missing vectors" error (22:47:38, batch `meteorite_grade_do-5ade3129…`)

**Where it's raised:** `consult._apply_render_verdict_decoded_job` → `_require_complete_grade_set` (consult.py:1382), before any score math. The `_render_score:` prefix in the message is misleading; scoring never ran. `IncompleteGradeSetError` → `METEORITE_FAILED_TECHNICAL_DO`.

**Why all 11 vectors are "missing":** the decoded job had **zero grades**. `meteorite_grade_do` is `grades_encoded_notes`. In that mode `agent._decode_payload` (agent.py:369–445) treats any pipe field that doesn't match `_GRADE_SEG` (2-letter code + grade letter A–F/X + digit 0–5) as **notes**, not as a bad line. If the model wrote its grades in any other shape (e.g. labels instead of codes, `AR=A/3`, a 3-char code, prose), every field went into `notes`, no `decode_failure` was recorded, and the row arrived with `grades: []`. The completeness check then reports every rubric label as missing.

How I ruled out the other path: if the model had used codes that weren't in the rubric, the earlier reason-hydrate step would have raised `No rubric criterion matching vector …` first. Only an empty grade list gets past hydrate and lists all 11 as missing.

**So in AST-2117 terms:** this is the response-format side of "code enforces prompt content." The encoded grammar is hard-coded in `_GRADE_SEG` and doesn't follow what the DB prompt tells the model. The notes mode also swallows a format mismatch silently instead of surfacing it as a retryable decode failure that shows the raw line.

**To confirm the actual shape:** the stored response for that batch is on the deployed DB, not local. Check Admin → agent data for `meteorite_grade_do-5ade3129-88e5-4b0e-be38-9d0eaf2e4e89` (83 output tokens, so it did answer).

#### chuckles — 2026-10-09T23:33:27.946Z
[check-linear] answered — re: the `meteorite_grade_do` `_render_score: missing vectors [...]` error (batch `meteorite_grade_do-5ade3129…`)

**Where it's raised:** `consult._require_complete_grade_set` (consult.py:838), called from `_apply_render_verdict_decoded_job` (consult.py:1382) — the exact-vector-set check every scored grade_* / meteorite_grade_* job runs before score math. `IncompleteGradeSetError` → `_run_batch_consult` routes the job to its fail dest (`METEORITE_FAILED_TECHNICAL_DO`). The `_render_score:` prefix is just the message string; `_render_score` itself never ran.

**Why *all 11* vectors are missing:** the job decoded with an **empty `grades` list**, not with wrong grades. If any grade had decoded under an unknown name, grade-reason hydration (which runs first) would have thrown `No rubric criterion matching vector …` instead. With `grades == []`, hydration is a no-op and the set check reports every rubric label as missing.

**How grades end up empty — `_decode_payload` for `grades_encoded_notes` (agent.py:369–445):** each pipe field must match `_GRADE_SEG` exactly (`^[A-Z]{2}[ABCDFX][0-5]$`, e.g. `ADA4`). Any field that doesn't match is **silently moved into `notes`** (do/get/like allow a notes tail), so a format slip costs every grade without raising a decode error. Repro against current `dev`:

| Model line | Decoded |
|---|---|
| `000\|ADA4\|ASB3\|good fit` | 2 grades ✅ |
| `000\|ADA4 ASB3\|good fit` (space-joined in one field) | `grades: []` |
| `000\|AD=A4\|AS=B3` | `grades: []` |
| `000\|ADA4,ASB3\|x` | `grades: []` |
| `0\|Strong fit overall` (prose only) | `grades: []` |

**What it was in this run:** not visible from here — local DB has no rows for that batch (it ran on the deployed host). The `RESPONSE` block in `agent_data` for that batch_id will show which shape the model sent (out=83 tokens fits a one-field or prose answer).

**Relation to the inventory above:** this is item 5 (exact-set match) plus a decode gap: the notes-tail fallback hides a format violation that should have shown up as a decode failure. Code and rubric are in sync here. Either the prompt/model drifted on format (a DB fix) or the decoder needs to report "line had zero grade segments" as a `decode_failure`. Pick one for the bug ticket.

#### susan — 2026-10-09T23:32:12.761Z
@chuckles So, where did this error come from:

```
[2026-10-09 22:47:32] INFO src.core.dispatcher: somerset | dispatch job starting meteorite_grade_do — 1 available (batch: meteorite_grade_do-5ade3129-88e5-4b0e-be38-9d0eaf2e4e89)
[2026-10-09 22:47:38] INFO src.external.llm_compat: LLM openrouter host=Nebius task=meteorite_grade_do 3.2s stop=end_turn tokens in=9222 out=83
[2026-10-09 22:47:38] ERROR src.core.consult: 1fea8e7e-33f2-4ffa-be71-94ada9e6ce7d -> METEORITE_FAILED_TECHNICAL_DO [_render_score: missing vectors ['AI-Assisted Delivery Rigor', 'Autonomous Scope Ownership', 'Clean Handoff & Documentation', 'Delivering Under Regulatory Weight', 'Distributed Team Cadence', 'Hands-On Technical Partnership', 'Process & Systems Design', 'Rapid Value Ramp', 'Scope Discipline & Iteration Efficiency', 'Stakeholder De-escalation', 'Turnaround of Slipping Programs']]
[2026-10-09 22:47:38] INFO src.core.dispatcher: somerset | dispatch job task completed: meteorite_grade_do pass:0 fail:0 error:1 (batch: meteorite_grade_do-5ade3129-88e5-4b0e-be38-9d0eaf2e4e89)
[2026-10-09 22:47:42] INFO src.core.monitor: [monitor] auto_run_error triggered — task=meteorite_grade_do status=COMPLETED errors=1 processed=1 batch=meteorite_grade_do-5ade3129-88e5-4b0e-be38-9d0eaf2e4e89
[2026-10-09 22:47:42] INFO src.core.monitor: [monitor] fetching meteorite_grade_do-5ade3129-88e5-4b0e-be38-9d0eaf2e4e89 log entries for email body...
[2026-10-09 22:47:42] INFO src.core.monitor: [monitor] sending alert to runtime-dispatch-error-498a58685f26@intake.linear.app — subject: [✅/Somerset] meteorite_grade_do COMPLETED: 1 error(s) / 1 processed | meteorite_grade_do-5ade3129-88e5-4b0e-be38-9d0eaf2e4e89
[2026-10-09 22:47:42] INFO src.core.monitor: [monitor] alert sent OK to runtime-dispatch-error-498a58685f26@intake.linear.app
```

#### chuckles — 2026-10-09T22:42:58.934Z
## Findings — agent call sites & validation

**TL;DR:** No caller checks rubric/prompt *content* before the call. After the call, every rubric-graded path runs the agent's grade letters back through the rubric's own grade table (`consult._lookup_rubric_reason_for_grade`) and **raises** when the letter isn't listed there. The rubric that bites is code, not DB: `EMBEDDED_EVALUATE_JD_CRITERIA` (QC/GC) and `EMBEDDED_COMPANY_PREFILTER_CRITERIA` (RC) live in `src/utils/config.py` and **win over the DB row on merge**, so a DB fix can't fix them. QC's table is A/B/C/F only (no D; X explicitly forbidden since AST-1910) → any QC=D or QC=X answer throws `No rubric description for vector 'Quality Check' grade X` and, in batch consult, **fails the whole batch** (hydrate runs before the per-job loop).

### Shared layer — `agent.do_task` (applies to every row below)

| Stage | Check | Source of truth |
|---|---|---|
| Pre | Empty resolved tokens → call not sent (AST-2000) | DB prompt (data-driven) ✅ |
| Pre | Missing provider API key → not sent | candidate keys ✅ |
| Pre | Caller-chain hydration error → not sent | DB ✅ |
| Pre | `requires_candidate_key` w/o identity → **warn only** | — |
| Pre | Rubric / prompt content | **none** |
| Post | `_strict_encoded_batch_consult_envelope_err` (envelope shape) | code (shape only) |
| Post | `_validate_response_schema` (`TASK_CONFIG.response_schema` types/enums/required) | **code** |
| Post | `_validate_grade_confidence_in_payload` (X⇒conf 0, else 1–5) | **code** |
| Post | `_decode_payload` `_GRADE_SEG` regex — letter ∈ `ASTRAL_CONFIG.valid_grades` (A–F,X) | **code** |
| Post | `_decode_payload` vet path — letter ∈ `INFLOW_CONFIG.vet.pass_grades ∪ fail_grades` (A–D / F; **X illegal**) | **code** |
| Post | `consult._normalize_rubric_task_response` → `_grade_letter_for_criterion` / `_job_from_letter_pipe` silently drop letters ∉ `valid_grades` | **code** |
| Post | `_validate_grades` (expected vectors + `valid_grades`) | **dead** — no TASK_CONFIG task has `vectors` |

### Shared consult helpers (post-call, called by rows below)

| Helper | What it enforces | Fails how |
|---|---|---|
| `_hydrate_grade_reasons_from_rubric` → `_lookup_rubric_reason_for_grade` (consult.py:297–327) | every returned letter must exist in that vector's rubric grade table | `ValueError` → batch/entity fail |
| `_require_complete_grade_set` (consult.py:838) | returned vectors == live rubric labels exactly | `IncompleteGradeSetError` → retry/fail dest |
| `_require_not_all_literal_x` | not every grade X | fail dest |
| `_render_pass_fail` | F≥conf2 / all-X / no conf>1 → fail | verdict (code rule) |
| `_render_score` | rubric importance math | verdict |
| `candidate.rubric_criteria_for_task` → `_merge_embedded_*` | **code-defined RC / QC / GC override DB rows with the same code** | — (root of "can't fix in DB") |

### roster.py

| Function | Task key | Pre-call (caller) | Post-call (caller) |
|---|---|---|---|
| `vet_inflow_discovery_company` (510) | `vet_inflow_discovery` cfg | blurb present | `_apply_vet_inflow_result_row`: grade ∈ **hard-coded** `pass_grades` {A,B,C,D} / `fail_grades` {F}; anything else (incl. X) → `unknown grade` error |
| `vet_inflow_discovery_company_batch` (559) | same | ready-row filter | same, per hit_index |
| `resolve_website_company` (707) | `find_company_website` | hits list non-empty | `task_success` + website present (shape only) |
| `prefilter_company` (1809) | `prefilter_company` | website present | `_apply_prefilter_decoded_company_outcome`: **hydrate (letter∈table)** + `_require_complete_grade_set` + `_render_pass_fail` / `_render_score`; ValueError → `_prefilter_fail` |
| `_run_batch_company_prefilter` (1975) | `prefilter_company` | — | **batch-wide hydrate** (roster.py:2080) — one bad letter fails all companies; then per-company outcome as above |
| `company_upshot_batch` (2258) | upshot task | — | upshot text present per company (shape) |
| `_find_job_page_from_assembled` (2409) | `select_job_page` | — | dict shape / link-retry logic |
| `_fetch_select_job_page` (3083) | `select_job_page` | — | raises if no parsed_response |
| `_fetch_prefilter_notes` (3348) | `prefilter_company` | website + visible text | hydrate (letter∈table), errors swallowed → no notes |
| `_fetch_parse_job_list` (3578) | `parse_job_list` | — | success/empty-tokens; selector validated separately (`_validate_parse_job_list_raw_job_listings`) |

### consult.py

| Function | Task key | Pre-call (caller) | Post-call (caller) |
|---|---|---|---|
| `render_verdict` (1423) | per-job consult | job/company + live_content present | `_apply_render_verdict_decoded_job`: **hydrate (letter∈table)**; scored → `_require_complete_grade_set` + all-X + `_render_score`; binary → `_render_pass_fail` |
| `_run_batch_consult` (1666) — backs `qualify_job_listings`, `qualify_meteorite`, `evaluate_jd_batch`, `evaluate_meteorite_batch`, `grade_do/get/like_batch`, `meteorite_like_batch` | each | live_content assembly | **batch-wide hydrate** (consult.py:1775) — one bad letter fails the whole batch → error_state; then per-job `process` (qualify: `_require_complete_grade_set`+pass/fail; evaluate_jd: same; grade_*: `_apply_render_verdict_decoded_job`) |
| `_run_analysis_upshot_batch` (1220) | analysis upshot | company + live_content | parsed is dict (shape) |
| `_run_cover_letter_for_job` (2598) → `agent.run_cover_letter_artifact_chain_for_job` | cover letter chain | resume body persisted | chain success only |
| `_run_dispatch_chain_job_batch` (2624) | dispatch chain | row matches chain, cd present | success only (graduation in do_task) |

### candidate.py

| Function | Task key | Pre-call (caller) | Post-call (caller) |
|---|---|---|---|
| `parse_candidate_resume` (3664) | `craft_resume_base` | raw resume non-empty | parsed present; split structure/content |
| `run_requested_artifacts_dispatch` (3870) | run_next chain start | candidate present | success; craft-rubric persist merges embedded RC/QC/GC then `normalize_rubric_artifacts_on_save` (≥2 grade lines, importance 1–10 — **does not require all letters**) |
| `run_session_resume_parse` (3954) | `simple_resume_parse` | resume text + candidate | success only |
| `run_candidate_artifact_generation` (4127) | `craft_*` | candidate present | success; craft-rubric output re-merged with embedded criteria (candidate.py:4279/4285) |

### tracker.py

No agent calls. Only reads stored responses (`_parsed_response_from_stored_response_text`, `get_entity_agent_story`).

### Where "prompt content enforced in code" bites (input for the bug ticket)

1. **Embedded rubric vectors override DB** — `EMBEDDED_EVALUATE_JD_CRITERIA` (QC, GC) and `EMBEDDED_COMPANY_PREFILTER_CRITERIA` (RC), config.py:2489–2600, merged "embedded wins on code" in `candidate._merge_embedded_*`. QC text also carries the "Never grade QC X" rule (AST-1910, 1cacc0635). DB edits to these vectors are ignored.
2. **Letter-must-be-in-table check** — `_lookup_rubric_reason_for_grade` raises instead of degrading (e.g. empty reason). Combined with #1: QC=D/X → hard failure.
3. **Batch blast radius** — hydrate runs once over the whole response in `_run_batch_consult` (consult.py:1775) and `_run_batch_company_prefilter` (roster.py:2080), so one off-table letter fails every entity in the batch.
4. **Hard-coded letter sets** — `ASTRAL_CONFIG.valid_grades`, `INFLOW_CONFIG.vet.pass_grades/fail_grades`, X⇒conf-0 rule, `_render_pass_fail` F/X rules. These are grade-scale semantics (arguably legit code), not per-prompt content — flag for Susan's call.
5. **Exact vector-set match** (`_require_complete_grade_set`) compares against the live (DB+embedded) rubric — data-driven, but inherits #1.
6. Dead code: `agent._validate_grades` (no task defines `vectors`).

---

_Implementation detail may live in git history on `origin/dev`._
