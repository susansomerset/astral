import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const HELPER_PATH = "../../../../src/ui/frontend/src/lib/stytchRedirect"

describe("getStytchAuthenticateRedirectUrl", () => {
  beforeEach(() => {
    vi.stubGlobal("window", { location: { origin: "http://localhost:5173" } })
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.resetModules()
  })

  it("returns VITE_STYTCH_REDIRECT_URL trimmed without trailing slash", async () => {
    vi.stubEnv("VITE_STYTCH_REDIRECT_URL", "  https://staging.example.com/authenticate/  ")
    const { getStytchAuthenticateRedirectUrl } = await import(HELPER_PATH)
    expect(getStytchAuthenticateRedirectUrl()).toBe("https://staging.example.com/authenticate")
  })

  it("falls back to window.location.origin/authenticate when env unset", async () => {
    vi.stubEnv("VITE_STYTCH_REDIRECT_URL", "")
    const { getStytchAuthenticateRedirectUrl } = await import(HELPER_PATH)
    expect(getStytchAuthenticateRedirectUrl()).toBe("http://localhost:5173/authenticate")
  })

  it("strips trailing slash from origin fallback", async () => {
    vi.stubGlobal("window", { location: { origin: "http://localhost:5173/" } })
    vi.stubEnv("VITE_STYTCH_REDIRECT_URL", "")
    const { getStytchAuthenticateRedirectUrl } = await import(HELPER_PATH)
    expect(getStytchAuthenticateRedirectUrl()).toBe("http://localhost:5173/authenticate")
  })
})
