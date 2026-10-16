import { readdirSync, readFileSync, statSync } from "node:fs"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"
import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import { useCandidate } from "../../../../src/ui/frontend/src/contexts/CandidateContext"
import ArtifactsBaseResumeContent from "../../../../src/ui/frontend/src/pages/ArtifactsBaseResumeContent"
import { STATE_UI_MANIFEST_FIXTURE } from "../fixtures/stateUiManifestFixture"
import { renderWithProviders } from "../test-utils"
import { resetStytchTestState } from "../stytchMock"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)
const root = resolve(dirname(fileURLToPath(import.meta.url)), "../../../..")

const CATALOG = {
  body_formats: ["free_prose"],
  required_ids: ["professional_summary"],
  contact_ids: [],
  extra_id_pattern: "^[a-z_]+$",
  reserved_extra_ids: [],
  new_extra_default_format: "free_prose",
  page_break_policies: ["normal"],
  page_break_policy_labels: { normal: "Flow" },
  page_break_policy_default: "normal",
  body_format_details: { free_prose: { label: "Prose", description: "Prose", font_family: "serif" } },
  hidden_flow_label: "Hidden",
}

const row = (id: string, title: string, order: number) => ({
  id, title, order, format: "free_prose", enabled: true, job_agent_editable: true,
  required: id === "professional_summary", format_locked: false, page_break_policy: "normal",
})

const SECTIONS: Record<string, ReturnType<typeof row>[]> = {
  c1: [row("professional_summary", "Summary", 0), row("technical_skills", "Skills", 1)],
  c2: [row("professional_summary", "Work History", 0)],
}
const BODIES: Record<string, Record<string, string>> = {
  c1: { professional_summary: "Saved summary", technical_skills: "Saved skills" },
  c2: { professional_summary: "Candidate two body" },
}

const printGets = (cid: string) =>
  mockedApi.mock.calls.filter(([u]) => u === `/candidate/resume/base?candidate_id=${cid}`).length

function CandidateSelectC2() {
  const { setSelectedId } = useCandidate()
  return <button type="button" onClick={() => setSelectedId("c2")}>Select c2</button>
}

/** Full first paint: auth, manifest, candidates, ui_config, structure + entity GETs, base print HTML, candidate PUT. */
function installMocks(candidates: string[] = ["c1"]) {
  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    const json = (body: unknown) => ({ ok: true, status: 200, json: async () => body }) as Response
    if (url === "/api/me") return json({ user_id: "u1", name: "Test", is_admin: true })
    if (url === "/api/state_ui_manifest") return json(STATE_UI_MANIFEST_FIXTURE)
    if (url === "/api/candidates") {
      return json(candidates.map(id => ({ astral_candidate_id: id, state: "ACTIVE_SEARCH", candidate_data: {} })))
    }
    if (url === "/api/ui_config") return json({ column_types: {}, base_resume_accent_palette: ["#112233", "#445566"] })
    const structure = url.match(/^\/api\/candidates\/(c\d)\/resume_structure$/)
    if (structure && !init) return json({ all_sections: SECTIONS[structure[1]], accent_color: "#445566", catalog: CATALOG })
    const entity = url.match(/^\/api\/candidates\/(c\d)$/)
    if (entity && !init) return json({ candidate_data: { artifacts: { base_resume: BODIES[entity[1]] } } })
    if (/^\/api\/candidates\/c\d\/data$/.test(url) && init?.method === "PUT") return json({})
    const print = url.match(/^\/candidate\/resume\/base\?candidate_id=(c\d)$/)
    if (print) return { ok: true, status: 200, text: async () => `<html>base print ${print[1]}</html>` } as Response
    throw new Error(`unexpected api call: ${url} ${init?.method ?? "GET"}`)
  })
}

/** Left / right panel of the split pane (children either side of the separator). */
function panels() {
  const sep = screen.getByRole("separator")
  return { left: sep.previousElementSibling as HTMLElement, right: sep.nextElementSibling as HTMLElement }
}
const previewHtml = (el: HTMLElement) => el.querySelector('iframe[title="Print preview"]')?.getAttribute("srcdoc")

describe("ArtifactsBaseResumeContent — AST-2084 split pane", () => {
  beforeEach(() => {
    localStorage.clear()
    resetStytchTestState()
    mockedApi.mockReset()
    installMocks()
  })

  it("renders the base resume editor left and the live base print preview right (§6c)", async () => {
    renderWithProviders(<ArtifactsBaseResumeContent />)
    await waitFor(() => expect(screen.getByRole("separator")).toBeInTheDocument())
    const { left, right } = panels()
    expect(await within(left).findByLabelText("Search sections")).toBeInTheDocument()
    expect(within(left).getByText("Summary")).toBeInTheDocument()
    expect(within(left).getByText("Skills")).toBeInTheDocument()
    await waitFor(() => expect(previewHtml(right)).toBe("<html>base print c1</html>"))
    // Editor owns the accent swatches now.
    expect(within(left).getByRole("group", { name: "Resume accent color" })).toBeInTheDocument()
  })

  it("preview refetches once per editor save, never while typing", async () => {
    renderWithProviders(<ArtifactsBaseResumeContent />)
    const { left } = await waitFor(() => panels())
    await waitFor(() => expect(printGets("c1")).toBe(1))
    fireEvent.click(await within(left).findByText("Summary"))
    const box = await within(left).findByLabelText("Summary content")
    await userEvent.type(box, " more")
    expect(printGets("c1")).toBe(1)
    fireEvent.focusOut(box)
    await waitFor(() => expect(printGets("c1")).toBe(2))
    const puts = mockedApi.mock.calls.filter(([u, init]) => u === "/api/candidates/c1/data" && init?.method === "PUT")
    expect(puts).toHaveLength(1)
    expect(JSON.parse(String(puts[0][1]?.body)).artifacts.base_resume.professional_summary).toBe("Saved summary more")
  })

  it("shows no Generate / Regenerate / Save / Cancel / Save sections (AC2/AC3)", async () => {
    renderWithProviders(<ArtifactsBaseResumeContent />)
    const { left } = await waitFor(() => panels())
    await within(left).findByLabelText("Search sections")
    for (const name of [/generate/i, /^save/i, /^cancel$/i]) {
      expect(screen.queryByRole("button", { name })).not.toBeInTheDocument()
    }
  })

  it("switching candidates retargets both the editor and the preview", async () => {
    installMocks(["c1", "c2"])
    renderWithProviders(<><CandidateSelectC2 /><ArtifactsBaseResumeContent /></>)
    await waitFor(() => expect(previewHtml(panels().right)).toBe("<html>base print c1</html>"))
    await userEvent.click(screen.getByRole("button", { name: "Select c2" }))
    await waitFor(() => expect(previewHtml(panels().right)).toBe("<html>base print c2</html>"))
    expect(await within(panels().left).findByText("Work History")).toBeInTheDocument()
    expect(within(panels().left).queryByText("Skills")).toBeNull()
  })

  it("no candidate selected → message, no editor or print fetch", async () => {
    installMocks([])
    renderWithProviders(<ArtifactsBaseResumeContent />)
    expect(await screen.findByText("No candidate selected.")).toBeInTheDocument()
    expect(screen.queryByRole("separator")).toBeNull()
    expect(mockedApi.mock.calls.some(([u]) => String(u).startsWith("/candidate/"))).toBe(false)
  })
})

describe("AST-2084 source gates (AC2/AC3/AC5)", () => {
  // Every .ts/.tsx file under the frontend src tree.
  const srcRoot = resolve(root, "src/ui/frontend/src")
  const files = (): string[] => {
    const walk = (d: string): string[] => readdirSync(d).flatMap(n => {
      const p = resolve(d, n)
      return statSync(p).isDirectory() ? walk(p) : /\.tsx?$/.test(n) ? [p] : []
    })
    return walk(srcRoot)
  }
  const read = (rel: string) => readFileSync(resolve(srcRoot, rel), "utf8")

  it("no Save sections and no ArtifactEditor resume-mode identifiers anywhere in frontend src", () => {
    const hits = files().flatMap(f => {
      const text = readFileSync(f, "utf8")
      return [/Save sections/, /useCandidateResumeStructure|structureCatalog|onStructureSave/]
        .filter(re => re.test(text)).map(re => `${f.slice(srcRoot.length)}: ${re}`)
    })
    expect(hits).toEqual([])
  })

  it("base page has no craft_resume_base; both resume surfaces use ResumeContentEditor, not ArtifactEditor", () => {
    const page = read("pages/ArtifactsBaseResumeContent.tsx")
    expect(page).not.toMatch(/craft_resume_base/)
    expect(page).toMatch(/import ResumeContentEditor/)
    expect(page).not.toMatch(/ArtifactEditor/)
    const modal = read("components/JobArtifactEditModal.tsx")
    expect(modal).toMatch(/use_resume_structure\s*\?\s*<ResumeContentEditor/)
  })

  it("AST-1577: ui-consistency directive still has no write-operative link", () => {
    const draft = readFileSync(resolve(root, "canon/directives/active/patt.artifact.ui-consistency.md"), "utf8")
    expect(draft).toMatch(/^id: patt\.artifact\.ui-consistency$/m)
    expect(draft).not.toMatch(/write-operative/)
  })
})
