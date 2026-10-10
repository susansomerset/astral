import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import { copyJobSnapshotToClipboard } from "../../../../src/ui/frontend/src/lib/copyJobSnapshot"
import JobAnalysisReportModal from "../../../../src/ui/frontend/src/components/JobAnalysisReportModal"
import { STATE_UI_MANIFEST_FIXTURE } from "../fixtures/stateUiManifestFixture"
import { baseCandidate, installBaseApiMocks, jsonResponse } from "../pages/page-mocks"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

vi.mock("../../../../src/ui/frontend/src/lib/copyJobSnapshot", () => ({
  copyJobSnapshotToClipboard: vi.fn(),
}))

const mockedApi = vi.mocked(api)
const mockedCopy = vi.mocked(copyJobSnapshotToClipboard)

beforeEach(() => {
  mockedCopy.mockReset()
  mockedCopy.mockResolvedValue(true)
})

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
        // AST-1695: title/Apply navigate via listing_href (not raw job_link)
        listing_href: "https://jobs.example/apply",
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

// AST-1874: Analysis opens by default; Summary-pane tests select Summary explicitly.
async function openSummaryTab() {
  await userEvent.click(within(topTabBar()).getByRole("button", { name: "Summary" }))
}

describe("JobAnalysisReportModal — AST-948 horizontal shell", () => {
  beforeEach(() => mockedApi.mockReset())

  it("renders Analysis / Summary / Artifacts / Discussion horizontal tabs with Analysis default (AST-1874)", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j948"))
    renderWithProviders(<JobAnalysisReportModal jobId="j948" onClose={() => {}} />)
    await waitForShell()
    const bar = topTabBar()
    // Default tab is picked by an effect after the tab bar paints — wait for it.
    await waitFor(() => expect(within(bar).getByRole("button", { name: "Analysis" })).toHaveClass("active"))
    // AST-1551 / AST-1692: Discussion follows Artifacts; Meteorite filtered when related_meteorite null
    expect(within(bar).getAllByRole("button").map(t => t.textContent)).toEqual([
      "Analysis", "Summary", "Artifacts", "Discussion",
    ])
    expect(screen.getByText("JD Analysis")).toBeInTheDocument()
    expect(document.querySelector(".side-tab-list")).toBeNull()
    // Summary section chrome (bodies filled by AST-949)
    await openSummaryTab()
    expect(screen.getByText("Job Summary")).toBeInTheDocument()
    expect(screen.getByText("Company Upshot")).toBeInTheDocument()
    expect(screen.getByText("Noteworthy Caveats")).toBeInTheDocument()
    expect(screen.getByText("Questions to Ask")).toBeInTheDocument()
    expect(screen.getByText("Raw Job Description")).toBeInTheDocument()
  })

  it("shows Analysis section chrome with all phases collapsed by default", async () => {
    // AST-1327/1328: Analysis collapse-all (was JD-expanded under AST-948).
    installBaseApiMocks(mockedApi, jobHandler("j948"))
    renderWithProviders(<JobAnalysisReportModal jobId="j948" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Analysis" }))
    expect(screen.getByText("JD Analysis")).toBeInTheDocument()
    expect(screen.getByText("DO Analysis")).toBeInTheDocument()
    expect(screen.getByText("GET Analysis")).toBeInTheDocument()
    expect(screen.getByText("LIKE Analysis")).toBeInTheDocument()
    expect(screen.queryAllByRole("button", { name: "Collapse section" }).length).toBe(0)
    expect(screen.getAllByRole("button", { name: "Expand section" }).length).toBe(4)
  })
  it("empty Artifacts tab shows Generate only (no section chrome)", async () => {
    // AST-951 supersedes AST-948 always-on empty section chrome for Artifacts.
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
    expect(screen.queryByText("Job Resume")).not.toBeInTheDocument()
    expect(screen.queryByText("Cover Letter")).not.toBeInTheDocument()
    expect(screen.queryByText("Application Questions")).not.toBeInTheDocument()
    // AST-2084 AC4: nothing generated → no thumbnails and no print fetches.
    expect(document.querySelector(".print-preview-thumb")).toBeNull()
    expect(mockedApi.mock.calls.some(([u]) => String(u).startsWith("/candidate/"))).toBe(false)
    const btn = await screen.findByRole("button", { name: "Generate Artifacts" })
    await userEvent.click(btn)
    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith("/api/jobs/j948/generate_artifacts", { method: "POST" }),
    )
    await waitFor(() => expect(onClose).toHaveBeenCalled())
  })

  it("AST-645: Generate Artifacts uses in-flight class while request pending", async () => {
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
    expect(btn).toHaveClass("btn")
    expect(btn).toHaveClass("primary")
    expect(btn).not.toHaveClass("in-flight")
    await userEvent.click(btn)
    await waitFor(() => expect(btn).toHaveClass("in-flight"))
    // AST-951: busy label stays Generate Artifacts until close; Generating… is in-progress chrome
    expect(btn).toHaveTextContent("Generate Artifacts")
    resolveGenerate(jsonResponse({ ok: true, state: "BUILD_ARTIFACTS" }))
    await waitFor(() => expect(btn).not.toHaveClass("in-flight"))
  })

  it("sticky header: plain title + listing line + company link, copy controls, no Apply button", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j948"))
    renderWithProviders(<JobAnalysisReportModal jobId="j948" onClose={() => {}} />)
    await waitForShell()
    expect(screen.queryByRole("link", { name: "Analyst" })).not.toBeInTheDocument()
    expect(screen.getByRole("link", { name: "https://jobs.example/apply" })).toHaveAttribute("href", "https://jobs.example/apply")
    expect(screen.getByRole("link", { name: "Globex" })).toHaveAttribute("href", "https://globex.example")
    expect(screen.getByRole("button", { name: "Copy Application Email" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Copy LinkedIn Profile" })).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Apply" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Preview Materials" })).not.toBeInTheDocument()
    // Modal title is company only — job title lives in sticky header
    expect(screen.getByRole("heading", { name: "Globex" })).toHaveClass("modal-title")
  })

  it("AST-1546: Print Resume success — two-arg open, opener null, no popup-blocked toast; Cover still noopener (AST-1350)", async () => {
    // Bug-repro: success must not toast popup-blocked; blob open has no features string (AST-1545).
    const fakeWin = { opener: {} as Window | null }
    const openSpy = vi.spyOn(window, "open").mockImplementation(() => fakeWin as unknown as Window)
    const createSpy = vi.fn(() => "blob:jar-resume-html")
    const revokeSpy = vi.fn()
    vi.stubGlobal("URL", { createObjectURL: createSpy, revokeObjectURL: revokeSpy })
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
              // AST-1593: Print Resume shows for the hydrated job_resume leaf only.
              job_resume: { professional_summary: "Draft" },
              cover_letter: { Letter: "Hello" },
            },
          },
        })
      }
      if (url === `/api/candidates/${baseCandidate.astral_candidate_id}/resume_structure`) {
        return jsonResponse({
          sections: [{ id: "professional_summary", label: "Summary" }],
          accent_color: null,
        })
      }
      if (url === `/api/candidates/${baseCandidate.astral_candidate_id}/data` && init?.method === "PUT") {
        return jsonResponse({})
      }
      if (url === "/candidate/resume/j-print" && !init) {
        return {
          ok: true,
          text: async () => "<html><body>job resume</body></html>",
        } as Response
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j-print" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(screen.getByRole("button", { name: "Print Resume" }))
    await waitFor(() => expect(openSpy).toHaveBeenCalledWith("blob:jar-resume-html", "_blank"))
    expect(fakeWin.opener).toBeNull()
    expect(screen.queryByText("Popup blocked — allow popups to open the HTML tab.")).not.toBeInTheDocument()
    expect(createSpy).toHaveBeenCalled()
    expect(mockedApi.mock.calls.some(([u]) => u === "/candidate/resume/j-print")).toBe(true)
    await userEvent.click(screen.getByRole("button", { name: "Print Cover Letter" }))
    expect(openSpy).toHaveBeenCalledWith("/candidate/cover/j-print", "_blank", "noopener,noreferrer")
    openSpy.mockRestore()
    vi.unstubAllGlobals()
  })

  it("AST-1350: Print Resume unsupported toast — no tab", async () => {
    const openSpy = vi.spyOn(window, "open").mockImplementation(() => null)
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j-unsup" && !init) {
        return jsonResponse({
          astral_job_id: "j-unsup",
          job_title: "Role",
          company: "Co",
          state: "CANDIDATE_REVIEW",
          state_changed_at: null,
          job_link: "https://jobs.example/apply",
          job_data: {
            job_description: "JD",
            analysis_upshot: fullUpshot(),
            artifacts: {
              job_resume: { professional_summary: "Draft", experience: "legacy" },
              cover_letter: { Letter: "Hello" },
            },
          },
        })
      }
      if (url === `/api/candidates/${baseCandidate.astral_candidate_id}/data` && init?.method === "PUT") {
        return jsonResponse({})
      }
      if (url === `/api/candidates/${baseCandidate.astral_candidate_id}/resume_structure` && !init) {
        return jsonResponse({
          sections: [{ id: "professional_summary", label: "Summary" }],
          accent_color: null,
        })
      }
      if (url === "/candidate/resume/j-unsup" && !init) {
        return {
          ok: false,
          status: 400,
          json: async () => ({ error: "unsupported resume structure, please regenerate" }),
        } as Response
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j-unsup" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(screen.getByRole("button", { name: "Print Resume" }))
    await waitFor(() =>
      expect(
        screen.getAllByText("unsupported resume structure, please regenerate").length,
      ).toBeGreaterThan(0),
    )
    expect(openSpy).not.toHaveBeenCalled()
    openSpy.mockRestore()
  })

  it("hides print buttons when artifacts are empty", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j948"))
    renderWithProviders(<JobAnalysisReportModal jobId="j948" onClose={() => {}} />)
    await waitForShell()
    expect(screen.queryByRole("button", { name: "Print Resume" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Print Cover Letter" })).not.toBeInTheDocument()
  })

  it("job-link line uses listing_href for CANDIDATE_REVIEW (Apply filtered from Artifacts)", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j-ready", { state: "CANDIDATE_REVIEW" }))
    renderWithProviders(<JobAnalysisReportModal jobId="j-ready" onClose={() => {}} />)
    await waitForShell()
    expect(screen.queryByRole("link", { name: "Analyst" })).not.toBeInTheDocument()
    expect(screen.getByRole("link", { name: "https://jobs.example/apply" })).toHaveAttribute("href", "https://jobs.example/apply")
    expect(screen.queryByRole("button", { name: "Apply" })).not.toBeInTheDocument()
    // Apply filtered from Artifacts strip — navigable open is the job-link line (AST-1873) + CLIENT handler
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
    await openSummaryTab()
    expect(screen.getByText("Job Summary")).toBeInTheDocument()
    expect(screen.queryByText("No analysis upshot on file.")).not.toBeInTheDocument()
  })

  it("shows Generating… + Cancel on Artifacts for BUILD_ARTIFACTS", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j-build", { state: "BUILD_ARTIFACTS" }))
    renderWithProviders(<JobAnalysisReportModal jobId="j-build" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Artifacts" }))
    const strip = document.querySelector(".recommended-report-artifacts-actions") as HTMLElement
    expect(within(strip).getByRole("button", { name: "Generating…" })).toBeDisabled()
    expect(within(strip).getByRole("button", { name: "Generating…" })).toHaveClass("in-flight")
    expect(within(strip).getByRole("button", { name: "Cancel" })).toBeInTheDocument()
    expect(screen.queryByText("Job Resume")).not.toBeInTheDocument()
  })
})

describe("JobAnalysisReportModal — AST-1334 footer opt-out", () => {
  beforeEach(() => mockedApi.mockReset())

  it("omits modal footer Cancel; header Close still dismisses", async () => {
    const onClose = vi.fn()
    installBaseApiMocks(mockedApi, jobHandler("j1334"))
    renderWithProviders(<JobAnalysisReportModal jobId="j1334" onClose={onClose} />)
    await waitForShell()
    expect(document.querySelector(".modal-footer")).toBeNull()
    // Default (Analysis) tab: no footer Cancel — only Artifacts in-flight Cancel remains elsewhere
    expect(screen.queryByRole("button", { name: "Cancel" })).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Close" }))
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it("BUILD_ARTIFACTS keeps Artifacts-strip Cancel without a footer Cancel", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j1334-build", { state: "BUILD_ARTIFACTS" }))
    renderWithProviders(<JobAnalysisReportModal jobId="j1334-build" onClose={() => {}} />)
    await waitForShell()
    expect(document.querySelector(".modal-footer")).toBeNull()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Artifacts" }))
    const strip = document.querySelector(".recommended-report-artifacts-actions") as HTMLElement
    expect(within(strip).getByRole("button", { name: "Cancel" })).toBeInTheDocument()
    // Exactly one Cancel in the document (Artifacts strip — not a footer twin)
    expect(screen.getAllByRole("button", { name: "Cancel" })).toHaveLength(1)
  })
})

describe("JobAnalysisReportModal — AST-949 Summary tab sections", () => {
  beforeEach(() => mockedApi.mockReset())

  // AST-2071: Company Upshot reads company_upshot; prefilter grade notes are a decoy that must not render
  function companyWithUpshot(url: string, init?: RequestInit) {
    if (url === "/api/companies/Globex") {
      return jsonResponse({
        company_website: "https://globex.example",
        company_upshot: "Steady growth, remote-friendly.",
        prefilter_company_notes: "GRADE_NOTES_DECOY",
      })
    }
    return jobHandler("j949")(url, init)
  }

  it("fills Summary section bodies from upshot, company upshot, and JD", async () => {
    installBaseApiMocks(mockedApi, companyWithUpshot)
    renderWithProviders(<JobAnalysisReportModal jobId="j949" onClose={() => {}} />)
    await waitForShell()
    await openSummaryTab()
    expect(await screen.findByText("Strong thematic fit.")).toBeInTheDocument()
    expect(await screen.findByText("Steady growth, remote-friendly.")).toBeInTheDocument()
    expect(screen.queryByText("GRADE_NOTES_DECOY")).not.toBeInTheDocument()
    expect(screen.getByText("Remote only")).toBeInTheDocument()
    expect(screen.getByText("What is the team size?")).toBeInTheDocument()
    // Raw JD starts collapsed — expand to read body
    expect(screen.queryByText("Full JD body text")).not.toBeVisible()
    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    expect(screen.getByText("Full JD body text")).toBeVisible()
  })

  it("content-aware expand: Raw JD collapsed; populated sections open", async () => {
    installBaseApiMocks(mockedApi, companyWithUpshot)
    renderWithProviders(<JobAnalysisReportModal jobId="j949" onClose={() => {}} />)
    await waitForShell()
    await openSummaryTab()
    await waitFor(() => expect(screen.getByText("Steady growth, remote-friendly.")).toBeInTheDocument())
    // job_summary + company + caveats + questions expanded; raw_jd collapsed
    expect(screen.getAllByRole("button", { name: "Collapse section" }).length).toBe(4)
    expect(screen.getAllByRole("button", { name: "Expand section" }).length).toBe(1)
  })

  it("shows empty-state copy when upshot and company upshot are missing", async () => {
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
        // whitespace upshot = empty; grade notes present but must not fill the section (AST-2071)
        return jsonResponse({ company_website: null, company_upshot: "   ", prefilter_company_notes: "GRADE_NOTES_DECOY" })
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j949-empty" onClose={() => {}} />)
    await waitForShell()
    await openSummaryTab()
    expect(await screen.findByText("No job summary on file.")).toBeInTheDocument()
    // company / caveats / questions / raw_jd start collapsed when empty — expand to read copy
    const expands = screen.getAllByRole("button", { name: "Expand section" })
    expect(expands.length).toBe(4)
    await userEvent.click(expands[0])
    expect(screen.getByText("No company upshot on file.")).toBeVisible()
    expect(screen.queryByText("GRADE_NOTES_DECOY")).not.toBeInTheDocument()
    await userEvent.click(expands[1])
    expect(screen.getByText("No noteworthy caveats on file.")).toBeVisible()
    await userEvent.click(expands[2])
    expect(screen.getByText("No questions to ask on file.")).toBeVisible()
    await userEvent.click(expands[3])
    expect(screen.getByText("No job description on file.")).toBeVisible()
  })

  it("company upshot comes from company API, not job_data", async () => {
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
            company_upshot: "FROM_JOB_DATA",
          },
        })
      }
      if (url === "/api/companies/Globex") {
        return jsonResponse({
          company_website: "https://globex.example",
          company_upshot: "FROM_COMPANY_API",
        })
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j949-notes" onClose={() => {}} />)
    await waitForShell()
    await openSummaryTab()
    expect(await screen.findByText("FROM_COMPANY_API")).toBeInTheDocument()
    expect(screen.queryByText("FROM_JOB_DATA")).not.toBeInTheDocument()
  })
})

describe("JobAnalysisReportModal — AST-950 Analysis tab grades and confidence", () => {
  beforeEach(() => mockedApi.mockReset())

  const jdRubric = [{ code: "JD", label: "Job Description (JD)", importance: 1 }]
  const doRubric = [{ code: "TE", label: "Technical (TE)", importance: 2 }]

  function analysisJobHandler(jobId: string) {
    return (url: string, init?: RequestInit) => {
      if (url === `/api/jobs/${jobId}` && !init) {
        // Top-level *_rubric / *_grades mirror AST-1063 API flatten (header columns read top-level).
        return jsonResponse({
          astral_job_id: jobId,
          job_title: "Analyst",
          company: "Globex",
          state: "RECOMMENDED",
          state_changed_at: "2026-01-03T00:00:00Z",
          job_link: "https://jobs.example/apply",
          jd_grades: [
            { vector: "Job Description (JD)", grade: "A", reason: "Strong match", confidence: 4 },
          ],
          jd_rubric: jdRubric,
          do_grades: [{ vector: "Technical (TE)", grade: "B", reason: "Solid skills", confidence: 3 }],
          do_rubric: doRubric,
          job_data: {
            job_description: "Full JD body text",
            analysis_upshot: fullUpshot(),
            jd_grades: [
              { vector: "Job Description (JD)", grade: "A", reason: "Strong match", confidence: 4 },
            ],
            do_grades: [
              { vector: "Technical (TE)", grade: "B", reason: "Solid skills", confidence: 3 },
            ],
            jd_rubric: jdRubric,
            do_rubric: doRubric,
          },
        })
      }
      if (url === "/api/companies/Globex") {
        return jsonResponse({ company_website: "https://globex.example" })
      }
      return undefined
    }
  }

  it("shows JD/DO/GET/LIKE only with all phases collapsed (no Overview)", async () => {
    installBaseApiMocks(mockedApi, analysisJobHandler("j950"))
    renderWithProviders(<JobAnalysisReportModal jobId="j950" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Analysis" }))
    expect(screen.getByText("JD Analysis")).toBeInTheDocument()
    expect(screen.getByText("DO Analysis")).toBeInTheDocument()
    expect(screen.getByText("GET Analysis")).toBeInTheDocument()
    expect(screen.getByText("LIKE Analysis")).toBeInTheDocument()
    expect(screen.queryByText("Overview")).not.toBeInTheDocument()
    expect(screen.queryAllByRole("button", { name: "Collapse section" }).length).toBe(0)
    expect(screen.getAllByRole("button", { name: "Expand section" }).length).toBe(4)
  })

  it("header grade+confidence row visible while collapsed; take_* above rubric when expanded", async () => {
    installBaseApiMocks(mockedApi, analysisJobHandler("j950"))
    renderWithProviders(<JobAnalysisReportModal jobId="j950" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Analysis" }))

    // All collapsed: header metadata (grade+confidence) still painted
    expect(document.querySelector(".recommended-report-phase-grade-row")).toBeTruthy()
    expect(
      document.querySelector(".recommended-report-phase-grade-cell .grade-dot.dot-a"),
    ).toBeTruthy()
    expect(
      document.querySelectorAll(".recommended-report-phase-grade-cell .confidence-bullets").length,
    ).toBeGreaterThan(0)
    expect(screen.queryByText("JD phase thought")).not.toBeVisible()

    // Expand JD — take above AgentAnalysisHeader; collapse again keeps header
    const expands = screen.getAllByRole("button", { name: "Expand section" })
    await userEvent.click(expands[0])
    expect(await screen.findByText("JD phase thought")).toBeVisible()
    expect(screen.getByText("Strong match")).toBeVisible()
    await userEvent.click(screen.getByRole("button", { name: "Collapse section" }))
    expect(screen.getByText("JD phase thought")).not.toBeVisible()
    expect(document.querySelector(".recommended-report-phase-grade-row")).toBeTruthy()
  })

  it("expanded DO shows take_do above consult grades", async () => {
    installBaseApiMocks(mockedApi, analysisJobHandler("j950"))
    renderWithProviders(<JobAnalysisReportModal jobId="j950" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Analysis" }))
    const expands = screen.getAllByRole("button", { name: "Expand section" })
    // Phase order: JD, DO, GET, LIKE — all start collapsed
    await userEvent.click(expands[1])
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
    const expands = screen.getAllByRole("button", { name: "Expand section" })
    await userEvent.click(expands[0])
    const jdPanel = document.querySelector(".collapsible-panel.is-expanded") as HTMLElement
    expect(jdPanel).toBeTruthy()
    expect(within(jdPanel).getByText("No consult detail on file.")).toBeVisible()
    expect(document.querySelector(".recommended-report-phase-grade-row")).toBeNull()
  })

  // AST-1328 bug-repro: live gazer artifact underlaps job-carried jd_rubric — header still full.
  it("AST-1328: Analysis header uses job-carried jd_rubric when live jobdesc_rubric underlaps", async () => {
    const grades = [
      { vector: "Embedded/Firmware/Hardware Domain", grade: "A", confidence: 5, reason: "fit" },
      { vector: "Quality Check", grade: "B", confidence: 4, reason: "ok" },
    ]
    const rubric = [
      { code: "EFW", label: "Embedded/Firmware/Hardware Domain", importance: 1, grade_descriptions: [] },
      { code: "QC", label: "Quality Check", importance: 5, grade_descriptions: [] },
    ]
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/me") {
        return jsonResponse({ user_id: "u1", name: "Test User", is_admin: true })
      }
      if (url === "/api/candidates") {
        return jsonResponse([
          {
            ...baseCandidate,
            candidate_data: {
              ...baseCandidate.candidate_data,
              artifacts: {
                ...baseCandidate.candidate_data.artifacts,
                // Live underlap — pre-AST-1327 header would show only QC
                jobdesc_rubric: [{ code: "QC", label: "Quality Check", importance: 5 }],
              },
            },
          },
        ])
      }
      if (url === "/api/state_ui_manifest") {
        return jsonResponse(STATE_UI_MANIFEST_FIXTURE)
      }
      if (url === "/api/jobs/j950-meteorite" && !init) {
        return jsonResponse({
          astral_job_id: "j950-meteorite",
          job_title: "Firmware",
          company: "meteorite-co",
          state: "RECOMMENDED",
          state_changed_at: "2026-01-03T00:00:00Z",
          jd_grades: grades,
          jd_rubric: rubric,
          job_data: {
            job_description: "JD",
            analysis_upshot: fullUpshot(),
            jd_grades: grades,
            jd_rubric: rubric,
          },
        })
      }
      if (url === "/api/companies/meteorite-co") {
        return jsonResponse({ company_website: null })
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j950-meteorite" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Analysis" }))
    await waitFor(() =>
      expect(document.querySelectorAll(".recommended-report-phase-grade-cell").length).toBe(2),
    )
    expect(document.querySelector(".grade-dot.dot-a")).toBeTruthy()
    expect(document.querySelector(".grade-dot.dot-b")).toBeTruthy()

    // AST-1771: header + expanded detail share importance+grade order (QC before EFW).
    const headerCells = document.querySelectorAll(".recommended-report-phase-grade-cell")
    expect(headerCells[0].querySelector(".grade-dot.dot-b")).toBeTruthy()
    expect(headerCells[1].querySelector(".grade-dot.dot-a")).toBeTruthy()
    const firstDotTitle = headerCells[0].querySelector(".grade-dot")?.getAttribute("title") ?? ""
    expect(firstDotTitle.startsWith("Quality Check")).toBe(true)

    const expands = screen.getAllByRole("button", { name: "Expand section" })
    await userEvent.click(expands[0])
    await waitFor(() => expect(document.querySelectorAll(".analysis-vector").length).toBe(2))
    const vectors = Array.from(document.querySelectorAll(".analysis-vector")).map(el => el.textContent ?? "")
    expect(vectors[0]).toMatch(/Quality Check/)
    expect(vectors[1]).toMatch(/Embedded|Firmware/)
  })
})
describe("JobAnalysisReportModal — AST-951 Artifacts tab layouts", () => {
  beforeEach(() => mockedApi.mockReset())

  it("compound BUILD_ARTIFACTS hop shows Generating… + Cancel via base-state fallback", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j-hop", { state: "BUILD_ARTIFACTS.draft_job_resume" }))
    renderWithProviders(<JobAnalysisReportModal jobId="j-hop" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Artifacts" }))
    const strip = document.querySelector(".recommended-report-artifacts-actions") as HTMLElement
    expect(within(strip).getByRole("button", { name: "Generating…" })).toBeDisabled()
    expect(within(strip).getByRole("button", { name: "Cancel" })).toBeInTheDocument()
  })

  it("Cancel closes modal after cancel_build POST", async () => {
    const onClose = vi.fn()
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j-cancel/cancel_artifact_build" && init?.method === "POST") {
        return jsonResponse({ ok: true, state: "RECOMMENDED" })
      }
      return jobHandler("j-cancel", { state: "BUILD_ARTIFACTS" })(url, init)
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j-cancel" onClose={onClose} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Artifacts" }))
    const strip = document.querySelector(".recommended-report-artifacts-actions") as HTMLElement
    await userEvent.click(within(strip).getByRole("button", { name: "Cancel" }))
    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith("/api/jobs/j-cancel/cancel_artifact_build", {
        method: "POST",
      }),
    )
    await waitFor(() => expect(onClose).toHaveBeenCalled())
  })

  it("ERROR_ANTICIPATE_SCAN is not Generating… chrome", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j-err", { state: "ERROR_ANTICIPATE_SCAN" }))
    renderWithProviders(<JobAnalysisReportModal jobId="j-err" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Artifacts" }))
    expect(screen.queryByRole("button", { name: "Generating…" })).not.toBeInTheDocument()
  })

  /** AST-2084: job with generated artifacts; print routes answer with distinct HTML so each preview is identifiable. */
  function artifactJobMocks(jobId: string, artifacts: Record<string, unknown>, log?: { url: string; method: string }[]) {
    let jobGets = 0
    installBaseApiMocks(mockedApi, (url, init) => {
      log?.push({ url, method: init?.method ?? "GET" })
      if (url === `/api/jobs/${jobId}` && !init?.method) {
        jobGets += 1
        return jsonResponse({
          astral_job_id: jobId,
          candidate_id: baseCandidate.astral_candidate_id,
          job_title: "Role",
          company: "Co",
          state: "CANDIDATE_REVIEW",
          state_changed_at: null,
          job_link: "https://jobs.example/apply",
          job_data: { job_description: "JD", analysis_upshot: fullUpshot(), artifacts },
        })
      }
      if (url === `/candidate/resume/${jobId}`) return { ok: true, status: 200, text: async () => "<html>resume print</html>" } as Response
      if (url === `/candidate/cover/${jobId}`) return { ok: true, status: 200, text: async () => "<html>cover print</html>" } as Response
      // Edit modal's ResumeContentEditor reads the job structure.
      if (url === `/api/jobs/${jobId}/resume_structure`) {
        return jsonResponse({
          all_sections: [{
            id: "professional_summary", title: "Summary", enabled: true, order: 0, format: "free_prose",
            job_agent_editable: true, required: true, format_locked: false, page_break_policy: "normal",
          }],
          accent_color: null,
          catalog: {
            body_formats: ["free_prose"], required_ids: ["professional_summary"], contact_ids: [],
            extra_id_pattern: "^[a-z_]+$", reserved_extra_ids: [], new_extra_default_format: "free_prose",
            page_break_policies: ["normal"], page_break_policy_labels: { normal: "Flow" }, page_break_policy_default: "normal",
            body_format_details: { free_prose: { label: "Prose", description: "Prose", font_family: "serif" } },
            hidden_flow_label: "Hidden",
          },
        })
      }
      if (url === "/api/shapes/candidates") {
        return jsonResponse({ detail: { cover_letter: [{ key: "Letter", label: "Letter" }] } })
      }
      return undefined
    })
    return { jobGets: () => jobGets }
  }

  async function openArtifactsExpanded(jobId: string) {
    renderWithProviders(<JobAnalysisReportModal jobId={jobId} onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Artifacts" }))
    const sectionList = await waitFor(() => document.querySelector(".recommended-report-section-list") as HTMLElement)
    for (const b of within(sectionList).getAllByRole("button", { name: "Expand section" })) await userEvent.click(b)
    return sectionList
  }

  const thumbs = () => [...document.querySelectorAll(".print-preview-thumb")] as HTMLElement[]
  const thumbHtml = (t: HTMLElement) => t.querySelector("iframe")?.getAttribute("srcdoc")
  const editModal = () => document.querySelector(".modal-overlay--stacked") as HTMLElement | null

  it("AST-2084: populated Artifacts shows Job Resume + Cover Letter thumbnails, Edit on the resume only, no inline editors", async () => {
    artifactJobMocks("j-pop", { job_resume: { professional_summary: "Draft text" }, cover_letter: { Letter: "Cover body" } })
    const sectionList = await openArtifactsExpanded("j-pop")
    expect(screen.queryByRole("button", { name: "Generate Artifacts" })).not.toBeInTheDocument()
    const headerLabels = [...sectionList.querySelectorAll(".collapsible-panel-label-wrap")].map(el => el.textContent?.trim())
    expect(headerLabels).toEqual(["Job Resume", "Cover Letter"])
    await waitFor(() => expect(thumbs().map(thumbHtml)).toEqual(["<html>resume print</html>", "<html>cover print</html>"]))
    expect(within(sectionList).getAllByRole("button", { name: "Edit" })).toHaveLength(1)
    // No inline editor bodies on the report.
    expect(screen.queryByDisplayValue("Draft text")).not.toBeInTheDocument()
    expect(screen.queryByDisplayValue("Cover body")).not.toBeInTheDocument()
    expect(sectionList.querySelector("textarea")).toBeNull()
  })

  it("AST-2084: only a generated artifact gets a thumbnail", async () => {
    artifactJobMocks("j-one", { job_resume: { professional_summary: "Draft text" } })
    const sectionList = await openArtifactsExpanded("j-one")
    const headerLabels = [...sectionList.querySelectorAll(".collapsible-panel-label-wrap")].map(el => el.textContent?.trim())
    expect(headerLabels).toEqual(["Job Resume"])
    await waitFor(() => expect(thumbs()).toHaveLength(1))
    expect(mockedApi.mock.calls.some(([u]) => u === "/candidate/cover/j-one")).toBe(false)
  })

  it("AST-2084: resume thumbnail opens a stacked full-screen editor + live preview over the report; close reloads the report", async () => {
    const m = artifactJobMocks("j-edit", { job_resume: { professional_summary: "Draft text" }, cover_letter: { Letter: "Cover body" } })
    await openArtifactsExpanded("j-edit")
    await waitFor(() => expect(thumbs()).toHaveLength(2))
    await userEvent.click(thumbs()[0])
    const modal = await waitFor(() => { const el = editModal(); expect(el).toBeTruthy(); return el! })
    expect(within(modal).getByRole("heading", { name: "Job Resume" })).toBeInTheDocument()
    // Report stays mounted underneath (stacked, not replaced).
    expect(document.querySelector(".recommended-report-tabs")).toBeTruthy()
    expect(await within(modal).findByLabelText("Search sections")).toBeInTheDocument()
    await waitFor(() => expect(modal.querySelector('iframe[title="Print preview"]')?.getAttribute("srcdoc")).toBe("<html>resume print</html>"))
    const before = m.jobGets()
    await userEvent.click(within(modal).getByRole("button", { name: "Close" }))
    await waitFor(() => expect(editModal()).toBeNull())
    await waitFor(() => expect(m.jobGets()).toBeGreaterThan(before))
  })

  it("AST-2084: Edit opens the resume modal; cover thumbnail opens the cover editor + cover preview", async () => {
    artifactJobMocks("j-both", { job_resume: { professional_summary: "Draft text" }, cover_letter: { Letter: "Cover body" } })
    const sectionList = await openArtifactsExpanded("j-both")
    await waitFor(() => expect(thumbs()).toHaveLength(2))
    await userEvent.click(within(sectionList).getByRole("button", { name: "Edit" }))
    let modal = await waitFor(() => { const el = editModal(); expect(el).toBeTruthy(); return el! })
    expect(within(modal).getByRole("heading", { name: "Job Resume" })).toBeInTheDocument()
    expect(await within(modal).findByLabelText("Search sections")).toBeInTheDocument()
    await userEvent.click(within(modal).getByRole("button", { name: "Close" }))
    await waitFor(() => expect(editModal()).toBeNull())
    await waitFor(() => expect(thumbs()).toHaveLength(2))
    await userEvent.click(thumbs()[1])
    modal = await waitFor(() => { const el = editModal(); expect(el).toBeTruthy(); return el! })
    // Modal title (the cover editor carries its own "Cover Letter" heading too).
    expect(modal.querySelector(".modal-title")?.textContent).toBe("Cover Letter")
    expect(within(modal).queryByLabelText("Search sections")).toBeNull()
    await waitFor(() => expect(modal.querySelector('iframe[title="Print preview"]')?.getAttribute("srcdoc")).toBe("<html>cover print</html>"))
  })

  it("AST-2084: Print Resume opens the shared print HTML with no candidate structure fetch or PUT", async () => {
    const fakeWin = { opener: {} as Window | null }
    const openSpy = vi.spyOn(window, "open").mockImplementation(() => fakeWin as unknown as Window)
    vi.stubGlobal("URL", { createObjectURL: vi.fn(() => "blob:jar-2084"), revokeObjectURL: vi.fn() })
    const log: { url: string; method: string }[] = []
    artifactJobMocks("j-print2084", { job_resume: { professional_summary: "Draft text" } }, log)
    renderWithProviders(<JobAnalysisReportModal jobId="j-print2084" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(screen.getByRole("button", { name: "Print Resume" }))
    await waitFor(() => expect(openSpy).toHaveBeenCalledWith("blob:jar-2084", "_blank"))
    expect(log.some(c => c.url === "/candidate/resume/j-print2084")).toBe(true)
    expect(log.filter(c => c.method === "PUT")).toEqual([])
    expect(log.some(c => c.url.endsWith("/resume_structure"))).toBe(false)
    openSpy.mockRestore()
    vi.unstubAllGlobals()
  })

  it("does not show Reset or Regenerate on Artifacts tab", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j948"))
    renderWithProviders(<JobAnalysisReportModal jobId="j948" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Artifacts" }))
    expect(screen.queryByRole("button", { name: /Reset/i })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: /Regenerate/i })).not.toBeInTheDocument()
  })
})

describe("JobAnalysisReportModal — AST-1274 load error honesty", () => {
  beforeEach(() => mockedApi.mockReset())

  it("shows Job not found only for HTTP 404", async () => {
    installBaseApiMocks(mockedApi, (url) => {
      if (url === "/api/jobs/j-404") {
        return jsonResponse({ error: "Not found" }, { ok: false, status: 404 })
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j-404" onClose={() => {}} />)
    expect(await screen.findByText("Job not found")).toBeInTheDocument()
    expect(screen.queryByText(/Load failed/i)).not.toBeInTheDocument()
  })

  it("shows JSON error for non-404 failures", async () => {
    installBaseApiMocks(mockedApi, (url) => {
      if (url === "/api/jobs/j-500") {
        return jsonResponse({ error: "story hydrate blew up" }, { ok: false, status: 500 })
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j-500" onClose={() => {}} />)
    expect(await screen.findByText("story hydrate blew up")).toBeInTheDocument()
    expect(screen.queryByText("Job not found")).not.toBeInTheDocument()
  })

  it("falls back to Load failed (HTTP status) when body has no error", async () => {
    installBaseApiMocks(mockedApi, (url) => {
      if (url === "/api/jobs/j-503") {
        return jsonResponse({}, { ok: false, status: 503 })
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j-503" onClose={() => {}} />)
    expect(await screen.findByText("Load failed (HTTP 503)")).toBeInTheDocument()
    expect(screen.queryByText("Job not found")).not.toBeInTheDocument()
  })
})

describe("JobAnalysisReportModal — AST-1348 Analysis score title chrome", () => {
  beforeEach(() => mockedApi.mockReset())

  it("shows formatted score title when breakdown is present; plain label when absent", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j1348" && !init) {
        return jsonResponse({
          astral_job_id: "j1348",
          job_title: "Analyst",
          company: "Globex",
          state: "RECOMMENDED",
          state_changed_at: "2026-01-03T00:00:00Z",
          job_link: "https://jobs.example/apply",
          jd_grades: [
            { vector: "Job Description (JD)", grade: "A", reason: "Strong match", confidence: 4 },
          ],
          jd_rubric: [{ code: "JD", label: "Job Description (JD)", importance: 1 }],
          jd_score: 8.5,
          jd_score_breakdown: { earned: 137.4, possible: 150.2, max: 320.9 },
          // DO: grades present but no breakdown / score → plain label
          do_grades: [{ vector: "Technical (TE)", grade: "B", reason: "Solid", confidence: 3 }],
          do_rubric: [{ code: "TE", label: "Technical (TE)", importance: 2 }],
          job_data: {
            job_description: "Full JD body text",
            analysis_upshot: fullUpshot(),
          },
        })
      }
      if (url === "/api/companies/Globex") {
        return jsonResponse({ company_website: "https://globex.example" })
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j1348" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Analysis" }))
    expect(
      screen.getByText("JD Analysis - 8.5 - score: 137 out of 150 possible (321 max total)"),
    ).toBeInTheDocument()
    expect(screen.getByText("DO Analysis")).toBeInTheDocument()
    expect(screen.queryByText(/^DO Analysis - score:/)).not.toBeInTheDocument()
    expect(screen.getByText("GET Analysis")).toBeInTheDocument()
    expect(screen.getByText("LIKE Analysis")).toBeInTheDocument()
  })
})

describe("JobAnalysisReportModal — AST-1421 snapshot Copy", () => {
  beforeEach(() => mockedApi.mockReset())

  it("copies via the helper and does not drive email/linkedin copyFeedback", async () => {
    mockedCopy.mockResolvedValue(true)
    installBaseApiMocks(mockedApi, jobHandler("j1421"))
    renderWithProviders(<JobAnalysisReportModal jobId="j1421" onClose={() => {}} />)
    await waitForShell()
    const copyBtn = screen.getByRole("button", { name: "Copy Job JSON" })
    expect(screen.getByRole("button", { name: "Copy Application Email" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Copy LinkedIn Profile" })).toBeInTheDocument()
    await userEvent.click(copyBtn)
    await waitFor(() => expect(mockedCopy).toHaveBeenCalledWith("j1421"))
    await waitFor(() => expect(screen.getByRole("button", { name: /^Copied$/ })).toBeInTheDocument())
    expect(document.querySelector(".recommended-report-copy-feedback")).toBeNull()
    await waitFor(
      () => expect(screen.getByRole("button", { name: "Copy Job JSON" })).toBeInTheDocument(),
      { timeout: 3000 },
    )
  })
})

describe("JobAnalysisReportModal — AST-1696 Copy Link", () => {
  beforeEach(() => {
    mockedApi.mockReset()
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      configurable: true,
    })
  })

  it("writes absolute /jobs/detail/<id> URL and returns idle label; other header actions stay", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j1696"))
    renderWithProviders(<JobAnalysisReportModal jobId="j1696" onClose={() => {}} />)
    await waitForShell()
    const links = document.querySelector(".recommended-report-links") as HTMLElement
    expect(within(links).getByRole("button", { name: "Copy Job Link" })).toHaveClass("btn", "secondary")
    expect(within(links).getByRole("button", { name: "Copy Job JSON" })).toBeInTheDocument()
    expect(within(links).getByRole("button", { name: "Copy Application Email" })).toBeInTheDocument()
    expect(within(links).getByRole("button", { name: "Copy LinkedIn Profile" })).toBeInTheDocument()

    await userEvent.click(within(links).getByRole("button", { name: "Copy Job Link" }))
    await waitFor(() =>
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
        `${window.location.origin}/jobs/detail/j1696`,
      ),
    )
    await waitFor(() =>
      expect(within(links).getByRole("button", { name: /^Copied$/ })).toBeInTheDocument(),
    )
    expect(document.querySelector(".recommended-report-copy-feedback")).toBeNull()
    await waitFor(
      () => expect(within(links).getByRole("button", { name: "Copy Job Link" })).toBeInTheDocument(),
      { timeout: 3000 },
    )
  })
})

describe("JobAnalysisReportModal — AST-1551 Discussion tab", () => {
  beforeEach(() => mockedApi.mockReset())

  it("Discussion tab with empty story shows zero hop headers", async () => {
    // AST-1612 / AST-1609: default job agent_story empty → 0 Expand buttons.
    installBaseApiMocks(mockedApi, jobHandler("j1551"))
    renderWithProviders(<JobAnalysisReportModal jobId="j1551" onClose={() => {}} />)
    await waitForShell()
    const bar = topTabBar()
    const discussion = within(bar).getByRole("button", { name: "Discussion" })
    // AST-1692: Meteorite omitted when related_meteorite null — Discussion still last visible
    const tabs = within(bar).getAllByRole("button")
    expect(tabs.map(t => t.textContent)).toEqual([
      "Analysis",
      "Summary",
      "Artifacts",
      "Discussion",
    ])
    expect(within(bar).queryByRole("button", { name: "Meteorite" })).not.toBeInTheDocument()
    await userEvent.click(discussion)
    expect(screen.queryByText("Contemplate Job")).not.toBeInTheDocument()
    expect(screen.queryByText("Propose Application Responses")).not.toBeInTheDocument()
    expect(screen.queryAllByRole("button", { name: "Expand section" })).toHaveLength(0)
  })

  it("partial agent_story shows only hops with RESPONSE", async () => {
    installBaseApiMocks(
      mockedApi,
      jobHandler("j1551-partial", {
        agent_story: [
          {
            task_key: "contemplate_job",
            blocks: [
              { type: "PROMPT", id: "p", content: "hidden" },
              { type: "RESPONSE", id: "r", content: '{"hop":1}' },
            ],
          },
        ],
      }),
    )
    renderWithProviders(<JobAnalysisReportModal jobId="j1551-partial" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Discussion" }))
    expect(screen.getAllByRole("button", { name: "Expand section" })).toHaveLength(1)
    expect(screen.getByText("Contemplate Job")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    const area = document.querySelector("textarea.entity-story-content") as HTMLTextAreaElement
    expect(area).toBeTruthy()
    expect(area.readOnly).toBe(true)
    expect(area.value).toContain('"hop": 1')
    expect(screen.queryByDisplayValue("hidden")).not.toBeInTheDocument()
  })
})




describe("JobAnalysisReportModal — AST-1692 Meteorite tab", () => {
  beforeEach(() => mockedApi.mockReset())

  const related = {
    id: 7,
    created_at: "2026-02-01T00:00:00Z",
    updated_at: "2026-02-02T00:00:00Z",
    state_changed_at: "2026-02-03T00:00:00Z",
    estelle_notified_at: null,
    link: "https://jobs.example/m7",
    classify_outcome: "QUALIFIED",
    content: '{"pane":true}',
    state: "LANDED",
    source_kind: "email",
    source_id: "src-7",
    error: null,
  }

  it("shows Meteorite after Discussion when related_meteorite is present", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j1692", { related_meteorite: related }))
    renderWithProviders(<JobAnalysisReportModal jobId="j1692" onClose={() => {}} />)
    await waitForShell()
    const bar = topTabBar()
    expect(within(bar).getAllByRole("button").map(t => t.textContent)).toEqual([
      "Analysis",
      "Summary",
      "Artifacts",
      "Discussion",
      "Meteorite",
    ])
    await userEvent.click(within(bar).getByRole("button", { name: "Meteorite" }))
    expect(screen.getByText("Timestamps")).toBeInTheDocument()
    expect(screen.getByText("created_at: 2026-02-01T00:00:00Z")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "https://jobs.example/m7" })).toBeInTheDocument()
    expect(screen.getByText("classify_outcome: QUALIFIED")).toBeInTheDocument()
    const area = document.querySelector("textarea.entity-story-content") as HTMLTextAreaElement
    expect(area?.readOnly).toBe(true)
    expect(area?.value).toContain('"pane": true')
  })

  it("omits Meteorite tab when related_meteorite is null", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j1692-null", { related_meteorite: null }))
    renderWithProviders(<JobAnalysisReportModal jobId="j1692-null" onClose={() => {}} />)
    await waitForShell()
    const bar = topTabBar()
    expect(within(bar).queryByRole("button", { name: "Meteorite" })).not.toBeInTheDocument()
    expect(within(bar).getAllByRole("button").map(t => t.textContent)).toEqual([
      "Analysis",
      "Summary",
      "Artifacts",
      "Discussion",
    ])
  })
})

describe("JobAnalysisReportModal — AST-1599 no Source base resume on Artifacts", () => {
  beforeEach(() => mockedApi.mockReset())

  it("[bug-repro] populated Artifacts after finished build must not show Source base resume", async () => {
    // Pre-fix (AST-1585 panel): Artifacts always renders provenance; epic forbids it.
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j1599-pop" && !init) {
        return jsonResponse({
          astral_job_id: "j1599-pop",
          job_title: "Role",
          company: "Co",
          state: "CANDIDATE_REVIEW",
          state_changed_at: null,
          job_link: "https://jobs.example/apply",
          job_data: {
            job_description: "JD",
            analysis_upshot: fullUpshot(),
            // no base_resume_artifact_id — provenance gap must not appear
            artifacts: {
              job_resume: { professional_summary: "Draft text" },
              cover_letter: { Letter: "Cover body" },
            },
          },
        })
      }
      if (url === `/api/candidates/${baseCandidate.astral_candidate_id}/resume_structure`) {
        return jsonResponse({
          sections: [{ id: "professional_summary", label: "Summary" }],
          accent_color: null,
        })
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j1599-pop" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Artifacts" }))
    expect(screen.queryByText("Source base resume")).not.toBeInTheDocument()
    expect(
      screen.queryByText("No pinned base resume for this build."),
    ).not.toBeInTheDocument()
    const sectionList = document.querySelector(".recommended-report-section-list") as HTMLElement
    expect(sectionList).toBeTruthy()
    const headerLabels = [...sectionList.querySelectorAll(".collapsible-panel-label-wrap")].map(
      el => el.textContent?.trim(),
    )
    expect(headerLabels).toContain("Job Resume")
    expect(headerLabels).toContain("Cover Letter")
    const operativeCalls = mockedApi.mock.calls.filter(([url]) =>
      String(url).includes("/operative/base_resume"),
    )
    expect(operativeCalls).toHaveLength(0)
  })

  it("[bug-repro] empty Artifacts (Generate) must not show Source base resume", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j1599-empty"))
    renderWithProviders(<JobAnalysisReportModal jobId="j1599-empty" onClose={() => {}} />)
    await waitForShell()
    await userEvent.click(within(topTabBar()).getByRole("button", { name: "Artifacts" }))
    expect(screen.queryByText("Source base resume")).not.toBeInTheDocument()
    expect(
      screen.queryByText("No pinned base resume for this build."),
    ).not.toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Generate Artifacts" })).toBeInTheDocument()
  })
})

describe("JobAnalysisReportModal — AST-1695 listing_href title", () => {
  beforeEach(() => mockedApi.mockReset())

  it("job-link line <a> uses listing_href; raw job_link alone is not navigable", async () => {
    installBaseApiMocks(
      mockedApi,
      jobHandler("j1695-a", {
        job_link: "https://jobs.example/stale-column",
        listing_href: "https://jobs.example/listing",
      }),
    )
    renderWithProviders(<JobAnalysisReportModal jobId="j1695-a" onClose={() => {}} />)
    await waitForShell()
    // AST-1873: title plain; listing_href is the job-link line href
    expect(screen.queryByRole("link", { name: "Analyst" })).not.toBeInTheDocument()
    expect(screen.getByRole("link", { name: "https://jobs.example/listing" })).toHaveAttribute(
      "href",
      "https://jobs.example/listing",
    )
  })

  it("null listing_href → plain title span even when job_link is http(s)", async () => {
    installBaseApiMocks(
      mockedApi,
      jobHandler("j1695-b", {
        job_link: "https://jobs.example/apply",
        listing_href: null,
      }),
    )
    renderWithProviders(<JobAnalysisReportModal jobId="j1695-b" onClose={() => {}} />)
    await waitForShell()
    expect(screen.queryByRole("link", { name: "Analyst" })).not.toBeInTheDocument()
    expect(document.querySelector(".recommended-report-title")).toHaveTextContent("Analyst")
  })

  it("non-http listing_href → plain title span", async () => {
    installBaseApiMocks(
      mockedApi,
      jobHandler("j1695-c", {
        listing_href: "not-a-url",
        job_link: "https://jobs.example/apply",
      }),
    )
    renderWithProviders(<JobAnalysisReportModal jobId="j1695-c" onClose={() => {}} />)
    await waitForShell()
    expect(screen.queryByRole("link", { name: "Analyst" })).not.toBeInTheDocument()
  })
})
describe("JobAnalysisReportModal — AST-1704 non-http job_link chrome", () => {
  beforeEach(() => {
    mockedApi.mockReset()
    mockedCopy.mockReset()
    mockedCopy.mockResolvedValue(true)
  })

  it("shows breadcrumb text and plain title when job_link is non-http", async () => {
    const crumb = "From:a@x.com 9/17 14:05 Eastern To:b@y.com"
    installBaseApiMocks(
      mockedApi,
      jobHandler("j-crumb", { job_link: crumb, listing_href: null, state: "RECOMMENDED" }),
    )
    renderWithProviders(<JobAnalysisReportModal jobId="j-crumb" onClose={() => {}} />)
    await waitForShell()
    expect(screen.queryByRole("link", { name: "Analyst" })).not.toBeInTheDocument()
    expect(screen.getByText("Analyst")).toHaveClass("recommended-report-title")
    expect(screen.getByText(crumb)).toHaveClass("recommended-report-job-link-text")
  })
})

describe("JobAnalysisReportModal — AST-1874 Analysis default, list score, Skip", () => {
  beforeEach(() => mockedApi.mockReset())

  const scored = (extra: Record<string, unknown> = {}) => ({
    jd_grades: [{ vector: "Job Description (JD)", grade: "A", reason: "Strong match", confidence: 4 }],
    jd_rubric: [{ code: "JD", label: "Job Description (JD)", importance: 1 }],
    jd_score_breakdown: { earned: 42, possible: 50, max: 60 },
    ...extra,
  })

  function skipHandler(jobId: string, detail: Record<string, unknown>, skipResponse?: Response) {
    return (url: string, init?: RequestInit) => {
      if (url === `/api/jobs/${jobId}/skip` && init?.method === "POST") return skipResponse
      return jobHandler(jobId, detail)(url, init)
    }
  }

  // AC1: per-job reset returns to the first manifest tab (Analysis), not a literal.
  it("switching jobId after selecting Summary returns to Analysis", async () => {
    installBaseApiMocks(mockedApi, (url, init) => jobHandler("j-a")(url, init) ?? jobHandler("j-b")(url, init))
    const { rerender } = renderWithProviders(<JobAnalysisReportModal jobId="j-a" onClose={() => {}} />)
    await waitForShell()
    await openSummaryTab()
    expect(within(topTabBar()).getByRole("button", { name: "Summary" })).toHaveClass("active")
    rerender(<JobAnalysisReportModal jobId="j-b" onClose={() => {}} />)
    await waitFor(() =>
      expect(within(topTabBar()).getByRole("button", { name: "Analysis" })).toHaveClass("active"),
    )
    expect(within(topTabBar()).getByRole("button", { name: "Summary" })).not.toHaveClass("active")
  })

  // AC3: list score (one decimal) in the JD header; absent → segment dropped.
  it("JD header carries the one-decimal list score", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j-s1", scored({ jd_score: 3.66 })))
    renderWithProviders(<JobAnalysisReportModal jobId="j-s1" onClose={() => {}} />)
    await waitForShell()
    expect(
      await screen.findByText("JD Analysis - 3.7 - score: 42 out of 50 possible (60 max total)"),
    ).toBeInTheDocument()
  })

  it("JD header drops the score segment when jd_score is absent", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j-s2", scored()))
    renderWithProviders(<JobAnalysisReportModal jobId="j-s2" onClose={() => {}} />)
    await waitForShell()
    expect(
      await screen.findByText("JD Analysis - score: 42 out of 50 possible (60 max total)"),
    ).toBeInTheDocument()
    expect(screen.queryByText(/JD Analysis - (\u2014|-) /)).not.toBeInTheDocument()
  })

  // AC5: visibility is the server's can_skip only.
  it.each([
    [true, true],
    [false, false],
    [undefined, false],
  ])("can_skip=%s → Skip this Job shown=%s (last in row when shown)", async (canSkip, shown) => {
    installBaseApiMocks(mockedApi, jobHandler("j-v", { can_skip: canSkip }))
    renderWithProviders(<JobAnalysisReportModal jobId="j-v" onClose={() => {}} />)
    await waitForShell()
    const row = document.querySelector(".recommended-report-links") as HTMLElement
    const buttons = within(row).getAllByRole("button")
    if (shown) {
      expect(buttons.at(-1)).toHaveTextContent("Skip this Job")
    } else {
      expect(within(row).queryByRole("button", { name: "Skip this Job" })).not.toBeInTheDocument()
    }
  })

  // AC6: POST /skip → refresh + close once on 200; 409 → server message toast, stays open.
  it("Skip success posts, refreshes once, closes once", async () => {
    const onClose = vi.fn()
    const onRefresh = vi.fn()
    installBaseApiMocks(mockedApi, skipHandler("j-ok", { can_skip: true }, jsonResponse({ ok: true })))
    renderWithProviders(<JobAnalysisReportModal jobId="j-ok" onClose={onClose} onRefresh={onRefresh} />)
    await waitForShell()
    await userEvent.click(screen.getByRole("button", { name: "Skip this Job" }))
    await waitFor(() => expect(onClose).toHaveBeenCalledTimes(1))
    expect(onRefresh).toHaveBeenCalledTimes(1)
    expect(
      mockedApi.mock.calls.filter(([u, i]) => u === "/api/jobs/j-ok/skip" && i?.method === "POST"),
    ).toHaveLength(1)
  })

  it("Skip 409 shows the server message and keeps the modal open", async () => {
    const onClose = vi.fn()
    const onRefresh = vi.fn()
    installBaseApiMocks(
      mockedApi,
      skipHandler(
        "j-409",
        { can_skip: true },
        jsonResponse({ error: "Invalid transition: CANDIDATE_APPLIED -> CANDIDATE_SKIPPED" }, { ok: false, status: 409 }),
      ),
    )
    renderWithProviders(<JobAnalysisReportModal jobId="j-409" onClose={onClose} onRefresh={onRefresh} />)
    await waitForShell()
    await userEvent.click(screen.getByRole("button", { name: "Skip this Job" }))
    expect(
      await screen.findByText("Invalid transition: CANDIDATE_APPLIED -> CANDIDATE_SKIPPED"),
    ).toBeInTheDocument()
    expect(onClose).not.toHaveBeenCalled()
    expect(onRefresh).not.toHaveBeenCalled()
    expect(screen.getByRole("button", { name: "Skip this Job" })).toBeEnabled()
  })
})
