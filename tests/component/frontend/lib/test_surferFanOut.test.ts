import { beforeEach, describe, expect, it, vi } from "vitest"
import type { FanOutPorts, RemainingWork } from "../../../../src/ui/extension/src/lib/fanOut"

const dwell = vi.fn(async () => 0.01)
const fetchPacingConfig = vi.fn(async () => ({
  dwell_center_seconds: 10,
  dwell_spread_seconds: 5,
  max_tabs: 1,
  mv3_idle_ceiling_seconds: 30,
}))
const createTabBudget = vi.fn(() => {
  let inFlight = 0
  return {
    async acquire() {
      if (inFlight >= 1) throw new Error("budget exceeded")
      inFlight += 1
    },
    release() {
      inFlight -= 1
    },
    inFlight: () => inFlight,
  }
})

vi.mock("../../../../src/ui/extension/src/lib/dwell", () => ({
  dwell: (...args: unknown[]) => dwell(...args),
}))
vi.mock("../../../../src/ui/extension/src/lib/pacingConfig", () => ({
  fetchPacingConfig: (...args: unknown[]) => fetchPacingConfig(...args),
  createTabBudget: (...args: unknown[]) => createTabBudget(...args),
}))

const { runPacedFanOut } = await import("../../../../src/ui/extension/src/lib/fanOut")

function remaining(partial: Partial<RemainingWork> & { remaining_urls: string[] }): RemainingWork {
  return {
    batch_id: "surfer-b1",
    status: "RUNNING",
    done_count: 0,
    total_count: partial.remaining_urls.length || partial.total_count || 0,
    ...partial,
  }
}

function makePorts(overrides: Partial<FanOutPorts> = {}): FanOutPorts & {
  calls: string[]
} {
  const calls: string[] = []
  const ports: FanOutPorts & { calls: string[] } = {
    calls,
    getJson: vi.fn(async (path: string) => {
      calls.push(`getJson:${path}`)
      return {
        dwell_center_seconds: 10,
        dwell_spread_seconds: 5,
        max_tabs: 1,
        mv3_idle_ceiling_seconds: 30,
      }
    }),
    fetchRemaining: vi.fn(async () => remaining({ remaining_urls: [], total_count: 0 })),
    postPage: vi.fn(async ({ pageUrl }) => {
      calls.push(`post:${pageUrl}`)
      return { ok: true as const }
    }),
    reportUrlFailure: vi.fn(async ({ pageUrl, reason }) => {
      calls.push(`fail:${pageUrl}:${reason}`)
    }),
    openTab: vi.fn(async (url) => {
      calls.push(`open:${url}`)
      return 7
    }),
    waitForLoad: vi.fn(async (tabId) => {
      calls.push(`wait:${tabId}`)
    }),
    captureVisibleText: vi.fn(async () => {
      calls.push("capture")
      return "visible job text"
    }),
    closeTab: vi.fn(async (tabId) => {
      calls.push(`close:${tabId}`)
    }),
    ...overrides,
  }
  return ports
}

describe("runPacedFanOut — AST-1239", () => {
  beforeEach(() => {
    dwell.mockClear()
    fetchPacingConfig.mockClear()
    createTabBudget.mockClear()
  })

  it("rejects empty batchId", async () => {
    await expect(runPacedFanOut("  ", makePorts())).rejects.toThrow(/batchId/)
  })

  it("returns empty_batch when total_count is 0 and no remaining", async () => {
    const ports = makePorts({
      fetchRemaining: vi.fn(async () => remaining({ remaining_urls: [], total_count: 0 })),
    })
    const result = await runPacedFanOut("surfer-b1", ports)
    expect(result).toEqual({
      batchId: "surfer-b1",
      visited: 0,
      failed: 0,
      stoppedReason: "empty_batch",
    })
    expect(ports.openTab).not.toHaveBeenCalled()
  })

  it("returns exhausted when remaining empty but total_count > 0", async () => {
    const ports = makePorts({
      fetchRemaining: vi.fn(async () =>
        remaining({ remaining_urls: [], total_count: 3, done_count: 3 }),
      ),
    })
    const result = await runPacedFanOut("surfer-b1", ports)
    expect(result.stoppedReason).toBe("exhausted")
  })

  it("visits once: open → wait → dwell → capture → post → close (delivery only)", async () => {
    let n = 0
    const ports = makePorts({
      fetchRemaining: vi.fn(async () => {
        n += 1
        if (n === 1) return remaining({ remaining_urls: ["https://jobs.example/1"], total_count: 1 })
        return remaining({ remaining_urls: [], total_count: 1, done_count: 0 })
      }),
    })
    const result = await runPacedFanOut("surfer-b1", ports, { debug: true })
    expect(result).toEqual({
      batchId: "surfer-b1",
      visited: 1,
      failed: 0,
      stoppedReason: "exhausted",
    })
    expect(fetchPacingConfig).toHaveBeenCalledOnce()
    expect(dwell).toHaveBeenCalledOnce()
    expect(ports.calls).toEqual([
      "open:https://jobs.example/1",
      "wait:7",
      "capture",
      "post:https://jobs.example/1",
      "close:7",
    ])
    expect(ports.postPage).toHaveBeenCalledWith({
      batchId: "surfer-b1",
      pageUrl: "https://jobs.example/1",
      pageText: "visible job text",
      debug: true,
    })
    // Delivery ack is not treated as batch COMPLETED — loop exits on empty remaining only.
    expect(ports.fetchRemaining).toHaveBeenCalledTimes(2)
  })

  it("empty capture records empty_capture and continues", async () => {
    let n = 0
    const ports = makePorts({
      fetchRemaining: vi.fn(async () => {
        n += 1
        if (n === 1) return remaining({ remaining_urls: ["https://jobs.example/bad"], total_count: 1 })
        return remaining({ remaining_urls: [], total_count: 1 })
      }),
      captureVisibleText: vi.fn(async () => "   "),
    })
    const result = await runPacedFanOut("surfer-b1", ports)
    expect(result.visited).toBe(0)
    expect(result.failed).toBe(1)
    expect(ports.reportUrlFailure).toHaveBeenCalledWith({
      batchId: "surfer-b1",
      pageUrl: "https://jobs.example/bad",
      reason: "empty_capture",
      debug: undefined,
    })
    expect(ports.postPage).not.toHaveBeenCalled()
    expect(ports.closeTab).toHaveBeenCalledOnce()
  })

  it("page error records page_error:<detail> and continues", async () => {
    let n = 0
    const ports = makePorts({
      fetchRemaining: vi.fn(async () => {
        n += 1
        if (n === 1) return remaining({ remaining_urls: ["https://jobs.example/err"], total_count: 1 })
        return remaining({ remaining_urls: [], total_count: 1 })
      }),
      openTab: vi.fn(async () => {
        throw new Error("net::ERR_NAME_NOT_RESOLVED")
      }),
    })
    const result = await runPacedFanOut("surfer-b1", ports)
    expect(result.failed).toBe(1)
    expect(ports.reportUrlFailure).toHaveBeenCalledWith(
      expect.objectContaining({
        reason: "page_error:net::ERR_NAME_NOT_RESOLVED",
      }),
    )
  })

  it("stops with no_progress when server re-offers a URL already recorded this run", async () => {
    const ports = makePorts({
      fetchRemaining: vi.fn(async () =>
        remaining({ remaining_urls: ["https://jobs.example/stuck"], total_count: 1 }),
      ),
    })
    const result = await runPacedFanOut("surfer-b1", ports)
    expect(result.stoppedReason).toBe("no_progress")
    expect(result.visited).toBe(1)
    expect(ports.openTab).toHaveBeenCalledTimes(1)
    expect(ports.fetchRemaining).toHaveBeenCalledTimes(2)
  })

  it("closeTab failure does not abort the batch", async () => {
    let n = 0
    const ports = makePorts({
      fetchRemaining: vi.fn(async () => {
        n += 1
        if (n === 1) return remaining({ remaining_urls: ["https://jobs.example/1"], total_count: 1 })
        return remaining({ remaining_urls: [], total_count: 1 })
      }),
      closeTab: vi.fn(async () => {
        throw new Error("tab already gone")
      }),
    })
    const result = await runPacedFanOut("surfer-b1", ports)
    expect(result.visited).toBe(1)
    expect(result.stoppedReason).toBe("exhausted")
  })
})
