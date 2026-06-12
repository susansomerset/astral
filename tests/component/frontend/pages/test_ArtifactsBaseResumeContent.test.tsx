import { fireEvent, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import ArtifactsBaseResumeContent from "../../../../src/ui/frontend/src/pages/ArtifactsBaseResumeContent"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("ArtifactsBaseResumeContent", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { json: async () => [{ astral_candidate_id: "c1", state: "CONTEXT_READY", candidate_data: {} }] } as Response
      }
      if (url === "/api/candidates/c1" && !init) {
        return {
          json: async () => ({
            candidate_data: {
              artifacts: {
                base_resume: [{ label: "Summary", content: "Saved summary" }],
              },
            },
          }),
        } as Response
      }
      if (url === "/api/system/ui_config") {
        return {
          json: async () => ({
            column_types: {},
            base_resume_accent_palette: ["#112233", "#445566"],
          }),
        } as Response
      }
      if (url === "/api/shapes/candidates") {
        return {
          json: async () => ({
            detail: {
              base_resume_structure: [{ key: "summary", label: "Summary" }],
            },
          }),
        } as Response
      }
      if (url === "/api/candidates/c1/data" && init?.method === "PUT") {
        return { ok: true, json: async () => ({}) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
  })

  it("renders base resume artifact editor", async () => {
    renderWithProviders(<ArtifactsBaseResumeContent />)
    await waitFor(() => expect(screen.getByRole("heading", { name: "Base Resume Content" })).toBeInTheDocument())
    expect(screen.getByDisplayValue("Saved summary")).toBeInTheDocument()
  })

  it("renders accent swatches and saves selection", async () => {
    renderWithProviders(<ArtifactsBaseResumeContent />)
    await waitFor(() => expect(screen.getByRole("group", { name: "Resume accent color" })).toBeInTheDocument())
    fireEvent.click(screen.getByRole("button", { name: "#112233" }))
    await waitFor(() => expect(screen.getByText("Accent color saved")).toBeInTheDocument())
    const putCall = mockedApi.mock.calls.find(
      ([url, init]) => url === "/api/candidates/c1/data" && init?.method === "PUT",
    )
    expect(putCall).toBeTruthy()
    const body = JSON.parse(String(putCall?.[1]?.body))
    expect(body.artifacts.base_resume.accent_color).toBe("#112233")
  })
})
