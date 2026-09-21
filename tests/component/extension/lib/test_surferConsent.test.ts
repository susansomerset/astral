// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from "vitest"
import {
  fetchSurferConsent,
  needsDisclosure,
  optInSurferConsent,
  type SurferConsentDto,
} from "../../../../src/ui/extension/src/lib/surferConsent"
import { mountSurferDisclosure } from "../../../../src/ui/extension/src/lib/surferDisclosureDom"

const dto: SurferConsentDto = {
  status: "none",
  accepted_version: null,
  updated_at: null,
  current_version: "2",
  disclosure_copy: "Para one.\n\nPara two\nwith break.",
  is_current: false,
  disclosure_title: "Before you use Astral Surfer",
  opt_in_label: "I understand — turn on Surfer",
  decline_label: "Not now",
  current_ok_title: "Surfer is on",
  current_ok_body: "Already current.",
}

describe("Surfer consent lib — AST-1237", () => {
  beforeEach(() => {
    document.body.replaceChildren()
  })

  it("needsDisclosure is true only when not current", () => {
    expect(needsDisclosure(dto)).toBe(true)
    expect(needsDisclosure({ ...dto, is_current: true })).toBe(false)
  })

  it("fetchSurferConsent and optInSurferConsent use injected helpers", async () => {
    const getJson = vi.fn(async (path: string) => {
      expect(path).toBe("/api/candidates/c1/surfer/consent")
      return dto
    })
    expect(await fetchSurferConsent("c1", getJson)).toEqual(dto)
    expect(getJson).toHaveBeenCalledOnce()

    const putJson = vi.fn(async (path: string, body: unknown) => {
      expect(path).toBe("/api/candidates/c1/surfer/consent")
      expect(body).toEqual({ action: "opt_in", accepted_version: "2" })
      return { ...dto, is_current: true, status: "opted_in", accepted_version: "2" }
    })
    const next = await optInSurferConsent("c1", dto, putJson)
    expect(next.is_current).toBe(true)
    expect(putJson).toHaveBeenCalledOnce()
  })

  it("mountSurferDisclosure renders chrome and wires handlers; decline does not opt-in", async () => {
    const host = document.createElement("div")
    document.body.appendChild(host)
    const onOptIn = vi.fn()
    const onDecline = vi.fn()
    const { unmount } = mountSurferDisclosure(host, dto, { onOptIn, onDecline })
    const root = host.shadowRoot ?? host
    expect(root.querySelector(".astral-surfer-consent-title")?.textContent).toBe(dto.disclosure_title)
    const paragraphs = root.querySelectorAll(".astral-surfer-consent-body p")
    expect(paragraphs.length).toBe(2)
    expect(paragraphs[0].textContent).toBe("Para one.")
    expect(paragraphs[1].querySelector("br")).toBeTruthy()

    const optInBtn = root.querySelector(".astral-surfer-consent-opt-in") as HTMLButtonElement
    const declineBtn = root.querySelector(".astral-surfer-consent-decline") as HTMLButtonElement
    expect(optInBtn.textContent).toBe(dto.opt_in_label)
    expect(declineBtn.textContent).toBe(dto.decline_label)

    declineBtn.click()
    expect(onDecline).toHaveBeenCalledOnce()
    expect(onOptIn).not.toHaveBeenCalled()

    optInBtn.click()
    expect(onOptIn).toHaveBeenCalledOnce()

    unmount()
    expect(root.querySelector(".astral-surfer-consent-panel")).toBeNull()
  })
})
