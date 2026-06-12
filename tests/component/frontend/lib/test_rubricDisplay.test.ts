import { describe, expect, it } from "vitest"
import {
  RUBRIC_DEFAULT_IMPORTANCE,
  buildJobListRubricColumns,
  buildJobListRubricColumnsFromArtifact,
  formatRubricColumnTooltip,
  formatRubricVectorHeader,
  normalizeRubricVectorKey,
  resolveRubricHeaderCode,
  rubricItemImportance,
  sortJobListRubricColumns,
} from "../../../../src/ui/frontend/src/lib/rubricDisplay"

describe("rubricItemImportance", () => {
  it("returns stored integers in range", () => {
    expect(rubricItemImportance({ importance: 3 })).toBe(3)
  })

  it("falls back for missing or invalid values", () => {
    expect(rubricItemImportance({})).toBe(RUBRIC_DEFAULT_IMPORTANCE)
    expect(rubricItemImportance({ importance: 0 })).toBe(RUBRIC_DEFAULT_IMPORTANCE)
    expect(rubricItemImportance({ importance: 11 })).toBe(RUBRIC_DEFAULT_IMPORTANCE)
    expect(rubricItemImportance({ importance: 2.5 })).toBe(RUBRIC_DEFAULT_IMPORTANCE)
    expect(rubricItemImportance({ importance: Number.NaN })).toBe(RUBRIC_DEFAULT_IMPORTANCE)
    expect(rubricItemImportance({ importance: "5" })).toBe(RUBRIC_DEFAULT_IMPORTANCE)
    expect(rubricItemImportance({ importance: 10 })).toBe(10)
  })
})

describe("normalizeRubricVectorKey", () => {
  it("strips trailing model codes and lowercases", () => {
    expect(normalizeRubricVectorKey("Culture Fit (AB)")).toBe("culture fit")
    expect(normalizeRubricVectorKey("  Skills  ")).toBe("skills")
  })
})

describe("formatRubricColumnTooltip", () => {
  it("formats label and importance as Label (n)", () => {
    expect(formatRubricColumnTooltip("Title Match", 7)).toBe("Title Match (7)")
    expect(formatRubricColumnTooltip(undefined, 5)).toBe("?? (5)")
  })
})

describe("resolveRubricHeaderCode", () => {
  it("prefers code then label prefix", () => {
    expect(resolveRubricHeaderCode({ code: "TE", label: "Technical" })).toBe("TE")
    expect(resolveRubricHeaderCode({ label: "Culture" })).toBe("CU")
  })
})

describe("sortJobListRubricColumns", () => {
  it("orders by importance desc then code asc", () => {
    const cols = sortJobListRubricColumns([
      { code: "B", label: "B", importance: 1, headerCode: "B", headerTooltip: "B (1)" },
      { code: "A", label: "A", importance: 10, headerCode: "A", headerTooltip: "A (10)" },
      { code: "C", label: "C", importance: 10, headerCode: "C", headerTooltip: "C (10)" },
    ])
    expect(cols.map(c => c.code)).toEqual(["A", "C", "B"])
  })
})

describe("buildJobListRubricColumnsFromArtifact", () => {
  it("builds compact headers and sorts by importance", () => {
    const cols = buildJobListRubricColumnsFromArtifact([
      { code: "CU", label: "Culture", importance: 1 },
      { code: "TE", label: "Technical", importance: 7 },
    ])
    expect(cols[0].headerCode).toBe("TE")
    expect(cols[0].headerTooltip).toBe("Technical (7)")
    expect(cols[1].headerCode).toBe("CU")
  })
})

describe("buildJobListRubricColumns", () => {
  it("uses artifact when present else job grades", () => {
    const fromArt = buildJobListRubricColumns({
      rubricArtifactKey: "like_rubric",
      artifacts: { like_rubric: [{ code: "TE", label: "Technical", importance: 3 }] },
      gradeKey: "like_grades",
      jobs: [],
    })
    expect(fromArt[0].headerCode).toBe("TE")

    const fromGrades = buildJobListRubricColumns({
      rubricArtifactKey: "like_rubric",
      artifacts: {},
      gradeKey: "like_grades",
      jobs: [{ like_grades: [{ vector: "Fit" }] }],
    })
    expect(fromGrades[0].headerCode).toBe("Fit")
  })
})

describe("formatRubricVectorHeader", () => {
  it("includes code when present", () => {
    expect(formatRubricVectorHeader(4, "Culture", "CF")).toBe("4 - Culture (CF)")
  })

  it("omits code and normalizes missing pieces", () => {
    expect(formatRubricVectorHeader(4, "Culture", "")).toBe("4 - Culture")
    expect(formatRubricVectorHeader(undefined, "Culture", "")).toBe(`${RUBRIC_DEFAULT_IMPORTANCE} - Culture`)
    expect(formatRubricVectorHeader(12, "  ", "CF")).toBe(`${RUBRIC_DEFAULT_IMPORTANCE} - ?? (CF)`)
    expect(formatRubricVectorHeader(7, undefined, "CF")).toBe("7 - ?? (CF)")
    expect(formatRubricVectorHeader(8, "  ", undefined)).toBe("8 - ??")
  })
})
