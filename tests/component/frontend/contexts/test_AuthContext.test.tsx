import { renderHook, waitFor } from "@testing-library/react"
import type { ReactNode } from "react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import { AuthProvider, useAuth } from "../../../../src/ui/frontend/src/contexts/AuthContext"
import { getHadSession, getLogOffReason } from "../../../../src/ui/frontend/src/lib/sessionAuthMark"
import { startSessionExtendLoop } from "../../../../src/ui/frontend/src/lib/sessionExtend"
import { resetStytchTestState, stytchTestState } from "../stytchMock"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

vi.mock("../../../../src/ui/frontend/src/lib/sessionExtend", () => ({
  startSessionExtendLoop: vi.fn(() => () => {}),
}))

const mockedApi = vi.mocked(api)
const mockedStartExtend = vi.mocked(startSessionExtendLoop)

function wrapper({ children }: { children: ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>
}

function stubPolicyFetch(): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input)
      if (url.includes("/api/auth_session_policy")) {
        return Response.json({
          session_duration_minutes: 20,
          activity_extension_interval_minutes: 10,
        })
      }
      return new Response("not found", { status: 404 })
    }),
  )
}

describe("AuthContext", () => {
  beforeEach(() => {
    resetStytchTestState()
    mockedApi.mockReset()
    mockedStartExtend.mockClear()
    stubPolicyFetch()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it("loads /api/me and exposes isAdmin true for admin users", async () => {
    mockedApi.mockResolvedValue({
      ok: true,
      json: async () => ({ user_id: "admin-1", name: "Admin", is_admin: true }),
    } as Response)

    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.isAdmin).toBe(true)
    expect(result.current.user?.user_id).toBe("admin-1")
    expect(mockedApi).toHaveBeenCalledWith("/api/me")
    expect(getHadSession()).toBe(true)
  })

  it("loads /api/me and exposes isAdmin false for non-admin users", async () => {
    mockedApi.mockResolvedValue({
      ok: true,
      json: async () => ({ user_id: "user-1", name: "User", is_admin: false }),
    } as Response)

    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.isAdmin).toBe(false)
    expect(result.current.user?.is_admin).toBe(false)
  })

  it("clears user when Stytch session is absent", async () => {
    stytchTestState.session = null
    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.user).toBeNull()
    expect(result.current.isAdmin).toBe(false)
    expect(mockedApi).not.toHaveBeenCalled()
    expect(mockedStartExtend).not.toHaveBeenCalled()
  })

  it("sets server-rejection when /api/me returns 401", async () => {
    mockedApi.mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({}),
    } as Response)

    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.user).toBeNull()
    expect(getHadSession()).toBe(true)
    expect(getLogOffReason()).toBe("server-rejection")
  })

  it("AST-1374: starts session extend loop while session exists", async () => {
    mockedApi.mockResolvedValue({
      ok: true,
      json: async () => ({ user_id: "admin-1", name: "Admin", is_admin: true }),
    } as Response)

    renderHook(() => useAuth(), { wrapper })

    await waitFor(() => expect(mockedStartExtend).toHaveBeenCalled())
    expect(mockedStartExtend).toHaveBeenCalledWith(
      expect.anything(),
      {
        session_duration_minutes: 20,
        activity_extension_interval_minutes: 10,
      },
    )
  })
})
