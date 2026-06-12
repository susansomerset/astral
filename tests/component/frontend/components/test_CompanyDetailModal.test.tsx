import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CompanyDetailModal from "../../../../src/ui/frontend/src/components/CompanyDetailModal"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const company = {
  short_name: "acme",
  company_name: "Acme Corp",
  company_website: "https://acme.test",
  job_site: "https://jobs.acme.test",
  state: "ACTIVE",
  last_scan_at: "2026-01-01T00:00:00Z",
  prefilter_company_notes: "note",
  state_history: [{ to_state: "ACTIVE", timestamp: "2026-01-01T00:00:00Z" }],
  job_state_counts: { NEW: 2, CLOSED: 1 },
  agent_story: [{ task_key: "scan", blocks: [{ type: "PROMPT", id: "1", content: "ok" }] }],
}

describe("CompanyDetailModal", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  it("loads, edits, and saves an editable company", async () => {
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { json: async () => [] } as Response
      }
      if (url === "/api/companies/acme" && !init) {
        return { json: async () => company } as Response
      }
      if (url === "/api/companies/acme" && init?.method === "PUT") {
        return { ok: true, json: async () => ({}) } as Response
      }
      throw new Error(url)
    })
    const onClose = vi.fn()
    const onSaved = vi.fn()
    renderWithProviders(<CompanyDetailModal shortName="acme" onClose={onClose} onSaved={onSaved} />)
    await waitFor(() => expect(screen.getByDisplayValue("Acme Corp")).toBeInTheDocument())
    await userEvent.clear(screen.getByDisplayValue("Acme Corp"))
    await userEvent.type(screen.getByDisplayValue(""), "Acme Updated")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(onSaved).toHaveBeenCalled())
    expect(onClose).toHaveBeenCalled()
    await userEvent.click(screen.getByText("scan"))
    expect(screen.getByDisplayValue("ok")).toBeInTheDocument()
  })

  it("renders readonly watch companies", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/candidates") {
        return { json: async () => [] } as Response
      }
      if (url === "/api/companies/acme") {
        return { json: async () => ({ ...company, state: "WATCH", job_state_counts: {} }) } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(<CompanyDetailModal shortName="acme" onClose={() => {}} onSaved={() => {}} />)
    await waitFor(() => expect(screen.getByText("No jobs tracked yet.")).toBeInTheDocument())
    expect(screen.queryByRole("button", { name: "Save" })).not.toBeInTheDocument()
  })

  it("handles load and save failures", async () => {
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { json: async () => [] } as Response
      }
      if (url === "/api/companies/bad" && !init) {
        throw new Error("network")
      }
      if (url === "/api/companies/acme" && !init) {
        return { json: async () => company } as Response
      }
      if (url === "/api/companies/acme" && init?.method === "PUT") {
        return { ok: false, json: async () => ({ error: "bad save" }) } as Response
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
