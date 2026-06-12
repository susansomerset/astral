import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import ArtifactsCompanySearchTerms from "../../../../src/ui/frontend/src/pages/ArtifactsCompanySearchTerms"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("ArtifactsCompanySearchTerms", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "CONTEXT_READY", candidate_data: {} }],
        } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            company_search_terms: "Series B fintech\nremote-first",
            candidate_data: {},
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        return { ok: true, json: async () => ({}) } as Response
      }
      if (url === "/api/candidates/c1/generate/craft_company_search_terms" && init?.method === "POST") {
        return {
          ok: true,
          json: async () => ({
            success: true,
            parsed_response: { search_terms: "generated term one\ngenerated term two" },
          }),
        } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
  })

  it("renders company search terms page with loaded text and generate affordance", async () => {
    renderWithProviders(<ArtifactsCompanySearchTerms />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Company Search Terms" })).toBeInTheDocument(),
    )
    expect(screen.getByRole("textbox")).toHaveValue("Series B fintech\nremote-first")
    expect(screen.getByRole("button", { name: "Regenerate" })).toBeInTheDocument()
  })

  it("populates textarea after generate when empty", async () => {
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "CONTEXT_READY", candidate_data: {} }],
        } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return { json: async () => ({ company_search_terms: "", candidate_data: {} }) } as Response
      }
      if (url === "/api/candidates/c1/generate/craft_company_search_terms" && init?.method === "POST") {
        return {
          ok: true,
          json: async () => ({
            success: true,
            parsed_response: { search_terms: "generated term one\ngenerated term two" },
          }),
        } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })

    renderWithProviders(<ArtifactsCompanySearchTerms />)
    await waitFor(() => expect(screen.getByRole("button", { name: "Generate" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Generate" }))
    await waitFor(() =>
      expect(screen.getByRole("textbox")).toHaveValue("generated term one\ngenerated term two"),
    )
    expect(screen.getByRole("button", { name: "Save" })).toBeInTheDocument()
  })
})
