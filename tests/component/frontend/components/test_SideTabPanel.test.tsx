import { fireEvent, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"
import SideTabPanel, { type SideTab } from "../../../../src/ui/frontend/src/components/SideTabPanel"
import { renderWithProviders } from "../test-utils"

const baseTabs: SideTab[] = [
  { id: "a", label: "Alpha", content: "one" },
  { id: "b", label: "Beta", content: "two" },
]

describe("SideTabPanel", () => {
  it("uses default minTabs and maxTabs when omitted", async () => {
    const onChange = vi.fn()
    renderWithProviders(
      <SideTabPanel tabs={[{ id: "only", label: "Only", content: "" }]} editable onChange={onChange} />,
    )
    expect(screen.getByTitle("Remove")).toBeDisabled()
    expect(screen.getByRole("button", { name: "+ Add" })).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: "+ Add" }))
    expect(onChange).toHaveBeenCalled()
  })

  it("renders read-only tabs and switches active content", async () => {
    renderWithProviders(<SideTabPanel tabs={baseTabs} />)
    expect(screen.getAllByText("Alpha").length).toBeGreaterThan(0)
    expect(screen.getByDisplayValue("one")).toBeInTheDocument()
    await userEvent.click(screen.getAllByText("Beta")[0])
    expect(screen.getByDisplayValue("two")).toBeInTheDocument()
  })

  it("supports custom renderContent", () => {
    renderWithProviders(
      <SideTabPanel
        tabs={baseTabs}
        renderContent={id => <div data-testid={`custom-${id}`}>{id}</div>}
      />,
    )
    expect(screen.getByTestId("custom-a")).toBeInTheDocument()
  })

  it("edits, reorders, removes, and adds tabs", async () => {
    const onChange = vi.fn()
    const { rerender } = renderWithProviders(
      <SideTabPanel tabs={baseTabs} editable onChange={onChange} minTabs={1} maxTabs={3} />,
    )

    await userEvent.dblClick(screen.getAllByText("Alpha")[0])
    const renameInput = screen.getAllByDisplayValue("Alpha")[0]
    await userEvent.clear(renameInput)
    await userEvent.type(renameInput, "Renamed")
    fireEvent.blur(renameInput)
    expect(onChange).toHaveBeenCalled()

    await userEvent.click(screen.getAllByTitle("Move down")[0])
    await userEvent.click(screen.getAllByTitle("Move up")[0])
    await userEvent.click(screen.getAllByTitle("Remove")[0])
    await userEvent.click(screen.getByRole("button", { name: "+ Add" }))

    rerender(
      <SideTabPanel
        tabs={[{ id: "z", label: "Zeta", content: "z" }]}
        editable
        onChange={onChange}
      />,
    )
    expect(screen.getAllByText("Zeta").length).toBeGreaterThan(0)
  })

  it("blocks invalid moves, removals, and additions at limits", async () => {
    const onChange = vi.fn()
    renderWithProviders(
      <SideTabPanel tabs={[{ id: "only", label: "Only", content: "" }]} editable onChange={onChange} minTabs={1} maxTabs={1} />,
    )
    expect(screen.getByTitle("Move up")).toBeDisabled()
    expect(screen.getByTitle("Move down")).toBeDisabled()
    expect(screen.getByTitle("Remove")).toBeDisabled()
    expect(screen.queryByRole("button", { name: "+ Add" })).not.toBeInTheDocument()

    const twoTabs = [
      { id: "a", label: "A", content: "" },
      { id: "b", label: "B", content: "" },
    ]
    const { rerender } = renderWithProviders(
      <SideTabPanel tabs={twoTabs} editable onChange={onChange} />,
    )
    await userEvent.click(screen.getAllByTitle("Move up")[0])
    onChange.mockClear()
    await userEvent.click(screen.getAllByTitle("Move down")[0])
    onChange.mockClear()
    rerender(<SideTabPanel tabs={twoTabs} editable onChange={onChange} maxTabs={2} />)
    expect(screen.queryByRole("button", { name: "+ Add" })).not.toBeInTheDocument()
  })

  it("handles empty tabs, rename enter, and active removal", async () => {
    const onChange = vi.fn()
    renderWithProviders(<SideTabPanel tabs={[]} editable onChange={onChange} />)
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument()

    const tabs: SideTab[] = [
      { id: "a", label: "A", content: "a" },
      { id: "b", label: "B", content: "b" },
    ]
    const { rerender } = renderWithProviders(
      <SideTabPanel tabs={tabs} editable onChange={onChange} minTabs={1} />,
    )
    await userEvent.dblClick(screen.getAllByText("A")[0])
    const rename = screen.getAllByDisplayValue("A")[0]
    fireEvent.keyDown(rename, { key: "Enter" })
    await userEvent.click(screen.getAllByTitle("Remove")[0])
    rerender(
      <SideTabPanel
        tabs={[{ id: "b", label: "B", content: "b" }]}
        editable
        onChange={onChange}
        minTabs={1}
      />,
    )
    expect(screen.getByDisplayValue("b")).toBeInTheDocument()
  })
})
