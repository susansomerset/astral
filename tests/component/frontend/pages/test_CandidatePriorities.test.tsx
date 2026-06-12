import { screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CandidatePriorities from "../../../../src/ui/frontend/src/pages/CandidatePriorities"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("CandidatePriorities", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return { json: async () => ({ candidate_data: { context: { priorities: "remote work" } } }) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
  })

  it("renders priorities context editor", async () => {
    renderWithProviders(<CandidatePriorities />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Priorities" })).toBeInTheDocument())
    expect(screen.getByRole("textbox")).toHaveValue("remote work")
  })
})
