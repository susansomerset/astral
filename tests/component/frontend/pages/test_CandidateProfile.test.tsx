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
      return jsonResponse({
        first: "Ada",
        last: "Lovelace",
        pronouns: "they/them",
        candidate_data: overrides.candidate ?? candidateData,
      })
    }
    if (url === `/api/candidates/${candidateId}/data` && init?.method === "PUT") {
      return overrides.save ? overrides.save(init) : jsonResponse({ candidate_data: candidateData })
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
