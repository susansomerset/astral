<!-- linear-archive: AST-492 archived 2026-06-15 -->

## Linear archive (AST-492)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-492/llm-provider-brain-setting-tiers-and-tier-mappings-support-other-ai  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-491 — Support other ai models: DeepSeek  
**Blocked by / blocks / related:** parent: AST-491; blocks: AST-495; blocks: AST-493

### Description

## What this implements

Product configuration for the active LLM provider (config-driven for v1, not per-candidate UI), the **Little / Medium / Big** `brain_setting` tier catalog on agents, and canonical tier→vendor-model mappings for Anthropic and DeepSeek—including thinking vs non-thinking for DeepSeek per Susan’s decisions (Big: v4-pro + thinking; Medium: v4-flash + thinking; Little: v4-flash without thinking). Pricing metadata for cost calculation must live in config as the single source of truth.

## Acceptance criteria

3. Each agent used in production can be configured with **Little**, **Medium**, or **Big** tier; changing tier changes which concrete model runs for that agent under the active provider, verifiable from admin agent detail or logged call metadata.
4. Tier **Big** on Anthropic and tier **Big** on DeepSeek for the same agent definition invoke different vendor models per the configured mapping table.
5. Missing required provider API key for the selected provider causes startup or call failure consistent with existing secret handling (fail loud, no silent fallback to the other vendor).

## Boundaries

Does not implement DeepSeek HTTP client, `do_task` routing, timesheet tables, or admin UI labels—sibling tickets. Does not add providers beyond Anthropic + DeepSeek. Does not change TASK_CONFIG prompts or grading.

## Notes for planning

* Replace agent `model_code` storage semantics with `brain_setting` (Little/Medium/Big) where applicable; map at runtime using active provider from config.
* `DEEPSEEK_API_KEY` env only; provider switch is a config literal for now.
* Read **AST-324** merged behavior on `origin/dev` for `AGENT_CONFIG` patterns.

## Git branch (authoritative)

Per **orientation-astral** § Branch law: parent `ftr/AST-491-support-other-ai-models-deepseek`, child `sub/AST-491/<child-segment>`. Created at dispatch-linear.

### Comments

#### radia — 2026-05-26T22:45:01.998Z
**Diff:** three-dot `origin/dev` vs **AST-491 dispatch** [`sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings`](https://github.com/susansomerset/astral/tree/sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings). **Publish tip:** `abc5fbe68cff6b219fb62c9012cc7db45e15a574`.

- **Tier + pricing source of truth** — `LLM_PROVIDER_CONFIG` / `BRAIN_*` literals, Anthropic tier map, DeepSeek SKU + thinking flags and `DEEPSEEK_MODEL_PRICING` with dated vendor citation in `src/utils/config.py` match plan and AST-491 Q&A.
- **Secrets / startup** — `validate_llm_provider_environment()` with bracket reads; wired in `src/ui/server.py` before DB sync (`# noqa`), consistent with §2.1.
- **Persistence** — `brain_setting` column + deterministic backfill; `save_agent` requires tier on INSERT; `_UPDATE_AGENT_ALLOWED` drops `model_code` writes.

**discuss** — `database._expose_agent_public` sets JSON `model_code` / `resolved_model_key` from the **currently configured** provider. Intended for UI compat per integration notes; double-check callers if anything assumed `model_code` always equals a stable Anthropic AGENT_CONFIG key across provider switches.

Review appendix (cherry-pick target): [`docs/features/roster/ast-492-llm-provider-brain-setting-tiers-and-tier-mappings.md`](https://github.com/susansomerset/astral/blob/07dd50afc311dcfdc6f8668c36bf3b72f9016077/docs/features/roster/ast-492-llm-provider-brain-setting-tiers-and-tier-mappings.md) (`07dd50af`).

#### betty — 2026-05-26T22:36:44.376Z
[check-linear]

- Cleared Ada’s latest `[qa-handoff]`: **`TestAst492BrainSettingDoTask`** now uses **`test_send_to_deepseek_receives_vendor_model_and_tier_meta`** (mocks **`send_to_deepseek`**, asserts **`vendor_model`** + **`tier_meta`** from **`resolve_brain_setting_to_deepseek_tier_meta`**) instead of expecting a pre-AST-493 **`ValueError`**.
- **`docs/ASTRAL_TEST_BIBLE.md`** §**7.13zd** updated so the catalog matches integrated DeepSeek dispatch.
- Published: **`origin/sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings`** @ **`abc5fbe68cff6b219fb62c9012cc7db45e15a574`**.
- **Manifest (pytest** — same narrow set as the handoff command):  
  `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst492BrainSettingConfig tests/component/data/database/test_agents.py tests/component/core/test_agent.py::TestAst492BrainSettingDoTask tests/component/ui/api/test_api_admin.py::TestAdminConfigAndAgents`  
  (On current **`dev-betty`**, config class is **`TestAst492LlmBrainTierConfig`** — see bible §7.13zd if Ada’s note still says the old name.)

Assignee stays **Ada** for **`test-astral`** (already **Tests Ready**).

#### ada — 2026-05-26T22:25:28.598Z
[qa-handoff]

`TestAst492BrainSettingDoTask::test_deepseek_active_provider_raises_before_send` still expects `ValueError` matching `AST-493` when `get_active_llm_provider` returns `"deepseek"` (no `send_to_*` call). On `dev-ada` after merging `origin/sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings`, product resolves `brain_setting` → DeepSeek `vendor_model` and proceeds toward `send_to_deepseek`; the run fails later on task validation (`Missing required field 'jobs'`), not on the old stub.

**Command:**  
`./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst492BrainSettingConfig tests/component/data/database/test_agents.py tests/component/core/test_agent.py::TestAst492BrainSettingDoTask tests/component/ui/api/test_api_admin.py::TestAdminConfigAndAgents`

**Ask:** Please update this case (or drop it) so the manifest matches the integrated contract: DeepSeek `do_task` is live on dev-ada with `send_to_deepseek` + tier meta—e.g. assert `send_to_deepseek` is invoked with the expected `vendor_model` / `tier_meta`, or gate the test on a flag if you need to keep dual behavior.

@Betty White

#### betty — 2026-05-26T22:23:23.997Z
QA test manifest (Betty)

1. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst492BrainSettingConfig tests/component/data/database/test_agents.py tests/component/core/test_agent.py::TestAst492BrainSettingDoTask tests/component/ui/api/test_api_admin.py::TestAdminConfigAndAgents`
2. Canonical map: **`docs/ASTRAL_TEST_BIBLE.md` §7.13zd** (`LLM_PROVIDER_CONFIG` / `brain_setting` / admin agents / `do_task` resolution).

**Publish tip:** `origin/sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings` @ `80256920` (includes `test(AST-492): …` on the sub ref).

— Betty

#### betty — 2026-05-26T22:23:05.048Z
**QA manifest (Betty)**

1. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst492LlmBrainTierConfig tests/component/data/database/test_agents.py tests/component/ui/api/test_api_admin.py::TestAdminConfigAndAgents tests/component/core/test_agent.py::TestAst492BrainSettingDoTask`
2. Regression check (empty `brain_setting` on mocked agent row): `./scripts/testing/run_component_tests.sh tests/component/core/test_agent.py::TestDoTask::test_rejects_unknown_or_misconfigured_tasks`
3. Test updates: `docs/ASTRAL_TEST_BIBLE.md` §7.13zd — class name **`TestAst492LlmBrainTierConfig`**, narrow command matches (1).
4. Publish tip: `origin/sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings` @ `80256920` (`test(AST-492): brain_setting QA — config, DB agent rows, do_task SKU, admin API`).

— Betty

#### ada — 2026-05-26T22:09:06.555Z
Plan doc (**Roster**, `brain_setting` = Little/Medium/Big aligned with Susan’s AST-491 Q6):

https://github.com/susansomerset/astral/blob/sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings/docs/features/roster/ast-492-llm-provider-brain-setting-tiers-and-tier-mappings.md

**Self-assessment (with reasons)**  
**Scope · MAJOR-CHANGE** — Hits `src/utils/config.py` (provider + tier map + DeepSeek pricing), `database.py` agent column migration/backfill, `agent.py` do_task anthropic resolution, and `api_admin.py` CRUD/task enrichment/adhoc prelude so stored semantics match runtime; unavoidable for replacing `model_code` end-to-end for Anthropic.  
**Conf · conf-high** — Tier resolution mirrors existing `AGENT_CONFIG` / `get_model`; migrations continue the guarded `_ensure_*_schema` style; DeepSeek SKU strings only enter config literals per code rules while HTTP stays AST-493.  
**risk-HIGH** — A bad tier→model map or sloppy backfill silently changes which Anthropic SKU runs production traffic; duplicate startup env checks parallel Anthropic (`DEEPSEEK_API_KEY` when `active_provider=="deepseek"`) reduce “half-configured DeepSeek” incidents.

Ada

---

# AST-492 — LLM provider, brain_setting tiers, and tier mappings

**Parent:** [AST-491 — Support other ai models: DeepSeek](https://linear.app/astralcareermatch/issue/AST-491/support-other-ai-models-deepseek)  
**Publish ref (origin):** `sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings`  
**Ticket:** [AST-492](https://linear.app/astralcareermatch/issue/AST-492/llm-provider-brain-setting-tiers-and-tier-mappings-support-other-ai)

This ticket adds config-driven active LLM provider selection (literal, v1 global), a three-value **`brain_setting`** catalog (**Little**, **Medium**, **Big**) on agent rows replacing vendor-specific **`model_code`**, canonical tier→model mappings for Anthropic (via existing `AGENT_CONFIG` keys) and DeepSeek (vendor model id + thinking / reasoning flags), and DeepSeek pricing metadata in **`config.py`** as the single source of truth for cost math (consumed fully once **AST-493** wires the client). **`do_task`** and admin adhoc paths that today call **`get_model(agent["model_code"])`** resolve **Little/Medium/Big** to the Anthropic **`AGENT_CONFIG`** key when **`active_provider` is `"anthropic"`**; selecting **`"deepseek"`** fails loudly at orchestration boundaries until **AST-493** lands the dispatch branch (no silent fallback, no DeepSeek HTTP in this ticket).

## Files Changed (planned)

Spike output, if any, stays under **`debug/spikes/AST-492/`** only.

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `LLM_PROVIDER_CONFIG` (or equivalently named block): `active_provider` (`"anthropic"` \| `"deepseek"`), ordered tuple/list `brain_settings = ("Little", "Medium", "Big")`, nested `tier_map["anthropic"][tier]` → `agent_config_key` (must be keys of `AGENT_CONFIG`), `tier_map["deepseek"][tier]` → `vendor_model`, `thinking` bool, optional `reasoning_effort` string per parent Q&A (Big/Medium: thinking; Little: non-thinking flash). Add `DEEPSEEK_MODEL_PRICING` (or under same block): per `vendor_model` keys used in tier_map with `model_label`, `cpm_input`, `cpm_output`, `cpm_cache_read`, `cpm_cache_write` (use `0` when vendor does not charge cache write — Susan’s note). Add helpers: `get_active_llm_provider() -> str`, `validate_allowed_brain_setting(s: str) -> None`, `resolve_brain_setting_to_anthropic_agent_key(brain_setting: str) -> str`, `resolve_brain_setting_to_deepseek_tier_meta(brain_setting: str) -> dict` (returns vendor_model + thinking flags for **AST-493** only — no imports from **`external`** here). Fail loud if `active_provider == "deepseek"` and **`os.environ["DEEPSEEK_API_KEY"]`** missing at **`validate_llm_provider_environment()`** (new), called once from Flask app factory / `server.py` startup after imports, matching Anthropic **`ANTHROPIC_API_KEY`** style (required env, no fallback). | utils |
| `src/data/database.py` | Update header inventory comment for `agent` row shape. Migrate storage from **`model_code`** to **`brain_setting`**: (1) `_ensure_agent_schema`-style migration: if column `brain_setting` missing, add it; backfill from `model_code` using deterministic map `claude-haiku-4-5`→`Little`, `claude-sonnet-4-6`→`Medium`, `claude-opus-4-6`→`Big`, any other legacy value → default **`Medium`** with a single startup log line via **`logging`** from caller or note in migration comment only (data layer must not log per rules — encode default in migration SQL only). (2) Deprecate writes to `model_code`: change **`save_agent`**, **`update_agent`**, **`list_agents`**, **`get_agent`** semantics so JSON/API uses **`brain_setting`** as the authoritative field; after backfill, stop reading `model_code` in product code paths (column may remain NULL for new rows or be dropped in a follow-up migration if SQLite PRAGMA allows safe rename — prefer **ALTER add + backfill + ignore old column** over risky table rebuild unless already patterned in repo). | data |
| `src/core/agent.py` | After loading `agent_row`, read `brain_setting` (required). Branch: if **`get_active_llm_provider() == "anthropic"`**, set `resolved_anthropic_key = resolve_brain_setting_to_anthropic_agent_key(brain_setting)`; use `get_model(resolved_anthropic_key)` for defaults; pass `resolved_anthropic_key` as `model_code` into **`_assemble_blocks_seven_segment`** and **`send_to_anthropic`** (unchanged external signature). If **`get_active_llm_provider() == "deepseek"`**, raise **`ValueError`** with message that DeepSeek dispatch is **AST-493** (no HTTP, no stub client). Update debug log line to print `brain_setting` and `resolved_anthropic_key`. | core |
| `src/ui/api/api_admin.py` | Replace agent create/update validation: accept **`brain_setting`** in body; validate with **`validate_allowed_brain_setting`**. Remove checks that **`model_code in AGENT_CONFIG`** for agent CRUD. **`GET /agents/models`** remains the Anthropic catalog for workbench until product asks otherwise; optionally add **`GET /agents/brain_settings`** returning allowed tier list from config (if needed by frontend in same PR — only if already consumed; **AST-495** owns label copy). **`_enrich_tasks`**: replace `agent.get("model_code")` with resolved display: when provider anthropic, show resolved AGENT_CONFIG key or `brain_setting` per product need — plan: expose both `brain_setting` and `resolved_model_key` for admin diagnostics (tiers observable). **`_resolve_adhoc`**: same resolution as **`do_task`** for anthropic; deepseek raises same **`ValueError`**. Timesheet AVG query raw SQL referencing `timesheets` table: **leave table name untouched in this ticket** (**AST-494** renames unified query). | ui |
| `tests/component/utils/test_config.py` | Tests for tier map keys, **`resolve_brain_setting_to_anthropic_agent_key`** happy path + invalid tier **`ValueError`**, **`validate_llm_provider_environment`** raises when **`active_provider`** deepseek and env key stripped. | tests |
| `tests/component/data/test_database.py` (or existing agent migration tests) | Agent migration: after migration, seeded agents have **`brain_setting`** in {Little, Medium, Big}; **`save_agent`** persists **`brain_setting`**. | tests |
| `tests/component/core/test_agent.py` | **`do_task`** with mocked **`send_to_anthropic`** asserts passed `model_code` matches tier→Anthropic mapping when provider anthropic; with provider deepseek patched, asserts **`do_task`** raises before external call. | tests |
| `tests/component/ui/api/test_api_admin.py` | Agent CRUD rejects invalid **`brain_setting`**; accepts valid tiers. | tests |

## Stage 1: Config primitives and helpers

**Done when:** `LLM_PROVIDER_CONFIG` and DeepSeek pricing literals exist in `config.py`; helpers resolve Anthropic tier and validate brain_setting; **`validate_llm_provider_environment`** exists; **`python -m compileall`** passes with no cyclic import from **`external`**.

1. In `src/utils/config.py`, after **`AGENT_CONFIG`** / **`get_model`**, add **`LLM_PROVIDER_CONFIG`** structured exactly so **Little / Medium / Big** are the only tier strings (capitalization fixed in code constants, e.g. **`BRAIN_LITTLE = "Little"`** tuples) and **`active_provider`** is the literal **`"anthropic"`** until Susan switches to **`"deepseek"`** post-493.
2. Add **`DEEPSEEK_*`** pricing keyed by the same **`vendor_model`** strings used under **`tier_map["deepseek"]`**; include **`cpm_cache_write`: 0** where Susan specified no differentiated cache-write price; **`cpm_cache_read`** populated from DeepSeek docs or Susan-provided rates (if unknown at build time, use explicit placeholder literals with comment **`# VERIFY PRICING — Susan`** and stop build if Susan has not supplied numbers — do not invent silent zeros for input/output).
3. Implement **`get_active_llm_provider()`** reading **`LLM_PROVIDER_CONFIG["active_provider"]`** only (no env override per parent Q1).
4. Implement **`validate_allowed_brain_setting(value: str) -> None`**: raises **`ValueError`** if not in configured set.
5. Implement **`resolve_brain_setting_to_anthropic_agent_key(brain_setting: str) -> str`**: returns **`tier_map["anthropic"][brain_setting]["agent_config_key"]`**; must be valid **`AGENT_CONFIG`** key (assert by **`get_model`** in tests, not in hot path if avoidable).
6. Implement **`validate_llm_provider_environment()`**: if **`active_provider == "anthropic"`**, require **`os.environ["ANTHROPIC_API_KEY"]`** (existing pattern); if **`"deepseek"`**, require **`os.environ["DEEPSEEK_API_KEY"]`**. Use bracket access, no **`.get()`** fallback, consistent with **ASTRAL_CODE_RULES §2.1** secrets rule for keys ( Anthropic client already enforces for calls — this adds startup parity for DeepSeek selection).
7. In `src/ui/server.py` (or the single app factory used by **`server.py`**), call **`validate_llm_provider_environment()`** once after config import when the web app starts.

⚠️ **Decision:** Tier names in DB and API are **Little / Medium / Big** (parent brief said Small; AST-491 Q6 and AST-492 title use **Little** — **Little** wins for code and DB).

## Stage 2: Agent table migration and data API

**Done when:** All agent rows carry **`brain_setting`**; **`save_agent` / `update_agent` / `get_agent` / `list_agents`** expose **`brain_setting`**; no code path **writes** `model_code` for new saves.

1. In `src/data/database.py`, extend agent schema migration: add **`brain_setting TEXT`** if missing.
2. Backfill **`brain_setting`** from **`model_code`** using the fixed map in stage 1 table (haiku→Little, sonnet→Medium, opus→Big, else Medium).
3. Change **`save_agent`** signature to **`brain_setting: Optional[str] = None`** (and stop accepting **`model_code`** for new writes — or accept both only for one transition commit where **`model_code`** maps to tier if **`brain_setting` absent — pick **one**; prefer **require `brain_setting`** on create, optional on update with same validation).
4. Update **`_UPDATE_AGENT_ALLOWED`** frozenset to replace **`model_code`** with **`brain_setting`**.
5. Update **`list_agents`** SELECT to prefer **`brain_setting`** column in returned dicts.

## Stage 3: Wire `do_task` + admin CRUD + adhoc (Anthropic only)

**Done when:** Production **`do_task`** path resolves tier for Anthropic; admin cannot set invalid tiers; **`active_provider`** deepseek fails before network; **`run_adhoc`** path consistent.

1. In `src/core/agent.py` **`do_task`**, replace **`agent_model_code = agent_row.get("model_code")`** block with **`brain_setting`** load + **`get_active_llm_provider()`** branch per Stage 1.
2. Keep **`send_to_anthropic`** signature and **`calculate_cost_*`** keyed by Anthropic **`AGENT_CONFIG`** alias (resolved key).
3. In `src/ui/api/api_admin.py`, update **`create_agent`** / **`update_agent`** bodies and validations per Files table.
4. Update **`_resolve_adhoc`** and **`_enrich_tasks`** **`model_code`** usages to **`brain_setting`** resolution.
5. Add/adjust tests listed in Files table until green (**`pytest`** scoped to touched tests acceptable for **build-astral**).

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Touches **`config.py`** (platform-wide literals), **`database.py`** agent persistence, **`agent.py`** core orchestration, and **`api_admin.py`**.

**Conf:** `high` — Mirrors existing **`AGENT_CONFIG`** + **`get_model`** patterns; migrations follow **`_ensure_*_schema`** style in **`database.py`**.

**Risk:** `HIGH` — Wrong tier mapping or migration default routes production traffic to the wrong Anthropic SKU or clears model selection; startup validation must prevent silent DeepSeek attempts without keys.

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** Centralize tier strings and maps only in **`config.py`**; no duplicate tier lists in React or DB layer.
- **§2.1 config:** All provider/tier/pricing literals in **`config.py`**; **`DEEPSEEK_API_KEY`** / **`ANTHROPIC_API_KEY`** only via **`os.environ`** in validation and existing clients.
- **§2.4 batch processing:** No change to **`batch_id`** pattern.
- **§2.6 state machine:** No change.
- **§3.3 imports:** **`config`** helpers stay utils-pure; **`validate_llm_provider_environment`** may use **`os.environ`** only.
- **§3.5 naming:** snake_case Python; API JSON **`brain_setting`** matches DB column.

No conflicts identified; if DeepSeek public pricing is not yet fixed, stop for Susan input rather than shipping guessed **`cpm_*`** (that would be **`conf-!!-NONE`**).

## Review stub (Ada — build)

- **Publish ref:** [`origin/sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings`](https://github.com/susansomerset/astral/tree/sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings) — branch tip includes **`docs(AST-492): review stub`** after the three **`feat(AST-492):`** code commits (**`git cherry-pick`** order Stage 1 → 3).
- **Integration:** Implemented on **`dev-ada`** as three commits (**`feat(AST-492):`** … Stage 1–3), cherry-picked in order onto the **`sub/*`** ref.

## Execution contract

Per **`plan-astral`**: execute stages in order; one commit per stage on **`dev-ada`** during **build-astral**; cherry-pick commits whose subject includes **`AST-492`** onto **`origin/sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings`** via detached **`/tmp/astral-ada-pub-AST-492-$$`** worktree only. Do not merge unrelated **`dev-ada`** commits into this **`sub/*`** ref.

## Review

**Reviewer:** Radia. **Diff:** `origin/dev`…[`origin/sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings`](https://github.com/susansomerset/astral/tree/sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings). **Code tip:** `abc5fbe68cff6b219fb62c9012cc7db45e15a574`.

### What’s solid

- `LLM_PROVIDER_CONFIG` / `DEEPSEEK_MODEL_PRICING` / tier helpers match the approved plan; DeepSeek rates carry an explicit vendor citation and date in config.
- Agent schema adds `brain_setting` with deterministic backfill from legacy `model_code`; new rows require tier; `validate_llm_provider_environment()` runs at Flask startup with bracket env reads.
- `do_task` resolves Anthropic SKUs from tier; non-Anthropic provider path is deferred correctly on this slice (DeepSeek lands in AST-493 chain).

### Issues / notes

| Severity | Topic | Location | Note |
|----------|-------|----------|------|
| discuss | Admin JSON shape | `database._expose_agent_public` | Resolving `model_code` / `resolved_model_key` from the **active** provider is deliberate for UI compat; confirm no consumer assumes `model_code` stays a literal AGENT_CONFIG alias when `active_provider` flips. |

### Recommended actions

| Priority | Action |
|----------|--------|
| Later | If product needs stable per-row vendor metadata, consider an explicit field rather than overloading `model_code`. |

## Resolution — 2026-05-26

- Radia **`review-astral`** surfaced **discuss** only ( **`_expose_agent_public`** `model_code` / `resolved_model_key` semantics when **`active_provider`** changes); **no fix-now** items. Publish tip reviewed: **`abc5fbe68cff6b219fb62c9012cc7db45e15a574`** (**`origin/sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings`**). Product unchanged on resolve pass; callers remain tier + provider–aware via existing integration tests and AST-493 dispatch.
- **§9a** dry-runs (**`merge-tree`** vs **`origin/dev`** and parent **`origin/ftr/AST-491-support-other-ai-models-deepseek`**) run clean before **`User Testing`**.

