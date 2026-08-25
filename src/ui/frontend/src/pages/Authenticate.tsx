import { useEffect, useRef, useState } from "react"
import { Link, useNavigate, type NavigateFunction } from "react-router-dom"
import { useStytch, useStytchSession } from "@stytch/react"
import { useAuth } from "../contexts/AuthContext"
import { consumeAuthReturnPath } from "../lib/sessionAuthMark"
import { completeAuthenticateFromUrl } from "../lib/stytchAuthenticateHandoff"

type Phase = "loading" | "handoff" | "error"

function postAuthNavigate(navigate: NavigateFunction): void {
  const returnPath = consumeAuthReturnPath()
  navigate(returnPath ?? "/", { replace: true })
}

export default function Authenticate() {
  const stytch = useStytch()
  const { session, isInitialized } = useStytchSession()
  const { localAuthPassthrough } = useAuth()
  const navigate = useNavigate()
  const handoffStarted = useRef(false)
  const [phase, setPhase] = useState<Phase>("loading")
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    if (localAuthPassthrough === null) {
      return
    }
    if (localAuthPassthrough) {
      navigate("/", { replace: true })
      return
    }
    if (!isInitialized) {
      return
    }
    if (session) {
      postAuthNavigate(navigate)
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
        postAuthNavigate(navigate)
        return
      }
      window.history.replaceState({}, document.title, window.location.pathname)
      setErrorMessage(result.message ?? "Sign-in could not be completed.")
      setPhase("error")
    })()
  }, [localAuthPassthrough, stytch, session, isInitialized, navigate])

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
