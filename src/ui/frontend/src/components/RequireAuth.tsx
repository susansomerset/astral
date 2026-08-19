import type { ReactNode } from "react"
import { useStytchSession } from "@stytch/react"
import { useAuth } from "../contexts/AuthContext"
import {
  getHadSession,
  getLogOffReason,
  setLogOffReason,
} from "../lib/sessionAuthMark"
import Login from "../pages/Login"
import LogOffScreen from "../pages/LogOffScreen"

export default function RequireAuth({ children }: { children: ReactNode }) {
  const { session, isInitialized } = useStytchSession()
  const { localAuthPassthrough } = useAuth()

  if (localAuthPassthrough === null) {
    return <p>Loading…</p>
  }
  if (localAuthPassthrough) {
    return children
  }

  if (!isInitialized && !session) {
    return <p>Loading…</p>
  }

  let logOffReason = getLogOffReason()
  if (!logOffReason && !session && getHadSession()) {
    setLogOffReason("timeout")
    logOffReason = "timeout"
  }
  if (logOffReason) {
    return <LogOffScreen reason={logOffReason} />
  }
  if (!session) {
    return <Login />
  }
  return children
}
