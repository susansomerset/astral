import { render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, afterEach, describe, expect, it, vi } from "vitest"
import Authenticate from "../../../../src/ui/frontend/src/pages/Authenticate"
import { AuthProvider } from "../../../../src/ui/frontend/src/contexts/AuthContext"
import { captureAuthReturnPath } from "../../../../src/ui/frontend/src/lib/sessionAuthMark"
import { resetStytchTestState, stytchTestState } from "../stytchMock"
import { stubAuthPublicFetches } from "../test-utils"

const navigate = vi.fn()

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom")
  return {
    ...actual,
    useNavigate: () => navigate,
  }
})

function renderAuthenticate() {
  return render(
    <MemoryRouter initialEntries={["/authenticate?stytch_token_type=oauth&token=abc"]}>
      <AuthProvider>
        <Authenticate />
      </AuthProvider>
    </MemoryRouter>,
  )
}

describe("Authenticate page (AST-830 / AST-1374 / AST-1441)", () => {
  let replaceState: ReturnType<typeof vi.fn>

  beforeEach(() => {
    resetStytchTestState()
    navigate.mockReset()
    replaceState = vi.fn()
    vi.spyOn(window.history, "replaceState").mockImplementation(replaceState)
    stubAuthPublicFetches(false)
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it("shows Completing sign-in while Stytch session is not initialized", () => {
    stytchTestState.isInitialized = false
    renderAuthenticate()
    expect(screen.getByText("Completing sign-in…")).toBeInTheDocument()
    expect(navigate).not.toHaveBeenCalled()
  })

  it("navigates home when a Stytch session already exists", async () => {
    stytchTestState.session = { user_id: "u1" }
    renderAuthenticate()
    await waitFor(() =>
      expect(navigate).toHaveBeenCalledWith("/", { replace: true }),
    )
  })

  it("navigates home after successful OAuth handoff", async () => {
    stytchTestState.session = null
    stytchTestState.parseAuthenticateUrlResult = {
      token: "abc",
      tokenType: "oauth",
      handled: true,
    }
    stytchTestState.authenticateByUrlImpl = async () => ({
      handled: true,
      tokenType: "oauth",
    })
    renderAuthenticate()
    await waitFor(() =>
      expect(navigate).toHaveBeenCalledWith("/", { replace: true }),
    )
  })

  it("navigates home when URL has no authenticate token", async () => {
    stytchTestState.session = null
    stytchTestState.parseAuthenticateUrlResult = null
    renderAuthenticate()
    await waitFor(() =>
      expect(navigate).toHaveBeenCalledWith("/", { replace: true }),
    )
  })

  it("shows in-app error with Try again when handoff fails", async () => {
    stytchTestState.session = null
    stytchTestState.parseAuthenticateUrlResult = {
      token: "abc",
      tokenType: "oauth",
      handled: true,
    }
    stytchTestState.authenticateByUrlImpl = async () => {
      throw new Error("OAuth token already consumed")
    }
    renderAuthenticate()
    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent("OAuth token already consumed"),
    )
    expect(screen.getByRole("link", { name: "Try again" })).toHaveAttribute("href", "/")
    expect(window.history.replaceState).toHaveBeenCalledWith(
      {},
      document.title,
      window.location.pathname,
    )
  })

  it("runs authenticateByUrl at most once per mount (single-flight guard)", async () => {
    stytchTestState.session = null
    stytchTestState.parseAuthenticateUrlResult = {
      token: "abc",
      tokenType: "oauth",
      handled: true,
    }
    const authenticateByUrl = vi.fn(async () => ({ handled: true, tokenType: "oauth" }))
    stytchTestState.authenticateByUrlImpl = authenticateByUrl
    renderAuthenticate()
    await waitFor(() => expect(navigate).toHaveBeenCalled())
    expect(authenticateByUrl).toHaveBeenCalledTimes(1)
    expect(authenticateByUrl).toHaveBeenCalledWith({ session_duration_minutes: 20 })
  })

  it("AST-1441: navigates home without authenticateByUrl when passthrough is on", async () => {
    stubAuthPublicFetches(true)
    stytchTestState.session = null
    const authenticateByUrl = vi.fn(async () => ({ handled: true, tokenType: "oauth" }))
    stytchTestState.authenticateByUrlImpl = authenticateByUrl
    stytchTestState.parseAuthenticateUrlResult = {
      token: "abc",
      tokenType: "oauth",
      handled: true,
    }
    renderAuthenticate()
    await waitFor(() =>
      expect(navigate).toHaveBeenCalledWith("/", { replace: true }),
    )
    expect(authenticateByUrl).not.toHaveBeenCalled()
  })

  it("AST-1482: navigates to stored return path when session already exists", async () => {
    captureAuthReturnPath("/jobs/detail/j-return", "")
    stytchTestState.session = { user_id: "u1" }
    renderAuthenticate()
    await waitFor(() =>
      expect(navigate).toHaveBeenCalledWith("/jobs/detail/j-return", { replace: true }),
    )
  })

  it("AST-1482: navigates to stored return path after successful OAuth handoff", async () => {
    captureAuthReturnPath("/jobs/detail/j-oauth", "")
    stytchTestState.session = null
    stytchTestState.parseAuthenticateUrlResult = {
      token: "abc",
      tokenType: "oauth",
      handled: true,
    }
    stytchTestState.authenticateByUrlImpl = async () => ({
      handled: true,
      tokenType: "oauth",
    })
    renderAuthenticate()
    await waitFor(() =>
      expect(navigate).toHaveBeenCalledWith("/jobs/detail/j-oauth", { replace: true }),
    )
  })

  it("AST-1482: navigates to stored return path when URL has no authenticate token", async () => {
    captureAuthReturnPath("/jobs/detail/j-notoken", "")
    stytchTestState.session = null
    stytchTestState.parseAuthenticateUrlResult = null
    renderAuthenticate()
    await waitFor(() =>
      expect(navigate).toHaveBeenCalledWith("/jobs/detail/j-notoken", { replace: true }),
    )
  })
})
