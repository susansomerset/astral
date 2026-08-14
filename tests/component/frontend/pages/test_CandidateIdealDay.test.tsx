import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CandidateIdealDay from "../../../../src/ui/frontend/src/pages/CandidateIdealDay"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("CandidateIdealDay — AST-1366 Ideal Day edit surface", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }],
        } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: { context: { ideal_day: "deep focus mornings" } },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        const body = JSON.parse(String(init.body || "{}"))
        return {
          ok: true,
          json: async () => ({ candidate_data: body }),
        } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
  })

  it("renders Ideal Day context editor (§6c routed page)", async () => {
    renderWithProviders(<CandidateIdealDay />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Ideal Day" })).toBeInTheDocument(),
    )
    expect(screen.getByRole("textbox")).toHaveValue("deep focus mornings")
  })

  it("saves context.ideal_day via PUT /data merge", async () => {
    const puts: unknown[] = []
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }],
        } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: { context: { ideal_day: "deep focus mornings" } },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        const body = JSON.parse(String(init.body || "{}"))
        puts.push(body)
        return { ok: true, json: async () => ({ candidate_data: body }) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })

    renderWithProviders(<CandidateIdealDay />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Ideal Day" })).toBeInTheDocument(),
    )
    await userEvent.clear(screen.getByRole("textbox"))
    await userEvent.type(screen.getByRole("textbox"), "quiet maker mornings")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Ideal Day saved")).toBeInTheDocument())
    expect(puts).toEqual([{ context: { ideal_day: "quiet maker mornings" } }])
  })
})
