import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import {
  POPUP_BLOCKED_MESSAGE,
  fetchPrintHtml,
  openHtmlInNewTab,
} from "../../../../src/ui/frontend/src/lib/printHtml"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

function htmlResponse(body: string): Response {
  return { ok: true, status: 200, text: async () => body } as Response
}

function errorResponse(status: number, json: () => Promise<unknown>): Response {
  return { ok: false, status, json } as unknown as Response
}

// AST-2082: one shared fetch/open helper for builder print HTML (base, job resume, cover).
describe("AST-2082 fetchPrintHtml", () => {
  beforeEach(() => mockedApi.mockReset())

  it.each([
    ["base", "c 1", "/candidate/resume/base?candidate_id=c%201"],
    ["job_resume", "job/1", "/candidate/resume/job%2F1"],
    ["cover", "job-1", "/candidate/cover/job-1"],
  ] as const)("AC3: %s reads its builder route and returns the exact body", async (kind, id, path) => {
    mockedApi.mockResolvedValue(htmlResponse("<html><body>Ada</body></html>"))
    await expect(fetchPrintHtml({ kind, id })).resolves.toEqual({ ok: true, html: "<html><body>Ada</body></html>" })
    expect(mockedApi).toHaveBeenCalledWith(path)
  })

  it("non-2xx returns the builder's error text, else HTTP status", async () => {
    mockedApi.mockResolvedValueOnce(errorResponse(404, async () => ({ error: "Job not found" })))
    await expect(fetchPrintHtml({ kind: "job_resume", id: "j" })).resolves.toEqual({ ok: false, error: "Job not found" })
    mockedApi.mockResolvedValueOnce(errorResponse(500, async () => { throw new Error("not json") }))
    await expect(fetchPrintHtml({ kind: "cover", id: "j" })).resolves.toEqual({ ok: false, error: "HTTP 500" })
    mockedApi.mockResolvedValueOnce(errorResponse(502, async () => ({ error: "" })))
    await expect(fetchPrintHtml({ kind: "cover", id: "j" })).resolves.toEqual({ ok: false, error: "HTTP 502" })
  })

  it("legacy empty-base key path reads as operator copy for base only", async () => {
    const legacy = async () => ({ error: "Candidate missing artifacts.base_resume" })
    mockedApi.mockResolvedValueOnce(errorResponse(400, legacy))
    await expect(fetchPrintHtml({ kind: "base", id: "c1" })).resolves.toEqual({
      ok: false,
      error: "No printable base resume content for this candidate",
    })
    mockedApi.mockResolvedValueOnce(errorResponse(400, legacy))
    await expect(fetchPrintHtml({ kind: "job_resume", id: "j" })).resolves.toEqual({
      ok: false,
      error: "Candidate missing artifacts.base_resume",
    })
  })

  it("blank body and thrown errors never throw", async () => {
    mockedApi.mockResolvedValueOnce(htmlResponse("  \n"))
    await expect(fetchPrintHtml({ kind: "base", id: "c1" })).resolves.toEqual({ ok: false, error: "HTML response was empty" })
    mockedApi.mockRejectedValueOnce(new Error("network down"))
    await expect(fetchPrintHtml({ kind: "base", id: "c1" })).resolves.toEqual({ ok: false, error: "network down" })
    mockedApi.mockRejectedValueOnce("boom")
    await expect(fetchPrintHtml({ kind: "base", id: "c1" })).resolves.toEqual({ ok: false, error: "Print failed" })
  })
})

describe("AST-2082 openHtmlInNewTab", () => {
  beforeEach(() => {
    vi.useFakeTimers()
    URL.createObjectURL = vi.fn(() => "blob:preview")
    URL.revokeObjectURL = vi.fn()
  })
  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it("opens the blob in a new tab, severs opener, revokes after 60s", () => {
    const win = { opener: {} } as unknown as Window
    const open = vi.spyOn(window, "open").mockReturnValue(win)
    expect(openHtmlInNewTab("<p>x</p>")).toBeNull()
    expect(open).toHaveBeenCalledWith("blob:preview", "_blank")
    expect(win.opener).toBeNull()
    const blob = vi.mocked(URL.createObjectURL).mock.calls[0][0] as Blob
    expect(blob.type).toBe("text/html;charset=utf-8")
    expect(URL.revokeObjectURL).not.toHaveBeenCalled()
    vi.advanceTimersByTime(60_000)
    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:preview")
  })

  it("returns the popup-blocked message when window.open yields null", () => {
    vi.spyOn(window, "open").mockReturnValue(null)
    expect(openHtmlInNewTab("<p>x</p>")).toBe(POPUP_BLOCKED_MESSAGE)
  })
})
