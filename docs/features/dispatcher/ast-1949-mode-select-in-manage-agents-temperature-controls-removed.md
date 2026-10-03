# AST-1949 — Mode select in Manage Agents; temperature controls removed

- **Parent:** [AST-1946 — Support "Big" brain OpenRouter models](https://linear.app/astralcareermatch/issue/AST-1946)
- **Ticket:** [AST-1949](https://linear.app/astralcareermatch/issue/AST-1949)
- **Publish ref:** `origin/sub/AST-1946/AST-1949-manage-agents-mode`
- **Canon Scope:** none (ticket § Citations: frontend-only, no active pattern or statute governs this page).
- **Blocked by:** [AST-1948](https://linear.app/astralcareermatch/issue/AST-1948), already on this sub via `origin/ftr/AST-1946-big-brain-openrouter`. It gives the backend contract this page must follow:
  - `POST /api/admin/agents` requires `agent_id`, `model_id`, `brain_setting` and `mode` (400 otherwise). `PUT /api/admin/agents/<id>` requires `mode` on every call (400 `"mode is required"`). Neither accepts `temperature`.
  - `GET /api/admin/agents` and `GET /api/admin/agents/<id>` return `mode` (`"Deterministic"` | `"Creative"`, or `null` on rows the AST-1950 migration has not touched yet). They no longer return `temperature` or `model_code`.
  - `GET /api/admin/agents/models` brain-size rows carry only `order` and `default_max_tokens`. `default_temperature` is gone.

Manage Agents today still shows a temperature input, a Temp column, and pre-fills temperature from `default_temperature` on size change. It also omits `mode`, so every save now fails AST-1948's required-mode check. This ticket adds a required Mode select (Deterministic / Creative) to the add/edit form and sends it as `mode`. It swaps the list's Temp column for a Mode column. It removes the temperature input and the temperature half of the size pre-fill. The `Agent` / model types drop `temperature`, `model_code` and `default_temperature`. No backend file is touched.

## Scope gate

Every row in **Files Changed** is named in this ticket's `## Scope`, and every change below is the kind Scope describes for that file:

- `src/ui/frontend/src/pages/AdminAgentPrompts.tsx`: the add/edit form gains a Mode select sent as `mode`, and drops the temperature input and the temperature half of the size pre-fill. The list swaps Temp for Mode. The `Agent` / `BrainSizeRow` types drop `temperature`, `model_code` and `default_temperature`, and `Agent` gains `mode`, which is the field the new select and column read.
- `tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx` and `docs/test-bible/frontend/pages.md` are Betty's in `qa-child`. The engineer does not touch them.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | Types: `default_temperature`, `model_code`, `temperature` out, `mode` in. New `AGENT_MODES` constant. Temp column → Mode column. `editTemp`/`addTemp` state → `editMode`/`addMode`. `applyTierDefaults` pre-fills max tokens only. Save bodies send `mode`, not `temperature`. `BrainSettingFields` swaps its Temperature input for a Mode select. | ui |

No other file is touched.

## Stage 1: Mode replaces temperature on Manage Agents

**Done when:** `rg -n "temperature" src/ui/frontend/src/pages/AdminAgentPrompts.tsx` returns nothing. `npm run build` and `npm run lint` in `src/ui/frontend/` pass. In the browser, the list shows a Mode column and no Temp column. Add/Edit show a Mode select with exactly Deterministic / Creative where Temperature used to be, and saving sends `mode` and no `temperature`.

All edits are in `src/ui/frontend/src/pages/AdminAgentPrompts.tsx`.

1. **`BrainSizeRow`:** delete the line `default_temperature: number`. The interface keeps `order` and `default_max_tokens`.

2. **New constant**, placed directly after the `byOrder` function and before `interface Agent`:

   ```ts
   /** Agent mode choices; must match AGENT_MODES in src/utils/config.py (AST-1947). The models endpoint does not send them. */
   const AGENT_MODES = ["Deterministic", "Creative"] as const
   ```

   ⚠️ **Decision:** The two mode names are hardcoded in the page. No route returns `AGENT_MODES`, and this ticket "does **not** touch the backend". Adding them to `/agents/models` would be backend scope the ticket excludes. AC 12's mode-literal grep covers only `agent.py`, `api_admin.py` and `database.py`, so a literal here is allowed.

3. **`interface Agent`:** delete `model_code?: string` and `temperature?: number`. Add `mode?: string | null` on the line after `brain_setting?: string | null`.

4. **`LIST_COLUMNS`:** replace `{ key: "temperature",    label: "Temp",          sortable: true },` with `{ key: "mode",           label: "Mode",          sortable: true },`, in the same position (after Brain setting, before Max Tok).

5. **Edit state:** rename `const [editTemp, setEditTemp] = useState("")` to `const [editMode, setEditMode] = useState("")`, keeping the column alignment of the surrounding lines.

6. **Add state:** rename `const [addTemp, setAddTemp] = useState("")` to `const [addMode, setAddMode] = useState("")`, keeping alignment.

7. **`applyTierDefaults`** becomes max-tokens only. Replace the function (and keep its leading comment, changing "fill defaults" to "fill the max-tokens default") with:

   ```ts
   // When size changes in add/edit, fill the max-tokens default from that model's row for that size
   function applyTierDefaults(modelId: string, setting: string, setMaxTok: (m: string) => void) {
     const row = models[modelId]?.brain_sizes[setting]
     if (!row)
       return
     setMaxTok(String(row.default_max_tokens))
   }
   ```

8. **Update every `applyTierDefaults` call site** to pass the max-tokens setter directly:
   - `onAddTierChange`: `applyTierDefaults(addModelId, setting, setAddMaxTok)`
   - `onEditTierChange`: `applyTierDefaults(editModelId, setting, setEditMaxTok)`
   - `onAddModelChange`: `applyTierDefaults(modelId, size, setAddMaxTok)`
   - `onEditModelChange`: `applyTierDefaults(modelId, size, setEditMaxTok)`
   - `openAddModal`: `applyTierDefaults(firstModel, firstSize, setAddMaxTok)`

   ⚠️ **Decision:** Changing the mode does **not** re-fill max tokens. Scope only removes the temperature half of the size pre-fill. It does not tie max tokens to mode. The backend resolver already applies the mode's OpenRouter cap when the row's `max_tokens` is blank.

9. **`openEdit`:** replace `setEditTemp(full.temperature != null ? String(full.temperature) : "")` with:

   ```ts
   setEditMode(typeof full.mode === "string" ? full.mode : "")
   ```

10. **`handleEditSave`:** in the `body` literal, replace the `temperature: editTemp ? parseFloat(editTemp) : undefined,` line with `mode:        editMode,` (aligned with `content:` / `max_tokens:`). `mode` is always sent because AST-1948's PUT requires it on every call.

11. **`handleAddSave`:** in the `body` literal, replace the `temperature: addTemp ? parseFloat(addTemp) : undefined,` line with `mode:        addMode,` (aligned).

12. **`handleAddSave` success reset:** replace `setAddTemp(""); setAddMaxTok("")` with `setAddMode(""); setAddMaxTok("")`.

13. **`openAddModal`:** after the `applyTierDefaults(...)` line from step 8, add `setAddMode(AGENT_MODES[0])`.

    ⚠️ **Decision:** Add pre-selects the first mode (Deterministic), the same way `openAddModal` already pre-selects the first model and its first size. "Required" is enforced by the select always holding a value on Add, and by the server's 400 on Edit. No client-side guard is added. An Edit on a not-yet-migrated row (`mode: null`) shows the `— choose mode —` placeholder (step 16). Saving without picking one hits AST-1948's 400 `"mode is required"`, which the existing `readApiError` → toast path already shows. Considered and rejected: blank Add plus a `"Mode is required"` toast guard in both save handlers. That adds two guards for a case the server already rejects, and Add would behave differently from Model / Brain size.

14. **`BrainSettingFields` call sites:** in both the Edit and Add modals, replace the `temp={…}` prop with `mode={editMode}` / `mode={addMode}`, and replace `onTempChange={…}` with `onModeChange={setEditMode}` / `onModeChange={setAddMode}`.

15. **`renderedAgents`:** add `mode: a.mode || "—",` after the `brain_setting: tierCell(a),` line, so unmigrated rows show an em dash like an empty brain setting does.

16. **`BrainSettingFields`** component:
    - Docstring becomes: `/** Model select, then that model's own brain sizes, the agent mode and max_tokens (catalog-driven; AST-1880, AST-1949) */`
    - Props: rename `temp` → `mode` (type `string`) and `onTempChange` → `onModeChange` (type `(v: string) => void`), in both the destructuring list and the type literal, in the same positions.
    - Replace the Temperature `dep-field` block (the `<div className="dep-field" style={{ flex: 1 }}>` holding `<label className="dep-field-label">Temperature</label>` and its number `<input>`) with:

      ```tsx
      <div className="dep-field" style={{ flex: 1 }}>
        <label className="dep-field-label">Mode</label>
        <select className="dep-input" value={mode} onChange={e => onModeChange(e.target.value)}>
          {mode === "" ? <option value="">— choose mode —</option> : null}
          {AGENT_MODES.map(m => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>
      ```

      The Max Tokens field next to it, in the same flex row, is unchanged. The label text is exactly `Mode`, because the page test finds fields by `dep-field-label` text.

17. **Verify:** from the repo root run `rg -n "temperature|default_temperature|model_code|editTemp|addTemp|onTempChange" src/ui/frontend/src/pages/AdminAgentPrompts.tsx`, which must return nothing. Then in `src/ui/frontend/` run `npm run build` (tsc + vite) and `npm run lint`, and both must pass. Commit: `code(AST-1949): Manage Agents — Mode select and column; temperature controls removed`.

## Tests expected to move (Betty, `qa-child`)

The engineer does not edit these. Listed so Betty's manifest lines up with the change:

- `tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx`: fixtures still carry `default_temperature`, `model_code` and `temperature`. The AST-1880 Add test asserts `field("Temperature")` values and a POST body with `temperature: 0.6`. Those assertions become `field("Mode")` (Add defaults to `Deterministic`, options exactly `["Deterministic", "Creative"]`) and a body with `mode` and no `temperature`. The Edit test's PUT body gains `mode`. AC 10 adds: no Temperature field for any model, and a Mode column with no Temp column in the list header.
- `docs/test-bible/frontend/pages.md`: the Manage Agents rows follow the same change.

## Estimate

Confirm Chuckles estimate: 2 — agree
