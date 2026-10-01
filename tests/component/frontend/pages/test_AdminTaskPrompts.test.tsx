import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import TaskPrompts from "../../../../src/ui/frontend/src/pages/AdminTaskPrompts"
import { installBaseApiMocks as installBase, jsonResponse, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

// AST-1909: model catalog (AST-1880 shape; jsonify sorts keys, `order` carries catalog order).
const models = {
  "kimi-k2.6": {
    order: 1,
    label: "Kimi K2.6",
    server_id: "kimi",
    server_label: "Kimi",
    brain_sizes: {
      Big: { order: 1, default_temperature: 1, default_max_tokens: 32000 },
      Little: { order: 0, default_temperature: 0.6, default_max_tokens: 8192 },
    },
  },
  claude: {
    order: 0,
    label: "Claude",
    server_id: "anthropic",
    server_label: "Anthropic",
    brain_sizes: {
      Big: { order: 2, default_temperature: 1, default_max_tokens: 32000 },
      Little: { order: 0, default_temperature: 0.7, default_max_tokens: 8192 },
      Medium: { order: 1, default_temperature: 0.2, default_max_tokens: 64000 },
    },
  },
}
const agentRows: Record<string, { agent_id: string; model_id: string; brain_setting: string }> = {
  agent_a: { agent_id: "agent_a", model_id: "claude", brain_setting: "Medium" },
  agent_b: { agent_id: "agent_b", model_id: "kimi-k2.6", brain_setting: "Big" },
}

/** Every test here also serves the catalog + agent GET/PUT the edit modal calls (AST-1909); test handlers win. */
function installBaseApiMocks(m: typeof mockedApi, handler: (url: string, init?: RequestInit) => unknown) {
  installBase(m, async (url: string, init?: RequestInit) => {
    const routed = await handler(url, init)
    if (routed !== undefined) return routed
    if (url === "/api/admin/agents/models") return jsonResponse(models)
    const agentId = /^\/api\/admin\/agents\/([^/?]+)$/.exec(url)?.[1]
    if (agentId && agentId !== "ids" && agentId !== "models") {
      if (init?.method === "PUT") return { ok: true, json: async () => ({}) } as Response
      const row = agentRows[agentId]
      return row
        ? ({ ok: true, status: 200, json: async () => row } as Response)
        : ({ ok: false, status: 404, json: async () => ({ error: `Agent not found: ${agentId}` }) } as Response)
    }
    return undefined
  })
}

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

  describe("AST-893 Expand One on Manage Tasks list", () => {
    const twoGroupTasks = [
      tasks[0],
      {
        ...tasks[1],
        task_group_order: "phase_two",
        task_group_name: "Phase Two",
      },
    ]

    function mockTwoGroups() {
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
        if (url.startsWith("/api/admin/tasks?") || url === "/api/admin/tasks") {
          return { json: async () => twoGroupTasks } as Response
        }
        if (url === "/api/admin/agents/ids") return { json: async () => ["agent_a", "agent_b"] } as Response
        if (url === "/api/admin/tasks/meta/tokens") return jsonResponse(["candidate_name"])
        if (url === "/api/admin/tasks/meta/chain_tokens") return jsonResponse([])
        if (url === "/api/admin/tasks/task_a" && !init?.method) {
          return {
            json: async () => ({
              ...twoGroupTasks[0],
              system_prompt: "",
              user_prompt: "user",
              cache_prompt: "cache",
              cache_prompt_b: "b0",
              cache_prompt_c: "c0",
              cache_prompt_d: "d0",
              nocache_prompt: "nocache",
            }),
          } as Response
        }
      })
    }

    it("opening a second list section closes the first; no Expand all chrome", async () => {
      mockTwoGroups()
      renderWithProviders(<TaskPrompts />)
      await waitFor(() => expect(screen.getByText("Manage Tasks")).toBeInTheDocument())
      expect(screen.getByText(/Phase One \(1\)/)).toBeInTheDocument()
      expect(screen.getByText(/Phase Two \(1\)/)).toBeInTheDocument()
      expect(screen.queryByRole("button", { name: "Expand all" })).not.toBeInTheDocument()
      expect(screen.queryByRole("button", { name: "Collapse all" })).not.toBeInTheDocument()

      const phaseOne = screen.getByText(/Phase One \(1\)/).closest(".collapsible-panel") as HTMLElement
      const phaseTwo = screen.getByText(/Phase Two \(1\)/).closest(".collapsible-panel") as HTMLElement
      await userEvent.click(within(phaseOne).getByRole("button", { name: "Expand section" }))
      await waitFor(() => expect(within(phaseOne).getByText("task_a")).toBeVisible())

      await userEvent.click(within(phaseTwo).getByRole("button", { name: "Expand section" }))
      await waitFor(() => expect(within(phaseTwo).getByText("task_b")).toBeVisible())
      expect(within(phaseOne).getByText("task_a")).not.toBeVisible()
    }, 20000)
  })

  describe("AST-1215 alphabetical run_next options", () => {
    it("edit modal run_next options are lexicographic even when tasks load unsorted", async () => {
      const unsorted = [
        {
          ...tasks[1],
          task_key: "zebra",
          task_key_uuid: "uuid-z",
          run_next: "",
          task_seq: 3,
          task_name: "zebra",
        },
        {
          ...tasks[0],
          task_key: "alpha",
          task_key_uuid: "uuid-a2",
          run_next: "mid",
          task_seq: 1,
          task_name: "alpha",
        },
        {
          ...tasks[1],
          task_key: "mid",
          task_key_uuid: "uuid-m",
          run_next: "",
          task_seq: 2,
          task_name: "mid",
        },
      ]
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
        if (url.startsWith("/api/admin/tasks?") || url === "/api/admin/tasks") {
          return { json: async () => unsorted } as Response
        }
        if (url === "/api/admin/agents/ids") return { json: async () => ["agent_a"] } as Response
        if (url === "/api/admin/tasks/meta/tokens") return jsonResponse(["candidate_name"])
        if (url === "/api/admin/tasks/meta/chain_tokens") return jsonResponse([])
        if (url === "/api/admin/tasks/alpha" && !init?.method) {
          return {
            json: async () => ({
              ...unsorted[1],
              system_prompt: "s",
              user_prompt: "u",
              cache_prompt: "c",
              cache_prompt_b: "",
              cache_prompt_c: "",
              cache_prompt_d: "",
              nocache_prompt: "n",
              run_next: "mid",
            }),
          } as Response
        }
      })
      renderWithProviders(<TaskPrompts />)
      await waitFor(() => expect(screen.getByText("Manage Tasks")).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
      await userEvent.click(screen.getByText("alpha"))
      await waitFor(() => expect(screen.getByRole("heading", { name: /Edit: alpha/ })).toBeInTheDocument())
      const editModal = screen.getByRole("heading", { name: /Edit: alpha/ }).closest(".modal-card") as HTMLElement
      const runNextSelect = within(editModal).getByDisplayValue("mid")
      const values = Array.from(runNextSelect.querySelectorAll("option"))
        .map(o => (o as HTMLOptionElement).value)
        .filter(Boolean)
      // Current task_key is omitted from run_next options (cycle guard); remaining keys stay alpha-sorted.
      expect(values).toEqual(["mid", "zebra"])
    }, 20000)
  })

  describe("AST-1410 silent refetch", () => {
    function hangTasksGet() {
      const inner = mockedApi.getMockImplementation()!
      let release: (value: Response) => void = () => {}
      mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
        if ((url === "/api/admin/tasks" || url.startsWith("/api/admin/tasks?")) && !init?.method) {
          return new Promise<Response>((resolve) => { release = resolve })
        }
        return inner(url, init)
      })
      return (body: unknown) => {
        release({ ok: true, json: async () => body } as Response)
      }
    }

    it("revert while edit overlay is open keeps the draft and skips Loading...", async () => {
      installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
        if (url === "/api/admin/repo_json/status") {
          return {
            ok: true,
            json: async () => ({
              agent: { diverged: false, repo_relative_path: "data/admin/agent.json" },
              agent_task: { diverged: true, repo_relative_path: "data/admin/agent_task.json" },
            }),
          } as Response
        }
        if (url === "/api/admin/repo_json/revert/agent_task" && init?.method === "POST") {
          return { ok: true, json: async () => ({ ok: true }) } as Response
        }
        if (url.startsWith("/api/admin/tasks?") || url === "/api/admin/tasks") {
          return { json: async () => tasks } as Response
        }
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
      })
      renderWithProviders(<TaskPrompts />)
      await waitFor(() => expect(screen.getByText("task_a")).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
      await userEvent.click(screen.getByText("task_a"))
      await waitFor(() => expect(screen.getByRole("heading", { name: /Edit: task_a/ })).toBeInTheDocument())
      const groupName = screen.getByDisplayValue("Phase One")
      await userEvent.type(groupName, " draft")
      const release = hangTasksGet()
      await userEvent.click(screen.getByRole("button", { name: "Revert to file" }))
      await waitFor(() => expect(screen.getByRole("alertdialog")).toBeInTheDocument())
      const confirms = screen.getAllByRole("button", { name: "Revert to file" })
      await userEvent.click(confirms[confirms.length - 1])
      await waitFor(() => expect(screen.getByRole("heading", { name: /Edit: task_a/ })).toBeInTheDocument())
      expect(screen.queryByText("Loading...")).not.toBeInTheDocument()
      expect(screen.getByDisplayValue("Phase One draft")).toBeInTheDocument()
      expect(screen.getByText("task_a")).toBeInTheDocument()
      release(tasks)
      await waitFor(() => expect(screen.getByRole("heading", { name: /Edit: task_a/ })).toBeInTheDocument())
      expect(screen.getByDisplayValue("Phase One draft")).toBeInTheDocument()
    }, 20000)
  })

  // AST-1909: Manage Task modal picks the task's agent's model + brain size (catalog-driven, saved on the agent).
  describe("AST-1909 task modal model + brain size", () => {
    /** Field select by its dep-field label (page pattern). */
    function selectByLabel(container: HTMLElement, label: string) {
      return within(container).getByText(label, { selector: "label" }).closest(".dep-field")!.querySelector("select") as HTMLSelectElement
    }
    const optionLabels = (sel: HTMLSelectElement) => Array.from(sel.options).map(o => o.textContent)
    const agentPuts = () => mockedApi.mock.calls.filter(([u, i]) => String(u).startsWith("/api/admin/agents/") && i?.method === "PUT")

    /** mockApi() plus an extra task on agent_a, so the hint counts 2. */
    function mockWithSharedAgent(taskOverrides: Record<string, unknown> = {}) {
      mockApi()
      const base = mockedApi.getMockImplementation()!
      const shared = [...tasks, { ...tasks[1], task_key: "task_c", task_key_uuid: "uuid-c", agent_id: "agent_a", task_name: "task_c", task_seq: 3 }]
      mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
        if ((url.startsWith("/api/admin/tasks?") || url === "/api/admin/tasks") && !init?.method) return { json: async () => shared } as Response
        if (url === "/api/admin/tasks/task_a" && !init?.method) {
          const r = await base(url, init) as Response
          const full = await r.json()
          return { json: async () => ({ ...full, ...taskOverrides }) } as Response
        }
        return base(url, init)
      })
    }

    async function openTaskA() {
      renderWithProviders(<TaskPrompts />)
      await waitFor(() => expect(screen.getByText("Manage Tasks")).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
      await userEvent.click(screen.getByText("task_a"))
      await waitFor(() => expect(screen.getByRole("heading", { name: /Edit: task_a/ })).toBeInTheDocument())
      return screen.getByRole("heading", { name: /Edit: task_a/ }).closest(".modal-card") as HTMLElement
    }

    it("selects show the agent's model + size in catalog order, with the shared-agent hint", async () => {
      mockWithSharedAgent()
      const modal = await openTaskA()
      await waitFor(() => expect(selectByLabel(modal, "Model")).toHaveValue("claude"))
      expect(optionLabels(selectByLabel(modal, "Model"))).toEqual(["Claude", "Kimi K2.6"])
      expect(selectByLabel(modal, "Brain size")).toHaveValue("Medium")
      expect(optionLabels(selectByLabel(modal, "Brain size"))).toEqual(["Little", "Medium", "Big"])
      expect(within(modal).getByText("Applies to agent agent_a — used by 2 task(s)")).toBeInTheDocument()
      // Read-only "Model: <sku>" line is gone.
      expect(within(modal).queryByText("Model:")).not.toBeInTheDocument()
      expect(mockedApi.mock.calls.some(([u]) => u === "/api/admin/agents/agent_a")).toBe(true)
    }, 20000)

    it("model change keeps the size when offered, else takes the first; Save PUTs task then agent", async () => {
      mockWithSharedAgent()
      const modal = await openTaskA()
      await waitFor(() => expect(selectByLabel(modal, "Model")).toHaveValue("claude"))
      await userEvent.selectOptions(selectByLabel(modal, "Model"), "kimi-k2.6")
      // Kimi has no Medium → first size.
      expect(selectByLabel(modal, "Brain size")).toHaveValue("Little")
      expect(optionLabels(selectByLabel(modal, "Brain size"))).toEqual(["Little", "Big"])
      await userEvent.selectOptions(selectByLabel(modal, "Brain size"), "Big")
      await userEvent.selectOptions(selectByLabel(modal, "Model"), "claude")
      // Claude offers Big → kept.
      expect(selectByLabel(modal, "Brain size")).toHaveValue("Big")
      await userEvent.click(within(modal).getByRole("button", { name: "Save" }))
      await waitFor(() => expect(screen.getByText(/Task "task_a" updated/)).toBeInTheDocument())
      const urls = mockedApi.mock.calls.map(([u, i]) => `${i?.method ?? "GET"} ${u}`)
      const taskPut = urls.indexOf("PUT /api/admin/tasks/task_a")
      const agentPut = urls.indexOf("PUT /api/admin/agents/agent_a")
      expect(taskPut).toBeGreaterThan(-1)
      expect(agentPut).toBeGreaterThan(taskPut)
      expect(agentPuts()).toHaveLength(1)
      expect(JSON.parse(String(agentPuts()[0][1]?.body))).toEqual({ model_id: "claude", brain_setting: "Big" })
      // List re-fetch after save.
      expect(urls.lastIndexOf("GET /api/admin/tasks")).toBeGreaterThan(agentPut)
    }, 20000)

    it("Save without a model/size change sends only the task PUT", async () => {
      mockWithSharedAgent()
      const modal = await openTaskA()
      await waitFor(() => expect(selectByLabel(modal, "Model")).toHaveValue("claude"))
      await userEvent.click(within(modal).getByRole("button", { name: "Save" }))
      await waitFor(() => expect(screen.getByText(/Task "task_a" updated/)).toBeInTheDocument())
      expect(agentPuts()).toHaveLength(0)
    }, 20000)

    it("changing the Agent select loads that agent's model + size and hint", async () => {
      mockWithSharedAgent()
      const modal = await openTaskA()
      await waitFor(() => expect(selectByLabel(modal, "Model")).toHaveValue("claude"))
      await userEvent.selectOptions(selectByLabel(modal, "Agent"), "agent_b")
      await waitFor(() => expect(selectByLabel(modal, "Model")).toHaveValue("kimi-k2.6"))
      expect(selectByLabel(modal, "Brain size")).toHaveValue("Big")
      expect(within(modal).getByText("Applies to agent agent_b — used by 1 task(s)")).toBeInTheDocument()
    }, 20000)

    it("no agent selected: Model disabled with — no agent —, Save sends no agent PUT", async () => {
      mockWithSharedAgent()
      const modal = await openTaskA()
      await waitFor(() => expect(selectByLabel(modal, "Model")).toHaveValue("claude"))
      await userEvent.selectOptions(selectByLabel(modal, "Agent"), "")
      await waitFor(() => expect(selectByLabel(modal, "Model")).toBeDisabled())
      expect(optionLabels(selectByLabel(modal, "Model"))).toContain("— no agent —")
      await userEvent.click(within(modal).getByRole("button", { name: "Save" }))
      await waitFor(() => expect(screen.getByText(/Task "task_a" updated/)).toBeInTheDocument())
      expect(agentPuts()).toHaveLength(0)
    }, 20000)

    it("agent row 404 (no such agent) also disables Model", async () => {
      mockWithSharedAgent({ agent_id: "ghost_agent" })
      const modal = await openTaskA()
      await waitFor(() => expect(mockedApi.mock.calls.some(([u]) => u === "/api/admin/agents/ghost_agent")).toBe(true))
      await waitFor(() => expect(selectByLabel(modal, "Model")).toBeDisabled())
      expect(optionLabels(selectByLabel(modal, "Model"))).toContain("— no agent —")
    }, 20000)

    it("agent PUT 400 surfaces its error in the toast after the task PUT", async () => {
      mockWithSharedAgent()
      const inner = mockedApi.getMockImplementation()!
      mockedApi.mockImplementation(async (url: string, init?: RequestInit) =>
        url === "/api/admin/agents/agent_a" && init?.method === "PUT"
          ? ({ ok: false, status: 400, json: async () => ({ error: "Brain size not offered for this model" }) } as Response)
          : inner(url, init),
      )
      const modal = await openTaskA()
      await waitFor(() => expect(selectByLabel(modal, "Model")).toHaveValue("claude"))
      await userEvent.selectOptions(selectByLabel(modal, "Brain size"), "Big")
      await userEvent.click(within(modal).getByRole("button", { name: "Save" }))
      await waitFor(() => expect(screen.getByText("Brain size not offered for this model")).toBeInTheDocument())
      expect(mockedApi.mock.calls.some(([u, i]) => u === "/api/admin/tasks/task_a" && i?.method === "PUT")).toBe(true)
      expect(agentPuts()).toHaveLength(1)
    }, 20000)
  })

})
