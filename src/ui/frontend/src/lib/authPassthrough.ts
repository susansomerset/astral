export interface AuthPassthrough {
  local_auth_passthrough: boolean
}

/** Public non-secret local-auth signal (AST-1440). Raw fetch — not api() — so the pre-login gate is free of Bearer/401 log-off coupling. Fail closed: only boolean true counts. */
export async function fetchAuthPassthrough(): Promise<boolean> {
  try {
    const r = await fetch("/api/auth_passthrough", { credentials: "include" })
    if (!r.ok) return false
    const data = (await r.json()) as Partial<AuthPassthrough>
    return data.local_auth_passthrough === true
  } catch {
    return false
  }
}
