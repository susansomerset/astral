<!-- linear-archive: AST-1957 archived 2026-10-08 -->

## Linear archive (AST-1957)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1957/manage-agents-edits-the-plain-settings-refactor-agent-settings-and  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1953 — Refactor agent settings and ingest per-endpoint model options  
**Blocked by / blocks / related:** parent: AST-1953

### Description

## What this implements

The admin routes take and return the settings, and the models list drops brain sizes. The Manage Agents form gets plain inputs for each setting, and brain size and mode are removed. After #1. Does **not** touch the call path (#2).

## Citations

`stat.logging.info.api`.

## Scope

* `src/ui/api/api_admin.py` (**modified**):
  * **Modified agent create/update:** take and return the settings (type checks only) and no longer require or accept `brain_setting` / `mode`.
  * **Modified** `GET /agents/models`**:** returns model id, label, server and default output budget, with no brain sizes.
  * **Modified adhoc/workbench resolvers:** use the new resolver.
* `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` (**modified**):
  * **Modified form:** the Functional scope 7 inputs, sent as the settings keys.
  * **Removed:** brain-size and mode controls, the `AGENT_MODES` constant and the size pre-fill.
  * **Modified list columns:** show the settings.
  * **Modified model types:** drop brain sizes.
* Tests and bibles (Betty in `qa-child`):
  * `tests/component/ui/api/test_api_admin.py`
  * `tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx`
  * `docs/test-bible/ui/api/api_admin.md`
  * `docs/test-bible/frontend/pages.md`

## Acceptance criteria

"Stubbed client" means the component-test stubs of the Anthropic SDK client used by `test_llm_compat.py`, `test_anthropic.py` and `test_agent.py`.

10. **Manage Agents edits the settings.**
    * **Check (frontend component test):** the edit form renders the seven settings inputs and saves them under the settings keys, with no `brain_setting` or `mode` in the body.
    * **Check:** `rg -n "brain_setting|AGENT_MODES|Deterministic|Creative" src/ui/frontend/src/pages/AdminAgentPrompts.tsx` returns nothing.
    * **Fails if:** any input is missing or a retired control remains.

## Boundaries

Does not touch the call path (#2) or config/database (#1). Uses #1's resolver.

## Notes for planning

Parent AST-1953 Description is the authority (Functional scope, Technical scope, Susan's 2026-10-03 answers). Code it loosely — no vocabulary lists, no pre-send gating (Susan).

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1953-agent-settings`, child `sub/AST-1953/AST-1957-manage-agents-settings`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-03T23:19:49.006Z
[code-rubric] PROCEED (Commit: 9a514b89) Admin settings UI+API clean

#### betty — 2026-10-03T23:18:07.877Z
`origin/sub/AST-1953/AST-1957-manage-agents-settings` @ `9a514b899` · manifest in pages.md bible

#### joan — 2026-10-03T23:09:18.227Z
[plan-rubric] PROCEED (Commit: fb90852e7) Admin settings wired

#### ada — 2026-10-03T23:08:01.671Z
`origin/sub/AST-1953/AST-1957-manage-agents-settings` @ `fb90852e7` · plan ready

---

# AST-1957 — Manage Agents edits the plain settings

- **Ticket:** [AST-1957](https://linear.app/astralcareermatch/issue/AST-1957) · **Parent:** [AST-1953](https://linear.app/astralcareermatch/issue/AST-1953) Refactor agent settings and ingest per-endpoint model options
- **Publish ref:** `sub/AST-1953/AST-1957-manage-agents-settings` (origin only)
- **Canon Scope:** `stat.logging.info.api`

The admin agent routes stop requiring `brain_setting` / `mode` and pass the seven plain settings (`quantization`, `temperature`, `reasoning_effort`, `provider_allow_fallbacks`, `provider_only`, `provider_ignore`, `provider_sort`) straight to the data layer, which AST-1955 already type-checks. `GET /agents/models` drops brain sizes and returns each model's own default output budget. The Manage Tasks enrichment and the ad-hoc/workbench resolver switch from `resolve_model_brain` to AST-1955's `resolve_agent_settings`. The Manage Agents form loses its brain-size and mode controls and gains the Functional scope 7 inputs, and the list shows the settings. This ticket does **not** touch `agent.py` / `llm_compat.py` / `anthropic.py` (AST-1956), `config.py` / `database.py` (AST-1955), or live rows (AST-1958).

## Scope gate

Both files below are named in this ticket's `## Scope`. Every change is one of the kinds that Scope lists for its file: create/update take the settings, `GET /agents/models` drops brain sizes, the resolvers switch to the new resolver, the form gets the settings inputs and loses the retired controls, the list shows the settings, and the model types drop brain sizes. Tests and bibles listed there are Betty's (`qa-child`). No test-tree edits here.

## AC boundaries

| AC | Check | Closed here by | Closes on ftr after |
|----|-------|----------------|---------------------|
| 10 | Edit form renders the seven settings inputs and saves them under the settings keys, with no `brain_setting` / `mode` in the body | Stage 2 (form + `settingsBody`) | Betty's frontend component test (`test_AdminAgentPrompts.test.tsx`) |
| 10 | `rg -n "brain_setting\|AGENT_MODES\|Deterministic\|Creative" src/ui/frontend/src/pages/AdminAgentPrompts.tsx` returns nothing | Stage 2 Done-when | — (closes here) |
| 5 | `rg … src/` returns nothing | Stage 1 Done-when `rg` over `api_admin.py`, and Stage 2's over `AdminAgentPrompts.tsx` | AST-1956 (`agent.py`, `llm_compat.py`, `anthropic.py`) |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Agent create/update take the settings and stop requiring `brain_setting` / `mode`. `GET /agents/models` drops brain sizes. `_enrich_tasks` and `_resolve_adhoc` use `resolve_agent_settings`. | ui (api) |
| `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | Settings inputs replace brain-size/mode controls. List columns show the settings. Model types drop brain sizes. | ui (frontend) |

## API contract (used by both stages)

The settings keys, their types and what "empty" means are AST-1955's **Settings contract** (`docs/features/agent/ast-1955-plain-agent-settings-and-per-sku-direct-models.md`). Its one-line summary:

| Key | JSON type when set | Empty |
|-----|--------------------|-------|
| `quantization`, `reasoning_effort`, `provider_sort` | string | `null` |
| `temperature` | number | `null` |
| `provider_allow_fallbacks` | boolean | `null` (new rows default `true`) |
| `provider_only`, `provider_ignore` | array of strings | `null` |

The routes add no checks of their own. `database.save_agent` / `database.update_agent` raise `ValueError` on a wrong type, and the routes already map `ValueError` to 400 `{"error": str(e)}`. `GET /agents`, `GET /agents/<id>` and the `PUT` response already return the settings (decoded lists, bool fallbacks) through `database._expose_agent_public` (AST-1955), so they need no change.

## Stage 1: Admin API — settings in, brain sizes out, new resolver

**Done when:** `python3 -m py_compile src/ui/api/api_admin.py` succeeds, and `rg -n 'brain_setting|brain_sizes|resolve_model_brain|AGENT_MODE|"mode"|\bmode\b *=' src/ui/api/api_admin.py` returns nothing. (The pattern skips the unrelated "AUTO mode" / "batch mode" comments and `auto_mode=` / `batch_call_mode` names.)

All edits are in `src/ui/api/api_admin.py`. On this sub alone the module can't be imported: `src/core/agent.py` still imports `resolve_model_brain` until AST-1956 lands (parent **Sequencing**). The Done-when therefore uses `py_compile` and `rg`, not an import.

1. **Imports.**
   - In the `from src.data.database import (` block (lines ~14–23), add `AGENT_SETTING_COLUMNS,` as the last name.
   - In the `from src.utils.config import (` block (~line 57), replace `resolve_model_brain,` with `resolve_agent_settings,`.

2. **New helper**, directly after `_api_completed` (~line 136):
   ```python
   def _agent_settings_from_body(body: Dict[str, Any]) -> Dict[str, Any]:
       """The plain agent settings present in a request body, passed as-is (AST-1957).
       Type checks live in the data layer (save_agent / update_agent raise ValueError → 400)."""
       return {k: body[k] for k in AGENT_SETTING_COLUMNS if k in body}
   ```

3. **`list_agents` (~line 141).** Replace the comment with:
   `# database._expose_agent_public decodes the settings and exposes model_id + SKU (AST-1878, AST-1955).`

4. **`list_models` (~lines 192–212).** Replace the whole function body and docstring with:
   ```python
   def list_models():
       """Model catalog for Manage Agents (AST-1880, AST-1957): label, server and the default output budget
       used when an agent leaves max_tokens empty. jsonify sorts keys, so `order` carries catalog order for the UI."""
       return jsonify({
           mid: {
               "order": i,
               "label": m["label"],
               "server_id": m["server"],
               "server_label": get_llm_server(m["server"])["label"],
               "default_max_tokens": m["default_max_tokens"],
           }
           for i, (mid, m) in enumerate(LLM_MODEL_CONFIG.items())
       })
   ```
   The decorators `@admin_bp.route("/agents/models")` / `@require_admin` are unchanged. The response has no `brain_sizes` key.

5. **`create_agent` (~lines 224–250).**
   - Delete the `brain_setting = …`, `mode = body.get("mode")` and `mode = mode.strip() …` lines.
   - Change the required check to:
     ```python
     if not agent_id or not model_id:
         return jsonify({"error": "agent_id and model_id are required"}), 400
     ```
   - Replace the comment above `database.save_agent(` with `# Data layer checks model_id against the catalog and type-checks the settings (AST-1955).`
   - Replace the `save_agent` call with:
     ```python
     database.save_agent(
         agent_id,
         body.get("content", ""),
         model_id=model_id,
         max_tokens=body.get("max_tokens"),
         **_agent_settings_from_body(body),
     )
     ```
   - The 409 duplicate check, the `except ValueError` → 400, the `_api_completed(None, "/api/admin/agents", "POST", 201)` line and the `{"created": agent_id}` 201 response are unchanged.

   ⚠️ **Decision (create response):** the 201 body stays `{"created": agent_id}`. "Take and return the settings" is met by `GET /agents/<id>` and the `PUT` response, which return the full row with settings. The form ignores the create body and reloads the list. Changing the shape would break an existing contract for no caller.

6. **`update_agent` (~lines 253–278).**
   - Delete the `mode = body.get("mode")` line and its `mode is required` 400 block.
   - Replace the `kwargs` comprehension with:
     ```python
     kwargs = {
         k: (body[k].strip() if k == "model_id" and isinstance(body[k], str) else body[k])
         for k in ("content", "model_id", "max_tokens", *AGENT_SETTING_COLUMNS)
         if k in body
     }
     ```
   - Replace the comment above `database.update_agent(` with `# update_agent checks model_id and type-checks the settings before its UPDATE (AST-1955).`
   - The 404 check, the `No updatable fields provided` 400, the `except ValueError` → 400, the `_api_completed(None, f"/api/admin/agents/{agent_id}", "PUT", 200)` line and the row response are unchanged.

   ⚠️ **Decision (retired keys):** "no longer require or accept `brain_setting` / `mode`" is met by not reading them. Create reads only named keys, and update builds `kwargs` from an allow-list, so a stale client that sends either key has it ignored, the same as any other unknown key today. There is no special 400 for them, because code that names the retired keys would fail AC 5's `rg` over `src/`.

   ⚠️ **Decision (strings as sent):** settings strings are not stripped in the route. "Type checks only" means the value is stored as sent, and stripping a non-string would raise. The form trims before sending (Stage 2 step 4). `model_id` keeps today's strip.

7. **`_enrich_tasks` (~lines 383–404 and the row dict ~465).**
   - Replace the comment `# Agent model + brain size → catalog SKU and pricing row for cache threshold math (AST-1880).` with `# Agent model + settings → catalog SKU and pricing row for cache threshold math (AST-1880, AST-1957).`
   - Delete `brain_setting_eff = ""` and the `brain_setting_eff = (agent.get("brain_setting") or "").strip()` line.
   - Replace the `route = resolve_model_brain(…)` call (3 lines) with:
     `route = resolve_agent_settings((agent.get("model_id") or "").strip(), agent)`
   - The `except ValueError` warning block is unchanged.
   - Replace the comment `# Cache threshold (model_cfg is the catalog pricing row for the agent's model + brain size)` with `# Cache threshold (model_cfg is the catalog pricing row for the agent's model)`.
   - In `rows.append({…})`, delete the `"brain_setting":        brain_setting_eff,` line. The other keys are unchanged.

   ⚠️ **Decision:** `_enrich_tasks` is not literally an "adhoc/workbench resolver", but it is the third caller of `resolve_model_brain` in this file, and the kind of change is the same one Scope gives the other two (switch to the new resolver). The function is gone after AST-1955, so this call must move, and AC 5's `rg` forbids `brain_setting` anywhere in `src/`. Dropping the row's `brain_setting` key is safe: `rg -n brain_setting src/ui/frontend/src` shows only `AdminAgentPrompts.tsx` (Stage 2), so Manage Tasks never reads it.

8. **`_resolve_adhoc` (~lines 1547–1558).**
   - Replace the comment `# Agent model + brain size → server, SKU and tier row (AST-1880); no global provider.` with `# Agent model + plain settings → server, SKU and tier (AST-1880, AST-1957); tier carries temperature, effort and provider.`
   - Replace the `route = resolve_model_brain(…)` call (5 lines) with:
     `route = resolve_agent_settings((agent.get("model_id") or "").strip(), agent)`
   - Everything after it is unchanged: `tier = route["tier"]`, `temperature = tier["temperature"]`, the `max_tokens` default, and the returned dict (`model_code`, `server_id`, `tier`, `temperature`, `max_tokens`, …).

   ⚠️ **Decision (workbench call unchanged):** `adhoc_test` keeps passing `model_code`, `server_id`, `tier`, `temperature` and `max_tokens` to `run_adhoc_workbench_test` exactly as today. `tier` now carries `reasoning_effort` and `provider` (AST-1955 resolver), so AST-1956 can send them from inside `run_adhoc` with no change to this call. No new keyword is passed from this file.

9. **Logging (`stat.logging.info.api`).** No logger call is added, removed or changed. Create (`POST 201`) and update (`PUT 200`) keep their single `_api_completed` line at the route. `GET /agents/models` is an idempotent read and logs nothing. The `_enrich_tasks` warning is a display-row degrade and is unchanged.

10. Run `python3 -m py_compile src/ui/api/api_admin.py` and `ruff check src/ui/api/api_admin.py` (if `ruff` is not on PATH, `python3 -m pyflakes src/ui/api/api_admin.py`), then the **Done when** `rg`.

## Stage 2: Manage Agents form and list

**Done when:** `rg -n "brain_setting|brain_sizes|BrainSize|AGENT_MODES|Deterministic|Creative|\bmode\b" src/ui/frontend/src/pages/AdminAgentPrompts.tsx` returns nothing, and from `src/ui/frontend/`, `npx tsc -b` and `npx eslint src/pages/AdminAgentPrompts.tsx` both exit 0.

All edits are in `src/ui/frontend/src/pages/AdminAgentPrompts.tsx`. If `src/ui/frontend/node_modules` is missing, run `npm ci` in `src/ui/frontend/` first. `node_modules` is gitignored, so nothing from it is committed.

1. **Model types (lines ~13–26).** Replace the `BrainSizeRow` / `ModelRow` block and its doc comment with:
   ```tsx
   /** GET /api/admin/agents/models — keyed by model id (AST-1880, AST-1957). JSON keys arrive sorted, so `order`
    *  carries catalog order; default_max_tokens is what a call uses when the agent leaves max_tokens empty. */
   interface ModelRow {
     order: number
     label: string
     server_id: string
     server_label: string
     default_max_tokens: number
   }
   ```
   `ModelCatalog` and `byOrder` are unchanged.

2. **Remove `AGENT_MODES`** and its comment (lines ~33–34).

3. **`Agent` interface (~36–47).** Replace `brain_setting?: string | null` and `mode?: string | null` with:
   ```tsx
   quantization?: string | null
   temperature?: number | null
   reasoning_effort?: string | null
   provider_allow_fallbacks?: boolean | null
   provider_only?: string[] | null
   provider_ignore?: string[] | null
   provider_sort?: string | null
   ```

4. **Settings form helpers.** Directly after the `Agent` interface, add:
   ```tsx
   /** Plain agent settings as the form edits them (AST-1957): text inputs hold strings, lists are comma-separated. */
   interface SettingsForm {
     quantization: string
     temperature: string
     reasoning_effort: string
     provider_allow_fallbacks: boolean
     provider_only: string
     provider_ignore: string
     provider_sort: string
   }

   // New agents start with fallbacks on (the data layer's new-row default) and everything else empty.
   const EMPTY_SETTINGS: SettingsForm = {
     quantization: "", temperature: "", reasoning_effort: "", provider_allow_fallbacks: true,
     provider_only: "", provider_ignore: "", provider_sort: "",
   }

   function settingsFromAgent(a: Agent): SettingsForm {
     return {
       quantization:             a.quantization ?? "",
       temperature:              a.temperature != null ? String(a.temperature) : "",
       reasoning_effort:         a.reasoning_effort ?? "",
       // Stored null reads as the default (true); saving writes the checkbox value explicitly.
       provider_allow_fallbacks: a.provider_allow_fallbacks ?? true,
       provider_only:            (a.provider_only ?? []).join(", "),
       provider_ignore:          (a.provider_ignore ?? []).join(", "),
       provider_sort:            a.provider_sort ?? "",
     }
   }

   /** Comma-separated slugs → list; blank → null (not sent on the wire). */
   function slugList(s: string): string[] | null {
     const v = s.split(",").map(x => x.trim()).filter(Boolean)
     return v.length ? v : null
   }

   /** Form → request body under the settings keys. Every key is always sent, so clearing an input clears the setting. */
   function settingsBody(f: SettingsForm): Record<string, unknown> {
     return {
       quantization:             f.quantization.trim() || null,
       temperature:              f.temperature.trim() === "" ? null : Number(f.temperature),
       reasoning_effort:         f.reasoning_effort.trim() || null,
       provider_allow_fallbacks: f.provider_allow_fallbacks,
       provider_only:            slugList(f.provider_only),
       provider_ignore:          slugList(f.provider_ignore),
       provider_sort:            f.provider_sort.trim() || null,
     }
   }
   ```
   ⚠️ **Decision:** both forms send all seven keys on every save. `PUT` is a partial update in which a sent `null` clears a setting (`database.update_agent`), so sending everything is what lets Susan blank out a value. No vocabulary, range or per-model check (Susan: "code it loosely"). `temperature` is sent as `Number(...)`; the `type="number"` input keeps non-numeric text out.

5. **`LIST_COLUMNS` (~49–58).** Replace the `brain_setting` and `mode` entries with these seven, in this order, between `model_label` and `max_tokens`:
   ```tsx
   { key: "quantization",             label: "Quant",     sortable: true },
   { key: "temperature",              label: "Temp",      sortable: true },
   { key: "reasoning_effort",         label: "Effort",    sortable: true },
   { key: "provider_allow_fallbacks", label: "Fallbacks", sortable: true },
   { key: "provider_only",            label: "Only",      sortable: true },
   { key: "provider_ignore",          label: "Ignore",    sortable: true },
   { key: "provider_sort",            label: "Sort",      sortable: true },
   ```

6. **Delete `tierCell`** (~75–79).

7. **Component state (~90–106).**
   - Edit: delete `editBrainSetting` and `editMode`. Add `const [editSettings, setEditSettings] = useState<SettingsForm>(EMPTY_SETTINGS)`.
   - Add: delete `addBrainSetting` and `addMode`. Add `const [addSettings, setAddSettings] = useState<SettingsForm>(EMPTY_SETTINGS)`.

8. **Delete the size helpers:** `applyTierDefaults`, `sizeForModel`, `onAddTierChange`, `onEditTierChange`, `onAddModelChange` and `onEditModelChange` (~135–173), with their comments. The model select calls `setAddModelId` / `setEditModelId` directly (step 13).

   ⚠️ **Decision:** nothing pre-fills `max_tokens` (Scope: "Removed: … the size pre-fill"). An empty `max_tokens` means the model default (Functional scope 5), so the input shows that default as its placeholder (step 13) and stays empty unless Susan types an override.

9. **`openEdit` (~175–190).** Delete the `setEditBrainSetting(…)` (3 lines) and `setEditMode(…)` calls. After `setEditModelId(…)`, add `setEditSettings(settingsFromAgent(full))`.

10. **`handleEditSave` (~192–219).** Replace the `body` construction (the object literal plus the `model_id` and `brain_setting` `if` blocks) with:
    ```tsx
    const body: Record<string, unknown> = {
      content:     editContent,
      max_tokens:  editMaxTok ? parseInt(editMaxTok) : undefined,
      ...settingsBody(editSettings),
    }
    if (editModelId)
      body.model_id = editModelId
    ```
    The fetch, toast, refresh and `loadAll` calls are unchanged.

11. **`handleAddSave` (~221–252).** Same change, using `addMaxTok` / `addSettings` / `addModelId` (keep `agent_id: id` as the first key). In the success reset line, replace `setAddModelId(""); setAddBrainSetting("")` and `setAddMode(""); setAddMaxTok("")` with `setAddModelId(""); setAddSettings(EMPTY_SETTINGS); setAddMaxTok("")`.

12. **`renderedAgents` and `openAddModal` (~292–307).**
    - Replace the `brain_setting: tierCell(a),` and `mode: a.mode || "—",` lines with:
      ```tsx
      quantization:             a.quantization || "—",
      temperature:              a.temperature ?? "—",
      reasoning_effort:         a.reasoning_effort || "—",
      provider_allow_fallbacks: a.provider_allow_fallbacks == null ? "—" : a.provider_allow_fallbacks ? "yes" : "no",
      provider_only:            a.provider_only?.length ? a.provider_only.join(", ") : "—",
      provider_ignore:          a.provider_ignore?.length ? a.provider_ignore.join(", ") : "—",
      provider_sort:            a.provider_sort || "—",
      ```
      If `tsc` rejects the mixed types against `Agent`, type the mapped rows as `Agent` via the existing `[key: string]: unknown` index signature (e.g. `const renderedAgents: Agent[] = agents.map(...)`). Do not change `ListPage`.
    - `openAddModal` becomes:
      ```tsx
      function openAddModal() {
        setAddModelId(byOrder(models)[0] ?? "")
        setAddSettings(EMPTY_SETTINGS)
        setAddMaxTok("")
        setAddOpen(true)
      }
      ```

13. **Replace `BrainSettingFields`** (the component and its doc comment, ~474–543) with `AgentSettingsFields`:
    ```tsx
    /** Model select, max_tokens override and the agent's plain call settings, sent as stored (AST-1880, AST-1957). */
    function AgentSettingsFields({
      models,
      modelId,
      onModelChange,
      maxTok,
      onMaxTokChange,
      settings,
      onSettingsChange,
    }: {
      models: ModelCatalog
      modelId: string
      onModelChange: (v: string) => void
      maxTok: string
      onMaxTokChange: (v: string) => void
      settings: SettingsForm
      onSettingsChange: (s: SettingsForm) => void
    }) {
      const noModelMatch = !!modelId && !models[modelId]
      const defaultMax = models[modelId]?.default_max_tokens
      // One text input per string setting; key is the SettingsForm field it edits.
      const text = (key: keyof SettingsForm, label: string, placeholder: string) => (
        <div className="dep-field" style={{ flex: 1 }}>
          <label className="dep-field-label">{label}</label>
          <input
            className="dep-input"
            type="text"
            value={settings[key] as string}
            placeholder={placeholder}
            onChange={e => onSettingsChange({ ...settings, [key]: e.target.value })}
          />
        </div>
      )
      return (
        <>
          <div className="dep-field">
            <label className="dep-field-label">Model</label>
            <select className="dep-input" value={modelId} onChange={e => onModelChange(e.target.value)}>
              {noModelMatch ? <option value={modelId}>— (unknown model) —</option> : null}
              {modelId === "" ? <option value="">— choose model —</option> : null}
              {byOrder(models).map(id => (
                <option key={id} value={id}>{models[id].label}</option>
              ))}
            </select>
          </div>
          <div style={{ display: "flex", gap: 12 }}>
            <div className="dep-field" style={{ flex: 1 }}>
              <label className="dep-field-label">Max Tokens</label>
              <input
                className="dep-input"
                type="number" step="1" min="1"
                value={maxTok}
                placeholder={defaultMax != null ? `default ${defaultMax}` : ""}
                onChange={e => onMaxTokChange(e.target.value)}
              />
            </div>
            <div className="dep-field" style={{ flex: 1 }}>
              <label className="dep-field-label">Temperature</label>
              <input
                className="dep-input"
                type="number" step="any"
                value={settings.temperature}
                placeholder="not sent"
                onChange={e => onSettingsChange({ ...settings, temperature: e.target.value })}
              />
            </div>
            {text("reasoning_effort", "Effort", "e.g. high, none")}
          </div>
          <div style={{ display: "flex", gap: 12 }}>
            {text("quantization", "Quantization", "e.g. bf16")}
            {text("provider_sort", "Provider sort", "e.g. price")}
            <div className="dep-field" style={{ flex: 1 }}>
              <label className="dep-field-label">
                <input
                  type="checkbox"
                  checked={settings.provider_allow_fallbacks}
                  onChange={e => onSettingsChange({ ...settings, provider_allow_fallbacks: e.target.checked })}
                />{" "}
                Allow provider fallbacks
              </label>
            </div>
          </div>
          <div style={{ display: "flex", gap: 12 }}>
            {text("provider_only", "Provider only", "comma-separated slugs")}
            {text("provider_ignore", "Provider ignore", "comma-separated slugs")}
          </div>
        </>
      )
    }
    ```

14. **Modal call sites (~354–364 edit, ~403–413 add).** Replace each `<BrainSettingFields … />` with:
    ```tsx
    <AgentSettingsFields
      models={models}
      modelId={editModelId}
      onModelChange={setEditModelId}
      maxTok={editMaxTok}
      onMaxTokChange={setEditMaxTok}
      settings={editSettings}
      onSettingsChange={setEditSettings}
    />
    ```
    and the add twin, with `addModelId` / `setAddModelId` / `addMaxTok` / `setAddMaxTok` / `addSettings` / `setAddSettings`.

15. Run `npx tsc -b` and `npx eslint src/pages/AdminAgentPrompts.tsx` from `src/ui/frontend/`, then the **Done when** `rg`. React does not write `app_log` (`stat.logging.info.api` Notes), so no logging is involved in this stage.

## Sequencing risk (for Betty / Chuckles — not a step)

`src/ui/api/api_admin.py` imports `src.core.agent`, which imports `resolve_model_brain` until AST-1956 lands on ftr. On this sub alone, `tests/component/ui/api/test_api_admin.py` therefore fails at collection, the same way AST-1955's `tests/component/core/` does (see AST-1955 plan **Sequencing risk**). The frontend component test (`test_AdminAgentPrompts.test.tsx`) is not affected. The API manifest needs to run after AST-1956 is on ftr, or on the ftr rollup.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

**Ticket:** AST-1957  
**Overall:** APPROVED  
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51  
**Publish ref:** `sub/AST-1953/AST-1957-manage-agents-settings` @ `fb90852e7322b5b0bb801a9e7882d25dd9e16226`

### Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.info.api | A | | |

### Traceability

10 → Stage 2 (`AgentSettingsFields`, `settingsBody`, list columns, Done-when `rg`; form AC closes with Betty `test_AdminAgentPrompts.test.tsx` per **AC boundaries**) · 5 (parent) → **AC boundaries** + Stage 1/2 file-scoped `rg` (remainder AST-1956 on ftr)

### Findings

#### acceptable

- **Location:** Plan structure — no `## Self-assessment`
- **Finding:** Estimate confirm plus staged done-when and **Sequencing risk** carry complexity.
- **Recommendation:** None blocking.

- **Location:** **Sequencing risk**
- **Finding:** `test_api_admin.py` collection blocked until AST-1956 merges `resolve_model_brain` removal; frontend test path unaffected. Matches parent sequencing and AST-1955 precedent.
- **Recommendation:** Betty manifest ordering only; no plan revision.

context_tokens≈58000

## Review

- **Branch:** `sub/AST-1953/AST-1957-manage-agents-settings`
- **Build commits:** `5d1e79562` (Stage 1 admin API) · `15ba5277d` (Stage 2 Manage Agents form and list)
- **Build notes:** both stages executed as written, and each stage's Done-when checks passed (`py_compile` and `rg` for Stage 1; `tsc -b`, `eslint` and `rg` for Stage 2). One point the plan left open: in Stage 2 step 12, `tsc` rejected the display rows (grid cells are strings), as the plan anticipated. The plan's example annotation (`const renderedAgents: Agent[]`) does not compile, so the rows are cast per row with `as unknown as Agent`, following the existing `as unknown as CsvRow` in `AdminCostReconciliation.tsx`. `ListPage` is unchanged. Ruff on `api_admin.py` adds only two `UP006` hints for the helper's `Dict[str, Any]`, which matches the file's existing `Dict` annotations and the plan's code. `tests/component/ui/api/test_api_admin.py` still can't import on this sub until AST-1956 lands (see **Sequencing risk**).

## Radia review

**Ticket:** AST-1957  
**Publish ref:** `9a514b8991db12f51be0beb8754124b62e2e30fe` (`origin/sub/AST-1953/AST-1957-manage-agents-settings`)  
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51  
**Overall:** CLEAN  

### Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.info.api | A | | |

### Column diff vs plan stage

(aligned) — Joan validate: `stat.logging.info.api` A.

### Frame diff

(none)

### Findings

#### fix-now

(none)

#### discuss

(none)

#### advisory

- **Location:** `git diff origin/dev...origin/sub/AST-1953/AST-1957-manage-agents-settings` (stacked publish ref)
- **Finding:** Three-dot diff vs `origin/dev` includes AST-1955 product paths (`src/utils/config.py`, `src/data/database.py`, seed, fixture) and AST-1958 plan doc, because this sub stacks on AST-1955 (not on `dev` yet). AST-1957 commits are confined to `api_admin.py`, `AdminAgentPrompts.tsx`, and Betty tests/bible for those surfaces.
- **Recommendation:** Treat as sibling/stack carry when reading the diff; score plan fidelity on the two in-scope product files only.

- **Location:** `AdminAgentPrompts.tsx` list rows / `ListPage` typing (build notes)
- **Finding:** Plan’s `renderedAgents: Agent[]` example does not type-check; tip uses per-row `as unknown as Agent` (same pattern as `AdminCostReconciliation.tsx`). Behavior matches plan; typing is a local compile workaround.
- **Recommendation:** Optional one-line note in plan **Review** for the next doc publish; no product change required.

- **Location:** **Sequencing risk** / bible § AST-1957
- **Finding:** `tests/component/ui/api/test_api_admin.py` still fails collection until AST-1956 removes `resolve_model_brain` from `src/core/agent.py` (import chain). Frontend `test_AdminAgentPrompts.test.tsx` is the AC 10 closure path on this sub.
- **Recommendation:** Betty/`test-child` manifest on ftr rollup after AST-1956; no change on AST-1957 tip.

- **Location:** Estimate confirm **3**
- **Finding:** Two-stage API + frontend surface plus manifests fits confirmed points despite stacked diff size.
- **Recommendation:** None.

### What's solid

- Stage 1 matches plan: `_agent_settings_from_body`, create/update wiring, `list_models` drops `brain_sizes`, `_enrich_tasks` / `_resolve_adhoc` use `resolve_agent_settings`, `brain_setting` dropped from enrichment row; Done-when `rg` clean on `api_admin.py`.
- Stage 2 matches plan: `AgentSettingsFields`, `settingsBody` / `settingsFromAgent`, list columns for seven settings, AC `rg` clean on `AdminAgentPrompts.tsx`; create/update still use `_api_completed` only (no new API `logger` lines).
- `stat.logging.info.api`: no added/removed/changed route completion logging in the API diff; idempotent `GET /agents/models` remains silent.
- Boundaries hold: no `agent.py` / `llm_compat.py` in this ticket’s product delta; parent AC 5 remainder still deferred to AST-1956 per **AC boundaries**.

### Recommended actions (downstream — not for Radia)

- Chuckles: append artifact, `docs(AST-1957): Radia review — clean`, push publish ref, post slim upshot `--as radia`, **Review Posted** → PROCEED to **User Testing** (with AST-1955 already UT, merge-child/ftr ordering per parent workflow).

context_tokens≈52000
