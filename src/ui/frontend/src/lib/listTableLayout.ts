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

/** User-resized width wins; else measured; stickyLeftPx still uses 120 fallback when both missing. */
export function mergeWidthsForSticky(
  persisted: Record<string, number>,
  measured: Record<string, number>,
): Record<string, number> {
  const out: Record<string, number> = { ...measured }
  for (const [key, w] of Object.entries(persisted)) {
    if (typeof w === "number" && w > 0) out[key] = w
  }
  return out
}

export function measureListTableColumnWidths(
  table: HTMLTableElement,
  orderedKeys: string[],
  hasCheckbox: boolean,
): { checkboxWidthPx: number; dataWidths: Record<string, number> } {
  const headerRow = table.tHead?.rows[0]
  if (!headerRow) return { checkboxWidthPx: LIST_TABLE_CHECKBOX_WIDTH_PX, dataWidths: {} }
  let colIdx = 0
  let checkboxWidthPx = LIST_TABLE_CHECKBOX_WIDTH_PX
  if (hasCheckbox) {
    checkboxWidthPx = headerRow.cells[colIdx]?.offsetWidth ?? LIST_TABLE_CHECKBOX_WIDTH_PX
    colIdx += 1
  }
  const dataWidths: Record<string, number> = {}
  for (const key of orderedKeys) {
    const cell = headerRow.cells[colIdx]
    if (cell && cell.offsetWidth > 0) dataWidths[key] = cell.offsetWidth
    colIdx += 1
  }
  return { checkboxWidthPx, dataWidths }
}

/** Cumulative sticky `left` for a data column index (0-based within ordered data columns). */
export function stickyLeftPx(
  dataColIndex: number,
  colWidths: Record<string, number>,
  orderedKeys: string[],
  hasCheckbox: boolean,
  frozenDataColumns: number,
  checkboxWidthPx: number = LIST_TABLE_CHECKBOX_WIDTH_PX,
): number | null {
  if (dataColIndex >= frozenDataColumns) return null
  let left = hasCheckbox ? checkboxWidthPx : 0
  for (let i = 0; i < dataColIndex; i++) {
    const key = orderedKeys[i]
    left += colWidths[key] ?? 120
  }
  return left
}
