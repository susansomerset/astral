import { useEffect, useState } from "react"
import { createPortal } from "react-dom"

export type ToastVariant = "success" | "error" | "info"

export interface ToastMessage {
  text: string
  variant?: ToastVariant
  durationMs?: number
}

interface ToastProps {
  message: ToastMessage | null
  onDone: () => void
}

const ICONS: Record<ToastVariant, string> = {
  success: "\u2713",
  error: "\u2717",
  info: "\u2139",
}

export default function Toast({ message, onDone }: ToastProps) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (!message) return
    // Trigger enter animation on next frame
    requestAnimationFrame(() => setVisible(true))
    const timer = setTimeout(() => {
      setVisible(false)
      setTimeout(onDone, 300) // wait for exit animation
    }, message.durationMs ?? 3000)
    return () => clearTimeout(timer)
  }, [message, onDone])

  if (!message) return null
  const variant = message.variant ?? "info"

  return createPortal(
    <div className={`toast toast-${variant} ${visible ? "toast-visible" : ""}`}>
      <span className="toast-icon">{ICONS[variant]}</span>
      <span className="toast-text">{message.text}</span>
    </div>,
    document.body
  )
}
