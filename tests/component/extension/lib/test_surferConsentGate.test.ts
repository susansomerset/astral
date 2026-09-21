import { beforeEach, describe, expect, it, vi } from "vitest"
import {
  assertMayCapture,
  fetchConsent,
  mayCapture,
  type SurferConsentDto,
} from "../../../../src/ui/extension/src/lib/surferConsentGate"
import { optOutSurfer } from "../../../../src/ui/extension/src/lib/surferOffSwitch"

describe("Surfer consent gate / off-switch — AST-1238", () => {
  beforeEach(() => {
    vi.unstubAllGlobals()
  })

  it("mayCapture requires is_current", () => {
    expect(mayCapture({ is_current: true, capture_denied_message: "x" })).toBe(true)
    expect(mayCapture({ is_current: false, capture_denied_message: "x" })).toBe(false)
  })

  it("fetchConsent GETs with Bearer and assertMayCapture throws denied message", async () => {
    const dto: SurferConsentDto = {
      is_current: false,
      capture_denied_message: "Surfer is not enabled for this account.",
      status: "none",
    }
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => dto,
    }))
    vi.stubGlobal("fetch", fetchMock)

    const got = await fetchConsent("https://api.example", "c1", "tok")
    expect(got).toEqual(dto)
    expect(fetchMock).toHaveBeenCalledWith(
      "https://api.example/api/candidates/c1/surfer/consent",
      expect.objectContaining({
        method: "GET",
        credentials: "omit",
        headers: { Authorization: "Bearer tok" },
      }),
    )

    await expect(assertMayCapture("https://api.example", "c1", "tok")).rejects.toThrow(
      /not enabled/,
    )
  })

  it("assertMayCapture returns dto when current", async () => {
    const dto: SurferConsentDto = {
      is_current: true,
      capture_denied_message: "denied",
      status: "opted_in",
    }
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({ ok: true, json: async () => dto })),
    )
    await expect(assertMayCapture("https://api.example", "c1", "tok")).resolves.toEqual(dto)
  })

  it("optOutSurfer PUTs action opt_out", async () => {
    const dto: SurferConsentDto = {
      is_current: false,
      capture_denied_message: "denied",
      status: "opted_out",
    }
    const fetchMock = vi.fn(async (_url: string, init?: RequestInit) => {
      expect(init?.method).toBe("PUT")
      expect(JSON.parse(String(init?.body))).toEqual({ action: "opt_out" })
      return { ok: true, json: async () => dto }
    })
    vi.stubGlobal("fetch", fetchMock)
    await expect(optOutSurfer("https://api.example", "c1", "tok")).resolves.toEqual(dto)
  })
})
