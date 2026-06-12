import { render, screen } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import Login from "../../../../src/ui/frontend/src/pages/Login"
import { lastStytchLoginConfig, resetStytchTestState } from "../stytchMock"

describe("Login", () => {
  beforeEach(() => {
    resetStytchTestState()
    vi.stubGlobal("window", { location: { origin: "http://localhost:5173" } })
  })

  afterEach(() => {
    vi.unstubAllEnvs()
  })

  it("renders StytchLogin with canonical redirect URLs from env", () => {
    vi.stubEnv("VITE_STYTCH_REDIRECT_URL", "https://railway.example/authenticate")
    render(<Login />)
    expect(screen.getByTestId("stytch-login")).toBeInTheDocument()
    expect(lastStytchLoginConfig).toMatchObject({
      emailMagicLinksOptions: {
        loginRedirectURL: "https://railway.example/authenticate",
        signupRedirectURL: "https://railway.example/authenticate",
      },
      oauthOptions: {
        loginRedirectURL: "https://railway.example/authenticate",
        signupRedirectURL: "https://railway.example/authenticate",
      },
    })
  })

  it("uses origin/authenticate fallback when env unset", () => {
    vi.stubEnv("VITE_STYTCH_REDIRECT_URL", "")
    render(<Login />)
    expect(lastStytchLoginConfig).toMatchObject({
      emailMagicLinksOptions: {
        loginRedirectURL: "http://localhost:5173/authenticate",
      },
      oauthOptions: {
        loginRedirectURL: "http://localhost:5173/authenticate",
      },
    })
  })
})
