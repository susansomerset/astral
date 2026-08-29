# AST-1535 — Compact filtered import picker UI

- **Linear:** [AST-1535](https://linear.app/astralcareermatch/issue/AST-1535)
- **Parent:** [AST-1532](https://linear.app/astralcareermatch/issue/AST-1532)
- **Publish ref:** `sub/AST-1532/AST-1535-compact-filtered-import-picker-ui`

Agent Ad Hoc import still mounts an unbounded `list-page-table` of every `agent_data` batch (`GET /api/admin/adhoc/runs` with no query params, once on mount). Sibling [AST-1534](https://linear.app/astralcareermatch/issue/AST-1534) already ships filtered/capped runs + `UI_CONFIG["adhoc_import_picker_visible_rows"]` on `GET /api/ui_config`. This ticket owns **picker chrome only**: pass `candidate_id` / `task_key` on refetch, constrain the table wrap to ~N visible body rows with overflow scroll, keep Load / confirmLoad / row selection / `GET /api/agent_data/<batch_id>` unchanged.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | Refetch `/api/admin/adhoc/runs` with `candidate_id` / `task_key` when those change; read `adhoc_import_picker_visible_rows` from `/api/ui_config`; set wrap `maxHeight` to ~N body rows + sticky header; clear stale row selection; preserve Load / confirmLoad | ui |

Do **not** edit: `src/utils/config.py`, `src/data/database.py`, `src/core/agent.py`, `src/ui/api/**`, `src/ui/frontend/src/lib/uiConfig.ts`, `App.css`, Save As / Preview / Test handlers, `GET /api/agent_data/<batch_id>`, `tests/`, bible. Do **not** invent a client `limit` query param (API owns the cap). Do **not** add a new component file or route.

**Depends on AST-1534 contract (already User Testing):**  
`GET /api/admin/adhoc/runs?candidate_id=<id>&task_key=<catalog_key>` → JSON array `{batch_id, created_at, entity_id, task_key}`, at most `adhoc_import_runs_limit` rows, newest first. Omit/blank `candidate_id` → `[]`. Candidate + blank/omit `task_key` → last N for that candidate across task keys. `adhoc_import_picker_visible_rows` is on `GET /api/ui_config`.

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

**Done when:** The import table wrap scrolls inside a max height that shows about `adhoc_import_picker_visible_rows` body rows (plus the sticky header), read from `GET /api/ui_config` — not a bare literal `5` in JSX. With more rows than that (up to the API cap of 10), the wrap scrolls; with fewer, no pointless empty scroll chrome beyond content. Prompt editor tabs below remain reachable without paging through an unfiltered full-page table. Load / confirmLoad / Save As / Preview / Test still behave as before Stage 1.

1. In the same file, add state for the visible-row count and a mount (or once-per-page) effect that loads it from ui_config:

```tsx
  const [importPickerVisibleRows, setImportPickerVisibleRows] = useState<number | null>(null)

  useEffect(() => {
    api("/api/ui_config")
      .then(r => r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`)))
      .then(cfg => {
        const n = cfg?.adhoc_import_picker_visible_rows
        setImportPickerVisibleRows(typeof n === "number" && n > 0 ? n : null)
      })
      .catch(() => setImportPickerVisibleRows(null))
  }, [])
```

⚠️ **Decision:** Fetch `/api/ui_config` inline in this page (live Flask route: `system_bp` `/api` + `/ui_config` — same path as `CandidateProfile.tsx` / `IntakePreamblePanel.tsx`) rather than extending `src/ui/frontend/src/lib/uiConfig.ts` — ticket Scope lists only `AdminAnthropicAdHoc.tsx`. Do not use `/api/system/ui_config` (stale alias; no blueprint route). Do not add the key to the shared `UiConfig` interface in this ticket.

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

## Revisions

Revision 1 — 2026-08-29
Driven by: Joan `[plan-rubric] REVIEW … fix ui_config URL` / fix-now (plan-discuss round=1)
Changes: Every plan reference to `GET /api/system/ui_config` → live `GET /api/ui_config` (summary, Files Changed, Depends-on, Stage 2 Done when / step 1 code + Decision). Decision now cites `CandidateProfile` / `IntakePreamblePanel`; explicitly rejects the stale `/api/system/ui_config` alias.

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1535
**Overall:** REVISE
**Publish ref:** `sub/AST-1532/AST-1535-compact-filtered-import-picker-ui` @ `fdbed48252bc7fc41e4ede6e744fdf5a61b797e6`

## Traceability
AC2→Stage 2; AC3→Stage 1; AC4→Stages 1–2 (Load/confirmLoad untouched; smoke Stage 2); parent AC1→N/A (AST-1534 API)

## Findings

### fix-now
- **Severity:** fix-now
- **Location:** Stage 2 — ui_config fetch (`api("/api/system/ui_config")`); Files Changed / Depends-on prose
- **Finding:** Plan prescribes `GET /api/system/ui_config`, but the live Flask route is `system_bp` prefix `/api` + `@system_bp.route("/ui_config")` → **`GET /api/ui_config`** (`api_system.py`). There is no `/api/system/ui_config` blueprint route; unmatched `/api/*` paths fall through to the React catch-all (HTML 200), so `r.json()` fails, the catch sets `importPickerVisibleRows` to `null`, and `maxHeight` stays `undefined`. Child AC2 (≈five visible rows + scroll) would not be met in production — only the API cap (10 rows) limits height.
- **Recommendation:** In Stage 2 step 1, fetch `api("/api/ui_config")` (same payload — spreads `UI_CONFIG` including `adhoc_import_picker_visible_rows`). Update plan prose that says `/api/system/ui_config` to `/api/ui_config` for accuracy. `CandidateProfile.tsx` / `IntakePreamblePanel.tsx` already use the live path; `ArtifactsBaseResumeContent.tsx` is the stale alias donor — do not copy its URL here.

### acceptable
- **Location:** Stage 2 — `ADHOC_IMPORT_PICKER_HEAD_PX` / `ADHOC_IMPORT_PICKER_ROW_PX`
- **Finding:** Pixel layout mirrors of `.list-page-table` CSS, not business caps.
- **Recommendation:** Acceptable — visible-row **count** comes only from `adhoc_import_picker_visible_rows`; pixels size the viewport.

- **Location:** Stage 2 — `maxHeight: undefined` when config missing
- **Finding:** No hardcoded `5` fallback if ui_config fails after a correct URL.
- **Recommendation:** Acceptable once URL is fixed — API cap is 10 rows; degraded unbounded wrap is bounded and documented.

- **Location:** Boundaries — `tests/`, bible
- **Finding:** No component-test plan for filtered refetch / scroll viewport.
- **Recommendation:** Acceptable at plan gate — Betty owns qa-child; plan scope is single page file only.

## Notes
- Status `Plan Ready`; assignee Joan Clarke (validator spawn carries authority).
- Zero completed `[plan-discuss]` rounds — round=1 concern for this REVISE.
- Scope faithful: single file `AdminAnthropicAdHoc.tsx`; no API/config edits; no client `limit` param.
- Stage 1 filtered refetch (`[selectedId, taskKey]`, skip when no candidate, omit `task_key` for “No Task”, stale selection clear, cancellation guard) matches AST-1534 contract and child AC3.
- `pattern.ui.shared-button-roles` preserved (`btn primary` Load); `list-page-table-wrap--scroll` matches existing admin list pattern.
- Depends on AST-1534 query-param contract — sibling sub ref ships `adhoc_import_runs_limit` + `adhoc_import_picker_visible_rows` on ui_config spread.

context_tokens≈52000

## Joan validate (round 2)

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1535
**Overall:** APPROVED
**Publish ref:** `sub/AST-1532/AST-1535-compact-filtered-import-picker-ui` @ `a80cf9275cc7a04a45131a2776c60f22e022e6ec`

## Traceability
AC2→Stage 2; AC3→Stage 1; AC4→Stages 1–2 (Load/confirmLoad untouched; smoke Stage 2); parent AC1→N/A (AST-1534 API)

## Notes
- Status `Plan Ready`; assignee Joan Clarke. One completed plan-discuss round (round=1 concern + reply) — prior fix-now resolved in revision 1 (`/api/ui_config`).
- Scope: single file `AdminAnthropicAdHoc.tsx` only; no API/config/test creep.
- Stage 1: `[selectedId, taskKey]` refetch, skip fetch when no candidate, omit `task_key` for “No Task”, stale selection clear, cancellation guard — matches AST-1534 contract and child AC3.
- Stage 2: `api("/api/ui_config")` matches live `system_bp` route; visible-row count from `adhoc_import_picker_visible_rows`; layout px mirrors documented; `list-page-table-wrap--scroll` + sticky thead — child AC2.
- Load / confirmLoad / `GET /api/agent_data/<batch_id>` unchanged — child AC4.
- `pattern.ui.shared-button-roles` preserved (`btn primary` Load); frontend placement/naming statutes satisfied; no client `limit` param.

context_tokens≈55000
