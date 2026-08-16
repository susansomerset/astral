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

## Review (build stub)

**Publish ref:** `origin/sub/AST-1390/AST-1391-deepseek-big-output-budget`
**Tip (pre-review):** `aa2bd119`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `06e62678` | DeepSeek Big tier `max_tokens: 384000`; `deepseek_brain_max_tokens_floor` |
| 2 | `aa2bd119` | `do_task` applies that floor after the craft 32000 / AST-1380 block |

## Radia review

# Radia review — AST-1391

**Publish ref:** `sub/AST-1390/AST-1391-deepseek-big-output-budget` @ `d649ec23`  
**Diff baseline:** `origin/dev...origin/sub/AST-1390/AST-1391-deepseek-big-output-budget`  
**Internal grade:** **CLEAN**

---

## Summary

Focused two-file product change: `384000` on DeepSeek `BRAIN_BIG` in `tier_map`, `deepseek_brain_max_tokens_floor()` helper, and a `do_task` floor applied **after** the AST-903 craft floor and AST-1380 thinking-off copy. Betty landed component tests + bible updates on a separate commit; engineer code commits touch only `src/utils/config.py` and `src/core/agent.py`.

Implementation matches Joan’s APPROVED plan (Stages 1–2), parent boundary (no SKU default bump, no `run_adhoc` / Admin), and AC1–AC6 coverage in the test manifest.

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.config.config-block` | conforms | `384000` lives on `LLM_PROVIDER_CONFIG["tier_map"]["deepseek"][BRAIN_BIG]`; helper reads live dict — no second drifting constant in `agent.py`. |
| `pattern.layers.import-discipline` | conforms | `core` imports one `utils` helper; no `external`/`data`/`ui` layer touches. |

---

## Plan adherence

- **Stage 1:** `max_tokens: 384000` on Big only; Little/Medium lack key; `DEEPSEEK_MODEL_PRICING["deepseek-v4-pro"]["default_max_tokens"]` unchanged at `16000`; helper matches plan shape.
- **Stage 2:** Floor inserted immediately after craft/AST-1380 block, before debug emission and provider calls; uses `deepseek_brain_max_tokens_floor(brain_setting)` (not stubbed `tier_meta`); `send_to_deepseek` still receives explicit `max_tokens=agent_max_tokens`.
- **Boundaries:** No edits to `deepseek.py`, `anthropic.py`, Admin adhoc paths, thinking/temperature/`PROVIDER_CALL_BUDGET`. Estimate **3** still fits footprint (config + hop + Betty tests).
- **Joan straggler (C4):** Plan verdict attached; no `Excluded` statute list in artifact — no straggler callouts.

---

## C6 judgment aids (§5a–§5g)

| Lens | Result |
|------|--------|
| Imports (B1) | Top-level `utils` import only. **Advisory:** `deepseek_brain_max_tokens_floor` sits after `resolve_*` imports rather than strict alpha — cosmetic only. |
| Layer compliance (B2) | Clean — core→utils only. |
| Silent failure (D2) | None introduced. |
| Fallbacks (D3) | `.get("max_tokens")` → `None` is correct floor-absent semantics, not a false-present sentinel. |
| Logging (E1) | No new `print()` / raw `logging`; existing `if debug:` `[DEBUG] do_task` + `debug_detail` `llm_params` lines run after floor (AC5). |
| Debug contract (§5f) | Not triggered for new emission — reuses gated existing paths. |
| External cleanliness (§5g) | No `src/external/` diff — n/a. |
| Cross-ticket (§5d) | No sibling scope smuggled; `run_adhoc` untouched. |

---

## Findings

### fix-now

*(none)*

### discuss

*(none)*

### advisory

- **Import ordering** — `src/core/agent.py` import block: `deepseek_brain_max_tokens_floor` could sit before `resolve_brain_setting_to_deepseek_tier_meta` for strict alphabetical order; plan allowed “alphabetically-adjacent” — no functional impact.

---

## What's solid

- Floor keyed on resolved `brain_setting` avoids tests that stub `tier_meta` without `max_tokens` silently skipping the product floor (plan Decision).
- Floor-not-cap semantics exercised (`400000` agent row wins).
- Craft DeepSeek Big: AST-1380 thinking-off preserved; `max_tokens` now Big floor, not `CRAFT_RUBRIC_MAX_TOKENS` (AC6).
- `tier_meta` may now carry `max_tokens` from `resolve_brain_setting_to_deepseek_tier_meta`, but `send_to_deepseek` still reads only `thinking` / `reasoning_effort` — core owns the resolved int per `astral.agent.do-task-delegation`.

---

## Frame diff

`(none)` — product footprint matches Joan frame (`config.py` + `agent.py`). Betty-added `tests/` + `docs/test-bible/**` are pipeline-expected, not engineer scope creep.

---

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | not-applicable | No confidence/scoring paths in diff. |
| `astral.agent.do-task-delegation` | scoped | conforms | Core resolves `agent_max_tokens` before `send_to_deepseek` / `send_to_anthropic`. |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | No grade-vector logic touched. |
| `astral.batch.batch-id-first` | scoped | not-applicable | No batch claim/ledger changes. |
| `astral.batch.batch-id-format` | scoped | not-applicable | No batch id formatting. |
| `astral.batch.claim-process-release` | scoped | not-applicable | No claim/process/release paths. |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | No entity response storage changes. |
| `astral.config.config-source-of-truth` | scoped | conforms | `384000` on `tier_map` Big tier; helper reads live config. |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | No secrets/env handling. |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | No debug artifacts. |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | No spike files. |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | No dispatch seed paths. |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | No run-next chain edits. |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single feature doc `ast-1391-deepseek-big-output-budget.md`. |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty commit limited to tests + test-bible. |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Engineer commits (`06e62678`, `aa2bd119`) touch `src/` only. |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Token budget resolved in core; external unchanged. |
| `astral.layers.import-direction` | scoped | conforms | `agent.py` → `utils.config` only. |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | No `scripts/` changes. |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | No UI changes. |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | No coat-check paths. |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | No consult/render paths. |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | No API auth surfaces. |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | No seed JSON edits. |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | No catalog seed changes. |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | Hot-path change is runtime config read — not boot seed. |
| `astral.seed.define-approved` | scoped | not-applicable | No define/seed workflow. |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | No operator row handling. |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | No coverage join logic. |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | No data-layer changes. |
| `astral.standards.database-header-inventory` | scoped | not-applicable | No DB/migration changes. |
| `astral.standards.debug-contract-gated` | scoped | conforms | No new ungated debug emission; existing lines behind `debug=True`. |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Single-purpose helper; minimal `do_task` insertion. |
| `astral.standards.in-scope-only` | scoped | conforms | Product diff limited to planned config + hop sites. |
| `astral.standards.logging-via-utils` | scoped | conforms | Uses existing `get_logger` / `debug_detail` patterns. |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | `AST-1391` traceability in comments only. |
| `astral.standards.no-cross-contamination` | scoped | conforms | No unrelated feature bleed. |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Literal in config block, not scattered in core. |
| `astral.standards.public-then-helpers` | scoped | conforms | Helper placed after `resolve_brain_setting_to_deepseek_tier_meta`. |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | No utils→data late imports. |
| `astral.state.core-decides-transitions` | scoped | not-applicable | No state transitions. |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | No job state machine edits. |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | No daisy-chain run logic. |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | No frontend files. |
| `astral.ui.naming-conventions` | scoped | not-applicable | No UI naming. |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | No gunicorn/deploy config. |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1391)` commit present. |
| `orch.git.commit-vocabulary` | universal | conforms | `code` / `test` / `docs` / `merge-tests` prefixes used. |
| `orch.git.flow-direction-inviolable` | universal | conforms | Work on `sub/AST-1390/...`; not landing on `dev` directly. |
| `orch.git.ftr-sub-topology` | universal | conforms | Child `sub/` under parent AST-1390. |
| `orch.git.merge-on-checkout` | universal | conforms | No merge violations observed in review scope. |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | Linear history; no force/rebase signs. |
| `orch.git.no-dev-agent-branches` | universal | conforms | Publish ref is `sub/...`, not agent-named branch. |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | Review in `astral-AST-1390` worktree. |
| `orch.git.three-permanent-branches` | universal | conforms | Diff vs `origin/dev` only. |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Product choice (Big floor, skip adhoc) already in approved plan. |
| `orch.pipeline.plan-is-bible` | universal | conforms | Implementation tracks staged plan. |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Single-child review scope. |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Spawned at Tests Passed. |
| `orch.roles.archie-approves-statutes` | universal | conforms | Joan APPROVED plan-rubric. |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Tests/bible on Betty commit. |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee Ada through review. |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Engineer remains assignee at Tests Passed. |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No banned-path commits in product tree. |

**Sweep count:** 64 active statutes scored in-session (per `canon/statutes/README.md` harvested table).

---

## Notes

- Joan plan-rubric verdict attached; no `Excluded` statute list — C4 straggler check clear.
- Recommend **Review Posted** → **resolve-child** not required (PROCEED); datt may advance to **User Testing** per PROCEED mapping.
- Downstream only if Susan wants Admin adhoc parity later — explicitly out of AST-1391 boundary; do not expand scope here.

context_tokens≈38000

---
