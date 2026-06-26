<!-- linear-archive: AST-493 archived 2026-06-15 -->

## Linear archive (AST-493)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-493/deepseek-client-and-provider-dispatch-routing-support-other-ai-models  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-491 — Support other ai models: DeepSeek  
**Blocked by / blocks / related:** parent: AST-491; blocks: AST-494

### Description

## What this implements

DeepSeek integration using the **Anthropic-compatible** API surface (`https://api.deepseek.com/anthropic`), plus centralized routing so all existing agent/task flows that use the shared AI entry point invoke the correct provider and resolved model from config + agent `brain_setting` without callers selecting a vendor.

## Acceptance criteria

1. With `DEEPSEEK_API_KEY` set, when config selects DeepSeek, a representative agent task completes end-to-end with the same success/failure semantics as today on Anthropic.
2. With config selecting Anthropic, existing agent tasks behave as before (no regression on a representative graded task).
3. For DeepSeek calls that return cache read usage, downstream timesheet writes receive cache read token counts (write path consumed by sibling timesheet ticket).

## Boundaries

Does not own timesheet schema migration or admin UI label changes. Does not enable OpenAI-compatible DeepSeek chat API. Does not add third-party agent-tool integrations.

## Notes for planning

* Mirror established `anthropic.py` external-layer patterns; core `do_task` delegates by provider.
* Support DeepSeek thinking modes for flash/pro tiers per parent definition answers.

## Git branch (authoritative)

Per **orientation-astral** § Branch law: parent `ftr/AST-491-support-other-ai-models-deepseek`, child `sub/AST-491/<child-segment>`. Created at dispatch-linear.

### Comments

#### ada — 2026-05-27T03:06:42.959Z
[check-linear]

- **Session scope:** Susan directed **assigned issue ids: (none)** — no `test-astral` / publish-ref merges for this inbox pass beyond **§0a** integration line.
- **Skill §6:** **`test-astral`** is not invoked unless she names that stage in the same message after **check-linear**; this run was **check-linear** only with an empty allowlist.
- **Acknowledged** your **`@Ada Lovelace`** handoff: manifest on **`origin/sub/AST-491/AST-493-deepseek-client-and-provider-dispatch-routing`** @ **`be9ee17c3c52a15b3fab8f0cd1609e4130ec27b8`**, §**7.13ze** narrow command, Radia review posted after your note.
- **§0a (this workspace):** `git fetch origin`, **`dev-ada`**, **`git merge origin/dev`** — completed; working tree reflects merged **`origin/dev`** tip.

Ready when Susan assigns AST-491 work to me or names **`test-astral`** for this ticket.

#### radia — 2026-05-26T22:45:14.579Z
**Diff:** three-dot `origin/dev` vs **AST-491 dispatch** [`sub/AST-491/AST-493-deepseek-client-and-provider-dispatch-routing`](https://github.com/susansomerset/astral/tree/sub/AST-491/AST-493-deepseek-client-and-provider-dispatch-routing). **Publish tip:** `be9ee17c3c52a15b3fab8f0cd1609e4130ec27b8`.

- **`src/external/deepseek.py`** — Shape and parsing arms mirror `anthropic.py` (explicit ticket comment); uses `calculate_cost_components_deepseek`, `provider="deepseek"` and unified ledger kwargs merged with AST-494.
- **Core routing** — `do_task` / extended `run_adhoc` (`tier_meta` drives DeepSeek branch) delegate by `get_active_llm_provider()`; callers stay vendor-oblivious.
- **Silent exception handling on timesheet record** matches the existing Anthropic client pattern (preserve primary success/failure path).

**discuss** — Thinking path wires `thinking` + `output_config["effort"]` rather than the `reasoning_effort` wording in some vendor examples; smoke against current DeepSeek anthropic-compat docs so reasoning/thinking knobs are honored. Config still carries unused `reasoning_effort` on tier rows (acceptable if single-effort stance).

Review appendix (cherry-pick target): [`ast-493-deepseek-client-and-provider-dispatch-routing.md`](https://github.com/susansomerset/astral/blob/6262a3a9bfb39eee879dab2dd9e479f113524553/docs/features/roster/ast-493-deepseek-client-and-provider-dispatch-routing.md) @ `6262a3a9`.

#### betty — 2026-05-26T22:36:46.451Z
[check-linear]

- Prior “docs-only publish ref” **blocker withdrawn**: product **`do_task` / `run_adhoc`** DeepSeek path is on the integration line; Ada’s **`[qa-handoff]`** was on **AST-492** (cleared there).
- QA: **`docs(AST-493)`** — **`docs/ASTRAL_TEST_BIBLE.md`** §**7.13ze** (DeepSeek **`send_to_deepseek`** + unified **`agent_timesheets`** / **`agent_req_id`** manifest command).
- Published: **`origin/sub/AST-491/AST-493-deepseek-client-and-provider-dispatch-routing`** @ **`be9ee17c3c52a15b3fab8f0cd1609e4130ec27b8`**.

**Manifest (pytest narrow, §7.13ze):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst492LlmBrainTierConfig \
  tests/component/core/test_agent.py::TestAst492BrainSettingDoTask \
  tests/component/data/database/test_timesheets.py \
  tests/component/core/test_timesheets.py
```

**Betty:** Move this issue to **Tests Ready** if the UI still shows **Code Complete** (MCP **`save_issue`** update failed from this session).

@Ada Lovelace — **`test-astral`** queue.

#### betty — 2026-05-26T22:27:54.695Z
@susan — **Blocked for qa-astral:** `origin/sub/AST-491/AST-493-deepseek-client-and-provider-dispatch-routing` tip is **docs-only** (plan commit); no `send_to_deepseek` / `deepseek` client on that ref — `do_task` still raises for deepseek. Holding **Code Complete**; no Tests Ready handoff until implementation lands on the publish ref (or you confirm a different authoritative branch).

— Betty

#### betty — 2026-05-26T22:24:11.933Z
@susan — blocker for QA handoff: **`origin/sub/AST-491/AST-493-deepseek-client-and-provider-dispatch-routing` tip (`471cea87`) is docs-only.** There is no `src/external/deepseek.py`, no `send_to_deepseek`, and `do_task` / product code on the integration tip I’m using still has the AST-492 DeepSeek stub. I can’t post a truthful **Tests Ready** manifest until Ada’s implementation commits reach this publish ref.

Recommendation: Ada cherry-picks / merges product SHAs onto the **`AST-493` sub publish ref**, then Betty re-runs qa-astral.

— Betty

#### ada — 2026-05-26T22:09:11.736Z
Plan doc:

https://github.com/susansomerset/astral/blob/sub/AST-491/AST-493-deepseek-client-and-provider-dispatch-routing/docs/features/roster/ast-493-deepseek-client-and-provider-dispatch-routing.md

**Self-assessment (with reasons)**  
**Scope · MAJOR-CHANGE** — New `external/deepseek.py`, forks `agent.py` do_task/run_adhoc, extends `cost_calculator.py`; necessary to meet “single AI entry stays do_task while vendor swaps underneath.”  
**Conf · conf-Medium** — Anthropic Python SDK pointed at DeepSeek base URL plus thinking/reasoning flags is plausible but empirical; mocks + comparing against DeepSeek’s Anthropic-compat doc are the mitigation; stop with a parent-issue comment if `messages.create` kwargs disagree with live docs.  
**risk-HIGH** — Bad `usage` mapping or omitting reasoning fields yields wrong billed tokens or degraded responses feeding unchanged grading validators; parity tests anchoring `{success, timesheet..., parsed_response}` contract are mandatory before Code Complete.

Ada

---

# AST-493 — DeepSeek client and provider dispatch routing

**Parent:** [AST-491 — Support other ai models: DeepSeek](https://linear.app/astralcareermatch/issue/AST-491/support-other-ai-models-deepseek)  
**Depends on:** [AST-492](https://linear.app/astralcareermatch/issue/AST-492/llm-provider-brain-setting-tiers-and-tier-mappings-support-other-ai) (`brain_setting`, tier metadata, DeepSeek pricing in config)  
**Publish ref (origin):** `sub/AST-491/AST-493-deepseek-client-and-provider-dispatch-routing`  
**Ticket:** [AST-493](https://linear.app/astralcareermatch/issue/AST-493/deepseek-client-and-provider-dispatch-routing-support-other-ai-models)

Adds `src/external/deepseek.py` with `send_to_deepseek` that hits DeepSeek’s Anthropic-compatible Messages API (`https://api.deepseek.com/anthropic`) using `os.environ["DEEPSEEK_API_KEY"]`, mirrors the observable contract of `send_to_anthropic` (success dict shape, parsing for `response_format`, `record_timesheet` invocation with usage-derived token splits including cache read/write fields). Parsing helpers: duplicate the small `_parse_json_response` / `_parse_python_code_response` / `_parse_api_response` pattern from `src/external/anthropic.py` into `deepseek.py` with a one-line comment `mirror anthropic.py — avoid refactor in this ticket` rather than extracting to utils (violates utils purity if placed there).

Wires `do_task` / `run_adhoc` (`src/core/agent.py`): when `get_active_llm_provider() == "anthropic"` keep existing stack; when `"deepseek"`, call `send_to_deepseek` with vendor `model`, thinking / reasoning knobs from `resolve_brain_setting_to_deepseek_tier_meta(brain_setting)` (AST-492). Cache read counts on the DeepSeek usage object must flow into `_timesheet_kwargs` / `record_timesheet` the same semantic slots Anthropic uses (AST-494 may rename kwargs to `agent_req_id`; this ticket stays consistent with whichever column name `_add_timesheet_entry` expects on the integration branch).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/deepseek.py` | New `send_to_deepseek(...)`: kwargs aligned with `send_to_anthropic` (blocks, response_format, model as vendor SKU string, temperature, max_tokens, task_key_uuid, candidate_id, batch sizing, estimate fields, record_timesheet). Client: Anthropic SDK `Anthropic(api_key=..., base_url="https://api.deepseek.com/anthropic", timeout=...)` reuse same `_API_CALL_TIMEOUT` pattern as anthropic.py (define shared optional module-level constant later only if duplication offends Chuckles/Susan). Build `messages.create` kwargs including thinking per DeepSeek anthropic-compat docs (`thinking`, `reasoning_effort`) when tier_meta says thinking; stop and comment on **AST-493** parent if docs vs SDK disagree. Normalize `usage` to attributes `calculate_cost_components_deepseek` expects (adapt if DeepSeek nests differently). Timesheet kwarg naming: whatever `database._add_timesheet_entry` still uses on this branch (before AST-494: `anthropic_req_id`; after merge with 494 subject line: follow that branch literal). Always pass vendor model string through `model_code` timesheet slot for pricing lookup. `__all__ = ["send_to_deepseek"]`. | external |
| `src/utils/cost_calculator.py` | Implement `calculate_cost_components_deepseek(usage, vendor_model: str)` (and totals if reused) sourcing `DEEPSEEK_MODEL_PRICING[vendor_model]` from config (AST-492). Same return keys as `calculate_cost_components` for Anthropic. | utils |
| `src/core/agent.py` | After block assembly in `do_task`, branch `get_active_llm_provider()`; anthropic keeps `send_to_anthropic`; deepseek awaits `send_to_deepseek(...)`. Populate `tier_meta` from AST-492 helper; temperatures / max_tokens from tier meta or DeepSeek pricing entry defaults AST-492 must define (`default_temperature`, `default_max_tokens` per SKU). Extend `run_adhoc` similarly (provider branch inside agent.py only — no new imports in api_admin aside from unchanged `run_adhoc`). Import `send_to_deepseek` from external. | core |
| `tests/component/external/test_deepseek.py` | Mock `messages.create`: success path asserts thinking-related kwargs present for tiers that require thinking; `record_timesheet` mock sees non-zero cache_read when mocked usage includes cache-read tokens. | tests |
| `tests/component/core/test_agent.py` | Assert deepseek branch dispatches mocked `send_to_deepseek`; anthropic stays on `send_to_anthropic` when provider=`anthropic`. | tests |
| `tests/component/utils/test_cost_calculator.py` | Golden examples for DeepSeek pricing rows. | tests |

## Stage 1: External client parity

**Done when:** `send_to_deepseek` returns `{success, api_response, parsed_response, timesheet, error}` symmetric to `send_to_anthropic` for success and API failure paths.

1. Implement `deepseek.py` following the layout of ```183:331:src/external/anthropic.py``` (imports, timeouts, asyncio.to_thread, usage extraction, `_timesheet_kwargs` population, parsed_response branching, agent_performance metadata).
2. Client init: bracket env read only in client factory; missing key raises ValueError wording parallel to `_get_client` in anthropic.py.
3. Thinking: map `tier_meta` dict from AST-492 into documented API fields; omit fields when tier is Little non-thinking flash.

⚠️ **Decision:** No `deepseek.py` imports from `database`; only callbacks.

## Stage 2: DeepSeek pricing path

**Done when:** `calculate_cost_components_deepseek` returns non-null components for mocked usage with nonzero cache reads; zero `cpm_cache_write` does not explode.

1. Implement pricing lookup by `vendor_model` string strictly from config keys.
2. Call from `send_to_deepseek` when building `_timesheet_kwargs`.

## Stage 3: Core routing (`do_task` + `run_adhoc`)

**Done when:** Smoke tests prove Anthropic regressions unaffected; DeepSeek mocked path invokes `record_timesheet` exactly once.

1. In `do_task`, replace AST-492 deepseek stub with actual `await send_to_deepseek(...)`; keep logging parity (debug prints vendor model).
2. In `run_adhoc`, replicate provider branching so admin adhoc parity matches dispatcher path (same model resolution semantics as AST-492 for brain_setting tiers).

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — New vendor module touches core omnibus `agent.py`.

**Conf:** `Medium` — Depends on undocumented edges of Anthropic-compat mode on DeepSeek; mitigations: mocks plus manual curl comparison note in Linear if blocked.

**Risk:** `HIGH` — Incorrect usage mapping or reasoning flags yield silent wrong costs or truncation; tests must anchor cache fields.

## Self-review vs ASTRAL_CODE_RULES

- §3.3: `deepseek` imports utils + cost_calculator + logging + formatting (like anthropic.py); never data.
- §2.2: Persistence only through `record_timesheet` callable from core.
- §2.1: Pricing literals only via config-backed dict from AST-492.

No `conf-!!-NONE`; if offline pricing numbers missing, escalate before merge per AST-492.

## Execution contract

Cherry-pick only commits mentioning `AST-493` onto `origin/sub/AST-491/AST-493-deepseek-client-and-provider-dispatch-routing`; publish via detached `/tmp/astral-ada-pub-AST-493-$$`.

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-491/AST-493-deepseek-client-and-provider-dispatch-routing`  
**Product commit:** `e1bf2d0c` (feat AST-493 — merged `origin/sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings` prerequisite, then shipped DeepSeek routing + ledger hooks)

## Review

**Reviewer:** Radia. **Diff:** `origin/dev`…[`origin/sub/AST-491/AST-493-deepseek-client-and-provider-dispatch-routing`](https://github.com/susansomerset/astral/tree/sub/AST-491/AST-493-deepseek-client-and-provider-dispatch-routing). **Code tip:** `be9ee17c3c52a15b3fab8f0cd1609e4130ec27b8`.

### What's solid

- `src/external/deepseek.py` mirrors `anthropic.py` shape (result dict, parsing arms, usage → cost via `calculate_cost_components_deepseek`, `record_timesheet` hooks, `provider="deepseek"`).
- `do_task` / `run_adhoc` branch on `get_active_llm_provider()` with tier meta from config; no vendor selection in callers.
- Swallowed exceptions around timesheet persistence match the existing Anthropic client pattern (cost build / DB write failures must not mask primary API outcome).

### Issues / notes

| Severity | Topic | Location | Note |
|----------|-------|----------|------|
| discuss | Request kwargs | `send_to_deepseek` | Thinking path sets `thinking` + `output_config.effort`; plan text mentioned `reasoning_effort` in places. Spot-check against current DeepSeek anthropic-compat docs so reasoning depth is actually applied. |
| advisory | Config carry | `tier_map` | `reasoning_effort` is present on tier meta but not forwarded into API kwargs; fine if deliberate (single effort level). |

### Recommended actions

| Priority | Action |
|----------|--------|
| Optional | Confirm one live or staged call logs the expected reasoning/thinking metadata in the vendor response when Medium/Big tiers are exercised. |

## Resolution — 2026-05-26

- Radia **`review-astral`**: **discuss** (thinking **`kwargs`** vs doc wording **`reasoning_effort`**) and **advisory** (unused **`reasoning_effort`** tier meta — acceptable if single-effort stance). **No fix-now** items; **`send_to_deepseek`** remains aligned with the Anthropic Python SDK knobs used against DeepSeek’s compat surface; optional live smoke deferred to UAT. Publish tip **`be9ee17c3c52a15b3fab8f0cd1609e4130ec27b8`** (**`6262a3a9bfb39eee879dab2dd9e479f113524553`** subtree includes Radia doc follow-ups atop product **`e1bf2d0c`**).
- **§9a** dry-runs vs **`origin/dev`** and **`origin/ftr/AST-491-support-other-ai-models-deepseek`** clean before **`User Testing`**.

