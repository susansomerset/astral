import { screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import ArtifactsJobListCriteria from "../../../../src/ui/frontend/src/pages/ArtifactsJobListCriteria"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("ArtifactsJobListCriteria", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }] } as Response
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
})
