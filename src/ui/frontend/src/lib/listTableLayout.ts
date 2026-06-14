export interface ListTableUiConfig {
  list_table_frozen_data_columns?: number
  list_table_cell_truncate_chars?: number
}

export const LIST_TABLE_CHECKBOX_WIDTH_PX = 40

export function resolveFrozenDataColumns(
  ui: ListTableUiConfig | null,
  override?: number,
): number {
  if (typeof override === "number" && override >= 0) return override
  const n = ui?.list_table_frozen_data_columns
  return typeof n === "number" && n >= 0 ? n : 0
}

export function resolveCellTruncateChars(ui: ListTableUiConfig | null): number {
  const n = ui?.list_table_cell_truncate_chars
  return typeof n === "number" && n > 0 ? n : 30
}

export function truncateForDisplay(text: string, maxChars: number): { display: string; full: string } {
  const full = text
  if (full.length <= maxChars) return { display: full, full }
  return { display: full.slice(0, maxChars) + "\u2026", full }
}

/** Cumulative sticky `left` for a data column index (0-based within ordered data columns). */
export function stickyLeftPx(
  dataColIndex: number,
  colWidths: Record<string, number>,
  orderedKeys: string[],
  hasCheckbox: boolean,
  frozenDataColumns: number,
): number | null {
  if (dataColIndex >= frozenDataColumns) return null
  let left = hasCheckbox ? LIST_TABLE_CHECKBOX_WIDTH_PX : 0
  for (let i = 0; i < dataColIndex; i++) {
    const key = orderedKeys[i]
    left += colWidths[key] ?? 120
  }
  return left
}
