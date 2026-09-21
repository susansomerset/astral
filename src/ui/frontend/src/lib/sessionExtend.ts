export interface StytchSessionExtendClient {
  session: {
    getSync: () => unknown
    authenticate: (opts: {
      session_duration_minutes: number
    }) => Promise<unknown>
  }
}

const ACTIVITY_EVENTS = ["pointerdown", "keydown"] as const

/** Activity-driven extend, throttled to intervalMs. First qualifying event fires immediately. */
export function startSessionExtendLoop(
  stytch: StytchSessionExtendClient,
  opts: {
    session_duration_minutes: number
    activity_extension_interval_minutes: number
  },
): () => void {
  const intervalMs = opts.activity_extension_interval_minutes * 60_000
  let lastExtendAt = 0
  const onActivity = () => {
    if (!stytch.session.getSync()) return
    const now = Date.now()
    if (lastExtendAt !== 0 && now - lastExtendAt < intervalMs) return
    lastExtendAt = now
    void stytch.session
      .authenticate({
        session_duration_minutes: opts.session_duration_minutes,
      })
      .catch(() => {
        /* leave session as-is; natural expiry → existing log-off path */
      })
  }
  for (const type of ACTIVITY_EVENTS) {
    window.addEventListener(type, onActivity, true)
  }
  return () => {
    for (const type of ACTIVITY_EVENTS) {
      window.removeEventListener(type, onActivity, true)
    }
  }
}
