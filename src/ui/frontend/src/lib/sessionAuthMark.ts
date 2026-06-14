const HAD_SESSION_KEY = "astral-had-stytch-session"
const LOGOFF_REASON_KEY = "astral-logoff-reason"

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

/** Clears both keys — call before Refresh reload so Login appears after reload. */
export function clearSessionAuthMarks(): void {
  try {
    sessionStorage.removeItem(HAD_SESSION_KEY)
    sessionStorage.removeItem(LOGOFF_REASON_KEY)
  } catch { /* private mode */ }
}
