import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it } from "vitest"
import ReportSectionList from "../../../../src/ui/frontend/src/components/ReportSectionList"

const sections = [
  { section_id: "open", nav_label: "Open Section", default_expanded: true },
  { section_id: "closed", nav_label: "Closed Section", default_expanded: false },
]

describe("ReportSectionList — AST-948", () => {
  it("seeds expanded state from default_expanded and renders leading", async () => {
    const user = userEvent.setup()
    render(
      <ReportSectionList
        leading={<button type="button">Leading action</button>}
        sections={sections}
        renderSection={id => <p>{id}-body</p>}
      />,
    )

    expect(screen.getByRole("button", { name: "Leading action" })).toBeInTheDocument()
    expect(screen.getByText("Open Section")).toBeInTheDocument()
    expect(screen.getByText("Closed Section")).toBeInTheDocument()
    expect(screen.getByText("open-body")).toBeVisible()
    expect(screen.getByText("closed-body")).not.toBeVisible()

    await user.click(screen.getByRole("button", { name: "Expand section" }))
    expect(screen.getByText("closed-body")).toBeVisible()
  })

  it("does not render Expand all / Collapse all chrome", () => {
    render(<ReportSectionList sections={sections} renderSection={() => null} />)
    expect(screen.queryByRole("button", { name: "Expand all" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Collapse all" })).not.toBeInTheDocument()
  })
})

describe("ReportSectionList — AST-950 renderMetadata", () => {
  it("passes renderMetadata into CollapsiblePanel header", () => {
    render(
      <ReportSectionList
        sections={[{ section_id: "phase_jd", nav_label: "JD Analysis", default_expanded: true }]}
        renderSection={() => <p>body</p>}
        renderMetadata={id => <span data-testid={`meta-${id}`}>META</span>}
      />,
    )
    expect(screen.getByTestId("meta-phase_jd")).toHaveTextContent("META")
    expect(screen.getByText("body")).toBeVisible()
  })
})
