import { beforeEach, describe, expect, it, vi } from "vitest"
import {
  createTabBudget,
  fetchPacingConfig,
  getPacingConfig,
  setPacingConfig,
  type SurferPacingConfig,
} from "../../../../src/ui/extension/src/lib/pacingConfig"
import { dwell } from "../../../../src/ui/extension/src/lib/dwell"

const DEFAULT: SurferPacingConfig = {
  dwell_center_seconds: 10,
  dwell_spread_seconds: 5,
  max_tabs: 1,
  mv3_idle_ceiling_seconds: 30,
}

describe("Surfer pacing — AST-1236", () => {
  beforeEach(() => {
    setPacingConfig(DEFAULT)
  })

  it("fetchPacingConfig caches via injected getJson", async () => {
    const getJson = vi.fn(async (path: string) => {
      expect(path).toBe("/api/surfer/pacing_config")
      return {
        dwell_center_seconds: 8,
        dwell_spread_seconds: 2,
        max_tabs: 1,
        mv3_idle_ceiling_seconds: 30,
      }
    })
    const cfg = await fetchPacingConfig(getJson)
    expect(cfg.dwell_center_seconds).toBe(8)
    expect(getPacingConfig().dwell_spread_seconds).toBe(2)
    expect(getJson).toHaveBeenCalledOnce()
  })

  it("dwell sleeps inside centre±spread and returns chosen seconds", async () => {
    vi.useFakeTimers()
    vi.spyOn(Math, "random").mockReturnValue(0) // floor = 5
    const pending = dwell()
    await vi.runAllTimersAsync()
    const seconds = await pending
    expect(seconds).toBe(5)
    vi.spyOn(Math, "random").mockReturnValue(1 - Number.EPSILON) // near hi = 15
    const pendingHi = dwell()
    await vi.runAllTimersAsync()
    const hi = await pendingHi
    expect(hi).toBeGreaterThan(14.9)
    expect(hi).toBeLessThanOrEqual(15)
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it("dwell rejects bounds that meet or exceed mv3 ceiling", async () => {
    await expect(
      dwell({ centerSeconds: 20, spreadSeconds: 10 }),
    ).rejects.toThrow(/mv3_idle_ceiling_seconds/)
  })

  it("createTabBudget(1) never exceeds one in flight (slot transfer)", async () => {
    const budget = createTabBudget(1)
    await budget.acquire()
    expect(budget.inFlight()).toBe(1)

    let secondResolved = false
    const second = budget.acquire().then(() => {
      secondResolved = true
    })
    await Promise.resolve()
    expect(secondResolved).toBe(false)
    expect(budget.inFlight()).toBe(1)

    // Transfer: leave inFlight booked for the waiter (no free-then-reclaim race).
    budget.release()
    await second
    expect(secondResolved).toBe(true)
    expect(budget.inFlight()).toBe(1)

    budget.release()
    expect(budget.inFlight()).toBe(0)
  })

  it("createTabBudget rejects max_tabs < 1", () => {
    expect(() => createTabBudget(0)).toThrow(/max_tabs/)
  })
})
