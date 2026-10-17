import { screen, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import ScheduledActions from "../../../../src/ui/frontend/src/pages/AdminScheduledActions"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const CAP_PATH = "/api/admin/scheduler/auto_thread_cap"
type Cap = { max_auto_threads: number; default: number; min: number; max: number }
const freshCap: Cap = { max_auto_threads: 3, default: 3, min: 1, max: 100 }

type ThreadEntry = {
  running: boolean
  draining: boolean
  task_key: string
  candidate_id: string
  is_auto: boolean
}

const json = (body: unknown, ok = true, status = 200) =>
  ({ ok, status, json: async () => body }) as Response

/** Build N AUTO + M CLICK running thread_status entries (ids 1..N+M). */
function mixedThreads(autoCount: number, clickCount: number): Record<number, ThreadEntry> {
  const out: Record<number, ThreadEntry> = {}
  let id = 1
  for (let i = 0; i < autoCount; i++, id++) {
    out[id] = { running: true, draining: false, task_key: "scan_jobs", candidate_id: "c1", is_auto: true }
  }
  for (let i = 0; i < clickCount; i++, id++) {
    out[id] = { running: true, draining: false, task_key: "scan_jobs", candidate_id: "c1", is_auto: false }
  }
  return out
}

function mockApi(threads: Record<number, ThreadEntry>, cap: Cap = freshCap) {
  installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
    if (url === "/api/candidates") return json([])
    if (url === "/api/admin/scheduler/thread_status") return json(threads)
    if (url === "/api/admin/dispatch_tasks" && !init?.method) return json([])
    if (url === "/api/admin/dispatch_tasks/task_keys") return json({})
    if (url === "/api/admin/dispatch_tasks/state_options") return json({ job: [], company: [], candidate: [] })
    if (url === "/api/admin/dispatch_tasks/score_floor_options") return json({ values: [] })
    if (url === CAP_PATH && !init?.method) return json(cap)
  })
}

const capSelect = () => screen.getByLabelText("Max AUTO threads") as HTMLSelectElement
const badge = () => document.querySelector(".dispatch-status-badge") as HTMLElement | null

describe("AST-2273 Scheduled Actions header AUTO/CLICK running badge", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    vi.useFakeTimers({ shouldAdvanceTime: true })
    vi.spyOn(window, "alert").mockImplementation(() => {})
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  // Board repro: Max AUTO = 3, 3 AUTO + 2 CLICK — must not read as "5 running" vs the cap.
  it("mixed: shows 3 AUTO · 2 CLICK, not 5 running; Max AUTO stays 3; Stop All enabled", async () => {
    mockApi(mixedThreads(3, 2))
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(capSelect()).toHaveValue("3"))
    await waitFor(() => expect(badge()?.textContent).toBe("3 AUTO · 2 CLICK"))
    expect(screen.queryByText("5 running")).not.toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Stop All" })).not.toBeDisabled()
  })

  it("AUTO only: shows 3 AUTO running (no bare 3 running, no CLICK)", async () => {
    mockApi(mixedThreads(3, 0))
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(capSelect()).toHaveValue("3"))
    await waitFor(() => expect(badge()?.textContent).toBe("3 AUTO running"))
    expect(screen.queryByText("3 running")).not.toBeInTheDocument()
    expect(badge()?.textContent).not.toMatch(/CLICK/)
  })

  it("CLICK only: shows 2 CLICK running; Max AUTO still shown", async () => {
    mockApi(mixedThreads(0, 2))
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(capSelect()).toHaveValue("3"))
    await waitFor(() => expect(badge()?.textContent).toBe("2 CLICK running"))
    expect(screen.queryByText("2 running")).not.toBeInTheDocument()
  })
})
