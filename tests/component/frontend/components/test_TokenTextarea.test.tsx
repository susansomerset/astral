import { cleanup, fireEvent, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"
import TokenTextarea from "../../../../src/ui/frontend/src/components/TokenTextarea"
import { renderWithProviders } from "../test-utils"

function hasTokenMenu() {
  return document.querySelector('[style*="z-index: 100"], [style*="zIndex: 100"]') != null
}

function focusEnd(textarea: HTMLTextAreaElement) {
  textarea.focus()
  textarea.setSelectionRange(textarea.value.length, textarea.value.length)
  fireEvent.keyUp(textarea)
}

describe("TokenTextarea", () => {
  it("opens trigger but keeps the menu hidden when no token matches the filter", () => {
    const onChange = vi.fn()
    renderWithProviders(
      <TokenTextarea value="{$ZZ" onChange={onChange} tokens={["FOO"]} />,
    )
    const ta = screen.getByRole("textbox") as HTMLTextAreaElement
    ta.focus()
    ta.setSelectionRange(ta.value.length, ta.value.length)
    fireEvent.keyUp(ta)
    expect(hasTokenMenu()).toBe(false)
    fireEvent.keyDown(ta, { key: "Enter" })
    expect(onChange).not.toHaveBeenCalled()
  })

  it("honours an explicit rows prop (default-param branch)", () => {
    const onChange = vi.fn()
    renderWithProviders(
      <TokenTextarea value="" onChange={onChange} tokens={["FOO"]} rows={7} />,
    )
    expect((screen.getByRole("textbox") as HTMLTextAreaElement).rows).toBe(7)
  })

  it("updates value and inserts a token from the dropdown", async () => {
    const onChange = vi.fn()
    renderWithProviders(
      <TokenTextarea value="Hello {$" onChange={onChange} tokens={["FOO", "BAR"]} />,
    )
    const textarea = screen.getByRole("textbox") as HTMLTextAreaElement
    focusEnd(textarea)
    expect(screen.getByText((_, node) => node?.textContent === "{$FOO}")).toBeInTheDocument()
    await userEvent.click(screen.getByText((_, node) => node?.textContent === "{$FOO}"))
    expect(onChange).toHaveBeenCalledWith("Hello {$FOO}")
  })

  it("supports keyboard navigation and dismissal", async () => {
    const onChange = vi.fn()
    renderWithProviders(
      <TokenTextarea value="{$" onChange={onChange} tokens={["AAA", "BBB"]} />,
    )
    const textarea = screen.getByRole("textbox") as HTMLTextAreaElement
    focusEnd(textarea)
    fireEvent.keyDown(textarea, { key: "ArrowDown" })
    fireEvent.keyDown(textarea, { key: "ArrowUp" })
    fireEvent.keyDown(textarea, { key: "Enter" })
    expect(onChange).toHaveBeenCalledWith("{$AAA}")
  })

  it("dismisses on escape, outside click, and closed tokens", async () => {
    const onChange = vi.fn()
    const { unmount } = renderWithProviders(
      <TokenTextarea value="{$FOO}" onChange={onChange} tokens={["FOO"]} />,
    )
    const closed = screen.getByRole("textbox") as HTMLTextAreaElement
    closed.setSelectionRange(closed.value.length, closed.value.length)
    fireEvent.keyUp(closed)
    expect(hasTokenMenu()).toBe(false)
    unmount()
    cleanup()

    renderWithProviders(
      <TokenTextarea value="{$" onChange={onChange} tokens={["FOO"]} />,
    )
    const open = screen.getByRole("textbox") as HTMLTextAreaElement
    focusEnd(open)
    fireEvent.keyDown(open, { key: "Escape" })
    expect(hasTokenMenu()).toBe(false)
    cleanup()

    renderWithProviders(
      <TokenTextarea value="{$bad}" onChange={onChange} tokens={["FOO"]} />,
    )
    focusEnd(screen.getByRole("textbox") as HTMLTextAreaElement)
    expect(hasTokenMenu()).toBe(false)
    cleanup()

    renderWithProviders(
      <TokenTextarea value="plain" onChange={onChange} tokens={["FOO"]} />,
    )
    focusEnd(screen.getByRole("textbox") as HTMLTextAreaElement)
    expect(hasTokenMenu()).toBe(false)
    cleanup()

    const { container } = renderWithProviders(
      <TokenTextarea value="{$" onChange={onChange} tokens={["FOO"]} />,
    )
    focusEnd(screen.getByRole("textbox") as HTMLTextAreaElement)
    fireEvent.mouseDown(container.ownerDocument.body)
    expect(hasTokenMenu()).toBe(false)
  })

  it("ignores keyboard handling when the menu is hidden or empty", () => {
    const onChange = vi.fn()
    renderWithProviders(
      <TokenTextarea value="plain" onChange={onChange} tokens={["FOO"]} />,
    )
    const textarea = screen.getByRole("textbox")
    fireEvent.keyDown(textarea, { key: "Tab" })
    expect(onChange).not.toHaveBeenCalled()
  })

  it("handles tab insertion and invalid trigger text", async () => {
    const onChange = vi.fn()
    renderWithProviders(
      <TokenTextarea value="{$" onChange={onChange} tokens={["FOO"]} />,
    )
    const textarea = screen.getByRole("textbox") as HTMLTextAreaElement
    focusEnd(textarea)
    fireEvent.keyDown(textarea, { key: "Tab" })
    expect(onChange).toHaveBeenCalledWith("{$FOO}")

    cleanup()
    renderWithProviders(
      <TokenTextarea value="{$x" onChange={onChange} tokens={["FOO"]} />,
    )
    focusEnd(screen.getByRole("textbox") as HTMLTextAreaElement)
    expect(hasTokenMenu()).toBe(false)
  })

  it("ignores checkTrigger when the textarea unmounts before the deferred pass", () => {
    vi.useFakeTimers()
    const onChange = vi.fn()
    const { unmount } = renderWithProviders(
      <TokenTextarea value="" onChange={onChange} tokens={["FOO"]} />,
    )
    const textarea = screen.getByRole("textbox") as HTMLTextAreaElement
    fireEvent.change(textarea, { target: { value: "{$" } })
    unmount()
    vi.runOnlyPendingTimers()
    vi.useRealTimers()
    expect(onChange).toHaveBeenCalled()
  })
})
