<!-- linear-archive: AST-695 archived 2026-06-23 -->

## Linear archive (AST-695)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-695/deepseek-brain-tier-mapping-update-deepseek-brain-model-changes  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-694 — Deepseek brain model changes  
**Blocked by / blocks / related:** parent: AST-694

### Description

## What this implements

Update the config-driven DeepSeek brain tier table so **Little**, **Medium**, and **Big** resolve to Susan's specified vendor models and thinking flags when the active LLM provider is DeepSeek. Runtime agent dispatch continues to resolve tiers from config automatically; this ticket owns the mapping correction and the component tests that assert tier resolution.

## Acceptance criteria

1. With `active_provider` set to DeepSeek, resolving **Little** yields vendor model `deepseek-v4-flash` with thinking disabled.
2. With `active_provider` set to DeepSeek, resolving **Medium** yields vendor model `deepseek-v4-pro` with thinking disabled.
3. With `active_provider` set to DeepSeek, resolving **Big** yields vendor model `deepseek-v4-pro` with thinking enabled.
4. A representative agent task configured as **Medium** completes successfully on DeepSeek after the change and logged call metadata shows `deepseek-v4-pro` without thinking mode.
5. A representative agent task configured as **Big** completes successfully on DeepSeek after the change and logged call metadata shows `deepseek-v4-pro` with thinking mode enabled.
6. New DeepSeek timesheet rows after deploy record costs using the pricing entry for the vendor model actually used (flash for Little; pro for Medium and Big).
7. With `active_provider` set to Anthropic, Little / Medium / Big still resolve to the existing Anthropic model aliases with no regression in a representative graded task.
8. Automated tests that assert DeepSeek tier resolution are updated to match the new Medium mapping and remain green on the epic branch.

## Boundaries

* Does not switch `active_provider`, add providers, or change Anthropic tier mappings.
* Does not change TASK_CONFIG prompts/schemas/grading or per-agent brain_setting assignments in the database.
* Does not backfill historical timesheet costs.
* Sibling tickets: none — this is the sole implementation child for [AST-694](https://linear.app/astralcareermatch/issue/AST-694/deepseek-brain-model-changes).

## Notes for planning

* Primary touch: `LLM_PROVIDER_CONFIG["tier_map"]["deepseek"]` in product config (single source of truth per ASTRAL_CODE_RULES §2.1).
* `DEEPSEEK_MODEL_PRICING` already includes both flash and pro SKUs — verify cost paths still resolve correctly after Medium moves to pro.
* Component tests in `tests/component/utils/test_config.py` and any agent tests asserting Medium tier meta need updating.
* Big tier thinking/reasoning_effort: preserve existing production behavior for thinking-on pro calls unless config already specifies otherwise.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-694-deepseek-brain-model-changes`, child `sub/AST-694/AST-695-deepseek-brain-tier-mapping-update`, standalone `ftr/<segment>`. Created at **dispatch-parent**. Engineers publish to `origin/<sub-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### radia — 2026-06-16T01:49:18.625Z
### Review vs `origin/dev`

**Ref:** `origin/sub/AST-694/AST-695-deepseek-brain-tier-mapping-update` @ `d2fbf26` (includes `docs/features/foundation/ast-695-deepseek-brain-tier-mapping-update.md` Radia section)

### Plan fidelity

- Stage 1 matches plan: `LLM_PROVIDER_CONFIG["tier_map"]["deepseek"][BRAIN_MEDIUM]` → `deepseek-v4-pro`, `thinking: False`, `reasoning_effort: None`; AST-694 block comment; Little/Big unchanged; no edits to `agent.py`, `deepseek.py`, pricing, Anthropic map, or `active_provider`.
- Self-Assessment scope (`minor`) matches the diff footprint.

### ASTRAL_CODE_RULES

- **§2.1 config:** Tier literals stay in `LLM_PROVIDER_CONFIG`; `BRAIN_*` constants preserved — no duplicate tier lists.
- **§1.3 / §3.3:** Config-only product change; no new imports or cross-layer violations.
- **§5f / §5g:** N/A (no debug or external-layer diffs).

### Tests

- `test_resolve_deepseek_tier_meta` asserts Medium → pro non-thinking; Betty bible row + narrowed manifest documented.
- `TestAst492BrainSettingDoTask` / `TestAst492ResolveAdhocApiAdmin` remain Little-tier fixtures (same resolution helpers) — acceptable for this ticket's config-only scope.

**fix-now:** none

**discuss:** none

**Advisory:** Optional follow-up — Medium-tier `do_task` / adhoc component assertions if Susan wants end-to-end Medium SKU coverage beyond config resolution.

#### betty — 2026-06-16T01:24:43.288Z
## QA test manifest (AST-695)

**Publish ref:** `origin/sub/AST-694/AST-695-deepseek-brain-tier-mapping-update` @ `ab17e54`
**Product commit:** `1d7bc60` (Medium tier → `deepseek-v4-pro`, thinking off)

### Existing coverage (bible-backed)

1. **`tests/component/utils/test_config.py::TestAst492LlmBrainTierConfig::test_resolve_deepseek_tier_meta`** — Medium → `deepseek-v4-pro`, `thinking=False`; Little/Big unchanged (`docs/test-bible/utils/config.md` **AST-695**).
2. **`tests/component/core/test_agent.py::TestAst492BrainSettingDoTask::test_send_to_deepseek_receives_vendor_model_and_tier_meta`** — `do_task` passes resolved `vendor_model` + `tier_meta` to `send_to_deepseek` (Little tier; config-driven).
3. **`tests/component/ui/api/test_api_admin.py::TestAst492ResolveAdhocApiAdmin::test_resolve_adhoc_deepseek_sets_tier_meta_and_vendor_as_model_code`** — admin adhoc resolve DeepSeek payload (Little tier regression).

### Broken / obsolete tests

None — Betty extended `test_resolve_deepseek_tier_meta` for Medium mapping; dispatch/adhoc tests read tier meta from config and required no assertion changes.

### Run (test-child)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst492LlmBrainTierConfig::test_resolve_deepseek_tier_meta \
  tests/component/core/test_agent.py::TestAst492BrainSettingDoTask::test_send_to_deepseek_receives_vendor_model_and_tier_meta \
  tests/component/ui/api/test_api_admin.py::TestAst492ResolveAdhocApiAdmin::test_resolve_adhoc_deepseek_sets_tier_meta_and_vendor_as_model_code
```

**Pass criterion:** pytest green on narrowed args — not zero-arg harness / branch-lock gate.

### Bible shasum (publish ref)

- `docs/test-bible/utils/config.md` → `9ec21aac5ed484c1674bd3750edd4159e3cbfe48`

— Betty

#### ada — 2026-06-16T01:21:19.782Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-694/AST-695-deepseek-brain-tier-mapping-update/docs/features/foundation/ast-695-deepseek-brain-tier-mapping-update.md

**Scope:** minor — single `LLM_PROVIDER_CONFIG` tier_map edit; Medium moves from flash+thinking to pro non-thinking.

**Conf:** high — mapping fully specified in AST-694/695; existing resolve/send_to_deepseek paths consume config without new modules.

**Risk:** Medium — wrong Medium literals mis-price or enable thinking on mid-tier calls; Betty config tests + existing timesheet vendor_model plumbing mitigate.

---

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
- **Product commit:** `1d7bc60` — Medium tier → `deepseek-v4-pro`, thinking off; AST-694 comment on deepseek tier block.

## Radia review (AST-695)

**Diff:** `origin/dev...origin/sub/AST-694/AST-695-deepseek-brain-tier-mapping-update` @ `ab17e54`

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stage 1 matches plan exactly: `BRAIN_MEDIUM` → `deepseek-v4-pro`, `thinking: False`, `reasoning_effort: None`; block comment updated to AST-694 wording; Little/Big untouched; no scope creep into `agent.py`, `deepseek.py`, pricing, or Anthropic tier map. |
| Self-Assessment | Scope `minor` / Conf `high` align with the four-file diff (config + config test + plan + bible). |
| §2.1 config | Tier literals remain in `LLM_PROVIDER_CONFIG["tier_map"]["deepseek"]`; `BRAIN_*` constants preserved. |
| Tests | `test_resolve_deepseek_tier_meta` now asserts Medium → pro non-thinking alongside existing Little/Big rows; Betty manifest in `docs/test-bible/utils/config.md` documents narrowed pytest gate. |
| Layer / imports | Config-only product edit; no new cross-layer imports, logging, batch, or external-layer changes (§5f/§5g N/A). |

### Issues

None (**fix-now:** 0 · **discuss:** 0).

### Recommended actions

| Priority | Action |
| --- | --- |
| — | Proceed to **`resolve-child`** — no product changes required from review. |
| Advisory | `TestAst492BrainSettingDoTask` and `TestAst492ResolveAdhocApiAdmin` remain **Little-tier** fixtures; Medium coverage is sufficient at `resolve_brain_setting_to_deepseek_tier_meta` — same resolution path `do_task` / `_resolve_adhoc` already use. Optional future hardening: add a Medium-tier adhoc/`do_task` assertion if Susan wants end-to-end Medium SKU logging in component tests. |

## Resolution (Ada — resolve)

**Date:** 2026-06-16  
**Review ref:** `origin/sub/AST-694/AST-695-deepseek-brain-tier-mapping-update` @ `d2fbf26`

Radia posted **fix-now: none**, **discuss: none**. No product changes required — `code(AST-695)` @ `1d7bc60` stands as shipped. Advisory (optional Medium-tier `do_task`/adhoc component assertions) deferred; config resolution test + existing Little-tier dispatch fixtures cover the resolution path.

**§9a dry-run:** publish ref merges cleanly into `origin/dev` and `origin/ftr/AST-694-deepseek-brain-model-changes`.
