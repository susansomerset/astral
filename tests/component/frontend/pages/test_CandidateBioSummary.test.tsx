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

  it("AST-2068 AC4: Bio Summary unsaved draft saves before a move; arrows step back, re-hydrate, disable at ends", async () => {
    // Fake server: uuid-keyed versions; a save appends a version and makes it current.
    const bodies: Record<string, string> = { "u-1": "bio v1", "u-2": "bio v2" }
    const order = ["u-1", "u-2"]
    let current = "u-2"
    const map = () =>
      Object.fromEntries(order.map((u, i) => [u, { created_at: "t", current: u === current ? 1 : 0, position: i + 1 }]))
    const base = "/api/candidates/c1/artifacts/candidate.context.bio_summary"
    const calls: string[] = []
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return { json: async () => ({ candidate_data: { context: { bio_summary: bodies[current] } } }) } as Response
      }
      if (url === `${base}/versions`) return { ok: true, json: async () => ({ versions: map() }) } as Response
      if (url === `${base}/current` && init?.method === "PUT") {
        calls.push("move")
        current = JSON.parse(String(init.body)).artifact_uuid
        return { ok: true, json: async () => ({ current, versions: map() }) } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        calls.push("save")
        const text = JSON.parse(String(init.body)).context.bio_summary
        const uid = `u-${order.length + 1}`
        bodies[uid] = text
        order.push(uid)
        current = uid
        return { ok: true, json: async () => ({ candidate_data: { context: { bio_summary: text } } }) } as Response
      }
      throw new Error(`unexpected api call: ${url} ${init?.method ?? "GET"}`)
    })
    renderWithProviders(<CandidateBioSummary />)
    await screen.findByDisplayValue("bio v2")
    expect(await screen.findByText("2 of 2")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Next version" })).toBeDisabled()
    // Unsaved draft + back: saves the draft as v3 first, then steps back from it to v2 (the version on screen).
    const box = screen.getByRole("textbox")
    await userEvent.clear(box)
    await userEvent.type(box, "bio draft")
    await userEvent.click(screen.getByRole("button", { name: "Previous version" }))
    await waitFor(() => expect(calls).toEqual(["save", "move"]))
    await screen.findByDisplayValue("bio v2")
    expect(screen.getByText("2 of 3")).toBeInTheDocument()
    expect(bodies["u-3"]).toBe("bio draft")
    // Clean back: no save, previous body, back disabled at 1 of N.
    await userEvent.click(screen.getByRole("button", { name: "Previous version" }))
    await screen.findByDisplayValue("bio v1")
    expect(screen.getByText("1 of 3")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Previous version" })).toBeDisabled()
    expect(calls).toEqual(["save", "move", "move"])
  })
})
