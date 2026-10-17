import { cleanup, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import { formatCell } from "../../../../src/ui/frontend/src/lib/fmt"
import CompaniesWatchList from "../../../../src/ui/frontend/src/pages/CompaniesWatchList"
import { renderWithProviders } from "../test-utils"
import { candidateId, companyListHandler, installBaseApiMocks, jsonResponse } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

vi.mock("../../../../src/ui/frontend/src/components/JobDetailModal", () => ({
  default: (props: { jobId: string | null; onClose: () => void; stacked?: boolean }) =>
    props.jobId == null ? null : (
      <div data-testid="job-detail-probe">
        JobDetailModal:{props.jobId}:stacked={String(!!props.stacked)}
        <button type="button" onClick={props.onClose}>Close job</button>
      </div>
    ),
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

/** Minimal AST-2320 watch_list shapes for §6c dates / counts / modal wiring. */
const watchListShapeCols = [
  { key: "company_name", label: "Company", sortable: true },
  { key: "best_fit_label", label: "Best Fit", sortable: true },
  { key: "best_fit_at", label: "Best Fit Date", sortable: true, type: "datetime" },
  { key: "jobs", label: "Jobs", sortable: true, type: "int" },
  { key: "jl", label: "JL", sortable: true, type: "int" },
  { key: "active", label: "ACTIVE", sortable: true, type: "int" },
]

const enrichedCompanies = [
  {
    short_name: "acme",
    company_name: "Acme Corp",
    state: "WATCH",
    best_fit_label: "ACTIVE",
    best_fit_at: "2026-03-15T12:00:00Z",
    jobs: 12,
    jl: 0,
    active: 10,
    active_newest_at: "2026-03-15T12:00:00Z",
  },
  {
    short_name: "beta",
    company_name: "Beta Inc",
    state: "WATCH",
    best_fit_label: "JL",
    best_fit_at: "2026-02-01T00:00:00Z",
    jobs: 3,
    jl: 9,
    active: 2,
    active_newest_at: "2026-01-20T00:00:00Z",
  },
]

function enrichedWatchListHandler(
  extra?: (url: string, init?: RequestInit) => Promise<Response> | Response | undefined,
) {
  return (url: string, init?: RequestInit) => {
    const fromExtra = extra?.(url, init)
    if (fromExtra !== undefined) return fromExtra
    if (url === `/api/companies?view=watch_list&candidate_id=${candidateId}`) {
      return jsonResponse(enrichedCompanies)
    }
    if (url === "/api/shapes/companies") {
      return jsonResponse({ list: { watch_list: watchListShapeCols } })
    }
    if (url.startsWith("/api/companies/") && url.includes("/jobs?")) {
      return jsonResponse([])
    }
    if (url.startsWith("/api/companies/") && !url.includes("bulk_state") && !url.includes("/add")) {
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
    throw new Error(`unexpected api call: ${url}`)
  }
}

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

  it("AST-2321: ignore-only bulk; no Retry Scrape", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/companies/bulk_state" && init?.method === "POST") {
        return jsonResponse({ updated: 1 })
      }
      return companyListHandler("watch_list", companies, "watch_list")(url)
    })
    renderWithProviders(<CompaniesWatchList />)
    await waitFor(() => expect(screen.getByText("Beta Inc")).toBeInTheDocument())

    await userEvent.click(within(screen.getByRole("row", { name: /Acme Corp/ })).getByRole("checkbox"))
    expect(screen.queryByRole("button", { name: "Retry Scrape" })).not.toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Set to Ignore" })).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Set to Ignore" }))
    await waitFor(() => expect(screen.getByText("1 companies updated")).toBeInTheDocument())
    const bulkCall = mockedApi.mock.calls.find(([u]) => u === "/api/companies/bulk_state")
    expect(JSON.parse(String(bulkCall?.[1]?.body))).toEqual({
      short_names: ["acme"],
      to_state: "IGNORE",
    })
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
    // Row checkbox (not "Show dates" / select-all) — index 0 is the dates toggle.
    await userEvent.click(within(screen.getByRole("row", { name: /Acme Corp/ })).getByRole("checkbox"))
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
      if (url === "/api/ui_config") {
        return jsonResponse({ column_types: {} })
      }
      throw new Error(url)
    })
    renderWithProviders(<CompaniesWatchList />)
    await waitFor(() => expect(screen.getByText("Loading...")).toBeInTheDocument())
    expect(mockedApi.mock.calls.some(call => String(call[0]).includes(`view=watch_list&candidate_id=${candidateId}`))).toBe(false)
  })

  it("AST-2322: Add Company posts careers URL as job_site and toasts short_name", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/companies/add" && init?.method === "POST") {
        return jsonResponse({ short_name: "acme_co", state: "TEST_WATCH" }, { ok: true, status: 201 })
      }
      return companyListHandler("watch_list", companies, "watch_list")(url)
    })
    renderWithProviders(<CompaniesWatchList />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Add Company" }))
    expect(screen.getByRole("heading", { name: "Add Company" })).toBeInTheDocument()
    expect(screen.getByText("Careers Page URL")).toBeInTheDocument()
    await userEvent.type(screen.getByLabelText("Company Name"), "Acme Co")
    await userEvent.type(screen.getByLabelText("Website"), "https://acme.test")
    await userEvent.type(screen.getByLabelText("Careers Page URL"), "https://acme.test/careers")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Added acme_co (TEST_WATCH)")).toBeInTheDocument())
    const addCall = mockedApi.mock.calls.find(([url]) => url === "/api/companies/add")
    expect(JSON.parse(String(addCall?.[1]?.body))).toEqual({
      candidate_id: candidateId,
      company_name: "Acme Co",
      company_website: "https://acme.test",
      job_site: "https://acme.test/careers",
    })
  })

  it("AST-2322: Add Company failure toasts error", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/companies/add" && init?.method === "POST") {
        return jsonResponse({ error: "job_site required" }, { ok: false, status: 400 })
      }
      return companyListHandler("watch_list", companies, "watch_list")(url)
    })
    renderWithProviders(<CompaniesWatchList />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Add Company" }))
    await userEvent.type(screen.getByLabelText("Company Name"), "Acme Co")
    await userEvent.type(screen.getByLabelText("Website"), "https://acme.test")
    await userEvent.type(screen.getByLabelText("Careers Page URL"), "https://acme.test/careers")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Add company failed")).toBeInTheDocument())
  })

  it("AST-2321: Show dates toggles count cell format", async () => {
    installBaseApiMocks(mockedApi, enrichedWatchListHandler())
    renderWithProviders(<CompaniesWatchList />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())

    const acmeRow = screen.getByRole("row", { name: /Acme Corp/ })
    // Toggle off (default): plain count; zero JL is not a button
    expect(within(acmeRow).getByRole("button", { name: "10" })).toBeInTheDocument()
    expect(within(acmeRow).queryByRole("button", { name: "0" })).not.toBeInTheDocument()
    expect(within(acmeRow).getByText("0")).toBeInTheDocument()

    await userEvent.click(screen.getByRole("checkbox", { name: /Show dates/i }))
    const expectedDate = formatCell("2026-03-15T12:00:00Z", "date")
    expect(within(acmeRow).getByRole("button", { name: `10 (${expectedDate})` })).toBeInTheDocument()
  })

  it("AST-2321: ACTIVE header sorts numerically (10 after 2)", async () => {
    installBaseApiMocks(mockedApi, enrichedWatchListHandler())
    renderWithProviders(<CompaniesWatchList />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())

    // Default company_name asc → Acme then Beta; ACTIVE values are 10 then 2.
    const before = screen.getAllByRole("row").slice(1).map(r => r.textContent ?? "")
    expect(before[0]).toContain("Acme Corp")
    expect(before[1]).toContain("Beta Inc")

    await userEvent.click(screen.getByRole("columnheader", { name: "ACTIVE" }))
    const after = screen.getAllByRole("row").slice(1).map(r => r.textContent ?? "")
    // Asc by ACTIVE: Beta (2) then Acme (10) — proves numeric, not lexicographic "10" before "2".
    expect(after[0]).toContain("Beta Inc")
    expect(after[1]).toContain("Acme Corp")
  })

  it("AST-2321: count click opens jobs modal then stacked job detail", async () => {
    const jobsUrl =
      `/api/companies/acme/jobs?bucket=active&candidate_id=${candidateId}`
    installBaseApiMocks(
      mockedApi,
      enrichedWatchListHandler((url) => {
        if (url === jobsUrl) {
          return jsonResponse([
            {
              astral_job_id: "j1",
              job_title: "Staff Eng",
              state: "ACTIVE",
              state_changed_at: "2026-03-15T12:00:00Z",
            },
            {
              astral_job_id: "j2",
              job_title: "PM",
              state: "ACTIVE",
              state_changed_at: "2026-03-14T12:00:00Z",
            },
          ])
        }
        return undefined
      }),
    )
    renderWithProviders(<CompaniesWatchList />)
    await waitFor(() => expect(screen.getByText("Acme Corp")).toBeInTheDocument())

    await userEvent.click(
      within(screen.getByRole("row", { name: /Acme Corp/ })).getByRole("button", { name: "10" }),
    )
    expect(await screen.findByRole("heading", { name: "ACTIVE — acme" })).toBeInTheDocument()
    expect(screen.getByText("Staff Eng")).toBeInTheDocument()
    expect(screen.getByText("PM")).toBeInTheDocument()
    // Count click must not open company detail
    expect(mockedApi.mock.calls.every(([u]) => u !== "/api/companies/acme")).toBe(true)

    await userEvent.click(screen.getByText("Staff Eng"))
    expect(screen.getByTestId("job-detail-probe").textContent).toContain(
      "JobDetailModal:j1:stacked=true",
    )
  })
})
