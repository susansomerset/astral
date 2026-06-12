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

