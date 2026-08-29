# AST-1535 — Compact filtered import picker UI

- **Linear:** [AST-1535](https://linear.app/astralcareermatch/issue/AST-1535)
- **Parent:** [AST-1532](https://linear.app/astralcareermatch/issue/AST-1532)
- **Publish ref:** `sub/AST-1532/AST-1535-compact-filtered-import-picker-ui`

Agent Ad Hoc import still mounts an unbounded `list-page-table` of every `agent_data` batch (`GET /api/admin/adhoc/runs` with no query params, once on mount). Sibling [AST-1534](https://linear.app/astralcareermatch/issue/AST-1534) already ships filtered/capped runs + `UI_CONFIG["adhoc_import_picker_visible_rows"]` on `GET /api/system/ui_config`. This ticket owns **picker chrome only**: pass `candidate_id` / `task_key` on refetch, constrain the table wrap to ~N visible body rows with overflow scroll, keep Load / confirmLoad / row selection / `GET /api/agent_data/<batch_id>` unchanged.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | Refetch `/api/admin/adhoc/runs` with `candidate_id` / `task_key` when those change; read `adhoc_import_picker_visible_rows` from `/api/system/ui_config`; set wrap `maxHeight` to ~N body rows + sticky header; clear stale row selection; preserve Load / confirmLoad | ui |

Do **not** edit: `src/utils/config.py`, `src/data/database.py`, `src/core/agent.py`, `src/ui/api/**`, `src/ui/frontend/src/lib/uiConfig.ts`, `App.css`, Save As / Preview / Test handlers, `GET /api/agent_data/<batch_id>`, `tests/`, bible. Do **not** invent a client `limit` query param (API owns the cap). Do **not** add a new component file or route.

**Depends on AST-1534 contract (already User Testing):**  
`GET /api/admin/adhoc/runs?candidate_id=<id>&task_key=<catalog_key>` → JSON array `{batch_id, created_at, entity_id, task_key}`, at most `adhoc_import_runs_limit` rows, newest first. Omit/blank `candidate_id` → `[]`. Candidate + blank/omit `task_key` → last N for that candidate across task keys. `adhoc_import_picker_visible_rows` is on `GET /api/system/ui_config`.

## Stage 1: Filtered refetch on candidate / task change

**Done when:** With no candidate selected, the import picker shows zero rows and does not call `/api/admin/adhoc/runs` without a candidate (or the call is skipped and `importRuns` is set to `[]`). With a candidate selected, the effect that loads import runs includes `candidate_id=<selectedId>`; when `taskKey` is non-empty it also includes `task_key=<taskKey>`; when `taskKey` is empty it omits `task_key`. Changing `selectedId` or `taskKey` re-runs the fetch and replaces `importRuns`. If the previously selected `selectedImportBatchId` is not in the new array, selection clears to `""`. Load button / `doLoad` / confirm modal are untouched in this stage. No height/scroll change yet.

1. In `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, replace the mount-only import-runs `useEffect` (currently deps `[]`, calls `api("/api/admin/adhoc/runs")` with no query) with an effect that depends on `[selectedId, taskKey]` and does the following:

```tsx
  useEffect(() => {
    if (!selectedId) {
      setImportRuns([])
      setSelectedImportBatchId("")
      return
    }
    const params = new URLSearchParams({ candidate_id: selectedId })
    if (taskKey) params.set("task_key", taskKey)
    let cancelled = false
    api(`/api/admin/adhoc/runs?${params}`)
      .then(r => r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`)))
      .then(d => {
        if (cancelled) return
        const rows: ImportRun[] = Array.isArray(d) ? d : []
        setImportRuns(rows)
        setSelectedImportBatchId(prev =>
          prev && rows.some(r => r.batch_id === prev) ? prev : ""
        )
      })
      .catch(e => {
        if (cancelled) return
        setImportRuns([])
        setSelectedImportBatchId("")
        setToast({ text: e.message, variant: "error" })
      })
    return () => { cancelled = true }
  }, [selectedId, taskKey])
```

⚠️ **Decision:** Skip the HTTP call when `selectedId` is falsy and set `importRuns` to `[]` locally — matches sibling contract (blank candidate → empty list) and avoids a needless round-trip. Do not pass `task_key` when the dropdown is “No Task” (`taskKey === ""`); sibling treats blank/omit as “all task keys for that candidate.”

2. Do **not** change `doLoad`, `handleLoadClick`, `confirmLoad` modal, row `onClick` / selected highlight, table column headers (`timestamp` / `entity_id` / `task_key`), or the Load button’s `className="btn primary"` / disabled rule.

## Stage 2: Five-row scrollable picker viewport

**Done when:** The import table wrap scrolls inside a max height that shows about `adhoc_import_picker_visible_rows` body rows (plus the sticky header), read from `GET /api/system/ui_config` — not a bare literal `5` in JSX. With more rows than that (up to the API cap of 10), the wrap scrolls; with fewer, no pointless empty scroll chrome beyond content. Prompt editor tabs below remain reachable without paging through an unfiltered full-page table. Load / confirmLoad / Save As / Preview / Test still behave as before Stage 1.

1. In the same file, add state for the visible-row count and a mount (or once-per-page) effect that loads it from system ui_config:

```tsx
  const [importPickerVisibleRows, setImportPickerVisibleRows] = useState<number | null>(null)

  useEffect(() => {
    api("/api/system/ui_config")
      .then(r => r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`)))
      .then(cfg => {
        const n = cfg?.adhoc_import_picker_visible_rows
        setImportPickerVisibleRows(typeof n === "number" && n > 0 ? n : null)
      })
      .catch(() => setImportPickerVisibleRows(null))
  }, [])
```

⚠️ **Decision:** Fetch `/api/system/ui_config` inline in this page (same pattern as `ArtifactsBaseResumeContent.tsx`) rather than extending `src/ui/frontend/src/lib/uiConfig.ts` — ticket Scope lists only `AdminAnthropicAdHoc.tsx`. Do not add the key to the shared `UiConfig` interface in this ticket.

2. Above the component (near other module consts), add named layout mirrors for `.list-page-table` padding in `App.css` (thead `padding: 6px 10px`, tbody `padding: 5px 10px`, `font-size: 13px`, 1px border):

```tsx
// Layout mirrors of App.css .list-page-table th/td — used only to size the picker viewport.
const ADHOC_IMPORT_PICKER_HEAD_PX = 33
const ADHOC_IMPORT_PICKER_ROW_PX = 29
```

3. Replace the import table wrap (currently `className="list-page-table-wrap"` with `style={{ marginBottom: 16, maxHeight: "none" }}`) so it uses scroll + config-driven height:

```tsx
      <div
        className="list-page-table-wrap list-page-table-wrap--scroll"
        style={{
          marginBottom: 16,
          maxHeight: importPickerVisibleRows == null
            ? undefined
            : ADHOC_IMPORT_PICKER_HEAD_PX + importPickerVisibleRows * ADHOC_IMPORT_PICKER_ROW_PX,
          overflowY: "auto",
        }}
      >
```

Keep the inner `<table className="list-page-table">`, thead columns, and tbody row map / click / selection highlight exactly as they are after Stage 1.

⚠️ **Decision:** Pixel-per-row constants are layout mirrors of existing CSS, not business caps — the **count** of visible rows comes only from `adhoc_import_picker_visible_rows`. If ui_config is missing or the key is absent, leave `maxHeight` unset (`undefined`) rather than hardcoding `5` in the style object; once config loads, the viewport snaps to N rows. Sticky thead (already in `.list-page-table thead th`) continues to work inside the scrolling wrap via `list-page-table-wrap--scroll`.

4. Smoke-check by hand after implement (build-child): candidate off → empty picker; candidate on + empty task key → up to 10 rows for that candidate; candidate + task key → filtered set; scroll when rows > visible count; Load still fills the seven editors via `GET /api/agent_data/<batch_id>` with dirty confirm.

## Estimate

Confirm Chuckles estimate: 2 — agree
