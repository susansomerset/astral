import { screen, within } from "@testing-library/react"
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
  it("shows Copy Job JSON when email and LinkedIn are absent", () => {
    renderWithProviders(
      <RecommendedJobReportHeader
        {...base}
        applicationEmail={null}
        linkedInUrl={null}
        onCopySnapshot={() => {}}
      />,
    )
    expect(screen.getByRole("button", { name: "Copy Job JSON" })).toHaveClass("btn", "secondary")
    expect(screen.queryByRole("button", { name: "Copy Application Email" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Copy LinkedIn Profile" })).not.toBeInTheDocument()
  })

  it("keeps email and LinkedIn copy controls beside Copy Job JSON", async () => {
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
    await userEvent.click(screen.getByRole("button", { name: "Copy Job JSON" }))
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
    expect(screen.getByRole("button", { name: "Copy Job JSON" })).toBeEnabled()
  })
})

describe("RecommendedJobReportHeader — AST-1695 listing title", () => {
  it("http(s) jobLink → linked on the job-link line (title stays plain); null → plain span", () => {
    // AST-1873: title is never an <a>; the listing href moves to the small line below it.
    const { rerender } = renderWithProviders(
      <RecommendedJobReportHeader
        {...base}
        jobLink="https://jobs.example/listing"
        applicationEmail={null}
        linkedInUrl={null}
      />,
    )
    expect(screen.queryByRole("link", { name: "Analyst" })).not.toBeInTheDocument()
    expect(screen.getByRole("link", { name: "https://jobs.example/listing" })).toHaveAttribute(
      "href",
      "https://jobs.example/listing",
    )
    rerender(
      <RecommendedJobReportHeader
        {...base}
        jobLink={null}
        applicationEmail={null}
        linkedInUrl={null}
      />,
    )
    expect(screen.queryByRole("link", { name: "Analyst" })).not.toBeInTheDocument()
    expect(document.querySelector(".recommended-report-title")).toHaveTextContent("Analyst")
  })
})

describe("RecommendedJobReportHeader — AST-1696 Copy Link", () => {
  it("shows Copy Job Link alone when snapshot/email/LinkedIn are absent", () => {
    renderWithProviders(
      <RecommendedJobReportHeader
        {...base}
        applicationEmail={null}
        linkedInUrl={null}
        onCopyDetailLink={() => {}}
      />,
    )
    expect(screen.getByRole("button", { name: "Copy Job Link" })).toHaveClass("btn", "secondary")
    expect(screen.queryByRole("button", { name: "Copy Job JSON" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Copy Application Email" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Copy LinkedIn Profile" })).not.toBeInTheDocument()
  })

  it("keeps Copy Job JSON, email, and LinkedIn beside Copy Job Link", async () => {
    const onLink = vi.fn()
    const onSnap = vi.fn()
    const onEmail = vi.fn()
    const onLi = vi.fn()
    renderWithProviders(
      <RecommendedJobReportHeader
        {...base}
        applicationEmail="ada@example.com"
        linkedInUrl="https://linkedin.com/in/ada"
        onCopyDetailLink={onLink}
        onCopySnapshot={onSnap}
        onCopyApplicationEmail={onEmail}
        onCopyLinkedIn={onLi}
      />,
    )
    const links = document.querySelector(".recommended-report-links") as HTMLElement
    await userEvent.click(within(links).getByRole("button", { name: "Copy Job Link" }))
    expect(onLink).toHaveBeenCalledTimes(1)
    expect(within(links).getByRole("button", { name: "Copy Job JSON" })).toBeInTheDocument()
    expect(within(links).getByRole("button", { name: "Copy Application Email" })).toBeInTheDocument()
    expect(within(links).getByRole("button", { name: "Copy LinkedIn Profile" })).toBeInTheDocument()
  })

  it("shows Copied on the link control when detailLinkCopied", () => {
    const { rerender } = renderWithProviders(
      <RecommendedJobReportHeader
        {...base}
        applicationEmail={null}
        linkedInUrl={null}
        onCopyDetailLink={() => {}}
        detailLinkCopied
      />,
    )
    expect(screen.getByRole("button", { name: /^Copied$/ })).toHaveClass("btn", "secondary")
    rerender(
      <RecommendedJobReportHeader
        {...base}
        applicationEmail={null}
        linkedInUrl={null}
        onCopyDetailLink={() => {}}
        detailLinkCopied={false}
      />,
    )
    expect(screen.getByRole("button", { name: "Copy Job Link" })).toBeInTheDocument()
  })
})
describe("RecommendedJobReportHeader — AST-1704 http(s)-only href", () => {
  it("uses http jobLink as the job-link line href (AST-1873: not the title)", () => {
    renderWithProviders(
      <RecommendedJobReportHeader
        {...base}
        jobLink="https://jobs.example/apply"
        applicationEmail={null}
        linkedInUrl={null}
      />,
    )
    expect(screen.queryByRole("link", { name: "Analyst" })).not.toBeInTheDocument()
    const line = document.querySelector(".recommended-report-job-link-text") as HTMLElement
    expect(within(line).getByRole("link", { name: "https://jobs.example/apply" })).toHaveAttribute(
      "href",
      "https://jobs.example/apply",
    )
  })

  it("shows non-http jobLink as text without title href", () => {
    const crumb = "From:a@x.com 9/17 14:05 Eastern To:b@y.com"
    renderWithProviders(
      <RecommendedJobReportHeader
        {...base}
        jobLink={crumb}
        applicationEmail={null}
        linkedInUrl={null}
      />,
    )
    expect(screen.queryByRole("link", { name: "Analyst" })).not.toBeInTheDocument()
    expect(screen.getByText("Analyst")).toHaveClass("recommended-report-title")
    expect(screen.getByText(crumb)).toHaveClass("recommended-report-job-link-text")
  })
})

describe("RecommendedJobReportHeader — AST-1873 title row, job-link line, Skip", () => {
  const noContacts = { applicationEmail: null, linkedInUrl: null }

  // AC6: Skip renders only with onSkip, last among the row's buttons; busy disables it.
  it("Skip this Job is the last row button when onSkip is passed; absent otherwise", async () => {
    const onSkip = vi.fn()
    const { rerender } = renderWithProviders(
      <RecommendedJobReportHeader
        {...base}
        applicationEmail="ada@example.com"
        linkedInUrl="https://linkedin.com/in/ada"
        onCopyDetailLink={() => {}}
        onCopySnapshot={() => {}}
        onSkip={onSkip}
      />,
    )
    const row = document.querySelector(".recommended-report-links") as HTMLElement
    const buttons = within(row).getAllByRole("button")
    expect(buttons.map(b => b.textContent)).toEqual([
      "Copy Job Link", "Copy Job JSON", "Copy Application Email", "Copy LinkedIn Profile", "Skip this Job",
    ])
    expect(buttons.at(-1)).toHaveClass("btn", "secondary")
    await userEvent.click(buttons.at(-1)!)
    expect(onSkip).toHaveBeenCalledTimes(1)
    rerender(
      <RecommendedJobReportHeader {...base} {...noContacts} onCopyDetailLink={() => {}} onCopySnapshot={() => {}} />,
    )
    expect(screen.queryByRole("button", { name: "Skip this Job" })).not.toBeInTheDocument()
  })

  it("skipBusy disables Skip; row still renders when Skip is the only action", () => {
    renderWithProviders(<RecommendedJobReportHeader {...base} {...noContacts} onSkip={() => {}} skipBusy />)
    const row = document.querySelector(".recommended-report-links") as HTMLElement
    expect(within(row).getAllByRole("button")).toHaveLength(1)
    expect(within(row).getByRole("button", { name: "Skip this Job" })).toBeDisabled()
  })

  // AC8 (DOM half): buttons share the title's row container, not a sibling row below it.
  it("button row and title block are children of the same header row", () => {
    renderWithProviders(
      <RecommendedJobReportHeader {...base} {...noContacts} onCopySnapshot={() => {}} />,
    )
    const headerRow = document.querySelector(".recommended-report-header-row") as HTMLElement
    const title = headerRow.querySelector(".recommended-report-title-block .recommended-report-title")
    expect(title).toHaveTextContent("Analyst")
    expect(headerRow.querySelector(":scope > .recommended-report-links")).not.toBeNull()
    expect(headerRow.querySelector(":scope > .recommended-report-title-block")).not.toBeNull()
  })

  // AC9: title never linked; line shows http href as new-tab <a>, non-http text plain, nothing when absent.
  it("http href → title plain, line is <a target=_blank> directly below the title", () => {
    renderWithProviders(
      <RecommendedJobReportHeader {...base} {...noContacts} jobLink="https://x.test/j" />,
    )
    const title = document.querySelector(".recommended-report-title") as HTMLElement
    expect(title.closest("a")).toBeNull()
    const a = screen.getByRole("link", { name: "https://x.test/j" })
    expect(a).toHaveAttribute("href", "https://x.test/j")
    expect(a).toHaveAttribute("target", "_blank")
    // Order in the title block: title, then job-link line, then company.
    expect(title.nextElementSibling).toHaveClass("recommended-report-job-link-text")
  })

  it("jobLinkText with no http href → plain text line (no <a>)", () => {
    renderWithProviders(
      <RecommendedJobReportHeader {...base} {...noContacts} jobLink={null} jobLinkText="meteorite-123" />,
    )
    const line = screen.getByText("meteorite-123")
    expect(line).toHaveClass("recommended-report-job-link-text")
    expect(line.querySelector("a")).toBeNull()
  })

  it("jobLinkText is shown while an http jobLink stays the href", () => {
    renderWithProviders(
      <RecommendedJobReportHeader {...base} {...noContacts} jobLink="https://x.test/j" jobLinkText="Listing" />,
    )
    expect(screen.getByRole("link", { name: "Listing" })).toHaveAttribute("href", "https://x.test/j")
  })

  it("neither jobLink nor jobLinkText → no job-link line", () => {
    renderWithProviders(<RecommendedJobReportHeader {...base} {...noContacts} jobLink={null} jobLinkText={null} />)
    expect(document.querySelector(".recommended-report-job-link-text")).toBeNull()
  })
})
