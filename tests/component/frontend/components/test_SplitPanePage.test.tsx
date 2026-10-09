import { fireEvent, render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"
import SplitPanePage from "../../../../src/ui/frontend/src/components/SplitPanePage"

const ROOT_W = 1000
const LEFT_W = 497 // calc(50% - 3px) of a 1000px container

/** jsdom has no layout: give the root and left panel real widths for the drag math. */
function stubWidths() {
  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockImplementation(function (this: HTMLElement) {
    // Root is the only element with three children (left | divider | right).
    const width = this.children.length === 3 ? ROOT_W : LEFT_W
    return { width, height: 600, top: 0, left: 0, right: width, bottom: 600, x: 0, y: 0, toJSON: () => ({}) } as DOMRect
  })
}

function renderPane() {
  const { unmount } = render(<SplitPanePage left={<span>LEFT</span>} right={<span>RIGHT</span>} />)
  const divider = screen.getByRole("separator")
  const leftPanel = screen.getByText("LEFT").parentElement as HTMLDivElement
  const rightPanel = screen.getByText("RIGHT").parentElement as HTMLDivElement
  const root = divider.parentElement as HTMLDivElement
  return { divider, leftPanel, rightPanel, root, unmount }
}

// AST-2082: left | divider | right filling the parent; divider drag resizes the left panel.
describe("AST-2082 SplitPanePage", () => {
  afterEach(() => vi.restoreAllMocks())

  it("fills its parent and starts at half width", () => {
    const { divider, leftPanel, rightPanel, root } = renderPane()
    expect(root.style.width).toBe("100%")
    expect(root.style.height).toBe("100%")
    expect(divider).toHaveAttribute("aria-orientation", "vertical")
    expect(leftPanel.style.width).toBe("calc(50% - 3px)")
    expect(rightPanel.style.flex).toMatch(/^1/)
  })

  it("AC2: dragging 100px right grows the left panel by 100px; right panel takes the rest", () => {
    stubWidths()
    const { divider, leftPanel, rightPanel, root } = renderPane()
    fireEvent.mouseDown(divider, { clientX: 500 })
    // Mid-drag: panels ignore the pointer (iframe would swallow mousemove) and text selection is off.
    expect(leftPanel.style.pointerEvents).toBe("none")
    expect(rightPanel.style.pointerEvents).toBe("none")
    expect(root.style.userSelect).toBe("none")
    fireEvent.mouseMove(window, { clientX: 600 })
    expect(leftPanel.style.width).toBe(`${LEFT_W + 100}px`)
    expect(rightPanel.style.flex).toMatch(/^1/)
    fireEvent.mouseUp(window)
    expect(leftPanel.style.pointerEvents).toBe("")
    expect(root.style.userSelect).toBe("")
    // Released: further moves do nothing.
    fireEvent.mouseMove(window, { clientX: 900 })
    expect(leftPanel.style.width).toBe(`${LEFT_W + 100}px`)
  })

  it("clamps to the container: never negative, never past the divider", () => {
    stubWidths()
    const { divider, leftPanel } = renderPane()
    fireEvent.mouseDown(divider, { clientX: 500 })
    fireEvent.mouseMove(window, { clientX: -5000 })
    expect(leftPanel.style.width).toBe("0px")
    fireEvent.mouseMove(window, { clientX: 5000 })
    expect(leftPanel.style.width).toBe(`${ROOT_W - 6}px`)
    fireEvent.mouseUp(window)
  })

  it("unmount mid-drag removes the window listeners", () => {
    stubWidths()
    const remove = vi.spyOn(window, "removeEventListener")
    const { divider, unmount } = renderPane()
    fireEvent.mouseDown(divider, { clientX: 500 })
    remove.mockClear()
    unmount()
    const removed = remove.mock.calls.map(([type]) => type)
    expect(removed).toEqual(expect.arrayContaining(["mousemove", "mouseup"]))
  })

  it("unmount without a drag is a no-op", () => {
    const remove = vi.spyOn(window, "removeEventListener")
    const { unmount } = renderPane()
    remove.mockClear()
    unmount()
    expect(remove.mock.calls.map(([type]) => type)).not.toContain("mousemove")
  })
})
