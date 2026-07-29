import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AdminManageEmail from "../../../../src/ui/frontend/src/pages/AdminManageEmail"
import { installBaseApiMocks, jsonResponse, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const ROWS = [
  {
    id: "m1",
    thread_id: "t1",
    subject: "Hello Astral",
    from_address: "sender@example.com",
    date: "Mon, 1 Jan 2026",
    unread: true,
    candidate_match: { matched: true, astral_candidate_id: "cand-ada" },
  },
  {
    id: "m2",
    thread_id: "t2",
    subject: "",
    from_address: "other@example.com",
    date: "Tue, 2 Jan 2026",
    unread: false,
    candidate_match: { matched: false, astral_candidate_id: null },
  },
]

describe("AdminManageEmail — AST-1033 / AST-1040 / AST-1048 (§6c routed page)", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  function mockApis(
    extra?: (url: string, init?: RequestInit) => Promise<Response | undefined> | Response | undefined,
  ) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      const fromExtra = extra ? await extra(url, init) : undefined
      if (fromExtra !== undefined) return fromExtra
      if (url === "/api/admin/inbox/messages") {
        return jsonResponse({ messages: ROWS })
      }
    })
  }

  it("renders Manage Email heading and inbox rows on first paint", async () => {
    mockApis()
    renderWithProviders(<AdminManageEmail />)
    expect(screen.getByRole("heading", { name: "Manage Email" })).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    expect(screen.getByText("sender@example.com")).toBeInTheDocument()
    expect(screen.getByText("Unread")).toBeInTheDocument()
    expect(screen.getByText("Read")).toBeInTheDocument()
    expect(mockedApi).toHaveBeenCalledWith("/api/admin/inbox/messages")
  })

  it("list Candidate column shows match bind or em dash (AST-1048)", async () => {
    mockApis()
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    expect(screen.getByRole("columnheader", { name: "Candidate" })).toBeInTheDocument()
    const matched = screen.getByText("Matched: cand-ada")
    expect(matched).toHaveClass("manage-email-match")
    const unmatchedRow = screen.getByText("other@example.com").closest("tr")
    expect(unmatchedRow).toBeTruthy()
    expect(unmatchedRow!.textContent).toContain("—")
  })

  it("matched row: modal shows bind + enabled Create; raw HTML source (AST-1040/1048)", async () => {
    const raw = "<p>body html</p>"
    mockApis(async (url) => {
      if (url === "/api/admin/inbox/messages/m1") {
        return jsonResponse({ id: "m1", html_body: raw })
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    await userEvent.click(screen.getByText("Hello Astral"))
    await waitFor(() => expect(screen.getByTitle("Email body")).toBeInTheDocument())
    expect(screen.getByRole("heading", { name: "Hello Astral", level: 2 })).toBeInTheDocument()
    const modalMatch = screen.getByText("Matched: cand-ada", {
      selector: ".manage-email-match--modal",
    })
    expect(modalMatch).toBeInTheDocument()
    const create = screen.getByRole("button", { name: "Create" })
    expect(create).toBeEnabled()
    const source = screen.getByTitle("Email body")
    expect(source.tagName).toBe("PRE")
    expect(source).toHaveClass("email-html-source")
    expect(source).toHaveTextContent(raw)
    expect(document.querySelector("iframe")).toBeNull()
    expect(mockedApi).toHaveBeenCalledWith("/api/admin/inbox/messages/m1")
  })

  it("unmatched row: modal omits match line; Create disabled; browse still works", async () => {
    mockApis(async (url) => {
      if (url === "/api/admin/inbox/messages/m2") {
        return jsonResponse({ id: "m2", html_body: "" })
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("other@example.com")).toBeInTheDocument())
    const row = screen.getByText("other@example.com").closest("tr")
    expect(row).toBeTruthy()
    await userEvent.click(row!)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Message", level: 2 })).toBeInTheDocument(),
    )
    // List may still show other rows' match cells; modal must omit the bind line.
    expect(document.querySelector(".manage-email-match--modal")).toBeNull()
    expect(screen.getByRole("button", { name: "Create" })).toBeDisabled()
    const source = screen.getByTitle("Email body")
    expect(source.tagName).toBe("PRE")
    expect(source).toHaveTextContent("")
  })

  it("list failure shows inline error + toast", async () => {
    mockApis(async (url) => {
      if (url === "/api/admin/inbox/messages") {
        return jsonResponse({ error: "blocked" }, false)
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getAllByText("blocked").length).toBeGreaterThanOrEqual(2))
    expect(screen.queryByRole("table")).not.toBeInTheDocument()
  })

  it("body fetch failure shows modal error without source panel", async () => {
    mockApis(async (url) => {
      if (url === "/api/admin/inbox/messages/m1") {
        return jsonResponse({ error: "upstream" }, false)
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    await userEvent.click(screen.getByText("Hello Astral"))
    await waitFor(() => expect(screen.getByText("upstream")).toBeInTheDocument())
    expect(screen.queryByTitle("Email body")).not.toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Create" })).toBeEnabled()
  })
})
