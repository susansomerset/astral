import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CompanyDetailModal from "../../../../src/ui/frontend/src/components/CompanyDetailModal"
import { renderWithProviders } from "../test-utils"
import { installBaseApiMocks, jsonResponse } from "../pages/page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const company = {
  short_name: "acme",
  company_name: "Acme Corp",
  company_website: "https://acme.test",
  job_site: "https://jobs.acme.test",
  state: "NEW",
  last_scan_at: "2026-01-01T00:00:00Z",
  prefilter_company_notes: "note",
  originating_search_term: "fintech startups",
  state_history: [{ to_state: "NEW", timestamp: "2026-01-01T00:00:00Z" }],
  job_state_counts: { NEW: 2, CLOSED: 1 },
  agent_story: [{ task_key: "scan", blocks: [{ type: "PROMPT", id: "1", content: "ok" }] }],
}

describe("CompanyDetailModal", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("loads, edits, and saves an editable company", async () => {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/companies/acme" && !init) {
        return jsonResponse(company)
      }
      if (url === "/api/companies/acme" && init?.method === "PUT") {
        return jsonResponse({})
      }
      throw new Error(url)
    })
    const onClose = vi.fn()
    const onSaved = vi.fn()
    renderWithProviders(<CompanyDetailModal shortName="acme" onClose={onClose} onSaved={onSaved} />)
    await waitFor(() => expect(screen.getByDisplayValue("Acme Corp")).toBeInTheDocument())
    expect(screen.getByText("Originating Search Term")).toBeInTheDocument()
    expect(screen.getByText("fintech startups")).toBeInTheDocument()
    await userEvent.clear(screen.getByDisplayValue("Acme Corp"))
    await userEvent.type(screen.getByDisplayValue(""), "Acme Updated")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(onSaved).toHaveBeenCalled())
    expect(onClose).toHaveBeenCalled()
    const putCall = mockedApi.mock.calls.find(
      ([url, init]) => url === "/api/companies/acme" && init?.method === "PUT",
    )
    expect(putCall).toBeTruthy()
    const putBody = JSON.parse(String(putCall![1]?.body))
    expect(putBody).not.toHaveProperty("originating_search_term")
    expect(putBody).toMatchObject({ company_name: "Acme Updated" })
    await userEvent.click(screen.getByText("scan"))
    expect(screen.getByDisplayValue("ok")).toBeInTheDocument()
  })

  it("shows em dash when originating search term is missing", async () => {
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url === "/api/companies/acme") {
        return jsonResponse({ ...company, originating_search_term: null })
      }
      throw new Error(url)
    })
    renderWithProviders(<CompanyDetailModal shortName="acme" onClose={() => {}} onSaved={() => {}} />)
    await waitFor(() => expect(screen.getByText("Originating Search Term")).toBeInTheDocument())
    const row = screen.getByText("Originating Search Term").closest("div")
    expect(row?.textContent).toContain("—")
  })

  it("renders readonly watch companies", async () => {
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url === "/api/companies/acme") {
        return jsonResponse({ ...company, state: "WATCH", job_state_counts: {} })
      }
      throw new Error(url)
    })
    renderWithProviders(<CompanyDetailModal shortName="acme" onClose={() => {}} onSaved={() => {}} />)
    await waitFor(() => expect(screen.getByText("No jobs tracked yet.")).toBeInTheDocument())
    expect(screen.queryByRole("button", { name: "Save" })).not.toBeInTheDocument()
  })

  it("handles load and save failures", async () => {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/companies/bad" && !init) {
        throw new Error("network")
      }
      if (url === "/api/companies/acme" && !init) {
        return jsonResponse(company)
      }
      if (url === "/api/companies/acme" && init?.method === "PUT") {
        return jsonResponse({ error: "bad save" }, { ok: false })
      }
      throw new Error(url)
    })
    renderWithProviders(<CompanyDetailModal shortName="bad" onClose={() => {}} onSaved={() => {}} />)
    await waitFor(() => expect(screen.getByText("Failed to load company")).toBeInTheDocument())

    renderWithProviders(<CompanyDetailModal shortName="acme" onClose={() => {}} onSaved={() => {}} />)
    await waitFor(() => expect(screen.getByDisplayValue("Acme Corp")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("bad save")).toBeInTheDocument())
  })
})
