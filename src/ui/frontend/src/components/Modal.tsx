import { useRef, useCallback, useContext, type ReactNode } from "react"
import { createPortal } from "react-dom"
import { ConfirmContext } from "./UserPrompt"

export interface ModalProps {
  open: boolean
  onClose: () => void
  title: string
  children: ReactNode
  onSave?: () => void
  dirty?: boolean
  size?: "wide"
  stacked?: boolean
}

export default function Modal({ open, onClose, title, children, onSave, dirty, size, stacked }: ModalProps) {
  const ctxConfirm = useContext(ConfirmContext)

  // Auto-detect dirty: any input/change event inside the modal body sets the flag.
  // Callers can also override with the dirty prop.
  const touchedRef = useRef(false)
  const onBodyInput = useCallback(() => { touchedRef.current = true }, [])

  if (!open) return null

  const isDirty = dirty ?? touchedRef.current
  const guardedClose = async () => {
    if (isDirty && onSave) {
      // Without UserPromptProvider (unit tests): use synchronous window.confirm so fireEvent-driven tests behave.
      const discard = ctxConfirm
        ? await ctxConfirm("You have unsaved changes. Discard them?", {
            title: "Discard changes?",
            confirmLabel: "Discard",
            variant: "danger",
          })
        : window.confirm("You have unsaved changes. Discard them?")
      if (!discard) return
    }
    touchedRef.current = false
    onClose()
  }

  return createPortal(
    <div className={`modal-overlay${stacked ? " modal-overlay--stacked" : ""}`}>
      <div className={`modal-card${size === "wide" ? " modal-card--wide" : ""}`}>
        <div className="modal-header">
          <h2 className="modal-title">{title}</h2>
          <button className="modal-close" onClick={guardedClose} aria-label="Close">×</button>
        </div>
        <div className="modal-body" onInput={onBodyInput} onChange={onBodyInput}>
          {children}
        </div>
        <div className="modal-footer">
          <button className="modal-btn cancel" onClick={guardedClose}>Cancel</button>
          {onSave && (
            <button className="modal-btn save" onClick={onSave}>Save</button>
          )}
        </div>
      </div>
    </div>,
    document.body
  )
}
