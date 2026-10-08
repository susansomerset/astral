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

// AST-2060: production list payload (GET /api/candidates) never carries rubric rows — only the
// hydrated detail (GET /api/candidates/<id>) does, so modal content must come via the detail fetch.
const LIST = [{ astral_candidate_id: "c1", state: "ACTIVE", candidate_data: { artifacts: {} } }]

const detailWith = (joblist_rubric: unknown[]) =>
  ({
    ok: true,
    json: async () => ({ astral_candidate_id: "c1", candidate_data: { artifacts: { joblist_rubric } } }),
  }) as Response

type Detail = Response | Promise<Response> | (() => Response | Promise<Response>)

// Routes the api mock by URL. Unknown paths keep the list response so providers behave as before.
// A function `detail` is invoked per call — keeps rejections lazy (no unhandled-rejection trip).
function mockApiRoutes({ list = LIST, detail }: { list?: unknown; detail: Detail }) {
  const listResponse = { ok: true, json: async () => list } as Response
  mockedApi.mockImplementation(async (path: string) => {
    if (path === "/api/candidates/c1") return typeof detail === "function" ? detail() : detail
    return listResponse
  })
}

describe("AgentAnalysisHeader", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    mockApiRoutes({
      detail: detailWith([{ label: "Fit", code: "FIT", content: "Rubric body", importance: 8 }]),
    })
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
    expect(await screen.findByText("Rubric body")).toBeInTheDocument()
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
    expect(await screen.findByText("No rubric found for this vector.")).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Close" }))
  })

  it("matches rubric rows by code and handles missing modal content", async () => {
    // Code-only detail row (no label) — content matched by code.
    mockApiRoutes({ detail: detailWith([{ code: "FIT", content: "Body", importance: 8 }]) })
    renderWithProviders(
      <AgentAnalysisHeader
        grades={[{ vector: "fit", grade: "A" }]}
        rubricArtifact="joblist_rubric"
      />,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: "show rubric" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "show rubric" }))
    expect(await screen.findByText("Body")).toBeInTheDocument()
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

  // AST-2060 [bug-repro]: pre-fix, content came from the (never-hydrated) list → instant not-found.
  it("AST-2059: show rubric reads content from hydrated candidate detail, not the list payload", async () => {
    let resolveDetail!: (r: Response) => void
    mockApiRoutes({ detail: new Promise<Response>(r => { resolveDetail = r }) })
    renderWithProviders(
      <AgentAnalysisHeader grades={[{ vector: "fit", grade: "A" }]} rubricArtifact="joblist_rubric" />,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: "show rubric" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "show rubric" }))
    // No not-found flash while the detail fetch is in flight.
    expect(screen.getByText("Loading rubric…")).toBeInTheDocument()
    expect(screen.queryByText("No rubric found for this vector.")).not.toBeInTheDocument()
    resolveDetail(detailWith([{ label: "Fit", code: "FIT", content: "Hydrated body", importance: 8 }]))
    expect(await screen.findByText("Hydrated body")).toBeInTheDocument()
    expect(mockedApi).toHaveBeenCalledWith("/api/candidates/c1")
  })

  it("AST-2059: failed detail fetch ends on the fallback, not stuck loading", async () => {
    let detail: Detail = { ok: false, json: async () => ({}) } as Response
    mockApiRoutes({ detail: () => (typeof detail === "function" ? detail() : detail) })
    renderWithProviders(
      <AgentAnalysisHeader grades={[{ vector: "fit", grade: "A" }]} rubricArtifact="joblist_rubric" />,
    )
    await waitFor(() => expect(screen.getByRole("button", { name: "show rubric" })).toBeInTheDocument())

    // Case 1: !r.ok
    await userEvent.click(screen.getByRole("button", { name: "show rubric" }))
    expect(await screen.findByText("No rubric found for this vector.")).toBeInTheDocument()
    expect(screen.queryByText("Loading rubric…")).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "Close" }))

    // Case 2: rejected fetch — created lazily on the call, after the click.
    detail = () => Promise.reject(new Error("network"))
    await userEvent.click(screen.getByRole("button", { name: "show rubric" }))
    expect(await screen.findByText("No rubric found for this vector.")).toBeInTheDocument()
    expect(screen.queryByText("Loading rubric…")).not.toBeInTheDocument()
  })
})
