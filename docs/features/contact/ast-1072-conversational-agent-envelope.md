# AST-1072 — Conversational agent envelope (success / failure / concern)

**Linear:** [AST-1072](https://linear.app/astralcareermatch/issue/AST-1072/conversational-agent-envelope-success-failure-concern-contact-estelle)  
**Parent:** [AST-1046](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope)  
**Publish ref:** `sub/AST-1046/AST-1072-conversational-agent-envelope`

Schema + `do_task` contract for a conversational turn envelope with outcomes **success** | **failure** | **concern**. A **concern** outcome carries a short admin-visible aside about user struggle / negative experience. This ticket does **not** wire Slack, Contact resolve, listen gate, or the Estelle turn loop (AST-1073).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CONVERSATIONAL_OUTCOMES`, `CONVERSATIONAL_PERFORMANCE_SCHEMA`, `CONTACT_ESTELLE_CONFIG`, `is_conversational_task` / helpers; register `contact_estelle_turn` in `TASK_CONFIG` with `task_type="CHAT"` | utils |
| `src/core/agent.py` | CHAT-aware envelope validation (concern ≠ hard failure; `admin_aside` required on concern); preserve turn outcome on `do_task` result; brain override from `CONTACT_ESTELLE_CONFIG`; Style D debug for turn outcomes; `stringify_response_schema` path via config uses conversational performance schema for CHAT | core |
| `data/admin/agent_task.json` | Add minimal `contact_estelle_turn` row (`agent_id=principal_recruiter_estelle`) with envelope instructions in prompts so `do_task` can resolve the task | data/admin seed |

**Out of plan (sibling AST-1073 / AST-1043):** Slack Events, Manage Slack listen gate, resolve-util, Slack context cache, Contact ACL skills, Estelle turn loop orchestration, changing `principal_recruiter_estelle.brain_setting` globally (stays **Big** for upshot).

## Stage 1: Config — conversational envelope + CHAT task registration

**Done when:** `TASK_CONFIG["contact_estelle_turn"]` exists with `task_type="CHAT"`, conversational performance schema constants are importable, and `CONTACT_ESTELLE_CONFIG["default_brain_setting"] == BRAIN_MEDIUM`. Non-CHAT tasks still use `BASE_SCHEMA` (`success` \| `failure` only).

1. In `src/utils/config.py`, immediately after `BASE_SCHEMA`, add:

```python
CONVERSATIONAL_OUTCOMES = ("success", "failure", "concern")

# agent_performance shape for task_type=CHAT only — do not mutate BASE_SCHEMA.
CONVERSATIONAL_PERFORMANCE_SCHEMA = {
    "status": {
        "type": "str",
        "required": True,
        "enum": list(CONVERSATIONAL_OUTCOMES),
    },
    "failure_note": {"type": "str", "required": False},
    "admin_aside": {"type": "str", "required": False},
}

CONTACT_ESTELLE_CONFIG = {
    # Conversational Contact turns default Medium / non-thinking (DeepSeek tier_map).
    # Do not change principal_recruiter_estelle.brain_setting (Big) used by analysis_upshot.
    "default_brain_setting": BRAIN_MEDIUM,
    "task_key": "contact_estelle_turn",
}
```

   Place `CONTACT_ESTELLE_CONFIG` **after** `BRAIN_MEDIUM` is defined (or set `"default_brain_setting": "Medium"` literal matching `BRAIN_MEDIUM` and assert equality in a one-liner next to `LLM_PROVIDER_CONFIG` if forward-reference is awkward). Prefer literal `"Medium"` plus a module-level assert after `BRAIN_MEDIUM` exists: `assert CONTACT_ESTELLE_CONFIG["default_brain_setting"] == BRAIN_MEDIUM`.

2. Add helper (same file, near other task helpers):

```python
def is_conversational_task(task_key: str) -> bool:
    cfg = TASK_CONFIG.get(task_key) or {}
    return cfg.get("task_type") == "CHAT"
```

3. Register `TASK_CONFIG["contact_estelle_turn"]` (near other task entries; no dispatch `trigger_state`):

```python
"contact_estelle_turn": {
    "print_label": "Contact Estelle Turn",
    "response_format": "json",
    "response_schema": {
        "reply": {"type": "str", "required": True},
    },
    "entity_type": None,
    "requires_candidate_key": False,
    "trigger_state": None,
    "task_type": "CHAT",
    "agent_task": "contact_estelle_turn",
},
```

⚠️ **Decision:** Conversational turn outcome lives in **`agent_performance.status`** (`success` \| `failure` \| `concern`), parallel to rubric `agent_performance`, not as a payload field. Payload is user-facing `reply` only. **Do not** extend global `BASE_SCHEMA` — only `task_type=="CHAT"` uses `CONVERSATIONAL_PERFORMANCE_SCHEMA`.

⚠️ **Decision:** Task key `contact_estelle_turn` is the sole CHAT registration in this ticket. AST-1073 consumes it; do not invent additional CHAT keys here.

## Stage 2: `do_task` contract — validate, preserve outcome, brain, debug

**Done when:** For `contact_estelle_turn`, (a) `status=failure` still fails `do_task` with `success=False`; (b) `status=concern` with non-empty `admin_aside` yields `success=True` and exposes outcome + aside on the result; (c) `status=concern` without `admin_aside` fails validation; (d) brain used for this task is Medium from config, not Estelle’s Big; (e) `debug=True` emits Style D index + `|` detail for the turn outcome; (f) `stringify_response_schema("contact_estelle_turn")` shows conversational performance enum including `concern`.

1. In `stringify_response_schema` (`config.py`): when `is_conversational_task(task_key)`, build envelope with `_schema_to_example(CONVERSATIONAL_PERFORMANCE_SCHEMA)` instead of `BASE_SCHEMA`. Leave all other tasks unchanged.

2. In `src/core/agent.py`, extend `_validate_response_schema` (or add a CHAT branch called from it) so that when `is_conversational_task(task_key)`:

   - Validate `agent_performance` against `CONVERSATIONAL_PERFORMANCE_SCHEMA` field types/enum (reuse `_validate_schema_object_fields` on the performance dict, or mirror BASE checks).
   - If `status == "failure"`: keep today’s behavior — return error string `Agent failure: …` (short-circuit; do not validate payload as success path).
   - If `status == "concern"`: require `admin_aside` to be a non-empty stripped string; else return `"Conversational concern requires non-empty admin_aside"`. Do **not** treat concern as `Agent failure`.
   - If `status == "success"`: `admin_aside` optional; empty/omitted OK.
   - Then validate `agent_payload` against the task `response_schema` as today (`reply` required).

   Pass `task_key` into validation (signature already has it). Non-CHAT tasks: unchanged `BASE_SCHEMA` path (`success` \| `failure` only).

3. Before the existing unwrap `parsed = parsed["agent_payload"]` (around the post-validation success path), when `is_conversational_task(task_key)` and the envelope snapshot still has `agent_performance`:

   - Set `result["agent_performance"] =` the performance dict (status / failure_note / admin_aside).
   - Set `result["conversational_outcome"] =` normalized status string (`success` \| `failure` \| `concern`).
   - Then unwrap payload into `parsed_response` as today so callers still get flat `{ "reply": ... }`.

4. Add a small public helper in `agent.py` (or `config.py` if pure):

```python
def conversational_turn_from_do_task_result(result: dict) -> dict:
    """Shape for AST-1073: outcome, reply, admin_aside, success."""
    ...
```

   Return at least: `success` (bool from result), `outcome` (from `conversational_outcome` or inferred), `reply` (from `parsed_response`), `admin_aside` (from `agent_performance`).

5. Brain override: after resolving `brain_setting` from `agent_row` in `do_task`, if `is_conversational_task(task_key)`:

```python
brain_setting = CONTACT_ESTELLE_CONFIG["default_brain_setting"]
```

   ⚠️ **Decision:** Override only for conversational CHAT tasks. Do **not** edit `data/admin/agent.json` Estelle `brain_setting` (remains Big for upshot). Medium maps to DeepSeek non-thinking per existing `LLM_PROVIDER_CONFIG["tier_map"]["deepseek"]`.

6. Debug contract (only when `debug=True`), after conversational outcome is known on the success or validation-failure path for CHAT tasks:

   - `debug_index(func="do_task(contact_estelle_turn)", index=1, total=1, identifier=<index or task_key>, outcome=<status or "validation error">)`
   - `debug_detail(f"conversational_outcome={status} admin_aside_len={n} reply_len={m}")` (lengths only — do not dump full reply/aside blobs without `truncate_debug_content` if ever logging text).

   Gate with existing `_do_task_debug_logger` / `debug` flag. No new ungated `[DEBUG]` info lines.

## Stage 3: Minimal `agent_task` seed for `contact_estelle_turn`

**Done when:** `data/admin/agent_task.json` contains a `task_key=contact_estelle_turn` row bound to `principal_recruiter_estelle`, with prompts that instruct the ternary envelope + `admin_aside` on concern, and repo JSON sync can load it (same shape as sibling rows).

1. Append one object to `data/admin/agent_task.json` following existing row field set (`agent_id`, `task_key`, `task_key_uuid`, `task_name`, `system_prompt`, `cache_prompt` / segments as used by peers, `nocache_prompt`, `user_prompt`, `run_next` empty/`""`, `current` true, group metadata consistent with Estelle tasks).

2. Prompt content must state explicitly:
   - JSON two-key envelope `agent_performance` + `agent_payload`.
   - `agent_performance.status` is exactly one of `success`, `failure`, `concern`.
   - On `concern`, set `admin_aside` to one short sentence for Astral admins about user struggle / negative experience.
   - On `failure`, set `failure_note` (agent could not perform the turn).
   - `agent_payload.reply` is the user-visible message text.
   - Do not put the admin aside in `reply`.

3. Generate a fresh `task_key_uuid` (UUID4). Do not reuse another task’s uuid.

⚠️ **Decision:** Seed is contract-minimal so `do_task("contact_estelle_turn", …)` resolves prompts. AST-1073 owns turn-loop context assembly, Slack wiring, and richer Estelle Contact prompts/skills. Do not expand this seed into ACL/skill catalogs.

## Self-Assessment

**Scope:** `Single-Component` — config schema + `do_task` validation/preserve/brain/debug for one CHAT task; one agent_task seed row. No Slack/UI/dispatcher.

**Conf:** `high` — reuses `agent_performance` / `agent_payload` envelope, reserved `CHAT` task_type, existing Style D debug helpers, and Medium tier mapping already in `LLM_PROVIDER_CONFIG`.

**Risk:** `Medium` — incorrect concern→failure coupling would break callers; brain override bugs could silently use Big/thinking; touching `_validate_response_schema` must not regress non-CHAT tasks. Mitigated by scoping all new branches behind `is_conversational_task`.

## Code rules check

- **§2.1 config:** literals in `CONTACT_ESTELLE_CONFIG` / schemas; no env for brain default.
- **§2.2 do-task-delegation:** core still calls `do_task`; no direct Anthropic assembly in new code.
- **§1.5.1 debug-contract-gated:** Style D only when `debug=True`.
- **§1.3 DRY:** single `CONVERSATIONAL_PERFORMANCE_SCHEMA`; no per-call string enums.
- **Layers:** utils config + core agent only; no `src/data/` debug; Slack stays external/sibling.
)
