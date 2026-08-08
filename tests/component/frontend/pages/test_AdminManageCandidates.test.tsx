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

  function mockApi(counts: Record<string, number> = { doe_jane: 3 }) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/shapes/candidates") return { json: async () => shapes } as Response
      if (url === "/api/candidates/states") return { json: async () => ["ACTIVE", "DELETED"] } as Response
      if (url === "/api/candidates?include_deleted=true") return { json: async () => [candidate] } as Response
      if (url === "/api/admin/dispatch_tasks/counts") return { ok: true, json: async () => ({ counts }) } as Response
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
      if (url === "/api/admin/dispatch_tasks/counts") {
        countsCalls += 1
        const n = setBody ? 7 : 3
        return { ok: true, json: async () => ({ counts: { doe_jane: n } }) } as Response
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
      if (url === "/api/admin/dispatch_tasks/counts") {
        return { ok: true, json: async () => ({ counts: { doe_jane: 1 } }) } as Response
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
      if (url === "/api/admin/dispatch_tasks/counts") {
        return { ok: true, json: async () => ({ counts: { doe_jane: 0 } }) } as Response
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
})
