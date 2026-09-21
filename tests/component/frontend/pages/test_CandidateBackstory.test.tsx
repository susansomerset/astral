import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CandidateBackstory from "../../../../src/ui/frontend/src/pages/CandidateBackstory"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("CandidateBackstory — AST-1663 plain_text ContextTextPage", () => {
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
            candidate_data: { context: { backstory: "career pivot" } },
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

  it("AST-1663: renders Backstory editor (§6c routed page)", async () => {
    renderWithProviders(<CandidateBackstory />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Backstory" })).toBeInTheDocument(),
    )
    expect(screen.getByRole("textbox")).toHaveValue("career pivot")
  })

  it("AST-1663: save PUT context.backstory and reloads same text", async () => {
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
            candidate_data: { context: { backstory: "career pivot" } },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        const body = JSON.parse(String(init.body || "{}"))
        puts.push(body)
        return {
          ok: true,
          json: async () => ({
            candidate_data: { context: { backstory: body.context.backstory } },
          }),
        } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })

    renderWithProviders(<CandidateBackstory />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Backstory" })).toBeInTheDocument(),
    )
    await userEvent.clear(screen.getByRole("textbox"))
    await userEvent.type(screen.getByRole("textbox"), "grew up fixing bikes")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Backstory saved")).toBeInTheDocument())
    expect(puts).toEqual([{ context: { backstory: "grew up fixing bikes" } }])
    expect(screen.getByRole("textbox")).toHaveValue("grew up fixing bikes")
  })

  it("AST-1663: empty draft disables Save (plain_text bodyShape)", async () => {
    renderWithProviders(<CandidateBackstory />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Backstory" })).toBeInTheDocument(),
    )
    await userEvent.clear(screen.getByRole("textbox"))
    expect(screen.getByRole("button", { name: "Save" })).toBeDisabled()
    expect(
      mockedApi.mock.calls.every(
        ([url, init]) => !(url.includes("/data") && init?.method === "PUT"),
      ),
    ).toBe(true)
  })

  it("AST-1663: page hardcodes bodyShape plain_text; ArtifactEditor untouched", async () => {
    const { readFileSync } = await import("node:fs")
    const { resolve } = await import("node:path")
    const src = readFileSync(
      resolve(__dirname, "../../../../src/ui/frontend/src/pages/CandidateBackstory.tsx"),
      "utf8",
    )
    expect(src).toMatch(/bodyShape="plain_text"/)
    expect(src).toMatch(/contextKey="backstory"/)
    expect(src).not.toMatch(/ArtifactEditor/)
  })
})
