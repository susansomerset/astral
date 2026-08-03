import { fireEvent, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import SessionCoverLetter from "../../../../src/ui/frontend/src/pages/AdminSessionCoverLetter"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const FILLED: Record<string, string> = {
  from_block: "Susan Somerset\nhire@example.com",
  letter_date: "July 27, 2026",
  to_block: "",
  subject: "",
  letter: "Dear Hiring Team,\n\nThanks.",
  signoff_closing: "Best,",
  signature: "Susan Somerset",
}

describe("AdminSessionCoverLetter — AST-1025", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    vi.stubGlobal(
      "open",
      vi.fn(() => ({ closed: false })),
    )
    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:session-cover-html"),
      revokeObjectURL: vi.fn(),
    })
  })

  function mockApis(
    extra?: (url: string, init?: RequestInit) => Promise<Response | undefined> | Response | undefined,
  ) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      const fromExtra = extra ? await extra(url, init) : undefined
      if (fromExtra !== undefined) return fromExtra
    })
  }

  function fillRequired() {
    fireEvent.change(screen.getByLabelText(/^From block$/), {
      target: { value: FILLED.from_block },
    })
    fireEvent.change(screen.getByLabelText(/^Date$/), {
      target: { value: FILLED.letter_date },
    })
    fireEvent.change(screen.getByLabelText(/^Letter body$/), {
      target: { value: FILLED.letter },
    })
    fireEvent.change(screen.getByLabelText(/^Sign-off closing$/), {
      target: { value: FILLED.signoff_closing },
    })
    fireEvent.change(screen.getByLabelText(/^Signature name$/), {
      target: { value: FILLED.signature },
    })
  }

  it("renders page; Open HTML disabled until required fields filled (§6c)", async () => {
    mockApis()
    renderWithProviders(<SessionCoverLetter />)
    expect(screen.getByRole("heading", { name: "Session Cover Letter" })).toBeInTheDocument()
    expect(screen.getByText(/does not save to the database/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/To block \(optional\)/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Subject \(optional\)/)).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeDisabled()
    fillRequired()
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeEnabled()
    expect(window.open).not.toHaveBeenCalled()
  })

  it("Open HTML posts fields + null candidate_id and opens blob tab", async () => {
    mockApis(async (url, init) => {
      if (url === "/api/admin/session_cover_letter/html" && init?.method === "POST") {
        const body = JSON.parse(String(init.body))
        expect(body.from_block).toBe(FILLED.from_block)
        expect(body.letter).toBe(FILLED.letter)
        expect(body.candidate_id).toBeNull()
        return {
          ok: true,
          text: async () => "<html><body>cover html</body></html>",
        } as Response
      }
    })
    renderWithProviders(<SessionCoverLetter />)
    fillRequired()
    await userEvent.click(screen.getByRole("button", { name: "Open HTML" }))
    await waitFor(() =>
      expect(window.open).toHaveBeenCalledWith(
        "blob:session-cover-html",
        "_blank",
        "noopener,noreferrer",
      ),
    )
    expect(JSON.parse(localStorage.getItem("session_cover_letter:last_render") || "null")).toEqual({
      fields: expect.objectContaining({
        from_block: FILLED.from_block,
        letter: FILLED.letter,
        signature: FILLED.signature,
      }),
      candidate_id: null,
    })
    expect(localStorage.getItem("session_cover_letter:fields")).toContain("Dear Hiring Team")
  })

  it("Open HTML error shows message and does not open tab", async () => {
    mockApis(async (url, init) => {
      if (url === "/api/admin/session_cover_letter/html" && init?.method === "POST") {
        return {
          ok: false,
          status: 400,
          json: async () => ({ success: false, error: "from_block is required" }),
        } as Response
      }
    })
    renderWithProviders(<SessionCoverLetter />)
    fillRequired()
    await userEvent.click(screen.getByRole("button", { name: "Open HTML" }))
    await waitFor(() =>
      expect(screen.getAllByText("from_block is required").length).toBeGreaterThan(0),
    )
    expect(window.open).not.toHaveBeenCalled()
    // useLocalStorage may persist JSON null as the string "null"
    expect(JSON.parse(localStorage.getItem("session_cover_letter:last_render") || "null")).toBeNull()
  })

  it("empty HTML body does not open tab", async () => {
    mockApis(async (url, init) => {
      if (url === "/api/admin/session_cover_letter/html" && init?.method === "POST") {
        return { ok: true, text: async () => "   " } as Response
      }
    })
    renderWithProviders(<SessionCoverLetter />)
    fillRequired()
    await userEvent.click(screen.getByRole("button", { name: "Open HTML" }))
    await waitFor(() =>
      expect(screen.getAllByText("HTML response was empty").length).toBeGreaterThan(0),
    )
    expect(window.open).not.toHaveBeenCalled()
  })

  it("forwards selected candidate_id on Open HTML", async () => {
    localStorage.setItem("astral_selected_candidate", "cand-9")
    mockApis(async (url, init) => {
      if (url === "/api/candidates") {
        return {
          ok: true,
          json: async () => [
            { astral_candidate_id: "cand-9", state: "ACTIVE_SEARCH", candidate_data: {} },
          ],
        } as Response
      }
      if (url === "/api/admin/session_cover_letter/html" && init?.method === "POST") {
        const body = JSON.parse(String(init.body))
        expect(body.candidate_id).toBe("cand-9")
        return {
          ok: true,
          text: async () => "<html><body>ok</body></html>",
        } as Response
      }
    })
    renderWithProviders(<SessionCoverLetter />)
    fillRequired()
    await userEvent.click(screen.getByRole("button", { name: "Open HTML" }))
    await waitFor(() => expect(window.open).toHaveBeenCalled())
  })

  it("restores fields from localStorage on remount", async () => {
    localStorage.setItem("session_cover_letter:fields", JSON.stringify(FILLED))
    mockApis()
    renderWithProviders(<SessionCoverLetter />)
    expect(screen.getByDisplayValue("July 27, 2026")).toBeInTheDocument()
    expect(screen.getByDisplayValue("Susan Somerset")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeEnabled()
  })
})

describe("AdminSessionCoverLetter — AST-1139", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    vi.stubGlobal(
      "open",
      vi.fn(() => ({ closed: false })),
    )
    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:session-cover-html"),
      revokeObjectURL: vi.fn(),
    })
  })

  function mockApis(
    extra?: (url: string, init?: RequestInit) => Promise<Response | undefined> | Response | undefined,
  ) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      const fromExtra = extra ? await extra(url, init) : undefined
      if (fromExtra !== undefined) return fromExtra
    })
  }

  function fillRequiredExceptFromBlock() {
    fireEvent.change(screen.getByLabelText(/^Date$/), {
      target: { value: FILLED.letter_date },
    })
    fireEvent.change(screen.getByLabelText(/^Letter body$/), {
      target: { value: FILLED.letter },
    })
    fireEvent.change(screen.getByLabelText(/^Sign-off closing$/), {
      target: { value: FILLED.signoff_closing },
    })
    fireEvent.change(screen.getByLabelText(/^Signature name$/), {
      target: { value: FILLED.signature },
    })
  }

  it("empty From block + selected candidate enables Open HTML (§6c)", async () => {
    localStorage.setItem("astral_selected_candidate", "cand-9")
    mockApis(async (url) => {
      if (url === "/api/candidates") {
        return {
          ok: true,
          json: async () => [
            { astral_candidate_id: "cand-9", state: "ACTIVE_SEARCH", candidate_data: {} },
          ],
        } as Response
      }
    })
    renderWithProviders(<SessionCoverLetter />)
    expect(
      screen.getByText(/leave From block empty to use that candidate/i),
    ).toBeInTheDocument()
    fillRequiredExceptFromBlock()
    expect(screen.getByLabelText(/^From block$/)).toHaveValue("")
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeEnabled()
  })

  it("empty From block without candidate keeps Open HTML disabled", async () => {
    mockApis()
    renderWithProviders(<SessionCoverLetter />)
    fillRequiredExceptFromBlock()
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeDisabled()
    expect(screen.getByText(/Without a candidate,\s*From block is required/i)).toBeInTheDocument()
  })

  it("Open HTML posts empty from_block with candidate_id", async () => {
    localStorage.setItem("astral_selected_candidate", "cand-9")
    mockApis(async (url, init) => {
      if (url === "/api/candidates") {
        return {
          ok: true,
          json: async () => [
            { astral_candidate_id: "cand-9", state: "ACTIVE_SEARCH", candidate_data: {} },
          ],
        } as Response
      }
      if (url === "/api/admin/session_cover_letter/html" && init?.method === "POST") {
        const body = JSON.parse(String(init.body))
        expect(body.from_block).toBe("")
        expect(body.candidate_id).toBe("cand-9")
        expect(body.letter).toBe(FILLED.letter)
        return {
          ok: true,
          text: async () => "<html><body>resolved</body></html>",
        } as Response
      }
    })
    renderWithProviders(<SessionCoverLetter />)
    fillRequiredExceptFromBlock()
    await userEvent.click(screen.getByRole("button", { name: "Open HTML" }))
    await waitFor(() => expect(window.open).toHaveBeenCalled())
  })
})

const COVER_FROM_UI = {
  default_template: "{$FULL_NAME} | {$LOCATION}\n{$CONTACT_EMAIL} | {$PHONE}",
  authoring_help:
    "Allowed tokens: {$FULL_NAME}, {$LOCATION}, {$CONTACT_EMAIL}, {$PHONE}. Type | between segments; cover print shows •. Leave empty to use the default template (see placeholder).",
  session_authoring_help:
    "Enter cover-letter field values, then Open HTML to Print → PDF. Letter fields come from this form. From block supports {$FULL_NAME}, {$LOCATION}, {$CONTACT_EMAIL}, {$PHONE}; type | for • in print. When a candidate is selected, leave From empty to use that candidate’s saved from-block or the default token template. Without a candidate, From is required. This tool does not save to the database.",
}

describe("AdminSessionCoverLetter — AST-1149", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    vi.stubGlobal(
      "open",
      vi.fn(() => ({ closed: false })),
    )
    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:session-cover-html"),
      revokeObjectURL: vi.fn(),
    })
  })

  function mockApis(
    extra?: (url: string, init?: RequestInit) => Promise<Response | undefined> | Response | undefined,
  ) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/ui_config" || url === "/api/system/ui_config") {
        return {
          ok: true,
          json: async () => ({ cover_from_block: COVER_FROM_UI }),
        } as Response
      }
      const fromExtra = extra ? await extra(url, init) : undefined
      if (fromExtra !== undefined) return fromExtra
    })
  }

  it("renders config-driven intro + From help/placeholder (§6c)", async () => {
    mockApis()
    renderWithProviders(<SessionCoverLetter />)
    await waitFor(() =>
      expect(screen.getByText(/default token template/i)).toBeInTheDocument(),
    )
    expect(screen.getByText(/Allowed tokens: \{\$FULL_NAME\}/i)).toBeInTheDocument()
    expect(screen.getByText(/type \| for • in print/i)).toBeInTheDocument()
    // Help text lives inside the <label>, so accessible name is not exactly "From block".
    const from = screen.getByPlaceholderText(/\{\$FULL_NAME\}/)
    expect(from.getAttribute("placeholder")).toBe(COVER_FROM_UI.default_template)
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeDisabled()
  })

  it("empty From + candidate still enables Open HTML with config help", async () => {
    localStorage.setItem("astral_selected_candidate", "cand-9")
    mockApis(async (url) => {
      if (url === "/api/candidates") {
        return {
          ok: true,
          json: async () => [
            { astral_candidate_id: "cand-9", state: "ACTIVE_SEARCH", candidate_data: {} },
          ],
        } as Response
      }
    })
    renderWithProviders(<SessionCoverLetter />)
    await waitFor(() =>
      expect(screen.getByText(/default token template/i)).toBeInTheDocument(),
    )
    fireEvent.change(screen.getByLabelText(/^Date$/), {
      target: { value: FILLED.letter_date },
    })
    fireEvent.change(screen.getByLabelText(/^Letter body$/), {
      target: { value: FILLED.letter },
    })
    fireEvent.change(screen.getByLabelText(/^Sign-off closing$/), {
      target: { value: FILLED.signoff_closing },
    })
    fireEvent.change(screen.getByLabelText(/^Signature name$/), {
      target: { value: FILLED.signature },
    })
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeEnabled()
  })
})
