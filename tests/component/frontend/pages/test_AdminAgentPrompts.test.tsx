import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AgentPrompts from "../../../../src/ui/frontend/src/pages/AdminAgentPrompts"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const models = [
  {
    model_code: "claude-sonnet",
    model_label: "Claude Sonnet",
    cpm_input: 3,
    cpm_output: 15,
    cpm_cache_write: 3.75,
    cpm_cache_read: 0.3,
    default_temperature: 0.2,
    default_max_tokens: 4096,
  },
]

const brainCatalog = [
  {
    brain_setting: "Little",
    label: "Little",
    default_temperature: 0.7,
    default_max_tokens: 8192,
  },
  {
    brain_setting: "Medium",
    label: "Medium",
    default_temperature: 0.2,
    default_max_tokens: 64000,
  },
  {
    brain_setting: "Big",
    label: "Big",
    default_temperature: 1,
    default_max_tokens: 32000,
  },
]

const agents = [
  {
    agent_id: "agent_a",
    model_code: "claude-sonnet",
    temperature: 0.2,
    max_tokens: 4096,
    task_count: 0,
    content_length: 12,
    updated_at: "2026-05-01T00:00:00Z",
  },
  {
    agent_id: "agent_b",
    model_code: "missing-model",
    temperature: 0.1,
    max_tokens: 1024,
    task_count: 2,
    content_length: 8,
    updated_at: "2026-05-02T00:00:00Z",
  },
]

describe("AdminAgentPrompts", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  function mockApi() {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/admin/agents/brain_settings") return { json: async () => brainCatalog } as Response
      if (url === "/api/admin/agents" && !init?.method) return { json: async () => agents } as Response
      if (url === "/api/admin/agents/models") return { json: async () => models } as Response
      if (url === "/api/admin/agents/agent_a" && !init?.method) {
        return { json: async () => ({ ...agents[0], content: "system prompt" }) } as Response
      }
      if (url === "/api/admin/agents/agent_a" && init?.method === "PUT")
        return { ok: true, status: 200, json: async () => ({ agent_id: "agent_a", brain_setting: "Medium" }) } as Response
      if (url === "/api/admin/agents" && init?.method === "POST") return { ok: true, json: async () => ({}) } as Response
      if (url === "/api/admin/agents/agent_a" && init?.method === "DELETE") return { ok: true, json: async () => ({}) } as Response
    })
  }

  it("lists agents, edits, adds, and deletes", async () => {
    mockApi()
    renderWithProviders(<AgentPrompts />)
    await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())

    await userEvent.click(screen.getByText("agent_a"))
    await waitFor(() => expect(screen.getByDisplayValue("system prompt")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.queryByText("Edit: agent_a")).not.toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "+ Add Agent" }))
    fireEvent.change(screen.getByPlaceholderText("e.g. job_analyst_grace"), { target: { value: "New Agent" } })
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText(/Agent "new_agent" created/)).toBeInTheDocument())

    const deleteButtons = screen.getAllByRole("button", { name: "Delete" })
    expect(deleteButtons[1]).toBeDisabled()
    await userEvent.click(deleteButtons[0])
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText(/Agent "agent_a" deleted/)).toBeInTheDocument())
  }, 20000)

  it("shows validation and error toasts", async () => {
    mockApi()
    renderWithProviders(<AgentPrompts />)
    await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "+ Add Agent" }))
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    expect(screen.getByText("Agent ID is required")).toBeInTheDocument()

    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url === "/api/admin/agents/agent_a") throw new Error("load failed")
    })
    await userEvent.click(screen.getByText("agent_a"))
    await waitFor(() => expect(screen.getByText("load failed")).toBeInTheDocument())
  }, 15000)
})
