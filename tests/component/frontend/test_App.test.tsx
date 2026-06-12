import { render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../src/ui/frontend/src/lib/api"
import App from "../../../src/ui/frontend/src/App"
import { resetStytchTestState } from "./stytchMock"

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

  it("redirects the index route into the jobs shell", async () => {
    window.history.pushState({}, "", "/")
    render(<App />)
    await waitFor(() => expect(screen.getByText("Recommended")).toBeInTheDocument())
  })
})
