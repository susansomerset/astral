import { beforeEach, describe, expect, it, vi } from "vitest"
import api, { setAuthTokenGetter, setUnauthorizedHandler } from "../../../../src/ui/frontend/src/lib/api"
import {
  clearSessionAuthMarks,
  getLogOffReason,
  markHadSession,
} from "../../../../src/ui/frontend/src/lib/sessionAuthMark"

describe("api", () => {
  beforeEach(() => {
    clearSessionAuthMarks()
    setAuthTokenGetter(() => null)
    setUnauthorizedHandler(null)
    vi.stubGlobal("fetch", vi.fn(async () => new Response("ok")))
  })

  it("adds the bearer token when a getter is registered", async () => {
    setAuthTokenGetter(() => "session-jwt-abc")
    const response = await api("/api/ping", { method: "POST", headers: { "X-Test": "1" } })
    expect(response.status).toBe(200)
    expect(fetch).toHaveBeenCalledWith("/api/ping", expect.objectContaining({ method: "POST" }))
    const headers = (fetch as ReturnType<typeof vi.fn>).mock.calls[0][1].headers as Headers
    expect(headers.get("Authorization")).toBe("Bearer session-jwt-abc")
    expect(headers.get("X-Test")).toBe("1")
  })

  it("omits Authorization when no token getter returns a value", async () => {
    await api("/api/ping")
    const headers = (fetch as ReturnType<typeof vi.fn>).mock.calls[0][1].headers as Headers
    expect(headers.get("Authorization")).toBeNull()
  })

  it("sets server-rejection and calls unauthorized handler on 401 when had-session", async () => {
    markHadSession()
    const handler = vi.fn()
    setUnauthorizedHandler(handler)
    vi.stubGlobal("fetch", vi.fn(async () => new Response("unauthorized", { status: 401 })))
    const response = await api("/api/ping")
    expect(response.status).toBe(401)
    expect(getLogOffReason()).toBe("server-rejection")
    expect(handler).toHaveBeenCalledOnce()
  })

  it("does not set log-off reason on 401 for first-time visitors", async () => {
    const handler = vi.fn()
    setUnauthorizedHandler(handler)
    vi.stubGlobal("fetch", vi.fn(async () => new Response("unauthorized", { status: 401 })))
    await api("/api/ping")
    expect(getLogOffReason()).toBeNull()
    expect(handler).not.toHaveBeenCalled()
  })
})
