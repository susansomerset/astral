import { fireEvent, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import AdminVectorFeedback from "../../../../src/ui/frontend/src/pages/AdminVectorFeedback"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"
import { resetStytchTestState } from "../stytchMock"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

vi.mock("../../../../src/ui/frontend/src/assets/astral_logo.png", () => ({
  default: "logo.png",
}))

const mockedApi = vi.mocked(api)

const detailRow = {
  vector_feedback_id: "vf-1",
  candidate_id: "c1",
  batch_id: "batch-725",
  task_key: "grade_get",
  feedback_type: "relevance",
  value: "A",
  value_label: "Aligned",
  vector_code: "G1",
  vector_label: "G1",
  vector_assessment_header: "5 - G1 fit (G1)",
  vector_content: "Criterion body text",
  created_at: "2026-06-01T12:00:00Z",
  agent_data_id: null,
}

const summaryRow = {
  code: "G1",
  label: "G1",
  importance: 5,
  batch_count: 1,
  feedback_row_count: 3,
  relevance_dist: "A:1",
  clarity_dist: "O:1",
  verdict_dist: "K:1",
}

describe("AdminVectorFeedback", () => {
  beforeEach(() => {
    localStorage.clear()
    resetStytchTestState()
    mockedApi.mockReset()
  })

  it("loads summary and detail tables with filters and batch modal", async () => {
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url.startsWith("/api/admin/vector_feedback/task_keys")) {
        return { json: async () => ["grade_get", "evaluate_jd"] } as Response
      }
      if (url.startsWith("/api/admin/vector_feedback/summary")) {
        return { json: async () => [summaryRow] } as Response
      }
      if (url.startsWith("/api/admin/vector_feedback")) {
        return { json: async () => [detailRow] } as Response
      }
      if (url.startsWith("/api/agent_data/")) {
        return { json: async () => [] } as Response
      }
      if (url.includes("/api/admin/timesheets")) {
        return { json: async () => [] } as Response
      }
    })

    renderWithProviders(<AdminVectorFeedback />, {
      router: { initialEntries: ["/admin/vector_feedback?candidate_id=c1&owner_task_key=grade_get"] },
    })

    await waitFor(() => expect(screen.getByText("Per-vector summary (active rubric)")).toBeInTheDocument())
    expect(screen.getByText("Vector feedback rows")).toBeInTheDocument()
    expect(screen.getByText("vf-1")).toBeInTheDocument()
    expect(screen.getByText("5 - G1 fit (G1)")).toBeInTheDocument()
    expect(screen.getByRole("columnheader", { name: "Assessment" })).toBeInTheDocument()

    fireEvent.blur(screen.getByLabelText("From"), { target: { value: "2026-05-01" } })
    fireEvent.blur(screen.getByLabelText("To"), { target: { value: "2026-06-14" } })

    const batchBtn = await screen.findByRole("button", { name: "batch-725" })
    await userEvent.click(batchBtn)
    await waitFor(() => expect(screen.getByText(/Tokens & Cost/)).toBeInTheDocument())
  }, 15000)

  it("shows summary placeholder without candidate and task", async () => {
    installBaseApiMocks(mockedApi, async (url: string) => {
      if (url.startsWith("/api/admin/vector_feedback/task_keys")) {
        return { json: async () => [] } as Response
      }
      if (url.startsWith("/api/admin/vector_feedback")) {
        return { json: async () => [] } as Response
      }
    })

    renderWithProviders(<AdminVectorFeedback />, {
      router: { initialEntries: ["/admin/vector_feedback"] },
    })

    await waitFor(() =>
      expect(screen.getByText("Select candidate and rubric task to see per-vector aggregation.")).toBeInTheDocument(),
    )
    expect(screen.getByText("No vector feedback rows match filters.")).toBeInTheDocument()
  })
})
