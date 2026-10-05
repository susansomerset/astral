import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import JobsProcessing from "../../../../src/ui/frontend/src/pages/JobsProcessing"
import { renderWithProviders } from "../test-utils"
import { createdColumnJobs, expectCreatedColumn, installTzCandidate } from "./created-column"
import { expectJobTitleCells, jobTitleJobs } from "./job-title-cell"
import { installBaseApiMocks, jobsViewHandler } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const jobs = [
  {
    astral_job_id: "j1",
    job_title: "Alpha Role",
    company: "Acme",
    state: "PASSED_JOBLIST",
    state_changed_at: "2026-01-02T00:00:00Z",
    latest_score: 0.88,
    joblist_grades: [{ vector: "Job List (JL)", grade: "A", confidence: 0.8 }],
  },
  {
    astral_job_id: "j2",
    job_title: "Beta Role",
    company: "Beta",
    state: "JD_READY",
    state_changed_at: "2026-01-01T00:00:00Z",
    latest_score: null,
    jd_grades: { JD: "B" },
  },
]

describe("JobsProcessing", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("expands sections, sorts columns, and opens job details", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("processing", jobs))
    renderWithProviders(<JobsProcessing />)
    await waitFor(() => expect(screen.getByText(/Passed Job List/)).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: /Passed Job List/ }))
    await userEvent.click(screen.getByRole("columnheader", { name: /Job Title/ }))
    await userEvent.click(screen.getByRole("columnheader", { name: /Score/ }))
    await userEvent.click(screen.getByText("Alpha Role"))
    await waitFor(() => expect(mockedApi).toHaveBeenCalledWith("/api/jobs/j1"))
    await userEvent.click(screen.getByRole("button", { name: /Passed Job List/ }))
    await userEvent.click(screen.getByRole("button", { name: /JD Ready/ }))
    await userEvent.click(screen.getByRole("columnheader", { name: /JD/ }))
    await userEvent.click(screen.getByText("Beta Role"))
  })

  it("shows empty when jobs response is invalid", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("processing", { bad: true } as unknown as typeof jobs))
    renderWithProviders(<JobsProcessing />)
    await waitFor(() => expect(screen.getByText("No jobs processing")).toBeInTheDocument())
  })

  // AST-1975: Processing replaces In Review; title, view key, and artifact-build jobs land here.
  it("titled Processing; fetches view=processing; BUILD_ARTIFACTS jobs get a Building Artifacts section", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("processing", [{
      astral_job_id: "j-build",
      job_title: "Build Role",
      company: "BuildCo",
      state: "BUILD_ARTIFACTS",
      state_changed_at: "2026-01-01T00:00:00Z",
    }]))
    renderWithProviders(<JobsProcessing />)
    await waitFor(() => expect(screen.getByRole("button", { name: /Building Artifacts \(1\)/ })).toBeInTheDocument())
    expect(screen.getByRole("heading", { level: 1, name: "Processing" })).toBeInTheDocument()
    expect(mockedApi.mock.calls.some(([url]) => String(url).startsWith("/api/jobs?view=processing&"))).toBe(true)
    expect(mockedApi.mock.calls.some(([url]) => String(url).includes("view=in_review"))).toBe(false)
    await userEvent.click(screen.getByRole("button", { name: /Building Artifacts/ }))
    await userEvent.click(screen.getByText("Build Role"))
    await waitFor(() => expect(mockedApi).toHaveBeenCalledWith("/api/jobs/j-build"))
  })

  it("shows a legacy section for unmapped processing state", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("processing", [{
      astral_job_id: "j-legacy",
      job_title: "Legacy Role",
      company: "OldCo",
      state: "RETIRED_EXAMPLE_STATE",
      state_changed_at: "2026-01-01T00:00:00Z",
    }]))
    renderWithProviders(<JobsProcessing />)
    await waitFor(() => expect(screen.getByText(/RETIRED EXAMPLE STATE.*legacy/i)).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: /RETIRED EXAMPLE STATE.*legacy/i }))
    expect(screen.getByText("Legacy Role")).toBeInTheDocument()
  })

  describe("AST-893 Expand One default", () => {
    it("opening a second section closes the first; no Expand all chrome", async () => {
      installBaseApiMocks(mockedApi, jobsViewHandler("processing", jobs))
      renderWithProviders(<JobsProcessing />)
      await waitFor(() => expect(screen.getByText(/Passed Job List/)).toBeInTheDocument())
      expect(screen.queryByRole("button", { name: "Expand all" })).not.toBeInTheDocument()
      expect(screen.queryByRole("button", { name: "Collapse all" })).not.toBeInTheDocument()

      await userEvent.click(screen.getByRole("button", { name: /Passed Job List/ }))
      expect(screen.getByText("Alpha Role")).toBeInTheDocument()

      await userEvent.click(screen.getByRole("button", { name: /JD Ready/ }))
      expect(screen.getByText("Beta Role")).toBeInTheDocument()
      expect(screen.queryByText("Alpha Role")).not.toBeInTheDocument()
    })
  })

  describe("AST-1064 group-by job-carried rubric", () => {
    it("splits Passed Job List into tables by joblist_rubric fingerprint", async () => {
      const narrow = [{ code: "JL", label: "Job List", importance: 5, grade_descriptions: [] }]
      const wide = [
        { code: "JL", label: "Job List", importance: 5, grade_descriptions: [] },
        { code: "TT", label: "Title Match", importance: 4, grade_descriptions: [] },
      ]
      const grouped = [
        {
          astral_job_id: "g1",
          job_title: "Group Narrow",
          company: "Acme",
          state: "PASSED_JOBLIST",
          state_changed_at: "2026-01-03T00:00:00Z",
          joblist_rubric: narrow,
          joblist_grades: [{ vector: "Job List", grade: "A", confidence: 0.8 }],
          joblist_score: 7.1,
          latest_score: 0.1,
        },
        {
          astral_job_id: "g2",
          job_title: "Group Wide",
          company: "Beta",
          state: "PASSED_JOBLIST",
          state_changed_at: "2026-01-02T00:00:00Z",
          joblist_rubric: wide,
          joblist_grades: [
            { vector: "Job List", grade: "B", confidence: 0.5 },
            { vector: "Title Match", grade: "A", confidence: 0.9 },
          ],
          joblist_score: 8.2,
          latest_score: 0.2,
        },
      ]
      installBaseApiMocks(mockedApi, jobsViewHandler("processing", grouped))
      renderWithProviders(<JobsProcessing />)
      await waitFor(() => expect(screen.getByText(/Passed Job List/)).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: /Passed Job List/ }))
      expect(document.querySelectorAll(".list-page-table").length).toBeGreaterThanOrEqual(2)
      expect(screen.getByRole("columnheader", { name: "TT" })).toBeInTheDocument()
      expect(screen.getAllByRole("columnheader", { name: "JL" }).length).toBeGreaterThanOrEqual(2)
      expect(screen.getByText("Group Narrow")).toBeInTheDocument()
      expect(screen.getByText("Group Wide")).toBeInTheDocument()
      expect(screen.getByText("7.10")).toBeInTheDocument()
      expect(screen.getByText("8.20")).toBeInTheDocument()
      expect(document.querySelectorAll(".grade-dot").length).toBeGreaterThanOrEqual(3)
    })
  })

  describe("AST-1086 compact headers and grade-dot tooltips", () => {
    it("grades-only Passed Job List shows compact JL header with full-name title", async () => {
      installBaseApiMocks(mockedApi, jobsViewHandler("processing", [jobs[0]]))
      renderWithProviders(<JobsProcessing />)
      await waitFor(() => expect(screen.getByText(/Passed Job List/)).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: /Passed Job List/ }))
      const th = screen.getByRole("columnheader", { name: "JL" })
      expect(th).toHaveAttribute("title", "Job List (5)")
      expect(th.textContent).toMatch(/^JL/)
      expect(screen.queryByRole("columnheader", { name: /Job List \(JL\)/ })).not.toBeInTheDocument()
    })

    it("grade-dot title includes reason and confidence parenthetical", async () => {
      const tipJob = {
        astral_job_id: "tip-ir",
        job_title: "Tooltip Processing",
        company: "TipCo",
        state: "PASSED_JOBLIST",
        state_changed_at: "2026-01-06T00:00:00Z",
        joblist_grades: [{
          vector: "Job List (JL)",
          grade: "A",
          confidence: 5,
          reason: "Clear joblist fit",
        }],
      }
      installBaseApiMocks(mockedApi, jobsViewHandler("processing", [tipJob]))
      renderWithProviders(<JobsProcessing />)
      await waitFor(() => expect(screen.getByText(/Passed Job List/)).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: /Passed Job List/ }))
      const dot = document.querySelector(".grade-dot.dot-a")
      expect(dot).toBeTruthy()
      expect(dot?.getAttribute("title")).toBe(
        "Clear joblist fit (The source explicitly states it.)",
      )
    })
  })

  describe("AST-1410 silent refetch", () => {
    it("closing the job modal refreshes the list without Loading...", async () => {
      installBaseApiMocks(mockedApi, jobsViewHandler("processing", jobs))
      renderWithProviders(<JobsProcessing />)
      await waitFor(() => expect(screen.getByText(/Passed Job List/)).toBeInTheDocument())
      await userEvent.click(screen.getByRole("button", { name: /Passed Job List/ }))
      await userEvent.click(screen.getByText("Alpha Role"))
      await waitFor(() => expect(mockedApi).toHaveBeenCalledWith("/api/jobs/j1"))
      const inner = mockedApi.getMockImplementation()!
      let release: (value: Response) => void = () => {}
      mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
        if (typeof url === "string" && url.includes("view=processing") && !init?.method) {
          return new Promise<Response>((resolve) => { release = resolve })
        }
        return inner(url, init)
      })
      await userEvent.click(screen.getByRole("button", { name: "Close" }))
      expect(screen.getByText("Alpha Role")).toBeInTheDocument()
      expect(screen.queryByText("Loading...")).not.toBeInTheDocument()
      release({ ok: true, json: async () => jobs } as Response)
      await waitFor(() => expect(screen.getByText("Alpha Role")).toBeInTheDocument())
    })
  })
})

describe("JobsProcessing — AST-1979 Created column", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("Created left of Updated, shows created_at in candidate tz, sorts and toggles; default unchanged", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("processing", createdColumnJobs(jobs[0])))
    installTzCandidate(mockedApi)
    renderWithProviders(<JobsProcessing />)
    await userEvent.click(await screen.findByRole("button", { name: /Passed Job List/ }))
    await expectCreatedColumn(screen.getByRole("table"), /^Updated/)
  })

  it("AST-1982: long title cut at 50 + … with portaled full-title tooltip; 50-char title untouched", async () => {
    installBaseApiMocks(mockedApi, jobsViewHandler("processing", jobTitleJobs(jobs[0])))
    renderWithProviders(<JobsProcessing />)
    await userEvent.click(await screen.findByRole("button", { name: /Passed Job List/ }))
    await expectJobTitleCells(screen.getByRole("table"))
  })
})
