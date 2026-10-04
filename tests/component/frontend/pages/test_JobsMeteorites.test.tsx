import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { useLocation } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { useCandidate } from "../../../../src/ui/frontend/src/contexts/CandidateContext"
import api from "../../../../src/ui/frontend/src/lib/api"
import { fmtTime } from "../../../../src/ui/frontend/src/lib/fmt"
import { getUiConfig, loadUiConfig } from "../../../../src/ui/frontend/src/lib/uiConfig"
import JobsMeteorites from "../../../../src/ui/frontend/src/pages/JobsMeteorites"
import { renderWithProviders } from "../test-utils"
import { CUT_TITLE, EDGE_TITLE, expectJobTitleCells, jobTitleJobs } from "./job-title-cell"
import { candidateId, installBaseApiMocks, jsonResponse } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const LIST_COLUMNS = [
  { key: "state", label: "State", sortable: true },
  { key: "job_title", label: "Title", sortable: true },
  { key: "employer_name", label: "Employer", sortable: true },
]

const ROW_A = {
  id: 11,
  candidate_id: "c1",
  state: "READY",
  job_title: "Title A",
  employer_name: "Employer A",
  classify_outcome: "link",
  link: "https://a.example/j",
  astral_job_id: "job-a",
}

const ROW_B = {
  id: 22,
  candidate_id: "c2",
  state: "NEW",
  job_title: "Title B",
  employer_name: "Employer B",
  classify_outcome: null,
  link: "not-http",
  astral_job_id: null,
}

const DETAIL_SECTIONS = [
  { section_id: "meteorite_timestamps", nav_label: "Timestamps", default_expanded: true },
  { section_id: "meteorite_link", nav_label: "Link", default_expanded: true },
  { section_id: "meteorite_content", nav_label: "Content", default_expanded: true },
  { section_id: "meteorite_provenance", nav_label: "Provenance", default_expanded: false },
  { section_id: "meteorite_job", nav_label: "Linked Job", default_expanded: true },
]

function CandidateSelectC2() {
  const { setSelectedId } = useCandidate()
  return (
    <button type="button" onClick={() => setSelectedId("c2")}>
      Select c2
    </button>
  )
}

function listUrl(cid: string) {
  return `/api/candidates/${encodeURIComponent(cid)}/meteorites`
}

describe("JobsMeteorites — AST-1749", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("renders page title and loads candidate-scoped list from API columns", async () => {
    installBaseApiMocks(mockedApi, (url) => {
      if (url === listUrl(candidateId)) {
        return jsonResponse({ columns: LIST_COLUMNS, meteorites: [ROW_A] })
      }
      return undefined
    })
    renderWithProviders(<JobsMeteorites />)
    await waitFor(() => expect(screen.getByText("Meteorites")).toBeInTheDocument())
    await waitFor(() => expect(screen.getByText("Title A")).toBeInTheDocument())
    expect(screen.getByText("Employer A")).toBeInTheDocument()
    expect(mockedApi).toHaveBeenCalledWith(listUrl(candidateId))
    // Read-only: no mutate verbs on meteorite paths
    const mutate = mockedApi.mock.calls.filter(
      ([u, init]) =>
        typeof u === "string" &&
        u.includes("meteorite") &&
        init &&
        typeof init === "object" &&
        "method" in init &&
        ["POST", "PUT", "PATCH", "DELETE"].includes(String((init as RequestInit).method)),
    )
    expect(mutate).toHaveLength(0)
  })

  it("empty honesty — zero rows shows empty message, not placeholders", async () => {
    installBaseApiMocks(mockedApi, (url) => {
      if (url === listUrl(candidateId)) {
        return jsonResponse({ columns: LIST_COLUMNS, meteorites: [] })
      }
      return undefined
    })
    renderWithProviders(<JobsMeteorites />)
    await waitFor(() => expect(screen.getByText("No meteorites yet")).toBeInTheDocument())
    expect(screen.queryByText("Title A")).not.toBeInTheDocument()
  })

  it("candidate switch refetches and drops prior candidate rows", async () => {
    const user = userEvent.setup()
    installBaseApiMocks(mockedApi, (url) => {
      if (url === "/api/candidates") {
        return jsonResponse([
          { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} },
          { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: {} },
        ])
      }
      if (url === listUrl("c1")) {
        return jsonResponse({ columns: LIST_COLUMNS, meteorites: [ROW_A] })
      }
      if (url === listUrl("c2")) {
        return jsonResponse({ columns: LIST_COLUMNS, meteorites: [ROW_B] })
      }
      return undefined
    })
    renderWithProviders(
      <>
        <CandidateSelectC2 />
        <JobsMeteorites />
      </>,
    )
    await waitFor(() => expect(screen.getByText("Title A")).toBeInTheDocument())
    await user.click(screen.getByRole("button", { name: "Select c2" }))
    await waitFor(() => expect(screen.getByText("Title B")).toBeInTheDocument())
    expect(screen.queryByText("Title A")).not.toBeInTheDocument()
    expect(mockedApi).toHaveBeenCalledWith(listUrl("c2"))
  })

  it("row click opens detail modal with content and metadata", async () => {
    const user = userEvent.setup()
    installBaseApiMocks(mockedApi, (url) => {
      if (url === listUrl(candidateId)) {
        return jsonResponse({ columns: LIST_COLUMNS, meteorites: [ROW_A] })
      }
      if (url === "/api/meteorites/11") {
        return jsonResponse({
          sections: DETAIL_SECTIONS,
          meteorite: {
            id: 11,
            candidate_id: "c1",
            state: "READY",
            content: '{"ok":true}',
            classify_outcome: "link",
            link: "https://a.example/j",
            astral_job_id: "job-a",
            job_title: "Title A",
            employer_name: "Employer A",
            created_at: "2026-01-01T00:00:00Z",
            updated_at: "2026-01-02T00:00:00Z",
            state_changed_at: "2026-01-03T00:00:00Z",
            source_kind: "email",
            source_id: "mid-1",
            error: null,
            estelle_notified_at: null,
          },
        })
      }
      return undefined
    })
    renderWithProviders(<JobsMeteorites />)
    await waitFor(() => expect(screen.getByText("Title A")).toBeInTheDocument())
    await user.click(screen.getByText("Title A"))
    await waitFor(() => expect(screen.getByText("Timestamps")).toBeInTheDocument())
    expect(screen.getByText("created_at: 2026-01-01T00:00:00Z")).toBeInTheDocument()
    expect(screen.getByText("classify_outcome: link")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "https://a.example/j" })).toHaveAttribute(
      "href",
      "https://a.example/j",
    )
    expect(screen.getByRole("link", { name: /Open job job-a/ })).toHaveAttribute(
      "href",
      "/jobs/detail/job-a",
    )
    expect(mockedApi).toHaveBeenCalledWith("/api/meteorites/11")
  })
})

// AST-1976 AC 14: Job State cell = live job.state (AST-1974 LEFT JOIN), "—" when unlanded; the Job cell opens
// the Job Analysis Report in place (URL stays /jobs/meteorites); elsewhere on the row still opens the Meteorite modal.
// Production JOBS_METEORITES_LIST_COLUMNS keys/labels (src/utils/config.py): Job, Job State (AST-1976), Created (AST-1980).
const PROD_COLUMNS = [
  { key: "state", label: "State", sortable: true },
  { key: "job_title", label: "Title", sortable: true },
  { key: "employer_name", label: "Employer", sortable: true },
  { key: "classify_outcome", label: "Classify", sortable: true },
  { key: "link", label: "Link", sortable: true },
  { key: "astral_job_id", label: "Job", sortable: true },
  { key: "job_state", label: "Job State", sortable: true },
  { key: "job_created_at", label: "Created", sortable: true, type: "datetime" },
  { key: "state_changed_at", label: "State Changed", sortable: true, defaultDesc: true, type: "datetime" },
]

describe("JobsMeteorites — AST-1976 landed-job state and job link", () => {
  const LANDED = { ...ROW_A, job_state: "RECOMMENDED" }
  const UNLANDED = { ...ROW_B, candidate_id: "c1", job_state: null }
  // Minimal GET /api/jobs/<id> body for JobAnalysisReportModal (same shape as the Recommended row-click test).
  const reportJob = (state: string) => ({
    astral_job_id: "job-a",
    job_title: "Title A",
    company: "Employer A",
    state,
    can_skip: true,
    job_data: {
      job_description: "JD",
      analysis_upshot: {
        take_get: "x", take_do: "", take_like: "", take_jd: "", whole_jd_upshot: "Summary",
        segment_upshots: [], candidate_questions: [], caveats: [],
      },
    },
  })

  function LocationProbe() {
    return <p data-testid="pathname">{useLocation().pathname}</p>
  }

  function renderPage() {
    renderWithProviders(
      <>
        <JobsMeteorites />
        <LocationProbe />
      </>,
      { router: { initialEntries: ["/jobs/meteorites"] } },
    )
  }

  // Cell under the named header, by header index (column order comes from the API).
  const cellUnder = (rowText: string, header: string) => {
    const row = screen.getByText(rowText).closest("tr")!
    const headers = within(row.closest("table")!).getAllByRole("columnheader")
    return row.children[headers.findIndex(h => (h.textContent ?? "").startsWith(header))] as HTMLElement
  }

  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("Job State cell shows the landed job's state; unlanded rows show — in Job and Job State", async () => {
    installBaseApiMocks(mockedApi, url =>
      url === listUrl(candidateId) ? jsonResponse({ columns: PROD_COLUMNS, meteorites: [LANDED, UNLANDED] }) : undefined)
    renderPage()
    await waitFor(() => expect(screen.getByText("Title A")).toBeInTheDocument())
    expect(cellUnder("Title A", "Job State")).toHaveTextContent(/^RECOMMENDED$/)
    expect(within(cellUnder("Title A", "Job")).getByRole("button", { name: "job-a" })).toBeInTheDocument()
    expect(cellUnder("Title B", "Job State")).toHaveTextContent(/^—$/)
    expect(cellUnder("Title B", "Job")).toHaveTextContent(/^—$/)
    expect(within(cellUnder("Title B", "Job")).queryByRole("button")).toBeNull()
  })

  it("job link opens the Job Analysis Report in place; Meteorite modal stays closed", async () => {
    const user = userEvent.setup()
    installBaseApiMocks(mockedApi, url => {
      if (url === listUrl(candidateId)) return jsonResponse({ columns: PROD_COLUMNS, meteorites: [LANDED] })
      if (url === "/api/jobs/job-a") return jsonResponse(reportJob("RECOMMENDED"))
      return undefined
    })
    renderPage()
    await waitFor(() => expect(screen.getByText("Title A")).toBeInTheDocument())
    await user.click(screen.getByRole("button", { name: "job-a" }))
    await waitFor(() => expect(document.querySelector(".recommended-report-tabs")).toBeTruthy())
    expect(mockedApi).toHaveBeenCalledWith("/api/jobs/job-a")
    expect(screen.getByTestId("pathname")).toHaveTextContent(/^\/jobs\/meteorites$/)
    expect(mockedApi.mock.calls.some(([u]) => u === "/api/meteorites/11")).toBe(false)
    expect(screen.queryByText("Timestamps")).toBeNull()
  })

  it("clicking elsewhere on a landed row opens the Meteorite modal, not the report", async () => {
    const user = userEvent.setup()
    installBaseApiMocks(mockedApi, url => {
      if (url === listUrl(candidateId)) return jsonResponse({ columns: PROD_COLUMNS, meteorites: [LANDED] })
      if (url === "/api/meteorites/11") return jsonResponse({ sections: DETAIL_SECTIONS, meteorite: { ...LANDED } })
      return undefined
    })
    renderPage()
    await waitFor(() => expect(screen.getByText("Title A")).toBeInTheDocument())
    await user.click(cellUnder("Title A", "Job State"))
    await waitFor(() => expect(mockedApi).toHaveBeenCalledWith("/api/meteorites/11"))
    expect(mockedApi.mock.calls.some(([u]) => u === "/api/jobs/job-a")).toBe(false)
    expect(document.querySelector(".recommended-report-tabs")).toBeNull()
    expect(screen.getByTestId("pathname")).toHaveTextContent(/^\/jobs\/meteorites$/)
  })

  it("Skip in the report reloads the list so Job State is not stale", async () => {
    const user = userEvent.setup()
    let jobState = "RECOMMENDED"
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === listUrl(candidateId)) {
        return jsonResponse({ columns: PROD_COLUMNS, meteorites: [{ ...LANDED, job_state: jobState }] })
      }
      if (url === "/api/jobs/job-a" && !init) return jsonResponse(reportJob(jobState))
      if (url === "/api/jobs/job-a/skip" && init?.method === "POST") {
        jobState = "CANDIDATE_SKIPPED"
        return jsonResponse({ ok: true })
      }
      return undefined
    })
    renderPage()
    await waitFor(() => expect(cellUnder("Title A", "Job State")).toHaveTextContent(/^RECOMMENDED$/))
    await user.click(screen.getByRole("button", { name: "job-a" }))
    await user.click(await screen.findByRole("button", { name: "Skip this Job" }))
    await waitFor(() => expect(cellUnder("Title A", "Job State")).toHaveTextContent(/^CANDIDATE_SKIPPED$/))
    expect(document.querySelector(".recommended-report-tabs")).toBeNull()
  })
})

// AST-1980 AC 6 / AC 7: config-served Created column = landed job's created_at (job_created_at), not the
// meteorite's own created_at; "—" when unlanded; sorts through ListPage with no page code.
describe("JobsMeteorites — AST-1980 Created column", () => {
  // Own created_at is the same on every row and far from job_created_at, so showing it as Created can't pass.
  const OWN_CREATED = "2026-02-01T00:00:00Z"
  const EARLY = { ...ROW_A, created_at: OWN_CREATED, job_created_at: "2025-06-01T12:00:00Z" }
  const UNLANDED = { ...ROW_B, candidate_id: "c1", astral_job_id: null, created_at: OWN_CREATED, job_created_at: null }
  const LATE = { ...ROW_A, id: 33, job_title: "Title C", astral_job_id: "job-c", created_at: OWN_CREATED, job_created_at: "2025-09-15T08:30:00Z" }

  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("Created sits left of State Changed, shows job_created_at (— when unlanded), and sorts / toggles", async () => {
    installBaseApiMocks(mockedApi, url =>
      url === listUrl(candidateId) ? jsonResponse({ columns: PROD_COLUMNS, meteorites: [EARLY, UNLANDED, LATE] }) : undefined)
    // ListPage reads a module-level ui_config cache (earlier tests fill it with column_types: {}).
    // Prime it, then give it production column_types.datetime so cells go through formatCell(…, "datetime").
    await new Promise<void>(resolve => loadUiConfig(resolve))
    const types = getUiConfig()!.column_types
    const prior = types.datetime
    types.datetime = { align: "left", number_format: "datetime" }
    try {
      await assertCreatedColumn()
    } finally {
      if (prior) types.datetime = prior
      else delete types.datetime
    }
  })

  async function assertCreatedColumn() {
    renderWithProviders(<JobsMeteorites />)
    await waitFor(() => expect(screen.getByText("Title C")).toBeInTheDocument())

    const table = screen.getByText("Title C").closest("table")!
    const headers = () => within(table).getAllByRole("columnheader")
    const idx = (label: string) => headers().findIndex(h => (h.textContent ?? "").startsWith(label))
    const created = idx("Created")
    expect(created).toBeGreaterThan(-1)
    expect(idx("State Changed")).toBe(created + 1)

    const rowOf = (title: string) => screen.getByText(title).closest("tr")!
    const createdCell = (title: string) => rowOf(title).children[created].textContent
    expect(createdCell("Title A")).toBe(fmtTime(EARLY.job_created_at))
    expect(createdCell("Title C")).toBe(fmtTime(LATE.job_created_at))
    expect(createdCell("Title B")).toBe("\u2014")
    expect(createdCell("Title A")).not.toBe(fmtTime(OWN_CREATED))

    const titles = () => within(table).getAllByRole("row").slice(1).map(r => r.children[idx("Title")].textContent)
    // No defaultDesc: first click ascending (null first), second click reverses; indicator on Created.
    await userEvent.click(headers()[created])
    expect(titles()).toEqual(["Title B", "Title A", "Title C"])
    expect(headers()[created].textContent).toMatch(/^Created ▲/)
    await userEvent.click(headers()[created])
    expect(titles()).toEqual(["Title C", "Title A", "Title B"])
    expect(headers()[created].textContent).toMatch(/^Created ▼/)
  }
})

// AST-1982 AC 4 / AC 7: job_title escapes ListPage's 30-char cut (cut at 50 via JobTitleText); other columns keep 30;
// search still reads the full raw title.
describe("JobsMeteorites — AST-1982 Job Title cut", () => {
  const LONG_EMPLOYER = "Employer Name That Runs Past Thirty Chars"
  const rows = jobTitleJobs(ROW_A).map((r, i) => ({ ...r, id: 40 + i, employer_name: i === 0 ? LONG_EMPLOYER : "Short Co" }))

  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    installBaseApiMocks(mockedApi, url =>
      url === listUrl(candidateId) ? jsonResponse({ columns: PROD_COLUMNS, meteorites: rows }) : undefined)
  })

  it("Title cut at 50 + … with portaled tooltip; 50-char title untouched; other columns still cut at 30", async () => {
    renderWithProviders(<JobsMeteorites />)
    await waitFor(() => expect(screen.getByText(EDGE_TITLE)).toBeInTheDocument())
    await expectJobTitleCells(screen.getByText(EDGE_TITLE).closest("table")!, /^Title/)
    expect(screen.getByText(`${LONG_EMPLOYER.slice(0, 30)}\u2026`)).toBeInTheDocument()
    expect(screen.getByTitle(LONG_EMPLOYER)).toBeInTheDocument()
  })

  it("search for a word past char 50 of a title still returns that row", async () => {
    renderWithProviders(<JobsMeteorites />)
    await waitFor(() => expect(screen.getByText(EDGE_TITLE)).toBeInTheDocument())
    expect(CUT_TITLE).not.toContain("Zanzibar")
    await userEvent.type(screen.getByPlaceholderText("Search..."), "Zanzibar")
    await waitFor(() => expect(screen.queryByText(EDGE_TITLE)).toBeNull())
    expect(screen.getByText(CUT_TITLE)).toBeInTheDocument()
  })
})
