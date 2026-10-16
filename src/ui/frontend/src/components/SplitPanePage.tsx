import { useEffect, useRef, useState, type CSSProperties, type MouseEvent as ReactMouseEvent, type ReactNode } from "react"

const DIVIDER_PX = 6

export interface SplitPanePageProps {
  left: ReactNode
  right: ReactNode
}

/**
 * Left | divider | right, filling its parent: `.content` as a page (nav edge to
 * viewport right, no padding there) or the body of a fullscreen Modal.
 * Inline styles because the left width is drag-driven state.
 */
export default function SplitPanePage({ left, right }: SplitPanePageProps) {
  const rootRef = useRef<HTMLDivElement>(null)
  const leftRef = useRef<HTMLDivElement>(null)
  // null until the first drag: left starts at half the container.
  const [leftWidth, setLeftWidth] = useState<number | null>(null)
  const [dragging, setDragging] = useState(false)
  const stopDragRef = useRef<(() => void) | null>(null)

  // Unmount mid-drag must not leave window listeners behind.
  useEffect(() => () => stopDragRef.current?.(), [])

  function startDrag(e: ReactMouseEvent) {
    if (!rootRef.current || !leftRef.current) return
    e.preventDefault()
    const startX = e.clientX
    const startWidth = leftRef.current.getBoundingClientRect().width
    const maxWidth = rootRef.current.getBoundingClientRect().width - DIVIDER_PX
    // Clamped to the container only, so neither panel can go negative or overflow.
    const onMove = (ev: MouseEvent) =>
      setLeftWidth(Math.min(maxWidth, Math.max(0, startWidth + ev.clientX - startX)))
    const stop = () => {
      window.removeEventListener("mousemove", onMove)
      window.removeEventListener("mouseup", stop)
      stopDragRef.current = null
      setDragging(false)
    }
    window.addEventListener("mousemove", onMove)
    window.addEventListener("mouseup", stop)
    stopDragRef.current = stop
    setDragging(true)
  }

  // Mid-drag the panels ignore the pointer, or the preview iframe would swallow mousemove.
  const panel: CSSProperties = { height: "100%", overflow: "auto", pointerEvents: dragging ? "none" : undefined }

  return (
    <div
      ref={rootRef}
      style={{ display: "flex", width: "100%", height: "100%", overflow: "hidden", userSelect: dragging ? "none" : undefined }}
    >
      <div ref={leftRef} style={{ ...panel, flexShrink: 0, width: leftWidth ?? `calc(50% - ${DIVIDER_PX / 2}px)` }}>
        {left}
      </div>
      <div
        role="separator"
        aria-orientation="vertical"
        onMouseDown={startDrag}
        style={{ width: DIVIDER_PX, flexShrink: 0, cursor: "col-resize", background: "var(--border)" }}
      />
      <div style={{ ...panel, flex: 1, minWidth: 0 }}>{right}</div>
    </div>
  )
}
