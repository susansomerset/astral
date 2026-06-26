import type { ReactNode } from "react"
import { useStytchSession } from "@stytch/react"
import {
  getHadSession,
  getLogOffReason,
  setLogOffReason,
} from "../lib/sessionAuthMark"
import Login from "../pages/Login"
import LogOffScreen from "../pages/LogOffScreen"

export default function RequireAuth({ children }: { children: ReactNode }) {
  const { session, isInitialized } = useStytchSession()

  if (!isInitialized) {
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
