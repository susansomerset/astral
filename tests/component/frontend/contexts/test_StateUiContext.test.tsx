import { renderHook, waitFor } from "@testing-library/react"
import type { ReactNode } from "react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import { AuthProvider } from "../../../../src/ui/frontend/src/contexts/AuthContext"
import {
  StateUiProvider,
  useStateUi,
} from "../../../../src/ui/frontend/src/contexts/StateUiContext"
import { STATE_UI_MANIFEST_FIXTURE } from "../fixtures/stateUiManifestFixture"
import { resetStytchTestState } from "../stytchMock"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

function wrapper({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <StateUiProvider>{children}</StateUiProvider>
    </AuthProvider>
  )
}

describe("StateUiProvider", () => {
  beforeEach(() => {
    resetStytchTestState()
    mockedApi.mockReset()
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return { ok: true, json: async () => ({ user_id: "u1", name: "User", is_admin: true }) } as Response
      }
      throw new Error(url)
    })
  })

  it("loads the manifest from the API", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return { ok: true, json: async () => ({ user_id: "u1", name: "User", is_admin: true }) } as Response
      }
      if (url === "/api/state_ui_manifest") {
        return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
      }
      throw new Error(url)
    })

    const { result } = renderHook(() => useStateUi(), { wrapper })

    await waitFor(() => expect(result.current.loadState).toBe("ready"))
    expect(result.current.manifest?.jobs.in_review_sections[0].label).toBe("New")
  })

  it("leaves manifest null when the request fails", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/me") {
        return { ok: true, json: async () => ({ user_id: "u1", name: "User", is_admin: true }) } as Response
      }
      if (url === "/api/state_ui_manifest") {
        return { ok: false, json: async () => ({}) } as Response
      }
      throw new Error(url)
    })
    const { result } = renderHook(() => useStateUi(), { wrapper })

    await waitFor(() => expect(result.current.loadState).toBe("error"))
    expect(result.current.manifest).toBeNull()
  })
})
