import { beforeEach, describe, expect, it, vi } from "vitest"
import api, { setAuthTokenGetter } from "../../../../src/ui/frontend/src/lib/api"

describe("api", () => {
  beforeEach(() => {
    setAuthTokenGetter(() => null)
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
})
