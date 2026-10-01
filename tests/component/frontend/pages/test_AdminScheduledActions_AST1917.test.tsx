import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
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
// AST-1916 payload on a fresh server start (config default 3, bounds 1..100).
const freshCap: Cap = { max_auto_threads: 3, default: 3, min: 1, max: 100 }

const json = (body: unknown, ok = true, status = 200) =>
  ({ ok, status, json: async () => body }) as Response

// capGet / capPost: Response to return, or an Error to throw (network failure).
function mockApi(capGet: Response | Error, capPost?: (body: unknown) => Response | Error) {
  installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
    // Full first-paint set for the routed page (§6c) — same routes as the AST-1104 file.
    if (url === "/api/candidates") return json([])
    if (url === "/api/admin/scheduler/thread_status") return json({})
    if (url === "/api/admin/dispatch_tasks" && !init?.method) return json([])
    if (url === "/api/admin/dispatch_tasks/task_keys") return json({})
    if (url === "/api/admin/dispatch_tasks/state_options") return json({ job: [], company: [], candidate: [] })
    if (url === "/api/admin/dispatch_tasks/score_floor_options") return json({ values: [] })
    if (url === CAP_PATH && !init?.method) {
      if (capGet instanceof Error) throw capGet
      return capGet
    }
    if (url === CAP_PATH && init?.method === "POST" && capPost) {
      const r = capPost(JSON.parse(String(init.body)))
      if (r instanceof Error) throw r
      return r
    }
  })
}

const capSelect = () => screen.getByLabelText("Max AUTO threads") as HTMLSelectElement
const optionValues = () => Array.from(capSelect().options).map(o => o.value)
const capPosts = () => mockedApi.mock.calls.filter(([u, i]) => u === CAP_PATH && i?.method === "POST")

describe("AST-1917 Scheduled Actions header Max AUTO threads dropdown", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    vi.useFakeTimers({ shouldAdvanceTime: true })
    vi.spyOn(window, "alert").mockImplementation(() => {})
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it("AC1/AC2: shows the live cap pre-selected with exactly 1..100 options", async () => {
    mockApi(json(freshCap))
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(capSelect()).toHaveValue("3"))
    const values = optionValues()
    expect(values).toHaveLength(100)
    expect(values[0]).toBe("1")
    expect(values[99]).toBe("100")
    expect(values).toEqual(Array.from({ length: 100 }, (_, i) => String(i + 1)))
  })

  it("AC3: option range follows the API bounds, not page literals", async () => {
    mockApi(json({ max_auto_threads: 4, default: 3, min: 2, max: 6 }))
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(capSelect()).toHaveValue("4"))
    expect(optionValues()).toEqual(["2", "3", "4", "5", "6"])
  })

  it("POSTs the pick as a JSON number and shows the server-returned value", async () => {
    // Server answers 8 for a pick of 7 → the select must show the server's value, not the pick.
    mockApi(json(freshCap), () => json({ ...freshCap, max_auto_threads: 8 }))
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(capSelect()).toHaveValue("3"))
    await userEvent.selectOptions(capSelect(), "7")
    await waitFor(() => expect(capSelect()).toHaveValue("8"))
    expect(capPosts()).toHaveLength(1)
    expect(JSON.parse(String(capPosts()[0][1]?.body))).toEqual({ max_auto_threads: 7 })
  })

  it("reverts to the prior cap and toasts the API error on a 400", async () => {
    mockApi(json(freshCap), () => json({ error: "max_auto_threads must be a whole number between 1 and 100" }, false, 400))
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(capSelect()).toHaveValue("3"))
    await userEvent.selectOptions(capSelect(), "50")
    await waitFor(() => expect(screen.getByText("max_auto_threads must be a whole number between 1 and 100")).toBeInTheDocument())
    expect(capSelect()).toHaveValue("3")
    expect(window.alert).not.toHaveBeenCalled()
  })

  it("reverts and shows the fallback toast when the POST throws", async () => {
    mockApi(json(freshCap), () => new Error("network down"))
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(capSelect()).toHaveValue("3"))
    await userEvent.selectOptions(capSelect(), "9")
    await waitFor(() => expect(screen.getByText("Failed to set max AUTO threads")).toBeInTheDocument())
    expect(capSelect()).toHaveValue("3")
  })

  it.each([
    ["non-ok GET", json({ error: "nope" }, false, 500)],
    ["GET throws", new Error("network down")],
  ])("hides the dropdown silently when the cap load fails (%s)", async (_label, capGet) => {
    mockApi(capGet)
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
    await waitFor(() => expect(mockedApi.mock.calls.some(([u]) => u === CAP_PATH)).toBe(true))
    expect(screen.queryByLabelText("Max AUTO threads")).not.toBeInTheDocument()
    expect(screen.queryByText("nope")).not.toBeInTheDocument()
    expect(screen.queryByText("network down")).not.toBeInTheDocument()
  })
})
