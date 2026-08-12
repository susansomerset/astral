import { render } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import {
  artifactHasContent,
  buildPhaseSectionGradeConfidenceRow,
  gradesForHeader,
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

  it("returns true on BUILD_ARTIFACTS when job_resume or resume_content has text", () => {
    expect(
      materialsPreviewVisible("BUILD_ARTIFACTS", {
        job_resume: { professional_summary: "draft" },
      }),
    ).toBe(true)
    expect(
      materialsPreviewVisible("BUILD_ARTIFACTS", {
        resume_content: { professional_summary: "legacy" },
      }),
    ).toBe(true)
  })
})

describe("recommendedJobReport — AST-948 print helpers", () => {
  it("printResumeVisible follows resume_content via artifactHasContent", () => {
    expect(printResumeVisible({ resume_content: { professional_summary: "x" } })).toBe(true)
    expect(printResumeVisible({ resume_content: { professional_summary: "   " } })).toBe(false)
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

  it("printResumeVisible accepts job_resume pin or legacy resume_content", () => {
    expect(printResumeVisible({ job_resume: "pin-id" })).toBe(true)
    expect(printResumeVisible({ resume_content: { professional_summary: "x" } })).toBe(true)
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
    expect(isArtifactsBuildInProgress("ERROR_BUILD_ARTIFACTS")).toBe(false)
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
