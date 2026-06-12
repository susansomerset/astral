import { screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CompaniesWatchHistory from "../../../../src/ui/frontend/src/pages/CompaniesWatchHistory"
import { renderWithProviders } from "../test-utils"
import { candidateId, companyColumns, installBaseApiMocks, jsonResponse } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const scans = [
  {
    batch_id: "b1",
    short_name: "acme",
    company_name: "Acme Corp",
    scan_completed_at: "2026-01-01T00:00:00Z",
    total_found: 3,
    new: 1,
    duplicates: 2,
    status: "success",
    failure_message: null,
  },
  {
    batch_id: "b2",
    short_name: "beta",
    company_name: "Beta Corp",
    scan_completed_at: "2026-01-02T00:00:00Z",
    total_found: 0,
    new: 0,
    duplicates: 0,
    status: "failed",
    failure_message: "timeout",
  },
]

describe("CompaniesWatchHistory", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("renders scan history with success and failure status styling", async () => {
    installBaseApiMocks(mockedApi, url => {
      if (url === `/api/companies/scan_history?candidate_id=${candidateId}`) {
        return jsonResponse(scans)
      }
      if (url === "/api/shapes/companies") {
        return jsonResponse({ list: { watch_history: companyColumns.watch_history } })
      }
      throw new Error(url)
    })
    renderWithProviders(<CompaniesWatchHistory />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())
    expect(screen.getByText("success")).toBeInTheDocument()
    expect(screen.getByText("failed")).toBeInTheDocument()
  })

  it("shows the empty state for non-array payloads", async () => {
    installBaseApiMocks(mockedApi, url => {
      if (url === `/api/companies/scan_history?candidate_id=${candidateId}`) {
        return jsonResponse({ bad: true })
      }
      if (url === "/api/shapes/companies") {
        return jsonResponse({ list: { watch_history: [] } })
      }
      throw new Error(url)
    })
    renderWithProviders(<CompaniesWatchHistory />)
    await waitFor(() => expect(screen.getByText("No scan history recorded yet.")).toBeInTheDocument())
  })

  it("skips scan_history fetch when no candidate is selected", async () => {
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
      throw new Error(`unexpected api call: ${url}`)
    })
    renderWithProviders(<CompaniesWatchHistory />)
    await waitFor(() => expect(screen.getByText("Loading...")).toBeInTheDocument())
    expect(mockedApi.mock.calls.some(c => String(c[0]).includes("scan_history"))).toBe(false)
  })

  it("uses the status renderer when null status is present and the shape includes a status column", async () => {
    const scansWithNullStatus = [{ ...scans[0], status: null as unknown as string }]
    installBaseApiMocks(mockedApi, url => {
      if (url === `/api/companies/scan_history?candidate_id=${candidateId}`) {
        return jsonResponse(scansWithNullStatus)
      }
      if (url === "/api/shapes/companies") {
        return jsonResponse({ list: { watch_history: companyColumns.watch_history } })
      }
      throw new Error(url)
    })
    renderWithProviders(<CompaniesWatchHistory />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())
    // Custom status render: falsy val takes the `|| ""` fallback (branch coverage).
    expect(screen.getByRole("columnheader", { name: "Status" })).toBeInTheDocument()
  })

  it("does not attach the status colour renderer when the shape omits a status column", async () => {
    const scansWithNullStatus = [{ ...scans[0], status: null as unknown as string }]
    installBaseApiMocks(mockedApi, url => {
      if (url === `/api/companies/scan_history?candidate_id=${candidateId}`) {
        return jsonResponse(scansWithNullStatus)
      }
      if (url === "/api/shapes/companies") {
        return jsonResponse({ list: { watch_history: [{ key: "company_name", label: "Company" }] } })
      }
      throw new Error(url)
    })
    renderWithProviders(<CompaniesWatchHistory />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())
    expect(screen.queryByRole("columnheader", { name: "Status" })).not.toBeInTheDocument()
  })

  it("treats null shapes payload as empty columns", async () => {
    installBaseApiMocks(mockedApi, url => {
      if (url === `/api/companies/scan_history?candidate_id=${candidateId}`) {
        return jsonResponse(scans)
      }
      if (url === "/api/shapes/companies") {
        return jsonResponse(null as unknown as Record<string, unknown>)
      }
      throw new Error(url)
    })
    renderWithProviders(<CompaniesWatchHistory />)
    // Rows load but ListPage renders zero data cells when column defs are empty — no "Acme Corp" text.
    await waitFor(() => expect(screen.queryByText("Loading...")).not.toBeInTheDocument())
    expect(screen.getByRole("heading", { name: "Watch History" })).toBeInTheDocument()
    expect(screen.getByRole("table").querySelectorAll("tbody tr")).toHaveLength(scans.length)
  })
})
