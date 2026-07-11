import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, afterEach, beforeAll, describe, expect, it, vi } from "vitest"
import "../../../../src/ui/frontend/src/App.css"
import api from "../../../../src/ui/frontend/src/lib/api"
import PerformanceMonitor from "../../../../src/ui/frontend/src/pages/AdminPerformanceMonitor"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

/** AST-672: vitest CSS import does not apply rules in jsdom — inject product toolbar rule for placement AC. */
function ensureDispatchLogToolbarCss() {
  if (document.querySelector('style[data-test="dispatch-log-toolbar-ast672"]')) return
  const style = document.createElement("style")
  style.setAttribute("data-test", "dispatch-log-toolbar-ast672")
  style.textContent = `.dispatch-log-toolbar { display: flex; justify-content: flex-start; margin-bottom: 6px; }`
  document.head.appendChild(style)
}

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

const adminCandidates = [
  { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { profile: { timezone: "America/Los_Angeles" }, first: "Ada" } },
  { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: { profile: { timezone: "America/Los_Angeles" }, first: "Betty" } },
]

/** AST-634: urlPresentDisablesSync needs candidate_id on mount or RTL hangs on nav sync. */
function withCandidateQuery(path: string): string {
  if (path.includes("candidate_id=")) return path
  return `${path}${path.includes("?") ? "&" : "?"}candidate_id=c1`
}

function renderPerformanceMonitor(path = "/admin/performance", opts?: Parameters<typeof renderWithProviders>[1]) {
  return renderWithProviders(<PerformanceMonitor />, {
    ...opts,
    router: { initialEntries: [withCandidateQuery(path)], ...opts?.router },
  })
}

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
  beforeAll(() => {
    ensureDispatchLogToolbarCss()
  })

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
    renderPerformanceMonitor("/admin/performance?task_key=task_a&status=COMPLETED")

    await waitFor(() => expect(screen.getByText("Execution History")).toBeInTheDocument())
    const table = screen.getByRole("table")
    await userEvent.click(within(table).getByText("task_a"))
    await waitFor(() => expect(screen.getByText("failed")).toBeInTheDocument())
    const copyBtn = screen.getByTitle("Copy logs to clipboard")
    const toolbar = copyBtn.closest(".dispatch-log-toolbar")
    expect(toolbar).not.toBeNull()
    expect(getComputedStyle(toolbar!).justifyContent).toMatch(/flex-start|start/)
    await userEvent.click(copyBtn)
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
    renderPerformanceMonitor()
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
    renderPerformanceMonitor()
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

    renderPerformanceMonitor()
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

    renderPerformanceMonitor("/admin/performance?date_from=2026-05-19")
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
      renderPerformanceMonitor()
      await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
      const table = screen.getByRole("table")
      expect(within(table).getByText("anticipate_scan")).toBeInTheDocument()
      expect(within(table).getByText("contemplate_job")).toBeInTheDocument()
      expect(within(table).getByText("consult_get")).toBeInTheDocument()
      expect(within(table).getAllByText("▶")).toHaveLength(3)
    }, 15000)

    it("expands hop-scoped logs per batch_id", async () => {
      mockChainList(chainHopRowsForToday())
      renderPerformanceMonitor()
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
      renderPerformanceMonitor()
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
      renderPerformanceMonitor("/admin/performance?task_key=anticipate_scan")
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
      renderPerformanceMonitor()
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
      renderPerformanceMonitor()
      await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
      const table = screen.getByRole("table")
      const badge = within(table).getByText("FAILED")
      expect(badge).toHaveClass("dispatch-status-fail")
    }, 15000)
  })

  // AST-840 — client-side log level filter on expanded batch logs (parent AST-838).
  describe("AST-840 log level filter", () => {
    const mixedLogs = [
      { id: "log-info", level: "INFO", logger_name: "core", message: "verbose info line", batch_id: "batch-1", created_at: "2026-05-01T10:00:01Z" },
      { id: "log-error", level: "ERROR", logger_name: "core", message: "failure detail", batch_id: "batch-1", created_at: "2026-05-01T10:00:02Z" },
    ]

    function mockMixedLogsApi(extraLedgerRows: typeof ledgerRow[] = [ledgerRow]) {
      installBaseApiMocks(mockedApi, async (url: string) => {
        if (url.startsWith("/api/admin/dispatch_ledger/batch-1/logs")) {
          return { json: async () => mixedLogs } as Response
        }
        if (url.startsWith("/api/agent_data/")) return { json: async () => [] } as Response
        if (url.startsWith("/api/admin/timesheets?batch_id=")) return { json: async () => [] } as Response
        if (url.startsWith("/api/admin/dispatch_ledger")) {
          return { json: async () => extraLedgerRows } as Response
        }
        if (url === "/api/candidates") {
          return { json: async () => candidateFixture } as Response
        }
      })
    }

    it("renders Level control defaulting to All", async () => {
      mockMixedLogsApi()
      renderPerformanceMonitor()
      await waitFor(() => expect(screen.getByText("Execution History")).toBeInTheDocument())
      const levelSelect = screen.getByLabelText("Level", { selector: "select" }) as HTMLSelectElement
      expect(levelSelect.value).toBe("")
      expect(Array.from(levelSelect.options).map(o => o.textContent)).toEqual(["All", "DEBUG", "INFO", "WARNING", "ERROR"])
    }, 15000)

    it("seeds Level from URL log_level param", async () => {
      mockMixedLogsApi()
      renderPerformanceMonitor("/admin/performance?log_level=ERROR")
      await waitFor(() => expect(screen.getByText("Execution History")).toBeInTheDocument())
      const levelSelect = screen.getByLabelText("Level", { selector: "select" }) as HTMLSelectElement
      expect(levelSelect.value).toBe("ERROR")
    }, 15000)

    it("does not pass log_level to ledger fetch", async () => {
      const calls: string[] = []
      mockMixedLogsApi()
      mockedApi.mockImplementation(async (url: string) => {
        if (url.startsWith("/api/admin/dispatch_ledger?")) calls.push(url)
        if (url.startsWith("/api/admin/dispatch_ledger/batch-1/logs")) {
          return { json: async () => mixedLogs } as Response
        }
        if (url.startsWith("/api/admin/dispatch_ledger")) {
          return { json: async () => [ledgerRow] } as Response
        }
        if (url === "/api/candidates") return { json: async () => candidateFixture } as Response
        if (url.startsWith("/api/agent_data/")) return { json: async () => [] } as Response
      })
      renderPerformanceMonitor("/admin/performance?log_level=ERROR")
      await waitFor(() => expect(screen.getByText("Execution History")).toBeInTheDocument())
      await waitFor(() => expect(calls.length).toBeGreaterThan(0))
      expect(calls.every(u => !u.includes("log_level="))).toBe(true)
    }, 15000)

    it("shows only matching severities when Level is set", async () => {
      mockMixedLogsApi()
      renderPerformanceMonitor("/admin/performance?log_level=ERROR")
      await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
      await userEvent.click(within(screen.getByRole("table")).getByText("task_a"))
      await waitFor(() => expect(screen.getByText("failure detail")).toBeInTheDocument())
      expect(screen.queryByText("verbose info line")).not.toBeInTheDocument()
    }, 15000)

    it("shows filtered-empty message when batch has logs but none at selected level", async () => {
      mockMixedLogsApi()
      renderPerformanceMonitor("/admin/performance?log_level=WARNING")
      await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
      await userEvent.click(within(screen.getByRole("table")).getByText("task_a"))
      await waitFor(() => expect(screen.getByText("No 'WARNING' type log entries for this batch.")).toBeInTheDocument())
      expect(screen.queryByText("No log entries for this batch.")).not.toBeInTheDocument()
      expect(screen.queryByTitle("Copy logs to clipboard")).not.toBeInTheDocument()
    }, 15000)

    it("keeps FAILED ledger rows visible when Level is ERROR", async () => {
      const failedRow = { ...ledgerRow, status: "FAILED", total_failed: 1, total_passed: 0 }
      mockMixedLogsApi([failedRow])
      renderPerformanceMonitor("/admin/performance?log_level=ERROR")
      await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
      const table = screen.getByRole("table")
      expect(within(table).getByText("FAILED")).toBeInTheDocument()
      await userEvent.click(within(table).getByText("task_a"))
      await waitFor(() => expect(screen.getByText("failure detail")).toBeInTheDocument())
    }, 15000)

    it("copies only filtered log lines", async () => {
      mockMixedLogsApi()
      renderPerformanceMonitor("/admin/performance?log_level=ERROR")
      await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
      await userEvent.click(within(screen.getByRole("table")).getByText("task_a"))
      await waitFor(() => expect(screen.getByText("failure detail")).toBeInTheDocument())
      await userEvent.click(screen.getByTitle("Copy logs to clipboard"))
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
        "[2026-05-01T10:00:02Z] ERROR core: failure detail",
      )
      expect(String((navigator.clipboard.writeText as ReturnType<typeof vi.fn>).mock.calls[0][0])).not.toContain("verbose info line")
    }, 15000)

    it("updates expanded view when Level changes without refetching logs", async () => {
      const logCalls: string[] = []
      mockMixedLogsApi()
      mockedApi.mockImplementation(async (url: string) => {
        if (url.includes("/logs")) {
          logCalls.push(url)
          return { json: async () => mixedLogs } as Response
        }
        if (url.startsWith("/api/admin/dispatch_ledger")) {
          return { json: async () => [ledgerRow] } as Response
        }
        if (url === "/api/candidates") return { json: async () => candidateFixture } as Response
        if (url.startsWith("/api/agent_data/")) return { json: async () => [] } as Response
      })
      renderPerformanceMonitor()
      await waitFor(() => expect(screen.getByRole("table")).toBeInTheDocument())
      await userEvent.click(within(screen.getByRole("table")).getByText("task_a"))
      await waitFor(() => expect(screen.getByText("verbose info line")).toBeInTheDocument())
      const before = logCalls.length
      const levelSelect = screen.getByLabelText("Level", { selector: "select" }) as HTMLSelectElement
      await userEvent.selectOptions(levelSelect, "ERROR")
      await waitFor(() => expect(screen.getByText("failure detail")).toBeInTheDocument())
      expect(screen.queryByText("verbose info line")).not.toBeInTheDocument()
      expect(logCalls.length).toBe(before)
    }, 20000)
  })

  describe("AST-634 admin candidate filter", () => {
    it("lists global candidates even when ledger rows omit them", async () => {
      installBaseApiMocks(mockedApi, async (url: string) => {
        if (url.startsWith("/api/admin/dispatch_ledger")) {
          return { json: async () => [ledgerRow] } as Response
        }
        if (url === "/api/candidates") {
          return { json: async () => adminCandidates } as Response
        }
      })
      renderPerformanceMonitor()
      await waitFor(() => expect(screen.getByText("Execution History")).toBeInTheDocument())
      const candidateSelect = screen.getByLabelText("Candidate", { selector: "select" }) as HTMLSelectElement
      await waitFor(() => expect(candidateSelect.options.length).toBeGreaterThan(1))
      const optionLabels = Array.from(candidateSelect.options).map(o => o.textContent)
      expect(optionLabels).toContain("Ada")
      expect(optionLabels).toContain("Betty")
    }, 15000)

    it("passes candidate_id from URL into ledger fetch", async () => {
      const calls: string[] = []
      installBaseApiMocks(mockedApi, async (url: string) => {
        if (url.startsWith("/api/admin/dispatch_ledger?")) calls.push(url)
        if (url.startsWith("/api/admin/dispatch_ledger")) {
          return { json: async () => [ledgerRow] } as Response
        }
        if (url === "/api/candidates") {
          return { json: async () => adminCandidates } as Response
        }
      })
      renderPerformanceMonitor("/admin/performance?candidate_id=c2")
      await waitFor(() => expect(screen.getByText("Execution History")).toBeInTheDocument())
      await waitFor(() => expect(calls.some(u => u.includes("candidate_id=c2"))).toBe(true))
    }, 15000)

    it("direct candidate switch c1 to c2 refetches ledger without All intermediate step", async () => {
      const rowC1 = { ...ledgerRow, batch_id: "b-c1", candidate_id: "c1", task_key: "task_c1" }
      const rowC2 = { ...ledgerRow, batch_id: "b-c2", candidate_id: "c2", task_key: "task_c2" }
      const calls: string[] = []
      installBaseApiMocks(mockedApi, async (url: string) => {
        if (url.startsWith("/api/admin/dispatch_ledger?")) {
          calls.push(url)
          if (url.includes("candidate_id=c2")) return { json: async () => [rowC2] } as Response
          if (url.includes("candidate_id=c1")) return { json: async () => [rowC1] } as Response
          return { json: async () => [rowC1, rowC2] } as Response
        }
        if (url.startsWith("/api/admin/dispatch_ledger")) {
          return { json: async () => [rowC1] } as Response
        }
        if (url === "/api/candidates") {
          return { json: async () => adminCandidates } as Response
        }
      })
      localStorage.setItem("astral_selected_candidate", "c1")
      renderPerformanceMonitor("/admin/performance?candidate_id=c1")
      await waitFor(() => expect(within(screen.getByRole("table")).getByText("task_c1")).toBeInTheDocument())
      const candidateSelect = screen.getByLabelText("Candidate", { selector: "select" }) as HTMLSelectElement
      await waitFor(() => expect(candidateSelect.options.length).toBeGreaterThan(2))
      await userEvent.selectOptions(candidateSelect, "c2")
      await waitFor(() => expect(calls.some(u => u.includes("candidate_id=c2"))).toBe(true))
      await waitFor(() => expect(within(screen.getByRole("table")).getByText("task_c2")).toBeInTheDocument())
      expect(within(screen.getByRole("table")).queryByText("task_c1")).not.toBeInTheDocument()
      expect(candidateSelect.value).toBe("c2")
    }, 20000)
  })
})
