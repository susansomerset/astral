import type { ReactNode } from "react"

/** Shared Stytch session state for Vitest — reset in beforeEach as needed. */
export const stytchTestState = {
  session: {} as object | null,
  isInitialized: true,
  sessionJwt: "test-session-jwt",
}

export function resetStytchTestState(): void {
  stytchTestState.session = {}
  stytchTestState.isInitialized = true
  stytchTestState.sessionJwt = "test-session-jwt"
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
