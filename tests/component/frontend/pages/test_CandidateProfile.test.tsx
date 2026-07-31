import { screen, waitFor, within } from "@testing-library/react"
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

const mockedApi = vi.mocked(api)

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
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getAllByText("nope").length).toBeGreaterThan(0))
  })
})

// AST-1082: Profile load/save wires full + websites[]; shape labels; Title Patterns on Profile only
describe("CandidateProfile AST-1082 contact manage", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
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
