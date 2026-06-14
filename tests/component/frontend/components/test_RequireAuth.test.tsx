import { screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it } from "vitest"
import RequireAuth from "../../../../src/ui/frontend/src/components/RequireAuth"
import {
  markHadSession,
  setLogOffReason,
} from "../../../../src/ui/frontend/src/lib/sessionAuthMark"
import { renderWithProviders } from "../test-utils"
import { resetStytchTestState, stytchTestState } from "../stytchMock"

describe("RequireAuth", () => {
  beforeEach(() => {
    resetStytchTestState()
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
})
