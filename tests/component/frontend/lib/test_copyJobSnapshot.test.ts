import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import { copyJobSnapshotToClipboard } from "../../../../src/ui/frontend/src/lib/copyJobSnapshot"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("copyJobSnapshotToClipboard — AST-1421", () => {
  beforeEach(() => {
    mockedApi.mockReset()
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    })
  })

  it("pretty-prints JSON onto the clipboard on OK", async () => {
    const body = { job: { astral_job_id: "j1" }, agent_data: {} }
    mockedApi.mockResolvedValue({
      ok: true,
      json: async () => body,
    } as Response)
    expect(await copyJobSnapshotToClipboard("j1")).toBe(true)
    expect(mockedApi).toHaveBeenCalledWith("/api/jobs/j1/copy")
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(JSON.stringify(body, null, 2))
  })

  it("encodes the job id and omits query params", async () => {
    mockedApi.mockResolvedValue({
      ok: true,
      json: async () => ({}),
    } as Response)
    await copyJobSnapshotToClipboard("job/x y")
    expect(mockedApi).toHaveBeenCalledWith("/api/jobs/job%2Fx%20y/copy")
    expect(String(mockedApi.mock.calls[0][0])).not.toContain("debug")
  })

  it("returns false on non-OK, json failure, and clipboard reject — no throw", async () => {
    mockedApi.mockResolvedValue({ ok: false } as Response)
    expect(await copyJobSnapshotToClipboard("j1")).toBe(false)
    expect(navigator.clipboard.writeText).not.toHaveBeenCalled()

    mockedApi.mockResolvedValue({
      ok: true,
      json: async () => {
        throw new Error("bad json")
      },
    } as Response)
    expect(await copyJobSnapshotToClipboard("j1")).toBe(false)

    mockedApi.mockResolvedValue({
      ok: true,
      json: async () => ({}),
    } as Response)
    vi.mocked(navigator.clipboard.writeText).mockRejectedValue(new Error("denied"))
    expect(await copyJobSnapshotToClipboard("j1")).toBe(false)
  })
})
