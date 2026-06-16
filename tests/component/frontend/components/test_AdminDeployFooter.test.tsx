import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AdminDeployFooter from "../../../../src/ui/frontend/src/components/AdminDeployFooter"
import { fmtTime, setFmtTimezone } from "../../../../src/ui/frontend/src/lib/fmt"
import { renderWithProviders } from "../test-utils"
import { resetStytchTestState } from "../stytchMock"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

describe("AdminDeployFooter", () => {
  beforeEach(() => {
    resetStytchTestState()
    mockedApi.mockReset()
    setFmtTimezone("UTC")
  })

  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

  it("renders environment and uptime when deploy_status succeeds", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "admin-1", name: "Admin", is_admin: true }),
        } as Response
      }
      if (url === "/api/deploy_status") {
        return {
          ok: true,
          json: async () => ({
            environment: "local",
            uptime: "5m",
            uptime_seconds: 300,
          }),
        } as Response
      }
      throw new Error(url)
    })

    renderWithProviders(<AdminDeployFooter />)
    await waitFor(() => expect(screen.getByLabelText("Deploy status")).toBeInTheDocument())
    expect(screen.getByText("local")).toBeInTheDocument()
    expect(screen.getByText("5m")).toBeInTheDocument()
  })

  it("shows merge ticket tooltip after 500ms hover on env wrap when merge_tickets present", async () => {
    const recent = "2026-05-13T12:00:00Z"
    const older = "2026-05-13T11:00:00Z"
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "admin-1", name: "Admin", is_admin: true }),
        } as Response
      }
      if (url === "/api/deploy_status") {
        return {
          ok: true,
          json: async () => ({
            environment: "local",
            uptime: "5m",
            uptime_seconds: 300,
            merge_tickets: [
              { ticket_id: "AST-675", recorded_at: recent },
              { ticket_id: "AST-646", recorded_at: older },
            ],
          }),
        } as Response
      }
      throw new Error(url)
    })

    renderWithProviders(<AdminDeployFooter />)
    await waitFor(() => expect(screen.getByText("local")).toBeInTheDocument())
    const envLabel = screen.getByText("local")
    expect(envLabel).toHaveClass("nav-deploy-env-interactive")
    expect(envLabel).not.toHaveAttribute("title")
    expect(screen.queryByRole("tooltip", { name: "Recent merge tickets" })).not.toBeInTheDocument()

    const envWrap = envLabel.closest(".nav-deploy-env-wrap")
    expect(envWrap).not.toBeNull()
    fireEvent.mouseEnter(envWrap!)

    await delay(200)
    expect(screen.queryByRole("tooltip", { name: "Recent merge tickets" })).not.toBeInTheDocument()

    await waitFor(
      () => expect(screen.getByRole("tooltip", { name: "Recent merge tickets" })).toBeInTheDocument(),
      { timeout: 800 },
    )
    const tooltip = screen.getByRole("tooltip", { name: "Recent merge tickets" })
    const lines = within(tooltip).getAllByText(/AST-\d+/)
    expect(lines).toHaveLength(2)
    expect(lines[0]).toHaveTextContent(`AST-675 ${fmtTime(recent)}`)
    expect(lines[1]).toHaveTextContent(`AST-646 ${fmtTime(older)}`)
    expect(screen.getByText("5m")).not.toHaveAttribute("title")
  })

  it("hides merge ticket tooltip before 500ms hover and on mouse leave", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "admin-1", name: "Admin", is_admin: true }),
        } as Response
      }
      if (url === "/api/deploy_status") {
        return {
          ok: true,
          json: async () => ({
            environment: "dev",
            uptime: "5m",
            uptime_seconds: 300,
            merge_tickets: [{ ticket_id: "AST-675", recorded_at: "2026-05-13T12:00:00Z" }],
          }),
        } as Response
      }
      throw new Error(url)
    })

    renderWithProviders(<AdminDeployFooter />)
    await waitFor(() => expect(screen.getByText("dev")).toBeInTheDocument())
    const envWrap = screen.getByText("dev").closest(".nav-deploy-env-wrap")!

    fireEvent.mouseEnter(envWrap)
    await delay(200)
    expect(screen.queryByRole("tooltip", { name: "Recent merge tickets" })).not.toBeInTheDocument()

    fireEvent.mouseLeave(envWrap)
    await delay(600)
    expect(screen.queryByRole("tooltip", { name: "Recent merge tickets" })).not.toBeInTheDocument()

    fireEvent.mouseEnter(envWrap)
    await waitFor(
      () => expect(screen.getByRole("tooltip", { name: "Recent merge tickets" })).toBeInTheDocument(),
      { timeout: 800 },
    )

    fireEvent.mouseLeave(envWrap)
    await waitFor(
      () => expect(screen.queryByRole("tooltip", { name: "Recent merge tickets" })).not.toBeInTheDocument(),
    )
  })

  it("renders static environment span when merge_tickets empty or missing", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "admin-1", name: "Admin", is_admin: true }),
        } as Response
      }
      if (url === "/api/deploy_status") {
        return {
          ok: true,
          json: async () => ({
            environment: "staging",
            uptime: "1h",
            uptime_seconds: 3600,
            merge_tickets: [],
          }),
        } as Response
      }
      throw new Error(url)
    })

    renderWithProviders(<AdminDeployFooter />)
    await waitFor(() => expect(screen.getByText("staging")).toBeInTheDocument())
    const envLabel = screen.getByText("staging")
    expect(envLabel).not.toHaveClass("nav-deploy-env-interactive")
    expect(envLabel).not.toHaveAttribute("title")
    expect(screen.queryByRole("tooltip", { name: "Recent merge tickets" })).not.toBeInTheDocument()
  })

  it("caps merge ticket tooltip at 20 lines", async () => {
    const merge_tickets = Array.from({ length: 25 }, (_, i) => ({
      ticket_id: `AST-${i}`,
      recorded_at: "2026-05-13T12:00:00Z",
    }))
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "admin-1", name: "Admin", is_admin: true }),
        } as Response
      }
      if (url === "/api/deploy_status") {
        return {
          ok: true,
          json: async () => ({
            environment: "prod",
            uptime: "2d",
            uptime_seconds: 172800,
            merge_tickets,
          }),
        } as Response
      }
      throw new Error(url)
    })

    renderWithProviders(<AdminDeployFooter />)
    await waitFor(() => expect(screen.getByText("prod")).toBeInTheDocument())
    const envWrap = screen.getByText("prod").closest(".nav-deploy-env-wrap")!
    fireEvent.mouseEnter(envWrap)
    await waitFor(
      () => expect(screen.getByRole("tooltip", { name: "Recent merge tickets" })).toBeInTheDocument(),
      { timeout: 800 },
    )

    const tooltip = screen.getByRole("tooltip", { name: "Recent merge tickets" })
    const lines = within(tooltip).getAllByText(/^AST-\d+/)
    expect(lines).toHaveLength(20)
    expect(lines[0]).toHaveTextContent("AST-0")
    expect(lines[19]).toHaveTextContent("AST-19")
    expect(within(tooltip).queryByText(/AST-24/)).not.toBeInTheDocument()
  })

  it("omits environment label when API payload has no environment", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "admin-1", name: "Admin", is_admin: true }),
        } as Response
      }
      if (url === "/api/deploy_status") {
        return {
          ok: true,
          json: async () => ({
            uptime: "<1m",
            uptime_seconds: 10,
          }),
        } as Response
      }
      throw new Error(url)
    })

    renderWithProviders(<AdminDeployFooter />)
    await waitFor(() => expect(screen.getByText("<1m")).toBeInTheDocument())
    expect(screen.queryByText("local")).not.toBeInTheDocument()
  })

  it("shows unavailable message when deploy_status fetch fails", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "admin-1", name: "Admin", is_admin: true }),
        } as Response
      }
      if (url === "/api/deploy_status") {
        return { ok: false, status: 500 } as Response
      }
      throw new Error(url)
    })

    renderWithProviders(<AdminDeployFooter />)
    await waitFor(() => expect(screen.getByText("Deploy status unavailable")).toBeInTheDocument())
  })
})
