import { describe, expect, it } from "vitest"
import {
  LIST_TABLE_CHECKBOX_WIDTH_PX,
  measureListTableColumnWidths,
  mergeWidthsForSticky,
  resolveCellTruncateChars,
  resolveFrozenDataColumns,
  stickyLeftPx,
  truncateForDisplay,
} from "../../../../src/ui/frontend/src/lib/listTableLayout"

describe("listTableLayout (AST-647)", () => {
  it("resolveFrozenDataColumns prefers override then ui_config", () => {
    expect(resolveFrozenDataColumns({ list_table_frozen_data_columns: 2 }, 3)).toBe(3)
    expect(resolveFrozenDataColumns({ list_table_frozen_data_columns: 2 })).toBe(2)
    expect(resolveFrozenDataColumns(null)).toBe(0)
  })

  it("resolveCellTruncateChars falls back to 30", () => {
    expect(resolveCellTruncateChars({ list_table_cell_truncate_chars: 12 })).toBe(12)
    expect(resolveCellTruncateChars(null)).toBe(30)
  })

  it("truncateForDisplay adds ellipsis when over max", () => {
    const long = "x".repeat(40)
    const { display, full } = truncateForDisplay(long, 30)
    expect(full).toBe(long)
    expect(display).toBe(`${"x".repeat(30)}\u2026`)
    expect(truncateForDisplay("short", 30)).toEqual({ display: "short", full: "short" })
  })

  it("stickyLeftPx accounts for checkbox width and prior columns", () => {
    const widths = { a: 100, b: 80, c: 60 }
    const keys = ["a", "b", "c"]
    expect(stickyLeftPx(0, widths, keys, true, 2)).toBe(LIST_TABLE_CHECKBOX_WIDTH_PX)
    expect(stickyLeftPx(1, widths, keys, true, 2)).toBe(LIST_TABLE_CHECKBOX_WIDTH_PX + 100)
    expect(stickyLeftPx(2, widths, keys, true, 2)).toBeNull()
  })

  it("AST-657: stickyLeftPx accepts measured checkbox width", () => {
    const widths = { a: 100, b: 80 }
    const keys = ["a", "b"]
    expect(stickyLeftPx(0, widths, keys, true, 2, 52)).toBe(52)
    expect(stickyLeftPx(1, widths, keys, true, 2, 52)).toBe(152)
  })

  it("AST-657: mergeWidthsForSticky prefers persisted over measured", () => {
    expect(mergeWidthsForSticky({ a: 200 }, { a: 90, b: 50 })).toEqual({ a: 200, b: 50 })
    expect(mergeWidthsForSticky({}, { a: 90 })).toEqual({ a: 90 })
  })

  it("AST-657: measureListTableColumnWidths reads header cell offsetWidth", () => {
    const table = document.createElement("table")
    const thead = document.createElement("thead")
    const tr = document.createElement("tr")
    const cb = document.createElement("th")
    const a = document.createElement("th")
    const b = document.createElement("th")
    Object.defineProperty(cb, "offsetWidth", { value: 48 })
    Object.defineProperty(a, "offsetWidth", { value: 110 })
    Object.defineProperty(b, "offsetWidth", { value: 75 })
    tr.append(cb, a, b)
    thead.append(tr)
    table.append(thead)
    const { checkboxWidthPx, dataWidths } = measureListTableColumnWidths(table, ["a", "b"], true)
    expect(checkboxWidthPx).toBe(48)
    expect(dataWidths).toEqual({ a: 110, b: 75 })
  })
})
