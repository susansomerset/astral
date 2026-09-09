import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it } from "vitest"
import JobDiscussionPane from "../../../../src/ui/frontend/src/components/JobDiscussionPane"
import type { AgentStoryEntry } from "../../../../src/ui/frontend/src/components/AgentStoryTab"

// Catalog order lockstep with TestAst1550ReportDiscussionSections._NINE (+ optional anticipate_scan).
const CATALOG = [
  { section_id: "contemplate_job", nav_label: "Contemplate Job", default_expanded: false },
  { section_id: "draft_job_resume", nav_label: "Draft Job Resume", default_expanded: false },
  { section_id: "check_job_resume", nav_label: "Check Job Resume", default_expanded: false },
  { section_id: "draft_cover_letter", nav_label: "Draft Cover Letter", default_expanded: false },
  { section_id: "check_cover_letter", nav_label: "Check Cover Letter", default_expanded: false },
  { section_id: "draft_application_responses", nav_label: "Draft Application Responses", default_expanded: false },
  { section_id: "check_application_responses", nav_label: "Check Application Responses", default_expanded: false },
  { section_id: "polish_application_package", nav_label: "Polish Application Package", default_expanded: false },
  { section_id: "propose_application_responses", nav_label: "Propose Application Responses", default_expanded: false },
]

describe("JobDiscussionPane — AST-1551", () => {
  it("hides all headers when agentStory is empty", () => {
    // AST-1612 / AST-1609: empty story → 0 Expand buttons (no always-on hop slots).
    render(<JobDiscussionPane sections={CATALOG} agentStory={[]} />)
    for (const s of CATALOG) {
      expect(screen.queryByText(s.nav_label)).not.toBeInTheDocument()
    }
    expect(screen.queryAllByRole("button", { name: "Expand section" })).toHaveLength(0)
    expect(document.querySelector("textarea.entity-story-content")).toBeNull()
  })

  it("expands RESPONSE-only body; pretty-prints JSON; skips PROMPT", async () => {
    const user = userEvent.setup()
    const story: AgentStoryEntry[] = [
      {
        task_key: "contemplate_job",
        blocks: [
          { type: "PROMPT", id: "p1", content: "secret prompt" },
          { type: "RESPONSE", id: "r1", content: '{"ok":true}' },
        ],
      },
    ]
    render(<JobDiscussionPane sections={CATALOG.slice(0, 1)} agentStory={story} />)

    await user.click(screen.getByRole("button", { name: "Expand section" }))
    const jsonArea = document.querySelector("textarea.entity-story-content") as HTMLTextAreaElement
    expect(jsonArea).toBeTruthy()
    expect(jsonArea.readOnly).toBe(true)
    expect(jsonArea.value).toContain('"ok": true')
    expect(jsonArea.value).not.toContain("secret prompt")
  })

  it("skips empty RESPONSE and shows the next RESPONSE body (Agent Story parity)", async () => {
    // AC4 / plan: same empty-RESPONSE filter as AgentStoryTab — blank RESPONSE must not hide later content.
    const user = userEvent.setup()
    const story: AgentStoryEntry[] = [
      {
        task_key: "contemplate_job",
        blocks: [
          { type: "RESPONSE", id: "r0", content: "" },
          { type: "RESPONSE", id: "r1", content: '{"ok":true}' },
        ],
      },
    ]
    render(<JobDiscussionPane sections={CATALOG.slice(0, 1)} agentStory={story} />)
    await user.click(screen.getByRole("button", { name: "Expand section" }))
    const area = document.querySelector("textarea.entity-story-content") as HTMLTextAreaElement
    expect(area).toBeTruthy()
    expect(area.value).toContain('"ok": true')
  })

  it("shows raw text RESPONSE with real line breaks", async () => {
    const user = userEvent.setup()
    const story: AgentStoryEntry[] = [
      {
        task_key: "draft_job_resume",
        blocks: [{ type: "RESPONSE", id: "r2", content: "plain line\nbreaks" }],
      },
    ]
    render(
      <JobDiscussionPane
        sections={[{ section_id: "draft_job_resume", nav_label: "Draft Job Resume", default_expanded: false }]}
        agentStory={story}
      />,
    )
    await user.click(screen.getByRole("button", { name: "Expand section" }))
    const area = document.querySelector("textarea.entity-story-content") as HTMLTextAreaElement
    expect(area.value).toBe("plain line\nbreaks")
  })

  it("treats RESPONSE (2) as RESPONSE body", async () => {
    const user = userEvent.setup()
    const story: AgentStoryEntry[] = [
      {
        task_key: "contemplate_job",
        blocks: [{ type: "RESPONSE (2)", id: "r2", content: "dup body" }],
      },
    ]
    render(<JobDiscussionPane sections={CATALOG.slice(0, 1)} agentStory={story} />)
    await user.click(screen.getByRole("button", { name: "Expand section" }))
    const area = document.querySelector("textarea.entity-story-content") as HTMLTextAreaElement
    expect(area.value).toBe("dup body")
  })

  it("omits hop with no usable RESPONSE (no empty header)", () => {
    // AST-1612: missing/empty hop is not rendered — no Expand click.
    render(<JobDiscussionPane sections={CATALOG.slice(0, 1)} agentStory={[]} />)
    expect(screen.queryByText("Contemplate Job")).not.toBeInTheDocument()
    expect(screen.queryAllByRole("button", { name: "Expand section" })).toHaveLength(0)
  })

  it("shows anticipate_scan header when story has RESPONSE", async () => {
    // AST-1612 bug-repro: unique-parent hop visible only when this job has RESPONSE.
    const user = userEvent.setup()
    const sections = [
      { section_id: "anticipate_scan", nav_label: "Anticipate Scan", default_expanded: false },
      ...CATALOG.slice(0, 1),
    ]
    const story: AgentStoryEntry[] = [
      {
        task_key: "anticipate_scan",
        blocks: [{ type: "RESPONSE", id: "a1", content: '{"scan":true}' }],
      },
    ]
    render(<JobDiscussionPane sections={sections} agentStory={story} />)
    expect(screen.getByText("Anticipate Scan")).toBeInTheDocument()
    expect(screen.queryByText("Contemplate Job")).not.toBeInTheDocument()
    expect(screen.getAllByRole("button", { name: "Expand section" })).toHaveLength(1)
    await user.click(screen.getByRole("button", { name: "Expand section" }))
    const area = document.querySelector("textarea.entity-story-content") as HTMLTextAreaElement
    expect(area.value).toContain('"scan": true')
  })
})
