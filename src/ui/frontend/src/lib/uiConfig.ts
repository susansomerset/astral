import api from "./api"

interface ColumnTypeConfig { align: "left" | "right" | "center"; number_format: string | null }

export interface UiConfig {
  column_types: Record<string, ColumnTypeConfig>
  list_table_frozen_data_columns?: number
  list_table_cell_truncate_chars?: number
}

let _uiConfig: UiConfig | null = null
let _uiConfigPending: Promise<void> | null = null

export function getUiConfig(): UiConfig | null {
  return _uiConfig
}

export function loadUiConfig(onReady: () => void) {
  if (_uiConfig) { onReady(); return }
  if (!_uiConfigPending) {
    _uiConfigPending = api("/api/system/ui_config")
      .then(r => r.json())
      .then(d => { _uiConfig = d })
      .catch(() => { _uiConfig = { column_types: {} } })
      .finally(() => { _uiConfigPending = null })
  }
  _uiConfigPending.then(onReady)
}
