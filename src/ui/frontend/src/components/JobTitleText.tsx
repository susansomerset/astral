import { useEffect, useState, type ReactNode } from "react"
import { createPortal } from "react-dom"
import { truncateForDisplay } from "../lib/listTableLayout"
import { getUiConfig, loadUiConfig, resolveJobTitleTruncateChars } from "../lib/uiConfig"

const TOOLTIP_GAP_PX = 4

/** AST-1981: shared job-title renderer — cuts at UI_CONFIG job_title_truncate_chars; full title in a portaled, wrapped tooltip only when cut. */
export default function JobTitleText({ title, fallback }: { title: string | null | undefined; fallback: ReactNode }) {
  const [, forceUpdate] = useState(0)
  // Same module-level UI config cache as ListPage; re-render once it resolves.
  useEffect(() => { loadUiConfig(() => forceUpdate(n => n + 1)) }, [])
  // Viewport coords of the open tooltip; null = closed.
  const [pos, setPos] = useState<{ top: number; left: number } | null>(null)
  // position:fixed would detach from the text on scroll — close instead (capture catches table/modal scrollers).
  useEffect(() => {
    if (!pos) return
    const close = () => setPos(null)
    window.addEventListener("scroll", close, true)
    return () => window.removeEventListener("scroll", close, true)
  }, [pos])

  // Caller owns the empty-title fallback ("—", company, …); never invented here.
  if (!title) return <>{fallback}</>
  const { display, full } = truncateForDisplay(title, resolveJobTitleTruncateChars(getUiConfig()))
  // Short title: plain text — no wrapper, no tooltip, no native title attribute.
  if (display === full) return <>{full}</>
  return (
    <>
      <span
        onMouseEnter={e => {
          const r = e.currentTarget.getBoundingClientRect()
          setPos({ top: r.bottom + TOOLTIP_GAP_PX, left: r.left })
        }}
        onMouseLeave={() => setPos(null)}
      >
        {display}
      </span>
      {/* Portaled to body so table / modal overflow can't clip it. */}
      {pos && createPortal(
        <div role="tooltip" className="job-title-tooltip" style={{ top: pos.top, left: pos.left }}>{full}</div>,
        document.body,
      )}
    </>
  )
}
