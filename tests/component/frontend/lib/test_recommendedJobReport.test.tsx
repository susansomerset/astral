import { render } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import {
  artifactHasContent,
  buildPhaseListGradeRow,
  buildPhaseSectionGradeConfidenceRow,
  formatPhaseScore,
  formatPhaseSectionScoreTitle,
  gradesForHeader,
  jobScoreBreakdownForGradesField,
  materialsPreviewVisible,
  primaryActionsForState,
  anyReportArtifactContent,
  artifactsTabPrimaryActions,
  isArtifactsBuildInProgress,
  printCoverVisible,
  printResumeVisible,
} from "../../../../src/ui/frontend/src/lib/recommendedJobReport"
import { STATE_UI_MANIFEST_FIXTURE } from "../fixtures/stateUiManifestFixture"

describe("recommendedJobReport — AST-581 materialsPreviewVisible", () => {
  it("returns true on CANDIDATE_REVIEW even when artifacts empty", () => {
    expect(materialsPreviewVisible("CANDIDATE_REVIEW", {})).toBe(true)
  })

  it("returns false on RECOMMENDED without artifact content", () => {
    expect(materialsPreviewVisible("RECOMMENDED", {})).toBe(false)
  })

  it("returns true on BUILD_ARTIFACTS when hydrated job_resume has text", () => {
    expect(
      materialsPreviewVisible("BUILD_ARTIFACTS", {
        job_resume: { professional_summary: "draft" },
      }),
    ).toBe(true)
    // AST-1593: resume_content alone is not job-resume SoT
    expect(
      materialsPreviewVisible("BUILD_ARTIFACTS", {
        resume_content: { professional_summary: "legacy" },
      }),
    ).toBe(false)
  })
})

describe("recommendedJobReport — AST-948 print helpers", () => {
  it("printResumeVisible follows hydrated job_resume via artifactHasContent", () => {
    expect(printResumeVisible({ job_resume: { professional_summary: "x" } })).toBe(true)
    expect(printResumeVisible({ job_resume: { professional_summary: "   " } })).toBe(false)
    expect(printResumeVisible({ resume_content: { professional_summary: "x" } })).toBe(false)
    expect(printResumeVisible({})).toBe(false)
  })

  it("printCoverVisible follows cover_letter via artifactHasContent", () => {
    expect(printCoverVisible({ cover_letter: { Letter: "Hello" } })).toBe(true)
    expect(printCoverVisible({ cover_letter: { Letter: "  " } })).toBe(false)
    expect(printCoverVisible({ resume_content: { professional_summary: "x" } })).toBe(false)
  })
})

describe("recommendedJobReport — AST-1100 pin-slot visibility", () => {
  it("artifactHasContent treats non-empty pin strings as content", () => {
    expect(artifactHasContent({ job_resume: "batch-1-response-aaaa" }, "job_resume")).toBe(true)
    expect(artifactHasContent({ job_resume: "   " }, "job_resume")).toBe(false)
    expect(artifactHasContent({ job_resume: { professional_summary: "x" } }, "job_resume")).toBe(true)
  })

  it("printResumeVisible accepts job_resume pin; resume_content is not SoT", () => {
    expect(printResumeVisible({ job_resume: "pin-id" })).toBe(true)
    expect(printResumeVisible({ resume_content: { professional_summary: "x" } })).toBe(false)
    expect(printResumeVisible({})).toBe(false)
  })

  it("materialsPreviewVisible uses remapped resume/cover checks", () => {
    expect(materialsPreviewVisible("RECOMMENDED", { job_resume: "pin-id" })).toBe(true)
    expect(materialsPreviewVisible("RECOMMENDED", { cover_letter: "pin-cover" })).toBe(true)
    expect(materialsPreviewVisible("RECOMMENDED", {})).toBe(false)
  })
})

describe("recommendedJobReport — AST-565", () => {
  it("primaryActionsForState reads manifest primary_actions_by_state", () => {
    const actions = primaryActionsForState(STATE_UI_MANIFEST_FIXTURE, "RECOMMENDED")
    expect(actions[0]?.action_key).toBe("generate_artifacts")
    expect(primaryActionsForState(STATE_UI_MANIFEST_FIXTURE, "CANDIDATE_REVIEW")[0]?.action_key).toBe("apply")
  })

  it("artifactHasContent detects non-empty artifact dicts", () => {
    expect(artifactHasContent({ resume_content: { professional_summary: "x" } }, "resume_content")).toBe(true)
    expect(artifactHasContent({ resume_content: { professional_summary: "   " } }, "resume_content")).toBe(false)
    expect(artifactHasContent({}, "resume_content")).toBe(false)
  })
})

describe("recommendedJobReport — AST-950 grade+confidence header row", () => {
  it("buildPhaseSectionGradeConfidenceRow paints from job-carried jd_rubric", () => {
    const grades = [{ vector: "Job Description (JD)", grade: "A", confidence: 4, reason: "ok" }]
    const job = {
      jd_grades: grades,
      jd_rubric: [{ code: "JD", label: "Job Description (JD)", importance: 1 }],
    }
    const { container } = render(
      <>{buildPhaseSectionGradeConfidenceRow(grades, job, "jd_grades")}</>,
    )
    expect(container.querySelector(".recommended-report-phase-grade-row")).toBeTruthy()
    expect(container.querySelector(".grade-dot.dot-a")).toHaveTextContent("A")
    expect(container.querySelector(".confidence-bullets")).toBeTruthy()
    expect(container.querySelectorAll(".confidence-bullet--on").length).toBe(4)
  })

  it("buildPhaseSectionGradeConfidenceRow falls back to grades-only when jd_rubric absent", () => {
    const grades = [{ vector: "X", grade: "B", confidence: 2 }]
    const job = { jd_grades: grades }
    const { container } = render(
      <>{buildPhaseSectionGradeConfidenceRow(grades, job, "jd_grades")}</>,
    )
    expect(container.querySelector(".grade-dot.dot-b")).toHaveTextContent("B")
    expect(container.querySelectorAll(".confidence-bullet--on").length).toBe(2)
  })

  // AST-1328 bug-repro: meteorite mismatch — header follows job-carried *_rubric, not live artifact underlap.
  it("AST-1328: header shows every job-carried vector when live jobdesc_rubric underlaps", () => {
    const grades = [
      { vector: "Embedded/Firmware/Hardware Domain", grade: "A", confidence: 5 },
      { vector: "Quality Check", grade: "B", confidence: 4 },
    ]
    const job = {
      jd_grades: grades,
      jd_rubric: [
        { code: "EFW", label: "Embedded/Firmware/Hardware Domain", importance: 1, grade_descriptions: [] },
        { code: "QC", label: "Quality Check", importance: 5, grade_descriptions: [] },
      ],
      // Decoy — helper must not read live candidate artifacts (AST-1327).
      artifacts: {
        jobdesc_rubric: [{ code: "QC", label: "Quality Check", importance: 5 }],
      },
    }
    const { container } = render(
      <>{buildPhaseSectionGradeConfidenceRow(grades, job, "jd_grades")}</>,
    )
    expect(container.querySelectorAll(".recommended-report-phase-grade-cell").length).toBe(2)
    expect(container.querySelector(".grade-dot.dot-a")).toBeTruthy()
    expect(container.querySelector(".grade-dot.dot-b")).toBeTruthy()
  })

  // AST-1771: same fixture — header left-to-right is importance then grade (QC/B before EFW/A).
  it("AST-1771: header grade dots order QC before EFW with vector-prefixed tooltip", () => {
    const grades = [
      { vector: "Embedded/Firmware/Hardware Domain", grade: "A", confidence: 5, reason: "fit" },
      { vector: "Quality Check", grade: "B", confidence: 4, reason: "ok" },
    ]
    const job = {
      jd_grades: grades,
      jd_rubric: [
        { code: "EFW", label: "Embedded/Firmware/Hardware Domain", importance: 1, grade_descriptions: [] },
        { code: "QC", label: "Quality Check", importance: 5, grade_descriptions: [] },
      ],
    }
    const { container } = render(
      <>{buildPhaseSectionGradeConfidenceRow(grades, job, "jd_grades")}</>,
    )
    const cells = container.querySelectorAll(".recommended-report-phase-grade-cell")
    expect(cells.length).toBe(2)
    expect(cells[0].querySelector(".grade-dot.dot-b")).toBeTruthy()
    expect(cells[1].querySelector(".grade-dot.dot-a")).toBeTruthy()
    const firstTitle = cells[0].querySelector(".grade-dot")?.getAttribute("title") ?? ""
    expect(firstTitle.startsWith("Quality Check")).toBe(true)
  })

  it("gradesForHeader normalizes array and object maps", () => {
    expect(gradesForHeader([{ vector: "JD", grade: "A", confidence: 3 }])).toEqual([
      { vector: "JD", grade: "A", confidence: 3, reason: undefined },
    ])
    expect(gradesForHeader({ TE: "B" })).toEqual([{ vector: "TE", grade: "B" }])
    expect(gradesForHeader(null)).toEqual([])
  })
})
describe("recommendedJobReport — AST-951 Artifacts helpers", () => {
  it("isArtifactsBuildInProgress covers base and hop, not ERROR", () => {
    expect(isArtifactsBuildInProgress("BUILD_ARTIFACTS")).toBe(true)
    expect(isArtifactsBuildInProgress("BUILD_ARTIFACTS.draft_job_resume")).toBe(true)
    expect(isArtifactsBuildInProgress("ERROR_ANTICIPATE_SCAN")).toBe(false)
    expect(isArtifactsBuildInProgress("RECOMMENDED")).toBe(false)
  })

  it("artifactsTabPrimaryActions falls back to BUILD_ARTIFACTS for hops", () => {
    const hop = artifactsTabPrimaryActions(STATE_UI_MANIFEST_FIXTURE, "BUILD_ARTIFACTS.x")
    expect(hop[0]?.action_key).toBe("cancel_build")
    const rec = artifactsTabPrimaryActions(STATE_UI_MANIFEST_FIXTURE, "RECOMMENDED")
    expect(rec[0]?.action_key).toBe("generate_artifacts")
    expect(artifactsTabPrimaryActions(STATE_UI_MANIFEST_FIXTURE, "CANDIDATE_REVIEW")).toEqual([])
  })

  it("anyReportArtifactContent gates on report_artifact_tabs keys", () => {
    const tabs = STATE_UI_MANIFEST_FIXTURE.jobs.recommended.report_artifact_tabs!
    expect(anyReportArtifactContent({}, tabs)).toBe(false)
    expect(
      anyReportArtifactContent({ job_resume: { professional_summary: "x" } }, tabs),
    ).toBe(true)
  })
})

describe("recommendedJobReport — AST-1348 phase score header helpers", () => {
  const tpl =
    STATE_UI_MANIFEST_FIXTURE.jobs.recommended.phase_score_header_title_template!

  it("jobScoreBreakdownForGradesField reads top-level and job_data", () => {
    const trio = { earned: 137.4, possible: 150.2, max: 320.9 }
    expect(
      jobScoreBreakdownForGradesField({ jd_score_breakdown: trio }, "jd_grades"),
    ).toEqual(trio)
    expect(
      jobScoreBreakdownForGradesField(
        { job_data: { do_score_breakdown: trio } },
        "do_grades",
      ),
    ).toEqual(trio)
    expect(jobScoreBreakdownForGradesField({}, "jd_grades")).toBeNull()
    expect(jobScoreBreakdownForGradesField({ jd_score_breakdown: trio }, "jd_score")).toBeNull()
    expect(
      jobScoreBreakdownForGradesField(
        { jd_score_breakdown: { earned: 1, possible: "x", max: 3 } },
        "jd_grades",
      ),
    ).toBeNull()
  })

  it("formatPhaseSectionScoreTitle rounds and fills template", () => {
    expect(
      formatPhaseSectionScoreTitle(
        "JD Analysis",
        { earned: 137.4, possible: 150.2, max: 320.9 },
        tpl,
      ),
    ).toBe("JD Analysis - score: 137 out of 150 possible (321 max total)")
    expect(
      formatPhaseSectionScoreTitle(
        "DO Analysis",
        { earned: 0, possible: 0, max: 300 },
        "",
      ),
    ).toBe("DO Analysis - score: 0 out of 0 possible (300 max total)")
  })
})

describe("recommendedJobReport — AST-1874 list score in phase header", () => {
  const tpl =
    STATE_UI_MANIFEST_FIXTURE.jobs.recommended.phase_score_header_title_template!
  const trio = { earned: 42, possible: 50, max: 60 }

  it("formatPhaseScore: finite number → one decimal; anything else → em dash", () => {
    expect(formatPhaseScore(3.66)).toBe("3.7")
    expect(formatPhaseScore(0)).toBe("0.0")
    for (const v of [null, undefined, "3.7", Number.NaN, Number.POSITIVE_INFINITY]) {
      expect(formatPhaseScore(v)).toBe("\u2014")
    }
  })

  it("fills {score} with the one-decimal list score (AC3)", () => {
    expect(tpl).toContain(" - {score}")
    expect(formatPhaseSectionScoreTitle("JD Analysis", trio, tpl, 3.66)).toBe(
      "JD Analysis - 3.7 - score: 42 out of 50 possible (60 max total)",
    )
  })

  it("absent / non-finite score drops the whole ' - {score}' segment — no em dash, no empty dash", () => {
    for (const s of [undefined, null, "3.7", Number.NaN]) {
      const out = formatPhaseSectionScoreTitle("JD Analysis", trio, tpl, s)
      expect(out).toBe("JD Analysis - score: 42 out of 50 possible (60 max total)")
      expect(out).not.toContain("\u2014")
    }
  })

  it("no-template fallback carries the same score segment rule", () => {
    expect(formatPhaseSectionScoreTitle("DO Analysis", trio, "", 8.5)).toBe(
      "DO Analysis - 8.5 - score: 42 out of 50 possible (60 max total)",
    )
    expect(formatPhaseSectionScoreTitle("DO Analysis", trio, "  ")).toBe(
      "DO Analysis - score: 42 out of 50 possible (60 max total)",
    )
  })
})

describe("recommendedJobReport — AST-1968 letterless list grade row", () => {
  // AST-1771 fixture: importance-then-grade order puts QC/B before EFW/A.
  const grades = [
    { vector: "Embedded/Firmware/Hardware Domain", grade: "A", confidence: 5, reason: "fit" },
    { vector: "Quality Check", grade: "B", confidence: 4, reason: "ok" },
  ]
  const job = {
    jd_grades: grades,
    jd_rubric: [
      { code: "EFW", label: "Embedded/Firmware/Hardware Domain", importance: 1, grade_descriptions: [] },
      { code: "QC", label: "Quality Check", importance: 5, grade_descriptions: [] },
    ],
  }
  const dotSig = (root: ParentNode) =>
    [...root.querySelectorAll(".grade-dot")].map(d => ({
      colour: [...d.classList].find(c => c.startsWith("dot-")),
      title: d.getAttribute("title"),
    }))

  it("AC10/AC11: same circles, colours, order and tooltips as the modal row; no letters, no confidence", () => {
    const list = render(<>{buildPhaseListGradeRow(job, "jd_grades")}</>).container
    const modal = render(<>{buildPhaseSectionGradeConfidenceRow(grades, job, "jd_grades")}</>).container
    expect(list.querySelector(".recommended-list-phase-grade-row")).toBeTruthy()
    expect(dotSig(list)).toEqual(dotSig(modal))
    expect(dotSig(list).map(d => d.colour)).toEqual(["dot-b", "dot-a"])
    for (const dot of list.querySelectorAll(".grade-dot")) {
      expect(dot).toHaveClass("grade-dot-letterless")
      expect(dot.textContent).toBe("")
    }
    expect(list.querySelector(".confidence-bullets")).toBeNull()
  })

  it("modal row keeps letters and confidence after the shared-helper refactor", () => {
    const modal = render(<>{buildPhaseSectionGradeConfidenceRow(grades, job, "jd_grades")}</>).container
    const dots = [...modal.querySelectorAll(".grade-dot")]
    expect(dots.map(d => d.textContent)).toEqual(["B", "A"])
    expect(modal.querySelector(".grade-dot-letterless")).toBeNull()
    expect(modal.querySelectorAll(".confidence-bullets")).toHaveLength(2)
  })

  // Columns come from top-level fields (list API flattens); grade values follow jobGradesForField
  // (job_data first) — same source as the modal's renderAnalysisMetadata.
  it("grade values prefer job_data via jobGradesForField; null with no grades", () => {
    const both = {
      jd_grades: [{ vector: "X", grade: "A", confidence: 1 }],
      job_data: { jd_grades: [{ vector: "X", grade: "C", confidence: 1 }] },
    }
    const { container } = render(<>{buildPhaseListGradeRow(both, "jd_grades")}</>)
    expect(container.querySelector(".grade-dot.dot-c")).toBeTruthy()
    expect(container.querySelector(".grade-dot.dot-a")).toBeNull()
    expect(buildPhaseListGradeRow({}, "jd_grades")).toBeNull()
  })
})
