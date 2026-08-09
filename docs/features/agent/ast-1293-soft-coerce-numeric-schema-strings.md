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
