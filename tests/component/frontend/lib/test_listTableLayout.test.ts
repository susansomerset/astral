import { describe, expect, it } from "vitest"
import {
  LIST_TABLE_CHECKBOX_WIDTH_PX,
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
})
