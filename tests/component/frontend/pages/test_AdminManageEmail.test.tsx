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

describe("AdminManageEmail — AST-1033 / AST-1040 / AST-1048 / AST-1051 (§6c routed page)", () => {
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

  it("matched row has Actions Create; unmatched has none (AST-1051)", async () => {
    mockApis()
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    expect(screen.getByRole("columnheader", { name: "Actions" })).toBeInTheDocument()
    const matchedRow = screen.getByText("Hello Astral").closest("tr")
    const unmatchedRow = screen.getByText("other@example.com").closest("tr")
    expect(matchedRow).toBeTruthy()
    expect(unmatchedRow).toBeTruthy()
    expect(matchedRow!.querySelector("button.manage-email-create")).toBeTruthy()
    expect(unmatchedRow!.querySelector("button.manage-email-create")).toBeNull()
  })

  it("matched row: modal shows bind + raw HTML; no Create in modal (AST-1040/1051)", async () => {
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
    expect(document.querySelector(".manage-email-actions")).toBeNull()
    const source = screen.getByTitle("Email body")
    expect(source.tagName).toBe("PRE")
    expect(source).toHaveClass("email-html-source")
    expect(source).toHaveTextContent(raw)
    expect(document.querySelector("iframe")).toBeNull()
    expect(mockedApi).toHaveBeenCalledWith("/api/admin/inbox/messages/m1")
  })

  it("unmatched row: modal omits match line; browse still works (AST-1051)", async () => {
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
    expect(document.querySelector(".manage-email-match--modal")).toBeNull()
    expect(document.querySelector(".manage-email-actions")).toBeNull()
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
    // List-row Create remains available outside the modal.
    expect(screen.getByRole("button", { name: "Create" })).toBeEnabled()
  })

  it("list-row Create POSTs create-job without opening modal (AST-1051)", async () => {
    mockApis(async (url, init) => {
      if (
        url === "/api/admin/inbox/messages/m1/create-job" &&
        init?.method === "POST"
      ) {
        return jsonResponse({
          astral_job_id: "job-42",
          company: "meteorite-cand-ada",
          state: "METEORITE_NEW",
          latest_score: 10,
          company_inserted: true,
          astral_candidate_id: "cand-ada",
          mode: "body",
          created: [
            {
              astral_job_id: "job-42",
              company: "meteorite-cand-ada",
              state: "METEORITE_NEW",
              latest_score: 10,
              company_inserted: true,
            },
          ],
          skipped: [],
        })
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    const matchedRow = screen.getByText("Hello Astral").closest("tr")!
    await userEvent.click(matchedRow.querySelector("button.manage-email-create")!)
    await waitFor(() => expect(screen.getByText("Created job job-42")).toBeInTheDocument())
    expect(screen.queryByRole("heading", { name: "Hello Astral", level: 2 })).not.toBeInTheDocument()
    expect(mockedApi).toHaveBeenCalledWith(
      "/api/admin/inbox/messages/m1/create-job",
      expect.objectContaining({ method: "POST" }),
    )
    expect(mockedApi).not.toHaveBeenCalledWith("/api/admin/inbox/messages/m1")
  })

  it("list-row Create all-skipped toasts skip message (AST-1061)", async () => {
    mockApis(async (url, init) => {
      if (
        url === "/api/admin/inbox/messages/m1/create-job" &&
        init?.method === "POST"
      ) {
        return jsonResponse({
          astral_job_id: null,
          company: "meteorite-cand-ada",
          state: null,
          latest_score: null,
          company_inserted: false,
          astral_candidate_id: "cand-ada",
          mode: "links",
          created: [],
          skipped: [
            {
              reason: "known_job_link",
              url: "https://jobs.example.com/x",
              matched_company_job_id: null,
            },
          ],
        })
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    const matchedRow = screen.getByText("Hello Astral").closest("tr")!
    await userEvent.click(matchedRow.querySelector("button.manage-email-create")!)
    await waitFor(() =>
      expect(screen.getByText("Skipped 1 (already known or empty)")).toBeInTheDocument(),
    )
  })

  it("list-row Create failure toasts error (AST-1051)", async () => {
    mockApis(async (url, init) => {
      if (url === "/api/admin/inbox/messages/m1/create-job" && init?.method === "POST") {
        return jsonResponse({ error: "message is not matched to a candidate" }, false)
      }
    })
    renderWithProviders(<AdminManageEmail />)
    await waitFor(() => expect(screen.getByText("Hello Astral")).toBeInTheDocument())
    const matchedRow = screen.getByText("Hello Astral").closest("tr")!
    await userEvent.click(matchedRow.querySelector("button.manage-email-create")!)
    await waitFor(() =>
      expect(screen.getByText("message is not matched to a candidate")).toBeInTheDocument(),
    )
    expect(screen.queryByRole("heading", { name: "Hello Astral", level: 2 })).not.toBeInTheDocument()
  })
})
