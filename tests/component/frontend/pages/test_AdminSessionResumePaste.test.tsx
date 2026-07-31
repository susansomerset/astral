import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import SessionResumePaste from "../../../../src/ui/frontend/src/pages/AdminSessionResumePaste"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const STRUCTURE = {
  sections: {
    experience: {
      id: "experience",
      title: "Experience",
      enabled: true,
      order: 0,
      job_agent_editable: true,
    },
  },
}

describe("AdminSessionResumePaste — AST-987", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    vi.stubGlobal(
      "open",
      vi.fn(() => ({ closed: false })),
    )
    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:session-html"),
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

  it("renders page; Parse success enables Open HTML; failure never opens tab (§6c)", async () => {
    mockApis(async (url, init) => {
      if (url === "/api/admin/session_resume/parse" && init?.method === "POST") {
        return {
          ok: true,
          json: async () => ({
            success: true,
            resume_structure: STRUCTURE,
            base_resume: { experience: "Jobs from paste" },
          }),
        } as Response
      }
    })
    renderWithProviders(<SessionResumePaste />)
    expect(screen.getByRole("heading", { name: "Session Resume Paste" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Parse" })).toBeDisabled()
    expect(screen.getByRole("button", { name: "View Parsed JSON" })).toBeDisabled()
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeDisabled()
    // Button order: Parse → View Parsed JSON → Open HTML (AST-1035).
    const rowButtons = screen.getAllByRole("button").filter(b =>
      ["Parse", "View Parsed JSON", "Open HTML"].includes(b.textContent || ""),
    )
    expect(rowButtons.map(b => b.textContent)).toEqual([
      "Parse",
      "View Parsed JSON",
      "Open HTML",
    ])

    const textarea = screen.getByPlaceholderText(/Paste full resume text/)
    fireEvent.change(textarea, { target: { value: "Full resume paste" } })
    expect(screen.getByRole("button", { name: "Parse" })).toBeEnabled()

    await userEvent.click(screen.getByRole("button", { name: "Parse" }))
    await waitFor(() => expect(screen.getByText("Parsed resume structure.")).toBeInTheDocument())
    expect(screen.getByRole("button", { name: "View Parsed JSON" })).toBeEnabled()
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeEnabled()
    expect(window.open).not.toHaveBeenCalled()
    expect(JSON.parse(localStorage.getItem("session_resume:last_parse") || "null")).toEqual({
      resume_structure: STRUCTURE,
      base_resume: { experience: "Jobs from paste" },
    })
    expect(localStorage.getItem("session_resume:paste_text")).toContain("Full resume paste")
  })

  it("failed parse shows error and does not open HTML tab", async () => {
    mockApis(async (url, init) => {
      if (url === "/api/admin/session_resume/parse" && init?.method === "POST") {
        return {
          ok: false,
          status: 500,
          json: async () => ({ success: false, error: "agent boom" }),
        } as Response
      }
    })
    renderWithProviders(<SessionResumePaste />)
    fireEvent.change(screen.getByPlaceholderText(/Paste full resume text/), {
      target: { value: "bad paste" },
    })
    await userEvent.click(screen.getByRole("button", { name: "Parse" }))
    await waitFor(() => expect(screen.getAllByText("agent boom").length).toBeGreaterThan(0))
    expect(screen.getByRole("button", { name: "View Parsed JSON" })).toBeDisabled()
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeDisabled()
    expect(window.open).not.toHaveBeenCalled()
  })

  it("View Parsed JSON shows lastParse payload; close keeps lastParse (AST-1035)", async () => {
    const payload = {
      resume_structure: STRUCTURE,
      base_resume: { experience: "Jobs from paste" },
    }
    localStorage.setItem("session_resume:paste_text", JSON.stringify("kept paste"))
    localStorage.setItem("session_resume:last_parse", JSON.stringify(payload))
    mockApis()
    renderWithProviders(<SessionResumePaste />)
    const viewBtn = await screen.findByRole("button", { name: "View Parsed JSON" })
    expect(viewBtn).toBeEnabled()
    await userEvent.click(viewBtn)
    const modal = screen.getByText("Parsed resume JSON").closest(".modal-card") as HTMLElement
    expect(modal).toBeTruthy()
    const pre = within(modal).getByText((_, el) => el?.tagName === "PRE")
    expect(pre.textContent).toBe(JSON.stringify(payload, null, 2))
    expect(pre.textContent).toContain("resume_structure")
    expect(pre.textContent).toContain("base_resume")
    // Close must not clear lastParse / disable Open HTML.
    await userEvent.click(within(modal).getByRole("button", { name: "Close" }))
    await waitFor(() => expect(screen.queryByText("Parsed resume JSON")).not.toBeInTheDocument())
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeEnabled()
    expect(JSON.parse(localStorage.getItem("session_resume:last_parse") || "null")).toEqual(payload)
  })

  it("Open HTML posts session JSON and opens blob tab", async () => {
    localStorage.setItem("session_resume:paste_text", JSON.stringify("kept paste"))
    localStorage.setItem(
      "session_resume:last_parse",
      JSON.stringify({
        resume_structure: STRUCTURE,
        base_resume: { experience: "Jobs" },
      }),
    )
    mockApis(async (url, init) => {
      if (url === "/api/admin/session_resume/html" && init?.method === "POST") {
        const body = JSON.parse(String(init.body))
        expect(body.base_resume.experience).toBe("Jobs")
        return {
          ok: true,
          text: async () => "<html><body>session html</body></html>",
        } as Response
      }
    })
    renderWithProviders(<SessionResumePaste />)
    await waitFor(() => expect(screen.getByRole("button", { name: "Open HTML" })).toBeEnabled())
    await userEvent.click(screen.getByRole("button", { name: "Open HTML" }))
    await waitFor(() =>
      expect(window.open).toHaveBeenCalledWith("blob:session-html", "_blank", "noopener,noreferrer"),
    )
  })

  it("Open HTML error shows message and does not open tab", async () => {
    localStorage.setItem("session_resume:paste_text", JSON.stringify("kept paste"))
    localStorage.setItem(
      "session_resume:last_parse",
      JSON.stringify({
        resume_structure: STRUCTURE,
        base_resume: { experience: "Jobs" },
      }),
    )
    mockApis(async (url, init) => {
      if (url === "/api/admin/session_resume/html" && init?.method === "POST") {
        return {
          ok: false,
          status: 400,
          json: async () => ({ success: false, error: "base_resume content is required" }),
        } as Response
      }
    })
    renderWithProviders(<SessionResumePaste />)
    await waitFor(() => expect(screen.getByRole("button", { name: "Open HTML" })).toBeEnabled())
    await userEvent.click(screen.getByRole("button", { name: "Open HTML" }))
    await waitFor(() =>
      expect(screen.getAllByText("base_resume content is required").length).toBeGreaterThan(0),
    )
    expect(window.open).not.toHaveBeenCalled()
  })

  it("restores paste + last parse from localStorage on remount", async () => {
    localStorage.setItem("session_resume:paste_text", JSON.stringify("restored paste"))
    localStorage.setItem(
      "session_resume:last_parse",
      JSON.stringify({
        resume_structure: STRUCTURE,
        base_resume: { experience: "Restored" },
      }),
    )
    mockApis()
    renderWithProviders(<SessionResumePaste />)
    expect(screen.getByDisplayValue("restored paste")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "View Parsed JSON" })).toBeEnabled()
    expect(screen.getByRole("button", { name: "Open HTML" })).toBeEnabled()
  })
})
