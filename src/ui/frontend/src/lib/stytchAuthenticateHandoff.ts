/** Outcomes from /authenticate URL token exchange (AST-830). */
export type AuthenticateHandoffOutcome =
  | "success"
  | "no-token"
  | "unsupported-token"
  | "error"

export interface AuthenticateHandoffResult {
  outcome: AuthenticateHandoffOutcome
  /** Stytch token type when parseAuthenticateUrl found a token (oauth | magic_links | …). */
  tokenType?: string
  /** Human-readable message for error / unsupported-token UI. */
  message?: string
}

/** Minimal Stytch client surface used by Authenticate.tsx — matches @stytch/react useStytch(). */
export interface StytchAuthenticateClient {
  parseAuthenticateUrl?: () => {
    token: string
    tokenType: string
    handled: boolean
  } | null
  authenticateByUrl: (opts: {
    session_duration_minutes: number
  }) => Promise<{
    handled: boolean
    tokenType?: string
    token?: string
  } | null>
}

const SESSION_DURATION_MINUTES = 60

/**
 * Exchange OAuth / magic-link token from current URL params for a Stytch client session.
 * Call once per /authenticate page load.
 */
export async function completeAuthenticateFromUrl(
  stytch: StytchAuthenticateClient,
): Promise<AuthenticateHandoffResult> {
  const parsed = stytch.parseAuthenticateUrl?.() ?? null
  if (!parsed) {
    return { outcome: "no-token" }
  }
  if (!parsed.handled) {
    return {
      outcome: "unsupported-token",
      tokenType: parsed.tokenType,
      message: `Sign-in link type "${parsed.tokenType}" is not supported here.`,
    }
  }
  try {
    const result = await stytch.authenticateByUrl({
      session_duration_minutes: SESSION_DURATION_MINUTES,
    })
    if (result?.handled) {
      return { outcome: "success", tokenType: result.tokenType ?? parsed.tokenType }
    }
    return {
      outcome: "error",
      tokenType: parsed.tokenType,
      message: "Sign-in could not be completed.",
    }
  } catch (err) {
    const msg =
      err instanceof Error ? err.message : "Sign-in could not be completed."
    return { outcome: "error", tokenType: parsed.tokenType, message: msg }
  }
}
