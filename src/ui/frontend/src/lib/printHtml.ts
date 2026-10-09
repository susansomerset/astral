import api from "./api"

/** Which builder print route to read. `id` is the candidate id for `base`, else the job id. */
export interface PrintTarget {
  kind: "base" | "job_resume" | "cover"
  id: string
}

export type PrintHtmlResult = { ok: true; html: string } | { ok: false; error: string }

export const POPUP_BLOCKED_MESSAGE = "Popup blocked — allow popups to open the HTML tab."

// Builder print routes keyed by target kind; each current-reads its artifact server-side.
const PRINT_PATHS: Record<PrintTarget["kind"], (id: string) => string> = {
  base: id => `/candidate/resume/base?candidate_id=${encodeURIComponent(id)}`,
  job_resume: id => `/candidate/resume/${encodeURIComponent(id)}`,
  cover: id => `/candidate/cover/${encodeURIComponent(id)}`,
}

/** GET the print HTML; failures come back as the builder's error text (never thrown). */
export async function fetchPrintHtml(target: PrintTarget): Promise<PrintHtmlResult> {
  try {
    const r = await api(PRINT_PATHS[target.kind](target.id))
    if (!r.ok) {
      let msg = `HTTP ${r.status}`
      try {
        const data = await r.json()
        if (typeof data.error === "string" && data.error) msg = data.error
      } catch { /* non-JSON error body */ }
      // Legacy internal key-path error for an empty base reads as the operator copy.
      if (target.kind === "base" && msg === "Candidate missing artifacts.base_resume") {
        msg = "No printable base resume content for this candidate"
      }
      return { ok: false, error: msg }
    }
    const html = await r.text()
    return html.trim() ? { ok: true, html } : { ok: false, error: "HTML response was empty" }
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : "Print failed" }
  }
}

/** Open HTML as a blob in a new tab. Returns POPUP_BLOCKED_MESSAGE when blocked, else null. */
export function openHtmlInNewTab(html: string): string | null {
  const blobUrl = URL.createObjectURL(new Blob([html], { type: "text/html;charset=utf-8" }))
  // No noopener/noreferrer features — those force a null return even on success.
  const win = window.open(blobUrl, "_blank")
  window.setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000)
  if (!win) return POPUP_BLOCKED_MESSAGE
  win.opener = null
  return null
}
