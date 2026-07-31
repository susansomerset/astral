import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import ScheduledActions from "../../../../src/ui/frontend/src/pages/AdminScheduledActions"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const taskKeysConfig = {
  scan_jobs: {
    entity_type: "job",
    trigger_state: "NEW",
    task_group_order: "D. Job Analysis",
    task_group_name: "D. Job Analysis",
    task_seq: 2,
    task_name: "scan_jobs",
    is_scored: true,
  },
  watch_cos: {
    entity_type: "company",
    trigger_state: "WATCH",
    task_group_order: "C. Company Roster",
    task_group_name: "C. Company Roster",
    task_seq: 1,
    task_name: "watch_cos",
    is_scored: false,
  },
}

const defaultScoreFloorOptions = Array.from({ length: 21 }, (_, i) => (i * 0.5).toFixed(2))

const scanJobsC1 = {
  id: 10,
  candidate_id: "c1",
  task_key: "scan_jobs",
  entity_type: "job",
  trigger_state: "NEW",
  freq_hrs: 1,
  min_count: 1,
  batch_size: 5,
  score_floor: 1.5,
  is_scored: true,
  auto_mode: 1,
  debug: 0,
  skip_cache: 0,
  max_runs: 0,
  last_run_at: "2026-05-01T00:00:00Z",
  updated_at: "2026-05-01T00:00:00Z",
  available_count: 12,
}

const watchCosZeroAvail = {
  id: 12,
  candidate_id: "c2",
  task_key: "watch_cos",
  entity_type: null as string | null,
  trigger_state: null as string | null,
  freq_hrs: 0,
  min_count: 1,
  batch_size: null as number | null,
  score_floor: null as number | null,
  is_scored: false,
  auto_mode: 1,
  debug: 0,
  skip_cache: 0,
  max_runs: 0,
  last_run_at: "2026-05-01T00:00:00Z",
  updated_at: "2026-05-01T00:00:00Z",
  available_count: 0,
}

const candidatesBadTz = [
  {
    astral_candidate_id: "c1",
    state: "ACTIVE",
    candidate_data: { first: "Ada", last: "One", contact: { timezone: "Not/AZone" } },
  },
  {
    astral_candidate_id: "c2",
    state: "ACTIVE",
    candidate_data: { first: "Betty", last: "Two", contact: { timezone: "UTC" } },
  },
]

describe("AST-1104 Candidate All + Avail All blank-page survival", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    vi.useFakeTimers({ shouldAdvanceTime: true })
    vi.spyOn(window, "alert").mockImplementation(() => {})
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  function mockApi() {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { ok: true, json: async () => candidatesBadTz } as Response
      }
      if (url === "/api/admin/scheduler/thread_status") {
        return { ok: true, json: async () => ({}) } as Response
      }
      if (url === "/api/admin/dispatch_tasks" && !init?.method) {
        return { ok: true, json: async () => [scanJobsC1, watchCosZeroAvail] } as Response
      }
      if (url === "/api/admin/dispatch_tasks/task_keys") {
        return { ok: true, json: async () => taskKeysConfig } as Response
      }
      if (url === "/api/admin/dispatch_tasks/state_options") {
        return { ok: true, json: async () => ({ job: ["NEW"], company: ["WATCH"], candidate: [] }) } as Response
      }
      if (url === "/api/admin/dispatch_tasks/score_floor_options") {
        return { ok: true, json: async () => ({ values: defaultScoreFloorOptions }) } as Response
      }
    })
  }

  async function filtersRoot(): Promise<HTMLElement> {
    await waitFor(() => expect(document.querySelector(".admin-filters")).toBeTruthy())
    return document.querySelector(".admin-filters") as HTMLElement
  }

  async function selectAllCandidatesFilter() {
    const root = await filtersRoot()
    await waitFor(() => expect(within(root).getByLabelText("Candidate").querySelectorAll("option").length).toBeGreaterThan(1))
    await userEvent.selectOptions(within(root).getByLabelText("Candidate"), "")
  }

  async function selectAvailAll() {
    const root = await filtersRoot()
    await userEvent.selectOptions(within(root).getByLabelText("Avail"), "")
  }

  it("keeps chrome and zero-Avail Last Run rows mounted under Candidate All + Avail All", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    mockApi()
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
    expect(within(await filtersRoot()).getByLabelText("Avail")).toHaveValue("gt0")

    await selectAllCandidatesFilter()
    await selectAvailAll()
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
    expect(within(await filtersRoot()).getByLabelText("Avail")).toHaveValue("")

    const rosterHeading = await waitFor(() => screen.getByText(/C\. Company Roster \(.*AUTO\)/))
    const rosterPanel = rosterHeading.closest(".collapsible-panel") as HTMLElement
    if (!within(rosterPanel).queryByRole("table")) {
      const expandBtn = within(rosterPanel).queryByRole("button", { name: "Expand section" })
      if (expandBtn) await userEvent.click(expandBtn)
    }
    await waitFor(() => expect(within(rosterPanel).getByText("watch_cos")).toBeVisible())
    // Last Run via <Time> + fmtTime UTC fallback (invalid nav timezone must not blank the page)
    expect(within(rosterPanel).getByRole("table").textContent).toMatch(/5\/1\/26/)
    expect(screen.getByText(/D\. Job Analysis \(.*AUTO\)/)).toBeInTheDocument()
  }, 20000)

  it("switching Avail gt0 ↔ All with Candidate All keeps Scheduled Actions mounted", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    mockApi()
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
    await selectAllCandidatesFilter()
    await selectAvailAll()
    await waitFor(() => expect(screen.getByText(/C\. Company Roster \(.*AUTO\)/)).toBeInTheDocument())
    expect(screen.getByText("Scheduled Actions")).toBeInTheDocument()

    await userEvent.selectOptions(within(await filtersRoot()).getByLabelText("Avail"), "gt0")
    await waitFor(() => expect(screen.queryByText(/C\. Company Roster \(.*AUTO\)/)).not.toBeInTheDocument())
    expect(screen.getByText("Scheduled Actions")).toBeInTheDocument()

    await selectAvailAll()
    await waitFor(() => expect(screen.getByText(/C\. Company Roster \(.*AUTO\)/)).toBeInTheDocument())
    expect(screen.getByText("Scheduled Actions")).toBeInTheDocument()
  }, 20000)
})
