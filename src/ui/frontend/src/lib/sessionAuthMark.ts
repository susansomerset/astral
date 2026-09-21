const HAD_SESSION_KEY = "astral-had-stytch-session"
const LOGOFF_REASON_KEY = "astral-logoff-reason"
const AUTH_RETURN_PATH_KEY = "astral-auth-return-path"

export type LogOffReason = "timeout" | "server-rejection"

export function markHadSession(): void {
  try { sessionStorage.setItem(HAD_SESSION_KEY, "1") } catch { /* private mode */ }
}

export function getHadSession(): boolean {
  try { return sessionStorage.getItem(HAD_SESSION_KEY) === "1" } catch { return false }
}

export function getLogOffReason(): LogOffReason | null {
  try {
    const v = sessionStorage.getItem(LOGOFF_REASON_KEY)
    return v === "timeout" || v === "server-rejection" ? v : null
  } catch { return null }
}

export function setLogOffReason(reason: LogOffReason): void {
  try { sessionStorage.setItem(LOGOFF_REASON_KEY, reason) } catch { /* private mode */ }
}

/** Clears had-session + log-off keys — not auth return path (LogOff Refresh → Login re-capture). */
export function clearSessionAuthMarks(): void {
  try {
    sessionStorage.removeItem(HAD_SESSION_KEY)
    sessionStorage.removeItem(LOGOFF_REASON_KEY)
  } catch { /* private mode */ }
}

export function isSafeAuthReturnPath(path: string): boolean {
  const trimmed = path.trim()
  if (!trimmed) return false
  if (!trimmed.startsWith("/") || trimmed.startsWith("//")) return false
  if (
    trimmed === "/authenticate"
    || trimmed.startsWith("/authenticate?")
    || trimmed.startsWith("/authenticate/")
  ) {
    return false
  }
  return true
}

export function captureAuthReturnPath(pathname: string, search: string): void {
  const path = `${pathname}${search}`
  if (!isSafeAuthReturnPath(path)) return
  try { sessionStorage.setItem(AUTH_RETURN_PATH_KEY, path) } catch { /* private mode */ }
}

export function peekAuthReturnPath(): string | null {
  try {
    const v = sessionStorage.getItem(AUTH_RETURN_PATH_KEY)
    return v && isSafeAuthReturnPath(v) ? v : null
  } catch { return null }
}

export function consumeAuthReturnPath(): string | null {
  try {
    const v = sessionStorage.getItem(AUTH_RETURN_PATH_KEY)
    sessionStorage.removeItem(AUTH_RETURN_PATH_KEY)
    return v && isSafeAuthReturnPath(v) ? v : null
  } catch { return null }
}
