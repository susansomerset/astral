import { screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CandidateBackstory from "../../../../src/ui/frontend/src/pages/CandidateBackstory"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("CandidateBackstory", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return { json: async () => ({ candidate_data: { context: { backstory: "career pivot" } } }) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
  })

  it("renders backstory context editor", async () => {
    renderWithProviders(<CandidateBackstory />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Backstory" })).toBeInTheDocument())
    expect(screen.getByRole("textbox")).toHaveValue("career pivot")
  })
})
