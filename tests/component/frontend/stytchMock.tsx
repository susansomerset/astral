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

export function StytchLogin() {
  return <div data-testid="stytch-login">Stytch Login</div>
}
