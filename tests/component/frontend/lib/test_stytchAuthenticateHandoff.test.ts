import { describe, expect, it, vi } from "vitest"
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

describe("completeAuthenticateFromUrl", () => {
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

  it("returns success when authenticateByUrl handles the token", async () => {
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
    expect(authenticateByUrl).toHaveBeenCalledWith({ session_duration_minutes: 60 })
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
