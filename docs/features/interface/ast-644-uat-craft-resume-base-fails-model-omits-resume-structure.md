# AST-644 — UAT: craft_resume_base fails — model omits resume_structure

**Linear:** [AST-644 — UAT: craft_resume_base fails — model omits resume_structure](https://linear.app/astralcareermatch/issue/AST-644/uat-craft-resume-base-fails-model-omits-resume-structure)  
**Parent:** [AST-601 — Rebuild 519 git casualty](https://linear.app/astralcareermatch/issue/AST-601/rebuild-519-git-casualty) (context only)  
**Publish ref:** `origin/sub/AST-601/AST-644-craft-resume-base-missing-structure` (origin only)

## Summary

Susan’s **Generate** path for candidate `karfo` runs `craft_resume_base`. The LLM returns a valid envelope (`agent_performance.status: success`) with content fields in `agent_payload` (`candidate_name`, `professional_summary`, `experience`, etc.) but **no** `resume_structure` key. `do_task` calls `normalize_craft_resume_base_agent_payload` then `_validate_response_schema`; because `TASK_CONFIG["craft_resume_base"]["response_schema"]` marks `resume_structure` as required, validation fails with `Missing required field 'resume_structure'` before `parse_candidate_resume` can persist anything.

Downstream persistence already handles omission: `split_craft_resume_base_payload` falls back to `default_resume_structure()` when structure is missing or has no `sections` (AST-517). The gap is **pre-validation normalization** — it flattens nested section strings but never injects the default catalog, so schema validation hard-fails on models that skip the structure block. This bug closes that gap by injecting `default_resume_structure()` in `normalize_craft_resume_base_agent_payload` when structure is absent or empty, mirroring the split path. No UI, `DATA_SHAPES`, or AST-517 storage schema changes.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Extend `normalize_craft_resume_base_agent_payload` to inject default structure when omitted | core |
| `tests/component/core/test_candidate.py` | Regression: missing/empty `resume_structure` passes schema after normalize | test (Betty manifest — engineer runs during test-child) |

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/core/agent.py` | Already calls normalize before `_validate_response_schema` for `craft_resume_base` (~lines 1713–1722) |
| `src/utils/config.py` | Keep `resume_structure` `required: True` in schema — normalization supplies it |
| `src/core/candidate.py` | `split_craft_resume_base_payload`, `parse_candidate_resume` — already default on split |

**Out of scope:** Base Resume Content UI / API (AST-616), global `DATA_SHAPES`, AST-517 storage shape, prompt edits, making `resume_structure` optional in schema.

---

## Stage 1: Inject default structure in pre-validation normalize

**Done when:** `normalize_craft_resume_base_agent_payload` ensures `agent_payload` (or flat payload dict) contains a valid `resume_structure` with non-empty `sections` before `_validate_response_schema` runs, using the same fallback rule as `split_craft_resume_base_payload`.

1. In `src/core/candidate.py`, locate `normalize_craft_resume_base_agent_payload` (~line 488). After the existing payload resolution block and **after** `_flatten_craft_resume_section_strings(payload)` (flatten first so nested structure content still promotes when structure is present), add default injection:

   ```python
   raw_struct = payload.get("resume_structure")
   if not isinstance(raw_struct, dict) or not raw_struct.get("sections"):
       payload["resume_structure"] = default_resume_structure()
   ```

   ⚠️ **Decision:** Match `split_craft_resume_base_payload` (~lines 585–589): missing key, non-dict, or dict without `sections` → config default. Do **not** call `normalize_resume_structure` here — invalid partial blobs from the model still fail at split/persist if they somehow bypass injection; UAT repro is **omitted** key, not malformed structure.

2. Do **not** change `TASK_CONFIG["craft_resume_base"]["response_schema"]` — keep `"resume_structure": {"type": "dict", "required": True}` so the contract stays “structure always present after normalize.”

3. Do **not** modify `split_craft_resume_base_payload` or `parse_candidate_resume` unless build discovers they no longer receive post-unwrap flat dicts (they should remain unchanged).

4. `python3 -m py_compile src/core/candidate.py`

**Ritual:** `code(AST-644): inject default resume_structure before craft_resume_base schema validation`

---

## Stage 2: Regression tests (Betty manifest / test-child)

**Done when:** Component tests prove envelope payloads without `resume_structure` pass `_validate_response_schema` after normalize, and `split_craft_resume_base_payload` still yields default structure + content keys.

Betty adds these to the **Tests Ready** manifest. If omitted, engineer adds only the cases below.

1. In `tests/component/core/test_candidate.py`, inside `TestAst517ResumeStructure`, add **`test_normalize_injects_default_when_resume_structure_missing`**:
   - Build envelope matching UAT repro:

     ```python
     parsed = {
         "agent_performance": {"status": "success"},
         "agent_payload": {
             "candidate_name": "Kar Fo",
             "candidate_title": "Engineer",
             "candidate_contact_detail": "kar@example.com",
             "professional_summary": "Summary",
             "core_competencies": "Skills",
             "experience": "Jobs",
         },
     }
     ```

   - Call `candidate_mod.normalize_craft_resume_base_agent_payload(parsed)`.
   - Assert `parsed["agent_payload"]["resume_structure"]["sections"]` contains `candidate_name` (default catalog).
   - Import `_validate_response_schema` from `src.core.agent` and `TASK_CONFIG`; assert `_validate_response_schema(parsed, TASK_CONFIG["craft_resume_base"]["response_schema"], "craft_resume_base") is None`.

2. Add **`test_normalize_injects_default_when_resume_structure_sections_empty`**:
   - Envelope with `"resume_structure": {"sections": {}}` plus required content strings.
   - After normalize, assert default sections injected and schema validation passes.

3. Add **`test_split_still_uses_default_when_structure_missing_without_normalize`** (documents existing split behavior — should already pass, no code change):
   - Flat dict `{"professional_summary": "only body"}` through `split_craft_resume_base_payload` only; assert default structure + content (existing `test_split_uses_default_when_structure_missing` may suffice — skip duplicate if identical).

4. Re-run `tests/component/core/test_candidate.py` — `TestAst517ResumeStructure` and existing normalize/schema tests must stay green.

**Ritual:** `test(AST-644): craft_resume_base normalize injects default resume_structure`

---

## Execution contract reminders

- Do **not** change Base Resume Content UI, `GET …/resume_structure`, or accent persistence (AST-616).
- Do **not** remove or weaken `resume_structure` in `response_schema` — injection is the fix.
- When model **does** return a valid custom `resume_structure`, normalize must **not** overwrite it (injection guard is only when missing/empty sections).
- Blocking ambiguity → `🛑` comment on **AST-601** parent per plan-child execution contract.

---

## Self-Assessment

**Scope:** `Single-Component` — One helper extension in `candidate.py` plus focused component tests; no config schema or UI changes.

**Conf:** `high` — Root cause is confirmed in code path (validate before split); AST-517 already defines default fallback at split; existing tests cover split-default and normalize-flatten; fix is a small parity gap closure.

**Risk:** `Medium` — `craft_resume_base` gates candidate artifact generation; wrong injection logic could overwrite valid model structure or mask malformed blobs; guard conditions mirror proven split path.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `default_resume_structure()` — same fallback as split/resolve; no duplicate catalog |
| §2.1 config | No new config keys; catalog stays in `RESUME_STRUCTURE_DEFAULT` |
| §2.4 batch | N/A — single-candidate task path |
| §2.6 state machine | N/A — no state transition change |
| §3.3 imports | Changes stay in `candidate.py`; no new cross-layer imports |
| §3.5 naming | Existing function extended; no new public API surface |

No conflicts requiring `conf-!!-NONE`.
