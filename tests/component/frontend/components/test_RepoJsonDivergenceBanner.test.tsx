import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import RepoJsonDivergenceBanner from "../../../../src/ui/frontend/src/components/RepoJsonDivergenceBanner"
import { UserPromptProvider } from "../../../../src/ui/frontend/src/components/UserPrompt"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

function divergedStatus(tableKey: "agent" | "agent_task") {
  return {
    agent: {
      diverged: tableKey === "agent",
      repo_relative_path: "data/admin/agent.json",
    },
    agent_task: {
      diverged: tableKey === "agent_task",
      repo_relative_path: "data/admin/agent_task.json",
    },
  }
}

function renderBanner(
  tableKey: "agent" | "agent_task" = "agent",
  opts?: { refreshToken?: number; onReverted?: () => void },
) {
  return render(
    <UserPromptProvider>
      <RepoJsonDivergenceBanner
        tableKey={tableKey}
        refreshToken={opts?.refreshToken}
        onReverted={opts?.onReverted}
      />
    </UserPromptProvider>,
  )
}

describe("RepoJsonDivergenceBanner", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  it("AST-783: hides banner when table is not diverged", async () => {
    mockedApi.mockResolvedValue({
      ok: true,
      json: async () => ({
        agent: { diverged: false, repo_relative_path: "data/admin/agent.json" },
        agent_task: { diverged: false, repo_relative_path: "data/admin/agent_task.json" },
      }),
    } as Response)
    renderBanner("agent")
    await waitFor(() => expect(mockedApi).toHaveBeenCalledWith("/api/admin/repo_json/status"))
    expect(screen.queryByRole("button", { name: "Revert to file" })).not.toBeInTheDocument()
  })

  it("AST-783: shows warning and reverts after themed confirm", async () => {
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/admin/repo_json/status") {
        return {
          ok: true,
          json: async () => divergedStatus("agent"),
        } as Response
      }
      if (url === "/api/admin/repo_json/revert/agent" && init?.method === "POST") {
        return { ok: true, json: async () => ({ ok: true, row_count: 1 }) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderBanner("agent")
    await waitFor(() => expect(screen.getByRole("button", { name: "Revert to file" })).toBeInTheDocument())
    expect(screen.getByText(/agent personas/)).toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: "Revert to file" }))
    await waitFor(() => expect(screen.getByRole("alertdialog")).toBeInTheDocument())
    const confirmButtons = screen.getAllByRole("button", { name: "Revert to file" })
    await userEvent.click(confirmButtons[confirmButtons.length - 1])

    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith("/api/admin/repo_json/revert/agent", { method: "POST" }),
    )
  })
})

describe("RepoJsonDivergenceBanner — AST-1506", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  it("rewritten warning omits restart deploy overwrite copy", async () => {
    mockedApi.mockResolvedValue({
      ok: true,
      json: async () => divergedStatus("agent"),
    } as Response)
    renderBanner("agent")
    await waitFor(() => expect(screen.getByRole("button", { name: "Show Differences" })).toBeInTheDocument())
    expect(screen.getByRole("button", { name: "Update file with table version" })).toBeInTheDocument()
    expect(screen.queryByText(/restart/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/deploy/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/export_repo_admin_json/i)).not.toBeInTheDocument()
  })

  it("Show Differences loads compare payload for tableKey only", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/admin/repo_json/status") {
        return { ok: true, json: async () => divergedStatus("agent_task") } as Response
      }
      if (url === "/api/admin/repo_json/compare/agent_task") {
        return {
          ok: true,
          json: async () => ({
            table_key: "agent_task",
            diverged: true,
            repo_relative_path: "data/admin/agent_task.json",
            only_in_database: [],
            only_in_file: [],
            changed_rows: [
              {
                row_key: "craft_do_rubric",
                fields: [
                  { field: "content", file_value: "on-disk", database_value: "live-edit" },
                ],
              },
            ],
          }),
        } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderBanner("agent_task")
    await waitFor(() => expect(screen.getByRole("button", { name: "Show Differences" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Show Differences" }))

    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith("/api/admin/repo_json/compare/agent_task"),
    )
    expect(mockedApi).not.toHaveBeenCalledWith("/api/admin/repo_json/compare/agent")
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: /Differences — task prompts/i })).toBeInTheDocument(),
    )
    expect(screen.getByText("Row: craft_do_rubric")).toBeInTheDocument()
    expect(screen.getByText("on-disk")).toBeInTheDocument()
    expect(screen.getByText("live-edit")).toBeInTheDocument()
  })

  it("Update file confirm posts write then refetches status and onReverted", async () => {
    const onReverted = vi.fn()
    let statusCalls = 0
    mockedApi.mockImplementation(async (url: string, init?: RequestInit) => {
      if (url === "/api/admin/repo_json/status") {
        statusCalls += 1
        return {
          ok: true,
          json: async () =>
            statusCalls === 1
              ? divergedStatus("agent")
              : {
                  agent: { diverged: false, repo_relative_path: "data/admin/agent.json" },
                  agent_task: { diverged: false, repo_relative_path: "data/admin/agent_task.json" },
                },
        } as Response
      }
      if (url === "/api/admin/repo_json/write/agent" && init?.method === "POST") {
        return {
          ok: true,
          json: async () => ({
            ok: true,
            table_key: "agent",
            row_count: 6,
            repo_relative_path: "data/admin/agent.json",
          }),
        } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderBanner("agent", { onReverted })
    await waitFor(() => expect(screen.getByRole("button", { name: "Update file with table version" })).toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "Update file with table version" }))
    await waitFor(() =>
      expect(screen.getByRole("alertdialog", { name: "Update file with table version" })).toBeInTheDocument(),
    )
    const confirmButtons = screen.getAllByRole("button", { name: "Update file with table version" })
    await userEvent.click(confirmButtons[confirmButtons.length - 1])

    await waitFor(() =>
      expect(mockedApi).toHaveBeenCalledWith("/api/admin/repo_json/write/agent", { method: "POST" }),
    )
    await waitFor(() => expect(statusCalls).toBeGreaterThanOrEqual(2))
    await waitFor(() => expect(onReverted).toHaveBeenCalled())
  })

  it("Update file cancel does not post write", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/admin/repo_json/status") {
        return { ok: true, json: async () => divergedStatus("agent") } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderBanner("agent")
    await waitFor(() => expect(screen.getByRole("button", { name: "Update file with table version" })).toBeInTheDocument())

    await userEvent.click(screen.getByRole("button", { name: "Update file with table version" }))
    await waitFor(() =>
      expect(screen.getByRole("alertdialog", { name: "Update file with table version" })).toBeInTheDocument(),
    )
    await userEvent.click(screen.getByRole("button", { name: "Cancel" }))

    expect(mockedApi).not.toHaveBeenCalledWith("/api/admin/repo_json/write/agent", expect.anything())
    await waitFor(() => expect(screen.getByRole("button", { name: "Update file with table version" })).toBeInTheDocument())
  })
})

function tallComparePayload(changedCount: number) {
  const changed_rows = Array.from({ length: changedCount }, (_, i) => ({
    row_key: `drift_row_${i + 1}`,
    fields: [
      {
        field: "content",
        file_value: "x".repeat(200),
        database_value: "y".repeat(200),
      },
    ],
  }))
  return {
    table_key: "agent_task",
    diverged: true,
    repo_relative_path: "data/admin/agent_task.json",
    only_in_database: [],
    only_in_file: [],
    changed_rows,
  }
}

describe("RepoJsonDivergenceBanner — AST-1511", () => {
  beforeEach(() => {
    mockedApi.mockReset()
  })

  it("[bug-repro] Show Differences modal scrolls to later changed rows", async () => {
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/admin/repo_json/status") {
        return { ok: true, json: async () => divergedStatus("agent_task") } as Response
      }
      if (url === "/api/admin/repo_json/compare/agent_task") {
        return { ok: true, json: async () => tallComparePayload(4) } as Response
      }
      throw new Error(`unexpected api call: ${url}`)
    })
    renderBanner("agent_task")
    await waitFor(() => expect(screen.getByRole("button", { name: "Show Differences" })).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Show Differences" }))

    await waitFor(() =>
      expect(screen.getByRole("heading", { name: /Differences — task prompts/i })).toBeInTheDocument(),
    )

    const modalBody = document.querySelector(".modal-card--wide .modal-body") as HTMLElement
    expect(modalBody).toBeTruthy()
    const scrollWrap = modalBody.firstElementChild as HTMLElement
    expect(scrollWrap.style.overflowY).toBe("auto")
    expect(scrollWrap.style.height).toBe("100%")

    const fourthRow = screen.getByText("Row: drift_row_4")
    scrollWrap.scrollTop = scrollWrap.scrollHeight
    expect(fourthRow).toBeVisible()
  })
})
