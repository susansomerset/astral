import { screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import ArtifactsJobListCriteria from "../../../../src/ui/frontend/src/pages/ArtifactsJobListCriteria"
import { STATE_UI_MANIFEST_FIXTURE } from "../fixtures/stateUiManifestFixture"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

describe("ArtifactsJobListCriteria", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") {
        return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
      }
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }] } as Response
      }
      if (/\/api\/candidates\/[^/]+\/generate\/[^/]+\/pending$/.test(url)) {
        return {
          ok: false,
          status: 404,
          json: async () => ({ error: "No recoverable generation" }),
        } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                joblist_rubric: [{ label: "Title", content: "Engineer", importance: 4 }],
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

  it("renders job list criteria editor", async () => {
    renderWithProviders(<ArtifactsJobListCriteria />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Job List Criteria" })).toBeInTheDocument())
  })

  it("AST-1200: criterion prompt textarea visible without expand click", async () => {
    renderWithProviders(<ArtifactsJobListCriteria />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Job List Criteria" })).toBeInTheDocument())
    const field = await screen.findByDisplayValue("Engineer")
    expect(field.closest(".collapsible-panel-body")).not.toHaveAttribute("hidden")
  })
})