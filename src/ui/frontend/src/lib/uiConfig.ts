import api from "./api"

interface ColumnTypeConfig { align: "left" | "right" | "center"; number_format: string | null }
/** AST-2042: one theme registry entry served from UI_CONFIG.themes (keyed by palette id). */
export interface ThemeEntry { label: string; profile_selectable: boolean }
export interface UiConfig {
  column_types: Record<string, ColumnTypeConfig>
  list_table_frozen_data_columns?: number
  list_table_cell_truncate_chars?: number
  /** AST-1981: job-title display cut served from UI_CONFIG; read via resolveJobTitleTruncateChars. */
  job_title_truncate_chars?: number
  /** AST-2042: palette id -> entry; each id has a matching [data-theme] block in App.css. */
  themes?: Record<string, ThemeEntry>
  /** AST-2042: palette applied when the selected candidate has no stored theme. */
  default_theme?: string
}

let _uiConfig: UiConfig | null = null
let _uiConfigPending: Promise<void> | null = null

export function getUiConfig(): UiConfig | null {
  return _uiConfig
}

export function loadUiConfig(onReady: () => void) {
  if (_uiConfig) { onReady(); return }
  if (!_uiConfigPending) {
    _uiConfigPending = api("/api/ui_config")
      .then(r => r.json())
      .then(d => { _uiConfig = d })
      .catch(() => { _uiConfig = { column_types: {} } })
      .finally(() => { _uiConfigPending = null })
  }
  _uiConfigPending.then(onReady)
}

/** Job-title cut length; falls back to 50 until UI config loads (mirrors resolveCellTruncateChars). */
export function resolveJobTitleTruncateChars(ui: UiConfig | null): number {
  const n = ui?.job_title_truncate_chars
  return typeof n === "number" && n > 0 ? n : 50
}
