# AST-1452 — Ad Hoc import picker and Load

- **Linear:** [AST-1452](https://linear.app/astralcareermatch/issue/AST-1452)
- **Parent:** [AST-1439](https://linear.app/astralcareermatch/issue/AST-1439)
- **Publish ref:** `sub/AST-1439/AST-1452-ad-hoc-import-picker-and-load`

Agent Ad Hoc can fetch catalog prompts by task key, but it cannot pick a stored `agent_data` run and copy it onto the workbench. This ticket owns **picker chrome and Load only**: list UI (sibling #1’s JSON), Load into the seven editors (TASK → User; missing slots empty), RESPONSE display via existing `BatchAgentDataPanes`, one leading `adhoc-` strip on the workbench task key without catalog fetch-from-task, `entity_id` restore, and dirty-editor replace confirm matching fetch-from-task. Does **not** own `GET /api/admin/adhoc/runs` or Test persist prefix (AST-1451). Does **not** change Save As, Preview modal chrome, or production `do_task`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | Import list table, Load, editor mapping, skip catalog fetch, entity lock, panes for imported batch | ui |

Do **not** edit: `src/data/database.py`, `src/core/agent.py`, `src/ui/api/**` (list + load GET are AST-1451 / existing `GET /api/agent_data/<batch_id>`), `src/utils/config.py`, `src/ui/frontend/src/components/BatchAgentDataModal.tsx` (`BatchAgentDataPanes` is reused as-is), Save As / Preview modal markup (except Preview/Test JSON `entity_id` / `entity_ids` when the import entity lock is set — Stage 2), `tests/`, bible, Manage Tasks, production `do_task`.

**Sibling contract (AST-1451 — do not reimplement):**

- List: `GET /api/admin/adhoc/runs` → JSON **array** of `{batch_id, created_at, entity_id, task_key}`, newest first, no cap.
- Load body: `GET /api/agent_data/<batch_id>` → JSON **array** of block objects with at least `block_type` and `block_data` (plain text). Do not pass `entity_id` or `block_type` query args on this GET (full batch, all blocks).

## Stage 1: Import list on Agent Ad Hoc

**Done when:** Opening Agent Ad Hoc as an admin loads `GET /api/admin/adhoc/runs` once and renders every returned row in a `list-page-table` (columns: timestamp = `created_at`, `entity_id`, `task_key`) with no filter, search, pagination, or row cap. Clicking a row selects it (visual selected state). Empty array → table headers plus empty tbody (no placeholder rows). Failed list GET → existing `Toast` error; table stays empty. `npx tsc --noEmit` in `src/ui/frontend` passes.

1. In `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, add this type next to `EntityMeta`:

```ts
interface ImportRun {
  batch_id: string
  created_at: string | null
  entity_id: string | null
  task_key: string | null
}
```

2. In `AnthropicAdHoc`, add state:

```ts
const [importRuns, setImportRuns] = useState<ImportRun[]>([])
const [selectedImportBatchId, setSelectedImportBatchId] = useState<string>("")
```

3. Add a `useEffect` with `[]` deps (mount once) that calls `api("/api/admin/adhoc/runs")`, then `r.ok ? r.json() : Promise.reject(new Error(...))`, then `setImportRuns(Array.isArray(d) ? d : [])`. On catch, `setToast({ text: e.message, variant: "error" })` and leave `importRuns` as `[]`. Do **not** pass query params. Do **not** slice/limit the array.

4. In the JSX, **above** the `{/* ── Action buttons ── */}` block (after the entity-meta row), insert:

```tsx
      <div className="list-page-table-wrap" style={{ marginBottom: 16, maxHeight: "none" }}>
        <table className="list-page-table">
          <thead>
            <tr>
              <th>timestamp</th>
              <th>entity_id</th>
              <th>task_key</th>
            </tr>
          </thead>
          <tbody>
            {importRuns.map(run => (
              <tr
                key={run.batch_id}
                className="clickable"
                onClick={() => setSelectedImportBatchId(run.batch_id)}
                style={selectedImportBatchId === run.batch_id ? { background: "var(--bg-card)" } : undefined}
              >
                <td>{run.created_at ?? ""}</td>
                <td>{run.entity_id ?? ""}</td>
                <td>{run.task_key ?? ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
```

   Render `created_at` / `entity_id` / `task_key` as the API strings (empty cell when null). Do **not** add filters, search inputs, “showing N of M”, or `slice`. Do **not** add a new CSS class in `App.css`.

5. In the action-buttons row, **before** the Preview button, add:

```tsx
        <button
          className="btn primary"
          disabled={!selectedImportBatchId}
          onClick={() => { /* Stage 2 wires this */ }}
        >
          Load
        </button>
```

   Leave `onClick` as a no-op function `() => {}` until Stage 2 (button still disabled when nothing is selected). Do **not** change Preview / Test / Save As handlers in this stage.

⚠️ **Decision:** Full unfiltered table (parent: “the list is the table”), not a `<select>`. No `maxHeight`/`overflow` cap on the wrap — parent forbids a display cap.

## Stage 2: Load into editors, panes, task key, entity, confirm

**Done when:** Load of a selected batch fills System / Cache A–D / No Cache / User from SYSTEM / CACHE_A–D / NO_CACHE / TASK `block_data` (missing types → `""`), does not put RESPONSE into an editor, and shows `BatchAgentDataPanes` for **that** `batch_id`. Source rows are only read (GET). Workbench Task Key becomes the run’s `task_key` with a **single** leading `adhoc-` stripped, and the taskKey effect does **not** call `doFetchFrom` / `setConfirmFetch` for that set. If the run has `entity_id`, the next Preview/Test POST sends that id as `entity_id` and omits `entity_ids`. Dirty seven-editor content shows the same Yes, Replace (`btn danger`) / Cancel (`btn secondary`) banner family as fetch-from-task; Cancel leaves editors, `testBatchId`/panes, task key, and entity lock unchanged. `npx tsc --noEmit` in `src/ui/frontend` passes.

1. Add helpers **inside** `AnthropicAdHoc` (after `previewField` is not available inside — place them as inner functions after `hasContent`):

```ts
  function stripOneAdhocPrefix(raw: string): string {
    const s = (raw || "").trim()
    return s.startsWith("adhoc-") ? s.slice("adhoc-".length) : s
  }

  function textOfBlocks(blocks: { block_type?: string; block_data?: string }[], blockType: string): string {
    return blocks
      .filter(b => b.block_type === blockType)
      .map(b => (typeof b.block_data === "string" ? b.block_data : ""))
      .join("\n\n")
  }
```

   Strip **one** prefix only (no while-loop). `textOfBlocks` returns `""` when no blocks of that type.

2. Add refs/state:

```ts
  const skipCatalogFetchRef = useRef(false)
  const [importEntityLock, setImportEntityLock] = useState<string | null>(null)
  const [confirmLoad, setConfirmLoad] = useState<string | null>(null)
```

   `importEntityLock`: `null` = not in import-entity mode (Preview/Test use today’s batch vs single logic). Non-null string (including `""`) = Load restored that `entity_id` and Preview/Test must send it as a single entity.

3. In the `useEffect` that depends on `[taskKey, selectedId]` (comment `{/* When task key changes, load entity list + prompts */}`), **keep** the `adhoc/entities` fetch exactly as today. After the `isInitialMount` early return, add **before** `const existing = tasks.find(...)`:

```ts
    if (skipCatalogFetchRef.current) {
      skipCatalogFetchRef.current = false
      return
    }
```

   That return skips `setConfirmFetch` and `doFetchFrom` only. It must **not** skip the entities `api(...)` call above it.

4. On the Task Key `<select>`, change `onChange` to:

```ts
onChange={e => { setImportEntityLock(null); setTaskKey(e.target.value) }}
```

   On the entity `<select>` (non-batch branch), wrap `setEntityId` with `setImportEntityLock(null)` then `setEntityId`. On the batchCount `<input>`, wrap with `setImportEntityLock(null)` then existing `setBatchCount`. Do **not** clear the lock when `setTaskKey` is called from `doLoad`.

5. Replace `handlePreview` / `handleTest` body field `entity_id` / `entity_ids` with:

```ts
        entity_id: importEntityLock !== null
          ? importEntityLock
          : (entityMeta_batchIds ? "" : (entityId || "")),
        entity_ids: importEntityLock !== null ? undefined : (entityMeta_batchIds || undefined),
```

   Agent-required checks stay unchanged (`if (!agentId) { setToast...; return }`). Do **not** change Preview modal JSX, tab list, or `/api/admin/adhoc/preview` / `test` URLs.

6. Implement `doLoad(batchId: string)`:

```ts
  function doLoad(batchId: string) {
    setConfirmLoad(null)
    api(`/api/agent_data/${encodeURIComponent(batchId)}`)
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || `HTTP ${r.status}`) })
        return r.json()
      })
      .then(data => {
        const blocks = Array.isArray(data) ? data : []
        setSystemPrompt(textOfBlocks(blocks, "SYSTEM"))
        setCachePrompt(textOfBlocks(blocks, "CACHE_A"))
        setCachePromptB(textOfBlocks(blocks, "CACHE_B"))
        setCachePromptC(textOfBlocks(blocks, "CACHE_C"))
        setCachePromptD(textOfBlocks(blocks, "CACHE_D"))
        setNocachePrompt(textOfBlocks(blocks, "NO_CACHE"))
        setUserPrompt(textOfBlocks(blocks, "TASK"))
        const run = importRuns.find(r => r.batch_id === batchId)
        const catalog = stripOneAdhocPrefix(run?.task_key || "")
        if (catalog !== taskKey) {
          skipCatalogFetchRef.current = true
          setTaskKey(catalog)
        }
        const restoredEntity = run?.entity_id == null ? "" : String(run.entity_id)
        setEntityId(restoredEntity)
        setImportEntityLock(restoredEntity)
        setTestBatchId(batchId)
        setToast({ text: `Loaded agent data ${batchId}`, variant: "success" })
      })
      .catch(e => setToast({ text: e.message, variant: "error" }))
  }
```

   Do **not** call `doFetchFrom`. Do **not** write `agentId`. Do **not** PUT/POST `agent_data`. If `task_key` after strip is not in `taskKeysSorted`, still `setTaskKey(catalog)` (the select will show the raw value if the browser keeps it; do **not** add a fake catalog fetch). FEEDBACK / RESPONSE are not assigned to the seven editors.

7. `handleLoadClick`:

```ts
  function handleLoadClick() {
    if (!selectedImportBatchId) return
    if (hasContent) setConfirmLoad(selectedImportBatchId)
    else doLoad(selectedImportBatchId)
  }
```

   Wire the Stage 1 Load button `onClick={handleLoadClick}`.

8. Next to the existing `{confirmFetch && (...)}` banner, add a **same-structure** banner for `confirmLoad`:

- Gold border card, copy: `Replace current prompt content with imported run?`
- `button className="btn danger"` → `onClick={() => doLoad(confirmLoad)}` labeled `Yes, Replace`
- `button className="btn secondary"` → `onClick={() => setConfirmLoad(null)}` labeled `Cancel`

   Cancel must not call `doLoad`, must not change `testBatchId`, editors, `taskKey`, or `importEntityLock`.

9. If `entityMeta` is showing and `entityId` is non-empty and that id is **not** in `entityMeta.entities`, append `{ id: entityId, label: entityId }` to the mapped `<option>` list (non-batch select only) so the restored id remains visible/selected. Do **not** invent extra entity rows when the id is already in the list.

⚠️ **Decision:** Skip catalog fetch with `skipCatalogFetchRef`, not by leaving Task Key blank. AC4 is “do not replace imported editor text with catalog `agent_task` prompts”; the dropdown still needs the catalog key so Test records `adhoc-<task_key>` (AST-1451 already strips a second `adhoc-` if the posted key is prefixed).

⚠️ **Decision:** `importEntityLock` rather than changing global batch_mode Preview/Test. Today batch_mode ignores `entityId` and sends `entity_ids`. AC5 requires the loaded run’s `entity_id` on the next Preview/Test; the lock does that until the operator changes Task Key, entity select, or First-N.

## Estimate

Confirm Chuckles estimate: 3 — agree

One page, existing GET + `BatchAgentDataPanes`, confirm cloned from fetch-from-task, one skip-fetch ref. No new routes or schema.

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1452
**Overall:** APPROVED
**Publish-ref:** `origin/sub/AST-1439/AST-1452-ad-hoc-import-picker-and-load` @ `590f37461b21e84ed5012792785cf6a98e5dfa66`

### Traceability
AC2→S2 editor fill + `BatchAgentDataPanes` on imported `batch_id`; AC3→S2 task-key strip + no catalog fetch (Test prefix = AST-1451); AC4→S2 `skipCatalogFetchRef`; AC5→S2 `importEntityLock` + entity option append; AC6→S2 `confirmLoad` banner. Parent AC1 list chrome→S1 table + row select (data from AST-1451 `GET /api/admin/adhoc/runs`); parent AC7 debug list→N/A (sibling #1).

R1–R3 (in-session): 18 universal considered, all `conforms`. 18 scoped considered, all `conforms` (single `ui` page edit; reuses `BatchAgentDataPanes` + fetch-from-task confirm shape; `btn primary` / `btn danger` / `btn secondary`; block-type strings match existing `BatchAgentDataModal` `BLOCK_TYPE_ORDER`; no new routes/API; `importEntityLock` is presentation/session state, not duplicated catalog rules). 28 scoped excluded (no `src/core`/`data`/scripts/docs touch). Cited patterns `pattern.ui.shared-button-roles`, `pattern.config.config-block`, all `status: approved` and match plan shape. Sibling contract for list/load GET is explicit; does not reimplement AST-1451.

R6: faithful to child definition (picker + Load only). Boundaries respected (no list query, no Save As/Preview chrome, no `do_task`). `skipCatalogFetchRef` placement matches existing `taskKey` effect (`isInitialMount` return first, then skip, then `confirmFetch`/`doFetchFrom`). Estimate 3 is honest.

Findings: none (`fix-now` / `discuss`).

context_tokens≈58000

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-1439/AST-1452-ad-hoc-import-picker-and-load`  
**Product commits:** `7a5d1f19` (Stage 1 — import run list + Load button), `5cd9cef2` (Stage 2 — editor mapping, skip catalog fetch, entity lock, replace confirm)

No API or `config.py` edits. List source remains `GET /api/admin/adhoc/runs`; Load body remains `GET /api/agent_data/<batch_id>`; panes reuse `BatchAgentDataPanes`.

