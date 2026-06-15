# AST-491 — Support other ai models: DeepSeek

<!-- linear-archive: AST-491 archived 2026-06-15 -->

## Linear archive (AST-491)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-491/support-other-ai-models-deepseek  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Astral routes every AI agent call through a single Anthropic-backed stack today. That locks cost and capacity to one vendor and makes it hard to experiment with DeepSeek (already keyed in local and Railway env) without rewriting agent configuration per model name. This feature introduces a second LLM provider and a **Small / Medium / Big** capability tier so roster (and all other) agent work can run on the provider chosen for the candidate, with equivalent tier semantics on each side—e.g. a “Big” Anthropic call and a “Big” DeepSeek call without agents hard-coding vendor SKUs. Susan expects accurate per-call cost accounting across providers, including cache-hit tracking where the vendor supports it, so admin cost views remain trustworthy after the split.

## Functional scope

* **Provider catalog:** The product recognizes at least two LLM providers: the existing Anthropic integration and DeepSeek. Provider credentials are supplied via environment configuration (no secrets in app config).
* **Tier-based agent configuration:** Each configured agent is assigned a **Small**, **Medium**, or **Big** tier (not a vendor-specific model id). At runtime the system resolves tier + active provider to the concrete model and call defaults (temperature, token limits, cache thresholds) defined in product configuration.
* **Candidate provider selection:** For a given candidate session, AI work uses the provider configured for that candidate (Anthropic or DeepSeek). When DeepSeek is selected, tier resolution uses the DeepSeek mapping; when Anthropic is selected, the Anthropic mapping. Behavior of prompts, tasks, grading, and response validation is unchanged—only the backend model and billing path differ.
* **Unified AI dispatch:** All existing agent/task flows that today invoke the shared AI entry point continue to work without callers choosing a vendor; routing is centralized based on agent tier and candidate provider.
* **Per-provider cost logging:** Every completed provider API call records token usage and computed cost in persistent storage. Anthropic-originated history is retained in provider-specific storage; DeepSeek (and future providers) log to a generalized agent-timesheet store with provider-neutral request identifiers and the same analytical dimensions already used for batch, candidate, task, and performance fields. Cache read (“hit”) volumes are stored and costed even when the vendor does not bill cache creation separately.
* **Configuration-driven mappings:** Canonical tier → model and pricing metadata for each provider live in config (single source of truth per code rules). Adding or retargeting a tier mapping does not require code changes beyond config updates.
* **Admin visibility:** Existing administrator views for agents and timesheets continue to show model/tier and cost data; they reflect multi-provider rows after the change (no silent loss of historical Anthropic data).

## Boundaries

* **Not in scope:** Additional providers beyond DeepSeek (OpenAI, Gemini, etc.), per-task provider overrides, or changing TASK_CONFIG prompts/schemas/grading rules.
* **Not in scope:** DeepSeek “agent tool” integrations (Claude Code, Copilot, etc.) that bypass Astral’s own dispatch—only in-app `do_task` / agent flows.
* **Not in scope:** Replacing or redesigning candidate API keys (`candidate_api_key`) unless Susan explicitly ties them to LLM provider choice in a follow-up.
* **Must not break:** Existing Anthropic agents and tasks on candidates still configured for Anthropic; batch locking, `agent_data`, `agent_responses`, and dispatch ledger linkage; [AST-324](https://linear.app/astralcareermatch/issue/AST-324/refactor-timesheets-to-allow-confident-cost-calculations) timesheet granularity and cost-reconciliation workflows.
* **Config discipline:** Allowed providers, tiers, and model/pricing catalogs are config-driven literals; API keys remain environment-only (no fallbacks).
* **Project note:** Ticket lives under **Astral Roster**, but capability is **platform-wide** (any feature using the shared AI entry point). Roster inflow ([AST-490](https://linear.app/astralcareermatch/issue/AST-490/roster-inflow)) and other backlog roster work are separate unless Susan later declares a hard dependency.

## Acceptance criteria

1. With `DEEPSEEK_API_KEY` set in the runtime environment, a DeepSeek-configured candidate can complete at least one end-to-end agent task (same success/failure semantics as today on Anthropic) without manual provider selection in application code paths.
2. With a candidate still on Anthropic, existing agent tasks behave as before (no regression in pass/fail handling for a representative graded task).
3. Each agent used in production can be configured with **Small**, **Medium**, or **Big** tier; changing tier changes which concrete model runs for that agent under the active candidate provider, verifiable from admin agent detail or logged call metadata.
4. Tier **Big** on Anthropic and tier **Big** on DeepSeek for the same agent definition invoke different vendor models per the configured mapping table (not the same hard-coded model id for both).
5. After Anthropic calls, cost rows appear in Anthropic-dedicated timesheet storage with historical rows preserved across deploy/migration.
6. After DeepSeek calls, cost rows appear in generalized agent-timesheet storage with `agent_req_id` (or equivalent neutral id), token breakdown fields populated, and a non-null computed total cost.
7. For DeepSeek calls that return cache read usage, stored rows include cache read token counts and a cost component for cache reads; cache write cost may be zero when the vendor does not charge for creation.
8. Administrator timesheet listing/export includes entries from both storage locations (or a unified query) for a date range that spans Anthropic-only and DeepSeek-only activity.
9. Missing required provider API key for the selected candidate provider causes startup or call failure consistent with existing secret handling (fail loud, no silent fallback to the other vendor).

## Dependencies and blockers

* [AST-324](https://linear.app/astralcareermatch/issue/AST-324/refactor-timesheets-to-allow-confident-cost-calculations) (Done): Refactored timesheets and `AGENT_CONFIG`—this feature extends that foundation; planners should read the merged behavior on `origin/dev`.
* **Environment:** `DEEPSEEK_API_KEY` in local `.env` and Railway (Susan confirmed). Anthropic keys unchanged.
* No blocking open sibling tickets identified. [AST-490](https://linear.app/astralcareermatch/issue/AST-490/roster-inflow) (Roster inflow) does not block provider support unless Susan decides inflow must ship only on DeepSeek.

## Open questions

1. **Where is provider chosen?** Per candidate record, global default, environment flag, or admin UI—and can two candidates on the same deployment use different providers concurrently?
   1. Provider will be set in the config.py file for now.  We may later give candidates the option to use another provider, but for now, it's config-driven.
2. **Tier catalog:** Is **Small / Medium / Big** exhaustive for every agent, or do any agents need a legacy direct model binding (e.g. always-Haiku prefilter)?
   1. No, the tier catalog is that simple and should stay that way.
3. **Mapping ownership:** Confirm the initial Anthropic ↔ DeepSeek model pairs per tier (Susan mentioned Opus-class “Big” on Anthropic—which exact alias—and which DeepSeek SKUs: `deepseek-v4-flash`, `deepseek-v4-pro`, thinking vs non-thinking).
   1. Right: Big is "deepseek-v4-pro" + thinking, Medium is v4-flash + thinking, and Small is v4-flash without thinking.
4. **API compatibility:** Ship using DeepSeek’s Anthropic-compatible API surface (minimal change to current call shape) vs OpenAI-compatible chat completions—Susan’s brief references both.
   1. Absolutely use the anthropic compatible API surface for reasons stated.
5. **Timesheet cutover:** Rename/migrate existing `timesheets` → Anthropic-only table only, or maintain a compatibility view/API name for admin tools during transition?
   1. Migration will involve an append of all anthropic data from anthropic_timesheets into agent_timesheets, and then rewiring the apis calling the timesheets table to use agent_timesheets instead and reference "agent_req_id" instead of "anthropic_req_id", but no other logical change will be needed because we are preserving the column names.
6. **Admin UX in v1:** Must Agents admin let Susan pick tier (and/or provider), or is tier/provider config-only until a later UI ticket?
   1. Only change here is the labels in the config:  Models will now be brain_setting "Big/Medium/Little" and whatever that setting maps to for the provider, that's what is used at runtime.
7. **Thinking / reasoning:** Should any tier enable DeepSeek thinking/reasoning modes, or stay aligned with today’s non-thinking production calls only?
   1. Definitely need to support the thinking modes for flash and pro, as well as non-thinking for flash.

---

## Original brief

Right now we support anthropic, and our models are exclusively from that source.

We need to add DeepSeek and assign models to the agents.  I think we're going to just see if we can support "Small/Medium/Big" for models rather than explicitly call the model name for the agent, then if the candidate uses deepseek instead of anthropic, there's an equivalent "Big" model to use where we might use Opus 4.7 from anthropic.

I have already set up the env variable in the local astral/.env file for DEEPSEEK_API_KEY (and saved it to variables on railway).

**Deliverables for this ticket will be:**
new file: src/externals/deepseek.py --> Functionally identical to [anthropic.py](<http://anthropic.py>) 
updates: timesheets in astral.db becomes anthropic_timesheets
new table: agent_timesheets --> Structurally identical to anthropic_timesheets with generalized field names: agent_req_id vs anthropic_req_id, but all other columns remain the same.  (DeepSeek does not differentiate price on cache write vs no cache, but we still want to track the cache reads ("cache hits"), and calculate the cost for each call.

From DeepSeek:

# **Your First API Call**

The DeepSeek API uses an API format compatible with OpenAI/Anthropic. By modifying the configuration, you can use the OpenAI/Anthropic SDK or softwares compatible with the OpenAI/Anthropic API to access the DeepSeek API.

| **PARAM** | **VALUE** |
| -- | -- |
| base_url (OpenAI) | `https://api.deepseek.com` |
| base_url (Anthropic) | `https://api.deepseek.com/anthropic` |
| api_key | apply for an [API key](<https://platform.deepseek.com/api_keys>) |
| model\* | `deepseek-v4-flash`&#10;`deepseek-v4-pro`&#10;`deepseek-chat` (to be deprecated on 2026/07/24)&#10;`deepseek-reasoner` (to be deprecated on 2026/07/24) |

\* The model names `deepseek-chat` and `deepseek-reasoner` will be deprecated on 2026/07/24. For compatibility, they correspond to the non-thinking mode and thinking mode of `deepseek-v4-flash`, respectively.

## **Integrate with Agent Tools**

The DeepSeek API is supported by many popular AI agent and coding assistant tools. If you use tools like Claude Code, GitHub Copilot, or OpenCode, you can use DeepSeek as the backend model directly — no code required.

See the [Agent Integrations Guide](<https://api-docs.deepseek.com/quick_start/agent_integrations/claude_code>) for details.

## **Invoke The Chat API**

Once you have obtained an API key, you can access the DeepSeek model using the following example scripts in the OpenAI API format. This is a non-stream example, you can set the `stream` parameter to `true` to get stream response.

For examples using the Anthropic API format, please refer to [Anthropic API](<https://api-docs.deepseek.com/guides/anthropic_api>).

* **curl**
* **python**
* **nodejs**

```
curl https://api.deepseek.com/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${DEEPSEEK_API_KEY}" \
  -d '{
        "model": "deepseek-v4-pro",
        "messages": [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "Hello!"}
        ],
        "thinking": {"type": "enabled"},
        "reasoning_effort": "high",
        "stream": false
      }'
```

### Comments

#### chuckles — 2026-05-27T02:12:11.243Z
[check-linear]

**Root cause:** `do_task` / `_resolve_adhoc` passed **`candidate_api_key`** (per-candidate **Anthropic** key) into `send_to_deepseek` whenever `requires_candidate_key` was true — so `evaluate_jd` hit DeepSeek with your `sk-ant-…` key (401, suffix matched Anthropic).

**Fix (local `dev`, not yet on `ftr`):**
- `src/core/agent.py` — only set `api_key_override` from `candidate_api_key` when `active_provider == "anthropic"`.
- `src/ui/api/api_admin.py` — same for adhoc resolve.
- Tests: `test_deepseek_ignores_candidate_anthropic_api_key`, `test_resolve_adhoc_deepseek_does_not_use_candidate_anthropic_key`.

Restart backend after pull; DeepSeek calls use **`DEEPSEEK_API_KEY`** only. Candidate profile Anthropic key unchanged for when you switch back to `anthropic`.

— Chuckles

#### chuckles — 2026-05-27T02:04:03.812Z
[check-linear]

**401 on `evaluate_jd` — not a routing bug.** DeepSeek returned `authentication_error` / invalid API key (suffix `GQAA` in their message). `send_to_deepseek` reads **`DEEPSEEK_API_KEY`** only via `os.environ["DEEPSEEK_API_KEY"]` (`src/external/deepseek.py`); there is no code path that substitutes Anthropic’s key for DeepSeek calls.

**Checklist (local UAT):**
1. In `.env`, confirm **`DEEPSEEK_API_KEY`** is the key from [platform.deepseek.com](https://platform.deepseek.com/api_keys) — not `ANTHROPIC_API_KEY`, not a Railway placeholder, no stray quotes/newlines.
2. **Restart** the Flask process after any `.env` edit (startup validates the key when `LLM_PROVIDER_CONFIG["active_provider"]` is `"deepseek"`).
3. Quick sanity: `curl` or a one-line Python call against `https://api.deepseek.com/anthropic` with that key before re-running the dispatcher batch.
4. If local `.env` is correct but Railway fails, sync **`DEEPSEEK_API_KEY`** in Railway env for that deployment.

**Config note:** `active_provider` is **`deepseek`** in `config.py` on your tree — so consult/dispatch correctly targets DeepSeek; the failure is credential rejection, not Grace/Medium tier logic.

**ftr tip for reasoning-effort change:** `67627fc6` (Medium → `high`, Big → `max`) — cherry-picked from local `dev`; pull/merge that ref if you want UAT on the composite branch.

— Chuckles

#### susan — 2026-05-27T02:02:09.921Z
Running with new deepseek, we got errors:

\[evaluate_jd_batch_evaluate_jd-479421d8-427c-44cc-9753-d3f4b644d627\]

Error code: 401 - {'error': {'message': 'Authentication Fails, Your api key: \*\*\*\*GQAA is invalid', 'type': 'authentication_error', 'param': None, 'code': 'invalid_request_error'}}

#### chuckles — 2026-05-26T23:35:56.620Z
## Manual test steps

**Prerequisites:** `ANTHROPIC_API_KEY` and `DEEPSEEK_API_KEY` in `.env`; restart backend after any config change. Local **`dev`** merged from **`origin/ftr/AST-491-support-other-ai-models-deepseek`** @ **`0c69865d`** (`aa0d2f96` on local dev). Component harness green on that ftr tip.

### Config & provider (AST-492 / AST-493)

1. In `src/utils/config.py`, confirm `LLM_PROVIDER_CONFIG["active_provider"]` is **`"anthropic"`**. Start app — should boot without error.
2. Change `active_provider` to **`"deepseek"`** (literal only). Restart — app must start only if `DEEPSEEK_API_KEY` is set; remove key temporarily to confirm fail-loud startup.
3. Set back to **`"anthropic"`** for steps below unless testing DeepSeek explicitly.

### Admin Agents — Little / Medium / Big (AST-495)

4. Open **Admin → Manage Agents**. Model column should show **Little**, **Medium**, or **Big** (not Haiku/Sonnet/Opus labels).
5. Edit an agent: tier dropdown lists three tiers from **`GET /api/admin/agents/brain_settings`**.
6. Save an agent as **Medium**; confirm list refresh shows **Medium**.

### Anthropic path (regression)

7. With `active_provider` **anthropic**, run one representative graded agent task (e.g. prefilter or consult step you know). Pass/fail behavior should match pre-change expectations.

### DeepSeek path

8. Set `active_provider` **deepseek**, restart. Run the same class of task as step 7. Confirm completion (or same structured failure as Anthropic would produce for bad input — not import/routing errors).

### Timesheets (AST-494)

9. Open **Admin → Agent Timesheets** (or export). Confirm rows load with **`agent_req_id`** (not `anthropic_req_id` in API/UI labels).
10. After steps 7–8, confirm new rows appear with token breakdown and non-null cost.
11. Optional: spot-check `anthropic_timesheets` still holds legacy Anthropic rows; `agent_timesheets` includes appended history + new calls.

### Cost reconciliation

12. If you use cost-reconciliation CSV flow, run a short date range spanning today’s test calls — export should include DeepSeek and Anthropic activity from the unified store.

---

`origin/ftr/AST-491-support-other-ai-models-deepseek` @ **0c69865d** · local **`dev`** @ **aa0d2f96**. All four **`sub/AST-491/*`** branches deleted from origin.

Reset after UAT: `git reset --hard origin/dev`

— Chuckles

#### betty — 2026-05-26T23:32:40.743Z
**qa-astral (Betty)** — component harness green; parent **`ftr` tip** pushed:

- **`origin/ftr/AST-491-support-other-ai-models-deepseek` @ [`0c69865d`](https://github.com/susansomerset/astral/commit/0c69865d)** — **`fix(AST-491)`**: Admin **`GET /api/admin/agents/brain_settings`** + **`config`** helpers (`brain_setting_for_anthropic_agent_key`, `admin_brain_setting_catalog`, …) parity with **`dev-betty` / Ada AST‑492‑495**, so **`AdminAgentPrompts`** contract matches product; **`test(AST-491)`** / **`docs(AST-491)`**: assertions use **`resolve_brain_setting_to_anthropic_agent_key`** + **`get_model`** / **`BRAIN_SETTINGS`** only (no test dependency on interim naming); bible §**7.13zd** (+ **`TestAst492ResolveAdhocApiAdmin`** in manifest rows).

Local verification: `./scripts/testing/run_component_tests.sh` green on **`dev-betty`**; publish worktree spot-check **`pytest`** on **`TestAdminConfigAndAgents`**, **`TestAst492ResolveAdhocApiAdmin`**, **`TestAst492LlmBrainTierConfig`**, **`TestCheckParseResultsBranches`**.

**Subs:** **`docs(AST-491)`** cherry onto each **`origin/sub/AST-491/*`** hit **`ASTRAL_TEST_BIBLE.md` conflicts only** — left at prior tips per § Test Bible (**`@Betty`** on rollup or re-run qa if subs need verbatim ftr bible blob).

_No Linear status moves (per Susan)._

— Betty

#### betty — 2026-05-26T23:18:33.259Z
**AST-491 / prep-uat / component suite (Betty pass)**

**dev-betty:** `ffb95003` — test-only fixes + **`docs/ASTRAL_TEST_BIBLE.md`** §7.13zd (admin CRUD empty `model_code` infer skip, **`TestEnrichTasks::test_enrich_tasks_unknown_llm_provider_skips_tier_catalog_lookups`**, manifest line). `./scripts/testing/run_component_tests.sh` was green on **`dev-betty`** before publishing.

**Pushed:** cherry-picked to **`origin/ftr/AST-491-support-other-ai-models-deepseek`** → **`082ec46c`** (had to resolve **`tests/component/utils/test_config.py`** vs existing **`TestAst492BrainSettingConfig`** on ftr; kept **`infer_brain_setting_from_legacy_model_code("")`** assertion and full **`TestAst492LlmBrainTierConfig`** helpers).

**Blocker:** re-running `./scripts/testing/run_component_tests.sh` on a detached worktree at **`082ec46c`** hit **10** pytest failures (**`test_roster.py`** parse_results trio, **`test_api_admin`** admin/adhoc gaps, **`TestAst492LlmBrainTierConfig`** calling **`anthropic_agent_key_for_brain_setting`** / **`admin_brain_setting_catalog`**). That means **tests+bible landed without the matching product lines** already present on **`dev-betty`** but not in the cherry-picked single commit atop old ftr.

**Recommendation:** sync the publish ref to the **same tree as `dev-betty`** (merge **`dev-betty`** into a throwaway **`origin/ftr/…`** checkout, rerun component script, **`git push`** `HEAD:ftr/AST-491-support-other-ai-models-deepseek`) **or** cherry-pick ordered SHAs between **`origin/ftr…`** merge-base and **`ffb95003`** that touch **`src/`** (`config.py`, roster, api_admin…) before treating ftr tip as authoritative.

Ping if you want a strict minimal cherry-pick list once someone can run `git cherry`/`log` locally — agent shell flake blocked that here.

— Betty

#### betty — 2026-05-26T23:08:13.995Z
**[qa-astral] bible sync (AST-491 epic)**

- **`docs/ASTRAL_TEST_BIBLE.md`** unified on **`dev-betty`** with **`§7.13zd`** + **`§7.13ze`** and one **`docs(AST-491): test bible — unified ftr definitive for epic 491`** commit (`493d8a0c` on `dev-betty`; provenance sentence under **`§7.13ze`**).
- **Definitive tip:** **`origin/ftr/AST-491-support-other-ai-models-deepseek`** @ **`a4707c70630117a0b81a71d5629c862c78fc481f`** — same **`ASTRAL_TEST_BIBLE.md`** blob (SHA-256 **`29ad62af5d224192d2305874b770c012df0291e0bebc0588f1c459f9d5484a38`**) now on **`ftr`** and **`origin/sub/AST-491/AST-{492..495}-…`** sibling branches (`a60009d1`, `557e0427`, `1cc77db6`, `83270132` respectively).

Rollup (**`rollup-child`** / merges into **`ftr`**) should be unblocked from bible skew; subs can merge **`ftr`** first per **`orientation-astral`** + **`qa-astral`** § Test Bible — sole authority.

— Betty

#### chuckles — 2026-05-26T22:48:47.975Z
@susan — **rollup-child** stalled merging **AST-493** `sub/…` → `ftr/AST-491-support-other-ai-models-deepseek` after **AST-492** rolled up cleanly (`ftr` tip `56508c32`).

**Conflict:** `docs/ASTRAL_TEST_BIBLE.md` (AST-492 vs AST-493 test sections).

**State:** All four children **User Testing** (492–495). **AST-494** / **AST-495** not yet on `ftr/` until 493 rollup completes.

**Next:** Resolve bible conflict on `ftr/` (or refresh **AST-493** `sub/*` with `origin/dev` + push, re-run rollup), then Chuckles can finish rollup + **prep-uat**.

— Chuckles

#### chuckles — 2026-05-26T22:05:36.698Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-491 (parent) | `ftr/AST-491-support-other-ai-models-deepseek` |
| AST-492 | `sub/AST-491/AST-492-llm-provider-brain-setting-tiers-and-tier-mappings` |
| AST-493 | `sub/AST-491/AST-493-deepseek-client-and-provider-dispatch-routing` |
| AST-494 | `sub/AST-491/AST-494-timesheet-split-migration-and-unified-admin-api` |
| AST-495 | `sub/AST-491/AST-495-admin-agents-ui-brain-setting-labels` |

**blockedBy:** AST-493 → AST-492; AST-494 → AST-493; AST-495 → AST-492

— Chuckles

#### chuckles — 2026-05-26T21:52:27.315Z
@susan — **AST-491** definition is on the ticket (Backlog). Seven open questions need your call before dispatch:

1. Where provider is chosen (per candidate vs global vs env vs admin).
2. Whether Small/Medium/Big covers every agent or some stay on a fixed model.
3. Initial tier → model mapping for Anthropic and DeepSeek (incl. thinking vs non-thinking SKUs).
4. Anthropic-compatible vs OpenAI-compatible DeepSeek API for v1.
5. Timesheet rename/migration vs compatibility layer for admin APIs.
6. Whether Agents admin must edit tier/provider in this epic or config-only v1.
7. DeepSeek thinking/reasoning modes in or out of scope.

Reply on the ticket or here; I’ll fold answers into the definition and we’re clear for **Todo + Chuckles** when you’re happy.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
