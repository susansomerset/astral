import { afterEach, describe, expect, it, vi } from "vitest"
import { fetchAuthPassthrough } from "../../../../src/ui/frontend/src/lib/authPassthrough"

describe("fetchAuthPassthrough (AST-1441)", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it("returns true only when local_auth_passthrough is boolean true", async () => {
    const fetchMock = vi.fn(async () => Response.json({ local_auth_passthrough: true }))
    vi.stubGlobal("fetch", fetchMock)
    await expect(fetchAuthPassthrough()).resolves.toBe(true)
    expect(fetchMock).toHaveBeenCalledWith("/api/auth_passthrough", { credentials: "include" })
  })

  it("fails closed for false, missing field, string true, non-ok, and network error", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => Response.json({ local_auth_passthrough: false })))
    await expect(fetchAuthPassthrough()).resolves.toBe(false)

    vi.stubGlobal("fetch", vi.fn(async () => Response.json({})))
    await expect(fetchAuthPassthrough()).resolves.toBe(false)

    vi.stubGlobal("fetch", vi.fn(async () => Response.json({ local_auth_passthrough: "true" })))
    await expect(fetchAuthPassthrough()).resolves.toBe(false)

    vi.stubGlobal("fetch", vi.fn(async () => new Response("nope", { status: 503 })))
    await expect(fetchAuthPassthrough()).resolves.toBe(false)

    vi.stubGlobal("fetch", vi.fn(async () => {
      throw new Error("network")
    }))
    await expect(fetchAuthPassthrough()).resolves.toBe(false)
  })
})
