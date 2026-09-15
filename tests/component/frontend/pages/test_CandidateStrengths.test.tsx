import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CandidateStrengths from "../../../../src/ui/frontend/src/pages/CandidateStrengths"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("CandidateStrengths — AST-1634 plain_text ContextTextPage", () => {
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
            candidate_data: { context: { strengths: "leadership" } },
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

  it("AST-1634: renders Strengths editor (§6c routed page)", async () => {
    renderWithProviders(<CandidateStrengths />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Strengths" })).toBeInTheDocument(),
    )
    expect(screen.getByRole("textbox")).toHaveValue("leadership")
  })

  it("AST-1634: save PUT context.strengths and reloads same text", async () => {
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
            candidate_data: { context: { strengths: "leadership" } },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        const body = JSON.parse(String(init.body || "{}"))
        puts.push(body)
        return {
          ok: true,
          json: async () => ({
            candidate_data: { context: { strengths: body.context.strengths } },
          }),
        } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })

    renderWithProviders(<CandidateStrengths />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Strengths" })).toBeInTheDocument(),
    )
    await userEvent.clear(screen.getByRole("textbox"))
    await userEvent.type(screen.getByRole("textbox"), "systems thinker")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Strengths saved")).toBeInTheDocument())
    expect(puts).toEqual([{ context: { strengths: "systems thinker" } }])
    expect(screen.getByRole("textbox")).toHaveValue("systems thinker")
  })

  it("AST-1634: empty draft disables Save (plain_text bodyShape)", async () => {
    renderWithProviders(<CandidateStrengths />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Strengths" })).toBeInTheDocument(),
    )
    await userEvent.clear(screen.getByRole("textbox"))
    expect(screen.getByRole("button", { name: "Save" })).toBeDisabled()
    expect(mockedApi.mock.calls.every(([url, init]) => !(url.includes("/data") && init?.method === "PUT"))).toBe(
      true,
    )
  })
})
