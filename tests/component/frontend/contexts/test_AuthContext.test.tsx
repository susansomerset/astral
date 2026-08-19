import { renderHook, waitFor } from "@testing-library/react"
import type { ReactNode } from "react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import { AuthProvider, useAuth } from "../../../../src/ui/frontend/src/contexts/AuthContext"
import { getHadSession, getLogOffReason } from "../../../../src/ui/frontend/src/lib/sessionAuthMark"
import { startSessionExtendLoop } from "../../../../src/ui/frontend/src/lib/sessionExtend"
import { resetStytchTestState, stytchTestState } from "../stytchMock"
import { stubAuthPublicFetches } from "../test-utils"

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

describe("AuthContext", () => {
  beforeEach(() => {
    resetStytchTestState()
    mockedApi.mockReset()
    mockedStartExtend.mockClear()
    stubAuthPublicFetches(false)
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

  it("AST-1408: JWT rotation re-reads /api/me without flipping loading", async () => {
    const meUser = { user_id: "admin-1", name: "Admin", is_admin: true }
    let releaseRevalidate!: (value: Response) => void
    const revalidateGate = new Promise<Response>((resolve) => {
      releaseRevalidate = resolve
    })
    let meCalls = 0
    mockedApi.mockImplementation(() => {
      meCalls += 1
      if (meCalls === 1) {
        return Promise.resolve({
          ok: true,
          json: async () => meUser,
        } as Response)
      }
      return revalidateGate
    })

    const { result, rerender } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.user?.user_id).toBe("admin-1")
    expect(meCalls).toBe(1)

    stytchTestState.sessionJwt = "rotated-jwt"
    rerender()
    await waitFor(() => expect(meCalls).toBe(2))
    expect(result.current.loading).toBe(false)
    expect(result.current.user?.user_id).toBe("admin-1")

    releaseRevalidate({
      ok: true,
      json: async () => meUser,
    } as Response)
    await waitFor(() => expect(result.current.loading).toBe(false))
  })

  it("AST-1408: session object identity change does not restart extend loop", async () => {
    mockedApi.mockResolvedValue({
      ok: true,
      json: async () => ({ user_id: "admin-1", name: "Admin", is_admin: true }),
    } as Response)

    const { rerender } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(mockedStartExtend).toHaveBeenCalledTimes(1))

    stytchTestState.session = { rotated: true }
    rerender()
    await waitFor(() => expect(mockedStartExtend).toHaveBeenCalledTimes(1))
  })

  it("AST-1408: session loss clears user without leaving loading true", async () => {
    mockedApi.mockResolvedValue({
      ok: true,
      json: async () => ({ user_id: "admin-1", name: "Admin", is_admin: true }),
    } as Response)

    const { result, rerender } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.user?.user_id).toBe("admin-1"))

    stytchTestState.session = null
    rerender()
    await waitFor(() => expect(result.current.user).toBeNull())
    expect(result.current.loading).toBe(false)
    expect(result.current.isAdmin).toBe(false)
  })

  it("AST-1441: passthrough loads /api/me with no Stytch session and skips extend", async () => {
    stubAuthPublicFetches(true)
    stytchTestState.session = null
    mockedApi.mockResolvedValue({
      ok: true,
      json: async () => ({ user_id: "local-operator", name: "Local Operator", is_admin: true }),
    } as Response)

    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.localAuthPassthrough).toBe(true)
    expect(result.current.user).toEqual({
      user_id: "local-operator",
      name: "Local Operator",
      is_admin: true,
    })
    expect(result.current.isAdmin).toBe(true)
    expect(mockedApi).toHaveBeenCalledWith("/api/me")
    expect(getHadSession()).toBe(false)
    expect(mockedStartExtend).not.toHaveBeenCalled()
  })

  it("AST-1441: leftover Stytch session does not start extend when passthrough is on", async () => {
    stubAuthPublicFetches(true)
    mockedApi.mockResolvedValue({
      ok: true,
      json: async () => ({ user_id: "local-operator", name: "Local Operator", is_admin: true }),
    } as Response)

    renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(mockedApi).toHaveBeenCalledWith("/api/me"))
    expect(mockedStartExtend).not.toHaveBeenCalled()
  })

  it("AST-1441: passthrough /api/me 401 does not set server-rejection", async () => {
    stubAuthPublicFetches(true)
    stytchTestState.session = null
    mockedApi.mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({}),
    } as Response)

    const { result } = renderHook(() => useAuth(), { wrapper })
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.user).toBeNull()
    expect(getLogOffReason()).toBeNull()
  })
})
