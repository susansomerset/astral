import { describe, expect, it } from "vitest"
import { browserTabTitle } from "../../../../src/ui/frontend/src/lib/documentTitle"

describe("browserTabTitle", () => {
  it.each([
    [undefined, "Astral"],
    [null, "Astral"],
    ["", "Astral"],
    ["   ", "Astral"],
    ["Jolane Abrams", "Astral - Jolane Abrams"],
    ["  Jolane Abrams  ", "Astral - Jolane Abrams"],
  ] as const)("formats %j → %s", (full, title) => {
    expect(browserTabTitle(full)).toBe(title)
  })
})
