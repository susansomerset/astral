import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { startSessionExtendLoop } from "../../../../src/ui/frontend/src/lib/sessionExtend"

describe("startSessionExtendLoop (AST-1374)", () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it("does not fire immediately; authenticates on cadence while session exists", async () => {
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
    await vi.advanceTimersByTimeAsync(10 * 60_000)
    expect(authenticate).toHaveBeenCalledTimes(1)
    expect(authenticate).toHaveBeenCalledWith({ session_duration_minutes: 20 })

    clear()
    await vi.advanceTimersByTimeAsync(10 * 60_000)
    expect(authenticate).toHaveBeenCalledTimes(1)
  })

  it("skips authenticate when getSync is falsy", async () => {
    const authenticate = vi.fn(async () => ({}))
    startSessionExtendLoop(
      { session: { getSync: () => null, authenticate } },
      {
        session_duration_minutes: 20,
        activity_extension_interval_minutes: 10,
      },
    )
    await vi.advanceTimersByTimeAsync(10 * 60_000)
    expect(authenticate).not.toHaveBeenCalled()
  })

  it("swallows authenticate rejection without throwing", async () => {
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
    await vi.advanceTimersByTimeAsync(10 * 60_000)
    expect(authenticate).toHaveBeenCalledTimes(1)
  })
})
