import { useCallback, useEffect, useRef } from "react"
import { useBlocker, type BlockerFunction } from "react-router-dom"
import { useUserConfirm } from "../components/UserPrompt"

export type DirtyLeaveSaveThenNavigateOptions = {
  /** When false, navigation is never blocked and no prompt shows. */
  isDirty: boolean
  /**
   * Persist the draft. Must resolve on success and reject on failure.
   * Caller owns toasts / inline error UI on rejection (same as ordinary Save).
   * On success, caller must clear dirty (update snapshot) before the promise resolves
   * so a follow-on navigation is not re-blocked on stale dirty=true.
   */
  onSave: () => Promise<void>
  message?: string
  title?: string
  confirmLabel?: string
  cancelLabel?: string
}

const DEFAULT_MESSAGE = "You have unsaved changes. Save before leaving?"
const DEFAULT_TITLE = "Save changes?"
const DEFAULT_CONFIRM_LABEL = "Save"
const DEFAULT_CANCEL_LABEL = "Cancel"

/** Block dirty SPA pathname changes; Save (primary) then proceed, cancel/fail stay. */
export function useDirtyLeaveSaveThenNavigate(options: DirtyLeaveSaveThenNavigateOptions): void {
  const {
    isDirty,
    onSave,
    message = DEFAULT_MESSAGE,
    title = DEFAULT_TITLE,
    confirmLabel = DEFAULT_CONFIRM_LABEL,
    cancelLabel = DEFAULT_CANCEL_LABEL,
  } = options

  const confirm = useUserConfirm()
  // One confirm cycle per blocked transition (Strict Mode / effect re-entry).
  const promptKeyRef = useRef<string | null>(null)

  const shouldBlock = useCallback<BlockerFunction>(
    ({ currentLocation, nextLocation }) =>
      isDirty && currentLocation.pathname !== nextLocation.pathname,
    [isDirty],
  )

  const blocker = useBlocker(shouldBlock)

  useEffect(() => {
    if (blocker.state !== "blocked") {
      promptKeyRef.current = null
      return
    }

    const key = `${blocker.location.key}:${blocker.location.pathname}`
    if (promptKeyRef.current === key) return
    promptKeyRef.current = key

    let cancelled = false
    ;(async () => {
      const ok = await confirm(message, {
        title,
        confirmLabel,
        cancelLabel,
        variant: "default",
      })
      if (cancelled) return
      if (!ok) {
        blocker.reset?.()
        return
      }
      try {
        await onSave()
        if (cancelled) return
        blocker.proceed?.()
      } catch {
        if (!cancelled) blocker.reset?.()
      }
    })()

    return () => {
      cancelled = true
    }
  }, [blocker, cancelLabel, confirm, confirmLabel, message, onSave, title])
}
