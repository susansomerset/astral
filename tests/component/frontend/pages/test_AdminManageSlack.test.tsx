import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AdminManageSlack from "../../../../src/ui/frontend/src/pages/AdminManageSlack"
import { installBaseApiMocks, jsonResponse, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("AdminManageSlack — AST-1067 / AST-1094 (§6c routed page)", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  function mockApis(
    extra?: (url: string, init?: RequestInit) => Promise<Response | undefined> | Response | undefined,
  ) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      const fromExtra = extra ? await extra(url, init) : undefined
      if (fromExtra !== undefined) return fromExtra
      if (url === "/api/admin/contact/listen" && (!init || !init.method || init.method === "GET")) {
        return jsonResponse({
          listen_enabled: false,
          environment: "staging",
          is_production: false,
        })
      }
      if (url === "/api/admin/contact/estelle_activity") {
        return jsonResponse({ users: [] })
      }
    })
  }

  it("renders Manage Slack heading and listen state on first paint", async () => {
    mockApis()
    renderWithProviders(<AdminManageSlack />)
    expect(screen.getByRole("heading", { name: "Manage Slack" })).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText("staging")).toBeInTheDocument())
    expect(screen.getByText("Off")).toBeInTheDocument()
    expect(screen.getByText(/Non-production/)).toBeInTheDocument()
    expect(mockedApi).toHaveBeenCalledWith("/api/admin/contact/listen")
    expect(mockedApi).toHaveBeenCalledWith("/api/admin/contact/estelle_activity")
  })

  it("toggle PUT enables listen and shows success toast", async () => {
    const user = userEvent.setup()
    mockApis(async (url, init) => {
      if (url === "/api/admin/contact/listen" && init?.method === "PUT") {
        return jsonResponse({
          listen_enabled: true,
          environment: "staging",
          is_production: false,
        })
      }
    })
    renderWithProviders(<AdminManageSlack />)
    await waitFor(() => expect(screen.getByText("Off")).toBeInTheDocument())
    await user.click(screen.getByRole("button", { name: "Enable listen" }))
    await waitFor(() => expect(screen.getByText("On")).toBeInTheDocument())
    expect(screen.getByText("Slack listen enabled")).toBeInTheDocument()
  })

  it("renders @Estelle users activity table from GET estelle_activity (AST-1094)", async () => {
    mockApis(async (url) => {
      if (url === "/api/admin/contact/estelle_activity") {
        return jsonResponse({
          users: [
            {
              slack_user_id: "U-estelle",
              bind_ok: true,
              astral_candidate_id: "cand-1",
              candidate_state: "PROSPECT",
              inbound_message_count: 3,
              last_channel: "C-home",
              last_message_ts: "1710000000.000100",
            },
          ],
        })
      }
    })
    renderWithProviders(<AdminManageSlack />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "@Estelle users" })).toBeInTheDocument(),
    )
    expect(screen.getByText("U-estelle")).toBeInTheDocument()
    expect(screen.getByText("ok")).toBeInTheDocument()
    expect(screen.getByText("cand-1")).toBeInTheDocument()
    expect(screen.getByText("3")).toBeInTheDocument()
    expect(screen.getByText("C-home")).toBeInTheDocument()
    expect(screen.getByText("1710000000.000100")).toBeInTheDocument()
  })

  it("shows empty activity copy when no users recorded (AST-1094)", async () => {
    mockApis()
    renderWithProviders(<AdminManageSlack />)
    await waitFor(() =>
      expect(screen.getByText("No @Estelle users recorded yet.")).toBeInTheDocument(),
    )
  })
})
