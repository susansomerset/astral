import {
  createContext,
  useCallback,
  useContext,
  useEffect,
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

function sessionJwt(stytch: ReturnType<typeof useStytch>): string | null {
  return stytch.session.getTokens()?.session_jwt ?? null
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const stytch = useStytch()
  const { session } = useStytchSession()
  const [user, setUser] = useState<MeUser | null>(null)
  const [loading, setLoading] = useState(true)

  const loadMe = useCallback(async (jwt: string) => {
    setAuthTokenGetter(() => jwt)
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
      setAuthTokenGetter(() => null)
      setUser(null)
      setLoading(false)
      return
    }
    const jwt = sessionJwt(stytch)
    if (!jwt) {
      setAuthTokenGetter(() => null)
      setUser(null)
      setLoading(false)
      return
    }
    loadMe(jwt)
  }, [session, stytch, loadMe])

  const refreshMe = useCallback(() => {
    const jwt = sessionJwt(stytch)
    if (jwt) loadMe(jwt)
  }, [stytch, loadMe])

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
