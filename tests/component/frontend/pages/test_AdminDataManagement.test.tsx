import { fireEvent, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import DataManagement from "../../../../src/ui/frontend/src/pages/AdminDataManagement"
import { installBaseApiMocks, renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", () => ({
  default: vi.fn(),
  setAuthTokenGetter: vi.fn(),
  setUnauthorizedHandler: vi.fn(),
}))

const mockedApi = vi.mocked(api)

describe("AdminDataManagement", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    })
  })

  function mockApi(
    extra?: (url: string, init?: RequestInit) => Promise<Response | undefined> | Response | undefined,
  ) {
    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      const fromExtra = extra ? await extra(url, init) : undefined
      if (fromExtra !== undefined) return fromExtra

      if (url === "/api/admin/data/sql" && init?.method === "POST") {
        const body = JSON.parse(String(init.body))
        if (body.sql.includes("sqlite_master")) {
          return { ok: true, json: async () => ({ type: "select", columns: ["name"], rows: [{ name: "agent_task" }], count: 1 }) } as Response
        }
        if (body.sql.includes("PRAGMA table_info")) {
          return { ok: true, json: async () => ({ type: "select", columns: ["name", "type", "pk"], rows: [{ name: "id", type: "INTEGER", pk: 1 }], count: 1 }) } as Response
        }
        if (body.sql.startsWith("UPDATE")) {
          return { ok: true, json: async () => ({ type: "execute", rows_affected: 2 }) } as Response
        }
        return { ok: true, json: async () => ({ type: "select", columns: ["id", "payload"], rows: [{ id: 1, payload: JSON.stringify({ a: 1 }) }], count: 1 }) } as Response
      }
      if (url === "/api/admin/data/table_copy_upsert" && init?.method === "POST") {
        return {
          ok: true,
          json: async () => ({ ok: true, inserted: 2, updated: 1, skipped: 3 }),
        } as Response
      }
    })
  }

  it("runs sql, copies output, browses schema, and completes table upsert from modal", async () => {
    mockApi()
    renderWithProviders(<DataManagement />)
    // Table name appears in upsert <select> and schema list — wait on option (first paint §6c)
    await waitFor(() => expect(screen.getByRole("option", { name: "agent_task" })).toBeInTheDocument())

    const schemaRows = screen.getAllByText("agent_task")
    await userEvent.click(schemaRows[schemaRows.length - 1])
    expect(screen.getByText("id")).toBeInTheDocument()

    const textarea = screen.getByPlaceholderText(/SELECT \* FROM agent_task/)
    fireEvent.change(textarea, { target: { value: "SELECT id, payload FROM agent_task" } })
    await userEvent.click(screen.getByRole("button", { name: "Run" }))
    await waitFor(() => expect(screen.getByText("1 row(s)")).toBeInTheDocument())
    await userEvent.click(screen.getByRole("button", { name: "Copy Output" }))
    expect(navigator.clipboard.writeText).toHaveBeenCalled()

    fireEvent.change(textarea, { target: { value: "UPDATE agent_task SET id = 1" } })
    fireEvent.keyDown(textarea, { key: "Enter", metaKey: true })
    await waitFor(() => expect(screen.getByText("2 row(s) affected")).toBeInTheDocument())

    // Table Upsert: same sqlite_master-driven list as schema browser (§6c — full page + modal path)
    const upsertPick = screen.getByRole("combobox")
    await userEvent.selectOptions(upsertPick, "agent_task")
    await userEvent.click(screen.getByRole("button", { name: "Update" }))
    expect(screen.getByRole("heading", { name: "Upsert rows — agent_task" })).toBeInTheDocument()
    fireEvent.change(screen.getByPlaceholderText(/Paste Copy Output JSON array here/), {
      target: { value: '[{"id":1}]' },
    })
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    const dialog = await screen.findByRole("alertdialog", { name: "Apply upsert" })
    await userEvent.click(within(dialog).getByRole("button", { name: "Apply" }))
    await waitFor(() =>
      expect(screen.getByText(/Upsert completed: inserted 2, updated 1, skipped 3/)).toBeInTheDocument(),
    )
  }, 20000)

  it("toasts when upsert paste is empty and when API reports ok:false", async () => {
    mockApi(async (url, init) => {
      if (url === "/api/admin/data/table_copy_upsert" && init?.method === "POST") {
        return { ok: true, json: async () => ({ ok: false, error: "bad payload" }) } as Response
      }
    })
    renderWithProviders(<DataManagement />)
    await waitFor(() => expect(screen.getByText("Table Upsert")).toBeInTheDocument())
    await userEvent.selectOptions(screen.getByRole("combobox"), "agent_task")
    await userEvent.click(screen.getByRole("button", { name: "Update" }))
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(screen.getByText("Paste JSON rows first.")).toBeInTheDocument())

    fireEvent.change(screen.getByPlaceholderText(/Paste Copy Output JSON array here/), { target: { value: "[]" } })
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    const dialog = await screen.findByRole("alertdialog", { name: "Apply upsert" })
    await userEvent.click(within(dialog).getByRole("button", { name: "Apply" }))
    await waitFor(() => expect(screen.getByText("bad payload")).toBeInTheDocument())
  }, 15000)

  it("handles sql errors", async () => {
    mockApi()
    renderWithProviders(<DataManagement />)
    await waitFor(() => expect(screen.getByRole("option", { name: "agent_task" })).toBeInTheDocument())

    installBaseApiMocks(mockedApi, async (url: string, init?: RequestInit) => {
      if (url === "/api/admin/data/sql" && init?.method === "POST") {
        return { ok: false, json: async () => ({ error: "bad sql" }) } as Response
      }
    })
    const textarea = screen.getByPlaceholderText(/SELECT \* FROM agent_task/)
    fireEvent.change(textarea, { target: { value: "SELECT bad" } })
    await userEvent.click(screen.getByRole("button", { name: "Run" }))
    await waitFor(() => expect(screen.getByText("bad sql")).toBeInTheDocument())
  }, 15000)
})
