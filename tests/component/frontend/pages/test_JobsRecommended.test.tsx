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
    await userEvent.click(companyHeader)
    const rowsAsc = within(recSection).getAllByRole("row").slice(1).map(r => r.textContent ?? "")
    expect(rowsAsc[0]).toContain("Acme")
    expect(rowsAsc[1]).toContain("Zulu")
    await userEvent.click(companyHeader)
    const rowsDesc = within(recSection).getAllByRole("row").slice(1).map(r => r.textContent ?? "")
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
    expect(within(bar).getByRole("button", { name: "Summary" })).toHaveClass("active")
    expect(screen.getByText("Job Summary")).toBeInTheDocument()
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
})
