import { useCallback, useEffect, useState, type KeyboardEvent, type MouseEvent } from "react"
import { createPortal } from "react-dom"
import { useLocation } from "react-router-dom"
import { useCandidate } from "../contexts/CandidateContext"
import {
  ERROR_TOAST_DURATION_MS,
  formatDiagnosticBundle,
  type ToastMessage,
} from "../lib/toastDiagnostics"

export type { ToastMessage } from "../lib/toastDiagnostics"
export type ToastVariant = NonNullable<ToastMessage["variant"]>

interface ToastProps {
  message: ToastMessage | null
  onDone: () => void
}

const ICONS: Record<NonNullable<ToastMessage["variant"]>, string> = {
  success: "\u2713",
  error: "\u26A0", // warning — not an X lookalike (dismiss owns ×)
  info: "\u2139",
}

export default function Toast({ message, onDone }: ToastProps) {
  const [visible, setVisible] = useState(false)
  const [copied, setCopied] = useState(false)
  const { pathname } = useLocation()
  const { selectedId } = useCandidate()

  useEffect(() => {
    setCopied(false)
  }, [message])

  useEffect(() => {
    if (!message) return
    requestAnimationFrame(() => setVisible(true))
    const duration =
      message.durationMs ??
      (message.variant === "error" ? ERROR_TOAST_DURATION_MS : 3000)
    const timer = setTimeout(() => {
      setVisible(false)
      setTimeout(onDone, 300)
    }, duration)
    return () => clearTimeout(timer)
  }, [message, onDone])

  const handleClick = useCallback(async () => {
    if (!message || message.variant !== "error" || copied) return
    const bundle = formatDiagnosticBundle(message, pathname, selectedId)
    try {
      await navigator.clipboard.writeText(bundle)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      /* clipboard blocked */
    }
  }, [message, copied, pathname, selectedId])

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault()
        void handleClick()
      }
    },
    [handleClick],
  )

  // Same exit animation as the auto-dismiss timer — no clipboard write.
  const handleDismiss = useCallback(
    (e: MouseEvent) => {
      e.stopPropagation()
      e.preventDefault()
      setVisible(false)
      setTimeout(onDone, 300)
    },
    [onDone],
  )

  if (!message) return null
  const variant = message.variant ?? "info"
  const isError = variant === "error"

  return createPortal(
    <div
      className={`toast toast-${variant} ${visible ? "toast-visible" : ""}`}
    >
      <span className="toast-icon">{ICONS[variant]}</span>
      {isError ? (
        <span
          className="toast-copy-target toast-error-clickable"
          role="button"
          tabIndex={0}
          onClick={() => void handleClick()}
          onKeyDown={handleKeyDown}
        >
          <span className="toast-text">{copied ? "Copied to clipboard" : message.text}</span>
          {!copied && <span className="toast-copy-hint">Click to copy</span>}
        </span>
      ) : (
        <span className="toast-text">{message.text}</span>
      )}
      {isError && (
        <button
          type="button"
          className="icon-control"
          title="Dismiss"
          aria-label="Dismiss"
          onClick={handleDismiss}
        >
          ×
        </button>
      )}
    </div>,
    document.body,
  )
}
