import { fireEvent, render, screen } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import LogOffScreen from "../../../../src/ui/frontend/src/pages/LogOffScreen"
import {
  clearSessionAuthMarks,
  getHadSession,
  getLogOffReason,
  markHadSession,
  setLogOffReason,
} from "../../../../src/ui/frontend/src/lib/sessionAuthMark"

describe("LogOffScreen", () => {
  const reload = vi.fn()

  beforeEach(() => {
    sessionStorage.clear()
    reload.mockReset()
    vi.stubGlobal("location", { reload })
  })

  it("renders timeout copy", () => {
    render(<LogOffScreen reason="timeout" />)
    expect(screen.getByTestId("logoff-screen")).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: "You were signed out" })).toBeInTheDocument()
    expect(screen.getByText(/session expired after a period of inactivity/i)).toBeInTheDocument()
    expect(screen.queryByTestId("stytch-login")).not.toBeInTheDocument()
  })

  it("renders server-rejection copy", () => {
    render(<LogOffScreen reason="server-rejection" />)
    expect(screen.getByRole("heading", { name: "Your session is no longer valid" })).toBeInTheDocument()
    expect(screen.getByText(/server rejected your request/i)).toBeInTheDocument()
  })

  it("Refresh clears session marks and reloads the page", () => {
    markHadSession()
    setLogOffReason("server-rejection")
    render(<LogOffScreen reason="server-rejection" />)
    fireEvent.click(screen.getByTestId("logoff-refresh"))
    expect(getHadSession()).toBe(false)
    expect(getLogOffReason()).toBeNull()
    expect(reload).toHaveBeenCalledOnce()
  })
})
