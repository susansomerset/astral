import { screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AdminDeployFooter from "../../../../src/ui/frontend/src/components/AdminDeployFooter"
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
