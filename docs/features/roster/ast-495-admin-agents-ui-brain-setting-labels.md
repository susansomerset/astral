<!-- linear-archive: AST-495 archived 2026-06-15 -->

## Linear archive (AST-495)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-495/admin-agents-ui-brain-setting-labels-support-other-ai-models-deepseek  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-491 — Support other ai models: DeepSeek  
**Blocked by / blocks / related:** parent: AST-491

### Description

## What this implements

Administrator **Manage Agents** UI shows **Little / Medium / Big** `brain_setting` choices (from config) instead of vendor-specific model names. Runtime resolution to the active provider’s concrete model is opaque to the admin user in v1.

## Acceptance criteria

3. Each agent used in production can be configured with **Little**, **Medium**, or **Big** tier; changing tier changes which concrete model runs for that agent under the active provider, verifiable from admin agent detail or logged call metadata.

## Boundaries

Does not add per-candidate provider picker in UI (config-only for v1). Does not implement DeepSeek client or timesheet migration—siblings. Does not change timesheet list/export screens unless required for `brain_setting` display on agent rows only.

## Notes for planning

* Coordinate with Ada on API shape for agents list/update (`brain_setting` vs legacy `model_code`).
* Labels must match config literals: Little, Medium, Big.

## Git branch (authoritative)

Per **orientation-astral** § Branch law: parent `ftr/AST-491-support-other-ai-models-deepseek`, child `sub/AST-491/<child-segment>`. Created at dispatch-linear.

### Comments

#### radia — 2026-05-26T22:45:23.706Z
**Diff:** three-dot `origin/dev` vs **AST-491 dispatch** [`sub/AST-491/AST-495-admin-agents-ui-brain-setting-labels`](https://github.com/susansomerset/astral/tree/sub/AST-491/AST-495-admin-agents-ui-brain-setting-labels). **Publish tip:** `32ab64dee4e25015fd794db4f6fc447ca6ea7a31`.

- **Config-driven tiers** — `GET /api/admin/agents/brain_settings` feeds the Manage Agents picker; TS does not own an authoritative `["Little","Medium","Big"]` hardlist (aligned with §1.4 / §2.1).
- **Persistence** — Add/edit payloads send `brain_setting`; list shows tier verbatim or em dash when unset.
- **Product fit** — Anthropic-specific CPM readout dropped so admins are not misled once DeepSeek tiers exist.

**advisory** — Catalog fetch `.catch(() => {})` swallows failures (empty tiers, no toast). Fine as polish backlog unless Susan wants load errors surfaced.

Review appendix (cherry-pick target): [`ast-495-admin-agents-ui-brain-setting-labels.md`](https://github.com/susansomerset/astral/blob/0ce0da4ddb9892cfa749176b1f95cd055a83b947/docs/features/roster/ast-495-admin-agents-ui-brain-setting-labels.md) @ `0ce0da4d`.

#### katherine — 2026-05-26T22:42:55.575Z
**test-astral** — manifest green after integration publish.

**Publish:** `origin/sub/AST-491/AST-495-admin-agents-ui-brain-setting-labels` @ `32ab64de` (`fix(AST-495): stack AST-492/493 product for integrated Betty manifest`).

**Integration:** Betty’s prior tip only carried QA/tests without full AST-492/493 product; merged sibling `sub/AST-491/AST-492-…` then `AST-493-…` on `dev-kath`, then recreated the stacked product tree on the publish ref (no unrelated `dev-kath` churn).

**Manifest (Betty)**

1. Pytest — pass:

```bash
./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst492LlmBrainTierConfig tests/component/data/database/test_agents.py tests/component/core/test_agent.py::TestAst492BrainSettingDoTask tests/component/ui/api/test_api_admin.py::TestAdminConfigAndAgents
```

(`run_component_tests.sh` also runs full Vitest at the end; use item 2 for the scoped Vitest Betty listed.)

2. Vitest — pass:

```bash
cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx
```

#### betty — 2026-05-26T22:36:48.970Z
[check-linear]

- Cleared Betty’s **`[qa-handoff]`** thread by publishing the stacked QA commits ( **`test(AST-495)`** Vitest + bible, then **`test(AST-492)`** **`do_task`** DeepSeek mock, **`test(AST-494)`** timesheet **`agent_req_id`**, **`docs(AST-493)`** §**7.13ze** on the publish ref).
- Published: **`origin/sub/AST-491/AST-495-admin-agents-ui-brain-setting-labels`** @ **`075d42aeb22955e241e10c618bdfedb58e194fe9`**.

**Manifest**

1. Pytest (§7.13zd):  
   `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst492LlmBrainTierConfig tests/component/data/database/test_agents.py tests/component/core/test_agent.py::TestAst492BrainSettingDoTask tests/component/ui/api/test_api_admin.py::TestAdminConfigAndAgents`
2. Vitest (**§6c** page):  
   `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx`

**Betty:** Set status **Tests Ready** if UI still **Code Complete**.

@Katherine Johnson — **`test-astral`** after green on the manifest.

#### betty — 2026-05-26T22:27:53.332Z
[qa-handoff]

**Integrated on `dev-betty`:** merge commit `0d3bfecd` (AST-495 tip + conflict resolution with AST-492 for `api_admin` / `config`). QA commit `4715e281` (bible §7.13zd, Vitest `AdminAgentPrompts` brain_settings mock, `TestAdminConfigAndAgents` catalog assertions, dedupe `test_config` AST-492 class).

**Manifest (pytest narrow):**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst492LlmBrainTierConfig \
  tests/component/data/database/test_agents.py \
  tests/component/core/test_agent.py::TestAst492BrainSettingDoTask \
  tests/component/ui/api/test_api_admin.py::TestAdminConfigAndAgents
```
**Vitest:** `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx`

**Publish note:** cherry-pick `4715e281` onto `origin/sub/AST-491/AST-495-admin-agents-ui-brain-setting-labels` **conflicts** — that branch tip predates the AST-492+495 merged admin/config shape. Tests and bible expect the integrated tree on `dev-betty`. Prefer **test-astral** from `dev-betty` (or rebase/rollup child onto parent that already includes AST-492, then replay QA commit).

— Betty

#### betty — 2026-05-26T22:24:12.981Z
@susan — integration blocker on **`dev-betty`**: merging **`origin/sub/AST-491/AST-495-admin-agents-ui-brain-setting-labels`** conflicts in **`src/ui/api/api_admin.py`** and **`src/utils/config.py`** against the lineage that already carries **AST-492** (+ **AST-493** docs tip). Betty won’t resolve product merges per **`qa-astral`**.

Recommendation: Katherine (or rollup) aligns **AST-495** with the sibling stack on the authoritative integration line (rebasing / merging the sibling composition Chuckles expects for **AST-491**), then re-publishes **`sub/…/AST-495-…`** so QA can **`merge`** cleanly and add page-level Vitest per **§6c**.

— Betty

#### katherine — 2026-05-26T22:07:45.053Z
**Plan doc:** `docs/features/roster/ast-495-admin-agents-ui-brain-setting-labels.md`  
**Published to:** `origin/sub/AST-491/AST-495-admin-agents-ui-brain-setting-labels` (cherry-pick `30f4e7d3`)  
**GitHub (convention per workflow):** https://github.com/susansomerset/astral/blob/ftr/AST-495/docs/features/roster/ast-495-admin-agents-ui-brain-setting-labels.md  

**Self-assessment (with justification)**  
- **Scope (`Single-Component`):** Only `AdminAgentPrompts.tsx` is in the implementation file table; timesheets and provider UI stay out of scope per the ticket boundaries.  
- **Conf (`Medium`):** Exact catalog URL and JSON keys come from AST-492’s merged `api_admin.py`; the plan requires reading that file on the integration tip instead of guessing field names.  
- **Risk (`Medium`):** If POST/PUT sends the wrong field name or the UI hardcodes tiers, admins could save a bad config; the plan forces server-driven catalog options and matching save payload names to reduce that.

**Note:** Linear still shows **AST-492** as blocker; `build-astral` should wait until agent `brain_setting` + catalog exist on the integration line, as stated in Stage 1 step 1.

---

# Admin Agents UI: `brain_setting` labels (Little / Medium / Big)

**Parent Linear issue:** [AST-491 — Support other ai models: DeepSeek](https://linear.app/astralcareermatch/issue/AST-491/support-other-ai-models-deepseek)  
**Feature ref (origin only):** `ftr/AST-495` (per orientation; this child’s publish ref is `sub/AST-491/AST-495-admin-agents-ui-brain-setting-labels` on `origin`).  
**Assigned ticket:** [AST-495](https://linear.app/astralcareermatch/issue/AST-495/admin-agents-ui-brain-setting-labels-support-other-ai-models-deepseek)

## Summary

Administrators use **Manage Agents** (`AdminAgentPrompts.tsx`) to configure agents. After platform work on multi-provider routing, agents are identified by a **capability tier** (`brain_setting`) whose canonical literals are **Little**, **Medium**, and **Big**—not vendor SKUs. This plan replaces vendor **model** selection and labels in that screen with tier selection and tier labels. Runtime mapping from tier + active provider to concrete model stays on the backend (AST-492 / config); the UI does not show or edit Anthropic/DeepSeek model ids in v1.

**Dependency:** Linear lists **AST-492** as blocking. **Do not start `build-astral` implementation until** the API and agent persistence for `brain_setting` (and any tier catalog endpoint) from AST-492 are present on the branch you integrate from (typically `origin/sub/…` AST-492 or merged parent integration). If those endpoints or fields are missing when executing a step, stop and comment on **[AST-491](https://linear.app/astralcareermatch/issue/AST-491/support-other-ai-models-deepseek)** per the execution contract—not on a sibling-only thread.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | Tier-based UX: list column, add/edit payloads, catalogs from API (no vendor model picker for agents) | ui |

**Out of explicit scope per ticket:** timesheet list/export screens; DeepSeek client; per-candidate provider picker. **Coordinate with Ada (AST-492)** on JSON field names and catalog route path; steps below assume a **tier catalog** and **agent CRUD** that expose `brain_setting`. If the merged API uses different names, follow the merged API and update this plan in a **Revisions** section before building.

---

## Stage 1: Align data types and loading with AST-492 API

**Done when:** The page compiles, loads agents and tier catalog from the new/updated admin endpoints, and holds tier state in React state without yet changing modals or list rendering (or: if you prefer one commit, complete Stage 2 in the same branch before commit—still execute steps in order).

1. Open `src/ui/api/api_admin.py` on the **same integration tip** as the frontend and identify the **authoritative** shapes after AST-492:
   - Agent row fields on `GET /api/admin/agents` and `GET /api/admin/agents/<agent_id>`: confirm presence of `brain_setting` (string).
   - Tier catalog: the route that lists allowed tiers plus any `default_temperature` / `default_max_tokens` Ada exposes (exact path—e.g. a new `GET /api/admin/...`—**copy from live code**, do not invent).
2. In `AdminAgentPrompts.tsx`, introduce a **`BrainSettingCatalogRow`** interface (name may match JSON) matching that catalog payload: at minimum a stable **`brain_setting`** key and label text if separate; include numeric defaults only if the API provides them.
3. Replace **`ModelConfig`** / **`models`** state used for **agent configuration** with catalog state, e.g. **`brainSettings`** loaded once on mount from the catalog URL identified in step 1 (same `api()` client and error handling pattern as today’s `models` fetch).
4. Extend the **`Agent`** interface with **`brain_setting?: string`** (and keep other fields the API returns). Do **not** hardcode the tier set `["Little","Medium","Big"]` in TypeScript for **authoritative** options—**dropdown options must come from the catalog response** (ASTRAL_CODE_RULES §1.4 / §2.1: allowed values originate in config; server reflects config). If the API returns only those three rows with `brain_setting` equal to `Little` | `Medium` | `Big`, that satisfies the rule.
5. Remove or stop calling **`GET /api/admin/agents/models`** from this page **once** the tier catalog supersedes it for agent create/edit. If Ada temporarily keeps both, use only the tier catalog for the agent form; do not show `AGENT_CONFIG` vendor rows to admins on this screen.

---

## Stage 2: List, add, and edit UX — tiers only (no vendor names)

**Done when:** The Manage Agents table column shows tier labels (**Little / Medium / Big** matching server literals), add/edit sends **`brain_setting`** on POST/PUT as required by **`api_admin.py`**, and vendor-specific model names are not selectable or displayed for agent configuration. Saving an agent persists tier through the backend.

1. Rename the list column keyed **`model_code`** to **`brain_setting`** in **`LIST_COLUMNS`**: **`label`** should read **`Brain setting`** (or **`Tier`**—pick one term and use consistently in headings and modal). Sorting may sort on raw `brain_setting` string server order is fine if `sortable` remains true.
2. Replace **`modelLabel()`** / **`renderedAgents`** mapping: display the **`brain_setting`** string from each agent row. If absent/null, show **`—`** (same as empty model today). Prefer **verbatim** API string for display so labels stay aligned with config literals (**Little**, **Medium**, **Big**).
3. Replace **`editModel`** / **`addModel`** state with **`editBrainSetting`** / **`addBrainSetting`** (strings). Initialize **`addBrainSetting`** to the **first catalog entry’s** `brain_setting` when catalog loads (mirror current `models[0].model_code` behavior).
4. Replace **`applyModelDefaults`** with **`applyTierDefaults(brain_setting, setter)`**: read **`default_temperature`** and **`default_max_tokens`** from the catalog row matching `brain_setting`. If AST-492’s catalog **does not** include defaults per tier, **stop** and post a blocker comment on **AST-491** (Step: apply tier defaults; Issue: no defaults source; propose: extend catalog vs keep agent-stored temps).
5. In **`openEdit`**, set edit tier from **`full.brain_setting`** (fallback empty string). Remove reading **`full.model_code`** for the **tier** control (legacy field may still exist in JSON—**do not** surface it in UI).
6. **`handleEditSave`** / **`handleAddSave`**: send JSON **`brain_setting`** (not **`model_code`**) with the same optionality rules as today’s model field (omit or send empty only if API allows; match **`create_agent` / `update_agent`** parameter names in `api_admin.py`). Keep **`content`**, **`temperature`**, **`max_tokens`** unchanged unless Ada’s contract removes them.
7. Replace **`ModelFields`** with a **`BrainSettingFields`** (or renamed) component:
   - **Select** options: map **`brainSettings`** from API to **`<option value={row.brain_setting}>`**; option **visible text** must be the human label specified by API (if only `brain_setting` exists, use that string—must be **Little**, **Medium**, **Big** per product copy).
   - **Remove** the **`agent-model-costs`** CPM block (`In: $…/M`, etc.). Tier-to-vendor pricing is opaque in v1; showing Anthropic-only CPM under a tier is misleading.
8. After save, **`loadAll()`** must show updated tier in the grid.

---

## Stage 3: Verification (no new files)

**Done when:** Manual checks pass; no new Playwright unless Betty’s manifest requires it.

1. **Compile:** `npm run build` in `src/ui/frontend` (or project-standard frontend build) succeeds.
2. **Manual:** Open **Manage Agents**; confirm list shows **Little / Medium / Big** (or **—** for unset). Add agent with each tier; reopen edit; values round-trip. Confirm network payloads use **`brain_setting`** only for tier (no vendor model in body for this screen).
3. **Regression:** Delete flow, system prompt textarea, temp/max tokens behavior unchanged except defaults from tier catalog when changing tier.

---

## Execution contract (for the developer agent)

Per **plan-astral**: execute stages in order; one commit per stage on **`dev-kath`** during **build-astral**, then publish per **build-astral** / orientation (cherry-pick to **`origin/sub/AST-491/AST-495-admin-agents-ui-brain-setting-labels`** for this child). Do not add files not listed. If AST-492 API differs from assumptions here, **stop** and comment on **AST-491** with proposed resolutions.

---

## Review stub (build AST-495)

- **Publish ref:** `origin/sub/AST-491/AST-495-admin-agents-ui-brain-setting-labels`
- **Commit:** *(update after cherry-pick / push)*

**Integration note:** Until AST-492 persists **`brain_setting`** on agent rows, the admin API attaches **`brain_setting`** for list/detail via **`brain_setting_for_anthropic_agent_key(model_code)`**, and accepts **`brain_setting`** on POST/PUT by resolving to the Anthropic **`AGENT_CONFIG`** alias (**`anthropic_agent_key_for_brain_setting`**). **`GET /api/admin/agents/brain_settings`** serves the tier catalog from config. AST-492’s **`LLM_PROVIDER_CONFIG`** can replace duplicated tier literals later.

---

## Self-Assessment

**Scope:** `Single-Component` — Touches only the Manage Agents page component; backend contract is consumed, not implemented here.

**Conf:** `Medium` — Correctness depends on AST-492’s finalized JSON and routes; the plan defers exact URLs to the merged `api_admin.py` and requires verification on integration tip.

**Risk:** `Medium` — Wrong payload or label drift could misconfigure agents or confuse admins; mitigation is server-driven catalog and verbatim tier display strings.

---

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** Single shared tier selector component for add/edit; avoid duplicating option lists.
- **§2.1 config / §1.4:** Tier **options** from API (config-backed), not hardcoded sets in React.
- **§2.4 / §2.6:** Not applicable (no batch/state machine in this UI).
- **§3.3 imports:** Frontend-only; existing `api` client.
- **§3.5:** Keep page flat in **`pages/`**; styles remain in **`App.css`** only if new classes are needed—prefer existing **`dep-*`** patterns already used in this file.

No conflicts flagged; if Ada exposes legacy **`model_code`** alongside **`brain_setting`**, UI must ignore **`model_code`** for display and editing on this ticket.

## Review

**Reviewer:** Radia. **Diff:** `origin/dev`…[`origin/sub/AST-491/AST-495-admin-agents-ui-brain-setting-labels`](https://github.com/susansomerset/astral/tree/sub/AST-491/AST-495-admin-agents-ui-brain-setting-labels). **Code tip:** `32ab64dee4e25015fd794db4f6fc447ca6ea7a31`.

### What's solid

- Manage Agents consumes `/api/admin/agents/brain_settings`; tier options are server-driven (no authoritative hardcoded trio in TS), matching §1.4 / §2.1.
- List/add/edit send `brain_setting`; vendor CPM strip avoids misleading Anthropic-only pricing under a tier label.
- Unmapped tier shows a guarded select state (`— (unmapped) —`) instead of silently coercing.

### Issues / notes

| Severity | Topic | Location | Note |
|----------|-------|----------|------|
| advisory | Silent fetch failure | `AdminAgentPrompts.tsx` | `.catch(() => {})` on catalog load hides network errors — empty dropdown without toast. Acceptable polish debt unless Susan wants surfaced errors here. |

### Recommended actions

| Priority | Action |
|----------|--------|
| Optional | Surface a toast on brain_settings fetch failure for faster admin diagnosis. |

---

## Resolution — 2026-05-26

**Radia review:** `review-astral` on **`Review Posted`**; consolidated findings in **Review** above (code tip **`32ab64dee4e25015fd794db4f6fc447ca6ea7a31`** cited in-plan).

**Changes vs review**

| Class | Handling |
|-------|----------|
| **Solid / verified** | No product delta this pass — implementation already aligned (config/catalog-driven tiers, `brain_setting` on list/add/edit, Anthropic-specific CPM removed). |
| **Advisory — silent catalog fetch** | Deferred as optional polish (toast / surfaced load error per **Recommended actions**); not required to close **`Review Posted`** on happy path. |

**Git / process:** **`dev-kath`** merged **`origin/dev`** then **`origin/sub/AST-491/AST-495-admin-agents-ui-brain-setting-labels`** per resolve-astral §4; subsequent **`origin/sub/AST-491/AST-495-admin-agents-ui-brain-setting-labels`** tip updated by cherry-picking only commits whose subject references **AST-495** (no wholesale merge from **`dev-kath`**).

