# DeepSeek Big output budget

- **Linear:** [AST-1391](https://linear.app/astralcareermatch/issue/AST-1391)
- **Parent:** [AST-1390](https://linear.app/astralcareermatch/issue/AST-1390)
- **Publish ref:** `sub/AST-1390/AST-1391-deepseek-big-output-budget`

Big-brain DeepSeek hops currently share the modest v4-pro SKU default (`default_max_tokens: 16000`) with Medium, then often get capped further by a stored agent-row value. Thinking and the visible answer share that budget, so Big cannot actually think and finish. This ticket puts **384000** on the DeepSeek **Big** tier in config and applies it as a **floor** on the shared `do_task` hop when the active provider is DeepSeek and the resolved brain is Big.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `max_tokens: 384000` on DeepSeek `BRAIN_BIG` only; add `deepseek_brain_max_tokens_floor` | utils |
| `src/core/agent.py` | After existing craft floor, apply that helper as a floor on DeepSeek hops | core |

Do **not** edit: `src/external/deepseek.py`, `src/external/anthropic.py`, `DEEPSEEK_MODEL_PRICING`, Anthropic `AGENT_CONFIG`, `src/ui/api/api_admin.py` (`_resolve_adhoc` / catalog), `PROVIDER_CALL_BUDGET`, thinking / temperature / top_p, `tests/`, bible.

## Stages

### Stage 1: Named 384000 on the DeepSeek Big tier

**Done when:** `resolve_brain_setting_to_deepseek_tier_meta(BRAIN_BIG)["max_tokens"] == 384000`; Little and Medium dicts still have **no** `max_tokens` key; `DEEPSEEK_MODEL_PRICING["deepseek-v4-pro"]["default_max_tokens"]` is still `16000`; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, inside `LLM_PROVIDER_CONFIG["tier_map"]["deepseek"][BRAIN_BIG]` (the existing dict that already has `vendor_model`, `thinking`, `reasoning_effort`), add exactly one new key after `reasoning_effort`:

   ```python
   BRAIN_BIG: {
       "vendor_model": "deepseek-v4-pro",
       "thinking": True,
       "reasoning_effort": "max",
       "max_tokens": 384000,  # AST-1391: hop output floor; not the shared v4-pro SKU default
   },
   ```

2. Do **not** add `max_tokens` to `BRAIN_LITTLE` or `BRAIN_MEDIUM`. Do **not** change `DEEPSEEK_MODEL_PRICING` (Medium shares `deepseek-v4-pro` and must keep `default_max_tokens: 16000`). Do **not** change `tier_map["anthropic"]` or any `AGENT_CONFIG` `default_max_tokens`.

3. Immediately after `resolve_brain_setting_to_deepseek_tier_meta` (same config section, before `validate_llm_provider_environment`), add this helper — no other new public functions:

   ```python
   def deepseek_brain_max_tokens_floor(brain_setting: str) -> Optional[int]:
       """AST-1391: DeepSeek tier output-token floor, or None when the tier has none."""
       validate_allowed_brain_setting(brain_setting)
       raw = (
           LLM_PROVIDER_CONFIG["tier_map"]
           .get("deepseek", {})
           .get(brain_setting, {})
           .get("max_tokens")
       )
       if raw is None:
           return None
       return int(raw)
   ```

   `Optional` is already imported in `config.py`. `validate_allowed_brain_setting` already rejects unknown brains.

4. Do **not** strip `max_tokens` from `resolve_brain_setting_to_deepseek_tier_meta`'s returned dict (it already `dict()`-copies the whole tier). `send_to_deepseek` currently reads only `thinking` and `reasoning_effort` from `tier_meta`; leave that as-is.

⚠️ **Decision:** The 384000 lives on the DeepSeek **Big tier dict**, not on `DEEPSEEK_MODEL_PRICING["deepseek-v4-pro"]`. Raising the SKU default would raise Medium too (parent Boundary). The helper reads the live `tier_map` so the floor is config-driven (`pattern.config.config-block`, `astral.config.config-source-of-truth`) rather than a second module-level constant that can drift from the dict.

⚠️ **Decision:** Key name is `max_tokens` (not `default_max_tokens`) so it cannot be confused with the SKU pricing default that `do_task` already uses when the agent row has no stored max.

### Stage 2: Apply the floor on the shared `do_task` hop

**Done when:** A DeepSeek Big `do_task` hop passes `max_tokens` of at least 384000 into `send_to_deepseek`, including when the agent row's stored max is 16000 (or 100). A DeepSeek Medium hop still sends the current Medium budget (agent-row or v4-pro `16000`), not 384000. A DeepSeek Little hop is unchanged. An Anthropic Big hop still uses the existing Anthropic path (`send_to_anthropic` with Opus `default_max_tokens` / agent-row / craft floor) — never 384000. With `debug=True`, the existing `do_task` max-tokens debug line and `llm_params` Style D line show the floored value. Craft-rubric DeepSeek Big hops still force `tier_meta.thinking=False` / `reasoning_effort=None` (AST-1380 Decision A) and may send 384000 because the Big floor is higher than `CRAFT_RUBRIC_MAX_TOKENS`.

1. In `src/core/agent.py`, add `deepseek_brain_max_tokens_floor` to the existing `from src.utils.config import (` block (alphabetically-adjacent to `resolve_brain_setting_to_deepseek_tier_meta` is fine; do not import `LLM_PROVIDER_CONFIG` or `BRAIN_BIG` into `agent.py`).

2. In `do_task`, immediately **after** the existing AST-903 / AST-1380 block that currently looks like:

   ```python
   agent_max_tokens = agent_row.get("max_tokens") if agent_row.get("max_tokens") is not None else model_cfg["default_max_tokens"]
   if task_key in CRAFT_RUBRIC_UI_TASK_KEYS:
       agent_max_tokens = max(int(agent_max_tokens), int(CRAFT_RUBRIC_MAX_TOKENS))
       if provider == "deepseek" and tier_meta is not None:
           tier_meta = {**tier_meta, "thinking": False, "reasoning_effort": None}
   ```

   insert:

   ```python
   if provider == "deepseek":
       _ds_floor = deepseek_brain_max_tokens_floor(brain_setting)
       if _ds_floor is not None:
           agent_max_tokens = max(int(agent_max_tokens), _ds_floor)
   ```

   Order is mandatory: agent-row / SKU default → craft 32000 floor (craft keys only) → DeepSeek Big 384000 floor. Result for DeepSeek Big craft: `max(max(agent_or_sku, 32000), 384000) = 384000`. Result when the agent row is already higher than 384000: the agent-row value wins (floor, not cap).

3. Do **not** add a new debug line. The existing `debug=True` `logger.info("[DEBUG] do_task(...) max_tokens=%s ...")` and the Style D `llm_params ... max_tokens=...` already print `agent_max_tokens` **after** this site; they will show 384000 (or higher) once the floor runs. Do **not** emit those lines when `debug=False`.

4. Do **not** change the `send_to_deepseek` / `send_to_anthropic` call sites except that they already pass `max_tokens=agent_max_tokens` — keep that. Do **not** teach `send_to_deepseek` to read `tier_meta["max_tokens"]`; core owns the resolved int (`astral.layers.core-vs-external-bright-line`, `astral.agent.do-task-delegation`).

5. Do **not** apply this floor in `run_adhoc` or `src/ui/api/api_admin.py` `_resolve_adhoc`. Those are Admin workbench paths; this ticket's Boundaries exclude Admin UI / seed backfill. The representative hop is `do_task`.

6. Do **not** change AST-1380 Decision A (the thinking-off copy inside the craft `if`). Do **not** change `CRAFT_RUBRIC_MAX_TOKENS`. Do **not** change thinking, temperature, top_p, or `PROVIDER_CALL_BUDGET`. Do **not** edit `tests/` or `docs/test-bible/**` — Betty owns those. Existing component test `TestAst1380CraftRubricThinkingOffAndFailureBanner::test_craft_get_rubric_deepseek_big_forces_thinking_false` currently asserts `max_tokens == CRAFT_RUBRIC_MAX_TOKENS` (32000) for a DeepSeek Big craft hop; after this stage that hop sends 384000 (AC 6). Leave the test red for Betty — do not patch it.

⚠️ **Decision:** Floor from `deepseek_brain_max_tokens_floor(brain_setting)` (live `tier_map`), not from `tier_meta.get("max_tokens")`. Several existing tests stub `resolve_brain_setting_to_deepseek_tier_meta` with a thinking-only dict; reading the stub would silently skip the product floor. The helper keys off the resolved `brain_setting` (already Medium for conversational Estelle via `CONTACT_ESTELLE_CONFIG` **before** this site), so chat hops do not pick up Big.

⚠️ **Decision:** Skip `run_adhoc` / `_resolve_adhoc`. Ticket owns the shared agent hop (`do_task`) only. Applying the floor in Admin adhoc would be sibling-scope.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1391
**Overall:** APPROVED
**Publish ref:** `sub/AST-1390/AST-1391-deepseek-big-output-budget` @ `a1d04410`

## Traceability
AC1→S1,S2 | AC2→S2 | AC3→S1,S2 | AC4→S2 | AC5→S2 | AC6→S2

## Findings

### acceptable
- **Location:** Stage 2 step 6 — `test_craft_get_rubric_deepseek_big_forces_thinking_false`
- **Finding:** Craft DeepSeek Big test currently asserts `max_tokens == CRAFT_RUBRIC_MAX_TOKENS` (32000); post-build it should expect 384000 per AC6.
- **Recommendation:** Engineer leaves test red; Betty updates assertion on qa-child — consistent with `astral.git.engineer-test-tree-ban` and plan boundary.

No `fix-now` or `discuss` findings. In-session R3: universal orchestration set + scoped statutes (`astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.agent.do-task-delegation`, `astral.layers.core-vs-external-bright-line`, `astral.layers.import-direction`, `astral.standards.in-scope-only`, `astral.standards.debug-contract-gated`) all **conform**. Cited patterns (`pattern.config.config-block`, `pattern.layers.import-discipline`) match solution shape.

**R6 checklist (summary):** Definition fidelity ✓ — two-file footprint (`config.py` literal + `agent.py` floor), layer imports respected, 384000 not on shared v4-pro SKU default, craft/AST-1380 ordering preserved, `run_adhoc`/`_resolve_adhoc` explicitly out of boundary, no scope creep into siblings. Plan matches current `do_task` insertion site (post craft floor, pre debug/provider call).

context_tokens≈42000
