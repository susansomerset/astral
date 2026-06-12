<!-- linear-archive: AST-338 archived 2026-06-03 -->

## Linear archive (AST-338)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-338/refactor-qualify-job-listings  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-345

### Description

Revise prompt content for qualify_job_listing to parse, evaluate and IF AND ONLY IF there are no "F" grades assessed, provide the additional metadata parsed. so "02-ABFX", "03-ABBC-Superstar-https://www.jobs…/jobid/384-384-salary_range:100-140k"

The first three values will be instructed to be the title, url and jobid, and additional content needs a label.

This is, of course, to reduce the output volume without necessitating a secondary call for metadata.

### Comments

_No comments._

---

# AST-338 Refactor qualify_job_listings

## Plan

### Context

`qualify_job_listings` currently returns a full JSON response for every job in a batch — `astral_job_id`, `job_title`, `job_link`, `company_job_id`, `grades`, `salary_range`, `location`. Most jobs **fail** at this stage. Returning all that metadata for failing jobs is pure wasted output tokens.

AST-336 built the abbreviated response infrastructure (`grade_only`, `grade_reason`, `grade_notes`). AST-338 replaces those generic names with task-specific output type keys and introduces `qualify_job_output` — a conditional format that emits only grades for failing jobs, and grades + metadata for passing ones.

- **Failing jobs (any F grade):** `02-ABFX` — position + grades only, nothing else.
- **Passing jobs (no F grades):** `03-ABBC|Superstar|https://jobs.co/id/384-b|384-b|salary_range:100-140k` — position + grades + metadata.

Token cost drops to near-zero for the majority (failing) jobs, while passing jobs still capture everything needed to bootstrap the job record.

---

### Design Decisions

**D1 — New `qualify_job_output` output type.**
A task-specific entry in `output_types`, replacing the generic `grade_meta` name. `output_types` keys are named for the task they serve — the instructions reference specific fields (`job_title`, `job_link`, `company_job_id`) so pretending they're reusable generic types is misleading. The conditional behaviour (metadata only when no F grade) is `qualify_job_output`-specific.

**D2 — `|` as the metadata field separator.**
The issue examples show `-` throughout, but `-` is unambiguous for `{pos}-{grades}` only. After that it conflicts badly:
- URLs always contain `://` and paths like `/jobs/id/384-b`
- Salary ranges like `100-140k`
- Company job IDs like `job-384-senior`

Proposal: use `|` as the separator between metadata fields. So the full format is:
```
{pos}-{grades}                                         (failing job)
{pos}-{grades}|{title}|{url}|{jobid}|{key}:{val}|...  (passing job)
```
**→ ✅ Confirmed — `|` as metadata separator.**

**D3 — Positional metadata fields: title, url, jobid.**
Per the issue, the first three metadata fields are always `job_title`, `job_link`, `company_job_id` (in that order, no label needed). Additional fields use `key:value` format. Currently the relevant optional fields from the existing response schema are `salary_range` and `location`. Any others the Agent finds can be expressed as `key:value`.

**D4 — `response_format` changes from `"json"` to `"text"` for `qualify_job_listings`.**
The AST-336 abbreviated hydration in `agent.py` only activates when `response_format == "text"`. The current value is `"json"`. This change is required.

**D5 — `response_schema` is removed or stubbed for this task.**
The existing JSON schema validates the full JSON response. With a text format, schema validation doesn't apply. The `response_schema` should be cleared or replaced with a minimal stub so that `_validate_response_schema` doesn't run on a text response.

**D6 — Vector names come from the joblist rubric (candidate data), not TASK_CONFIG.**
Unlike `grade_do`/`grade_get`/`grade_like`, `qualify_job_listings` has no static `vectors` list in TASK_CONFIG — its grading criteria come from the candidate's `joblist_rubric` artifact (a candidate-specific list of `{label, content}` items). The hydrator needs the rubric labels to produce `{"vector": "<label>", "grade": "<X>"}` tuples. The vector labels are available in `cd["artifacts"]["joblist_rubric"]["criteria"][i]["label"]`.

**D7 — Batch hydration is output_type-driven, not task-driven.**
The current hydration in `agent.py` handles single-line responses. `qualify_job_listings` is a batch task: one `do_task` call, one multi-line text blob back with N lines (one per job). The hydrator needs to map array positions back to `astral_job_id`s, which requires the input jobs list.

The hydration dispatch lives in `_run_batch_consult` (consult.py) and is keyed on `output_type`, not on `task_key`. No per-task hook or closure. When `output_type == "qualify_job_output"`, `_run_batch_consult` calls `hydrate_response(output_type, schema, lines)` (exported from agent.py) and proceeds with the standard `{"jobs": [...]}` structure. Any future batch task with the same output_type gets this for free.

**D8 — Agent prompt update is a manual DB change.**
The `qualify_job_listings` prompt in `agent_task` uses `{$OUTPUT_INSTRUCTIONS}` — resolved from `qualify_job_output`'s `instructions` field via the token system. Prompt author controls placement; no auto-injection into `nocache_content`.

---

### Step 1: Restructure `output_types` entries as task-specific dicts with a single `instructions` token field

**File:** `src/utils/config.py`

Each `output_types` entry becomes a task-specific dict with a single `instructions` field. Keys are named for the task they serve — not generic output categories. Rename existing flat-string entries accordingly and drop the auto-inject logic in `do_task`. The prompt author places `{$OUTPUT_INSTRUCTIONS}` explicitly, consistent with `{$REASON_CODES}`, `{$JOBLIST_RUBRIC}`, etc.

```python
"output_types": {
    "qualify_job_output": {
        "instructions": (
            "Output one line per job — no JSON, no extra text.\n"
            "If any grade is F: {array_position}-{grades}\n"
            "If no F grades:    {array_position}-{grades}|{job_title}|{job_link}|{company_job_id}[|{key}:{value}...]\n"
            "  {array_position}: 0-based input position, zero-padded to 2 digits\n"
            "  {grades}: one letter per rubric criterion, in order (A/B/C/D/F/X)\n"
            "  Additional metadata fields use key:value format (e.g., salary_range:100-140k)"
        ),
    },
    "evaluate_jd_output": {
        "instructions": "...",   # existing grade_only content, reworded for evaluate_jd
    },
    "consult_grade_output": {
        "instructions": "...",   # existing grade_reason/grade_notes content, reworded for consult tasks
    },
}
```

Rename `output_type` values in TASK_CONFIG to match (e.g., `qualify_job_listings` gets `"output_type": "qualify_job_output"`).

Add one TOKEN_SOURCES entry:
```python
"OUTPUT_INSTRUCTIONS": {"source": "output_type", "field": "instructions"},
```

`resolve_tokens` handles `source: "output_type"` by looking up `ASTRAL_CONFIG["output_types"][TASK_CONFIG[task_key]["output_type"]]["instructions"]`.

---

### Step 2: Update TASK_CONFIG for `qualify_job_listings`

**File:** `src/utils/config.py`

Three changes to the `qualify_job_listings` block:
1. `"response_format": "text"` (was `"json"`)
2. Add `"output_type": "qualify_job_output"`
3. Remove `response_schema` (or replace with an empty stub `{}`) — JSON validation doesn't apply to text responses

```python
"qualify_job_listings": {
    "phase": "D. Job Analysis",
    "seq": 1,
    "response_schema": {},         # text format — no JSON schema validation
    "response_format": "text",     # was "json"
    "output_type": "qualify_job_output",   # NEW
    "context_format": "qualify_job_listings_{index}",
    "entity_type": "job",
    "requires_candidate_key": True,
    "trigger_state": None,
},
```

---

### Step 3: Add `hydrate_response()` to `agent.py`

**File:** `src/core/agent.py`

Instead of a task-specific function, one exported function dispatches by `output_type`:

```python
def hydrate_response(
    output_type: str,
    response_schema: Dict[str, Any],
    lines: List[str],
) -> Dict[str, Any]:
    """Hydrate abbreviated Agent response into structured data.

    output_type drives dispatch. response_schema carries the context each
    type needs — different keys per type:

      grade_only / grade_reason / grade_notes:
        {"vectors": [...], "reason_codes": {...}}  (reason_codes for grade_reason only)

      grade_meta:
        {"jobs": [...], "rubric_labels": [...]}    (jobs for pos→id mapping, labels for vector names)

    lines: abbreviated response already split on newline, blanks stripped.
    Returns {"jobs": [...]} for batch types, or the single-job structure for single-job types.
    """
    if output_type == "qualify_job_output":
        return _hydrate_grade_meta(lines, response_schema["jobs"], response_schema["rubric_labels"])
    elif output_type in ("grade_only", "grade_reason", "grade_notes"):
        # single-line — existing helpers, wrapped for uniform interface
        if len(lines) != 1:
            raise ValueError(f"{output_type} expects exactly 1 line, got {len(lines)}")
        vectors = response_schema.get("vectors", [])
        reason_codes = response_schema.get("reason_codes")
        array_pos, grades = _hydrate_abbreviated_response(lines[0], vectors, output_type, reason_codes)
        return {"array_pos": array_pos, "grades": grades}
    else:
        raise ValueError(f"hydrate_response: unknown output_type {output_type!r}")
```

Private helper: `_hydrate_grade_meta(lines, jobs, rubric_labels) -> {"jobs": [...]}` — parses each line, maps `array_pos → jobs[array_pos]["astral_job_id"]`, builds grades from rubric_labels.

Private helper: `_parse_grade_meta_line(line, rubric_labels) -> dict` — parses one `NN-GRADES` or `NN-GRADES|title|url|jobid[|key:val...]` line.

The existing single-job helpers remain; `hydrate_response` wraps them for the single-job path.

---

### Step 4: `_run_batch_consult` dispatches via `hydrate_response`

**File:** `src/core/consult.py`

```python
from src.core.agent import hydrate_response

output_type = TASK_CONFIG.get(task_key, {}).get("output_type", "natural")
    if output_type == "qualify_job_output":
    cd = ctx.get("candidate_data") if ctx else None
    rubric = (cd or {}).get("artifacts", {}).get("joblist_rubric", {})
    rubric_labels = [c["label"] for c in (rubric.get("criteria") or [])]
    schema = {"jobs": jobs, "rubric_labels": rubric_labels}
    raw_lines = [l for l in (result["parsed_response"] or "").splitlines() if l.strip()]
    try:
            parsed = hydrate_response(output_type, schema, raw_lines)
    except Exception as e:
        error_state = cfg.get("error_state")
        if error_state:
            tracker.transition_job_state(astral_ids, error_state)
        return {"success": False, "error": str(e), "passed": 0, "failed": 0, "total": len(jobs)}
else:
    parsed = result["parsed_response"]

response_jobs = parsed["jobs"]
```

Output_type-driven, no task-specific code. A future batch task with `output_type: "grade_meta"` gets this for free.

---

### Step 5: `qualify_job_listings` in `consult.py` — minimal changes

**File:** `src/core/consult.py`

1. **`assemble()`** — unchanged (already sends job_site + raw_job_listing per job).

2. **`process()`** — unchanged in structure. The hydrated `response_job` dict comes from `hydrate_response`, which populates the same fields the current JSON response provides (`job_title`, `job_link`, `company_job_id`, `grades`, `salary_range`, `location`). Failing jobs (any F grade) will have `job_title=None`, `job_link=None`, etc. — the existing relative-URL check and min_title_length check still apply.

3. **Call to `_run_batch_consult`** — **no change at all**. The output_type dispatch in Step 4 handles everything transparently.

---

### Step 6: Prompt update in `agent_task` table

**Manual update — no migration script.**

The `qualify_job_listings` prompt row in the `agent_task` table needs to:
1. Remove any instruction to return JSON (replaced by `grade_meta` instructions injected from config)
2. Clarify the conditional metadata rule: "only append metadata if ALL grades are non-F"
3. Confirm field order: title → full job URL (constructed from job_site + relative path if needed) → company job ID → optional labeled extras

Note: the `grade_meta` format instructions from `ASTRAL_CONFIG["output_types"]["grade_meta"]` are injected automatically into `nocache_content` by `do_task`. The prompt should complement those, not duplicate them.

---

## Files Changed

| File | Change |
|------|--------|
| `src/utils/config.py` | Convert all `output_types` entries to task-specific dicts with `instructions` field; add `qualify_job_output` entry; rename `grade_only`/`grade_reason`/`grade_notes` to `evaluate_jd_output`/`consult_grade_output`; add `OUTPUT_INSTRUCTIONS` to TOKEN_SOURCES; update `qualify_job_listings` in TASK_CONFIG: `response_format → "text"`, `output_type → "qualify_job_output"`, clear `response_schema` |
| `src/utils/config.py` → `resolve_tokens` | Handle `source: "output_type"` — resolve `instructions` field from `ASTRAL_CONFIG["output_types"][task_output_type]` |
| `src/core/agent.py` | Remove auto-inject-to-nocache_content logic for output_types; add `_parse_grade_meta_line()`, `_hydrate_grade_meta()` (private helpers) and `hydrate_response()` (exported unified dispatcher) |
| `src/core/consult.py` | Add output_type-aware hydration dispatch in `_run_batch_consult`; `qualify_job_listings` call site is unchanged |
| `agent_task` DB table | Update `qualify_job_listings` prompt (manual) — add `{$OUTPUT_INSTRUCTIONS}` token where format instructions belong |

---

## Open Questions

| # | Question | Default if no answer |
|---|----------|----------------------|
| Q1 | Confirm `\|` as metadata separator (vs. keeping `-` from issue examples) | ✅ Confirmed — use `\|` |
| Q2 | output_type dispatch in `_run_batch_consult` vs. per-task hook | ✅ Confirmed — output_type-driven dispatch, no task-specific hooks |
| Q3 | Is `ctx["candidate_data"]["artifacts"]["joblist_rubric"]` reliably populated at call time? | ✅ Confirmed — task can't run without artifacts |

---

## Code Rules Check (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.4 No hardcoded sets — `grade_meta` format string in config, not inline | ✅ |
| §2.1 Config as source of truth — new output type lives in `ASTRAL_CONFIG["output_types"]` | ✅ |
| §2.4 Batch processing — `_run_batch_consult` claim/process/release pattern preserved | ✅ |
| §1.3 DRY — hydrator lives in `agent.py` (single home for all hydration logic) | ✅ |
| §3.3 Layer rules — `agent.py` is core; consult.py imports from agent.py ✅ | ✅ |
| §2.6 State machine — no changes to states or transitions | ✅ |
| §1.5 Logging — hydrator raises `ValueError`, caller logs at batch level | ✅ |
| `response_schema` cleared for text task | ⚠️ Verify `_validate_response_schema` skips cleanly on `{}` schema |

---

## Review

**Commit:** uncommitted (working tree diff against HEAD on `dev`)
**Branch:** `dev`
**Reviewed:** 2026-03-22

---

## What's Solid

- **Plan fidelity is high.** Steps 1–5 from the plan are all represented in the diff. The new `qualify_job_output` entry, TASK_CONFIG changes (`response_format: "text"`, `output_type`, empty `response_schema`), `hydrate_response()` dispatcher in `agent.py`, output_type-aware hydration in `_run_batch_consult`, and the refactored `process()` in `qualify_job_listings` all land as specified.
- **Clean removal of the auto-inject pattern.** The old `do_task` block that appended output instructions to `nocache_content` and the post-response decompression block are fully removed. The new `{$OUTPUT_INSTRUCTIONS}` token + `TOKEN_SOURCES` resolver is a cleaner, config-driven replacement — prompt authors control placement.
- **Hydration dispatch is output_type-driven, not task-driven** — exactly as D7 specifies. Future batch tasks with a different output_type get their own branch in `hydrate_response()` with zero changes to `_run_batch_consult`.
- **`_parse_grade_meta_line` is solid.** Validates position, grade count vs rubric length, grade values against `VALID_GRADES`, and separates the failing-job (grades-only) from passing-job (grades + metadata) paths cleanly.
- **`process()` refactor in `qualify_job_listings` is a nice improvement.** Early return for failing jobs (no metadata → just save grades and transition) keeps the passing-job path cleaner and avoids unnecessary title/URL validation on jobs that are already failing.
- **Ad Hoc endpoint hydration.** The `adhoc_test` endpoint now mirrors `_run_batch_consult`'s hydration logic and surfaces the structured result as `hydrated` in the response. The UI displays it in a `<pre>` block. Useful for prompt iteration.
- **`_validate_response_schema` is safe** with `response_schema: {}` — the guard at line 686 checks `response_format in ("json", "python")` and skips for `"text"`, so the empty schema is never even evaluated.

---

## Issues

### Issue 1 — `output_types` is in `DISPATCH_TASKS`, resolver reads `ASTRAL_CONFIG` ⚠️ required

The `resolve_tokens` handler for `source: "output_type"` (config.py line 1281) looks up:
```python
entry = ASTRAL_CONFIG.get("output_types", {}).get(output_type_key, {})
```

But `output_types` was moved into `DISPATCH_TASKS` (line 834), not `ASTRAL_CONFIG`. The plan (Step 1) says the entry belongs in `ASTRAL_CONFIG["output_types"]` — and the `resolve_tokens` code was written to match that. But the actual dict landed in `DISPATCH_TASKS["output_types"]` instead.

**Impact:** `{$OUTPUT_INSTRUCTIONS}` will always resolve to empty string. The Agent prompt will never receive format instructions, so responses will be unstructured and hydration will fail on every call.

**Fix:** Either move `output_types` into `ASTRAL_CONFIG` (as the plan specifies), or change the resolver to read from `DISPATCH_TASKS`. Moving to `ASTRAL_CONFIG` is the cleaner path — `DISPATCH_TASKS` is for dispatchable task entries, not output format definitions.

---

### Issue 2 — Old `grade_only`/`grade_reason`/`grade_notes` removed but still referenced 🔧 fix now

The plan (Step 1) says to rename the existing output types: `grade_only` → `evaluate_jd_output`, `grade_reason`/`grade_notes` → `consult_grade_output`. Instead, they were deleted entirely. The old decompression code in `do_task` was also deleted (the block that handled these types post-response).

The existing tasks `evaluate_jd`, `consult_do`, `consult_get`, `consult_like` don't currently have `output_type` set in TASK_CONFIG, so they're not broken *today* — they still use `response_format: "json"` and the old schema validation path. But: (a) the AST-336 abbreviated output infrastructure is now orphaned — the config entries are gone, the decompression functions (`_decompress_grade_only`, `_decompress_grade_reason`, `_decompress_grade_notes`) are still in `agent.py` but nothing calls them, and (b) the `hydrate_response` dispatcher doesn't handle the old types, so re-enabling them would require rework.

**Impact:** Not a runtime break, but the AST-336 output_type infrastructure is effectively dead code after this change. If the intent was to preserve it, the rename-and-restructure from the plan should be applied. If the intent was to defer those types to a future ticket, the orphaned decompression functions should be cleaned up.

**Recommendation:** Clarify intent. Either restore the renamed entries per the plan, or remove the dead decompression functions and document that those output types will be re-implemented when their tasks migrate to text format.

---

### Issue 3 — Indentation error in `AdminAnthropicAdHoc.tsx` 🔧 fix now

Line 176 has `setHydrated(null)` indented with 8 spaces instead of 4:

```typescript
    setTesting(true)
    setResponse(null)
        setHydrated(null)    // ← 8 spaces instead of 4
    setTimesheet(null)
```

JavaScript doesn't care (it's syntactically valid), but it's a formatting inconsistency that will trip a linter or confuse a reader.

---

### Issue 4 — Ad Hoc hydration uses `run_adhoc`, not `do_task` — candidate_data not resolved through token system ℹ️ advisory

The `adhoc_test` endpoint calls `run_adhoc` (which bypasses `do_task`), then separately hydrates the response. The hydration works because it fetches `candidate_data` directly from the database. But `run_adhoc` doesn't call `resolve_tokens` on the prompt — the Ad Hoc preview system handles that separately via `preview_task_prompt`. This is consistent with the existing pattern, but worth noting: the Ad Hoc path and the production path diverge in how `{$OUTPUT_INSTRUCTIONS}` gets resolved. If the token resolution happens at preview time (before the test button is pressed), the Ad Hoc flow will work. If the user edits the prompt after preview but before test, the token won't re-resolve.

**Impact:** Low — the Ad Hoc is a development tool, and the existing preview→test flow already has this characteristic for all tokens.

---

### Issue 5 — `api_admin.py` imports `database` directly ℹ️ advisory

Line 665: `candidate = database.get_candidate(candidate_id)` — the Ad Hoc hydration code in `api_admin.py` imports and calls the data layer directly. Per §3.3, the UI layer may import core and utils only, never data.

However, `api_admin.py` already has extensive direct `database` imports (line 7) established by prior tickets. This is pre-existing tech debt, not new. The new hydration code follows the established pattern in this file.

---

### Issue 6 — `process()` raises `ValueError` on relative URL for passing jobs — inconsistent error handling ℹ️ advisory

In `qualify_job_listings.process()`, a relative `job_link` raises `ValueError`, which causes `_run_batch_consult` to catch it, add the job to `bad_grades`, and eventually transition it to `error_state`. Meanwhile, a too-short title gets an explicit `transition_job_state` to `error_state` and returns cleanly.

Both are validation failures on passing jobs, but they use different mechanisms (exception vs. explicit transition). The `ValueError` path means the job ends up in `bad_grades` set and gets a generic "process_fn failed" log warning, which is less informative than a purpose-built log line. This existed before this PR (the `raise ValueError` was there), but the refactored flow makes the inconsistency more visible.

---

## Recommended Actions

| # | Severity | Action |
|---|----------|--------|
| 1 | Fix now | Move `output_types` dict from `DISPATCH_TASKS` into `ASTRAL_CONFIG` so `resolve_tokens` can find it. Without this, `{$OUTPUT_INSTRUCTIONS}` resolves to empty and the feature is non-functional. |
| 2 | Discuss | Decide whether the old AST-336 output types (`grade_only`, `grade_reason`, `grade_notes`) should be renamed-and-restructured per the plan, or deferred. If deferred, remove the orphaned decompression functions. |
| 3 | Fix now | Fix indentation of `setHydrated(null)` on line 176 of `AdminAnthropicAdHoc.tsx` (8 spaces → 4). |
| 4 | Advisory | Ad Hoc token resolution divergence is a known characteristic, not a new bug. No action needed. |
| 5 | Advisory | `api_admin.py` direct data-layer imports are pre-existing tech debt. No action for this PR. |
| 6 | Advisory | Consider making relative-URL rejection use the same explicit-transition pattern as the too-short-title check, for consistency. Not blocking. |
