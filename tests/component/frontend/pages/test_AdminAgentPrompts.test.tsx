import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AgentPrompts from "../../../../src/ui/frontend/src/pages/AdminAgentPrompts"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

// AST-1880: GET /agents/models — keyed by model id, each model's own sizes; `order` carries catalog order.
// AST-1948: sizes carry no default_temperature (the agent's mode decides temperature).
const models = {
  "kimi-k2.6": {
    order: 1,
    label: "Kimi K2.6",
    server_id: "kimi",
    server_label: "Kimi",
    brain_sizes: {
      Big: { order: 1, default_max_tokens: 32000 },
      Little: { order: 0, default_max_tokens: 8192 },
    },
  },
  claude: {
    order: 0,
    label: "Claude",
    server_id: "anthropic",
    server_label: "Anthropic",
    brain_sizes: {
      Big: { order: 2, default_max_tokens: 32000 },
      Little: { order: 0, default_max_tokens: 8192 },
      Medium: { order: 1, default_max_tokens: 64000 },
    },
  },
}

// AST-1948: agent rows carry mode; temperature / model_code are gone.
const agents = [
  {
    agent_id: "agent_a",
    model_id: "claude",
    brain_setting: "Medium",
    mode: "Deterministic",
    max_tokens: 4096,
    task_count: 0,
    content_length: 12,
    updated_at: "2026-05-01T00:00:00Z",
  },
  {
    agent_id: "agent_b",
    model_id: "kimi-k2.6",
    brain_setting: "Big",
    mode: "Creative",
    max_tokens: 1024,
    task_count: 2,
    content_length: 8,
    updated_at: "2026-05-02T00:00:00Z",
  },
]

describe("AdminAgentPrompts", () => {
  let postBodies: Record<string, unknown>[] = []
  let putBodies: Record<string, unknown>[] = []
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    postBodies = []
    putBodies = []
  })

  const field = (label: string) =>
    screen.getByText(label, { selector: "label.dep-field-label" }).closest(".dep-field") as HTMLElement
  const optionTexts = (label: string) =>
    within(field(label)).getAllByRole("option").map(o => o.textContent)

  const agentTokens = ["FIRST_NAME", "LAST_NAME"]

  function mockApi() {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/admin/repo_json/status") {
        return {
          ok: true,
          json: async () => ({
            agent: { diverged: false, repo_relative_path: "data/admin/agent.json" },
            agent_task: { diverged: false, repo_relative_path: "data/admin/agent_task.json" },
          }),
        } as Response
      }
      if (url === "/api/candidates") {
        return { ok: true, json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
      }
      if (url === "/api/admin/agents/meta/tokens") return { ok: true, json: async () => agentTokens } as Response
      if (url === "/api/admin/agents" && !init?.method) return { ok: true, json: async () => agents } as Response
      if (url === "/api/admin/agents/models") return { ok: true, json: async () => models } as Response
      if (url === "/api/admin/agents/agent_a" && !init?.method) {
        return { ok: true, json: async () => ({ ...agents[0], content: "system prompt" }) } as Response
      }
      if (url === "/api/admin/agents/agent_a" && init?.method === "PUT") {
        putBodies.push(JSON.parse(String(init.body)))
        return { ok: true, status: 200, json: async () => ({ agent_id: "agent_a", brain_setting: "Medium" }) } as Response
      }
      if (url === "/api/admin/agents" && init?.method === "POST") {
        postBodies.push(JSON.parse(String(init.body)))
        return { ok: true, json: async () => ({}) } as Response
      }
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

  it("AST-1880: Add picks a model, then only that model's sizes; defaults follow model + size", async () => {
    mockApi()
    renderWithProviders(<AgentPrompts />)
    await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
    // Model column shows the catalog label.
    expect(screen.getByText("Claude")).toBeInTheDocument()
    expect(screen.getByText("Kimi K2.6")).toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: "+ Add Agent" }))
    // First model in catalog order, its first size, and that row's max-tokens default.
    expect(optionTexts("Model")).toEqual(["Claude", "Kimi K2.6"])
    expect(within(field("Model")).getByRole("combobox")).toHaveValue("claude")
    expect(optionTexts("Brain size")).toEqual(["Little", "Medium", "Big"])
    expect(within(field("Brain size")).getByRole("combobox")).toHaveValue("Little")
    // AST-1949: Add opens on Deterministic with exactly the two modes.
    expect(optionTexts("Mode")).toEqual(["Deterministic", "Creative"])
    expect(within(field("Mode")).getByRole("combobox")).toHaveValue("Deterministic")
    await userEvent.selectOptions(within(field("Brain size")).getByRole("combobox"), "Medium")
    expect(within(field("Max Tokens")).getByRole("spinbutton")).toHaveValue(64000)

    // Kimi has no Medium: size falls back to Kimi's first size and its max-tokens default.
    await userEvent.selectOptions(within(field("Model")).getByRole("combobox"), "kimi-k2.6")
    expect(optionTexts("Brain size")).toEqual(["Little", "Big"])
    expect(within(field("Brain size")).getByRole("combobox")).toHaveValue("Little")
    expect(within(field("Max Tokens")).getByRole("spinbutton")).toHaveValue(8192)
    // Size / model changes never touch the mode.
    expect(within(field("Mode")).getByRole("combobox")).toHaveValue("Deterministic")
    await userEvent.selectOptions(within(field("Mode")).getByRole("combobox"), "Creative")

    fireEvent.change(screen.getByPlaceholderText("e.g. job_analyst_grace"), { target: { value: "kimi agent" } })
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(postBodies).toHaveLength(1))
    expect(postBodies[0]).toMatchObject({
      model_id: "kimi-k2.6", brain_setting: "Little", mode: "Creative", max_tokens: 8192,
    })
    expect(postBodies[0]).not.toHaveProperty("temperature")
  }, 20000)

  it("AST-1880: Edit shows the agent's model + size and sends model_id on Save", async () => {
    mockApi()
    renderWithProviders(<AgentPrompts />)
    await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
    await userEvent.click(screen.getByText("agent_a"))
    await waitFor(() => expect(screen.getByDisplayValue("system prompt")).toBeInTheDocument())
    expect(within(field("Model")).getByRole("combobox")).toHaveValue("claude")
    expect(within(field("Brain size")).getByRole("combobox")).toHaveValue("Medium")
    // AST-1949: the row's stored mode pre-selects.
    expect(within(field("Mode")).getByRole("combobox")).toHaveValue("Deterministic")
    // Switching to Big keeps the model; Save carries both plus mode, never temperature.
    await userEvent.selectOptions(within(field("Brain size")).getByRole("combobox"), "Big")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(putBodies).toHaveLength(1))
    expect(putBodies[0]).toMatchObject({ model_id: "claude", brain_setting: "Big", mode: "Deterministic" })
    expect(putBodies[0]).not.toHaveProperty("temperature")
  }, 20000)

  // AST-1949 AC 8: Mode select (exactly Deterministic / Creative) sent as `mode`; no temperature
  // control for any model; list has Mode, not Temp. Unmigrated rows (mode null, AST-1950) show — / a placeholder.
  describe("AST-1949 Manage Agents mode", () => {
    const headers = () =>
      screen.getAllByRole("columnheader").map(th => (th.textContent ?? "").replace(/[▲▼]/g, "").trim())

    it("list has a Mode column showing each row's mode and no Temp column", async () => {
      mockApi()
      renderWithProviders(<AgentPrompts />)
      await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
      expect(headers()).toContain("Mode")
      expect(headers()).not.toContain("Temp")
      expect(screen.getByText("Deterministic")).toBeInTheDocument()
      expect(screen.getByText("Creative")).toBeInTheDocument()
    }, 15000)

    it("no Temperature field renders in Add or Edit for any model or size", async () => {
      mockApi()
      renderWithProviders(<AgentPrompts />)
      await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
      const noTemp = () => {
        expect(screen.queryByText("Temperature", { selector: "label.dep-field-label" })).not.toBeInTheDocument()
        expect(screen.queryByText(/temp/i, { selector: "label" })).not.toBeInTheDocument()
      }
      await userEvent.click(screen.getByRole("button", { name: "+ Add Agent" }))
      for (const [mid, m] of Object.entries(models)) {
        await userEvent.selectOptions(within(field("Model")).getByRole("combobox"), mid)
        for (const size of Object.keys(m.brain_sizes)) {
          await userEvent.selectOptions(within(field("Brain size")).getByRole("combobox"), size)
          noTemp()
        }
      }
      await userEvent.click(screen.getByRole("button", { name: "Cancel" }))
      await userEvent.click(screen.getByText("agent_a"))
      await waitFor(() => expect(screen.getByDisplayValue("system prompt")).toBeInTheDocument())
      noTemp()
    }, 20000)

    it("Edit switches mode and PUT sends the new mode without temperature", async () => {
      mockApi()
      renderWithProviders(<AgentPrompts />)
      await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
      await userEvent.click(screen.getByText("agent_a"))
      await waitFor(() => expect(screen.getByDisplayValue("system prompt")).toBeInTheDocument())
      expect(optionTexts("Mode")).toEqual(["Deterministic", "Creative"])
      await userEvent.selectOptions(within(field("Mode")).getByRole("combobox"), "Creative")
      await userEvent.click(screen.getByRole("button", { name: "Save" }))
      await waitFor(() => expect(putBodies).toHaveLength(1))
      expect(putBodies[0]).toMatchObject({ content: "system prompt", mode: "Creative" })
      expect(putBodies[0]).not.toHaveProperty("temperature")
    }, 20000)

    it("an unmigrated row (mode null) shows — in the list and a choose-mode placeholder in Edit", async () => {
      const unmigrated = { ...agents[0], mode: null }
      installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
        if (url === "/api/candidates") return { ok: true, json: async () => [] } as Response
        if (url === "/api/admin/agents/meta/tokens") return { ok: true, json: async () => agentTokens } as Response
        if (url === "/api/admin/agents" && !init?.method) return { ok: true, json: async () => [unmigrated] } as Response
        if (url === "/api/admin/agents/models") return { ok: true, json: async () => models } as Response
        if (url === "/api/admin/agents/agent_a" && !init?.method) {
          return { ok: true, json: async () => ({ ...unmigrated, content: "system prompt" }) } as Response
        }
      })
      renderWithProviders(<AgentPrompts />)
      await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
      const row = screen.getByText("agent_a").closest("tr") as HTMLElement
      expect(within(row).getByText("—")).toBeInTheDocument()
      await userEvent.click(screen.getByText("agent_a"))
      await waitFor(() => expect(screen.getByDisplayValue("system prompt")).toBeInTheDocument())
      expect(within(field("Mode")).getByRole("combobox")).toHaveValue("")
      expect(optionTexts("Mode")).toEqual(["— choose mode —", "Deterministic", "Creative"])
      // Picking a mode drops the placeholder.
      await userEvent.selectOptions(within(field("Mode")).getByRole("combobox"), "Deterministic")
      expect(optionTexts("Mode")).toEqual(["Deterministic", "Creative"])
    }, 20000)
  })

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

  it("AST-636: shows token autocomplete when typing {$ in edit modal", async () => {
    mockApi()
    renderWithProviders(<AgentPrompts />)
    await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
    await userEvent.click(screen.getByText("agent_a"))
    await waitFor(() => expect(screen.getByDisplayValue("system prompt")).toBeInTheDocument())
    const textarea = screen.getByDisplayValue("system prompt") as HTMLTextAreaElement
    fireEvent.change(textarea, { target: { value: "{$" } })
    textarea.setSelectionRange(2, 2)
    fireEvent.keyUp(textarea)
    await waitFor(() => {
      expect(screen.getByText((_, node) => node?.textContent === "{$FIRST_NAME}")).toBeInTheDocument()
    })
    await userEvent.click(screen.getByText((_, node) => node?.textContent === "{$FIRST_NAME}"))
    await waitFor(() => expect(textarea).toHaveValue("{$FIRST_NAME}"))
  }, 15000)

  it("AST-636: tolerates non-OK agent token meta without showing picker", async () => {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { ok: true, json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
      }
      if (url === "/api/admin/agents/meta/tokens") {
        return { ok: false, status: 500, json: async () => ({ error: "fail" }) } as Response
      }
      if (url === "/api/admin/agents/models") return { ok: true, json: async () => models } as Response
      if (url === "/api/admin/agents" && !init?.method) return { ok: true, json: async () => agents } as Response
      if (url === "/api/admin/agents/agent_a" && !init?.method) {
        return { ok: true, json: async () => ({ ...agents[0], content: "system prompt" }) } as Response
      }
    })
    renderWithProviders(<AgentPrompts />)
    await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
    await userEvent.click(screen.getByText("agent_a"))
    await waitFor(() => expect(screen.getByDisplayValue("system prompt")).toBeInTheDocument())
    const textarea = screen.getByDisplayValue("system prompt") as HTMLTextAreaElement
    fireEvent.change(textarea, { target: { value: "system prompt{$" } })
    textarea.setSelectionRange(textarea.value.length, textarea.value.length)
    fireEvent.keyUp(textarea)
    expect(screen.queryByText((_, node) => node?.textContent === "{$FIRST_NAME}")).not.toBeInTheDocument()
  }, 15000)

  it("AST-632: loads agent tokens, preview resolved, save preserves literal placeholders", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    let putBody = ""
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { ok: true, json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
      }
      if (url === "/api/admin/agents/meta/tokens") return { ok: true, json: async () => agentTokens } as Response
      if (url === "/api/admin/agents/models") return { ok: true, json: async () => models } as Response
      if (url === "/api/admin/agents" && !init?.method) return { ok: true, json: async () => agents } as Response
      if (url === "/api/admin/agents/agent_a" && !init?.method) {
        return { ok: true, json: async () => ({ ...agents[0], content: "Hello {$FIRST_NAME}" }) } as Response
      }
      if (url === "/api/admin/agents/preview" && init?.method === "POST") {
        const body = JSON.parse(String(init?.body))
        expect(body.candidate_id).toBe("c1")
        expect(body.content).toBe("Hello {$FIRST_NAME}")
        return { ok: true, json: async () => ({ candidate_id: "c1", content: "Hello Ada" }) } as Response
      }
      if (url === "/api/admin/agents/agent_a" && init?.method === "PUT") {
        putBody = String(init?.body)
        return { ok: true, status: 200, json: async () => ({ agent_id: "agent_a" }) } as Response
      }
    })
    renderWithProviders(<AgentPrompts />)
    await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
    await userEvent.click(screen.getByText("agent_a"))
    await waitFor(() => expect(screen.getByDisplayValue("Hello {$FIRST_NAME}")).toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "Preview Resolved" }))
    await waitFor(() => expect(screen.getByText("Hello Ada")).toBeInTheDocument())
    expect(screen.getByText(/Preview: c1/)).toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(putBody).toContain("{$FIRST_NAME}"))
    expect(putBody).not.toContain("Hello Ada")
  }, 20000)

  it("AST-783: shows agent repo JSON divergence banner on routed page", async () => {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/admin/repo_json/status") {
        return {
          ok: true,
          json: async () => ({
            agent: { diverged: true, repo_relative_path: "data/admin/agent.json" },
            agent_task: { diverged: false, repo_relative_path: "data/admin/agent_task.json" },
          }),
        } as Response
      }
      if (url === "/api/candidates") {
        return { ok: true, json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
      }
      if (url === "/api/admin/agents/models") return { ok: true, json: async () => models } as Response
      if (url === "/api/admin/agents" && !init?.method) return { ok: true, json: async () => agents } as Response
    })
    renderWithProviders(<AgentPrompts />)
    await waitFor(() => expect(screen.getByText(/agent personas/)).toBeInTheDocument())
    expect(screen.getByRole("button", { name: "Revert to file" })).toBeInTheDocument()
  }, 15000)

  it("AST-1302: row Delete is icon-control with D", async () => {
    mockApi()
    renderWithProviders(<AgentPrompts />)
    await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
    const deletes = screen.getAllByRole("button", { name: "Delete" })
    expect(deletes[0]).toHaveClass("icon-control")
    expect(deletes[0]).toHaveTextContent("D")
    expect(deletes[0]).not.toBeDisabled()
    expect(deletes[1]).toHaveClass("icon-control")
    expect(deletes[1]).toHaveTextContent("D")
    expect(deletes[1]).toBeDisabled()
    expect(deletes[0]).not.toHaveClass("dep-btn")
  }, 15000)

  describe("AST-1410 silent refetch", () => {
    it("post-save list refetch keeps the table and skips Loading...", async () => {
      mockApi()
      renderWithProviders(<AgentPrompts />)
      await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
      await userEvent.click(screen.getByText("agent_a"))
      await waitFor(() => expect(screen.getByDisplayValue("system prompt")).toBeInTheDocument())
      const inner = mockedApi.getMockImplementation()!
      let release: (value: Response) => void = () => {}
      mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
        if (url === "/api/admin/agents" && !init?.method) {
          return new Promise<Response>((resolve) => { release = resolve })
        }
        return inner(url, init)
      })
      await userEvent.click(screen.getByRole("button", { name: "Save" }))
      await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
      expect(screen.queryByText("Loading...")).not.toBeInTheDocument()
      release({ ok: true, json: async () => agents } as Response)
      await waitFor(() => expect(screen.queryByText("Edit: agent_a")).not.toBeInTheDocument())
      expect(screen.getByText("agent_a")).toBeInTheDocument()
    }, 20000)
  })
})
