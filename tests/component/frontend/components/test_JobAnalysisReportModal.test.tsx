import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import JobAnalysisReportModal from "../../../../src/ui/frontend/src/components/JobAnalysisReportModal"
import { baseCandidate, installBaseApiMocks, jsonResponse } from "../pages/page-mocks"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

function fullUpshot() {
  return {
    take_get: "GET phase thought",
    take_do: "DO phase thought",
    take_like: "LIKE phase thought",
    take_jd: "JD phase thought",
    whole_jd_upshot: "Strong thematic fit.",
    segment_upshots: [],
    candidate_questions: [{ text: "What is the team size?" }],
    caveats: [{ text: "Remote only" }],
  }
}

function jobHandler(
  jobId: string,
  overrides: Record<string, unknown> = {},
): (url: string, init?: RequestInit) => Promise<Response> | Response | undefined {
  return (url, init) => {
    if (url === `/api/jobs/${jobId}` && !init) {
      return jsonResponse({
        astral_job_id: jobId,
        job_title: "Analyst",
        company: "Globex",
        state: "RECOMMENDED",
        state_changed_at: "2026-01-03T00:00:00Z",
        job_link: "https://jobs.example/apply",
        job_data: {
          job_description: "Full JD body text",
          analysis_upshot: fullUpshot(),
          jd_grades: [{ vector: "JD", grade: "A", reason: "Strong match" }],
        },
        ...overrides,
      })
    }
    if (url === "/api/companies/Globex") {
      return jsonResponse({ company_website: "https://globex.example" })
    }
    if (url === `/api/candidates/${baseCandidate.astral_candidate_id}/resume_structure`) {
      return jsonResponse({
        sections: [{ id: "professional_summary", label: "Summary" }],
        accent_color: null,
      })
    }
    return undefined
  }
}

async function waitForShell() {
  await waitFor(() => expect(document.querySelector(".recommended-report-tabs")).toBeTruthy())
}

function topTabBar() {
  return document.querySelector(".recommended-report-tabs") as HTMLElement
}

describe("JobAnalysisReportModal — AST-948 horizontal shell", () => {
  beforeEach(() => mockedApi.mockReset())

  it("renders Summary / Analysis / Artifacts horizontal tabs with Summary default", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j948"))
    renderWithProviders(<JobAnalysisReportModal jobId="j948" onClose={() => {}} />)
    await waitForShell()
    const bar = topTabBar()
    expect(within(bar).getByRole("button", { name: "Summary" })).toHaveClass("active")
    expect(within(bar).getByRole("button", { name: "Analysis" })).toBeInTheDocument()
    expect(within(bar).getByRole("button", { name: "Artifacts" })).toBeInTheDocument()
    expect(document.querySelector(".side-tab-list")).toBeNull()
    // Summary section chrome (bodies filled by AST-949)
    expect(screen.getByText("Job Summary")).toBeInTheDocument()
    expect(screen.getByText("Company Upshot")).toBeInTheDocument()
    expect(screen.getByText("Noteworthy Caveats")).toBeInTheDocument()
    expect(screen.getByText("Questions to Ask")).toBeInTheDocument()
    expect(screen.getByText("Raw Job Description")).toBeInTheDocument()
  })

  it("shows Analysis section chrome with JD Analysis expanded by default", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j948"))
    renderWithProviders(<JobAnalysisReportModal jobId="j948" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Analysis" }))
    expect(screen.getByText("JD Analysis")).toBeInTheDocument()
    expect(screen.getByText("DO Analysis")).toBeInTheDocument()
    expect(screen.getByText("GET Analysis")).toBeInTheDocument()
    expect(screen.getByText("LIKE Analysis")).toBeInTheDocument()
    // JD default expanded → Collapse control present; others start collapsed
    const collapses = screen.getAllByRole("button", { name: "Collapse section" })
    expect(collapses.length).toBe(1)
    expect(screen.getAllByRole("button", { name: "Expand section" }).length).toBe(3)
  })

  it("shows Artifacts section chrome and parks Generate on the leading strip", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j948/generate_artifacts" && init?.method === "POST") {
        return jsonResponse({ ok: true, state: "BUILD_ARTIFACTS" })
      }
      return jobHandler("j948")(url, init)
    })
    const onClose = vi.fn()
    renderWithProviders(<JobAnalysisReportModal jobId="j948" onClose={onClose} />)
    await waitForShell()
    expect(screen.queryByRole("button", { name: "Generate Artifacts" })).not.toBeInTheDocument()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Artifacts" }))
    expect(screen.getByText("Job Resume")).toBeInTheDocument()
    expect(screen.getByText("Cover Letter")).toBeInTheDocument()
    expect(screen.getByText("Application Questions")).toBeInTheDocument()
    const btn = await screen.findByRole("button", { name: "Generate Artifacts" })
    await userEvent.click(btn)
    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith("/api/jobs/j948/generate_artifacts", { method: "POST" }),
    )
    await waitFor(() => expect(onClose).toHaveBeenCalled())
  })

  it("AST-645: Generate Artifacts uses in-flight class while Working", async () => {
    let resolveGenerate!: (value: Response) => void
    const generatePromise = new Promise<Response>((resolve) => {
      resolveGenerate = resolve
    })
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j948/generate_artifacts" && init?.method === "POST") {
        return generatePromise
      }
      return jobHandler("j948")(url, init)
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j948" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Artifacts" }))
    const btn = await screen.findByRole("button", { name: "Generate Artifacts" })
    expect(btn).not.toHaveClass("in-flight")
    await userEvent.click(btn)
    await waitFor(() => expect(btn).toHaveClass("in-flight"))
    expect(btn).toHaveTextContent("Working…")
    resolveGenerate(jsonResponse({ ok: true, state: "BUILD_ARTIFACTS" }))
    await waitFor(() => expect(btn).not.toHaveClass("in-flight"))
  })

  it("sticky header: deeplinked title + company, copy controls, no Apply button", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j948"))
    renderWithProviders(<JobAnalysisReportModal jobId="j948" onClose={() => {}} />)
    await waitForShell()
    expect(screen.getByRole("link", { name: "Analyst" })).toHaveAttribute("href", "https://jobs.example/apply")
    expect(screen.getByRole("link", { name: "Globex" })).toHaveAttribute("href", "https://globex.example")
    expect(screen.getByRole("button", { name: "Copy Application Email" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Copy LinkedIn Profile" })).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Apply" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Preview Materials" })).not.toBeInTheDocument()
    // Modal title is company only — job title lives in sticky header
    expect(screen.getByRole("heading", { name: "Globex" })).toHaveClass("modal-title")
  })

  it("Print Resume / Print Cover Letter open AST-605 HTML routes when artifacts exist", async () => {
    const openSpy = vi.spyOn(window, "open").mockImplementation(() => null)
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j-print" && !init) {
        return jsonResponse({
          astral_job_id: "j-print",
          job_title: "Role",
          company: "Co",
          state: "CANDIDATE_REVIEW",
          state_changed_at: null,
          job_link: "https://jobs.example/apply",
          job_data: {
            job_description: "JD",
            analysis_upshot: fullUpshot(),
            artifacts: {
              resume_content: { professional_summary: "Draft" },
              cover_letter: { Letter: "Hello" },
            },
          },
        })
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j-print" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(screen.getByRole("button", { name: "Print Resume" }))
    expect(openSpy).toHaveBeenCalledWith("/candidate/resume/j-print", "_blank", "noopener,noreferrer")
    await userEvent.click(screen.getByRole("button", { name: "Print Cover Letter" }))
    expect(openSpy).toHaveBeenCalledWith("/candidate/cover/j-print", "_blank", "noopener,noreferrer")
    openSpy.mockRestore()
  })

  it("hides print buttons when artifacts are empty", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j948"))
    renderWithProviders(<JobAnalysisReportModal jobId="j948" onClose={() => {}} />)
    await waitForShell()
    expect(screen.queryByRole("button", { name: "Print Resume" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Print Cover Letter" })).not.toBeInTheDocument()
  })

  it("job title deeplink replaces Apply for CANDIDATE_REVIEW", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j-ready", { state: "CANDIDATE_REVIEW" }))
    renderWithProviders(<JobAnalysisReportModal jobId="j-ready" onClose={() => {}} />)
    await waitForShell()
    expect(screen.getByRole("link", { name: "Analyst" })).toHaveAttribute("href", "https://jobs.example/apply")
    expect(screen.queryByRole("button", { name: "Apply" })).not.toBeInTheDocument()
    // Apply filtered from Artifacts strip — no primary actions left on CANDIDATE_REVIEW
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Artifacts" }))
    expect(screen.queryByRole("button", { name: "Generate Artifacts" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Apply" })).not.toBeInTheDocument()
  })

  it("renders shell without crashing when analysis_upshot is absent", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j-empty" && !init) {
        return jsonResponse({
          astral_job_id: "j-empty",
          job_title: "X",
          company: "Co",
          state: "RECOMMENDED",
          state_changed_at: null,
          job_data: { job_description: "txt" },
        })
      }
      if (url === "/api/companies/Co") {
        return jsonResponse({ company_website: null })
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j-empty" onClose={() => {}} />)
    await waitForShell()
    // Shell chrome only — empty-state copy is AST-949 (sibling; may be absent on this tip)
    expect(screen.getByText("Job Summary")).toBeInTheDocument()
    expect(screen.queryByText("No analysis upshot on file.")).not.toBeInTheDocument()
  })

  it("shows Cancel on Artifacts strip for BUILD_ARTIFACTS", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j-build", { state: "BUILD_ARTIFACTS" }))
    renderWithProviders(<JobAnalysisReportModal jobId="j-build" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Artifacts" }))
    const strip = document.querySelector(".recommended-report-artifacts-actions") as HTMLElement
    expect(within(strip).getByRole("button", { name: "Cancel" })).toBeInTheDocument()
  })
})

describe("JobAnalysisReportModal — AST-949 Summary tab sections", () => {
  beforeEach(() => mockedApi.mockReset())

  function companyWithNotes(url: string, init?: RequestInit) {
    if (url === "/api/companies/Globex") {
      return jsonResponse({
        company_website: "https://globex.example",
        prefilter_company_notes: "Steady growth, remote-friendly.",
      })
    }
    return jobHandler("j949")(url, init)
  }

  it("fills Summary section bodies from upshot, company notes, and JD", async () => {
    installBaseApiMocks(mockedApi, companyWithNotes)
    renderWithProviders(<JobAnalysisReportModal jobId="j949" onClose={() => {}} />)
    await waitForShell()
    expect(await screen.findByText("Strong thematic fit.")).toBeInTheDocument()
    expect(await screen.findByText("Steady growth, remote-friendly.")).toBeInTheDocument()
    expect(screen.getByText("Remote only")).toBeInTheDocument()
    expect(screen.getByText("What is the team size?")).toBeInTheDocument()
    // Raw JD starts collapsed — expand to read body
    expect(screen.queryByText("Full JD body text")).not.toBeVisible()
    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    expect(screen.getByText("Full JD body text")).toBeVisible()
  })

  it("content-aware expand: Raw JD collapsed; populated sections open", async () => {
    installBaseApiMocks(mockedApi, companyWithNotes)
    renderWithProviders(<JobAnalysisReportModal jobId="j949" onClose={() => {}} />)
    await waitForShell()
    await waitFor(() => expect(screen.getByText("Steady growth, remote-friendly.")).toBeInTheDocument())
    // job_summary + company + caveats + questions expanded; raw_jd collapsed
    expect(screen.getAllByRole("button", { name: "Collapse section" }).length).toBe(4)
    expect(screen.getAllByRole("button", { name: "Expand section" }).length).toBe(1)
  })

  it("shows empty-state copy when upshot and company notes are missing", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j949-empty" && !init) {
        return jsonResponse({
          astral_job_id: "j949-empty",
          job_title: "X",
          company: "Co",
          state: "RECOMMENDED",
          state_changed_at: null,
          job_data: {},
        })
      }
      if (url === "/api/companies/Co") {
        return jsonResponse({ company_website: null, prefilter_company_notes: "   " })
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j949-empty" onClose={() => {}} />)
    await waitForShell()
    expect(await screen.findByText("No job summary on file.")).toBeInTheDocument()
    // company / caveats / questions / raw_jd start collapsed when empty — expand to read copy
    const expands = screen.getAllByRole("button", { name: "Expand section" })
    expect(expands.length).toBe(4)
    await userEvent.click(expands[0])
    expect(screen.getByText("No company upshot on file.")).toBeVisible()
    await userEvent.click(expands[1])
    expect(screen.getByText("No noteworthy caveats on file.")).toBeVisible()
    await userEvent.click(expands[2])
    expect(screen.getByText("No questions to ask on file.")).toBeVisible()
    await userEvent.click(expands[3])
    expect(screen.getByText("No job description on file.")).toBeVisible()
  })

  it("company notes come from company API, not job_data", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j949-notes" && !init) {
        return jsonResponse({
          astral_job_id: "j949-notes",
          job_title: "Analyst",
          company: "Globex",
          state: "RECOMMENDED",
          state_changed_at: null,
          job_link: "https://jobs.example/apply",
          job_data: {
            job_description: "JD",
            analysis_upshot: fullUpshot(),
            // decoy — must not be used
            prefilter_company_notes: "FROM_JOB_DATA",
          },
        })
      }
      if (url === "/api/companies/Globex") {
        return jsonResponse({
          company_website: "https://globex.example",
          prefilter_company_notes: "FROM_COMPANY_API",
        })
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j949-notes" onClose={() => {}} />)
    await waitForShell()
    expect(await screen.findByText("FROM_COMPANY_API")).toBeInTheDocument()
    expect(screen.queryByText("FROM_JOB_DATA")).not.toBeInTheDocument()
  })
})

describe("JobAnalysisReportModal — AST-950 Analysis tab grades and confidence", () => {
  beforeEach(() => mockedApi.mockReset())

  function analysisJobHandler(jobId: string) {
    return (url: string, init?: RequestInit) => {
      if (url === `/api/jobs/${jobId}` && !init) {
        return jsonResponse({
          astral_job_id: jobId,
          job_title: "Analyst",
          company: "Globex",
          state: "RECOMMENDED",
          state_changed_at: "2026-01-03T00:00:00Z",
          job_link: "https://jobs.example/apply",
          job_data: {
            job_description: "Full JD body text",
            analysis_upshot: fullUpshot(),
            jd_grades: [
              { vector: "JD", grade: "A", reason: "Strong match", confidence: 4 },
            ],
            do_grades: [
              { vector: "TE", grade: "B", reason: "Solid skills", confidence: 3 },
            ],
          },
        })
      }
      if (url === "/api/companies/Globex") {
        return jsonResponse({ company_website: "https://globex.example" })
      }
      return undefined
    }
  }

  it("shows JD/DO/GET/LIKE only with JD expanded by default (no Overview)", async () => {
    installBaseApiMocks(mockedApi, analysisJobHandler("j950"))
    renderWithProviders(<JobAnalysisReportModal jobId="j950" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Analysis" }))
    expect(screen.getByText("JD Analysis")).toBeInTheDocument()
    expect(screen.getByText("DO Analysis")).toBeInTheDocument()
    expect(screen.getByText("GET Analysis")).toBeInTheDocument()
    expect(screen.getByText("LIKE Analysis")).toBeInTheDocument()
    expect(screen.queryByText("Overview")).not.toBeInTheDocument()
    expect(screen.getAllByRole("button", { name: "Collapse section" }).length).toBe(1)
    expect(screen.getAllByRole("button", { name: "Expand section" }).length).toBe(3)
  })

  it("header grade+confidence row visible when JD collapsed; take_* above rubric when expanded", async () => {
    installBaseApiMocks(mockedApi, analysisJobHandler("j950"))
    renderWithProviders(<JobAnalysisReportModal jobId="j950" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Analysis" }))

    // JD expanded: Estelle take above AgentAnalysisHeader
    expect(await screen.findByText("JD phase thought")).toBeVisible()
    expect(screen.getByText("Strong match")).toBeVisible()
    expect(document.querySelector(".recommended-report-phase-grade-row")).toBeTruthy()
    expect(
      document.querySelectorAll(".recommended-report-phase-grade-cell .confidence-bullets").length,
    ).toBeGreaterThan(0)

    // Collapse JD — header metadata (grade+confidence) stays; body take/reason hide
    await userEvent.click(screen.getByRole("button", { name: "Collapse section" }))
    expect(screen.getByText("JD phase thought")).not.toBeVisible()
    expect(document.querySelector(".recommended-report-phase-grade-row")).toBeTruthy()
    expect(
      document.querySelector(".recommended-report-phase-grade-cell .grade-dot.dot-a"),
    ).toBeTruthy()
  })

  it("expanded DO shows take_do above consult grades", async () => {
    installBaseApiMocks(mockedApi, analysisJobHandler("j950"))
    renderWithProviders(<JobAnalysisReportModal jobId="j950" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Analysis" }))
    const expands = screen.getAllByRole("button", { name: "Expand section" })
    // DO is first collapsed section after JD
    await userEvent.click(expands[0])
    expect(await screen.findByText("DO phase thought")).toBeVisible()
    expect(screen.getByText("Solid skills")).toBeVisible()
  })

  it("empty grades show consult empty copy; missing upshot does not crash", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j950-empty" && !init) {
        return jsonResponse({
          astral_job_id: "j950-empty",
          job_title: "X",
          company: "Co",
          state: "RECOMMENDED",
          state_changed_at: null,
          job_data: { job_description: "txt" },
        })
      }
      if (url === "/api/companies/Co") {
        return jsonResponse({ company_website: null })
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j950-empty" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Analysis" }))
    expect(screen.getByText("JD Analysis")).toBeInTheDocument()
    const jdPanel = document.querySelector(".collapsible-panel.is-expanded") as HTMLElement
    expect(jdPanel).toBeTruthy()
    expect(within(jdPanel).getByText("No consult detail on file.")).toBeVisible()
    expect(document.querySelector(".recommended-report-phase-grade-row")).toBeNull()
  })
})
