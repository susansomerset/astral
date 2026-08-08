import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { Route, Routes, useLocation } from "react-router-dom"
import api from "../../../../src/ui/frontend/src/lib/api"
import NavigationShell from "../../../../src/ui/frontend/src/components/NavigationShell"
import { renderWithProviders, stubNavViewport } from "../test-utils"
import { resetStytchTestState } from "../stytchMock"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

vi.mock("../../../../src/ui/frontend/src/assets/astral_logo.png", () => ({
  default: "logo.png",
}))

const mockedApi = vi.mocked(api)

const candidatesFixture = [
  { astral_candidate_id: "c1", state: "ACTIVE", first: "Ada", last: "Lovelace", candidate_data: {} },
  { astral_candidate_id: "c2", state: "ACTIVE", first: "Grace", last: "Hopper", candidate_data: {} },
]

function PathProbe() {
  const { pathname } = useLocation()
  return <div data-testid="pathname">{pathname}</div>
}

function mockShellApis(opts: { isAdmin: boolean; navGroups?: unknown[] }) {
  const navGroups = opts.navGroups ?? [
    {
      label: "Jobs",
      items: [
        { label: "Open", path: "/jobs", enabled: true, count: 3 },
        { label: "Closed", path: "/closed", enabled: false },
        { label: "Recommended", path: "/recommended", enabled: true },
      ],
    },
  ]
  mockedApi.mockImplementation(async (url: string) => {
    if (url === "/api/me") {
      return {
        ok: true,
        json: async () => ({
          user_id: opts.isAdmin ? "admin-1" : "user-1",
          name: opts.isAdmin ? "Admin" : "User",
          is_admin: opts.isAdmin,
        }),
      } as Response
    }
    if (url === "/api/candidates") {
      return { json: async () => candidatesFixture } as Response
    }
    if (url.startsWith("/api/nav_config")) {
      return { ok: true, json: async () => navGroups } as Response
    }
    if (url === "/api/deploy_status") {
      return {
        ok: true,
        json: async () => ({
          environment: "local",
          uptime: "1h15m",
          uptime_seconds: 4500,
        }),
      } as Response
    }
    throw new Error(url)
  })
}

describe("NavigationShell", () => {
  beforeEach(() => {
    localStorage.clear()
    resetStytchTestState()
    mockedApi.mockReset()
    stubNavViewport(true)
  })

  it("renders navigation groups, badges, and candidate selection", async () => {
    mockShellApis({ isAdmin: true })

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
    await waitFor(() => expect(screen.getByLabelText("Deploy status")).toBeInTheDocument())
    expect(screen.getByText("local")).toBeInTheDocument()
    expect(screen.getByText("1h15m")).toBeInTheDocument()
  })

  it("disables candidate select for non-admin users", async () => {
    mockShellApis({ isAdmin: false, navGroups: [] })

    renderWithProviders(<NavigationShell />)
    await waitFor(() => expect(screen.getByRole("combobox")).toBeDisabled())
    expect(screen.queryByLabelText("Deploy status")).not.toBeInTheDocument()
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
      if (url === "/api/deploy_status") {
        return {
          ok: true,
          json: async () => ({
            uptime: "5m",
            uptime_seconds: 300,
          }),
        } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(<NavigationShell />)
    expect(screen.getByText("Loading...")).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText("Failed to load navigation. Check server connection.")).toBeInTheDocument())
  })

  describe("AST-1286 responsive shell", () => {
    it("wide viewport keeps native candidate select (no checked list)", async () => {
      stubNavViewport(true)
      mockShellApis({ isAdmin: true })
      renderWithProviders(<NavigationShell />, { router: { initialEntries: ["/jobs"] } })
      await waitFor(() => expect(screen.getByRole("combobox")).toBeInTheDocument())
      expect(screen.queryByRole("button", { name: "Ada Lovelace" })).not.toBeInTheDocument()
      expect(document.querySelector(".sidebar-candidate-menu")).toBeNull()
    })

    it("narrow: hamburger opens drawer; backdrop dismisses without route change", async () => {
      stubNavViewport(false)
      mockShellApis({ isAdmin: true })
      renderWithProviders(
        <Routes>
          <Route path="/" element={<NavigationShell />}>
            <Route path="jobs" element={<PathProbe />} />
            <Route path="recommended" element={<PathProbe />} />
          </Route>
        </Routes>,
        { router: { initialEntries: ["/jobs"] } },
      )
      await waitFor(() => expect(screen.getByText("Jobs")).toBeInTheDocument())
      const openBtn = screen.getByRole("button", { name: "Open navigation" })
      expect(openBtn).toHaveAttribute("aria-expanded", "false")
      expect(document.querySelector(".nav-backdrop")).toBeNull()

      await userEvent.click(openBtn)
      expect(screen.getByRole("button", { name: "Close navigation" })).toHaveAttribute("aria-expanded", "true")
      expect(document.getElementById("app-sidebar")).toHaveClass("sidebar--open")
      const backdrop = document.querySelector(".nav-backdrop")
      expect(backdrop).not.toBeNull()

      await userEvent.click(backdrop as Element)
      await waitFor(() => {
        expect(screen.getByRole("button", { name: "Open navigation" })).toHaveAttribute("aria-expanded", "false")
      })
      expect(document.querySelector(".nav-backdrop")).toBeNull()
      expect(screen.getByTestId("pathname")).toHaveTextContent("/jobs")
    })

    it("narrow: enabled nav destination navigates and closes drawer", async () => {
      stubNavViewport(false)
      mockShellApis({ isAdmin: true })
      renderWithProviders(
        <Routes>
          <Route path="/" element={<NavigationShell />}>
            <Route path="jobs" element={<PathProbe />} />
            <Route path="recommended" element={<PathProbe />} />
          </Route>
        </Routes>,
        { router: { initialEntries: ["/jobs"] } },
      )
      await waitFor(() => expect(screen.getByText("Jobs")).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: "Open navigation" }))
      await userEvent.click(screen.getByText("Jobs"))
      await userEvent.click(screen.getByRole("link", { name: /Recommended/ }))
      await waitFor(() => expect(screen.getByTestId("pathname")).toHaveTextContent("/recommended"))
      expect(screen.getByRole("button", { name: "Open navigation" })).toHaveAttribute("aria-expanded", "false")
      expect(document.querySelector(".nav-backdrop")).toBeNull()
    })

    it("narrow: admin checked candidate list selects and marks current", async () => {
      stubNavViewport(false)
      mockShellApis({ isAdmin: true })
      renderWithProviders(<NavigationShell />, { router: { initialEntries: ["/jobs"] } })
      await waitFor(() => expect(screen.getByRole("button", { name: "Ada Lovelace" })).toBeInTheDocument())
      expect(screen.queryByRole("combobox")).not.toBeInTheDocument()

      await userEvent.click(screen.getByRole("button", { name: "Ada Lovelace" }))
      const list = document.querySelector(".sidebar-candidate-menu-list") as HTMLElement
      expect(list).not.toBeNull()
      const selected = within(list).getByRole("button", { name: /✓ Ada Lovelace/ })
      expect(selected).toHaveClass("is-selected")

      await userEvent.click(within(list).getByRole("button", { name: /Grace Hopper/ }))
      expect(localStorage.getItem("astral_selected_candidate")).toBe("c2")
      await waitFor(() => expect(screen.getByRole("button", { name: "Grace Hopper" })).toBeInTheDocument())
      // Menu closes after select; drawer stays open (pathname unchanged).
      expect(document.querySelector(".sidebar-candidate-menu-list")).toBeNull()
    })

    it("narrow: non-admin cannot change candidate; deploy footer omitted", async () => {
      stubNavViewport(false)
      mockShellApis({ isAdmin: false, navGroups: [] })
      renderWithProviders(<NavigationShell />)
      await waitFor(() => expect(screen.getByRole("button", { name: "Ada Lovelace" })).toBeInTheDocument())
      expect(screen.queryByLabelText("Deploy status")).not.toBeInTheDocument()

      await userEvent.click(screen.getByRole("button", { name: "Ada Lovelace" }))
      const list = document.querySelector(".sidebar-candidate-menu-list") as HTMLElement
      const other = within(list).getByRole("button", { name: /Grace Hopper/ })
      expect(other).toBeDisabled()
      await userEvent.click(other)
      expect(localStorage.getItem("astral_selected_candidate")).toBe("c1")
    })
  })
})
