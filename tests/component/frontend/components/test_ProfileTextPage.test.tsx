import { fireEvent, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import * as CandidateContext from "../../../../src/ui/frontend/src/contexts/CandidateContext"
import api from "../../../../src/ui/frontend/src/lib/api"
import ProfileTextPage from "../../../../src/ui/frontend/src/components/ProfileTextPage"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)
let selectedId: string | null = "c1"

function mockCandidates() {
  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    if (url === "/api/candidates") {
      return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
    }
    if (url === "/api/candidates/c1" && !init) {
      return {
        json: async () => ({
          candidate_data: { profile: { bio: "saved bio", note: 42 } },
        }),
      } as Response
    }
    if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
      return { ok: true, json: async () => ({ candidate_data: { profile: { bio: "new bio" } } }) } as Response
    }
    throw new Error(`unexpected api call: ${url}`)
  })
}

describe("ProfileTextPage", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    selectedId = "c1"
    vi.spyOn(CandidateContext, "useCandidate").mockImplementation(() => ({
      candidates: [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }],
      selectedId,
      setSelectedId: vi.fn(),
      refresh: vi.fn(),
    }))
  })

  it("shows loading then edits and saves a profile field", async () => {
    mockCandidates()
    renderWithProviders(<ProfileTextPage title="Bio" profileKey="bio" />)

    expect(screen.getByText("Loading...")).toBeInTheDocument()
    await waitFor(() => expect(screen.getByRole("heading", { name: "Bio" })).toBeInTheDocument())

    const textarea = screen.getByRole("textbox")
    expect(textarea).toHaveValue("saved bio")
    await userEvent.clear(textarea)
    await userEvent.type(textarea, "new bio")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Bio saved")).toBeInTheDocument())
  })

  it("coerces non-string profile values to empty and restores on cancel", async () => {
    mockCandidates()
    renderWithProviders(<ProfileTextPage title="Note" profileKey="note" />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Note" })).toBeInTheDocument())

    const textarea = screen.getByRole("textbox")
    expect(textarea).toHaveValue("")
    await userEvent.type(textarea, "draft")
    await userEvent.click(screen.getByRole("button", { name: "Cancel" }))
    expect(textarea).toHaveValue("")
  })

  it("shows save errors", async () => {
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return { json: async () => ({ candidate_data: { profile: { bio: "saved bio" } } }) } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        return { ok: false, json: async () => ({ error: "nope" }) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderWithProviders(<ProfileTextPage title="Bio" profileKey="bio" />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Bio" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("nope")).toBeInTheDocument())
  })

  it("uses default save errors and non-string saved values", async () => {
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return { json: async () => ({ candidate_data: { profile: { bio: "saved bio" } } }) } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        return { ok: false, json: async () => ({}) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderWithProviders(<ProfileTextPage title="Bio" profileKey="bio" />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Bio" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Save failed")).toBeInTheDocument())

    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return { json: async () => ({ candidate_data: { profile: { bio: "saved bio" } } }) } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        return { ok: true, json: async () => ({ candidate_data: { profile: { bio: 12 } } }) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Bio saved")).toBeInTheDocument())
    expect(screen.getByRole("textbox")).toHaveValue("saved bio")
  })

  it("shows no candidate after selection clears", async () => {
    mockCandidates()
    const { rerender } = renderWithProviders(<ProfileTextPage title="Bio" profileKey="bio" />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Bio" })).toBeInTheDocument())
    selectedId = null
    rerender(<ProfileTextPage title="Bio" profileKey="bio" />)
    expect(screen.getByText("No candidate selected.")).toBeInTheDocument()
  })

  it("stays on loading when no candidate is selected", async () => {
    selectedId = null
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/candidates") {
        return { json: async () => [] } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderWithProviders(<ProfileTextPage title="Bio" profileKey="bio" />)
    await waitFor(() => expect(screen.getByText("Loading...")).toBeInTheDocument())
    expect(mockedApi.mock.calls.some(call => String(call[0]).startsWith("/api/candidates/c1"))).toBe(false)
  })
})
