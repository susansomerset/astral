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
  /** Stub for session.authenticate extend loop (AST-1374). */
  sessionAuthenticateImpl: async (_opts: {
    session_duration_minutes: number
  }) => ({} as unknown),
}

export function resetStytchTestState(): void {
  stytchTestState.session = {}
  stytchTestState.isInitialized = true
  stytchTestState.sessionJwt = "test-session-jwt"
  stytchTestState.parseAuthenticateUrlResult = null
  stytchTestState.authenticateByUrlImpl = async () => ({ handled: true, tokenType: "oauth" })
  stytchTestState.sessionAuthenticateImpl = async () => ({})
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

/** Stable client identity — production `useStytch()` does not allocate a new object per render. */
const stytchClient = {
  session: {
    getTokens: () =>
      stytchTestState.session
        ? { session_jwt: stytchTestState.sessionJwt }
        : null,
    // AST-1374 activity extend loop
    getSync: () => stytchTestState.session,
    authenticate: (opts: { session_duration_minutes: number }) =>
      stytchTestState.sessionAuthenticateImpl(opts),
  },
  parseAuthenticateUrl: () => stytchTestState.parseAuthenticateUrlResult,
  authenticateByUrl: (opts: { session_duration_minutes: number }) =>
    stytchTestState.authenticateByUrlImpl(opts),
}

export function useStytch() {
  return stytchClient
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
