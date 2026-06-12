import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"

describe("api", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response("ok")))
  })

  it("adds the bearer token and forwards fetch options", async () => {
    const response = await api("/api/ping", { method: "POST", headers: { "X-Test": "1" } })
    expect(response.status).toBe(200)
    expect(fetch).toHaveBeenCalledWith("/api/ping", expect.objectContaining({ method: "POST" }))
    const headers = (fetch as ReturnType<typeof vi.fn>).mock.calls[0][1].headers as Headers
    expect(headers.get("Authorization")).toBe("Bearer stub-susan-token")
    expect(headers.get("X-Test")).toBe("1")
  })
})
