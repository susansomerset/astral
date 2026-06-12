import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"
import CandidateJobRowActions from "../../../../src/ui/frontend/src/components/CandidateJobRowActions"

describe("CandidateJobRowActions", () => {
  it("renders skip and view analysis for review-like states", async () => {
    const onSkip = vi.fn()
    const onView = vi.fn()
    render(
      <CandidateJobRowActions
        state="CANDIDATE_REVIEW"
        onSkip={onSkip}
        onViewAnalysis={onView}
      />,
    )
    await userEvent.click(screen.getByRole("button", { name: "Skip" }))
    await userEvent.click(screen.getByRole("button", { name: "View Job Analysis" }))
    expect(onSkip).toHaveBeenCalledOnce()
    expect(onView).toHaveBeenCalledOnce()
  })

  it("renders resurrect for CANDIDATE_SKIPPED", async () => {
    const onResurrect = vi.fn()
    render(<CandidateJobRowActions state="CANDIDATE_SKIPPED" onResurrect={onResurrect} />)
    await userEvent.click(screen.getByRole("button", { name: "Resurrect" }))
    expect(onResurrect).toHaveBeenCalledOnce()
  })
})
