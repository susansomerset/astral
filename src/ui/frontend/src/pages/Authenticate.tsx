import { useEffect, useRef, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useStytch, useStytchSession } from "@stytch/react"
import { completeAuthenticateFromUrl } from "../lib/stytchAuthenticateHandoff"

type Phase = "loading" | "handoff" | "error"

export default function Authenticate() {
  const stytch = useStytch()
  const { session, isInitialized } = useStytchSession()
  const navigate = useNavigate()
  const handoffStarted = useRef(false)
  const [phase, setPhase] = useState<Phase>("loading")
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    if (!isInitialized) {
      return
    }
    if (session) {
      navigate("/", { replace: true })
      return
    }
    if (handoffStarted.current) {
      return
    }
    handoffStarted.current = true
    setPhase("handoff")

    void (async () => {
      const result = await completeAuthenticateFromUrl(stytch)
      if (result.outcome === "success" || result.outcome === "no-token") {
        navigate("/", { replace: true })
        return
      }
      window.history.replaceState({}, document.title, window.location.pathname)
      setErrorMessage(result.message ?? "Sign-in could not be completed.")
      setPhase("error")
    })()
  }, [stytch, session, isInitialized, navigate])

  if (phase === "error") {
    return (
      <div className="content" style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "2rem", gap: "1rem" }}>
        <p role="alert">{errorMessage}</p>
        <Link to="/">Try again</Link>
      </div>
    )
  }

  return <p>Completing sign-in…</p>
}
