import { readFileSync } from "node:fs"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"
import CandidateJobRowActions from "../../../../src/ui/frontend/src/components/CandidateJobRowActions"

const appCss = readFileSync(
  resolve(dirname(fileURLToPath(import.meta.url)), "../../../../src/ui/frontend/src/App.css"),
  "utf-8",
)

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

describe("CandidateJobRowActions — AST-1302 icon-control", () => {
  it("uses single initials and icon-control on review-like and skipped rows", () => {
    const { rerender } = render(
      <CandidateJobRowActions state="CANDIDATE_REVIEW" onSkip={() => {}} onViewAnalysis={() => {}} />,
    )
    const skip = screen.getByRole("button", { name: "Skip" })
    const view = screen.getByRole("button", { name: "View Job Analysis" })
    expect(skip).toHaveClass("icon-control")
    expect(skip).toHaveTextContent("S")
    expect(view).toHaveClass("icon-control")
    expect(view).toHaveTextContent("J")
    expect(screen.queryByText("Sk")).not.toBeInTheDocument()
    expect(screen.queryByText("Jr")).not.toBeInTheDocument()

    rerender(<CandidateJobRowActions state="CANDIDATE_SKIPPED" onResurrect={() => {}} />)
    const resurrect = screen.getByRole("button", { name: "Resurrect" })
    expect(resurrect).toHaveClass("icon-control")
    expect(resurrect).toHaveTextContent("R")
  })

  it("uses single initials and icon-control on post-applied rows", async () => {
    const onAction = vi.fn()
    render(<CandidateJobRowActions state="CANDIDATE_APPLIED" onAction={onAction} />)
    const reapply = screen.getByRole("button", { name: "Reapply" })
    const interview = screen.getByRole("button", { name: "Interview" })
    const rejected = screen.getByRole("button", { name: "Rejected" })
    const ghosted = screen.getByRole("button", { name: "Ghosted" })
    expect(reapply).toHaveClass("icon-control")
    expect(reapply).toHaveTextContent("R")
    expect(interview).toHaveClass("icon-control")
    expect(interview).toHaveTextContent("I")
    expect(rejected).toHaveClass("icon-control")
    expect(rejected).toHaveTextContent("X")
    expect(ghosted).toHaveClass("icon-control")
    expect(ghosted).toHaveTextContent("G")
    await userEvent.click(reapply)
    await userEvent.click(interview)
    await userEvent.click(rejected)
    await userEvent.click(ghosted)
    expect(onAction.mock.calls.map(c => c[0])).toEqual(["review", "interview", "rejected", "ghosted"])
  })

  it("retires leftover icon families in App.css", () => {
    expect(appCss).toMatch(/\.icon-control\s*\{/)
    expect(appCss).toMatch(/\.collapsible-panel-header \.icon-control\s*\{/)
    expect(appCss).not.toMatch(/\.job-list-icon-btn\s*\{/)
    expect(appCss).not.toMatch(/\.list-page-edit-btn\s*\{/)
    expect(appCss).not.toMatch(/\.modal-close\s*\{/)
    expect(appCss).not.toMatch(/\.collapsible-panel-chevron-btn\s*\{/)
  })
})
