import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CandidateSurfer from "../../../../src/ui/frontend/src/pages/CandidateSurfer"
import { renderWithProviders } from "../test-utils"
import { candidateId, installBaseApiMocks, jsonResponse } from "./page-mocks"

const confirm = vi.fn(async () => true)

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

vi.mock("../../../../src/ui/frontend/src/components/UserPrompt", async () => {
  const actual = await vi.importActual<
    typeof import("../../../../src/ui/frontend/src/components/UserPrompt")
  >("../../../../src/ui/frontend/src/components/UserPrompt")
  return { ...actual, useUserConfirm: () => confirm }
})

const mockedApi = vi.mocked(api)

const baseLabels = {
  off_switch_heading: "Astral Surfer",
  off_switch_button_label: "Turn Surfer off",
  off_switch_confirm: "Turn Surfer off?",
  status_on_label: "Surfer is on — the extension may capture pages you choose.",
  status_off_label: "Surfer is off — nothing will be captured.",
  status_stale_label:
    "Surfer was on under an older disclosure — capture is paused until you opt in again.",
  uninstall_guidance: "To remove the extension entirely: open chrome://extensions.",
}

describe("CandidateSurfer — AST-1238", () => {
  beforeEach(() => {
    localStorage.clear()
    confirm.mockReset()
    confirm.mockResolvedValue(true)
    mockedApi.mockReset()
  })

  it("empty state when no candidate selected", async () => {
    installBaseApiMocks(mockedApi, async (url) => {
      if (url === "/api/candidates") return jsonResponse([])
      throw new Error(`unexpected api call: ${url}`)
    })
    renderWithProviders(<CandidateSurfer />)
    await waitFor(() => expect(screen.getByText("Select a candidate.")).toBeInTheDocument())
  })

  it("shows on status and opts out after confirm", async () => {
    const puts: unknown[] = []
    let current = {
      status: "opted_in",
      is_current: true,
      ...baseLabels,
    }
    installBaseApiMocks(mockedApi, async (url, init) => {
      if (url === `/api/candidates/${candidateId}/surfer/consent` && !init?.method) {
        return jsonResponse(current)
      }
      if (url === `/api/candidates/${candidateId}/surfer/consent` && init?.method === "PUT") {
        puts.push(JSON.parse(String(init.body)))
        current = { status: "opted_out", is_current: false, ...baseLabels }
        return jsonResponse(current)
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderWithProviders(<CandidateSurfer />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: baseLabels.off_switch_heading })).toBeInTheDocument(),
    )
    expect(screen.getByText(baseLabels.status_on_label)).toBeInTheDocument()
    expect(screen.getByText(baseLabels.uninstall_guidance)).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: baseLabels.off_switch_button_label }))
    await waitFor(() => expect(screen.getByText("Surfer turned off")).toBeInTheDocument())
    expect(puts).toEqual([{ action: "opt_out" }])
    expect(confirm).toHaveBeenCalledWith(baseLabels.off_switch_confirm)
    expect(screen.getByText(baseLabels.status_off_label)).toBeInTheDocument()
  })

  it("stale opted_in shows stale label and still offers off-switch", async () => {
    installBaseApiMocks(mockedApi, async (url, init) => {
      if (url === `/api/candidates/${candidateId}/surfer/consent` && !init?.method) {
        return jsonResponse({
          status: "opted_in",
          is_current: false,
          ...baseLabels,
        })
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderWithProviders(<CandidateSurfer />)
    await waitFor(() => expect(screen.getByText(baseLabels.status_stale_label)).toBeInTheDocument())
    expect(screen.getByRole("button", { name: baseLabels.off_switch_button_label })).toBeInTheDocument()
    expect(screen.queryByText(baseLabels.status_off_label)).not.toBeInTheDocument()
  })

  it("cancel confirm does not PUT", async () => {
    confirm.mockResolvedValue(false)
    installBaseApiMocks(mockedApi, async (url, init) => {
      if (url === `/api/candidates/${candidateId}/surfer/consent` && !init?.method) {
        return jsonResponse({ status: "opted_in", is_current: true, ...baseLabels })
      }
      if (init?.method === "PUT") throw new Error("must not PUT when confirm cancelled")
      throw new Error(`unexpected api call: ${url}`)
    })
    renderWithProviders(<CandidateSurfer />)
    await waitFor(() =>
      expect(screen.getByRole("button", { name: baseLabels.off_switch_button_label })).toBeInTheDocument(),
    )
    await userEvent.click(screen.getByRole("button", { name: baseLabels.off_switch_button_label }))
    expect(confirm).toHaveBeenCalled()
  })

  it("off status hides off-switch button", async () => {
    installBaseApiMocks(mockedApi, async (url, init) => {
      if (url === `/api/candidates/${candidateId}/surfer/consent` && !init?.method) {
        return jsonResponse({ status: "none", is_current: false, ...baseLabels })
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderWithProviders(<CandidateSurfer />)
    await waitFor(() => expect(screen.getByText(baseLabels.status_off_label)).toBeInTheDocument())
    expect(screen.queryByRole("button", { name: baseLabels.off_switch_button_label })).not.toBeInTheDocument()
  })
})
