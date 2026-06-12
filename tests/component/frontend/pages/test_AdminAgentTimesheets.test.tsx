import { cleanup, fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AgentTimesheets from "../../../../src/ui/frontend/src/pages/AdminAgentTimesheets"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const row = {
  agent_req_id: "req-1",
  created_at: "2026-05-01T12:00:00Z",
  candidate_id: "c1",
  batch_id: "batch-1",
  task_key_uuid: "task-uuid",
  model_code: "claude",
  batch_size: 1,
  cache_write_tokens: 10,
  cache_read_tokens: 20,
  no_cache_prompt_tokens: 30,
  no_cache_live_tokens: 40,
  total_no_cache_input_tokens: 70,
  total_output_tokens: 50,
  calc_cost_cache_write: 0.01,
  calc_cost_cache_read: 0.02,
  calc_cost_no_cache_input: 0.03,
  calc_cost_output: 0.04,
  total_cost: 0.1,
  agent_performance: "ok",
  failure_note: null,
}

describe("AdminAgentTimesheets", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    URL.createObjectURL = vi.fn(() => "blob:timesheets")
    URL.revokeObjectURL = vi.fn()
  })

  it("loads rows, shows totals, filters, selects, and exports", async () => {
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url.startsWith("/api/admin/timesheets/export")) {
        return { blob: async () => new Blob(["csv"]) } as Response
      }
      if (url.startsWith("/api/admin/timesheets")) {
        return { json: async () => [row] } as Response
      }
    })

    renderWithProviders(<AgentTimesheets />, {
      router: { initialEntries: ["/admin/agent_timesheets?batch_id=batch-1&candidate_id=c1"] },
    })

    await waitFor(() => expect(screen.getByText("Agent Timesheets")).toBeInTheDocument())
    expect(screen.getByText(/All \(1 rows\)/)).toBeInTheDocument()
    expect(screen.getByRole("columnheader", { name: "$ Total" })).toBeInTheDocument()
    expect(screen.getByText("$0.1000")).toBeInTheDocument()

    fireEvent.change(screen.getByPlaceholderText("batch_id"), { target: { value: "batch-2" } })
    fireEvent.blur(screen.getByLabelText("From"), { target: { value: "2026-05-01" } })
    fireEvent.blur(screen.getByLabelText("To"), { target: { value: "2026-05-14" } })

    const table = await screen.findByRole("table")
    await userEvent.click(within(table).getAllByRole("checkbox")[0])
    expect(screen.getByText(/Selected \(1 rows\)/)).toBeInTheDocument()

    const anchorClick = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {})
    await userEvent.click(screen.getByRole("button", { name: "Export CSV" }))
    await waitFor(() => expect(anchorClick).toHaveBeenCalled())
    anchorClick.mockRestore()
  }, 15000)

  it("handles empty and failed loads", async () => {
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url.startsWith("/api/admin/timesheets")) {
        return { json: async () => [] } as Response
      }
    })

    renderWithProviders(<AgentTimesheets />)
    await waitFor(() => expect(screen.getByText("No timesheet entries found.")).toBeInTheDocument())

    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url.startsWith("/api/admin/timesheets")) {
        throw new Error("fail")
      }
    })
    cleanup()
    renderWithProviders(<AgentTimesheets />)
    await waitFor(() => expect(screen.getByText("No timesheet entries found.")).toBeInTheDocument())
  }, 15000)
})
