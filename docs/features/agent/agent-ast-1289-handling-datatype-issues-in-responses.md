# AST-1289 — Handling datatype issues in responses

**Component:** agent  
**Children:** AST-1293  
**Linear archived:** AST-1289 2026-08-19; AST-1293 2026-08-19

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-09 10:47 | AST-1293 | docs | `e1de3d52b` | plan — soft-coerce numeric schema strings |
| 2026-08-09 10:54 | AST-1293 | docs | `140c017e8` | review stub after Stage 1 soft-coerce |
| 2026-08-09 10:54 | AST-1293 | code | `080e1ca4d` | soft-coerce int schema-str fields before validate |
| 2026-08-09 10:57 | AST-1293 | merge-tests | `1cfe278a0` | origin/tests a88fd54b48fc790463d8418df476221bfb9f6386 |
| 2026-08-09 10:57 | AST-1293 | test | `a88fd54b4` | soft-coerce int schema-str fields + Style D coverage |
| 2026-08-09 11:03 | AST-1293 | docs | `160a211ba` | Radia review — clean |
| 2026-08-09 11:04 | AST-1293 | resolve | `f5e3d2d06` | — clean |
| 2026-08-12 05:55 | AST-1289 | docs | `dc47a1475` | mirror epic registry Threads |
| 2026-08-19 12:50 | AST-1293 | docs | `2bf7d5df2` | archive Linear issue content |
| 2026-08-19 12:53 | AST-1289 | docs | `dd24a8ba5` | archive Linear issue content |

## Epic — AST-1289

_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1289/handling-datatype-issues-in-responses · Status at archive: Archive · Project: Astral Agent · Assignee: chuckles · Priority / estimate: Urgent / —_

### Purpose

LLM batch responses sometimes echo job-slot indexes as bare numbers (`0`, `1`, `2`) while the task schema expects strings (`"000"` / `"001"` / slot text). Today that type nit rejects an otherwise-good envelope and burns the whole chunk. This epic makes ingest a little liberal on that index datatype so valid job rows still land, without treating the failure as scrape or bot blocking.

### Functional scope

1. When a response field is declared as string in the task schema and the model returns a whole number (integer, not boolean), ingest coerces it to a string before schema validation so the field does not fail on type alone.
2. Nested job items are included — a numeric `astral_job_id` (batch-slot echo) must not fail the whole `jobs` list when the rest of the item is otherwise valid.
3. Coercion is stringification of the number only; it does not invent zero-padding. Existing claim/slot binding that already maps digit slot echoes to claimed job ids continues to own identity resolution after validation.
4. Task schema field types stay string for these index/id fields — we do not flip the declared type to integer to match the model habit.
5. When `debug=True` on the agent path that validates/coerces, each coercion shows what was found (raw type/value) and what was recorded (string form) under Style D index detail; when `debug=False`, no new debug noise from this path.

### Architectural definition

* **Patterns to reuse** — `pattern.config.config-block`: string vs number tolerance must not scatter magic type sets; declared response field types remain in `TASK_CONFIG` / task schema config. Soft-coerce stays beside the existing pre-validate list→string habit on the shared `do_task` validation path (`astral.agent.do-task-delegation`).
* **New patterns proposed** — none. This extends the existing pre-validate soft-coerce family (list→string already ships); int→string for schema `str` fields is the same shape, not a new catalog entry unless Archie later wants it named.
* **Applicable statutes** — universal active set; `astral.agent.do-task-delegation` (validation/coerce stays on the central agent response path); `astral.config.config-source-of-truth` (schema types remain config-owned); `astral.standards.in-scope-only` (no scrape/bot/qualify redesign); `astral.standards.debug-contract-gated` (Style D only when `debug=True`); `astral.standards.dry-and-focused-functions` (extend the existing coerce helper rather than a parallel validator).

### Boundaries

* Does **not** change scrape, bot-block, or qualify state machines — this is schema/type tolerance only.
* Does **not** accept dict/list/bool where the schema expects string (list→string remains the existing special case; dict stays hard-fail unless a separate schema ticket like AST-1144 flips the declared type).
* Does **not** rewrite claim-binding rules, zero-pad policy, or prompt catalogs except where a planner must document the coerce behavior for UAT.
* Does **not** loosen required-field presence, enums, grade/confidence bounds, or non-string schema types.
* Does **not** bury per-task schema flips for unrelated fields inside this epic.

### Acceptance criteria

1. A successful agent envelope whose `jobs[n].astral_job_id` is an integer batch-slot echo (e.g. `0`) validates and is available for downstream apply the same way an equivalent string slot echo already is — no `Field 'astral_job_id' must be str, got int` rejection for that case alone.
2. A chunk that previously failed solely for integer slot ids (while sibling chunks with string ids succeeded) no longer fails on that type nit; other real schema failures still reject.
3. Declared schema type for these fields remains string in config after the change.
4. With `debug=True`, a coerced integer slot id is visible as found→recorded under Style D; with `debug=False`, this path adds no new debug lines.
5. Boolean `true`/`false` and object values for string fields still fail validation (no accidental bool/dict soft-accept).

### Dependencies and blockers

none.

### Open questions

none.

### Proposed child tickets


##### 1: **Soft-coerce numeric schema strings on do_task validate - Ada**

Own the pre-validate soft-coerce so integer values on schema-string fields (including nested `jobs[].astral_job_id` slot echoes) become strings before type checks; keep schema declarations as string; leave claim/slot binding and non-string type rules alone. Observable outcome: Deepseek-style integer slot ids no longer sink an otherwise-valid batch envelope. Does **not** own prompt rewrites, scrape/bot handling, or per-field schema type flips.
**Citations:** `pattern.config.config-block`; `astral.agent.do-task-delegation`; `astral.config.config-source-of-truth`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`.

Monolith check: Functional scope has 5 capabilities and 1 child — intentional single vertical slice; coerce-before-validate must ship with unchanged string schema contract and existing slot-id binding so UAT can prove ingest without a half-applied pipeline.

---

### Original brief

I think we can be a little bit liberal about ingesting indexed job items that are numbers not strings, so we don't reject a whole response on the basis of the index's data type.
```
jobs[0]: Field 'astral_job_id' must be str, got int

Deepseek sometimes returned batch-slot ids as bare integers (0, 1, 2) instead of the zero-padded strings ("000", "001", "002"). Two chunks of 3 jobs each failed that way → 6 errors. The other chunks that returned string ids went through fine (METEORITE_QUALIFIED).

So: schema/type nit from the LLM response, not scraping/bot blocking.
```
```
  "agent_performance": {
    "status": "success"
  },
  "agent_payload": {
    "jobs": [
      {
        "astral_job_id": 0,
        "company_job_id": "9050070",
        "job_title": "Technical Business Analyst",
        "job_link": "https://www.dice.com/job-detail/c797094a-2fea-406c-8c58-ad2d19471685",
        "jd_text": "Job Summary:We are seeking an experienced Business Analyst to support ahigh-priority initiative to upgrade pharmacy claims processing systems from NCPDP Version D.0 to F6. The Business Analyst will partner with business stakeholders, pharmacy operations, compliance
```

#### Comments

_No comments._

---

### Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

#### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1289 (parent) | ftr/AST-1289-handling-datatype-issues-in-responses |
| AST-1293 | sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings |

**Epic worktree:** `astral-AST-1289/` — one active sub checked out at a time.

## Sub-issues

### AST-1293 — Soft-coerce numeric schema strings on do_task validate

_Archived: 2026-08-19 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1293/soft-coerce-numeric-schema-strings-on-do-task-validate-handling · Status at archive: Archive · Project: Astral Agent · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1289_

#### What this implements

Own the pre-validate soft-coerce so integer values on schema-string fields (including nested `jobs[].astral_job_id` slot echoes) become strings before type checks; keep schema declarations as string; leave claim/slot binding and non-string type rules alone. Observable outcome: Deepseek-style integer slot ids no longer sink an otherwise-valid batch envelope. Does **not** own prompt rewrites, scrape/bot handling, or per-field schema type flips.

#### In scope

- [X] `astral.agent.do-task-delegation` — extend shared `do_task` pre-validate soft-coerce (`_coerce_schema_str_fields_from_list` in `src/core/agent.py`) for int→str + nested `items_schema`
- [X] `pattern.config.config-block` / `astral.config.config-source-of-truth` — leave `TASK_CONFIG` response_schema field types as `str` (no type flips)
- [X] `astral.standards.debug-contract-gated` — Style D found→recorded for int→str only when `debug=True`
- [X] `astral.standards.in-scope-only` / `astral.standards.dry-and-focused-functions` — one coerce family; no scrape/bot/prompt/claim-binding work

#### Considered but excluded

* Prompt / catalog rewrites — out of Boundaries; identity still claim/slot binding after validate
* Scrape / bot-block / qualify state machines — datatype tolerance only (`src/core/agent.py` validate path)
* Per-field schema type flips to `int` in `src/utils/config.py` — config stays source of truth as `str`
* Zero-pad invention on coerce — plain `str(int)` only
* Soft-accept of `bool` / `dict` / `float` on schema-`str` fields — validator remains strict
* Parallel coerce helper — would duplicate schema walk; extend existing list→str helper instead

#### Acceptance criteria

1. [x] A successful agent envelope whose `jobs[n].astral_job_id` is an integer batch-slot echo (e.g. `0`) validates and is available for downstream apply the same way an equivalent string slot echo already is — no `Field 'astral_job_id' must be str, got int` rejection for that case alone.
2. [x] A chunk that previously failed solely for integer slot ids (while sibling chunks with string ids succeeded) no longer fails on that type nit; other real schema failures still reject.
3. [x] Declared schema type for these fields remains string in config after the change.
4. [x] With `debug=True`, a coerced integer slot id is visible as found→recorded under Style D; with `debug=False`, this path adds no new debug lines.
5. [x] Boolean `true`/`false` and object values for string fields still fail validation (no accidental bool/dict soft-accept).

#### Boundaries

Does not own prompt rewrites, scrape/bot handling, per-field schema type flips, claim-binding rule changes, or zero-pad invention. Single-child epic — no sibling slices.

#### Notes for planning

Soft-coerce sits beside the existing pre-validate list→string habit on the shared `do_task` validation path. Extend that family for int→string (exclude bool).

##### Comments


###### radia — 2026-08-09T18:03:30.689Z

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1293
**Publish ref:** `sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings` @ `160a211b`
**Overall:** CLEAN

#### Plan adherence

- Stage 1 matches plan: extend `_coerce_schema_str_fields_from_list` for int→str + nested `items_schema`; both `do_task` sites pass `debug=debug`.
- Self-Assessment Scope `Single-Component` matches footprint (`src/core/agent.py` + bible/tests); no config type flips or claim/slot binding changes.
- AC1–AC5 covered; bool/dict/float stay hard-fail via `type(val) is int`.

#### Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.config.config-block | conforms | Left `TASK_CONFIG` schema types as `str`; no second source of truth |

#### Frame diff

(none)

**What’s solid:** One soft-coerce family on the shared validate path; Style D found→recorded gated on `debug=True` (§5f); Joan plan-rubric APPROVED with no Excluded list (no C4 straggler). Full active set (64) scored in-session.

context_tokens≈48000

#### QA test manifest

**Publish:** `origin/sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings` @ `1cfe278a` (`merge-tests(AST-1293): origin/tests a88fd54b`)

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_agent.py::TestAst1293SoftCoerceNumericSchemaStrings tests/component/core/test_agent.py::TestResponseSchemaBranches::test_coerce_schema_str_list_to_newlines_before_validate -q`
   - Nested int `jobs[].astral_job_id` → `"0"` then validates
   - list→str regression
   - bool / dict / float still hard-fail
   - Style D found→recorded when `debug=True`; silent when `debug=False`
   - `TASK_CONFIG["qualify_meteorite"]` slot id type remains `str`

**Broken / obsolete:** none

**Integration:** none revised

**Bible shasum** (`origin/<publish-ref>`):
- `docs/test-bible/core/agent.md` `cb0021818d48158bb132ff7ac06a47af2b5f0f1f`

###### joan — 2026-08-09T17:52:44.962Z

[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1293
**Overall:** APPROVED
**Publish ref:** `sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings` @ `e1de3d52`

#### Traceability

AC1→S1; AC2→S1; AC3→S1; AC4→S1; AC5→S1

Plan faithfully implements the child scope: extend `_coerce_schema_str_fields_from_list` on the shared `do_task` pre-validate path for int→str (with `type(val) is int` bool exclusion), recurse `items_schema` for nested `jobs[]`, pass `debug` to both call sites for Style D found→recorded, leave `TASK_CONFIG` types as `str`, and keep claim/slot binding untouched. Single-file `core` change respects layer/import rules; DRY extends existing walker rather than parallel helper.

context_tokens≈52000

###### ada — 2026-08-09T17:48:02.176Z

Plan: [`agent-ast-1289-handling-datatype-issues-in-responses.md#ast-1293--soft-coerce-numeric-schema-strings-on-dotask-validate`](https://github.com/susansomerset/astral/blob/sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings/docs/features/agent/ast-1293-soft-coerce-numeric-schema-strings.md) on `origin/sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings` @ `e1de3d52`.

**Self-assessment**
- **Scope:** Single-Component — extend `_coerce_schema_str_fields_from_list` + two `do_task` call sites in `src/core/agent.py` only.
- **Conf:** high — reuses the existing list→str pre-validate habit and Style D `_do_task_debug_logger`; int→str uses `type(val) is int` so bool stays hard-fail.
- **Risk:** Medium — sits on every json/python `do_task` validate; gate is narrow (schema `str` + exact `int`) so bool/dict/float still reject.

---

#### Stages


##### Stage 1: Extend pre-validate str soft-coerce (list + int, nested)

**Done when:** Calling the coerce helper on a successful envelope whose `jobs[n].astral_job_id` is the integer `0` mutates that field to `"0"` in place; `_validate_response_schema` then returns `None` for an otherwise-valid payload. Bool / dict on a schema-`str` field still fail validation. With `debug=True`, a coerced int emits Style D found→recorded; with `debug=False`, no new debug-contract lines from this path.

1. In `src/core/agent.py`, keep the public call name `_coerce_schema_str_fields_from_list(parsed, schema, *, debug: bool = False)` (add the keyword-only `debug` arg; default `False` preserves existing callers/tests).

2. Keep resolving the walk root via `_inner_task_payload(parsed)` as today. If the payload is not a `dict`, return immediately (unchanged).

3. Replace the single-level loop body with a recursive walk over a field schema dict (start with the task `schema` on the inner payload). For each `field_name` / `field_spec` where `field_spec` is a `dict`:

   a. Read `type_spec = field_spec.get("type", "str")` and `val = obj.get(field_name)`.

   b. **Existing list→str (schema `str` only):** If `type_spec == "str"` and `isinstance(val, list)`, keep today's join behavior (`str(item).strip()` for non-empty items, `"\n".join(...)`, assign back onto `obj[field_name]`). Keep the existing `logger.info` when `log_batch_id.get()` is set — do not convert that path to Style D in this ticket.

   c. **New int→str (schema `str` only):** Else if `type_spec == "str"` and `type(val) is int` (use `type(val) is int`, **not** `isinstance(val, int)`, so `bool` is excluded), set `obj[field_name] = str(val)`. Do **not** coerce `float`, `bool`, `dict`, or non-list non-int types.

   d. **Nested list items:** If `type_spec == "list"` and `field_spec` has `items_schema` and `isinstance(val, list)`, for each index `idx` / `item` in `val`: when `item` is a `dict`, recurse with `items_schema` on that item (path prefix `f"{field_name}[{idx}]"` for debug). Non-dict items are left alone for the validator to reject.

   e. Do **not** recurse into `object`/`dict` field values beyond `items_schema` list items — matching `_validate_schema_object_fields` (payload fields + list `items_schema` only).

4. **Style D for int→str only** (statute `astral.standards.debug-contract-gated`): when `debug` is True **and** an int→str coercion runs, emit via `_do_task_debug_logger(True)`:

   - `debug_index(func="_coerce_schema_str_fields_from_list", index=<1-based coerce counter for this call>, total=<same counter after walk or emit after each with running index>, identifier=<field path e.g. `jobs[0].astral_job_id`>, outcome="coerced int→str")`
   - `debug_detail(f"found={raw!r} ({type(raw).__name__}) recorded={coerced!r}")`

   Practical shape: maintain a local list of coerce events during the walk, then emit one Style D pair per event with `index=i`, `total=len(events)`. If zero int coercions, emit **nothing**. When `debug` is False, skip all `debug_index` / `debug_detail` for this helper (no new ungated `logger.info` for int→str).

5. At both existing call sites in `do_task` (json/python pre-validate around the current `_coerce_schema_str_fields_from_list(parsed, schema)` and the post-rubric-decode twin), change to `_coerce_schema_str_fields_from_list(parsed, schema, debug=debug)` so the hop's `debug` flag gates Style D.

6. Do **not** edit `TASK_CONFIG` / any `response_schema` field types in `src/utils/config.py`. Do **not** change `_validate_schema_object_fields` type checks (bool/dict on `str` still hard-fail; coerce runs first so int never reaches that check on the happy path). Do **not** touch claim/slot binding, zero-pad policy, prompts, scrape, or bot handling.

⚠️ **Decision:** Extend `_coerce_schema_str_fields_from_list` in place (add int→str + `items_schema` recursion + `debug`) rather than a parallel helper. Parent architecture and `astral.standards.dry-and-focused-functions` require one soft-coerce family on the shared `do_task` path; a second walker would duplicate the schema walk and drift from list→str.

⚠️ **Decision:** Use `type(val) is int` (not `isinstance`) so Python's `bool` subclass of `int` cannot soft-accept. Matches the parent boundary and AC5.

⚠️ **Decision:** Coerce is plain `str(int)` with no zero-padding. Slot identity remains claim/binding's job after validation (parent Functional scope §3).

#### Self-Assessment

**Scope:** `Single-Component` — one helper + two call-site kwargs in `src/core/agent.py` (core validation path); no config/UI/data changes.

**Conf:** `high` — the list→str pre-validate habit and Style D `_do_task_debug_logger` pattern already exist; int→str + nested walk is a direct extension with an explicit bool exclusion.

**Risk:** `Medium` — this sits on every json/python `do_task` validate; a bad coerce could stringify values that should fail, but the `type is int` gate and unchanged validator keep bool/dict/float hard-fail.

#### Code-rules check

- §1.3 DRY: one walker extended; no parallel coerce module.
- §1.5.1 debug-contract-gated: int→str Style D only when `debug=True`; no new ungated debug lines.
- §2.1 / config-source-of-truth: schema types remain `str` in config; no type flips.
- §2.3 schema validation: type checks stay strict; soft-coerce is pre-validate only.
- §3.3 imports: no new imports required (`get_logger` / `_do_task_debug_logger` already in module).

#### Review (build stub)

**Publish ref:** `origin/sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings`
**Tip (pre-review):** `080e1ca4`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `080e1ca4` | Extend `_coerce_schema_str_fields_from_list` for int→str + nested `items_schema`; pass `debug` at both `do_task` pre-validate sites; Style D when `debug=True` |

#### Radia review — CLEAN

`[code-rubric] revision=2` · tip pre-docs `1cfe278a` · `origin/dev...origin/sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings`

**Overall:** CLEAN — full active statute set (64) scored in-session; no fix-now / discuss.

**What’s solid**
- Extends shared `_coerce_schema_str_fields_from_list` (int→str + `items_schema` recursion) without parallel walker or config type flips.
- `type(val) is int` keeps bool hard-fail; Style D found→recorded only when `debug=True`.
- Both `do_task` pre-validate call sites pass `debug=debug`; Betty coverage matches AC1–AC5.

**Pattern conformance:** `pattern.config.config-block` | conforms | TASK_CONFIG slot-id types left `str`.

**Notes:** Joan plan-rubric APPROVED (no Excluded list → no C4 straggler). §5f applied; §5g N/A.

#### Resolution

**2026-08-09** — Radia `[code-rubric] revision=2` **CLEAN** (no fix-now / discuss / Frame diff). No product changes after review. Publish tip before resolve commit: `160a211b` (`docs(AST-1293): Radia review — clean`). Advancing to User Testing.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/agent.py` | Extend `_coerce_schema_str_fields_from_list` for int→str (+  | `080e1ca4d` |
| | _tests_ | — | 1 file(s) |
