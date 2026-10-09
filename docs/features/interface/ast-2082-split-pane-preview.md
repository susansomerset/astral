# AST-2082 — Split-pane layout, print preview/thumbnail, full-screen modal (Resume Edit Overhaul)

- **Parent:** [AST-2046 Resume Edit Overhaul](https://linear.app/astralcareermatch/issue/AST-2046)
- **Ticket:** [AST-2082](https://linear.app/astralcareermatch/issue/AST-2082)
- **Publish ref:** `sub/AST-2046/AST-2082-split-pane-preview` (origin only)
- **Depends on:** nothing in this epic. #3 ([AST-2083](https://linear.app/astralcareermatch/issue/AST-2083)) uses `printHtml.ts` for Print. #4 ([AST-2084](https://linear.app/astralcareermatch/issue/AST-2084)) composes `SplitPanePage`, `PrintPreview`, and `Modal size="fullscreen"`, and moves the two existing print copies onto `printHtml.ts`. None of their files are touched here.
- **Canon Scope:** `patt.artifact.read-current`.

This ticket ships four frontend building blocks and wires none of them. `SplitPanePage` is a left/right layout with a draggable divider. It fills its parent, which is `.content` on a page and the modal body inside a full-screen modal. `PrintPreview` shows builder print HTML for a base resume, a job resume, or a cover letter in an iframe. It refetches once each time its refresh key changes, and has a scaled-down, click-to-open thumbnail mode. `printHtml.ts` is the one shared helper that fetches print HTML and opens it as a blob in a new tab, with the existing error and popup-blocked handling. `Modal` gains a `fullscreen` size.

## Ground truth (verified on this branch at `f717a77ea`)

- **Layout:** `src/ui/frontend/src/components/NavigationShell.tsx` L262–263 renders `<main className="content"><Outlet /></main>`. In `src/ui/frontend/src/App.css`, `.shell` (L240) is `display: flex; height: 100vh; overflow: hidden`. `.sidebar` (L248) is 240 px with `flex-shrink: 0`. `.content` (L613) is `flex: 1; overflow-y: auto` and has **no padding**. Below 1024 px (L362–395), the sidebar is `position: fixed` (an overlay, out of flow) and `.content` gets `padding-top: 52px; width: 100%`. L215–217 sets `box-sizing: border-box` globally. Pages render straight into `.content` (e.g. `ArtifactsBaseResumeContent.tsx` returns a fragment). So a child at `width: 100%; height: 100%` already runs from the nav's right edge (0 when the nav is an overlay) to `window.innerWidth`.
- **Modal:** `src/ui/frontend/src/components/Modal.tsx` — `size?: "wide"` (L13), `className` set at L48, `.modal-body` at L53. In CSS, `.modal-card` (L1206) is `width: 560px; max-width: 90vw; max-height: 85vh; border: 1px; border-radius: 10px; flex column`. `.modal-body` (L1234) is `padding: 20px; overflow-y: auto; flex: 1`. `.modal-card--wide` (L2411–2425) is `min(1100px, 92vw) × 90vh`, with body `padding: 0; min-height: 0`. `.modal-overlay` (L1192) is `position: fixed; inset: 0`, flex-centered.
- **Print copies to replace (the callers move in #4):**
  - `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` L147–202 `handlePrint`. It calls `api('/candidate/resume/base?candidate_id=…')`. On `!r.ok` the message is the JSON `error` or `HTTP <status>`. It maps the legacy `"Candidate missing artifacts.base_resume"` to `"No printable base resume content for this candidate"`. Empty text gives `"HTML response was empty"`. Then it builds a blob URL, calls `window.open(blobUrl, "_blank")`, sets `win.opener = null` or toasts `"Popup blocked — allow popups to open the HTML tab."`, and revokes the URL after 60 000 ms. A thrown error gives `"Print failed"`.
  - `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` L244–286 `handlePrintResume` — the same sequence against `/candidate/resume/<jobId>`, without the legacy-message mapping.
  - Out of Scope (not named by the ticket): the blob copies in `AdminSessionCoverLetter.tsx` L133 and `AdminSessionResumePaste.tsx` L106 stay as they are.
- **Cover route:** `/candidate/cover/<jobId>` (used by `MaterialsPreviewModal.tsx` L27–30 and `JobAnalysisReportModal.tsx` L746).
- **HTTP helper:** `src/ui/frontend/src/lib/api.ts` — default export `api(path, options)` returns `Response` (Bearer token + `credentials: "include"`).
- **Print HTML width:** `src/core/builder.py` L1290 `--max-width: 800px`. L1501 has a `@media (max-width: 600px)` mobile breakpoint.
- **Error text class:** `.entity-error` (App.css L2603: danger color, 13 px, 16 px padding) is already used by the entity modals.
- **ESLint:** `eslint.config.js` enables `react-hooks` recommended and `react-refresh/only-export-components`.
- **Tooling:** this worktree has **no `src/ui/frontend/node_modules`**. Run `npm ci` in `src/ui/frontend` once before the first build or lint.
- **Existing tests:** `tests/component/frontend/components/test_Modal.test.tsx` uses `size="wide"` (L59, L181). Those callers are unchanged, so no known test drift.

## Canon conformance — `patt.artifact.read-current`

The preview and thumbnail never hold their own copy of resume or cover content. Every render reads the builder print routes. Those routes current-read the artifacts on the server. The preview refetches whenever its caller signals that a save landed (`refreshKey`), and it never hydrates from `*_data` blob fields on the client. The fetched HTML is kept only as the iframe's `srcDoc` for display, and the next refresh replaces it.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/printHtml.ts` | **New** — `PrintTarget`, `PrintHtmlResult`, `POPUP_BLOCKED_MESSAGE`, `fetchPrintHtml`, `openHtmlInNewTab` | ui (lib) |
| `src/ui/frontend/src/components/PrintPreview.tsx` | **New** — full-panel iframe / click-to-open thumbnail; refetch on `refreshKey` | ui (component) |
| `src/ui/frontend/src/components/SplitPanePage.tsx` | **New** — left / divider / right, drag-resizable, fills parent | ui (component) |
| `src/ui/frontend/src/components/Modal.tsx` | `size` gains `"fullscreen"` (inline card + body styles) | ui (component) |

No other files. No `App.css` edits (that file is #3's scope).

## Stage 1: Shared print-HTML helper

**Done when:** `src/ui/frontend/src/lib/printHtml.ts` exists with the exports below. `npm run build` passes, and `npx eslint src/lib/printHtml.ts` reports 0 problems. No component imports it yet.

1. In `src/ui/frontend`, if `node_modules` is absent, run `npm ci`.
2. Create `src/ui/frontend/src/lib/printHtml.ts` with exactly this content:

```ts
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
```

⚠️ **Decision:** The helpers return values instead of toasting. Toast state is local to each page or modal (`setToast`), so the caller shows `result.error` or the returned popup message in its own toast. `POPUP_BLOCKED_MESSAGE` is exported so the copy lives in one place. Pre-print structure persistence (`persistStructureRows` in both current copies) stays a caller concern. The parent drops it for the job Print in #4.

⚠️ **Decision:** `PrintTarget` is `{ kind, id }` (one id field) rather than a union with `candidateId`/`jobId`. That lets `PrintPreview` key its effect on two primitives (Stage 2) without an `exhaustive-deps` suppression. The path table is keyed by `kind`.

3. Run `npm run build` and `npx eslint src/lib/printHtml.ts` from `src/ui/frontend`. Both must pass with 0 errors.
4. Commit: `code(AST-2082): printHtml shared fetch/open helper`.

## Stage 2: PrintPreview (full panel + thumbnail)

**Done when:** `src/ui/frontend/src/components/PrintPreview.tsx` exists as below. Build and `npx eslint src/components/PrintPreview.tsx` pass. With a valid target, the full mode renders one `<iframe title="Print preview">` whose `srcDoc` is exactly the route's body. With a failing route, it renders `<p class="entity-error">` with the error text. A `refreshKey` change triggers exactly one new GET.

1. Create `src/ui/frontend/src/components/PrintPreview.tsx` with exactly this content:

```tsx
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
```

⚠️ **Decision:** The thumbnail renders the HTML in an 816 × 1056 iframe (US Letter at 96 dpi) and scales it to 25%, giving a 204 × 264 px box. 816 px keeps the builder's 600 px mobile breakpoint from kicking in, so the thumbnail looks like the printed page. These are layout constants, not config. Thumbnail *eligibility* is #1's config flag, read by #4.

⚠️ **Decision:** On a refresh, the previous HTML stays on screen until the new response lands, so there is no blank flash between saves. A `live` flag drops a response that comes back after the target or `refreshKey` has changed, so an older response never overwrites a newer one.

⚠️ **Decision:** The thumbnail wrapper carries `className="print-preview-thumb"` with no rules in this ticket. It is the hook for #3's thumbnail styles in `App.css` (border, hover). Size and scale stay inline because they are computed from the constants above.

2. Run `npm run build` and `npx eslint src/components/PrintPreview.tsx`. Both must pass with 0 errors.
3. Commit: `code(AST-2082): PrintPreview full panel and thumbnail`.

## Stage 3: SplitPanePage + full-screen Modal

**Done when:** `SplitPanePage.tsx` exists as below, and `Modal` accepts `size="fullscreen"`. Build and `npx eslint src/components/SplitPanePage.tsx src/components/Modal.tsx` pass. Inside a full-width parent, dragging the divider 100 px right grows the left panel by 100 px and shrinks the right panel by 100 px. A `size="fullscreen"` modal's card is `100vw × 100vh` with a padding-free body, and `size="wide"` / no-size modals render exactly as before.

1. Create `src/ui/frontend/src/components/SplitPanePage.tsx` with exactly this content:

```tsx
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
```

⚠️ **Decision:** There is no `mode` prop. Page mode and modal mode are the same thing: fill the parent. `.content` has no padding and already runs from the nav's right edge (0 when the nav is an overlay below 1024 px) to `window.innerWidth`. The full-screen modal body (step 2) is `100vw` with no padding. So `width/height: 100%` meets parent AC1 in both places with no measuring. If Joan or Susan wants an explicit `mode` prop anyway, it would be a no-op.

⚠️ **Decision:** The initial split is 50/50 (`calc(50% - 3px)` each side of a 6 px divider) until the first drag. After that, the left width is a pixel value in state. Dragging is clamped only to the container (`0 … containerWidth − divider`), with **no** minimum panel width. A minimum would be an added limit; say so if you want one.

⚠️ **Decision:** The drag uses `mousedown` on the divider plus `mousemove`/`mouseup` on `window`, not pointer capture. jsdom implements neither `PointerEvent` nor `setPointerCapture`, so this keeps Betty's component tests and Playwright drags on the same path. While dragging, both panels get `pointer-events: none` and the root gets `user-select: none`. Without that, moving across the preview iframe stops the drag (the iframe swallows the events) and the left text gets selected.

2. In `src/ui/frontend/src/components/Modal.tsx`:
   - Change the import on L1 to `import { useRef, useCallback, useContext, type CSSProperties, type ReactNode } from "react"`.
   - Change L13 `size?: "wide"` to `size?: "wide" | "fullscreen"`, and add the doc comment `/** "fullscreen": card fills the viewport, body unpadded (split-pane modals). */` on the line above it.
   - After the `ModalProps` interface (before `export default function Modal`), add:

```tsx
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
```

   - In the component body, after `const isDirty = …`, add `const fullscreen = size === "fullscreen"`.
   - On the `modal-card` div (L48), keep the existing `className` expression unchanged and add `style={fullscreen ? FULLSCREEN_CARD : undefined}`.
   - On the `modal-body` div (L53), keep `className`, `onInput`, and `onChange` unchanged and add `style={fullscreen ? FULLSCREEN_BODY : undefined}`.
   - Change nothing else (header, footer, dirty guard, `stacked`, portal).

⚠️ **Decision:** The full-screen size uses inline styles on the card and body instead of a `.modal-card--fullscreen` CSS rule, because `App.css` belongs to #3. `border: none` is required: with the 1 px card border, the split pane would be `100vw − 2px` and fail parent AC1 ("both panels together span the viewport width"). The body's `overflow: hidden` + `min-height: 0` let `SplitPanePage` (`height: 100%`) fill exactly the space under the header, with the panels scrolling on their own. The header (title + ×) stays. Callers choose `showFooter={false}` and leave out `onSave` for autosave surfaces (#4). Without `onSave`, the dirty-discard prompt never fires.

3. Run `npm run build` and `npx eslint src/components/SplitPanePage.tsx src/components/Modal.tsx`. Both must pass with 0 errors.
4. Commit: `code(AST-2082): SplitPanePage and fullscreen Modal size`.

## Integration notes (for siblings — no work here)

- **#3 `ResumeContentEditor` Print:** `const r = await fetchPrintHtml(target); if (!r.ok) toast(r.error); else { const blocked = openHtmlInNewTab(r.html); if (blocked) toast(blocked) }`.
- **#4 Base page:** `<SplitPanePage left={<ResumeContentEditor … onSaved={() => setRefreshKey(k => k + 1)} />} right={<PrintPreview target={{ kind: "base", id: selectedId }} refreshKey={refreshKey} />} />`.
- **#4 Job edit modal:** `<Modal size="fullscreen" stacked showFooter={false} …><SplitPanePage … /></Modal>`. Thumbnails use `<PrintPreview thumbnail target={{ kind: "job_resume" | "cover", id: jobId }} onClick={…} />`.
- **#4 replaces** the print copies in `ArtifactsBaseResumeContent.tsx` and `JobAnalysisReportModal.tsx` with the Stage 1 helpers.

## Parent AC coverage

- **AC1 (spans content area):** Stage 3 (fill-parent layout + full-screen modal). Observable once #4 mounts it.
- **AC2 (divider resizes ±2 px):** Stage 3 drag math (`startWidth + dx`, right panel `flex: 1`).
- **AC3 (preview = print HTML):** Stage 2 `srcDoc` = the exact response body from the Stage 1 route table.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2082
**Overall:** APPROVED
**Corpus:** 2d1b73da19cf1d14276e5c26f52b37aa8047d159
**Publish ref:** `origin/sub/AST-2046/AST-2082-split-pane-preview` @ `495a7901c`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.read-current | A | | |

## Traceability

AC1→S3 (fill-parent + fullscreen modal body; end-to-end proof in #4) · AC2→S3 (divider drag math) · AC3→S1–S2 (route table + iframe `srcDoc` = GET body)

## Findings

### acceptable — AC1–AC3 observable only after #4 wires surfaces
- **Severity:** acceptable
- **Location:** `## Parent AC coverage`, ticket `## Boundaries`
- **Finding:** This child ships primitives only; split-pane span and live preview in Base Resume / job modal are integration tests for AST-2084, not missing plan stages here.
- **Recommendation:** Betty/Radia UAT on #4 for parent AC1–3; this ticket’s Done-when commands stay component-level.

### acceptable — No `## Self-assessment` block
- **Severity:** acceptable
- **Location:** Plan doc structure
- **Finding:** Estimate confirm only; no conf/self-assessment section.
- **Recommendation:** Optional; not blocking (consistent with AST-2081-style backend/UI slice plans).

### discuss — Split pane has no minimum panel width
- **Severity:** discuss
- **Location:** Stage 3 `SplitPanePage` drag clamp (`0 … maxWidth`)
- **Finding:** A hard drag can collapse a panel to zero width; parent AC2 only asserts ±2 px coupling on a 100 px move, not a floor.
- **Recommendation:** If Susan wants a usability floor, add it in plan or defer to #4 polish; not a canon or scope defect.

### discuss — Canon Scope gap (informational)
- **Severity:** discuss
- **Location:** Frozen list vs new files under `src/ui/frontend/src/{components,lib}`
- **Finding:** `astral.ui.frontend-file-placement` and `astral.layers.import-direction` plainly govern placement/imports but are not on this ticket’s list; plan follows normal `components/` + `lib/` layout and `../lib/printHtml` imports.
- **Recommendation:** No list change mid-flight; Archie may add on a future frontend-heavy child if the team wants explicit scoring.

## R6 (summary)

Definition fidelity: Four files match AST-2082 `## Scope`; no #3/#4 files touched. `printHtml.ts` centralizes the two documented print copies (callers migrate in #4). `PrintPreview` refetches on `refreshKey` + primitive target keys; no `*_data` client hydrate. `SplitPanePage` and fullscreen `Modal` inline styles respect “no App.css in this ticket.” Ground truth cites NavigationShell, Modal CSS, and existing print handlers. Stages are ordered (helper → preview → layout/modal) with explicit decisions (toast at caller, no `mode` prop, pointer-events during drag, fullscreen borderless for true `100vw`).

context_tokens≈52000

## Review (build)

**Built:** `origin/sub/AST-2046/AST-2082-split-pane-preview` @ `78edbc31c` (last code commit; branch since synced with refreshed ftr `dbd1611bc`)

Stages 1–3: `b701b6f36` `printHtml.ts` (`fetchPrintHtml`, `openHtmlInNewTab`, `POPUP_BLOCKED_MESSAGE`) · `821e81632` `PrintPreview.tsx` (full-panel `srcDoc` iframe, 204 × 264 thumbnail, refetch on `refreshKey`) · `78edbc31c` `SplitPanePage.tsx` + `Modal` `size="fullscreen"`. `npm run build`, `tsc -b --noEmit`, and eslint on all four files clean; `test_Modal.test.tsx` 8 passed (unchanged). Tests deferred to Betty — no known drift.

**Deviations:** none. No minimum panel width (per Joan discuss note + Susan).

## Radia review

[code-rubric]
**Ticket:** AST-2082
**Publish ref:** `3d101f16e9bc60349ebf8fdeb85be2999145a9c5` (`origin/sub/AST-2046/AST-2082-split-pane-preview`)
**Corpus:** `2d1b73da19cf1d14276e5c26f52b37aa8047d159`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.read-current | A | | |

## Column diff vs plan stage

(aligned) — Joan **A**; code **A**.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

- **Minimum panel width** — `SplitPanePage.tsx` drag clamp `Math.max(0, …)` allows zero-width panels (Joan plan discuss; build note: no floor per Susan).
  - **@susan:** Add a minimum left/right width (e.g. 120px) before #4 wires surfaces, or keep collapse-to-zero until polish?
  - **Default:** Leave as shipped; revisit in **AST-2084** if split-pane UX feels broken in UAT.

### advisory

- **Sibling product carry (stacked publish ref):** `git diff origin/dev...origin/sub/AST-2046/AST-2082-split-pane-preview` includes **AST-2081** backend product (`src/core/{builder,candidate,tracker}.py`, `src/ui/api/api_{candidate,jobs}.py`, `src/utils/config.py`) from `sync(ftr)` / 2081 commits on the same ref. **AST-2082-only commits** (`b701b6f36`, `821e81632`, `78edbc31c`) touch only the four scoped frontend files. Score this ticket against those commits; do not re-litigate 2081 canon on 2082’s upshot (2081 review is separate).
- **Sibling test/bible carry:** `merge-tests` / ftr sync also pulls `test_roster.py`, theme/BatchAgent modal tests, and bible rows for **AST-2081** and other siblings — expected on epic subs.
- **Parent AC1–AC3:** Observable end-to-end only after **AST-2084** composes these primitives (Joan acceptable); component tests on this ref cover `printHtml`, `PrintPreview`, `SplitPanePage`, and fullscreen `Modal`.
- **Canon Scope (informational):** `astral.ui.frontend-file-placement` / `astral.layers.import-direction` govern layout but are off the frozen list (Joan note); placement matches plan (`components/`, `lib/printHtml.ts`).

## What’s solid

- **`printHtml.ts`:** Single SoT for builder print GET paths; legacy base-resume error mapping preserved; `openHtmlInNewTab` matches existing popup/revoke behavior.
- **`PrintPreview`:** No client hydrate from `*_data` blobs; each `refreshKey` / target change triggers `fetchPrintHtml` (server routes current-read artifacts); iframe `srcDoc` is display-only; thumbnail uses `pointerEvents: "none"` and drag-safe `SplitPanePage` panel styling.
- **`SplitPanePage` / `Modal`:** Match plan (50/50 until drag, window listeners + cleanup, fullscreen inline card/body without `App.css`; `wide` path unchanged).

## Recommended actions (for Chuckles — not Radia)

- Append this artifact under `## Review (code)` (or equivalent) in `docs/features/interface/ast-2082-split-pane-preview.md`; commit `docs(AST-2082): Radia review — clean`; push publish ref.
- Post slim upshot via `linear_proxy.py --as radia save-comment`.
- **Review Posted** → datt **§3h** **PROCEED** toward UT (no resolve-child canon work unless Susan answers min-width discuss).

```
[code-rubric] PROCEED (Commit: 3d101f16e) Preview via print GET; four files
```

context_tokens≈28000

**Chuckles:** Clean (PROCEED, no fix-now). Discuss item (minimum panel width) is a product call for Susan, not engineer work; default stands (no floor, revisit in AST-2084 UAT). The "no floor" instruction came from Chuckles relaying the Joan-approved plan, not from Susan. Clean-review shortcut (do-all-the-things §3h) → User Testing.
