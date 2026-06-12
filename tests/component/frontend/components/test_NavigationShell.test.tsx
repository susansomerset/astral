import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import NavigationShell from "../../../../src/ui/frontend/src/components/NavigationShell"
import { renderWithProviders } from "../test-utils"
import { resetStytchTestState } from "../stytchMock"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

vi.mock("../../../../src/ui/frontend/src/assets/astral_logo.png", () => ({
  default: "logo.png",
}))

const mockedApi = vi.mocked(api)

describe("NavigationShell", () => {
  beforeEach(() => {
    localStorage.clear()
    resetStytchTestState()
    mockedApi.mockReset()
  })

  it("renders navigation groups, badges, and candidate selection", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "admin-1", name: "Admin", is_admin: true }),
        } as Response
      }
      if (url === "/api/candidates") {
        return {
          json: async () => [
            { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { first: "Ada", last: "Lovelace" } },
            { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: {} },
          ],
        } as Response
      }
      if (url.startsWith("/api/nav_config")) {
        return {
          ok: true,
          json: async () => [
            {
              label: "Jobs",
              items: [
                { label: "Open", path: "/jobs", enabled: true, count: 3 },
                { label: "Closed", path: "/closed", enabled: false },
              ],
            },
          ],
        } as Response
      }
      throw new Error(url)
    })

    renderWithProviders(<NavigationShell />, {
      router: { initialEntries: ["/jobs"] },
    })

    await waitFor(() => expect(screen.getByText("Jobs")).toBeInTheDocument())
    await userEvent.click(screen.getByText("Jobs"))
    await waitFor(() => expect(screen.getByText("Open")).toBeInTheDocument())
    expect(screen.getByText("[3]")).toBeInTheDocument()
    expect(screen.getByText("Closed")).toBeInTheDocument()
    await waitFor(() => expect(screen.getByRole("combobox")).not.toBeDisabled())
    await userEvent.selectOptions(screen.getByRole("combobox"), "c2")
    expect(localStorage.getItem("astral_selected_candidate")).toBe("c2")
  })

  it("disables candidate select for non-admin users", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "user-1", name: "User", is_admin: false }),
        } as Response
      }
      if (url === "/api/candidates") {
        return {
          json: async () => [
            { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { first: "Ada", last: "Lovelace" } },
            { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: {} },
          ],
        } as Response
      }
      if (url.startsWith("/api/nav_config")) {
        return { ok: true, json: async () => [] } as Response
      }
      throw new Error(url)
    })

    renderWithProviders(<NavigationShell />)
    await waitFor(() => expect(screen.getByRole("combobox")).toBeDisabled())
  })

  it("shows loading and error states", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "admin-1", name: "Admin", is_admin: true }),
        } as Response
      }
      if (url === "/api/candidates") {
        return { json: async () => [] } as Response
      }
      if (url.startsWith("/api/nav_config")) {
        return { ok: false, status: 500 } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(<NavigationShell />)
    expect(screen.getByText("Loading...")).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText("Failed to load navigation. Check server connection.")).toBeInTheDocument())
  })
})
