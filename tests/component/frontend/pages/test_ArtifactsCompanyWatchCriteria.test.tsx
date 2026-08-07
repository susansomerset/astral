import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import ArtifactsCompanyWatchCriteria from "../../../../src/ui/frontend/src/pages/ArtifactsCompanyWatchCriteria"
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

function pendingNotFoundResponse(): Response {
  return {
    ok: false,
    status: 404,
    json: async () => ({ error: "No recoverable generation" }),
  } as Response
}

describe("ArtifactsCompanyWatchCriteria", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    installPageApiMocks(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }],
        } as Response
      }
      if (/\/api\/candidates\/[^/]+\/generate\/[^/]+\/pending$/.test(url)) {
        return pendingNotFoundResponse()
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                company_prefilter: [{ label: "Stage", content: "Series B", importance: 5 }],
              },
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        return { ok: true, json: async () => ({}) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
  })

  it("renders company watch criteria editor", async () => {
    renderWithProviders(<ArtifactsCompanyWatchCriteria />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Company Watch Criteria" })).toBeInTheDocument())
  })

  it("AST-1253: Regenerate Yes POSTs generate_artifacts (chain handoff)", async () => {
    let generateUrl = ""
    installPageApiMocks(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }],
        } as Response
      }
      if (/\/api\/candidates\/[^/]+\/generate\/[^/]+\/pending$/.test(url)) {
        return pendingNotFoundResponse()
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                company_prefilter: [{ label: "Stage", content: "Series B", importance: 5 }],
              },
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/generate_artifacts" && init?.method === "POST") {
        generateUrl = url
        return { ok: true, json: async () => ({ ok: true, state: "REQUESTED_ARTIFACTS" }) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })

    renderWithProviders(<ArtifactsCompanyWatchCriteria />)
    await waitFor(() => expect(screen.getByRole("button", { name: "Regenerate" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Regenerate" }))
    expect(screen.getByText(/Reset all artifact rubrics/i)).toBeInTheDocument()
    expect(screen.getByText(/Job Description Criteria/)).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Yes" }))
    await waitFor(() => expect(generateUrl).toBe("/api/candidates/c1/generate_artifacts"))
    await waitFor(() =>
      expect(screen.getByText("Artifacts build requested — watch Execution History")).toBeInTheDocument(),
    )
  })
})
