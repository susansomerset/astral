import { fireEvent, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "../../../../src/ui/frontend/src/lib/api"
import ListPage from "../../../../src/ui/frontend/src/components/ListPage"
import { renderWithProviders } from "../test-utils"

vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})

const mockedApi = vi.mocked(api)

const rows = [
  { id: "1", name: "Alpha", amount: 10, note: "x".repeat(120), custom: "one" },
  { id: "2", name: "Beta", amount: 5, note: "short", custom: "two" },
]

describe("ListPage", () => {
  beforeEach(() => {
    localStorage.clear()
    mockedApi.mockReset()
    mockedApi.mockImplementation(async (url: string) => {
      if (url === "/api/system/ui_config") {
        return {
          json: async () => ({
            column_types: {
              currency: { align: "right", number_format: "$0.00" },
            },
          }),
        } as Response
      }
      throw new Error(`Unhandled api ${url}`)
    })
  })

  it("renders loading and empty states", async () => {
    renderWithProviders(<ListPage title="Empty Page" columns={[{ key: "name", label: "Name" }]} rows={[]} loading />)
    expect(screen.getByText("Loading...")).toBeInTheDocument()
    renderWithProviders(<ListPage title="Empty Page 2" columns={[{ key: "name", label: "Name" }]} rows={[]} emptyMessage="Nothing here" />)
    await waitFor(() => expect(screen.getByText("Nothing here")).toBeInTheDocument())
  })

  it("filters, sorts, selects, and runs bulk actions", async () => {
    const onSelectionChange = vi.fn()
    const bulk = vi.fn()
    renderWithProviders(
      <ListPage
        title="Jobs"
        columns={[
          { key: "name", label: "Name", defaultDesc: true },
          { key: "amount", label: "Amount", type: "currency" },
          { key: "note", label: "Note", expandable: true, sortable: false },
          { key: "custom", label: "Custom", render: value => `C:${value}` },
        ]}
        rows={rows}
        selectable
        bulkActions={[{ label: "Archive", onClick: bulk }, { label: "Delete", onClick: bulk, variant: "danger" }]}
        onSelectionChange={onSelectionChange}
        onRowClick={row => row.id}
        rowActions={row => <button type="button">{`act-${row.id}`}</button>}
        horizontalScrollable
        actions={<span>toolbar</span>}
      />,
    )
    await waitFor(() => expect(screen.getByText("Alpha")).toBeInTheDocument())
    expect(screen.getByText("toolbar")).toBeInTheDocument()
    await userEvent.type(screen.getByPlaceholderText("Search..."), "beta")
    expect(screen.getByText("Beta")).toBeInTheDocument()
    await userEvent.clear(screen.getByPlaceholderText("Search..."))
    await userEvent.click(screen.getByRole("columnheader", { name: /Name/ }))
    await userEvent.click(screen.getByRole("columnheader", { name: /Name/ }))
    await userEvent.click(screen.getAllByRole("checkbox")[0])
    await userEvent.click(screen.getByRole("button", { name: "Archive" }))
    expect(bulk).toHaveBeenCalledWith(["1", "2"])
    await userEvent.click(screen.getByText("more"))
    await userEvent.click(screen.getByText("less"))
    await userEvent.click(screen.getByText("act-1"))
    fireEvent.click(screen.getByText("Alpha"))
  })

  it("persists column layout and handles drag resize", async () => {
    renderWithProviders(
      <ListPage
        title="Layout"
        columns={[
          { key: "name", label: "Name" },
          { key: "amount", label: "Amount" },
        ]}
        rows={rows}
      />,
    )
    await waitFor(() => expect(screen.getByText("Alpha")).toBeInTheDocument())
    const headers = screen.getAllByRole("columnheader")
    fireEvent.dragStart(headers[0])
    fireEvent.dragOver(headers[1])
    fireEvent.drop(headers[1])
    const handle = document.querySelector(".col-resize-handle") as HTMLElement
    fireEvent.mouseDown(handle, { clientX: 100 })
    fireEvent.mouseMove(document, { clientX: 180 })
    fireEvent.mouseUp(document)
    expect(localStorage.getItem("listpage:Layout")).toContain("name")
  })

  it("persists column layout and handles drag resize", async () => {
    localStorage.setItem("listpage:Quirk", "{ not json")
    renderWithProviders(
      <ListPage title="Quirk" columns={[{ key: "name", label: "Name" }]} rows={[{ id: "1", name: "Row" }]} />,
    )
    await waitFor(() => expect(screen.getByText("Row")).toBeInTheDocument())
    const setItem = vi.spyOn(Storage.prototype, "setItem")
    setItem.mockImplementation(() => {
      throw new Error("quota")
    })
    const handle = document.querySelector(".col-resize-handle") as HTMLElement
    fireEvent.mouseDown(handle, { clientX: 100 })
    fireEvent.mouseMove(document, { clientX: 220 })
    fireEvent.mouseUp(document)
    setItem.mockRestore()
  })

  it("uses default idField and survives empty default sort", async () => {
    renderWithProviders(
      <ListPage
        title="Defaults"
        columns={[
          { key: "name", label: "Name", sortable: false },
        ]}
        rows={[{ id: "42", name: "Forty-two" }]}
      />,
    )
    await waitFor(() => expect(screen.getByText("Forty-two")).toBeInTheDocument())
  })
})
