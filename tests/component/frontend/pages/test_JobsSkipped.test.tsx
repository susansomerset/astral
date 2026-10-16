import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import JobsSkipped from "../../../../src/ui/frontend/src/pages/JobsSkipped"
import { renderWithProviders } from "../test-utils"
import { createdColumnJobs, expectCreatedColumn, installTzCandidate } from "./created-column"
import { expectJobTitleCells, jobTitleJobs } from "./job-title-cell"
import { installBaseApiMocks, jobsViewHandler } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const floorJob = {
  astral_job_id: "floor-1",
  job_title: "Floor Role",
  company: "Acme",
  state: "BUILD_ARTIFACTS",
  state_changed_at: "2026-01-02T00:00:00Z",
  latest_score: 0.42,
  dispatch_score_floor: 0.75,
  virtual_skip: true,
}

const failedJob = {
  astral_job_id: "fail-1",
  job_title: "Failed Role",
  company: "Beta",
  state: "FAILED_LIKE",
  state_changed_at: "2026-01-01T00:00:00Z",
  latest_score: 0.55,
  like_grades: [{ vector: "Technical (TE)", grade: "D", confidence: 0.2 }],
}


const meteoriteFailedDoJob = {
  astral_job_id: "met-do-1",
  job_title: "Meteorite Do Fail",
  company: "meteorite-co",
  state: "METEORITE_FAILED_DO",
  state_changed_at: "2026-01-03T00:00:00Z",
  latest_score: 0.4,
  do_grades: [{ vector: "Fit", grade: "F", confidence: 0.9 }],
}

const regularFailedGetJob = {
  astral_job_id: "reg-get-1",
  job_title: "Regular Get Fail",
  company: "Delta",
  state: "FAILED_GET",
  state_changed_at: "2026-01-03T01:00:00Z",
  latest_score: 0.35,
  get_grades: [{ vector: "Fit", grade: "F", confidence: 0.8 }],
}

const skippedJob = {
  astral_job_id: "skip-1",
  job_title: "Skipped Role",
  company: "Gamma",
  state: "CANDIDATE_SKIPPED",
  state_changed_at: "2026-01-04T00:00:00Z",
  latest_score: 0.6,
  like_grades: [{ vector: "Technical (TE)", grade: "B", confidence: 0.5 }],
}

describe("JobsSkipped", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("renders floor and failed sections, selects rows, and retries", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("skipped", [floorJob, failedJob]))
    renderWithProviders(<JobsSkipped />)
    await waitFor(() => expect(screen.getByText(/Below dispatch score floor/)).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: /Below dispatch score floor/ }))
    await userEvent.click(screen.getByRole("columnheader", { name: /State/ }))
    await userEvent.click(screen.getByRole("columnheader", { name: /Score/ }))
    await userEvent.click(screen.getByText("Floor Role"))
    await userEvent.click(screen.getByRole("button", { name: /Below dispatch score floor/ }))
    await userEvent.click(screen.getByRole("button", { name: /Failed LIKE/ }))
    const checkbox = screen.getByRole("checkbox")
    await userEvent.click(checkbox)
    const retry = screen.getByRole("button", { name: "Retry (1)" })
    expect(retry).toHaveClass("btn", "primary")
    await userEvent.click(retry)
    await waitFor(() => expect(screen.getByText("1 jobs queued for retry")).toBeInTheDocument())
    // AST-1156: FAILED_LIKE → CULTURE_READY (not hard-coded NEW).
    expect(mockedApi).toHaveBeenCalledWith(
      "/api/jobs/bulk_state",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ astral_job_ids: ["fail-1"], to_state: "CULTURE_READY" }),
      }),
    )
    await userEvent.click(checkbox)
    await userEvent.click(screen.getByRole("columnheader", { name: /TE/ }))
    await userEvent.click(screen.getByText("Failed Role"))
  })

  it("handles empty payloads and retry failures", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("skipped", { bad: true } as unknown as typeof failedJob[]))
    renderWithProviders(<JobsSkipped />)
    await waitFor(() => expect(screen.getByText("No skipped jobs")).toBeInTheDocument())

    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/bulk_state") {
        return Promise.reject(new Error("network"))
      }
      return jobsViewHandler("skipped", [failedJob])(url, init)
    })
    renderWithProviders(<JobsSkipped />)
    await waitFor(() => expect(screen.getByText(/Failed LIKE/)).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: /Failed LIKE/ }))
    await userEvent.click(screen.getByRole("checkbox"))
    await userEvent.click(screen.getByRole("button", { name: "Retry (1)" }))
    await waitFor(() => expect(screen.getByText("Retry failed")).toBeInTheDocument())
  })

  it("shows Resurrect action on CANDIDATE_SKIPPED rows when section is expanded", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("skipped", [skippedJob]))
    renderWithProviders(<JobsSkipped />)
    await waitFor(() => expect(screen.getByRole("button", { name: /CANDIDATE_SKIPPED/ })).toBeInTheDocument())
    expect(screen.queryByRole("button", { name: "Resurrect" })).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: /CANDIDATE_SKIPPED/ }))
    expect(screen.getByRole("columnheader", { name: "Actions" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Resurrect" })).toBeInTheDocument()
  })

  it("resurrect on CANDIDATE_SKIPPED posts candidate_action review", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("skipped", [skippedJob]))
    renderWithProviders(<JobsSkipped />)
    await waitFor(() => expect(screen.getByRole("button", { name: /CANDIDATE_SKIPPED/ })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: /CANDIDATE_SKIPPED/ }))
    await userEvent.click(screen.getByRole("button", { name: "Resurrect" }))
    await waitFor(() => expect(screen.getByRole("heading", { name: "Return to review" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith(
        "/api/jobs/skip-1/candidate_action",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ action: "review", notes: "" }),
        }),
      ),
    )
  })

  describe("AST-893 Expand One default", () => {
    it("opening a second section closes the first; no Expand all chrome", async () => {
      installBaseApiMocks(mockedApi, jobsViewHandler("skipped", [floorJob, failedJob]))
      renderWithProviders(<JobsSkipped />)
      await waitFor(() => expect(screen.getByText(/Below dispatch score floor/)).toBeInTheDocument())
      expect(screen.queryByRole("button", { name: "Expand all" })).not.toBeInTheDocument()
      expect(screen.queryByRole("button", { name: "Collapse all" })).not.toBeInTheDocument()

      await userEvent.click(screen.getByRole("button", { name: /Below dispatch score floor/ }))
      expect(screen.getByText("Floor Role")).toBeInTheDocument()

      await userEvent.click(screen.getByRole("button", { name: /Failed LIKE/ }))
      expect(screen.getByText("Failed Role")).toBeInTheDocument()
      expect(screen.queryByText("Floor Role")).not.toBeInTheDocument()
    })
  })

  describe("AST-1064 group-by job-carried rubric", () => {
    const rubricNarrow = [{ code: "ET", label: "Employment Type", importance: 5, grade_descriptions: [] }]
    const rubricWide = [
      { code: "CS", label: "Company Stage", importance: 5, grade_descriptions: [] },
      { code: "ET", label: "Employment Type", importance: 3, grade_descriptions: [] },
    ]

    it("renders separate tables for different like_rubric shapes and paints grades + phase score", async () => {
      const jobs = [
        {
          astral_job_id: "a1",
          job_title: "Aligned A",
          company: "meteorite-somerset",
          state: "FAILED_LIKE",
          state_changed_at: "2026-01-05T00:00:00Z",
          like_rubric: rubricNarrow,
          like_grades: [{ vector: "Employment Type", grade: "X", confidence: 0 }],
          like_score: 10,
          latest_score: 1,
        },
        {
          astral_job_id: "a2",
          job_title: "Aligned B",
          company: "meteorite-somerset",
          state: "FAILED_LIKE",
          state_changed_at: "2026-01-04T00:00:00Z",
          like_rubric: rubricNarrow,
          like_grades: [{ vector: "Employment Type", grade: "X", confidence: 0 }],
          like_score: 10,
          latest_score: 1,
        },
        {
          astral_job_id: "b1",
          job_title: "Other Shape",
          company: "OtherCo",
          state: "FAILED_LIKE",
          state_changed_at: "2026-01-03T00:00:00Z",
          like_rubric: rubricWide,
          like_grades: [
            { vector: "Company Stage", grade: "F", confidence: 2 },
            { vector: "Employment Type", grade: "X", confidence: 0 },
          ],
          like_score: 3.5,
          latest_score: 99,
        },
      ]
      installBaseApiMocks(mockedApi, jobsViewHandler("skipped", jobs))
      renderWithProviders(<JobsSkipped />)
      await waitFor(() => expect(screen.getByRole("button", { name: /Failed LIKE/ })).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: /Failed LIKE/ }))

      const tables = document.querySelectorAll(".list-page-table")
      expect(tables.length).toBeGreaterThanOrEqual(2)
      expect(screen.getAllByRole("columnheader", { name: "ET" }).length).toBeGreaterThanOrEqual(2)
      expect(screen.getByRole("columnheader", { name: "CS" })).toBeInTheDocument()
      expect(screen.getByText("Aligned A")).toBeInTheDocument()
      expect(screen.getByText("Other Shape")).toBeInTheDocument()
      expect(document.querySelectorAll(".grade-dot").length).toBeGreaterThanOrEqual(3)
      expect(screen.getAllByText("10.00").length).toBeGreaterThanOrEqual(2)
      expect(screen.getByText("3.50")).toBeInTheDocument()
      expect(screen.queryByText("99.00")).not.toBeInTheDocument()
      expect(screen.queryByText("1.00")).not.toBeInTheDocument()
    })

    it("keeps one table when all jobs share the same job-carried rubric", async () => {
      const jobs = [
        {
          astral_job_id: "s1",
          job_title: "Same One",
          company: "Co",
          state: "FAILED_LIKE",
          state_changed_at: "2026-01-02T00:00:00Z",
          like_rubric: rubricNarrow,
          like_grades: [{ vector: "Employment Type", grade: "X", confidence: 0 }],
          like_score: 2,
        },
        {
          astral_job_id: "s2",
          job_title: "Same Two",
          company: "Co",
          state: "FAILED_LIKE",
          state_changed_at: "2026-01-01T00:00:00Z",
          like_rubric: rubricNarrow,
          like_grades: [{ vector: "Employment Type", grade: "F", confidence: 2 }],
          like_score: 4,
        },
      ]
      installBaseApiMocks(mockedApi, jobsViewHandler("skipped", jobs))
      renderWithProviders(<JobsSkipped />)
      await waitFor(() => expect(screen.getByRole("button", { name: /Failed LIKE/ })).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: /Failed LIKE/ }))
      expect(document.querySelectorAll(".list-page-table")).toHaveLength(1)
      expect(screen.getByRole("columnheader", { name: "ET" })).toBeInTheDocument()
      expect(screen.getByText("Same One")).toBeInTheDocument()
      expect(screen.getByText("Same Two")).toBeInTheDocument()
    })
  })

  describe("AST-1086 compact headers and grade-dot tooltips", () => {
    it("grades-only Failed LIKE shows compact TE header with full-name title", async () => {
      installBaseApiMocks(mockedApi, jobsViewHandler("skipped", [failedJob]))
      renderWithProviders(<JobsSkipped />)
      await waitFor(() => expect(screen.getByRole("button", { name: /Failed LIKE/ })).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: /Failed LIKE/ }))
      const th = screen.getByRole("columnheader", { name: "TE" })
      expect(th).toHaveAttribute("title", "Technical (5)")
      expect(th.textContent).toMatch(/^TE/)
      expect(screen.queryByRole("columnheader", { name: /Technical \(TE\)/ })).not.toBeInTheDocument()
    })

    it("grade-dot title includes reason and confidence parenthetical", async () => {
      const job = {
        astral_job_id: "tip-1",
        job_title: "Tooltip Role",
        company: "TipCo",
        state: "FAILED_LIKE",
        state_changed_at: "2026-01-06T00:00:00Z",
        like_grades: [{
          vector: "Technical (TE)",
          grade: "B",
          confidence: 4,
          reason: "Strong match on stack",
        }],
      }
      installBaseApiMocks(mockedApi, jobsViewHandler("skipped", [job]))
      renderWithProviders(<JobsSkipped />)
      await waitFor(() => expect(screen.getByRole("button", { name: /Failed LIKE/ })).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: /Failed LIKE/ }))
      const dot = document.querySelector(".grade-dot.dot-b")
      expect(dot).toBeTruthy()
      expect(dot?.getAttribute("title")).toBe(
        "Strong match on stack (The source strongly suggests it.)",
      )
    })
  })

  describe("AST-1156 hop-correct Skipped Retry", () => {
    it("retries meteorite FAILED_DO to METEORITE_PASSED_JD", async () => {
      installBaseApiMocks(mockedApi, jobsViewHandler("skipped", [meteoriteFailedDoJob]))
      renderWithProviders(<JobsSkipped />)
      await waitFor(() =>
        expect(screen.getByRole("button", { name: /Meteorite Failed DO/i })).toBeInTheDocument(),
      )
      await userEvent.click(screen.getByRole("button", { name: /Meteorite Failed DO/i }))
      await userEvent.click(screen.getByRole("checkbox"))
      await userEvent.click(screen.getByRole("button", { name: "Retry (1)" }))
      await waitFor(() => expect(screen.getByText("1 jobs queued for retry")).toBeInTheDocument())
      expect(mockedApi).toHaveBeenCalledWith(
        "/api/jobs/bulk_state",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            astral_job_ids: ["met-do-1"],
            to_state: "METEORITE_PASSED_JD",
          }),
        }),
      )
    })

    it("mixed meteorite Do fail + regular Get fail posts two hop-correct destinations", async () => {
      installBaseApiMocks(
        mockedApi,
        jobsViewHandler("skipped", [meteoriteFailedDoJob, regularFailedGetJob]),
      )
      renderWithProviders(<JobsSkipped />)
      await waitFor(() =>
        expect(screen.getByRole("button", { name: /Meteorite Failed DO/i })).toBeInTheDocument(),
      )
      await userEvent.click(screen.getByRole("button", { name: /Meteorite Failed DO/i }))
      await userEvent.click(screen.getByRole("checkbox"))
      await userEvent.click(screen.getByRole("button", { name: /Meteorite Failed DO/i }))
      await userEvent.click(screen.getByRole("button", { name: /Failed GET/i }))
      await userEvent.click(screen.getByRole("checkbox"))
      await userEvent.click(screen.getByRole("button", { name: "Retry (2)" }))
      await waitFor(() => expect(screen.getByText("2 jobs queued for retry")).toBeInTheDocument())
      expect(mockedApi).toHaveBeenCalledWith(
        "/api/jobs/bulk_state",
        expect.objectContaining({
          body: JSON.stringify({
            astral_job_ids: ["met-do-1"],
            to_state: "METEORITE_PASSED_JD",
          }),
        }),
      )
      expect(mockedApi).toHaveBeenCalledWith(
        "/api/jobs/bulk_state",
        expect.objectContaining({
          body: JSON.stringify({
            astral_job_ids: ["reg-get-1"],
            to_state: "PASSED_DO",
          }),
        }),
      )
    })
  })

  describe("AST-1410 silent refetch", () => {
    it("Retry refreshes the list without Loading...", async () => {
      installBaseApiMocks(mockedApi, jobsViewHandler("skipped", [failedJob]))
      renderWithProviders(<JobsSkipped />)
      await waitFor(() => expect(screen.getByRole("button", { name: /Failed LIKE/ })).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: /Failed LIKE/ }))
      await userEvent.click(screen.getByRole("checkbox"))
      const inner = mockedApi.getMockImplementation()!
      let release: (value: Response) => void = () => {}
      mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
        if (typeof url === "string" && url.includes("view=skipped") && !init?.method) {
          return new Promise<Response>((resolve) => { release = resolve })
        }
        return inner(url, init)
      })
      await userEvent.click(screen.getByRole("button", { name: "Retry (1)" }))
      expect(screen.getByText("Failed Role")).toBeInTheDocument()
      expect(screen.queryByText("Loading...")).not.toBeInTheDocument()
      release({ ok: true, json: async () => [] } as Response)
      await waitFor(() => expect(screen.getByText("No skipped jobs")).toBeInTheDocument())
    })
  })

})

describe("JobsSkipped — AST-1979 Created column", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  // Below-floor variant labels the neighbour "Updated"; regular failed variant labels it "Failed At".
  it.each([
    ["below-floor", floorJob, /Below dispatch score floor/, /^Updated/],
    ["regular", failedJob, /Failed LIKE/, /^Failed At/],
  ] as const)("%s table: Created left of its time column, shows created_at in candidate tz, sorts and toggles; default unchanged", async (_variant, base, section, updatedLabel) => {
    installBaseApiMocks(mockedApi, jobsViewHandler("skipped", createdColumnJobs(base)))
    installTzCandidate(mockedApi)
    renderWithProviders(<JobsSkipped />)
    await userEvent.click(await screen.findByRole("button", { name: section }))
    await expectCreatedColumn(screen.getByRole("table"), updatedLabel)
  })

  // AST-1982: the title cell renders inside the section loop, so each table variant gets the check.
  it.each([
    ["below-floor", floorJob, /Below dispatch score floor/],
    ["regular", failedJob, /Failed LIKE/],
  ] as const)("AST-1982 %s table: long title cut at 50 + … with portaled tooltip; 50-char title untouched", async (_variant, base, section) => {
    installBaseApiMocks(mockedApi, jobsViewHandler("skipped", jobTitleJobs(base)))
    renderWithProviders(<JobsSkipped />)
    await userEvent.click(await screen.findByRole("button", { name: section }))
    await expectJobTitleCells(screen.getByRole("table"))
  })
})

describe("JobsSkipped — AST-2106 grouped, collapsible Skipped page", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  const job = (id: string, state: string) => ({
    astral_job_id: id,
    job_title: `Role ${id}`,
    company: "Co",
    state,
    state_changed_at: "2026-01-01T00:00:00Z",
  })
  // Group heading buttons read "▼<label> (<count>)"; section buttons never use a bare group label.
  const GROUP_TEXT = /^\u25BC(Error|Bot block|Fail|Other) \(\d+\)$/
  const groupHeadings = () =>
    screen.queryAllByRole("button").map(b => b.textContent ?? "").filter(t => GROUP_TEXT.test(t)).map(t => t.slice(1))
  const groupBox = (heading: string) => {
    const btn = screen.getAllByRole("button").find(b => b.textContent === `\u25BC${heading}`)
    expect(btn, heading).toBeTruthy()
    return btn!.parentElement!
  }
  // Exactly these section buttons sit inside the group (sections collapsed, so no row-action buttons).
  const expectSectionsIn = (heading: string, sections: RegExp[]) => {
    const box = groupBox(heading)
    for (const name of sections) expect(within(box).getByRole("button", { name })).toBeInTheDocument()
    expect(within(box).getAllByRole("button")).toHaveLength(1 + sections.length)
  }
  const render = async (rows: unknown[]) => {
    installBaseApiMocks(mockedApi, jobsViewHandler("skipped", rows))
    renderWithProviders(<JobsSkipped />)
    await waitFor(() => expect(groupHeadings().length).toBeGreaterThan(0))
  }

  it("AC4: Error, Bot block, Fail headings in order with counts; each section under its own group; no Other", async () => {
    await render([
      job("e1", "ERROR_GRADE_DO"), job("b1", "BOT_BLOCKED_FETCH_JD"),
      job("f1", "FAILED_JD"), job("s1", "CANDIDATE_SKIPPED"),
    ])
    expect(groupHeadings()).toEqual(["Error (1)", "Bot block (1)", "Fail (2)"])
    expectSectionsIn("Error (1)", [/Failed Technical DO/])
    expectSectionsIn("Bot block (1)", [/BOT_BLOCKED_FETCH_JD/])
    expectSectionsIn("Fail (2)", [/Failed Job Description/, /CANDIDATE_SKIPPED/])
  })

  it("AC5: INVALID_TITLE adds Other (1) last", async () => {
    await render([
      job("e1", "ERROR_GRADE_DO"), job("b1", "BOT_BLOCKED_FETCH_JD"),
      job("f1", "FAILED_JD"), job("s1", "CANDIDATE_SKIPPED"), job("i1", "INVALID_TITLE"),
    ])
    expect(groupHeadings()).toEqual(["Error (1)", "Bot block (1)", "Fail (2)", "Other (1)"])
    expectSectionsIn("Other (1)", [/INVALID_TITLE/])
  })

  it("AC5: unmapped legacy ERROR_SOMETHING_OLD lands in Error, MYSTERY_STATE in Other (after Fail)", async () => {
    await render([job("x1", "ERROR_SOMETHING_OLD"), job("m1", "MYSTERY_STATE"), job("f1", "FAILED_JD")])
    expect(groupHeadings()).toEqual(["Error (1)", "Fail (1)", "Other (1)"])
    expectSectionsIn("Error (1)", [/ERROR SOMETHING OLD/])
    expectSectionsIn("Fail (1)", [/Failed Job Description/])
    expectSectionsIn("Other (1)", [/MYSTERY STATE/])
  })

  it("AC6: virtual_skip below-floor row renders under Fail, below Error", async () => {
    await render([floorJob, job("e1", "ERROR_GRADE_DO")])
    expect(groupHeadings()).toEqual(["Error (1)", "Fail (1)"])
    expectSectionsIn("Fail (1)", [/Below dispatch score floor/])
    expectSectionsIn("Error (1)", [/Failed Technical DO/])
  })

  it("AC7: group heading collapses its sections and restores them with section expand state intact", async () => {
    await render([job("f1", "FAILED_JD"), job("f2", "FAILED_DO"), job("e1", "ERROR_GRADE_DO")])
    await userEvent.click(screen.getByRole("button", { name: /Failed Job Description/ }))
    expect(screen.getByText("Role f1")).toBeInTheDocument()

    await userEvent.click(groupBox("Fail (2)").querySelector("button")!)
    expect(screen.queryByRole("button", { name: /Failed Job Description/ })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: /Failed DO/ })).not.toBeInTheDocument()
    expect(screen.queryByText("Role f1")).not.toBeInTheDocument()
    // Other groups untouched.
    expectSectionsIn("Error (1)", [/Failed Technical DO/])

    await userEvent.click(groupBox("Fail (2)").querySelector("button")!)
    // Re-expanded: the open section is still open, the closed one still closed.
    expect(screen.getByText("Role f1")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Failed DO/ })).toBeInTheDocument()
    expect(screen.queryByText("Role f2")).not.toBeInTheDocument()
  })

  it("AC8: only a FAILED_JD job renders only the Fail heading", async () => {
    await render([job("f1", "FAILED_JD")])
    expect(groupHeadings()).toEqual(["Fail (1)"])
  })

  it("AC8: no skipped jobs shows the empty-state text and no group heading", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("skipped", []))
    renderWithProviders(<JobsSkipped />)
    await waitFor(() => expect(screen.getByText("No skipped jobs")).toBeInTheDocument())
    expect(groupHeadings()).toEqual([])
  })

  it("AC9: mixed Error + FAILED_DO selection posts one bulk_state per distinct retry target", async () => {
    await render([job("e1", "ERROR_EVALUATE_JD"), job("d1", "FAILED_DO")])
    await userEvent.click(screen.getByRole("button", { name: /ERROR_EVALUATE_JD/ }))
    await userEvent.click(screen.getByRole("checkbox"))
    await userEvent.click(screen.getByRole("button", { name: /Failed DO/ }))
    await userEvent.click(screen.getByRole("checkbox"))
    await userEvent.click(screen.getByRole("button", { name: "Retry (2)" }))
    await waitFor(() => expect(screen.getByText("2 jobs queued for retry")).toBeInTheDocument())
    const posts = mockedApi.mock.calls.filter(([url]) => url === "/api/jobs/bulk_state").map(([, init]) => init?.body)
    expect(posts).toEqual(expect.arrayContaining([
      JSON.stringify({ astral_job_ids: ["e1"], to_state: "JD_READY" }),
      JSON.stringify({ astral_job_ids: ["d1"], to_state: "PASSED_JD" }),
    ]))
    expect(posts).toHaveLength(2)
  })
})
