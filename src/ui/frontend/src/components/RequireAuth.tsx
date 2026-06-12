import type { ReactNode } from "react"
import { useStytchSession } from "@stytch/react"
import Login from "../pages/Login"

export default function RequireAuth({ children }: { children: ReactNode }) {
  const { session, isInitialized } = useStytchSession()

  if (!isInitialized) {
    return <p>Loading…</p>
  }
  if (!session) {
    return <Login />
  }
  return children
}
