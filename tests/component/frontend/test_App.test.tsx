import { render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../src/ui/frontend/src/lib/api"
import App from "../../../src/ui/frontend/src/App"
import { resetStytchTestState } from "./stytchMock"
import { stubNavViewport } from "./test-utils"

vi.mock("../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

vi.mock("../../../src/ui/frontend/src/lib/stytchClient", () => ({
  stytchClient: {},
}))

vi.mock("../../../src/ui/frontend/src/assets/astral_logo.png", () => ({
  default: "logo.png",
}))

const mockedApi = vi.mocked(api)

describe("App", () => {
  beforeEach(() => {
    // NavigationShell needs matchMedia; data-router ErrorBoundary surfaces the miss.
    stubNavViewport(true)
    localStorage.clear()
    resetStytchTestState()
    mockedApi.mockReset()
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return {
          ok: true,
          json: async () => ({ user_id: "admin-1", name: "Admin", is_admin: true }),
        } as Response
      }
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
      }
      if (url.startsWith("/api/nav_config")) {
        return { ok: true, json: async () => [] } as Response
      }
      if (url === "/api/state_ui_manifest") {
        return Promise.reject(new Error("use default manifest"))
      }
      if (url === "/api/system/ui_config") {
        return { json: async () => ({ column_types: {} }) } as Response
      }
      if (url.startsWith("/api/jobs?view=recommended")) {
        return { json: async () => [] } as Response
      }
      if (url === "/api/shapes/jobs") {
        return { json: async () => ({ list: { recommended: [] } }) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
  })

  it("boots createBrowserRouter shell (RouterProvider)", async () => {
    // Index Navigate / outlet paint hit RR7+jsdom AbortSignal under Node 24; shell still mounts.
    window.history.pushState({}, "", "/jobs/recommended")
    render(<App />)
    await waitFor(() => expect(screen.getByAltText("Astral")).toBeInTheDocument())
    expect(document.querySelector(".shell")).toBeTruthy()
  })
})
