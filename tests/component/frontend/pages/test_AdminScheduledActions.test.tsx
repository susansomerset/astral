import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import { useCandidate } from "../../../../src/ui/frontend/src/contexts/CandidateContext"
import ScheduledActions from "../../../../src/ui/frontend/src/pages/AdminScheduledActions"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const adminCandidates = [
  { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { first: "Ada", last: "One" } },
  { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: { first: "Betty", last: "Two" } },
]

function CandidateSelectC2() {
  const { setSelectedId } = useCandidate()
  return (
    <button type="button" onClick={() => setSelectedId("c2")}>
      Select c2 nav
    </button>
  )
}

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
  scan_jobs: { entity_type: "job", trigger_state: "NEW", task_group_order: "D. Job Analysis", task_group_name: "D. Job Analysis", task_seq: 2, task_name: "scan_jobs", is_scored: true },
  watch_cos: { entity_type: "company", trigger_state: "WATCH", task_group_order: "C. Company Roster", task_group_name: "C. Company Roster", task_seq: 1, task_name: "watch_cos", is_scored: false },
}

const defaultScoreFloorOptions = Array.from({ length: 21 }, (_, i) => (i * 0.5).toFixed(2))

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
      candidates?: unknown[]
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
    const candidates = extra?.candidates ?? adminCandidates
    const threads = extra?.threads ?? {
      1: { running, draining: false, task_key: "scan_jobs", candidate_id: "c1", is_auto: false },
    }
    const keysDefault = { scan_jobs: { entity_type: "job", trigger_state: "NEW", task_group_order: "D. Job Analysis", task_group_name: "D. Job Analysis", task_seq: 1, task_name: "scan_jobs", is_scored: true } }
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { ok: true, json: async () => candidates } as Response
      }
      if (url === "/api/admin/scheduler/thread_status") {
        if (extra?.threadStatusOk === false) return { ok: false, json: async () => ({}) } as Response
        return { ok: true, json: async () => threads } as Response
      }
      if (url === "/api/admin/dispatch_tasks" && !init?.method) return { ok: true, json: async () => tasks } as Response
      if (url === "/api/admin/dispatch_tasks/task_keys") {
        return { ok: true, json: async () => (extra?.taskKeysPayload !== undefined ? extra.taskKeysPayload : keysDefault) } as Response
      }
      if (url === "/api/admin/dispatch_tasks/state_options") {
        const def = { job: ["NEW", "READY"], company: ["WATCH"], candidate: [] }
        return { ok: true, json: async () => (extra?.stateOptionsPayload !== undefined ? extra.stateOptionsPayload : def) } as Response
      }
      if (url === "/api/admin/dispatch_tasks/score_floor_options") {
        return { ok: true, json: async () => ({ values: defaultScoreFloorOptions }) } as Response
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

  async function selectAllCandidatesFilter() {
    const candidateSelect = await screen.findByLabelText("Candidate", { selector: "select" })
    await userEvent.selectOptions(candidateSelect, "")
  }

  async function expandFirstPhaseSection() {
    // AST-785 auto-opens the first section — wait for table or Expand (race-safe).
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
    await waitFor(() => {
      if (screen.queryByRole("table")) return
      expect(screen.getAllByRole("button", { name: "Expand section" }).length).toBeGreaterThan(0)
    })
    if (screen.queryByRole("table")) return
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
      if (url === "/api/admin/dispatch_tasks/state_options") return { ok: true, json: async () => ({ job: [], company: [], candidate: [] }) } as Response
      if (url === "/api/admin/dispatch_tasks/score_floor_options") return { ok: true, json: async () => ({ values: defaultScoreFloorOptions }) } as Response
    })
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("No dispatch tasks configured")).toBeInTheDocument())
  }, 20000)

  it("normalizes task_keys and state_options payloads when api returns arrays / non-arrays", async () => {
    mockApi(false, {
      taskKeysPayload: [] as unknown as Record<string, unknown>,
      stateOptionsPayload: { job: "nope", company: 3, candidate: 7 } as unknown as { job: string[]; company: string[]; candidate: string[] },
      threadStatusOk: false,
    })
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
  }, 20000)

  it("groups rows into DB grouping sections and allows zero expanded", async () => {
    mockApi(false, {
      tasks: [dispatchTask, sparseRow],
      taskKeysPayload: taskKeysConfig,
      threads: {},
    })
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
    await selectAllCandidatesFilter()
    expect(screen.getByText(/D\. Job Analysis \(0 \/ 1 AUTO\)/)).toBeInTheDocument()
    expect(screen.getByText(/C\. Company Roster \(1 \/ 1 AUTO\)/)).toBeInTheDocument()
    const rosterPanel = screen.getByText(/C\. Company Roster \(1 \/ 1 AUTO\)/).closest(".collapsible-panel") as HTMLElement
    await waitFor(() => expect(within(rosterPanel).getByText("watch_cos")).toBeVisible())
    await userEvent.click(within(rosterPanel).getByRole("button", { name: "Collapse section" }))
    await waitFor(() => expect(within(rosterPanel).queryByText("watch_cos")).not.toBeInTheDocument())
    expect(screen.queryByRole("table")).not.toBeInTheDocument()
    const jobPanel = screen.getByText(/D\. Job Analysis \(0 \/ 1 AUTO\)/).closest(".collapsible-panel") as HTMLElement
    await userEvent.click(within(jobPanel).getByRole("button", { name: "Expand section" }))
    await waitFor(() => expect(within(jobPanel).getByText("scan_jobs")).toBeVisible())
    await userEvent.click(within(jobPanel).getByRole("button", { name: "Collapse section" }))
    await waitFor(() => expect(within(jobPanel).queryByText("scan_jobs")).not.toBeInTheDocument())
  }, 20000)


  it("AST-739: task_keys grouping metadata drives section labels", async () => {
    mockApi(false, {
      tasks: [dispatchTask, sparseRow],
      taskKeysPayload: taskKeysConfig,
      threads: {},
    })
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
    await selectAllCandidatesFilter()
    expect(screen.getByText(/D\. Job Analysis \(0 \/ 1 AUTO\)/)).toBeInTheDocument()
    expect(screen.getByText(/C\. Company Roster \(1 \/ 1 AUTO\)/)).toBeInTheDocument()
    expect(screen.queryByText(/phase/i)).not.toBeInTheDocument()
  }, 20000)

  it("AST-749: grade_do row groups under task_keys metadata not (unassigned)", async () => {
    const gradeDoTask = {
      ...dispatchTask,
      id: 3,
      task_key: "grade_do",
      trigger_state: "PASSED_JD",
      candidate_id: "c1",
      auto_mode: 0,
    }
    const gradeKeys = {
      grade_do: {
        entity_type: "job",
        trigger_state: "PASSED_JD",
        task_group_order: "D. Job Analysis",
        task_group_name: "D. Job Analysis",
        task_seq: 2,
        task_name: "grade_do",
        is_scored: true,
      },
    }
    mockApi(false, { tasks: [gradeDoTask], taskKeysPayload: gradeKeys, threads: {} })
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
    await selectAllCandidatesFilter()
    expect(screen.getByText(/D\. Job Analysis \(0 \/ 1 AUTO\)/)).toBeInTheDocument()
    expect(screen.queryByText("(unassigned)")).not.toBeInTheDocument()
  }, 20000)

  it("AST-647: phase table freezes first three data columns", async () => {
    mockApi(false, { tasks: [dispatchTask], taskKeysPayload: taskKeysConfig, threads: {} })
    renderWithProviders(<ScheduledActions />)
    await expandFirstPhaseSection()
    await waitFor(() => expect(within(screen.getByRole("table")).getByText("scan_jobs")).toBeInTheDocument())
    const headers = within(screen.getByRole("table")).getAllByRole("columnheader")
    expect(headers[0]).toHaveClass("list-table-cell-frozen")
    expect(headers[1]).toHaveClass("list-table-cell-frozen")
    expect(headers[2]).toHaveClass("list-table-cell-frozen")
    expect(headers[3]).not.toHaveClass("list-table-cell-frozen")
    const row = within(screen.getByRole("table")).getAllByRole("row")[1]
    const cells = within(row).getAllByRole("cell")
    expect(cells[0]).toHaveClass("list-table-cell-frozen")
    expect(cells[1]).toHaveClass("list-table-cell-frozen")
    expect(cells[2]).toHaveClass("list-table-cell-frozen")
    expect(cells[3]).not.toHaveClass("list-table-cell-frozen")
  }, 20000)

  it("AST-746: phase table mounts on expand; measured sticky left avoids 120px fallback gap", async () => {
    mockApi(false, { tasks: [dispatchTask], taskKeysPayload: taskKeysConfig, threads: {} })
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
    await selectAllCandidatesFilter()

    await expandFirstPhaseSection()
    await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
    const table = screen.getByRole("table")
    const headers = within(table).getAllByRole("columnheader")
    // jsdom offsetWidth is 0 on first paint — must not apply erroneous 120px sticky fallback on Task.
    expect(headers[1].style.left).not.toBe("120px")
    expect(headers[3]).not.toHaveClass("list-table-cell-frozen")
    expect(headers[3].style.left).toBe("")

    const headerCells = table.querySelector("thead tr")!.querySelectorAll("th")
    Object.defineProperty(headerCells[0], "offsetWidth", { configurable: true, value: 88 })
    Object.defineProperty(headerCells[1], "offsetWidth", { configurable: true, value: 72 })
    Object.defineProperty(headerCells[2], "offsetWidth", { configurable: true, value: 56 })
    await userEvent.click(headers[0])
    await waitFor(() => expect(headers[1].style.left).toBe("88px"))
    expect(parseFloat(headers[1].style.left)).toBeLessThan(120)
    expect(headers[2].style.left).toBe("160px")
    expect(headers[3].style.left).toBe("")
  }, 20000)

  it("AST-760: frozen headers use left-only sticky; Entity does not width-lock over State", async () => {
    mockApi(false, { tasks: [dispatchTask], taskKeysPayload: taskKeysConfig, threads: {} })
    renderWithProviders(<ScheduledActions />)
    await expandFirstPhaseSection()
    await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
    const table = screen.getByRole("table")
    const headers = within(table).getAllByRole("columnheader")
    expect(headers[2].style.width).toBe("")
    expect(headers[2].style.minWidth).toBe("")
    expect(headers[3]).not.toHaveClass("list-table-cell-frozen")
    expect(headers[3].style.left).toBe("")

    const headerCells = table.querySelector("thead tr")!.querySelectorAll("th")
    Object.defineProperty(headerCells[0], "offsetWidth", { configurable: true, value: 88 })
    Object.defineProperty(headerCells[1], "offsetWidth", { configurable: true, value: 72 })
    Object.defineProperty(headerCells[2], "offsetWidth", { configurable: true, value: 56 })
    await userEvent.click(headers[0])
    await waitFor(() => expect(headers[2].style.left).toBe("160px"))
    expect(headers[2].style.width).toBe("")
    expect(headers[2].style.minWidth).toBe("")
    expect(headers[3].style.left).toBe("")
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
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
    await selectAllCandidatesFilter()
    await expandFirstPhaseSection()
    await waitFor(() => expect(screen.getAllByText("∞").length).toBeGreaterThan(0))
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
    mockApi(false, { tasks: [dispatchTask], taskKeysPayload: taskKeysConfig, candidates: [] })
    renderWithProviders(<ScheduledActions />)
    await expandFirstPhaseSection()
    await waitFor(() => expect(within(screen.getByRole("table")).getByText("scan_jobs")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "+ Add Task" }))
    const modal = screen.getByText("Add Task").closest(".modal-card") as HTMLElement
    expect(within(modal).getByRole("button", { name: "Save" })).toBeDisabled()
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
      if (url === "/api/admin/dispatch_tasks/score_floor_options") {
        return { ok: true, json: async () => ({ values: defaultScoreFloorOptions }) } as Response
      }
    })
    renderWithProviders(<ScheduledActions />)
    await expandFirstPhaseSection()
    await waitFor(() => expect(screen.getByText("12")).toBeInTheDocument())
    await vi.advanceTimersByTimeAsync(5000)
    await waitFor(() => expect(screen.getByText("99")).toBeInTheDocument())
  }, 20000)

  describe("AST-634 admin candidate filter", () => {
    beforeEach(() => {
      vi.useRealTimers()
    })
    afterEach(() => {
      vi.useFakeTimers({ shouldAdvanceTime: true })
    })

    it("defaults to nav candidate, All shows every candidate, manual All blocks nav sync", async () => {
      localStorage.setItem("astral_selected_candidate", "c1")
      mockApi(false, {
        tasks: [dispatchTask, sparseRow],
        taskKeysPayload: taskKeysConfig,
        threads: {},
      })
      renderWithProviders(
        <>
          <CandidateSelectC2 />
          <ScheduledActions />
        </>,
      )
      await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
      const candidateSelect = screen.getByLabelText("Candidate", { selector: "select" }) as HTMLSelectElement
      await waitFor(() => expect(candidateSelect.value).toBe("c1"))

      await expandFirstPhaseSection()
      expect(within(screen.getByRole("table")).getByText("scan_jobs")).toBeInTheDocument()
      expect(within(screen.getByRole("table")).queryByText("watch_cos")).not.toBeInTheDocument()

      await userEvent.selectOptions(candidateSelect, "")
      await expandFirstPhaseSection()
      await waitFor(() => expect(screen.getByText(/C\. Company Roster/)).toBeInTheDocument())

      await userEvent.click(screen.getByRole("button", { name: "Select c2 nav" }))
      expect(candidateSelect.value).toBe("")
    }, 25000)

    it("nav sync updates default filter when Susan has not manually changed dropdown", async () => {
      localStorage.setItem("astral_selected_candidate", "c1")
      mockApi(false, {
        tasks: [dispatchTask, sparseRow],
        taskKeysPayload: taskKeysConfig,
        threads: {},
      })
      renderWithProviders(
        <>
          <CandidateSelectC2 />
          <ScheduledActions />
        </>,
      )
      await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
      const candidateSelect = screen.getByLabelText("Candidate", { selector: "select" }) as HTMLSelectElement
      await waitFor(() => expect(candidateSelect.value).toBe("c1"))
      await userEvent.click(screen.getByRole("button", { name: "Select c2 nav" }))
      await waitFor(() => expect(candidateSelect.value).toBe("c2"))
    }, 15000)
  })

  const scanJobsC1Auto = {
    ...dispatchTask,
    id: 10,
    candidate_id: "c1",
    task_key: "scan_jobs",
    auto_mode: 1,
    debug: 0,
    available_count: 12,
    score_floor: 1.5,
    freq_hrs: 1,
    min_count: 1,
    batch_size: 5,
    max_runs: 0,
  }
  const scanJobsC2Off = {
    ...dispatchTask,
    id: 11,
    candidate_id: "c2",
    task_key: "scan_jobs",
    auto_mode: 0,
    debug: 1,
    available_count: 5,
    score_floor: 2.0,
    freq_hrs: 2,
    min_count: 2,
    batch_size: 3,
    max_runs: 1,
  }
  const watchCosZeroAvail = {
    ...sparseRow,
    id: 12,
    available_count: 0,
    auto_mode: 1,
    debug: 0,
  }

  function adminFiltersRoot(): HTMLElement {
    const el = document.querySelector(".admin-filters")
    if (!el) throw new Error("admin-filters missing")
    return el as HTMLElement
  }

  async function selectFilterByLabel(label: string, value: string) {
    const select = within(adminFiltersRoot()).getByLabelText(label)
    await userEvent.selectOptions(select, value)
  }

  describe("AST-751 filters, AUTO summary, and All-candidate layout", () => {
    const multiRows = [scanJobsC1Auto, scanJobsC2Off, watchCosZeroAvail]

    it("section header shows AUTO-on count over filtered rows", async () => {
      mockApi(false, { tasks: multiRows, taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
      await selectAllCandidatesFilter()
      expect(screen.getByText(/D\. Job Analysis \(1 \/ 2 AUTO\)/)).toBeInTheDocument()
      expect(screen.getByText(/C\. Company Roster \(1 \/ 1 AUTO\)/)).toBeInTheDocument()
    }, 20000)

    it("AUTO filter narrows visible rows when Candidate is All", async () => {
      mockApi(false, { tasks: multiRows, taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      await selectFilterByLabel("AUTO", "on")
      const jobPanel = screen.getByText(/D\. Job Analysis \(1 \/ 1 AUTO\)/).closest(".collapsible-panel") as HTMLElement
      await userEvent.click(within(jobPanel).getByRole("button", { name: "Expand section" }))
      await waitFor(() => expect(within(jobPanel).getByText("c1")).toBeVisible())
      expect(within(jobPanel).queryByText("c2")).not.toBeInTheDocument()
    }, 20000)

    it("combined AUTO and Task filters intersect", async () => {
      mockApi(false, { tasks: multiRows, taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      await selectFilterByLabel("AUTO", "on")
      await userEvent.selectOptions(screen.getByLabelText(/Task/i, { selector: "select" }), "watch_cos")
      await waitFor(() => expect(screen.queryByText(/D\. Job Analysis \(.*AUTO\)/)).not.toBeInTheDocument())
      expect(screen.getByText(/C\. Company Roster \(1 \/ 1 AUTO\)/)).toBeInTheDocument()
    }, 20000)

    it("places Candidate, Avail, and Last Run as rightmost columns", async () => {
      mockApi(false, { tasks: [scanJobsC1Auto], taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await expandFirstPhaseSection()
      const headers = within(screen.getByRole("table")).getAllByRole("columnheader")
      expect(headers[headers.length - 3]).toHaveTextContent(/Candidate/)
      expect(headers[headers.length - 2]).toHaveTextContent(/Avail/)
      expect(headers[headers.length - 1]).toHaveTextContent(/Last Run/)
    }, 20000)

    it("renders em dash for zero or null available count", async () => {
      mockApi(false, { tasks: [watchCosZeroAvail], taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      const rosterPanel = screen.getByText(/C\. Company Roster \(1 \/ 1 AUTO\)/).closest(".collapsible-panel") as HTMLElement
      // AST-785 may already auto-open the sole section — click Expand only when present.
      const expandBtn = within(rosterPanel).queryByRole("button", { name: "Expand section" })
      if (expandBtn) await userEvent.click(expandBtn)
      await waitFor(() => expect(within(rosterPanel).getByRole("table")).toBeInTheDocument())
      const row = within(rosterPanel).getByRole("table").querySelectorAll("tbody tr")[0]
      const cells = within(row as HTMLElement).getAllByRole("cell")
      expect(cells[cells.length - 2]).toHaveTextContent("—")
    }, 20000)

    it("All-candidate default sort orders same task by available count descending", async () => {
      mockApi(false, { tasks: [scanJobsC2Off, scanJobsC1Auto], taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      const jobPanel = screen.getByText(/D\. Job Analysis \(1 \/ 2 AUTO\)/).closest(".collapsible-panel") as HTMLElement
      await waitFor(() => expect(within(jobPanel).getByRole("table")).toBeInTheDocument())
      const tbody = within(jobPanel).getByRole("table").querySelector("tbody") as HTMLElement
      const candidateCells = within(tbody).getAllByRole("row").map(r => within(r).getAllByRole("cell")[11].textContent)
      expect(candidateCells[0]).toContain("c1")
      expect(candidateCells[1]).toContain("c2")
    }, 20000)

    it("floor range filter excludes non-scored rows", async () => {
      mockApi(false, { tasks: multiRows, taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      await selectFilterByLabel("Floor min", "1.50")
      await waitFor(() => expect(screen.queryByText(/C\. Company Roster \(.*AUTO\)/)).not.toBeInTheDocument())
      expect(screen.getByText(/D\. Job Analysis \(.*AUTO\)/)).toBeInTheDocument()
    }, 20000)
  })

  function sectionGroupKey(order: string, name: string): string {
    return `${order}\u0000${name}`
  }

  describe("AST-768 section/group filter", () => {
    const multiRows = [scanJobsC1Auto, scanJobsC2Off, watchCosZeroAvail]
    const jobGroupKey = sectionGroupKey("D. Job Analysis", "D. Job Analysis")
    const rosterGroupKey = sectionGroupKey("C. Company Roster", "C. Company Roster")

    it("renders Section/Group with All plus catalog groups from task_keys", async () => {
      const extendedKeys = {
        ...taskKeysConfig,
        stale_group: {
          entity_type: "job",
          trigger_state: "NEW",
          task_group_order: "Z. Future",
          task_group_name: "Z. Future",
          task_seq: 99,
          task_name: "stale_group",
          is_scored: false,
        },
      }
      mockApi(false, { tasks: multiRows, taskKeysPayload: extendedKeys, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
      const select = within(adminFiltersRoot()).getByLabelText("Section/Group")
      const labels = Array.from(select.querySelectorAll("option")).map(o => o.textContent)
      expect(labels).toContain("All")
      expect(labels).toContain("D. Job Analysis")
      expect(labels).toContain("C. Company Roster")
      expect(labels).toContain("Z. Future")
    }, 20000)

    it("selecting a group shows only rows in that task_group_name", async () => {
      mockApi(false, { tasks: multiRows, taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      await selectFilterByLabel("Section/Group", rosterGroupKey)
      expect(screen.queryByText(/D\. Job Analysis \(.*AUTO\)/)).not.toBeInTheDocument()
      expect(screen.getByText(/C\. Company Roster \(1 \/ 1 AUTO\)/)).toBeInTheDocument()
      const rosterPanel = screen.getByText(/C\. Company Roster \(1 \/ 1 AUTO\)/).closest(".collapsible-panel") as HTMLElement
      await waitFor(() => expect(within(rosterPanel).getByText("watch_cos")).toBeVisible())
      expect(within(rosterPanel).queryByText("scan_jobs")).not.toBeInTheDocument()
    }, 20000)

    it("Section/Group and Task filters intersect to empty when Task outside group", async () => {
      mockApi(false, { tasks: multiRows, taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      await selectFilterByLabel("Section/Group", jobGroupKey)
      await userEvent.selectOptions(screen.getByLabelText(/Task/i, { selector: "select" }), "watch_cos")
      await waitFor(() =>
        expect(screen.getByText(/No dispatch tasks match the current filters/)).toBeInTheDocument(),
      )
    }, 20000)

    it("Section/Group and AUTO filters intersect", async () => {
      mockApi(false, { tasks: multiRows, taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      await selectFilterByLabel("Section/Group", jobGroupKey)
      await selectFilterByLabel("AUTO", "on")
      expect(screen.getByText(/D\. Job Analysis \(1 \/ 1 AUTO\)/)).toBeInTheDocument()
      expect(screen.queryByText(/C\. Company Roster \(.*AUTO\)/)).not.toBeInTheDocument()
      const jobPanel = screen.getByText(/D\. Job Analysis \(1 \/ 1 AUTO\)/).closest(".collapsible-panel") as HTMLElement
      await userEvent.click(within(jobPanel).getByRole("button", { name: "Expand section" }))
      await waitFor(() => expect(within(jobPanel).getByText("c1")).toBeVisible())
      expect(within(jobPanel).queryByText("c2")).not.toBeInTheDocument()
    }, 20000)

    it("with Candidate All, group filter narrows sections and default sort by avail desc", async () => {
      mockApi(false, { tasks: [scanJobsC2Off, scanJobsC1Auto], taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      await selectFilterByLabel("Section/Group", jobGroupKey)
      expect(screen.queryByText(/C\. Company Roster \(.*AUTO\)/)).not.toBeInTheDocument()
      const jobPanel = screen.getByText(/D\. Job Analysis \(1 \/ 2 AUTO\)/).closest(".collapsible-panel") as HTMLElement
      await waitFor(() => expect(within(jobPanel).getByRole("table")).toBeInTheDocument())
      const tbody = within(jobPanel).getByRole("table").querySelector("tbody") as HTMLElement
      const candidateCells = within(tbody).getAllByRole("row").map(r => within(r).getAllByRole("cell")[11].textContent)
      expect(candidateCells[0]).toContain("c1")
      expect(candidateCells[1]).toContain("c2")
    }, 20000)

    it("section header AUTO counts reflect post-filter rows in selected group", async () => {
      mockApi(false, { tasks: multiRows, taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      expect(screen.getByText(/D\. Job Analysis \(1 \/ 2 AUTO\)/)).toBeInTheDocument()
      await selectFilterByLabel("Section/Group", jobGroupKey)
      expect(screen.getByText(/D\. Job Analysis \(1 \/ 2 AUTO\)/)).toBeInTheDocument()
      await selectFilterByLabel("AUTO", "on")
      expect(screen.getByText(/D\. Job Analysis \(1 \/ 1 AUTO\)/)).toBeInTheDocument()
    }, 20000)
  })

  describe("AST-887 Avail > 0 filter", () => {
    // scanJobs* avail > 0; watchCosZeroAvail = 0; nullAvailRoster = null (em-dash cases)
    const nullAvailRoster = {
      ...sparseRow,
      id: 13,
      available_count: null as number | null,
      auto_mode: 0,
      debug: 0,
    }
    const multiRows = [scanJobsC1Auto, scanJobsC2Off, watchCosZeroAvail, nullAvailRoster]

    it("defaults Avail to All and still shows zero/null Avail rows", async () => {
      mockApi(false, { tasks: multiRows, taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      const availSelect = within(adminFiltersRoot()).getByLabelText("Avail")
      expect(availSelect).toHaveValue("")
      expect(screen.getByText(/D\. Job Analysis \(1 \/ 2 AUTO\)/)).toBeInTheDocument()
      expect(screen.getByText(/C\. Company Roster \(1 \/ 2 AUTO\)/)).toBeInTheDocument()
    }, 20000)

    it("Avail > 0 hides zero/null Avail rows and omits empty sections", async () => {
      mockApi(false, { tasks: multiRows, taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      await selectFilterByLabel("Avail", "gt0")
      await waitFor(() => expect(screen.queryByText(/C\. Company Roster \(.*AUTO\)/)).not.toBeInTheDocument())
      expect(screen.getByText(/D\. Job Analysis \(1 \/ 2 AUTO\)/)).toBeInTheDocument()
      const jobPanel = screen.getByText(/D\. Job Analysis \(1 \/ 2 AUTO\)/).closest(".collapsible-panel") as HTMLElement
      await userEvent.click(within(jobPanel).getByRole("button", { name: "Expand section" }))
      await waitFor(() => expect(within(jobPanel).getByText("c1")).toBeVisible())
      expect(within(jobPanel).getByText("c2")).toBeVisible()
      const availCells = within(jobPanel).getByRole("table").querySelectorAll("tbody tr")
      for (const row of Array.from(availCells)) {
        const cells = within(row as HTMLElement).getAllByRole("cell")
        expect(cells[cells.length - 2]).not.toHaveTextContent("—")
      }
    }, 20000)

    it("Avail > 0 ANDs with AUTO filter", async () => {
      mockApi(false, { tasks: multiRows, taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      await selectFilterByLabel("Avail", "gt0")
      await selectFilterByLabel("AUTO", "on")
      expect(screen.getByText(/D\. Job Analysis \(1 \/ 1 AUTO\)/)).toBeInTheDocument()
      expect(screen.queryByText(/C\. Company Roster \(.*AUTO\)/)).not.toBeInTheDocument()
      const jobPanel = screen.getByText(/D\. Job Analysis \(1 \/ 1 AUTO\)/).closest(".collapsible-panel") as HTMLElement
      await userEvent.click(within(jobPanel).getByRole("button", { name: "Expand section" }))
      await waitFor(() => expect(within(jobPanel).getByText("c1")).toBeVisible())
      expect(within(jobPanel).queryByText("c2")).not.toBeInTheDocument()
    }, 20000)

    it("clearing Avail back to All restores zero/null Avail sections", async () => {
      mockApi(false, { tasks: multiRows, taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      await selectFilterByLabel("Avail", "gt0")
      await waitFor(() => expect(screen.queryByText(/C\. Company Roster \(.*AUTO\)/)).not.toBeInTheDocument())
      await selectFilterByLabel("Avail", "")
      await waitFor(() => expect(screen.getByText(/C\. Company Roster \(1 \/ 2 AUTO\)/)).toBeInTheDocument())
      expect(screen.getByText(/D\. Job Analysis \(1 \/ 2 AUTO\)/)).toBeInTheDocument()
    }, 20000)
  })

  describe("AST-780 error toast replaces alert", () => {
    it("shows error toast on auto toggle failure and run failure", async () => {
      mockApi(false, { putOk: false, runOk: false, threads: {}, taskKeysPayload: taskKeysConfig })
      renderWithProviders(<ScheduledActions />)
      await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
      await selectAllCandidatesFilter()
      await waitFor(() => expect(within(screen.getByRole("table")).getByText("scan_jobs")).toBeInTheDocument())
      const tbody = within(screen.getByRole("table")).getAllByRole("rowgroup")[1]
      await userEvent.click(within(tbody).getAllByRole("button", { name: "OFF" })[0])
      await waitFor(() => expect(screen.getByText("put bad")).toBeInTheDocument())
      expect(window.alert).not.toHaveBeenCalled()
      await userEvent.click(within(tbody).getByRole("button", { name: "Run" }))
      await waitFor(() => expect(screen.getByText("run bad")).toBeInTheDocument())
      expect(window.alert).not.toHaveBeenCalled()
    }, 20000)

    it("shows error toast when edit save PUT fails", async () => {
      mockApi(false, { putOk: false, threads: {}, taskKeysPayload: taskKeysConfig })
      renderWithProviders(<ScheduledActions />)
      await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
      await selectAllCandidatesFilter()
      await waitFor(() => expect(within(screen.getByRole("table")).getByText("scan_jobs")).toBeInTheDocument())
      await userEvent.click(within(screen.getByRole("table")).getByText("scan_jobs"))
      await waitFor(() => expect(screen.getByText("Edit Task")).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: "Save" }))
      await waitFor(() => expect(screen.getByText("put bad")).toBeInTheDocument())
      expect(window.alert).not.toHaveBeenCalled()
    }, 20000)

    it("shows error toast when add save POST fails", async () => {
      localStorage.setItem("astral_selected_candidate", "c1")
      installBaseApiMocks(mockedApi, async (url, init) => {
        if (url === "/api/admin/scheduler/thread_status") return { ok: true, json: async () => ({}) } as Response
        if (url === "/api/admin/dispatch_tasks" && !init?.method) return { ok: true, json: async () => [] } as Response
        if (url === "/api/admin/dispatch_tasks/task_keys") return { ok: true, json: async () => taskKeysConfig } as Response
        if (url === "/api/admin/dispatch_tasks/state_options") return { ok: true, json: async () => ({ job: ["NEW"], company: ["WATCH"] }) } as Response
        if (url === "/api/admin/dispatch_tasks/score_floor_options") return { ok: true, json: async () => ({ values: defaultScoreFloorOptions }) } as Response
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
      await waitFor(() => expect(screen.getByText("nope")).toBeInTheDocument())
      expect(window.alert).not.toHaveBeenCalled()
    }, 20000)
  })

  describe("AST-773 edit modal task_key", () => {
    const extendedTaskKeys = {
      ...taskKeysConfig,
      grade_do: {
        entity_type: "job",
        trigger_state: "PASSED_JD",
        task_group_order: "D. Job Analysis",
        task_group_name: "D. Job Analysis",
        task_seq: 3,
        task_name: "grade_do",
        is_scored: true,
      },
    }

    it("edit modal shows Task select with current key selected", async () => {
      mockApi(false, { tasks: [dispatchTask], taskKeysPayload: extendedTaskKeys, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await expandFirstPhaseSection()
      await userEvent.click(within(screen.getByRole("table")).getByText("scan_jobs"))
      await waitFor(() => expect(screen.getByText("Edit Task")).toBeInTheDocument())
      const modal = screen.getByText("Edit Task").closest(".modal-card") as HTMLElement
      const taskSelect = within(modal).getAllByRole("combobox")[0]
      expect(taskSelect).toHaveValue("scan_jobs")
    }, 20000)

    it("task change preserves trigger_state and score_floor in PUT body", async () => {
      let putBody: Record<string, unknown> | null = null
      installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
        if (url === "/api/candidates") return { ok: true, json: async () => adminCandidates } as Response
        if (url === "/api/admin/scheduler/thread_status") return { ok: true, json: async () => ({}) } as Response
        if (url === "/api/admin/dispatch_tasks" && !init?.method) return { ok: true, json: async () => [dispatchTask] } as Response
        if (url === "/api/admin/dispatch_tasks/task_keys") return { ok: true, json: async () => extendedTaskKeys } as Response
        if (url === "/api/admin/dispatch_tasks/state_options") return { ok: true, json: async () => ({ job: ["NEW", "PASSED_JD"], company: ["WATCH"] }) } as Response
        if (url === "/api/admin/dispatch_tasks/score_floor_options") return { ok: true, json: async () => ({ values: defaultScoreFloorOptions }) } as Response
        if (url.startsWith("/api/admin/dispatch_tasks/") && init?.method === "PUT") {
          putBody = JSON.parse(String(init.body))
          return { ok: true, json: async () => ({}) } as Response
        }
        return { ok: false, json: async () => ({}) } as Response
      })
      renderWithProviders(<ScheduledActions />)
      await expandFirstPhaseSection()
      await userEvent.click(within(screen.getByRole("table")).getByText("scan_jobs"))
      await waitFor(() => expect(screen.getByText("Edit Task")).toBeInTheDocument())
      const modal = screen.getByText("Edit Task").closest(".modal-card") as HTMLElement
      await userEvent.selectOptions(within(modal).getAllByRole("combobox")[0], "grade_do")
      await userEvent.click(within(modal).getByRole("button", { name: "Save" }))
      await waitFor(() => expect(putBody).not.toBeNull())
      expect(putBody!.task_key).toBe("grade_do")
      expect(putBody!.trigger_state).toBe("NEW")
      expect(putBody!.score_floor).toBe(1.5)
    }, 20000)

    it("AUTO row cannot open Edit Task", async () => {
      mockApi(false, {
        tasks: [sparseRow],
        taskKeysPayload: taskKeysConfig,
        threads: {},
      })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      const rosterPanel = screen.getByText(/C\. Company Roster \(1 \/ 1 AUTO\)/).closest(".collapsible-panel") as HTMLElement
      await userEvent.click(within(rosterPanel).getByRole("button", { name: "Expand section" }))
      await userEvent.click(within(rosterPanel).getByText("watch_cos"))
      expect(screen.queryByText("Edit Task")).not.toBeInTheDocument()
    }, 20000)

    it("running thread row can edit and save new task_key", async () => {
      let putBody: Record<string, unknown> | null = null
      installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
        if (url === "/api/candidates") return { ok: true, json: async () => adminCandidates } as Response
        if (url === "/api/admin/scheduler/thread_status") {
          return {
            ok: true,
            json: async () => ({
              1: { running: true, draining: false, task_key: "scan_jobs", candidate_id: "c1", is_auto: false },
            }),
          } as Response
        }
        if (url === "/api/admin/dispatch_tasks" && !init?.method) return { ok: true, json: async () => [dispatchTask] } as Response
        if (url === "/api/admin/dispatch_tasks/task_keys") return { ok: true, json: async () => extendedTaskKeys } as Response
        if (url === "/api/admin/dispatch_tasks/state_options") return { ok: true, json: async () => ({ job: ["NEW", "PASSED_JD"], company: ["WATCH"] }) } as Response
        if (url === "/api/admin/dispatch_tasks/score_floor_options") return { ok: true, json: async () => ({ values: defaultScoreFloorOptions }) } as Response
        if (url.startsWith("/api/admin/dispatch_tasks/") && init?.method === "PUT") {
          putBody = JSON.parse(String(init.body))
          return { ok: true, json: async () => ({}) } as Response
        }
        return { ok: false, json: async () => ({}) } as Response
      })
      renderWithProviders(<ScheduledActions />)
      await expandFirstPhaseSection()
      await userEvent.click(within(screen.getByRole("table")).getByText("scan_jobs"))
      await waitFor(() => expect(screen.getByText("Edit Task")).toBeInTheDocument())
      const modal = screen.getByText("Edit Task").closest(".modal-card") as HTMLElement
      await userEvent.selectOptions(within(modal).getAllByRole("combobox")[0], "grade_do")
      await userEvent.click(within(modal).getByRole("button", { name: "Save" }))
      await waitFor(() => expect(putBody?.task_key).toBe("grade_do"))
      await waitFor(() => expect(screen.queryByText("Edit Task")).not.toBeInTheDocument())
    }, 20000)

    it("409 on save keeps edit modal open", async () => {
      mockApi(false, { putOk: false, tasks: [dispatchTask], taskKeysPayload: extendedTaskKeys, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await expandFirstPhaseSection()
      await userEvent.click(within(screen.getByRole("table")).getByText("scan_jobs"))
      await waitFor(() => expect(screen.getByText("Edit Task")).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: "Save" }))
      await waitFor(() => expect(screen.getByText("Edit Task")).toBeInTheDocument())
    }, 20000)
  })

  describe("AST-804 candidate Input State options", () => {
    const inflowDiscoveryRow = {
      ...dispatchTask,
      id: 3,
      task_key: "inflow_discovery",
      entity_type: "candidate",
      trigger_state: "LIVE_PROMPTS",
      is_scored: false,
      score_floor: null as number | null,
    }
    const inflowTaskKeys = {
      ...taskKeysConfig,
      inflow_discovery: {
        entity_type: "candidate",
        trigger_state: "LIVE_PROMPTS",
        task_group_order: "A. Candidate",
        task_group_name: "A. Candidate",
        task_seq: 1,
        task_name: "inflow_discovery",
        is_scored: false,
      },
    }
    const candidateStateOptions = {
      job: ["NEW", "PASSED_JD"],
      company: ["WATCH"],
      candidate: ["LIVE_PROMPTS", "NEW"],
    }

    it("edit modal Input State lists candidate states for inflow_discovery row", async () => {
      mockApi(false, {
        tasks: [inflowDiscoveryRow],
        taskKeysPayload: inflowTaskKeys,
        stateOptionsPayload: candidateStateOptions,
        threads: {},
      })
      renderWithProviders(<ScheduledActions />)
      await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
      await selectAllCandidatesFilter()
      const candidatePanel = screen.getByText(/A\. Candidate \(0 \/ 1 AUTO\)/).closest(".collapsible-panel") as HTMLElement
      const expandBtn = within(candidatePanel).queryByRole("button", { name: "Expand section" })
      if (expandBtn) await userEvent.click(expandBtn)
      await waitFor(() => expect(within(candidatePanel).getByText("inflow_discovery")).toBeVisible())
      await userEvent.click(within(candidatePanel).getByText("inflow_discovery"))
      await waitFor(() => expect(screen.getByText("Edit Task")).toBeInTheDocument())
      const modal = screen.getByText("Edit Task").closest(".modal-card") as HTMLElement
      const inputStateSelect = within(modal).getAllByRole("combobox")[1]
      expect(within(inputStateSelect).getByRole("option", { name: "LIVE_PROMPTS" })).toBeInTheDocument()
      expect(within(inputStateSelect).queryByRole("option", { name: "PASSED_JD" })).not.toBeInTheDocument()
    }, 20000)
  })

  describe("AST-785 dispatch_tasks list UX", () => {
    const jobGroupKey = `${"D. Job Analysis"}\u0000${"D. Job Analysis"}`

    it("auto-opens first section on load so table is visible without manual expand", async () => {
      mockApi(false, { tasks: [dispatchTask], taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
      await selectAllCandidatesFilter()
      await waitFor(() => expect(within(screen.getByRole("table")).getByText("scan_jobs")).toBeInTheDocument())
    }, 20000)

    it("shows filter-aware empty message when rows exist but filters hide all", async () => {
      const multiRows = [dispatchTask, sparseRow]
      mockApi(false, { tasks: multiRows, taskKeysPayload: taskKeysConfig, threads: {} })
      renderWithProviders(<ScheduledActions />)
      await selectAllCandidatesFilter()
      await selectFilterByLabel("Section/Group", jobGroupKey)
      await userEvent.selectOptions(screen.getByLabelText(/Task/i, { selector: "select" }), "watch_cos")
      await waitFor(() =>
        expect(screen.getByText(/No dispatch tasks match the current filters/)).toBeInTheDocument(),
      )
    }, 20000)

    it("shows toast when dispatch_tasks fetch fails", async () => {
      installBaseApiMocks(mockedApi, async (url: string) => {
        if (url === "/api/admin/scheduler/thread_status") return { ok: true, json: async () => ({}) } as Response
        if (url === "/api/admin/dispatch_tasks") {
          return { ok: false, status: 500, json: async () => ({ error: "boom" }) } as Response
        }
        if (url === "/api/admin/dispatch_tasks/task_keys") return { ok: true, json: async () => ({}) } as Response
        if (url === "/api/admin/dispatch_tasks/state_options") {
          return { ok: true, json: async () => ({ job: [], company: [], candidate: [] }) } as Response
        }
        if (url === "/api/admin/dispatch_tasks/score_floor_options") {
          return { ok: true, json: async () => ({ values: defaultScoreFloorOptions }) } as Response
        }
      })
      renderWithProviders(<ScheduledActions />)
      await waitFor(() => expect(screen.getByText("Failed to load dispatch tasks (500)")).toBeInTheDocument())
    }, 20000)
  })
})
