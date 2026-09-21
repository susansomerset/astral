import { beforeEach, describe, expect, it } from "vitest"
import {
  captureAuthReturnPath,
  clearSessionAuthMarks,
  consumeAuthReturnPath,
  getHadSession,
  getLogOffReason,
  isSafeAuthReturnPath,
  markHadSession,
  peekAuthReturnPath,
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

describe("sessionAuthMark — AST-1482 auth return path", () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it("isSafeAuthReturnPath accepts in-app paths and rejects unsafe values", () => {
    expect(isSafeAuthReturnPath("/jobs/detail/j-abc")).toBe(true)
    expect(isSafeAuthReturnPath("/jobs/recommended?foo=1")).toBe(true)
    expect(isSafeAuthReturnPath("")).toBe(false)
    expect(isSafeAuthReturnPath("   ")).toBe(false)
    expect(isSafeAuthReturnPath("//evil.example/path")).toBe(false)
    expect(isSafeAuthReturnPath("/authenticate")).toBe(false)
    expect(isSafeAuthReturnPath("/authenticate?token=x")).toBe(false)
    expect(isSafeAuthReturnPath("/authenticate/extra")).toBe(false)
  })

  it("capture, peek, and consume round-trip a safe path", () => {
    captureAuthReturnPath("/jobs/detail/j-deeplink", "")
    expect(peekAuthReturnPath()).toBe("/jobs/detail/j-deeplink")
    expect(consumeAuthReturnPath()).toBe("/jobs/detail/j-deeplink")
    expect(peekAuthReturnPath()).toBeNull()
  })

  it("does not store unsafe paths", () => {
    captureAuthReturnPath("/authenticate", "")
    expect(peekAuthReturnPath()).toBeNull()
  })

  it("consume removes unsafe stored paths and returns null", () => {
    sessionStorage.setItem("astral-auth-return-path", "/authenticate")
    expect(consumeAuthReturnPath()).toBeNull()
    expect(sessionStorage.getItem("astral-auth-return-path")).toBeNull()
  })

  it("clearSessionAuthMarks leaves auth return path intact", () => {
    captureAuthReturnPath("/jobs/detail/j-keep", "")
    markHadSession()
    setLogOffReason("timeout")
    clearSessionAuthMarks()
    expect(peekAuthReturnPath()).toBe("/jobs/detail/j-keep")
    expect(getHadSession()).toBe(false)
  })
})
