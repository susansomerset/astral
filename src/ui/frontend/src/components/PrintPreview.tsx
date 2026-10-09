import { useEffect, useState } from "react"
import { fetchPrintHtml, type PrintHtmlResult, type PrintTarget } from "../lib/printHtml"

// US Letter at 96 dpi: wider than the builder's 600px mobile breakpoint, so the
// thumbnail shows the printed layout, then scales it down.
const PAGE_W = 816
const PAGE_H = 1056
const THUMB_SCALE = 0.25

export interface PrintPreviewProps {
  target: PrintTarget
  /** Bump after a save lands; each change refetches once. */
  refreshKey?: number
  /** Scaled-down, non-interactive render; clicks go to `onClick`. */
  thumbnail?: boolean
  onClick?: () => void
}

export default function PrintPreview({ target, refreshKey = 0, thumbnail = false, onClick }: PrintPreviewProps) {
  const { kind, id } = target
  const [result, setResult] = useState<PrintHtmlResult | null>(null)

  // Keyed on primitives so a fresh target object from the caller does not refetch.
  useEffect(() => {
    let live = true
    void fetchPrintHtml({ kind, id }).then(r => { if (live) setResult(r) })
    return () => { live = false }
  }, [kind, id, refreshKey])

  if (result && !result.ok) return <p className="entity-error">{result.error}</p>

  if (!thumbnail) {
    return result ? (
      <iframe
        title="Print preview"
        srcDoc={result.html}
        style={{ display: "block", width: "100%", height: "100%", border: 0 }}
      />
    ) : null
  }

  return (
    <div
      className="print-preview-thumb"
      onClick={onClick}
      style={{
        width: PAGE_W * THUMB_SCALE,
        height: PAGE_H * THUMB_SCALE,
        overflow: "hidden",
        cursor: onClick ? "pointer" : undefined,
      }}
    >
      {result && (
        <iframe
          title="Print preview"
          srcDoc={result.html}
          tabIndex={-1}
          scrolling="no"
          style={{
            width: PAGE_W,
            height: PAGE_H,
            border: 0,
            transform: `scale(${THUMB_SCALE})`,
            transformOrigin: "0 0",
            pointerEvents: "none",
          }}
        />
      )}
    </div>
  )
}
