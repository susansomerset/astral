import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import TaskPrompts from "../../../../src/ui/frontend/src/pages/AdminTaskPrompts"
import { installBaseApiMocks, jsonResponse, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const tasks = [
  {
    task_key: "task_a",
    task_key_uuid: "uuid-a",
    agent_id: "agent_a",
    run_next: "task_b",
    task_group_order: "phase_one",
    task_group_name: "Phase One",
    task_seq: 1,
    task_name: "task_a",
    model_code: "claude",
    system_prompt_tokens: 10,
    base_cache_tokens: 20,
    parsed_cache_tokens: null,
    cache_min_tokens: 100,
    cache_satisfied: false,
    nocache_prompt_tokens: 30,
    avg_live_tokens: null,
    avg_output_tokens: 5,
    task_ready: false,
    updated_at: "2026-05-01T00:00:00Z",
  },
  {
    task_key: "task_b",
    task_key_uuid: "uuid-b",
    agent_id: "agent_b",
    run_next: "",
    task_group_order: "phase_one",
    task_group_name: "Phase One",
    task_seq: 2,
    task_name: "task_b",
    model_code: "claude",
    system_prompt_tokens: 11,
    base_cache_tokens: 21,
    parsed_cache_tokens: 22,
    cache_min_tokens: 101,
    cache_satisfied: true,
    nocache_prompt_tokens: 31,
    avg_live_tokens: 40,
    avg_output_tokens: null,
    task_ready: true,
    updated_at: "2026-05-02T00:00:00Z",
  },
]

describe("AdminTaskPrompts", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

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
      if (url.startsWith("/api/admin/tasks?") || url === "/api/admin/tasks") return { json: async () => tasks } as Response
      if (url === "/api/admin/agents/ids") return { json: async () => ["agent_a", "agent_b"] } as Response
      if (url === "/api/admin/tasks/meta/tokens") return jsonResponse(["candidate_name"])
      if (url === "/api/admin/tasks/meta/chain_tokens") return jsonResponse([])
      if (url === "/api/admin/tasks/task_a" && !init?.method) {
        return {
          json: async () => ({
            ...tasks[0],
            system_prompt: "{$SELECTED_AGENT}",
            user_prompt: "user",
            cache_prompt: "cache",
            cache_prompt_b: "b0",
            cache_prompt_c: "c0",
            cache_prompt_d: "d0",
            nocache_prompt: "nocache",
            run_next: "task_b",
          }),
        } as Response
      }
      if (url === "/api/admin/tasks/task_a" && init?.method === "PUT") return { ok: true, json: async () => ({}) } as Response
      if (url.startsWith("/api/admin/tasks/task_a/preview")) {
        return {
          ok: true,
          json: async () => ({
            candidate_id: "c1",
            system: "resolved system",
            user: "resolved user",
            cache: "resolved cache",
            cache_a: "ra",
            cache_b: "rb",
            cache_c: "",
            cache_d: "",
            nocache: "resolved nocache",
          }),
        } as Response
      }
    })
  }

  it("loads grouped tasks and edits, previews, and saves", async () => {
    localStorage.setItem("astral_admin_task_prompts_default_expanded", "cache")
    mockApi()
    renderWithProviders(<TaskPrompts />)
    await waitFor(() => expect(screen.getByText("Manage Tasks")).toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    await userEvent.click(screen.getByText("task_a"))
    await waitFor(() => expect(screen.getByDisplayValue("cache")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Preview Resolved" }))
    await waitFor(() => expect(screen.getByText("resolved system")).toBeInTheDocument())
    const closes = screen.getAllByRole("button", { name: "Close" })
    await userEvent.click(closes[closes.length - 1])
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText(/Task "task_a" updated/)).toBeInTheDocument())
    const putCall = mockedApi.mock.calls.find(
      ([url, init]) => url === "/api/admin/tasks/task_a" && init?.method === "PUT",
    )
    expect(putCall).toBeTruthy()
    const body = JSON.parse(String(putCall?.[1]?.body))
    expect(body.system_prompt).toBe("{$SELECTED_AGENT}")
  }, 20000)

  it("shows System Prompt panel and persists system_prompt on save", async () => {
    localStorage.setItem("astral_admin_task_prompts_default_expanded", "system")
    mockApi()
    renderWithProviders(<TaskPrompts />)
    await waitFor(() => expect(screen.getByText("Manage Tasks")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    await userEvent.click(screen.getByText("task_a"))
    await waitFor(() => expect(screen.getByDisplayValue("{$SELECTED_AGENT}")).toBeInTheDocument())
    const systemArea = screen.getByPlaceholderText(/Empty = use assigned agent content/)
    await userEvent.clear(systemArea)
    await userEvent.type(systemArea, "custom system")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText(/Task "task_a" updated/)).toBeInTheDocument())
    const putCall = mockedApi.mock.calls.find(
      ([url, init]) => url === "/api/admin/tasks/task_a" && init?.method === "PUT",
    )
    expect(JSON.parse(String(putCall?.[1]?.body)).system_prompt).toBe("custom system")
  }, 20000)

  it("allows zero expanded grouping sections on the list page", async () => {
    mockApi()
    renderWithProviders(<TaskPrompts />)
    await waitFor(() => expect(screen.getByText("Manage Tasks")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    await waitFor(() => expect(screen.getByText("task_a")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Collapse section" }))
    const taskCell = screen.getByText("task_a")
    expect(taskCell).not.toBeVisible()
  }, 20000)

  it("allows zero expanded prompt panels in the edit modal", async () => {
    localStorage.setItem("astral_admin_task_prompts_default_expanded", "user")
    mockApi()
    renderWithProviders(<TaskPrompts />)
    await waitFor(() => expect(screen.getByText("Manage Tasks")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    await userEvent.click(screen.getByText("task_a"))
    await waitFor(() => expect(screen.getByDisplayValue("user")).toBeInTheDocument())
    const editHeading = screen.getByRole("heading", { name: /Edit: task_a/ })
    const editModal = editHeading.closest(".modal-card")!
    await userEvent.click(within(editModal).getByRole("button", { name: "Collapse section" }))
    for (const val of ["user", "cache", "b0", "c0", "d0", "nocache", "{$SELECTED_AGENT}"]) {
      expect(within(editModal).getByDisplayValue(val)).not.toBeVisible()
    }
  }, 20000)

  it("AST-456: seven edit panels, chain_tokens fetched, preview cache B tab, PUT cache_prompt_d", async () => {
    localStorage.setItem("astral_admin_task_prompts_default_expanded", "cache_d")
    mockApi()
    renderWithProviders(<TaskPrompts />)
    await waitFor(() => expect(screen.getByText("Manage Tasks")).toBeInTheDocument())
    await waitFor(() =>
      expect(mockedApi.mock.calls.some(([u]) => String(u) === "/api/admin/tasks/meta/chain_tokens")).toBe(true),
    )

    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    await userEvent.click(screen.getByText("task_a"))
    await waitFor(() => expect(screen.getByDisplayValue("d0")).toBeInTheDocument())
    const editHeading = screen.getByRole("heading", { name: /Edit: task_a/ })
    const editPanels = editHeading.closest(".modal-card")!.querySelector(".admin-task-prompts-edit-panels")!
    expect(within(editPanels as HTMLElement).getByText("System Prompt")).toBeInTheDocument()
    expect(within(editPanels as HTMLElement).getByText("Cache Block A")).toBeInTheDocument()
    expect(within(editPanels as HTMLElement).getByText("Cache Block B")).toBeInTheDocument()
    expect(within(editPanels as HTMLElement).getByText("Cache Block C")).toBeInTheDocument()
    expect(within(editPanels as HTMLElement).getByText("Cache Block D")).toBeInTheDocument()
    expect(within(editPanels as HTMLElement).getByText("No Cache Block")).toBeInTheDocument()
    expect(within(editPanels as HTMLElement).getByText("User Prompt")).toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: "Preview Resolved" }))
    await waitFor(() => expect(screen.getByRole("heading", { name: /Preview: task_a/ })).toBeInTheDocument())
    const previewCard = screen.getByRole("heading", { name: /Preview: task_a/ }).closest(".modal-card")!
    await userEvent.click(within(previewCard).getByRole("button", { name: "Cache Block B" }))
    await waitFor(() => expect(within(previewCard).getByText("rb")).toBeInTheDocument())

    await userEvent.click(screen.getAllByRole("button", { name: "Close" }).pop()!)

    const dTa = screen.getByPlaceholderText(/Cache block D \(optional\)/)
    await userEvent.clear(dTa)
    await userEvent.type(dTa, "d-segment-updated")

    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText(/Task "task_a" updated/)).toBeInTheDocument())
    const putCall = mockedApi.mock.calls.find(
      ([url, init]) => url === "/api/admin/tasks/task_a" && init?.method === "PUT",
    )
    const body = JSON.parse(String(putCall?.[1]?.body))
    expect(body.cache_prompt_d).toBe("d-segment-updated")
    expect(body.cache_prompt_b).toBe("b0")
    expect(body.cache_prompt).toBe("cache")
  }, 25000)


  it("AST-739: shows task_name, grouping sections, and persists grouping fields on save", async () => {
    localStorage.setItem("astral_admin_task_prompts_default_expanded", "user")
    mockApi()
    renderWithProviders(<TaskPrompts />)
    await waitFor(() => expect(screen.getByText("Manage Tasks")).toBeInTheDocument())
    expect(screen.getByText(/Phase One \(2\)/)).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    await userEvent.click(screen.getByText("task_a"))
    const editModal = screen.getByRole("heading", { name: /Edit: task_a/ }).closest(".modal-card")!
    await waitFor(() => expect(within(editModal).getByDisplayValue("phase_one")).toBeInTheDocument())
    const groupName = within(editModal).getByDisplayValue("Phase One")
    await userEvent.clear(groupName)
    await userEvent.type(groupName, "Renamed Group")
    const seqInput = within(editModal).getByRole("spinbutton")
    await userEvent.clear(seqInput)
    await userEvent.type(seqInput, "9")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText(/Task "task_a" updated/)).toBeInTheDocument())
    const putCall = mockedApi.mock.calls.find(
      ([url, init]) => url === "/api/admin/tasks/task_a" && init?.method === "PUT",
    )
    const body = JSON.parse(String(putCall?.[1]?.body))
    expect(body.task_group_order).toBe("phase_one")
    expect(body.task_group_name).toBe("Renamed Group")
    expect(body.task_seq).toBe(9)
    expect(body.task_name).toBe("task_a")
  }, 20000)

  it("handles load failures", async () => {
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url.includes("/api/admin/tasks")) throw new Error("tasks failed")
      if (url === "/api/admin/agents/ids") return { json: async () => [] } as Response
      if (url === "/api/admin/tasks/meta/tokens") return jsonResponse([])
      if (url === "/api/admin/tasks/meta/chain_tokens") return jsonResponse([])
    })
    renderWithProviders(<TaskPrompts />)
    await waitFor(() => expect(screen.getByText("No tasks configured.")).toBeInTheDocument())
  }, 15000)

  it("appends astral_job_id to preview when job entity task has job id filled (AST-513)", async () => {
    const jobTasks = [
      {
        ...tasks[0],
        task_key: "contemplate_job",
        task_name: "contemplate_job",
        entity_type: "job",
      },
    ]
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url.startsWith("/api/admin/tasks?") || url === "/api/admin/tasks") return { json: async () => jobTasks } as Response
      if (url === "/api/admin/agents/ids") return { json: async () => ["agent_a"] } as Response
      if (url === "/api/admin/tasks/meta/tokens") return jsonResponse(["VISIBLE_JD"])
      if (url === "/api/admin/tasks/meta/chain_tokens") return jsonResponse([])
      if (url === "/api/admin/tasks/contemplate_job" && !init?.method) {
        return {
          json: async () => ({
            ...jobTasks[0],
            system_prompt: "",
            user_prompt: "user",
            cache_prompt: "",
            nocache_prompt: "",
            entity_type: "job",
          }),
        } as Response
      }
      if (url.startsWith("/api/admin/tasks/contemplate_job/preview")) {
        return { ok: true, json: async () => ({ system: "resolved", user: "u", cache: "", nocache: "" }) } as Response
      }
    })
    renderWithProviders(<TaskPrompts />)
    await waitFor(() => expect(screen.getByText("Manage Tasks")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    await userEvent.click(screen.getByText("contemplate_job"))
    await waitFor(() => expect(screen.getByPlaceholderText("astral job id")).toBeInTheDocument())
    await userEvent.type(screen.getByPlaceholderText("astral job id"), "job-513")
    await userEvent.click(screen.getByRole("button", { name: "Preview Resolved" }))
    await waitFor(() =>
      expect(
        mockedApi.mock.calls.some(([url]) =>
          String(url).includes("/api/admin/tasks/contemplate_job/preview") &&
          String(url).includes("astral_job_id=job-513"),
        ),
      ).toBe(true),
    )
  }, 20000)

  it("AST-783: shows task repo JSON divergence banner on routed page", async () => {
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url === "/api/admin/repo_json/status") {
        return {
          ok: true,
          json: async () => ({
            agent: { diverged: false, repo_relative_path: "data/admin/agent.json" },
            agent_task: { diverged: true, repo_relative_path: "data/admin/agent_task.json" },
          }),
        } as Response
      }
      if (url.startsWith("/api/admin/tasks?") || url === "/api/admin/tasks") return { json: async () => tasks } as Response
      if (url === "/api/admin/agents/ids") return { json: async () => ["agent_a", "agent_b"] } as Response
    })
    renderWithProviders(<TaskPrompts />)
    await waitFor(() => expect(screen.getByText(/task prompts/)).toBeInTheDocument())
    expect(screen.getByRole("button", { name: "Revert to file" })).toBeInTheDocument()
  }, 15000)
})
