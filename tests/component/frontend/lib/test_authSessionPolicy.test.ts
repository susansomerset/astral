import { afterEach, describe, expect, it, vi } from "vitest"
import { fetchAuthSessionPolicy } from "../../../../src/ui/frontend/src/lib/authSessionPolicy"

describe("fetchAuthSessionPolicy (AST-1374)", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it("returns ints from GET /api/auth_session_policy via raw fetch", async () => {
    const fetchMock = vi.fn(async () =>
      Response.json({
        session_duration_minutes: 20,
        activity_extension_interval_minutes: 10,
      }),
    )
    vi.stubGlobal("fetch", fetchMock)

    await expect(fetchAuthSessionPolicy()).resolves.toEqual({
      session_duration_minutes: 20,
      activity_extension_interval_minutes: 10,
    })
    expect(fetchMock).toHaveBeenCalledWith("/api/auth_session_policy", {
      credentials: "include",
    })
  })

  it("rejects when response is not ok", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("nope", { status: 503 })),
    )
    await expect(fetchAuthSessionPolicy()).rejects.toThrow(
      "Session policy unavailable (503)",
    )
  })

  it("rejects when duration or cadence is missing or non-positive", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        Response.json({
          session_duration_minutes: 0,
          activity_extension_interval_minutes: 10,
        }),
      ),
    )
    await expect(fetchAuthSessionPolicy()).rejects.toThrow(
      "Session policy response invalid",
    )
  })
})
