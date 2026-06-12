import { useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useStytch, useStytchSession } from "@stytch/react"

export default function Authenticate() {
  const stytch = useStytch()
  const { session } = useStytchSession()
  const navigate = useNavigate()

  useEffect(() => {
    if (session) {
      navigate("/", { replace: true })
      return
    }
    stytch.authenticateByUrl({ session_duration_minutes: 60 })
  }, [stytch, session, navigate])

  return <p>Completing sign-in…</p>
}
