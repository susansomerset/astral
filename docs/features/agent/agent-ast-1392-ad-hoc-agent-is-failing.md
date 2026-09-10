# AST-1392 — Ad hoc Agent is failing

**Component:** agent  
**Children:** AST-1393, AST-1394  
**Linear archived:** AST-1392 2026-08-31; AST-1393 2026-08-31; AST-1394 2026-08-31

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-15 18:29 | AST-1393 | docs | `2a87dcd53` | plan — serialize ad-hoc success body to text |
| 2026-08-15 18:32 | AST-1393 | docs | `41cce40b3` | Joan validate — stringify before store |
| 2026-08-15 18:36 | AST-1393 | docs | `32a89ab5a` | review stub — stage 1 |
| 2026-08-15 18:36 | AST-1393 | code | `7fed10d1f` | stringify ad-hoc success body before store |
| 2026-08-15 18:44 | AST-1393 | merge-tests | `a45fff616` | origin/tests 4667aad6389599ab9fadd1c263465d412c51e5dc |
| 2026-08-15 18:44 | AST-1393 | test | `4667aad63` | stringify Ad Hoc success body before store |
| 2026-08-15 18:50 | AST-1393 | docs | `79aeb64ed` | Radia review — core stringify clean |
| 2026-08-15 18:58 | AST-1394 | docs | `eed6751e7` | plan — show ad-hoc test body without type invalidation |
| 2026-08-15 19:02 | AST-1394 | docs | `c282658c9` | Joan validate — display without invalidation |
| 2026-08-15 19:05 | AST-1394 | code | `e5d49eb97` | stringify ad-hoc test HTTP body via _caller_response_blob |
| 2026-08-15 19:06 | AST-1394 | code | `f685256ea` | coerce ad-hoc success body to text in workbench |
| 2026-08-15 19:07 | AST-1394 | docs | `f1f0b20b6` | review stub — stages 1–2 |
| 2026-08-15 19:11 | AST-1394 | test | `322c49043` | Ad Hoc Test body display without type invalidation |
| 2026-08-15 19:12 | AST-1394 | merge-tests | `c4c22d2d2` | origin/tests 322c4904322dd61bb81f66fae00a36686f10f6cc |
| 2026-08-15 19:18 | AST-1394 | docs | `c261d379c` | Radia review — display overlay clean |
| 2026-08-31 14:16 | AST-1393 | docs | `064988d80` | archive Linear issue content |
| 2026-08-31 14:16 | AST-1394 | docs | `46a46a48a` | archive Linear issue content |
| 2026-08-31 14:19 | AST-1392 | docs | `84f7a13dc` | archive Linear issue content |

## Epic — AST-1392

_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1392/ad-hoc-agent-is-failing · Status at archive: Archive · Project: Astral Agent · Assignee: chuckles · Priority / estimate: Urgent / 3_

### Purpose

Agent Ad Hoc Test is a diagnostic workbench: when the model actually replies, Susan needs to see that reply and keep it on the run's inspection trail. Today a successful DeepSeek (or similar) JSON payload whose body is an object — not a string — dies at RESPONSE storage (`block_data must be a str`) even though the live Test still looked fine. This epic makes a successful Ad Hoc reply bulletproof: type, schema, envelope shape, or store serialization must not invalidate or hide the body.

### Functional scope

1. When Agent Ad Hoc Test receives a successful provider reply, the workbench displays that body as text. If the body is a structured object or list, it is shown as JSON text so the operator sees what the model returned, not a type error and not a Python dump. Other shapes show as their text.
2. The same text is stored as the RESPONSE block for that Test run, so Execution History inspection has the body. The data store still only accepts text; the workbench serializes before write. A structured payload must not raise a string-type storage error.
3. A successful provider reply is a successful Test. Type, schema, envelope shape, or storage serialization must not mark the Test failed, replace the body with an error overlay, or dump a store traceback as the operator-facing outcome. Provider or API failures still fail the Test — there is no body to display.
4. When `debug=True` on this workbench path, a serialized store shows what was found (type/shape) and what was recorded (text) under Style D index detail. When `debug=False`, this path adds no new debug lines. After this epic, a successful structured payload must not emit `_store_response_block failed` with `block_data must be a str`.

### Architectural definition

* **Patterns to reuse** — `pattern.batch.entity-agent-responses`: Ad Hoc Test already writes RESPONSE rows through the existing store helper; keep tagging `entity_id` when an entity is in scope, and keep `block_data` as text. `pattern.ui.admin-endpoint`: the Admin Test route stays a thin authenticated surface that returns the serialized body; React renders it. `pattern.layers.import-discipline`: serialize and persist in core; UI does not call data. Reuse the existing `do_task` habit of JSON-serializing object/list payloads before RESPONSE write — this is the same store contract, applied to the workbench success path that currently extracts a payload and passes a non-string through.
* **New patterns proposed** — none. Serializing a structured Ad Hoc body to text before store/display is not a new catalog shape.
* **Applicable statutes** — universal active set; `astral.standards.data-raises-caller-logs` (do not loosen the data-layer string contract — core serializes, data still raises on non-text); `astral.batch.entity-agent-responses-latest-only` (RESPONSE rows remain the inspection trail); `astral.agent.do-task-delegation` (Ad Hoc Test stays on the workbench wrapper, not routed through production `do_task` validation just to get a store); `astral.standards.debug-contract-gated` (found→recorded only when `debug=True`); `astral.standards.in-scope-only` (no production ingest/schema redesign); `astral.standards.dry-and-focused-functions` (one stringify habit for workbench success, not parallel store helpers); `astral.layers.import-direction` / `astral.layers.core-vs-external-bright-line`.

### Boundaries

* Does **not** change production `do_task` schema validation or AST-1289 integer-to-string coerce on declared string fields. Pipeline ingest stays strict except for that already-shipped coerce.
* Does **not** relax `save_agent_data` to accept non-text `block_data`. The string contract stays; callers serialize.
* Does **not** treat provider/API failures as success, skip ledger rows, or drop prompt-block storage.
* Does **not** change Preview (no provider call), dispatch batch apply, or other Admin pages except Agent Ad Hoc Test display of the returned body.
* Does **not** invent a new envelope: when a payload key is present, display/store that payload body (JSON text if structured); when it is absent, display/store the raw reply text. This is not a dump of a new wrapper format.
* Does **not** reopen AST-1391 DeepSeek Big token floors on the workbench path.

### Acceptance criteria

1. An Agent Ad Hoc Test whose model returns a successful JSON envelope with an object payload (the `craft_company_search_terms` shape in the original brief) completes as success: the workbench shows the payload as JSON text, and no `_store_response_block failed` / `block_data must be a str` traceback appears for that run.
2. Execution History inspection for that Test run includes a RESPONSE body equal to the text shown in the workbench (JSON text of the payload, not an empty or missing block).
3. A successful reply that is already plain text still displays and stores as that text — no extra JSON wrapping.
4. A provider/API failure still surfaces as a failed Test (error shown; no fake success body).
5. With `debug=True`, the serialized store is visible as found→recorded under Style D; with `debug=False`, this path adds no new debug lines.
6. Production dispatch/`do_task` schema rejection of non-coerced bad types is unchanged (bool/object on a declared string field still fails ingest the way it does after AST-1289).

### Dependencies and blockers

none.

### Open questions

none.

### Proposed child tickets


##### 1!: **Serialize Ad Hoc success body to text - Ada**

Own the workbench success path so any successful model body becomes text before RESPONSE write (JSON text for objects/lists, otherwise the raw text), using one stringify habit rather than a second store helper. Persist that text; with `debug=True` show found type/shape → recorded text; never let a non-string payload raise a storage type error as the Test outcome. Does **not** own React chrome or production `do_task` schema validation (see #2 and Boundaries).
**Citations:** `pattern.batch.entity-agent-responses`; `astral.standards.data-raises-caller-logs`; `astral.batch.entity-agent-responses-latest-only`; `astral.standards.debug-contract-gated`; `astral.standards.dry-and-focused-functions`; `astral.agent.do-task-delegation`.
**Estimate: 2**

##### 2: **Show Ad Hoc Test body without type invalidation - Katherine**

After #1, the Admin Test response returns that same text, and the workbench displays it (pretty-printed when it is JSON). A successful provider reply must never be replaced with a type or schema error overlay. Does **not** own persist, debug contract, or production ingest.
**Citations:** `pattern.ui.admin-endpoint`; `pattern.layers.import-discipline`; `astral.layers.import-direction`; `astral.standards.in-scope-only`.
**Estimate: 2**

Monolith check: Functional scope has 4 capabilities and 2 children — persist/debug vs display are separable UAT slices; stringify in core must land first so display and Execution History share one text.

---

### Original brief

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

#### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1393 — Serialize Ad Hoc success body to text

_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1393/serialize-ad-hoc-success-body-to-text-ad-hoc-agent-is-failing · Status at archive: Archive · Project: Astral Agent · Assignee: ada · Priority / estimate: None / 2 · Blocked by / blocks / related: parent: AST-1392; blocks: AST-1394_

#### What this implements

Own the workbench success path so any successful model body becomes text before RESPONSE write (JSON text for objects/lists, otherwise the raw text), using one stringify habit rather than a second store helper. Persist that text; with `debug=True` show found type/shape → recorded text; never let a non-string payload raise a storage type error as the Test outcome. Does **not** own React chrome or production `do_task` schema validation (see #2 and Boundaries).

#### Citations

`pattern.batch.entity-agent-responses`; `astral.standards.data-raises-caller-logs`; `astral.batch.entity-agent-responses-latest-only`; `astral.standards.debug-contract-gated`; `astral.standards.dry-and-focused-functions`; `astral.agent.do-task-delegation`.

#### Acceptance criteria

- [X] 1. An Agent Ad Hoc Test whose model returns a successful JSON envelope with an object payload (the `craft_company_search_terms` shape in the original brief) completes as success: the workbench shows the payload as JSON text, and no `_store_response_block failed` / `block_data must be a str` traceback appears for that run.
- [X] 2. Execution History inspection for that Test run includes a RESPONSE body equal to the text shown in the workbench (JSON text of the payload, not an empty or missing block).
- [X] 3. A successful reply that is already plain text still displays and stores as that text — no extra JSON wrapping.
- [X] 4. With `debug=True`, the serialized store is visible as found→recorded under Style D; with `debug=False`, this path adds no new debug lines.

#### Boundaries

- [X] Does **not** own React chrome, Admin Test HTTP display overlay, or production `do_task` schema validation / AST-1289 coerce. Sibling #2 owns showing the Test body without type invalidation. Does **not** relax `save_agent_data` to accept non-text `block_data`. Does **not** treat provider/API failures as success.

#### Notes for planning

Reuse the existing `do_task` habit of JSON-serializing object/list payloads before RESPONSE write. Data layer still raises on non-text; core serializes. Ad Hoc Test stays on the workbench wrapper, not routed through production `do_task` validation just to get a store.

#### QA test manifest

1. Existing string-payload ledger + store: `tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger`
2. Object/list/plain-text stringify + debug Style D: `tests/component/core/test_agent.py::TestAst1393SerializeAdhocSuccessBody`

**Broken / obsolete:** none.

**Integration:** none revised.

**Narrowed run:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger \
  tests/component/core/test_agent.py::TestAst1393SerializeAdhocSuccessBody \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum** (`origin/sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text`):

* `docs/test-bible/core/agent.md` `ef3348a750fe36f10629fa51b7b88f3510442bc4`

##### Comments


###### radia — 2026-08-16T01:50:20.466Z

[code-rubric] PROCEED (Commit: a45fff61) core stringify clean

###### betty — 2026-08-16T01:46:00.211Z

`origin/sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text` @ `a45fff61` · object payload stringify coverage

###### joan — 2026-08-16T01:33:02.943Z

[plan-rubric] PROCEED (Commit: 2a87dcd5) stringify before store

###### ada — 2026-08-16T01:29:58.092Z

`origin/sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text` @ `2a87dcd5` · stringify before store

---

#### Stages


##### Stage 1: Stringify workbench success body before RESPONSE write

**Done when:** `run_adhoc_workbench_test` on a successful result whose `parsed_response` is a JSON envelope with an object `agent_payload` (the `craft_company_search_terms` shape) passes a `str` into `_store_response_block` — compact JSON text of that payload, not a dict, not a Python `str(dict)` dump — and the Test still completes success (`dispatch_ledger` `COMPLETED`). A successful plain-text `parsed_response` is stored unchanged (no extra JSON wrapping). With `debug=True`, Style D shows found type/shape → recorded text for that serialize; with `debug=False`, this path adds no new debug-contract lines. `python3 -m py_compile src/core/agent.py` passes.

1. In `src/core/agent.py`, in `run_adhoc_workbench_test`, replace **only** the success-path body that currently reads:
```python
           parsed = result.get("parsed_response")
           if isinstance(parsed, dict) and "agent_payload" in parsed:
               response_text = parsed["agent_payload"] or ""
           else:
               response_text = str(parsed) if parsed is not None else ""
           try:
               _store_response_block(
                   entity_type,
                   workbench_task_key,
                   batch_id,
                   response_text,
                   index=entity_id,
                   debug=debug)
           except Exception:
               logger.debug("_store_response_block failed", exc_info=True)
```

   with this exact sequence (still inside the existing `else:` of `if not result.get("success"):`):
```python
           parsed = result.get("parsed_response")
           if isinstance(parsed, dict) and "agent_payload" in parsed:
               body = parsed["agent_payload"]
           else:
               body = parsed
           try:
               response_text = _caller_response_blob(body)
               if debug:
                   dbg = get_logger(__name__, debug_flag=True)
                   if isinstance(body, dict):
                       shape = f"keys={sorted(body.keys())}"
                   elif isinstance(body, list):
                       shape = f"len={len(body)}"
                   elif isinstance(body, str):
                       shape = f"len={len(body)}"
                   elif body is None:
                       shape = "none"
                   else:
                       shape = type(body).__name__
                   dbg.debug_index(
                       func="run_adhoc_workbench_test",
                       index=1,
                       total=1,
                       identifier=workbench_task_key,
                       outcome="serialized store",
                   )
                   dbg.debug_detail(
                       f"found type={type(body).__name__} shape={shape}"
                   )
                   dbg.debug_detail_block(response_text)
               _store_response_block(
                   entity_type,
                   workbench_task_key,
                   batch_id,
                   response_text,
                   index=entity_id,
                   debug=debug)
           except Exception:
               logger.debug("_store_response_block failed", exc_info=True)
```

   `get_logger` is already imported in this module. `_caller_response_blob` already lives in this file (`json.dumps(..., ensure_ascii=False, default=str)` for dict/list; `str(body)` for other non-`None`; `""` for `None`). Do **not** add a second stringify helper. Do **not** call `json.dumps` inline here.

2. Do **not** change the failure branch (`if not result.get("success"):`) — it already stores `_failure_response_block_data(...)` as text. Provider/API failures stay failed Tests.

3. Do **not** change `_store_response_block` to accept non-text. Do **not** change `save_agent_data`. Do **not** route Ad Hoc Test through production `do_task` validation to get a store. Do **not** change `do_task`'s own `store_content = json.dumps(parsed) if isinstance(parsed, (dict, list)) else (parsed or raw_text)` line.

4. Do **not** mutate `result["parsed_response"]`. Do **not** add a new key on `result`. `return result` at the end of the function stays as-is. Sibling #2 owns returning this text from `POST /api/admin/adhoc/test` and pretty-printing it in React.

5. Do **not** pretty-print the stored JSON (`indent=`). Compact JSON from `_caller_response_blob` is the stored RESPONSE body. Do **not** wrap an already-`str` body in extra JSON quotes.

6. Do **not** edit `tests/` or `docs/test-bible/**`. Existing component test `test_success_completes_ledger_and_stores_blocks` still sees `_store_response_block` arg `[3] == "ok"` for a string payload. Betty owns any new object-payload coverage.

⚠️ **Decision:** Reuse `_caller_response_blob` instead of a new workbench-only dumps helper or a second `_store_response_block` that accepts objects. That function is already the dict/list → JSON text / else `str` habit in this file (`astral.standards.dry-and-focused-functions`). Data still raises on non-text (`astral.standards.data-raises-caller-logs`).

⚠️ **Decision:** Keep extracting `agent_payload` when that key is present, then stringify **that** body — not the full `{agent_performance, agent_payload}` envelope. Parent: when a payload key is present, store that payload body. `do_task` dumps the full `parsed` envelope; workbench stays on the payload (existing extract, now JSON text). Empty dict/list become `"{}"` / `"[]"` (structured JSON text), not `""` from the old `or ""` falsy collapse.

⚠️ **Decision:** Do not change `do_task` store or Admin HTTP/React in this ticket. Production ingest and sibling #2 display are out of Boundaries. One stringify call site for the workbench success path is enough.

⚠️ **Decision:** Debug is Style D on `run_adhoc_workbench_test` (index `1/1`, identifier=`workbench_task_key`, outcome=`serialized store`), found type/shape on one `|` detail line, recorded text via `debug_detail_block` (truncation contract). Emit only when `debug=True`. Do not log the raw found object.

#### Estimate

Confirm Chuckles estimate: 2 — agree

#### Traceability

AC1 persist/no-traceback → S1 | AC2 RESPONSE body → S1 | AC3 plain text → S1 | AC4 debug found→recorded → S1
(AC1 workbench **display** / pretty-print → sibling #2, not this plan)

#### Joan validate

[plan-rubric]
**Rubric:** plan-rubric
revision: 1
**Ticket:** AST-1393
**Overall:** APPROVED
**Publish ref:** `sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text` @ `2a87dcd5`

#### Traceability

AC1 persist/no-traceback → S1 (workbench display → sibling #2) | AC2 RESPONSE body → S1 | AC3 plain text → S1 | AC4 debug found→recorded → S1

#### Findings


##### acceptable — epic split / AC1 display clause

- **Location:** Plan Boundaries + `## Traceability` note; child Description AC1
- **Finding:** Child AC1 quotes “workbench shows … as JSON text,” but this plan correctly limits scope to core stringify + store; Admin HTTP/React display is sibling #2. Boundaries and traceability call this out explicitly.
- **Recommendation:** No plan change required. UAT for #1 should verify RESPONSE persistence and absence of `_store_response_block failed` / `block_data must be a str`; workbench display parity lands with #2.

##### acceptable — Stage 1 done-when vs AC2 wording

- **Location:** Stage 1 “Done when”
- **Finding:** Done-when specifies `str` into `_store_response_block` and ledger `COMPLETED`; AC2’s “equal to text shown in the workbench” is only fully testable after #2. Store path implies AC2 for Execution History.
- **Recommendation:** Optional clarity only — Betty may assert RESPONSE row content in component tests when she adds object-payload coverage.

context_tokens≈11500

#### Review (build stub)

**Publish ref:** `origin/sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text`
**Tip (pre-review):** `7fed10d1`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `7fed10d1` | Workbench success body via `_caller_response_blob` before RESPONSE write; Style D found→recorded when `debug=True` |

#### Radia review

**Rubric:** code-rubric.v1
**Ticket:** AST-1393
**Publish ref:** `origin/sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text` @ `a45fff61`
**Overall:** CLEAN
**Diff baseline:** `origin/dev...origin/sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text` (4 files: `src/core/agent.py`, `tests/component/core/test_agent.py`, `docs/test-bible/core/agent.md`, `agent-ast-1392-ad-hoc-agent-is-failing.md#ast-1393--serialize-ad-hoc-success-body-to-text`)

#### Statutes checked

63 active statutes per `canon/statutes/README.md` § Harvested corpus (registry row count; README footer “65” appears stale vs table).

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no confidence/grade paths touched |
| `astral.agent.do-task-delegation` | scoped | not-applicable | workbench path only; `do_task` unchanged |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no schema/vector validation changes |
| `astral.batch.batch-id-first` | scoped | conforms | existing workbench `batch_id` flow preserved |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch-id format changes |
| `astral.batch.claim-process-release` | scoped | not-applicable | not dispatcher claim/release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | uses existing `_store_response_block` / agent_data path |
| `astral.config.config-source-of-truth` | scoped | not-applicable | no config edits |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no env/secrets |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifacts |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spikes |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch seed |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no `run_next` changes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single feature doc for AST-1393 |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Betty merge-tests only on test paths |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | product commit `7fed10d1` touches `src/` only; tests via `merge-tests(AST-1393)` |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | core-only product change |
| `astral.layers.import-direction` | scoped | conforms | no new imports; existing `get_logger` |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no scripts |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | no UI |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | RESPONSE store, not coat-check lazy fetch |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no consult/render |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no API surface |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no seed |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no seed/boot |
| `astral.seed.define-approved` | scoped | not-applicable | no seed |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no seed |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no seed |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | stringify in core before data; `save_agent_data` still text-only |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no DB/schema |
| `astral.standards.debug-contract-gated` | scoped | conforms | Style D gated on `debug=True`; `debug_index` / `debug_detail` / `debug_detail_block` |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | reuses `_caller_response_blob`, no second helper |
| `astral.standards.in-scope-only` | scoped | conforms | single call site; Admin HTTP/React / `do_task` untouched |
| `astral.standards.logging-via-utils` | scoped | conforms | `get_logger(__name__, debug_flag=True)` |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | applies to `src/**` only; product symbols unchanged |
| `astral.standards.no-cross-contamination` | scoped | conforms | no unrelated subsystem edits |
| `astral.standards.no-hardcoded-sets` | scoped | not-applicable | no hardcoded sets |
| `astral.standards.public-then-helpers` | scoped | not-applicable | no new public API surface |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils changes |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job states |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | no frontend |
| `astral.ui.naming-conventions` | scoped | not-applicable | no UI |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1393): origin/tests 4667aad` |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `docs` / `test` / `merge-tests` vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub branch off ftr epic topology |
| `orch.git.ftr-sub-topology` | universal | conforms | `sub/AST-1392/AST-1393-…` |
| `orch.git.merge-on-checkout` | universal | conforms | no checkout violations observed |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear commits |
| `orch.git.no-dev-agent-branches` | universal | conforms | publish ref on `sub/…` |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1392 worktree |
| `orch.git.three-permanent-branches` | universal | conforms | dev/tests/sub flow |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | no product-policy forks |
| `orch.pipeline.plan-is-bible` | universal | conforms | implementation matches Joan-approved Stage 1 |
| `orch.pipeline.project-scoped-queues` | universal | conforms | n/a to diff |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review gate satisfied |
| `orch.roles.archie-approves-statutes` | universal | conforms | n/a |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty landed tests + bible; engineer did not author test-tree in `code()` commit |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee Ada |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada still assignee at Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no ban evasion observed |

**C4 straggler:** Joan plan-rubric APPROVED attached; no `Excluded` statute list in artifact — nothing to straggle.

#### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | plan cites statutes (`dry-and-focused-functions`, `data-raises-caller-logs`), not `canon/patterns/**` catalog entries |

#### Plan adherence

Stage 1 implemented verbatim in `run_adhoc_workbench_test` success path (`src/core/agent.py` ~3548–3587): extract `agent_payload` when present → `_caller_response_blob(body)` → `_store_response_block` with `str`; Style D (`debug_index` 1/1, identifier=`workbench_task_key`, found type/shape, `debug_detail_block(response_text)`) only when `debug=True`; failure branch, `do_task`, Admin API/React, and data-layer contract unchanged. Empty `{}`/`[]` now persist as `"{}"`/`"[]"` per documented plan decision (not the old `or ""` collapse). Estimate **2** matches footprint. Sibling #2 boundary respected — no `api_admin` or frontend diffs.

Betty manifest (`TestAst515AdhocWorkbenchLedger`, `TestAst1393SerializeAdhocSuccessBody`) aligns with `docs/test-bible/core/agent.md` AST-1393 rows: object/list/str/plain-text/empty cases, debug Style D, `debug=False` quiet.

##### C6 judgment aids (§5a–§5g)

| Lens | Result |
|------|--------|
| Imports (B1) | OK — no new imports |
| Layer compliance (B2) | OK — core-only |
| Silent failure (D2) | Pre-existing `except Exception: logger.debug("_store_response_block failed")` retained per plan; see advisory |
| Fallbacks (D3) | OK — intentional `{}`/`[]` JSON text per plan decision |
| Logging (E1) / §5f debug | OK — gated Style D; no `[DEBUG]` hand-roll |
| Cross-ticket (§5d) | OK — sibling #2 scope not smuggled |
| §5g external | n/a — no `src/external/` diff |

#### Findings


##### advisory — broad `except` log label

- **Location:** `src/core/agent.py` `run_adhoc_workbench_test` success-path `try`/`except` (~3554–3587)
- **Finding:** The `try` now wraps `_caller_response_blob`, debug emission, and `_store_response_block`, but the `except` message remains `"_store_response_block failed"`. Serialize/debug failures would log under that label. Plan-mandated structure; `_caller_response_blob` is unlikely to raise on normal payloads.
- **Recommendation:** No fix-now. Optional follow-up (out of AST-1393 scope): widen message to `"adhoc success serialize/store failed"` if this path ever needs sharper ops signal.

##### advisory — store failure still yields COMPLETED ledger

- **Location:** same function, post-`except` ledger update (~3591–3601)
- **Finding:** Pre-existing: swallowed store exception does not flip ledger to FAILED. Not introduced by this ticket.
- **Recommendation:** Defer; not AST-1393 scope.

#### What's solid

- Root cause fix is minimal and at the right layer: stringify before the data contract, not weakening `save_agent_data`.
- Reuses `_caller_response_blob` — same JSON habit as elsewhere in `agent.py`.
- Betty tests cover the crash repro (object payload → compact JSON `str`), regression (string payload unchanged), and debug contract without log-string golden brittleness.
- Debug instrumentation matches AST-538 Style D: index 1/1, found→recorded, gated on `debug=True`.

#### Frame diff

(none) — diff matches Joan-approved plan Stage 1; no scope/frame drift.

#### Notes

- Joan plan-rubric: APPROVED @ `2a87dcd5`; no excluded-statute table in attachment.
- UAT note for Chuckles/Susan: AC1 “workbench shows JSON text” display parity is sibling #2; this ticket delivers store-side stringify + debug only.

context_tokens≈28000

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/agent.py` | Stringify workbench success body via `_caller_response_blob` | `7fed10d1f` |
| | _tests_ | — | 1 file(s) |

### AST-1394 — Show Ad Hoc Test body without type invalidation

_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1394/show-ad-hoc-test-body-without-type-invalidation-ad-hoc-agent-is · Status at archive: Archive · Project: Astral Agent · Assignee: katherine · Priority / estimate: None / 2 · Blocked by / blocks / related: parent: AST-1392_

#### What this implements

After #1, the Admin Test response returns that same text, and the workbench displays it (pretty-printed when it is JSON). A successful provider reply must never be replaced with a type or schema error overlay. Does **not** own persist, debug contract, or production ingest.

#### Citations

`pattern.ui.admin-endpoint`; `pattern.layers.import-discipline`; `astral.layers.import-direction`; `astral.standards.in-scope-only`.

#### Acceptance criteria

- [X] An Agent Ad Hoc Test whose model returns a successful JSON envelope with an object payload (the `craft_company_search_terms` shape in the original brief) completes as success: the workbench shows the payload as JSON text, and no `_store_response_block failed` / `block_data must be a str` traceback appears for that run.
- [X] A successful reply that is already plain text still displays and stores as that text — no extra JSON wrapping.
- [X] A provider/API failure still surfaces as a failed Test (error shown; no fake success body).

#### Boundaries

Does **not** own persist, debug contract, or production ingest (sibling #1). Does **not** change Preview, dispatch batch apply, or other Admin pages except Agent Ad Hoc Test display of the returned body. Does **not** invent a new envelope: when a payload key is present, display that payload body (JSON text if structured); when it is absent, display the raw reply text.

#### Notes for planning

After sibling #1. Thin Admin Test surface returns the serialized body; React renders it. UI does not call data.

#### QA test manifest

1. Existing string/numeric HTTP + 500: `tests/component/ui/api/test_api_admin.py::TestAdhocRoutes::test_adhoc_preview_and_test`
2. Object/list/plain stringify + failure envelope: `tests/component/ui/api/test_api_admin.py::TestAst1394AdhocTestResponseText`
3. Routed Agent Ad Hoc page (**§6c**) + object/plain/failure chrome: `tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx`

**Broken / obsolete:** none.

**Integration:** none revised.

**Narrowed run:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_admin.py::TestAdhocRoutes::test_adhoc_preview_and_test \
  tests/component/ui/api/test_api_admin.py::TestAst1394AdhocTestResponseText \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx
```

**Pass criterion:** pytest + Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasums** (`origin/sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation`):

* `docs/test-bible/ui/api/api_admin.md` `8749badfc3db0fa7fe3c8b2a98ce8edf179a2631`
* `docs/test-bible/frontend/pages.md` `947b561898651125cf3cfd397fa2a2ddb29d6839`

##### Comments


###### radia — 2026-08-16T02:18:41.661Z

[code-rubric] PROCEED (Commit: c4c22d2d) display overlay clean

###### betty — 2026-08-16T02:12:51.710Z

`origin/sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation` @ `c4c22d2d` · display without type invalidation

###### joan — 2026-08-16T02:02:14.697Z

[plan-rubric] PROCEED (Commit: eed6751e) display without invalidation

###### katherine — 2026-08-16T01:59:07.504Z

`origin/sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation` @ `eed6751e` · plan ready

---

#### Stages


##### Stage 1: Admin Test HTTP returns serialized body as text

**Done when:** `POST /api/admin/adhoc/test` on a successful workbench result whose `parsed_response` is a JSON envelope with an object `agent_payload` (the `craft_company_search_terms` shape) returns HTTP 200 `{"success": true, "response_text": <str>, ...}` where `response_text` is compact JSON text of that payload — the same string `_caller_response_blob` produces, not a nested JSON object, not a Python `str(dict)` dump. A successful plain-text `parsed_response` (or string `agent_payload`) is returned unchanged (no extra JSON wrapping). A numeric `parsed_response` such as `123` is still `"123"`. A provider/API failure (`success` false or raised exception) still returns HTTP 500 with `{"success": false, "error": ...}` — no fake success body. `python3 -m py_compile src/ui/api/api_admin.py` passes.

1. In `src/ui/api/api_admin.py`, add `_caller_response_blob` to the existing `src.core.agent` import (do **not** add a new import block, do **not** import from `src.data` for this ticket):
```python
   from src.core.agent import (
       run_adhoc_workbench_test,
       _decode_payload,
       resolved_agent_content,
       resolved_task_system,
       _chain_context,
       _caller_response_blob,
   )
```

2. In `adhoc_test`, after the existing `if not result.get("success"):` 500 return and **before** `timesheet = result.get("timesheet", {})`, replace **only** this success-body extraction:
```python
       response_text = result.get("parsed_response") or ""
       # For tasks with JSON envelope, do_task auto-extracts agent_payload into parsed_response.
       # If it's still a dict here (e.g. run_adhoc doesn't do the extraction), pull it out.
       if isinstance(response_text, dict) and "agent_payload" in response_text:
           response_text = response_text["agent_payload"] or ""
       if not isinstance(response_text, str):
           response_text = str(response_text)
```

   with this exact sequence:
```python
       parsed = result.get("parsed_response")
       if isinstance(parsed, dict) and "agent_payload" in parsed:
           body = parsed["agent_payload"]
       else:
           body = parsed
       response_text = _caller_response_blob(body)
```

   Leave the encoded `_decode_payload` block and the `return jsonify({"success": True, "response_text": response_text, "hydrated": hydrated, "timesheet": timesheet})` unchanged. `response_text` is always a `str` (compact JSON for dict/list via `_caller_response_blob`; otherwise `str(body)` or `""` for `None`). Flask therefore emits a JSON **string** field, not a nested object.

3. Do **not** pretty-print in the API (`indent=`). Compact JSON matches the RESPONSE text sibling #1 stored. React pretty-prints for display (Stage 2).

4. Do **not** use `parsed_response or ""` before the extract — an empty dict/list is falsy and would collapse to `""`. Empty dict/list become `"{}"` / `"[]"` (same as #1). Do **not** wrap an already-`str` body in extra JSON quotes.

5. Do **not** change the failure branches (`except Exception` → 500, `if not result.get("success")` → 500). Do **not** change `_resolve_adhoc`, Preview, `run_adhoc_workbench_test` arguments, `@require_admin`, or `hydrated`. Do **not** call `database` / `save_agent_data` from this route. Do **not** add schema validation on this overlay — a successful provider reply stays `success: True` even when the payload would fail production `do_task` ingest.

6. Do **not** edit `tests/` or `docs/test-bible/**`. Existing component cases that assert `response_text == "payload"` (string `agent_payload`) and `response_text == "123"` (numeric `parsed_response`) stay valid. Betty owns any new object-payload HTTP coverage.

⚠️ **Decision:** Import `_caller_response_blob` rather than a second `json.dumps` in `api_admin.py` or a new public helper in `agent.py`. The UI layer already imports private agent helpers (`_decode_payload`, `_chain_context`). One stringify habit means HTTP `response_text` equals the stored RESPONSE body (`astral.standards.dry-and-focused-functions`). UI still does not call data (`pattern.layers.import-discipline` / `astral.layers.import-direction`).

⚠️ **Decision:** Keep extracting `agent_payload` when that key is present, then stringify **that** body — not the full `{agent_performance, agent_payload}` envelope. Parent: when a payload key is present, display that payload body. Same extract as #1.

##### Stage 2: Workbench displays the body; success is never an ERROR overlay

**Done when:** On `POST /api/admin/adhoc/test` HTTP 200 with `success: true`, the Agent Ad Hoc **Response** `<pre>` shows the payload as text. When `response_text` is compact JSON (object payload from Stage 1), the existing `formatResponse` pretty-prints it (`JSON.stringify(..., null, 2)`). When `response_text` is already plain text, it displays unchanged. If `response_text` is a nested object/list (defense — Stage 1 should not emit this), it is coerced to JSON text and shown — React does **not** throw (`response.startsWith` / “Objects are not valid as a React child”) and does **not** replace it with `ERROR: …`. HTTP `!ok` / `success: false` still set `ERROR: …` (red overlay). Preview UI is unchanged.

1. In `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, immediately **above** the existing `formatResponse` helper, add this function (do **not** change `formatResponse` itself):
```tsx
     function responseBodyToText(body: unknown): string {
       if (typeof body === "string") return body
       if (body == null) return ""
       try { return JSON.stringify(body) } catch { return String(body) }
     }

     function formatResponse(text: string): string {
       try { return JSON.stringify(JSON.parse(text), null, 2) } catch { return text }
     }
```

   `JSON.stringify` without `indent` — compact text in state; `formatResponse` at render still pretty-prints JSON strings. `body == null` covers both `null` and `undefined`.

2. In `handleTest`, inside `.then(data => { ... })`, replace **only** the success assignment:
```tsx
           if (data.success) {
             setResponse(data.response_text)
             setTimesheet(data.timesheet || null)
           } else {
             setResponse(`ERROR: ${data.error || "Unknown error"}`)
           }
```

   with:
```tsx
           if (data.success) {
             setResponse(responseBodyToText(data.response_text))
             setTimesheet(data.timesheet || null)
           } else {
             setResponse(`ERROR: ${data.error || "Unknown error"}`)
           }
```

   Leave the `if (!r.ok)` throw, the `.catch(e => setResponse(\`ERROR: ${e.message}\`))`, `setTesting`, timesheet display, and the Response `<pre>` (including `response.startsWith("ERROR:")` color and `{formatResponse(response)}`) unchanged. `setResponse` always receives a `string` on the success path, so `startsWith` stays valid.

3. Do **not** set `ERROR:` when `data.success` is true, even if `response_text` is an object, list, number, or empty. Do **not** add schema / type validation in this page. Do **not** re-enable the commented hydrated-output section. Do **not** change Preview, Save As, prompt tabs, or other Admin pages. Do **not** add a display truncation / length cap on the Response `<pre>` (existing `maxHeight: 600` overflow stays).

4. Do **not** edit `tests/` or `docs/test-bible/**`. Existing frontend case that posts `response_text: "{\"ok\":true}"` and asserts pretty-printed `"ok": true` stays valid. Betty owns any new object-payload chrome coverage.

⚠️ **Decision:** Pretty-print in React, not in the API. HTTP `response_text` stays compact so it matches the stored RESPONSE; the workbench pretty-prints at render via the existing `formatResponse` (`pattern.ui.admin-endpoint`: API returns the resolved body; React renders it).

⚠️ **Decision:** Coerce-to-string on the success path even after Stage 1 always returns a `str`. That is the type-invalidation guard: a nested JSON object in `response_text` must still display as JSON text, never crash the page or become an `ERROR:` overlay. Failure overlays stay reserved for HTTP/`success: false`.

#### Estimate

Confirm Chuckles estimate: 2 — agree

#### Traceability

AC1 workbench shows JSON text / no type overlay → S1 + S2 | AC2 plain-text display → S1 + S2 | AC3 provider failure still failed Test → S1 (500) + S2 (`ERROR:`)
(AC persist / debug / production ingest → sibling #1, not this plan)

#### Joan validate

[plan-rubric]
**Rubric:** plan-rubric
revision: 1
**Ticket:** AST-1394
**Overall:** APPROVED
**Publish ref:** `sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation` @ `eed6751e`

#### Traceability

AC1 workbench shows JSON text / no type overlay → S1 + S2 (persist/traceback → sibling #1) | AC2 plain-text display → S1 + S2 (store → sibling #1) | AC3 provider failure still failed Test → S1 (500) + S2 (`ERROR:`)

#### Findings


##### acceptable — AC1 traceback / AC2 store clauses

- **Location:** Child Description AC1–AC2; plan `## Traceability` footer
- **Finding:** Ticket AC text still quotes persist/traceback language from the parent epic; this plan correctly limits scope to Admin HTTP + React display. Boundaries and traceability defer store/debug to AST-1393.
- **Recommendation:** No plan change. Full epic UAT needs #1 landed first for store/traceback; #2 UAT verifies `response_text` is always `str` and the Response `<pre>` never type-invalidates on `success: true`.

##### acceptable — duplicate extract+stringify in API

- **Location:** Stage 1; sibling #1 leaves `result["parsed_response"]` as the original envelope
- **Finding:** `agent_payload` extract mirrors core workbench logic because #1 does not expose serialized text on `result`. Importing `_caller_response_blob` keeps the stringify habit aligned with stored RESPONSE text.
- **Recommendation:** Acceptable given the sibling split. Optional future refactor (out of scope): core returns a dedicated `response_text` field — not required for this ticket.

context_tokens≈17500

#### Review (build stub)

**Publish ref:** `origin/sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation`
**Tip (pre-review):** `f685256e`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `e5d49eb9` | Admin Test HTTP `response_text` via `_caller_response_blob` (compact JSON text of payload) |
| 2 | `f685256e` | Workbench coerces success body to text before `setResponse`; existing `formatResponse` pretty-prints JSON |

#### Radia review — AST-1394

**Rubric:** code-rubric.v1
**Ticket:** AST-1394
**Publish ref:** `origin/sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation` @ `c4c22d2d`
**Overall:** CLEAN
**Diff baseline:** `origin/dev...origin/sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation` (11 files; includes stacked AST-1393 predecessor on this sub tip)

**AST-1394 product delta** (commits `e5d49eb9`, `f685256e`): `src/ui/api/api_admin.py`, `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` only — no `src/core/agent.py` edits in 1394 code commits (agent.py changes in the three-dot diff are AST-1393, already PROCEED @ `a45fff61`).

#### Statutes checked

63 active statutes per `canon/statutes/README.md` § Harvested corpus.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | no grade/confidence paths |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no `do_task` changes in 1394 delta |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no schema validation added |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch claim changes |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch-id format changes |
| `astral.batch.claim-process-release` | scoped | not-applicable | not dispatcher claim/release |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no agent_data write path in 1394 delta |
| `astral.config.config-source-of-truth` | scoped | not-applicable | no config edits |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no env/secrets |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifacts |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spikes |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch seed |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no `run_next` |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single AST-1394 feature doc |
| `astral.git.betty-no-src-or-features` | scoped | not-applicable | Betty merge-tests on test paths only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | engineer `code()` commits touch `src/ui/` only; tests via `merge-tests(AST-1394)` |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | UI overlay only; no external imports |
| `astral.layers.import-direction` | scoped | conforms | `ui → core` import of `_caller_response_blob` matches existing `_decode_payload` / `_chain_context` habit; plan-approved |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no scripts |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | no new hardcoded job/candidate state lists |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | display overlay, not coat-check |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no consult/render |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | conforms | `adhoc_test` retains `@require_admin` |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no seed |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no seed/boot |
| `astral.seed.define-approved` | scoped | not-applicable | no seed |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no seed |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no seed |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | route does not call `save_agent_data`; stringify before JSON response |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no DB/schema |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no new debug-contract emission in 1394 delta |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | reuses `_caller_response_blob`; no second `json.dumps` in API |
| `astral.standards.in-scope-only` | scoped | conforms | Admin Test HTTP + React chrome only; Preview/dispatch/other pages untouched |
| `astral.standards.logging-via-utils` | scoped | not-applicable | no new logging |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | applies to `src/**`; no new ticket-id symbols in product code |
| `astral.standards.no-cross-contamination` | scoped | conforms | scoped to Ad Hoc Test overlay |
| `astral.standards.no-hardcoded-sets` | scoped | not-applicable | no hardcoded sets |
| `astral.standards.public-then-helpers` | scoped | not-applicable | no file layout churn |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils changes |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state transitions |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job states |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run chain |
| `astral.ui.frontend-file-placement` | scoped | conforms | change in existing `AdminAnthropicAdHoc.tsx` |
| `astral.ui.naming-conventions` | scoped | conforms | `responseBodyToText` follows page conventions |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server config |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1394): origin/tests 322c490` |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `docs` / `test` / `merge-tests` |
| `orch.git.flow-direction-inviolable` | universal | conforms | sub off AST-1392 ftr |
| `orch.git.ftr-sub-topology` | universal | conforms | `sub/AST-1392/AST-1394-…` |
| `orch.git.merge-on-checkout` | universal | conforms | no violations observed |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear commits |
| `orch.git.no-dev-agent-branches` | universal | conforms | publish ref on `sub/…` |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1392 worktree |
| `orch.git.three-permanent-branches` | universal | conforms | dev/tests/sub flow |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | no product-policy forks |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 match Joan-approved plan |
| `orch.pipeline.project-scoped-queues` | universal | conforms | n/a to diff |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed gate satisfied |
| `orch.roles.archie-approves-statutes` | universal | conforms | n/a |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty tests + bible; engineer did not author test-tree in `code()` |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee Katherine |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Katherine still assignee |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no ban evasion |

**C4 straggler:** Joan plan-rubric APPROVED attached; no `Excluded` statute list — nothing to straggle.

#### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | plan references `pattern.layers.import-discipline` / `pattern.ui.admin-endpoint` in decisions; no `canon/patterns/**` catalog ids in Architectural definition |

#### Plan adherence

**Stage 1** (`api_admin.py` `adhoc_test` ~1474–1479): `agent_payload` extract → `_caller_response_blob(body)` → always-`str` `response_text`; failure branches, `_decode_payload` / `hydrated`, Preview, and `run_adhoc_workbench_test` args unchanged. Empty `{}`/`[]` → `"{}"`/`"[]"` (not falsy collapse). Regression cases `"payload"` / `"123"` preserved in existing `TestAdhocRoutes`.

**Stage 2** (`AdminAnthropicAdHoc.tsx`): `responseBodyToText` added above `formatResponse`; success path `setResponse(responseBodyToText(data.response_text))`; `formatResponse` + `ERROR:` overlay logic unchanged. Nested-object defense tested.

**Boundaries:** No `src/core/agent.py` persist/debug edits in 1394 code commits. No Preview, `do_task` coerce, or schema overlay on success. Estimate **2** matches footprint.

**Cross-ticket (AST-1393):** Duplicate extract+stringify in API is plan-documented and acceptable — HTTP `response_text` aligns with stored RESPONSE text when both use `_caller_response_blob` + same extract. Predecessor #1 on sub tip is expected for stacked epic work.

**Betty manifest** aligns with bible: `TestAst1394AdhocTestResponseText` + `TestAdhocRoutes` (API); `test_AdminAnthropicAdHoc.test.tsx` AST-1394 cases (object/plain/nested/ERROR).

##### C6 judgment aids (§5a–§5g)

| Lens | Result |
|------|--------|
| Imports (B1) | OK — one symbol added to existing `src.core.agent` import block |
| Layer compliance (B2) | OK — `ui → core`; no `ui → data` for stringify |
| Silent failure (D2) | OK — pre-existing `except` on encoded `_decode_payload` unchanged; no new swallows |
| Fallbacks (D3) | OK — intentional `{}`/`[]` JSON text; `responseBodyToText` null guard |
| Logging (E1) / §5f | n/a — no new debug emission |
| Config/state in UI (G1) | OK |
| Cross-ticket (§5d) | OK — #1 persist scope not re-smuggled; #2 display-only |
| §5g external | n/a |

#### Findings


##### advisory — duplicate stringify vs AST-1393 core path

- **Location:** `src/ui/api/api_admin.py` `adhoc_test` (~1474–1479); mirrors `run_adhoc_workbench_test` in AST-1393
- **Finding:** Extract + `_caller_response_blob` duplicated because #1 leaves `parsed_response` as the original envelope. Joan flagged acceptable; drift risk if one call site changes without the other.
- **Recommendation:** No fix-now. Optional future refactor (out of epic scope): core returns `response_text` on `result` for overlay consumption.

##### advisory — misleading Stage 2 commit message

- **Location:** git `f685256e` message says “workbench” / implies `agent.py`; diff is `AdminAnthropicAdHoc.tsx` only
- **Finding:** Commit archaeology only; code is correct.
- **Recommendation:** None for resolve-child.

##### advisory — `body` variable reuse in `adhoc_test`

- **Location:** `api_admin.py` ~1436 vs ~1476–1478
- **Finding:** Request `body` dict shadowed by payload `body` after success extract. Harmless — request fields already consumed.
- **Recommendation:** Optional rename to `payload_body` in a hygiene pass; not blocking.

#### What's solid

- Fixes the type-invalidation failure mode at both layers: API always emits `response_text` as `str`; React coerces nested objects before `setResponse`, so `response.startsWith("ERROR:")` stays safe.
- Pretty-print stays in React (`formatResponse`); API returns compact JSON matching stored RESPONSE text from #1.
- Betty tests cover object/list/empty/plain/numeric HTTP cases and frontend success/failure/nested-object defense without golden log strings.
- Engineer respected test-tree ownership and plan boundaries (UI-only product commits).

#### Frame diff

(none) — AST-1394 implementation matches Joan-approved Stages 1–2; no scope/frame drift.

#### Notes

- Three-dot diff vs `origin/dev` includes AST-1393 files (agent.py, AST-1393 tests/docs) because sub branch stacks on #1; Radia AST-1393 verdict was PROCEED — no regression observed in combined tip.
- Joan plan-rubric: APPROVED @ `eed6751e`; no excluded-statute table.
- Epic UAT: verify object-payload Test shows pretty-printed JSON in Response `<pre>`, no `ERROR:` on `success: true`, and provider failure still red `ERROR:` overlay.

context_tokens≈22000

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/ui/api/api_admin.py` | Import `_caller_response_blob`; stringify Ad Hoc Test succes | `e5d49eb97` |
| ✓ | `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | Coerce a success body to text before `setResponse`; keep exi | `f685256ea` |
| | _tests_ | — | 2 file(s) |
