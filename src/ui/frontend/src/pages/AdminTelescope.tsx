/**
 * AST-1728 — Admin Telescope workbench: URL + options → raw scrape + scrape_meta.
 */
import { useCallback, useState, type CSSProperties, type FormEvent } from "react"
import Toast, { type ToastMessage } from "../components/Toast"
import api from "../lib/api"

type ResponseType = "text" | "html"

type ScrapeMeta = {
  bot_blocked?: boolean
  cookies_dismissed?: boolean
  issues?: string[]
  content_chars?: number
  requested_url?: string
  final_url?: string
}

type ScrapeResult = {
  final_url?: string
  text?: string | string[]
  html?: string | string[]
  links?: unknown
  scrape_meta?: ScrapeMeta
  [key: string]: unknown
}

function formatBody(data: ScrapeResult | null, responseType: ResponseType): string {
  if (!data) return ""
  if (responseType === "html") {
    const h = data.html
    if (Array.isArray(h)) return h.join("\n---\n")
    return typeof h === "string" ? h : ""
  }
  const t = data.text
  if (Array.isArray(t)) return t.join("\n---\n")
  return typeof t === "string" ? t : ""
}

/** AST-1730 — read-only scrollable wrapping pane (raw body + JSON dump). */
const RESPONSE_PANE_STYLE: CSSProperties = {
  display: "block",
  width: "100%",
  boxSizing: "border-box",
  minHeight: 200,
  maxHeight: "60vh",
  overflow: "auto",
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
  fontFamily: "monospace",
  fontSize: 12,
  lineHeight: 1.5,
  resize: "vertical",
}

export default function AdminTelescope() {
  const [url, setUrl] = useState("")
  const [responseType, setResponseType] = useState<ResponseType>("text")
  const [expand, setExpand] = useState(true)
  const [waitReady, setWaitReady] = useState(false)
  const [links, setLinks] = useState(true)
  const [cull, setCull] = useState(false)
  // AST-1744 — Tag is the only primary; Class name is secondary (combinable).
  const [tag, setTag] = useState("")
  const [className, setClassName] = useState("")
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<ScrapeResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const [showJson, setShowJson] = useState(false)
  const clearToast = useCallback(() => setToast(null), [])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (busy) return
    setBusy(true)
    setError(null)
    setResult(null)
    try {
      const body: Record<string, unknown> = {
        url: url.trim(),
        response_type: responseType,
        expand,
        wait_ready: waitReady,
        links: responseType === "text" ? links : true,
        cull: responseType === "html" ? cull : false,
      }
      if (tag.trim()) body.tag = tag.trim()
      if (className.trim()) body.class_name = className.trim()
      const res = await api("/api/admin/telescope", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      })
      const data = (await res.json().catch(() => ({}))) as ScrapeResult & {
        error?: string
        detail?: string
      }
      if (!res.ok) {
        const msg =
          (typeof data.error === "string" && data.error) ||
          (typeof data.detail === "string" && data.detail) ||
          `HTTP ${res.status}`
        setError(msg)
        setToast({ text: msg, variant: "error" })
        return
      }
      setResult(data)
    } catch (err) {
      const msg = (err as Error).message || "request failed"
      setError(msg)
      setToast({ text: msg, variant: "error" })
    } finally {
      setBusy(false)
    }
  }

  const meta = result?.scrape_meta

  // AST-1734 — unlock page scroll; keep list-page card chrome (do not touch global CSS).
  return (
    <div className="list-page" style={{ height: "auto", overflow: "visible" }}>
      <h1 className="list-page-title">Telescope</h1>
      <p className="list-page-subtitle">
        Call the Telescope service and inspect raw content plus scrape metadata.
      </p>

      <form className="admin-telescope-form" onSubmit={onSubmit}>
        <label className="admin-telescope-field">
          <span>URL</span>
          <input
            type="url"
            value={url}
            onChange={e => setUrl(e.target.value)}
            required
            placeholder="https://…"
          />
        </label>

        <fieldset className="admin-telescope-field">
          <legend>Response type</legend>
          <label>
            <input
              type="radio"
              name="response_type"
              checked={responseType === "text"}
              onChange={() => setResponseType("text")}
            />{" "}
            text
          </label>
          <label>
            <input
              type="radio"
              name="response_type"
              checked={responseType === "html"}
              onChange={() => setResponseType("html")}
            />{" "}
            html
          </label>
        </fieldset>

        <div className="admin-telescope-toggles">
          <label>
            <input
              type="checkbox"
              checked={expand}
              onChange={e => setExpand(e.target.checked)}
            />{" "}
            expand (scroll / Load More — not numbered pages)
          </label>
          <label>
            <input
              type="checkbox"
              checked={waitReady}
              onChange={e => setWaitReady(e.target.checked)}
            />{" "}
            wait_ready
          </label>
          <label>
            <input
              type="checkbox"
              checked={links}
              disabled={responseType === "html"}
              onChange={e => setLinks(e.target.checked)}
            />{" "}
            links
          </label>
          <label>
            <input
              type="checkbox"
              checked={cull}
              disabled={responseType === "text"}
              onChange={e => setCull(e.target.checked)}
            />{" "}
            cull (html)
          </label>
        </div>

        <label className="admin-telescope-field">
          <span>Tag (optional)</span>
          <input
            type="text"
            value={tag}
            onChange={e => setTag(e.target.value)}
            placeholder="html / div / span / body / head / ul"
          />
        </label>

        <label className="admin-telescope-field">
          <span>Class name (optional)</span>
          <input
            type="text"
            value={className}
            onChange={e => setClassName(e.target.value)}
            placeholder="shaders (no leading dot)"
          />
        </label>

        <button type="submit" disabled={busy || !url.trim()}>
          {busy ? "Scraping…" : "Scrape"}
        </button>
      </form>

      {error ? <p className="admin-telescope-error">{error}</p> : null}

      {meta ? (
        <section className="admin-telescope-meta">
          <h2>Scrape metadata</h2>
          <ul>
            <li>bot_blocked: {String(meta.bot_blocked)}</li>
            <li>cookies_dismissed: {String(meta.cookies_dismissed)}</li>
            <li>content_chars: {String(meta.content_chars ?? "")}</li>
            <li>issues: {(meta.issues || []).join(", ") || "(none)"}</li>
            <li>final_url: {result?.final_url || meta.final_url || ""}</li>
          </ul>
        </section>
      ) : null}

      {result ? (
        <section className="admin-telescope-body">
          <h2>Raw {responseType}</h2>
          <textarea
            className="admin-telescope-pre"
            readOnly
            value={formatBody(result, responseType)}
            spellCheck={false}
            style={RESPONSE_PANE_STYLE}
          />
          <button type="button" onClick={() => setShowJson(v => !v)}>
            {showJson ? "Hide" : "Show"} full JSON
          </button>
          {showJson ? (
            <textarea
              className="admin-telescope-pre"
              readOnly
              value={JSON.stringify(result, null, 2)}
              spellCheck={false}
              style={RESPONSE_PANE_STYLE}
            />
          ) : null}
        </section>
      ) : null}

      {toast ? <Toast message={toast} onDone={clearToast} /> : null}
    </div>
  )
}
