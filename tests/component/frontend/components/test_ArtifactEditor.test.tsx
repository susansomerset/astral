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

function mockApis(state = "CONTEXT_READY") {
  mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
    if (url === "/api/state_ui_manifest") return stateUiManifestResponse()
    if (url === "/api/candidates") {
      return {
        json: async () => [{ astral_candidate_id: "c1", state, candidate_data: {} }],
      } as Response
    }
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
        jobPersistence={{ jobId: "j1" }}
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
  })
})
