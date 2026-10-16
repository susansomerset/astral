import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { useLocation } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { useCandidate } from "../../../../src/ui/frontend/src/contexts/CandidateContext"
import api from "../../../../src/ui/frontend/src/lib/api"
import SearchResults from "../../../../src/ui/frontend/src/pages/SearchResults"
import { STATE_UI_MANIFEST_FIXTURE } from "../fixtures/stateUiManifestFixture"
import { renderWithProviders } from "../test-utils"
import { jsonResponse } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

// The four modals have their own suites; here a stand-in reports which one opened, for which id, and can close.
function modalProbe(name: string, idProp: string) {
  return {
    default: (props: Record<string, unknown> & { onClose: () => void }) =>
      props[idProp] == null ? null : (
        <div data-testid="open-modal">
          {name}:{String(props[idProp])}:{typeof props[idProp]}
          <button type="button" onClick={props.onClose}>Close modal</button>
        </div>
      ),
  }
}
vi.mock("../../../../src/ui/frontend/src/components/JobAnalysisReportModal", () => modalProbe("JobAnalysisReportModal", "jobId"))
vi.mock("../../../../src/ui/frontend/src/components/JobDetailModal", () => modalProbe("JobDetailModal", "jobId"))
vi.mock("../../../../src/ui/frontend/src/components/CompanyDetailModal", () => modalProbe("CompanyDetailModal", "shortName"))
vi.mock("../../../../src/ui/frontend/src/components/MeteoriteDetailModal", () => modalProbe("MeteoriteDetailModal", "meteoriteId"))

const mockedApi = vi.mocked(api)

type Hit = Record<string, unknown>
const job = (id: string, name: string, kind: "report" | "detail", extra: Hit = {}): Hit => ({
  entity_id: id, display_name: name, state: "NEW", tier: "base", matched_fields: ["job_title"],
  jobs_list: kind === "report" ? "ready" : "processing", modal_kind: kind, ...extra,
})
const company = (id: string, state = "IMPORTED"): Hit => ({
  entity_id: id, display_name: `${id} Inc`, state, tier: "base", matched_fields: ["short_name"],
})
const meteorite = (id: number): Hit => ({
  entity_id: id, display_name: `Met ${id}`, state: null, tier: "payload", matched_fields: ["content", "error"],
})
const empty = { job: [], company: [], meteorite: [] }

const CANDIDATES = [
  { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} },
  { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: {} },
]

/** First-paint mocks (auth, candidates, state manifest, ui_config) + a per-test /api/search handler. */
function mockApis(search: (q: string, cid: string) => Promise<Response> | Response, candidates = CANDIDATES) {
  mockedApi.mockImplementation(async (url: string) => {
    if (url === "/api/me") return jsonResponse({ user_id: "u1", name: "Admin", is_admin: true })
    if (url === "/api/candidates") return jsonResponse(candidates)
    if (url === "/api/state_ui_manifest") return jsonResponse(STATE_UI_MANIFEST_FIXTURE)
    if (url === "/api/ui_config" || url === "/api/system/ui_config") return jsonResponse({ column_types: {} })
    if (url.startsWith("/api/search?")) {
      const p = new URLSearchParams(url.slice("/api/search?".length))
      return search(p.get("q") ?? "", p.get("candidate_id") ?? "")
    }
    throw new Error(`Unhandled api ${url}`)
  })
}

const searchCalls = () => mockedApi.mock.calls.map(c => String(c[0])).filter(u => u.startsWith("/api/search"))

function LocationProbe() {
  const loc = useLocation()
  return <div data-testid="location">{loc.pathname + loc.search}</div>
}

function SelectC2() {
  const { setSelectedId } = useCandidate()
  return <button type="button" onClick={() => setSelectedId("c2")}>Select c2</button>
}

function renderPage(url = "/search?q=acme") {
  return renderWithProviders(
    <>
      <SearchResults />
      <LocationProbe />
      <SelectC2 />
    </>,
    { router: { initialEntries: [url] } },
  )
}

const sectionTitles = () => screen.queryAllByRole("heading", { level: 2 }).map(h => h.textContent)
function rowsOf(title: string) {
  const section = screen.getByRole("heading", { level: 2, name: title }).closest("section")!
  return within(section).getAllByRole("row").slice(1)
}

describe("SearchResults — AST-2173 / AST-2174", () => {
  beforeEach(() => {
    localStorage.clear()
    localStorage.setItem("astral_selected_candidate", "c1")
    mockedApi.mockReset()
  })

  // AC 11 (UI half): only non-empty types, Jobs → Companies → Meteorites, "<Label> (<n>)"; API row order kept.
  it("renders Jobs (2) then Meteorites (1), no Companies heading, rows in API order", async () => {
    mockApis(() => jsonResponse({
      job: [job("j-b", "Zeta role", "report"), job("j-a", "Alpha role", "detail", { tier: "payload", matched_fields: ["job_data"] })],
      company: [],
      meteorite: [meteorite(7)],
    }))
    renderPage()
    await waitFor(() => expect(sectionTitles()).toEqual(["Jobs (2)", "Meteorites (1)"]))
    expect(screen.queryByText(/Companies/)).toBeNull()
    // Not re-sorted client side: base "Zeta" stays ahead of payload "Alpha".
    expect(rowsOf("Jobs (2)").map(r => within(r).getAllByRole("cell")[0].textContent)).toEqual(["Zeta role", "Alpha role"])
    const [met] = rowsOf("Meteorites (1)")
    expect(within(met).getAllByRole("cell").map(c => c.textContent)).toEqual(["Met 7", "—", "content, error"])
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Search results for “acme”")
  })

  it("all three lists empty → 'No results' and no section headings", async () => {
    mockApis(() => jsonResponse(empty))
    renderPage()
    await waitFor(() => expect(screen.getByText("No results")).toBeInTheDocument())
    expect(sectionTitles()).toEqual([])
  })

  it("failed request reads as 'No results'", async () => {
    mockApis(() => jsonResponse({ error: "boom" }, { ok: false, status: 500 }))
    renderPage()
    await waitFor(() => expect(screen.getByText("No results")).toBeInTheDocument())
    expect(sectionTitles()).toEqual([])
  })

  // AC 10: reload of the URL = same request (q from the URL, encoded) for the selected candidate.
  it("requests /api/search with the URL's q and the selected candidate, encoded", async () => {
    mockApis(() => jsonResponse(empty))
    renderPage("/search?q=R%26D%20lead")
    await waitFor(() => expect(searchCalls().length).toBeGreaterThan(0))
    expect(searchCalls()).toContain("/api/search?q=R%26D%20lead&candidate_id=c1")
  })

  // AC 10: blank q → no request with blank q.
  it.each(["/search", "/search?q=", "/search?q=%20%20"])("blank q (%s) → no request, 'No results'", async url => {
    mockApis(() => jsonResponse(empty))
    renderPage(url)
    await waitFor(() => expect(screen.getByText("No results")).toBeInTheDocument())
    await waitFor(() => expect(mockedApi.mock.calls.some(c => c[0] === "/api/candidates")).toBe(true))
    expect(searchCalls()).toEqual([])
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(/^Search results$/)
  })

  // AC 12: no candidate → "Select a candidate", no request.
  it("no candidate selected → 'Select a candidate' and no /api/search request", async () => {
    localStorage.clear()
    mockApis(() => jsonResponse(empty), [])
    renderPage()
    await waitFor(() => expect(mockedApi.mock.calls.some(c => c[0] === "/api/candidates")).toBe(true))
    expect(screen.getByText("Select a candidate")).toBeInTheDocument()
    expect(searchCalls()).toEqual([])
  })

  // AC 12: switch A → B re-fetches; A's rows never shown for B, even while B is in flight.
  it("candidate switch re-fetches and never shows the previous candidate's rows", async () => {
    let releaseB: (r: Response) => void = () => {}
    mockApis((_q, cid) =>
      cid === "c1"
        ? jsonResponse({ ...empty, company: [company("a-only")] })
        : new Promise<Response>(res => { releaseB = res }),
    )
    renderPage()
    await waitFor(() => expect(screen.getByText("a-only Inc")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Select c2" }))
    await waitFor(() => expect(searchCalls()).toContain("/api/search?q=acme&candidate_id=c2"))
    expect(screen.queryByText("a-only Inc")).toBeNull()
    expect(screen.getByText("Loading...")).toBeInTheDocument()
    releaseB(jsonResponse({ ...empty, company: [company("b-only")] }))
    await waitFor(() => expect(screen.getByText("b-only Inc")).toBeInTheDocument())
    expect(screen.queryByText("a-only Inc")).toBeNull()
  })

  // AC 8 (UI half) + AC 9: right modal, right id, no navigation away.
  it.each([
    ["Report job", "JobAnalysisReportModal:j-rep:string"],
    ["Detail job", "JobDetailModal:j-det:string"],
    ["acme Inc", "CompanyDetailModal:acme:string"],
    ["Met 42", "MeteoriteDetailModal:42:number"],
  ])("clicking %s opens %s and stays on /search", async (rowText, expected) => {
    mockApis(() => jsonResponse({
      job: [job("j-rep", "Report job", "report"), job("j-det", "Detail job", "detail")],
      company: [company("acme")],
      meteorite: [meteorite(42)],
    }))
    renderPage()
    await userEvent.click(await screen.findByText(rowText))
    const modals = screen.getAllByTestId("open-modal")
    expect(modals).toHaveLength(1)
    expect(modals[0]).toHaveTextContent(expected)
    expect(screen.getByTestId("location")).toHaveTextContent("/search?q=acme")
  })

  // AC 13: closing a modal re-fetches in place; the row's State updates without a reload.
  it("closing a modal re-fetches and updates the row's State", async () => {
    let state = "IMPORTED"
    mockApis(() => jsonResponse({ ...empty, company: [company("acme", state)] }))
    renderPage()
    await userEvent.click(await screen.findByText("acme Inc"))
    state = "WATCHING"
    const before = searchCalls().length
    await userEvent.click(screen.getByRole("button", { name: "Close modal" }))
    await waitFor(() => expect(within(rowsOf("Companies (1)")[0]).getAllByRole("cell")[1]).toHaveTextContent("WATCHING"))
    expect(searchCalls().length).toBe(before + 1)
    expect(screen.queryByTestId("open-modal")).toBeNull()
    expect(screen.queryByText("Loading...")).toBeNull()
  })
})
