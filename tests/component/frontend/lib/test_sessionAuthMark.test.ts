import { beforeEach, describe, expect, it } from "vitest"
import {
  clearSessionAuthMarks,
  getHadSession,
  getLogOffReason,
  markHadSession,
  setLogOffReason,
} from "../../../../src/ui/frontend/src/lib/sessionAuthMark"

describe("sessionAuthMark", () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it("marks and reads had-session", () => {
    expect(getHadSession()).toBe(false)
    markHadSession()
    expect(getHadSession()).toBe(true)
  })

  it("stores and reads log-off reasons", () => {
    setLogOffReason("timeout")
    expect(getLogOffReason()).toBe("timeout")
    setLogOffReason("server-rejection")
    expect(getLogOffReason()).toBe("server-rejection")
  })

  it("returns null for invalid stored reason", () => {
    sessionStorage.setItem("astral-logoff-reason", "unknown")
    expect(getLogOffReason()).toBeNull()
  })

  it("clears both keys", () => {
    markHadSession()
    setLogOffReason("timeout")
    clearSessionAuthMarks()
    expect(getHadSession()).toBe(false)
    expect(getLogOffReason()).toBeNull()
  })
})
