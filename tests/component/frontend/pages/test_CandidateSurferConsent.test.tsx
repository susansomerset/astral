import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CandidateSurferConsent from "../../../../src/ui/frontend/src/pages/CandidateSurferConsent"
import { renderWithProviders } from "../test-utils"
import { candidateId, installBaseApiMocks, jsonResponse } from "./page-mocks"

const navigate = vi.fn()

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom")
  return { ...actual, useNavigate: () => navigate }
})

const mockedApi = vi.mocked(api)

const disclosureDto = {
  status: "none",
  accepted_version: null,
  updated_at: null,
  current_version: "2",
  disclosure_copy:
    "Session paragraph one.\n\nTerms risk paragraph.\n\nOptional framing paragraph.",
  is_current: false,
  disclosure_title: "Before you use Astral Surfer",
  opt_in_label: "I understand — turn on Surfer",
  decline_label: "Not now",
  current_ok_title: "Surfer is on",
  current_ok_body: "You already opted in to the current Surfer disclosure.",
}

const currentOkDto = {
  ...disclosureDto,
  status: "opted_in",
  accepted_version: "2",
  updated_at: "2026-08-07 12:00:00",
  is_current: true,
}

describe("CandidateSurferConsent — AST-1237", () => {
  beforeEach(() => {
    localStorage.clear()
    navigate.mockReset()
    mockedApi.mockReset()
  })

  it("empty state when no candidate selected", async () => {
    installBaseApiMocks(mockedApi, async (url) => {
      if (url === "/api/candidates") return jsonResponse([])
      throw new Error(`unexpected api call: ${url}`)
    })
    renderWithProviders(<CandidateSurferConsent />)
    await waitFor(() =>
      expect(screen.getByText("Select a candidate to view Surfer consent.")).toBeInTheDocument(),
    )
  })

  it("renders disclosure from GET DTO and opts in via PUT with current_version", async () => {
    const puts: unknown[] = []
    installBaseApiMocks(mockedApi, async (url, init) => {
      if (url === `/api/candidates/${candidateId}/surfer/consent` && !init?.method) {
        return jsonResponse(disclosureDto)
      }
      if (url === `/api/candidates/${candidateId}/surfer/consent` && init?.method === "PUT") {
        puts.push(JSON.parse(String(init.body)))
        return jsonResponse(currentOkDto)
      }
      throw new Error(`unexpected api call: ${url} ${init?.method ?? "GET"}`)
    })
    renderWithProviders(<CandidateSurferConsent />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: disclosureDto.disclosure_title })).toBeInTheDocument(),
    )
    expect(screen.getByText("Session paragraph one.")).toBeInTheDocument()
    expect(screen.getByText("Terms risk paragraph.")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: disclosureDto.opt_in_label }))
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: currentOkDto.current_ok_title })).toBeInTheDocument(),
    )
    expect(puts).toEqual([{ action: "opt_in", accepted_version: "2" }])
    expect(screen.queryByRole("button", { name: disclosureDto.opt_in_label })).not.toBeInTheDocument()
  })

  it("decline navigates away with no PUT", async () => {
    installBaseApiMocks(mockedApi, async (url, init) => {
      if (url === `/api/candidates/${candidateId}/surfer/consent` && !init?.method) {
        return jsonResponse(disclosureDto)
      }
      if (init?.method === "PUT") {
        throw new Error("decline must not PUT")
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderWithProviders(<CandidateSurferConsent />)
    await waitFor(() =>
      expect(screen.getByRole("button", { name: disclosureDto.decline_label })).toBeInTheDocument(),
    )
    await userEvent.click(screen.getByRole("button", { name: disclosureDto.decline_label }))
    expect(navigate).toHaveBeenCalledWith("/jobs/recommended")
  })

  it("current consent shows ok chrome without opt-in controls", async () => {
    installBaseApiMocks(mockedApi, async (url, init) => {
      if (url === `/api/candidates/${candidateId}/surfer/consent` && !init?.method) {
        return jsonResponse(currentOkDto)
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderWithProviders(<CandidateSurferConsent />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: currentOkDto.current_ok_title })).toBeInTheDocument(),
    )
    expect(screen.getByText(/already opted in/i)).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: disclosureDto.opt_in_label })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: disclosureDto.decline_label })).not.toBeInTheDocument()
  })
})
