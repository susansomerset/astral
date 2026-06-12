import { cleanup, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CompaniesNewList from "../../../../src/ui/frontend/src/pages/CompaniesNewList"
import { renderWithProviders } from "../test-utils"
import { companyListHandler, installBaseApiMocks, jsonResponse } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const companies = [
  {
    short_name: "acme",
    company_name: "Acme Corp",
    company_website: "https://acme.test",
    state: "NEW",
    created_at: "2026-01-01T00:00:00Z",
    state_history: [],
  },
]

describe("CompaniesNewList", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("loads companies and imports valid CSV rows", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/companies/import" && init?.method === "POST") {
        return jsonResponse({ created: 2 })
      }
      return companyListHandler("new_list", companies, "new_list")(url)
    })
    renderWithProviders(<CompaniesNewList />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Import CSV" }))
    await userEvent.type(
      screen.getByPlaceholderText(/short_name,company_name,company_website/),
      "short_name,company_name,company_website\nbeta,Beta Corp,https://beta.test\n",
    )
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("2 companies imported")).toBeInTheDocument())
  }, 15_000)

  it("rejects empty or header-only CSV imports", async () => {
    installBaseApiMocks(mockedApi, companyListHandler("new_list", companies, "new_list"))
    renderWithProviders(<CompaniesNewList />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Import CSV" }))
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await userEvent.click(screen.getByRole("button", { name: "Import CSV" }))
    await userEvent.type(screen.getByPlaceholderText(/short_name,company_name,company_website/), "short_name,company_name,company_website\n")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("No valid rows found in CSV")).toBeInTheDocument())
  })

  it("handles import failures and non-array payloads", async () => {
    installBaseApiMocks(mockedApi, companyListHandler("new_list", { bad: true } as unknown as typeof companies, "new_list"))
    renderWithProviders(<CompaniesNewList />)
    await waitFor(() => expect(screen.getByText("No records found.")).toBeInTheDocument())

    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/companies/import") {
        return Promise.reject(new Error("network"))
      }
      return companyListHandler("new_list", companies, "new_list")(url)
    })
    cleanup()
    renderWithProviders(<CompaniesNewList />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Import CSV" }))
    await userEvent.type(screen.getByPlaceholderText(/short_name,company_name,company_website/), "gamma,Gamma Corp,https://gamma.test")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Import failed")).toBeInTheDocument())
  })
})
