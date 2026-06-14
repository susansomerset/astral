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

describe("JobAnalysisReportModal — AST-565 tabbed Recommended report", () => {
  beforeEach(() => mockedApi.mockReset())

  it("renders summary and phase tabs with upshot on Job Summary", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j565"))
    renderWithProviders(<JobAnalysisReportModal jobId="j565" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByText("Strong thematic fit.")).toBeInTheDocument())
    const rail = document.querySelector(".side-tab-list")!
    expect(rail).toHaveTextContent("Job Summary")
    expect(rail).toHaveTextContent("Job Description")
    expect(rail).toHaveTextContent("JD")
    expect(screen.getByText("Noteworthy Caveats")).toBeInTheDocument()
    expect(screen.getByText("Remote only")).toBeInTheDocument()
  })

  it("shows full JD on Job Description tab", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j565"))
    renderWithProviders(<JobAnalysisReportModal jobId="j565" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByText("Strong thematic fit.")).toBeInTheDocument())
    const rail = document.querySelector(".side-tab-list") as HTMLElement
    await userEvent.click(within(rail).getByText("Job Description"))
    expect(await screen.findByText("Full JD body text")).toBeInTheDocument()
  })

  it("shows Estelle take_jd above consult on JD phase tab", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j565"))
    renderWithProviders(<JobAnalysisReportModal jobId="j565" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByText("Strong thematic fit.")).toBeInTheDocument())
    const rail = document.querySelector(".side-tab-list") as HTMLElement
    const jdTab = Array.from(rail.querySelectorAll(".side-tab-item")).find(el => el.textContent?.includes("JD"))
    await userEvent.click(jdTab!)
    expect(await screen.findByText("JD phase thought")).toBeInTheDocument()
  })

  it("shows grade dots on phase tab labels when grades exist", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j565"))
    renderWithProviders(<JobAnalysisReportModal jobId="j565" onClose={() => {}} />)
    await waitFor(() => expect(document.querySelector(".recommended-report-tab-label .grade-dot")).toBeTruthy())
  })

  it("shows company name as site link and copyable profile links", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j565"))
    renderWithProviders(<JobAnalysisReportModal jobId="j565" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByRole("link", { name: "Globex" })).toHaveAttribute(
      "href",
      "https://globex.example",
    ))
    expect(screen.getByRole("heading", { name: "Analyst" })).toHaveClass("modal-title")
    expect(document.querySelector(".recommended-report-title")).toBeNull()
    expect(screen.getByRole("button", { name: "Email" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "LinkedIn" })).toBeInTheDocument()
  })

  it("shows phase tabs when legacy upshot omits take_jd", async () => {
    const legacy = { ...fullUpshot() }
    delete (legacy as { take_jd?: string }).take_jd
    installBaseApiMocks(mockedApi, (url, init) =>
      jobHandler("j565", { job_data: { job_description: "JD", analysis_upshot: legacy, jd_grades: [] } })(
        url,
        init,
      ),
    )
    renderWithProviders(<JobAnalysisReportModal jobId="j565" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByText("Strong thematic fit.")).toBeInTheDocument())
    const rail = document.querySelector(".side-tab-list")!
    expect(rail).toHaveTextContent("JD")
    expect(rail).toHaveTextContent("DO")
  })

  it("shows Generate Artifacts primary action for RECOMMENDED", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j565/generate_artifacts" && init?.method === "POST") {
        return jsonResponse({ ok: true, state: "BUILD_ARTIFACTS" })
      }
      return jobHandler("j565")(url, init)
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j565" onClose={() => {}} />)
    const btn = await screen.findByRole("button", { name: "Generate Artifacts" })
    await userEvent.click(btn)
    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith("/api/jobs/j565/generate_artifacts", { method: "POST" }),
    )
  })

  it("AST-645: Generate Artifacts primary action uses in-flight class while Working", async () => {
    let resolveGenerate!: (value: Response) => void
    const generatePromise = new Promise<Response>((resolve) => {
      resolveGenerate = resolve
    })
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j565/generate_artifacts" && init?.method === "POST") {
        return generatePromise
      }
      return jobHandler("j565")(url, init)
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j565" onClose={() => {}} />)
    const btn = await screen.findByRole("button", { name: "Generate Artifacts" })
    expect(btn).not.toHaveClass("in-flight")
    await userEvent.click(btn)
    await waitFor(() => expect(btn).toHaveClass("in-flight"))
    expect(btn).toHaveTextContent("Working…")
    resolveGenerate(jsonResponse({ ok: true, state: "BUILD_ARTIFACTS" }))
    await waitFor(() => expect(btn).not.toHaveClass("in-flight"))
  })

  it("opens job_link via Apply on CANDIDATE_REVIEW", async () => {
    const openSpy = vi.spyOn(window, "open").mockImplementation(() => null)
    installBaseApiMocks(mockedApi, jobHandler("j-ready", { state: "CANDIDATE_REVIEW" }))
    renderWithProviders(<JobAnalysisReportModal jobId="j-ready" onClose={() => {}} />)
    await userEvent.click(await screen.findByRole("button", { name: "Apply" }))
    expect(openSpy).toHaveBeenCalledWith("https://jobs.example/apply", "_blank", "noopener,noreferrer")
    openSpy.mockRestore()
  })

  it("shows empty summary when analysis_upshot is absent", async () => {
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
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j-empty" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByText("No analysis upshot on file.")).toBeInTheDocument())
    expect(screen.queryByText("DO")).not.toBeInTheDocument()
  })

  it("shows Resume artifact tab when resume_content exists", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j-review" && !init) {
        return jsonResponse({
          astral_job_id: "j-review",
          job_title: "Role",
          company: "Co",
          state: "CANDIDATE_REVIEW",
          state_changed_at: "2026-01-03T00:00:00Z",
          job_data: {
            job_description: "JD",
            analysis_upshot: fullUpshot(),
            artifacts: { resume_content: { professional_summary: "Draft text" } },
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
    renderWithProviders(<JobAnalysisReportModal jobId="j-review" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByText("Resume")).toBeInTheDocument())
    await userEvent.click(screen.getByText("Resume"))
    await waitFor(() => expect(screen.queryByText("Loading resume structure…")).not.toBeInTheDocument())
    await userEvent.click(await screen.findByRole("button", { name: "Expand section" }))
    expect(await screen.findByDisplayValue("Draft text")).toBeInTheDocument()
  })

  it("shows artifact tabs when resume_content exists (any state)", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j-rec" && !init) {
        return jsonResponse({
          astral_job_id: "j-rec",
          job_title: "Role",
          company: "Co",
          state: "RECOMMENDED",
          state_changed_at: null,
          job_data: {
            job_description: "JD",
            analysis_upshot: fullUpshot(),
            artifacts: { resume_content: { professional_summary: "Visible draft" } },
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
    renderWithProviders(<JobAnalysisReportModal jobId="j-rec" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByText("Resume")).toBeInTheDocument())
  })
})

describe("JobAnalysisReportModal — AST-581 Preview Materials", () => {
  beforeEach(() => mockedApi.mockReset())

  it("shows Preview Materials on CANDIDATE_REVIEW", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j-581-review" && !init) {
        return jsonResponse({
          astral_job_id: "j-581-review",
          job_title: "Role",
          company: "Co",
          state: "CANDIDATE_REVIEW",
          state_changed_at: "2026-01-03T00:00:00Z",
          job_data: {
            job_description: "JD",
            analysis_upshot: fullUpshot(),
            artifacts: { resume_content: { professional_summary: "Draft" } },
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
    renderWithProviders(<JobAnalysisReportModal jobId="j-581-review" onClose={() => {}} />)
    expect(await screen.findByRole("button", { name: "Preview Materials" })).toBeInTheDocument()
  })

  it("hides Preview Materials on RECOMMENDED without artifacts", async () => {
    installBaseApiMocks(mockedApi, jobHandler("j-581-rec"))
    renderWithProviders(<JobAnalysisReportModal jobId="j-581-rec" onClose={() => {}} />)
    await waitFor(() => expect(screen.getByText("Strong thematic fit.")).toBeInTheDocument())
    expect(screen.queryByRole("button", { name: "Preview Materials" })).not.toBeInTheDocument()
  })

  it("opens preview modal with Resume tab iframe", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j-581-open" && !init) {
        return jsonResponse({
          astral_job_id: "j-581-open",
          job_title: "Role",
          company: "Co",
          state: "CANDIDATE_REVIEW",
          state_changed_at: null,
          job_data: {
            job_description: "JD",
            analysis_upshot: fullUpshot(),
            artifacts: { resume_content: { professional_summary: "x" } },
          },
        })
      }
      if (url === `/api/candidates/${baseCandidate.astral_candidate_id}/resume_structure`) {
        return jsonResponse({ sections: [], accent_color: null })
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j-581-open" onClose={() => {}} />)
    await userEvent.click(await screen.findByRole("button", { name: "Preview Materials" }))
    expect(await screen.findByRole("heading", { name: "Preview Materials" })).toBeInTheDocument()
    const iframe = document.querySelector("iframe.materials-preview-iframe") as HTMLIFrameElement
    expect(iframe?.src).toContain("/candidate/resume/j-581-open")
  })

  it("shows Cover Letter tab when cover_letter has content", async () => {
    installBaseApiMocks(mockedApi, (url, init) => {
      if (url === "/api/jobs/j-581-cover" && !init) {
        return jsonResponse({
          astral_job_id: "j-581-cover",
          job_title: "Role",
          company: "Co",
          state: "CANDIDATE_REVIEW",
          state_changed_at: null,
          job_data: {
            job_description: "JD",
            analysis_upshot: fullUpshot(),
            artifacts: {
              resume_content: { professional_summary: "x" },
              cover_letter: { Letter: "Hello" },
            },
          },
        })
      }
      if (url === `/api/candidates/${baseCandidate.astral_candidate_id}/resume_structure`) {
        return jsonResponse({ sections: [], accent_color: null })
      }
      return undefined
    })
    renderWithProviders(<JobAnalysisReportModal jobId="j-581-cover" onClose={() => {}} />)
    await userEvent.click(await screen.findByRole("button", { name: "Preview Materials" }))
    await userEvent.click(await screen.findByRole("button", { name: "Cover Letter" }))
    const iframe = document.querySelector("iframe.materials-preview-iframe") as HTMLIFrameElement
    expect(iframe?.src).toContain("/candidate/cover/j-581-cover")
  })
})
