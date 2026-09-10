<!-- linear-archive: AST-345 archived 2026-06-03 -->

## Linear archive (AST-345)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-345/missing-response-schema-for-qualify-job-listings-and-evaluate-jd  
**Status at archive:** Done  
**Project:** Astral Agent  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

What we expect back from the anthropic call is not the hydrated response_schema.

000|ERC|MEC|PGA|WAA|MWC|KOB|QCB|2983982372|Mediocre Job Title|[https://www.workheredummy.com/jobs/2983982372|location:Remote|salary_range:$140-160k](<https://www.workheredummy.com/jobs/2983982372%7Clocation:Remote%7Csalary_range:$140-160k>)
001|ERA|MEA|PGF|WAA|MWA|KOA|QCA|8398237461
002|ERB|MEB|PGB|WAB|MWA|KOA|QCB|9823975238|Fine Job Title|[https://www.workheredummy.com/jobs/9823975238|location:Remote|salary_range:$140-160k](<https://www.workheredummy.com/jobs/9823975238%7Clocation:Remote%7Csalary_range:$140-160k>)
003|ERC|MEC|PGC|WAC|MWC|KOC|QCC|2983472983|So-So Job Title|[https://www.workheredummy.com/jobs/2983472983|location:Remote|salary_range:$160-180k](<https://www.workheredummy.com/jobs/2983472983%7Clocation:Remote%7Csalary_range:$160-180k>)
004|ERD|MED|PGD|WAD|MWD|KOD|QCD|2983470239|Um Nope Job Title|[https://www.workheredummy.com/jobs/2983470239|location:Remote|salary_range:$140-160k](<https://www.workheredummy.com/jobs/2983470239%7Clocation:Remote%7Csalary_range:$140-160k>)
005|ERD|MED|PGD|WAD|MWD|KOD|QCF|2983702392
006|ERF|MEF|PGF|WAF|MWF|KOF|QCF
007|ERA|MEF|PGA|WAA|MWA|KOA|QCA
008|ERA|MEA|PGA|WAA|MWA|KOF|QCF
009|ERA|MEA|PGA|WAA|MWA|KOA|QCA|2839756234|Dream Job Title|[https://www.workheredummy.com/jobs/2983982372|location:Remote|salary_range:$140-160k](<https://www.workheredummy.com/jobs/2983982372%7Clocation:Remote%7Csalary_range:$140-160k>)

The hydrated response schema is like: 
{Astral_job_id:"…",
external_job_id: "2983982372",
grades: \["ER":{"vector":"Easy Rider", "grade":"C"}, "ME":{"vector":"Medical Experience", "grade":"A"}…\]
job_data: \[{key:title, value:"Mediocre Job Title"}, {key:"job_link", value:"[https://www.workheredummy.com/jobs/2983982372](<https://www.workheredummy.com/jobs/2983982372%7Clocation:Remote%7Csalary_range:$140-160k>)"}, {key:"location", value:"Remote"}…\]

It is the agent's hydrate response that produces the structured output, and that structured output MUST be EXACTLY what is specified in "Response_schema" for the task.

### Comments

_No comments._

---

# AST-345: Missing Response Schema for qualify_job_listings and evaluate_jd

## Root Cause

Both `qualify_job_listings` and `evaluate_jd` have `response_schema: {}` in `TASK_CONFIG`. An
empty dict is falsy, so `stringify_response_schema` returns `""` — the `{$RESPONSE_SCHEMA}` token
is blank. With no envelope example and `response_format: "json"`, haiku-4-5 improvises a JSON
object for `agent_payload` instead of returning a compact string. This crashes `hydrate_response`
which expects pipe-delimited text lines.

**The pipe-delimited compact format was correct and intentional.** The fix is to:
1. Define proper `output_types` entries with clear `payload_instructions` for the AI
2. Add `response_schema` to both tasks (the structured contract for downstream callers)
3. Move hydration into `do_task` so callers always receive a fully structured `response_schema`

---

## Architecture: `output_types` as the DRY Format Registry

`ASTRAL_CONFIG["output_types"]` is the existing registry for payload format definitions. Tasks
reference it via `output_type`. `{$OUTPUT_INSTRUCTIONS}` already resolves from
`output_types[task.output_type]["instructions"]` — the token infrastructure is in place.

We're extending the registry with three reusable format types:

| Key | Format | Who uses it |
|-----|--------|-------------|
| `grades_json` | JSON `agent_payload` referencing `{$RESPONSE_SCHEMA}` | `grade_do`, etc. |
| `grades_encoded` | Compact text, grades only | `evaluate_jd` |
| `grades_encoded_meta` | Compact text, grades + optional metadata | `qualify_job_listings` |

`do_task` checks `output_type` to decide whether hydration is needed after the AI responds.
Tasks without `grades_encoded*` output types behave exactly as today — zero behavior change.

---

## What We Are Pulling Out

### Relics (delete)

| Item | Where | Why |
|------|-------|-----|
| `qualify_job_output` | `ASTRAL_CONFIG["output_types"]` | Replaced by `grades_encoded_meta` |
| `evaluate_jd_output` | `ASTRAL_CONFIG["output_types"]` | Replaced by `grades_encoded` |
| `_parse_grade_segment` | `agent.py` | Replaced by `_decode_payload` |
| `_parse_grade_meta_line` | `agent.py` | Replaced by `_decode_payload` |
| `_hydrate_grade_meta` | `agent.py` | Replaced by `_decode_payload` |
| `hydrate_response` | `agent.py` (public) + `consult.py` import | Replaced by internal decoding in `do_task` |
| Output-type hydration block | `consult.py` lines 213–235 | `do_task` now returns fully decoded output |

### Future Features (deferred)

| Item | Notes |
|------|-------|
| `confidence` / `require_confidence` | `_parse_grade_segment` had scaffolding for a confidence digit on grade segments. Never wired end-to-end. Removed cleanly now; add back properly when scoped. |

---

## Step 1 — `src/utils/config.py`

### 1a. Add three reusable entries to `output_types`; remove the two task-specific ones

The existing `instructions` field is renamed to `payload_instructions` — clearer about its
purpose. Update `TOKEN_SOURCES["OUTPUT_INSTRUCTIONS"]` field reference accordingly.

```python
"output_types": {
    # Generic JSON format — prompt uses {$RESPONSE_SCHEMA} separately to show the structure.
    "grades_json": {
        "payload_instructions": (
            "Respond with valid JSON using exactly the structure shown in the response schema.\n"
            "This output is parsed by software — any deviation will cause a processing failure."
        ),
    },
    # Compact encoded format — grades only, no metadata fields.
    "grades_encoded": {
        "payload_instructions": (
            "Output one line per item — no JSON, no extra text.\n"
            "Format: {pos}|{code}{grade}|{code}{grade}|...\n"
            "  {pos}: 0-based input position, zero-padded to 3 digits\n"
            "  {code}: 2-char rubric vector code from the grading instructions\n"
            "  {grade}: one letter — A B C D F X\n"
            "\nExample:\n"
            "006|ERF|MEF|PGF|WAF|MWF|KOF|QCF\n"
            "007|ERA|MEF|PGA|WAA|MWA|KOA|QCA\n"
            "008|ERA|MEA|PGA|WAA|MWA|KOF|QCF"
        ),
    },
    # Compact encoded format — grades + optional metadata fields.
    "grades_encoded_meta": {
        "payload_instructions": (
            "Output one line per item — no JSON, no extra text.\n"
            "Format: {pos}|{code}{grade}|...|{company_job_id}[|{job_title}|{job_link}[|{key}:{value}...]]\n"
            "  {pos}: 0-based input position, zero-padded to 3 digits\n"
            "  {code}: 2-char rubric vector code from the grading instructions\n"
            "  {grade}: one letter — A B C D F X\n"
            "  Metadata fields follow grades when your instructions say to include them.\n"
            "\nExample:\n"
            "000|ERC|MEC|PGA|WAA|MWC|KOB|QCB|2983982372|Mediocre Job Title|https://www.workheredummy.com/jobs/2983982372|location:Remote|salary_range:$140-160k\n"
            "001|ERA|MEA|PGF|WAA|MWA|KOA|QCA|8398237461\n"
            "002|ERB|MEB|PGB|WAB|MWA|KOA|QCB|9823975238|Fine Job Title|https://www.workheredummy.com/jobs/9823975238|location:Remote|salary_range:$140-160k"
        ),
    },
},
```

Update `TOKEN_SOURCES["OUTPUT_INSTRUCTIONS"]`:
```python
"OUTPUT_INSTRUCTIONS": {"source": "output_type", "field": "payload_instructions"},
```

### 1b. Update both task configs: set `output_type` and add `response_schema`

The `response_schema` here is the **structured contract** for downstream callers — not shown in the
prompt for encoded tasks (their `payload_instructions` examples are sufficient).

**`qualify_job_listings`:**
```python
"output_type": "grades_encoded_meta",
"response_schema": {
    "jobs": {
        "type": "list", "required": True,
        "items_schema": {
            "astral_job_id":  {"type": "str", "required": True},
            "grades":         {"type": "list", "required": True,
                               "items_schema": {
                                   "vector": {"type": "str", "required": True},
                                   "grade":  {"type": "str", "required": True},
                               }},
            "company_job_id": {"type": "str", "required": False},
            "job_title":      {"type": "str", "required": False},
            "job_link":       {"type": "str", "required": False},
            "job_data":       {"type": "dict", "required": False},  # key:value extras (location, salary_range, company, etc.)
        },
    },
},
```

**`evaluate_jd`:**
```python
"output_type": "grades_encoded",
"response_schema": {
    "jobs": {
        "type": "list", "required": True,
        "items_schema": {
            "astral_job_id": {"type": "str", "required": True},
            "grades":        {"type": "list", "required": True,
                              "items_schema": {
                                  "vector": {"type": "str", "required": True},
                                  "grade":  {"type": "str", "required": True},
                              }},
        },
    },
},
```

### 1c. Add `int` branch to `_schema_to_example`

`elif t == "int": result[key] = 0` — integer fields render as `0` in prompt examples.

---

## Step 2 — `src/core/agent.py`

### Replace pipe-parser stack with `_decode_payload`

Delete `_parse_grade_segment`, `_parse_grade_meta_line`, `_hydrate_grade_meta`, `hydrate_response`.

Grade segments are auto-detected by pattern — any pipe-delimited field matching
`[A-Z]{2}[<valid_grade_letters>]` after the position index is a grade. `_GRADE_SEG` is built at
module load from `ASTRAL_CONFIG["valid_grades"]` so the regex stays in sync with the config.

For non-meta types (`_meta` not in `output_type`), any content after the grade segments raises
`ValueError` — unrecognized trailing content is an AI format violation for grades-only tasks.

`do_task` checks `"_encoded" in output_type` to decide whether to decode, and passes `output_type`
through so the decoder knows whether to accept metadata. Schema validation runs **after** hydration
against the assembled `response_schema` — not against the raw string payload.

```python
# Module level — built from config so valid_grades is the single source of truth
import re
_valid = "".join(ASTRAL_CONFIG.get("valid_grades", []))
_GRADE_SEG = re.compile(rf'^[A-Z]{{2}}[{_valid}]$')


def _decode_payload(task_key: str, output_type: str, payload: str, ctx: dict) -> dict:
    """Parse compact pipe-delimited agent_payload into response_schema shape.

    Grade segments auto-detected by _GRADE_SEG pattern.
    pos → astral_job_id via ctx["batch_entities"].
    Vector codes stored as-is (e.g. "ER") — no label lookup needed.
    With_meta derived from "_meta" in output_type; trailing non-grade content raises if False.
    """
    with_meta = "_meta" in output_type
    batch_entities = (ctx or {}).get("batch_entities") or []
    lines = [l for l in (payload or "").splitlines() if l.strip()]

    result_jobs = []
    for line in lines:
        fields = [f.strip() for f in line.split("|")]
        try:
            pos = int(fields[0])
        except (ValueError, IndexError):
            raise ValueError(f"[{task_key}] bad position field in line: {line!r}")
        if pos < 0 or pos >= len(batch_entities):
            raise ValueError(f"[{task_key}] pos {pos} out of range (batch={len(batch_entities)})")

        grades, meta = [], []
        for f in fields[1:]:
            (grades if _GRADE_SEG.match(f) else meta).append(f)

        if meta and not with_meta:
            raise ValueError(f"[{task_key}] unrecognized trailing content in grades-only line: {line!r}")

        job = {
            "astral_job_id": batch_entities[pos]["astral_job_id"],
            "grades": [{"vector": seg[:2], "grade": seg[2]} for seg in grades],
        }
        if with_meta:
            for i, key in enumerate(("company_job_id", "job_title", "job_link")):
                if i < len(meta):
                    job[key] = meta[i] or None
            # key:value extras → job_data dict (location, salary_range, company name, etc.)
            if meta[3:]:
                job["job_data"] = {
                    k.strip(): (v.strip() or None)
                    for field in meta[3:] if ":" in field
                    for k, v in [field.split(":", 1)]
                }

        result_jobs.append(job)

    return {"jobs": result_jobs}
```

### Wire into `do_task` — decode first, validate schema after

For encoded tasks, skip raw payload schema validation (it's a string, not a dict). Hydrate first,
then validate the assembled result against `response_schema` so the pieces got reassembled correctly.

```python
output_type = task_config.get("output_type", "")

if "_encoded" in output_type and parsed is not None:
    parsed = _decode_payload(task_key, output_type, parsed, ctx)
    result["parsed_response"] = parsed
    schema_error = _validate_response_schema(task_key, parsed, task_config)
    if schema_error:
        return {**result, "success": False, "error": schema_error}
```

---

## Step 3 — `src/core/consult.py`

### Add `batch_entities` to task ctx

```python
task_ctx = {**ctx, "batch_size": len(jobs), "batch_entities": jobs} if ctx else \
           {"batch_size": len(jobs), "batch_entities": jobs}
```

### Remove output_type decode block and `hydrate_response` import

`do_task` now returns a fully decoded `response_schema` shape. `_run_batch_consult` reads
`result["parsed_response"]["jobs"]` directly — no local hydration step.

---

## Step 3b — `src/core/tracker.py`

### Flatten `job_data` dict in `initialize_job`

`_decode_payload` packs dynamic extras into `job_data: {}` on the response job.
`initialize_job`'s current pass-through would nest that as `{"job_data": {...}}` in the DB
column. One line fix — flatten it before saving:

```python
metadata = {k: v for k, v in parsed_job.items() if k not in _JOB_COLUMN_FIELDS and k not in ("astral_job_id", "grades")}
# Flatten nested job_data dict so extras merge cleanly into the job_data DB column
if isinstance(metadata.get("job_data"), dict):
    metadata.update(metadata.pop("job_data"))
```

---

## Step 4 — `src/core/dispatcher.py`

Move `monitor.auto_run_error()` from after the `finally` block to inside it, between
`flush_log_buffer()` and `log_batch_id.set(None)`. Monitor logs currently fall outside the
batch's `log_batch_id` context and are invisible in the batch log view.

```python
finally:
    ...
    flush_log_buffer()
    # Call while log_batch_id still set — monitor logs appear in the batch log view
    if not is_click and accumulated.get("total_errors", 0) > 0:
        monitor.auto_run_error(task_key, batch_id, accumulated, final_status)
    log_batch_id.set(None)
    ...
```

Remove the duplicate monitor call that currently follows the `finally` block.

---

## Files Changed

| File | Action | What |
|------|--------|------|
| `src/utils/config.py` | MODIFY | Add `grades_json`, `grades_encoded`, `grades_encoded_meta` to `output_types`; rename `instructions` → `payload_instructions`; remove `qualify_job_output` and `evaluate_jd_output`; update `TOKEN_SOURCES["OUTPUT_INSTRUCTIONS"]` field; update `output_type` + add `response_schema` on both tasks; `int` branch in `_schema_to_example` |
| `src/core/agent.py` | MODIFY | Add `_GRADE_SEG` (built from config) + `_decode_payload`; wire into `do_task` with decode-then-validate order; delete `_parse_grade_segment`, `_parse_grade_meta_line`, `_hydrate_grade_meta`, `hydrate_response` |
| `src/core/consult.py` | MODIFY | Add `batch_entities` to ctx; remove decode block + `hydrate_response` import |
| `src/core/tracker.py` | MODIFY | `initialize_job`: flatten nested `job_data` dict into metadata before DB save |
| `src/core/dispatcher.py` | MODIFY | Move `monitor.auto_run_error()` inside `finally` before `log_batch_id.set(None)` |

---

## Code Rules Review

| Rule | Check |
|------|-------|
| **Layer rules** | All changes within existing layers. No new cross-layer imports. |
| **Config as source of truth** | `output_types` in `ASTRAL_CONFIG` owns format definitions. `response_schema` in `TASK_CONFIG` owns the downstream contract. |
| **DRY** | Three tasks can share `grades_encoded`/`grades_encoded_meta` — no per-task instruction strings. Four pipe-parser functions → one `_decode_payload`. |
| **do_task pattern** | `do_task` remains the single AI entry point. Hydration is internal — callers receive `response_schema` shape and are unaware of encoding. |
| **No heuristics/limits** | No truncation, no depth limits. All lines processed. |
| **Error handling** | `_decode_payload` raises on malformed data; `do_task` catches → `{"success": False}`; `_run_batch_consult` transitions to `error_state`. |

---

## Review

**Commit:** `0e1d790dc7890870e3cd1c8e9128efc6000f5db0`
**Branch:** `dev`
**Reviewed:** 2026-04-23

---

## What's Solid

- **Plan fidelity is high.** All five steps are implemented and match the spec. Output-type registry, `_decode_payload`, `do_task` wiring, `consult.py` cleanup, `tracker.py` flattening, and the dispatcher monitor move — all present and correct.
- **`_decode_payload` is cleaner than what it replaced.** Four functions collapsed to one, rubric coupling eliminated, grade segments auto-detected via regex instead of positional indexing against rubric labels. Significantly less brittle.
- **`_GRADE_SEG` built from config.** `valid_grades` is the single source of truth for grade letters — the regex stays in sync automatically. Good pattern.
- **Decode-then-validate order is correct.** Early schema validation for encoded tasks passes through (string payload → no-op), decode runs, then the assembled dict is validated against `response_schema`. The fallback in `_validate_response_schema` (`perf = parsed; payload = parsed` when neither envelope key is present) handles the decoded shape correctly without requiring a special code path.
- **`confidence_levels` removed cleanly.** Not in the plan, but it was dead weight once `_parse_grade_segment` went. Good housekeeping.
- **Dispatcher monitor fix is tight.** Moving `auto_run_error` inside `finally` before `log_batch_id.set(None)` is the right fix — one line move, duplicate call removed, no regressions.
- **Layer rules clean.** No new cross-layer imports introduced. `hydrate_response` correctly removed from both `agent.py` (definition) and `consult.py` (import + call sites).

---

## Issues

### Issue 1 — Stale comment in `consult.py` references deleted function ℹ️ advisory

In `qualify_job_listings`, the `assemble()` inner function has this comment:

```python
# 0-based numbered format — astral_job_id is intentionally excluded from live content
# so the agent can't echo it back; position mapping is handled in _hydrate_grade_meta.
```

`_hydrate_grade_meta` is gone. Position mapping now happens in `_decode_payload`. One-liner fix.

---

### Issue 2 — `_validate_response_schema` has no `dict` type branch ℹ️ advisory

`_schema_to_example` handles `"dict"` type correctly (added alongside `"object"` in this commit). But `_validate_response_schema` has no corresponding branch — only `"object"` is validated:

```python
if type_spec == "object" and not isinstance(val, dict):
    return f"Field '{field_name}' must be object, got {type(val).__name__}"
```

The `qualify_job_listings` response schema has `"job_data": {"type": "dict", "required": False}`. If the AI somehow returned a non-dict `job_data`, the validator would silently accept it. In practice, `_decode_payload` always emits `job_data` as a proper dict (from `key:value` extras parsing), or omits it entirely — so this isn't a live bug. But the inconsistency between `_schema_to_example` and `_validate_response_schema` will bite the next person who adds a `"dict"` typed required field.

Fix: add `elif type_spec == "dict" and not isinstance(val, dict)` to the validator, parallel to the `"object"` branch.

---

### Issue 3 — `grades_json` output type is dead code ℹ️ advisory

`grades_json` is added to `ASTRAL_CONFIG["output_types"]` with `payload_instructions`, but no task in `TASK_CONFIG` uses `output_type: "grades_json"`. The docblock in `output_types` says it's for `grade_do`, etc. — but those tasks use standard JSON response schema today and don't reference this key.

Not harmful — it's a pre-wired hook for a future migration. Just worth knowing it's aspirational, not functional today.

---

## Recommended Actions

| # | Severity | Action |
|---|----------|--------|
| 1 | Advisory | Fix stale comment in `consult.py` `assemble()` — replace `_hydrate_grade_meta` reference with `_decode_payload` |
| 2 | Advisory | Add `"dict"` type branch to `_validate_response_schema`, parallel to the existing `"object"` branch |
| 3 | Advisory | Annotate `grades_json` in config as "reserved for future use" or remove until a task needs it |

---

## Resolution

- **Issue 1**: Fixed — updated stale comment in `consult.py` `assemble()` to reference `_decode_payload` instead of `_hydrate_grade_meta`.
- **Issue 2**: Fixed — added `"dict"` to the `"object"` type check in `_validate_response_schema` (`type_spec in ("object", "dict")`), covering the `job_data` field in `qualify_job_listings` response schema.
- **Issue 3**: Annotated `grades_json` in config as "reserved for future use — no task uses this key today."
