import { screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import JobsResponded from "../../../../src/ui/frontend/src/pages/JobsResponded"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("JobsResponded", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    mockedApi.mockResolvedValue({
      json: async () => ({ column_types: {} }),
    } as Response)
  })

  it("renders responded jobs list shell", async () => {
    renderWithProviders(<JobsResponded />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Responded" })).toBeInTheDocument())
    expect(screen.getByText("No records found.")).toBeInTheDocument()
  })
})
