import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import ArtifactEditor from "../../../../src/ui/frontend/src/components/ArtifactEditor"
import { STATE_UI_MANIFEST_FIXTURE } from "../fixtures/stateUiManifestFixture"
import { installBaseApiMocks } from "../pages/page-mocks"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

function stateUiManifestResponse(): Response {
  return { ok: true, json: async () => STATE_UI_MANIFEST_FIXTURE } as Response
}

/** AST-902 recovery GETs …/generate/<task>/pending after load; 404 = no-op. */
function pendingNotFoundResponse(): Response {
  return {
    ok: false,
    status: 404,
    json: async () => ({ error: "No recoverable generation" }),
  } as Response
}

function isPendingGenerateUrl(url: string): boolean {
  return /\/api\/candidates\/[^/]+\/generate\/[^/]+\/pending$/.test(url)
}

function mockApis(state = "CONTEXT_READY") {
  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
    if (url === "/api/candidates") {
      return {
        json: async () => [{ astral_candidate_id: "c1", state, candidate_data: {} }],
      } as Response
    }
    if (isPendingGenerateUrl(url)) return pendingNotFoundResponse()
    if (url === "/api/candidates/c1" && !init) {
      return {
        json: async () => ({
          candidate_data: {
            artifacts: {
              rubric: [{ label: "Fit", content: "Body", importance: 5 }],
              resume: [{ label: "Summary", content: "Saved" }],
            },
          },
        }),
      } as Response
    }
    if (url === "/api/shapes/candidates") {
      return {
        json: async () => ({
          detail: {
            resume: [{ key: "summary", label: "Summary" }],
          },
        }),
      } as Response
    }
    if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
      return { ok: true, json: async () => ({}) } as Response
    }
    if (url === "/api/candidates/c1/generate/craft_rubric" && init?.method === "POST") {
      return {
        ok: true,
        status: 200,
        json: async () => ({
          success: true,
          parsed_response: { criteria: [{ label: "Generated", content: "New body" }] },
        }),
      } as Response
    }
    throw new Error(url)
  })
}

describe("ArtifactEditor", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("shows no-candidate and shape error states", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/candidates") {
        return { json: async () => [] } as Response
      }
      if (url === "/api/shapes/candidates") {
        return { json: async () => ({ detail: { resume: [] } }) } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(<ArtifactEditor title="Rubric" artifactKey="rubric" taskKey="craft_rubric" />)
    await waitFor(() => expect(screen.getByText("No candidate selected.")).toBeInTheDocument())

    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "CONTEXT_READY", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1") {
        return { json: async () => ({ candidate_data: { artifacts: {} } }) } as Response
      }
      if (isPendingGenerateUrl(url)) return pendingNotFoundResponse()
      if (url === "/api/shapes/candidates") {
        return { json: async () => ({ detail: { resume: [] } }) } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(
      <ArtifactEditor title="Resume" artifactKey="resume" taskKey="craft_resume" shapesKey="resume" />,
    )
    await waitFor(() => expect(screen.getByText(/Failed to load field definitions/)).toBeInTheDocument())
  })

  it("edits rubric artifacts, regenerates, and saves", async () => {
    mockApis("CONTEXT_READY")
    renderWithProviders(<ArtifactEditor title="Rubric" artifactKey="rubric" taskKey="craft_rubric" />)
    await waitFor(() => expect(screen.getByText("Rubric")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Regenerate" }))
    await userEvent.click(screen.getAllByRole("button", { name: "Regenerate" })[1])
    await waitFor(() => expect(screen.getByText("Generated — review and Save or Cancel")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Saved")).toBeInTheDocument())
  })

  it("AST-645: Generate/Regenerate button uses in-flight class while generating", async () => {
    let resolveGenerate!: (value: Response) => void
    const generatePromise = new Promise<Response>((resolve) => {
      resolveGenerate = resolve
    })
    mockApis("CONTEXT_READY")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "CONTEXT_READY", candidate_data: {} }],
        } as Response
      }
      if (isPendingGenerateUrl(url)) return pendingNotFoundResponse()
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                rubric: [{ label: "Fit", content: "Body", importance: 5 }],
              },
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/generate/craft_rubric" && init?.method === "POST") {
        return generatePromise
      }
      throw new Error(url)
    })
    renderWithProviders(<ArtifactEditor title="Rubric" artifactKey="rubric" taskKey="craft_rubric" />)
    await waitFor(() => expect(screen.getByRole("button", { name: "Regenerate" })).toBeInTheDocument())
    const generateBtn = screen.getByRole("button", { name: "Regenerate" })
    expect(generateBtn).not.toHaveClass("in-flight")
    await userEvent.click(generateBtn)
    await userEvent.click(screen.getAllByRole("button", { name: "Regenerate" })[1])
    await waitFor(() => expect(generateBtn).toHaveClass("in-flight"))
    expect(screen.getByRole("button", { name: "Save" })).not.toHaveClass("in-flight")
    resolveGenerate({
      ok: true,
      json: async () => ({
        success: true,
        parsed_response: { criteria: [{ label: "Generated", content: "New body" }] },
      }),
    } as Response)
    await waitFor(() => expect(generateBtn).not.toHaveClass("in-flight"))
    expect(generateBtn).toHaveClass("save")
  })

  it("supports fixed-shape artifacts and add/remove controls", async () => {
    mockApis("CONTEXT_READY")
    renderWithProviders(
      <ArtifactEditor title="Resume" artifactKey="resume" taskKey="craft_resume" shapesKey="resume" />,
    )
    await waitFor(() => expect(screen.getByDisplayValue("Saved")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Cancel" }))
  })

  it("loads fixed tabs from structureSections without shapes fetch", async () => {
    mockApis("CONTEXT_READY")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "CONTEXT_READY", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                base_resume: { professional_summary: "Struct body", orphan_section: "skip" },
              },
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        return { ok: true, json: async () => ({}) } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(
      <ArtifactEditor
        title="Base Resume Content"
        artifactKey="base_resume"
        taskKey="craft_resume_base"
        useCandidateResumeStructure
        structureSections={[
          { id: "professional_summary", label: "Custom Summary" },
          { id: "technical_skills", label: "Custom Skills" },
        ]}
      />,
    )
    await waitFor(() => expect(screen.getByDisplayValue("Struct body")).toBeInTheDocument())
    expect(screen.queryByDisplayValue("skip")).not.toBeInTheDocument()
    expect(mockedApi.mock.calls.some(([u]) => u === "/api/shapes/candidates")).toBe(false)
  })

  it("job persistence mode loads job resume_content and PUTs on save (AST-553)", async () => {
    const putBodies: { resume_content?: Record<string, string> }[] = []
    installBaseApiMocks(mockedApi, async (url, init) => {
      if (url === "/api/jobs/j1" && !init?.method) {
        return {
          json: async () => ({
            astral_job_id: "j1",
            job_data: { artifacts: { resume_content: { professional_summary: "hello" } } },
          }),
        } as Response
      }
      if (url === "/api/jobs/j1/artifacts/resume_content" && init?.method === "PUT") {
        putBodies.push(JSON.parse(String(init.body)))
        return { ok: true, json: async () => ({ ok: true }) } as Response
      }
      throw new Error(`${url} ${init?.method ?? "GET"}`)
    })
    renderWithProviders(
      <ArtifactEditor
        title="Resume draft"
        artifactKey="resume_content"
        taskKey="craft_resume_base"
        useCandidateResumeStructure
        structureSections={[{ id: "professional_summary", label: "Summary" }]}
        jobPersistence={{ jobId: "j1", artifactKey: "resume_content" }}
      />,
    )
    await waitFor(() => expect(screen.getByText("Resume draft")).toBeInTheDocument())
    expect(screen.queryByRole("button", { name: "Generate" })).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    const field = await screen.findByDisplayValue("hello")
    await userEvent.clear(field)
    await userEvent.type(field, "updated")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Saved")).toBeInTheDocument())
    expect(
      mockedApi.mock.calls.some(
        ([u, init]) => u === "/api/jobs/j1/artifacts/resume_content" && init?.method === "PUT",
      ),
    ).toBe(true)
    expect(putBodies.at(-1)?.resume_content?.professional_summary).toMatch(/updated/)
    // AST-902: jobPersistence must not hit craft pending recovery
    expect(mockedApi.mock.calls.some(([u]) => isPendingGenerateUrl(String(u)))).toBe(false)
  })

  it("AST-902: empty criteria on Generate shows error and clears review mode", async () => {
    mockApis("CONTEXT_READY")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "CONTEXT_READY", candidate_data: {} }],
        } as Response
      }
      if (isPendingGenerateUrl(url)) return pendingNotFoundResponse()
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: { artifacts: { rubric: [{ label: "Fit", content: "Body", importance: 5 }] } },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/generate/craft_rubric" && init?.method === "POST") {
        return {
          ok: true,
          status: 200,
          json: async () => ({ success: true, parsed_response: { criteria: [] } }),
        } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(<ArtifactEditor title="Rubric" artifactKey="rubric" taskKey="craft_rubric" />)
    await waitFor(() => expect(screen.getByRole("button", { name: "Regenerate" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Regenerate" }))
    await userEvent.click(screen.getAllByRole("button", { name: "Regenerate" })[1])
    await waitFor(() =>
      expect(screen.getByText("Generation returned no criteria")).toBeInTheDocument(),
    )
    expect(screen.queryByText("Generated — review and Save or Cancel")).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Save" })).not.toBeInTheDocument()
  })

  it("AST-902: pending recovery loads criteria into review mode", async () => {
    mockApis("CONTEXT_READY")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "CONTEXT_READY", candidate_data: {} }],
        } as Response
      }
      if (url === "/api/candidates/c1/generate/craft_get_rubric/pending") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            success: true,
            recovered: true,
            source: "pending_stash",
            batch_id: "user-craft_get_rubric-x",
            parsed_response: {
              criteria: [{ code: "GT", label: "Recovered Get", content: "From stash", importance: 7 }],
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: { artifacts: { get_rubric: [] } },
          }),
        } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(
      <ArtifactEditor title="Get Job Criteria" artifactKey="get_rubric" taskKey="craft_get_rubric" />,
    )
    await waitFor(() =>
      expect(
        screen.getByText("Recovered completed generation — review and Save or Cancel"),
      ).toBeInTheDocument(),
    )
    expect(screen.getByDisplayValue("From stash")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Save" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument()
  })

  it("AST-902: network interrupt on Generate suggests page-return recovery", async () => {
    mockApis("CONTEXT_READY")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "CONTEXT_READY", candidate_data: {} }],
        } as Response
      }
      if (isPendingGenerateUrl(url)) return pendingNotFoundResponse()
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: { artifacts: { rubric: [{ label: "Fit", content: "Body", importance: 5 }] } },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/generate/craft_rubric" && init?.method === "POST") {
        throw new TypeError("Failed to fetch")
      }
      throw new Error(url)
    })
    renderWithProviders(<ArtifactEditor title="Rubric" artifactKey="rubric" taskKey="craft_rubric" />)
    await waitFor(() => expect(screen.getByRole("button", { name: "Regenerate" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Regenerate" }))
    await userEvent.click(screen.getAllByRole("button", { name: "Regenerate" })[1])
    await waitFor(() =>
      expect(
        screen.getByText(
          "Generation request interrupted — if it finished on the server, return to this page to recover",
        ),
      ).toBeInTheDocument(),
    )
  })

  it("AST-904: Save failure shows server error and keeps review mode", async () => {
    mockApis("CONTEXT_READY")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "CONTEXT_READY", candidate_data: {} }],
        } as Response
      }
      if (isPendingGenerateUrl(url)) return pendingNotFoundResponse()
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: { get_rubric: [{ label: "Fit", content: "Body", importance: 5 }] },
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/generate/craft_get_rubric" && init?.method === "POST") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            success: true,
            parsed_response: {
              criteria: [{ code: "GT", label: "Generated", content: "New body", importance: 5 }],
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        return {
          ok: false,
          status: 400,
          json: async () => ({ error: "criterion content invalid" }),
        } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(
      <ArtifactEditor title="Get Job Criteria" artifactKey="get_rubric" taskKey="craft_get_rubric" />,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: "Regenerate" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Regenerate" }))
    await userEvent.click(screen.getAllByRole("button", { name: "Regenerate" })[1])
    await waitFor(() =>
      expect(screen.getByText("Generated — review and Save or Cancel")).toBeInTheDocument(),
    )
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("criterion content invalid")).toBeInTheDocument())
    expect(screen.queryByText("Save failed")).not.toBeInTheDocument()
    // Review mode retained — Save/Cancel still available
    expect(screen.getByRole("button", { name: "Save" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument()
  })
})
