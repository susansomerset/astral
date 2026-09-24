import { screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CompaniesMeteorite from "../../../../src/ui/frontend/src/pages/CompaniesMeteorite"
import { renderWithProviders } from "../test-utils"
import { candidateId, installBaseApiMocks, jsonResponse } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const companies = [
  {
    short_name: "alice@example.com-c1",
    company_name: "meteorite",
    state: "METEORITE",
    state_updated_at: "2026-01-01T00:00:00Z",
  },
]

describe("CompaniesMeteorite", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("loads meteorite companies list", async () => {
    installBaseApiMocks(mockedApi, (url) => {
      if (url === `/api/companies?view=meteorite_list&candidate_id=${candidateId}`) {
        return jsonResponse(companies)
      }
      return undefined
    })
    renderWithProviders(<CompaniesMeteorite />)
    await waitFor(() => expect(screen.getByText("Meteorite")).toBeInTheDocument())
    await waitFor(() => expect(screen.getByText("meteorite")).toBeInTheDocument())
    expect(mockedApi).toHaveBeenCalledWith(
      `/api/companies?view=meteorite_list&candidate_id=${candidateId}`,
    )
  })

  it("handles non-array payloads", async () => {
    installBaseApiMocks(mockedApi, (url) => {
      if (url === `/api/companies?view=meteorite_list&candidate_id=${candidateId}`) {
        return jsonResponse({ bad: true })
      }
      return undefined
    })
    renderWithProviders(<CompaniesMeteorite />)
    await waitFor(() => expect(screen.getByText("No records found.")).toBeInTheDocument())
  })
})
