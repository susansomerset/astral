import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CompaniesIgnored from "../../../../src/ui/frontend/src/pages/CompaniesIgnored"
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
    state: "IGNORE",
    prefilter_company_notes: "nope",
    state_updated_at: "2026-01-01T00:00:00Z",
    state_history: [],
  },
]

describe("CompaniesIgnored", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("loads companies and moves selected rows to watch", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/companies/bulk_state" && init?.method === "POST") {
        return jsonResponse({ updated: 1 })
      }
      return companyListHandler("ignored", companies, "ignored")(url)
    })
    renderWithProviders(<CompaniesIgnored />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())
    await userEvent.click(screen.getAllByRole("checkbox")[0])
    await userEvent.click(screen.getByRole("button", { name: "Move to Watch" }))
    await waitFor(() => expect(screen.getByText("1 precious snowflakes moved to watch list")).toBeInTheDocument())
  })

  it("falls back to empty columns when shape has no ignored list", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/companies/bulk_state" && init?.method === "POST") {
        return jsonResponse({ updated: 1 })
      }
      if (url === `/api/companies?view=ignored&candidate_id=${candidateId}`) {
        return jsonResponse(companies)
      }
      if (url === "/api/shapes/companies") {
        return jsonResponse({ list: { watch_list: [] } })
      }
      return undefined
    })
    renderWithProviders(<CompaniesIgnored />)
    await waitFor(() => expect(document.querySelectorAll("tbody tr.clickable")).toHaveLength(1))
  })

  it("handles non-array payloads and move failures", async () => {
    installBaseApiMocks(mockedApi, companyListHandler("ignored", { bad: true } as unknown as typeof companies, "ignored"))
    renderWithProviders(<CompaniesIgnored />)
    await waitFor(() => expect(screen.getByText("No records found.")).toBeInTheDocument())

    installBaseApiMocks(mockedApi, (url) => {
      if (url === "/api/companies/bulk_state") {
        return Promise.reject(new Error("network"))
      }
      return companyListHandler("ignored", companies, "ignored")(url)
    })
    renderWithProviders(<CompaniesIgnored />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())
    await userEvent.click(screen.getAllByRole("checkbox")[0])
    await userEvent.click(screen.getByRole("button", { name: "Move to Watch" }))
    await waitFor(() => expect(screen.getByText("Move failed")).toBeInTheDocument())
  })
})
