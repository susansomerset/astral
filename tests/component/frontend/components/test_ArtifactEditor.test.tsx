import { act, fireEvent, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
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
    if (url === "/api/ui_config") return uiConfigResponse()
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
    if (url === "/api/ui_config") return uiConfigResponse()
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

// AST-2051 / AST-2068: resume editors (structure mode / jobPersistence) blur-save bodies — no timer;
// header Save/Cancel renders only during Generate review.

/** Blur the focused field (jsdom fires a bubbling focusout → dep-body onBlur) and settle the PUT chain. */
async function blurToSave() {
  await act(async () => {
    ;(document.activeElement as HTMLElement | null)?.blur()
  })
}

function expectNoHeaderSaveCancel() {
  expect(screen.queryByRole("button", { name: "Save" })).not.toBeInTheDocument()
  expect(screen.queryByRole("button", { name: "Cancel" })).not.toBeInTheDocument()
}

const okResponse = () => ({ ok: true, json: async () => ({}) }) as Response

/** JAR Job Resume editor: job j1 resume_content with one professional_summary body. */
function mockJobResume(putBodies: { resume_content?: Record<string, string> }[]) {
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
      return okResponse()
    }
    throw new Error(`${url} ${init?.method ?? "GET"}`)
  })
}

function renderJobResume(onSaved?: () => void) {
  return renderWithProviders(
    <ArtifactEditor
      title="Resume draft"
      artifactKey="resume_content"
      taskKey="craft_resume_base"
      jobPersistence={{ jobId: "j1", artifactKey: "resume_content", onSaved }}
    />,
  )
}

describe("ArtifactEditor", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it("shows no-candidate and shape error states", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/ui_config") return uiConfigResponse()
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
      if (url === "/api/ui_config") return uiConfigResponse()
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
      if (url === "/api/ui_config") return uiConfigResponse()
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

  it("job persistence mode loads job resume_content and autosaves PUT (AST-553 / AST-2051)", async () => {
    const putBodies: { resume_content?: Record<string, string> }[] = []
    mockJobResume(putBodies)
    renderJobResume()
    await waitFor(() => expect(screen.getByText("Resume draft")).toBeInTheDocument())
    expect(screen.queryByRole("button", { name: "Generate" })).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    const field = await screen.findByDisplayValue("hello")
    await userEvent.clear(field)
    await userEvent.type(field, "updated")
    expectNoHeaderSaveCancel()
    await blurToSave()
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
      if (url === "/api/ui_config") return uiConfigResponse()
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
      if (url === "/api/ui_config") return uiConfigResponse()
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
      if (url === "/api/ui_config") return uiConfigResponse()
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
      if (url === "/api/ui_config") return uiConfigResponse()
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
      if (url === "/api/ui_config") return uiConfigResponse()
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


  it("AST-1200: candidate criteria expand-all shows prompt bodies without chevron click", async () => {
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/ui_config") return uiConfigResponse()
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
      if (url === "/api/ui_config") return uiConfigResponse()
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
      if (url === "/api/ui_config") return uiConfigResponse()
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

  it("AST-1253: empty chain Generate POSTs generate_artifacts without modal", async () => {
    const posts: string[] = []
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/ui_config") return uiConfigResponse()
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
      if (url === "/api/ui_config") return uiConfigResponse()
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

  it("AST-1410: no-snapshot Cancel re-GETs last-saved tabs without location.reload", async () => {
    const reload = vi.fn()
    vi.stubGlobal("location", { ...window.location, reload })
    let jobGets = 0
    // AST-2051: shapesKey job editors (cover letter / application responses) are the only non-review Cancel path left.
    installBaseApiMocks(mockedApi, async (url, init) => {
      if (url === "/api/shapes/candidates") {
        return { json: async () => ({ detail: { cover_letter: [{ key: "body", label: "Body" }] } }) } as Response
      }
      if (url === "/api/jobs/j1" && !init?.method) {
        jobGets += 1
        const body = jobGets === 1 ? "hello" : "from-server"
        return {
          json: async () => ({
            astral_job_id: "j1",
            job_data: { artifacts: { cover_letter: { body } } },
          }),
        } as Response
      }
      throw new Error(`${url} ${init?.method ?? "GET"}`)
    })
    renderWithProviders(
      <ArtifactEditor
        title="Cover letter"
        artifactKey="cover_letter"
        taskKey="draft_cover_letter"
        shapesKey="cover_letter"
        jobPersistence={{ jobId: "j1", artifactKey: "cover_letter" }}
      />,
    )
    await waitFor(() => expect(screen.getByText("Cover letter")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    const field = await screen.findByDisplayValue("hello")
    await userEvent.clear(field)
    await userEvent.type(field, "dirty local")
    await userEvent.click(screen.getByRole("button", { name: "Cancel" }))
    await waitFor(() => expect(screen.getByDisplayValue("from-server")).toBeInTheDocument())
    expect(screen.getByText("Cover letter")).toBeInTheDocument()
    expect(screen.queryByText("Loading...")).not.toBeInTheDocument()
    expect(reload).not.toHaveBeenCalled()
    expect(jobGets).toBe(2)
    vi.unstubAllGlobals()
  })

  // AST-1480: structure-mode body hydrate + edit loop (chrome vs body split; label-churn; JAR overlay)
  it("AST-1593: job_resume load uses hydrated current leaf body", async () => {
    const putBodies: { job_resume?: Record<string, string> }[] = []
    installBaseApiMocks(mockedApi, async (url, init) => {
      if (url === "/api/jobs/j1" && !init?.method) {
        return {
          json: async () => ({
            astral_job_id: "j1",
            job_data: {
              artifacts: {
                job_resume: { professional_summary: "From catalog current" },
                resume_content: { professional_summary: "legacy sibling" },
              },
            },
          }),
        } as Response
      }
      if (url === "/api/jobs/j1/artifacts/job_resume" && init?.method === "PUT") {
        putBodies.push(JSON.parse(String(init.body)))
        return { ok: true, json: async () => ({ ok: true }) } as Response
      }
      throw new Error(`${url} ${init?.method ?? "GET"}`)
    })
    renderWithProviders(
      <ArtifactEditor
        title="Job Resume"
        artifactKey="job_resume"
        taskKey="craft_resume_base"
        jobPersistence={{ jobId: "j1", artifactKey: "job_resume" }}
      />,
    )
    await waitFor(() => expect(screen.getByText("Job Resume")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    const field = await screen.findByDisplayValue("From catalog current")
    expect(field).not.toBeDisabled()
    await userEvent.clear(field)
    await userEvent.type(field, "Edited JAR")
    expectNoHeaderSaveCancel()
    await blurToSave()
    await waitFor(() => expect(screen.getByText("Saved")).toBeInTheDocument())
    expect(putBodies.at(-1)?.job_resume?.professional_summary).toMatch(/Edited JAR/)
  })

  it("AST-1480: rubric free-form body edit PUTs edited content", async () => {
    // Radia fix-now: bodiesEditable must stay true in rubric chrome mode (not only fixedFields/jobPersistence).
    const putBodies: { artifacts?: { rubric?: { label?: string; content?: string }[] } }[] = []
    mockApis("ACTIVE_SEARCH")
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
      if (url === "/api/ui_config") return uiConfigResponse()
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
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        putBodies.push(JSON.parse(String(init.body)))
        return { ok: true, json: async () => ({}) } as Response
      }
      throw new Error(url)
    })
    const { unmount } = renderWithProviders(
      <ArtifactEditor title="Rubric" artifactKey="rubric" taskKey="craft_rubric" />,
    )
    const field = await screen.findByDisplayValue("Body")
    expect(field).not.toBeDisabled()
    await userEvent.clear(field)
    await userEvent.type(field, "Edited free-form body")
    // Rubric chrome uses autosave / unmount flush (no explicit Save button outside review)
    unmount()
    await waitFor(() => expect(putBodies.length).toBeGreaterThan(0))
    expect(
      putBodies.some(b =>
        (b.artifacts?.rubric ?? []).some(r => /Edited free-form body/.test(String(r.content ?? ""))),
      ),
    ).toBe(true)
  })

  // --- AST-2051 resume editor autosave contract (AST-2056 bug-repro) ---

  it("AST-2051 / AST-2068: jobPersistence Job Resume body edit saves one PUT on blur (none while typing), no header Save/Cancel", async () => {
    const puts: { resume_content?: Record<string, string> }[] = []
    mockJobResume(puts)
    renderJobResume()
    await userEvent.click(await screen.findByRole("button", { name: "Expand section" }))
    await userEvent.type(await screen.findByDisplayValue("hello"), " edited")
    expectNoHeaderSaveCancel()
    expect(screen.getByText("Unsaved changes")).toBeInTheDocument()
    expect(puts).toHaveLength(0)
    await blurToSave()
    await waitFor(() => expect(puts).toHaveLength(1))
    expect(puts[0].resume_content?.professional_summary).toBe("hello edited")
    await waitFor(() => expect(screen.getByText("All changes saved")).toBeInTheDocument())
  })

  it("AST-2051 [bug-repro]: jobPersistence autosave skips onSaved; unmount flush calls it", async () => {
    const puts: { resume_content?: Record<string, string> }[] = []
    const onSaved = vi.fn()
    mockJobResume(puts)
    const { unmount } = renderJobResume(onSaved)
    await userEvent.click(await screen.findByRole("button", { name: "Expand section" }))
    const field = await screen.findByDisplayValue("hello")
    await userEvent.type(field, " a")
    await blurToSave()
    await waitFor(() => expect(puts).toHaveLength(1))
    await waitFor(() => expect(screen.getByText("All changes saved")).toBeInTheDocument())
    // JAR's onSaved re-GETs and remounts the editor — autosave ticks must not trigger it.
    expect(onSaved).not.toHaveBeenCalled()
    await userEvent.type(field, " b")
    unmount()
    await waitFor(() => expect(puts).toHaveLength(2))
    expect(puts[1].resume_content?.professional_summary).toBe("hello a b")
    await waitFor(() => expect(onSaved).toHaveBeenCalledTimes(1))
  })

  // --- AST-2068 version arrows on the JAR cover letter (job route) ---

  it("AST-2068 AC4: JAR cover letter arrows step back via the job route; a failed move toasts and keeps the body", async () => {
    const bodies: Record<string, string> = { "u-1": "letter v1", "u-2": "letter v2" }
    let current = "u-2"
    let failMove = false
    const map = () => ({
      "u-1": { created_at: "t", current: current === "u-1" ? 1 : 0, position: 1 },
      "u-2": { created_at: "t", current: current === "u-2" ? 1 : 0, position: 2 },
    })
    const base = "/api/jobs/j1/artifacts/job.artifacts.cover_letter"
    installBaseApiMocks(mockedApi, async (url, init) => {
      if (url === "/api/shapes/candidates") {
        return { json: async () => ({ detail: { cover_letter: [{ key: "body", label: "Body" }] } }) } as Response
      }
      if (url === "/api/jobs/j1" && !init?.method) {
        return {
          json: async () => ({ astral_job_id: "j1", job_data: { artifacts: { cover_letter: { body: bodies[current] } } } }),
        } as Response
      }
      if (url === `${base}/versions`) return { ok: true, json: async () => ({ versions: map() }) } as Response
      if (url === `${base}/current` && init?.method === "PUT") {
        if (failMove) return { ok: false, status: 400, json: async () => ({ error: "not a version" }) } as Response
        current = JSON.parse(String(init.body)).artifact_uuid
        return { ok: true, json: async () => ({ current, versions: map() }) } as Response
      }
      throw new Error(`${url} ${init?.method ?? "GET"}`)
    })
    renderWithProviders(
      <ArtifactEditor
        title="Cover letter"
        artifactKey="cover_letter"
        taskKey="draft_cover_letter"
        shapesKey="cover_letter"
        jobPersistence={{ jobId: "j1", artifactKey: "cover_letter" }}
      />,
    )
    expect(await screen.findByText("2 of 2")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Next version" })).toBeDisabled()
    await userEvent.click(screen.getByRole("button", { name: "Expand section" }))
    await screen.findByDisplayValue("letter v2")
    await userEvent.click(screen.getByRole("button", { name: "Previous version" }))
    await screen.findByDisplayValue("letter v1")
    expect(screen.getByText("1 of 2")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Previous version" })).toBeDisabled()
    // Server rejects the move → error toast, body and indicator unchanged.
    failMove = true
    await userEvent.click(screen.getByRole("button", { name: "Next version" }))
    expect(await screen.findByText("not a version")).toBeInTheDocument()
    expect(screen.getByDisplayValue("letter v1")).toBeInTheDocument()
    expect(screen.getByText("1 of 2")).toBeInTheDocument()
  })
})
