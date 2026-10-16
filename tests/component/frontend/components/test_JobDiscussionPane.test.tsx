import { screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it } from "vitest"
import JobDiscussionPane from "../../../../src/ui/frontend/src/components/JobDiscussionPane"
import type { AgentStoryEntry } from "../../../../src/ui/frontend/src/components/AgentStoryTab"
import { renderWithProviders } from "../test-utils"

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

function payloadJson(prose: string): string {
  return JSON.stringify({ agent_payload: prose })
}

describe("JobDiscussionPane — AST-1551 / AST-2234", () => {
  it("hides all headers when agentStory is empty", () => {
    renderWithProviders(<JobDiscussionPane sections={CATALOG} agentStory={[]} />)
    for (const s of CATALOG) {
      expect(screen.queryByText(s.nav_label)).not.toBeInTheDocument()
    }
    expect(screen.queryAllByRole("button", { name: "Expand section" })).toHaveLength(0)
    expect(document.querySelector("textarea.entity-story-content")).toBeNull()
  })

  it("AC6: expands RESPONSE agent_payload prose (unescaped); skips PROMPT", async () => {
    const user = userEvent.setup()
    const story: AgentStoryEntry[] = [
      {
        task_key: "contemplate_job",
        agent_name: "Estelle",
        task_name: "Contemplate Job",
        created_at: "2026-03-05T16:48:00Z",
        blocks: [
          { type: "PROMPT", id: "p1", content: "secret prompt" },
          { type: "RESPONSE", id: "r1", content: payloadJson('Line one\nLine "two"') },
        ],
      },
    ]
    renderWithProviders(<JobDiscussionPane sections={CATALOG.slice(0, 1)} agentStory={story} />)

    // AC7: named header uses agent_name / task_name / stamp (UTC fallback when candidate tz unset).
    expect(screen.getByText(/Estelle's Contemplate Job @/)).toBeInTheDocument()
    await user.click(screen.getByRole("button", { name: "Expand section" }))
    const area = document.querySelector("textarea.entity-story-content") as HTMLTextAreaElement
    expect(area).toBeTruthy()
    expect(area.readOnly).toBe(true)
    expect(area.value).toBe('Line one\nLine "two"')
    expect(area.value).not.toContain("secret prompt")
  })

  it("skips empty RESPONSE and shows the next RESPONSE body (Agent Story parity)", async () => {
    const user = userEvent.setup()
    const story: AgentStoryEntry[] = [
      {
        task_key: "contemplate_job",
        blocks: [
          { type: "RESPONSE", id: "r0", content: "" },
          { type: "RESPONSE", id: "r1", content: payloadJson("later body") },
        ],
      },
    ]
    renderWithProviders(<JobDiscussionPane sections={CATALOG.slice(0, 1)} agentStory={story} />)
    await user.click(screen.getByRole("button", { name: "Expand section" }))
    const area = document.querySelector("textarea.entity-story-content") as HTMLTextAreaElement
    expect(area.value).toBe("later body")
  })

  it("omits hop when RESPONSE has no agent_payload prose", () => {
    const story: AgentStoryEntry[] = [
      {
        task_key: "contemplate_job",
        blocks: [{ type: "RESPONSE", id: "r1", content: '{"ok":true}' }],
      },
    ]
    renderWithProviders(<JobDiscussionPane sections={CATALOG.slice(0, 1)} agentStory={story} />)
    expect(screen.queryAllByRole("button", { name: "Expand section" })).toHaveLength(0)
  })

  it("treats RESPONSE (2) as RESPONSE body when agent_payload present", async () => {
    const user = userEvent.setup()
    const story: AgentStoryEntry[] = [
      {
        task_key: "contemplate_job",
        blocks: [{ type: "RESPONSE (2)", id: "r2", content: payloadJson("dup body") }],
      },
    ]
    renderWithProviders(<JobDiscussionPane sections={CATALOG.slice(0, 1)} agentStory={story} />)
    await user.click(screen.getByRole("button", { name: "Expand section" }))
    const area = document.querySelector("textarea.entity-story-content") as HTMLTextAreaElement
    expect(area.value).toBe("dup body")
  })

  it("omits hop with no usable RESPONSE (no empty header)", () => {
    renderWithProviders(<JobDiscussionPane sections={CATALOG.slice(0, 1)} agentStory={[]} />)
    expect(screen.queryByText("Contemplate Job")).not.toBeInTheDocument()
    expect(screen.queryAllByRole("button", { name: "Expand section" })).toHaveLength(0)
  })

  it("shows anticipate_scan header when story has agent_payload RESPONSE", async () => {
    const user = userEvent.setup()
    const sections = [
      { section_id: "anticipate_scan", nav_label: "Anticipate Scan", default_expanded: false },
      ...CATALOG.slice(0, 1),
    ]
    const story: AgentStoryEntry[] = [
      {
        task_key: "anticipate_scan",
        agent_name: "Laslo",
        task_name: "Anticipate Scan",
        blocks: [{ type: "RESPONSE", id: "a1", content: payloadJson("scan ok") }],
      },
    ]
    renderWithProviders(<JobDiscussionPane sections={sections} agentStory={story} />)
    expect(screen.getByText(/Laslo's Anticipate Scan/)).toBeInTheDocument()
    expect(screen.queryByText("Contemplate Job")).not.toBeInTheDocument()
    expect(screen.getAllByRole("button", { name: "Expand section" })).toHaveLength(1)
    await user.click(screen.getByRole("button", { name: "Expand section" }))
    const area = document.querySelector("textarea.entity-story-content") as HTMLTextAreaElement
    expect(area.value).toBe("scan ok")
  })
})
