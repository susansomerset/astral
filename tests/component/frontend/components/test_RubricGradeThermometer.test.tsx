import { readFileSync, readdirSync, statSync } from "node:fs"
import path from "node:path"
import { render } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import RubricGradeThermometer from "../../../../src/ui/frontend/src/components/RubricGradeThermometer"

const frontendSrc = path.resolve(__dirname, "../../../../src/ui/frontend/src")

function walk(dir: string): string[] {
  const out: string[] = []
  for (const name of readdirSync(dir)) {
    const full = path.join(dir, name)
    if (statSync(full).isDirectory()) out.push(...walk(full))
    else out.push(full)
  }
  return out
}

describe("RubricGradeThermometer", () => {
  it("AST-2262: keeps positive A-B-C-D-F-X letters, orders them, and dates the tooltip", () => {
    const { container } = render(
      <RubricGradeThermometer
        letters={[
          { grade: " x ", count: 1, last_seen: "2026-06-01 09:00:00" },
          { grade: "A", count: 0, last_seen: "2026-01-01 00:00:00" },
          { grade: "Z", count: 4, last_seen: "2026-01-01 00:00:00" },
          { grade: "f", count: 3, last_seen: "2026-05-02 00:00:00" },
          { grade: "B", count: 2, last_seen: "  2026-04-03 11:22:33" },
        ]}
      />,
    )
    const segs = [...container.querySelectorAll(".rubric-grade-thermometer-seg")]
    expect(segs.map(el => el.className)).toEqual([
      "rubric-grade-thermometer-seg seg-b",
      "rubric-grade-thermometer-seg seg-f",
      "rubric-grade-thermometer-seg seg-x",
    ])
    expect(segs.map(el => el.getAttribute("title"))).toEqual([
      "B, 2, 2026-04-03",
      "F, 3, 2026-05-02",
      "X, 1, 2026-06-01",
    ])
    expect((segs[0] as HTMLElement).style.flexGrow).toBe("2")
    expect(container.querySelector(".rubric-grade-thermometer")?.childElementCount).toBe(3)
  })

  it("AST-2262: an empty kept list still renders the track", () => {
    const { container } = render(
      <RubricGradeThermometer letters={[{ grade: "A", count: 0, last_seen: "" }]} />,
    )
    const track = container.querySelector(".rubric-grade-thermometer")
    expect(track).not.toBeNull()
    expect(track?.childElementCount).toBe(0)
  })

  it("AST-2262: segment colors are the existing grade tokens, and pages do not draw a second bar", () => {
    const css = readFileSync(path.join(frontendSrc, "App.css"), "utf8")
    for (const letter of ["a", "b", "c", "d", "f", "x"]) {
      expect(css).toContain(`.rubric-grade-thermometer-seg.seg-${letter} { background: var(--grade-${letter}); }`)
    }
    const pages = walk(path.join(frontendSrc, "pages"))
    for (const file of pages) {
      const text = readFileSync(file, "utf8")
      expect(text).not.toContain("RubricGradeThermometer")
      expect(text).not.toContain("rubric-grade-thermometer")
    }
    const callers = walk(frontendSrc).filter(file =>
      readFileSync(file, "utf8").includes("RubricGradeThermometer"),
    )
    expect(callers.map(file => path.relative(frontendSrc, file)).sort()).toEqual([
      "components/ArtifactEditor.tsx",
      "components/RubricGradeThermometer.tsx",
    ])
  })
})
