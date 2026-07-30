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

## Review (build stub)

**Publish ref:** `origin/sub/AST-1046/AST-1072-conversational-agent-envelope`
**Plan path:** `docs/features/contact/ast-1072-conversational-agent-envelope.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–3 | `af00f02a` | CHAT envelope schema + do_task contract + contact_estelle_turn seed |

**Tip:** `f6ce687e17ad39df28ce5182139d5240e1470a67` on `origin/sub/AST-1046/AST-1072-conversational-agent-envelope`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1

**Rubric:** code-rubric.v1  
**Ticket:** AST-1072  
**Publish ref (pre-docs tip):** `912dc2c721c950f215300ce9eb8e8a901e6c4990`  
**Overall:** DISCUSS

### What’s solid

- CHAT-only `CONVERSATIONAL_PERFORMANCE_SCHEMA` / `CONTACT_ESTELLE_CONFIG` leave `BASE_SCHEMA` and Estelle Big/upshot intact; brain override gated by `is_conversational_task`.
- Concern requires non-empty `admin_aside` and is not treated as `Agent failure`; failure still short-circuits `do_task` with `success=False`.
- Style D turn-outcome `debug_index` + `|` detail gated on `debug=True`; lengths only (no full reply/aside blobs).
- Boundaries held: no Slack / turn-loop / `src/external` / Estelle agent-row brain mutation; Betty owns test-tree via one `merge-tests`.

### Issues

**discuss (C4 straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` at plan time; all three are in-scope on `origin/dev...origin/sub/...` (plan file + Betty test-tree). Each scores **conforms** on the product diff — straggler callout only, no product fix.

**advisory:** Validation-failure debug path labels `outcome="validation error"` for both schema errors and CHAT `status=failure` short-circuits; detail still emits. Prefer `failure` when the envelope status is failure if AST-1073 operators rely on the index outcome string.

### Recommended actions

- Engineer: no fix-now. Acknowledge stragglers / optional advisory polish, then proceed to User Testing when ready.
- No product or test-tree edits from Radia.

### Pattern conformance

| Cited id | Verdict |
|----------|---------|
| `pattern.agent.conversational-envelope` | conforms |
| `pattern.config.config-block` | conforms |
| `astral.agent.do-task-delegation` | conforms (also statute) |
| `astral.standards.debug-contract-gated` | conforms (also statute) |
| `astral.layers.core-vs-external-bright-line` | conforms (also statute) |

### Plan adherence

Diff matches Self-Assessment Single-Component / high / Medium: config + `do_task` CHAT contract + one `agent_task` seed. Sibling AST-1073 / AST-1043 scope not smuggled. Review stub tip hash was stale vs merge-tests tip (docs note only).

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | No graded confidence / scoring path touched |
| astral.agent.do-task-delegation | scoped | conforms | Envelope via `do_task`; no new direct Anthropic assembly |
| astral.agent.grade-vector-validation | scoped | conforms | No vectors / grade tasks |
| astral.batch.batch-id-first | scoped | conforms | No batch claim/process work |
| astral.batch.batch-id-format | scoped | conforms | No batch_id invention |
| astral.batch.claim-process-release | scoped | conforms | No dispatcher batch work |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Relies on existing do_task storage path |
| astral.config.config-source-of-truth | scoped | conforms | Outcomes/schema/brain in config; BASE_SCHEMA untouched |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring/dispatch floor changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env for brain default |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths ∩ artifacts/spikes empty |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan doc in docs/features; not spike notes (C4 straggler) |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/contact/ast-1072-….md` (C4 straggler) |
| astral.git.betty-no-src-or-features | scoped | conforms | Engineer owns src/features; Betty did not touch them |
| astral.git.engineer-test-tree-ban | scoped | conforms | tests/bible via Betty `test` + one merge-tests (C4 straggler) |
| astral.layers.core-vs-external-bright-line | scoped | conforms | utils + core only; Slack/external left to siblings |
| astral.layers.import-direction | scoped | conforms | core→utils imports; no layer inversion |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers ∩ scripts empty |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Config block; no UI business rules |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check work |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult/render_verdict work |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers ∩ ui empty |
| astral.standards.data-raises-caller-logs | scoped | conforms | No data-layer Python; admin JSON seed only |
| astral.standards.database-header-inventory | scoped | not-applicable | layers ∩ data empty |
| astral.standards.debug-contract-gated | scoped | conforms | Style D only when debug=True; lengths not full blobs |
| astral.standards.dry-and-focused-functions | scoped | conforms | Single schema + `is_conversational_task` gate |
| astral.standards.in-scope-only | scoped | conforms | Envelope contract only; Slack/turn loop excluded |
| astral.standards.logging-via-utils | scoped | conforms | Uses existing `_do_task_debug_logger` helpers |
| astral.standards.no-cross-contamination | scoped | conforms | Stays utils/core + admin seed |
| astral.standards.no-hardcoded-sets | scoped | conforms | `CONVERSATIONAL_OUTCOMES` / schema in config |
| astral.standards.public-then-helpers | scoped | conforms | Helpers colocated with validation; matches agent.py layout |
| astral.standards.utils-data-late-import-only | scoped | conforms | No new utils→data import |
| astral.state.core-decides-transitions | scoped | conforms | No state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state work |
| astral.state.no-daisy-chain-in-run | scoped | conforms | No run_next chain work |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers ∩ ui frontend empty |
| astral.ui.naming-conventions | scoped | not-applicable | layers ∩ ui empty |
| astral.ui.single-gunicorn-worker | scoped | conforms | Touches config.py but not worker/RAILWAY |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Exactly one merge-tests SHA on sub |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Publish on origin/sub only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1046/AST-1072-…` |
| orch.git.merge-on-checkout | universal | conforms | No illegal merge recipe in diff |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in history |
| orch.git.no-dev-agent-branches | universal | conforms | Uses sub publish-ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree astral-AST-1046 |
| orch.git.three-permanent-branches | universal | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Plan decisions explicit; no open product Q |
| orch.pipeline.plan-is-bible | universal | conforms | Stages + Files Changed match diff |
| orch.pipeline.project-scoped-queues | universal | conforms | Contact child scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | No canon/statutes edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty test + merge-tests ownership |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee Ada through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer remains assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | No banned path commits by engineer |

**Notes:** Joan plan-rubric APPROVED attached. C4 stragglers listed under Issues. Active statute count = 56.

context_tokens≈52000
)
