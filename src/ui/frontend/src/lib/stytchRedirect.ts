/** Canonical Stytch login/signup/OAuth redirect (AST-613). Must match Stytch Dashboard allowlist exactly. */
export function getStytchAuthenticateRedirectUrl(): string {
  const fromEnv = import.meta.env.VITE_STYTCH_REDIRECT_URL?.trim()
  if (fromEnv) {
    return fromEnv.replace(/\/$/, "")
  }
  const origin = window.location.origin.replace(/\/$/, "")
  return `${origin}/authenticate`
}
