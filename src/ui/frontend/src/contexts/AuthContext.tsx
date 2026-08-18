import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type ReactNode,
} from "react"
import { useStytch, useStytchSession } from "@stytch/react"
import api, { setAuthTokenGetter, setUnauthorizedHandler } from "../lib/api"
import { fetchAuthSessionPolicy } from "../lib/authSessionPolicy"
import { startSessionExtendLoop } from "../lib/sessionExtend"
import { markHadSession, setLogOffReason } from "../lib/sessionAuthMark"

export interface MeUser {
  user_id: string
  name: string
  is_admin: boolean
}

interface AuthCtx {
  user: MeUser | null
  isAdmin: boolean
  loading: boolean
  refreshMe: () => void
}

const AuthContext = createContext<AuthCtx>({
  user: null,
  isAdmin: false,
  loading: true,
  refreshMe: () => {},
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const stytch = useStytch()
  const { session } = useStytchSession()
  const [user, setUser] = useState<MeUser | null>(null)
  const [loading, setLoading] = useState(true)
  const [, setAuthEpoch] = useState(0)
  const identityResolvedRef = useRef(false)
  const sessionPresent = Boolean(session)

  // Stable string dep — Stytch hook objects may change identity every render.
  const sessionJwt =
    session ? stytch.session.getTokens()?.session_jwt ?? null : null

  // Child useEffects run before parent useEffect — wire the token in layout phase.
  useLayoutEffect(() => {
    setAuthTokenGetter(() => sessionJwt)
  }, [sessionJwt])

  useEffect(() => {
    setUnauthorizedHandler(() => setAuthEpoch((n) => n + 1))
    return () => setUnauthorizedHandler(null)
  }, [])

  const loadMe = useCallback(async () => {
    if (!identityResolvedRef.current) {
      setLoading(true)
    }
    try {
      const r = await api("/api/me")
      if (!r.ok) {
        if (r.status === 401) {
          setLogOffReason("server-rejection")
          setAuthEpoch((n) => n + 1)
        }
        setUser(null)
        return
      }
      const data = await r.json() as MeUser
      setUser(data)
    } catch {
      setUser(null)
    } finally {
      identityResolvedRef.current = true
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!sessionPresent) {
      identityResolvedRef.current = false
      setUser(null)
      setLoading(false)
      return
    }
    markHadSession()
    loadMe()
  }, [sessionPresent, sessionJwt, loadMe])

  // Config-backed Stytch session extend while a client session exists (AST-1374).
  useEffect(() => {
    if (!sessionPresent) return
    let cancelled = false
    let clear: (() => void) | undefined
    void (async () => {
      try {
        const policy = await fetchAuthSessionPolicy()
        if (cancelled) return
        clear = startSessionExtendLoop(stytch, policy)
        // Unmount may have won the race between await and assign.
        if (cancelled) {
          clear()
          clear = undefined
        }
      } catch {
        /* no loop if policy unavailable; session still expires on create-time duration */
      }
    })()
    return () => {
      cancelled = true
      clear?.()
    }
  }, [sessionPresent, stytch])

  const refreshMe = useCallback(() => {
    if (session) loadMe()
  }, [session, loadMe])

  return (
    <AuthContext.Provider
      value={{
        user,
        isAdmin: Boolean(user?.is_admin),
        loading,
        refreshMe,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthCtx {
  return useContext(AuthContext)
}
