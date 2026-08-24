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

const PREVIEW_TAB_LABELS = [
  "System",
  "Cache A",
  "Cache B",
  "Cache C",
  "Cache D",
  "No Cache",
  "User",
  "Live Content",
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

const defaultImportRuns = [
  {
    batch_id: "import-batch-1",
    created_at: "2026-01-01T12:00:00Z",
    entity_id: "job-1",
    task_key: "adhoc-task_a",
  },
  {
    batch_id: "import-batch-2",
    created_at: "2026-01-02T12:00:00Z",
    entity_id: "orphan-entity",
    task_key: "adhoc-evaluate_jd",
  },
]

describe("AdminAnthropicAdHoc", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  function mockApi(
    testResult?: { ok?: boolean; json: Record<string, unknown> },
    opts?: { importRuns?: typeof defaultImportRuns; agentDataByBatch?: Record<string, unknown[]> },
  ) {
    const testOk = testResult?.ok !== false
    const testJson = testResult?.json ?? {
      success: true,
      batch_id: "adhoc-batch-1",
      response_text: "{\"ok\":true}",
      timesheet: { duration: 1.2, inputtotal: 10, outputtotal: 5, inputcached: 2 },
    }
    const importRuns = opts?.importRuns ?? defaultImportRuns
    const agentDataByBatch = opts?.agentDataByBatch ?? {}
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/admin/adhoc/runs") {
        return { ok: true, json: async () => importRuns } as Response
      }
      if (url === "/api/admin/agents/ids") return { json: async () => ["agent_a"] } as Response
      if (url === "/api/admin/tasks/meta/tokens") return { json: async () => ["candidate_name"] } as Response
      if (url === "/api/admin/tasks" || url.startsWith("/api/admin/tasks?")) return { json: async () => tasks } as Response
      if (url.startsWith("/api/admin/adhoc/entities")) {
        return { ok: true, json: async () => ({ entity_type: "job", trigger_state: "NEW", batch_mode: false, entities: [{ id: "job-1", label: "Job 1" }] }) } as Response
      }
      if (url === "/api/admin/adhoc/preview" && init?.method === "POST") {
        return {
          ok: true,
          json: async () => ({
            system: "sys",
            cache: "alias-cache",
            cache_a: "cache A body",
            cache_b: "",
            cache_c: "",
            cache_d: "",
            nocache: "nocache",
            user: "user",
            live_content: "live",
          }),
        } as Response
      }
      if (url === "/api/admin/adhoc/test" && init?.method === "POST") {
        return { ok: testOk, json: async () => testJson } as Response
      }
      if (url.startsWith("/api/agent_data/")) {
        const batchId = decodeURIComponent(url.slice("/api/agent_data/".length))
        const blocks = agentDataByBatch[batchId] ?? [
          { agent_data_id: "1", block_type: "SYSTEM", block_data: "sys-block", token_size: 1, task_key: "t", created_at: "now" },
          { agent_data_id: "2", block_type: "RESPONSE", block_data: "{\"ok\":true}", token_size: 1, task_key: "t", created_at: "now" },
        ]
        return { ok: true, json: async () => blocks } as Response
      }
      if (url.startsWith("/api/admin/timesheets")) {
        return {
          json: async () => [
            {
              cache_write_tokens: 1,
              cache_read_tokens: 2,
              total_no_cache_input_tokens: 3,
              total_output_tokens: 4,
              calc_cost_cache_write: 0.1,
              calc_cost_cache_read: 0.2,
              calc_cost_no_cache_input: 0.3,
              calc_cost_output: 0.4,
            },
          ],
        } as Response
      }
      if (url.startsWith("/api/admin/dispatch_ledger/")) {
        return { ok: true, json: async () => ({ candidate_id: "c1", task_key: "task_a" }) } as Response
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
    expect(screen.queryByText("Resolved Prompt Preview")).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "▶ Test" }))
    await waitFor(() => expect(screen.getByText("Tokens & Cost")).toBeInTheDocument())
    fireEvent.change(screen.getByPlaceholderText("User prompt content..."), { target: { value: "existing content" } })
    await userEvent.click(screen.getByRole("button", { name: "Save As" }))
    const saveGroup = screen.getByRole("button", { name: "Save As" }).parentElement as HTMLElement
    await userEvent.click(within(saveGroup).getByText("task_b"))
  }, 20000)

  it("lists tasks against the selected candidate id", async () => {
    mockApi()
    renderWithProviders(<AnthropicAdHoc />)
    await waitFor(() =>
      expect(mockedApi.mock.calls.some(([u]) => String(u) === "/api/admin/tasks?candidate_id=c1")).toBe(true),
    )
  }, 15000)

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
      if (url === "/api/admin/adhoc/runs") return { ok: true, json: async () => [] } as Response
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

  it("AST-1394: successful Test mounts agent_data panes; not an ERROR overlay", async () => {
    mockApi({
      json: {
        success: true,
        batch_id: "adhoc-batch-1",
        response_text: JSON.stringify({ search_terms: "alpha\nbeta" }),
        timesheet: {},
      },
    })
    renderWithProviders(<AnthropicAdHoc />)
    await readyToTest()
    await userEvent.click(screen.getByRole("button", { name: "▶ Test" }))
    await waitFor(() => expect(screen.getByText("Tokens & Cost")).toBeInTheDocument())
    expect(screen.getByRole("button", { name: "RESPONSE" })).toBeInTheDocument()
    expect(screen.queryByText(/ERROR:/)).not.toBeInTheDocument()
  }, 20000)

  it("AST-1394: nested object response_text does not type-invalidate the page", async () => {
    mockApi({
      json: {
        success: true,
        batch_id: "adhoc-batch-1",
        response_text: { search_terms: "alpha" },
        timesheet: {},
      },
    })
    renderWithProviders(<AnthropicAdHoc />)
    await readyToTest()
    await userEvent.click(screen.getByRole("button", { name: "▶ Test" }))
    await waitFor(() => expect(screen.getByText("Tokens & Cost")).toBeInTheDocument())
    expect(screen.queryByText(/ERROR:/)).not.toBeInTheDocument()
  }, 20000)

  it("AST-1394: provider failure toasts; does not mount panes", async () => {
    mockApi({ ok: false, json: { success: false, error: "nope" } })
    renderWithProviders(<AnthropicAdHoc />)
    await readyToTest()
    await userEvent.click(screen.getByRole("button", { name: "▶ Test" }))
    await waitFor(() => expect(screen.getByText("nope")).toBeInTheDocument())
    expect(screen.queryByText("Tokens & Cost")).not.toBeInTheDocument()
    expect(screen.queryByText(/ERROR:/)).not.toBeInTheDocument()
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
    await waitFor(() => expect(screen.getByText("Tokens & Cost")).toBeInTheDocument())
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

  function agentDataGets(): string[] {
    return mockedApi.mock.calls.map(([u]) => String(u)).filter(u => u.startsWith("/api/agent_data/"))
  }

  it("AST-1413: Preview Prompt opens eight-tab modal; page has no inline preview block", async () => {
    mockApi()
    renderWithProviders(<AnthropicAdHoc />)
    await waitFor(() => expect(screen.getByText("Agent Ad Hoc")).toBeInTheDocument())
    expect(screen.queryByText("Resolved Prompt Preview")).not.toBeInTheDocument()
    await userEvent.selectOptions(screen.getAllByRole("combobox")[1], "agent_a")
    await userEvent.click(screen.getByRole("button", { name: "Preview Prompt" }))
    await waitFor(() => expect(screen.getByRole("heading", { name: "Preview" })).toBeInTheDocument())
    expect(screen.queryByText("Resolved Prompt Preview")).not.toBeInTheDocument()
    for (const label of PREVIEW_TAB_LABELS) {
      expect(screen.getByRole("button", { name: label })).toBeInTheDocument()
    }
    expect(screen.getByText("sys")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Cache A" }))
    expect(screen.getByText("cache A body")).toBeInTheDocument()
    expect(screen.queryByText("alias-cache")).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Cache B" }))
    expect(screen.getByText("(empty)")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Live Content" }))
    expect(screen.getByText("live")).toBeInTheDocument()
    expect(agentDataGets()).toEqual([])
    await userEvent.click(screen.getByRole("button", { name: "Cancel" }))
    await waitFor(() => expect(screen.queryByRole("heading", { name: "Preview" })).not.toBeInTheDocument())
  }, 20000)

  it("AST-1413: successful Test mounts panes; Preview does not clear them", async () => {
    mockApi()
    renderWithProviders(<AnthropicAdHoc />)
    await readyToTest()
    await userEvent.click(screen.getByRole("button", { name: "▶ Test" }))
    await waitFor(() => expect(screen.getByText("Tokens & Cost")).toBeInTheDocument())
    expect(screen.getByRole("button", { name: "SYSTEM" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "RESPONSE" })).toBeInTheDocument()
    const afterTest = agentDataGets().length
    expect(afterTest).toBeGreaterThan(0)
    await userEvent.click(screen.getByRole("button", { name: "Preview Prompt" }))
    await waitFor(() => expect(screen.getByRole("heading", { name: "Preview: task_a" })).toBeInTheDocument())
    expect(agentDataGets()).toHaveLength(afterTest)
    expect(screen.getByText("Tokens & Cost")).toBeInTheDocument()
  }, 20000)

  it("AST-1413: Test without batch_id toasts and leaves panes unmounted", async () => {
    mockApi({ json: { success: true, timesheet: {} } })
    renderWithProviders(<AnthropicAdHoc />)
    await readyToTest()
    await userEvent.click(screen.getByRole("button", { name: "▶ Test" }))
    await waitFor(() => expect(screen.getByText("Test succeeded without batch_id")).toBeInTheDocument())
    expect(screen.queryByText("Tokens & Cost")).not.toBeInTheDocument()
    expect(agentDataGets()).toEqual([])
  }, 20000)

  function taskGets(): string[] {
    return mockedApi.mock.calls
      .map(([u, init]) => [String(u), (init as RequestInit | undefined)?.method ?? "GET"] as const)
      .filter(([u, m]) => u.startsWith("/api/admin/tasks/") && m === "GET" && !u.includes("?"))
      .map(([u]) => u)
  }

  function importBlocks(batchId: string) {
    return [
      { agent_data_id: "s1", block_type: "SYSTEM", block_data: "imported-system", token_size: 1, task_key: "t", created_at: "now" },
      { agent_data_id: "a1", block_type: "CACHE_A", block_data: "imported-cache-a", token_size: 1, task_key: "t", created_at: "now" },
      { agent_data_id: "u1", block_type: "TASK", block_data: "imported-user", token_size: 1, task_key: "t", created_at: "now" },
      { agent_data_id: "r1", block_type: "RESPONSE", block_data: "{\"imported\":true}", token_size: 1, task_key: "t", created_at: "now" },
    ]
  }

  async function selectImportRow(batchId: string) {
    const row = screen.getByText(batchId === "import-batch-1" ? "2026-01-01T12:00:00Z" : "2026-01-02T12:00:00Z").closest("tr")
    expect(row).toBeTruthy()
    await userEvent.click(row as HTMLElement)
  }

  it("AST-1452: mount loads import runs into the table", async () => {
    mockApi(undefined, { importRuns: defaultImportRuns })
    renderWithProviders(<AnthropicAdHoc />)
    await waitFor(() =>
      expect(mockedApi.mock.calls.some(([u]) => String(u) === "/api/admin/adhoc/runs")).toBe(true),
    )
    expect(screen.getByRole("columnheader", { name: "timestamp" })).toBeInTheDocument()
    expect(screen.getByText("2026-01-01T12:00:00Z")).toBeInTheDocument()
    expect(screen.getByText("orphan-entity")).toBeInTheDocument()
    expect(screen.getByText("adhoc-evaluate_jd")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Load" })).toBeDisabled()
  }, 15000)

  it("AST-1452: Load fills editors and mounts panes for the imported batch", async () => {
    mockApi(undefined, {
      importRuns: defaultImportRuns,
      agentDataByBatch: { "import-batch-2": importBlocks("import-batch-2") },
    })
    renderWithProviders(<AnthropicAdHoc />)
    await waitFor(() => expect(screen.getByText("Agent Ad Hoc")).toBeInTheDocument())
    await selectImportRow("import-batch-2")
    expect(screen.getByRole("button", { name: "Load" })).toBeEnabled()
    await userEvent.click(screen.getByRole("button", { name: "Load" }))
    await waitFor(() => expect(screen.getByText("Loaded agent data import-batch-2")).toBeInTheDocument())
    expect(screen.getByDisplayValue("imported-system")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Cache Block A" }))
    expect(screen.getByDisplayValue("imported-cache-a")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Cache Block B" }))
    expect(screen.getByPlaceholderText("Cache block B (optional).")).toHaveValue("")
    await userEvent.click(screen.getByRole("button", { name: "User Prompt" }))
    expect(screen.getByDisplayValue("imported-user")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "RESPONSE" })).toBeInTheDocument()
    expect(agentDataGets()).toContain("/api/agent_data/import-batch-2")
  }, 20000)

  it("AST-1452: Load strips one adhoc- prefix without catalog fetch-from-task", async () => {
    mockApi(undefined, {
      importRuns: defaultImportRuns,
      agentDataByBatch: { "import-batch-2": importBlocks("import-batch-2") },
    })
    renderWithProviders(<AnthropicAdHoc />)
    await waitFor(() => expect(screen.getByText("Agent Ad Hoc")).toBeInTheDocument())
    await selectImportRow("import-batch-2")
    await userEvent.click(screen.getByRole("button", { name: "Load" }))
    await waitFor(() => expect(screen.getByDisplayValue("imported-system")).toBeInTheDocument())
    expect(taskGets()).not.toContain("/api/admin/tasks/evaluate_jd")
    expect(screen.queryByText(/Loaded prompts from "evaluate_jd"/)).not.toBeInTheDocument()
    await userEvent.selectOptions(screen.getAllByRole("combobox")[1], "agent_a")
    await userEvent.click(screen.getByRole("button", { name: "Preview Prompt" }))
    await waitFor(() => expect(screen.getByRole("heading", { name: "Preview: evaluate_jd" })).toBeInTheDocument())
  }, 20000)

  it("AST-1452: importEntityLock sends restored entity_id on Preview", async () => {
    mockApi(undefined, {
      importRuns: defaultImportRuns,
      agentDataByBatch: { "import-batch-2": importBlocks("import-batch-2") },
    })
    renderWithProviders(<AnthropicAdHoc />)
    await waitFor(() => expect(screen.getByText("Agent Ad Hoc")).toBeInTheDocument())
    await selectImportRow("import-batch-2")
    await userEvent.click(screen.getByRole("button", { name: "Load" }))
    await waitFor(() => expect(screen.getByDisplayValue("imported-system")).toBeInTheDocument())
    expect(screen.getAllByRole("combobox")[2]).toHaveValue("orphan-entity")
    await userEvent.selectOptions(screen.getAllByRole("combobox")[1], "agent_a")
    await userEvent.click(screen.getByRole("button", { name: "Preview Prompt" }))
    await waitFor(() => expect(screen.getByRole("heading", { name: "Preview: evaluate_jd" })).toBeInTheDocument())
    const preview = lastJsonBody("/api/admin/adhoc/preview", "POST")
    expect(preview.entity_id).toBe("orphan-entity")
    expect(preview.entity_ids).toBeUndefined()
  }, 20000)

  it("AST-1452: dirty editors confirm Load; Cancel leaves content unchanged", async () => {
    mockApi(undefined, {
      importRuns: defaultImportRuns,
      agentDataByBatch: { "import-batch-2": importBlocks("import-batch-2") },
    })
    renderWithProviders(<AnthropicAdHoc />)
    await waitFor(() => expect(screen.getByText("Agent Ad Hoc")).toBeInTheDocument())
    fireEvent.change(screen.getByPlaceholderText("User prompt content..."), { target: { value: "keep-me" } })
    await selectImportRow("import-batch-2")
    await userEvent.click(screen.getByRole("button", { name: "Load" }))
    expect(screen.getByText("Replace current prompt content with imported run?")).toBeInTheDocument()
    const loadGetsBeforeCancel = agentDataGets().length
    await userEvent.click(screen.getByRole("button", { name: "Cancel" }))
    expect(screen.queryByText("Replace current prompt content with imported run?")).not.toBeInTheDocument()
    expect(screen.getByDisplayValue("keep-me")).toBeInTheDocument()
    expect(agentDataGets()).toHaveLength(loadGetsBeforeCancel)
    expect(screen.queryByRole("button", { name: "RESPONSE" })).not.toBeInTheDocument()
  }, 20000)

  it("AST-1452: dirty confirm Yes replaces editor content", async () => {
    mockApi(undefined, {
      importRuns: defaultImportRuns,
      agentDataByBatch: { "import-batch-2": importBlocks("import-batch-2") },
    })
    renderWithProviders(<AnthropicAdHoc />)
    await waitFor(() => expect(screen.getByText("Agent Ad Hoc")).toBeInTheDocument())
    fireEvent.change(screen.getByPlaceholderText("User prompt content..."), { target: { value: "draft" } })
    await selectImportRow("import-batch-2")
    await userEvent.click(screen.getByRole("button", { name: "Load" }))
    await userEvent.click(screen.getByRole("button", { name: "Yes, Replace" }))
    await waitFor(() => expect(screen.getByDisplayValue("imported-system")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "User Prompt" }))
    expect(screen.getByDisplayValue("imported-user")).toBeInTheDocument()
    expect(screen.queryByDisplayValue("draft")).not.toBeInTheDocument()
  }, 20000)
})
