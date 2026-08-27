# AST-1515 — Contact-task config, markup parse, and dispatch

**Linear:** [AST-1515](https://linear.app/astralcareermatch/issue/AST-1515/contact-task-config-markup-parse-and-dispatch-estelle-needs-to-be)  
**Parent:** [AST-1414](https://linear.app/astralcareermatch/issue/AST-1414/estelle-needs-to-be-able-to-use-our-endpoints) — Estelle needs to be able to use our endpoints  
**Publish ref:** `sub/AST-1414/AST-1515-contact-task-config-markup-parse-dispatch`

Child #1 of AST-1414: register all contact-task keys in a new `CONTACT_TASK_CONFIG` block, parse `~~/<contact_task_key> [parameters]~~` from Estelle's reply, dispatch only allowlisted keys via dynamic handler imports, strip markup before Slack post, optionally run one same-event follow-up Estelle turn with task payloads in live content, and teach the markup contract in `contact_estelle_turn` prompts. Does **not** implement gazer scrape, meteorite create, or read handlers (siblings AST-1516–1518); does **not** extend `CONTACT_CONFIG` skills ACL.

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/utils/config.py` — modified — `CONTACT_TASK_CONFIG` block with all task keys + handler metadata
- `src/core/contact.py` — modified — markup parser, dispatch router, follow-up turn, markup strip before Slack post
- `data/admin/agent_task.json` — modified — `contact_estelle_turn` markup prompts

**Out of scope (siblings):** `src/core/gazer.py` (gazer scrape handler), `src/core/meteorite.py` (`create_contact_meteorite`), `src/core/tracker.py` (read handlers). **Does not** remove or rewrite AST-1471 `land_calls` — that path stays; contact-task markup is the new epic dispatch framework siblings register against.

**Depends on:** AST-1073 turn loop + AST-1072 envelope on tip (present after `sync-child.sh`). Sibling handler functions may be absent until their tickets land — dispatch must fail gracefully without breaking the turn.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | New `CONTACT_TASK_CONFIG` block (six keys, handler dotted paths, param metadata); import-time asserts; collision checks vs `TASK_CONFIG` and `CONTACT_CONFIG["skills"]` | utils |
| `src/core/contact.py` | Markup parse/strip helpers; `contact_tasks()` accessor; dynamic handler dispatch; follow-up turn wiring; Style D on dispatch paths; live_content contact-task catalog | core |
| `data/admin/agent_task.json` | Extend `contact_estelle_turn` system prompt: markup syntax, available keys, conversational-reply rule (no raw payloads in Slack) | data |

## Stage 1: `CONTACT_TASK_CONFIG` block

**Done when:** `CONTACT_TASK_CONFIG` exposes all six parent epic keys with handler metadata and parameter descriptions; import-time asserts pass; no key collides with `TASK_CONFIG` or `CONTACT_CONFIG["skills"]`; `contact_tasks()` in `contact.py` can read the block (Stage 2).

1. In `src/utils/config.py`, after `CONTACT_ESTELLE_CONFIG` asserts (~line 4439), add block comment `# CONTACT_TASK_CONFIG: allowlisted Contact task keys (AST-1515 / AST-1414). Distinct from CONTACT_CONFIG skills ACL and TASK_CONFIG dispatch catalog.`

2. Add `CONTACT_TASK_CONFIG` dict with exactly these keys (handler dotted paths are the **sibling implementation targets** — not implemented in this ticket):

| `task_key` | `handler` (module.attr) | `description` | `param_hint` |
|------------|-------------------------|---------------|--------------|
| `gazer_scrape` | `src.core.gazer.contact_task_gazer_scrape` | Fetch visible text + links + blocked/ok/closed/missing for one URL | single URL (rest of markup line) |
| `create_contact_meteorite` | `src.core.meteorite.create_contact_meteorite` | Land a meteorite from link (scrape-first) or pasted page text | URL or page text (rest of line) |
| `get_job_by_pattern` | `src.core.tracker.contact_task_get_job_by_pattern` | Resolve one fully hydrated job for the Slack candidate from a text pattern | pattern string (rest of line) |
| `get_job_data` | `src.core.tracker.contact_task_get_job_data` | Return stored job data for an id belonging to the candidate | astral job id (rest of line) |
| `get_company_data` | `src.core.tracker.contact_task_get_company_data` | Return stored company data via extant getters | company short_name or id (rest of line) |
| `get_candidate_data` | `src.core.tracker.contact_task_get_candidate_data` | Return stored candidate data for the Slack-resolved candidate | optional sub-path or empty (rest of line may be blank) |

   Each entry shape:

```python
"gazer_scrape": {
    "handler": "src.core.gazer.contact_task_gazer_scrape",
    "description": "Fetch visible text, links, and blocked/ok/closed/missing for one job URL.",
    "param_hint": "Single URL — remainder of the markup line after the task key.",
    "requires_candidate": True,
},
```

   Use the table above for all six keys. `requires_candidate` is `True` for every key in v1 (all handlers are candidate-scoped per parent Technical scope).

3. Add import-time asserts immediately after the dict:

   - `CONTACT_TASK_CONFIG` is a non-empty `dict`.
   - Every key is a non-empty `str`; every value is a `dict` with non-empty `str` fields `handler`, `description`, `param_hint`; `requires_candidate` is `bool`.
   - For each `task_key` in `CONTACT_TASK_CONFIG`: `task_key not in TASK_CONFIG` and `task_key not in CONTACT_CONFIG["skills"]`.
   - Each `handler` is a non-empty `str` containing at least one `.`. Split on the **last** `.` → non-empty `module_path` and non-empty `attr_name` (same rule as Stage 2 `_resolve_contact_task_handler`). Assert `module_path.startswith("src.core.")`.

4. Do **not** add runtime config helpers in `config.py` beyond the block — accessors live in `contact.py` (mirrors `contact_skills()` pattern).

## Stage 2: Markup parser and dispatch router

**Done when:** `parse_contact_task_markup(text)` returns ordered `(task_key, param)` spans; `strip_contact_task_markup(text)` removes all spans; `run_contact_task_dispatch(...)` resolves only config-listed keys, dynamically imports handlers, calls them with a uniform signature, returns per-task result dicts; unknown keys and missing handlers are skipped or recorded without raising; Style D found/recorded emits when `debug=True`.

1. In `src/core/contact.py` module docstring, add AST-1515 line: contact-task markup parse/dispatch + same-event follow-up turn.

2. Update imports: add `import re` and `import importlib` at top; add `CONTACT_TASK_CONFIG` to the `src.utils.config` import line.

3. Add compiled markup regex as module constant `_CONTACT_TASK_MARKUP_RE`:

```python
_CONTACT_TASK_MARKUP_RE = re.compile(
    r"~~/([a-z][a-z0-9_]*)\s*(.*?)\s*~~",
    re.DOTALL,
)
```

   ⚠️ **Decision:** Parameters are the remainder of the line between key and closing `~~` (trimmed). Supports URLs, pasted text, and patterns with spaces. Unknown keys outside `CONTACT_TASK_CONFIG` are parsed but not dispatched (AC1).

4. Add public helpers (before `run_contact_estelle_turn`):

```python
def contact_tasks() -> Dict[str, Any]:
    """Shallow copy of CONTACT_TASK_CONFIG allowlist."""
    return dict(CONTACT_TASK_CONFIG)


def parse_contact_task_markup(text: str) -> List[Tuple[str, str]]:
    """Return ordered (task_key, param) pairs from Estelle reply markup."""
    raw = text if isinstance(text, str) else ""
    out: List[Tuple[str, str]] = []
    for m in _CONTACT_TASK_MARKUP_RE.finditer(raw):
        key = (m.group(1) or "").strip()
        param = (m.group(2) or "").strip()
        if key:
            out.append((key, param))
    return out


def strip_contact_task_markup(text: str) -> str:
    """Remove all contact-task markup spans; collapse runs of blank lines to one."""
    raw = text if isinstance(text, str) else ""
    stripped = _CONTACT_TASK_MARKUP_RE.sub("", raw)
    stripped = re.sub(r"\n{3,}", "\n\n", stripped)
    return stripped.strip()
```

5. Add private **`_resolve_contact_task_handler(handler: str)`** using `importlib`:

   - Split on last `.` → `(module_path, attr_name)`.
   - `importlib.import_module(module_path)` then `getattr(mod, attr_name)`.
   - On `ImportError`, `AttributeError`, or `ValueError`: return `None` (caller records `handler_unavailable`).

6. Add public **`run_contact_task_dispatch`**:

```python
def run_contact_task_dispatch(
    *,
    astral_candidate_id: str,
    markup_spans: List[Tuple[str, str]],
    debug: bool = False,
) -> List[Dict[str, Any]]:
```

   Behavior:

   - `log = get_logger(__name__)`; `log.set_debug_flag(debug)`.
   - `total = len(markup_spans)`; iterate with 1-based `index`.
   - Skip spans whose `task_key` ∉ `CONTACT_TASK_CONFIG` (no result row — AC1 unknown keys not executed).
   - If `requires_candidate` and no non-empty `astral_candidate_id`: append `{"ok": False, "error": "no_candidate", "task_key": key}`; Style D when debug.
   - Resolve handler; if `None`: append `{"ok": False, "error": "handler_unavailable", "task_key": key}`; continue.
   - Call handler with **`handler(astral_candidate_id, param, debug=debug)`** — sync or async:
     - If `asyncio.iscoroutinefunction(handler)`: `result = asyncio.run(handler(...))`.
     - Else: `result = handler(...)`.
   - Normalize return: if not `dict`, wrap as `{"ok": True, "result": result}`; else pass through and ensure `task_key` key set.
   - On exception: append `{"ok": False, "error": str(exc), "task_key": key}` — turn stays alive.
   - **Style D (debug=True only):** per span — `debug_index` with `func="contact.run_contact_task_dispatch"`, universal `index N/M`, `identifier=task_key`, outcome `found` then `recorded`; `debug_detail` with `param=` (via `truncate_debug_content` when long) and result summary (`ok=`, `error=` or truncated payload via `truncate_debug_content(json.dumps(...))`).

   ⚠️ **Decision — no sibling file edits:** Handlers live in gazer/meteorite/tracker (siblings). Missing handlers return `handler_unavailable` until siblings land — framework is testable without stub modules in this ticket.

   ⚠️ **Decision — handler contract:** Siblings implement `def contact_task_…(astral_candidate_id: str, param: str, *, debug: bool = False) -> dict` (async allowed). Contact dispatch owns `asyncio.run` for async handlers.

7. Do **not** wire into `run_contact_estelle_turn` yet (Stage 3).

## Stage 3: Turn integration — strip, dispatch, follow-up, Slack post

**Done when:** `run_contact_estelle_turn` parses markup from the first turn reply, strips it before Slack post, dispatches allowlisted tasks, runs at most one follow-up `do_task(contact_estelle_turn)` when any listed task was dispatched, uses the follow-up stripped reply for Slack when follow-up runs, injects contact-task catalog into live_content, and returns `contact_task_results` on the turn dict. `land_calls` and `skill_calls` behavior unchanged. Markup from the follow-up turn is stripped but **not** re-dispatched (one dispatch round per inbound event).

1. In `run_contact_estelle_turn` live_content builder (~lines 841–868), after the ACL skills block and **before** `## Land meteorite`, append:

```
## Available contact tasks (markup)
Embed instructions in agent_payload.reply only — not skill_calls.
Syntax: ~~/<task_key> <parameters>~~
Only use task keys listed below. Contact executes markup after your turn and strips it from the Slack-visible reply. Do not paste raw task payloads into reply — stay conversational.
```

   Then loop `for task_key, meta in contact_tasks().items():` append `- {task_key}: {description} | param: {param_hint}`.

2. After step **d** (`do_task` + `conversational_turn_from_do_task_result`), before skill_calls:

   a. `reply_raw = turn.get("reply")` (string or empty).  
   b. `markup_spans = parse_contact_task_markup(reply_raw)`.  
   c. `reply_stripped = strip_contact_task_markup(reply_raw)`.  
   d. `contact_task_results = run_contact_task_dispatch(astral_candidate_id=astral_candidate_id or "", markup_spans=markup_spans, debug=debug)`.

3. **Follow-up turn (same event, at most once):** When `markup_spans` contains at least one span whose `task_key` ∈ `CONTACT_TASK_CONFIG`:

   a. Build `follow_live_content` starting with the same header fields as the original turn (channel, thread, candidate, state).  
   b. Append `## Contact task results (same inbound event)` and for each result JSON-line (compact `json.dumps`, no pretty-print) via `truncate_debug_content` chunks if needed for live_content size — use `_trim` helper already in function.  
   c. Append `## Conversation` + history + latest inbound (same trim rules as first turn).  
   d. Second `asyncio.run(do_task(task_key, live_content=follow_live_content, index=astral_candidate_id or channel, candidate_data=candidate_data, debug=debug, store_agent_data=True))`.  
   e. `follow_turn = conversational_turn_from_do_task_result(follow_result)`.  
   f. `reply_for_slack = strip_contact_task_markup(follow_turn.get("reply") or "")`.  
   g. Use `follow_turn` for outcome/success/admin_aside; do **not** merge skill_calls/land_calls from follow-up parsed_response into execution (follow-up is narrative only).

   If no listed markup spans, `reply_for_slack = reply_stripped` and skip follow-up.

4. Replace step **f** outbound logic to use `reply_for_slack` instead of raw `reply`:

   - `reply_ok` checks `reply_for_slack` non-empty after strip.  
   - `format_contact_reply_text(reply_for_slack)` → `contact_post_message`.

5. Extend turn return dict with `"contact_task_results": contact_task_results` (list, possibly empty).

6. Extend step **h** Style D recorded bookend `debug_detail` to include `contact_tasks={len(contact_task_results)} contact_task_ok={...}` counts.

7. Do **not** remove AST-1471 `land_calls` block or processing — parallel paths until epic retires land_calls in a future ticket.

## Stage 4: `contact_estelle_turn` prompt contract

**Done when:** `data/admin/agent_task.json` row `contact_estelle_turn` teaches markup syntax, lists that Contact executes `~~/…~~` from reply (not JSON fields), names the six task keys at a high level, and reinforces conversational reply without raw payloads. `user_prompt` may add one line pointing at the live_content contact-task section.

1. In `contact_estelle_turn` **`system_prompt`**, after the existing `skill_calls` paragraph, append (preserve JSON-only envelope rules):

```
Contact tasks (AST-1414): when you need backend work (scrape a URL, land a meteorite, read job/company/candidate data), embed markup inside agent_payload.reply:
  ~~/<task_key> <parameters>~~
Use only task keys from the "Available contact tasks (markup)" section in live_content. You may include multiple markup spans in one reply. Contact strips markup before Slack users see your message and runs tasks after your turn; a follow-up turn may run in the same event with results — summarize outcomes conversationally in that follow-up, never paste raw JSON payloads to the user.
Do not put markup in skill_calls or other JSON fields. skill_calls remain for ACL entity-save only.
```

2. In **`user_prompt`**, after the live_content sentence, add: `When the context block lists contact tasks, prefer markup in reply over inventing data.`

3. Do **not** add markup fields to `TASK_CONFIG["contact_estelle_turn"]["response_schema"]` — markup stays in the reply string per `pattern.core.contact-task-markup`.

4. Touch **only** the `contact_estelle_turn` row in `agent_task.json` — no unrelated task normalization.

## Execution contract

- Execute stages and steps in order; one commit per stage on epic worktree; push `git push origin HEAD:sub/AST-1414/AST-1515-contact-task-config-markup-parse-dispatch` after each.
- No files outside Files Changed.
- Handler import failures are expected until siblings AST-1516–1518 land — do not add stub handlers in gazer/meteorite/tracker in this ticket.
- Ambiguity or missing AST-1073 turn hooks → stop, comment on **AST-1515** with Stage blocked format, wait.
- Test tree / bible: Betty only — engineer does not edit `tests/` or `docs/test-bible/**`.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Revisions

Revision 1 — 2026-08-27  
Driven by: Joan `[plan-discuss] round=1 concern` — fix-now on Stage 1 step 3 handler assert bullet  
Changes: Replaced "exactly one `.`" assert with last-dot split + non-empty module/attr + `module_path.startswith("src.core.")` to match Stage 2 `_resolve_contact_task_handler`.

## Joan validate

[plan-discuss] round=1 concern
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1515
**Overall:** REVISE
**Publish ref:** `sub/AST-1414/AST-1515-contact-task-config-markup-parse-dispatch` @ `ab96557a05151fff1be88d3892409791b070cef8`

## Traceability
AC1→S1,S2,S3; AC2→S3,S4; AC3→S2,S3; parent AC2–6→N/A (sibling handlers); all stages map to parent Purpose/Functional scope slice for markup/dispatch framework.

## Findings

### fix-now — Stage 1 step 3, handler assert bullet
**Finding:** Assert text says handler strings contain **exactly one** `.` separating module path from attribute, but the example (`src.core.gazer.contact_task_gazer_scrape`) has three dots, and Stage 2 step 5 correctly splits on the **last** `.`. Implementing the assert as written (`count('.') == 1`) will fail at import for every registered handler.
**Recommendation:** Rewrite the assert to match resolution logic: handler must be a non-empty str containing at least one `.`; split on last `.` yields non-empty module path and attribute; optionally assert module path starts with `src.core.`.

### discuss — Citations / `pattern.core.contact-task-markup`
**Finding:** Child cites `pattern.core.contact-task-markup` (proposed); no matching file under `canon/patterns/**`. Parent epic explicitly assigns child #1 to introduce it — acceptable for build, but catalog entry is not drafted yet.
**Recommendation:** No plan change required before build; flag for Archie pattern draft/approval track parallel to implementation (parent already names it proposed).

### acceptable — Scope, layers, config, debug
Files Changed and stages stay inside ticket **## Scope**; no sibling file edits; `CONTACT_TASK_CONFIG` + collision asserts mirror existing `CONTACT_CONFIG` / `TASK_CONFIG` discipline; Style D dispatch logging is `debug=True`-gated; follow-up uses `do_task` (not direct Anthropic I/O); `land_calls` / `skill_calls` paths preserved.

context_tokens≈32000

## Joan validate (round 2)

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1515
**Overall:** APPROVED
**Publish ref:** `sub/AST-1414/AST-1515-contact-task-config-markup-parse-dispatch` @ `79aebd465e4e0fdc635d3bfec7f6c08c19c31177`

## Traceability
AC1→S1,S2,S3; AC2→S3,S4; AC3→S2,S3; parent AC2–6→N/A (sibling handlers); all stages map to parent Purpose/Functional scope slice for markup/dispatch framework.

## Findings

### acceptable — Revision 1 (handler assert)
Stage 1 step 3 now matches Stage 2 `_resolve_contact_task_handler`: at least one `.`, split on last dot, non-empty module/attr, `module_path.startswith("src.core.")`. Prior fix-now closed.

### acceptable — `pattern.core.contact-task-markup` (proposed)
No `canon/patterns/**` draft yet; parent epic explicitly assigns child #1 to introduce it. Plan shape is documented inline; does not block framework build.

### acceptable — Scope, layers, config, debug
Files Changed and stages stay inside ticket **## Scope**; no sibling file edits; `CONTACT_TASK_CONFIG` + collision asserts mirror `CONTACT_CONFIG` / `TASK_CONFIG` discipline; Style D dispatch logging is `debug=True`-gated; follow-up uses `do_task`; `land_calls` / `skill_calls` preserved.

context_tokens≈38000
