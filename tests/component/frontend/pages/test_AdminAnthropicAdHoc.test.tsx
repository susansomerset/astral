import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AnthropicAdHoc from "../../../../src/ui/frontend/src/pages/AdminAnthropicAdHoc"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const SEGMENT_KEYS = [
  "system_prompt",
  "user_prompt",
  "cache_prompt",
  "cache_prompt_b",
  "cache_prompt_c",
  "cache_prompt_d",
  "nocache_prompt",
] as const

const EDITOR_TAB_LABELS = [
  "System Prompt",
  "Cache Block A",
  "Cache Block B",
  "Cache Block C",
  "Cache Block D",
  "No Cache Block",
  "User Prompt",
]

const emptyLens = {
  user_prompt_len: 0,
  cache_prompt_len: 0,
  cache_prompt_b_len: 0,
  cache_prompt_c_len: 0,
  cache_prompt_d_len: 0,
  nocache_prompt_len: 0,
  system_prompt_len: 0,
}

const tasks = [
  { task_key: "task_a", ...emptyLens, user_prompt_len: 1 },
  { task_key: "task_b", ...emptyLens },
  { task_key: "task_b_only", ...emptyLens, cache_prompt_b_len: 4 },
]

describe("AdminAnthropicAdHoc", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  function mockApi(testResult?: { ok?: boolean; json: Record<string, unknown> }) {
    const testOk = testResult?.ok !== false
    const testJson = testResult?.json ?? {
      success: true,
      response_text: "{\"ok\":true}",
      timesheet: { duration: 1.2, inputtotal: 10, outputtotal: 5, inputcached: 2 },
    }
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/admin/agents/ids") return { json: async () => ["agent_a"] } as Response
      if (url === "/api/admin/tasks/meta/tokens") return { json: async () => ["candidate_name"] } as Response
      if (url === "/api/admin/tasks" || url.startsWith("/api/admin/tasks?")) return { json: async () => tasks } as Response
      if (url.startsWith("/api/admin/adhoc/entities")) {
        return { ok: true, json: async () => ({ entity_type: "job", trigger_state: "NEW", batch_mode: false, entities: [{ id: "job-1", label: "Job 1" }] }) } as Response
      }
      if (url === "/api/admin/adhoc/preview" && init?.method === "POST") {
        return { ok: true, json: async () => ({ system: "sys", cache: "cache", nocache: "nocache", user: "user", live_content: "live" }) } as Response
      }
      if (url === "/api/admin/adhoc/test" && init?.method === "POST") {
        return { ok: testOk, json: async () => testJson } as Response
      }
      if (url === "/api/admin/tasks/task_a") {
        return {
          json: async () => ({
            system_prompt: "loaded system",
            user_prompt: "loaded user",
            cache_prompt: "loaded cache A",
            cache_prompt_b: "loaded cache B",
            cache_prompt_c: "loaded cache C",
            cache_prompt_d: "loaded cache D",
            nocache_prompt: "loaded nocache",
          }),
        } as Response
      }
      if (url === "/api/admin/tasks/task_b_only" && init?.method !== "PUT") {
        return { json: async () => ({ cache_prompt_b: "only B" }) } as Response
      }
      if (url === "/api/admin/tasks/task_b" && init?.method === "PUT") return { ok: true, json: async () => ({}) } as Response
      if (url === "/api/admin/tasks/task_b_only" && init?.method === "PUT") return { ok: true, json: async () => ({}) } as Response
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

  it("AST-1215: Task Key select and Save As list are lexicographic despite unsorted /tasks", async () => {
    const unsortedTasks = [
      { task_key: "zebra", user_prompt_len: 0, cache_prompt_len: 0, nocache_prompt_len: 0 },
      { task_key: "alpha", user_prompt_len: 1, cache_prompt_len: 0, nocache_prompt_len: 0 },
      { task_key: "mid", user_prompt_len: 0, cache_prompt_len: 0, nocache_prompt_len: 0 },
    ]
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url === "/api/admin/agents/ids") return { json: async () => ["agent_a"] } as Response
      if (url === "/api/admin/tasks/meta/tokens") return { json: async () => ["candidate_name"] } as Response
      if (url === "/api/admin/tasks" || url.startsWith("/api/admin/tasks?")) return { json: async () => unsortedTasks } as Response
      if (url.startsWith("/api/admin/adhoc/entities")) {
        return {
          ok: true,
          json: async () => ({
            entity_type: "job",
            trigger_state: "NEW",
            batch_mode: false,
            entities: [{ id: "job-1", label: "Job 1" }],
          }),
        } as Response
      }
      if (url === "/api/candidates") {
        return {
          json: async () => [
            { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { first: "Jane", last: "Doe" } },
          ],
        } as Response
      }
    })
    renderWithProviders(<AnthropicAdHoc />)
    await waitFor(() => expect(screen.getByText("Agent Ad Hoc")).toBeInTheDocument())
    const taskSelect = screen.getAllByRole("combobox")[0]
    const selectValues = Array.from(taskSelect.querySelectorAll("option"))
      .map(o => (o as HTMLOptionElement).value)
      .filter(Boolean)
    expect(selectValues).toEqual(["alpha", "mid", "zebra"])

    // Save As stays disabled until a prompt has content.
    fireEvent.change(screen.getByPlaceholderText("User prompt content..."), {
      target: { value: "draft content" },
    })
    await userEvent.click(screen.getByRole("button", { name: "Save As" }))
    const saveGroup = screen.getByRole("button", { name: "Save As" }).parentElement as HTMLElement
    const menuKeys = Array.from(saveGroup.querySelectorAll("div"))
      .map(d => (d.textContent || "").replace(/\s*●\s*$/, "").trim())
      .filter(t => t === "alpha" || t === "mid" || t === "zebra")
    expect(menuKeys).toEqual(["alpha", "mid", "zebra"])
  }, 15000)

  async function readyToTest() {
    await waitFor(() => expect(screen.getByText("Agent Ad Hoc")).toBeInTheDocument())
    await userEvent.selectOptions(screen.getAllByRole("combobox")[0], "task_a")
    await waitFor(() => expect(screen.getByText(/Loaded prompts from "task_a"/)).toBeInTheDocument())
    await waitFor(() => expect(screen.getAllByRole("combobox").length).toBeGreaterThanOrEqual(3))
    await userEvent.selectOptions(screen.getAllByRole("combobox")[1], "agent_a")
    await userEvent.selectOptions(screen.getAllByRole("combobox")[2], "job-1")
  }

  it("AST-1394: object payload JSON text pretty-prints; success is not ERROR", async () => {
    mockApi({
      json: {
        success: true,
        response_text: JSON.stringify({ search_terms: "alpha\nbeta" }),
        timesheet: {},
      },
    })
    renderWithProviders(<AnthropicAdHoc />)
    await readyToTest()
    await userEvent.click(screen.getByRole("button", { name: "▶ Test" }))
    await waitFor(() => expect(screen.getByText(/"search_terms"/)).toBeInTheDocument())
    expect(screen.queryByText(/ERROR:/)).not.toBeInTheDocument()
  }, 20000)

  it("AST-1394: nested object response_text still displays; never type-invalidates", async () => {
    // Defense: Stage 1 should emit a string; coerce-to-text must still render an object.
    mockApi({
      json: {
        success: true,
        response_text: { search_terms: "alpha" },
        timesheet: {},
      },
    })
    renderWithProviders(<AnthropicAdHoc />)
    await readyToTest()
    await userEvent.click(screen.getByRole("button", { name: "▶ Test" }))
    await waitFor(() => expect(screen.getByText(/"search_terms"/)).toBeInTheDocument())
    expect(screen.queryByText(/ERROR:/)).not.toBeInTheDocument()
  }, 20000)

  it("AST-1394: plain text displays unchanged", async () => {
    mockApi({ json: { success: true, response_text: "plain ok", timesheet: {} } })
    renderWithProviders(<AnthropicAdHoc />)
    await readyToTest()
    await userEvent.click(screen.getByRole("button", { name: "▶ Test" }))
    await waitFor(() => expect(screen.getByText("plain ok")).toBeInTheDocument())
    expect(screen.queryByText(/ERROR:/)).not.toBeInTheDocument()
  }, 20000)

  it("AST-1394: provider failure still shows ERROR overlay", async () => {
    mockApi({ ok: false, json: { success: false, error: "nope" } })
    renderWithProviders(<AnthropicAdHoc />)
    await readyToTest()
    await userEvent.click(screen.getByRole("button", { name: "▶ Test" }))
    await waitFor(() => expect(screen.getByText(/ERROR: nope/)).toBeInTheDocument())
  }, 20000)

  function lastJsonBody(url: string, method: string): Record<string, unknown> {
    const hits = mockedApi.mock.calls.filter(
      ([u, init]) => u === url && (init as RequestInit | undefined)?.method === method,
    )
    expect(hits.length).toBeGreaterThan(0)
    return JSON.parse(String((hits[hits.length - 1][1] as RequestInit).body))
  }

  function expectSevenSegmentKeys(body: Record<string, unknown>) {
    for (const key of SEGMENT_KEYS) {
      expect(body).toHaveProperty(key)
      expect(typeof body[key]).toBe("string")
    }
  }

  it("AST-1412: seven editor tabs match Manage Tasks labels", async () => {
    mockApi()
    renderWithProviders(<AnthropicAdHoc />)
    await waitFor(() => expect(screen.getByText("Agent Ad Hoc")).toBeInTheDocument())
    for (const label of EDITOR_TAB_LABELS) {
      expect(screen.getByRole("button", { name: label })).toBeInTheDocument()
    }
  }, 15000)

  it("AST-1412: Cache B loads into B not A; Save As lights from B-only content", async () => {
    mockApi()
    renderWithProviders(<AnthropicAdHoc />)
    await waitFor(() => expect(screen.getByText("Agent Ad Hoc")).toBeInTheDocument())
    await userEvent.selectOptions(screen.getAllByRole("combobox")[0], "task_b_only")
    await waitFor(() =>
      expect(screen.getByText(/Loaded prompts from "task_b_only"/)).toBeInTheDocument(),
    )
    await userEvent.click(screen.getByRole("button", { name: "Cache Block B" }))
    expect(screen.getByDisplayValue("only B")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Cache Block A" }))
    expect(screen.queryByDisplayValue("only B")).not.toBeInTheDocument()
    expect(screen.getByPlaceholderText("Cache block A (ephemeral cached at API when non-empty).")).toHaveValue("")
    expect(screen.getByRole("button", { name: "Save As" })).toBeEnabled()
  }, 20000)

  it("AST-1412: Preview, Test, and Save As send all seven keys; empty System is empty string", async () => {
    mockApi()
    renderWithProviders(<AnthropicAdHoc />)
    await waitFor(() => expect(screen.getByText("Agent Ad Hoc")).toBeInTheDocument())
    await userEvent.selectOptions(screen.getAllByRole("combobox")[1], "agent_a")
    await userEvent.click(screen.getByRole("button", { name: "Cache Block B" }))
    fireEvent.change(screen.getByPlaceholderText("Cache block B (optional)."), { target: { value: "only B" } })

    await userEvent.click(screen.getByRole("button", { name: "Preview Prompt" }))
    await waitFor(() => expect(screen.getByText("sys")).toBeInTheDocument())
    const preview = lastJsonBody("/api/admin/adhoc/preview", "POST")
    expectSevenSegmentKeys(preview)
    expect(preview.system_prompt).toBe("")
    expect(preview.cache_prompt).toBe("")
    expect(preview.cache_prompt_b).toBe("only B")

    await userEvent.click(screen.getByRole("button", { name: "▶ Test" }))
    await waitFor(() => expect(screen.getByText(/"ok": true/)).toBeInTheDocument())
    const testBody = lastJsonBody("/api/admin/adhoc/test", "POST")
    expectSevenSegmentKeys(testBody)
    expect(testBody.system_prompt).toBe("")
    expect(testBody.cache_prompt).toBe("")
    expect(testBody.cache_prompt_b).toBe("only B")

    await userEvent.click(screen.getByRole("button", { name: "Save As" }))
    const saveGroup = screen.getByRole("button", { name: "Save As" }).parentElement as HTMLElement
    await userEvent.click(within(saveGroup).getByText("task_b"))
    await waitFor(() => expect(screen.getByText(/Prompts saved to "task_b"/)).toBeInTheDocument())
    const put = lastJsonBody("/api/admin/tasks/task_b", "PUT")
    expectSevenSegmentKeys(put)
    expect(put.system_prompt).toBe("")
    expect(put.cache_prompt).toBe("")
    expect(put.cache_prompt_b).toBe("only B")
  }, 20000)

  it("AST-1412: overwrite marker treats Cache-B-only list lens as existing content", async () => {
    mockApi()
    renderWithProviders(<AnthropicAdHoc />)
    await waitFor(() => expect(screen.getByText("Agent Ad Hoc")).toBeInTheDocument())
    fireEvent.change(screen.getByPlaceholderText("User prompt content..."), { target: { value: "draft" } })
    await userEvent.click(screen.getByRole("button", { name: "Save As" }))
    const saveGroup = screen.getByRole("button", { name: "Save As" }).parentElement as HTMLElement
    expect(within(saveGroup).getByText("task_b_only ●")).toBeInTheDocument()
    expect(within(saveGroup).getByText("task_b")).toBeInTheDocument()
    expect(within(saveGroup).queryByText("task_b ●")).not.toBeInTheDocument()
  }, 15000)
})
