import { describe, expect, it } from "vitest"
import {
  artifactHasContent,
  materialsPreviewVisible,
  primaryActionsForState,
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

  it("returns true on BUILD_ARTIFACTS when resume_content has text", () => {
    expect(
      materialsPreviewVisible("BUILD_ARTIFACTS", {
        resume_content: { professional_summary: "draft" },
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
