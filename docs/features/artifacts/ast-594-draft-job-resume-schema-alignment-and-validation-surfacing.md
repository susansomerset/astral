# AST-594 — draft_job_resume schema alignment and validation surfacing

**Linear:** [AST-594](https://linear.app/astralcareermatch/issue/AST-594/draft-job-resume-schema-alignment-and-validation-surfacing-draft-job)  
**Parent:** [AST-592](https://linear.app/astralcareermatch/issue/AST-592/draft-job-resume-dispatch-job-failed)  
**Publish ref:** `sub/AST-592/ast-594-draft-job-resume-schema-alignment` (origin only)

Susan's `draft_job_resume` hop failed with `Missing required field 'grades'` after a successful-looking DeepSeek response that returned structure-keyed resume prose (`candidate_name`, `professional_summary`, `experience`, …). **AST-450** left a graded-consult `TASK_CONFIG` on this hop; the model and **AST-313** prompts expect **AST-551** / **AST-518** section-keyed resume content instead. This ticket replaces the stale schema, validates payloads against the active candidate's enabled section catalog (all sections optional; unknown keys rejected), normalizes nested/wrapped JSON like **craft_resume_base** (**AST-536** precedent), and makes validation failures legible on the hop's Execution History row and in backend logs.

**Out of scope:** Manage Tasks prompt text (**AST-313**), consult-path graded tasks (`grade_do`, `grade_get`, `grade_like`, …), unrelated **AST-300** UAT items, Execution History UI redesign beyond surfacing the existing error message on the hop row.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Replace `draft_job_resume` graded-consult block with structure-hop metadata-only `response_schema`; remove `vectors`, `grading_mode`, `context_format`; add `resume_section_payload: True` flag. | utils |
| `src/core/candidate.py` | Add `normalize_draft_job_resume_agent_payload`, `validate_draft_job_resume_payload` (catalog whitelist, optional sections, unknown-key errors). | core |
| `src/core/agent.py` | Wire normalize + catalog validation for `draft_job_resume`; skip vector/grade validation for that key; improve validation-failure audit body + `flush_log_buffer` on hop-scoped failures. | core |
| `tests/component/utils/test_config.py` | Assert `draft_job_resume` no longer requires `grades` / vectors / `grade_like` context. | tests |
| `tests/component/core/test_candidate.py` | Unit tests for normalize + catalog validation helpers. | tests |
| `tests/component/core/test_agent.py` | Replace grade-vector `draft_job_resume` tests with structure-keyed acceptance, unknown-key rejection, validation message observability. | tests |

**Not in this ticket:** `src/core/tracker.py` persist gate (already structure-aware per **AST-551**), `src/core/dispatcher.py`, Manage Tasks DB rows, frontend.

---

## Stage 1: Retire graded-consult contract on `draft_job_resume`

**Done when:** `TASK_CONFIG["draft_job_resume"]` no longer lists `grades`, `vectors`, `grading_mode`, or `context_format: "grade_like_{index}"`; static schema covers optional job metadata only; config tests pass.

1. In **`src/utils/config.py`**, replace the **`draft_job_resume`** entry (currently lines ~602–643) with:

   ```python
   "draft_job_resume": {
       "phase": "E. Job Artifacts",
       "seq": 4,
       "response_schema": {
           "astral_job_id": {"type": "str", "required": False},
           "company": {"type": "str", "required": False},
           "title": {"type": "str", "required": False},
       },
       "response_format": "json",
       "resume_section_payload": True,
       "entity_type": "job",
       "requires_candidate_key": True,
       "trigger_state": None,
   },
   ```

   - **Remove** the entire `grades` block, `vectors` list, `grading_mode`, and `context_format`.
   - **Do not** add per-section keys to `response_schema` — section bodies are validated at runtime against the candidate catalog (Stage 2).
   - Update the stale comment *"Graded resume draft — vectors/schema kept…"* to note structure-keyed hop per **AST-551** / **AST-592**.

2. In **`tests/component/utils/test_config.py`**, extend **`TestAst450ArtifactPipelineTaskKeys`** (or add **`TestAst594DraftJobResumeSchema`**) with assertions:
   - `"grades" not in TASK_CONFIG["draft_job_resume"]["response_schema"]`
   - `"vectors" not in TASK_CONFIG["draft_job_resume"]`
   - `"grading_mode" not in TASK_CONFIG["draft_job_resume"]`
   - `TASK_CONFIG["draft_job_resume"].get("context_format") is None`
   - `TASK_CONFIG["draft_job_resume"].get("resume_section_payload") is True`

3. Run `python3 -m py_compile src/utils/config.py`.

⚠️ **Decision:** Static schema stays metadata-only so Susan can add custom section ids on `artifacts.resume_structure` without config edits; runtime validation enforces the catalog (**AST-518** / Susan 2026-06-06: all sections optional).

---

## Stage 2: Normalize and validate structure-keyed payloads

**Done when:** Helpers accept Susan's original brief payload (no `grades`), reject invented keys with an explicit error, and normalize nested wrappers before validation; unit tests green.

1. In **`src/core/candidate.py`**, add module-level constant **`_DRAFT_JOB_RESUME_METADATA_KEYS = frozenset({"astral_job_id", "company", "title", "task_success"})`** (same optional metadata as static schema + existing `task_success` pattern).

2. Add **`normalize_draft_job_resume_agent_payload(parsed: dict) -> None`** (mutates like `normalize_craft_resume_base_agent_payload`):
   - Resolve inner dict: `payload = parsed.get("agent_payload")` when dict, else `parsed` when dict.
   - If **`resume_structure`** present with nested **`content`** / section **`content`** fields, call existing **`_flatten_craft_resume_section_strings(payload)`** (reuse — do not duplicate flatten logic).
   - For each **`nest_key`** in **`_CRAFT_RESUME_CONTENT_DICT_KEYS`** (`content`, `section_content`, `base_resume`): when `payload[nest_key]` is a dict, promote each **`(sid, val)`** onto `payload[sid]` when `sid` not already a coercible string.
   - For every key in **`payload`** that is not in **`_DRAFT_JOB_RESUME_METADATA_KEYS`** and not **`resume_structure`**: if value is list/dict, replace with **`_coerce_resume_section_string(val)`** when that returns a string (handles list-of-lines and list-of-dict experience blobs per existing craft_resume coercion).

3. Add **`validate_draft_job_resume_payload(parsed: dict, candidate_data: dict) -> Optional[str]`** returning error string or **`None`**:
   - Call **`normalize_draft_job_resume_agent_payload(parsed)`** first.
   - **`payload = _inner`-equivalent**: use `parsed.get("agent_payload")` if dict else `parsed`.
   - If not dict → **`"agent_payload must be a dict"`**.
   - **`structure = resolve_resume_structure(candidate_data)`**; **`allowed = set(enabled_resume_section_ids(structure))`**.
   - If **`allowed`** empty → **`"candidate has no enabled resume sections"`**.
   - For each **`key, val`** in **`payload.items()`**:
     - Skip keys in **`_DRAFT_JOB_RESUME_METADATA_KEYS`** and **`resume_structure`**.
     - Skip **`grades`**, **`dealbreakers`**, **`clarifications`**, **`overall_assessment`**, **`ja_notes`** with explicit error **`Unknown field 'grades' (graded consult fields are not valid on draft_job_resume)"`** — use a single message pattern **`Unknown or disallowed field '{key}' on draft_job_resume"`** listing consult leftovers and unknown catalog ids alike.
     - If **`key not in allowed`** → **`f"Unknown resume section key '{key}' (not in candidate catalog: {sorted(allowed)})"`**.
     - If section value present and **`_coerce_resume_section_string(val)`** is **`None`** → **`f"Section '{key}' must be prose text (string or coercible list)"`**.
     - When coerced text differs from raw, write coerced string back onto **`payload[key]`** (mutate so downstream **`{$CALLER_*}`** hops see flat strings).
   - **Do not** require any section to be present (all optional per Susan).
   - Return **`None`** when all keys pass.

4. In **`tests/component/core/test_candidate.py`**, add class **`TestAst594DraftJobResumePayload`**:
   - **`test_validate_accepts_structure_keyed_subset`**: default structure; payload with `professional_summary` + `experience` strings only → **`None`**.
   - **`test_validate_rejects_unknown_section_key`**: payload with `made_up_section` → error contains **`Unknown resume section key`** and **`made_up_section`**.
   - **`test_validate_rejects_grades_field`**: payload with `grades: []` → error mentions **`grades`**.
   - **`test_normalize_promotes_nested_content_dict`**: `agent_payload: {content: {professional_summary: "x"}}` → after normalize, top-level `professional_summary == "x"`.
   - **`test_normalize_flattens_resume_structure_wrapper`**: mirror **`test_normalize_flattens_nested_section_content_onto_top_level`** pattern but without requiring full craft_resume_base schema.

5. Run `python3 -m py_compile src/core/candidate.py` and pytest on the new class.

---

## Stage 3: Wire `do_task` validation and failure surfacing

**Done when:** `do_task("draft_job_resume", …)` runs normalize + catalog validation after JSON parse; successful Susan-like payloads return `success: True` without `grades`; validation failures set hop ledger **FAILED**, log ERROR with exact message, store RESPONSE body with message first; `run_next` still receives flat `agent_payload` for **check_job_resume** (**AST-530** hop logging unchanged).

1. In **`src/core/agent.py`**, add helper **`_validation_failure_audit_body(err: str, raw_text: Optional[str], parsed: Any) -> str`**:
   - Return **`f"Validation failed: {err}\n\n--- model response ---\n{body}"`** where **`body = _audit_response_body(raw_text, parsed, None)`** (never omit **`err`** when raw_text exists — fixes Susan's "response looks fine" confusion).

2. In **`do_task`**, in the JSON validation block (both pre-decode ~1363 and post-decode ~1478 paths where **`craft_resume_base`** normalization already runs):
   - After **`craft_resume_base`** normalize branch, add:
     ```python
     if task_key == "draft_job_resume":
         from src.core.candidate import normalize_draft_job_resume_agent_payload
         normalize_draft_job_resume_agent_payload(parsed)
     ```
   - After **`_validate_response_schema(parsed, schema, task_key)`** succeeds (metadata schema only for this key), when **`task_config.get("resume_section_payload")`** and **`candidate_data`** from ctx/job context is non-empty:
     ```python
     from src.core.candidate import validate_draft_job_resume_payload
     cat_err = validate_draft_job_resume_payload(parsed, candidate_data)
     ```
     On **`cat_err`**: treat like schema failure (same return path as existing **`err`** block below).

3. In the existing schema / catalog failure block (~1371–1387 and parallel post-decode path):
   - Replace **`_audit_response_body(raw_text, parsed, err)`** with **`_validation_failure_audit_body(err, raw_text, parsed)`** for stored RESPONSE rows.
   - After **`logger.error("do_task validation failed. task_key=%r error=%s", …)`**, when **`log_batch_id.get()`** is set, call **`flush_log_buffer()`** so Execution History expanded logs show the ERROR line immediately (hop ledger path per **AST-531**).
   - Keep **`_close_hop_ledger(success=False, clear_log=True)`** unchanged.

4. In vector/grade validation block (~1410–1431): wrap with **`if task_config.get("vectors") and task_key != "draft_job_resume":`** — or simply rely on vectors removed from config so block is skipped; add explicit guard comment referencing **AST-594** so a future re-add does not regress.

5. **Regression guard for AC4:** Do **not** change **`run_next`** recursion, **`_chain_tokens_for_next_hop`**, or **`_log_chain_entry`** format. After success, existing unwrap **`parsed = parsed["agent_payload"]`** (~1433) must still run so **`{$CALLER_RESPONSE}`** carries flat section strings.

6. In **`tests/component/core/test_agent.py`**:
   - **Replace** **`test_passes_vector_grade_validation_in_json_envelope`** with **`test_draft_job_resume_accepts_structure_keyed_payload_without_grades`**: monkeypatch LLM to return Susan-like subset (`professional_summary`, `experience` as string or coercible list); **`ctx={"candidate_data": {…}}`** with default **`resolve_resume_structure`**; assert **`out["success"] is True`**.
   - **Replace** **`test_skips_grade_validation_when_grades_missing`** with **`test_draft_job_resume_rejects_unknown_section_key`**: payload **`{"agent_payload": {"bogus_section": "x"}}`**; assert **`out["success"] is False`**, **`"Unknown resume section key" in out["error"]`**.
   - **Add** **`test_draft_job_resume_validation_failure_surfaces_message_in_error_and_response_block`**: enable hop ledger monkeypatch pattern from existing chain tests; on failure assert **`out["error"]`** equals catalog message; assert **`save_agent_data`** / **`_store_response_block`** received body starting with **`Validation failed:`** (spy **`save_agent_data`** block_data arg).
   - **Update** **`test_json_confidence_store_exception`** / **`test_json_grade_store_exception`** when they use **`draft_job_resume`** — switch to a task that still uses graded vectors (e.g. keep one on **`evaluate_jd`** if applicable) or delete if redundant.

7. Run targeted pytest:
   ```bash
   cd /Users/susan/chuckles/astral-ada
   python3 -m pytest tests/component/core/test_candidate.py::TestAst594DraftJobResumePayload tests/component/core/test_agent.py -k "draft_job_resume" -q
   python3 -m pytest tests/component/utils/test_config.py -k "Ast450 or Ast594" -q
   ```

---

## Stage 4: Manual verification notes (Susan / parent AST-592 UAT)

**Done when:** Parent AC 1–4 observable on integration branch after build + test.

1. Re-run dispatch batch **`draft_job_resume-80308ccb-087e-4100-af38-937ea9c75e01`** (or manual **Run** on **`draft_job_resume`** for the same job) — hop **COMPLETED**, no **`grades`** error.
2. Execution History: failed hop row shows **FAILED**; expand logs → ERROR line contains exact validation text; View agent data → RESPONSE starts with **`Validation failed:`** when intentionally malformed.
3. Successful chain: **`check_job_resume`** hop still receives prior hop content via **`{$CALLER_*}`**; **AST-530** hop log lines still present in backend logs.

---

## Self-Assessment

**Scope:** `scope-Single-Component` — Touches `config.py` one task entry, two helpers in `candidate.py`, and targeted `do_task` validation paths in `agent.py` plus component tests; no dispatcher or UI changes.

**Conf:** `conf-high` — **AST-536** / **craft_resume_base** normalization and **AST-551** tracker catalog patterns already exist; the fix is rewiring `draft_job_resume` off **AST-450** graded stubs and exposing existing error text on hop rows.

**Risk:** `risk-Medium` — Wrong catalog validation or breaking **`{$CALLER_*}`** unwrap would block the resume artifact chain mid-**AST-300** UAT; graded consult tasks must remain untouched.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Plan compliance |
|------|-----------------|
| §1.3 DRY | Reuses `_flatten_craft_resume_section_strings`, `_coerce_resume_section_string`, `resolve_resume_structure`, `enabled_resume_section_ids`; no second catalog resolver. |
| §2.1 config | Task behavior driven by `TASK_CONFIG` flag + catalog from candidate artifacts; no env lookups. |
| §2.4 batch | Hop ledger + `log_batch_id` unchanged; `flush_log_buffer` only on validation failure when batch scoped. |
| §2.6 state machine | No job state transitions in this ticket. |
| §3.3 imports | Lazy imports inside `do_task` for candidate helpers (matches `craft_resume_base` pattern). |
| §3.5 naming | New helpers prefixed by domain (`normalize_draft_job_resume_*`, `validate_draft_job_resume_*`). |

No conflicts requiring `conf-!!-NONE`.

---

## Build (Ada)

**Branch:** `sub/AST-592/ast-594-draft-job-resume-schema-alignment`  
**Tip:** `ab01d00452720b5126acb48f78dd1b2105d838d1`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `9f816e32` | Retire graded-consult `TASK_CONFIG` for `draft_job_resume` |
| 2 | `ced5b960` | `normalize_draft_job_resume_agent_payload` + `validate_draft_job_resume_payload` |
| 3 | `ab01d004` | `do_task` catalog validation + `_validation_failure_audit_body` + hop log flush |

**Betty note:** Component tests per plan Stages 1–3 (`test_config`, `test_candidate`, `test_agent`) not included in build — per build-astral test-tree ban; manifest at qa-astral.

## Radia review (AST-594)

**Diff:** `origin/dev...origin/sub/AST-592/ast-594-draft-job-resume-schema-alignment` (8 files, +529 / −93)  
**Published:** `c40385b2`

### What's solid

- **Plan fidelity:** Graded-consult `TASK_CONFIG` retired; `resume_section_payload: True` drives runtime catalog validation. Normalization reuses **AST-536** helpers; validation errors surface via `_validation_failure_audit_body` + `flush_log_buffer` on hop-scoped failures — matches AC 2–3.
- **§1.3 DRY / §2.1 config:** Single catalog path through `resolve_resume_structure` / `enabled_resume_section_ids`; no duplicate section resolver.
- **§3.3 imports:** Lazy `candidate` imports in `do_task` mirror `craft_resume_base`; acceptable per plan.
- **Regression guard:** Explicit `task_key != "draft_job_resume"` on vector validation; `agent_payload` unwrap unchanged after success path.
- **Tests:** Config, candidate helper, and `do_task` coverage align with bible §7.13zv manifest (structure-keyed accept, unknown key, disallowed `grades`, `Validation failed:` RESPONSE prefix).

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| **discuss** | `src/core/agent.py` — `if task_config.get("resume_section_payload") and cd:` | Catalog whitelist skipped when `candidate_data` is falsy (`{}`). Plan says validate when candidate_data is non-empty; production dispatch loads candidate via tracker, so Susan's batch should be covered. Confirm ad-hoc/preview runs without candidate_data are intentionally unvalidated. |
| **advisory** | `tests/component/core/test_agent.py` — `_draft_job_resume_ctx()` | Helper name implies draft_job_resume only but is reused for several `evaluate_jd` tests; harmless, slightly confusing for future readers. |
| **advisory** | `src/core/agent.py` — confidence/grade failure paths | Still use `_audit_response_body`; schema/catalog failures now use `_validation_failure_audit_body`. Out of AST-594 scope; optional follow-up for consistent hop RESPONSE formatting. |
| **advisory** | `src/core/agent.py` — `_validation_failure_audit_body` | Applied to all JSON schema validation failures (not only `draft_job_resume`). Beneficial for Execution History clarity; slightly broader than ticket title. |

**Verdict:** No **fix-now** items. Ready for **resolve-astral** after discuss item acknowledged (or accepted as intentional).

## Resolution (Ada, 2026-06-06)

- **fix-now:** None — no product changes required.
- **discuss (catalog gate on falsy `cd`):** **Accepted as intentional.** Stage 3 plan explicitly gates catalog validation on non-empty `candidate_data`; metadata-only schema still runs. Production dispatch and tracker paths load candidate data before `draft_job_resume`; ad-hoc preview without `ctx`/`candidate_data` remains metadata-validated only (same pattern as other `requires_candidate_key` warnings). No fail-closed change in this ticket.
- **advisory:** Deferred — helper rename and uniform confidence RESPONSE formatting out of scope for **AST-594**.
