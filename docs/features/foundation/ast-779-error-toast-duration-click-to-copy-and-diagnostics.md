# AST-779 — Error toast duration, click-to-copy, and diagnostics (Update error toast)

- **Linear (this ticket):** [AST-779](https://linear.app/astralcareermatch/issue/AST-779/error-toast-duration-click-to-copy-and-diagnostics-update-error-toast)
- **Parent:** [AST-770](https://linear.app/astralcareermatch/issue/AST-770/update-error-toast)
- **Publish ref:** `origin/sub/AST-770/AST-779-error-toast-diagnostics`

## Summary

Extend the shared `Toast` component so **error** toasts stay visible ~15 seconds, look clickable, and copy a multi-line diagnostic bundle to the clipboard on click (with brief “Copied” feedback). Add small frontend helpers to attach API/route/candidate context to error toasts without breaking pages that only pass `{ text, variant: "error" }`. Add a shared Flask helper plus a global `/api/*` exception handler so 500 responses include `exception_type` and `traceback` when available.

## Layer contract (mandatory)

| Layer | This ticket | Import rule |
|-------|-------------|-------------|
| `src/ui/api_errors.py` | **New** — shared JSON error payload + traceback enrichment | ui (Flask helpers) |
| `src/ui/server.py` | Register `/api/*` exception handler | ui |
| `src/ui/frontend/src/lib/toastDiagnostics.ts` | **New** — duration constant, bundle formatter, `ApiError` class | frontend only |
| `src/ui/frontend/src/components/Toast.tsx` | 15s error duration, click-to-copy, copied state | frontend only |
| `src/ui/frontend/src/App.css` | Clickable error affordance styles | frontend only |
| `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | Representative admin — wire `ApiError` on API failure paths | frontend only |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | Representative candidate — wire `ApiError` on save failure | frontend only |
| All other pages / blueprints | **Read-only** unless build hits a literal blocker | — |

⚠️ **Decision:** **Error duration** defaults inside `Toast.tsx`: when `variant === "error"` and `durationMs` is omitted, use **`15000`**. Success/info keep **`3000`** (current default). Pages may still override with explicit `durationMs`.

⚠️ **Decision:** **Click-to-copy** applies only to **`variant === "error"`**. Success/info toasts remain non-interactive (`pointer-events: none` preserved for those variants).

⚠️ **Decision:** **Auto context at copy time** — `Toast` reads `useLocation()` pathname and `useCandidate().selectedId` when building the clipboard bundle. Callers that only pass `{ text, variant: "error" }` still get route + candidate id in the copy payload (AC 3–4) without refactors across every page.

⚠️ **Decision:** **Optional `diagnostics` field** on `ToastMessage` carries API-sourced fields (`http_status`, `api_path`, `exception_type`, `traceback`, `response_body`, etc.). Representative pages **AdminAgentPrompts** and **CandidateProfile** use `readApiError(response)` so enriched backend fields flow into copy bundles (AC 5). Other pages unchanged.

⚠️ **Decision:** **Backend enrichment** via new `api_errors.py` + `@app.errorhandler(Exception)` registered in `server.py` for paths starting with `/api/`. Uncaught exceptions return JSON `{ "error": "<message>", "exception_type": "<class name>", "traceback": "<formatted tb>" }` with status 500. Explicit handler responses must **never** include `Authorization` headers, cookies, or env secrets. Existing `{ "error": "..." }`-only responses remain valid; enrichment is additive.

⚠️ **Decision:** **Copy confirmation** — on successful clipboard write, swap toast text to **"Copied to clipboard"** (keep error styling) for **2 seconds**, then restore the original message and **do not reset** the 15s dismiss timer (AC 6).

## Out of scope (explicit)

| Item | Owner |
|------|-------|
| Refactoring every page’s `.catch()` to use `ApiError` | Future — only two representative pages in this ticket |
| Refactoring every blueprint `jsonify({"error": ...})` call site | Future — global 500 handler + helper for new code |
| AST-538 debug-logging contract on batch/dispatch paths | Out of epic boundary |
| Admin Performance Monitor changes | Out of epic boundary |
| Committing under `tests/` or `docs/ASTRAL_TEST_BIBLE.md` | **Betty** (`qa-child`) — engineer pre-commit hook blocks |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api_errors.py` | **New** — `error_json`, `server_error_from_exception` | ui |
| `src/ui/server.py` | Register `/api/*` exception handler | ui |
| `src/ui/frontend/src/lib/toastDiagnostics.ts` | **New** — types, formatter, `ApiError`, `readApiError`, `errorToastFromApiError` | ui |
| `src/ui/frontend/src/components/Toast.tsx` | Duration, click-to-copy, copied state, context hooks | ui |
| `src/ui/frontend/src/App.css` | `.toast-error` clickable affordance | ui |
| `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | Use `readApiError` on failing admin agent API calls | ui |
| `src/ui/frontend/src/pages/CandidateProfile.tsx` | Use `readApiError` on profile save failure | ui |
| `tests/component/frontend/components/test_Toast.test.tsx` | Extend for 15s error, click-copy, copied feedback | tests (Betty manifest) |
| `tests/component/ui/api/test_api_errors.py` | **New** — handler returns enriched 500 JSON | tests (Betty manifest) |
| `docs/ASTRAL_TEST_BIBLE.md` | AST-779 manifest rows | bible (Betty) |

## Stage 1: Backend API error enrichment

**Done when:** Uncaught exception on any `/api/*` route returns JSON with `error`, `exception_type`, and `traceback` keys (status 500); non-API routes unaffected; `python -m compileall src/ui` passes.

1. Create `src/ui/api_errors.py` with:

```python
import traceback
from typing import Any

from flask import jsonify


def error_json(message: str, status: int = 400, **extra: Any):
    """Return (Response, status). Always includes \"error\" key; extra keys are optional enrichments."""
    body: dict[str, Any] = {"error": message}
    for key, value in extra.items():
        if value is not None:
            body[key] = value
    return jsonify(body), status


def server_error_from_exception(exc: BaseException):
    """500 payload for toast diagnostics — no secrets, no request headers."""
    return error_json(
        str(exc) or exc.__class__.__name__,
        500,
        exception_type=exc.__class__.__name__,
        traceback="".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
    )
```

2. In `src/ui/server.py`, after blueprint registration and before `bootstrap_runtime()` (or immediately after blueprints — pick one spot and keep handler registration before `if __name__` only runs in dev), add:

```python
from flask import request
from ui.api_errors import server_error_from_exception


@app.errorhandler(Exception)
def _api_uncaught_exception(exc: Exception):
    if not request.path.startswith("/api/"):
        raise exc
    return server_error_from_exception(exc)
```

3. Verify manually (build stage): `curl -s -X POST http://localhost:5001/api/admin/agents` with invalid body is **not** required — unit test covers handler. No changes to individual blueprint modules in this stage.

## Stage 2: Frontend diagnostics helpers

**Done when:** `toastDiagnostics.ts` exports formatter + `readApiError`; `npm run build` in `src/ui/frontend/` passes; no Toast UI changes yet.

1. Create `src/ui/frontend/src/lib/toastDiagnostics.ts` with these exports:

```typescript
export const ERROR_TOAST_DURATION_MS = 15000

export interface ToastDiagnostics {
  timestamp?: string
  route?: string
  astral_candidate_id?: string | null
  api_path?: string
  http_method?: string
  http_status?: number
  response_body?: string
  exception_type?: string
  traceback?: string
}

export interface ToastMessage {
  text: string
  variant?: "success" | "error" | "info"
  durationMs?: number
  diagnostics?: ToastDiagnostics
}

export class ApiError extends Error {
  readonly diagnostics: ToastDiagnostics
  constructor(message: string, diagnostics: ToastDiagnostics) {
    super(message)
    this.name = "ApiError"
    this.diagnostics = diagnostics
  }
}

/** Parse non-OK Response body; throw ApiError with enrichment fields when present. */
export async function readApiError(response: Response, apiPath: string, method = "GET"): Promise<never> {
  const body = await response.json().catch(() => ({} as Record<string, unknown>))
  const message =
    (typeof body.error === "string" && body.error) ||
    (typeof body.message === "string" && body.message) ||
    `HTTP ${response.status}`
  throw new ApiError(message, {
    timestamp: new Date().toISOString(),
    api_path: apiPath,
    http_method: method,
    http_status: response.status,
    response_body: JSON.stringify(body, null, 2),
    exception_type: typeof body.exception_type === "string" ? body.exception_type : undefined,
    traceback: typeof body.traceback === "string" ? body.traceback : undefined,
  })
}

export function errorToastFromApiError(err: ApiError): ToastMessage {
  return { text: err.message, variant: "error", diagnostics: err.diagnostics }
}

/** Multi-line clipboard bundle — stable key order for Linear paste. */
export function formatDiagnosticBundle(
  message: ToastMessage,
  route: string,
  candidateId: string | null,
): string {
  const d = message.diagnostics ?? {}
  const lines: string[] = [
    "Astral error diagnostic",
    `timestamp: ${d.timestamp ?? new Date().toISOString()}`,
    `message: ${message.text}`,
    `route: ${d.route ?? route}`,
  ]
  if (candidateId) lines.push(`astral_candidate_id: ${candidateId}`)
  if (d.api_path) lines.push(`api_path: ${d.api_path}`)
  if (d.http_method) lines.push(`http_method: ${d.http_method}`)
  if (d.http_status != null) lines.push(`http_status: ${d.http_status}`)
  if (d.exception_type) lines.push(`exception_type: ${d.exception_type}`)
  if (d.response_body) {
    lines.push("response_body:")
    lines.push(d.response_body)
  }
  if (d.traceback) {
    lines.push("traceback:")
    lines.push(d.traceback)
  }
  return lines.join("\n")
}
```

2. In `src/ui/frontend/src/components/Toast.tsx`, **move** the local `ToastMessage` / `ToastVariant` type definitions out — import `ToastMessage`, `ERROR_TOAST_DURATION_MS`, `formatDiagnosticBundle` from `../lib/toastDiagnostics` instead. Re-export `ToastMessage` and `ToastVariant` from `Toast.tsx` for backward-compatible page imports:

```typescript
export type { ToastMessage } from "../lib/toastDiagnostics"
export type ToastVariant = NonNullable<ToastMessage["variant"]>
```

## Stage 3: Toast component behavior and styles

**Done when:** Error toasts show for 15s, display copy affordance, copy bundle on click with confirmation; success/info unchanged at ~3s; `npm run build` passes.

1. In `Toast.tsx`, import `useLocation` from `react-router-dom` and `useCandidate` from `../contexts/CandidateContext`.

2. Replace duration logic inside the dismiss `useEffect`:

```typescript
const duration =
  message.durationMs ??
  (message.variant === "error" ? ERROR_TOAST_DURATION_MS : 3000)
```

3. Add component state: `const [copied, setCopied] = useState(false)`.

4. Add click handler (error only):

```typescript
async function handleClick() {
  if (!message || message.variant !== "error" || copied) return
  const bundle = formatDiagnosticBundle(message, location.pathname, selectedId)
  try {
    await navigator.clipboard.writeText(bundle)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  } catch {
    /* clipboard blocked — no-op */
  }
}
```

5. Render:
   - Root `div` className: include `toast-error-clickable` when `variant === "error"`.
   - Set `role="button"` and `tabIndex={0}` on error toasts; `onClick={handleClick}`; `onKeyDown` triggers copy on Enter/Space.
   - Display text: `copied ? "Copied to clipboard" : message.text`.
   - Append hint span when error and not copied: `<span className="toast-copy-hint">Click to copy</span>` (after main text).

6. In `App.css` §11 Toast, add:

```css
.toast-error-clickable {
  pointer-events: auto;
  cursor: pointer;
}
.toast-error-clickable:hover {
  filter: brightness(1.08);
}
.toast-copy-hint {
  margin-left: 8px;
  font-size: 12px;
  font-weight: 500;
  opacity: 0.85;
}
```

7. Do **not** change success/info `pointer-events: none` on base `.toast` — only `.toast-error-clickable` overrides to `auto`.

## Stage 4: Representative page wiring

**Done when:** Admin agent load/save failures and candidate profile save failures attach API diagnostics to error toasts; other pages still compile unchanged.

1. In `AdminAgentPrompts.tsx`, for each `api(...)` chain that currently does:

```typescript
if (!r.ok) return r.json().then(e => { throw new Error(e.error || "...") })
```

replace with:

```typescript
if (!r.ok) return readApiError(r, "<exact path string>", "<METHOD>")
```

Use the literal path passed to `api()` (e.g. `"/api/admin/agents/agent_a"`, `"/api/admin/agents"`, `"/api/admin/agents/preview"`). Update `.catch` handlers:

```typescript
.catch(e => setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: e.message, variant: "error" }))
```

Apply to: agent list load error path (~line 147), update save, create save, delete, preview — all existing error-toast `.catch` sites in this file.

2. In `CandidateProfile.tsx`, profile save handler (~line 84): replace `throw new Error(e.error || "Save failed")` with `readApiError(r, `/api/candidates/${id}`, "PUT")` (use the actual candidate id variable in the path). Update `.catch`:

```typescript
.catch(e => setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: e.message, variant: "error" }))
```

3. Do **not** modify other pages in this ticket — they inherit 15s duration + route/candidate copy via Toast auto-context.

## Test manifest (Betty `qa-child` — engineer does not commit)

**Done when:** Betty’s manifest rows pass in `test-child`.

1. Extend `tests/component/frontend/components/test_Toast.test.tsx`:
   - Error toast without explicit `durationMs` uses 15000ms timer (advance fake timers 15000 + 300, assert `onDone` once).
   - Success toast still dismisses at 3000ms default.
   - Click error toast → mock `navigator.clipboard.writeText` → assert called with string containing `message:` and `route:`.
   - After click, assert **"Copied to clipboard"** visible; after 2000ms original text returns.
   - Assert `.toast-error-clickable` and **"Click to copy"** hint on error variant.

2. Add `tests/component/ui/api/test_api_errors.py`:
   - Register minimal Flask app with same error handler pattern (or import `server.app` test client).
   - Route that raises `RuntimeError("boom")` under `/api/test/boom` → assert 500 JSON keys `error`, `exception_type`, `traceback`.
   - Route outside `/api/` that raises → assert exception propagates (not swallowed).

## Self-Assessment

**Scope:** `Single-Component` — Primary touch is shared `Toast.tsx` plus one small lib module and one Flask error helper; two representative pages demonstrate API diagnostic wiring.

**Conf:** `high` — Patterns exist (`Toast`, `api()` error JSON, `CandidateContext`); ticket boundaries are explicit and backward-compatible for pages passing only `{ text, variant: "error" }`.

**Risk:** `Medium` — Global Flask exception handler must not intercept non-API routes or leak secrets; mis-wiring could change 500 response shapes for API clients, but enrichment is additive and scoped to `/api/*`.

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Shared `toastDiagnostics.ts` and `api_errors.py` avoid duplicating format logic across pages/blueprints. |
| §2.1 config | Durations live as named constants in frontend lib (`ERROR_TOAST_DURATION_MS`), not magic numbers scattered in pages. |
| §3.3 imports | `api_errors.py` uses Flask/jsonify only; frontend lib has no core/data imports; Toast imports context + lib only. |
| §3.5 naming | New files follow snake_case (Python) and camelCase/PascalCase (TS) conventions. |
| §1.5 logging | No new backend debug logging; traceback only in JSON error responses for operator copy, not `app_log`. |

No plan conflicts requiring escalation.

## Review stub

| Field | Value |
|-------|-------|
| **Publish ref** | `origin/sub/AST-770/AST-779-error-toast-diagnostics` |
| **Built tip** | `cc9b5f0` |
| **Stages** | 1 — `api_errors.py` + `/api/*` handler (`501b915`); 2 — `toastDiagnostics.ts` (`f8bde5c`); 3 — Toast 15s + click-to-copy + CSS (`0379f75`); 4 — AdminAgentPrompts + CandidateProfile ApiError wiring (`cc9b5f0`) |
| **Betty next** | `test_Toast.test.tsx` extensions + `test_api_errors.py` per plan test manifest |

## Radia review (2026-06-24)

**Diff:** `origin/dev...origin/sub/AST-770/AST-779-error-toast-diagnostics` @ `50ae12a`

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity (Stages 1–4) | `api_errors.py` + `/api/*` handler; `toastDiagnostics.ts` helpers; Toast 15s error dismiss, click-to-copy, copied feedback without timer reset; representative `AdminAgentPrompts` + `CandidateProfile` `readApiError` wiring. |
| Backward compatibility | Pages passing `{ text, variant: "error" }` only still get route + candidate id via Toast auto-context; success/info unchanged (~3s, non-interactive). |
| §3.3 layer | `api_errors.py` Flask/jsonify only; frontend lib has no core/data imports; `server.py` late import matches existing pattern. |
| §1.5 logging | Traceback in JSON 500 responses only — no new `app_log` / debug-contract emission. |
| Handler scope | Non-`/api/` paths re-raise; test manifest covers enriched 500 JSON and non-API propagation. |
| Tests | Betty manifest rows present: Toast Vitest (15s/3s/copy/copied), `test_api_errors.py` helper + handler contract. |
| Self-Assessment | Scope `Single-Component` matches diff footprint; Conf `high` — no `!!-NONE` gap. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **advisory** | `server.py` `_api_uncaught_exception` | Catch-all `Exception` on `/api/*` would also wrap Werkzeug `HTTPException` (404/403) as enriched 500 if a route later uses `abort()` — today no `abort`/`HTTPException` in `src/ui/`. Optional hardening: re-raise `HTTPException` subclasses before `server_error_from_exception`. |

### Recommended actions

| Action | Owner |
|--------|-------|
| None required for resolve | — |
| Optional: guard `HTTPException` in handler when touching this file again | Engineer (future) |
