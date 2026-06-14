import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useLayoutEffect,
  useState,
  type ReactNode,
} from "react"
import { useStytch, useStytchSession } from "@stytch/react"
import api, { setAuthTokenGetter } from "../lib/api"

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

  // Stable string dep — Stytch hook objects may change identity every render.
  const sessionJwt =
    session ? stytch.session.getTokens()?.session_jwt ?? null : null

  // Child useEffects run before parent useEffect — wire the token in layout phase.
  useLayoutEffect(() => {
    setAuthTokenGetter(() => sessionJwt)
  }, [sessionJwt])

  const loadMe = useCallback(async () => {
    setLoading(true)
    try {
      const r = await api("/api/me")
      if (!r.ok) {
        setUser(null)
        return
      }
      const data = await r.json() as MeUser
      setUser(data)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!session) {
      setUser(null)
      setLoading(false)
      return
    }
    // sessionJwt may be null when Stytch uses opaque cookies — /api/me uses cookie auth.
    loadMe()
  }, [session, sessionJwt, loadMe])

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
