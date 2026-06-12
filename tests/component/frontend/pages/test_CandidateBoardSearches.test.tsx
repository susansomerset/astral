import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CandidateBoardSearches from "../../../../src/ui/frontend/src/pages/CandidateBoardSearches"
import { baseCandidate, candidateId, installBaseApiMocks, jsonResponse } from "./page-mocks"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const boards = [{ board_key: "tst", label: "Test Board" }]

const searches = [
  {
    board_search_id: "bs-1",
    board_key: "tst",
    label: "Remote PM",
    mode: "criteria" as const,
    criteria: { title_query: "pm" },
    deeplink_url: null,
    state: "ACTIVE" as const,
    created_at: "2026-05-01T10:00:00Z",
    updated_at: "2026-05-02T11:00:00Z",
  },
]

function boardSearchesHandler(url: string, init?: RequestInit) {
  if (url === "/api/boards") return jsonResponse(boards)
  if (
    url.startsWith(`/api/boards/searches?candidate_id=${encodeURIComponent(baseCandidate.astral_candidate_id)}`) &&
    (!init || !init.method)
  ) {
    return jsonResponse(searches)
  }
  if (url === "/api/boards/searches" && init?.method === "POST") {
    return jsonResponse({ board_search_id: "bs-new", ...searches[0] })
  }
  return Promise.reject(new Error(`unexpected api ${url}`))
}

function installBoardSearchMocks(patchCaptures?: { lastPatchBody: string }) {
  const boardsPayload = [{ board_key: "tst", label: "Test board" }]
  const searchesPayload = [
    {
      board_search_id: "bs-1",
      board_key: "tst",
      label: "Open roles",
      mode: "criteria",
      criteria: { title_query: "eng" },
      state: "ACTIVE",
      created_at: "2026-05-01 10:00:00",
      updated_at: "2026-05-01 11:00:00",
    },
    {
      board_search_id: "bs-err",
      board_key: "tst",
      label: "Broken scan",
      mode: "criteria",
      criteria: {},
      state: "ERROR",
      created_at: "2026-05-02 10:00:00",
      updated_at: "2026-05-02 11:00:00",
    },
  ]

  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    if (url === "/api/candidates") {
      return jsonResponse([{ astral_candidate_id: candidateId, state: "ACTIVE", candidate_data: {} }])
    }
    if (url === "/api/boards") return jsonResponse(boardsPayload)
    if (url.startsWith(`/api/boards/searches?candidate_id=${encodeURIComponent(candidateId)}`) && (!init || !init.method)) {
      return jsonResponse(searchesPayload)
    }
    if (init?.method === "PATCH" && url.startsWith("/api/boards/searches/") && patchCaptures) {
      patchCaptures.lastPatchBody = typeof init.body === "string" ? init.body : ""
      return jsonResponse({ ...searchesPayload[1], state: "ACTIVE" })
    }
    if (init?.method === "POST" && url === "/api/boards/searches")
      return jsonResponse({ ...searchesPayload[0], board_search_id: "bs-new", label: "N" })
    throw new Error(`unexpected api: ${url} ${init?.method ?? "GET"}`)
  })
}

describe("CandidateBoardSearches", () => {
  beforeEach(() => {
    localStorage.clear()
    localStorage.setItem("astral_selected_candidate", baseCandidate.astral_candidate_id)
    mockedApi.mockReset()
  })

  it("AST-457: renders list with label, board, gaze state, and timestamp columns", async () => {
    installBaseApiMocks(mockedApi, boardSearchesHandler)
    renderWithProviders(<CandidateBoardSearches />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Board Searches" })).toBeInTheDocument())
    await waitFor(() => expect(screen.getByText("Remote PM")).toBeInTheDocument())
    expect(screen.getByText("Label")).toBeInTheDocument()
    expect(screen.getByText("Board")).toBeInTheDocument()
    expect(screen.getByText("Gaze state")).toBeInTheDocument()
    expect(screen.getByText("Created")).toBeInTheDocument()
    expect(screen.getByText("Updated")).toBeInTheDocument()
    expect(screen.getByText("Test Board")).toBeInTheDocument()
  })

  it("AST-457: creates criteria-mode search via POST", async () => {
    installBaseApiMocks(mockedApi, boardSearchesHandler)
    renderWithProviders(<CandidateBoardSearches />)
    await waitFor(() => expect(screen.getByRole("button", { name: "New search" })).toBeEnabled())
    await userEvent.click(screen.getByRole("button", { name: "New search" }))
    const modal = screen.getByRole("heading", { name: "New board search" }).closest(".modal-card")!
    await userEvent.type(within(modal as HTMLElement).getAllByRole("textbox")[0], "New role")
    await userEvent.selectOptions(within(modal as HTMLElement).getByRole("combobox"), "tst")
    await userEvent.click(within(modal as HTMLElement).getByRole("button", { name: "Save" }))
    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith(
        "/api/boards/searches",
        expect.objectContaining({
          method: "POST",
          body: expect.stringContaining('"mode":"criteria"'),
        }),
      ),
    )
  })

  it("AST-457: mode switch to deeplink clears criteria after UserPrompt confirm", async () => {
    installBaseApiMocks(mockedApi, boardSearchesHandler)
    renderWithProviders(<CandidateBoardSearches />)
    await waitFor(() => expect(screen.getByRole("button", { name: "New search" })).toBeEnabled())
    await userEvent.click(screen.getByRole("button", { name: "New search" }))
    const modal = screen.getByRole("heading", { name: "New board search" }).closest(".modal-card")!
    const criteria = within(modal as HTMLElement).getByDisplayValue("{}")
    await userEvent.clear(criteria)
    await userEvent.type(criteria, "not-empty")
    await userEvent.click(within(modal as HTMLElement).getByRole("button", { name: "Deeplink" }))
    await waitFor(() => expect(screen.getByRole("alertdialog", { name: "Switch mode?" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Continue" }))
    expect(within(modal as HTMLElement).getByPlaceholderText("https://…")).toBeInTheDocument()
    expect(within(modal as HTMLElement).queryByDisplayValue("not-empty")).not.toBeInTheDocument()
  })

  it("AST-457: renders list with label, board, gaze state, and timestamp columns", async () => {
    installBaseApiMocks(mockedApi, boardSearchesHandler)
    renderWithProviders(<CandidateBoardSearches />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Board Searches" })).toBeInTheDocument())
    await waitFor(() => expect(screen.getByText("Remote PM")).toBeInTheDocument())
    expect(screen.getByText("Label")).toBeInTheDocument()
    expect(screen.getByText("Board")).toBeInTheDocument()
    expect(screen.getByText("Gaze state")).toBeInTheDocument()
    expect(screen.getByText("Created")).toBeInTheDocument()
    expect(screen.getByText("Updated")).toBeInTheDocument()
    expect(screen.getByText("Test Board")).toBeInTheDocument()
  })

  it("AST-457: creates criteria-mode search via POST", async () => {
    installBaseApiMocks(mockedApi, boardSearchesHandler)
    renderWithProviders(<CandidateBoardSearches />)
    await waitFor(() => expect(screen.getByRole("button", { name: "New search" })).toBeEnabled())
    await userEvent.click(screen.getByRole("button", { name: "New search" }))
    const modal = screen.getByRole("heading", { name: "New board search" }).closest(".modal-card")!
    await userEvent.type(within(modal as HTMLElement).getAllByRole("textbox")[0], "New role")
    await userEvent.selectOptions(within(modal as HTMLElement).getByRole("combobox"), "tst")
    await userEvent.click(within(modal as HTMLElement).getByRole("button", { name: "Save" }))
    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith(
        "/api/boards/searches",
        expect.objectContaining({
          method: "POST",
          body: expect.stringContaining('"mode":"criteria"'),
        }),
      ),
    )
  })

  it("AST-457: mode switch to deeplink clears criteria after confirm", async () => {
    installBaseApiMocks(mockedApi, boardSearchesHandler)
    renderWithProviders(<CandidateBoardSearches />)
    await waitFor(() => expect(screen.getByRole("button", { name: "New search" })).toBeEnabled())
    await userEvent.click(screen.getByRole("button", { name: "New search" }))
    const modal = screen.getByRole("heading", { name: "New board search" }).closest(".modal-card")!
    const criteria = within(modal as HTMLElement).getByDisplayValue("{}")
    await userEvent.clear(criteria)
    await userEvent.type(criteria, "not-empty")
    await userEvent.click(within(modal as HTMLElement).getByRole("button", { name: "Deeplink" }))
    expect(window.confirm).toHaveBeenCalled()
    expect(within(modal as HTMLElement).getByPlaceholderText("https://…")).toBeInTheDocument()
    expect(within(modal as HTMLElement).queryByDisplayValue("not-empty")).not.toBeInTheDocument()
  })

  it("renders page and gaze state labels (ACTIVE / ERROR)", async () => {
    installBoardSearchMocks()
    renderWithProviders(<CandidateBoardSearches />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Board Searches" })).toBeInTheDocument())
    expect(screen.getAllByText("ACTIVE").length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText("ERROR")).toBeInTheDocument()
  })

  it("resume from ERROR PATCHes state ACTIVE", async () => {
    const cap = { lastPatchBody: "" }
    installBoardSearchMocks(cap)
    renderWithProviders(<CandidateBoardSearches />)
    await waitFor(() => expect(screen.getByRole("button", { name: "Resume ACTIVE" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Resume ACTIVE" }))
    await waitFor(() => expect(cap.lastPatchBody).toContain('"state":"ACTIVE"'))
    expect(JSON.parse(cap.lastPatchBody)).toEqual({ state: "ACTIVE" })
  })

  it("create flow sends Paused workflow as state INACTIVE", async () => {
    installBoardSearchMocks()
    const bodies: string[] = []
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return jsonResponse([{ astral_candidate_id: candidateId, state: "ACTIVE", candidate_data: {} }])
      }
      if (url === "/api/boards") return jsonResponse([{ board_key: "tst", label: "Test board" }])
      if (url.startsWith(`/api/boards/searches?candidate_id=${encodeURIComponent(candidateId)}`) && (!init || !init.method))
        return jsonResponse([])
      if (init?.method === "POST" && url === "/api/boards/searches") {
        bodies.push(typeof init.body === "string" ? init.body : "")
        return jsonResponse({
          board_search_id: "bs-new",
          board_key: "tst",
          label: "L",
          mode: "criteria",
          criteria: { x: true },
          state: "INACTIVE",
          created_at: "now",
          updated_at: "now",
        })
      }
      throw new Error(`unexpected api: ${url} ${init?.method ?? "GET"}`)
    })
    renderWithProviders(<CandidateBoardSearches />)
    await waitFor(() => expect(screen.getByRole("button", { name: "New search" })).not.toBeDisabled())
    await userEvent.click(screen.getByRole("button", { name: "New search" }))
    await waitFor(() => expect(screen.getByRole("heading", { name: "New board search" })).toBeInTheDocument())
    const modal = screen.getByRole("heading", { name: "New board search" }).closest(".modal-card") as HTMLElement
    await userEvent.type(within(modal).getAllByRole("textbox")[0], "L")
    await userEvent.click(within(modal).getByRole("button", { name: "Paused" }))
    await userEvent.click(within(modal).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(bodies.length).toBe(1))
    const parsed = JSON.parse(bodies[0]!) as Record<string, unknown>
    expect(parsed.state).toBe("INACTIVE")
    expect(parsed.mode).toBe("criteria")
  })
})
