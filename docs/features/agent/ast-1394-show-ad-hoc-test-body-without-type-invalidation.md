# Show Ad Hoc Test body without type invalidation

- **Linear:** [AST-1394](https://linear.app/astralcareermatch/issue/AST-1394)
- **Parent:** [AST-1392](https://linear.app/astralcareermatch/issue/AST-1392)
- **Publish ref:** `sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation`

After sibling #1 (`AST-1393`) the workbench success path already stringifies an object/list payload to compact JSON text via `_caller_response_blob` before the RESPONSE write, and leaves `result["parsed_response"]` as the original envelope. This ticket is the Admin Test overlay: `POST /api/admin/adhoc/test` returns that same text as `response_text` (always a `str`), and the Agent Ad Hoc workbench displays it — pretty-printed when it is JSON. A successful provider reply is never replaced with a type or schema error overlay. Provider/API failures still fail the Test.

Does **not** own persist, debug contract, or production ingest (sibling #1 / Boundaries). Does **not** edit `src/core/agent.py` beyond importing the existing stringify helper into the UI API. Does **not** change Preview, dispatch batch apply, or other Admin pages.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Import `_caller_response_blob`; stringify Ad Hoc Test success body the same way #1 stores it; `response_text` is always `str` | ui |
| `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | Coerce a success body to text before `setResponse`; keep existing pretty-print; never treat `success: true` as an `ERROR:` overlay | ui |

Do **not** edit: `src/core/agent.py` (no persist/debug changes), `src/data/database.py`, `do_task` schema validation / AST-1289 coerce, Preview (`/api/admin/adhoc/preview` or the Preview UI), hydrated-output section (stays commented out), `tests/`, bible.

## Stages

### Stage 1: Admin Test HTTP returns serialized body as text

**Done when:** `POST /api/admin/adhoc/test` on a successful workbench result whose `parsed_response` is a JSON envelope with an object `agent_payload` (the `craft_company_search_terms` shape) returns HTTP 200 `{"success": true, "response_text": <str>, ...}` where `response_text` is compact JSON text of that payload — the same string `_caller_response_blob` produces, not a nested JSON object, not a Python `str(dict)` dump. A successful plain-text `parsed_response` (or string `agent_payload`) is returned unchanged (no extra JSON wrapping). A numeric `parsed_response` such as `123` is still `"123"`. A provider/API failure (`success` false or raised exception) still returns HTTP 500 with `{"success": false, "error": ...}` — no fake success body. `python3 -m py_compile src/ui/api/api_admin.py` passes.

1. In `src/ui/api/api_admin.py`, add `_caller_response_blob` to the existing `src.core.agent` import (do **not** add a new import block, do **not** import from `src.data` for this ticket):

   ```python
   from src.core.agent import (
       run_adhoc_workbench_test,
       _decode_payload,
       resolved_agent_content,
       resolved_task_system,
       _chain_context,
       _caller_response_blob,
   )
   ```

2. In `adhoc_test`, after the existing `if not result.get("success"):` 500 return and **before** `timesheet = result.get("timesheet", {})`, replace **only** this success-body extraction:

   ```python
       response_text = result.get("parsed_response") or ""
       # For tasks with JSON envelope, do_task auto-extracts agent_payload into parsed_response.
       # If it's still a dict here (e.g. run_adhoc doesn't do the extraction), pull it out.
       if isinstance(response_text, dict) and "agent_payload" in response_text:
           response_text = response_text["agent_payload"] or ""
       if not isinstance(response_text, str):
           response_text = str(response_text)
   ```

   with this exact sequence:

   ```python
       parsed = result.get("parsed_response")
       if isinstance(parsed, dict) and "agent_payload" in parsed:
           body = parsed["agent_payload"]
       else:
           body = parsed
       response_text = _caller_response_blob(body)
   ```

   Leave the encoded `_decode_payload` block and the `return jsonify({"success": True, "response_text": response_text, "hydrated": hydrated, "timesheet": timesheet})` unchanged. `response_text` is always a `str` (compact JSON for dict/list via `_caller_response_blob`; otherwise `str(body)` or `""` for `None`). Flask therefore emits a JSON **string** field, not a nested object.

3. Do **not** pretty-print in the API (`indent=`). Compact JSON matches the RESPONSE text sibling #1 stored. React pretty-prints for display (Stage 2).

4. Do **not** use `parsed_response or ""` before the extract — an empty dict/list is falsy and would collapse to `""`. Empty dict/list become `"{}"` / `"[]"` (same as #1). Do **not** wrap an already-`str` body in extra JSON quotes.

5. Do **not** change the failure branches (`except Exception` → 500, `if not result.get("success")` → 500). Do **not** change `_resolve_adhoc`, Preview, `run_adhoc_workbench_test` arguments, `@require_admin`, or `hydrated`. Do **not** call `database` / `save_agent_data` from this route. Do **not** add schema validation on this overlay — a successful provider reply stays `success: True` even when the payload would fail production `do_task` ingest.

6. Do **not** edit `tests/` or `docs/test-bible/**`. Existing component cases that assert `response_text == "payload"` (string `agent_payload`) and `response_text == "123"` (numeric `parsed_response`) stay valid. Betty owns any new object-payload HTTP coverage.

⚠️ **Decision:** Import `_caller_response_blob` rather than a second `json.dumps` in `api_admin.py` or a new public helper in `agent.py`. The UI layer already imports private agent helpers (`_decode_payload`, `_chain_context`). One stringify habit means HTTP `response_text` equals the stored RESPONSE body (`astral.standards.dry-and-focused-functions`). UI still does not call data (`pattern.layers.import-discipline` / `astral.layers.import-direction`).

⚠️ **Decision:** Keep extracting `agent_payload` when that key is present, then stringify **that** body — not the full `{agent_performance, agent_payload}` envelope. Parent: when a payload key is present, display that payload body. Same extract as #1.

### Stage 2: Workbench displays the body; success is never an ERROR overlay

**Done when:** On `POST /api/admin/adhoc/test` HTTP 200 with `success: true`, the Agent Ad Hoc **Response** `<pre>` shows the payload as text. When `response_text` is compact JSON (object payload from Stage 1), the existing `formatResponse` pretty-prints it (`JSON.stringify(..., null, 2)`). When `response_text` is already plain text, it displays unchanged. If `response_text` is a nested object/list (defense — Stage 1 should not emit this), it is coerced to JSON text and shown — React does **not** throw (`response.startsWith` / “Objects are not valid as a React child”) and does **not** replace it with `ERROR: …`. HTTP `!ok` / `success: false` still set `ERROR: …` (red overlay). Preview UI is unchanged.

1. In `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, immediately **above** the existing `formatResponse` helper, add this function (do **not** change `formatResponse` itself):

   ```tsx
     function responseBodyToText(body: unknown): string {
       if (typeof body === "string") return body
       if (body == null) return ""
       try { return JSON.stringify(body) } catch { return String(body) }
     }

     function formatResponse(text: string): string {
       try { return JSON.stringify(JSON.parse(text), null, 2) } catch { return text }
     }
   ```

   `JSON.stringify` without `indent` — compact text in state; `formatResponse` at render still pretty-prints JSON strings. `body == null` covers both `null` and `undefined`.

2. In `handleTest`, inside `.then(data => { ... })`, replace **only** the success assignment:

   ```tsx
           if (data.success) {
             setResponse(data.response_text)
             setTimesheet(data.timesheet || null)
           } else {
             setResponse(`ERROR: ${data.error || "Unknown error"}`)
           }
   ```

   with:

   ```tsx
           if (data.success) {
             setResponse(responseBodyToText(data.response_text))
             setTimesheet(data.timesheet || null)
           } else {
             setResponse(`ERROR: ${data.error || "Unknown error"}`)
           }
   ```

   Leave the `if (!r.ok)` throw, the `.catch(e => setResponse(\`ERROR: ${e.message}\`))`, `setTesting`, timesheet display, and the Response `<pre>` (including `response.startsWith("ERROR:")` color and `{formatResponse(response)}`) unchanged. `setResponse` always receives a `string` on the success path, so `startsWith` stays valid.

3. Do **not** set `ERROR:` when `data.success` is true, even if `response_text` is an object, list, number, or empty. Do **not** add schema / type validation in this page. Do **not** re-enable the commented hydrated-output section. Do **not** change Preview, Save As, prompt tabs, or other Admin pages. Do **not** add a display truncation / length cap on the Response `<pre>` (existing `maxHeight: 600` overflow stays).

4. Do **not** edit `tests/` or `docs/test-bible/**`. Existing frontend case that posts `response_text: "{\"ok\":true}"` and asserts pretty-printed `"ok": true` stays valid. Betty owns any new object-payload chrome coverage.

⚠️ **Decision:** Pretty-print in React, not in the API. HTTP `response_text` stays compact so it matches the stored RESPONSE; the workbench pretty-prints at render via the existing `formatResponse` (`pattern.ui.admin-endpoint`: API returns the resolved body; React renders it).

⚠️ **Decision:** Coerce-to-string on the success path even after Stage 1 always returns a `str`. That is the type-invalidation guard: a nested JSON object in `response_text` must still display as JSON text, never crash the page or become an `ERROR:` overlay. Failure overlays stay reserved for HTTP/`success: false`.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Traceability

AC1 workbench shows JSON text / no type overlay → S1 + S2 | AC2 plain-text display → S1 + S2 | AC3 provider failure still failed Test → S1 (500) + S2 (`ERROR:`)
(AC persist / debug / production ingest → sibling #1, not this plan)

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
revision: 1
**Ticket:** AST-1394
**Overall:** APPROVED
**Publish ref:** `sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation` @ `eed6751e`

## Traceability
AC1 workbench shows JSON text / no type overlay → S1 + S2 (persist/traceback → sibling #1) | AC2 plain-text display → S1 + S2 (store → sibling #1) | AC3 provider failure still failed Test → S1 (500) + S2 (`ERROR:`)

## Findings

### acceptable — AC1 traceback / AC2 store clauses
- **Location:** Child Description AC1–AC2; plan `## Traceability` footer
- **Finding:** Ticket AC text still quotes persist/traceback language from the parent epic; this plan correctly limits scope to Admin HTTP + React display. Boundaries and traceability defer store/debug to AST-1393.
- **Recommendation:** No plan change. Full epic UAT needs #1 landed first for store/traceback; #2 UAT verifies `response_text` is always `str` and the Response `<pre>` never type-invalidates on `success: true`.

### acceptable — duplicate extract+stringify in API
- **Location:** Stage 1; sibling #1 leaves `result["parsed_response"]` as the original envelope
- **Finding:** `agent_payload` extract mirrors core workbench logic because #1 does not expose serialized text on `result`. Importing `_caller_response_blob` keeps the stringify habit aligned with stored RESPONSE text.
- **Recommendation:** Acceptable given the sibling split. Optional future refactor (out of scope): core returns a dedicated `response_text` field — not required for this ticket.

context_tokens≈17500

## Review (build stub)

**Publish ref:** `origin/sub/AST-1392/AST-1394-show-ad-hoc-test-body-without-type-invalidation`
**Tip (pre-review):** `f685256e`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `e5d49eb9` | Admin Test HTTP `response_text` via `_caller_response_blob` (compact JSON text of payload) |
| 2 | `f685256e` | Workbench coerces success body to text before `setResponse`; existing `formatResponse` pretty-prints JSON |
