import { screen, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"
import RecommendedJobReportHeader from "../../../../src/ui/frontend/src/components/RecommendedJobReportHeader"
import { renderWithProviders } from "../test-utils"
import { CUT_TITLE, EDGE_TITLE, LONG_TITLE, expectFullTitleTooltip } from "../pages/job-title-cell"

const base = {
  jobTitle: "Analyst",
  jobLink: null as string | null,
  companyName: "Globex",
  companyWebsite: null as string | null,
}

describe("RecommendedJobReportHeader — AST-2233 triage chrome", () => {
  it("AC1: no Copy controls or labels in the header", () => {
    renderWithProviders(
      <RecommendedJobReportHeader
        {...base}
        onSkip={() => {}}
        onApplied={() => {}}
        onGenerateArtifacts={() => {}}
      />,
    )
    for (const name of [
      "Copy Job Link",
      "Copy Job JSON",
      "Copy Application Email",
      "Copy LinkedIn Profile",
    ]) {
      expect(screen.queryByRole("button", { name })).not.toBeInTheDocument()
    }
    expect(document.querySelector(".recommended-report-links")).toBeNull()
  })

  it("AC2: Skip / Applied / Generate in actions; no Print Resume/Cover", async () => {
    const onSkip = vi.fn()
    const onApplied = vi.fn()
    const onGenerate = vi.fn()
    renderWithProviders(
      <RecommendedJobReportHeader
        {...base}
        onSkip={onSkip}
        onApplied={onApplied}
        onGenerateArtifacts={onGenerate}
      />,
    )
    expect(screen.queryByRole("button", { name: "Print Resume" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Print Cover Letter" })).not.toBeInTheDocument()
    const actions = document.querySelector(".recommended-report-header-actions") as HTMLElement
    const buttons = within(actions).getAllByRole("button")
    expect(buttons.map(b => b.textContent)).toEqual([
      "Skip This Job",
      "Applied to this Job",
      "Generate Artifacts",
    ])
    await userEvent.click(within(actions).getByRole("button", { name: "Skip This Job" }))
    await userEvent.click(within(actions).getByRole("button", { name: "Applied to this Job" }))
    await userEvent.click(within(actions).getByRole("button", { name: "Generate Artifacts" }))
    expect(onSkip).toHaveBeenCalledTimes(1)
    expect(onApplied).toHaveBeenCalledTimes(1)
    expect(onGenerate).toHaveBeenCalledTimes(1)
  })

  it("actions row omitted when no callbacks; busy props disable buttons", () => {
    const { rerender } = renderWithProviders(<RecommendedJobReportHeader {...base} />)
    expect(document.querySelector(".recommended-report-header-actions")).toBeNull()
    rerender(
      <RecommendedJobReportHeader
        {...base}
        onSkip={() => {}}
        skipBusy
        onApplied={() => {}}
        appliedBusy
        onGenerateArtifacts={() => {}}
        generateBusy
      />,
    )
    const actions = document.querySelector(".recommended-report-header-actions") as HTMLElement
    expect(within(actions).getByRole("button", { name: "Skip This Job" })).toBeDisabled()
    expect(within(actions).getByRole("button", { name: "Applied to this Job" })).toBeDisabled()
    expect(within(actions).getByRole("button", { name: "Generate Artifacts" })).toBeDisabled()
  })

  it("website is its own line under the job link; company name is plain (not the website <a>)", () => {
    renderWithProviders(
      <RecommendedJobReportHeader
        {...base}
        jobLink="https://jobs.example/listing"
        companyWebsite="https://globex.example"
        companyName="Globex Corp"
        discoveredAt="2026-01-15T12:00:00Z"
      />,
    )
    const website = screen.getByRole("link", { name: "https://globex.example" })
    expect(website).toHaveAttribute("href", "https://globex.example")
    expect(website).toHaveAttribute("target", "_blank")
    expect(website.closest(".recommended-report-website-line")).not.toBeNull()
    const company = document.querySelector(".recommended-report-company") as HTMLElement
    expect(company).toHaveTextContent("Globex Corp")
    expect(company.closest("a")).toBeNull()
    expect(document.querySelector(".recommended-report-company-date")!.textContent).toMatch(/ · /)
  })

  it("date strip shows discovered + recommended; applied only when appliedAt formats", () => {
    const { rerender } = renderWithProviders(
      <RecommendedJobReportHeader
        {...base}
        discoveredAt="2026-01-15T12:00:00Z"
        recommendedAt="2026-01-20T08:00:00Z"
      />,
    )
    const strip = document.querySelector(".recommended-report-date-strip") as HTMLElement
    expect(within(strip).getByText(/Date discovered/)).toBeInTheDocument()
    expect(within(strip).getByText(/Date recommended/)).toBeInTheDocument()
    expect(within(strip).queryByText(/Date applied/)).not.toBeInTheDocument()
    rerender(
      <RecommendedJobReportHeader
        {...base}
        discoveredAt="2026-01-15T12:00:00Z"
        recommendedAt="2026-01-20T08:00:00Z"
        appliedAt="2026-02-01T10:00:00Z"
      />,
    )
    expect(
      within(document.querySelector(".recommended-report-date-strip") as HTMLElement).getByText(
        /Date applied/,
      ),
    ).toBeInTheDocument()
  })
})

describe("RecommendedJobReportHeader — AST-1695 listing title", () => {
  it("http(s) jobLink → linked on the job-link line (title stays plain); null → plain span", () => {
    const { rerender } = renderWithProviders(
      <RecommendedJobReportHeader {...base} jobLink="https://jobs.example/listing" />,
    )
    expect(screen.queryByRole("link", { name: "Analyst" })).not.toBeInTheDocument()
    expect(screen.getByRole("link", { name: "https://jobs.example/listing" })).toHaveAttribute(
      "href",
      "https://jobs.example/listing",
    )
    rerender(<RecommendedJobReportHeader {...base} jobLink={null} />)
    expect(screen.queryByRole("link", { name: "Analyst" })).not.toBeInTheDocument()
    expect(document.querySelector(".recommended-report-title")).toHaveTextContent("Analyst")
  })
})

describe("RecommendedJobReportHeader — AST-1704 http(s)-only href", () => {
  it("uses http jobLink as the job-link line href (AST-1873: not the title)", () => {
    renderWithProviders(<RecommendedJobReportHeader {...base} jobLink="https://jobs.example/apply" />)
    expect(screen.queryByRole("link", { name: "Analyst" })).not.toBeInTheDocument()
    const line = document.querySelector(".recommended-report-job-link-text") as HTMLElement
    expect(within(line).getByRole("link", { name: "https://jobs.example/apply" })).toHaveAttribute(
      "href",
      "https://jobs.example/apply",
    )
  })

  it("shows non-http jobLink as text without title href", () => {
    const crumb = "From:a@x.com 9/17 14:05 Eastern To:b@y.com"
    renderWithProviders(<RecommendedJobReportHeader {...base} jobLink={crumb} />)
    expect(screen.queryByRole("link", { name: "Analyst" })).not.toBeInTheDocument()
    expect(screen.getByText("Analyst")).toHaveClass("recommended-report-title")
    expect(screen.getByText(crumb)).toHaveClass("recommended-report-job-link-text")
  })
})

describe("RecommendedJobReportHeader — AST-1873 title row / job-link line (revised AST-2233)", () => {
  it("http href → title plain, line is <a target=_blank> directly below the title", () => {
    renderWithProviders(<RecommendedJobReportHeader {...base} jobLink="https://x.test/j" />)
    const title = document.querySelector(".recommended-report-title") as HTMLElement
    expect(title.closest("a")).toBeNull()
    const a = screen.getByRole("link", { name: "https://x.test/j" })
    expect(a).toHaveAttribute("href", "https://x.test/j")
    expect(a).toHaveAttribute("target", "_blank")
    expect(title.nextElementSibling).toHaveClass("recommended-report-job-link-text")
  })

  it("jobLinkText with no http href → plain text line (no <a>)", () => {
    renderWithProviders(
      <RecommendedJobReportHeader {...base} jobLink={null} jobLinkText="meteorite-123" />,
    )
    const line = screen.getByText("meteorite-123")
    expect(line).toHaveClass("recommended-report-job-link-text")
    expect(line.querySelector("a")).toBeNull()
  })

  it("jobLinkText is shown while an http jobLink stays the href", () => {
    renderWithProviders(
      <RecommendedJobReportHeader {...base} jobLink="https://x.test/j" jobLinkText="Listing" />,
    )
    expect(screen.getByRole("link", { name: "Listing" })).toHaveAttribute("href", "https://x.test/j")
  })

  it("neither jobLink nor jobLinkText → no job-link line", () => {
    renderWithProviders(<RecommendedJobReportHeader {...base} jobLink={null} jobLinkText={null} />)
    expect(document.querySelector(".recommended-report-job-link-text")).toBeNull()
  })
})

// AST-1983 AC 5: .recommended-report-title renders through JobTitleText.
describe("RecommendedJobReportHeader — AST-1983 title cut", () => {
  it("long title: first 50 chars + … with the full-title tooltip, outside the header", async () => {
    renderWithProviders(<RecommendedJobReportHeader {...base} jobTitle={LONG_TITLE} />)
    const title = document.querySelector<HTMLElement>(".recommended-report-title")!
    expect(title.textContent).toBe(CUT_TITLE)
    await expectFullTitleTooltip(within(title).getByText(CUT_TITLE), title.closest(".recommended-report-header-row")!)
  })

  it("50-char title: shown exactly, no tooltip, no title attribute", async () => {
    renderWithProviders(<RecommendedJobReportHeader {...base} jobTitle={EDGE_TITLE} />)
    const title = document.querySelector<HTMLElement>(".recommended-report-title")!
    expect(title.textContent).toBe(EDGE_TITLE)
    expect(title.querySelector("[title]")).toBeNull()
    await userEvent.hover(title)
    expect(screen.queryByRole("tooltip")).toBeNull()
  })
})
