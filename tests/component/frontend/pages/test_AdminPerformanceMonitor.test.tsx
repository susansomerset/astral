import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, afterEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import PerformanceMonitor from "../../../../src/ui/frontend/src/pages/AdminPerformanceMonitor"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const ledgerRow = {
  batch_id: "batch-1",
  task_key: "task_a",
  candidate_id: "c1",
  started_at: "2026-05-01T10:00:00Z",
  completed_at: "2026-05-01T10:00:05Z",
  status: "COMPLETED",
  total_processed: 2,
  total_passed: 2,
  total_failed: 0,
  total_errors: 0,
  total_cost: 0.5,
}

const candidateFixture = [
  { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { profile: { timezone: "America/Los_Angeles" } } },
]

function chainHopRowsForToday() {
  const today = new Date().toLocaleDateString("en-CA", { timeZone: "America/Los_Angeles" })
  const base = {
    candidate_id: "c1",
    started_at: `${today}T12:00:00Z`,
    completed_at: `${today}T12:00:05Z`,
    status: "COMPLETED",
    total_processed: 1,
    total_passed: 1,
    total_failed: 0,
    total_errors: 0,
    total_cost: 0.01,
  }
  return [
    { ...base, batch_id: "anticipate_scan-uuid-1", task_key: "anticipate_scan" },
    { ...base, batch_id: "contemplate_job-uuid-2", task_key: "contemplate_job", started_at: `${today}T11:00:00Z` },
    { ...base, batch_id: "consult_get-uuid-3", task_key: "consult_get", started_at: `${today}T10:00:00Z` },
  ]
}

describe("AdminPerformanceMonitor", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    vi.useFakeTimers({ shouldAdvanceTime: true })
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  function mockApi() {
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url.startsWith("/api/agent_data/")) {
        return { json: async () => [] } as Response
      }
      if (url.startsWith("/api/admin/timesheets?batch_id=")) {
        return { json: async () => [] } as Response
      }
      if (url.startsWith("/api/admin/dispatch_ledger/batch-1/logs")) {
        return { json: async () => [{ id: "log-1", level: "ERROR", logger_name: "core", message: "failed", batch_id: "batch-1", created_at: "2026-05-01T10:00:01Z" }] } as Response
      }
      if (url.startsWith("/api/admin/dispatch_ledger")) {
        return { json: async () => [ledgerRow] } as Response
      }
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { profile: { timezone: "America/Los_Angeles" } } }] } as Response
      }
    })
  }

  it("loads ledger rows, filters, expands logs, and opens batch modal", async () => {
    mockApi()
    renderWithProviders(<PerformanceMonitor />, {
      router: { initialEntries: ["/admin/performance?task_key=task_a&status=COMPLETED"] },
    })

    await waitFor(() => expect(screen.getByText("Execution History")).toBeInTheDocument())
    const table = screen.getByRole("table")
    await userEvent.click(within(table).getByText("task_a"))
    await waitFor(() => expect(screen.getByText("failed")).toBeInTheDocument())
    await userEvent.click(screen.getByTitle("Copy logs to clipboard"))
    expect(navigator.clipboard.writeText).toHaveBeenCalled()
    await userEvent.click(screen.getByTitle("View agent data for this batch"))
    await waitFor(() => expect(screen.getByText("No agent data blocks recorded for this batch.")).toBeInTheDocument())
  }, 20000)

  it("defaults ledger fetch to today when date_from absent", async () => {
    let ledgerUrl = ""
    mockApi()
    mockedApi.mockImplementation(async (url: string) => {
      if (url.startsWith("/api/admin/dispatch_ledger?")) ledgerUrl = url
      if (url.startsWith("/api/admin/dispatch_ledger") && !url.includes("?")) {
        return { json: async () => [ledgerRow] } as Response
      }
      if (url === "/api/candidates") {
        return {
          json: async () => [
            { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { profile: { timezone: "America/Los_Angeles" } } },
          ],
        } as Response
      }
      if (url.startsWith("/api/agent_data/")) return { json: async () => [] } as Response
      throw new Error(`unexpected ${url}`)
    })
    renderWithProviders(<PerformanceMonitor />)
    await waitFor(() => expect(screen.getByText("Execution History")).toBeInTheDocument())
    await waitFor(() => expect(ledgerUrl).toContain("date_from="))
  }, 15000)

  it("skip checks hides finished zero-count rows but keeps RUNNING", async () => {
    const today = new Date().toLocaleDateString("en-CA", { timeZone: "UTC" })
    const startedToday = `${today}T10:00:00Z`
    const rowToday = { ...ledgerRow, started_at: startedToday, completed_at: `${today}T10:00:05Z` }
    const zeroDone = {
      ...rowToday,
      batch_id: "batch-zero-done",
      status: "COMPLETED",
      total_processed: 0,
      total_passed: 0,
      total_failed: 0,
      total_errors: 0,
      total_cost: 0,
    }
    const zeroRunning = {
      ...rowToday,
      batch_id: "batch-zero-run",
      status: "RUNNING",
      total_processed: 0,
      total_passed: 0,
      total_failed: 0,
      total_errors: 0,
      total_cost: 0,
      completed_at: null,
    }
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url.startsWith("/api/admin/dispatch_ledger")) {
        return { json: async () => [rowToday, zeroDone, zeroRunning] } as Response
      }
      if (url.startsWith("/api/agent_data/")) return { json: async () => [] } as Response
      if (url === "/api/candidates") {
        return {
          json: async () => [
            { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { profile: { timezone: "UTC" } } },
          ],
        } as Response
      }
    })
    renderWithProviders(<PerformanceMonitor />)
    await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
    const table = screen.getByRole("table")
    expect(within(table).getByText("RUNNING")).toBeInTheDocument()
    expect(within(table).getAllByText("COMPLETED")).toHaveLength(1)
  }, 15000)

  it("shows empty logs and collapses expanded rows", async () => {
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url.startsWith("/api/admin/dispatch_ledger/batch-1/logs")) return { json: async () => [] } as Response
      if (url.startsWith("/api/admin/dispatch_ledger")) return { json: async () => [ledgerRow] } as Response
    })

    renderWithProviders(<PerformanceMonitor />)
    await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
    const table = screen.getByRole("table")
    await userEvent.click(within(table).getByText("task_a"))
    await waitFor(() => expect(screen.getByText("No log entries for this batch.")).toBeInTheDocument())
    await userEvent.click(within(table).getByText("task_a"))
    expect(screen.queryByText("No log entries for this batch.")).not.toBeInTheDocument()
  }, 15000)

  it("commits date filters on blur so partial typing does not reload ledger", async () => {
    vi.useRealTimers()
    const calls: string[] = []
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url.startsWith("/api/admin/dispatch_ledger")) {
        calls.push(url)
        return { json: async () => [ledgerRow] } as Response
      }
      if (url.startsWith("/api/admin/dispatch_ledger/batch-1/logs")) {
        return { json: async () => [] } as Response
      }
    })

    renderWithProviders(<PerformanceMonitor />, {
      router: { initialEntries: ["/admin/performance?date_from=2026-05-19"] },
    })
    await waitFor(() => expect(screen.getByText("Execution History")).toBeInTheDocument())
    const from = screen.getByLabelText("From") as HTMLInputElement
    const before = calls.length
    fireEvent.change(from, { target: { value: "2026-05-21" } })
    expect(calls.length).toBe(before)
    fireEvent.blur(from)
    await waitFor(() => expect(calls.some(u => u.includes("date_from=2026-05-21"))).toBe(true))
    fireEvent.change(from, { target: { value: "" } })
    fireEvent.blur(from)
    await waitFor(() => expect(calls.some(u => !u.includes("date_from="))).toBe(true))
    vi.useFakeTimers({ shouldAdvanceTime: true })
  }, 20000)

  // AST-532 — per-hop Execution History UI (parent AST-528); batch_id-scoped expand/inspect.
  describe("AST-532 per-hop execution history UI", () => {
    function mockChainList(rows: typeof ledgerRow[]) {
      installBaseApiMocks(mockedApi, async (url: string) => {
        if (url.startsWith("/api/admin/dispatch_ledger/anticipate_scan-uuid-1/logs")) {
          return { json: async () => [{ id: "l1", level: "INFO", logger_name: "core", message: "hop-one-log", batch_id: "anticipate_scan-uuid-1", created_at: "2026-05-01T10:00:01Z" }] } as Response
        }
        if (url.startsWith("/api/admin/dispatch_ledger/contemplate_job-uuid-2/logs")) {
          return { json: async () => [{ id: "l2", level: "INFO", logger_name: "core", message: "hop-two-log", batch_id: "contemplate_job-uuid-2", created_at: "2026-05-01T10:00:02Z" }] } as Response
        }
        if (url.startsWith("/api/agent_data/anticipate_scan-uuid-1")) {
          return { json: async () => [{ agent_data_id: "a1", block_type: "RESPONSE", block_data: "\"hop-one-response\"", token_size: 1, task_key: "anticipate_scan", created_at: "2026-05-01T10:00:01Z" }] } as Response
        }
        if (url.startsWith("/api/agent_data/contemplate_job-uuid-2")) {
          return { json: async () => [{ agent_data_id: "a2", block_type: "RESPONSE", block_data: "\"hop-two-response\"", token_size: 1, task_key: "contemplate_job", created_at: "2026-05-01T10:00:02Z" }] } as Response
        }
        if (url.startsWith("/api/admin/timesheets?batch_id=")) {
          return { json: async () => [] } as Response
        }
        if (url.startsWith("/api/admin/dispatch_ledger")) {
          return { json: async () => rows } as Response
        }
        if (url === "/api/candidates") {
          return { json: async () => candidateFixture } as Response
        }
      })
    }

    it("lists separate per-hop rows with correct task keys", async () => {
      mockChainList(chainHopRowsForToday())
      renderWithProviders(<PerformanceMonitor />)
      await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
      const table = screen.getByRole("table")
      expect(within(table).getByText("anticipate_scan")).toBeInTheDocument()
      expect(within(table).getByText("contemplate_job")).toBeInTheDocument()
      expect(within(table).getByText("consult_get")).toBeInTheDocument()
      expect(within(table).getAllByText("▶")).toHaveLength(3)
    }, 15000)

    it("expands hop-scoped logs per batch_id", async () => {
      mockChainList(chainHopRowsForToday())
      renderWithProviders(<PerformanceMonitor />)
      await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
      const table = screen.getByRole("table")
      await userEvent.click(within(table).getByText("anticipate_scan"))
      await waitFor(() => expect(screen.getByText("hop-one-log")).toBeInTheDocument())
      expect(screen.queryByText("hop-two-log")).not.toBeInTheDocument()
      await userEvent.click(within(table).getByText("anticipate_scan"))
      expect(screen.queryByText("hop-one-log")).not.toBeInTheDocument()
      await userEvent.click(within(table).getByText("contemplate_job"))
      await waitFor(() => expect(screen.getByText("hop-two-log")).toBeInTheDocument())
      expect(screen.queryByText("hop-one-log")).not.toBeInTheDocument()
    }, 20000)

    it("opens hop-scoped agent_data per batch_id", async () => {
      mockChainList(chainHopRowsForToday())
      renderWithProviders(<PerformanceMonitor />)
      await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
      const table = screen.getByRole("table")
      await userEvent.click(within(table).getByText("anticipate_scan"))
      await waitFor(() => expect(screen.getByTitle("View agent data for this batch")).toBeInTheDocument())
      await userEvent.click(screen.getByTitle("View agent data for this batch"))
      await waitFor(() => expect(screen.getByDisplayValue(/hop-one-response/)).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: /close/i }))
      await userEvent.click(within(table).getByText("contemplate_job"))
      await waitFor(() => expect(screen.getByTitle("View agent data for this batch")).toBeInTheDocument())
      await userEvent.click(screen.getByTitle("View agent data for this batch"))
      await waitFor(() => expect(screen.getByDisplayValue(/hop-two-response/)).toBeInTheDocument())
    }, 20000)

    it("task filter passes task_key to ledger fetch", async () => {
      const calls: string[] = []
      installBaseApiMocks(mockedApi, async (url: string) => {
        if (url.startsWith("/api/admin/dispatch_ledger")) {
          calls.push(url)
          const rows = url.includes("task_key=anticipate_scan")
            ? chainHopRowsForToday().filter(r => r.task_key === "anticipate_scan")
            : chainHopRowsForToday()
          return { json: async () => rows } as Response
        }
        if (url === "/api/candidates") return { json: async () => candidateFixture } as Response
      })
      renderWithProviders(<PerformanceMonitor />, {
        router: { initialEntries: ["/admin/performance?task_key=anticipate_scan"] },
      })
      await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
      await waitFor(() => expect(calls.some(u => u.includes("task_key=anticipate_scan"))).toBe(true))
      const table = screen.getByRole("table")
      expect(within(table).getByText("anticipate_scan")).toBeInTheDocument()
      expect(within(table).queryByText("contemplate_job")).not.toBeInTheDocument()
    }, 15000)

    it("regression adhoc and user prefixed task keys still render", async () => {
      const rows = [
        ...chainHopRowsForToday(),
        {
          ...chainHopRowsForToday()[0],
          batch_id: "adhoc-b1",
          task_key: "adhoc-evaluate_jd",
        },
        {
          ...chainHopRowsForToday()[0],
          batch_id: "user-b1",
          task_key: "user-craft_resume_base",
        },
      ]
      mockChainList(rows)
      renderWithProviders(<PerformanceMonitor />)
      await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
      const table = screen.getByRole("table")
      expect(within(table).getByText("adhoc-evaluate_jd")).toBeInTheDocument()
      expect(within(table).getByText("user-craft_resume_base")).toBeInTheDocument()
      expect(within(table).getByText("anticipate_scan")).toBeInTheDocument()
    }, 15000)

    it("failed mid-chain hop shows FAILED badge", async () => {
      const today = new Date().toLocaleDateString("en-CA", { timeZone: "America/Los_Angeles" })
      const rows = [
        {
          batch_id: "fail-b",
          task_key: "contemplate_job",
          candidate_id: "c1",
          started_at: `${today}T09:00:00Z`,
          completed_at: `${today}T09:00:03Z`,
          status: "FAILED",
          total_processed: 1,
          total_passed: 0,
          total_failed: 1,
          total_errors: 0,
          total_cost: 0.02,
        },
      ]
      mockChainList(rows)
      renderWithProviders(<PerformanceMonitor />)
      await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
      const table = screen.getByRole("table")
      const badge = within(table).getByText("FAILED")
      expect(badge).toHaveClass("dispatch-status-fail")
    }, 15000)
  })
})
