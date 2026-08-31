import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it } from "vitest"
import JobDiscussionPane from "../../../../src/ui/frontend/src/components/JobDiscussionPane"
import type { AgentStoryEntry } from "../../../../src/ui/frontend/src/components/AgentStoryTab"

const NINE = [
  { section_id: "contemplate_job", nav_label: "Contemplate Job", default_expanded: false },
  { section_id: "advise_job_resume", nav_label: "Advise Job Resume", default_expanded: false },
  { section_id: "draft_job_resume", nav_label: "Draft Job Resume", default_expanded: false },
  { section_id: "check_job_resume", nav_label: "Check Job Resume", default_expanded: false },
  { section_id: "finalize_job_resume", nav_label: "Finalize Job Resume", default_expanded: false },
  { section_id: "draft_cover_letter", nav_label: "Draft Cover Letter", default_expanded: false },
  { section_id: "check_cover_letter", nav_label: "Check Cover Letter", default_expanded: false },
  { section_id: "finalize_cover_letter", nav_label: "Finalize Cover Letter", default_expanded: false },
  { section_id: "propose_application_responses", nav_label: "Propose Application Responses", default_expanded: false },
]

describe("JobDiscussionPane — AST-1551", () => {
  it("renders nine collapsed sections from manifest labels", () => {
    render(<JobDiscussionPane sections={NINE} agentStory={[]} />)
    for (const s of NINE) {
      expect(screen.getByText(s.nav_label)).toBeInTheDocument()
    }
    expect(screen.getAllByRole("button", { name: "Expand section" })).toHaveLength(9)
    expect(screen.queryByRole("button", { name: "Collapse section" })).not.toBeInTheDocument()
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
    render(<JobDiscussionPane sections={NINE.slice(0, 1)} agentStory={story} />)

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
    render(<JobDiscussionPane sections={NINE.slice(0, 1)} agentStory={story} />)
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
    render(<JobDiscussionPane sections={NINE.slice(0, 1)} agentStory={story} />)
    await user.click(screen.getByRole("button", { name: "Expand section" }))
    const area = document.querySelector("textarea.entity-story-content") as HTMLTextAreaElement
    expect(area.value).toBe("dup body")
  })

  it("missing hop stays empty after expand", async () => {
    const user = userEvent.setup()
    render(<JobDiscussionPane sections={NINE.slice(0, 1)} agentStory={[]} />)
    await user.click(screen.getByRole("button", { name: "Expand section" }))
    expect(document.querySelector("textarea.entity-story-content")).toBeNull()
  })
})
