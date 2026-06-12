import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import * as CandidateContext from "../../../../src/ui/frontend/src/contexts/CandidateContext"
import api from "../../../../src/ui/frontend/src/lib/api"
import ContextTextPage from "../../../../src/ui/frontend/src/components/ContextTextPage"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

function mockCandidates(contextValue: unknown) {
  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    if (url === "/api/candidates") {
      return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
    }
    if (url === "/api/candidates/c1" && !init) {
      return { json: async () => ({ candidate_data: { context: { story: contextValue } } }) } as Response
    }
    if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
      return { ok: true, json: async () => ({ candidate_data: { context: { story: "saved text" } } }) } as Response
    }
    throw new Error(`unexpected api call: ${url}`)
  })
}

describe("ContextTextPage", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    vi.spyOn(CandidateContext, "useCandidate").mockImplementation(() => ({
      candidates: [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }],
      selectedId: "c1",
      setSelectedId: vi.fn(),
      refresh: vi.fn(),
    }))
  })

  it("does not fetch context when no candidate is selected (effect early return)", () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/candidates") {
        return { json: async () => [] } as Response
      }
      if (url === "/api/state_ui_manifest") {
        return Promise.reject(new Error("use default manifest"))
      }
      if (url === "/api/system/ui_config") {
        return { json: async () => ({ column_types: {} }) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    vi.mocked(CandidateContext.useCandidate).mockImplementation(() => ({
      candidates: [],
      selectedId: null,
      setSelectedId: vi.fn(),
      refresh: vi.fn(),
    }))
    renderWithProviders(<ContextTextPage title="Story" contextKey="story" />)
    expect(screen.getByText("Loading...")).toBeInTheDocument()
  })

  it("falls back to draft when save response omits coercible context", async () => {
    mockCandidates("user draft")
    renderWithProviders(<ContextTextPage title="Story" contextKey="story" />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Story" })).toBeInTheDocument())
    await userEvent.clear(screen.getByRole("textbox"))
    await userEvent.type(screen.getByRole("textbox"), "typed")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return { json: async () => ({ candidate_data: { context: { story: "typed" } } }) } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        return { ok: true, json: async () => ({ candidate_data: { context: {} } }) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Story saved")).toBeInTheDocument())
    expect(screen.getByRole("textbox")).toHaveValue("typed")
  })

  it("loads string context values and saves", async () => {
    mockCandidates("plain text")
    renderWithProviders(<ContextTextPage title="Story" contextKey="story" />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Story" })).toBeInTheDocument())
    expect(screen.getByRole("textbox")).toHaveValue("plain text")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Story saved")).toBeInTheDocument())
  })

  it("coerces array and object context values for display", async () => {
    mockCandidates([
      "line one",
      { title: "Role", organization: "Org", job_reality: "Reality", left_because: "Because" },
      { label: "Skill", description: "Detail" },
      { description: "No label" },
      null,
    ])
    renderWithProviders(<ContextTextPage title="Story" contextKey="story" />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Story" })).toBeInTheDocument())
    const value = (screen.getByRole("textbox") as HTMLTextAreaElement).value
    expect(value).toContain("line one")
    expect(value).toContain("Role — Org")
    expect(value).toContain("Skill: Detail")
    expect(value).toContain("No label")
  })

  it("coerces non-array truthy values and handles save failures", async () => {
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
      }
      if (url === "/api/state_ui_manifest") {
        return { json: async () => ({}) } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return { json: async () => ({ candidate_data: { context: { story: 99 } } }) } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        return { ok: false, json: async () => ({}) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderWithProviders(<ContextTextPage title="Story" contextKey="story" />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Story" })).toBeInTheDocument())
    expect(screen.getByRole("textbox")).toHaveValue("99")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Save failed")).toBeInTheDocument())
  })

  it("restores draft on cancel", async () => {
    mockCandidates("saved")
    renderWithProviders(<ContextTextPage title="Story" contextKey="story" />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Story" })).toBeInTheDocument())
    await userEvent.type(screen.getByRole("textbox"), " draft")
    await userEvent.click(screen.getByRole("button", { name: "Cancel" }))
    expect(screen.getByRole("textbox")).toHaveValue("saved")
  })

  it("coerces null description on labeled rows and clears selection after load", async () => {
    mockCandidates([{ label: "L", description: null }])
    const { rerender } = renderWithProviders(<ContextTextPage title="Story" contextKey="story" />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Story" })).toBeInTheDocument())
    expect(screen.getByRole("textbox")).toHaveValue("L: ")

    vi.mocked(CandidateContext.useCandidate).mockImplementation(() => ({
      candidates: [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }],
      selectedId: null,
      setSelectedId: vi.fn(),
      refresh: vi.fn(),
    }))
    rerender(<ContextTextPage title="Story" contextKey="story" />)
    expect(screen.getByText("No candidate selected.")).toBeInTheDocument()
  })

  it("covers additional coercion and save branches", async () => {
    mockCandidates([
      { title: "Role", organization: "Org" },
      { label: "", description: "desc only" },
    ])
    renderWithProviders(<ContextTextPage title="Story" contextKey="story" />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Story" })).toBeInTheDocument())
    expect(screen.getByRole("textbox")).toHaveValue("Role — Org\n\ndesc only")

    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return { json: async () => ({ candidate_data: { context: { story: "saved" } } }) } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        return { ok: true, json: async () => ({ candidate_data: { context: { story: null } } }) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Story saved")).toBeInTheDocument())
    // Saved payload carries story: null — textarea keeps derived display until reload
  })
})
