import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AgentAnalysisHeader from "../../../../src/ui/frontend/src/components/AgentAnalysisHeader"
import { renderWithProviders } from "../test-utils"

// AuthContext registers token/401 hooks on mount — keep named exports (AST-1771 keeper).
vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

describe("AgentAnalysisHeader", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    mockedApi.mockResolvedValue({
      json: async () => [
        {
          astral_candidate_id: "c1",
          state: "ACTIVE",
          candidate_data: {
            artifacts: {
              joblist_rubric: [
                { label: "Fit", code: "FIT", content: "Rubric body", importance: 8 },
              ],
            },
          },
        },
      ],
    } as Response)
  })

  it("renders grades with rubric links and opens the modal", async () => {
    renderWithProviders(
      <AgentAnalysisHeader
        grades={[{ vector: "fit", grade: "A", reason: "because", confidence: 3 }]}
        rubricArtifact="joblist_rubric"
      />,
    )
    await waitFor(() => expect(screen.getByText("because")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "show rubric" }))
    expect(screen.getByText("Rubric body")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Close" }))
  })

  it("falls back to raw vector labels without rubric data", async () => {
    renderWithProviders(
      <AgentAnalysisHeader grades={[{ vector: "raw", grade: "B" }]} />,
    )
    await waitFor(() => expect(screen.getByText("raw")).toBeInTheDocument())
    expect(screen.queryByRole("button", { name: "show rubric" })).not.toBeInTheDocument()
  })

  it("opens the rubric modal with no matching row (null content)", async () => {
    renderWithProviders(
      <AgentAnalysisHeader
        grades={[{ vector: "orphan", grade: "C" }]}
        rubricArtifact="joblist_rubric"
      />,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: "show rubric" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "show rubric" }))
    expect(screen.getByText("No rubric found for this vector.")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Close" }))
  })

  it("matches rubric rows by code and handles missing modal content", async () => {
    mockedApi.mockResolvedValue({
      json: async () => [
        {
          astral_candidate_id: "c1",
          state: "ACTIVE",
          candidate_data: {
            artifacts: {
              joblist_rubric: [{ code: "FIT", content: "Body", importance: 8 }],
            },
          },
        },
      ],
    } as Response)
    renderWithProviders(
      <AgentAnalysisHeader
        grades={[{ vector: "fit", grade: "A" }]}
        rubricArtifact="joblist_rubric"
      />,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: "show rubric" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "show rubric" }))
    expect(screen.getByText("Body")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Close" }))
  })

  it("normalizes an empty vector key when matching rubric rows", async () => {
    renderWithProviders(
      <AgentAnalysisHeader
        grades={[{ vector: "", grade: "D" }]}
        rubricArtifact="joblist_rubric"
      />,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: "show rubric" })).toBeInTheDocument())
  })

  // AST-1771: detail rows share importance+grade order with Recommended header (consult lists EFW first).
  it("AST-1771: detail rows match importance+grade order", async () => {
    const grades = [
      { vector: "Embedded/Firmware/Hardware Domain", grade: "A", confidence: 5, reason: "fit" },
      { vector: "Quality Check", grade: "B", confidence: 4, reason: "ok" },
    ]
    const rubric = [
      { code: "EFW", label: "Embedded/Firmware/Hardware Domain", importance: 1, grade_descriptions: [] },
      { code: "QC", label: "Quality Check", importance: 5, grade_descriptions: [] },
    ]
    renderWithProviders(<AgentAnalysisHeader grades={grades} rubricItems={rubric} />)
    await waitFor(() => expect(document.querySelectorAll(".analysis-vector").length).toBe(2))
    const vectors = Array.from(document.querySelectorAll(".analysis-vector")).map(el => el.textContent ?? "")
    expect(vectors[0]).toMatch(/Quality Check/)
    expect(vectors[1]).toMatch(/Embedded|Firmware/)
  })
})
