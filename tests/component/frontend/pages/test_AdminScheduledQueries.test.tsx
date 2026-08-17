import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AdminScheduledQueries from "../../../../src/ui/frontend/src/pages/AdminScheduledQueries"
import { installBaseApiMocks, jsonResponse, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const row = {
  scheduled_query_id: "q1",
  name: "purge old",
  sql_text: "DELETE FROM x",
  active: true,
  interval_hours: 24,
  last_run_at: null,
  last_rows_affected: null,
  last_error: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
}

describe("AdminScheduledQueries — AST-1410 (§6c routed page)", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  function mockList(rows: typeof row[] = [row]) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/admin/scheduled_queries" && !init?.method) {
        return jsonResponse(rows)
      }
      if (url === "/api/admin/scheduled_queries/q1" && init?.method === "PUT") {
        return jsonResponse({ ok: true })
      }
    })
  }

  it("renders Scheduled Queries and the saved row on first paint", async () => {
    mockList()
    renderWithProviders(<AdminScheduledQueries />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Scheduled Queries" })).toBeInTheDocument())
    expect(screen.getByText("purge old")).toBeInTheDocument()
    expect(screen.getByText(/every 24h · active/)).toBeInTheDocument()
  })

  it("AST-1410: Activate refetch keeps the row and skips Loading…", async () => {
    mockList()
    renderWithProviders(<AdminScheduledQueries />)
    await waitFor(() => expect(screen.getByText("purge old")).toBeInTheDocument())
    const inner = mockedApi.getMockImplementation()!
    let release: (value: Response) => void = () => {}
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/admin/scheduled_queries" && !init?.method) {
        return new Promise<Response>((resolve) => { release = resolve })
      }
      return inner(url, init)
    })
    // toggleActive awaits load(); do not await click until the silent GET is released
    const pending = userEvent.click(screen.getByRole("button", { name: "Deactivate" }))
    await waitFor(() => {
      const gets = mockedApi.mock.calls.filter(([u, init]) => u === "/api/admin/scheduled_queries" && !init?.method)
      expect(gets.length).toBeGreaterThan(1)
    })
    expect(screen.getByText("purge old")).toBeInTheDocument()
    expect(screen.queryByText("Loading…")).not.toBeInTheDocument()
    release({ ok: true, json: async () => [{ ...row, active: false }] } as Response)
    await pending
    await waitFor(() => expect(screen.getByRole("button", { name: "Activate" })).toBeInTheDocument())
    expect(screen.queryByText("Loading…")).not.toBeInTheDocument()
  })
})
