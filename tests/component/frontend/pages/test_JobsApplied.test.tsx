import { screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import JobsApplied from "../../../../src/ui/frontend/src/pages/JobsApplied"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("JobsApplied", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    mockedApi.mockResolvedValue({
      json: async () => ({ column_types: {} }),
    } as Response)
  })

  it("renders applied jobs list shell", async () => {
    renderWithProviders(<JobsApplied />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Applied" })).toBeInTheDocument())
    expect(screen.getByText("No records found.")).toBeInTheDocument()
  })
})
