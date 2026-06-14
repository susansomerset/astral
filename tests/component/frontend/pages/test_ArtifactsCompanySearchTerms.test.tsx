import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import ArtifactsCompanySearchTerms from "../../../../src/ui/frontend/src/pages/ArtifactsCompanySearchTerms"
import { STATE_UI_MANIFEST_FIXTURE } from "../fixtures/stateUiManifestFixture"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

function installPageApiMocks(handler: (url: string, init?: RequestInit) => Promise<Response> | Response) {
  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    if (url === "/api/me") {
      return { json: async () => ({ user_id: "u1", name: "Test User", is_admin: true }) } as Response
    }
    if (url === "/api/state_ui_manifest") {
      return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
    }
    return handler(url, init)
  })
}

describe("ArtifactsCompanySearchTerms", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    installPageApiMocks(async (url: string, init?: RequestInit) => {
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

  it("AST-645: Generate button uses in-flight class while generating", async () => {
    let resolveGenerate!: (value: Response) => void
    const generatePromise = new Promise<Response>((resolve) => {
      resolveGenerate = resolve
    })
    installPageApiMocks(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "CONTEXT_READY", candidate_data: {} }],
        } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return { json: async () => ({ company_search_terms: "", candidate_data: {} }) } as Response
      }
      if (url === "/api/candidates/c1/generate/craft_company_search_terms" && init?.method === "POST") {
        return generatePromise
      }
      throw new Error(`unexpected api call: ${url}`)
    })

    renderWithProviders(<ArtifactsCompanySearchTerms />)
    const generateBtn = await screen.findByRole("button", { name: "Generate" })
    expect(generateBtn).not.toHaveClass("in-flight")
    await userEvent.click(generateBtn)
    await waitFor(() => expect(generateBtn).toHaveClass("in-flight"))
    expect(screen.getByRole("button", { name: "Save" })).not.toHaveClass("in-flight")
    resolveGenerate({
      ok: true,
      json: async () => ({
        success: true,
        parsed_response: { search_terms: "generated term one\ngenerated term two" },
      }),
    } as Response)
    await waitFor(() => expect(generateBtn).not.toHaveClass("in-flight"))
  })

  it("populates textarea after generate when empty", async () => {
    installPageApiMocks(async (url: string, init?: RequestInit) => {
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
