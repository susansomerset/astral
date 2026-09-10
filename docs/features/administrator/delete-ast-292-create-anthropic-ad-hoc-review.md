# AST-292: Create Anthropic Ad Hoc — Code Review

**Branch:** `<agent>/ast-292-create-anthropic-ad-hoc`
**Commit to review:** `1ee3c61`
**Reviewer:** Chuckles

---

## Overall Assessment

**Ship it.** This is a well-scoped, self-contained tool. The backend is minimal and correct; the frontend covers the full workflow without unnecessary abstraction. A few real issues to flag — one with actual correctness risk — but nothing blocking.

---

## `admin_adhoc.py`

### `_resolve_adhoc` is clean

Agent lookup, model param resolution, token resolution — all correct. The fallback for temperature/max_tokens (`if agent.get("temperature") is not None`) mirrors the pattern in `anthropic.py do_task` exactly. Good.

### `asyncio.run()` inside a Flask route — real risk

```python
result = asyncio.run(_fetch_response_from_content(...))
```

`asyncio.run()` creates a new event loop and blocks the thread until done. This works fine in development with a single-threaded Flask server. However, if the server ever runs under an async worker (e.g., `uvicorn`, `hypercorn`, or any ASGI adapter), `asyncio.run()` will raise `RuntimeError: This event loop is already running`. The existing `admin_agents.py` and `admin_tasks.py` don't call async functions — this is the only endpoint that does. Worth noting so whoever runs `uvicorn` in the future isn't confused by the crash. Low risk given current deployment, but it's a landmine.

### `response_format="text"` is hardcoded

This is the right default for a general-purpose workbench — there's no response schema. Calling with `"text"` avoids the JSON parsing path in `_send_and_parse`. Correct.

### `cache_content=resolved["cache"] or None`

The `or None` conversion means an empty string cache prompt is treated as "no cache" — which is what you want. Correct.

### No agent_response logging — by design

The spec says to skip it. `_fetch_response_from_content` still logs a timesheet row (via `_send_and_parse`), which is the acceptable side effect noted in the plan.

---

## `AnthropicAdHoc.tsx`

### `candidateName` is an IIFE inside the component body

```tsx
const candidateName = (() => {
  const c = candidates.find(c => c.astral_candidate_id === selectedId)
  ...
})()
```

This runs on every render. Not a perf issue at this scale, but a `useMemo` with `[candidates, selectedId]` deps would be more idiomatic and clearer in intent.

### Dropdown menus are hand-rolled inline

Both Fetch From and Save As use inline `<div>`-based dropdowns with `position: absolute`. These don't dismiss on outside click — the only way to close them is to click the button again or select an item. If the user opens Fetch From, then clicks somewhere else on the page, the dropdown stays open. In practice this is a minor annoyance for an admin-only tool; the existing `Modal` pattern would handle dismissal properly, but the inline dropdown is lighter and acceptable here.

### `window.confirm()` for FETCH FROM overwrite warning

```tsx
if (!window.confirm(`This will replace your current prompt content...`)) return
```

This is the browser native confirm dialog — blocks the main thread. The SAVE AS overwrite uses a custom inline confirmation block (`confirmTask` state) which is much nicer. The inconsistency is notable: Fetch From uses `window.confirm`, Save As uses the in-page confirm block. Should be unified to the in-page pattern.

### `handleTest` doesn't check `r.ok` before parsing

```tsx
.then(r => r.json())
.then(data => {
  if (data.success) { ... } else { setResponse(`ERROR: ${data.error}`) }
})
```

Compare to `handlePreview` and `handleFetchFrom` which check `r.ok` and throw on non-200. `handleTest` always calls `.json()` regardless of HTTP status code. If the server returns a 500 with an HTML error page (e.g., a Flask unhandled exception), `.json()` will throw a parse error, caught by `.catch(e => setResponse(...))`, which is okay — but the error message will be "Unexpected token < in JSON..." rather than anything useful. Low severity; the backend is well-guarded, but the error UX could be cleaner.

### Timesheet field names

```tsx
timesheet.duration ... timesheet.inputtotal ... timesheet.outputtotal ... timesheet.inputcached
```

These field names need to match what `_send_and_parse` actually returns in the timesheet dict. Worth verifying against the `add_timesheet_entry` call signature in `database.py` — if the actual keys are different (e.g., `tokens_input` vs `inputtotal`), the stats strip would silently show nothing. Not a crash risk since the `&&` guards handle missing fields, but the display would be blank.

### No "clear" / "reset" button

Once you've run a test and loaded response state, there's no way to clear the editor back to a blank state short of manually deleting text. Fine for v1, worth a future addition.

### The `hasContent` guard on Save As is correct

```tsx
const hasContent = userPrompt.trim() || cachePrompt.trim() || nocachePrompt.trim()
```

Disables Save As when all three prompts are empty. Correct.

---

## `routes.tsx` / `config.py`

The Artifacts routes and nav entries here are from ast-291 (they're in the diff because this branch was cut after 291 landed on main). The only ast-292-specific changes are the `AnthropicAdHoc` import and route swap. Both are clean.

---

## Summary of actionable items

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | Medium | `admin_adhoc.py` | `asyncio.run()` inside Flask route will crash under any async WSGI/ASGI server — note as a known constraint |
| 2 | Low | `AnthropicAdHoc.tsx` | FETCH FROM uses `window.confirm` for overwrite; SAVE AS uses inline confirm block — should be unified |
| 3 | Low | `AnthropicAdHoc.tsx` | `handleTest` doesn't check `r.ok` before `.json()` — non-JSON error responses produce confusing error messages |
| 4 | Low | `AnthropicAdHoc.tsx` | Timesheet field names (`inputtotal`, `outputtotal`, etc.) should be verified against actual `add_timesheet_entry` keys |
| 5 | Note | `AnthropicAdHoc.tsx` | Dropdowns don't dismiss on outside-click — minor UX rough edge for an admin tool |
| 6 | Note | `AnthropicAdHoc.tsx` | `candidateName` IIFE on every render — consider `useMemo` |

Item 1 is the one to keep in the back of your mind for deployment. Items 2–3 are worth fixing before real use. Items 4–6 are polish.
