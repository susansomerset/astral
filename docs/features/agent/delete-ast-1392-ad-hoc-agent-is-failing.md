# AST-1392 — Ad hoc Agent is failing

<!-- linear-archive: AST-1392 archived 2026-08-31 -->

## Linear archive (AST-1392)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1392/ad-hoc-agent-is-failing  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Agent Ad Hoc Test is a diagnostic workbench: when the model actually replies, Susan needs to see that reply and keep it on the run's inspection trail. Today a successful DeepSeek (or similar) JSON payload whose body is an object — not a string — dies at RESPONSE storage (`block_data must be a str`) even though the live Test still looked fine. This epic makes a successful Ad Hoc reply bulletproof: type, schema, envelope shape, or store serialization must not invalidate or hide the body.

## Functional scope

1. When Agent Ad Hoc Test receives a successful provider reply, the workbench displays that body as text. If the body is a structured object or list, it is shown as JSON text so the operator sees what the model returned, not a type error and not a Python dump. Other shapes show as their text.
2. The same text is stored as the RESPONSE block for that Test run, so Execution History inspection has the body. The data store still only accepts text; the workbench serializes before write. A structured payload must not raise a string-type storage error.
3. A successful provider reply is a successful Test. Type, schema, envelope shape, or storage serialization must not mark the Test failed, replace the body with an error overlay, or dump a store traceback as the operator-facing outcome. Provider or API failures still fail the Test — there is no body to display.
4. When `debug=True` on this workbench path, a serialized store shows what was found (type/shape) and what was recorded (text) under Style D index detail. When `debug=False`, this path adds no new debug lines. After this epic, a successful structured payload must not emit `_store_response_block failed` with `block_data must be a str`.

## Architectural definition

* **Patterns to reuse** — `pattern.batch.entity-agent-responses`: Ad Hoc Test already writes RESPONSE rows through the existing store helper; keep tagging `entity_id` when an entity is in scope, and keep `block_data` as text. `pattern.ui.admin-endpoint`: the Admin Test route stays a thin authenticated surface that returns the serialized body; React renders it. `pattern.layers.import-discipline`: serialize and persist in core; UI does not call data. Reuse the existing `do_task` habit of JSON-serializing object/list payloads before RESPONSE write — this is the same store contract, applied to the workbench success path that currently extracts a payload and passes a non-string through.
* **New patterns proposed** — none. Serializing a structured Ad Hoc body to text before store/display is not a new catalog shape.
* **Applicable statutes** — universal active set; `astral.standards.data-raises-caller-logs` (do not loosen the data-layer string contract — core serializes, data still raises on non-text); `astral.batch.entity-agent-responses-latest-only` (RESPONSE rows remain the inspection trail); `astral.agent.do-task-delegation` (Ad Hoc Test stays on the workbench wrapper, not routed through production `do_task` validation just to get a store); `astral.standards.debug-contract-gated` (found→recorded only when `debug=True`); `astral.standards.in-scope-only` (no production ingest/schema redesign); `astral.standards.dry-and-focused-functions` (one stringify habit for workbench success, not parallel store helpers); `astral.layers.import-direction` / `astral.layers.core-vs-external-bright-line`.

## Boundaries

* Does **not** change production `do_task` schema validation or AST-1289 integer-to-string coerce on declared string fields. Pipeline ingest stays strict except for that already-shipped coerce.
* Does **not** relax `save_agent_data` to accept non-text `block_data`. The string contract stays; callers serialize.
* Does **not** treat provider/API failures as success, skip ledger rows, or drop prompt-block storage.
* Does **not** change Preview (no provider call), dispatch batch apply, or other Admin pages except Agent Ad Hoc Test display of the returned body.
* Does **not** invent a new envelope: when a payload key is present, display/store that payload body (JSON text if structured); when it is absent, display/store the raw reply text. This is not a dump of a new wrapper format.
* Does **not** reopen AST-1391 DeepSeek Big token floors on the workbench path.

## Acceptance criteria

1. An Agent Ad Hoc Test whose model returns a successful JSON envelope with an object payload (the `craft_company_search_terms` shape in the original brief) completes as success: the workbench shows the payload as JSON text, and no `_store_response_block failed` / `block_data must be a str` traceback appears for that run.
2. Execution History inspection for that Test run includes a RESPONSE body equal to the text shown in the workbench (JSON text of the payload, not an empty or missing block).
3. A successful reply that is already plain text still displays and stores as that text — no extra JSON wrapping.
4. A provider/API failure still surfaces as a failed Test (error shown; no fake success body).
5. With `debug=True`, the serialized store is visible as found→recorded under Style D; with `debug=False`, this path adds no new debug lines.
6. Production dispatch/`do_task` schema rejection of non-coerced bad types is unchanged (bool/object on a declared string field still fails ingest the way it does after AST-1289).

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1!: **Serialize Ad Hoc success body to text - Ada**

Own the workbench success path so any successful model body becomes text before RESPONSE write (JSON text for objects/lists, otherwise the raw text), using one stringify habit rather than a second store helper. Persist that text; with `debug=True` show found type/shape → recorded text; never let a non-string payload raise a storage type error as the Test outcome. Does **not** own React chrome or production `do_task` schema validation (see #2 and Boundaries).
**Citations:** `pattern.batch.entity-agent-responses`; `astral.standards.data-raises-caller-logs`; `astral.batch.entity-agent-responses-latest-only`; `astral.standards.debug-contract-gated`; `astral.standards.dry-and-focused-functions`; `astral.agent.do-task-delegation`.
**Estimate: 2**

#### 2: **Show Ad Hoc Test body without type invalidation - Katherine**

After #1, the Admin Test response returns that same text, and the workbench displays it (pretty-printed when it is JSON). A successful provider reply must never be replaced with a type or schema error overlay. Does **not** own persist, debug contract, or production ingest.
**Citations:** `pattern.ui.admin-endpoint`; `pattern.layers.import-discipline`; `astral.layers.import-direction`; `astral.standards.in-scope-only`.
**Estimate: 2**

Monolith check: Functional scope has 4 capabilities and 2 children — persist/debug vs display are separable UAT slices; stringify in core must land first so display and Execution History share one text.

---

## Original brief

```
127.0.0.1 - - [15/Aug/2026 18:06:31] "GET /api/deploy_status HTTP/1.1" 200 -
LLM deepseek task=adhoc 101.8s stop=end_turn tokens in=693 out=8372
send_to_deepseek index 1/1 adhoc -> success
 | provider=deepseek model=deepseek-v4-pro task=adhoc duration=101.8s stop_reason=end_turn
 | vendor=deepseek-v4-pro tokens fresh=693 cache_read=768 cache_write=0 output=8372
 | response_preview:
 | {
 |   "agent_performance": {
 |     "status": "success",
 |     "note": "No blockers. Task completed in full and delivered in the payload below."
 |   },
 |   "agent_payload": {
 |     "provenance_note": "These search term sets are built strictly from the three observable facts supplied in this thread: (1) many years of product marketing in SaaS, (2) experience with medical software, and (3) hands-on elder-caregiving context for a mother with diabetes. Susan's priorities/preferences file and any additional experience were not available in this thread, so I have deliberately drawn on nothing else. Every set points at companies with a software output where those three facts overlap, so each is a plausible place for Susan to contribute meaningfully. Terms intentionally avoid job titles and the words 'jobs,' 'careers,' 'hiring,' 'roles,' and avoid queries that mainly return patient advice rather than companies. To widen or sharpen this net with new categories, route the questions at the end to Susan; her answers are the only legitimate source for new terms.",
 |     "search_term_sets": [
 |       {
 |         "set_id": "set_01",
 |         "theme": "Healthcare SaaS, broad net",
 |         "terms": [
 |           "healthcare SaaS platforms",
 |           "B2B software for healthcare organizations",
 |           "healthcare software companies",
 | <184 lines omitted>
 |           "digital health startups for chronic illness",
 |           "aging and chronic disease technology companies",
 |           "digital health companies improving older adult care"
 |         ]
 |       }
 |     ],
 |     "questions_for_susan": [
 |       "Which SaaS industries or verticals has she marketed in beyond health and medical (e.g., logistics, fintech, HR, edtech)? Her answer would justify entirely new non-healthcare term sets.",
 |       "On the medical software side, was her experience clinical/provider-facing, payer-facing, patient-facing, or device-companion software? That would let us weight these sets toward her deepest ground.",
 |       "Beyond diabetes, what conditions or day-to-day situations shape her mother's care (mobility, memory, nutrition, coordinating multiple clinicians)? That would suggest additional caregiver-tool search angles.",
 |       "Which problems does she most want to solve in her work (access, affordability, aging independence, caregiver burden, clinician time)? That would help the team filter which newly found companies earn a place on the watch list.",
 |       "What company stage and size does she want to target (early startup, growth-stage, established vendor)? That would help the team decide which weekly results are worth following closely."
 |     ]
 |   }
 | }
 | agent_data_write block_type=SYSTEM outcome=ref_existing agent_data_id=adhoc-craft_company_search_terms-9dfbaaa9-ed68-4d77-be15-c45c247446e0-system-62d8d1467a37b990 ref_agent_data_id='craft_do_rubric-fee7ae75-a7bf-442d-8bdf-60b2d3cef7d7-system-be201799ca609ff9'
127.0.0.1 - - [15/Aug/2026 18:06:31] "GET /api/nav_config?candidate_id=somerset HTTP/1.1" 200 -
 | agent_data_write block_type=TASK outcome=ref_existing agent_data_id=adhoc-craft_company_search_terms-9dfbaaa9-ed68-4d77-be15-c45c247446e0-task-285773f9f8ad290e ref_agent_data_id='craft_company_search_terms-ddcc80d6-9003-48b7-8269-37a63ee5b1b2-task-f3fc67d0d58c1bc6'
[ ~ ] _store_response_block failed
Traceback (most recent call last):
  File "/Users/susan/chuckles/astral/src/core/agent.py", line 3555, in run_adhoc_workbench_test
    _store_response_block(
  File "/Users/susan/chuckles/astral/src/core/agent.py", line 1690, in _store_response_block
    result = save_agent_data(
             ^^^^^^^^^^^^^^^^
  File "/Users/susan/chuckles/astral/src/data/database.py", line 5872, in save_agent_data
    raise ValueError("block_data must be a str")
ValueError: block_data must be a str
adhoc workbench test finished task_key='craft_company_search_terms' batch_id=adhoc-craft_company_search_terms-9dfbaaa9-ed68-4d77-be15-c45c247446e0 success=True cost=0.010369094999999998
127.0.0.1 - - [15/Aug/2026 18:06:31] "POST /api/admin/adhoc/test HTTP/1.1" 200 -
127.0.0.1 - - [15/Aug/2026 18:07:01] "GET /api/deploy_status HTTP/1.1" 200 -
127.0.0.1 - - [15/Aug/2026 18:07:01] "GET /api/nav_config?candidate_id=somerset HTTP/1.1" 200 -
```

Response appeared fine in the AdHoc agent.

I also want to make the ad hoc agent response "bullet proof".  No matter what it is, do not invalidate it for data types or any other reason.  Just display exactly what comes back.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
