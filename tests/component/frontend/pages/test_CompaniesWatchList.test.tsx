import { cleanup, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CompaniesWatchList from "../../../../src/ui/frontend/src/pages/CompaniesWatchList"
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
    company_website: "https://acme.test",
    state: "WATCH",
    last_scan_at: "2026-01-01T00:00:00Z",
    state_history: [],
  },
  {
    short_name: "beta",
    company_name: "Beta Inc",
    company_website: "https://beta.test",
    state: "WATCH",
    last_scan_at: "2026-01-02T00:00:00Z",
    state_history: [],
  },
]

describe("CompaniesWatchList", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("loads companies and opens the detail modal", async () => {
    // Same routing as other cases; a lone `url =>` handler once drifted from listKey/shape parity.
    installBaseApiMocks(mockedApi, companyListHandler("watch_list", companies, "watch_list"))
    renderWithProviders(<CompaniesWatchList />)
    expect(await screen.findByRole("columnheader", { name: "Company" })).toBeInTheDocument()
    expect(await screen.findByText("Acme Corp")).toBeInTheDocument()
    await userEvent.click(screen.getByText("Acme Corp"))
    await waitFor(() => expect(mockedApi).toHaveBeenCalledWith("/api/companies/acme"))
  })

  it("runs retry and ignore bulk actions", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/companies/bulk_state" && init?.method === "POST") {
        return jsonResponse({ updated: 1 })
      }
      return companyListHandler("watch_list", companies, "watch_list")(url)
    })
    renderWithProviders(<CompaniesWatchList />)
    await waitFor(() => expect(screen.getByText("Beta Inc")).toBeInTheDocument())

    await userEvent.click(within(screen.getByRole("row", { name: /Acme Corp/ })).getByRole("checkbox"))
    await userEvent.click(screen.getByRole("button", { name: "Retry Scrape" }))
    await waitFor(() => expect(screen.getByText("1 companies updated")).toBeInTheDocument())

    await userEvent.click(within(screen.getByRole("row", { name: /Beta Inc/ })).getByRole("checkbox"))
    await userEvent.click(screen.getByRole("button", { name: "Set to Ignore" }))
    await waitFor(() => expect(screen.getByText("1 companies updated")).toBeInTheDocument())
    await waitFor(() => expect(mockedApi).toHaveBeenCalledWith(
      "/api/companies/bulk_state",
      expect.objectContaining({ method: "POST" }),
    ))
  })

  it("handles non-array payloads and bulk failures", async () => {
    installBaseApiMocks(mockedApi, companyListHandler("watch_list", { bad: true } as unknown as typeof companies, "watch_list"))
    renderWithProviders(<CompaniesWatchList />)
    await waitFor(() => expect(screen.getByText("No records found.")).toBeInTheDocument())

    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/companies/bulk_state") {
        return Promise.reject(new Error("network"))
      }
      return companyListHandler("watch_list", companies, "watch_list")(url)
    })
    cleanup()
    renderWithProviders(<CompaniesWatchList />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())
    await userEvent.click(screen.getAllByRole("checkbox")[0])
    await userEvent.click(screen.getByRole("button", { name: "Set to Ignore" }))
    await waitFor(() => expect(screen.getByText("Bulk action failed")).toBeInTheDocument())
  })

  it("uses empty columns when shapes omit watch_list", async () => {
    installBaseApiMocks(mockedApi, (url: string) => {
      if (url === `/api/companies?view=watch_list&candidate_id=${candidateId}`) {
        return jsonResponse(companies)
      }
      if (url === "/api/shapes/companies") {
        return jsonResponse({ list: {} })
      }
      if (url.startsWith("/api/companies/") && !url.includes("bulk_state")) {
        return jsonResponse({
          short_name: "acme",
          company_name: "Acme Corp",
          company_website: "https://acme.test",
          state: "WATCH",
          state_history: [],
          job_state_counts: {},
          agent_story: [],
        })
      }
      throw new Error(url)
    })
    renderWithProviders(<CompaniesWatchList />)
    await waitFor(() => expect(screen.getAllByRole("row")).toHaveLength(3))
    expect(screen.queryByRole("columnheader", { name: "Company" })).not.toBeInTheDocument()
  })

  it("skips loading when no candidate is selected", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/candidates") {
        return jsonResponse([])
      }
      if (url === "/api/state_ui_manifest") {
        return Promise.reject(new Error("use default manifest"))
      }
      if (url === "/api/system/ui_config") {
        return jsonResponse({ column_types: {} })
      }
      throw new Error(url)
    })
    renderWithProviders(<CompaniesWatchList />)
    await waitFor(() => expect(screen.getByText("Loading...")).toBeInTheDocument())
    expect(mockedApi.mock.calls.some(call => String(call[0]).includes(`view=watch_list&candidate_id=${candidateId}`))).toBe(false)
  })
})
