export interface AuthSessionPolicy {
  session_duration_minutes: number
  activity_extension_interval_minutes: number
}

/** Public non-secret policy (AST-1373). Use raw fetch — not api() — so pre-login handoff stays free of Bearer/401 log-off coupling. */
export async function fetchAuthSessionPolicy(): Promise<AuthSessionPolicy> {
  const r = await fetch("/api/auth_session_policy", { credentials: "include" })
  if (!r.ok) {
    throw new Error(`Session policy unavailable (${r.status})`)
  }
  const data = (await r.json()) as Partial<AuthSessionPolicy>
  const session_duration_minutes = Number(data.session_duration_minutes)
  const activity_extension_interval_minutes = Number(
    data.activity_extension_interval_minutes,
  )
  if (
    !Number.isFinite(session_duration_minutes) ||
    session_duration_minutes <= 0 ||
    !Number.isFinite(activity_extension_interval_minutes) ||
    activity_extension_interval_minutes <= 0
  ) {
    throw new Error("Session policy response invalid")
  }
  return { session_duration_minutes, activity_extension_interval_minutes }
}
