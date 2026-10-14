# AST-2179 — Forced-tool transport

- **Linear:** [AST-2179](https://linear.app/astralcareermatch/issue/AST-2179) · parent [AST-2172](https://linear.app/astralcareermatch/issue/AST-2172) (Enforced structured output for rubric graders)
- **Publish ref:** `origin/sub/AST-2172/AST-2179-forced-tool-transport`
- **Assignee:** Katherine

Both Messages-protocol clients (`send_to_anthropic`, `send_to_llm_compat`) gain an optional `forced_tool` argument (`{"name": str, "input_schema": dict}`). When it is set, they send it as the only tool with `tool_choice` naming it, keep the max_tokens fail-closed check, and return the tool's input dict as `parsed_response`. On OpenRouter-routed models a forced-tool call also sends `provider.require_parameters: true`, early enough that the AST-1959 host probe carries it too. `getTimestampPrefix` gains a flag that swaps in the envelope-free `prompt_prefix_structured` (added by AST-2177). `llm_external` gains the tool-input extractor, and its text extractor falls back to the tool input as JSON so audit/debug text isn't empty. `_parse_json_response` loses its encoded-grade-string coercion. This is transport only. Nothing passes `forced_tool` or the prefix flag yet; AST-2180 (child #5) wires grader calls onto it, and AST-2178's `build_grade_tool_schema` supplies `input_schema`.

## What's already on this sub (verified at plan time)

- The sub was synced against `origin/ftr/AST-2172-structured-output-graders`, so AST-2176/2177/2178 are in `HEAD`. ⚠️ The spawn's `sync-child.sh … --ftr AST-2172` looks for `origin/ftr/AST-2172`, which doesn't exist, and silently skips the parent merge. The builder must pass **`--ftr AST-2172-structured-output-graders`** (the registry's `parent_ftr`).
- `ASTRAL_CONFIG["prompt_prefix_structured"]` exists (`src/utils/config.py` ~5065, AST-2177).
- `src/core/grade_schema.py::build_grade_tool_schema(output_type, codes, row_ids)` returns the `input_schema` dict only. There is no tool-name constant anywhere in `src/`, so the tool name is the caller's (AST-2180's) and transport takes it from `forced_tool["name"]`.
- `src/external/openrouter.py::_probe_request_kwargs` copies every real-call kwarg except `messages`/`system`. So `tools`, `tool_choice` and `extra_body.provider.require_parameters` reach the probe unchanged as long as they are in `api_kwargs` before `get_batch_host` is called. No change to `openrouter.py` is needed for AC 4.
- `get_model_routing(server_id, sku)` returns `"direct"` or `"openrouter"` (`LLM_MODEL_ROUTING_TYPES`).
- `enable_web_search` has no caller under `src/core`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/llm_external.py` | New `extract_tool_input`; `extract_api_response_text` falls back to the tool input as JSON when there is no text block | utils |
| `src/external/anthropic.py` | New `_forced_tool_body`; `forced_tool` on `send_to_anthropic` (send, truncation check, parse); `getTimestampPrefix(structured=False)`; drop encoded-string coercion in `_parse_json_response`; debug line for the `messages.create` kwargs | external |
| `src/external/llm_compat.py` | `forced_tool` on `send_to_llm_compat` (send, `require_parameters` for OpenRouter-routed, truncation check, parse) | external |

No other file. `agent.py`, `consult.py`, `roster.py`, `formatting.py` and `openrouter.py` are not touched.

## Stage 1: Tool-input extractor and raw-text fallback (`llm_external.py`)

**Done when:** `extract_tool_input` returns a matching `tool_use` block's input and raises when there is none. `extract_api_response_text` returns the text block when one exists, the tool input JSON when only a `tool_use` block exists, and still raises `"API response content block missing text attribute"` for thinking-only content.

1. In `src/utils/llm_external.py`, add `import json` above `from typing import …`, keeping the existing import order (`asyncio`, then `json`).
2. In `extract_api_response_text`, replace
   ```python
       if not text_parts:
           raise ValueError("API response content block missing text attribute")
   ```
   with
   ```python
       if not text_parts:
           # Forced-tool reply (AST-2172): no text block, so audit/debug text is the tool input as JSON.
           tool_inputs = [b.input for b in api_response.content if getattr(b, "type", None) == "tool_use"]
           if tool_inputs:
               return json.dumps(tool_inputs[-1])
           raise ValueError("API response content block missing text attribute")
   ```
   A text block still wins when present (parent Technical scope: "gets the JSON of that input when there is no text block"). Only `type == "tool_use"` counts, so web-search `server_tool_use` blocks never feed the fallback.
3. Directly after `extract_api_response_text`, add:
   ```python
   def extract_tool_input(api_response: Any, tool_name: str) -> Dict[str, Any]:
       """Input dict of the named tool_use block — the payload of a forced-tool call (AST-2172). Raises when absent."""
       for block in getattr(api_response, "content", None) or []:
           if getattr(block, "type", None) == "tool_use" and getattr(block, "name", None) == tool_name:
               if not isinstance(block.input, dict):
                   raise ValueError(f"Tool {tool_name!r} input is not an object")
               return block.input
       raise ValueError(f"API response has no {tool_name!r} tool call")
   ```
4. `python3 -m py_compile src/utils/llm_external.py`, then the Done-when check with `SimpleNamespace` fakes (no network):
   ```bash
   python3 -c "
   from types import SimpleNamespace as N; from src.utils.llm_external import extract_tool_input as t, extract_api_response_text as x
   r = N(content=[N(type='tool_use', name='submit_grades', input={'000': {}})])
   assert t(r, 'submit_grades') == {'000': {}} and x(r) == '{\"000\": {}}'
   assert x(N(content=[N(type='text', text='hi'), N(type='tool_use', name='s', input={})])) == 'hi'
   for bad in (lambda: t(r, 'other'), lambda: x(N(content=[N(thinking='x')]))):
       try: bad(); raise SystemExit('expected ValueError')
       except ValueError: pass
   print('ok')"
   ```
5. Commit `code(AST-2179): llm_external — forced-tool input extractor + raw-text fallback`, then publish.

## Stage 2: Anthropic client (`anthropic.py`)

**Done when:** `_forced_tool_body` produces one tool plus a `tool_choice` naming it. `getTimestampPrefix(structured=True)` contains `prompt_prefix_structured` and not the envelope sentence. `_parse_json_response` no longer imports or calls the encoded helpers. `send_to_anthropic` compiles with the new argument.

1. In the `from src.utils.formatting import (…)` block, delete `coerce_grades_encoded_json_parse`, `looks_like_encoded_grades_text` and `clean_encoded_agent_payload`, keeping `heal_agent_payload_envelope` and `heal_json`. In the `from src.utils.llm_external import (…)` block, add `extract_tool_input` after `extract_api_response_text`.
2. `getTimestampPrefix`: change the signature to `def getTimestampPrefix(structured: bool = False) -> str:`. Add one docstring line: `structured=True swaps the two-key envelope sentence for prompt_prefix_structured (forced-tool calls, AST-2172).` Replace
   `envelope_instruction = ASTRAL_CONFIG.get("prompt_prefix", "")`
   with
   `envelope_instruction = ASTRAL_CONFIG.get("prompt_prefix_structured" if structured else "prompt_prefix", "")`.
   The existing callers (`agent.py:1325`, `agent.py:3171`) pass nothing and are unchanged.
3. `_parse_json_response`: delete the `if isinstance(obj, str):` block (the three lines calling `coerce_grades_encoded_json_parse`), leaving `obj = json.loads(cleaned)` / `return obj`. Delete the two lines `if looks_like_encoded_grades_text(cleaned):` / `return {"agent_payload": clean_encoded_agent_payload(cleaned)}`. Nothing else in the function changes.

   ⚠️ **Decision:** Between this child landing on ftr and AST-2180 landing, a grader reply that is bare encoded text (not JSON) fails to parse here instead of being wrapped. `agent.py:2482` still coerces a JSON-string payload itself. That gap only ever exists on `ftr`, never on `dev`, and this ticket's Scope assigns the removal here.
4. Directly after `_effort_body`, add:
   ```python
   def _forced_tool_body(forced_tool: Dict[str, Any]) -> Dict[str, Any]:
       """One forced tool as Messages-protocol kwargs (AST-2172): the model must answer by calling it."""
       name = forced_tool["name"]
       return {
           "tools": [{"name": name, "input_schema": forced_tool["input_schema"]}],
           "tool_choice": {"type": "tool", "name": name},
       }
   ```
   `llm_compat` imports it the same way it imports `_effort_body`.
5. `send_to_anthropic`:
   1. Add the keyword `forced_tool: Optional[Dict[str, Any]] = None,` after `record_timesheet`. Add a docstring line: `forced_tool ({name, input_schema}) → sent as the only tool with tool_choice forcing it; its input is parsed_response.`
   2. Directly after the `if not model_code: raise …` guard, add:
      ```python
      if forced_tool and enable_web_search:
          raise ValueError("forced_tool and enable_web_search cannot be combined")
      ```
      ⚠️ **Decision:** Raise rather than silently let one `tools` list overwrite the other. There's no caller of `enable_web_search` in `src/core`, so this never fires today.
   3. Directly after the `if enable_web_search:` block, add:
      ```python
      if forced_tool:
          api_kwargs.update(_forced_tool_body(forced_tool))
      ```
   4. Directly before `def _make_api_call():`, add `logger.debug("Calling messages.create: %s", api_kwargs)`. This is the same line `llm_compat` already emits, and it makes AC 3's "debug `messages.create` kwargs" observable on this client as well. The schema stays on debug only (`stat.logging.debug`).
   5. Truncation check: change `if response_format == "json" and stop_reason == "max_tokens":` to `if (response_format == "json" or forced_tool) and stop_reason == "max_tokens":`. The error text and return shape are unchanged.
   6. Parse block: replace
      ```python
      parsed_response = None
      if response_format:
          if response_format not in ("text", "json", "python"):
              raise ValueError(f"Invalid response_format: {response_format}")
          response_dict = {"success": True, "api_response": response, "timesheet": timesheet}
          try:
              if response_format == "text":
      ```
      with
      ```python
      parsed_response = None
      if response_format or forced_tool:
          if response_format and response_format not in ("text", "json", "python"):
              raise ValueError(f"Invalid response_format: {response_format}")
          response_dict = {"success": True, "api_response": response, "timesheet": timesheet}
          try:
              if forced_tool:
                  # The forced tool's input is the payload (AST-2172), whatever response_format says.
                  parsed_response = extract_tool_input(response, forced_tool["name"])
              elif response_format == "text":
      ```
      The existing `elif "json"` / `elif "python"` branches and the `except Exception as parse_err:` failure path stay as they are. A missing tool call therefore takes the same logged-once parse-failure return (`stat.logging.error`: no new error log).
   7. No other change. The `agent_performance` timesheet read (`parsed_response.get("agent_performance")`) works unchanged, because AST-2178's schema puts `agent_performance` in the tool input.
6. `python3 -m py_compile src/external/anthropic.py`, then:
   ```bash
   python3 -c "
   from src.external.anthropic import _forced_tool_body as f, getTimestampPrefix as g
   from src.utils.config import ASTRAL_CONFIG as C
   b = f({'name': 'submit_grades', 'input_schema': {'type': 'object'}})
   assert b == {'tools': [{'name': 'submit_grades', 'input_schema': {'type': 'object'}}], 'tool_choice': {'type': 'tool', 'name': 'submit_grades'}}
   assert C['prompt_prefix_structured'] in g(True) and 'two-key envelope' not in g(True) and 'two-key envelope' in g()
   print('ok')"
   rg -n 'coerce_grades_encoded_json_parse|looks_like_encoded_grades_text|clean_encoded_agent_payload' src/external/   # expect no output
   ```
7. Commit `code(AST-2179): anthropic — forced tool send/parse, structured timestamp prefix, drop encoded coercion`, then publish.

## Stage 3: Compat client (`llm_compat.py`)

**Done when:** with `forced_tool` set, `api_kwargs` has one tool plus `tool_choice`. On an `openrouter`-routed model, `extra_body.provider.require_parameters is True` before `get_batch_host` runs. Without `forced_tool`, or on a `direct` model, `api_kwargs` is byte-identical to today's.

1. Imports: add `_forced_tool_body` to `from src.external.anthropic import …` (it becomes `_effort_body, _forced_tool_body, _parse_api_response, …`). Add `extract_tool_input` to the `from src.utils.llm_external import (…)` block, in alphabetical position after `classify_provider_rate_limit`.
2. `send_to_llm_compat`: add the keyword `forced_tool: Optional[Dict[str, Any]] = None,` after `record_timesheet`. Extend the docstring with: `forced_tool ({name, input_schema}) → only tool + tool_choice; OpenRouter-routed adds provider.require_parameters (probe included); its input is parsed_response.`
3. Replace
   ```python
   provider = {"provider": tier["provider"]} if tier.get("provider") else {}
   ```
   with
   ```python
   provider_obj = dict(tier.get("provider") or {})
   # Forced tool on OpenRouter (AST-2172): only route to hosts that honour tools/tool_choice. Set before the
   # AST-1959 probe, which copies these kwargs, so the probed host can take the real call.
   if forced_tool and get_model_routing(server_id, sku) == "openrouter":
       provider_obj["require_parameters"] = True
   provider = {"provider": provider_obj} if provider_obj else {}
   ```
   ⚠️ **Decision:** `require_parameters` is gated on `forced_tool`, not just on routing. Parent Functional scope 2 says "every other task is sent exactly as today", and `require_parameters` would narrow host routing for every non-grader OpenRouter call too. AC 4 only constrains grader calls and direct calls, so both readings pass it; this one leaves non-grader traffic untouched.
4. Directly after the `if system_blocks: api_kwargs["system"] = system_blocks` lines (still before `async def _send`, and before the probe), add:
   ```python
   if forced_tool:
       api_kwargs.update(_forced_tool_body(forced_tool))
   ```
5. Truncation check: same change as Stage 2 step 5.5 (`(response_format == "json" or forced_tool)`).
6. Parse block: same replacement as Stage 2 step 5.6. The compat block's `except` return also carries `"host": host`; keep it as is.
7. No new logging. The existing `logger.debug("Calling messages.create: server=%s %s", …)` and the probe's own debug line already show the tools and `require_parameters`.
8. `python3 -m py_compile src/external/llm_compat.py src/external/anthropic.py src/utils/llm_external.py`, then a kwargs check with no network. Patch `_send` out by intercepting `await_provider_call_with_budget`, and patch `require_controlled_external_io`:
   ```bash
   python3 -c "
   import asyncio; from unittest.mock import patch
   import src.external.llm_compat as m
   from src.utils.config import LLM_MODEL_CONFIG as M, get_llm_server as S
   seen = []
   async def fake(fn, **kw): raise RuntimeError('stop')
   compat = lambda v: S(v['server'])['protocol'] == 'anthropic_compat'
   orr = next(v for v in M.values() if v['routing'] == 'openrouter' and compat(v)); dr = next(v for v in M.values() if v['routing'] == 'direct' and compat(v))
   ft = {'name': 'submit_grades', 'input_schema': {'type': 'object'}}
   with patch.object(m, 'require_controlled_external_io'), patch.object(m, 'await_provider_call_with_budget', fake), \
        patch.object(m.logger, 'debug', lambda msg, *a: seen.append(a[-1]) if 'messages.create' in msg else None), \
        patch.object(m, 'log_batch_id') as b:
       b.get.return_value = None
       for mdl, tool in ((orr, ft), (dr, ft), (orr, None)):
           asyncio.run(m.send_to_llm_compat([], server_id=mdl['server'], sku=mdl['sku'], tier={}, api_key='k', forced_tool=tool))
   (o, d, plain) = seen
   assert o['tool_choice'] == {'type': 'tool', 'name': 'submit_grades'} and len(o['tools']) == 1 and o['extra_body']['provider']['require_parameters'] is True
   assert 'tools' in d and 'require_parameters' not in str(d)
   assert 'tools' not in plain and 'tool_choice' not in plain and 'require_parameters' not in str(plain)
   print('ok')"
   ```
   The probe leg of AC 4 is structural: `_probe_request_kwargs` copies `extra_body.provider` and adds `zdr`. Betty's component test can assert it through `get_batch_host`. If this check script fails because a config fact assumed above has drifted (the model-config shape or the server `protocol` values), stop and comment rather than rewriting the check.
9. Commit `code(AST-2179): llm_compat — forced tool send/parse, require_parameters on OpenRouter-routed`, then publish.

## Expected test churn (Betty, not this build)

- `tests/component/external/test_anthropic.py::…test_wraps_top_level_json_string_encoded_grades` and `…test_wraps_bare_encoded_text_without_json` assert the coercion this ticket removes, so they go red after Stage 2.
- `tests/component/utils/test_llm_external.py::…test_raises_when_no_text_blocks` stays green (thinking-only content has no `tool_use` block).
- AC 3 and AC 4 need new component cases on both clients' kwargs (and the probe kwargs through `get_batch_host`). No live provider calls (Susan, 2026-10-14).

## Open risk for Chuckles / Susan (out of this ticket's scope — not planned)

`openrouter._batch_key` keys the AST-1959 host map on every request kwarg except `messages`/`system`, and `tools` is now part of that. A grader batch whose calls carry different schemas (a different row count in the last chunk, or different rubric codes) gets a separate probe, and possibly a different host, per distinct schema. That means more probe calls and split prompt caches within one batch. It doesn't affect correctness, and AC 4 still holds. Fixing it means touching `src/external/openrouter.py`, which no child of AST-2172 has in scope, so I'm raising it here rather than adding it.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2179
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `origin/sub/AST-2172/AST-2179-forced-tool-transport` @ `166439748`

## Canon scores

| id | grade | effort | one-line |
|----|-------|--------|----------|
| `stat.logging.error` | A | | |
| `stat.logging.debug` | A | | |

## Traceability

**3** → Stage 2 (`_forced_tool_body`, `forced_tool` on `send_to_anthropic`, debug `messages.create` kwargs) + Stage 3 (same on `send_to_llm_compat`, mock asserts tools/`tool_choice` when `forced_tool` set, absent when `None`) + **Expected test churn** (Betty: kwargs AC 3 on both clients). Full “any **grader task**” wiring is **not** in this child (Boundaries → #5 passes `forced_tool`); plan proves transport, not task selection. **4** → Stage 3 steps 3–4 (`require_parameters` on OpenRouter `provider_obj` before `extra_body` / `get_batch_host`), plan note on `_probe_request_kwargs` copy-through + Betty probe via `get_batch_host`. Parent AC 1–2, 5–11 / 10a–10b N/A.

## Findings

### discuss

- **Location:** Child AC **3** vs Boundaries  
  **Finding:** AC text names “any grader task”; this ticket only adds optional `forced_tool` and does not read `structured_output` / task keys (#5). Stage 3 mock and Betty’s planned component tests validate kwargs when `forced_tool` is passed, not that `grade_do` automatically sends a schema.  
  **Recommendation:** Treat AC **3** as satisfied at epic level only after AST-2180; for AST-2179, Betty’s new kwargs cases are the committed gate (plan already lists them).

- **Location:** Open risk — `openrouter._batch_key` + varying `tools` schemas  
  **Finding:** Per-schema probe/cache split within one batch; correctness and AC **4** hold; more probes possible. No child scopes `openrouter.py`.  
  **Recommendation:** Susan/Chuckles track as epic ops follow-up, not a plan blocker.

- **Location:** Stage 2 — `_parse_json_response` coercion removal  
  **Finding:** On `ftr` only, bare encoded grader text fails JSON parse until #5 uses forced-tool path; plan documents overlap with `agent.py` JSON-string coercion.  
  **Recommendation:** Accept per Scope partition; keep #5 before grader traffic on ftr.

- **Location:** AC **4** verification  
  **Finding:** Probe leg is structural (`api_kwargs` before `get_batch_host`); no live OpenRouter in plan (Susan 2026-10-14).  
  **Recommendation:** Betty asserts probe kwargs mirror real call; acceptable for validate-plan.

### acceptable

- **Location:** Scope / Files Changed  
  **Finding:** Only `llm_external.py`, `anthropic.py`, `llm_compat.py`; no `agent.py`, `openrouter.py`, schema build.

- **Location:** `stat.logging.debug`  
  **Finding:** Full `api_kwargs` on `messages.create` at debug on anthropic (parity with compat); schema not logged at error; no truncation; no `if debug` gating at call site.

- **Location:** `stat.logging.error`  
  **Finding:** Missing/invalid tool input uses existing parse `except` + `log_llm_batch_summary` path; no duplicate exception logs introduced.

- **Location:** `llm_external`  
  **Finding:** Text block wins over tool fallback; `server_tool_use` excluded; named `extract_tool_input` for `parsed_response`; JSON string for audit when text absent (parent Technical scope).

- **Location:** `getTimestampPrefix(structured=True)`  
  **Finding:** Uses AST-2177 `prompt_prefix_structured`; default callers unchanged; matches #2 contract for envelope omission on forced-tool calls (#5).

- **Location:** `require_parameters` gating  
  **Finding:** Only `forced_tool` + `openrouter` routing; non-grader OpenRouter traffic unchanged (plan decision aligns with parent FS §2 “every other task exactly as today”).

- **Location:** Dependencies  
  **Finding:** Plan assumes `HEAD` includes #6–#8 on sub via `--ftr AST-2172-structured-output-graders`; warns against bare `--ftr AST-2172`.

### fix-now

(none)

## R6 (condensed)

- Parent transport slice (forced tool + `tool_choice`, tool input as payload, OpenRouter `require_parameters`, prefix flag) matches stages.  
- `forced_tool` vs `enable_web_search` mutual exclusion is reasonable.  
- Truncation treat `forced_tool` like JSON for max_tokens fail-closed.  
- Plan Discuss: **0** rounds; **Plan Ready**, assignee Joan (ticket assignee Katherine — Chuckles handoff only).

context_tokens≈88000
