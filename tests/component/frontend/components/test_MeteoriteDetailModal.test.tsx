import { readFileSync } from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"
import MeteoriteDetailModal from "../../../../src/ui/frontend/src/components/MeteoriteDetailModal"
import api from "../../../../src/ui/frontend/src/lib/api"
import { CUT_TITLE, LONG_TITLE, expectFullTitleTooltip } from "../pages/job-title-cell"

const _DIR = path.dirname(fileURLToPath(import.meta.url))

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const SECTIONS = [
  { section_id: "meteorite_timestamps", nav_label: "Timestamps", default_expanded: true },
  { section_id: "meteorite_link", nav_label: "Link", default_expanded: true },
  { section_id: "meteorite_content", nav_label: "Content", default_expanded: true },
  { section_id: "meteorite_provenance", nav_label: "Provenance", default_expanded: false },
  { section_id: "meteorite_job", nav_label: "Linked Job", default_expanded: true },
]

function detail(overrides: Record<string, unknown> = {}) {
  return {
    id: 7,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-02T00:00:00Z",
    state_changed_at: "2026-01-03T00:00:00Z",
    estelle_notified_at: null,
    link: "https://jobs.example/m",
    classify_outcome: "QUALIFIED",
    content: '{"ok":true}',
    state: "LANDED",
    source_kind: "email",
    source_id: "msg-1",
    error: null,
    job_title: "Staff Eng",
    employer_name: "Acme",
    astral_job_id: "job-99",
    ...overrides,
  }
}

function renderModal(id: number | null) {
  return render(
    <MemoryRouter>
      <MeteoriteDetailModal meteoriteId={id} onClose={() => {}} />
    </MemoryRouter>,
  )
}

describe("MeteoriteDetailModal — AST-1749", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  it("returns null when closed", () => {
    const { container } = renderModal(null)
    expect(container.firstChild).toBeNull()
    expect(mockedApi).not.toHaveBeenCalled()
  })

  it("http(s) link is navigable; non-http is plain text", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/meteorites/7") {
        return {
          ok: true,
          status: 200,
          json: async () => ({ sections: SECTIONS, meteorite: detail() }),
        } as Response
      }
      throw new Error(`unexpected ${url}`)
    })
    const { rerender } = renderModal(7)
    await waitFor(() =>
      expect(screen.getByRole("link", { name: "https://jobs.example/m" })).toBeInTheDocument(),
    )

    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/meteorites/8") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            sections: SECTIONS,
            meteorite: detail({ id: 8, link: "inbox:folder/msg", astral_job_id: "" }),
          }),
        } as Response
      }
      throw new Error(`unexpected ${url}`)
    })
    rerender(
      <MemoryRouter>
        <MeteoriteDetailModal meteoriteId={8} onClose={() => {}} />
      </MemoryRouter>,
    )
    await waitFor(() => expect(screen.getByText("inbox:folder/msg")).toBeInTheDocument())
    expect(screen.queryByRole("link", { name: "inbox:folder/msg" })).not.toBeInTheDocument()
  })

  it("job deeplink present when astral_job_id set; absent when blank", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/meteorites/7") {
        return {
          ok: true,
          status: 200,
          json: async () => ({ sections: SECTIONS, meteorite: detail() }),
        } as Response
      }
      throw new Error(`unexpected ${url}`)
    })
    const { rerender } = renderModal(7)
    await waitFor(() =>
      expect(screen.getByRole("link", { name: /Open job job-99/ })).toHaveAttribute(
        "href",
        "/jobs/detail/job-99",
      ),
    )

    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/meteorites/9") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            sections: SECTIONS,
            meteorite: detail({ id: 9, astral_job_id: "   " }),
          }),
        } as Response
      }
      throw new Error(`unexpected ${url}`)
    })
    rerender(
      <MemoryRouter>
        <MeteoriteDetailModal meteoriteId={9} onClose={() => {}} />
      </MemoryRouter>,
    )
    await waitFor(() => expect(screen.getByText("Staff Eng — Acme")).toBeInTheDocument())
    expect(screen.queryByRole("link", { name: /Open job/ })).not.toBeInTheDocument()
  })

  it("404 shows honest error; no Save footer", async () => {
    mockedApi.mockImplementation(async () => {
      return { ok: false, status: 404, json: async () => ({ error: "meteorite not found" }) } as Response
    })
    renderModal(404)
    await waitFor(() => expect(screen.getByText("Meteorite not found")).toBeInTheDocument())
    expect(screen.queryByRole("button", { name: /save/i })).not.toBeInTheDocument()
  })
})

// AST-1983 AC 5: only the job-title part of the header is cut (JobTitleText); the " — <employer>" suffix stays whole.
describe("MeteoriteDetailModal — AST-1983 header title cut", () => {
  const LONG_EMPLOYER = "Employer Name That Runs Well Past Fifty Characters Inc"

  function serve(meteorite: Record<string, unknown>) {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/meteorites/7") {
        return { ok: true, status: 200, json: async () => ({ sections: SECTIONS, meteorite }) } as Response
      }
      throw new Error(`unexpected ${url}`)
    })
  }

  beforeEach(() => {
    mockedApi.mockReset()
  })

  it("title + employer: cut title, whole employer, full-title tooltip on hover", async () => {
    serve(detail({ job_title: LONG_TITLE, employer_name: LONG_EMPLOYER }))
    renderModal(7)
    const heading = await screen.findByRole("heading", { name: `${CUT_TITLE} — ${LONG_EMPLOYER}` })
    expect(heading.textContent).toBe(`${CUT_TITLE} — ${LONG_EMPLOYER}`)
    await expectFullTitleTooltip(within(heading).getByText(CUT_TITLE), heading.closest(".modal-overlay")!)
  })

  it("title only: header is the cut title", async () => {
    serve(detail({ job_title: LONG_TITLE, employer_name: null }))
    renderModal(7)
    expect((await screen.findByRole("heading", { name: CUT_TITLE })).textContent).toBe(CUT_TITLE)
  })

  it("employer only: header is the whole employer, never cut", async () => {
    serve(detail({ job_title: "  ", employer_name: LONG_EMPLOYER }))
    renderModal(7)
    expect((await screen.findByRole("heading", { name: LONG_EMPLOYER })).textContent).toBe(LONG_EMPLOYER)
  })
})


const EDITABLE_FIELDS = [
  "state",
  "content",
  "link",
  "job_title",
  "employer_name",
  "electronic_contact",
]
const STATE_OPTIONS = ["READY", "CHECK_UNIQUE", "BOT_BLOCKED_SCRAPE_METEORITE", "DUPLICATE"]
const DEFAULT_SAVE = "CHECK_UNIQUE"

function editableEnvelope(meteoriteOverrides: Record<string, unknown> = {}) {
  return {
    sections: SECTIONS,
    meteorite: detail({
      state: "READY",
      content: "stored content",
      link: "https://old.example/j",
      job_title: "Old Title",
      employer_name: "Old Co",
      electronic_contact: "old@ex.com",
      astral_job_id: null,
      ...meteoriteOverrides,
    }),
    editable: true,
    editable_fields: EDITABLE_FIELDS,
    state_options: STATE_OPTIONS,
    default_save_state: DEFAULT_SAVE,
  }
}

describe("MeteoriteDetailModal — AST-2224 candidate edit form", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  it("AC1 React half: modal source has no hard-coded LANDED / CHECK_UNIQUE / NEW", () => {
    const src = readFileSync(
      path.resolve(_DIR, "../../../../src/ui/frontend/src/components/MeteoriteDetailModal.tsx"),
      "utf8",
    )
    expect(src).not.toMatch(/LANDED|"CHECK_UNIQUE"|"NEW"/)
  })

  it("editable detail: one control per server field, state select defaults, Save present", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/meteorites/7") {
        return { ok: true, status: 200, json: async () => editableEnvelope() } as Response
      }
      throw new Error(`unexpected ${url}`)
    })
    render(
      <MemoryRouter>
        <MeteoriteDetailModal meteoriteId={7} onClose={() => {}} />
      </MemoryRouter>,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: /^save$/i })).toBeInTheDocument())

    expect(screen.getByRole("textbox", { name: /^content$/i })).toHaveValue("stored content")
    expect(screen.getByRole("textbox", { name: /^link$/i })).toHaveValue("https://old.example/j")
    expect(screen.getByRole("textbox", { name: /^job_title$/i })).toHaveValue("Old Title")
    expect(screen.getByRole("textbox", { name: /^employer_name$/i })).toHaveValue("Old Co")
    expect(screen.getByRole("textbox", { name: /^electronic_contact$/i })).toHaveValue("old@ex.com")

    const stateSelect = screen.getByRole("combobox", { name: /^state$/i })
    expect(stateSelect).toHaveValue(DEFAULT_SAVE)
    for (const opt of STATE_OPTIONS) {
      expect(within(stateSelect).getByRole("option", { name: opt })).toBeInTheDocument()
    }
    // AST-2325 layout: non-content keys in profile-contact-grid, then content full-width
    // (DOM label order ≠ raw editable_fields when content is mid-list on the server).
    const form = document.querySelector(".meteorite-edit-form")
    expect(form).not.toBeNull()
    const labelKeys = Array.from(form!.querySelectorAll("label")).map(lab => {
      const t = lab.firstChild
      return t && t.nodeType === Node.TEXT_NODE ? String(t.textContent) : ""
    })
    const expectedLabelOrder = [
      ...EDITABLE_FIELDS.filter(k => k !== "content"),
      ...EDITABLE_FIELDS.filter(k => k === "content"),
    ]
    expect(labelKeys).toEqual(expectedLabelOrder)
  })

  it("non-editable detail: read-only sections, no Save", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/meteorites/7") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            sections: SECTIONS,
            meteorite: detail({ state: "LANDED" }),
            editable: false,
            editable_fields: EDITABLE_FIELDS,
            state_options: STATE_OPTIONS,
            default_save_state: DEFAULT_SAVE,
          }),
        } as Response
      }
      throw new Error(`unexpected ${url}`)
    })
    renderModal(7)
    await waitFor(() => expect(screen.getByText("Timestamps")).toBeInTheDocument())
    expect(screen.queryByRole("button", { name: /^save$/i })).not.toBeInTheDocument()
    expect(screen.queryByRole("textbox", { name: /^content$/i })).not.toBeInTheDocument()
    expect(document.querySelector(".meteorite-edit-form")).toBeNull()
  })

  it("Save 200: re-applies detail, draft.state from stored row, onSaved once", async () => {
    const user = userEvent.setup()
    const onSaved = vi.fn()
    let getCount = 0
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/meteorites/7" && (!init || !init.method || init.method === "GET")) {
        getCount += 1
        return { ok: true, status: 200, json: async () => editableEnvelope() } as Response
      }
      if (url === "/api/meteorites/7" && init?.method === "PUT") {
        const body = JSON.parse(String(init.body))
        expect(Object.keys(body).sort()).toEqual([...EDITABLE_FIELDS].sort())
        return {
          ok: true,
          status: 200,
          json: async () =>
            editableEnvelope({
              state: "READY",
              content: body.content,
              link: body.link,
              job_title: body.job_title,
              employer_name: body.employer_name,
              electronic_contact: body.electronic_contact,
            }),
        } as Response
      }
      throw new Error(`unexpected ${url} ${init?.method}`)
    })
    render(
      <MemoryRouter>
        <MeteoriteDetailModal meteoriteId={7} onClose={() => {}} onSaved={onSaved} />
      </MemoryRouter>,
    )
    await waitFor(() => expect(screen.getByRole("combobox", { name: /^state$/i })).toHaveValue(DEFAULT_SAVE))

    await user.clear(screen.getByRole("textbox", { name: /^content$/i }))
    await user.type(screen.getByRole("textbox", { name: /^content$/i }), "edited body")
    await user.selectOptions(screen.getByRole("combobox", { name: /^state$/i }), "READY")
    await user.click(screen.getByRole("button", { name: /^save$/i }))

    await waitFor(() => expect(onSaved).toHaveBeenCalledTimes(1))
    // Post-save draft.state comes from stored meteorite.state (READY), not default_save_state.
    await waitFor(() =>
      expect(screen.getByRole("combobox", { name: /^state$/i })).toHaveValue("READY"),
    )
    expect(screen.getByRole("textbox", { name: /^content$/i })).toHaveValue("edited body")
    expect(getCount).toBe(1) // initial GET only; PUT response body refreshes without a second GET
  })

  it("Save 409: shows server error text; onSaved does not fire", async () => {
    const user = userEvent.setup()
    const onSaved = vi.fn()
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/meteorites/7" && (!init || !init.method || init.method === "GET")) {
        return { ok: true, status: 200, json: async () => editableEnvelope() } as Response
      }
      if (url === "/api/meteorites/7" && init?.method === "PUT") {
        return {
          ok: false,
          status: 409,
          json: async () => ({ error: "meteorite is claimed by a running batch" }),
        } as Response
      }
      throw new Error(`unexpected ${url}`)
    })
    render(
      <MemoryRouter>
        <MeteoriteDetailModal meteoriteId={7} onClose={() => {}} onSaved={onSaved} />
      </MemoryRouter>,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: /^save$/i })).toBeInTheDocument())
    await user.click(screen.getByRole("button", { name: /^save$/i }))
    await waitFor(() =>
      expect(screen.getByText("meteorite is claimed by a running batch")).toBeInTheDocument(),
    )
    expect(onSaved).not.toHaveBeenCalled()
  })
})


// [bug-repro] AST-2325: editable form must use profile dep-* chrome (board REVISE).
describe("MeteoriteDetailModal — AST-2325 profile field chrome", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  it("[bug-repro] editable fields use dep-field / dep-input and profile-contact-grid", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/meteorites/7") {
        return { ok: true, status: 200, json: async () => editableEnvelope() } as Response
      }
      throw new Error(`unexpected ${url}`)
    })
    render(
      <MemoryRouter>
        <MeteoriteDetailModal meteoriteId={7} onClose={() => {}} />
      </MemoryRouter>,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: /^save$/i })).toBeInTheDocument())

    const form = document.querySelector(".meteorite-edit-form")
    expect(form).not.toBeNull()
    // Repro: non-content fields share Candidate Profile contact grid + dep-* chrome.
    const grid = form!.querySelector(".profile-contact-grid")
    expect(grid).not.toBeNull()
    expect(form!.querySelectorAll(".job-analysis-upshot-body")).toHaveLength(0)

    for (const key of EDITABLE_FIELDS.filter(k => k !== "content")) {
      const field = grid!.querySelector(`#meteorite-edit-${key}`)?.closest(".dep-field")
      expect(field, `missing dep-field for ${key}`).not.toBeNull()
      const control = field!.querySelector(`#meteorite-edit-${key}`)
      expect(control).not.toBeNull()
      expect(control!.classList.contains("dep-input")).toBe(true)
      if (key === "state") {
        expect(control!.classList.contains("dep-select")).toBe(true)
      }
      const label = field!.querySelector("label.dep-field-label")
      expect(label).not.toBeNull()
      expect(label!.getAttribute("htmlFor") || label!.getAttribute("for")).toBe(`meteorite-edit-${key}`)
    }

    const contentField = form!.querySelector("#meteorite-edit-content")?.closest(".dep-field")
    expect(contentField, "content dep-field").not.toBeNull()
    // content is full-width below the grid, not inside profile-contact-grid
    expect(grid!.contains(contentField)).toBe(false)
    const content = contentField!.querySelector("#meteorite-edit-content")
    expect(content).not.toBeNull()
    expect(content!.classList.contains("dep-input")).toBe(true)
    expect(content!.classList.contains("dep-textarea")).toBe(true)
    expect(content!.classList.contains("entity-story-content")).toBe(false)
  })
})
