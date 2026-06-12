import { createContext, useCallback, useContext, useRef, useState, type ReactNode } from "react"
import { createPortal } from "react-dom"

export type UserConfirmOptions = {
  title?: string
  confirmLabel?: string
  cancelLabel?: string
  variant?: "default" | "danger"
}

type Pending = { message: string } & Required<Pick<UserConfirmOptions, "title" | "confirmLabel" | "cancelLabel" | "variant">>

// eslint-disable-next-line react-refresh/only-export-components -- shared with Modal for sync confirm fallback path
export const ConfirmContext = createContext<((message: string, opts?: UserConfirmOptions) => Promise<boolean>) | null>(null)

/** Themed confirm dialog (replaces `window.confirm`). Prefer `UserPromptProvider` above the tree; without it, falls back to `window.confirm` (Storybook/tests). */
// eslint-disable-next-line react-refresh/only-export-components -- hook + provider same module
export function useUserConfirm() {
  const ctxFn = useContext(ConfirmContext)
  const fallback = useCallback((message: string, opts?: UserConfirmOptions): Promise<boolean> => {
    void opts
    return Promise.resolve(window.confirm(message))
  }, [])
  return ctxFn ?? fallback
}

export function UserPromptProvider({ children }: { children: ReactNode }) {
  const [pending, setPending] = useState<Pending | null>(null)
  const resolveRef = useRef<((ok: boolean) => void) | null>(null)

  const confirm = useCallback((message: string, opts?: UserConfirmOptions) => {
    return new Promise<boolean>(resolve => {
      resolveRef.current = resolve
      setPending({
        message,
        title: opts?.title ?? "Confirm",
        confirmLabel: opts?.confirmLabel ?? "OK",
        cancelLabel: opts?.cancelLabel ?? "Cancel",
        variant: opts?.variant ?? "default",
      })
    })
  }, [])

  const finish = (ok: boolean) => {
    resolveRef.current?.(ok)
    resolveRef.current = null
    setPending(null)
  }

  return (
    <ConfirmContext.Provider value={confirm}>
      {children}
      {pending && createPortal(
        <div
          className="modal-overlay user-prompt-overlay"
          role="presentation"
          onClick={() => finish(false)}
        >
          <div
            className="modal-card user-prompt-card"
            role="alertdialog"
            aria-labelledby="user-prompt-title"
            aria-describedby="user-prompt-message"
            onClick={e => e.stopPropagation()}
          >
            <div className="modal-header">
              <h2 id="user-prompt-title" className="modal-title">{pending.title}</h2>
            </div>
            <div className="modal-body">
              <p id="user-prompt-message" className="user-prompt-message">{pending.message}</p>
            </div>
            <div className="modal-footer">
              <button type="button" className="modal-btn cancel" onClick={() => finish(false)}>
                {pending.cancelLabel}
              </button>
              <button
                type="button"
                className={`modal-btn${pending.variant === "danger" ? " danger" : " save"}`}
                onClick={() => finish(true)}
              >
                {pending.confirmLabel}
              </button>
            </div>
          </div>
        </div>,
        document.body,
      )}
    </ConfirmContext.Provider>
  )
}
