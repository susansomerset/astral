import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import {
  completeAuthenticateFromUrl,
  type StytchAuthenticateClient,
} from "../../../../src/ui/frontend/src/lib/stytchAuthenticateHandoff"

function makeClient(
  overrides: Partial<StytchAuthenticateClient> = {},
): StytchAuthenticateClient {
  return {
    parseAuthenticateUrl: () => null,
    authenticateByUrl: vi.fn(async () => ({ handled: true, tokenType: "oauth" })),
    ...overrides,
  }
}

function stubPolicy(
  policy: {
    session_duration_minutes: number
    activity_extension_interval_minutes: number
  } = {
    session_duration_minutes: 20,
    activity_extension_interval_minutes: 10,
  },
): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => Response.json(policy)),
  )
}

describe("completeAuthenticateFromUrl", () => {
  beforeEach(() => {
    stubPolicy()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it("returns no-token when parseAuthenticateUrl is missing", async () => {
    const stytch = makeClient({ parseAuthenticateUrl: undefined })
    await expect(completeAuthenticateFromUrl(stytch)).resolves.toEqual({
      outcome: "no-token",
    })
  })

  it("returns no-token when parseAuthenticateUrl finds nothing", async () => {
    const stytch = makeClient({ parseAuthenticateUrl: () => null })
    await expect(completeAuthenticateFromUrl(stytch)).resolves.toEqual({
      outcome: "no-token",
    })
  })

  it("returns unsupported-token when parsed token is not handled", async () => {
    const stytch = makeClient({
      parseAuthenticateUrl: () => ({
        token: "t1",
        tokenType: "reset_password",
        handled: false,
      }),
    })
    await expect(completeAuthenticateFromUrl(stytch)).resolves.toEqual({
      outcome: "unsupported-token",
      tokenType: "reset_password",
      message: 'Sign-in link type "reset_password" is not supported here.',
    })
  })

  it("returns success with configured session_duration_minutes (not hardcoded 60)", async () => {
    const authenticateByUrl = vi.fn(async () => ({
      handled: true,
      tokenType: "magic_links",
    }))
    const stytch = makeClient({
      parseAuthenticateUrl: () => ({
        token: "t1",
        tokenType: "oauth",
        handled: true,
      }),
      authenticateByUrl,
    })
    await expect(completeAuthenticateFromUrl(stytch)).resolves.toEqual({
      outcome: "success",
      tokenType: "magic_links",
    })
    expect(authenticateByUrl).toHaveBeenCalledWith({ session_duration_minutes: 20 })
  })

  it("returns error when policy fetch fails (no fallback duration)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("down", { status: 500 })),
    )
    const authenticateByUrl = vi.fn(async () => ({ handled: true }))
    const stytch = makeClient({
      parseAuthenticateUrl: () => ({
        token: "t1",
        tokenType: "oauth",
        handled: true,
      }),
      authenticateByUrl,
    })
    await expect(completeAuthenticateFromUrl(stytch)).resolves.toEqual({
      outcome: "error",
      tokenType: "oauth",
      message: "Session policy unavailable (500)",
    })
    expect(authenticateByUrl).not.toHaveBeenCalled()
  })

  it("returns error when authenticateByUrl resolves without handled", async () => {
    const stytch = makeClient({
      parseAuthenticateUrl: () => ({
        token: "t1",
        tokenType: "oauth",
        handled: true,
      }),
      authenticateByUrl: vi.fn(async () => ({ handled: false })),
    })
    await expect(completeAuthenticateFromUrl(stytch)).resolves.toEqual({
      outcome: "error",
      tokenType: "oauth",
      message: "Sign-in could not be completed.",
    })
  })

  it("returns error with message when authenticateByUrl rejects", async () => {
    const stytch = makeClient({
      parseAuthenticateUrl: () => ({
        token: "t1",
        tokenType: "oauth",
        handled: true,
      }),
      authenticateByUrl: vi.fn(async () => {
        throw new Error("OAuth token already consumed")
      }),
    })
    await expect(completeAuthenticateFromUrl(stytch)).resolves.toEqual({
      outcome: "error",
      tokenType: "oauth",
      message: "OAuth token already consumed",
    })
  })
})
