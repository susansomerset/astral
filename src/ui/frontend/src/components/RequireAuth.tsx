import { useEffect, type ReactNode } from "react"
import { useLocation } from "react-router-dom"
import { useStytchSession } from "@stytch/react"
import { useAuth } from "../contexts/AuthContext"
import {
  captureAuthReturnPath,
  getHadSession,
  getLogOffReason,
  setLogOffReason,
} from "../lib/sessionAuthMark"
import Login from "../pages/Login"
import LogOffScreen from "../pages/LogOffScreen"

export default function RequireAuth({ children }: { children: ReactNode }) {
  const { session, isInitialized } = useStytchSession()
  const { localAuthPassthrough } = useAuth()
  const location = useLocation()

  // Hoisted for capture effect — same timeout inference as render below.
  let logOffReason = getLogOffReason()
  if (!logOffReason && !session && getHadSession()) {
    setLogOffReason("timeout")
    logOffReason = "timeout"
  }

  useEffect(() => {
    if (localAuthPassthrough !== false) return
    if (!isInitialized && !session) return
    const blocked = Boolean(logOffReason) || !session
    if (!blocked) return
    captureAuthReturnPath(location.pathname, location.search)
  }, [
    localAuthPassthrough,
    session,
    isInitialized,
    logOffReason,
    location.pathname,
    location.search,
  ])

  if (localAuthPassthrough === null) {
    return <p>Loading…</p>
  }
  if (localAuthPassthrough) {
    return children
  }

  if (!isInitialized && !session) {
    return <p>Loading…</p>
  }

  if (logOffReason) {
    return <LogOffScreen reason={logOffReason} />
  }
  if (!session) {
    return <Login />
  }
  return children
}
