import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"
import RecommendedJobReportHeader from "../../../../src/ui/frontend/src/components/RecommendedJobReportHeader"
import { renderWithProviders } from "../test-utils"

const base = {
  jobTitle: "Analyst",
  jobLink: null as string | null,
  companyName: "Globex",
  companyWebsite: null as string | null,
  showPrintResume: false,
  showPrintCover: false,
}

describe("RecommendedJobReportHeader — AST-1421 snapshot Copy", () => {
  it("shows Copy when email and LinkedIn are absent", () => {
    renderWithProviders(
      <RecommendedJobReportHeader
        {...base}
        applicationEmail={null}
        linkedInUrl={null}
        onCopySnapshot={() => {}}
      />,
    )
    expect(screen.getByRole("button", { name: /^Copy$/ })).toHaveClass("btn", "secondary")
    expect(screen.queryByRole("button", { name: "Copy Application Email" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Copy LinkedIn Profile" })).not.toBeInTheDocument()
  })

  it("keeps email and LinkedIn copy controls beside diagnostic Copy", async () => {
    const onSnap = vi.fn()
    const onEmail = vi.fn()
    const onLi = vi.fn()
    renderWithProviders(
      <RecommendedJobReportHeader
        {...base}
        applicationEmail="ada@example.com"
        linkedInUrl="https://linkedin.com/in/ada"
        copyFeedback="Copied"
        onCopySnapshot={onSnap}
        onCopyApplicationEmail={onEmail}
        onCopyLinkedIn={onLi}
      />,
    )
    await userEvent.click(screen.getByRole("button", { name: /^Copy$/ }))
    expect(onSnap).toHaveBeenCalledTimes(1)
    expect(screen.getByRole("button", { name: "Copy Application Email" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Copy LinkedIn Profile" })).toBeInTheDocument()
    expect(screen.getByText("Copied")).toHaveClass("recommended-report-copy-feedback")
    await userEvent.click(screen.getByRole("button", { name: "Copy Application Email" }))
    expect(onEmail).toHaveBeenCalledTimes(1)
  })

  it("shows Copied and disables while copying", () => {
    const { rerender } = renderWithProviders(
      <RecommendedJobReportHeader
        {...base}
        applicationEmail={null}
        linkedInUrl={null}
        onCopySnapshot={() => {}}
        snapshotCopied
        snapshotCopying
      />,
    )
    const btn = screen.getByRole("button", { name: /^Copied$/ })
    expect(btn).toBeDisabled()
    rerender(
      <RecommendedJobReportHeader
        {...base}
        applicationEmail={null}
        linkedInUrl={null}
        onCopySnapshot={() => {}}
        snapshotCopied={false}
        snapshotCopying={false}
      />,
    )
    expect(screen.getByRole("button", { name: /^Copy$/ })).toBeEnabled()
  })
})
