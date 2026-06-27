import type { ReactNode } from "react"

/** Shared Stytch session state for Vitest — reset in beforeEach as needed. */
export const stytchTestState = {
  session: {} as object | null,
  isInitialized: true,
  sessionJwt: "test-session-jwt",
  /** Return value for parseAuthenticateUrl (AST-830). */
  parseAuthenticateUrlResult: null as {
    token: string
    tokenType: string
    handled: boolean
  } | null,
  /** Stub for authenticateByUrl (AST-830). */
  authenticateByUrlImpl: async (_opts: { session_duration_minutes: number }) =>
    ({ handled: true, tokenType: "oauth" }) as {
      handled: boolean
      tokenType?: string
      token?: string
    } | null,
}

export function resetStytchTestState(): void {
  stytchTestState.session = {}
  stytchTestState.isInitialized = true
  stytchTestState.sessionJwt = "test-session-jwt"
  stytchTestState.parseAuthenticateUrlResult = null
  stytchTestState.authenticateByUrlImpl = async () => ({ handled: true, tokenType: "oauth" })
  lastStytchLoginConfig = null
  try {
    sessionStorage.clear()
  } catch {
    /* jsdom private mode */
  }
}

export function StytchProvider({ children }: { children: ReactNode }) {
  return children
}

export function useStytch() {
  return {
    session: {
      getTokens: () =>
        stytchTestState.session
          ? { session_jwt: stytchTestState.sessionJwt }
          : null,
    },
    parseAuthenticateUrl: () => stytchTestState.parseAuthenticateUrlResult,
    authenticateByUrl: stytchTestState.authenticateByUrlImpl,
  }
}

export function useStytchSession() {
  return {
    session: stytchTestState.session,
    isInitialized: stytchTestState.isInitialized,
  }
}

/** Last config passed to StytchLogin — for Login page redirect assertions (AST-613). */
export let lastStytchLoginConfig: unknown = null

export function StytchLogin({ config }: { config?: unknown }) {
  lastStytchLoginConfig = config ?? null
  return <div data-testid="stytch-login">Stytch Login</div>
}
