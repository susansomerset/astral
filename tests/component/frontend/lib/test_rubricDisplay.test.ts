import { describe, expect, it } from "vitest"
import {
  RUBRIC_DEFAULT_IMPORTANCE,
  analysisTimeScoreForJob,
  buildJobListRubricColumns,
  buildJobListRubricColumnsForGroup,
  buildJobListRubricColumnsFromArtifact,
  formatRubricColumnTooltip,
  formatRubricVectorHeader,
  groupJobsByAlignedRubric,
  jobCarriedRubricKey,
  jobCarriedScoreKey,
  jobListRubricFingerprint,
  jobListRubricFingerprintFromGrades,
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

describe("AST-1064 job-carried list helpers", () => {
  it("maps gradeKey to rubric and score keys", () => {
    expect(jobCarriedRubricKey("jd_grades")).toBe("jd_rubric")
    expect(jobCarriedScoreKey("like_grades")).toBe("like_score")
    expect(jobCarriedRubricKey("")).toBe("")
    expect(jobCarriedRubricKey("latest_score")).toBe("")
    expect(jobCarriedScoreKey("nope")).toBe("")
  })

  it("fingerprints rubric shape ignoring order and importance", () => {
    const a = jobListRubricFingerprint([
      { code: "B", label: "Beta", importance: 1 },
      { code: "A", label: "Alpha", importance: 9 },
    ])
    const b = jobListRubricFingerprint([
      { code: "A", label: "Alpha", importance: 2 },
      { code: "B", label: "Beta", importance: 2 },
    ])
    expect(a).toBe(b)
    expect(jobListRubricFingerprint([])).toBe("")
    expect(jobListRubricFingerprint(null)).toBe("")
  })

  it("fingerprints grades-only arrays and maps", () => {
    expect(jobListRubricFingerprintFromGrades([
      { vector: "Beta (B)" },
      { vector: "Alpha (A)" },
    ])).toBe(jobListRubricFingerprintFromGrades([
      { vector: "Alpha (A)" },
      { vector: "Beta (B)" },
    ]))
    expect(jobListRubricFingerprintFromGrades({ JD: "B", Fit: "A" })).toContain("jd")
    expect(jobListRubricFingerprintFromGrades(null)).toBe("")
  })

  it("groups by job-carried rubric, grades fallback, and empty", () => {
    const rubricA = [{ code: "CS", label: "Company Stage", importance: 5 }]
    const rubricB = [
      { code: "CS", label: "Company Stage", importance: 5 },
      { code: "ET", label: "Employment Type", importance: 3 },
    ]
    const jobs = [
      { id: "1", like_rubric: rubricA, like_grades: [{ vector: "Company Stage", grade: "A" }] },
      { id: "2", like_rubric: rubricA, like_grades: [{ vector: "Company Stage", grade: "B" }] },
      { id: "3", like_rubric: rubricB, like_grades: [{ vector: "Employment Type", grade: "X" }] },
      { id: "4", like_grades: [{ vector: "Fit", grade: "C" }] },
      { id: "5" },
    ]
    const groups = groupJobsByAlignedRubric(jobs, "like_grades")
    expect(groups).toHaveLength(4)
    expect(groups[0].jobs.map(j => j.id)).toEqual(["1", "2"])
    expect(groups[0].columnSourceJob.id).toBe("1")
    expect(groups[1].jobs.map(j => j.id)).toEqual(["3"])
    expect(groups[2].fingerprint.startsWith("grades:")).toBe(true)
    expect(groups[2].jobs.map(j => j.id)).toEqual(["4"])
    expect(groups[3].fingerprint).toBe("__empty__")
    expect(groups[3].jobs.map(j => j.id)).toEqual(["5"])
  })

  it("builds group columns from job-carried rubric not live artifacts", () => {
    const cols = buildJobListRubricColumnsForGroup({
      gradeKey: "like_grades",
      columnSourceJob: {
        like_rubric: [{ code: "ET", label: "Employment Type", importance: 8 }],
        like_grades: [{ vector: "Employment Type", grade: "X" }],
      },
    })
    expect(cols).toHaveLength(1)
    expect(cols[0].headerCode).toBe("ET")
    expect(cols[0].headerTooltip).toBe("Employment Type (8)")

    const fallback = buildJobListRubricColumnsForGroup({
      gradeKey: "like_grades",
      columnSourceJob: {
        like_grades: [{ vector: "Technical (TE)", grade: "D" }],
      },
    })
    expect(fallback[0].headerCode).toBe("Technical (TE)")
  })

  it("prefers phase score over latest_score", () => {
    expect(analysisTimeScoreForJob({ like_score: 4.5, latest_score: 9 }, "like_grades")).toBe(4.5)
    expect(analysisTimeScoreForJob({ latest_score: 9 }, "like_grades")).toBe(9)
    expect(analysisTimeScoreForJob({ latest_score: 2 }, "")).toBe(2)
    expect(analysisTimeScoreForJob({}, "like_grades")).toBeNull()
  })
})
