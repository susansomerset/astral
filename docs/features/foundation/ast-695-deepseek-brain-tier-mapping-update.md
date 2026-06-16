# AST-695 — DeepSeek brain tier mapping update

**Parent:** [AST-694 — Deepseek brain model changes](https://linear.app/astralcareermatch/issue/AST-694/deepseek-brain-model-changes)  
**Publish ref (origin):** `sub/AST-694/AST-695-deepseek-brain-tier-mapping-update`  
**Ticket:** [AST-695](https://linear.app/astralcareermatch/issue/AST-695/deepseek-brain-tier-mapping-update-deepseek-brain-model-changes)

AST-491 shipped DeepSeek brain tiers (Little / Medium / Big) with **Medium** mapped to `deepseek-v4-flash` + thinking enabled. Susan's updated ladder (AST-694) retargets **Medium** to `deepseek-v4-pro` with thinking disabled, while **Little** stays flash non-thinking and **Big** stays pro with thinking. This ticket corrects the config-driven `tier_map["deepseek"]` table only; runtime dispatch (`do_task`, `run_adhoc`, `send_to_deepseek`) already reads tier meta from config and needs no routing changes when the literals are fixed.

## Files Changed (planned)

Spike output, if any, stays under **`debug/spikes/AST-695/`** only.

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `src/utils/config.py` | Update `LLM_PROVIDER_CONFIG["tier_map"]["deepseek"][BRAIN_MEDIUM]` and the block comment above the deepseek tier entries | utils | engineer |
| `tests/component/utils/test_config.py` | Extend `test_resolve_deepseek_tier_meta` to assert Medium → pro, thinking off; keep Little/Big assertions | tests | Betty (`merge-tests`) |
| `tests/component/core/test_agent.py` | If Betty's manifest includes Medium-tier DeepSeek dispatch assertions, align expected `vendor_model` / `tier_meta` with config | tests | Betty (`merge-tests`) |
| `tests/component/ui/api/test_api_admin.py` | If Betty's manifest includes Medium `_resolve_adhoc` DeepSeek assertions, align expected payload | tests | Betty (`merge-tests`) |

**No changes:** `active_provider`, Anthropic `tier_map`, `DEEPSEEK_MODEL_PRICING` (both SKUs already present), `src/core/agent.py`, `src/external/deepseek.py`, `src/ui/api/api_admin.py`, agent DB rows, TASK_CONFIG, or admin UI tier labels.

## Current vs target (DeepSeek tier_map only)

| Tier | Current (wrong Medium) | Target (AST-694) |
|------|------------------------|------------------|
| Little | `deepseek-v4-flash`, `thinking: False`, `reasoning_effort: None` | unchanged |
| Medium | `deepseek-v4-flash`, `thinking: True`, `reasoning_effort: "high"` | `deepseek-v4-pro`, `thinking: False`, `reasoning_effort: None` |
| Big | `deepseek-v4-pro`, `thinking: True`, `reasoning_effort: "max"` | unchanged |

## Stage 1: Correct DeepSeek Medium tier literals in config

**Done when:** `resolve_brain_setting_to_deepseek_tier_meta(BRAIN_MEDIUM)` returns `vendor_model == "deepseek-v4-pro"` and `thinking is False`; Little and Big meta unchanged; `python3 -m py_compile src/utils/config.py` passes; no other product files modified.

1. In `src/utils/config.py`, locate `LLM_PROVIDER_CONFIG["tier_map"]["deepseek"]` (currently ~lines 2084–2100).
2. Replace the **`BRAIN_MEDIUM`** entry with exactly:

```python
            BRAIN_MEDIUM: {
                "vendor_model": "deepseek-v4-pro",
                "thinking": False,
                "reasoning_effort": None,
            },
```

3. Update the comment immediately above the deepseek tier block from the AST-491 wording (`Little = v4-flash non-thinking; Medium/Big thinking; Big = pro`) to: `# AST-694: Little = v4-flash non-thinking; Medium = v4-pro non-thinking; Big = v4-pro thinking.`
4. Do **not** edit `BRAIN_LITTLE`, `BRAIN_BIG`, `tier_map["anthropic"]`, `DEEPSEEK_MODEL_PRICING`, or `active_provider`.
5. Run `python3 -m py_compile src/utils/config.py`.

⚠️ **Decision:** Medium uses pro **non-thinking** defaults from `DEEPSEEK_MODEL_PRICING["deepseek-v4-pro"]` (`default_max_tokens: 16000`, etc.) via existing `do_task` / `_resolve_adhoc` paths — no separate override dict in this ticket.

⚠️ **Decision:** Big keeps `reasoning_effort: "max"` as shipped; `send_to_deepseek` already maps thinking-on tiers to `output_config.effort` — do not change Big's effort level.

## Verification (test-child / Betty manifest — not build-child)

**Done when:** Betty's `merge-tests` updates land and scoped pytest is green on `origin/sub/AST-694/AST-695-deepseek-brain-tier-mapping-update`.

1. **Config unit tests (Betty):** In `tests/component/utils/test_config.py`, inside `TestAst492LlmBrainTierConfig.test_resolve_deepseek_tier_meta`, add Medium assertions:

   - `medium = cfg.resolve_brain_setting_to_deepseek_tier_meta(cfg.BRAIN_MEDIUM)`
   - `assert medium["vendor_model"] == "deepseek-v4-pro"`
   - `assert medium["thinking"] is False`

   Keep existing Little (flash, thinking off) and Big (pro, thinking on) assertions.

2. **Regression spot-check (test-child):** Run pytest on Betty's manifest rows covering `TestAst492LlmBrainTierConfig`, `TestAst492BrainSettingDoTask`, and `TestAst492ResolveAdhocApiAdmin` — no product edits in `tests/` during **build-child**.

3. **Manual UAT hooks (Susan / prep-uat — reference only):** After deploy, AC 4–5 are satisfied when a Medium-tier adhoc or batch task logs `deepseek-v4-pro` with thinking disabled and a Big-tier task logs `deepseek-v4-pro` with thinking enabled; AC 7 when Anthropic provider smoke still resolves Haiku/Sonnet/Opus aliases.

## Self-Assessment

**Scope:** `minor` — Single config block edit in `src/utils/config.py`; downstream routing and pricing lookup already consume `resolve_brain_setting_to_deepseek_tier_meta`.

**Conf:** `high` — Mapping is fully specified in AST-694/695 descriptions; existing AST-492/493 patterns apply without new modules or API surface.

**Risk:** `Medium` — Wrong Medium literals mis-price calls (flash vs pro) or enable thinking on mid-tier work; mitigated by config unit tests and existing `do_task` / timesheet vendor_model plumbing.

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** Tier strings remain `BRAIN_*` constants; no duplicate tier lists elsewhere.
- **§2.1 config:** All SKU/thinking literals stay in `LLM_PROVIDER_CONFIG`; no env overrides for tier mapping.
- **§2.4 batch processing:** No batch/dispatch changes.
- **§2.6 state machine:** No state machine changes.
- **§3.3 imports:** Config-only edit; no new cross-layer imports.
- **§3.5 naming:** Existing snake_case helpers unchanged.

No conflicts identified.

## Execution contract

- **build-child:** One stage → one `code(AST-695)` commit on epic worktree; publish via `git push origin HEAD:sub/AST-694/AST-695-deepseek-brain-tier-mapping-update`.
- **Do not** edit `tests/` during build — Betty owns manifest + `merge-tests`.
- If `DEEPSEEK_MODEL_PRICING` lacks a row for a tier `vendor_model` after the edit, stop and comment on AST-694 (should not happen — pro row already exists).

## Review stub (Ada — build)

- **Publish ref:** `origin/sub/AST-694/AST-695-deepseek-brain-tier-mapping-update`
- **Product commit:** `code(AST-695)` — Medium tier → `deepseek-v4-pro`, thinking off; AST-694 comment on deepseek tier block.
