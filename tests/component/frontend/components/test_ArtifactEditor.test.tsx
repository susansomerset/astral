import { fireEvent, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import React from "react"
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

const EXPERIENCE_UI_CONFIG = {
  experience_job_ui_fields: [
    { key: "company", label: "Company" },
    { key: "title", label: "Title" },
    { key: "dates", label: "Dates" },
    { key: "location", label: "Location" },
    { key: "accomplishments", label: "Accomplishments" },
  ],
  unsupported_resume_structure_message: "unsupported resume structure, please regenerate",
}

function uiConfigResponse(): Response {
  return { ok: true, json: async () => EXPERIENCE_UI_CONFIG } as Response
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

function mockApis(state = "ACTIVE_SEARCH") {
  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
    if (url === "/api/system/ui_config") return uiConfigResponse()
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


/** Base Resume + legacy string experience under a candidate state (AST-1375 escape hatch). */
function mockBaseResumeUnsupported(state: string) {
  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
    if (url === "/api/system/ui_config") return uiConfigResponse()
    if (url === "/api/candidates") {
      return { json: async () => [{ astral_candidate_id: "c1", state, candidate_data: {} }] } as Response
    }
    if (isPendingGenerateUrl(url)) return pendingNotFoundResponse()
    if (url === "/api/candidates/c1" && !init) {
      return {
        json: async () => ({
          candidate_data: {
            artifacts: {
              base_resume: { experience: "legacy prose blob" },
            },
          },
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
      if (url === "/api/system/ui_config") return uiConfigResponse()
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
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }] } as Response
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
    mockApis("ACTIVE_SEARCH")
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
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }],
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
    expect(generateBtn).toHaveClass("btn")
    expect(generateBtn).toHaveClass("primary")
  })

  it("supports fixed-shape artifacts and add/remove controls", async () => {
    mockApis("ACTIVE_SEARCH")
    renderWithProviders(
      <ArtifactEditor title="Resume" artifactKey="resume" taskKey="craft_resume" shapesKey="resume" />,
    )
    await waitFor(() => expect(screen.getByDisplayValue("Saved")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Cancel" }))
  })

  it("loads fixed tabs from structureSections without shapes fetch", async () => {
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }] } as Response
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
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }],
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
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }],
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

  it("AST-905: skips pending recovery when loaded criteria already have content", async () => {
    mockApis("ACTIVE_SEARCH")
    let pendingCalls = 0
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }],
        } as Response
      }
      if (url === "/api/candidates/c1/generate/craft_get_rubric/pending") {
        pendingCalls += 1
        // Would overwrite if applied — must not be fetched when content exists
        return {
          ok: true,
          status: 200,
          json: async () => ({
            success: true,
            recovered: true,
            source: "pending_stash",
            parsed_response: {
              criteria: [{ code: "GT", label: "Overwrite", content: "SHOULD NOT APPLY", importance: 1 }],
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                get_rubric: [{ label: "Existing Get", content: "Keep me", importance: 5 }],
              },
            },
          }),
        } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(
      <ArtifactEditor title="Get Job Criteria" artifactKey="get_rubric" taskKey="craft_get_rubric" />,
    )
    await waitFor(() => expect(screen.getByDisplayValue("Keep me")).toBeInTheDocument())
    // Empty-only gate: no pending fetch when tabs already have content
    expect(pendingCalls).toBe(0)
    expect(
      screen.queryByText("Recovered completed generation — review and Save or Cancel"),
    ).not.toBeInTheDocument()
    expect(screen.queryByDisplayValue("SHOULD NOT APPLY")).not.toBeInTheDocument()
  })

  it("AST-902: network interrupt on Generate suggests page-return recovery", async () => {
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }],
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
    // Non-chain craft_rubric keeps ad-hoc regenerate → review → Save (chain keys hand off).
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }],
        } as Response
      }
      if (isPendingGenerateUrl(url)) return pendingNotFoundResponse()
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: { rubric: [{ label: "Fit", content: "Body", importance: 5 }] },
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/generate/craft_rubric" && init?.method === "POST") {
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
      <ArtifactEditor title="Rubric" artifactKey="rubric" taskKey="craft_rubric" />,
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

  it("AST-996/AST-1351: experience job array loads in ExperienceJobsEditor and Saves as array", async () => {
    const jobs = [
      {
        company: "Acme Corp",
        title: "Engineer",
        dates: "2020-2023",
        location: "Remote",
        accomplishments: ["Shipped widgets"],
      },
    ]
    const putBodies: { artifacts?: { base_resume?: Record<string, unknown> } }[] = []
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                base_resume: {
                  professional_summary: "Summary body",
                  experience: jobs,
                },
              },
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        putBodies.push(JSON.parse(String(init.body)))
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
          { id: "experience", label: "Custom Jobs" },
        ]}
      />,
    )
    await waitFor(() => expect(screen.getByDisplayValue("Summary body")).toBeInTheDocument())
    // AST-1351/1382: collapsible header (not Role N / JSON textarea)
    expect(screen.getByText(/Acme Corp, Engineer \/ 2020-2023/)).toBeInTheDocument()
    await userEvent.click(screen.getByText(/Acme Corp, Engineer \/ 2020-2023/))
    expect(screen.getByDisplayValue("Acme Corp")).toBeInTheDocument()
    expect(screen.getByDisplayValue("Engineer")).toBeInTheDocument()
    expect(screen.queryByDisplayValue(/"company": "Acme Corp"/)).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Saved")).toBeInTheDocument())
    expect(putBodies.at(-1)?.artifacts?.base_resume?.experience).toEqual(jobs)
    expect(typeof putBodies.at(-1)?.artifacts?.base_resume?.professional_summary).toBe("string")
  })

  it("AST-1351: legacy string experience shows unsupported notice and Save aborts", async () => {
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                base_resume: {
                  experience: "legacy prose blob",
                },
              },
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        throw new Error("Save should not fire")
      }
      throw new Error(url)
    })
    renderWithProviders(
      <ArtifactEditor
        title="Base Resume Content"
        artifactKey="base_resume"
        taskKey="craft_resume_base"
        useCandidateResumeStructure
        structureSections={[{ id: "experience", label: "Custom Jobs" }]}
      />,
    )
    await waitFor(() =>
      expect(screen.getByText("unsupported resume structure, please regenerate")).toBeInTheDocument(),
    )
    expect(screen.getByDisplayValue("legacy prose blob")).toBeDisabled()
    expect(screen.queryByText("Role 1")).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() =>
      expect(screen.getAllByText("unsupported resume structure, please regenerate").length).toBeGreaterThan(0),
    )
    expect(mockedApi.mock.calls.some(([u, init]) => u === "/api/candidates/c1/data" && init?.method === "PUT")).toBe(
      false,
    )
  })


  it("AST-1375: unsupported experience outside generate allowlist shows Regenerate", async () => {
    // REQUESTED_ARTIFACTS_ERROR is not in artifact_generate_states — escape hatch must surface Regenerate.
    mockBaseResumeUnsupported("REQUESTED_ARTIFACTS_ERROR")
    renderWithProviders(
      <ArtifactEditor
        title="Base Resume Content"
        artifactKey="base_resume"
        taskKey="craft_resume_base"
        useCandidateResumeStructure
        structureSections={[{ id: "experience", label: "Custom Jobs" }]}
      />,
    )
    await waitFor(() =>
      expect(screen.getByText("unsupported resume structure, please regenerate")).toBeInTheDocument(),
    )
    expect(screen.getByRole("button", { name: "Regenerate" })).toBeInTheDocument()
  })

  it("AST-1375: inflight hide states keep Generate/Regenerate hidden when unsupported", async () => {
    for (const state of ["REQUESTED_ARTIFACTS", "REQUESTED_ARTIFACTS_RETRY"] as const) {
      mockBaseResumeUnsupported(state)
      const { unmount } = renderWithProviders(
        <ArtifactEditor
          title="Base Resume Content"
          artifactKey="base_resume"
          taskKey="craft_resume_base"
          useCandidateResumeStructure
          structureSections={[{ id: "experience", label: "Custom Jobs" }]}
        />,
      )
      await waitFor(() =>
        expect(screen.getByText("unsupported resume structure, please regenerate")).toBeInTheDocument(),
      )
      expect(screen.queryByRole("button", { name: "Regenerate" })).not.toBeInTheDocument()
      expect(screen.queryByRole("button", { name: "Generate" })).not.toBeInTheDocument()
      unmount()
    }
  })

  it("AST-1375: Regenerate confirms then POSTs craft_resume_base; array experience clears notice", async () => {
    const jobs = [
      {
        company: "Acme Corp",
        title: "Engineer",
        dates: "2020-2023",
        location: "Remote",
        accomplishments: ["Shipped widgets"],
      },
    ]
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [
            { astral_candidate_id: "c1", state: "REQUESTED_ARTIFACTS_ERROR", candidate_data: {} },
          ],
        } as Response
      }
      if (isPendingGenerateUrl(url)) return pendingNotFoundResponse()
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: { base_resume: { experience: "legacy prose blob" } },
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/generate/craft_resume_base" && init?.method === "POST") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            success: true,
            parsed_response: { experience: jobs },
          }),
        } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(
      <ArtifactEditor
        title="Base Resume Content"
        artifactKey="base_resume"
        taskKey="craft_resume_base"
        useCandidateResumeStructure
        structureSections={[{ id: "experience", label: "Custom Jobs" }]}
      />,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: "Regenerate" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Regenerate" }))
    await userEvent.click(screen.getAllByRole("button", { name: "Regenerate" })[1])
    await waitFor(() => expect(screen.getByText("Generated — review and Save or Cancel")).toBeInTheDocument())
    expect(
      mockedApi.mock.calls.some(
        ([u, init]) => u === "/api/candidates/c1/generate/craft_resume_base" && init?.method === "POST",
      ),
    ).toBe(true)
    expect(screen.queryByText("unsupported resume structure, please regenerate")).not.toBeInTheDocument()
    expect(screen.getByText(/Acme Corp, Engineer \/ 2020-2023/)).toBeInTheDocument()
    await userEvent.click(screen.getByText(/Acme Corp, Engineer \/ 2020-2023/))
    expect(screen.getByDisplayValue("Acme Corp")).toBeInTheDocument()
  })

  it("AST-1375: valid job-array experience stays allowlist-only (no escape)", async () => {
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [
            { astral_candidate_id: "c1", state: "REQUESTED_ARTIFACTS_ERROR", candidate_data: {} },
          ],
        } as Response
      }
      if (isPendingGenerateUrl(url)) return pendingNotFoundResponse()
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                base_resume: {
                  experience: [
                    {
                      company: "Acme",
                      title: "Dev",
                      dates: "2021",
                      location: "Remote",
                      accomplishments: ["Shipped"],
                    },
                  ],
                },
              },
            },
          }),
        } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(
      <ArtifactEditor
        title="Base Resume Content"
        artifactKey="base_resume"
        taskKey="craft_resume_base"
        useCandidateResumeStructure
        structureSections={[{ id: "experience", label: "Custom Jobs" }]}
      />,
    )
    await waitFor(() => expect(screen.getByText(/Acme, Dev \/ 2021/)).toBeInTheDocument())
    expect(screen.queryByRole("button", { name: "Regenerate" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Generate" })).not.toBeInTheDocument()
  })

  it("AST-1200: candidate criteria expand-all shows prompt bodies without chevron click", async () => {
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }],
        } as Response
      }
      if (isPendingGenerateUrl(url)) return pendingNotFoundResponse()
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                joblist_rubric: [
                  { label: "Title fit", content: "Prompt A body", importance: 5 },
                  { label: "Scope", content: "Prompt B body", importance: 4 },
                ],
              },
            },
          }),
        } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(
      <ArtifactEditor title="Job List Criteria" artifactKey="joblist_rubric" taskKey="craft_joblist_rubric" />,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: "Regenerate" })).toBeInTheDocument())
    const a = await screen.findByDisplayValue("Prompt A body")
    const b = screen.getByDisplayValue("Prompt B body")
    // Expand-all: CollapsiblePanel bodies not hidden (DOM contract for AC1)
    expect(a.closest(".collapsible-panel-body")).not.toHaveAttribute("hidden")
    expect(b.closest(".collapsible-panel-body")).not.toHaveAttribute("hidden")
    expect(screen.getAllByRole("button", { name: "Collapse section" })).toHaveLength(2)
  })

  it("AST-1200: collapse one criterion stays closed while typing in another", async () => {
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }],
        } as Response
      }
      if (isPendingGenerateUrl(url)) return pendingNotFoundResponse()
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                joblist_rubric: [
                  { label: "Title fit", content: "Prompt A body", importance: 5 },
                  { label: "Scope", content: "Prompt B body", importance: 4 },
                ],
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
      <ArtifactEditor title="Job List Criteria" artifactKey="joblist_rubric" taskKey="craft_joblist_rubric" />,
    )
    // Wait for one-shot expand-all seed before interacting
    await waitFor(() => expect(screen.getAllByRole("button", { name: "Collapse section" })).toHaveLength(2))
    const a = screen.getByDisplayValue("Prompt A body")
    const aBody = a.closest(".collapsible-panel-body")
    expect(aBody).not.toHaveAttribute("hidden")
    await userEvent.click(screen.getAllByRole("button", { name: "Collapse section" })[0])
    await waitFor(() => expect(aBody).toHaveAttribute("hidden"))
    const b = screen.getByDisplayValue("Prompt B body")
    await userEvent.type(b, " more")
    expect(aBody).toHaveAttribute("hidden")
    expect(b.closest(".collapsible-panel-body")).not.toHaveAttribute("hidden")
  })

  it("AST-1200: jobPersistence dict tabs stay expand-one (bodies hidden until expand)", async () => {
    installBaseApiMocks(mockedApi, async (url, init) => {
      if (url === "/api/jobs/j1" && !init?.method) {
        return {
          json: async () => ({
            astral_job_id: "j1",
            job_data: {
              artifacts: {
                proposed_answers: { q1: "Answer one", q2: "Answer two" },
              },
            },
          }),
        } as Response
      }
      throw new Error(`${url} ${init?.method ?? "GET"}`)
    })
    renderWithProviders(
      <ArtifactEditor
        title="Application Questions"
        artifactKey="proposed_answers"
        taskKey="craft_proposed_answers"
        jobPersistence={{ jobId: "j1", artifactKey: "proposed_answers" }}
      />,
    )
    await waitFor(() => expect(screen.getByText("Application Questions")).toBeInTheDocument())
    // Expand-one: ▶ chevrons; bodies start with hidden (not criteria expand-all)
    expect(screen.getAllByRole("button", { name: "Expand section" }).length).toBeGreaterThanOrEqual(1)
    const answer = screen.getByDisplayValue("Answer one")
    expect(answer.closest(".collapsible-panel-body")).toHaveAttribute("hidden")
    await userEvent.click(screen.getAllByRole("button", { name: "Expand section" })[0])
    await waitFor(() =>
      expect(screen.getByDisplayValue("Answer one").closest(".collapsible-panel-body")).not.toHaveAttribute("hidden"),
    )
  })

  it("AST-1200: empty criteria page still shows New Criterion editor expanded", async () => {
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }],
        } as Response
      }
      if (isPendingGenerateUrl(url)) return pendingNotFoundResponse()
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: { artifacts: { joblist_rubric: [] } },
          }),
        } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(
      <ArtifactEditor title="Job List Criteria" artifactKey="joblist_rubric" taskKey="craft_joblist_rubric" />,
    )
    // Wait for expand-all seed on the empty New Criterion affordance
    await waitFor(() => expect(screen.getByRole("button", { name: "Collapse section" })).toBeInTheDocument())
    expect(screen.getByText(/New Criterion/)).toBeInTheDocument()
    const area = screen.getByPlaceholderText("Enter new criterion…")
    expect(area.closest(".collapsible-panel-body")).not.toHaveAttribute("hidden")
  })

  it("AST-1200: structure mode stays expand-one (not criteria expand-all)", async () => {
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }],
        } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                base_resume: {
                  professional_summary: "Summary body",
                  technical_skills: "Skills body",
                },
              },
            },
          }),
        } as Response
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
          { id: "professional_summary", label: "Summary" },
          { id: "technical_skills", label: "Skills" },
        ]}
      />,
    )
    await waitFor(() => expect(screen.getByText("Base Resume Content")).toBeInTheDocument())
    // Structure sets fixedFields → rubricMode false → expand-one
    await waitFor(() =>
      expect(screen.getAllByRole("button", { name: "Expand section" }).length).toBeGreaterThanOrEqual(1),
    )
    const summary = screen.getByDisplayValue("Summary body")
    expect(summary.closest(".collapsible-panel-body")).toHaveAttribute("hidden")
    await userEvent.click(screen.getAllByRole("button", { name: "Expand section" })[0])
    await waitFor(() =>
      expect(screen.getByDisplayValue("Summary body").closest(".collapsible-panel-body")).not.toHaveAttribute("hidden"),
    )
  })

  it("AST-1253: empty chain Generate POSTs generate_artifacts without modal", async () => {
    const posts: string[] = []
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }],
        } as Response
      }
      if (isPendingGenerateUrl(url)) return pendingNotFoundResponse()
      if (url === "/api/candidates/c1" && !init) {
        return { json: async () => ({ candidate_data: { artifacts: { get_rubric: [] } } }) } as Response
      }
      if (url === "/api/candidates/c1/generate_artifacts" && init?.method === "POST") {
        posts.push(url)
        return { ok: true, json: async () => ({ ok: true, state: "REQUESTED_ARTIFACTS" }) } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(
      <ArtifactEditor title="Get Job Criteria" artifactKey="get_rubric" taskKey="craft_get_rubric" />,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: "Generate" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Generate" }))
    expect(screen.queryByText(/Reset all artifact rubrics/i)).not.toBeInTheDocument()
    await waitFor(() => expect(posts).toEqual(["/api/candidates/c1/generate_artifacts"]))
    await waitFor(() =>
      expect(screen.getByText("Artifacts build requested — watch Execution History")).toBeInTheDocument(),
    )
  })

  it("AST-1253: Regenerate lists hop labels; Yes posts generate_artifacts; No cancels", async () => {
    const posts: string[] = []
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return {
          json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }],
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
      if (url === "/api/candidates/c1/generate_artifacts" && init?.method === "POST") {
        posts.push(url)
        return { ok: true, json: async () => ({ ok: true, state: "REQUESTED_ARTIFACTS" }) } as Response
      }
      throw new Error(url)
    })
    renderWithProviders(
      <ArtifactEditor title="Get Job Criteria" artifactKey="get_rubric" taskKey="craft_get_rubric" />,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: "Regenerate" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Regenerate" }))
    expect(screen.getByRole("heading", { name: /Reset all artifact rubrics/i })).toBeInTheDocument()
    expect(screen.getByText(/Job Description Criteria/)).toBeInTheDocument()
    expect(screen.getByText(/Like Job Criteria/)).toBeInTheDocument()
    expect(screen.getByText(/Do Job Criteria/)).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "No" }))
    expect(posts).toEqual([])
    expect(screen.queryByRole("heading", { name: /Reset all artifact rubrics/i })).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Regenerate" }))
    await userEvent.click(screen.getByRole("button", { name: "Yes" }))
    await waitFor(() => expect(posts).toEqual(["/api/candidates/c1/generate_artifacts"]))
  })

  it("AST-1382 [bug-repro]: content Save bundles resume_structure format (prior free_prose)", async () => {
    const putBodies: { artifacts?: { base_resume?: unknown; resume_structure?: { sections?: Record<string, { format?: string; page_break_policy?: string }> } } }[] = []
    const catalog = {
      body_formats: ["free_prose", "word_cloud", "bullet_list"],
      required_ids: ["prior_experience"],
      contact_ids: [] as string[],
      extra_id_pattern: "^extra_",
      reserved_extra_ids: [] as string[],
      new_extra_default_format: "bullet_list",
      page_break_policies: ["normal", "page_break_before", "avoid_split"],
      page_break_policy_labels: {
        normal: "Flow uninterrupted",
        page_break_before: "New page before",
        avoid_split: "Keep block together",
      },
      page_break_policy_default: "avoid_split",
    }
    const structureRows = [
      {
        id: "prior_experience",
        title: "Prior Experience",
        enabled: true,
        order: 0,
        format: "free_prose",
        job_agent_editable: true,
        required: true,
        format_locked: false,
        page_break_policy: "avoid_split",
      },
    ]
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                base_resume: { prior_experience: "Earlier ops and delivery." },
              },
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        putBodies.push(JSON.parse(String(init.body)))
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
        structureSections={[{ id: "prior_experience", label: "Prior Experience" }]}
        structureCatalog={catalog}
        structureRows={structureRows}
        onStructureRowsChange={() => {}}
        onStructureSave={() => {}}
      />,
    )
    await waitFor(() => expect(screen.getByDisplayValue("Earlier ops and delivery.")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Saved")).toBeInTheDocument())
    const arts = putBodies.at(-1)?.artifacts
    expect(arts?.resume_structure?.sections?.prior_experience?.format).toBe("free_prose")
    expect(arts?.resume_structure?.sections?.prior_experience?.page_break_policy).toBe("avoid_split")
    expect(arts?.base_resume).toEqual({ prior_experience: "Earlier ops and delivery." })
  })

  it("AST-1476: page-break dropdown + content Save and Save sections persist policy", async () => {
    const putBodies: { artifacts?: { resume_structure?: { sections?: Record<string, { page_break_policy?: string }> } } }[] = []
    const structureSaves: { id: string; page_break_policy: string }[][] = []
    const catalog = {
      body_formats: ["free_prose", "bullet_list"],
      required_ids: ["professional_summary"],
      contact_ids: [] as string[],
      extra_id_pattern: "^extra_",
      reserved_extra_ids: [] as string[],
      new_extra_default_format: "bullet_list",
      page_break_policies: ["normal", "page_break_before", "avoid_split"],
      page_break_policy_labels: {
        normal: "Flow uninterrupted",
        page_break_before: "New page before",
        avoid_split: "Keep block together",
      },
      page_break_policy_default: "avoid_split",
    }
    const initialRows = [
      {
        id: "professional_summary",
        title: "Summary",
        enabled: true,
        order: 0,
        format: "free_prose",
        job_agent_editable: true,
        required: true,
        format_locked: false,
        page_break_policy: "avoid_split",
      },
    ]
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/system/ui_config") return uiConfigResponse()
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "ACTIVE_SEARCH", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: { base_resume: { professional_summary: "Summary body" } },
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        putBodies.push(JSON.parse(String(init.body)))
        return { ok: true, json: async () => ({}) } as Response
      }
      throw new Error(url)
    })
    function Harness() {
      const [rows, setRows] = React.useState(initialRows)
      return (
        <ArtifactEditor
          title="Base Resume Content"
          artifactKey="base_resume"
          taskKey="craft_resume_base"
          useCandidateResumeStructure
          structureSections={[{ id: "professional_summary", label: "Summary" }]}
          structureCatalog={catalog}
          structureRows={rows}
          onStructureRowsChange={setRows}
          onStructureSave={next => {
            structureSaves.push(next.map(r => ({ id: r.id, page_break_policy: r.page_break_policy })))
          }}
        />
      )
    }
    renderWithProviders(<Harness />)
    await waitFor(() => expect(screen.getByDisplayValue("Summary body")).toBeInTheDocument())
    const pageBreak = screen.getByRole("combobox", { name: "Page break" })
    expect(Array.from(pageBreak.querySelectorAll("option")).map(o => o.textContent)).toEqual([
      "Flow uninterrupted",
      "New page before",
      "Keep block together",
    ])
    await userEvent.selectOptions(pageBreak, "page_break_before")
    await userEvent.click(screen.getByRole("button", { name: "Save sections" }))
    expect(structureSaves.at(-1)?.[0]?.page_break_policy).toBe("page_break_before")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Saved")).toBeInTheDocument())
    expect(
      putBodies.at(-1)?.artifacts?.resume_structure?.sections?.professional_summary?.page_break_policy,
    ).toBe("page_break_before")
  })

  it("AST-1410: no-snapshot Cancel re-GETs last-saved tabs without location.reload", async () => {
    const reload = vi.fn()
    vi.stubGlobal("location", { ...window.location, reload })
    let jobGets = 0
    installBaseApiMocks(mockedApi, async (url, init) => {
      if (url === "/api/jobs/j1" && !init?.method) {
        jobGets += 1
        const summary = jobGets === 1 ? "hello" : "from-server"
        return {
          json: async () => ({
            astral_job_id: "j1",
            job_data: { artifacts: { resume_content: { professional_summary: summary } } },
          }),
        } as Response
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
    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    const field = await screen.findByDisplayValue("hello")
    await userEvent.clear(field)
    await userEvent.type(field, "dirty local")
    await userEvent.click(screen.getByRole("button", { name: "Cancel" }))
    await waitFor(() => expect(screen.getByDisplayValue("from-server")).toBeInTheDocument())
    expect(screen.getByText("Resume draft")).toBeInTheDocument()
    expect(screen.queryByText("Loading...")).not.toBeInTheDocument()
    expect(reload).not.toHaveBeenCalled()
    expect(jobGets).toBe(2)
    vi.unstubAllGlobals()
  })
})
