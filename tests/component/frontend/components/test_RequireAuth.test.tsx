import { screen, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import RequireAuth from "../../../../src/ui/frontend/src/components/RequireAuth"
import {
  markHadSession,
  peekAuthReturnPath,
  setLogOffReason,
} from "../../../../src/ui/frontend/src/lib/sessionAuthMark"
import { renderWithProviders, stubAuthPublicFetches } from "../test-utils"
import { resetStytchTestState, stytchTestState } from "../stytchMock"

describe("RequireAuth", () => {
  beforeEach(() => {
    resetStytchTestState()
    stubAuthPublicFetches(false)
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("shows Login when there is no Stytch session", async () => {
    stytchTestState.session = null
    renderWithProviders(
      <RequireAuth>
        <p>Protected content</p>
      </RequireAuth>,
    )
    await waitFor(() => expect(screen.getByTestId("stytch-login")).toBeInTheDocument())
    expect(screen.queryByText("Protected content")).not.toBeInTheDocument()
  })

  it("renders children when a Stytch session exists", async () => {
    renderWithProviders(
      <RequireAuth>
        <p>Protected content</p>
      </RequireAuth>,
    )
    await waitFor(() => expect(screen.getByText("Protected content")).toBeInTheDocument())
    expect(screen.queryByTestId("stytch-login")).not.toBeInTheDocument()
  })

  it("shows LogOffScreen with timeout copy after session loss when user had authenticated", async () => {
    markHadSession()
    stytchTestState.session = null
    renderWithProviders(
      <RequireAuth>
        <p>Protected content</p>
      </RequireAuth>,
    )
    await waitFor(() => expect(screen.getByTestId("logoff-screen")).toBeInTheDocument())
    expect(screen.getByRole("heading", { name: "You were signed out" })).toBeInTheDocument()
    expect(screen.queryByTestId("stytch-login")).not.toBeInTheDocument()
    expect(screen.queryByText("Protected content")).not.toBeInTheDocument()
  })

  it("AST-1408: shows Loading when Stytch is uninitialized and there is no session", () => {
    stytchTestState.isInitialized = false
    stytchTestState.session = null
    renderWithProviders(
      <RequireAuth>
        <p>Protected content</p>
      </RequireAuth>,
    )
    expect(screen.getByText("Loading…")).toBeInTheDocument()
    expect(screen.queryByText("Protected content")).not.toBeInTheDocument()
  })

  it("AST-1408: keeps children mounted when a session exists even if Stytch is uninitialized", async () => {
    stytchTestState.isInitialized = false
    renderWithProviders(
      <RequireAuth>
        <p>Protected content</p>
      </RequireAuth>,
    )
    await waitFor(() => expect(screen.getByText("Protected content")).toBeInTheDocument())
    expect(screen.queryByText("Loading…")).not.toBeInTheDocument()
  })

  it("shows LogOffScreen with server-rejection copy when reason is set", async () => {
    markHadSession()
    setLogOffReason("server-rejection")
    stytchTestState.session = {}
    renderWithProviders(
      <RequireAuth>
        <p>Protected content</p>
      </RequireAuth>,
    )
    await waitFor(() => expect(screen.getByTestId("logoff-screen")).toBeInTheDocument())
    expect(screen.getByRole("heading", { name: "Your session is no longer valid" })).toBeInTheDocument()
    expect(screen.queryByText("Protected content")).not.toBeInTheDocument()
  })

  it("AST-1441: renders children with no session when passthrough is on", async () => {
    stubAuthPublicFetches(true)
    stytchTestState.session = null
    renderWithProviders(
      <RequireAuth>
        <p>Protected content</p>
      </RequireAuth>,
    )
    await waitFor(() => expect(screen.getByText("Protected content")).toBeInTheDocument())
    expect(screen.queryByTestId("stytch-login")).not.toBeInTheDocument()
    expect(screen.queryByTestId("logoff-screen")).not.toBeInTheDocument()
  })

  it("AST-1441: leftover log-off mark does not mount LogOffScreen when passthrough is on", async () => {
    stubAuthPublicFetches(true)
    markHadSession()
    setLogOffReason("timeout")
    stytchTestState.session = null
    renderWithProviders(
      <RequireAuth>
        <p>Protected content</p>
      </RequireAuth>,
    )
    await waitFor(() => expect(screen.getByText("Protected content")).toBeInTheDocument())
    expect(screen.queryByTestId("logoff-screen")).not.toBeInTheDocument()
    expect(screen.queryByTestId("stytch-login")).not.toBeInTheDocument()
  })

  it("AST-1482: captures deeplink path when Login gate blocks unauthenticated visit", async () => {
    stytchTestState.session = null
    renderWithProviders(
      <RequireAuth>
        <p>Protected content</p>
      </RequireAuth>,
      { router: { initialEntries: ["/jobs/detail/j-deeplink"] } },
    )
    await waitFor(() => expect(screen.getByTestId("stytch-login")).toBeInTheDocument())
    expect(peekAuthReturnPath()).toBe("/jobs/detail/j-deeplink")
  })

  it("AST-1482: captures path on LogOffScreen after session timeout", async () => {
    markHadSession()
    stytchTestState.session = null
    renderWithProviders(
      <RequireAuth>
        <p>Protected content</p>
      </RequireAuth>,
      { router: { initialEntries: ["/jobs/detail/j-timeout"] } },
    )
    await waitFor(() => expect(screen.getByTestId("logoff-screen")).toBeInTheDocument())
    expect(peekAuthReturnPath()).toBe("/jobs/detail/j-timeout")
  })

  it("AST-1482: does not capture while Stytch bootstrap Loading", () => {
    stytchTestState.isInitialized = false
    stytchTestState.session = null
    renderWithProviders(
      <RequireAuth>
        <p>Protected content</p>
      </RequireAuth>,
      { router: { initialEntries: ["/jobs/detail/j-loading"] } },
    )
    expect(screen.getByText("Loading…")).toBeInTheDocument()
    expect(peekAuthReturnPath()).toBeNull()
  })

  it("AST-1482: does not capture when authenticated children render", async () => {
    renderWithProviders(
      <RequireAuth>
        <p>Protected content</p>
      </RequireAuth>,
      { router: { initialEntries: ["/jobs/detail/j-authed"] } },
    )
    await waitFor(() => expect(screen.getByText("Protected content")).toBeInTheDocument())
    expect(peekAuthReturnPath()).toBeNull()
  })

  it("AST-1482: does not capture when local auth passthrough is on", async () => {
    stubAuthPublicFetches(true)
    stytchTestState.session = null
    renderWithProviders(
      <RequireAuth>
        <p>Protected content</p>
      </RequireAuth>,
      { router: { initialEntries: ["/jobs/detail/j-passthrough"] } },
    )
    await waitFor(() => expect(screen.getByText("Protected content")).toBeInTheDocument())
    expect(peekAuthReturnPath()).toBeNull()
  })
})
