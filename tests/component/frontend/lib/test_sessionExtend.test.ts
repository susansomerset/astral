import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { startSessionExtendLoop } from "../../../../src/ui/frontend/src/lib/sessionExtend"

describe("startSessionExtendLoop (AST-1374)", () => {
  beforeEach(() => {
    vi.useFakeTimers({ toFake: ["Date"] })
    vi.setSystemTime(new Date("2026-09-19T17:00:00Z"))
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it("authenticates on first pointerdown; throttles until the policy interval", () => {
    const authenticate = vi.fn(async () => ({}))
    const getSync = vi.fn(() => ({ user_id: "u1" }))
    const clear = startSessionExtendLoop(
      { session: { getSync, authenticate } },
      {
        session_duration_minutes: 20,
        activity_extension_interval_minutes: 10,
      },
    )

    expect(authenticate).not.toHaveBeenCalled()
    window.dispatchEvent(new Event("pointerdown", { bubbles: true }))
    expect(authenticate).toHaveBeenCalledTimes(1)
    expect(authenticate).toHaveBeenCalledWith({ session_duration_minutes: 20 })

    window.dispatchEvent(new Event("pointerdown", { bubbles: true }))
    expect(authenticate).toHaveBeenCalledTimes(1)

    vi.setSystemTime(new Date("2026-09-19T17:10:00Z"))
    window.dispatchEvent(new Event("keydown", { bubbles: true }))
    expect(authenticate).toHaveBeenCalledTimes(2)

    clear()
    vi.setSystemTime(new Date("2026-09-19T17:20:00Z"))
    window.dispatchEvent(new Event("pointerdown", { bubbles: true }))
    expect(authenticate).toHaveBeenCalledTimes(2)
  })

  it("skips authenticate when getSync is falsy", () => {
    const authenticate = vi.fn(async () => ({}))
    startSessionExtendLoop(
      { session: { getSync: () => null, authenticate } },
      {
        session_duration_minutes: 20,
        activity_extension_interval_minutes: 10,
      },
    )
    window.dispatchEvent(new Event("pointerdown", { bubbles: true }))
    expect(authenticate).not.toHaveBeenCalled()
  })

  it("swallows authenticate rejection without throwing", () => {
    const authenticate = vi.fn(async () => {
      throw new Error("extend failed")
    })
    startSessionExtendLoop(
      { session: { getSync: () => ({}), authenticate } },
      {
        session_duration_minutes: 20,
        activity_extension_interval_minutes: 10,
      },
    )
    expect(() => {
      window.dispatchEvent(new Event("pointerdown", { bubbles: true }))
    }).not.toThrow()
    expect(authenticate).toHaveBeenCalledTimes(1)
  })
})
