import { screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import ArtifactsLikeJobCriteria from "../../../../src/ui/frontend/src/pages/ArtifactsLikeJobCriteria"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("ArtifactsLikeJobCriteria", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "CONTEXT_READY", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                like_rubric: [{ label: "Culture", content: "Collaborative", importance: 2 }],
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

  it("renders like job criteria editor", async () => {
    renderWithProviders(<ArtifactsLikeJobCriteria />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Like Job Criteria" })).toBeInTheDocument())
  })
})
