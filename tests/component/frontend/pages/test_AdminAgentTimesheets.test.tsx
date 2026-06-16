import { cleanup, fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { Route, Routes, useLocation } from "react-router-dom"
import NavigationShell from "../../../../src/ui/frontend/src/components/NavigationShell"
import api from "../../../../src/ui/frontend/src/lib/api"
import AgentTimesheets from "../../../../src/ui/frontend/src/pages/AdminAgentTimesheets"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"
import { resetStytchTestState } from "../stytchMock"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

vi.mock("../../../../src/ui/frontend/src/assets/astral_logo.png", () => ({
  default: "logo.png",
}))

const mockedApi = vi.mocked(api)

function ScheduledStub() {
  const { pathname } = useLocation()
  return (
    <div>
      <div>Scheduled Actions Page</div>
      <div data-testid="pathname">{pathname}</div>
    </div>
  )
}

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
    resetStytchTestState()
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

  describe("AST-634 admin candidate filter", () => {
    it("uses Candidate dropdown and passes candidate_id on export", async () => {
      let exportUrl = ""
      installBaseApiMocks(mockedApi, async (url: string) => {
        if (url.startsWith("/api/admin/timesheets/export")) {
          exportUrl = url
          return { blob: async () => new Blob(["csv"]) } as Response
        }
        if (url.startsWith("/api/admin/timesheets")) {
          return { json: async () => [row] } as Response
        }
        if (url === "/api/candidates") {
          return {
            json: async () => [
              { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} },
              { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: {} },
            ],
          } as Response
        }
      })

      renderWithProviders(<AgentTimesheets />, {
        router: { initialEntries: ["/admin/agent_timesheets?candidate_id=c1"] },
      })
      await waitFor(() => expect(screen.getByText("Agent Timesheets")).toBeInTheDocument())
      expect(screen.getByLabelText("Candidate", { selector: "select" })).toBeInTheDocument()
      expect(screen.queryByPlaceholderText("candidate_id")).not.toBeInTheDocument()

      const anchorClick = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {})
      await userEvent.click(screen.getByRole("button", { name: "Export CSV" }))
      await waitFor(() => expect(exportUrl).toContain("candidate_id=c1"))
      anchorClick.mockRestore()
    }, 15000)
  })

  describe("AST-709 nav and candidate filter", () => {
    it("direct candidate switch c1 to c2 refetches timesheets without All intermediate step", async () => {
      const rowC1 = { ...row, agent_req_id: "req-c1", candidate_id: "c1" }
      const rowC2 = { ...row, agent_req_id: "req-c2", candidate_id: "c2" }
      const calls: string[] = []
      installBaseApiMocks(mockedApi, async (url: string) => {
        if (url.startsWith("/api/admin/timesheets?")) {
          calls.push(url)
          if (url.includes("candidate_id=c2")) return { json: async () => [rowC2] } as Response
          if (url.includes("candidate_id=c1")) return { json: async () => [rowC1] } as Response
          return { json: async () => [rowC1, rowC2] } as Response
        }
        if (url.startsWith("/api/admin/timesheets")) {
          return { json: async () => [rowC1] } as Response
        }
        if (url === "/api/candidates") {
          return {
            json: async () => [
              { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} },
              { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: {} },
            ],
          } as Response
        }
      })
      localStorage.setItem("astral_selected_candidate", "c1")
      renderWithProviders(<AgentTimesheets />, {
        router: { initialEntries: ["/admin/agent_timesheets?candidate_id=c1"] },
      })
      await waitFor(() =>
        expect(within(screen.getByRole("table")).getByText("req-c1")).toBeInTheDocument(),
      )
      const candidateSelect = screen.getByLabelText("Candidate", { selector: "select" }) as HTMLSelectElement
      await waitFor(() => expect(candidateSelect.options.length).toBeGreaterThan(2))
      await userEvent.selectOptions(candidateSelect, "c2")
      await waitFor(() => expect(calls.some(u => u.includes("candidate_id=c2"))).toBe(true))
      await waitFor(() =>
        expect(within(screen.getByRole("table")).getByText("c2")).toBeInTheDocument(),
      )
      expect(candidateSelect.value).toBe("c2")
    }, 20000)

    it("nav click away from Agent Timesheets stays on destination", async () => {
      installBaseApiMocks(mockedApi, async (url: string) => {
        if (url.startsWith("/api/admin/timesheets")) {
          return { json: async () => [row] } as Response
        }
        if (url.startsWith("/api/nav_config")) {
          return {
            ok: true,
            json: async () => [
              {
                label: "Admin",
                items: [
                  { label: "Agent Timesheets", path: "/admin/agent_timesheets", enabled: true },
                  { label: "Scheduled Actions", path: "/admin/scheduled_actions", enabled: true },
                ],
              },
            ],
          } as Response
        }
        if (url === "/api/deploy_status") {
          return {
            ok: true,
            json: async () => ({ environment: "local", uptime: "1h", uptime_seconds: 3600 }),
          } as Response
        }
        if (url === "/api/candidates") {
          return {
            json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }],
          } as Response
        }
      })

      renderWithProviders(
        <Routes>
          <Route path="/" element={<NavigationShell />}>
            <Route path="admin/agent_timesheets" element={<AgentTimesheets />} />
            <Route path="admin/scheduled_actions" element={<ScheduledStub />} />
          </Route>
        </Routes>,
        { router: { initialEntries: ["/admin/agent_timesheets?candidate_id=c1"] } },
      )
      await waitFor(() => expect(screen.getByText("Agent Timesheets")).toBeInTheDocument())
      await waitFor(() => expect(screen.getByText("Admin")).toBeInTheDocument())
      await userEvent.click(screen.getByText("Admin"))
      await userEvent.click(screen.getByRole("link", { name: "Scheduled Actions" }))
      await waitFor(() => expect(screen.getByText("Scheduled Actions Page")).toBeInTheDocument())
      expect(screen.getByTestId("pathname")).toHaveTextContent("/admin/scheduled_actions")
    }, 20000)
  })
})
