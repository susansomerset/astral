<!-- linear-archive: AST-336 archived 2026-06-03 -->

## Linear archive (AST-336)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-336/update-astral-agent-for-minimal-output  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-345

### Description

For the initial stages of job analysis, we want to minimize the cost per job evaluation.  This can be accomplished by instructing the agent to respond with encoded content, so a JSON with grades vectors turns into "1-ABBD" or "93-A15B13B27D04"

The logic is:
We pass up input in a finite array of jobs, and the results would identify:

for "grade_only" task_key.output_type
<array_position>-<vector_0_grade><vector_1_grade><vector_2_grade>…<vector_N_grade>

for "grade_reason" task_key.output_type
<array_position>-<vector_0_grade><vector_0_reason_code><vector_1_grade><vector_1_reason_code><vector_2_grade><vector_2_reason_code>…<vector_N_grade><vector_N_reason_code>

for "grade_notes" task_key.output_type
<array_position>-<vector_0_grade><vector_0_notes><vector_1_grade><vector_1_notes><vector_2_grade><vector_2_notes>…<vector_N_grade><vector_N_notes>

Then Agent would receive the abbreviated output and create a fully formed JSON output JSON for the array passed to populate the data.

Anatomy of my wildcards:
\[array_position\] means the numerical, 0-based position of the job item.  not astral_job_id or company_job_id, just the reference to the position of the array.  Instructions will require there be a grade-stub for every array.

\[vector_N\_\*\] means that Agent does not know or care how many vectors to expect for the prompt, it is driven by the candidate's artifacts.

\[grade_only\] means just a single letter character in the position of the vector order, so "ABBD" means four vectors total, with an "A" for Vector 0, a "B" for Vectors 1 and 2, and a "D" for Vector 3.

\[grade_notes\] means a letter with a natural language explanation from Sonnet/Opus to explain why the grade was given. These are used further down the funnel where the volume is much more manageable.

\[grade_reason\] means a letter and a two-digit code selected from a library of options provided in the prompt, so that some anticipated context can be provided, for example, the job_description_reason_codes might look like:
10:"Lots of deep industry knowledge required"
15:"Graduate Degree explicitly required"
25:"Salary too low"
37:"Ping-pong tables mentioned"

Like "TITLE_PATTERNS", "REASON_CODES" will be candidate-specific (one man's ping-pong table is another man's … something), so we will add it to the candidate_data.profile as a string in the same manner as TITLE_PATTERNS.

### Comments

_No comments._

---

# AST-336 Update Astral Agent for Minimal Output

## Plan

### Context

Currently, Agent responses return full JSON structures for all evaluations. For initial job analysis stages (especially batch operations like `qualify_job_listings`), we want to reduce token costs by having the Agent return abbreviated codes instead of verbose JSON, then decompress those codes back to full structures before storage.

The abbreviated format is a transmission optimization only—the database always receives complete JSON as today.

### Design Decisions

**D1 — Abbreviated format is internal only.** The Agent receives instructions to output abbreviated codes (e.g., "01-ABBD" for grade_only), but the database stores full JSON. Decompression happens in `agent.py` before schema validation and storage.

**D2 — Three output formats.** Tasks can request one of three formats:
- `grade_only`: Position and letters only, e.g., "01-ABBD" (4 vectors)
- `grade_reason`: Position, letters, and 2-digit reason codes, e.g., "01-A10B15B27D04"
- `grade_notes`: Position, letters, and natural language notes from Agent, e.g., "01-A(Strong fit)B(Adequate)"
- `natural`: No special formatting (default for non-grading tasks)

**D3 — Single shared REASON_CODES per candidate.** Unlike output types which vary per task, reason codes are a single candidate-level library (location: `candidate_data.profile.reason_codes`). The reason code values are context-specific but the keys (two-digit codes) are stable within a candidate's profile.

**D4 — Output type is task-level config.** Each task in `agent_task` table (or TASK_CONFIG) carries an `output_type` field. Tasks default to `natural` (no abbreviation). Prompt instructions are injected based on this field.

**D5 — Decompression failure → ERROR state for batch.** If abbreviated output parsing fails, the malformed response string is stored for audit, and all jobs in that batch for that task_key transition to ERROR state.

**D6 — Instructions injected during prompt assembly.** Output type instructions live in `AGENT_CONFIG["output_types"]` and are appended to prompts during `do_task()` execution (in nocache_content so they're not cached).

---

### Step 1: Add REASON_CODES to TOKEN_SOURCES

**File:** `src/utils/config.py` (around line 1192, after TITLE_PATTERNS)

**Change:** Add new token source:
```python
"REASON_CODES":         {"source": "candidate", "path": "profile.reason_codes"},
```

This allows prompts to reference `{$REASON_CODES}` and receive the candidate's reason code library (a JSON string like `{"10": "Lots of deep industry knowledge required", "15": "Graduate Degree required"}`).

---

### Step 2: Add Output Type Instructions to AGENT_CONFIG

**File:** `src/utils/config.py` (after AGENT_CONFIG model definitions, after line 896)

**Change:** Add new section with output type instructions:
```python
# Output type instructions for abbreviated Agent responses.
# Injected into prompts based on task's output_type field.
"output_types": {
    "natural": "",  # No special formatting
    "grade_only": (
        "Format your response as abbreviated codes: {array_position}-{grades}\n"
        "Where {array_position} is the 0-based position of the job in the input array (zero-padded to 2 digits),\n"
        "and {grades} is a sequence of single-letter grades in vector order.\n"
        "Example: 01-ABBD means position 1 with grades A, B, B, D for vectors 0, 1, 2, 3."
    ),
    "grade_reason": (
        "Format your response as abbreviated codes: {array_position}-{grades_and_codes}\n"
        "Where {array_position} is the 0-based position of the job in the input array (zero-padded to 2 digits),\n"
        "and {grades_and_codes} is a sequence of grade letters followed by 2-digit reason codes.\n"
        "The reason codes are from this library:\n{$REASON_CODES}\n"
        "Example: 01-A10B15B27D04 means position 1 with grade A (code 10), B (code 15), B (code 27), D (code 04)."
    ),
    "grade_notes": (
        "Format your response as abbreviated codes: {array_position}-{grades_and_notes}\n"
        "Where {array_position} is the 0-based position of the job in the input array (zero-padded to 2 digits),\n"
        "and {grades_and_notes} is a sequence of grade letters followed by natural language explanations in double quotes.\n"
        "Example: 01-A\"Strong technical fit\"B\"Acceptable compensation\"D\"Remote policy mismatch\""
    ),
}
```

---

### Step 3: Create _decompress_abbreviated_response() Helper

**File:** `src/core/agent.py` (new function, before do_task)

**Change:** Add decompression helper:
```python
def _decompress_abbreviated_response(
    response_text: str,
    template: Dict[str, Any],
    vectors: List[Dict[str, Any]],
    output_type: str,
    reason_codes: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Decompress abbreviated Agent response back into full JSON template.
    
    Args:
        response_text: Abbreviated response from Agent (e.g., "01-ABBD" or "01-A10B15B")
        template: Response schema template (e.g., {"jobs": [{...}, {...}]})
        vectors: List of vector dicts with "name" field (from TASK_CONFIG)
        output_type: One of "grade_only", "grade_reason", "grade_notes"
        reason_codes: Dict mapping 2-digit codes to reason strings (for grade_reason only)
    
    Returns: Fully populated template with grades filled in for the specified array position
    
    Raises: ValueError if response cannot be parsed
    """
    response_text = response_text.strip()
    
    # Parse array_position and grades sequence
    if "-" not in response_text:
        raise ValueError(f"Abbreviated response missing '-' separator: {response_text!r}")
    
    parts = response_text.split("-", 1)
    try:
        array_pos = int(parts[0])
    except ValueError:
        raise ValueError(f"Invalid array position (must be integer): {parts[0]!r}")
    
    codes_str = parts[1]
    
    # Decompress based on output_type
    if output_type == "grade_only":
        grades = _decompress_grade_only(codes_str, vectors)
    elif output_type == "grade_reason":
        if not reason_codes:
            raise ValueError("grade_reason requires reason_codes dict")
        grades = _decompress_grade_reason(codes_str, vectors, reason_codes)
    elif output_type == "grade_notes":
        grades = _decompress_grade_notes(codes_str, vectors)
    else:
        raise ValueError(f"Unknown output_type: {output_type!r}")
    
    # Populate template at array_pos
    result = json.loads(json.dumps(template))  # Deep copy
    
    # Find the array field in template (typically "jobs" for batch tasks)
    for key, val in result.items():
        if isinstance(val, list) and val:
            if array_pos >= len(val):
                raise ValueError(f"Array position {array_pos} out of bounds (array has {len(val)} items)")
            val[array_pos]["grades"] = grades
            break
    
    return result


def _decompress_grade_only(codes_str: str, vectors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parse grade-only format: ABBD → [{"vector": "V0", "grade": "A"}, ...]"""
    if len(codes_str) != len(vectors):
        raise ValueError(
            f"grade_only expects {len(vectors)} letters (one per vector), "
            f"got {len(codes_str)}: {codes_str!r}"
        )
    grades = []
    for i, letter in enumerate(codes_str):
        if letter not in VALID_GRADES:
            raise ValueError(f"Invalid grade '{letter}' at position {i} (must be in {sorted(VALID_GRADES)})")
        grades.append({"vector": vectors[i]["name"], "grade": letter})
    return grades


def _decompress_grade_reason(
    codes_str: str,
    vectors: List[Dict[str, Any]],
    reason_codes: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Parse grade+reason format: A10B15B27 → [{"vector": "V0", "grade": "A", "reason": "..."}, ...]"""
    if len(codes_str) % 3 != 0:
        raise ValueError(
            f"grade_reason expects 3 chars per vector (letter + 2-digit code), "
            f"got {len(codes_str)} chars (not divisible by 3): {codes_str!r}"
        )
    num_grades = len(codes_str) // 3
    if num_grades != len(vectors):
        raise ValueError(
            f"grade_reason has {num_grades} grades but expected {len(vectors)} "
            f"(one per vector)"
        )
    
    grades = []
    for i in range(num_grades):
        grade_letter = codes_str[i * 3]
        reason_code = codes_str[i * 3 + 1:i * 3 + 3]
        
        if grade_letter not in VALID_GRADES:
            raise ValueError(f"Invalid grade '{grade_letter}' at position {i}")
        if reason_code not in reason_codes:
            raise ValueError(f"Reason code '{reason_code}' at position {i} not in library")
        
        grades.append({
            "vector": vectors[i]["name"],
            "grade": grade_letter,
            "reason": reason_codes[reason_code],
        })
    return grades


def _decompress_grade_notes(codes_str: str, vectors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parse grade+notes format: A"Strong fit"B"OK experience" → [{"vector": "V0", "grade": "A", "reason": "Strong fit"}, ...]"""
    grades = []
    pos = 0
    
    for i in range(len(vectors)):
        if pos >= len(codes_str):
            raise ValueError(f"Unexpected end of codes_str at vector {i}")
        
        grade_letter = codes_str[pos]
        if grade_letter not in VALID_GRADES:
            raise ValueError(f"Invalid grade '{grade_letter}' at vector {i}")
        pos += 1
        
        if pos >= len(codes_str) or codes_str[pos] != '"':
            raise ValueError(f"Expected quoted note after grade at vector {i}")
        pos += 1
        
        note_end = codes_str.find('"', pos)
        if note_end == -1:
            raise ValueError(f"Unclosed quote in notes for vector {i}")
        
        note_text = codes_str[pos:note_end]
        pos = note_end + 1
        
        grades.append({
            "vector": vectors[i]["name"],
            "grade": grade_letter,
            "reason": note_text,
        })
    
    if pos != len(codes_str):
        raise ValueError(f"Extra characters after final note: {codes_str[pos:]!r}")
    
    return grades
```

---

### Step 4: Inject Output Instructions into Prompts

**File:** `src/core/agent.py` in `do_task()` function

**Location:** After line 371 (after resolving nocache_content token)

**Change:** Add output type instruction injection:
```python
    # Inject abbreviated output instructions if configured
    output_type = task_config.get("output_type", "natural")
    if output_type != "natural":
        output_instructions = AGENT_CONFIG.get("output_types", {}).get(output_type, "")
        if output_instructions:
            # For grade_reason, substitute REASON_CODES token
            if output_type == "grade_reason":
                reason_codes_token = resolve_tokens("{$REASON_CODES}", cd, task_key)
                output_instructions = output_instructions.replace("{$REASON_CODES}", reason_codes_token)
            
            # Append to nocache_content so instructions aren't cached
            nocache_content = (nocache_content or "") + "\n\n" + output_instructions
```

Also update imports at top of agent.py to include:
```python
from src.utils.config import (
    TASK_CONFIG, BASE_SCHEMA, BLOCK_TYPES, AGENT_CONFIG,  # Add AGENT_CONFIG
    resolve_tokens, get_model, CHARS_PER_TOKEN,
)
```

---

### Step 5: Integrate Decompression into Response Handling

**File:** `src/core/agent.py` in `do_task()` function

**Location:** After line 442 (after parsed_response is extracted from result)

**Change:** Add decompression call before schema validation:
```python
    # Decompress abbreviated response if configured
    output_type = task_config.get("output_type", "natural")
    if output_type != "natural" and parsed is not None:
        try:
            vectors = task_config.get("vectors", [])
            reason_codes = None
            if output_type == "grade_reason":
                reason_codes_str = cd.get("reason_codes", "{}")
                try:
                    reason_codes = json.loads(reason_codes_str) if isinstance(reason_codes_str, str) else reason_codes_str
                except json.JSONDecodeError:
                    raise ValueError(f"Invalid reason_codes JSON: {reason_codes_str!r}")
            
            parsed = _decompress_abbreviated_response(
                response_text=parsed if isinstance(parsed, str) else json.dumps(parsed),
                template=schema,
                vectors=vectors,
                output_type=output_type,
                reason_codes=reason_codes,
            )
            result["parsed_response"] = parsed
        except Exception as decomp_err:
            raw_text = None
            api_resp = result.get("api_response")
            if api_resp and hasattr(api_resp, "content") and api_resp.content:
                raw_text = getattr(api_resp.content[0], "text", None)
            logger.error("do_task decompression failed. task_key=%r error=%s", task_key, decomp_err)
            _store_agent_response(task_config, task_key, index, raw_text or parsed, None, result)
            return {
                "success": False,
                "api_response": result.get("api_response"),
                "parsed_response": None,
                "error": str(decomp_err),
                "raw_response": parsed,
                "timesheet": result.get("timesheet", {}),
            }
```

---

### Step 6: Add output_type to TASK_CONFIG Tasks (Future)

**File:** `src/utils/config.py` in TASK_CONFIG definitions

**Change:** For tasks that should use abbreviated output, add field:
```python
"output_type": "grade_only",  # or "grade_reason", "grade_notes"
```

Initial tasks for this feature:
- `qualify_job_listings`: `output_type: "grade_only"`
- `evaluate_jd`: `output_type: "grade_reason"`
- `grade_do`, `grade_get`, `grade_like`: `output_type: "grade_notes"`

Default for all other tasks: `output_type: "natural"` (no abbreviation)

---

## Files Changed

| File | Changes |
|------|---------|
| `src/utils/config.py` | Add REASON_CODES to TOKEN_SOURCES; add AGENT_CONFIG_OUTPUT_TYPES dict with instruction templates |
| `src/core/agent.py` | Add _decompress_abbreviated_response() and helper functions (_decompress_grade_only, _decompress_grade_reason, _decompress_grade_notes); add output_type instruction injection in do_task(); integrate decompression before schema validation; update imports |

---

## Review

**Commit:** `406fbe2cbf8e408cc1f85d4c0f062843231688b2`
**Branch:** `dev`
**Reviewed:** 2026-03-22

---

## What's Solid

- Clean separation of concerns: config holds instruction templates, agent.py holds decompression logic, prompt injection is in the right place (nocache_content).
- Three format-specific parsers are well-structured with clear error messages and tight validation — every malformed input is caught with a descriptive ValueError.
- The `grade_notes` parser handles the tricky quoted-string format correctly, including unclosed quote and trailing character detection.
- Backward compatible by default: `output_type` defaults to `"natural"`, and no TASK_CONFIG entries use abbreviated output yet, so nothing changes for existing tasks.
- Error path stores the raw response for audit before returning failure — good for debugging AI misbehavior.
- REASON_CODES TOKEN_SOURCES entry follows the established pattern exactly.

---

## Issues

### Issue 1 — Template vs Schema mismatch in `_decompress_abbreviated_response` ⚠️ required

The function receives `schema` (the task's `response_schema`) as the `template` parameter (line 622–623 of agent.py, calling with `template=schema`). But `response_schema` is a *validation* schema — it contains field specs like `{"task_success": {"type": "bool", "required": True}, "grades": {"type": "list", ...}}`. It is not a data template with actual arrays of job objects.

The decompression function deep-copies this schema and then iterates looking for a list field (`if isinstance(val, list) and val`). Since the schema values are dicts (field specs), not lists, the loop will never find a list, grades are never populated, and the function returns the raw validation schema object as if it were the decompressed response. This then passes to `_validate_response_schema`, which will either reject it or produce garbage.

**Root cause:** The plan says "template: Response schema template (e.g., {"jobs": [{...}, {...}]})" — this implies a *data structure* template, not the validation schema. The code conflates the two.

**Options:**
1. Build a real data template from the schema + vectors at decompression time (dynamically construct the expected output shape).
2. Add a `response_template` field to TASK_CONFIG for abbreviated tasks that provides the target data structure.
3. Skip the template approach entirely — have `_decompress_abbreviated_response` return a flat `{"grades": [...]}` dict that the caller merges into position.

**Recommendation:** Option 3 is simplest and most robust. The decompression function shouldn't need to know the shape of the full response — it just needs to produce the grades array, and the caller can place it.

### Issue 2 — `response_format` tension with abbreviated output 🔧 fix now

The abbreviated output formats (`grade_only`, `grade_reason`, `grade_notes`) instruct the Agent to return compact text codes like `"01-ABBD"`. But the decompression guard (line 611) checks `response_format in ("json", "python")`. When `response_format` is `"json"`, Anthropic will attempt to parse the Agent's output as JSON — and `"01-ABBD"` is not valid JSON.

Either:
- The Agent returns raw text and `response_format` should be `"text"` for abbreviated tasks (but then the guard skips decompression).
- Or the Agent wraps the abbreviated code in a JSON envelope like `{"abbreviated": "01-ABBD"}` (but then the prompt instructions need updating).

This is a design gap — the format the Agent is told to produce doesn't match the format the pipeline expects to receive.

**Recommendation:** For abbreviated tasks, `response_format` should likely be `"text"`, and the decompression guard should check `output_type != "natural"` without also gating on `response_format`. Or define a new response_format value that signals "text input, JSON output after decompression."

### Issue 3 — `output_type` read twice in `do_task()` ℹ️ advisory

`output_type = task_config.get("output_type", "natural")` appears at line 526 and again at line 610. Same value, same source. The second read shadows the first. Harmless but unnecessary — just reuse the variable from line 526.

### Issue 4 — Plan says `AGENT_CONFIG["output_types"]`, code uses `AGENT_CONFIG_OUTPUT_TYPES` ℹ️ advisory

The plan (Step 2) specifies output type instructions as a nested key inside `AGENT_CONFIG`:
```python
AGENT_CONFIG["output_types"] = { ... }
```

The implementation creates a separate top-level dict `AGENT_CONFIG_OUTPUT_TYPES`. This is arguably fine (maybe better — keeps AGENT_CONFIG focused on model definitions), but it diverges from the plan and from the ASTRAL_CODE_RULES pattern that `AGENT_CONFIG` is the home for agent configuration. The plan also references it as `AGENT_CONFIG.get("output_types", {})` in the code snippets but the implementation uses `AGENT_CONFIG_OUTPUT_TYPES.get(...)`.

Not a bug, but worth noting the intentional deviation so the plan doesn't mislead future readers.

### Issue 5 — `reason_codes` sourced from `cd` directly, not through TOKEN_SOURCES ℹ️ advisory

The decompression block (line 616) reads reason codes via `cd.get("reason_codes", "{}")`, pulling from the flat candidate_data dict. But the plan (D3) says reason codes live at `candidate_data.profile.reason_codes`, and Step 1 adds a TOKEN_SOURCES entry for nested path resolution: `"REASON_CODES": {"source": "candidate", "path": "profile.reason_codes"}`.

The prompt injection correctly uses `resolve_tokens("{$REASON_CODES}", cd, task_key)` which traverses the nested path. But the decompression code does a flat `cd.get("reason_codes")` — these are different lookups. If `cd` is a nested dict (which it is, per TOKEN_SOURCES path conventions), `cd.get("reason_codes")` will return `None` and fall back to `"{}"`, producing an empty reason_codes dict. The decompression will then fail with "Reason code 'XX' not in library."

**Recommendation:** Use `resolve_tokens` or manually traverse `cd["profile"]["reason_codes"]` to match the TOKEN_SOURCES path.

---

## Recommended Actions
| # | Severity | Action |
|---|----------|--------|
| 1 | Fix now | `_decompress_abbreviated_response` receives validation schema, not data template — will produce garbage output when activated. Rethink the template approach or return flat grades and let caller place them. |
| 2 | Fix now | Abbreviated text output (`"01-ABBD"`) will fail JSON parsing when `response_format` is `"json"`. Reconcile the response_format with abbreviated output expectations. |
| 3 | Advisory | Remove duplicate `output_type` read at line 610 — reuse the variable from line 526. |
| 4 | Advisory | Note plan deviation: `AGENT_CONFIG_OUTPUT_TYPES` vs planned `AGENT_CONFIG["output_types"]`. Update plan or code for consistency. |
| 5 | Fix now | `cd.get("reason_codes")` does a flat lookup but the data lives at `profile.reason_codes` (nested). Use the same path resolution as TOKEN_SOURCES. |

---

## Resolution

### Fixes Applied

All three critical issues have been addressed:

#### Fix 1 — Template/Schema Mismatch (Issue 1)

**Problem:** `_decompress_abbreviated_response` was receiving a validation schema (field specs) instead of a data template, so it couldn't find array fields to populate.

**Solution:** Changed return type from full template to `(array_position, grades)` tuple. The decompression function now only parses the abbreviated codes and returns the grades list. The caller in `do_task()` is responsible for placing grades into the actual response structure.

**Code change in agent.py:**
- Simplified function signature to not take `template` parameter
- Returns `tuple(int, List[Dict])` instead of `Dict[str, Any]`
- Caller in do_task() handles placement into response structure

#### Fix 2 — Response Format Tension (Issue 2)

**Problem:** Abbreviated tasks instruct Agent to output raw text codes like `"01-ABBD"`, but decompression guard checked `response_format in ("json", "python")`. Anthropic would try to parse the text as JSON and fail.

**Solution:** Changed decompression guard to require `response_format == "text"`. For abbreviated output tasks:
- Prompt instructs Agent to output abbreviated codes as plain text
- `response_format` must be `"text"` (not JSON)
- Decompression happens in do_task before schema validation
- Full JSON is reconstructed and stored as usual

**Code change in agent.py line 598:**
- Changed: `if output_type != "natural" and parsed is not None and response_format in ("json", "python"):`
- To: `if output_type != "natural" and parsed is not None and response_format == "text":`

#### Fix 3 — Reason Codes Path Mismatch (Issue 5)

**Problem:** Decompression code did flat lookup `cd.get("reason_codes")` but data lives at nested path `profile.reason_codes` (per TOKEN_SOURCES definition).

**Solution:** Changed to use nested path traversal matching TOKEN_SOURCES:

**Code change in agent.py line 603:**
- Changed: `reason_codes_str = cd.get("reason_codes", "{}")`
- To: `reason_codes_str = cd.get("profile", {}).get("reason_codes", "{}")`

### Additional Improvements

**Advisory 3 (duplicate output_type read):** Removed duplicate by reusing variable from line 526.

**Advisory 4 (config structure deviation):** Documented that `AGENT_CONFIG_OUTPUT_TYPES` is intentionally separate from `AGENT_CONFIG` to keep model pricing config distinct from task instruction templates.

### Updated Task Requirements

For abbreviated tasks to work correctly, TASK_CONFIG entries must specify **both**:

1. `"output_type": "grade_only" | "grade_reason" | "grade_notes"`
2. `"response_format": "text"` — CRITICAL: must be "text", not "json"

Example:
```python
"qualify_job_listings": {
    # ... existing fields ...
    "output_type": "grade_only",
    "response_format": "text",  # ← MUST be "text" for abbreviated output
},
```

### Testing

All fixes verified:
- Decompression functions return correct (array_pos, grades) tuple
- Response format constraint enforced  
- Nested reason_codes lookup matches TOKEN_SOURCES pattern
- Code compiles without syntax errors

### Status

**Code now functional.** All critical issues resolved. Infrastructure ready for Step 6 (configuring actual TASK_CONFIG entries with abbreviated output_types).