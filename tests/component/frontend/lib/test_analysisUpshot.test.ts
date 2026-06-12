import { describe, expect, it } from "vitest"
import { parseAnalysisUpshot, snakeCaseToTitle } from "../../../../src/ui/frontend/src/lib/analysisUpshot"

describe("analysisUpshot — AST-481", () => {
  const valid = () => ({
    take_get: "a",
    take_do: "",
    take_like: "",
    take_jd: "",
    whole_jd_upshot: "",
    segment_upshots: [],
    candidate_questions: [],
    caveats: [],
  })

  it("snakeCaseToTitle collapses underscores", () => {
    expect(snakeCaseToTitle("take_get")).toBe("Take Get")
    expect(snakeCaseToTitle("whole_jd_upshot")).toBe("Whole Jd Upshot")
  })

  it("parseAnalysisUpshot returns null for non-objects and wrong arrays", () => {
    expect(parseAnalysisUpshot(null)).toBeNull()
    expect(parseAnalysisUpshot("x")).toBeNull()
    expect(parseAnalysisUpshot([])).toBeNull()
    expect(
      parseAnalysisUpshot({
        ...valid(),
        segment_upshots: [{}],
      })
    ).toBeNull()
  })

  it("parseAnalysisUpshot rejects headline-empty payloads as null", () => {
    expect(
      parseAnalysisUpshot({
        take_get: "",
        take_do: "   ",
        take_like: "",
        take_jd: "",
        whole_jd_upshot: "",
        segment_upshots: [],
        candidate_questions: [],
        caveats: [],
      })
    ).toBeNull()
  })

  it("parseAnalysisUpshot coerces missing take_jd for legacy upshots (AST-561)", () => {
    expect(
      parseAnalysisUpshot({
        ...valid(),
        take_jd: undefined,
      })
    ).toMatchObject({ take_jd: "", take_get: "a" })
  })

  it("parseAnalysisUpshot accepts segment or question-only substance", () => {
    expect(
      parseAnalysisUpshot({
        take_get: "",
        take_do: "",
        take_like: "",
        take_jd: "",
        whole_jd_upshot: "",
        segment_upshots: [{ segment_key: "k", upshot: "Seg" }],
        candidate_questions: [],
        caveats: [],
      })
    ).toMatchObject({ segment_upshots: [{ segment_key: "k", upshot: "Seg" }] })
    expect(
      parseAnalysisUpshot({
        ...valid(),
        take_get: "",
        candidate_questions: [{ text: "Ask?" }],
      })
    ).toMatchObject({ candidate_questions: [{ text: "Ask?" }] })
  })
})
