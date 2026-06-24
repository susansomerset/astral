import { useCallback, useEffect, useState, type KeyboardEvent } from "react"
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
  error: "\u2717",
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

  if (!message) return null
  const variant = message.variant ?? "info"
  const isError = variant === "error"

  return createPortal(
    <div
      className={`toast toast-${variant} ${visible ? "toast-visible" : ""}${isError ? " toast-error-clickable" : ""}`}
      role={isError ? "button" : undefined}
      tabIndex={isError ? 0 : undefined}
      onClick={isError ? () => void handleClick() : undefined}
      onKeyDown={isError ? handleKeyDown : undefined}
    >
      <span className="toast-icon">{ICONS[variant]}</span>
      <span className="toast-text">{copied ? "Copied to clipboard" : message.text}</span>
      {isError && !copied && (
        <span className="toast-copy-hint">Click to copy</span>
      )}
    </div>,
    document.body,
  )
}
