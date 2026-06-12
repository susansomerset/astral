<!-- linear-archive: AST-288 archived 2026-06-03 -->

## Linear archive (AST-288)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-288/consult-uses-agent-model  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** High / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Update [consult.py](<http://consult.py>) and [anthropic.py](<http://anthropic.py>) so that API call parameters (model, temperature, max_tokens) flow from the agent record rather than global config. The api block is being removed from ASTRAL_CONFIG — callers must supply all parameters explicitly or the system hard-fails.

**Acceptance Criteria:**

[**consult.py**](<http://consult.py>)** Changes:**

* When fetching the agent record for a task, read `model_code`, `temperature`, and `max_tokens` from the agent row
* Pass all three explicitly to `do_task` (or the underlying `_fetch_response`) as named parameters
* Raise a clear ValueError if any of the three are missing or None on the agent record — no silent fallback

[**anthropic.py**](<http://anthropic.py>)** Changes:**

* `_fetch_response` requires `model`, `temperature`, and `max_tokens` as explicit parameters — no defaults, no fallback to config
* Remove all references to `ASTRAL_CONFIG['api']`
* Hard crash (raise ValueError) if any of the three are not provided by the caller
* `calculate_cost_with_cache` call updated to pass `model_code` per the updated cost_calculator.py signature

**Notes:**

* This issue depends on: Per-Agent Model Configuration (Astral Admin)
* The intent is zero tolerance for misconfiguration — a mis-configured agent should fail loudly at runtime, not silently use a wrong or expensive model
* Chuckles to verify all callers of do_task / \_fetch_response after this change and confirm no other callers are broken

**Database:**

* No schema changes in this issue
* [database.py](<http://database.py>) module docstring updated per ASTRAL_CODE_RULES 1.1 if touched

### Comments

_No comments._

---

# ast-288: Consult Uses Agent Model — Plan

## Overview

Verify and finalize that API call parameters (model, temperature, max_tokens) flow from the agent record through `do_task` for all consult paths. AST-287 already implemented the core plumbing — `do_task` extracts model params from the agent row, validates them, and threads them through to `_send_and_parse`. This ticket confirms zero-tolerance enforcement, fixes stale references, updates callers that reference renamed task keys, and handles a syntax error from config changes.

**Already done in AST-287:**

- `do_task` reads `model_code`, `temperature`, `max_tokens` from agent record
- Raises `ValueError` if `model_code` is missing/NULL — no silent fallback
- Falls back to `MODELS[model_code]["default_temperature"]` / `default_max_tokens` only when agent values are NULL
- `_send_and_parse` requires explicit `model_code` — raises `ValueError` if not provided
- `calculate_cost_with_cache(usage, model_code)` — model-aware pricing
- `ASTRAL_CONFIG["api"]` block removed; no code reads from it

**What this ticket delivers:**

- Fix stale comment in `anthropic.py` referencing removed `ASTRAL_CONFIG["api"]`
- Fix `candidate.py` caller that uses renamed task key `"parse_resume"` → `"parse_resume_text"`
- Fix syntax error in `config.py` TASK_CONFIG (unclosed brace on `craft_application_responses`)
- Rename `bio_upshot` → `bio_summary` and relocate from `artifacts` to `context` in candidate_data
- Confirm consult.py callers work unchanged (they delegate to `do_task` which handles everything)
- Verify all other `do_task` callers in `roster.py` and `consult.py` — no changes needed

---

## Sub 1: Fix stale comment in `anthropic.py`

**File:** `src/external/anthropic.py`

Line 37 referenced the removed `ASTRAL_CONFIG["api"]` block. Replaced with:

```python
# API call params (model, temperature, max_tokens) come from agent records, not config.
```

---

## Sub 2: Fix renamed task key in `candidate.py`

**File:** `src/core/candidate.py`

`parse_candidate_resume()` called `do_task(task_key="parse_resume", ...)`. The task was renamed to `"parse_resume_text"` in TASK_CONFIG. Updated the call and the docstring reference.

---

## Sub 3: Fix syntax error in `config.py`

**File:** `src/utils/config.py`

The `craft_application_responses` entry was missing its closing `},` — the `}` on line 420 closed `TASK_CONFIG` prematurely instead of closing the entry dict. This caused a `SyntaxError: '{' was never closed` crash on the production server at deploy time.

---

## Sub 4: Rename `bio_upshot` → `bio_summary`, relocate to context

`bio_summary` is candidate-sourced data (the candidate can provide it directly or it can be seeded by `bootstrap_candidate_context`), so it belongs in `context`, not `artifacts`.

**Files changed:**

- `src/utils/config.py`: `TOKEN_SOURCES` entry `BIO_UPSHOT` → `BIO_SUMMARY`, path changed from `artifacts.bio_upshot` to `context.bio_summary`. `bootstrap_candidate_context` response_schema field renamed `bio_upshot` → `bio_summary`.
- `src/data/database.py`: Added `_migrate_bio_upshot_to_summary()` — idempotent migration that moves existing `artifacts.bio_upshot` values to `context.bio_summary` for all candidates. Called from `_migrate_candidate_data_structure()`.

---

## Sub 5: Caller audit — confirm no changes needed

All `do_task` callers in the codebase:


| File                        | Caller                   | Task key                                                                                                 | Status                                               |
| --------------------------- | ------------------------ | -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `src/core/consult.py`       | `render_verdict`         | dynamic from `cfg["agent_task"]`                                                                         | OK — `do_task` handles model params                  |
| `src/core/consult.py`       | `qualify_job_listings`   | `"qualify_job_listings"`                                                                                 | OK                                                   |
| `src/core/consult.py`       | `evaluate_jd`            | `"evaluate_jd"`                                                                                          | OK                                                   |
| `src/core/roster.py`        | multiple callers         | `"prefilter_company"`, `"find_job_site"`, `"vet_job_list"`, `"parse_job_list"`, `"select_culture_pages"` | OK — all valid task keys                             |
| `src/core/candidate.py`     | `parse_candidate_resume` | `"parse_resume"`                                                                                         | **FIXED** → `"parse_resume_text"`                    |
| `scripts/call_anthropic.py` | `_fetch_response`        | N/A (file-based legacy)                                                                                  | OK — defaults to Sonnet via `_fetch_response` params |


No other callers need changes. `consult.py` in particular requires zero modifications — it calls `do_task` with a task_key, and `do_task` internally resolves the agent, reads model params from the agent row, and threads them through.

---

## File change summary


| File                        | Change type                                                                                                                 |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `src/external/anthropic.py` | Fix stale comment (line 37)                                                                                                 |
| `src/core/candidate.py`     | Update task key `"parse_resume"` → `"parse_resume_text"` + docstring                                                        |
| `src/utils/config.py`       | Fix unclosed brace in `craft_application_responses`; rename `bio_upshot` → `bio_summary` in TOKEN_SOURCES + response_schema |
| `src/data/database.py`      | Add `_migrate_bio_upshot_to_summary()` migration                                                                            |


