import { useRef, useCallback, useContext, type CSSProperties, type ReactNode } from "react"
import { createPortal } from "react-dom"
import { ConfirmContext } from "./UserPrompt"

export interface ModalProps {
  open: boolean
  onClose: () => void
  /** AST-1981: node, not string — headers host JobTitleText (cut + tooltip). Plain strings still work. */
  title: ReactNode
  children: ReactNode
  onSave?: () => void
  dirty?: boolean
  /** "fullscreen": card fills the viewport, body unpadded (split-pane modals). */
  size?: "wide" | "fullscreen"
  stacked?: boolean
  /** When false, omit Cancel/Save footer strip (default true). */
  showFooter?: boolean
}

// Inline so the size ships with the component; App.css is outside this ticket's scope.
const FULLSCREEN_CARD: CSSProperties = {
  width: "100vw",
  height: "100vh",
  maxWidth: "100vw",
  maxHeight: "100vh",
  border: "none",
  borderRadius: 0,
}
const FULLSCREEN_BODY: CSSProperties = { padding: 0, minHeight: 0, overflow: "hidden" }

export default function Modal({ open, onClose, title, children, onSave, dirty, size, stacked, showFooter = true }: ModalProps) {
  const ctxConfirm = useContext(ConfirmContext)

  // Auto-detect dirty: any input/change event inside the modal body sets the flag.
  // Callers can also override with the dirty prop.
  const touchedRef = useRef(false)
  const onBodyInput = useCallback(() => { touchedRef.current = true }, [])

  if (!open) return null

  const isDirty = dirty ?? touchedRef.current
  const fullscreen = size === "fullscreen"
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
      <div className={`modal-card${size === "wide" ? " modal-card--wide" : ""}`} style={fullscreen ? FULLSCREEN_CARD : undefined}>
        <div className="modal-header">
          <h2 className="modal-title">{title}</h2>
          <button type="button" className="icon-control" onClick={guardedClose} title="Close" aria-label="Close">×</button>
        </div>
        <div className="modal-body" style={fullscreen ? FULLSCREEN_BODY : undefined} onInput={onBodyInput} onChange={onBodyInput}>
          {children}
        </div>
        {showFooter && (
          <div className="modal-footer">
            <button className="btn secondary" onClick={guardedClose}>Cancel</button>
            {onSave && (
              <button className="btn primary" onClick={onSave}>Save</button>
            )}
          </div>
        )}
      </div>
    </div>,
    document.body
  )
}
