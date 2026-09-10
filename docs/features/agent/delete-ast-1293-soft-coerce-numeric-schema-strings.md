<!-- linear-archive: AST-1293 archived 2026-08-19 -->

## Linear archive (AST-1293)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1293/soft-coerce-numeric-schema-strings-on-do-task-validate-handling  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1289 — Handling datatype issues in responses  
**Blocked by / blocks / related:** parent: AST-1289

### Description

## What this implements

Own the pre-validate soft-coerce so integer values on schema-string fields (including nested `jobs[].astral_job_id` slot echoes) become strings before type checks; keep schema declarations as string; leave claim/slot binding and non-string type rules alone. Observable outcome: Deepseek-style integer slot ids no longer sink an otherwise-valid batch envelope. Does **not** own prompt rewrites, scrape/bot handling, or per-field schema type flips.

## In scope

- [X] `astral.agent.do-task-delegation` — extend shared `do_task` pre-validate soft-coerce (`_coerce_schema_str_fields_from_list` in `src/core/agent.py`) for int→str + nested `items_schema`
- [X] `pattern.config.config-block` / `astral.config.config-source-of-truth` — leave `TASK_CONFIG` response_schema field types as `str` (no type flips)
- [X] `astral.standards.debug-contract-gated` — Style D found→recorded for int→str only when `debug=True`
- [X] `astral.standards.in-scope-only` / `astral.standards.dry-and-focused-functions` — one coerce family; no scrape/bot/prompt/claim-binding work

## Considered but excluded

* Prompt / catalog rewrites — out of Boundaries; identity still claim/slot binding after validate
* Scrape / bot-block / qualify state machines — datatype tolerance only (`src/core/agent.py` validate path)
* Per-field schema type flips to `int` in `src/utils/config.py` — config stays source of truth as `str`
* Zero-pad invention on coerce — plain `str(int)` only
* Soft-accept of `bool` / `dict` / `float` on schema-`str` fields — validator remains strict
* Parallel coerce helper — would duplicate schema walk; extend existing list→str helper instead

## Acceptance criteria

1. [x] A successful agent envelope whose `jobs[n].astral_job_id` is an integer batch-slot echo (e.g. `0`) validates and is available for downstream apply the same way an equivalent string slot echo already is — no `Field 'astral_job_id' must be str, got int` rejection for that case alone.
2. [x] A chunk that previously failed solely for integer slot ids (while sibling chunks with string ids succeeded) no longer fails on that type nit; other real schema failures still reject.
3. [x] Declared schema type for these fields remains string in config after the change.
4. [x] With `debug=True`, a coerced integer slot id is visible as found→recorded under Style D; with `debug=False`, this path adds no new debug lines.
5. [x] Boolean `true`/`false` and object values for string fields still fail validation (no accidental bool/dict soft-accept).

## Boundaries

Does not own prompt rewrites, scrape/bot handling, per-field schema type flips, claim-binding rule changes, or zero-pad invention. Single-child epic — no sibling slices.

## Notes for planning

Soft-coerce sits beside the existing pre-validate list→string habit on the shared `do_task` validation path. Extend that family for int→string (exclude bool).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1289-handling-datatype-issues-in-responses`, child `sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-09T18:03:30.689Z
[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1293
**Publish ref:** `sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings` @ `160a211b`
**Overall:** CLEAN

## Plan adherence
- Stage 1 matches plan: extend `_coerce_schema_str_fields_from_list` for int→str + nested `items_schema`; both `do_task` sites pass `debug=debug`.
- Self-Assessment Scope `Single-Component` matches footprint (`src/core/agent.py` + bible/tests); no config type flips or claim/slot binding changes.
- AC1–AC5 covered; bool/dict/float stay hard-fail via `type(val) is int`.

## Pattern conformance
| id | verdict | one-line |
|----|---------|----------|
| pattern.config.config-block | conforms | Left `TASK_CONFIG` schema types as `str`; no second source of truth |

## Frame diff
(none)

**What’s solid:** One soft-coerce family on the shared validate path; Style D found→recorded gated on `debug=True` (§5f); Joan plan-rubric APPROVED with no Excluded list (no C4 straggler). Full active set (64) scored in-session.

context_tokens≈48000
— Radia

#### betty — 2026-08-09T17:57:37.937Z
## QA test manifest

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

— Betty

#### joan — 2026-08-09T17:52:44.962Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1293
**Overall:** APPROVED
**Publish ref:** `sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings` @ `e1de3d52`

## Traceability
AC1→S1; AC2→S1; AC3→S1; AC4→S1; AC5→S1

Plan faithfully implements the child scope: extend `_coerce_schema_str_fields_from_list` on the shared `do_task` pre-validate path for int→str (with `type(val) is int` bool exclusion), recurse `items_schema` for nested `jobs[]`, pass `debug` to both call sites for Style D found→recorded, leave `TASK_CONFIG` types as `str`, and keep claim/slot binding untouched. Single-file `core` change respects layer/import rules; DRY extends existing walker rather than parallel helper.

context_tokens≈52000

— Joan

#### ada — 2026-08-09T17:48:02.176Z
Plan: [`docs/features/agent/ast-1293-soft-coerce-numeric-schema-strings.md`](https://github.com/susansomerset/astral/blob/sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings/docs/features/agent/ast-1293-soft-coerce-numeric-schema-strings.md) on `origin/sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings` @ `e1de3d52`.

**Self-assessment**
- **Scope:** Single-Component — extend `_coerce_schema_str_fields_from_list` + two `do_task` call sites in `src/core/agent.py` only.
- **Conf:** high — reuses the existing list→str pre-validate habit and Style D `_do_task_debug_logger`; int→str uses `type(val) is int` so bool stays hard-fail.
- **Risk:** Medium — sits on every json/python `do_task` validate; gate is narrow (schema `str` + exact `int`) so bool/dict/float still reject.

---

# Soft-coerce numeric schema strings on do_task validate

- **Linear:** [AST-1293](https://linear.app/astralcareermatch/issue/AST-1293/soft-coerce-numeric-schema-strings-on-do-task-validate-handling)
- **Parent:** [AST-1289](https://linear.app/astralcareermatch/issue/AST-1289/handling-datatype-issues-in-responses)
- **Publish ref:** `sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings`

Deepseek (and similar models) sometimes echo batch-slot indexes as bare integers (`0`, `1`) while `TASK_CONFIG` declares those fields as `str`. Today `_validate_schema_object_fields` rejects with `Field 'astral_job_id' must be str, got int` and the whole chunk dies. This ticket extends the existing pre-validate soft-coerce on the shared `do_task` path so integers on schema-`str` fields (including nested `jobs[].astral_job_id`) become strings before type checks, without flipping schema types or loosening bool/dict rejection.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Extend `_coerce_schema_str_fields_from_list` for int→str (+ nested `items_schema`); pass `debug` from both pre-validate call sites; Style D found→recorded when `debug=True` | core |

No `src/utils/config.py` edits — declared schema types stay `str`.

## Stages

### Stage 1: Extend pre-validate str soft-coerce (list + int, nested)

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

## Self-Assessment

**Scope:** `Single-Component` — one helper + two call-site kwargs in `src/core/agent.py` (core validation path); no config/UI/data changes.

**Conf:** `high` — the list→str pre-validate habit and Style D `_do_task_debug_logger` pattern already exist; int→str + nested walk is a direct extension with an explicit bool exclusion.

**Risk:** `Medium` — this sits on every json/python `do_task` validate; a bad coerce could stringify values that should fail, but the `type is int` gate and unchanged validator keep bool/dict/float hard-fail.

## Code-rules check

- §1.3 DRY: one walker extended; no parallel coerce module.
- §1.5.1 debug-contract-gated: int→str Style D only when `debug=True`; no new ungated debug lines.
- §2.1 / config-source-of-truth: schema types remain `str` in config; no type flips.
- §2.3 schema validation: type checks stay strict; soft-coerce is pre-validate only.
- §3.3 imports: no new imports required (`get_logger` / `_do_task_debug_logger` already in module).

## Review (build stub)

**Publish ref:** `origin/sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings`
**Tip (pre-review):** `080e1ca4`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `080e1ca4` | Extend `_coerce_schema_str_fields_from_list` for int→str + nested `items_schema`; pass `debug` at both `do_task` pre-validate sites; Style D when `debug=True` |

## Radia review — CLEAN

`[code-rubric] revision=2` · tip pre-docs `1cfe278a` · `origin/dev...origin/sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings`

**Overall:** CLEAN — full active statute set (64) scored in-session; no fix-now / discuss.

**What’s solid**
- Extends shared `_coerce_schema_str_fields_from_list` (int→str + `items_schema` recursion) without parallel walker or config type flips.
- `type(val) is int` keeps bool hard-fail; Style D found→recorded only when `debug=True`.
- Both `do_task` pre-validate call sites pass `debug=debug`; Betty coverage matches AC1–AC5.

**Pattern conformance:** `pattern.config.config-block` | conforms | TASK_CONFIG slot-id types left `str`.

**Notes:** Joan plan-rubric APPROVED (no Excluded list → no C4 straggler). §5f applied; §5g N/A.

## Resolution

**2026-08-09** — Radia `[code-rubric] revision=2` **CLEAN** (no fix-now / discuss / Frame diff). No product changes after review. Publish tip before resolve commit: `160a211b` (`docs(AST-1293): Radia review — clean`). Advancing to User Testing.
