import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import JobsRecommended from "../../../../src/ui/frontend/src/pages/JobsRecommended"
import { renderWithProviders } from "../test-utils"
import { baseCandidate, installBaseApiMocks, jobsViewHandler, jsonResponse } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const sectionedJobs = [
  {
    astral_job_id: "j-rec",
    job_title: "Rec Role",
    company: "Zulu",
    state: "RECOMMENDED",
    state_changed_at: "2026-01-03T00:00:00Z",
    jd_score: 8.5,
    do_score: 7.0,
    get_score: 6.0,
    like_score: null,
  },
  {
    astral_job_id: "j-rec2",
    job_title: "Rec Role B",
    company: "Acme",
    state: "RECOMMENDED",
    state_changed_at: "2026-01-02T00:00:00Z",
    jd_score: 5.0,
    do_score: 5.0,
    get_score: 5.0,
    like_score: 5.0,
  },
  {
    astral_job_id: "j-prog",
    job_title: "Prog Role",
    company: "Gamma Co",
    state: "BUILD_ARTIFACTS",
    state_changed_at: "2026-01-02T00:00:00Z",
    jd_score: 7.0,
    do_score: 7.0,
    get_score: 7.0,
    like_score: 7.0,
  },
  {
    astral_job_id: "j-ready",
    job_title: "Ready Role",
    company: "Beta",
    state: "CANDIDATE_REVIEW",
    state_changed_at: "2026-01-01T00:00:00Z",
    jd_score: 9.0,
    do_score: 9.0,
    get_score: 9.0,
    like_score: 9.0,
  },
]

describe("JobsRecommended", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("groups jobs into state sections with JD/DO/GET/LIKE phase scores", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("recommended", sectionedJobs))
    renderWithProviders(<JobsRecommended />)
    await waitFor(() => expect(screen.getByText("Rec Role")).toBeInTheDocument())

    expect(screen.getByRole("heading", { name: /Recommended \(2\)/ })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: /In Progress \(1\)/ })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: /Ready \(1\)/ })).toBeInTheDocument()

    expect(screen.getByText("Prog Role")).toBeInTheDocument()
    expect(screen.getByText("Ready Role")).toBeInTheDocument()

    for (const label of ["JD", "DO", "GET", "LIKE"]) {
      expect(screen.getAllByRole("columnheader", { name: new RegExp(`^${label}`) }).length).toBeGreaterThan(0)
    }
    expect(screen.queryByRole("columnheader", { name: /^Score/ })).not.toBeInTheDocument()
    expect(screen.queryByRole("columnheader", { name: /Passed At/ })).not.toBeInTheDocument()
    expect(screen.getAllByRole("columnheader", { name: /Updated/ }).length).toBeGreaterThan(0)

    const recSection = screen.getByRole("heading", { name: /Recommended \(2\)/ }).parentElement!
    expect(within(recSection).getByText("8.5")).toBeInTheDocument()
    expect(within(recSection).getAllByText("\u2014").length).toBeGreaterThan(0)
  })

  it("sorts by company within a section", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("recommended", sectionedJobs))
    renderWithProviders(<JobsRecommended />)
    await waitFor(() => expect(screen.getByText("Rec Role")).toBeInTheDocument())

    const recSection = screen.getByRole("heading", { name: /Recommended \(2\)/ }).parentElement!
    const companyHeader = within(recSection).getByRole("columnheader", { name: /Company/ })
    // AST-1968: Analysis toggle defaults on — skip the expanded row under each job row.
    const jobRows = () =>
      within(recSection).getAllByRole("row").slice(1)
        .filter(r => !r.classList.contains("recommended-analysis-row"))
        .map(r => r.textContent ?? "")
    await userEvent.click(companyHeader)
    const rowsAsc = jobRows()
    expect(rowsAsc[0]).toContain("Acme")
    expect(rowsAsc[1]).toContain("Zulu")
    await userEvent.click(companyHeader)
    const rowsDesc = jobRows()
    expect(rowsDesc[0]).toContain("Zulu")
    expect(rowsDesc[1]).toContain("Acme")
  })

  it("opens the report modal from a row click", async () => {
    const listHandler = jobsViewHandler("recommended", [sectionedJobs[0]])
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j-rec" && !init) {
        return jsonResponse({
          ...sectionedJobs[0],
          job_data: {
            job_description: "JD",
            analysis_upshot: {
              take_get: "x",
              take_do: "",
              take_like: "",
              take_jd: "",
              whole_jd_upshot: "Summary",
              segment_upshots: [],
              candidate_questions: [],
              caveats: [],
            },
          },
        })
      }
      return listHandler(url, init)
    })
    renderWithProviders(<JobsRecommended />)
    await waitFor(() => expect(screen.getByText("Rec Role")).toBeInTheDocument())
    await userEvent.click(screen.getByText("Rec Role"))
    // AST-948: horizontal top tabs (not left side-tab rail)
    await waitFor(() => expect(document.querySelector(".recommended-report-tabs")).toBeTruthy())
    const bar = document.querySelector(".recommended-report-tabs") as HTMLElement
    // AST-1874: report opens on the first manifest tab (Analysis) — modal default, not list output
    await waitFor(() => expect(within(bar).getByRole("button", { name: "Analysis" })).toHaveClass("active"))
    expect(screen.getByText("JD Analysis")).toBeInTheDocument()
    expect(document.querySelector(".side-tab-list")).toBeNull()
    expect(screen.queryByText("State History")).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Skip This Job" })).not.toBeInTheDocument()
  })

  it("shows Skip without Jr on Recommended rows (AST-565)", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("recommended", [sectionedJobs[0]]))
    renderWithProviders(<JobsRecommended />)
    await waitFor(() => expect(screen.getByText("Rec Role")).toBeInTheDocument())
    expect(screen.getByRole("button", { name: "Skip" })).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "View Job Analysis" })).not.toBeInTheDocument()
  })

  it("shows empty state for invalid payloads", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("recommended", { bad: true } as unknown as typeof sectionedJobs))
    renderWithProviders(<JobsRecommended />)
    await waitFor(() => expect(screen.getByText("No recommended jobs yet")).toBeInTheDocument())
  })

  it("shows Actions column with Skip for review-like rows", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("recommended", sectionedJobs))
    renderWithProviders(<JobsRecommended />)
    await waitFor(() => expect(screen.getByText("Ready Role")).toBeInTheDocument())
    expect(screen.getAllByRole("columnheader", { name: "Actions" }).length).toBeGreaterThan(0)
    expect(screen.getAllByRole("button", { name: "Skip" }).length).toBeGreaterThan(0)
    expect(screen.queryByRole("button", { name: "View Job Analysis" })).not.toBeInTheDocument()
  })

  it("skip action calls API without opening report modal", async () => {
    const reviewJob = {
      ...sectionedJobs[3],
      astral_job_id: "j-review",
      job_title: "Review Role",
    }
    installBaseApiMocks(mockedApi, jobsViewHandler("recommended", [reviewJob]))
    renderWithProviders(<JobsRecommended />)
    await waitFor(() => expect(screen.getByText("Review Role")).toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "Skip" }))
    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith("/api/jobs/j-review/skip", { method: "POST" }),
    )
    expect(mockedApi.mock.calls.some(([url]) => url === "/api/jobs/j-review" && !String(url).includes("/skip"))).toBe(
      false,
    )
  })

  it("skip works for RECOMMENDED state rows", async () => {
    const recommendedJob = {
      ...sectionedJobs[0],
      astral_job_id: "j-rec-only",
      job_title: "Recommended Only",
    }
    installBaseApiMocks(mockedApi, jobsViewHandler("recommended", [recommendedJob]))
    renderWithProviders(<JobsRecommended />)
    await waitFor(() => expect(screen.getByText("Recommended Only")).toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "Skip" }))
    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith("/api/jobs/j-rec-only/skip", { method: "POST" }),
    )
  })

  describe("AST-1410 silent refetch", () => {
    it("Skip refreshes the list without Loading...", async () => {
      const recommendedJob = {
        ...sectionedJobs[0],
        astral_job_id: "j-rec-silent",
        job_title: "Silent Rec",
      }
      installBaseApiMocks(mockedApi, jobsViewHandler("recommended", [recommendedJob]))
      renderWithProviders(<JobsRecommended />)
      await waitFor(() => expect(screen.getByText("Silent Rec")).toBeInTheDocument())
      const inner = mockedApi.getMockImplementation()!
      let release: (value: Response) => void = () => {}
      mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
        if (typeof url === "string" && url.includes("view=recommended") && !init?.method) {
          return new Promise<Response>((resolve) => { release = resolve })
        }
        return inner(url, init)
      })
      await userEvent.click(screen.getByRole("button", { name: "Skip" }))
      expect(screen.getByText("Silent Rec")).toBeInTheDocument()
      expect(screen.queryByText("Loading...")).not.toBeInTheDocument()
      release({ ok: true, json: async () => [] } as Response)
      await waitFor(() => expect(screen.getByText("No recommended jobs yet")).toBeInTheDocument())
    })
  })
})

  it("AST-1057: prepends Meteorites for meteorite- company jobs; leaves vetted sections intact", async () => {
    const mixed = [
      ...sectionedJobs,
      {
        astral_job_id: "j-met-rec",
        job_title: "Meteorite Rec",
        company: "meteorite-cand-1",
        state: "RECOMMENDED",
        state_changed_at: "2026-01-04T00:00:00Z",
        jd_score: 8.0,
        do_score: 8.0,
        get_score: 8.0,
        like_score: 8.0,
      },
      {
        astral_job_id: "j-met-ready",
        job_title: "Meteorite Ready",
        company: "meteorite-cand-1",
        state: "CANDIDATE_REVIEW",
        state_changed_at: "2026-01-05T00:00:00Z",
        jd_score: 9.0,
        do_score: 9.0,
        get_score: 9.0,
        like_score: 9.0,
      },
    ]
    installBaseApiMocks(mockedApi, jobsViewHandler("recommended", mixed))
    renderWithProviders(<JobsRecommended />)
    await waitFor(() => expect(screen.getByText("Meteorite Rec")).toBeInTheDocument())

    expect(screen.getByRole("heading", { name: /Meteorites \(2\)/ })).toBeInTheDocument()
    // Vetted-company Recommended / In Progress / Ready unchanged.
    expect(screen.getByRole("heading", { name: /Recommended \(2\)/ })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: /In Progress \(1\)/ })).toBeInTheDocument()
    expect(screen.getByRole("heading", { name: /Ready \(1\)/ })).toBeInTheDocument()

    const met = screen.getByRole("heading", { name: /Meteorites \(2\)/ }).parentElement!
    expect(within(met).getByText("Meteorite Rec")).toBeInTheDocument()
    expect(within(met).getByText("Meteorite Ready")).toBeInTheDocument()
    // Meteorites section renders first among list-page-section headings.
    const headings = screen.getAllByRole("heading").map(h => h.textContent ?? "")
    const metIdx = headings.findIndex(t => /Meteorites \(2\)/.test(t))
    const recIdx = headings.findIndex(t => /Recommended \(2\)/.test(t))
    expect(metIdx).toBeGreaterThanOrEqual(0)
    expect(metIdx).toBeLessThan(recIdx)
  })

  it("AST-1057: omits Meteorites when no meteorite- company jobs", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("recommended", sectionedJobs))
    renderWithProviders(<JobsRecommended />)
    await waitFor(() => expect(screen.getByText("Rec Role")).toBeInTheDocument())
    expect(screen.queryByRole("heading", { name: /Meteorites/ })).not.toBeInTheDocument()
    expect(screen.getByRole("heading", { name: /Recommended \(2\)/ })).toBeInTheDocument()
  })

  // AST-1708/AST-1709: null company must not throw in isMeteoriteJob; stays out of Meteorites.
  it("AST-1708/AST-1709: null company does not throw; stays out of Meteorites", async () => {
    const mixed = [
      ...sectionedJobs,
      {
        astral_job_id: "j-null-co",
        job_title: "Null Company Rec",
        company: null as unknown as string,
        state: "RECOMMENDED",
        state_changed_at: "2026-01-06T00:00:00Z",
        jd_score: 1,
        do_score: 1,
        get_score: 1,
        like_score: 1,
      },
      {
        astral_job_id: "j-met-null-case",
        job_title: "Meteorite Rec",
        company: "meteorite-cand-1",
        state: "RECOMMENDED",
        state_changed_at: "2026-01-04T00:00:00Z",
        jd_score: 8.0,
        do_score: 8.0,
        get_score: 8.0,
        like_score: 8.0,
      },
    ]
    installBaseApiMocks(mockedApi, jobsViewHandler("recommended", mixed))
    renderWithProviders(<JobsRecommended />)
    await waitFor(() => expect(screen.getByText("Null Company Rec")).toBeInTheDocument())

    expect(screen.getByRole("heading", { name: /Meteorites \(1\)/ })).toBeInTheDocument()
    const met = screen.getByRole("heading", { name: /Meteorites \(1\)/ }).parentElement!
    expect(within(met).getByText("Meteorite Rec")).toBeInTheDocument()
    expect(within(met).queryByText("Null Company Rec")).not.toBeInTheDocument()

    expect(screen.getByRole("heading", { name: /Recommended \(3\)/ })).toBeInTheDocument()
    const rec = screen.getByRole("heading", { name: /Recommended \(3\)/ }).parentElement!
    expect(within(rec).getByText("Null Company Rec")).toBeInTheDocument()
  })

describe("JobsRecommended — AST-1968 triage upgrades", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  // List GET + per-job POSTs over a mutable row set, so each refresh reflects the action:
  // generate → BUILD_ARTIFACTS (In Progress); skip / candidate_action → row leaves the list.
  function statefulJobsHandler(initial: Array<Record<string, unknown>>) {
    let rows = initial.map(j => ({ ...j }))
    const posts: string[] = []
    const handler = (url: string, init?: RequestInit) => {
      if (url.startsWith("/api/jobs?view=recommended") && !init) return jsonResponse(rows)
      const m = /^\/api\/jobs\/([^/]+)\/(skip|candidate_action|generate_artifacts)$/.exec(url)
      if (m && init?.method === "POST") {
        posts.push(url)
        const [, id, op] = m
        rows = op === "generate_artifacts"
          ? rows.map(j => (j.astral_job_id === id ? { ...j, state: "BUILD_ARTIFACTS" } : j))
          : rows.filter(j => j.astral_job_id !== id)
        return jsonResponse({ ok: true })
      }
      throw new Error(`unexpected api call: ${url}${init?.method ? ` ${init.method}` : ""}`)
    }
    return { handler, posts }
  }

  const section = (name: RegExp) => screen.getByRole("heading", { name }).parentElement!
  const rowOf = (title: string) => screen.getByText(title).closest("tr")!
  const select = (title: string) => userEvent.click(screen.getByRole("checkbox", { name: `Select ${title}` }))
  // Job rows only (Analysis toggle on by default adds a row under each).
  const jobTitles = (sec: HTMLElement) =>
    within(sec).getAllByRole("row").slice(1)
      .filter(r => !r.classList.contains("recommended-analysis-row"))
      .map(r => r.children[2]?.textContent ?? "")
  // Cell under the named header, located by header index (column order is manifest-driven).
  const cellUnder = (title: string, header: RegExp) => {
    const row = rowOf(title)
    const headers = within(row.closest("table")!).getAllByRole("columnheader")
    return row.children[headers.findIndex(h => header.test(h.textContent ?? ""))] as HTMLElement
  }

  async function renderPage(handler: (url: string, init?: RequestInit) => Response | Promise<Response>) {
    installBaseApiMocks(mockedApi, handler)
    renderWithProviders(<JobsRecommended />)
    await waitFor(() => expect(screen.getAllByRole("checkbox", { name: /^Select / }).length).toBeGreaterThan(0))
  }

  it("AC1/AC15: row Generate Artifacts only on RECOMMENDED rows", async () => {
    await renderPage(jobsViewHandler("recommended", sectionedJobs))
    const gen = { name: "Generate Artifacts" }
    expect(within(section(/^Recommended \(/)).getAllByRole("button", gen)).toHaveLength(2)
    expect(within(section(/^In Progress \(/)).queryByRole("button", gen)).toBeNull()
    expect(within(section(/^Ready \(/)).queryByRole("button", gen)).toBeNull()
  })

  it("AC2: row Generate POSTs generate_artifacts and the job moves to In Progress", async () => {
    const { handler, posts } = statefulJobsHandler(sectionedJobs)
    await renderPage(handler)
    await userEvent.click(within(rowOf("Rec Role")).getByRole("button", { name: "Generate Artifacts" }))
    await waitFor(() => expect(within(section(/^In Progress \(2\)/)).getByText("Rec Role")).toBeInTheDocument())
    expect(posts).toEqual(["/api/jobs/j-rec/generate_artifacts"])
  })

  it("AC4: bulk bar hidden with no selection; counts follow the checked rows", async () => {
    await renderPage(jobsViewHandler("recommended", sectionedJobs))
    // Every section's rows carry a checkbox.
    expect(screen.getAllByRole("checkbox", { name: /^Select / })).toHaveLength(sectionedJobs.length)
    for (const name of [/^Skip \(/, /^Applied \(/, /^Generate Artifacts \(/]) {
      expect(screen.queryByRole("button", { name })).toBeNull()
    }
    await select("Rec Role")
    await select("Rec Role B")
    await select("Ready Role")
    expect(screen.getByRole("button", { name: "Skip (3)" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Applied (3)" })).toBeInTheDocument()
    // n = checked RECOMMENDED jobs only
    expect(screen.getByRole("button", { name: "Generate Artifacts (2)" })).toBeInTheDocument()
  })

  it("AC5/AC8: bulk Skip posts every selected job, toasts the split, clears selection", async () => {
    const { handler, posts } = statefulJobsHandler(sectionedJobs)
    await renderPage(handler)
    await select("Rec Role")
    await select("Rec Role B")
    await select("Ready Role")
    await userEvent.click(screen.getByRole("button", { name: "Skip (3)" }))
    expect(await screen.findByText("Skip: 3 succeeded, 0 failed")).toBeInTheDocument()
    expect([...posts].sort()).toEqual([
      "/api/jobs/j-ready/skip",
      "/api/jobs/j-rec/skip",
      "/api/jobs/j-rec2/skip",
    ])
    await waitFor(() => expect(screen.queryByText("Rec Role")).toBeNull())
    expect(screen.queryByText("Rec Role B")).toBeNull()
    expect(screen.queryByText("Ready Role")).toBeNull()
    for (const box of screen.getAllByRole("checkbox", { name: /^Select / })) expect(box).not.toBeChecked()
    expect(screen.queryByRole("button", { name: /^Skip \(/ })).toBeNull()
  })

  it("AC6/AC8: bulk Applied opens one notes modal and applies the same note to each job", async () => {
    const { handler, posts } = statefulJobsHandler(sectionedJobs)
    await renderPage(handler)
    await select("Rec Role")
    await select("Prog Role")
    await userEvent.click(screen.getByRole("button", { name: "Applied (2)" }))
    expect(screen.getAllByPlaceholderText("Notes…")).toHaveLength(1)
    await userEvent.type(screen.getByPlaceholderText("Notes…"), "bulk-test")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    expect(await screen.findByText("Applied: 2 succeeded, 0 failed")).toBeInTheDocument()
    expect([...posts].sort()).toEqual(["/api/jobs/j-prog/candidate_action", "/api/jobs/j-rec/candidate_action"])
    const bodies = mockedApi.mock.calls
      .filter(([url]) => String(url).endsWith("/candidate_action"))
      .map(([, init]) => JSON.parse(String((init as RequestInit).body)))
    expect(bodies).toEqual([
      { action: "applied", notes: "bulk-test" },
      { action: "applied", notes: "bulk-test" },
    ])
    expect(screen.queryByPlaceholderText("Notes…")).toBeNull()
    for (const box of screen.getAllByRole("checkbox", { name: /^Select / })) expect(box).not.toBeChecked()
    expect(screen.queryByRole("button", { name: /^Applied \(/ })).toBeNull()
  })

  it("AC7/AC8: bulk Generate sends only eligible (RECOMMENDED) jobs", async () => {
    const { handler, posts } = statefulJobsHandler(sectionedJobs)
    await renderPage(handler)
    await select("Rec Role")
    await select("Ready Role")
    await userEvent.click(screen.getByRole("button", { name: "Generate Artifacts (1)" }))
    expect(await screen.findByText("Generate Artifacts: 1 succeeded, 0 failed")).toBeInTheDocument()
    expect(posts).toEqual(["/api/jobs/j-rec/generate_artifacts"])
    expect(within(section(/^Ready \(/)).getByText("Ready Role")).toBeInTheDocument()
    for (const box of screen.getAllByRole("checkbox", { name: /^Select / })) expect(box).not.toBeChecked()
    expect(screen.queryByRole("button", { name: /^Generate Artifacts \(/ })).toBeNull()
  })

  it("AC9: Analysis toggle defaults on with JD/DO/GET/LIKE lines under each job; off removes them", async () => {
    await renderPage(jobsViewHandler("recommended", sectionedJobs))
    const toggle = screen.getByRole("checkbox", { name: "Analysis" })
    expect(toggle).toBeChecked()
    const expanded = document.querySelectorAll("tr.recommended-analysis-row")
    expect(expanded).toHaveLength(sectionedJobs.length)
    for (const row of expanded) {
      // Directly under its own job row, never stacked on another expanded row.
      expect(row.previousElementSibling?.classList.contains("recommended-analysis-row")).toBe(false)
      const labels = [...row.querySelectorAll(".recommended-analysis-line-label")].map(l => l.textContent)
      expect(labels).toEqual(["JD", "DO", "GET", "LIKE"])
    }
    await userEvent.click(toggle)
    expect(document.querySelectorAll("tr.recommended-analysis-row")).toHaveLength(0)
    expect(document.querySelectorAll("tbody tr")).toHaveLength(sectionedJobs.length)
  })

  it("AC10: list grade circles carry no letter and no confidence bullets", async () => {
    const graded = {
      ...sectionedJobs[1],
      jd_grades: [{ vector: "Job Description (JD)", grade: "A", confidence: 4 }],
      do_grades: [{ vector: "Delivery", grade: "B", confidence: 3 }],
    }
    await renderPage(jobsViewHandler("recommended", [graded]))
    const expanded = document.querySelector("tr.recommended-analysis-row") as HTMLElement
    const dots = expanded.querySelectorAll(".grade-dot")
    expect(dots).toHaveLength(2)
    for (const dot of dots) {
      expect(dot).toHaveClass("grade-dot-letterless")
      expect(dot.textContent).toBe("")
    }
    expect(expanded.querySelector(".dot-a")).toBeTruthy()
    expect(expanded.querySelector(".dot-b")).toBeTruthy()
    expect(document.querySelector(".list-page-table .confidence-bullets")).toBeNull()
    // Phases without grades keep their line with an em dash (exactly four lines).
    expect(expanded.querySelectorAll(".recommended-analysis-line")).toHaveLength(4)
  })

  it("AC13: Total sums the four phase scores; any missing phase shows an em dash", async () => {
    const sum = { ...sectionedJobs[1], astral_job_id: "j-sum", job_title: "Sum Role",
      jd_score: 7.0, do_score: 6.5, get_score: 8.0, like_score: 5.5 }
    await renderPage(jobsViewHandler("recommended", [sum, sectionedJobs[0]]))
    expect(cellUnder("Sum Role", /^Total/)).toHaveTextContent(/^27\.0$/)
    // j-rec has like_score null
    expect(cellUnder("Rec Role", /^Total/)).toHaveTextContent(/^\u2014$/)
  })

  it("AC14: Total sorts asc/desc with missing totals placed like the phase columns", async () => {
    const sum = { ...sectionedJobs[1], astral_job_id: "j-sum", job_title: "Sum Role",
      jd_score: 7.0, do_score: 6.5, get_score: 8.0, like_score: 5.5 }
    // Rec Role (total —), Rec Role B (20.0), Sum Role (27.0)
    await renderPage(jobsViewHandler("recommended", [sectionedJobs[0], sectionedJobs[1], sum]))
    const rec = section(/^Recommended \(3\)/)
    const totalHeader = within(rec).getByRole("columnheader", { name: /^Total/ })
    await userEvent.click(totalHeader)
    expect(jobTitles(rec)).toEqual(["Rec Role B", "Sum Role", "Rec Role"])
    await userEvent.click(totalHeader)
    expect(jobTitles(rec)).toEqual(["Rec Role", "Sum Role", "Rec Role B"])
    // Same null placement as a phase column: LIKE has the same null on Rec Role.
    const likeHeader = within(rec).getByRole("columnheader", { name: /^LIKE/ })
    await userEvent.click(likeHeader)
    expect(jobTitles(rec)[2]).toBe("Rec Role")
    await userEvent.click(likeHeader)
    expect(jobTitles(rec)[0]).toBe("Rec Role")
  })
})

