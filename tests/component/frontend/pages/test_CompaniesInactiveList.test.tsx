import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CompaniesInactiveList from "../../../../src/ui/frontend/src/pages/CompaniesInactiveList"
import { renderWithProviders } from "../test-utils"
import { candidateId, companyListHandler, installBaseApiMocks, jsonResponse } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const companies = [
  {
    short_name: "acme",
    company_name: "Acme Corp",
    state: "INACTIVE",
    state_updated_at: "2026-01-01T00:00:00Z",
    state_history: [],
  },
]

describe("CompaniesInactiveList", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("loads companies and retries selected rows", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/companies/bulk_state" && init?.method === "POST") {
        return jsonResponse({ updated: 1 })
      }
      return companyListHandler("inactive_list", companies, "inactive_list")(url)
    })
    renderWithProviders(<CompaniesInactiveList />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())
    await userEvent.click(screen.getAllByRole("checkbox")[0])
    await userEvent.click(screen.getByRole("button", { name: "Retry" }))
    await waitFor(() => expect(screen.getByText("1 companies queued for website review")).toBeInTheDocument())
  })

  it("falls back to empty columns when shape has no inactive list", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/companies/bulk_state" && init?.method === "POST") {
        return jsonResponse({ updated: 1 })
      }
      if (url === `/api/companies?view=inactive_list&candidate_id=${candidateId}`) {
        return jsonResponse(companies)
      }
      if (url === "/api/shapes/companies") {
        return jsonResponse({ list: { ignored: [] } })
      }
      return undefined
    })
    renderWithProviders(<CompaniesInactiveList />)
    await waitFor(() => expect(document.querySelectorAll("tbody tr.clickable")).toHaveLength(1))
  })

  it("handles non-array payloads and retry failures", async () => {
    installBaseApiMocks(mockedApi, companyListHandler("inactive_list", { bad: true } as unknown as typeof companies, "inactive_list"))
    renderWithProviders(<CompaniesInactiveList />)
    await waitFor(() => expect(screen.getByText("No records found.")).toBeInTheDocument())

    installBaseApiMocks(mockedApi, (url) => {
      if (url === "/api/companies/bulk_state") {
        return Promise.reject(new Error("network"))
      }
      return companyListHandler("inactive_list", companies, "inactive_list")(url)
    })
    renderWithProviders(<CompaniesInactiveList />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())
    await userEvent.click(screen.getAllByRole("checkbox")[0])
    await userEvent.click(screen.getByRole("button", { name: "Retry" }))
    await waitFor(() => expect(screen.getByText("Retry failed")).toBeInTheDocument())
  })
})
