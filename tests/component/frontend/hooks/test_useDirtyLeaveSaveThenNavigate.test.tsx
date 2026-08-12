import { screen, waitFor } from "@testing-library/react"
import { renderHook } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import type { ReactNode } from "react"
import type { Blocker, BlockerFunction } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { UserPromptProvider } from "../../../../src/ui/frontend/src/components/UserPrompt"
import { useDirtyLeaveSaveThenNavigate } from "../../../../src/ui/frontend/src/hooks/useDirtyLeaveSaveThenNavigate"

/** Controllable `useBlocker` — full data-router navigate hits jsdom AbortSignal bugs under RR7/Node 24. */
const blockerCtl: {
  value: Blocker
  shouldBlock: BlockerFunction | null
} = {
  value: { state: "unblocked" },
  shouldBlock: null,
}

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>()
  return {
    ...actual,
    useBlocker: (fn: boolean | BlockerFunction) => {
      if (typeof fn === "function") blockerCtl.shouldBlock = fn
      return blockerCtl.value
    },
  }
})

function wrapper({ children }: { children: ReactNode }) {
  return <UserPromptProvider>{children}</UserPromptProvider>
}

function setUnblocked() {
  blockerCtl.value = { state: "unblocked" }
}

function setBlocked(key = "nav-1") {
  const proceed = vi.fn()
  const reset = vi.fn()
  blockerCtl.value = {
    state: "blocked",
    location: { pathname: "/other", search: "", hash: "", key, state: null },
    proceed,
    reset,
  }
  return { proceed, reset }
}

describe("useDirtyLeaveSaveThenNavigate — AST-1335", () => {
  beforeEach(() => {
    setUnblocked()
    blockerCtl.shouldBlock = null
  })

  it("BlockerFunction is false when clean; true only on pathname change when dirty", () => {
    const onSave = vi.fn(async () => undefined)
    const { rerender } = renderHook(
      (props: { isDirty: boolean }) =>
        useDirtyLeaveSaveThenNavigate({ isDirty: props.isDirty, onSave }),
      { initialProps: { isDirty: false }, wrapper },
    )
    expect(blockerCtl.shouldBlock).toBeTypeOf("function")
    const args = {
      currentLocation: { pathname: "/leave", search: "", hash: "", key: "a", state: null },
      nextLocation: { pathname: "/other", search: "", hash: "", key: "b", state: null },
      historyAction: "PUSH" as const,
    }
    expect(blockerCtl.shouldBlock!(args)).toBe(false)

    rerender({ isDirty: true })
    expect(blockerCtl.shouldBlock!(args)).toBe(true)
    // Same pathname + search change must not block (Profile text tabs / query chrome).
    expect(
      blockerCtl.shouldBlock!({
        ...args,
        nextLocation: { ...args.currentLocation, search: "?tab=notes", key: "c" },
      }),
    ).toBe(false)
  })

  it("dirty leave shows Save-primary prompt; Cancel stays (reset, no onSave)", async () => {
    const onSave = vi.fn(async () => undefined)
    const { rerender } = renderHook(
      () => useDirtyLeaveSaveThenNavigate({ isDirty: true, onSave }),
      { wrapper },
    )
    const { proceed, reset } = setBlocked()
    rerender()
    const dialog = await screen.findByRole("alertdialog")
    expect(dialog).toHaveTextContent("Save changes?")
    expect(dialog).toHaveTextContent("You have unsaved changes. Save before leaving?")
    const saveBtn = screen.getByRole("button", { name: "Save" })
    expect(saveBtn.className).toMatch(/\bbtn\b/)
    expect(saveBtn.className).toMatch(/\bprimary\b/)
    expect(screen.getByRole("button", { name: "Cancel" }).className).toMatch(/\bsecondary\b/)
    await userEvent.click(screen.getByRole("button", { name: "Cancel" }))
    await waitFor(() => expect(reset).toHaveBeenCalled())
    expect(proceed).not.toHaveBeenCalled()
    expect(onSave).not.toHaveBeenCalled()
  })

  it("Save then proceeds after onSave resolves", async () => {
    const onSave = vi.fn(async () => undefined)
    const { rerender } = renderHook(
      () => useDirtyLeaveSaveThenNavigate({ isDirty: true, onSave }),
      { wrapper },
    )
    const { proceed, reset } = setBlocked("save-ok")
    rerender()
    await screen.findByRole("alertdialog")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(onSave).toHaveBeenCalledTimes(1))
    await waitFor(() => expect(proceed).toHaveBeenCalled())
    expect(reset).not.toHaveBeenCalled()
  })

  it("save failure resets; does not proceed", async () => {
    const onSave = vi.fn(async () => {
      throw new Error("save failed")
    })
    const { rerender } = renderHook(
      () => useDirtyLeaveSaveThenNavigate({ isDirty: true, onSave }),
      { wrapper },
    )
    const { proceed, reset } = setBlocked("save-fail")
    rerender()
    await screen.findByRole("alertdialog")
    await userEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(onSave).toHaveBeenCalledTimes(1))
    await waitFor(() => expect(reset).toHaveBeenCalled())
    expect(proceed).not.toHaveBeenCalled()
  })
})
