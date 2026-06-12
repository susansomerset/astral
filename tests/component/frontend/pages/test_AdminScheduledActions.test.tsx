import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import ScheduledActions from "../../../../src/ui/frontend/src/pages/AdminScheduledActions"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const dispatchTask = {
  id: 1,
  candidate_id: "c1",
  task_key: "scan_jobs",
  entity_type: "job",
  trigger_state: "NEW",
  freq_hrs: 1,
  min_count: 1,
  batch_size: 5,
  score_floor: 1.5,
  is_scored: true,
  auto_mode: 0,
  debug: 0,
  skip_cache: 0,
  max_runs: 0,
  last_run_at: "2026-05-01T00:00:00Z",
  updated_at: "2026-05-01T00:00:00Z",
  available_count: 12,
}

const taskKeysConfig = {
  scan_jobs: { entity_type: "job", trigger_state: "NEW", phase: "D. Job Analysis", seq: 2, is_scored: true },
  watch_cos: { entity_type: "company", trigger_state: "WATCH", phase: "C. Company Roster", seq: 1, is_scored: false },
}

const sparseRow = {
  ...dispatchTask,
  id: 2,
  task_key: "watch_cos",
  candidate_id: "c2",
  entity_type: null as string | null,
  trigger_state: null as string | null,
  batch_size: null as number | null,
  score_floor: null as number | null,
  freq_hrs: 0,
  max_runs: 0,
  available_count: null as number | null,
  is_scored: false,
  auto_mode: 1,
  debug: 1,
}

describe("AdminScheduledActions", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    vi.useFakeTimers({ shouldAdvanceTime: true })
    vi.spyOn(window, "alert").mockImplementation(() => {})
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  type ThreadEntry = { running: boolean; draining: boolean; task_key: string; candidate_id: string; is_auto: boolean }

  function mockApi(
    running = true,
    extra?: {
      tasks?: unknown[]
      threads?: Record<number, ThreadEntry>
      taskKeysPayload?: unknown
      stateOptionsPayload?: unknown
      threadStatusOk?: boolean
      putOk?: boolean
      postOk?: boolean
      runOk?: boolean
    },
  ) {
    const tasks = extra?.tasks ?? [dispatchTask]
    const threads = extra?.threads ?? {
      1: { running, draining: false, task_key: "scan_jobs", candidate_id: "c1", is_auto: false },
    }
    const keysDefault = { scan_jobs: { entity_type: "job", trigger_state: "NEW", phase: "D. Job Analysis", seq: 1, is_scored: true } }
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/admin/scheduler/thread_status") {
        if (extra?.threadStatusOk === false) return { ok: false, json: async () => ({}) } as Response
        return { ok: true, json: async () => threads } as Response
      }
      if (url === "/api/admin/dispatch_tasks" && !init?.method) return { ok: true, json: async () => tasks } as Response
      if (url === "/api/admin/dispatch_tasks/task_keys") {
        return { ok: true, json: async () => (extra?.taskKeysPayload !== undefined ? extra.taskKeysPayload : keysDefault) } as Response
      }
      if (url === "/api/admin/dispatch_tasks/state_options") {
        const def = { job: ["NEW", "READY"], company: ["WATCH"] }
        return { ok: true, json: async () => (extra?.stateOptionsPayload !== undefined ? extra.stateOptionsPayload : def) } as Response
      }
      if (url.endsWith("/run")) {
        if (extra?.runOk === false) return { ok: false, json: async () => ({ error: "run bad" }) } as Response
        return { ok: true, json: async () => ({}) } as Response
      }
      if (url.endsWith("/stop") || url === "/api/admin/scheduler/stop_all") return { ok: true, json: async () => ({}) } as Response
      if (url.startsWith("/api/admin/dispatch_tasks/") && init?.method === "PUT") {
        if (extra?.putOk === false) return { ok: false, json: async () => ({ error: "put bad" }) } as Response
        return { ok: true, json: async () => ({}) } as Response
      }
      if (url === "/api/admin/dispatch_tasks" && init?.method === "POST") {
        if (extra?.postOk === false) return { ok: false, json: async () => ({ error: "post bad" }) } as Response
        return { ok: true, json: async () => ({}) } as Response
      }
    })
  }

  async function expandFirstPhaseSection() {
    await waitFor(() =>
      expect(screen.getAllByRole("button", { name: "Expand section" }).length).toBeGreaterThan(0),
    )
    await userEvent.click(screen.getAllByRole("button", { name: "Expand section" })[0])
  }

  it("renders tasks, edits, runs, and stops threads", async () => {
    mockApi(true)
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
    await expandFirstPhaseSection()

    await userEvent.click(screen.getByRole("button", { name: "Stop All" }))
    await userEvent.click(screen.getByRole("button", { name: "Kill Now" }))
    await userEvent.click(within(screen.getByRole("table")).getByText("scan_jobs"))
    await waitFor(() => expect(screen.getByText("Edit Task")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    const tbody = within(screen.getByRole("table")).getAllByRole("rowgroup")[1]
    await userEvent.click(within(tbody).getAllByRole("button", { name: "OFF" })[0])
    await userEvent.click(within(tbody).getByRole("button", { name: "Stop" }))
  }, 20000)

  it("handles empty state", async () => {
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url === "/api/admin/scheduler/thread_status") return { ok: true, json: async () => ({}) } as Response
      if (url === "/api/admin/dispatch_tasks") return { ok: true, json: async () => [] } as Response
      if (url === "/api/admin/dispatch_tasks/task_keys") return { ok: true, json: async () => ({}) } as Response
      if (url === "/api/admin/dispatch_tasks/state_options") return { ok: true, json: async () => ({ job: [], company: [] }) } as Response
    })
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("No dispatch tasks configured")).toBeInTheDocument())
  }, 20000)

  it("normalizes task_keys and state_options payloads when api returns arrays / non-arrays", async () => {
    mockApi(false, {
      taskKeysPayload: [] as unknown as Record<string, unknown>,
      stateOptionsPayload: { job: "nope", company: 3 } as unknown as { job: string[]; company: string[] },
      threadStatusOk: false,
    })
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
  }, 20000)

  it("groups rows into phase sections and allows zero expanded", async () => {
    mockApi(false, {
      tasks: [dispatchTask, sparseRow],
      taskKeysPayload: taskKeysConfig,
      threads: {},
    })
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
    expect(screen.getByText(/D\. Job Analysis \(1\)/)).toBeInTheDocument()
    expect(screen.getByText(/C\. Company Roster \(1\)/)).toBeInTheDocument()
    expect(screen.queryByRole("table")).not.toBeInTheDocument()
    const jobPanel = screen.getByText(/D\. Job Analysis \(1\)/).closest(".collapsible-panel") as HTMLElement
    await userEvent.click(within(jobPanel).getByRole("button", { name: "Expand section" }))
    await waitFor(() => expect(within(jobPanel).getByText("scan_jobs")).toBeVisible())
    await userEvent.click(within(jobPanel).getByRole("button", { name: "Collapse section" }))
    expect(within(jobPanel).getByText("scan_jobs")).not.toBeVisible()
  }, 20000)

  it("sorts columns, filters task key, and shows row edge cases", async () => {
    mockApi(false, {
      tasks: [dispatchTask, sparseRow],
      taskKeysPayload: taskKeysConfig,
      threads: {
        1: { running: true, draining: true, task_key: "scan_jobs", candidate_id: "c1", is_auto: true },
      },
    })
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getAllByText("∞").length).toBeGreaterThan(0))
    await expandFirstPhaseSection()
    expect(screen.getAllByText("—").length).toBeGreaterThan(0)

    await userEvent.selectOptions(screen.getByLabelText(/Task/i, { selector: "select" }), "scan_jobs")
    await waitFor(() => expect(screen.queryByText(/C\. Company Roster/)).not.toBeInTheDocument())
    await expandFirstPhaseSection()
    await waitFor(() => expect(within(screen.getByRole("table")).queryByText("watch_cos")).not.toBeInTheDocument())

    await userEvent.selectOptions(screen.getByLabelText(/Task/i, { selector: "select" }), "")
    await userEvent.click(screen.getByRole("columnheader", { name: /Candidate/i }))
    await userEvent.click(screen.getByRole("columnheader", { name: /Candidate/i }))
    await userEvent.click(screen.getByRole("columnheader", { name: /Batch/i }))
  }, 20000)

  it("add task modal: company task sets WATCH state options", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    mockApi(false, { tasks: [dispatchTask], taskKeysPayload: taskKeysConfig })
    renderWithProviders(<ScheduledActions />)
    await expandFirstPhaseSection()
    await waitFor(() => expect(within(screen.getByRole("table")).getByText("scan_jobs")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "+ Add Task" }))
    const modal = screen.getByText("Add Task").closest(".modal-card") as HTMLElement
    const selects = within(modal).getAllByRole("combobox")
    await userEvent.selectOptions(selects[0], "watch_cos")
    const stateOptions = Array.from(selects[1].querySelectorAll("option")).map(o => o.textContent)
    expect(stateOptions).toContain("WATCH")
    await userEvent.click(within(modal).getByRole("button", { name: "Cancel" }))
  }, 20000)

  it("save disabled on add when no candidate selected", async () => {
    localStorage.clear()
    mockApi(false, { tasks: [dispatchTask], taskKeysPayload: taskKeysConfig })
    renderWithProviders(<ScheduledActions />)
    await expandFirstPhaseSection()
    await waitFor(() => expect(within(screen.getByRole("table")).getByText("scan_jobs")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "+ Add Task" }))
    expect(screen.getByRole("button", { name: "Save" })).toBeDisabled()
  }, 20000)

  it("alerts on auto toggle failure and run failure", async () => {
    const alertSpy = vi.spyOn(window, "alert").mockImplementation(() => {})
    mockApi(false, { putOk: false, runOk: false, threads: {} })
    renderWithProviders(<ScheduledActions />)
    await expandFirstPhaseSection()
    await waitFor(() => expect(within(screen.getByRole("table")).getByText("scan_jobs")).toBeInTheDocument())
    const tbody = within(screen.getByRole("table")).getAllByRole("rowgroup")[1]
    await userEvent.click(within(tbody).getAllByRole("button", { name: "OFF" })[0])
    await userEvent.click(within(tbody).getByRole("button", { name: "Run" }))
    expect(alertSpy.mock.calls.length).toBeGreaterThanOrEqual(2)
    alertSpy.mockRestore()
  }, 20000)

  it("alerts when edit save PUT fails", async () => {
    const alertSpy = vi.spyOn(window, "alert").mockImplementation(() => {})
    mockApi(false, { putOk: false, threads: {} })
    renderWithProviders(<ScheduledActions />)
    await expandFirstPhaseSection()
    await waitFor(() => expect(within(screen.getByRole("table")).getByText("scan_jobs")).toBeInTheDocument())
    await userEvent.click(within(screen.getByRole("table")).getByText("scan_jobs"))
    await waitFor(() => expect(screen.getByText("Edit Task")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    expect(alertSpy).toHaveBeenCalled()
    alertSpy.mockRestore()
  }, 20000)

  it("alerts when add save POST fails", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    const alertSpy = vi.spyOn(window, "alert").mockImplementation(() => {})
    installBaseApiMocks(mockedApi, async (url, init) => {
      if (url === "/api/admin/scheduler/thread_status") return { ok: true, json: async () => ({}) } as Response
      if (url === "/api/admin/dispatch_tasks" && !init?.method) return { ok: true, json: async () => [] } as Response
      if (url === "/api/admin/dispatch_tasks/task_keys") return { ok: true, json: async () => taskKeysConfig } as Response
      if (url === "/api/admin/dispatch_tasks/state_options") return { ok: true, json: async () => ({ job: ["NEW"], company: ["WATCH"] }) } as Response
      if (url === "/api/admin/dispatch_tasks" && init?.method === "POST") return { ok: false, json: async () => ({ error: "nope" }) } as Response
    })
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("No dispatch tasks configured")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "+ Add Task" }))
    const modal = screen.getByText("Add Task").closest(".modal-card") as HTMLElement
    const selects = within(modal).getAllByRole("combobox")
    await userEvent.selectOptions(selects[0], "scan_jobs")
    await userEvent.selectOptions(selects[1], "NEW")
    await userEvent.click(within(modal).getByRole("button", { name: "Save" }))
    expect(alertSpy).toHaveBeenCalled()
    alertSpy.mockRestore()
  }, 20000)

  it("stop-all modal: overlay and cancel close", async () => {
    mockApi(true, {
      threads: {
        1: { running: true, draining: false, task_key: "scan_jobs", candidate_id: "c1", is_auto: false },
      },
    })
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Stop All" }))
    await waitFor(() => expect(screen.getByText("Kill Running Threads")).toBeInTheDocument())
    await userEvent.click(screen.getByText("Kill Running Threads").closest(".modal-overlay") as HTMLElement)
    await waitFor(() => expect(screen.queryByText("Kill Running Threads")).not.toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "Stop All" }))
    await userEvent.click(screen.getByRole("button", { name: "Cancel" }))
  }, 20000)

  it("edit modal closes when overlay clicked", async () => {
    mockApi(false, { threads: {} })
    renderWithProviders(<ScheduledActions />)
    await expandFirstPhaseSection()
    await waitFor(() => expect(within(screen.getByRole("table")).getByText("scan_jobs")).toBeInTheDocument())
    await userEvent.click(within(screen.getByRole("table")).getByText("scan_jobs"))
    await waitFor(() => expect(screen.getByText("Edit Task")).toBeInTheDocument())
    await userEvent.click(screen.getByText("Edit Task").closest(".modal-overlay") as HTMLElement)
    await waitFor(() => expect(screen.queryByText("Edit Task")).not.toBeInTheDocument())
  }, 20000)

  it("reloads dispatch tasks when a manual run thread finishes", async () => {
    let poll = 0
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/admin/scheduler/thread_status") {
        poll += 1
        const running = poll === 1
        return {
          ok: true,
          json: async () => ({
            1: { running, draining: false, task_key: "scan_jobs", candidate_id: "c1", is_auto: false },
          }),
        } as Response
      }
      if (url === "/api/admin/dispatch_tasks" && !init?.method) {
        const avail = poll > 1 ? 99 : 12
        return { ok: true, json: async () => [{ ...dispatchTask, available_count: avail }] } as Response
      }
      if (url === "/api/admin/dispatch_tasks/task_keys") {
        return { ok: true, json: async () => taskKeysConfig } as Response
      }
      if (url === "/api/admin/dispatch_tasks/state_options") {
        return { ok: true, json: async () => ({ job: ["NEW"], company: ["WATCH"] }) } as Response
      }
    })
    renderWithProviders(<ScheduledActions />)
    await expandFirstPhaseSection()
    await waitFor(() => expect(screen.getByText("12")).toBeInTheDocument())
    await vi.advanceTimersByTimeAsync(5000)
    await waitFor(() => expect(screen.getByText("99")).toBeInTheDocument())
  }, 20000)
})
