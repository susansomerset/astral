import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CandidateBioSummary from "../../../../src/ui/frontend/src/pages/CandidateBioSummary"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("CandidateBioSummary — AST-1650 plain_text ContextTextPage", () => {
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
            candidate_data: { context: { bio_summary: "builder bio" } },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        const body = JSON.parse(String(init.body || "{}"))
        return { ok: true, json: async () => ({ candidate_data: body }) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
  })

  it("AST-1650: renders Bio Summary editor (§6c routed page)", async () => {
    renderWithProviders(<CandidateBioSummary />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Bio Summary" })).toBeInTheDocument(),
    )
    expect(screen.getByRole("textbox")).toHaveValue("builder bio")
  })

  it("AST-1650: save PUT context.bio_summary and reloads same text", async () => {
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
            candidate_data: { context: { bio_summary: "builder bio" } },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        const body = JSON.parse(String(init.body || "{}"))
        puts.push(body)
        return {
          ok: true,
          json: async () => ({
            candidate_data: { context: { bio_summary: body.context.bio_summary } },
          }),
        } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })

    renderWithProviders(<CandidateBioSummary />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Bio Summary" })).toBeInTheDocument(),
    )
    await userEvent.clear(screen.getByRole("textbox"))
    await userEvent.type(screen.getByRole("textbox"), "fresh bio text")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Bio Summary saved")).toBeInTheDocument())
    expect(puts).toEqual([{ context: { bio_summary: "fresh bio text" } }])
    expect(screen.getByRole("textbox")).toHaveValue("fresh bio text")
  })

  it("AST-1650: empty draft disables Save (plain_text bodyShape)", async () => {
    renderWithProviders(<CandidateBioSummary />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Bio Summary" })).toBeInTheDocument(),
    )
    await userEvent.clear(screen.getByRole("textbox"))
    expect(screen.getByRole("button", { name: "Save" })).toBeDisabled()
    expect(mockedApi.mock.calls.every(([url, init]) => !(url.includes("/data") && init?.method === "PUT"))).toBe(
      true,
    )
  })
})
