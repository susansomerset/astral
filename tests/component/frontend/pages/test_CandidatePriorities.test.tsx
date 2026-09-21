import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CandidatePriorities from "../../../../src/ui/frontend/src/pages/CandidatePriorities"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("CandidatePriorities — AST-1653 plain_text ContextTextPage", () => {
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
            candidate_data: { context: { priorities: "remote work" } },
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

  it("AST-1653: renders Priorities editor (§6c routed page)", async () => {
    renderWithProviders(<CandidatePriorities />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Priorities" })).toBeInTheDocument(),
    )
    expect(screen.getByRole("textbox")).toHaveValue("remote work")
  })

  it("AST-1653: save PUT context.priorities and reloads same text", async () => {
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
            candidate_data: { context: { priorities: "remote work" } },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        const body = JSON.parse(String(init.body || "{}"))
        puts.push(body)
        return {
          ok: true,
          json: async () => ({
            candidate_data: { context: { priorities: body.context.priorities } },
          }),
        } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })

    renderWithProviders(<CandidatePriorities />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Priorities" })).toBeInTheDocument(),
    )
    await userEvent.clear(screen.getByRole("textbox"))
    await userEvent.type(screen.getByRole("textbox"), "mission-driven teams")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Priorities saved")).toBeInTheDocument())
    expect(puts).toEqual([{ context: { priorities: "mission-driven teams" } }])
    expect(screen.getByRole("textbox")).toHaveValue("mission-driven teams")
  })

  it("AST-1653: empty draft disables Save (plain_text bodyShape)", async () => {
    renderWithProviders(<CandidatePriorities />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Priorities" })).toBeInTheDocument(),
    )
    await userEvent.clear(screen.getByRole("textbox"))
    expect(screen.getByRole("button", { name: "Save" })).toBeDisabled()
    expect(
      mockedApi.mock.calls.every(
        ([url, init]) => !(url.includes("/data") && init?.method === "PUT"),
      ),
    ).toBe(true)
  })

  it("AST-1653: page hardcodes bodyShape plain_text; ArtifactEditor untouched", async () => {
    const { readFileSync } = await import("node:fs")
    const { resolve } = await import("node:path")
    const src = readFileSync(
      resolve(__dirname, "../../../../src/ui/frontend/src/pages/CandidatePriorities.tsx"),
      "utf8",
    )
    expect(src).toMatch(/bodyShape="plain_text"/)
    expect(src).toMatch(/contextKey="priorities"/)
    expect(src).not.toMatch(/ArtifactEditor/)
  })
})
