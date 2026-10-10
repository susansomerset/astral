import { readFileSync } from "node:fs"
import { resolve } from "node:path"
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))
// ui_config is served by /api/ui_config; the editor only reads the three resume keys below.
vi.mock("../../../../src/ui/frontend/src/lib/uiConfig", () => ({
  getUiConfig: () => ({
    column_types: {},
    base_resume_accent_palette: ["#1F4E79", "#7A1F1F"],
    experience_job_ui_fields: [
      { key: "company", label: "Company" },
      { key: "title", label: "Title" },
      { key: "accomplishments", label: "Accomplishments" },
    ],
    unsupported_resume_structure_message: "FX unsupported, regenerate",
  }),
  loadUiConfig: (cb: () => void) => cb(),
}))
// printHtml itself is covered by test_printHtml (AST-2082); here only the editor's call contract matters.
vi.mock("../../../../src/ui/frontend/src/lib/printHtml", () => ({
  fetchPrintHtml: vi.fn(),
  openHtmlInNewTab: vi.fn(),
}))

import api from "../../../../src/ui/frontend/src/lib/api"
import { fetchPrintHtml, openHtmlInNewTab } from "../../../../src/ui/frontend/src/lib/printHtml"
import ResumeContentEditor from "../../../../src/ui/frontend/src/components/ResumeContentEditor"

const apiMock = vi.mocked(api)

// Fixture catalog: every label/description/font is a test-only string, so any of them on screen proves AC13 (config-driven).
const CATALOG = {
  body_formats: ["free_prose", "bullet_list", "line", "dual_column", "experience_detail"],
  required_ids: ["candidate_name", "professional_summary", "highlights", "experience"],
  contact_ids: ["candidate_name"],
  extra_id_pattern: "^[a-z][a-z0-9_]*$",
  reserved_extra_ids: [],
  new_extra_default_format: "line",
  page_break_policies: ["normal", "avoid_split", "page_break_before"],
  page_break_policy_labels: { normal: "FX Flow", avoid_split: "FX Keep", page_break_before: "FX New Page" },
  page_break_policy_default: "normal",
  body_format_details: {
    free_prose: { label: "FX Prose", description: "FX prose desc", font_family: "FxSerif, serif" },
    bullet_list: { label: "FX Bullets", description: "FX bullets desc", font_family: "FxSans, sans-serif" },
    line: { label: "FX Line", description: "FX line desc", font_family: "FxMono, monospace" },
    dual_column: { label: "FX Columns", description: "FX columns desc", font_family: "FxSans, sans-serif" },
    experience_detail: { label: "FX Experience", description: "FX experience desc", font_family: "FxSerif, serif" },
  },
  hidden_flow_label: "FX Hidden",
}

const row = (id: string, title: string, order: number, format: string | null, extra: Record<string, unknown> = {}) => ({
  id, title, order, format, enabled: true, job_agent_editable: true,
  required: CATALOG.required_ids.includes(id), format_locked: id === "experience" || format === null,
  page_break_policy: "normal", ...extra,
})

const BASE_ROWS = [
  row("candidate_name", "Name", 0, null),
  row("professional_summary", "Summary", 1, "free_prose"),
  row("highlights", "Highlights", 2, "bullet_list"),
  row("experience", "Experience", 3, "experience_detail"),
  row("awards", "Awards", 4, "line"),
  row("technical_skills", "Skills", 5, "dual_column"),
]
const JOBS = [{ company: "Acme", title: "Lead", accomplishments: ["Scaled search"] }]
const BASE_BODY = {
  candidate_name: "Ada Q",
  professional_summary: "Builds data platforms",
  highlights: "Led platform team\nShipped search",
  experience: JOBS,
  awards: "Turing Award",
  technical_skills: "Languages: Python",
}
// Job resume: summary differs from base, Skills/Awards dropped (Skills → SECTION REMOVED), Volunteer is job-only (NEW).
const JOB_ROWS = [
  row("candidate_name", "Name", 0, null),
  row("professional_summary", "Summary", 1, "free_prose"),
  row("highlights", "Highlights", 2, "bullet_list"),
  row("experience", "Experience", 3, "experience_detail"),
  row("volunteer", "Volunteer", 4, "line"),
]
const JOB_BODY = {
  candidate_name: "Ada Q",
  professional_summary: "Tailored summary",
  highlights: "Led platform team\nShipped search",
  experience: JOBS,
  volunteer: "Food bank",
}

type Call = { path: string; method: string; body: unknown }
let calls: Call[]
let routes: Record<string, () => { status?: number; json: unknown }>

const ok = (json: unknown) => () => ({ json })
const respond = (status: number, json: unknown) =>
  ({ ok: status < 400, status, json: async () => json }) as unknown as Response

function setRoutes(over: Record<string, () => { status?: number; json: unknown }> = {}) {
  routes = {
    "GET /api/candidates/c1": ok({ candidate_data: { artifacts: { base_resume: BASE_BODY } } }),
    "GET /api/candidates/c1/resume_structure": ok({ all_sections: BASE_ROWS, accent_color: "#1f4e79", catalog: CATALOG }),
    "PUT /api/candidates/c1/data": ok({ ok: true }),
    "GET /api/jobs/j1": ok({ candidate_id: "c1", job_data: { artifacts: { job_resume: JOB_BODY } } }),
    "GET /api/jobs/j1/resume_structure": ok({ all_sections: JOB_ROWS, accent_color: null, catalog: CATALOG }),
    "PUT /api/jobs/j1/artifacts/job_resume_structure": ok({ ok: true }),
    "PUT /api/jobs/j1/artifacts/job_resume": ok({ ok: true }),
    ...over,
  }
}

const puts = () => calls.filter(c => c.method === "PUT")

beforeEach(() => {
  calls = []
  setRoutes()
  apiMock.mockImplementation(async (path: string, init?: RequestInit) => {
    const method = init?.method ?? "GET"
    calls.push({ path, method, body: init?.body ? JSON.parse(String(init.body)) : undefined })
    const route = routes[`${method} ${path}`]
    if (!route) return respond(404, { error: `no route ${method} ${path}` })
    const r = route()
    return respond(r.status ?? 200, r.json)
  })
  vi.mocked(fetchPrintHtml).mockResolvedValue({ ok: true, html: "<html>printed</html>" })
  vi.mocked(openHtmlInNewTab).mockReturnValue(null)
})

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
  document.head.querySelectorAll("style[data-ast2083]").forEach(s => s.remove())
})

async function renderEditor(kind: "base" | "job" = "base", onSaved = vi.fn()) {
  // Toast reads the route (useLocation), so the editor needs a router.
  const utils = render(
    <MemoryRouter><ResumeContentEditor target={{ kind, id: kind === "base" ? "c1" : "j1" }} onSaved={onSaved} /></MemoryRouter>,
  )
  await screen.findByText("Summary")
  return { ...utils, onSaved }
}

const rowEl = (id: string) => document.querySelector(`[data-section-id="${id}"]`) as HTMLElement
const rowIds = () => [...document.querySelectorAll("[data-section-id]")].map(e => e.getAttribute("data-section-id"))
const expand = (id: string) => fireEvent.click(within(rowEl(id)).getByTitle("Expand"))
const leave = (el: Element) => fireEvent.focusOut(el)

describe("AST-2083 ResumeContentEditor — autosave (AC4/AC5)", () => {
  it("typing sends nothing; field exit sends one base PUT with only the body half, then onSaved once", async () => {
    const { onSaved } = await renderEditor()
    expand("professional_summary")
    const box = screen.getByLabelText("Summary content")
    let text = "Builds data platforms"
    for (const ch of "0123456789") fireEvent.change(box, { target: { value: (text += ch) } })
    // Saves run on the promise chain: let it drain before asserting nothing was sent.
    await act(async () => {})
    expect(puts()).toHaveLength(0)
    expect(onSaved).not.toHaveBeenCalled()
    leave(box)
    await waitFor(() => expect(onSaved).toHaveBeenCalledTimes(1))
    expect(puts()).toHaveLength(1)
    const sent = puts()[0]
    expect(sent.path).toBe("/api/candidates/c1/data")
    const arts = (sent.body as { artifacts: Record<string, unknown> }).artifacts
    expect(Object.keys(arts)).toEqual(["base_resume"])
    expect((arts.base_resume as Record<string, unknown>).professional_summary).toBe(text)
  })

  it("field exit with nothing dirty sends no PUT and no onSaved", async () => {
    const { onSaved } = await renderEditor()
    expand("professional_summary")
    leave(screen.getByLabelText("Summary content"))
    await act(async () => {})
    expect(puts()).toHaveLength(0)
    expect(onSaved).not.toHaveBeenCalled()
  })

  it("renders no Save / Cancel / Save sections button on base or job", async () => {
    for (const kind of ["base", "job"] as const) {
      await renderEditor(kind)
      for (const name of [/^save/i, /^cancel$/i]) expect(screen.queryByRole("button", { name })).toBeNull()
      cleanup()
    }
  })

  it("a failed save toasts the server error, stays dirty, and the next field exit retries", async () => {
    const { onSaved } = await renderEditor()
    setRoutes({ "PUT /api/candidates/c1/data": () => ({ status: 500, json: { error: "FX boom" } }) })
    expand("awards")
    const input = screen.getByLabelText("Awards content")
    fireEvent.change(input, { target: { value: "Nobel" } })
    leave(input)
    expect(await screen.findByText("FX boom")).toBeTruthy()
    expect(onSaved).not.toHaveBeenCalled()
    setRoutes()
    leave(input)
    await waitFor(() => expect(onSaved).toHaveBeenCalledTimes(1))
    expect(puts()).toHaveLength(2)
    expect((puts()[1].body as { artifacts: { base_resume: Record<string, string> } }).artifacts.base_resume.awards).toBe("Nobel")
  })

  it("unmounting with an unsaved edit flushes it", async () => {
    const { unmount } = await renderEditor()
    expand("awards")
    fireEvent.change(screen.getByLabelText("Awards content"), { target: { value: "Fields Medal" } })
    unmount()
    await waitFor(() => expect(puts()).toHaveLength(1))
    expect((puts()[0].body as { artifacts: { base_resume: Record<string, string> } }).artifacts.base_resume.awards).toBe("Fields Medal")
  })

  it("shows a load error when a GET fails", async () => {
    setRoutes({ "GET /api/candidates/c1/resume_structure": () => ({ status: 500, json: {} }) })
    render(<MemoryRouter><ResumeContentEditor target={{ kind: "base", id: "c1" }} /></MemoryRouter>)
    expect(await screen.findByText("Failed to load resume: HTTP 500")).toBeTruthy()
  })
})

describe("AST-2083 ResumeContentEditor — collapsed rows and search (AC6/AC8/AC13)", () => {
  it("collapsed row shows Label: value on one line with catalog tooltip, label, and font", async () => {
    await renderEditor()
    const r = rowEl("highlights")
    expect(within(r).getByText("Highlights")).toBeTruthy()
    const value = r.querySelector(".resume-section-value") as HTMLElement
    expect(value.textContent).toBe("Led platform team Shipped search")
    expect(value.style.fontFamily).toBe("FxSans, sans-serif")
    expect(within(r).getByText("FX Bullets").getAttribute("title")).toBe("FX bullets desc")
    expect(r.querySelector(".resume-section-icon")?.getAttribute("title")).toBe("FX Flow")
    expect(within(r).getByTitle("Move up")).toBeTruthy()
    expect(within(r).getByTitle("Move down")).toBeTruthy()
  })

  it("experience preview flattens jobs; contact row has no format label; first/last arrows disabled", async () => {
    await renderEditor()
    expect(rowEl("experience").querySelector(".resume-section-value")?.textContent).toBe("Acme · Lead • Scaled search")
    const name = rowEl("candidate_name")
    expect(name.querySelector(".resume-section-format")).toBeNull()
    expect((within(name).getByTitle("Move up") as HTMLButtonElement).disabled).toBe(true)
    expect((within(rowEl("technical_skills")).getByTitle("Move down") as HTMLButtonElement).disabled).toBe(true)
  })

  it("delete control only on non-required rows", async () => {
    await renderEditor()
    expect(within(rowEl("professional_summary")).queryByLabelText("Delete section")).toBeNull()
    expect(within(rowEl("awards")).getByLabelText("Delete section")).toBeTruthy()
  })

  it("hidden row shows the catalog Hidden label as its flow tooltip", async () => {
    setRoutes({
      "GET /api/candidates/c1/resume_structure": ok({
        all_sections: BASE_ROWS.map(r => (r.id === "awards" ? { ...r, enabled: false } : r)),
        accent_color: null, catalog: CATALOG,
      }),
    })
    await renderEditor()
    expect(rowEl("awards").querySelector(".resume-section-icon")?.getAttribute("title")).toBe("FX Hidden")
  })

  it("search filters case-insensitively on title and content; clearing restores every row", async () => {
    await renderEditor()
    const search = screen.getByLabelText("Search sections")
    fireEvent.change(search, { target: { value: "PLATFORM" } })
    expect(rowIds()).toEqual(["professional_summary", "highlights"])
    fireEvent.change(search, { target: { value: "skills" } })
    expect(rowIds()).toEqual(["technical_skills"])
    fireEvent.change(search, { target: { value: "acme" } })
    expect(rowIds()).toEqual(["experience"])
    fireEvent.change(search, { target: { value: "" } })
    expect(rowIds()).toEqual(BASE_ROWS.map(r => r.id))
  })
})

describe("AST-2083 ResumeContentEditor — header controls (AC9/AC12/AC13)", () => {
  it("format select lists catalog labels (incl. line); experience format is locked", async () => {
    await renderEditor()
    expand("awards")
    const fmt = within(rowEl("awards")).getByLabelText("Format") as HTMLSelectElement
    expect([...fmt.options].map(o => o.text)).toEqual(["FX Prose", "FX Bullets", "FX Line", "FX Columns", "FX Experience"])
    expect(fmt.value).toBe("line")
    expand("experience")
    expect((within(rowEl("experience")).getByLabelText("Format") as HTMLSelectElement).disabled).toBe(true)
  })

  it("line format edits in a single-line input; prose edits in a textarea", async () => {
    await renderEditor()
    expand("awards")
    expand("professional_summary")
    expect(screen.getByLabelText("Awards content").tagName).toBe("INPUT")
    expect(screen.getByLabelText("Summary content").tagName).toBe("TEXTAREA")
  })

  it("format change saves the structure immediately", async () => {
    await renderEditor()
    expand("awards")
    fireEvent.change(within(rowEl("awards")).getByLabelText("Format"), { target: { value: "free_prose" } })
    await waitFor(() => expect(puts()).toHaveLength(1))
    const arts = (puts()[0].body as { artifacts: { resume_structure: { sections: Record<string, { format: string }> } } }).artifacts
    expect(Object.keys(arts)).toEqual(["resume_structure"])
    expect(arts.resume_structure.sections.awards.format).toBe("free_prose")
  })

  it("flow select: Hidden sets enabled=false, a policy re-enables with that policy; required rows have no Hidden", async () => {
    await renderEditor()
    expand("awards")
    const flow = within(rowEl("awards")).getByLabelText("Flow") as HTMLSelectElement
    expect([...flow.options].map(o => o.text)).toEqual(["FX Hidden", "FX Flow", "FX Keep", "FX New Page"])
    fireEvent.change(flow, { target: { value: "__hidden__" } })
    await waitFor(() => expect(puts()).toHaveLength(1))
    const sec = (n: number) => (puts()[n].body as { artifacts: { resume_structure: { sections: Record<string, { enabled: boolean; page_break_policy: string }> } } })
      .artifacts.resume_structure.sections.awards
    expect(sec(0).enabled).toBe(false)
    fireEvent.change(flow, { target: { value: "page_break_before" } })
    await waitFor(() => expect(puts()).toHaveLength(2))
    expect(sec(1)).toMatchObject({ enabled: true, page_break_policy: "page_break_before" })
    expand("professional_summary")
    const reqFlow = within(rowEl("professional_summary")).getByLabelText("Flow") as HTMLSelectElement
    expect([...reqFlow.options].map(o => o.text)).not.toContain("FX Hidden")
  })

  it("Job Edit checkbox shows on base only and saves immediately", async () => {
    await renderEditor()
    expand("awards")
    fireEvent.click(within(rowEl("awards")).getByLabelText("Job Edit"))
    await waitFor(() => expect(puts()).toHaveLength(1))
    expect((puts()[0].body as { artifacts: { resume_structure: { sections: Record<string, { job_agent_editable: boolean }> } } })
      .artifacts.resume_structure.sections.awards.job_agent_editable).toBe(false)
    cleanup()
    await renderEditor("job")
    expand("volunteer")
    expect(within(rowEl("volunteer")).queryByLabelText("Job Edit")).toBeNull()
  })

  it("label typing saves on field exit, not per keystroke", async () => {
    await renderEditor()
    expand("awards")
    const label = within(rowEl("awards")).getByLabelText("Section label")
    fireEvent.change(label, { target: { value: "Honors" } })
    await act(async () => {})
    expect(puts()).toHaveLength(0)
    leave(label)
    await waitFor(() => expect(puts()).toHaveLength(1))
    expect((puts()[0].body as { artifacts: { resume_structure: { sections: Record<string, { title: string }> } } })
      .artifacts.resume_structure.sections.awards.title).toBe("Honors")
  })

  it("accent swatch saves the uppercased color and marks itself pressed", async () => {
    await renderEditor()
    const group = screen.getByRole("group", { name: "Resume accent color" })
    expect(within(group).getByLabelText("#1F4E79").getAttribute("aria-pressed")).toBe("true")
    fireEvent.click(within(group).getByLabelText("#7A1F1F"))
    await waitFor(() => expect(puts()).toHaveLength(1))
    expect((puts()[0].body as { artifacts: { resume_structure: { accent_color: string } } }).artifacts.resume_structure.accent_color).toBe("#7A1F1F")
    expect(within(group).getByLabelText("#7A1F1F").getAttribute("aria-pressed")).toBe("true")
  })
})

describe("AST-2083 ResumeContentEditor — add, delete, reorder (AC7/AC10/AC11)", () => {
  it("Add Section appends an expanded row in the default format, locked until labeled and saved", async () => {
    await renderEditor()
    fireEvent.change(screen.getByLabelText("Search sections"), { target: { value: "zzz" } })
    fireEvent.click(screen.getByRole("button", { name: "Add Section" }))
    expect((screen.getByLabelText("Search sections") as HTMLInputElement).value).toBe("")
    const ids = rowIds()
    expect(ids).toHaveLength(BASE_ROWS.length + 1)
    const added = document.querySelector(`[data-section-id="${ids.at(-1)}"]`) as HTMLElement
    expect(added.classList.contains("is-expanded")).toBe(true)
    expect((within(added).getByLabelText("Format") as HTMLSelectElement).value).toBe("line")
    expect((added.querySelector(".resume-section-body input") as HTMLInputElement).disabled).toBe(true)
    expect(puts()).toHaveLength(0)
  })

  it("an unlabeled new row is never sent; once labeled it saves last and adopts the server's slug id", async () => {
    await renderEditor()
    fireEvent.click(screen.getByRole("button", { name: "Add Section" }))
    const added = () => document.querySelector(`[data-section-id="${rowIds().at(-1)}"]`) as HTMLElement
    const label = within(added()).getByLabelText("Section label")
    // A header change elsewhere saves while the new row is still blank: the blank row is withheld.
    expand("awards")
    fireEvent.change(within(rowEl("awards")).getByLabelText("Flow"), { target: { value: "avoid_split" } })
    await waitFor(() => expect(puts()).toHaveLength(1))
    const sent0 = (puts()[0].body as { artifacts: { resume_structure: { sections: Record<string, unknown> } } }).artifacts.resume_structure.sections
    expect(Object.keys(sent0)).toEqual(BASE_ROWS.map(r => r.id))
    // Server slugs the title; the follow-up structure GET reveals the new id.
    setRoutes({
      "GET /api/candidates/c1/resume_structure": ok({
        all_sections: [...BASE_ROWS, row("volunteering", "Volunteering", 6, "line", { required: false, format_locked: false })],
        accent_color: "#1F4E79", catalog: CATALOG,
      }),
    })
    fireEvent.change(label, { target: { value: "Volunteering" } })
    leave(label)
    await waitFor(() => expect(rowIds().at(-1)).toBe("volunteering"))
    const sections = (puts()[1].body as { artifacts: { resume_structure: { sections: Record<string, { title: string; order: number }> } } })
      .artifacts.resume_structure.sections
    const last = Object.values(sections).at(-1)!
    expect(last).toMatchObject({ title: "Volunteering", order: BASE_ROWS.length })
    // Adopted row unlocks and stays expanded.
    expect((within(rowEl("volunteering")).getByLabelText("Volunteering content") as HTMLInputElement).disabled).toBe(false)
  })

  it("delete asks first: cancel keeps the row and sends nothing", async () => {
    const ask = vi.spyOn(window, "confirm").mockReturnValue(false)
    await renderEditor()
    fireEvent.click(within(rowEl("awards")).getByLabelText("Delete section"))
    await act(async () => {})
    expect(ask).toHaveBeenCalledWith('Delete the "Awards" section?')
    expect(rowEl("awards")).toBeTruthy()
    expect(puts()).toHaveLength(0)
  })

  it("delete confirm removes the row from structure and body in one save", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true)
    await renderEditor()
    fireEvent.click(within(rowEl("awards")).getByLabelText("Delete section"))
    await waitFor(() => expect(puts()).toHaveLength(1))
    expect(rowEl("awards")).toBeNull()
    const arts = (puts()[0].body as { artifacts: { resume_structure: { sections: Record<string, unknown> }; base_resume: Record<string, unknown> } }).artifacts
    expect(arts.resume_structure.sections).not.toHaveProperty("awards")
    expect(arts.base_resume).not.toHaveProperty("awards")
  })

  it("arrow move saves the new order", async () => {
    await renderEditor()
    fireEvent.click(within(rowEl("awards")).getByTitle("Move up"))
    await waitFor(() => expect(puts()).toHaveLength(1))
    const order = ["candidate_name", "professional_summary", "highlights", "awards", "experience", "technical_skills"]
    expect(rowIds()).toEqual(order)
    const sections = (puts()[0].body as { artifacts: { resume_structure: { sections: Record<string, { order: number }> } } }).artifacts.resume_structure.sections
    expect(Object.entries(sections).map(([k, v]) => [k, v.order])).toEqual(order.map((k, i) => [k, i]))
  })

  it("drag handle onto another row moves it there and saves", async () => {
    await renderEditor()
    const handle = rowEl("technical_skills").querySelector(".resume-section-drag") as HTMLElement
    const setData = vi.fn()
    fireEvent.dragStart(handle, { dataTransfer: { setData } })
    expect(setData).toHaveBeenCalledWith("text/plain", "technical_skills")
    fireEvent.drop(rowEl("professional_summary"))
    await waitFor(() => expect(puts()).toHaveLength(1))
    expect(rowIds()).toEqual(["candidate_name", "technical_skills", "professional_summary", "highlights", "experience", "awards"])
  })
})

describe("AST-2083 ResumeContentEditor — experience body", () => {
  it("experience row expands into the jobs editor", async () => {
    await renderEditor()
    expand("experience")
    expect(rowEl("experience").querySelector(".experience-jobs-editor-role-label")?.textContent).toContain("Acme")
  })

  it("unparseable experience shows the config notice, refuses body saves, but still saves structure", async () => {
    setRoutes({
      "GET /api/candidates/c1": ok({ candidate_data: { artifacts: { base_resume: { ...BASE_BODY, experience: "legacy blob" } } } }),
    })
    await renderEditor()
    expand("experience")
    expect(within(rowEl("experience")).getByText("FX unsupported, regenerate")).toBeTruthy()
    expand("awards")
    const input = screen.getByLabelText("Awards content")
    fireEvent.change(input, { target: { value: "Nobel" } })
    leave(input)
    // Inline notice plus the save-refused toast.
    await waitFor(() => expect(screen.getAllByText("FX unsupported, regenerate")).toHaveLength(2))
    expect(puts()).toHaveLength(0)
    fireEvent.click(within(rowEl("awards")).getByTitle("Move up"))
    await waitFor(() => expect(puts()).toHaveLength(1))
    expect(Object.keys((puts()[0].body as { artifacts: Record<string, unknown> }).artifacts)).toEqual(["resume_structure"])
  })
})

describe("AST-2114 ResumeContentEditor — search filters Experience jobs", () => {
  const ACME = { company: "Acme", title: "Lead", accomplishments: ["Scaled search"] }
  const GLOBEX = { company: "Globex", title: "Engineer", accomplishments: ["Built billing"] }
  const twoJobs = () =>
    setRoutes({ "GET /api/candidates/c1": ok({ candidate_data: { artifacts: { base_resume: { ...BASE_BODY, experience: [ACME, GLOBEX] } } } }) })
  const jobLabels = () => [...rowEl("experience").querySelectorAll(".experience-jobs-editor-role-label")].map(e => e.textContent)
  const addRole = () => within(rowEl("experience")).queryByRole("button", { name: "Add role" })

  it("[bug-repro] a job-text match shows only matching jobs; title match or empty query shows all", async () => {
    twoJobs()
    await renderEditor()
    expand("experience")
    expect(jobLabels()).toEqual(["Acme, Lead", "Globex, Engineer"])
    const search = screen.getByLabelText("Search sections")
    fireEvent.change(search, { target: { value: "acme" } })
    expect(rowIds()).toEqual(["experience"])
    expect(jobLabels()).toEqual(["Acme, Lead"])
    // Decision 1: a blank new role would match nothing, so Add role hides while filtering.
    expect(addRole()).toBeNull()
    // Accomplishment text counts (same haystack as the section match).
    fireEvent.change(search, { target: { value: "BILLING" } })
    expect(jobLabels()).toEqual(["Globex, Engineer"])
    // Decision 2: a section-title hit shows the whole section.
    fireEvent.change(search, { target: { value: "exper" } })
    expect(jobLabels()).toEqual(["Acme, Lead", "Globex, Engineer"])
    expect(addRole()).not.toBeNull()
    fireEvent.change(search, { target: { value: "" } })
    expect(jobLabels()).toEqual(["Acme, Lead", "Globex, Engineer"])
    expect(puts()).toHaveLength(0)
  })

  it("editing a filtered job saves the full array, hidden jobs included; filtering alone sends nothing", async () => {
    twoJobs()
    const { onSaved } = await renderEditor()
    expand("experience")
    fireEvent.change(screen.getByLabelText("Search sections"), { target: { value: "globex" } })
    await act(async () => {})
    expect(puts()).toHaveLength(0)
    expect(onSaved).not.toHaveBeenCalled()
    fireEvent.click(within(rowEl("experience")).getByText("Globex, Engineer"))
    const title = within(rowEl("experience")).getByDisplayValue("Engineer")
    fireEvent.change(title, { target: { value: "Staff" } })
    leave(title)
    await waitFor(() => expect(onSaved).toHaveBeenCalledTimes(1))
    const arts = (puts()[0].body as { artifacts: { base_resume: Record<string, unknown> } }).artifacts
    expect(arts.base_resume.experience).toEqual([ACME, { ...GLOBEX, title: "Staff" }])
  })
})

describe("AST-2083 ResumeContentEditor — job target and Compare to Base (AC14)", () => {
  it("job body edit sends only the job_resume PUT", async () => {
    const { onSaved } = await renderEditor("job")
    expand("volunteer")
    const input = screen.getByLabelText("Volunteer content")
    fireEvent.change(input, { target: { value: "Shelter" } })
    leave(input)
    await waitFor(() => expect(onSaved).toHaveBeenCalledTimes(1))
    expect(puts().map(p => p.path)).toEqual(["/api/jobs/j1/artifacts/job_resume"])
    expect((puts()[0].body as { job_resume: Record<string, unknown> }).job_resume.volunteer).toBe("Shelter")
  })

  it("job structure change sends only the job_resume_structure PUT", async () => {
    await renderEditor("job")
    fireEvent.click(within(rowEl("volunteer")).getByTitle("Move up"))
    await waitFor(() => expect(puts()).toHaveLength(1))
    const sent = puts()[0]
    expect(sent.path).toBe("/api/jobs/j1/artifacts/job_resume_structure")
    expect(Object.keys((sent.body as { job_resume_structure: { sections: object } }).job_resume_structure.sections))
      .toEqual(["candidate_name", "professional_summary", "highlights", "volunteer", "experience"])
  })

  it("Compare to Base is job-only", async () => {
    await renderEditor()
    expect(screen.queryByRole("button", { name: "Compare to Base" })).toBeNull()
  })

  it("compare marks one differs, one NEW SECTION, one SECTION REMOVED; toggling off clears them", async () => {
    await renderEditor("job")
    const toggle = screen.getByRole("button", { name: "Compare to Base" })
    fireEvent.click(toggle)
    const removed = await screen.findByText(/^SECTION REMOVED: Skills: Languages: Python$/)
    expect(toggle.getAttribute("aria-pressed")).toBe("true")
    expect(rowEl("professional_summary").querySelector(".resume-section-compare")?.textContent).toBe("Builds data platforms")
    expect(rowEl("highlights").querySelector(".resume-section-compare")).toBeNull()
    expect(rowEl("experience").querySelector(".resume-section-compare")).toBeNull()
    expect(rowEl("volunteer").querySelector(".resume-section-new")?.textContent).toBe("NEW SECTION: Not found in base")
    // Awards is also base-only; it anchors after experience with Skills (base order), both before Volunteer.
    const removedTexts = [...document.querySelectorAll(".resume-section-removed-text")].map(e => e.textContent)
    expect(removedTexts).toEqual(["SECTION REMOVED: Awards: Turing Award", "SECTION REMOVED: Skills: Languages: Python"])
    const order = [...document.querySelectorAll("[data-section-id], .resume-section-removed")]
      .map(e => e.getAttribute("data-section-id") ?? "removed")
    expect(order).toEqual(["candidate_name", "professional_summary", "highlights", "experience", "removed", "removed", "volunteer"])
    expect(removed).toBeTruthy()
    fireEvent.click(toggle)
    expect(document.querySelector(".resume-section-removed, .resume-section-compare")).toBeNull()
  })

  it("compare refetches the candidate base each time it turns on", async () => {
    await renderEditor("job")
    const toggle = screen.getByRole("button", { name: "Compare to Base" })
    const baseGets = () => calls.filter(c => c.method === "GET" && c.path === "/api/candidates/c1").length
    fireEvent.click(toggle)
    await screen.findByText(/SECTION REMOVED: Skills/)
    fireEvent.click(toggle)
    fireEvent.click(toggle)
    await screen.findByText(/SECTION REMOVED: Skills/)
    expect(baseGets()).toBe(2)
  })

  it("Add on a removed section inserts it after its anchor with base content: structure PUT then job_resume PUT", async () => {
    await renderEditor("job")
    fireEvent.click(screen.getByRole("button", { name: "Compare to Base" }))
    const removed = (await screen.findByText(/SECTION REMOVED: Skills/)).closest(".resume-section-removed") as HTMLElement
    fireEvent.click(within(removed).getByRole("button", { name: "Add" }))
    await waitFor(() => expect(puts()).toHaveLength(2))
    expect(puts().map(p => p.path)).toEqual(["/api/jobs/j1/artifacts/job_resume_structure", "/api/jobs/j1/artifacts/job_resume"])
    expect(Object.keys((puts()[0].body as { job_resume_structure: { sections: object } }).job_resume_structure.sections))
      .toEqual(["candidate_name", "professional_summary", "highlights", "experience", "technical_skills", "volunteer"])
    expect((puts()[1].body as { job_resume: Record<string, unknown> }).job_resume.technical_skills).toBe("Languages: Python")
    expect(screen.queryByText(/SECTION REMOVED: Skills/)).toBeNull()
    expect(rowEl("technical_skills").querySelector(".resume-section-compare")).toBeNull()
  })

  it("compare fetch failure toasts", async () => {
    await renderEditor("job")
    setRoutes({ "GET /api/candidates/c1": () => ({ status: 500, json: {} }) })
    fireEvent.click(screen.getByRole("button", { name: "Compare to Base" }))
    expect(await screen.findByText("Compare failed: HTTP 500")).toBeTruthy()
  })
})

describe("AST-2083 ResumeContentEditor — Print (AC15)", () => {
  it("base Print flushes pending edits first, then opens the base print HTML", async () => {
    await renderEditor()
    expand("awards")
    fireEvent.change(screen.getByLabelText("Awards content"), { target: { value: "Nobel" } })
    vi.mocked(fetchPrintHtml).mockImplementation(async () => {
      expect(puts()).toHaveLength(1)
      return { ok: true, html: "<html>printed</html>" }
    })
    fireEvent.click(screen.getByRole("button", { name: "Print" }))
    await waitFor(() => expect(openHtmlInNewTab).toHaveBeenCalledWith("<html>printed</html>"))
    expect(fetchPrintHtml).toHaveBeenCalledWith({ kind: "base", id: "c1" })
  })

  it("job Print targets job_resume; a fetch error or blocked popup toasts", async () => {
    await renderEditor("job")
    vi.mocked(fetchPrintHtml).mockResolvedValueOnce({ ok: false, error: "FX no resume" })
    fireEvent.click(screen.getByRole("button", { name: "Print" }))
    expect(await screen.findByText("FX no resume")).toBeTruthy()
    expect(fetchPrintHtml).toHaveBeenCalledWith({ kind: "job_resume", id: "j1" })
    vi.mocked(openHtmlInNewTab).mockReturnValueOnce("FX popup blocked")
    fireEvent.click(screen.getByRole("button", { name: "Print" }))
    expect(await screen.findByText("FX popup blocked")).toBeTruthy()
  })
})

describe("AST-2083 experience job header color (AC16)", () => {
  // jsdom does not load App.css: inject the two product rules so computed color tracks App.css.
  const css = readFileSync(resolve(__dirname, "../../../../src/ui/frontend/src/App.css"), "utf8")
  const ruleFor = (selector: string) => {
    const m = css.match(new RegExp(`(^|\\n)${selector.replace(/[.-]/g, c => `\\${c}`)}\\s*\\{[^}]*\\}`))
    expect(m, `App.css must define ${selector}`).toBeTruthy()
    return m![0]
  }

  it("role label rule sets no color of its own; section title rule does", () => {
    expect(ruleFor(".experience-jobs-editor-role-label")).not.toMatch(/\bcolor\s*:/)
    expect(ruleFor(".resume-section-title")).toMatch(/\bcolor\s*:\s*var\(--heading\)/)
  })

  it("job header and section header compute the same color", async () => {
    const style = document.createElement("style")
    style.setAttribute("data-ast2083", "")
    style.textContent = `${ruleFor(".resume-section-title")}\n${ruleFor(".experience-jobs-editor-role-label")}`
      .replace(/var\(--heading\)/g, "rgb(1, 2, 3)")
    document.head.appendChild(style)
    await renderEditor()
    expand("experience")
    const job = rowEl("experience").querySelector(".experience-jobs-editor-role-label") as HTMLElement
    const section = rowEl("highlights").querySelector(".resume-section-title") as HTMLElement
    expect(getComputedStyle(section).color).toBe("rgb(1, 2, 3)")
    expect(getComputedStyle(job).color).toBe(getComputedStyle(section).color)
  })
})
