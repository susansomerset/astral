import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it } from "vitest"
import JobMeteoritePane, {
  type RelatedMeteorite,
} from "../../../../src/ui/frontend/src/components/JobMeteoritePane"

// Lockstep with JOBS_RECOMMENDED_REPORT_METEORITE_SECTIONS / AST-1691 config.
const CATALOG = [
  { section_id: "meteorite_timestamps", nav_label: "Timestamps", default_expanded: true },
  { section_id: "meteorite_link", nav_label: "Link", default_expanded: true },
  { section_id: "meteorite_ai", nav_label: "AI Content", default_expanded: true },
  { section_id: "meteorite_provenance", nav_label: "Provenance", default_expanded: false },
]

function baseMeteorite(overrides: Partial<RelatedMeteorite> = {}): RelatedMeteorite {
  return {
    id: 42,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-02T00:00:00Z",
    state_changed_at: "2026-01-03T00:00:00Z",
    estelle_notified_at: null,
    link: "https://jobs.example/meteorite",
    classify_outcome: "QUALIFIED",
    content: '{"ok":true}',
    state: "LANDED",
    source_kind: "email",
    source_id: "msg-1",
    error: null,
    ...overrides,
  }
}

describe("JobMeteoritePane — AST-1692", () => {
  it("renders four section headers from manifest order", () => {
    render(<JobMeteoritePane sections={CATALOG} relatedMeteorite={baseMeteorite()} />)
    expect(screen.getByText("Timestamps")).toBeInTheDocument()
    expect(screen.getByText("Link")).toBeInTheDocument()
    expect(screen.getByText("AI Content")).toBeInTheDocument()
    expect(screen.getByText("Provenance")).toBeInTheDocument()
  })

  it("timestamps match row; estelle_notified_at only when set", async () => {
    const user = userEvent.setup()
    const { rerender } = render(
      <JobMeteoritePane sections={CATALOG} relatedMeteorite={baseMeteorite()} />,
    )
    // Timestamps default_expanded true — body visible without Expand
    expect(screen.getByText("created_at: 2026-01-01T00:00:00Z")).toBeInTheDocument()
    expect(screen.getByText("updated_at: 2026-01-02T00:00:00Z")).toBeInTheDocument()
    expect(screen.getByText("state_changed_at: 2026-01-03T00:00:00Z")).toBeInTheDocument()
    expect(screen.queryByText(/estelle_notified_at:/)).not.toBeInTheDocument()

    rerender(
      <JobMeteoritePane
        sections={CATALOG}
        relatedMeteorite={baseMeteorite({ estelle_notified_at: "2026-01-04T00:00:00Z" })}
      />,
    )
    expect(screen.getByText("estelle_notified_at: 2026-01-04T00:00:00Z")).toBeInTheDocument()
    // Expand unused here — keep user to satisfy import when panels collapse
    void user
  })

  it("http(s) link is navigable; breadcrumb is plain text", () => {
    const { rerender } = render(
      <JobMeteoritePane sections={CATALOG} relatedMeteorite={baseMeteorite()} />,
    )
    const href = screen.getByRole("link", { name: "https://jobs.example/meteorite" })
    expect(href).toHaveAttribute("href", "https://jobs.example/meteorite")
    expect(href).toHaveAttribute("target", "_blank")

    rerender(
      <JobMeteoritePane
        sections={CATALOG}
        relatedMeteorite={baseMeteorite({ link: "inbox:folder/msg" })}
      />,
    )
    expect(screen.queryByRole("link")).not.toBeInTheDocument()
    expect(screen.getByText("inbox:folder/msg")).toBeInTheDocument()
    expect(screen.getByText("inbox:folder/msg").tagName).toBe("P")
  })

  it("AI section shows classify_outcome + read-only pretty content", () => {
    render(<JobMeteoritePane sections={CATALOG} relatedMeteorite={baseMeteorite()} />)
    expect(screen.getByText("classify_outcome: QUALIFIED")).toBeInTheDocument()
    const area = document.querySelector("textarea.entity-story-content") as HTMLTextAreaElement
    expect(area).toBeTruthy()
    expect(area.readOnly).toBe(true)
    expect(area.value).toContain('"ok": true')
  })

  it("provenance rows include error only when present", async () => {
    const user = userEvent.setup()
    render(
      <JobMeteoritePane
        sections={CATALOG}
        relatedMeteorite={baseMeteorite({ error: "classify failed" })}
      />,
    )
    // Provenance default_expanded false — expand first
    const expands = screen.getAllByRole("button", { name: "Expand section" })
    await user.click(expands[expands.length - 1])
    expect(screen.getByText("id: 42")).toBeInTheDocument()
    expect(screen.getByText("state: LANDED")).toBeInTheDocument()
    expect(screen.getByText("source_kind: email")).toBeInTheDocument()
    expect(screen.getByText("source_id: msg-1")).toBeInTheDocument()
    expect(screen.getByText("error: classify failed")).toBeInTheDocument()
  })

  it("empty link and empty AI show empty copy", () => {
    render(
      <JobMeteoritePane
        sections={CATALOG}
        relatedMeteorite={baseMeteorite({
          link: "",
          classify_outcome: null,
          content: null,
        })}
      />,
    )
    expect(screen.getByText("No link on file.")).toBeInTheDocument()
    expect(screen.getByText("No AI content on file.")).toBeInTheDocument()
  })
})
