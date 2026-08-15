export interface StytchSessionExtendClient {
  session: {
    getSync: () => unknown
    authenticate: (opts: {
      session_duration_minutes: number
    }) => Promise<unknown>
  }
}

/** Returns clear() for the interval. Does not fire immediately — first tick after intervalMs. */
export function startSessionExtendLoop(
  stytch: StytchSessionExtendClient,
  opts: {
    session_duration_minutes: number
    activity_extension_interval_minutes: number
  },
): () => void {
  const intervalMs = opts.activity_extension_interval_minutes * 60_000
  const tick = () => {
    if (!stytch.session.getSync()) return
    void stytch.session
      .authenticate({
        session_duration_minutes: opts.session_duration_minutes,
      })
      .catch(() => {
        /* leave session as-is; natural expiry → existing log-off path */
      })
  }
  const id = window.setInterval(tick, intervalMs)
  return () => window.clearInterval(id)
}
