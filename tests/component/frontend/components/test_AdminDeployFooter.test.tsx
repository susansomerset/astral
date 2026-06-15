import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
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

  it("opens merge ticket popup on environment button click when merge_tickets present", async () => {
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
    await waitFor(() => expect(screen.getByRole("button", { name: "local" })).toBeInTheDocument())
    const envBtn = screen.getByRole("button", { name: "local" })
    expect(envBtn).not.toHaveAttribute("title")
    expect(envBtn).toHaveAttribute("aria-expanded", "false")

    await userEvent.click(envBtn)
    const popup = screen.getByRole("listbox", { name: "Recent merge tickets" })
    expect(envBtn).toHaveAttribute("aria-expanded", "true")
    const items = within(popup).getAllByRole("listitem")
    expect(items).toHaveLength(2)
    expect(items[0]).toHaveTextContent(`AST-675 ${fmtTime(recent, "UTC")}`)
    expect(items[1]).toHaveTextContent(`AST-646 ${fmtTime(older, "UTC")}`)
    expect(screen.getByText("5m")).not.toHaveAttribute("title")
  })

  it("closes merge ticket popup on second click or outside mousedown", async () => {
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
    await waitFor(() => expect(screen.getByRole("button", { name: "dev" })).toBeInTheDocument())
    const envBtn = screen.getByRole("button", { name: "dev" })

    await userEvent.click(envBtn)
    expect(screen.getByRole("listbox", { name: "Recent merge tickets" })).toBeInTheDocument()

    await userEvent.click(envBtn)
    expect(screen.queryByRole("listbox", { name: "Recent merge tickets" })).not.toBeInTheDocument()

    await userEvent.click(envBtn)
    expect(screen.getByRole("listbox", { name: "Recent merge tickets" })).toBeInTheDocument()
    fireEvent.mouseDown(document.body)
    expect(screen.queryByRole("listbox", { name: "Recent merge tickets" })).not.toBeInTheDocument()
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
    expect(screen.queryByRole("button", { name: "staging" })).not.toBeInTheDocument()
    expect(screen.getByText("staging")).not.toHaveAttribute("title")
    expect(screen.queryByRole("listbox", { name: "Recent merge tickets" })).not.toBeInTheDocument()
  })

  it("caps merge ticket popup at 20 list items", async () => {
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
    await waitFor(() => expect(screen.getByRole("button", { name: "prod" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "prod" }))
    const popup = screen.getByRole("listbox", { name: "Recent merge tickets" })
    const items = within(popup).getAllByRole("listitem")
    expect(items).toHaveLength(20)
    expect(items[0]).toHaveTextContent("AST-0")
    expect(items[19]).toHaveTextContent("AST-19")
    expect(within(popup).queryByText(/AST-24/)).not.toBeInTheDocument()
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
