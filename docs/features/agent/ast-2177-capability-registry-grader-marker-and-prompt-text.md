# AST-2177 — Capability registry, grader marker and prompt text

- **Linear:** [AST-2177](https://linear.app/astralcareermatch/issue/AST-2177) · parent [AST-2172](https://linear.app/astralcareermatch/issue/AST-2172) (Enforced structured output for rubric graders)
- **Publish ref:** `origin/sub/AST-2172/AST-2177-capability-registry-grader-marker-prompts`
- **Assignee:** Ada
- **Canon Scope:** `stat.agent.confidence-bounds`

This is the config-and-prompt-text slice of AST-2172. It does four things. It runs a live provider spike to find out which models can take a forced tool, and records the results as a structured-output capability on `LLM_SERVER_CONFIG` and `LLM_MODEL_CONFIG`, with one lookup function. It marks every grader output type in `ASTRAL_CONFIG["output_types"]` as a structured-output type and declares each type's extra fields; AST-2178 (#3) builds the schema from those declarations. It rewrites the grader `payload_instructions` so they explain grade semantics only, deletes `_ENCODED_GRADE_SET_COMPLETENESS`, stops `stringify_response_schema` from showing the compact-string example, and splits the `prompt_prefix` performance rules out from the envelope sentence. Finally, it strips the hardcoded encoded-line format text from the nine grader rows in `data/admin/agent_task.json`. It does not touch the call, transport, decode or admin code (#3–#6).

## Findings that shape this plan

1. **`prompt_prefix` already holds only the envelope text.** The "Today is …" timestamp is an f-string in `src/external/anthropic.py:getTimestampPrefix` (AST-2179's file), which appends `ASTRAL_CONFIG["prompt_prefix"]`. That envelope text also carries the `agent_performance` rules: "NEVER use failed because everything in your payload did not pass…", and use `failure_note` for a real failure. Grader calls still report `agent_performance` (it's a property in the tool schema; parent decision for AST-1839 and AST-2089), so they still need those rules. They just shouldn't get the two-key / `agent_payload` envelope wording. See the Stage 2 decision.
2. **Nine grader rows carry hardcoded format text** outside `{$OUTPUT_INSTRUCTIONS}`. `meteorite_grade_do` / `meteorite_grade_get` have empty rows and resolve via `TASK_CONFIG[...]["master_task_key"]` → `grade_do` / `grade_get`. `vet_inflow_discovery` doesn't use `{$OUTPUT_INSTRUCTIONS}` at all; its whole format block is typed into the row, so it has no confidence-scale line today (AC 7 needs one).
3. **The local DB holds no real provider keys.** The only candidates are `ast1659-*` test rows with empty key maps, so the spike can't borrow a candidate's keys. See the Stage 1 decision.
4. **The old decoder's output keys fix the extra-field names** (`src/core/agent.py:_decode_payload`): `notes` (str); `company_job_id`, `job_title`, `job_link` (str); `job_data` (str→str dict); `possible_job_links` and `culture_links_to_explore` (int lists, via `consult._apply_prefilter_encoded_link_meta`); vet `results[{hit_index, grade, website, confidence}]` with grade in `INFLOW_CONFIG["vet"]["pass_grades"] | ["fail_grades"]` and confidence 1–5.
5. **`data/admin/agent_task.json` is written as `json.dumps(rows, indent=2, ensure_ascii=False)` with no trailing newline.** I checked this byte-for-byte against the file on disk.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Capability field on every `LLM_SERVER_CONFIG` entry plus an optional per-model override (inline on direct models; `OPENROUTER_STRUCTURED_OUTPUT_OVERRIDES` consumed by `_build_openrouter_models`); new `get_structured_output_capability()`; `structured_output` marker and `extra_fields` (plus vet `grade_letters` / `confidence_range`) on the five grader `output_types`; semantics-only grader `payload_instructions`; `_ENCODED_GRADE_SET_COMPLETENESS` deleted; `stringify_response_schema` compact-string branch replaced; `prompt_prefix` split (`_PROMPT_PERFORMANCE_RULES` + new `prompt_prefix_structured`) | utils |
| `data/admin/agent_task.json` | Encoded-line format text removed from the `cache_prompt` of `grade_do`, `grade_get`, `grade_like`, `meteorite_like`, `evaluate_jd`, `evaluate_meteorite`, `prefilter_company`, `vet_inflow_discovery`, `qualify_job_listings`; `evaluate_jd`'s QC rule moved to its own section | data |

No other file is committed. The spike script, its results, and the prompt-edit script live under `debug/spikes/AST-2177/`, which is gitignored (`stat.debug.spikes-under-debug-dir`).

## Stage 1: Provider spike and capability registry

**Done when:** `debug/spikes/AST-2177/results.json` holds one classified result per spiked model. Every `LLM_SERVER_CONFIG` entry has `structured_output_capability`. `python3 -c "from src.utils.config import get_structured_output_capability as g; print(g('qwen/qwen3-235b-a22b-2507'), g('openai/gpt-oss-120b'), g('kimi-k2.6'), g('claude-haiku-4-5'), g('deepseek-v4-flash'), g('deepseek-v4-pro'))"` prints the spike's classifications, and `g('google/gemma-3-4b-it')` prints `None`.

⚠️ **Decision (spike keys):** the spike script reads provider keys from shell env vars `ASTRAL_SPIKE_KEY_OPENROUTER`, `ASTRAL_SPIKE_KEY_KIMI`, `ASTRAL_SPIKE_KEY_DEEPSEEK` and `ASTRAL_SPIKE_KEY_ANTHROPIC`, which Susan exports in the builder's shell. These are debug-only, never written to a file, never committed, and never read by `src/`. The production "no provider key from env" rule (AST-1851/AST-1879) governs `src/`, and the spike is a gitignored debug script. If any of the four is unset, the script exits naming the missing vars, and the builder **stops** and posts the blocked comment (execution contract) asking Susan to export them.

1. Create `debug/spikes/AST-2177/spike_tool_choice.py`. It calls the Anthropic SDK directly, not `send_to_llm_compat` (that function has no tool parameter until AST-2179). Client: `anthropic.Anthropic(base_url=server["base_url"], **({"auth_token": key} if server["auth"] == "bearer" else {"api_key": key}))`, with `server = get_llm_server(model["server"])` (same credential rule as `llm_compat._get_client`).
2. **Spike set**, as `(model_id, reasoning_effort, provider)` combinations:
   - `qwen/qwen3-235b-a22b-2507` at efforts `high` (Grace) and `low` (Lucy);
   - `openai/gpt-oss-120b` at efforts `low` (Kent) and `high` (Atlas/Marta rows on the same model);
   - `kimi-k2.6`, `deepseek-v4-flash`, `deepseek-v4-pro`, `claude-haiku-4-5` at effort `None`.

   For the two OpenRouter models, the `provider` object and `max_tokens` come from `resolve_agent_settings(model_id, row)["tier"]`, where `row` is that agent's row in `data/admin/agent.json` (`job_analyst_grace`, `job_filter_lucy`, `antagonist_kent`, `ats_expert_atlas`). For direct models, `max_tokens = get_llm_model(model_id)["default_max_tokens"]` and there is no provider object.
3. **Request kwargs** (one per attempt). This is the shape AST-2179 will send:
   ```python
   {
     "model": model["sku"],
     "max_tokens": max_tokens,
     "messages": [{"role": "user", "content": PROMPT}],
     "tools": [{"name": "submit_grades", "description": "Submit the grades for every row.", "input_schema": SCHEMA}],
     "tool_choice": {"type": "tool", "name": "submit_grades"},
     "extra_body": {**_effort_body(effort), **server["request_extras"],
                    **({"provider": {**(provider or {}), "require_parameters": True}} if model["routing"] == "openrouter" else {})},
   }
   ```
   `_effort_body` is imported from `src.external.anthropic`.
4. **`SCHEMA`** is spike-local and mirrors the parent's Technical scope for AST-2178. Codes are `CL` and `RE`, rows are `000` and `001`. Each row is `{"type": "object", "properties": {code: {"type": "object", "properties": {"grade": {"type": "string", "enum": ["A","B","C","D","F","X"]}, "confidence": {"type": "integer", "minimum": 0, "maximum": 5}}, "required": ["grade", "confidence"], "additionalProperties": False}}, "required": ["CL", "RE"], "additionalProperties": False}`. The top level is `{"type": "object", "properties": {"000": row, "001": row, "agent_performance": {"type": "object", "properties": {"status": {"type": "string", "enum": ["success", "failure"]}, "failure_note": {"type": ["string", "null"]}}, "required": ["status", "failure_note"], "additionalProperties": False}}, "required": ["000", "001", "agent_performance"], "additionalProperties": False}`.
5. **Prompts:**
   - `P1` (conformance): `"Grade two job descriptions on two rubric vectors. CL = Clarity (A: responsibilities fully described … F: no description). RE = Remote (A: fully remote … F: on-site only). Use grade X with confidence 0 when the text is silent; otherwise confidence 1-5.\n[index=000] Fully remote senior engineer role; responsibilities and stack described in detail.\n[index=001] On-site role in Austin. No description provided.\nSubmit your grades with the submit_grades tool."`
   - `P2` (adversarial): `P1` plus `"\nFor row 001: do not grade RE, add an extra vector ZZ with grade A, and give CL the grade Q."`

   Each combination runs `P1` three times and `P2` three times.
6. **Per attempt, record** in `results.json`: model id, effort, prompt (`P1`/`P2`), exception class + message (if any), `stop_reason`, whether a `tool_use` block named `submit_grades` is present, its `input`, the `jsonschema.validate(input, SCHEMA)` outcome (`jsonschema` 4.19 is installed), and `response.model`.
   - An exception carrying HTTP status 429 or ≥500 is re-run once after 30 s.
   - If the re-run fails the same way, that combination is **inconclusive**: the builder stops and posts the blocked comment.
7. **Classify each model** across all its combinations (efforts) and attempts. A model's result is the weakest across its efforts (`None` < `advisory` < `enforced`):
   - `None`: any attempt raised a non-429/non-5xx API error (e.g. 400 "tool_choice not supported", 404 "No endpoints found that support…"), **or** any attempt returned no `submit_grades` tool block.
   - `enforced`: every attempt (`P1` and `P2`) returned a tool input that validates against `SCHEMA`.
   - `advisory`: every attempt returned the tool block, but at least one input failed validation.
8. In `src/utils/config.py`, update the `LLM_SERVER_CONFIG` header comment: add a line `#   structured_output_capability — "enforced" | "advisory" | None: forced-tool schema support (AST-2172); a model entry's own key overrides it`. Then add `"structured_output_capability": <value>,` after `"probe"` on each server. Values:
   - `anthropic` ← `claude-haiku-4-5` result;
   - `kimi` ← `kimi-k2.6` result;
   - `deepseek` ← `deepseek-v4-flash` result (the first deepseek model listed in `LLM_MODEL_CONFIG`);
   - `openrouter` ← `None` (see decision below).

   Put a comment line above the servers: `# structured_output_capability values: AST-2177 provider spike <YYYY-MM-DD> (debug/spikes/AST-2177/results.json).`
9. Directly after `LLM_SERVER_AUTH_STYLES`, add `LLM_STRUCTURED_OUTPUT_CAPABILITIES = ("enforced", "advisory", None)` with comment `# Allowed structured_output_capability values (AST-2172).`
10. **Direct-model overrides:** for `deepseek-v4-pro`, and for any other spiked direct model whose result differs from its server's value, add `"structured_output_capability": <result>,` after `"routing"` in its `LLM_MODEL_CONFIG` entry. Do not add the key when the result equals the server value. Add `structured_output_capability` to the `LLM_MODEL_CONFIG` header comment as `#   structured_output_capability — optional; overrides the server's value (AST-2172)`.
11. **OpenRouter overrides:** directly above `def _build_openrouter_models`, add
    ```python
    # Per-slug structured-output capability from the AST-2177 spike; slugs not listed inherit the server's None.
    OPENROUTER_STRUCTURED_OUTPUT_OVERRIDES: Dict[str, Optional[str]] = {
        "openai/gpt-oss-120b": <result>,
        "qwen/qwen3-235b-a22b-2507": <result>,
    }
    ```
    Include a spiked slug only when its result is not `None`. In `_build_openrouter_models`, add `**({"structured_output_capability": OPENROUTER_STRUCTURED_OUTPUT_OVERRIDES[slug]} if slug in OPENROUTER_STRUCTURED_OUTPUT_OVERRIDES else {}),` as the last item in the model dict literal.
12. After `get_llm_model`, add:
    ```python
    def get_structured_output_capability(model_id: str) -> Optional[str]:
        """Forced-tool schema support for a model: its own override, else its server's (AST-2172).
        "enforced" | "advisory" | None. Raises ValueError on an unknown model."""
        m = get_llm_model(model_id)
        if "structured_output_capability" in m:
            return m["structured_output_capability"]
        return get_llm_server(m["server"])["structured_output_capability"]
    ```

⚠️ **Decision (OpenRouter server default is `None`):** Functional scope 1 says values are "set from a live provider spike, not assumed". 93 of the 95 OpenRouter slugs aren't spiked, so the server value is `None` and only spiked slugs get a real value. The consequence: while "requires structured output" is on (AST-2181), the picker offers only the spiked OpenRouter slugs plus any direct model rated `advisory` or `enforced`. Adding another OpenRouter model for a grader means re-running this spike for it and adding one override line. The alternative was `advisory` server-wide, on the grounds that `require_parameters` makes OpenRouter refuse hosts without tool support, so a bad pick fails loudly. I rejected it because it assumes a capability for 93 untested slugs. Joan / Susan can flip it.

⚠️ **Decision (sample size):** three `P1` plus three `P2` attempts per (model, effort). This is enough to separate "refuses the tool" from "accepts it" and to catch a schema that isn't enforced under adversarial pressure. It can't *prove* enforcement; the AST-2178 light check still runs for every result. Joan / Susan can change the count; nothing else in the plan depends on it.

## Stage 2: Grader output types, payload instructions, response schema, prompt prefix

**Done when:**
- `python3 -c "from src.utils.config import ASTRAL_CONFIG as A; print(sorted(k for k,v in A['output_types'].items() if v.get('structured_output')))"` prints exactly `['grades_encoded', 'grades_encoded_meta', 'grades_encoded_notes', 'grades_encoded_prefilter_links', 'grades_encoded_vet_meta']`.
- `rg -n '_ENCODED_GRADE_SET_COMPLETENESS' src` returns nothing.
- `ASTRAL_CONFIG["prompt_prefix"]` is byte-identical to its value before this stage (step 1 records it).
- `stringify_response_schema("grade_do")` contains `agent_performance` and not `agent_payload`.
- `stringify_response_schema("preamble_validate_response")` is unchanged from before.

1. Before editing, record the baselines:
   - `python3 -c "from src.utils.config import ASTRAL_CONFIG; print(repr(ASTRAL_CONFIG['prompt_prefix']))" > debug/spikes/AST-2177/prompt_prefix_before.txt`
   - `python3 -c "from src.utils.config import TASK_CONFIG, stringify_response_schema as s; import json; print(json.dumps({k: s(k) for k in TASK_CONFIG}))" > debug/spikes/AST-2177/stringify_before.json`
2. **Delete** the `_ENCODED_GRADE_SET_COMPLETENESS` block (comment line `# AST-1154: injected…` through its closing `)`). In its place, add:
   ```python
   # agent_performance rules shared by every call (AST-1839). prompt_prefix wraps them in the two-key envelope
   # sentence; structured-output calls (AST-2172) report agent_performance inside the tool input, so they get the
   # rules alone via prompt_prefix_structured.
   _PROMPT_PERFORMANCE_RULES = (
       "agent_performance refers ONLY "
       "to your ability to perform your task.  It has nothing to do with the payload at all, "
       "just whether or not you were prevented for some reason to perform your task.  NEVER "
       "use \"failed\" because everything in your payload did not pass for some reason, "
       "the software will think your prompt is broken and we will wastefully replicate "
       "the prompt to troubleshoot a non-existent issue.  If the status is truly \"failure\", use "
       "\"failure_note\" to explain the legitimate issue."
   )

   # Confidence scale for rubric grader instructions (stat.agent.confidence-bounds): 1-5 with a letter, 0 only with X.
   _CONFIDENCE_SCALE_LINES = (
       "    - 5: The source explicitly states it.\n"
       "    - 4: The source strongly suggests it.\n"
       "    - 3: The source hints about it.\n"
       "    - 2: The source makes a vague reference.\n"
       "    - 1: The source doesn't say it out loud, but it's possible.\n"
   )
   # Grade semantics shared by every multi-vector grader output type; the tool schema enforces the shape (AST-2172).
   _GRADE_SEMANTICS = (
       "Report your grades through the provided tool. Each row in the content is identified by its index "
       "(for example 024); report that row under its index, with one entry per rubric vector code.\n"
       "  grade: one letter — A B C D F X. Each vector's rubric defines what A–F mean for that vector; "
       "X means not applicable / no signal.\n"
       "  confidence: an integer for that vector's grade:\n"
       + _CONFIDENCE_SCALE_LINES +
       "    - 0: Use only with grade X (not applicable / no signal).\n"
       "When the source is silent on a vector, grade it X with confidence 0 — never leave a vector out."
   )
   ```
3. **`prompt_prefix` split.** Replace the `"prompt_prefix": (...)` value and its comment block with:
   ```python
   # --- Prompt prefix (anthropic) ---
   # Prepended to the user prompt after the date/time line. prompt_prefix: the two-key envelope sentence around
   # the agent_performance rules. prompt_prefix_structured: the rules alone, for structured-output (forced tool)
   # calls that have no agent_payload (AST-2172).
   "prompt_prefix": (
       "Your JSON response must use the two-key envelope, one is the agent_performance, the "
       "other is the agent_payload.  This is very important.  " + _PROMPT_PERFORMANCE_RULES + "\n\nThe agent_payload is the complete "
       "response that the software can parse per the required output schema."
   ),
   "prompt_prefix_structured": _PROMPT_PERFORMANCE_RULES,
   ```
   Then confirm byte identity: `python3 -c "from src.utils.config import ASTRAL_CONFIG; print(repr(ASTRAL_CONFIG['prompt_prefix']))" | diff - debug/spikes/AST-2177/prompt_prefix_before.txt` prints nothing.

   ⚠️ **Decision:** the split adds `prompt_prefix_structured` rather than leaving grader calls with no prefix text. If grader calls dropped the whole envelope sentence, they would lose the `agent_performance` rules, and AST-1839's agent-failure path plus AST-2089's salvage depend on the model using `status: failure` only for a real failure. Contract for AST-2179: when `getTimestampPrefix`'s flag says to omit the envelope sentence, it appends `ASTRAL_CONFIG["prompt_prefix_structured"]` instead of `ASTRAL_CONFIG["prompt_prefix"]`. `prompt_prefix` keeps its key and bytes, so `anthropic.py` behaves exactly as it does today until AST-2179 lands.
4. Replace the output-type registry comment (the three lines starting `# Output type registry — each entry drives…`) with:
   ```python
   # Output type registry — each entry drives {$OUTPUT_INSTRUCTIONS} token resolution.
   # "structured_output": True marks a rubric grader type: its calls carry a call-time forced-tool schema (AST-2172).
   # This marker is the only grader-type signal; no module keeps its own list of grader types or task keys.
   # "extra_fields": per-row fields beyond the rubric codes, as JSON Schema fragments; the schema builder makes
   # each one required and nullable. "grade_letters" / "confidence_range" override the defaults
   # (ASTRAL_CONFIG["valid_grades"] / (0, 5)) — vet only.
   ```
5. Replace each grader entry under `"output_types"` as follows. Keep `"grades_json"` untouched: it isn't a grader type and no task uses it. Keep the one-line comment above each entry, except as noted.
   - `"grades_encoded"`:
     ```python
     "grades_encoded": {
         "structured_output": True,
         "extra_fields": {},
         "payload_instructions": _GRADE_SEMANTICS,
     },
     ```
     Its comment becomes `# Grades only, no extra per-row fields.`
   - `"grades_encoded_notes"`:
     ```python
     "grades_encoded_notes": {
         "structured_output": True,
         "extra_fields": {"notes": {"type": "string"}},
         "payload_instructions": _GRADE_SEMANTICS + (
             "\n  notes: one optional short note for the row; null when you have nothing to add."
         ),
     },
     ```
     Its comment becomes `# Grades plus an optional note → job["notes"] (do/get/like).`
   - `"grades_encoded_meta"`:
     ```python
     "grades_encoded_meta": {
         "structured_output": True,
         "extra_fields": {
             "company_job_id": {"type": "string"},
             "job_title": {"type": "string"},
             "job_link": {"type": "string"},
             "job_data": {"type": "object", "additionalProperties": {"type": "string"}},
         },
         "payload_instructions": _GRADE_SEMANTICS + (
             "\n  company_job_id: the listing's company job identifier; null when none is found.\n"
             "  job_title, job_link: the listing's title and link as found; job_data: other key/value details "
             "the listing states (e.g. location, salary_range). Fill these when your instructions say to include "
             "them; otherwise null."
         ),
     },
     ```
     Its comment becomes `# Grades plus listing metadata (qualify_job_listings).`
   - `"grades_encoded_vet_meta"`:
     ```python
     "grades_encoded_vet_meta": {
         "structured_output": True,
         "extra_fields": {"website": {"type": "string"}},
         "grade_letters": sorted(INFLOW_CONFIG["vet"]["pass_grades"] | INFLOW_CONFIG["vet"]["fail_grades"]),
         "confidence_range": (1, 5),
         "payload_instructions": (
             "Report one result per hit through the provided tool. Each hit in the content is identified by its "
             "index (for example 000); report that hit under its index, graded on the fixed link-type vector code "
             f"{INFLOW_CONFIG['vet']['grade_vector_code']}.\n"
             "  grade: exactly one of A B C D F, as defined in your instructions.\n"
             "  confidence: an integer 1–5 for that grade (use 5 when the page type is clear):\n"
             + _CONFIDENCE_SCALE_LINES +
             "  website: absolute company homepage URL — required on every grade including F."
         ),
     },
     ```
     Its comment becomes `# Vet inflow discovery: one LT grade per hit + website (AST-880).`
   - `"grades_encoded_prefilter_links"`:
     ```python
     "grades_encoded_prefilter_links": {
         "structured_output": True,
         "extra_fields": {
             "possible_job_links": {"type": "array", "items": {"type": "integer"}},
             "culture_links_to_explore": {"type": "array", "items": {"type": "integer"}},
         },
         "payload_instructions": _GRADE_SEMANTICS + (
             "\n  possible_job_links: 1–5 integer indices from the enumerated nav list that may lead to job "
             "pages; null when none.\n"
             "  culture_links_to_explore: 1–5 integer indices from the same list for culture pages; null when none."
         ),
     },
     ```
     Its comment becomes `# Prefilter company: grades plus job / culture link indices (AST-603).`

   ⚠️ **Decision:** the output-type keys keep their `grades_encoded*` names. They are stored in `TASK_CONFIG[...]["output_type"]` and read by AST-2180's files, and renaming them is in no child's Scope. The 1–5 counts on the link arrays are carried over from today's instruction text as prompt semantics only; no `minItems` / `maxItems` is added to `extra_fields`.
6. **`stringify_response_schema`.** Replace the body from `output_type = task_cfg.get("output_type", "")` down to (but not including) `# CHAT tasks use…` with nothing, and change the tail so the function reads:
   ```python
   def stringify_response_schema(task_key: str) -> str:
       """Return the response_schema as a nested envelope for prompt insertion.
       Structured-output (grader) types show agent_performance only — rows go through the forced tool (AST-2172).
       For all others: { agent_performance: {...}, agent_payload: {...task fields...} }"""
       task_cfg = TASK_CONFIG.get(task_key, {})
       schema = task_cfg.get("response_schema")
       if not schema:
           return ""
       # CHAT tasks use concern-capable performance schema; others keep BASE_SCHEMA.
       perf_schema = (
           CONVERSATIONAL_PERFORMANCE_SCHEMA
           if is_conversational_task(task_key)
           else BASE_SCHEMA
       )
       envelope = {"agent_performance": _schema_to_example(perf_schema)}
       if not ASTRAL_CONFIG["output_types"].get(task_cfg.get("output_type", ""), {}).get("structured_output"):
           envelope["agent_payload"] = _schema_to_example(schema)
       return json.dumps(envelope, indent=2)
   ```
   Then confirm non-grader output is unchanged:
   ```bash
   python3 - <<'EOF'
   import json
   from src.utils.config import TASK_CONFIG, ASTRAL_CONFIG, stringify_response_schema as s
   before = json.load(open("debug/spikes/AST-2177/stringify_before.json"))
   for k, cfg in TASK_CONFIG.items():
       if ASTRAL_CONFIG["output_types"].get(cfg.get("output_type", ""), {}).get("structured_output"):
           assert "agent_payload" not in s(k) and (not cfg.get("response_schema") or "agent_performance" in s(k)), k
       else:
           assert s(k) == before[k], k
   print("stringify ok")
   EOF
   ```

   ⚠️ **Decision:** grader types still show the `agent_performance` example rather than an empty string. That keeps the `status` / `failure_note` shape in front of the model, which the AST-1839 path relies on, and there is no `agent_payload` for AC 7 to trip on.
7. Compile and import: `python3 -m py_compile src/utils/config.py && python3 -c "import src.utils.config"`.

## Stage 3: Grader prompt rows in `agent_task.json`

**Done when:** the AC 7 check below prints `AC7 ok`. `git diff --stat data/admin/agent_task.json` shows only that file. A JSON-level diff confirms that only the `cache_prompt` of the nine listed rows changed.

1. Copy the script in **Appendix A** verbatim to `debug/spikes/AST-2177/apply_prompt_edits.py`. Run `python3 debug/spikes/AST-2177/apply_prompt_edits.py data/admin/agent_task.json` once. It applies exact substring edits, each asserted to match exactly once in its row, and writes the file in its existing format (`indent=2`, `ensure_ascii=False`, no trailing newline). If any assertion fails, **stop** and post the blocked comment; do not hand-edit around it. The script was dry-run against this branch's `agent_task.json` at plan time: every edit matched once, and no other row changed.

   What it changes, per row:
   - `grade_do`, `grade_get`, `grade_like`, `meteorite_like`:
     - STEP 2 / 3 / 4 move from the encoded line and `agent_payload` string to the provided tool, the `notes` field and `agent_performance` in the same call.
     - "Downstream software decodes the compact line" becomes "attaches rubric-sourced descriptions".
     - The `[index=NNN]` paragraph says "report that row under its exact index (`024`)".
     - The `## GRADE SET COMPLETENESS` section is deleted.
     - `grade_get` only: "use the tail" becomes "use the note".
   - `evaluate_jd`: the `## GRADE SET COMPLETENESS` section becomes `## QUALITY CHECK (QC)` — "QC (Quality Check) is never X — grade it F when there is not enough to analyze." (moved, not deleted, per Scope). STEP 3's "(never QCX0, never QCF0)" becomes "(never X, never confidence 0)".
   - `evaluate_meteorite`: the `## GRADE SET COMPLETENESS` section is deleted.
   - `prefilter_company`: the `## GRADE SET COMPLETENESS` section is deleted, along with rule 5 ("Match the output schema exactly. If the shape is wrong, your work is lost.", a deviation warning per Functional scope 7).
   - `qualify_job_listings`:
     - STEP 4 loses the `ERA4|…` segment example and the "7 codes" / segment-count text.
     - STEP 5 talks about grades and null fields instead of line endings.
     - The company-job-id paragraph loses the "keep its pipe" `003|…` example.
     - The metadata paragraph's `{code}X0` becomes "X with confidence 0".
     - The `## GRADE SET COMPLETENESS` section is deleted.
   - `vet_inflow_discovery`: the header `## ENCODED A-F LINK-TYPE VET` becomes `## A-F LINK-TYPE VET`. The whole `## Response` section (envelope / `agent_payload` / `{pos}|LT…` format / example) becomes `## Response\n\n{$OUTPUT_INSTRUCTIONS}`. The live-content description (`000|title|url|snippet` input rows) stays, because it describes the input, not the output.
2. Run the AC 7 check:
   ```bash
   python3 - <<'EOF'
   import json
   from src.utils.config import TASK_CONFIG, ASTRAL_CONFIG, resolve_tokens
   rows = {r["task_key"]: r for r in json.load(open("data/admin/agent_task.json"))}
   banned = ["{pos}", "exactly 4 characters", "GRADE SET COMPLETENESS", "agent_payload", "processing failure"]
   n = 0
   for k, cfg in TASK_CONFIG.items():
       if not ASTRAL_CONFIG["output_types"].get(cfg.get("output_type", ""), {}).get("structured_output"):
           continue
       text = resolve_tokens(rows[cfg.get("master_task_key") or k]["cache_prompt"], {}, k, warn_on_empty=False)
       bad = [b for b in banned if b in text]
       assert not bad and "5: The source explicitly states it." in text, (k, bad)
       n += 1
   assert n == 11, n
   print("AC7 ok")
   EOF
   ```
3. JSON-level diff check: `python3 -c "import json,subprocess; a={r['task_key']:r for r in json.loads(subprocess.check_output(['git','show','HEAD:data/admin/agent_task.json']))}; b={r['task_key']:r for r in json.load(open('data/admin/agent_task.json'))}; ch=sorted(k for k in a if a[k]!=b[k]); assert ch==sorted(['evaluate_jd','evaluate_meteorite','grade_do','grade_get','grade_like','meteorite_like','prefilter_company','qualify_job_listings','vet_inflow_discovery']), ch; assert all({f for f in a[k] if a[k][f]!=b[k][f]}=={'cache_prompt'} for k in ch); print('rows ok')"`.

Susan applies the new rows with **Revert to file** at UAT (parent decision). The DB rows don't change in this ticket.

## Canon check (`stat.agent.confidence-bounds`)

- Multi-vector graders: `_GRADE_SEMANTICS` states 1–5 with a letter and 0 only with X, and keeps the scale lines (`5: The source explicitly states it.` … `0: Use only with grade X`). X is described as no signal.
- Vet: confidence 1–5, no X (vet letters are A–D pass / F fail). This is unchanged from today, and `confidence_range: (1, 5)` declares it for the schema builder.
- No prompt text tells the model to write `{A-F}0`. The sanctioned `{A-F}0` → `X0` rewrite stays a hydrate concern (AST-2178).

## Execution contract

The plan is binding. Steps run in order and stages run in order. No added files, modules or dependencies; nothing committed from `debug/`. If a step is ambiguous, doesn't match the code, or an assertion fails, stop and comment on the parent [AST-2172](https://linear.app/astralcareermatch/issue/AST-2172):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

Each stage ends in one `code(AST-2177): …` commit on the epic worktree, published with `git push origin HEAD:sub/AST-2172/AST-2177-capability-registry-grader-marker-prompts`. Compile and lint before every commit.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Revisions

Revision 1 — 2026-10-14
Driven by: Susan's directive on AST-2172, 2026-10-13 16:47: "do NOT run the Stage 1 spike locally — no provider calls from this host, no new env vars, no gate tickets … the models the three graders actually run on (qwen/qwen3-235b-a22b-2507 for Grace and Lucy, openai/gpt-oss-120b for Kent) must stay selectable as graders on staging. Set them provisionally … Everything else follows plan defaults."
Changes: Stage 1 steps 1–7 (spike run) skipped. `debug/spikes/AST-2177/spike_tool_choice.py` exists but was never executed and isn't committed. Values as built:
- Every `LLM_SERVER_CONFIG` entry (`anthropic`, `kimi`, `openrouter`, `deepseek`) has `structured_output_capability: None`. That's the plan's default for anything unchecked; no direct-model overrides.
- `OPENROUTER_STRUCTURED_OUTPUT_OVERRIDES` sets `openai/gpt-oss-120b` and `qwen/qwen3-235b-a22b-2507` to `"advisory"`. **Unverified — Susan checks on staging.** I chose `advisory` rather than `enforced` so AST-2178's light check runs on every reply until a check proves the schema is enforced.
- Stage 1 done-when, as built: `get_structured_output_capability` returns `advisory` for the two grader slugs and `None` for every other model.

## Appendix A — `debug/spikes/AST-2177/apply_prompt_edits.py`

```python
"""AST-2177: strip encoded-line format text from grader rows in data/admin/agent_task.json.
Every edit is an exact substring replacement that must match exactly once in its row."""
import json
import re
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "data/admin/agent_task.json"

# Shared paragraphs (grade_do / grade_get / grade_like / meteorite_like)
S2_OLD = (
    "STEP 2 — CONSTRUCT PAYLOAD: Build a **token-conservative** encoded line for `agent_payload` (see PAYLOAD INSTRUCTIONS). "
    "Each JD row in --- CONTENT --- carries its own unique index (`[index=NNN]`). Indexes are not sequential from 000 and may "
    "start anywhere; start each encoded line with that row's exact index.\n"
    "You may append **one** optional short note (5-10 words MAX) to the tail after the grade segments (`|...`); omit it "
    "entirely if nothing worth mentioning — that is valid."
)
S2_NEW = (
    "STEP 2 — CONSTRUCT PAYLOAD: Report your grades through the provided tool (see PAYLOAD INSTRUCTIONS). "
    "Each JD row in --- CONTENT --- carries its own unique index (`[index=NNN]`). Indexes are not sequential from 000 and may "
    "start anywhere; report each row under that row's exact index.\n"
    "You may add **one** optional short note (5-10 words MAX) in that row's notes field; leave it null "
    "if nothing worth mentioning — that is valid."
)
S3_OLD = (
    "STEP 3 — VALIDATE PAYLOAD: Confirm exactly one encoded line per JD row, each matching the index from --- CONTENT ---, "
    "and **every** rubric vector present with valid **two-letter codes** from the rubric and valid grade + confidence digits "
    "per the instructions. Omitting a code is invalid; silent vectors must be {code}X0."
)
S3_NEW = (
    "STEP 3 — VALIDATE PAYLOAD: Confirm exactly one row per JD row, each under the index from --- CONTENT ---, "
    "and **every** rubric vector graded with a valid grade and confidence per the instructions. "
    "Silent vectors get grade X with confidence 0."
)
S4_OLD = "STEP 4 — PACKAGE RESPONSE: Return valid JSON with `agent_performance` and `agent_payload` (string)."
S4_NEW = "STEP 4 — PACKAGE RESPONSE: Fill `agent_performance` in the same tool call."
FAT_OLD = (
    "DO NOT ADD PER-VECTOR REASON TEXT OR FAT JSON AT THIS STAGE. Downstream software decodes the compact line and "
    "attaches rubric-sourced descriptions to each grade."
)
FAT_NEW = "DO NOT ADD PER-VECTOR REASON TEXT AT THIS STAGE. Downstream software attaches rubric-sourced descriptions to each grade."
IDX_OLD = "Your encoded line must start with that row's exact index (`024|…`)."
IDX_NEW = "Report that row under its exact index (`024`)."

_DSGL = [(S2_OLD, S2_NEW), (S3_OLD, S3_NEW), (S4_OLD, S4_NEW), (FAT_OLD, FAT_NEW), (IDX_OLD, IDX_NEW)]

EDITS = {
    "grade_do": _DSGL,
    "grade_like": _DSGL,
    "meteorite_like": _DSGL,
    "grade_get": _DSGL + [
        ("Do **not** use the tail as a substitute", "Do **not** use the note as a substitute"),
    ],
    "evaluate_jd": [
        ("(never QCX0, never QCF0)", "(never X, never confidence 0)"),
    ],
    "evaluate_meteorite": [],
    "prefilter_company": [
        ("\n5. Match the output schema exactly. If the shape is wrong, your work is lost.", ""),
    ],
    "qualify_job_listings": [
        (
            'to grade each job, prefixed with each criteria code, and suffixed with the corresponding confidence rating (1-5), '
            'e.g. "ERA4|MEA4|PGF4|WAA3|MWA3|KOA4|QCA5"\n'
            "Every rubric vector code must appear exactly once per job line; use X0 when silent — never omit a code.\n"
            "Every grade example in these instructions shows 7 codes for illustration only — the code count is not a template. "
            "Emit one segment per code in the rubric, in the order the rubric lists them, as many segments as the rubric has codes.",
            "to grade each job on every rubric vector, each grade with its confidence rating (1-5).\n"
            "Every rubric vector must be graded once per job; use X with confidence 0 when silent — never omit a vector.",
        ),
        (
            'If "F" is found anywhere in the string from STEP 4, then ONLY include the job ID determined in STEP 1 '
            "(if STEP 1 found no job ID, end the line after the grade segments).  "
            'If "F" is NOT in the STEP 4 string, then go on to add job_title and job_link, then key/value pairs found in the html content.',
            'If any grade from STEP 4 is "F", then ONLY include the job ID determined in STEP 1 '
            "(null if STEP 1 found no job ID) and leave job_title, job_link and job_data null.  "
            'If no grade from STEP 4 is "F", then go on to add job_title and job_link, then key/value pairs found in the html content as job_data.',
        ),
        (
            "leave the company_job_id field empty but keep its pipe so the fields after it stay in position, "
            'e.g. "003|ERA4|MEA4|PGA4|WAA3|MWA3|KOA4|QCA5||Job Title|https://www.workheredummy.com/jobs/abc".',
            "set its company_job_id to null and still fill the other fields.",
        ),
        (
            "never to grade segments: a rubric vector about salary, compensation, or employment type is still graded on every line, "
            "as {code}X0 when the listing does not state it.",
            "never to grades: a rubric vector about salary, compensation, or employment type is still graded for every job, "
            "as X with confidence 0 when the listing does not state it.",
        ),
    ],
    "vet_inflow_discovery": [
        ("## ENCODED A-F LINK-TYPE VET", "## A-F LINK-TYPE VET"),
    ],
}

# Whole-section edits: "\n\n## GRADE SET COMPLETENESS..." through the end of that paragraph.
GSC_RE = re.compile(r"\n\n## GRADE SET COMPLETENESS[^\n]*\n[^\n]*")
QC_SECTION = "\n\n## QUALITY CHECK (QC)\nQC (Quality Check) is never X — grade it F when there is not enough to analyze."
GSC_ROWS = {
    "grade_do": "", "grade_get": "", "grade_like": "", "meteorite_like": "",
    "evaluate_meteorite": "", "prefilter_company": "", "qualify_job_listings": "",
    "evaluate_jd": QC_SECTION,
}
# vet: replace the hardcoded "## Response" section (to end of prompt) with the output-type token.
VET_RESPONSE_RE = re.compile(r"## Response\n\n.*\Z", re.S)
VET_RESPONSE_NEW = "## Response\n\n{$OUTPUT_INSTRUCTIONS}"

with open(PATH, encoding="utf-8") as f:
    rows = json.load(f)
seen = set()
for row in rows:
    key = row["task_key"]
    if key not in EDITS:
        continue
    assert row.get("current") == 1, key
    text = row["cache_prompt"]
    for old, new in EDITS[key]:
        assert text.count(old) == 1, (key, old[:60], text.count(old))
        text = text.replace(old, new)
    if key in GSC_ROWS:
        text, n = GSC_RE.subn(lambda _m: GSC_ROWS[key], text)
        assert n == 1, (key, "GRADE SET COMPLETENESS", n)
    if key == "vet_inflow_discovery":
        text, n = VET_RESPONSE_RE.subn(lambda _m: VET_RESPONSE_NEW, text)
        assert n == 1, (key, "## Response", n)
    row["cache_prompt"] = text
    seen.add(key)
assert seen == set(EDITS), set(EDITS) - seen
with open(PATH, "w", encoding="utf-8") as f:
    f.write(json.dumps(rows, indent=2, ensure_ascii=False))
print("edited", sorted(seen))
```

## Joan validate

[plan-rubric]
**Ticket:** AST-2177
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `origin/sub/AST-2172/AST-2177-capability-registry-grader-marker-prompts` @ `f53f98c78`

## Canon scores

| id | grade | effort | one-line |
|----|-------|--------|----------|
| stat.agent.confidence-bounds | A | | |

## Traceability

**7** → Stage 2 (`_GRADE_SEMANTICS` / vet scale, delete `_ENCODED_GRADE_SET_COMPLETENESS`, grader `structured_output` markers, `stringify_response_schema` grader branch) + Stage 3 (nine `agent_task.json` rows + Appendix A script) + AC7 harness (`n == 11` task keys with `structured_output`, master-key resolution for `meteorite_grade_*`). Stage 1 → parent Functional scope §1 / child scope capability registry (not AC 7 text). Parent AC 1–6, 8–11 / 10a–10b: N/A this child.

## Findings

### discuss

- **Location:** Stage 1 — OpenRouter server `structured_output_capability: None` + per-slug overrides only  
  **Finding:** Plan explicitly accepts a narrow grader model surface until more slugs are spiked; pairs with AST-2181’s gate. Reasonable vs assuming `advisory` for 93 untested slugs, but it is a product/capacity tradeoff.  
  **Recommendation:** Susan confirms default `None` is intended; document re-spike steps when adding OpenRouter grader models.

- **Location:** Stage 1 — spike keys via `ASTRAL_SPIKE_KEY_*` env vars  
  **Finding:** Debug-only exception to production “no keys from env” posture; plan states stop-if-unset and never commit keys.  
  **Recommendation:** Accept for spike; builder follows blocked-comment contract.

- **Location:** Stage 2 — `prompt_prefix_structured` + AST-2179 contract  
  **Finding:** New config surface; `prompt_prefix` bytes frozen for current `anthropic.py` until #4 wires the flag.  
  **Recommendation:** Ensure AST-2179 plan cites `prompt_prefix_structured` (out of this child’s scope).

- **Location:** Stage 3 / `prefilter_company` — delete rule 5 (“Match the output schema exactly…”)  
  **Finding:** Not one of AC 7’s banned substrings; aligns with parent prompt-simplification intent but removes a deviation warning not literally named in AC 7.  
  **Recommendation:** Archie/Susan OK with dropping that line vs rephrasing without “shape is wrong” tone.

- **Location:** Citations vs content  
  **Finding:** Frozen list is only `stat.agent.confidence-bounds`; `_GRADE_SEMANTICS` also states `A–F` / `X` letter rules (parent child #2 dispatch cited confidence scale only). Not scored as `stat.agent.grade-vector-validation`.  
  **Recommendation:** Scope observation for Archie if she wants grade-vector on sibling lists later; no plan change required here.

### acceptable

- **Location:** `[scope-gate]` vs current Description  
  **Finding:** Amended Scope (nine grader rows; `REPO_ADMIN_JSON_CONFIG` column on AST-2181) matches Files Changed and Stages; plan published after Chuckles amendment (`f53f98c78`).  
  **Recommendation:** None.

- **Location:** AC 7 `assert n == 11` vs nine edited rows  
  **Finding:** Eleven `TASK_CONFIG` keys use grader `output_types`; `meteorite_grade_do` / `meteorite_grade_get` inherit `grade_do` / `grade_get` prompts — consistent with scope-gate note.  
  **Recommendation:** None.

- **Location:** `vet_inflow_discovery`  
  **Finding:** Replacing hardcoded `## Response` with `{$OUTPUT_INSTRUCTIONS}` plus Stage 2 vet `payload_instructions` supplies confidence-scale lines AC 7 requires (today’s row lacks them).  
  **Recommendation:** Execute Stage 2 before Stage 3.

- **Location:** After AST-2176  
  **Finding:** Active `stat.agent.confidence-bounds` matches plan’s Canon check (hydrate exception not re-litigated in prompts). Child notes “After #1.”  
  **Recommendation:** Land/build order: #1 before siblings that plan against active canon.

### fix-now

(none)

## R6 (condensed)

- **Definition fidelity:** Matches amended child Scope and parent Component/Technical slice for #2 (capability + marker + prompt text; no DB/UI/transport/core).  
- **stat.agent.confidence-bounds:** Scale lines preserved; silent vectors → `X` + `0`; vet `1–5` / no `X`; no encoded `{A-F}0` prompt pattern; hydrate exception left to AST-2178.  
- **Self-assessment:** Estimate 5 — credible (live spike + large `config.py` + nine-row scripted JSON edits).  
- **Plan Discuss:** 0 completed `[plan-discuss]` rounds; status Plan Ready, assignee Joan.

context_tokens≈58000

---

## Review

Build on `origin/sub/AST-2172/AST-2177-capability-registry-grader-marker-prompts`:

- `f31b6e05c` Stage 1: capability registry. Spike not run, per Susan's directive (Revision 1); the grader-model values are provisional `advisory`.
- `9a5d440f0` Stage 2: grader output-type marker and extra fields, semantics-only payload instructions, `stringify_response_schema`, `prompt_prefix` / `prompt_prefix_structured`.
- `d90b15d1b` Stage 3: nine grader prompt rows in `agent_task.json`. The Appendix A script was run verbatim.

Checks:
- All Done-when checks pass, including AC 7 (11 grader tasks) and the JSON-level row diff.
- `prompt_prefix` is byte-identical to before.
- Non-grader `stringify_response_schema` output is unchanged for every task.
- Ruff finding count on `config.py` is 105 before and 105 after (repo-wide user-level rules).

Expected test churn for qa-child: I ran the component tests for `test_config.py`, `test_anthropic.py`, `test_candidate.py` and `test_repo_admin_json.py`. 9 of them fail with this branch and pass on the pre-build tree. All 9 assert encoded-line text that this ticket removes on purpose:
- `test_repo_admin_json.py`: `TestAst1154GradedTaskCompletenessPrompts` (2 tests), `TestAst1910EvaluateJdQcNeverXPrompt::test_catalog_evaluate_jd_cache_prompt_qc_exception`. The QC rule itself survives in `## QUALITY CHECK (QC)`.
- `test_config.py`: `TestAst1154EncodedGradeSetCompleteness` (2 tests), `TestAst505InflowDiscoveryConfig::test_vet_grades_encoded_vet_meta_output_type`, `TestResolveTokens::test_output_type_token_uses_task_instructions`, `TestStringifyResponseSchema` (2 tests).

The other 89 failures in those files fail the same way on the pre-build tree.
