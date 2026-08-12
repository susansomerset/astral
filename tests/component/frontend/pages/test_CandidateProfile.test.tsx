import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import CandidateProfile from "../../../../src/ui/frontend/src/pages/CandidateProfile"
import { renderWithProviders } from "../test-utils"
import { candidateId, jsonResponse } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

/** Profile mounts the real helper → useBlocker needs a data router; capture wiring instead. */
const dirtyLeave = vi.fn()
vi.mock("../../../../src/ui/frontend/src/hooks/useDirtyLeaveSaveThenNavigate", () => ({
  useDirtyLeaveSaveThenNavigate: (opts: { isDirty: boolean; onSave: () => Promise<void> }) => {
    dirtyLeave(opts)
  },
}))

const mockedApi = vi.mocked(api)

function latestDirtyLeave(): { isDirty: boolean; onSave: () => Promise<void> } {
  const last = dirtyLeave.mock.calls.at(-1)?.[0] as
    | { isDirty: boolean; onSave: () => Promise<void> }
    | undefined
  if (!last) throw new Error("useDirtyLeaveSaveThenNavigate was not called")
  return last
}

const profileSections = {
  detail: {
    profile: [
      {
        label: "Contact Information",
        fields: [
          { key: "first", label: "First Name", type: "text" },
          { key: "last", label: "Last Name", type: "text" },
          { key: "full", label: "Full Name", type: "text" },
          { key: "contact.contact_email", label: "Email for Resume", type: "text" },
          { key: "contact.reply_email", label: "Email for Messages (if different)", type: "text" },
          { key: "contact.extra_emails", label: "Extra emails (binding)", type: "string_list" },
          {
            key: "pronouns",
            label: "Pronoun preference",
            type: "select",
            options: [
              { value: "", label: "(not set)" },
              { value: "they/them", label: "they/them" },
              { value: "she/her", label: "she/her" },
              { value: "he/him", label: "he/him" },
            ],
          },
          { key: "contact.github", label: "GitHub (username or URL)", type: "text" },
          { key: "contact.linkedin_url", label: "LinkedIn (username or URL)", type: "text" },
          { key: "contact.websites", label: "Websites", type: "string_list" },
          { key: "contact.reason_codes", label: "Reason Codes", type: "textarea" },
        ],
      },
      {
        label: "Bio Summary",
        fields: [{ key: "context.bio_summary", label: "Bio Summary", type: "textarea" }],
      },
      {
        label: "Original Resume Text",
        fields: [{ key: "context.raw_resume", label: "Original Resume Text", type: "textarea" }],
      },
      {
        label: "Title Patterns",
        fields: [{ key: "contact.title_patterns", label: "Title Patterns (one regex per line)", type: "textarea" }],
      },
      {
        label: "Cover Letter From",
        fields: [
          {
            key: "contact.cover_letter_from_block",
            label: "Cover letter From block",
            type: "textarea",
            placeholder: "{$FULL_NAME} | {$LOCATION}\n{$CONTACT_EMAIL} | {$PHONE}",
            help: "Allowed tokens: {$FULL_NAME}, {$LOCATION}, {$CONTACT_EMAIL}, {$PHONE}. Type | between segments; cover print shows •. Leave empty to use the default template (see placeholder).",
          },
        ],
      },
      {
        label: "Signature Image",
        fields: [{ key: "contact.cover_letter_signature_image", label: "Signature Image", type: "signature_image" }],
      },
    ],
  },
}

const candidateData = {
  first: "Ada",
  last: "Lovelace",
  full: "Ada Lovelace",
  pronouns: "they/them",
  contact: {},
  context: { bio_summary: "builder", raw_resume: "resume text" },
}

function installProfileMocks(overrides: {
  candidates?: unknown
  candidate?: unknown
  save?: (init?: RequestInit) => Promise<Response> | Response
} = {}) {
  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    if (url === "/api/candidates") {
      return jsonResponse(overrides.candidates ?? [{ astral_candidate_id: candidateId, state: "ACTIVE", candidate_data: {} }])
    }
    if (url === "/api/shapes/candidates") {
      return jsonResponse(profileSections)
    }
    if (url === `/api/candidates/${candidateId}` && !init) {
      // Top-level name columns (incl. full) — editValuesFromCandidate reads c.full, not contact blob
      return jsonResponse({
        first: "Ada",
        last: "Lovelace",
        full: "Ada Lovelace",
        pronouns: "they/them",
        candidate_data: overrides.candidate ?? candidateData,
      })
    }
    if (url === `/api/candidates/${candidateId}/data` && init?.method === "PUT") {
      return overrides.save
        ? overrides.save(init)
        : jsonResponse({
            first: "Ada",
            last: "Lovelace",
            full: "Ada Lovelace",
            pronouns: "they/them",
            candidate_data: candidateData,
          })
    }
    if (url === "/api/ui_config" || url === "/api/system/ui_config") {
      return jsonResponse({ cover_letter_signature_image: { max_width_px: 200, max_height_px: 80 } })
    }
    if (url === "/api/state_ui_manifest") {
      return Promise.reject(new Error("use default manifest"))
    }
    throw new Error(`unexpected api call: ${url}${init?.method ? ` ${init.method}` : ""}`)
  })
}

describe("CandidateProfile", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    dirtyLeave.mockClear()
  })

  it("saves pronoun preference from contact grid", async () => {
    let savedBody: Record<string, unknown> | null = null
    installProfileMocks({
      save: async (init) => {
        savedBody = JSON.parse(String(init?.body))
        return jsonResponse({ candidate_data: candidateData })
      },
    })
    renderWithProviders(<CandidateProfile />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument())
    const contactField = screen.getByText("Pronoun preference", { selector: "label.dep-field-label" }).closest(".dep-field")!
    const pronoun = within(contactField as HTMLElement).getByRole("combobox")
    expect(pronoun).toHaveDisplayValue("they/them")
    await userEvent.selectOptions(pronoun, "she/her")
    expect(screen.getByRole("button", { name: "Save" })).toHaveClass("btn", "primary")
    expect(screen.getByRole("button", { name: "Cancel" })).toHaveClass("btn", "secondary")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Profile saved")).toBeInTheDocument())
    expect(savedBody?.pronouns).toBe("she/her")
  })

  // AST-1014: middle name removed from profile shapes — AST-510 canceled.
  it.skip("renders middle name and includes it in save payload", async () => {
    let savedBody: Record<string, unknown> | null = null
    installProfileMocks({
      save: async (init) => {
        savedBody = JSON.parse(String(init?.body))
        return jsonResponse({ candidate_data: candidateData })
      },
    })
    renderWithProviders(<CandidateProfile />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument())
    expect(screen.getByDisplayValue("Ann")).toBeInTheDocument()
  })

  it("renders profile fields and saves changes", async () => {
    installProfileMocks()
    renderWithProviders(<CandidateProfile />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument())
    const firstName = screen.getByDisplayValue("Ada")
    await userEvent.clear(firstName)
    await userEvent.type(firstName, "Grace")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Profile saved")).toBeInTheDocument())
  })

  it("restores values on cancel and locks resume text when base resume exists", async () => {
    installProfileMocks({
      candidate: {
        ...candidateData,
        artifacts: { base_resume: [{ label: "Summary", content: "locked" }] },
      },
    })
    renderWithProviders(<CandidateProfile />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Bio Summary" }))
    const bio = screen.getByDisplayValue("builder")
    await userEvent.type(bio, " draft")
    await userEvent.click(screen.getByRole("button", { name: "Cancel" }))
    expect(bio).toHaveValue("builder")
    await userEvent.click(screen.getByRole("button", { name: "Original Resume Text" }))
    expect(screen.getByDisplayValue("resume text")).toBeDisabled()
  })

  it("renders profile page and signature image tab (hooks-safe load path)", async () => {
    installProfileMocks()
    renderWithProviders(<CandidateProfile />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument())
    await waitFor(() => expect(screen.getByRole("button", { name: "Signature Image" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Signature Image" }))
    expect(screen.getByText(/JPEG only, max 200×80 pixels/)).toBeInTheDocument()
  })

  it("shows save errors", async () => {
    installProfileMocks({
      save: () => jsonResponse({ error: "nope" }, { ok: false }),
    })
    renderWithProviders(<CandidateProfile />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument())
    // persistProfile rethrows for dirty-leave; assert via onSave (header Save is void — see Linear).
    await expect(latestDirtyLeave().onSave()).rejects.toBeTruthy()
    await waitFor(() => expect(screen.getAllByText("nope").length).toBeGreaterThan(0))
  })
})

// AST-1082: Profile load/save wires full + websites[]; shape labels; Title Patterns on Profile only
describe("CandidateProfile AST-1082 contact manage", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    dirtyLeave.mockClear()
  })

  it("PUT includes full override and contact.websites list; never profile.*", async () => {
    let savedBody: Record<string, unknown> | null = null
    installProfileMocks({
      candidate: {
        contact: { websites: ["https://a.example"], github: "ada" },
        context: { bio_summary: "builder", raw_resume: "resume text" },
      },
      save: async (init) => {
        savedBody = JSON.parse(String(init?.body))
        return jsonResponse({
          first: "Ada",
          last: "Lovelace",
          full: "Countess of Lovelace",
          pronouns: "they/them",
          candidate_data: {
            contact: { websites: ["https://a.example"], github: "ada" },
            context: { bio_summary: "builder", raw_resume: "resume text" },
          },
        })
      },
    })
    renderWithProviders(<CandidateProfile />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument())
    const fullField = screen.getByText("Full Name", { selector: "label.dep-field-label" }).closest(".dep-field")!
    const fullInput = within(fullField as HTMLElement).getByRole("textbox")
    expect(fullInput).toHaveValue("Ada Lovelace")
    await userEvent.clear(fullInput)
    await userEvent.type(fullInput, "Countess of Lovelace")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Profile saved")).toBeInTheDocument())
    expect(savedBody?.full).toBe("Countess of Lovelace")
    expect(savedBody?.first).toBe("Ada")
    expect(savedBody?.last).toBe("Lovelace")
    expect((savedBody?.contact as Record<string, unknown>)?.websites).toEqual(["https://a.example"])
    expect(savedBody).not.toHaveProperty("profile")
  })

  it("normalizes missing websites to [] and round-trips Add website row on Save", async () => {
    let savedBody: Record<string, unknown> | null = null
    installProfileMocks({
      candidate: {
        contact: { phone: "555" },
        context: { bio_summary: "builder", raw_resume: "resume text" },
      },
      save: async (init) => {
        savedBody = JSON.parse(String(init?.body))
        return jsonResponse({
          first: "Ada",
          last: "Lovelace",
          full: "Ada Lovelace",
          pronouns: "they/them",
          candidate_data: {
            contact: { phone: "555", websites: ["https://new.example"] },
            context: { bio_summary: "builder", raw_resume: "resume text" },
          },
        })
      },
    })
    renderWithProviders(<CandidateProfile />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument())
    // Scope Add to Websites — Profile also has Extra emails string_list (AST-1092)
    const websitesField = screen.getByText("Websites", { selector: "label.dep-field-label" }).closest(".dep-field")!
    const addBtn = within(websitesField as HTMLElement).getByRole("button", { name: "Add" })
    const list = addBtn.closest(".dep-string-list") as HTMLElement
    await userEvent.click(addBtn)
    const siteInput = within(list).getByRole("textbox")
    await userEvent.type(siteInput, "https://new.example")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Profile saved")).toBeInTheDocument())
    expect((savedBody?.contact as Record<string, unknown>)?.websites).toEqual(["https://new.example"])
    expect(savedBody?.full).toBe("Ada Lovelace")
  })

  it("renders username-or-URL labels and keeps Title Patterns on Profile tabs", async () => {
    installProfileMocks()
    renderWithProviders(<CandidateProfile />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument())
    expect(screen.getByText("GitHub (username or URL)", { selector: "label.dep-field-label" })).toBeInTheDocument()
    expect(screen.getByText("LinkedIn (username or URL)", { selector: "label.dep-field-label" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Title Patterns" })).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Title Patterns" }))
    // TabbedTextArea hosts the section (not FormFields labels) — heading + textarea is the edit surface
    expect(screen.getByRole("heading", { name: "Title Patterns" })).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/title patterns/i)).toBeInTheDocument()
  })

  it("cleared full is still present on PUT so core empty-full recompute can run", async () => {
    let savedBody: Record<string, unknown> | null = null
    installProfileMocks({
      save: async (init) => {
        savedBody = JSON.parse(String(init?.body))
        return jsonResponse({
          first: "Ada",
          last: "Lovelace",
          full: "Ada Lovelace",
          pronouns: "they/them",
          candidate_data: candidateData,
        })
      },
    })
    renderWithProviders(<CandidateProfile />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument())
    const fullField = screen.getByText("Full Name", { selector: "label.dep-field-label" }).closest(".dep-field")!
    const fullInput = within(fullField as HTMLElement).getByRole("textbox")
    await userEvent.clear(fullInput)
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Profile saved")).toBeInTheDocument())
    expect(Object.prototype.hasOwnProperty.call(savedBody, "full")).toBe(true)
    expect(savedBody?.full).toBe("")
  })
})

// AST-1092: Resume/Messages labels + extra_emails string_list round-trip (binding list)
describe("CandidateProfile AST-1092 extra binding emails", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    dirtyLeave.mockClear()
  })

  it("renders Resume/Messages labels and Extra emails string_list", async () => {
    installProfileMocks()
    renderWithProviders(<CandidateProfile />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument())
    expect(screen.getByText("Email for Resume", { selector: "label.dep-field-label" })).toBeInTheDocument()
    expect(
      screen.getByText("Email for Messages (if different)", { selector: "label.dep-field-label" }),
    ).toBeInTheDocument()
    expect(screen.getByText("Extra emails (binding)", { selector: "label.dep-field-label" })).toBeInTheDocument()
  })

  it("normalizes missing extra_emails to [] and round-trips Add on Save", async () => {
    let savedBody: Record<string, unknown> | null = null
    installProfileMocks({
      candidate: {
        contact: { contact_email: "ada@ex.com" },
        context: { bio_summary: "builder", raw_resume: "resume text" },
      },
      save: async (init) => {
        savedBody = JSON.parse(String(init?.body))
        return jsonResponse({
          first: "Ada",
          last: "Lovelace",
          full: "Ada Lovelace",
          pronouns: "they/them",
          candidate_data: {
            contact: { contact_email: "ada@ex.com", extra_emails: ["extra@ex.com"] },
            context: { bio_summary: "builder", raw_resume: "resume text" },
          },
        })
      },
    })
    renderWithProviders(<CandidateProfile />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument())
    const extrasField = screen
      .getByText("Extra emails (binding)", { selector: "label.dep-field-label" })
      .closest(".dep-field")!
    const addBtn = within(extrasField as HTMLElement).getByRole("button", { name: "Add" })
    const list = addBtn.closest(".dep-string-list") as HTMLElement
    await userEvent.click(addBtn)
    await userEvent.type(within(list).getByRole("textbox"), "extra@ex.com")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Profile saved")).toBeInTheDocument())
    expect((savedBody?.contact as Record<string, unknown>)?.extra_emails).toEqual(["extra@ex.com"])
    expect(savedBody).not.toHaveProperty("profile")
  })
})

describe("CandidateProfile — AST-1149", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    dirtyLeave.mockClear()
  })

  it("Cover Letter From tab shows shapes help + default-template placeholder (§6c)", async () => {
    let savedBody: Record<string, unknown> | null = null
    installProfileMocks({
      candidate: {
        ...candidateData,
        contact: { cover_letter_from_block: "" },
      },
      save: async (init) => {
        savedBody = JSON.parse(String(init?.body))
        return jsonResponse({
          first: "Ada",
          last: "Lovelace",
          full: "Ada Lovelace",
          pronouns: "they/them",
          candidate_data: {
            ...candidateData,
            contact: { cover_letter_from_block: "{$FULL_NAME} | {$LOCATION}" },
          },
        })
      },
    })
    renderWithProviders(<CandidateProfile />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument(),
    )
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Cover Letter From" })).toBeInTheDocument(),
    )
    await userEvent.click(screen.getByRole("button", { name: "Cover Letter From" }))
    expect(screen.getByText(/Allowed tokens: \{\$FULL_NAME\}/i)).toBeInTheDocument()
    expect(screen.getByText(/cover print shows •/i)).toBeInTheDocument()
    // LabeledTextArea uses an h3 title — textarea has no accessible name.
    const from = screen.getByPlaceholderText(/\{\$FULL_NAME\}/)
    expect(from.getAttribute("placeholder")).toBe(
      "{$FULL_NAME} | {$LOCATION}\n{$CONTACT_EMAIL} | {$PHONE}",
    )
    // userEvent.type treats `{` as a key modifier — set value directly.
    fireEvent.change(from, { target: { value: "{$FULL_NAME} | {$LOCATION}" } })
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Profile saved")).toBeInTheDocument())
    expect((savedBody?.contact as Record<string, unknown>)?.cover_letter_from_block).toBe(
      "{$FULL_NAME} | {$LOCATION}",
    )
  })
})

describe("CandidateProfile — AST-1336 dirty-leave wiring", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    dirtyLeave.mockClear()
  })

  it("wires helper: clean → dirty on edit; Cancel reverts; onSave PUT then clears dirty", async () => {
    let savedBody: Record<string, unknown> | null = null
    installProfileMocks({
      save: async (init) => {
        savedBody = JSON.parse(String(init?.body))
        return jsonResponse({
          first: String(savedBody?.first ?? "Ada"),
          last: "Lovelace",
          full: "Ada Lovelace",
          pronouns: "they/them",
          candidate_data: { ...candidateData, first: savedBody?.first },
        })
      },
    })
    renderWithProviders(<CandidateProfile />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument(),
    )
    await waitFor(() => expect(dirtyLeave).toHaveBeenCalled())
    expect(latestDirtyLeave().isDirty).toBe(false)

    const first = screen.getByDisplayValue("Ada")
    await userEvent.clear(first)
    await userEvent.type(first, "Augusta")
    await waitFor(() => expect(latestDirtyLeave().isDirty).toBe(true))

    // In-page text tab switch is not leave (pathname unchanged); contact draft stays mounted.
    await userEvent.click(screen.getByRole("button", { name: "Bio Summary" }))
    expect(latestDirtyLeave().isDirty).toBe(true)
    expect(screen.getByDisplayValue("Augusta")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Original Resume Text" }))
    expect(latestDirtyLeave().isDirty).toBe(true)
    expect(screen.getByDisplayValue("Augusta")).toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: "Cancel" }))
    await waitFor(() => expect(latestDirtyLeave().isDirty).toBe(false))
    expect(screen.getByDisplayValue("Ada")).toBeInTheDocument()

    const firstAgain = screen.getByDisplayValue("Ada")
    await userEvent.clear(firstAgain)
    await userEvent.type(firstAgain, "Augusta")
    await waitFor(() => expect(latestDirtyLeave().isDirty).toBe(true))
    await latestDirtyLeave().onSave()
    await waitFor(() => expect(savedBody?.first).toBe("Augusta"))
    await waitFor(() => expect(latestDirtyLeave().isDirty).toBe(false))
    await waitFor(() => expect(screen.getByText("Profile saved")).toBeInTheDocument())
  })

  it("onSave failure surfaces error toast and rejects (helper must not proceed)", async () => {
    installProfileMocks({
      save: () => jsonResponse({ error: "leave-save-failed" }, { ok: false }),
    })
    renderWithProviders(<CandidateProfile />)
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument(),
    )
    const first = screen.getByDisplayValue("Ada")
    await userEvent.clear(first)
    await userEvent.type(first, "Augusta")
    await waitFor(() => expect(latestDirtyLeave().isDirty).toBe(true))
    await expect(latestDirtyLeave().onSave()).rejects.toBeTruthy()
    await waitFor(() =>
      expect(screen.getAllByText("leave-save-failed").length).toBeGreaterThan(0),
    )
    expect(latestDirtyLeave().isDirty).toBe(true)
  })
})
