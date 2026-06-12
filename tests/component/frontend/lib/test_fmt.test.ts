import { describe, expect, it } from "vitest"
import {
  formatCell,
  fmtTime,
  setFmtTimezone,
} from "../../../../src/ui/frontend/src/lib/fmt"

describe("fmtTime", () => {
  it("returns em dash for empty values", () => {
    expect(fmtTime(null)).toBe("—")
    expect(fmtTime(undefined)).toBe("—")
    expect(fmtTime("")).toBe("—")
  })

  it("formats UTC timestamps with explicit timezone", () => {
    const out = fmtTime("2026-05-13T12:00:00Z", "UTC")
    expect(out).toContain("5/13/26")
  })

  it("appends Z for bare UTC timestamps and honors default timezone", () => {
    setFmtTimezone("UTC")
    const out = fmtTime("2026-05-13 12:00:00")
    expect(out).toContain("5/13/26")
  })

  it("keeps offset timestamps unchanged", () => {
    const out = fmtTime("2026-05-13T12:00:00+00:00", "UTC")
    expect(out).toContain("5/13/26")
  })

  it("returns the raw value when parsing fails", () => {
    expect(fmtTime("not-a-date")).toBe("not-a-date")
  })
})

describe("formatCell", () => {
  it("returns em dash for empty values", () => {
    expect(formatCell(null, "integer")).toBe("—")
    expect(formatCell(undefined, "integer")).toBe("—")
    expect(formatCell("", "integer")).toBe("—")
  })

  it("formats known number formats", () => {
    expect(formatCell(12, "integer")).toBe("12")
    expect(formatCell(1.2, "decimal")).toContain("1.20")
    expect(formatCell(1.2, "currency")).toContain("$")
    expect(formatCell("2026-05-13 12:00:00", "date")).toContain("5/13/26")
    expect(formatCell("2026-05-13 12:00:00", "datetime")).toContain("5/13/26")
  })

  it("falls back when numbers are not numeric", () => {
    expect(formatCell("plain", "integer")).toBe("plain")
    expect(formatCell("plain", "decimal")).toBe("plain")
    expect(formatCell("plain", "currency")).toBe("plain")
  })

  it("falls back for unknown formats", () => {
    expect(formatCell("plain", "text")).toBe("plain")
    expect(formatCell("plain", null)).toBe("plain")
  })
})
