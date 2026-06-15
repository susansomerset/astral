import { screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

describe("ListPage AST-647 list table layout", () => {
  beforeEach(async () => {
    vi.resetModules()
    localStorage.clear()
    const api = (await import("../../../../src/ui/frontend/src/lib/api")).default
    vi.mocked(api).mockImplementation(async (url: string) => {
      if (url === "/api/system/ui_config") {
        return {
          json: async () => ({
            column_types: {},
            list_table_frozen_data_columns: 2,
            list_table_cell_truncate_chars: 30,
          }),
        } as Response
      }
      throw new Error(`Unhandled api ${url}`)
    })
  })

  it("applies frozen-column classes from ui_config default and truncates long cells", async () => {
    const { default: ListPage } = await import("../../../../src/ui/frontend/src/components/ListPage")
    const longName = "N".repeat(45)
    renderWithProviders(
      <ListPage
        title="Frozen"
        columns={[
          { key: "name", label: "Name" },
          { key: "amount", label: "Amount" },
          { key: "note", label: "Note" },
        ]}
        rows={[{ id: "1", name: longName, amount: 1, note: "ok" }]}
        selectable
        rowActions={() => <button type="button">act</button>}
      />,
    )
    await waitFor(() => expect(screen.getByText(`${"N".repeat(30)}\u2026`)).toBeInTheDocument())
    expect(screen.getByTitle(longName)).toBeInTheDocument()
    const table = screen.getByRole("table")
    expect(table.closest(".list-page-table-wrap--scroll")).toBeTruthy()
    const headers = screen.getAllByRole("columnheader")
    expect(headers[0]).toHaveClass("list-table-cell-frozen")
    expect(headers[1]).toHaveClass("list-table-cell-frozen")
    expect(headers[2]).toHaveClass("list-table-cell-frozen")
    expect(headers[3]).not.toHaveClass("list-table-cell-frozen")
    expect(headers[4]).toHaveClass("list-table-cell-frozen-right")
    const cells = screen.getAllByRole("cell")
    expect(cells[0]).toHaveClass("list-table-cell-frozen")
    expect(cells[1]).toHaveClass("list-table-cell-frozen")
    expect(cells[2]).toHaveClass("list-table-cell-frozen")
    expect(cells[3]).not.toHaveClass("list-table-cell-frozen")
  })

  it("AST-652: default list-page-table uses autosize layout (not force-fit fixed)", async () => {
    const { default: ListPage } = await import("../../../../src/ui/frontend/src/components/ListPage")
    renderWithProviders(
      <ListPage
        title="Autosize"
        columns={[
          { key: "name", label: "Name" },
          { key: "amount", label: "Amount" },
        ]}
        rows={[{ id: "1", name: "Alpha", amount: 2 }]}
      />,
    )
    await waitFor(() => expect(screen.getByText("Alpha")).toBeInTheDocument())
    const table = screen.getByRole("table")
    expect(table).toHaveClass("list-page-table")
    expect(table.className).not.toMatch(/list-page-table--auto/)
    expect(getComputedStyle(table).tableLayout).toBe("auto")
    expect(getComputedStyle(table).width).not.toBe("100%")
  })

  it("AST-657: frozen data columns get cumulative sticky left offsets after measure", async () => {
    const { default: ListPage } = await import("../../../../src/ui/frontend/src/components/ListPage")
    renderWithProviders(
      <ListPage
        title="Measured freeze"
        columns={[
          { key: "name", label: "Name" },
          { key: "amount", label: "Amount" },
          { key: "note", label: "Note" },
        ]}
        rows={[{ id: "1", name: "Alpha", amount: 2, note: "ok" }]}
        selectable
        rowActions={() => <button type="button">act</button>}
      />,
    )
    await waitFor(() => expect(screen.getByText("Alpha")).toBeInTheDocument())
    const headers = screen.getAllByRole("columnheader")
    // jsdom offsetWidth is 0 — second frozen column still advances via width fallback (120px).
    await waitFor(() => expect(headers[2].style.left).toBe("120px"))
    const parseLeft = (el: HTMLElement) => parseFloat(el.style.left || "0")
    expect(parseLeft(headers[2])).toBeGreaterThan(parseLeft(headers[1]))
    expect(headers[1]).toHaveClass("list-table-cell-frozen")
    expect(headers[2]).toHaveClass("list-table-cell-frozen")
    expect(headers[3]).not.toHaveClass("list-table-cell-frozen")
  })

  it("honors frozenDataColumns override over ui_config", async () => {
    const { default: ListPage } = await import("../../../../src/ui/frontend/src/components/ListPage")
    renderWithProviders(
      <ListPage
        title="Override"
        frozenDataColumns={1}
        columns={[
          { key: "name", label: "Name" },
          { key: "amount", label: "Amount" },
        ]}
        rows={[{ id: "1", name: "Alpha", amount: 2 }]}
      />,
    )
    await waitFor(() => expect(screen.getByText("Alpha")).toBeInTheDocument())
    const headers = screen.getAllByRole("columnheader")
    expect(headers[0]).toHaveClass("list-table-cell-frozen")
    expect(headers[1]).not.toHaveClass("list-table-cell-frozen")
  })
})
