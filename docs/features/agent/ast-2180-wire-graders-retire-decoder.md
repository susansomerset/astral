# AST-2180 — Wire graders onto the structured path; retire the decoder

- **Linear:** [AST-2180](https://linear.app/astralcareermatch/issue/AST-2180) · parent [AST-2172](https://linear.app/astralcareermatch/issue/AST-2172) (Enforced structured output for rubric graders)
- **Publish ref:** `origin/sub/AST-2172/AST-2180-wire-graders-retire-decoder`
- **Assignee:** Ada
- **Canon Scope:** `patt.task.dispatch-retry`, `stat.agent.grade-vector-validation`, `stat.agent.confidence-bounds`, `stat.logging.warning`, `stat.logging.error`

This ticket puts every grader call onto the structured path. A grader is any task whose `ASTRAL_CONFIG["output_types"]` entry carries `structured_output: True` (11 task keys). For each grader call, `do_task` builds the forced tool from the call's rubric codes and row ids (AST-2178 `build_grade_tool_schema`) and sends it through `_send_to_server`, which hands it to the transport (AST-2179 `forced_tool`). The timestamp prefix drops the envelope sentence. The tool input is hydrated into the old decoded shape (AST-2178 `hydrate_grade_tool_input`), so scoring, grades_key persistence and retry routing downstream don't change. The AST-1839 agent-failure path and the AST-2089 salvage now read `agent_performance` from the tool input. Consult and roster route each per-entity light-check failure through the existing `_RETRY` sibling, with the hydrate's own reason (`patt.task.dispatch-retry`). The ad-hoc workbench test sends the same forced tool and hydrates the same way (`api_admin.adhoc_test`, moved here from AST-2181). Then the decoder and its string helpers are deleted: `_decode_payload`, `_GRADE_SEG`, `_grade_segment`, `_LINK_PREFIX_RE`, the strict encoded-batch helpers, consult's normalize cluster and the formatting coercion helpers. There are no live provider calls in build or verification (Susan, 2026-10-14). AC 8 is Susan's staging check after the epic lands.

## Findings that shape this plan

1. **This sub carries #2–#4.** It was synced with `--ftr AST-2172-structured-output-graders` @ `1b0b4dc7d`. `grade_schema.py` (AST-2178) is present, and so are `forced_tool` on `send_to_anthropic` / `send_to_llm_compat` and `getTimestampPrefix(structured=…)` (AST-2179). The bare `--ftr AST-2172` skips the parent merge.
2. **All 11 grader task keys reach `do_task` through call sites in this Scope.** consult: `render_verdict` (1538) and `_run_batch_consult` (1772), covering grade_do/get/like, the meteorite aliases, evaluate_jd/meteorite and qualify_job_listings. roster: prefilter single (1882), prefilter batch (2151), `_fetch_prefilter_notes` (3517), vet single (537) and vet batch (616). The `meteorite.py` `do_task` calls (`qualify_meteorite`, `stage_meteorite`, review-duplicate) are non-graders. So are the `vector_labels = {}` defaults in `_run_dispatch_chain_job_batch` and `run_cover_letter_artifact_chain_for_job`; they stay untouched.
3. **Codes and row ids come from ctx.** Every multi-vector call site already passes `vector_labels` (rubric order, one key per code) and `batch_entities` / `batch_index_map`. The exception is `_fetch_prefilter_notes`, which passes `_vector_labels_from_ctx(None)` and so gets `{}` (fixed in Stage 3). Vet grades its one configured vector, `INFLOW_CONFIG["vet"]["grade_vector_code"]` (`LT`).
4. **Vector reviews ride `agent_performance`.** Ten of the 11 graders are `is_vector_feedback_task`; vet is the exception. `RUBRIC_FEEDBACK_CONFIG["prompt_suffix"]` asks for `vector_reviews` inside `agent_performance`, and `_capture_rubric_vector_feedback` reads them from there (AST-724 / AST-860). AST-2178's `_AGENT_PERFORMANCE_SCHEMA` is closed (`status`, `failure_note`, `additionalProperties: false`), so an enforcing host would drop every review. See the Stage 1 decision.
5. **Vet never read `agent_performance.status`.** Today the AST-1839 agent-failure branch is gated on `rubric_encoded`, which needs `rubric_artifact`, and vet has none. That gate is kept as `task_config.get("rubric_artifact")`.
6. **Vet skipped the rubric branch and went through the generic JSON validation.** With a tool-input dict (`{"000": …, "agent_performance": …}`), that would fail validation against vet's `results[]` schema, so the generic branch skips every structured task.
7. **After Stage 1, consult's normalize cluster has no callers.** `_normalize_rubric_task_response` is called only from `agent.py` (salvage + decode), and both calls go in Stage 1. Every helper below it is reached only from it or from `_decode_payload` (checked with `rg` at plan time): `_should_decode_as_encoded_line`, `_ENCODED_LINE_RE`, `_parse_link_index_field`, `_apply_prefilter_encoded_link_meta`, `_extract_grade_letter`, `_extract_grade_confidence`, `_pascal_from_snake`, `_criterion_json_keys`, `_grade_letter_for_criterion`, `_coerce_link_list`, `_json_link_fields`, `_ensure_jobs_astral_ids`, `_ensure_companies_company_ids`, `_job_from_rubric_json` and `_job_from_letter_pipe`. The three `_bind_response_jobs_*` functions in the same region are still used by `_run_batch_consult` and stay.
8. **The vet single path sends the stored blurb unrenumbered.** `_discovery_blurb_line(hit, index=…)` stores the CSE hit's own index, but the schema keys the one row `000`. The batch path already renumbers (`_renumber_vet_blurb_line(b, i)`).
9. **AC 6's literal `rg` pattern also matches an unrelated line.** `duplicate vector code` matches `src/core/candidate.py:1633` (`"Rubric '{rk}' has duplicate vector codes: …"`, rubric-save validation, AST-1513). `candidate.py` is outside this Scope, and the line has nothing to do with the decoder. See § AC 6 note.
10. **Lint baseline** (`ruff check --select F,E9`, plan time): `agent.py` 4, `consult.py` 5, `roster.py` 10, `formatting.py` 1, `api_admin.py` 1. Each stage must not add a finding.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | `GRADE_TOOL_NAME`, `grade_call_codes`, `grade_forced_tool`; forced tool built before send in `do_task`; `structured` flag on `_assemble_blocks_seven_segment`; `forced_tool` on `_send_to_server`, `run_adhoc`, `run_adhoc_workbench_test`; grader response branch → hydrate (agent failure + salvage from the tool input); delete `_decode_payload`, `_GRADE_SEG`, `_valid_grade_letters`, `_grade_segment`, `_LINK_PREFIX_RE`, strict encoded-batch helpers, formatting coercion imports | core |
| `src/ui/api/api_admin.py` | `adhoc_test` only: forced tool from the candidate's rubric codes, hydrate via `grade_schema`; drop the `_decode_payload` import | ui |
| `src/core/consult.py` | Delete `_normalize_rubric_task_response` + its dead-only helpers (Finding 7); import only `do_task` from agent; reword three comments naming `_decode_payload` | core |
| `src/core/roster.py` | Vet single row id `000`; vet + prefilter (single and batch) route light-check failures with their reason; `_fetch_prefilter_notes` sends real codes | core |
| `src/utils/formatting.py` | Delete `_ENCODED_GRADE_LINE`, `clean_encoded_agent_payload`, `looks_like_encoded_grades_text`, `coerce_grades_encoded_json_parse` | utils |

No other file. `grade_schema.py`, `config.py`, `anthropic.py`, `llm_compat.py`, `llm_external.py`, `meteorite.py`, `candidate.py` and `database.py` are not touched. Nothing under `debug/` is committed.

**Python for checks:** `PY=/home/susan/astral/.venv/bin/python`. System `python3` lacks `asyncpg`/`nh3`, so the module imports in these checks fail under it. Run every command from the repo root.

## Stage 1: `agent.py` — build, send and hydrate the forced tool

**Done when:** the step 10 one-liner prints `stage1 ok`. `rg -n '_normalize_rubric_task_response|coerce_grades_encoded_json_parse\(|_strict_encoded_batch_consult_envelope_err\(|rubric_encoded|envelope_err' src/core/agent.py` prints nothing; the function *definitions* of the strict helpers remain until Stage 4. `ruff check --select F,E9 src/core/agent.py` shows no finding beyond the plan-time 4.

1. **Import.** Directly after `from src.core.timesheets import record_timesheet_entry`, add:
   ```python
   from src.core.grade_schema import build_grade_tool_schema, grade_row_ids, hydrate_grade_tool_input
   ```
   In the `from src.utils.formatting import (…)` block, delete `coerce_grades_encoded_json_parse,`. Its only call goes in step 6, and leaving the import would add a ruff F401 finding.
2. **Helpers.** Directly above `async def _send_to_server(`, add the content of **Appendix A** verbatim. It ends with two blank lines before `async def _send_to_server(`.
3. **`_assemble_blocks_seven_segment`.** After the parameter `candidate_id: Optional[str] = None,`, add `structured: bool = False,`. In the docstring, after the first sentence, add the line `structured=True: grader call — timestamp prefix without the envelope sentence (AST-2172).` Change `full_user = getTimestampPrefix() + user_content` to `full_user = getTimestampPrefix(structured=structured) + user_content`.
4. **`_send_to_server`.** After `batch_size: int = 1,`, add `forced_tool: Optional[Dict[str, Any]] = None,`. In the `common = dict(…)` call, after `record_timesheet=record_timesheet_entry,`, add `forced_tool=forced_tool,`. Both clients take the keyword (AST-2179).
5. **`do_task`, before send.** Directly after the empty-tokens `return _with_harvest({… "timesheet": {},\n        })` block and before `context = _build_context(task_key, task_config, index)`, insert:
   ```python
       # AST-2172: grader calls carry a forced tool built from this call's rubric codes and row ids.
       try:
           forced_tool = grade_forced_tool(task_key, ctx)
       except ValueError as exc:
           # No rubric codes → no schema; a grader call never goes out without one (we control the rubric data).
           logger.error(
               "%s | %s skipped — %s\n  This call is not going out",
               index or candidate_id or "-",
               task_key,
               exc,
           )
           return _with_harvest({
               "success": False,
               "error": str(exc),
               "api_response": None,
               "parsed_response": None,
               "timesheet": {},
           })
       structured = forced_tool is not None
   ```
   In the `_assemble_blocks_seven_segment(` call of `do_task`, add `structured=structured,` after `candidate_id=candidate_id,`. In the `_send_to_server(` call of `do_task`, add `forced_tool=forced_tool,` after `batch_size=batch_size,`.

   ⚠️ **Decision (no-codes call):** a grader with no rubric codes fails the hop before anything is sent: one ERROR, the same severity and shape as the AST-2000 empty-tokens skip. The consult and roster callers already route `success: False` per entity through `_RETRY`, then the error state (`patt.task.dispatch-retry`, "every other failed attempt"). This can only happen when a candidate has no rubric for the task. It is placed before the hop ledger opens, so there is no ledger to close.
6. **`do_task`, parse setup.** Replace this block, from `parsed = result.get("parsed_response")` through the second `envelope_err = _strict_encoded_batch_consult_envelope_err(task_key, parsed)`:
   ```python
       parsed = result.get("parsed_response")
       output_type = task_config.get("output_type", "")
       rubric_encoded = "_encoded" in output_type and bool(task_config.get("rubric_artifact"))
       strict_batch = _is_strict_encoded_batch_consult(task_key)
       …
       if strict_batch and not envelope_err:
           envelope_err = _strict_encoded_batch_consult_envelope_err(task_key, parsed)
   ```
   with:
   ```python
       parsed = result.get("parsed_response")
       output_type = task_config.get("output_type", "")
   ```
   Then delete the whole `if envelope_err:` block (from `if envelope_err:` through its `"timesheet": result.get("timesheet", {})})`). The vector-feedback normalize and `envelope_snapshot` lines between the two stay as they are.
7. **Generic JSON branch.** Change `if parsed is not None and response_format in ("json", "python") and not rubric_encoded:` to `if parsed is not None and response_format in ("json", "python") and not structured:` (Finding 6).
8. **`agent_payload` unwrap.** Change `if isinstance(parsed, dict) and "agent_payload" in parsed:` to `if not structured and isinstance(parsed, dict) and "agent_payload" in parsed:`. Inside that block, delete the AST-1839 sub-block: from the comment `# AST-1839: rubric-encoded tasks skip _validate_response_schema, so the envelope status is` through its `"salvaged_response": salvaged, "timesheet": result.get("timesheet", {})})`. It moves to step 9. The `# AST-1072` conversational lines, the unwrap and the list join stay.
9. **Grader branch.** Replace everything from the line `output_type = task_config.get("output_type", "")` that follows the unwrap block (the second assignment in `do_task`) through the `return _with_harvest({…})` that ends the `elif "_encoded" in output_type and isinstance(parsed, str):` branch with the content of **Appendix B** verbatim. The `if post_rubric_decode:` block that follows stays unchanged and still validates the hydrated shape.
10. **`run_adhoc_workbench_test` / `run_adhoc`.** In both signatures, after `debug: bool = False,`, add `forced_tool: Optional[Dict[str, Any]] = None,`. In `run_adhoc_workbench_test`, pass `forced_tool=forced_tool,` to `run_adhoc(` after `debug=debug,`. In `run_adhoc`, add `structured=forced_tool is not None,` to its `_assemble_blocks_seven_segment(` call after `candidate_id=candidate_id,`, and add `forced_tool=forced_tool,` to its `_send_to_server(` call after `no_cache_live_tokens=no_cache_live_tokens,`. Add to `run_adhoc`'s docstring: `forced_tool ({name, input_schema}) → grader test, same tool as do_task (AST-2172).`
11. Check (no network):
    ```bash
    $PY -m py_compile src/core/agent.py && $PY -c "
    from src.core import grade_schema as G
    from src.core.agent import grade_forced_tool as f, grade_call_codes as c, GRADE_TOOL_NAME as N
    ctx = {'batch_entities': [{'astral_job_id': 'a'}, {'astral_job_id': 'b'}], 'vector_labels': {'CL': 'Clarity', 'RE': 'Remote'}}
    t = f('grade_do', ctx); s = t['input_schema']
    assert t['name'] == N == 'submit_grades' and s['required'] == ['000', '001', 'agent_performance'], s['required']
    assert s['properties']['000']['required'] == ['CL', 'RE', 'notes'] and c('grade_do', ctx) == ['CL', 'RE']
    ap = s['properties']['agent_performance']
    assert ap['required'] == ['status', 'failure_note', 'vector_reviews'] and ap['additionalProperties'] is False
    assert G._AGENT_PERFORMANCE_SCHEMA['required'] == ['status', 'failure_note']   # shared constant not mutated
    v = f('vet_inflow_discovery', {'batch_entities': [{'company_id': 'x'}]})['input_schema']
    assert v['properties']['000']['required'][0] == 'LT' and 'vector_reviews' not in v['properties']['agent_performance']['properties']
    assert f('preamble_validate_response', {}) is None
    try:
        f('evaluate_jd', {'batch_entities': [{'astral_job_id': 'a'}]}); raise SystemExit('no-codes FAIL')
    except ValueError:
        pass
    print('stage1 ok')"
    ruff check --select F,E9 src/core/agent.py
    ```
12. Commit `code(AST-2180): agent — forced tool on grader calls, hydrate replaces coerce/strict-envelope/decode`, then publish.

⚠️ **Decision (vector reviews in the tool schema, Finding 4):** `grade_forced_tool` adds `vector_reviews` (required-but-nullable array of strings) to the call's `agent_performance` object for vector-feedback tasks. It copies the object, so AST-2178's shared constant is never mutated. Without this, every enforcing host strips the reviews and AST-860 capture silently stops for 10 of the 11 graders. Capture is lenient and never fails a run, so nothing would show the loss. It lives at the call site because `grade_schema.py` (AST-2178) is outside this Scope. If Joan or Susan would rather `grade_schema.py` own it, it's a 3-line move there in a follow-up, and this block would go.

⚠️ **Decision (agent-failure gate):** the AST-1839 branch stays gated on `task_config.get("rubric_artifact")`, today's `rubric_encoded` minus the output-type string test (Finding 5). Vet keeps ignoring `status`, as it does today.

⚠️ **Decision (tool name):** `GRADE_TOOL_NAME = "submit_grades"` (the parent brief's name) is a public module constant in `agent.py`. The tool name belongs to the caller (AST-2179 plan), and `api_admin` builds through `grade_forced_tool`, so no other module spells it.

## Stage 2: `api_admin.adhoc_test` — same tool, same hydrate

**Done when:** `$PY -c "import src.ui.api.api_admin"` exits 0, `rg -n '_decode_payload' src/ui` prints nothing, and `ruff check --select F,E9 src/ui/api/api_admin.py` shows no finding beyond the plan-time 1.

1. Change `from src.core.consult import list_timesheets` to `from src.core.consult import _rubric_criteria_for_cfg, _vector_labels_map, list_timesheets`.
2. In the comment above `from src.core.agent import (`, replace `` `_decode_payload` `` with `` grader forced-tool helpers ``. In that import list, replace the line `    _decode_payload,` with the two lines `    grade_call_codes,` and `    grade_forced_tool,`. Directly after the closing `)` of that import, add `from src.core.grade_schema import hydrate_grade_tool_input`.
3. In `adhoc_test`, directly after `task_response_format = task_cfg.get("response_format") or "text"`, insert:
   ```python
       # AST-2172: a grader test sends the forced tool do_task would, from this candidate's rubric codes.
       ids = entity_ids if entity_ids else ([entity_id] if entity_id else [])
       id_key = "company_id" if task_cfg.get("entity_type") == "company" else "astral_job_id"
       grade_ctx = {
           "batch_entities": [{id_key: eid} for eid in ids],
           "vector_labels": _vector_labels_map(_rubric_criteria_for_cfg(resolved["candidate_id"], task_cfg)),
       }
       try:
           forced_tool = grade_forced_tool(task_key, grade_ctx)
       except ValueError as e:
           return jsonify({"success": False, "error": str(e)}), 400
   ```
   In the `run_adhoc_workbench_test(` call, add `forced_tool=forced_tool,` after `debug=ui_llm_debug(),`.
4. Replace this block:
   ```python
       # Decode encoded payload if the task uses a compact encoded output_type
       hydrated = None
       output_type = TASK_CONFIG.get(task_key, {}).get("output_type", "")
       if "_encoded" in output_type and response_text:
           try:
               ids = entity_ids if entity_ids else ([entity_id] if entity_id else [])
               batch_entities = [{"astral_job_id": jid} for jid in ids]
               hydrated = _decode_payload(task_key, output_type, response_text, {"batch_entities": batch_entities})
           except Exception as e:
               hydrated = {"error": str(e)}
   ```
   with:
   ```python
       # Grader reply: hydrate the tool input exactly as do_task does (AST-2172).
       hydrated = None
       if forced_tool and isinstance(parsed, dict):
           try:
               hydrated = hydrate_grade_tool_input(
                   task_key, task_cfg["output_type"], parsed, grade_call_codes(task_key, grade_ctx), grade_ctx,
               )
           except Exception as e:
               hydrated = {"error": str(e)}
   ```
5. Run the Done-when checks, then commit `code(AST-2180): api_admin adhoc_test — forced tool + grade_schema hydrate, drop _decode_payload` and publish.

⚠️ **Decision (ad-hoc entity ids):** company tasks (prefilter, vet) get `company_id` entities. The hydrate keys company rows by `company_id`, and the old `{"astral_job_id": …}` stub would raise `KeyError` there. A grader ad-hoc test with no candidate rubric returns 400 with the hydrate module's own message. Ad-hoc rows are positional `000…`, matching `_build_adhoc_live_content`'s order, which is the same `ids` list the old decode used.

## Stage 3: consult + roster — real codes, per-entity reasons, normalize retired

**Done when:** `$PY -c "import src.core.consult, src.core.roster"` exits 0. `rg -n '_normalize_rubric_task_response|_should_decode_as_encoded_line|_apply_prefilter_encoded_link_meta|_job_from_letter_pipe|_job_from_rubric_json|_decode_payload|_grade_segment|_LINK_PREFIX_RE' src/core/consult.py src/core/roster.py` prints nothing. `ruff check --select F,E9` on both files shows no finding beyond the plan-time 5 / 10.

**consult.py**

1. Change `from src.core.agent import _LINK_PREFIX_RE, _grade_segment, do_task` to `from src.core.agent import do_task`.
2. Delete from the line `# AST-603: shared rubric response normalization (prefilter + future consult reuse).` through the end of `_ensure_companies_company_ids` (its last line is `            company["company_id"] = batch_entities[i].get("company_id")`). Leave two blank lines between `_hydrate_response_jobs_grade_reasons` and `def _bind_response_jobs_to_claimed(`.
3. Delete from `def _job_from_rubric_json(` through the line `    raise ValueError(f"[{task_key}] unrecognised rubric response shape: {type(parsed).__name__}")`, which ends `_normalize_rubric_task_response`. Leave two blank lines between `_bind_unmatched_empty_link_jobs_by_order` and `def _effective_no_signal_for_score(`.
4. In `_run_batch_consult`:
   - `# Build code→label map from candidate's rubric so _decode_payload can hydrate vector names` becomes `# Build code→label map from candidate's rubric: its codes build the grader tool schema and label the hydrated grades`.
   - `# batch_entities + vector_labels passed so do_task/_decode_payload can map pos→id and code→label` becomes `# batch_entities + vector_labels let do_task build schema rows/codes and map row id→entity, code→label (AST-2172)`.

   In `qualify_job_listings`'s `assemble`, `# so the agent can't echo it back; position mapping is handled in _decode_payload.` becomes `# so the agent can't echo it back; row ids map back to entities in grade_schema's hydrate.`
5. Lint rule: if `ruff check --select F401 src/core/consult.py` now reports an unused import it didn't report before step 2, delete exactly that imported name. Delete nothing else.

**roster.py**

6. `vet_inflow_discovery_company` (single):
   - `live_content = f"Discovery hit (index|title|url|snippet)\n{blurb}"` becomes `live_content = f"Discovery hit (index|title|url|snippet)\n{_renumber_vet_blurb_line(blurb, 0)}"`, with the comment `# Row id 000 — the tool schema keys this call's one hit as 000 (AST-2172).` on the line above.
   - Replace
     ```python
         if not row:
             _warn_company(short_name, "-", "missing results")
             logger.debug("Response from vet parse: missing results list")
             return {"success": False, "state": None, "error": "missing results"}
     ```
     with
     ```python
         if not row:
             # A light-check failure names its own reason (AST-2172); otherwise the hit is simply absent.
             fails = parsed.get("decode_failures") or []
             why = (fails[0].get("reason") if fails and isinstance(fails[0], dict) else None) or "missing results"
             _warn_company(short_name, "-", why)
             logger.debug("Response from vet parse: missing results list")
             return {"success": False, "state": None, "error": why}
     ```
7. `vet_inflow_discovery_company_batch`: directly before `passed = failed = errors = 0`, add
   ```python
       # Light-check failures name their own reason (AST-2172); still one warning per hit below.
       fail_by_hit = {
           f.get("hit_index"): f.get("reason") for f in (parsed.get("decode_failures") or []) if isinstance(f, dict)
       }
   ```
   and change `_warn_company(short_name, "-", f"missing results row hit_index={i}")` to `_warn_company(short_name, "-", fail_by_hit.get(i) or f"missing results row hit_index={i}")`. Counting and state handling are unchanged.
8. `prefilter_company` (single): directly before the `try:` that calls `flat = _flatten_prefilter_parsed(parsed)`, insert
   ```python
           fails = parsed.get("decode_failures") if isinstance(parsed, dict) else None
           if fails and not parsed.get("companies"):
               # Light-check failure (AST-2172): same retry route as a bad shape, with the hydrate's reason.
               return _prefilter_fail(short_name, cfg, result, f"decode: {fails[0].get('reason')}")
   ```
   `_prefilter_fail` with no `api_result` is retryable. That's the same route the `_flatten_prefilter_parsed` `ValueError` takes today for an empty `companies` list, so only the logged reason changes.
9. `_run_batch_company_prefilter`: directly after `fabricated = received_ids - sent_ids`, insert
   ```python
       # Per-company light-check failures (AST-2172) retry with their own reason, not as omitted.
       decode_failed = {
           f["company_id"]: f["reason"]
           for f in (parsed.get("decode_failures") or [])
           if f.get("company_id") in input_by_id and f["company_id"] not in received_ids
       }
       missing -= decode_failed.keys()
   ```
   and directly after `retried = 0`, insert
   ```python
       for cid, why in decode_failed.items():
           retried += _transition_prefilter_batch_failures(
               [input_by_id[cid]], cfg, debug=debug, fail_class="decode", reason=why,
           )
   ```
   This mirrors consult's `decode_failed` handling in `_run_batch_consult`: one `who -> dest [why]` warning per company (`stat.logging.warning`) and the same `_RETRY`-then-error routing as an omitted id (`patt.task.dispatch-retry`).
10. `_fetch_prefilter_notes`: change `"vector_labels": _vector_labels_from_ctx(None),` to `"vector_labels": _vector_labels_from_ctx({"astral_candidate_id": candidate_id}),`, with the comment `# Real rubric codes — a grader call never goes out without them (AST-2172).` on the line above. `candidate_id` is the `_company_candidate_id(company)` value assigned before the `try:`.
11. Run the Done-when checks, then commit `code(AST-2180): consult/roster — grader ctx codes + per-entity light-check reasons; retire normalize` and publish.

⚠️ **Decision (delete the normalize cluster — Joan weighs at validate):** Scope says "compact-line branches removed from normalize/routing". After Stage 1, though, `_normalize_rubric_task_response` has no callers at all (Finding 7). Its remaining branches handle free-JSON and letter-pipe shapes that a forced tool makes impossible. This plan deletes the function and the 15 helpers reachable only from it, rather than keep a callerless function minus one branch. **Alternative if struck:** keep `_normalize_rubric_task_response` and delete only its compact-line branch (the `_ENCODED_LINE_RE` / `_should_decode_as_encoded_line` / `_decode_payload` block), the AST-2126 `grades_encoded_notes` no-segment branch (needed for AC 7), `_ENCODED_LINE_RE`, `_should_decode_as_encoded_line` and `_apply_prefilter_encoded_link_meta`. Betty owns the test churn either way.

⚠️ **Decision (vet single row id, Finding 8):** renumbering the one blurb to `000` makes the prompt match the schema row the host enforces. Today a stored hit index other than 0 made `_decode_payload` drop the line as out of range, so this also closes that path.

⚠️ **Decision (`_fetch_prefilter_notes`):** only the codes change. Its ctx still carries no candidate API key, so `do_task` returns its missing-key result before anything is built or sent, exactly as today. Making that coat-check path actually call the provider is a separate behaviour change and isn't planned here.

## Stage 4: delete the decoder and string helpers

**Done when:**
- `rg -n '_decode_payload|coerce_grades_encoded_json_parse|clean_encoded_agent_payload|_ENCODED_GRADE_SET_COMPLETENESS|duplicate vector code|unexpected trailing content' src` prints exactly one line, `src/core/candidate.py:1633` (§ AC 6 note).
- `rg -n '"grades_encoded' src/core src/external src/ui/api` prints nothing (AC 7).
- `rg -n '_GRADE_SEG|_grade_segment|_LINK_PREFIX_RE|_STRICT_ENCODED_BATCH_CONSULT_KEYS|_is_strict_encoded_batch_consult|looks_like_encoded_grades_text|_ENCODED_GRADE_LINE' src` prints only the four out-of-scope comments (`candidate.py` 1436 / 1477 / 1617, `database.py` 6074).
- `$PY -c "import src.core.agent, src.core.consult, src.core.roster, src.ui.api.api_admin, src.utils.formatting"` exits 0, and ruff shows no finding beyond the plan-time counts.

1. `agent.py`: in the `from src.utils.formatting import (…)` block, delete `clean_encoded_agent_payload,` (`coerce_grades_encoded_json_parse` went in Stage 1), keeping `hydrate_entity_labels` and `split_entity_segments`.
2. `agent.py`: delete from the comment `# Batch encoded consult dispatch: models must return the usual JSON envelope, not bare compact lines (AST-501 / AST-503).` through the end of `_strict_encoded_batch_consult_envelope_err` (its last line is `    return None`, directly before the `# ----` section rule).
3. `agent.py`: change the section header line `# _decode_payload — compact encoded payload → response_schema shape` to `# Grade confidence validation on decoded payload shapes`. Below the header, delete from `# Built from config so valid_grades is the single source of truth for grade letters.` through the end of `_grade_segment` (`    return norm if _GRADE_SEG.match(norm) else None`). Keep `_validate_grade_confidence_list`, `_inner_task_payload`, `_effective_entity_type` and `_validate_grade_confidence_in_payload`.
4. `agent.py`: delete the whole `def _decode_payload(` function, through `    return out` and its trailing blank lines, so two blank lines precede the following `# ----` rule.
5. `formatting.py`: delete the two lines `# Compact grades_encoded row: 000|DTA5|GCA4|…` and `_ENCODED_GRADE_LINE = re.compile(r"^\d{3}\|")`, and the three functions `clean_encoded_agent_payload`, `looks_like_encoded_grades_text` and `coerce_grades_encoded_json_parse`. Leave two blank lines between `enumerate_array` and `parse_enumerate_array`.
6. Lint rule as in Stage 3 step 5, for `agent.py` and `formatting.py`: delete only names that `ruff --select F401` newly flags.
7. Run the Done-when checks, then commit `code(AST-2180): retire the encoded decoder — _decode_payload, segment regexes, strict-batch + string coercion helpers` and publish.

## Traceability

- **AC 5 (missing code → retry, never X):** `hydrate_grade_tool_input` records the missing code as a per-entity `decode_failures` row (AST-2178) and never defaults it to X. Stage 1 passes the hydrated dict on unchanged. `_run_batch_consult` already subtracts `decode_failures` from `missing` and routes each through `_consult_batch_fail_dest` (`_RETRY` sibling), while row `000` flows to `process_fn`. `render_verdict` does the same for a single job (`mine` lookup). Stage 3 adds the same routing for prefilter single and batch, and the vet reasons.
- **AC 6 (decoder retired):** Stage 4 deletions plus the Stage 2 / Stage 3 removals (see the AC 6 note for the one unrelated hit).
- **AC 7 (one marker):** the literal is deleted with `_decode_payload` and consult's normalize. Every module now reads `structured_output` through `grade_forced_tool` (`agent.py`), and nothing in `src/core`, `src/external` or `src/ui/api` names an output type.
- **AC 8 (live shape errors stop):** not verifiable from this host (Susan, 2026-10-14: no provider calls). Susan runs a `meteorite_grade_do` batch on staging after the epic lands.
- **Parent AC 3 (epic level, from AST-2179):** closes here. Every grader `do_task` and grader ad-hoc test now passes `forced_tool`, and `grade_forced_tool` returns `None` for every other task, so non-grader kwargs are unchanged.

## § AC 6 note — one hit outside this ticket

AC 6's pattern `duplicate vector code` also matches `src/core/candidate.py:1633`, `return f"Rubric '{rk}' has duplicate vector codes: {', '.join(dupes)}"`. That's the rubric-save validator, which has nothing to do with the decoder, and `candidate.py` is outside this Scope. The decoder's own message (`duplicate vector code … in encoded line`) is deleted in Stage 4. This plan leaves `candidate.py` alone. Chuckles or Joan: either narrow AC 6 (e.g. `duplicate vector code [A-Z]` or `in encoded line`), or accept this one known hit. Betty's AC 6 test should match whichever is chosen. Likewise, four comments in `candidate.py` / `database.py` still name `_GRADE_SEG`. They're stale but harmless, and they're out of scope.

## Canon check

- **`patt.task.dispatch-retry`:** no new retry queue. Every light-check failure, and the no-codes skip, returns through the existing per-entity routers (`_consult_batch_fail_dest`, `_prefilter_batch_fail_dest`), which take an entity to its `_RETRY` sibling first and the configured error state second. Vet's existing error counting is unchanged.
- **`stat.agent.grade-vector-validation`:** the schema `do_task` sends lists every code as required and closes each row, with the grade enum. On advisory hosts the hydrate's light check enforces the same rules (AST-2178). This ticket only routes the outcome.
- **`stat.agent.confidence-bounds`:** X0 normalization and X ⇒ 0 stay in the hydrate. No confidence is coerced here, and `_validate_grade_confidence_in_payload` still runs on the hydrated shape in the `post_rubric_decode` block.
- **`stat.logging.warning`:** each failed entity is warned once, by the router that moves it (`_log_fail_dest` / `_warn_company`), now naming the hydrate's reason. The hydrate warns only for an unattachable row id (AST-2178).
- **`stat.logging.error`:** a hydrate exception is warned once at the existing `do_task` handler (`warn_exc`, unchanged), and transport parse failures stay logged in transport (AST-2179). The no-codes skip is one ERROR before send, the same as the AST-2000 empty-token skip.

## Execution contract

The plan is binding. Steps run in order, and stages run in order. No added files, modules or dependencies, and nothing committed from `debug/`. If a step is ambiguous, an anchor line doesn't match the code, or a check fails, stop and comment on the parent [AST-2172](https://linear.app/astralcareermatch/issue/AST-2172):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

Each stage ends in one `code(AST-2180): …` commit on the epic worktree, published with `git push origin HEAD:sub/AST-2172/AST-2180-wire-graders-retire-decoder`. Compile (`$PY -m py_compile` on every touched file) and lint before every commit; never `--no-verify`. Run `sync-child.sh` with `--ftr AST-2172-structured-output-graders`. No live provider calls.

## Expected test churn (Betty, not this build)

Tests that import or patch the deleted names go red. Plan-time `rg -l` file counts under `tests/`: `_decode_payload` 4, `_GRADE_SEG` 4, `_STRICT_ENCODED_BATCH_CONSULT_KEYS` 3, `_is_strict_encoded_batch_consult` 1, `_normalize_rubric_task_response` 2, `_should_decode_as_encoded_line` 2, `_parse_link_index_field` 1. The `formatting` coercion helpers have no direct test imports. So do do_task tests that feed encoded-string grader replies, and the api_admin ad-hoc decode test. New coverage worth having: grader `do_task` sends `forced_tool` and non-graders don't (parent AC 3, end to end); AC 5 through `_run_batch_consult` with a hydrated `decode_failures`; agent failure + salvage from tool `agent_performance`; `vector_reviews` admitted on feedback tasks; prefilter single/batch and vet reasons; ad-hoc company-task hydrate.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Appendix A — `agent.py` helpers (Stage 1 step 2)

```python
# Forced-tool name on every grader call (AST-2172); transport reads it back from forced_tool["name"].
GRADE_TOOL_NAME = "submit_grades"


def grade_call_codes(task_key: str, ctx: Optional[Dict[str, Any]]) -> List[str]:
    """Rubric vector codes for one grader call — the same list feeds the schema and the hydrate.
    Vet grades its one configured vector; every other grader the keys of ctx["vector_labels"] (rubric order)."""
    vet = INFLOW_CONFIG["vet"]
    if task_key == vet["task_key"]:
        return [vet["grade_vector_code"]]
    return list((ctx or {}).get("vector_labels") or {})


def grade_forced_tool(task_key: str, ctx: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """{name, input_schema} when task_key's output type carries structured_output; None for every other task.
    Raises ValueError when a grader call has no rubric codes."""
    output_type = (TASK_CONFIG.get(task_key) or {}).get("output_type", "")
    if not ASTRAL_CONFIG["output_types"].get(output_type, {}).get("structured_output"):
        return None
    schema = build_grade_tool_schema(output_type, grade_call_codes(task_key, ctx), grade_row_ids(ctx or {}))
    if is_vector_feedback_task(task_key):
        # AST-860 vector reviews ride agent_performance (RUBRIC_FEEDBACK_CONFIG prompt_suffix). The closed object
        # must admit them or enforcing hosts drop every review; copied so grade_schema's constant stays intact.
        perf = schema["properties"]["agent_performance"]
        schema["properties"]["agent_performance"] = {
            **perf,
            "properties": {
                **perf["properties"],
                "vector_reviews": {"type": ["array", "null"], "items": {"type": "string"}},
            },
            "required": [*perf["required"], "vector_reviews"],
        }
    return {"name": GRADE_TOOL_NAME, "input_schema": schema}


```

## Appendix B — `do_task` grader branch (Stage 1 step 9)

Indented for `do_task`'s body (4 spaces).

```python
    # Grader tasks (AST-2172): the forced tool's input hydrates into the decoded jobs[] / companies[] / results[]
    # shape, so scoring, grades_key persistence and retry routing downstream are unchanged.
    post_rubric_decode = False
    if structured:
        codes = grade_call_codes(task_key, ctx)
        _perf = parsed.get("agent_performance") if isinstance(parsed, dict) else None
        # AST-1839: a model-reported failure (bad source content) is an agent failure. Rubric graders only —
        # vet never read status.
        if task_config.get("rubric_artifact") and _agent_performance_status(_perf) == "failure":
            _note = (_perf.get("failure_note") if isinstance(_perf, dict) else None) or parsed.get("failure_note")
            agent_err = f"Agent failure: {_note or 'Agent returned status=failure with no note'}"
            _warn_hop_no_success(task_key, agent_err, parsed)
            # Keep cleanly hydrated rows so a batch caller fails only the gaps, not the batch (AST-2089).
            # Same validation bar as the success path; any error → None → caller fails the whole batch.
            salvaged = None
            if (ctx or {}).get("batch_entities"):
                try:
                    _cand = hydrate_grade_tool_input(task_key, output_type, parsed, codes, ctx)
                    if schema:
                        _coerce_schema_str_fields_from_list(_cand, schema, debug=debug)
                    if ((_cand.get("jobs") or _cand.get("companies"))
                            and not _validate_response_schema(_cand, schema, task_key)
                            and not _validate_grade_confidence_in_payload(_cand, task_key)):
                        salvaged = _cand
                except Exception as exc:
                    logger.debug("%s | no salvage after agent failure: %s: %s", task_key, type(exc).__name__, exc)
            if _should_store:
                try:
                    await asyncio.to_thread(_store_response_block,
                        entity_type,
                        task_key,
                        batch_id,
                        _failure_response_block_data(index, _audit_response_body(raw_text, parsed, agent_err)),
                        index=index,
                        debug=debug, entity_ids=_store_ids)
                except Exception as exc:
                    _log_swallowed_agent_data(index, task_key, exc)
            _close_hop_ledger(success=False, clear_log=True, failure_error=agent_err)
            return _with_harvest({"success": False, "agent_failure": True, "api_response": result.get("api_response"),
                    "parsed_response": None, "error": agent_err, "raw_response": parsed,
                    "salvaged_response": salvaged, "timesheet": result.get("timesheet", {})})
        try:
            logger.debug(
                "Calling hydrate_grade_tool_input: [task_key=%s, output_type=%s, codes=%s, parsed=%s]",
                task_key, output_type, codes, parsed,
            )
            parsed = hydrate_grade_tool_input(task_key, output_type, parsed, codes, ctx or {})
            logger.debug("Response from hydrate_grade_tool_input: %s", parsed)
            result["parsed_response"] = parsed
            post_rubric_decode = True
        except Exception as exc:
            logger.warn_exc(
                "%s | %s\n  %s: %s\n  Returning this hop as failed",
                index or "-",
                task_key,
                type(exc).__name__,
                exc,
            )
            if _should_store:
                try:
                    await asyncio.to_thread(_store_response_block,
                        entity_type, task_key, batch_id,
                        _failure_response_block_data(index, _audit_response_body(raw_text, parsed, str(exc))),
                        index=index,
                    debug=debug, entity_ids=_store_ids)
                except Exception:
                    _log_swallowed_agent_data(index, task_key)
            _close_hop_ledger(success=False, clear_log=True, failure_error=str(exc))
            return _with_harvest({"success": False, "api_response": result.get("api_response"),
                    "parsed_response": None, "error": str(exc), "timesheet": result.get("timesheet", {})})
```
