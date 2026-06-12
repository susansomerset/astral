import { cleanup, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it } from "vitest"
import AgentStoryTab, { type AgentStoryEntry } from "../../../../src/ui/frontend/src/components/AgentStoryTab"
import { renderWithProviders } from "../test-utils"

const entry: AgentStoryEntry = {
  task_key: "analyze",
  created_at: "2026-01-01T00:00:00Z",
  agent_performance: "good",
  failure_note: "none",
  vector_grades: [{ vector: "fit", grade: "A", reason: "strong", confidence: 4 }],
  rubric_artifact: "joblist_rubric",
  blocks: [
    { type: "PROMPT", id: "1", content: "plain" },
    { type: "RESPONSE", id: "2", content: "" },
    { type: "RESPONSE", id: "3", content: "{\"ok\":true}" },
    { type: "RESPONSE", id: "4", content: "not-json" },
  ],
}

describe("AgentStoryTab", () => {
  it("renders metadata, grades, and block tabs", async () => {
    renderWithProviders(<AgentStoryTab entry={entry} />)
    expect(screen.getByText("analyze")).toBeInTheDocument()
    expect(screen.getByText("good")).toBeInTheDocument()
    expect(screen.getByText("none")).toBeInTheDocument()
    expect(screen.getByText("strong")).toBeInTheDocument()
    expect(screen.getByDisplayValue("plain")).toBeInTheDocument()
    const responseTabs = screen.getAllByRole("button", { name: "RESPONSE" })
    await userEvent.click(responseTabs[0])
    expect(screen.getByDisplayValue(/"ok": true/)).toBeInTheDocument()
  })

  it("shows an empty state when no blocks remain", () => {
    renderWithProviders(
      <AgentStoryTab
        entry={{
          task_key: "empty",
          blocks: [{ type: "RESPONSE", id: "1", content: "" }],
        }}
      />,
    )
    expect(screen.getByText("No prompt blocks recorded.")).toBeInTheDocument()
  })

  it("handles missing blocks and stale tab indexes", async () => {
    const { rerender } = renderWithProviders(
      <AgentStoryTab
        entry={{
          task_key: "shift",
          blocks: [
            { type: "PROMPT", id: "1", content: "one" },
            { type: "PROMPT", id: "2", content: "two" },
            { type: "PROMPT", id: "3", content: "three" },
          ],
        }}
      />,
    )
    await userEvent.click(screen.getAllByRole("button", { name: "PROMPT" })[0])
    await userEvent.click(screen.getAllByRole("button", { name: "PROMPT" })[2])
    rerender(
      <AgentStoryTab
        entry={{
          task_key: "shift",
          blocks: [{ type: "PROMPT", id: "1", content: "only" }],
        }}
      />,
    )
    expect(screen.getByDisplayValue("")).toBeInTheDocument()

    cleanup()
    renderWithProviders(<AgentStoryTab entry={{ task_key: "none" }} />)
    expect(screen.getByText("No prompt blocks recorded.")).toBeInTheDocument()
  })
})
