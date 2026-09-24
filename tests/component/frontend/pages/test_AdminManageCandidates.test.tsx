import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import ManageCandidates from "../../../../src/ui/frontend/src/pages/AdminManageCandidates"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

const pronounFieldDef = {
  key: "pronouns",
  label: "Pronoun preference",
  type: "select" as const,
  options: [
    { value: "", label: "(not set)" },
    { value: "they/them", label: "they/them" },
    { value: "she/her", label: "she/her" },
    { value: "he/him", label: "he/him" },
  ],
}

const shapes = {
  list: {
    manage: [
      { key: "astral_candidate_id", label: "ID" },
      { key: "first", label: "First" },
      { key: "slack_username", label: "Slack username" },
      { key: "api_key_status", label: "API Key" },
      { key: "dispatch_task_count", label: "Dispatch tasks", type: "int" },
    ],
  },
  detail: {
    profile: [{ label: "Contact Information", fields: [pronounFieldDef] }],
  },
}

const candidate = {
  astral_candidate_id: "doe_jane",
  state: "ACTIVE",
  has_api_key: true,
  first: "Jane",
  last: "Doe",
  pronouns: "she/her",
  candidate_data: {
    contact: { contact_email: "jane@example.com" },
  },
}

/** dep-field labels omit htmlFor; locate sibling input (AST-511 middle field between first/last). */
function textboxByFieldLabel(container: HTMLElement, label: string) {
  const field = within(container).getByText(label, { selector: "label.dep-field-label" }).closest(".dep-field")!
  return within(field as HTMLElement).getByRole("textbox")
}

function comboboxByFieldLabel(container: HTMLElement, label: string) {
  const field = within(container).getByText(label, { selector: "label.dep-field-label" }).closest(".dep-field")!
  return within(field as HTMLElement).getByRole("combobox")
}

describe("AdminManageCandidates", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  function mockApi(
    counts: Record<string, number> = { doe_jane: 3 },
    unbound: { slack_user_id: string; username: string }[] = [],
  ) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") return { json: async () => ["ACTIVE", "DELETED"] } as Response
      if (url === "/api/candidates?include_deleted=true") return { json: async () => [candidate] } as Response
      if (url === "/api/admin/dispatch_tasks/counts") return { ok: true, json: async () => ({ counts }) } as Response
      // AST-1668 sibling GET — default empty so Add/Edit open does not throw Unhandled api.
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        return { ok: true, json: async () => ({ users: unbound }) } as Response
      }
      if (url === "/api/candidates" && init?.method === "POST") return { ok: true, json: async () => ({}) } as Response
      if (url === "/api/candidates/doe_jane/data" && init?.method === "PUT") return { ok: true, json: async () => ({}) } as Response
      if (url === "/api/candidates/doe_jane" && init?.method === "DELETE") return { ok: true, json: async () => ({}) } as Response
    })
  }

  it("renders candidates and supports add, view, edit, and delete", async () => {
    mockApi()
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    expect(screen.getByText("🔑 Set")).toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: "+ Add Candidate" }))
    const addModal = screen.getByText("Add Candidate").closest(".modal-card") as HTMLElement
    fireEvent.change(textboxByFieldLabel(addModal, "First Name"), { target: { value: "New" } })
    fireEvent.change(textboxByFieldLabel(addModal, "Last Name"), { target: { value: "Person" } })
    await userEvent.click(within(addModal as HTMLElement).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText(/Candidate "New Person" created/)).toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "View" }))
    expect(screen.getByText(/"contact_email": "jane@example.com"/)).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Close" }))

    await userEvent.click(screen.getByRole("button", { name: "Edit" }))
    const editModal = screen.getByText(/Edit: doe_jane/).closest(".modal-card")!
    await userEvent.click(within(editModal as HTMLElement).getByRole("button", { name: "Show" }))
    await userEvent.click(within(editModal as HTMLElement).getByRole("button", { name: "Clear" }))
    const clearDialog = await screen.findByRole("alertdialog", { name: "Clear API key" })
    await userEvent.click(within(clearDialog).getByRole("button", { name: "Clear key" }))
    await userEvent.click(within(editModal as HTMLElement).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Candidate updated")).toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "Delete" }))
    const deleteDialog = await screen.findByRole("alertdialog", { name: "Delete candidate" })
    await userEvent.click(within(deleteDialog).getByRole("button", { name: "Delete" }))
    await waitFor(() => expect(screen.getByText(/Candidate "doe_jane" deleted/)).toBeInTheDocument())
  }, 20000)

  it("validates add form and surfaces API errors", async () => {
    mockApi()
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "+ Add Candidate" }))
    await userEvent.click(within(screen.getByText("Add Candidate").closest(".modal-card") as HTMLElement).getByRole("button", { name: "Save" }))
    expect(screen.getByText("First and last name are required")).toBeInTheDocument()

    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates" && init?.method === "POST") {
        return { ok: false, json: async () => ({ error: "Create failed" }) } as Response
      }
    })
    const addModal = screen.getByText("Add Candidate").closest(".modal-card") as HTMLElement
    fireEvent.change(textboxByFieldLabel(addModal, "First Name"), { target: { value: "Bad" } })
    fireEvent.change(textboxByFieldLabel(addModal, "Last Name"), { target: { value: "Request" } })
    await userEvent.click(within(addModal as HTMLElement).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Create failed")).toBeInTheDocument())
  }, 15000)

  it("includes pronouns in create and edit payloads", async () => {
    let postBody: Record<string, unknown> | null = null
    let putBody: Record<string, unknown> | null = null
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") return { json: async () => ["ACTIVE", "DELETED"] } as Response
      if (url === "/api/candidates?include_deleted=true") return { json: async () => [candidate] } as Response
      if (url === "/api/admin/dispatch_tasks/counts") return { ok: true, json: async () => ({ counts: { doe_jane: 3 } }) } as Response
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        return { ok: true, json: async () => ({ users: [] }) } as Response
      }
      if (url === "/api/candidates" && init?.method === "POST") {
        postBody = JSON.parse(String(init.body))
        return { ok: true, json: async () => ({}) } as Response
      }
      if (url === "/api/candidates/doe_jane/data" && init?.method === "PUT") {
        putBody = JSON.parse(String(init.body))
        return { ok: true, json: async () => ({}) } as Response
      }
      if (url === "/api/candidates/doe_jane" && init?.method === "DELETE") return { ok: true, json: async () => ({}) } as Response
    })
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "+ Add Candidate" }))
    const addModal = screen.getByText("Add Candidate").closest(".modal-card") as HTMLElement
    fireEvent.change(textboxByFieldLabel(addModal, "First Name"), { target: { value: "Pat" } })
    fireEvent.change(textboxByFieldLabel(addModal, "Last Name"), { target: { value: "Smith" } })
    await userEvent.selectOptions(comboboxByFieldLabel(addModal, "Pronoun preference"), "they/them")
    await userEvent.click(within(addModal).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(postBody).not.toBeNull())
    expect((postBody!.candidate_data as { contact: { contact_email: string } }).contact.contact_email).toBe("")
    expect(postBody!.pronouns).toBe("they/them")

    await userEvent.click(screen.getByRole("button", { name: "Edit" }))
    const editModal = screen.getByText(/Edit: doe_jane/).closest(".modal-card") as HTMLElement
    expect(comboboxByFieldLabel(editModal, "Pronoun preference")).toHaveDisplayValue("she/her")
    await userEvent.selectOptions(comboboxByFieldLabel(editModal, "Pronoun preference"), "he/him")
    await userEvent.click(within(editModal).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(putBody).not.toBeNull())
    expect(putBody!.pronouns).toBe("he/him")

    await userEvent.click(screen.getByRole("button", { name: "Edit" }))
    const editClear = screen.getByText(/Edit: doe_jane/).closest(".modal-card") as HTMLElement
    await userEvent.selectOptions(comboboxByFieldLabel(editClear, "Pronoun preference"), "")
    putBody = null
    await userEvent.click(within(editClear).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(putBody).not.toBeNull())
    expect(putBody!.pronouns).toBe("")
  }, 20000)

  // AST-511 canceled — no middle field on AdminManageCandidates until ticket is revived.
  it.skip("includes profile.middle in create and edit payloads", async () => {
    let postBody: Record<string, unknown> | null = null
    let putBody: Record<string, unknown> | null = null
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") return { json: async () => ["ACTIVE", "DELETED"] } as Response
      if (url === "/api/candidates?include_deleted=true") return { json: async () => [candidate] } as Response
      if (url === "/api/admin/dispatch_tasks/counts") return { ok: true, json: async () => ({ counts: { doe_jane: 3 } }) } as Response
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        return { ok: true, json: async () => ({ users: [] }) } as Response
      }
      if (url === "/api/candidates" && init?.method === "POST") {
        postBody = JSON.parse(String(init.body))
        return { ok: true, json: async () => ({}) } as Response
      }
      if (url === "/api/candidates/doe_jane/data" && init?.method === "PUT") {
        putBody = JSON.parse(String(init.body))
        return { ok: true, json: async () => ({}) } as Response
      }
      if (url === "/api/candidates/doe_jane" && init?.method === "DELETE") return { ok: true, json: async () => ({}) } as Response
    })
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "+ Add Candidate" }))
    const addModal = screen.getByText("Add Candidate").closest(".modal-card") as HTMLElement
    fireEvent.change(textboxByFieldLabel(addModal, "First Name"), { target: { value: "Pat" } })
    fireEvent.change(textboxByFieldLabel(addModal, "Middle Name"), { target: { value: "Lee" } })
    fireEvent.change(textboxByFieldLabel(addModal, "Last Name"), { target: { value: "Smith" } })
    await userEvent.click(within(addModal as HTMLElement).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(postBody).not.toBeNull())
    expect((postBody!.candidate_data as { profile: { middle: string } }).profile.middle).toBe("Lee")

    await userEvent.click(screen.getByRole("button", { name: "Edit" }))
    const editModal = screen.getByText(/Edit: doe_jane/).closest(".modal-card") as HTMLElement
    fireEvent.change(textboxByFieldLabel(editModal, "Middle Name"), { target: { value: "Quinn" } })
    await userEvent.click(within(editModal).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(putBody).not.toBeNull())
    expect((putBody!.profile as { middle: string }).middle).toBe("Quinn")
  }, 15000)

  it.skip("creates candidate with empty middle when first and last are set", async () => {
    let postBody: Record<string, unknown> | null = null
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") return { json: async () => ["ACTIVE"] } as Response
      if (url === "/api/candidates?include_deleted=true") return { json: async () => [] } as Response
      if (url === "/api/admin/dispatch_tasks/counts") return { ok: true, json: async () => ({ counts: {} }) } as Response
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        return { ok: true, json: async () => ({ users: [] }) } as Response
      }
      if (url === "/api/candidates" && init?.method === "POST") {
        postBody = JSON.parse(String(init.body))
        return { ok: true, json: async () => ({}) } as Response
      }
    })
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "+ Add Candidate" }))
    const addModal = screen.getByText("Add Candidate").closest(".modal-card") as HTMLElement
    fireEvent.change(textboxByFieldLabel(addModal, "First Name"), { target: { value: "Only" } })
    fireEvent.change(textboxByFieldLabel(addModal, "Last Name"), { target: { value: "Names" } })
    await userEvent.click(within(addModal as HTMLElement).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(postBody).not.toBeNull())
    expect((postBody!.candidate_data as { profile: { middle: string } }).profile.middle).toBe("")
  }, 15000)

  // AST-876: dispatch-task count column + Set dispatch tasks (confirm → set_from_template).
  it("shows dispatch task count and sets from template after confirm", async () => {
    let setBody: Record<string, unknown> | null = null
    let countsCalls = 0
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") return { json: async () => ["ACTIVE", "DELETED"] } as Response
      if (url === "/api/candidates?include_deleted=true") return { json: async () => [candidate] } as Response
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        return { ok: true, json: async () => ({ users: [] }) } as Response
      }
      if (url === "/api/admin/dispatch_tasks/counts") {
        countsCalls += 1
        const n = setBody ? 7 : 3
        return { ok: true, json: async () => ({ counts: { doe_jane: n } }) } as Response
      }
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        return { ok: true, json: async () => ({ users: [] }) } as Response
      }
      if (url === "/api/admin/dispatch_tasks/set_from_template" && init?.method === "POST") {
        setBody = JSON.parse(String(init.body))
        return {
          ok: true,
          json: async () => ({
            candidate_id: "doe_jane",
            template_candidate_id: "somerset",
            inserted: 2,
            updated: 1,
            deleted: 0,
            count: 7,
          }),
        } as Response
      }
    })
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    expect(screen.getByText("Dispatch tasks")).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText("3")).toBeInTheDocument())
    expect(countsCalls).toBeGreaterThanOrEqual(1)

    await userEvent.click(screen.getByRole("button", { name: "Set dispatch tasks for doe_jane" }))
    const dialog = await screen.findByRole("alertdialog", { name: "Set dispatch tasks" })
    await userEvent.click(within(dialog).getByRole("button", { name: "Set tasks" }))
    await waitFor(() => expect(setBody).toEqual({ candidate_id: "doe_jane" }))
    await waitFor(() => expect(screen.getByText('Dispatch tasks set for "doe_jane" (7 rows)')).toBeInTheDocument())
    await waitFor(() => expect(screen.getByText("7")).toBeInTheDocument())
    // Must not call run/execution endpoints
    const urls = mockedApi.mock.calls.map(c => String(c[0]))
    expect(urls.some(u => u.includes("/run") || u.includes("/stop"))).toBe(false)
  }, 20000)

  it("does not POST set_from_template when confirm is cancelled", async () => {
    mockApi()
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Set dispatch tasks for doe_jane" }))
    const dialog = await screen.findByRole("alertdialog", { name: "Set dispatch tasks" })
    await userEvent.click(within(dialog).getByRole("button", { name: "Cancel" }))
    expect(
      mockedApi.mock.calls.some(
        c => c[0] === "/api/admin/dispatch_tasks/set_from_template" && (c[1] as RequestInit | undefined)?.method === "POST",
      ),
    ).toBe(false)
  }, 15000)

  it("surfaces set_from_template API errors", async () => {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") return { json: async () => ["ACTIVE", "DELETED"] } as Response
      if (url === "/api/candidates?include_deleted=true") return { json: async () => [candidate] } as Response
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        return { ok: true, json: async () => ({ users: [] }) } as Response
      }
      if (url === "/api/admin/dispatch_tasks/counts") {
        return { ok: true, json: async () => ({ counts: { doe_jane: 1 } }) } as Response
      }
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        return { ok: true, json: async () => ({ users: [] }) } as Response
      }
      if (url === "/api/admin/dispatch_tasks/set_from_template" && init?.method === "POST") {
        return { ok: false, json: async () => ({ error: "Candidate not found: doe_jane" }) } as Response
      }
    })
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Set dispatch tasks for doe_jane" }))
    const dialog = await screen.findByRole("alertdialog", { name: "Set dispatch tasks" })
    await userEvent.click(within(dialog).getByRole("button", { name: "Set tasks" }))
    await waitFor(() => expect(screen.getByText("Candidate not found: doe_jane")).toBeInTheDocument())
  }, 15000)

  // AST-1288: illegal-hop are-you-sure → confirm_state_override retry (AST-1287 contract)
  const hopCandidate = {
    ...candidate,
    state: "NEW_CANDIDATE",
  }

  function mockIllegalHopApi(opts: {
    onIllegal?: (body: Record<string, unknown>) => void
    confirmOk?: boolean
  } = {}) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") {
        return { json: async () => ["NEW_CANDIDATE", "ACTIVE_SEARCH", "NOT_A_STATE"] } as Response
      }
      if (url === "/api/candidates?include_deleted=true") {
        return { json: async () => [hopCandidate] } as Response
      }
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        return { ok: true, json: async () => ({ users: [] }) } as Response
      }
      if (url === "/api/admin/dispatch_tasks/counts") {
        return { ok: true, json: async () => ({ counts: { doe_jane: 0 } }) } as Response
      }
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        return { ok: true, json: async () => ({ users: [] }) } as Response
      }
      if (url === "/api/candidates/doe_jane/data" && init?.method === "PUT") {
        const body = JSON.parse(String(init.body)) as Record<string, unknown>
        if (body.confirm_state_override === true) {
          return { ok: opts.confirmOk !== false, json: async () => (opts.confirmOk === false ? { error: "force failed" } : {}) } as Response
        }
        if (body.state === "ACTIVE_SEARCH") {
          opts.onIllegal?.(body)
          return {
            ok: false,
            json: async () => ({
              error: "Invalid candidate state transition: NEW_CANDIDATE -> ACTIVE_SEARCH",
              code: "illegal_candidate_transition",
              from_state: "NEW_CANDIDATE",
              to_state: "ACTIVE_SEARCH",
            }),
          } as Response
        }
        if (body.state === "NOT_A_STATE") {
          return { ok: false, json: async () => ({ error: "Unknown candidate state: NOT_A_STATE" }) } as Response
        }
        return { ok: true, json: async () => ({}) } as Response
      }
    })
  }

  it("AST-1288: illegal hop shows from→to confirm; confirm retries with override", async () => {
    const firstBodies: Record<string, unknown>[] = []
    mockIllegalHopApi({ onIllegal: b => firstBodies.push(b) })
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Edit" }))
    const editModal = screen.getByText(/Edit: doe_jane/).closest(".modal-card")!
    fireEvent.change(comboboxByFieldLabel(editModal as HTMLElement, "State (admin override)"), {
      target: { value: "ACTIVE_SEARCH" },
    })
    await userEvent.click(within(editModal as HTMLElement).getByRole("button", { name: "Save" }))
    const dialog = await screen.findByRole("alertdialog", { name: "Confirm illegal state change" })
    expect(dialog).toHaveTextContent("NEW_CANDIDATE → ACTIVE_SEARCH")
    expect(firstBodies[0]?.confirm_state_override).toBeUndefined()
    await userEvent.click(within(dialog).getByRole("button", { name: "Change state" }))
    await waitFor(() => expect(screen.getByText("Candidate updated")).toBeInTheDocument())
    const puts = mockedApi.mock.calls.filter(
      c => c[0] === "/api/candidates/doe_jane/data" && (c[1] as RequestInit)?.method === "PUT",
    )
    expect(puts).toHaveLength(2)
    const retry = JSON.parse(String((puts[1][1] as RequestInit).body))
    expect(retry.state).toBe("ACTIVE_SEARCH")
    expect(retry.confirm_state_override).toBe(true)
  }, 20000)

  it("AST-1288: cancel illegal confirm leaves state unchanged and does not send override", async () => {
    mockIllegalHopApi()
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Edit" }))
    const editModal = screen.getByText(/Edit: doe_jane/).closest(".modal-card")!
    fireEvent.change(comboboxByFieldLabel(editModal as HTMLElement, "State (admin override)"), {
      target: { value: "ACTIVE_SEARCH" },
    })
    await userEvent.click(within(editModal as HTMLElement).getByRole("button", { name: "Save" }))
    const dialog = await screen.findByRole("alertdialog", { name: "Confirm illegal state change" })
    await userEvent.click(within(dialog).getByRole("button", { name: "Cancel" }))
    await waitFor(() =>
      expect(screen.getByText("State unchanged; other fields saved if they were.")).toBeInTheDocument(),
    )
    // Modal stays open; state select reset to from_state
    expect(screen.getByText(/Edit: doe_jane/)).toBeInTheDocument()
    expect(comboboxByFieldLabel(editModal as HTMLElement, "State (admin override)")).toHaveValue("NEW_CANDIDATE")
    const puts = mockedApi.mock.calls.filter(
      c => c[0] === "/api/candidates/doe_jane/data" && (c[1] as RequestInit)?.method === "PUT",
    )
    expect(puts).toHaveLength(1)
    expect(JSON.parse(String((puts[0][1] as RequestInit).body)).confirm_state_override).toBeUndefined()
  }, 20000)

  it("AST-1288: legal hop saves without illegal-state confirm", async () => {
    mockIllegalHopApi()
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Edit" }))
    const editModal = screen.getByText(/Edit: doe_jane/).closest(".modal-card")!
    fireEvent.change(textboxByFieldLabel(editModal as HTMLElement, "First Name"), {
      target: { value: "Janet" },
    })
    await userEvent.click(within(editModal as HTMLElement).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Candidate updated")).toBeInTheDocument())
    expect(screen.queryByRole("alertdialog", { name: "Confirm illegal state change" })).toBeNull()
    const puts = mockedApi.mock.calls.filter(
      c => c[0] === "/api/candidates/doe_jane/data" && (c[1] as RequestInit)?.method === "PUT",
    )
    expect(puts).toHaveLength(1)
    expect(JSON.parse(String((puts[0][1] as RequestInit).body)).confirm_state_override).toBeUndefined()
  }, 20000)

  it("AST-1288: unknown-state 400 does not open illegal confirm", async () => {
    mockIllegalHopApi()
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Edit" }))
    const editModal = screen.getByText(/Edit: doe_jane/).closest(".modal-card")!
    fireEvent.change(comboboxByFieldLabel(editModal as HTMLElement, "State (admin override)"), {
      target: { value: "NOT_A_STATE" },
    })
    await userEvent.click(within(editModal as HTMLElement).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText(/Unknown candidate state/)).toBeInTheDocument())
    expect(screen.queryByRole("alertdialog", { name: "Confirm illegal state change" })).toBeNull()
  }, 20000)

  it("AST-1302: row actions are icon-control (View/Edit/Delete SVGs + T)", async () => {
    mockApi()
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    const view = screen.getByRole("button", { name: "View" })
    const edit = screen.getByRole("button", { name: "Edit" })
    const del = screen.getByRole("button", { name: "Delete" })
    const setTasks = screen.getByRole("button", { name: "Set dispatch tasks for doe_jane" })
    expect(view).toHaveClass("icon-control")
    expect(edit).toHaveClass("icon-control")
    expect(del).toHaveClass("icon-control")
    expect(setTasks).toHaveClass("icon-control")
    expect(setTasks).toHaveTextContent("T")
    expect(setTasks).not.toHaveTextContent("Set dispatch tasks")
    const snap = screen.getByRole("button", { name: "Snapshot Slack channel for doe_jane" })
    expect(snap).toHaveClass("icon-control")
    expect(snap).toHaveTextContent("S")
    expect(view).not.toHaveClass("list-page-edit-btn")
    expect(setTasks).not.toHaveClass("dep-btn")
  }, 20000)

  // AST-1669: Manage Candidates Slack bind dropdown (§6c routed page).
  it("AST-1669: add stamps slack_user_id + slack_username from unbound dropdown", async () => {
    let postBody: Record<string, unknown> | null = null
    let unboundCalls = 0
    const unboundPool = [
      { slack_user_id: "U_ADA", username: "ada.lovelace" },
      { slack_user_id: "U_HEDY", username: "hedy.lamarr" },
    ]
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") return { json: async () => ["ACTIVE", "DELETED"] } as Response
      if (url === "/api/candidates?include_deleted=true") return { json: async () => [candidate] } as Response
      if (url === "/api/admin/dispatch_tasks/counts") {
        return { ok: true, json: async () => ({ counts: { doe_jane: 3 } }) } as Response
      }
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        unboundCalls += 1
        // After bind: pool drops U_ADA (AC6 — sibling GET omits bound id).
        const users = unboundCalls > 1 ? unboundPool.filter(u => u.slack_user_id !== "U_ADA") : unboundPool
        return { ok: true, json: async () => ({ users }) } as Response
      }
      if (url === "/api/candidates" && init?.method === "POST") {
        postBody = JSON.parse(String(init.body))
        return { ok: true, json: async () => ({}) } as Response
      }
    })
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "+ Add Candidate" }))
    const addModal = screen.getByText("Add Candidate").closest(".modal-card") as HTMLElement
    await waitFor(() => expect(unboundCalls).toBeGreaterThanOrEqual(1))
    const slackSelect = comboboxByFieldLabel(addModal, "Slack username")
    expect(within(slackSelect).getByRole("option", { name: "— none —" })).toBeInTheDocument()
    expect(within(slackSelect).getByRole("option", { name: "ada.lovelace" })).toBeInTheDocument()
    expect(within(slackSelect).getByRole("option", { name: "hedy.lamarr" })).toBeInTheDocument()
    // No Slack Web API from React — only sibling admin GET.
    expect(mockedApi.mock.calls.every(c => !String(c[0]).includes("slack.com"))).toBe(true)

    fireEvent.change(textboxByFieldLabel(addModal, "First Name"), { target: { value: "Ada" } })
    fireEvent.change(textboxByFieldLabel(addModal, "Last Name"), { target: { value: "Lovelace" } })
    await userEvent.selectOptions(slackSelect, "U_ADA")
    await userEvent.click(within(addModal).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(postBody).not.toBeNull())
    const contact = (postBody!.candidate_data as { contact: Record<string, string> }).contact
    expect(contact.slack_user_id).toBe("U_ADA")
    expect(contact.slack_username).toBe("ada.lovelace")
    await waitFor(() => expect(unboundCalls).toBeGreaterThanOrEqual(2))
  }, 20000)

  it("AST-1669: edit prepends current bind; empty selection omits Slack keys", async () => {
    const boundCandidate = {
      ...candidate,
      candidate_data: {
        contact: {
          contact_email: "jane@example.com",
          slack_user_id: "U_BOUND",
          slack_username: "jane.bound",
        },
      },
    }
    let putBody: Record<string, unknown> | null = null
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") return { json: async () => ["ACTIVE", "DELETED"] } as Response
      if (url === "/api/candidates?include_deleted=true") {
        return { json: async () => [boundCandidate] } as Response
      }
      if (url === "/api/admin/dispatch_tasks/counts") {
        return { ok: true, json: async () => ({ counts: { doe_jane: 3 } }) } as Response
      }
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        // Bound id absent from unbound (already bound) — page prepends synthetic option.
        return {
          ok: true,
          json: async () => ({ users: [{ slack_user_id: "U_FREE", username: "free.user" }] }),
        } as Response
      }
      if (url === "/api/candidates/doe_jane/data" && init?.method === "PUT") {
        putBody = JSON.parse(String(init.body))
        return { ok: true, json: async () => ({}) } as Response
      }
    })
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "Edit" }))
    const editModal = screen.getByText(/Edit: doe_jane/).closest(".modal-card") as HTMLElement
    const slackSelect = comboboxByFieldLabel(editModal, "Slack username")
    await waitFor(() => expect(slackSelect).toHaveValue("U_BOUND"))
    expect(within(slackSelect).getByRole("option", { name: "jane.bound" })).toBeInTheDocument()
    expect(within(slackSelect).getByRole("option", { name: "free.user" })).toBeInTheDocument()

    // Empty selection → omit Slack keys (no accidental unbind).
    await userEvent.selectOptions(slackSelect, "")
    fireEvent.change(textboxByFieldLabel(editModal, "First Name"), { target: { value: "Janet" } })
    await userEvent.click(within(editModal).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(putBody).not.toBeNull())
    const contact = putBody!.contact as Record<string, string>
    expect(contact.contact_email).toBe("jane@example.com")
    expect(contact.slack_user_id).toBeUndefined()
    expect(contact.slack_username).toBeUndefined()
  }, 20000)

  it("AST-1669: add dropdown stamps slack_user_id + slack_username via admin GET", async () => {
    let postBody: Record<string, unknown> | null = null
    let unboundCalls = 0
    const free = { slack_user_id: "U_FREE", username: "free.user" }
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") return { json: async () => ["ACTIVE", "DELETED"] } as Response
      if (url === "/api/candidates?include_deleted=true") return { json: async () => [candidate] } as Response
      if (url === "/api/admin/dispatch_tasks/counts") return { ok: true, json: async () => ({ counts: { doe_jane: 3 } }) } as Response
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        unboundCalls += 1
        // After bind, sibling GET omits the newly bound id (AC6).
        const users = unboundCalls <= 1 ? [free] : []
        return { ok: true, json: async () => ({ users }) } as Response
      }
      if (url === "/api/candidates" && init?.method === "POST") {
        postBody = JSON.parse(String(init.body))
        return { ok: true, json: async () => ({}) } as Response
      }
    })
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "+ Add Candidate" }))
    const addModal = screen.getByText("Add Candidate").closest(".modal-card") as HTMLElement
    await waitFor(() => expect(comboboxByFieldLabel(addModal, "Slack username")).toBeInTheDocument())
    const slackSelect = comboboxByFieldLabel(addModal, "Slack username")
    expect(within(slackSelect).getByRole("option", { name: "— none —" })).toBeInTheDocument()
    expect(within(slackSelect).getByRole("option", { name: "free.user" })).toBeInTheDocument()
    // Already-bound usernames are not in the unbound GET — not shown as free choices.
    expect(within(slackSelect).queryByRole("option", { name: "bound.other" })).toBeNull()
    fireEvent.change(textboxByFieldLabel(addModal, "First Name"), { target: { value: "New" } })
    fireEvent.change(textboxByFieldLabel(addModal, "Last Name"), { target: { value: "Bind" } })
    await userEvent.selectOptions(slackSelect, "U_FREE")
    await userEvent.click(within(addModal).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(postBody).not.toBeNull())
    const contact = (postBody!.candidate_data as { contact: Record<string, string> }).contact
    expect(contact.slack_user_id).toBe("U_FREE")
    expect(contact.slack_username).toBe("free.user")
    // Refresh unbound after bind (second GET).
    await waitFor(() => expect(unboundCalls).toBeGreaterThanOrEqual(2))
    // Pool source is admin GET only — never Slack Web API hosts.
    const urls = mockedApi.mock.calls.map(c => String(c[0]))
    expect(urls.some(u => u.includes("slack.com") || u.includes("users.list"))).toBe(false)
    expect(urls).toContain("/api/admin/contact/unbound_slack_users")
  }, 20000)

  it("AST-1669: edit keeps current bind option; empty selection omits Slack keys", async () => {
    let putBody: Record<string, unknown> | null = null
    const boundCand = {
      ...candidate,
      candidate_data: {
        contact: {
          contact_email: "jane@example.com",
          slack_user_id: "U_BOUND",
          slack_username: "jane.slack",
        },
      },
    }
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") return { json: async () => ["ACTIVE", "DELETED"] } as Response
      if (url === "/api/candidates?include_deleted=true") return { json: async () => [boundCand] } as Response
      if (url === "/api/admin/dispatch_tasks/counts") return { ok: true, json: async () => ({ counts: { doe_jane: 3 } }) } as Response
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        return {
          ok: true,
          json: async () => ({ users: [{ slack_user_id: "U_FREE", username: "free.user" }] }),
        } as Response
      }
      if (url === "/api/candidates/doe_jane/data" && init?.method === "PUT") {
        putBody = JSON.parse(String(init.body))
        return { ok: true, json: async () => ({}) } as Response
      }
    })
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Edit" }))
    const editModal = screen.getByText(/Edit: doe_jane/).closest(".modal-card") as HTMLElement
    const slackSelect = comboboxByFieldLabel(editModal, "Slack username")
    await waitFor(() => expect(within(slackSelect).getByRole("option", { name: "jane.slack" })).toBeInTheDocument())
    expect(slackSelect).toHaveValue("U_BOUND")
    expect(within(slackSelect).getByRole("option", { name: "free.user" })).toBeInTheDocument()
    // Empty selection must not clear existing bind (omit Slack keys from PUT).
    await userEvent.selectOptions(slackSelect, "")
    await userEvent.click(within(editModal).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(putBody).not.toBeNull())
    const contact = putBody!.contact as Record<string, string>
    expect(contact.slack_user_id).toBeUndefined()
    expect(contact.slack_username).toBeUndefined()
    expect(contact.contact_email).toBe("jane@example.com")
  }, 20000)


  // AST-1789: channel column, membership warning, S snapshot (§6c routed page).
  it("AST-1789: list shows slack_username or em dash placeholder", async () => {
    const withUser = {
      ...candidate,
      candidate_data: {
        contact: { contact_email: "jane@example.com", slack_username: "jane.bound" },
      },
    }
    const unbound = {
      ...candidate,
      astral_candidate_id: "doe_unbound",
      first: "Un",
      last: "Bound",
      candidate_data: { contact: { contact_email: "u@example.com" } },
    }
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") return { json: async () => ["ACTIVE", "DELETED"] } as Response
      if (url === "/api/candidates?include_deleted=true") {
        return { json: async () => [withUser, unbound] } as Response
      }
      if (url === "/api/admin/dispatch_tasks/counts") {
        return { ok: true, json: async () => ({ counts: { doe_jane: 1, doe_unbound: 0 } }) } as Response
      }
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        return { ok: true, json: async () => ({ users: [] }) } as Response
      }
    })
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    expect(screen.getByText("jane.bound")).toBeInTheDocument()
    // Empty username → em dash placeholder in slack_username column.
    const dashes = screen.getAllByText("—")
    expect(dashes.length).toBeGreaterThanOrEqual(1)
  }, 20000)

  it("AST-1789: add stamps channel id+name; unbound warn without membership GET", async () => {
    let postBody: Record<string, unknown> | null = null
    const channels = [
      { id: "C_ALPHA", name: "alpha" },
      { id: "C_EMPTY", name: "" },
    ]
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") return { json: async () => ["ACTIVE", "DELETED"] } as Response
      if (url === "/api/candidates?include_deleted=true") return { json: async () => [candidate] } as Response
      if (url === "/api/admin/dispatch_tasks/counts") {
        return { ok: true, json: async () => ({ counts: { doe_jane: 3 } }) } as Response
      }
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        return { ok: true, json: async () => ({ users: [] }) } as Response
      }
      if (url.includes("/api/admin/contact/slack_channel_membership")) {
        throw new Error("membership must not be called on add")
      }
      if (url === "/api/candidates" && init?.method === "POST") {
        postBody = JSON.parse(String(init.body))
        return { ok: true, json: async () => ({}) } as Response
      }
    })
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "+ Add Candidate" }))
    const addModal = screen.getByText("Add Candidate").closest(".modal-card") as HTMLElement
    const channelSelect = comboboxByFieldLabel(addModal, "Slack channel")
    await waitFor(() =>
      expect(within(channelSelect).getByRole("option", { name: "alpha" })).toBeInTheDocument(),
    )
    expect(within(channelSelect).getByRole("option", { name: "(unnamed)" })).toBeInTheDocument()
    await userEvent.selectOptions(channelSelect, "C_ALPHA")
    expect(await within(addModal).findByRole("alert")).toHaveTextContent(
      /no Slack user is bound/i,
    )
    expect(mockedApi.mock.calls.every(c => !String(c[0]).includes("slack_channel_membership"))).toBe(
      true,
    )
    expect(mockedApi.mock.calls.every(c => !String(c[0]).includes("slack.com"))).toBe(true)

    fireEvent.change(textboxByFieldLabel(addModal, "First Name"), { target: { value: "Ada" } })
    fireEvent.change(textboxByFieldLabel(addModal, "Last Name"), { target: { value: "Lovelace" } })
    await userEvent.click(within(addModal).getByRole("button", { name: "Save" }))
    await waitFor(() => expect(postBody).not.toBeNull())
    const contact = (postBody!.candidate_data as { contact: Record<string, string> }).contact
    expect(contact.slack_channel_id).toBe("C_ALPHA")
    expect(contact.slack_channel_name).toBe("alpha")
  }, 20000)

  it("AST-1789: edit membership warn for not_member; clears when member", async () => {
    const bound = {
      ...candidate,
      candidate_data: {
        contact: {
          contact_email: "jane@example.com",
          slack_user_id: "U_BOUND",
          slack_username: "jane.bound",
          slack_channel_id: "C1",
          slack_channel_name: "general",
        },
      },
    }
    let membershipCalls = 0
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") return { json: async () => ["ACTIVE", "DELETED"] } as Response
      if (url === "/api/candidates?include_deleted=true") return { json: async () => [bound] } as Response
      if (url === "/api/admin/dispatch_tasks/counts") {
        return { ok: true, json: async () => ({ counts: { doe_jane: 1 } }) } as Response
      }
      if (url === "/api/admin/contact/slack_channels") {
        return {
          ok: true,
          json: async () => ({
            channels: [
              { id: "C1", name: "general" },
              { id: "C2", name: "private" },
            ],
          }),
        } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        return { ok: true, json: async () => ({ users: [] }) } as Response
      }
      if (url.startsWith("/api/admin/contact/slack_channel_membership")) {
        membershipCalls += 1
        const u = new URL(url, "http://local")
        const channel = u.searchParams.get("channel")
        if (channel === "C2") {
          return {
            ok: true,
            json: async () => ({
              channel: "C2",
              slack_user_id: "U_BOUND",
              is_member: false,
              warn: true,
              warn_reason: "not_member",
            }),
          } as Response
        }
        return {
          ok: true,
          json: async () => ({
            channel: channel,
            slack_user_id: "U_BOUND",
            is_member: true,
            warn: false,
            warn_reason: null,
          }),
        } as Response
      }
    })
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Edit" }))
    const editModal = screen.getByText(/Edit: doe_jane/).closest(".modal-card") as HTMLElement
    const channelSelect = comboboxByFieldLabel(editModal, "Slack channel")
    await waitFor(() => expect(channelSelect).toHaveValue("C1"))
    // openEdit re-checks stored channel — member → no alert
    await waitFor(() => expect(membershipCalls).toBeGreaterThanOrEqual(1))
    expect(within(editModal).queryByRole("alert")).toBeNull()

    await userEvent.selectOptions(channelSelect, "C2")
    expect(await within(editModal).findByRole("alert")).toHaveTextContent(
      /not a member of this channel/i,
    )

    await userEvent.selectOptions(channelSelect, "C1")
    await waitFor(() => expect(within(editModal).queryByRole("alert")).toBeNull())
  }, 20000)

  it("AST-1789: S icon-control copies snapshot JSON to clipboard", async () => {
    const withChannel = {
      ...candidate,
      candidate_data: {
        contact: {
          contact_email: "jane@example.com",
          slack_channel_id: "C_SNAP",
          slack_channel_name: "snap",
        },
      },
    }
    const snapshotBody = {
      astral_candidate_id: "doe_jane",
      channel_id: "C_SNAP",
      channel_name: "snap",
      messages: [{ ts: "1.0", text: "hi" }, { ts: "2.0", text: "later" }],
    }
    const writeText = vi.fn(async () => undefined)
    Object.assign(navigator, { clipboard: { writeText } })

    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") return { json: async () => ["ACTIVE", "DELETED"] } as Response
      if (url === "/api/candidates?include_deleted=true") {
        return { json: async () => [withChannel] } as Response
      }
      if (url === "/api/admin/dispatch_tasks/counts") {
        return { ok: true, json: async () => ({ counts: { doe_jane: 1 } }) } as Response
      }
      if (url === "/api/admin/contact/slack_channels") {
        return { ok: true, json: async () => ({ channels: [] }) } as Response
      }
      if (url === "/api/admin/contact/unbound_slack_users") {
        return { ok: true, json: async () => ({ users: [] }) } as Response
      }
      if (url.startsWith("/api/admin/contact/slack_channel_snapshot")) {
        return { ok: true, json: async () => snapshotBody } as Response
      }
    })
    renderWithProviders(<ManageCandidates />)
    await waitFor(() => expect(screen.getByText("Manage Candidates")).toBeInTheDocument())
    const snap = screen.getByRole("button", { name: "Snapshot Slack channel for doe_jane" })
    expect(snap).toHaveClass("icon-control")
    await userEvent.click(snap)
    await waitFor(() => expect(writeText).toHaveBeenCalled())
    expect(writeText.mock.calls[0][0]).toBe(JSON.stringify(snapshotBody, null, 2))
    expect(screen.getByText("Slack channel snapshot copied")).toBeInTheDocument()
    expect(
      mockedApi.mock.calls.some(c =>
        String(c[0]).startsWith("/api/admin/contact/slack_channel_snapshot"),
      ),
    ).toBe(true)
    expect(mockedApi.mock.calls.every(c => !String(c[0]).includes("slack.com"))).toBe(true)
  }, 20000)


})
