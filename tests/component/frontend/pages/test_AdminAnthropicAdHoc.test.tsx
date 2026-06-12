import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AnthropicAdHoc from "../../../../src/ui/frontend/src/pages/AdminAnthropicAdHoc"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const tasks = [
  { task_key: "task_a", user_prompt_len: 1, cache_prompt_len: 0, nocache_prompt_len: 0 },
  { task_key: "task_b", user_prompt_len: 0, cache_prompt_len: 0, nocache_prompt_len: 0 },
]

describe("AdminAnthropicAdHoc", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  function mockApi() {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/admin/agents/ids") return { json: async () => ["agent_a"] } as Response
      if (url === "/api/admin/tasks/meta/tokens") return { json: async () => ["candidate_name"] } as Response
      if (url === "/api/admin/tasks") return { json: async () => tasks } as Response
      if (url.startsWith("/api/admin/adhoc/entities")) {
        return { ok: true, json: async () => ({ entity_type: "job", trigger_state: "NEW", batch_mode: false, entities: [{ id: "job-1", label: "Job 1" }] }) } as Response
      }
      if (url === "/api/admin/adhoc/preview" && init?.method === "POST") {
        return { ok: true, json: async () => ({ system: "sys", cache: "cache", nocache: "nocache", user: "user", live_content: "live" }) } as Response
      }
      if (url === "/api/admin/adhoc/test" && init?.method === "POST") {
        return { ok: true, json: async () => ({ success: true, response_text: "{\"ok\":true}", timesheet: { duration: 1.2, inputtotal: 10, outputtotal: 5, inputcached: 2 } }) } as Response
      }
      if (url === "/api/admin/tasks/task_a") {
        return { json: async () => ({ user_prompt: "loaded user", cache_prompt: "loaded cache", nocache_prompt: "loaded nocache" }) } as Response
      }
      if (url === "/api/admin/tasks/task_b" && init?.method === "PUT") return { ok: true, json: async () => ({}) } as Response
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { first: "Jane", last: "Doe" } }] } as Response
      }
    })
  }

  it("previews, tests, fetches prompts, and saves as", async () => {
    mockApi()
    renderWithProviders(<AnthropicAdHoc />)
    await waitFor(() => expect(screen.getByText("Agent Ad Hoc")).toBeInTheDocument())

    await userEvent.selectOptions(screen.getAllByRole("combobox")[0], "task_a")
    await waitFor(() =>
      expect(screen.getByText(/Loaded prompts from "task_a"/)).toBeInTheDocument(),
    )
    await waitFor(() => expect(screen.getAllByRole("combobox").length).toBeGreaterThanOrEqual(3))
    await userEvent.selectOptions(screen.getAllByRole("combobox")[1], "agent_a")
    await userEvent.selectOptions(screen.getAllByRole("combobox")[2], "job-1")
    await userEvent.click(screen.getByRole("button", { name: "Preview Prompt" }))
    await waitFor(() => expect(screen.getByText("sys")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "▶ Test" }))
    await waitFor(() => expect(screen.getByText(/"ok": true/)).toBeInTheDocument())
    fireEvent.change(screen.getByPlaceholderText("User prompt content..."), { target: { value: "existing content" } })
    await userEvent.click(screen.getByRole("button", { name: "Save As" }))
    const saveGroup = screen.getByRole("button", { name: "Save As" }).parentElement as HTMLElement
    await userEvent.click(within(saveGroup).getByText("task_b"))
  }, 20000)

  it("requires an agent before preview and test", async () => {
    mockApi()
    renderWithProviders(<AnthropicAdHoc />)
    await waitFor(() => expect(screen.getByText("Agent Ad Hoc")).toBeInTheDocument())
    expect(screen.getByRole("button", { name: "Preview Prompt" })).toBeDisabled()
    expect(screen.getByRole("button", { name: "▶ Test" })).toBeDisabled()
  }, 15000)
})
