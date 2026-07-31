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
  gaze_email: {
    entity_type: null as string | null,
    trigger_state: null as string | null,
    task_group_order: "4000",
    task_group_name: "Job Review",
    task_seq: 2.3,
    task_name: "gaze_email",
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
  always_visible_under_avail_gt0: false,
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
  always_visible_under_avail_gt0: false,
}

/** Shared mailbox shell — zero entity avail, API carve-out flag true (AST-1106). */
const gazeEmailZeroAvailVisible = {
  id: 41,
  candidate_id: null as string | null,
  task_key: "gaze_email",
  entity_type: null as string | null,
  trigger_state: null as string | null,
  freq_hrs: 0,
  min_count: 1,
  batch_size: 1,
  score_floor: null as number | null,
  is_scored: false,
  auto_mode: 0,
  debug: 0,
  skip_cache: 0,
  max_runs: 0,
  last_run_at: null as string | null,
  updated_at: "2026-07-31T00:00:00Z",
  available_count: 0,
  always_visible_under_avail_gt0: true,
}

const candidates = [
  {
    astral_candidate_id: "c1",
    state: "ACTIVE",
    candidate_data: { first: "Ada", last: "One", contact: { timezone: "UTC" } },
  },
  {
    astral_candidate_id: "c2",
    state: "ACTIVE",
    candidate_data: { first: "Betty", last: "Two", contact: { timezone: "UTC" } },
  },
]

describe("AST-1106 gaze_email always visible under Avail gt0", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    vi.useFakeTimers({ shouldAdvanceTime: true })
    vi.spyOn(window, "alert").mockImplementation(() => {})
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  function mockApi(tasks = [scanJobsC1, watchCosZeroAvail, gazeEmailZeroAvailVisible]) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/candidates") {
        return { ok: true, json: async () => candidates } as Response
      }
      if (url === "/api/admin/scheduler/thread_status") {
        return { ok: true, json: async () => ({}) } as Response
      }
      if (url === "/api/admin/dispatch_tasks" && !init?.method) {
        return { ok: true, json: async () => tasks } as Response
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

  it("default Avail gt0 keeps gaze_email (flag) and still hides other zero-Avail rows (§6c)", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    mockApi()
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
    expect(within(await filtersRoot()).getByLabelText("Avail")).toHaveValue("gt0")

    await selectAllCandidatesFilter()
    await waitFor(() => expect(screen.getByText(/Job Review \(.*AUTO\)/)).toBeInTheDocument())
    expect(screen.getByText(/D\. Job Analysis \(.*AUTO\)/)).toBeInTheDocument()
    expect(screen.queryByText(/C\. Company Roster \(.*AUTO\)/)).not.toBeInTheDocument()

    const jr = screen.getByText(/Job Review \(.*AUTO\)/).closest(".collapsible-panel") as HTMLElement
    if (!within(jr).queryByRole("table")) {
      const expandBtn = within(jr).queryByRole("button", { name: "Expand section" })
      if (expandBtn) await userEvent.click(expandBtn)
    }
    await waitFor(() => expect(within(jr).getByText("gaze_email")).toBeVisible())
    // Null-safe Candidate cell (Ada follow-up): expand+render with candidate_id null must not throw.
    const gazeRow = within(jr).getByText("gaze_email").closest("tr") as HTMLElement
    const cells = within(gazeRow).getAllByRole("cell")
    // Candidate column is immediately before Avail (both may show "—" for mailbox shells).
    expect(cells[cells.length - 3].textContent).toBe("—")
  }, 20000)

  it("zero-Avail without always_visible flag stays omitted under default gt0", async () => {
    localStorage.setItem("astral_selected_candidate", "c1")
    mockApi([scanJobsC1, watchCosZeroAvail])
    renderWithProviders(<ScheduledActions />)
    await waitFor(() => expect(screen.getByText("Scheduled Actions")).toBeInTheDocument())
    await selectAllCandidatesFilter()
    await waitFor(() => expect(screen.getByText(/D\. Job Analysis \(.*AUTO\)/)).toBeInTheDocument())
    expect(screen.queryByText(/C\. Company Roster \(.*AUTO\)/)).not.toBeInTheDocument()
    expect(screen.queryByText(/Job Review \(.*AUTO\)/)).not.toBeInTheDocument()
  }, 20000)
})
