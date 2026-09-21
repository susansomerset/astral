import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { useCandidate } from "../../../../src/ui/frontend/src/contexts/CandidateContext"
import api from "../../../../src/ui/frontend/src/lib/api"
import JobsMeteorites from "../../../../src/ui/frontend/src/pages/JobsMeteorites"
import { renderWithProviders } from "../test-utils"
import { candidateId, installBaseApiMocks, jsonResponse } from "./page-mocks"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const LIST_COLUMNS = [
  { key: "state", label: "State", sortable: true },
  { key: "job_title", label: "Title", sortable: true },
  { key: "employer_name", label: "Employer", sortable: true },
]

const ROW_A = {
  id: 11,
  candidate_id: "c1",
  state: "READY",
  job_title: "Title A",
  employer_name: "Employer A",
  classify_outcome: "link",
  link: "https://a.example/j",
  astral_job_id: "job-a",
}

const ROW_B = {
  id: 22,
  candidate_id: "c2",
  state: "NEW",
  job_title: "Title B",
  employer_name: "Employer B",
  classify_outcome: null,
  link: "not-http",
  astral_job_id: null,
}

const DETAIL_SECTIONS = [
  { section_id: "meteorite_timestamps", nav_label: "Timestamps", default_expanded: true },
  { section_id: "meteorite_link", nav_label: "Link", default_expanded: true },
  { section_id: "meteorite_content", nav_label: "Content", default_expanded: true },
  { section_id: "meteorite_provenance", nav_label: "Provenance", default_expanded: false },
  { section_id: "meteorite_job", nav_label: "Linked Job", default_expanded: true },
]

function CandidateSelectC2() {
  const { setSelectedId } = useCandidate()
  return (
    <button type="button" onClick={() => setSelectedId("c2")}>
      Select c2
    </button>
  )
}

function listUrl(cid: string) {
  return `/api/candidates/${encodeURIComponent(cid)}/meteorites`
}

describe("JobsMeteorites — AST-1749", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
  })

  it("renders page title and loads candidate-scoped list from API columns", async () => {
    installBaseApiMocks(mockedApi, (url) => {
      if (url === listUrl(candidateId)) {
        return jsonResponse({ columns: LIST_COLUMNS, meteorites: [ROW_A] })
      }
      return undefined
    })
    renderWithProviders(<JobsMeteorites />)
    await waitFor(() => expect(screen.getByText("Meteorites")).toBeInTheDocument())
    await waitFor(() => expect(screen.getByText("Title A")).toBeInTheDocument())
    expect(screen.getByText("Employer A")).toBeInTheDocument()
    expect(mockedApi).toHaveBeenCalledWith(listUrl(candidateId))
    // Read-only: no mutate verbs on meteorite paths
    const mutate = mockedApi.mock.calls.filter(
      ([u, init]) =>
        typeof u === "string" &&
        u.includes("meteorite") &&
        init &&
        typeof init === "object" &&
        "method" in init &&
        ["POST", "PUT", "PATCH", "DELETE"].includes(String((init as RequestInit).method)),
    )
    expect(mutate).toHaveLength(0)
  })

  it("empty honesty — zero rows shows empty message, not placeholders", async () => {
    installBaseApiMocks(mockedApi, (url) => {
      if (url === listUrl(candidateId)) {
        return jsonResponse({ columns: LIST_COLUMNS, meteorites: [] })
      }
      return undefined
    })
    renderWithProviders(<JobsMeteorites />)
    await waitFor(() => expect(screen.getByText("No meteorites yet")).toBeInTheDocument())
    expect(screen.queryByText("Title A")).not.toBeInTheDocument()
  })

  it("candidate switch refetches and drops prior candidate rows", async () => {
    const user = userEvent.setup()
    installBaseApiMocks(mockedApi, (url) => {
      if (url === "/api/candidates") {
        return jsonResponse([
          { astral_candidate_id: "c1", state: "ACTIVE", candidate_data: {} },
          { astral_candidate_id: "c2", state: "ACTIVE", candidate_data: {} },
        ])
      }
      if (url === listUrl("c1")) {
        return jsonResponse({ columns: LIST_COLUMNS, meteorites: [ROW_A] })
      }
      if (url === listUrl("c2")) {
        return jsonResponse({ columns: LIST_COLUMNS, meteorites: [ROW_B] })
      }
      return undefined
    })
    renderWithProviders(
      <>
        <CandidateSelectC2 />
        <JobsMeteorites />
      </>,
    )
    await waitFor(() => expect(screen.getByText("Title A")).toBeInTheDocument())
    await user.click(screen.getByRole("button", { name: "Select c2" }))
    await waitFor(() => expect(screen.getByText("Title B")).toBeInTheDocument())
    expect(screen.queryByText("Title A")).not.toBeInTheDocument()
    expect(mockedApi).toHaveBeenCalledWith(listUrl("c2"))
  })

  it("row click opens detail modal with content and metadata", async () => {
    const user = userEvent.setup()
    installBaseApiMocks(mockedApi, (url) => {
      if (url === listUrl(candidateId)) {
        return jsonResponse({ columns: LIST_COLUMNS, meteorites: [ROW_A] })
      }
      if (url === "/api/meteorites/11") {
        return jsonResponse({
          sections: DETAIL_SECTIONS,
          meteorite: {
            id: 11,
            candidate_id: "c1",
            state: "READY",
            content: '{"ok":true}',
            classify_outcome: "link",
            link: "https://a.example/j",
            astral_job_id: "job-a",
            job_title: "Title A",
            employer_name: "Employer A",
            created_at: "2026-01-01T00:00:00Z",
            updated_at: "2026-01-02T00:00:00Z",
            state_changed_at: "2026-01-03T00:00:00Z",
            source_kind: "email",
            source_id: "mid-1",
            error: null,
            estelle_notified_at: null,
          },
        })
      }
      return undefined
    })
    renderWithProviders(<JobsMeteorites />)
    await waitFor(() => expect(screen.getByText("Title A")).toBeInTheDocument())
    await user.click(screen.getByText("Title A"))
    await waitFor(() => expect(screen.getByText("Timestamps")).toBeInTheDocument())
    expect(screen.getByText("created_at: 2026-01-01T00:00:00Z")).toBeInTheDocument()
    expect(screen.getByText("classify_outcome: link")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "https://a.example/j" })).toHaveAttribute(
      "href",
      "https://a.example/j",
    )
    expect(screen.getByRole("link", { name: /Open job job-a/ })).toHaveAttribute(
      "href",
      "/jobs/detail/job-a",
    )
    expect(mockedApi).toHaveBeenCalledWith("/api/meteorites/11")
  })
})
