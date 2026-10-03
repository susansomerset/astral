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

// AST-1880 / AST-1957: GET /agents/models — keyed by model id; `order` carries catalog order; each model's own
// default output budget, no brain sizes.
const models = {
  "kimi-k2.6": { order: 1, label: "Kimi K2.6", server_id: "kimi", server_label: "Kimi", default_max_tokens: 16000 },
  "claude-haiku-4-5": {
    order: 0, label: "Claude Haiku 4.5", server_id: "anthropic", server_label: "Anthropic", default_max_tokens: 8192,
  },
}

// AST-1957: rows carry the seven plain settings as the data layer exposes them (lists decoded, bool fallbacks).
const emptySettings = {
  quantization: null, temperature: null, reasoning_effort: null, provider_allow_fallbacks: null,
  provider_only: null, provider_ignore: null, provider_sort: null,
}
const agents = [
  {
    agent_id: "agent_a",
    model_id: "claude-haiku-4-5",
    ...emptySettings,
    temperature: 0.2,
    provider_allow_fallbacks: true,
    max_tokens: 4096,
    task_count: 0,
    content_length: 12,
    updated_at: "2026-05-01T00:00:00Z",
  },
  {
    agent_id: "agent_b",
    model_id: "kimi-k2.6",
    quantization: "fp8",
    temperature: null,
    reasoning_effort: "none",
    provider_allow_fallbacks: false,
    provider_only: ["groq", "together"],
    provider_ignore: ["deepinfra"],
    provider_sort: "price",
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
      if (url === "/api/admin/agents/agent_b" && !init?.method) {
        return { ok: true, json: async () => ({ ...agents[1], content: "b prompt" }) } as Response
      }
      if (/^\/api\/admin\/agents\/agent_[ab]$/.test(url) && init?.method === "PUT") {
        putBodies.push(JSON.parse(String(init.body)))
        return { ok: true, status: 200, json: async () => ({ ...agents[0] }) } as Response
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

  // AST-1957 AC 10: seven plain settings inputs replace brain size + mode — Quantization, Temperature, Effort,
  // Allow provider fallbacks (checkbox), Provider only, Provider ignore, Provider sort — sent under the settings keys.
  describe("AST-1957 Manage Agents plain settings", () => {
    const textInput = (label: string) => within(field(label)).getByRole("textbox") as HTMLInputElement
    const tempInput = () => within(field("Temperature")).getByRole("spinbutton") as HTMLInputElement
    const maxTokInput = () => within(field("Max Tokens")).getByRole("spinbutton") as HTMLInputElement
    const fallbacks = () => screen.getByRole("checkbox", { name: /allow provider fallbacks/i }) as HTMLInputElement
    const textLabels = ["Quantization", "Effort", "Provider only", "Provider ignore", "Provider sort"]
    const headers = () =>
      screen.getAllByRole("columnheader").map(th => (th.textContent ?? "").replace(/[▲▼]/g, "").trim())
    const noRetiredControls = () => {
      for (const label of ["Brain size", "Mode"])
        expect(screen.queryByText(label, { selector: "label.dep-field-label" })).not.toBeInTheDocument()
    }

    it("list shows the settings columns, not Brain setting / Mode", async () => {
      mockApi()
      renderWithProviders(<AgentPrompts />)
      await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
      expect(headers()).toEqual(expect.arrayContaining(["Quant", "Temp", "Effort", "Fallbacks", "Only", "Ignore", "Sort"]))
      expect(headers()).not.toContain("Brain setting")
      expect(headers()).not.toContain("Mode")
      const rowA = screen.getByText("agent_a").closest("tr") as HTMLElement
      for (const cell of ["Claude Haiku 4.5", "0.2", "yes"]) expect(within(rowA).getByText(cell)).toBeInTheDocument()
      const rowB = screen.getByText("agent_b").closest("tr") as HTMLElement
      for (const cell of ["fp8", "none", "no", "groq, together", "deepinfra", "price"])
        expect(within(rowB).getByText(cell)).toBeInTheDocument()
    }, 15000)

    it("Add opens on the first model, empty settings with fallbacks on; Max Tokens placeholder follows the model", async () => {
      mockApi()
      renderWithProviders(<AgentPrompts />)
      await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: "+ Add Agent" }))
      noRetiredControls()
      expect(optionTexts("Model")).toEqual(["Claude Haiku 4.5", "Kimi K2.6"])
      expect(within(field("Model")).getByRole("combobox")).toHaveValue("claude-haiku-4-5")
      for (const label of textLabels) expect(textInput(label)).toHaveValue("")
      expect(tempInput()).toHaveValue(null)
      expect(fallbacks()).toBeChecked()
      // Empty max_tokens means the model default: shown as placeholder, never pre-filled.
      expect(maxTokInput()).toHaveValue(null)
      expect(maxTokInput()).toHaveAttribute("placeholder", "default 8192")
      await userEvent.selectOptions(within(field("Model")).getByRole("combobox"), "kimi-k2.6")
      expect(maxTokInput()).toHaveAttribute("placeholder", "default 16000")
      expect(maxTokInput()).toHaveValue(null)
    }, 20000)

    it("Add saves every setting under its key (trimmed, lists split) with no brain_setting or mode", async () => {
      mockApi()
      renderWithProviders(<AgentPrompts />)
      await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: "+ Add Agent" }))
      fireEvent.change(screen.getByPlaceholderText("e.g. job_analyst_grace"), { target: { value: "kimi agent" } })
      await userEvent.selectOptions(within(field("Model")).getByRole("combobox"), "kimi-k2.6")
      fireEvent.change(textInput("Quantization"), { target: { value: " bf16 " } })
      fireEvent.change(tempInput(), { target: { value: "0.7" } })
      fireEvent.change(textInput("Effort"), { target: { value: "high" } })
      await userEvent.click(fallbacks())
      fireEvent.change(textInput("Provider only"), { target: { value: " groq, together ,, " } })
      fireEvent.change(textInput("Provider sort"), { target: { value: "price" } })
      await userEvent.click(screen.getByRole("button", { name: "Save" }))
      await waitFor(() => expect(postBodies).toHaveLength(1))
      // Exact body: blank Provider ignore goes out as null; empty max_tokens is not sent.
      expect(postBodies[0]).toEqual({
        agent_id: "kimi_agent", content: "", model_id: "kimi-k2.6",
        quantization: "bf16", temperature: 0.7, reasoning_effort: "high", provider_allow_fallbacks: false,
        provider_only: ["groq", "together"], provider_ignore: null, provider_sort: "price",
      })
    }, 20000)

    it("AC 10: Edit renders the seven settings from the row and saves them under the settings keys", async () => {
      mockApi()
      renderWithProviders(<AgentPrompts />)
      await waitFor(() => expect(screen.getByText("agent_b")).toBeInTheDocument())
      await userEvent.click(screen.getByText("agent_b"))
      await waitFor(() => expect(screen.getByDisplayValue("b prompt")).toBeInTheDocument())
      noRetiredControls()
      expect(within(field("Model")).getByRole("combobox")).toHaveValue("kimi-k2.6")
      expect(textInput("Quantization")).toHaveValue("fp8")
      expect(tempInput()).toHaveValue(null)
      expect(textInput("Effort")).toHaveValue("none")
      expect(fallbacks()).not.toBeChecked()
      expect(textInput("Provider only")).toHaveValue("groq, together")
      expect(textInput("Provider ignore")).toHaveValue("deepinfra")
      expect(textInput("Provider sort")).toHaveValue("price")
      // Set temperature, clear two settings, turn fallbacks on.
      fireEvent.change(tempInput(), { target: { value: "0.3" } })
      fireEvent.change(textInput("Quantization"), { target: { value: "" } })
      fireEvent.change(textInput("Provider ignore"), { target: { value: "" } })
      await userEvent.click(fallbacks())
      await userEvent.click(screen.getByRole("button", { name: "Save" }))
      await waitFor(() => expect(putBodies).toHaveLength(1))
      // Every settings key is sent, so a cleared input clears the stored setting.
      expect(putBodies[0]).toEqual({
        content: "b prompt", max_tokens: 1024, model_id: "kimi-k2.6",
        quantization: null, temperature: 0.3, reasoning_effort: "none", provider_allow_fallbacks: true,
        provider_only: ["groq", "together"], provider_ignore: null, provider_sort: "price",
      })
    }, 20000)

    it("a row with every setting empty shows — in the list, blanks in Edit with fallbacks checked, and saves fallbacks true", async () => {
      const bare = { ...agents[0], ...emptySettings }
      installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
        if (url === "/api/candidates") return { ok: true, json: async () => [] } as Response
        if (url === "/api/admin/agents/meta/tokens") return { ok: true, json: async () => agentTokens } as Response
        if (url === "/api/admin/agents" && !init?.method) return { ok: true, json: async () => [bare] } as Response
        if (url === "/api/admin/agents/models") return { ok: true, json: async () => models } as Response
        if (url === "/api/admin/agents/agent_a" && !init?.method) {
          return { ok: true, json: async () => ({ ...bare, content: "system prompt" }) } as Response
        }
        if (url === "/api/admin/agents/agent_a" && init?.method === "PUT") {
          putBodies.push(JSON.parse(String(init.body)))
          return { ok: true, status: 200, json: async () => bare } as Response
        }
      })
      renderWithProviders(<AgentPrompts />)
      await waitFor(() => expect(screen.getByText("agent_a")).toBeInTheDocument())
      const row = screen.getByText("agent_a").closest("tr") as HTMLElement
      // One em dash per settings column.
      expect(within(row).getAllByText("—")).toHaveLength(7)
      await userEvent.click(screen.getByText("agent_a"))
      await waitFor(() => expect(screen.getByDisplayValue("system prompt")).toBeInTheDocument())
      for (const label of textLabels) expect(textInput(label)).toHaveValue("")
      expect(tempInput()).toHaveValue(null)
      // Stored null reads as the new-row default; Save writes it explicitly.
      expect(fallbacks()).toBeChecked()
      await userEvent.click(screen.getByRole("button", { name: "Save" }))
      await waitFor(() => expect(putBodies).toHaveLength(1))
      expect(putBodies[0]).toMatchObject({ ...emptySettings, provider_allow_fallbacks: true })
      expect(putBodies[0]).not.toHaveProperty("brain_setting")
      expect(putBodies[0]).not.toHaveProperty("mode")
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
